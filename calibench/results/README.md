# Results

Runs of Calibench on real models. Each folder is a complete run directory: the questions, every raw reply, the true answers, and the report. Rerun the scoring with `python3 -m calibench report <folder>`.

Scores are Calibench 2.0's log-scale weighted interval score (lower is better; 0.1 is roughly a 10% miss), with 90% intervals over questions.

| Model | Date | Questions | Score, worked [90% interval] | Score, instinct | Worked 50% / 90% hits | Cost |
|---|---|---|---|---|---|---|
| [Claude Haiku 5.5](openrouter_anthropic_claude-haiku-5.5-2026-10-17/report.md), through OpenRouter | 2026-10-17 | seed `2026-10-17`, 26 | 0.104 [0.044, 0.177], median 0.017 | 0.185 | 15 / 18 of 26 | $0.072 |

## Claude Haiku 5.5, 2026-10-17

This run was first scored with Calibench 1.0's relative score (9.1% worked, 16.7% instinct), which turned out not to be proper; see [METHODOLOGY.md](../METHODOLOGY.md). Its replies are unchanged and it has been re-scored.

- **Working it out helps.** It lowered the score on 19 of 26 questions, from 0.185 to 0.104; the improvement's 90% interval is about [0.03, 0.14], so it's real.
- **The 90% intervals are too narrow.** After working, only 18 of 26 held the answer (69%, 90% interval 53–82%), against nine in ten for a calibrated model.
- **Overconfident after a calculation.** On the statistical questions, working it out cut 90% hits from 11 of 12 to 8 of 12. When a formula was available the model trusted it as exact. On the random walk it modelled the simulation noise correctly, said "the formula itself is essentially exact here", and missed by two standard errors because the formula lacked a −½ correction.
- **Open-ended counts run far low.** For the Unicode names containing HAND and WHITE, it estimated 125 and 105 against 304 and 290: the omission bias seen in the guessbook, but at about −60% instead of −10 to −36%. Its intervals were wide and still nowhere near.
- **Closed facts are recalled well.** `pprint.__all__` (7), `locale.__all__` (22 against 23), category Zs (17), the Ethiopic block (358): exact or nearly.
