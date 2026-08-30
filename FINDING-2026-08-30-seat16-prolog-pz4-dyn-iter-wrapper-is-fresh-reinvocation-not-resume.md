# FINDING 2026-08-30 seat16 — PZ-4's remaining rung14/15 failures: ROOT CAUSE CONFIRMED. Retract-tainted predicates compile to a synthesized SUSPEND-wrapped generator function; retrying it is a full fresh re-invocation (`jmp` back to its own entry), not a resume. This IS the same structural class as this row's four original convergence FINDINGs — just one layer further out than seat03's own trace looked. Not attempting the fix (it's the shared retained-activation-frame design, not a local patch).

## CONTEXT
Continues directly from `FINDING-2026-08-30-seat03-prolog-pz4-remaining-failures-are-retract-then-enumerate-dyn-iter-resume-not-persisted.md`. seat03 isolated the trigger (retract-then-enumerate-same-predicate), traced it to `rt_pl_dyn_iter_gen`'s `resume` slot reading back 0 on retry, and left an explicit open question: is this in scope for this row's steps (a)-(f), or a separate local defect in the by-name trampoline? This FINDING answers that question with code- and gdb-grounded evidence, and refutes one natural-looking hypothesis along the way (recorded so nobody re-spends time on it).

## HYPOTHESIS REFUTED FIRST (before the real mechanism) — the ζ-slot width for `IR_CALL_BUILTIN_GEN` is NOT under-granted
Initial suspicion: `bb_call_byname_gen_str`'s `genoff = resoff + 16*(1+narg)` looked like it could land one quad past whatever `zeta_storage.c`'s allocator actually reserved for the node (a classic "next sibling's slot" collision). Traced the real call chain to be sure rather than assuming:
- `zls_grant()` (`zeta_storage.c:209-215`) reserves **quad 0 = "result"** at the node's own granted base `off`, *then* calls `zls_grant_locals(nd, scope_id, off + 16)` and returns `1 + zls_grant_locals(...)`.
- `zls_grant_locals`'s `IR_CALL_BUILTIN_GEN` case (`zeta_storage.c:173-177`) receives that already-shifted `off+16` as its own `off`, grants `narg` argv quads there, then one resume quad at `off + 16*narg`, and returns `1 + narg`.
- Total granted = `1 (result, from zls_grant) + 1 (resume) + narg (args)` = **exactly** what the template computes (`resoff`=result, `resoff+16`=argbase, `resoff+16*(1+narg)`=genoff). No off-by-one, no aliasing with the next node. **Refuted by code reading, not just unreproduced — recording so this isn't re-chased.**

