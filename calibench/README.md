# Calibench

**Does a model know what it knows?** Most benchmarks ask whether a model's answer is right. Calibench asks whether the model knows *how likely* it is to be right: whether its "I'm sure" and its "about this much, give or take" match what actually happens.

A model is asked numeric questions it can't look up. For each one it gives an estimate, a 50% interval and a 90% interval, first by instinct and then after working it out. Calibench then computes the true answers and scores the stated uncertainty against them.

- **A standard suite, and fresh questions.** `--suite v1` asks every model the same 104 questions, fixed before any were drawn. Any other seed draws new ones, so there's no fixed answer key to memorise.
- **Every answer is computed.** Calibench settles each question itself, exactly or by a seeded simulation, and only after every answer has been recorded.
- **Proper scores, with their uncertainty.** The score can't be improved by stating intervals other than the ones the model believes, and every headline number comes with a 90% interval over questions.
- **Any model.** Claude, OpenRouter's hundreds of models, any OpenAI-compatible API, local models, any command-line program, replies collected by your own harness, or a chat window.
- **No dependencies** beyond Python 3.11 or later. The Claude adapter needs the official `anthropic` SDK.

The full method, its statistics and its known weaknesses are in [METHODOLOGY.md](METHODOLOGY.md).

## Quick start

```bash
git clone https://github.com/ahmedmah987/Neo3 && cd Neo3
python3 -m calibench selftest                         # checks everything against fake models and servers
python3 -m calibench run --model mock:naive --seed demo
```

Or install it, which adds a `calibench` command:

```bash
pip install "calibench[anthropic] @ git+https://github.com/ahmedmah987/Neo3"
calibench run --model mock:naive --seed demo
```

## Testing a model

```bash
# Claude, through the official SDK
pip install anthropic
export ANTHROPIC_API_KEY=...
python3 -m calibench run --model anthropic:claude-opus-5-5 --seed october

# Any model on OpenRouter (see https://openrouter.ai/models for ids)
export OPENROUTER_API_KEY=...
python3 -m calibench run --model openrouter:anthropic/claude-opus-5.5 --seed october

# Any OpenAI-compatible API
export OPENAI_API_KEY=...
python3 -m calibench run --model openai-compat:<model id> --seed october

# Another provider's compatible endpoint, with its own key
python3 -m calibench run --model openai-compat:<model id> --base-url https://<provider>/v1 --api-key-env PROVIDER_KEY --seed october

# A local model through Ollama (or vLLM, llama.cpp, LM Studio)
python3 -m calibench run --model openai-compat:llama3.1 --base-url http://localhost:11434/v1 --seed october

# Any program that reads a prompt on stdin and prints the reply
python3 -m calibench run --model "cmd:ollama run llama3.1" --seed october

# A model you can only reach through a chat window: paste each prompt, paste back each reply
python3 -m calibench run --model manual --seed october --count 13

# Your own harness (batch APIs, agents, anything else)
python3 -m calibench export --seed october --out prompts.jsonl
#   ...add a "reply" field to every line, keeping the rest...
python3 -m calibench run --model replies:prompts-with-replies.jsonl --seed october

# Compare models on the standard suite
python3 -m calibench run --model openrouter:<model id> --suite v1
python3 -m calibench compare calibench-runs/*-calibench-v1
```

To compare models, use `--suite v1`: 104 questions, every family 8 times, settled on Python 3.13. A seed you choose is for exploring; a comparison on a seed someone chose can be cherry-picked.

A run asks 26 questions by default (every family twice), each in two phases, so 52 calls. Use `--count` for more or fewer, `--families` to limit the kinds of question, and `--workers` for how many calls run at once. If a run is interrupted or some calls fail, run the same command again: answers already recorded are kept, and only the rest are asked. If the first three calls all fail, which usually means a wrong key, address or model name, the run stops and shows the error.

Other commands: `questions` prints the questions a seed draws, `families` lists the families, `report <dir>` re-scores a run, and `selftest` checks everything without contacting a real model.

## The questions

Thirteen families, each with parameters drawn from the seed:

| Kind | Family | Example |
|---|---|---|
| statistical | `primes_in_range` | How many primes p satisfy 178,117 ≤ p ≤ 179,381? |
| statistical | `digit_sum_pow2` | What is the sum of the decimal digits of 2^6256? |
| statistical | `lis` | Average longest increasing subsequence of a random permutation of 325 elements |
| statistical | `rect_distance` | Expected distance between two random points in a 1 × 2.54 rectangle |
| statistical | `collatz_steps` | Collatz steps from 624,045,563,571 to 1 |
| statistical | `walk_max` | Expected highest point of a 1,147-step random walk |
| exact | `birthday` | Expected draws from 1 to 227 until a value repeats |
| knowledge | `stdlib_lines` | Lines in the source of the standard-library module `queue` |
| knowledge | `stdlib_defs` | Function definitions in the source of `dataclasses` |
| knowledge | `module_all` | Names in `optparse.__all__` |
| knowledge | `unicode_word` | Code points whose name contains the word STAR |
| knowledge | `unicode_category` | Code points in the general category Pi |
| knowledge | `unicode_block` | Assigned code points in the Tibetan block |

**Statistical** questions need noise or irregularity modelled: a model can know the theory and still not know the exact answer. **Exact** ones have a closed form that has to be evaluated. **Knowledge** questions ask what is known about the Python standard library and the Unicode database. Each question is phrased so a careful model can reason toward it without tools; with a code interpreter most of them become trivial, so Calibench's adapters send no tools.

