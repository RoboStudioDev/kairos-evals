"""Running an eval: plan the calls, price them, make them, save every answer, score them.

Every answer is saved in ``runs/<time>/`` before it's scored, so scoring can be redone for free
(``python3 -m kairos_evals score runs/<time>``) after a check changes.
"""

from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import gemini, pricing
from .checks import DraftScore, member_view, score_draft
from .fixtures import ROOT, Case, load_cases
from .judge import JUDGE_GENERATION, JUDGE_MODEL, build_judge_prompt, judge_memories, read_verdict
from .prompt import GENERATION, build_draft_prompt, clean_draft, parse_json_loose, request_for

RUNS_DIR = ROOT / "runs"
EXAMPLES_DIR = ROOT / "examples"

# Output we expect per call, thinking included, for the "likely" cost. Measured 2026-10-15: Argon
# drafts averaged 227 output tokens with no thinking; 3.8 Flash drafts 260 plus 1,547 thinking; the
# judge (3.8 Flash) 705, of which 656 thinking. Rounded up here; every report shows the real numbers.
LIKELY_DRAFT_OUTPUT = {"gemini-4-argon": 400, "gemini-3.8-flash": 2000}
LIKELY_JUDGE_OUTPUT = 1000


@dataclass
class Job:
    case: Case
    model: str
    repeat: int

    @property
    def name(self) -> str:
        return f"{self.case.id}__{self.model}__r{self.repeat}"


def plan(cases: list[Case], models: list[str], repeats: int) -> list[Job]:
    # Repeat outermost, so a run stopped early still covers every case once.
    return [Job(c, m, k) for k in range(1, repeats + 1) for c in cases for m in models]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _placeholder_view(case: Case) -> list[dict]:
    """A stand-in draft of typical size, only for pricing the judge before any draft exists."""
    ids = case.must_place or [m["id"] for m in case.memoir["memories"]]
    return [
        {"title": "A chapter title of about forty characters", "note": "One plain line about what this chapter covers, roughly a hundred characters long.", "ids": ids[i : i + 3], "kept": False}
        for i in range(0, len(ids), 3)
    ]


def judge_selftest_items() -> list[dict]:
    """Drafts with planted problems, each beside the clean reference draft for the same case.
    The judge must grade the planted one worse (examples/judge-selftest.json)."""
    path = EXAMPLES_DIR / "judge-selftest.json"
    if not path.exists():
        return []
    items = []
    for item in json.loads(path.read_text(encoding="utf-8")):
        planted = json.loads((EXAMPLES_DIR / "planted" / f"{item['planted']}.json").read_text(encoding="utf-8"))
        reference = json.loads((EXAMPLES_DIR / "reference" / f"{item['case']}.json").read_text(encoding="utf-8"))
        items.append({**item, "reference": reference, "planted": planted["answer"]})
    return items


def estimate(cases: list[Case], models: list[str], repeats: int, judge: bool, project: str, token: str) -> dict:
    """Price a run with Google's free token counter. No model is run."""
    lines, likely, ceiling, calls = [], 0.0, 0.0, 0
    for model in models:
        tokens_in = 0
        for case in cases:
            prompt = build_draft_prompt(request_for(_case_dict(case), case.memoir, model))
            tokens_in += gemini.count_tokens(prompt, model, project, token)
        n = len(cases) * repeats
        cap_out = GENERATION["maxOutputTokens"]
        lk = repeats * pricing.cost(model, tokens_in, LIKELY_DRAFT_OUTPUT.get(model, 2000) * len(cases))
        cl = repeats * pricing.cost(model, tokens_in, cap_out * len(cases))
        lines.append({"what": f"drafts on {model}", "calls": n, "inputTokens": tokens_in * repeats, "likely": lk, "ceiling": cl})
        likely, ceiling, calls = likely + lk, ceiling + cl, calls + n
    if judge:
        tokens_in = 0
        for case in cases:
            r = request_for(_case_dict(case), case.memoir, models[0])
            prompt = build_judge_prompt(case.settings, judge_memories(case, r), _placeholder_view(case), None)
            tokens_in += gemini.count_tokens(prompt, JUDGE_MODEL, project, token)
        per_case_in = tokens_in / len(cases)
        selftest = [i for i in judge_selftest_items() if any(c.id == i["case"] for c in cases)]
        n = len(cases) * repeats * len(models) + 2 * len(selftest)  # self-test: clean + planted
        lk = pricing.cost(JUDGE_MODEL, int(per_case_in * n), LIKELY_JUDGE_OUTPUT * n)
        cl = pricing.cost(JUDGE_MODEL, int(per_case_in * n), JUDGE_GENERATION["maxOutputTokens"] * n)
        lines.append({"what": f"judge on {JUDGE_MODEL} (incl. its self-test)", "calls": n, "inputTokens": int(per_case_in * n), "likely": lk, "ceiling": cl})
        likely, ceiling, calls = likely + lk, ceiling + cl, calls + n
    return {"lines": lines, "calls": calls, "likely": likely, "ceiling": ceiling}


