# FINDING 2026-07-21 — PAS-SELFHOST-3d: searchid stall was a CAPTURED-VAR-BY-REF bug (FIXED); next blocker is RECORD/ARRAY LOCALS SHARE ONE GLOBAL CELL

**Author:** Claude (session 2026-07-21). **Status:** RUNG 1 FIXED + M3 145/0 (no regressions, 4 sibling langs green). RUNG 2 BRACKETED with a 4-line minimal repro, NO CODE LANDED for it.

## RUNG 1 — searchid stall — ROOT FOUND AND FIXED (corrects the 2026-07-20 FINDING)

The 2026-07-20 doc concluded the searchid stall was "a field-layout / per-scope record-decode divergence; pointer VALUE survives (`@@ST-NIL=0`)." **That was wrong.** The pointer value does NOT survive — the by-ref writeback of the handle is lost.

MEASURED (minimally-instrumented real pcom, `##SIDW`/`##CALLR` = ord(lcp) handle):
```
##SIDW h=55      <- inside searchid at label 1, fcp:=lcp writes handle 55 for i
##CALLR h=       <- back in statement's ident case, lcp reads BLANK (not 55)
```
gdb confirmed searchid's writeback DOES fire `rt_assign_var(var.slen=1, var.ptr=0x…33f0, val.i=55)` — it writes 55 through a raw stack pointer. But `statement` reads its `lcp` from a DIFFERENT cell → blank.

ROOT: `lcp` is a **captured variable** in `statement` (nested proc `forstatement` at pcom.pas:3327 references it), so SCRIP rewrites every read/write of `lcp` to a mangled capture-global (`__up_statement_lcp`) with prologue/epilogue save/restore, abandoning the frame slot. The zeta dump shows both cells: `__upsv_statement_lcp` at +5984 and `lcp` at +6000. BUT `pas_call_args_brm` (`lower_pascal.c:213-214`) built the by-ref `IR_VAR_REF` from the **raw name** (`args[k]->v.sval`), bypassing `pas_resolve_name` — so `searchid`'s `var fcp` got `&<frame slot lcp>` (+6000) while every read of `lcp` in the caller went to the capture-global. searchid writes 55 to the dead frame slot; caller reads the capture-global → blank.

