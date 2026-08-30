# FINDING: Pascal `case` statement branch bodies inside a `procedure`, assigning to a variable declared in the enclosing (global) scope, silently write to the wrong location — a new, pre-existing, unrelated bug unmasked while verifying the case-insensitivity fix

## Context
Found while verifying `pascal-identifiers-must-be-case-insensitive-writeln-only-lowercase` against the vendored FPC suite (`corpus/packages/pascal/fpc_tests/`, row `fpc-tests-vendor-script-run`). One file, `tbs_tb0169.pas`, moved from PASS to FAIL when the case-insensitivity fix landed — investigated fully before accepting or reverting anything, per this project's "a red that clears should be re-measured" culture (and its inverse: a red that appears needs the same scrutiny, not an assumed-regression revert).

## NOT a regression from the case-insensitivity fix — a masked, unrelated, pre-existing bug
`tbs_tb0169.pas`'s own `error` procedure calls `Writeln(...)` (capital W) then `Halt(1)`. **Before** the case-insensitivity fix, `Writeln` was not recognized (case-sensitive builtin lookup), so the FIRST call inside `error` failed loudly (`Error 5`) before printing anything — stdout stayed empty, which happened to byte-match the `.ref` (also empty) for a completely unrelated reason: the test's *correct* behavior is also to produce no output (neither `error` call should fire on a correctly-evaluated boolean `case`). **After** the fix, `Writeln` resolves correctly, `error`'s message prints, and execution reaches `Halt(1)` — which is a **separate, still-unimplemented builtin** (isolated: a bare `Halt(1)` call anywhere raises `Error 5 — Undefined function or operation`, no relation to casing). But `error` should never have been called in the first place at 45>2.

## ROOT CAUSE, ISOLATED CLEANLY (three-step narrowing, each verified independently)
```pascal
program t;
var greater : boolean;
procedure compare(i,j : integer);
begin
   case (i>j) of
     true : begin greater:=true; end;
     false : begin greater:=false; end;
   end;
end;
begin
  greater := false;
  compare(45,2);
  writeln('after compare(45,2), greater=', greater);   (* prints 0 -- WRONG, should be 1 *)
end.
```
- A **top-level** (non-procedure) boolean `case` assigning to a local var: **correct** (verified in isolation).
- The **same** `compare` procedure using **`if i>j then greater:=true else greater:=false`** instead of `case`: **correct** (`greater=1`, verified in isolation).
- Only the combination — **`case` statement, inside a `procedure`, branch body assigns to a variable declared outside that procedure** — produces the wrong result (`greater` reads back as its pre-call, unchanged value, `0`/false, regardless of which branch should have fired).

This narrows the defect to how `case`-branch compound-statement bodies (`begin ... end` as a `case` arm) resolve a variable reference when compiled inside a procedure whose own frame is not the variable's declaring scope — the assignment is landing somewhere that isn't the global `greater`, while the exact same assignment via `if/else` in the identical procedure context lands correctly.

## SCOPE, NOT YET ESTABLISHED
Not tested: whether this needs the branch body to be a `begin...end` block specifically (vs. a bare single statement per `case` arm), whether it's boolean-case-specific or reproduces with an integer/enum `case` selector too, or whether it also affects a `case` inside a `procedure` writing to that procedure's OWN local (as opposed to an outer/global) variable. Not attempted — this needs its own minimal-repro sweep, not a guess.

## NOT ATTEMPTED
No fix, no root-cause trace into `emit.cpp`/`lower_pascal.c`/`pascal.y`'s `case`-statement lowering. Flagging precisely rather than guessing at the mechanism. Also not filed: `Halt` being entirely unimplemented (confirmed separately, trivially reproducible, likely its own quick row — a plain `Halt(1);` anywhere raises `Error 5`) — named here since it's what this exact file hits SECOND, but it is a distinct, unrelated gap (a missing builtin, not a wrong-location write) and shouldn't be conflated with the case/scope defect above.

## NEXT ACTOR
1. Minimal repro above reproduces reliably (isolated, no corpus dependency) — start there, not `tbs_tb0169.pas` directly.
2. Establish scope (single-statement case arms vs. blocks; boolean vs. ordinal case selector; global vs. procedure-local target variable) before touching `case`-statement codegen.
3. `Halt` unimplemented is a separate, smaller, likely-quick gap — its own row if picked up.
