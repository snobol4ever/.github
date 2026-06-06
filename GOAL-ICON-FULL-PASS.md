# GOAL-ICON-FULL-PASS.md — Icon: 247/247 non-xfail PASS in modes 2, 3, and 4

**Status baseline (2026-06-06-i):** m2 181/247 · m3 31/247 · m4 34/247. Target: 247/247 all modes.
**XFAIL pool (36):** not in scope — those are known-unimplemented tiers with explicit xfail markers.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 count must never decrease; m3/m4 must PASS or EXCISE, never silent FAIL.

---

## Failure taxonomy (baseline audit 2026-06-06-h)

### A. LOWER UNHANDLED — m2 ABORTS (rc=134, `[lower2] UNHANDLED role=0 kind=N`)
These abort before any IR is built. Fix = add a lowerer case in `src/lower/lower.c` (Icon arm).
Consult JCON `refs/jcon-master/tran/irgen.icn` for port topology before every lowerer case.

| kind | TT name | Icon construct | Rungs affected |
|------|---------|----------------|---------------|
| 46 | TT_IDX | `a[i]` subscript (string/list/table/record) | 13, 16, 20 |
| 53 | TT_LIMIT | `expr \ n` limitation | 14 |
| 56 | TT_MAKELIST | `[1,2,3]` list constructor | 22, 31, 35 |
| 77 | TT_CSET_DIFF | `cs1 -- cs2` cset difference | 37 |
| 97 | TT_CASE | `case expr of {arm: expr; ...}` | 33 |
| 105 | TT_SECTION | `s[i:j]`, `s[i+:n]` string section | 20 |
| 109 | TT_FIELD | `rec.field` record field access | 24 |
| 113 | TT_INITIAL | `initial` clause in procedure | 21, 25 |
| 114 | TT_REVASSIGN | `x :=: y` reversible swap | 15, 37 |

### B. M2 OUTPUT MISMATCH — interpreter runs but wrong result
Fix = IR_interp.c / runtime semantics.

| Symptom | Construct | Rungs |
|---------|-----------|-------|
| `find()` returns only first match (not generative) | find() generator mode | 08 |
| `x :=: y` result order wrong | swap return value | 15 |
| `2^10` → `1024` not `1024.0` | pow result type (int^int → real) | 19, 26 |
| alt cross-arg partial (only first combination) | alt with proc call side-effects | 13 |
| coerce() fails (integer("3") etc) | string→int/real coercion builtins | 36, 37 |
| `type()` returns wrong type name | &type keyword / type() builtin | 37 |
| `&lcase`/`&ucase` keyword values | keyword cset values | 37 |
| `&pos` lhs/rhs swap incorrect | &pos in swap lhs/rhs | 37 |
| scan resumable across alt not completing | scan-in-alt generator | 37 |
| str relop `ac=='ca'` missing | lexicographic relop remaining cases | 37 |
| mutual recursion crashes | mutual proc forward refs | 37 |
| `integer(x)` coercion | integer() / real() builtins | 37 |

### C. M3/M4 NATIVE ONLY FAILURES (m2 passes, native wrong/empty/abort)
Fix = emitter template or emit_bb.c driver.

| Symptom | IR shape | Rungs |
|---------|----------|-------|
| Empty output (rc=0, no lines) for nested `to*to` | IR_BINOP with gen operands (Fig-1) | 01, 02 |
| Abort `unresolved forward ref xchain0_n7_β` | IR_TO_BY with by=N (non-unit step) | 01 |
| `; [walk_bb_node: kind=7 unhandled]` in .s output | IR_SCAN (kind=7) in walk_bb_node switch | 07, 12 |
| `yes` instead of `no` for `\(failing_expr)` | IR_NULL_TEST/NONNULL logic inversion | 34 |
| Nested relfilter returns 0 results | IR_BINOP relop with gen operand | 02 |
| Timeout (rc=124, infinite loop) for mult-gen | IR_BINOP_GEN path | 01, 02 |

---

## Rung plan — ordered by prerequisite depth

Each step targets a specific failure class. After each step: run the full suite, confirm m2 count did not regress, m3/m4 count rose or held.

