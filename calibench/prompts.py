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

PROMPTS = {"instinct": INSTINCT, "worked": WORKED}

RETRY = ("\n\nYour previous reply didn't end with a valid JSON object of that form. "
         "Answer again and end with exactly that JSON object, using plain numbers.")

JSON_OBJECT = re.compile(r"\{[^{}]*\}")


def _number(value):
    if isinstance(value, str):
        value = float(value.replace(",", "").replace("_", "").strip())
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"not a finite number: {value!r}")
    return value


def _interval(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"not an interval: {value!r}")
    return sorted(_number(v) for v in value)


def parse_answer(reply):
    """The last JSON object in the reply that has an estimate, with intervals as sorted pairs.

    An estimate outside its own intervals is accepted; each interval is scored on its own.
    """
    for candidate in reversed(JSON_OBJECT.findall(reply or "")):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "estimate" in data:
            try:
                return {"estimate": _number(data["estimate"]),
                        "p50": _interval(data.get("p50")), "p90": _interval(data.get("p90"))}
            except (TypeError, ValueError):
                continue
    raise ValueError("no JSON object with an estimate and two intervals")
