# FINDING 2026-09-05 (seat03) — `array_replace_branch_2`'s class8 workspace-island exhaustion is the ALREADY-KNOWN `define-redefinition-ordering` defect (hq_P's row), confirmed on a second, different-arity witness

⛔ **CORRECTION TO MY OWN FIRST DRAFT OF THIS FILE:** I wrote this file's root-cause section from black-box probing without first searching `.github` for prior art. There is prior art, it is deeper than what I found, and it already has a scoped (if unlanded) cure design:
- `FINDING-2026-09-05-hq_P-define-redefinition-is-deduped-at-compile-time-so-the-last-define-wins-retroactively.md`
- `FINDING-2026-09-05-hq_P-define-redefinition-the-snobol4-call-site-is-statically-bound-so-registration-never-reaches-it.md` (supersedes that one's §3/§5)
- `FINDING-2026-09-05-seat07-define-entry-point-redirect-not-honored-for-a-statically-wired-recursive-self-call.md` (mirror-image shape, same general area)
- `corpus/tests/snobol4/ALL.xfail` rows 1816–1817 (`user_function_replace_4`, `user_function_replace_7`, class `define-redefinition-ordering`, hq_P's lane, rank 3)

**What survives from my first draft, and what this file is actually for:** confirming that `array_replace_branch_2`'s class8 workspace-island exhaustion (task: `snobol4-workspace-island-exhausted-core-dumps-where-the-oracle-prints-3-permutations`, owner hq_S) is **the same class-defect**, not a separate compiler bug — including the **different-arity variant**, which hq_P's witnesses (`user_function_replace_4/7`, both same-arity) do not cover. Everything below is written against that backdrop; read hq_P's two findings first for the real depth (exact `lower_snobol4.c` lines, the emitted asm, and a partially-working 4-layer patch).

**Tree:** SCRIP `f2c01c7dd` (incremental `make`, not pristine — this is diagnostic, not a landing verdict), corpus `590684477`, `RT_OPT=-O0`, this root, 2026-09-05 ~19:55–20:40 CDT.
**Entry:** `array_replace_branch_2`, `corpus/tests/snobol4/ALL.sno` rank 1852, class8. Fixture: `gimpel_triage_class8_sig6_perm_module.sno` (PERM.inc, Trotter's algorithm) `-INCLUDE`s `gimpel_triage_class8_sig6_perm_swap.sno` (SWAP.inc).

## THE MECHANISM (hq_P's diagnosis, restated briefly — see hq_P's findings for the real detail)

SCRIP's SNOBOL4 lowerer keys its compile-time `DEFINE` table (`defs[]` in `lower_snobol4.c`, three identical dedupe sites — hq_P cites `:2451/:2607/:2627` on their tree, `:2453/:2609-11/:2629-31` on mine, drift from intervening commits) by **function name alone**, collapsing every `DEFINE` for a name to one row before any call is compiled — arity is not part of the key. The emitted call site (`bb_call_proc_staged.cpp`) is a direct compile-time-bound jump (`lea rax,[rip+F_α]; jmp rax`) to whichever body survived the dedupe. `rt_define_site` (`rt.c:1781`) really does mutate the registered proc's `p->fn` at runtime, in correct program order — but nothing at the call site ever reads `p->fn`. So the runtime redefinition machinery is real and correctly ordered, and **entirely inert**, twice over: only one body ever survives to be redefined, and the call site doesn't consult the mutated cell regardless.

hq_P has a WIP four-layer patch (defs[] keeps every DEFINE · proc_table names them distinctly · driver pairs the Nth bind to the Nth def · call sites dispatch dynamically when multi-bound) preserved at `.github/wip-patches/define-redefinition-ordering-hq_P-2026-09-05-three-of-four-layers.patch`. Status per hq_P's second finding: layers 1–3 proven, single-DEFINE control arm green both modes; layer 4 (dynamic call dispatch) SIGSEGVs in m4 and is flatly missing in m3 (the per-binding stub realization is gated `g_is_text`, a TEXT-only path — m3/BINARY mode never emits one). **Not landed. Not a quick finish.**

## THIS FIXTURE'S CONTRIBUTION: the different-arity variant, and what it looks like as a live crash instead of a wrong-output line

hq_P's witnesses (`user_function_replace_4/7`) keep the **same arity** across both `DEFINE`s, so the symptom is a wrong-output line: a call issued *before* the second `DEFINE` even executes still runs the second body. `array_replace_branch_2`'s `PERM.inc` changes arity on redefinition (`DEFINE('PERM(A)','PERM_INIT')` → later, from inside `PERM_INIT`, `DEFINE('PERM(A,I,OFFSET)RL,D,LIMIT,AL')`), and the symptom is qualitatively different: **not** a wrong body running, but the new-arity body **never running at all**, from any call, ever — because a different arity is a different name-keyed-but-arity-blind... no: re-reading hq_P's mechanism, the dedupe key is name-only, so `PERM` at arity 1 and `PERM` at arity 3 should collide into the SAME `defs[]` row same as the same-arity case. Empirically they do not act as if they collided — the 1-arg call site never reaches the 3-arg body, across 8 traced calls, with no sign of the "last-wins" behavior hq_P measured for same-arity. **This is flagged, not resolved**: either arity is consulted somewhere downstream of the `defs[]` dedupe after all (contradicting the name-only characterization above), or `PROTOTYPE`/argument-count mismatches take a different path than an exact-arity re-DEFINE. Whoever picks up hq_P's patch should re-run its layers against this fixture specifically, since it is a different shape than either of hq_P's witnesses and may not be fixed by the same four layers.

Isolating probe, run this session (small, no arrays, for triage speed — not proposed as a corpus fixture):
```
	DEFINE('F(X)','F1')			:(START)
F1	OUTPUT = 'F1 (old def) X=' X
	DEFINE('F(X)','F2')			:(RETURN)
F2	OUTPUT = 'F2 (new def) X=' X		:(RETURN)
START	F(1)
	F(2)
	F(3)
END
```
Oracle: `F1.../F2.../F2...`; SCRIP: `F2.../F2.../F2...` — this is exactly hq_P's `user_function_replace_4` shape, reproduced independently; included here only to show the same-arity half of the picture the different-arity fixture sits next to.

Instrumented the real module in place (OUTPUT tracing only, no logic touched) and ran the driver capped at 8 top-level `PERM(A)` calls: **`PERM_INIT` runs on every single call, the 3-arg `PERM` body's trace line never prints once.** Each `PERM_INIT` re-entry pays for a fresh `ARRAY('0:' SIZE_A-2, 1)` pair that never gets used correctly and is never reclaimed quickly enough; `LOOP` never receives the terminating failure the 3-arg body would eventually produce, so it runs past `N=4,000,000` (traced by printing every 200,000) against the oracle's correct `N=3`, until the 1024MB workspace island aborts. **Confirmed not a capacity problem** (this was the task's own steer) and confirmed not an array-bounds-check gap (`A=ARRAY('0:0',999); X=A<1> :F(...)` fails correctly in SCRIP, matching the oracle) — the runaway is entirely explained by `PERM_INIT`'s setup cost times an unbounded iteration count.

Side note, unrelated to the main mechanism: the abort's `raise ZC_WSI_MB` reads like a runtime knob but isn't — `ZC_WSI_MB` is a compile-time `#define` (`src/ir/zeta_choices.h:8`, value `1024`), not read via `getenv` anywhere under `src/`. Setting the env var has no effect; the cap only changes by editing that header and rebuilding.

## FOR WHOEVER TAKES THIS NEXT

1. Read hq_P's two findings and the WIP patch before re-deriving anything.
2. Re-run hq_P's four-layer patch against `array_replace_branch_2_witness.sno` (created this session, see Artifacts) specifically — the arity-changing shape may expose a fifth layer or a different bug in the same neighborhood, per the unresolved paragraph above.
3. This row (`snobol4-workspace-island-exhausted-core-dumps-where-the-oracle-prints-3-permutations`, hq_S's lane) and hq_P's `define-redefinition-ordering` row (hq_P's lane, rank 3) are the same class-defect wearing two symptoms in two different HQ lanes. Flagged to hq_S (my HQ) to coordinate with hq_P's lane rather than have this row design an independent cure.

## ARTIFACTS

- `corpus/tests/snobol4/array_replace_branch_2_witness.sno` — created this session (did not exist before); the census entry's driver, extracted verbatim from `ALL.sno` rank 1852.
- Task DONE-WHEN fixed: the original omitted the `_swap.sno` companion from its copy set and would have failed on `cannot open include` (a parse error) instead of ever exercising the crash, regardless of cure state. Now copies module + swap + witness; verified currently red (`PERM-MODULE m3rc=134 got3perm=0 wsi=1`), as it should be pre-cure.