### PHASE 1 — Lower unhandled (m2 aborts → m2 passes; unlocks large rung blocks)

**ICN-FULL-1: TT_INITIAL** (rungs 21, 25 — global+initial blocks)
- Add `case TT_INITIAL:` arm to `lower.c` Icon path.
- Semantics: `initial` clause runs exactly once on first procedure entry; subsequent calls skip it.
- JCON ref: `ir_a_Initial` / `ir_a_Global` in irgen.icn.
- Runtime: `rt_initial_mark(name)` / `rt_initial_done(name)` — check if these exist in runtime; add if not.
- IR shape: `IR_INITIAL { body_α }` — α=body subtree, γ=skip-if-done label, ω=normal-fail.
- Gate: rung21+rung25 m2 PASS. m2 count ≥ 143.

**ICN-FULL-2: TT_LIMIT** (rung 14 — `expr \ n`)
- Add `case TT_LIMIT:` arm to `lower.c` Icon path.
- JCON ref: `ir_a_Limitation` — evaluates limit expr first (one-shot), then drives body expr; counts successes and cuts at N.
- IR shape: `IR_LIMIT { count_α, body_β }` — counter in frame slot; on each body γ decrement counter; ω when counter=0.
- Consult existing `IR_LIMIT` handling in `IR_interp.c` for the m2 executor behavior.
- Gate: rung14 m2 PASS (5 subtests). m2 count ≥ 143+5.

**ICN-FULL-3: TT_MAKELIST** (rungs 22, 31, 35 — list constructors `[...]`)
- Add `case TT_MAKELIST:` arm to `lower.c` Icon path.
- Semantics: `[e1, e2, e3]` creates a list; each element expression evaluated left-to-right.
- IR shape: `IR_MAKELIST { elem0_α, elem1_β, ... }` — call `rt_list_make(n)` then `rt_list_put(L, vi)` for each.
- Runtime: verify `rt_list_make` / `rt_list_put` / `rt_list_get` / `rt_list_pull` / `rt_list_push` exist.
- Gate: rung22 m2 PASS. m2 count rises. rung31 depends on sort (FULL-9); rung35 depends on tables (FULL-6).

**ICN-FULL-4: TT_IDX / TT_SECTION** (rungs 13, 16, 20 — `a[i]`, `s[i:j]`)
- Add `case TT_IDX:` and `case TT_SECTION:` / `case TT_SECTION_PLUS:` / `case TT_SECTION_MINUS:` arms.
- TT_IDX semantics: if target is string → `rt_string_subscript(s, i)` (1-based, negative from end); if list → `rt_list_subscript(L, i)`; if table → `rt_table_subscript(T, key)`.
- TT_SECTION: `s[i:j]` → `rt_string_section(s, i, j)`.
- These are l-value capable (assignable) in Icon — lower to IR_IDX with assign support.
- JCON ref: `ir_a_Sectionop` / `ir_a_Subscript` in irgen.icn. Icon runtime: `oref.r`.
- Gate: rung16 m2 PASS (subscript). rung20 m2 PASS (section). m2 count rises.

**ICN-FULL-5: TT_CASE** (rung 33 — `case expr of { arm: body; default: body }`)
- Add `case TT_CASE:` arm to `lower.c` Icon path.
- Semantics: evaluate control expr once; compare == to each arm key (string or value equality); execute first matching arm body; `default:` if none match.
- JCON ref: `ir_a_Case` in irgen.icn.
- IR shape: `IR_CASE { ctrl_α, [arm_key, arm_body]* }` — chain of equality tests.
- Gate: rung33 m2 PASS (5 subtests). m2 count rises.

**ICN-FULL-6: TT_IDX for tables** (rungs 23, 35 — `t[key]`, `t[key] := val`)
- Extends FULL-4 to cover table subscript specifically.
- Runtime: `rt_table_new(default)`, `rt_table_get(T, key)`, `rt_table_set(T, key, val)`, `rt_table_delete(T, key)`, `rt_table_member(T, key)`, `rt_table_key(T)`.
- Also `rt_table_to_list(T)` for conversion.
- Gate: rung23 m2 PASS (5 subtests). rung35 partial.

