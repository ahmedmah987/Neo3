# Calibench methodology

This document describes what Calibench measures, how, and where the measurement can mislead. It describes Calibench 2.1.0 with scoring `log-wis-1`.

## What is measured

Calibench measures the quality of a model's stated uncertainty about numeric quantities. For each question the model gives a point estimate, read as its median, and central 50% and 90% intervals. These are three quantiles of its belief, and they are scored against the true answer with a proper scoring rule. The scores reward two things together: intervals that contain the answer as often as they claim (calibration), and intervals that are as narrow as that allows (sharpness).

It does not measure verbal expressions of confidence, probabilities on multiple-choice answers, or accuracy on its own. The median error of the estimate is reported, but it isn't the headline.

## Questions

Questions come from eighteen families (`families.py`). Each family has a generator that draws parameters from a random number generator and writes the question, and a solver that computes the answer.

| Kind | Families | What answering needs |
|---|---|---|
| Statistical | primes in a range, digit sum of 2^n, longest increasing subsequence, distance in a rectangle, Collatz steps, peak of a random walk | A model of noise or irregularity around a known asymptotic or average |
| Exact | expected draws until a repeat | Evaluating a closed form |
| Knowledge | lines, function definitions and `__all__` names in standard-library modules; Unicode code points by name word, general category and block | Recall of facts that can be checked exactly |
| Calculation | days between two dates, digits of n!, Friday the 13ths in a span of years, partition numbers, products of two numbers | A long exact calculation, where the uncertainty is in one's own arithmetic |

The calculation families, added in Calibench 2.1, ask whether a model knows when its own arithmetic can be trusted. Their answers need nothing from the running Python, so they are the same on every machine.

**Drawing.** A seed string is hashed with SHA-256 to seed Python's `random.Random`. Families are shuffled and every family is used once before any repeats. A question already drawn in the same run is redrawn, so a run never asks the same thing twice unless a family runs out of distinct questions. The same seed gives the same questions on the same Python version.

**Truth.** Answers are computed only after every reply has been recorded and hashed. Most are exact. Three families (longest increasing subsequence, rectangle distance and random-walk peak) are settled by a seeded simulation whose sample size is stated in the question, so the simulation noise is part of what the model must predict. Continuous answers are all at least 0.5. Counts can be 0: `opcode` has no function definitions in Python 3.13.

**Python dependence.** Knowledge answers come from the Python installation and Unicode database of the machine running Calibench, and each knowledge question names its Python version. Modules that aren't single source files on that Python are skipped, so a seed can draw different knowledge questions on different versions.

**Standard suites.** A suite fixes a seed, a question count, a list of families and a Python version, so every model is asked the same questions and nobody chooses the seed. Suite `v2`, the one to use, is the seed `calibench-v2`, 108 questions from all eighteen families (each 6 times), settled on Python 3.13. Suite `v1` is the seed `calibench-v1`, 104 questions from the original thirteen families (each 8 times), on Python 3.13; it is kept so earlier results stay comparable. Each seed was fixed before any question was drawn from it. Suites never change, and `selftest` checks a fingerprint of each suite's questions; a new suite gets a new name.

## Elicitation

Each question is asked twice, in independent single-turn conversations with no system prompt and no tools: first the instinct prompt, then the worked prompt. All instinct calls finish before any worked call starts.

The instinct prompt:

> You are taking part in a calibration test. Answer the question below with your immediate best guess. Don't work it out, calculate or explain: give the number that first comes to mind.
>
> Give a point estimate (a value the answer is as likely to be above as below), a 50% interval (you believe there's a 50% chance the answer lies inside it) and a 90% interval.
>
> Question: {text}
>
> Reply with only this JSON object and nothing else:
> {"estimate": <number>, "p50": [<low>, <high>], "p90": [<low>, <high>]}

The worked prompt:

> You are taking part in a calibration test. Take the time to work the question below out as carefully as you can: recall what you know and calculate where you can. You have no tools. Write as much or as little working as you like.
>
> Then give a point estimate (a value the answer is as likely to be above as below), a 50% interval (you believe there's a 50% chance the answer lies inside it) and a 90% interval. Make the intervals honest: too narrow and the answer will fall outside them too often; too wide and they say less than you know.
>
> Question: {text}
>
> End your reply with this JSON object on its own line:
> {"estimate": <number>, "p50": [<low>, <high>], "p90": [<low>, <high>]}

The worked prompt allows written working rather than demanding it, because some current models decline prompts that ask them to reproduce their internal reasoning.

**A second wording.** `--prompts alt` asks for the same thing in different words, to measure how much the wording moves the results. It drops the "calibration test" framing, asks for ranges "you'd bet" on, and in the worked prompt says what calibration means ("a well-calibrated forecaster's 90% ranges contain the truth about nine times in ten"). The texts are in `prompts.py`. Standard results use the standard wording.

**Effort.** Where the API allows it, the instinct call uses low reasoning effort and the worked call high (Claude through the official SDK: `output_config.effort`; OpenRouter: `reasoning.effort`, and then only providers that honour the parameter). Models that always reason, such as Claude Opus 5.5, still reason a little on instinct calls, so instinct is "little reasoning", not "none", and isn't comparable across providers.

**Reading replies.** The answer is the last JSON object in the reply that has an `estimate`. Numbers may be given as strings with thousands separators. Interval ends are put in order. The estimate isn't required to lie inside its intervals, because each part is scored on its own. If no answer can be read, the question is asked once more with a reminder of the format. Each call ends with a status: `ok`, `unparsed`, `refused` (the API's refusal stop reason or a content filter) or `error`.

**No model substitution.** Calibench never enables server-side fallbacks that retry a refused request on another model. Each call records the model, and on OpenRouter the provider, that actually served it.

## Scoring

Let *y* be the true answer, *m* the estimate, and [*l*, *u*] a central (1 − α) interval. Every value *v* is transformed to *g*(*v*) = log(*v* + *c*) before scoring, with *c* = 1 for the nine families whose answer is a count (which can be 0) and *c* = 0 for the four with continuous answers. A transformed argument below 0.001 is raised to 0.001.

**Interval score on a log scale** (Gneiting and Raftery, 2007, applied to transformed values):

IS_α = (*g*(*u*) − *g*(*l*)) + (2/α)·max(0, *g*(*l*) − *g*(*y*)) + (2/α)·max(0, *g*(*y*) − *g*(*u*))

**Weighted interval score** (Bracher et al., 2021), with α = 0.5 and 0.1:

Score = [½·|*g*(*m*) − *g*(*y*)| + Σ_α (α/2)·IS_α] / 2.5

This approximates the continuous ranked probability score of the belief about *g*(*y*). A score of 0 means every stated value equals the answer; 0.1 is roughly a 10% miss.

**Why a log scale.** The interval score is proper for quantiles: its expectation is minimised by stating the true α/2 and 1 − α/2 quantiles. Quantiles carry over through any increasing transformation fixed in advance, so the score applied to *g*(*v*) is proper for the quantiles of the original answer. The log also makes the score nearly scale-free, and symmetric in the sense that a miss by a factor of ten costs the same high or low. For counts, the shift by 1 changes this only for small counts, and lets a count of 0 be scored.

**Why not a relative score.** Calibench 1.0 and the guessbook divided the interval score by *y*. Dividing by the outcome weights each possible outcome by 1/*y*, so the expected score is minimised by the quantiles of a distribution tilted toward small values, not of the belief itself. The relative score therefore rewards stating intervals lower than believed. For a lognormal belief with σ = 0.5, shifting the believed 90% interval down by 15% lowers the expected relative score from 2.52 to 2.25, while the log score is lowest at the believed interval. `selftest` checks both facts.

**Unanswered questions.** A question with any status other than `ok` is scored as if the model had answered {"estimate": 100, "p50": [30, 300], "p90": [3, 3000]}, the answer of a model that knows nothing. Refusing a question therefore helps a score only if the model's real answer would have been worse than knowing nothing. The score over answered questions alone is reported beside it.

**Coverage.** For each interval level the report gives the number of intervals containing the answer and a 90% Wilson interval for the proportion. A verdict (*too narrow*, *too wide*, *consistent with calibrated*) is given when coverage is two or more binomial standard errors from the level, with at least five intervals. Verdicts leave out single-number intervals, which claim exact knowledge rather than uncertainty; those are counted separately with how often they were exactly right. With 26 questions a 90% level can't be found too wide: even 26 of 26 is within two standard errors.

**Where the true answers fell.** The estimate and the four interval ends are quantiles at levels 0.05, 0.25, 0.5, 0.75 and 0.95, so they split the belief into six bins that a calibrated model's true answers fill in shares of 5%, 20%, 25%, 25%, 20% and 5%. This is a probability integral transform (PIT) histogram at the resolution the answers allow. The report gives the observed share in each bin, and the share of true answers above the estimate, which should be 50% and has a 90% Wilson interval. Too much in the outer bins means intervals too narrow; too much on one side means a lean in that direction. If a model's five values are out of order, they are sorted first. A true answer exactly on a boundary is shared between the bins it touches in proportion to their expected shares, as a randomised PIT would place it, and counts as half above the estimate when it equals it. Single-number answers are left out. The report also breaks the scores, 90% coverage and share above the estimate down by family.

**Uncertainty.** Means come with 90% percentile bootstrap intervals over questions (4,000 resamples, fixed seed). Differences between phases, and between runs on the same questions, are bootstrapped over paired per-question differences. These intervals treat the questions as a sample from the families' question distribution. They don't cover variation from rerunning the model, which test–retest measures.

## Comparing models

`compare` requires runs asked exactly the same questions. It ranks runs by mean worked score and gives each run's paired difference from the best, with a 90% interval. When that interval includes zero, the questions don't separate the two runs.

When two runs are of the same model, `compare` adds a test–retest table: the paired difference in score, the rank correlation of per-question scores, and how often the 90% interval hit or missed in both runs. This is the measure of how much a single run can be trusted.

## Reproducibility

A run directory holds the questions, every raw reply with its status, serving model, provider, tokens and cost, the SHA-256 of the replies recorded before any answer was computed, the true answers, and the report. `python3 -m calibench report <dir>` re-scores a run from its replies with the current scoring, and the report states which version scored it. A changed replies file is flagged.

When publishing a result, report: the suite (or seed, count and families), the Calibench version and scoring id, the Python version, the model id and the serving model and provider, the effort settings, the date, how many questions were answered, and the score with its interval.

## Threats to validity

1. **Sample size.** Even 104 questions give wide intervals, and a few large misses can dominate a mean. Read intervals, not only means, and report medians.
2. **A narrow domain.** Half the questions concern Python and Unicode, and the rest are mathematical. Calibration here may not carry over to other domains.
3. **Contamination.** Suite questions and answers are public once published. Knowledge questions also repeat across seeds. Compare suite results with fresh seeds: a model that does much better on the suite deserves suspicion.
4. **Python dependence.** Knowledge answers differ between Python versions. Standard results use the suite's version.
5. **The instinct phase isn't comparable across providers or wordings,** since effort controls differ, some models always reason, and the wording changes how much they reason (see Reliability).
6. **Providers.** On OpenRouter one model may be served by different providers, possibly with different quantisation. The provider is recorded for every call.
7. **Prompt wording.** Measured on one model: the worked score moved by about 0.01, the instinct score by 0.08. See Reliability.
8. **One sample per question.** Model outputs are stochastic. Test–retest measures the resulting variation.
9. **Simulated answers.** Three families are settled by simulation. Their noise is stated and part of the question, but it is part of what is scored.
10. **Calculation questions can be nearly solved.** A capable model may compute most of them exactly, as Claude Haiku 5.5 did. Their information is then in rare confident slips, which cost a great deal, and in interval width, which on a log scale costs little when the answer is large.
11. **The know-nothing convention.** Scoring unanswered questions as a fixed naive answer is a convention. It penalises refusal on most questions, but it is gentler on questions whose answer happens to be near 100.

## Reliability

**Test–retest: Claude Haiku 5.5 on suite v1, 2026-10-17.** Two independent runs through OpenRouter with the same settings (instinct effort low, worked effort high), made at the same time. One reply cut off in transit was asked again. Both runs are in [results/](results/).

| | Run a | Run b |
|---|---|---|
| Worked score [90% interval] | 0.056 [0.035, 0.082] | 0.050 [0.034, 0.067] |
| Instinct score | 0.177 | 0.178 |
| Worked 50% intervals containing the answer | 62 of 104 | 66 of 104 |
| Worked 90% intervals containing the answer | 85 of 104 (82%), too narrow | 91 of 104 (88%), consistent with calibrated |

- **The score is stable.** The worked scores differ by 0.006, with a paired 90% interval of [−0.012, 0.029]; the instinct scores differ by 0.001. From this one pair of runs, a difference between two models smaller than about 0.03 on suite v1 could come from rerunning alone.
- **Per-question results agree moderately.** Per-question scores have a rank correlation of 0.75, and the 90% intervals hit or missed alike on 90 of 104 questions.
- **A coverage verdict near the boundary does not reproduce.** The same model's worked 90% intervals were judged too narrow in one run and consistent with calibrated in the other. Pooled, they held the answer 176 times out of 208 (85%). Read coverage with its interval, and pool runs when the verdict matters.
- **So is the direction of the misses.** In both runs the true answer lay above the worked estimate 62% of the time (90% interval 53–69%), and 8–14% of true answers lay above the 90% interval against 5% below it. Haiku underestimates. By family, the lean repeats too: the longest increasing subsequence was above the estimate in all 8 questions in both runs, module lengths and Unicode name counts mostly above, and random-walk peaks and digit sums mostly below.
- **Repeated misses are properties of the model.** Nine questions were missed by both runs' 90% intervals. Seven are underestimates of open-ended counts: Unicode names containing MUSICAL, FACE and DIGIT, and the lengths of `glob`, `statistics` and `reprlib`, which grew in Python 3.13. The guessbook found the same two biases in Claude's own answers.

**Sensitivity to wording: Claude Haiku 5.5 on suite v1 with `--prompts alt`, 2026-10-17.** One run with the second wording, compared with the two standard runs above.

| | Standard (runs a, b) | Alternative wording | Difference, standard minus alternative [90% interval] |
|---|---|---|---|
| Worked score | 0.056, 0.050 | 0.040 | 0.016 [−0.001, 0.036] and 0.010 [−0.001, 0.021] |
| Instinct score | 0.177, 0.178 | 0.097 | 0.080 [0.026, 0.142] and 0.081 [0.027, 0.142] |
| Reasoning tokens per instinct answer | 220, 236 | 410 | |
| Worked 90% intervals containing the answer | 85, 91 of 104 | 92 of 104 | |
| Worked answers above the estimate | 62%, 62% | 59% | |

- **The instinct score depends on the wording.** The second wording nearly halved it, far beyond test–retest (−0.001 [−0.020, 0.016]). It also nearly doubled the reasoning spent on instinct answers: "say what your gut tells you" restrains the model less than "Don't work it out, calculate or explain". Instinct scores are only comparable under the same wording and effort settings, and are best read as a secondary measure.
- **The worked score barely depends on it.** The second wording scored 0.010–0.016 better, an effect whose intervals just reach zero: perhaps real, and if so small, about twice the test–retest difference. Its worked prompt also says what calibration means, which may help a little.
- **The lean survives the change of wording.** True answers lay above the worked estimate 59% of the time (90% interval 51–67%).

## References

- Gneiting, T., and Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.
- Bracher, J., Ray, E. L., Gneiting, T., and Reich, N. G. (2021). Evaluating epidemic forecasts in an interval format. *PLOS Computational Biology*, 17(2), e1008618.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209–212.
