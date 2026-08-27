# FINDING — N-2 item 2 step 1: the host edge is not a CALL node, and `main` is not representative — the forward-reference hazard is REAL, 3 edges in 2 of the 8

**Seat:** `hq_P` · **Date:** 2026-08-27 · **Mode:** FLEET-12
**Row:** `icon-n2-generator-activation-frames` step 1 (blocks `icon-bench-correct-zero-of-eight`, weight 15)
**Landed:** SCRIP `5cf65ded` — predicate is **INERT**, `getenv`-gated, zero emission change.

## Two corrections to the step-1 design, both measured

### 1. ⛔ The host edge is `IR_PROC_GEN`, not a call op — and the NODE KIND IS THE PREDICATE

The rung said *"scan `g_emit_cfg->all[]` for a DIRECT call whose callee is `is_generator` in the stage2 proc
table."* Implemented literally (`IR_CALL` / `IR_CALL_PROC_STAGED` + proc-table lookup) it found **`hosts=0` on the
canonical four-line witness** — a program whose entire purpose is that `main` calls a generator.

⭐ **`lower_icon.c:148` already did the work and encoded the answer in the OPCODE:**
`build(cx, icn_proc_is_generator(name) ? IR_PROC_GEN : (gb ? IR_CALL_BUILTIN_GEN : IR_CALL))`, with
`IR_LIT(call).sval = name`; `:1374` rewrites the same way post-lower. **So no `is_generator` lookup is needed at
all** — the proc table is consulted only to resolve the callee's INDEX for the forward-reference test.

⭐ **The transferable part: the design described a lookup the compiler had already performed and thrown into the
op.** A predicate written from the design rather than the tree returns a confident, plausible **zero** — and a
zero is the one answer nobody re-checks, because "the shape isn't there" reads as good news.

### 2. ⛔ The forward-reference test is EMISSION order, not TABLE order — 18 vs 3

Every emit loop `continue`s on `main` and emits it separately afterwards (six sites), so **a `main` host is emitted
LAST and can never forward-reference anything.** Scored by table index, `bench_correct` reported **18** forward
references. Scored by emission position, the true count is **3**. The 15 phantoms were all `main`.

⭐ **A hazard count that is 6x too high is not the safe direction to be wrong in.** It would have justified the
expensive cure (a full pre-pass) on evidence that mostly did not exist — and when the pre-pass later looked
oversized for its yield, the retreat would have been to drop the guard entirely, which the *real* 3 edges do need.

## ⭐ The question this row owed: is the `main` case representative? **NO.**

The prior FINDING closed with *"`bench_correct`'s eight programs must be checked for the host-is-a-proc shape
before anyone assumes the `main` case is representative."* Measured, all eight:

| program | host edges | forward |
|---|---|---|
| concord | 1 | 0 |
| deal | 0 | 0 |
| **geddump** | 21 | **2** (`event`→`gedval` 1→8 · `gedload`→`gedwalk` 4→6) |
| ipxref | 0 | 0 |
| micsum | 0 | 0 |
| queens | 0 | 0 |
| rsg | 0 | 0 |
| **tgrlink** | 2 | **1** (`dumpcode`→`aseq` 3→4) |
| **TOTAL** | **24** | **3** |

✅ **RULED BY MEASUREMENT: the forward-reference guard is MANDATORY before step 2 lands, not optional.** Three real
edges in two of the eight programs would read `proc_fb_buf[]` as **0 rather than erroring**, sizing a host carve
silently too small — the silent overflow ceo refused worst-case reservation to avoid, arriving through the other
door. This settles the prior FINDING's open (a)-or-(b): **(a) a pre-pass recording all generator procs' frame bytes
before ANY graph is emitted** is the cure the evidence supports; a loud REFUSE is the acceptable floor.

## Broad sweep — where the predicate fires (515 Icon files)

| corpus | files | scanned | no-scan | hosts | edges | forward | indirect |
|---|---|---|---|---|---|---|---|
| `benchmarks/icon` | 37 | 37 | 0 | 11 | 25 | 4 | 11 |
| `tests/icon` | 474 | 464 | **10** | 21 | 35 | 2 | 55 |
| `demo/icon` | 4 | 4 | 0 | 40 | 168 | 15 | 4 |
| **total** | **515** | **505** | **10** | **72** | **228** | **21** | **70** |

- **The shape is common, not exotic** — 72 host graphs, 228 edges.
- **The hazard is 21/228 ≈ 9.2%** and appears in all three corpora, not just benchmarks.
- ⚠️ **10 `tests/icon` files never reached the scan** (compile died earlier). Reported as `no-scan`, **not** as zero
  hosts — a file that could not be examined is not a file with nothing in it.
- ⭐ **70 indirect (`IR_CALL_VALUE`) nodes** sit in the explicitly-UNRULED region (ceo 2026-08-27, handed to `hq_C`'s
  one-shape-test design). Counted, never treated as host edges. **This is data hq_C's design needs: the unruled case
  is not hypothetical, it is 70 sites.**

## Cross-frontend exposure of the PREDICATE: none

`grep -c IR_PROC_GEN src/lower/lower_*.c` → **`lower_icon.c: 2`, and nothing else.** The predicate is Icon-only by
construction. ⛔ This does **not** extend to step 2: promoting the host touches `x86_main_prologue()` /
`bb_glue_framed_enter()`, the glue path every frontend shares, where `RULES.md` § SHARED-NODE VERDICT SCOPE binds
and SNOBOL4 + Icon + Prolog + Snocone boards are all owed.

## Control arms — `make pristine`, `RT_OPT=-O0`

`.s` **byte-identical** diag-on vs diag-off (204 lines). SNOBOL4 **m3 365/365 · m4 365/365 · SKIP=0 · MISSING=0**
rc=0 · `emit_no_lang` rc=0 · `template_medium` rc=0 · Icon smoke **m3 14/14 · m4 14/14** · D2 witness **= pinned
baseline** (five shapes CRASH 5/5 m3=m4, controls CORRECT). ⚠️ The pristine verdict was taken **before** a rebase
onto concurrent fleet work; re-proved after the rebase on an **incremental** build (SNOBOL4 365/365,
`emit_no_lang` rc=0, Icon smoke 14/14) — so the post-rebase reading re-proves the denominator, not a pristine verdict.

⚠️ **A self-caught instrument defect, recorded rather than hidden:** the first inertness check compared two `.s`
files that both failed to exist (a `cd` had moved the shell) and printed **"⛔ DIVERGED"** — a confident wrong
answer from absent inputs, the same false-signal class this project keeps convicting itself over. Re-written to
**REFUSE** when either input is missing or empty. The check that cannot fail and the check that cannot tell you it
did not run are the same defect.

## ⛔ Not claimed

Not a cure for anything — step 1 is inert **by design**, and the D2 board is unmoved, which is the correct result.
`bench_correct` is **not** re-scored and must not be. Steps 2–5 are untouched.
