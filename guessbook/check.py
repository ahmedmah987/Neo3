"""Checks for the question families, on small cases with known answers.

Run with: python3 guessbook/check.py
The families live in the calibench package; this runs its family checks.
Prints only pass or fail, never a value from a real round.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))   # the calibench package

from calibench import selftest                                            # noqa: E402

selftest.check_families()
print("\nall checks passed" if not selftest.failures else f"\n{len(selftest.failures)} failure(s)")
raise SystemExit(1 if selftest.failures else 0)
