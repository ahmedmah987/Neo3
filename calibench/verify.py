"""Auditing a run directory: is it what it says it is?

A run can be checked by anyone with the directory and this package: that the replies weren't changed
after their hash was recorded, that the questions are what the seed (and suite) draw, that every
question has a recorded call, that the true answers recompute, and that the report follows from the
replies and the true answers under the current scoring.
"""
import hashlib
import json
import pathlib
import platform

from .families import KINDS
from .questions import (CALC1_FAMILIES, ORIGINAL_FAMILIES, SUITES, V2_FAMILIES, draw, fingerprint, rng_from_seed,
                        solve)
from .report import build, render, scored_phases
from .runner import load_records, read_json
from .scoring import PHASES

FILES = ("run.json", "questions.json", "answers.jsonl", "results.json", "report.json", "report.md")
PYTHON_DEPENDENT = {"knowledge"}          # kinds whose answers come from the Python running the benchmark


def families_of(meta):
    """The families a run drew from. Before 2.2.1 a run without --families recorded "all", which meant
    whatever families its version had: the original thirteen before 2.1, eighteen in 2.1, twenty-two in 2.2.0."""
    families = meta.get("families")
    if families not in (None, "all"):
        return families
    version = tuple(int(part) for part in meta["calibench"].split("."))
    return (ORIGINAL_FAMILIES if version < (2, 1) else V2_FAMILIES if version < (2, 2)
            else sorted(V2_FAMILIES + CALC1_FAMILIES))


def normal(data):
    return json.loads(json.dumps(data))


def verify(directory):
    """A list of (passed, message) pairs. A check that can't be made here is reported as passed, with why."""
    d = pathlib.Path(directory)
    checks = []

    def check(passed, message):
        checks.append((bool(passed), message))

    missing = [f for f in FILES if not (d / f).exists()]
    if missing:
        check(False, f"missing {', '.join(missing)}")
        return checks
    meta = read_json(d / "run.json")
    questions = read_json(d / "questions.json")["questions"]
    records = load_records(d / "answers.jsonl")
    results = read_json(d / "results.json")
    stored = read_json(d / "report.json")

    digest = hashlib.sha256((d / "answers.jsonl").read_bytes()).hexdigest()
    check(digest == meta["answers_sha256"], "the replies are unchanged since the run recorded their hash")

    families = families_of(meta)
    here = platform.python_version()
    if meta["python"].rsplit(".", 1)[0] == here.rsplit(".", 1)[0]:
        check(draw(rng_from_seed(meta["seed"]), meta["count"], families) == questions,
              f"the questions are what seed `{meta['seed']}` draws")
    else:
        check(True, f"not redrawn: drawn on Python {meta['python']}, running {here}")
    if meta.get("suite"):
        check(fingerprint(questions) == SUITES[meta["suite"]]["sha256"], f"the questions are exactly suite {meta['suite']}'s")

    check(all((q["q"], p) in records for q in questions for p in PHASES), "every question has a recorded call in both phases")

    truth = {r["q"]: r["answer"] for r in results["results"]}
    same_python = results.get("python") == here
    wrong, skipped = [], 0
    for q in questions:
        if KINDS[q["family"]] in PYTHON_DEPENDENT and not same_python:
            skipped += 1
        elif normal(solve(q)) != truth.get(q["q"]):
            wrong.append(q["q"])
    note = (f"; {skipped} knowledge answers not rechecked, settled on Python {results.get('python')} and running {here}"
            if skipped else "")
    check(not wrong, f"the true answers recompute ({len(questions) - skipped} checked{note})"
          + (f"; these differ: {', '.join(map(str, wrong))}" if wrong else ""))

    fresh = build(meta, questions, records, results["results"])
    check(normal(scored_phases(fresh["phases"])) == scored_phases(stored["phases"])
          and normal(fresh["questions"]) == stored["questions"],
          "the report follows from the replies and true answers under the current scoring")
    check(render(stored) == (d / "report.md").read_text(encoding="utf-8"), "report.md is the rendering of report.json")
    return checks
