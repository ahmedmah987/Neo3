"""Scoring: interval scores on a log scale, coverage, and their uncertainty.

Answers are scored on a log scale: log(x) for continuous answers, which are all at least 0.5, and
log(1 + x) for counts, which can be 0. A fixed increasing transform keeps the scores proper (stating
the quantiles you believe is the best strategy), makes questions of every size comparable, and treats
a miss by a factor the same in either direction. A score is in natural-log units: 0.1 is roughly a
10% miss. Lower is better.

The relative interval score (divided by the true answer) is kept only for the guessbook. It is not
proper: dividing by the answer rewards stating intervals lower than you believe. See METHODOLOGY.md.
"""
import math
import random
import statistics

PHASES = ("instinct", "worked")
LEVELS = (("p50", 0.5), ("p90", 0.1))        # interval, and alpha for a central (1 − alpha) interval
FLOOR = 1e-3                                  # a stated value (plus its offset) below this counts as this
KNOW_NOTHING = {"estimate": 100, "p50": [30, 300], "p90": [3, 3000]}   # how an unanswered question is scored
SCORING = "log-wis-1"           # log(x), or log(1 + x) for counts; weighted interval score


def inside(interval, x):
    return interval[0] <= x <= interval[1]


def offset(family):
    from .families import COUNTS

    return 1 if family in COUNTS else 0


def _log(value, shift):
    return math.log(max(value + shift, FLOOR))


def log_interval_score(interval, x, alpha, shift=0):
    """Gneiting and Raftery's interval score for a central (1 − alpha) interval, on a log scale.

    Width plus 2/alpha times any distance by which the answer falls outside, after taking
    log(value + shift). Quantiles carry over through a fixed increasing transform, so it is
    minimised by stating the true alpha/2 and 1 − alpha/2 quantiles.
    """
    if x + shift <= 0:
        raise ValueError("log-scale scores need a positive true answer, or a count with shift 1")
    lo, hi, t = _log(interval[0], shift), _log(interval[1], shift), _log(x, shift)
    return (hi - lo) + 2 / alpha * (max(0, lo - t) + max(0, t - hi))


def log_wis(answer, x, shift=0):
    """Bracher et al.'s weighted interval score on a log scale: the estimate read as a median,
    and both intervals. It approximates the continuous ranked probability score of log(answer)."""
    total = 0.5 * abs(_log(answer["estimate"], shift) - _log(x, shift))
    total += sum(alpha / 2 * log_interval_score(answer[key], x, alpha, shift) for key, alpha in LEVELS)
    return total / (len(LEVELS) + 0.5)


def interval_score(interval, x, alpha):
    """The interval score relative to the answer, as the guessbook has always used it. Not proper."""
    lo, hi = interval
    return ((hi - lo) + 2 / alpha * (max(0, lo - x) + max(0, x - hi))) / (abs(x) or 1)


def bootstrap_mean(values, level=0.9, samples=4_000, seed=0):
    """A percentile bootstrap interval for the mean, resampling questions."""
    if len(values) < 2:
        return None
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(samples))
    return [means[int(samples * (1 - level) / 2)], means[int(samples * (1 + level) / 2) - 1]]


def wilson(hits, n, z=1.645):
    """A 90% Wilson interval for a proportion."""
    if not n:
        return None
    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [max(0.0, centre - half), min(1.0, centre + half)]


def verdict(hits, n, level):
    """Whether interval coverage is consistent with the stated level, at about two standard errors."""
    if n < 5:
        return "too few to tell"
    z = (hits - level * n) / math.sqrt(n * level * (1 - level))
    if z <= -2:
        return "too narrow (overconfident)"
    if z >= 2:
        return "too wide (underconfident)"
    return "consistent with calibrated"


def spearman(a, b):
    """Rank correlation, with ties given their average rank."""
    def ranks(values):
        order = sorted(range(len(values)), key=values.__getitem__)
        r = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    try:
        return statistics.correlation(ra, rb)
    except statistics.StatisticsError:      # every score the same in one run
        return None


# The five stated values are quantiles at these levels, so they split the belief into six bins
# that should hold these shares of the true answers.
BINS = ("below the 90% interval", "in the 90% interval, below the 50%", "in the 50% interval, below the estimate",
        "in the 50% interval, above the estimate", "in the 90% interval, above the 50%", "above the 90% interval")
BIN_SHARES = (0.05, 0.20, 0.25, 0.25, 0.20, 0.05)


def bin_weights(answer, x):
    """Which of the six bins the true answer fell in. An answer on a boundary is shared between the
    bins it touches in proportion to their expected shares, as a randomised PIT would place it.
    Values out of order (an estimate outside its own interval) are sorted first."""
    edges = sorted([answer["p90"][0], answer["p50"][0], answer["estimate"], answer["p50"][1], answer["p90"][1]])
    lower, upper = [-math.inf] + edges, edges + [math.inf]
    touched = [i for i in range(6) if lower[i] <= x <= upper[i]]
    total = sum(BIN_SHARES[i] for i in touched)
    return {i: BIN_SHARES[i] / total for i in touched}


def where_answers_fell(pairs):
    """Shares of true answers in each bin, and above the estimate, leaving out single-number answers."""
    ranged = [(a, x) for a, x in pairs if a["p90"][0] != a["p90"][1]]
    counts = [0.0] * 6
    for a, x in ranged:
        for i, w in bin_weights(a, x).items():
            counts[i] += w
    above = sum(1.0 if x > a["estimate"] else 0.5 if x == a["estimate"] else 0.0 for a, x in ranged)
    return {"n": len(ranged), "bins": counts, "above": above,
            "above_ci": wilson(round(above), len(ranged)) if ranged else None}


def summarize(items):
    """Metrics for a list of (answer, truth, shift) triples.

    Coverage verdicts leave out single-number intervals: an exact answer that is known is
    knowledge, not evidence about calibration. Those are counted separately.
    """
    n = len(items)
    if not n:
        return {"n": 0}
    scores = [log_wis(a, x, s) for a, x, s in items]
    pairs = [(a, x) for a, x, _ in items]
    out = {"n": n, "score_mean": statistics.fmean(scores), "score_median": statistics.median(scores),
           "score_ci": bootstrap_mean(scores)}
    for key, alpha in LEVELS:
        level = round(1 - alpha, 2)
        ranged = [(a, x) for a, x in pairs if a[key][0] != a[key][1]]
        hits = sum(inside(a[key], x) for a, x in pairs)
        out[key] = {
            "level": level,
            "interval_score": statistics.fmean(log_interval_score(a[key], x, alpha, s) for a, x, s in items),
            "hits": hits,
            "hits_ci": wilson(hits, n),
            "ranged": len(ranged),
            "ranged_hits": sum(inside(a[key], x) for a, x in ranged),
        }
        out[key]["verdict"] = verdict(out[key]["ranged_hits"], out[key]["ranged"], level)
    points = [(a, x) for a, x in pairs if a["p90"][0] == a["p90"][1]]
    out["certain"] = len(points)
    out["certain_right"] = sum(a["estimate"] == x for a, x in points)
    out["median_error"] = statistics.median(abs(a["estimate"] - x) / max(abs(x), 1) for a, x in pairs)
    out["fell"] = where_answers_fell(pairs)
    return out
