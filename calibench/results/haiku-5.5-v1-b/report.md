# Calibench report: openrouter:anthropic/claude-haiku-5.5

Seed `calibench-v1`, 104 questions, Calibench 2.0.0, Python 3.13.16 (Unicode 15.1.0), started 2026-10-17T03:18:44+00:00.

**Standard suite v1.**

Served by: anthropic/claude-haiku-5.5 via Claude Platform on AWS.

Tokens: prompt tokens 51,704, completion tokens 442,602, reasoning tokens 369,829.

Cost reported by the API: 0.2265 (US dollars on OpenRouter).

## Summary

| | Instinct | Worked |
|---|---|---|
| Answered | 104 of 104 | 104 of 104 |
| **Score**, mean [90% interval] | **0.178** [0.128, 0.234] | **0.050** [0.034, 0.067] |
| Score, median | 0.051 | 0.008 |
| Interval score, 50% / 90% intervals | 0.867 / 2.443 | 0.237 / 0.679 |
| 50% intervals containing the answer [90% interval] | 63 of 104 (61%) [53%, 68%] | 66 of 104 (63%) [55%, 71%] |
| … leaving out single numbers | 62 of 103 (60%): too wide (underconfident) | 54 of 92 (59%): consistent with calibrated |
| 90% intervals containing the answer [90% interval] | 83 of 104 (80%) [73%, 85%] | 91 of 104 (88%) [81%, 92%] |
| … leaving out single numbers | 83 of 104 (80%): too narrow (overconfident) | 91 of 104 (88%): consistent with calibrated |
| Answers given as certain (a single number) | 0, 0 exactly right | 0, 0 exactly right |
| Median error of the estimate | 2.5% | 0.7% |
| Estimate closer to the answer | 20 | 61 |

Working it out lowered the score on 85 of 104 questions answered both ways, from 0.178 to 0.050 on average (improvement [0.081, 0.183]).

The score is the weighted interval score (Bracher et al., 2021) on a log scale: it combines the estimate and both intervals, is lowest when the stated intervals are the ones the model believes, and treats a miss by a factor in either direction alike. Lower is better; 0.1 is roughly a 10% miss. Intervals in brackets are 90% intervals over questions. Coverage verdicts leave out single-number intervals, which say "I know this exactly" and are counted on their own line.

## By kind of question

Knowledge questions ask what is known (the Python standard library, the Unicode database); statistical ones need noise or irregularity modelled; exact ones have a closed-form answer that must be evaluated.

| Kind | Phase | Questions | Score | 50% hits | 90% hits |
|---|---|---|---|---|---|
| exact | instinct | 8 | 0.122 | 8 of 8 (100%) | 8 of 8 (100%) |
| exact | worked | 8 | 0.045 | 8 of 8 (100%) | 8 of 8 (100%) |
| knowledge | instinct | 48 | 0.291 | 27 of 48 (56%) | 33 of 48 (69%) |
| knowledge | worked | 48 | 0.072 | 32 of 48 (67%) | 39 of 48 (81%) |
| statistical | instinct | 48 | 0.075 | 28 of 48 (58%) | 42 of 48 (88%) |
| statistical | worked | 48 | 0.028 | 26 of 48 (54%) | 44 of 48 (92%) |

## Questions

Each answer is shown as estimate [90% interval], ✓ or ✗ for whether the 50% and 90% intervals contain the true answer, and its score.

