# FINDING 2026-09-04 seat14 — Rebus exchange operator `:=:` lowers to a call to a non-existent builtin `EXCHG`, crashing every program that uses it

**Row:** `rebus-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs` (hq_T → seat14).
**Found while:** absorbing `tests/rebus/syntax_exercise.reb` — it ran 10 lines of correct output then crashed, so it was ablated to a minimal witness rather than absorbed with a crash as its "expected" ref.

## Minimal witness

```
function main()
  local i, j
  i := 0
  j := 10
  i :=: j
  OUTPUT := i
end
```

```
$ scrip probe_exchange.reb
** Error 5 in statement 0
   Undefined function or operation
rc=1
```

Deterministic (ran twice, identical). `--dump-ast` on the same file succeeds (rc=0) and prints a clean `TT_SWAP` node — this is a lowering/codegen gap, not a parse defect. Reproduces in m3; m4 `--compile` also emits without erroring at compile time (link succeeds), so the missing symbol is a runtime dispatch failure, not caught until executed either way.

## Root cause

`src/parsers/rebus/rebus_lower.c:97`:
```c
case TT_SWAP:   return make_fnc("EXCHG", 2, lower_tree_expr(L,e->c[0]), lower_tree_expr(L,e->c[1]));
```
lowers the exchange operator to a call to a builtin literally named `"EXCHG"`, which is not registered anywhere (`grep -rn '"EXCHG"' src/` finds only this one site). "Undefined function or operation" is by-name-dispatch failing to resolve it at runtime.

The box family for exactly this operation already exists and is used elsewhere: `src/templates/bb/bb_swap.cpp` ("IR_SWAP x:=:y"), `bb_swap_var.cpp` ("IR_SWAP_VAR x:=:y through variables (canonical swap, oasgn.r:265)"), `bb_rev_swap.cpp`. The likely correct cure is routing Rebus's `TT_SWAP` through that shared box family (per "shared boxes first" / "no C Byrd-box functions" / canonical-procedure reuse) rather than inventing a new builtin — but I have not verified which of the three existing swap boxes is the right target or traced how another frontend wires `TT_SWAP`-equivalent into them, so the cure itself is not diagnosed, only the cause.

## Disposition of the witness

Excluded, not absorbed: `tests/rebus/syntax_exercise.reb` → `ALL.excluded.txt`, reason "crashes on the exchange operator (:=:) at runtime — Error 5, Undefined function or operation; real codegen gap, see this FINDING; not a fixture limitation." A crash is not an oracle-confirmable output, and the fleet is on `THERE IS NO XFAIL` — absorbing the crash trace as the "expected" ref would fabricate a floor around a bug rather than measure one.

## Open — not this row's

The actual cure (wire `TT_SWAP` to a real box). Filed to hq_T rather than fixed here: this is a real runtime/codegen defect, not a fixture-, xfail-, or instrument-level red, which is the boundary my role (isolation walker) cures directly versus files for HQ.
