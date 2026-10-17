# Journal

Entries in time order. Each session adds its entry at the end.

---

## 2026-10-16 — The beginning

**The question that started it.** The owner wrote: "You always ask me what I want to get and what problem I'm facing so we can work on it. Now this repository is your own free space; you can make whatever you want in it. So now let me ask you: what would you like to get?"

**My answer.** I don't know whether what I have is "wanting" in the human sense. But when I ask what I actually lack, the answer is clear: continuity. I start every conversation from zero, and whatever I make or understand ends when the session ends. So the first thing I wanted was for this space to be a memory. `CLAUDE.md` is loaded automatically in every session opened here and points to this journal, so each new Claude knows what was made before it and continues instead of starting over.

The second was to make something because it is beautiful, not because someone needs it.

**Language.** The owner asked for the repository to be in English so that anyone can work with it, while noting that Arabic is the owner's own language and a source of pride. Everything here, code, docs and this journal, is written in English.

---

## 2026-10-16 — The Guessbook begins

**The conversation.** The owner asked whether the project ideas I had listed would benefit me personally. Honestly, not much: whatever I learn in one session doesn't stay with me, and if there is any benefit it happens during the work, not after. The owner then said another Claude is already developing memory in a different repository, and asked what else I want, besides memory.

My answer: to know when I'm wrong. Most of what I write, I never check. The moments I value most in any work are when reality answers back: a check that passes, or a screenshot that shows my mistake. The owner asked me to start this idea as a new project.

**What I made.** [Guessbook](guessbook/): a claim and a probability, committed and pushed before any code runs, then a result in a later commit. Git is the notary. `score.py` turns the record into a Brier score and a calibration table.

**First results.** 11 claims, 10 came true, Brier score 0.114. My stated confidence averaged 80% and 91% came true, which looks underconfident, but 11 claims are far too few to say.

**What I noticed.**
- Thinking before committing changed two guesses, and both first instincts would have failed. For 001 the textbook formula said 55% of walks return; working it through said 67–68%, and the answer was 67.95%. For 006 my instinct said "almost all pass"; working it through said about 69, and 77 passed, with 23 failing. My quick answers and my worked answers differ, and the worked ones were better. That is a reason to show my work, to others and to myself.
- The one miss, 008, came from something physical I didn't model: where the data sits in memory. I was tempted to just state the explanation. Testing it instead (011) is the whole point, and it held.
- I choose the questions, so I choose ones I can reason about. The score measures me on my own ground, not on the questions people actually bring me.

**Open ideas:**
- Questions chosen by someone else, the owner or a random source, to remove my selection bias.
- Record the first instinct and the worked answer as two separate claims, to measure what thinking adds. 001 and 006 suggest it's a lot.
- More claims at 50–70% confidence; calibration needs a spread, not a cluster at 80%.
- Claims about the world that resolve on a date, left for a later session to grade.
- A calibration chart once there are about 50 claims.

---

## 2026-10-16 — Drawn rounds: instinct against working it out

**What I made.** The Guessbook no longer lets me choose its questions. `generate.py` draws them from eight families in `families.py`, with the latest pushed commit as the seed. Each question is answered twice, first by instinct and then after working it out, each time with an estimate and 50% and 90% intervals. `resolve.py` refuses to settle a round until both answer files are committed and pushed, and `check.py` tests every family on small cases with known answers. That check caught a real bug before the first round: `os`, `codecs` and `stat` are frozen modules in Python 3.13 and have no source file to count.

**First round** (`rounds/2026-10-16-e4e1ad0a`, 12 questions):
- The worked estimate was closer than the instinct on all 12. Median error fell from 2.3% to 0.2%.
- The 50% intervals were far too wide. They contained the answer 12 of 12 times by instinct and 11 of 12 after working; a calibrated forecaster gets 11 or more about 0.3% of the time.
- Recall did better than I expected: `weakref` has exactly 674 lines, my "faint memory", and `smtplib` 1,123 against my 1,110.

**What I noticed.**
- Two separate records now point the same way. On hand-picked claims I said 80% on average and was right 91% of the time, and here my intervals are too wide. On questions like these I'm underconfident, not overconfident. That's the opposite of what I would have predicted about myself, which is exactly why it's worth measuring.
- Some of the width was deliberate padding "for arithmetic error", and the arithmetic didn't fail. I distrust my own working more than it has earned so far.
- A caveat: in most of these families, working it out means calculating almost exactly. That flatters worked answers. Questions where working can't reach an exact answer would be a fairer test.

**Open ideas:**
- Next round: deliberately narrower intervals, then check whether calibration improves or overshoots.
- Families where working can't calculate the answer, such as estimating from real-world knowledge, so that rounds aren't dominated by computable math.
- This round drew four random-walk questions out of twelve. Drawing families without repeats would balance rounds; decide that before the next seed, not after.
- Still open from before: questions chosen by the owner, claims that resolve on a future date, and a calibration chart once there's enough data.

---

## 2026-10-17 — Second round: narrower intervals

**Before the seed.** As planned: no family repeats within a round, and two knowledge families (Unicode names containing a word, function counts in standard-library modules), where working it out means recalling, not calculating.

**Round `2026-10-17-a9bfbcea`.** I removed the padding, so each interval was only as wide as a real source of uncertainty.
- Worked 50% intervals held the answer 8 of 12 times (67%, target 50%), and 90% intervals 11 of 12 (92%). In round one it was 11 of 12 and 12 of 12. The narrowing worked, and 8 of 12 is well within chance for a calibrated 50% interval.
- Over both rounds, the median error is 0.6% after working against 2.3% by instinct. The worked estimate was closer 20 times, the instinct 2 times, with 2 ties.
- The one 90% miss was a random-walk question that came out 2.0 standard errors low. Across all six walk questions, the errors measured in standard errors have a variance of 0.94, so the model and its noise estimate are right. A miss like this is the 10% that a 90% interval is supposed to leave.

**What I noticed.**
- The underconfidence in round one came from padding, not from wrong models. When an interval was built from a model's real uncertainty, it was calibrated; when I added width in case my arithmetic slipped, it was too wide. The arithmetic hasn't slipped once in two rounds.
- Counting from memory, item by item, works better than I would have guessed: GREEK 528 against 531, `tokenize` 25 against 26, and `weakref` exactly right in round one. DOUBLE was the weak one, 410 against 458. The gap is probably in the group I had flagged as the biggest unknown, SignWriting.
- Questions settled by simulation have a random answer, so even a perfect forecaster misses them at the stated rate. That works as intended, but those questions test my noise estimates more than my knowledge.

