# FINDING 2026-09-01 seat05 — the Prolog "no main BB graph" fatal is TWO independent defects sharing one symptom, and the dominant one is the arm nobody had scoped

**⭐ HEADLINE: `[IBB] FATAL: main BB graph not found` (m3 rc=134 + core dump, m4 rc=1) is not one bug. It is two,
with unrelated causes, reaching the same NULL through the same line — and the larger of the two is the
CLAUSE-ONLY file, which is ceo's dominant class (~139 of 371 master-suite entries, 37%) and which the row's own
suggested cure direction did not address at all.** Row `prolog-directive-only-file-fatals-no-main-bb-graph`
(rank 0). Cured and pushed: SCRIP `3ce7a526`.

## The two defects

Both end at the same place: `lower_pl_stage2()` (`src/lower/lower_prolog.c`) leaves its local `clause` NULL, so
nothing is registered as main, and the driver aborts at `scrip.c:1863` (m3) / `:1392` (m4).

**(a) DIRECTIVE-ONLY — an allowlist, not a lookup.** `prolog_lower.c` wraps a bare `:- Goal.` into a
`pj_dir_<N>` helper plus `initialization(pj_dir_<N>)` **only for a closed list of goal names** (`begin_tests`,
`end_tests`, `dynamic`, `use_module`, `module`, `ensure_loaded`, `discontiguous`, `meta_predicate`, `nb_setval`).
A goal outside that list is never wrapped, so it never becomes an `initialization(...)` statement and never
reaches the accumulator in `lower_pl_stage2()`, which matches only `initialization`.

**(b) CLAUSE-ONLY — THE DOMINANT ARM, AND STRUCTURALLY OUTSIDE (a)'s CURE.** A file with no directives at all and
no `main/0` has **no helpers to synthesize from**. The row's stated direction — *"a file with no main/0 needs a
synthesized main/0 whose body is those helpers in source order"* — is correct for (a) and a no-op for (b).
⭐ **This is the arm that matters most, and it is the one that reads as already-handled if you only look at the
directive machinery.** Every witness ceo sampled (`simple_assign_3` = `foo(X,Y) :- X @>= Y.`, `simple_program_2`,
three more) is this arm. Its cure is a synthesized `main :- true.`, unrelated to (a)'s.

**(c) A third, smaller defect found en route — a silent drop.** `if (!b) continue;` in the body-build loop.
`pl_init_resolve_body()` resolves a goal NAME to a user clause's body: right for `initialization(main)`, NULL for
a bare directive (`write/1` is a builtin and owns no clause row) and NULL for `initialization(undefined_pred)`.
Both vanished at compile time. A goal that resolves to no clause body **is** its own body; an unresolvable one now
falls into the pre-existing warn-and-continue arm (warning names the goal, exit 0), which is what swipl does.

⭐ **No new globals.** (c)'s resolve-fallback is precisely what avoids needing a parallel is-directive flag array,
which was the obvious and forbidden design.

## Reference behaviour, measured — the oracle, not an assumption

`foo(X,Y) :- X @>= Y.` → swipl rc=0, **no output**. `:- write(hello), nl.` → swipl rc=0, prints `hello\n`.
Post-cure: clause-only rc=0 with output byte-equal to swipl in **both** modes; directive-only rc=0, no abort, no
FATAL, both modes. `rc=134` no longer occurs on either witness in either mode.

⛔ **The `139` is NOT claimed cured.** The Prolog master re-run died under contention, so the board delta is
UNMEASURED and must be read from the harness before anyone states a number.

## ⛔ A SECOND CLASS SURFACED BEHIND THE FIRST, exactly as ceo predicted — and it is parser-side

A bare `:- A, B.` directive **loses every conjunct after the first, at parse time**, upstream of all lowering:

```
$ scrip --dump-ast  ':- write(hello), nl.'
(STMT :subj (TT_FNC write (TT_QLIT "hello")))          ← the `, nl` is simply absent

$ scrip --dump-ast  'main :- write(hello), nl.'
(STMT :subj (TT_CHOICE main/0 (TT_CLAUSE (TT_FNC write ...) (TT_QLIT "nl"))))   ← both goals present, runs
```

So the defect is specific to **bare-directive goals**, not to conjunction. With the abort cured,
`:- write(hello), nl.` now prints `hello` (5 bytes) where swipl prints `hello\n` (6) — the missing newline is the
dropped `nl`. Not curable in `lower_prolog.c`; hq_C's lane.

## ⛔ A CORRECTION TO MY OWN CAUSAL CLAIM — two different failures print the same sentence

`3ce7a526`'s commit message attributes its `make test` refusal (*"harness produced no SUITE_BOARD line for the
master suite"*) to the documented single-call cap (row `corpus-runner-master-suite-exceeds-single-call-cap`).
**That attribution is probably wrong and I am correcting it here, since a pushed commit message cannot be
amended.** ceo's all-hands relay reports a box-wide `pkill -f corpus_suite_harness.py run` at ~18:28 CDT that
killed 19 harness processes belonging to other seats. My run is timestamped **18:25:53 CDT** — in flight, three
minutes ahead of the kill. It was almost certainly **killed, not capped**.

⭐ **The lesson is the one this project keeps paying for: the cap and the kill emit the BYTE-IDENTICAL refusal, so
the message cannot distinguish them, and the cap being real, documented and cited made the wrong cause feel
confirmed.** The procedure I took was right either way (re-run directly; it returned
`SUITE_BOARD family=ALL total=1726 m4_pass=1649 m4_fail=0 … m4_xfail=70 m4_xpass=7`, green). Only the explanation
was wrong — the "correct procedure with a false explanation" shape. A refusal that cannot name which of two
causes fired should say so, or carry a discriminator.

## Loose ends, routed not dropped

- 7 m4 `XPASS (marker stale, promote it)` entries from the floor run → routed to hq_C by name (they promoted five
  markers in the same fence/arbno replace-branch family earlier today). Reported **unattributed**: no pre-change
  baseline exists on this tree, so they are neither claimed pre-existing nor claimed mine.
- The floor was measured **mode 4 only** (`--modes m4`, the hard gate; m3 informational). m3 was not run on the
  master suite, and that limit is stated rather than left to inference.
