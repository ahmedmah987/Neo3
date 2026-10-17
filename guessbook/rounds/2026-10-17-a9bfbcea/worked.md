# Worked answers, round 2026-10-17-a9bfbcea

How each worked answer in `worked.json` was reached, written before anything was run.

Lesson carried over from the first round: my intervals were too wide. This time an interval is only as wide as a real source of uncertainty: simulation noise, the randomness of the thing itself, or gaps in what I know. There is no extra padding "for arithmetic error".

**1. Digit sum of 2^3832.** It has ⌊3832 · log₁₀2⌋ + 1 = ⌊1153.547⌋ + 1 = 1,154 digits. The leading digit is 3, since 10^0.547 ≈ 3.52, and the last digit is 6, since 3832 is divisible by 4. Treating the other 1,152 digits as random (mean 4.5, variance 8.25) gives 3 + 6 + 5,184 = **5,193**, with a standard deviation of √(1,152 · 8.25) ≈ 97. The intervals are that standard deviation and nothing more.

**2, 11. Highest point of an N-step walk.** E[M] = E|S_N| − (1 − P(S_N = 0)) / 2, as in the first round, where all four of these answers landed close.
- N = 890: √(566.59) = 23.803, so E ≈ 23.797 − 0.5 + 0.013 = **23.31**. Simulation error 0.28.
- N = 1,342: √(854.34) = 29.229, so E ≈ 29.224 − 0.5 + 0.011 = **28.73**. Simulation error 0.35.

**3. Primes in [2,208,270, 2,216,007].** That's 7,738 numbers at density 1 / ln(2.212·10⁶) = 1 / 14.609, so **530**. Last round's prime count landed 11 above my estimate. For intervals this long, Montgomery–Soundararajan put the variance at about mean × (ln(x/h) − 2.42) / ln x ≈ 0.22 × mean, a standard deviation near 11. I use 13.

**4. Draws until a repeat, d = 3,625,240.** √(πd/2) = √(5,694,513.68) = 2,386.318, so E ≈ 2,386.318 + 0.667 + 0.00005 = **2,386.985**. Last round this formula was right to within 0.0001.

**5. Collatz steps from 947,083,466,021.** ln n = 27.577. In the random-walk model, the number of shortcut steps T has mean 191.8 and standard deviation 52.9, with skewness about 0.83 (an inverse-Gaussian shape). Ordinary steps are 1.631·T − 25.1, and the constant measured in guess 003 is −2. Using Cornish–Fisher quantiles: median **274**, quartiles 221 and 337, 5th and 95th percentiles 164 and 448. That is wide, but the width is real.

**6. Unicode names with the word DOUBLE.** Counted by groups from memory. DOUBLE-STRUCK, which splits into the word DOUBLE: 55 mathematical, 17 letterlike, 25 Arabic mathematical, so 97. Combining marks about 20; punctuation and quotation marks about 35; brackets about 10; box drawing 33; arrows about 45; mathematical operators about 45; miscellaneous technical about 10; DOUBLE DANDA and DOUBLE SHAD across Indic and related scripts about 18; Latin, Cyrillic and Hebrew letters about 25; musical symbols about 6; SignWriting about 50, which is the biggest unknown; other bits about 15. Total about **410**.

**7. Longest increasing subsequence, n = 261.** 2√n − 1.7711·n^(1/6) = 32.311 − 4.477 = 27.834. In round one the same formula was 0.45 low at n = 872, consistent with a constant correction of about +½. So **28.33**; the simulation error is 0.07 and the correction is uncertain by about 0.15.

**8. Lines in `fractions`.** Recall: the long `__new__`, `limit_denominator`, the float-style `__format__` added in 3.12, and the long `_operator_fallbacks` docstring. About **1,000**.

**9. Mean distance in a 1 × 6.41 rectangle.** Same exact formula as round one, where it was right to within simulation noise. 0.024338 + 263.374721 − 247.255737 + 2.5 × (6.384277 + 0.398914) = 33.101300, divided by 15 gives **2.2068**. Simulation error is about 0.0024.

**10. Function definitions in `tokenize`.** Since 3.12, tokenize is a thin layer over the C tokenizer. From memory: group, any, maybe, _all_string_prefixes, _compile, TokenInfo's `__repr__` and `exact_type`, Untokenizer's four methods, untokenize, _get_normal_name, detect_encoding with its two inner functions, open, tokenize, generate_tokens, _generate_tokens_from_c_tokenizer, _transform_msg, and _main with its two inner functions. That makes **25**.

**12. Unicode names with the word GREEK.** Greek and Coptic block 135, minus 14 Coptic, so 121. Greek Extended 233. Four combining Greek marks. Ancient Greek Numbers 79 minus NOMISMA SIGN, so 78. GREEK SYMBOL TAU RHO 1. Ancient Greek Musical Notation 70. Five small-capital letters, five subscripts, one in Latin Extended-E, TURNED GREEK SMALL LETTER IOTA 1, and nine GREEK CROSS symbols. Total **528**.
