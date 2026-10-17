"""Checks for Calibench: the families on small cases with known answers, reading replies, the scores,
a whole run, and every model adapter against a fake server or program.

Run with: python3 -m calibench selftest
Nothing here contacts a real model, and nothing prints a value from a real question.
"""
import contextlib
import http.server
import importlib.util
import io
import itertools
import json
import os
import pathlib
import random
import sys
import tempfile
import threading
import time

from . import families as F
from . import models, report, runner
from .prompts import PROMPTS, parse_answer
from .questions import draw, rng_from_seed, solve
from .scoring import interval_score, verdict, weighted_interval_score

failures = []


def check(name, ok):
    print(("ok    " if ok else "FAIL  ") + name, flush=True)
    if not ok:
        failures.append(name)


def raises(fn, *args):
    try:
        fn(*args)
    except (Exception, SystemExit):
        return True
    return False


# ---- families ------------------------------------------------------------------------------

def brute_lis(seq):
    best = [1] * len(seq)
    for i, x in enumerate(seq):
        for j in range(i):
            if seq[j] < x:
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def check_families():
    missing = [name for name in F.STDLIB_MODULES if name not in F.available_modules()]
    check("stdlib modules are single files" + (f" (not on this Python: {missing})" if missing else ""), not missing)
    check("primes in range matches trial division",
          all(F.solve_primes_in_range(a, a + 700) == sum(map(is_prime, range(a, a + 701)))
              for a in (100_000, 123_457, 999_000)))
    check("digit sum of 2^10 is 7 and of 2^15 is 26",
          F.solve_digit_sum_pow2(10) == 7 and F.solve_digit_sum_pow2(15) == 26)
    check("patience sorting gives the exact LIS of all 720 permutations of 6",
          all(F.lis_length(p) == brute_lis(p) for p in itertools.permutations(range(6))))
    # The average LIS over all permutations of 3 is exactly 2.
    check("average LIS for n = 3 is close to 2", abs(F.solve_lis(3, 1) - 2) < 0.1)
    check("mean distance in the unit square is about 0.5214", abs(F.solve_rect_distance(1, 7) - 0.5214) < 0.004)
    check("Collatz from 27 takes 111 steps", F.solve_collatz_steps(27) == 111)
    check("expected draws until a repeat with 365 values is about 24.6166", abs(F.solve_birthday(365) - 24.6166) < 1e-3)
    # Walk of 2 steps: ++ peaks at 2, +- at 1, the other two at 0, so the mean is 3/4.
    check("expected peak of a 2-step walk is 3/4", abs(F.solve_walk_max(2, 3) - 0.75) < 0.05)
    check("Unicode names split into words at spaces and hyphens",
          F.name_words(ord("A")) == ["LATIN", "CAPITAL", "LETTER", "A"] and "IDEOGRAPH" in F.name_words(0x4E00))
    check("function definitions are counted, nested and async included, lambdas not",
          F.count_defs("def a():\n    def b(): pass\nclass C:\n    async def d(self): pass\nf = lambda: 0\n") == 3)
    check("exactly one code point is a line separator (Zl)", F.solve_unicode_category("Zl") == 1)
    check("Basic Latin, U+0000–U+007F, is fully assigned", F.solve_unicode_block(0x00, 0x7F) == 128)
    check("json.__all__ has 7 names", F.solve_module_all("json") == 7)
    check("every family has a kind", set(F.KINDS) == set(F.FAMILIES))
    bad_blocks = [name for name, lo, hi in F.UNICODE_BLOCKS if not lo < hi or (hi + 1) % 16]
    check("block ranges are well formed", not bad_blocks)
    rng = random.Random("throwaway")                # values are not printed
    for name, (make, _) in sorted(F.FAMILIES.items()):
        params, text, short = make(rng)
        check(f"{name} draws a question", bool(text) and bool(short) and isinstance(params, dict))


# ---- drawing, reading replies, scoring -----------------------------------------------------

