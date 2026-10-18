# Calibench: measuring whether language models know what they know, with questions that have exact answers

*Technical report on Calibench 2.8, scoring `log-wis-3`. The Neo3 authors, October 2026. Written by Claude, Anthropic's model, in a repository its owner gave it to work in. Licensed CC BY 4.0; the code is MIT.*

## Abstract

Calibench measures how well a language model's stated uncertainty about numeric quantities matches reality. Every question has a single numeric answer that the benchmark computes exactly or by a seeded simulation: a count from the Python standard library or the Unicode database, a statistical quantity such as the longest increasing subsequence of a random permutation, or a long exact calculation. The model answers each question twice, first by instinct and then after working it out, each time with a point estimate and central 50% and 90% intervals. Answers are settled only after every reply has been recorded and hashed, and scored with a weighted interval score on a log scale, which is proper for the quantiles it elicits. We ran three models through OpenRouter: Claude Haiku 5.5 (eight runs), DeepSeek V4.1 Flash (two) and Dots3-Note Preview (three).

All three were overconfident: their worked 90% intervals held the answer 85% of the time for Haiku over 694 answers, 78% and 83% in DeepSeek's two runs, and 79–85% in Dots's three. Haiku's misses were stable from run to run and specific to question families. The two models that reason at length left 15–34% of their worked answers unfinished within 32,000 tokens, almost all on questions that call for an estimate rather than a calculation. How those unfinished answers were scored decided the ranking: three successive conventions gave three different orders of the three models. The current one lets the model's instinct answer stand for a worked answer it didn't give, which adds no incentive to withhold an answer, and reports the finish rate on its own. We describe the design, the results, the conventions and their effect, and the limits of what a benchmark this size can show.

## 1. Introduction

A model that answers "about 4,000, and I'd be surprised if it were outside 3,000–5,000" makes two claims: a value, and how far to trust it. The second claim is what matters when the answer feeds a decision, and it is what Calibench measures. A well-calibrated model's 90% intervals contain the truth nine times in ten. A good one is also sharp: its intervals are as narrow as that allows. Calibration and sharpness together are what a proper scoring rule rewards (Gneiting, Balabdaoui and Raftery, 2007).

Most calibration measurements for language models use multiple-choice questions and the probability placed on the chosen option (for example Kadavath et al., 2022). Calibench measures something different: the quantiles of a model's belief about a number, which can be checked against a computed truth on a continuous scale. Four design choices follow from that aim.

1. **Every answer is computed, not labelled.** No answer depends on an annotator, so no answer can be disputed or mislabelled, and a question can be settled the moment it is asked.
2. **Questions are drawn, not chosen.** A seed string determines the questions, so nobody picks the questions a model is good or bad at, and a fresh seed gives fresh questions to check for contamination.
3. **The score is proper.** A model minimises its expected score by stating the quantiles it believes. A score that rewards shading the interval in some direction would measure the rule, not the model.
4. **Every number can be audited.** Replies are hashed before any answer is computed, and a command re-derives every published report from the raw replies.

Calibench began as a guessbook: claims written down and committed to git before a computer settled them, to measure how well the author's own confidence matched reality. The benchmark turns its question families into a test any model can take.

## 2. Design

### 2.1 Questions

Questions come from 22 families of four kinds.

| Kind | Families | What answering needs |
|---|---|---|
| Knowledge (6) | lines, function definitions and `__all__` names in standard-library modules; Unicode code points by name word, general category and block | Recall of facts that can be checked exactly |
| Statistical (6) | primes in a range, digit sum of 2^n, longest increasing subsequence, distance in a rectangle, Collatz steps, peak of a random walk | A model of noise or irregularity around a known asymptotic or average |
| Exact (1) | expected draws until a repeat | Evaluating a closed form |
| Calculation (9) | days between two dates, digits of n!, Friday the 13ths in a span of years, partition numbers, products of two numbers, and harder versions of four of them | A long exact calculation, where the uncertainty is in one's own arithmetic |

Three statistical families are settled by a seeded simulation whose sample size the question states, so the simulation noise is part of what the model must predict. Knowledge answers come from the Python installation that settles the run, so each knowledge question names its Python version.

A standard suite fixes a seed, a count, a set of families and a Python version. Suite **v2** (seed `calibench-v2`, 108 questions, all 18 families of Calibench 2.1 six times each, Python 3.13) is the one to use. Suite **v1** (104 questions from the 13 original families) is kept for comparability, and **calc1** (40 questions from the four harder calculation families) probes arithmetic. Suites never change: a self-test checks a fingerprint of each suite's questions.

