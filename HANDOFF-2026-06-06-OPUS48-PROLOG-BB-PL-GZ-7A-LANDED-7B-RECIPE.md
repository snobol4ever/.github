# HANDOFF — PROLOG-BB · PL-GZ-7a LANDED (m2 ITE-commit to canon) · PL-GZ-7b RECIPE (new-path §4.5 box)
2026-06-06 · Opus 4.8 · SCRIP main @ `7a7bf75`

## STATE AT HANDOFF
SCRIP commits this session: `3d9ccfd` (PL-GZ-7a m2 ITE-commit) · `7a7bf75` (gate `test_gate_pl_gz7.sh`).
Both rebased over incoming PB-10a2 / PB-10a2-m34 / SNO-HY-2b work and battery-verified on the merged tree.
Gates at handoff: GATE-1 m2 5/5 HARD · m3 4+1EXC · m4 5/5 — GATE-3 m2 **115/115 HARD** · m3 18/0/97 ·
m4 105/0/10 (ZERO re-baselines: the buggy commit behavior was never encoded in any `.expected`) —
gz2/3/4/5a/5b/5c/6/6b/7 PASS — one_box · no_vstack · coupling PASS — corpus `.s` clean.
Pre-existing on the remote tip, NOT this session's: rebus hello-row drift in
`test_smoke_compile_hello_all_langs.sh` (FAIL-compile; present at the PB-10a2 tip before my commits —
bisected; likely the documented `walk_bb_node kind=7` residue, owner rung PB-10a2-m34 lineage).

## LANDED — PL-GZ-7a: m2 ORACLE TO CANON (paper §4.5 bounded condition)
Headline: `( a(X), X >= 2 -> true ; X = 0 )` under a fail-driver — m2 printed `2 3 0`, now prints `2`,
== m3 == m4. Absorbs WAM-CP-9. Design (all in `3d9ccfd`):
- `IR_ITE` (m2 case): records `zi->cp_mark = resolve_cp_current()` and resets `zi->committed = 0` on every
  forward entry. Stateless otherwise — every arrival at the node IS a forward entry, because the published
  construct β = ω_in (semidet) and in-conjunction redo bypasses the node by wiring.
