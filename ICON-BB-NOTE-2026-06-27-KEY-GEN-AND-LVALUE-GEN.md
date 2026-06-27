# ICON-BB note 2026-06-27 — IR_KEY_GEN landed + !t:=v lvalue-generator gap mapped

## Session result (Claude, on SCRIP base 70e2b370 — UNCOMMITTED)

`key(t)` is now a proper Icon generator. Suite **PASS=211→212 FAIL=41→40**,
m3==m4 byte-identical, rigorous FAIL-set diff = exactly one gain
(`rung23_table_table_key`), zero regressions, no swaps. icon 12/12 m3+m4,
prolog 5/5, snobol4 7/7, all four icn discipline gates green, template-purity
clean, bb_bin_t gate 0.

### What was wrong
`key(t)` returned only the FIRST table key (single-shot), so
`every total +:= t[key(t)]` summed one key → 10 not 60. Root cause: `key`
routed through the stateless by-name builtin dispatch (no resume cursor),
unlike `!t` which lowers to the `IR_LIST_BANG` generator box holding an index.

### The fix — completed the half-scaffolded IR_KEY_GEN kind
`IR_KEY_GEN` already existed in the enum and in three emit_bb.c generator
classifiers (lines ~1468/2196/2207) but had NO lowerer, dispatch, template, or
runtime helper. Wired it to reuse the entire IR_LIST_BANG resume machinery:

| File | Change |
|------|--------|
| `src/runtime/rt_runtime.c` | `list_bang_key_at` — bucket-walk returning `ep->key_descr` (clone of `list_bang_at`'s table branch) |
| `src/runtime/rt/rt.c` | `rt_list_bang_key_at` wrapper |
| `src/lower/lower_icon.c` | `lower_key` (intercept `key(t)` in `lower_call`, build `IR_KEY_GEN` over the table arg, mirror `TT_ITERATE`); add `key` to `icn_call_allow_gen` |
| `src/emitter/BB_templates/bb_key_gen.cpp` | NEW — clone of `bb_iterate` calling `rt_list_bang_key_at` |
| `src/emitter/BB_templates/bb_templates.h` | declare `bb_key_gen` |
| `src/emitter/emit_core.c` | `case IR_KEY_GEN: bb_emit_x86(bb_key_gen(nd));` |
| `src/emitter/emit_bb.c` | route `IR_KEY_GEN` → `flat_drive_list_bang`; add to `bb_call_write_route` wintexpr (~2843), `is_intexpr_shape` (~3067), `descr_chain_arity` returns 0 (~3702) |
| `Makefile` | source list + explicit compile rule for `bb_key_gen.cpp` |

### KEY LESSON — the consumer-side classifiers are load-bearing
Lowerer+template+runtime got the generator ITERATING (correct count of values)
but `write(key(t))` printed BLANK until `IR_KEY_GEN` was also registered in the
FOUR consumer slot-recognition sites above. Without them `write`'s arg fell to
the generic by-name marshal (route 0) which re-evaluates from an unwired slot.
A mode-4 runtime probe confirmed the keys were retrieved correctly all along
(mode-3 uses the in-`scrip` runtime; mode-4 uses libscrip_rt.so — probe the
right one). The bug was purely consumer slot-wiring, not the generator.

Verified robust: integer keys, string keys, `every key(t) do …`, empty-table
clean failure, `every t[key(t)]` composite — all correct both modes.

## NEXT — `!t := v` (assign to a generator lvalue) is BROKEN [kind=5 cluster]

`every !t := 88` (set every table element to 88) emits
`# [walk_bb_node: kind=5 unhandled]` and is a NO-OP. AST:
```
TT_EVERY( TT_ASSIGN( TT_ITERATE(t), TT_ILIT 88 ) )
```
i.e. `IR_ASSIGN` whose LVALUE is a generator (`!t`), reaching the unhandled
default in emit_core.c IR_ASSIGN (line ~435: not flat-chain + RHS not in the
whitelist → falls through). This is the kind=5 bucket that also blocks several
rung36 integration programs (substring/table/lists/mindfa/record/wordcnt).

This is NOT a small isolated arm (unlike key). It needs the generator to yield
element *references* (lvalues), not values, threaded to an assign that writes
through them — the `IR_RASGN`/reversible-assign family territory. Plan a real
design (how `!x` produces an assignable cell ref, where the assign target slot
comes from) rather than patching. Likely shares mechanism with `x[i] <- v`
(flat_drive_rasgn non-VAR lvalue, another open cluster).

## Handoff status
UNCOMMITTED on disposable sandbox. 8 files changed (7 modified + 1 new
bb_key_gen.cpp). Before committing: run the codegen artifact-refresh
(util_regen_* / update_icon_bench_asm.sh) since the emitter changed, then
commit + push, then `scripts/handoff_status.sh` for the authoritative status.