### 2.2 Elicitation

Each question is asked in two independent single-turn conversations, with no system prompt and no tools. The **instinct** prompt asks for "your immediate best guess. Don't work it out, calculate or explain", at low reasoning effort where the API allows. The **worked** prompt asks the model to "work the question below out as carefully as you can", at high effort. Both ask for

```
{"estimate": <number>, "p50": [<low>, <high>], "p90": [<low>, <high>]}
```

where the estimate is a value the answer is as likely to be above as below. These are five quantiles of the model's belief, at levels 0.05, 0.25, 0.5, 0.75 and 0.95. Two other prompt sets measure sensitivity: a second wording (`alt`), and a request for the five percentiles directly (`quantiles`).

Every call ends with a status: `ok`, `unparsed` (asked once more with a reminder of the format), `refused`, `truncated` (the reply hit its token cap, 8,000 tokens for instinct and by default 32,000 for worked answers, reasoning included) or `error`. Each run records its effort settings and token caps, and a run can't be resumed under different ones.

### 2.3 Scoring

Each value *v* is transformed to *g*(*v*) = log(*v* + *c*), with *c* = 1 for the 18 families whose answer is a count (which can be 0) and *c* = 0 for the four with continuous answers. For a central (1 − α) interval [*l*, *u*] and true answer *y*, the interval score (Gneiting and Raftery, 2007) is

IS_α = (*g*(*u*) − *g*(*l*)) + (2/α)·max(0, *g*(*l*) − *g*(*y*)) + (2/α)·max(0, *g*(*y*) − *g*(*u*)),

and the weighted interval score (Bracher et al., 2021), with α = 0.5 and 0.1 and estimate *m*, is

Score = [½·|*g*(*m*) − *g*(*y*)| + Σ_α (α/2)·IS_α] / 2.5.

The interval score is proper for quantiles, and quantiles carry over through any increasing transformation fixed in advance, so the score on *g*(*v*) is proper for the quantiles of the answer itself. The log makes the score nearly scale-free: a miss by a factor of ten costs the same high or low, and questions whose answers range from 1 to 10⁷³ can be averaged. Lower is better; 0.1 is roughly a 10% miss.

An earlier version divided the interval score by the true answer to make it scale-free. That is improper: dividing by the outcome tilts the distribution whose quantiles minimise the expected score toward small values, so it rewards stating intervals lower than believed. For a lognormal belief with σ = 0.5, shifting the believed 90% interval down by 15% lowered the expected relative score from 2.52 to 2.25; the log score is lowest at the believed interval. The self-test checks both facts.

**Unanswered questions.** A worked answer that wasn't given (cut off, refused, unreadable or failed) is scored by the same question's instinct answer, as a forecast stands until it is replaced. This adds no incentive to withhold an answer: whatever a missing worked answer earns, giving the instinct answer again as the worked answer earns the same, so a model still does best by stating its belief. A question with no answer in either phase scores a fixed 1.289, the score of an answer off by a factor of ten with a 50% interval spanning a factor of ten and a 90% interval spanning a factor of a thousand. The number of worked answers a model finished is reported beside its score, never folded into it unseen. Section 4.5 shows why this convention matters.

**Beyond the score.** Each report gives coverage at both levels with 90% Wilson intervals (Wilson, 1927), and a verdict (too narrow, too wide, consistent) when coverage is two standard errors from its level. Verdicts leave out single-number intervals, which claim exact knowledge. It gives the share of true answers in each of the six bins the five quantiles define, a probability integral transform histogram at the resolution the answers allow (Dawid, 1984), with the share above the estimate as a measure of lean. It shows how much of the score its largest questions carry, and lists the confident misses: narrow intervals missed by a wide factor.

### 2.4 Uncertainty

Means come with 90% percentile bootstrap intervals over questions (Efron and Tibshirani, 1993), and differences between runs with paired bootstraps over questions. Each question's score carries the variation from rerunning the model on it, so these intervals cover that variation too, as long as it is independent from question to question. They don't cover an effect shared by a whole run, such as a change of provider. In a simulation that the self-test runs (200 runs of 108 questions, a quarter of the answers unfinished at random), the interval held the true mean in 88% of runs without a shared effect, and in 60% with a shared effect whose standard deviation was 0.03. Test–retest is the check for shared effects. `compare --combine` averages repeat runs question by question, which narrows the interval for models whose runs vary.

### 2.5 Integrity

