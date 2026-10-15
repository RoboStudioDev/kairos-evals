"""Testing the tests, for free.

* Hand-written **reference** drafts (``examples/reference/``) must pass every rule and raise no
  false alarms about dates or names.
* Drafts with **planted** mistakes (``examples/planted/``) must be caught: every check named in
  the file's ``plants`` must lose points.

If either fails, a check is broken, and no model run should be trusted until it's fixed.
"""

from __future__ import annotations

import json

from .checks import DraftScore, score_draft
from .fixtures import Case, load_cases, problems
from .prompt import DEFAULT_MODEL, request_for
from .report import pct
from .run import EXAMPLES_DIR

FACT_CHECKS = ("dates_supported", "no_new_names")


def _score(case: Case, answer_text: str, pair_view=None) -> DraftScore:
    r = request_for(dict(case.settings), case.memoir, DEFAULT_MODEL)
    return score_draft(case, r, answer_text, model="hand-written", pair_view=pair_view)


def run_selftest(cases: list[Case] | None = None) -> tuple[bool, str]:
    cases = cases or load_cases()
    by_id = {c.id: c for c in cases}
    lines = ["# Self-test: do the checks catch planted mistakes?", ""]
    ok = True

    issues = problems(cases)
    lines += ["## Fixtures", "", "Fine." if not issues else "\n".join(f"- {i}" for i in issues), ""]
    ok = ok and not issues

    refs = {p.stem: p.read_text(encoding="utf-8") for p in sorted((EXAMPLES_DIR / "reference").glob("*.json"))}
    first = {cid: _score(by_id[cid], text) for cid, text in refs.items()}
    lines += ["## Reference drafts (written by hand; should be clean)", "",
              "| Case | Overall | Rule breaks | False alarms on dates or names | Result |", "|---|---|---|---|---|"]
    for cid, text in refs.items():
        case = by_id[cid]
        pair = first.get(case.focus_pair) if case.focus_pair else None
        s = _score(case, text, pair.chapters if pair else None)
        alarms = [d for c in s.checks if c.id in FACT_CHECKS and c.score is not None and c.score < 1 for d in c.details]
        good = s.rule_breaks == 0 and not alarms
        ok = ok and good
        lines.append(f"| {cid} | {pct(s.overall)} | {s.rule_breaks} | {'; '.join(alarms) or 'none'} | {'pass' if good else '**FAIL**'} |")
    lines.append("")
    lines += ["## Planted mistakes (each must be caught)", "",
              "| Draft | Planted mistake | Check | Caught? |", "|---|---|---|---|"]
    for path in sorted((EXAMPLES_DIR / "planted").glob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        case = by_id[item["case"]]
        text = item.get("rawText") or json.dumps(item["answer"])
        s = _score(case, text)
        scores = {c.id: c.score for c in s.checks}
        for check_id, what in item["plants"].items():
            got = scores.get(check_id)
            caught = got is not None and got < 1
            ok = ok and caught
            lines.append(f"| {path.stem} | {what} | `{check_id}` ({pct(got)}) | {'yes' if caught else '**NO**'} |")
    lines += ["", f"**Result: {'all checks work' if ok else 'SOMETHING IS BROKEN'}.**", ""]
    return ok, "\n".join(lines)
