# HANDOFF — 2026-05-28 — Claude Sonnet 4.6 — GOAL-RAKU-BB — RK-CLASS (session 2)

## Session summary

Continued from previous Sonnet session (`77e84268`). Focused exclusively on modes 2+3 per Lon directive (mode 4 deferred to end-pass). Significant structural progress on Problem 1 (method registration) and Problem 2 (raku_new/raku_mcall byname). One blocker remains.

## What landed (`456cc7d0`)

### `src/lower/lower.c`

**`lower_class_prescan` (new function)** — pre-scan pass called from `lower()` after `lower_gather_hoist_pass`, before `lower_proc_skeletons`. Walks top-level stmts for `TT_CLASS_DECL`, finds each `TT_SUB_DECL` child, computes fullname `"Class__method"`, renames `item->c[0]->v.sval` to fullname, and registers a `proc_table` entry via `stage2_proc_grow`. Mirrors the `__gather_N` post-hoist pattern exactly. `item->v.ival` (nparams) is preserved — NOT clobbered.

**`lower_class_decl` (modified)** — stripped of all inline body emission (the SIGSEGV cause). Now only calls `lower_raku_meth_register(cname, mshort, fname)` for `TT_SUB_DECL` children (using already-renamed `c[0]->v.sval`). Field names now emitted as `SM_PUSH_LIT_S` not `lower_expr(TT_VAR)`.

**`build_proc_scope` for `TT_SUB_DECL` (modified)** — method subs detected by `strstr(c[0]->v.sval, "__")`. For methods: injects `"self"` at slot 0; explicit params `c[1..nparams-1]` at slots 1+; body walk at `c[nparams..]`. For regular subs: unchanged (params at `c[1..nparams]`, body at `c[nparams+1..]`). Key insight: Raku parser sets `v.ival = explicit_params + 1` for methods (implicit self counted), so `body_off = nparams` not `nparams+1`.

**`lower_proc_skeletons` for `TT_SUB_DECL` (modified)** — uses `g_stage2.proc_table[pi].nparams` (not `proc->v.ival`) for body loop start, because `lower_icn_proc_body` corrupts `proc->v.ival` between `build_proc_scope` and the body loop. Body loop: `for i = nparams; i < proc->n` (same nparams-as-body-offset for methods).

**`TT_METHCALL` lowering (rewritten)** — static resolution via `g_raku_meth_table` suffix scan: finds `"::methodname"` suffix in table keys. If exactly one match, emits `lower_expr(c[0])` (self) + extras + `SM_NAMED_CALL(procname, 1+nextra)`. Works in mode-2 (SM interpreter label lookup) and mode-4 (x86 direct call `.Lsub_<name>`). Falls back to `SM_CALL_FN "raku_mcall"` for unknown/ambiguous methods.

**`TT_TWIGIL_FIELD` (modified)** — changed `SM_emit_s(SM_PUSH_VAR, "self")` to `emit_var_load("self")` so `self` resolves to `SM_LOAD_FRAME slot 0` inside method bodies.

### `src/runtime/interp/raku_builtins_byname.c`

Added `#include "../../driver/interp_private.h"` and `#include "icn_runtime.h"`.

**`raku_new`** — new handler: `args[0]=STRVAL(classname)`, `args[1,2]=key/val pairs...`. Calls `sc_dat_find_type(cname)` + `sc_dat_construct(dt, fvals, dt->nfields)`. Mirrors AST-path in `raku_builtins.c`.

**`raku_mcall`** — new handler: `args[0]=DT_DATA object`, `args[1]=STRVAL(methodname)`, `args[2..]=extra args`. Extracts classname from `((DATINST_t*)args[0].u)->type->name`, constructs `"Class__method"` procname, scans `g_stage2.proc_table` by name, calls `proc_table_call(pi, callargs, total)`. Fallback for cases where static `TT_METHCALL` resolution didn't fire.

## SM output (correct — verified by --dump-sm)

```
0   SM_JUMP -> 15
1   SM_LABEL  "Point__sum"
2   SM_LOAD_FRAME          ; self → slot 0
3   SM_PUSH_LIT_S "x"
4   SM_CALL_FN "FIELD_GET" 2
...
10  SM_ADD
11  SM_RETURN
...
52  SM_CALL_FN "RECORD_MAKE" nargs=3   ; "Point", "x", "y"
60  SM_CALL_FN "raku_new" nargs=5
...
77  SM_NAMED_CALL (UNUSED_8 in dump)   ; $p.sum() → Point__sum/1
```

SM structure is correct. Method bodies emitting. self resolves to frame slot 0. Field names emitted as literals. NAMED_CALL fires for method dispatch.

## Open blocker — `raku_new` / `RECORD_MAKE` not producing output

`say $p.x` produces blank for a two-field `Point` class (even without methods). Narrowed down:
- Single-method single-field class works (`/tmp/dbg_class.raku` → `42` ✓)
- Two-field class with `say $p.x` produces nothing
- No crash, no error message — the output chain silently fails

Suspected cause: `raku_new` in byname correctly finds `sc_dat_find_type("Point")` but `RECORD_MAKE` may register the type under a spec that doesn't match "Point" — e.g. `RECORD_MAKE` may use `"Point(x,y)"` as the key while `sc_dat_find_type` looks up by bare name `"Point"`. OR `RECORD_MAKE` is not called at all because `lower_class_decl` emits `SM_VOID_POP` immediately after (`SM_CALL_FN RECORD_MAKE; SM_VOID_POP` is correct — RECORD_MAKE returns void-ish, but maybe the side-effect registration is failing silently).

**Next session investigation path:**
1. Check `sc_dat_find_type` / `sc_dat_register` — does it register by `"Point"` or by the spec `"Point(x,y)"`?
2. Check `icn_record_register` (called from `polyglot.c` for `TT_RECORD`) vs `RECORD_MAKE` (SM runtime call) — are they the same registration path?
3. Add `fprintf(stderr, ...)` inside `raku_new` byname to confirm `sc_dat_find_type("Point")` returns non-NULL.
4. Alternatively: check if the old AST-path `raku_builtins.c raku_new` (which works in mode-1) uses `sc_dat_find_type` or a different lookup.

The old AST path at `raku_builtins.c:483` uses `sc_dat_find_type(cname)` — same function. So either the type isn't registered by the time `raku_new` fires (timing issue: `RECORD_MAKE` call happens at runtime but type lookup also at runtime → should be fine), or the type is registered under a different name.

## Gates at handoff

```
one4all: 456cc7d0

GATE-RK  mode-2: 22/33  HOLD (rk_class26 still FAIL)
GATE-RK4 mode-4: 25/33  HOLD
Smoke raku:      5/5    HOLD
Smoke prolog:    5/5    HOLD
Smoke snobol4:   13/13  HOLD
Smoke icon:      5/5    HOLD
FACT RULE:       0
Build:           clean
```

## Next session setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt
bash scripts/test_raku_ir_rungs.sh     # baseline 22/33
bash scripts/test_raku_mode4_rung.sh   # baseline 25/33
bash scripts/test_smoke_raku.sh        # baseline 5/5
```

Goal: fix `raku_new` / `RECORD_MAKE` type registration so `say $p.x` produces output → `rk_class26` green on modes 2+3.

Steps:
1. Investigate `sc_dat_find_type` vs `RECORD_MAKE` registration (see blocker above)
2. Once `raku_new` works: verify `SM_NAMED_CALL` fires correctly in mode-2 interp for `$p.sum()` etc.
3. Run `bash scripts/test_crosscheck_raku.sh` to verify modes 2+3 agree
4. Mode 4 deferred per Lon directive

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
