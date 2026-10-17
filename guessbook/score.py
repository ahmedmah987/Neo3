"""Score the guessbook.

Run with: python3 guessbook/score.py   (writes guessbook/SCORE.md and prints it)

Two kinds of record are scored:
- hand-picked guesses (guesses/NNN-slug/): one true-or-false claim each, with a probability;
- drawn rounds (rounds/<date>-<seed>/): questions drawn from a seed, each answered twice,
  by instinct and after working it out, with an estimate, a 50% interval and a 90% interval.
"""
import json
import pathlib
import re
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))   # the calibench package
from calibench.families import KINDS                                       # noqa: E402
from calibench.scoring import inside, interval_score                      # noqa: E402

ROOT = pathlib.Path(__file__).parent
BUCKETS = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0001)]
PHASES = ("instinct", "worked")


# ---- hand-picked guesses -------------------------------------------------------------------

def front_matter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit(f"{path}: missing front matter")
    fields = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


def load_guesses():
    rows = []
    for d in sorted((ROOT / "guesses").iterdir()):
        if not d.is_dir():
            continue
        g = front_matter(d / "guess.md")
        p = float(g["p"])
        if not 0 <= p <= 1:
            sys.exit(f"{d}/guess.md: p must be between 0 and 1")
        row = {"id": d.name, "claim": g["claim"], "p": p, "outcome": None}
        result = d / "result.md"
        if result.exists():
            outcome = front_matter(result).get("outcome")
            if outcome not in ("true", "false"):
                sys.exit(f"{result}: outcome must be true or false")
            row["outcome"] = outcome == "true"
        rows.append(row)
    return rows


def report_guesses(rows):
    done = [r for r in rows if r["outcome"] is not None]
    lines = ["## Hand-picked claims", "", f"{len(done)} resolved, {len(rows) - len(done)} pending."]
    if done:
        hits = sum(r["outcome"] for r in done)
        brier = sum((r["p"] - r["outcome"]) ** 2 for r in done) / len(done)
        lines += ["", f"- Claims that came true: {hits} of {len(done)}",
                  f"- Brier score: {brier:.3f} (0 is perfect; always saying 50% scores 0.250)",
                  "", "A claim given less than 50% counts as the opposite claim at 1 − p.", "",
                  "| Stated confidence | Claims | Average stated | Came true |",
                  "|---|---|---|---|"]
        for lo, hi in BUCKETS:
            group = []
            for r in done:
                p, o = (r["p"], r["outcome"]) if r["p"] >= 0.5 else (1 - r["p"], not r["outcome"])
                if lo <= p < hi:
                    group.append((p, o))
            if group:
                avg = sum(p for p, _ in group) / len(group)
                right = sum(o for _, o in group)
                lines.append(f"| {lo:.0%}–{min(hi, 1):.0%} | {len(group)} | {avg:.0%} "
                             f"| {right} of {len(group)} ({right / len(group):.0%}) |")
    lines += ["", "| Guess | Claim | p | Outcome |", "|---|---|---|---|"]
    for r in rows:
        outcome = "pending" if r["outcome"] is None else str(r["outcome"]).lower()
        lines.append(f"| [{r['id']}](guesses/{r['id']}/) | {r['claim']} | {r['p']:.2f} | {outcome} |")
    return lines


# ---- drawn rounds --------------------------------------------------------------------------

def check_answers(path, answers, questions):
    """Each question needs an estimate inside its 50% interval, inside its 90% interval."""
    by_q = {a.get("q"): a for a in answers}
    for q in questions:
        a = by_q.get(q["q"])
        if a is None:
            sys.exit(f"{path}: no answer for question {q['q']}")
        try:
            lo90, hi90 = a["p90"]
            lo50, hi50 = a["p50"]
            ok = lo90 <= lo50 <= a["estimate"] <= hi50 <= hi90
        except (KeyError, TypeError, ValueError):
            ok = False
        if not ok:
            sys.exit(f"{path}: question {q['q']} needs p90[0] ≤ p50[0] ≤ estimate ≤ p50[1] ≤ p90[1]")
    return by_q


def load_rounds():
    rounds = []
    base = ROOT / "rounds"
    for d in sorted(base.iterdir()) if base.exists() else []:
        if not d.is_dir():
            continue
        questions = json.loads((d / "questions.json").read_text(encoding="utf-8"))["questions"]
        phases = {}
        for phase in PHASES:
            f = d / f"{phase}.json"
            if f.exists():
                phases[phase] = check_answers(f, json.loads(f.read_text(encoding="utf-8")), questions)
        results = {}
        if (d / "results.json").exists():
            data = json.loads((d / "results.json").read_text(encoding="utf-8"))
            results = {r["q"]: r["answer"] for r in data["results"]}
        rounds.append({"name": d.name, "questions": questions, "phases": phases, "results": results})
    return rounds


def num(x):
    return f"{x:,}" if isinstance(x, int) else f"{x:,.4g}"


