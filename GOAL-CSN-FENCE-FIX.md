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

**Canonical fix path: extend the FENCE PDL trap entry.**  FNCA's
trap entry currently occupies 3 descriptors (slots 1=FNCBCL,
2=cursor, 3=LENFCL).  Grow it to N descriptors (N = 5 or 6) and
store the FENCE outer-state values in the extended slots.  FNCB
and FNCC read them out of the trap entry directly via `GETDC`.
The PDL is already the right structure for this — it's how SCNR,
STARP, ATP, and every other PDL-using primitive in CSNOBOL4 saves
state, and it's how SPITBOL's `p_fna..p_fnd` puts saves on `xs`
(its pattern matching stack analog).  No second stack, no
allocator, no synchronization hazards.

**First step F-0** is to revert csnobol4 `1d225f8` (session #41's
C-helper landing) back to its parent `b01b47b` (the original 6-cstack
PUSH state).  That gives a clean starting point — we don't want to
build the PDL-extension fix on top of a partial fix that will then
need un-untangling.

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

## SPITBOL reference (port this structure)

Source of truth: `x64/sbl.min` lines 11473–11500 (doc block) and
11978–12039 (`p_fna..p_fnd` implementation).

SPITBOL saves only TWO things on `xs` at FENCE entry:
- `pmhbs` — the pattern history-stack base (analog of PDLHED)
- An indirect `=ndfnb` pointer (the FNC-trap-back link)

No save of MAXLEN, no save of LENFCL beyond what the trap entry
itself carries, no save of name-list state.  CSNOBOL4's 6-item
save list is significantly heavier than necessary even ignoring
the cstack-overwrite issue.

When implementing the PDL-extension fix, **first port SPITBOL's
save list** (PDLHED equivalent + back-link), then add CSNOBOL4-
specific items only if regression tests demand them.  Do not
preserve CSNOBOL4's 6-item save by default — that was always
overkill.

---

## Audit of what genuinely needs cross-RCALL persistence

