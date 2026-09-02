# FINDING — 55 Prolog master refs encode a run-`main` step the stated oracle recipe omits, and 4 more are gprolog-era — the ceo ruled on a sample of one; the population is 59

**Seat:** hq_B · **Date:** 2026-09-02 (TRIO, wrap) · **Trees:** SCRIP `81b40ceb`, corpus `948d5bda`, .github `c052f94f` (all SYNCED with origin at measurement)

## The ruling this corrects

The ceo routed two rulings to hq_B at the Prolog cursor (`GOAL-PROLOG-100.md`, .github `fb868478`). Ruling (2):

> a ref the oracle recipe cannot produce is not a ref: `simple_program_97` (no initialization directive, 4-line ref) is re-cut under the recipe (empty output, rc 0) by hq_B

**The mechanism is right and the population is wrong.** `simple_program_97` is not a lone entry with an unproducible ref; it is one of **59**. And it is not in the class the ruling assigns it to — re-cutting it to empty would have destroyed a correct ref.

## Measured

Recipe, read from the harness rather than from prose — `corpus_suite_harness.py:181` returns `"-q -g halt"`:

```bash
swipl -q -g halt <entry>.pl          # /usr/bin/swipl, SWI-Prolog 9.0.4 for x86_64-linux
```

Master split into its 400 entries by the `%---- <n> <name>` separators, refs split identically from `ALL.ref`:

| population | count |
|---|---|
| master entries | 400 |
| carry `:- initialization(main).` | 203 |
| carry no `initialization(...)` at all **and** have a non-empty ref | 60 |
| …of those, produce **empty output, rc 0** under the stated recipe | **59** |
| …of those 59, reproduce their ref **byte-exactly** once `-g main` is added | **55** |
| …still differing | **4** |

`main` is defined and never called, so the load finishes and `-g halt` exits. The refs were cut by something that ran `main`; the recipe as implemented does not.

## The 4 that `-g main` does not rescue — each gprolog-era, one per cause

- **`146_simple_program_97`** — the entry the ceo ruled on. Its ref is not unproducible; it is the **third `*power*` entry**, pinning gprolog floats. Under run-`main` + swipl 9.0.4 it yields `1024 / 1024 / 1 / 0.5` against the ref's `1024.0 / 1024 / 1.0 / 0.5`. This is ruling **(1)**'s subject (`**`/`^` on integers yield an integer), not ruling (2)'s. Its two siblings were re-pinned in corpus `62dc7995`; this is the one left.
- **`145_simple_program_103`** — ref's third line `bar(x)` needs gprolog-permissive `atom_to_term/3`; swipl raises `atom_to_term/3: Arguments are not sufficiently instantiated`.
- **`239_functor_2`**, **`344_copy_term_ite_list_replace_1`** — refs pin gprolog variable names `_G0`/`_G1`; swipl prints address-derived names (`_5200`, `_7628`) that **vary between runs**. These two are unproducible under swipl by any flag set, not merely mis-pinned.

## ⛔ The cure is the directive, NOT the recipe — measured, because the obvious fix is wrong

Adding `-g main` to the harness recipe **double-runs** the 203 entries that already carry the directive:

```
135_format_directive_1   ref: hello
  swipl -q -g halt          -> hello          (correct)
  swipl -q -g main -g halt  -> hello\nhello   (doubled)
```

So the recipe stays as it is, and the 55 take `:- initialization(main).` — which is exactly the corpus change the ceo's ruling already authorises (*"adding the directive is a corpus change hq_B may make where the family's siblings carry it"*): **203 siblings carry it.** Never a second run mode invented for one entry — and never one invented for 55 either.

## Why this sat unseen, and the shape it shares with the rest of the file

`corpus_suite_harness.py:1316-1326` already carries seat05's guard for this exact signature — *"swipl's `-g halt` fires before/instead of a `:- initialization(main,main)` goal, so the ORACLE produces empty for a whole class of prolog programs that run fine bare"* — and it **refuses to mint an empty ref**. The guard is correct and it is forward-only: it stops the 60th from being written; it cannot see the 59 already committed. A guard against minting a defect is not a census of the defect already minted.

⭐ **The general form, which is this org's recurring one:** the ruling asked *"can the recipe produce THIS ref?"* and got a true answer about one entry. The question that pays is *"how many refs can the recipe not produce?"* — and nothing in the instrument volunteers the difference. Same family as `command -v` answering *is it on PATH* when asked *does it exist*, and `$?`-after-a-pipeline answering for the wrong command.

## Consequence for the board — REPORTED, not a gate claim

The master board grades against these refs, not against a live oracle, so it is internally consistent and **no board number here is wrong**. What is wrong is that 55 of 400 refs cannot be re-derived from the stated oracle recipe, which is the ceo's own criterion for what a ref is. This is a REPORTED observation for `GOAL-PROLOG-100.md`; it blocks nothing and no rung verdict depends on it.

## Exact next step (hq_B, next session — NOT done this session, on Lon's wrap order)

1. Add `:- initialization(main).` to the 55, one commit, proven by the board in the same commit per the INTERIM PROMOTION PROTOCOL.
2. Re-pin `146_simple_program_97` to `1024 / 1024 / 1 / 0.5` under ruling (1) — the third and last `*power*` entry.
3. Route `145`, `239`, `344` to the ceo: three refs no swipl flag set can produce (two of them address-nondeterministic), needing a ruling on re-cut vs. XFAIL.
