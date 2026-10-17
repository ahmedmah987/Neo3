"""Draw a round of questions from a seed I don't choose.

Usage: python3 guessbook/generate.py [count]

The seed is the current commit, which must already be pushed, so the questions are fixed
by public history before I see them, and anyone can regenerate them from that commit.
One round per seed: drawing again from the same commit is refused.
"""
import datetime
import json
import pathlib
import random
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))   # the calibench package
from calibench.questions import draw                                       # noqa: E402

ROOT = pathlib.Path(__file__).parent


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT)


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    if git("status", "--porcelain").stdout.strip():
        sys.exit("commit everything first: the seed must be a commit that describes the whole tree")
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    if ahead.returncode or ahead.stdout.strip() != "0":
        sys.exit("push first: the seed must be public before the questions are drawn")
    head = git("rev-parse", "HEAD").stdout.strip()

    round_dir = ROOT / "rounds" / f"{datetime.date.today().isoformat()}-{head[:8]}"
    if round_dir.exists():
        sys.exit(f"{round_dir.name} already exists: one round per seed")

    questions = draw(random.Random(int(head, 16)), count)    # every family once before any repeats

    round_dir.mkdir(parents=True)
    (round_dir / "questions.json").write_text(
        json.dumps({"seed": head, "questions": questions}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"round {round_dir.name}, seed {head}\n")
    for q in questions:
        print(f"{q['q']:>2}. {q['text']}")


if __name__ == "__main__":
    main()
