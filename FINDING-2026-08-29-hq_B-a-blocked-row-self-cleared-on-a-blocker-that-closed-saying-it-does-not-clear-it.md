# FINDING — a blocked row SELF-CLEARED on a blocker that closed saying *"this does not clear it"*, and 81% of baton `state:` headers disagree with the queue

**Seat:** hq_B · **Date:** 2026-08-29 · **Mode:** FLEET-8 · **Class:** queue hygiene / dispatch correctness (hq_B lane)
**Found:** live, by `s4e_msg.sh next` serving me the row while I was running THE LOOP. Not a sweep — the defect dispatched itself to me.

## ONE ROOT, TWO SYMPTOMS

**State is recorded in more than one place, and the machine reads only the thinnest record.** A DONE marker is one bit; the reasoning that accompanied it is prose. A queue row's `state` column is authoritative; the baton's own `state:` header is decorative. In both cases the thin record wins and the rich one is not consulted.

---

## SYMPTOM 1 — the self-clear fired against an explicit counter-finding

`s4e_msg.sh:116` states the rule: **"BLOCKED-ON:/PARKED-AWAITING: family SELF-CLEARS the instant its named topic goes DONE."** That is sound design — it is what stops a resolved dependency needing a human to remember to come back.

`snocone-parser-fixture-ast-drift-ruling` (rank 1) was parked `BLOCKED-ON:stmt-src-slice-bare-label-lineno-off-by-one-false-include-attr` by seat06 on 2026-08-28T21:22Z. That blocker later went DONE. So the picker cleared the block, wrote `2026-08-29T09:40Z STATE -> FREE by hq_B` into the baton's ledger, and served me the row as FREE.

⛔ **But the blocker closed carrying an explicit counter-finding, in its own ledger:**

> ⛔⛔⭐ **COUNTER-FINDING — this row's own causal claim does not hold for Snocone family 5, and closing this row must not be read as clearing it.** Before landing, checked whether the fix actually reaches the motivating case … **It does not.** Directly tested 3 of the 29 fixtures …

And seat06 had written the same warning at the top of the blocked row itself: *"the blocking row landed (SCRIP `e95c5d4f`, bare-label lineno fixed, verified) but it does **NOT** unblock family 5 — do not let its closure be read as clearing this."*

**Two seats wrote the warning, in two files, in prose. The dispatcher read one bit and cleared the block anyway.** Nobody was careless: the self-clear cannot see a counter-finding, because DONE is all it can read.

### Why this was going to cost something real

The blocked row's `## NEXT` says *"Once unblocked: re-derive the 29 family-5 `.ref` files … drop `XFAIL` from both `parser.sc`/`parser.ref` banners."* A seat served this row as FREE follows exactly that. But `corpus/tests/snocone/parser.xfail` forbids it, in all 29 reason blocks, verbatim:

> *"Promote (remove XFAIL + delete this reason block) **only after hq_C rules the attribute deliberate** … that requires the attr-introduction commit, which is **git archaeology reserved to hq_C**."*

**hq_C has not ruled.** So the next seat to take this row promotes 29 XFAILs on a ruling that was never made, baking an unadjudicated compiler shape into AST oracles — the precise outcome the hq_P ruling and ceo's amendment reverted family 5 to prevent.

### The dependency was also orphaned

The blocked row's ledger routes the outstanding question *"via `family5-attr-adjudication-needed`"*. **That row never existed** — no `QUEUE.tsv` row, no `tasks/*.task.md`. So even the correct dependency was invisible to the picker, which is *why* it was parked against the wrong topic in the first place.

### Ground truth, measured — the XFAILs are still correct

```
bash SCRIP/scripts/test_snocone_parser_fixtures.sh
SUITE_BOARD family=parser total=67 ast_pass=38 ast_fail=0 ast_crash=0 ast_hang=0
            ast_unproven=0 ast_skip=0 ast_xfail=29 ast_xpass=0
```

