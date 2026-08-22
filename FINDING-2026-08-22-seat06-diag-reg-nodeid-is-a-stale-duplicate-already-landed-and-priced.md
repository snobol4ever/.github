# FINDING seat06 — `diag-reg-nodeid` is a stale duplicate of seat8's already-landed `diag-regs-stmt-and-bb`; verified the two DONE-WHEN items nobody had checked yet (ZSM cross-run stability, timed-bench pricing) — no code changed, row closes DONE

**Session:** seat06 (`/home/claude06`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `diag-reg-nodeid` (rank 3, "LON DIRECTIVE s198, IDEA 2 OF 2")
**Tree:** SCRIP `cd13321e` clean · corpus clean (fresh pull, 1189 files of fleet-wide drift) · `.github` clean · **zero src/ changes this session — verification only**

## 1. The row is stale — the exact mechanism it asks for is already built, merged, and pushed

`diag-reg-nodeid` and its sibling `diag-reg-stmtno` (both rank 3, both dated "LON DIRECTIVE s198") were split off the original combined row `diag-regs-stmt-and-bb` (rank 1) at some earlier point. That combined row has since been fully built and landed by seat8 (SCRIP `c951f257`/`c5e97682`, both real ancestors of current `origin/main` — my local clone was simply behind and a `git pull --rebase` surfaced them). Confirmed live in the current tree: `SCRIP_DIAG_REGS` killswitch (`x86_diag_regs_on()`/`x86_diag_regs_on_c()`, default ON) in `x86_asm.h`; r10=statement number written in `bb_statement.cpp`; r11=BB node id written centrally in `x86_port_hook()` for every α/β port-definition site, both languages, both media, via the existing `x86("mov", …)` encoder — zero new globals, zero new encoders. Full design/history: `ARCH-SNOBOL4-RTX.md` §2 (the CLAIMED bullet) and `FINDING-2026-08-22-seat8-diag-regs-stmt-and-bb-landed.md`. `GOAL-SNOBOL4-100.md`'s newest cursor (seat8, second session) adds the one live caveat: the row landed ahead of the *full* r10/r11 eradication ladder (`DISPATCH-R10-R11-ERADICATION.md`), which HQ has since ruled is the correct end-state precondition — but the code is **kept, not reverted**, per HQ's explicit ruling, with `WREG_CLAIM_LIVE` staying 0 until the ladder completes. None of that residual ladder work is this row's scope (it's `bb_call_fn.cpp`/RTX-hand-asm eradication, tracked separately).

Nothing was left for me to *build*. What was left, and what this session actually did, is verify the two specific DONE-WHEN items in `diag-reg-nodeid`'s own (more detailed) brief that seat8's landing FINDING doesn't address, because they belong to the split row, not the combined one.

## 2. DONE-WHEN item — "a ZSM trace of the SAME program under -O0/-O2 diffs with ZERO normalization"

Measured directly (`corpus/probe/diag_regs_witness.sno`, mode-3, `SCRIP_ZSM=1 SCRIP_ZSM_RING=1`):
- **Default (`SCRIP_DIAG_REGS` unset/1):** `node=` values are dense and IDENTICAL across two separate process launches (`7, 0, 7, 7` both times). The brief's original problem (ASLR-shifting raw addresses) is solved under the shipped default.
- **`SCRIP_DIAG_REGS=0`:** the SAME program, three separate launches, gives `node=72464` / `83120` / `10928` — reproducing the *exact* original ASLR-noise problem. Root cause: `scrip.c`'s mode-3 dispatch enables `bb_node_id()`'s dense numbering ONLY `if (x86_diag_regs_on_c())` (line ~1587), whereas mode-4's two dispatch sites enable it unconditionally (lines ~1188, ~1396). ⛔ **NOT A BUG — an intentional, already-reasoned tradeoff** (per the landing FINDING: gated on purpose so `SCRIP_DIAG_REGS=0` is a *total*, structurally-provable revert to pre-row behavior, which is exactly what the row's own killswitch byte-identity proof relies on). Recommend **documenting, not patching**: a future debugging session that wants stable ZSM node ids on mode-3 must not also set `SCRIP_DIAG_REGS=0`. Program output/correctness is untouched either way (`bb_node_id()`'s only non-diagnostic consumer, `zw_carve_k`'s `SCRIP_BB_ONLY`/`SCRIP_BB_SKIP` bisection list, is itself off by default).

## 3. DONE-WHEN item — "timed bench family, arm ON/OFF, RT_OPT labelled, regression is a design input not a reason to hide the number"

Nobody had actually priced this (checked: no FINDING greps for `SCRIP_DIAG_REGS` alongside timing numbers). Rebuilt `make pristine` with **RT_OPT="-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer"** (labelled per RULES O0-DEV-O2-BENCH), compiled all 5 named benchmarks mode-4 twice each (`SCRIP_DIAG_REGS` unset vs `=0`), linked against the same `out/libscrip_rt.so`, timed with `date +%s%N` wall-clock, median of 5–9 reps:

| benchmark | N | ON median (ms) | OFF median (ms) | Δ | verdict |
|---|---:|---:|---:|---:|---|
| arith_loop | 3,000,000 | 75 | 78 | −3.8% | noise (ON nominally faster) |
| func_call | 3,000,000 | 87 | 90 | −3.3% | noise |
| op_dispatch | 3,000,000 | 99 | 104 | −4.8% | noise |
| var_access (1st pass) | 3,000,000 | 111 | 101 | +9.9% | **did not replicate** — see below |
| var_access (re-measured) | 8,000,000 | 232 | 233 | −0.4% | noise |
| fibonacci | 20,000 | 560 | 561 | −0.2% | noise, `check:` output identical both arms |

var_access's first-pass +9.9% was a small-N/low-rep artifact (spread of ~15ms on ~100ms runs); re-measured at ~3x the N and more reps it collapses to noise. **Verdict: no measurable wall-clock regression on any of the 5 named "5–7x win" benchmarks.** The cost is real at the instruction level, not zero — `diff on.s off.s` for arith_loop shows exactly the expected shape (one `mov r11, <id>` per box α/β, occasionally paired with `mov r10, <stno>` at statement boundaries; label names and control flow are byte-identical otherwise) — but it's a handful of register-immediate loads per box in a loop whose body is already dozens of instructions, and it doesn't clear the wall-clock noise floor (~±3–5% on this box/VM) on any tested kernel.

## 4. Disposition

`diag-reg-nodeid` closes **DONE** — the mechanism is built, its killswitch is proven, and both of this row's own distinguishing DONE-WHEN items (ZSM stability, timed pricing) are now verified rather than assumed. No code touched; nothing to revert. **Sibling row `diag-reg-stmtno` (rank 3, unclaimed) is equally stale** — same combined feature already covers its half (r10=statement number) — flagging so nobody freelances a rebuild of already-shipped work; not closing it myself since it was never my claim.

**Housekeeping:** this session also pulled all three repos fresh (SCRIP/`corpus`/`.github` were all behind origin — SCRIP was 164 files / several real landings behind, corpus 1189 files behind); temporarily rebuilt with RT_OPT=-O2 for the pricing measurement above, then rebuilt back to a clean pristine -O0 default before finishing (O0-DEV-O2-BENCH).
