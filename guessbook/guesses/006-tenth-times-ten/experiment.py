"""Guess 006: for how many n in 1..100 does (0.1 * n) * 10 == n hold exactly?"""
passes = [n for n in range(1, 101) if (0.1 * n) * 10 == n]
fails = [n for n in range(1, 101) if (0.1 * n) * 10 != n]

print(f"{len(passes)} of 100 come back exactly")
print("fail:", fails)
print("claim:", 60 <= len(passes) <= 80)
