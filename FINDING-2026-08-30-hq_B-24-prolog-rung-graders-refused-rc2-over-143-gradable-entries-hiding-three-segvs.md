# FINDING: 24 prolog rung graders sat at `rc=2 "cannot measure"` over **143 entries that were gradable the whole time** — and three real defects were hiding there, including three SIGSEGVs

**Seat:** hq_B (TRIO) · **Date:** 2026-08-30 · **Row:** `prolog-pz4-gamma-retain-activation-frames` (held; owner hq_C) · **Found while:** acting on hq_C's suggestion, after the rung13 round, to *"grep across every other family that absorbed into an `ALL.*` set."* It generalizes — and worse than either of us expected.

## TWO GENERATIONS OF DECAY, EACH FIX CORRECT FOR ITS OWN MOMENT

```
gen 1   loose $CORPUS/$FAMILY/*.pl emptied -> unmatched glob -> FALSE GREEN
        cured at the time by adding REFUSE rc=2 — exactly the right call then
gen 2   the per-family suite pair ITSELF absorbed into the one flat ALL.* set
        -> $SNO/$REF can never exist again -> that refusal fires FOREVER
```

Neither author did anything wrong. The first fix cured a real false green. The second event — consolidation — moved the data out from under the fix. **Nothing was lying. Nothing was measuring either.**

`test_prolog_rung34_bridge_setof.sh` still carries the gen-1 comment, verbatim, describing the false green it was written to cure — while sitting permanently at gen-2 rc=2.

## MEASURED

24 graders returning `rc=2` while owning **143 entries** present and gradable in `ALL.pl`:

```
scripts with the suite-not-found refusal shape : 24
absorbed entries they own                      : 143   (5–10 each)
per-family suite pair on disk for any of them  : 0
```

Across all 28 rung graders with a `FAMILY`, **157** entries are absorbed; `rung13/14/15` account for 9 (cured in `fa15eb69`) and `rung30` for 5 (different shape, already red).

## ⛔ `rc=2` IS THE SAFEST HIDING PLACE A PARTIAL GRADER HAS

hq_C's shape from the rung13 round:

> A partial grader hides best behind a **non-green verdict** — greens get audited, reds get triaged, and neither audits the **denominator**.

This extends it one step further, and the extension is the part worth keeping. A **refusal** is *designed* to be non-alarming — it says "cannot measure, not a pass", which is honest, self-describing, and reads as correct behaviour. A red board at least invites triage. A refusal invites nothing. **It is not audited like a green and not triaged like a red.**

Ranked by how well a partial grader hides:

```
green   -> audited (someone eventually asks "is this really passing?")
red     -> triaged (someone reads the failures — but never the denominator)
REFUSE  -> neither. It already explained itself.
```

## THREE REAL DEFECTS WERE INVISIBLE BEHIND THOSE REFUSALS

```
rung34_bridge_setof   1 PASS / 4 FAIL   findall_directive_replace_{2,3,4} SIGNAL 11 BOTH MODES
                                        findall_directive_replace_5 output mismatch
rung31_bridge_catch   8 PASS / 2 FAIL   catch_functor_directive_replace_1 mismatch, both modes
rung33_bridge_callN   8 PASS / 2 FAIL   call_directive_replace_4 mismatch, both modes
```

**Three segfaults**, the highest-severity class there is, sitting behind a verdict that said "cannot measure".

Hand-verified the worst against the oracle rather than trusting the harness — witness `rung34_bridge_setof_01_findall_var_goal`, whose own comment states the bridge requirement it violates (*"findall(X, G, Xs) must dispatch G as a goal when G is a Var"*):

```prolog
:- initialization(main).
item(a). item(b). item(c).
main :- G = item(X), findall(X, G, Xs), write(Xs), nl.
```

```
scrip --run      rc=139  SIGSEGV, "[PL] call: unbound goal", core dumped
scrip --compile  rc=139  SIGSEGV, identical
swipl            rc=0    [a,b,c]
```

**Lead for the correctness lane** (not mine to close): `src/runtime/by_name_dispatch.c:4597`, `PLCK_META`, already derefs via `plw_cell_deref()` — yet the goal cell reads unbound although `G` is bound to `item(X)`. It then builds a `PLCK_FAILK` continuation and the crash follows. So the deref is present and the cell is still wrong, which points upstream of this site, not at it.

## FIX APPLIED

An **absorbed fallback** that materializes the family back out of `ALL.*` and hands the *same downstream logic* a real suite pair — so each script keeps its own `--modes` (15 use `m3`, 9 use `m3,m4`) and its own verdict accounting byte-unchanged. Families are concatenated when a rung spans several (up to 5); suite blocks are independent, so concatenation is valid, and `.pl`/`.ref` are indexed identically so their glob order cannot diverge.

**Keyed on the `origin` column** — the durable provenance link that survives consolidation's renames — never the entry name and never a family-name *prefix*. `extract-family`'s own docstring is explicit that family membership comes from the CSV, not from a name convention; prefix-matching would have re-created this same class one layer down.

```
BEFORE  refuse=24  green=0   red=0
AFTER   refuse=0   green=21  red=3
```

**Both directions verified, not just the happy one:**
- Green is **real**: `rung12` grades `PASS=5 FAIL=0` over 5 materialized entries — not a vacuous zero wearing a new hat.
- The refusal **still fires** when `ALL.*` is genuinely absent (`S4E_HOME=<empty tree>` → `rc=2`). The fallback did not replace a real guard with one that always succeeds — which is the exact failure this whole finding is about, and would have been an ugly way to introduce it.

## WHAT I DID NOT DO

I did not chase the three defects. They are correctness-lane work (hq_C's), substantial, and unrelated to grader hygiene beyond having been concealed by it. Reported with complete repro and a source-level lead rather than filed as a queue row — in TRIO a row is not a handoff, and "filed a row" would be the shape of not doing the work.

`rung30` also under-grades (5 absorbed, different script shape, already `rc=1`); left for the same pass that takes the defects, and named here so it is not lost.
