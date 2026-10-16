---
claim: "Between 10,000 and 13,000 primes below 1,000,000 are still prime when their digits are reversed."
p: 0.80
---

# 002 · Primes that survive reversal

**Question.** How many primes below 1,000,000 are still prime when their digits are written backwards? Palindromic primes such as 11 and 101 count, and so does 13, because 31 is prime.

**Claim.** Between 10,000 and 13,000. **Probability: 80%.**

**Reasoning.** Work through the 6-digit primes, which dominate. The reversal ends in the prime's first digit, so only primes starting with 1, 3, 7 or 9 have a chance. From the prime counts I remember (π(2·10⁵) = 17,984, π(4·10⁵) = 33,860 and so on) that is 30,887 of the 68,906 six-digit primes. Their reversals are numbers near 10⁵–10⁶ with prime density about 1 / ln R ≈ 0.077, but they are already known to be odd, not multiples of 5 (×2.5), not multiples of 3 (the digit sum is unchanged, ×1.5), and not multiples of 11 (for an even number of digits the alternating digit sum only flips sign, ×1.1). That gives about 0.32, so roughly 9,800 six-digit hits. The same reasoning gives about 1,460 five-digit hits, about 230 four-digit, 43 three-digit, and 13 below 100. Total about 11,600.

**Did I already know?** No. The prime counts at round numbers are from memory; the rest is derived.
