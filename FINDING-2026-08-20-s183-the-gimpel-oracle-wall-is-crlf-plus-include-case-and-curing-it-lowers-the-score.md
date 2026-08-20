# FINDING s183 — THE GIMPEL ORACLE WALL IS CRLF + INCLUDE-NAME CASE, AND CURING IT **LOWERS** THE SCORE

**Seat:** seat1 (Opus 5), 2026-08-20, queue row 3 `oracle-format-unscr`. **Tree:** SCRIP `943e404a`, corpus `7a5515fd`. **Zero stock-sbl edits** — the `x64` tree is verified clean (`git status --porcelain` empty).
**Brief:** *"THE CHEAPEST META POINTS ON THE BOARD … sbl answers ERROR 214 on the classic column format these suites are written in."*

## ⛔ THE BRIEF'S PREMISE IS FALSIFIED IN THREE PLACES — ALL MEASURED
| brief says | measured |
|---|---|
| `ERROR 214` | **`ERROR 230` — syntax error: illegal character**, at exactly one column past each line's last visible character. `ERROR 214` occurs on **one file out of 145**. |
| "classic **column format**" | **CRLF line endings.** Nothing to do with column conventions. |
| gimpel **and** lon are one format defect | **lon has ZERO CRLF.** Its failure is `ERROR 285 — include file cannot be opened`, an include-**root** problem, a different defect. |

## THE TWO REAL DEFECTS IN GIMPEL, BOTH CURED (pure corpus normalization)
1. **CRLF line endings — 143 of 145 files.** The trailing `\r` is the illegal character. Stripped.
2. **`-INCLUDE` name CASE MISMATCH — 57 of 60 distinct names.** The Gimpel library was authored on a case-insensitive filesystem: `-INCLUDE "seq.sno"` resolved to `SEQ.sno` there and resolves to nothing here. **129 spellings corrected across 75 files** to the on-disk names. ⛔ Files were **NOT renamed** — correcting the reference is the minimal normalization and leaves every other citation of these modules intact.

## RECEIPTS — ORACLE CENSUS OVER ALL 145 FILES, BEFORE AND AFTER
| class | before | after |
|---|---|---|
| `ERROR 230` (CRLF) | **78** | **0** |
| `ERROR 285` (include) | **78** | **3** — `resolution.sno`, `stringout.sno`, `system.inc`, genuinely absent from the corpus |
| **`No END statement`** | 65 | **131** ← the irreducible blocker, unmasked as the other two cleared |
| scorable (sbl rc=0) | **0** | **10** |

## ⭐⭐ THE HEADLINE THE BRIEF DID NOT ANTICIPATE — **CURING THE ORACLE LOWERS THE NUMBER**
| suite | SCORE before | SCORE after | UNSCR before | UNSCR after |
|---|---|---|---|---|
| gimpel | **0.0** (N=0) | **20.0** (N=10) | 145 | **135** |
| lon | 33.3 (N=21) | 33.3 (N=21) | 78 | 78 (correctly unmoved — no CRLF to fix) |
| **META (these two suites, w=10)** | **33.3** | **26.7** | | |
Both runs are complete 244-row runs (`test-results/sc-gimpel-lon` → `sc-gimpel-lon-after`); a mid-run report was read at 198 and again at 222 rows and **discarded as partial**, not reported.
**WHY IT FELL:** with N=0 gimpel contributed *nothing* to META; with N=10 it contributes 20.0 at weight 5, so META = (20.0×5 + 33.3×5)/10 = 26.7. **The normalization did not regress anything — it made ten previously-invisible rows visible, and SCRIP fails eight of them.** ⛔ **"The cheapest META points on the board" is exactly backwards for this suite:** UNSCR was *hiding* SCRIP failures, and curing the oracle converts hidden rows into scored reds before it converts any into greens. Any future row that proposes buying META by fixing oracle plumbing must price this in.

## ⛔ WHY `UNSCR < 10` IS UNREACHABLE BY NORMALIZATION — THE ROW'S DONE-WHEN CANNOT BE MET
After both cures, **131 of 145 gimpel files answer `No END statement found`.** They are **LIBRARY MODULES** — a `DEFINE` plus a `:(X_END)` label, no main body, no `END`, **no output to score**. `AGT.sno` is the archetype: it defines `AGT(S1,S2)` and stops. Reaching `UNSCR < 10` would mean **authoring ~131 driver programs**, which is a different rung and arguably the wrong shape (a library module has nothing to diff). **gimpel UNSCR 145 → 135 is the ceiling for this row as written.**

## THE LON HALF — NOT MINE TO DECIDE, ROUTED NOT FREELANCED
lon's 78 UNSCR is `ERROR 285`, and its includes **do exist** — in `corpus/programs/include/` and `corpus/programs/snobol4/demo/beauty/`. The harness runs sbl with `SETL4PATH=.` and SCRIP with `SNO_LIB=<progdir>`, so **neither engine can see them**; measured, a corrected `SETL4PATH` flips several lon rows from `ORACLE_FAIL` to a live oracle immediately. A further **~20 include names are absent from the corpus entirely** (including an absolute `/home/build/bin/portable.sno` and several `../`-relative forms). Fixing this means editing `scorecard_snobol4.sh` (**harness — not sbl, not corpus**) and possibly teaching `SNO_LIB` a path **list**, both outside this row's "normalize the corpus" mandate. **Asked `hq/q-oracle-format-unscr`; row HELD, not done.**

