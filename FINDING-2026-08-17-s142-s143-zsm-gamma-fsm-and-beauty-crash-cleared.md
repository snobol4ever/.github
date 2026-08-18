# FINDING s142/s143 — ζ-SM GETS γ + A FOUR-STATE FSM, BEAUTY'S CRASH IS CLEARED, THE REAL BLOCKER IS NOT AN RBP BUG

**Session:** 2026-08-17 s142/s143 (Claude Sonnet 5). SCRIP: 2 files (`src/runtime/runtime_init.c`,
`src/templates/x86_asm.h`), zero template `.cpp` edits. Default arm byte-identical, regens ×3 zero changed bytes.

---

## ⛔ THE HEADLINE

`beauty.sno < beauty.sno`, mode 3, under `SCRIP_ZSM=1`: **exit 0, zero BOMBs, instrument runs the program to its own
completion.** This is a change from s141: the instrument itself no longer crashes anything. But **beauty's actual
stopping point (line 10 of 622, `Parse Error` on `-INCLUDE`) is NOT an RBP/frame defect** — it is a `-INCLUDE`
directive-handling gap, completely outside the ζ-frame class this rung's tooling targets. See "THE REAL BLOCKER"
below.

## WHAT LANDED — γ + THE FOUR-STATE FSM (NEXT SEAT (a) FROM FINDING-s141)

Exactly as the s141 finding predicted: γ rides the SAME `x86_jmp()` TRANSFER seam ω already used (`x86_gamma()` →
`x86_jmp(X86P_GAMMA)`, confirmed at the source) — zero new seams, zero template edits. Added `x86_zdp_rbp_gamma_at`
mirroring the existing ω arm.

FSM states added to `zsm_ent`: `FRESH → LIVE` (α) `→ SUSPENDED` (γ) `→ RESUMED` (β) `→ SUSPENDED` (γ, loop)
`→ DEAD` (ω, from any live state). Verified on a real backtracking witness (`probe/m1/m1_repl_r1.sno`) — the trace
shows the exact textbook cycle with zero violations:
```
α(FRESH→LIVE) → γ(LIVE→SUSPENDED) → β(SUSPENDED→RESUMED) → γ(RESUMED→SUSPENDED)
```

