# FINDING 2026-08-29 (seat04) — NV_SET_fn's `_xd` debug-trace gate: real, small, mechanistically confirmed to the instruction

Row: `perf-match-begin-beta-cure`, concrete-next-action (b) — "line/instruction-level attribution inside
`NV_SET_fn`/`_var_find_cached`." Companion to the same-day
`FINDING-2026-08-29-seat04-nv-cell-fastset-plt-hidden-real-but-small.md` (the PLT-hide fix); read that one first
for the measurement methodology (individual `perf stat` invocations, not `-r`'s aggregate, which is corrupted
under this container's FLEET-16 PMU contention) — this FINDING reuses it without re-deriving.

## What attribution found

Static, deterministic disassembly (`objdump -dSl`, matching this row's own first-step methodology for β —
"STATIC, deterministic, whole-program — not sampled" — rather than leading with sampling) of `NV_SET_fn` and its
always-inlined `_var_find_cached`/`NV_CELL_IF_FASTSET_fn` body shows the cache-HIT fast path costs **69
instructions** at this project's pinned `RT_OPT=-O0` — far more than the logical operation count ("one hash, one
pointer compare, one generation compare, one strcmp") the source comment describes. At `-O0`, GCC keeps nothing
in registers across statements; every intermediate round-trips through a stack slot, so each *logical* op costs
several *physical* instructions. This is real but not this row's to fix — cutting it would mean either lifting
the never-lifted `-O0` policy (⛔ explicitly forbidden, CLAUDE.md: "an -O2 number measures a compiler that's being
deleted") or hand-writing this function in assembly, which is a design-level undertaking given the two
correctness hazards (pointer-instability, shadowing) already documented in the function's own comments — **not a
same-sitting cut, recorded as direction only.**

**What WAS a same-sitting cut:** the very first thing `NV_SET_fn` does on every call, before even the
`_var_init_done` check, is a debug-trace gate (`core.c:2409`, env var `SCRIP_EXPR_STORE_DBG`) written as two
independent `if` statements on the same `static int _xd`:
```c
if (_xd < 0) _xd = getenv("SCRIP_EXPR_STORE_DBG") ? 1 : 0;
if (_xd && name && name[0] == 'E' && ...) { ...fprintf... }
```
At `-O0` this compiles to **two separate load+test+branch sequences of the same static variable** — 6
instructions — on the steady-state disabled path (the only path that exists in production; `_xd` is 0 after the
first call, forever). This is the exact same shape of pattern this function's own prologue has *already* had cut
twice before (visible in its own comments): `rt_sxt_break_fast` ("was an unconditional PLT call on every string
store, 1.87% of roman.sno") and the `g_protected_pat_vars_armed` lead pre-filter ("cannot change the answer, only
reach it without a PLT hop"). Same family of defect, not yet applied here.

⛔ **Read as a warning before trusting this, per this row's own `rt_anchor_g` lesson** (plausible-looking ceremony
that measured 0.00%): this one is different in kind, not just in degree — `rt_anchor_g` sat inside a *rarely-taken
retry loop*; this sits on `NV_SET_fn`'s own unconditional entry path, executed on literally every call, no branch
skips it. That structural difference is why it was worth measuring rather than dismissing by analogy.

## The cure

Wrap both existing checks in one outer `if (_xd)` gate (`_xd` is truthy when uninitialized (-1) or enabled (1),
falsy only when initialized-and-disabled (0) — exactly the common case). Semantics-preserving in all three states
(uninit/first-call, disabled/common, enabled/rare — verified by hand, all three produce identical observable
behavior to the original); the fast-skip case drops from two load+test+branch sequences to one.

## Measurement

Same paired methodology as the PLT-hide FINDING: byte-identical emitted `.s` between configs (confirmed by
diff), each config linked against its own stable, non-clobberable `.so` copy, 5 interleaved single-invocation
`perf stat -e instructions:u` trials per side against the full porter workload (this row's standard basis:
`corpus/demo/snobol4/porter/{porter.sno,porter.input}`, 190,138 B input). This measurement sits on top of the
already-committed PLT-hide fix (both sides of this pair have it; only the `_xd` gate differs).

| | instructions:u (5 runs) | mean |
|---|---|---|
| fix (`_xd` gated) | 798499078 / 798499954 / 798499663 / 798498167 / 798498324 | 798,499,037.2 |
| baseline | 799194039 / 799195460 / 799196849 / 799196179 / 799194405 | 799,195,386.4 |

**Delta: 696,349.2 fewer instructions with the fix (~0.087%)** — smaller than the PLT-hide's 0.173%, but every
trial, cleanly separated from each side's own ~2,000-3,000-instruction run-to-run spread (out of ~800M, the same
noise floor already established).

⭐ **Mechanistic cross-check, not just a before/after number:** the predicted saving is exactly 3 instructions per
`NV_SET_fn` call in the steady state (verified against the actual disassembly of both configs, not assumed).
696,349.2 ÷ 3 = 232,116.4 — and 232,116 × 3 = 696,348, **within 1.2 instructions of the measured mean**, well
inside the noise floor. This both confirms the mechanism precisely and implies `NV_SET_fn` is called almost
exactly 232,116 times during a full porter run — independently plausible (a Porter-stemming workload doing
repeated per-word/per-character variable reassignment), and a different, unrelated call count from the PLT-hide
FINDING's ~1.39M (that delta came from `pattern_match.c`'s call site to a *different* function, not `NV_SET_fn`
itself — the two FINDINGs are not measuring the same call site and should not be added together as if they were
double-counting one number).

## Correctness

- Byte-identical porter output, fix vs. baseline, both built from the same `.s`.
- `make pristine` + `bash scripts/test_corpus_snobol4.sh`: **mode-3 PASS=1298 FAIL=0, mode-4 PASS=1298 FAIL=0
  SKIP=0, TOTAL=238s.**

## Disposition

Committed and pushed this sitting — real, safe, mechanistically confirmed to the instruction, correctness fully
verified at gate level.
