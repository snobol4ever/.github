# FINDING 2026-09-02 (ceo, TRIO, Icon work on Lon's order, fourth landing) — `name()` over an alternation, a keyword, or a static resolved in the lowerer; `name()` of a list/table/record element is a runtime naming gap, rowed

**Row:** `icon-assign-nameless-emit-guard-var` gap (2), the lowerer half; **landed** SCRIP `7409bf45` (lowerer only). **Oracle:** Arizona `icont`/`iconx` v9.5.25a. **Box clock** 17:15–17:40 CDT, under Lon's wrap-up order.

## Measured (scrip on `bd6bacb7` vs oracle)

| shape | before | oracle |
|---|---|---|
| `name(main)` · `name(T)` local · `name(a)` param | = oracle | "main" "T" "a" |
| `static s; name(s)` | `"main__STATIC__s"` (the statics prepass renames the tree; the literal arm echoed the mangled name) | "s" |
| `every write(image(name(x \| y)))` · `name(main \| T)` | nothing | "x" "y" · "main" "T" |
| `name(&subject)` | nothing | "&subject" |
| `name(L[2])` | nothing | "L[2]" |

The `name` arm of `lower_call` returns the name at compile time only for a plain identifier; an alternation or keyword argument fell to the lvalue path, whose slot references carry no name at runtime, and the runtime `name` builtin then fails.

## The cure

`name(A | B | …)` is rewritten at the tree level to `name(A) | name(B) | …` (each arm reaches the literal arm; Icon's `name` over an alternation generates the arms' names in order); `name(&kw)` lowers as the literal `"&kw"`; a static's mangled name (`<proc>__STATIC__<name>`) is un-mangled for the current procedure.

## Not cured — rowed

`name()` of a list element, table element or record field prints nothing: the element `VARREF` carries no base name and no normalised index (`rung36_jcon_var` expects `"L[200]"` for `L[-1]` on a 200-list, `"T[\"abc\"]"` with the key imaged, `"complex.r"` with the record TYPE for an anonymous record). Row `icon-name-of-a-list-table-or-record-element-prints-nothing-vcell-carries-no-base-name` (rank 2) carries the mechanism and a DONE-WHEN that fails today (rc=1 measured).

## Verdicts on the patched tree

38 probes = oracle (the full set of this session's Icon witnesses); `rung36_jcon_var` diff shrank from 57 to 50 lines — the remaining lines are exactly the element names above and `display()`; Icon smoke 14/14 both modes; `strip_comments.py --check` 0; `test_gate_emit_no_lang.sh` OK; STRICT rung suite `PASS=264 FAIL=6 BADEXIT=1 XFAIL=27 TOTAL=298` in all three modes — the watermark, unchanged; re-proved on the rebased build 26/26 + smoke 14/14.
