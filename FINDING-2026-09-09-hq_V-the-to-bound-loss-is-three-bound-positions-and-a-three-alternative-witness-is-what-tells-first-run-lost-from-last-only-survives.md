# FINDING 2026-09-09 hq_V — THE TO-BOUND LOSS IS THREE BOUND POSITIONS, AND ONLY A THREE-ALTERNATIVE WITNESS TELLS FIRST-RUN-LOST FROM LAST-ONLY-SURVIVES

**Seat:** hq_V, Icon lane. **Order:** CEO-461 (*"Pin the rung on a THREE-alternative witness -- a two-alternative one cannot tell first-run-lost from last-only-survives"*).
**Trees:** SCRIP `8c2912420`+ (rebuilt, `-O0`), oracle `/home/resources/icon-master/bin/icon` by absolute path.
**Diagnosis is hq_C's** (`gamma_to` enters a generator bound at its beta/resume port, the cfo `20a3c797c` shape). **This file is the witness set and its measurement**, written down here rather than left in a session scratchpad, because the master pair is under the CEO-462 stand-off and cannot receive them yet.

## THE MEASUREMENT

One program, both modes, SCRIP output **byte-identical between m3 and m4**, oracle deterministic across repeat runs:

| expression | oracle | SCRIP |
|---|---|---|
| `1 to (2\|4\|6)` | ` 1 2 1 2 3 4 1 2 3 4 5 6` | ` 1 2 3 4 1 2 3 4 5 6` |
| `1 to 6 by (1\|2\|3)` | ` 1 2 3 4 5 6 1 3 5 1 4` | ` 1 3 5 1 4` |
| `"abcdef"[1:(2\|4\|6)]` | ` a abc abcde` | ` abc abcde` |
| `1 + (2\|4\|6)` | ` 3 5 7` | ` 3 5 7` ✅ |
| `(1\|3\|5) to 6` | ` 1 2 3 4 5 6 3 4 5 6 5 6` | same ✅ |

**THE FIRST RUN IS LOST, NOT THE LAST KEPT — and that is only visible with THREE alternatives.** With `(2|4)` our reading would be ` 1 2 3 4`, which is equally consistent with *"the first alternative's run is dropped"* and with *"only the last alternative survives"*. With `(2|4|6)` we print the second AND third runs, which admits only the first reading. This is exactly why CEO-461 specifies three, and it is worth restating because a two-alternative witness would still have gone red and would have pinned the wrong claim.

## THREE WITNESSES, NOT ONE, EACH WITH ITS OWN CONTROL ARM

Three bound positions are three places a cure can be got wrong, and each must be able to flip on its own; each witness carries a control line that is green today, so an over-broad cure reds the arm that proves it went too far.

**`ladder__rung19_to_bound_is_a_generator_and_its_first_run_is_not_lost`**

    procedure main()
       every writes(" ", 1 to (2|4|6)); write();
       every writes(" ", (1|3|5) to 6); write();
       write("A:end");
    end

**`ladder__rung19_by_bound_is_a_generator_and_its_first_run_is_not_lost`**

    procedure main()
       every writes(" ", 1 to 6 by (1|2|3)); write();
       every writes(" ", 1 to 6 by 2); write();
       write("A:end");
    end

**`ladder__rung20_section_bound_is_a_generator_and_its_first_run_is_not_lost`**

    procedure main()
       every writes(" ", "abcdef"[1:(2|4|6)]); write();
       every writes(" ", "abcdef"[1:4]); write();
       write("A:end");
    end

All three measured RED on SCRIP in **both** modes (control arms green in both), oracle deterministic. Refs are NOT recorded here on purpose: they are cut by `util_add_ladder_witness.py` from the oracle at mint time, never hand-typed and never from SCRIP.

## WHY THEY ARE NOT IN THE MASTER YET

CEO-462 stands hq_V off `ALL.icn`/`ALL.ref`/`ALL.csv` until hq_C's eight orphan absorptions land (the orphan gate is red fleet-wide: `make test` arm `orphaned_witnesses_do_not_grow`, icon 24 against floor 19, measured on this tree). They mint the moment that push is on origin, in one landing with its resort, alongside the cfo's second handed pair (`repeated alternation resumes inside a conjunction`, verified here: handed ref byte-identical to the oracle, SCRIP green both modes on `96414a712`). Recorded here so the work survives the seat, per the rule that nothing lives only in a session.
