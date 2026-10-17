# Worked answers, round 2026-10-17-d8b9f233

How each worked answer in `worked.json` was reached, written before anything was run.

This round is scored with the interval score, which is minimised by honest quantiles. So each 50% interval is my 25th to 75th percentile, and each 90% interval is my 5th to 95th percentile, even when that makes them lopsided.

**1. Draws until a repeat, d = 2,918,712.** √(πd/2) = √(4,584,702.089) = 2,141.19175. Adding 2/3 and (1/12)·√(π/(2d)) = 0.00006 gives **2,141.85847**. The formula has been right to 0.0001 three times, so the intervals cover arithmetic only.

**2. Code points in category Mc.** Spacing marks are mostly Indic vowel signs. Counted script by script from memory: the ten big Indic scripts about 101; Myanmar about 30; Saurashtra 18; Grantha 15; Lepcha 13; Khmer 11; Tai Tham, Balinese, Javanese, Sharada, Newa, Tirhuta and Dives Akuru about 10 each; Miao 55 (its vowel signs U+16F51–16F87 are all Mc); musical symbols 8; and about 70 more spread over smaller scripts, the Vedic signs and the Hangul tone marks. Total about **455**. Every script's count is uncertain by roughly a third.

**3. Highest point of a 1,936-step walk.** E[M] = √(3,872/π)·(1 − 1/7,744) − ½ + ½·P(S = 0) = 35.1024 − 0.5 + 0.0091 = **34.611**. Simulation error 0.42.

**4. Lines in `wave`.** About 510 lines before 3.12. 3.12 moved the old `chunk` module's class in as `_Chunk` (about 100 lines) and added WAVE_FORMAT_EXTENSIBLE support. About **660**.

**5. Mean distance in a 1 × 1.69 rectangle.** Exact formula: 0.350128 + 4.826809 − 0.404969 + 2.5 × (1.604296 + 0.766710) = 10.699481, divided by 15 gives **0.71330**. Simulation error is about 0.0005. My instinct of 0.70 was off by more than the interval allowed.

**6. Unicode names with the word HEBREW.** The Hebrew block has 88 assigned characters (U+0591–05C7, 05D0–05EA, 05EF–05F4), all named HEBREW …. The Hebrew presentation forms at U+FB1D–FB4F have 46, with gaps at FB37, FB3D, FB3F, FB42 and FB45. Total **134**.

**7. Collatz steps from 998,542,385,833.** Traced by hand, checking each 3n + 1 as n + 2n:

> 998,542,385,833 → … → step 70: 865,666,414,265 → … → step 173: 190,177,782,827 → … → step 235: 25,128,919 → … → step 305: 467 → 1,402 → 701 → 2,104 → 1,052 → step 310: 526

526 is on the trajectory of 27, which takes 111 steps; 526 is 32 steps in, so 79 steps remain, and 310 + 79 = **389**. If the trace is wrong anywhere, the answer would look like a draw from the model, median about 276. At about 90% confidence in the trace, the honest 5th percentile sits near that median and the 95th at 389 itself.

**8. Names in `secrets.__all__`.** choice, randbelow, randbits, SystemRandom, token_bytes, token_hex, token_urlsafe, compare_digest: **8**.

**9. Assigned in the Thaana block.** U+0780–07A5 letters (38), 07A6–07B0 vowel signs (11), 07B1 NAA (1): **50**.

**10. Function definitions in `textwrap`.** TextWrapper has 9 methods: `__init__`, `_munge_whitespace`, `_split`, `_fix_sentence_endings`, `_handle_long_word`, `_wrap_chunks`, `_split_chunks`, `wrap`, `fill`. The module has wrap, fill, shorten, dedent and indent. indent used to define two inner functions; I think 3.13 may have replaced one with a lambda. So 14 to 16, estimate **15**. My instinct of 22 was far off.

**11. Digit sum of 2^7726.** It has ⌊7,726 · log₁₀2⌋ + 1 = 2,326 digits. The leading digit is 5, since 10^0.758 ≈ 5.7, and the last digit is 4, since 7,726 ≡ 2 (mod 4). So 5 + 4 + 2,324 × 4.5 = **10,467**, with a standard deviation of √(2,324 · 8.25) ≈ 139.

**12. Primes in [106,716, 116,750].** By density: 10,035 / ln(111,733) = 10,035 / 11.6239 = 863.3. But I remember π(100,000) = 9,592, π(110,000) = 10,453 and π(120,000) = 11,301, which put both decades a little below the density estimate (861 and 848 against 865 and 858). Spreading those counts evenly over the interval gives 855. I settle on **858**. The interval is short-range error only: the gap between π(x) and li(x) is almost the same at both ends.
