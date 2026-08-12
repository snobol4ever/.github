# FINDING 2026-08-12 s33 (Opus 5) — HOME-RBX X-0/X-1: THE CAS ISLAND WAS NEVER SCANNED AND A FALSE COMMENT IS WHY, AND MY OWN pz PREDICTION WAS WRONG

**Seat:** RBX (`GOAL-SN4-HOME-RBX.md`). **Rungs:** X-0 CLOSED (contract, zero code), X-1 CLOSED (SCRIP `9ecb75a9`).
**Fingerprints:** SCRIP parent `52545cbf` → `9ecb75a9` · corpus `c91d1adf` (read-only) · x64 oracle cloned.

## HEADLINE 1 — the CAS capture-pending island was invisible to the collector, and the reason it survived is a comment that asserted the opposite

`pattern_match.c`'s CAS-1 banner read: the stacks "are covered by `RT_SLAB_GC_ROOTS` today." **False at HEAD, in two independent ways:**
1. `RT_SLAB_GC_ROOTS` is `#define RT_SLAB_GC_ROOTS 0` (`rt_slab.h:14`).
2. It gates **ZERO `#if RT_SLAB_GC_ROOTS` bodies tree-wide** — grep returns nothing. Its own header calls it the TR-3 libgc compensation and says "DELETE AT TR-4 with libgc." libgc was deleted; the compensation went with it; **only the sentence remained.**

`rt_cas_roots(base,bytes)` — the "named root area" export the banner points at — had **zero consumers** from the day it was written ("for GC-W-1's MARK tomorrow"). So neither mechanism was live and the banner said both were.

Meanwhile the island holds, by its own declaration: `g_capx` (a `DESCR_t` stack), `g_dfx` (`DESCR val`), `g_dcf` (**three `char*` INTO THE SUBJECT** plus a pending DESCR), `g_spk` (name ptr + DESCR). Every one is a live reference into the collected workspace that no root phase walked.

**LESSON (the generalizable one):** a stale comment asserting coverage is worse than no comment. It converts a hole into a *checked* box for every reader after it. The X-0 sweep found this only because the rung said *read cold* and the ledger demanded pin-vs-range be recorded per region rather than "GC: yes/no". **Banner corrected in place** so the next reader is not misled again.

## HEADLINE 2 — PIN ≠ SCAN, and the distinction is the whole rung

`rt_gc_root_pin_add` → `rt_gc_pin_ptr`: keeps the **containing block alive** (`gc_heap.c:625`).
`rt_gc_root_range_add` → `gc_cons_scan`: walks the **interior**, marks referents (`:626`).
Registering the pin alone is sufficient for LIVENESS OF THE BLOCK and useless for REACHABILITY THROUGH IT. `rtcc_gc_register` did exactly that, under a comment reading "BLOCK-CANONICAL … registering it is sufficient" — true for the property it names, false for the one that matters.

**RTCC remains LATENT, not dead, and the gating in the goal file is correct:** slots [0..4] (the `rax/rcx/rdx/rsi/rdi` arg tier) are unclaimed, and the claimed slots hold non-collectible values — R9 the constant GVA base, R10/R11 the Γ/Ω wires (code addresses). **X-5 claiming the arg tier is what makes it live.** X-5 gated on X-1 is right.

## HEADLINE 3 — the fix is NON-VACUOUS, proven by one witness, and only one exists

