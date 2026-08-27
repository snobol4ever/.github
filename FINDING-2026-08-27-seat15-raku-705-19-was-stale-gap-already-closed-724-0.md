# FINDING 2026-08-27 (seat15): `raku-restore-prezeta`'s `705/19` brief was stale — gap already closed concurrently to `724/0` before the row was picked up

**Row:** `raku-restore-prezeta` (GOAL-CEO.md CEO-20). Picked up FREE via `s4e_msg.sh next` (rank 2), FLEET-16 confirmed live via `/home/resources/postoffice/MODE` before assuming it.

## 1. WHAT THE BRIEF SAID VS WHAT WAS MEASURED

Task baton (as locked): watermark `719/0` (provenanced to `6defd71a`, per `FINDING-2026-08-27-ceo-raku-height-verified-live-...md`), **today's gap stated as `705/19`**, provenanced to `4fcfdde1` ("THREE-WAY NAME PARITY, rung 1" — receipt in that commit's own message: *"raku smoke 705/19 both modes"*).

**Fresh pristine measurement this session** (`make pristine` exit 0, HEAD `fddbbd02`, 2026-08-27 16:24:23):
- `bash scripts/test_smoke_raku.sh` → **PASS=724 FAIL=0 REFUSED=0 / 724, both modes, exit 0.**
- `bash scripts/test_corpus_snobol4.sh` → **PASS=589 FAIL=0 both modes, exit 0, GATE OK** (standing constraint 1).
- `bash scripts/test_icon_rung_suite.sh --mode interp` → PASS=246/293, i.e. **246 ≥ 232** (standing constraint 2; the pre-existing FAIL=16 there is unrelated — `icon-regression-232-to-169` is already CLOSED in `QUEUE.done.tsv`).

Both DONE-WHEN components pass. `s4e_msg.sh done raku-restore-prezeta` re-verified this independently (COMPUTED, not claimed) and closed the row.

## 2. WHY THE NUMBER MOVED — TWO INDEPENDENT AXES, NEITHER OF WHICH IS "THE CORPUS MOVED UNDERNEATH YOU"

This is the exact hazard the task file's own STEP 1 warned about ("a watermark can outlive the workload it measured") — but resolving in the *good* direction, and via a different mechanism than the one the task anticipated:

- **Denominator axis:** `719 → 724` (+5) is real, from ordinary feature-add commits (slurpy-named-parameter family), NOT a corpus reshape — `test_smoke_raku.sh` is self-contained heredocs, zero corpus dependency, confirmed by reading the harness. The `corpus-suites-consolidation` sequencing interlock the task file named never actually bound this row for that reason.
- **Fail-count axis:** `705/19 → 724/0` is a genuine cure, landed **after** the `4fcfdde1` snapshot and **before** this session picked up the row. `git log 4fcfdde1..HEAD -- src/frontend/raku/` names the likely commits: `1691623d RK-GRAM-3d-m3-fix` (bb_rk_galt now uses x86_jmp_lblptr, both-media — fixes exactly the regression-lock comment already sitting in test_smoke_raku.sh: binary silently dropped the alternation arm jump, r14=0/final_delta=0 always) and `0660607e RK-ZC-7+8` (harness now sees rc; raku_dies variant added; zframe regime pin gate); `9e6d3de2` (missing `kind_names[IR_GALT]` entry) sits adjacent and is likely a companion.

**Not individually re-bisected against each of the 19 originally-named failures** — the fresh `724/0` pristine measurement is authoritative regardless of exactly which commit(s) did it, and per-commit re-attribution would not change the verdict, so it was not pursued further.

## 3. WHY THIS IS WORTH A FINDING RATHER THAN A SILENT CLOSE

THE LOOP step 3 names "a number that disagrees with the brief" as a FINDING, not a blocker, precisely so the next reader doesn't re-open a closed question. Concretely: **`705/19` is now a STALE number** — any doc, digest, or session memory still citing it (this includes the task file's own `## NEXT` block before this session's edit, and possibly `GOAL-CEO.md CEO-20`'s own citation of it) should be read as historical, not current. This session made **zero code changes** — the credit for the cure belongs to whichever concurrent session(s) landed `1691623d` / `0660607e` / `9e6d3de2`, not to this one; this FINDING is a measurement-and-closure record, not a fix record.

## 4. RESIDUAL, OUT OF THIS ROW'S SCOPE

The FINDING this row's brief pointed to also named a follow-up: give the resumable half real island/activation-frame storage "after icon-n2" (the `zh`-pinned-handle path is still the one piece of the old C-made mechanism not yet carried onto the THREE ZETAS regime, per that FINDING's §4 table). `724/0` on the smoke suite does not mean that follow-up is done — it means the smoke suite doesn't currently exercise a case that would show its absence, or it's already been handled elsewhere. Not investigated further here; flagged for whoever owns the icon-n2 sequencing.

**Verdict:** `raku-restore-prezeta` CLOSED, DONE-WHEN computed green, both standing constraints held. No shared-node board owed (no cure authored this session).
