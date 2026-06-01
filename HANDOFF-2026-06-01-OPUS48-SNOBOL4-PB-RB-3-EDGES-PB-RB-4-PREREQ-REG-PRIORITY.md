# HANDOFF 2026-06-01 (Opus 4.8) — SNOBOL4: PB-RB-3 edge probes, PB-RB-4 topology prereq, GOAL prune, REG-ladder promoted to TOP priority

**Repos / HEADs at handoff:** SCRIP `e39c329` (pushed) · .github `<this commit>` (pushed).
**Identity:** `git config user.name LCherryholmes`, `user.email lcherryh@yahoo.com`.
**Build (lockstep, always together):** `cd SCRIP && bash scripts/build_scrip.sh && make libscrip_rt`.

## What landed this session (SCRIP)

1. **`706d665` — PB-RB-3 edge probes.** The happy-path probe only matched a literal via the unanchored outer
   start-loop. Added `test/snobol4/pat_bb/probe_pb_rb_3_match_fail.c` (in `scripts/test_sno_pat_bb_probe.sh`, now
   3/3) exercising the two ch.18 step-6 BINARY-arm edges that were unverified:
   - **A. whole-match FAIL** — `'z'` ∉ `'abc'`: start cursor advances to exhaustion (`start > Σlen`) → `jmp lbl_ω`
     → statement FAIL port → `result.v == 99`.
   - **B1. anchored mismatch** — `&ANCHOR=1`, `'b'` present at cursor 1 but unreachable: step-6 must NOT slide the
     start cursor → fails immediately → `v == 99`.
   - **B2. control** — same chain, `&ANCHOR=0`: `'b'` reached by the slide → SUCCEED `v == 1`, proving the anchor
     flag is the sole cause of B1.
   - Two apparent bugs checked and found CORRECT: `kw_anchor` is genuinely 8 bytes in the live `.so` (the
     `int kw_anchor=0` at `stmt_exec.c:128` compiles only under `STMT_EXEC_STANDALONE`; the live build uses
     `extern int64_t`), so `bb_match.cpp`'s `cmp qword [rcx],0` is right; and `result.v==99` is the canonical FAIL
     code from `xa_flat_epilogue`'s `fail_half` (`eax=99`), not garbage. Runtime contract: **v==1 SUCCEED / 99 FAIL.**
   - Test-only, byte-neutral.

2. **`e39c329` — PB-RB-4 topology prereq.** Two `prove_lower2.c` SNOBOL4 proofs (prove count **65 → 67**):
   `MATCH('a' 'b')` = PATMAT + wire_seq(IR_PAT_CAT) + 2 PLIT = 4 real nodes; `MATCH('a'|'b')` = PATMAT +
   wire_alt(IR_PAT_ALT) + 2 PLIT = 4. In both, the composite element's OUTER γ AND ω thread back to the
   IR_PAT_MATCH node (Lon "jump to alpha, return from omega").
   - **KEY FINDING:** `lower2_match_entry` (lower.c:2276) calls `lower2(cx, e, m, m, …)` under `ROLE_PATTERN`, which
     ALREADY handles `TT_CAT` (wire_seq/IR_PAT_CAT) and `TT_ALT` (wire_alt/IR_PAT_ALT). **PB-RB-4's lowering/topology
     layer already exists** — the genuinely-new PB-RB-4 work is the emitter-side STITCH wiring + mode-3 drive, NOT the
     IR topology.
   - Test-only, byte-neutral.

## What landed this session (.github)

3. **GOAL-SNOBOL4-BB.md pruned 2261 → ~1565 lines** (`c7cd4b79`, then watermark/prereq updates `0b344247`):
   collapsed the spent PB-RB-3 design-deliberation + over-documented step to one terse `[x]` done-record; collapsed
   the ~600-line HEAD-by-HEAD "Session State" ledger + LM/PND completed history to a 16-line summary (kept open
   LM-6, BOX-ZERO); collapsed the stale multi-watermark dump + Icon-focused "IMMEDIATE NEXT" to one SNOBOL4-current
   watermark. All six FACT-RULE blocks untouched (`audit_concurrency_invariants.sh` byte-identical-×3 green;
   LOWER md5 `5097ed94`, EMITTER `307534d6`). Per-session detail now lives in the HANDOFF files.

4. **REG LADDER promoted to TOP priority (this commit, Lon directive).** New `## 🔴 CURRENT PRIORITY` section
   placed immediately after the FACT-RULE blocks (top of actionable content) containing the full REG ladder
   (REG-0…REG-FENCE + completion test). The watermark "NEXT" now states the priority order explicitly: **REG ladder
   FIRST, then PB-RB-4+.** No content lost — the block was MOVED, not rewritten; the PB-RB feature ladder and the
   BROKERED-ERADICATION rung remain below at lower priority.

