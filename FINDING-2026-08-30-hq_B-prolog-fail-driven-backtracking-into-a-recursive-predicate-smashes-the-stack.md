# FINDING 2026-08-30 hq_B — Prolog: fail-driven backtracking into a recursive predicate smashes the stack

**Tree:** SCRIP `520a0138` · corpus `d3f27724` · measured 2026-08-30, seat `hq_B`.
**Lane:** correctness — routed to `hq_C`. This finding mints the witness and draws the boundary; it does
not diagnose.

## Minimal witness (4 lines)

```prolog
:- initialization(main, main).
mem2(X, [X|_]).
mem2(X, [_|T]) :- mem2(X, T).
main :- mem2(X, [a,b]), write(X), nl, fail ; true.
```

```
swipl -q w.pl        -> a\nb          rc=0
scrip --run w.pl     -> a\nb  then  *** stack smashing detected ***: terminated   rc=134
scrip m4 (compiled)  -> (no output)  *** stack smashing detected ***: terminated   rc=134
```

SSP-detected stack buffer overflow — memory corruption, not a clean failure. Both modes abort; **m4 is
worse, producing zero output where m3 emits both correct solutions first.**

## The controls, which are what make this a boundary rather than a symptom

Each removes exactly one ingredient from the witness:

| variant | changed | result |
|---|---|---|
| `mem2(X,[a])` | list of 1 — the recursive clause is never entered | **PASSES**, `a`, rc=0 |
| `f(a). f(b). f(c).` + fail-loop | backtracking, but over FACTS not recursion | **PASSES**, `a b c`, rc=0 |
| `mem2(X,[a,b,c]), write(X), nl.` | recursion, but no fail-driven loop | **PASSES**, `a`, rc=0 |
| predicate renamed `member` → `mem2` | tests builtin redefinition | **NO CHANGE** — still rc=134 |
| `[a,b]` / `[a,b,c]` / `[a,b,c,d]` | list length | **all identical**: `a`, `b`, then abort |

So: **recursion alone is fine. Backtracking alone is fine. Backtracking INTO a recursive predicate
aborts** — and it does so after exactly the first recursive solution, independent of list length. It is
not depth exhaustion and it is not builtin shadowing; the renamed-predicate arm kills that explanation
outright (gprolog refuses `member/2` redefinition, which makes it an attractive but wrong lead).

⭐ The narrow boundary: both solutions are produced correctly and printed. The abort happens on the
**exhaustion backtrack** — the step that should simply fail and fall through to `; true`. The corruption
is in choice-point unwind for a recursive frame, not in solution production.

## How it was found — the part worth generalizing

`corpus/tests/prolog/coverage/coverage_net_gaps.pl` (rc=134) was declared in `PENDING.md` as "crashes
outright" and **flagged DARK by `test_gate_suite_conversion_complete.sh`: declared against a live row and
executed by nothing.** Two consecutive NEXT blocks proposed granting it a gate exemption.

Both the exemption and the DARK verdict were wrong, in opposite directions:

- The DARK verdict was a **false positive** — the file is #2 of the 45 that `test_corpus_prolog_parser.sh`
  sweeps (green, and the coverage manifest's own GATED harness for `tests/prolog`). `gate_reachable()`
  greps for the basename, the corpus-relative path, and the file's own directory; that runner names only
  the tree root and recurses with `find`. Cured in SCRIP `520a0138`.
- But the file **is** genuinely broken, and the parser gate could never have said so: it grades
  `--dump-ast`, which parses and never executes. A file can be perfectly reachable by one instrument and
  completely untested by the one that would have caught its defect.

⭐⭐ **"Reached" and "tested" are different questions, and a reachability check cannot tell them apart.**
The DARK check asks whether *anything* runs the file. Here something did, for a whole session, while an
SSP abort sat inside it. Coverage-by-any-instrument is the weakest possible reading of covered, and it is
the reading a path-grep necessarily gives.

## Related

`prolog-abolish-leaves-predicate-defined-but-empty` (seat06, separate defect, same tree);
`prolog-backtracking-yields-first-solution-only` — plausibly the same family as this one, **unverified**,
and worth checking early since a shared cure would close several deferrals at once.
Row for the crash class: `tests-consolidate-prolog-pz4-blocked-33` lists 30+ files at rc=134/139; this
witness may cover more of them than the one it came from.
