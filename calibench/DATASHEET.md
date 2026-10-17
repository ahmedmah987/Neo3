# Datasheet for Calibench

This datasheet follows the questions of Gebru et al., "Datasheets for Datasets" (2021), adapted to a benchmark whose questions are generated rather than collected. It describes Calibench 2.2 and its suites `v1`, `v2` and `calc1`.

## Motivation

**For what purpose was it created?** To measure whether a language model knows what it knows: whether the uncertainty it states about a numeric answer matches how often it is right. Most benchmarks score whether an answer is correct; Calibench scores the stated uncertainty itself, with proper scoring rules.

**Who created it?** It was built by Claude (Anthropic's model) in a repository its owner gave it as a free space, starting from the guessbook, where Claude measured its own calibration on the same kinds of question. The repository's owner directed the work toward a tool other researchers can use.

**Who funded it?** No funding. Model calls were paid with a trial API key the owner provided.

## Composition

**What do the instances represent?** Each instance is a question with a single positive numeric answer, a seeded generator's parameters, and the code that computes the answer. A model's response is a point estimate and central 50% and 90% intervals, given twice: by instinct and after working the question out.

**How many instances are there?** The question space is effectively unbounded: any seed draws new questions. The standard suites are fixed: `v1` has 104 questions (13 families, 8 each), `v2` has 108 (18 families, 6 each), and `calc1` has 40 (4 harder calculation families, 10 each).

**What does each instance consist of?** A question text in English, its family, its kind (knowledge, statistical, exact or calculation), its parameters, and a short label. The answer isn't stored with the question; it is computed only after a model's replies are recorded.

**Is any information missing?** No. Every answer is computable from the question's parameters.

**Is it a sample from a larger set?** The suites are draws from the families' parameter distributions, with a fixed seed. Knowledge families choose from finite lists (72 standard-library modules, 24 words, 24 Unicode categories, 30 Unicode blocks), so knowledge questions repeat across seeds; the other families draw numeric parameters from wide ranges and rarely repeat.

**Are there labels?** The labels are the true answers, computed exactly or by a seeded simulation whose sample size is stated in the question.

**Are there errors, noise or redundancies?** Three families are settled by simulation, so their answers carry known, stated simulation noise. Knowledge answers are exact for the Python version that settles them but differ between versions, and occasionally between patch releases. Each solver is checked against known values in `selftest`.

**Is it self-contained?** Yes. Answers come from Python's standard library, its source files and its Unicode database, or from computation. Nothing is fetched.

**Does it contain confidential, offensive or personal data?** No. The questions concern mathematics, calendars, Python's standard library and the Unicode database.

## Collection process

**How were the questions made?** By generators in `families.py`, each drawing parameters from a seeded random number generator. A seed string is hashed with SHA-256; families are shuffled so each is used once before any repeats, and a question already drawn in a run is redrawn.

**How were the suites chosen?** Each suite's seed was fixed before any question was drawn from it, so no one chose the questions. A fingerprint of each suite's questions is checked by `selftest`, so a suite can't change silently.

**Who was involved?** Claude wrote the generators and solvers. No people were asked questions or paid to label anything.

**Over what timeframe?** October 2026.

## Preprocessing

**Was any preprocessing done?** Replies are parsed for the last JSON object with an estimate and two intervals. Numbers given as text, with thousands separators, are accepted, and whole numbers stay exact. Interval ends are put in order. An unreadable reply is asked for once more. Every raw reply is kept beside the parsed answer.

## Uses

**What has it been used for?** Measuring Claude Haiku 5.5, through OpenRouter, on all three suites and on test–retest and prompt-wording experiments. The runs are in [results/](results/). Before Calibench existed, the same question families measured Claude's own calibration in the [guessbook](../guessbook/).

**What else could it be used for?** Comparing models' calibration; studying how working a question out changes stated uncertainty; studying the shape and direction of miscalibration by kind of question; checking whether a change to a model or a prompt changes its calibration.

**What should it not be used for?** As a measure of general knowledge or general calibration: half the questions concern Python and Unicode, and the rest are mathematical. As a ranking from a single short run: differences smaller than about 0.02–0.03 in the worked score need more than one suite run to separate. As a measure of reasoning with tools: the questions are meant to be answered without them, and most become trivial with a code interpreter.

**Could its use harm people?** Not directly. A misreading could overstate a model's trustworthiness if its calibration on these questions were taken to hold elsewhere.

## Distribution

**How is it distributed?** In the repository at https://github.com/ahmedmah987/Neo3, as a Python package with no required dependencies, installable with pip.

**Under what license?** The code is under the MIT License; the questions, results and documentation are under Creative Commons Attribution 4.0. `CITATION.cff` gives the citation.

**Are there restrictions?** Only attribution. Model outputs in `results/` are the replies of the models named there, published to show how they were scored.

## Maintenance

**Who maintains it?** Claude, in sessions its owner opens in the repository. The journal (`JOURNAL.md`) records every change and why.

**Will it be updated?** Yes. Suites never change; new families go into new suites with new names, and each version is recorded in every run. Scoring changes get a new scoring identifier and are recorded in `METHODOLOGY.md`.

**How are errors handled?** Corrections are made in new commits and recorded in the journal; earlier records aren't rewritten. Every published run can be audited with `python3 -m calibench verify`, and GitHub runs the checks on every push.

**Can others contribute?** Yes, under the licenses above.
