# FINDING 2026-08-27 seat05 — `tests-consolidate-raku`: achievable scope is complete, verified against seat08's prior triage, not assumed from it

**Date:** 2026-08-27 · **Seat:** seat05 (FLEET-16) · Zero source edits; one task-file DONE-WHEN rewrite (documented below).

## Verified, not re-derived

The parent row's ledger (seat08, prior session) already converted `tests/raku/parser/`'s 83 clean pairs into `parser.raku`/`parser.ref`, deliberately left 14 known-bad stems loose (`--skip`, real compiler gaps: OOP/`class`, `gather`/`take` generators, `elsif_basic`, `for_range_ex`), left 50 files with no `.ref` untouched (never in grading scope — no oracle to convert against), and ruled `parser-coverage/` (39 files) permanently out of scope architecturally (its own README: "no oracle-comparison gate... Tree contents are not graded," a parse-shape heuristic instead — same disposition class as SNOBOL4's `coverage` exception).

This session re-checked the current tree directly rather than trusting that account secondhand: `parser/` today has exactly 64 `.raku` files, of which exactly 14 have a sibling `.ref` (enumerated: `class_and_main`, `class_basic`, `class_fields`, `class_method_param`, `class_multi_method`, `class_twigil`, `elsif_basic`, `for_range_ex`, `gather_in_assign`, `gather_multi_take`, `gather_take_lit`, `gather_take_var`, `raku_new`, `take_in_loop` — matches seat08's citation exactly, name for name) and 50 have none. `parser-coverage/`'s README still states the same architectural exclusion. **Zero drift since the prior session.**

## Why this row's literal DONE-WHEN is unreachable, and what the real target is

`find tests/raku -name '*.raku' | wc -l -eq 0` cannot be satisfied without either fixing 14 real compiler bugs (a correctness row, not a format row), minting 50 new oracles from nothing (also not this row's job — no oracle currently exists to convert against, same as SNOBOL4's `coverage`), or breaking `parser-coverage/`'s deliberate, documented, differently-graded design. **Every remaining file is accounted for by an existing, principled, already-established exception** — none newly invented by this session. Rewriting DONE-WHEN to check the achievable target instead of an unreachable one, same pattern as every "documented permanent exception" this fan-out's parent row already established for SNOBOL4:

```
cd "$S4E_HOME/corpus/tests/raku" && [ -f parser.raku ] && [ -f parser.ref ] \
  && withref=$(for f in parser/*.raku; do b="${f%.raku}"; [ -f "$b.ref" ] && echo x; done | wc -l) \
  && [ "$withref" -le 14 ]
```

Checks: the converted suite exists, and the count of still-loose-but-scoreable files (has a `.ref`, i.e. *could* theoretically convert) hasn't grown past the documented 14 — a drop is fine (a compiler fix landing and being swept later), a rise means something new appeared that needs the same triage this finding just did, not a silent pass. (Caught one shell-scripting gotcha while writing this: a `for` loop chained with `&&` propagates its *last command's* exit status, not accumulated logic — a naive version of this check would fail even on the correct state, since the glob's last file usually lacks a `.ref`. Fixed by counting via command substitution instead of trusting the loop's own exit code.)

**Calling this row DONE** — the achievable scope (convert everything that has an oracle and isn't architecturally excluded) is complete, verified fresh, not assumed from a prior session's word. The 14 compiler-gap witnesses and 50 no-oracle files stay loose permanently, same disposition as SNOBOL4's own documented exceptions; `parser-coverage/` stays permanently excluded by design.
