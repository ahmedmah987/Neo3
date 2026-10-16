---
outcome: true
---

# Result 006

```
77 of 100 come back exactly
fail: [3, 6, 7, 12, 14, 23, 24, 28, 29, 41, 46, 48, 51, 53, 56, 58, 61, 63, 82, 87, 92, 96, 97]
claim: True
```

**True, near the edge.** 77 pass, inside 60–80 but near the top; the uniform-error model predicted about 69. The more useful lesson is the one I nearly made: my first instinct, "almost all of them", would have been badly wrong, with 23 failures. As predicted, failures come in doubling chains (3, 6, 12, 24, 48, 96 and 7, 14, 28, 56), so the outcome depends only on the odd part of n.
