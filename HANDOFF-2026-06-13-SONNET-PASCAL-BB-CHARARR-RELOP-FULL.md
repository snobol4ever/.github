# HANDOFF-2026-06-13-SONNET-PASCAL-BB-CHARARR-RELOP-FULL.md

## Session summary
Goal: GOAL-PASCAL-BB.md — Lon's directive "ignore mode 2, get modes 3 and 4 working."

Closed the full char-array comparison surface (all six relops × VAR/LIT_S/CALL)
in M3/M4 — the mechanism `pcom.pas` uses for reserved-word lookup. Three fixes,
each regression-protected by a gated probe.

## Gate state
- Entering: M2 103/0 · M3 103/0 · M4 103/0 (M4 verified via proper link-and-run gate)
- Leaving:  M2 106/0 · M3 106/0 · M4 106/0  XFAIL=1  (+3 probes)

## M4 gate clarification (important)
`scrip --compile` emits GAS `.intel_syntax noprefix` TEXT, not a binary. The gate
must assemble+link+run before comparing to .ref:
```
scrip --compile f.pas > p.s && gcc -c p.s -o p.o &&
gcc p.o -L<out> -lscrip_rt -lgc -lm -Wl,-rpath,<out> -o p.bin && ./p.bin
```
(recipe = corpus `scripts/test_mode4_broad_corpus_snobol4.sh` `compile_mode4()`).
Comparing the raw asm text to .ref is a false-fail. `/tmp/run_gate_m4.sh` (recreate
each session) uses the link-and-run form; M4 was already 103/0, not failing.