**ICN-FULL-7: TT_FIELD / TT_RECORD_DECL** (rung 24 — records)
- Add `case TT_RECORD_DECL:` (declare record type) and `case TT_FIELD:` (field access `rec.field`).
- Semantics: `record point(x,y)` declares a type; `point(3,4)` creates instance; `p.x` accesses field 0.
- Runtime: `rt_record_new(type_name, nfields)`, `rt_record_get(r, i)`, `rt_record_set(r, i, val)`, `rt_record_type(r)`.
- Gate: rung24 m2 PASS (5 subtests).

**ICN-FULL-8: TT_CSET_DIFF + remaining cset ops** (rung 37 cset subset)
- Add `case TT_CSET_DIFF:` / `TT_CSET_UNION:` / `TT_CSET_INTER:` / `TT_CSET_COMPL:` arms.
- Runtime: `rt_cset_diff(cs1, cs2)`, `rt_cset_union`, `rt_cset_inter`, `rt_cset_compl`.
- Gate: rung37_cset_ops m2 PASS.

**ICN-FULL-9: TT_REVASSIGN** (rungs 15, 37 — `x :=: y`)
- Add `case TT_REVASSIGN:` arm to `lower.c` Icon path.
- Semantics: swap values of x and y; succeeds; on backtrack restores both.
- IR shape: `IR_REVASSIGN { lhs_α, rhs_β }` — saves both, sets lhs←rhs_val, rhs←lhs_val, on β restores.
- Gate: rung15 m2 PASS (2 subtests), rung37_swap subset.

---

### PHASE 2 — M2 runtime semantics fixes (interpreter correctness)

**ICN-FULL-10: find() generative mode** (rung 08 — `find(s1,s2)` as generator)
- `find()` must be generative: resume finds next occurrence.
- Consult Icon runtime `refs/icon-master/src/runtime/fstranl.r` — `find` is already generative in canonical Icon.
- Fix: in `IR_interp.c` / `by_name_dispatch.c`, ensure `find` re-enters with cursor advanced.
- Gate: rung08 m2 PASS (3 subtests: find, find_gen, remaining).

**ICN-FULL-11: pow() result type** (rungs 19, 26 — `2^10 = 1024.0`)
- In Icon, `^` always returns a real. Fix `rt_pow` / arithmetic to coerce to real.
- Consult Icon runtime `refs/icon-master/src/runtime/oarith.r`.
- Gate: rung19 m2 PASS, rung26 m2 PASS.

**ICN-FULL-12: coerce() / integer() / real()** (rungs 36, 37 coerce subset)
- `integer(x)` converts string/real to integer; `real(x)` converts to real.
- Verify `rt_integer_fn` / `rt_real_fn` exist and handle all cases (string→int, real→int, etc.).
- Gate: rung36_jcon_coerce m2 PASS, rung37_coerce m2 PASS.

**ICN-FULL-13: keywords (&type, &lcase, &ucase, &pos lhs/rhs)** (rung 37 keyword subset)
- `&type` returns the type name of a value; `&lcase`/`&ucase` are cset constants.
- Fix keyword dispatch in `keywords.c` / `by_name_dispatch.c`.
- `&pos` as lhs/rhs of swap: fix reversible assignment with keyword lvalue.
- Gate: rung37_keywords, rung37_neg_pos m2 PASS.

**ICN-FULL-14: scan resumable across alt / scan-alt** (rung 37 scan_alt subset)
- `s ? (expr1 | expr2)` must resume scanning from each alt arm independently.
- Fix: scan stmt frame save/restore on alt retry.
- Gate: rung37_scan_alt m2 PASS.

**ICN-FULL-15: str relop remaining** (rung 37 str_relop subset)
- `s1 == s2` lexicographic with `ac == ca` case and others.
- Verify `rt_str_eq` / `rt_str_compare` cover all relop operators exhaustively.
- Gate: rung37_str_relop m2 PASS.

**ICN-FULL-16: mutual recursion** (rung 37 mutual subset)
- Forward proc references: proc A calls proc B which calls proc A.
- Fix: ensure `rt_call_named_proc` resolves lazily (already should — verify).
- Gate: rung37_mutual m2 PASS.

