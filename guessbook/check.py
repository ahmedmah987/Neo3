"""Checks for the question families, on small cases with known answers.

Run with: python3 guessbook/check.py
Prints only pass or fail, never a value from a real round.
"""
import itertools
import random

import families as F

failures = []


def check(name, ok):
    print(("ok    " if ok else "FAIL  ") + name)
    if not ok:
        failures.append(name)


def brute_lis(seq):
    best = [1] * len(seq)
    for i, x in enumerate(seq):
        for j in range(i):
            if seq[j] < x:
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


# Every listed module resolves to a single .py file.
missing = []
for name in F.STDLIB_MODULES:
    try:
        F.module_path(name)
    except ValueError:
        missing.append(name)
check("stdlib modules are single files" + (f" (not: {missing})" if missing else ""), not missing)

check("primes in range matches trial division",
      all(F.solve_primes_in_range(a, a + 700) == sum(map(is_prime, range(a, a + 701)))
          for a in (100_000, 123_457, 999_000)))
check("digit sum of 2^10 is 7 and of 2^15 is 26",
      F.solve_digit_sum_pow2(10) == 7 and F.solve_digit_sum_pow2(15) == 26)
check("patience sorting gives the exact LIS of all 720 permutations of 6",
      all(F.lis_length(p) == brute_lis(p) for p in itertools.permutations(range(6))))
# The average LIS over all permutations of 3 is exactly 2.
check("average LIS for n = 3 is close to 2", abs(F.solve_lis(3, 1) - 2) < 0.1)

check("mean distance in the unit square is about 0.5214", abs(F.solve_rect_distance(1, 7) - 0.5214) < 0.004)
check("Collatz from 27 takes 111 steps", F.solve_collatz_steps(27) == 111)
check("expected draws until a repeat with 365 values is about 24.6166", abs(F.solve_birthday(365) - 24.6166) < 1e-3)

# Walk of 2 steps: ++ peaks at 2, +- at 1, the other two at 0, so the mean is 3/4.
check("expected peak of a 2-step walk is 3/4", abs(F.solve_walk_max(2, 3) - 0.75) < 0.05)

# make() works for every family on a throwaway seed (values are not printed).
rng = random.Random("throwaway")
for name, (make, solve) in sorted(F.FAMILIES.items()):
    params, text, short = make(rng)
    check(f"{name} draws a question", bool(text) and bool(short) and isinstance(params, dict))

print("\nall checks passed" if not failures else f"\n{len(failures)} failure(s)")
raise SystemExit(1 if failures else 0)
