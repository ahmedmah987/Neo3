# Worked answers, round 2026-10-16-e4e1ad0a

How each worked answer in `worked.json` was reached, written before anything was run.

**1. Collatz steps from 270,508,552,667.** The random-walk model gives about 10.41 ln n steps, and ln n ≈ 26.32, so about 274. Guess 003 measured the model's constant at about −2. Single runs vary a lot. In the shortcut map, log n moves by ln 1.5 or ln 0.5 (mean −0.144, standard deviation 0.549), so the first-passage time from 26.32 down to 0 has a standard deviation of about 52 shortcut steps, about 75–80 ordinary steps. The spread is skewed to the right. Estimate 272.

**2, 6, 7, 9. Highest point of an N-step walk.** By the reflection principle, P(M ≥ m) = P(S ≥ m) + P(S ≥ m + 1), which sums to E[M] = E|S_N| − (1 − P(S_N = 0)) / 2. This checks out for N = 2 (¾, the case in `check.py`). For even N, E|S_N| = N·P(S_N = 0) ≈ √(2N/π)·(1 − 1/(4N)). For odd N, E|S_N| = E|S_N+1| and P(S_N = 0) = 0. The answers are estimated from 4,000 walks, and M has a standard deviation of about 0.60√N, so the standard error is about 0.30–0.42. The intervals are mostly that noise.
- N = 1,556: √(990.58) = 31.474, so E ≈ 31.468 − 0.5 + 0.010 = **30.98**
- N = 996: √(634.07) = 25.181, so E ≈ 25.175 − 0.5 + 0.013 = **24.69**
- N = 1,921 (odd): √(1,223.58) = 34.980, so E ≈ 34.976 − 0.5 = **34.48**
- N = 1,778: √(1,131.90) = 33.644, so E ≈ 33.639 − 0.5 + 0.009 = **33.15**

**3. Longest increasing subsequence, n = 872.** Baik–Deift–Johansson: E[L] ≈ 2√n − 1.7711·n^(1/6) = 59.06 − 5.47 = 53.59. At finite n the correction is usually a bit smaller than the limit, so I push the estimate up to 54.0. My uncertainty about lower-order terms is about ±1, much bigger than the simulation's ±0.09.

**4, 11. Mean distance in a 1 × b rectangle.** Exact formula, with d = √(1 + b²): E = (1/15)[1/b² + b³ + d(3 − 1/b² − b²) + (5/2)(b² ln((1 + d)/b) + (1/b) ln(b + d))]. I checked it two ways: it gives 0.5214 for the unit square, and it tends to b/3 as b grows.
- b = 1.23: 0.66098 + 1.86087 + 1.30958 + 2.5 × (1.12377 + 0.84149) = 8.74460, divided by 15 gives **0.58297**
- b = 2.37: 0.17803 + 13.31205 − 7.18950 + 2.5 × (2.30478 + 0.67419) = 13.74801, divided by 15 gives **0.91653**. Big terms cancel here, so an arithmetic slip would matter more; I widened that interval.

The simulation error with 400,000 pairs is about 0.0005.

**5, 12. Lines in `smtplib` and `weakref`.** Recall only. smtplib has the exception classes, the SMTP class with its auth, starttls and sendmail methods, SMTP_SSL, LMTP and a small `__main__` block; I remember it as a bit over 1,100 lines. weakref has WeakValueDictionary, KeyedRef, WeakKeyDictionary, WeakMethod and finalize; I have a faint memory of about 674 lines. Both may have drifted by 3.13.

**8. Draws until a repeat, d = 114,705.** E = 1 + Q(d) ≈ √(πd/2) + 2/3 + (1/12)√(π/(2d)). Checked against d = 365, it gives 24.6166, the known value. √(180,178.19) = 424.474, so E ≈ **425.141**. The answer is computed exactly, so the interval only covers arithmetic error.

**10. Primes in [1,829,380, 1,834,725].** That's 5,346 numbers with density 1 / ln(1.832·10⁶) = 1 / 14.42, so about **371**. Prime counts in intervals this long vary less than a Poisson count would; I use a standard deviation of about 15.