## CURRENT PRIORITY for the next session — the REG ladder (BB templates → ratified registers)

**Why:** the SNOBOL4 pattern BB templates still use the LEGACY subject model — cursor in `[r10]`, Σ via
`movabs &Σ;deref` / `lea [rip+Σ]`, Δ via `movabs &Σlen` / `[rip+Σlen]`, where `TEMPLATE_ADDR_SIGMA` /
`TEMPLATE_ADDR_SIGLEN` are **emitter-process global addresses**. Migrating to the ratified convention
**Σ=R13, δ=R14, Δ=R15, ζ=R12** (r10 stays the per-BLOB data-block ptr) gives (a) convention compliance and (b)
**removes the process-local-address bake → SNOBOL mode-4 relocatability** (the m4 0/6 blocker). NOT a convention
change (the byte-identical-×3 table is untouched) → SNOBOL-session-local, NO lockstep.

**Order:** REG-0 (register-establishment contract) is coupled to BB_MATCH and is effectively done as part of the
landed PB-RB-3, so the first CODE step is **REG-1 (`bb_lit`)**: BINARY+TEXT — cursor `[r10]`→`r14d`, Σ-base
`movabs &Σ;deref`→use `r13`, Δ-compare `movabs &Σlen`→`cmp …,r15d`, β `δ-=len`→`sub r14d,len`; removes both
`TEMPLATE_ADDR_SIG*` bakes; re-derive the patch tuple (it SHRINKS — the two movabs+deref blocks vanish). Then
REG-2 (cursor-advancing leaves), REG-3 (position leaves), REG-4 (combinators — saved-δ slot moves `[r10]`→ζ-slot
of R14), REG-5 (generators+capture, coordinate with BROK-1/2), REG-FENCE (add `scripts/test_gate_sno_pat_reg.sh`:
zero `TEMPLATE_ADDR_SIG*` + zero `[r10]`-cursor in the pattern family; wire into Session Setup; **re-measure SNOBOL
m4** — expected > 0/6 once a pattern chain assembles+links+runs standalone). R13/R14/R15 are SysV callee-saved, so
they survive `call memcmp@PLT` with no per-box save. **Mode-2 oracle (`bb_exec.c`) is UNTOUCHED — m2 7/7 HARD must
stay invariant every step.** Each step: prove topology unchanged, migrate BINARY+TEXT together, disasm-verify the
new register usage, gate.

**Then** PB-RB-4 (emitter arm only — topology proven `e39c329`): `IR_STITCH_SEQ`/`IR_STITCH_ALT` in IR.h, the two
`bb_stitch_*.cpp` templates (BINARY+TEXT) wiring two child heads' four ports (runtime twin of `wire_seq`/`wire_alt`),
emit_core dispatch + append-only Makefile, mode-3 probe for `S ('a'|'b')` / `S 'a' 'b'`. Then PB-RB-5…OPT, BROK-0…3.

## Gates at handoff (all green / at floor)

`prove_lower2.sh` **67/0** · PAT-BB probes **3/3** · SNOBOL4 smoke m2 **7/7 HARD** / m3 5/6 (floor 5; lone fail =
`define`/user-fn) / m4 0/6 (floor 0; REG ladder unblocks) · Icon m2 **12/12 HARD** / m3 12/12 / m4 12/12 ·
`test_gate_no_vstack.sh` PASS (g_vstack 0) · `test_gate_sm_dead.sh` 0 · `audit_concurrency_invariants.sh` OK
(FACT RULES byte-identical-×3) · purity 7 (MEDIUM_BINARY-exempt baseline).

## Pointers

GOAL: `.github/GOAL-SNOBOL4-BB.md` (single source of truth; 🔴 CURRENT PRIORITY at top, then sessions/architecture,
PB-RB ladder, REG ladder is now AT TOP, BROKERED rung, watermark+log at bottom). Match driver:
`SCRIP/src/emitter/BB_templates/bb_match.cpp`. Literal matcher (REG-1 target): `bb_lit.cpp`. Emitter glue:
`src/emitter/emit_bb.c` (`flat_drive_match`, `sno_flat_chain_build`, `codegen_sno_flat_chain_body`). Epilogue / v=1/99
contract: `src/emitter/XA_templates/xa_flat.cpp`. Lowering: `src/lower/lower.c` (`lower2_match_entry`:2276); proof:
`src/lower/prove_lower2.c` (`dump_match`:209). Probes: `test/snobol4/pat_bb/`, harness
`scripts/test_sno_pat_bb_probe.sh`.
