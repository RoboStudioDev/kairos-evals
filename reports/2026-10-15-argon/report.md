# Kairos Outline drafts, scored (2026-10-15)

**What ran:** 6 made-up memoir cases × 1 model(s) × 3 run(s) = 18 Outline drafts, each read by a judge (Gemini 3.8 Flash).
**Cost:** $0.27 (drafts $0.09, judge $0.18). **When:** 2026-10-15T11:21:00 to 2026-10-15T11:24:51.

Scores are out of 100. Each draft is scored in four areas; its overall score is the average of the four. A *rule break* is any miss on a hard rule from the prompt. See [How to read this](#how-to-read-this).

## Scores by model

| Model | Overall | Follows the rules | Sensible chapters | Sticks to the facts | Fits the Focus | Drafts with a rule break | Seconds per draft (typical, slowest) | Cost per draft |
|---|---|---|---|---|---|---|---|---|
| Gemini 4 Argon | **99** | 100 | 98 | 100 | 100 | 0 of 18 | 8, 78 | $0.0050 |

## Scores by case

Overall is the average across runs, with the lowest and highest run in brackets.

| Case | Model | Overall (low–high) | Follows the rules | Sensible chapters | Sticks to the facts | Fits the Focus |
|---|---|---|---|---|---|---|
| abel-four-memories | Gemini 4 Argon | **100** (100–100) | 100 | 100 | 100 | 100 |
| ezra-not-chosen | Gemini 4 Argon | **100** (100–100) | 100 | 100 | 100 | 100 |
| ida-shuffled | Gemini 4 Argon | **100** (100–100) | 100 | 100 | 100 | 100 |
| june-selfhelp-kept | Gemini 4 Argon | **97** (92–100) | 100 | 89 | 100 | 100 |
| rosa-life | Gemini 4 Argon | **100** (100–100) | 100 | 100 | 100 | 100 |
| rosa-resilience | Gemini 4 Argon | **100** (100–100) | 100 | 100 | 100 | 100 |

What each case tests:

- **abel-four-memories** — Four memories, book type Other in the member's own words. Few chapters; nothing made up.
- **ezra-not-chosen** — The member hasn't picked a kind of book. The agent should suggest a resilience story.
- **ida-shuffled** — Memories arrive out of order; no book type, no audience. Expect a life memoir, told in time order.
- **june-selfhelp-kept** — Self-help for young business owners. The member wrote two chapters herself; they must come back untouched.
- **rosa-life** — Life memoir, chosen by the member, for her grandchildren.
- **rosa-resilience** — The same memories as a resilience story, for anyone who has lost a spouse.

## Every check

Average score, and how many drafts got full marks, where the check applies.

| Area | Check | Gemini 4 Argon |
|---|---|---|
| Follows the rules | Gave an answer the app can read (JSON with chapters) | 100 (18/18) |
| Follows the rules | Used only memories it was given (no made-up memory ids) | 100 (18/18) |
| Follows the rules | Put each memory in at most one chapter | 100 (18/18) |
| Follows the rules | Kept each chapter the member wrote, exactly once | 100 (3/3) |
| Follows the rules | Book type answered the way the prompt asks | 100 (18/18) |
| Follows the rules | Chapter count, title and note lengths within the limits | 100 (18/18) |
| Sensible chapters | Placed the memories this book needs | 100 (18/18) |
| Sensible chapters | Left out notes that don't belong in a book (car registration, Wi-Fi) | 100 (15/15) |
| Sensible chapters | Kept memories of the same event or time in one chapter | 93 (14/15) |
| Sensible chapters | Didn't mix far-apart parts of life in one chapter | 100 (6/6) |
| Sensible chapters | Chapters and their memories in time order | 100 (6/6) |
| Sticks to the facts | Every year or decade it names matches the memories | n/a |
| Sticks to the facts | No names or places that aren't in the memories (word check) | 100 (18/18) |
| Fits the Focus | Suggested the right kind of book (when the member hadn't chosen) | 100 (6/6) |
| Fits the Focus | Changing the Focus changed the plan | 100 (6/6) |
| Fits the Focus | Titles and notes fit the chosen Focus and reader (judge, 1-5) | 100 (18/18) |
| Sticks to the facts | No claims the memories don't support (judge) | 100 (18/18) |

## What went wrong

**Kept memories of the same event or time in one chapter** (1)

- june-selfhelp-kept · Gemini 4 Argon · run 1: split 'Marcus runs a crew' and 'Selling to Marcus'

## Can the judge be trusted?

Before trusting the judge, it grades drafts with planted problems next to clean ones. It passes when it does what each row expects: rate the planted draft's Focus lower, and/or find more made-up claims in it than in the clean draft.

| Case | Planted problem | Clean: Focus, claims found | Planted: Focus, claims found | Judge passed? |
|---|---|---|---|---|
| rosa-resilience | reads like a cookbook and a travel log; says Ted died in a car crash | 5/5, 0 | 1/5, 2 | yes |
| abel-four-memories | names the father Ruben and invents a Navy career | 5/5, 0 | 4/5, 3 | yes |

## The drafts themselves

Run 1 of each case on Gemini 4 Argon, as the member would see it. (Every draft is saved in this run's `drafts/` folder.)

### abel-four-memories — scored 100

1. **Who Your Grandfather Was** — Stories of your grandfather's patience, humor, and the things he loved.
    - Dad's fishing hat (1984)
    - The Sunday he taught me to drive (1991)
2. **The Day He Met You** — When you were born and your grandfather held you for the first time.
    - Dad meets Mateo (2008)
3. **One Last Cast** — Our final fishing trip together at Lake Orrin.
    - The last fishing trip (2015)

Not in a chapter yet: nothing

### ezra-not-chosen — scored 100

Suggested kind of book: **resilience**

1. **Learning the Trade** — Starting out on Uncle Remy's floor and opening Crumb & Kettle on Canal Street.
    - Flour on Uncle Remy's floor (1998)
    - Leaving culinary school (2003)
    - Opening day on Canal Street (2009)
    - The regulars (2012)
2. **When the Canal Came Over** — The flood that ruined the bakery and the neighbors who showed up with shovels.
    - The canal comes over (2017)
    - Mucking out (2017)
    - The insurance letter (2017)
3. **The Loaves Paid in Advance** — Baking in the church basement and how Ostrander Flats brought the shop back.
    - Baking in a church basement (2017)
    - The prepaid loaves (2018)
    - Reopening (2018)
4. **Higher Ground** — Cinder blocks, Nia joining the bakery, and passing the craft on to Canal Street kids.
    - Up on cinder blocks (2019)
    - Nia joins the bakery (2022)
    - Saturday bread class (2024)

Not in a chapter yet: Dentist, Truck

### ida-shuffled — scored 100

Suggested kind of book: **life**

1. **Growing Up on the Farm** — Childhood days with family, winter storms, and moving to the town school.
    - Haying with Grandpa Ott (1947)
    - Snowed in for nine days (1952)
    - The schoolhouse closes (1955)
2. **First Jobs and Coming Home** — Working in the Merriton typing pool before returning to the family farm.
    - The typing pool in Merriton (1959)
    - Coming home (1961)
3. **Years at the Brindle Courier** — Starting as a typist and spending twenty-three years as the county editor.
    - The Courier's want ad (1966)
    - Editor (1975)
    - The elevator fire (1984)
    - Last issue (1998)
4. **Next Chapters and Legacy** — Fixing the Coldwater road, quilting front pages, and passing stories down.
    - Running for council (1999)
    - The front-page quilt (2012)
    - Ida's sheep, again (2019)

Not in a chapter yet: Furnace filter

### june-selfhelp-kept — scored 92

1. **Starting with what you have** — How to begin with almost nothing and win trust when you make mistakes.
    - The first mower (2001)
    - The wall that fell down (2003)
2. **Lesson one: say the price out loud** *(the member's own chapter)* — Underpricing, and learning to charge what the work costs.
    - The Ochoa lawn (2001)
    - Saying the price out loud (2002)
3. **Knowing your numbers and when to walk away** — Tracking what jobs really cost and turning down bad terms.
    - Saying no to Fairmont (2005)
    - The notebook of every bid (2006)
4. **Your first hire** *(the member's own chapter)*
    - Hiring Marcus (2010)
5. **Taking care of your people** — Keeping the crew paid in hard times and learning to let them lead.
    - The recession winter (2008)
    - Marcus runs a crew (2013)
6. **Stepping back and letting go** — Setting boundaries before you burn out, and passing the business on.
    - Asleep at a stoplight (2016)
    - Selling to Marcus (2021)

Not in a chapter yet: Office Wi-Fi

### rosa-life — scored 100

1. **Growing Up in Larkspur Bend** — Childhood days in Papa's shop, skating with Lou, and graduating high school.
    - Sorting heels in Papa's shop (1955)
    - The winter the Tamsin froze (1957)
    - Mama's polka hour (1960)
    - Graduating from Larkspur Bend High (1967)
2. **Corran City and Meeting Ted** — Leaving home for nursing school, first hospital shifts, and marrying Ted.
    - The bus to Corran City (1967)
    - Night shifts on Ward Four (1968)
    - Meeting Ted at the laundromat (1969)
    - Our wedding at St. Casimir's (1970)
3. **The Willet Road Years** — Raising June and Sam, family nights at the kitchen table, and becoming head nurse.
    - June is born (1973)
    - Sam and the creek (1976)
    - The kitchen table years (1981)
    - Head nurse (1988)
4. **Losing Ted and Finding My Way** — Ted's illness, grieving his loss, and starting over with Hattie and the garden.
    - The diagnosis (2004)
    - Ted's last morning (2004)
    - His side of the bed (2005)
    - Hattie and the Tuesday group (2005)
    - Driving the highway again (2006)
    - Ted's Garden (2006)
5. **The Years Since** — Retiring from nursing, watching Pia grow, and seeing the ocean at seventy.
    - Retirement party (2011)
    - Pia learns to ride a bike (2016)
    - Seeing the ocean at seventy (2019)

Not in a chapter yet: Car registration, Phone plan

### rosa-resilience — scored 100

1. **What We Built Together** — Meeting Ted, raising June and Sam, and the quiet joy of our ordinary days on Willet Road.
    - Meeting Ted at the laundromat (1969)
    - Our wedding at St. Casimir's (1970)
    - June is born (1973)
    - Sam and the creek (1976)
    - The kitchen table years (1981)
    - Head nurse (1988)
2. **The Long Goodbye** — Ted's diagnosis, the deck he finished, and his last morning at home.
    - The diagnosis (2004)
    - Ted's last morning (2004)
3. **The Empty Side of the Bed** — The quiet months after Ted died and finding a friend who understood.
    - His side of the bed (2005)
    - Hattie and the Tuesday group (2005)
4. **Finding My Footing** — Learning to do things on my own and planting something new with Hattie.
    - Driving the highway again (2006)
    - Ted's Garden (2006)
5. **The Life That Kept Growing** — Retiring from nursing, watching my granddaughter grow, and carrying Ted with me to the ocean.
    - Retirement party (2011)
    - Pia learns to ride a bike (2016)
    - Seeing the ocean at seventy (2019)

Not in a chapter yet: Sorting heels in Papa's shop, The winter the Tamsin froze, Mama's polka hour, Graduating from Larkspur Bend High, The bus to Corran City, Night shifts on Ward Four, Car registration, Phone plan

## How to read this

- **Follows the rules**: valid answer, only real memory ids, each memory once, the member's own chapters kept, book type answered as asked, chapter count and lengths within the limits. These are the prompt's hard rules: the app quietly repairs some of them (it drops made-up ids), but a miss still means the agent didn't do what it was told.
- **Sensible chapters**: checked against an answer key written for each made-up memoir. Did the memories that matter get placed, did the noise (car registration, Wi-Fi) stay out, did memories of the same event stay together, were far-apart parts of life kept apart, and is a life memoir in time order.
- **Sticks to the facts**: years in titles and notes must match the memories; capitalized words that are in neither the memories nor the dictionary are flagged as possible made-up names; the judge lists any other claim the memories don't support.
- **Fits the Focus**: the suggested book type (when the member hadn't chosen), whether switching Life memoir → Resilience story actually changed the plan, and the judge's 1–5 rating.
- Model answers vary from run to run, which is why each case runs more than once.
