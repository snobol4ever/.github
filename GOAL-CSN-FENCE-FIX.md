# GOAL-CSN-FENCE-FIX.md — CSNOBOL4 FENCE(P) builtin nested-recursion segfault

**Repo:** csnobol4 (primary), one4all (gates only)
**Done when:** `csnobol4 -bf -P64k -S64k beauty.sno < beauty.sno` produces
N>500 lines of output without segfault and without "Caught signal" diagnostic.
PLUS one4all Smoke=7, Broker=49 preserved.  PLUS the existing 10-test
`test/fence_function/` suite continues to pass.

**Lifted from:** `GOAL-LANG-SNOBOL4.md` SN-26-bridge-coverage-i (sessions
#37–#41).  That sub-rung is now closed in name only: this goal carries
the full diagnostic state forward as its own first-class workstream.

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
# expected (current): "Caught signal 11 in statement 1074 at level 0"
# expected (fixed):   beauty.sno output (lines of formatted SNOBOL4)
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

## Background — what's been ruled out

**The cstack-overwrite (session #38, original SN-26-i bug):** FNCA's
`PUSH (MAXLEN, LENFCL, PDLPTR, PDLHED, NAMICL, NHEDCL)` saved 6 values
to cstack. Under nested FENCE recursion, intermediate `RSTSTK` rewinds
inside SCIN1's tail-call BRANCH chain exposed FNCA's saved cstack slots
to overwrite by unrelated subsequent pushes.  The signature was
`L_SALT1: D(LENFCL) = D(D_A(PDLPTR) + 3*DESCR)` reading from an address
where `PDLPTR.a.i = 0xc0` (= 192 = 12·DESCR sentinel).

This was fixed in session #41 by migrating FNCA/FNCB/FNCC's save/restore
from cstack to a C-level helper stack (`fnc_save_push`/`fnc_save_pop`
in `lib/pat.c`).  The save-list was simultaneously audited down from
6 items to 2 items (PDLHED, NAMICL).  Build clean.  fence_function/
10/10 PASS.  **Old crash signature gone.**

**Why this audit IS sound (verified session #40):**
- MAXLEN: SCNR reloads from XSP at every scanner entry (v311.sil:3536) — never preserved across pattern recursion.
- LENFCL: stored in trap-entry slot 3 by FNCA itself, restored by SALT1 (`GETDC LENFCL,PDLPTR,3*DESCR` v311.sil:3613) before SALT2's PATBRA dispatch to FNCB.
- PDLPTR_outer: derivable from FNCA-time PDLHED via `DECRA PDLPTR, 3*DESCR` (FNCC does `MOVD PDLPTR, PDLHED` then walks back past the trap entry).
- NHEDCL_outer: at FNCA-entry == NAMICL_outer (FNCA does `MOVD NHEDCL, NAMICL`), so saving NAMICL covers both.

---

## The remaining bug — current crash signature

After session #41's migration, the tiny repro and beauty self-host
**still segfault**, but at a different location:

```
SCIN1 () at isnobol4.c:11456
11456    D(PTBRCL) = D(D_A(ZCL));
```

Where `ZCL` was just loaded at line 11437 from `D(D_A(PATBCL) +
D_A(PATICL))`.  At crash time, observed via gdb (CSN_NO_SEGV_HANDLER=1):
- `ZCL = {a={i=0, ptr=0x0}, f=0, v=320}` — NULL descriptor
- `XCL.a.ptr = 0x7eafbecbd660` — valid heap pointer
- `YCL = {a={i=336}, ...}` — small offset
- `PATBCL = {a={i=139293281609616, ptr=0x7eafbe91e790}, ...}` — heap pointer
- `PATICL = {a={i=139293281608656, ptr=0x7eafbe91e3d0}, f=0, v=0}` — **a heap pointer where an offset belongs**

PATICL holds a pointer-sized value but `D_F(PATICL) & FNC` is false
(the FNC flag was lost in the descriptor copy), so SCIN1 falls through
to SCIN3 instead of dispatching via PATBRA.  The wild PATBCL+PATICL
addition reads garbage that maps to a NULL-descriptor-shaped region;
the subsequent `D(D_A(ZCL))` deref at line 11456 segfaults.

---

## Session #41 trace evidence (gathered with FNC_TRACE instrumentation, reverted)

Tiny repro produced this sequence before the crash:

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
| 9 | **FNCB entry** (FNCA #3's fail) | a8e0 | a910 | 0xc0 | 0xc0 | 0 |
| 10| **FNCB AFT** | a8e0 | a3d0 | 0xc0 | 0xc0 | 0 |
| 11| → segfault in failure walker |

After FNCB's `fnc_save_pop`, both PDLPTR and PDLHED match FNCA #3's
pre-state byte-for-byte (rows 5 vs 10).  FENCE arithmetic is correct
on this path.  **The crash happens somewhere AFTER FNCB's BRANCH(FAIL),
in the failure walker re-reading PDL slot 1 at offset PDLPTR+DESCR.**

Crash addresses: PATBCL=0x7eafbe91e790, PATICL=0x7eafbe91e3d0.
PATICL is loaded by SALT2 from PDL slot 1 (`D(XCL) = D(D_A(PDLPTR) +
DESCR)`).  Some subsequent failure cycle reads slot 1 at an address
that contains a heap pointer instead of a then-or offset descriptor.

---

## Working hypotheses (ranked by likelihood — none verified)

### H1 (most likely): NHEDCL save IS needed; audit was wrong on this point

Pre-fix FNCB POP'd 6 items including NHEDCL.  Our patch drops NHEDCL
from the save list on grounds that `NHEDCL_outer == NAMICL_outer at
FNCA-time`.  This is **only true for the outermost FENCE** — for a
nested FENCE, the outer FENCE's FNCA already overwrote NHEDCL with
its own NAMICL value.  When the inner FENCE's FNCA runs, the current
NHEDCL is the OUTER FENCE's NAMICL, not the truly-original NHEDCL.

In the trace, NHEDCL=`0xc0` consistently after FNCA #2's MOVD, so
restoring NAMICL=`0xc0` happens to leave NHEDCL at the correct value
for THIS run.  But there may be paths in beauty.sno where this is not
true — and even when the values match, the **act of re-establishing
the invariant** matters: pre-fix code was self-correcting.

**Test:** add `nhedcl` to `struct fnc_save_frame`, save in push,
restore in pop.  Run tiny repro.  If still crashes, H1 is wrong.

### H2: LENFCL needs explicit FNCB restore

Audit says SALT1 restores LENFCL via `GETDC LENFCL,PDLPTR,3*DESCR`.
But the trace shows `FNCB entry: LENFCL=0` — so we entered FNCB via
**SALF1** (which sets `LENFCL=0`), not SALT1.  SALF1 doesn't reload
LENFCL from the trap entry.  When FNCB exits with LENFCL=0, subsequent
SCIN3 entries see `LENFCL=0` instead of the truly-outer LENFCL.

**Test:** in FNCB, after `fnc_save_pop`, also do
`D(LENFCL) = D(D_A(PDLPTR) + 3*DESCR)` (where PDLPTR is now back
at the outer trap-entry base — so `+3*DESCR` reads the outer trap's
LENFCL slot).  This requires verifying that PDLPTR after FNCB's save_pop
points at a place where `+3*DESCR` is a valid trap-entry slot 3.  In
the trace, FNCB exits with PDLPTR=a8e0 — the slot at `a8e0+3*DESCR=a910`
is FNCC #2's trap slot 3 (LENFCL value).  Hmm — that's not the OUTER
trap's slot 3 either; that's FNCC1's seal entry trap.

**Risk:** this fix could read the wrong LENFCL too.  The pre-fix
6-cstack POP of LENFCL would have restored the ORIGINAL pre-FNCA
LENFCL — there's no PDL slot containing that value once we DECRA past
FNCA's trap entry.

### H3: PDLPTR save IS needed at the SIL level; FNCC's MOVD-then-DECRA derivation is wrong in some paths

Goal-file's session #41 entry already flagged this: "I assumed FNCC's
pre-FNCA PDLPTR equals `inner-PDLHED - 3*DESCR` — but if the outer
pattern's PDLPTR was already at a different position (e.g. after its
own SCNR traps), the pre-FNCA PDLPTR_outer may have been higher than
what `inner-PDLHED - 3*DESCR` yields."

Trace contradicts H3 for THIS run (rows 5 vs 8 vs 10 all match the
DECRA derivation).  But beauty.sno may have other paths that don't.

**Test:** add `pdlptr` to `struct fnc_save_frame`; save real outer
PDLPTR in push; in FNCC, replace `MOVD PDLPTR,PDLHED` + `DECRA -3` with
just `fnc_save_pop` reading PDLPTR directly.  Same for FNCB.  Run tiny
repro.

### H4: It's not in FNC* at all; the failure walker has its own bug

The post-FNCB failure walker is reading slot 1 of a PDL entry that
contains a heap-pointer-shaped descriptor.  That descriptor was
written by SOMETHING — possibly an inner-P primitive (NME, ENME, ATP,
SCNR, etc.) that pushed a trap and never popped it because FENCE's
unwinding skipped past it.  This would make the bug a **PDL leak**:
inner-P matched, FNCC fired, but inner-P's intermediate traps didn't
unwind properly because FNCC's `MOVD PDLPTR,PDLHED` discarded them
without running their failure handlers.

This is actually how FENCE is *supposed* to work — FENCE truncates
all of inner-P's history.  But maybe one of those discarded entries
was supposed to leave a side-effect that the outer scope depends on,
and the corruption manifests later when the failure walker walks
back across the discontinuity.

**Test:** instrument SALT2 to print every slot 1 read; identify the
exact memory address of the bad descriptor; backtrack to who wrote it.

### H5: NAMICL/name-list consistency

If inner-P wrote name-list entries that reference offsets within a
NAMICL region that NMD-handlers later read, and FENCE-discards leave
those entries dangling, name-list traversal could segfault.  The fact
that the corrupt PATICL value is heap-pointer-shaped (`0x7e...`) is
suspicious — that range is where NAMICL data lives in the trace.

---

## Suggested attack plan

1. **Try H1 first** — cheapest test (one-line addition to
   `struct fnc_save_frame`, two-line additions in push/pop).  If
   tiny repro clears, run beauty self-host; if that clears, run gates.

2. If H1 fails, **try H3** — also cheap, mostly mechanical.  Pre-fix
   code worked structurally (modulo cstack-overwrite); restoring
   the full SIL-level save list via C helpers is the most conservative
   path that's still safe under nested FENCE.

3. If H1+H3 still fail, **escalate to H4 instrumentation**: add a
   write-tracking helper to PDL slot writes; on crash, identify the
   originating writer.  This is the heavyweight path but gives ground
   truth.

4. Throughout: SPITBOL `sbl.min` lines 11978–12039 (`p_fna..p_fnd`)
   and the doc block at 11473–11500 are the reference implementation.
   SPITBOL saves only `pmhbs` + an `=ndfnb` indirect on `xs`.  When
   in doubt, port SPITBOL's structure rather than continuing to
   rationalize CSNOBOL4's 6-item save.

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

GOAL-LANG-SNOBOL4 sub-rung SN-26-bridge-coverage-h (3-way harness
on beauty.sno) is blocked on this fix.  Workarounds:
- Run 2-way SCRIP-vs-SPITBOL harness (no csn) — see GOAL-LANG-SNOBOL4
  SN-26-bridge-coverage-h variant.
- Run beauty self-host on SPITBOL alone — already produces 646 lines
  of canonical output (md5 abfd19a7a834484a96e824851caee159).

---

## Files of interest

| File | Role |
|------|------|
| csnobol4/v311.sil:4093-4156 | FNCA/FNCB/FNCC/FNCD SIL source |
| csnobol4/lib/pat.c:127-184 | C save-helpers (post session #41) |
| csnobol4/isnobol4.c:12258-12299 | generated FNCA/B/C/D label code |
| csnobol4/snobol4.c (same range) | generated FNCA/B/C/D label code |
| csnobol4/genc.sno | SIL → C generator (regen tool) |
| csnobol4/test/fence_function/ | 10-test regression suite |
| corpus/programs/snobol4/demo/beauty/beauty.sno | self-host target |
| sbl.min:11978-12039 | SPITBOL p_fna..p_fnd reference |
| sbl.min:11473-11500 | SPITBOL FENCE doc block |

---

## Closed sub-rungs

(None yet — this goal opens fresh as of 2026-04-27.)

---

## Active rung — F-1 (test H1: add NHEDCL to save frame)

**Done-when:** tiny repro produces beauty's formatted output (no
"Caught signal 11").  If passes, escalate to F-2 (full beauty
self-host); if fails, advance to F-3 (test H3).

**Steps:**
- [ ] Build `-O0 -g` baseline; reconfirm tiny repro segfaults.
- [ ] Add `struct descr nhedcl;` to `struct fnc_save_frame` in `lib/pat.c`.
- [ ] In `fnc_save_push`: save `res.nhedcl[0]`.
- [ ] In `fnc_save_pop`: restore `res.nhedcl[0]`.
- [ ] Rebuild; run tiny repro.
- [ ] If clean: run beauty self-host (`< beauty.sno`); confirm N>500 lines.
- [ ] If clean: run fence_function/ regression suite; confirm 10/10.
- [ ] If clean: commit.

---

## Closed-rung pointers

- `git log --grep "SN-26-bridge-coverage-i" --oneline` (csnobol4 + .github)
- `git log --grep "GOAL-CSN-FENCE-FIX" --oneline` (this goal once landed)

---

## Current state

**HEADs:**
- csnobol4 @ `1d225f8` (session #41 EMERGENCY HANDOFF — partial fix landed, bug not closed)
- one4all @ `78a2a98e`
- corpus @ `7041a14`
- x64 @ `3e519f9`
- active step → F-1 (H1 hypothesis test)

**Gates as of session start:**
- Tiny repro: SEGFAULTS at isnobol4.c:11456 (L_SCIN4 ZCL deref).
- Beauty self-host: SEGFAULTS at beauty.sno:616 statement 1074.
- one4all Smoke=7, Broker=49: not re-run this session (no one4all change).
- csnobol4 fence_function/ 10-test suite: PASS=10 (confirmed session #41).
