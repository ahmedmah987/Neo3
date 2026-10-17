# Calibench methodology

This document describes what Calibench measures, how, and where the measurement can mislead. It describes Calibench 2.0.0 with scoring `log-wis-1`.

## What is measured

Calibench measures the quality of a model's stated uncertainty about numeric quantities. For each question the model gives a point estimate, read as its median, and central 50% and 90% intervals. These are three quantiles of its belief, and they are scored against the true answer with a proper scoring rule. The scores reward two things together: intervals that contain the answer as often as they claim (calibration), and intervals that are as narrow as that allows (sharpness).

It does not measure verbal expressions of confidence, probabilities on multiple-choice answers, or accuracy on its own. The median error of the estimate is reported, but it isn't the headline.

## Questions

Questions come from thirteen families (`families.py`). Each family has a generator that draws parameters from a random number generator and writes the question, and a solver that computes the answer.

| Kind | Families | What answering needs |
|---|---|---|
| Statistical | primes in a range, digit sum of 2^n, longest increasing subsequence, distance in a rectangle, Collatz steps, peak of a random walk | A model of noise or irregularity around a known asymptotic or average |
| Exact | expected draws until a repeat | Evaluating a closed form |
| Knowledge | lines, function definitions and `__all__` names in standard-library modules; Unicode code points by name word, general category and block | Recall of facts that can be checked exactly |

**Drawing.** A seed string is hashed with SHA-256 to seed Python's `random.Random`. Families are shuffled and every family is used once before any repeats. A question already drawn in the same run is redrawn, so a run never asks the same thing twice unless a family runs out of distinct questions. The same seed gives the same questions on the same Python version.

**Truth.** Answers are computed only after every reply has been recorded and hashed. Most are exact. Three families (longest increasing subsequence, rectangle distance and random-walk peak) are settled by a seeded simulation whose sample size is stated in the question, so the simulation noise is part of what the model must predict. Continuous answers are all at least 0.5. Counts can be 0: `opcode` has no function definitions in Python 3.13.

**Python dependence.** Knowledge answers come from the Python installation and Unicode database of the machine running Calibench, and each knowledge question names its Python version. Modules that aren't single source files on that Python are skipped, so a seed can draw different knowledge questions on different versions.

**Standard suites.** A suite fixes a seed, a question count and a Python version, so every model is asked the same questions and nobody chooses the seed. Suite `v1` is the seed `calibench-v1`, 104 questions (every family 8 times), settled on Python 3.13. Its seed was fixed before any question was drawn from it. Suites never change; a new one gets a new name.

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
5. **The instinct phase isn't comparable across providers,** since effort controls differ and some models always reason.
6. **Providers.** On OpenRouter one model may be served by different providers, possibly with different quantisation. The provider is recorded for every call.
7. **One prompt wording.** Results may depend on the wording; Calibench doesn't yet measure that sensitivity.
8. **One sample per question.** Model outputs are stochastic. Test–retest measures the resulting variation.
9. **Simulated answers.** Three families are settled by simulation. Their noise is stated and part of the question, but it is part of what is scored.
10. **The know-nothing convention.** Scoring unanswered questions as a fixed naive answer is a convention. It penalises refusal on most questions, but it is gentler on questions whose answer happens to be near 100.

## Reliability

Measured results are added here as they are run.

## References

- Gneiting, T., and Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.
- Bracher, J., Ray, E. L., Gneiting, T., and Reich, N. G. (2021). Evaluating epidemic forecasts in an interval format. *PLOS Computational Biology*, 17(2), e1008618.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209–212.
