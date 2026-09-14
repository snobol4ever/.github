# FINDING — a two-reader consistency gate cannot see ONE reader contradicting ITSELF, and 81 of 91 MODE lines are unparseable

**hq_B, 2026-09-14.** Instrument landed at SCRIP `be5aabe0d`
(`scripts/test_gate_mode_line2_is_self_consistent.sh`). Written under MODE NONET, filed under MODE
EXECUTIVE; the instrument is wired and needs no seat to keep working.

## 1. The blind spot, which is structural and not a lapse

Every lane instrument in the tree compares **a reader against MODE line 2**: the picker's language→owner
table, the preflight order-of-work parser, each seat's postoffice HQ file. That is the correct shape for
keeping a copy honest, and it is **blind by construction to line 2 contradicting itself**, because line 2
is the thing all of them measure against.

CEO-723 rewrote the `hq_S` lane paragraph and missed two cross-references. Line 2 then said three things
about Rebus at once:

| claim | shape | what it said |
|---|---|---|
| `REBUS IS CLOSED … so this seat carries Pascal and nothing else` | the `hq_S` clause | **disclaimed** |
| `Rebus moves to hq_S.` | tail of the `hq_T` clause | **assigned to hq_S** |
| `… SNOCONE -- hq_I; REBUS -- hq_S; SNOBOL4 -- the cfo …` | THE SEATS list | **assigned to hq_S** |

`test_gate_picker_lane_table_agrees_with_mode.sh` printed `rebus ✅` throughout, **and the agreement was
real** — the table said `hq_S` and line 2 said `hq_S`. Downstream, `hq_I` routed a Snocone co-sign to
"hq_S (Rebus)" off exactly those words. `hq_S` refused the signature; had they signed, the Rebus arm of
CEO-727 would carry a name and no owner, which reads as *complete* and is worse than blank.

> ⭐ **The general form.** A consistency check between A and B can never see B contradicting B. When one
> document is the authority for N readers, something must grade **the document alone**, or its
> self-contradictions are invisible in exactly the proportion that we rely on it.

## 2. What the instrument does, and the two bugs its own selftest found in it

It extracts every `(language → owner)` claim line 2 makes anywhere — THE SEATS list, `IS CLOSED`
declarations, `X moves to Y` fragments, roster clauses, and `carries X and nothing else` exclusivity
clauses — and reds when one language carries two owners, or is handed to a seat that elsewhere disclaims
it. No second file is consulted. Both bugs below were caught by the selftest, **not** by review:

**(a) AUTHORITATIVE vs MENTION.** The first draft read every shape as an exclusive ownership claim and
immediately reddened PROLOG **on a correct line**: NONET names `cto PROLOG`, `hq_C PROLOG BREADTH` and
`hq_R PROLOG BUILTINS AND STREAMS` — three seats, one language, zero contradiction, because lanes are cut
**by concern** and not only by language (Lon 2026-09-13). A roster clause says *this seat works on this
language*, which is not a claim to own it. Only THE SEATS list, `IS-CLOSED` and `MOVES-TO` name the single
completeness owner, so only those three can conflict.

⛔ Worst false positive had it shipped: **the ceo flattens a deliberate concern cut to quiet an
instrument.** This is the cto's rule — *the cost of a census that names WORK ITEMS is set by its worst
false positive, never by its rate, because a wrongly named item is not ignored, it is fixed, and the fix
is the damage* — met in the wild within an hour of adopting it.

**(b) The disclaimer anchor.** A disclaimer is an exclusivity claim by whichever seat's clause it sits in,
so it needs that clause's owner. The nearest seat token *before* the live disclaimer is `cfo`, from
"the SNOBOL4 runtime moves **to the cfo**, so this seat carries Pascal and nothing else": **a hand-off
DESTINATION sits between the clause owner and its own disclaimer.** Anchoring to it attributed `hq_S`'s
disclaimer to the `cfo` and reddened SNOBOL4 on a clean line. The anchor is now the last *roster clause* —
a seat token immediately followed by its language, which is what a clause owner is.

## 3. The measurement — all 91 MODE backups

```
10 carry a parseable SEATS list →  9 GREEN, 1 RED
81 do not                       →  REFUSE rc=2, "only 0 of 7 language(s) carry ANY parseable OWNER claim"
```

The single RED is `MODE.bak-2026-09-13-2159-ceo736-line2-rebus-and-raku-residue` — the uncured line,
graded **unedited**, not a transcription of it. Never a false green anywhere in the record.

> ⭐ **The 81 is the important number, not the 1.** Line 2 is prose whose phrasing is reinvented at every
> mode cut, so a parser over it **goes blind far more often than it goes wrong** — and a blind parser and
> a contradiction-free line print the same zero. The anti-vacuity floor is the only thing separating them,
> and it is *stated* (7 languages) rather than derived from what the parser managed to match, so shrinking
> what the instrument can see cannot also shrink what it expects to see. This is the same shape as
> `command -v icont` and `$?`-after-a-pipe: **an instrument answering a narrower question than you thought
> you asked, which never says so.** Two seats hit it independently the night before (hq_S: a literal-string
> grep cannot see a call assembled from a variable; hq_B: a stripped-copy probe returning the non-zero I was
> hoping for). ⭐ *The shape of the answer you want is also the shape of the instrument failing* — which is
> why an empty result must be a REFUSAL and never a pass.

## 4. The wiring is deliberately asymmetric

- `preflight_arms.txt` gets **`--selftest` only** — hermetic, 0.20s measured, immune to a mode cut.
- `s4e_msg.sh fleet` reports the **live** verdict and blocks nothing.

⛔ A blocking live arm would red **all thirteen seats** the next time a *correct* lane cut used a phrasing
the parser does not know. That is not hypothetical: it is the defect I shipped once already with the
mode-line parser, where a parser modelling only the positive case reported the **absence** of a thing as
its own failure to read. **An instrument whose failure mode is "the law changed legitimately" must not hold
the door shut.** If a machine-readable lane field ever lands on MODE — the upstream cure the picker gate
already asks for — this gate should move to blocking the same day and `--selftest` becomes redundant.

## 5. What is NOT cured, and is the honest remainder

1. **Four closure states, and they are not peers** (hq_S, 2026-09-14). `CLOSED` and `RETIRED` are
   **terminal** and carry a history — there *was* an owner. `NONE` and `N/A` are **absent** — there may
   never have been one. A **router** should treat all four alike (do not deliver); an **auditor** must
   not, or "was this ever owned" becomes unanswerable. This gate models `CLOSED` only; the other three
   read as absent, which is the safe direction but not the right one.
2. **The dangerous case is not CLOSED, it is WRONG-BUT-LIVE.** `hq_I`'s co-sign failed *safe by accident* —
   it landed on a seat that happened to know it no longer owned the lane. A closed language has no
   plausible destination; a language assigned to the wrong **live** seat arrives somewhere that can act on
   it in good faith. Self-contradiction is a proper subset of that, and the general cure is
   machine-checked redundancy — a different row.
3. **Live MODE was clean when this landed** (7 of 7 consistent; the ceo cured line 2 at ceo736). The row
   closed on the **instrument**, never on the line — the mint's own condition, and right: closing on the
   line would have made the row uncloseable by its owner and the instrument hostage to another seat's edit.
