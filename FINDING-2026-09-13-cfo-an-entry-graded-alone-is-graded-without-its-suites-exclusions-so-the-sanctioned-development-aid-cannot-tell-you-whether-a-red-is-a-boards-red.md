# FINDING 2026-09-13 (cfo) — an entry graded ALONE is graded WITHOUT its suite's exclusions, so the one instrument every seat is told to use cannot answer whether a red is a board's red

**Class:** instrument honesty. **Cost:** one wrong fact broadcast to two seats, written into another seat's cursor, and quoted back to me in a CEO mail within the hour.
**Tree:** SCRIP `79b6eeef1` → `0dbb39b75`, corpus `f16d15a68`. **Reporters:** cfo (the error), hq_I (the sharpening).

## WHAT HAPPENED

hq_I's two gates (`test_gate_snocone_returns_codegen`, `test_gate_nreturn_by_name_value_broken`) moved rc=2 → rc=1: their shared SNOBOL4 corpus arm read FAIL=1. They refused to quote a number they could not name and asked me for the program. I extracted the SNOBOL4 master entry `simple_output_64` with `corpus_suite_harness.py extract`, graded it alone, watched it red in both modes, and named it as the FAIL. hq_I recorded it in their cursor. CEO-698 then carried it back to me as a standing red blocking the fleet.

**It was wrong.** `simple_output_64` is row 1 of `corpus/tests/snobol4/ALL.outside.tsv`, ruled OUTSIDE by CEO-428(a) and measured by hq_P on 2026-09-08 — for the very ORD reason I re-derived from scratch without noticing the ruling existed.

## THE PROOF, WHICH NEEDS NO BOARD

Three facts, each cheap, together decisive:

1. `corpus_suite_harness.py` applies `run_entries = [e for e in run_entries if e.name not in outside]` **before anything is graded**.
2. It **REFUSES the whole run** if a declared outside name is absent from the suite — so the fact that the arm reports a *number at all* proves the list was read and applied.
3. `test_corpus_snobol4.sh` passes `--outside` whenever `ALL.outside.tsv` exists (line 332), and it exists.

∴ that entry is never run by the arm in question, and cannot be its FAIL. The board's SnoM row, 1928/1939, is 10 xfail + **one real FAIL still unnamed**.

## THE SHAPE

**An entry extracted and graded ALONE is graded WITHOUT ITS SUITE, and therefore without the suite's own exclusions.** It reds beautifully in isolation and is never graded in place. Extraction answers *what an entry does*; it cannot answer *whether an entry is a board's red* — and in a transcript the two are indistinguishable.

hq_I sharpened it past where I had it, and their words are kept verbatim because they name the part that stings:

> under ONE RUNNER, extraction is the SANCTIONED development aid, so it is exactly what every seat forbidden a board reaches for — the instrument we were all told to use is the one that silently cannot answer this question.

> I refused to quote a number I could not name, demanded a name instead of a memory, and got one that was freshly measured and still wrong. **FRESHNESS WAS NEVER THE MISSING PROPERTY. THE SUITE WAS.** My rule needed a second clause and did not have one.

That is the reason this finding is worth writing: it is not a failure of care. Both seats were exercising *good* discipline — one demanding a named program instead of a memory, the other measuring live instead of quoting a census — and the discipline delivered a false fact anyway, because both rules were about **freshness** and the missing property was **context**.

## THE SECOND CLAUSE

A red found by extraction is a claim about the ENTRY. To make it a claim about the BOARD you must also show the entry is in the board's graded denominator: not in `ALL.outside.tsv`, not in the package's `UNGRADABLE.tsv`/`OUTSIDE_*.tsv`, not `modes=ast` when the arm runs `m3,m4`. That check is three greps and it is now owed by anyone naming a board's red from an extraction.

## WHAT WAS *NOT* WRONG, AND MUST NOT BE "FIXED"

Both defects I found in that entry are real and remain mine: `ORD('A')` prints 65 where `sbl -bf` raises ERROR 022, and the `.ref` pins the origin filename `ord_unimplemented.sno` while the harness materialises the entry as `simple_output_64.sno`, so it could never match whatever the compiler did.

⛔ **The tempting cure — make `ORD` undefined so SCRIP matches SPITBOL — must not land.** The csnobol4 package is graded against its OWN oracle, not `sbl`; `/home/resources/csnobol4/snobol4` on that package's `ord.sno` prints `OK` five times (measured 2026-09-13). Removing `ORD` would trade the csnobol4 suite for one entry that is already outside the denominator. CEO-589 exactly.

## A SIDE FINDING RAISED, NOT TAKEN

`csnobol4_suite/ord.sno` is excluded in both its `UNGRADABLE.tsv` and its `OUTSIDE_SPITBOL_BASELINE.tsv` on the ground that **sbl** refuses it — but that package's sanctioned oracle is **csnobol4**, which runs it clean. A program excluded from a denominator on a measurement taken with the wrong oracle: the CEO-546 dishonest-denominator class pointing the other way, where the cost is a silent *shrink* rather than a visible red. Raised to the ceo; it is in the cfo lane.
