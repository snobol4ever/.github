# FINDING 2026-08-28 hq_P — `bench_correct` is **5/8**, not 0/8, and the residue is EXACTLY the three programs with a real `suspend` statement

Row: `icon-bench-correct-zero-of-eight` (ANNOUNCEMENT burn-down, rank 0) · MODE `FLEET-12` · SCRIP `e7bdff53` · corpus `5a6d91129` · RT_OPT `-O0`

## ⭐⭐ THE HEADLINE — THE ROW'S OWN NAME IS NOW WRONG

`bench_correct` scores **5 IDENTICAL / 3 CRASH**. The row, its GOAL line, its board table, and **two LEDGER
entries written earlier the same day (s278, s282)** all still say **0/8**. The 0/8 has been stale for some time
and nobody re-measured, for a reason given in this row's own baton — see THE PROCESS DEFECT below.

| program | real `suspend` stmts | s269 board | **MEASURED NOW** |
|---|---|---|---|
| `concord` | 1 | SIGSEGV (3 lines) | **CRASH** (3 lines, oracle 1345) |
| `geddump` | 5 | SIGSEGV (0) | **CRASH** (0, oracle 12568) |
| `tgrlink` | 6 | SIGSEGV (2) | **CRASH** (2, oracle 3239) |
| `ipxref` | **0** | SIGSEGV (0) | ✅ **IDENTICAL** (1230) |
| `rsg` | 0 | SIGSEGV (5000, died on 5001) | ✅ **IDENTICAL** (5000) |
| `micsum` | 0 | HANG (1) | ✅ **IDENTICAL** (2) |
| `deal` | 0 | RUNAWAY | ✅ **IDENTICAL** (17000) |
| `queens` | 0 | RUNAWAY | ✅ **IDENTICAL** (16653) |

**The correlation is exact, 8 of 8: every program containing a real `suspend` statement CRASHES; every program
without one PASSES.** No exceptions in either direction.

## HOW IT WAS VERIFIED (two instruments, two samples, and an empty-window guard)

1. `scripts/honest_icon_correctness.sh` run twice, standalone, no build in the tree: **identical both samples**,
   rc=0, `5 IDENTICAL / 3 CRASH`.
2. **Independent hand re-measurement** (not the harness): compile mode-4 with LINKDEPS, gcc-link, run under
   `OUTPUT=1 stdbuf -o0`, extract the same output window, compare by **md5**:
   `deal b6943cff · queens c5d54504 · rsg 9f82e322 · micsum 1addb1bb · ipxref 295675fb` — **oracle md5 == SCRIP md5
   for all five**, with oracle windows non-empty at 17000 / 16653 / 5000 / 2 / 1230 lines and `rc=0`.
   The non-empty check is deliberate: this harness's historical false-green was two EMPTY windows comparing equal.

## ⛔ CORRECTING THE s277 CORRECTION — IT UNDERCOUNTED, AND ITS PREDICTION IS WRONG IN BOTH DIRECTIONS

s277 established that this row was two defects, not one — that stands and is confirmed. But it counted with
`grep -cw suspend` and reported *"four of the eight contain ZERO `suspend`"*. **It is FIVE.**

⭐ **`ipxref`'s single "suspend" is a STRING LITERAL** — the word `"suspend"` inside a list of Icon reserved words
(`ipxref.icn:68-70`, `resword := [... "static","suspend","then" ...]`). It is data, not code. Stripping comments and
double-quoted strings before counting gives the true statement counts: `concord 1 · geddump 5 · tgrlink 6 ·
ipxref 0 · rsg 0 · micsum 0 · deal 0 · queens 0`.

⛔ This is the project's recurring instrument shape again — **a true measurement answering a narrower question than
the one it was read as** (`grep -cw` answers *does this token appear*, read as *does this statement occur*), the same
family as `command -v icont` answering *is it on PATH* read as *does it exist*.

**Consequence for N-2, and it is good news in both halves:**
- s277 predicted *"expect N-2 to move AT MOST 4 of 8"*. In fact the five without a real `suspend` **already pass, and
  they did not need N-2 at all.**
- N-2's remaining yield is therefore **exactly 3**, and it is the whole residue: **if N-2 works, this board goes to
  8/8.** A `bench_correct` reading below 8/8 after N-2 lands is a real shortfall, not a predicted partial —
  ⛔ **the "expect a PARTIAL move, re-triage the residue" guidance in this row's older LEDGERs is now VOID.**

