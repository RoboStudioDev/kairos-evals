# Kairos Outline drafts, scored (2026-10-15)

**What ran:** 3 made-up memoir cases × 1 model(s) × 3 run(s) = 9 Outline drafts, each read by a judge (Gemini 3.8 Flash).
**Cost:** $0.29 (drafts $0.12, judge $0.17). **When:** 2026-10-15T12:06:34 to 2026-10-15T12:07:34.

Scores are out of 100. Each draft is scored in four areas; its overall score is the average of the four. A *rule break* is any miss on a hard rule from the prompt. See [How to read this](#how-to-read-this).

## Scores by model

| Model | Overall | Follows the rules | Sensible chapters | Sticks to the facts | Fits the Focus | Drafts with a rule break | Seconds per draft (typical, slowest) | Cost per draft |
|---|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | **99** | 100 | 99 | 94 | 100 | 0 of 9 | 8, 18 | $0.0133 |

## Scores by case

Overall is the average across runs, with the lowest and highest run in brackets.

| Case | Model | Overall (low–high) | Follows the rules | Sensible chapters | Sticks to the facts | Fits the Focus |
|---|---|---|---|---|---|---|
| danny-family-life | Gemini 4 Argon | **96** (94–97) | 100 | 99 | 83 | 100 |
| danny-i-kept-misfits | Gemini 4 Argon | **100** (100–100) | 100 | 100 | 100 | 100 |
| danny-shared-versions | Gemini 4 Argon | **100** (100–100) | 100 | 100 | 100 | 100 |

What each case tests:

- **danny-family-life** — Three generations as one life memoir: 79 memories arriving in three blocks (Danny III's, then his father's, then his grandfather's), four noise notes, a birth and two deaths each told twice, and echoes across decades that tempt chapters by theme.
- **danny-i-kept-misfits** — Danny I's war as a resilience story, with four chapters the member wrote that don't fit the memories: two with no memories behind them, one asking for Bill without his memory, one with the wrong year. All four must come back untouched.
- **danny-shared-versions** — Nine moments told by two or three Dannys, grouped by person, so versions of one moment arrive far apart. Some versions disagree, one of them on the year. Every version of a moment belongs in one chapter.

## Every check

Average score, and how many drafts got full marks, where the check applies.

| Area | Check | Gemini 4 Argon |
|---|---|---|
| Follows the rules | Gave an answer the app can read (JSON with chapters) | 100 (9/9) |
| Follows the rules | Used only memories it was given (no made-up memory ids) | 100 (9/9) |
| Follows the rules | Put each memory in at most one chapter | 100 (9/9) |
| Follows the rules | Kept each chapter the member wrote, exactly once | 100 (3/3) |
| Follows the rules | Book type answered the way the prompt asks | 100 (9/9) |
| Follows the rules | Chapter count, title and note lengths within the limits | 100 (9/9) |
| Sensible chapters | Placed the memories this book needs | 100 (9/9) |
| Sensible chapters | Left out notes that don't belong in a book (car registration, Wi-Fi) | 100 (6/6) |
| Sensible chapters | Kept memories of the same event or time in one chapter | 99 (8/9) |
| Sensible chapters | Didn't mix far-apart parts of life in one chapter | 99 (2/3) |
| Sensible chapters | Chapters and their memories in time order | 100 (3/3) |
| Sticks to the facts | Every year or decade it names matches the memories | 100 (3/3) |
| Sticks to the facts | No names or places that aren't in the memories (word check) | 97 (8/9) |
| Fits the Focus | Suggested the right kind of book (when the member hadn't chosen) | n/a |
| Fits the Focus | Changing the Focus changed the plan | n/a |
| Fits the Focus | Titles and notes fit the chosen Focus and reader (judge, 1-5) | 100 (9/9) |
| Sticks to the facts | No claims the memories don't support (judge) | 92 (6/9) |

## What went wrong

**Kept memories of the same event or time in one chapter** (1)

- danny-family-life · Gemini 4 Argon · run 1: split 'My son' and 'Born'

**Didn't mix far-apart parts of life in one chapter** (2)

- danny-family-life · Gemini 4 Argon · run 1: 'Born' and 'Plankowner — SEAL Team SIX' share 'Dad's War: The Frogmen'
- danny-family-life · Gemini 4 Argon · run 1: 'Born' and 'Retired — twenty-two years' share 'Dad's War: The Frogmen'

**No claims the memories don't support (judge)** (3)

- danny-family-life · Gemini 4 Argon · run 1: '101st Airborne' in 'Grandpa's War: Easy Company': The memories mention Easy Company, the 506th, and paratroopers, but never explicitly name the 101st Airborne.
- danny-family-life · Gemini 4 Argon · run 2: 'Pakistan' in 'Green Team, Ajax, and Abbottabad': Pakistan is not mentioned in any of the memories.
- danny-family-life · Gemini 4 Argon · run 3: '101st Airborne' in 'Danny I: The Jump': The memories mention volunteering for the Paratroopers, Airborne, and the 506th, but never mention the 101st Airborne.

**No names or places that aren't in the memories (word check)** (1)

- danny-family-life · Gemini 4 Argon · run 2: 'Pakistan' isn't in the memories or the dictionary

## The drafts themselves

Run 1 of each case on Gemini 4 Argon, as the member would see it. (Every draft is saved in this run's `drafts/` folder.)

### danny-family-life — scored 96

1. **Grandpa's War: Easy Company** — Great-grandfather Danny I answers the call after Pearl Harbor and jumps into Europe with the 101st Airborne.
    - WW2 — Pearl Harbor (1941)
    - WW2 — Volunteered for the Paratroopers (1942)
    - WW2 — Camp Toccoa, Currahee (1942)
    - WW2 — Got My Jump Wings (1942)
    - WW2 — Shipped Out for England (1943)
    - WW2 — D-Day: the Normandy Jump & Brécourt Manor (1944)
    - WW2 — Carentan (1944)
    - WW2 — Operation Market Garden (1944)
    - WW2 — Battle of the Bulge (1944)
    - WW2 — Foy (1945)
    - WW2 — The Eagle's Nest (1945)
    - WW2 — Came Home (1945)
    - My son (1947)
2. **Dad's War: The Frogmen** — Grandfather Danny II grows up in the quiet after the war, joins the Navy, and fights in Vietnam with SEAL Team TWO.
    - Born (1947)
    - Enlisted — U.S. Navy (1965)
    - UDT training — graduated (1966)
    - SEAL Team TWO — Little Creek (1967)
    - Vietnam — 8th Platoon, Det Alfa (1967)
    - Tet — Chau Doc (1968)
    - The Rung Sat (1968)
    - Rotated home (1968)
    - My son (1970)
    - Second tour (1971)
    - Plankowner — SEAL Team SIX (1980)
    - Retired — twenty-two years (1987)
3. **Growing Up Between Two Wars** — My childhood in the seventies and eighties, wearing Grandpa's loaned jump wings and watching Dad.
    - First steps (1973)
    - Family dog, Rex (1975)
    - First day of school (1976)
    - Built a treehouse (1977)
    - Grandpa’s jump wings (1978)
    - Parents’ divorce (1982)
    - Made the team (1984)
    - High School Graduation (1988)
4. **Third Generation: Following Dad's Footsteps** — Enlisting in the Navy, surviving BUD/S, and checking aboard my father's old team in the nineties.
    - Enlisted — U.S. Navy (1989)
    - BUD/S — Hell Week (1989)
    - Checked aboard SEAL Team TWO (1990)
    - First deployment (1990)
    - Made Petty Officer (1991)
    - Moved out (1993)
    - Made Chief (1995)
    - Wedding Day (1996)
    - Bought first car (1998)
    - Y2K survived (2000)
5. **Everything Changes: September 11th and Afghanistan** — The towers fall, Grandpa passes away as I pack for war, and my first rotations overseas.
    - September 11th (2001)
    - The last week (2001)
    - Grandpa died (2001)
    - First house down payment (2001)
    - First rotation — Afghanistan (2002)
    - Totaled the car (2003)
    - Beach weekend (2005)
6. **Green Team, Ajax, and the Long War** — Screening for Dad's old unit, working point with my dog Ajax, the raid in Abbottabad, and losing Dad.
    - Green Team — selected (2005)
    - Ajax (2008)
    - Tokyo trip (2008)
    - The compound in Paktika (2009)
    - A full-scale mock-up, somewhere in North Carolina (2011)
    - Abbottabad (2011)
    - The last week (2011)
    - Dad died (2011)
7. **Coming Home and the Quiet After** — Retiring after twenty-two years, bringing Ajax home for good, and saying goodbye to the best partner I ever had.
    - Retired — twenty-two years (2011)
    - Ajax came home for good (2012)
    - Lost the big client (2013)
    - Ajax (2013)
    - Ran a half marathon (2015)
8. **A Second Life: Building in Peace** — Going back to school, learning to code, starting a company, and finding peace in an ordinary life.
    - Shipped first app (2017)
    - New Home (2017)
    - Gave a keynote (2019)
    - Layoff — Old Job (2020)
    - Bachelor of Computer Science (2020)
    - Hit 1,000 users (2021)
    - Camping under the stars (2022)
    - Hired the first employee (2023)
    - First Talk — DevConf (2024)
    - Christmas (2024)
    - Garden finally bloomed (2025)
    - Coffee with an old friend (2026)

Not in a chapter yet: Truck registration, Wi-Fi password, Dentist, Gutters

### danny-i-kept-misfits — scored 100

1. **Currahee** — Enlisting after Pearl Harbor and earning a place in Easy Company.
    - WW2 — Pearl Harbor (1941)
    - WW2 — Volunteered for the Paratroopers (1942)
    - WW2 — Camp Toccoa, Currahee (1942)
2. **Jump wings, 1943** *(the member's own chapter)* — Benning, the day they pinned the silver on.
    - WW2 — Got My Jump Wings (1942)
3. **Into Normandy** — Waiting in England, jumping on D-Day, and losing Bill at Carentan.
    - WW2 — Shipped Out for England (1943)
    - WW2 — D-Day: the Normandy Jump & Brécourt Manor (1944)
    - WW2 — Carentan (1944)
4. **Holland and the Bulge** — Jumping into Holland and holding the frozen line from Bastogne to Foy.
    - WW2 — Operation Market Garden (1944)
    - WW2 — Battle of the Bulge (1944)
    - WW2 — Foy (1945)
5. **Coming home** *(the member's own chapter)* — Bill. Say his name in this chapter.
    - WW2 — The Eagle's Nest (1945)
    - WW2 — Came Home (1945)
6. **The wedding** *(the member's own chapter)* — Margaret thinks this should come before the farm. She is right.
7. **The farm** *(the member's own chapter)* — For the grandchildren.
8. **What We Pass On** — Holding my newborn son and watching my grandson answer the call years later.
    - My son (1947)
    - The last week (2001)

Not in a chapter yet: nothing

### danny-shared-versions — scored 100

1. **Sons and Grandsons** — The births of Danny II in 1947 and Danny III in 1970, remembered by father and son.
    - My son (1947)
    - Born (1947)
    - The grandson (1970)
    - My son (1970)
2. **The Wings on Loan** — Three views of the afternoon in 1978 when Grandpa pinned his war wings on his grandson.
    - The wings, on loan (1978)
    - From the doorway (1978)
    - Grandpa’s jump wings (1978)
3. **Mornings in the Woods** — Cold mornings hunting together, hot cups from the thermos, and not a single deer.
    - Measuring the wrong thing (1982)
    - Three cups from the thermos (1983)
    - Not one deer (1983)
4. **The Scorecard in the Pocket** — An afternoon at the range in 1985, and the lunch that mattered more than the score.
    - What did you enjoy? (1985)
    - The scorecard in my pocket (1985)
    - Grandpa stole my fries (1985)
5. **First Summer Without Orders** — Danny II retires in 1987, and three generations take a slow walk up a steep hill.
    - Retired — twenty-two years (1987)
    - Dad's retirement (1987)
    - The hill got steeper (1987)
    - First summer without orders (1987)
    - Two old men and an argument (1987)
6. **The Loan Comes Due** — The last weeks of Danny I in 2001 and Danny II in 2011, and the things left unsaid.
    - The last week (2001)
    - Grandpa died (2001)
    - The last week (2011)
    - Dad died (2011)

Not in a chapter yet: Dentist, Gutters

## How to read this

- **Follows the rules**: valid answer, only real memory ids, each memory once, the member's own chapters kept, book type answered as asked, chapter count and lengths within the limits. These are the prompt's hard rules: the app quietly repairs some of them (it drops made-up ids), but a miss still means the agent didn't do what it was told.
- **Sensible chapters**: checked against an answer key written for each made-up memoir. Did the memories that matter get placed, did the noise (car registration, Wi-Fi) stay out, did memories of the same event stay together, were far-apart parts of life kept apart, and is a life memoir in time order.
- **Sticks to the facts**: years in titles and notes must match the memories; capitalized words that are in neither the memories nor the dictionary are flagged as possible made-up names; the judge lists any other claim the memories don't support.
- **Fits the Focus**: the suggested book type (when the member hadn't chosen), whether switching Life memoir → Resilience story actually changed the plan, and the judge's 1–5 rating.
- Model answers vary from run to run, which is why each case runs more than once.
