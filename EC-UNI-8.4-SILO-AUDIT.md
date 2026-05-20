# EC-UNI-8.4 silo audit — findings

**Date:** 2026-05-19 (Opus 4.7)
**Commit:** one4all `af370d45` (after EC-UNI-8.3 matrix gate PASS)

## Scope

After EC-UNI-8.3 established the per-fn matrix invariant (every template fn
carries an arm or n/a sentinel for each cell of the 5-backend × 2-mode
matrix), an audit was performed on emitter sources outside `SM_templates/`
and `BB_templates/` to find residual opcode-discriminating switches —
"silo" code that defeats the template architecture.

Search command:

```
grep -rn "switch.*->op\|switch (instr" src/emitter/ | grep -v _templates/
```

## Findings

10 hits, partitioned into three categories:

### A. Silo walkers (4) — EC-UNI-5 already moved bodies to templates, but
each walker has its own dispatch switch:

| File:Line | Function | Status |
|---|---|---|
| emit_core.c:1795 | `emit_jvm_one_instr` | per-op switch; arms call `sm_*` templates |
| emit_core.c:1964 | `emit_js_from_sm` | per-op switch; arms call `sm_*` templates |
| emit_core.c:2087 | `emit_net_from_sm` | per-op switch; arms call `sm_*` templates |
| emit_core.c:1500 | `emit_wasm_from_sm` | per-op switch; arms call `sm_*` templates |

These are the four backend-specific dispatch switches. EC-UNI-5 moved the
per-op *bodies* into SM_templates, but the four walker switches still exist
in parallel. EC-UNI-8.4-fix would collapse them into a single
`emit_sm_dispatch()` that all backends share — but this is essentially the
same target as EC-UNI-5 and is being addressed via the EC-UNI-3
feature-flagged unified-dispatch hook (in `dispatch_one_x86_text`, which
must be generalised to drive every backend, not just x86).

**Disposition:** OPEN — track as EC-UNI-8.4-fix or fold into EC-UNI-5
completion. Not blocking; the four switches are harmless today (correct
output, just LOC bloat).

### B. Legacy x86 walker (1) — EC-UNI-4 target:

| File:Line | Function | Status |
|---|---|---|
| emit_sm.c:3080 | `emit_walk_codegen` | the legacy x86 walker; EC-UNI-3 has wired a unified-dispatch hook ahead of it; EC-UNI-4 deletes it once beauty.sno byte-identity is proven |

**Disposition:** OPEN — explicitly deferred to EC-UNI-4. Beauty.sno gate
(EC-UNI-3-beauty) is the prerequisite.

### C. Whitelisted (5) — non-opcode-dispatch analysis passes:

| File:Line | Function | Justification |
|---|---|---|
| emit_sm.c:1249 | `strtab_collect` | WASM string-table analysis; reads opcode to find string literals |
| emit_sm.c:1269 | `strtab_collect` (2nd switch) | same fn; second pass over name literals |
| emit_sm.c:2331 | `emit_flat_invariant` | predicate that classifies opcodes into flat-eligible categories |
| emit_sm.c:2607 | `pattern_windows_collect` | analysis pass that finds SM_PAT_* spans in the program |
| emit_sm.c:2921 | `dispatch_one_x86_text` | THIS IS the EC-UNI-3 unified-dispatch hook (not a silo, intended endpoint) |

**Disposition:** PASS — these switches exist for non-emission reasons
(analysis, classification, the new unified-dispatch hook itself). They are
not dispatch-to-emission silos and should remain.

## Recommended action

1. **EC-UNI-3-beauty** first (close the EC-UNI-3 rung): prove byte-identity
   on beauty.sno with the unified-dispatch hook on. This is the prerequisite
   for everything downstream.

2. **EC-UNI-4** next: delete `emit_walk_codegen` (silo B, 1 switch).

3. **EC-UNI-8.4-fix** after: generalise `dispatch_one_x86_text` into
   `emit_sm_dispatch(SM_Program *, FILE *, bb_emit_mode_t)` that handles
   x86/JVM/JS/NET/WASM uniformly. Delete the four walker switches in
   category A. Net LOC savings estimated >500.

## Total silo count
- Today: 5 (Category A × 4 + Category B × 1)
- After EC-UNI-3-beauty + EC-UNI-4: 4 (Category A only)
- After EC-UNI-8.4-fix: 0

Whitelisted analysis switches (Category C) always remain.
