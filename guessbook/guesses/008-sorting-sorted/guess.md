---
claim: "In CPython, sorted() on 1,000,000 floats already in order is at least 10 times faster than on the same floats shuffled (best of 5 runs)."
p: 0.85
---

# 008 · Sorting what is already sorted

**Question.** In CPython, how much faster is `sorted()` on a list of 1,000,000 floats that is already in order, compared with the same floats in random order?

**Claim.** At least 10 times faster, comparing the best of 5 runs of each. **Probability: 85%.**

**Reasoning.** Timsort finds the single existing run with about n comparisons, while random input needs about n log₂ n ≈ 20n comparisons plus merging. CPython also has a fast path for comparing floats, which makes every comparison cheap. That shrinks the sorting cost but leaves fixed costs that are the same in both cases: copying the list and the pre-pass that checks every element's type. I estimate about 5–10 ms for the ordered list against 150–300 ms for the shuffled one, a ratio of 20 or more. The risk is that the fixed costs are bigger than I think.

**Did I already know?** I know how Timsort works. I don't know the timings on this machine.
