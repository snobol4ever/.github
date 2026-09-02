# FINDING 2026-09-02 seat14 — `list_directive_2`'s post-crash-fix wrong answer is PZ-4 territory, not a smaller bug

**Tree:** SCRIP `d9e4ac2a1` · corpus `7ecfdd20c` (both pristine, `RT_OPT=-O0`) · oracle `swipl` · measured
2026-09-02, seat14, mode FLEET-16. Row `prolog-plw-unify-cells-var-nonvar-trail-smash`.

## Recap: why this needed a fresh look

Seat10's independent fix (SCRIP `72c7ec09f`, `dop_call_nothrow` arms its own dead-cstack floor) cured the
stack-smash SIGABRT this row's DONE-WHEN witness (`list_directive_2` = `rung05_backtrack_backtrack`:
`member(X,[X|_]).  member(X,[_|T]):-member(X,T).  main :- member(X,[a,b,c]),write(X),nl,fail ; true.`) used
to hit. Seat04 (2026-09-02) confirmed the crash is gone but the witness now prints `a`, `b`, then `_G0`
forever (rc never returned — timeout, not a clean rc) instead of `a`/`b`/`c`, and flagged this as "a
genuinely different, and probably more tractable, debugging target." **I measured that hope directly and it
does not hold: the new symptom is the same activation-frame-lifetime class PZ-4 already owns, reached
through a different door.**

## The mechanism, watched live (not inferred)

`plc_dead_cstack()` (`src/parsers/prolog/pl_cell.h:64`) is what seat10's fix newly arms. `pl_trail_unwind()`
(`:81-90`) calls it once per trail entry being undone; when it returns true, the entry's restore is
**skipped** — `*ents[t->top].addr = ents[t->top].old` never executes — specifically to avoid writing through
a stale C-stack address seat10's own FINDING already proved gets reused (that reuse is the whole reason the
SIGABRT existed).

gdb trace (`break pl_cell.h:88`, condition-evaluated `plc_dead_cstack(ents[t->top].addr)` in-frame, full
script in this FINDING's receipts) on the unfixed witness, breaking down the **one** `dop_unwind_nothrow`
call that unwinds back to `mark=2` right after `b` prints:

| top (post-decrement) | addr | `old` (the value that would be restored) | `cur` (what's actually there now) | skipped? |
|---|---|---|---|---|
| 7 | `0x7fffffff8be0` | `v=0x00(DT_SNUL) slen=0 i=0` — an unbound cell | `v=0x50(DT_PLREF) slen=3 i=-2475851428855655168` — **a live, validly-tagged compound-term reference** | ✅ skipped |
| 6 | (not dead) | — | — | restored normally |
| 5 | `0x7fffffff8bc0` | `v=0x00(DT_SNUL) slen=0 i=0` — an unbound cell | `v=0xA0 slen=1 i=0` — **not a valid `DTYPE_t` at all** (max defined tag is `DT_DATA=0x70`) | ✅ skipped |

Two separate, unambiguous confirmations that `plc_dead_cstack` is judging correctly, not falsely: entry 7's
address currently holds a **live, correctly-tagged `DT_PLREF` cell** — restoring `old` there would silently
corrupt an unrelated, currently-in-use compound term, a worse outcome than the wrong answer we get instead.
Entry 5's address holds an out-of-range tag — plain reused-stack garbage. **This is not a bug in the dead
check.** `DT_SNUL=0x00` is what a zeroed/never-explicitly-tagged cell reads as, and `pl_cell_unbound()`
(`pl_cell.h:37`) already treats `DT_SNUL` as equivalent to `DT_PLVAR` — so `old` here is a completely ordinary
"this was an unbound variable" trail entry, nothing anomalous about the push.

## Why skipping the restore produces runaway recursion, not just a wrong value

Continuing the trace past this unwind: each subsequent "round" (one more `dop_call_nothrow`/`dop_unwind_nothrow`
entry, identifiable by a fresh, lower `g_plw_unwind_floor`) has **more trail entries to walk than the round
before it** (7, then 8, then 16, then 26, then 36+ before I capped the script), and the floor drops by a
roughly constant amount each round — the signature of genuine, unbounded **C-stack recursion**, not a tight
retry loop at fixed depth. `_G0` (an unbound variable's default print form) prints once per round: `write/1`
is reading a cell that was supposed to be re-bound to the next list element but is instead reading back
unbound, because the earlier skip left it that way, and whatever re-enters the retry never supplies a fresh
binding either — so it retries again, one C-frame deeper, forever. I did not chase the exact call site that
recurses (that's inside the `member/2`-recursion retry path already implicated by every earlier pass on this
row and on `prolog-backtracking-yields-first-solution-only`) — the floor/skip evidence above is sufficient to
place the defect class without it.

## The conclusion this changes

**The cell that entry 7/5 needed to reset lives in a C-stack frame that no longer exists by the time the
unwind reaches it** — precisely RULES.md's BB FRAME-PLACEMENT CRITERION: *"the determining factor... is the
UNBOUNDED stack growth between the time a box leaves at GAMMA and is resumed at BETA... [or] any time
UNBOUNDED growth prevents an OPERAND from being loaded by its OPERATOR with a fixed offset."* `member/2`'s
own recursion is exactly that unbounded growth, and the choice-point-local variable is exactly the operand
that can no longer be reached. That criterion's remedy is **promotion to a ζ-ACTIVATION-FRAME (RBP)** — the
one thing `prolog-plw-floor-bypass-safety-unproven`/`dop_call_nothrow`'s C-stack heuristic *cannot* supply,
because there is no live memory left to redirect the write to, only a judgment call about whether to corrupt
something else instead. **This is `prolog-pz4-gamma-retain-activation-frames` territory (hq_C), the same
prerequisite `prolog-member-2-redo-smashes-stack-canary` (C34), `prolog-forall-wrong-answer-rung57` (C7), and
three more `PARKED-AWAITING` rows on Ladder C already name** — not a smaller, independent bug as hoped.
`member/2`'s own recursive structure is what both this row and C34 have in common; this FINDING is evidence
they may be the *same* mechanism seen from the crash side (C34) and the post-crash-fix wrong-answer side
(this row), not just siblings — worth hq_C checking when PZ-4 lands, not re-deriving.

## Not fixed here, and why

Nothing in `plc_dead_cstack`/`pl_trail_unwind`/`dop_call_nothrow` is safe to change to chase this: the skip
is demonstrably *correct* on both witnessed entries (one would have corrupted a live compound term), so
loosening it re-opens the SIGABRT class seat10 just closed for 4 entries; there is no local, narrow fix
available in this leaf. The real fix is PZ-4's own activation-frame promotion, not mine to attempt (hq_C's
claimed row, real stakes, shared with the same `bb_call_proc_staged.cpp`-adjacent territory every other
investigator on this family has already declined to rush).

## Receipts

gdb scripts and full unbounded-round capture (80 dead-checks before I stopped it) available on request /
reproducible via: `break pl_cell.h:88`, conditional-print `plc_dead_cstack(ents[t->top].addr)` plus
`ents[t->top].{addr,old}` and `ents[t->top].addr` dereferenced (the "current" column), against
`./scrip corpus/tests/prolog/ALL.pl`'s `list_directive_2` entry (extract via
`corpus_suite_harness.py extract`). Witness command:
```
python3 scripts/corpus_suite_harness.py extract corpus/tests/prolog/ALL.pl corpus/tests/prolog/ALL.ref list_directive_2 /tmp/w.pl
./scrip /tmp/w.pl </dev/null   # a, b, then _G0 forever (no natural termination — kill with timeout)
```
