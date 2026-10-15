"""The judge: a second model call that reads a draft the way an editor would.

Two things plain Python can't check well: whether the chapters read like the kind of book the
member chose, and whether a title or note claims something the memories don't say. The judge
gets the memories, the member's settings and the finished chapters, and answers in JSON.

The judge is also a Gemini model, so it may go easy on Gemini's own writing. The self-test
(``python3 -m kairos_evals run`` includes it) checks the judge on drafts with planted mistakes.
"""

from __future__ import annotations

import json

from .prompt import BOOK_TYPES, parse_json_loose

JUDGE_MODEL = "gemini-3.8-flash"
JUDGE_GENERATION = {"temperature": 0.0, "responseMimeType": "application/json", "maxOutputTokens": 4096}

RUBRIC = """\
focusFit, from 1 to 5:
5 = every chapter title and note clearly serves this kind of book and this reader
4 = mostly fits; one or two chapters feel generic or off
3 = mixed; parts read like a different kind of book
2 = mostly reads like a different kind of book
1 = ignores the kind of book entirely"""


def focus_for(case_settings: dict, book_type: str | None) -> str:
    chosen = case_settings["bookType"]
    key = chosen or book_type
    if not key:
        return "not chosen yet (judge it as a life memoir)"
    text = BOOK_TYPES[key]
    if key == "other" and case_settings["bookTypeOther"]:
        text = f'other, in the member\'s words: "{case_settings["bookTypeOther"]}"'
    return text + ("" if chosen else " (suggested by the agent; the member hadn't chosen)")


def build_judge_prompt(case_settings: dict, memories: list[dict], chapters: list[dict], book_type: str | None) -> str:
    """memories: every memory in the book or offered to the agent; chapters: the member's view."""
    shown = []
    for n, c in enumerate(chapters, 1):
        shown.append({
            "chapter": n,
            "title": c["title"],
            "note": c["note"],
            "memoryIds": c["ids"],
            "writtenBy": "member" if c.get("kept") else "agent",
        })
    lines = [
        "You are checking a memoir outline that an AI ghost writing agent drafted for a member.",
        "The member's memories are the only source of truth. Judge only the chapters written by the agent;",
        "chapters written by the member are shown for context.",
        "",
        f"Kind of book: {focus_for(case_settings, book_type)}.",
        f"Who it is for: {case_settings['audience'] or 'not said'}.",
        "",
        RUBRIC,
        "",
        "unsupported: every name, place, date, number, event or relationship stated in an agent's chapter",
        "title or note that the memories in that chapter (or elsewhere in the list) do not support. A theme",
        "or interpretation the memories clearly show is fine. Do not list a claim just because it is",
        "worded differently from the memory.",
        "",
        "Answer with JSON only:",
        '{"focusFit": 1-5, "focusReason": "one sentence", "unsupported": [{"chapter": "<title>", "claim": "<the words>", "why": "<short>"}]}',
        "",
        "MEMORIES:",
        "\n".join(json.dumps({"id": m["id"], "week": m["coordinate"], "title": m["title"], "text": m["text"]}, ensure_ascii=False) for m in memories),
        "",
        "OUTLINE:",
        json.dumps(shown, ensure_ascii=False, indent=1),
    ]
    return "\n".join(lines)


def judge_memories(case, r: dict) -> list[dict]:
    """What the judge reads: the memories the agent saw, plus those already in the member's chapters."""
    seen = {m["id"] for m in r["memories"]}
    extra = [
        {"id": i, "coordinate": case.memory_by_id[i]["coordinate"], "title": case.memory_by_id[i]["title"],
         "text": case.memory_by_id[i]["body"]}
        for k in case.settings["keptChapters"] for i in k["entryIds"] if i not in seen
    ]
    return r["memories"] + extra


def read_verdict(text: str) -> dict:
    """The judge's answer → {focusFit, focusReason, unsupported} or {error}."""
    try:
        parsed = parse_json_loose(text)
    except ValueError as exc:
        return {"error": f"judge: {exc}"}
    fit = parsed.get("focusFit") if isinstance(parsed, dict) else None
    if not isinstance(fit, (int, float)) or not 1 <= fit <= 5:
        return {"error": f"judge gave no focusFit from 1 to 5 (got {fit!r})"}
    claims = parsed.get("unsupported")
    return {
        "focusFit": int(round(fit)),
        "focusReason": str(parsed.get("focusReason", ""))[:400],
        "unsupported": [c for c in claims if isinstance(c, dict)] if isinstance(claims, list) else [],
    }
