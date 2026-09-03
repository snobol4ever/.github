# FINDING: a substring assertion the refusal ALSO contains is a coincidence, not a measurement — it held `test_gate_s4e_picker_v2` green at 18/19 while its headline property measured nothing

## TASK
`postoffice-gates-red-on-origin-because-no-s4e-gate-is-in-make-test` (FLEET-16, ceo dispatch, hq_B).
GOAL: three postoffice instruments were RED ON ORIGIN, each because the FIXTURE predates a cure to the
tool it grades, and nothing catches them because no `s4e_*` gate was in any runner. Measured on SCRIP
`05fee14f` (pulled `--ff-only` at session start; SCRIP, `.github` and corpus were ALL behind).

## THE HEADLINE: A GREEN CHECK THAT WAS MATCHING THE REFUSAL BANNER
`test_gate_s4e_picker_v2.sh` reported **18 passed, 1 failed** — one plausible red in a suite that was
otherwise reassuring. The truth is that its P1 block, the *rank-sorted picker*, the property the gate
exists for, was **locking nothing at all**. All four sandbox rows were being skipped, and the two
"passing" checks were matching text inside the SKIP MESSAGE:

```
↩ skipped 4 free row(s) owned by another seat (topmost: rank 0  THE-RANK-ZERO-ROW  (owner brief-0)).
QUEUE EMPTY — every row claimed.
```

against assertions written as `case "$out" in *"THE-RANK-ZERO-ROW"*` and `*"brief-0"*`. Both substrings
appear **in the refusal**. Only the third check — `*"another-row"*`, naming a row the banner does not
mention — was capable of telling the truth, and it is the single red that got this row minted.

⭐ **THE GENERAL FORM: an assertion whose substring the failure output can also contain is not an
assertion, it is a coincidence.** It is the `$?`-after-a-pipeline defect wearing test clothes — the
instrument answers a narrower question than you think you asked and never says so. The tell is
structural and greppable: a `case`/`grep` matching a bare *identifier* (a topic, a filename, a symbol)
rather than an anchored *verdict* (`LOCKED <topic>`). Refusal messages quote the thing they are
refusing, so the more informative the error, the more likely it satisfies a lazy assertion. Anchoring
is now on the verdict word: `*"LOCKED THE-RANK-ZERO-ROW (rank 0)"*`.

## THE UNDERLYING CLASS: FIXTURES TRACKING A COLUMN CONTRACT THAT MOVED
In all three gates the TOOL was correct and the FIXTURE was stale. `QUEUE.tsv` column 3 is still read
into a variable named `brief` but has been **used as the owner** since `THE OWNER COLUMN CONSTRAINS THE
PICK` (ceo 2026-09-03): anything not `''`, `unassigned` or the running seat is skipped as another seat's
row. Fixtures wrote `brief-9`/`b` there — none of those — so every row read as owned-by-someone-else.

- `test_gate_s4e_picker_v2.sh` — owner column `brief-N`; P1 measured nothing (above). **19/19.**
- `test_gate_picker_autounblock.sh` — owner column `b`; U2/U4/U5 red. **6/6.**
- `test_gate_dispatch_bus_failure_modes.sh` — failure A was only that it runs picker_v2 as a sub-suite
  and inherited its red; failure B closed a row with **no baton**, refused rc=2 since the HOLE-A cure of
  2026-08-28. Minted the baton the fixture always needed. **7/7.**

⛔ This sandbox has now been cured for this class **twice in the same file**: its own header records
s266 repointing the 4th column to state. Column 3 followed. A fixture that hard-codes a positional
contract will decay every time that contract moves, and it decays SILENTLY because a skipped row and an
empty queue are indistinguishable from a test that had nothing to do.

⭐ Two of the three diagnoses in the minted GOAL were right; **one was wrong and worth recording.** The
autounblock failures were attributed to the scratch postoffice having no `MODE` file (mandatory since
s266). The missing MODE file is real and now fixed — but it was **not the cause**: U1–U3 print the same
`⛔ MODE FILE ABSENT` banner and passed. It was the *first line of output*, so `head -1` put it in the
"actual:" slot of every failure report, and it read as the cause for a whole session. A loud correct
error banner sitting above the real failure is camouflage.

## U3 HAD TO CHANGE, AND NOT TO MAKE IT PASS
Curing the owner column turned U3 red: it asserted the state column reads `FREE` after the row is
served. `FREE` was only ever observable **because the row was skipped** — the park wrote FREE and
nothing claimed it. A row that is actually served is `CLAIMED:seatAA`. U3 now asserts the stale
`BLOCKED-ON:`/`PARKED-AWAITING:` spelling is gone AND the column agrees with the claim (s265: a column
disagreeing with its claim is the defect the file exists to catch). That is strictly stronger than the
old check, not a relaxation — the pre-fix injection still reds it, and all three gates still pass
`--self-check`, so each can still say NO.

## THE CURE FOR "NOBODY RUNS IT": `make test-postoffice`
Per ceo ruling (this row's LEDGER): a `test-postoffice` target runs every **hermetic** `s4e_*` gate and
`make test` runs it as the SECOND arm, right after `strip_comments --check`. Every seat's `next`/`done`/
`assign` rides on this one tool, so a red here is a red for all sixteen seats at once.

**Hermetic is measured, not assumed.** The nine gates below each build their own scratch postoffice
under `mktemp`; the set was verified to leave `/home/resources/postoffice` byte-identical (QUEUE.tsv,
QUEUE.done.tsv, `claims/`, `tasks/`) across a full run. The six gates that read the LIVE postoffice
(`baton_donewhen_runnable{,_live}`, `baton_next_blocks`, `baton_one_next_block`,
`baton_state_header_single_record`, `queue_is_an_index`, `s4e_release_verbs_mark_last_row`) are OUT:
they grade rows sixteen seats are editing right now and red on a dirty fleet BY DESIGN — the same reason
`test_gate_preflight_complete.sh` is out. Four of those six are red on origin as of this writing; that
is a separate question and is NOT what this row cured.

**FAIL-ONCE PROOF.** Planted the exact defect this row cured (one fixture row's owner column repointed
to `brief`) and ran `make test`: **rc=2 in 7 seconds**, naming the gate.

⛔ The first version of the target used `@bash …`, and the planted red produced `⛔ GATE FAIL: 1 of 9
check(s) failed` with **zero occurrences of the failing script's name** anywhere in the output — nine
candidates and no way to tell which. The `@` also silently disagreed with `test:`'s own unprefixed
style. Dropped it; make now echoes each gate, so the last echoed line names the failure. A runner that
says a gate failed but not WHICH gate has converted a red into a search.

## FILES
- `SCRIP/Makefile` — `test-postoffice` target (9 gates, ~13-22s), wired as `test`'s second arm; `.PHONY`.
- `SCRIP/scripts/test_gate_s4e_picker_v2.sh` — owner column, MODE file, verdict-anchored assertions.
- `SCRIP/scripts/test_gate_picker_autounblock.sh` — owner column, MODE file, U3 rewritten to the contract.
- `SCRIP/scripts/test_gate_dispatch_bus_failure_modes.sh` — baton minted for check E.
