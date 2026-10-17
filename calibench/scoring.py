"""Scoring: interval scores, coverage, and what coverage says about calibration.

All scores are relative to the true answer, so questions of very different sizes can be averaged.
Lower is better for every score, and none can be improved by stating intervals other than
the ones you believe.
"""
import math
import statistics

PHASES = ("instinct", "worked")
LEVELS = (("p50", 0.5), ("p90", 0.1))        # interval, and alpha for a central (1 − alpha) interval


def inside(interval, x):
    return interval[0] <= x <= interval[1]


def interval_score(interval, x, alpha):
    """Gneiting and Raftery's score for a central (1 − alpha) interval, relative to the answer.

    Width plus 2/alpha times any distance by which the answer falls outside. It is minimised
    by giving the true alpha/2 and 1 − alpha/2 quantiles.
    """
    lo, hi = interval
    return ((hi - lo) + 2 / alpha * (max(0, lo - x) + max(0, x - hi))) / (abs(x) or 1)


def weighted_interval_score(answer, x):
    """Bracher et al.'s weighted interval score: the estimate read as a median, and both intervals.

    It approximates the continuous ranked probability score of the belief the answer describes.
    """
    total = 0.5 * abs(answer["estimate"] - x) / (abs(x) or 1)
    total += sum(alpha / 2 * interval_score(answer[key], x, alpha) for key, alpha in LEVELS)
    return total / (len(LEVELS) + 0.5)


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


def summarize(pairs):
    """Metrics for a list of (answer, truth) pairs.

    Coverage verdicts leave out single-number intervals: an exact answer that is known is
    knowledge, not evidence about calibration. Those are counted separately.
    """
    n = len(pairs)
    if not n:
        return {"n": 0}
    out = {"n": n}
    wis = [weighted_interval_score(a, x) for a, x in pairs]
    out["wis_mean"] = statistics.fmean(wis)
    out["wis_median"] = statistics.median(wis)
    for key, alpha in LEVELS:
        level = round(1 - alpha, 2)
        ranged = [(a, x) for a, x in pairs if a[key][0] != a[key][1]]
        out[key] = {
            "level": level,
            "interval_score": statistics.fmean(interval_score(a[key], x, alpha) for a, x in pairs),
            "hits": sum(inside(a[key], x) for a, x in pairs),
            "ranged": len(ranged),
            "ranged_hits": sum(inside(a[key], x) for a, x in ranged),
        }
        out[key]["verdict"] = verdict(out[key]["ranged_hits"], out[key]["ranged"], level)
    points = [(a, x) for a, x in pairs if a["p90"][0] == a["p90"][1]]
    out["certain"] = len(points)
    out["certain_right"] = sum(a["estimate"] == x for a, x in points)
    out["median_error"] = statistics.median(abs(a["estimate"] - x) / (abs(x) or 1) for a, x in pairs)
    return out
