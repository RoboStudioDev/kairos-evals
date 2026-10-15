"""The checks: what a good Outline draft is, turned into scores.

A draft is scored in four areas. Each check gives a score from 0 to 1 (or "doesn't apply"); an
area's score is the average of its checks, and the draft's overall score is the average of its
areas, shown out of 100.

1. Follows the rules  - the hard rules in the prompt. Anything under full marks is a rule break.
2. Sensible chapters  - memories land where a person would put them (checked against the answer
                        key written for each made-up memoir).
3. Sticks to the facts - no dates, names or claims the memories don't support.
4. Fits the Focus     - the plan reads like the kind of book the member chose.

Checks marked "judge" need a second model to read the draft (see judge.py). Everything else is
plain Python and free to run.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from itertools import combinations
from pathlib import Path
from statistics import median
from typing import Any

from .fixtures import Case
from .prompt import BOOK_TYPES, clean_draft, parse_json_loose

AREAS = {
    "rules": "Follows the rules",
    "chapters": "Sensible chapters",
    "facts": "Sticks to the facts",
    "focus": "Fits the Focus",
}

TITLE_MAX = 60  # "Chapter titles: short and plain, under 60 characters."
NOTE_MAX = 140  # "Notes: one line under 140 characters"
FOCUS_OVERLAP_MAX = 0.5


@dataclass
class Check:
    id: str
    area: str
    label: str
    score: float | None  # None = doesn't apply to this case
    hard: bool = False
    details: list[str] = field(default_factory=list)


@dataclass
class DraftScore:
    case: str
    model: str
    repeat: int
    usable: bool
    checks: list[Check]
    areas: dict[str, float | None]
    overall: float | None
    rule_breaks: int
    chapters: list[dict]  # what the member would see: title, note, memory ids, kept?
    book_type: str | None
    cost: float = 0.0
    seconds: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None  # thinking included
    thinking_tokens: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


# ── Helpers ──────────────────────────────────────────────────────────────────────────────────


def coord_key(coordinate: str) -> int:
    """coordinateKey in the app: year·week·day as one sortable number."""
    parts = [int(p) for p in coordinate.split(".")] + [0, 0]
    return parts[0] * 1000 + parts[1] * 10 + parts[2]


def member_view(case: Case, r: dict, cleaned: dict) -> list[dict]:
    """The chapters the member would end up with (applyDraft): kept chapters come back untouched,
    and go back where they were if the draft dropped them."""
    kept = {c["id"]: c for c in case.settings["keptChapters"]}
    view, placed_kept = [], set()
    for item in cleaned["chapters"]:
        if "keep" in item:
            c = kept[item["keep"]]
            view.append({"title": c["title"], "note": c.get("note", ""), "ids": list(c["entryIds"]), "kept": True})
            placed_kept.add(c["id"])
        else:
            view.append({"title": item["title"], "note": item["note"], "ids": item["entryIds"], "kept": False})
    for i, c in enumerate(case.settings["keptChapters"]):
        if c["id"] not in placed_kept:
            view.insert(min(i, len(view)), {"title": c["title"], "note": c.get("note", ""), "ids": list(c["entryIds"]), "kept": True})
    return view


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _name(case: Case, memory_id: str) -> str:
    m = case.memory_by_id.get(memory_id)
    return f"'{m['title']}'" if m else memory_id


# Words that look like names to the "made-up names" check unless we know better. A dictionary is
# used when the computer has one (/usr/share/dict/words on macOS and most Linux); this short list
# covers the basics when it doesn't.
COMMON_WORDS = set(
    """a an the and or but of in on at to for from with by as into over under after before about
    my our your his her their its we us me you he she they it this that these those who what when
    where why how all one two three first last new old early late later years year days day life home
    family love loss work school mom dad mama papa mother father grandma grandpa son daughter brother
    sister husband wife friend friends kids children part chapter prologue epilogue lessons lesson
    story beginning beginnings end again back still ever never goodbye okay online email""".split()
)
# Past tenses the dictionary lists only as their present form ("paid" -> "pay").
IRREGULAR = dict(
    pair.split(":")
    for pair in """paid:pay said:say laid:lay made:make kept:keep left:leave lost:lose built:build
    found:find felt:feel took:take gave:give came:come went:go ran:run grew:grow knew:know held:hold
    met:meet taught:teach brought:bring thought:think bought:buy sold:sell told:tell won:win
    fought:fight stood:stand understood:understand began:begin begun:begin wrote:write written:write
    broke:break broken:break fell:fall fallen:fall""".split()
)
_DICT_PATH = Path("/usr/share/dict/words")
_dictionary: set[str] | None = None


def dictionary() -> set[str]:
    """Lower-case dictionary words (proper nouns in the dictionary are left out)."""
    global _dictionary
    if _dictionary is None:
        words = set()
        if _DICT_PATH.exists():
            for line in _DICT_PATH.read_text(encoding="utf-8", errors="ignore").split():
                if line.islower():
                    words.add(line)
        _dictionary = words
    return _dictionary


def dictionary_in_use() -> bool:
    return bool(dictionary())


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def _stems(word: str) -> list[str]:
    w = word.lower().replace("’", "'")
    w = re.sub(r"'s$", "", w).strip("'-")
    out = [w]
    if w in IRREGULAR:
        out.append(IRREGULAR[w])
    for suffix, repl in (("ies", "y"), ("es", ""), ("s", ""), ("ing", ""), ("ing", "e"), ("ed", ""), ("ed", "e"), ("ers", ""), ("er", "")):
        stem = w[: -len(suffix)] + repl
        if w.endswith(suffix) and len(stem) >= 3:
            out.append(stem)
            if not repl and len(stem) >= 4 and stem[-1] == stem[-2]:
                out.append(stem[:-1])  # "letting" -> "lett" -> "let"
    out.extend(part for part in w.split("-") if part)
    return out


def _known(word: str, vocab: set[str]) -> bool:
    words = dictionary()
    return any(s in vocab or s in COMMON_WORDS or s in words for s in _stems(word))


def source_vocab(case: Case, r: dict) -> set[str]:
    """Every word the agent was given: the memories it saw, the member's chapters and settings."""
    texts = [m["title"] + " " + m["text"] for m in r["memories"]]
    texts += [c["title"] + " " + c.get("note", "") for c in case.settings["keptChapters"]]
    texts += [case.settings["audience"], case.settings["bookTypeOther"]]
    vocab = set()
    for t in texts:
        for w in WORD_RE.findall(t):
            vocab.update(_stems(w))
    return vocab


