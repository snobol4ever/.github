# FINDING — the corpus re-grid turned a RED board GREEN: measured before and after, one session, one script

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-08-24 (s272) · **Mode:** FLEET-12
**Trees:** before — SCRIP `d1b1cfa7` / corpus `0f8b0e2dd` · after — SCRIP `ab9c087c` / corpus `fea43840f` / `.github` `e813bb4c`
**Trigger:** CEO's Lon-ordered corpus re-grid (verbs on top; the `corpus/<language>/` level eliminated), landed between the two measurements.

---

## THE MEASUREMENT

The same script, run by the same seat, on both sides of the move:

| when | tree | `bash scripts/test_prolog_rung13.sh` | exit |
|---|---|---|---|
| ~21:1xZ | corpus `0f8b0e2dd` | `PASS=0 FAIL=5` — five real failures | **rc=1** |
| ~21:5xZ | corpus `fea43840f` | `SKIP: /home/claude_C/corpus/prolog missing` | ⛔ **rc=0** |

⛔ **The board did not go red. It went green.**

**Mechanism, and it is one line.** `corpus/prolog/` moved to `corpus/tests/prolog/`. Line 7 of each rung script is:

```sh
[ -d "$CORPUS" ] || { echo "SKIP: $CORPUS missing"; exit 0; }
```

A missing corpus becomes **success**. Every honestly-graded Prolog number is invisible again — the precise state that `prolog-assertz-retract-abolish-unmasked` was minted to end, restored by a directory move.

**Blast radius, measured: 14 scripts** now silently SKIP-and-exit-0 — the whole `test_prolog_rung12…21` ladder plus `rung36_arith_edge`, `rung37_term_ops`, `rung38_iso_errors`, and the Icon equivalents.

**Corroboration, independent and from a different seat:** seat07 reported `test_gate_no_fossil_src_paths.sh` at **GATE FAIL, rc=1, 53 fossil default paths of 210 examined** — prolog 50, icon 31, pascal 6, snobol4 5, snocone 4, rebus 1, probe 1. Re-verified here on this seat's own build. seat07 correctly declined to fix scripts belonging to rows they do not own and flagged under the non-blocking-finding protocol.

---

## WHY THIS IS THE DANGEROUS DIRECTION

A move that breaks a board **loudly** costs an hour. A move that breaks a board **quietly, in the passing direction** costs however long it takes someone to notice — and nobody goes looking behind a green board. The pre-move numbers (rung13 **0/5**, rung14 **2/5**, rung15 **1/5**) were independently reproduced by this seat before the move and stand as the honest board; after the move nothing in the fleet reports them at all.

⚠️ **`prolog-assertz-retract-abolish-unmasked`'s STEP 1 is now a trap.** It instructs a seat to "re-run the repointed rungs and reproduce 0/5, 2/5, 1/5." **Today that yields `SKIP` and rc=0 on all three**, from which a reasonable seat could conclude the row is cured. It is not. That warning is now written into the row itself.

---

## THE ONE THING THAT WORKED, AND IT SHOULD BE COPIED

⭐ **seat04's `test_gate_no_fossil_src_paths.sh` caught this within minutes of the re-grid.** It exists for exactly this: *"a hardcoded default corpus path that no longer resolves is now a computed FAIL, not a silent smaller-or-empty corpus."* It fired immediately, and it is the only reason this surfaced now rather than at the next campaign.

⛔ **But note precisely what it does and does not do: the gate catches the fossil path; the rung scripts still return 0.** The gate is a detector bolted alongside the liars, not a cure for them. Both halves need fixing.

---

## THE REPAIR — BOTH HALVES, AND THE SECOND ONE IS THE POINT

1. **Repoint** the 53 fossil defaults (`corpus/prolog` → `corpus/tests/prolog`, `corpus/icon` → `corpus/tests/icon`, …).
2. **Convert every missing-corpus arm to REFUSE with `rc=2`**, never `exit 0`.

⛔ **Fixing only (1) rearms the silent-skip guard for the next move, and there will be a next move.** The corpus has now been re-shaped three times in four days (s269 flatten, s271 lon move, s272 re-grid). The row's own GOAL text demanded `rc=2` *before* the re-grid — *"When you touch this harness, make the missing-corpus arm REFUSE (rc=2), never skip"* — and that instruction has now been vindicated twice by the same defect in one day.

⭐ **The general law this is the third instance of today:** ⛔ **a guard that converts "I could not measure" into "nothing to report" is the most productive bug-hiding mechanism in this codebase.** Today's three, all independently found: this one (`[ -d "$CORPUS" ] || exit 0`); `s4e_hq()`'s `[ -d "$PO/hq/inbox" ]` fallback, which stranded 17 asks in a retired mailbox; and `trace-dump-permissive`'s DONE-WHEN, permanently false because it requires a `.ref` that has never existed. **Same shape every time: a directory-existence check standing in for a decision or a measurement it cannot actually make.**

⭐ **The counter-example, from the same hour, showing it is a choice and not a constraint:** `test_corpus_snobol4.sh` hit the identical situation mid-rebase — its suite file was momentarily absent — and **refused with rc=2**: *"no suite file at …/suites/crosscheck/patterns.sno … Repoint them; do NOT read the shrunken total as a pass. FAIL=0 over a shrunken denominator is not green."* Same class of event, one line of difference, and it cost one `git pull` and zero false conclusions.

---

## ROUTING

Escalated to CEO (re-grid fallout, needs an owner; the fix is script paths, not Icon/Prolog semantics, so it is **not** SNOBOL4-FIRST-blocked). Full before/after table written into `prolog-assertz-retract-abolish-unmasked.task.md` with the STEP-1 trap warning. No duplicate row minted — the mechanism belongs to the existing one. seat06's and seat07's questions answered directly.

⛔ hq_C ran the three rung scripts **only** to verify a live regression in a row this seat owns, not as workflow; Lon's SNOBOL4-FIRST order stands and is unaffected.