| # | Question | True answer | Instinct | Worked |
|---|---|---|---|---|
| 1 | Unicode names with the word MUSICAL | 518 | 60 [30, 120] 50✗ 90✗ · 1.837 | 470 [448, 490] 50✗ 90✗ · 0.079 |
| 2 | lines in `smtplib` | 1,123 | 1,600 [1,100, 2,300] 50✗ 90✓ · 0.191 | 1,130 [1,000, 1,290] 50✓ 90✓ · 0.017 |
| 3 | highest point of a 426-step walk | 15.8 | 16.5 [1.3, 33.9] 50✓ 90✓ · 0.202 | 15.98 [15.65, 16.31] 50✗ 90✓ · 0.006 |
| 4 | draws until a repeat, d = 35,930 | 238.2 | 238 [61, 464] 50✓ 90✓ · 0.119 | 238.2 [236.5, 240] 50✓ 90✓ · 0.001 |
| 5 | digit sum of 2^1269 | 1,736 | 1,365 [1,270, 1,460] 50✗ 90✗ · 0.211 | 1,724 [1,632, 1,816] 50✓ 90✓ · 0.008 |
| 6 | names in `timeit.__all__` | 4 | 3 [1, 6] 50✓ 90✓ · 0.121 | 4 [4, 5] 50✓ 90✓ · 0.004 |
| 7 | mean distance in a 1 × 2.52 rectangle | 0.9621 | 0.97 [0.8, 1.17] 50✓ 90✓ · 0.024 | 0.9625 [0.9585, 0.9665] 50✓ 90✓ · 0.001 |
| 8 | code points in category Po | 628 | 630 [520, 760] 50✓ 90✓ · 0.024 | 790 [735, 845] 50✗ 90✗ · 0.198 |
| 9 | assigned in the Thaana block | 50 | 50 [48, 52] 50✓ 90✓ · 0.004 | 50 [49, 51] 50✓ 90✓ · 0.001 |
| 10 | function definitions in `optparse` | 122 | 380 [280, 500] 50✗ 90✗ · 0.991 | 105 [85, 130] 50✗ 90✓ · 0.081 |
| 11 | primes in [3,164,661, 3,229,443] | 4,399 | 4,325 [4,280, 4,370] 50✗ 90✗ · 0.012 | 4,325 [4,240, 4,410] 50✗ 90✓ · 0.010 |
| 12 | Collatz steps from 87,974,385,043 | 246 | 120 [60, 200] 50✗ 90✗ · 0.501 | 170 [95, 250] 50✗ 90✓ · 0.211 |
| 13 | longest increasing subsequence, n = 112 | 17.81 | 17.2 [15.8, 18.6] 50✗ 90✓ · 0.018 | 17.33 [17, 17.7] 50✗ 90✗ · 0.018 |
| 14 | mean distance in a 1 × 9.91 rectangle | 3.359 | 3.36 [3.15, 3.6] 50✓ 90✓ · 0.008 | 3.356 [3.345, 3.367] 50✓ 90✓ · 0.001 |
| 15 | assigned in the Thai block | 87 | 87 [78, 89] 50✓ 90✓ · 0.007 | 87 [86, 88] 50✓ 90✓ · 0.000 |
| 16 | Unicode names with the word FRACTION | 98 | 90 [55, 140] 50✓ 90✓ · 0.069 | 80 [62, 100] 50✗ 90✓ · 0.119 |
| 17 | code points in category Pc | 10 | 10 [7, 16] 50✓ 90✓ · 0.033 | 10 [9, 12] 50✓ 90✓ · 0.005 |
| 18 | function definitions in `traceback` | 70 | 95 [60, 150] 50✗ 90✓ · 0.160 | 66 [48, 90] 50✓ 90✓ · 0.048 |
| 19 | lines in `shutil` | 1,569 | 1,450 [1,200, 1,750] 50✗ 90✓ · 0.042 | 1,490 [1,340, 1,700] 50✗ 90✓ · 0.026 |
| 20 | longest increasing subsequence, n = 1,643 | 75.54 | 75 [71.5, 78] 50✓ 90✓ · 0.007 | 75 [73.8, 76.2] 50✗ 90✓ · 0.004 |
| 21 | highest point of a 1,512-step walk | 31.04 | 31 [27.5, 34.5] 50✓ 90✓ · 0.014 | 31.02 [30.2, 31.85] 50✓ 90✓ · 0.003 |
| 22 | primes in [8,284,359, 8,296,430] | 753 | 758 [733, 782] 50✓ 90✓ · 0.005 | 758 [712, 804] 50✓ 90✓ · 0.008 |
| 23 | Collatz steps from 337,264,368,477 | 248 | 330 [160, 520] 50✗ 90✓ · 0.130 | 185 [115, 265] 50✗ 90✓ · 0.164 |
| 24 | names in `weakref.__all__` | 13 | 11 [7, 18] 50✓ 90✓ · 0.082 | 13 [12, 14] 50✓ 90✓ · 0.003 |
| 25 | draws until a repeat, d = 6,620,093 | 3,225 | 3,225 [824, 6,298] 50✓ 90✓ · 0.119 | 3,225 [824, 6,300] 50✓ 90✓ · 0.119 |
| 26 | digit sum of 2^1219 | 1,550 | 1,651 [1,560, 1,742] 50✗ 90✗ · 0.038 | 1,650 [1,560, 1,740] 50✗ 90✗ · 0.038 |
| 27 | function definitions in `hmac` | 11 | 30 [14, 60] 50✗ 90✗ · 0.625 | 12 [9, 16] 50✓ 90✓ · 0.042 |
| 28 | assigned in the Playing Cards block | 82 | 82 [78, 84] 50✓ 90✓ · 0.003 | 80 [60, 84] 50✓ 90✓ · 0.015 |
| 29 | longest increasing subsequence, n = 4,365 | 125.4 | 125 [118.9, 131.1] 50✓ 90✓ · 0.007 | 125 [124, 126] 50✓ 90✓ · 0.002 |
| 30 | mean distance in a 1 × 4.45 rectangle | 1.572 | 1.53 [1.47, 1.6] 50✗ 90✓ · 0.014 | 1.572 [1.56, 1.585] 50✓ 90✓ · 0.001 |
| 31 | Unicode names with the word CAPITAL | 2,032 | 1,800 [900, 3,200] 50✓ 90✓ · 0.107 | 1,850 [1,680, 2,060] 50✗ 90✓ · 0.053 |
| 32 | Collatz steps from 904,534,976,486 | 239 | 330 [180, 520] 50✗ 90✓ · 0.171 | 239 [232, 246] 50✓ 90✓ · 0.003 |
| 33 | code points in category So | 6,639 | 6,700 [5,300, 8,200] 50✓ 90✓ · 0.030 | 6,640 [6,450, 6,850] 50✓ 90✓ · 0.003 |
| 34 | digit sum of 2^2531 | 3,353 | 3,430 [3,300, 3,560] 50✗ 90✓ · 0.012 | 3,436 [3,306, 3,566] 50✗ 90✓ · 0.013 |
| 35 | lines in `functools` | 1,036 | 1,000 [700, 1,400] 50✓ 90✓ · 0.051 | 1,000 [880, 1,120] 50✓ 90✓ · 0.020 |
| 36 | draws until a repeat, d = 46,781 | 271.7 | 272 [69, 529] 50✓ 90✓ · 0.120 | 271.7 [69, 530] 50✓ 90✓ · 0.119 |
| 37 | highest point of a 869-step walk | 22.92 | 23.6 [20.8, 26.4] 50✓ 90✓ · 0.020 | 23.03 [22.55, 23.5] 50✓ 90✓ · 0.004 |
| 38 | names in `locale.__all__` | 23 | 60 [25, 110] 50✗ 90✗ · 0.558 | 22 [19, 26] 50✓ 90✓ · 0.023 |
| 39 | primes in [591,475, 604,946] | 1,020 | 1,013 [958, 1,068] 50✓ 90✓ · 0.007 | 1,013 [980, 1,046] 50✓ 90✓ · 0.005 |
| 40 | longest increasing subsequence, n = 2,201 | 87.91 | 88.9 [86.5, 91.2] 50✗ 90✓ · 0.006 | 87.4 [86.7, 88.1] 50✗ 90✓ · 0.003 |
| 41 | code points in category Me | 13 | 153 [120, 185] 50✗ 90✗ · 2.288 | 13 [12, 14] 50✓ 90✓ · 0.003 |
| 42 | lines in `tabnanny` | 340 | 440 [350, 560] 50✗ 90✗ · 0.157 | 340 [305, 385] 50✓ 90✓ · 0.013 |
| 43 | primes in [310,586, 338,601] | 2,242 | 2,208 [2,135, 2,280] 50✗ 90✓ · 0.008 | 2,206 [2,165, 2,248] 50✗ 90✓ · 0.009 |
| 44 | mean distance in a 1 × 4.51 rectangle | 1.59 | 1.62 [1.46, 1.8] 50✓ 90✓ · 0.015 | 1.59 [1.586, 1.595] 50✓ 90✓ · 0.000 |
| 45 | function definitions in `csv` | 17 | 35 [12, 80] 50✗ 90✓ · 0.353 | 22 [19, 25] 50✗ 90✗ · 0.185 |
| 46 | digit sum of 2^7366 | 10,060 | 9,981 [9,759, 10,203] 50✓ 90✓ · 0.004 | 9,981 [9,759, 10,203] 50✓ 90✓ · 0.004 |
| 47 | Collatz steps from 189,630,655,112 | 291 | 130 [70, 230] 50✗ 90✗ · 0.562 | 169 [130, 210] 50✗ 90✗ · 0.449 |
| 48 | draws until a repeat, d = 2,138 | 58.62 | 58.6 [15, 113] 50✓ 90✓ · 0.119 | 58.62 [57.9, 59.3] 50✓ 90✓ · 0.001 |
| 49 | names in `base64.__all__` | 22 | 20 [17, 23] 50✗ 90✓ · 0.051 | 20 [20, 22] 50✗ 90✓ · 0.042 |
| 50 | Unicode names with the word GREEK | 531 | 200 [100, 350] 50✗ 90✗ · 0.737 | 510 [488, 532] 50✗ 90✓ · 0.023 |
| 51 | assigned in the General Punctuation block | 111 | 105 [101, 108] 50✗ 90✗ · 0.043 | 111 [110, 112] 50✓ 90✓ · 0.000 |
| 52 | highest point of a 707-step walk | 20.72 | 21.2 [3.3, 43.8] 50✓ 90✓ · 0.184 | 20.72 [20.25, 21.2] 50✓ 90✓ · 0.003 |
| 53 | lines in `glob` | 572 | 230 [160, 330] 50✗ 90✗ · 0.753 | 290 [242, 345] 50✗ 90✗ · 0.601 |
| 54 | function definitions in `webbrowser` | 25 | 75 [45, 120] 50✗ 90✗ · 0.843 | 32 [22, 45] 50✗ 90✓ · 0.132 |
| 55 | assigned in the Lao block | 83 | 83 [78, 88] 50✓ 90✓ · 0.005 | 82 [77, 85] 50✓ 90✓ · 0.008 |
| 56 | longest increasing subsequence, n = 452 | 38.19 | 37.6 [35.8, 39.4] 50✓ 90✓ · 0.008 | 37.9 [37.1, 38.7] 50✓ 90✓ · 0.004 |
| 57 | highest point of a 1,229-step walk | 27.5 | 28 [4, 58] 50✓ 90✓ · 0.186 | 27.98 [27.43, 28.52] 50✗ 90✓ · 0.009 |
| 58 | digit sum of 2^8596 | 11,455 | 11,646 [11,406, 11,886] 50✗ 90✓ · 0.010 | 11,646 [11,405, 11,890] 50✗ 90✓ · 0.009 |
| 59 | draws until a repeat, d = 6,016 | 97.88 | 92 [25, 190] 50✓ 90✓ · 0.131 | 97.88 [96.8, 99] 50✓ 90✓ · 0.001 |
| 60 | names in `gzip.__all__` | 5 | 4 [2, 10] 50✓ 90✓ · 0.118 | 5 [4, 6] 50✓ 90✓ · 0.007 |
| 61 | code points in category Pf | 10 | 10 [8, 13] 50✓ 90✓ · 0.027 | 10 [9, 12] 50✓ 90✓ · 0.005 |
| 62 | primes in [335,112, 371,030] | 2,787 | 2,810 [2,750, 2,870] 50✗ 90✓ · 0.004 | 2,812 [2,765, 2,860] 50✗ 90✓ · 0.005 |
| 63 | Unicode names with the word HEBREW | 134 | 88 [60, 130] 50✗ 90✗ · 0.255 | 134 [128, 140] 50✓ 90✓ · 0.005 |
| 64 | mean distance in a 1 × 2.07 rectangle | 0.826 | 0.8 [0.75, 0.85] 50✗ 90✓ · 0.017 | 0.8256 [0.823, 0.828] 50✓ 90✓ · 0.000 |
| 65 | Collatz steps from 23,010,656,711 | 195 | 150 [60, 260] 50✗ 90✓ · 0.141 | 165 [88, 255] 50✓ 90✓ · 0.094 |
| 66 | code points in category Sk | 125 | 125 [100, 155] 50✓ 90✓ · 0.025 | 124 [117, 133] 50✓ 90✓ · 0.009 |
| 67 | draws until a repeat, d = 131,706 | 455.5 | 455 [116, 888] 50✓ 90✓ · 0.120 | 455.5 [453.5, 457.5] 50✓ 90✓ · 0.000 |
| 68 | Unicode names with the word FACE | 179 | 80 [40, 160] 50✗ 90✗ · 0.485 | 116 [109, 123] 50✗ 90✗ · 0.407 |
| 69 | longest increasing subsequence, n = 827 | 52.6 | 52.1 [50.8, 53.4] 50✓ 90✓ · 0.005 | 51.7 [50.1, 53.3] 50✗ 90✓ · 0.009 |
| 70 | digit sum of 2^3289 | 4,430 | 4,455 [4,305, 4,605] 50✓ 90✓ · 0.005 | 4,456 [4,307, 4,605] 50✓ 90✓ · 0.005 |
| 71 | assigned in the Georgian block | 88 | 88 [80, 90] 50✓ 90✓ · 0.003 | 88 [85, 90] 50✓ 90✓ · 0.002 |
| 72 | mean distance in a 1 × 3.1 rectangle | 1.142 | 1.23 [1.1, 1.36] 50✗ 90✓ · 0.038 | 1.143 [1.137, 1.147] 50✓ 90✓ · 0.000 |
| 73 | highest point of a 1,415-step walk | 29.89 | 30 [26, 34] 50✓ 90✓ · 0.019 | 30.02 [29.4, 30.6] 50✓ 90✓ · 0.003 |
| 74 | primes in [188,978, 218,173] | 2,379 | 2,386 [2,340, 2,430] 50✓ 90✓ · 0.002 | 2,388 [2,330, 2,446] 50✓ 90✓ · 0.003 |
| 75 | lines in `statistics` | 1,817 | 940 [700, 1,300] 50✗ 90✗ · 0.519 | 1,100 [850, 1,400] 50✗ 90✗ · 0.396 |
| 76 | function definitions in `operator` | 67 | 60 [20, 140] 50✓ 90✓ · 0.134 | 66 [60, 72] 50✓ 90✓ · 0.013 |
| 77 | names in `difflib.__all__` | 12 | 14 [8, 24] 50✓ 90✓ · 0.090 | 13 [11, 14] 50✓ 90✓ · 0.027 |
| 78 | Collatz steps from 360,172,167,088 | 160 | 130 [70, 220] 50✓ 90✓ · 0.111 | 168 [100, 255] 50✓ 90✓ · 0.067 |
| 79 | Collatz steps from 905,376,815,232 | 177 | 108 [60, 175] 50✗ 90✗ · 0.285 | 177 [165, 190] 50✓ 90✓ · 0.007 |
| 80 | names in `tabnanny.__all__` | 3 | 3 [1, 6] 50✓ 90✓ · 0.076 | 3 [3, 4] 50✓ 90✓ · 0.004 |
| 81 | digit sum of 2^706 | 925 | 958 [888, 1,028] 50✗ 90✓ · 0.018 | 961 [890, 1,030] 50✗ 90✓ · 0.020 |
| 82 | draws until a repeat, d = 944,525 | 1,219 | 1,219 [180, 2,300] 50✓ 90✓ · 0.125 | 1,219 [311, 2,379] 50✓ 90✓ · 0.119 |
| 83 | function definitions in `weakref` | 65 | 80 [40, 140] 50✓ 90✓ · 0.116 | 105 [88, 125] 50✗ 90✗ · 0.398 |
| 84 | primes in [865,988, 892,619] | 1,952 | 1,945 [1,904, 1,986] 50✓ 90✓ · 0.003 | 1,946 [1,885, 2,005] 50✓ 90✓ · 0.004 |
| 85 | code points in category Nd | 680 | 680 [640, 730] 50✓ 90✓ · 0.009 | 680 [664, 700] 50✓ 90✓ · 0.002 |
| 86 | longest increasing subsequence, n = 121 | 18.59 | 18.3 [17, 19.6] 50✓ 90✓ · 0.011 | 18.3 [17.5, 19.1] 50✓ 90✓ · 0.008 |
| 87 | highest point of a 853-step walk | 22.61 | 23.3 [1.8, 57.2] 50✓ 90✓ · 0.204 | 23.31 [22.8, 23.8] 50✗ 90✗ · 0.021 |
| 88 | mean distance in a 1 × 7.13 rectangle | 2.442 | 2.42 [2.35, 2.5] 50✓ 90✓ · 0.006 | 2.441 [2.432, 2.449] 50✓ 90✓ · 0.001 |
| 89 | Unicode names with the word DIGIT | 898 | 300 [200, 420] 50✗ 90✗ · 0.955 | 790 [745, 832] 50✗ 90✗ · 0.106 |
| 90 | assigned in the Gothic block | 27 | 27 [26, 27] 50✓ 90✓ · 0.001 | 27 [26, 28] 50✓ 90✓ · 0.001 |
| 91 | lines in `string` | 314 | 300 [200, 450] 50✓ 90✓ · 0.052 | 320 [285, 365] 50✓ 90✓ · 0.020 |
| 92 | draws until a repeat, d = 4,022 | 80.15 | 80.2 [20, 155] 50✓ 90✓ · 0.120 | 80.15 [79.2, 81.1] 50✓ 90✓ · 0.001 |
| 93 | primes in [1,135,630, 1,167,274] | 2,277 | 2,268 [2,222, 2,314] 50✓ 90✓ · 0.003 | 2,266 [2,236, 2,296] 50✗ 90✓ · 0.003 |
| 94 | assigned in the Greek and Coptic block | 135 | 135 [118, 144] 50✓ 90✓ · 0.014 | 135 [133, 136] 50✓ 90✓ · 0.001 |
| 95 | names in `mailbox.__all__` | 17 | 17 [13, 20] 50✓ 90✓ · 0.014 | 17 [16, 18] 50✓ 90✓ · 0.002 |
| 96 | mean distance in a 1 × 1.09 rectangle | 0.5454 | 0.546 [0.535, 0.558] 50✓ 90✓ · 0.003 | 0.5451 [0.5428, 0.5474] 50✓ 90✓ · 0.001 |
| 97 | code points in category Cf | 170 | 170 [140, 200] 50✓ 90✓ · 0.019 | 170 [160, 184] 50✓ 90✓ · 0.006 |
| 98 | Collatz steps from 70,587,310,865 | 194 | 170 [80, 300] 50✓ 90✓ · 0.103 | 170 [110, 245] 50✗ 90✓ · 0.072 |
| 99 | digit sum of 2^5606 | 7,438 | 7,596 [7,400, 7,790] 50✗ 90✓ · 0.012 | 7,596 [7,395, 7,800] 50✗ 90✓ · 0.011 |
| 100 | Unicode names with the word CYRILLIC | 507 | 256 [200, 320] 50✗ 90✗ · 0.586 | 509 [495, 525] 50✓ 90✓ · 0.004 |
| 101 | longest increasing subsequence, n = 104 | 17.15 | 16.6 [13.6, 19.5] 50✓ 90✓ · 0.023 | 16.55 [15.7, 17.3] 50✗ 90✓ · 0.020 |
| 102 | lines in `reprlib` | 230 | 170 [125, 230] 50✗ 90✓ · 0.164 | 165 [143, 196] 50✗ 90✗ · 0.252 |
| 103 | function definitions in `base64` | 28 | 37 [20, 60] 50✓ 90✓ · 0.124 | 26 [21, 32] 50✓ 90✓ · 0.037 |
| 104 | highest point of a 996-step walk | 24.79 | 24.7 [2, 52] 50✓ 90✓ · 0.194 | 25.17 [24.6, 25.75] 50✗ 90✓ · 0.008 |
