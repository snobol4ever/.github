# FINDING 2026-09-12 hq_C — a KEEP.md retraction re-declares the very files it retracts

**Row:** `rebus-absorb-…-census-reads-zero` / the CEO-607 abolish half. **Trees:** corpus `bc3fe44bb`,
SCRIP `55aaa01ad`. **Ruling acted on:** CEO-607 — *"kept loose is not the answer — under no-XFAIL a faulty
test is FIXED AGAINST ITS ORACLE."*

## 1. THE DECLARATION AND ITS RETRACTION ARE THE SAME STRING TO THE MATCHER

`_declared_in_keep` (`util_build_master_suite.py`) resolves a keeper by `_delim_match` — a delimited
substring search **over the entire text of KEEP.md**. It has no notion of sections, headings, or tone.

So when CEO-607 overruled a keeper declaration and I went to replace it with the usual honest record —
*"these three were declared keepers on 2026-09-12; that was wrong, here is why, they are now absorbed"* —
**that paragraph would have kept all three out of the master**, silently, while reading to every human as
the opposite. The retraction is a declaration.

⭐ **The general form: a matcher that reads a whole file cannot distinguish a claim from a discussion of
that claim.** Every convention where "the file mentions the name" IS the assertion has this property, and
the hazard surfaces exactly when someone tries to be diligent — nobody deletes history without a note, and
the note is the bug. Documented in the KEEP.md itself, which now names no basenames at all and points here.

⛔ It is the twin of the lesson already in that file: a **brace-expanded** heading
(`rung15_abolish_abolish_{existing,one_of_two,then_query_fail}.pl`) reads perfectly and declares NOTHING.
The two failures are opposite in sign — one under-declares, one over-declares — and **both look correct on
the page.** Only `_declared_in_keep(path, root, {})` answers the question; the prose never does.

## 2. A HAND-CUT REF IS NOT THE HARNESS'S CUT, AND THE DIFFERENCE IS INVISIBLE

Cutting the three refs the obvious way — `swipl -q $f > $f.expected` — produced refs that **both SCRIP
modes read FAIL against**, after I had measured all four implementations agreeing by eye minutes earlier.

The cause: `swipl -q` **falls through to the toplevel**, hits EOF on stdin and emits a **trailing newline**
that the program never wrote. `resolve_oracle_bin`'s own docstring records this, and
`cmd_capture_oracle_refs` strips it with `.rstrip("\n")` — the one place in the tree that knows. Cut by
hand, the ref grades the oracle's *toplevel behaviour* alongside the program's output.

⭐ **"Never reimplement the shared authorities" is usually taught as duplication hygiene. This is the
sharper reason:** the authority's value was never the code, it was the *accumulated knowledge of what the
oracle does besides answering* — and that knowledge is invisible at the call site. My re-implementation was
three characters shorter and looked identical. `cmd_capture_oracle_refs` cut it correctly and reported
`GREEN (m3=AGREE m4=AGREE)` in the same breath — the measurement MODES.tsv wanted, for free.

⛔ **AND THE BAD REF HAD ALREADY BEEN PINNED.** The builder had absorbed it, and on the next run it said
*"already in the master … NOT re-appended"* — **merge-never-replace means a wrong entry is durable.** The
loose pair then read UNVERIFIED, which names the symptom (they disagree) and not the direction (the MASTER
is the stale half). The recovery is to revert the master and absorb once from corrected refs; there is no
"re-absorb" verb. A first absorption is therefore worth more scrutiny than its reversibility suggests.

## 3. THE WITNESSES WERE VACUOUS, AND THE GATE THAT GRADED THEM WAS GREEN

All three `.expected` files had been **0 bytes since 2026-09-01**, because the sources carried **no entry
point** — no `:- initialization(main).`, so `main` never ran under `swipl -q`. `test_prolog_rung15.sh`
compared empty output to an empty ref and printed **PASS**. Three vacuous greens, for eleven days.

⛔ The board could not have caught it: **a vacuous pass and a real pass are the same cell.** What caught it
was a ruling forcing someone to ask what the witnesses *assert*.

Fixed against the oracle: setup moved into the initialization goal (which also cures the gprolog half —
load-time `:- assertz(…)` is an unknown directive there, so nothing existed to abolish, a **fixture fault
and not evidence about Prolog**), and the assertion is now the exact ISO error term via `catch/3` —
`existence_error(procedure,fact/1)` — which is stronger than matching swipl's implementation-specific
English prose and is **byte-identical under swipl, gprolog, SCRIP m3 and SCRIP m4**.

⭐ Asserting the error **term** rather than the oracle's **message** also sidesteps a ref that cannot be
shared: the uncaught form's stderr embeds the source file's **absolute path** — measured, even when invoked
by bare name from its own directory — so a stderr-cut ref for these would have passed in one seat's root and
failed in every other. Worth knowing before the `ALL.err` row wires stderr assertions.
