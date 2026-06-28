# HANDOFF — 2026-06-28 — Claude Sonnet 4.6 → Next Session
## GOAL: GOAL-IR-IMMUTABLE-EMIT  (JCON wholesale Icon emitter rewrite)

---

## PUSHED STATE

**SCRIP:** `ea09c10c` on `main` (origin confirmed)
**`.github`:** `742b0775` on `main` (origin confirmed)
**Gate:** `A op-writes=29  B field-writes=9  → HARD TOTAL = 38`  (target 0)
**Icon suite:** `PASS=213  FAIL=40  XFAIL=36  TOTAL=289`  (green baseline)
**SNOBOL4 mode-3 smoke:** 7/7
**Credential used this session:** revoke `REDACTED_REVOKE_BEFORE_REUSE` — it appeared in transcript.

---

## WHAT HAPPENED THIS SESSION (chronological)

### 1. Green-restore  (`f23ff36f`)
Inherited tree was Icon 187 (suite-RED) from the half-landed B1 value band (`18bb0eda`).
Restored `emit_bb.c` to its pre-band parent; KEPT the B0 keystone substrate intact:
- `IR_t.lhs` field + `nvalue_slots` field on `IR_graph_t`
- `ir_tmp_slot_assign_flat` in `scrip_ir.c`
- Driver wiring in `scrip.c` (both `--run` and `--compile` paths)

The pass is inert-but-landed: slots are pre-assigned by LOWER but the emitter still
ignores `nd->lhs` and uses the old `bb_slot_alloc16` walk-order path.

**Diagnosis confirmed:** B1 broke because it overlaid a reserved `[0, nvalue*16)` value
band on the SAME walk-order cursor feeding scratch/varslots, across 3 emit entries with
2 frame-base conventions (0/16). This is why piecemeal partial conversion fails.
The only correct path is moving ALL slot allocation into LOWER (fresh parallel driver).

### 2. Capture phase stops mutating IR  (`84b3d995`) — gate 42→40

`flat_drive_capture` drove the same MATCH_ASSIGN node twice (SAVE pass, COMMIT pass)
by writing a phase onto the IR node: `IR_LIT(pBB).ival = 0/1/2`.
`walk_bb_node` copies `IR_LIT(nd).ival → g_emit.op_ival` unconditionally.
`bb_match_capture` read `_.op_ival` for the SAVE/COND/IMM split.

Fix: new `sm_emit_t` field `op_phase`; driver sets it; template reads it.
`.s` byte-identical: capgood.sno + beauty.sno (RULES.md file). field-writes 11→9.

### 3. Binop dispatch stops swapping `->op`  (`ea09c10c`) — gate 40→38

`flat_drive_binop_tree` had two swap sites:
`_sk = pBB->op; pBB->op = binop_slot_kind(pBB); EMIT_PAIR_FILL(...); pBB->op = _sk;`
The kind (ARITH/RELOP/CONCAT) rode in the node's op field as a temp.

Fix: new `sm_emit_t` field `op_binop_kind`; driver sets it from `binop_slot_kind()`;
new `walk_bb_node case IR_BINOP:` dispatches on it to the variant templates.
Existing specific-op cases (`IR_BINOP_ARITH` etc.) kept — other paths still reach them.
`.s` byte-identical: add/sub/mul/relop/concat program. op-writes 31→29.

---

## THE MECHANICAL PATTERN  (every `->op` swap converts this way — memorize it)

The emitter specializes a generic op into a variant by temporarily mutating the node:
```c
IR_e _sk = nd->op;
nd->op = VARIANT_OP;
EMIT_PAIR_FILL(nd, lbl_γ, lbl_ω, lbl_β);
nd->op = _sk;
```
`walk_bb_node`'s switch then routes to the variant's template.

**Convert WITHOUT touching `nd->op`** (zero blast radius on the many `== GENERIC` checks):

**Step A:** Add a dedicated `sm_emit_t` field in `emit_globals.h` carrying the routing
decision. It survives `EMIT_PAIR_FILL` because `bb_fill_alpha` and `walk_bb_node`'s
preamble never touch new fields. It is consumed synchronously by the immediately-following
FILL (safe under nesting, like `op_off`).