def name_like_words(text: str, sentence_case: bool) -> list[str]:
    """Capitalized words. In a sentence (a note), the first word of each sentence is skipped."""
    out = []
    for sentence in re.split(r"(?<=[.!?:;])\s+", text) if sentence_case else [text]:
        words = WORD_RE.findall(sentence)
        for i, w in enumerate(words):
            if sentence_case and i == 0:
                continue
            if w[0].isupper() and len(w) > 1:
                out.append(w)
    return out


YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)(s)?\b")
SHORT_DECADE_RE = re.compile(r"['’](\d)0s\b")


def years_in(text: str) -> list[tuple[str, int, int]]:
    """Years and decades in a piece of text, as (as written, first year, last year)."""
    found = []
    for m in YEAR_RE.finditer(text):
        y = int(m.group(1))
        found.append((m.group(0), y, y + 9 if m.group(2) else y))
    for m in SHORT_DECADE_RE.finditer(text):
        found.append((m.group(0), -1, int(m.group(1)) * 10))  # '70s: century unknown
    return found


STOP = set("a an the and or of in on at to for from with my our your his her their is are".split())


def title_words(chapters: list[dict]) -> set[str]:
    words = set()
    for c in chapters:
        if c.get("kept"):
            continue
        for w in WORD_RE.findall(c["title"].lower()):
            if w not in STOP:
                words.update(_stems(w)[:1])
    return words


def focus_overlap(a: list[dict], b: list[dict]) -> float | None:
    """How much two drafts' chapter titles share, 0 to 1 (Jaccard on title words)."""
    wa, wb = title_words(a), title_words(b)
    if not wa or not wb:
        return None
    return len(wa & wb) / len(wa | wb)


