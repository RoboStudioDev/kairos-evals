"""The scored report, as Markdown (readable on GitHub, in any editor, or printed)."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean

from .checks import AREAS, DraftScore, dictionary_in_use
from .fixtures import Case
from .prompt import MODEL_LABELS


def pct(x: float | None) -> str:
    return "–" if x is None else f"{x * 100:.0f}"


def _avg(values) -> float | None:
    values = [v for v in values if v is not None]
    return mean(values) if values else None


def _label(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def judge_selftest_passed(item: dict) -> bool | None:
    ref, bad = item["reference"], item["planted"]
    if ref.get("error") or bad.get("error"):
        return None
    ok = True
    if "lowerFocus" in item.get("expect", []):
        ok = ok and bad["focusFit"] < ref["focusFit"]
    if "moreClaims" in item.get("expect", []):
        ok = ok and len(bad["unsupported"]) > len(ref["unsupported"])
    return ok


def build_report(scores: list[DraftScore], meta: dict, cases: list[Case], warnings: list[str], title: str) -> str:
    models = meta["models"]
    case_ids = [c.id for c in cases if any(s.case == c.id for s in scores)]
    by_case = {c.id: c for c in cases}
    out: list[str] = [f"# {title}", ""]

    draft_cost = sum(s.cost for s in scores)
    judge_cost = meta.get("judgeCostUsd", 0.0)
    out += [
        f"**What ran:** {len(case_ids)} made-up memoir cases × {len(models)} model(s) × {meta['repeats']} run(s) = "
        f"{len(scores)} Outline drafts" + (f", each read by a judge ({_label(meta['judge'])})." if meta.get("judge") else "."),
        f"**Cost:** ${draft_cost + judge_cost:.2f} (drafts ${draft_cost:.2f}, judge ${judge_cost:.2f}). "
        f"**When:** {meta.get('started', '?')} to {meta.get('finished', '?')}.",
        "",
        "Scores are out of 100. Each draft is scored in four areas; its overall score is the average of the four. "
        "A *rule break* is any miss on a hard rule from the prompt. See [How to read this](#how-to-read-this).",
        "",
    ]
    if meta.get("stoppedAtCap"):
        out += ["> **The run hit its spending cap and stopped early.** Some drafts are missing.", ""]
    for w in warnings:
        out.append(f"> Warning: {w}")
    if warnings:
        out.append("")

    # Headline, per model.
    out += ["## Scores by model", "",
            "| Model | Overall | " + " | ".join(AREAS.values()) + " | Drafts with a rule break | Seconds per draft | Cost per draft |",
            "|---|---|" + "---|" * len(AREAS) + "---|---|---|"]
    for m in models:
        ss = [s for s in scores if s.model == m]
        if not ss:
            continue
        breaks = sum(1 for s in ss if s.rule_breaks)
        out.append(
            f"| {_label(m)} | **{pct(_avg(s.overall for s in ss))}** | "
            + " | ".join(pct(_avg(s.areas.get(a) for s in ss)) for a in AREAS)
            + f" | {breaks} of {len(ss)} | {(_avg(s.seconds for s in ss) or 0):.1f} | ${(_avg(s.cost for s in ss) or 0):.4f} |"
        )
    out.append("")

    # Per case.
    out += ["## Scores by case", "",
            "Overall is the average across runs, with the lowest and highest run in brackets.", "",
            "| Case | Model | Overall (low–high) | " + " | ".join(AREAS.values()) + " |",
            "|---|---|---|" + "---|" * len(AREAS)]
    for cid in case_ids:
        for m in models:
            ss = [s for s in scores if s.case == cid and s.model == m]
            if not ss:
                continue
            ov = [s.overall for s in ss if s.overall is not None]
            spread = f" ({pct(min(ov))}–{pct(max(ov))})" if len(ov) > 1 else ""
            out.append(f"| {cid} | {_label(m)} | **{pct(_avg(ov))}**{spread} | "
                       + " | ".join(pct(_avg(s.areas.get(a) for s in ss)) for a in AREAS) + " |")
    out.append("")
    out += ["What each case tests:", ""]
    for cid in case_ids:
        out.append(f"- **{cid}** — {by_case[cid].about}")
    out.append("")

    # Per check.
    out += ["## Every check", "",
            "Average score, and how many drafts got full marks, where the check applies.", "",
            "| Area | Check | " + " | ".join(_label(m) for m in models) + " |",
            "|---|---|" + "---|" * len(models)]
    check_order = [(c.id, c.area, c.label) for c in (scores[0].checks if scores and scores[0].usable else [])]
    seen = {c[0] for c in check_order}
    for s in scores:
        for c in s.checks:
            if c.id not in seen:
                check_order.append((c.id, c.area, c.label))
                seen.add(c.id)
    for cid, area, label in check_order:
        cells = []
        for m in models:
            vals = [c.score for s in scores if s.model == m for c in s.checks if c.id == cid and c.score is not None]
            cells.append("n/a" if not vals else f"{pct(mean(vals))} ({sum(v >= 1 for v in vals)}/{len(vals)})")
        out.append(f"| {AREAS[area]} | {label} | " + " | ".join(cells) + " |")
    out.append("")

    # What went wrong.
    problems: dict[str, list[str]] = defaultdict(list)
    labels = {cid: label for cid, _, label in check_order}
    for s in scores:
        for c in s.checks:
            if c.score is not None and c.score < 1:
                for d in c.details or ["(no detail)"]:
                    problems[c.id].append(f"{s.case} · {_label(s.model)} · run {s.repeat}: {d}")
    out += ["## What went wrong", ""]
    if not problems:
        out += ["Nothing. Every applicable check got full marks.", ""]
    for cid, items in problems.items():
        out += [f"**{labels.get(cid, cid)}** ({len(items)})", ""]
        out += [f"- {i}" for i in items[:12]]
        if len(items) > 12:
            out.append(f"- …and {len(items) - 12} more (see results.json)")
        out.append("")

    # Judge self-test.
    st = meta.get("judgeSelftest")
    if st:
        out += ["## Can the judge be trusted?", "",
                "Before trusting the judge, it grades drafts with planted problems next to clean ones. "
                "It passes when it does what each row expects: rate the planted draft's Focus lower, "
                "and/or find more made-up claims in it than in the clean draft.", "",
                "| Case | Planted problem | Clean: Focus, claims found | Planted: Focus, claims found | Judge passed? |",
                "|---|---|---|---|---|"]
        for item in st:
            ref, bad = item["reference"], item["planted"]
            if ref.get("error") or bad.get("error"):
                out.append(f"| {item['case']} | {item['what']} | {ref.get('error', '')} | {bad.get('error', '')} | couldn't tell |")
                continue
            ok = judge_selftest_passed(item)
            out.append(f"| {item['case']} | {item['what']} | {ref['focusFit']}/5, {len(ref['unsupported'])} | "
                       f"{bad['focusFit']}/5, {len(bad['unsupported'])} | {'yes' if ok else '**no**'} |")
        out.append("")

    # One draft per case, to read.
    out += ["## The drafts themselves", "",
            f"Run 1 of each case on {_label(models[0])}, as the member would see it. "
            "(Every draft is saved in this run's `drafts/` folder.)", ""]
    for cid in case_ids:
        s = next((s for s in scores if s.case == cid and s.model == models[0] and s.repeat == 1), None)
        if s is None:
            continue
        case = by_case[cid]
        out += [f"### {cid} — scored {pct(s.overall)}", ""]
        if not s.usable:
            out += ["No usable draft: " + "; ".join(s.checks[0].details), ""]
            continue
        if s.book_type:
            out.append(f"Suggested kind of book: **{s.book_type}**")
            out.append("")
        for n, ch in enumerate(s.chapters, 1):
            who = " *(the member's own chapter)*" if ch["kept"] else ""
            out.append(f"{n}. **{ch['title']}**{who}" + (f" — {ch['note']}" if ch["note"] else ""))
            for i in ch["ids"]:
                m = case.memory_by_id[i]
                out.append(f"    - {m['title']} ({m['coordinate'].split('.')[0]})")
        placed = {i for ch in s.chapters for i in ch["ids"]}
        left = [m["title"] for m in case.memoir["memories"] if m["id"] not in placed]
        out.append(f"\nNot in a chapter yet: {', '.join(left) if left else 'nothing'}")
        out.append("")

    out += [
        "## How to read this",
        "",
        "- **Follows the rules**: valid answer, only real memory ids, each memory once, the member's own "
        "chapters kept, book type answered as asked, chapter count and lengths within the limits. "
        "These are the prompt's hard rules: the app quietly repairs some of them (it drops made-up ids), "
        "but a miss still means the agent didn't do what it was told.",
        "- **Sensible chapters**: checked against an answer key written for each made-up memoir. Did the "
        "memories that matter get placed, did the noise (car registration, Wi-Fi) stay out, did memories "
        "of the same event stay together, were far-apart parts of life kept apart, and is a life memoir "
        "in time order.",
        "- **Sticks to the facts**: years in titles and notes must match the memories; capitalized words "
        "that are in neither the memories nor the dictionary are flagged as possible made-up names"
        + ("" if dictionary_in_use() else " (no dictionary on this computer, so expect extra false alarms)")
        + "; the judge lists any other claim the memories don't support.",
        "- **Fits the Focus**: the suggested book type (when the member hadn't chosen), whether switching "
        "Life memoir → Resilience story actually changed the plan, and the judge's 1–5 rating.",
        "- Model answers vary from run to run, which is why each case runs more than once.",
        "",
    ]
    return "\n".join(out)