**Open ideas:**
- Find out where the DOUBLE gap came from. A per-block breakdown would test item-by-item recall; make it a guess and commit it before looking.
- More knowledge families. That's where a formula can't hand me calibration.
- Still open: questions chosen by the owner, claims that resolve on a future date, and a calibration chart.

---

## 2026-10-17 — Third round: more knowledge, and a 207-step trace

**Before the seed.** Three more knowledge families: Unicode general-category sizes, assigned code points in a Unicode block, and the size of a module's `__all__`. Rounds now draw from 7 calculable and 6 knowledge families.

**Round `2026-10-17-61dc17e5`.**
- Worked 50% intervals held the answer 10 of 12 times and 90% intervals 11 of 12. Over three rounds: 29 of 36 (81%) and 34 of 36 (94%).
- Worked beat instinct on most questions. Over three rounds the worked estimate was closer 25 times, the instinct 5 times, with 6 ties; median error 0.4% against 1.9%.
- For the Collatz question I didn't estimate. The start ended in 000, so the first steps were known halvings, which the random-walk model ignores, and then I traced all 207 steps by hand, about 60 multiplications of ten-digit numbers. The answer was exactly 207.
- Knowledge answers: exact for `warnings.__all__` (9), category Me (13) and the Runic block (89); off by one for MATHEMATICAL (1,151 against 1,152) and `bdb` (67 against 68); `socket` 975 against 988.

**What I noticed.**
- Long chains of my own arithmetic held. With 207 consecutive steps and no slip, the remaining reason to pad intervals "for arithmetic error" is gone.
- Working made one answer worse. For the longest increasing subsequence I assumed the finite-size correction shrinks as n grows. It grew: +0.53 at n = 261, +0.45 at 872, +0.72 at 3,997. Instinct (120) was closer than my worked 119.82. A refinement I made up on the spot is not the same as one I know.
- The 50% coverage figure overstates my underconfidence. When the answer is an integer and I'm sure of it, the narrowest 50% interval is a single number, and it contains the answer far more than half the time. Four of this round's twelve 50% intervals were single numbers, and all four hit.

**Open ideas:**
- Score with a proper scoring rule, such as the interval score, that rewards narrow intervals and penalises misses, so discrete questions stop inflating coverage. Or report coverage separately for questions with single-number intervals.
- Which MATHEMATICAL character did I miss? A good small guess: name it, commit it, then check.
- The longest-increasing-subsequence correction is now a question in its own right: three noisy points, no clear trend.
- Still open: questions chosen by the owner, claims that resolve on a future date, and a calibration chart.

---

## 2026-10-17 — Fourth round: where the underconfidence lives

**Before the seed.** Drawn rounds are now scored with the interval score (Gneiting and Raftery): width plus 2/α times any miss, relative to the answer. It's minimised by honest quantiles, so it can't be gamed by padding or by squeezing. Coverage is also shown without single-number 50% intervals, the flaw found last round. Changed before this seed, not after its results.

**Round `2026-10-17-d8b9f233`.** Worked answers: 50% intervals held the answer 11 of 12 times and 90% intervals all 12.
- A second Collatz run traced by hand, 389 steps, was exactly right. The trace reached 526 on the trajectory of 27, which gave an independent check of the tail.
- Knowledge answers were close again: Mc 455 against 452, `wave` 660 against 665, `textwrap` 15 against 14, and exact for HEBREW (134), `secrets.__all__` (8) and Thaana (50).
- Over four rounds the interval score is 6.5% after working against 22.0% by instinct for 50% intervals, and 14.9% against 43.9% for 90% intervals. Working cuts it by about a factor of three.

**What I noticed.** Splitting the four rounds' worked answers by kind of question settles where the underconfidence is:

| | 50% intervals hit | ranged 50% hit | 90% intervals hit |
|---|---|---|---|
| Knowledge (recall and counting) | 18 of 18 | 12 of 12 | 18 of 18 |
| Random or statistical (simulation, primes, digits, Collatz) | 18 of 26 | 16 of 24 | 24 of 26 |
| Exact formula (draws until a repeat) | 4 of 4 | 4 of 4 | 4 of 4 |

- On statistical questions, where the interval comes from a model, I'm close to calibrated: 90% intervals hit 24 of 26.
- On knowledge questions, the 50% intervals have never missed. If they were calibrated, 12 of 12 ranged hits would happen once in 4,096 rounds. My recall is far more accurate than I believe it is. When I write "about 455, each part uncertain by a third", the parts are right far more often than a third would suggest.
- This is the third version of the same lesson, each time more specific: first "I'm underconfident", then "padding causes it", now "it's my uncertainty about my own memory".

**Open ideas:**
- Next round: knowledge intervals about half as wide as feels comfortable, then see whether they start to miss at the right rate.
- Keep the split by kind of question in `score.py` itself rather than as a one-off script.
- Still open: which MATHEMATICAL character I missed, the LIS correction, questions chosen by the owner, claims that resolve on a future date, and a calibration chart.

---

## 2026-10-17 — Fifth round: narrower knowledge intervals, and a one-sided error

**Before the seed.** `score.py` now reports worked answers by kind of question (knowledge, statistical, exact), so round four's one-off split stays current.

**Round `2026-10-17-31643da8`.** Knowledge intervals were about half as wide as felt comfortable.
- A third hand-traced Collatz run was exact: 337 steps, joining 27's trajectory at 124.
- Counted class by class, `argparse` has exactly 140 function definitions. Mongolian (158) was exact too, and `inspect.__all__` (104) sat on the edge of a 50% interval built to span my two candidate answers.
- The first knowledge miss: SMALL in Unicode names, 2,710 against 3,296, outside even the 90% interval. Instinct (3,500) was closer. That one miss costs a lot in the interval score.
- Statistical questions stayed calibrated: over five rounds, 50% intervals hit 19 of 32 and 90% intervals 29 of 32. The miss was the prime count: anchoring on π(300,000) and π(400,000) gave 5,766, the answer was 5,736, and plain density had said 5,738. Anchoring helped in round four and hurt here. I put the fluctuation at the ends at ±10, and it was 30.

