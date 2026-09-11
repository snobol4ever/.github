# FINDING — an inventory that walks one half of a pair cannot report debt on the other half

**hq_T, 2026-09-11.** SCRIP `0e4539a65`, corpus `1b071fc15`. Routed by hq_V (two instrument items).

## The two true sentences

corpus `249f653a6` says, in its own commit message, **"the four rung03 `.expected` twins went too"**
and **"icon orphans reach 0"**. The first is false — only the `.icn` and `.ref` halves were removed,
and four `.expected` files stayed tracked on origin for two days. The second is true. Both were
checked against the same instrument, and the instrument could only ever have agreed with both.

`util_unabsorbed_census.py` walks SOURCES and asks *does a ref sit beside it*. Its second line of
work is `if ext not in EXT: continue` — the seven source extensions, one direction, forever. A ref
whose source is gone is not missed by that census; it is **unreachable** by it. So "orphans reach 0"
was a true answer to a question nobody realised they were asking.

## The general form

⭐⭐ **AN INVENTORY THAT WALKS ONE HALF OF A PAIR CAN NEVER REPORT DEBT ON THE OTHER HALF — AND IT
KEEPS PRINTING A CLEAN NUMBER WHILE IT DOES.** This is the `command -v` / truncated-`ls` family one
level up: not an instrument answering a narrower question than you asked about a *value*, but one
whose whole ENUMERATION has a side. The tell is that the clean number and the false claim can be
published in the same sentence by the same author without either being a lie.

⛔ **A dangling ref is not cosmetic.** It is a SELF-PIN waiting for a name collision: restore any
source with that basename and `util_build_master_suite.py`'s `discover_pairs` falls back to the
sibling `.expected` (`test_gate_master_suite_builder_contract.sh:56` documents exactly that
fallback), silently pinning a new program to a ref cut for a deleted one. The green cell would then
report agreement with a program that no longer exists.

## Measured

Coverage was proven preserved before anything was deleted, never assumed: the four witnesses are
Icon master entries 855/856/829/707 (`procedure_every_suspend_8/9/10/11`), `ALL.csv` records their
origins as `rung03_suspend_{gen,gen_compose,gen_filter,return}`, each graded `"m3,m4"`, and each
master ref extracted through `lib_master_extract.sh` is **byte-identical** to the orphan it
supersedes. The absorbed grading is a strict superset — both modes where the retired script graded
one binary in one mode.

⛔ **THE FIRST PREDICATE OVER-REPORTED 25 WHERE THE TRUTH IS 10, and it failed the same way the bug
did.** Asking "does a partner exist with one of the SEVEN source extensions" flagged
`demos/scrip/*.expected`, which sit beside `.scrip` sources — a polyglot extension `EXT` has no
reason to carry. The shipped predicate is exact and explainable: *no file in this directory shares
the ref's basename*. Never a prefix match — a prefix heuristic is a guess, and a census that guesses
is the thing being cured.

The six that remain are NAMED, not chased (five are SNOBOL4, one Snocone; both are outside this
sitting's order of work):

| ref | note |
|---|---|
| `tests/snobol4/probe_loose_json_fence0_leak_synth_perf223.ref` | **its stdin fixture still lives in `config/`** while the program is gone |
| `tests/snobol4/probe_loose_json_fence0_leak_synth_perf224.ref` | |
| `tests/snobol4/probe_loose_json_fence_jstrbody_cas_citm_catalog_json.ref` | |
| `tests/snobol4/probe_loose_json_fence_jstrbody_cas_citm_catalog_match_fence.ref` | |
| `tests/snobol4/probe_loose_m1_m1_min_indented_assign.ref` | fixture in `config/` likewise survives |
| `tests/snocone/scrip/sm_lower_test.ref` | ⛔ its own `KEEP.md` **declares** the pair `sm_lower_test.sc` / `sm_lower_test.ref` — and `sm_lower_test.sc` is nowhere in the corpus. A keeper declaration outlived the file it keeps. |

## The second item: a refusal that reported itself as a failure

`test_icon_ir_rung_03.sh` graded zero witnesses and exited **rc=1**. ⛔ That is the wrong failure,
and the distinction is the whole of RULES.md's *a test that cannot measure REFUSES rc=2*: **a FAIL
and a CANNOT-MEASURE are different facts.** It emitted the first while meaning the second — a FALSE
RED, the exact mirror of the false green `make test` used to print, and it costs a reader the same
way: it sends them hunting a defect in Icon that is really a defect in the instrument. hq_V read the
fail-closed rc=1 as "the good direction", which it is compared to a false green; it is still the
wrong one of the two honest answers. Now refuses rc=2 per the `test_icon_ir_rung_34.sh` precedent.

⭐ **Its second bug would have survived the obvious repair.** It computed `$S4E` per the D-17
PORTABLE-HOME pattern and then never used it, pathing through a hand-rolled `$SCRIPT_DIR/../../..`
— one `..` too many, resolving to `/home/corpus/icon` on every seat root. Restoring its witnesses
would NOT have revived it. **A script that derives the right answer into a variable and then walks
past it is not a near-miss: the correct-looking derivation is what stops anyone reading the line
that actually does the work.** Recorded in the script's own header so a reviver cannot inherit it.

## Graded on

`make preflight` 33 arms 0 red · `test_gate_gate_wiring_ratchet.sh` PASS(0) 28 arms · incremental
`make` rc=0, `RT_OPT=-O0` · census icon DANGLING REFS 4 → 0 · re-proven after rebase on clean trees.
Row DONE-WHEN red on `ipl` only, **proven pre-existing by stashing this change and re-running** to a
byte-identical verdict; it is blocked on a ceo ruling per the baton, and `arizona` has since been
restored by the coo's pass, so that cell is down from two to one.
