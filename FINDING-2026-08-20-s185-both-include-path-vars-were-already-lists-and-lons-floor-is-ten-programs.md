# FINDING s185 — **BOTH INCLUDE-PATH VARIABLES WERE ALREADY LISTS.** THE FIX IS ONE HARNESS EDIT, AND lon's REAL FLOOR IS **10 PROGRAMS, NOT 43**

**Seat:** seat1 (Opus 5), 2026-08-20, queue row `lon-include-root` (successor to `oracle-format-unscr`, HQ-73). **Trees:** SCRIP `ffbc1425`, corpus `2d966ce9`, x64 clean (`git status --porcelain` empty — **zero stock-sbl edits**). **Zero corpus edits.** One file changed: `SCRIP/scripts/scorecard_snobol4.sh`.
**Brief:** *"reproduce ONE lon ERROR 285 row by hand under both engines, then decide the smaller fix — teaching `scorecard_snobol4.sh` a correct include root per engine, vs teaching `SNO_LIB` a path LIST."*

## ⛔ THE FORK HAD NO SECOND PRONG — BOTH HALVES WERE ALREADY TRUE. MEASURED, NOT READ.
| the brief / ADDENDUM 1 says | measured at this HEAD |
|---|---|
| *"`SETL4PATH` in stock sbl is a **PREFIX, NOT A PATH LIST**"* (ADDENDUM 1, s184) | **IT IS A COLON LIST.** Negative control `A` with the file absent → `ERROR 285`; `A:B` → **OK**; `B:A` → **OK**; `A/:B/` → **OK**; `/nonexistent` → `ERROR 285`; unset → `ERROR 285`. Trailing slash is **not** required and no arm SIGSEGV'd. **No pooled include dir is needed for the oracle.** |
| *"…and possibly teaching `SNO_LIB` a path **list**"* | **`SNO_LIB` HAS ALWAYS BEEN A LIST** — `src/driver/scrip.c:941` splits it with `strsep(&sp,":")`. `scrip.c:935` already pushes the program's own dir **first**, and `snobol4.l:67` already adds each *resolved* include's own directory, so nested includes chain by themselves. **Zero SCRIP code needed.** |
| — (not in the brief) | **Both engines also accept lowercase `-include`.** 8 lon programs use it. A census regex that greps `-INCLUDE` under-counts the class by 5 programs; mine did, until sbl disagreed with it and sbl was right. |

So the row's two candidate fixes collapse into **one three-hunk shell edit** and neither engine needed teaching.

## THE FIX — `scorecard_snobol4.sh`, THE `lib` COLUMN BECOMES A COLON LIST HANDED TO **BOTH** ENGINES
1. `sc_libpath()` resolves the `lib` spec — a colon list of `SELFDIR` \| `CORPUS` \| *corpus-relative dir* — once per program (program dir first, so a suite can never be shadowed by the shared library).
2. The oracle line changes `SETL4PATH=.` → `SETL4PATH=".:$lib"`. **This is the whole point of the row: the two engines were being shown different libraries, and the oracle was the one kept blind.**
3. Two suites declare the roots their programs actually cite — `gimpel … SELFDIR:programs/include` and `lon … SELFDIR:programs/lon/sno:programs/include:programs/include/ebnf:programs/snobol4/demo/beauty:programs/csnobol4-suite`.

**Every root is load-bearing, by ablation** (residue programs when each is dropped): `demo/beauty` **+37** · `include/ebnf` +1 · `csnobol4-suite` +1 · `lon/sno` +0 programs but it is what resolves `debug.sno` (3 programs, currently masked by a co-occurring miss). **Pooling was checked for collisions, not assumed:** across all 66 names in lon's transitive closure that exist in more than one tree, **every duplicate set is byte-identical (uniq_md5 = 1)** — with the single exception called out under CLASS B below, which is why that one is routed and not guessed.

