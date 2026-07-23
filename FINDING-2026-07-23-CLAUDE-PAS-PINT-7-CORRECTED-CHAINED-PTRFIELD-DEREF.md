# FINDING 2026-07-23 (CORRECTED) — PAS-PINT-7 is NOT aggregate-local alias; it is chained pointer-field deref

**Supersedes the diagnosis in `FINDING-2026-07-23-CLAUDE-PAS-PINT-7-AGG-LOCAL-ALIAS-UNDER-RECURSION.md`.**
That finding's root-cause claim ("aggregate locals alias one per-proc global cell under recursion") and its
proposed fix ("give aggregate locals per-activation frame slots in `lower_pascal.c pas_resolve_name`") are
**wrong for the actual pcom symptom** — verified by measurement this session. No code changed this session.
Gates on clean HEAD: M3 spot-checked green (39/39 of first 40; full 149/0 recipe unchanged from HEAD).

---

## How the prior diagnosis was falsified (MEASURE-FIRST)

1. The prior finding's own minimal repro `ov6.pas` (record local under 3-deep recursion) now runs **correct**
   on a clean HEAD build (`300 200 100`, matching native fpc). The scalar control `ov7.pas` is also correct.
   So the "aggregate-local alias under recursion" mechanism does **not** reproduce.
2. The real pcom symptom (`array[1..N] of integer` mis-sized) has nothing to do with recursion. Isolated with
   `t_sz.pas` (`var a: array[1..5] of integer; x,y: integer`):
   - Native pcom: `x`→offset 14, `y`→15 (array occupies 5 units).
   - SCRIP-pcom: `x`→offset 10, `y`→11 (array occupies **1** unit). The array size collapses to 1.

## The real bracket (instrumented pcom copies in /tmp, native fpc-3.2.2 oracle at /tmp/p4o)

Array size in pcom is `lsize := lsize*(lmax-lmin+1)` (pcom.pas:1321), with `lmin/lmax` from
`getbounds(inxtype,...)` (pcom.pas:628). Instrumenting the array-decl block and `getbounds`:

- `#DBGARR` (after getbounds): native `lmin=1 lmax=5` → finalsize 5. SCRIP `lmin=0 lmax=0` → finalsize 1.
- `#GB` (inside getbounds `with fsp^`): native `form=1` (subrange) → takes the subrange branch → reads
  `min.ival=1, max.ival=5`. SCRIP `form=0` (scalar) → subrange branch NOT taken → `fmin/fmax` stay 0,0.

So `getbounds` sees `inxtype^.form = scalar(0)` where it should be `subrange(1)`. But the subrange type was
built correctly:

- `#IMM` (immediately after `lsp^.form := subrange` at pcom.pas:1088, and after the `constant()` call):
  SCRIP reads `ord(lsp^.form)=1`. **The write is correct.**
- `#P1..#P5` (tracking the same subrange cell as it flows through array-decl processing, pcom.pas:1296–1315):
  the cell's `form` reads **1** immediately, then **0**, then via one alias `1` while via another `0`, then
  `3`, then `8` (=`variant`) by the time `getbounds` is reached. Reading the SAME heap cell through
  different pointer expressions yields different field values.

## Root cause (reduced to a 20-line standalone repro — verified on clean HEAD)

The fault is **chained deref of a pointer-valued record field**: `base^.ptrfield^.g` reads the wrong value,
even though the stored pointer is correct.

`ptr2.pas` (see `/tmp/pint7/ptr2.pas`):
```pascal
program ptr2;
type
  eform = (escalar, esubrange, epointer, epower, earrays);
  pp = ^prec;
  prec = record size: integer;
           case form: eform of
             escalar:  (fc: integer);
             esubrange: (rmin, rmax: integer);
             earrays:   (ael, inx: pp)
         end;
var arr, sub, cpy: pp;
begin
  new(arr); arr^.form := earrays;
  new(sub); sub^.form := esubrange; sub^.rmin := 1; sub^.rmax := 5;
  arr^.inx := sub;
  cpy := arr^.inx;
  writeln('A copy-then-deref: cpy^.form=', ord(cpy^.form));        { native 1 · SCRIP 1  ✓ }
  writeln('B chained deref:   arr^.inx^.form=', ord(arr^.inx^.form)); { native 1 · SCRIP BLANK ✗ }
  if arr^.inx = sub then writeln('C ptr-eq TRUE') else writeln('C ptr-eq FALSE');  { both TRUE }
end.
```

Discriminator result:
- **A** copy the field to a plain pointer var, deref that → **correct** (single-level deref is fine).
- **C** `arr^.inx = sub` → **TRUE** (the pointer VALUE stored in the field is correct).
- **B** direct chained `arr^.inx^.form` → **wrong/blank**.

