# GOAL-CSN-FENCE-FIX.md — CSNOBOL4 FENCE(P) builtin nested-recursion segfault

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** csnobol4 (primary), SCRIP (gates only)
**Done when:** `csnobol4 -bf -P64k -S64k beauty.sno < beauty.sno` produces
N>500 lines of output without segfault and without "Caught signal" diagnostic.
PLUS SCRIP Smoke=7, Broker=49 preserved.  PLUS the existing 10-test
`test/fence_function/` suite continues to pass.

**Lifted from:** `GOAL-LANG-SNOBOL4.md` SN-26-bridge-coverage-i (sessions
#37–#41).  This goal carries the full diagnostic state forward.

---

## Direction (set 2026-04-27 session #42, ratified by Lon)

⛔ **No separate parallel save stack.**  The session #41
`fnc_save_push` / `fnc_save_pop` C-helper approach (`lib/pat.c`,
`realloc`-grown array of `struct fnc_save_frame`) is **retired**.
A second memory structure that has to stay in sync with PDL unwinds
is exactly the cross-cutting fragility we want to avoid.

⛔ **No assumed fix.**  As of session #42 we **do not know** what
the right fix is.  An earlier draft of this file proposed a specific
PDL-trap-entry-extension as if it were the solution; that proposal
was speculation, not a verified fix path.  Trace evidence from
session #42 (see "The remaining bug" below) shows the crash happens
**after** FNCB has cleanly restored byte-correct outer state — i.e.
the bug may not be in the save/restore mechanism at all.  Saving
more state, or saving it in a different place, may not help.

The next session's first job is **investigation**, not coding.
F-0 (revert session #41) is a baseline-cleanup step; F-1 is now an
**investigation rung**, not an implementation rung.  Code lands
only after the design space below has been weighed against fresh
diagnostic evidence.

---

## Open design space — none verified, all candidates

These are alternative shapes the fix could take.  Each is a
hypothesis about where the bug actually lives.  The right one
depends on diagnostic evidence we have not yet gathered.

### D1 — Failure-walker fence-aware mode (Lon's suggestion)

Add a "you are inside a FENCEd region" flag (or a depth counter,
or a sentinel PDL entry the walker recognizes) so the failure
walker knows it cannot backtrack past a seal.  FNCA sets it on
entry; FNCC1's seal entry maintains it; FNCD or FNCB clears it.

Why this is plausible: SIL's FENCE is conceptually a *wall*, not
a save/restore point.  The save/restore model treats FENCE as if
it were ATP-like (with a paired entry/exit save), which may be a
misframing.  If the failure walker is reading garbage PDL slots
*beyond* the FENCE seal, the right fix isn't "save more state"
but "stop the walker from going there."

What we'd need to know:
- Is the failure walker actually crossing a seal boundary it
  shouldn't?  Currently unverified.
- What does CSNOBOL4 currently do when the walker hits FNCDCL
  in slot 1?  (It dispatches to FNCD, which does
  `MOVD PDLPTR,PDLHED` + `MOVD NAMICL,NHEDCL` + `BRANCH FAIL`
  — i.e. it already truncates.  But maybe truncation alone isn't
  enough; maybe the walker re-reads slots before reaching FNCD.)

### D2 — Compile FENCE(P) to a different pattern shape

FNCA/FNCB/FNCC/FNCD as four cooperating PDL primitives may be
the wrong decomposition.  SPITBOL's `p_fna..p_fnd` are also four,
but they share `xs` (the pattern stack), not cstack — and SPITBOL
saves much less.  An alternative is to make FENCE(P) compile to
a wrapper that sets a one-shot mode flag, calls P normally, then
restores the mode flag — no separate trap entries needed.

Why this is plausible: it sidesteps the entire FNCA/FNCB/FNCC/FNCD
machinery, which has clearly been a chronic source of subtle bugs
(SN-26-csn-regen-fix has been latent forever; the cstack-overwrite
took 5 sessions to diagnose; the new crash signature is post-fix).

Risk: changes the IR contract for FENCE.  May break the
fence_function/ regression tests in ways that are themselves
revealing.

### D3 — PDL-trap-entry extension (the earlier proposal)

Grow FNCA's trap entry from 3 to N descriptors and store outer
state in slots 4..N.  Drop cstack PUSH entirely.  Documented
above in the now-revised Layout section.

Why we are NOT defaulting to this: trace evidence from session
#42 shows that even with byte-correct PDLPTR/PDLHED/NAMICL
restoration via the C-helper migration, the crash persists.
This suggests saving more state in the trap entry won't fix
anything — the bug isn't in WHAT we save, it's in something
the failure walker does after FNCB returns.

Keep on the list because the trace evidence may be misleading
us, and PDL-extension remains the conservative fix if no other
approach pans out.

### D4 — Failure walker reads stale PDL slot 1 — fix at the read site

The session #42 trace shows the crash is at SCIN3 line 11437
reading `D(D_A(PATBCL) + D_A(PATICL))` where PATICL holds a
heap-pointer-shaped value.  PATICL was set by SALT2 from PDL
slot 1.  Slot 1 should hold a then-or descriptor; instead it
holds something whose `.a.i` is a heap pointer.

Possibilities:
- a4. Slot 1 was written legitimately by some earlier matching
  primitive but never overwritten/cleared when FNCC1 wrote
  the seal entry.  In that case the fix is to clear slots
  1..3 of FNCC1's INCRA region before the seal write.
- b4. Slot 1 was written by a primitive that uses `.a.ptr`
  semantics (heap pointer) for its then-or, not `.a.i` semantics
  (offset).  In that case there's a type-tag mismatch and the
  fix is at SALT2 to read `.f` and dispatch on type.
- c4. The slot we're reading is in an entirely different PDL
  region than we think.  The investigation tool would be PDL
  write-tracking.

### D5 — It's not in FENCE; it's in some primitive FENCE composes with

Beauty's `*snoParse *snoSpace` chain composes FENCE with other
pattern primitives.  Maybe the bug is in one of those (e.g. STAR,
ARBNO, BAL) and FENCE is just the messenger.  Test: build a
non-FENCE-using pattern that exercises the same primitive depth
and see if it segfaults too.

### D6 — Recursive-SCAN reimplementation (chosen by F-1, sessions #42–#43)

**This is the design F-2 will implement.**  Restructure FENCE(P) to
match the working shape of STAR (`*P` unevaluated expression) and
EXPVAL: a single forward-dispatch primitive whose C body makes a
**recursive call to SCAN** for the inner pattern, with isolation
provided by a NULL+CURSOR sentinel pushed onto the PDL.

Backed by Gimpel 1973 (CACM 16:2, "A Theory of Discrete Patterns
and Their Implementation in SNOBOL4"), which presents this as the
canonical implementation pattern for compounds that need history-stack
isolation.  See `csnobol4/docs/F-1-findings.md` for full sketch and
rationale.

Why this fixes the bug: FNCA's locals (MAXLEN, LENFCL, PDLPTR, PDLHED,
NAMICL, NHEDCL) live in the C call frame of the FENCE handler for
the duration of the recursive SCAN call.  RSTSTK cannot rewind them
because they're not on cstack.  When SCAN returns, the locals are
still in scope.  The cstack-overwrite bug class is structurally
eliminated.

Why earlier designs (D1-D4) won't work: Layouts A-E of D3
(PDL-extension) were attempted in session #43 — multiple variants,
all failed.  Even byte-correct save/restore via the C-helper
(session #41) crashed at L_SCIN4.  The save/restore mechanism alone
is not the right fix.

Why this works architecturally: ATP, BAL, EXPVAL all use the same
RCALL-with-balanced-PUSH/POP idiom and they don't have this bug.
Make FENCE structurally identical and the bug class is gone.

---

## Investigation plan

The first session on this goal (after F-0 baseline-revert) does
NOT write a fix.  It writes diagnostic instrumentation and
gathers evidence to choose between D1–D5.

Concrete diagnostic targets:
1. **PDL-write-site sweep.**  Find every site in `isnobol4.c`
   that writes to a PDL slot 1 (`D(D_A(PDLPTR) + DESCR) = ...`).
   Add an env-gated logger.  Run tiny repro.  Identify which
   site wrote the bad slot-1 descriptor that SALT2 later reads.
   This is the single most informative thing we can measure.

2. **PDL slot 1 content at every SALT2 entry.**  Log
   `D(D_A(PDLPTR) + DESCR)` at SALT2 entry on every cycle.
   Identify the cycle where slot 1 first contains a
   heap-pointer-shaped descriptor.  Cross-reference with the
   write-site sweep to find the corresponding writer.

3. **FENCE seal verification.**  At FNCC1 (seal write), log
   the slots that FNCC1 INCRA'd into.  Verify they were
   either pristine or owned by FNCC1.  If they were owned by
   inner-P matching that hasn't been popped, we have a FENCE
   leak.

4. **Cross-check on SPITBOL.**  Run the same tiny repro on
   SPITBOL x64 with maximum tracing.  SPITBOL handles this
   pattern correctly.  Compare FNCB/FNCC equivalents'
   behavior.

The result of this investigation is **a clear hypothesis** about
which design (D1–D5) is right, with evidence.  Only then do we
write code.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

Tiny repro (always reproduce first thing, before any code change):
```bash
cat > /tmp/tiny.in <<'EOF'
                  ppStop         =  ARRAY('1:4')
END
EOF
cd /home/claude/corpus/programs/snobol4/demo/beauty
SNO_LIB=. /home/claude/csnobol4/snobol4 -bf -P64k -S64k beauty.sno < /tmp/tiny.in
# expected at F-0 baseline (post-revert):  "Caught signal 11 ... statement 1074"
#   with the OLD signature (L_SALT1 reading PDLPTR.a.i = 0xc0 sentinel).
# expected (fixed): beauty.sno output (lines of formatted SNOBOL4)
```

Full beauty self-host (after tiny repro passes):
```bash
SNO_LIB=. /home/claude/csnobol4/snobol4 -bf -P64k -S64k beauty.sno < beauty.sno | wc -l
# expected: > 500
```

Gate after fix:
```bash
cd /home/claude/csnobol4 && make -f Makefile2 test    # incl. fence_function/
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh         # PASS=7
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh  # PASS=49
```

---

## Background — original bug (sessions #37–#40)

**Cstack-overwrite on nested FENCE.**  FNCA's
`PUSH (MAXLEN, LENFCL, PDLPTR, PDLHED, NAMICL, NHEDCL)` saves 6
values to `cstack` (csnobol4's heap-allocated descriptor stack).
Under nested FENCE recursion, intermediate `RSTSTK` rewinds inside
SCIN1's tail-call BRANCH chain expose FNCA's saved cstack slots
to overwrite by unrelated subsequent pushes.  Crash signature:
`L_SALT1: D(LENFCL) = D(D_A(PDLPTR) + 3*DESCR)` reading from an
address where `PDLPTR.a.i = 0xc0` (= 192 = 12·DESCR sentinel) —
i.e. PDLPTR itself was clobbered with an unrelated integer push.

**Why FNCA is uniquely vulnerable** (verified session #39):
FNCA/FNCB/FNCC live as labels INSIDE SCIN1 separated by tail-call
`BRANCH` chains.  ATP2/EXPV7/ENMI4 also do 6-PUSH but wrap them
around an `RCALL` to a separate C function (TRPHND), which makes
the PUSHes balanced within a single C-stack frame.  Only FENCE has
the asymmetric structure where FNCA pushes and FNCB/FNCC pop
across an `RSTSTK` boundary that can rewind past the pushes.

---

## Why a parallel C-helper stack is the wrong shape

The session #41 attempt added `fnc_save_push` / `fnc_save_pop`
helpers in `lib/pat.c` backed by a `realloc`-grown array.  This
eliminated the cstack-overwrite signature but introduced a NEW
crash (L_SCIN4 ZCL deref — see "Remaining bug" below).  Beyond
the not-actually-fixed-yet problem, the design has structural
issues:

1. **Two stacks for one logical operation.**  Every FENCE entry/exit
   now touches both PDL (the trap entry) AND `fnc_save_stack`.
   These have separate lifetimes, separate growth policies, and
   separate failure modes.  When (not if) someone adds a new
   pattern primitive that does FENCE-like state save/restore,
   they'll have to know about both.

2. **Unwinding mismatch.**  PDL entries unwind automatically when
   the failure walker walks back through SALT1/SALT2.  The
   parallel C-helper stack doesn't — it requires explicit
   `fnc_save_pop` calls at FNCB and FNCC.  If a future fix path
   ever needs to bail out of FENCE state mid-pattern (e.g. on
   error 13/31), the parallel stack will be left in an
   inconsistent state.

3. **No SPITBOL precedent.**  SPITBOL's `p_fna..p_fnd` saves to
   `xs` (its pattern matching stack), which is the analog of
   CSNOBOL4's PDL.  Our oracle solves this exact problem WITHOUT
   a separate stack.  When in doubt, port SPITBOL's structure.

4. **Allocator inside the runtime hot path.**  `realloc` on a
   first-time-FENCE in a long-running program is a soft real-time
   glitch with no benefit.  The PDL is pre-sized at startup and
   never reallocates.

---

## The remaining bug — current crash signature

(With session #41 partial fix in place, csnobol4 @ `1d225f8`.)

```
SCIN1 () at isnobol4.c:11456
11456    D(PTBRCL) = D(D_A(ZCL));
```

Where `ZCL` was just loaded at line 11437 from `D(D_A(PATBCL) +
D_A(PATICL))`.  At crash time, observed via gdb:
- `ZCL = {a={i=0, ptr=0x0}, f=0, v=320}` — NULL descriptor
- `XCL.a.ptr = 0x7eafbecbd660` — valid heap pointer
- `YCL = {a={i=336}, ...}` — small offset
- `PATBCL = {a={i=139293281609616, ptr=0x7eafbe91e790}, ...}` — heap pointer
- `PATICL = {a={i=139293281608656, ptr=0x7eafbe91e3d0}, f=0, v=0}` — **a heap pointer where an offset belongs**

PATICL holds a pointer-sized value but `D_F(PATICL) & FNC` is false
(the FNC flag was lost in the descriptor copy), so SCIN1 falls
through to SCIN3 instead of dispatching via PATBRA.  The wild
PATBCL+PATICL addition reads garbage that maps to a NULL-descriptor-
shaped region; the subsequent `D(D_A(ZCL))` deref at line 11456
segfaults.

**Session #42 trace evidence** (FNC_TRACE instrumentation, reverted)
on the tiny repro:

| # | Event | PDLPTR | PDLHED | NAMICL | NHEDCL | LENFCL |
|---|-------|--------|--------|--------|--------|--------|
| 1 | FNCA #1 entry | a3a0 | a010 | 0x60 | nil | 1 |
| 2 | FNCA #2 entry (nested) | a730 | a3d0 | 0xc0 | 0x60 | 1 |
| 3 | FNCC #1 entry | a7c0 | a760 | 0xc0 | 0xc0 | 1 |
| 4 | FNCC #1 AFT | a730 | a3d0 | 0xc0 | 0xc0 | 1 |
| 5 | FNCA #3 entry | a8e0 | a3d0 | 0xc0 | 0xc0 | 1 |
| 6 | FNCA #4 entry (nested in #3) | aa90 | a910 | 0xc0 | 0xc0 | 1 |
| 7 | FNCC #2 entry | ab20 | aac0 | 0xc0 | 0xc0 | 1 |
| 8 | FNCC #2 AFT | aa90 | a910 | 0xc0 | 0xc0 | 1 |
| 9 | FNCB entry (FNCA #3's fail) | a8e0 | a910 | 0xc0 | 0xc0 | 0 |
| 10| FNCB AFT | a8e0 | a3d0 | 0xc0 | 0xc0 | 0 |
| 11| → segfault in failure walker |

After FNCB's `fnc_save_pop`, both PDLPTR and PDLHED match FNCA #3's
pre-state byte-for-byte (rows 5 vs 10).  FENCE arithmetic is correct
on this path.  The crash happens AFTER FNCB's `BRANCH(FAIL)` — the
failure walker reads PDL slot 1 at offset PDLPTR+DESCR and gets
a heap-pointer-shaped descriptor.  Note also: FNCB entry at row 9
has `LENFCL=0`, meaning we entered FNCB via SALF1 (which clears
LENFCL) rather than SALT1 (which restores LENFCL from trap-entry
slot 3).  This affects which slot-3 contents FNCB sees.

The crash MAY clear once the cstack-overwrite is properly fixed
via PDL-extension (the C-helper migration was incomplete or wrong;
PDL-extension may make this go away as a side effect).  If it
doesn't, it's a separate bug in the failure walker's interaction
with FENCE-sealed regions and gets its own sub-rung.

---

## SPITBOL reference (read first)

Source of truth: `x64/sbl.min` lines 11473–11500 (doc block) and
11978–12039 (`p_fna..p_fnd` implementation).

SPITBOL saves only TWO things on `xs` at FENCE entry: `pmhbs`
(pattern history-stack base, analog of PDLHED) and an indirect
`=ndfnb` pointer (FNC-trap-back link).  No save of MAXLEN, no
save of LENFCL beyond what the trap entry itself carries, no
save of name-list state.  CSNOBOL4's 6-item save list is heavier
than necessary even ignoring the cstack-overwrite issue.

Whichever design (D1–D5 above) we ultimately pick, the SPITBOL
implementation is the reference for what state actually needs
preserving and how a robust FENCE behaves under nested recursion.
Read it before writing any code.

---

## Audit of what genuinely needs cross-RCALL persistence

(Verified session #40.  Useful as background; informs but does
not decide between D1–D5.)

| Value | Save needed? | Reasoning |
|-------|--------------|-----------|
| MAXLEN | NO | SCNR reloads from XSP at every scanner entry (v311.sil:3536).  Never preserved across pattern recursion. |
| LENFCL | partly | Already in trap-entry slot 3 from FNCA's `PUTDC PDLPTR,3*DESCR,LENFCL`.  SALT1 restores it before FNCB dispatch.  SALF1 path enters FNCB with LENFCL=0 — verify whether outer-LENFCL recovery matters there. |
| PDLPTR_outer | YES (under save/restore framing) | Currently derived in FNCC via `MOVD PDLPTR,PDLHED` + `DECRA -3*DESCR`.  Derivation is correct ONLY when outer PDLPTR == outer PDLHED at FNCA-time.  Not safe in general. |
| PDLHED_outer | YES (under save/restore framing) | FNCA does `MOVD PDLHED,PDLPTR` to set new inner PDLHED.  Outer value must be saved.  SPITBOL's `pmhbs`. |
| NAMICL_outer | YES (under save/restore framing) | Inner-P pattern primitives (NME/ENME/DNME) write to NAMICL.  Outer value needs explicit restore. |
| NHEDCL_outer | YES (probably, under save/restore framing) | Pre-fix POP restored NHEDCL.  Audit said `NHEDCL == NAMICL at FNCA-time`, but for nested FENCE that's only true for the OUTERMOST.  Trace evidence inconclusive. |

**Caveat:** every "save needed" entry above is conditional on
the fix being a save/restore design (D3).  Under D1 (fence-aware
walker) or D2 (different pattern shape), most of these become
moot — the outer state is not corrupted in the first place because
the failure walker doesn't reach into the FENCEd region.

---

## Active rung — F-0 (revert session #41 C-helper landing)

**Done-when:** csnobol4 working tree matches `b01b47b` (the
emergency-handoff commit BEFORE session #41's partial fix).  Tiny
repro reproduces the ORIGINAL crash signature
(`L_SALT1 PDLPTR.a.i=0xc0`), not the session #41 signature
(`L_SCIN4 ZCL deref`).

**Steps:**
- [x] `cd /home/claude/csnobol4 && git revert --no-edit 1d225f8`
- [x] Build: `bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh`
- [x] Tiny repro: confirm OLD crash signature (`Caught signal 11 in statement 1074`).
- [x] gdb confirm: `CSN_NO_SEGV_HANDLER=1 gdb --args ... < /tmp/tiny.in` shows L_SALT1 at the crash, NOT L_SCIN4.
- [x] fence_function/ regression: `cd /home/claude/csnobol4 && make -f Makefile2 test` — confirm 10/10 tests still PASS.
- [x] Commit revert with message `F-0: revert session #41 C-helper FENCE save migration; baseline restored before fix-design investigation`.
- [x] Push.

**No code changes; pure revert.** This step exists to give the
investigation rung (F-1) a clean starting point.  We do not yet
know what the fix is — F-0 only ensures we are diagnosing the
ORIGINAL bug, not the session #41 partial-fix's downstream effects.

---

## Active rung — F-1 (investigation, not implementation)

**Done-when:** we have **a clear hypothesis** about which design
(D1–D5, or some sixth not-yet-named candidate) is correct,
backed by diagnostic evidence — not by argument.  At that point
F-1 closes and a new rung F-2 opens for the actual implementation.

**This rung writes NO production code.**  Diagnostic
instrumentation only, reverted before any commit per RULES.md.
The goal is to read the bug, not to fix it.

**Steps:**
- [x] **Step 1: SPITBOL reading.**  Read `x64/sbl.min:11473–11500`
      (FENCE doc block) and `11978–12039` (`p_fna..p_fnd`).  Record
      what state SPITBOL preserves and how its failure walker
      handles a sealed region.  Note any structural differences
      from CSNOBOL4's FNCA/FNCB/FNCC/FNCD shape.
      **Outcome:** SPITBOL saves only `pmhbs` + `=ndfnb` indirect on
      single failure stack `xs`.  CSNOBOL4 saves 6 things on a
      separate cstack — that's the structural mismatch.  See
      `docs/F-1-findings.md`.
- [x] **Step 2: PDL-write-site sweep.**  Found via reading SCIN3
      (line 11436), SCNR5 (3553), ATP (3941), BAL (analogous), and
      FENCE primitives.  All write at PDLPTR+1..+3 after INCRA-by-3.
- [x] **Step 3: Add a PDL-slot-1 write logger.**  Done inline as
      `FNC_TRACE=1` env-gated trace at FNCA-pre, FNCA-post, FNCB-pre,
      FNCB-post, FNCC-pre, FNCC-post.
- [x] **Step 4: Add a SALT2 read-side logger.**  Trace evidence
      already showed the read site reads garbage — augmented logging
      to confirm slot 4-6 of D3-Layout-B were being overwritten by
      the next SCIN3 push.
- [x] **Step 5: Find the bad write.**  Identified — under D3 Layout B,
      saves at PDLPTR+4..+6 overwritten by subsequent SCIN3 push.
      Under D3 Layout C, saves at PDLPTR+1..+3 overwrite the
      SCIN3-around-FNCA entry.  ALL D3 layouts have a placement
      conflict with the failure walker's PDLPTR-relative reads.
- [x] **Step 6: Decide between D1–D5.**  None of D1-D5 fit the
      evidence.  Per Gimpel 1973 paper (page 8, Figure 11) and the
      working precedents of STAR/EXPVAL/ATP/BAL, a SIXTH design — D6
      Recursive-SCAN — emerges as the correct fix.  Added to the
      design space above.
- [x] **Step 7: Revert all instrumentation per RULES.md.**
      Working tree clean — `git status` shows no modified files.
- [x] **Step 8: Commit a NOTES file** — `csnobol4/docs/F-1-findings.md`
      contains full investigation summary, paper citations, layout-by-
      layout failure analysis, and D6 implementation sketch.
- [x] **Step 9: Open F-2.**  Implementation rung opened — see below.

**Risk:** investigation rungs sometimes fail to converge on a
clear answer.  If F-1 produces ambiguous evidence after one full
session, the right move is to commit the partial findings as a
notes file and re-plan, not to start writing code on a hunch.

**Anti-goal:** do NOT pre-decide between D1–D5.  An earlier draft
of this goal file proposed D3 (PDL-extension) as the canonical
fix without evidence.  That was a mistake.  The trace evidence we
already have suggests the bug may not be in the save/restore
mechanism at all — saving more state may not help.  Resist the
urge to start writing FNCA/FNCB/FNCC edits before F-1 closes.

---

## Active rung — F-2 (D6 implementation: recursive-SCAN reimplementation)

**Done-when:**
- `csnobol4 -bf -P64k -S64k beauty.sno < /tmp/tiny.in` runs without
  segfault and produces >0 lines of output.
- `csnobol4 -bf -P64k -S64k beauty.sno < beauty.sno | wc -l` ≥ 500.
- `cd csnobol4/test/fence_function && make csnobol4` shows 10/10 PASS.
- SCRIP Smoke=7 and Broker=49 preserved.

**Design:** D6 from the Open Design Space section above.  Full sketch
in `csnobol4/docs/F-1-findings.md`.

**Steps:**
- [x] **Step 1: STAR/EXPVAL precedent reading.**  Read `STARP6`,
      `L_STARP6`, `L_STAR1`, `STAR1` in `isnobol4.c` and `v311.sil`.
      Confirm the shape we'll mirror.  Note pattern-node layout for
      STAR (likely 4-descriptor: function descr, then-or, value-
      residual, ARG).
- [x] **Step 2: FNCPP node-write fix (session #45).**  Four bugs
      fixed in FNCPP (isnobol4.c + snobol4.c) and data_init.h/h2:
      (a) `int_t base = D_A(ZPTR)` cast — replaced with
      `D_A(D_A(ZPTR))` pattern throughout.
      (b) slot[1] stored `D(FNCAFN)` (value copy, a.i=37) instead of
      pointer — fixed to `D_A=ptr(FNCAFN), D_F=FNC, D_V=3`.
      (c) `D_V=2` in fncafn/fncapt+1 — fixed to `D_V=3` so cpypat
      walks 5 descriptors (mirrors STARFN) and copies slot[4]=P in
      concatenated patterns.
      (d) FNCA had no SCFLCL PDL sentinel before inner SCIN call —
      inner scan's failure walker crashed into outer SCONCL.  Fixed
      by mirroring STARP6: push SCFLCL trap, set PDLHED=PDLPTR
      (sentinel base), then push outer state + SAVSTK + SCIN.
      **fence_function/ suite: 10/10 PASS.**
- [x] **Step 3: IPC two-way divergence hunt for beauty self-host.**
      Run via `STDIN_SRC=/tmp/tiny.in PARTICIPANTS="csn spl" \
      bash SCRIP/scripts/test_monitor_3way_sync_step_auto.sh \
      corpus/programs/snobol4/demo/beauty/beauty.sno` (run with the
      beauty dir as CWD and `SNO_LIB=.` so includes resolve).  First
      divergence: csn record #1 = `LABEL stno=2`, spl record #1 =
      `LABEL stno=1` — protocol-shape difference, not a bug.  Real
      semantic divergence surfaces immediately as csn dies SIGPIPE
      after stmt 2 of `global.inc` while spl runs cleanly through
      beauty's load and parse phases.

      **First FENCE-specific bug located and fixed (csnobol4 c314e49):**
      `L_FNCBX` in `isnobol4.c`/`snobol4.c` did `BRANCH(FAIL)` after
      restoring outer cstack state; that returns from SCIN1 with the
      outer alternation's PDL trap entry unconsumed.  Fix: replace
      `BRANCH(FAIL)` with `goto L_TSALT` so the local failure walker
      consumes the outer trap and lets the alternation try its second
      branch.  Minimal repro `p = FENCE('a') | 'b'` matched against
      `'b'` now matches as it does in SPITBOL.  fence_function/ still
      10/10 PASS.  beauty advanced past "Parse Error" — now segfaults
      later at stmt 1074 (line 616, the *snoParse top-level call).
- [ ] **Step 3a: TXSP corruption in walker descent (session #63 diagnosis).**

      **Current concrete task for next session (#64):**

      Find the exact line in `isnobol4.c` that sets `S_L(TXSP)` to a
      heap-pointer-shaped value during the failure walker's descent
      through the leaked-region of `*var`-dispatched FENCE(P).

      **Why this is the task** (session #63 evidence):

      With the s58 paired-STREXCCL sentinels committed, all 6 fence_suite
      CRASHes are gone (44 OK / 4 FAIL / 0 CRASH).  The remaining 4 FAILs
      (119, 124, 127, 129) all produce `unexpected match` — wrong-answer
      semantics, not memory corruption.

      Session #63 instrumented L_RPSII and L_SALT2 entries (see
      `csnobol4/docs/F-2-Step3a-session63-diag.txt`) and ran the 5-line
      repro on test 119.  The trace shows:

      1. RPOS(0) fires correctly with TXSP=0, MAXLEN=2, computes
         TVAL=2/NVAL=0 → goto L_TSALF (clean fail).  Arithmetic is fine.
      2. Walker descends through 6 SALT2 events.
      3. Between SALT2 #5 (slot1=heap-pointer-with-FNC-set, slot2=0x...b5a0
         = cmd's PATBCL — i.e. STREXCCL fires, restoring PATBCL=cmd) and
         SALT2 #6, **TXSP transitions from 0 to 140702518392224**, which
         is exactly cmd's PATBCL value.

      The corruption is `S_L(TXSP) = D_A(<heap-pointer-shaped-thing>)`
      executed during walker descent.  Some primitive is reading what
      should be a small integer cursor and getting a heap pointer, then
      assigning it to TXSP.

      **What was ruled out:**

      - Session #61's "in-place SCIN3-FENCEPT overwrite" — implemented in
        s63, gates show NO change (44/4/0 unchanged).  Reverted.  The
        bug is NOT the SCIN3-FENCEPT trap re-dispatching FNCA.
      - Earlier sessions ruled out: PDLPTR rewind arithmetic (s49–s51),
        cstack overwrite (closed by s58), single-iteration STREXCCL alone
        (s56), targeted slot-zeroing (s54).

      **Concrete steps for session #64:**

      1. Apply diagnostic: `csnobol4/docs/F-2-Step3a-session63-diag.txt`
         (L_RPSII + L_SALT2 trace).
      2. Find every TXSP-write site:
         ```bash
         grep -n 'S_L(TXSP)\s*=' isnobol4.c
         grep -n 'S_L(TXSP)\s*+=' isnobol4.c
         ```
         Likely sites include: SALT2 line 11498, SCIN3 fall-through path,
         L_ANYC6, L_TBII, L_RTBII, L_SPNC5, primitive success paths.
      3. Add an env-gated logger at every TXSP-write site:
         ```c
         if (getenv("TXSP_TRACE")) {
             fprintf(stderr, "TXSP_WRITE site=%d new=%ld old=%ld YCL=%lx XPTR=%lx\n",
                 SITE_ID, (long)D_A(YCL), (long)S_L(TXSP),
                 (long)D_A(YCL), (long)D_A(XPTR));
         }
         ```
         (One per site, with unique SITE_ID = source line number.)
      4. Run `RPOS_TRACE=1 WALK_TRACE=1 TXSP_TRACE=1 ./snobol4 -bf
         /tmp/repro5.sno` where `/tmp/repro5.sno` is:
         ```
                 cmd = FENCE('a' | 'ab')
                 outer = ARBNO(*cmd)
                 s = 'ab'
                 s POS(0) *outer RPOS(0)                               :S(BAD)F(GOOD)
         BAD     OUTPUT = 'unexpected match'                            :(END)
         GOOD    OUTPUT = 'sealed'
         END
         ```
      5. Find the SITE_ID where TXSP gets set to 140702518392224 (or
         whatever the heap-pointer value is in the new run — it will be
         a value with `D_A == cmd's PATBCL`).
      6. Decide fix candidates based on what site fires:
         - If SALT2 line 11498 (`S_L(TXSP) = D_A(YCL)`): the trap being
           dispatched has a wrong slot[2] (YCL).  Fix where that trap
           was pushed (likely an inner-SCIN3 push during cmd's body
           matching, where YCL got computed from a corrupted descriptor).
         - If a primitive (SPNC5 / TBII / etc.): the primitive is being
           dispatched under wrong PATBCL state, with XPTR/YCL holding
           pointer-shaped values.  Fix is upstream — that primitive
           should not have been reachable.
      7. Test gates AFTER fix: guard5, Tier F 16/16, fence_function 10/10,
         fence_suite ≥45/48, beauty ≥500 lines.
      8. Commit only if all gates pass; save diff + findings if not.

      **Floors that must be preserved (unchanged from session #58):**
      - fence_function/ 10/10 PASS.
      - fence_suite Tier F (132–147) 16/16 PASS.
      - fence_suite Tier A–E ≥ 44/48 (don't lose the 6 CRASHes that
        s58 promoted to OK).
      - guard5 (`cmd=(LEN(1)|LEN(2)); outer=(*cmd 'X'); s='ABX'`) must
        continue to produce `inner backtrack worked`.

      **Files of interest for session #64:**
      - `csnobol4/isnobol4.c` — TXSP write sites.
      - `csnobol4/docs/F-2-Step3a-session63-findings.md` — full s63 trace.
      - `csnobol4/docs/F-2-Step3a-session63-diag.txt` — applied diff for
        existing diag.
      - `csnobol4/docs/F-2-Step3a-session58-paired-strexc-attempt.diff` —
        the s58 architectural foundation (NOT YET committed; apply first
        if working from a HEAD that doesn't have it integrated).

      **History note:** Step 3a has been the active task since session
      #45 (now 19 sessions).  Sessions #58 made the most progress (6
      CRASHes → 0).  Session #63 reduced the bug to a single-line
      diagnostic question.  Sessions #44–#62 narrative is preserved
      below in the per-session "## Session #N update" sections; do
      NOT repeat their refuted hypotheses.

- [ ] **Step 3b: SIL/C consistency cleanup.**  Per RULES.md the SIL is
      the source of truth; the same edits made in `isnobol4.c` and
      `snobol4.c` for cpypat / FNCPP / FNCA must be ported back to
      `v311.sil` and `lib/pat.c` (pat.c is C source, not generated, so
      that one is already canonical). Also: the SIL FNCAPT template at
      v311.sil:12203 still says `4*DESCR / v=2` — it needs to be
      reconciled with the implemented C 5*DESCR / v=4 layout.
- [ ] **Step 4: Build clean after Step 3a fix.**
      `bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh`
- [ ] **Step 5: fence_function/ regression.**  10/10 expected.
- [ ] **Step 6: Tiny repro.**  ≥1 line output, no segfault.
- [ ] **Step 7: Full self-host.**  beauty.sno ≥500 lines.
- [ ] **Step 8: Smoke gates.**  Smoke=7, Broker=49.
- [ ] **Step 9: Commit.**  csnobol4 first, .github last.

**Risks listed in `docs/F-1-findings.md`** under "Risks for F-2".
Pattern-shape change is a contract break; verify by running the
fence_function/ regression early.

---

## Closed sub-rungs

- **F-0 (revert session #41 C-helper)** — closed session #42.
  csnobol4 @ `4172be1`.  Original L_SALT1 crash signature restored
  as expected baseline.
- **F-1 (investigation)** — closed session #43.  D6 chosen.
  Findings notes in `csnobol4/docs/F-1-findings.md` (committed in
  same session as F-1 close).

---

## Diagnostic infrastructure (already in tree)

- **`CSN_NO_SEGV_HANDLER=1`** env var bypasses csnobol4's friendly
  signal-11 handler so gdb gets a clean backtrace.  Always-off in
  normal runs.  Source: `lib/init.c:688`.

- **gdb HW watchpoints DO NOT WORK in this container** — see
  RULES.md "Debugging" section.  Use C-level `__builtin_trap()`
  + `_check()` helpers instead.

- **Diagnostic patches are diagnostic — never commit them.** Per
  RULES.md.  Keep `.orig` backups, revert before commit.

- **build with `-O0 -g`:** `make -f Makefile2 OPT="-O0 -g" xsnobol4`
  then `cp xsnobol4 snobol4`.  The default `-O3` build inlines too
  aggressively for clean stack traces.

---

## Bypass for blocked work

GOAL-LANG-SNOBOL4 sub-rung SN-26-bridge-coverage-h is now
2-way (SPITBOL + scrip), unblocked by this goal — see
`GOAL-LANG-SNOBOL4.md` top-of-file note.  No SCRIP work
depends on this goal closing.

The original 3-way harness restoration becomes possible once
F-1 lands.

---

## Files of interest

| File | Role |
|------|------|
| csnobol4/v311.sil:4093-4156 | FNCA/FNCB/FNCC/FNCD SIL source — primary edit target |
| csnobol4/lib/pat.c:127-184 | C save-helpers (post session #41) — DELETE in F-1 |
| csnobol4/isnobol4.c:12258-12299 | generated FNCA/B/C/D label code — regen target |
| csnobol4/snobol4.c (same range) | generated FNCA/B/C/D label code — regen target |
| csnobol4/genc.sno | SIL → C generator (regen tool) |
| csnobol4/test/fence_function/ | 10-test regression suite |
| corpus/programs/snobol4/demo/beauty/beauty.sno | self-host target |
| x64/sbl.min:11473-11500 | SPITBOL FENCE doc block (read first) |
| x64/sbl.min:11978-12039 | SPITBOL p_fna..p_fnd reference |

---

## Closed-rung pointers

- `git log --grep "SN-26-bridge-coverage-i" --oneline` (csnobol4 + .github) — pre-pivot history
- `git log --grep "GOAL-CSN-FENCE-FIX" --oneline` — this goal once landed

---

## Current state

**HEADs:**
- csnobol4 @ session #66 (working tree CLEAN at HEAD `451ccae`; session #66 docs commit landed; no runtime change since #64)
- SCRIP @ `06433f90`
- corpus @ session #65 `6f00145` (53 tests at IDs 100–152; Tier G additions + 118/127/140/141 corrections)
- x64 @ `71ff275`
- active step → **F-2 Step 3a** (sessions #49–#66; session #58 paired-sentinel eliminates all CRASHes; session #64 commits TXSP write-site fix at isnobol4.c:11498 — gate-neutral; session #65 verifies test suite against SPITBOL oracle, expands to 53 tests with Tier G; session #65 (cont) isolates L_FNCD discriminator (`BRANCH(FAIL)` → `goto L_TSALT`); **session #66** applies + falsifies the composed fix (L_FNCD goto-L_TSALT + FNCA-success zeroing): zeroing fired correctly but had no effect; trace evidence on test 148 pinpoints bug to **a SCIN3-pushed entry inside the protected leak region** at PDLPTR=e910 with slot[1]={a=0x60,f=0}, dispatched under switched PATBCL=cmd via session #64's SCIN3 fall-through path. Resolves the session #62 vs #64 tension definitively: bug is on failure-walker path (#64) but inside the protected region, NOT in an "abandoned" region. Refutes FNCA-success zeroing (the entry lives in the OUTER scan's frame, not FNCA's). Recommends **option (A2)**: at L_STARP2 success, conditionally zero non-FNC entries in [STREX_entrypdl+3*DESCR..PDLPTR] IF an FNCDCL exists in the region. Should preserve guard5 (no FENCE → no FNCDCL → no zeroing) and fix all 7 cluster A/B FAILs. Findings in `csnobol4/docs/F-2-Step3a-session66-findings.md`. Diagnostic patch saved as `csnobol4/docs/F-2-Step3a-session66-diagnostic.diff`. csnobol4 advanced to `451ccae`. Beauty 42 lines unchanged.)

**Gates as of session #65 end (working tree CLEAN, no runtime code changed since session #64):**
- fence_function/ suite: **10/10 PASS** (preserved across baseline / s52 / s56 / s58 / s64 / s65)
- fence_suite/ (53 tests after Tier G additions):
  - csnobol4 baseline (HEAD `5fbf2ce`):       **46 OK / 7 FAIL / 0 CRASH**
  - SPITBOL oracle (`-bf`):                   **53 OK / 0 FAIL / 0 CRASH** (clean — first time)
  - The 7 csnobol4 FAILs: 119, 124, 127, 129, 148, 149, 152 (bug-class regression target)
  - 150, 151 PASS (negative discriminators that prove bug needs ARBNO + `*var` specifically)
- guard5 regression-prevention: ✓
- Tier F (16 depth-stress tests at IDs 132–147): 16/16 PASS
- beauty self-host: 42 lines (unchanged since #58)

**Session #65 also corrected three pre-existing corpus errors:**
- Test 127 `.ref` was generated under SPITBOL `-b` (case-fold ON) but Makefile invokes `-bf` (case-fold OFF). Regenerated under `-bf`.
- Tests 140, 141 used label names colliding under SPITBOL's case-fold default (`shift`/`Shift`, `grab`/`Grab`). Renamed for cross-dialect portability.
- Test 118 documented as structurally degenerate — `outer` assigned AFTER the match, so `*outer` dereferences unassigned variable and FENCE machinery never runs. The test "passed" for the wrong reason. Test 149 added as the proper version.

**Pre-session-#65 history below this line — superseded gates marked (stale):**

**Gates as of session #58 end (working tree CLEAN, no code changes committed):**
- fence_function/ suite: **10/10 PASS** (preserved across baseline / s52 / s56 / s58)
- fence_suite/ (48 tests, Tier A–F):
  - csnobol4 baseline (HEAD `8ebab64`):       **40 OK / 2 FAIL / 6 CRASH**
  - csnobol4 + session #52 patch:             **43 OK / 3 FAIL / 2 CRASH**
  - csnobol4 + session #56 patch (s52+strexccl): **43 OK / 3 FAIL / 2 CRASH** (no improvement over s52)
  - csnobol4 + **session #58 patch** (s52+s56+paired-bottom): **44 OK / 4 FAIL / 0 CRASH** ← 109/113/130 promoted to OK
  - SPITBOL oracle: 47 OK / 1 FAIL (test 127 known-bad-`.ref`)
- guard5 regression-prevention: ✓ across all four states
- Tier F (16 depth-stress tests): 16/16 across all four states
- beauty self-host: 35 lines baseline → **42 lines with s58** (first non-zero gain since #45)

**What session #49 found:**

1. **The bug class beauty triggers, in 5 lines.** The minimal reproducer:
```snobol
        cmd = FENCE('a' | 'ab')
        s = 'ab'
        s  POS(0) *cmd RPOS(0)  :s(ok)f(fail)
ok      OUTPUT = 'ok'  :(done)
fail    OUTPUT = 'fail'
done
END
```
csnobol4 SIGSEGVs at `isnobol4.c:11437` (SCIN1: `D(ZCL) = D(D_A(PATBCL) + D_A(PATICL))` with PATICL = `stdio_ops+16`-shaped pointer); SPITBOL prints `fail`.

2. **The bug is in FNCA's seal slot[2] write.** Currently FNCA writes `D(PDLHED)` — the OUTER-SCAN PDLHED (just popped from cstack) — into the FNCDCL trap entry. When the seal fires, L_FNCD does `PDLPTR = YCL` (= seal slot[2]). The walker then reads slot[1] at `outer-scan-PDLHED + DESCR` — STALE memory because outer-scan PDLHED is not a valid PDL position inside the *cmd matching context. STARP6 (the `*` matcher) had pushed SCFLCL at PDLPTR'+DESCR where PDLPTR' = FNCA's outer-PDLPTR-at-entry value `S` — but `S` ≠ outer-scan-PDLHED.

3. **Proposed fix (verified working in isolation):** synthesize a PTR descriptor pointing to `S = current PDLPTR - 3*DESCR` and store IT in seal slot[2]:
```c
D_A(TMVAL) = D_A(PDLPTR) - 3*DESCR;
D_F(TMVAL) = D_V(TMVAL) = 0;
D(D_A(PDLPTR) + 2*DESCR) = D(TMVAL);
```
Result: ✓ min_crash converts SEGV → clean fail. ✓ nested *cmd1*cmd2 case works. ✓ fence_function/ 10/10 preserved. ✗ Beauty self-host: clean "Parse Error" → SEGV (regression in error class — same crash signature `PATICL=0xc0` from F-0 baseline).

4. **The fix is NOT committed.** Per RULES.md, turning clean failure into crash is a regression in error class. The deeper bug exposed by beauty needs a separate fix that likely involves PDL slot zeroing for abandoned regions during FNCA's success-path rewind. The full investigation is in `csnobol4/docs/F-2-Step3a-findings.md`.

**What session #49 produced:**
- `csnobol4/docs/F-2-Step3a-findings.md` — full investigation, gdb-verified diagnosis, proposed fix code, rationale for not committing yet.
- `corpus/crosscheck/patterns/068_pat_fence_fn_via_var.sno` and `.ref` — minimal regression test (currently fails on csnobol4, passes on SPITBOL).
- This goal-file state update.

**What remains:**
1. **Step 3a continued** — implement the deep-nesting fix together with the seal slot[2] fix, so beauty stops crashing AND ≥500 lines self-host. The seal slot[2] fix from `F-2-Step3a-findings.md` is ready to apply once the deep-nesting bug is resolved.
2. **Step 3a continued** — add test 068 to `csnobol4/test/fence_function/Makefile` TESTS list (currently fails — will pass with the fix).
3. **Step 3b** — port C edits back into `v311.sil` for SIL/C consistency.
4. **Steps 4–9** — clean build, regression, beauty, smoke gates, commit.

**What session #50 added (no code, diagnosis only):**

Session #50 re-verified session #49's seal slot[2] = PDLPTR-3*DESCR fix
(same result: min_crash clean, fence_function 10/10, beauty regresses
clean→SEGV).  Then went deeper with C-level traps inserted at SCIN3
slot[1] write and SALT2 slot[1] read, both gated on `XCL == {0x90,0,64}`.
In a single beauty run, captured BOTH events:

- SCIN3 push wrote slot[1]=`{0x90,0,64}` at PDLPTR=0x..b700, **PATBCL=0x..eeeca90**.
- Later, SALT2 read THAT SAME slot, **PATBCL=0x..ef5dc40** (different).

The bad slot was a then-or trap pushed under an inner sub-pattern
(dispatched via STAR/`*var`).  The walker reaches it under the OUTER
pattern's PATBCL → SCIN3 fall-through dispatches `OUTER_PATBCL + 0x90`
→ garbage memory → SEGV.  This is a **PATBCL context mismatch**, not
a cstack-overwrite as session #49 had hypothesized.

Re-read of SPITBOL `p_fnc/p_fnd` (`x64/sbl.min:11978-12047`) revealed
TWO things missed in earlier sessions:
- SPITBOL has an optimization where NO seal is placed if inner P
  leaves no alternatives (`pfnc1` path).
- SPITBOL's `p_fnd` does `mov xs,wb; brn flpop` — `flpop` consumes
  ONE MORE trap entry beyond the seal's rewind target.  This is the
  trap that originally dispatched FENCA (the SCIN3-around-FENCEPT
  in CSNOBOL4 terms).

The CSNOBOL4 seal currently rewinds to FENCA-entry-PDLPTR.  It needs
to rewind ONE TRAP REGION DEEPER (entry-PDLPTR - 3*DESCR).  Full
arithmetic walk-through and Plan B (PATBCL save in extended seal
entry) documented in `csnobol4/docs/F-2-Step3a-findings.md` "Session
#50 update" section.

**Honest circularity check (per RULES.md):**

The seal slot[2] = PDLPTR-3*DESCR fix was already proposed and
verified in session #49.  Session #50 partially repeated that work
before confirming it via git log inspection.  The genuinely-new
session #50 contribution is the PATBCL context-mismatch diagnosis
and the SPITBOL `flpop` re-reading.  Session #51 should NOT re-test
the seal slot[2] fix in isolation — that has been verified twice.
Session #51 should implement the rewind-one-deeper arithmetic and
test against beauty directly.

---

## Session #51 update — fence_suite/ landed; 4 distinct bug classes mapped

Session #51 implemented the rewind-one-deeper fix proposed by session #50
(slot[2] = PDLPTR - 6*DESCR instead of -3*DESCR) and tested it.  Result:

- ✅ `min_crash.sno` (`*cmd RPOS(0)` against FENCE alts): SEGV → `fail`.
  Same outcome session #49 already had.
- ✅ fence_function/ 10/10 preserved.
- ❌ Beauty self-host: still SEGV at stmt 1074 (33 lines). Regression
  from baseline's clean 35-line "Parse Error".

Per RULES.md (regression in error class is unsafe to commit), the
arithmetic fix was reverted before commit.  This is the **same outcome
as sessions #49 and #50** — the seal slot[2] fix alone is correct in
isolation but doesn't close the gate.

### What session #51 produced (the genuinely-new contribution)

Pivoted from continuing the diagnostic spiral to **building a 32-test
FENCE regression suite** that maps the bug landscape concretely:

- `corpus/crosscheck/patterns/100..131` (32 new tests)
- `csnobol4/test/fence_suite/` (Makefile + README)
- 5 tiers: baseline (A) / *var indirection (B) / ARBNO+FENCE (C) /
  real grammars (D: calc, regex, JSON) / beauty-class (E)

**Baseline result on csnobol4 HEAD: 26 OK / 4 FAIL / 2 CRASH.**

The 6 non-passing tests reveal **4 distinct csnobol4 FENCE bugs**, all
absent in fence_function/'s 10/10 PASS coverage:

| Bug | Tests | Shape |
|-----|-------|-------|
| 1. Outer-alt fall-through after FENCE-via-`*var` continuation fails | 114, 124 | `(*cmd 'X' \| *cmd 'Y' \| LEN(0))` where `cmd=FENCE(...)` |
| 2. Conditional-assign `.` inside FENCE not committed on success | 127 | `FENCE(num)` where `num = digits . N` |
| 3. SEGV on `*outer`/ARBNO/`*cmd`/FENCE triple indirection | 119, 129 | The beauty.sno stmt 1074 bug class |
| 4. Concat of two `*var`-FENCE with mismatched alt length | 130 | `outer = *cmdA *cmdB` under `*outer` |

Test **119 / 129** is the smallest known repro of the beauty crash —
5 lines.  Bug 3 is the highest priority; bugs 1, 4 likely share root
cause; bug 2 is on a separate axis (conditional-assign commit through
recursive-SCIN return).

### Recommended next-session approach

Stop iterating on isolated repro fixes.  The session #44–#51 pattern of
"land a fix that passes fence_function but fails beauty" suggests
fence_function's 10 tests have insufficient coverage to drive
correctness.  The new 32-test suite has the scope.

For session #52:

1. Commit no code until **all 4 tier C/E CRASH tests pass** (119, 129,
   118, 116).  Tier A/B sanity-floor (16 tests) must stay green.
2. Pivot off the seal slot[2] / -6*DESCR arithmetic line of attack.
   Three sessions (#49, #50, #51) have validated it works in isolation
   and fails on beauty — that's enough evidence the underlying bug
   isn't in the seal arithmetic.  Bug 2 (conditional-assign commit)
   suggests the issue is in how D6's recursive-SCIN call returns
   match-state to the outer SCIN frame, not in the seal.
3. Investigate the conditional-assign-not-committed path (bug 2) first
   on test 127.  It's a non-crashing FAIL — easier to instrument than
   a SEGV, and may reveal the same underlying mechanism that breaks
   bugs 1, 3, 4.

### Honest circularity check (session #51)

Sessions #44–#51 = 8 sessions on F-2 Step 3a, beauty self-host stuck at
33–35 lines for the entire run.  Each session has landed a real fix and
each session has been blocked by the next-deeper bug.  This pattern is
visible in the goal file's own state notes.

The 32-test suite is the first session #51 deliverable that DOESN'T touch
the FNCA/FNCB/FNCC/FNCD code.  It's an explicit attempt to break the
---


## Session #52 update — SPITBOL-aligned flpop fix (verified for *var class, NOT committed)

Session #52's genuinely-new contribution: **the first L_FNCD modification
in the F-2 Step 3a series.**  Sessions #49–#51 only adjusted seal slot[2]
arithmetic; L_FNCD itself was always `D(PDLPTR)=D(YCL); FAIL`.

### What session #52 did

1. Re-read SPITBOL `p_fna..p_fnd` (`x64/sbl.min:11978-12046`) and `flpop`
   (`sbl.min:3144`, doc at `:16234`).  Identified the previously-underweighted
   detail: `p_fnd` does **two** things — `xs=wb` (rewind to inner base) AND
   `flpop` (pop one more entry = the p_fna entry itself).  The CSNOBOL4
   L_FNCD was missing the flpop step.

2. Implemented the corresponding two-part fix:
   - **FNCA success path (slot[2] write):** store `entry-PDLPTR` (= "inner
     base", `PDLPTR - 3*DESCR` at seal-push time) instead of `D(PDLHED)`.
   - **L_FNCD body:** after `PDLPTR = YCL`, add `D_A(PDLPTR) -= 3*DESCR`
     (the flpop equivalent — consumes the SCFLCL trap entry, mirroring
     SPITBOL's `flpop` consuming p_fna's 2-word entry).

3. Tested:
   - fence_function: **10/10 PASS** (preserved)
   - fence_suite: **26/4/2** (up from baseline 24/2/6 — first time 109 and
     113 PASS on csnobol4)
   - beauty: regression — clean Parse Error → SEGV at stmt 1074

4. Per RULES.md (regression in error class is unsafe to commit), reverted
   the working tree to clean.  Saved the patch as
   `csnobol4/docs/F-2-Step3a-session52-flpop-fix.patch` so session #53 can
   apply it without re-deriving.

### Why session #52 stopped where it did

The remaining 2 CRASHes (119, 129) and the beauty regression all share
**the same crash signature**: `PATICL = 0xc0` (= 12*DESCR) with `f=0`
(no FNC), causing SALT2 to fall through to L_SCIN3, which dispatches at
`OUTER_PATBCL + 0xc0` → garbage → SEGV.

This is the **PATBCL context-mismatch** bug session #50 diagnosed.  Slot[1]
was pushed by an INNER pattern's SCIN3 under a different PATBCL.  When
inner-P matched and the recursive SCIN returned, those traps weren't
cleared from PDL.  The outer failure walker reaches them with the outer
PATBCL.

The session #52 SPITBOL-aligned fix correctly handles **single-level**
`*var → FENCE → tail-fail` (tests 109, 113) — that's where SPITBOL's
exact mechanism applies cleanly.  But it does NOT help when there's an
**outer ARBNO loop** (119, 129, beauty) — because ARBNO's iteration
traps and orphaned inner-P traps from prior ARBNO iterations remain on
PDL after the seal fires.  Those orphans are what SALT2 then misreads.

### What session #52 produced

- `csnobol4/docs/F-2-Step3a-session52-flpop-fix.patch` — verified-in-isolation
  patch (54 lines).  `git apply` clean on HEAD `48d99a3`.
- `csnobol4/docs/F-2-Step3a-session52-findings.md` — full investigation
  with SPITBOL-to-CSNOBOL4 mapping table, test results matrix, and
  recommended next-session approach.
- This goal-file state update.

### Recalibration of session #51's reported baseline

Session #51's note claimed fence_suite baseline was 26/4/2.  A fresh
build of HEAD `48d99a3` in session #52 measures **24/2/6** — three
tests session #51 listed as FAIL (109, 113, 130) actually CRASH on
csnobol4.  The session #51 number was likely measured against a build
artifact that included some uncommitted experimental change and then
reported as "baseline."  Session #52's 24/2/6 is the true baseline.

### `.ref` file corrections needed (separate session #53 cleanup task)

`fence_suite/` currently has 2 tests whose `.ref` files don't match
SPITBOL's actual output:

| Test | SPITBOL output | .ref expects |
|------|----------------|--------------|
| 127  | `k=age s="age":42 n=42 b=` | `k=age s= n=42 b=` |
| 130  | `fail` | `sequence of star-cmd-FENCE matched` |

Test 127's "Bug 2" in the README ("conditional-assign not committed
inside FENCE") is partly a wrong-`.ref` artifact — SPITBOL's behavior
matches BREAK + `.` semantics, just not what the test author expected.
Test 130 is also wrong — SPITBOL fails on that input.

Correcting these `.ref` files turns fence_suite into a legitimate
30-target oracle gate.  This is a pure-corpus change (no csnobol4 code).

### Recommended session #53 approach

1. **Correct `.ref` files** for tests 127 and 130 in `corpus/crosscheck/patterns/`.
   This is independent of any csnobol4 code work and unblocks the gate.

2. **Apply `docs/F-2-Step3a-session52-flpop-fix.patch`** as the starting
   point.  Verified correct in isolation — tests 109, 113 + improvements
   to 114, 130.

3. **Read SPITBOL `p_arb` and `p_str`** (sbl.min — find via `grep -n p_arb`)
   to understand how ARBNO/STAR clean up their PDL state on success.
   Then design and implement the fix for the orphaned-trap class.

4. **Done-when:** beauty self-host ≥ 500 lines with no SEGV, fence_suite
   30/30 (or 32/32 if `.ref` corrections preserved test count), fence_function
   10/10 preserved, Smoke=7, Broker=49.

### Honest circularity check (session #52)

Session #52 advanced from "design space" to "first SPITBOL-faithful fix that
makes the canonical 5-line beauty bug class (test 109) pass."  This is
distinct from sessions #49–#51's seal-arithmetic-only attempts.  The
remaining work — orphaned ARBNO traps — is a separately-diagnosable bug
class with a clear next-session path (read SPITBOL p_arb).  The pattern
of "land a real fix, hit the next-deeper bug" continues, but the 32-test
suite + this documented patch make the next step concrete rather than
exploratory.

---

## Session #54 update — targeted slot-zeroing rejected; STREXCCL design crystallized

Session #54 implemented the "targeted slot-zeroing" fix proposed by
session #53's findings (see `docs/F-2-Step3a-session53-findings.md`):
at L_STARP2 / L_DSARP2 success, walk PDL from saved-pre-SCIN snapshot
to current PDLPTR, zeroing slot[1] of any non-FNC trap so SALT2 takes
the SALT3 (clean fail-through) path.

### Results

| Gate | s52 baseline | s54 zeroing |
|------|--------------|-------------|
| fence_function | 10/10 | **10/10** ✅ |
| fence_suite | 27 OK / 3 FAIL / 2 CRASH | **29 OK / 3 FAIL / 0 CRASH** ✅ (best ever) |
| 5-line inner-backtrack repro | matches | **fails** ❌ |
| beauty self-host | ~32 lines clean Parse Error | **~10 lines clean Parse Error** ❌ |

The 2 CRASHes (119, 129 — canonical beauty-class) are FIXED.  But two
4-test classes regress: tests 114/124/(plus 2 others) and the new
5-line inner-backtrack repro.  Beauty regresses from ~32 lines to ~10
lines (no SEGV — clean Parse Error, but earlier).  Per RULES.md
(regression in error class), NOT committed.  Saved as
`csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff`.

### Session #54's genuinely-new contribution

**The 5-line regression guard repro** that demonstrates why session
#53's hypothesis was wrong:

```snobol4
        cmd = (LEN(1) | LEN(2))
        outer = (*cmd 'X')
        s = 'ABX'
        s POS(0) outer RPOS(0)                                :S(YES)F(NO)
YES     OUTPUT = 'inner backtrack worked'                     :(END)
NO      OUTPUT = 'fail'
END
```

SPITBOL outputs `inner backtrack worked`.  csnobol4 + session #52 patch
also outputs `inner backtrack worked` (correct).  csnobol4 + session
#54 zeroing outputs `fail` (regression).  This is now a **permanent
regression guard** — any future fix that breaks this is wrong
regardless of how many fence_suite tests it improves.

### How outer-pattern walker correctly reaches inner backtrack

Traced via instrumented SALT2 / SCIN1-entry / L_UNSC / L_DSAR.  The
mechanism uses CSNOBOL4's existing UNSCCL-restart machinery:

1. Outer SCIN1 with PATBCL=outer matches up through `*cmd 'X'`.
2. `*cmd` is dispatched as DSAR (case 14).  DSARP2 PUSHes outer
   state to cstack, sets UNSCCL=1, calls SCIN1.
3. Inner SCIN1 sees UNSCCL=1 → L_UNSC: `D(PATBCL) = D(YPTR)` —
   sets PATBCL=cmd.  Inner SCIN1 matches LEN(1) and pushes a
   then-or trap with slot[1] = offset-into-cmd-pattern (FNC=0).
4. Inner success → SCIN1 returns 2 → STARP2 → POP cstack
   restoring outer PATBCL.  Outer 'X' fails on 'B'.
5. SALT2 walks back.  Among outer's traps is the one outer's
   compilation pushed signaling "redo *cmd" — dispatches via
   `case 14: goto L_DSAR` (FNC=1, function descriptor).
6. L_DSAR sets UNSCCL=1, calls SCIN1.  Inner SCIN1 → L_UNSC:
   PATBCL=cmd AGAIN.  Walker continues PAST L_UNSC into L_SALT3
   → L_SALT1 → L_SALT2 — but PDLPTR is now at the position WHERE
   the inner alt traps were left.
7. Walker dispatches the inner alt trap (slot[1]=offset-into-cmd-
   pattern) under PATBCL=cmd.  Finds LEN(2).  Match succeeds.

**Step 7 is what zeroing destroys.**  The leaked inner trap that
session #53 thought was "stale and crashing" is actually the
legitimate inner-alternation continuation.  When PATBCL is correctly
restored to inner via the DSAR redo path, the trap dispatches
correctly.

### Sharpened diagnosis of test 119 crash

Test 119 trace shows: after FNCDCL seal fires, walker correctly walks
back through several FNC-flagged traps (PATBCL switches via FNCBX/STARP5
POPs).  Eventually reaches a leaked SCIN3-pushed trap at PDL=ab0 with
slot[1]=0x200 (an offset valid under cmd PATBCL but NOT outer PATBCL).
Walker has fully consumed all DSAR-redo traps by this point — there is
no remaining mechanism to re-route through L_UNSC.  Dispatched under
outer PATBCL → reads pattern at outer-PATBCL+0x200 → wild memory →
SEGV.

The crash class is therefore: **leaked inner traps that get reached
AFTER the walker has consumed all DSAR-redo entries**.  Targeted
zeroing fixes them but unavoidably destroys live-leak inner-backtrack
traps too — distinguishing the two is impossible at zeroing time.

### What the right fix shape looks like — STREXCCL

The architectural answer is the SPITBOL `=ndexc` sentinel approach,
mirrored from `p_nth` (sbl.min:12213).

When STARP6/DSARP success path runs AND inner SCIN pushed entries on
PDL (i.e. PDLPTR > saved_snapshot), install a NEW sentinel trap that,
when dispatched by SALT2, restores PATBCL to inner and continues the
failure walk.  Leaked inner traps remain BELOW the sentinel; walker
reaches sentinel FIRST and switches PATBCL before walking through them.

Concretely (recommended implementation for session #55):

1. Define a new constant `STREXCCL` analogous to `FNCDCL` —
   descriptor with FNC flag and a.i = pointer to L_STREXC handler.
2. Add a new PATBRA case (after case 40 = FNCD).
3. Define `L_STREXC`: `D(PATBCL) = D(YCL); goto L_SALT3;` (or
   L_SALT2 if LENFCL needs preserving — verify against SPITBOL
   p_exc semantics).
4. STARP6/DSARP entry: ADD a new cstack push for inner-PATBCL
   (which equals YPTR right before SCIN call).
5. STARP6/DSARP success path: pop saved-PDL-snapshot AND saved-
   inner-PATBCL.  If `D_A(PDLPTR) > saved_snapshot`, push STREXCCL
   trap with slot[2] = saved-inner-PATBCL.  Otherwise no sentinel
   needed (mirrors SPITBOL p_nth's `beq xt,xs,pnth1` optimization).

The symmetric "restore outer PATBCL when walker descends past the
inner region" happens automatically via existing FNCBX/STARP5 cstack
POPs because outer's existing traps remain BELOW the inner region.

### What session #54 did NOT do

- Did not implement STREXCCL (a 4-step landing: define handler, wire
  dispatch, modify STARP6/DSARP, regen v311.sil for SIL/C consistency).
  Designing it correctly needs careful reading of how SCFLCL/FNCDCL
  handlers preserve LENFCL state — done by session #54 but not
  implemented.
- Did not commit any code changes.

### Files added this session

- `csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff` — the
  rejected fix, preserved as a "do not repeat" artifact.
- `csnobol4/docs/F-2-Step3a-session54-findings.md` — full diagnosis
  + session #55 implementation plan.

### Recommended session #55 plan

1. Apply `csnobol4/docs/F-2-Step3a-session52-flpop-fix.patch`.
2. Re-read `x64/sbl.min:11515-11600` (expression-pattern doc block)
   and `12213-12230` (p_nth) carefully.  Note especially how
   `pnth1` (no-entries-pushed optimization) is structured.
3. Re-read `csnobol4/docs/F-2-Step3a-session54-findings.md`
   "Open question for session #55" before deciding conditional
   vs unconditional sentinel install.
4. Implement STREXCCL per the design above.
5. Run BOTH gates AND the 5-line regression guard:
   - fence_function (must be 10/10)
   - fence_suite (target 30+/32 including 119, 129)
   - 5-line `cmd=(LEN(1)|LEN(2)); outer=(*cmd 'X'); s='ABX'`
     (must produce `inner backtrack worked`)
   - beauty self-host (target ≥ 500 lines)
6. If all gates pass, commit csnobol4 first, then .github.  If any
   regress, do NOT commit; document findings.

### Honest circularity check

Session #54 advanced from "design space" to "explicit refutation of
session #53's hypothesis with a regression guard, AND a concrete
SPITBOL-precedented fix path (STREXCCL = `=ndexc` analog)."  Sessions
#44–#54 = 11 sessions on F-2 Step 3a.  fence_function preserved 10/10
throughout.  Each session has eliminated a wrong-fix candidate.  The
remaining wrong-fix candidates (D1–D5 from earlier design space, plus
zeroing) are now closed.  STREXCCL is the next attempt and fits the
architecture more precisely than any prior candidate.


---

## Session #55 update — Tier F enhancement to fence_suite (16 stress tests, all PASS on baseline)

Session #55 did NOT implement STREXCCL.  Instead, it added 16
depth-recursion stress tests (Tier F, IDs 132–147) to `fence_suite/`
to *empirically demarcate the bug class* before attempting the fix.

### What landed

| Repo | Files |
|------|-------|
| corpus | `crosscheck/patterns/132_*.sno`/`.ref` … `147_*.sno`/`.ref` (32 new files) |
| csnobol4 | `test/fence_suite/Makefile` — added TIER_F block, suite size 32→48 |
| csnobol4 | `test/fence_suite/Makefile` — added missing `-bf` to spitbol target |
| csnobol4 | `test/fence_suite/README.md` — Tier F documentation + empirical results |
| csnobol4 | `docs/F-2-Step3a-session55-tier-f-findings.md` — full report |

### Tier F coverage

- Canonical Gimpel `FENCE(*P | epsilon)` at depths 3 / 30 / 100 (132–134)
- Balanced delimiters `()` `([{<>}])` via mutual recursion (135–137)
- Calculator with parenthesized recursion (138–139)
- The `EVAL("pat . *f()")` double-function trick from beauty Shift/Reduce (140–141)
- ARBNO + FENCE + `*var` combinations (142–143)
- Nested-choice grammars with backtrack across FENCE seals (144)
- Left-fold via ARBNO + FENCE (145)
- FENCE longest-alt with `.` capture (146)
- FENCE through `*var` inside concat (147)

### Empirical result — all 16 Tier F tests PASS on csnobol4 baseline

| Suite | Baseline (HEAD `6d08540`) |
|-------|---------------------------|
| fence_function | 10/10 PASS |
| fence_suite Tier A–E (32) | 24 OK / 2 FAIL / 6 CRASH |
| fence_suite Tier F (16) | **16/16 PASS** |
| fence_suite total (48) | **40 OK / 2 FAIL / 6 CRASH** |
| SPITBOL on full suite | 47 OK / 1 FAIL (test 127 `.ref` known-bad pre-existing) |

### What this empirically rules out (genuinely-new contribution)

The 119/129/130 bug class is **NOT** caused by:
- Depth recursion alone — 134 (depth 100), 136 (parens depth 40) PASS
- Mutual recursion via `*var` — 135–137 PASS
- Calculator-style `*var` nesting — 138–139 PASS
- Double-function `EVAL("pat . *f()")` dispatch — 140–141 PASS
- Generic ARBNO + FENCE — 142 PASS
- Regex with FENCE — 143 PASS
- Nested grammars with FENCE backtrack — 144 PASS
- Left-fold via ARBNO+FENCE — 145 PASS
- Capture into FENCE alts — 146 PASS
- FENCE inside `*var` inside concat (no outer ARBNO) — 147 PASS

### What it confirms

The bug class requires the **conjunction** of:
1. `*var` indirection of a FENCE-containing pattern, AND
2. An outer ARBNO/iteration that pushes its own redo traps, AND
3. A tail-anchor failure that walks past the FENCE seal AND past
   the outer ARBNO's redo trap into leaked then-or alternation
   traps from the inner pattern's matching.

This is precisely the mechanism session #54's STREXCCL design
addresses.  Tier F validates STREXCCL as the *narrow correct fix*
rather than a broader runtime restructure.

### Regression-prevention floor for future sessions

Tier F + the 5-line guard5 (`cmd=(LEN(1)|LEN(2)); outer=(*cmd 'X');
s='ABX'`) together form the **regression-prevention floor**.  Any
proposed fix that breaks any of the 16+1 cases is wrong regardless
of how many other tests it improves.

This rules out (for future sessions):
- Naïve PDLPTR rewind (session #53) — would discard FNCDCLs that
  142, 143 rely on
- Targeted slot-zeroing (session #54) — kills inner-backtrack which
  guard5 specifically tests
- Saving-more-state in the seal (session #41 / D3 layouts A–E) —
  doesn't address PATBCL routing, just PDLPTR rewind

STREXCCL doesn't share these failure modes.

### What session #55 did NOT do

- Did not implement STREXCCL (deferred to session #56)
- Did not run gates with the session #52 patch + STREXCCL combination
- Did not advance beauty self-host (still 35 lines)
- Did not commit any runtime source-code changes (csnobol4 source tree
  bit-identical to HEAD `6d08540`)

### Recommended session #56 plan

1. Run baseline suite (sanity check Tier F still 16/16 on current HEAD).
2. Apply `docs/F-2-Step3a-session52-flpop-fix.patch`.
3. Implement STREXCCL via SIL edits to `v311.sil`:
   - Add `XSTREX EQU 41`
   - Add `STREXC` to `PATBRA SELBRA` dispatch list
   - Add `STREXCCL DESCR STREXFN,FNC,2` data cell
   - Add `STREXFN DESCR XSTREX,0,2` function descriptor
   - Add `STREXC` label body (mirror `UNSC`/`SALT3`)
   - Modify STARP6/DSARP2 to push `PDLPTR` snapshot on cstack
   - Modify STARP2 to conditionally push STREXCCL trap on success
   - Modify STARP5 to pop-and-discard snapshot on failure
4. Regen via `make snobol4.c isnobol4.c`, build via `make -f Makefile2 xsnobol4`.
5. Gate stack (in order, stop at first regression):
   - guard5 must produce `inner backtrack worked`
   - **Tier F all 16 must remain PASS** ← new floor from session #55
   - fence_function 10/10
   - fence_suite total ≥46/48 (target 47/48 or 48/48 minus test 127)
   - Beauty self-host ≥500 lines
6. Smoke gates skipped if SCRIP not cloned.
7. Commit csnobol4 first, then `.github` per RULES.md.

### Honest circularity check

Sessions #44–#54 attempted runtime fixes; sessions #50, #51, #54
contributed diagnosis docs without runtime changes.  Session #55
contributes a **48-test gate** that disqualifies wrong-fix candidates
empirically.  This is a different kind of progress than the prior
sessions and not subject to the "land a fix, hit next-deeper bug"
spiral — Tier F is a tool, not a fix attempt.  The beauty counter
remains at 35 lines because no runtime work was done; that is correct
for a session focused on test infrastructure.

corpus working tree status: 32 new untracked files (132–147 .sno/.ref).
csnobol4 working tree status: 2 modified (Makefile, README.md), 1 new
docs file.  No runtime source files modified.  Ready to commit as
"test-only" advancement of the goal.
## Session #56 update — STREXCCL implemented; insufficient alone

Session #56 implemented the STREXCCL sentinel proposed by sessions #54/#55
(SPITBOL `=ndexc` analog).  Implementation is correct in shape:
fence_function preserved 10/10, Tier F preserved 16/16, guard5
preserved.  But fence_suite did **not** improve over s52 alone — same
**43 OK / 3 FAIL / 2 CRASH (of 48)**.  119/129 still CRASH; 114/124 still FAIL.

### What landed (uncommitted, saved as patch artifact)

C-only implementation of STREXCCL in `isnobol4.c`, 5 edits:

1. Static descriptors `STREXCCL_d`/`STREXFN_d` lazily initialized via
   `STREXC_INIT()` macro.  No `res.h`/`data_init.h`/`equ.h` touches —
   `XSTREX = 41` literal, file-local statics.  SIL parallel edit
   deferred to Step 3b.
2. New dispatch `case 41: goto L_STREXC;` in PATBRA switch.
3. New `L_STREXC:` handler — `D(PATBCL) = D(YCL); goto L_SALT3;`.
4. STARP6 + DSARP2: `PUSH(PDLPTR); PUSH(YPTR);` after the existing 5
   saves (entry-PDLPTR snapshot + inner-PATBCL = YPTR).
5. STARP2 success: pop the two extras + existing 5; conditionally
   install STREXCCL with `slot[2]=inner_PATBCL` when
   `D_A(PDLPTR) > D_A(STREX_entrypdl)` (mirrors p_nth's `pnth1`
   optimization).  STARP5 fail: pop and discard.

Saved as `docs/F-2-Step3a-session56-strexccl-attempt.diff` (90 lines
combined with s52 — self-contained against HEAD `1b2e28a`).  Verified
to reproduce gates from a clean checkout.

### Trace evidence — STREXCCL fires but PATBCL is already inner

Added env-gated `STREXC_TRACE=1` instrumentation at install + FIRE
sites.  Test 114 produces a single trace pair:
```
STREXC: install at PDLPTR=...9b0 entry=...950 innerpat=7f667bc0b9d0
STREXC: FIRE — restoring PATBCL=7f667bc0b9d0 (was 7f667bc0b9d0)
```

PATBCL was **already** `= cmd` (the inner pattern) at the moment the
walker reached the sentinel.  Some upstream handler set PATBCL=inner
during outer's failure walk before the walker hit STREXCCL.  This
**refutes session #54's hypothesis** — the bug isn't "leaked traps
dispatched under wrong PATBCL" because by the time the walker reaches
them, PATBCL has already been changed to inner by some other
mechanism.

### Recommended session #57 plan

1. Apply `docs/F-2-Step3a-session56-strexccl-attempt.diff` (self-contained,
   includes both s52 flpop fix and STREXCCL together).
2. Add a PATBCL-write logger — env-gated `_check_patbcl(site_id)`
   helper at every `D(PATBCL) = ...` and `D_A(PATBCL) = ...` site
   in `isnobol4.c`.  Find sites with:
   ```bash
   grep -nE 'D_A\(PATBCL\)\s*=|D\(PATBCL\)\s*=' isnobol4.c
   ```
3. Run test 114 with the logger.  Identify which write sets PATBCL=cmd
   at the wrong moment.  That site is the bug.
4. Decide between (a) fixing the upstream write, or (b) augmenting
   STREXCCL with a paired BOTTOM-of-region sentinel pushed BEFORE
   the inner SCIN call (between existing 5 PUSHes and the STREXCCL
   pair) that switches PATBCL=outer when walker descends past inner.
5. Test gate stack (in order, stop at first regression):
   - guard5 must produce `inner backtrack worked`
   - Tier F all 16 must remain PASS
   - fence_function 10/10
   - fence_suite total ≥45/48 (target 47/48 minus test 127 known-bad-ref)
   - Beauty self-host ≥500 lines
6. Commit only if all gates pass; save findings + diff if not.

### What session #56 did NOT do

- Did not advance beauty self-host (still 35 lines from baseline).
- Did not implement the BOTTOM-of-region paired sentinel.
- Did not port STREXCCL to `v311.sil`/`snobol4.c` — Step 3b.

### Files this session

- `csnobol4/docs/F-2-Step3a-session56-strexccl-attempt.diff` — clean
  combined patch (s52 + STREXCCL), 90 lines, self-contained.  Verified
  to reproduce all gates.
- `csnobol4/docs/F-2-Step3a-session56-findings.md` — full investigation
  with implementation excerpts and session #57 plan.
- `.github/PLAN.md` and this goal file updated.
- No runtime source changes committed.  Working tree clean.

### Honest circularity check

Sessions #44–#56 = 13 sessions on F-2 Step 3a.  fence_function preserved
10/10 throughout.  Tier F preserved 16/16 since session #55.

Session #56's genuine new contribution: **first-time implementation of
STREXCCL** + **empirical refutation of session #54's hypothesis** via
trace evidence.  STREXCCL is a correct-shape change (preserves all
floors, doesn't break inner-backtrack guard5, doesn't kill any of
Tier F's 16 stress patterns) but is insufficient because the
PATBCL=inner state arrives at the sentinel via some upstream write
that hasn't yet been identified.

The PATBCL-write logger is the next concrete diagnostic — a 1-hour
task that should pinpoint the specific bug site in `isnobol4.c`.


---

## Session #57 update — multi-iteration ARBNO leak class identified; STREXCCL design insufficient

Session #57 followed the session #56 plan: applied
`docs/F-2-Step3a-session56-strexccl-attempt.diff`, then instrumented
**all** PATBCL-touching sites in `isnobol4.c` (3 `D(PATBCL) = ...`
writes + 7 `POP(PATBCL)` cstack restores + every SALT2 entry).

The trace on test 119 **refutes both** session #54's hypothesis
("leaked traps under wrong PATBCL because no DSAR-redo route") and
session #56's hypothesis ("upstream write sets PATBCL=inner before
sentinel fires").

### Genuinely-new diagnosis: multi-iteration ARBNO leak

There are exactly **3 sites in the file** that write `D(PATBCL)` —
SCIN1A entry, UNSC (DSAR-redo path), STREXC (the sentinel itself) —
and 7 `POP(PATBCL)` cstack restore sites.  Every PATBCL change in the
test 119 run is accounted for by these 10 sites.  **There is no
"upstream write" that sets PATBCL=inner mysteriously.**

The actual mechanism: in `s POS(0) *outer RPOS(0)` where `outer =
ARBNO(*cmd)`, each successful ARBNO iteration of `*cmd` leaves an
inner-pattern leak region on PDL with its own STREXCCL on top.
**STREXCCL only protects the most recent iteration's leak region.**
Earlier iterations' leaks remain BELOW that STREXCCL on PDL.

When outer's tail (`RPOS(0)`) fails, walker descends:
1. Hits STREXCCL of iter#3 → PATBCL=cmd. Walks iter#3 leaks safely.
2. Iter#3 fails → STARP5 cstack POP → PATBCL=outer.
3. Walker continues descending — now into iter#2's leak region,
   which has NO STREXCCL above it any more (iter#3's STREXCCL is
   already consumed/below current PDLPTR).
4. Reads slot `{a=0x200, f=0, v=96}` from iter#2's leak under
   `PATBCL=outer`.  L_SCIN3 fallthrough does
   `D(outer + 0x200)` → garbage descriptor → ZCL=NULL → SEGV at
   `isnobol4.c:11521` `D(PTBRCL) = D(D_A(ZCL))`.

The crash is now **decisively understood**: it's not "wrong PATBCL on
the dispatched trap" or "missing PATBCL restore"; it's **earlier
ARBNO iterations' leaks unprotected because their STREXCCL has been
consumed**.

### What the right fix looks like (candidates for session #58)

Three candidates documented in
`csnobol4/docs/F-2-Step3a-session57-findings.md`:

- **(c) Persistent STREXCCL across iterations** — make the sentinel
  not consume on first walker pass; reinstall it after each
  iteration.  Non-trivial: when does it actually retire?
- **(b refined) Paired BOTTOM-of-region sentinel** — push two
  sentinels per STARP6 (top + bottom of leak region).  Bottom one
  switches PATBCL back to outer when walker descends past it.  Issue:
  SCFLCL's `BRANCH(FAIL)` would also fire prematurely.  Need to
  re-read SPITBOL `p_str / =ndexc` to see how SPITBOL handles this.
- **(d) Truncate PDL at STARP2 + deferred-alt array** — drop
  inner-leaks at success time but record them in a side-table on
  the inner pattern descriptor; DSAR-redo handler re-pushes them.
  Risk: changes pattern descriptor shape.

### Files added this session (untracked, to be committed)

- `csnobol4/docs/F-2-Step3a-session57-findings.md` — full diagnosis
  with the decisive 12-event trace before crash, geometric
  interpretation of multi-iteration leak stratification, and three
  fix candidates.
- `csnobol4/docs/F-2-Step3a-session57-diagnostic.diff` — 145-line
  reusable instrumentation patch (env-gated `PATBCL_LOG=1`) that
  adds the PATBCL-write/POP loggers + SALT2-entry logger.  Future
  sessions can apply with `git apply` to reproduce traces.

### What session #57 did NOT do

- Did NOT modify any production code beyond the s56 patch (reverted).
- Did NOT advance beauty self-host (still 35 lines baseline).
- Did NOT implement (b), (c), or (d).  All three are credible but
  none has been verified.
- Did NOT read SPITBOL `p_str / flpop / =ndexc` interactions in the
  detail needed to choose between (b), (c), (d).

### Recommended session #58 plan

1. Apply `docs/F-2-Step3a-session56-strexccl-attempt.diff`.
2. Optionally apply `docs/F-2-Step3a-session57-diagnostic.diff` for
   trace re-runs.
3. **Read SPITBOL** `sbl.min` around `p_str` (≈12100s), `=ndexc`
   (≈12213), `flpop` (≈3144).  Specifically: does SPITBOL leave
   alts on `xs` (its pattern history stack) on `p_str` success?
   How does it handle stranded entries from prior iterations of
   an outer ARBNO of `*var`?
4. Implement (b), (c), or (d) based on what SPITBOL does.
5. Test gate stack: guard5, Tier F 16/16, fence_function 10/10,
   fence_suite ≥45/48, beauty ≥500 lines.
6. Commit only if all gates pass.

### Honest circularity check

Sessions #44–#57 = 14 sessions on F-2 Step 3a.  fence_function
preserved 10/10 throughout.  Tier F preserved 16/16 since session #55.
Beauty stuck at 33–35 lines.

Session #57's genuinely-new contributions:

1. **Direct trace evidence** (not gdb post-mortem inference) of every
   PATBCL transition AND every PDL slot the walker reads.  Previous
   sessions reasoned about the bug; #57 watched it.
2. **Identification of the multi-iteration ARBNO leak class.**
   Sessions #50/#54/#56 framed the bug as a single region.  It's a
   stack of regions, all unprotected except the top.
3. **Refutation of session #56's "upstream write" hypothesis.** No
   upstream write exists.  All 3 PATBCL-write sites behave correctly.
   The bug is not about *who writes PATBCL*; it's about *which slots
   the walker reads under it*.
4. **Reusable diagnostic patch** that future sessions can apply
   with `git apply` instead of re-deriving instrumentation.

The pattern of "land a diagnostic, hit deeper structural issue"
continues, but session #57 has narrowed the structural issue to a
specific named bug class with three concrete fix shapes to choose
between.  Session #58's job is to read SPITBOL more carefully and
implement one.

---

## Session #58 update — paired top+bottom STREXCCL eliminates all fence_suite CRASHes; semantic FAIL on 119/129 remains

Session #58 read SPITBOL `p_exa`/`p_nth`/`p_exb`/`p_exc` (sbl.min:11920-12000,
12213) AND `p_aba`/`p_abb`/`p_abc`/`p_abd` (11600-11665) carefully — first
session to actually do the SPITBOL reading session #57 ordered.

### Architectural finding

CSNOBOL4 has all the parts of SPITBOL's `pmhbs` mechanism but they are
wired differently.  SPITBOL's failure walker doesn't bound-check; instead
every level installs a **bottom sentinel** at level entry whose handler
restores `pmhbs` to outer when reached.  The top sentinel `=ndexc`
(CSNOBOL4 STREXCCL — session #56) AND the bottom sentinel `=ndexb`
(CSNOBOL4: **MISSING**) wrap each leak region symmetrically.  CSNOBOL4
has SCFLCL at the bottom but its handler is FAIL (exits SCAN entirely),
which is wrong for the multi-iteration case where the walker must
*continue* past iter#N's region into iter#N-1's.

### Implementation

Three edits to `isnobol4.c` (~40 net lines, combined with s52 + s56 = 195
total):

1. **L_STARP2 success path:** rewrite SCFLCL trap at `STREX_entrypdl + DESCR`
   to STREXCCL with slot[2] = OUTER PATBCL.  Walker reaching the bottom of
   this iteration's region now restores PATBCL=outer and continues failp
   into earlier regions — symmetric with the top STREXCCL (slot[2] = inner).
   Same handler `L_STREXC` fires both.
2. **L_DSARP2:** push SCFLCL frame symmetrically with STARP6, so DSARP2
   success at L_STARP2 has a known target for the bottom-rewrite.
3. (Top STREXCCL push from s56 preserved unchanged.)

SCFLCL is preserved on the FAIL path (STARP5) — when inner SCIN failed,
walker walked through and consumed SCFLCL → FAIL → exited SCIN.  No
bottom-rewrite needed.

### Gates (vs. baseline / s52 / s56)

| | Baseline | s52 | s56 | **s58** |
|---|---|---|---|---|
| fence_function | 10/10 | 10/10 | 10/10 | **10/10** |
| Tier F | 16/16 | 16/16 | 16/16 | **16/16** |
| guard5 | OK | OK | OK | **OK** |
| fence_suite total | 40/2/6 | 43/3/2 | 43/3/2 | **44/4/0** |
| **CRASHes** | 6 | 2 | 2 | **0** |
| beauty self-host lines | 35 | 35 | 35 | **42** |

### What's resolved

- **All 6 fence_suite CRASHes eliminated.**  Tests 109, 113, 130 — CRASH
  at baseline and CRASH after s56 alone — are now OK.  This is direct
  evidence the paired-sentinel mechanism handles cases the top-only
  sentinel couldn't.  Tier F (16 depth-stress tests) preserved 16/16.
- **Bug class shifted from memory corruption to wrong-answer semantics.**
  Tests 119 and 129 went from CRASH to FAIL (`unexpected match` instead
  of `triple-indirect FENCE sealed`).  This is much easier to debug.
- **Beauty self-host advanced 35 → 42 lines** before Error 17 (controlled
  program error, not memory corruption).  First non-zero gain since
  session #45.

### What's NOT resolved

- **Tests 119 / 129 give wrong semantic answer.**  SPITBOL says no match
  (FENCE seals); s58 says match.  Hypothesis: the bottom-STREXCCL routing
  somehow lets the walker re-enter the inner cmd region under inner
  PATBCL via an EARLIER iteration's top STREXCCL — and that re-entry
  finds an FNCDCL (FENCE seal) but treats it as a legitimate retry rather
  than as a sealed wall.
- **Beauty: still 42 lines, far short of ≥500.**

### Why s58 is NOT committed

Per RULES.md "regression in error class is unsafe to commit": tests 119
and 129 went from CRASH to FAIL.  This IS a strict improvement (memory
corruption → wrong-answer is universally accepted as progress) and no
prior-OK test regressed.  But the F-2 Step 3a `Done when` requires beauty
self-host ≥500 lines, and 42 lines is far short.  Saved as
`docs/F-2-Step3a-session58-paired-strexc-attempt.diff` (195 lines,
self-contained against HEAD `8ebab64`, verified to reproduce all gates).

### Recommended session #59 plan

1. Apply `docs/F-2-Step3a-session58-paired-strexc-attempt.diff`.
2. Optionally apply `docs/F-2-Step3a-session57-diagnostic.diff` for
   PATBCL_LOG=1 / STREXC_TRACE=1 traces.
3. **Trace test 119** with diagnostic.  Identify which path leads to the
   unexpected match.  Look for:
   - Does ARBNO iterate more than once when SPITBOL would do zero or one?
   - Does an FNCDCL (FENCE seal) get bypassed via STREXCCL routing?
   - Does the bottom-STREXCCL fire during a legitimate inner-pattern-fail
     walk (when it should leave the walker in inner-mode all the way down
     to SCFLCL → FAIL exit)?
4. **Cross-check on test 130** (FAIL→OK in s58) — understand WHY it now
   passes; that mechanism may inform 119/129's still-failing path.
5. **Possible refinement**: bottom-STREXCCL should only fire when walker
   reached it via "failed all inner alts above" path, not when walker was
   supposed to exit to STARP5 via SCFLCL→FAIL.  May need a flag distinguishing
   fail-mid-iteration from fail-after-iteration-success.
6. Test gate stack: guard5, Tier F 16/16, fence_function 10/10, fence_suite
   ≥45/48, **119/129 must give correct semantic answer**, beauty ≥ 500 lines.
7. Commit only if all gates pass AND 119/129 give correct semantic.

### Files this session

- `csnobol4/docs/F-2-Step3a-session58-findings.md`
- `csnobol4/docs/F-2-Step3a-session58-paired-strexc-attempt.diff` (195
  lines, self-contained vs. HEAD `8ebab64`)
- This goal-file update + PLAN.md state-cell update.
- No production source changes committed.  Working tree clean except for
  the docs files.

### Honest circularity check

Sessions #44–#58 = 15 sessions on F-2 Step 3a.  fence_function preserved
10/10 throughout.  Tier F preserved 16/16 since session #55.

Session #58's genuinely-new contributions:

1. **First architectural mapping** of CSNOBOL4 STAR/DSAR ↔ SPITBOL
   p_exa/p_nth/p_exb/p_exc with concrete identification of which
   structural piece is missing in CSNOBOL4 (the bottom sentinel handler
   that restores walker base to outer instead of FAIL-exiting the SCAN).
2. **First implementation that eliminates ALL fence_suite CRASHes** (6 → 0).
   Sessions #51–#57 reduced crashes 6 → 2 but never to zero.
3. **Tests 109, 113, 130 promoted to OK** that were CRASH at baseline AND
   CRASH after s56 alone.  Direct evidence the paired-sentinel mechanism
   handles cases the top-only sentinel couldn't.
4. **+7 lines of beauty self-host progress** (35 → 42).  Modest but the
   first non-zero gain since session #45.

The "land an architectural step forward, hit deeper bug" pattern continues,
but the next bug (119/129 wrong-answer) is no longer in the memory-
corruption class — it's debugger-tractable with normal traces.

---

## Session #59 update — trace evidence + PATBCL-offset architectural diagnosis

Session #59 continued from s58's paired-sentinel design.  Added SALT2-
entry trace and ran test 119: **only 7 SALT2 events** before "unexpected
match" output (down from session #57's 69 events — s58's paired sentinels
have already eliminated most walker wandering).

### Decisive trace observation

Event [2] at PDLPTR=9c0 PATBCL=bb60 (outer-most): slot[1]={a=0xb0,f=0,
v=240}.  Non-FNC, offset 0xb0.  L_SALT2 falls through to L_SCIN3.
L_SCIN3 increments PATICL to 0xc0 and reads ZCL = D(bb60 + 0xc0).
Outer-most pattern is `s POS(0) *outer RPOS(0)`; offset 0xc0 = 12*DESCR
lands past the *outer STARPT block (which is 11*DESCR per v311.sil:12219).
**The slot was pushed during inner *cmd matching (under PATBCL=cmd)
where 0xb0 was a valid offset within cmd's compiled pattern.  Read under
PATBCL=outer-most, 0xb0 indexes into a different node — but one that
happens to be a valid pattern dispatch (a STAR/DSAR-shaped descriptor),
so it doesn't crash; it just spuriously redoes the match.**

This is a **CSNOBOL4-vs-SPITBOL architectural difference**:

- **SPITBOL pcode:** alt links are direct memory pointers.  Each pcode
  node stands alone.  Dispatching a leaked alt does NOT depend on which
  "container" pattern is current.
- **CSNOBOL4 PATBRA:** alt links are byte offsets within the current
  pattern (PATBCL).  Same offset, different PATBCL = different node.
  Leaked entries become semantically wrong without crashing.

### Two STREXBCL bottom-handler variants tested

1. **FAIL-on-fire** (terminate inner SCAN call when bottom-sentinel
   reached):
   - Result: fence_suite **43 OK / 5 FAIL / 0 CRASH** — REGRESSED by 1
     vs. s58's 44/4/0.
   - Interpretation: terminating via FAIL is too aggressive; some
     legitimate alt-backtrack cases need the walker to continue past
     the bottom-sentinel to dispatch surviving outer alts.

2. **PATBCL=outer + continue walker** (== s58's STREXCCL_bottom behavior,
   just renamed to STREXBCL):
   - Result: identical to s58 (44/4/0, test 119 wrong-answer).
   - Interpretation: the *handler* isn't the discriminator; the bug is
     which entries the walker reaches AFTER the sentinel.

### Two structural fix candidates for session #60

#### (a) PDLHED-bound SALT2 walker — RECOMMENDED

Maintain PDLHED as a per-iteration base (analog of SPITBOL pmhbs).  At
STARP6/DSARP2 entry, save PDLHED to cstack and `MOVD PDLHED, PDLPTR`
(matching what EXPVAL/BAL/ATP already do — see v311.sil:2711, 3941, 4259).
Modify SALT2 to bound: when `PDLPTR <= PDLHED`, do NOT loop; invoke
the level's "I'm at base" handler (mirrors SPITBOL `p_exb`/`p_abb`).

This already exists in CSNOBOL4 for BAL: `PCOMP PDLPTR, PDLHED, TSALF,
TSALF, INTR13` at v311.sil:3975.  STAR/DSAR don't have it.

Implementation:
- L_STARP6: PUSH(PDLHED) before existing PUSHes; `D(PDLHED) = D(PDLPTR)`
  after SCFLCL frame setup.
- L_DSARP2: same.
- L_STARP2 success / L_STARP5 fail: POP(PDLHED) at the start.
- L_SALT2: `if (D_A(PDLPTR) <= D_A(PDLHED)) goto L_AT_LEVEL_BASE;`
- L_AT_LEVEL_BASE: invoke saved-base sentinel; restore outer PDLHED
  and continue popping.

Pros: Architecturally clean.  Reuses existing PDLHED machinery.
Mirrors SPITBOL pmhbs faithfully.

Cons: Touches the failure-walker hot loop.  Risk of regression in
non-STAR cases.  Needs careful PDLHED save/restore plumbing.

#### (b) Truncate-on-success with deferred-alts array

At STARP2 success, walk inner region, copy non-FNC alts to side array,
truncate PDLPTR.  At DSAR-redo, push deferred alts back.

Pros: No SALT2 hot-loop change.

Cons: Changes pattern descriptor shape (breaks pattern-equality).
Heavier per-success cost.

### What session #59 did NOT do

- Did NOT modify production code (test patches reverted).
- Did NOT advance beauty self-host.
- Did NOT implement (a) or (b).

### What session #59 produced

- `csnobol4/docs/F-2-Step3a-session59-findings.md` — full trace,
  architectural diagnosis, fix candidates.
- csnobol4 commit `1b59147` (findings.md only).
- This goal-file update.

### Honest circularity check

Sessions #44–#59 = 16 sessions on F-2 Step 3a.  Each has narrowed the
bug.  Session #59's contribution: **identified that the remaining issue
is architectural (PATBCL-relative offsets), not just sentinel-routing.**
The fix shape (PDLHED-bound walker) is well-defined and has BAL as an
existing precedent in CSNOBOL4.  Session #60 has a concrete patch path.


---

## Session #62 update — full PDL dump diagnostic; bug locus narrowed (no code change)

Session #62 followed the session #60-final-handoff plan exactly: instrumented
`isnobol4.c` with an env-gated PDL-dump diagnostic at three checkpoints
(FNCA-success, STARP2-after-sentinels, every SALT2 entry).  Reverted before
commit per RULES.md.  Full findings in
`csnobol4/docs/F-2-Step3a-session62-findings.md`.

### Genuine new contribution

**Bug-class boundary sharpened to 5-line repro:**

```snobol
        cmd = FENCE('a' | 'ab')
        outer = ARBNO(*cmd)
        s = 'ab'
        s POS(0) *outer RPOS(0)                               :S(BAD)F(GOOD)
BAD     OUTPUT = 'unexpected match'                            :(END)
GOOD    OUTPUT = 'sealed'
END
```

Empirical bisection — bug requires the **conjunction of ALL FOUR**:

1. `*var` outer indirection (DSAR dispatch path)
2. ARBNO inside that var
3. `*var` inside the ARBNO body (second DSAR dispatch)
4. FENCE dispatched from that inner var

Drop any one of (1)-(4) → bug disappears.  This is sharper than session #55's
Tier F characterization.

### What the dump revealed

- The seal at FNCA-success is correctly placed (`aa20`, top of PDL after
  rewind+push).  Seal-base mechanics work.
- Inner FENCE's `'a'|'ab'` alts ARE properly truncated by FNCA's
  POP+rewind.  Those leaks aren't the issue.
- STREXCCL paired sentinels (top + bottom) correctly bracket the leak
  region.  PATBCL routing through them works.
- **The leaked alt-cont at `a960` (slot[1]=0x90) was previously assumed
  to be inner-FENCE leak.  It is NOT.**  It's an outer-DSARP2-era alt
  (offset into outer ARBNO body, not into FENCE-inner P).  Its
  consumption is part of legitimate ARBNO redo machinery — clearing it
  would break ARBNO backtrack.

### What the trace silence tells us

**No SALT2 events appear between DUMP #3 (STARP2-after-sentinels) and the
"unexpected match" output.**  This means the wrong-match path does NOT
go through the failure walker.  The match SUCCEEDS DIRECTLY via
SCOK/SCIN2/RTN2 propagation upward.

This is decisive evidence that the bug is NOT in:
- FNCA arithmetic
- STARP2 sentinel placement
- Seal propagation through the failure walker
- PATBCL routing in STREXCCL

The bug is in the SUCCESS path AFTER STARP2 of `*cmd` returns — somewhere
between DUMP #3 and the final "unexpected match" output.  Possibilities:

- ARBNO redo machinery dispatches `*cmd` again under a wrong PATBCL,
  finding 'ab' as a longer match.
- `*outer`'s STARP2 doesn't properly handle the case where its inner
  matched fewer characters than required by RPOS(0).
- The top-level pattern's MAXLEN/cursor bookkeeping is off by some
  amount specific to this 4-level nesting.

### Recommended session #63 plan

The diagnostic ladder needs to extend INTO the success path.  Candidates:

1. **Instrument L_SCOK / L_SCIN2 entry/exit.**  Log PATBCL, PATICL, cursor
   each time L_SCOK fires.  Trace the chain of RTN2 propagations after
   FNCA-success.
2. **Instrument SCNR's success-completion path** (L_SCNR3, L_SCNR4-6).
3. **Instrument every PATBRA case dispatch in SALT2.**  Log the case number
   when walker dispatches an FNC-flagged trap.
4. **Use the simpler `s='ab'` repro** for diagnostic runs.
5. **Find where 'ab' actually matches.**  The wrong match has to come from
   `'ab'` being committed somewhere.  Add a one-shot trap at every place
   the matcher commits a 2-char-or-longer match; log cursor and pattern.
6. Once located, fix candidates depend on the discovery — likely either
   ARBNO redo dispatch, *cmd's STARP2 success-handoff to outer, or
   *outer's STARP2/STARP5 pop-and-continue.

### What session #62 did NOT do

- Did NOT modify production code (diagnostic reverted).
- Did NOT advance beauty self-host.
- Did NOT improve fence_suite (still 44/4/0).
- Did NOT identify the exact wrong-match path (only narrowed the bug
  region from "anywhere in FENCE/STAR/STREXCCL machinery" to "in the
  SCOK success-propagation path between *cmd's STARP2 and SCAN exit").

### Files this session

- `csnobol4/docs/F-2-Step3a-session62-findings.md` — full findings,
  trace excerpts, bug-class bisection, session #63 plan.
- This goal-file update + PLAN.md state-cell.
- No production source changes.  csnobol4 working tree clean at
  HEAD `e723517`.

### Honest checkpoint

Sessions #44–#62 = 18 sessions on F-2 Step 3a.  fence_function preserved
10/10.  Tier F preserved 16/16 since #55.  fence_suite stuck at 44/4/0
since #58 (5 sessions).  Beauty stuck at 42 lines since #58 (5 sessions).

Session #62 is exclusively diagnostic — no fix attempted, no code change
committed, no gate movement.  Per RULES.md investigation-rung guidance,
this is acceptable.  But the strategic question from session #60's final
handoff stands: **is closing this bug worth more sessions, or should the
goal pivot?**  Possible pivots:
- Remove FENCE(P) from beauty.sno entirely (Plan B route)
- Use SPITBOL exclusively for beauty self-host
- Accept 44/4/0 and document the remaining 4 FAILs as known limitation

The bug now has the smallest known repro (5 lines, `s='ab'`) and a clear
narrowed locus (SCOK success path).  Session #63 can attempt a focused
fix.  But Lon's input on whether to continue is welcome.

---

## Session #63 update — session #61 in-place SCIN3 fix attempted; refuted by gates; bug narrowed to TXSP corruption

Session #63 implemented session #61's "CRITICAL NEW FINDING" in-place
SCIN3-FENCEPT trap overwrite at FNCA's success path: replace the
3-DESCR push of FNCDCL above the SCFLCL position with an in-place
overwrite of the SCIN3-FENCEPT trap slots at P0 = entry-PDLPTR.

### Gates after the s63 fix attempt

| Gate | Baseline | s63 attempt |
|------|----------|-------------|
| fence_function | 10/10 | **10/10** ✅ |
| fence_suite | 44/4/0 | **44/4/0** ❌ no change |
| guard5 | OK | OK |
| 5-line bug repro | wrong-match | **wrong-match** ❌ no change |

**Reverted before commit per RULES.md.** Same 4 tests (119, 124, 127,
129) still FAIL with `unexpected match`. The SCIN3-FENCEPT trap is NOT
the dispatch point that produces the wrong match.

### Genuinely-new contribution: TXSP corruption identified

Added env-gated diagnostics (saved as
`docs/F-2-Step3a-session63-diag.txt`) at L_RPSII and L_SALT2 entries.

Run with `RPOS_TRACE=1 WALK_TRACE=1` on the 5-line repro shows **6 SALT2
events** between RPSII failure and "unexpected match" output — refines
session #62's incomplete "no SALT2 events" claim.

**Decisive finding:** between SALT2 #5 (STREXCCL sentinel fires,
restoring PATBCL=cmd) and SALT2 #6 (next descent step), **TXSP changes
from 0 to 140702518392224 — which equals cmd's PATBCL heap-pointer
value (0x7FF7DBA0B5A0)**. No code in the visible STREXCCL/SALT3/SALT1/
SALT2 path writes TXSP. So either a SCIN3 fall-through fires off-trace,
or a primitive dispatched between #5 and #6 sets TXSP from a
heap-pointer-shaped register. After this corruption, some pattern
primitive succeeds spuriously and SCOK propagates upward.

The bug is now narrowed to **TXSP corruption during walker descent**,
NOT pattern-dispatch corruption.

### Recommended session #64 plan

1. Apply `docs/F-2-Step3a-session63-diag.txt` (RPSII + SALT2 trace).
2. Add additional traces at:
   - Every `S_L(TXSP) = ...` write site in `isnobol4.c`.
   - Every L_PATBRA case dispatch (log case number + PATBCL/PATICL/YCL/TXSP).
   - L_SCIN3 entry (log PATBCL, PATICL, TXSP).
3. Run with `TXSP_TRACE=1 PATBRA_TRACE=1 SCIN3_TRACE=1` and identify
   the exact instruction that sets TXSP to PATBCL's value.
4. Fix candidates depend on what's found.

### Files this session

- `csnobol4/docs/F-2-Step3a-session63-findings.md` — full findings.
- `csnobol4/docs/F-2-Step3a-session63-diag.txt` — diagnostic patch.
- This goal-file update.
- No code changes committed. Working tree clean.

### Honest checkpoint

Sessions #44–#63 = 19 sessions on F-2 Step 3a. fence_function preserved
10/10. Tier F preserved 16/16 since #55. fence_suite stuck at 44/4/0
since #58 (6 sessions). Beauty stuck at 42 lines since #58.

Session #63 ruled out the session #61 hypothesis with gate evidence
(not just argument), and produced the first concrete TXSP-corruption
diagnosis with reusable diagnostic infrastructure. The bug now has
a precise handle: "between SALT2 #5 and SALT2 #6, TXSP gets PATBCL's
value." Session #64 should be able to instrument every TXSP write
site and pinpoint the line.

---

## Session #64 update — TXSP write-site identified and fixed (gate-neutral); FNCDCL-at-P2 refuted; architectural mechanism named

Session #64 followed session #63's plan exactly: instrumented every
`S_L(TXSP) = ...` site in `isnobol4.c` and pinpointed the corruption
to a single line.

### Genuine new contribution: the bug line

**`isnobol4.c:11498`** — `S_L(TXSP) = D_A(YCL)` in `L_SALT2` fires for
**all** non-zero PATICL entries, including FNC-flagged traps.

For SCIN3-pushed (non-FNC) traps, `slot[2]` is a saved cursor (TXSP) —
restoring it makes sense.  For FNC traps (STREXCCL, FNCDCL, NMECL,
DNMECL, etc.), `slot[2]` is **handler-specific data** — for STREXCCL
specifically, it's a heap-pointer-shaped PATBCL value.  Writing that
into TXSP corrupts the scan cursor with a wild value, which session
#63 traced as `TXSP = 140702518392224 = cmd's PATBCL`.

### Fix (committed)

```c
L_SALT2:
    D(XCL) = D(D_A(PDLPTR) + DESCR);
    D(YCL) = D(D_A(PDLPTR) + 2*DESCR);
    D_A(PDLPTR) -= 3*DESCR;
    D(PATICL) = D(XCL);
    if (D_A(PATICL) == 0)
        goto L_SALT3;
    /* session #64: only restore scan cursor (TXSP) from slot[2] for non-FNC
     * traps.  For FNC traps (STREXCCL, FNCDCL, etc.), slot[2] holds handler-
     * specific data (e.g. a PATBCL heap pointer), NOT a cursor offset.
     * Writing it into TXSP corrupts the cursor, causing spurious matches. */
    if (!(D_F(PATICL) & FNC)) {
        S_L(TXSP) = D_A(YCL);
        goto L_SCIN3;
    }
    D(PTBRCL) = D(D_A(PATICL));
L_PATBRA:
    ...
```

### Gates (with TXSP-only fix committed)

| Gate | Baseline | s64 |
|------|----------|-----|
| fence_function | 10/10 | **10/10** ✓ |
| fence_suite | 44/4/0 | **44/4/0** ✓ |
| guard5 | OK | **OK** ✓ |
| beauty self-host | 42 lines | **42 lines** ✓ |

**No regression.  No gate-count improvement.**  Fix is correctness-
improving and committable per RULES.md (eliminates a latent
corruption mode).  In the current bug class, the corruption happened
to not affect the wrong-match outcome because the walker dispatched
the leaked alt via PATBRA (FNC=1) which doesn't run line 11498's
write — but session #63's gdb evidence showed the corruption WAS
happening on a parallel walker path.

### What TXSP fix alone doesn't repair (still 4 wrong-answer FAILs)

Re-traced repro5 with TXSP fix applied.  TXSP correctly stays at 0
throughout walker descent (was 140702518392224 in s63).  But output
is still `unexpected match`:

The 6th SALT2 event has `slot1=0x60` (non-FNC, valid offset under
cmd PATBCL), `PATBCL=cmd` (set by STREXCCL at event #5), and the
walker takes SCIN3 fall-through.  SCIN3 reads
`D(PATBCL + PATICL + DESCR) = D(cmd + 0x68)` — a valid pattern node
inside cmd, specifically the `'ab'` alternative of `'a' | 'ab'`.
The walker dispatches that alternative, matches `'ab'` from cursor
0, advances to cursor 2.  RPOS(0) succeeds → "unexpected match".

The walker is dispatching a leaked inner-FENCE alt-cont under
restored inner PATBCL.  FENCE seal should have prevented this.

### FNCDCL-at-P2 attempt (not committed; refuted)

Hypothesis: place FNCDCL at P2 (top of leaked region) instead of P1
(clean base) so walker hits seal before any leaked alts.

Implemented as a single-block edit in FNCA's success path:

```c
{
    int_t p2_save = D_A(PDLPTR);   /* P2 = top of leaks */
    POP(NHEDCL); POP(NAMICL); POP(PDLHED);
    POP(PDLPTR);                    /* PDLPTR = SCFLCL slot */
    D_A(PDLPTR) -= 3*DESCR;         /* discard SCFLCL → P1 */
    POP(YCL); POP(XCL); POP(PATICL); POP(PATBCL); POP(MAXLEN);
    D_A(TMVAL) = D_A(PDLPTR);       /* TMVAL.a = P1 */
    D_F(TMVAL) = D_V(TMVAL) = 0;
    D_A(PDLPTR) = p2_save + 3*DESCR;
    if (D_A(PDLPTR) > D_A(PDLEND)) BRANCH(INTR31)
    D(D_A(PDLPTR) + DESCR) = D(FNCDCL);     /* seal at P2 */
    D(D_A(PDLPTR) + 2*DESCR) = D(TMVAL);    /* slot[2] = P1 */
    D(D_A(PDLPTR) + 3*DESCR) = D(LENFCL);
}
goto L_SCOK;
```

**Result**: still `unexpected match`.  Trace evidence shows FNCDCL
**is** placed at P2 (e.g. PDLPTR=0x...a30) but **never fires** —
the walker never reaches it.

### Architectural finding — why FNCDCL placement is moot

After FNCA returns success via SCOK, control returns up the call
stack to the enclosing `*outer` scan dispatched via DSAR/STARP6.
That scan continues (more ARBNO iterations of `*cmd`).  Eventually
`*outer` returns and **its STARP2 success path runs**.

STARP2 does:

1. `POP(PDLPTR)` from cstack — restores PDLPTR to its
   `*outer`-entry value, **far below the FNCDCL I placed at P2**.
2. Installs its own STREXCCL sentinels (top + bottom) bracketing
   the entire `*outer` leak region.

After STARP2, **FNCDCL is in abandoned memory** — physically still
present, but above PDLPTR.  When RPOS(0) eventually fails and the
walker descends from current PDLPTR, it walks through STARP2's
STREXCCL bracketed region.  The walker hits STARP2's top STREXCCL
(PATBCL → cmd routing), then descends into the leak region — which
contains the still-physically-present leaked inner-FENCE alt-conts
from cmd's original matching.  Walker dispatches them under
PATBCL=cmd, finds valid pattern nodes, matches.

**Mechanism named**: FENCE's leaked alt-conts and `*outer`'s
STARP2 leak region OVERLAP in physical memory.  STARP2's PDLPTR-
restore abandons FENCE's seal but cannot remove the leaks (which
were pushed during cmd's matching, before STARP6's PDLPTR snapshot
existed in this nesting level — actually they're above PDLPTR after
STARP2 restore so they're "abandoned" too, but still in physical
memory and still dispatchable when walker descends from a higher
PDLPTR).  STARP2 then re-routes the walker through the abandoned
region under inner PATBCL=cmd.  FENCE seal is bypassed.

This is a refinement over session #57's hypothesis (which named
"multi-iteration ARBNO leaks unprotected because their STREXCCL
was consumed").  Session #57 located the bug class correctly but
explained the failure path imprecisely.  Session #64 names the
exact failure mechanism: STARP2 abandons the seal AND re-routes
the walker through the abandoned leaks.

### Implications for fix design

Re-evaluating session #57's candidates:

- **(a) PDLHED-bound SALT2 walker** — would prevent walker from
  descending below PDLHED, but PDLHED is the ENCLOSING scan's
  base, not FENCE's seal-base.  Doesn't help.
- **(b refined) Paired bottom STREXCCL** — session #58's fix.
  Eliminated all 6 CRASHes.  Doesn't help with semantic FENCE-seal
  violations because STARP2 abandons the seal.
- **(c) Persistent STREXCCL across iterations** — doesn't help;
  by the time walker reaches the relevant region, it's under
  STARP2's outer routing, not FNCA's.
- **(d) Truncate-on-success with deferred-alts array, OR
  zero-leaks at FNCA-success** — **architecturally correct**.
  FNCA's success path must PHYSICALLY zero the leaked alt-conts
  (slot[1] = 0 makes them benign — walker takes SALT3 path) so
  even after STARP2 abandons the region and re-routes through it,
  the leaks are no longer dispatchable.

Session #54's "targeted slot-zeroing" was right in spirit but
**wrong in placement**.  Session #54 zeroed at L_STARP2/L_DSARP2
(STAR's success path), which is too late — by then the leaks have
already been "blessed" by STARP2's STREXCCL routing for legitimate
ARBNO redo purposes.  And session #54's zeroing also nuked
legitimate inner-backtrack continuations (guard5).

Session #65's zeroing should be **at FNCA's success path** — walk
PDL from P1+3*DESCR to P2, zero slot[1] of any non-FNC trap.
Important distinction:

| Session | Where | What gets zeroed |
|---------|-------|------------------|
| s54 (rejected) | STAR/DSAR success | All inner-pattern leaks below STAR's snapshot — including legitimate ARBNO redo conts and FENCE leaks indistinguishably |
| s65 (proposed) | FENCE success | Only leaks from inner-P matching (between FNCA-entry-PDLPTR and post-SCIN PDLPTR).  STAR/DSAR's own redo conts are NOT in this region. |

The s65 placement is narrow and surgical: only zeros what FNCA
itself "owns" as inner-P leakage.

### Why s65 should preserve guard5

Guard5 is `cmd=(LEN(1)|LEN(2)); outer=(*cmd 'X'); s='ABX'` — **no
FENCE involved**.  FNCA never runs.  s65 zeroing at FNCA-success
never fires.  guard5's inner-backtrack continues to work via the
existing UNSC/DSAR-redo machinery.

### Why s65 should fix tests 119/124/127/129

All four use FENCE — that's the bug-class boundary established
by session #55's Tier F (16/16 PASS without FENCE).  At FENCE
success, zeroing leaked alt-conts ensures STARP2's later STREXCCL
routing has nothing dispatchable to land on.  Walker takes SALT3
path through zeroed slots, descends to STARP2's bottom STREXCCL,
restores PATBCL=outer, continues correctly.

### Recommended session #65 plan

1. Apply s64 TXSP fix (already committed at `<HASH>`).

2. Implement FNCA-success leaked-alt zeroing.  Pseudocode:
   ```c
   /* In FNCA success path, after POPs but before placing FNCDCL: */
   {
       int_t p1 = D_A(PDLPTR);  /* clean base after POP+sub */
       int_t p2 = p2_save;       /* top of leaks (saved before POPs) */
       int_t p;
       for (p = p1 + 3*DESCR; p <= p2; p += 3*DESCR) {
           if (!(D_F(p + DESCR) & FNC)) {
               D_A(p + DESCR) = 0;       /* zero slot[1] */
               D_F(p + DESCR) = 0;
               D_V(p + DESCR) = 0;
           }
       }
   }
   ```

3. Test gate stack:
   - guard5 must produce `inner backtrack worked`
   - Tier F all 16 must remain PASS
   - fence_function 10/10
   - fence_suite **target ≥45/48** (119/124/127/129 → OK)
   - beauty ≥500 lines

4. If beauty advances ≥500 lines: commit + close F-2 Step 3a.
5. If beauty stalls at intermediate count but fence_suite improves:
   commit gate-improving fix and document next bug class.
6. If guard5 breaks or any prior-OK test regresses: revert,
   document in s65 findings.

### Files this session

- `csnobol4/isnobol4.c` — TXSP fix at L_SALT2 (committable, +8/-2 lines)
- `csnobol4/docs/F-2-Step3a-session64-findings.md` — full investigation
- `.github/PLAN.md` — state-cell update
- `.github/GOAL-CSN-FENCE-FIX.md` — this update

### Honest checkpoint

Sessions #44–#64 = 20 sessions on F-2 Step 3a.  fence_function preserved
10/10.  Tier F preserved 16/16 since #55.  fence_suite at 44/4/0
since #58 (7 sessions).  Beauty at 42 lines since #58.

Session #64's contributions:

1. **Pinpointed the exact line** (`isnobol4.c:11498`) for the
   TXSP corruption session #63 traced.  Fix is committable and
   gate-neutral — locks in correctness improvement.
2. **Refuted FNCDCL-at-P2** as a sufficient fix via direct trace
   evidence.
3. **Named the architectural mechanism**: STARP2's PDLPTR-restore
   abandons FENCE's seal AND re-routes the walker through the
   abandoned region.  Refines session #57's framing.
4. **Refined fix recommendation**: zero leaked alts at FNCA-success
   (NOT at STARP2 like session #54 tried).  The placement
   distinction is the key insight session #65 needs.

The pattern of "land an analytic step forward, hit deeper bug"
continues, but session #65 has a specific surgical fix to attempt
with clear test predictions.

---

## Session #65 update — fence_suite oracle-verified, expanded to 53 tests, bug class sharpened (NO runtime change)

Session #65 was scoped to **verify the test suite against the SPITBOL oracle
and fill its actual coverage gaps** before any further attempt at the
runtime fix outlined in session #64's plan (FNCA-success leaked-alt zeroing).

### Why this scope

20 sessions on F-2 Step 3a, six successive "land a fix, hit deeper bug"
cycles, two prior sessions where the proposed fix was implemented and
refuted by gates.  Before another such cycle, audit the gates themselves.
The audit found three concrete corpus errors and two structural gaps that
would have invalidated whatever fix landed next.

### Key discoveries

#### 1. SPITBOL was 46/2/0 of 48, not 47/1 as the goal file claimed

Direct measurement on session #65's HEAD (built csnobol4 from clean clone,
ran fence_suite both `csnobol4` and `spitbol` Makefile targets):

- **Test 127's `.ref` was wrong for the gate.** The .ref (`k=age s="age":42
  n=42 b=`) was generated under SPITBOL `-b` (case-fold ON) where input
  variable `s` collides with capture variable `S`.  The Makefile invokes
  SPITBOL with `-bf` (case-fold OFF), where they don't collide and SPITBOL
  produces `k=age s= n=42 b=`.  Regenerated `.ref` under `-bf`.
- **Tests 140 and 141 had cross-dialect label-name collisions.** Used
  `shift`/`Shift` and `grab`/`Grab` as labels.  Under SPITBOL's case-fold
  default these are duplicates and SPITBOL rejects with ERROR 217.  csnobol4
  treats them as distinct.  Renamed labels to `inner`/`outer` and
  `grab`/`catch` so both implementations accept the source.

After both corrections, **SPITBOL `-bf` is 53/0/0 of 53** — the first time
the oracle gate is actually clean.

#### 2. Test 118 was structurally degenerate

Test 118's source order:
```
        cmd = FENCE('a' | 'ab')
        s = 'aab'
        s POS(0) *outer RPOS(0)                               :S(BAD)F(GOOD)
        outer = ARBNO(*cmd)
```

In SNOBOL4 statements execute in source order.  `outer` is unassigned at
match time, so `*outer` dereferences a NULL pattern and the match fails
immediately — the FENCE machinery never runs.  Both csnobol4 and SPITBOL
agree on the no-match outcome ("FENCE sealed") only because no one ran
the seal-test logic.  Test 118 was listed in the goal file's session #51
strategy section as a target the fix must hit; it never actually exercised
the bug.

Replaced 118 with comment-only documentation of the degeneracy.  Added
test 149 as the proper version (outer assigned BEFORE match).

#### 3. The bug class is sharper than session #62 stated

Session #62 reported the bug requires four ingredients (`*var` outer +
ARBNO inside + `*var` inside + FENCE inner).  Tier G's two new negative
discriminators tighten this:

- **Test 150** (`outer = (*cmd | *cmd *cmd | *cmd *cmd *cmd)` with no
  ARBNO, same FENCE'd cmd, same backtrack-needed input) **PASSES** on
  csnobol4.  This proves the bug requires **ARBNO specifically**, not
  generic-iteration.  The bug is in ARBNO's redo-trap mechanism, not in
  any iterating outer construct.
- **Test 151** (ARBNO of *inline* FENCE with backtrack-needed input,
  no `*var` indirection) **PASSES** on csnobol4.  This proves the bug
  requires **`*var` indirection** of the FENCE pattern, not inline FENCE.

The refined bug-class conjunction is precisely:
1. **`*var` indirection** of a FENCE-containing pattern, AND
2. **ARBNO** as the outer iterator (not other iteration shapes), AND
3. Tail-anchor failure that backtracks across the FENCE seal.

This rules out broader hypotheses sessions #50/#54/#57 had entertained.

#### 4. Test 127's failure was masked by case-fold collision

Test 127 used `S` as a capture variable (`BREAK('"') . S`) and `s` as the
input string.  Under SPITBOL `-b` they collide; under `-bf` they don't.
csnobol4 always treats them as distinct.  The original `.ref` was generated
under `-b` semantics, making it impossible to tell what the test was
actually measuring.

**Test 152 (added)** is 127 with capture variables renamed to `SVAL`,
`NVAL`, `KVAL`, `BVAL`.  Same FENCE structure, no case-fold ambiguity.
csnobol4 still fails 152 — that's bug 2 (conditional-assign inside FENCE
not committed on success), which 127's case-fold collision had been
hiding.

### What landed (corpus)

5 new test files (10 .sno+.ref pairs total), 4 corrections:

| Action | File | Purpose |
|--------|------|---------|
| Modify | 118.sno | Comment-only — documents structural degeneracy |
| Modify | 127.ref | Regenerated under SPITBOL `-bf` |
| Modify | 140.sno | Labels renamed for SPITBOL portability |
| Modify | 141.sno | Labels renamed for SPITBOL portability |
| Add    | 148.sno + .ref | Bug-class POSITIVE — variant of 119, input `'ab'` |
| Add    | 149.sno + .ref | Bug-class POSITIVE — corrected version of 118 |
| Add    | 150.sno + .ref | NEGATIVE — no-ARBNO outer iteration |
| Add    | 151.sno + .ref | NEGATIVE — inline FENCE in ARBNO |
| Add    | 152.sno + .ref | Bug-class POSITIVE — 127 with renamed captures |

corpus advanced from `d9f09d6` to `6f00145`.

### What landed (csnobol4)

3 files modified — test infrastructure only, no runtime source changes:

- `test/fence_suite/Makefile` — Tier G integration, count strings updated,
  header rewritten with session #65 narrative
- `test/fence_suite/README.md` — title updated, Tier G section appended
  (per-test role table + findings summary)
- `docs/F-2-Step3a-session65-findings.md` — full session writeup (180 lines)

csnobol4 advanced from `723ac19` to `5fbf2ce`.

### Suite results after session #65

| Implementation | Tests | OK | FAIL | CRASH |
|----------------|-------|----|------|-------|
| SPITBOL `-bf`  | 53    | **53** | 0 | 0 |
| csnobol4       | 53    | 46 | 7    | 0 |

The 7 csnobol4 FAILs (119, 124, 127, 129, 148, 149, 152) form the
**bug-class regression target**.

### What this means for the next runtime-fix session

Session #64 proposed FNCA-success leaked-alt zeroing as the next attempt.
That plan is consistent with Tier G's negative-discriminator evidence:
inline FENCE inside ARBNO works correctly (test 151), so FNCA itself
isn't the leak source — the leak is in how `*var`-dispatched FENCE hands
state back through STAR/DSAR.  Bug requires ARBNO redo specifically,
consistent with session #57's multi-iteration leak diagnosis.

**However**, session #62's PDL-dump diagnostic (no SALT2 events between
post-STARP2 dump and wrong-match output) suggests the wrong match goes
through the SUCCESS path, not the failure walker.  If true, zeroing
slot[1] of leaked traps doesn't help — the walker never reads them.

Session #62 and session #64 are in tension on this point.  Session #64's
narrative was written without re-running session #62's diagnostic to
falsify it.  This tension was not visible from inside session #64; it
became visible only after session #65's audit.

**Concrete plan for session #66:**

Re-run session #62's PDL-dump diagnostic on **test 148** (not 119).  Test
148 has shorter input (`'ab'` not `'aab'`) and a single ARBNO iteration
of FENCE-sealed `'a'` before tail-anchor failure.  The diagnostic state
space is much smaller than 119's, making the trace easier to read.  The
trace will either:

- **Show SALT2 events on the wrong-match path** → session #64's framing
  holds → zeroing is the right fix → implement it.
- **Show no SALT2 events** → session #62's framing holds → zeroing won't
  help → redirect investigation to the success path (likely STARP2's
  redo dispatch).

Either outcome closes the open tension before any code is committed.

### What session #65 did NOT do

- Did NOT modify any runtime source (`isnobol4.c`, `snobol4.c`, `v311.sil`,
  `lib/pat.c` all unchanged).
- Did NOT advance beauty self-host (still 42 lines).
- Did NOT implement session #64's proposed zeroing fix.
- Did NOT resolve the session #62 vs #64 tension (that's session #66's job).

### Honest checkpoint

Sessions #44–#65 = 21 sessions on F-2 Step 3a.  Session #65's contribution
is non-runtime: it sharpens the gate.  This is similar to session #55's
Tier F contribution.  Beauty self-host and fence_function counts unchanged
because no runtime code changed.

The 7-FAIL bug-class target is more specific than the prior 4-FAIL target
in two ways: (a) it includes tests 148/149 which are harder for any
"accidentally passes" fix to satisfy than 119/129 alone (different input
strings, different output messages), and (b) the negative discriminators
150/151 reject overly-broad fixes that the prior gate would have allowed.

---

## Session #65 (continued) — L_FNCD bug isolated by attribute-grid analysis

### What was done

Built attribute grid for all 53 fence_suite tests (FENCE present, *var
indirection, ARBNO, RPOS(0), conditional capture, *var-to-FENCE chain,
ARBNO-of-*var-to-FENCE chain, match via *var, nested *var to FENCE).
Sorted by csnobol4 result.  Looked for the column or column-combination
that's uniformly true across all 7 FAILs and uniformly false across
all 46 OKs.

The two failure clusters became visible immediately:

- **Cluster A** (119, 129, 148, 149) — Y across `FENCE`, `*var`, `ARBNO`,
  `RPOS(0)`, `*var-to-FENCE`, `ARBNO-of-*var`, `ARBNO-of-*var-to-FENCE`,
  `match-via-*var`, `nested-*var-to-FENCE`.
- **Cluster B** (124, 127, 152) — Y across `FENCE`, `RPOS(0)`,
  `dot-capture`; N across the *var/ARBNO columns.

No single column unifies them.  But the *behavioral* attribute does:
in both clusters, FENCE matches successfully, then something post-FENCE
in the same SCIN frame fails, and there exists a backtrackable
alternative outside the FENCE that should be tried.  Reading L_FNCD's
body revealed the bug.

### The bug — one line

`isnobol4.c:12437`:

```c
L_FNCD:
    D(PDLPTR) = D(YCL);            /* restore to inner base */
    D_A(PDLPTR) -= 3*DESCR;        /* flpop: consume SCFLCL trap */
    D(NAMICL) = D(NHEDCL);
    BRANCH(FAIL)                   /* <- THIS IS WRONG */
```

`BRANCH(FAIL)` is `return 1` from SCIN.  It exits the entire scan.

SPITBOL's analog `p_fnd` (sbl.min:12044):

```
p_fnd  ent  bl_p0
       mov  xs,wb            pop stack to fence() history base
       brn  flpop            pop base entry and fail
```

`flpop` (sbl.min:16242):
```
flpop  rtn
       add  xs,*num02        pop two entries off stack
       ejc                   (drops into failp)
```

`failp` (sbl.min:16256):
```
failp  rtn
       mov  xr,(xs)+         load alternative node pointer
       mov  wb,(xs)+         restore old cursor
       mov  xl,(xr)          load pcode entry pointer
       bri  xl               jump to execute code for node
```

So SPITBOL's seal handler does NOT exit the scan.  It pops to inner-base,
pops two more entries, then `failp` POPS THE NEXT ALT FROM THE STACK
AND DISPATCHES IT.  csnobol4's L_TSALT is the analog of `failp`.

The fix is one line: `BRANCH(FAIL)` → `goto L_TSALT`.

### Two opposite symptoms from one bug

- **Cluster B** (124/127/152): walker fails too early.  FENCE matches,
  RPOS(0) (or successor) fails, walker hits FNCDCL, BRANCH(FAIL) exits
  scan.  Outer alts are still on PDL but never tried.
- **Cluster A** (119/129/148/149) + **150**: BRANCH(FAIL) was OVER-
  correcting.  It blocked all alts including LEAKED inner-FENCE alts
  physically still on PDL above PDLPTR-after-rewind.  Removing
  BRANCH(FAIL) lets walker reach those leaks.

The two symptoms are the two sides of the same overcorrection.

### Why the attempt regressed 150

Tested `BRANCH(FAIL)` → `goto L_TSALT`:

| Test | Baseline | s65-L_FNCD attempt |
|------|----------|-------------------|
| 124 (cluster B)                    | FAIL | **OK** ✓ |
| 119, 129, 148, 149 (cluster A)     | FAIL | FAIL (unchanged) |
| 127, 152 (cluster B variants)      | FAIL | FAIL (unchanged) |
| **150 (negative discriminator)**   | **OK** | **FAIL** ✗ |
| guard5                             | OK | OK |
| fence_function                     | 10/10 | 10/10 |

Net 46/7/0 unchanged but with one previously-passing test now wrong-
answer.  Per RULES.md regression-in-error-class, NOT committed.

### The composed fix shape

Session #66 must combine:

1. **L_FNCD: `goto L_TSALT`** (this attempt's diff) — necessary.
2. **One of:**
   - (a) Physical leak removal at FNCA-success.  Walk PDL from
     inner-base+3*DESCR to old_PDLPTR; zero slot[1] of non-FNC entries.
     (Session #64's proposed runtime work.)
   - (b) Persistent STREXCCL bottom-sentinel across multi-iteration
     ARBNO contexts.  (Session #58 implemented top-and-bottom; this
     would extend.)

(1) lets the walker reach legitimate alts; (2) prevents it from reaching
leaked ones.  Together they should:
- flip 119, 124, 127, 129, 148, 149, 152 → OK
- keep 150 OK (negative discriminator)
- keep 151 OK (negative discriminator)
- preserve fence_function 10/10
- preserve Tier F 16/16
- preserve guard5

### Resolution of session #62/#64 narrative tension

Session #62: "no SALT2 events between post-STARP2 dump and wrong-match
output → bug on success path."  Session #64: "failure-walker dispatches
abandoned-seal region → bug on failure-walker path."  These looked
contradictory.

Both were partially right:
- The leaks are formed on the success path (FNCA's success leaves them
  on PDL above PDLPTR-after-rewind).  Session #62 was right about
  WHERE the leaks come from.
- The walker dispatches them on the failure path (BRANCH(FAIL)'s
  removal exposes them).  Session #64 was right about HOW they cause
  wrong matches.

The composed fix addresses both: leak removal at the success-path
formation site (per #62) + correct walker continuation (per #64).

### Files this session-continuation

- `csnobol4/docs/F-2-Step3a-session65-L_FNCD-attempt.diff` — 1-line
  patch, applies clean to HEAD `5fbf2ce`.
- `csnobol4/docs/F-2-Step3a-session65-L_FNCD-findings.md` — 175-line
  writeup with full SPITBOL comparison and minimal repro.
- This goal-file update + PLAN.md state-cell update.
- csnobol4 advanced from `5fbf2ce` to `b2764cf` (docs+diff only).
- No source changes committed.

### Concrete plan for session #66

```bash
# 1. Apply the L_FNCD fix
cd /home/claude/csnobol4
git apply docs/F-2-Step3a-session65-L_FNCD-attempt.diff

# 2. Implement option (a): leaked-alt zeroing at FNCA-success.
#    See csnobol4/docs/F-2-Step3a-session64-findings.md "session #65 fix
#    recommendation" section for the pseudocode.  Insert the loop in
#    isnobol4.c L_FNCA's success path, between the POPs that restore
#    outer state and the FNCDCL push (around line 12381-12388).

# 3. Build and gate
make -f Makefile2 xsnobol4 && cp xsnobol4 snobol4
cd test/fence_suite && make csnobol4 | tail -2
cd ../fence_function && make | tail -1

# 4. Expected: 51/2/0 of 53 (only 127, 152 = bug 2 remain)
#    OR 53/0/0 if the composed fix also resolves bug 2.

# 5. If 150 still regresses, try option (b) instead of (a).
```

---

## Session #66 update — bug location identified definitively (NO runtime change)

Session #66 followed session #65 (continued)'s plan: applied the L_FNCD
`goto L_TSALT` patch + implemented session #64's proposed FNCA-success
leaked-alt zeroing.  Result: identical to L_FNCD-only baseline (46/7/0,
124↔150 swap).  The zeroing **fired correctly** (verified via trace) but
**had no effect** on cluster A.

Reverted both attempts, kept only env-gated trace instrumentation, ran
on test 148 (smallest cluster A repro: input `'ab'`).

### The decisive trace evidence

Test 148 wrong-match path produces 5 SALT2 events before "leak: seal
failed" output (refines session #62's "no SALT2 events" claim).  The
critical sequence:

```
[12] SALT2 PDLPTR=e940 slot1={a=...a560,f=1,v=2} slot2={a=cmd}     <- top STREXCCL
[13] STREXC-FIRE  old_PATBCL=outer  new_PATBCL=cmd
[14] SALT2 PDLPTR=e910 slot1={a=0x60, f=0, v=0}                    <- *** the bug ***
[15] SCOK  PDLPTR=e910 PATBCL=cmd PATICL=0x90  TXSP=0
[16] FNCA-ENTRY  <- FENCE re-entered (matches 'ab' alt)
```

The entry at PDLPTR=e910 with `slot[1]={a=0x60, f=0}` is BETWEEN
top-STREXCCL (e940) and bottom-STREXCCL (e8e0) — INSIDE the protected
leak region.  After top STREXCCL switches PATBCL to cmd, walker reads
this non-FNC entry, session #64's fix routes it to SCIN3 fall-through,
SCIN3 dispatches `D(cmd + 0x60 + DESCR)` = a real cmd-pattern node
(the 'ab' alt of `'a'|'ab'`), match succeeds.

### What this resolves

The session #62 vs #64 narrative tension is resolved by this trace:
- Session #62 was wrong about the SALT2 count (test 119 has more events
  than 148 because of longer input, but the bug shape is the same:
  walker dispatches a SCIN3-pushed entry INSIDE the protected leak
  region).
- Session #64's "abandoned-seal region above STARP2" framing was right
  about the path (failure walker) but wrong about the region (entry is
  IN the protected region, not above PDLPTR-after-STARP2).

### Why the FNCA-success zeroing didn't fix it

FNCA's frame is [P1..P2] where P1 = PDLPTR before SCFLCL push.  The
problematic entry at e910 sits at PDL position pushed by SCIN3 during
**cmd's outer pattern walk** (not during FENCE's inner P matching).
That position is in the OUTER scan's PDL region — specifically, inside
[STREX_entrypdl..PDLPTR_at_STARP2_entry] — which is OUTSIDE FNCA's
frame.  FNCA-success zeroing literally cannot reach it.

### The correct fix shape — option (A2)

At L_STARP2 success, walk the leak region [STREX_entrypdl+3*DESCR ..
PDLPTR_at_STARP2_entry].  If ANY entry is FNCDCL (PATBRA case 40),
zero slot[1] of all non-FNC entries in the region.  Else leave alone.

This conditional design:
- Preserves guard5 (no FENCE → no FNCDCL → no zeroing → DSAR-redo
  machinery intact).
- Should fix all 7 cluster A/B FAILs (FENCE → FNCDCL present →
  zeroing kills the SCIN3 leak before walker can dispatch it).
- Is gate-targeted and testable: ≥51/53 expected.

### Recommended session #67 plan

```bash
cd /home/claude/csnobol4

# 1. Apply L_FNCD patch (necessary for cluster B).
git apply docs/F-2-Step3a-session65-L_FNCD-attempt.diff

# 2. Optionally apply diagnostic patch for re-trace ability.
git apply docs/F-2-Step3a-session66-diagnostic.diff

# 3. Implement option (A2) at L_STARP2 success path
#    (isnobol4.c around line 12247, after the sentinel-install block).

# 4. Build and gate
make -f Makefile2 xsnobol4 && cp xsnobol4 snobol4
# 4a. guard5  (expect: inner backtrack worked)
# 4b. fence_function (expect: 10/10)
# 4c. fence_suite (expect: 51+ OK)

# 5. Commit only if all gates pass.
```

### Files this session

- `csnobol4/docs/F-2-Step3a-session66-findings.md` — full investigation.
- `csnobol4/docs/F-2-Step3a-session66-diagnostic.diff` — reusable
  trace patch (env-gated `S148_TRACE=1`).
- This goal-file update + PLAN.md state cell.
- No runtime source changes.
- csnobol4 advanced to `451ccae` (docs only).

### Honest checkpoint

Sessions #44–#66 = 22 sessions on F-2 Step 3a.  fence_function preserved
10/10.  Tier F preserved 16/16 since #55.  fence_suite at 46/7/0 since
#65.  Beauty at 42 lines since #58.

Session #66's genuine new contribution: **direct trace evidence
pinpointing the bug** (slot[1].a=0x60 at PDLPTR=e910 on test 148) and
the session #64 fall-through mechanism (`if !FNC: TXSP = D_A(YCL); goto
L_SCIN3`) that dispatches it under switched PATBCL.  Plus a falsifiable
fix candidate (A2) with gate predictions.

The pattern of "narrow the bug, hit deeper structural question"
continues, but session #67 has the smallest precise target yet:
"zero entries in this specific PDL range at this specific point, gated
on FNCDCL presence."  Not a structural redesign, just an additional
small surgery at L_STARP2.

---

## Session #67 update — A2 zeroing landed for Cluster B; refutes session #66 framing for Cluster A (NO runtime change committed)

Session #67 implemented session #66's recommended option (A2): apply the
L_FNCD goto-L_TSALT patch + add zeroing of non-FNC slot[1]s in the leak
region at L_STARP2 success, gated on FNCDCL presence.

### Gates after composed s67 fix

| Gate | s64/s65/s66 baseline | **s67 (composed)** |
|------|--------------|-------------------|
| guard5 | OK | **OK** ✓ |
| fence_function | 10/10 | **10/10** ✓ |
| Tier F (132–147) | 16/16 | **16/16** ✓ |
| fence_suite total | 46/7/0 | **47/6/0** (gained test 124) |
| beauty self-host | 42 lines | (not measured) |

Three gate variants for A2 tested:

| Variant | Cluster A | guard5 |
|---------|-----------|--------|
| A2 + FNCDCL-in-current-region (s66 plan) | unchanged | OK |
| A2 + FNCDCL-anywhere-PDLHED..PDLPTR (committed shape) | unchanged | OK |
| A2 + unconditional zero | **FIXED 51/2/0** | **BROKEN** |

### Genuinely-new finding: refutes session #66 framing

Trace evidence on test 148 (env-gated `A2_TRACE=1`) shows that **STARP2 #1
fires BEFORE FNCA runs anywhere on PDL**. The bug entry `{a=0x60}` lives
in STARP2 #1's leak region, but at that moment FNCDCL doesn't exist
ANYWHERE on PDL. Session #66 hypothesized the bug entry was a "leaked
inner-FENCE alt-cont" between STREXCCL sentinels — that framing requires
FENCE to have run, but FENCE hasn't run at STARP2 #1 time.

The leak source is therefore NOT FENCE's inner alt-conts. Some pattern
matching activity inside STARP6 #1's SCIN call pushes the `{a=0x60}` entry
and never cleans it up. The walker later mis-routes through it because
STARP2 #1's STREXCCL pair switches PATBCL=cmd, and 0x60 happens to be a
valid offset inside cmd's compiled pattern (the 'ab' alt of `'a'|'ab'`).

### Five fix candidates documented for session #68

1. Side-channel `fence_active` flag (timing wrong — see findings).
2. Tag SCIN3 pushes with FENCE-context metadata (invasive).
3. Validate slot[1].a range against PATBCL pattern size at L_STREXC time.
4. Walk PDL deeper than STREX_entrypdl (to PDLHED) — risky.
5. **Investigate STARP6 #1's identity** to find the source primitive.

### Recommended session #68 plan

1. Apply `docs/F-2-Step3a-session67-A2-attempt.diff` (composed fix; gains
   test 124, all floors preserved).
2. Apply `docs/F-2-Step3a-session67-diagnostic.diff` for trace
   instrumentation.
3. Tag every SCIN3 push with the PATBRA case that dispatched into it. Run
   test 148. Find which case pushed the `{a=0x60}` entry. The entry was
   pushed during STARP6 #1's SCIN call.
4. Examine that primitive's success-path cleanup. Likely missing a PDLPTR
   rewind step.
5. Test gates: guard5, fence_function 10/10, Tier F 16/16, fence_suite
   ≥51/53 (target 53/53 minus bug-2 = 127/152).
6. If beauty advances ≥500 lines: commit + close F-2 Step 3a.

### Files this session

- `csnobol4/docs/F-2-Step3a-session67-A2-attempt.diff` — composed patch
  (54 lines): L_FNCD goto-L_TSALT + A2 zeroing with PDLHED gate.
- `csnobol4/docs/F-2-Step3a-session67-diagnostic.diff` — instrumentation
  (96 lines): STARP6/DSARP2 entry counters, A2 STARP2 PDL dump with FNC-
  case identification, FNCA-success FNCDCL placement log. Env-gated
  `A2_TRACE=1`.
- `csnobol4/docs/F-2-Step3a-session67-findings.md` — full investigation
  with trace excerpts and five fix candidates.
- This goal-file update + PLAN.md state cell.
- No runtime source changes committed. Working tree: only the three new
  docs files untracked. Build verified at baseline (46/7/0).

### Honest checkpoint

Sessions #44–#67 = 24 sessions on F-2 Step 3a. fence_function preserved
10/10. Tier F preserved 16/16 since #55. fence_suite at 46/7/0 since #65;
session #67 bumps to 47/6/0 with composed fix (Cluster B closed, NOT
committed because Cluster A unchanged).

Session #67's contribution: empirical refutation of session #66 framing,
plus a clean composed patch that closes Cluster B and a clear next-session
diagnostic target (the STARP6 #1 source primitive identity).

---

## Session #67 update — Byrd Box FENCE per user direction (NO runtime committed)

After A2 attempts and the empirical refutation of session #66's framing,
user requested a structurally different approach: implement FENCE as a
proper Byrd Box (4 ports: alpha/beta/gamma/omega) with per-instance local
storage on C-stack, replacing the cstack PUSH/POP save/restore scheme.

### BB Implementation

`csnobol4/docs/F-2-Step3a-session67-BB-FENCE.diff` (202 lines).

Key design:
- **C-stack-local storage** via `struct fnc_bb` at top of `SCIN1` — each
  SCIN1 frame owns its own. Nested FENCEs get their own SCIN1 frame.
  Immune to RSTSTK and nested-SCIN cstack manipulation.
- **Two-trap protocol:** alpha pushes SCFLCL (inner-base sentinel); beta
  replaces it in-place with FNCDCL (the seal).
- **PDL truncation at beta:** `D_A(PDLPTR) = fence_trap_pos` drops any
  leaks P pushed. Makes the seal physical rather than relying on walker
  cooperation.
- **No cstack PUSH/POP** — entire save/restore is C-locals.

### Gate results — BB FENCE

| Gate | s64 baseline | **s67 BB** | s67 A2 |
|------|--------------|------------|--------|
| guard5 | OK | **OK** ✓ | OK |
| fence_function | 10/10 | **10/10** ✓ | 10/10 |
| Tier F (132–147) | 16/16 | **16/16** ✓ | 16/16 |
| fence_suite | 46/7/0 | **46/7/0** | 47/6/0 |

BB closes Cluster B (test 124) like A2 but regresses 150 — same trade-off
the L_FNCD-only attempt session #65 hit. **Net suite count unchanged from
baseline.** A2 is gate-incrementally better; BB is architecturally better.

### Why BB doesn't close Cluster A

Cluster A's bug entry is pushed by ARBNO/STAR machinery **before** any
FENCE machinery runs (session #67 earlier finding via trace). BB truncation
only drops leaks inside P's matching scope. Leaks from outer ARBNO are
below the FENCE trap and shouldn't be touched (they belong to outer scope).

The bug is **structurally outside FENCE**. No FENCE rewrite — clean BB or
otherwise — can close Cluster A.

### Architectural verdict

BB FENCE is strictly cleaner than the previous cstack-PUSH/POP scheme:
- 9-PUSH/9-POP per call → 9 C-local assignments per call
- No RSTSTK hazard
- No SAVSTK/cstack interaction with nested SCIN
- 4 ports clearly labeled
- Physical seal via truncation

**A2 zeroing on top of BB FENCE would close 150** without disturbing the
BB structure (orthogonal concerns: BB cleans inner-scope PDL at FENCE
boundaries, A2 cleans outer-scope PDL leaks at L_STARP2).

### Recommended session #68 plan

1. Apply `docs/F-2-Step3a-session67-BB-FENCE.diff` (architectural foundation).
2. Apply A2 zeroing on top (L_STARP2 hook with FNCDCL-anywhere gate) to
   recover test 150 and gain test 124. Expected: 47/6/0 with cleaner code.
3. Pivot Cluster A diagnosis to STARP6 #1's source primitive — find
   which PATBRA case dispatched the SCIN3 push that left `{a=0x60}` on
   PDL during STARP6 #1's inner SCIN. That primitive's success path is
   missing a PDLPTR rewind step.
4. If fix lands and beauty advances ≥500 lines: commit + close F-2 Step 3a.

### Files this session (final)

- `csnobol4/docs/F-2-Step3a-session67-A2-attempt.diff` — 54 lines
  (composed L_FNCD goto-L_TSALT + A2 zeroing with PDLHED gate; gives 47/6/0).
- `csnobol4/docs/F-2-Step3a-session67-BB-FENCE.diff` — 202 lines
  (Byrd Box FENCE; gives 46/7/0, architecturally cleaner).
- `csnobol4/docs/F-2-Step3a-session67-diagnostic.diff` — 96 lines
  (env-gated `A2_TRACE=1` instrumentation).
- `csnobol4/docs/F-2-Step3a-session67-findings.md` — full findings.
- This goal-file update + PLAN.md state cell.
- No runtime committed. csnobol4 working tree at HEAD `451ccae`.

### Two competing patches, neither closes F-2

A2: gate-incremental gain (47/6/0), uses zeroing as workaround.
BB: architectural cleanup (46/7/0), structural foundation for future work.

Session #68 should compose BB + A2 (orthogonal — BB is FENCE-internal, A2
is L_STARP2-external) and pivot to STARP6 #1 source-primitive diagnosis
for the remaining Cluster A tests.
