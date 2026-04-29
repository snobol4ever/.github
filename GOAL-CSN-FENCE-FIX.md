# GOAL-CSN-FENCE-FIX.md — CSNOBOL4 FENCE(P) builtin nested-recursion segfault

**Repo:** csnobol4 (primary), one4all (gates only)
**Done when:** `csnobol4 -bf -P64k -S64k beauty.sno < beauty.sno` produces
N>500 lines of output without segfault and without "Caught signal" diagnostic.
PLUS one4all Smoke=7, Broker=49 preserved.  PLUS the existing 10-test
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
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
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
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh         # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh  # PASS=49
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
- [x] Build: `bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh`
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
- one4all Smoke=7 and Broker=49 preserved.

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
      bash one4all/scripts/test_monitor_3way_sync_step_auto.sh \
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
- [ ] **Step 3a: pre-existing STAR-against-empty-subject bug.**
      Discovered while bisecting beauty's remaining failure: any `*var`
      pattern matched against an empty subject fails on csnobol4 but
      succeeds on SPITBOL — independent of FENCE.  Verified present in
      vanilla CSNOBOL4 2.3.3 (`a509cd7` "Initial import"), so it is
      NOT a regression from any FENCE work, but it IS what blocks the
      Step 3 done-when (beauty self-host ≥500 lines).

      **Session #47 update (2026-04-28): the simple STAR-against-empty
      repro now passes.** Either the bug class shifted under earlier
      FENCE fixes or the original diagnosis was overly narrow. The
      tiny repro `*LEN(0)` against `''` now matches on both csnobol4
      and SPITBOL.  Beauty still crashes at stmt 1074 (line 616, the
      `*snoParse *snoSpace RPOS(0)` chain) but the immediate crash is
      different — see investigation below.

      **Session #47 investigation found and partially fixed a different
      bug class** (cpypat / FENCE(P) node layout):

      Root cause: the 5-descriptor FENCE(P) node built by FNCPP with
      `slot[1].v=3` was incompatible with cpypat's STAR-style v=3
      semantics ("4-descr advance with slot[4] overlapping next node's
      title"). When FENCE(P) was concatenated into a larger pattern
      via CONPP→cpypat, the source FENCE(P) block was 5*DESCR but
      cpypat advanced 4*DESCR per iteration, causing it to read past
      the block end on the second iteration and corrupt destination
      pattern memory.

      Fix landed (working tree, uncommitted at session #47 end):
      1. `lib/pat.c` cpypat: handle `v7==4` as a self-contained 5-descr
         node — copies slot[4] AND advances 5*DESCR.
      2. `isnobol4.c` + `snobol4.c` FNCPP: writes `slot[1].v=4` instead
         of 3, preserving 5-descr / slot[4]=P layout (slot[3]=0 stays
         needed for QUICKSCAN length check at SCIN3).
      3. `isnobol4.c` + `snobol4.c` FNCA / FNCBX: also pushes/pops
         PDLPTR onto cstack so success and failure paths can rewind PDL
         past inner-SCIN's leaked entries before pushing the FNCD seal
         (success) or returning to outer failure walker (failure). Also
         removed the spurious `D(PDLHED) = D(PDLPTR)` clobber that was
         destroying outer's PDLHED.

      Results:
      - fence_function 10/10 PASS preserved (no regression).
      - Beauty tiny repro: was SIGSEGV, now Error 17 (controlled
        program error — no memory corruption).
      - Beauty self-host: still 36 lines (need 500+).
      - The remaining failure is **inside the recursive SCIN call from
        FNCA**: at SCIN1's PATBRA fall-through (BRANCH INTR13) because
        PTBRCL.a points to a non-pattern global function (KEYWRD).
        gdb stack shows `INTR13 ← SCIN1 ← SCIN ← SCIN1 (FNCA's SCIN
        call) ← SCIN`. So the inner pattern P that FNCA fed to SCIN
        has a corrupted dispatch tag — `D_A(ZCL)` points into `res`
        (global static area) instead of a valid PATBRA index.

      **Hypothesis for next session**: P itself becomes corrupted
      during inner SCIN matching. Candidates:
      - L_STAR's residual cache write `D(D_A(XPTR) + 7*DESCR) = D(YPTR)`
        is hitting P's territory if P is shorter than 8 descriptors.
      - PDL-based pattern building during inner-P evaluation overwrites
        P's slot[1] dispatch tag.
      - cpypat is being called inside inner-P matching with stale or
        wrong source/dest, corrupting P.

      Next session should add a SCIN1-entry trap that records the
      pattern at PATBCL and verifies slot[1] is FNC-flagged — re-run
      the trap during beauty to catch the first time P is corrupt.

- [ ] **Step 3b: SIL/C consistency cleanup.**  Per RULES.md the SIL is
      the source of truth; the same edits made in `isnobol4.c` and
      `snobol4.c` for cpypat / FNCPP / FNCA must be ported back to
      `v311.sil` and `lib/pat.c` (pat.c is C source, not generated, so
      that one is already canonical). Also: the SIL FNCAPT template at
      v311.sil:12203 still says `4*DESCR / v=2` — it needs to be
      reconciled with the implemented C 5*DESCR / v=4 layout.
- [ ] **Step 4: Build clean after Step 3a fix.**
      `bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh`
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
- csnobol4 @ session #49 (F-2 Step 3a continued — *cmd-FENCE-RPOS bug class isolated)
- one4all @ `06433f90`
- corpus @ session #49 (added test 068 — fence_via_var)
- x64 @ `71ff275`
- active step → **F-2 Step 3a** (cstack-overwrite at deep nesting blocks beauty self-host)

**Gates as of session #49 end:**
- fence_function/ suite: **10/10 PASS** (preserved)
- Tiny repro: **clean "Parse Error"** (unchanged from session #48)
- beauty self-host: **35 lines** (unchanged; SPITBOL: 646)
- one4all Smoke/Broker: NOT RUN (still gated on beauty)
- New test `corpus/crosscheck/patterns/068_pat_fence_fn_via_var`: **FAIL on csnobol4** (SEGV); SPITBOL passes. Added to corpus but NOT in fence_function/ TESTS list yet — will be added when fix lands.

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