- `IR_ITE_COMMIT` — new kind, inserted at lower time on the cond.γ edge (cond's success target): truncates
  the ledger to `zi->cp_mark` (`resolve_cp_truncate`) and sets `zi->committed = 1`. This is the bounded
  condition: the condition's choicepoints are deleted at first success.
- `IR_ITE_GATE` — new kind, inserted on the cond.ω edge: `committed ? ω_in : else.α`. The paper's E1.fail
  gate — post-commit condition exhaustion must reach ω, never Else (this killed the residual `0`).
- Ledger-coherent liveness: `bb_body_has_live_choice` IR_CHOICE arm now requires ledger membership
  (`c == zc->cp && c->resume == bb` walk — the gz6 `cp_cut_away` test generalized). A committed-away clause
  CP reads dead, so the goal-spine resume never re-walks a bounded condition. The re-walk never re-enters
  the ITE because the commit removed exactly the liveness that would trigger it; forward re-entries get the
  unconditional fresh reset they need. (A resume-mode-flag protocol was designed and proved UNNECESSARY.)
- `\+` (g_neg_goal) and `\=` (g_not_unify) share the same node pair — both conditions are bounded.
- m4 untouched BY CONSTRUCTION: the legacy walker (`flat_drive_ite`) is structure-driven — it reads
  `zi->cond/then_/else_` and passes its own labels, never following lower-time γ/ω edges, so edge-only
  nodes are invisible to it. Both new kinds ARE whitelisted in `pl_rich_node_emittable` (scrip.c) because
  `pl_rich_graph_ok` iterates EVERY `g->all[]` node with `default: return 0` — without the whitelist every
  `->`/`\+`/`\=` graph would de-admit from the m4 RICH path.
- Construct-level semidet (β = ω_in) is the codified port-table row and AGREES with the m4
  `flat_drive_ite` β→ω tombstone — pinned by the `semidet` probe (else-generator NOT re-satisfied).
Files: `src/contracts/IR.h` + `scrip_ir.c` (two kinds after `IR_CELL_CUT`), `src/interp/IR_interp_state.h`
(`bb_ite_state_t` += `void *cp_mark; int committed;` — trailing, ABI-safe), `src/lower/lower_prolog.c`
(g_ite/g_neg_goal/g_not_unify: zi alloc'd before cond; commit node = cond's γ_in; gate node = cond's ω_in),
`src/interp/IR_interp.c` (three cases + liveness), `src/driver/scrip.c` (whitelist).
Gate `test_gate_pl_gz7.sh` (`7a7bf75`): five probes — commit · barecall · reentry · semidet · negbound —
each pinned m2 == m3 == m4 == explicit canon. Behavioral pin only at this stage (these programs run the
LEGACY path in all modes); GZ-path assertions, declines, and the corrupt-proof arrive with 7b's ratchet.
ACCEPTED CAVEAT: `zi->cp_mark/committed` are per-NODE, not per-activation — a recursive ITE-in-condition
clobbers the outer activation's mark (under-truncation). Exotic; legacy-only; 7b's frame rows are
per-activation by construction.

## DIAGNOSED — DISJ trust_me_else_fail (gz6b-logged m2 divergence): ROOT FOUND, FIX POINT NAMED
Repro isolation (decisive): disj ALONE is canon; the divergence REQUIRES a failing goal AFTER the disj.
  d1 `main :- ( p(X), write(X), nl, fail ; true ).` → m2 `a` ✓
  d2 `main :- ( p(X), write(X), nl, fail ; true ), q(w).` (q(w) fails) → m2 `a a` ✗ (m3/m4 `a` = canon)
Root: when the B-side goal fails, the GCONJ backward-resume re-drives the already-committed disj — the
static β-chain threads into arm0's internals, which SELF-RESET on exhaustion (the invariant that makes
forward re-entry work), so they re-run FRESH and re-print. The disj-node advance path is NOT the re-entry
route, and liveness is NOT the gate: a last-arm liveness guard in `bb_body_has_live_choice` +
`pl_callee_disj_hint` (live iff `counter < n_arm-1` via `bb_operand_aux_get`) was implemented, proven
ineffective on the repro, and REVERTED (tree clean). The fix point is the GCONJ-resume ↔ disj-advance
CONTROL PATH: on the last arm the disj's redo routing must be dead (CP deleted), i.e. the backward chain
must not thread into arm internals once committed. NOTE: the freshly-rebased `cs->disj_hint`/`cs->cp_floor`
scaffolding in the liveness readers is ORTHOGONAL — it does not address this control-flow re-entry.
RECOMMENDATION: this is a redo-routing redesign of legacy machinery that PL-GZ-FENCE deletes; m3/m4 are
already canon and the gz6b gate pins them. Spend the effort on 7b instead; sweep this only if a rung
ratchet demands m2 parity here.

## RECIPE — PL-GZ-7b: THE NEW-PATH §4.5 BOX (recon complete, implement from here)
Template architecture (read these first, they are the whole idiom):
- `src/emitter/BB_templates/bb_cell_cut.cpp` (21 lines) — pure wiring: α falls to γ; β jmp ω; the driver
  wires its ω to the callee fail landing. The "delete CP by never wiring it" philosophy.
- `src/emitter/BB_templates/bb_cell_choice.cpp` (80 lines) — frame rows `GZ_CELL_OFF(mark_slot)` =
  trail mark + `mark_slot+1` = 1-based cursor; α takes `rt_trail_mark`; clause-k fail landing L(k) sets
  cursor=k+2, unwinds, falls into k+1; last L unwinds + jmp ω; **β = cmp/je dispatch on the cursor row** —
  the house indexed-goto. THIS IS THE §4.5 GATE DIALECT.
- Emitter drive: `emit_bb.c` `gz_emit_callee` (~line 437) — per-goal `pgl[j]`/`pgb[j]` α/β labels; redo
  target `gw = (g->t == IR_CELL_CUT) ? cl_ω : (jj==0 ? failtgt : pgb[j-1])`; `gz_fill_goal(g, next_γ, gw,
  pgb[j])`; clause-advance + β-dispatch emitted via `FILL(frame_node,...)` with `g_emit.op_sa` aspects and
  `lbl_δ` (gz6b's op_sa=1/2/3/4 precedent). `flat_drive_gz_query` (~line 510) is the query-frame analog
  (two-segment dval==2.0 precedent — aspects degenerate when a segment is trivial).
- Driver: `pl_gz_admit` (scrip.c:803) / `pl_gz_build_goal` (scrip.c:717) — builds γ-linked CELL chains
  per goal kind (CELL_UNIFY fact-inline · CELL_CHOICE via `pl_gz_choice_inline` w/ `mark_slot = *cslot,
  cslot+=2` · CELL_CALL w/ callees[] · DET_WRITE/DET_NL · FAIL · SUCCEED=skip). `pl_gz_count_synth`
  (scrip.c:701) pre-counts synth slots. Templates dispatch from `emit_core.c` ~494:
  `case IR_CELL_X: { extern void bb_cell_x(void); bb_prepare(nd); bb_cell_x(); }`.
The §4.5 ifstmt mapped onto this dialect (VERBATIM — start/resume/gate, bounded E1):
  ifstmt.α: jmp E1.α. E1 chain emitted like a clause body, EXCEPT: its success continuation = a stub
  `mov FR(gate_off), 1 ; jmp E2.α`; its first-goal fail target = the E1-fail landing
  `mov FR(gate_off), 2 ; jmp E3.α`. ifstmt.β: `cmp FR(gate_off),1 ; je E2.resume ; jmp E3.resume`
  (the bb_cell_choice cursor-β idiom = the paper's `goto [gate]`). E2/E3 chains: success → ifstmt.γ,
  fail-chain bottoms out at ifstmt.ω. **E1's per-cell β labels are emitted but NEVER REFERENCED** — the
  bounded condition: for a CELL_CHOICE condition this IS gprolog's Pl_Delete_Choice_Point, achieved by
  wiring (cut-cell philosophy), no runtime call, coupling gate stays 0. Det E2/E3 degenerate: their
  "resume" = their β tombstones → ω (gz6b dval-degeneration precedent) — emit the gate machinery anyway
  (truthful template), it simply dispatches to tombstones.
Implementation order:
 1. `IR_CELL_ITE` after `IR_ITE_GATE` in IR.h + scrip_ir.c name. Add to `bb_kind_is_driver_owned`
    (emit_bb.c — check it; cells are driver-owned so m2 never sees them) and any cell whitelists.
 2. `pl_gz_ite_state_t { IR_t *cond_head, *then_head, *else_head; int gate_slot; }` in IR_interp_state.h.
 3. `pl_gz_build_goal`: `if (gg->t == IR_ITE)` arm — pull `bb_ite_state_t *zi` from ival; build THREE
    sub-chains by recursing the SAME builder over `zi->cond_root/then_root/else_root` (NO-DUP: GCONJ root →
    iterate its `zs->goals[]`; single goal → one call; IR_SUCCEED → empty chain head=NULL means
    fall-through). `gate_slot = (*cslot)++`. Nested goals MUST also flow through `pl_gz_count_synth`
    (factor a shared per-goal counter the way gz6b factored the builder). Then emit one IR_CELL_ITE node
    carrying the state into the parent chain.
 4. `emit_bb.c`: in the chain-drive loop(s), `IR_CELL_ITE` → a recursive sub-chain drive (reuse/factor the
    pgl/pgb per-goal loop from gz_emit_callee — NO-DUP; keep the CELL_CUT cl_ω ternary working INSIDE
    branches) with the wiring above. The gate stubs + β dispatch can live in `bb_cell_ite.cpp` driven by
    op_sa-style aspects (gate-set-1 / gate-set-2 / β-dispatch) with `lbl_δ` carrying the jump targets —
    exactly the bb_query_frame aspect pattern.
 5. `bb_cell_ite.cpp` + Makefile **×2** (sources list ~line 170s AND compile rule ~line 391s — the known
    gotcha). MEDIUM_TEXT comment citing §4.5 verbatim (start/resume/gate; E1 bounded by unreferenced β).
 6. m3 ≡ m4 by construction (same MEDIUM_BINARY in-process). No interp case needed for driver-owned cells.
 7. Probes — floor (det cond): `p(a).  ( p(X) -> write(X) ; write(n) ), nl.` → `a`; const-mismatch cond →
    `n`. **MONEY probe (choice cond, THE commit):** `p(a). p(b). main :- ( ( p(X) -> write(X) ;
    write(n) ), nl, fail ; true ).` → exactly `a` in ALL modes (m2 canon already pinned at 7a). Arith
    conds are NOT admitted until PL-GZ-8 — the 7a headline program stays legacy until then; do not force it.
 8. Ratchet `test_gate_pl_gz7.sh`: keep the five 7a probes; ADD admitted probes asserting the GZ path
    (m3 stderr has no INTERP-FALLBACK; `.s` contains the ifstmt labels), DECLINES (arith cond → unadmitted,
    legacy verdicts still equal), and a CORRUPT-PROOF (force gate index 1↔2 or break a label → loud
    divergence) per the gz6b style.

## PROCESS NOTES (hard-won this session)
- ALWAYS rebuild BOTH targets after edits and filter case-insensitively: `make ... 2>&1 | grep -iE
  "error|Built"`. A lowercase-only grep hid a failed build and produced a STALE-BINARY false negative
  (`2 0`) that cost a full debugging detour — the pure gate design had been correct all along.
- The remote moves fast (three sibling pushes during this session). `git pull --rebase`, then RE-RUN the
  full Prolog battery on the merged tree before pushing — incoming work touched IR_interp.c twice today.
- Token remote: `git remote set-url origin https://<token>@github.com/snobol4ever/<repo>` then push.
- `IR_interp_resume` re-walks from `bbg->entry`, re-executing every node case; node cases must be
  idempotent under re-walk via their own state. Trust ledger truncation + liveness over per-node latches:
  two latch designs failed (alternating-eaten iterations) because the published β=ω_in bypasses the node.
- Per RULES: corpus `.s` hygiene after suite runs (clean this session); commit identity LCherryholmes.