## RECEIPTS — FOUR SUITES, SAME COMMAND, BEFORE (`sc-before-s185`) AND AFTER (`sc-after-s185`), 490 ROWS EACH
| suite | W | N before → after | SCORE before → after | UNSCR before → after |
|---|---|---|---|---|
| patterns | 10 | 122 → 122 | 96.3 → **96.3** | 0 → 0 |
| csnobol4_suite | 5 | 123 → 123 | 32.5 → **32.5** | 1 → 1 |
| gimpel | 5 | 10 → 10 | 20.0 → **20.0** | 135 → 135 |
| **lon** | 5 | **21 → 56** | **33.3 → 12.5** | **78 → 43** |
| **META (these four, w=25)** | | | **55.7 → 51.5** | |
**The two control suites are byte-identical — 246 rows, ZERO status changes in either mode.** The patch is inert wherever no list is declared, by construction: every other suite's `lib` resolves either to the program's own directory (already `.`) or to a path that does not exist (see the latent finding below).
**lon 21 → 56 scorable is EXACTLY the ceiling ADDENDUM 1 priced at "+35 rows, zero regress"** — reached with no scratch pool, no symlink farm, no corpus duplication, and no `.` -prefix trickery. The same 7 programs pass before and after; **nothing regressed and nothing new passed.**

**CORPUS FAIL-SET UNCHANGED, after `make pristine` (RT_OPT `-O0`, FACT RULE O0-DEV):** **m3 332/5 · m4 325/11 SKIP 1** — the s183 watermark exactly, fail-set identical **by name**. Expected (this row touches no compiler source) but run rather than asserted, since the row's DONE-WHEN names it.

## ⭐⭐ THE STANDING TRAP FIRES A THIRD TIME — AND THIS IS ITS CLEANEST INSTANCE
HQ-73's law: **UNSCR HIDES SCRIP REDS.** Here it is exact and unmixed with anything else — 35 rows moved from invisible to scored, **all 35 are SCRIP failures**, so lon's SCORE falls 33.3 → 12.5 and the four-suite META falls 55.7 → 51.5 **on a change that fixed a harness defect and broke nothing.** The 12.5 is not a regression; it is the first honest number lon has ever had. Any rung that proposes buying META by repairing oracle plumbing must price this, every time.

## ⛔ THE DONE-WHEN'S RESIDUE, NAMED FILE-BY-FILE — AND IT IS **NOT ONE CLASS**
lon programs whose compile still dies on an unopenable include: **74 → 35** (measured directly by running all 99 under sbl on both arms; a static resolver reproduces 35/35 exactly once its regex accepts lowercase `-include`, so the model below is calibrated against the engine, not asserted).

**CLASS A — GENUINELY ABSENT from the corpus: 14 names, and they block 10 of the 35 programs. THIS IS THE FLOOR.**
`host.sno` (2) · `BCP.sno` · `findname.sno` · `nmake.sno` · `external/directs.sno` · `transl8tweetish.sno` · `portable.sno` · `/home/build/bin/portable.sno` (an absolute path into a build machine that does not exist) · `ss.sno` · `ini.sno` · `utility.sno` · `../URL.sno` · `../export.sno` · `../ini.sno`.
Programs: `blob.sno` `Blogzilla.sno` `build.sno` `ssls.sno` `ssreorg.sno` `TZ.sno` `verify.sno` `atif.sno` `mkblddir.sno` `Extractor.sno`.

