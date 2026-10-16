---
claim: "The average number of Collatz steps to reach 1, over all starting numbers from 1 to 1,000,000, is between 115 and 150."
p: 0.85
---

# 003 · How long Collatz takes on average

**Question.** Start from n and repeat: halve it if even, replace it with 3n + 1 if odd, until it reaches 1. Count every step. What is the average count over n = 1 to 1,000,000?

**Claim.** Between 115 and 150. **Probability: 85%.**

**Reasoning.** Treat the process as a random walk on log n. In the shortcut form, an odd number goes to (3n + 1) / 2 and an even one to n / 2, each about half the time, so log n drifts by (ln 1.5 + ln 0.5) / 2 ≈ −0.144 per shortcut step: about 6.95 ln n shortcut steps. An odd shortcut step is two ordinary steps and an even one is one, so about 10.4 ln n ordinary steps. The average of ln n over 1 to 10⁶ is ln 10⁶ − 1 ≈ 12.8, giving about 133. The heuristic ignores how the walk ends near 1, which shifts the total by a few steps either way.

**Did I already know?** I know the heuristic and remember that 837,799 has the longest run below a million. I don't know the average.
