"""Guess 005: exact probability that 20 die rolls miss at least one face.

Computed with a Markov chain on the number of distinct faces seen, a different method
from the inclusion-exclusion used in the guess.
"""
from fractions import Fraction

ROLLS = 20
seen = [Fraction(0)] * 7          # seen[k] = P(exactly k distinct faces so far)
seen[0] = Fraction(1)
for _ in range(ROLLS):
    nxt = [Fraction(0)] * 7
    for k, pr in enumerate(seen):
        if pr:
            nxt[k] += pr * Fraction(k, 6)
            if k < 6:
                nxt[k + 1] += pr * Fraction(6 - k, 6)
    seen = nxt

missing = 1 - seen[6]
print(f"P(a face is missing after {ROLLS} rolls) = {missing} ≈ {float(missing):.6f}")
print("claim:", Fraction(150, 1000) <= missing <= Fraction(154, 1000))
