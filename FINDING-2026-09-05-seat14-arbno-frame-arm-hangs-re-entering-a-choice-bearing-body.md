# FINDING 2026-09-05 seat14 — `ARBNO-FRAME` arm hangs re-entering a body with internal choice

**Seat:** seat14 · **Row:** `snobol4-deferred-arbno-reentry-hangs-arbno-pos-rpos-branch-81` · **Mode:** FLEET-20 (hq_T lane)
**Trees graded:** SCRIP `674319235` · corpus `4e11cb9ee` · .github `3ed2c636`
**Build:** incremental `make`, `RT_OPT=-O0` (buildinfo). Box clock 2026-09-05 ~13:45–14:00 CDT.

## 1. The defect, in one sentence

`bb_match_arbno_frame` (`src/templates/bb/bb_match_arbno.cpp:92-119`) **hangs — a genuine non-terminating
loop, not a slow search — whenever ARBNO's body has internal choice (an alternation) and is re-entered**,
regardless of whether the eventual overall answer would be MATCH or NOMATCH, and regardless of whether the
alternation's second arm is ever actually reachable.

⛔ **Not the same bug as this morning's `f3baca595`** (ARBNO null-body-guard recedes to body ENTRY not TAIL,
this file, this function, landed by hq_T 11:17 CDT today). That fix concerns a body that is a **chain**
(multiple boxes). Every witness below has a body that is a **single** box (one alternation, no chain) —
`sn4_arbno_tailbeta()`'s PAIR(4)-vs-PAIR(1) distinction that fix turns on does not distinguish these
witnesses at all (§3 rules this out directly, measured, not assumed).

## 2. Isolation — 8 minimal witnesses, one variable at a time

All run `timeout 5`/`8`/`30` under `./scrip --run`, mode-3 default. PASS/FAIL below means SCRIP terminated
and printed the correct branch (verified against hand-worked expected SNOBOL4 semantics); HANG means
`timeout` killed it (rc=124) with **zero bytes of output** and CPU pegged 66-94%, RSS flat ~10MB (not a
memory blow-up, not I/O-blocked — actively spinning).

```
v1  G1=ARBNO('a')          'aab' + RPOS(0)   exhausts to FAIL, no alternation anywhere    TERMINATES (nomatch)
v3  G1=ARBNO('a'|'ab')     'zzz' + RPOS(0)   alternation present but body NEVER attempted  TERMINATES (nomatch)
v2  G1=ARBNO('a'|'ab')     'aab' + RPOS(0)   MUST retry alternation's 2nd arm to SUCCEED    HANGS
v4  G1=ARBNO('a'|'ab')     'abc' + RPOS(0)   MUST retry alternation, then still FAILS       HANGS
v5  G1=ARBNO('a'|'ab')     'abcdef' + 'Q'    same as v2/v4 but plain trailing literal,      HANGS
                                              not RPOS -- rules out RPOS as an ingredient
v6  G1=ARBNO('a'|'ZZZ')    'aab' + 'Q'       2nd alt arm NEVER reachable (always fails) --  HANGS
                                              re-entry only ever needs to reduce rep count,
                                              exactly like v1, EXCEPT the body is syntactically
                                              an alternation -- rules out "actually choosing
                                              the 2nd arm" as an ingredient
v7  P=('a'|'ab') RPOS(0)   'ab'  (NO ARBNO)  plain alternation re-entry, no wrapping ARBNO   TERMINATES (match)
v8  P=('a'|'ab') 'Q'       'abc' (NO ARBNO)  plain alternation re-entry to exhaustion,       TERMINATES (nomatch)
                                              no ARBNO
```

**The isolation is exact:** `ARBNO(<body>)` re-entry hangs **iff** `<body>` is syntactically an alternation —
independent of whether the run would succeed (v2) or fail (v4/v5/v6), independent of whether the second arm
is reachable (v6), independent of whether the forcing continuation is `RPOS` or a plain literal (v5). Plain
alternation re-entry with no ARBNO involved (v7, v8) is correct. Plain ARBNO re-entry with a non-choice body
(v1) is correct. It is specifically the **composition**.

Real corpus witness (`arbno_pos_rpos_branch_81`, extracted via `corpus_suite_harness.py extract`) reproduces
identically: `'abcdef' POS(0) *(ARBNO('a'|'ab') RPOS(0))`, expected `nomatch`. Confirmed non-terminating at
two different bounds, not merely slow: **8s** (rc=124, 94% CPU, RSS 10160KB) and **30s** (rc=124, 66% CPU,
RSS 10184KB, i.e. flat) — ruling out "needs 21s" per this row's own FIRST STEP guard.

