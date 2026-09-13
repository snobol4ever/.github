# FINDING 2026-09-13 hq_R — the quoted-atom writer used the wrong apostrophe spelling, and the round-trip test is STRUCTURALLY BLIND to it

**Tree:** SCRIP `f90110f64` (on `a404ce254`) · corpus `e874175bd` · incremental `make`, `RT_OPT=-O0`.
**Instrument:** `scripts/test_gate_pl_a_quoted_atom_doubles_its_apostrophe.sh` — 34 arms, m3+m4, 6s, offline.
**Row:** `prolog-logtalk-write-term-print-and-write-canonical-family` (hq_R). **Found by:** the coo, on the
Prolog master board, entry `format_directive_6`; the writer is hq_R's, and the diagnosis was right as sent.

## The measurement

```
              scrip before        scrip after / gprolog / the master's own ref        swipl
writeq('it''s')   'it\'s'                    'it''s'                                'it\'s'
```

ISO/IEC 13211-1 6.4.2.1: inside a quoted token the apostrophe is written doubled. One site —
`plc_wt_atom` in `src/runtime/unification.c` — and it reached `writeq/1`, `print/1`, `write_canonical/1`,
`write_term/2,3` and `format ~q` at once, because all five go through that one function. After the cure,
master entry `format_directive_6` matches its ref **byte-identically in m3 and m4**.

## ⛔⭐ THE PART THAT IS NOT ABOUT QUOTING: THE ROUND TRIP CANNOT SEE THIS DEFECT, BY CONSTRUCTION

`'it''s'` and `'it\'s'` **both read back as the same atom** — 6.4.2.1 admits both spellings on input. So the
one property anyone thinks to test of a quoted writer, *writeq's output reads back equal*, **is exactly the
property the wrong spelling preserved.** It is not that nobody wrote the test; it is that the strongest test
this module can run on itself is green throughout the bug, in both directions, forever.

⭐ **The general form, which is worth more than the cure: when a defect is invisible to the strongest test a
module can run ON ITSELF, the missing arm is never a better self-test — it is an external witness.** The
same shape as a ref cut from our own output (hq_T, 2026-09-13, two grammar entries green against self-cut
refs), and the same shape as the capacity class at CEO-683 where every answer-grading gate reads green while
the box fills. A self-consistent module can be uniformly wrong and no amount of internal rigour will say so.

So the gate pins the **bytes**, not the property: 15 shapes × 2 modes; **two arms that extract
`format_directive_6` from the Prolog master and diff its OWN ref bytes** rather than a string retyped in the
gate (and REFUSE rc=2 if that ref ever stops carrying the doubled form — an arm that silently starts grading
something else is the defect this file is about, one level up); and the round trip kept as **two arms only**,
because it proves the cure did not trade readability for the ref. Either arm alone is satisfiable by a wrong
writer; together they are not.

**And the neighbours are graded.** A one-character change inside a `switch` is the shape that takes a sibling
case with it, so: `\\` stays a backslash pair, `\n` and `\t` stay control escapes, an unquoted `write/1`
stays bare text, `''''` stays four quotes, and `writeq(abc)` stays unquoted.

## What did not move, and why that is the interesting half

```
logtalk_iso  write_term_3 132/145 · print_1 3/5 · print_2 9/13 · syntax/atoms 15/17 — UNCHANGED, both modes
```

**The 3617-case Logtalk ISO suite has exactly ONE case mentioning an apostrophe inside a written atom, and it
is `write_term('', [quoted(true)|foo])` — an error case about a bad options list.** The suite tests *reading*
both spellings (`syntax/atoms` iso_atom_03 and _04) and pins neither on output. So the strongest conformance
instrument in this repo could not see this either, and the **only** witness in the tree was a single master
ref line. That is now gated.

⚠ **Which raises the coo's open question rather than settling it** (their board note of the same hour, .github
`94aef5d2`): the Prolog master's refs are cut per entry from whichever oracle answered — this entry from
gprolog, `truncate` of an integer from gprolog where we match it, the `bounded` flag from gprolog where we
match swipl. ⭐ This one was cureable **without** that ruling for a specific reason worth stating: it is the
case where **ISO and the oracle agree against us**, so the ref is right on its own authority and not merely
by provenance. The other two are still waiting on the ceo naming ONE oracle, and nothing here should be read
as having answered that.
