# FINDING 2026-08-02c — SN4 s23j — REPL-PIN: the fence-denied population was unpinned, and the raw op_sa read the deleted carve

**Session:** s23j (Claude), directive: *"Get benchmarks working using NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. Continue."* + the standing grant.

## THE DEFECT CHAIN (three benchmarks, one class)

string_pattern / mixed_workload / roman all silently produced empty-or-zero results, M3==M4. Bisect (inline+capture+replace PASS · stored+replace FAIL · stored+capture-no-replace PASS) isolated **replacement through a stored pattern** — `S PAT = ''` — as the broken construct. The monitor bracketed to statement 1 but is dark for non-seal statements (the GE-1 tap gap, reconfirmed); the statement bracket came from the bisect, the land mine from the .s + gdb per RULES.

**Root cause, two compounding halves:**
1. **The pin conjunct excluded the fence-denied population.** HEAD-PIN (s22z) fired on `(subjc||op_zres) && deep && hpin`. A replacement statement's subject has a SECOND consumer (the splice), so the SOLE-CONSUMER FENCE denies subjc; spine-resident PATREF vetoes ZD arming (PATREF is not a run-member kind at emit.cpp:1886), so op_zres=0 too. Result: rbp-flavored FRQ slots with NOTHING establishing rbp — gdb: `rt_match_enter(lo=0x7fffffffea80 [argv territory], hi=0)`, zero-length subject, silent :F.
2. **The legacy subject read spelled the deleted carve.** `FRQ(op_sa)` on the pinned (rbp) arm renders RAW flat coordinates (256 against a 176B claim — the hoffb comment's 066 shape) while the producer WROTE through zvo to the claim slot (+160, gdb-verified at [rbp+160] post-pin). Writer and reader in different coordinate systems.

## THE FIX (SCRIP `0fdf7932`, 3 template files)

`rpin() = deep && hpin && (subjc || zres || !flat_jmp_entry)` — ONE authority across the four sites (op_stmt_pin publication, pin emission, +40-save complement, subject-read respell). The s22z population pins exactly as before; the legacy-subject population joins ONLY on non-jmp-entry graphs. The pinned legacy subject read respells `RDQ("rsp", hoff(op_sa))` — the SAME resolver the pin slot already used, landing on the writer's zvo coordinate (hoffb was tried first and resolved into outer_Σ's slot — the base resolver is the wrong half for a reader-depth read). `bb_match_replace:33`'s rbp restore gains the `!op_stmt_pin` twin gate release:78 has carried since s22z — without it: correct output then SEGV (the terminal cut received a stale base).

## THE CONTAINMENT (roman)

The unconditioned widening crashed roman at 3 iterations: its match lives in `proc_LBL__ROMAN`, **LP jmp=1** — a DEFINE body entered by `rt_goto_transfer` at runtime-variable depth, where hoff's compile-time rsp spelling is invalid by construction. The fixed population is jmp=0. jmp-entry chains keep the pre-session regime VERBATIM (roman returns to its known baseline-red DIFF, not a crash) until the **r9/wire-carried claim base** (CARRIED-OPEN) retires the compile-time spelling itself. Degrade never die.

## MEASUREMENTS

- **Benchmarks 16→18/21** (string_pattern, mixed_workload fixed; M3==M4 on all 21 verdicts). Residue: eval_fixed/eval_dynamic (deferred-eval family, separate bracket) + roman (r9/wire rung).
- **Crosscheck 318:** m3 **282/25/10** (+1: `127_pat_json_keyvalue` newly passes) · m4 **266/39/10/2L EXACT** — **zero P→F BY SET both modes**, proven against a parent-binary A/B (git stash → rebuild → run → restore), not against remembered counts.
- **127/152 are one placement-flicker pair:** 152 flickered into the fail set on one roll; env-pad test (s23i method) reconfirmed its verdict is a pure function of environment-block size — 0/3 vs 2-3/3 on dummy-var length. The layout change reshuffled which twin lands safe. Both are the s23i cap-slot defect awaiting r9/wire; neither is a session regression.
- Regen ×4 done (corpus `bd5be761`/`49350480`/`e6950c05` + SCRIP feature); crosscheck churn = exactly the replace-class artifacts.

## INSTRUMENT NOTES

- Benchmark diffs MUST strip `ms:` lines (the canonical harnesses do); a naive diff reports 19/21 false-FAIL.
- `SCRIP_LP_DIAG=1` prints the per-chain jmp/pat/gen flags — it is the cheap discriminator this fix's containment predicate was read from.
- gdb needs `apt-get update` first in this container (s22m note holds).
