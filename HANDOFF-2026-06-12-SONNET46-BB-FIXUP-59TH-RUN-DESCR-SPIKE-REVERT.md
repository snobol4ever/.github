# HANDOFF — 2026-06-12 · 59th attended run (Sonnet 4.6)

## What landed
**NOTHING LANDED — design spike + revert. SCRIP stays at e3e2261.**

## What was attempted: bb_gvar_assign_descr.cpp

Attempted 3-file conversion:
- `bb_gvar_assign_descr.cpp`: removed 4 static helpers, replaced IF(MEDIUM_TEXT) head-wrapper, replaced 6 bypasses (x86_frame_load64×2, x86_frame_store64×2, x86_ro_load_q, x86_ro_seal_str) with x86() forms, added direct `[rip+__]` lea for the name string via bb_ls
- `emit_bb.c`: added IR_ASSIGN_DESCR case to bb_prepare (sets bb_ls = intern(sval))
- `emit_core.c`: added `bb_prepare(nd)` before `bb_gvar_assign_descr()` dispatch

**Built OK. m4 assembly produced `lea rdi, [rip + .S0]` with .S0 UNDEFINED → link failure.**

## Root cause: strtab-flush gap in Icon text-mode pipeline

`emit_intern_str(s)` returns `g_flat_intern_str(s)` — but `g_flat_intern_str` pointer is NEVER initialized (`lower_flat_set_intern_str` is declared, defined, but never called anywhere in the codebase). So `emit_intern_str` always returns NULL.

`bb_intern_into(buf, sval)` fallback: calls `strtab_label(buf, 64, sval)` → `strtab_intern(sval)` — this DOES add the string to the strtab table (generating `.S0` as the label name). BUT the strtab is flushed by `xa_emit_strtab_rodata()`, which IS called in the SNOBOL4 flat-chain pipeline but is NOT called in the Icon `--compile` (text-mode) pipeline.

The old `x86_ro_seal_str(0, dst_name())` bypassed this entirely by emitting the string INLINE in the .text section alongside the box blob (not via the strtab at all).

## Why the bypass is load-bearing

`x86_ro_seal_str` / `x86_ro_load_q` are the only mechanism that correctly handles inline string embedding for the Icon global-assign path. Until `xa_emit_strtab_rodata()` is wired into the Icon --compile pipeline (or a new x86() funnel form is added for inline-sealed strings), the bp=6 bypasses in bb_gvar_assign_descr.cpp cannot be removed without breaking the build.

## PIN required from Lon

Two canonical fix paths:
1. Wire `xa_emit_strtab_rodata()` into the Icon text-mode pipeline at the right flush point (probably in `scrip.c` or the Icon flat-chain driver, after box emission)
2. Add a new `x86("seal_str", ...)` / `x86("load_ro_str", ...)` dispatch pair to x86_asm.h that inlines the string equivalent to `x86_ro_seal_str` + `x86_ro_load_q` but through the funnel

Both are non-trivial infrastructure changes. **PIN NEEDED before next session attempts bb_gvar_assign_descr.**

## Current state
- SCRIP @ e3e2261 (gvar_assign_concat CLEAN; descr reverted; working tree clean)
- .github @ (this commit)
- GRAND: 1920 · FILES: 127/108 dirty/19 clean
- Gates: all at floors (sno m4 7/7 HARD verified post-revert)

## Next session
**Cursor: `bb_gvar_assign_descr.cpp [S]`**

Do NOT attempt conversion of bp=6 bypasses until Lon provides a PIN on the strtab-flush gap. Options on arrival:
1. **If Lon pins fix path 1 or 2**: implement the pipeline fix then convert the template
2. **If Lon says advance cursor**: skip descr (mark [S] in tracker), move to `bb_gvar_assign_lit_i.cpp` (TOTAL=8: mt=1 lv=0 rp=4 hc=2 sd=1 bp=0 — simpler, no bp issues)

Note: `bb_gvar_assign_lit_i.cpp`, `bb_gvar_assign_lit_s.cpp`, `bb_gvar_assign_var.cpp`, `bb_gvar_assign_call.cpp` are all in the same family and may share the same strtab-flush dependency for their own static helpers. Verify before assuming they're bp-clean.
