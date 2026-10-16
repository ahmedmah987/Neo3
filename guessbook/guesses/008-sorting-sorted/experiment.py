"""Guess 008: speed of sorted() on ordered versus shuffled floats."""
import platform
import random
import sys
import timeit

rng = random.Random(8)
data = [rng.random() for _ in range(1_000_000)]
ordered = sorted(data)

t_random = min(timeit.repeat(lambda: sorted(data), number=1, repeat=5))
t_ordered = min(timeit.repeat(lambda: sorted(ordered), number=1, repeat=5))
ratio = t_random / t_ordered

print(f"Python {sys.version.split()[0]} on {platform.machine()}")
print(f"shuffled: {t_random * 1000:.1f} ms, already sorted: {t_ordered * 1000:.1f} ms, ratio {ratio:.1f}")
print("claim:", ratio >= 10)