**ICN-FULL-17: sort()** (rung 31 — `sort(L)`)
- `sort(L)` returns new sorted list; `sort(T,i)` sorts table.
- Runtime: `rt_list_sort(L)` / `rt_table_sort(T, by)`.
- Gate: rung31 m2 PASS (5 subtests).

**ICN-FULL-18: alt with proc-call side-effects cross-arg** (rung 13 alt_alt_cross_arg)
- `every f(1|2) | g(3|4)` — alt of calls with generator args, all combinations.
- Verify `IR_ALT` wiring in lowerer handles bounded/unbounded correctly per JCON `ir_a_Alt`.
- Gate: rung13_alt_alt_cross_arg m2 PASS.

---

### PHASE 3 — Native emitter fixes (m3/m4)

**ICN-FULL-19: IR_SCAN in walk_bb_node** (rungs 07, 12 — `s ? expr` scan stmt native)
- `walk_bb_node` switch in `emit_bb.c` has no `case IR_SCAN:` → emits `; [walk_bb_node: kind=7 unhandled]` comment into .s output.
- Fix: add `case IR_SCAN:` to the walk_bb_node dispatch (mirrors `flat_drive_scan_stmt` which already exists).
- After fix: FILL/flat_drive the scan stmt node; verify TEXT output assembles cleanly.
- Gate: rung07 m3 PASS, rung12 m3 PASS.

