"""Model adapters. A model is anything that turns a prompt into a reply.

Specs:
  anthropic:<model id>      Claude through the official SDK (pip install anthropic)
  openai-compat:<model id>  any server with an OpenAI-compatible /chat/completions endpoint
  openrouter:<model id>     any model on OpenRouter, with the key in OPENROUTER_API_KEY
  cmd:<shell command>       any program that reads the prompt on stdin and writes the reply
  replies:<file.jsonl>      replies you collected yourself, one per line of `calibench export`
  manual                    you paste each reply yourself (for chat-only models)
  mock:naive                a built-in model that knows nothing, as a floor to compare against
"""
import difflib
import http.client
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

MAX_TOKENS = {"instinct": 8_000, "worked": 32_000}


class Model:
    parallel = True          # whether several questions may be asked at once
    retries = True           # whether an unreadable reply may be asked for again
    settings = {}            # what a run should record about how the model was asked (effort, token caps)

    def ask(self, prompt, phase):
        """Return (reply text, info dict)."""
        raise NotImplementedError


class AnthropicModel(Model):
    """Claude through the official SDK. Credentials come from the environment (ANTHROPIC_API_KEY,
    ANTHROPIC_AUTH_TOKEN or an `ant auth login` profile).

    Refusal fallbacks are deliberately left off: a fallback would let another model answer under
    this model's name. A refusal is recorded as a refusal instead.
    """

    def __init__(self, model_id, efforts, base_url=None, timeout=600, max_tokens=MAX_TOKENS):
        try:
            import anthropic
        except ImportError:
            sys.exit("the anthropic: adapter needs the official SDK: pip install anthropic")
        self.model_id = model_id or "claude-opus-5-5"
        self.efforts, self.max_tokens = efforts, max_tokens
        self.settings = {"effort": efforts, "max_tokens": max_tokens}
        options = {"timeout": timeout}
        if base_url:
            options["base_url"] = base_url
        self.client = anthropic.Anthropic(**options)

    def ask(self, prompt, phase):
        extra = {}
        if self.efforts.get(phase) not in (None, "", "none"):
            extra["output_config"] = {"effort": self.efforts[phase]}
        with self.client.messages.stream(
            model=self.model_id,
            max_tokens=self.max_tokens[phase],
            messages=[{"role": "user", "content": prompt}],
            **extra,
        ) as stream:
            response = stream.get_final_message()
        text = "".join(block.text for block in response.content if block.type == "text")
        info = {"served_model": response.model, "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        if response.stop_reason == "refusal":
            info["refused"] = True
            details = getattr(response, "stop_details", None)
            info["refusal_category"] = getattr(details, "category", None) if details else None
        return text, info


def _request_json(url, payload, headers, timeout, attempts=3):
    """POST a JSON payload, or GET if there is none, retrying rate limits, server errors, lost connections
    and replies cut off partway."""
    body = json.dumps(payload).encode() if payload is not None else None
    for attempt in range(attempts):
        request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as error:
            retryable = error.code == 429 or error.code >= 500
            if not retryable or attempt == attempts - 1:
                detail = error.read().decode(errors="replace")[:500]
                raise RuntimeError(f"HTTP {error.code} from {url}: {detail}") from None
        except (OSError, http.client.HTTPException) as error:     # refused, reset, timed out or cut off
            if attempt == attempts - 1:
                reason = getattr(error, "reason", None) or f"{type(error).__name__}: {error}"
                raise RuntimeError(f"could not reach {url}: {reason}") from None
        time.sleep(2 ** (attempt + 1))


class OpenAICompatModel(Model):
    """Any server that speaks the OpenAI-compatible chat completions protocol: hosted providers,
    or local servers such as Ollama, vLLM, llama.cpp and LM Studio."""

    def __init__(self, model_id, base_url, api_key_env, timeout=600):
        if not model_id:
            sys.exit("openai-compat: needs a model id, for example openai-compat:llama3.1")
        self.model_id = model_id
        self.url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        self.api_key = os.environ.get(api_key_env or "OPENAI_API_KEY", "")
        self.timeout = timeout

    def payload(self, prompt, phase):
        return {"model": self.model_id, "messages": [{"role": "user", "content": prompt}]}

    def headers(self):
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def ask(self, prompt, phase):
        data = _request_json(self.url, self.payload(prompt, phase), self.headers(), self.timeout)
        choice = data["choices"][0]
        if choice.get("finish_reason") == "error":
            raise RuntimeError(f"the server reported an error: {json.dumps(choice.get('error'))[:500]}")
        content = choice["message"].get("content") or ""
        if isinstance(content, list):          # some servers return content as a list of parts
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        info = {"served_model": data.get("model"), "stop_reason": choice.get("finish_reason")}
        if data.get("provider"):
            info["provider"] = data["provider"]
        if choice.get("finish_reason") == "content_filter":
            info["refused"] = True
        usage = data.get("usage") or {}
        info.update({k: usage[k] for k in ("prompt_tokens", "completion_tokens", "cost") if usage.get(k) is not None})
        if usage:                     # zero is recorded, and None when the server doesn't report reasoning
            info["reasoning_tokens"] = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
        return content, info


class OpenRouterModel(OpenAICompatModel):
    """Any model on OpenRouter. The key is read from OPENROUTER_API_KEY and sent only to OpenRouter;
    without one no Authorization header is sent, for setups where a proxy adds it.

    The model is looked up first, so a mistyped id fails before anything is spent. Effort is sent
    through OpenRouter's reasoning setting to models that support it, and then only providers that
    honour it are used. OpenRouter never swaps in a different model unless asked to, and Calibench
    doesn't ask; each call records the model and provider that served it, and its cost.
    """
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, model_id, efforts, base_url=None, api_key_env=None, timeout=600, max_tokens=MAX_TOKENS):
        if not model_id:
            sys.exit("openrouter: needs a model id, for example openrouter:anthropic/claude-opus-5.5")
        base = (base_url or self.BASE_URL).rstrip("/")
        super().__init__(model_id, base, api_key_env or "OPENROUTER_API_KEY", timeout)
        self.efforts = efforts
        try:
            listing = _request_json(base + "/models", None, {}, timeout)["data"]
        except (RuntimeError, KeyError, ValueError) as error:
            sys.exit(f"openrouter: couldn't list models: {error}")
        found = {m["id"]: m for m in listing}
        if model_id not in found:
            close = difflib.get_close_matches(model_id, list(found), n=5, cutoff=0.6)
            sys.exit(f"openrouter: no model {model_id!r}" + (f"; did you mean one of: {', '.join(close)}" if close else
                     "; see https://openrouter.ai/models"))
        info = found[model_id]
        self.reasoning = "reasoning" in (info.get("supported_parameters") or [])
        self.max_output = (info.get("top_provider") or {}).get("max_completion_tokens")
        self.max_tokens = {phase: min(cap, self.max_output or cap) for phase, cap in max_tokens.items()}
        self.settings = {"effort": efforts if self.reasoning else None, "max_tokens": self.max_tokens}

    def payload(self, prompt, phase):
        data = super().payload(prompt, phase)
        data["max_tokens"] = self.max_tokens[phase]
        effort = self.efforts.get(phase)
        if self.reasoning and effort not in (None, "", "none"):
            data["reasoning"] = {"effort": effort, "exclude": True}
            data["provider"] = {"require_parameters": True}
        return data

    def headers(self):
        return {**super().headers(), "HTTP-Referer": "https://github.com/ahmedmah987/Neo3", "X-Title": "Calibench"}


