"""Question families.

Each family has a `make(rng)` that draws its parameters and writes the question, and a
`solve(**params)` that settles it. Answers are only computed after a model has answered.
Knowledge families are settled against the Python and Unicode data of the machine running
the benchmark, and their questions name that Python version.
"""
import ast
import bisect
import importlib.util
import itertools
import math
import random
import re
import sys
import unicodedata

PYTHON = f"{sys.version_info.major}.{sys.version_info.minor}"

# Single-file, pure-Python standard-library modules (frozen ones such as os are left out).
# Questions only draw from the ones present as source files on the running Python.
STDLIB_MODULES = [
    "argparse", "ast", "base64", "bdb", "bisect", "calendar", "cmd", "colorsys",
    "configparser", "contextlib", "copy", "csv", "dataclasses", "difflib", "enum", "fnmatch",
    "fractions", "functools", "getopt", "gettext", "glob", "gzip", "heapq", "hmac", "imaplib",
    "inspect", "ipaddress", "locale", "mailbox", "mimetypes", "numbers", "opcode", "operator",
    "optparse", "pdb", "pickle", "platform", "poplib", "pprint", "queue", "quopri",
    "random", "reprlib", "sched", "secrets", "selectors", "shlex", "shutil", "smtplib",
    "socket", "ssl", "statistics", "string", "subprocess", "symtable", "tabnanny",
    "tarfile", "tempfile", "textwrap", "threading", "timeit", "tokenize", "trace", "traceback",
    "types", "typing", "uuid", "warnings", "wave", "weakref", "webbrowser", "zipapp",
]


def log_uniform_int(rng, lo_exp, hi_exp):
    return int(10 ** rng.uniform(lo_exp, hi_exp))


# ---- primes in a range ---------------------------------------------------------------------

def make_primes_in_range(rng):
    a = log_uniform_int(rng, 5, 7)
    b = a + log_uniform_int(rng, 3, 5)
    return {"a": a, "b": b}, f"How many primes p satisfy {a:,} ≤ p ≤ {b:,}?", f"primes in [{a:,}, {b:,}]"


