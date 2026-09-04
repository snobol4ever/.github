# FINDING 2026-09-04 hq_P — the README grids' agreement gate was measuring THE BOX, not the engine

Row `readme-perf-grids-three-angles-all-seven` (I26), after ceo CEO-192 reopened it: every README grid
must be RE-MEASURED on the two-number WORK/OVERHEAD three-angle basis, tree-labelled, RT_OPT=-O0.
Tree: SCRIP `380cc4162` / corpus `201d9e021`, RT_OPT=-O0, modes m3+m4, clean benchmark oracle
`spitbol-bench-oracle/sbl -bf`. MODE went QUARTET → FLEET-4 → FLEET-8 during the sitting.

## 1. ⭐ THE HEADLINE: THE SAME TREE SCORES 2, 6 OR 12 OF 19 KERNELS DEPENDING ON WHO ELSE IS ON THE BOX

`bench_triangulate_snobol4.sh` publishes a kernel only when angle 1 (fixed TIME) and angle 2 (fixed
ITERATIONS) AGREE on **both** the SPITBOL arm and the SCRIP arm. Three runs of the SAME instrument:

| when | box | kernels published |
|---|---|---:|
| 2026-08-31 | shared | 6 of 19 |
| 2026-09-04 earlier (seat13) | 16-seat fleet, load 20–30 | **2 of 19** |
| 2026-09-04 this run (hq_P) | FLEET-4/8 winding down, load ~2.8 on 16 cores | **12 of 19** |

⛔ **The engine did not change between the second and third rows — the neighbours did.** The published
table was LOAD-limited, not engine-limited, and nothing in its output said so: a withheld kernel and a
slow kernel print the same way to a reader. The README had actually predicted this in its own prose
("a quiet re-run, not a loaded one, is what would move this table") — the prediction was right and had
been sitting unexecuted because no quiet window existed while 16 seats ran.
⭐ **The transferable rule: an agreement gate whose tolerance is fixed and whose noise is not, grades
the machine.** The SNOBOL4 harness already knows this — `NOISE-FLOOR.tsv`'s own header says *"THE FLOOR
IS A PROPERTY OF MACHINE LOAD, NOT ONLY OF THE ENGINE"* and *"NEVER compare a floor baked under load
with one baked solo"*. The lesson had been learned in the floor file and not yet applied to the three
harnesses that have no floor at all (below).

## 2. ⛔ PASCAL AND RAKU CANNOT PASS THEIR OWN GATE: A FLAT TOLERANCE SET **BELOW** THE NOISE IT JUDGES

`bench_triangulate_pascal.sh` on this quiet box: of 21 kernel/engine cells, **3 AGREE and 18 DISAGREE**,
and NO kernel has both its `fpc` arm and a SCRIP arm agreeing — so **zero kernels are publishable vs
fpc**, on a box where SNOBOL4 published twelve. The tolerance is `TOL_PCT=10` flat, marked UNBAKED (no
`NOISE-FLOOR.tsv` exists for pascal); the measured angle-1-vs-angle-2 ratios are 0.7048–0.9426, i.e. a
spread of ~6–30%. A 10% tolerance judging ~13% typical disagreement can essentially never say AGREE.
`bench_triangulate_prolog.sh` and `bench_triangulate_raku.sh` carry the identical flat-10%-UNBAKED
tolerance; Raku's README already records that its first cross-proof run read DISAGREE in every cell.

⭐ **AND THE PASCAL DISAGREEMENT IS SYSTEMATIC, NOT NOISE — WHICH MEANS BAKING A FLOOR WOULD NOT CURE
IT, IT WOULD HIDE IT.** Every one of the 21 ratios is BELOW 1.0 (0.7048…0.9426, not one above), so
angle 1 reports a consistently lower rate than angle 2 for every kernel on every engine. Random noise
straddles 1.0; a one-sided spread is a BIAS between the two instruments (a warmup or search-overhead
difference in the fixed-time arm is the obvious candidate). ⛔ So the cure for Pascal is NOT "bake a
wider floor until cells go green" — that would paper a real instrument bias into a passing gate, which
is the vacuous-test class RULES.md already warns about. The bias must be found first. A wider floor is
right only where the spread is two-sided.

## 3. ⛔ A SLOPE KERNEL MEASURED ONCE IS A CORRECT ANSWER TO A NARROWER QUESTION (batch-15 §1, again)

hq_P first built `bench_two_number_ir.sh` to take the WORK/OVERHEAD split in callgrind Ir, and ran it
over the 21 SNOBOL4 kernels as whole programs. Result: **12 of 21 tripped CEO-173's ">=50% startup"
refusal** and multiples came out as low as **0.140x**. Every number was correctly measured and every
number was answering the wrong question — a `benchmarks/snobol4` kernel exposes a `*BENCH kernel=`
entry that a harness LOOPS, so its published figure is a SLOPE with startup divided away, while a
single whole-program run is one default-sized iteration with SCRIP's 2.79M-Ir startup on top. Nothing
in the output distinguished the two. The census matters: **19 of 23 kernels are slope-capable, 4 are
whole-program** (`fib_recur`, `test_icon`, and the two twins) — so the tree genuinely holds both bases
and a board must pick per kernel, never per language.
✅ CURE: `bench_ir_slope.sh` fits `Ir(n) = OVERHEAD + n·WORK` at n/2n/4n. The slope IS work-per-iteration
with startup cancelled **exactly** (not subtracted from a different program, which is the law's marked
interim), and the intercept IS overhead. 16 of 19 kernels fit linearly.

