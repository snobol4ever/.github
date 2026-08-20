# FINDING-2026-08-16-s120-arbno-stored-no-resume.md

**Session s120 (Claude Opus 5). SCRIP `aa1a3901`, corpus `330c0d32`. Both LOCAL AND UNPUSHED — credential asked in-chat twice, not yet supplied.**

---

## 1. MILESTONE 1 ORACLE HALF SURVIVED — DO NOT RE-DERIVE IT

s119's cursor says its M1 earn was "LOCAL AND UNPUSHED", and indeed corpus `b5bc9175` does
**not** exist on origin. **The work was not lost.** Re-measured first thing this session on a
fresh clone:

    sbl -bf beauty.sno < beauty.sno   →  rc=0, 622 lines, BYTE-IDENTICAL to beauty.sno

The GenTab fix that earned it (`fcb8724e`) *was* pushed; `b5bc9175` carried nothing
load-bearing. **The oracle half of Milestone 1 is intact at HEAD.** Verify with the command
above rather than re-doing s119's hunt.

## 2. MON-CAP: THE MONITOR SEGV IS `SCRIP_SLIM_PAIR`, AND IT IS CURABLE TODAY

Confirmed a third time by independent measurement, then **localized and cured**:

- `MONITOR_BIN=1` SEGVs on **any user-function call**. 4-line repro: `DEFINE('F(X)')` +
  one call. DEFINE alone is innocent (rc=0); RETURN vs FRETURN and whether the result is
  assigned make no difference. Baseline without the monitor is rc=0 for all.
- gdb fingerprint: **r10=r11=0** (unseated γ/ω wires), RIP in `.fini_array`
  (`__do_global_dtors_aux_fini_array_entry`), frame #1 = `0x0000000100000002`, a descriptor
  tagword walked as a return address. Reached via `rt_outer_call`.
- **Mechanism (not theory — read from the source):** `MONITOR_BIN` forces `n_gva_m3=0`
  (`src/driver/scrip.c:1574` and `:1722`). GVA-off makes both the SCC gate and the role-4
  TINY shim refuse, so every call falls to the **legacy flat-glue arm**
  (`bb_call_proc_staged.cpp:742`, twin at `:463`). That arm pushes the γ/ω pair **only**
  under `SCRIP_SLIM_PAIR`; without it the site pushes nothing and `:(RETURN)` pops
  enclosing-frame bytes. The template's own comment says exactly this.
- **`SCRIP_SLIM_PAIR=1` cures it.** All five call repros go rc=139 → rc=0 with correct
  output. beauty under the monitor goes **rc=139 → rc=1**.
- **It is INERT at default:** `SCRIP_SLIM_PAIR=1` alone on beauty (monitor dark) is
  byte-identical to baseline — rc=0, 10 lines. Expected, since the arm is only reachable
  with GVA off.

**Still open under the monitor:** beauty then hits `** Error 22 in statement 0 / Undefined
function called`. Not chased. It is NOT the includes — all 16 `.inc` files load clean under
`MONITOR_BIN=1 SCRIP_SLIM_PAIR=1`, and DEFINE-with-locals, `-INCLUDE`'d DEFINEs, and nested
calls are all green under the monitor.

**Lon's ruling on the `SCRIP_SLIM_PAIR` default is still owed.** Grant received in-chat s120
("All your choices. I'm with you on this."), but the measurement above argues for
default-ON with an inverted killswitch, in the s118 `SCRIP_BYNAME_ALPHA` shape. Not landed
this session — the session spent its remaining budget on the M1 blocker below.

## 3. ⭐⭐⭐ THE M1 `Parse Error` IS LOCALIZED — AND THE DEFERRED-EVALUATION STORY IS FALSIFIED

**A variable-held `ARB`/`ARBNO` never backtracks.** Inline works; stored does not.

Sessions s117–s119 pursued this as a deferred-evaluation (`*`) defect because beauty's shape
is `ARBNO(*Command)`. **The `*` is not the discriminator.** `probe/arbnostore/arbno_stored_red.sno`
contains no `*` anywhere — its ARBNO argument is the literal `'a'` — and fails identically.
Removing the `*` changes nothing; removing the **variable store** changes everything.

| pattern | inline in match | stored in a variable |
|---|---|---|
| `ARBNO('a')` under `POS(0) … RPOS(0)` | PASS | **FAIL** |
| `ARB` under `POS(0) … RPOS(0)` | PASS | **FAIL** |
| `SPAN('a')`, `LEN(1)`, `'a' | 'b'` | PASS | PASS |

Deterministic patterns survive storage; the two needing a **resumable choice point** do not.
Both `POS(0)` and `RPOS(0)` anchors are load-bearing — a probe missing either is green and
proves nothing. m3 ≡ m4 on all seven probes, so the defect is in the shared LOWER/EMITTER path.

**Mechanism, read from `--dump-ir`:**

    STORED (red)                          INLINE (green)
    main: 3  CALL "SNO$MKPAT"             main: 5  MATCH_ARBNO
         13  MATCH_POS   ω=12                   6  MATCH_RPOS  ω=5   ← back INTO the ARBNO
         15  MATCH_RPOS  ω=12  ⛔
    PAT$0: 0 MATCH_ARBNO γ=1@ SUCCEED
                          ω=2@ FAIL   ⛔ both terminal

