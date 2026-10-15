# What the harder cases say (2026-10-15)

Gemini 4 Argon, the model Kairos uses by default, drafted 9 Outlines on the three harder Danny
cases, three runs each. Gemini 3.8 Flash read every draft as the judge. The run took about a minute
and cost $0.29. The full scores are in [report.md](report.md).

## The short version

**Argon scored 99 out of 100 again, with no rule breaks in 9 drafts.** The two cases built to trip
up the structure scored 100 in every run. The weak spot showed up where the first run couldn't
find one: on the big three-generation memoir, Argon writes **true facts the memories never state**
into its chapter notes. These cases can now tell a good draft from a great one.

## What it got right

- **It kept the member's chapters, even the ones that don't fit (3 of 3).** Danny I's member wrote
  four chapters the memories don't support: two with nothing behind them, one asking for Bill
  without Bill's memory, one with the wrong year. Every draft returned all four exactly as written.
- **Every version of a shared moment in one chapter (3 of 3).** Nine moments are told by two or
  three Dannys and arrive far apart, some disagreeing on details or the year. Argon gathered each
  moment's versions together every time.
- **Every rule, every time (9 of 9):** valid JSON, no made-up memory ids, no memory in two chapters.
- **It left out the noise (6 of 6)** and told the family memoir in time order (3 of 3), with every
  year it named matching the memories.

## The misses: all on `danny-family-life` (96)

- **It adds what it knows.** Two drafts name the "101st Airborne" and one names "Pakistan". Both are
  true in history: Easy Company of the 506th served in the 101st, and Abbottabad is in Pakistan. But
  the memories never say either. In a memoir, the member's own words are the source, so the agent
  shouldn't add facts, even correct ones. The judge flagged 3 of 9 drafts; "Sticks to the facts"
  scored 83 on this case.
- **One split birth (run 1).** Danny II's birth is told twice: by his father ("My son", 1947) and by
  himself ("Born", 1947). Run 1 put them in different chapters, and its "Dad's War: The Frogmen"
  chapter ran from his 1947 birth to his 1987 retirement.

## What the scores don't show

- **The estimate ran low.** Priced at "likely $0.21"; it cost $0.29. The judge reads all 79
  memories for the family case, so its readings were longer than the 1,000-token guess. Still far
  under the $1.12 cap.
- **Bigger memoir, slower draft.** The 79-memory case took about 18 seconds per draft; the smaller
  two took 5 to 9.

## Next, if wanted

- Tell the prompt plainly not to add names, places or units the memories don't mention, then re-run
  these three cases (about $0.30) to see if the outside facts stop.
