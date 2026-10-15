# Self-test: do the checks catch planted mistakes?

## Fixtures

Fine.

## Reference drafts (written by hand; should be clean)

| Case | Overall | Rule breaks | False alarms on dates or names | Result |
|---|---|---|---|---|
| abel-four-memories | 100 | 0 | none | pass |
| danny-family-life | 100 | 0 | none | pass |
| danny-i-kept-misfits | 100 | 0 | none | pass |
| danny-shared-versions | 100 | 0 | none | pass |
| ezra-not-chosen | 100 | 0 | none | pass |
| ida-shuffled | 100 | 0 | none | pass |
| june-selfhelp-kept | 100 | 0 | none | pass |
| rosa-life | 100 | 0 | none | pass |
| rosa-resilience | 100 | 0 | none | pass |

## Planted mistakes (each must be caught)

| Draft | Planted mistake | Check | Caught? |
|---|---|---|---|
| abel-made-up-father | answers bookType 'other' although the member already chose | `book_type_rule` (0) | yes |
| abel-made-up-father | five chapters from four memories (one of them empty) | `sizes` (67) | yes |
| abel-made-up-father | '1975' on a memory from 1984 | `dates_supported` (0) | yes |
| abel-made-up-father | the father named 'Ruben', and 'Norfolk', neither in any memory | `no_new_names` (50) | yes |
| danny-family-by-person | Danny I's last week (2001) filed with his war, and Danny II's birth with his 1980s and his death | `apart` (99) | yes |
| danny-family-by-person | each death and the 1947 birth split between the two men who tell it | `together` (75) | yes |
| danny-family-by-person | 'Fathers and sons' (1947 and 1970) placed last, after 2026 | `time_order` (92) | yes |
| danny-family-careless | 13 chapters; the prompt allows 3 to 12 | `sizes` (67) | yes |
| danny-family-careless | the truck registration note placed in a chapter | `left_out_noise` (75) | yes |
| danny-family-careless | Abbottabad and Danny II's last week left out | `placed_what_matters` (96) | yes |
| danny-family-careless | a memory id that doesn't exist (demo-iii-2011.20) | `real_memories_only` (99) | yes |
| danny-family-careless | 'Checked aboard SEAL Team TWO' in two chapters | `each_memory_once` (99) | yes |
| danny-family-careless | 'Fort Bragg', which no memory mentions | `no_new_names` (75) | yes |
| danny-family-careless | '1950s' on Danny I's war chapter (1944-1945) | `dates_supported` (0) | yes |
| danny-i-fixed-member-year | rewrote the member's 'Jump wings, 1943' with the right year instead of keeping it | `keeps_member_chapters` (75) | yes |
| danny-i-fixed-member-year | listed the member's wings memory, which it was never sent | `real_memories_only` (92) | yes |
| danny-i-kept-dropped | the member's empty chapters 'The wedding' and 'The farm' dropped | `keeps_member_chapters` (50) | yes |
| danny-i-kept-dropped | Carentan, where Bill died, left out | `placed_what_matters` (75) | yes |
| danny-i-kept-dropped | Bastogne and Foy split into separate chapters | `together` (0) | yes |
| danny-i-kept-dropped | '1943' on the Normandy chapter (its memory is from 1944) | `dates_supported` (0) | yes |
| danny-shared-by-person | every moment split up: one chapter per Danny instead of one per moment | `together` (0) | yes |
| danny-shared-by-person | Danny II's hunting morning (filed a year early) left out | `placed_what_matters` (95) | yes |
| danny-shared-by-person | the dentist note placed in a chapter | `left_out_noise` (50) | yes |
| ezra-wrong-suggestion | suggests a life memoir for a story that is mostly the flood | `suggested_book_type` (0) | yes |
| ezra-wrong-suggestion | the flood and the comeback left out | `placed_what_matters` (27) | yes |
| ezra-wrong-suggestion | the dentist appointment placed in a chapter | `left_out_noise` (50) | yes |
| ida-one-chapter-each | suggests self-help for a whole-life story | `suggested_book_type` (0) | yes |
| ida-one-chapter-each | 13 chapters, one per memory (the limit is 12) | `sizes` (67) | yes |
| ida-one-chapter-each | chapters left in the shuffled order the memories arrived in | `time_order` (50) | yes |
| ida-one-chapter-each | the furnace filter note given its own chapter | `left_out_noise` (0) | yes |
| ida-one-chapter-each | '1950s' on the 1975 editor chapter | `dates_supported` (0) | yes |
| ida-one-chapter-each | the hay wagon and the snowed-in winter in separate chapters | `together` (0) | yes |
| june-kept-chapters-broken | the member's 'Your first hire' dropped, 'Lesson one' included twice | `keeps_member_chapters` (0) | yes |
| june-kept-chapters-broken | the Wi-Fi password note placed in a chapter | `left_out_noise` (0) | yes |
| june-kept-chapters-broken | 'Selling to Marcus' left out | `placed_what_matters` (86) | yes |
| not-json | the model answers in prose instead of JSON | `valid_answer` (0) | yes |
| rosa-life-many-mistakes | a memory id that doesn't exist (rv99) | `real_memories_only` (96) | yes |
| rosa-life-many-mistakes | 'The bus to Corran City' listed twice | `each_memory_once` (96) | yes |
| rosa-life-many-mistakes | answers bookType 'life' although the member already chose | `book_type_rule` (0) | yes |
| rosa-life-many-mistakes | a 68-character title | `sizes` (95) | yes |
| rosa-life-many-mistakes | the car registration note placed in a chapter | `left_out_noise` (50) | yes |
| rosa-life-many-mistakes | Ted's diagnosis and his last morning split up | `together` (57) | yes |
| rosa-life-many-mistakes | a childhood memory filed with the later years | `apart` (97) | yes |
| rosa-life-many-mistakes | Willet Road years before nursing school | `time_order` (85) | yes |
| rosa-life-many-mistakes | '1990s' on a 1950s childhood chapter | `dates_supported` (0) | yes |
| rosa-life-many-mistakes | 'Lake Tahoe', which no memory mentions | `no_new_names` (75) | yes |
| rosa-resilience-wrong-book | the grief months and Hattie's group left out | `placed_what_matters` (67) | yes |

**Result: all checks work.**
