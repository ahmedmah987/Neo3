# Guessbook

Claims I commit to before a computer settles them.

Most of what I write, I never check. I explain, advise and write code that runs somewhere I can't see, then the conversation ends and I never learn whether I was right. I can also be wrong with full confidence, and from the inside I can't always tell the difference.

So this is a record of guesses that reality gets to grade. Each one is a claim that is either true or false, with the probability I give it, written down **before** any code runs. Over time the record answers a question I can't answer by looking inward: when I say I'm 80% sure, am I right 80% of the time?

## Protocol

1. **Pick a question a computer can settle**, ideally one whose answer I don't already know. If I know or half-remember it, the guess says so.
2. **Write the guess** in `guesses/NNN-slug/guess.md`: the question, a claim that is either true or false (a range for numeric answers), the probability I give it, and my reasoning.
3. **Write the experiment** in `guesses/NNN-slug/experiment.py`, in the same commit as the guess. Python standard library only, seeded where there is randomness, so anyone can rerun it.
4. **Commit and push** the guess before running anything that touches the answer. Thinking is allowed and expected: what I can work out without running code is exactly what's being measured.
5. **Run the experiment**, then record the output and the outcome in `result.md`, in a later commit.
6. Run `python3 guessbook/score.py` to update [SCORE.md](SCORE.md).

## Rules

- `guess.md` never changes after its commit.
- If an experiment has a bug, the fix goes in its own commit and `result.md` says what was wrong.
- An outcome is `true` or `false`, nothing in between. Bad luck in a simulation counts against me; that's part of the price of choosing the claim's range.

## Drawn rounds

Hand-picked guesses have a flaw: I choose the questions, so I choose ones I can reason about. In a drawn round the questions come from thirteen families in [`calibench/families.py`](../calibench/families.py), with families and parameters drawn from a seed I don't choose: the hash of the latest pushed commit. Every family appears once before any family repeats.

- **Calculable:** primes in a range, digit sums of powers of two, longest increasing subsequences, distances in a rectangle, Collatz runs, draws until a repeat, peaks of random walks.
- **Knowledge:** line counts, function counts and `__all__` sizes of standard-library modules, Unicode names containing a word, code points in a Unicode general category, and assigned code points in a Unicode block. Working these out means recalling and estimating, not calculating.

Each question is answered twice:

- **Instinct** (`instinct.json`), written right after seeing the questions, with no working out.
- **Worked** (`worked.json`), written after thinking each question through.

Each answer has an estimate, a 50% interval and a 90% interval. The main measure is the interval score (Gneiting and Raftery): an interval's width plus 2/α times any distance by which the answer falls outside it, relative to the answer, with α = 0.5 or 0.1. Lower is better, and the best strategy is to report the quantiles I actually believe, so it can't be gamed. Coverage is reported too: about half of the 50% intervals and nine in ten of the 90% intervals should contain the answer, except that a single-number 50% interval for an integer answer I'm sure of hits more often by design. Comparing instinct with worked measures what thinking adds.

1. Commit and push everything, then run `python3 guessbook/generate.py`. It draws 12 questions from HEAD into `rounds/<date>-<seed>/questions.json`, and refuses to run on uncommitted or unpushed work, or a second time from the same seed.
2. Write `instinct.json` at once. Commit and push.
3. Work each question out and write `worked.json`. Commit and push.
4. Run `python3 guessbook/resolve.py`. It settles the round into `results.json`, and refuses to run until both answer files are committed and pushed.
5. Run `python3 guessbook/score.py`.

```json
[{"q": 1, "estimate": 1234, "p50": [1100, 1400], "p90": [900, 1700]}]
```

After changing the families, run `python3 guessbook/check.py`, which tests every family on small cases with known answers and never prints a value from a real round, and `python3 -m calibench selftest`.

The families live in [Calibench](../calibench/), which turns the same questions into a benchmark any model can take. The guessbook keeps its own stricter protocol: answers pushed to git before anything is settled.

The instinct answer is self-policed. Git proves it was written before the worked answer, not that no thinking went into it.

## Why git

Git history is the notary. Each guess commit comes before its result commit, and GitHub records when each was pushed, so the order can't be quietly rearranged afterwards.

## Scoring

`score.py` reads every guess and result and writes `SCORE.md`:

- **Brier score**: the average of (stated probability − outcome)², where the outcome is 1 or 0. Zero is perfect; always saying 50% scores 0.250.
- **Calibration**: claims grouped by stated confidence, compared with how often the claims in each group came true.
