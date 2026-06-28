# HANDOFF — 2026-06-28 — Claude Sonnet 4.6 → Next Session
## GOAL: GOAL-IR-IMMUTABLE-EMIT (JCON wholesale Icon emitter rewrite)

---

## PUSHED STATE

**SCRIP:** `0e677f4c` on `main` (origin confirmed)
**`.github`:** pending push this handoff
**Gate:** `A op-writes=29  B field-writes=9  → HARD TOTAL = 38`  (target 0; unchanged across all 5 rungs)
**Icon suite:** NOT RUN (authorized — no full regression per standing directive)
**hello world:** green mode-3/4/full-cycle on every rung

---

## WHAT HAPPENED THIS SESSION (chronological)

### Strategy fix (no code)
Abandoned the band-overlay approach (prior −40 regression). Recognized the `jcon_value_slot` solution:
converted producers must read `nd->lhs` AND reserve it in the cursor
(`if nd->lhs+16 > g_flat_slot_count: g_flat_slot_count = nd->lhs+16`)
so fallback `bb_slot_alloc16` calls don't reuse the same offset. This is the bridge until LOWER assigns ALL
slots wholesale (option-a, the durable end-state).

### Rung 1 — JCON driver beachhead (`cbfcb608`)
Stood up `emit_jcon_node` (new function in `emit_bb.c`) — the direct `bc_gen` analog. Placed before
`codegen_flat_chain_body`. Routed the chunk-walker's dispatch (`walk_bb_flat(nodes[i], ...)`) through it,
default-on (`SCRIP_ICN_JCON=0` selects old path as oracle). Converted initial spine:
- `IR_LIT_S`: `jcon_value_slot(nd)` → `FILL`
- `IR_CALL`: `EMIT_PAIR_RESET + DEF_JMP + EMIT_PAIR_FILL` (no rt_* routing)
- `IR_SUCCEED`: `EMIT_PAIR_RESET + JMP(γ) + DEF_JMP(β→ω) + EMIT_PAIR_FILL`
- `IR_FAIL`: `FILL`
- `default`: `walk_bb_flat` fallback (the rotting old path)

hello world byte-identical to old path (both --run and .s), mode-4 full cycle green.

### Rung 2 — Storage spine (`be4f1b62`)
Added `jcon_value_slot` helper (the key technique). Converted:
- `IR_LIT_I`: `jcon_value_slot(nd)` → `FILL`
- `IR_VAR`: local=varslot-peek (`op_sa=voff`, `op_off=voff`), keyword=alloc+`op_sval`, global=alloc+gva_k.
  Falls back on `walk_bb_flat` for no-name/gvar-chain case.

`x:=2;write(x)` byte-identical. 4 storage variant programs byte-identical.

### Rung 3 — Arithmetic (`0603e374`)
Converted `IR_BINOP`:
- Reads operand slots: `descr_binop_opnd_slot(child0/1)` → `op_sa`/`op_sb`
- Result: `jcon_value_slot(nd)` → `op_off`
- Dispatch: `g_emit.op_binop_kind = binop_slot_kind(nd)` → `EMIT_PAIR_FILL`
  (NO `->op` swap — F1 disease avoided for the Icon path; `walk_bb_node`'s `IR_BINOP` case dispatches
  on `op_binop_kind` to the variant template, landed `ea09c10c`)
- Falls back on `walk_bb_flat` when operands have no slots yet.

`write(1+2)`, `write(2+3*4)=14`, `a:=5;b:=6;write(a+b)` correct. Structurally identical to old path
(same instruction count; offsets renumbered to LOWER scheme — not byte-identical, correct by design).

### Rung 4 — Unary (`35c97021`)
Converted `IR_UNOP`/`IR_NEG`/`IR_POS`/`IR_NONNULL`/`IR_NULL_TEST`/`IR_SIZE`/`IR_NOT`:
- `op_sa = descr_binop_opnd_slot(child0)`, `op_off = jcon_value_slot(nd)`, `FILL`
- Falls back on `walk_bb_flat` when operand has no slot.

`write(-x)`, `-x+1` (unop∘binop) correct.

