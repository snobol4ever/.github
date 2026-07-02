# JCON-TO-SCRIP-IR-MAP.md — the one-to-one IR→codegen correspondence (Icon first)

**Attached to:** `GOAL-IR-IMMUTABLE-EMIT.md` (Ground Zero #5).
**Purpose:** a durable, per-instruction translation table so the JCON→SCRIP conversion is mechanical
and survivable across sessions. The last campaign re-flubbed because the correspondence lived only in
a model's head; this doc makes it ground truth. STATUS column SUPERSEDED (2026-07-01): `SCRIP/scripts/audit_jcon_wholesale.sh` (66 probes, icont-oracle 4-way) is the per-construct ground truth. Naming: JCON's `lhs` was realized as **`IR_t.tmp`** (no `IR_TMP` opcode) — read `lhs` below as `tmp`; see GOAL-IR-IMMUTABLE-EMIT.md STANDING DIRECTIVE.

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
| `ir_RealLit`     | 366 | yes (lhs) | `bb_real_lit`  | EXISTS (`IR_LIT_F`) — ✅ JCON-driver converted (`e44e2359`, reads `nd->lhs`) |
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

**SCRIP-specific scalar keyword note:** SCRIP has a separate `IR_KEYWORD` node for SCALAR keyword-literals
(`&ucase`, `&digits`, `&letters`) — distinct from `ir_Key`/`IR_KEY_GEN` (the GENERATOR keyword form like
`&fail`/`&pos`). `IR_KEYWORD` is ✅ JCON-driver converted (`be7d8c8f`): emit reads `nd->lhs`, and it was added
to LOWER `jcon_converted_producer` so the slot comes from LOWER. `IR_KEY_GEN` (the generator form) is still
on the fallback path.

---

## (superseded planning deleted 2026-07-01)
The B0/B1 tmp-slot-pass design, BUILD ORDER clusters, and the 2026-06-28 dead-end/rung-reorder watermark saga are DELETED (git has them) — the campaign landed differently and is tracked in GOAL-IR-IMMUTABLE-EMIT.md (IR_t.tmp doctrine, `drive_value_slot`, the wholesale audit). This file's live value is the ROSETTA STONE + THREE INVARIANTS + the per-instruction table above.
