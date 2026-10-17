# Worked answers, round 2026-10-17-31643da8

How each worked answer in `worked.json` was reached, written before anything was run.

The lesson from round four: knowledge intervals have never missed at 50%, because my recall is better than I believe. This round they're about half as wide as feels comfortable. Statistical intervals stay exactly as wide as their models say.

**1. Highest point of a 1,362-step walk.** √(2,724/π)·(1 − 1/5,448) − ½ + ½·P(S = 0) = 29.4408 − 0.5 + 0.0108 = **28.952**. Simulation error 0.35.

**2. Assigned in the Mongolian block.** U+1800–180F (punctuation, the free variation selectors including FVS4 from Unicode 14, and the vowel separator): 16. Digits: 10. Letters U+1820–1878, including CHA WITH TWO DOTS from Unicode 11: 89. U+1880–18AA: 43. Total **158**.

**3. Longest increasing subsequence, n = 185.** 2√n − 1.7711·n^(1/6) = 27.203 − 4.228 = 22.975. The correction has been measured three times (+0.53, +0.45, +0.72); I use +0.53. That gives **23.51**.

**4. Names in `inspect.__all__`.** 3.13 gave inspect an `__all__`. Listed from memory: 14 classes and named tuples, 12 CORO_/GEN_/AGEN_ state constants, TPFLAGS_IS_ABSTRACT, and 67 functions, from classify_class_attrs to walktree. That's 94. If the ten CO_* code flags are included as well, it's 104. I can't tell which, so the answer is bimodal: estimate **99**, with the 50% interval spanning both modes.

**5. Collatz steps from 772,456,875,771.** Traced by hand, checking each 3n + 1 as n + 2n and each run of halvings by multiplying back:

> 772,456,875,771 → … → step 35: 48,937,231,841 → … → step 110: 1,325,786,173 → … → step 189: 62,357 → … → step 212: 347 → … → step 229: 124

124 is on the trajectory of 27 (27 → 82 → 41 → 124), which takes 111 steps, so 108 remain: **337**. Both earlier traces were exact. If this one slipped, the answer would look like a draw from the model, median about 272; the 90% interval keeps that much room below.

**6. Mean distance in a 1 × 3.2 rectangle.** Exact formula: 0.097656 + 32.768 − 24.600306 + 2.5 × (3.150081 + 0.587457) = 17.609196, divided by 15 gives **1.17395**. Simulation error is about 0.0011.

**7. Draws until a repeat, d = 1,190,973.** √(πd/2) = √(1,870,776.014) = 1,367.76314, plus 2/3 and 0.0001, gives **1,368.4299**.

**8. Function definitions in `argparse`.** Counted class by class: HelpFormatter about 31 (with `_Section` and the inner functions in `_format_usage` and `_metavar_formatter`); the four formatter subclasses 5; the Action family (Action, BooleanOptionalAction, the eight store, append, count, help and version actions, _SubParsersAction with its pseudo-action, _ExtendAction) about 35; FileType, Namespace, ArgumentError and _AttributeHolder 11; _ActionsContainer 18; the two group classes 8; ArgumentParser about 34 (including the three inner functions of `_parse_known_args`); two module helpers. Total about **140**, far below my instinct of 180.

**9. Unicode names with the word SMALL.** Counted by group. Latin, including IPA, phonetic extensions, modifiers, enclosed, fullwidth, tags and combining: about 1,071. Mathematical alphanumerics: 13 Latin styles × 26 − 4 holes, plus dotless i and j, plus 5 Greek styles × 25, plus digamma, so 462. Greek: 186. Cyrillic, including Extended-D's 63 modifier letters: 257. Cased scripts (Armenian, Nuskhuri, Coptic, Glagolitic, Deseret, Osage, Old Hungarian, Warang Citi, Medefaidrin, Adlam, Vithkuqi, Cherokee): 540. Small form variants, small kana, Arabic small marks, small Roman numerals and symbols: 195. Total about **2,710**, well below my instinct of 3,500.

**10. Lines in `shutil`.** A long module: copy and copytree machinery, rmtree with its fd-based and onexc variants, archive registration, disk_usage, chown, which, get_terminal_size. About **1,600**.

**11. Digit sum of 2^8832.** It has 2,659 digits. The leading digit is 4, since 10^0.697 ≈ 4.98, and the last is 6, since 8832 ≡ 0 (mod 4). So 4 + 6 + 2,657 × 4.5 = **11,966**, with a standard deviation of 148.

**12. Primes in [314,525, 387,797].** Anchored on π(300,000) = 25,997 and π(400,000) = 33,860, which I recall, and filling the gaps at each end with ∫dt/ln t: π(314,525) ≈ 25,997 + 1,149.5, and π(387,797) ≈ 33,860 − 947.2. That gives **5,766**. Plain density would say 5,738, but that 100,000-wide stretch holds about 30 more primes than li predicts. Fluctuation at the two ends is about ±10.
