# What the first run says (2026-10-15)

Gemini 4 Argon, the model Kairos uses by default, drafted 18 Outlines: six made-up memoir cases,
three runs each. A second model, Gemini 3.8 Flash, read every draft as the judge. The run took
under four minutes and cost $0.27. The full scores are in [report.md](report.md).

## The short version

**Argon scored 99 out of 100.** In 18 drafts it broke none of the prompt's rules, and the judge
found nothing made up. On these cases it plans a book the way a careful editor would. That is also
this run's limit: the cases are too easy to tell a good draft from a great one.

## What it got right

- **Every rule, every time (18 of 18).** It always gave the app valid JSON. It used no memory ids
  that don't exist and put no memory in two chapters. It returned the two chapters the member wrote
  in June's book exactly once, in all three runs. When the member had already picked a kind of
  book, it answered `null` as asked.
- **It left out the noise.** In all 15 drafts that had mundane notes mixed in, every one stayed
  out of the book: car registration, phone plan, Wi-Fi password, dentist, furnace filter.
- **It suggested the right kind of book when it had to guess (6 of 6):** a resilience story for the
  flooded bakery, a life memoir for Ida.
- **It put things back in order.** Ida's memories arrived shuffled; every draft told her life in
  time order.
- **The Focus changes the plan.** The same memories, planned as a life memoir, open with "Growing
  Up in Larkspur Bend". Planned as a resilience story, they become "What We Built Together", "The
  Long Goodbye" and "The Empty Side of the Bed", and Rosa's childhood is left out, as it should be.
- **It matches the member's style.** June wrote her own chapter titles in sentence case ("Your
  first hire"), and Argon wrote its titles for her book the same way. Everywhere else it used
  Title Case.
- **It's consistent.** Drafts barely change from run to run. Rosa's life memoir has the same first
  three chapter titles in all three runs.

## The one miss

June, run 1: "Marcus runs a crew" went into "Taking care of your people", away from "Selling to
Marcus". The answer key wanted those two together, but Argon's choice is defensible.

## What the scores don't show

- **The chapters are big.** Books got 3 to 7 chapters: Rosa's whole life in 5 or 6, Ida's in 4.
  That's within the prompt's 3 to 12, but a coarse plan for a long life.
- **Speed varies a lot.** A typical draft took 8 seconds; the slowest took 78. Four drafts ran at
  once, so some of that wait may be queueing on Google's side.
- **The judge is generous.** It gave all 18 drafts 5 out of 5 and found no unsupported claims. It
  isn't blind, though. On drafts with planted problems it dropped to 1 out of 5 and caught the
  made-up car crash, the invented name "Ruben" and the invented Navy career. It catches bad drafts
  but can't rank good ones against each other.
- **The checker needed one fix.** The first scoring flagged five ordinary words ("Paid", "Owed",
  "Letting", "Goodbye") as possible made-up names, because the word list was missing some past
  tenses. That's fixed and covered by a test, and the run was re-scored for free: "Sticks to the
  facts" went from 97 to 100. The self-test still catches the planted names.

## Next, if wanted

- Harder cases: much larger memoirs, memories that contradict each other, and member chapters
  that don't fit the memories.
- The Outline's other jobs: placing new memories into an existing Outline, and edits from the chat.
- Gemini 3.8 Flash (the app's Quick option) on the same cases, about $0.30, to see what the
  cheaper model gives up.
