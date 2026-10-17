"""Draw questions from a seed. The same seed always gives the same questions on the same Python."""
import hashlib
import json
import random

from .families import FAMILIES, KINDS


def rng_from_seed(seed):
    """Any string works as a seed; hashing it means similar seeds give unrelated questions."""
    return random.Random(int(hashlib.sha256(str(seed).encode()).hexdigest(), 16))


def draw(rng, count=12, families=None):
    """Draw `count` questions, using every family once before any family repeats.

    A question already drawn is drawn again, so a run doesn't ask the same thing twice
    unless a family runs out of different questions.
    """
    names = sorted(families or FAMILIES)
    unknown = set(names) - set(FAMILIES)
    if unknown:
        raise ValueError(f"unknown families: {', '.join(sorted(unknown))}")
    order = []
    while len(order) < count:
        batch = names[:]
        rng.shuffle(batch)
        order += batch
    questions, seen = [], set()
    for i, family in enumerate(order[:count], 1):
        for _ in range(100):
            params, text, short = FAMILIES[family][0](rng)
            key = (family, json.dumps(params, sort_keys=True))
            if key not in seen:
                break
        seen.add(key)
        questions.append({"q": i, "family": family, "kind": KINDS[family], "params": params,
                          "short": short, "text": text})
    return questions


def solve(question):
    return FAMILIES[question["family"]][1](**question["params"])
