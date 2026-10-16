"""Settle drawn rounds, but only once both of my answers are committed and pushed.

Usage: python3 guessbook/resolve.py
"""
import json
import pathlib
import subprocess
import sys
import time

from families import FAMILIES
from score import PHASES, check_answers

ROOT = pathlib.Path(__file__).parent


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT)


def committed_and_pushed(path):
    if git("ls-files", "--error-unmatch", str(path)).returncode:
        return False
    if git("diff", "--quiet", "HEAD", "--", str(path)).returncode:
        return False
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    return ahead.returncode == 0 and ahead.stdout.strip() == "0"


def main():
    for round_dir in sorted((ROOT / "rounds").iterdir()):
        if not round_dir.is_dir() or (round_dir / "results.json").exists():
            continue
        files = [round_dir / f"{phase}.json" for phase in PHASES]
        if not all(f.exists() and committed_and_pushed(f) for f in files):
            print(f"{round_dir.name}: waiting until {' and '.join(f.name for f in files)} are committed and pushed")
            continue
        questions = json.loads((round_dir / "questions.json").read_text(encoding="utf-8"))["questions"]
        for f in files:
            check_answers(f, json.loads(f.read_text(encoding="utf-8")), questions)

        results = []
        for q in questions:
            start = time.time()
            answer = FAMILIES[q["family"]][1](**q["params"])
            results.append({"q": q["q"], "answer": answer})
            print(f"{round_dir.name} {q['q']:>2}. {q['short']}: {answer} ({time.time() - start:.1f} s)")
        (round_dir / "results.json").write_text(
            json.dumps({"python": sys.version.split()[0], "results": results}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
