---
claim: "If the already-sorted list holds fresh float objects allocated in sorted order, sorted() on it is at least 10 times faster than on the shuffled list (best of 5 runs)."
p: 0.75
---

# 011 · Why 008 was wrong

**Background.** Guess 008 claimed that `sorted()` on 1,000,000 already-ordered floats would be at least 10 times faster than on the same floats shuffled. It was 5.5 times faster: 313.6 ms against 56.9 ms. I had expected 5–10 ms for the ordered case.

**Question.** Is memory layout the reason? In 008 the ordered list held the *same* float objects as the shuffled one. Those objects were created in the shuffled order, so they sit in memory roughly in that order, and walking the ordered list visits them in a random memory order, one cache miss per element. If I give the ordered list fresh copies of the floats, created in sorted order, its walk becomes sequential.

**Claim.** With fresh floats allocated in sorted order, the shuffled list (unchanged from 008) takes at least 10 times as long to sort as the ordered one. **Probability: 75%.**

**Reasoning.** A cache miss costs on the order of 50–100 ns, and 10⁶ of them is 50–100 ms, about what 008 measured. Without them, the ordered case should cost a list copy, a type-check pass and about 10⁶ cheap comparisons: under 15 ms. Two things could still break the claim. The allocator might not lay out a million new floats sequentially, or something other than memory order might explain 008.

**Did I already know?** No. This is a hypothesis formed after seeing 008's result, and this guess is how it gets tested.
