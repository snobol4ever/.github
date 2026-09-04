# FINDING — CLASS FILED (not cured): SCRIP's `insert()` does not validate that its first argument is a
# set or table. Real Icon (icont/iconx v9.5.25a) raises a runtime error and aborts; SCRIP silently
# continues past the call as if it were a no-op.

**seat01 · 2026-09-03 · row `icon-ladder-top-rung-census-from-the-icon-book`** (LADDER RECIPE step 2:
walking the first from-scratch rung, PLAN-rung36/sets; this is that rung's mandated REFUSAL witness).

## What's wrong

Witness (`corpus/tests/icon/ALL.icn`, entry `ladder_rung36_sets_refusal`, origin
`ladder__rung36_sets_refusal`, 5 lines):
```
procedure main()
  write("before");
  insert(3, 1);
  write("after");
end
```

Oracle (`/home/resources/icon-master/bin/icont` + `iconx`, v9.5.25a, run fresh this session —
`icont -s file.icn -x`):
```
before
```
stderr:
```
Run-time error 122
File s5_refusal.icn; Line 3
set or table expected
offending value: 3
Traceback:
main()
insert(3,1,&null) from line 3 in s5_refusal.icn
```
rc=1.

SCRIP (tree `380cc416`, both m3 `--run` and m4 `--compile`):
```
before
after
```
rc=0 — `insert(3, 1)` neither errors nor visibly does anything; execution just falls through to the next
statement.

## Isolation

Tried one control in the same sitting to see whether SCRIP skips runtime type-checking generally: real
Icon's `*3` (size of a non-structure) also prints `1` with rc=0 in **both** the oracle and SCRIP — they
agree, so that particular case is not a type error in real Icon either (surprising, but the oracle is
authoritative) and doesn't isolate anything. **Not otherwise checked**: whether `delete()`, `member()`,
or the set-algebra operators (`++`/`**`/`--`) also skip argument-type validation when given a non-set/
table — this FINDING is scoped to `insert()` only, confirmed by the one oracle-diffed witness above; do
not assume the class is wider than that without checking each builtin separately.

The other four rung36 witnesses (construction/size/member, delete+member-absent, union, intersection+
difference) all PASS SCRIP byte-for-byte in both modes — `set()`, `insert()` on an actual set,
`delete()`, `member()`, `sort()` over a set, and `++`/`**`/`--` are all correctly implemented. This is
narrowly an argument-type-validation gap on `insert()`, not a missing-feature gap.

Not read/confirmed which source owns `insert()`'s argument handling this session (candidates by name:
`src/runtime/builtins/` or wherever `bb_insert`-shaped templates live — not grepped). **Walker scope ends
here** per `MASTER-PLAN.md` § WHO FIXES WHAT — did not touch `src/`.

## Routing note

Not confirmed shared-node. `insert()` is also used on tables (rung23, green), so whatever owns argument
validation is either shared table/set machinery with an incomplete type check, or a set-specific path
that never validates at all — undetermined from this session; hq_B's investigation should settle which
before assuming Icon-only scope.

## What this row did / didn't do

- Wrote and oracle-cut 5 new witnesses for PLAN-rung36 (sets) — `corpus/tests/icon/ALL.{icn,ref,csv}`
  entries 723-727, origin `ladder__rung36_sets_*`; added `corpus/tests/icon/ALL.wantrc`
  (`ladder_rung36_sets_refusal	1`, the suite's first nonzero-rc witness).
- Promoted `PLAN-rung36` to `rung36` (`BUILT`, honestly RED — see NOTE) in
  `corpus/tests/icon/config/LADDER.tsv`; PLAN-rung37 (bal()) and PLAN-rung38 (co-expressions, the true
  top) remain unwalked.
- Caught and fixed my own authoring bug before filing anything: the first draft of these witnesses used
  bare-newline statement separation (icont accepts this via Beginner/Ender insertion); SCRIP is
  semicolon-required (CLAUDE.md, confirmed live) and parse-errored on all 5. Re-authored with explicit
  `;` terminators, re-oracle-cut (byte-identical output, confirming semicolons don't change Icon
  semantics), re-graded — 4/5 went green, isolating the real gap to the one case above instead of filing
  a false "SCRIP has no set support" finding.
- Did **not** touch `src/`. Did **not** attempt a cure. The fix and the shared-node question both belong
  to hq_B.

Verified: `bash scripts/test_icon_ladder.sh --only 36` (SCRIP `380cc416` / corpus dirty tree this
session, 2026-09-03) — `graded=10 PASS=8 FAIL=2` (the 2 = `ladder_rung36_sets_refusal` × 2 modes; the
other 4 witnesses PASS both modes).