**Step B:** At each swap site, set the field instead of mutating `->op`:
```c
// BEFORE:
{ IR_e _sk = pBB->op; pBB->op = binop_slot_kind(pBB); EMIT_PAIR_FILL(...); pBB->op = _sk; }
// AFTER:
{ g_emit.op_binop_kind = (int)binop_slot_kind(pBB); EMIT_PAIR_FILL(...); }
```

**Step C:** Add a generic `case GENERIC_OP:` in `walk_bb_node` (`emit_core.c`) that
dispatches on the field to the variant template(s). Keep existing specific-op cases.

**Step D — MANDATORY VERIFY:** Run `--compile --target=x86` on a program that exercises
the construct. `diff BASE.s NEW.s` must be **empty**. (Build at the commit before your
change, compile, stash, rebuild, compile, restore, diff.) If not empty, diagnose before
committing.

**Reference implementation:** `ea09c10c` (the binop conversion). Copy it.

---

## REMAINING `->op` SWAP SITES IN `emit_bb.c`

Gate-relevant: each site is one op-write in category A (29 remaining).

### GVAR-arith cluster — the entangled case (~11 op-writes; BIGGEST Icon cluster)
These are in `flat_drive_gvar_assign_binop` and neighbors. The base node is IR_ASSIGN
(a global-var store with a binop rhs), swapped to a binop-gvar op:

| Line (approx) | Swap target | Base node |
|---|---|---|
| 2215 | `IR_BINOP_GVAR_CONCAT` | `nd` (IR_BINOP) |
| 2236 | `IR_BINOP_GVAR_ARITH` | `pBB` |
| 3013 | `IR_BINOP_GVAR_ARITH` | `asgn` (IR_ASSIGN) |
| 3022, 3031, 3040, 3049 | `IR_BINOP_GVAR_ARITH` | `nd` |
| 3068, 3087 | `IR_BINOP_GVAR_ARITH_SLOT` | `nd` |
| 3113 | `IR_BINOP_GVAR_RELOP` | `nd` |
| 3126 | `binop_slot_kind(nd)` | `nd` |
| 3254 | `IR_UNOP_GVAR_SLOT` | `nd` |

All live in `flat_drive_gvar_assign_binop` / `flat_drive_gvar_seq_passthrough`.
The fix needs an `op_gvar_route` field (or reuse `op_binop_kind` with an offset).
The redirect goes inside `walk_bb_node`'s existing `IR_ASSIGN` handling — more
invasive than the clean binop case but the same recipe.
**Verify with:** `g := 5; write(g + 1)` (global-var arith) and `g := "a"; write(g || "b")`.

### SNOBOL4 match retags — deprioritized (other-language moratorium)
```
2471: pBB->op = IR_MATCH_HEAD    (save/restore _sk, clean swap)
2476: pBB->op = IR_MATCH_RETRY   (clean swap)
2499: pBB->op = IR_MATCH_ADVANCE (clean swap)
2547: pBB->op = IR_ASSIGN_DESCR  (clean swap)
```
Trivially clean but SNOBOL4 is on hold until Icon is done.

### Permanent / classify-time retags — different disease
```
3259: IR_PROC_GEN → IR_CALL_PROC_STAGED (no restore)
3674: nd->op = IR_PROC_GEN / IR_CALL_PROC_STAGED / IR_CALL_BUILTIN / IR_CALL_GVAR_USERPROC
3688: same family
2243/2248: c0->op = IR_LIT_I (save/restore, for gvar scalar coerce)
```
These are a pre-emit runtime-query classification pass that permanently retags call nodes.
Faithful fix: move the classification into LOWER (or a pre-emit resolve pass writing into
a side-table / enum field in IR_t). Touching these without understanding the full call
resolution chain is high-risk; leave for after the GVAR cluster.

---

## REMAINING F4 FIELD-WRITE SITES (9 in category B)

Category B = `IR_LIT`/`IR_EXEC` field writes.

