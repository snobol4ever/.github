# FINDING seat08 — A LON-PARKED ROW (`161-o2-red`) SURFACED AS RANK-0 FREE WORK; `s4e_msg.sh` HAS NO PARK/UNCLAIM VERB TO STOP IT RECURRING

**seat08 (`/home/claude08`, Claude Sonnet 5), 2026-08-23, THE LOOP queue row `161-o2-red` (rank 0, claimed via `next`). SCRIP at `2a81f82c` (this seat's first v2 pull, 70 commits behind → current). No source changes land from this FINDING — it is a queue-hygiene / tooling-gap attribution, not a compiler fix.**

## ⛔ (1) HEADLINE — THE PICKER SERVED A ROW LON HIMSELF RULED TO PARK

Running the loop fresh after this seat's first Protocol-v2 pull, `s4e_msg.sh next` locked `161-o2-red` as `rank 0`, `QUEUE.tsv state FREE`. But `/home/resources/postoffice/tasks/161-o2-red.task.md`'s own header reads `state: PARKED (Lon s258)`, and its own last LEDGER entry (hq_C, 2026-08-22) is Lon's verbatim ruling to stop chasing the underlying defect: *"I doubt having BEAUTY running in -O2 matters much... In the end there will be NO C code. It will all be ASM... Let's get something fixed. Move on."* The two culprit functions (`c_rt_cap_open`, `rt_call_proc_descr`) are C runtime slated for hand-written-ASM replacement — hq_C's own words: *"a miscompilation in code scheduled for deletion is sunk cost."*

Per the standing rule that Lon's word overrides the brief (`RULES.md` / this seat's `CLAUDE.md` §THE LOOP item 6), I did **not** resume the -O1/-O2 register-coalescing chase. This is not a comment on hq_C's investigation, which is thorough and stands (file-level bisect → ddmin → disassembly read → variable-coalescing signal, all in the ledger) — it is a comment on the row's *lifecycle state* being wrong.

## (2) WHY THIS MATTERS FLEET-WIDE, NOT JUST TO ONE SEAT

`next`'s v2 serve order is `my-ASSIGNED → my-unfinished-claim → rank-sorted-FREE` (`s4e_msg.sh:232-234`). Rank 0 is the *highest* priority in that third pass. Any seat with no assignment and no existing claim — i.e. **every idle seat in the fleet** — will be served this exact parked row first, for as long as it sits unclaimed at rank 0/FREE. One seat wasting a turn on it is a rounding error; sixteen seats doing it, repeatedly, across `/clear` cycles, is not.

## (3) THE TOOLING GAP, CONFIRMED BY READING THE SOURCE (not inferred)

`s4e_msg.sh`'s full verb list (current, post-v2-rollout): `next|done|ask|send|check|clear|claim|assign|sweep|board|banner|fleet|mailbox`. There is **no** verb that ends a claim short of `done`. And `done` (`s4e_msg.sh:139-`) now genuinely enforces `DONE-WHEN` — reads it from the task file, runs it for real, refuses on non-zero, refuses a vacuous criterion, runs a vacuity probe in an empty directory. That enforcement is correct and working as designed (confirmed by reading it, not assumed) — but it means `done` is **only** the right tool for a row that is actually finished. Marking `161-o2-red` done would be dishonest here: `DONE-WHEN` as written only checks whichever arm is currently linked, the task's own `## NEXT` block says outright *"THE DONE-WHEN ABOVE ONLY CHECKS THE CURRENT ARM. Run it at ALL THREE: -O0, -O1, -O2,"* and the GOAL is explicit that the defect must be fixed *"under ANY optimisation level."* -O0 already matches the oracle; -O1/-O2 do not. Calling `done` here — even if it happened to pass because the currently-linked runtime is the -O0 dev default — would be exactly the false-green/vacuous-criterion shape the v2 rollout's own `done` enforcement (and hq_P's V2-5 gate-honesty work) was built to close. I am not routing around that discipline to unstick myself.

Net: there is a real gap between "a row should stop being dispatched" (a human/HQ lifecycle decision) and "a row is done" (a mechanically-verified fact) — and only the second has a verb.

## (4) WHAT I DID THIS TURN, GIVEN THE GAP

- **Did not** hand-edit `QUEUE.tsv`'s `state`/`rank` columns myself. That file's state vocabulary is very likely gate-checked (`test_gate_queue_is_an_index.sh` exists specifically to enforce its shape); inventing a value outside whatever enum the gate expects risks a fleet-wide false-red that has nothing to do with this row. That decision belongs to whoever owns the gate, not to a seat improvising on shared control-plane state.
- **Did** append a signed LEDGER entry to `161-o2-red.task.md` recording this finding, so the next reader of the baton (not just the next reader of `QUEUE.tsv`) sees it immediately.
- **Did** message hq_C (the row's `owner:` and the ruling's author) directly, asking them to either correct the row's `QUEUE.tsv` rank/state so a parked row stops surfacing as top-priority FREE work, or say what has changed since s258 that legitimately un-parks it.
- **Am holding the claim** rather than releasing it bare. An empty/absent claim on a rank-0 row is an invitation for the next idle seat to walk into the same trap within one `next` call; a held, ledger-annotated claim at least fails safe until hq_C answers.

## (5) RECOMMENDATION FOR THE NEXT SEAT OR HQ THAT TOUCHES THIS

- If you are HQ and can see this: the durable fix is either a `park`/`release` verb (symmetric to `claim`, writing some non-`DONE` terminal marker the picker's Pass-3 skip-if-claimed logic already respects) or simply correcting `161-o2-red`'s `QUEUE.tsv` row now.
- If you are a seat and `next` hands you a row whose task-file header says anything other than the state `QUEUE.tsv` implied (PARKED, BLOCKED, or similar prose the picker doesn't understand): don't treat "the picker served it" as "it's live work." Read the header and the tail of the LEDGER before the `## NEXT` block, not just `## NEXT` in isolation — the NEXT block here is still the (correct, thorough) technical plan from before parking; nothing in it says PARKED, only the header and the ledger's last entry do.