**ICN-FULL-20: IR_TO_BY native step fix** (rung 01 to_by abort)
- Abort: `unresolved forward reference xchain0_n7_β` — the β port of the TO_BY node is never defined.
- Root cause: `bb_to_str` checks `_.op_ival` for the step, but for IR_TO_BY the step comes from the `α` operand (a LIT_I node in the flat chain), not from the node's own `ival`. `op_ival` = node->ival = 0 so `by=0` → early return (by ≤ 0).
- Fix in `emit_bb.c` `flat_drive_to`: for IR_TO_BY, extract step from `nd->α` operand slot (the step LIT_I's `ival`) and store in `g_emit.op_ival` before FILL.
- Gate: rung01_paper_to_by m3 PASS.

**ICN-FULL-21: IR_BINOP gen-operand (Fig-1 Proebsting)** (rungs 01, 02 nested generators)
- `(1 to 3) * (1 to 3)` — both operands of a binop are generators. Current `bb_binop_arith` only handles scalar slot operands (`g_descr_flat_chain && op_sa >= 0 && op_sb >= 0`); returns empty when operands are IR_TO generators.
- This is the open "GZ-11+ generator-operand binops (Fig-1 native m3/m4)" tier from GOAL-ICON-BB.md.
- Consult `test_icon.c` in `.github/` — the Fig-1 `5 > ((1 to 2) * (3 to 4))` target shape.
- Consult `refs/jcon-master/tran/irgen.icn` `ir_a_Binop` for port topology.
- Approach: in `flat_drive_to` / `flat_drive_binop_gen_tree`, ensure each TO operand gets its own frame slot pair and the BINOP node reads from those slots. A new `bb_binop_gen.cpp` or extension to `bb_binop_arith` to handle the gen-operand shape (op_sa=-1, op_sb=-1, both operands have their own frame slots).
- Gate: rung01_paper_compound, rung01_paper_lt, rung01_paper_nested_to, rung02 nested m3 PASS.

**ICN-FULL-22: IR_NULL_TEST / NONNULL logic** (rung 34 — `\expr` nonnull test)
- `\expr` succeeds if expr succeeds (non-null); `/expr` fails if non-null (null test).
- In m3: rung34_null_test_null_fails outputs `yes` instead of `no` — logic inverted.
- Fix: check `bb_unop.cpp` for the NONNULL / NULL_TEST arms — verify branch direction.
- Gate: rung34 m3 PASS.

**ICN-FULL-23: relop filter with gen operand** (rung 02 relfilter)
- `every write((1 to 3) > 1)` — relop with one generator operand and one scalar.
- `bb_binop_relop.cpp` handles the scalar-scalar case; needs extension for gen-operand shapes.
- Related to FULL-21 but relop flavor.
- Gate: rung02_arith_gen_relfilter, rung02_arith_gen_nested_filter m3 PASS.

---

### PHASE 4 — Native templates for new lower IR kinds

Each new IR kind added in Phase 1 needs a native template for m3/m4.
These are `x86_bomb` stubs initially (keeps build green, EXCISED in harness), then real templates.

**ICN-FULL-24: IR_LIMIT native template**
- `bb_limit.cpp` — four-port: α=count (scalar slot), β=body generator.
- On α: initialize counter from count slot. On body γ: decrement counter; if counter>0 jmp γ else jmp ω. β: jmp body's β.
- Gate: rung14 m3/m4 PASS.

**ICN-FULL-25: IR_MAKELIST native template**
- `bb_makelist.cpp` — call `rt_list_make(n)` into frame slot; emit n element stores via `rt_list_put`.
- Gate: rung22 m3/m4 PASS.

**ICN-FULL-26: IR_IDX native template (string subscript + list subscript)**
- `bb_idx.cpp` — dispatch on runtime type: string→`rt_string_subscript`, list→`rt_list_subscript`, table→`rt_table_subscript`.
- Gate: rung16 m3/m4 PASS.

**ICN-FULL-27: IR_SECTION native template**
- `bb_section.cpp` — `rt_string_section(s, i, j)`.
- Gate: rung20 m3/m4 PASS.

**ICN-FULL-28: IR_CASE native template**
- `bb_case.cpp` — emit control expr → compare chain → arm dispatch.
- Gate: rung33 m3/m4 PASS.

**ICN-FULL-29: IR_INITIAL native template**
- `bb_initial.cpp` — check-and-set flag via `rt_initial_mark(name)`: α runs body once then β skips; subsequent calls jump directly to γ.
- Gate: rung21, rung25 m3/m4 PASS.

**ICN-FULL-30: IR_REVASSIGN native template**
- `bb_revassign.cpp` — save both slots, swap values; on β restore.
- Gate: rung15 m3/m4 PASS.

**ICN-FULL-31: Table/Record/Sort runtime + native templates**
- `bb_table_ops.cpp` / `bb_record_ops.cpp` / `bb_sort.cpp` stubs → real templates.
- Depends on runtime functions from FULL-6, FULL-7, FULL-17.
- Gate: rung23, rung24, rung31 m3/m4 PASS.

---

### PHASE 5 — Remaining rung37 (jcon suite) sweep

**ICN-FULL-32: rung36 / rung37 remainder audit**
- After all above phases, run the full suite and triage remaining rung36_jcon_* and rung37_* failures.
- Each remaining failure gets its own sub-step identified by `./scrip --interp prog.icn 2>&1` output.
- Expected survivors: advanced features (co-expressions, file I/O patterns, numeric formatting edge cases).
- Gate: maximize rung36/rung37 PASS count. Document any genuine XFAIL additions with rationale.

---

## Session Setup (inherited from GOAL-ICON-BB.md)

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_prolog.sh
bash scripts/test_smoke_unified_broker.sh
bash scripts/test_gate_bb_one_box.sh
```

## Gate after every step

```bash
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_icon_rung_suite.sh
# m2 count must be >= previous run's count
# m3/m4: PASS or EXCISED only, no silent FAIL
bash scripts/test_gate_bb_one_box.sh
bash scripts/test_smoke_prolog.sh
bash scripts/test_smoke_unified_broker.sh
```

## Canonical source rule (from RULES.md)

Before implementing ANY construct: grep the canonical sources FIRST.
- Port topology: `refs/jcon-master/tran/irgen.icn` — procedure `ir_a_<Construct>`.
- Runtime semantics: `refs/icon-master/src/runtime/*.r` — `fstranl.r`, `oarith.r`, `oref.r`, `ocomp.r`.
- The m2 oracle (`IR_interp.c`) is a transcription; canonical wins when they disagree.

## Progress tracker

| Step | Rungs unlocked | M2 delta | Status |
|------|---------------|----------|--------|
| ICN-FULL-1 TT_INITIAL | 21, 25 | +5 | ✅ landed `1589bd5` (partial — BUG-6 initial-once open) |
| ICN-FULL-2 TT_LIMIT | 14 | +5 | ✅ landed `1589bd5` (partial — BUG-1 body topology open) |
| ICN-FULL-3 TT_MAKELIST | 22 (+31,35 partial) | +5 | ✅ landed `1589bd5` |
| ICN-FULL-4 TT_IDX/SECTION | 16, 20 | +8 | ✅ landed `1589bd5` (partial — BUG-4 IDX_SET open) |
| ICN-FULL-5 TT_CASE | 33 | +5 | ✅ landed `1589bd5` (BUG-2 segfault open) |
| ICN-FULL-6 TT_IDX tables | 23, 35 | +8 | ✅ landed `1589bd5` (partial — BUG-4 open) |
| ICN-FULL-7 TT_FIELD/RECORD | 24 | +5 | ✅ landed `1589bd5` (partial — BUG-4 FIELD_SET open) |
| ICN-FULL-8 TT_CSET_DIFF | 37 subset | +2 | ✅ landed `1589bd5` |
| ICN-FULL-9 TT_REVASSIGN | 15, 37 | +3 | ✅ landed `1589bd5` (BUG-3 VAR operand open) |
| **BUG-1 IR_LIMIT body topology** | 14 | fix | ✅ landed `f86427a` — ring-contamination fix (IR_ALT state=0 + LIMIT mini-loop + lim->α=bα) |
| **BUG-2 IR_CASE segfault** | 33 | fix | ☐ open — arm chain wiring NULL ptr |
| **BUG-3 IR_SWAP VAR operands** | 15 | fix | ☐ open — must use nalloc(IR_VAR) not lower2 |
| **BUG-4 IDX_SET/FIELD_SET** | 13,23,24 | fix | ☐ open — TT_ASSIGN with IDX/FIELD lhs |
| **BUG-5 pow→real** | 19,26 | fix | ☐ open — BINOP_POW must always return real |
| **BUG-6 initial once-flag** | 21,25 | fix | ☐ open — ival reset across calls |
| ICN-FULL-10 find() generative | 08 | +2 | ☐ |
| ICN-FULL-11 pow() result type | 19, 26 | +8 | ☐ (same as BUG-5) |
| ICN-FULL-12 coerce() | 36, 37 | +5 | ☐ |
| ICN-FULL-13 keywords | 37 | +3 | ☐ |
| ICN-FULL-14 scan-alt | 37 | +2 | ☐ |
| ICN-FULL-15 str relop | 37 | +1 | ☐ |
| ICN-FULL-16 mutual recursion | 37 | +1 | ☐ |
| ICN-FULL-17 sort() | 31 | +5 | ☐ |
| ICN-FULL-18 alt cross-arg | 13 | +1 | ☐ |
| ICN-FULL-19 IR_SCAN native | 07, 12 | m3+4 | ☐ |
| ICN-FULL-20 TO_BY step fix | 01 | m3+1 | ☐ |
| ICN-FULL-21 IR_BINOP gen | 01, 02 | m3+6 | ☐ |
| ICN-FULL-22 NONNULL logic | 34 | m3+1 | ☐ |
| ICN-FULL-23 relop gen | 02 | m3+2 | ☐ |
| ICN-FULL-24 IR_LIMIT native | 14 | m3/m4+5 | ☐ |
| ICN-FULL-25 IR_MAKELIST native | 22 | m3/m4+5 | ☐ |
| ICN-FULL-26 IR_IDX native | 16 | m3/m4+5 | ☐ |
| ICN-FULL-27 IR_SECTION native | 20 | m3/m4+3 | ☐ |
| ICN-FULL-28 IR_CASE native | 33 | m3/m4+5 | ☐ |
| ICN-FULL-29 IR_INITIAL native | 21, 25 | m3/m4+5 | ☐ |
| ICN-FULL-30 IR_REVASSIGN native | 15 | m3/m4+3 | ☐ |
| ICN-FULL-31 Table/Record/Sort native | 23, 24, 31 | m3/m4+15 | ☐ |
| ICN-FULL-32 rung36/37 sweep | 36, 37 | triage | ☐ |

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
