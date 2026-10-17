# Worked answers, round 2026-10-17-1a7c2d6d

How each worked answer in `worked.json` was reached, written before anything was run. Knowledge questions are labelled closed, enumerable or open, as in round seven; prime intervals are half again as wide as before.

**1. Highest point of a 441-step walk.** N is odd, so E = E|S₄₄₂| − ½ = √(884/π)·(1 − 1/1,768) − ½ = **16.2651**. Simulation error 0.20.

**2. Mean distance in a 1 × 8.9 rectangle.** Exact formula: 0.012625 + 704.969 − 682.650101 + 2.5 × (8.881382 + 0.323858) = 45.344624, divided by 15 gives **3.02297**. Simulation error is about 0.0033.

**3. Longest increasing subsequence, n = 1,078.** 2√n − 1.7711·n^(1/6) = 65.666 − 5.671 = 59.995. The six measured corrections average +0.51, so **60.51**.

**4. Code points in category Nl** (closed). Runic golden numbers 3, Roman numerals 39 (U+2160–2182 and 2185–2188), Hangzhou numerals and the ideographic zero 13, Bamum 10, Ancient Greek numbers 53, Gothic 2, Old Persian 5, Cuneiform numbers 111. **236**.

**5. Unicode names with the word GREEK.** This question came up in round two, where the answer was 531, with the same Python and Unicode version. This one measures nothing new: **531** from that result.

**6. Names in `enum.__all__`** (enumerable). EnumType, EnumMeta, EnumDict (new in 3.13's list), Enum, IntEnum, StrEnum, Flag, IntFlag, ReprEnum, auto, unique, property, verify, member, nonmember, FlagBoundary with STRICT, CONFORM, EJECT and KEEP, global_flag_repr, global_enum_repr, global_str, global_enum, EnumCheck with CONTINUOUS, NAMED_FLAGS and UNIQUE, pickle_by_global_name, pickle_by_enum_name. **30**.

**7. Lines in `optparse`** (enumerable). Docstring and copyright block, `__all__`, the exception classes, HelpFormatter and its two subclasses, Option, Values, OptionContainer, OptionGroup and the long OptionParser. About **1,680**.

**8. Collatz steps from 252,385,005,544.** Traced by hand:

> 252,385,005,544 → (3 halvings) 31,548,125,693 → … → step 59: 266,788,781 → … → step 99: 528,181 → step 105: 49,517 → … → step 146: 1,765 → step 151: 331 → … → step 162: 35

35 takes 13 steps, so **175**, unusually fast; the model's median is about 263. If the trace slipped, the answer would look like a draw near that median, so the 90% interval stretches up to it.

**9. Primes in [224,907, 259,190].** 34,284 numbers at density 1 / 12.3969 give 2,766, less about 3 for the widening gap between li(x) and π(x). My prime counts have leaned low (mean −9 over six), so **2,760**, with intervals half again as wide as before.

**10. Draws until a repeat, d = 562,753.** √(πd/2) = √(883,970.345) = 940.19697, plus 2/3 and 0.00014, gives **940.86378**.

**11. Function definitions in `trace`** (enumerable). _Ignore (2), _modname and _fullmodname, CoverageResults (5), four line-finding helpers, Trace (12), main with its inner parse_ignore_dir, and the _settrace and _unsettrace helpers. **29**.

**12. Digit sum of 2^4686.** It has 1,411 digits. The leading digit is 4, since 10^0.627 ≈ 4.24, and the last is 4. So 4 + 4 + 1,409 × 4.5 = **6,348**, with a standard deviation of 108.
