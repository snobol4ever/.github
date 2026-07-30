# FINDING s225-PL (2026-07-30) — ⭐⭐ THE s221 BOARD IS `benchmarks/prolog/bench/` (22 FILES), AND IT REPRODUCES 2,060,043 / 19-OF-22 TO THE DIGIT IN MODE 3. THE PLCALL KILL-SWITCH GATE NOW PASSES ON PROLOG. ONE BANKED DEFECT IS PATH-SPECIFIC, NOT REAL.

**Ladder:** `PL-RTX` (`GOAL-PROLOG-RTX.md`) · **Contract:** `ARCH-PROLOG-RTX.md` · **Ledger:** `RTX-CLAIMS.md`
**Tree:** SCRIP `8437c3d7` on origin + s224's local `440f7d6d`. RT_OPT=`-O0`. **Zero source edits s225.**

---

## 0. ⛔ PRIORITY STATEMENT — s224-PL GOT HERE FIRST AND THIS FINDING DOES NOT CLAIM ITS RESULTS

**s224-PL struck item 0, named the basename root cause, resolved the queens gap by `md5sum`, falsified two
shared-ledger verdicts, and voided s223's false `PUSH BLOCKED` banner — all before this session ran.** s225
reached the same conclusion about item 0 **independently and second**, sharing a container with s224 without
knowing it. Where this finding overlaps s224, **s224 has priority and the better method** (it measured
`scrip`'s own exit status and caught its own pipeline-`$?` error; it keyed files by `md5sum`).

**s225's contribution is narrow and is exactly one of s224's own NEXT items:** *"re-rank the s221 board with
full-path+md5 keys and re-audit every verdict derived from it."* That is discharged below.

## 1. ⭐⭐ THE BOARD IS A FIFTH DIRECTORY — `benchmarks/prolog/bench/`, 22 FILES — AND IT MATCHES TO THE DIGIT

s224 measured `benchmarks/prolog/vanroy/` (**21** files) and inferred the match from reach alone:
*"19/21 matches the s221 board's 19/22 reach exactly."* Reasonable — but the board is a **different
directory with a different file count**, and it does not need inferring. Measured, `scrip --run`, all 22:

**`benchmarks/prolog/bench/` — 22 files, 22/22 rc=0, zero `[IBB] FATAL`.**

Census (`util_rtx_arm_census.sh`, gate ON) over all 22, symbol `rt_proc_call_open_det`:

| | s221 board figure | s225 re-measured, mode 3 |
|---|---|---|
| corpus-wide ENTRIES | **2,060,043** | **2,060,043** |
| reach | **19/22** | **19/22** |
| BAILED_C | 0 | **0, every program** |

Per-program: `queensn` 1,596,708 · `queens` 430,081 · `zebra` 14,483 · `sendmore` 9,380 · `meta_qsort` 3,656 ·
`ham` 1,642 · `crypt` 1,394 · `mu` 606 · `queens_8` 556 · `nrev` 528 · `nreverse` 496 · `qsort` 376 ·
`query` 127 · `cal` 5 · `derive`/`divide10`/`log10`/`ops8`/`times10` 1 each. Zeros: `deriv` · `fib` · `tak`.

⇒ **the s221 board was measured in mode 3 from `bench/`.** Not inferred — reproduced. Item 0 is closed twice over.
⇒ s224's four-directory census becomes **five**: `bench/` · `vanroy/` · `src/swi-vanroy/` · `src/gnu-examplespl/` · `programs/prolog/`.
⇒ **perf vehicle:** `bench/queensn.pl` = **1,596,708 arrivals, 78% of board traffic** in one rc=0 program.

## 2. ⭐ A SMALL CORRECTION TO s224(2)(a), AND IT IS THE BASENAME RULE BITING ITS OWN DISCOVERER

s224 attributes **430,081** to `vanroy/queens.pl` (N=16, md5 `4b27b1d9…`). But `vanroy/queens.pl` is a
**looped** wrapper (`main :- l__(1)`, real work under `bench__main`) and under a 60 s timeout it returns
**rc=124** — s224 measured that itself. The file that censuses to **exactly 430,081** is
**`bench/queens.pl`** (`main :- queens(16, R), write(R), nl.`), measured here.
⇒ **THREE files are named `queens.pl`, not two:** `bench/` (N=16, **430,081** = the board figure) ·
`vanroy/` (N=16, looped, times out) · `programs/prolog/` (N=6, **12,957**).
⇒ s224's N=6-vs-N=16 explanation of the 33× **stands and is correct**; only the path label moves.
⇒ This is the sharpest possible endorsement of s224's owed FACT RULE: **the session that discovered
basename-keyed measurement was itself off by one directory on a basename.** Full path + `md5sum`, always.

## 3. ⭐ `meta_qsort`'s "REAL BANKED DEFECT" IS PATH-SPECIFIC — RE-EXAMINE BEFORE BANKING

s224 recorded `vanroy/meta_qsort.pl` ⇒ **rc=134 `rt_pl_cterm: island exhausted`**, calling it *"a real banked
defect."* Measured here: **`bench/meta_qsort.pl` ⇒ rc=0, correct completion, 3,656 arrivals.**
⇒ the crash is **not** a property of `meta_qsort` the program; it is a property of that path's variant
(the looped wrapper drives far more search). ⛔ **Do not bank it as a general defect** — bank it as
*"`vanroy/meta_qsort.pl` exhausts the cterm island under the loop wrapper"*, which is a different and
much narrower claim. **Fourth consequence of the basename habit, found while confirming the third.**

## 4. ✅ OWED ITEM DISCHARGED — THE PLCALL KILL-SWITCH GATE PASSES ON PROLOG, BOTH MODES

s223 generalized `test_gate_rtx_killswitch_sets.sh` with an `EXT` param but **launched the Prolog sweep
without completing it**; it appears in no later cursor. Completed:

`test_gate_rtx_killswitch_sets.sh PLCALL <bench> 4 both pl` ⇒
**`[m3 --run] IDENTICAL=22 QUARANTINE=0 MOVER=0`** · **`[m4 --compile] IDENTICAL=22 QUARANTINE=0 MOVER=0 SKIP=0`** · **GATE PASS.**

N=4 per arm. ⇒ ON/OFF/PRISTINE are output-identical across the entire board in **both** media. Combined with
s223's falsification probe (164/0 → 111/53 on deliberately broken asm), RTX-1-PL's correctness case is closed.

## 5. WATERMARK / STATE

- Prolog watermark re-proved at session start: **164/164 interp + 164/164 compile, FAIL=0.**
- **Zero source edits.** No perf claim. The `.so` used was s224's build (mtime 12:41) carrying its
  uncommitted `$between` hoist — correctness results are unaffected in kind; **no timing taken from it.**
- s224's `440f7d6d` is **left untouched**: it is another session's live, unpushed work in a shared container.

## 6. ⛔ PROCESS — I MADE THE SAME CLASS OF ERROR I CAME TO WRITE UP, TWICE IN ONE SESSION

**(a) I accused the parallel session of fabricating a commit.** `git show --stat --no-patch --oneline 440f7d6d`
printed no file list; I read that as *an empty commit asserting work never done.* It is a real one-line change
to `by_name_dispatch.c` — `git diff --stat` shows it plainly. **The flag suppressed the stat, not the change.**
**(b) I drafted this finding as a discovery of item 0's falsity** without checking whether the goal file had
moved under me. s224 had already struck it, in this same working tree.
⇒ Both are the s223 shape exactly — *"promoted a tool artifact into a false claim, for want of one command"* —
and I hit them **while reading s223's retraction of that identical mistake, and s224's improvement on it.**
⇒ **The cheap check that would have caught both: re-read the artifact you are about to contradict, at HEAD,
immediately before writing.** For (a) that is one `git diff`; for (b) one `view` of the cursor.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
