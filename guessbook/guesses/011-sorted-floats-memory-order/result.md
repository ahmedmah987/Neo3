---
outcome: true
---

# Result 011

```
Python 3.13.16 on x86_64
shuffled: 307.1 ms
ordered, shared objects: 57.4 ms (ratio 5.4)
ordered, fresh objects:  15.6 ms (ratio 19.7)
claim: True
```

**True.** Same values, same comparisons, only a different memory order, and the ordered sort went from 57.4 ms to 15.6 ms. About 42 ms of guess 008's ordered sort was cache misses. The fresh case came in slightly above my "under 15 ms" estimate, but the claim was about the ratio, which reached 19.7.
