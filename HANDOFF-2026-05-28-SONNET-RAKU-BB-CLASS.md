# HANDOFF — 2026-05-28 — Claude Sonnet 4.6 — GOAL-RAKU-BB — RK-CLASS

## Session summary

Three rungs landed (all 3 modes verified), one rung partial.

### Completed

**RK-EXCEPTIONS** (SCRIP `ed6fec27`)
- `raku_exc_clear`, `raku_exc_check`, `raku_exc_get` added to `raku_builtins_byname.c` (were referenced in lower.c but never implemented in the rt path).
- `raku_die` replaced `snprintf` with SSE-safe `memcpy` (Q13a).
- `raku_try_hash_builtin`: added `args[0].v != DT_S && args[0].v != DT_SNUL` early-exit guard — was calling `VARVAL_fn(INTVAL)` → `snprintf` on garbage pointer → SIGSEGV whenever `say(int)` was called inside any sub with a `my`-decl.
- GATE-RK4 22→23.

**RK-IO** (SCRIP `753d85e2` + fixup `4b4e3a11`)
- `rk_fileio38`: `for lines($path) -> $line` was calling `lines` on every iteration (lowered as a generator loop). Added `TT_ITERATE(TT_FNC)` arm in `lower_every` — evaluates the call once into a fresh `__arr_N` temp, then routes through `lower_raku_iterate_arr` BB path. Guard: `strncmp(sval, "__gather_", 9) != 0` excludes `gather{}` which is a generator FNC.
- `rk_stdio39`: `raku_capture` returned `INTVAL` not `FHVAL` — fixed to `FHVAL(n)`. Added `fflush(stdout)` before non-stdout handle writes in both `write` (icn_runtime.c) and `raku_print_fh/say_fh` (raku_builtins_byname.c). `setvbuf(stdout, NULL, _IOLBF, 0)` added to both `rt_init` (mode-4) and `scrip.c` startup (modes 2+3). Runner updated to `2>&1`.
- GATE-RK4 23→25.

### Partial — RK-CLASS (SCRIP `77e84268`)

**What works:**
- `lower_field` fix: Raku `$p.x` parses as `TT_FIELD` with field name in `t->v.sval` (not `c[1]`). `ICN_FIELD_NAME` macro returns NULL for these nodes. Fixed `lower_field` to fall back to `t->v.sval`.

**Remaining blockers for `rk_class26`:**

**Problem 1 — Method bodies emitted inline in main (mode-4 segfault).**
`lower_class_decl` emits method bodies inline: `for (int j = nparams; j < item->n; j++) lower_expr(item->c[j])`. These land in `main`'s preamble before any label, execute as sequential code, hit `RETURN` (bare `ret`), pop garbage → SIGSEGV.

Fix needed: method `TT_SUB_DECL` nodes inside `TT_CLASS_DECL` must be registered in `g_stage2.proc_table` so `lower_proc_skeletons` emits them as proper named subs (`.Lsub_Point__sum:` etc.).

The `polyglot_init` scanner only walks top-level nodes — it doesn't recurse into `TT_CLASS_DECL` children. Two options:
- (a) Make `polyglot_init` recurse into `TT_CLASS_DECL` and register the `TT_SUB_DECL` children under their renamed fullname (`ClassName__methname`). The rename already happens in `lower_class_decl` via `lower_raku_meth_register`.
- (b) Register them in `lower_class_decl` itself (like `__gather_N` procs are registered after `polyglot_init` at line 2722). This is simpler. After the `snprintf(fullname, ...)` call, add a `stage2_proc_grow` entry with the renamed sub. The `item->c[0]->v.sval` rename to `fname` must happen BEFORE the `stage2_proc_grow` so `lower_proc_skeletons` sees the right name.

**Problem 2 — `raku_new` / `raku_mcall` missing from modes 2+3.**
Both exist only in the AST-based `raku_builtins.c` path (using `interp_eval`). The byname path (`raku_builtins_byname.c`) used by modes 2+3 and mode-4's `rt_call` has neither.

All needed symbols are in libscrip_rt:
- `sc_dat_find_type(cname)` → `ScDatType*`
- `sc_dat_construct(t, fvals, nfields)` → `DESCR_t`
- `raku_meth_lookup(classname, methname)` → `const char* procname`
- `proc_table_call(pi, args, nargs)` → `DESCR_t`
- `g_stage2.proc_table[pi].name` for index lookup

`raku_new` byname signature: `args[0]=STRVAL(classname), args[1..2i-1,2i]=key/value pairs (alternating)`.
`raku_mcall` byname signature: `args[0]=DT_DATA object, args[1]=STRVAL(methname), args[2..]=extra args`.

For `raku_mcall`: extract class name from `((DATINST_t*)args[0].u)->type->name`, call `raku_meth_lookup(cname, mname)` to get procname (e.g. `"Point__sum"`), find pi by scanning `g_stage2.proc_table`, build args array with `args[0]` (self) + extra args, call `proc_table_call(pi, callargs, total)`.

**Problem 3 — Mode-4 method dispatch.**
With Problem 1 fixed, method subs will be emitted as `.Lsub_Point__sum:` local labels. The `TT_METHCALL` lowering currently emits `raku_mcall` via `rt_call` — but `rt_call` can't jump to a local x86 label by name string.

Two options:
- (a) **Static resolution at lower time** (preferred): in `TT_METHCALL` lowering (lower.c:2388), check if `c[1]` is `TT_QLIT` and scan `g_raku_meth_table` for a match. If found and there's exactly one class with that method name, emit `lower_expr(c[0])` + `STORE_FRAME 0` (self) + `SM_NAMED_CALL(procname, nextra+1)`. This avoids any runtime dispatch.
- (b) **Runtime function-pointer table**: register a `void* meth_fptrs[MAX]` array at startup and look up by string. More complex.

Option (a) has a caveat: if two classes have a method with the same name, the lookup is ambiguous without type tracking. For `rk_class26` both classes have distinct method names so static resolution works. Lon to advise on the general case.

## Gates at handoff

```
SCRIP: RK-CLASS partial (lower_field fix; 77e84268)

GATE-RK4 mode-4: 25/33  HOLD (rk_class26 still FAIL)
GATE-RK  mode-2: 22/33  HOLD
Crosscheck:      37/37  HOLD (modes 2+3 agree)
Smoke raku:      5/5    HOLD
Smoke prolog:    5/5    HOLD
Smoke snobol4:   13/13  HOLD
Smoke icon:      5/5    HOLD
FACT RULE grep:  0
Build:           clean
```

## NEXT session setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip libscrip_rt
bash scripts/test_raku_mode4_rung.sh   # baseline 25/33
bash scripts/test_raku_ir_rungs.sh     # baseline 22/33
bash scripts/test_smoke_raku.sh        # baseline 5/5
bash scripts/test_crosscheck_raku.sh   # baseline 37/37
```

Goal: `rk_class26` PASS on all 3 modes. Steps:
1. Register method TT_SUB_DECLs in proc_table inside lower_class_decl (Problem 1).
2. Add raku_new + raku_mcall to raku_builtins_byname.c (Problem 2).
3. Static method resolution in TT_METHCALL lowering or confirm with Lon (Problem 3).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
