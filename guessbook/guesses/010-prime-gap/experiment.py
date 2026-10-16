"""Guess 010: largest gap between consecutive primes below 1,000,000."""
N = 1_000_000

sieve = bytearray([1]) * N
sieve[0] = sieve[1] = 0
for i in range(2, int(N ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i::i] = bytes(len(range(i * i, N, i)))

gap, start, prev = 0, 0, 2
for p in range(3, N):
    if sieve[p]:
        if p - prev > gap:
            gap, start = p - prev, prev
        prev = p

print(f"largest gap below {N:,}: {gap}, from {start:,} to {start + gap:,}")
print("claim:", (gap, start) == (114, 492_113))
