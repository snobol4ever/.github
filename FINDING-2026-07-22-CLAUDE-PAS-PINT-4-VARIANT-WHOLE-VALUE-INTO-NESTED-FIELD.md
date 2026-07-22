# FINDING 2026-07-22 — PAS-PINT-4: variant-record whole-value store into a nested field (Claude)

## Summary
`outer.field := variantval` (a WHOLE variant/multi-slot record stored into a FIELD of an enclosing
record) dropped every slot but the first. This was the pcom string-literal blocker bracketed by the prior
session (FINDING-2026-07-22-...-STRING-LITERAL-CHAIN). **FIXED** — Pascal-only, 2 files, M3+M4 147/0, zero
regression. SCRIP-pcom now emits correct P-code for `writeln('HI')` and `writeln(i)` (proven: native fpc
`pint` runs SCRIP's emitted P-code and prints `HI`/`5`).

## Root cause — a WRITE/READ representation mismatch (corrects the prior FINDING's hypothesis)
The prior FINDING guessed the fix was in `arr_set_pure`/`__pas_field_set` "carrying all slots." Instrumenting
the actual runtime sinks (env-gated `SCRIP_PAS_DBG` byte-dumps, since removed) showed the real mechanism:

SCRIP record representation (confirmed from `by_name_dispatch.c` sinks):
- Outer record fields are separated by **SOH (`\x01`)**.
- A NESTED sub-record occupies ONE field, with its elements separated by **`\x05`**.
  `__pas_nrec_get`/`__pas_nrec_update`/`pas_nrec_subrec_set` all honor this `\x05`-in-one-SOH-field form.

`g.cval := v` (v = variant record, 3 SOH slots `0\x01ptr\x01 0`) lowered to the GENERIC `arr_set_pure`
element-store, which spliced v's whole value into field 0 of `g` **RAW, keeping v's SOH separators**. So
field 0 became `0\x01ptr\x01 0` — SOH where `\x05` was required. The read side
`__pas_nrec_get fi=0 ei=1` then parsed field 0 as just `"0"` and found no `\x05`-element 1 -> returned 0.

Decisive trace (v4, `program t; ... g.cval:=v; writeln(g.cval.valp^.slgth)`):
```
[ARR_SET] idx=0 cur=[0] rv=[0|SOH|1|SOH|0]      <- g.cval:=v spliced v's SOH slots raw into g field 0
[NREC_GET] fi=0 ei=1 cur=[0|SOH|1|SOH|0]         <- read wants field0 as x05-subrecord; finds none -> 0
```
Contrast v5 (PLAIN inner record, works): the plain record has ONE slot, stored as a single scalar `"1"`,
read correctly by `__pas_nrec_get fi=0 ei=0`. The bug needs BOTH (a) a MULTI-slot (variant) source AND
(b) a nested-field target — exactly the prior FINDING's elimination table.

## P4 source cross-check (why native Pascal never had this bug)
`comp.p`/`pcom.pas` `fieldlist`: variant arms are a TRUE OVERLAY — `displ` resets to `minsize` before each
arm; record size becomes `maxsize` (the largest arm). `int.p`/`pint.pas` `mov` (op 55, structured assign) is
a blind block copy of `q` tagged units. Native "preserves the pointer arm across whole-record copy" for free
because the record is already sized to the biggest arm and `mov` copies the whole footprint. SCRIP instead
stores arms as separate slots, so a whole-value store must carry every slot — which the SOH->x05 conversion
now does.

## Fix (2 files, Pascal-only, no shared files)
1. **Runtime** (`src/runtime/by_name_dispatch.c`, new sink after `__pas_nrec_update`):
   `__pas_nrec_field_set(outer, fi, whole_rec)` — replaces field `fi` of the SOH-separated outer record
   with `whole_rec`, converting the RHS's inner **SOH separators to `\x05`** so it lands as a proper nested
   sub-record. Only touches field `fi`; other fields untouched.
2. **Lowering** (`src/parser/pascal/pascal.y`, new clause in `mk_assign` before the fall-through):
   when the target is `TT_IDX(TT_VAR base, TT_ILIT fi)`, field `fi` of base's record type is ITSELF a record
   type (`pas_rectype_field_rectype_by_index` non-NULL), AND the RHS resolves to a record type
   (`pas_with_sel_rtype(rhs)` non-NULL), emit `base := __pas_nrec_field_set(base, fi, rhs)` instead of the
   generic `arr_set_pure`. Guarded tightly so plain `a[i] := scalar` (non-record field) is unaffected.

Regen: `bison -d -o pascal.tab.c pascal.y` -> **5 shift/reduce conflicts == pristine HEAD** (zero new).

## Verification
- v4 (the bracket): was `99`/`0`, now `99`/`99` in BOTH M3 and M4.
- v5 (plain rec into field) `99`, v6 (variant var-to-var) `99` — unchanged (no regression on the OK cases).
- New gated corpus probe `corpus/programs/pascal/vrecfield.pas` (+ `.ref`, SCRIP width-10, value-cross-checked
  vs native fpc `99`/`99`). M3 **147/0**, M4 **147/0** (was 146/0; +1 = the new probe).
- Cross-language: SNOBOL4/Icon/Prolog smokes unchanged. `mk_assign` is Pascal-only; the new clause fires only
  when both sides resolve to Pascal record types. Two apparent smoke "failures" (`empty_string.sno` parse
  error, `palindrome.pl` IR op=121) proven PRE-EXISTING via stash->pristine-HEAD rebuild (identical there).

## pcom->pint round-trip status (what this unblocks, and the NEXT rung)
- **SCRIP-pcom side: DONE.** `writeln('HI')` -> P-code `lca'HI...' / csp wrs / csp wln / retp`,
  structurally identical to native fpc-pcom (only cosmetic field-width spacing differs — non-bugs).
  **Native fpc `pint` runs SCRIP's emitted P-code and prints `HI`** — SCRIP's P-code is valid and complete.
- **SCRIP-pint side: NEXT RUNG (separate, pre-existing gap).** SCRIP running `pint.pas` soft-falls
  (`[SBB] mode-3 ... soft fall — no output`) on ANY write path (integer and string alike), so SCRIP-pint
  prints nothing where native pint prints the value. Bracketed to `emit_chain` returning NULL via
  `bb_emit_overflow` on pint's LARGE graph. Bumping FLAT_BUF_MAX (256K->16M) AND BB_PATCH_MAX (64K->1M)
  TOGETHER moved main past the NULL return, but a residual soft-fall persists from a PROC-level emit (no
  `[CHAIN_NULL]` from main once both limits raised). So the pint-execution gap is TWO-part: (a) mode-3 flat
  emission limits are too small for pint-scale graphs, and (b) a residual box-shape/proc emit gap remains
  after the limits are raised. Both experimental bumps were REVERTED (throwaway diagnostics); the fix for
  this is the next rung's work (PAS-PINT-5), not landed here.

## State
- SCRIP dirty: `src/parser/pascal/pascal.y` (+ regenerated `pascal.tab.c`/`.h`), `src/runtime/by_name_dispatch.c`.
- corpus dirty: `programs/pascal/vrecfield.pas` + `.ref` (new gated probe).
- `emit.cpp`/`emit.h` confirmed CLEAN (experimental limit bumps reverted; diagnostic removed).
- Committed locally; PUSH PENDING (awaiting credential).
