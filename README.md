# kairos-evals

[![tests](https://github.com/RoboStudioDev/kairos-evals/actions/workflows/tests.yml/badge.svg)](https://github.com/RoboStudioDev/kairos-evals/actions/workflows/tests.yml)

Scores the AI in [Kairos](https://kairosloom.life), a memoir app. Kairos's ghost writing agent
reads a member's memories and drafts an **Outline** for their book: the chapters, what each one
is about, and which memories go in it. This kit checks those drafts against **made-up memoirs**
and writes a scored report.

Plain Python with no packages to install. Every memoir here is invented. No real member's data
is used, and none ever leaves the app.

## What a good Outline draft is

Each draft gets a score out of 100, averaged over four areas:

| Area | What it checks | How |
|---|---|---|
| **Follows the rules** | The answer is valid JSON. It uses only memories it was given, puts each memory in at most one chapter, keeps the chapters the member wrote, answers the book type the way it was asked, and keeps chapter count, titles and notes within their limits. | Python |
| **Sensible chapters** | The memories that matter got placed. Noise ("Renewed the car registration") stayed out. Memories of the same event share a chapter, far-apart parts of a life don't, and a life memoir runs in time order. | Python, against an answer key written for each memoir |
| **Sticks to the facts** | Years in titles and notes match the memories. No names or places the memories never mention. No other claims the memories don't support. | Python for years and names; a second model (the *judge*) for everything else |
| **Fits the Focus** | The kind of book suggested when the member hadn't chosen. Whether switching *Life memoir* to *Resilience story* actually changes the plan. Whether the titles and notes fit the chosen kind of book and reader. | Python; the judge rates fit from 1 to 5 |

A **rule break** is any miss on the first area. The app quietly repairs some of these (it
drops memory ids the model made up), but a miss still means the model didn't do what it was told.

## The made-up memoirs

Five invented people in `fixtures/`, giving six cases:

| Case | What it tests |
|---|---|
| `rosa-life` | A whole life, 23 memories, as a life memoir for her grandchildren. Two mundane notes mixed in. |
| `rosa-resilience` | The same memories as a resilience story. Paired with the case above: the plan should change. |
| `ezra-not-chosen` | A bakery flooded and rebuilt. No book type chosen, so the agent should suggest *resilience*. |
| `june-selfhelp-kept` | Self-help for young business owners. The member wrote two chapters herself; both must come back untouched. |
| `abel-four-memories` | Only four memories, book type *Other* in the member's own words. A few chapters, nothing invented. The father is never named. |
| `ida-shuffled` | A whole life, but the memories arrive out of order, with no book type and no reader named. |

Each fixture file holds the memories, the member's settings, and the answer key: which memories
belong together, which parts of the life they come from, and which notes are noise.

## How to run it

You need Python 3.9 or newer (a Mac already has it). Get a copy and go into its folder:

```bash
git clone https://github.com/RoboStudioDev/kairos-evals.git
```

```bash
cd kairos-evals
```

**Free: prove the checks work.** Scores hand-written drafts, some clean and some with planted
mistakes, and fails if any check misses a mistake or raises a false alarm:

```bash
python3 -m kairos_evals selftest
```

**Free: the unit tests.**

```bash
python3 -m unittest
```

**Free: price a run.** Uses Google's token counter, which doesn't run the model:

```bash
python3 -m kairos_evals estimate
```

**Costs money: run it.** Without `--yes` it only prints the price. With `--yes` it drafts every
case, has the judge read each draft, saves every answer under `runs/`, and writes `report.md`
next to them. It stops itself before spending more than the "at most" price, or `--max-usd`.

```bash
python3 -m kairos_evals run --yes
```

Smaller runs: `--models argon` (one model), `--repeats 1`, `--no-judge`, `--cases rosa-life`.

**Free: re-score a saved run** after changing a check:

```bash
python3 -m kairos_evals score runs/<the run's folder>
```

Model runs call Gemini on Google Cloud (Vertex AI), the same models the app uses. The sign-in
comes from Google's `gcloud` tool (`gcloud auth login`). The project is gcloud's default, or
`--project`. No key is stored in this repository.

## What a run costs

Priced on 2026-10-15 with Google's token counter, for the six cases. Prices are in
`kairos_evals/pricing.py`:

| Run | Calls | Likely | At most |
|---|---|---|---|
| Full: both models × 3 repeats, with the judge (the default) | 76 | $0.82 | $3.99 |
| Argon only × 3 repeats, with the judge | 40 | $0.34 | $2.25 |
| Argon only × 3 repeats, no judge | 18 | $0.12 | $1.52 |
| Argon only × 1 run, no judge | 6 | $0.04 | $0.51 |

"Likely" uses the output measured on 2026-10-15, rounded up, with the models' thinking included:
about 400 tokens per Argon draft, 2,000 per Flash draft (Flash thinks before it answers; Argon
doesn't) and 1,000 per judge reading. "At most" is every call using its whole output allowance,
the most Google can bill. The two real runs cost $0.27 (Argon) and $0.47 (Flash).

## Sample reports

Every raw answer is kept next to each report, so any of them can be re-scored for free.

- [`reports/2026-10-15-argon/`](reports/2026-10-15-argon/): the first real run, 18 Outline
  drafts from Gemini 4 Argon. [What the scores say](reports/2026-10-15-argon/README.md).
- [`reports/2026-10-15-argon-vs-flash/`](reports/2026-10-15-argon-vs-flash/): Argon against
  Gemini 3.8 Flash on the same cases. Quality is a near tie, but on this task the "Quick" model
  was twice as slow and three times the cost. [The comparison](reports/2026-10-15-argon-vs-flash/README.md).

## How it stays honest

- **Same prompt as the app.** `kairos_evals/prompt.py` is a line-by-line copy of how Kairos
  builds the request, the prompt, and the clean-up of the model's answer. `python3 -m kairos_evals
  parity --app <the app's folder>` runs the app's own JavaScript on every case and confirms they
  match word for word.
- **The checks are tested.** `selftest` must catch every planted mistake and stay quiet on clean
  drafts. The planted drafts are in `examples/planted/`, and each one lists what it hides.
- **The judge is tested.** Every run with the judge also has it grade planted drafts next to
  clean ones. The report says whether it told them apart.
- **Runs repeat.** The model answers differently each time, so each case runs several times, and
  the report shows the lowest and highest runs.
- **Every answer is kept.** Raw answers are saved before scoring, so a change to a check can be
  re-scored for free.

## Limits

- The answer keys are one person's judgment of where memories belong. They test only clear-cut
  calls, like the same event or decades apart.
- The names check uses the computer's dictionary (built into macOS; the `wamerican` package on
  Ubuntu), so results can differ slightly between computers. A name that is also a common word
  ("Rose", "June") gets past it. The judge is there to catch those.
- The judge is a Gemini model grading Gemini's work, so it may go easy on it. The judge self-test
  keeps an eye on that, but a person should still read the drafts. The report includes them.
- Only the first draft is covered so far. Placing new memories into an existing Outline, and
  editing it from the chat, aren't scored yet.

## Files

```
fixtures/            the made-up memoirs, their answer keys and cases
examples/reference/  hand-written clean drafts (the self-test's "should pass")
examples/planted/    drafts with planted mistakes (the self-test's "must be caught")
kairos_evals/
  prompt.py          the app's request, prompt and answer clean-up, copied
  checks.py          the checks and scoring
  judge.py           the second model's instructions and how its answer is read
  gemini.py          calling Gemini on Vertex AI (plain HTTPS, gcloud sign-in)
  pricing.py         prices per model
  run.py             planning, pricing, running and scoring a run
  report.py          the Markdown report
  selftest.py        testing the checks
  parity.py          comparing the prompt with the app's code
tests/               unit tests (python3 -m unittest)
.github/workflows/   the same free checks on every push
reports/             reports worth keeping
```

## Licence

MIT. See [LICENSE](LICENSE).
