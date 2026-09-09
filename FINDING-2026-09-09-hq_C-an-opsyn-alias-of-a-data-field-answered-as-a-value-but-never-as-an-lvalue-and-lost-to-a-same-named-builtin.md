# An OPSYN alias of a DATA field answered as a value but never as an lvalue, and lost to a same-named builtin

**Seat** hq_C · **Date** 2026-09-09 · **Tree** SCRIP `7a6513db1` corpus `bbff6ad2b` · `RT_OPT=-O0` · oracle `sbl -bf`
**Row** `flip-gimpel-LSORT_driver` · **Cure** SCRIP `a68b60f1b`

## The symptom, which is the interesting part

`corpus/packages/snobol4/gimpel/LSORT_driver.sno` printed its linked list **in the original
order**, in both modes, with **no error and rc=0**. Nothing in the output said a sort had failed —
it said a sort had run and found the list already ordered.

That is the shape worth naming. `LSORT` is a merge sort. Its inner loop is

```
LSORT_C	PRED(VFLD(L1),VFLD(L2))			:F(LSORT_L1)
```

so when the predicate never succeeds, the merge takes from the left run every time — and a merge
that always takes the left run is a **stable sort of an already-sorted list**. The defect's output
is byte-identical to the correct output of a correct program on sorted input. There is no error
path to notice, no crash, no diagnostic: **a broken comparison in a stable merge sort disguises
itself as a sorted input.**

## Two independent defects, both reached through one line of SNOBOL4

`LSORT(L,VFLD,NFLD,PRED)` defaults its three names and then OPSYNs its **own parameter names**
onto them:

```
LSORT	VFLD  =  IDENT(VFLD)  'VALUE'
	NFLD  =  IDENT(NFLD)  'NEXT'
	PRED  =  IDENT(PRED)  'LGT'
	OPSYN('VFLD', VFLD)
	OPSYN('NFLD', NFLD)
	OPSYN('PRED', PRED)
```

so every field access in the merge runs through an alias. Behind that sat two unrelated defects.

### 1. An alias of a name that is BOTH a builtin and a live DATA field reached the builtin

`VALUE` is a SNOBOL4 builtin (`VALUE(name)` → the value of that variable) **and**, in this program,
a field of `DATA('LINK(NEXT,VALUE)')`. The builtin's own dispatch arm already resolves that
collision correctly — it gives the **field** precedence whenever some live `DATA` type declares one:

```c
if (rt_dat_field_of_any_live("VALUE")) { *out = dat_field_get("VALUE", args[0]); return 1; }
```

But `register_fn_alias` copies the target entry's **raw `fn` pointer**, so `APPLY_fn` called the
variable-value builtin *directly* and never reached that arm. The two spellings then disagreed:
`VALUE(rec)` was the field, an alias of `VALUE` was the builtin and answered NULL for a record.
The merge compared two nulls, `LGT` failed on every pair, and the list came out untouched.

⭐ **A precedence rule implemented inside one dispatch arm is not a rule, it is a local behaviour.**
Any route that reaches the same callee by another door — here, a copied function pointer — silently
gets the other meaning. The cure applies the same liveness test at the alias site, and reads
liveness **at call time**, not at OPSYN time, because a `DATA` call may follow the `OPSYN`.

### 2. A field reached through an alias never answered as an lvalue

The direct spelling of a field is known at lower time and becomes `IR_FIELD_VAR`. An alias is only
known at **run time**, so it arrives as a plain `CALL` under a pending `SNO$WANTNM` — and every
route from there (the dtax memo cache, the synonym redirect, the live-field arm) ends at the
**getter**. Under want-name that is wrong in two directions, and only one of them is loud:

| form | before | after |
|---|---|---|
| `NFLD(x) = v` | `[IDX] BOMB rt_assign_var: lvalue is not a variable`, abort | assigns the field |
| `.NFLD(x)` | returns the field's **contents**, used as a name | returns the field's name |

The second is the dangerous one. `.NFLD(x)` handed back the *string stored in the field*, which is
then a perfectly good variable name, so `$PTR = ...` wrote somewhere real — just not into the
record. **A name-of operator that returns a value instead of a name does not fail; it redirects
every write to whatever that value happens to spell.**

## The instrument lesson: `DT_DATA` is a range base, not a tag

The first attempt at the cure used `args[0].v == DT_DATA`, mirroring two existing call sites. That
is wrong, and it is wrong in a way that passes its first test: `DT_DATA` is `0x70` with
`DT_DATA_STRIDE 8`, so `== DT_DATA` matches **only a program's first record type**. `LSORT_driver`
declares two (`LINK`, then `CELL`) — the arm would have cured the `LINK` case and silently skipped
the `CELL` one. The cure uses `>= DT_DATA`. ⛔ Two existing sites (`src/driver/driver_call.c` and
the `BID_APPLY` arm in `by_name_dispatch.c`) still carry the `==` spelling; neither is on a path
this row's witnesses reach, and neither is mine to change on this row, but **they are one record
type away from the same defect.**

## How it was found, and one method note

Factorial ablation, not one-at-a-time removal. Three candidate causes were live — the alias name
being a formal parameter, the target being `VALUE`, and the call being in a function — and the
one-at-a-time arms each looked exculpatory. The 2×2 settled it in one run:

| alias name | target | result |
|---|---|---|
| parameter | `VALUE` | **empty** |
| parameter | `DATUM` (plain field) | correct |
| non-parameter | `VALUE` | correct |
| top level | `VALUE` | correct |

Only the **conjunction** fails, which is why neither single-variable arm found it. Re-ordering the
cases proved it was shape and not execution order.

⭐ **Also: the first cure I wrote changed nothing, and "no effect" reads as "wrong diagnosis."** It
was placed inside a live-field test the aliased name does not satisfy, so it never executed. A probe
proving the edit *runs* — before re-opening the diagnosis — is cheaper than re-deriving a cause that
was already correct.

## Verdict, on the merged tree

- **gimpel** `106/116 → 108/116` both modes (this row flipped `LSORT_driver`; `FPROFILE_driver`
  was flipped in the same window by `eb358a995`, not by this change). No new reds.
- **Control arms**, shared-node scope: SNOBOL4 master **m3 FAIL=0 · m4 FAIL=0** over 1896/1921;
  Icon master per-entry identity **0 regressions, 0 vanished** over 1557 entries.
- ⛔ **Two `make test` arms are red on origin and are NOT this change.** Measured both ways — with
  the change stashed and the tree rebuilt, the failure is identical:
  `test_gate_modes_declaration_travels` reports Icon above its orphaned-declaration watermark
  (`rung03_suspend_gen`, `rung03_suspend_gen_compose`, `rung03_suspend_gen_filter`,
  `seq_resumes_inside_a_conjunction`). Corpus-side declarations, owned by the seats that landed
  those entries.
