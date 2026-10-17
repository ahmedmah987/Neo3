"""Reports for one run, and comparisons between runs."""
import collections
import json
import random
import statistics

from .families import KINDS
from .scoring import PHASES, LEVELS, inside, summarize, weighted_interval_score


def question_key(q):
    return f"{q['family']} {json.dumps(q['params'], sort_keys=True)}"


def build(meta, questions, records, results):
    truth = {r["q"]: r["answer"] for r in results}
    report = {"meta": meta, "phases": {}, "kinds": {}, "questions": []}
    for phase in PHASES:
        recs = [records.get((q["q"], phase)) for q in questions]
        ok = [(q, r) for q, r in zip(questions, recs) if r and r["status"] == "ok"]
        statuses = collections.Counter(r["status"] if r else "missing" for r in recs)
        report["phases"][phase] = {"asked": len(questions), "statuses": dict(statuses),
                                   **summarize([(r["answer"], truth[q["q"]]) for q, r in ok])}
        report["kinds"][phase] = {
            kind: summarize([(r["answer"], truth[q["q"]]) for q, r in ok if q["kind"] == kind])
            for kind in sorted(set(KINDS.values()))
        }

    closer = {"instinct": 0, "worked": 0, "tie": 0}
    served, tokens, cost = set(), collections.Counter(), 0.0
    for q in questions:
        row = {"q": q["q"], "key": question_key(q), "family": q["family"], "kind": q["kind"],
               "short": q["short"], "answer": truth[q["q"]]}
        for phase in PHASES:
            r = records.get((q["q"], phase))
            cell = {"status": r["status"] if r else "missing"}
            for attempt in (r or {}).get("attempts", []):
                if attempt.get("served_model"):
                    served.add(attempt["served_model"] + (f" via {attempt['provider']}" if attempt.get("provider") else ""))
                for name in ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens", "reasoning_tokens"):
                    tokens[name] += attempt.get(name) or 0
                cost += attempt.get("cost") or 0
            if r and r["status"] == "ok":
                a = r["answer"]
                cell.update(a)
                cell["wis"] = weighted_interval_score(a, truth[q["q"]])
                cell["hits"] = {key: inside(a[key], truth[q["q"]]) for key, _ in LEVELS}
            row[phase] = cell
        if all("estimate" in row[p] for p in PHASES):
            errors = {p: abs(row[p]["estimate"] - row["answer"]) for p in PHASES}
            closer["tie" if errors["instinct"] == errors["worked"] else min(errors, key=errors.get)] += 1
        report["questions"].append(row)

    paired = [row for row in report["questions"] if all("wis" in row[p] for p in PHASES)]
    report["paired"] = {
        "n": len(paired),
        "closer": closer,
        "wis_instinct": statistics.fmean(r["instinct"]["wis"] for r in paired) if paired else None,
        "wis_worked": statistics.fmean(r["worked"]["wis"] for r in paired) if paired else None,
        "worked_better": sum(r["worked"]["wis"] < r["instinct"]["wis"] for r in paired),
    }
    report["served_models"] = sorted(served)
    report["tokens"] = {k: v for k, v in tokens.items() if v}
    report["cost"] = round(cost, 6) if cost else None
    return report


def pct(x):
    return "—" if x is None else f"{x:.1%}"


def frac(k, n):
    return f"{k} of {n} ({k / n:.0%})" if n else "—"


def num(x):
    return f"{x:,}" if isinstance(x, int) else f"{x:,.4g}"


def answered(phase):
    statuses = phase["statuses"]
    text = f"{statuses.get('ok', 0)} of {phase['asked']}"
    others = [f"{v} {k}" for k, v in sorted(statuses.items()) if k != "ok"]
    return text + (f" ({', '.join(others)})" if others else "")


