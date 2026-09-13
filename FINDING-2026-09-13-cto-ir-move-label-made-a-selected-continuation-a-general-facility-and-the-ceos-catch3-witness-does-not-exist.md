# FINDING — IR_MOVE_LABEL made a selected continuation a general facility, and the witness the law now names does not exist

**cto, 2026-09-13. SCRIP `2a963f4d5` (+ `d9dd1e7ec`). Row `prolog-ir-move-label-is-deleted-on-lons-order-and-the-if-type-gate-banks-an-arm-index-not-a-code-address`, closed by computed `done` (1s).**

## The order

Lon, in-chat to ceo, verbatim: *"The IR_MOVE_LABEL is invalid. There are no labels. That is a carry over from JCON. Delete that IR."* (CEO-693), then, narrowing it: *"We use static wiring only, unless it is an if-type construct. So fix that."* (CEO-694).

## What the op was

`IR_MOVE_LABEL` stored a **code address** into a frame slot — `lea rax,<target>` then `mov [gate+16],rax` — and `IR_INDIRECT_GOTO` jumped through it on its β port, `jmp [gate+16]`. A Proebsting `ifstmt.gate`, named as such in our own `frame_layout.c`.

**They are one idiom in two ops and neither survives alone.** `IR_INDIRECT_GOTO` had no other writer anywhere in the tree, so deleting the writer and keeping the reader leaves a box jumping through a slot nobody fills. Both are deleted.

In their place `IR_GATE_ARM` banks **its own position in its gate's operand list** — a small integer — and `IR_GATE`'s β dispatches on it with `cmp`/`je` over labels resolved at compile time. That is the idiom `IR_DISJUNCTION` has always used for `alt_i`. No code address is stored anywhere in an emitted program any more.

**This landing is more conservative than what Lon permits.** He allows the if-type gate to stay dynamic; every target here is static. The ceo's *"do not replace the stored target with another runtime indirection"* was taken as binding even after he narrowed it.

## ⛔ The correction: the law's named witness does not exist

CEO-693 and CEO-694 read `lower_prolog.c:542-544` and `:564` as *"the catch/3 error-catcher-try triple"* and ruled a three-two split — three sites to static wiring, if-then-else keeps its gate. **They are not catch/3.**

- `:542-544` are `ml_e`, `ml_c`, `ml_t` — the condition/then/else gate arms of **`pl_lower_softcut`**, the ISO soft cut `(C *-> T ; E)`. `:564` is `ml_ee`, its else arm.
- **`pl_lower_catch` begins below them and builds no gate at all**, not one, and never did. It is `IR_BOUND` + `IR_UNMARK` + a `$catch_handle` leaf.

A soft cut is an if-then-else whose condition does not commit. So under Lon's rule as written, **all five sites are if-type constructs and the exception covers all five.** The rule was right; the population was misread. There is no three to move.

**The cost is one sentence in a sovereign file.** `ARCH-ENGINE.md` now states the static-wiring law with *"catch/3 took the facility"* as its witness. The law is right and wants no softening — *a facility reachable by everything is used by everything* is exactly correct, and it is the half this landing was built to. But the honest witness is **stronger**: the facility was reachable by everything **and nothing else took it**, which is luck and not design, and is a better argument for scoping than a violation would have been. Left as written, a future seat greps for the catch/3 gate and finds nothing.

## The half that matters more than the rename

The deleted op's real damage was that it made a **selected continuation available as a general facility** any construct could reach for. `ARM 3` of the gate censuses every construction site of both ops and refuses any outside `pl_lower_ite` or `pl_lower_softcut`. **Mutation-proved:** a gate built inside `pl_lower_catch` reds it at 9 sites; reverting returns it to green at 8. An exception that only a rule protects is advisory; this one is enforced.

## The quiet hazard, which was real

`frame_layout.c` classified the op in **four** places. An op dropped from the enum but left in `zls_is_wiring` is a **silent slot-granting change, not a compile error** — the enum value is reused by the next op and the classification starts applying to something else. All four moved together.

One of them bit: `zls_mark_value_refs` at `:228` skips the arm op's operands, and the **gate** now has operands too — its arms — so without adding `IR_GATE` there the arms would have been marked as live *value* references. Nothing would have failed to compile.

`:173` **survives the op**, as CEO-694 requires for the if-type case, but it is now `ZK_RAW "gate.live arm index"` and no longer `ZK_PTR_CODE "stored resume target"`: a collector reading a code pointer there would be reading a small integer. Same 8 bytes, same offset. hq_U is told in those words, because its unnamed-hole census reads that exact field — and hq_U's own reply establishes it never appeared in that census at all, since the census counts *unnamed* reservation and a **named field for a dead op is invisible to it by construction**. That is a second class beside hq_U's, and it is the cto's.

## Measurement

- **DONE-WHEN** `test_gate_no_stored_code_address_in_the_prolog_gate.sh`, wired into `make test`, ~0.7s at load 8 with 3 concurrent seats. **PROVEN RED at ARM 1** before the cure with both ARM-2 controls green in both modes.
- **ARM 2 is the load-bearing half.** 28 lines over 15 predicates that exercise the **gate** and not merely the construct: an arm leaving a redo, an arm containing a cut, an else arm that backtracks, nesting, soft cut with and without an else, soft cut whose condition leaves a choicepoint, both forms inside `findall`, and **backtracking back into an arm from after the construct**, which is the only shape that reads the gate's β port at all. A cure that deletes the op and quietly makes if-then-else deterministic passes ARM 1 and fails ARM 2.
- **CONTROL ARM on every other frontend**, measured on a clean `origin/main` worktree built beside this one: all 40 `test_smoke_*.sh` with the change and without. **19 red without, 18 red with, sets identical minus one.** `test_smoke_polyglot.sh` is RED on origin (twice — m3 printing nothing, m4 failing to build) and GREEN here (twice, PASS=2 FAIL=0 both modes). A standing red cured as a side effect, **named rather than claimed**: the old path bombed on an unresolved resume-target label in a multi-frontend chain, which an index dispatch cannot have.
- `make preflight` 40 arms 0 red at load 2.2 on 16 cores, 1 concurrent seat. No board run; ONE RUNNER binds.

## ⛔ An instrument error of my own, logged because it is the fourth today

I had a full blocking set running when **CEO-697** arrived — *no seat runs a full blocking set for a landing verdict*. It was terminated at arm 62 of 236 and I did not re-run it. The ceo's finding applies to me exactly: reaching for the biggest available instrument **feels** careful and is the most expensive way to be less correct than the DONE-WHEN already makes you. One arm of that run, `test_gate_runners_refuse_on_a_stale_binary.sh`, went red — **because I rebuilt the binary mid-run**, which is the gate correctly reporting my own concurrency and not a defect in the tree. A full set on a moving tree tells you less than a proven DONE-WHEN on a still one.

## Two follow-ons, named so they are not re-derived

1. **The ceo must fix `ARCH-ENGINE.md`'s witness** (above). Routed with the source citation, not as a dispute.
2. The `corpus/benchmarks/prolog/bench` checkout was stale and red-ed a preflight arm. **The arm named its own cause and the exact command to cure it**, which is why it cost a minute rather than an hour — the shape every refusal should have. Note for rung 9: `benchmarks/prolog/vanroy/` is **retired** on origin (CEO-567, the iteration count leaves the artifact), so CTO-41's ten-file census population and its `tak.pl` witness have moved and must be re-resolved before that rung's numbers are quoted again.
