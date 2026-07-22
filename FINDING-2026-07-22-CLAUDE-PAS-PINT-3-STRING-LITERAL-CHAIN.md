# FINDING 2026-07-22 — PAS-PINT-3: `writeln('HI')` round-trip; string-literal chain (Claude)

## Summary
The PAS-PINT-3 cursor framed the blocker as a **pint interpreter handler** for `csp wrs`/`csp wln`.
The two-oracle bracket (fpc 3.2.2 native pcom/pint vs SCRIP) proves the fault is **entirely upstream
in pcom's string-literal handling under SCRIP** — pint faithfully prints the empty string it is given.

Decisive P-code diff (SCRIP-pcom `prr` vs native `prr` on `program t; begin writeln('HI') end.`):
```
SCRIP:   lca'                '     (16 blanks — the literal is lost)
native:  lca'HI              '
```
(The `ldci 2` field-width and `l N=9` spacing deltas are cosmetic print-width only, not bugs.)

## Oracle setup (reusable)
`apt-get install -y fp-compiler` → fpc 3.2.2. In a scratch dir with corpus `pcom.pas`/`pint.pas`:
```
fpc -Ci -Co -Cr -gl pcom.pas ; fpc -Ci -Co -Cr -gl pint.pas
./pcom < prog.pas > /dev/null ; cp prr prd ; ./pint < /dev/null    # native oracle prints HI
```
SCRIP round-trip: `scrip --run pcom.pas < prog.pas` → `prr`; `cp prr prd`; `scrip --run pint.pas < /dev/null`.

## Two fixes LANDED (pascal.y only; M3 146/0, zero regression)

### Fix 1 — char-array-FIELD element reads formatted as integers
`write(recfield^.arr[i])` printed the ordinal (`72`) not the char (`H`). `pas_is_charexpr` recognized a
char-array element only over a plain-VARIABLE base (`pas_is_chararr(e->c[0])`), never over a
**cafield-marked record-field node**. Added one branch:
`if (e->t == TT_IDX && e->n >= 2 && e->c[0] && pas_is_cafield(e->c[0])) return 1;`
Repros: r1/r2/r5/r6/r9/r10 (variant rec + `arr[i]^` with-selector + nested-proc uplevel — all native-match).

### Fix 2 — array-of-pointers element field-store ABORTED the compiler
`a[i]^.field[j] := x` where `a : array[..] of ^Rec` hit `FATAL emit_drive IR_ASSIGN guard`
(nameless 1-operand assign). ROOT: the element's pointed-to record type was DISCARDED at declaration —
the `array [..] of type` production nulls `g_pas_pend_ptrtarget`, so `a[i]^` could not resolve its record
type, `.field` fell back to an unresolved `TT_FIELD`, and `lower_assign` minted a nameless placeholder.
FIX: new `arrptr` registry (array-var-name → element record type):
- decls `g_pas_arrptr[]` / `g_pas_narrptr` / `pas_arrptr_add` / `pas_arrptr_target` + pending `g_pas_pend_arr_ptrto`
- capture element ptr-target in the `array..of type` production BEFORE the null (covers both `^Rec` and named ptr type)
- register in `var_decl` beside `pas_array_add`
- `pas_ptrexpr_target` resolves `TT_IDX[VAR a, <any index>]` via `pas_arrptr_target`
- reset `g_pas_narrptr`/`g_pas_pend_arr_ptrto` per program
Repro r8 (`a[i]^.sval[1] := 'H'`) now prints `[H]` (was abort). Zero new grammar conflicts (still 5, == pristine HEAD).

## STILL OPEN — the actual pcom blocker (BRACKETED to a minimal repro, fix locus identified)

pcom still emits blank `lca''` and stalls. Instrumented-pcom probes (RULES.md bracket theorem) pinpoint it:
- **DBG3 (last agreeing):** in `insymbol`, the string node is built correctly under SCRIP — `slgth=2 s1=H s2=I`.
- **DBG4 (first diverging):** in `loadaddress` (pcom.pas:2017), reading `cval.valp^.slgth` — native `2`,
  **SCRIP stalls silently on the read.** So the string-node pointer is valid at creation but DEAD by the
  time it is read back through the attribute record.

