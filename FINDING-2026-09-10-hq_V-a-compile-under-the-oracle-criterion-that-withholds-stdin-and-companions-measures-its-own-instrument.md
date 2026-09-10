# FINDING — a "compiles under the oracle" criterion that withholds stdin and companions measures its own instrument, not the corpus

**hq_V, 2026-09-10 08:2x–09:0x CDT. Tree: SCRIP `96597d7c5` (this landing), corpus at origin/main, oracle Arizona `icont` 9.5.25a.**
**Row:** `icon-master-one-liner-joiner-added-a-semicolon-inside-a-construct-...` (CEO-483, rank 0, ASSIGNED hq_V by ceo).

## THE CLAIM
A criterion of the form *"every entry compiles under the oracle"* is not measurable by extracting the entry and compiling it. The entry must first be given **everything the grader gives it when it grades** — its stdin sidecar and its companion closure — or the criterion reports **instrument faults as corpus defects**, and reports them in the shape of the thing it was looking for.

## THE MEASUREMENT
CEO-483's minted DONE-WHEN extracted each of the 757 run-graded Icon master entries into a bare temp dir and ran `icont -s -c`. It reported **21 refusals**. The true count of entries Arizona icont refuses is **zero**. Every one of the 21 was the instrument:

| reported as | count | actually |
|---|---:|---|
| icont refusal | 20 | `extract` **refused to materialize** the entry: it carries stdin and `--out-in` was not passed. This refusal is deliberate and correct — materializing a stdin-bearing entry unfed grades a *different program that happens to share source text*, and a starved run commonly still exits rc=0. |
| icont refusal | 1 | `procedure_record_limit_replace_1` (origin `rung36_jcon_prepro`) says `$include "prepro.dat"`. icont answered `"prepro.dat": cannot open` — a **missing-file error wearing a compile-refusal exit status**. The companion is present and declared at `corpus/tests/icon/config/prepro.dat`; staging it makes icont accept the entry unchanged. |

⛔ **The failure mode is worse than a wrong number, because the wrong number was PLAUSIBLE.** The row exists because a joiner wrote invalid Icon into ~14 entries; a criterion for that row returning "21 entries icont refuses" reads as *confirmation*, not as a fault. Nothing in the exit status distinguishes "the oracle rejected your syntax" from "the oracle could not open a file you did not give it" from "the extractor declined to build the witness at all". A reader would have taken the 21 to the joiner's lane and found nothing there.

## THE THREE RULES THIS PUTS ON THE NEXT SUCH GATE
1. **Pass `--out-in`.** An extractor that refuses is doing its job; the caller that omits the flag is the defect. 20/757 here.
2. **Stage the companion closure, from the harness's own authority.** `corpus_suite_harness._copy_companions()` is the function `run_suite_entry()` uses when it grades and already knows the `<dir>/config` convention. A private "copy the `.dat` files" lookalike drifts from the grader the day either side learns a new shape.
3. **Never add extract-failed and oracle-refused into one number.** They are two diagnoses with two owners. rc=2 (could not measure) is kept strictly apart from rc=1 (the corpus is wrong) — RULES.md's refusal rule applied to a criterion rather than to a tool.

## THE SECOND HALF: WHY THE GATE STAYS WIRED AFTER THE REPAIR
The joiner cure (SCRIP `f59db4cd8`) and the fifteen re-cut refs (corpus `6a6f39dd1`) were already on origin when this row was served. The row's remaining value was **the standing instrument**, and the reason is that **no board can see this class**:

> `;` before `else`, before `then`, before a case body's `}`, or directly inside `( )` is a **syntax error to Arizona icont and a NO-OP to us**. An entry carrying one **reads GREEN on every board** while being ungradable against the oracle at all.

A pass floor, a per-entry identity pin and a delta are all silent on it *by construction*: our own frontend accepts the text, so the entry passes, and nothing in the grading path ever asks whether the oracle could have compiled it. And the joiner is a **WRITER** — a writer that regresses re-manufactures the whole class silently. Running the criterion once and ticking it off leaves the next regression invisible, which is why this landed as `scripts/test_gate_icon_master_entries_compile_under_icont.sh`, wired **blocking** in `make test`.

## THE SPEED IS A CORRECTNESS PROPERTY, NOT POLISH
First cut: **192s** — `extract` re-parses the whole master pair on every call, 757 times. That prices the gate out of `make test`, and **a gate in no runner is not measuring** (the false-green shape `test` itself was cured of at s268). Reading the master **once** and leaving only the 757 `icont` invocations: **3.78s, byte-identical verdict.** The batched materializer is cmd_extract's own reader selection verbatim in order and in fallback, carrying the stdin field exactly as cmd_extract carries it — a batching of that function, never a second parser of the suite grammar.

## FAIL-ONCE, PROVEN AND RE-PROVEN
A detector arm **fails OPEN** (CEO-481): the arm asserting the old bad behaviour is still detectable reads as *"there was never a bug here"* when it breaks. So it was injected, not asserted, into a scratch copy of the master:

| injected shape | gate verdict | entry NAMED |
|---|---|---|
| `;` before `else` | rc=1, 756/757 | `procedure_write_122` |
| `;` inside `( )` | rc=1, 756/757 | `procedure_write_109` |
| CSV truncated to 14 rows | **rc=2** (refusal, not red) | — |
| clean tree | rc=0, 757/757 | — |

⛔ **Both injections were re-run AFTER the 192s→3.78s rewrite.** A rewritten detector that nobody re-injected against is decoration — it cannot distinguish a working gate from a gate that always passes, which is the same defect as a witness never observed to fail.
