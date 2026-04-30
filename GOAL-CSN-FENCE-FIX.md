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
- csnobol4 @ session #57 (working tree CLEAN; session #56 strexccl-attempt.diff + session #57 diagnostic.diff in docs/)
- one4all @ `06433f90`
- corpus @ session #53 `6955503` (32 tests at IDs 100–131; .ref corrections for 127, 130) + session #55 untracked Tier F (132–147, 32 files)
- x64 @ `71ff275`
- active step → **F-2 Step 3a** (sessions #49–#57 all attempted seal-arithmetic / PDL-rewind / slot-zeroing / STREXCCL sentinel; session #57 trace evidence finally pinpoints **multi-iteration ARBNO leak class** — STREXCCL only protects most recent iteration; earlier iterations' leaks remain unprotected on PDL; session #58 should read SPITBOL p_str/=ndexc/flpop and implement (b refined paired-bottom-sentinel) / (c persistent STREXCCL) / (d truncate + deferred-alts))

**Gates as of session #57 end (working tree CLEAN, no code changes committed):**
- fence_function/ suite: **10/10 PASS** (preserved across baseline / s52 / s52+strexccl)
- fence_suite/ (48 tests, Tier A–F):
  - csnobol4 baseline (HEAD `1b2e28a`): **40 OK / 2 FAIL / 6 CRASH**
  - csnobol4 + session #52 patch:        **43 OK / 3 FAIL / 2 CRASH**
  - csnobol4 + session #56 patch (s52+strexccl): **43 OK / 3 FAIL / 2 CRASH** (no improvement over s52 alone)
  - SPITBOL oracle: 47 OK / 1 FAIL (test 127 known-bad-`.ref`)
- guard5 regression-prevention: ✓ across all three states
- Tier F (16 depth-stress tests): 16/16 across all three states
- beauty self-host: 35 lines (baseline) / not advanced this session

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
6. Smoke gates skipped if one4all not cloned.
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
