---
claim: "In random graphs on 1,000 vertices with average degree 2, the largest connected component holds between 78% and 81.5% of the vertices, averaged over 20 graphs."
p: 0.85
---

# 009 · The giant component

**Question.** Build a random graph on 1,000 vertices, joining each pair independently with probability 2/999, so the average degree is 2. What fraction of the vertices lie in the largest connected component, averaged over 20 such graphs?

**Claim.** Between 0.780 and 0.815. **Probability: 85%.**

**Reasoning.** For large graphs with average degree c, the giant component's share s solves s = 1 − e^(−cs). For c = 2: try s = 0.797, then 1 − e^(−1.594) = 1 − 0.203 = 0.797, which is consistent. The size of one graph's giant component varies with a variance of about n·s(1 − s) / (1 − c(1 − s))² ≈ 460, a standard deviation near 2.1% of the vertices. Averaging 20 graphs shrinks that to about 0.5%. With c = 2 well past the threshold at 1, finite-size bias should be small.

**Did I already know?** I know the equation and solved it here.
