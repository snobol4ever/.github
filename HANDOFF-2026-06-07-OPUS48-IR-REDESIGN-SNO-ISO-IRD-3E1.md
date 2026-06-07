# HANDOFF 2026-06-07-C OPUS48 — IR-REDESIGN: SNO-ISO + IRD-3e-1 LANDED

## Commits (SCRIP origin/main)
- `2f17bf4` SNO-ISO-1 — complete+isolated SNOBOL4 value lower
- `5a40338` IRD-3e-1 — IF/WHILE cond child → operands[0], consumers dual-read

## Lon directive this session
Prioritize a COMPLETE and ISOLATED SNOBOL4 lower ahead of the IRD-3d prolog order.

## What landed
**SNO-ISO-1.** `lower_sno_value`'s default arm no longer calls `lower_value_shared` — lower_sno.c carries its own complete `sno_value_shared` dispatch (every arm explicit, default → `lower_unhandled`). The 15 shared `v_*` helpers it names were un-static'd and declared in lower_internal.h as shared infrastructure (same status as `lower_value_subgraph`/`wire_det_builtin1`). Zero `lower_value_shared` references remain in lower_sno.c.

**Census (instrumented run, sno 153 + sco 191 + rebus smoke).** Only `lang=1` ever fires — Snocone and Rebus transpile through the SNOBOL4 route. Fired kinds: QLIT 818, ILIT 456, VAR 347, PROGRAM 129 (→unhandled, NULL-tolerated), IF 118, SCAN 57, ADD 47, FLIT 39, IDX 37 (→unhandled), KEYWORD 36, plus MNS/PLS/SUB/MUL/DIV/POW, WHILE 12, ALT 10, DEFINE/VLIST/OPSYN/INDIRECT/DEFER/NAME, and stray pattern kinds in value role (POS/ANY/SPAN/BREAK/LEN/CAPT_COND → unhandled). **SNO-live α-writers: IF (wire_if), WHILE (v_while), ALT-DISJ (wire_alt).** UNTIL/REPEAT/EVERY/ITERATE-bang: zero SNO hits — icon-scope.

**IRD-3e-1.** Producers: wire_if `node->α=c1α` and v_while `wh->α=c1α` → `ir_operand_push(..., c1α)` (operands[0]=cond). Consumers dual-read: interp IR_IF arm (`cnd` accessor; ring-shape guard `!α&&!β` → `!cnd&&!β` — lowered/chain-RPN/ring regimes all route identically), interp IR_WHILE arm (3 loop reads via `cnd`), emit `while_cond_emittable(nd->α)` callsite → `bb_child0(nd)` (UNTIL shares the arm and still writes α — fallback covers), flat_drive_while guard + cond fetch → bb_child0.

## Untouched by design (recorded residue)
- IF/WHILE `->β` reads in interp = chain-shape then/body (RPN writers) — bulk-stage chain ecosystem.
- `while_cond_emittable` INTERNAL `cond->α`/`cond->β` reads — BINOP-child residue on an already-swept kind; converting them would un-degenerate a pre-existing m3 path = behavior change inside a sweep. Move, don't fix. Bulk scope.
- emit_bb.c 956/968 IF `->ω` reads = port wires (IRD-4 carrier change, not children).
- driver `icn_assign_safe_kind` = kind membership only.
- EMIT_PAIR_FILL / bb_fill_alpha = α-LABEL allocator, reads no child.
- interp IR_DISJ arm + flat_drive_disj read arms via `bb_operand_aux_get`, NOT `->α` — the DISJ α write (wire_alt 105 / pl_wire_alt 117) may be near-dead; census before assuming (driver gz DISJ sites: scrip.c 378/531/994/1156/1203/1231).

## Gate (both commits)
bake_ird3_baseline.sh at pre-session HEAD vs post: sno 153 / icn 9 / pl 8 / pas 5 per-file m2 sweeps byte-identical; **sco sweep ADDED** (191 .sc from test/snocone + corpus/crosscheck/snocone) byte-identical; **rebus smoke ADDED** (PASS=0 FAIL=4 pre-existing) identical; smoke_icon/prolog/snobol4/raku logs byte-identical; prove_lower PASS/FAIL rows md5-identical (68 PASS; raw log byte-diff is ASLR pointer noise in dump rows — compare rows, not bytes). IF (118×) and WHILE (12×) are corpus-hot, so sweep identity IS the live-kind proof.

## Environment (fresh container)
apt-get install -y libgc-dev; make. `make libscrip_rt` MANDATORY before any m4 work.

## NEXT (order per Lon 2026-06-07-C)
1. **IRD-3e-2 DISJ cluster** — shared wire_alt + prolog pl_wire_alt producers TOGETHER + driver gz DISJ census + operand_aux arm-list fold.
2. **IRD-3d prolog remaining** — ITE 313/334/355; γ-chained STRUCT 229/254 + g_builtin 272 arg lists (IRD-4 prereq); name-aware BUILTIN pair 179/194/209; kind ~381.
3. **IRD-3e-rest icon-scope** — ITERATE-bang 182, EVERY 347, UNTIL 424, REPEAT 437.
4. **Bulk stage (c)** — IR_interp.c/emit_bb.c residue, three RPN writers + chain consumers, gz-synth, RETURN chain residue, operand_aux DELETED.
5. **IRD-4** — γ/ω → IR_ref_t{node,"α"/"β"}; DELETE α/β fields; rename t→op. lower_sno already speaks the AG discipline end-to-end (γ/ω inherited in-params, α/β synthesized out-params only, operands for data feeds) — it should need ZERO touches at IRD-4.
6. **IRD-5** — fence audit, sizeof, ARCH-IR.md.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
