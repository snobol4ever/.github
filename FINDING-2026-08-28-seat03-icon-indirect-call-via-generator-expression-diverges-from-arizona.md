# FINDING 2026-08-28 seat03: indirect procedure call via a generator expression diverges from Arizona Icon

## Context

Found while working `tests-consolidate-icon` (corpus housecleaning fan-out). `rung37_proc_lookup.icn`
(one of 18 loose files under the flat `rung37` family — no dedicated consumer script, so this is
NOT a suite-conversion mechanism artifact) failed `corpus_suite_harness.py convert-blocks`'s own
pre-write "is the original file itself green" gate: **nothing was written or deleted** — the harness
correctly refused rather than silently converting a red witness. Not caused by, or specific to, the
conversion attempt.

## The witness

```icon
#SRC: IJ-3 focused test: proc() builtin + indirect invocation
procedure p0();
   write("p0");
end
procedure p1(x);
   write("p1", x);
end
procedure main();
   local plist;
   write(image(proc("write", 1)));
   if not (proc("noexist", 1)) then write("noexist fails");
   plist := [3, p0, p1];
   every write((!plist)());
   every write((!plist)(1));
end
```

## Verdicts

**`.expected` (this corpus's recorded oracle):**
```
function write
noexist fails
p0
p1
p0
p11
```

**Real Arizona Icon** (`/home/resources/icon-master/bin/icon`, already built on this box —
confirmed this is `icont`'s combined compile+run form, not a stale binary):
```
function write
noexist fails
p0
p1
p0
p11
```
**Byte-identical to `.expected`.** The oracle is correct, not stale — checked directly, not assumed.

**SCRIP, both modes** (`./scrip --run` and `./scrip --compile` + link — identical to each other,
so this is not an m3/m4 divergence, it reproduces the same way in both mediums):
```
function write
noexist fails
p0
p0
p1

p0
p0
p11
1
```

## Characterization

SCRIP produces EXTRA output the real semantics do not: `p0` is written twice instead of once
during the first `every write((!plist)())` pass, an empty line appears where the `3()` iteration
(calling a non-procedure) should simply fail silently and contribute nothing, and the second pass
(`every write((!plist)(1))`) also shows a doubled/extra tail (`p0`, `p0`, `p11`, `1` instead of the
correct `p0`, `p11`). The shared shape across all three anomalies is consistent with the callee
side of `(!plist)(...)` — a generator expression (`!plist`) used as the CALLEE of an invocation —
being evaluated or driven more than once per intended call, and the `3()` case (non-callable) not
failing cleanly. Not root-caused further — this is characterization, not a fix.

**Possible connection, not confirmed:** `rung37_subscript_genproc.icn` (converted this session via
`--skip`, deliberately left loose) documents a related-sounding mechanism in its own header:
*"The forward first-entry into the index expression must land the generator's alpha, never its
beta... the tgrlink class"* and references `lower_call`'s `la_res` path for resumable-argument
calls. Both witnesses involve a generator expression feeding into a call/index site. Whether
they share a root cause is unverified — flagging the possible connection for whoever investigates,
not asserting it.

## Disposition this session

- `rung37_proc_lookup.icn` left loose (not converted, not deleted, not fixed) — `--skip`ped from
  the rung37 suite conversion alongside `rung37_subscript_genproc.icn`, both for their own reasons.
- The other 17 rung37 entries converted cleanly (all green, verified both directions, both modes).
- Not filed as blocking anything — this task's DONE-WHEN only cares about the corpus tree; a
  correctness bug is HQ's/codegen-owner's call, not a reason to stall housecleaning.

## Open question for hq_C

Is this the same subsystem/root cause as `rung37_subscript_genproc.icn`'s documented tgrlink SEGV
class (both are generator-as-callee/index shapes), or unrelated? Worth a session with room to
actually trace `lower_call`'s generator-argument path rather than guess from the outside.