class CommandModel(Model):
    """Runs a shell command per question, with the prompt on stdin; the reply is its stdout."""

    def __init__(self, command, timeout=600):
        if not command:
            sys.exit("cmd: needs a command, for example cmd:ollama run llama3.1")
        self.command, self.timeout = command, timeout

    def ask(self, prompt, phase):
        result = subprocess.run(self.command, shell=True, input=prompt, capture_output=True,
                                text=True, timeout=self.timeout)
        if result.returncode != 0:
            raise RuntimeError(f"command exited with {result.returncode}: {result.stderr.strip()[-500:]}")
        return result.stdout, {"exit_code": 0}


class ManualModel(Model):
    """Shows each prompt and reads the reply you paste back, ended by a line containing only END."""
    parallel = False

    def ask(self, prompt, phase):
        print(f"\n{'=' * 70}\n[{phase}] Paste this into the model:\n{'-' * 70}\n{prompt}\n{'-' * 70}", file=sys.stderr)
        print("Paste the reply, then a line with only END:", file=sys.stderr)
        lines = []
        for line in sys.stdin:
            if line.strip() == "END":
                break
            lines.append(line)
        return "".join(lines), {}


class RepliesModel(Model):
    """Replies collected outside Calibench: each line of the file is a line of `calibench export`
    with a "reply" field added. Replies are matched to questions by their prompt."""
    retries = False

    def __init__(self, path):
        if not path:
            sys.exit("replies: needs a file, for example replies:replies.jsonl")
        self.replies = {}
        with open(path, encoding="utf-8") as f:
            for number, line in enumerate(f, 1):
                if line.strip():
                    item = json.loads(line)
                    if "prompt" not in item or "reply" not in item:
                        sys.exit(f"{path}:{number}: each line needs the exported prompt and a reply")
                    self.replies[item["prompt"]] = item["reply"]

    def ask(self, prompt, phase):
        if prompt not in self.replies:
            raise LookupError("no reply for this prompt in the file")
        return self.replies[prompt], {}


class NaiveModel(Model):
    """Knows nothing: the same guess for every question. A floor, not a competitor."""

    def ask(self, prompt, phase):
        from .scoring import KNOW_NOTHING

        return json.dumps(KNOW_NOTHING), {}


def make_model(spec, base_url=None, api_key_env=None, instinct_effort="low", worked_effort="high", timeout=600,
               worked_max_tokens=MAX_TOKENS["worked"]):
    scheme, _, rest = spec.partition(":")
    caps = {**MAX_TOKENS, "worked": worked_max_tokens}
    if scheme == "anthropic":
        return AnthropicModel(rest, {"instinct": instinct_effort, "worked": worked_effort}, base_url, timeout, caps)
    if scheme == "openai-compat":
        return OpenAICompatModel(rest, base_url, api_key_env, timeout)
    if scheme == "openrouter":
        return OpenRouterModel(rest, {"instinct": instinct_effort, "worked": worked_effort}, base_url, api_key_env,
                               timeout, caps)
    if scheme == "cmd":
        return CommandModel(rest, timeout)
    if scheme == "replies":
        return RepliesModel(rest)
    if spec == "manual":
        return ManualModel()
    if spec == "mock:naive":
        return NaiveModel()
    sys.exit(f"unknown model spec {spec!r}; see `python3 -m calibench run --help`")