(Verified session #40, still applies to PDL-extension path.)

| Value | Save needed? | Reasoning |
|-------|--------------|-----------|
| MAXLEN | NO | SCNR reloads from XSP at every scanner entry (v311.sil:3536). Never preserved across pattern recursion. |
| LENFCL | partly | Already in trap-entry slot 3 from FNCA's `PUTDC PDLPTR,3*DESCR,LENFCL`. SALT1 restores it before FNCB dispatch. SALF1 path enters FNCB with LENFCL=0 — verify whether outer-LENFCL recovery matters there. |
| PDLPTR_outer | YES | Currently derived in FNCC via `MOVD PDLPTR,PDLHED` + `DECRA -3*DESCR`. Derivation is correct ONLY when outer PDLPTR == outer PDLHED at FNCA-time. Not safe in general; save it explicitly. |
| PDLHED_outer | YES | FNCA does `MOVD PDLHED,PDLPTR` to set new inner PDLHED. Outer value must be saved. SPITBOL's `pmhbs`. |
| NAMICL_outer | YES | Inner-P pattern primitives (NME/ENME/DNME) write to NAMICL. Outer value needs explicit restore. |
| NHEDCL_outer | YES (probably) | Pre-fix POP restored NHEDCL. Audit said `NHEDCL == NAMICL at FNCA-time`, but for nested FENCE that's only true for the OUTERMOST. Trace evidence inconclusive — save it to be safe; remove later if tests prove redundant. |

**Net save set: 3 to 4 items** (PDLPTR, PDLHED, NAMICL, [NHEDCL]).

---

## Layout — extended FENCE trap entry

Current 3-descriptor layout (PDLPTR points at base; slots 1..3
written above):

```
PDLPTR_pre + 0:    (unused — base; PDLPTR sits here after INCRA -3)
PDLPTR_pre + 1*D:  FNCBCL          (then-or: triggers FNCB on failure)
PDLPTR_pre + 2*D:  cursor (TMVAL)
PDLPTR_pre + 3*D:  LENFCL
```

Proposed N=6 layout (6 descriptors):

```
PDLPTR_pre + 0:    (unused — base)
PDLPTR_pre + 1*D:  FNCBCL
PDLPTR_pre + 2*D:  cursor (TMVAL)
PDLPTR_pre + 3*D:  LENFCL          ; trap-entry slot 3 — SALT1 reads this
PDLPTR_pre + 4*D:  PDLPTR_outer    ; explicit save
PDLPTR_pre + 5*D:  PDLHED_outer    ; explicit save
PDLPTR_pre + 6*D:  NAMICL_outer    ; explicit save
                                   ; (NHEDCL_outer if H1's worry materializes)
```

After FNCA's `INCRA PDLPTR, 6*DESCR`, PDLPTR sits at the base of
the new entry; PDLHED is then assigned that same value.  PDLEND
overflow check applies to the larger size.

**FNCB entry path (failure walker via SALT1→SALT2→PATBRA):**

When inner-P fails, SALT1 reads `LENFCL` from `PDLPTR+3*DESCR`
(works as today — slot 3 unchanged).  SALT2 reads then-or from
`PDLPTR+1*DESCR` (= FNCBCL), reads cursor from slot 2, then
**`DECRA PDLPTR, 3*DESCR`** which moves PDLPTR back by 3
descriptors — but our entry is 6 descriptors deep!

Resolution: FNCB itself does the additional restoration.  After
SALT2's DECRA-3, PDLPTR points 3 slots above the trap-entry base.
The FENCE saves (slots 4, 5, 6 at the base) live at PDLPTR-2*DESCR,
PDLPTR-1*DESCR, and PDLPTR+0*DESCR.  Restore order: read PDLHED
and NAMICL first (they don't change PDLPTR), then read PDLPTR
last (because reading PDLPTR_outer overwrites PDLPTR itself):

```sil
FNCB   XPROC   ,
       GETDC   PDLHED,PDLPTR,(-1)*DESCR  ; slot 5: PDLHED_outer
       GETDC   NAMICL,PDLPTR,0           ; slot 6: NAMICL_outer
       GETDC   PDLPTR,PDLPTR,(-2)*DESCR  ; slot 4: PDLPTR_outer — LAST
       BRANCH  FAIL
```

If genc.sno's GETDC macro doesn't accept negative offsets,
reformulate using a TMP register:
```sil
FNCB   XPROC   ,
       MOVD    TMP,PDLPTR
       DECRA   TMP,2*DESCR              ; TMP now at trap-entry base+1
       GETDC   PDLHED,TMP,DESCR         ; slot 5
       GETDC   NAMICL,TMP,2*DESCR       ; slot 6
       GETDC   PDLPTR,TMP,0             ; slot 4: PDLPTR_outer
       BRANCH  FAIL
```

**FNCC entry path (P matched cleanly):**

P left PDLPTR somewhere ≥ inner-PDLHED.  FNCC needs to restore
outer state and seal the FENCE region.

```sil
FNCC   XPROC   ,
       MOVD    PDLPTR,PDLHED       ; snap PDLPTR back to FNCA-time post-INCRA value
*                                   ; PDLPTR now at base+6
       MOVD    TMP,PDLPTR
       DECRA   TMP,3*DESCR              ; TMP at trap-entry base
       GETDC   LENFCL,TMP,3*DESCR       ; slot 3 (unchanged from current)
       GETDC   PDLHED,TMP,5*DESCR       ; slot 5: PDLHED_outer
       GETDC   NAMICL,TMP,6*DESCR       ; slot 6: NAMICL_outer
       GETDC   PDLPTR,TMP,4*DESCR       ; slot 4: PDLPTR_outer — LAST
       PCOMP   PDLPTR,PDLHED,FNCC1,FNCC1,INTR13
FNCC1  ...    (unchanged from current, but writes seal at slots 1..3 of the NEW INCRA-3 region)
```

**Trap-entry slot overlap with subsequent SCNR pushes** — the
session #41 rejection note's concern.  Walk through: FNCA's
6-wide entry occupies `Po+0 .. Po+6*DESCR`.  After FNCA, PDLPTR
sits at `Po+6*DESCR`; PDLHED also.  Inner-P matching does
`INCRA PDLPTR, 3*DESCR` for SCNR/SCIN3 entries — the next entry
lands at `Po+9*DESCR`, with its slots at `Po+10`, `Po+11`,
`Po+12`.  No overlap with FNCA's region (`Po+1..Po+6`).
The session #41 concern was about Option A (extend to 5
descriptors) where SCNR's slot 1 at `Po+7` would have overlapped
FNCA's hypothetical slot 5 at `Po+7` from a shared base — that
analysis assumed a different layout.  With 6 slots and PDLPTR
ending at `Po+6`, the next push lands at `Po+9` and there is
no overlap.

---

## Active rung — F-0 (revert session #41 C-helper landing)

**Done-when:** csnobol4 working tree matches `b01b47b` (the
emergency-handoff commit BEFORE session #41's partial fix).  Tiny
repro reproduces the ORIGINAL crash signature
(`L_SALT1 PDLPTR.a.i=0xc0`), not the session #41 signature
(`L_SCIN4 ZCL deref`).

**Steps:**
- [ ] `cd /home/claude/csnobol4 && git revert --no-edit 1d225f8`
- [ ] Build: `bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh`
- [ ] Tiny repro: confirm OLD crash signature (`Caught signal 11 in statement 1074`).
- [ ] gdb confirm: `CSN_NO_SEGV_HANDLER=1 gdb --args ... < /tmp/tiny.in` shows L_SALT1 at the crash, NOT L_SCIN4.
- [ ] fence_function/ regression: `cd /home/claude/csnobol4 && make -f Makefile2 test` — confirm 10/10 tests still PASS.
- [ ] Commit revert with message `F-0: revert session #41 C-helper FENCE save migration; baseline restored for PDL-extension fix`.
- [ ] Push.

**No code changes; pure revert.** This step exists to give the
PDL-extension fix (F-1) a clean starting point.

---

## Active rung — F-1 (extend FENCE PDL trap entry to 6 descriptors)

**Done-when:** tiny repro produces beauty's formatted output
(no segfault).  fence_function/ 10/10.  Beauty self-host
N>500 lines.  Smoke=7, Broker=49.

**Steps:**
- [ ] Read SPITBOL `sbl.min:11473–11500` doc block; read `sbl.min:11978–12039` (`p_fna..p_fnd`).
- [ ] Confirm via SPITBOL exactly which values it puts on `xs`.
- [ ] In `v311.sil`: change FNCA's `INCRA PDLPTR, 3*DESCR` to `INCRA PDLPTR, 6*DESCR`.
- [ ] Add three `PUTDC` to FNCA: slots 4=PDLPTR_outer, 5=PDLHED_outer, 6=NAMICL_outer.  These must reference the PRE-INCRA values — capture them in temporary registers before the INCRA.
- [ ] Replace FNCA's 6-cstack PUSH with the new INCRA + 3 PUTDCs.  Drop the cstack PUSH entirely.
- [ ] Rewrite FNCB body per the layout block above (3 GETDCs in dependency order; PDLPTR last; then `BRANCH FAIL`).  Drop the cstack POP.
- [ ] Rewrite FNCC body per the layout block above (MOVD then 4 GETDCs; PDLPTR last; PCOMP unchanged).  Drop the cstack POP.
- [ ] Verify FNCD doesn't need updating — it does `MOVD PDLPTR,PDLHED` + `MOVD NAMICL,NHEDCL` + `BRANCH FAIL`; those should still work since PDLHED is the inner-P's, but verify NHEDCL is what we want post-FENCE-seal.
- [ ] Regenerate: `cd /home/claude/csnobol4 && ./snobol4 -b genc.sno --with BLOCKS v311.sil > snobol4.c2`.
- [ ] Apply the established hand-edit dance for FNCP/FNCA..FNCD (latent SN-26-csn-regen-fix — regen produces L_FNCA: labels but not top-level functions; tsort inlining handles the rest).
- [ ] Build `-O0 -g`: `make -f Makefile2 OPT="-O0 -g" xsnobol4 && cp xsnobol4 snobol4`.
- [ ] Tiny repro: expected to produce beauty output, not segfault.
- [ ] If tiny repro still segfaults: gdb to identify the new signature.  May indicate residual bug in failure walker (independent of FENCE save mechanism) — open F-2.
- [ ] If tiny repro clean: full beauty self-host, expect N>500 lines.
- [ ] If beauty clean: capture md5; record as new csn invariant.
- [ ] Run `make -f Makefile2 test` — confirm fence_function/ 10/10 PLUS no other regressions.
- [ ] Run `bash /home/claude/one4all/scripts/test_smoke_snobol4.sh` (PASS=7) and `test_smoke_unified_broker.sh` (PASS=49).
- [ ] Commit + push.

**Risk:** MEDIUM.  This is the right architectural shape, but the
SIL/genc.sno tooling is fragile (the FNCP/FNCA..FNCD hand-edit
dance is documented as "latent SN-26-csn-regen-fix" precisely
because regen behavior with `--with BLOCKS` is fiddly).  Budget
2 sessions for F-1: one to land + verify tiny repro, one to
debug residuals if any.

---

## Closed sub-rungs

(None yet.)

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
- csnobol4 @ `1d225f8` (session #41 EMERGENCY HANDOFF — to be reverted by F-0)
- one4all @ `78a2a98e`
- corpus @ `7041a14`
- x64 @ `3e519f9`
- active step → **F-0** (revert session #41; restore 6-cstack baseline)

**Gates as of session start:**
- Tiny repro: SEGFAULTS at isnobol4.c:11456 (L_SCIN4 ZCL deref) — session #41 signature.
- After F-0: tiny repro will SEGFAULT at L_SALT1 (PDLPTR=0xc0) — original signature.
- After F-1: tiny repro should produce beauty output cleanly.
- one4all Smoke=7, Broker=49: not affected by csnobol4-only work.
- csnobol4 fence_function/ 10-test suite: PASS=10 currently (verified session #41).