def report_rounds(rounds):
    lines = ["## Drawn rounds", "",
             "Questions drawn from a seed I don't choose. Each is answered twice, first by instinct and "
             "then after working it out, with an estimate, a 50% interval and a 90% interval.", "",
             "The interval score is the main measure: an interval's width plus a penalty of 2/α times any miss, "
             "relative to the answer (α is 0.5 for the 50% interval and 0.1 for the 90% one). Lower is better, "
             "and it can't be gamed by widening or narrowing intervals away from what I believe. Coverage is "
             "shown too, and also without single-number 50% intervals, which hit more than half the time "
             "whenever an integer answer is known."]
    stats = {phase: {"n": 0, "in50": 0, "in90": 0, "errors": [], "is50": [], "is90": [],
                     "ranged": 0, "ranged_in50": 0} for phase in PHASES}
    closer = {"worked": 0, "instinct": 0, "tie": 0}
    by_kind = {}                           # worked answers only, grouped by kind of question
    tables = []
    for rnd in rounds:
        table = [f"### {rnd['name']}", "", "| # | Question | Answer | Instinct | Worked |", "|---|---|---|---|---|"]
        for q in rnd["questions"]:
            answer = rnd["results"].get(q["q"])
            cells = []
            for phase in PHASES:
                a = rnd["phases"].get(phase, {}).get(q["q"])
                if a is None:
                    cells.append("—")
                    continue
                cell = num(a["estimate"])
                if answer is not None:
                    s = stats[phase]
                    s["n"] += 1
                    s["in50"] += inside(a["p50"], answer)
                    s["in90"] += inside(a["p90"], answer)
                    s["errors"].append(abs(a["estimate"] - answer) / abs(answer))
                    s["is50"].append(interval_score(a["p50"], answer, 0.5))
                    s["is90"].append(interval_score(a["p90"], answer, 0.1))
                    if a["p50"][0] != a["p50"][1]:
                        s["ranged"] += 1
                        s["ranged_in50"] += inside(a["p50"], answer)
                    marks = " ".join(f"{lvl}{'✓' if inside(a['p' + lvl], answer) else '✗'}" for lvl in ("50", "90"))
                    cell += f" ({marks})"
                cells.append(cell)
            if answer is not None and all(q["q"] in rnd["phases"].get(p, {}) for p in PHASES):
                e = {p: abs(rnd["phases"][p][q["q"]]["estimate"] - answer) for p in PHASES}
                closer["tie" if e["worked"] == e["instinct"] else min(e, key=e.get)] += 1
                w = rnd["phases"]["worked"][q["q"]]
                k = by_kind.setdefault(KINDS.get(q["family"], "other"),
                                       {"n": 0, "in50": 0, "ranged": 0, "ranged_in50": 0, "in90": 0, "is50": [], "is90": []})
                k["n"] += 1
                k["in50"] += inside(w["p50"], answer)
                k["in90"] += inside(w["p90"], answer)
                if w["p50"][0] != w["p50"][1]:
                    k["ranged"] += 1
                    k["ranged_in50"] += inside(w["p50"], answer)
                k["is50"].append(interval_score(w["p50"], answer, 0.5))
                k["is90"].append(interval_score(w["p90"], answer, 0.1))
            shown = "pending" if answer is None else num(answer)
            table.append(f"| {q['q']} | {q['short']} | {shown} | {cells[0]} | {cells[1]} |")
        tables += [""] + table

    if any(s["n"] for s in stats.values()):
        def frac(k, n):
            return f"{k} of {n} ({k / n:.0%})" if n else "—"
        def mean_pct(values):
            return f"{sum(values) / len(values):.2%}" if values else "—"
        lines += ["", "| | Instinct | Worked |", "|---|---|---|"]
        lines.append("| Interval score, 50% intervals | "
                     + " | ".join(mean_pct(stats[p]["is50"]) for p in PHASES) + " |")
        lines.append("| Interval score, 90% intervals | "
                     + " | ".join(mean_pct(stats[p]["is90"]) for p in PHASES) + " |")
        lines.append("| 50% intervals that contain the answer | "
                     + " | ".join(frac(stats[p]["in50"], stats[p]["n"]) for p in PHASES) + " |")
        lines.append("| … leaving out single-number intervals | "
                     + " | ".join(frac(stats[p]["ranged_in50"], stats[p]["ranged"]) for p in PHASES) + " |")
        lines.append("| 90% intervals that contain the answer | "
                     + " | ".join(frac(stats[p]["in90"], stats[p]["n"]) for p in PHASES) + " |")
        lines.append("| Median error of the estimate | "
                     + " | ".join(f"{statistics.median(stats[p]['errors']):.1%}" if stats[p]["errors"] else "—"
                                  for p in PHASES) + " |")
        lines.append(f"| Estimate closer to the answer | {closer['instinct']} | {closer['worked']} |")
        if closer["tie"]:
            lines.append(f"| Ties | {closer['tie']} | {closer['tie']} |")
        lines += ["", "Worked answers by kind of question: knowledge means recalling, statistical means modelling "
                  "noise or irregularity, exact means evaluating a known formula.", "",
                  "| Kind | Questions | 50% hits | … leaving out single numbers | 90% hits | Interval score 50% / 90% |",
                  "|---|---|---|---|---|---|"]
        for kind in sorted(by_kind):
            k = by_kind[kind]
            lines.append(f"| {kind} | {k['n']} | {frac(k['in50'], k['n'])} | {frac(k['ranged_in50'], k['ranged'])} "
                         f"| {frac(k['in90'], k['n'])} | {mean_pct(k['is50'])} / {mean_pct(k['is90'])} |")
    return lines + tables


if __name__ == "__main__":
    out = ["# Score", "", "Generated by `python3 guessbook/score.py`; don't edit by hand.", ""]
    out += report_guesses(load_guesses())
    rounds = load_rounds()
    if rounds:
        out += [""] + report_rounds(rounds)
    text = "\n".join(out) + "\n"
    (ROOT / "SCORE.md").write_text(text, encoding="utf-8")
    print(text, end="")
