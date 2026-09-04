# FINDING — the `perf-nv-set-fn-o0-overhead` recipe gap is CLOSED, and closing it exposed a second defect: the ratchet was keyed to a SYMBOL, not to a COST

**Seat:** hq_P (PERFORMANCE) · **Date:** 2026-09-04 · **Mode:** FLEET-16 · **Row:** `perf-nv-set-fn-o0-overhead`
**Tree:** measured at SCRIP `ae9ebfc20`; gate landed at `aed3136bb` and **re-proven there after rebase, bit-identical** (the two commits rebased over touch no `src/`). corpus `7818e202e`, .github `72ada474` — all three ff-only pulled at session start, all three were BEHIND.
**Arm:** `-O0`, mode-4, N=20000 · **Instrument:** callgrind Ir at fixed work · **Oracle:** n/a (perf row, no oracle)
**Source edits: ZERO.** One instrument-lane file changed: `SCRIP/scripts/test_gate_nv_set_fn_ir_ratchet.sh`.

## 1. The recipe is recovered, and it was never lost — only unrecorded

The row's DONE-WHEN-HISTORY named this the taker's first task: the pinned figure (122,092 Ir) came from a direct
callgrind of the committed `roman.sno`, which runs **ten** iterations and is **compile-dominated**, while the row's
headline figures (kernel total 353,472,366 Ir; `NV_SET_fn` 46,453,125 Ir) came from a **scaled** kernel whose recipe
was not written down.

⭐ **The recipe was half-recorded the whole time, in the GOAL's own first sentence: _"Measured N=20000, mode-4, `-O0`"_.**
What was missing was not the *scale* but the *mechanism* — how to reach N=20000 at all. That is the `*BENCH` marker at
`roman.sno:24` plus `bench_wrap.sh`:

```bash
bash scripts/bench_wrap.sh corpus/benchmarks/snobol4/roman.sno --mode=iter --n=20000 -o k.sno
./scrip --compile -o k.s k.sno < /dev/null
gcc -no-pie k.s -o k.bin -L out -lscrip_rt -Wl,-rpath,out -lm -lpthread
valgrind --tool=callgrind --callgrind-out-file=cg.out k.bin < /dev/null    # census must read `check: 1102`, `iters: 20000`
callgrind_annotate cg.out | grep -E ':(NV_SET_fn|NV_CELL_IF_FASTSET_fn)\b'
```

- `--mode=iter`, never `--mode=time`: a wall-clock deadline under callgrind measures the **instrument's** throughput
  (`FINDING-2026-08-22-bench-harness-unmeasurable`).
- **mode-4, not mode-3**: mode-3 profiles compiler + kernel in one process; the compile intercept measures
  **67,525,993 Ir** here and swamps the signal.
- **Confirmation the scale is right:** the mode-3 fit predicts a total of **353,539,093 Ir** at N=20000 against the
  row's published **353,472,366** — **0.02%**. The scale is confirmed, not assumed.
- **Reproducible to the instruction:** two full runs gave a bit-identical family total. Whole recipe: **~3.3 s**.

## 2. ⛔ roman is NONLINEAR in N — a slope is not available here, and that is a property of the kernel

Store-family Ir per iteration, mode-4: **588 Ir/iter** over N=5000→10000 vs **700 Ir/iter** over N=10000→20000 — a **19%
divergence**, so `bench_ir_slope.sh` would correctly print `NONLINEAR` and refuse a slope.

The cause is in the kernel's definition, not the instrument: `ROMAN_RUN(N)` converts `1000+1 .. 1000+N`, so as N grows the
integers grow, the numerals get longer, and the work per conversion genuinely rises. **This is why the row pins a TOTAL AT
FIXED WORK and why N is part of the pin** (RULES.md § FACT RULES: a SLOPE is not a TOTAL). Recorded because the natural
instinct — "use the slope tool, it cancels startup exactly" — is wrong *for this kernel* and nothing else says so.

## 3. ⛔⭐ The second defect, which only appeared once the right quantity was measured: THE COST MOVED, IT DID NOT GO AWAY

