# FINDING 2026-07-21 — PAS-SELFHOST-3d RUNG 2: record/array-local collision FIXED

## Summary
Same-named **record / array LOCALS** declared in different (sibling) Pascal procedures
collapsed onto ONE program-global, name-keyed storage cell. A callee writing its own
local therefore clobbered the caller's identically-named local. Scalars were unaffected
because scalar locals live in per-activation frame slots. Fixed with per-proc name
qualification of aggregate locals, mirroring the already-proven captured-scalar mangle.

M3 146/0 · M4 146/0 · SN4/ICN/PL/RK smokes green. Pascal-only edit (no shared emit).

## Repro (SCRIP-only, no fpc needed)
- `rc.pas` — `rec` record local `lattr` in both `inner` and `outer`; `outer` sets
  `lattr.f:=5`, calls `inner` (which sets its own `lattr.f:=99`), then prints `lattr.f`.
  BEFORE: prints `99` (wrong — inner clobbered outer). AFTER: prints `5`.
- `sc.pas` — same shape with integer (scalar) locals. Prints `5` before and after
  (scalars already correct — the isolation control).
- `rcap.pas` — record local `lattr` in `outer`, written by NESTED `inner` (capture).
  Prints `7` before and after (intended Pascal sharing preserved).

Gated as `corpus/programs/pascal/rec_local_collision.pas` (+`.ref` = `5`, width-10).

## Root cause (confirmed by `scrip --dump-ast rc.pas`)
1. A record local is represented as a `TT_VAR <name>` whose storage is a runtime
   name-keyed cell; `lattr.f` is lowered at PARSE time to `TT_IDX(TT_VAR lattr, ILIT k)`
   (field index baked in — so field lookup does NOT depend on the storage name).
2. The `program:` main-hoist (`pascal.y:533`) walked ALL `g_pas_arrays[]` entries and
   emitted a one-time `mk_array_init` into `main` under the **bare** name — including
   proc-locals. The AST dump for `rc.pas` showed `main` receiving TWO
   `(TT_ASSIGN (TT_VAR lattr) …)` inits, one for each proc's local, both bare `lattr`.
3. Only *captured* scalars were per-proc mangled (`pas_resolve_name` →
   `__up_<proc>_<var>`). Aggregate locals were never mangled → every proc's `lattr`
   resolved to the single global `lattr` cell.

## Fix (Pascal-only, 3 sites; mirrors captured-scalar path)
- `src/parser/pascal/pascal.y`
  - Added `int is_local` to the `g_pas_arrays[]` struct; set `is_local=(g_pas_level>=2)`
    in `pas_array_add` / `pas_array_add2d` (a proc's decls parse with `g_pas_level>=2`;
    `pas_proc_enter` runs before the body). Params (`pas_array_add2d_param`) stay
    `is_local=0`. Record locals already flow through `pas_array_add` (pascal.y:631), so
    they are covered too.
  - Added exported predicate `int pas_is_agg_local(const char *name)` → 1 iff `name` is a
    non-param, `is_local` entry in `g_pas_arrays[]`.
  - Main-hoist (`pascal.y:533`): now skips `is_local` entries. `mk_proc` (pascal.y:200)
    already emits a per-proc `mk_array_init` for each proc-local array, so the per-proc
    init still happens — under the (now mangled) reference name.
- `src/lower/lower_pascal.c`
  - `pas_resolve_name`: after the captured-scalar branch, added a branch that, when the
    name resolves to a local slot in a real (non-`main`) proc scope AND
    `pas_is_agg_local(name)`, returns `pas_cap_mangle(found_sc->proc_name, name)` and
    registers it as a global. The mangle keys on the **declaring scope's** proc_name.

### Why the declaring-scope key is correct for BOTH cases
- Sibling collision: `inner` and `outer` each own a `lattr`; each resolves in its own
  scope → `__up_inner_lattr` vs `__up_outer_lattr` → distinct cells. ✓
- Capture: nested `inner` reading `outer`'s `lattr` resolves the name by walking to the
  OUTER scope (`inner` has no such local) → both writer and owner key on `outer` →
  `__up_outer_lattr` → same cell → intended Pascal sharing. ✓

## Build / verify recipe used
```
cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y
cd $ROOT && rm -f scrip out/pascal.tab.o out/lower_pascal.o && make -j4 scrip
make libscrip_rt                      # 176 MB .so, M4 links it
bash /tmp/run_gate_m3.sh              # 146/0
bash /tmp/run_gate_m4.sh              # 146/0  (gcc -no-pie … -lscrip_rt -lm, NO -lgc)
```
Files compile as C (gcc, CBASE, no -std=c++17) → `pas_is_agg_local` uses plain C linkage
(no `extern "C"`), matching the existing `global_register`/`record_register` externs.

## pcom impact / next rung
This closes the record-local clobber that hit pcom's `assignment` procedure
(`comp.p:3120`, `lattr := gattr` — a record-valued local copied from the global `gattr`,
then clobbered across the `expression(fsys)` sub-call). RUNG 3: re-run pcom on a single
real assignment (`l_var1.pas`) and confirm the dropped store op (`sroi 9`) now emits;
if not, monitor→bracket the next divergence.
