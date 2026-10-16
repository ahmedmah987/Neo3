---
outcome: false
---

# Result 008

```
Python 3.13.16 on x86_64
shuffled: 313.6 ms, already sorted: 56.9 ms, ratio 5.5
claim: False
```

**False.** The shuffled case took about what I expected (313.6 ms), but the ordered case took 56.9 ms against my 5–10 ms. I reasoned about comparisons and fixed costs and missed memory layout. The ordered list holds the same float objects as the shuffled one, created in shuffled order, so walking it in value order jumps around memory.

That explanation was itself only a guess, so it became [guess 011](../011-sorted-floats-memory-order/) and was tested the same way. It held: with fresh floats allocated in sorted order, the ordered sort drops to 15.6 ms and the ratio rises to about 20.