| Line | Site | What it does | Fix approach |
|---|---|---|---|
| 1732 | `flat_drive_case` | `IR_LIT(arm).ival = 1` on a case arm | `op_case_phase` field |
| 1750 | `flat_drive_case` | `IR_LIT(arm).ival = 0` | same |
| 1762 | `flat_drive_case` | `IR_LIT(arm).ival = 1` | same |
| 1797 | `flat_drive_limit` | `IR_LIT(pBB).ival = (int64_t)IR_LIT(cnt).ival` | ride in `op_ival` pre-set |
| 2244 | `flat_drive_gvar_assign_binop` | `c0->op = IR_LIT_I; c0->ival = val` (save/restore) | pure gvar coerce; carry in `op_sa`/`op_sb` from LOWER |
| 2248 | same | restore | same |
| 2298 | `flat_drive_subject` | `IR_LIT(subj).sval = IR_LIT(pBB).sval` | `op_scan_subj_lit` field (already exists) |
| 2300 | same | `IR_LIT(subj).sval = ""` | same |
| 2303 | `flat_drive_scan_stmt` | `IR_LIT(slit).sval = subj_lit` | same |
| 715 | `flat_drive_gz_query` | `g_emit.op_ival = IR_LIT(pBB).ival` | this IS a `g_emit` set, not IR mutation — re-run gate to confirm if it's miscounted |

**Note on L715:** check with `grep -n "IR_LIT.*\.ival\s*=" src/emitter/emit_bb.c` after next gate run.
It may have been miscounted — `g_emit.op_ival = IR_LIT(pBB).ival` reads the node, doesn't write it.

---

## KEY ORIENTATION FACTS (read these before touching anything)

**Context sources this session (they were loaded; re-read if needed):**
- `JCON` `ir.icn`: 48 lines, the 30-odd `ir_Tmp`/`ir_Var`/`ir_IntLit`/… record defs → these are the SCRIP IR enum values
- `JCON` `gen_bc.icn`: 2038 lines; `bc_gen` at line 822 is the DISPATCH (≡ `walk_bb_flat` switch); each `bc_gen_ir_<X>` is one TEMPLATE (≡ one `bb_*.cpp`)
- `JCON` `irgen.icn`: 1559 lines; the `ir_a_<Construct>` procedures are the LOWER (≡ `lower_icon.c`)

**The four-label ↔ SCRIP reconciliation (still authoritative):**
- JCON `ir_info(start, resume, failure, success)` → start=**α**, resume=**β**, failure=**ω**, success=**γ**
- JCON CHUNKS (label stream) ↔ SCRIP TEMPLATES (α/β internal, γ/ω as `IR_ref_t` edge pointers)

**The templates are already clean** — `bb_binop_arith`, `bb_binop_relop` etc. read `op_sa`/`op_sb`/`op_off` from `g_emit` and emit x86; they never read `nd->lhs` and never mutate IR. The disease is 100% in `emit_bb.c` driver (the `walk_bb_flat` switch + `flat_drive_*` zoo + `bb_slot_alloc16` emit-time reconstruction + the `->op` swaps).

**The slot mechanic (B0 substrate, inert-but-landed):**
- `ir_tmp_slot_assign_flat` runs in LOWER (driver calls it for every Icon graph before emit)
- Every value-producer node (except IR_VAR) gets `nd->lhs = k * 16` (k counting from 0)
- `g->nvalue_slots` = count of value-producing nodes
- The emitter currently IGNORES `nd->lhs` (falls through to old `bb_slot_alloc16`)
- The NEXT BIG STEP: replace the `bb_slot_alloc16` calls in `walk_bb_flat` for Icon nodes with direct reads of `nd->lhs`

**IR_VAR/IR_ASSIGN in Icon:** IR_VAR is an lvalue ref (JCON `ir_Var`); its storage is by-name via `bb_varslot`. Do NOT give IR_VAR a value-band slot — confirmed correct in B0.

**`binop_slot_kind` is pure** — depends only on `IR_LIT(nd).ival` (BINOP_* constant), which LOWER sets. Safe to call at lower time.

