# JCON-TO-SCRIP-IR-MAP.md — the one-to-one IR→codegen correspondence (Icon first)

**Attached to:** `GOAL-IR-IMMUTABLE-EMIT.md` (Ground Zero #5).
**Purpose:** a durable, per-instruction translation table so the JCON→SCRIP conversion is mechanical
and survivable across sessions. The last campaign re-flubbed because the correspondence lived only in
a model's head; this doc makes it ground truth. UPDATE THE STATUS COLUMN EVERY RUNG.

---

## ⛔ THE ROSETTA STONE

`refs/jcon-master/tran/gen_bc.icn` is JCON's backend: **one procedure per IR instruction,
`bc_gen_ir_<X>(s, p)`, emitting JVM bytecode.** SCRIP mirrors it as **one `bb_<x>` template emitting
x86.** JCON targets the JVM, SCRIP targets x86 — same old, same old. The dispatch (`bc_gen`, line 822)
is a `case type(p)` over the instruction set; SCRIP's analog is template dispatch on `nd->op`.

JCON's IR set is `refs/jcon-master/tran/ir.icn` (the records). Its producer is
`refs/jcon-master/tran/irgen.icn` (`ir_a_<Construct>`, 43 procedures — the LOWER side).

---

## ⛔ THE THREE TRANSLATION INVARIANTS (get these uniform → fusion is impossible)

### 1. tmp = slot. The keystone.
JCON: every value-producing record has an `lhs` field = an `ir_Tmp(name)`. `bc_gen_ir_Tmp_rval`
emits `j_Aload(bc_tmp_table[name] + offset)`; `_assign` emits `j_Astore(...)`. **A tmp is a JVM
local index.** SCRIP-native form: a tmp is a **16-byte slot at `[r12+off]`**. The faithful realization
is a result-slot id on the producer node (`IR_t.lhs`), **assigned by a LOWER pass**, read by consumers
as `off(producer)`. Operands are producer nodes (`operands[]`); a consumer reads
`operand->lhs → [r12+off]`. NOTHING is allocated at emit time. (Scratch tmps with no single producer —
JCON's `ir_a_Scan` allocates `tmp/lv/mk/oldpos/oldsubject` — become slot ids the lowerer reserves.)

  | JCON `gen_bc.icn` | SCRIP template (x86) |
  |---|---|
  | `bc_tmp_table[name] + offset` (JVM local index) | `node->lhs` → `[r12+off]` |
  | `j_Aload(slot)` (read tmp) | `mov rXX, [r12+off]` |
  | `j_Astore(slot)` (write tmp) | `mov [r12+off], rXX` |

### 2. Four labels → two internal labels + two edge refs. The port reconciliation.
JCON exposes all four ports as first-class chunk labels (`ir_info(start, resume, failure, success)`)
because its **product is a flat chunk/label stream** linked by explicit `ir_Goto`/`ir_Succeed`/`ir_Fail`.
SCRIP's **product is per-box templates**, so two ports fold inward and two stay as edges:

  | JCON port (chunk label) | SCRIP realization |
  |---|---|
  | **start**   | **α** — the template's own entry label |
  | **resume**  | **β** — the template's own resume label (the `lbl_β` arg to `walk_bb_flat`) |
  | **success** | **γ** — `IR_t.γ` edge ref (`jmp` here on produce) |
  | **failure** | **ω** — `IR_t.ω` edge ref (`jmp` here on exhaust) |

So when JCON emits `bc_transfer_to(p.ir.success)` = `j_goto_w(L)`, SCRIP emits `jmp γ`. When JCON emits
`bc_conditional_transfer_to(failLabel, cond, notcond)`, SCRIP's template emits `jCC γ` / `jNCC ω`.
`ir_Succeed`→`bb_succeed` (wire to γ + stash resume), `ir_Fail`→`bb_fail` (wire to ω). This is the
"CHUNKS vs TEMPLATES" difference Lon named: same four-port semantics, different product shape.

### 3. The ONE deliberate divergence: `ir_OpFunction` splits by arity.
JCON merges every operator into `ir_OpFunction` (arity resolved at runtime — one Java vProc dispatch).
SCRIP is a template system (one BB = one instruction = direct x86), so an arity branch inside a
template is exactly what the model exists to avoid. Therefore `bc_gen_ir_OpFunction` (line 609) splits:
**`bb_binop` (arity 2, reads `op_sa`+`op_sb`)** and **`bb_unop` (arity 1, reads `op_sa`)**. LOWER picks
which by `*argList` (arity), where language belongs. The operation (ADD/LT/CONCAT…) is an **immediate on
the node**, never opcode identity (JCON: operation is `p.fn.name`, data). `ir_operator` (the descriptor)
folds into that immediate; it is not its own template. Resumability is ω-WIRING only (B3, confirmed);
coercion is an operand-representation flag. No language `#ifdef` in any template.

---

## PER-INSTRUCTION TABLE (Icon)

Status legend: `NEW` = template to be written; `EXISTS` = SCRIP opcode/template already present (verify it
obeys invariant 1 — reads `lhs`, no emit-time alloc); `C-track` = a Track-C add (genuine feature gap);
`slot-only` = no template, it IS a slot read/write; `fold` = folds into another template/immediate.

| JCON instruction | `gen_bc.icn` | produces value? | SCRIP target | status |
|---|---|---|---|---|
| `ir_IntLit`      | 351 | yes (lhs) | `bb_int_lit`   | EXISTS (`IR_LIT_I`) — move slot to lower |
| `ir_RealLit`     | 366 | yes (lhs) | `bb_real_lit`  | EXISTS (`IR_LIT_F`) |
| `ir_StrLit`      | 381 | yes (lhs) | `bb_str_lit`   | EXISTS (`IR_LIT_S`) |
| `ir_CsetLit`     | 395 | yes (lhs) | `bb_cset_lit`  | C-track (C2) |
| `ir_Tmp`         | 155/159 | — | (slot read/write) | slot-only (the keystone substrate) |
| `ir_Move`        | 220 | yes (lhs) | `bb_move`      | NEW (currently emit-time forwarding) |
| `ir_Deref`       | 125 | yes (lhs) | `bb_deref`     | NEW |
| `ir_Assign`      | 140 | no (target,value) | `bb_assign` | EXISTS (`IR_ASSIGN`) — collapse source variants |
| `ir_Var`         | 305 | yes (lhs) / lvalue | `bb_var`  | EXISTS (`IR_VAR`) — OLD frameslot + NEW NV arms |
| `ir_Key`         | 338 | yes (lhs) | `bb_key`       | EXISTS (`IR_KEY_GEN`) |
| `ir_Field`       | 185 | yes (lhs) | `bb_field`     | EXISTS (`IR_FIELD_GET`/`_SET`) |
| `ir_OpFunction`  | 609 | yes (lhs) | `bb_binop` / `bb_unop` | EXISTS — SPLIT by arity; op = immediate |
| `ir_operator`    | 705 | — | (operation immediate) | fold into binop/unop |
| `ir_Call`        | 664 | yes (lhs) | `bb_call`      | EXISTS (`IR_CALL`) — kill emit-time `rt_*` routing (B4) |
| `ir_MakeList`    | 582 | yes (lhs) | `bb_make_list` | C-track (C3) — today a builtin call |
| `ir_ResumeValue` | 551 | yes (lhs) | `bb_resume_value` | NEW |
| `ir_Goto`        | 291 | no | `bb_goto` / γ-wiring | EXISTS (`IR_GOTO`) |
| `ir_IndirectGoto`| 298 | no | `bb_indirect_goto` | EXISTS (`IR_GOTO_DYN`) |
| `ir_Label`       | 175 | — | (chunk label placement) | slot-only |
| `ir_TmpLabel`    | 165/169 | — | (label slot read/write) | slot-only |
| `ir_MoveLabel`   | 241 | no | `bb_move_label` | NEW |
| `ir_Succeed`     | 445 | no | `bb_succeed` (γ + resume stash) | EXISTS (`IR_SUCCEED`) |
| `ir_Fail`        | 492 | no | `bb_fail` (ω)   | EXISTS (`IR_FAIL`) |
| `ir_EnterInit`   | 801 | no | `bb_enter_init` (proc entry) | NEW (currently in proc preamble) |
| `ir_ScanSwap`    | 254 | no | `bb_scan_swap`  | NEW (scan env save/restore) |
| `ir_Create`      | 717 | yes (lhs) | `bb_create`   | C-track (C1) |
| `ir_CoRet`       | 752 | no | `bb_coret`      | C-track (C1) |
| `ir_CoFail`      | 777 | no | `bb_cofail`     | C-track (C1) |
| `ir_Unreachable` | 524 | no | `bb_unreachable` (ud2/bomb) | C-track (C4) |

**Structural (not instructions — handled by the chunk walker / program builder, not a template):**
`ir_Function`, `ir_Record`, `ir_Global`, `ir_Invocable`, `ir_Link`, `ir_chunk`, `ir_coordinate`.

---

## THE LOWER TMP-SLOT PASS (B0 — the literal missing piece)

Two LOWER-time passes, run after the per-language IR graph is built, before emit:

1. **tmp-assign:** walk the graph; every value-producing node gets a result tmp-id in `nd->lhs`.
   Operands already reference producer nodes (`operands[]`), so no operand rewrite is needed — a
   consumer reads `operand->lhs`. Scratch tmps (no single producer) get reserved ids the lowerer holds.
2. **slot-assign:** map each tmp-id → a 16-byte frame offset `off = id*16`; set `graph->nslots`.
   (Mirrors today's `g_flat_slot_count += 16` convention, but computed in LOWER, not emit.)

After these, the emitter reads `off(nd) = nd->lhs` directly. `bb_slot_alloc16`/`bb_slot_get` at emit time
are RETIRED for the JCON path. This is what makes the emitter read-only (the gate → 0).

**⚠ B1 COLLISION CAVEAT (must solve when flipping emit to read `lhs`).** Emit today allocates TWO kinds of
slot from the same `g_flat_slot_count` cursor starting near 0: (1) value-node result slots (what the pass
covers) and (2) SCRATCH/state slots (capture, ARBNO arena, generator state) via `bb_slot_alloc16(construct)`
/ `bb_slot_claim(bytes)`. The pass numbers value slots densely from 0, so a naive "emit reads `nd->lhs` for
value nodes while still allocating scratch the old way" COLLIDES the frame. B1 must either (a) move ALL slot
allocation (incl. scratch) into LOWER (the faithful JCON end-state — JCON's tmp table includes scratch tmps),
or (b) reserve value slots in `[0..nslots*16)` and start emit scratch at `graph->nslots*16`. Option (a) is
the target. The pass currently covers value-producers only and recurses leaf-SEQ; scan sub-graph + scratch
coverage is part of B1.

STATUS 2026-06-27: passes 1+2 fused as `ir_tmp_slot_assign` (off = id*16; value-producers only; runs in the
`--dump-ir` path; emit untouched). Locked by `scripts/test_gate_ir_tmp_slots.sh`. A flat Icon variant
`ir_tmp_slot_assign_flat` (off = id*16 over value-producers excluding `IR_VAR`; sets `g->nvalue_slots`) is
wired at the Icon bb-table call sites in `scrip.c` (~2767, ~3370) — still inert (nothing reads `lhs`).

FINDING 2026-06-28 (resolves option (a) vs (b) — it is (a), and not by preference): emit-time scratch uses
`bb_slot_claim(bytes)`, which is **keyless** — it bumps `g_flat_slot_count` and returns an offset with no
node to hang it on, interleaved in emit-walk order inside `bb_call`/`bb_gather`/`bb_match_*`/`bb_mapgrep`. So
the value-node cursor at any keyed `bb_slot_alloc16(nd)` depends on how many keyless claims ran before it in
the DFS walk (`bb_emit_order_visit`: γ, ω, operands). Consequence: the live frame layout is emit-walk-order
dependent, and `nd->lhs` computed in LOWER over `g->all` order does NOT equal emit's cursor even for value
producers. Option (b) (value slots `[0..nslots*16)`, scratch after) cannot keep the suite green because the
value numbering itself diverges. The faithful path is option (a): **every temporary — value, scratch, var —
becomes a LOWER-assigned slot in `nd->lhs`; keyless emit scratch is abolished** (JCON has no emit-time
allocation; its tmp table already includes scratch tmps). This forces a frame renumber, so the break is
structural, exactly as the campaign assumes — not an incidental regression to be tiptoed around.

---

## BUILD ORDER (one IR at a time; assemble when enough land)

Strategy: build the JCON-mirrored Icon path **NEW, beside the old fused path** (`emit_jcon`), and keep the old
path as a live oracle until the new path fully subsumes Icon, then delete it. Routing is per-proc, but note no
real Icon proc is pure-early-cluster (every program calls `write` → needs `Call`+ports, cluster 6/2), so the
**per-rung check is per-template `.s` equivalence on a crafted program** (the ea09c10c ethos: `--compile
--target=x86`, BASE-vs-NEW diff == 0 for code exercising exactly that template). The **Icon suite is the FINAL
gate**, applied at the whole-path flip — not a per-rung signal. Gate strict-0 + Icon green are the recovery
target; breaking mid-ladder is authorized.

- **Cluster 1 — slot spine, zero ports:** `IntLit/StrLit/RealLit → Tmp(slot) → Move/Assign/Deref → Goto`.
  Proves tmp-slots end to end with no four-port complexity. First runnable target builds toward
  `x := 2; write(x)` (note: that also needs `Call` + `Succeed`/`Fail` + `EnterInit` — cluster 2 deps).
  Exact current→new correspondence (reconnoitred 2026-06-28):
  - **Lit:** today `IR_LIT_I/S/F/NUL → bb_lit_scalar()` (already unified across kinds via `g_emit` fields).
    New `bb_jcon_lit` is the same x86 but takes its result slot from `nd->lhs`, not `bb_slot_alloc16_or_get`.
  - **Assign → collapse:** today a sprawl — `IR_ASSIGN`, `IR_ASSIGN_LIT_S/I`, `IR_ASSIGN_VAR/CONCAT/CALL/DESCR`,
    `IR_INDIRECT_ASSIGN_LIT_S/VAR`, `IR_ASSIGN_FRAME/_REF` → `bb_gvar_assign*` / `bb_assign_frame*` /
    `bb_assign_local`. JCON has ONE `ir_Move`. Collapse to a single `bb_jcon_move(dst_tmp, src_tmp)`; the
    source-kind specializations vanish because the source is ALWAYS already a tmp (its producer wrote its slot).
  - **Move/Deref → introduce:** no `IR_MOVE`/`IR_DEREF` opcodes exist; today they are implicit in the assign
    family + `bb_prepare`. LOWER must emit them explicitly (JCON does). `bb_jcon_deref` = load through a var
    cell into a result tmp; store side handled by `bb_jcon_move`.
  - **Goto:** today structural (γ/ω fallthrough/jump in the walk driver, no node). JCON `ir_Goto` is explicit;
    `bb_jcon_goto` emits the unconditional jump from the γ edge.
  - **Slot accessor:** `bb_slot_get/alloc16(nd)` → `bb_jcon_slot(nd){ return nd->lhs; }` (pure read, no mutate).
  - LOWER work: extend `ir_tmp_slot_assign_flat` → `ir_jcon_slot_assign` covering ALL temporaries on one base
    (value + the introduced move/deref tmps + the var region currently served by `bb_varslot(name)`).
- **Cluster 2 — ports:** `Succeed/Fail/ResumeValue`, `EnterInit`, `Label/TmpLabel`. Closes the minimal
  runnable program.
- **Cluster 3 — operators:** `OpFunction` → split `bb_binop`/`bb_unop`; `operator` immediate.
- **Cluster 4 — storage refs:** `Var/Key/Field` (both NV and frameslot arms).
- **Cluster 5 — control/indirect:** `MoveLabel/IndirectGoto/ScanSwap`.
- **Cluster 6 — structure/co-expr (Track C):** `Call` final-form, `MakeList/Create/CoRet/CoFail/Unreachable`.

---

## Watermark
Created 2026-06-27 (Lon directing the JCON-in-SCRIP wholesale conversion; Icon first, other languages
to follow as separate sessions). Foundation landed 2026-06-27: `IR_TMP` enum slot + `IR_t.lhs`
result-slot field (additive, inert).

2026-06-28 — Cluster-1 reconnaissance complete; architecture locked. Mapped the SCRIP side to be rewritten
against the JCON Rosetta: LOWER (`lower_icon.c`, 546 lines, already γ/ω/res chunk-threaded ≈ `irgen.icn`
shape), the tmp-slot passes (`scrip_ir.c` 338/345) + their Icon call sites (`scrip.c` 2767/3370), the emit
driver + slot accessors (`emit_core.c:342 walk_bb_node`; `emit_bb.c:55-83 bb_slot_alloc16/_or_get/get`,
keyless `bb_slot_claim`, name-keyed `bb_varslot`), and the Cluster-1 dispatch (`emit_core.c:420-470`). Key
result: the keyless-scratch finding (see FINDING 2026-06-28 above) proves the frame renumber is structural →
option (a) only; and per-rung verification is per-template `.s` equivalence, suite is the final gate. Exact
Cluster-1 current→new inventory recorded in BUILD ORDER above. No code changed this rung (doc/spec only;
Icon suite remains green at 213; gate HARD unchanged at 38).

NEXT RUNG (Cluster 1, executable from the inventory above, in order):
1. LOWER: write `ir_jcon_slot_assign(g)` assigning `nd->lhs` for ALL temporaries on one base — value
   producers + the introduced `IR_MOVE`/`IR_DEREF` result tmps + the var region (port `bb_varslot`'s
   name→off map into LOWER). Keep `ir_tmp_slot_assign_flat` until the new path subsumes it.
2. LOWER: have `lower_icon.c` emit explicit `IR_MOVE`/`IR_DEREF`/`IR_GOTO` for the spine instead of the
   implicit assign-family forms (add the opcodes to `IR.h` if absent).
3. EMITTER: new `emit_jcon` unit — `bb_jcon_slot(nd){return nd->lhs;}`, then `bb_jcon_lit`, `bb_jcon_move`
   (collapsing the assign sprawl), `bb_jcon_deref`, `bb_jcon_goto`, each reading slots via `bb_jcon_slot`.
4. VERIFY each template: `./scrip --compile --target=x86` on a crafted spine program; diff BASE-vs-NEW `.s`
   == 0. Do NOT run full regression; do NOT regen artifacts.
5. Update the PER-INSTRUCTION TABLE STATUS column and this watermark each template. Commit per RULES.md.
   Push only when Lon provides the credential, then `bash scripts/handoff_status.sh` must print HANDOFF
   COMPLETE (a handoff is not done until push succeeds).

2026-06-28 (cont.) — Cluster-1 step 1 partially landed; emit-side bug localized. Recovered uncommitted
lost-session work. LOWER `ir_jcon_slot_assign` (literal reserved-region slotting `[16,16+k*16)` via
`jcon_converted_producer` = lit kinds only; sets `g->jcon_value_region`) committed SCRIP **d68c695b** —
additive, inert, Icon `--run` **213** (baseline preserved). The emit-side change that makes literals READ
the reserved slot (`jcon_lit_slot` + cursor-base shift to `16+jcon_value_region` in
`descr_flat_chain_build_proc`/`_text` at emit_bb.c ~3736/3754) **regressed −40 (213→173)** and is REVERTED.
Bisection: LOWER pass alone = 213 ⇒ the literal `lhs` overwrite is read by nothing (truly inert); the entire
regression is inside emit_bb.c. Gating `jcon_lit_slot` on `g_descr_flat_chain` did NOT restore 213 ⇒ root
cause is NOT merely the other uncompensated builder bases (gvar 3986/4014 use `nslots`; 4066/4082=`16`;
3704/3720/4099=`0`). Strongest remaining suspects: (i) the base shift reads `entry->own->jcon_value_region`
but literal `lhs` is numbered per-graph — mismatch if a literal is emitted in a different proc's frame
(inlining/cross-graph), or `entry->own` ≠ the graph the pass ran on; (ii) `jcon_value_region` counts ALL
literals in `g->all`, but the descr path only slots literals it WALKS — if counts differ the reserved region
and the base shift disagree. NEXT RUNG: re-introduce emit_bb.c in two isolated pieces — (A) `jcon_lit_slot`
in the 4 `walk_bb_flat` literal cases, (B) the base shift — testing each alone on the descr path to pin the
culprit; verify `entry->own` identity and walked-vs-counted literal parity; land literals reading LOWER slots
at 213; only then extend the converted-producer frontier and compensate the remaining builder bases.
