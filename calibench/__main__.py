"""Command line: python3 -m calibench <command> --help"""
import argparse
import json
import pathlib
import secrets
import sys

from . import __version__
from .families import FAMILIES, KINDS
from .prompts import PROMPTS
from .questions import draw, rng_from_seed
from .scoring import PHASES

MODEL_HELP = """model to test:
  anthropic:<model id>      Claude through the official SDK (pip install anthropic); default claude-opus-5-5
  openai-compat:<model id>  any OpenAI-compatible server: hosted APIs, Ollama, vLLM, llama.cpp, LM Studio
  cmd:<shell command>       any program that reads the prompt on stdin and prints the reply
  replies:<file.jsonl>      replies you collected yourself: the lines of `export`, each with a "reply" added
  manual                    paste each reply yourself, for models you can only reach through a chat window
  mock:naive                knows nothing; a floor to compare against"""


def family_list(value):
    names = [v.strip() for v in value.split(",") if v.strip()]
    unknown = set(names) - set(FAMILIES)
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown families: {', '.join(sorted(unknown))}")
    return names


def add_draw_options(p, seed_required=False):
    p.add_argument("--seed", required=seed_required, help="any string; the same seed gives the same questions"
                   + ("" if seed_required else " (default: a new random seed)"))
    p.add_argument("--count", type=int, default=26, help="number of questions (default 26: every family twice)")
    p.add_argument("--families", type=family_list, help="comma-separated families to draw from (default: all)")


def cmd_run(args):
    from .models import make_model
    from .report import render
    from .runner import run

    seed = args.seed or secrets.token_hex(4)
    model = make_model(args.model, base_url=args.base_url, api_key_env=args.api_key_env,
                       instinct_effort=args.instinct_effort, worked_effort=args.worked_effort, timeout=args.timeout)
    report = run(model, args.model, seed, args.count, args.families, args.out, args.workers)
    print(render(report), end="")
    failed = sum(n for p in PHASES for s, n in report["phases"][p]["statuses"].items() if s not in ("ok", "refused"))
    if failed:
        print(f"\n{failed} calls failed or couldn't be read; run the same command again to retry them.", file=sys.stderr)


def cmd_questions(args):
    seed = args.seed or secrets.token_hex(4)
    print(f"seed {seed}\n")
    for q in draw(rng_from_seed(seed), args.count, args.families):
        print(f"{q['q']:>3}. [{q['kind']}] {q['text']}")


def cmd_export(args):
    lines = []
    questions = draw(rng_from_seed(args.seed), args.count, args.families)
    for phase in PHASES:
        for q in questions:
            lines.append(json.dumps({"id": f"{phase}-{q['q']}", "q": q["q"], "phase": phase,
                                     "prompt": PROMPTS[phase].format(text=q["text"])}, ensure_ascii=False))
    text = "\n".join(lines) + "\n"
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {len(lines)} prompts to {args.out}. Add a \"reply\" to each line, then run:\n"
              f"  python3 -m calibench run --model replies:{args.out} --seed {args.seed} --count {args.count}"
              + (f" --families {','.join(args.families)}" if args.families else ""), file=sys.stderr)
    else:
        print(text, end="")


def cmd_report(args):
    from .report import render
    from .runner import finish

    print(render(finish(args.dir)), end="")


def cmd_compare(args):
    from .report import compare

    reports = []
    for d in args.dirs:
        path = pathlib.Path(d) / "report.json"
        if not path.exists():
            sys.exit(f"{path} not found; run `python3 -m calibench report {d}` first")
        reports.append(json.loads(path.read_text(encoding="utf-8")))
    print(compare(reports), end="")


def cmd_families(args):
    for name in sorted(FAMILIES, key=lambda n: (KINDS[n], n)):
        print(f"{KINDS[name]:<12} {name}")


def cmd_selftest(args):
    from .selftest import main

    raise SystemExit(main())


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m calibench",
                                     description="Calibench: does a model know what it knows?")
    parser.add_argument("--version", action="version", version=f"calibench {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="ask a model the questions, then settle and score them",
                       formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--model", required=True, help=MODEL_HELP)
    add_draw_options(p)
    p.add_argument("--out", help="run directory (default: calibench-runs/<model>-<seed>)")
    p.add_argument("--workers", type=int, default=4, help="questions asked at once (default 4)")
    p.add_argument("--base-url", help="API base URL (openai-compat default: $OPENAI_BASE_URL or https://api.openai.com/v1)")
    p.add_argument("--api-key-env", help="environment variable holding the API key (openai-compat default: OPENAI_API_KEY)")
    p.add_argument("--instinct-effort", default="low", help="anthropic: effort for instinct answers (default low; none to omit)")
    p.add_argument("--worked-effort", default="high", help="anthropic: effort for worked answers (default high; none to omit)")
    p.add_argument("--timeout", type=float, default=600, help="seconds per call (default 600)")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("questions", help="print the questions a seed draws, without answers")
    add_draw_options(p)
    p.set_defaults(func=cmd_questions)

    p = sub.add_parser("export", help="write the prompts for a seed as JSON lines, to answer with your own harness")
    add_draw_options(p, seed_required=True)
    p.add_argument("--out", help="file to write (default: standard output)")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("report", help="settle and score a run directory again, and print its report")
    p.add_argument("dir")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("compare", help="compare runs on the questions they share")
    p.add_argument("dirs", nargs="+")
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("families", help="list the question families")
    p.set_defaults(func=cmd_families)

    p = sub.add_parser("selftest", help="check the families, the scoring and every model adapter")
    p.set_defaults(func=cmd_selftest)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