γ also gets the SAME `rbp==F` frame-integrity check β already had (this box's OWN frame, not the enclosing one) —
this localizes a lost frame to the DEPARTING box at the moment it happens, one hop earlier than the same defect
would previously have surfaced at the next β (finding-s141's own stated motivation for landing γ).

Also added: a LEAKED-ACTIVATION end-of-run report (`SCRIP_ZSM_LEAK_REPORT=1`, `atexit`-registered) — deliberately
read only at process end, never mid-run, since a SUSPENDED box mid-run is BY DESIGN not yet resumed (reading it as
a leak mid-run would repeat the s141 cut-2 mistake: convicting every un-backtracked-into ARBNO).

## ⛔ ONE REAL FINDING, MEASURED THEN CORRECTLY DOWNGRADED — READ THIS BEFORE TRUSTING THE FSM ON MATCH_BEGIN

The FIRST cut of the FSM made "α while an activation for this node is already LIVE/SUSPENDED/RESUMED" a HARD ABORT
(the natural reading of "illegal transition" from the s141 finding's own language). **Running it on beauty
immediately convicted a real, non-vacuous, reproducible signal on `IR_MATCH_BEGIN`'s own node** — and per RULES.md's
FALSE-POSITIVE-GATE discipline, this was investigated to ground before being trusted as a compiler defect. It is
NOT one:

- **gdb-confirmed, not assumed:** two α events on the SAME node id, IDENTICAL `rbp` both times (`0x7fffffffe8f0`),
  with the intervening γ reporting a DIFFERENT, lower `rbp` (`0x7fffffff9b88` — exactly 64 bytes down, the
  documented MATCH-RBP frame size). Identical rbp across both α's rules out recursion (a recursive call would sit
  at a progressively deeper, DIFFERENT rbp); this is a loop re-entering the same physical frame slot.
- **Source-confirmed root cause:** in the ζ-STANDING design, `IR_MATCH_BEGIN`'s frame is CONSTRUCT-scoped, not
  per-node. `IR_MATCH_BEGIN`'s own ω does the whack (`bb_match_begin.cpp`), but **so does `IR_MATCH_END`'s own α**,
  BEFORE `IR_MATCH_END`'s own γ (`bb_match_end.cpp:95-98`, `mov rsp,rbp / pop rbp` then `x86_gamma()`) — this is the
  actual, ordinary retirement path for a construct that succeeds without exhausting backtrack. `IR_MATCH_END` is a
  DIFFERENT IR node with a DIFFERENT node id, and `x86_zdp_rbp_frames()`'s predicate does not include
  `IR_MATCH_END`, so that whack currently emits NO ZSM event at all.
- **Conclusion:** MATCH_BEGIN's frame legitimately survives from its own γ, through the whole
  MATCH_BEGIN..MATCH_END bracket, and is retired by MATCH_END's α — a cross-node retirement this instrument was
  never told to attribute. A loop re-executing the same statement therefore legitimately shows a fresh α while
  MATCH_BEGIN's own last-known state is still SUSPENDED, because the retirement DID happen, just under a node id
  the instrument doesn't currently credit to the same activation.

**FIX (this session): downgraded from hard-abort to COUNTED, NOT FATAL** (`g_zsm_alpha_while_live`, same treatment
as the pre-existing `g_zsm_beta_no_alpha` "claimed impossible; counted, not fatal" precedent). Printed unconditionally
at process exit via the same `atexit` hook the leak report uses. Measured on beauty: **9 alpha-while-live events**,
zero of them fatal, zero of them distinguishable (by this instrument alone) from ordinary loop iteration.

⛔ **THIS IS NOT A FALSE-ALARM DISMISSAL — IT IS AN OPEN COVERAGE GAP, NAMED FOR THE NEXT SEAT.** A genuine leaked
MATCH_BEGIN frame (one that is NEVER retired, by any path) would produce the exact same counted-not-fatal signal as
9 ordinary loop iterations do, and this instrument currently cannot tell them apart. Closing this properly needs a
cross-node id thread — MATCH_END staging "which MATCH_BEGIN node id owns the frame I am about to whack" into its own
op_ fields, so MATCH_END's whack can emit `rt_zdp_sm_event(that_node_id, rbp_before_whack, rsp_before_whack, 3)` (a
synthetic ω attributed to MATCH_BEGIN's id) BEFORE popping. That is a real design task (a new planner field, ONE
AUTHORITY discipline, NOT a quick patch) and is out of scope for this session.

## THE REAL BLOCKER ON BEAUTY — NOT AN RBP DEFECT

With the crash cleared, `beauty.sno < beauty.sno` under `--run` now reaches its own STOPPING point cleanly (exit 0,
not a SIGABRT) and prints:
```
*-----------------------------------------------------------------------------------------------------------
* Program:       SNOBOL4 Beautifier
...
* Version:       0.25
*
Parse Error
START
```
against the oracle's:
```
...
*
START
-INCLUDE 'global.inc'
...
```
Minimal repro (`echo "-INCLUDE 'x.inc'" > t.sno; echo END >> t.sno; ./scrip --run t.sno`):
```
snobol4:2: error: cannot open include 'x.inc'
scrip: 1 parse error(s) in 't.sno' -- no code generated
```
**SCRIP's `-INCLUDE` handling tries to actually open and inline the named file** (real SPITBOL preprocessor
semantics), but beauty's self-host test feeds `beauty.sno` to itself as SUBJECT TEXT for the beautifier's own
pattern-matching logic to scan and echo, not as a real compilation unit whose `-INCLUDE`s should resolve on disk (the
sibling `.inc` files are not even present in `corpus/programs/snobol4/demo/beauty/` as of this session — only
`beauty.sno` itself). This is a FRONTEND/DRIVER-MODE question (how does `-INCLUDE` behave under `-bf`-equivalent
mode vs normal compile), completely orthogonal to the ζ-frame/RBP class this rung's tooling exists to find. **It is
the reason beauty stops at line 10 of 622**, not any frame defect — with the crash class cleared, this is now
visible as a bug of its own, previously masked by the earlier ZSM abort's mid-execution SIGABRT.

