# HANDOFF 2026-06-06 — Opus 4.8 — SNOBOL4-BB: ARBNO ALT-ARM FIX + BROK-0

**Repos at handoff:** SCRIP `680f23e` pushed; .github this commit; corpus untouched. Trees clean.

## Rung 1 — `f44f4df` ARBNO alternation child loses arms (054 m4 FLIP; rung M4 17→18, FAIL-M4=0)

Prior session's frame-corruption hypothesis was WRONG. Real cause: `wire_alt` returns α_out=entry[0] (FIRST ARM); `codegen_flat_body` walks ONE node → `ARBNO('a'|'b')` child body emitted only `LIT('a')`. Fix (emit_bb.c, +7/−1):
1. `ir_node_is_alt_arm` accepts `IR_PAT_ALT` alongside `IR_ALT`.
2. `codegen_flat_body`: `nd = ir_skip_alt_arms(nd)` — flat emission starts at the driver-owned join.
3. ARBNO pre-build save/restores `g_emit_cfg` to the INNER graph (operand_aux is PER-GRAPH; both the skip predicate and `flat_drive_alt`'s arm fetch missed otherwise).

SPITBOL manual grounding: ARBNO shy, null-first, each retry adds one instance (pp.121-122, 212). Manual's recursive-LIST example (`ARBNO("," P)` via pattern variable) passes `--run`. FIDELITY GAP (latent, no gate exercises): greedy loop + pop-only β cannot re-enter a matched instance's REMAINING alternatives (`ARBNO('ab'|'a') 'b'` on `'ab'` shape) — full per-instance backtracking comes with BROK-2's wired child.

## Rung 2 — `680f23e` BROK-0 dead-caller excision (−62 lines, m4 byte-neutral)

`patnd_needs_xlate` is CONDITIONAL, so deadness was proven empirically: fprintf probes on all 4 stmt_exec PATND call sites = ZERO hits across m3 smoke, m3-native smoke, GATE-2 broker (32 pass), and the full 280-program m3-native corpus. Deleted: `g_bb_mode` + `BB_MODE_*` enum, `bb_build_pure_mode`, `--bb=brokered/wired` flags + validation + usage, the BROKERED/DRIVER stmt_exec branch; surviving sites call `bb_build_flat`. `bb_build_brokered` the FUNCTION survives for BROK-3. 052/054 m4 asm byte-identical pre/post.

## Gates at handoff (2026-06-06 container)

smoke 19/19 (m2 7/7 HARD) · M3-native 19/19 · rung M2=18 M4=18 (053 FAIL-M2 pre-existing) · broker 32 · prove_lower2 PASS · REG-FENCE TIER1=0 · no_bb_bin_t 0 · binary-arms audit OK. Broad gates env-drifted: GATE-3 137-138/280, GATE-4 160/280, M3-native broad 160/280 — stash-baseline-verified (+1 with fix), NOT code regressions; old 178/251/195 watermarks were a different container.

## Next (see GOAL-SNOBOL4-BB.md frontier)

BROK-2 wired-child conversion (`call child_α` → jmp α/β; needs no-prologue/epilogue child mode in `codegen_flat_body`, γ/ω jmp to ARBNO labels) → BROK-3 → REG-RO (r10≈24). REC-2 (ARBNO BINARY arm) preferably AFTER BROK-2 settles the child contract.

## Facts that cost time (also folded into GOAL file)

- `operand_aux` is per-graph: sub-graph walks (ARBNO inner, pattern graphs) MUST switch `g_emit_cfg` (save/restore, cf. emit_bb.c:1477) or lookups silently miss.
- Driver-owned kinds (PAT_CAT/PAT_ALT/PAT_FENCE/GCONJ) emit arms inline; `wire_alt`/`wire_seq` α_out = FIRST ARM — always `ir_skip_alt_arms` before single-node walks.
- Probe method for deadness: fprintf markers + grep across all gates; runners swallow stderr, validate plumbing with one direct `--run` first.
- Broad-corpus counts are container-sensitive: stash-baseline before calling anything a regression.
- GOAL file pruned this session (Lon directive): completed rungs deleted (SR-1a, PB-RB-1/2/3/4/8, BROK-0, REC-1, W1, stale duplicates, embedded old handoff); verbose blocks tersed. FACT RULE bodies byte-untouched (cross-file md5 contract).
