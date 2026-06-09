# HANDOFF — 2026-06-04 Opus 4.8 — ICON-BB ICN-VAR-1 (the bb_var tier opens)

**HEAD (SCRIP) = `cf204ed`** on top of peer `84fee42` (PL-GZ-4b). One gated rung, chosen per the standing
watermark fork ("Or jump to the bb_var tier — the largest single unblock"). Full state in
`GOAL-ICON-BB.md` Watermark + the new ICN-VAR LADDER section (single source of truth).

## What landed (`cf204ed`)
Native Icon local-variable ASSIGN + READ, descr-flat-chain path:
- **`src/emitter/BB_templates/bb_assign_local.cpp`** (NEW box): rhs DESCR slot `[r12+op_a_slot]` 16B-copied
  to varslot `[r12+op_sb]` + own slot `[r12+op_off]`; pure `x86()`, reads only `_`, 0 raw-byte producers;
  single-shot β→ω, faithful per canonical `ir_a_Binop ":="` for the gated rhs shapes.
- **`emit_bb.c`** walk_bb_flat IR_ASSIGN local arm: `op_sb=bb_varslot(sval)`, `op_off=bb_slot_alloc16(nd)`.
- **`emit_core.c`** IR_ASSIGN: descr-flat-chain locals → `bb_assign_local` (one line, after the NV-global route).
- **`scrip.c`** precise wave-1 gating (hardened twice in-rung; see lesson).
- Makefile: src list + compile rule.

The read side needed NOTHING: `bb_var`'s descr-flat-chain varslot arm + the IR_VAR dispatch
(`bb_varslot_peek`→op_sa) already existed; assigns now create the varslots they read.

## THE TRANSFERABLE LESSON (load-bearing for every future gate widening)
The first gate draft (safe KIND set only, the bb_alt discipline) flipped **11 m4 programs EXCISED→FAIL** —
ALL carriers of the flagged **TT_AUGOP/swap lowerer misroute**: `x +:= 5` lowers as bare `v_det_call("x")`
IR_CALLs, which sit inside ANY naive kind set. m3 was shielded only by `for_run=1`'s builtin-call excise;
m4 (`for_run=0`) admits them. **Fix: IR_CALL inside an assign-containing graph is admissible only as
write/writes BY NAME.** Any widening of this gate must keep the by-name lens until the AUGOP desugar rung
lands. Second hardening: every local IR_VAR read must be assigned-or-param in its graph — retires the
latent `op_off=-1` runtime bomb as a loud EXCISE (a slice of the known ~150-abort permissiveness).

## Discovery worth knowing
`walk_bb_node`'s prologue ALREADY auto-deposits `op_a_slot = bb_slot_get(nd->α)` and `op_a_node_kind` —
consumer boxes get their α-operand's slot for free; driver arms only need op_sb/op_off-class extras.

## Gates at `cf204ed` (all green)
Probes `x:=42;write(x)` / `s:="hi"` / `y:=x` / reassign all **m2==m3==m4**; negatives (binop rhs,
unassigned read, the 11 misroute programs) EXCISE rc=0. Corpus **ALL THREE columns byte-identical in
EVERY bucket** via full stash/rebuild/set-diff: m2 **129 HARD** / m3 18+147E / m4 25+86E (zero drift —
no corpus program carries the pure wave-1 shape; probes carry the rung, the SCAN-3 precedent).
Smoke Icon 12/12 HARD · m3 5/12 · m4 5/12 · Prolog 5/5 · broker 32. bb_bin_t 0 · handencoded `--strict` 0 ·
icn_no_stack 0 · one-reg-frame 0 · scan fence PASS (28/28) · prove_lower2 PASS · FACT 0 ·
medium-invisible 343 unchanged (all documented Prolog-lane bb_builtin_*).

## NEXT (in leverage order — see ICN-VAR LADDER in GOAL-ICON-BB.md)
1. **ICN-VAR-2** — binop/relop var operands (`x:=x+1`, `x>5` reading varslots): operand-slot reads in the
   binop arith/relop boxes; raw-int64 binop slots need the DT_I retag arm (`bb_gvar_assign` IR_BINOP
   precedent). Direct unblock for the **if_expr/while/until/repeat smoke cluster** (8 kinds, zero native
   shapes). The old "bb_var bombs (no ζ-slot)" diagnosis is SUPERSEDED — the slot substrate exists now.
2. **ICN-VAR-3** — SCAN-13b adoption: GEN_SCAN slot-adoption piece (written up in its ladder entry) +
   var-subject scans (`s ? …`, hence every desugared `?:=`).
3. **TT_AUGOP desugar rung** (Rebus precedent) — doubly motivated: it is what the gate had to fence around.

Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.8
