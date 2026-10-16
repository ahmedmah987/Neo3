---
claim: "In a shuffled 52-card deck, the chance that some two neighbouring cards share a rank is between 0.94 and 0.97 (over 200,000 shuffles)."
p: 0.90
---

# 004 · Neighbouring cards of the same rank

**Question.** Shuffle a standard deck. How likely is it that somewhere in it two neighbouring cards have the same rank, such as two sevens side by side?

**Claim.** Between 0.94 and 0.97, estimated from 200,000 shuffles. **Probability: 90%.**

**Reasoning.** There are 51 neighbouring pairs, and each matches with probability 3/51, so on average there are exactly 3 matching pairs. If matches were independent, the chance of none would be e⁻³ ≈ 0.050, so the chance of at least one is about 0.95. The dependence between overlapping pairs should move this only a little.

**Did I already know?** Partly. I have a vague memory that the chance of no match is about 4.5%, which agrees.
