# FINDING 2026-09-05 seat03 — Icon Arizona suite: fresh census confirms board unmoved, two witnesses advanced

Session on `icon-arizona-suite-49-reds-censused-by-class-and-cured` under FLEET-20 (hq_B/Icon lane).
MEASURE FIRST per the row's own law: rebuilt (incremental, `make -j4 scrip` + `make libscrip_rt`),
re-ran the suite fresh rather than trusting the ledger, given today's heavy hq_B-lane Icon corpus
restructuring (LADDER.tsv/MODES.tsv rewrites, jcon_tests ALL.* deletion) had already re-cut this row's
own STRICT-rung literal seven times for reasons outside any session's own work.

## 1. Board reconfirmed, unmoved

`ARIZONA_SUITE_BOARD shipped=124 graded=89 gap=35 m3_pass=45 m3_reject=0 m3_fail=44 m4_pass=45
m4_reject=0 m4_fail=44` — identical to session 7's final reading. Unlike the STRICT-rung suite and
Icon master board (both hit by today's corpus restructuring), the Arizona suite's own denominator did
not move. DONE-WHEN (m3_pass>=50) still not met.

Housekeeping: the suite's own run drops `foo.baz` (checkc.icn/fncs1.icn) and `tmp3` (iobig.icn) as
untracked files in `corpus/packages/icon/arizona_tests/general/` every time it runs — this blocks the
SCORE.md row from landing ("corpus has uncommitted"). This is NOT new corpus damage; it is the same
class of issue `corpus/.gitignore`'s own ICON I/O-TEST SCRATCH comment already documents for the old
rung-suite location: `test_icon_arizona_suite.sh` is one of the "~5 sibling graders [that] still run
from the corpus CWD and are not yet converted" to the scratch-cwd+absolute-path pattern
`test_icon_all_rungs.sh` already adopted. Per that same comment, a bare `.gitignore` entry is
explicitly the wrong fix ("a net... while the writer lives") and removing tracked content is ceo's
call — so this session did not touch it, just manually removed the droppings before each of its own
suite runs and flags the conversion as still outstanding for whoever owns that queue.

## 2. `tprintf.icn` recount — confirmed, no new win

Per session 6/7's own flagged cheapest-lead, recounted fresh now that the `*`/size() precision fix is
in: the residual diff is exactly the already-scoped `icon-arizona-class-bignum-not-implemented` class
— `%d`/`%o`/`%x` columns int64-overflow for real values above ~1e16 (classic INT64_MIN/1000 saturation
pattern, e.g. `-9223372036854775.808`). Nothing new; do not re-open this file as a lead without a
design pass on bignum support.

## 3. `misc.icn` — NEW 5th silent-SIGSEGV witness, root cause found (not cured)

Flagged since session 6 as "a possible 5th silent-SIGSEGV witness, never actually gdb'd by anyone."
Confirmed SIGSEGV (rc=139). gdb backtrace:

```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff2a76b59 in scrip_coexpr_activate (target=0x100000002, x0=0, x1=0, out2=0x7fffffbf6bc0)
    at src/runtime/rt/rt_coexpr.c:184
184         if (target->dead) return 0;
```

`target=0x100000002` is not a real `scrip_coctx_t*` — it is a descriptor/tag-shaped bit pattern (high
word 1, low word 2) reaching a raw-pointer-typed C argument. Source line in `misc.icn`:
`pairs { 1 to 100, 11 to 99 by 11 };` calling `procedure pairs(e)` which does `@e[1]`, `@e[2]`. Real
Icon's `{ e1, e2 }` is a plain compound expression (NOT a coexpression/list constructor — that needs
explicit `create`), so `e` is bound to a scalar (the compound expression's own last value), and
`e[1]`/`e[2]` subscript that scalar; `@` (activate) is then applied to the subscript result, which is
not a coexpression at all. This is a genuine Icon program shape that should raise a controlled runtime
error ("invalid type — co-expression required"), not crash.

Root cause: **`@` has no type check on its operand before treating it as a coexpression pointer.**
Confirmed by reading the call site — `bb_activate()` (`src/templates/bb/bb_activate.cpp`) emits a bare
`call scrip_coexpr_activate` on the operand slot's raw value with no preceding type-tag guard, and
`scrip_coexpr_activate()` itself (`rt_coexpr.c:182-184`) only guards against a literal NULL
(`if (!target) scrip_co_uerror(...)`), never against a non-NULL value that isn't actually a
`scrip_coctx_t*`.

**Not cured this session.** This is BB-template/shared-runtime code (the `@` operator's own emission
path), not a fixture- or instrument-level fix, and is squarely the kind of change today's FLEET-20
role split (Sonnet walks/witnesses, Opus cures; a shared-node class goes to hq_U with the witness)
asks NOT be attempted by a walking seat. It is also a DIFFERENT root cause from all four existing
children of `icon-arizona-class-silent-segv-no-diagnostic` (gc2: buildplan/record construction;
iobig: cset registration × coexpr threading; tracer/others-b: integer-subscript snprintf; others-a:
uncoerced integer arg to `find()`) — genuinely a fifth distinct cause behind the same SIGSEGV/no-stderr
symptom the parent census row predicted. Minted as its own row,
`icon-arizona-segv-activate-non-coexpr-operand-misc`, hq_B, citing this census as origin; flagged to
hq_B (this row's ask target) as a candidate for hq_U routing given it touches shared activate/coexpr
machinery, not Icon-only.

## 4. `io.icn` — existing row's repro tightened to a 3-line pure-literal case

`icon-arizona-io-list-element-assign-alternation-swallows-open` (minted 2026-09-04, FREE, hq_B) already
isolated the shape to "assign-with-alternation as a non-first list-constructor element" using
`open()`/`stop()`. This session removed every dependency on file I/O, procedure calls, and even the
`stop()`-triggering failure — the bug reproduces with pure literals and no failure path at all:

```
procedure main()
   local n;
   n := (1 | 2);
   write(image(n));      # prints "1" — correct (control, outside any list)
end
```

```
procedure main()
   local n, L;
   L := [1, n := (1 | 2)];
   write(image(n));      # prints "2" — WRONG. Must print "1": a list constructor takes exactly
end                       # one value per element, and disjunction always yields its first
                          # alternative first.
```

Further isolation this session (all against `--run`, confirmed identically under `--compile`):
- `L := [n := (1|2)]` (alternation as the ONLY element) → correctly prints `1`.
- `L := [n := (1|2), 99]` (alternation FIRST, another element AFTER it) → correctly prints `1`.
- `L := [1, n := (1|2)]` (alternation SECOND, preceded by another element) → **wrongly prints `2`**.

So the defect requires specifically: a disjunction-valued element **preceded by at least one other
list-constructor element** — trailing elements after it are fine; only a non-first position is wrong,
exactly as originally isolated, but now with the smallest possible repro (no I/O, no procedures, no
failure path — this alone rules out any hypothesis resting on `open()`/`stop()` or on backtracking
into a genuinely-exhausted alternative; the bug fires even when both alternatives always succeed).

ASM-DIFF-FIRST (`--compile`) on the 2-element open/stop case showed the disjunction box's own
α/β/γ logic is byte-for-byte structurally identical to the 1-element passing case (same zero-init of
its own flag slot, same γ success-copy, same β retry-and-fallthrough) modulo renumbering — the
defect is NOT inside the disjunction box template itself. Given the `n := (1|2)` literal-only
variant returns the wrong ALTERNATIVE'S value rather than crashing or hanging, the leading hypothesis
is a **stack-slot allocation collision between the preceding list element's storage and either the
disjunction's own retry-state flag or its result-copy staging area**, only possible when something is
allocated ahead of the disjunction in the frame — i.e. a frame-layout/slot-numbering bug in
`make_list`'s per-element lowering, not a defect in any one box's own template code. Not root-caused
further; the `.s` pairs for the (now much smaller) literal-only repro are the next step for whoever
picks this up and should replace the open/stop-based `.s` pair this session generated, since they
isolate the same defect without exercising any file I/O or call machinery. Updated onto the existing
task baton directly (LEDGER entry, `## NEXT` rewritten) rather than re-minted, since the row already
existed and owns this exact shape.

## Verified NOT touched / no regression

Zero source changes landed this session (SCRIP, corpus both clean modulo the housekeeping in §1) —
this session is pure census/witness, consistent with 7 of 8 total sessions on the parent row not
reaching a full cure. `misc.icn`'s crash and `io.icn`'s wrong-value bug are BOTH pre-existing, confirmed
via direct repro against an unmodified tree; neither is caused by anything in this session or in
today's corpus restructuring (both repros are pure `.icn` snippets outside the corpus tree entirely).
