"""Reports for one run, and comparisons between runs."""
import collections
import json
import statistics

from .families import KINDS
from .questions import SUITES
from .scoring import (BIN_SHARES, BINS, KNOW_NOTHING, LEVELS, PHASES, bootstrap, bootstrap_mean, inside, log_wis,
                      offset, questions_needed, spearman, summarize, wilson)


DESCRIPTIVE = {"tokens"}             # phase fields that describe a run without being part of its score


def scored_phases(phases):
    """A report's phases without their descriptive fields: what must follow from the answers."""
    return {p: {k: v for k, v in s.items() if k not in DESCRIPTIVE} for p, s in phases.items()}


def legacy_zero(meta, records):
    """Before 2.3.1 the OpenRouter adapter left out reasoning counts of zero. In such a run, if any call
    reports reasoning, an attempt without the field reasoned for zero tokens. From 2.3.1 a missing or
    None count means the server didn't report one."""
    version = tuple(int(part) for part in meta.get("calibench", "0.0.0").split("."))
    return version < (2, 3, 1) and any("reasoning_tokens" in a for r in records for a in r.get("attempts", []))


def record_usage(record, zero_fill):
    """One call's (input, output, reasoning) tokens over all its attempts, each None if never reported."""
    inputs, outputs, thoughts, unknown = [], [], [], False
    for a in (record or {}).get("attempts", []):
        if a.get("input_tokens", a.get("prompt_tokens")) is not None:
            inputs.append(a.get("input_tokens", a.get("prompt_tokens")))
        out = a.get("output_tokens", a.get("completion_tokens"))
        if out is not None:
            outputs.append(out)
        if a.get("reasoning_tokens") is not None:
            thoughts.append(a["reasoning_tokens"])
        elif zero_fill and "reasoning_tokens" not in a and out is not None:
            thoughts.append(0)
        elif out is not None:
            unknown = True
    return (sum(inputs) if inputs else None, sum(outputs) if outputs else None,
            None if unknown or not thoughts else sum(thoughts))


def tokens_per_answer(recs, zero_fill):
    """Mean output and reasoning tokens per answer, over answers whose calls report them, retries included."""
    usage = [record_usage(r, zero_fill) for r in recs if r]
    output = [u[1] for u in usage if u[1] is not None]
    reasoning = [u[2] for u in usage if u[2] is not None]
    return {"output": statistics.fmean(output) if output else None,
            "reasoning": statistics.fmean(reasoning) if reasoning else None}


def question_key(q):
    return f"{q['family']} {json.dumps(q['params'], sort_keys=True)}"


def suite_status(meta):
    suite = meta.get("suite")
    if not suite:
        return None
    if meta["python"].rsplit(".", 1)[0] == SUITES[suite]["python"]:
        return f"standard suite {suite}"
    return (f"suite {suite} questions on Python {meta['python']}, so not comparable with standard {suite} "
            f"results, which use Python {SUITES[suite]['python']}")


