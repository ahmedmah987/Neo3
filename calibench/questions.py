"""Draw questions from a seed. The same seed always gives the same questions on the same Python."""
import hashlib
import json
import random

from .families import FAMILIES, KINDS

# Standard suites: a fixed set of questions every model is asked, so nobody chooses the seed. The seed
# was fixed before any question was drawn from it. Knowledge answers depend on the Python version, so
# a suite names the one its answers are settled on. A new suite gets a new name; a suite never changes.
SUITES = {
    "v1": {"seed": "calibench-v1", "count": 104, "python": "3.13",      # every family 8 times
           "sha256": "8a91a6e055e6f0f71efb4e615e42cb16725e35d5faac19b7fe51b78b6681aa51"},
}


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


def fingerprint(questions):
    """A hash of a set of questions, to check that a suite still draws exactly what it always has."""
    return hashlib.sha256(json.dumps(questions, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def solve(question):
    return FAMILIES[question["family"]][1](**question["params"])
