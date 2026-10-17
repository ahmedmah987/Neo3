# Worked answers, round 2026-10-17-d9289e0f

How each worked answer in `worked.json` was reached, written before anything was run. Knowledge questions are labelled closed, enumerable or open, as in rounds seven and eight.

**1. Primes in [2,815,980, 2,868,969].** That's 52,990 numbers at density 1 / 14.8602, so 3,566, less about 2 for the gap between li(x) and π(x). Estimate **3,564**. With h/x this small, the Montgomery–Soundararajan variance gives a standard deviation of about 19; I use 20.

**2. Function definitions in `fnmatch`** (closed). fnmatch, _compile_pattern, filter, fnmatchcase, translate, plus the _translate and _join_translated_parts helpers that 3.13 split out for `glob.translate`: **7**.

**3. Longest increasing subsequence, n = 339.** 2√n − 1.7711·n^(1/6) = 36.824 − 4.677 = 32.147. Seven measured corrections average +0.51, so **32.66**.

**4. Draws until a repeat, d = 188,392.** √(πd/2) = √(295,925.462) = 543.99031, plus 2/3 and 0.00024, gives **544.65722**.

**5. Names in `functools.__all__`** (closed). update_wrapper, wraps, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES, total_ordering, cache, cmp_to_key, lru_cache, reduce, partial, partialmethod, singledispatch, singledispatchmethod, cached_property: **14**. Placeholder arrives in 3.14, not 3.13.

**6. Assigned in the Currency Symbols block** (closed). U+20A0–20C0, through the som sign added in 14.0: **33**.

**7. Highest point of a 1,389-step walk.** N is odd, so E = E|S₁₃₉₀| − ½ = √(2,780/π)·(1 − 1/5,560) − ½ = **29.242**. Simulation error 0.36.

**8. Code points in category Nd** (enumerable). Decimal digits come in sets of ten. Counting sets: ASCII, two Arabic-Indic, NKo, ten Indic scripts plus Sinhala Lith, Thai, Lao, Tibetan, three Myanmar sets plus Tai Laing, Khmer, Mongolian, Limbu, New Tai Lue, two Tai Tham, Balinese, Sundanese, Lepcha, Ol Chiki, Vai, Saurashtra, Kayah Li, Javanese, Cham, Meetei Mayek, fullwidth, Osmanya, Hanifi Rohingya, Brahmi, Sora Sompeng, Chakma, Sharada, Khudawadi, Newa, Tirhuta, Modi, Takri, Ahom, Warang Citi, Dives Akuru, Bhaiksuki, the two Gondi scripts, Mro, Tangsa, Pahawh Hmong, five mathematical sets, Nyiakeng Puachue Hmong, Wancho, Adlam, segmented digits, Kawi and Nag Mundari. 68 sets: **680**.

**9. Unicode names with the word TRIANGLE** (open). Geometric Shapes 27; Geometric Shapes Extended about 8; the many TRIANGLE-HEADED arrows in Miscellaneous Symbols and Arrows (the hyphen splits off TRIANGLE) about 44; Supplemental Arrows-C triangle arrowheads 12; Miscellaneous Technical (the media-control double triangles and medium triangles) 11; mathematical symbols about 20; the four red emoji triangles; musical triangle noteheads about 8; COMBINING ENCLOSING UPWARD POINTING TRIANGLE and HEBREW YOD TRIANGLE. Itemized about 136. For open words my itemized counts have run 10–18% low, so **163**, with more room above.

**10. Collatz steps from 293,589,806,402.** Traced by hand:

> 293,589,806,402 → … → step 31: 8,266,536,941 → … → step 70: 196,390,301 → … → step 120: 2,952,511 → … → step 182: 505,607 → … → step 222: 1,001 → … → step 261: 143 → … → step 270: 364

364 is on the trajectory of 27, 17 steps in, so 94 remain: **364**, far above the model's median of about 266. If the trace slipped, the answer would look like a draw near that median, so the 90% interval stretches down to it.

**11. Digit sum of 2^9004.** It has 2,711 digits. The leading digit is 2, since 10^0.474 ≈ 2.98, and the last is 6. Benford's law pulls the second digit's mean down by about 0.3. So 2 + 6 + 2,709 × 4.5 − 0.3 = **12,198**, with a standard deviation of 150. Recent digit sums have leaned low, but not significantly, so I don't shift it further.

**12. Lines in `reprlib`** (enumerable). The recursive_repr decorator, and Repr with its `__init__` (bigger since 3.12 added the limits and indent as parameters), repr, repr1, _join and the repr_ methods for tuple, list, array, set, frozenset, deque, dict, str, int and instance, then _possibly_sorted and the module-level aRepr. About **230**.