### Minimal standalone repro (no pcom) — `v4`/`v7`
```pascal
program t;
type csp=^cc; cc=record slgth:integer end;
     valu=record case b:boolean of true:(ival:integer); false:(valp:csp) end;
     attr=record cval: valu end;
var g: attr; v: valu; lvp: csp;
begin new(lvp); lvp^.slgth:=99; v.valp:=lvp;
  writeln(v.valp^.slgth);         { 99 both }
  g.cval := v;                    { <-- pointer lost HERE under SCRIP }
  writeln(g.cval.valp^.slgth)     { native 99 ; SCRIP 0 }
end.
```

### Trigger isolated by elimination (all native-match; SCRIP differs only on the last)
- v1 var-to-var whole variant-record copy carrying a pointer arm → **OK**
- v5 PLAIN inner record with pointer, copied into a record FIELD → **OK**
- v6 variant record with pointer, var-to-var copy → **OK**
- **v4 VARIANT record with pointer, copied into a record FIELD → FAILS (`slgth=0`)**
=> the bug requires BOTH: (a) the copied record is a VARIANT with a pointer arm, AND (b) the copy target
is a FIELD of an outer record (`outer.field := variantval`).

### Mechanism / fix locus (next session — mechanical)
`g.cval := v` lowers to `(TT_ASSIGN (TT_IDX (TT_VAR gattr) (TT_ILIT 0)) (TT_VAR val))` → runtime
`arr_set_pure` (by_name_dispatch.c:3167) [or `__pas_field_set`:2176]. Both serialize the RHS whole record
via `to_cstring(args[2], rb, 64)` and SOH-splice it into the target field. A PLAIN inner record round-trips
through this; a VARIANT record's whole-r-value does NOT preserve its pointer-arm word. So the fix is in how
a **variant record read as a whole r-value for storage into a nested field** is materialized/serialized —
either `to_cstring` of a variant-record descriptor, or the r-value shape of `val` (variant) differs from a
plain record's. Confirm with a probe of what `val` serializes to (DT_A vs SOH string) at the `arr_set_pure`
entry, then make the variant whole-value carry its pointer word like the plain-record case already does.

### ROOT CONFIRMED — variant arms are NOT overlaid under SCRIP (the mechanism)
Probe: after `v.valp := lvp`, read the OTHER arm `v.ival` (the integer overlay of the same word):
native `28736` (the raw pointer value, overlaid as a C union would), **SCRIP `0`**. So SCRIP does NOT
represent a variant record as a true overlay — the arms have SEPARATE storage (stored as multiple SOH
elements, one slot per arm: `[ival][valp]`). This is self-consistent for var-to-var copy (v6 carries all
slots) and for reads through the SAME arm. It BREAKS only when a whole variant r-value is spliced into a
nested field by `arr_set_pure`/`__pas_field_set`, which carry a SINGLE element — element 0 = `ival` (=0),
dropping element 1 = `valp` (the live pointer). THE FIX (next session, runtime): the whole-record-value
store into a nested field must carry ALL slots of a variant/multi-field record (splice the whole
SOH-multi-element value), not one element — mirroring how var-to-var whole-record copy already preserves
every slot. Locus: `arr_set_pure` (by_name_dispatch.c:3167) idx-0 whole-value path + `__pas_field_set`:2176.
Guard the change so plain scalar element stores (the common `a[i] := scalar`) are unaffected — dispatch on
whether the RHS is itself a whole record value.

## State
- SCRIP dirty: `src/parser/pascal/pascal.y` (14 lines) + regenerated `pascal.tab.c/.h`. Pascal-only, no shared files.
- NOT committed, NOT pushed (needs credential). M3 146/0 verified with the two fixes in.
- corpus untouched (no new gated probes added yet — v4/r8/r1 are pcom-input-class repros, kept in /tmp).
