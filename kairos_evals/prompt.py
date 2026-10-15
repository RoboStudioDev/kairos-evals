"""The Outline draft request and prompt, exactly as the Kairos app builds them.

Ported line for line on 2026-10-15 from the app's source:

* the page's request (``toWireMemory`` and ``draftRequestParts`` in ``src/lib/memoirOutline.ts``),
* the server's clean-up and prompt (``cleanOutlineRequest``, ``buildDraftPrompt`` and
  ``cleanDraft`` in ``functions/memoirOutline.js``),
* the server's fence-tolerant JSON reader (``parseJsonLoose`` in ``functions/index.js``).

If the app changes any of these, this file has to change too. ``python3 -m kairos_evals parity``
compares the two word for word when the app's source is on the same machine.
"""

from __future__ import annotations

import json
import re
from typing import Any

# The kinds of book a member can choose (BOOK_TYPES in memoirOutline.js).
BOOK_TYPES = {
    "life": "a life memoir: the whole life, more or less in order",
    "resilience": "a resilience story: how they came through something hard",
    "selfHelp": "self-help through experience: what their life can teach someone else",
    "other": "not decided yet",
}

# The models a member can pick (aiModels.js). Argon is the app's default.
MODEL_LABELS = {
    "gemini-3.8-flash": "Gemini 3.8 Flash",
    "gemini-4-argon": "Gemini 4 Argon",
}
DEFAULT_MODEL = "gemini-4-argon"

# How the server calls the model for a draft (makeOutlineHandler / vertexGenerate).
GENERATION = {"temperature": 0.4, "responseMimeType": "application/json", "maxOutputTokens": 8192}

APP_TEXT_LIMIT = 280  # MEMORY_TEXT_FOR_LENA: the page sends only the start of each memory
MAX_MEMORIES = 500
MAX_CHAPTERS = 60
ID_RE = re.compile(r"^[\w.-]{1,128}$", re.ASCII)
CHAPTER_ID_RE = re.compile(r"^[\w-]{1,40}$", re.ASCII)
COORD_RE = re.compile(r"^\d{1,4}\.\d{1,2}(\.\d)?$", re.ASCII)


def pick_model(model_id: str | None) -> str:
    return model_id if model_id in MODEL_LABELS else DEFAULT_MODEL


def _str(value: Any, limit: int) -> str:
    """The server's str(): trim, then cut to `limit`."""
    return value.strip()[:limit] if isinstance(value, str) else ""


