"""Running a model through drawn questions, then settling and scoring them.

A run lives in one directory:
  run.json        what was run: model, seed, versions, and the hash of the answers
  questions.json  the questions drawn from the seed
  answers.jsonl   every call: the replies, the answer read from them, and its status
  results.json    the true answers, computed only after every answer is recorded
  report.json     the scores
  report.md       the scores, for reading

Running the same command again resumes: calls that already have an answer or a refusal are kept,
and failed ones are asked again.
"""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import platform
import re
import sys
import time
import unicodedata

from . import __version__
from .prompts import PROMPTS, RETRY, parse_answer
from .questions import draw, rng_from_seed, solve
from .scoring import PHASES, SCORING

KEPT = ("ok", "refused")
GIVE_UP_AFTER = 3          # calls that fail before any succeeds, which usually means a wrong key, URL or model


def log(message):
    print(message, file=sys.stderr, flush=True)


def default_dir(model_spec, seed):
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", model_spec).strip("_")[:60]
    return pathlib.Path("calibench-runs") / f"{slug}-{seed}"


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def ask(model, question, phase):
    """One question in one phase, with one more try if the reply can't be read."""
    prompt = PROMPTS[phase].format(text=question["text"])
    record = {"q": question["q"], "phase": phase, "status": None, "answer": None, "attempts": []}
    start = time.time()
    for attempt in range(2 if model.retries else 1):
        try:
            reply, info = model.ask(prompt if attempt == 0 else prompt + RETRY, phase)
        except Exception as error:                   # a failed call is recorded, not fatal
            record["attempts"].append({"error": f"{type(error).__name__}: {error}"})
            record["status"] = record["status"] or "error"
            break
        record["attempts"].append({"reply": reply, **info})
        if info.get("refused"):
            record["status"] = "refused"
            break
        try:
            record["answer"] = parse_answer(reply)
            record["status"] = "ok"
            break
        except ValueError:
            record["status"] = "unparsed"
    record["seconds"] = round(time.time() - start, 1)
    return record


def load_records(path):
    """The latest record for each (question, phase); a resumed run appends to the same file."""
    records = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                records[(r["q"], r["phase"])] = r
    return records


def run(model, model_spec, seed, count=26, families=None, out=None, workers=4, suite=None):
    out = pathlib.Path(out or default_dir(model_spec, seed))
    out.mkdir(parents=True, exist_ok=True)
    questions = draw(rng_from_seed(seed), count, families)
    if (out / "questions.json").exists():
        old = read_json(out / "questions.json")
        if old["questions"] != questions or old["model"] != model_spec:
            sys.exit(f"{out} holds a different run; choose another --out")
    else:
        write_json(out / "questions.json", {"seed": str(seed), "model": model_spec, "questions": questions})

    answers_path = out / "answers.jsonl"
    records = load_records(answers_path)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    if (out / "run.json").exists():
        started = read_json(out / "run.json")["started"]
    working = any(r["status"] != "error" for r in records.values())
    pending = [(q, phase) for phase in PHASES for q in questions
               if records.get((q["q"], phase), {}).get("status") not in KEPT]
    if pending:
        log(f"{model_spec}: {len(pending)} calls, seed {seed}, writing to {out}")
    with open(answers_path, "a", encoding="utf-8") as f:
        pool_size = max(1, workers) if model.parallel else 1
        with concurrent.futures.ThreadPoolExecutor(pool_size) as pool:
            for phase in PHASES:                    # every instinct answer before any worked one
                jobs = [pool.submit(ask, model, q, p) for q, p in pending if p == phase]
                for done, job in enumerate(concurrent.futures.as_completed(jobs), 1):
                    record = job.result()
                    records[(record["q"], phase)] = record
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    f.flush()
                    log(f"  {phase} {done}/{len(jobs)}: question {record['q']} {record['status']}")
                    working = working or record["status"] != "error"
                    if not working and done >= GIVE_UP_AFTER:
                        for j in jobs:
                            j.cancel()
                        sys.exit(f"the first {done} calls failed, so nothing more was asked. The last error:\n"
                                 f"  {record['attempts'][-1]['error']}\nFix it and run the same command again.")

    ordered = [records[(q["q"], phase)] for phase in PHASES for q in questions]
    answers_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ordered), encoding="utf-8")
    meta = {
        "calibench": __version__,
        "model": model_spec,
        "seed": str(seed),
        "count": count,
        "families": sorted(families) if families else "all",
        "suite": suite,
        "scoring": SCORING,
        "python": platform.python_version(),
        "unicode": unicodedata.unidata_version,
        "started": started,
        "answers_sha256": hashlib.sha256(answers_path.read_bytes()).hexdigest(),
    }
    write_json(out / "run.json", meta)
    return finish(out)


def settle(out, questions):
    """The true answers. Reused if they were already computed for these questions on this Python."""
    path = out / "results.json"
    if path.exists():
        old = read_json(path)
        if old.get("python") == platform.python_version() and [r["q"] for r in old["results"]] == [q["q"] for q in questions]:
            return old["results"]
    results = []
    for q in questions:
        start = time.time()
        results.append({"q": q["q"], "answer": solve(q), "seconds": round(time.time() - start, 2)})
    write_json(path, {"python": platform.python_version(), "unicode": unicodedata.unidata_version, "results": results})
    return results


def finish(out):
    """Settle the questions and write the report. Safe to run again on a finished run."""
    from .report import build, render

    out = pathlib.Path(out)
    meta = read_json(out / "run.json")
    questions = read_json(out / "questions.json")["questions"]
    records = load_records(out / "answers.jsonl")
    digest = hashlib.sha256((out / "answers.jsonl").read_bytes()).hexdigest()
    if digest != meta["answers_sha256"]:
        log(f"warning: {out / 'answers.jsonl'} changed after the run recorded its hash")
    results = settle(out, questions)
    report = build(meta, questions, records, results)
    report["answers_changed_after_run"] = digest != meta["answers_sha256"]
    report["scored_with"] = {"calibench": __version__, "scoring": SCORING}
    write_json(out / "report.json", report)
    (out / "report.md").write_text(render(report), encoding="utf-8")
    return report
