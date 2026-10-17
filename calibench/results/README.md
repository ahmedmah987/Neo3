# Results

Runs of Calibench on real models. Each folder is a complete run directory: the questions, every raw reply, the true answers, and the report. Rerun the scoring with `python3 -m calibench report <folder>`.

| Model | Date | Seed | Questions | Weighted interval score, worked (instinct) | Worked 50% / 90% hits | Cost |
|---|---|---|---|---|---|---|
| [Claude Haiku 5.5](openrouter_anthropic_claude-haiku-5.5-2026-10-17/report.md), through OpenRouter | 2026-10-17 | `2026-10-17` | 26 | 9.1%, median 1.7% (16.7%, median 8.9%) | 15 / 18 of 26 | $0.072 |

## Claude Haiku 5.5, 2026-10-17

- **Working it out helps.** It lowered the weighted interval score on 19 of 26 questions, and the median from 8.9% to 1.7%.
- **The 90% intervals are too narrow.** After working, only 18 of 26 held the answer (69%), against nine in ten for a calibrated model.
- **Overconfident after a calculation.** On the statistical questions, working it out cut 90% hits from 11 of 12 to 8 of 12. When a formula was available the model trusted it as exact. On the random walk it modelled the simulation noise correctly, said "the formula itself is essentially exact here", and missed by two standard errors because the formula lacked a −½ correction.
- **Open-ended counts run far low.** For the Unicode names containing HAND and WHITE, it estimated 125 and 105 against 304 and 290: the omission bias seen in the guessbook, but at about −60% instead of −10 to −36%. Its intervals were wide and still nowhere near.
- **Closed facts are recalled well.** `pprint.__all__` (7), `locale.__all__` (22 against 23), category Zs (17), the Ethiopic block (358): exact or nearly.