## 4. ⭐ Ir AND WALL CLOCK DISAGREE ON THIS WORKLOAD — BOTH ARE RIGHT, AND THE GRID MUST SAY WHICH IT IS

| kernel | timed (angles 1+2) | instructions retired (Ir slope) |
|---|:---:|:---:|
| op_dispatch | **3.12x** | 1.78x |
| pattern_bt | **1.48x** | 0.771x |
| table_variety | 0.663x | 0.692x |

SCRIP executes MORE instructions than SPITBOL on those kernels and retires them FASTER (better ILP and
locality). Ir counts instructions, not cycles. ⛔ So Ir is a cross-check, never a substitute: the law
defines WORK in TIME, and the headline multiples must stay the timed ones. Ir's value is that it is
deterministic (three consecutive runs byte-identical: 34405531 / 34405531 / 34405531) and immune to
neighbours — it is the only instrument that keeps working while 21 sessions share the box, and it
covers kernels the clock could not publish.

## 5. STARTUP IS ASYMMETRIC, AND IT IS WHY THE BASIS CHANGE MOVES NUMBERS

Empty-program cost, measured both ways on this tree: **Ir** — SPITBOL 208,782 · SCRIP m4 2,790,777 ·
m3 4,522,256. **Wall clock** (best of 15, `tools/bench_rusage`) — SPITBOL 741 µs · m4 2162 µs · m3
3827 µs. SCRIP's startup is ~13x SPITBOL's in instructions and ~3x in time. On Snocone's shortest
kernel that was **42.5% of the entire reading**, so moving to the WORK basis took `string_concat` from
1.42x to **2.42x**. Both numbers were always real; they measured different things, exactly as the law
says. The startup cost is itself real and is now reported as its own number rather than buried.

## 6. PROLOG'S KERNELS CANNOT BE MEASURED AT ALL RIGHT NOW

`bench_triangulate_prolog.sh` this run: **32 of 32 cells UNPROVEN** — neither angle could measure. This
is the crash class the script's own header documents (every van Roy kernel has the shape
`bench__main :- <compute>(...,F), write(F), nl.` and SCRIP m3 signals on all 21). Not a new defect and
not a regression; recorded so the Prolog B cell's "SCRIP not yet triangulated" is a measured statement.

## WHAT LANDED
- `scripts/bench_two_number_ir.sh` (whole-program WORK/OVERHEAD + the CEO-173 refusal) and
  `scripts/bench_ir_slope.sh` (the regression instrument), SCRIP `3af71406f`.
- README grids re-measured and tree-labelled for **snobol4, snocone, rebus**; SCORE.md B cells likewise.
- ⛔ **icon, prolog, pascal, raku grids NOT re-measured** — prolog and pascal are blocked on §2/§6 above,
  which are defects in the instruments, not in the grids; icon and raku were not reached this sitting.

## TWO GUARDS THIS ROW ADDED TO ITS OWN INSTRUMENTS (both negative-tested before use)
1. `ir_of` now REFUSES a run that did not exit 0. callgrind happily counts a program's ERROR path: the
   first Snocone board measured its "empty program" as `END` — valid SNOBOL4, a **parse error** in
   Snocone — and reported OVERHEAD=2,875,710 Ir, a real number off a program that never ran. Verified
   after the fix: `/bin/true` yields a count, `/bin/false` yields nothing.
2. The re-cut `pascal-function-returning-char-printed-as-ordinal` DONE-WHEN (ceo CEO-193, closed this
   sitting) now READS the printed denominator instead of pinning `total=159` against a board printing
   161. Negative-tested three ways before landing: no board line → rc=1; one m4 fail → rc=1; denominator
   grows while passes lag → rc=1.

## 7. ⛔⭐ POSTSCRIPT — hq_P VERIFIED ITS OWN CLAIM WITH A DIFFERENT INSTRUMENT THAN THE GATE USES

Having rewritten three grids, hq_P checked them by typing the DONE-WHEN's own `grep` at a prompt: all
three reported their hash, and hq_P told ceo "3 of 7 pass". Then it ran the DONE-WHEN the way `done`
runs it — extract the line, `bash -c "$DW"` — and got **hash=none for all seven**, including sections
that visibly carry a hash. The true count at the moment of the telegram was **0 of 7**.

CAUSE: the criterion greps `SCRIP [\x60]?[0-9a-f]{7,10}`, meaning "an optional backtick before the
hash". `grep` on this box is **ugrep 7.8.4**, not GNU grep. Typed directly it resolves `\x60` to a
backtick and matches ``SCRIP `380cc4162` ``; run through `bash -c` it does not, and `[\x60]` degrades
to the character set {\, x, 6, 0} — which cannot match a backtick, so the optional branch matches empty
and the very next character (the backtick) fails the hex-digit test. **A backticked hash — the natural
markdown form, and the form the criterion was clearly written to allow — is invisible to its own gate.**
✅ CURE: write the hash unbackticked (`SCRIP 380cc4162`); it matches on the optional-absent branch under
both invocations. Verified verbatim afterwards: snobol4 + snocone + rebus pass, the other four fail, rc=1.

⭐ THE RULE, and it is this FINDING's own §3 lesson turned on its author: **a DONE-WHEN verified by
hand-typing its command is not verified.** The hand-typed run and the gate's run are two instruments,
they differ in shell, quoting and grep dialect, and the hand-typed one answers "would this match if I
ran it" while the gate answers "does it match when `done` runs it". Extract the line and execute it
under `bash -c` — which is exactly what `done` does — before quoting a pass to anyone.