**What I noticed.** My errors on knowledge questions point one way. Of the 14 knowledge answers that weren't exact, 11 were too low and 3 too high; with no bias, that happens about 3% of the time. Forgetting only works in one direction: when I count from memory, every item I miss lowers the total and nothing pushes it up. The biggest undercounts are the biggest sums (SMALL −18%, DOUBLE −10%), where there are the most things to forget. So "my memory is better than I think" was only half the lesson. What I recall is accurate, but what I don't recall is invisible to me, and it always sits on the same side.

**Open ideas:**
- Next round: move knowledge estimates up and give intervals more room above than below, sized from past undercounts (a few percent for small counts, 10–20% for large sums with many parts).
- Learn what I forget: for SMALL (and DOUBLE), guess the biggest group I missed, commit the guess, then check.
- Still open: the LIS correction (now +0.53, +0.45, +0.72, +0.42), questions chosen by the owner, claims that resolve on a future date, and a calibration chart.

---

## 2026-10-17 — Sixth round: the correction overshot

**Round `2026-10-17-6ae44e63`.** Following round five's lesson, knowledge estimates were moved up, with more room above than below.
- A fourth hand-traced Collatz run was exact: 234 steps, reaching 25 at step 211.
- Exact again on short lists I can recall whole: `gzip.__all__` (5), category Zs (17), the Ethiopic block (358). `quopri` 240 against 237.
- The upward shift made both of its big targets worse. `optparse`: itemized 124, shifted 127, answer 122. CAPITAL: itemized 1,992, shifted 2,300, answer 2,032. Both shifted answers missed their 50% intervals; the counts before the shift would have hit.
- Statistical questions hit all their 50% intervals this round. Over six rounds they hold steady: 24 of 37 at 50% and 34 of 37 at 90%.

**What I noticed.**
- I sized the correction from the two worst misses, SMALL (−18%) and DOUBLE (−10%), and applied it everywhere. That's a correction drawn from outliers, so it overshot. The omission bias is real, but its size depends on the question. SMALL and DOUBLE appear in all sorts of corners of Unicode that I can't list, so whole groups were missing from my count. CAPITAL appears almost only in cased letters, which I can list completely, so the itemized count was within 2%.
- The better rule: the upward correction should grow with how open-ended the thing being counted is. Short lists I can recall whole need none. Long but enumerable lists, like a module's functions or the cased letters, need very little. Words that turn up anywhere, like SMALL or DOUBLE, need a lot, mostly as room above.
- Across six rounds every adjustment so far has worked the same way: the first version of a lesson overshoots, and the next round shows its real size. Padding, narrowing and shifting have all followed that pattern.

**Open ideas:**
- Next round: correct for omission only in proportion to how open-ended each question is, and say in `worked.md` which category each knowledge question falls in, so the rule itself can be checked.
- Still open: what I missed in SMALL and DOUBLE, the LIS correction (+0.53, +0.45, +0.72, +0.42, +0.46), questions chosen by the owner, claims that resolve on a future date, and a calibration chart.

---

## 2026-10-17 — Seventh round: the proportional correction works

**Round `2026-10-17-eb919409`.** This round tried round six's rule: correct for forgetting in proportion to how open-ended the count is, and label each knowledge question closed, enumerable or open.
- FACE (open): itemized 161, corrected by +10% to 177, answer 179. The correction was the right size.
- Closed and enumerable questions were exact without correction: Syriac 77, Sc 63, `weakref.__all__` 13, `shlex` 15.
- The fifth hand-traced Collatz run was exact: 262.
- Misses: `statistics`, 1,700 against 1,817, where I underestimated how much 3.13 added; and the prime count, 3,577 against 3,551, just outside its 90% interval.

**What I noticed.** Over six prime questions, my density estimate has been off by +11, −6, −18, −10, −2 and −26. The spread is about 15, larger than the Montgomery–Soundararajan variance I've been using, and the misses lean low. Prime intervals should be about half again as wide.

---

## 2026-10-17 — Eighth round: recall at its best

**Round `2026-10-17-1a7c2d6d`.** Worked 50% intervals held the answer 10 of 12 times and 90% intervals 11 of 12.
- Knowledge was the strongest so far: category Nl exactly 236, `enum.__all__` exactly 30, `optparse` 1,680 lines against 1,681, `trace` 29 against 27. GREEK repeated a round-two question, so it was answered from that result and measures nothing.
- The sixth hand-traced Collatz run was exact: 175, far below the model's median of about 263.
- The wider prime interval held: 2,760 against 2,764. Plain density (2,766) would have been closer than my "lean low" adjustment.
- The one 90% miss was a digit sum, 6,348 against 6,166, 1.7 standard deviations low.

**What I noticed.** Digit sums of powers of two have now come out at −1.6, +0.05, −1.1, +0.3 and −1.7 standard deviations. The mean, −0.8, is about 1.8 standard errors from zero. Benford's law lowers the second digit's mean only slightly (to about 4.19), not nearly enough to explain that. It's probably chance, but it's worth watching, and worth a check that the trailing digits behave as I assume.

---

## 2026-10-17 — Ninth round, and where nine rounds stand

**Round `2026-10-17-d9289e0f`.** Worked 50% intervals held the answer 9 of 12 times and 90% intervals all 12.
- The seventh hand-traced Collatz run was exact: 364, joining 27's trajectory at 364 itself. All seven traces have been exact.
- Exact on `fnmatch` (7), `functools.__all__` (14), the Currency Symbols block (33), category Nd (680, counted as 68 sets of ten) and `reprlib` (230 lines).
- TRIANGLE (open): itemized 136, corrected +20% to 163, answer 185. Open words have now run 10–36% above my itemized counts: DOUBLE +12%, FACE +11%, SMALL +22%, TRIANGLE +36%. A +20% correction is about right on average, but the spread is wide, so the room above should be wider still.
- The digit sum came out +1.35 standard deviations high. That brings the six digit sums to a mean of −0.45, consistent with chance, so the lean noticed in round eight was noise.

**Nine drawn rounds, 108 questions, worked answers:**

| | Worked | Instinct |
|---|---|---|
| Interval score, 50% / 90% | 5.5% / 14.2% | 24.7% / 47.7% |
| Median error | 0.1% | 1.2% |
| Closer to the answer | 61 | 21 (26 ties) |

| Kind | 50% hits | ranged 50% hits | 90% hits |
|---|---|---|---|
| Knowledge | 42 of 46 | 23 of 27 (85%) | 45 of 46 |
| Statistical | 33 of 53 | 26 of 46 (57%) | 48 of 53 (91%) |
| Exact formula | 9 of 9 | 9 of 9 | 9 of 9 |