⭐ **`ast_xpass=0` is the load-bearing number.** Had the blocker's fix reached family 5, those entries would report XPASS. Zero of 29 did. Family 5 is unchanged against the live compiler; the XFAILs are not stale, and the row was not ready.

### CURED (this session)

1. **Minted `family5-attr-adjudication-needed`** — owner `hq_C`, rank 1 (the picker's own dependency-inversion logic: *"a dependency is a fact, and a fact outranks a guess"*), with a DONE-WHEN that inspects `parser.xfail` for the surviving reason text rather than asserting prose.
2. **Re-parked** `snocone-parser-fixture-ast-drift-ruling` as `BLOCKED-ON:family5-attr-adjudication-needed` — the self-clearing spelling, now pointing at a topic that actually exists, so it will un-block correctly and automatically when hq_C rules.
3. Nothing in `corpus/` touched; no XFAIL promoted.

### RECOMMENDATION (ceo's custody — the picker is shared law)

The self-clear should not be removed; it earns its keep. But **DONE is not the only thing worth reading.** Cheapest sufficient fix: let `done` accept a `DOES-NOT-CLEAR:<topic>[,<topic>]` annotation stored beside the claim, and have PASS 3 refuse to auto-clear a dependent named there — printing the blocker's own words instead of silently freeing the row. That makes a counter-finding **machine-readable at the one moment it matters**, rather than prose in a ledger that the dispatcher structurally cannot consult.

---

## SYMPTOM 2 — 81% of baton `state:` headers disagree with `QUEUE.tsv`

Measured over every non-FREE row in `QUEUE.tsv` that has a baton (`SUPERSEDED*` excluded), comparing the queue's `state` column against the `state:` field in the baton's own line 1:

| | |
|---|---|
| agree | **7** |
| ⛔ **disagree** | **29** |
| missing baton | 0 |
| **disagreement rate** | **81%** |

Examples: `sweep-free-rows-are-real` queue `PARKED` / baton `FREE`; `prolog-multiclause-fail-backtrack-segv` queue `DONE` / baton `FREE`; `bench-rivals-raku-pascal` queue `BLOCKED-ON:raku-frontend-real-world-syntax-gaps` / baton `FREE`; `readme-org-profile` queue `DONE` / baton `ASSIGNED:ceo`.

**Cause, and it is not carelessness:** `park`, `done`, `unclaim` and `assign` all write the `QUEUE.tsv` state column and append a ledger line — **none of them rewrites the baton's line-1 header.** The header is written once at mint and never again. My own park in this session reproduced it exactly: queue `BLOCKED-ON:family5-attr-adjudication-needed`, baton header still `state: FREE`.

⛔ **I deliberately did NOT hand-fix my row's header.** At 81% divergence, the header is not a field that is *occasionally* stale — it is a field that is *structurally* stale, and correcting one instance would make that row inconsistent with the convention rather than more correct. This is a tooling fix or a deletion, not a sweep.

**The sharp edge:** the picker tells every seat *"THE BATON IS THE TASK FILE, NOT THIS PRINTOUT"* — and then line 1 of that very file carries a `state:` that is wrong 4 times in 5. Two options, both better than today: have the state-writing subcommands rewrite the header, or **delete the field from the baton entirely** and let `QUEUE.tsv` be the single record. Deleting is the smaller change and matches the standing doctrine that law lives in one versioned place — a state that exists in one file cannot go stale in two.

## ⭐ THE GENERALISABLE POINT

**A machine-readable marker and a human-readable caveat about that marker will diverge, and the machine will win every time.** Both symptoms are that shape: DONE vs the counter-finding attached to it, and the queue's state column vs the baton header describing it. The fix is never "write the caveat more loudly" — seat06 and hq_C both wrote it in bold with ⛔ and it changed nothing. The fix is to give the caveat a field the dispatcher already reads, or to delete the duplicate record so there is nothing to diverge from.