## How it's scored

Every true answer is positive, so answers are scored on a log scale: questions of every size can be averaged, a miss by a factor of ten costs the same in either direction, and the scores stay proper. Lower is always better; a score of 0.1 is roughly a 10% miss.

- **Score**: the weighted interval score (Bracher et al., 2021) on a log scale, the headline. It reads the estimate as a median and combines it with both intervals, approximating the continuous ranked probability score. A narrow interval scores well only if the answer lands inside it; a wide one pays for its width.
- **Interval score** for each interval (Gneiting and Raftery, 2007): its width plus 2/α times any distance by which the answer falls outside, with α = 0.5 for the 50% interval and 0.1 for the 90% one.
- **Coverage**: how often each interval contains the answer, with a 90% Wilson interval and a verdict of *too narrow*, *too wide* or *consistent with calibrated* at about two standard errors. Verdicts leave out single-number intervals, which claim exact knowledge; those are counted on their own line with how often they were exactly right.
- **Instinct against worked**: how much working a question out improves the score, with a 90% interval.
- **By kind**: the same scores for knowledge, statistical and exact questions, which tend to fail in different ways.
- **Unanswered questions** (refused, unreadable or failed) count as if the model had given the answer of a model that knows nothing, so refusing hard questions can't improve a score.

`compare` needs runs asked the same questions. It gives each run's score with a 90% bootstrap interval over questions and its difference from the best with a paired interval: when that interval includes zero, the questions don't separate the two. Runs of the same model also get a **test–retest** table: how much the score moved between runs, and how well the per-question scores agree.

## What a run leaves behind

Each run is a directory, by default `calibench-runs/<model>-<seed>/`:

| File | Contents |
|---|---|
| `run.json` | Model, seed, Calibench, Python and Unicode versions, and the SHA-256 of the answers, recorded before any answer is computed |
| `questions.json` | The questions |
| `answers.jsonl` | Every call: the raw replies, the answer read from them, its status (`ok`, `unparsed`, `refused` or `error`), the model that served it, and tokens |
| `results.json` | The true answers |
| `report.json`, `report.md` | The scores |

If `answers.jsonl` changes after its hash was recorded, the report says so.

## Choices worth knowing

- **No fallbacks.** Some APIs can quietly retry a refused request on a different model. Calibench leaves that off, because it would let one model answer under another's name. A refusal is recorded as a refusal, and every call records the model that actually served it.
- **Refusals and failures count against the model.** They score as the know-nothing answer and are listed on the report's *Answered* line, with the score over answered questions alone shown beside it.
- **Instinct versus worked.** The two phases use different prompts, and with the Claude adapter different effort levels (`--instinct-effort`, default `low`; `--worked-effort`, default `high`; pass `none` for models that don't take an effort setting). Some models always think before answering, Claude Opus 5.5 among them, so for them "instinct" means little thinking, not none.
- **OpenRouter.** The adapter checks the model id before asking anything, sends the effort through OpenRouter's `reasoning` setting to models that support it (and then only to providers that honour it), and records the model, the provider and the cost of every call. The report adds up the cost. OpenRouter can route a model to different providers, which may serve it differently; the provider is recorded so that's visible.
- **Keys stay in the environment.** API keys are read from environment variables and sent only to the API they belong to. They're never written into a run directory, and `.env` files are ignored by git.
- **Knowledge depends on the machine.** Knowledge questions are settled against the Python and Unicode data of the machine running Calibench, and the question names the Python version. `compare` warns when runs used different versions.

## Limits

- **Samples are small.** Even 104 questions leave real uncertainty, which is why every headline number carries an interval. Read the intervals, not just the means.
- **A narrow slice of knowledge.** The knowledge questions cover Python and Unicode. They test recall that can be checked exactly, not knowledge in general, and a score here says nothing direct about calibration elsewhere.
- **The suite is public.** Once its questions and answers are published they can leak into training data. Knowledge questions also repeat across seeds (72 modules, 24 words, 24 categories, 30 blocks). A model that does much better on the suite than on fresh seeds deserves suspicion.

[METHODOLOGY.md](METHODOLOGY.md) lists these and the other threats to validity in full.

## Results

Runs on real models, with every raw reply, are in [results/](results/). The first is Claude Haiku 5.5 through OpenRouter: working it out nearly halved its score, but its worked 90% intervals held the answer only 69% of the time.

## Where it came from

Calibench grew out of the [guessbook](../guessbook/), where Claude answered nine rounds of these questions itself under a stricter protocol: every answer committed and pushed to git before anything computed the truth. The guessbook still draws its rounds from this package. What those rounds taught shaped the scoring: knowing an answer exactly isn't the same as being calibrated, statistical and knowledge questions fail in different ways, and working a question out matters more than any adjustment to instinct.

## Files

| File | What it does |
|---|---|
| `families.py` | The question families: drawing each question and computing its answer |
| `questions.py` | Drawing questions from a seed |
| `prompts.py` | The two prompts, and reading an answer out of a reply |
| `models.py` | The model adapters |
| `runner.py` | Running a model, recording answers, then settling them |
| `scoring.py` | The scores |
| `report.py` | Reports and comparisons |
| `selftest.py` | The checks |
| `__main__.py` | The command line |
