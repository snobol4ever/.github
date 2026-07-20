# FINDING 2026-07-20 — ICN-LOCAL-SHADOW: declared local shadows record-field-accessor in IR_VAR→IR_PROC_VALUE rewrite

Session (Lon: "get JCON compiler self-hosting under SCRIP"). Base SCRIP `974bed29`.
SCRIP `37c45277`. Icon 241/20/32, zero regression (stash/rebuild/diff, FAIL set byte-identical, same 20 names).
Icon smoke 14/14 both modes. Gates no_stack/one_reg/semicolon PASS.

## PRIOR FINDING'S MIS-DIAGNOSIS — CORRECTED

FINDING-2026-07-19-CLAUDE-JCON-SELFHOST-FOUR-RESUME-FIXES-AND-LOCAL-VS-FIELD-COLLISION-BLOCKER.md
stated: "is_global("a") is TRUE (field accessor)" and pointed at the emitter's
`IR_VAR` gate (`is_global && !graph_has_local`) and the slot-grant in `zeta_storage.c`
as the fix location. Instrumentation this session proved BOTH claims wrong:

1. `is_global("a") == 0` — the field accessor `a` is NOT in the global table.
2. No `IR_VAR` node named `a` reaches the emitter or slot-grant at all — it is
   rewritten to `IR_PROC_VALUE` upstream in the LOWER pass.
3. `graph_has_local(g, "a") == 1` at every site — the declared local IS correctly
   in lnames; the gate function works fine.

## TRUE ROOT CAUSE — `lower_icon_resolve_call_kinds()` misses declared locals

`lower_icon_resolve_call_kinds()` (`src/lower/lower_icon.c` ~1379) walks every
`IR_VAR` node in every graph and rewrites it to `IR_PROC_VALUE` when the name is
a known proc/builtin/record-field-accessor. Its local-shadow guard:

```c
// checked: params (pnames) and assignment targets (IR_ASSIGN / IR_REV_ASSIGN)
// MISSING: declared locals (lnames / graph_has_local)
```

A record field like `a` (from `record u_cset(a)` in `gen_ucode.icn`) makes
`rt_builtin_is_known("a")` return 1 via `rt_dat_field_of_any()` at
`by_name_dispatch.c:266`. So a declared-but-UNASSIGNED local `a` — which has no
`IR_ASSIGN` node, so the assignment-target scan misses it — was rewritten from
`IR_VAR "a"` to `IR_PROC_VALUE "a"` → the field-accessor function value.

Consequence: `type(a)=="function"`, `image(a)=="function a"`, `\a` wrongly
succeeds and clobbers `ret := \a` in `parse_expr3`, which was the ast2ir blocker.

MINIMAL REPRO (`/tmp/fieldcol.icn`, confirmed both before and after fix):
```icon
record u_cset(a);
procedure main();
  local ret, a;
  ret := "realvalue";
  write("type(a)=", type(a));    # was: function  now: null
  write("image(a)=", image(a));  # was: function a  now: &null
  if \a then write("BUG") else write("OK");  # was: BUG  now: OK
  ret := \a;
  write("ret=", ret);            # was: EXPRESSION  now: realvalue
end
```

## INSTRUMENTATION PATH (how the root cause was found)

1. Added `SCRIP_DBG_LNAMES` print after lnames collection (lower_icon.c ~1321):
   → `[LNAMES] proc bb_idx=0 nlocals=2: ret a` — local `a` IS in lnames. Gate not here.

2. Added `SCRIP_DBG_VAR` print at `emit.cpp` IR_VAR dispatch (~782):
   → Only `ret` appeared — NO `IR_VAR` for `a` was driven at emit time.
   The node doesn't exist at emit time; it was rewritten upstream.

3. Added `SCRIP_DBG_SLOT` print at `zeta_storage.c:327` slot-grant gate:
   → Only `ret` appeared — `a` was never seen as an IR_VAR/IR_ASSIGN node.

4. Added `SCRIP_DBG_PV` at `lower_icon_resolve_call_kinds()` before and after the
   `is_global` guard:
   → `[PV-TOP] vn=a is_global=0 has_local=1 nlocals=2`
   → `[PV] vn=a is_global=0 isproc=0 builtin_known=1 has_local=1 nlocals=2`
   Land mine: `builtin_known=1` via `rt_dat_field_of_any("a")` and `is_global=0`
   (field-accessor is NOT in the global table) so the `is_global` guard at line 1384
   does NOT skip it, and `graph_has_local` was never consulted for the shadow check.

## THE FIX — one line in lower_icon_resolve_call_kinds()

```c
// BEFORE (after is_global guard):
int skip = 0;
for (int k = 0; !skip && g->pnames ...) ...params...
for (int k = 0; !skip && k < g->n; k++) ...IR_ASSIGN...

// AFTER: add this line between is_global guard and skip block:
if (graph_has_local(g, vn)) continue;
```

Canonical Icon scoping: a name declared `local` (or param) in a procedure always
shadows any global/builtin/field-accessor. Verified against JCON `irgen.icn`
`ir_a_Ident` — emits a plain by-name `ir_Var`; scope resolution against the
procedure's own local set is entirely the backend's job.

## VERIFICATION

- Repro after fix: `type(a)=null` `image(a)=&null` `\a` fails, `ret=realvalue` — m3 AND m4.
- Multi-field: `record u_str(n,a)` + `record thing(s)` + locals `n,a,s` all string-typed. ✓
- Assigned-local-over-field: `a := box(42); type(a)=="box"; a.a==42` — field access through
  a local still works correctly. ✓
- Zero regression: stash/rebuild/diff FAIL sets byte-identical (241/20/32, same 20 names). ✓
- Icon smoke 14/14 m3+m4 (libscrip_rt.so built this session). ✓
- no_stack / one_reg_frame / semicolon gates PASS. ✓

## JCON SELF-HOST STATUS AFTER THIS FIX

ast2ir blocker CLEARED. The collision that caused `parse_expr3`'s local `a` to
read as `function a` (field accessor from `gen_ucode.icn record u_cset(a)`) is
fixed. All single-char field names (`a`, `n`, `s` from gen_ucode records) now
correctly shadow their field-accessor builtins when declared as locals.

STILL OPEN (from prior cursor):
- `type()`/`image()` for record CONSTRUCTORS and builtins return `"function"`/
  `"function <n>"` instead of `"procedure"`/`"record constructor <n>"`.
  `by_name_dispatch.c` type() DT_E branch defaults "function" and only upgrades
  named user procs; record-constructor and builtin values need upgrading.
- Pipeline next: build 17-module jtran → run ast2ir on hello_t.icn → confirm
  `ir_Function` → bc_File → .u1/.u2 → jlink → run → byte-compare → benchmark.
- Pre-pinned regressions: geddump/tgrlink → `git revert 7aade169`; ipxref →
  LOWER-side lower_alt BFS ordering fix.

Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
