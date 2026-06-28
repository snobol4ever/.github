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
`--dump-ir` path; emit untouched). Locked by `scripts/test_gate_ir_tmp_slots.sh`.

---

## BUILD ORDER (one IR at a time; assemble when enough land)

Strategy: build the JCON-mirrored Icon path **NEW, beside the old fused path**, flip Icon over cluster by
cluster (gate strict-0 + Icon suite are the recovery target; breaking mid-ladder is authorized).

- **Cluster 1 — slot spine, zero ports:** `IntLit/StrLit/RealLit → Tmp(slot) → Move/Assign/Deref → Goto`.
  Proves tmp-slots end to end with no four-port complexity. First runnable target builds toward
  `x := 2; write(x)` (note: that also needs `Call` + `Succeed`/`Fail` + `EnterInit` — cluster 2 deps).
- **Cluster 2 — ports:** `Succeed/Fail/ResumeValue`, `EnterInit`, `Label/TmpLabel`. Closes the minimal
  runnable program.
- **Cluster 3 — operators:** `OpFunction` → split `bb_binop`/`bb_unop`; `operator` immediate.
- **Cluster 4 — storage refs:** `Var/Key/Field` (both NV and frameslot arms).
- **Cluster 5 — control/indirect:** `MoveLabel/IndirectGoto/ScanSwap`.
- **Cluster 6 — structure/co-expr (Track C):** `Call` final-form, `MakeList/Create/CoRet/CoFail/Unreachable`.

---

## Watermark
Created 2026-06-27 (Lon directing the JCON-in-SCRIP wholesale conversion; Icon first, other languages
to follow as separate sessions). Foundation landed this session: `IR_TMP` enum slot + `IR_t.lhs`
result-slot field (additive, inert — nothing reads `lhs` yet; gate + suites unchanged). Next rung:
Cluster 1 — the LOWER tmp-slot pass + `bb_int_lit`/`bb_assign` as the first faithful mirrors.