def build(meta, questions, records, results):
    truth = {r["q"]: r["answer"] for r in results}
    zero_fill = legacy_zero(meta, records.values())
    report = {"meta": meta, "suite": suite_status(meta), "phases": {}, "kinds": {}, "families": {}, "questions": []}
    for phase in PHASES:
        recs = [records.get((q["q"], phase)) for q in questions]
        ok = [(q, r) for q, r in zip(questions, recs) if r and r["status"] == "ok"]
        statuses = collections.Counter(r["status"] if r else "missing" for r in recs)
        every = [log_wis(r["answer"] if r and r["status"] == "ok" else KNOW_NOTHING, truth[q["q"]], offset(q["family"]))
                 for q, r in zip(questions, recs)]
        report["phases"][phase] = {
            "asked": len(questions), "statuses": dict(statuses), "tokens": tokens_per_answer(recs, zero_fill),
            "all": {"score_mean": statistics.fmean(every), "score_median": statistics.median(every),
                    "score_ci": bootstrap_mean(every)},
            **summarize([(r["answer"], truth[q["q"]], offset(q["family"])) for q, r in ok]),
        }
        report["kinds"][phase] = {
            kind: summarize([(r["answer"], truth[q["q"]], offset(q["family"])) for q, r in ok if q["kind"] == kind])
            for kind in sorted(set(KINDS.values()))
        }
        report["families"][phase] = {
            family: summarize([(r["answer"], truth[q["q"]], offset(family)) for q, r in ok if q["family"] == family])
            for family in sorted({q["family"] for q in questions})
        }

    closer = {"instinct": 0, "worked": 0, "tie": 0}
    served, tokens, cost = set(), collections.Counter(), 0.0
    for q in questions:
        x, shift = truth[q["q"]], offset(q["family"])
        row = {"q": q["q"], "key": question_key(q), "family": q["family"], "kind": q["kind"],
               "short": q["short"], "answer": x}
        for phase in PHASES:
            r = records.get((q["q"], phase))
            cell = {"status": r["status"] if r else "missing"}
            for attempt in (r or {}).get("attempts", []):
                if attempt.get("served_model"):
                    served.add(attempt["served_model"] + (f" via {attempt['provider']}" if attempt.get("provider") else ""))
                cost += attempt.get("cost") or 0
            for name, value in zip(("input", "output", "reasoning"), record_usage(r, zero_fill)):
                tokens[name] += value or 0
            if r and r["status"] == "ok":
                cell.update(r["answer"])
                cell["score"] = log_wis(r["answer"], x, shift)
                cell["hits"] = {key: inside(r["answer"][key], x) for key, _ in LEVELS}
            else:
                cell["score"] = log_wis(KNOW_NOTHING, x, shift)
                cell["imputed"] = True
            row[phase] = cell
        if all(row[p]["status"] == "ok" for p in PHASES):
            errors = {p: abs(row[p]["estimate"] - x) for p in PHASES}
            closer["tie" if errors["instinct"] == errors["worked"] else min(errors, key=errors.get)] += 1
        report["questions"].append(row)

    paired = [row for row in report["questions"] if all(row[p]["status"] == "ok" for p in PHASES)]
    gains = [r["instinct"]["score"] - r["worked"]["score"] for r in paired]
    report["paired"] = {
        "n": len(paired),
        "closer": closer,
        "score_instinct": statistics.fmean(r["instinct"]["score"] for r in paired) if paired else None,
        "score_worked": statistics.fmean(r["worked"]["score"] for r in paired) if paired else None,
        "gain_ci": bootstrap_mean(gains),
        "worked_better": sum(g > 0 for g in gains),
    }
    report["concentration"] = {phase: concentration(report["questions"], phase) for phase in PHASES}
    report["served_models"] = sorted(served)
    report["tokens"] = {k: v for k, v in tokens.items() if v}
    report["cost"] = round(cost, 6) if cost else None
    return report


def miss_factor(interval, x, shift):
    """How far outside an interval the answer fell, as a factor beyond the nearer end (1 if inside)."""
    lo, hi = (max(v + shift, 1e-3) for v in interval)
    t = x + shift
    return t / hi if t > hi else lo / t if t < lo else 1.0


def concentration(rows, phase):
    """How much of a phase's score its largest questions carry, and the misses that cost most."""
    scores = sorted((r[phase]["score"] for r in rows), reverse=True)
    total = sum(scores)
    out = {"top1_share": scores[0] / total if total else None,
           "top5_share": sum(scores[:5]) / total if total else None,
           "mean_without_top": statistics.fmean(scores[1:]) if len(scores) > 1 else None,
           "misses": []}
    for r in rows:
        c = r[phase]
        if c["status"] == "ok" and not c["hits"]["p90"]:
            shift = offset(r["family"])
            out["misses"].append({"q": r["q"], "short": r["short"], "answer": r["answer"], "estimate": c["estimate"],
                                  "p90": c["p90"], "factor": miss_factor(c["p90"], r["answer"], shift),
                                  "width": (max(c["p90"][1] + shift, 1e-3) / max(c["p90"][0] + shift, 1e-3)),
                                  "score": c["score"], "share": c["score"] / total if total else None,
                                  "side": "above" if r["answer"] > c["p90"][1] else "below"})
    out["misses"].sort(key=lambda m: -m["score"])
    return out