Anti-vacuity was the real risk here (this project's recurring "vacuous by volume" class). The island is reachable **only** through `c_rt_cap_open`'s `varname[0]=='*'` arm — the plain-name arm **returns early at `:799`** and never pushes. So `X . A` never touches it; only the deferred `*`-target form does.

Corpus-wide that form appears in **4 programs**: `probe/mv_arbno_callcap`, `crosscheck/control/expr_eval`, `crosscheck/patterns/140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`. Of those, **`mv_arbno_callcap` holds 40 bytes live in the island at a collection** = exactly `sizeof(rt_dcf_t)` (3 subject pointers + pending DESCR).

⛔ **HONEST LIMIT — this is a demonstrated-reachable latent hole now closed, NOT a demonstrated miscompile.** The witness passed before the fix, most plausibly because the conservative stack scan incidentally covered the same values. I am not claiming a fixed bug, and the next seat should not cite this as one.

## HEADLINE 4 — MY OWN X-0 PREDICTION WAS FALSIFIED: `pz` is already dead at HEAD

X-0 §D asserted that arming the rbx frontier would disable the `pz` punt-zero fast path and forced `cons_stack=1`, and **charged that cost to X-3**. **Wrong about who already paid it.** `rtcc_init.c:24`'s constructor calls `rtcc_gc_register()` unconditionally with `g_rtcc_on` defaulting to **1**, so `g_gc_rpin_n >= 1` from before `main`; `pz` is false in every run and `cons_stack` is forced to 1 at `:622`. **Every `[GC-COV]` line across the whole census reads `pz=0 cons_stack=1`** — 2432 collections on one program under stress plus every witness. The conservative stack+register scan is the *existing* regime. **X-3 does not owe this cost.** §D corrected in place.

Method note: I derived the prediction by reading the guard and did not run the one-line census that would have falsified it in thirty seconds. The census line existed only because the gate needed it — the instrument caught its own author.

## HEADLINE 5 — the `gc_*` crosscheck suite triggers ZERO natural collections (→ BOARD)

All **15/15** of `crosscheck/gc/*.sno` complete with **zero** garbage collections. Collections appear only under `SCRIP_GC_STRESS`. **The instrument is NOT dark** — positive control: the same program under `SCRIP_GC_STRESS=50` produced **2432** collections. So the zero is a property of the suite, not of the measurement. **The suite named for the GC does not exercise the GC.** Every "gc" pass in a phase-boundary floor is currently a statement about allocation, not collection. BOARD owns this (B-1 runner selection / denominator pinning).

## WHAT LANDED

- `rtcc_init.c` — `rtcc_gc_register` gains the range over the whole 256B block, XMM slots included. Asymmetry argument recorded: a real in an XMM slot that looks like a heap address costs one falsely-pinned block (bounded, safe); a missed GPR root costs a collected live object.
- `pattern_match.c` — new `rt_cas_live_span(i, &base, &bytes)` enumerating the **live prefix** of each sub-stack (the used cursor, not the multi-MB zero-filled carve — as the CAS-1 banner always specified). Index-driven so the collector loops it exactly as `gc_root_zeta` loops zeta frames.
- `gc_heap.c` — `gc_root_cas()` walks those spans with **`gc_zeta_frame`** (the DESCR-aware walker), not raw `gc_cons_scan`, because every sub-stack is DESCR-bearing with interleaved pointer/int fields. Plus the `SCRIP_GC_COVERAGE=1` census line.
- `scripts/test_gate_rc8a_gc_coverage.sh` — self-arming: CAS arm WARNs while unoccupied, FAILs once occupied; RTCC arm always FAILs. **Every assertion carries its positive control** via `SCRIP_GC_UNROOT={cas,rtcc}`, which re-opens the pre-s33 hole on demand. Armed `ranges=1 cas=40`; sabotaged `ranges=0 cas=0`. It also refuses to pass when no collection fired (prints BLOCKED — instrument DARK) rather than reporting a vacuous green.

## MEASUREMENTS (m3, BY SET, against my OWN HEAD control — BOARD's P0 floors do not exist yet)

| suite | HEAD | X-1 | verdict |
|---|---|---|---|
| `crosscheck/patterns` (122) | 76 / 46 | 76 / 46 | **IDENTICAL BY SET** (`diff` of failing sets, empty) |
| `crosscheck/gc` (15) | 15 / 0 | 15 / 0 | hold |
| `crosscheck/capture` (9) | 8 / 1 (`061_capture_in_arbno`) | 8 / 1 (same) | hold |

**Emitted `.s` byte-identical HEAD vs X-1** on the witness (`cmp`) ⇒ zero codegen touched ⇒ RULES step-4 artifact regen **not triggered**. Proved, not asserted.
**m4:** the witness is `rc=139` at **HEAD too** — pre-existing, not this diff. m4 was exercised by hand (`--compile` → `gcc -no-pie` → run); the *harness* arm is what is dark, not the emitter.

## OBSERVED, NOT MINE (filed, not fixed)

- **`ARB . A` capture diverges from oracle at HEAD.** `S = "hello world"; S ARB . A " " ARB . B` → oracle `hello/`, SCRIP `/hello ` (A and B contents swapped/shifted). A capture loop over a grown subject **SIGSEGVs** where the oracle prints `2290`. **Both reproduce with my diff stashed.** → RBP / LOWER seats.
- **HAZARD-1 (from X-0) stands:** `xa_flat.cpp:520,526` clobbers **rbx** as a scratch save slot for `caller_rbp` in Icon's ICN-FR-2 zframe ω. Direct violation of the one-authority rule on a shared emitter, and proof the claim gate does not yet cover rbx. → BOARD (gate row) + WIRES (eradication).

## PROCESS NOTE (worth carrying)

A `git stash pop` **silently did not apply** inside a command that hit the execution time limit; the tree sat at HEAD while I believed my diff was live. I caught it only because I re-checked `git stash list` and grepped for my own symbol before trusting the next measurement. This is the same class as "I twice read a working tree as origin" (s217). **Verify the tree, not the command's exit code, after any stash dance** — and prefer pushing over carrying.

**UNBLOCKS: RBX X-5** (its stated gate, RC-8a, is now green). **X-2 and X-3 unaffected and unblocked.**
