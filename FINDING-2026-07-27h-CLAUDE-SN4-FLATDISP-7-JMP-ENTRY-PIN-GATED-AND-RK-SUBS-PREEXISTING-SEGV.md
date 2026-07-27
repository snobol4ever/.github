# FINDING 2026-07-27h — FLATDISP-7: jmp-entry rbp pin gated per-graph; rk_subs segv is pre-existing

**Session s194.  SCRIP `d95b1a98` + three artifact-sweep commits.  Watermark m3 185/130 · m4 183/130 · DIVERGE=1 (W06_tab), re-proven fresh at session start and pre-commit — held exactly.  Census NET 237→119 (−49.8%), ratchet lowered.**

## 1. The census that shaped the fix — fibonacci's 26, fully accounted

The jmp-entry regime's rbp readers, enumerated by reading every emitting site (the s193 by-template-read discipline, applied to the emitter arms):

| Site | Reads | Count in fibonacci |
|---|---|---|
| Prologue save+seed (`mov [rsp+kt-8],rbp` + `mov rbp,rsp`) | — | 2 × 2 graphs = 4 |
| Determinate epilogue γ (result ×2, wire, lea unwind, restore) | 5 | ×2 graphs = 10 |
| Determinate epilogue ω (wire, lea unwind, restore) | 3 | ×2 graphs = 6 |
| Role-3 wire-adopt marshal (γ-wire, ω-wire, entry-rsp lea, caller-rbp) | 4 | 4 |
| Role-1/2 floater restores (`mov rbp,[rax+24]`) | 1 each | 2 (= the class-D pair) |

4+16+4+2 = 26.  **Zero hidden readers** — the accounting closed before any edit was made, which is what licensed gating all of it at once.

## 2. The predicate — and why FLATDISP-7 decoupled from 5a

`emit_jmp_pin_rbp() = flat_deep_arrival || flat_pat || flat_gen`, one static inline in emit.h beside `g_emit`, the ONLY reader-facing spelling (the xaf_deep single-reader discipline; cross-FILE drift between xa_flat.cpp and bb_save_restore.cpp is exactly what a shared accessor prevents).

The s193 cursor sequenced 5a (inline invariant blobs) BEFORE 7 (gate the seed), because "the jmp-entry arm seeds unconditionally … correct today because every PAT$ blob has fence/arbno/defer" — i.e. a bare classifier check would drop the seed from an invariant blob that STILL γ-suspends at the deep frontier.  The decoupling insight: **that is not a classifier gap, it is a second, independent reason to pin.**  A suspending activation's γ retains with rsp deep and its record/exit protocol reads the pinned rbp by contract (REG-7 U5) — regardless of what kinds its body contains.  So the pin condition is (deep-arrival ∨ suspends), the conjuncts fold into the predicate, and 7 lands safely today.  5a, when it comes, shrinks the flat_pat population; it can never make the predicate wrong.

## 3. What was gated (both media, every site)

- **Prologue**: BINARY `hdr` pair; `xaf_jmp_hdr_x86` pair (the LEXPREP2 x86() arm); the three TEXT snprintf twins (LEXPREP2 / NOFILL / EAGER) — the rbp pair split out of the format strings and appended conditionally.
- **Determinate epilogue**: new depth-static arms in BINARY and TEXT ahead of the pinned arms.  Form: `mov rdi,[rsp]` / `mov rsi,[rsp+8]` (result), wires at `[rsp+kt-24/-16]`, `add rsp, kt` as the ENTIRE teardown, `jmp rax`.  This is literally the pre-s90 rsp-relative form whose comment records it as "true for SNOBOL4's determinate procs, FALSE for Icon" — restored for exactly the graphs where the classifier proves the every-ω-pops assumption, language-blind.  New helpers `xaf_ld64_rsp` / `xaf_addq_rsp` pick as-matching disp8/imm8 short forms (R10: BINARY equals what `as` emits for the TEXT twin).
- **Role-3 wire-adopt** (bb_save_restore.cpp): depth-static arm reads the header via rsp (the box runs immediately post-prologue, pre-carve — rsp==base in BOTH regimes at that point) and marshals caller rbp from the LIVE REGISTER (`mov rcx, rbp`), since the ungated prologue neither saved nor clobbered it.
- **Role-1/2 floaters: correct UNCHANGED.**  The snap-record restore writes back the caller's rbp; when the callee never seeded, rbp already holds that value and the restore is a same-value write.  (Nested pinned activations save/restore their own, so the invariant survives arbitrary interleaving.)

Falsifiability, unchanged from s193: any depth-static graph that in fact arrives off-base at an exit reads garbage wires and the crosscheck fails loudly at once.  It did not — 185/130 · 183/130 · 1, twice.

## 4. Measured results

- fibonacci / func_call / func_call_overhead / indirect_dispatch: net 24 → **1** each (residual = the wire-adopt `mov rcx, rbp`, a register read, not a frame reference; the record contract requires the value).  mixed_workload 49→36, roman 42→29.  pattern_bt / string_pattern 25 each unchanged — PAT$ pins + fence boxes, the 5a population.  **Twelve of 16 benchmarks net ≤ 1.  NET 237 → 119.**
- Icon crosscheck 4/0 → 4/0.  SNOBOL4 bench-modes status column identical per program baseline↔after (OK=8 FAIL=4 CRASH=4, all pre-existing; timings are RT_OPT=-O0, not perf claims).
- Cost: +5 xa_flat medium-invisible WIP sites (101→106) — the helpers are raw-byte in the legacy epilogue stream, where x86() records would corrupt the `out_site = size()` patch bookkeeping.  Retired wholesale by XA-FLAT-CONVERT, not piecemeal here.

## 5. rk_subs — the segv is pre-existing; the flake is new visibility, not new breakage

Method: 20 runs per build, stash-cycled binaries, md5 over stdout.

| Build | segv | stdout |
|---|---|---|
| baseline (pre-FLATDISP-7) | 20/20 | empty 20/20 |
| FLATDISP-7 | 20/20 | complete-but-WRONG 14/20, empty 6/20 |

The Raku suite runs each program three times with `--run` and compares the runs to each other when no `.ref` exists (rk_subs has only `.expected`, which the suite does not read).  Baseline therefore "PASSED" rk_subs by consistently emitting NOTHING — three empty outputs agree.  FLATDISP-7 perturbs the crash/flush race enough that partial output sometimes survives, and that output is WRONG ("0 / hello " where .expected says "14 / hello raku / 7 / positive / zero / negative") — so the program is broken twice over (wrong values, then segv) on BOTH builds.  The suite's 51/0↔50/1 flapping is that coin-flip; Prolog's FAIL↔SKIP churn (2/3/4 ↔ 58/59/60, both builds, same binary) is timeout-sensitivity of the same shape.  **Raku-ladder item (the RK-NAMED-REST / slurpy work is mid-flight per the 07-26/27 findings); not entered here per DO-NOT-READ-UNRELATED-GOALS — recorded so the next Raku session starts from measurement, not from a red suite and a guess.**

## 6. Named residue

The per-benchmark net-1 (`mov rcx, rbp`) is semantically required: the pcall record's rbp slot must hold a valid caller value for the floater's unconditional restore, and only the emitted code knows which regime it is in.  Dropping it would need an rt-side signature/behavior split — not worth a rung.
