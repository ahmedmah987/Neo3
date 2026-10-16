"""Guess 003: average Collatz step count to reach 1, over n = 1..1,000,000."""
N = 1_000_000

steps = [0] * (N + 1)
for n in range(2, N + 1):
    m, k = n, 0
    while m >= n:                      # walk until we land on a number already counted
        m = m // 2 if m % 2 == 0 else 3 * m + 1
        k += 1
    steps[n] = k + steps[m]

average = sum(steps[1:]) / N
longest = max(range(1, N + 1), key=steps.__getitem__)
print(f"average steps to reach 1 for n = 1..{N:,}: {average:.2f}")
print(f"longest run: n = {longest:,} with {steps[longest]} steps")
print("claim:", 115 <= average <= 150)
