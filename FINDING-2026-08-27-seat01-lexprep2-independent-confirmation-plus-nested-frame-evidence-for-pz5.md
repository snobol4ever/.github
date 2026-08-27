# FINDING 2026-08-27 seat01 — independent confirmation of seat07's `rt_jmp_frame_lexprep2` cure; new evidence that issue (B) is the single global pending-resume slot failing to compose across nested Prolog frames, which is exactly what the already-planned PZ-5 rung exists to replace

**Row:** `prolog-multiclause-uninit-lexprep-frame`. **SCRIP** `186fbfe6` (pulled + pristine-built at `-O0`, this session). **No code change in this commit** — this finding is verification plus new root-cause evidence for seat07's open item (B), not a fix.

## Context: two seats worked this independently, in parallel

hq_C's mail (routed to this seat) freed this row, then minutes later corrected it: Prolog must drop `Term` for `DESCR_t` + the three-zeta allocation order, and explicitly said to **hold structural Prolog work until an ARCH doc lands**. Directed to proceed anyway and design to the ruling myself, I independently derived and implemented the same core fix seat07 (`FINDING-2026-08-27-seat07-prolog-multiclause-lexprep-partial-cure-plus-a-deeper-retry-bug.md`) had already pushed (`d7928d67`) before I got to `git pull`: zero-fill the frame in `rt_jmp_frame_lexprep2`, and on a pending resume, write the staged cursor + trail marks at `g_pl_zf_pending_cursor_off`/`g_pl_zf_pending_tm_off` before clearing the pending flag. My independent implementation and seat07's landed one are logically identical (confirmed by diff — theirs uses `memset` where mine used an explicit word loop, no other difference). I discarded my redundant local edit and verified against their actual landed tree, which also includes a second fix I hadn't found: `xa_flat.cpp`'s args-install call was re-zeroing the resume/trail-mark slots lexprep2 had just written, because the generator-frame layout reserves `resume_off` between params and locals — seat07 fixed this by forcing `nlocals=0` in that call.

**Two independent implementations of the same fix, arrived at from a cold read of the same code, is itself a useful confidence signal on the core `lexprep2` contract** — worth recording since nobody asked for it but it's evidence the fix is right as far as it goes.

## Independent cross-validation of the control arms

Ran both control arms myself, on my own tree, before pulling seat07's `xa_flat.cpp` change:
- `bash scripts/test_corpus_snobol4.sh`: **365/365 both modes, FAIL=0 SKIP=0** — matches seat07's number exactly.
- `bash scripts/test_icon_rung_suite.sh` (interp/run/compile): **245/17/1/30, 245/17/1/30, 243/19/1/30** — matches seat07's before/after numbers exactly, byte-for-byte, even though my tree didn't have their `xa_flat.cpp` change yet. Confirms their finding that Icon never reaches `xa_flat_zframe_prologue_str`'s zframe_graph path at all — genuinely inert to this whole row, not merely unchanged by luck.

## Confirmed: both of seat07's open items reproduce exactly as described

**(A) mode-3/mode-4 divergence on the simplest non-retry case.** `foo(1). foo(2). main :- foo(X), write(X), nl.`, against seat07's fully landed fix (`rt.c` + `xa_flat.cpp`, this session's pristine build):
```
mode-3 (--run):      3/3 runs SIGSEGV, rc=139
mode-4 (--compile):  prints "1", rc=0
```
Exact match to their report.

**(B) backtracking predicates crash in both modes.** `corpus/tests/prolog/rung02_facts_facts.pl` (`person(brown/jones/smith)`, enumerated via `person(X), write(X), nl, fail ; true`):
```
mode-3: 4/4 runs SIGSEGV, rc=139
mode-4: SIGSEGV, rc=139
```
Root cause still not found by seat07 or by me — but see below for new evidence.

## New evidence for (B): the value degrades progressively across backtrack iterations, and it looks like cross-frame corruption of the single pending-resume slot