MINIMAL REPRO (the prior sessions couldn't find it because the missing ingredient was **a captured local passed BY REFERENCE**): `/tmp/p4boot/cap.pas` — `stmt` has local `lcp` captured by nested `inner`; `stmt` calls `sid(var fcp)` passing `lcp` by ref; before fix `handle=0 klass=48`, after fix `handle=1 klass=9`.

FIX (2 lines, `lower_pascal.c` `pas_call_args_brm`): resolve the by-ref actual through `pas_resolve_name` so a captured var's by-ref references its mangled capture-global cell.
```c
int _brslot = -1; const char * _brn = pas_resolve_name(cx, args[k]->v.sval, &_brslot);
IR_t * vr = build(cx, IR_VAR_REF, (k == nargs - 1) ? call : NULL, ω); IR_LIT(vr).sval = _brn;
```
VERIFIED: **Pascal M3 145/0** (recreated gate at `/tmp/run_gate_m3.sh`); SNOBOL4/Icon/Prolog smokes green. pcom on `program t; var i:integer; begin i:=5 end.` went from a 40-byte stall to 147 bytes — now emits `ldci 5`, `retp`, correct labels `l 4=10`/`l 5=6`, full trailer. Only ONE op still missing vs native (see RUNG 2).

## RUNG 2 — the remaining `sroi 9` gap — BRACKETED (record/array locals share ONE global cell)

pcom var1 now differs from native by exactly one line: native emits `sroi 9` (store 5 into i@9); SCRIP drops it. TRACE (instrumented pcom):
```
##L0=0   after  lattr := gattr        (lattr.typtr non-nil)
##L1=0   after  insymbol              (still fine)
##L2=1   after  expression(fsys)      (lattr.typtr CLOBBERED to nil)
```
So `assignment`'s guard `(lattr.typtr<>nil) and (gattr.typtr<>nil)` is false → `store(lattr)` never called → no `sroi`. `lattr` (a local `attr` RECORD) is clobbered by the nested `expression(fsys)` call.

ROOT (measured, gdb + asm + IR dump): **record/array LOCALS are stored as program-global name-keyed cells, so same-named record/array locals in different procs share ONE cell and clobber each other across calls.**
- 4-LINE MINIMAL REPRO (`/tmp/p4boot/rc.pas`): `inner` and `asg` each declare `var r: rec`; `asg` sets `r.a:=5`, calls `inner` (which sets its `r.a:=99`), then reads `r.a` → prints **99** (native: 5). Scalar same-named locals do NOT collide (`sc.pas` → 5 correct). Only records/arrays collide.
- MECHANISM: `pas_array_add` (records go through it too, `pascal.y:631`) registers every array/record local by BARE NAME in the global `g_pas_arrays[]`; `program:` (`pascal.y:531-537`) hoists a `<name> := init` for every one into MAIN's body; reads/writes in each proc use the bare name. gdb: `r`'s init lowers in `main` where `scope_slot(main,"r")=-1` (main is level<2, `pas_local_add` skips it), so `lower_assign_var` (`lower_pascal.c:108`) calls `pas_reg_var("r")` → `r` is `is_global`. Pascal never populates `g->lnames`, so `graph_has_local` is ALWAYS 0 for Pascal → `IR_VAR`/`IR_ASSIGN` for `r` take the GVA global path (`emit.cpp:794/810`). asm of `rc.pas` confirms: `r` accessed via `rt_gva_island` + `.Lgvan0:.string "r"` in BOTH procs = same cell.
- Whole-record COPY is fine in isolation (`reccopy.pas` passes); the bug is purely the shared-cell aliasing between same-named record locals of different procs.

WHY IT SURFACED NOW: before RUNG 1, pcom stalled inside searchid and never reached `assignment`. RUNG 1 unblocked control flow far enough to expose this pre-existing record-storage defect. pcom uses same-named record locals pervasively (`lattr`, `lcp`, `lsp`, `lattr` in simpleexpression/term/factor/assignment) so this blocks self-hosting broadly.

## FIX DIRECTION for RUNG 2 (next session — NON-TRIVIAL, plan before coding)

Record/array LOCALS of real procs (level>=2) must get per-proc-unique storage. Options, cleanest first:
1. **Per-proc name qualification.** Give each record/array local a proc-qualified storage name (mirror the existing capture-mangle `__up_<proc>_<var>` scheme). Must be threaded consistently through: (a) `pas_array_add`/`pas_recvar_add`/`pas_chararr_add` at decl, (b) the main-hoist `program:` block (`pascal.y:533` — should NOT hoist proc-locals into main; `mk_proc:200` already emits a per-proc init in the owning body), (c) EVERY reference path — but note reads/writes/field-ops/`with`/by-ref all already funnel through `lower_var`/`lower_assign_var` → `pas_resolve_name`, so qualifying there (like captures) may suffice for the body; the decl-table + init-hoist are the parser-side halves that must agree. Current-proc identity at `var_decl` time: use a counter captured in `pas_proc_enter` (procs are named at the END of their production, so a numeric proc-id is the handle available mid-body).
2. Populate Pascal `g->lnames` (like `lower_icon.c:1321`) so `graph_has_local` is real, THEN make record/array locals true frame cells — larger, changes storage model.

GATING REQUIRED (RULES.md Landmine #2/#6): editing `pascal.y` needs `bison -d -o pascal.tab.c pascal.y` + `rm -f scrip && make` (the `.tab.o` goes stale otherwise); re-run M3+M4 (145/0) and, if any shared emit/lower file is touched, all four sibling language gates.

## ENV / REPRO
- Symlinks `/home/claude/{SCRIP,corpus,.github}`. `scrip` built (searchid fix in tree). fpc oracle in `/tmp/p4boot` (pcom native built).
- pcom pipeline: `./pcom < prog.pas` writes P-code to file `prr` in cwd (stdout is the LISTING). SCRIP same: `scrip --run pcom.pas < prog.pas` → `./prr`.
- Repro inputs: `/tmp/p4boot/l_var1.pas` (`var i:integer; begin i:=5`), `l_empty.pas` (self-hosts, `diff -w` clean). Minimal RUNG-2 repro: `/tmp/p4boot/rc.pas` (records collide), `sc.pas` (scalars don't), `reccopy.pas` (copy is fine), `cap.pas` (RUNG-1 fixed).
- Native oracles: `/tmp/nat_var1.prr` (138 B, has `sroi 9`), `/tmp/nat_empty.prr` (112 B).
- M3 gate: `bash /tmp/run_gate_m3.sh` → `M3: 145/0`.

## LANDED THIS SESSION
- `src/lower/lower_pascal.c` `pas_call_args_brm`: by-ref actual resolved through `pas_resolve_name` (RUNG 1 fix). M3 145/0, siblings green. NOT YET PUSHED (awaiting credential).