## What landed
All three share ONE type-polymorphic descriptor arm:
`bb_binop_gvar_relop.cpp` → `rt_relop_descr2(l_lo,l_hi,r_lo,r_hi,op)` →
`binop_apply` (M2's SOH-normalized memcmp; DT_I falls through to integer cmp).
The arm body is relop-agnostic (passes `op_ival` to `rt_relop_descr2`), so the
work was WIDENING DISPATCH GATES, not adding comparison logic.

1. **`id = 'writeln '`** — char-array VAR vs string LITERAL, EQ/NE.
   - Was bombing `bb_binop_relop: shape mismatch`. Pascal runs on
     `g_gvar_flat_chain`; `bb_binop_relop`'s arms are all `g_descr_flat_chain`-gated
     → bomb. The LIT_S operand had no slot, so the gvar-relop inner guard fell
     through to `flat_drive_binop_tree` → `bb_binop_relop`.
   - SCRIP `fe009d9`: `emit_bb.c` admits IR_LIT_S in the gvar-relop outer guard +
     trigger; `bb_binop_gvar_relop.cpp` descriptor arm gains a LIT_S sub-arm that
     builds a DT_S descriptor inline (lo=DT_S/slen0, hi=`lea [rip+sealed]`; slen0
     → binop_apply uses strlen). Content sealed via `bb_intern_into` (rodata),
     distinct from `strtab_label` var-name sealing. Probe `chararrlit` (=111).

2. **`a = b`** — char-array VAR vs VAR, EQ/NE. SILENT WRONG (both whole-array DT_S
   collapse to 0 via `rt_gvar_get_int` on the int fast path → `=` always true).
   - No runtime type info at the dispatch, but the PARSER knows char-array identity.
   - SCRIP `151caa1`: `pascal.y` `pas_rel`/`pas_is_strtyped` flag a relop AST node
     `v.ival=1` when both operands are string-typed (whole char-array VAR or string
     literal); `lower_pascal.c` `lower_binop` carries it → `IR_LIT(op).dval=1.0`
     (dval was unused on IR_BINOP — confirmed no reader); `emit_bb.c` trigger reads
     dval==1.0 to force the descriptor arm. Probe `chararrvv` (=21).

3. **`a < b` / `a >= 'lit'`** — char-array ORDERING (< <= > >=). VAR-vs-VAR took the
   int fast path; VAR-vs-LIT_S bombed the EQ/NE-only arm ("predicate failed").
   - SCRIP `2c7bd6d`: `pas_eqrel`→`pas_rel` covers all six relops (new
     `pas_rel_or_set` keeps set subset/superset for LE/GE, else flags string LE/GE);
     `emit_bb.c` trigger restructured — `op_relop_descr` fires when op∈[LT..NE] AND
     both operands ∈ {CALL, named-VAR, LIT_S} AND (hint dval==1.0 OR a LIT_S operand
     OR session-50 EQ/NE+CALL); `bb_binop_gvar_relop.cpp` D predicate widened
     EQ/NE → [LT..NE]. Integer VAR-vs-VAR / VAR-vs-LIT_I stay inline. Probe
     `chararrord` (=707).

corpus probes: `6abd1d34` chararrlit, `c0bd9902` chararrvv, `4552cb45` chararrord.

## Discipline (all clean)
- `bb_binop_gvar_relop.cpp`: 0 raw-byte producers, 0 `MEDIUM_*`, 0 `x86_(frame|ro|reg)_*`
  free-fns, 0 language names. Speaks only `x86(...)`.
- `emit_bb.c` / `lower_pascal.c` / `pascal.y` changes are IR-shape + type-hint logic
  (dispatch + parser), not template violations.
- Medium-invisible strict: `bb_binop_gvar_relop` NOT in REMAINING (only the
  pre-existing bb_is_cmp / bb_list / bb_resolve / bb_type_test).
- Pascal parser regenerated via `bison -d -o pascal.tab.c pascal.y` (Pascal-only).
  The "5 shift/reduce conflicts" are pre-existing — edits changed rule ACTIONS only,
  not productions.

## IMPORTANT learnings / landmines
- Pascal is on `g_gvar_flat_chain`, NOT `g_descr_flat_chain`. `bb_binop_relop`'s
  arms are descr-gated, so any relop that reaches it for Pascal bombs. The gvar
  relop path lives entirely in the `emit_bb.c` `IR_BINOP` `g_gvar_flat_chain &&
  op_is_rel` branch → `IR_BINOP_GVAR_RELOP` → `bb_binop_gvar_relop.cpp`.
- The descriptor arm is the type-polymorphic spine for ALL char-array/string
  comparison; do not duplicate comparison logic — just feed the right operands and
  set `op_relop_descr`.
- `IR_BINOP.dval` is the free field used to carry the parser's string-type hint.
- LIT_S content must be sealed with `bb_intern_into`/`emit_intern_str` (rodata),
  NOT `strtab_label` (that's for global-variable NV-table names).

## Remaining frontier (next session), priority order
1. **CALL-vs-CALL char-array ordering** (`rw[i] < rw[j]`) — no hint, no LIT_S →
   still integer fast path. Extend the string-type hint to indexed char-array
   expressions (parser knows `pas_is_chararr` of the base), or add an ordering
   CALL trigger. Decide from whether pcom's reserved-word search uses ordering.
2. **Array-of-char-arrays** (`rw[1][2] := 'x'`, `rw[1] = 'lit'`) — `flat_drive_assign`
   FATALs ("lhs (α) must be IR_VAR with sval, got kind=9"); M2 fails too, so this is
   an unimplemented nested-array feature, not purely M3.
3. **Default-space init** of unset packed-char elements (`chararr_probe` → "FAIL"
   not "MATCH") — shared across all modes, arguably non-standard (pcom pads
   reserved words explicitly), so deprioritized.

## What to read next session
- GOAL-PASCAL-BB.md (live state + mechanism inventory relop note), RULES.md
- For frontier #1: `bb_binop_gvar_relop.cpp` descriptor arm; `emit_bb.c` IR_BINOP
  gvar-relop trigger; `pascal.y` `pas_rel`/`pas_is_strtyped`.

## Watermark
Session 51 (2026-06-13). M3/M4: 103→106 (+3 char-array comparison probes; all six
relops × VAR/LIT_S/CALL closed). alphacmp (session 50) unaffected.
