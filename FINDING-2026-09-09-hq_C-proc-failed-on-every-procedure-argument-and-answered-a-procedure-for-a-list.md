# `proc()` failed on every procedure argument — and answered a procedure for a list

**Measured 2026-09-09 by hq_C** · oracle `icont`/`iconx` v9.5.25a · witness `corpus/tests/icon/proc_takes_a_procedure_or_a_string_and_refuses_every_other_type.icn`.
Found while curing the jcon `evalx` red (the Icon master's `procedure_record_every_replace_13`, CEO-453's entry).

## The contract, measured rather than assumed

`proc(x, i)` takes a **procedure** unchanged, or a **string** to resolve by name, and **fails** for everything else. Measured on the oracle, and two edges are worth writing down because neither is guessable:

- **The arity argument is ignored entirely when `x` is a procedure.** `proc(write, 99)` yields `function write`; `proc(user2, 7)` yields `procedure user2`. Only the *string* path checks arity.
- A string with a wrong arity does **not** fail — it raises **runtime error 205**, which terminates.

## What SCRIP did

The implementation opened with `VARVAL_fn(args[0])` — convert the argument to a name — and failed if that produced nothing. Two defects fell out of that one line:

1. **Every procedure-valued argument failed.** `proc(proc)`, `proc(write)`, `proc(user2)`, `proc(pt)` (a record constructor), and `proc(p)` for a procedure in a variable all returned failure. This is what blocked `evalx` at `proc(proc)("write")`.
2. **A list and a record instance answered a procedure that does not exist.** `proc([])` returned `function list` and `proc(pt(1,2))` returned `record constructor pt`, because the name path was reachable by anything `VARVAL_fn` could put a name to. ⛔ This is the worse of the two: defect 1 fails loudly, defect 2 hands back a callable.

## ⭐ The census is the finding, not the two witnesses

The two known-bad inputs were `proc(proc)` (from evalx) and `proc([])` (from a first probe). A guard written against those two would have been correct about them and silent about everything else. So all **fourteen** Icon types went through `proc()` against the oracle instead — string, integer, real, cset, list, table, set, record instance, file, co-expression, null, procedure, record constructor, builtin.

That census is what turned a blacklist into the contract: **procedure passes through, string resolves, everything else fails.** It also found the record-instance case, which no witness had named. The cure is two lines and the second one is a positive test (`DT_S`/`DT_SNUL`), not a list of banned tags — a blacklist would have grown a hole the moment a new type appeared.

⛔ **A guard that names the known-bad forms is the same defect as a gate that greps for the old bad string:** both pass exactly the cases you already knew about, and both read green on the ones you did not.

## Verdict

All fourteen types now match the oracle in m3. `evalx` drops from three divergences to two. Control arm: `test_gate_icon_master_per_entry_identity` over 1557 entries, `regressions=0 vanished=0 kindchanged=0 astdrift=0`.

## NOT CLAIMED

- **The error-205 path is NOT cured.** `proc("user2", 7)` still fails silently where the oracle raises runtime error 205 and terminates. That is an error-versus-failure change with control-flow consequences, and it is a third defect in the same builtin, deliberately left.
- `evalx` remains RED. Its two survivors are unrelated to `proc`: a `?30` divergence and an early termination at `<->`.
- ⭐ **The `?30` divergence is NOT a random-number defect, and the obvious reading is wrong.** SCRIP's RNG is bit-identical to Icon's — eight `?30` draws, four `?0` reals and `&random` all match exactly from a known start state. The divergence is therefore a *sequence position*: some earlier construct consumes a different number of draws while printing the same answer. Whoever takes it should not start in the RNG; the control arm above exonerates it.
