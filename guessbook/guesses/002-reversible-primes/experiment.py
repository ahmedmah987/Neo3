"""Guess 002: primes below 1,000,000 whose digit reversal is also prime."""
N = 1_000_000

sieve = bytearray([1]) * N
sieve[0] = sieve[1] = 0
for i in range(2, int(N ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i::i] = bytes(len(range(i * i, N, i)))

primes = [p for p in range(N) if sieve[p]]
# A prime never ends in 0, so its reversal has the same number of digits and stays below N.
reversible = [p for p in primes if sieve[int(str(p)[::-1])]]

print(f"{len(primes)} primes below {N:,}; {len(reversible)} stay prime when reversed")
print("claim:", 10_000 <= len(reversible) <= 13_000)
