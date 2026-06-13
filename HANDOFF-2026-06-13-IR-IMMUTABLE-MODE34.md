# HANDOFF — IR-IMMUTABLE rule (CORRECTED understanding)

## RETRACTION
An earlier version of this doc (and SCRIP commit `e50b089`) misread the rule and bombed the mode-3/4
emitter at its entry, disabling native codegen. **That was wrong and has been reverted (SCRIP `8b9a58e`).**
Do NOT physically purge the `emit_bb.c` walkers — the emitter's read of the IR is required and correct.

## The rule, correctly stated
Mode 3 (`--run`) and mode 4 (`--compile`) each require **exactly ONE full read of the IR at EMISSION time**
to build their artifact:
- mode 3 → an in-process executable image (the sealed x86 blob that is then jumped into);
- mode 4 → the `.s` assembly source (assembled + linked against `libscrip_rt.so`).

That emission-time read is fine. What the rule forbids is touching the IR **DURING EXECUTION** of the
emitted artifact — i.e. while the mode-3 blob or the mode-4 binary is RUNNING:
- no runtime helper (in `libscrip_rt`) may dereference an `IR_t *` at run time;
- no `IR_t *` may be baked into / captured by the generated code and chased at run time.

So: read the whole IR once, emit a self-contained artifact, then run the artifact with the IR never
consulted again. (For mode 4 this is automatic — the standalone binary doesn't even have the `IR_t` graph
in its address space. For mode 3 the IR lives in the same process, so the discipline must be actively kept:
the emitted blob and the runtime it calls must be IR-free at run time.)

## Current state — SCRIP `8b9a58e`
Native emission restored and working. m2 interp HARD gate PASS=202; icon smoke 12/12 all three modes;
prolog smoke 5/5 all modes. Icon rung tally at the pow-fold baseline: m2 202 / m3 76 / m4 82. The Icon pow
`^` constant-fold (lowering only, `2831781`) is intact.

## The ACTUAL task (next session)
Audit for IR access during EXECUTION, not emission:
1. Grep `libscrip_rt` runtime sources for any function reachable from a running emitted program that takes
   or dereferences an `IR_t *` / `IR_graph_t *` (e.g. helpers called via `x86("call", …)` from the
   templates that are handed an IR node pointer rather than already-marshalled data). Those are the
   violations — the emitted program would be reaching back into the IR at run time.
2. For mode 3 specifically, check what the sealed image / `rt_proc_*` registry holds: if any entry stores an
   `IR_t *` (vs. an emitted code pointer), and a runtime path chases it during execution, that violates the
   rule.
3. Where found: move the needed data into the emitted code / a run-time-owned structure at EMISSION time,
   and delete the run-time IR deref (stub its call site with `(*(volatile char *)NULL);` if it must remain
   as a tripwire). Emission-time IR reads in `emit_bb.c` are NOT targets.
4. Gate unchanged: m2 interp never drops below 202 (HARD); native smokes/gates stay green; verify mode-3
   and mode-4 still emit & run identically before/after.

## Note
The emitter being "by construction IR-reading" is fine — that IS the emission read. The mistake was
conflating emission with execution. Keep them distinct.
