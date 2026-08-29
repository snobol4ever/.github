# FINDING: hq_C's ruled Option 1 ("tighten `bb_call_route_classify` with a per-proc capability bit, SNOBOL4 unset") breaks standalone SNOBOL4 — `assign_driver.sno` regresses in both modes. NOT LANDED. Refined hypothesis for the next actor.

Row: `m3-passes-m4-fails-three-polyglot-demos`, topic `polyglot-callroute-dynscope-vs-frame`. hq_C ruled OPTION 1 (reply
to seat03, archived `hq_C/archive/...-q-polyglot-callroute-dynscope-vs-frame.msg`): tighten `bb_call_route_classify`'s
`rt_proc_is_registered(fn)` check with a genuine capability flag distinguishing frame-style procs (SNOBOL4 DEFINE) from
ones eligible for cell/name-based dynamic dispatch (Prolog/Raku/Icon), rather than scoping the mode-4 eager
pre-registration loop by language (barred — that's a language sentinel).

## What was implemented (all reverted, nothing landed in SCRIP)

Added `ProcEntry.stage_call` / `rt_proc_t.stage_call` (new field, fit into existing struct padding after
`frame_bytes` so `sizeof(rt_proc_t)` stayed 128 — the `_Static_assert` citing `rtx_plcall.s` baking a `shl 7` stride
is itself stale, that file no longer exists anywhere in the tree, grep-confirmed zero hits for
`g_rt_gen_procs`/`PROC_DYN_SCOPE`/any `shl ,7` in `*.s`/`*.S` — flagging since nothing here depended on fixing it).
Set `stage_call = 1` only at the proc-registration sites in `lower_prolog.c` (3 sites), `lower_raku.c` (2 sites),
`lower_icon.c` (1 site) — exactly where each frontend already self-marks its own calls `IR_CALL_PROC_STAGED` via
`rk_proc_known`/`icn_callable_proc_index`/unconditional Prolog construction. Left unset (0) for SNOBOL4. Gated
`bb_call_route_classify`'s registry fallback on `rt_proc_is_registered(fn) && rt_proc_is_stage_call(fn)`, and
simplified the BYNAME fallback to fire whenever the STAGED gate didn't (previously dead-guarded on
`!rt_proc_is_registered`, unreachable given the old unconditional STAGED check above it).

## Measured, not inferred: it's directionally right on the row's own target and wrong in general

**Control-arm A/B on the row's three named demos (pristine builds, same HEAD, patch stashed vs applied): byte-identical
matrices both ways** — `m3 PASS=2 FAIL=8 · m4 PASS=2 FAIL=8`, demo02/03/04/09 all `CRASH(sig=11)` both modes on
*both* trees. Not a regression there — but not a fix either; more on why below.

**Broad SNOBOL4 corpus gate (hq_C's own stated landing bar) caught a real break the demo-only check couldn't:**
`beauty_suite/assign_driver.sno` — plain, single-language, non-polyglot — passes clean on the control tree (`m3` and
`m4` both byte-match `.ref`) and **fails both modes on the patched tree** (m3: 4 of 7 sub-checks flip PASS→FAIL; m4:
`Error 5 ... Undefined function or operation` at statement 0). This file's only proc is `assign(var,val)`
(`-INCLUDE 'assign.inc'`), a plain SNOBOL4 `DEFINE`, structurally identical in kind to `check` in the polyglot repro.

## Why: the premise "SNOBOL4 procs should default to BYNAME, STAGED is a Prolog/Raku/Icon-only capability" is false

`is_sno_bb = (saw_sno || is_scrip) && !is_pascal` (`scrip.c:1014`) — **true for any SNOBOL4 content, standalone `.sno`
included, not just polyglot `.scrip` files.** The mode-4 eager pre-registration loop this row's whole investigation
centers on (`is_icon||is_raku||is_sno_bb||is_prolog`) therefore runs for ordinary standalone SNOBOL4 too, registering
every one of its own DEFINE'd procs before any call site compiles — exactly the mechanism blamed for the polyglot
collision. Before this session's patch, **every standalone SNOBOL4 DEFINE'd-proc call has always gone through
`CALL_ROUTE_PROC_STAGED`** via the old unconditional `rt_proc_is_registered(fn)` check, same as `check` in the
polyglot case — and it has always worked (that's what `assign_driver.sno` proves). Forcing SNOBOL4 to `stage_call=0`
(→ BYNAME) breaks the *normal, working* path, not just the broken polyglot one.

**Refined hypothesis, not yet verified — this is where the real bug most likely still lives:** seat03's own root-cause
chain showed `check`'s *registered address* resolves to `n206_statement_begin_bx` (the wrong node) in the polyglot
merge specifically, while the *identical* registration mechanism resolves correctly in isolation. `assign_driver.sno`
never merges sections — nothing corrupts its registry entry, so STAGED dispatch through a *correct* address works
fine. This points back at seat01's original, never-fully-localized lead (`sr3_gamma_label`/`bb_define.cpp`'s address
computation reading a stale `IR_GOTO_DEFERRED.sval` once multiple language sections share one flat node-numbering
space) as the more likely actual defect — a **registry-correctness** bug specific to merged compilation, not a
**routing-choice** bug. Routing away from STAGED only "fixes" demo04 by accident, by avoiding a corrupted address;
it breaks everything else that depends on STAGED reaching a correct one.

## Not landed, tree confirmed clean

All 8 touched files (`stage2.h`, `rt.h`, `rt.c`, `scrip.c`, `emit.cpp`, `lower_{prolog,raku,icon}.c`) reverted via
`git stash` (kept locally this session for reference, not pushed anywhere). `git status` clean at origin HEAD.
**Separately, and unaffected by any of the above:** `corpus` commit `224916cc1` (this session, pushed) fixed
`corpus/scrip/demo09/rpn.scrip`'s Icon section from icont-style newline-terminated to SCRIP's required semicolon
style — a real, isolated, unrelated parse bug (confirmed byte-for-byte reproducible standalone) that was masking
demo09's actual shared-with-demo04 crash behind a parse error. That fix stands regardless of this row's outcome.

## For the next actor

Do **not** re-attempt "default SNOBOL4 away from STAGED" in any form (language-keyed or capability-keyed) — proven to
regress standalone corpus. The two live options from hq_C's ruling context need a third look:
1. **Chase the address-computation angle directly**: instrument `rt_proc_register`'s `fn` pointer for `check` in the
   demo04 repro vs. `assign` in `assign_driver.sno` — confirm whether the registered address itself is wrong in the
   merge case (this session did not re-verify seat03's specific gdb finding, only re-derived the routing angle from
   the task file's prose).
2. If routing genuinely is part of the fix, the capability signal needs to distinguish "this proc's registry entry
   is trustworthy" from "this proc is SNOBOL4" — not the same thing, as `assign_driver.sno` shows.