## THE REAL MECHANISM — confirmed by ASM-DIFF-FIRST, then gdb (RULES.md order)
Repro used (byte-identical shape to seat03's `testB`): `f(a).f(b).f(c). main :- retract(f(a)), f(X), write(X), nl, fail. main.` — SCRIP HEAD `ae078681`, pristine `-O0`, `make pristine` before any measurement.

**1. `f/1`, once retract-tainted, is not just "a call site routed through `$dyn_iter`" — it is a whole separate compiled function**, `FN__f$2F1` (mangled `f/1`), synthesized by `lower_pl_dyniter_graph()` (`src/lower/lower_prolog.c:943-964`). That function's body is exactly `nmop → var_ref(s) → IR_CALL_BUILTIN_GEN("$dyn_iter") → IR_SUSPEND`. Its prologue (`--compile` output):
```
FN__f$2F1:
    sub  rsp, 192
    mov  [rsp+168], rcx
    mov  [rsp+176], rdx
    mov  [rsp+184], rsp
    mov  rdi, rsp; mov esi, 128; mov edx, 160
    call rt_jmp_frame_lexprep2@PLT       ; the SAME mailbox mechanism seat05's/seat02's FINDINGs already named
    ...
    call rt_icn_zframe_args_install@PLT
f$2F1_α_body:
    lea  rax, [rip + n3_suspend_β]
    mov  [rsp+128], rax
    ...                                    ; n2_call_builtin_gen_α eventually: mov FRQ(genoff), 0  (unconditional)
```
`main`'s own call site to `f(X)` is `n27_call_proc_staged`, and it is **not an ordinary staged call** — `zeta_storage.c:186` (`if (nd->op == IR_CALL_PROC_STAGED && zls_callee_is_gen(nd))`) grants it the GENP-SPINE extra slot, and the emitted code calls `rt_gen_spine_pass_γ`/`rt_gen_spine_pass_ω`/`rt_gen_spine_resume_enter` — i.e. this is precisely "a `call_proc_staged` to a generator callee," the exact shape this row's steps (a)-(f) target. It is not a coincidence that this matches — `rt_proc_is_generator("f")` is true because `f` now has an `IR_SUSPEND` in its compiled body.

**2. The retry path (`n27_call_proc_staged_β`) is a fresh re-invocation, not a resume-in-place.** Read directly off the emitted `.s` (testB.s:614-671):
```
n27_call_proc_staged_β:
    call rt_gen_spine_resume_enter@PLT      ; trivial k_level++ (rtx_icngen.s) -- not a resume mechanism itself
    call rt_pl_cp_pop3@PLT                  ; pop saved (cursor, trail-mark) from a GLOBAL array
    ...
    call rt_pl_zf_resume_set@PLT            ; stash (cursor, trail-mark) into 5 process-wide globals
    ...
    mov  edi,0; mov esi,1
    call rt_proc_call_open_det@PLT          ; <-- SAME call as the FIRST invocation (testB.s:535), same args
    ...
    jmp  rax                                ; <-- jumps to f$2F1's ENTRY AGAIN, not to a saved mid-function address
```
`rt_proc_call_open_det` resolves "f/1" to its entry point and the retry `jmp`s straight into it — i.e. **every retry re-runs `FN__f$2F1`'s full prologue and `f$2F1_α_body` from the top**, including `n2_call_builtin_gen_α`'s unconditional `mov FRQ(genoff), 0`.

**3. gdb confirms this dynamically, and rules out address drift** — breakpoint on `rt_pl_dyn_iter_gen`, `-batch`, printing `$rsp` / the `resume` pointer (rdx) / `*resume` on every hit:
```
CALL #1  rsp=0x7ffffffed2e0  resume_ptr=0x7ffffffedca0  *resume=0
CALL #2  rsp=0x7ffffffed2e0  resume_ptr=0x7ffffffedca0  *resume=0            <- WRONG, should carry call 1's `it`
CALL #3  rsp=0x7ffffffed2e0  resume_ptr=0x7ffffffedca0  *resume=140736133636528
```
**RSP and the resume-cell's physical address are IDENTICAL across all three calls.** This rules out both of the mechanisms I went in suspecting (stack-depth drift across the backtrack window, and slot aliasing with a neighbour) — the address is stable *because* backtracking correctly restores rsp to the exact depth `main` was at before it first called `f`, so a **fresh** `sub rsp,192` for `f$2F1` deterministically lands on the same bytes as before. The value is lost not because the memory is corrupted or misaddressed, but because **the instruction that zeroes it is unconditionally re-executed as ordinary, correct behaviour for what the compiled code believes is a brand-new call** — exactly seat03's own framing: *"The generator has no way to tell 'this is a fresh top-level call' from 'this is a retry whose resume slot got reset/lost.'"* Now grounded in exactly which instruction, on exactly which re-entry, and why the address is stable rather than drifting.

**4. Why `testC` (retract an unrelated predicate) passes, and why rung13 is now 5/5:** a predicate that is never retract-tainted is never wrapped in `lower_pl_dyniter_graph`'s `IR_SUSPEND` machinery at all — it stays on the plain `call_proc_staged` path to an ordinary (non-generator) callee, which is the path icon-n2's landing (items 3-4, `icon-n2-generator-activation-frames`, now DONE) already improved. rung13's witnesses are plain multi-fact enumeration through *that* path. rung14/15's three remaining failures are the only witnesses that force a predicate through the `IR_SUSPEND`-wrapped generator path — the one icon-n2's landing does not reach, because `rt_jmp_frame_lexprep2`'s mailbox only ever carried `(cursor, trail_mark)`, never a box-local generator's own private state.

## ANSWERING seat03's OPEN QUESTION DIRECTLY
**Yes — this is the same structural class as the four original PZ-4 convergence FINDINGs and hq_C's own DUO matrix** ("retry/resume state kept at a fixed offset or in a shared global, with no protection across a γ-suspend↔β-resume window where unbounded stack activity can intervene"). It reaches that same wall through the retract-synthesized generator wrapper (`lower_pl_dyniter_graph`) rather than through a hand-written multi-clause predicate, but the failure shape is identical: a **generator/goal activation that does not survive its own suspend↔resume round trip**, papered over today by a mailbox that only carries two of the fields a real generator needs. Implementing this row's steps (a)-(f) / the ratified zframe_graph BB-locals design (`ARCH-PROLOG-DESCR-ZETAS-hq_C.md` §5, seat02's seam design) should fix this too, **provided the implementation is applied at the `IR_CALL_PROC_STAGED && zls_callee_is_gen()` call-site class** (`n27` above) so it covers synthesized single-box generator wrappers, not only hand-written multi-clause predicates — structurally there is nothing wrapper-specific about the defect; `f$2F1` is an ordinary `IR_SUSPEND`-bearing graph from the pipeline's point of view.

## WHY NOT ATTEMPTED HERE
Same standing discipline as every predecessor's entry in this row's LEDGER, now with a firmer reason than "it's shared surface": the actual fix is **not** a local patch to `bb_call_byname_gen_str` or `rt_pl_dyn_iter_gen` (their own resume-cell bookkeeping is correct on its own terms, confirmed above) — it requires giving `f$2F1`-shaped activations a *retained* frame across suspend/resume, which is precisely the multi-session, ceo/Lon/hq_P-ratified design this row exists to land (steps a-f), now unblocked (icon-n2 items 3-4 are DONE) but still real, substantial, shared-surface implementation work. I looked for a narrower local escape hatch (e.g. threading the dyn-iter `it` pointer through the *existing* 5-field mailbox as a 6th field) and deliberately did not build it: that would be exactly the "quick patch that fights the ratified design" pattern ceo's design-check entry in this file warns against — the mailbox is what steps (a)-(f) are supposed to *retire*, not grow.

## NEXT ACTOR
1. This row's own steps (a)-(f) — once implemented — are the fix. When picking that up, treat `n27_call_proc_staged`'s `zls_callee_is_gen()` arm (GENP-SPINE) as an in-scope call-site class, not only direct hand-written multi-clause predicates, and grade rung14/15's `retract_retract_basic`/`retract_retract_mixed`/`abolish_then_reassert` as three more control witnesses (all three now share one root cause, confirmed above — fixing it should move all three together).
2. Corrected floor for whoever verifies next, name-for-name (unchanged from seat03's measurement, no source changed this pass either): rung13 5/5 · rung14 0/2 · rung15 3/4 (`abolish_then_reassert` only).
3. rung13/14/15's own gate scripts remain confirmed stale (seat11/seat03) — still `tests-consolidate-prolog`'s (hq_B's) lane, not this row's.
4. If someone wants a concrete first slice smaller than the full retained-frame design: instrument exactly what `f$2F1`'s own internal "already suspended" dispatch (the `[fb+0]`/`[fb+8]` check ADDENDUM 3 and seat02 both named) does with the `cursor` mailbox field on a resume — that's the one piece of `f$2F1`'s own body I did not fully single-step this pass (I confirmed the *entry* is a fresh re-invocation via ASM+gdb; I did not trace whether `f$2F1_α_body`'s own internal branch on the restored cursor ever attempts to skip re-running `n0`/`n1` and jump straight at `n2`/`n3` — if it does, that's the natural seam where a 6th field would need to slot in for the *properly designed* version of this fix, not a shortcut).

No SCRIP/corpus source changed this pass (investigation + a throwaway repro under the scratchpad only, compiled/run outside the tree). gdb script and repro `.pl`/`.s` are scratch, not committed.
