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

---

## 7. ⭐⭐⭐ ADDENDUM — THE TWO "FALSIFIED" LEDGER ROWS ARE NOT FALSE. ALL FOUR NUMBERS ARE CORRECT, AND THE DEFECT IS ONE LEVEL DEEPER THAN BASENAMES.

s224 recorded: *"⛔⛔ `RTX-CLAIMS.md` row `rt_call_arr_gen` reads `0` arrivals, `0/22`, `NOT-A-TARGET:PHANTOM-BY-EXECUTION`. MEASURED THIS SESSION: **2,815,800**"* and *"row `rt_arg_stage` reads `8` / `1/22` / `BLOCKED:MEASURED-ZERO`. MEASURED: **812,824**"* — two shared-ledger verdicts *"falsified by 5–6 orders of magnitude."*

**MEASURED BOTH WAYS, `util_rtx_count_syms.sh`, gate ON, `-O0`:**

| symbol | on the 22-program BOARD (`bench/`) | on `rung10_programs_puzzle_19.pl` |
|---|---|---|
| `rt_call_arr_gen` | **0 arrivals, reach 0/22** | **2,815,800** |
| `rt_arg_stage` | **8 arrivals, reach 1/22** (all 8 in `crypt.pl`) | **812,824** |

⇒ **the board columns reproduce the ledger rows EXACTLY** — `0`/`0/22` and `8`/`1/22`, digit for digit.
⇒ **s224's two figures also reproduce EXACTLY** — verified here independently: 2,815,800 and 812,824.
⇒ **NOTHING WAS FALSIFIED. All four numbers are true.** The ledger's columns are **board-wide arrivals and
reach-out-of-22**; s224 measured a **different workload** (`puzzle_19`, md5 `de5c1c9f…`) and compared its
count against a board-keyed row. **Two correct measurements of two different things.**

⛔ **THIS IS s224'S OWN DEFECT ONE LEVEL UP, AND IT SUBSUMES IT.** s224 named the disease *"measurement
keyed on basename"* — file identity not recorded. The ledger episode is **workload identity not recorded.**
Same disease, next level: **a count was written down without the thing it was a count OF.**
⇒ **THE FACT RULE SHOULD BE STATED ONCE, GENERALLY, NOT TWICE NARROWLY:** every recorded measurement
carries **(a) full path + `md5sum` of the program(s)** *and* **(b) the workload set and its size.** A bare
integer in a ranking column is unfalsifiable and, worse, *refutable-looking* — which is exactly how two
correct rows came to be marked false.

⭐ **THE INTERESTING FINDING THE "FALSIFICATION" WAS HIDING:** the board takes `rt_call_arr_gen` **zero
times in 22/22 programs** while `puzzle_19` takes it **2.8 M times.** That is not a bad ledger row — it is a
**coverage hole in the ranking corpus**, and it is far more actionable than a wrong verdict would have been.
The board cannot see an entire dispatch path that one rung-test program hammers.

⛔ **CONSEQUENCE FOR s224'S LANDED HOIST — IT IS WORKLOAD-SPECIFIC AND MUST BE LABELLED, NOT RETRACTED.**
The 1.047× (base 2844 → hoist 2716) was measured on `puzzle_19`, where the symbol takes 2.8 M calls. **On
the board the hoist is invisible by construction: 0 calls, 0/22.** The change is one line of C, free, and
correct — **keep it** — but its win belongs to `puzzle_19`'s workload and may not be quoted board-wide.

⛔⛔ **CROSS-LADDER HAZARD, AND IT IS THE URGENT PART.** `rt_arg_stage`'s `BLOCKED:MEASURED-ZERO` row is
**ICON-RTX's**. If *"falsified at 812,824"* reaches that ladder unqualified, it invites unblocking and
porting a symbol that takes **8 calls across the entire board.** The row is right. **Do not unblock it on
this evidence** — unblock it only if `puzzle_19`-class workloads are added to the board *as board members*,
which is a corpus decision, not a measurement.

### IDENTITY KEYS (the owed FACT RULE, applied to this session's disputed files)
```
de5c1c9f2321e5d678abb71cda4f47f1  corpus/programs/prolog/rung10_programs_puzzle_19.pl
fd781da367ab354c819f19b812218ad7  corpus/benchmarks/prolog/bench/queens.pl      = 430,081 (the board figure)
4b27b1d9004df817f4b73b34d87b2edd  corpus/benchmarks/prolog/vanroy/queens.pl     = looped wrapper, rc=124
c77a63aad44b535ce947463e20000ab9  corpus/programs/prolog/queens.pl              = N=6, 12,957
588e35e93b0bb9a830eb2fcd3ec2abea  corpus/benchmarks/prolog/bench/crypt.pl       = the only rt_arg_stage site on the board
```
⚠ Note `4b27b1d9…` is the md5 **s224 cited for the 430,081 file**; it is in fact the looped `vanroy` variant
it had itself clocked at rc=124. The 430,081 file is `fd781da3…`. **The keys settle it; prose could not.**
