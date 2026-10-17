# Calibench report: openrouter:anthropic/claude-haiku-5.5

Seed `2026-10-17`, 26 questions, Calibench 1.0.0, Python 3.13.16 (Unicode 15.1.0), started 2026-10-17T03:01:02+00:00.

Served by: anthropic/claude-haiku-5.5 via Claude Platform on AWS.

Tokens: prompt tokens 12,902, completion tokens 141,467, reasoning tokens 122,067.

Cost reported by the API: 0.0720 (US dollars on OpenRouter).

## Summary

| | Instinct | Worked |
|---|---|---|
| Answered | 26 of 26 | 26 of 26 |
| **Weighted interval score**, mean (median) | **16.7%** (8.9%) | **9.1%** (1.7%) |
| Interval score, 50% intervals | 83.7% | 44.3% |
| Interval score, 90% intervals | 207.9% | 115.9% |
| 50% intervals containing the answer | 16 of 26 (62%) | 15 of 26 (58%) |
| … leaving out single numbers | 15 of 25 (60%): consistent with calibrated | 13 of 24 (54%): consistent with calibrated |
| 90% intervals containing the answer | 20 of 26 (77%) | 18 of 26 (69%) |
| … leaving out single numbers | 20 of 26 (77%): too narrow (overconfident) | 18 of 26 (69%): too narrow (overconfident) |
| Answers given as certain (a single number) | 0, 0 exactly right | 0, 0 exactly right |
| Median error of the estimate | 2.7% | 2.4% |
| Estimate closer to the answer | 6 | 15 |

Working it out lowered the weighted interval score on 19 of 26 questions answered both ways, from 16.7% to 9.1% on average.

Scores are relative to the true answer, and lower is better. The weighted interval score combines the estimate and both intervals (Bracher et al., 2021): narrow intervals score well only if the answer lands inside them, so it can't be improved by stating intervals you don't believe. Coverage verdicts leave out single-number intervals, which say "I know this exactly" and are counted on their own line.

## By kind of question

Knowledge questions ask what is known (the Python standard library, the Unicode database); statistical ones need noise or irregularity modelled; exact ones have a closed-form answer that must be evaluated.

| Kind | Phase | Questions | Weighted interval score | 50% hits | 90% hits |
|---|---|---|---|---|---|
| exact | instinct | 2 | 9.9% | 2 of 2 (100%) | 2 of 2 (100%) |
| exact | worked | 2 | 10.1% | 2 of 2 (100%) | 2 of 2 (100%) |
| knowledge | instinct | 12 | 28.3% | 5 of 12 (42%) | 7 of 12 (58%) |
| knowledge | worked | 12 | 11.0% | 8 of 12 (67%) | 8 of 12 (67%) |
| statistical | instinct | 12 | 6.2% | 9 of 12 (75%) | 11 of 12 (92%) |
| statistical | worked | 12 | 7.0% | 5 of 12 (42%) | 8 of 12 (67%) |

## Questions

Each answer is shown as estimate [90% interval], with ✓ or ✗ for whether the 50% and 90% intervals contain the true answer.

| # | Question | True answer | Instinct | Worked |
|---|---|---|---|---|
| 1 | mean distance in a 1 × 2.39 rectangle | 0.9228 | 0.92 [0.78, 1.08] 50✓ 90✓ | 0.9226 [0.9175, 0.9275] 50✓ 90✓ |
| 2 | longest increasing subsequence, n = 144 | 20.59 | 20 [16.8, 23.2] 50✓ 90✓ | 19.9 [18.9, 21] 50✗ 90✓ |
| 3 | assigned in the Ethiopic block | 358 | 357 [310, 359] 50✓ 90✓ | 358 [342, 362] 50✓ 90✓ |
| 4 | draws until a repeat, d = 141 | 15.56 | 15.5 [4, 30] 50✓ 90✓ | 15.56 [5, 29] 50✓ 90✓ |
| 5 | Collatz steps from 492,058,289,036 | 150 | 170 [90, 290] 50✓ 90✓ | 275 [175, 400] 50✗ 90✗ |
| 6 | Unicode names with the word HAND | 304 | 75 [40, 130] 50✗ 90✗ | 125 [40, 240] 50✗ 90✗ |
| 7 | highest point of a 508-step walk | 17.56 | 18 [2.8, 37] 50✓ 90✓ | 17.97 [17.62, 18.33] 50✗ 90✗ |
| 8 | lines in `queue` | 385 | 330 [250, 430] 50✗ 90✓ | 392 [360, 430] 50✓ 90✓ |
| 9 | function definitions in `pickle` | 127 | 110 [60, 180] 50✓ 90✓ | 118 [94, 140] 50✓ 90✓ |
| 10 | primes in [546,440, 556,877] | 790 | 790 [764, 816] 50✓ 90✓ | 789 [757, 822] 50✓ 90✓ |
| 11 | code points in category No | 915 | 1,400 [1,100, 1,750] 50✗ 90✗ | 1,050 [960, 1,180] 50✗ 90✗ |
| 12 | digit sum of 2^3432 | 4,879 | 4,653 [4,502, 4,804] 50✗ 90✗ | 4,651 [4,500, 4,800] 50✗ 90✗ |
| 13 | names in `pprint.__all__` | 7 | 4 [2, 8] 50✗ 90✓ | 7 [6, 8] 50✓ 90✓ |
| 14 | assigned in the Lao block | 83 | 67 [56, 80] 50✗ 90✗ | 76 [68, 81] 50✗ 90✗ |
| 15 | primes in [1,470,770, 1,476,106] | 367 | 376 [352, 400] 50✗ 90✓ | 376 [354, 398] 50✓ 90✓ |
| 16 | Unicode names with the word WHITE | 290 | 80 [40, 140] 50✗ 90✗ | 105 [84, 135] 50✗ 90✗ |
| 17 | Collatz steps from 752,299,430,991 | 200 | 280 [160, 430] 50✗ 90✓ | 275 [120, 440] 50✗ 90✓ |
| 18 | lines in `textwrap` | 497 | 500 [430, 580] 50✓ 90✓ | 485 [448, 525] 50✓ 90✓ |
| 19 | longest increasing subsequence, n = 3,063 | 104.4 | 103.9 [102.3, 105.5] 50✓ 90✓ | 103.9 [103, 104.9] 50✗ 90✓ |
| 20 | highest point of a 427-step walk | 16.12 | 16.5 [2, 41] 50✓ 90✓ | 16.5 [16.15, 16.85] 50✗ 90✗ |
| 21 | digit sum of 2^8365 | 11,252 | 11,331 [11,094, 11,568] 50✓ 90✓ | 11,335 [11,098, 11,572] 50✓ 90✓ |
| 22 | draws until a repeat, d = 283,156 | 667.6 | 668 [171, 1,303] 50✓ 90✓ | 667.6 [170, 1,303] 50✓ 90✓ |
| 23 | function definitions in `traceback` | 70 | 80 [40, 150] 50✓ 90✓ | 75 [58, 98] 50✓ 90✓ |
| 24 | code points in category Zs | 17 | 17 [16, 18] 50✓ 90✓ | 17 [16, 18] 50✓ 90✓ |
| 25 | names in `locale.__all__` | 23 | 60 [30, 110] 50✗ 90✗ | 22 [20, 24] 50✓ 90✓ |
| 26 | mean distance in a 1 × 3.63 rectangle | 1.311 | 1.31 [1.18, 1.45] 50✓ 90✓ | 1.31 [1.306, 1.313] 50✓ 90✓ |
