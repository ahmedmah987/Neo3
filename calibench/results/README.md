# Results

Runs of Calibench on real models. Each folder is a complete run directory: the questions, every raw reply, the true answers, and the report. Rerun the scoring with `python3 -m calibench report <folder>`.

Scores are Calibench 2.0's log-scale weighted interval score (lower is better; 0.1 is roughly a 10% miss), with 90% intervals over questions. The table is generated from the runs' reports by `python3 -m calibench index calibench/results --write calibench/results/README.md`; don't edit it by hand.

<!-- index:start -->
| Run | Model | Prompts | Questions | Score, worked [90% interval] | Score, instinct | Worked 50% / 90% hits | Worked answers above the estimate | Cost |
|---|---|---|---|---|---|---|---|---|
| [haiku-5.5-v1-a](haiku-5.5-v1-a/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite v1, 104 | 0.056 [0.035, 0.082] | 0.177 | 62 / 85 of 104 | 62% | $0.225 |
| [haiku-5.5-v1-b](haiku-5.5-v1-b/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite v1, 104 | 0.050 [0.034, 0.067] | 0.178 | 66 / 91 of 104 | 62% | $0.226 |
| [haiku-5.5-v1-alt](haiku-5.5-v1-alt/report.md) | openrouter:anthropic/claude-haiku-5.5 | alt | suite v1, 104 | 0.040 [0.027, 0.054] | 0.097 | 66 / 92 of 104 | 59% | $0.217 |
| [haiku-5.5-v2](haiku-5.5-v2/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | suite v2, 108 | 0.068 [0.035, 0.111] | 0.098 | 80 / 94 of 108 | 51% | $0.285 |
| [openrouter_anthropic_claude-haiku-5.5-2026-10-17](openrouter_anthropic_claude-haiku-5.5-2026-10-17/report.md) | openrouter:anthropic/claude-haiku-5.5 | standard | seed `2026-10-17`, 26 | 0.104 [0.044, 0.177] | 0.185 | 15 / 18 of 26 | 52% | $0.072 |
<!-- index:end -->

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