## NEXT
1. **HQ ruling** on (a) re-scoping gimpel to its ~10 runnable programs vs. minting a driver-authoring rung, and (b) whether the lon include-root fix is this row or a new one.
2. If the include-root fix is granted: one `SETL4PATH`/`SNO_LIB` change serves **both** suites — gimpel's residual 3 and lon's 78 are the same class.
3. Price the "UNSCR hides reds" effect into any future META-buying row (see the headline above).

---

# ADDENDUM 1 (s184, seat1, same row) — THE LON HALF IS NOW MEASURED: THE INCLUDE ROOT IS WORTH **35 ROWS**, AND `UNSCR < 10` IS UNREACHABLE THERE TOO

The body above routed the lon half to HQ without a number, which made the ruling expensive. It is now priced. **Zero corpus edits, zero harness edits, zero stock-sbl edits** — this is a measurement in a scratch pool, nothing landed.

## METHOD — THE CEILING ARM
`SETL4PATH` in stock sbl is a **PREFIX, NOT A PATH LIST** (measured: `SETL4PATH=/dir` SEGVs, `SETL4PATH=/dir/` works, `.:/dir/` SEGVs, `/dir:.` is silently treated as one prefix). So the "include root solved" ceiling cannot be expressed as a list; it was built by pooling every candidate include into ONE flat scratch dir (`programs/include{,/ebnf}`, `probe/fwctx`, `demo/beauty`, `beauty_suite`, `csnobol4-suite`, `gimpel`, and lon's own four dirs), plus lowercase symlinks for the case class, then running all 99 lon programs against that prefix. 493 files, 726 entries with case links. Collision risk checked, not assumed: `semantic.inc` — the only pooled file that errors — has **three copies in the corpus and all three are byte-identical** (md5 `8689a727`), so the pool did not silently pick a wrong variant.

## RESULT — 99 lon PROGRAMS, sbl rc=0 IS "HAS A LIVE ORACLE"
| arm | scorable (rc=0) | UNSCR |
|---|---|---|
| baseline `SETL4PATH=.` (what the harness does today) | **21** | 78 |
| pooled includes (the ceiling) | **56** | **43** |
**35 rows flip fail→pass. ZERO regress** (checked both directions explicitly). Baseline 21 reproduces the body's N=21 exactly, so the arm is calibrated.

## ⛔ THE ANSWER TO THE ROW'S DONE-WHEN: **lon `UNSCR < 10` IS UNREACHABLE, FOR A DIFFERENT REASON THAN GIMPEL'S**
Even with a perfect include root, **43 of 99 still have no live oracle**, and none of the residue is include-path:
| residue class | rows | what it is |
|---|---|---|
| `ERROR 217` in an included module | 21 | real content sbl rejects (`semantic.inc(18)`, the EVAL/OPSYN block) — inclusion-order/context dependent, not a missing file |
| `ERROR 285` still | 15 | the ~15 include targets **genuinely absent from the corpus** (`BCP.sno`, `debug.sno`, `export.sno`, `directs.sno`, `findname.sno`, `portable.sno`, `host.sno`, `HTML.sno`, `ini.sno`, `nmake.sno`, `ss.sno`, `transl8tweetish.sno`, `URL.sno`, `utility.sno`, `OConners-Generator.sno`) — including an absolute `/home/build/bin/portable.sno` |
| **stock sbl SIGSEGV** | 8 | `Listen2TwitterFiles`, `addMsg`, `blob`, `bootstrap`, `build`, `mm`, `OConners-Generator`, `tsql` — ⛔ **stock-sbl fragility, not ours; do not "fix"** |
| timeout | 1 | `peg_solitaire` |

## ⭐ THE CORRECTION THIS ADDENDUM MAKES TO THE BODY
The body reported gimpel's blocker as "131 files are LIBRARY MODULES with no END". **That diagnosis does NOT transfer to lon, and the pooled arm proves it: only 4 of 99 lon files genuinely lack an `END` statement.** The `No END statement` that 31 of the remaining rc=1 rows print is a **CONSEQUENCE** — a failed `-INCLUDE` (or an `ERROR 217` inside one) aborts the compile before `END` is ever reached. Reading it as gimpel's root cause would have sent the next seat to author drivers lon does not need. **Two suites, two different walls, one identical symptom string.**

## THE RULING IS NOW CHEAP — (b) RESTATED WITH ITS PRICE
Fixing the include root buys **+35 scorable lon rows** and cannot be done as a path list (sbl takes a prefix). The three shapes, none landed:
1. **Harness** — `scorecard_snobol4.sh` learns a per-suite library dir (and `SNO_LIB` a list). Not corpus, not sbl. Cheapest, one edit, serves gimpel's residual 3 too.
2. **Corpus duplication** — copy the include set into each of lon's **four** program dirs (`lon/`, `lon/sno/`, `lon/eng685/`, `lon/rinky/`). In-mandate but 4x duplication of files that live in `probe/fwctx` — a PROBE dir, not a library.
3. **Corpus reference rewrite** — rewrite every `-INCLUDE` to a `../`-relative path. In-mandate, but 82 distinct names x 4 source dirs against targets scattered over five trees.
**⛔ STILL HELD, STILL NOT FREELANCED:** all three are structural corpus/harness decisions, and the row's mandate is "normalize the corpus". **Whichever is chosen, lon `UNSCR < 10` does not follow from it** — 43 rows fail for reasons no include fix reaches. As with gimpel, the row's threshold rests on a premise the suite does not satisfy.

## PRICE THE HEADLINE AGAIN
The body's law holds and now has a second instance: **UNSCR hides SCRIP reds.** Flipping 35 lon rows into scored rows converts hidden rows into visible ones before it converts any into greens, so this rung too should be expected to **lower** META before it raises it. Any META-buying row must price this.
