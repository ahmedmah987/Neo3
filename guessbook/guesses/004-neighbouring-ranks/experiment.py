"""Guess 004: chance that a shuffled deck has two neighbouring cards of the same rank."""
import random

TRIALS, SEED = 200_000, 4
rng = random.Random(SEED)
deck = [rank for rank in range(13) for _ in range(4)]

hits = 0
for _ in range(TRIALS):
    rng.shuffle(deck)
    if any(a == b for a, b in zip(deck, deck[1:])):
        hits += 1

estimate = hits / TRIALS
stderr = (estimate * (1 - estimate) / TRIALS) ** 0.5
print(f"{hits} of {TRIALS} shuffles had a neighbouring pair: {estimate:.4f} ± {stderr:.4f}")
print("claim:", 0.94 <= estimate <= 0.97)
