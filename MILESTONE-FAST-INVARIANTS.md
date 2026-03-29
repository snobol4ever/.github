# MILESTONE-FAST-INVARIANTS.md — M-G-INV: Fast 3×3 Invariant Harness

*Authored G-7 session, 2026-03-28, Claude Sonnet 4.6*

---

## Problem

The Grand Master Reorg touches all emitters. Every change must be gated by
the full 3×3 invariant matrix (SNOBOL4/Icon/Prolog × x86/JVM/.NET — 7 active
checks). The current runners:

- Recompile all runtime `.o` files **inside every test** (run_rung*.sh each rebuild)
- Run all 7 suites **serially** — wall time ~5–10 min
- Spawn `gcc` hundreds of times for link steps
- No shared runtime archive — link cost paid per test

Running this on every commit or after every emitter edit is prohibitively slow.

## Goal

A single script `test/run_invariants.sh` that:

1. **Builds runtime archives once** at startup — one `.a` per runtime family
2. **Runs all 7 active suites in parallel** — one background job per suite
3. **Reports pass/fail per cell** of the 3×3 matrix, with total wall time
4. **Exits 0** if all active cells pass, **1** if any fail
5. **Target wall time: < 60 seconds** on a 2-core machine

## Optimizations

| Optimization | Mechanism | Savings |
|---|---|---|
| Runtime pre-build | `ar rcs libsno4rt_asm.a *.o` once | Eliminates N×7 gcc -c calls |
| Parallel suites | `suite_fn &` + `wait` for all 7 | Serial→parallel on all cores |
| Per-test link uses archive | `gcc prog.o libsno4rt_asm.a` | Single link command, no .o list |
| Prolog runtime archive | `libsno4rt_pl.a` (atom+unify+builtin) | Same for Prolog x64 |
| No verbose per-test output | Only FAIL lines + final matrix | Less I/O contention |
| TIMEOUT tuned | 5s x86, 10s JVM (JVM startup cost) | No wasted wait |
| scrip-cc pipe | `scrip-cc ... | nasm -f elf64 /dev/stdin` | Skip temp .s file for x86 |

## Script location

`one4all/test/run_invariants.sh`

Called from `SESSION_BOOTSTRAP.sh` HOW block in place of the current
per-suite inline code.

## Success criteria

- All 7 active invariant cells pass (Icon .NET / Prolog .NET: SKIP — not impl)
- Wall time < 60s on 2-core CI container
- Single exit code (0 = all pass)
- Output: concise 3×3 matrix with per-cell status + wall time

## 3×3 output format

```
Invariants (Xs = wall time):
              x86          JVM          .NET
  SNOBOL4   106/106 ✓   106/106 ✓   110/110 ✓
  Icon       38-rung ✓   38-rung ✓      SKIP
  Prolog    30/30   ✓    31/31  ✓      SKIP
────────────────────────────────────────────
  ALL PASS  [12.4s]
```

## Status

| Step | Action | Done |
|------|--------|------|
| M-G-INV-DESIGN | This doc | ✅ G-7 |
| M-G-INV-BUILD | Write `test/run_invariants.sh` with all optimizations | ✅ G-7 |
| M-G-INV-WIRE | Replace SESSION_BOOTSTRAP.sh HOW block with call to `run_invariants.sh` | ✅ G-7 |
| M-G-INV-VERIFY | Run it, confirm all 7 cells report, wall time measured | pending |