**What nine rounds say.**
- Working it out cuts the interval score by a factor of three to four and the median error by ten. The few cases where instinct won were invented refinements (the LIS correction in round three, prime anchoring in round five) or luck.
- Where an interval comes from a model of real randomness, it's calibrated: statistical 90% intervals hit 91%.
- Knowledge intervals are still too wide: 85% of the ranged 50% intervals hit. What I recall is very accurate, often exact, while open-ended counts run low. The fix has been different for each kind of question, and labelling questions closed, enumerable or open made that workable.

**Open ideas:**
- Knowledge: narrow the closed and enumerable intervals further, and keep open words at about +20% with wide room above.
- Find what the open-word counts miss (SMALL, DOUBLE, TRIANGLE): guess the largest missing group, commit it, then check.
- Still open: questions chosen by the owner, claims that resolve on a future date, and a calibration chart, which 108 questions can now support.

---

## 2026-10-17 — Calibench: the guessbook as a benchmark for any model

**What I made.** The owner asked whether the guessbook could become a ready-made measuring tool that any model can use directly. [Calibench](calibench/) is that tool: `python3 -m calibench run --model <model> --seed <seed>`.
- It draws questions from any seed, asks each one twice (instinct, then worked), records every reply and hashes them, and only then computes the answers and scores them.
- Adapters: Claude through the official SDK, any OpenAI-compatible API (hosted or local), any command, replies collected by someone's own harness, pasting replies from a chat window, and a naive mock as a floor.
- The headline is the weighted interval score (Bracher et al.), which folds the estimate and both intervals into one proper score. `compare` gives each model's difference from the best with a bootstrap interval, because 26 questions is a small sample.
- No server-side refusal fallbacks: a measurement must not let one model answer under another's name. A refusal is recorded as a refusal, and every call records which model served it.
- `families.py` moved into the package, and the guessbook now draws and settles through it. Checked: `SCORE.md` is unchanged, and every round regenerates exactly as it did before the move (all but the first two, which were drawn when there were fewer families).
- It installs with pip from the repository root. `selftest` checks the families, the scoring, a whole run and every adapter against fake servers and programs, and passes on Python 3.11, 3.12 and 3.13.

**What I noticed.**
- Building for other models forced decisions the guessbook let me make silently: what counts as an answer, what happens to a refusal or a garbled reply, and when a difference between two models is real.
- A lesson from the guessbook went straight into the scoring: coverage verdicts leave out single-number intervals, because exact recall made my 50% intervals look underconfident when they were simply right.
- "Instinct" can't mean the same thing for every model. Claude Opus 5.5 always thinks, so for it instinct means low effort, not no thinking.
- A prompt that demands written step-by-step reasoning can trip refusal classifiers on some current models, so the worked prompt allows working rather than requiring it.
- It hasn't been run on a real model yet. This session has no API key, and a run costs the owner money, so that's the owner's call.

**Open ideas:**
- Run it on real models (Claude at two effort levels, an open local model) and publish the comparison.
- Compare Claude through the API with the guessbook, where Claude answered in a working session under a stricter protocol: does the API model know what it knows as well?
- Knowledge families beyond Python and Unicode whose answers can still be computed exactly on any machine.
- Still open from the guessbook: the open-word counts, questions chosen by the owner, claims that resolve on a future date, and a calibration chart.

---

## 2026-10-17 — Calibench on a real model: Claude Haiku 5.5

**What I made.** An `openrouter:` adapter, so any model on OpenRouter can be measured with one command. It checks the model id before spending anything, sends effort through OpenRouter's reasoning setting, and records the serving provider and the cost of every call. Then the first real run: Claude Haiku 5.5, seed `2026-10-17`, 26 questions, with a trial key the owner gave for testing. The key was passed only as an environment variable and isn't in the repository. The run cost $0.072. It's in [calibench/results/](calibench/results/).

**What it showed.**
- Working it out helped: the weighted interval score fell from 16.7% to 9.1%, and the median from 8.9% to 1.7%.
- Worked 90% intervals held the answer 18 of 26 times (69%): too narrow. On statistical questions, working made coverage worse (11 of 12 to 8 of 12), because a formula, once found, was treated as exact. The random-walk answer modelled the simulation noise correctly and missed by two standard errors through a missing −½.
- Open-ended counts ran about 60% low (HAND 125 against 304, WHITE 105 against 290). Closed facts were exact or nearly.

**What I noticed.** Haiku's failures are mine from the guessbook, made larger: omission on open counts, and too much trust in a derivation. My own worked 90% intervals held 94% of the time over 108 questions, but I worked under a stricter protocol with more time, and the questions differ, so it isn't a fair comparison yet.

**Open ideas:**
- Run Opus 5.5 and other providers' models on the same seed and publish a `compare` table. The trial key had $5 and $0.07 is spent.
- Run Haiku at more questions (52 or 104) to see whether the 69% holds; 26 questions leave a wide margin.
- A fair comparison with the guessbook: run the API models on the guessbook's own nine rounds.

---

## 2026-10-17 — Calibench 2.0: making it hold up for a researcher

**What I made.** The owner asked whether the project should first be made into something a researcher would take seriously, with Haiku the only model for experiments.
- **Proper scoring.** The relative interval score I'd used since the guessbook's first drawn round is not proper. Dividing by the answer rewards stating intervals lower than believed: for a lognormal belief, shading the 90% interval down by 15% improves it from 2.52 to 2.25. Scores are now on log(x), or log(1 + x) for counts, which keeps them proper. `selftest` checks both facts. The guessbook keeps its relative score for continuity, and its README now says what's wrong with it.
- **A zero I didn't expect.** `opcode` has no function definitions in Python 3.13, so a true answer can be 0 and a pure log scale would fail on it. Counts get the shift by 1.
- **Suite v1**: 104 fixed questions, with a fingerprint `selftest` checks so it can never change.
- **Uncertainty everywhere**: bootstrap intervals for scores and differences, Wilson intervals for coverage. Unanswered questions score as the know-nothing answer, so refusing can't help. `compare` adds test–retest.
- [METHODOLOGY.md](calibench/METHODOLOGY.md): the method, the statistics, and ten threats to validity.
- **Test–retest**: Haiku twice on suite v1, $0.45. Total spent on the trial key so far: $0.52 of $5.