def _js(value: Any) -> str:
    """JSON.stringify: no spaces, non-ASCII left as is."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


# ── What the page sends ──────────────────────────────────────────────────────────────────────


def client_body(case: dict, memoir: dict, model: str) -> dict:
    """The request body the Outline page posts for a first draft of this case."""
    kept = case.get("keptChapters", [])
    in_kept = {i for c in kept for i in c["entryIds"]}
    return {
        "mode": "outline",
        "task": "draft",
        "model": model,
        "bookType": case.get("bookType"),
        "bookTypeOther": case.get("bookTypeOther", ""),
        "audience": case.get("audience", ""),
        "chapters": [
            {"id": c["id"], "title": c["title"], "note": c.get("note", ""), "entryIds": c["entryIds"]}
            for c in kept
        ],
        "memories": [
            {
                "id": m["id"],
                "coordinate": m["coordinate"],
                "title": m["title"][:200],
                "text": m["body"][:APP_TEXT_LIMIT],
            }
            for m in memoir["memories"]
            if m["id"] not in in_kept
        ],
    }


# ── What the server does with it ─────────────────────────────────────────────────────────────


def clean_request(body: dict) -> dict:
    """cleanOutlineRequest: the body → the request the prompt is built from."""
    memories, seen = [], set()
    for m in body.get("memories", [])[:MAX_MEMORIES]:
        if not m or not ID_RE.fullmatch(str(m.get("id", ""))) or m["id"] in seen:
            continue
        if not COORD_RE.fullmatch(str(m.get("coordinate", ""))):
            continue
        seen.add(m["id"])
        memories.append(
            {
                "id": m["id"],
                "coordinate": m["coordinate"],
                "title": _str(m.get("title"), 200),
                "text": _str(m.get("text"), 300),
            }
        )
    chapters = []
    for c in body.get("chapters", [])[:MAX_CHAPTERS]:
        if not c or not CHAPTER_ID_RE.fullmatch(str(c.get("id", ""))):
            continue
        chapters.append(
            {
                "id": c["id"],
                "title": _str(c.get("title"), 120),
                "note": _str(c.get("note"), 500),
                "entryIds": [i for i in c.get("entryIds", []) if ID_RE.fullmatch(str(i))],
            }
        )
    book_type = body.get("bookType")
    return {
        "task": body.get("task"),
        "model": pick_model(body.get("model")),
        "bookType": book_type if book_type in BOOK_TYPES else None,
        "bookTypeOther": _str(body.get("bookTypeOther"), 120),
        "audience": _str(body.get("audience"), 1000),
        "memories": memories,
        "chapters": chapters,
    }


def _memory_lines(memories: list[dict]) -> str:
    return "\n".join(
        _js({"id": m["id"], "week": m["coordinate"], "title": m["title"], "start": m["text"]})
        for m in memories
    )


def _book_line(r: dict) -> str:
    if not r["bookType"]:
        return "The member has not chosen a kind of book yet."
    other = (
        f' In their words: "{r["bookTypeOther"]}".'
        if r["bookType"] == "other" and r["bookTypeOther"]
        else ""
    )
    return f"The book: {BOOK_TYPES[r['bookType']]}.{other}"


def build_draft_prompt(r: dict) -> str:
    """buildDraftPrompt, word for word."""
    kept = [{"id": c["id"], "title": c["title"], "note": c["note"]} for c in r["chapters"]]
    lines = [
        f"You are Kairos, the member's ghost writing agent (powered by {MODEL_LABELS[r['model']]}). A member is building a memoir from",
        "their own memories, and you are planning the book: grouping the memories into chapters.",
        "",
        _book_line(r),
        f"Who it is for: {r['audience'] or 'not said yet'}.",
        "",
        "Rules:",
        "- Use ONLY the memory ids listed below. Never invent a memory, a person, a place or an event.",
        "- Put each memory in at most one chapter. Leave a memory out if it does not belong in this",
        '  book; it will wait under "Not in a chapter yet".',
        "- Plan 3 to 12 chapters (fewer if there are only a few memories), in the order the book",
        "  should read.",
        "- Chapter titles: short and plain, under 60 characters. Notes: one line under 140 characters",
        "  saying what the chapter is about, in plain words.",
        "- List each chapter's memory ids in reading order.",
        (
            '- The member wrote the chapters under KEPT. Include each one exactly once, as {"keep": "<its id>"},'
            " where it belongs in the book. Do not change them."
            if kept
            else ""
        ),
        (
            '- Set "bookType" to null.'
            if r["bookType"]
            else '- Suggest the kind of book in "bookType": "life", "resilience", "selfHelp" or "other".'
        ),
        "",
        "Answer with JSON only, in this shape:",
        '{"bookType": null, "chapters": [{"title": "…", "note": "…", "entryIds": ["…"]}, {"keep": "…"}]}',
        "",
        f"KEPT: {_js(kept)}",
        "MEMORIES (one per line: id, week as year.week, title, how it starts):",
        _memory_lines(r["memories"]),
    ]
    # The app drops every empty line here, the intended blank separators included.
    return "\n".join(line for line in lines if line != "")


def parse_json_loose(text: str) -> Any:
    """parseJsonLoose: strip ``` fences, else take the outermost {...}. Raises ValueError."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", str(text or "").strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except ValueError:
        pass
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except ValueError:
            pass
    raise ValueError("The model did not return valid JSON.")


def clean_draft(parsed: Any, r: dict) -> dict:
    """cleanDraft: keep only real ids, each once, and the member's own chapters as they are.

    This is what the member would actually see, so the checks score it as well as the raw answer.
    """
    memory_ids = {m["id"] for m in r["memories"]}
    kept_ids = {c["id"] for c in r["chapters"]}
    in_kept = {i for c in r["chapters"] for i in c["entryIds"]}
    used, kept_seen, chapters = set(), set(), []
    items = parsed.get("chapters") if isinstance(parsed, dict) else None
    for item in items if isinstance(items, list) else []:
        if len(chapters) >= MAX_CHAPTERS or not isinstance(item, dict):
            continue
        if isinstance(item.get("keep"), str):
            if item["keep"] in kept_ids and item["keep"] not in kept_seen:
                kept_seen.add(item["keep"])
                chapters.append({"keep": item["keep"]})
            continue
        title = _str(item.get("title"), 120)
        if not title:
            continue
        entry_ids = []
        raw_ids = item.get("entryIds")
        for i in raw_ids if isinstance(raw_ids, list) else []:
            if isinstance(i, str) and i in memory_ids and i not in in_kept and i not in used:
                used.add(i)
                entry_ids.append(i)
        chapters.append({"title": title, "note": _str(item.get("note"), 500), "entryIds": entry_ids})
    suggested = parsed.get("bookType") if isinstance(parsed, dict) else None
    return {
        "task": "draft",
        "bookType": suggested
        if not r["bookType"] and isinstance(suggested, str) and suggested in BOOK_TYPES
        else None,
        "chapters": chapters,
    }


def request_for(case: dict, memoir: dict, model: str) -> dict:
    """The server-side request for one case: what the prompt and the checks work from."""
    return clean_request(client_body(case, memoir, model))
