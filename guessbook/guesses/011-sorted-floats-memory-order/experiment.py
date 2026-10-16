"""Guess 011: does allocating the ordered floats in sorted order make sorting them fast?"""
import platform
import random
import sys
import timeit

rng = random.Random(8)                      # same data as guess 008
data = [rng.random() for _ in range(1_000_000)]
same_objects = sorted(data)                 # 008's ordered list: shared objects, shuffled memory order
fresh = [x + 0.0 for x in same_objects]     # new float objects, created in sorted order

assert fresh == same_objects and fresh[0] is not same_objects[0]


def best(lst):
    return min(timeit.repeat(lambda: sorted(lst), number=1, repeat=5))


t_random, t_same, t_fresh = best(data), best(same_objects), best(fresh)
print(f"Python {sys.version.split()[0]} on {platform.machine()}")
print(f"shuffled: {t_random * 1000:.1f} ms")
print(f"ordered, shared objects: {t_same * 1000:.1f} ms (ratio {t_random / t_same:.1f})")
print(f"ordered, fresh objects:  {t_fresh * 1000:.1f} ms (ratio {t_random / t_fresh:.1f})")
print("claim:", t_random / t_fresh >= 10)
