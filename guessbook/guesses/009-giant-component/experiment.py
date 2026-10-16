"""Guess 009: share of vertices in the largest component of G(1000, 2/999), over 20 graphs."""
import collections
import random

N, GRAPHS, SEED = 1_000, 20, 9
P = 2 / (N - 1)
rng = random.Random(SEED)


def find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


shares = []
for _ in range(GRAPHS):
    parent = list(range(N))
    for i in range(N):
        for j in range(i + 1, N):
            if rng.random() < P:
                a, b = find(parent, i), find(parent, j)
                if a != b:
                    parent[a] = b
    sizes = collections.Counter(find(parent, v) for v in range(N))
    shares.append(max(sizes.values()) / N)

mean = sum(shares) / GRAPHS
print("largest-component shares:", " ".join(f"{s:.3f}" for s in shares))
print(f"mean over {GRAPHS} graphs: {mean:.4f}")
print("claim:", 0.780 <= mean <= 0.815)
