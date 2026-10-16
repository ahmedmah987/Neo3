---
outcome: true
---

# Result 002

```
78498 primes below 1,000,000; 11297 stay prime when reversed
claim: True
```

**True.** I estimated about 11,600 and got 11,297, 2.6% lower. The heuristic ran slightly high; a likely cause is that I used a single average density for each digit-length band instead of weighting it by where the reversals actually fall.