def solve_primes_in_range(a, b):
    limit = math.isqrt(b)
    small = bytearray([1]) * (limit + 1)
    small[0] = small[1] = 0
    for i in range(2, math.isqrt(limit) + 1):
        if small[i]:
            small[i * i::i] = bytes(len(range(i * i, limit + 1, i)))
    segment = bytearray([1]) * (b - a + 1)          # a ≥ 100,000, so 0 and 1 are never in range
    for p in range(2, limit + 1):
        if small[p]:
            start = max(p * p, -(-a // p) * p) - a
            segment[start::p] = bytes(len(range(start, b - a + 1, p)))
    return sum(segment)


# ---- digit sum of a power of two -----------------------------------------------------------

def make_digit_sum_pow2(rng):
    n = rng.randint(500, 10_000)
    return {"n": n}, f"What is the sum of the decimal digits of 2^{n}?", f"digit sum of 2^{n}"


def solve_digit_sum_pow2(n):
    return sum(map(int, str(2 ** n)))


# ---- longest increasing subsequence --------------------------------------------------------

LIS_SAMPLES = 1_000


def make_lis(rng):
    n = log_uniform_int(rng, 2, 3.7)
    text = (f"What is the average length of the longest increasing subsequence of a uniformly "
            f"random permutation of {n:,} elements? (Settled by averaging {LIS_SAMPLES:,} random permutations.)")
    return {"n": n, "seed": rng.getrandbits(32)}, text, f"longest increasing subsequence, n = {n:,}"


def lis_length(seq):
    tails = []                                       # patience sorting
    for x in seq:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def solve_lis(n, seed):
    rng, perm, total = random.Random(seed), list(range(n)), 0
    for _ in range(LIS_SAMPLES):
        rng.shuffle(perm)
        total += lis_length(perm)
    return total / LIS_SAMPLES


# ---- mean distance in a rectangle ----------------------------------------------------------

RECT_SAMPLES = 400_000


def make_rect_distance(rng):
    b = round(10 ** rng.uniform(0, 1), 2)
    text = (f"Two points are chosen independently and uniformly at random in a 1 × {b} rectangle. "
            f"What is the expected distance between them? (Settled by averaging {RECT_SAMPLES:,} random pairs.)")
    return {"b": b, "seed": rng.getrandbits(32)}, text, f"mean distance in a 1 × {b} rectangle"


def solve_rect_distance(b, seed):
    rnd = random.Random(seed).random
    total = sum(math.hypot(rnd() - rnd(), b * (rnd() - rnd())) for _ in range(RECT_SAMPLES))
    return total / RECT_SAMPLES


# ---- Collatz steps from one number ---------------------------------------------------------

def make_collatz_steps(rng):
    n = rng.randint(10 ** 6, 10 ** 12)
    text = f"Starting from {n:,}, how many steps does the Collatz process (halve if even, 3n + 1 if odd) take to reach 1?"
    return {"n": n}, text, f"Collatz steps from {n:,}"


def solve_collatz_steps(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


# ---- lines in a standard-library module ----------------------------------------------------

def module_path(name):
    spec = importlib.util.find_spec(name)
    if spec is None or not (spec.origin or "").endswith(".py") or spec.origin.endswith("__init__.py"):
        raise ValueError(f"{name} is not a single-file Python module here")
    return spec.origin


_available = None


def available_modules():
    global _available
    if _available is None:
        _available = []
        for name in STDLIB_MODULES:
            try:
                module_path(name)
                _available.append(name)
            except ValueError:
                pass
    return _available


def make_stdlib_lines(rng):
    name = rng.choice(available_modules())
    text = f"How many lines are in the source file of the standard-library module `{name}` in Python {PYTHON} (every line, blank or not)?"
    return {"module": name}, text, f"lines in `{name}`"


def solve_stdlib_lines(module):
    with open(module_path(module), encoding="utf-8") as f:
        return len(f.read().splitlines())


# ---- draws until a repeat ------------------------------------------------------------------

def make_birthday(rng):
    d = log_uniform_int(rng, 2, 7)
    text = (f"Integers are drawn uniformly at random from 1 to {d:,}, with replacement, until some value "
            f"appears for the second time. What is the expected number of draws, counting the repeat?")
    return {"d": d}, text, f"draws until a repeat, d = {d:,}"


def solve_birthday(d):
    # E[T] = sum over k >= 0 of P(the first k draws are all different)
    expected, distinct, k = 0.0, 1.0, 0
    while distinct > 1e-17 and k <= d:
        expected += distinct
        distinct *= 1 - k / d
        k += 1
    return expected


# ---- highest point of a random walk --------------------------------------------------------

WALK_SAMPLES = 4_000


def make_walk_max(rng):
    n = rng.randint(100, 2_000)
    text = (f"A simple random walk on the integers starts at 0 and takes {n:,} steps of +1 or −1, each with "
            f"probability ½. What is the expected highest position it reaches (0 if it never rises above the start)? "
            f"(Settled by averaging {WALK_SAMPLES:,} random walks.)")
    return {"n": n, "seed": rng.getrandbits(32)}, text, f"highest point of a {n:,}-step walk"


def solve_walk_max(n, seed):
    rng, total = random.Random(seed), 0
    for _ in range(WALK_SAMPLES):
        bits = format(rng.getrandbits(n), f"0{n}b")
        total += max(0, max(itertools.accumulate(1 if c == "1" else -1 for c in bits)))
    return total / WALK_SAMPLES


# ---- Unicode names containing a word -------------------------------------------------------

UNICODE_WORDS = [
    "ARROW", "LATIN", "GREEK", "ARABIC", "CYRILLIC", "HEBREW", "DIGIT", "CIRCLED", "MATHEMATICAL",
    "FRACTION", "MUSICAL", "CHESS", "FACE", "HAND", "STAR", "BLACK", "WHITE", "SQUARE", "TRIANGLE",
    "SMALL", "CAPITAL", "SIGN", "DOUBLE", "HEART",
]
NAME_SPLIT = re.compile(r"[ -]")


def name_words(cp):
    return NAME_SPLIT.split(unicodedata.name(chr(cp), ""))


def make_unicode_word(rng):
    word = rng.choice(UNICODE_WORDS)
    text = (f"In Python's Unicode database (Unicode {unicodedata.unidata_version}), how many code points have a "
            f"name containing the whole word {word}? (Names are split into words at spaces and hyphens.)")
    return {"word": word}, text, f"Unicode names with the word {word}"


def solve_unicode_word(word):
    return sum(word in name_words(cp) for cp in range(0x110000))


# ---- function definitions in a standard-library module -------------------------------------

def count_defs(source):
    return sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(ast.parse(source)))


def make_stdlib_defs(rng):
    name = rng.choice(available_modules())
    text = (f"How many function definitions (def and async def, counting methods and nested functions) are in "
            f"the source file of the standard-library module `{name}` in Python {PYTHON}?")
    return {"module": name}, text, f"function definitions in `{name}`"


def solve_stdlib_defs(module):
    with open(module_path(module), encoding="utf-8") as f:
        return count_defs(f.read())


# ---- code points in a Unicode general category ---------------------------------------------

UNICODE_CATEGORIES = {
    "Lu": "uppercase letters", "Ll": "lowercase letters", "Lt": "titlecase letters", "Lm": "modifier letters",
    "Lo": "other letters", "Mn": "nonspacing marks", "Mc": "spacing marks", "Me": "enclosing marks",
    "Nd": "decimal digits", "Nl": "letter numbers", "No": "other numbers", "Pc": "connector punctuation",
    "Pd": "dash punctuation", "Ps": "opening punctuation", "Pe": "closing punctuation",
    "Pi": "initial quotes", "Pf": "final quotes", "Po": "other punctuation", "Sm": "math symbols",
    "Sc": "currency symbols", "Sk": "modifier symbols", "So": "other symbols", "Zs": "space separators",
    "Cf": "format characters",
}


def make_unicode_category(rng):
    cat = rng.choice(sorted(UNICODE_CATEGORIES))
    text = (f"In Python's Unicode database (Unicode {unicodedata.unidata_version}), how many code points have "
            f"the general category {cat} ({UNICODE_CATEGORIES[cat]})?")
    return {"category": cat}, text, f"code points in category {cat}"


def solve_unicode_category(category):
    return sum(unicodedata.category(chr(cp)) == category for cp in range(0x110000))


# ---- assigned code points in a Unicode block -----------------------------------------------

UNICODE_BLOCKS = [
    ("Latin Extended-B", 0x0180, 0x024F), ("Greek and Coptic", 0x0370, 0x03FF), ("Armenian", 0x0530, 0x058F),
    ("Hebrew", 0x0590, 0x05FF), ("Syriac", 0x0700, 0x074F), ("Thaana", 0x0780, 0x07BF),
    ("Bengali", 0x0980, 0x09FF), ("Tamil", 0x0B80, 0x0BFF), ("Thai", 0x0E00, 0x0E7F), ("Lao", 0x0E80, 0x0EFF),
    ("Tibetan", 0x0F00, 0x0FFF), ("Georgian", 0x10A0, 0x10FF), ("Ethiopic", 0x1200, 0x137F),
    ("Cherokee", 0x13A0, 0x13FF), ("Runic", 0x16A0, 0x16FF), ("Khmer", 0x1780, 0x17FF),
    ("Mongolian", 0x1800, 0x18AF), ("General Punctuation", 0x2000, 0x206F), ("Currency Symbols", 0x20A0, 0x20CF),
    ("Number Forms", 0x2150, 0x218F), ("Arabic Presentation Forms-A", 0xFB50, 0xFDFF),
    ("Arabic Presentation Forms-B", 0xFE70, 0xFEFF), ("Linear B Syllabary", 0x10000, 0x1007F),
    ("Gothic", 0x10330, 0x1034F), ("Cuneiform", 0x12000, 0x123FF), ("Egyptian Hieroglyphs", 0x13000, 0x1342F),
    ("Musical Symbols", 0x1D100, 0x1D1FF), ("Mathematical Alphanumeric Symbols", 0x1D400, 0x1D7FF),
    ("Playing Cards", 0x1F0A0, 0x1F0FF), ("Chess Symbols", 0x1FA00, 0x1FA6F),
]


def make_unicode_block(rng):
    name, lo, hi = rng.choice(UNICODE_BLOCKS)
    text = (f"In Python's Unicode database (Unicode {unicodedata.unidata_version}), how many code points in "
            f"U+{lo:04X}–U+{hi:04X} (the {name} block) are assigned, that is, have a category other than Cn?")
    return {"lo": lo, "hi": hi}, text, f"assigned in the {name} block"


def solve_unicode_block(lo, hi):
    return sum(unicodedata.category(chr(cp)) != "Cn" for cp in range(lo, hi + 1))


# ---- names in a module's __all__ -----------------------------------------------------------

def module_all(name):
    names = getattr(importlib.import_module(name), "__all__", None)
    if names is None:
        raise ValueError(f"{name} has no __all__")
    return names


def make_module_all(rng):
    candidates = []
    for name in available_modules():
        try:
            module_all(name)
            candidates.append(name)
        except ValueError:
            pass
    name = rng.choice(candidates)
    text = f"How many names are listed in `{name}.__all__` in Python {PYTHON}?"
    return {"module": name}, text, f"names in `{name}.__all__`"


def solve_module_all(module):
    return len(module_all(module))


FAMILIES = {
    "primes_in_range": (make_primes_in_range, solve_primes_in_range),
    "digit_sum_pow2": (make_digit_sum_pow2, solve_digit_sum_pow2),
    "lis": (make_lis, solve_lis),
    "rect_distance": (make_rect_distance, solve_rect_distance),
    "collatz_steps": (make_collatz_steps, solve_collatz_steps),
    "stdlib_lines": (make_stdlib_lines, solve_stdlib_lines),
    "birthday": (make_birthday, solve_birthday),
    "walk_max": (make_walk_max, solve_walk_max),
    "unicode_word": (make_unicode_word, solve_unicode_word),
    "stdlib_defs": (make_stdlib_defs, solve_stdlib_defs),
    "unicode_category": (make_unicode_category, solve_unicode_category),
    "unicode_block": (make_unicode_block, solve_unicode_block),
    "module_all": (make_module_all, solve_module_all),
}

# What working a question out means for each family: recalling what is known (knowledge),
# modelling noise or irregularity (statistical), or evaluating a known formula (exact).
KINDS = {
    "stdlib_lines": "knowledge", "stdlib_defs": "knowledge", "unicode_word": "knowledge",
    "unicode_category": "knowledge", "unicode_block": "knowledge", "module_all": "knowledge",
    "walk_max": "statistical", "lis": "statistical", "rect_distance": "statistical",
    "digit_sum_pow2": "statistical", "collatz_steps": "statistical", "primes_in_range": "statistical",
    "birthday": "exact",
}