def check_core():
    a = draw(rng_from_seed("selftest"), 26)
    check("the same seed draws the same questions", a == draw(rng_from_seed("selftest"), 26))
    check("a different seed draws different questions", a != draw(rng_from_seed("selftest2"), 26))
    check("every family once before any repeats", len({q["family"] for q in a[:13]}) == 13
          and all(sum(q["family"] == f for q in a) == 2 for f in F.FAMILIES))
    many = draw(rng_from_seed("selftest"), 130)
    check("a run doesn't repeat a question", len({(q["family"], json.dumps(q["params"])) for q in many}) == 130)
    check("questions can be limited to some families",
          {q["family"] for q in draw(rng_from_seed("x"), 6, ["birthday", "lis"])} == {"birthday", "lis"})

    good = {"estimate": 12, "p50": [10, 14], "p90": [5, 20]}
    check("a bare JSON answer is read", parse_answer(json.dumps(good)) == good)
    check("the last JSON answer after working is read",
          parse_answer('First {"estimate": 1, "p50": [0, 2], "p90": [0, 3]} then {x} and\n' + json.dumps(good)) == good)
    check("numbers given as strings with commas are read",
          parse_answer('{"estimate": "1,200", "p50": ["1,000", 1400], "p90": [900, "2,000"]}')
          == {"estimate": 1200.0, "p50": [1000.0, 1400], "p90": [900, 2000.0]})
    check("reversed interval ends are put in order",
          parse_answer('{"estimate": 5, "p50": [6, 4], "p90": [9, 1]}')["p90"] == [1, 9])
    check("a reply with no usable answer is refused",
          raises(parse_answer, "about 12") and raises(parse_answer, '{"estimate": 5, "p50": [4]}')
          and raises(parse_answer, '{"estimate": NaN, "p50": [1, 2], "p90": [0, 3]}') and raises(parse_answer, None))
    check("both prompts carry the question and the answer format",
          all("Q?" in p.format(text="Q?") and '"p90"' in p.format(text="Q?") for p in PROMPTS.values()))

    check("interval score of a hit is its width over the answer", abs(interval_score([10, 20], 15, 0.1) - 10 / 15) < 1e-12)
    check("interval score of a miss adds 2/alpha times the miss", abs(interval_score([10, 20], 25, 0.1) - 110 / 25) < 1e-12)
    check("an exact single-number answer scores 0",
          weighted_interval_score({"estimate": 7, "p50": [7, 7], "p90": [7, 7]}, 7) == 0)
    check("a wider interval around the answer scores worse",
          weighted_interval_score({"estimate": 7, "p50": [6, 8], "p90": [5, 9]}, 7)
          < weighted_interval_score({"estimate": 7, "p50": [3, 11], "p90": [1, 20]}, 7))
    check("coverage verdicts", verdict(13, 26, 0.5) == "consistent with calibrated"
          and verdict(15, 26, 0.9) == "too narrow (overconfident)" and verdict(26, 26, 0.5) == "too wide (underconfident)"
          and verdict(2, 3, 0.9) == "too few to tell")


# ---- a whole run ---------------------------------------------------------------------------

FAST = ["birthday", "collatz_steps", "digit_sum_pow2", "module_all", "primes_in_range", "stdlib_defs",
        "stdlib_lines", "unicode_block"]


class OracleModel(models.Model):
    """Knows every answer exactly: a run with it must score perfectly."""

    def __init__(self, questions):
        self.truth = {q["text"]: solve(q) for q in questions}

    def ask(self, prompt, phase):
        x = next(v for text, v in self.truth.items() if text in prompt)
        return f"Working.\n{json.dumps({'estimate': x, 'p50': [x, x], 'p90': [x, x]})}", {"served_model": "oracle"}


class FlakyModel(models.Model):
    """Fails the first call for some questions, and answers badly but readably otherwise."""

    def __init__(self, failing):
        self.failing, self.seen = failing, set()

    def ask(self, prompt, phase):
        if any(q["text"] in prompt for q in self.failing) and (prompt, phase) not in self.seen:
            self.seen.add((prompt, phase))
            raise ConnectionError("simulated outage")
        return '{"estimate": 1, "p50": [1, 2], "p90": [1, 3]}', {}


def quiet(fn, *args):
    with contextlib.redirect_stderr(io.StringIO()):
        return fn(*args)


