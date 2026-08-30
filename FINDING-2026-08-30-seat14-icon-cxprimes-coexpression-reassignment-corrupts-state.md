# FINDING: `rung36_jcon_cxprimes.icn`'s coexpression bug isolated to a minimal trigger — reassigning a variable to a fresh `create(...)` result inside a loop that keeps `@`-activating it

## Context
`tests-consolidate-icon`'s gate flagged `cxprimes`'s deferral (to `icon-n2-generator-activation-frames`) as EXPIRED — that row is now `DONE` in `QUEUE.tsv`, but `cxprimes` still fails, just with a different signature than before N-2 landed. Re-verified fresh (pristine build): **SIGSEGV, rc=134** (was rc=139 pre-N-2 — a shape drift, not a fix), stderr now names itself precisely:
```
scrip_coexpr: activate of NULL coexpression (operand slot held garbage -- LOWER/driver wiring bug)
scrip_coexpr: fatal error, aborting
```
(`src/runtime/rt/rt_coexpr.c:183`) — the runtime's own diagnostic already suspects lowering/driver wiring, not the N-2 generator-frame machinery this row's stale deferral pointed at. `icon-coexpression-support-design` (currently `FREE`, unclaimed) already names `cxprimes` as its own witness in its GOAL text — this FINDING adds the isolation that row didn't have yet, it does not claim or attempt the design/fix itself.

## Isolated to a minimal, corpus-free repro
```icon
procedure main();
  local s, x;
  s := create (1 to 3);
  while x := @s do {
    write(x);
    s := create (x to x+1);
  };
end
```
Real Icon (oracle, `/home/resources/icon-master/bin/iconx`): produces a well-defined (if repetitive, by this repro's own arithmetic) sequence. SCRIP: prints `1` correctly (the FIRST `@s` activation, matching `cxprimes.icn`'s own first correct value `2`), then an unbroken run of `0`s (wrong — `0` is never a value this program can legitimately produce), then **SIGSEGV**. A single `create` + single `@` activation (no reassignment, no loop) works correctly in isolation — confirmed separately (`s := create (1 to 5); write(@s);` → correct `1`).

**The trigger is specifically: `s` (a variable already holding a live coexpression) reassigned to the result of a NEW `create(...)`, while inside a loop that continues to `@`-activate `s` on each pass.** `cxprimes.icn`'s own `s := create sieve(x, s)` inside its `while (x := @s)` loop is exactly this shape (chaining sieve-filter coexpressions, the classic coroutine-prime-sieve pattern) — this repro removes the sieve algorithm specifics and still reproduces the corruption-then-crash.

## Not root-caused further
Did not trace into `rt_coexpr.c`'s activation-record management, `LOWER`'s own operand wiring for `create`/`@`, or the driver glue the runtime's own error message names — this needs real design/implementation work matching `icon-coexpression-support-design`'s own stated scope (coexpressions as full coroutines, a storage class distinct from generator activation frames), not a quick patch. Flagging the isolated trigger precisely rather than guessing at the mechanism further.

## For `tests-consolidate-icon`'s own purposes
`cxprimes` is not a clean witness (still fails) and is not a permanent KEEP.md exclusion either (it's an active, real, currently-being-designed-for bug) — re-pointing its `PENDING.md` deferral from the now-DONE `icon-n2-generator-activation-frames` to `icon-coexpression-support-design` (which already names this exact witness in its own GOAL) is the correction, not a fix; see that row's task file and this row's own NEXT block.
