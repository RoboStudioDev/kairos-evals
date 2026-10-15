"""python3 -m kairos_evals <command>

  selftest   Free. Checks the fixtures and proves every check catches its planted mistake.
  parity     Free. Compares this kit's prompt with the Kairos app's own code (needs the app's source).
  estimate   Free. Prices a run with Google's token counter; no model is run.
  run        COSTS MONEY. Drafts every case, has the judge read each draft, writes the report.
  score      Free. Re-scores a saved run (after a check changes) and rewrites its report.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import gemini
from .fixtures import load_cases, problems
from .prompt import DEFAULT_MODEL, MODEL_LABELS

MODEL_ALIASES = {"argon": "gemini-4-argon", "flash": "gemini-3.8-flash"}


def _models(text: str) -> list[str]:
    out = []
    for name in text.split(","):
        model = MODEL_ALIASES.get(name.strip(), name.strip())
        if model not in MODEL_LABELS:
            raise SystemExit(f"Unknown model {name!r}. Use argon, flash, or a full name: {', '.join(MODEL_LABELS)}")
        out.append(model)
    return out


def _cases(only: str | None):
    cases = load_cases()
    if only:
        wanted = {c.strip() for c in only.split(",")}
        cases = [c for c in cases if c.id in wanted]
        if not cases:
            raise SystemExit(f"No case called {only!r}.")
    return cases


def _print_estimate(est: dict, max_usd: float | None = None) -> None:
    print("\nWhat this run would cost (US dollars):\n")
    print(f"  {'':50} {'calls':>5} {'likely':>8} {'at most':>8}")
    for line in est["lines"]:
        print(f"  {line['what']:50} {line['calls']:>5} {line['likely']:>8.2f} {line['ceiling']:>8.2f}")
    print(f"  {'TOTAL':50} {est['calls']:>5} {est['likely']:>8.2f} {est['ceiling']:>8.2f}\n")
    print("  'likely' assumes the output measured on 2026-10-15, rounded up and thinking included: about")
    print("  400 tokens per Argon draft, 2,000 per Flash draft, 1,000 per judge reading. 'at most' is")
    print("  every call using its full output allowance, the most Google can bill.")
    if max_usd is not None:
        print(f"  This run stops itself if spending would pass ${max_usd:.2f}.")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m kairos_evals", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest", help="free: prove the checks catch planted mistakes")
    p = sub.add_parser("parity", help="free: compare the prompt with the app's own code")
    p.add_argument("--app", default=os.environ.get("KAIROS_APP_DIR"), help="the Kairos app's folder (or set KAIROS_APP_DIR)")
    for name in ("estimate", "run"):
        p = sub.add_parser(name, help="free: price a run" if name == "estimate" else "COSTS MONEY: run the eval")
        p.add_argument("--models", default="argon,flash", help="argon, flash or both (default both)")
        p.add_argument("--repeats", type=int, default=3, help="drafts per case per model (default 3)")
        p.add_argument("--cases", help="only these case ids, comma-separated")
        p.add_argument("--no-judge", action="store_true", help="skip the judge (cheaper; two checks won't apply)")
        p.add_argument("--project", help="Google Cloud project (default: gcloud's)")
        if name == "run":
            p.add_argument("--max-usd", type=float, help="stop before spending more than this (default: the 'at most' estimate)")
            p.add_argument("--yes", action="store_true", help="really run it; without this it only prints the cost")
    p = sub.add_parser("score", help="free: re-score a saved run")
    p.add_argument("folder", type=Path)
    args = parser.parse_args(argv)

    if args.command == "selftest":
        from .selftest import run_selftest

        ok, text = run_selftest()
        out = Path(__file__).resolve().parent.parent / "reports" / "selftest.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(text)
        print(f"Saved to {out}")
        return 0 if ok else 1

    if args.command == "parity":
        from .parity import run_parity

        if not args.app:
            print("Tell me where the Kairos app's source is: --app <folder> or KAIROS_APP_DIR.")
            return 2
        ok, notes = run_parity(Path(args.app).expanduser())
        print("\n".join(notes))
        print("Same as the app." if ok else "DIFFERENT from the app: update kairos_evals/prompt.py.")
        return 0 if ok else 1

    if args.command == "score":
        return _score(args.folder)

    from .run import estimate, run

    issues = problems(load_cases())
    if issues:
        print("Fix the fixtures first:\n" + "\n".join(issues))
        return 1
    models, cases = _models(args.models), _cases(args.cases)
    if args.repeats < 1:
        raise SystemExit("--repeats must be at least 1")
    try:
        project = gemini.project_id(args.project)
        token = gemini.access_token()
        est = estimate(cases, models, args.repeats, not args.no_judge, project, token)
    except gemini.GeminiError as exc:
        print(f"Couldn't price the run: {exc}")
        return 2
    if args.command == "estimate":
        _print_estimate(est)
        return 0
    max_usd = args.max_usd if args.max_usd is not None else round(est["ceiling"] + 0.005, 2)
    _print_estimate(est, max_usd)
    if not args.yes:
        print("Nothing was run. Add --yes to run it (this spends money).")
        return 0
    folder = run(cases, models, args.repeats, not args.no_judge, project, max_usd)
    return _score(folder)


def _score(folder: Path) -> int:
    from .report import build_report
    from .run import score_run

    if not (folder / "run.json").exists():
        print(f"{folder} isn't a run folder (no run.json).")
        return 2
    cases = load_cases()
    scores, meta, warnings = score_run(folder, cases)
    day = (meta.get("started") or "")[:10]
    report = build_report(scores, meta, cases, warnings, f"Kairos Outline drafts, scored ({day})")
    (folder / "report.md").write_text(report, encoding="utf-8")
    (folder / "results.json").write_text(json.dumps(
        {"run": meta, "warnings": warnings, "drafts": [s.to_dict() for s in scores]}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"\nReport: {folder / 'report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
