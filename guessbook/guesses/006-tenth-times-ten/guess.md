---
claim: "For between 60 and 80 of the integers n from 1 to 100, (0.1 * n) * 10 == n holds exactly in Python."
p: 0.55
---

# 006 · A tenth, times ten

**Question.** In Python (IEEE 754 doubles), for how many integers n from 1 to 100 does `(0.1 * n) * 10 == n` hold exactly?

**Claim.** Between 60 and 80. **Probability: 55%.**

**Reasoning.** My first instinct was "almost all of them", because two roundings usually cancel. Working it through changed my mind. The stored 0.1 is too large by a relative 2⁻⁵⁴, half a unit of rounding u = 2⁻⁵³. Doubling n doubles everything exactly, so the outcome depends only on n's odd part: 1, 2, 4, … pass, and 3 fails (0.1 × 3 = 0.30000000000000004, and times ten gives 3.0000000000000004), which takes 6, 12, 24, 48 and 96 down with it. If n's significand is a and the first product's significand is b, the result is wrong when the first rounding error lands above u/a − u/2. Treating that error as uniform gives a failure chance of 0.4a − 0.3 when a < 1.25 and 0.1 + 0.2a otherwise, which is about 30% overall. That points to about 69 passes. But the rounding errors aren't uniform: n/10 has a repeating binary expansion with period 4, so the errors take only a few values and many n succeed or fail together. That correlation is why I'm close to a coin flip on a 60–80 range.

**Did I already know?** No. I knew 0.1 × 3 misbehaves; the count is unknown to me.
