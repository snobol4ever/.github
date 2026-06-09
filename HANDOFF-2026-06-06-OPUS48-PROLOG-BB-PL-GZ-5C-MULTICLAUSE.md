# HANDOFF — 2026-06-06 — Opus 4.8 — PROLOG-BB: PL-GZ-5c (multi-clause RULE predicates)

**Landed:** SCRIP `aa587c9` — PL-GZ-5c: multi-clause RULE predicates = full `path/2` on the
Proebsting-pure path, all three mediums byte-identical. The seed's `path`/`edge` shape is now real
compiled output. Ladder + STATE updated in `.github/GOAL-PROLOG-BB.md`.

## What 5c is

Callee-level choice over rule clauses, exactly the seed's `path_t`:

- **ONE frame per activation:** `[args | clause-0 locals+synth | clause-1 locals+synth | … | child
  slots]`. mark stays at `[ζ+0]`; the 1-based **cursor lives at `[ζ+4]`** (the seed's `ζ->i`) — both
  ints share the pre-cell header qword, zero extra slots. Cursor init `mov FR(4),1` at α (NC>1 only).
- **Per-clause body chains** keep the gz backward-redo wiring untouched. Clause K's goal-0 failure
  target is the **clause-advance block** (`cursor=K+2; rt_trail_unwind(entry mark); jmp clause K+1's
  first goal` — the seed's `fK_ω`); the LAST clause's goal-0 failure goes straight to the callee ω
  landing (which already unwinds + returns 0).
- **β re-entry = bb_cell_choice's cmp-chain**, emitted as per-clause template fragments: aspect 2 =
  `mov eax,FR(4); cmp eax,K+1; je δ` (δ = clause K's redo), aspect 3 = `jmp δ` (last clause's redo).
  A clause's redo is its LAST goal's β label; det βs pass through to their ω, so all-det clauses
  (facts) collapse onto the advance block — the seed's `edge_β → fK_ω` exactly.
- **Facts are empty-body rule clauses** under `pl_gz_rule_clause`, so a multi-clause FACT pred called
  from a callee body becomes a framed callee (the seed's `edge/2` with its own `edge_t`). Query-level
  fact choices keep the cheaper gz4 `CELL_CHOICE` inline — both mechanisms coexist, both correct.
- **Recursion:** validation cycles broken by `g_gz_visiting[]` (a graph on the list is being
  validated up-stack — assume ok, the outer frame fails for real if it must); build cycles broken by
  the 5b shell-first memo. `path :- edge, path` admits and runs at depth (gate probe `b c d e`).
- **One body builder:** `pl_gz_slot_map(s, ar, lbase)` = `s<ar ? s : lbase+(s-ar)`; single-clause
  callers pass `lbase=ar` ⇒ identity. No duplicated logic (the FACT rule held).

## The bug that mattered (LESSON, now in the ladder entry)

Driver→template immediates must ride **`op_off`/`op_sa`/`op_sb` ONLY**. `walk_bb_node`
(emit_core.c:385) unconditionally copies `nd->ival` into `g_emit.op_ival` — for `IR_CALLEE_FRAME`
nodes `nd->ival` is the **callee pointer**, which stomped the cursor constants set before `FILL`.
Symptom: `mov dword ptr [r12+4], 140535436082688` in the .s; m3 printed `b` then segfaulted on the
first clause-2 entry. Fix: aspects 2/4 read `_.op_off`.

## Files touched

- `src/interp/IR_interp_state.h` — `pl_gz_callee_t` += `int nclauses; IR_t * clause_head[4];`
- `src/driver/scrip.c` — `pl_gz_choice_rule_clauses` (validator + visiting list);
  `pl_gz_rule_body_goal_ok` / `pl_gz_rule_inline_check` admit choice-rule callees;
  `pl_gz_rule_callee_body(zs,cg,ce,clause_idx,lbase,…)` with slot remap + shared child allocation
  (`ce->arity + ce->nlocals + ce->nchild++`); `pl_gz_clause_nsynth`; `pl_gz_callee_get_choice`
  (two passes: lbase/total, then bodies); `pl_gz_callee_get_any` dispatcher; both call sites
  rerouted. Empty clause chains: legal single-clause (old behavior), declined multi-clause.
- `src/emitter/BB_templates/bb_callee_frame.cpp` — aspect 0 cursor init; aspect 1 β omits `jmp δ`
  when NC>1 (falls into the driver-sequenced cmp-chain); NEW aspects 2 (dispatch test), 3 (dispatch
  tail), 4 (clause advance). All bytes in the template; the driver only sequences + wires ports.
- `src/emitter/emit_bb.c` — `gz_emit_callee` multi-clause: flat per-clause label arrays with
  `cbase[]`, advance blocks, redo[] capture, β cmp-chain emission; NC==1 path emits the exact landed
  sequence.
- `scripts/test_gate_pl_gz5c.sh` — NEW (4 positives m2-verified: path `b c d`, all-det 2-clause
  `a b`, mixed fact+rule `a b c`, depth chain `b c d e`; structural asserts: `[r12 + 4]`, `_adv`,
  `rt_enter` in the .s; negatives: cut / list heads / 5-clause decline identically; corrupt-proven
  via the fail-loud discipline).
- `scripts/test_gate_pl_gz5a.sh`, `test_gate_pl_gz5b.sh` — **RATCHETED:** the 2-clause-rule negative
  is a 5c positive now; the frontier probe is arity-3 (`ar>2` is outside the rsi/rdx arg ABI — a
  stable negative until a deliberate ABI rung).

## Gate state at HEAD

GATE-1 m2 **5/5 HARD** · m3 4/0/1-EXC (`recursion` = cut+arith, flips by GZ-8) · m4 5/5.
GATE-3 m2 **115/115** · m3 18/0/97-EXC · m4 105/0/10-EXC. Coupling 19/10/0/39.
gz2 / gz3 / gz4 / gz5a / gz5b / **gz5c** all PASS. Corpus checkout clean.

## Next opener: PL-GZ-6 — cut

Lexical cut = pure wiring (the seed's `firstpath/1`; the full seed program then prints `b c d b`);
dynamic cut = frame gate (paper §4.5). Deletes the `rt_get_cut_flag`/`rt_choice_cut_*` global
protocol from the new path. The gz5c gate's neg1 (cut clause) flips to a positive then — ratchet it
the way 5a/5b were ratcheted here.
