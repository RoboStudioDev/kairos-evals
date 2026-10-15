# Argon vs Flash on the same Outline cases (2026-10-15)

Kairos lets members choose the model behind its ghost writing agent: Gemini 4 Argon (the
default) or Gemini 3.8 Flash (the "Quick" option). Both drafted the same six made-up memoir cases,
three times each, and the same judge (Gemini 3.8 Flash) read all 36 drafts. The two runs cost
$0.74 together. The full scores are in [report.md](report.md).

## The short version

| | Gemini 4 Argon | Gemini 3.8 Flash |
|---|---|---|
| Overall score | **99** | **98** |
| Rule breaks | 0 of 18 | 0 of 18 |
| Unsupported claims (judge) | 0 | 1 |
| Typical time per draft (slowest) | **8 s** (78 s) | 18 s (97 s) |
| Thinking tokens per draft | 0 | ~1,550 |
| Cost per draft | **$0.005** | $0.016 |

**On Outline drafts the "Quick" model is neither quicker nor cheaper.** Flash plans about as
well as Argon, but before answering it thinks through about 1,550 tokens, which Google bills as
output. Argon answers straight away. So Flash took twice as long and cost three times as much per
draft. List prices suggest the opposite, which is the point of measuring.

## Where they differ

- **Quality is a near tie.** Both followed every rule in all 18 drafts. Both left out every
  mundane note, suggested the right kind of book every time they had to guess, put shuffled
  memories back in time order, and changed the plan when the Focus changed.
- **Flash made one small factual slip.** In one bakery draft it wrote "Living with the river",
  but the memories are about a canal. The judge caught it; the deterministic checks can't, because
  "river" is an ordinary word.
- **Flash is more set in its ways.** In all three runs of June's self-help book it put "Marcus runs
  a crew" in a different chapter from "Selling to Marcus". Argon did that once in three. Both
  choices are defensible, but Flash never varied.

## What this doesn't show

- These are first drafts of an Outline, one kind of call. Chat replies or document reading might
  balance out differently.
- The app doesn't set a thinking budget, so neither does this eval. Flash with thinking turned
  down might be quick again; that would need its own run.
- The cases are still easy for both models (98–99). Harder cases are next.
