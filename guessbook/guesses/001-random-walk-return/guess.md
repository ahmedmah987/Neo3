---
claim: "Between 65% and 70% of 20,000 simple random walks on the square grid return to their start within 1,000 steps."
p: 0.75
---

# 001 · Random walk coming home

**Question.** A walker starts at the origin of the square grid and takes 1,000 steps, each one unit up, down, left or right with equal chance. What fraction of walkers stand on the origin again at some point within those steps?

**Claim.** Between 65% and 70%, measured over 20,000 walks. **Probability: 75%.**

**Reasoning.** My first instinct was the textbook asymptotic: the chance of no return after n steps falls like π / ln n, which at n = 1,000 says about 45% never return. But that formula is only leading order. A sharper route is the last-exit identity, 1 = Σₖ P(at origin at step k) · P(no return in the remaining n − k steps), which gives P(no return by n) ≤ 1 / G, where G is the expected number of visits to the origin up to step n. Here P(at origin at step 2j) = (C(2j, j) / 4ʲ)² ≈ 1 / (πj), so G ≈ 1 + (H₅₀₀ − ζ(2)/4) / π ≈ 3.04. That bounds non-return at about 33%, so returns are at least about 67%. Correcting for the bound's slack moves non-return down only slightly, to roughly 32%. I expect about 67–68%, with Monte Carlo noise of about ±0.3%.

**Did I already know?** The π / ln n asymptotic, yes. The value at 1,000 steps, no; it's derived above.