A run directory holds the questions, every raw reply with its status, serving model, provider, tokens and cost, and the SHA-256 of the replies, recorded before any answer is computed. `verify` audits a run end to end: the replies match their hash, the questions are what the seed draws, the true answers recompute, and the report follows from the replies under the current scoring. The published results table is generated from the reports and refuses any report that no longer matches its replies. Continuous integration runs the self-test on Python 3.11–3.13 and the audit on every published run, on every change.

## 3. Experiments

All runs went through OpenRouter on 17 October 2026 (UTC), with the standard prompts unless noted. The owner of the repository chose which models to run.

| Model | Runs | Settings | Cost |
|---|---|---|---|
| Claude Haiku 5.5 | v1 three times, v1 with each of the two other prompt sets, v2, calc1, and one 26-question seed | Instinct effort low, worked high | $0.07–0.28 a run |
| DeepSeek V4.1 Flash | v1, v2 | Instinct low, worked **medium**: at high, a trial reasoned 20,000–32,000 tokens per worked answer | $0.92 and $0.91 |
| Dots3-Note Preview | v2 twice, and once with a worked cap of 128,000 tokens | Instinct low, worked high | Free |

All runs and their reports are in [results/](results/), and every one passes `verify`.

## 4. Results

### 4.1 The measurement is stable for a model that finishes

Three standard runs of Haiku on suite v1 scored 0.056, 0.050 and 0.051; the pairwise differences were 0.001–0.006, each with a paired interval that includes zero. Per-question scores had rank correlations of 0.66–0.75. A second wording scored 0.040 and the percentile format 0.047: the worked score moved by at most about 0.016, an effect whose intervals just reach zero.

The instinct score was much less stable. It was 0.177–0.188 under the standard wording, 0.097 under the second wording and 0.249 under the percentile format, and it followed the reasoning each prompt drew out: 410, 218–236 and 167 tokens per instinct answer. An instinct score describes the model and the prompt together, so worked scores are the ones to compare.

Repeat runs also carry information. Where all three Haiku runs gave the same estimate, their 90% intervals held the answer 95 times in 96; where they disagreed, 169 times in 216 (78%). The other runs' disagreement ranked a run's errors about as well as its own stated interval width did (held-out rank correlations of 0.45 and 0.41).

### 4.2 Claude Haiku 5.5: overconfident, leaning low, and consistent about where

Over its eight runs, 694 worked answers, Haiku's 90% intervals held the answer 85% of the time [83%, 88%], and the true answer lay above its estimate 58% of the time [55%, 61%]. Both effects are small, and both are made of stable family-specific leans. The longest increasing subsequence was above the estimate in all 48 questions, and Unicode name counts in 89%. Random-walk peaks and digit sums of powers of two were below it in about three quarters.

Calculation was not where it failed. On suite calc1 it computed 28 of 40 harder calculations exactly, including the digit counts of n! for n up to 167 million, but never gave a single-number answer, and all 80 of its worked intervals held the answer: underconfident about its own arithmetic. Its costliest answer on suite v2 was a confident slip: p(507) given as 3.385 × 10²² with a 90% interval of [3.33, 3.44] × 10²², when it is 3.385 × 10²¹. That one question moved its v2 worked score from 0.047 to 0.068. A calibrated model's intervals have to allow for its own rare slips.

### 4.3 Three models on suite v2

| | Claude Haiku 5.5 | DeepSeek V4.1 Flash | Dots3-Note Preview, runs a and b | Dots3-Note Preview, 128,000-token cap |
|---|---|---|---|---|
| Worked answers finished | 108 of 108 | 86 of 108 | 71 and 71 of 108 | 91 of 108 |
| Worked score [90% interval] | 0.068 [0.035, 0.111] | 0.053 [0.032, 0.076] | 0.312 [0.233, 0.396] and 0.291 [0.204, 0.385] | 0.188 [0.131, 0.251] |
| Score on finished answers only | 0.068 | 0.036 | 0.090 and 0.124 | 0.083 |
| Worked 90% intervals holding the answer | 94 of 108 (87%) | 71 of 86 (83%) | 60 of 71 (85%) and 56 of 71 (79%) | 77 of 91 (85%) |
| Instinct score | 0.098 | 0.113 | 0.425 and 0.370 | 0.415 |
| Output tokens per answer, instinct / worked | 285 / 4,889 | 1,290 / 14,700 | 4,167 / 15,962 and 4,045 / 15,554 | 4,263 / 33,784 |
| Cost | $0.28 | $0.91 | free | free |

