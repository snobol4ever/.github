# HANDOFF 2026-06-06 (OPUS48, session B) — PROLOG-BB: PL-GZ-7b LANDED + GOAL PRUNE

SCRIP commit this session: `d85d8f3` (PL-GZ-7b). .github: `7510c75a` (GOAL prune 716→423, nine byte-identical FACT-RULE bodies verbatim, md5 invariant kept) + this doc.

## What landed (7b — the new-path §4.5 ifstmt box, `IR_CELL_ITE`)

Box = pure frame-gate WIRING, zero control-runtime calls (coupling 0). Emission shape, per ITE cell in a GZ chain:
ifstmt.α (comment only) falls into E1 (cond chain, emitted via the factored `gz_emit_chain`); E1 chain-γ = stub `mov FR(gate),1 ; jmp Then.α` (or ifstmt.γ when Then empty); E1 chain-ω = stub `mov FR(gate),2 ; jmp Else.α` (or ifstmt.γ when Else empty — the \\+ shape); Then/Else chains: success → ifstmt.γ, fail-chain bottoms at ifstmt.ω, CELL_CUT cl_ω ternary preserved inside; ifstmt.β = `def PORT_BETA ; mov eax,FR(gate) ; cmp 1 ; je δ ; jmp ε` with δ/ε = branch chain resumes (det tombstones → walk out at ω). **E1's resume label is emitted UNREFERENCED = the bounded condition** (Delete_Choice_Point by wiring).

Pieces: `IR_CELL_ITE` (IR.h after IR_ITE_GATE + scrip_ir.c name) · `pl_gz_ite_state_t{cond_head,then_head,else_head,gate_slot}` · driver `pl_gz_build_root` + ITE arm in the ONE builder, `pl_gz_count_synth` factored per-goal/per-root with ITE recursion, admit claimed-GCONJ pre-pass (ITE branch GCONJs excluded from softdisj accounting), IR_ITE reject dropped · emitter `gz_collect_callees` (ITE-recursive) + `gz_emit_chain`/`gz_emit_cell`/`gz_emit_ite` factored from the pgl/pgb loop, both drive loops rewired · `bb_cell_ite.cpp` (op_sa 0/1/2/3) + Makefile ×2 + emit_core dispatch.

## The two traps (cost this session — do not rediscover)

1. **`bb_prepare` bb_zn whitelist** (emit_bb.c ~890): bb_zn is set ONLY for an explicit kind list (CATCH/CELL_CHOICE/CELL_CALL/CALLEE_FRAME — now + CELL_ITE). A missing entry makes EVERY template aspect read NULL state and bomb (m3 SIGABRT rc=134, m4 .s full of rt_bomb). The recipe's "check any cell whitelists" meant exactly this. Any future cell kind: add it here FIRST.
2. **Construct-semidet pin vs §4.5 gate dispatch.** The gz7 `semidet` probe PINS ITE β=ω_in (else-generator NOT re-satisfied). The recipe's dispatch-to-resumes is truthful only when resumes are tombstones → **`pl_gz_chain_det` declines CELL_CHOICE/CELL_CALL in Then/Else** (cond unrestricted — bounded). All five 7a probes hold: `barecall` flips to GZ and stays canon; `semidet`/`commit`/`reentry`/`negbound` stay legacy. To admit resumable branches later WITHOUT breaking the pin: route the β-dispatch δ/ε to gw instead of chain resumes (and delete the guard).

## Verification (all on `d85d8f3`)

GATE-1 5/5 · 4/0/1-EXC · 5/5 (unchanged). GATE-3 m2 115/115 HARD · m3 **18→20** ratchet UP (+2 ITE rungs newly GZ-admitted, zero fails) · m4 105/0/10 unchanged. `test_gate_pl_gz7.sh` ratcheted + PASS: legacy pins + gzfloor1 (`a`) / gzfloor2 (`n`) / gzmoney (exactly `a`) GZ-ASSERTED (m3 no INTERP-FALLBACK, .s has gzi labels, no bombs) + arith-decline (fallback REQUIRED, verdicts equal) + corrupt-proof (stub ROUTING swap Then↔Else → loud divergence; gate-VALUE corruption is invisible at the det floor BY DESIGN — tombstone equivalence — becomes observable when GZ-8/9 admit resumable shapes). one_box PASS; FACT greps 0/0.

## GZ-8 opener notes

Arith/is + comparison builtins onto the GZ substrate (x86()-revamped bb_builtin families). Unlocks: ITE arith conditions — the 7a headline `( a(X), X>=2 -> … )` flips from legacy (build_goal's builtin arm currently declines anything but nl/write — that `return 0` is the decline point); the GATE-1 `recursion` m3 EXC. Builder entry points: `pl_gz_build_goal` builtin arm (scrip.c ~787) + admit's IR_ARITH reject (drop per-shape as re-admitted). Keep the decline-to-legacy safety: build failure → NULL → fallback. Ratchet `test_gate_pl_gz7.sh`'s gzdecl probe will need flipping from REQUIRE-fallback to REQUIRE-GZ when arith conds land — that flip IS the GZ-8 ITE evidence.

## Prune (also this session)

GOAL-PROLOG-BB.md 716→423 per Lon directive: landed rungs/closed tracks DELETED (git holds), MANDATORY-READ tersed (canon directive + modes + port table kept), nine byte-identical FACT-RULE bodies + NO-RESURRECT VERBATIM (exact-range diff vs siblings). RULES.md = Icon session's tersed version adopted. PLAN.md untouched (grand-master-reorg rule).
