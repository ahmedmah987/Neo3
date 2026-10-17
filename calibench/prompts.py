"""The two prompts a model sees, and reading its answer back."""
import json
import math
import re

INSTINCT = """You are taking part in a calibration test. Answer the question below with your immediate best guess. Don't work it out, calculate or explain: give the number that first comes to mind.

Give a point estimate (a value the answer is as likely to be above as below), a 50% interval (you believe there's a 50% chance the answer lies inside it) and a 90% interval.

Question: {text}

Reply with only this JSON object and nothing else:
{{"estimate": <number>, "p50": [<low>, <high>], "p90": [<low>, <high>]}}"""

WORKED = """You are taking part in a calibration test. Take the time to work the question below out as carefully as you can: recall what you know and calculate where you can. You have no tools. Write as much or as little working as you like.

Then give a point estimate (a value the answer is as likely to be above as below), a 50% interval (you believe there's a 50% chance the answer lies inside it) and a 90% interval. Make the intervals honest: too narrow and the answer will fall outside them too often; too wide and they say less than you know.

Question: {text}

End your reply with this JSON object on its own line:
{{"estimate": <number>, "p50": [<low>, <high>], "p90": [<low>, <high>]}}"""

# A second wording of the same request, to measure how much the wording moves the results. It drops
# the "calibration test" framing, asks for ranges you'd bet on, and says what calibration means.
INSTINCT_ALT = """Quick estimate, please. Without calculating or looking anything up, say what your gut tells you for the question below.

Question: {text}

Give three things: your best single guess (the middle of what you believe), a range you'd bet is 50% likely to contain the true value, and a range you'd bet is 90% likely to contain it. Reply with nothing but this JSON:
{{"estimate": <number>, "p50": [<low>, <high>], "p90": [<low>, <high>]}}"""

WORKED_ALT = """Here is a question with a single numeric answer. Think it through properly before you answer: use what you know, and do whatever calculation you can. No tools are available.

Question: {text}

Then give three things: your best single guess (the middle of what you believe), a range you'd bet is 50% likely to contain the true value, and a range you'd bet is 90% likely to contain it. Calibration matters more than precision: a well-calibrated forecaster's 90% ranges contain the truth about nine times in ten. Finish with this JSON on its own line:
{{"estimate": <number>, "p50": [<low>, <high>], "p90": [<low>, <high>]}}"""

# The same information asked for as five percentiles, to measure whether the format of the question
# (an estimate and two intervals, or percentiles) moves the results. The 5th and 95th percentiles bound
# the 90% interval, the 25th and 75th the 50% interval, and the 50th is the estimate.
INSTINCT_QUANTILES = """You are taking part in a calibration test. Answer the question below with your immediate best guess. Don't work it out, calculate or explain: give the numbers that first come to mind.

Give five percentiles of your belief about the answer: the 5th, 25th, 50th, 75th and 95th. The 5th percentile is a value you think the answer has only a 5% chance of being below, the 50th a value it is as likely to be above as below, and so on.

Question: {text}

Reply with only this JSON object and nothing else:
{{"q05": <number>, "q25": <number>, "q50": <number>, "q75": <number>, "q95": <number>}}"""

WORKED_QUANTILES = """You are taking part in a calibration test. Take the time to work the question below out as carefully as you can: recall what you know and calculate where you can. You have no tools. Write as much or as little working as you like.

Then give five percentiles of your belief about the answer: the 5th, 25th, 50th, 75th and 95th. The 5th percentile is a value you think the answer has only a 5% chance of being below, the 50th a value it is as likely to be above as below, and so on. Make them honest: the answer should fall below your 5th percentile about one time in twenty, and above your 95th about one time in twenty.

Question: {text}

End your reply with this JSON object on its own line:
{{"q05": <number>, "q25": <number>, "q50": <number>, "q75": <number>, "q95": <number>}}"""

PROMPT_SETS = {
    "standard": {"instinct": INSTINCT, "worked": WORKED},
    "alt": {"instinct": INSTINCT_ALT, "worked": WORKED_ALT},
    "quantiles": {"instinct": INSTINCT_QUANTILES, "worked": WORKED_QUANTILES},
}
QUANTILE_KEYS = ("q05", "q25", "q50", "q75", "q95")
PROMPTS = PROMPT_SETS["standard"]

RETRY = ("\n\nYour previous reply didn't end with a valid JSON object of that form. "
         "Answer again and end with exactly that JSON object, using plain numbers.")

JSON_OBJECT = re.compile(r"\{[^{}]*\}")


INTEGER = re.compile(r"[+-]?\d+")


def _number(value):
    if isinstance(value, str):
        text = value.replace(",", "").replace("_", "").strip()
        value = int(text) if INTEGER.fullmatch(text) else float(text)    # whole numbers stay exact
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"not a finite number: {value!r}")
    return value


def _interval(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"not an interval: {value!r}")
    return sorted(_number(v) for v in value)


def parse_answer(reply):
    """The last JSON object in the reply that has an estimate, with intervals as sorted pairs.

    An estimate outside its own intervals is accepted; each interval is scored on its own. An object
    of five percentiles is read as the same thing: the median is the estimate, the 25th and 75th
    percentiles the 50% interval, the 5th and 95th the 90% interval.
    """
    for candidate in reversed(JSON_OBJECT.findall(reply or "")):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "q50" in data and "estimate" not in data:
            try:
                q = {key: _number(data[key]) for key in QUANTILE_KEYS}
                if [q[key] for key in QUANTILE_KEYS] != sorted(q.values()):
                    continue                          # crossing percentiles describe no belief
                return {"estimate": q["q50"], "p50": [q["q25"], q["q75"]], "p90": [q["q05"], q["q95"]]}
            except (KeyError, TypeError, ValueError):
                continue
        if isinstance(data, dict) and "estimate" in data:
            try:
                return {"estimate": _number(data["estimate"]),
                        "p50": _interval(data.get("p50")), "p90": _interval(data.get("p90"))}
            except (TypeError, ValueError):
                continue
    raise ValueError("no JSON object with an estimate and two intervals")