def sc(x):
    return "—" if x is None else f"{x:.3f}"


def ci(interval, fmt=sc):
    return "" if not interval else f" [{fmt(interval[0])}, {fmt(interval[1])}]"


def pct(x):
    return "—" if x is None else f"{x:.0%}"


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
    scored = report.get("scored_with")
    if scored and scored["calibench"] != meta["calibench"]:
        lines[-1] += f" Scored with Calibench {scored['calibench']} ({scored['scoring']})."
    if report.get("suite"):
        lines += ["", f"**{report['suite'][0].upper() + report['suite'][1:]}.**"]
    if meta.get("prompts", "standard") != "standard":
        lines += ["", f"Prompts: **{meta['prompts']}** wording (see `prompts.py`)."]
    if report["served_models"]:
        lines += ["", f"Served by: {', '.join(report['served_models'])}."]
    if report["tokens"]:
        lines += ["", "Tokens: " + ", ".join(f"{k} {v:,}" for k, v in report["tokens"].items()) + "."]
    if report.get("cost"):
        lines += ["", f"Cost reported by the API: {report['cost']:.4f} (US dollars on OpenRouter)."]
    if report.get("answers_changed_after_run"):
        lines += ["", "**Warning:** answers.jsonl was changed after the run recorded its hash."]

    def row(label, cell):
        return f"| {label} | " + " | ".join(cell(phases[p]) if phases[p]["n"] else "—" for p in PHASES) + " |"

    def coverage(key, ranged):
        def cell(s):
            if ranged:
                return frac(s[key]["ranged_hits"], s[key]["ranged"]) + f": {s[key]['verdict']}"
            return frac(s[key]["hits"], s["n"]) + ci(s[key]["hits_ci"], pct)
        return cell

    unanswered = any(phases[p]["n"] < phases[p]["asked"] for p in PHASES)
    lines += ["", "## Summary", "", "| | Instinct | Worked |", "|---|---|---|",
              f"| Answered | {answered(phases['instinct'])} | {answered(phases['worked'])} |",
              "| **Score**, mean [90% interval] | " + " | ".join(
                  f"**{sc(phases[p]['all']['score_mean'])}**{ci(phases[p]['all']['score_ci'])}" for p in PHASES) + " |",
              "| Score, median | " + " | ".join(sc(phases[p]["all"]["score_median"]) for p in PHASES) + " |"]
    if unanswered:
        lines.append(row("Score, answered questions only", lambda s: f"{sc(s['score_mean'])}{ci(s['score_ci'])}"))
    lines += [row("Interval score, 50% / 90% intervals",
                  lambda s: f"{sc(s['p50']['interval_score'])} / {sc(s['p90']['interval_score'])}"),
              row("50% intervals containing the answer [90% interval]", coverage("p50", False)),
              row("… leaving out single numbers", coverage("p50", True)),
              row("90% intervals containing the answer [90% interval]", coverage("p90", False)),
              row("… leaving out single numbers", coverage("p90", True)),
              row("Answers given as certain (a single number)", lambda s: f"{s['certain']}, {s['certain_right']} exactly right"),
              row("Median error of the estimate", lambda s: f"{s['median_error']:.1%}")]
    spent = {p: phases[p].get("tokens") or {} for p in PHASES}
    if any(t.get("output") is not None for t in spent.values()):
        def tokens(t):
            if t.get("output") is None:
                return "—"
            return f"{t['output']:,.0f}" + (f" ({t['reasoning']:,.0f} reasoning)" if t.get("reasoning") is not None else "")
        lines.append(f"| Output tokens per answer | {tokens(spent['instinct'])} | {tokens(spent['worked'])} |")
    paired = report["paired"]
    if paired["n"]:
        lines.append(f"| Estimate closer to the answer | {paired['closer']['instinct']} | {paired['closer']['worked']} |")
        lines += ["", f"Working it out lowered the score on {paired['worked_better']} of {paired['n']} questions answered "
                  f"both ways, from {sc(paired['score_instinct'])} to {sc(paired['score_worked'])} on average "
                  f"(improvement{ci(paired['gain_ci']) or ' —'})."]
    lines += ["", "The score is the weighted interval score (Bracher et al., 2021) on a log scale: it combines the "
              "estimate and both intervals, is lowest when the stated intervals are the ones the model believes, "
              "and treats a miss by a factor in either direction alike. Lower is better; 0.1 is roughly a 10% miss. "
              "Intervals in brackets are 90% intervals over questions. Coverage verdicts leave out single-number "
              "intervals, which say \"I know this exactly\" and are counted on their own line."]
    if unanswered:
        lines += ["", "The score counts each unanswered question as if the model had answered "
                  f"`{json.dumps(KNOW_NOTHING)}`, as a model that knows nothing would; the rows below it use "
                  "answered questions only."]

    fell = {p: phases[p].get("fell") for p in PHASES}
    if any(f and f["n"] for f in fell.values()):
        lines += ["", "## Where the true answers fell", "",
                  "The estimate and the two intervals are five quantiles of the model's belief, so they split it into six "
                  "bins, and a calibrated model's true answers land in each bin in the expected share. Too many in the "
                  "outer bins means intervals too narrow; too many on one side of the estimate means a lean in that "
                  "direction. Single-number answers are left out, and an answer on a boundary is shared between the "
                  "bins it touches.", "",
                  "| The true answer was | Expected | Instinct | Worked |", "|---|---|---|---|"]
        for i, (label, share) in enumerate(zip(BINS, BIN_SHARES)):
            cells = [f"{f['bins'][i] / f['n']:.0%} ({f['bins'][i]:.4g})" if f and f["n"] else "—" for f in fell.values()]
            lines.append(f"| {label} | {share:.0%} | {cells[0]} | {cells[1]} |")
        cells = [f"{f['above'] / f['n']:.0%}{ci(f['above_ci'], pct)}" if f and f["n"] else "—" for f in fell.values()]
        lines.append(f"| **above the estimate**, with 90% interval | 50% | {cells[0]} | {cells[1]} |")
        lines += ["", "![Where the true answers fell](calibration.svg)"]

    conc = report.get("concentration")
    if conc:
        lines += ["", "## Where the score comes from", "",
                  "A few large misses can carry a mean. This shows how much of each score its largest questions "
                  "carry, and the worked answers whose 90% interval missed, costliest first.", "",
                  "| | Instinct | Worked |", "|---|---|---|",
                  "| Share of the score from the largest question | "
                  + " | ".join(pct(conc[p]["top1_share"]) for p in PHASES) + " |",
                  "| Share from the five largest | " + " | ".join(pct(conc[p]["top5_share"]) for p in PHASES) + " |",
                  "| Mean score without the largest question | "
                  + " | ".join(sc(conc[p]["mean_without_top"]) for p in PHASES) + " |"]
        misses = conc["worked"]["misses"]
        if misses:
            lines += ["", "**Worked answers outside their 90% interval.** *Outside by* is the factor between the "
                      "true answer and the nearer end of the interval; *width* is the ratio of the interval's ends, "
                      "so a narrow interval that misses by a wide factor is a confident miss.", "",
                      "| # | Question | True answer | Estimate [90% interval] | Width | Outside by | Score | Share of score |",
                      "|---|---|---|---|---|---|---|---|"]
            for m in misses[:10]:
                lines.append(f"| {m['q']} | {m['short']} | {num(m['answer'])} | {num(m['estimate'])} "
                             f"[{num(m['p90'][0])}, {num(m['p90'][1])}] | ×{m['width']:.3g} "
                             f"| ×{m['factor']:.3g} {m['side']} | {sc(m['score'])} | {pct(m['share'])} |")
            if len(misses) > 10:
                lines.append(f"| | {len(misses) - 10} more | | | | | | |")

    lines += ["", "## By kind of question", "",
              "Knowledge questions ask what is known (the Python standard library, the Unicode database); statistical "
              "ones need noise or irregularity modelled; exact ones have a closed-form answer that must be evaluated; "
              "calculation ones have an exact answer that takes long, careful arithmetic.", "",
              "| Kind | Phase | Questions | Score | 50% hits | 90% hits |", "|---|---|---|---|---|---|"]
    for kind in sorted(report["kinds"]["worked"]):
        for phase in PHASES:
            s = report["kinds"][phase][kind]
            if s["n"]:
                lines.append(f"| {kind} | {phase} | {s['n']} | {sc(s['score_mean'])} | "
                             f"{frac(s['p50']['hits'], s['n'])} | {frac(s['p90']['hits'], s['n'])} |")

    lines += ["", "## By family", "", "| Family | Kind | Questions | Score, worked | Score, instinct | Worked 90% hits "
              "| Worked answers above the estimate |", "|---|---|---|---|---|---|---|"]
    for family, s in report["families"]["worked"].items():
        si = report["families"]["instinct"][family]
        above = f"{s['fell']['above'] / s['fell']['n']:.0%}" if s["n"] and s["fell"]["n"] else "—"
        lines.append(f"| `{family}` | {KINDS[family]} | {s['n']} | {sc(s.get('score_mean'))} | {sc(si.get('score_mean'))} "
                     f"| {frac(s['p90']['hits'], s['n']) if s['n'] else '—'} | {above} |")

    lines += ["", "## Questions", "", "Each answer is shown as estimate [90% interval], ✓ or ✗ for whether the 50% "
              "and 90% intervals contain the true answer, and its score.", "",
              "| # | Question | True answer | Instinct | Worked |", "|---|---|---|---|---|"]
    for r in report["questions"]:
        cells = []
        for phase in PHASES:
            c = r[phase]
            if c["status"] != "ok":
                cells.append(f"{c['status']} · {sc(c['score'])}")
                continue
            marks = " ".join(f"{key[1:]}{'✓' if hit else '✗'}" for key, hit in c["hits"].items())
            cells.append(f"{num(c['estimate'])} [{num(c['p90'][0])}, {num(c['p90'][1])}] {marks} · {sc(c['score'])}")
        lines.append(f"| {r['q']} | {r['short']} | {num(r['answer'])} | {cells[0]} | {cells[1]} |")
    return "\n".join(lines) + "\n"