The stored pattern is lowered into a **`PAT$0` thunk whose `MATCH_ARBNO` terminates in a
closed SUCCEED/FAIL pair with no resumable entry.** The outer `MATCH_RPOS`'s ω therefore
points at `MATCH_BEGIN` — restarting the whole match — instead of back into the ARBNO to ask
for a longer alternative. ARBNO takes its shy null match (manual p.121: ARBNO is shy, matches
null initially, and is retried when a subsequent component fails) and is never retried.

That is beauty: `Parse = … ARBNO(*Command) …` (`:225`) matched under `POS(0) *Parse *Space
RPOS(0)` (`:608`) → fails → `:F(mainErr1)` → prints `Parse Error`, rc=0, 10 lines of 622.

This does **not** void `probe/defval/`'s SIGSEGV class (bare `C = *D` as a whole pattern
value, 4 RED there). That is real and distinct. It is simply not what makes beauty print
`Parse Error` — beauty exits rc=0 and never crashes.

## 4. LANDED: THE STALE ARBNO EXCLUSION IS DELETED (SCRIP `aa1a3901`)

`sno_pat_inline_ok` (the PAT-INLINE shape gate) excluded ARBNO, justified as *"any second
iteration SEGVs (witness `'aa' POS(0) ARBNO('a') RPOS(0)`; z4_arbno rc=139)"*. **Both named
witnesses were re-measured PASSING at HEAD before the edit:** the tmin witness MATCHes in m3
(and iterates correctly to 9), and `z4_arbno` completes its 150,000-iteration backtrack ladder
at `arbno 150000` == oracle ref. The statement-ARBNO rung landed; nobody deleted the gate,
per its own documented deletion condition.

GATES: crosscheck_snobol4 **m3 298/19, m4 297/19/1, DIVERGE 0 — before AND after, zero
movers, identical FAIL list**. `arbno_stored_red` FAIL → PASS. Killswitch
`SCRIP_PAT_INLINE_ARBNO=0` restores the exclusion (verified NOMATCH).

**SCOPE, STATED HONESTLY: this does not move beauty.** It fixes the non-deferred stored-ARBNO
class only.

## 5. ⛔ FALSIFIED THIS SESSION — DO NOT REDO

- **PAT-INLINE IS A STRUCTURAL DEAD END FOR beauty.** `Parse = nPush() ARBNO(*Command)
  ("'Parse'" & 'nTop()') nPop()` contains build-time **function calls**, and
  `sno_pat_invariant` (`lower_snobol4.c:986-996`) has no `TT_FNC` case → returns 0. `Parse`
  can therefore never enter the fz table, so the inline path at `:1392` is never consulted
  for it **no matter how the shape gate is widened**. Do not spend another seat widening
  `sno_pat_inline_ok` hoping to reach beauty.
- **Widening `sno_pat_invariant` to admit `TT_DEFER` REGRESSES.** Built behind
  `SCRIP_PAT_INVARIANT_DEFER`, measured, reverted clean. It *does* fix the deferred probe
  (`arbno_stored_defer_red` → MATCH), but crosscheck goes **298/19 → 294/23 (m3)** and
  **297/19 → 293/23 (m4)**. The predicate also feeds the PT-2 dead-store consumers
  (`sno_fz_is_dead_build` / `sno_fz_procname_is_dead` / `sno_fz_mark_defer`); widening the fz
  table has blast radius well beyond the inline path. Beauty stayed `Parse Error` with the
  knob on regardless — see the dead-end above.
- **Admitting `TT_DEFER` as ARBNO's direct argument in `sno_pat_inline_ok` is INERT alone** —
  it never fires, because `sno_pat_invariant` rejects the shape upstream first. Reverted.

## 6. ⭐ NEXT RUNG — THE REAL ONE

**Give the `PAT$` blob's `MATCH_ARBNO` a resumable entry**, so an outer `MATCH_RPOS` failure
routes back into the stored ARBNO instead of to `MATCH_BEGIN`. This is R-5's "backtrack β per
choice class" re-entry edge, exercised through a stored pattern value. It is the only route
that reaches beauty, because §5 rules the inline route out structurally.

Start from the two IR dumps in §3 — they name the exact wires that must change. The witness
set is `corpus/probe/arbnostore/` (2 remaining RED: `arb_stored_red`,
`arbno_stored_defer_red`) plus the seven crosscheck `*_arbno_defer_*` failures
(`165_pat_arbno_defer_var_body`, `180_pat_arbno_defer_nonrecursive`,
`181_pat_arbno_defer_tail_stressors`, `183_pat_arbno_defer_recursive_carry`, `141`, `145`,
`151`), which are all this one class and should move together.

Run the hunt with the monitor now that §2 makes it usable:
`MONITOR_BIN=1 SCRIP_SLIM_PAIR=1 PARTICIPANTS="spl scr" bash scripts/test_monitor_2way_spitbol_vs_run.sh <probe>`
(`STDIN_SRC=<file>` feeds stdin; beauty needs `STDIN_SRC=beauty.sno`).