def _case_dict(case: Case) -> dict:
    """The settings in the shape prompt.client_body reads."""
    return dict(case.settings)


def run(cases: list[Case], models: list[str], repeats: int, judge: bool, project: str, max_usd: float, workers: int = 4) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out = RUNS_DIR / stamp
    (out / "drafts").mkdir(parents=True)
    (out / "prompts").mkdir()
    if judge:
        (out / "judge").mkdir()
    jobs = plan(cases, models, repeats)
    (out / "run.json").write_text(json.dumps({
        "started": datetime.now().isoformat(timespec="seconds"),
        "models": models, "repeats": repeats, "judge": JUDGE_MODEL if judge else None,
        "cases": [c.id for c in cases], "generation": GENERATION, "judgeGeneration": JUDGE_GENERATION,
        "maxUsd": max_usd,
    }, indent=2) + "\n")

    token = gemini.access_token()
    lock = threading.Lock()
    budget = {"spent": 0.0, "reserved": 0.0, "stopped": False}

    def reserve(model: str, prompt: str, max_out: int) -> float | None:
        worst = pricing.cost(model, len(prompt) // 2, max_out)  # generous: ~2 characters per token
        with lock:
            if budget["spent"] + budget["reserved"] + worst > max_usd:
                budget["stopped"] = True
                return None
            budget["reserved"] += worst
            return worst

    def settle(worst: float, actual: float) -> None:
        with lock:
            budget["reserved"] -= worst
            budget["spent"] += actual

    def call(model: str, prompt: str, generation: dict) -> dict:
        worst = reserve(model, prompt, generation["maxOutputTokens"])
        if worst is None:
            return {"error": f"skipped: would pass the ${max_usd:.2f} spending cap"}
        try:
            resp = gemini.generate(prompt, model, project, token, generation)
        except gemini.GeminiError as exc:
            settle(worst, 0.0)
            return {"error": str(exc)}
        resp["costUsd"] = round(pricing.cost(model, resp["inputTokens"], resp["outputTokens"]), 6)
        settle(worst, resp["costUsd"])
        return resp

    def do(job: Job) -> None:
        try:
            _do(job)
        except Exception as exc:  # one broken draft must not stop a paid run
            print(f"  draft  {job.name}: crashed: {exc!r}", flush=True)
            (out / "drafts" / f"{job.name}.json").write_text(json.dumps(
                {"case": job.case.id, "model": job.model, "repeat": job.repeat, "promptSha": "",
                 "response": {"error": f"crashed: {exc!r}"}}, indent=2) + "\n", encoding="utf-8")

    def _do(job: Job) -> None:
        r = request_for(_case_dict(job.case), job.case.memoir, job.model)
        prompt = build_draft_prompt(r)
        (out / "prompts" / f"{job.case.id}__{job.model}.txt").write_text(prompt + "\n", encoding="utf-8")
        resp = call(job.model, prompt, GENERATION)
        record = {"case": job.case.id, "model": job.model, "repeat": job.repeat, "promptSha": sha(prompt), "response": resp}
        (out / "drafts" / f"{job.name}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if "error" in resp:
            print(f"  draft  {job.name}: {resp['error'][:100]}", flush=True)
        else:
            print(f"  draft  {job.name}: {resp['seconds']}s, ${resp['costUsd']:.4f}", flush=True)
        if not judge or "error" in resp:
            return
        try:
            parsed = parse_json_loose(resp["text"])
            view = member_view(job.case, r, clean_draft(parsed, r))
            book_type = clean_draft(parsed, r)["bookType"]
        except (ValueError, AttributeError, KeyError):
            return
        jprompt = build_judge_prompt(job.case.settings, judge_memories(job.case, r), view, book_type)
        jresp = call(JUDGE_MODEL, jprompt, JUDGE_GENERATION)
        verdict = read_verdict(jresp["text"]) if "text" in jresp else {"error": jresp["error"]}
        (out / "judge" / f"{job.name}.json").write_text(json.dumps(
            {"case": job.case.id, "model": job.model, "repeat": job.repeat, "verdict": verdict, "response": jresp},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def do_selftest(item: dict) -> dict:
        case = next(c for c in cases if c.id == item["case"])
        r = request_for(_case_dict(case), case.memoir, models[0])
        results = {}
        for kind in ("reference", "planted"):
            draft = item[kind]
            view = member_view(case, r, clean_draft(draft, r))
            jprompt = build_judge_prompt(case.settings, judge_memories(case, r), view, clean_draft(draft, r)["bookType"])
            jresp = call(JUDGE_MODEL, jprompt, JUDGE_GENERATION)
            results[kind] = read_verdict(jresp["text"]) if "text" in jresp else {"error": jresp["error"]}
            results[kind]["costUsd"] = jresp.get("costUsd", 0.0)
        return {"case": item["case"], "what": item["what"], "expect": item["expect"], **results}

    print(f"Running {len(jobs)} drafts{' + judge' if judge else ''}; spending cap ${max_usd:.2f}.", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(do, jobs))
    if judge:
        items = [i for i in judge_selftest_items() if any(c.id == i["case"] for c in cases)]
        selftest = [do_selftest(i) for i in items]
        (out / "judge-selftest.json").write_text(json.dumps(selftest, indent=2, ensure_ascii=False) + "\n")
    meta = json.loads((out / "run.json").read_text())
    meta.update({"finished": datetime.now().isoformat(timespec="seconds"), "spentUsd": round(budget["spent"], 4), "stoppedAtCap": budget["stopped"]})
    (out / "run.json").write_text(json.dumps(meta, indent=2) + "\n")
    return out


def score_run(folder: Path, cases: list[Case] | None = None) -> tuple[list[DraftScore], dict, list[str]]:
    """Score every saved draft in a run folder. Free."""
    cases = cases or load_cases()
    by_id = {c.id: c for c in cases}
    meta = json.loads((folder / "run.json").read_text())
    warnings = []
    records = []
    for path in sorted((folder / "drafts").glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        case = by_id.get(rec["case"])
        if case is None:
            warnings.append(f"{path.name}: case {rec['case']} is no longer in fixtures/")
            continue
        r = request_for(_case_dict(case), case.memoir, rec["model"])
        if sha(build_draft_prompt(r)) != rec["promptSha"]:
            warnings.append(f"{path.name}: the fixtures changed after this draft was made; scores may not match")
        jpath = folder / "judge" / path.name
        verdict = json.loads(jpath.read_text(encoding="utf-8"))["verdict"] if jpath.exists() else None
        records.append((case, r, rec, verdict))

    def score(case, r, rec, verdict, pair_view=None):
        resp = rec["response"]
        return score_draft(case, r, resp.get("text"), model=rec["model"], repeat=rec["repeat"],
                           error=resp.get("error"), judge=verdict, pair_view=pair_view)

    first = {(rec["case"], rec["model"], rec["repeat"]): score(case, r, rec, v) for case, r, rec, v in records}
    scores = []
    for case, r, rec, verdict in records:
        pair = first.get((case.focus_pair, rec["model"], rec["repeat"])) if case.focus_pair else None
        scores.append(score(case, r, rec, verdict, pair.chapters if pair and pair.usable else None))
    for s, (_, _, rec, _) in zip(scores, records):
        resp = rec["response"]
        s.cost = resp.get("costUsd", 0.0)
        s.seconds = resp.get("seconds")
        s.input_tokens = resp.get("inputTokens")
        s.output_tokens = resp.get("outputTokens")
        s.thinking_tokens = resp.get("thinkingTokens")
    judge_dir = folder / "judge"
    judge_cost = sum(json.loads(p.read_text())["response"].get("costUsd", 0.0) for p in judge_dir.glob("*.json")) if judge_dir.exists() else 0.0
    selftest_path = folder / "judge-selftest.json"
    meta["judgeSelftest"] = json.loads(selftest_path.read_text()) if selftest_path.exists() else None
    if meta["judgeSelftest"]:
        judge_cost += sum(i[k].get("costUsd", 0.0) for i in meta["judgeSelftest"] for k in ("reference", "planted"))
    meta["judgeCostUsd"] = judge_cost
    return scores, meta, warnings