def index(runs):
    """A table of runs, newest suite runs first: (directory name, report) pairs, read from report.json."""
    def where(meta):
        return f"suite {meta['suite']}" if meta.get("suite") else f"seed `{meta['seed']}`"

    rows = sorted(runs, key=lambda r: (not r[1]["meta"].get("suite"), r[1]["meta"]["started"], r[0]))
    lines = ["| Run | Model | Prompts | Questions | Score, worked [90% interval] | Score, instinct "
             "| Worked 50% / 90% hits | Worked answers above the estimate | Reasoning tokens per answer, instinct / worked "
             "| Cost |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name, rep in rows:
        meta, worked, instinct = rep["meta"], rep["phases"]["worked"], rep["phases"]["instinct"]
        fell = worked.get("fell") or {}
        above = f"{fell['above'] / fell['n']:.0%}" if fell.get("n") else "—"
        hits = f"{worked['p50']['hits']} / {worked['p90']['hits']} of {worked['n']}" if worked["n"] else "—"
        cost = f"${rep['cost']:.3f}" if rep.get("cost") else "—"
        thought = [(rep["phases"][p].get("tokens") or {}).get("reasoning") for p in PHASES]
        thought = "—" if None in thought else f"{thought[0]:,.0f} / {thought[1]:,.0f}"
        lines.append(f"| [{name}]({name}/report.md) | {meta['model']} | {meta.get('prompts', 'standard')} "
                     f"| {where(meta)}, {meta['count']} | {sc(worked['all']['score_mean'])}{ci(worked['all']['score_ci'])} "
                     f"| {sc(instinct['all']['score_mean'])} | {hits} | {above} | {thought} | {cost} |")
    return "\n".join(lines) + "\n"


def pool(reports, names):
    """Worked answers pooled over several runs, by family: how consistent a model's leans and misses are."""
    models = sorted({rep["meta"]["model"] for rep in reports})
    rows = [r for rep in reports for r in rep["questions"] if r["worked"]["status"] == "ok"]
    lines = ["# Calibench: runs pooled", "",
             f"Worked answers from {len(reports)} runs ({', '.join(names)}) of {', '.join(models)}: "
             f"{len(rows)} answered questions. A question asked in several runs counts once per run.", ""]
    if len(models) > 1:
        lines += ["**Note:** these runs are of different models, so pooled numbers mix them.", ""]
    lines += ["| Family | Kind | Answers | Score | 90% intervals containing the answer [90% interval] "
              "| True answer above the estimate [90% interval] |", "|---|---|---|---|---|---|"]

    def line(label, kind, group):
        n = len(group)
        hits = sum(r["worked"]["hits"]["p90"] for r in group)
        above = sum(1.0 if r["answer"] > r["worked"]["estimate"] else 0.5 if r["answer"] == r["worked"]["estimate"]
                    else 0.0 for r in group)
        return (f"| {label} | {kind} | {n} | {sc(statistics.fmean(r['worked']['score'] for r in group))} "
                f"| {frac(hits, n)}{ci(wilson(hits, n), pct)} | {above / n:.0%}{ci(wilson(round(above), n), pct)} |")

    for family in sorted({r["family"] for r in rows}, key=lambda f: (KINDS[f], f)):
        lines.append(line(f"`{family}`", KINDS[family], [r for r in rows if r["family"] == family]))
    lines.append(line("**all**", "", rows))
    lines += ["", "A family whose interval for *above the estimate* excludes 50% leans consistently: above 50% means "
              "the model underestimates it, below 50% that it overestimates. An answer equal to the estimate counts "
              "as half above."]
    return "\n".join(lines) + "\n"


def consistency(reports, names):
    """What several runs of one model on the same questions say beyond each run: whether the runs'
    disagreement shows where the model is wrong better than its stated intervals do, and whether
    averaging the runs' forecasts helps."""
    import math

    keys = [[r["key"] for r in rep["questions"]] for rep in reports]
    if len(reports) < 2 or any(sorted(k) != sorted(keys[0]) for k in keys):
        return "Consistency needs two or more runs asked the same questions.\n"
    by_key = [{r["key"]: r for r in rep["questions"]} for rep in reports]
    rows = []
    for key in keys[0]:
        cells = [b[key] for b in by_key]
        if any(c["worked"]["status"] != "ok" for c in cells):
            continue
        family, y = cells[0]["family"], cells[0]["answer"]
        shift = offset(family)

        def g(v):
            return math.log(max(v + shift, 1e-3))

        answers = [c["worked"] for c in cells]
        logs = [g(a["estimate"]) for a in answers]
        averaged = {"estimate": None, "p50": [], "p90": []}
        for name, pick in (("estimate", lambda a: a["estimate"]), ("p50lo", lambda a: a["p50"][0]),
                           ("p50hi", lambda a: a["p50"][1]), ("p90lo", lambda a: a["p90"][0]),
                           ("p90hi", lambda a: a["p90"][1])):
            value = math.exp(statistics.fmean(g(pick(a)) for a in answers)) - shift   # quantiles averaged on the log scale
            if name == "estimate":
                averaged["estimate"] = value
            else:
                averaged[name[:3]].append(value)
        # Held out: run j's error against the spread of the *other* runs' estimates, which share nothing
        # with it. (The spread of all runs bounds their mean error from below, a correlation by construction.)
        held_out = []
        for j, a in enumerate(answers):
            others = logs[:j] + logs[j + 1:]
            held_out.append({"spread": max(others) - min(others) if len(others) >= 2 else None,
                             "width": g(a["p90"][1]) - g(a["p90"][0]), "error": abs(logs[j] - g(y))})
        rows.append({
            "agree": len({a["estimate"] for a in answers}) == 1,
            "right": all(a["estimate"] == y for a in answers),
            "hits90": [inside(a["p90"], y) for a in answers],
            "held_out": held_out,
            "single": statistics.fmean(c["worked"]["score"] for c in cells),
            "averaged": log_wis(averaged, y, shift),
        })
    n = len(rows)
    models = sorted({rep["meta"]["model"] for rep in reports})
    prompts = sorted({rep["meta"].get("prompts", "standard") for rep in reports})
    agree = [r for r in rows if r["agree"]]
    disagree = [r for r in rows if not r["agree"]]

    def cover(group):
        hits = [h for r in group for h in r["hits90"]]
        return frac(sum(hits), len(hits)) if hits else "—"

    def corr(field):
        if field == "spread" and len(reports) < 3:
            return "— (needs three or more runs)"

        def rho(sample):
            pairs = [(h[field], h["error"]) for r in sample for h in r["held_out"]]
            return spearman([p[0] for p in pairs], [p[1] for p in pairs])
        return f"{sc(rho(rows))}{ci(bootstrap(rows, rho))}"

    gain = [r["single"] - r["averaged"] for r in rows]
    lines = ["# Calibench: consistency across runs", "",
             f"{len(reports)} runs ({', '.join(names)}) of {', '.join(models)}, with {' and '.join(prompts)} prompts, on the "
             f"same questions: {n} answered in every run. Worked answers only.", ""]
    if len(models) > 1 or len(prompts) > 1:
        lines += ["**Note:** these runs differ in model or prompts, so their disagreement isn't only sampling.", ""]
    lines += ["| | |", "|---|---|",
              f"| Questions where every run gave the same estimate | {frac(len(agree), n)} |",
              f"| … and that estimate was exactly right | {frac(sum(r['right'] for r in agree), len(agree))} |",
              f"| 90% intervals containing the answer, when the runs agree | {cover(agree)} |",
              f"| 90% intervals containing the answer, when they disagree | {cover(disagree)} |",
              f"| Rank correlation with a run's error: the other runs' disagreement [90% interval] | {corr('spread')} |",
              f"| Rank correlation with a run's error: its own stated 90% width [90% interval] | {corr('width')} |",
              f"| Score of a single run, mean | {sc(statistics.fmean(r['single'] for r in rows))} |",
              f"| Score of the runs' averaged forecast | {sc(statistics.fmean(r['averaged'] for r in rows))} |",
              f"| Improvement from averaging [90% interval] | {sc(statistics.fmean(gain))}{ci(bootstrap_mean(gain))} |",
              "", "A run's *error* is the distance of its estimate from the true answer on the log scale. The *other "
              "runs' disagreement* is the spread of the other runs' estimates on the same scale: it shares no estimate "
              "with the error it is compared with, so the correlation isn't built in. A correlation near 1 means the "
              "signal ranks the answers that are most wrong; the two rows compare the model's inconsistency with its "
              "stated uncertainty as warnings. Intervals are bootstraps over questions. The averaged forecast averages "
              "each of the five stated values across runs on the log scale."]
    return "\n".join(lines) + "\n"


def compare(reports, names=None):
    """Compare runs on the same questions. Unanswered questions score as the know-nothing answer."""
    names = names or [rep["meta"]["model"] for rep in reports]
    keys = [[r["key"] for r in rep["questions"]] for rep in reports]
    if any(sorted(k) != sorted(keys[0]) for k in keys):
        return ("These runs weren't asked the same questions. Run every model with the same --suite, "
                "or the same --seed, --count and --families, on the same Python.\n")
    order = keys[0]                      # the questions' own order, so intervals match each run's report
    models = [rep["meta"]["model"] for rep in reports]
    stats = []
    for rep, name, model in zip(reports, names, models):
        by_key = {r["key"]: r for r in rep["questions"]}
        rows = [by_key[k] for k in order]
        ok = [r for r in rows if r["worked"]["status"] == "ok"]
        scores = [r["worked"]["score"] for r in rows]
        prompts = rep["meta"].get("prompts", "standard")
        stats.append({
            "label": (model if models.count(model) == 1 else f"{model} ({name})")
            + (f" [{prompts} prompts]" if prompts != "standard" else ""),
            "model": model,
            "prompts": prompts,
            "scores": scores,
            "mean": statistics.fmean(scores),
            "instinct": statistics.fmean(r["instinct"]["score"] for r in rows),
            "answered": len(ok),
            "hits50": sum(r["worked"]["hits"]["p50"] for r in ok),
            "hits90": sum(r["worked"]["hits"]["p90"] for r in ok),
            "hits90_by_key": [r["worked"].get("hits", {}).get("p90") for r in rows],
        })
    stats.sort(key=lambda s: s["mean"])
    best, n = stats[0], len(order)
    pythons = {rep["meta"]["python"] for rep in reports}
    lines = ["# Calibench comparison", "",
             f"{n} questions, the same for every run. Scores are for worked answers unless marked; lower is better. "
             "An unanswered question scores as the know-nothing answer.", ""]
    if len(pythons) > 1:
        lines += [f"**Note:** runs used different Python versions ({', '.join(sorted(pythons))}).", ""]
    lines += ["| Run | Answered | Score [90% interval] | Median | 50% hits | 90% hits | Instinct score "
              "| Difference from the best [90% interval] | Questions needed to separate it |",
              "|---|---|---|---|---|---|---|---|---|"]
    for s in stats:
        if s is best:
            diff, needed = "best", ""
        else:
            d = [a - b for a, b in zip(s["scores"], best["scores"])]
            diff = f"+{sc(statistics.fmean(d))}{ci(bootstrap_mean(d))}"
            k = questions_needed(d)
            needed = "—" if k is None else f"about {k:,}"
        lines.append(f"| {s['label']} | {s['answered']} of {n} | {sc(s['mean'])}{ci(bootstrap_mean(s['scores']))} "
                     f"| {sc(statistics.median(s['scores']))} | {frac(s['hits50'], s['answered'])} "
                     f"| {frac(s['hits90'], s['answered'])} | {sc(s['instinct'])} | {diff} | {needed} |")
    lines += ["", "The interval for a difference is a bootstrap over questions. When it includes zero, these "
              "questions don't separate the two runs; more questions would. *Questions needed* is how many questions "
              "a difference this size would need to be separated with 80% power, from the spread of the per-question "
              "differences seen here; heavy tails make it a lower bound."]

    pairs = [(a, b) for i, a in enumerate(stats) for b in stats[i + 1:] if a["model"] == b["model"]]
    if pairs:
        lines += ["", "## Runs of the same model", "", "Runs of the same model on the same questions. With the same "
                  "prompts this is test–retest: a good benchmark gives a model nearly the same score each time. With "
                  "different prompts it measures sensitivity to wording, which matters only if it exceeds test–retest.", "",
                  "| Runs | Prompts | Difference in score [90% interval] | Rank correlation of question scores | Same 90% hit or miss |",
                  "|---|---|---|---|---|"]
        for a, b in pairs:
            d = [x - y for x, y in zip(b["scores"], a["scores"])]
            both = [(x, y) for x, y in zip(a["hits90_by_key"], b["hits90_by_key"]) if x is not None and y is not None]
            rho = spearman(a["scores"], b["scores"])
            same = "same" if a["prompts"] == b["prompts"] else f"{a['prompts']} / {b['prompts']}"
            lines.append(f"| {a['label']} / {b['label']} | {same} | {sc(statistics.fmean(d))}{ci(bootstrap_mean(d))} "
                         f"| {sc(rho)} | {frac(sum(x == y for x, y in both), len(both))} |")
    return "\n".join(lines) + "\n"