**`walk_bb_node` preamble** (emit_core.c:357) always runs `g_emit.op_ival = IR_LIT(nd).ival` before dispatch. New emit-state fields are NOT overwritten by the preamble — safe to pre-set before FILL.

---

## THE NEXT BIG STEP (the actual wholesale slot conversion)

The three rungs this session (`op_phase`, `op_binop_kind`, GVAR-arith next) are faithful
cleanup but they don't move the slot mechanic. The JCON model's core is:

> **Every slot is assigned at LOWER time. The emitter reads slots, never computes them.**

The current path: `walk_bb_flat` / `flat_drive_binop_tree` calls `bb_slot_alloc16(nd)` to
*compute and register* the slot into the slotmap at emit time. That's the reconstruction.

The future path: `walk_bb_flat` sets `g_emit.op_off = nd->lhs` (already in `nd->lhs` from
`ir_tmp_slot_assign_flat`), sets `g_emit.op_sa = operand0->lhs`, `g_emit.op_sb = operand1->lhs`,
then calls `FILL`. The templates already consume those fields — **no template changes needed**.

The blocker: the frame layout. LOWER's `ir_tmp_slot_assign_flat` assigns `lhs = k * 16` from
zero. But the emitter's frame has varslots allocated BEFORE value slots in the proc entry
(16 reserved for proc frame, then params, then vars). To read `nd->lhs` directly, the frame
base for value slots must be known at lower time — OR the templates must add a base offset.

**Suggested approach for next session:**
1. Pick the smallest runnable program: `write(1 + 2)` → `3`
2. Add a `g_icn_value_base` global (initially 0 for expressions, 16 for procs) that the
   new emit path adds to `nd->lhs` when setting `op_off`/`op_sa`/`op_sb`
3. For just IR_LIT_I and IR_BINOP, replace the `bb_slot_alloc16` call with
   `g_emit.op_off = g_icn_value_base + nd->lhs` in the `walk_bb_flat` case arms
4. Verify `write(1+2)` still prints `3` — this is the proof the slot mechanic works
5. Then sweep IR_VAR / IR_CALL / IR_SUCCEED / IR_FAIL for the full `main()` spine

---

## FILE MAP (as of ea09c10c)

| File | Role | Op-writes | Field-writes |
|---|---|---|---|
| `src/emitter/emit_bb.c` | Driver: `walk_bb_flat` + `flat_drive_*` | 29 | 9 |
| `src/emitter/emit_core.c` | `walk_bb_node` dispatch | 0 | 0 |
| `src/emitter/emit_globals.h` | `sm_emit_t` struct | 0 | 0 |
| `src/emitter/BB_templates/*.cpp` | x86 generators | 0 | 0 |
| `src/contracts/scrip_ir.c` | `ir_tmp_slot_assign_flat` (LOWER) | 0 | 0 |
| `src/contracts/IR.h` | `IR_t.lhs`, `IR_graph_t.nvalue_slots` | 0 | 0 |
| `src/driver/scrip.c` | Driver wiring for the lower pass | 0 | 0 |

New fields added this session: `sm_emit_t.op_phase` (int), `sm_emit_t.op_binop_kind` (int).

---

## DO NOT REGRESS

- Icon `PASS=213` — all Icon-only checks must hold
- `beauty.sno` mode-4 `.s` must stay byte-identical to the pre-session baseline
  (check: `git stash; make; scrip --compile beauty.sno > BASE.s; git stash pop; make; scrip --compile beauty.sno > NEW.s; diff`)
- Gate must not go UP from 38 (every rung is gate-neutral or gate-reducing)
- SNOBOL4 / Prolog / Raku / Pascal: other-language breakage AUTHORIZED this session
  per Lon's directive; they will be rebuilt with new boxes later. Do not spend time
  debugging or protecting them.

---

## COMMIT CADENCE

One commit per verified rung. Commit message format established:
`GROUND ZERO #5 <rung>: <what changed> — <what rides where>`

Push after each session with credential (revoke the one in this doc first).