## GATES

False-positive gate (5/5, re-run 3× across the session: initial γ+FSM landing, after the alpha-while-live downgrade,
and post-final-rebuild) — zero BOMBs on `m1_defer_LEN0` / `m1_inline_ALT` / `m1_nodefer_ALT` / `m1_alt_arm1_cap` /
`m1_alt_arm2_cap`. Non-vacuity: γ fires (confirmed in traces, e.g. `m1_alt_arm2_cap` 1α/1γ, `m1_repl_r1` full cycle).
Byte-identity: stash/rebuild diff on pristine HEAD (`e00be66d`) — `.compile` `.s` output byte-identical, all default
witness md5s match exactly. Regens ×3 (benchmark/feature/demo): zero changed bytes, run twice (once after the γ+FSM
landing, once after the final alpha-while-live downgrade). `test_gate_template_medium_invisible.sh --strict`: FAILs
on the SAME inherited baseline s138/s141 already recorded (`bb_glue_flat` 4, `xa_flat` 8) — touched files contribute
0, confirmed via `git diff --stat` scoping to exactly the two files this rung touched.

## NEXT SEAT — pick up exactly here

**(a) THE CROSS-NODE FRAME ATTRIBUTION DESIGN** (see the coverage-gap paragraph above) — stage MATCH_BEGIN's own
node id into MATCH_END's op_ fields (a new planner field, likely beside `emit_match_begin_frame_extra`'s existing
ARBNO-slot-widening precedent) so MATCH_END's whack can emit a synthetic ω for MATCH_BEGIN's id. Closing this turns
`g_zsm_alpha_while_live` from a counted-but-uninterpretable signal into a real leak detector.
**(b) THE `-INCLUDE` FRONTEND QUESTION.** Beauty's self-host test needs `-INCLUDE` to behave correctly when beauty
reads ITSELF as subject text — investigate whether `-bf`-equivalent mode should suppress real file-opening for
`-INCLUDE` (matching what the oracle does) or whether the `.inc` files need to actually exist in
`corpus/programs/snobol4/demo/beauty/`. This is the ACTUAL beauty-self-host blocker now that the RBP crash class is
cleared — a completely different bug from anything this rung's ζ-frame tooling targets.
**(c) CONDITIONAL-PORT COVERAGE via CONDITION INVERSION** at the `x86_jcc` seam (s141 NEXT SEAT (b), still open,
not attempted this session — the `-INCLUDE` discovery took priority once the crash cleared).
**(d) RE-RUN THE FALSE-POSITIVE GATE AFTER EVERY WIDENING, BEFORE READING ANY NUMBER** — this session's own
alpha-while-live cut needed exactly this discipline to avoid landing as an abort.

## MEASURED

γ non-vacuous (fires, `m1_repl_r1` full FSM cycle 1α/2γ/1β, zero violations) · false-positive gate 5/5 zero, 3
independent runs · beauty m3: **0 BOMBs, exit 0** (was SIGABRT before this session) · 9 alpha-while-live events on
beauty, counted not fatal · zero template `.cpp` touched · regens ×3 zero changed bytes, 2 independent runs ·
`.compile` `.s` byte-identical vs pristine HEAD stash/rebuild · `git diff --stat`: exactly 2 files, 106
insertions/8 deletions.