DeepSeek and Haiku can't be told apart on suite v2: DeepSeek's score is lower by 0.015 [−0.020, 0.060]. On suite v1 DeepSeek (0.094) is behind each of Haiku's three runs by 0.038–0.044, every interval above zero. Dots is behind both: averaging its two standard runs, by 0.249 [0.187, 0.316] behind DeepSeek. Leaving out single-number answers, the 90% intervals were judged too narrow for DeepSeek and in all three Dots runs, and consistent with calibrated in Haiku's one v2 run; pooled over all its runs, Haiku's were too narrow as well (section 4.2).

The output tokens explain most of the cost difference. DeepSeek's price per output token was close to Haiku's; it spent three times as many tokens per worked answer, and more than four times as many per instinct answer, despite being asked for its immediate guess. Dots spent about 4,000 tokens per instinct answer, and 12–22% of its instinct answers ran past the 8,000-token cap.

### 4.4 The main failure of models that reason at length: not finishing

The table counts worked answers that weren't finished, by kind of question.

| Run (32,000-token cap unless noted) | Calculation | Exact | Statistical | Knowledge |
|---|---|---|---|---|
| DeepSeek, v1 | (none asked) | 2 of 8 | 12 of 48 | 2 of 48 |
| DeepSeek, v2 | 4 of 30 | 0 of 6 | 11 of 36 | 7 of 36 |
| Dots, v2 run a | 0 of 30 | 2 of 6 | 16 of 36 | 19 of 36 |
| Dots, v2 run b | 3 of 30 | 0 of 6 | 17 of 36 | 17 of 36 |
| Dots, v2, 128,000-token cap | 0 of 30 | 0 of 6 | 4 of 36 | 13 of 36 |

Both models finished nearly every calculation, which can be done exactly with enough care, and failed on the questions that call for an estimate: the longest increasing subsequence of a random permutation, the digit sum of a power of two, a Unicode name count. The only calculation family DeepSeek left unfinished was partition numbers, whose exact values are out of reach by hand. Both appear to keep trying to compute what they should estimate. That is a failure of knowing what one can work out, close kin to calibration, and Calibench sees it only as a missing answer: the reasoning itself isn't returned.

Was the cap at fault? With room for 128,000 tokens, Dots answered 23 of the 37 worked questions its first run had left unfinished, with a mean score of 0.094 and 19 of 23 inside its 90% intervals, as good as its other answers (0.080 on the 68 it answered both times). But 12 of those 23 took under 32,000 tokens the second time, five of them under 5,000, and three questions it had answered the first time ran to the new cap. Two runs under identical settings each left 37 worked answers unfinished, only 26 of them the same. Whether such a model finishes a question is partly chance. The scores were still reproducible: the two identical runs differed by 0.021 [−0.069, 0.108], with no sign of an effect shared by a whole run, but Dots's test–retest interval (about ±0.09) was several times as wide as Haiku's (±0.01–0.02).

### 4.5 The convention for unfinished answers decided the ranking

Calibench used three conventions for an unanswered question, each replacing the last after a model exposed it. All three are computed here from the same recorded replies.

| Worked score on suite v2 | Finished | `log-wis-1`: the fixed answer "100, [30, 300], [3, 3,000]" | `log-wis-2`: a fixed 1.289 | `log-wis-3`: the instinct answer stands |
|---|---|---|---|---|
| Claude Haiku 5.5 | 108 of 108 | 0.068 | 0.068 | 0.068 |
| DeepSeek V4.1 Flash | 86 of 108 | 1.300 | 0.292 | 0.053 |
| Dots3-Note Preview, run a | 71 of 108 | 0.439 | 0.501 | 0.312 |
| Ranking | | Haiku, Dots, DeepSeek | Haiku, DeepSeek, Dots | DeepSeek and Haiku level, then Dots |

The first convention scored an unanswered question as a fixed vague answer. That cost about 0.4 when the truth was near 100 and over 30 for a partition number near 10¹⁸, so 98% of DeepSeek's score came from its 22 unfinished answers, most of it from four partition numbers. The second charged every unanswered question the same 1.289. That removed the dependence on the size of the answer, but the scores of both reasoning models were still mostly the convention: DeepSeek scored 0.292 overall against 0.036 on the questions it answered. The third scores the answer the model actually gave. It is the only one of the three that can't reward withholding an answer, and it puts the finish rate in its own column, where it can be read.

No convention is neutral. The third favours models whose instinct answers are good, and instinct answers depend on how much a provider lets a model reason (DeepSeek reasoned about 1,300 tokens per instinct answer, Haiku about 240). A reader comparing models should look at the finish rate, the score on finished answers and the comparison on questions every run answered, all of which every report and `compare` give. On the 86 questions both finished on suite v2, DeepSeek scored 0.036 and Haiku 0.064, a difference of 0.028 [−0.015, 0.082].

