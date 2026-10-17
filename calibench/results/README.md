# Results

Runs of Calibench on real models. Each folder is a complete run directory: the questions, every raw reply, the true answers, and the report. Rerun the scoring with `python3 -m calibench report <folder>`.

Scores are Calibench 2.0's log-scale weighted interval score (lower is better; 0.1 is roughly a 10% miss), with 90% intervals over questions. The table is generated from the runs' reports by `python3 -m calibench index calibench/results --write calibench/results/README.md`; don't edit it by hand.

<!-- index:start -->
| Run | Model | Prompts | Questions | Score, worked [90% interval] | Score, instinct | Worked 50% / 90% hits | Worked answers above the estimate | Reasoning tokens per answer, instinct / worked | Cost |
|---|---|---|---|---|---|---|---|---|---|
| [haiku-5.5-v1-a](haiku-5.5-v1-a/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite v1, 104 | 0.056 [0.035, 0.082] | 0.177 | 62 / 85 of 104 | 62% | 220 / 3,285 | $0.225 |
| [haiku-5.5-v1-b](haiku-5.5-v1-b/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite v1, 104 | 0.050 [0.034, 0.067] | 0.178 | 66 / 91 of 104 | 62% | 236 / 3,320 | $0.226 |
| [haiku-5.5-v1-alt](haiku-5.5-v1-alt/report.md) | openrouter:anthropic/claude-haiku-5.5 | alt | suite v1, 104 | 0.040 [0.027, 0.054] | 0.097 | 66 / 92 of 104 | 59% | 410 / 3,140 | $0.217 |
| [haiku-5.5-v2](haiku-5.5-v2/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite v2, 108 | 0.068 [0.035, 0.111] | 0.098 | 80 / 94 of 108 | 51% | 244 / 4,253 | $0.285 |
| [haiku-5.5-calc1](haiku-5.5-calc1/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite calc1, 40 | 0.000 [0.000, 0.000] | 0.019 | 40 / 40 of 40 | 52% | 493 / 3,679 | $0.100 |
| [haiku-5.5-v1-c](haiku-5.5-v1-c/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite v1, 104 | 0.051 [0.034, 0.069] | 0.188 | 58 / 88 of 104 | 59% | 218 / 3,463 | $0.233 |
| [haiku-5.5-v1-quantiles](haiku-5.5-v1-quantiles/report.md) | openrouter:anthropic/claude-haiku-5.5 | quantiles | suite v1, 104 | 0.047 [0.033, 0.063] | 0.249 | 61 / 85 of 104 | 62% | 167 / 3,412 | $0.229 |
| [openrouter_anthropic_claude-haiku-5.5-2026-10-17](openrouter_anthropic_claude-haiku-5.5-2026-10-17/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | seed `2026-10-17`, 26 | 0.104 [0.044, 0.177] | 0.185 | 15 / 18 of 26 | 52% | 182 / 4,513 | $0.072 |
<!-- index:end -->

## Claude Haiku 5.5 on suite v1: a percentile format

One run with `--prompts quantiles`, asking for the 5th, 25th, 50th, 75th and 95th percentiles instead of an estimate and two intervals: the same five values, asked for differently. The full analysis is in [METHODOLOGY.md](../METHODOLOGY.md#reliability).

- **Worked answers didn't change:** 0.047 against 0.050–0.056 for the standard runs, differences within noise, with the same coverage and the same lean low.
- **Instinct answers got worse:** 0.249 against 0.177–0.188, and their 90% intervals held the answer only 69 times in 104. The percentile format drew less reasoning before the instinct answer (167 tokens on average, against about 225).
- **Across all five v1 runs, the instinct score follows the reasoning the prompt draws out**: least reasoning, worst instinct score (percentiles); most reasoning, best (the alternative wording). The worked score barely moves. Compare models on worked answers.

## Claude Haiku 5.5 on suite v1: three runs, consistency

Three independent runs with the standard prompts (a, b and c), analysed together by `python3 -m calibench consistency`, generated below.

<!-- consistency:start -->
3 runs (haiku-5.5-v1-a, haiku-5.5-v1-b, haiku-5.5-v1-c) of openrouter:anthropic/claude-haiku-5.5, with standard prompts, on the same questions: 104 answered in every run. Worked answers only.

| | |
|---|---|
| Questions where every run gave the same estimate | 32 of 104 (31%) |
| … and that estimate was exactly right | 15 of 32 (47%) |
| 90% intervals containing the answer, when the runs agree | 95 of 96 (99%) |
| 90% intervals containing the answer, when they disagree | 169 of 216 (78%) |
| Rank correlation with a run's error: the other runs' disagreement [90% interval] | 0.447 [0.316, 0.569] |
| Rank correlation with a run's error: its own stated 90% width [90% interval] | 0.410 [0.273, 0.520] |
| Score of a single run, mean | 0.052 |
| Score of the runs' averaged forecast | 0.049 |
| Improvement from averaging [90% interval] | 0.003 [0.002, 0.005] |

A run's *error* is the distance of its estimate from the true answer on the log scale. The *other runs' disagreement* is the spread of the other runs' estimates on the same scale: it shares no estimate with the error it is compared with, so the correlation isn't built in. A correlation near 1 means the signal ranks the answers that are most wrong; the two rows compare the model's inconsistency with its stated uncertainty as warnings. Intervals are bootstraps over questions. The averaged forecast averages each of the five stated values across runs on the log scale.
<!-- consistency:end -->

- **When the runs agree, trust the intervals; when they don't, widen them.** Where all three runs gave the same estimate, their 90% intervals held the answer 99% of the time; where they disagreed, 78%.
- **Disagreement and stated width warn about equally well.** The other runs' disagreement ranks a run's errors about as well as its own stated interval width does (rank correlations of 0.45 and 0.41, with overlapping intervals). Inconsistency is a usable warning, but not a better one than what the model says.
- **Averaging three runs helps a little**: the averaged forecast scores 0.003 better than a single run, a small but clear gain.
- **A correction before publishing.** With only runs a and b, a first version of this analysis gave 0.74 for disagreement against 0.45 for width, which looked like a striking finding. It wasn't: the spread of two estimates bounds their mean error from below, so the two are correlated by construction. The analysis now compares each run's error with the *other* runs' disagreement, which needs three runs; with that, the striking gap disappears.

## Claude Haiku 5.5 across all runs, pooled by family

Worked answers from every Haiku run above, pooled by family, generated by `python3 -m calibench pool <dirs> --write calibench/results/README.md`. Pooling shows which leans hold up beyond one run: a family whose interval for *above the estimate* excludes 50% leans consistently.

<!-- pool:start -->
Worked answers from 8 runs (haiku-5.5-v1-a, haiku-5.5-v1-b, haiku-5.5-v1-c, haiku-5.5-v1-alt, haiku-5.5-v1-quantiles, haiku-5.5-v2, haiku-5.5-calc1, openrouter_anthropic_claude-haiku-5.5-2026-10-17) of openrouter:anthropic/claude-haiku-5.5: 694 answered questions. A question asked in several runs counts once per run.

| Family | Kind | Answers | Score | 90% intervals containing the answer [90% interval] | True answer above the estimate [90% interval] |
|---|---|---|---|---|---|
| `days_between` | calculation | 6 | 0.000 | 6 of 6 (100%) [69%, 100%] | 50% [22%, 78%] |
| `days_between_far` | calculation | 10 | 0.000 | 10 of 10 (100%) [79%, 100%] | 45% [19%, 65%] |
| `factorial_digits` | calculation | 6 | 0.000 | 6 of 6 (100%) [69%, 100%] | 50% [22%, 78%] |
| `factorial_digits_big` | calculation | 10 | 0.000 | 10 of 10 (100%) [79%, 100%] | 50% [27%, 73%] |
| `friday13` | calculation | 6 | 0.005 | 6 of 6 (100%) [69%, 100%] | 50% [22%, 78%] |
| `multiply` | calculation | 6 | 0.000 | 6 of 6 (100%) [69%, 100%] | 50% [22%, 78%] |
| `multiply_big` | calculation | 10 | 0.000 | 10 of 10 (100%) [79%, 100%] | 45% [19%, 65%] |
| `partitions` | calculation | 6 | 0.383 | 5 of 6 (83%) [50%, 96%] | 50% [22%, 78%] |
| `partitions_big` | calculation | 10 | 0.001 | 10 of 10 (100%) [79%, 100%] | 70% [44%, 87%] |
| `birthday` | exact | 48 | 0.045 | 48 of 48 (100%) [95%, 100%] | 54% [42%, 65%] |
| `module_all` | knowledge | 48 | 0.017 | 47 of 48 (98%) [91%, 100%] | 60% [49%, 71%] |
| `stdlib_defs` | knowledge | 48 | 0.083 | 42 of 48 (88%) [78%, 93%] | 49% [38%, 62%] |
| `stdlib_lines` | knowledge | 48 | 0.165 | 31 of 48 (65%) [53%, 75%] | 75% [64%, 84%] |
| `unicode_block` | knowledge | 48 | 0.015 | 44 of 48 (92%) [83%, 96%] | 59% [46%, 69%] |
| `unicode_category` | knowledge | 48 | 0.016 | 45 of 48 (94%) [85%, 97%] | 47% [35%, 58%] |
| `unicode_word` | knowledge | 48 | 0.185 | 18 of 48 (38%) [27%, 49%] | 89% [78%, 93%] |
| `collatz_steps` | statistical | 48 | 0.122 | 42 of 48 (88%) [78%, 93%] | 54% [42%, 65%] |
| `digit_sum_pow2` | statistical | 48 | 0.013 | 41 of 48 (85%) [75%, 92%] | 27% [18%, 39%] |
| `lis` | statistical | 48 | 0.010 | 38 of 48 (79%) [68%, 87%] | 100% [95%, 100%] |
| `primes_in_range` | statistical | 48 | 0.007 | 45 of 48 (94%) [85%, 97%] | 58% [46%, 69%] |
| `rect_distance` | statistical | 48 | 0.001 | 48 of 48 (100%) [95%, 100%] | 69% [57%, 79%] |
| `walk_max` | statistical | 48 | 0.009 | 35 of 48 (73%) [61%, 82%] | 27% [18%, 39%] |
| **all** |  | 694 | 0.051 | 593 of 694 (85%) [83%, 88%] | 58% [55%, 61%] |

A family whose interval for *above the estimate* excludes 50% leans consistently: above 50% means the model underestimates it, below 50% that it overestimates. An answer equal to the estimate counts as half above.
<!-- pool:end -->

What the pooled answers say:

- **Haiku's 90% intervals are too narrow overall**: the interval for their coverage lies below 90%.
- **It leans low overall**: the true answer lies above its estimate more often than half the time, with an interval that excludes 50%.
- **The leans are specific to families, and stable**: it underestimates the longest increasing subsequence every time, and Unicode name counts and module lengths nearly every time; it overestimates random-walk peaks and digit sums of powers of two. These are the same corrections the guessbook found in Claude's own answers.
- **Calculation isn't where it fails**: on every calculation family its intervals held the answer, often around an exact estimate.

## Claude Haiku 5.5 on suite calc1: harder calculation

Forty harder calculation questions, to find where its arithmetic gives out. It didn't, much.

- **Exact on 28 of 40 worked answers**: all 10 factorial digit counts (for n up to 167 million), 9 of 10 day counts across millennia (the tenth off by one), and 9 of 10 products of two numbers of up to 12 digits. The tenth product was computed correctly and then written rounded to 14 significant figures.
- **Partition numbers up to p(3,947) were never exact**, but always within 0.2%, and always inside the 90% interval.
- **Its intervals were too wide everywhere**: all 40 worked 90% intervals and all 40 50% intervals held the answer, and it still never gave a single number. On a log scale this costs almost nothing, so the worked score rounds to 0.000.

So a model as strong at calculation as Haiku makes these families nearly uninformative about its score, and informative mainly about whether it will commit to an answer it has computed. A calculation family that discriminates strong models would need answers no model can reach exactly without tools.

## Claude Haiku 5.5 on suite v2: the calculation questions

The first run on suite v2, which adds five calculation families: days between dates, digits of n!, Friday the 13ths, partition numbers and products.

- **Haiku is a strong calculator.** Its worked estimates were exactly right on all 24 date, factorial, Friday-the-13th and multiplication questions, and nearly all of its instinct estimates were too: it multiplied 6,787 × 2,142 exactly without being asked to work.
- **Its intervals don't trust its arithmetic.** It never gave a single-number answer, even for products it had computed exactly, and its worked 50% intervals held the answer 70% of the time leaving out single numbers: too wide. On these questions the log-scale score barely charges for that, because ±50 around fourteen million is almost no width.
- **One confident slip by a factor of ten.** For the partition number p(507) it answered 3.385 × 10²², with a 90% interval of [3.33, 3.44] × 10²². The answer is 3.385 × 10²¹: the digits right to four places, the exponent off by one, at instinct and after working. That single question scores 2.30 and moves the mean worked score from 0.047 to 0.068. A calibrated model's intervals have to allow for its own rare slips, and these didn't.
- **The old leans are still there.** Unicode name counts were above the estimate in all 6 questions and outside every 90% interval; the longest increasing subsequence was above in all 6; random-walk peaks were below in 5 of 6.

## Claude Haiku 5.5 on suite v1: test–retest

Two independent runs of the same model on the standard suite, to measure how far one run can be trusted. The full analysis is in [METHODOLOGY.md](../METHODOLOGY.md#reliability).

- **The score reproduces:** 0.056 and 0.050 for worked answers, a difference of 0.006 [−0.012, 0.029]; 0.177 and 0.178 for instinct.
- **The coverage verdict doesn't:** worked 90% intervals held the answer 82% of the time in one run (too narrow) and 88% in the other (consistent with calibrated). Pooled: 176 of 208, 85%. Haiku is somewhat overconfident in its 90% intervals, by less than the 26-question run suggested.
- **Working it out helps a lot:** in both runs the worked score is about a third of the instinct score, and the median error falls from about 3% to 0.7%.
- **The same misses twice:** nine questions fell outside both runs' 90% intervals, seven of them underestimated open-ended counts (Unicode names with a common word, and modules that grew in Python 3.13).

## Claude Haiku 5.5 on suite v1: a second wording

One run with `--prompts alt`, to measure how much the wording of the prompts matters. The full analysis is in [METHODOLOGY.md](../METHODOLOGY.md#reliability).

- **Worked answers barely moved:** 0.040 against 0.056 and 0.050, a difference whose interval just reaches zero.
- **Instinct answers changed a lot:** 0.097 against 0.177 and 0.178, a clear difference. The second wording ("say what your gut tells you") let the model reason about twice as much before its instinct answer.
- **The lean stayed:** the true answer was above the worked estimate 59% of the time.

## Claude Haiku 5.5 on seed 2026-10-17, the first run

This run was first scored with Calibench 1.0's relative score (9.1% worked, 16.7% instinct), which turned out not to be proper; see [METHODOLOGY.md](../METHODOLOGY.md). Its replies are unchanged and it has been re-scored.

- **Working it out helps.** It lowered the score on 19 of 26 questions, from 0.185 to 0.104; the improvement's 90% interval is about [0.03, 0.14], so it's real.
- **The 90% intervals are too narrow.** After working, only 18 of 26 held the answer (69%, 90% interval 53–82%), against nine in ten for a calibrated model.
- **Overconfident after a calculation.** On the statistical questions, working it out cut 90% hits from 11 of 12 to 8 of 12. When a formula was available the model trusted it as exact. On the random walk it modelled the simulation noise correctly, said "the formula itself is essentially exact here", and missed by two standard errors because the formula lacked a −½ correction.
- **Open-ended counts run far low.** For the Unicode names containing HAND and WHITE, it estimated 125 and 105 against 304 and 290: the omission bias seen in the guessbook, but at about −60% instead of −10 to −36%. Its intervals were wide and still nowhere near.
- **Closed facts are recalled well.** `pprint.__all__` (7), `locale.__all__` (22 against 23), category Zs (17), the Ethiopic block (358): exact or nearly.
