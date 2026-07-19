# FINDING-2026-07-19-CLAUDE-PAS-SELFHOST-3B-NESTED-VP-WRITEBACK.md

## Summary

PAS-SELFHOST-3b: `var`-parameter write-back to a local of a nested procedure is silently lost under SCRIP. The global side-effect of the callee executes; only the by-reference write to the nested frame cell fails. Both M3 and M4 reproduce identically → lowering bug in `lower_pascal.c`, not emit/templates.

## Trigger condition (measured)

Callee at outer/sibling lexical level takes a `var` integer parameter. Caller is a nested procedure. Actual argument is a local variable of that nested procedure. On return from callee, the local reads blank (uninitialized) instead of the written value.

## Minimal repro — `corpus/programs/pascal/nested_vp_writeback.pas`

```pascal
program t;
var glob : integer;
procedure setit(var nxt: integer);
begin glob := glob + 1; nxt := glob end;
procedure body;
  var seg : integer;
begin setit(seg); writeln('seg=', seg:1, ' glob=', glob:1) end;
begin glob := 0; body end.
```

Native (fpc): `seg=1 glob=1`
SCRIP M3/M4: `seg=  glob=1`

The global `glob` advances correctly; only `seg` (the nested-proc local passed by reference) stays blank.

## How it was found (pcom instrumentation)

Running SCRIP-pcom vs native-pcom on an empty program (`program t; begin end.`) showed SCRIP's P-code with blank label numbers: `ent   1   l    ` vs native `ent   1   l   4`. A three-probe campaign:

1. **Probe 1** (after `genlabel(entname); genlabel(segsize); genlabel(stacktop)` in `body`): native `PROBE seg=4 stk=5 ent=3`; SCRIP `PROBE seg=  stk=  ent=`. Values blank immediately after the `genlabel` calls.
2. **Probe 2** (inside `genlabel`, after `nxtlab := intlabel`): SCRIP `GENLAB intlabel=3 nxtlab=3` / `4` / `5` — values correct INSIDE `genlabel`.
3. **Probe 3** (probe 1 + print `intlabel` global): both native and SCRIP `GLOB intlabel=5` — global advanced correctly in both engines.

Bracket: write-back is correct at the callee write site; value is lost in the caller's frame before the caller reads it back. All three `genlabel` calls executed (intlabel=5 in both). Only the var-param destinations (`body`'s locals) failed to receive the written values under SCRIP.

The isolated `r_genlab.pas` repro (globals as var-arg targets) passed — confirming the bug is specific to nested-procedure locals as var-param targets, not var-params in general.

## Locus

`lower_pascal.c:213-215` (`pas_call_args_brm`): a `var`-param arg that is a plain `TT_VAR` not already byref builds `IR_VAR_REF` with the plain unmangled name. Suspected: `IR_VAR_REF` address resolution does not account for the nesting level of the actual argument's owning scope — it produces an address into the wrong frame (e.g. the GVA slot for the name rather than the current nested activation's frame cell). Meanwhile the corresponding direct read (`IR_VAR seg` via `pas_resolve_name`) would resolve correctly because the nested-proc local is in-frame at the current display level. The address the callee writes through doesn't alias the cell the caller reads.

`IR_VAR_REF` emission: `emit.cpp:735` / `bb_var_ref.cpp:18` / `zeta_storage.c:326`. The fix likely lives in `pas_call_args_brm` or in `IR_VAR_REF`'s address-computation: when the var-param actual is a local of a nested proc (slot >= 0 in the innermost `pas_scope_t`), the ref must use the frame-relative address (`[rbp+slot*16]` style), not the GVA path.

## Gate status at session close

M3 143/0 · M4 143/0 (no code landed; baseline unchanged). `nested_vp_writeback.pas` added to corpus — currently a FAILING probe (not yet gated; do not add to gate until fixed).

## Next session

Read `IR_VAR_REF` handling in `emit.cpp:1030` and `zeta_storage.c:326`. Determine whether the fix is: (a) in `pas_call_args_brm` — check scope slot of the var-arg name and emit `IR_VAR_FRAME_REF` (frame-relative address) instead of `IR_VAR_REF` (GVA-path address) when the name resolves to a nested-proc slot; or (b) in `IR_VAR_REF` dispatch — make it scope-aware. Fix, re-run gate (M3 143/0 · M4 143/0), run four-language smokes, then add `nested_vp_writeback.ref` and gate the new probe. After that: re-drive SCRIP-pcom on the empty program and confirm label numbers land correctly, then climb toward `var i:integer;` and the full var-decl section.