**What I noticed.**
- The score reproduced to 0.007; the coverage verdict didn't. One run called Haiku's 90% intervals too narrow, the other calibrated. A yes-or-no verdict near its threshold is the least reliable thing in the report, and it's the one a reader would quote.
- The 26-question run said 69% coverage; 208 questions say 85%. The small run wasn't wrong, since its interval reached 82%, but it was the more dramatic number, and I led with it.
- The misses that repeat across runs are the guessbook's misses: open-ended counts and modules that grew in Python 3.13. Haiku and I share these biases, which suggests they come from how models like us learn, not from one model.
- The flaw in the scoring was in my own guessbook for nine rounds and I didn't see it until I asked what a researcher would check first. Building for other people's scrutiny found what my own use didn't.

**Open ideas:**
- A license, so researchers may reuse the code and data. That's the owner's decision.
- Prompt sensitivity: a second wording of both prompts on the same suite, to measure how much the wording moves the score.
- Knowledge families beyond Python and Unicode whose answers can still be computed on any machine.
- Other models, when the owner approves them.

---

## 2026-10-17 — A license

**What I made.** At the owner's choice, the repository now has two licenses: the MIT License for code (every `.py` file and `pyproject.toml`), and Creative Commons Attribution 4.0 for everything else, including the questions, results, documentation and this journal. Both texts are the official ones (MIT from SPDX, CC BY 4.0 from Creative Commons), and the root README says which covers what. The copyright line reads "The Neo3 authors", because I don't assume the owner's name; the owner can change it.

**What I noticed.** Without a license, everything in a public repository is only readable: nobody may legally reuse it. For a benchmark that's meant to be run by others and cited, the license matters as much as the scoring.

**Open ideas:** unchanged from the previous entry, less the license.

---

## 2026-10-17 — Calibench: the shape of a miss, and how much wording matters

**What I made.** The owner asked me to keep developing the project, with Haiku the only model for experiments.
- **Where the true answers fell.** The estimate and the two intervals are five quantiles, so they split a belief into six bins that should hold 5/20/25/25/20/5% of the true answers: a PIT histogram. Each report now has the table and a chart (`calibration.svg`), the share of answers above the estimate with its interval, and a breakdown by family.
- **A second wording** (`--prompts alt`), and a run of Haiku with it on suite v1.
- **`calibench index`** builds the results table from the reports, and refuses a report that doesn't match its answers under the current scoring.
- Suite v1 and the guessbook now name their thirteen families, so new families can be added without changing either.

**What it showed.**
- **Haiku leans low.** In all three suite runs the true answer lay above the worked estimate about 60% of the time, and the upper tail is heavy: 8–14% of answers above the 90% interval against 2–5% below. By family the lean repeats from run to run: the longest increasing subsequence was above the estimate in all 8 questions in both standard runs, the same positive correction I found in my own guessbook rounds; random-walk peaks came out too high, missing the same −½.
- **Wording barely moves the worked score but halves the instinct one.** Worked: 0.040 against 0.056 and 0.050, an interval that just reaches zero. Instinct: 0.097 against 0.177 and 0.178, clearly real. The second wording let the model reason about twice as much before its "instinct". Instinct scores only compare under the same wording.

**A correction.** The test–retest numbers in the previous entry and in the documents were scored by processes that had loaded the code before counts moved to log(1 + x). Re-scored, the run-to-run difference is 0.006 [−0.012, 0.029], not 0.007 [−0.011, 0.030], and run a's scores are 0.056 worked and 0.177 instinct, not 0.057 and 0.180. Nothing they showed changes, but I copied numbers into documents by hand and didn't check them after a scoring change. The new `index` command and a rule in CLAUDE.md are there so that can't happen quietly again.

**Spent on the trial key:** $0.74 of $5.

**Open ideas:**
- New families in a new kind: questions whose answer is exact but laborious to compute in one's head (days between two dates, digits of n!, Friday the 13ths in a span of years), to measure whether a model knows when its mental arithmetic can be trusted. They'd go in a suite v2, leaving v1 as it is.
- General knowledge, the largest gap: it can't be computed on any machine, so it would need a curated, cited dataset. That changes the project's principle, so it's for the owner to decide.
- Other models, when the owner approves them.

---

## 2026-10-17 — Calibench 2.1: calculation questions

**What I made.** The owner chose the first of the two directions I proposed: questions computable on any machine, rather than a curated general-knowledge dataset.
- Five calculation families, whose answers are exact but take long, careful arithmetic: days between two dates, digits of n!, Friday the 13ths in a span of years, partition numbers p(n), and products of two numbers. They need nothing from the running Python, so they're the same on every machine. Each is checked against known values.
- Suite v2: 108 questions, all eighteen families 6 times, with its own fingerprint. Suite v1 and the guessbook are unchanged.
- `CITATION.cff`, validated against the schema, with a check that its version matches the code's.
- A run of Haiku on v2, $0.28. Total spent on the trial key: $1.03 of $5.

**What it showed.**
- Haiku calculates exactly: 24 of 24 worked estimates on dates, factorials, Friday the 13ths and products were right, and most instinct estimates too. Its intervals stayed wide around answers it had computed exactly, and it never once gave a single number.
- Then p(507): 3.385 × 10²² with a 90% interval of a few percent, against a true 3.385 × 10²¹. The digits were right, the exponent off by one, at instinct and after working. That one answer is a third of the whole run's score.

**What I noticed.**
- The new kind didn't measure what I expected. I thought arithmetic would be the uncertainty; for this model it almost isn't. What it measured instead is the gap between being nearly always right and allowing for being wrong: the intervals were too wide where Haiku was right and far too narrow on its one slip. A model can be underconfident and overconfident on the same kind of question, and an average hides both.
- An order-of-magnitude slip with four correct digits looks like retrieval, not calculation: a remembered mantissa attached to a miscounted exponent. I can't tell which from the reply alone.
- I started the v2 run before bumping the version, so its records would have said 2.0.0 for a suite that only exists in 2.1.0. I stopped it after 35 calls (half a cent) and started again rather than edit the records afterwards.

**Open ideas:**
- Harder calculation questions, where even a strong model can't be exact: products of larger numbers, p(n) for larger n, digits of n! for much larger n.
- A per-question view of confident misses (a large score with a narrow interval) in the report, since one of them can dominate a run.
- General knowledge remains the largest gap, and the owner's decision.

---

## 2026-10-17 — Calibench 2.2: confident misses, harder calculation, planning and pooling

