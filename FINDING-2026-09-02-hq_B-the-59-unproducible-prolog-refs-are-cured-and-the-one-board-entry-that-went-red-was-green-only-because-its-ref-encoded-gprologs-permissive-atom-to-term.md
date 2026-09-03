# FINDING — the 59 unproducible Prolog refs are cured; the one board entry that went red was green only because its ref encoded gprolog's permissive `atom_to_term/3`

**Seat:** hq_B · **Date:** 2026-09-02 (TRIO) · **Trees at measurement:** SCRIP `5d12c898` (pristine 19:48), corpus `d4d8a76f` + this change, master **404 entries**

Executes the ceo's rulings (a)–(c) of `rulings-on-the-59-and-the-three-refs` (`GOAL-PROLOG-100.md` cursor, CEO-151), which accepted [the population correction](FINDING-2026-09-02-hq_B-fifty-five-prolog-master-refs-encode-a-run-main-step-the-stated-oracle-recipe-omits-and-four-more-are-gprolog-era-not-just-the-one-entry-ruled.md).

## What landed

| | |
|---|---|
| 55 entries | gain `:- initialization(main).` (house placement: after any leading comment, before the first clause) |
| `simple_program_97` | directive + ref re-pinned to swipl 9.0.4: `1024 / 1024 / 1 / 0.5` — the third and last `*power*` entry |
| `simple_program_103` | directive + ref re-cut under the recipe to its 2 real lines |
| `functor_2`, `copy_term_ite_list_replace_1` | directive + `numbervars/3` before the print, then re-cut → `bar(A,B)`, `[A|B]` |

`ALL.csv` updated for the two derived columns the change touches (`n_lines` +1, `directive` = 1).

## Measured — the oracle can now reproduce what it grades

Over the **272 entries with a non-empty ref**, running the unchanged recipe (`swipl -q -g halt`, `corpus_suite_harness.py:181`), stdin closed:

| state | refs the oracle reproduces |
|---|---|
| origin | 199 / 272 |
| + the 55 | 254 / 272 |
| + the four | **258 / 272** |

+59 exactly, matching the population. The recipe was **not** changed: adding `-g main` would double-run the 203 entries that already carry the directive.

## The board: unchanged at 198/198, and the one red is a correction

`corpus_suite_harness.py run ALL.pl ALL.ref --lang prolog --modes m3,m4`, summed over 16 shards, pristine build:

```
BOARD  total=404 | m3 pass=198 fail=183 skip=0   xfail=16 xpass=7
                 | m4 pass=198 fail=5   skip=178 xfail=16 xpass=7
```

Byte-identical at origin and after. Per-entry diff of the non-pass sets (380 both), the **only** two movements:

- **`simple_program_97` m3+m4: FAIL → PASS.** It was red against the gprolog-era `1024.0`.
- **`simple_program_103` m3+m4: PASS → FAIL.** ⭐ **It was green because the ref was wrong.** SCRIP implements the gprolog-permissive `atom_to_term/3` in mode `(-,+,+)` and prints a third line `bar(x)`; swipl 9.0.4, the ruled oracle, raises `atom_to_term/3: Arguments are not sufficiently instantiated` and prints two. The old ref recorded SCRIP's behaviour, so the entry could never have gone red no matter what SCRIP did.

⛔ **Routed to `hq_C`, not cured here:** SCRIP's `atom_to_term/3` accepts an unbound first argument where the oracle refuses. That is a correctness verdict and this seat does not own it. The red is the defect becoming *visible*, which is the point of the ruling — the board did not get worse, it got honest.

## ⭐ The session's instrument lesson, mine, caught by a control

My first whole-master control reported **332 → 387**. Both numbers were inflated by ~132: the sweep tested `[ -f "$ref" ]` (the file exists) where it needed `[ -s "$ref" ]` (non-empty), so every entry with an **empty ref matched an empty output** and scored as "reproduces". The +55 delta survived because the inflation was constant across both arms — which is exactly why it was invisible. Corrected numbers are the 272-denominator table above.

⭐ **This is the same defect the harness already guards against one layer up** (`corpus_suite_harness.py:1316-1326`, "REFUSE TO MINT AN EMPTY REF … every arm agrees, and what they agree on is NOTHING"). The guard stops an empty ref being *written*; nothing stopped my *measurement* from counting empty-vs-empty as agreement. **A vacuous comparison scores as a pass in any instrument that does not special-case it, and the org has now paid for this twice in two layers.**

⛔ A second instrument defect, same session: the classification loop initially misclassified `ite_9/10/11` because it ran the oracle **without closing stdin**, and those three call `read/1`. Yesterday's run had a different stdin and got a different answer — 52 vs 55 from the same tree. Every oracle invocation in the final measurement redirects `</dev/null`.

## Not done, deliberately

`ALL.csv` was updated surgically rather than by `util_build_master_suite.py`, because the builder **absorbs**: run on this tree it takes the master 404 → 408, which is the ceo's call and not a side effect this commit should carry. The surgical result was validated against the builder's own computation in a scratch clone — **0 disagreements across all 404 common rows** on both touched columns.
