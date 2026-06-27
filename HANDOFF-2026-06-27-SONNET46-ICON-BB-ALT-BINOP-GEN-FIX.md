# HANDOFF: ICON-BB float-alt + alt-arm-skip + general-alt — COMPLETE

**Date:** 2026-06-27
**Model:** Claude Sonnet 4.6
**Commit:** 61f8836 (SCRIP main)
**Status:** COMPLETE — m3+m4 PASS=206 (was 201), FAIL=46, zero regressions
**Baseline:** PASS=201 FAIL=51 EXCISED=1 (HEAD 12f0656)

---

## What Was Done This Session

Three root-cause fixes for the binop-with-generator-operand blocker, plus
general alternation infrastructure.

### Fix 1 — Float alternation arms (`bb_alt.cpp`, `emit_bb.c`)

`(2.5 | 3.5 | 4.5)` and any IR_ALT with IR_LIT_F arms bombed at runtime with
an unresolved-forward-reference abort. Root cause: the op_parts ok-check in
`descr_chain_operand_refs` accepted only IR_LIT_I and IR_LIT_S; IR_LIT_F arms
set `op_parts_n=0`, forcing `bb_alt` to take the `x86_bomb` path which never
defines the box's β → bb_emit_end reported N unresolved forward references.

Fix: extended the ok-check to accept IR_LIT_F, stored the IEEE-754 double bits
via `memcpy(&fb, &fd, 8)` into `op_parts_ival[i]` with tag DT_R, and extended
`bb_alt.cpp`'s `.quad` emitter to treat `DT_R` the same as `DT_I` (both are
raw 64-bit values; the DESCR union overlays `double r` at the same offset as
`int64_t i`).

### Fix 2 — Alt-arm pollution of the RPN operand stack (`emit_bb.c`)

`3 < (2|4|5)` (right-gen binop) aborted with `[GZ-3] FATAL bb_call_write_binop:
write(binop) — slot miss`. Root cause: `descr_chain_operand_refs` (the RPN
operand reconstruction) did NOT skip alt arms in its DFS, unlike its sibling
`codegen_flat_chain_body`. So when the DFS followed LIT3's γ→ an alt-arm
literal, it pushed that alt-arm literal (never emitted standalone → slot=-1)
onto the value stack; the binop then popped it as its left operand.

Confirmed with a probe in `descr_binop_set_slots`:
- rg_int `3<(2|4|5)`: c0=LIT_I slot=-1 (wrong — the alt arm), c1=ALT slot=16
- lg_int `(1|2|3)<5`: c0=ALT slot=0, c1=LIT_I slot=24 (correct — both had slots)

Fix: applied `ir_skip_alt_arms` on the entry node and `ir_skip_alt_arms(c->γ.node)` /
`ir_skip_alt_arms(c->ω.node)` on all queue pushes in both DFS loops of
`descr_chain_operand_refs`.

### Fix 3 — γ/ω wiring lookup didn't skip alt arms (`emit_bb.c`)

After Fix 2, the slot miss was gone but rg_int still produced empty output.
Root cause: `codegen_flat_chain_body`'s per-node wiring loop compared against
raw `γ.node`/`ω.node`, but the chain was *built* with `ir_skip_alt_arms`, so
an alt-arm target was never found in the nodes[] array → defaulted to main_γ.
The left-operand literal box ended with `jmp main_γ`, bypassing the rest of
the chain on the first pass (confirmed in m4 asm).

Fix: hoisted `gtgt = ir_skip_alt_arms(nodes[i]->γ.node)` and
`otgt = ir_skip_alt_arms(nodes[i]->ω.node)` before both wiring lookup loops,
then used gtgt/otgt in the array-scan `if (nodes[k] == gtgt)` comparisons.

### Fix 4 — General (non-literal) alternation (`emit_bb.c`)

The `expr | "fallback"` idiom (non-literal arms in IR_ALT) bombed:
`bb_alt: unhandled (needs <=5 literal arms, descr flat-chain)`. This is the
dominant non-literal-alt pattern in all real Icon programs (e.g.
`write(o(x) | "fail")`, `write(image(integer(s)) | "none")`).

New `ir_alt_all_literal_arms` gate — preserves literal-odometer fast path
when all arms are IR_LIT_I/S/F. New `flat_drive_alt_general` — for all other
cases: allocates a shared result slot (bb_slot_alloc16 + claim(8)), emits
each arm via walk_bb_flat with cascading failure labels (arm_start[i+1] as
the next-fail target), copies the arm's DESCR value into the shared slot via
`bb_emit_repalt_yield` on arm success, then jumps γ. β → lbl_ω (non-resumable;
Icon alternation within every-do IS resumable but that path goes through
the literal odometer or the chain-level β wiring, not this driver).

Modeled on `flat_drive_repalt` (same per-arm DESCR copy pattern). No new
template required — reuses `bb_emit_repalt_yield(off, src_slot)` from
`emit_core.c`.

Verified: `f()|"fallback"` → "fallback" · `g()|"VALUE"` → "VALUE"

### Results

| Metric | Before | After |
|--------|--------|-------|
| m3 PASS | 201 | **206** |
| m4 PASS | 201 | **206** |
| FAIL | 51 | **46** |
| EXCISED | 1 | 1 |

5 newly passing rungs: rung13_alt_alt_augconcat, rung13_alt_alt_cross_arg,
rung13_alt_alt_nested, rung15_real_swap_lconcat, rung16_seqexpr_gen_basic.
(Exact count confirmed by suite diff.)

All smokes green: icon 12/12 m3+m4 · snobol4 7/7 · prolog 5/5.
All 4 icn discipline gates green. SNOBOL4 smoke unaffected by emit_bb.c change.

---

## Remaining 46 FAILs — root cause map

Re-tallied after this session:

| Count | Blocker |
|-------|---------|
| 16 | `[IBB] FATAL bb_call: unsupported call shape fn=<X>` — distinct builtins/computed: display, open, move, tab, remove, `o` (operator-string), `p` (indirect), `goal`, `?` (computed callee) |
| 14 | Wrong output (secondary blockers exposed by alt fix; various) |
| 5 | `walk_bb_node: kind=5 unhandled` (IR kind 5 = IR_ASSIGN_LIT_S in some shapes) |
| 3 | `flat_drive_rasgn: x<-v requires an IR_VAR lvalue` (non-VAR reversible-assign lvalue) |
| 2 | `walk_bb_node: kind=7 unhandled` |
| 1 | `bb_var: unhandled arm` |
| 1 | `bb_unop: operand slot unresolved (LIT_F/NUL)` |
| 1 | `bb_section: only plain s[i:j] has a native arm` |
| 1 | `bb_binop_relop: shape mismatch` |
| 1 | unresolved forward reference (deep) |
| 1 | `flat_drive_swap: x:=:y requires two IR_VAR operands` (keyword-swap OOB) |

No single high-yield fix remains in the obvious short-term. The 16×
unsupported-call-shape cluster is the largest lever but each is a distinct
builtin (many need file I/O, operator-string invocation, or coexpressions).

---

## Files Changed

| File | Change |
|------|--------|
| `src/emitter/BB_templates/bb_alt.cpp` | Accept DT_R arms in `.quad` emitter |
| `src/emitter/emit_bb.c` | Fix 2 (op_parts ok-check + memcpy), Fix 3 (descr_chain_operand_refs alt-arm skip), Fix 4 (codegen_flat_chain_body wiring skip), Fix 5 (flat_drive_alt_general + ir_alt_all_literal_arms) |

---

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