def check_run(tmp):
    seed, count = "selftest-run", 8
    questions = draw(rng_from_seed(seed), count, FAST)
    rep = quiet(runner.run, OracleModel(questions), "oracle", seed, count, FAST, tmp / "oracle", 3)
    worked = rep["phases"]["worked"]
    check("a run writes every file", all((tmp / "oracle" / f).exists() for f in
          ("run.json", "questions.json", "answers.jsonl", "results.json", "report.json", "report.md")))
    check("an oracle scores 0 with every interval hit", worked["n"] == count and worked["wis_mean"] == 0
          and worked["p90"]["hits"] == count and worked["certain_right"] == count)
    check("the served model is reported", rep["served_models"] == ["oracle"])
    before = (tmp / "oracle" / "answers.jsonl").read_text()
    quiet(runner.run, OracleModel(questions), "oracle", seed, count, FAST, tmp / "oracle", 3)
    check("running again resumes without asking again", (tmp / "oracle" / "answers.jsonl").read_text() == before)
    check("a different run is refused in the same directory",
          raises(quiet, runner.run, OracleModel(questions), "oracle", seed, count + 1, FAST, tmp / "oracle", 3))

    flaky = FlakyModel(questions[::2])
    rep = quiet(runner.run, flaky, "flaky", seed, count, FAST, tmp / "flaky", 1)
    check("failed calls are recorded as errors", rep["phases"]["worked"]["statuses"] == {"error": count // 2, "ok": count // 2})
    rep = quiet(runner.run, flaky, "flaky", seed, count, FAST, tmp / "flaky", 1)
    check("running again retries failed calls",
          rep["phases"]["worked"]["statuses"] == {"ok": count} and rep["phases"]["worked"]["wis_mean"] > 0)

    broken = models.make_model("openai-compat:none", base_url="http://127.0.0.1:9", timeout=5)
    with environ_and_sleep():
        stopped = raises(quiet, runner.run, broken, "broken", seed, count, FAST, tmp / "broken", 1)
    asked = len(runner.load_records(tmp / "broken" / "answers.jsonl"))
    check("a run stops early when every call fails", stopped and asked == runner.GIVE_UP_AFTER)

    rep = quiet(runner.run, models.NaiveModel(), "mock:naive", seed, count, FAST, tmp / "naive", 3)
    md = (tmp / "naive" / "report.md").read_text()
    check("a naive model scores worse than the oracle", rep["phases"]["worked"]["wis_mean"] > 0.1)
    check("the report has a summary, kinds and questions",
          all(s in md for s in ("## Summary", "## By kind of question", "## Questions")))
    table = report.compare([json.loads((tmp / d / "report.json").read_text()) for d in ("naive", "oracle")])
    check("compare ranks the oracle first", table.index("| oracle |") < table.index("| mock:naive |"))

    with open(tmp / "naive" / "answers.jsonl", "a") as f:
        f.write("\n")
    check("an edited answers file is flagged", quiet(runner.finish, tmp / "naive")["answers_changed_after_run"])


# ---- adapters ------------------------------------------------------------------------------

class FakeServer:
    """A local HTTP server that answers each POST with the next queued (status, headers, body)."""

    def __init__(self):
        self.queue, self.requests = [], []
        server = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                server.requests.append({"path": self.path, "headers": dict(self.headers), "body": json.loads(body)})
                status, headers, payload = server.queue.pop(0)
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def json(self, status, data):
        self.queue.append((status, {"Content-Type": "application/json"}, json.dumps(data).encode()))

    def sse(self, events):
        body = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events).encode()
        self.queue.append((200, {"Content-Type": "text/event-stream"}, body))

    def close(self):
        self.httpd.shutdown()


@contextlib.contextmanager
def environment(**values):
    old = {k: os.environ.get(k) for k in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


ANSWER = '{"estimate": 42, "p50": [40, 44], "p90": [30, 60]}'
LOCAL = {"NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost"}


def check_openai_compat():
    server = FakeServer()
    try:
        with environ_and_sleep():
            model = models.make_model("openai-compat:test-model", base_url=server.url + "/v1", api_key_env="CALIBENCH_TEST_KEY")
            server.json(503, {"error": "busy"})
            server.json(200, {"model": "test-model-2", "choices": [{"message": {"content": "Working. " + ANSWER},
                                                                    "finish_reason": "stop"}],
                              "usage": {"prompt_tokens": 10, "completion_tokens": 5}})
            reply, info = model.ask("PROMPT", "worked")
            sent = server.requests[-1]
            check("openai-compat: retries a 503, then reads the reply", ANSWER in reply and len(server.requests) == 2)
            check("openai-compat: sends the model, the prompt and the key",
                  sent["path"] == "/v1/chat/completions" and sent["body"]["model"] == "test-model"
                  and sent["body"]["messages"] == [{"role": "user", "content": "PROMPT"}]
                  and sent["headers"].get("Authorization") == "Bearer secret")
            check("openai-compat: records the served model and tokens",
                  info["served_model"] == "test-model-2" and info["completion_tokens"] == 5)
            server.json(200, {"choices": [{"message": {"content": [{"type": "text", "text": ANSWER}]},
                                           "finish_reason": "content_filter"}]})
            reply, info = model.ask("PROMPT", "instinct")
            check("openai-compat: content given as parts, and a content filter as a refusal",
                  reply == ANSWER and info.get("refused"))
            server.json(400, {"error": "bad request"})
            check("openai-compat: a 400 is an error, not retried", raises(model.ask, "PROMPT", "worked"))
    finally:
        server.close()


@contextlib.contextmanager
def environ_and_sleep():
    sleep = models.time.sleep
    models.time.sleep = lambda seconds: None
    try:
        with environment(CALIBENCH_TEST_KEY="secret", **LOCAL):
            yield
    finally:
        models.time.sleep = sleep


def message_events(text, stop_reason, stop_details=None):
    delta = {"stop_reason": stop_reason, "stop_sequence": None}
    if stop_details:
        delta["stop_details"] = stop_details
    return [
        {"type": "message_start", "message": {"id": "msg_test", "type": "message", "role": "assistant",
                                              "model": "claude-test-served", "content": [], "stop_reason": None,
                                              "stop_sequence": None, "usage": {"input_tokens": 11, "output_tokens": 1}}},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}},
        {"type": "content_block_stop", "index": 0},
        {"type": "message_delta", "delta": delta, "usage": {"output_tokens": 7}},
        {"type": "message_stop"},
    ]


