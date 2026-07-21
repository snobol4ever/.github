# FINDING: ICN-CDIFF-FIX — cset-diff/union/inter eager-coercion abort + bc_File advance to .class output

**Date:** 2026-07-21
**Author:** Claude Sonnet 4.6
**Commit:** (see ICN-CDIFF-FIX in SCRIP)
**Status:** CLOSED — bc_File produces `.class` files for hello_t.icn

---

## Summary

Two blockers diagnosed and one fixed this session, advancing the JCON self-host pipeline from
ast2ir output to full bc_File `.class` emission.

---

## Blocker 1 (FIXED): bc_File — Error 1 "Illegal data type" in rt_num_arith

### Symptom
Running `jtran preproc hello_t.icn : yylex : parse : ast2ir : bc_File` exited rc=1 with:
```
** Error 1 in statement 0
   Illegal data type
```

### Diagnosis
gdb backtrace:
```
core_runtime_error(code=1) ← to_real(v) ← rt_num_arith_impl(op=20=BINOP_CDIFF)
```

Root cause in `src/runtime/arithmetic.c:223` — `rt_num_arith_impl` ran `to_real(a)` and
`to_int(a)` **eagerly and unconditionally** before the switch, including for cset ops
(CUNION/CDIFF/CINTER). When a cset operand arrives as `DT_C` (actual cset descriptor),
`to_real()` hits the default branch and calls `core_runtime_error(1, NULL)` — before the
CDIFF branch at line 232 (which handles csets via string extraction) is ever reached.

The bug was latent in m3 (interpreter): `rt_num_arith`'s setjmp wrapper at line 211 caught
the Error 1 and returned FAILDESCR, which masked the abort in casual testing. In m4/jtran
(compiled path, different error-recovery context), the abort was fatal.

### Fix
`src/runtime/arithmetic.c`, two lines:
```c
// Before:
double ld = to_real(a), rd = to_real(b);
int64_t li = to_int(a),  ri = to_int(b);

// After:
double ld = csop ? 0.0 : to_real(a), rd = csop ? 0.0 : to_real(b);
int64_t li = csop ? 0   : to_int(a),  ri = csop ? 0   : to_int(b);
```
`csop` is defined two lines above: `int csop = (op==BINOP_CUNION||op==BINOP_CDIFF||op==BINOP_CINTER);`
The CDIFF/CUNION/CINTER branch computes from string forms and never uses ld/rd/li/ri.

### Verification
- Oracle (icont): `'abcdef' -- 'cd'` → `'abef'`, `'abc' ++ 'cde'` → `'abcde'`, `'abcdef' ** 'cdef'` → `'cdef'`
- SCRIP after fix: identical output on all three
- Icon smoke: 14/14 both modes (no regression)
- rung suite: 240/21/32 (unchanged from this-sandbox environmental baseline; rung37/rung17 real-formatting drift is pre-existing and unrelated — confirmed by A/B: rung37 produced `2.` both before and after the fix)

### bc_File result after fix
```
$ SCRIP_BETA_ELIDE_OFF=1 ./jtran preproc hello_t.icn : yylex : parse : ast2ir : bc_File \
    -O -class:lhello_t -dir:./tmp/
$ ls tmp/
lhello_t.class   links   p_lhello_t$main.class
```
rc=0, empty stderr. **JVM bytecode produced for hello_t.icn.**

---

## Blocker 2 (DIAGNOSED, non-blocking): symbolic_File — Error 5 "Undefined function or operation"

### Symptom
`jtran ... : ast2ir : symbolic_File` printed the function header then died:
```
procedure main( )
local
static
** Error 5 in statement 0
   Undefined function or operation
```

### Diagnosis
gdb backtrace:
```
core_runtime_error(5) ← APPLY_fn(name="name", nargs=1) ← rt_call_arr_impl
```

`dump_get_names` (dump.icn:25) calls `name(!x)` on each record to retrieve field names.
SCRIP has no `name()` builtin registered in `by_name_dispatch.c`.

Deeper issue: canonical Icon declares `name(underef v)` — the argument is passed without
dereferencing (lvalue semantics). But SCRIP's `!record` in this call context delivers the
**dereferenced field value** (DT_I integer), not a variable reference. Confirmed via probe:
`name(!pt(3,4))` arrives with descriptor `{v=DT_I, i=3}`, not a NAMETRAP/VCELL.

Oracle: `name(!pt(3,4))` → `pt.x`, `pt.y` (format: `recordname.fieldname`).

### Status
**Non-blocking for the self-host goal** — `symbolic_File` is a debug IR dump stage;
`bc_File` (the real bytecode generator) does not use `name()` at all. This blocker only
matters if we want the human-readable symbolic IR dump working.

Fix requires two parts:
1. Add `name()` builtin to `by_name_dispatch.c`
2. Ensure `!record` generators pass variable references (NAMETRAP/VCELL with field index)
   rather than dereferenced values when called in an `underef` context

---

## Pipeline state after this session

```
preproc   ✓
yylex     ✓
parse     ✓
ast2ir    ✓  (ICN-LOCAL-SHADOW fix, prior session)
bc_File   ✓  (ICN-CDIFF-FIX, this session) → lhello_t.class + p_lhello_t$main.class
jlink     NEXT
run       NEXT
```

---

## Next session

1. **jlink**: find/build jlink from jcon-master, link the `.class` files in `tmp/` into a
   runnable JCON bundle. Canonical jcon-master jlink lives at `refs/jcon-master/bin/jlink`
   (needs Java). Run with `java -jar jcon.zip lhello_t`.
2. **Byte-compare**: compare SCRIP-jtran `.class` output vs canonical icont→jtran `.class`
   for hello_t.icn.
3. **Three-way benchmark**: iconx / JCON-JVM / SCRIP-jtran on `irgen.icn` compile
   (the canonical bmark from jcon-master/tran/Makefile).
4. **rung suite regression hunt**: rung17/rung37 real-formatting `2.` vs `2.0` — trailing
   zero in real output. The `write(sqrt(4.0))` path: check `rt_real_to_str` / `real_str`
   for the `%g` vs `%.1f` format string. The prior sandbox had this right at 241/20/32.
5. **name() builtin**: implement for symbolic_File if needed.

---

## Environment notes

- SCRIP HEAD after commit: (ICN-CDIFF-FIX commit, see git log)
- `/home/claude/jt/`: workdir with all 17 modules, `jtran.s` (505K lines), `jtran` binary (5MB),
  `hello_t.icn`, `tmp/lhello_t.class`, `tmp/p_lhello_t$main.class`
- `/home/claude/work/icon-master/icon-master/bin/icont+iconx`: canonical oracle built this session
- libscrip_rt.so at `out/libscrip_rt.so` (rebuilt with CDIFF fix)