### Rung 5 — Assign (`0e677f4c`)
Converted `IR_ASSIGN` (local store only; global → `walk_bb_flat`):
- `op_sb = bb_varslot(vn)` (target varslot), `op_off = jcon_value_slot(nd)`, `FILL`
- `IR_ASSIGN` has lhs=-1 today (not a value-producer in LOWER's pass), so `jcon_value_slot` falls to
  `bb_slot_alloc16`. Result: byte-identical to old path for pure-assign cases.

---

## THE `jcon_value_slot` TECHNIQUE (memorize for next session)

```c
static int jcon_value_slot(IR_t *nd) {
    int e = bb_slot_get(nd);
    if (e >= 0) return e;                         // already registered — return it
    if (nd->lhs >= 0) {                           // LOWER assigned a slot
        bb_slot_register(nd, nd->lhs);            // register it in the slotmap
        if (nd->lhs + 16 > g_flat_slot_count)    // RESERVE it in the cursor
            g_flat_slot_count = nd->lhs + 16;    // ← this is the key that beat all prior attempts
        return nd->lhs;
    }
    return bb_slot_alloc16(nd);                   // fallback: allocate fresh (old behavior)
}
```

Without the cursor-advance, the next `bb_slot_alloc16` in the fallback path reuses the same offset →
collision. The reserve makes converted (lhs-based) and unconverted (cursor-based) slots co-exist safely.

---

## THE MECHANICAL PATTERN (every IR op converts this way)

For value-producers (LIT, VAR-read, BINOP, UNOP, CALL):
```c
case IR_XXX: {
    g_emit.op_off = jcon_value_slot(nd);   // result slot (from nd->lhs or alloc)
    g_emit.op_sa  = ...;                   // operand slot (from prior producer's registered slot)
    FILL(nd, lbl_γ, lbl_ω, lbl_β);        // template dispatch
    break;
}
```

For side-effect nodes (ASSIGN, SUCCEED, FAIL):
```c
case IR_ASSIGN: {
    g_emit.op_sb  = bb_varslot(vn);        // target storage slot
    g_emit.op_off = jcon_value_slot(nd);   // result copy (for chain continuity)
    FILL(nd, lbl_γ, lbl_ω, lbl_β);
    break;
}
```

EMIT_PAIR forms (CALL, SUCCEED) use `EMIT_PAIR_RESET + DEF_JMP + EMIT_PAIR_FILL` to wire β→ω.

---

## CURRENT STATE OF `emit_jcon_node`

```
case IR_LIT_S   → jcon_value_slot + FILL
case IR_LIT_I   → jcon_value_slot + FILL
case IR_VAR     → varslot/keyword/gva dispatch + FILL (global still falls to walk_bb_flat)
case IR_BINOP   → operand slots + jcon_value_slot + op_binop_kind + EMIT_PAIR_FILL
case IR_UNOP    (+ NEG/POS/NONNULL/NULL_TEST/SIZE/NOT) → op_sa + jcon_value_slot + FILL
case IR_ASSIGN  → op_sb=varslot + jcon_value_slot + FILL (local only; global→fallback)
case IR_CALL    → write-route + EMIT_PAIR_FILL
case IR_SUCCEED → JMP(γ) + DEF_JMP(β→ω) + EMIT_PAIR_FILL
case IR_FAIL    → FILL
default         → walk_bb_flat (the rotting fallback — shrinks each rung)
```

---

## NEXT RUNGS (pick up from here)

**Rung 6 — `IR_LIT_F` / `IR_LIT_NUL`** (trivial — same pattern as `IR_LIT_I`):
```c
case IR_LIT_F:   g_emit.op_off = jcon_value_slot(nd); FILL(nd, lbl_γ, lbl_ω, lbl_β); break;
case IR_LIT_NUL: g_emit.op_off = jcon_value_slot(nd); FILL(nd, lbl_γ, lbl_ω, lbl_β); break;
```
Verify: `write(3.14)`, `x := &null; write(x)`.

**Rung 7 — `IR_KEYWORD`** (`&pos`, `&null`, `&subject`, etc.):
```c
case IR_KEYWORD:
    g_emit.op_sval = IR_LIT(nd).sval;
    g_emit.op_off  = jcon_value_slot(nd);
    FILL(nd, lbl_γ, lbl_ω, lbl_β); break;
```
Verify: `write(&pos)`.

**Rung 8 — global `IR_VAR` + `IR_ASSIGN`** (currently hits `walk_bb_flat` for global names):
Add `op_gva_k` + gva-index lookup to the `IR_VAR` global arm in `emit_jcon_node`.
For `IR_ASSIGN` global: `flat_drive_global_assign` reachable from the `IR_ASSIGN` arm.

**Rung 9 — `IR_GOTO` / `IR_IF` / `IR_CONJ`** (control flow; currently correct via fallback):
```c
case IR_GOTO: emit_jmp_label(lbl_γ, JMP_JMP); emit_jmp_label(lbl_γ, JMP_JMP); break;
```

**Rung 10 — Wholesale slot assignment (option-a):** extend `ir_jcon_slot_assign` to ALL producers
(value+var+scratch). Once every node's slot comes from LOWER, retire `bb_slot_alloc16` in the JCON path
and flip `emit_jcon_node` to pure `nd->lhs` reads. Gate → 0 follows naturally.

---

## DO NOT REGRESS

- Gate must not go UP from 38 (every rung is gate-neutral or gate-reducing)
- `write("hello world")` green mode-3/4/full-cycle every rung
- Prior rungs verified before each commit (mode-3 oracle comparison)
- No full regression, no artifact regen (standing directive, other languages authorized-broken)

---

## SESSION RULES REMINDER

- `SCRIP_ICN_JCON=0` selects old `walk_bb_flat` path (oracle)
- `SCRIP_ICN_JCON=1` (default) selects `emit_jcon_node` (new path)
- Verify each rung: `./scrip --run` old vs new, `.s` diff for structural check, full cycle if time
- One commit per rung per RULES.md; push when credential available
- `bash scripts/handoff_status.sh` must print `HANDOFF COMPLETE` before declaring done

---

**Credential used this session: revoke `REDACTED_REVOKE_BEFORE_REUSE` — it appeared in transcript.**