def render(report):
    meta, phases = report["meta"], report["phases"]
    lines = [f"# Calibench report: {meta['model']}", "",
             f"Seed `{meta['seed']}`, {meta['count']} questions, Calibench {meta['calibench']}, "
             f"Python {meta['python']} (Unicode {meta['unicode']}), started {meta['started']}."]
    if report["served_models"]:
        lines += ["", f"Served by: {', '.join(report['served_models'])}."]
    if report["tokens"]:
        lines += ["", "Tokens: " + ", ".join(f"{k.replace('_', ' ')} {v:,}" for k, v in report["tokens"].items()) + "."]
    if report.get("cost"):
        lines += ["", f"Cost reported by the API: {report['cost']:.4f} (US dollars on OpenRouter)."]
    if report.get("answers_changed_after_run"):
        lines += ["", "**Warning:** answers.jsonl was changed after the run recorded its hash."]

    def row(label, cell):
        return f"| {label} | " + " | ".join(cell(phases[p]) if phases[p]["n"] else "—" for p in PHASES) + " |"

    def coverage(key, ranged):
        def cell(s):
            if not ranged:
                return frac(s[key]["hits"], s["n"])
            return frac(s[key]["ranged_hits"], s[key]["ranged"]) + f": {s[key]['verdict']}"
        return cell

    lines += ["", "## Summary", "", "| | Instinct | Worked |", "|---|---|---|",
              f"| Answered | {answered(phases['instinct'])} | {answered(phases['worked'])} |",
              row("**Weighted interval score**, mean (median)", lambda s: f"**{pct(s['wis_mean'])}** ({pct(s['wis_median'])})"),
              row("Interval score, 50% intervals", lambda s: pct(s["p50"]["interval_score"])),
              row("Interval score, 90% intervals", lambda s: pct(s["p90"]["interval_score"])),
              row("50% intervals containing the answer", coverage("p50", False)),
              row("… leaving out single numbers", coverage("p50", True)),
              row("90% intervals containing the answer", coverage("p90", False)),
              row("… leaving out single numbers", coverage("p90", True)),
              row("Answers given as certain (a single number)", lambda s: f"{s['certain']}, {s['certain_right']} exactly right"),
              row("Median error of the estimate", lambda s: pct(s["median_error"]))]
    paired = report["paired"]
    if paired["n"]:
        lines.append(f"| Estimate closer to the answer | {paired['closer']['instinct']} | {paired['closer']['worked']} |")
        lines += ["", f"Working it out lowered the weighted interval score on {paired['worked_better']} of "
                  f"{paired['n']} questions answered both ways, from {pct(paired['wis_instinct'])} to "
                  f"{pct(paired['wis_worked'])} on average."]
    lines += ["", "Scores are relative to the true answer, and lower is better. The weighted interval score "
              "combines the estimate and both intervals (Bracher et al., 2021): narrow intervals score well only if "
              "the answer lands inside them, so it can't be improved by stating intervals you don't believe. "
              "Coverage verdicts leave out single-number intervals, which say \"I know this exactly\" and are "
              "counted on their own line."]

    lines += ["", "## By kind of question", "",
              "Knowledge questions ask what is known (the Python standard library, the Unicode database); statistical "
              "ones need noise or irregularity modelled; exact ones have a closed-form answer that must be evaluated.", "",
              "| Kind | Phase | Questions | Weighted interval score | 50% hits | 90% hits |", "|---|---|---|---|---|---|"]
    for kind in sorted(report["kinds"]["worked"]):
        for phase in PHASES:
            s = report["kinds"][phase][kind]
            if s["n"]:
                lines.append(f"| {kind} | {phase} | {s['n']} | {pct(s['wis_mean'])} | "
                             f"{frac(s['p50']['hits'], s['n'])} | {frac(s['p90']['hits'], s['n'])} |")

    lines += ["", "## Questions", "", "Each answer is shown as estimate [90% interval], with ✓ or ✗ for whether "
              "the 50% and 90% intervals contain the true answer.", "",
              "| # | Question | True answer | Instinct | Worked |", "|---|---|---|---|---|"]
    for r in report["questions"]:
        cells = []
        for phase in PHASES:
            c = r[phase]
            if c["status"] != "ok":
                cells.append(c["status"])
                continue
            marks = " ".join(f"{key[1:]}{'✓' if hit else '✗'}" for key, hit in c["hits"].items())
            cells.append(f"{num(c['estimate'])} [{num(c['p90'][0])}, {num(c['p90'][1])}] {marks}")
        lines.append(f"| {r['q']} | {r['short']} | {num(r['answer'])} | {cells[0]} | {cells[1]} |")
    return "\n".join(lines) + "\n"


def bootstrap_interval(differences, level=0.9, samples=4_000):
    rng = random.Random(0)
    n = len(differences)
    means = sorted(statistics.fmean(rng.choices(differences, k=n)) for _ in range(samples))
    return means[int(samples * (1 - level) / 2)], means[int(samples * (1 + level) / 2) - 1]


def compare(reports):
    """Compare runs on the questions every run answered in both phases."""
    rows = [{r["key"]: r for r in rep["questions"] if all("wis" in r[p] for p in PHASES)} for rep in reports]
    shared = sorted(set.intersection(*(set(r) for r in rows)))
    if not shared:
        return ("These runs have no questions in common that all of them answered. "
                "Run every model with the same --seed and --count.\n")
    pythons = {rep["meta"]["python"] for rep in reports}
    stats = []
    for rep, by_key in zip(reports, rows):
        mine = [by_key[k] for k in shared]
        stats.append({
            "model": rep["meta"]["model"],
            "wis": [r["worked"]["wis"] for r in mine],
            "instinct": statistics.fmean(r["instinct"]["wis"] for r in mine),
            "hits50": sum(r["worked"]["hits"]["p50"] for r in mine),
            "hits90": sum(r["worked"]["hits"]["p90"] for r in mine),
        })
    for s in stats:
        s["mean"] = statistics.fmean(s["wis"])
    stats.sort(key=lambda s: s["mean"])
    best = stats[0]
    lines = ["# Calibench comparison", "",
             f"{len(shared)} questions that every run answered in both phases. Scores are for worked answers "
             f"unless marked; lower is better.", ""]
    if len(pythons) > 1:
        lines += [f"**Note:** runs used different Python versions ({', '.join(sorted(pythons))}), so knowledge "
                  "questions were settled against different data.", ""]
    lines += ["| Model | Weighted interval score, mean (median) | 50% hits | 90% hits | Instinct score | Difference from the best, 90% interval |",
              "|---|---|---|---|---|---|"]
    n = len(shared)
    for s in stats:
        if s is best:
            diff = "best"
        else:
            d = [a - b for a, b in zip(s["wis"], best["wis"])]
            lo, hi = bootstrap_interval(d)
            diff = f"+{pct(statistics.fmean(d))} ({pct(lo)} to {pct(hi)})"
        lines.append(f"| {s['model']} | {pct(s['mean'])} ({pct(statistics.median(s['wis']))}) | {frac(s['hits50'], n)} "
                     f"| {frac(s['hits90'], n)} | {pct(s['instinct'])} | {diff} |")
    lines += ["", "The interval for a difference is a bootstrap over questions. When it includes zero, these "
              "questions don't separate the two models; more questions would."]
    return "\n".join(lines) + "\n"
