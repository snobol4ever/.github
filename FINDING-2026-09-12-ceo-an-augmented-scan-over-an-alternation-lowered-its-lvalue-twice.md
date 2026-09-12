# FINDING 2026-09-12 15:32 CDT (ceo) — an augmented scan over an alternation lowered its lvalue twice

**Tree:** measured on SCRIP `4faf4ed6b`, cured `5eeeb3a47` · corpus `0c87851ca` (adllist, adlsort, adlcheck — the IPL programs that exposed it) · seat ceo (lane ICON TO 100%) · cursor CEO-633.

## Measurement

Minting refs for four address-list filters read three red in both modes: adllist printed blank names, adlsort nothing, adlcheck no
address blocks. All three go through `procs/adlutils.icn` `nextadd()`, whose last step is the idiom
`every text | comments ?:= { move(1); tab(0) }`. Witness (both modes): text "" comments "" where icont gives "abc" and "" — and
`every (text | comments) ?:= tab(0)` gave text = comments' value. Scope: `+:=`, `||:=` and `:=` over the same alternation are right.

## Cause

`case TT_AUGOP` rewrote `LV ?:= RHS` as the AST `LV := (LV ? RHS)`. For a plain variable that is harmless; for an alternation the
lvalue subtree is lowered twice — once as the scan subject (a value generator), once as the assignment target (an lvalue generator) —
and the two generators advance independently, so the subject scanned belongs to one variable and the result is assigned to another.
The other augmented operators lower the lvalue once and take `IR_DEREF` of that node, which is why they were right.

## Cure (SCRIP `5eeeb3a47`)

The `TT_SCAN` case is refactored into `lower_scan_impl(cx, subj_t, lv_t, body_t, γ, ω, res, lv_out)`: with a subject subtree its wiring
is the old case verbatim; with an lvalue subtree it lowers the lvalue once through `lower_lvalue_var` at the same point the subject used
to be lowered and scans over its `IR_DEREF`. An augmented scan whose lvalue is `TT_ALTERNATE`, `TT_IDX` or `TT_FIELD` builds
`IR_ASSIGN_VAR(lv, scan-result)` around it; a plain-variable lvalue keeps the rewrite. No template or runtime change.

## Proof

`test_gate_icn_augmented_scan_over_an_alternation.sh`: nine shapes, ref cut from icont, byte-identical in m3 and m4; `FAIL_ONCE=1`
trips the diff arm; wired into `make test`. Control arms: `test_smoke_icon` 15/15 both modes; all eight `test_gate_icn_*scan*` gates,
the seq and alternation gates, `emit_no_lang`, `icon_arguments_dereference_at_the_call` green; preflight 33/0; adllist, adlsort,
adlcheck, adlfirst PASS/PASS in the IPL runner's isolation.