Re-measured at the recovered recipe, `core.c:NV_SET_fn` reads **12,853,648 Ir (3.73%)** — against the row's headline
**46,453,125 Ir (12.46%)**. A **3.6x drop**. It is not a cure.

At SCRIP `702e2d162` (*"NV_CELL_IF_FASTSET_fn: one admission funnel for direct-cell stores; cures two oracle-graded wrong
answers"*) **the fast-path store — precisely what item 3 targets — was split out of `NV_SET_fn` into its own function.**
`NV_SET_fn` now calls it: **17,628,085 Ir inclusive, 183,613 calls** at N=20000.

Honest accounting at the recovered recipe, mode-4 N=20000, SCRIP `ae9ebfc20`:

| bucket | Ir | share |
|---|---:|---:|
| `core.c:NV_CELL_IF_FASTSET_fn` (the split-out fast path) | 12,944,539 | 3.76% |
| `core.c:NV_SET_fn` | 12,853,648 | 3.73% |
| `rt_protected.h:NV_SET_fn` (protected-pattern guard, inlined) | 2,019,666 | 0.59% |
| `gc_heap.h:NV_SET_fn` (write barrier, inlined) | 1,285,250 | 0.37% |
| **store family total** | **29,103,103** | **8.44%** |

Against seat07's fully-attributed **50,492,413 Ir (13.54%)** of 2026-08-24, the real reduction is **1.74x**, from other
people's work on the store path — **not** the 3.6x a symbol-keyed reading reports.

⭐ **THE TRANSFERABLE LESSON: AN ACCEPTANCE TEST A *REFACTOR* CAN SATISFY TESTS THE SPELLING, NOT THE MACHINE.** This is the
same shape hq_B caught on the sibling Prolog row, where `grep -c plc_ = 0` was closable by renaming ~200 refs of
must-survive code. ⛔ **The sharper half here is that the refactor was innocent and useful** — it cured two oracle-graded
wrong answers. **Nobody has to be gaming a symbol-keyed pin for it to go quietly wrong**; ordinary good work is enough.
A pin keyed to a *name* silently becomes a pin on a *different quantity* the moment someone moves code.

## 4. What landed

`test_gate_nv_set_fn_ir_ratchet.sh` rewritten: executes the recovered recipe and pins the **store-family sum**
`PIN=29103103` instead of a bare symbol. **Flat, not inclusive** — `--inclusive=yes` prints *two* entries for `NV_SET_fn`
(one keyed by absolute path, one by the `.so`) and a pin cannot choose between them without double-counting.

Proven by negative test, not asserted:

| arm | mutant | result |
|---|---|---|
| grades the real tree | none | **FAIL(1)**, 29,103,103 vs pin 29,103,103 — item 3's cure is not landed |
| can PASS at all | `PIN` raised | **rc=0** — the gate is not stuck red |
| census guard | `CENSUS="check: 9999"` | **REFUSES rc=2** — a crashed run yields a well-formed, *smaller* Ir figure, i.e. a spurious PASS |
| family vanished | family renamed in the regex | **REFUSES rc=2**, never passes |

The D-17 root derivation was incidentally proven too: the mutants, run from the scratchpad, refused rather than grading
the wrong tree.

## 5. ⛔ What this does NOT do

**Item 3 is still not cured and this row does not close.** The gate now grades the right quantity; it still reads FAIL(1).
seat05's finding stands unchanged: item 3's one identified lever (collapsing the
`g_comm_dbg`/`trace_set_n`/`monitor_fd` three-way check into one cached flag) **needs a NEW GLOBAL and therefore Lon's
explicit in-chat grant that session** — not available to an autonomous session. The banner-ready ask is already drafted on
the baton and is unchanged by this pass; what changed is that the measurement it would be graded against is now honest.

⚠️ **Newly visible and NOT pursued:** `NV_CELL_IF_FASTSET_fn` is now the single largest bucket in the family (12,944,539 Ir,
3.76%) and has never been attributed at source-line level by anyone — it did not exist when this row's attribution passes
ran. That is a candidate for its own row, flagged rather than taken (ROW FACTORY discipline).
