"""Reports for one run, and comparisons between runs."""
import collections
import json
import statistics

from .families import KINDS
from .questions import SUITES
from .scoring import (BIN_SHARES, BINS, KNOW_NOTHING, LEVELS, PHASES, bootstrap_mean, inside, log_wis, offset,
                      spearman, summarize)


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
    report = {"meta": meta, "suite": suite_status(meta), "phases": {}, "kinds": {}, "families": {}, "questions": []}
    for phase in PHASES:
        recs = [records.get((q["q"], phase)) for q in questions]
        ok = [(q, r) for q, r in zip(questions, recs) if r and r["status"] == "ok"]
        statuses = collections.Counter(r["status"] if r else "missing" for r in recs)
        every = [log_wis(r["answer"] if r and r["status"] == "ok" else KNOW_NOTHING, truth[q["q"]], offset(q["family"]))
                 for q, r in zip(questions, recs)]
        report["phases"][phase] = {
            "asked": len(questions), "statuses": dict(statuses),
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
                for name in ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens", "reasoning_tokens"):
                    tokens[name] += attempt.get(name) or 0
                cost += attempt.get("cost") or 0
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
    report["served_models"] = sorted(served)
    report["tokens"] = {k: v for k, v in tokens.items() if v}
    report["cost"] = round(cost, 6) if cost else None
    return report


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
        lines += ["", "Tokens: " + ", ".join(f"{k.replace('_', ' ')} {v:,}" for k, v in report["tokens"].items()) + "."]
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

    lines += ["", "## By kind of question", "",
              "Knowledge questions ask what is known (the Python standard library, the Unicode database); statistical "
              "ones need noise or irregularity modelled; exact ones have a closed-form answer that must be evaluated.", "",
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
             "| Worked 50% / 90% hits | Worked answers above the estimate | Cost |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, rep in rows:
        meta, worked, instinct = rep["meta"], rep["phases"]["worked"], rep["phases"]["instinct"]
        fell = worked.get("fell") or {}
        above = f"{fell['above'] / fell['n']:.0%}" if fell.get("n") else "—"
        hits = f"{worked['p50']['hits']} / {worked['p90']['hits']} of {worked['n']}" if worked["n"] else "—"
        cost = f"${rep['cost']:.3f}" if rep.get("cost") else "—"
        lines.append(f"| [{name}]({name}/report.md) | {meta['model']} | {meta.get('prompts', 'standard')} "
                     f"| {where(meta)}, {meta['count']} | {sc(worked['all']['score_mean'])}{ci(worked['all']['score_ci'])} "
                     f"| {sc(instinct['all']['score_mean'])} | {hits} | {above} | {cost} |")
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
    lines += ["| Run | Answered | Score [90% interval] | Median | 50% hits | 90% hits | Instinct score | Difference from the best [90% interval] |",
              "|---|---|---|---|---|---|---|---|"]
    for s in stats:
        if s is best:
            diff = "best"
        else:
            d = [a - b for a, b in zip(s["scores"], best["scores"])]
            diff = f"+{sc(statistics.fmean(d))}{ci(bootstrap_mean(d))}"
        lines.append(f"| {s['label']} | {s['answered']} of {n} | {sc(s['mean'])}{ci(bootstrap_mean(s['scores']))} "
                     f"| {sc(statistics.median(s['scores']))} | {frac(s['hits50'], s['answered'])} "
                     f"| {frac(s['hits90'], s['answered'])} | {sc(s['instinct'])} | {diff} |")
    lines += ["", "The interval for a difference is a bootstrap over questions. When it includes zero, these "
              "questions don't separate the two runs; more questions would."]

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
