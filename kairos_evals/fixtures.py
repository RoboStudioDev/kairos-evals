"""The made-up memoirs in ``fixtures/`` and their answer keys.

Each fixture file is one invented person: their memories (what the app would send), an answer
key written by hand, and one or more cases (the member's settings for one draft). Nothing here
comes from a real Kairos member.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .prompt import BOOK_TYPES, COORD_RE

ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = ROOT / "fixtures"


@dataclass
class Case:
    id: str
    about: str
    memoir: dict
    settings: dict  # bookType, bookTypeOther, audience, keptChapters
    must_place: list[str]
    together: list[list[str]]
    eras: list[list[str]]  # ordered; empty when the case doesn't judge "kept apart"
    noise: list[str]
    chronological: bool
    book_type: list[str] | None  # accepted suggestions when the member hasn't chosen
    min_chapters: int
    max_chapters: int
    focus_pair: str | None = None
    memory_by_id: dict = field(default_factory=dict)


def load_cases(folder: Path = FIXTURES_DIR) -> list[Case]:
    cases = []
    for path in sorted(folder.glob("*.json")):
        memoir = json.loads(path.read_text(encoding="utf-8"))
        key = memoir["answerKey"]
        all_ids = [m["id"] for m in memoir["memories"]]
        for c in memoir["cases"]:
            exp = c["expect"]
            kept_ids = {i for k in c.get("keptChapters", []) for i in k["entryIds"]}
            sent = [i for i in all_ids if i not in kept_ids]
            must = exp["mustPlace"]
            if must == "all":
                must = [i for i in sent if i not in key["noise"]]
            together = key["scenes"] if exp["together"] == "scenes" else exp["together"]
            n_sent = len(sent)
            cases.append(
                Case(
                    id=c["id"],
                    about=c["about"],
                    memoir=memoir,
                    settings={
                        "bookType": c.get("bookType"),
                        "bookTypeOther": c.get("bookTypeOther", ""),
                        "audience": c.get("audience", ""),
                        "keptChapters": c.get("keptChapters", []),
                    },
                    must_place=must,
                    together=together,
                    eras=key["eras"] if exp.get("apartByEra") else [],
                    noise=key["noise"],
                    chronological=bool(exp.get("chronological")),
                    book_type=exp.get("bookType"),
                    min_chapters=exp.get("minChapters", 3 if n_sent >= 6 else 1),
                    max_chapters=exp.get("maxChapters", 12),
                    focus_pair=c.get("focusPair"),
                    memory_by_id={m["id"]: m for m in memoir["memories"]},
                )
            )
    return cases


def problems(cases: list[Case]) -> list[str]:
    """Anything wrong with the fixtures themselves (empty list = fine)."""
    out = []
    seen_case = set()
    for case in cases:
        where = case.id
        if case.id in seen_case:
            out.append(f"{where}: duplicate case id")
        seen_case.add(case.id)
        ids = [m["id"] for m in case.memoir["memories"]]
        if len(ids) != len(set(ids)):
            out.append(f"{where}: duplicate memory ids")
        for m in case.memoir["memories"]:
            if not COORD_RE.fullmatch(m["coordinate"]):
                out.append(f"{where}: bad week {m['coordinate']!r} on {m['id']}")
            if len(m["body"]) > 280:
                out.append(f"{where}: {m['id']} is longer than the 280 characters the app sends")
        known = set(ids)
        named = (
            case.must_place
            + case.noise
            + [i for g in case.together for i in g]
            + [i for g in case.eras for i in g]
            + [i for k in case.settings["keptChapters"] for i in k["entryIds"]]
        )
        for i in named:
            if i not in known:
                out.append(f"{where}: answer key names unknown memory {i}")
        if case.settings["bookType"] is not None and case.settings["bookType"] not in BOOK_TYPES:
            out.append(f"{where}: unknown bookType")
        if case.book_type and case.settings["bookType"]:
            out.append(f"{where}: expects a suggestion although the member already chose")
    pairs = {c.id: c.focus_pair for c in cases if c.focus_pair}
    for a, b in pairs.items():
        if pairs.get(b) != a:
            out.append(f"{a}: focus pair {b} doesn't point back")
    return out
