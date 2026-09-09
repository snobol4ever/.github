# `<->` aborted the emitter because its operands are literals, not `IR_VAR` nodes

**Measured 2026-09-09 by hq_C** · oracle `icont`/`iconx` v9.5.25a · witness `corpus/tests/icon/reversible_exchange_on_locals_needs_a_varslot.icn`.
Found while curing the jcon `evalx` red. Cures the **simple** form only; the nested form is rowed (`icon-nested-reversible-exchange-loses-its-swap-and-the-chained-form-kills-the-procedure`).

## The defect

`x <-> y` on two locals aborted the compiler:

```
[TE-4] IR_REV_SWAP lhs local 'x' has no LOWER-granted varslot — grant it in
       ir_drive_slot_assign (scrip_ir.c), never allocate in the emitter
```

The vslot discovery loop in `src/ir/frame_layout.c` (renamed from `zeta_storage.c` mid-sitting by another seat, which is also why this cure landed through a rebase conflict) walks the graph and grants a frame slot to the local named by each node it recognises: `IR_ASSIGN`, `IR_REV_ASSIGN`, `IR_VAR`, `IR_VAR_REF`. `IR_REV_SWAP` is not in that list, and — this is the part that matters — **it could not have been reached by widening the list to more node kinds**, because it does not name its locals the way the others do. `lower_icon.c` puts the lhs name in `IR_LIT(nd).sval` and the rhs name on an **`IR_LIT_STRING` operand**. There is no `IR_VAR` node for either variable anywhere in the graph.

Cured by naming `IR_REV_SWAP` in that loop and granting **both** names — the loop previously assumed at most one local per node, so it also had to learn to grant two.

## ⭐ Why no swap witness ever caught it

`x :=: y` — ordinary exchange — was green throughout, and it is the construct anyone writing a swap test reaches for. The two operators look like a pair and are not: `:=:` lowers through nodes the slot loop already recognises, `<->` does not. **A green sibling that appears to cover the feature is the reason the gap survived**, and the same shape shows up twice more in this sitting's work (`lower_until` correct while `lower_while` was not).

## ⭐ The witness that measures nothing

The first draft of this witness declared `local x, y, z` and never assigned them. Every answer was `&null`, and it passed the moment the abort stopped — while being **structurally incapable** of detecting a wrong value, because with all operands `&null` a swap and a no-op are indistinguishable. Giving the locals real values (1, 2, 3) immediately exposed two further divergences.

⛔ **A witness for an operator that MOVES values must use values that can differ.** An uninitialised witness for an exchange tests only that it does not crash — and reads exactly like a passing test.

## ⭐ The first wrong line was not the defective one

Chasing those further divergences, the first line whose *printed value* disagreed was two steps downstream of the fault. The defective construct printed the **right result** and left the **wrong state**; nothing was visibly wrong until a later line read that state. The trace that localised it printed `x`, `y` and `z` after **every** step rather than the value of each expression.

This is the same shape as the `?30` divergence in `evalx`, where SCRIP's RNG is bit-identical to Icon's and the wrong number is a *sequence position* left by an earlier construct. **When a value is wrong, the suspect is not the line that printed it.**

## Verdict

`x <-> y`, its backtracking restore, and `x :=: y` all match the oracle in m3 and m4.

Control arm: `test_gate_icon_master_per_entry_identity` over 1557 entries, `regressions=0 vanished=0 kindchanged=0 astdrift=0`.

## NOT CLAIMED

- **The nested form is NOT cured**, and this landing converted an abort into a wrong answer for it. `(x <-> y) :=: z` now runs and leaves state consistent with the inner exchange never happening; `x <-> y :=: z` prints nothing and kills the enclosing procedure, because `TT_REVSWAP` lowers a non-name operand to a bare `IR_FAIL`. Both are rowed with the state trace and a control arm proving that ordinary failure *is* caught by `| "none"` while this one escapes it.
- `evalx` remains RED on both its surviving divergences; no master entry flips and no board row moves.
