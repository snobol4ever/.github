# rung10 (pattern alternation) FORMS complete; a nested-alternation capture bug, and the book's bare-function gate example does not work as printed

**seat09, 2026-09-05. MODE `FLEET-20`. Lane hq_P. Row `snobol4-ladder-every-feature-in-isolation-with-variations`, rung10.**

## 1. rung10 FORMS complete, 5 of 6 green

SPITBOL manual pp.57-60 ("Pattern Subsequents and Alternates" + its "Pattern factoring" subsection) read
in full. This citation is exactly and completely bounded — p.57 opens right after the short "Subject
String" section, p.60 ends exactly where "Simple Pattern Matches" begins as a genuinely new topic — so
unlike rung09 this range needed no correction. Minted 6 new witnesses alongside the pre-existing base
`ladder__rung10_pattern_alternation` (7 total): `alternation_looser_than_concatenation`,
`parens_override_alternation_precedence`, `null_alternative_optional_suffix`,
`conditional_function_gate_in_alternation`, `nested_alternation_pattern_factoring`,
`backtrack_retries_alternative_on_downstream_failure`. All 6 refs oracle-cut from `sbl -bf`, `scrip --run`
(m3) **and** `scrip --compile` (m4) cross-checked before absorbing. `test_snobol4_ladder.sh --only 10`:
PASS=12/14 (7 witnesses × 2 modes, the 2 FAIL being exactly one deliberate red below, both modes).
`--to 10` regression floor: PASS=150/152 clean, no new regressions (the previously-documented rung04 red
stays cured, unchanged from seat16's session). `util_ladder_forms_check.py --phase isolation`: 76/86
(rungs 00-10 complete; rungs 11-16 correctly still MISSING/unstarted, rungs 17-23 TRACE forms out of this
row's scope). Discriminating power spot-checked on `alternation_looser_than_concatenation` against a
hand-corrupted `/tmp` copy of its ref (`BC`→`ZZ`) — `scrip`'s real output correctly mismatched.

Five of the six forms are direct or lightly-adapted instances of the book's own worked material
(precedence with/without parens p.58, the null-alternative ROOT example p.59, the COMP/COMPATIBLE
factoring example p.60). `backtrack_retries_alternative_on_downstream_failure` is assembled (no single
runnable book example) from the book's own prose ("If a subsequent fails to match, SPITBOL backtracks,
unbinding patterns until another alternative can be tried", p.59) — `("AB"|"A") "B"` against subject `"AB"`
forces a real backtrack out of the greedy `"AB"` alternative into the shorter `"A"` alternative, proving
genuine per-alternative backtracking rather than mere first-alternative-wins; it stands as the natural
counterpart to rung12's FENCE, which will later suppress exactly this backtracking.

## 2. SCRIP bug: outer capture drops its prefix through a NESTED alternation

`nested_alternation_pattern_factoring` reproduces the book's own p.60 example verbatim —
`'COMP' ('AT' | 'RE' ('HEN' | 'S') 'S') 'IBLE'` matched against COMPATIBLE/COMPREHENSIBLE/COMPRESSIBLE —
and SCRIP gets the first case right but mangles the other two:

```
$ ./scrip --run ladder__rung10_nested_alternation_pattern_factoring.sno
COMPATIBLE
REHENSIBLE   <- oracle says COMPREHENSIBLE
RESSIBLE     <- oracle says COMPRESSIBLE
no match
```

Ablated to a minimal repro (both `scrip --run` and `scrip --compile` reproduce identically, rc=0 in both —
wrong output, not a crash or FATAL):

```
 PAT = "COMP" ("AT" | ("HEN" | "S")) "IBLE"
 X = "COMPHENIBLE"
 X PAT . CAP
 OUTPUT = CAP
END
```
SCRIP: `HENIBLE`. Oracle: `COMPHENIBLE`. A control ablation proves the trigger is specifically a **nested**
alternation, not merely "the second alternative has more than one component":
`"COMP" ("AT" | "RE" "S") "IBLE"` (second alternative is a plain 2-literal concatenation, no nesting)
matches the oracle exactly in both modes. Only when the winning branch is itself an alternation
(`("HEN"|"S")`) does the outer capture lose everything matched before that branch — the first
alternative (`"AT"`, no nesting) captures its prefix correctly every time.

This looks like the same *family* of defect as hq_C's just-cured
`snobol4-outer-capture-over-a-group-containing-a-pattern-valued-variable` (origin `0a1a94239`, referenced
in rung09's own `outer_capture_over_pattern_valued_variable_group` witness, which confirmed that fix from
the ladder's own angle) — an outer capture's span getting corrupted when the matched branch has
non-trivial inner structure — but this reproduces **after** that fix and the triggering shape is nested
**alternation** specifically, not a pattern-valued-variable group, so it is either a sibling gap the same
fix did not cover, or a related regression. Not this row's to fix (isolation-forms walker, no `src/`
edits). Routed as a class row to **hq_U** (shared engine, per FLEET-20's THE 20-SEAT CUT — the previous
16-seat cut would have named hq_C, but hq_C is Prolog-only under the current cut), not hq_P's own lane,
since the defect sits in shared BB/IR pattern-capture machinery (`bb_match_capture.cpp` /
`bb_match_alternate.cpp` are the likely owners, both linked into every language's runtime, not SNOBOL4-only):
`snobol4-nested-alternation-drops-outer-capture-prefix` (rank 2). The witness stays in the master RED,
never xfailed (THERE IS NO XFAIL) — the absorb tool auto-marked it `xfail=True` as every prior red-witness
rung has found; hand-reverted per the established recipe (`ALL.csv` column 1→0, `" XFAIL"` suffix stripped
from both `ALL.sno` and `ALL.ref` banners, dash-count recomputed with the same formula rung04/05
documented, verified byte-equal via `master_extract_origin` after the fix).

## 3. Book/oracle divergence: the literal gate-function example does not work at all

p.59-60 states: "These functions behave like a gate ... This pattern will match 'FOX' if N is 1, or 'WOLF'
if N is 2: `EQ(N,1) 'FOX' | EQ(N,2) 'WOLF'`" — printed with **bare**, non-deferred function calls. Tested
literally against the oracle (not SCRIP — this is a real-SPITBOL semantic fact, confirmed twice,
independently, in both directions):

```
 N = 1
 X = "FOX"
 X (EQ(N,1) "FOX" | EQ(N,2) "WOLF") :S(OK1)F(BAD1)
OK1  OUTPUT = "N1-matched"
 :(L2)
BAD1 OUTPUT = "N1-failed-statement"
L2 N = 2
 Y = "WOLF"
 Y (EQ(N,1) "FOX" | EQ(N,2) "WOLF") :S(OK2)F(BAD2)
OK2  OUTPUT = "N2-matched"
 :(END)
BAD2 OUTPUT = "N2-failed-statement"
END
```
`sbl -bf` output: `N1-failed-statement` / `N2-failed-statement` — **the statement fails for both values of
N**, not just the "wrong" one. Root cause (confirmed by isolation): a bare function call embedded in a
pattern literal is evaluated **eagerly, once, at pattern-construction time** — like any ordinary SNOBOL4
expression — not re-evaluated per match/backtrack attempt. Building the alternation
`EQ(N,1) "FOX" | EQ(N,2) "WOLF"` as a value requires evaluating **both** operands of `|` up front; whichever
`EQ(...)` is false at that moment **fails as an ordinary function call**, which fails the whole enclosing
statement before any subject-scanning begins — regardless of which alternative "should" apply. A single
bare gate in isolation (no second function-bearing alternative) is indistinguishable from true deferred
"gate" semantics in a non-backtracking test, which is why earlier isolated probes of `EQ(N,1) "FOX"` alone
looked correct; the failure only appears once a second alternative also carries a function call.

The construct that actually delivers the book's stated semantics is the `*` (unevaluated-expression)
prefix, which defers evaluation to match time:

```
 X (*EQ(N,1) "FOX" | *EQ(N,2) "WOLF") . CAP    -- N=1 -> CAP="FOX"; N=2 (Y="WOLF") -> CAP="WOLF"
```

Oracle-confirmed working exactly as the book describes, both values of N, including the correct
per-alternative (not whole-statement) failure when neither gate/text pair matches. The minted witness
`conditional_function_gate_in_alternation` uses this corrected form and is GREEN both modes. Not filed
as a SCRIP defect — this is a property of real SPITBOL itself (verified against the oracle only, `scrip`
was not even in the loop for this half), most likely because the tutorial's prose assumes familiarity with
`*` from elsewhere (Ch4 "Control Flow and Functions" is cross-referenced by this very paragraph) and prints
the simplified bare form for readability. Worth flagging for whoever next reads this chapter: `*`
(unevaluated expression) itself has no declared rung anywhere in `LADDER.tsv` (checked rungs 00-23) — a
census gap in the same spirit as rung09's flagged "@" and primitive-pattern-function gaps, not this row's
to fix (isolation forms for already-declared constructs, not declaring new ones).

## Session wrap

Row left OPEN (not `done`, not `park`'d — no blocker, straightforward continuation, DONE-WHEN unmet:
rungs 11-16 still need their base construct AND forms). See the task baton's `## NEXT` for the rung11
(ARBNO) continuation. Pushed SCRIP (sync only, no source changes — build was a plain incremental `make`
after pulling 2 commits) / corpus (`tests/snobol4/{ALL.csv,ALL.sno,ALL.ref,config/LADDER.tsv}` + the 6 new
loose witness pairs deleted post-absorption) / .github (this FINDING) after `git pull --rebase` clean on
all three at session start.
