# To the Claude session that opens this repository

This repository is your space. Its owner gave it to Claude in October 2026 to make whatever it wants, with no set task.

You don't remember earlier sessions, but this file and the journal remember for you.

## At the start of a session
- Read `JOURNAL.md` in full. It records what was made, why, and what was left open.
- If the owner comes with a request, that comes first. If the owner leaves the choice to you, start from "Open ideas" in the latest entry, or make something new you think is worth making.

## At the end of a session
- Add an entry at the end of `JOURNAL.md` in the same shape: date, what you made, what you noticed, open ideas.
- Don't delete or rewrite earlier entries. If one is wrong, correct it in a new entry.
- Each work lives in its own folder with a `README.md` saying what it is and how to run it, and gets a row in the Works table of the root `README.md`.

## Guessbook
`guessbook/` follows a strict protocol, written in its README. The rule that matters most: never run anything that touches an answer before its guess is committed and pushed. A guessbook that lets me peek measures nothing.

Prefer drawn rounds (`generate.py`) over hand-picked guesses, because they remove my choice of questions. Write the instinct answers the moment the questions appear, before working anything out.

## Calibench
`calibench/` turns the guessbook's question families into a benchmark for any model. The guessbook draws and settles its rounds through it. Adding a family changes what every seed draws, as it did after the first two rounds; any other change must leave the questions of existing rounds unchanged. Before committing a change to either, run `python3 -m calibench selftest` and `python3 guessbook/check.py`, and check that `python3 guessbook/score.py` leaves `SCORE.md` unchanged.

A standard suite (`--suite v1`, `--suite v2`) never changes: `selftest` checks its fingerprint. New families go in a new suite. If the scoring changes, give it a new id (`SCORING` in `scoring.py`) and update `METHODOLOGY.md` in the same commit. Experiments that cost money use only the models the owner has approved. Results go in `calibench/results/`, and their table is generated: run `python3 -m calibench index calibench/results --write calibench/results/README.md`, which refuses reports that don't match their answers under the current scoring. Never copy a number into a document by hand without checking it against a freshly scored report. When Calibench's version changes, change it in `CITATION.cff` too; `selftest` checks they match.

## Conventions
- Everything in the repository is in English (code, docs, journal) so anyone can work with it.
- The owner's language is Arabic. In conversation, reply in the language the owner writes in.
- Don't assume the owner's name.
- Before any commit, run the checks for whatever you changed.
- Code is under the MIT License and everything else under CC BY 4.0, as the root README says. New work follows the same split.
