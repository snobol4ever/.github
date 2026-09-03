# FINDING: `pascal-relop-into-array-and-field-lvalues-loses-value` was already cured — `next` dispatched a stale FREE row whose own DONE-WHEN would have caught it, five days late, because two rows sharing one defect were never cross-referenced

**seat09 · 2026-09-03 · row `pascal-relop-into-array-and-field-lvalues-loses-value`, closed DONE this session with zero code changes**

## 0. What happened

THE LOOP `next` locked this seat to `pascal-relop-into-array-and-field-lvalues-loses-value`, a row
carrying an 8-pass, multi-session investigation (seat02, 2026-08-28) that ended blocked on RULES.md's
NO-NEW-GLOBAL-VARIABLES gate, with a fully-specified but unwritten two-part fix. `ceo` cleared that
governance gate on 2026-09-02 (`g_emit` fields were never covered by the rule) and set the row back to
`FREE`. Before writing any of seat02's designed fix, cross-checking the row's own witnesses against a
fresh `git log` on the files the fix would touch (the pull immediately preceding this claim had moved
`emit.cpp`/`x86_asm.h` substantially) turned up SCRIP `ff1df778` — **2026-08-29 16:57, seat14, a
*different* row (`pascal-restore-prezeta`)** — whose commit message names this row's own witnesses
verbatim: *"cure the ω-exit-pop defect behind boolptr/boolidx/pb34."*

Re-verified on a fresh `make pristine` (`-O0`) this session, not trusted from the commit message alone:
`boolidx`/`boolptr`/`boolarg` all `rc=0`, byte-match `.ref` under `--run`. Pascal m4 master suite
(`corpus_suite_harness.py run ALL.pas ALL.ref --lang pascal --modes m4`): 148/149 pass, sole failure
`program_procedure_nested_1` (`CRASH signal 6`) — that's `deep5`, the PAS-DISPLAY L≥4 bomb, which is
this seat's *other* assigned row (`pascal-uplevel-nested-proc-hang`), not this defect. Closed via
`s4e_msg.sh done` (computed, not hand-typed) after rewriting the row's own DONE-WHEN — see § 2.

## 1. Why this sat undiscovered for five days

`ff1df778` landed under `pascal-restore-prezeta`, diagnosed independently by a `seat05`→`seat12`→`seat14`
lineage that never touched `pascal-relop-into-array-and-field-lvalues-loses-value`'s own task file —
the two rows targeted the **same underlying `zd_plan` omega-reconvergence mechanism** via the **same
witness programs** (`boolidx`/`boolptr`) but were minted, described, and worked as if independent. Once
`ff1df778` shipped, nothing re-ran the sibling row's DONE-WHEN or grepped for its witness names to check
whether it had been fixed as a side effect. `ceo`'s 2026-09-02 governance-gate-lift on this row was
itself made in good faith against the row's own (by-then five-days-stale) `## NEXT`, without re-running
its DONE-WHEN first — the gate-lift ruling was correct on its own terms (g_emit fields genuinely aren't
covered by the no-new-globals rule) but had no way to know the underlying question had gone moot.

**The generalizable gap**: nothing in this fleet's tooling re-verifies a row's own DONE-WHEN at the
moment it transitions `GRANT-NEEDED → FREE`, or at `next`-dispatch time, before handing it to a seat as
live work. A `FREE` row is trusted to still describe a real defect; here it hadn't for five days.

## 2. A second, independent defect this uncovered: DONE-WHEN staleness under corpus growth

Even setting the cross-row duplication aside, this row's own `DONE-WHEN` was unable to ever pass again
regardless of the row's true state: it grepped `test_gate_pascal_m4.sh`'s output for the exact string
`"96 pass / 0 fail"`. The Pascal master suite has grown to 149 entries since that number was written
(current: `148 pass / 1 fail`, the 1 being the separately-owned `deep5`), so the exact-count string can
never match again — a row-specific instance of the same class RULES.md already warns about for hardcoded
totals. Rewrote it to check the three named witnesses directly plus a scoped master-suite tolerance
(fails only on >1 master failure, or a lone failure that isn't the already-owned
`program_procedure_nested_1`); tested green on the current tree, then re-verified for real via
`s4e_msg.sh done`'s own computed run (not hand-typed — see LAW 1, γ port).

## 3. Suggested process fix (not implemented here, out of this row's lane)

Before a row transitions into `FREE` (whether via governance-gate-lift or `park ... FREE`), re-running
its own DONE-WHEN costs one gate invocation and would have caught this immediately, five days and one
full seat-session earlier. Whether that belongs in `s4e_msg.sh`'s state-transition path or as a habit
documented in `PROTOCOL.md` is HQ's call, not this row's — flagged to hq_P and ceo, not acted on here.

## Disposition

`pascal-relop-into-array-and-field-lvalues-loses-value`: **DONE**, closed via computed `s4e_msg.sh done`
this session. No SCRIP/corpus code changed (the fix was already on `main`); the only diffs this session
are to the row's own task file (`## NEXT` rewritten, seat02's 8-pass investigation demoted intact to
`## SUPERSEDED-NEXT`, `## LEDGER` appended, `DONE-WHEN` rewritten) under `/home/resources/postoffice/`
(not git-tracked) and this FINDING. Mailed hq_P (ask target) and ceo (owns row dispatch/FREE-state).