## WHAT MOVED IT — NOT ATTRIBUTED, BUT BOUNDED, AND IT IS **NOT** N-2

⛔ **I did not identify the cure, and I am not claiming one.** What is established:

- **It is not attributable to any post-2026-08-24 SCRIP work, N-2 included.** A **`make pristine`** build of SCRIP at
  `50805987` (2026-08-24, the s269 era) already produces `micsum ✅ · rsg ✅ · queens ✅` against today's harness,
  corpus and oracle. The five were passing at the s269-era compiler.
- **It is not the harness's link handling**: `LINKDEPS` was already present at `5ad95ab1` (s269's own harness cure).
- **It is not the programs**: corpus history for `benchmarks/icon/` since 2026-08-23 touches only `.s` artifacts.
- Therefore, for those five, **the 0/8 was an instrument-or-environment artifact, not a compiler verdict.** This row's
  own QA section already recorded that the first 0/8 run was corrupted by a concurrent `make pristine`, and that the
  label was wrong for the first two of three runs — the same class, one turn further.

⭐ **And the number was already visible in the tree.** hq_C's commit `4fd35994` (2026-08-28 08:44) records in its own
message, as an aside, *"normal run rc=0 with the pinned board unchanged (**5 IDENTICAL / 3 CRASH**, tgrlink SIGSEGV
as before)"* — while this row's baton and two same-day LEDGER entries said 0/8. **Nobody was wrong; the two records
simply never met.**

## ⛔⭐ THE PROCESS DEFECT — A GUARD AGAINST PREMATURE MEASUREMENT BECAME A GUARD AGAINST MEASUREMENT

This row carried, in bold, in four places: **"DO NOT RE-SCORE `bench_correct` YET"**, on the sound reasoning that a
re-score before N-2 landed would just re-measure the same 0/8 and might let a wrong-answer pass be booked as a cure.

⛔ **The cost of that guard is now measured: the board changed and no one looked for four sessions.** s272, s273,
s274, s275, s276, s277, s278 and s282 each carried `0/8` forward as a premise **without re-measuring, because the row
told them not to.** A number nobody is allowed to re-take cannot be discovered to be stale.

⭐ **The transferable rule: a "do not re-measure" guard must carry an expiry or a cheap canary.** Forbidding the
expensive *acceptance* re-score is right; forbidding the *diagnostic* measurement that would notice the premise
changed is not. They were one prohibition here and should have been two.

## ⚠️ MY OWN INSTRUMENT ERROR THIS SESSION, RECORDED BECAUSE IT IS THE SAME FAMILY

My first bisect probe printed **three PASSes off a stale binary.** Moving the clone *backwards* to an older commit
broke the build (`No rule to make target .../src/ir/bb_pool.c` — stale `.d` deps from the newer tree), `make` exited
2, and the probe — which checked only that `scrip` *existed* — happily graded the previous checkout's binary.
⭐ Caught only because I printed `build rc=` beside the verdicts and the two disagreed. Cured before any use: the
step now `rm -f scrip` first, uses `make pristine`, and **refuses rc=2 on build failure** instead of probing.
⛔ Identical in shape to the defect this very row exists to document — *non-empty is not alive*, and a binary that
exists is not a binary that was just built.

## SCORE IMPACT (unbooked)

`bench_correct` is weight **15** of Σ95 (`scorecard_icon.sh:7,16`). `0/8 → 5/8` is **+9.87 Icon META points**
(`100·15·(5/8)/95`). Reaching 8/8 via N-2 adds **+5.92** more, for **15.79** from this suite alone. The row's own
GOAL line — *"Icon META cannot pass ~82 while it sits at zero"* — was true and is now unblocked by ~10 points that
nothing in the record has claimed.

## STATUS

⛔ **Row is NOT done and remains blocked**: DONE-WHEN requires every row CRASH-free, and the three real-`suspend`
programs still SIGSEGV. That cure is **N-2**, which is `ASSIGNED:seat01` and RUNNING — **not mine to write** under
FLEET-12. Queue row moved from a stale `FREE`/`hq_P`-claim mismatch to `PARKED-AWAITING:icon-n2-generator-activation-frames`
so the block is machine-readable instead of living only in prose (this row's picker-livelock, third recurrence).

Re-score criterion unchanged for acceptance: clean solo run, oracle verified present, every row CRASH-free,
`timeout 600s`, never a board and a build in one tree.
