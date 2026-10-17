# Worked answers, round 2026-10-17-6ae44e63

How each worked answer in `worked.json` was reached, written before anything was run.

The lesson from round five: my knowledge errors point one way. When I count from memory, every forgotten item lowers the total, and nothing raises it. So knowledge estimates are moved up, and their intervals have more room above than below, a little for short lists and much more for big sums with many parts.

**1. Function definitions in `optparse`.** Counted class by class: HelpFormatter 15, IndentedHelpFormatter 3, TitledHelpFormatter 3, Option 18, Values 9, OptionContainer 17, OptionGroup 5, OptionParser 38, four exception classes with `__init__` and `__str__` 8, and 8 module-level functions (including the gettext fallbacks). That's 124. Moved up for forgetting: **127**.

**2. Lines in `quopri`.** Docstring, constants, the binascii import fallback, needsquoting, quote, encode (with an inner write), encodestring, decode, decodestring, ishex, unhex and main. About **240**.

**3. Names in `gzip.__all__`.** BadGzipFile, GzipFile, open, compress, decompress: **5**.

**4. Code points in category Zs.** SPACE, NO-BREAK SPACE, OGHAM SPACE MARK, the eleven at U+2000–200A, NARROW NO-BREAK SPACE, MEDIUM MATHEMATICAL SPACE and IDEOGRAPHIC SPACE: **17**.

**5. Collatz steps from 999,226,632,124.** Traced by hand. Two halvings first, then:

> 249,806,658,031 → … → step 29: 112,539,927,293 → … → step 91: 89,221,991 → … → step 155: 3,819,715 → … → step 180: 31,867 → … → step 201: 709 → step 206: 133 → step 211: 25

25 takes 23 steps to reach 1, so **234**. The three earlier traces were all exact. If this one slipped, the answer would look like a draw from the model, median about 277, so the 90% interval leaves room above.

**6. Assigned in the Ethiopic block.** I remember it as 358 of the block's 384 code points: **358**.

**7. Longest increasing subsequence, n = 581.** 2√n − 1.7711·n^(1/6) = 48.208 − 5.116 = 43.092. The measured corrections so far are +0.53, +0.45, +0.72 and +0.42, averaging +0.53. That gives **43.62**.

**8. Highest point of a 1,417-step walk.** N is odd, so E = E|S₁₄₁₈| − ½ = √(2,836/π)·(1 − 1/5,672) − ½ = **29.540**. Simulation error 0.36.

**9. Mean distance in a 1 × 4.02 rectangle.** Exact formula: 0.061880 + 64.964808 − 54.773439 + 2.5 × (3.979654 + 0.522277) = 21.508074, divided by 15 gives **1.43387**. Simulation error is about 0.0015.

**10. Digit sum of 2^4578.** It has 1,379 digits. The leading digit is 1, since 10^0.115 ≈ 1.30, and the last is 4, since 4578 ≡ 2 (mod 4). So 1 + 4 + 1,377 × 4.5 = **6,202**, with a standard deviation of 107.

**11. Unicode names with the word CAPITAL.** Counted by group. Latin, including small capitals, capital modifier letters, letterlike symbols, fullwidth, tags, and six enclosed sets (circled, parenthesized, squared, and the negative forms): about 741. Mathematical alphanumerics: 13 × 26 − 20 holes, plus 5 × 25 Greek, plus digamma, so 444. Greek 130. Cyrillic 185. Other cased scripts (Armenian, Asomtavruli and Mtavruli, Coptic, Glagolitic, Deseret, Osage, Old Hungarian, Warang Citi, Medefaidrin, Adlam, Vithkuqi): 492. Cherokee's capitals are named without the word, so 0. Itemized total: 1,992. On SMALL the same kind of count came out 18% low, and on DOUBLE 10% low, so I move it up by about 15% to **2,300**, with more room above.

**12. Draws until a repeat, d = 3,061,525.** √(πd/2) = √(4,809,032.224) = 2,192.95057, plus 2/3 and 0.00006, gives **2,193.6173**.
