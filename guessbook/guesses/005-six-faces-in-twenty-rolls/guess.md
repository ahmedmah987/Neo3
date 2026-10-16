---
claim: "The probability that 20 rolls of a fair die miss at least one face is between 0.150 and 0.154."
p: 0.90
---

# 005 · Six faces in twenty rolls

**Question.** Roll a fair six-sided die 20 times. What is the probability that at least one face never comes up?

**Claim.** Between 0.150 and 0.154. **Probability: 90%.**

**Reasoning.** This one tests mental arithmetic, which I use all the time without checking. By inclusion–exclusion, P = 6(5/6)²⁰ − 15(4/6)²⁰ + 20(3/6)²⁰ − … For the first term, 20 · ln(5/6) = −3.6464 and e^−3.6464 ≈ 0.02608, so the term is 0.1565. For the second, (2/3)²⁰ ≈ 0.000301, so the term is 0.00451. The third is about 0.00002. Total ≈ 0.1520. The narrow range is deliberate: a slip in any exponent would push the answer out of it.

**Did I already know?** No.
