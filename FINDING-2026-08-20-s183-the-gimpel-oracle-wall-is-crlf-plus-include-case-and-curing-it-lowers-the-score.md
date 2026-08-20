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