## 3. Arm identified, one hypothesis ruled out by direct measurement

`SCRIP_ARBNO_DIAG=1` (the codebase's own arm-choice diagnostic) on the minimal witnesses:

```
v1 (passes):  [ARBNO-ARM] FRAMELESS         (k0=1, sq=1)
v6 (hangs):   [ARBNO-ARM] ARBNO-FRAME       (k0=1, sq=0)
```

So the defect is confined to `bb_match_arbno_frame()` (the FRAMELESS arm, used for a choice-free body, is
unaffected). Trace of *why* ARBNO-FRAME is selected: `emit.cpp:1180` sets
`op_arbno_body_defer_unsafe = _du || arbno_reentry_hazard(nd)`; for a bare 2-arm alternation body
(`_alt=1,_dfr=0,_arb=0,_altnest=0,_du=0`), `arbno_reentry_hazard(nd)` must be returning true (ARBNO-FRAME is
in fact selected), i.e. **the code already knows this body shape needs special re-entry handling** — the
ARBNO-FRAME arm is the mechanism built for exactly this case, and it is the one that is broken.

⛔ **Ruled out by direct test, not assumed:** the obvious next hypothesis, given this file's fresh history,
is that this is the *same family* as this morning's entry/tail confusion (`sn4_arbno_tailbeta()` choosing
`PAIR(1)` — body ENTRY — where `PAIR(4)` — body TAIL — is needed, or vice versa). Forcing
`SCRIP_ARBNO_TAILBETA=0` (default is **on**, `emit.cpp:2374-2376`, a bare env-flag with no structural check
for whether the body is actually a multi-node chain) changes nothing:

```
SCRIP_ARBNO_TAILBETA=0  v2  -> still HANGS (rc=124)
SCRIP_ARBNO_TAILBETA=0  v6  -> still HANGS (rc=124)
SCRIP_ARBNO_TAILBETA=0  real witness -> still HANGS (rc=124)
SCRIP_ARBNO_TAILBETA=0  v1 (control) -> still TERMINATES (nomatch), no regression
```

PAIR(1) and PAIR(4) are — for these single-node bodies — either equally wrong or equally irrelevant to the
actual defect. **This is not the entry-vs-tail bug; it is something else in the same function**, most likely
in the PEND-MARK / `AFCQ(8)` r12-rollback bookkeeping (`bb_match_arbno.cpp:98-119`) or in how the
alternation's own choice-record survives being re-entered from inside that bookkeeping — `bb_match_alternate`
(`bb_match_alternate.cpp`) keeps its "which arm am I on" state either in an own-carved 32-byte rsp record or
an rbp-relative slot handed out by `sn4_choice_rbp_off_nd()` / `choice_frame_slot()` (`emit.cpp:2449-2458`);
I did not instrument which of the two this witness gets or watch that memory across iterations — that is the
next concrete step, and it is a `src/emitter` + `src/templates/bb` question together, both already inside
this row's own SCOPE exclusion.

**Confirmed tight cycle, not slow search:** two fully independent process launches (separate PIDs), each
interrupted under gdb at an arbitrary wall-clock offset (~2-3s in), land on the byte-identical instruction
address both times (`rip=0x7fffe9c00154`, a `jmp *rax` through an rbp-relative frame slot, consistent with
the ARBNO-FRAME arm's own port-jump shape). A 6-char subject with a 2-way alternation has a state space of a
handful of combinations (v7/v8, the no-ARBNO siblings, resolve in <0.03s) — this is not combinatorial
blow-up, it is a cycle.

## 4. Why this stays open, not fixed

This row's own SCOPE names `src/templates/bb`, `src/emitter` (among others) as shared-node classes: **stop
and route to hq_U rather than land it here.** §3 confirms the candidate mechanism sits in exactly those two
directories (`bb_match_arbno.cpp`'s re-entry bookkeeping, `emit.cpp`'s choice-record slot assignment) — this
is that case. Sent to hq_U with this document attached (see LEDGER); hq_T (row owner) notified in parallel.

## 5. DONE-WHEN

Row's own DONE-WHEN (extract `arbno_pos_rpos_branch_81`, run under a 20s bound, diff against ref): **still
RED** — confirmed non-terminating at 30s, no output. Stays open until hq_U's cure lands; re-run this row's
DONE-WHEN verbatim once one does, no re-diagnosis needed.