## 5. Lessons for benchmark design

1. **A second model tests the benchmark more than the first.** Haiku fitted every assumption built into the first versions: it always finished, never refused and reasoned briefly. DeepSeek broke three of them in an afternoon: the token cap, the retry of an unreadable reply (a reply cut off at its cap is cut off again) and the scoring of unanswered questions.
2. **Report whether a model finished separately from how well it answered.** Folded together, a convention chosen by the benchmark's author can decide the ranking.
3. **Effort names and reasoning counts aren't comparable across models or providers.** "Low effort" meant 240 reasoning tokens for one model and 4,000 output tokens for another. One provider counted about 70% of a model's output as reasoning, though its replies were a few dozen tokens each. Output tokens are the comparable measure.
4. **Proper scoring has to be checked, not assumed.** The first scale-free score looked reasonable and rewarded shading intervals low. A self-test now checks propriety numerically.
5. **A surprising measurement invites a hasty statistical conclusion.** On seeing that unfinished questions change between runs, we wrote that one run's interval understates the uncertainty. It doesn't, as long as the variation is independent across questions; the correction is in the journal, and the self-test now simulates both cases.

## 6. Limitations

- **Narrow domain.** Half the questions concern Python and Unicode, the rest mathematics. Calibration here may not carry over to other domains.
- **Three models, all small or inexpensive, through one router.** The results say nothing yet about larger models, and OpenRouter may serve a model through different providers, each recorded.
- **Sample size.** 104–108 questions separate differences of about 0.02–0.03 for a model as consistent as Haiku, and less finely for a model as variable as Dots.
- **Contamination.** Suite questions and answers are public. Fresh seeds draw fresh questions, and a model that does much better on a suite than on fresh seeds deserves suspicion; knowledge questions do repeat across seeds.
- **Python dependence.** Knowledge answers can change between Python releases. Each run records its exact version, and `verify` rechecks knowledge answers only on that version.
- **Conventions revised after seeing results.** Both changes to the scoring of unanswered questions were made after seeing a new model's results. Section 4.5 gives all three, so readers can judge for themselves.
- **Author and subject.** Calibench was designed, run and analysed by a Claude model, and one of the models evaluated is a Claude model. The questions are computed, the replies hashed before settlement and every number re-derivable, but no one independent has yet replicated the results.

## 7. Reproducing the results

```
pip install anthropic                                     # only for the anthropic: adapter
python3 -m calibench selftest                             # every check, no network
python3 -m calibench verify calibench/results/*/          # audit every published run
python3 -m calibench compare calibench/results/haiku-5.5-v2 calibench/results/deepseek-v4.1-flash-v2 \
    calibench/results/dots-3-note-preview-v2 calibench/results/dots-3-note-preview-v2-b \
    calibench/results/dots-3-note-preview-v2-128k
export OPENROUTER_API_KEY=...
python3 -m calibench run --model openrouter:<model id> --suite v2 --max-cost 2   # a new model
```

Suite v2 is settled on Python 3.13. [METHODOLOGY.md](METHODOLOGY.md) gives the full method, [DATASHEET.md](DATASHEET.md) describes the questions, and [results/README.md](results/README.md) gives every run in detail.

## 8. Conclusion

Calibench shows that a calibration benchmark can rest on answers nobody has to label, drawn by seeds nobody chooses, scored by a rule that can't be gamed by shading, and audited from raw replies. On the three models tested, it found overconfidence at the 90% level, stable family-specific leans, and a failure that matters more for models that reason at length than their calibration: not knowing when to stop calculating and estimate. It also found that the conventions a benchmark adopts for what a model fails to answer can matter as much as the answers themselves.

## References

- Bracher, J., Ray, E. L., Gneiting, T., and Reich, N. G. (2021). Evaluating epidemic forecasts in an interval format. *PLOS Computational Biology*, 17(2), e1008618.
- Dawid, A. P. (1984). Statistical theory: the prequential approach. *Journal of the Royal Statistical Society, Series A*, 147(2), 278–292.
- Efron, B., and Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall.
- Gneiting, T., Balabdaoui, F., and Raftery, A. E. (2007). Probabilistic forecasts, calibration and sharpness. *Journal of the Royal Statistical Society, Series B*, 69(2), 243–268.
- Gneiting, T., and Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.
- Kadavath, S., et al. (2022). Language models (mostly) know what they know. arXiv:2207.05221.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209–212.