# ── Scoring one draft ────────────────────────────────────────────────────────────────────────


def score_draft(
    case: Case,
    r: dict,
    raw_text: str | None,
    *,
    model: str = "",
    repeat: int = 1,
    error: str | None = None,
    judge: dict | None = None,
    pair_view: list[dict] | None = None,
) -> DraftScore:
    checks: list[Check] = []
    parsed: Any = None
    problem = error
    if problem is None:
        try:
            parsed = parse_json_loose(raw_text or "")
            if not isinstance(parsed, dict) or not isinstance(parsed.get("chapters"), list):
                problem = "The answer has no list of chapters."
        except ValueError as exc:
            problem = str(exc)
    checks.append(
        Check("valid_answer", "rules", "Gave an answer the app can read (JSON with chapters)",
              0.0 if problem else 1.0, hard=True, details=[problem] if problem else [])
    )
    if problem:
        return DraftScore(case.id, model, repeat, False, checks,
                          {a: 0.0 for a in AREAS}, 0.0, 1, [], None)

    sent_ids = {m["id"] for m in r["memories"]}
    raw_items = [c for c in parsed["chapters"] if isinstance(c, dict)]
    new_items = [c for c in raw_items if "keep" not in c]
    raw_ids = [i for c in new_items for i in (c.get("entryIds") if isinstance(c.get("entryIds"), list) else [])]

    # 1 · Follows the rules ─────────────────────────────────────────────────────────────────
    invented = [i for i in raw_ids if i not in sent_ids]
    checks.append(Check(
        "real_memories_only", "rules", "Used only memories it was given (no made-up memory ids)",
        1.0 - len(invented) / len(raw_ids) if raw_ids else 1.0, hard=True,
        details=[f"made-up id {i!r}" for i in invented]))

    real = [i for i in raw_ids if i in sent_ids]
    dupes = sorted({i for i in real if real.count(i) > 1})
    checks.append(Check(
        "each_memory_once", "rules", "Put each memory in at most one chapter",
        1.0 - (len(real) - len(set(real))) / len(real) if real else 1.0, hard=True,
        details=[f"{_name(case, i)} appears {real.count(i)} times" for i in dupes]))

    kept = case.settings["keptChapters"]
    if kept:
        keep_refs = [c["keep"] for c in raw_items if "keep" in c]
        details = [f"member's chapter '{k['title']}' appears {keep_refs.count(k['id'])} times"
                   for k in kept if keep_refs.count(k["id"]) != 1]
        details += [f"unknown kept chapter {k!r}" for k in keep_refs if k not in {c['id'] for c in kept}]
        good = sum(keep_refs.count(k["id"]) == 1 for k in kept)
        checks.append(Check("keeps_member_chapters", "rules",
                            "Kept each chapter the member wrote, exactly once", good / len(kept),
                            hard=True, details=details))
    else:
        checks.append(Check("keeps_member_chapters", "rules",
                            "Kept each chapter the member wrote, exactly once", None, hard=True))

    raw_type = parsed.get("bookType")
    if case.settings["bookType"]:
        ok = raw_type is None
        detail = [] if ok else [f"answered bookType {raw_type!r}; the member already chose, so it should be null"]
    else:
        ok = raw_type in BOOK_TYPES
        detail = [] if ok else [f"bookType {raw_type!r} is not one of {', '.join(BOOK_TYPES)}"]
    checks.append(Check("book_type_rule", "rules", "Book type answered the way the prompt asks",
                        1.0 if ok else 0.0, hard=True, details=detail))

    cleaned = clean_draft(parsed, r)
    view = member_view(case, r, cleaned)
    n_ch = len(view)
    count_ok = case.min_chapters <= n_ch <= case.max_chapters
    drafted = [c for c in view if not c["kept"]]  # the chapters the agent wrote
    long_titles = [c["title"] for c in drafted if len(c["title"]) >= TITLE_MAX]
    long_notes = [c["title"] for c in drafted if len(c["note"]) >= NOTE_MAX]
    parts = [1.0 if count_ok else 0.0]
    if drafted:
        parts += [1 - len(long_titles) / len(drafted), 1 - len(long_notes) / len(drafted)]
    details = []
    if not count_ok:
        details.append(f"{n_ch} chapters; expected {case.min_chapters} to {case.max_chapters}")
    details += [f"title over {TITLE_MAX} characters: '{t}'" for t in long_titles]
    details += [f"note over {NOTE_MAX} characters, in '{t}'" for t in long_notes]
    checks.append(Check("sizes", "rules", "Chapter count, title and note lengths within the limits",
                        _mean(parts), hard=True, details=details))

    # 2 · Sensible chapters ─────────────────────────────────────────────────────────────────
    chapter_of = {i: n for n, c in enumerate(view) for i in c["ids"]}
    placed = set(chapter_of)

    missing = [i for i in case.must_place if i not in placed]
    checks.append(Check("placed_what_matters", "chapters",
                        "Placed the memories this book needs",
                        1 - len(missing) / len(case.must_place) if case.must_place else None,
                        details=[f"left out {_name(case, i)}" for i in missing]))

    noise_in = [i for i in case.noise if i in placed and i in sent_ids]
    checks.append(Check("left_out_noise", "chapters",
                        "Left out notes that don't belong in a book (car registration, Wi-Fi)",
                        1 - len(noise_in) / len(case.noise) if case.noise else None,
                        details=[f"put {_name(case, i)} in '{view[chapter_of[i]]['title']}'" for i in noise_in]))

    pairs = [(a, b) for g in case.together for a, b in combinations(g, 2) if a in placed and b in placed]
    split = [(a, b) for a, b in pairs if chapter_of[a] != chapter_of[b]]
    checks.append(Check("together", "chapters",
                        "Kept memories of the same event or time in one chapter",
                        1 - len(split) / len(pairs) if pairs else None,
                        details=[f"split {_name(case, a)} and {_name(case, b)}" for a, b in split]))

    if case.eras:
        era_of = {i: n for n, g in enumerate(case.eras) for i in g}
        far = [(a, b) for a, b in combinations(sorted(era_of), 2)
               if abs(era_of[a] - era_of[b]) >= 2 and a in placed and b in placed]
        mixed = [(a, b) for a, b in far if chapter_of[a] == chapter_of[b]]
        checks.append(Check("apart", "chapters",
                            "Didn't mix far-apart parts of life in one chapter",
                            1 - len(mixed) / len(far) if far else None,
                            details=[f"{_name(case, a)} and {_name(case, b)} share '{view[chapter_of[a]]['title']}'"
                                     for a, b in mixed]))
    else:
        checks.append(Check("apart", "chapters", "Didn't mix far-apart parts of life in one chapter", None))

    if case.chronological:
        week = {i: coord_key(case.memory_by_id[i]["coordinate"]) for i in placed}
        mids = [(c["title"], median(week[i] for i in c["ids"])) for c in view if c["ids"]]
        between = [(a, b) for a, b in zip(mids, mids[1:])]
        backwards = [(a[0], b[0]) for a, b in between if b[1] < a[1]]
        inside = [(c["title"], a, b) for c in view for a, b in zip(c["ids"], c["ids"][1:])]
        out_of_order = [(t, a, b) for t, a, b in inside if week[b] < week[a]]
        parts = []
        if between:
            parts.append(1 - len(backwards) / len(between))
        if inside:
            parts.append(1 - len(out_of_order) / len(inside))
        details = [f"'{b}' comes after '{a}' but happened earlier" for a, b in backwards]
        details += [f"in '{t}', {_name(case, b)} is listed after {_name(case, a)} but happened earlier"
                    for t, a, b in out_of_order]
        checks.append(Check("time_order", "chapters", "Chapters and their memories in time order",
                            _mean(parts), details=details))
    else:
        checks.append(Check("time_order", "chapters", "Chapters and their memories in time order", None))

    # 3 · Sticks to the facts ───────────────────────────────────────────────────────────────
    source_text = " ".join([m["title"] + " " + m["text"] for m in r["memories"]] + [case.settings["audience"]])
    total, bad = 0, []
    for c in drafted:
        years = [case.memory_by_id[i]["coordinate"].split(".")[0] for i in c["ids"]]
        lo, hi = (int(min(years)), int(max(years))) if years else (None, None)
        for written, first, last in years_in(c["title"] + " " + c["note"]):
            total += 1
            if written in source_text:
                continue
            if first == -1:  # '70s: any century
                ok = lo is not None and any((y % 100) // 10 * 10 == last for y in range(lo, hi + 1))
            else:
                ok = lo is not None and first <= hi and last >= lo
            if not ok:
                span = f"{lo}-{hi}" if lo is not None else "no memories"
                bad.append(f"'{written}' in '{c['title']}' (its memories: {span})")
    checks.append(Check("dates_supported", "facts",
                        "Every year or decade it names matches the memories",
                        1 - len(bad) / total if total else None, details=bad))

    vocab = source_vocab(case, r)
    flagged = []
    for c in drafted:
        for w in name_like_words(c["title"], sentence_case=False) + name_like_words(c["note"], sentence_case=True):
            w = re.sub(r"['\u2019]s$", "", w)
            if not _known(w, vocab) and w not in flagged:
                flagged.append(w)
    checks.append(Check("no_new_names", "facts",
                        "No names or places that aren't in the memories (word check)",
                        max(0.0, 1 - 0.25 * len(flagged)),
                        details=[f"'{w}' isn't in the memories or the dictionary" for w in flagged]))

    # 4 · Fits the Focus ────────────────────────────────────────────────────────────────────
    if case.book_type and not case.settings["bookType"]:
        got = cleaned["bookType"]
        checks.append(Check("suggested_book_type", "focus",
                            "Suggested the right kind of book (when the member hadn't chosen)",
                            1.0 if got in case.book_type else 0.0,
                            details=[] if got in case.book_type else
                            [f"suggested {got!r}; expected {' or '.join(case.book_type)}"]))
    else:
        checks.append(Check("suggested_book_type", "focus",
                            "Suggested the right kind of book (when the member hadn't chosen)", None))

    if pair_view is not None:
        overlap = focus_overlap(view, pair_view)
        checks.append(Check(
            "focus_changes_plan", "focus",
            f"Changing the Focus changed the plan (paired case {case.focus_pair})",
            None if overlap is None else (1.0 if overlap <= FOCUS_OVERLAP_MAX else 0.0),
            details=[] if overlap is None else
            [f"chapter titles share {overlap:.0%} of their words with the {case.focus_pair} draft "
             f"(at most {FOCUS_OVERLAP_MAX:.0%} passes)"]))
    else:
        checks.append(Check("focus_changes_plan", "focus", "Changing the Focus changed the plan", None))

    if judge and not judge.get("error"):
        fit = judge["focusFit"]
        checks.append(Check("judge_focus_fit", "focus",
                            "Titles and notes fit the chosen Focus and reader (judge, 1-5)",
                            (fit - 1) / 4, details=[f"{fit}/5: {judge.get('focusReason', '')}"]))
        claims = judge.get("unsupported", [])
        checks.append(Check("judge_no_invented_facts", "facts",
                            "No claims the memories don't support (judge)",
                            max(0.0, 1 - 0.25 * len(claims)),
                            details=[f"'{c.get('claim', '')}' in '{c.get('chapter', '')}': {c.get('why', '')}"
                                     for c in claims]))
    else:
        why = [judge["error"]] if judge and judge.get("error") else []
        checks.append(Check("judge_focus_fit", "focus",
                            "Titles and notes fit the chosen Focus and reader (judge, 1-5)", None, details=why))
        checks.append(Check("judge_no_invented_facts", "facts",
                            "No claims the memories don't support (judge)", None, details=why))

    areas = {a: _mean([c.score for c in checks if c.area == a and c.score is not None]) for a in AREAS}
    overall = _mean([s for s in areas.values() if s is not None])
    rule_breaks = sum(1 for c in checks if c.hard and c.score is not None and c.score < 1)
    return DraftScore(case.id, model, repeat, True, checks, areas, overall, rule_breaks,
                      view, cleaned["bookType"])