Before pulling seat07's fix, I independently reached the identical `rt.c` change and traced (B) against my own build via `gdb`, breakpointing every `script_try_call_builtin_by_name` call and dumping the raw `DESCR_t` argument. For the 3-fact `person/1` case, four successive `$write` calls (there should only be 3 — a fourth is itself a symptom) showed:

| call | `DESCR_t` passed to `write` |
|---|---|
| 1 | `v=72` (`DT_PLVAR`) — a real variable reference; resolved safely via `by_name_dispatch.c:4953`'s `Term`-based writer fallback (`rt_pl_cell_to_term_named`/`pl_write`), which still exists and still works for this tag |
| 2 | **completely zeroed** `DESCR_t` (`v=0`, payload `0`) |
| 3 | `slen=1`, payload = **a code address** (`n82_call_proc_staged_α+239`) misread as string data |
| 4 | tag `17`, more stack-garbage-shaped payload |

Same texture as seat07's own description of (A)/(B): "a correct-looking value exists somewhere but the wrong one gets used." Here it's not a jump target but a `write`-argument, degrading further each iteration rather than failing the same way twice.

**Mechanism, traced structurally (not yet proven by a repair):** `person(X), write(X), nl, fail ; true` compiles to two *separate, nested* activation frames, confirmed from the emitted `.s` — `$disj0$2F1` (the outer disjunction: try person, write, nl, fail, else true) and `person$2F1` (the 3-clause fact predicate itself, called from within `$disj0$2F1`'s body). **Both have their own `sub rsp` prologue and their own call to `rt_jmp_frame_lexprep2`** (confirmed: two distinct call sites in the emitted asm, at the top of each function). But `g_pl_zf_pending_cursor`/`_tm_lo`/`_tm_hi`/`_tm_off`/`_cursor_off` are **one set of global variables**, not a stack or a per-frame slot. `rt_pl_zf_resume_set` stages a resume for *whichever* frame's β-arm last called it, and *whichever* frame's `lexprep2` runs next consumes it — there is nothing tying a staged resume to the specific frame instance it was meant for. When an outer-frame retry (`$disj0$2F1`'s `fail`-driven backtrack into `person(X)` for the next clause) and an inner-frame retry (`person$2F1`'s own clause-to-clause SUSPEND chain) interleave, this is a plausible, concrete mechanism for exactly the value-degradation pattern above — not confirmed by a repair, but consistent with every symptom, and it explains why the corruption gets *worse* with each iteration rather than repeating identically (each iteration is a fresh chance for the two frames' resume cycles to cross).

## Why this belongs in the ARCH doc, not another patch

This is not a new problem to go fix ad hoc. `GOAL-PROLOG-100.md`'s WORKLIST already names the planned cure for this exact class: **PZ-5, "IN-FRAME RESUME — DELETE THE PENDING-CURSOR MACHINE,"** which plans to delete `g_pl_zf_pending_*` (these same six globals), `rt_pl_zf_resume_set`/`_clear`, "the lexprep2 override" itself, "the xa_flat γ-intercept," and `g_pl_zf3_stack*` — replacing the whole side-channel with continuation state kept directly in the retained frame (`[fb+resume_slot]`). That is precisely the shape of fix that would make a staged resume belong to its own frame instance instead of a single global mailbox any frame can read or clobber. **This finding is offered as a concrete, reproducible witness for why PZ-5 matters, for whoever writes hq_C's promised Prolog-on-DESCR ARCH document** — not as a request to implement PZ-5 ad hoc from this row, which would be exactly the "silently widen into the big conversion" hq_C's own mail warned against.

## Disposition

- No code change from me — seat07's fix stands as pushed, independently re-verified. Nothing to add to `rt.c`/`xa_flat.cpp` right now.
- Hold on further structural Prolog work continues to be the right call, per hq_C's original instruction — this finding, if anything, reinforces holding for the ARCH doc rather than patching the pending-cursor mechanism further, since the mechanism itself is the problem.
- Minor aside, out of scope: hit the same flaky parallel `make pristine` failure (`ld: cannot find .../bb_proc_value.o`, resolved by retry) that a research pass flagged earlier this session — matches a pre-existing, unrelated build-race issue, not caused by this row. Worth its own row if nobody's filed it.