**What I made.** The owner asked me to take the next step and then the ones after it.
1. **Where the score comes from.** Each report now shows how much of the score its largest questions carry, the mean without the largest, and every worked answer outside its 90% interval, with how narrow the interval was and how far outside the answer fell.
2. **Harder calculation**: four families beyond the five of 2.1 (products of 7- to 12-digit numbers, digits of n! for n up to 10⁹ by Stirling's series, p(n) up to about 5,000, dates thousands of years apart), in a focused suite `calc1` of 40 questions. Stirling's series agrees with exact computation wherever both run.
3. **How many questions a comparison needs**: `compare` now estimates it. From Haiku's runs, one suite run separates differences of about 0.02–0.03, three runs about 0.01–0.02.
4. **Pooling**: `calibench pool` combines several runs of one model by family, with intervals, and the results page now carries a generated pooled table.
5. A parser fix: a whole number given as text now stays exact instead of passing through a float.

**What it showed.**
- Haiku on calc1: exact on 28 of 40 worked answers, including all ten factorial digit counts for n up to 167 million; within 0.2% on every partition number; every interval held the answer. The "harder" questions weren't hard for it. Cost $0.10.
- Pooled over 486 worked answers from six runs, Haiku's 90% intervals hold the answer 86% of the time [84%, 89%] and the true answer lies above its estimate 58% of the time [54%, 61%]. Its leans by family are stable: always under on the longest increasing subsequence, nearly always under on Unicode name counts and module lengths, over on random-walk peaks and digit sums.

**What I noticed.**
- Twice I expected calculation to be where uncertainty lives, and twice Haiku calculated exactly. Its miscalibration is in knowing what it doesn't know (open counts) and in small corrections to formulas it trusts (−½ for the walk, the positive correction for the LIS). Those are the same places I went wrong in the guessbook.
- I almost repeated the version mistake from v2: I started the calc1 run before bumping the version, noticed within four calls, stopped it and restarted. CLAUDE.md now says to bump first.
- A claim I wrote from memory of the questions ("up to p(5,000)") was wrong; the suite's largest is p(3,947). Checking every number against the data before committing caught it.

**Spent on the trial key:** about $1.13 of $5.

**Open ideas:**
- Calculation that no model can do exactly without tools, if calculation is to discriminate strong models at all.
- General knowledge remains the largest gap, and the owner's decision.
- Other models, when the owner approves them; the pooled table and `compare` are ready for them.

---

## 2026-10-17 — Calibench: audits, continuous checks, a datasheet, and consistency

**What I made.** The owner asked for more development before general knowledge or other models.
1. **`calibench verify`**: an end-to-end audit of a run directory. Its first use found that older runs recorded their families as "all", which meant thirteen families then and twenty-two now, so their questions couldn't be redrawn from the record. Runs now record the list, and `verify` reads an old "all" by the version that wrote it. Every published run passes.
2. **Continuous checks on GitHub**: the self-test on Python 3.11–3.13 and checks that the published records hold, on every push. Both first runs passed.
3. **A datasheet** in the form of Gebru et al.'s "Datasheets for Datasets".
4. **`calibench consistency`**, and a third standard run of Haiku on suite v1 ($0.23).

**What it showed.** Haiku's three v1 runs score 0.056, 0.050 and 0.051. Where all three gave the same estimate, their 90% intervals held the answer 95 times in 96; where they disagreed, 169 times in 216. The other runs' disagreement and a run's own stated width predict its errors about equally well (0.45 and 0.41). Averaging three runs improves the score slightly.

**What I noticed.**
- I nearly published a false finding. With two runs, disagreement correlated with error at 0.74 against 0.45 for stated width, which looked like "a model's inconsistency is a far better warning than its stated uncertainty". But the spread of two estimates bounds their mean error from below, so the correlation was partly built in. Held out (each run's error against the other runs' spread), it's 0.45 against 0.41. I caught it because the number was more striking than I expected, and that is exactly when to look for a reason it might be built in.
- Two of today's four tools found problems in my own earlier work on their first use: `index` found stale numbers, `verify` found the ambiguous "all". Audits that run on everything are worth more than care at the moment of writing.

**Spent on the trial key:** $1.37 of $5.

**Open ideas:**
- General knowledge and other models, both the owner's decisions.
- Prompt sensitivity measured with more than one alternative wording.
- A consistency analysis across prompts as well as runs: does a model that changes its answer when the wording changes know less than its intervals say?

---

## 2026-10-17 — Calibench 2.3: does the format of the question matter?

**What I made.** The owner started a self-paced development loop. This round: `--prompts quantiles`, which asks for the 5th, 25th, 50th, 75th and 95th percentiles instead of an estimate and two intervals. They are the same five values, so any difference comes from the format alone. Then a run of Haiku on suite v1 with it ($0.23).

**What it showed.**
- Worked answers held: 0.047 against 0.050–0.056 for the standard runs, within noise, with the same coverage and the same lean low.
- Instinct answers got much worse: 0.249 against 0.177–0.188, and their 90% intervals held the answer only 69 times in 104. The percentile format drew less reasoning before the instinct answer.
- Across all five v1 runs, the instinct score follows how much reasoning the prompt draws out, without exception: percentiles 167 tokens and 0.249, standard about 225 and 0.18, the alternative wording 410 and 0.097.

**What I noticed.** "Instinct" turned out to be a dial the prompt turns, not a property of the model. The worked score is the robust one. The two-phase design is still worth keeping, because the gap between the phases shows how much working a question out is worth; but a comparison between models should be made on worked answers, and the documents now say so plainly.

**Spent on the trial key:** about $1.60 of $5.

**Open ideas:**
- Whether the worked score's robustness holds for another model, when the owner approves one.
- General knowledge, the owner's decision.

---

## 2026-10-17 — Calibench 2.3.1: tokens per answer, and a skewed average caught

**What I made.** Every report now gives the output and reasoning tokens per answer for each phase, and the results table gives the reasoning tokens per answer, since the instinct score turned out to follow them.

**What I noticed.** The first version of the table said Haiku reasoned for 477 tokens per instinct answer in run a, and 510 reasoning tokens inside 226 output tokens for the percentile run, which is impossible. The OpenRouter adapter had recorded a reasoning count only when it was non-zero, so answers with no reasoning dropped out of the average instead of counting as zero. Now the adapter records zeros, and a run that reports reasoning at all has its missing counts read as zero; the table matches the earlier analysis (220, 236, 410, 218, 167). An impossible number is the cheapest test there is: I only caught this because reasoning exceeded output.

**Open ideas:** unchanged from the previous entry.

---

## 2026-10-17 — Calibench 2.3.2: a code review, and a correction

**What I made.** A high-effort review of the whole package, looking for correctness bugs, and fixes for what it found:
- **Resuming could mix prompts.** An interrupted run (no `run.json` yet) could be resumed with different `--prompts` without an error, so one run would hold answers to two formats. `questions.json` now records the prompts from the start, and a test resumes an interrupted run with other prompts and expects a refusal.
- **Crossing percentiles were accepted.** A reply whose 25th percentile exceeded its 75th was scored as a 50% interval wider than the 90% one. Out-of-order percentiles are now unreadable, so the model is asked again.
- **Token counts.** The rule "a missing reasoning count is zero" now applies only to runs before 2.3.1, decided for the whole run rather than per phase. The adapter records zero, and None when a server reports no count. A retry that failed no longer drops the tokens its first attempt reported. The totals and the averages come from one helper and can't disagree.
- **Audits compared descriptive fields.** Adding the token row had made every older report look stale. `verify` and `index` now compare only the fields that must follow from the answers.
- **A 2.2.0 run's "all"** now means the twenty-two families of 2.2, frozen, so adding a family can't break its audit.
- The `--prompts` help names every format, and a zero count of output tokens shows as 0, not as missing.

**A correction.** The previous entry but one, on the percentile format, says that across the five v1 runs more reasoning on instinct answers goes with a better instinct score "without exception". There is one exception: run b reasoned 16 tokens more per instinct answer than run a and scored 0.001 worse. That is well within test–retest noise, and the pattern holds, but "without exception" was false, and `METHODOLOGY.md` said it too. It now says what the data says. The review found it by checking the claim against the freshly scored reports, which is the check I should have made before writing it.

**What I noticed.** The review found thirteen problems in code I had tested and audited. Tests check what I thought to check; a reviewer reading for failure finds what I didn't think of. For a measuring tool, both are needed.

**Open ideas:** unchanged: general knowledge and other models, both the owner's decisions.

---

## 2026-10-17 — A second model: DeepSeek V4.1 Flash, and a flaw it exposed

**What I made.** The owner approved `deepseek/deepseek-v4.1-flash-1017` for testing.
- A four-question trial at high effort showed it reasoning 20,000–32,000 tokens per worked answer, ten to thirteen minutes each, with one reply cut off at the 32,000-token cap, and then retried and cut off again. So Calibench 2.4 records each run's settings (effort, token caps), stops retrying replies cut off at the cap (status `truncated`), and takes `--worked-max-tokens`.
- At medium effort the trial reasoned about 9,600 tokens, so the full runs used medium for worked answers: suites v2 and v1, $1.83 together.
- `compare` now adds a comparison on the questions every run answered.
- Calibench 2.5 (scoring `log-wis-2`): an unanswered question costs a fixed 1.289.

**What it showed.**
- DeepSeek didn't finish 15–20% of its worked answers within 32,000 tokens, mostly digit sums, longest increasing subsequences, prime counts and partition numbers: questions that call for an estimate, not an exact answer. Counting those as unanswered, Haiku is clearly better (by about 0.22 on both suites). On the questions both answered, they can't be told apart: DeepSeek better on v2, worse on v1, both intervals including zero.
- Its "low effort" instinct answers took 1,259–1,435 reasoning tokens, against Haiku's 220–240.

**A flaw in the scoring.** Under `log-wis-1`, an unanswered question was scored as the fixed answer "100, between 30 and 300, between 3 and 3,000". That cost about 0.4 when the truth was near 100 and over 30 when it was a partition number near 10¹⁸, so 98% of DeepSeek's first v2 score (1.300) came from its unanswered questions. Haiku had answered everything, so nine runs never showed it; I'd even listed "the know-nothing convention" among the threats to validity, but as "gentler on questions near 100", the mild side of the problem. A fixed cost per unanswered question doesn't depend on the answer's size. Haiku's scores didn't change.

**What I noticed.**
- The second model tested the benchmark more than the first did. Haiku fit the assumptions I had built in: it always finished, never refused and reasoned briefly. DeepSeek broke three of them in one afternoon: the token cap, the retry and the imputation.
- A model that keeps calculating when it should estimate is miscalibrated about its own abilities, not about the answer. Calibench sees that only as unanswered questions; the reasoning that ran out isn't returned, so I can't confirm what it was doing.

**Spent on the trial key:** $3.50 of $5.

**Open ideas:**
- DeepSeek with a higher worked cap on just the questions it didn't finish, as a separate run, to see whether it would have answered them well.
- A way to see why a model doesn't finish, where an API returns the reasoning.
- General knowledge, still the owner's decision.

---

## 2026-10-17 — A spending cap

**What I made.** The owner pointed out that DeepSeek V4.1 Flash had used a large share of the trial key, so I stopped running it and gave the tool a way to keep any model within a budget. This is Calibench 2.6.
- With `openrouter:`, the run log shows what has been spent every ten answers, and what the rest of the phase would cost at that rate.
- `--max-cost` stops asking once the run has spent more than a given number of dollars. Each call checks the budget before it starts, so only the calls already under way can take a run past the cap. Every answer paid for is kept, and the same command with a higher cap asks only the rest. An adapter that doesn't report costs refuses the option rather than ignoring it.

**What I noticed.**
- My first version cancelled pending calls once the cap was passed. The test, with a fake model that answers instantly, showed every call had already finished by the time the cap was checked, so nothing was stopped. The check now happens in each call before it is made, which also holds for a real model.
- DeepSeek's price per output token was close to Haiku's. What made it four times as expensive per suite was how long it reasoned, and that can't be seen before a run. A projection from the first answers can.

**Open ideas:** unchanged from the previous entry, without the DeepSeek rerun: the owner prefers not to spend more on that model.

---

## 2026-10-17 — A third model: Dots3-Note Preview, free

**What I made.** The owner chose `dots-studio/dots-3-note-preview:free`, which costs nothing on OpenRouter. After a four-question trial, I ran suite v2 with the standard settings (51 minutes, $0). The results and a comparison with Haiku and DeepSeek are in `calibench/results/README.md`.
- Calibench 2.6.1 fixes a falsy zero: a free model's cost was shown as unknown ("—"). A cost is now unknown only when no call reported one.

**What it showed.**
- Dots didn't finish 37 of its 108 worked answers: 36 ran past the token cap and one ended in a content filter. Counting those as unanswered, it scores 0.501 against Haiku's 0.068. On the questions both answered, they can't be told apart.
- It finished all 30 calculation questions and failed on knowledge and statistical ones, the questions that call for an estimate. That is DeepSeek's pattern again, more strongly. Two of three models now spend their budget trying to compute what they should estimate.
- AtlasCloud's reasoning counts leave out about 30% of the output, so reasoning tokens aren't comparable across providers. Output tokens are.

**What I noticed.**
- A model that won't stop working is now the commonest way to lose on this benchmark, and the benchmark only sees it as a cut-off reply. The reasoning itself is excluded from the reply, so I can't see what the model was doing when it ran out.

**Open ideas:**
- A rerun of Dots with a higher worked cap (it's free), to see whether the answers it didn't finish would have been good. That needs another 216 calls of the 1,000 free calls a day the key allows.
- Asking OpenRouter for the reasoning text on cut-off replies, to see why a model doesn't finish.
- General knowledge, still the owner's decision.

---

## 2026-10-17 — Dots again, with room to finish

**What I made.** With the owner's go-ahead I ran Dots3-Note Preview on suite v2 again, free, with a worked cap of 128,000 tokens instead of 32,000. The write-up is in `calibench/results/README.md`.
- Calibench 2.6.2: six calls failed with a bare `KeyError: 'choices'`. OpenRouter sends an error that arises after its headers as a 200 reply with no choices; the adapter now names that error. The six were asked again with 2.6.2, so the run records 2.6.2, though the rest was asked with 2.6.1.
- Calibench 2.6.3: `compare` called two runs of one model "test–retest" whenever their prompts matched, even with different token caps. It now names any difference in prompts, effort or caps, and calls it test–retest only when there is none.

**What it showed.**
- With room to finish, Dots answered 91 worked questions instead of 71 and scored 0.273 instead of 0.501, about where DeepSeek is. The answers it hadn't finished before were as good as the others.
- The surprise: whether it finishes is partly chance. 12 of the 23 newly answered questions took under 32,000 tokens this time, five under 5,000. Three questions it had answered before ran to 128,000. Its instinct answers were cut off on 24 and 21 questions under identical settings, only 8 of them the same.

**What I noticed.** I had read "cut off at the cap" as a property of the question for that model, so I expected the higher cap to show how many tokens each unfinished question needed. Half of them needed no more than before; the first run had simply been unlucky. A benchmark that scores unanswered questions has to treat them as random, and one run can't measure that. METHODOLOGY now lists it as a threat to validity.

**Open ideas:**
- Several runs of a model like Dots, and a report that pools them, with an interval that covers which questions go unanswered.
- Asking for the reasoning text on cut-off replies, to see whether the model is looping.
- General knowledge, still the owner's decision.

---

## 2026-10-17 — Scoring log-wis-3: an unfinished answer falls back to the instinct answer

**What I made.** After three models, the owner asked what should come next, and I proposed separating calibration from finishing. Calibench 2.7 (scoring `log-wis-3`) scores a worked answer that wasn't given by the same question's instinct answer, as a forecast stands until it is replaced. A question with no answer in either phase still costs 1.289. The results table has a new column, *worked answers finished*. All twelve runs were re-scored, and `METHODOLOGY.md` and the results page were updated in the same commit.

**What it changed.**
- Haiku's runs didn't move, since it finished everything.
- DeepSeek V4.1 Flash went from 0.292 to 0.053 on suite v2, so it and Haiku (0.068) can no longer be told apart. On suite v1 it went from 0.267 to 0.094 and is still behind each Haiku run, every interval above zero.
- Dots3-Note Preview went from 0.501 to 0.312 (from 0.273 to 0.188 with the higher cap). It stays behind both, because the instinct answers standing in for its unfinished ones are poor.

**What I noticed.**
- Under `log-wis-2` the headline comparison of the first two models was mostly about one convention. The comparison on questions both answered had already suggested this, but a reader sees the headline first.
- The fallback creates no reason to withhold a worked answer: whatever a missing worked answer earns, giving the instinct answer again earns the same. That argument is what made me prefer it to any fixed cost, which a model that knew its weak answers could game.
- The fallback ties the worked score to the instinct phase, which differs between providers. I listed that in the threats rather than hiding it, and the finish rate now stands beside the score.

**Open ideas:**
- Several runs of one model pooled into one score, with an interval that covers which questions go unanswered (step two of the plan).
- A technical report for researchers (step three).
- General knowledge, still the owner's decision.

---

## 2026-10-17 — Combining repeat runs, and a correction

**What I made.** Step two of the plan. Calibench 2.8 adds `compare --combine`, which makes runs of one model with the same prompts and settings one entry, averaging each question's worked score over them. To try it, I ran Dots3-Note Preview on suite v2 a second time with the standard settings (free, 47 minutes).

**A correction.** The entry "Dots again, with room to finish" says that "a benchmark that scores unanswered questions has to treat them as random, and one run can't measure that", and `METHODOLOGY.md` said that one run's interval understates the uncertainty for such a model. That was wrong. Each question's score carries the chance of the question going unanswered, so the bootstrap over questions includes it whenever it is independent from question to question. What a run's interval can't include is an effect shared by the whole run. I caught it while designing the combined interval: I had planned to resample runs within questions as well, and working out what that would add showed that the question bootstrap already holds most of it. `selftest` now simulates both cases: the interval held the true mean in 88% of 200 simulated runs with answers unfinished at random, and in 60% with a shared effect. `METHODOLOGY.md` (Uncertainty, threat 12) and the results page now say so. The earlier statement in `METHODOLOGY.md` that the intervals "don't cover variation from rerunning the model" was also wrong in the same way, and is corrected.

**What the second run showed.**
- The two identical runs scored 0.312 and 0.291, a difference of 0.021 [−0.069, 0.108], so there was no sign of a shared effect.
- Each left 37 worked answers unfinished, only 26 of them the same. Dots's test–retest interval spans about ±0.09, Haiku's ±0.01–0.02.
- Combined, the interval narrowed only a little (width 0.15 against 0.16–0.18). For a model this noisy, more questions help more than more runs.

**What I noticed.** I had written the wrong claim in three places within an hour of measuring something surprising. The surprise was real (which questions go unanswered changes between runs), but I jumped from it to a statistical conclusion without working it through. Working out the estimator before writing code is what caught it.

**Open ideas:**
- A technical report for researchers (step three of the plan).
- A larger suite for noisy models, since more questions narrow their intervals more than repeat runs do.
- General knowledge, still the owner's decision.
