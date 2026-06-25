# HANDOFF: Icon Tables (Tier C2) — COMPLETE

**Date:** 2026-06-25
**Model:** Claude Sonnet 4.6
**Commit:** 61bcc17 (SCRIP main)
**Status:** COMPLETE — m3+m4 PASS=189 (was 170), FAIL=7 (all pre-existing), zero regressions
**Baseline:** m3/m4 170/289 (HEAD f1aac7b / 54b69d4 RepAlt)

---

## What Was Done This Session

Icon table datatype (Tier C2 from ICON-BB-PUNCH-LIST-2026-06-24.md) made fully operational.
Three minimal surgical changes; no new templates, no new IR nodes, no new lowering.

### Root-cause analysis

All five rung23 table programs were EXCISED. The runtime was already complete:
- `TBBLK_t` / `table_new` / `table_get` / `table_set_descr` / `table_has` / `table_delete` in core.h/core.c
- `subscript_get` / `subscript_set` in pattern_match.c handle `DT_T` correctly
- `table` / `insert` / `delete` / `key` / `member` / `[]` all dispatch in `rt_call_arr`
- `bb_idx_set` already emits frame-slot loads `[r12+off]` for base/key/val; the
  fast-path checks `DT_A` (arrays), falls through to `subscript_set` for `DT_T`

Three blockers only:

**Blocker 1 — `rhs_kind_ok` excluded `"table"` explicitly (scrip.c:229)**
`t := table(0)` was rejected because `rhs_kind_ok` had `&& strcmp(bn,"table")` on the
known-builtin arm. Removed the strcmp exclusion.

**Blocker 2 — Gate hard-rejected `IR_IDX_SET` (scrip.c:326)**
`t[k] := v` lowers to `IR_IDX_SET`; the gate had `if (nd->op == IR_IDX_SET) return 0`
with a BENCH-F1 comment citing "LIT-operand slotting (m3) + global-list value flow
unfinished". Investigation showed the bb_idx_set template already uses frame slots
`FRQ(op_sa/sb/sc)` for base/key/val — the comment predated the frame-slot conversion.
Disabled the rejection (`if (0 && ...)`).

**Blocker 3 — `rt_size_d` had no `DT_T` branch (rt.c:~575)**
`*t` (SIZE unop) called `rt_size_d` which fell through to `VARVAL_fn(v)` → string
`"table(2)"` → `strlen` = 12. Added `if (v.v == DT_T) { r.i = v.tbl->size; return r; }`.

### Files changed

| File | Change |
|------|--------|
| `src/driver/scrip.c` | rhs_kind_ok: drop `strcmp(bn,"table")` exclusion; gate: disable IR_IDX_SET rejection |
| `src/runtime/rt/rt.c` | rt_size_d: add DT_T branch returning `tbl->size` |
| `src/emitter/BB_templates/bb_idx_set.cpp` | (RepAlt session carry-forward: frame-slot refactor) |
| `src/emitter/emit_bb.c` | (RepAlt session carry-forward: flat_drive_idx_set simplification) |

### New PASS breakdown (+19)

| Family | Rungs | Notes |
|--------|-------|-------|
| rung23 table basics | table_basic, table_default, table_insert_delete, table_member | ✅ |
| rung13 table (no-arg ctor) | table_basic, table_delete, table_subscript_assign, table_member | ✅ `table()` 0-arg path |
| rung24 records | records_record_loop | ✅ `every c.n := 1 to 3` uses IR_IDX_SET on record field |
| + prior RepAlt session | rung36_jcon_var now FAIL not EXCISED | (RepAlt carry-forward) |

### Remaining table gaps (not in scope this session)

- **rung23_table_table_key** (`every total +:= t[key(t)]`): `key(t)` is a generator builtin;
  goes through the one-shot `rt_call_arr` path, not the generator-resume path. Only first
  key is summed. Pre-existing gap — `key` needs the same generator-resume wiring as `bb_to`.
  Was EXCISED, now FAIL (correct: reveals pre-existing gap, no new code broken).
- **rung13_table_iterate** (`every v := !t do write(v)`): `!t` on a table is a generator;
  EXCISED (alt-taint gate, unrelated to tables).

---

## Suite Results

| Mode | PASS | FAIL | EXCISED | Total |
|------|------|------|---------|-------|
| m3 (--run) | **189** | 7 | 57 | 289 |
| m4 (--compile) | **189** | 7 | 57 | 289 |

FAIL=7: rung08 find-gen (rc=124) · rung13_alt_alt_cross_arg ×2 · rung23_table_key ·
rung30 builtins-seq (rc=139) · rung36_jcon_var (rc=1) · rung37_proc_lookup (rc=134).
All pre-existing; zero regressions in previously-passing tests.

Smoke: icon 12/12 m3+m4. Discipline gates: no-stack=0 · one-reg=0 · semicolon-prison PASS · LVA PASS.

---

## Open Items (unchanged from prior session)

- **suspend** rung03 ×3: DONE (d3e841b).
- **RepAlt** `|e`: DONE (54b69d4). rung36_jcon_var now FAIL (pre-existing gap in computed-call).
- **Tier A** gate widenings: record-ctor A1+A2, arm-scoped alt A3+A4.
- **Tier B**: find-gen B3 resume, cross-arg-alt B4.
- **key() generator** in `every` loop: needs generator-resume route for builtins (like bb_to).
- **!t on tables** (Bang/iterate): needs generator route.

---

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
