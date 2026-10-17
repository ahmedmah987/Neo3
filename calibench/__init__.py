"""Calibench: measures how well a model knows what it knows.

Every question has a single numeric answer that the benchmark can compute exactly or by a
seeded simulation. A model answers each question twice, first by instinct and then after
working it out, each time with an estimate, a 50% interval and a 90% interval. Answers are
settled only after all of them are recorded, and scored with the interval score.

Run `python3 -m calibench --help`.
"""
__version__ = "2.3.2"
