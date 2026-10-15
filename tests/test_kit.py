"""Unit tests. Run with:  python3 -m unittest   (no model calls, nothing to install)."""

from __future__ import annotations

import json
import os
import unittest
from datetime import date
from pathlib import Path

from kairos_evals import pricing
from kairos_evals.checks import member_view, name_like_words, score_draft, years_in
from kairos_evals.fixtures import load_cases, problems
from kairos_evals.prompt import (
    build_draft_prompt,
    clean_draft,
    parse_json_loose,
    request_for,
)
from kairos_evals.selftest import run_selftest

CASES = {c.id: c for c in load_cases()}


def req(case_id: str, model: str = "gemini-4-argon") -> dict:
    case = CASES[case_id]
    return request_for(dict(case.settings), case.memoir, model)


class Fixtures(unittest.TestCase):
    def test_fixtures_are_valid(self):
        self.assertEqual(problems(list(CASES.values())), [])

    def test_kept_memories_are_not_sent(self):
        sent = {m["id"] for m in req("june-selfhelp-kept")["memories"]}
        self.assertNotIn("jh02", sent)
        self.assertNotIn("jh08", sent)
        self.assertIn("jh01", sent)


class Prompt(unittest.TestCase):
    def test_prompt_matches_the_app_shape(self):
        prompt = build_draft_prompt(req("rosa-life"))
        self.assertIn("(powered by Gemini 4 Argon)", prompt)
        self.assertIn("The book: a life memoir: the whole life, more or less in order.", prompt)
        self.assertIn('- Set "bookType" to null.', prompt)
        self.assertIn("KEPT: []", prompt)
        self.assertNotIn("\n\n", prompt)  # the app drops its blank lines
        self.assertIn('{"id":"rv01","week":"1955.24","title":"Sorting heels in Papa\'s shop","start":', prompt)

    def test_unchosen_book_asks_for_a_suggestion(self):
        prompt = build_draft_prompt(req("ida-shuffled", "gemini-3.8-flash"))
        self.assertIn("The member has not chosen a kind of book yet.", prompt)
        self.assertIn("Who it is for: not said yet.", prompt)
        self.assertIn("(powered by Gemini 3.8 Flash)", prompt)

    def test_kept_chapters_are_listed(self):
        prompt = build_draft_prompt(req("june-selfhelp-kept"))
        self.assertIn('{"keep": "<its id>"}', prompt)
        self.assertIn('"id":"price-out-loud"', prompt)

    def test_other_book_type_quotes_the_member(self):
        prompt = build_draft_prompt(req("abel-four-memories"))
        self.assertIn('In their words: "Letters to my son about his grandfather".', prompt)

    @unittest.skipUnless(os.environ.get("KAIROS_APP_DIR"), "set KAIROS_APP_DIR to compare with the app's code")
    def test_parity_with_the_app(self):
        from kairos_evals.parity import run_parity

        ok, notes = run_parity(Path(os.environ["KAIROS_APP_DIR"]).expanduser())
        self.assertTrue(ok, notes)


class Cleanup(unittest.TestCase):
    def test_parse_json_loose(self):
        self.assertEqual(parse_json_loose('```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(parse_json_loose('Here you go: {"a": 1} hope it helps'), {"a": 1})
        with self.assertRaises(ValueError):
            parse_json_loose("no json here")

    def test_clean_draft_drops_made_up_and_repeated_ids(self):
        r = req("rosa-life")
        out = clean_draft({"bookType": "life", "chapters": [
            {"title": "A", "entryIds": ["rv01", "rv99", "rv01"]},
            {"title": "  ", "entryIds": ["rv02"]},
            {"title": "B", "entryIds": ["rv01", "rv02"]},
        ]}, r)
        self.assertIsNone(out["bookType"])  # the member already chose
        self.assertEqual([c["entryIds"] for c in out["chapters"]], [["rv01"], ["rv02"]])

    def test_dropped_member_chapter_comes_back(self):
        case = CASES["june-selfhelp-kept"]
        r = req(case.id)
        view = member_view(case, r, clean_draft({"chapters": [{"keep": "price-out-loud"}, {"title": "X", "entryIds": ["jh01"]}]}, r))
        self.assertEqual([c["title"] for c in view], ["Lesson one: say the price out loud", "Your first hire", "X"])


class Checks(unittest.TestCase):
    def test_years_and_decades(self):
        self.assertEqual(years_in("The 1970s, and 1984"), [("1970s", 1970, 1979), ("1984", 1984, 1984)])
        self.assertEqual(years_in("back in the '80s")[0][2], 80)

    def test_names_skip_sentence_starts_in_notes(self):
        self.assertEqual(name_like_words("Meeting Ted at the laundromat. Then Hattie.", sentence_case=True), ["Ted", "Hattie"])
        self.assertEqual(name_like_words("Grief came. Hattie helped.", sentence_case=True), [])
        self.assertEqual(name_like_words("Summers at Lake Tahoe", sentence_case=False), ["Summers", "Lake", "Tahoe"])

    def test_ordinary_words_are_not_names(self):
        # False alarms from the first real run (2026-10-15): all ordinary words.
        from kairos_evals.checks import _known

        for word in ("Paid", "Owed", "Letting", "Goodbye", "Stepping", "Weathering"):
            self.assertTrue(_known(word, set()), word)
        for word in ("Tahoe", "Ruben"):
            self.assertFalse(_known(word, set()), word)

    def test_unreadable_answer_scores_zero(self):
        case = CASES["abel-four-memories"]
        s = score_draft(case, req(case.id), "Sorry, I can't do that.")
        self.assertFalse(s.usable)
        self.assertEqual(s.overall, 0.0)

    def test_selftest_passes(self):
        ok, text = run_selftest(list(CASES.values()))
        self.assertTrue(ok, text)


class Pricing(unittest.TestCase):
    def test_argon_price_changes_after_launch(self):
        self.assertAlmostEqual(pricing.cost("gemini-4-argon", 1_000_000, 0, date(2026, 11, 30)), 2.00)
        self.assertAlmostEqual(pricing.cost("gemini-4-argon", 0, 1_000_000, date(2026, 12, 1)), 20.00)


if __name__ == "__main__":
    unittest.main()
