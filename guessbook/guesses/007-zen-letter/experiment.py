"""Guess 007: most frequent letter in the Zen of Python."""
import collections
import contextlib
import io

buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    import this  # noqa: F401  (importing prints the Zen)

counts = collections.Counter(c for c in buffer.getvalue().lower() if c.isascii() and c.isalpha())
top = max(counts.values())
print("most common:", counts.most_common(5))
print("claim:", counts["e"] == top and list(counts.values()).count(top) == 1)
