# FINDING 2026-08-03 (HQ seat, Lon-directed) — THE UNWIND RULING · U-1a SKELETON LANDED INERT · THE VALUE SPINE HAS NO βs TO UNWIND INTO

Parent: SCRIP `fa007877`. This session: ruling recorded (`.github` 3 files), U-1a choke arm landed inert behind `SCRIP_UNWIND` (default OFF, gate-off byte-identical to parent by stash A/B).

## §1 THE RULING (Lon, verbatim intent — full four-clause law at the top of GOAL-SNOBOL4-BB.md)
Failure NEVER whacks. Failure is an UNWIND: box N's ω frees OWN K only, rolls to pred's β, until STATEMENT_BEGIN's β exits to the `:F` target / next statement. Whacks are FORWARD-path only: FENCE0/1 commit · MATCH_END (SN4 language fence) · STATEMENT_END final success. "For each statement, you either arrive at one end or the other." SNOBOL4's statement is a natural FENCE boundary; Icon's statements are expressions and are NOT — same Byrd-Box algebra, language-selected sync points. VOIDED: zd_wp accumulated fail staging (the 5,923 census), ZW-5 O-2 depth stubs, ENDJMP/op_wsteal (same-day landing, superseded), mid-extent depth guards. SURVIVES: the ΣK ZPOP fold (legal fusion over whitelisted-trivial βs), law-4 RBP for success-side indeterminable whacks + match housekeeping.

## §2 U-1a LANDED (emit.cpp staging choke, before the ENDJMP block)
Arm: for armed non-UCLAIM members with `zd_wp>0`, plain edge (`!omega_is_beta/phi`), `op_wpop==0`, `!scan_live`, `!flat_stmt_frame`, in-BEGIN-bracket — retarget `node_ω → betas[pred]` with staged pop = LOCAL DIFFERENCE `(zd_k+zd_wp)[i] − (zd_k+zd_wp)[p]`, `wsteal=1`. Pred search walks backward inside the statement bracket; NODE-EXACT chased-target equality (one statement, one fail exit — a mid-extent `:F(elsewhere)` never finds a same-target pred and stays legacy, no arithmetic exclusion needed, the n54 class dissolves). The EARLIEST fail-capable member keeps its original edge = the full `(zd_k+zd_wp)` pop to the fail target — the BEGIN.β terminus FUSED over BEGIN's K=0 relay. Telescoping: chain net == legacy net, always. ENDJMP + ZW5-pool arms stand down per member via `!_uw_stolen`.

## §3 THE MEASUREMENT — FIRE SET IS EMPTY, AND WHY (⭐⭐⭐ the session's real finding)
Gate-on ≡ gate-off byte-identical on every probe tried (2-predicate value spine uw2/uw3; 044/045 POS/RPOS). Root cause, read from the dispatch table and templates, three layers:
1. **The value spine has NO emitted βs.** `IR_LIT_* / IR_VAR / IR_COERCE_NUMERIC / IR_CMP_TEST` dispatch cases call `DRIVE_FILL` with NO `DRIVE_PAIR_DEF_JMP` — their β labels are never defined anywhere in the output. Lon's opening observation ("all the missing beta sections") is literally visible at emit.cpp ~1218/~1228/~1367. Only BINOP-class, CALL-class, GOTO/SUCCEED/CUT, the STATEMENT trio, and the match kinds define β.
2. **`x86_pair_loop`'s jmp is RAW** (x86_asm.h ~2186): `jmp <name>` / bare 0xE9 record, NO X86H_JMP hook — a pair-flushed β carries no pops. The pops-bearing β primitive is the trivial trampoline (`x86_beta_trampoline` shape: hook pops + jmp resolved ω) that `flat_trivial_beta`'s whitelist describes (POS/RPOS/ABORT + gated SAVE only).
3. My pred guard borrowed `flat_trivial_beta` — so the pred whitelist ∩ plain-edge armed value-spine population = ∅. Scan statements are `scan_live`-guarded out; POS/RPOS live inside them.

## §4 WITNESS — THE DISEASE ITSELF, BASELINE
`/tmp/uw3.sno` (`X = GT(A,0) LT(A,B) A + B :F(FA)`, A=5): m3 prints `took fail` then **rc=139, GATE OFF, at parent** — the fail path over-frees and crashes after correct output at HEAD today. The success path (uw2) is green. ZD diag for the statement: 16 members, wpop telescopes 0→240, every fail edge staged with accumulated depth. This is the ruling's target population in one probe.

## §5 ARTIFACT STALENESS (attribution, stash A/B)
10 of 60 sampled crosscheck `.s` differ from compiler output — IDENTICALLY for the PARENT binary (4/4 sampled: 058_capture_dot_immediate, 033_goto_success, coverage_sno_nodes, 097_define_capture_return_d2probe). The `fa007877` merge landed without a regen; the s23f/s217 skew class. This session's gate-off delta is ZERO. Regen ×4 owed at the next code landing.

## §6 U-1b RECIPE (the lighting slice — next session)
1. **β emission for fail-capable value-spine kinds**: stage a per-node flag at the choke (e.g. `g_zd_uwbeta` → `_.op_uw_beta`, the sanctioned promoted-scalar shape) for gate-on armed CMP_TEST/COERCE_NUMERIC (BINOP/CALL β defs exist — verify their emission path fires hook pops, else same treatment); template edit (OMEGA-owned `bb_cmp_test.cpp`/`bb_coerce_numeric.cpp`): `+ IF(_.op_uw_beta, x86_beta_trampoline())` — R2/R6-compliant, medium-invisible. β body under staged wpop/wsteal = `add rsp, staged; jmp node_ω` — for a legacy-staged member that is the FULL remainder (correct terminus anywhere), for a U-armed member it is the DIFF link.
2. **Widen the pred whitelist** in the U-1a arm from `flat_trivial_beta` to {CMP_TEST, COERCE_NUMERIC, BINOP set, CALL set} — exactly the kinds whose β now exists.
3. **U-1c**: wire `IR_STATEMENT_BEGIN.ω` in lower's shim (today `lc_build(..., fb, NULL)`) to the statement fail continuation → BEGIN.β becomes the literal terminus; drop the earliest-member fusion.
4. Gates: uw2/uw3 witness pair (uw3 must go rc=139→0 once the chain owns the exit and glue stops double-whacking — if it stays 139, MONITOR-FIRST bracket the exit), full 318 BY SET both modes, bench 18/21, regen ×4.

## §7 GATE (this session)
Gate-off: byte-identical to parent (stash A/B, 4/4 divergers parent-attributed; 50/50 honest artifacts match). Gate-on: byte-identical everywhere (inert by §3). Build green -O0. No corpus commits (regen owed, §5). Full 318 not re-run — zero behavioral delta by construction.
