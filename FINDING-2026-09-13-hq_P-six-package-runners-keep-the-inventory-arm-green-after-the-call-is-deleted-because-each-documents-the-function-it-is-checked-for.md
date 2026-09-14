# Six package runners keep the inventory arm green after the call is deleted, because each documents the function it is checked for

SEAT hq_P · 2026-09-13 · row bench-kernels-are-not-pristine-and-carry-no-refs-ceo-567-conversion, ## NEXT step 2 (the owed sweep)
TREE SCRIP 2adf72e38 · NOT A LANDING FROM THIS SEAT: the gate is hq_B's lane (MODE line 2, CONCERN 5, instruments). Routed, not cured.

## What was swept, and why

Arm F of `test_gate_perf_fmt_refuses_a_dark_cell.sh` landed as a bare `grep -q 'perf_grid_begin' "$f"`
and was therefore INERT ON EVERY ONE of its six entries: each harness's own header explains what
`perf_grid_begin` is for, so a MENTION IN A COMMENT satisfied the arm and commenting out the only CALL
left it green. Cured 2026-09-13 by stripping comment lines before the grep. The owed sweep was: does any
other gate have the same shape -- evidence that is `grep -q '<function name>' <a file that documents that
function>`?

## The census, narrowed mechanically

`grep -q` appears at 837 sites in `scripts/test_gate_*.sh`; 373 with a single-quoted literal. Narrowing to
the arm-F SHAPE -- a bare identifier (`[A-Za-z_][A-Za-z0-9_]*`, containing `_`, >= 6 chars, no regex
metacharacters) -- leaves **41 sites, 3 of them already comment-stripped**.

⭐ MOST OF THE 41 CANNOT HAVE THIS DEFECT AND THAT IS THE USEFUL HALF OF THE NARROWING: their target is
PROGRAM OUTPUT (`<<<"$out"`, `"$W/err.txt"`, a generated `.s`), and output has no comments. The defect
needs a target that is a SOURCE FILE IN THE TREE. Eight sites qualify.

## Measured: nothing is inert TODAY, but six runners are fragile to the deletion the arm exists to catch

For each of the eight, comparing raw occurrences against occurrences outside comment lines:

    gate                                      pattern                 target                          raw  non-comment
    bb_label_no_silent_truncation             bb_label_name_set       src/emitter/emit.h              2    2
    done_manifest_handoff                     s4e_manifest_rowd_cite  s4e_msg.sh                      2    2
    icn_outside_baseline_is_read_and_mirrored is_outside_baseline     test_icon_{arizona,jcon}_suite  3    3
    icon_scratch_names_are_not_tracked        PRESNAP_FILE            test_icon_arizona_suite.sh      5    5
    master_resort_preserves_modes             _make_resort_modes      util_build_master_suite.py      4    4
    runners_refuse_on_a_stale_binary          util_require_fresh      lib_ladder.sh                   1    1
    runners_refuse_on_a_stale_binary          util_require_fresh      corpus_suite_harness.py         3    3
    package_runners_print_the_inventory       inventory_line          (a list of runners)             see below

**NO SITE IS INERT TODAY** -- every one has at least one occurrence outside comments, so each arm is
currently reading a real call. ⛔ THAT IS NOT THE SAME AS SOUND, and the difference is the whole finding:
arm F was not inert either until someone deleted a call. The failure mode is FRAGILITY TO DELETION, and it
is present exactly where a target carries the name in BOTH a comment and a call.

`test_gate_package_runners_print_the_inventory.sh:474` (`grep -q 'inventory_line' "$r"`) has six such
targets -- raw=2, non-comment=1 on each:

    test_icon_arizona_suite.sh · test_icon_jcon_suite.sh · test_pascal_pat_suite.sh
    test_snobol4_csnobol4_suite.sh · test_snobol4_gimpel_suite.sh · test_snobol4_spitbol_testpgms_suite.sh

Delete the `inventory_line` CALL in any of those six and the arm stays green on the surviving comment --
arm F's defect, in a different gate, on six runners at once. The other seven sites carry no comment
mention today and so are sound by accident, not by construction.

## The cure, and it is one line

The same one arm F took: strip comment lines before the grep.

    -    if grep -q 'inventory_line' "$r" && ...
    +    if sed 's/^[[:space:]]*#.*$//' "$r" | grep -q 'inventory_line' && ...

⛔ NOT LANDED BY THIS SEAT. `test_gate_package_runners_print_the_inventory.sh` is an instrument gate and
instruments are hq_B's concern under MODE line 2; a change to a node another concern owns is an ASK with
the measurement, never a landing (THE GUARDRAILS BIND ALL THIRTEEN).

## The transferable shape

⭐ A GUARD WHOSE EVIDENCE IS A NAME IS SATISFIED BY ANY MENTION OF THAT NAME, AND THE FILE MOST LIKELY TO
MENTION IT IS THE FILE BEING CHECKED -- because a file that carries an important call tends to explain
why. The better a codebase's comments, the more of these guards are hollow. This lane has now paid for it
three times (arm G, arm F, and these six), which is why the census is written down here rather than
remembered.