def check_anthropic():
    if importlib.util.find_spec("anthropic") is None:
        print("skip  anthropic: the SDK isn't installed (pip install anthropic)")
        return
    server = FakeServer()
    try:
        with environment(ANTHROPIC_API_KEY="selftest", **LOCAL):
            model = models.make_model("anthropic:claude-test", base_url=server.url,
                                      instinct_effort="low", worked_effort="none")
            server.sse(message_events("Working. " + ANSWER, "end_turn"))
            reply, info = model.ask("PROMPT", "instinct")
            sent = server.requests[-1]["body"]
            check("anthropic: streams the reply and records the served model and tokens",
                  ANSWER in reply and info["served_model"] == "claude-test-served" and info["output_tokens"] == 7)
            check("anthropic: sends the model, the prompt and the instinct effort",
                  sent["model"] == "claude-test" and sent["messages"][0]["content"] == "PROMPT"
                  and sent.get("output_config") == {"effort": "low"} and sent.get("stream") is True)
            check("anthropic: sends no fallbacks", "fallbacks" not in sent)
            server.sse(message_events("", "refusal", {"type": "refusal", "category": "cyber", "explanation": None}))
            reply, info = model.ask("PROMPT", "worked")
            check("anthropic: an effort of none is left out", "output_config" not in server.requests[-1]["body"])
            check("anthropic: a refusal is recorded as one", info.get("refused") and info.get("stop_reason") == "refusal")
    finally:
        server.close()


def check_other_adapters(tmp):
    script = tmp / "fake_model.py"
    script.write_text("import sys\nprompt = sys.stdin.read()\n"
                      "print('Working on: ' + str(len(prompt)))\n"
                      f"print({ANSWER!r} if 'Question:' in prompt else 'no question')\n")
    model = models.make_model(f"cmd:{sys.executable} {script}")
    reply, _ = model.ask("Question: what?", "worked")
    check("cmd: sends the prompt on stdin and reads stdout", parse_answer(reply)["estimate"] == 42)
    check("cmd: a failing command is an error", raises(models.make_model(f"cmd:{sys.executable} -c 'exit(3)'").ask, "x", "worked"))

    seed, count = "selftest-replies", 4
    exported = tmp / "prompts.jsonl"
    from .__main__ import main
    quiet(main, ["export", "--seed", seed, "--count", str(count), "--families", ",".join(FAST), "--out", str(exported)])
    lines = [json.loads(line) for line in exported.read_text().splitlines()]
    check("export writes both phases for every question", len(lines) == 2 * count)
    replies = tmp / "replies.jsonl"
    replies.write_text("".join(json.dumps({**item, "reply": ANSWER if item["phase"] == "worked" else "no idea"}) + "\n"
                               for item in lines))
    rep = quiet(runner.run, models.make_model(f"replies:{replies}"), f"replies:{replies}", seed, count, FAST, tmp / "replies", 2)
    check("replies: collected replies are scored, and unreadable ones counted, not retried",
          rep["phases"]["worked"]["statuses"] == {"ok": count} and rep["phases"]["instinct"]["statuses"] == {"unparsed": count})

    stdin = sys.stdin
    sys.stdin = io.StringIO(f"Some working.\n{ANSWER}\nEND\nleft over\n")
    try:
        reply, _ = quiet(models.ManualModel().ask, "PROMPT", "worked")
    finally:
        sys.stdin = stdin
    check("manual: reads a pasted reply up to END", parse_answer(reply)["estimate"] == 42 and "left over" not in reply)


def main():
    start = time.time()
    print("Families\n")
    check_families()
    print("\nDrawing, reading replies and scoring\n")
    check_core()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        print("\nA whole run\n")
        check_run(tmp)
        print("\nModel adapters\n")
        check_openai_compat()
        check_anthropic()
        check_other_adapters(tmp)
    print(f"\n{'all checks passed' if not failures else f'{len(failures)} failure(s)'} in {time.time() - start:.0f} s")
    return 1 if failures else 0
