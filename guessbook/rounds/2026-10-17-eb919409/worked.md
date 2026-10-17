# Worked answers, round 2026-10-17-eb919409

How each worked answer in `worked.json` was reached, written before anything was run.

The rule from round six: correct for forgetting only in proportion to how open-ended the count is. Each knowledge question is labelled **closed** (a short list I can recall whole: no correction), **enumerable** (long but listable: a small correction), or **open** (a word or thing that turns up anywhere: a bigger correction, mostly as room above).

**1. Assigned in the Syriac block** (closed). Punctuation U+0700–070D (14), the abbreviation mark U+070F, letters and marks U+0710–074A (59), and three Sogdian letters U+074D–074F. **77**.

**2. Primes in [1,035,950, 1,085,617].** 49,668 numbers at density 1 / 13.8745 gives 3,580. Here li(x) runs ahead of π(x), and that gap is still widening, by about 3 over this stretch, so **3,577**. Over five rounds my prime counts have been off by +11, −6, −18, −10 and −2, so I use a standard deviation of about 14 rather than the 13 the theory suggests.

**3. Draws until a repeat, d = 2,529,464.** √(πd/2) = √(3,973,272.76) = 1,993.30699, plus 2/3 and 0.00007, gives **1,993.97372**.

**4. Lines in `statistics`** (enumerable). About 1,450 to 1,500 in 3.12. 3.13 added `kde`, with its kernel tables and long docstring, and `kde_random`. About **1,700**.

**5. Code points in category Sc** (closed). $, ¢ £ ¤ ¥, Armenian dram, Afghani, two NKo, three Bengali, Gujarati, Tamil, Thai baht, Khmer riel, the 33 in U+20A0–20C0 (through the 14.0 som sign), North Indic rupee mark, rial sign, small and fullwidth dollar, four fullwidth signs, four Tamil fraction-block signs, Wancho ngun and Indic Siyaq rupee. **63**.

**6. Mean distance in a 1 × 2.7 rectangle.** Exact formula: 0.137174 + 19.683 − 12.746879 + 2.5 × (2.641798 + 0.636686) = 15.269504, divided by 15 gives **1.01797**. Simulation error is about 0.0009.

**7. Highest point of a 167-step walk.** N is odd, so E = E|S₁₆₈| − ½, and E|S₂ₘ| = √(4m/π)·(1 − 1/(8m) + …) with m = 84: 10.34176 × 0.998513 − 0.5 = **9.8264**. Simulation error 0.12.

**8. Unicode names with the word FACE** (open). Emoticons U+1F600–1F644: 69, every one a face, cat faces included. Supplemental Symbols and Pictographs: 27. Extended-A (melting, saluting, shaking and others): 7. Moon and sun faces plus 16 animal faces: 21. White and black smiling and frowning faces: 3. CLOCK FACE ONE OCLOCK to TWELVE-THIRTY: 24. SignWriting face positions: about 10. Itemized 161; the word is open-ended, so about +10%: **177**, with more room above.

**9. Names in `weakref.__all__`** (closed). ref, proxy, getweakrefcount, getweakrefs, WeakKeyDictionary, ReferenceType, ProxyType, CallableProxyType, ProxyTypes, WeakValueDictionary, WeakSet, WeakMethod, finalize: **13**.

**10. Collatz steps from 738,443,544,828.** Traced by hand, checking each 3n + 1 as n + 2n and each run of halvings by multiplying back:

> 738,443,544,828 → … → step 19: 65,713,542,991 → … → step 49: 616,760,095 → … → step 86: 9,768,355 → … → step 133: 195,809 → … → step 209: 443 → … → step 237: 101 → 304 → 152 → 76 → 38 → step 242: 19

19 takes 20 steps, so **262**. The four earlier traces were all exact. If this one slipped, the answer would look like a draw from the model, median about 272, so the 90% interval stretches up to that.

**11. Longest increasing subsequence, n = 1,039.** 2√n − 1.7711·n^(1/6) = 64.467 − 5.637 = 58.831. The five measured corrections average +0.52, so **59.35**.

**12. Function definitions in `shlex`** (enumerable). The shlex class has `__init__`, the `punctuation_chars` property, push_token, push_source, pop_source, get_token, read_token, sourcehook, error_leader, `__iter__` and `__next__` (11). The module has split, join, quote and _print_tokens. **15**.
