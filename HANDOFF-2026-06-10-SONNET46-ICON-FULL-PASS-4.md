# HANDOFF-2026-06-10-SONNET46-ICON-FULL-PASS-4.md

**Session:** 2026-06-10 · Claude Sonnet 4.6
**Goal:** GOAL-ICON-FULL-PASS — maximize m2 interpreter pass count
**HEAD (SCRIP):** `15608cf`
**m2:** 193/247 (was 192 at session start per actual build; goal watermark said 194 — minor drift)

---

## Work Done

### FULL-10: find() generative — LANDED `e79e806` (rebased `15608cf`)

**Root cause:** `every write(find("a","banana"))` only yielded first match.
Two-part fix:

1. `src/lower/lower_icon.c` `icn_det_call`: added `find` and `upto` to `allow_gen` check so `call_beta = call` (self-loop wiring) instead of `ω_in`. Without this, `every` had no β to pump.

2. `src/interp/IR_interp.c` `dval==3.0` builtin path: after `try_call_builtin_by_name` returns non-FAIL for `find`/`upto`, precompute ALL match positions into `susp_gen_cache` (same mechanism as user-proc generators with `state==1`/`counter`), then serve from cache on re-entry. `every write(find("a","banana"))` → `2\n4\n6`. ✅

**Why not a state==3 re-entry approach:** explored, abandoned — the `every` with `ival==0` and the arg subgraphs being frozen made it fragile. Precompute-all is cleaner and mirrors the existing user-proc generator cache path exactly.

### FULL-13: &-keyword routing — LANDED `15608cf` (rebased)

**Root cause:** Icon parser emits `TT_VAR` nodes with `sval="&lcase"` etc. (not `TT_KEYWORD`). The `TT_VAR` case in `lower_icon.c` lowered all such names to `IR_VAR` → NV_GET lookup → null.

**Fix:** `src/lower/lower_icon.c` `TT_VAR`/`TT_NAME` case: intercept `sval[0]=='&'` and emit `IR_KEYWORD` instead of `IR_VAR`. `kw_read()` in `keywords.c` already handles all the cset/math constants. Result: `type(&lcase)→cset`, `image(&lcase)→&lcase`, `*&lcase→26`, `&e→2.718...` etc.

**Residuals in rung37_keywords (3 items, still FAIL overall):**
- `& &e` parse ambiguity — `&e > 2.7 & &e < 2.8` parsed as `& (&e)` conjunction — parser precedence issue, not a keyword issue
- `&error := 42; write(&error)` — writable keyword write-back not persisted
- `&dump`/`&trace`/`&random` type — not yet implemented

---

## Next Steps (open in GOAL-ICON-FULL-PASS.md)

### FULL-15: cset literal canonical form (str relop `'ca' == "ac"`)

**Diagnosed, not yet fixed.** `'ca'` cset literal parsed and stored as raw `"ca"` string. `==` operator calls `VARVAL_fn` which returns raw `"ca"`, but `"ac"` is the canonical form. The `_STRREL` macro in `by_name_dispatch.c` doesn't canonicalize cset operands before comparing.

**Fix plan:** In `lower_icon.c` `TT_CSET` case, set `IR_LIT(n).dval = 1.0` as cset flag and store `cset_canonical(e->v.sval)`. In `IR_interp.c` `IR_LIT_S` handler, if `dval==1.0` emit `CSETVAL(...)` instead of `STRVAL`. This way cset literals become proper cset DESCRs and all existing cset-aware code paths handle them correctly.

**Expected gain:** rung37_str_relop PASS (+1), rung37_cset_ops potentially PASS (+several).

### FULL-14: scan-alt generator (`("ab"|"cd") ? move(1)`)

Only first alt subject fires. `IR_GEN_SCAN` + `IR_ALT` combination — the scan's subject alt needs to pump its β across subjects. Related to FULL-18.

### FULL-18: alt cross-arg / conjunction cross-product

`every x := (1|2|3) & y := (4|5)` only yields `1,4` — the `&` conjunction doesn't iterate. rung37_mutual test. Both FULL-14 and FULL-18 likely share the same root: `IR_ALT` β-resume not propagating through the scan/conjunction wrappers.

Consult `refs/jcon-master/tran/irgen.icn` `ir_a_Alt` and `ir_a_Scan` for canonical port topology before touching.

### FULL-12: string operator invocation

`o(x)` where `o="+"` — calling an operator as a proc by string name. `rung37_coerce.icn` calls `"+"("3")` expecting `3`. The `proc("+")(x)` dispatch path. Check `by_name_dispatch.c` for operator-string call dispatch.

### FULL-17: sort()

`sort(L)` and `sort(T,i)` not implemented. Add to `aggregates.c`. Consult `refs/icon-master/src/runtime/fstruct.r` for semantics.

---

## State Invariants (unchanged, all hold)

- m2 12/12 smoke HARD ✅
- Prolog m2 5/5 HARD ✅
- Unified broker 32/35 (pre-existing failures, not ours)
- No value stack, no C byrd-box functions, no bb_bin_t
- Zero SM opcodes for Icon programs
- `find`/`upto` now both have allow_gen=true in icn_det_call

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
