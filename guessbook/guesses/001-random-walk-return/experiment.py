"""Guess 001: fraction of 2D simple random walks that return to the start within 1,000 steps."""
import random

WALKS, STEPS, SEED = 20_000, 1_000, 1
MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1))
rng = random.Random(SEED)

returned = 0
for _ in range(WALKS):
    x = y = 0
    for _ in range(STEPS):
        dx, dy = MOVES[rng.randrange(4)]
        x += dx
        y += dy
        if x == 0 and y == 0:
            returned += 1
            break

fraction = returned / WALKS
print(f"{returned} of {WALKS} walks returned within {STEPS} steps: {fraction:.4f}")
print("claim:", 0.65 <= fraction <= 0.70)
