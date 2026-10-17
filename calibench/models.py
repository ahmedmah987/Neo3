"""Model adapters. A model is anything that turns a prompt into a reply.

Specs:
  anthropic:<model id>      Claude through the official SDK (pip install anthropic)
  openai-compat:<model id>  any server with an OpenAI-compatible /chat/completions endpoint
  cmd:<shell command>       any program that reads the prompt on stdin and writes the reply
  replies:<file.jsonl>      replies you collected yourself, one per line of `calibench export`
  manual                    you paste each reply yourself (for chat-only models)
  mock:naive                a built-in model that knows nothing, as a floor to compare against
"""
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

    def ask(self, prompt, phase):
        """Return (reply text, info dict)."""
        raise NotImplementedError


class AnthropicModel(Model):
    """Claude through the official SDK. Credentials come from the environment (ANTHROPIC_API_KEY,
    ANTHROPIC_AUTH_TOKEN or an `ant auth login` profile).

    Refusal fallbacks are deliberately left off: a fallback would let another model answer under
    this model's name. A refusal is recorded as a refusal instead.
    """

    def __init__(self, model_id, efforts, base_url=None, timeout=600):
        try:
            import anthropic
        except ImportError:
            sys.exit("the anthropic: adapter needs the official SDK: pip install anthropic")
        self.model_id = model_id or "claude-opus-5-5"
        self.efforts = efforts
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
            max_tokens=MAX_TOKENS[phase],
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


def _post_json(url, payload, headers, timeout, attempts=3):
    body = json.dumps(payload).encode()
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
        except urllib.error.URLError as error:
            if attempt == attempts - 1:
                raise RuntimeError(f"could not reach {url}: {error.reason}") from None
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

    def ask(self, prompt, phase):
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        data = _post_json(self.url, {"model": self.model_id, "messages": [{"role": "user", "content": prompt}]},
                          headers, self.timeout)
        choice = data["choices"][0]
        content = choice["message"].get("content") or ""
        if isinstance(content, list):          # some servers return content as a list of parts
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        info = {"served_model": data.get("model"), "stop_reason": choice.get("finish_reason")}
        if choice.get("finish_reason") == "content_filter":
            info["refused"] = True
        usage = data.get("usage") or {}
        info.update({k: usage[k] for k in ("prompt_tokens", "completion_tokens") if k in usage})
        return content, info


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
        return '{"estimate": 100, "p50": [30, 300], "p90": [3, 3000]}', {}


def make_model(spec, base_url=None, api_key_env=None, instinct_effort="low", worked_effort="high", timeout=600):
    scheme, _, rest = spec.partition(":")
    if scheme == "anthropic":
        return AnthropicModel(rest, {"instinct": instinct_effort, "worked": worked_effort}, base_url, timeout)
    if scheme == "openai-compat":
        return OpenAICompatModel(rest, base_url, api_key_env, timeout)
    if scheme == "cmd":
        return CommandModel(rest, timeout)
    if scheme == "replies":
        return RepliesModel(rest)
    if spec == "manual":
        return ManualModel()
    if spec == "mock:naive":
        return NaiveModel()
    sys.exit(f"unknown model spec {spec!r}; see `python3 -m calibench run --help`")