Therefore: store is correct, pointer value is correct, single deref is correct. The bug is specifically the
**chained access `(base^.ptrfield)^.field`** where the intermediate `^.ptrfield` is a pointer-valued record
field. This is a **frontend type-resolution / lowering bug, not a runtime representation bug** (the value is
correctly stored and reachable via a temp).

## Why pcom triggers it

pcom's `selector` (array arm) reads `inxtype^` where `inxtype` is a pointer-valued field of the array's
`structure` cell (`arrays: (aeltype, inxtype: stp)`). Reaching `inxtype^.form`/`.min.ival` is exactly the
chained-pointer-field-deref pattern. When resolution fails, the field index is not found, the wrong slot is
read → `form` looks like `scalar` → `getbounds` returns 0,0 → array size 1 → no `chki/deci` emitted and, in
`selector`, `comptypes(inxtype,gattr.typtr)` fails → `error(139)` → scalar `sro` instead of indexed `sto`.
(The `error(399)` on the `program` line is BENIGN — native pcom emits the identical `^399^14,14,18`; it is a
lexer artifact of how the source is fed, not a SCRIP bug. Do not chase it.)

## Fix locus (named, for next session)

`src/parser/pascal/pascal.y`, the field-select production `selector PERIOD IDENT` (~line 807) resolves the
base record type via `pas_selector_rectype($1)`. For a base that is `__pas_deref(TT_IDX(recvar, fieldidx))`
(i.e. `recvar^.ptrfield`), the chain is:
`pas_selector_rectype` → `pas_ptrexpr_target` → (TT_IDX+ILIT arm) `pas_with_sel_rtype(c[0])` +
`pas_rectype_field_ptrto_by_index(rt, fieldidx)`.

The registry DOES carry pointer-field target types (`g_pas_rectypes[].fldptrto[]`, populated via
`g_pas_pend_ptrtarget` in `pas_pend_add`). So one of these links is returning NULL for the chained case:
- (a) `pas_with_sel_rtype` fails to resolve `recvar`'s record type for the inner base, OR
- (b) the pointer-valued field's `fldptrto[fieldidx]` was never populated — most suspect for a **variant-arm**
  field (`earrays: (ael, inx: pp)`) and/or a field whose pointer type is **forward-declared** (`pp = ^prec`
  before `prec` is defined). The `structure` type in pcom is exactly this shape: variant-arm pointer fields
  with mutually-recursive forward pointer types.

**Next step:** instrument the grammar C (print what `pas_selector_rectype`/`pas_ptrexpr_target`/
`pas_rectype_field_ptrto_by_index` return for `ptr2.pas`'s `arr^.inx^.form`), find the NULL link, and populate
it. Most likely fix: ensure `fldptrto[]` is recorded for variant-arm pointer fields and for forward-declared
pointer field types (the `pas_pend_add` path for fields declared inside a `case ... of` variant, and the
resolution of a forward pointer target name). Then add `ptr2.pas` (+`.ref`) as a gated corpus probe and re-run
M3+M4. This is a `pascal.y`-only fix (frontend type tracking) → lower cross-language risk, but bison regen +
recompile of `pascal.tab.o` + `libscrip_rt` rebuild are required (landmines #2/#4).

## Artifacts (all in /tmp, ephemeral)
- `/tmp/pint7/ptr2.pas` — the decisive store-vs-read discriminator (KEEP; becomes the gated probe).
- `/tmp/pint7/ptr1.pas` — first reduced repro (chained deref via arr^.inx^.form).
- `/tmp/pint7/t_sz.pas`, `t_arr2.pas`, `t_off.pas` — pcom-level array-size symptom probes.
- `/tmp/pint7/pcom_dbg{2..6}.pas` — instrumented pcom copies (NOT the corpus oracle; corpus untouched).
- `/tmp/p4o/pcom`, `/tmp/p4o/pint` — native fpc-3.2.2 oracle binaries (`fpc -Mtp`).

## Also flagged (unexplained, non-blocking)
On `git status` early in this session, `src/lower/lower_pascal.c` showed the `pas_is_agg_local` line (81)
DELETED in the working tree (mtime 14:56, during the session) with `scrip` rebuilt at 14:58 — an edit I did
not make; reflog shows HEAD never moved. Saved to `/tmp/lower_pascal.LINEDELETED.c`, restored to HEAD, rebuilt
clean, and all findings above re-verified on the clean-HEAD build. If a parallel session touched it, that
explains it; otherwise worth a look. (Interestingly, that deletion is roughly the change the prior finding
proposed — but per the repro above it does NOT fix the real bug, since `ptr2.pas` still diverges on clean HEAD.)