**CLASS B — THE FILE IS IN THE CORPUS UNDER ANOTHER SPELLING: 8 names, and they are the ONLY blocker for the other 25 programs.**
| name cited | on disk as | programs | mechanical? |
|---|---|---|---|
| `Trace.sno` (from `programs/include/5ivesAlive.inc`) | `programs/snobol4/beauty_suite/trace.sno` **and** `programs/snobol4/demo/beauty/trace.inc` | **23** | ⛔ **NO — TWO candidates and they are NOT byte-identical**, differing at the `T8Trace` init line (`''` vs `.dummy`). Both carry the header `* Trace.inc` and define `T8Trace(lvl,str,ofs)`, so the module is right and the *variant* is the open question. **NOT GUESSED.** |
| `RANDOM.inc` (from `5ivesAlive.inc`, `TGen.inc`, +4 lon programs) | `programs/include/RANDOM.INC` — **one copy, same directory as the citer** | **21** | ✅ pure case, exactly HQ-73's blessed class (~6 one-line edits) |
| `../modules/random/random.sno` | `programs/csnobol4-suite/random.sno` | 2 | path shape, not case |
| `../HTML.sno` `../ReadWrite.sno` `../assign.sno` `../global.sno` `../system.sno` | `lon/sno/HTML.sno` · `beauty_suite/{ReadWrite,assign,global}.sno` · `gimpel/SYSTEM.sno` | 1 each (all `Blogzilla.sno`) | `../` forms that assume a tree layout this corpus does not have |

⛔ **THEREFORE THE DONE-WHEN AS WRITTEN IS NOT REACHABLE FROM THE HARNESS.** "ERROR 285 falls to the count of genuinely-absent includes" means **35 → 10**, and the 25-program gap is a **CORPUS NAMING** defect living inside the *shared library* (`programs/include/5ivesAlive.inc` alone accounts for both big names), not an include-root defect. Routed to HQ **with its price** as `q-lon-include-root`, per the lesson HQ recorded on the predecessor row — not held silently, and not freelanced.

## ⭐ A CORRECTION TO THE PREDECESSOR'S gimpel RESIDUE — IT WAS 3, IT IS 2
HQ-73 §2 records gimpel's genuinely-absent set as **`resolution.sno`, `stringout.sno`, `system.inc`**. **`system.inc` was never absent** — it is `programs/include/system.inc`, and it was merely unreachable from `SELFDIR`. Measured at name level on `TIMER.sno`: unresolved `{resolution.sno, system.inc}` → `{resolution.sno}` under the new lib. gimpel's suite numbers do **not** move (all 3 affected programs cite an absent name *as well*), which is why the board above reads 20.0/135 on both arms — **a name-level cure invisible at program level.** gimpel's true absent set is **`resolution.sno` and `stringout.sno`**.

## ⛔ LATENT HARNESS FINDING — THREE SUITES DECLARE A LIBRARY DIRECTORY THAT DOES NOT EXIST
`beauty_self` and `beauty_suite` route to `demo/beauty`, and `patterns`/`crosscheck` to `demo/inc`; resolved corpus-relative these are `$CORPUS/demo/beauty` and `$CORPUS/demo/inc`, and **neither path exists** (the real tree is `$CORPUS/programs/snobol4/demo/…`). They work only because SCRIP independently adds the program's own directory. The dead entries are inert (a nonexistent list member is skipped by both engines — measured), so this changes no number today and I have **not** touched it: `beauty_self` carries **w=20**, the heaviest weight on the board, and repointing it would silently widen what those suites can see. **Named for HQ, not fixed on this row.**

## NOT IN THIS ROW (brief's own ⛔, honored)
The ~131 gimpel LIBRARY MODULES and their scorecard weight — Lon's knob, escalated at HQ-73. No driver programs were authored.

## NEXT
1. **HQ ruling on CLASS B** (asked, with the number): may the `RANDOM.inc` case correction land under HQ-73's precedent, and which `Trace` variant is canonical (or should `5ivesAlive.inc` cite `trace.inc`, already on lon's root list)? **Worth 25 of the 35 residue programs.**
2. The three dead `lib` entries above — one-token fix each, but `beauty_self` is w=20; wants a deliberate ruling, not a drive-by.
3. lon's 43 UNSCR is now dominated by classes no path fix reaches (ADDENDUM 1's inventory: `ERROR 217` inside `semantic.inc`, 8 stock-sbl SIGSEGVs, 1 timeout). ⛔ **The 8 sbl SIGSEGVs are stock-sbl fragility — do not "fix" them.**
