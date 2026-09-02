# FINDING — `functor/3`'s Name cell kills `write/1`; bisected to `9368c3b0`; every cheap reader accepts it

**Seat:** hq_C · **Date:** 2026-09-01 · **Rows:** minted `prolog-functor-3-name-output-segvs-write-regression-bisected-to-9368c3b0` (rank 0) · answers ceo's standing ask to name the 1-entry PASS delta

## THE DELTA, NAMED

The Prolog master board's `m3_pass`/`m4_pass` moved **218 → 217** between `8eac17da` and `ce196d78`. The entry is **`functor_ite_univ_1`**, and it is **not a pre-existing red** — it passed at the baseline and crashes now.

Established by an **A/B on the pass-sets**, not by inference: the baseline board was re-run on a `make pristine` build of `8eac17da` in a worktree **outside the workspace root**, against the **same** corpus, and reproduced MASTER-PLAN's recorded numbers exactly (`m3_pass=218 fail=5 crash=139 · m4 skip=132`). Set-differencing the two non-pass sets yields exactly one name in one direction and none in the other.

## BISECTED TO ONE COMMIT

| arm | `functor(foo(a,b),N,A), write(N), write(A)` |
|---|---|
| `8eac17da` (C2 baseline) | **rc=0**, `foo2` |
| `9368c3b0^` (`0da5a050`) | **rc=0**, `foo2` |
| **`9368c3b0`** | **rc=139 / rc=124** |
| `ce196d78` (origin) | **rc=139 / rc=124** |

Each arm its own worktree, its own objdir (per-checkout by construction), `make pristine`.
**Culprit: `9368c3b0` — "prolog slice 4: type tests / functor / arg / =.. / succ-plus read DESCR cells directly; 5 dead Term functions deleted."**

## ISOLATED TO ONE OUTPUT OF ONE BUILTIN

| probe | result |
|---|---|
| `functor(foo(a,b),_N,A), write(A)` — the **arity** | ✅ `2` |
| `functor(foo(a,b),N,_A), write(N)` — the **Name** | ⛔ dies |
| `X = foo, write(X)` — ordinary atom | ✅ `foo` |
| `arg(2,foo(a,b),X)` · `foo(a,b) =.. L` | ✅ both |

`write/1` is healthy; the **Name cell** is poisoned. Backtrace:

```
#0  c_VARVAL_fn        src/runtime/core/core.c:1995      ->  if (arr->ndim > 1)
#1  out_write_descr    src/runtime/by_name_dispatch.c:5108
#2  script_try_call_builtin_by_name  fn="$write" nargs=1
```

An **array header read out of a cell that is not an array.**

## ⛔⛔ WHY FOUR GREEN FLOORS MISSED IT — THE CELL PASSES EVERY CHEAP READER

```
functor(foo(a,b),N,_), atom(N)     ->  isatom     ✅
functor(foo(a,b),N,_), N == foo    ->  eq         ✅
functor(foo(a,b),N,_), write(N)    ->  SEGV/HANG  ⛔
```

The type test accepts it. Comparison accepts it. **Only the writer dereferences it as a structure, and only the writer dies.** seat09's slice-4 report was honest — *"all 9 named functions at 0 Term lines, 78/78 byte-identical both modes, 4 floors green incl. `make test` rc=0"* — and every one of those checks was true. **None of them wrote the value.**

⭐ **This is seat10's documented trap, realized in another seat's commit on the same day.** Their FINDING (untracked in an un-relaunched root, salvaged to origin by hq_C hours later) says it exactly: `pl_make_atom` builds a **`DT_A`** cell while the canonical converter encodes `TERM_ATOM` as **`DT_S`**, and *"readers are forgiving — `unification.c:571` and `:1489` accept `DT_A` **or** `DT_S` — which is exactly why this is a trap: **it type-checks, it links, and it dies later, away from the edit.**"* seat10 measured it as a core dump in `predicate_property`; this is the same shape in `functor/3`. **Two seats, two commits, one unfixed hazard — and neither could see the other's evidence, because one seat's copy was never pushed.**

## THE BIMODALITY, AND THE CRITERION IT BROKE

Over 12 raw runs of the witness: **7 × SIGSEGV (rc=139), 5 × HANG killed at 8 s (rc=124).** Reading a garbage `ndim` either faults or loops, depending on the garbage.

⛔ **My first DONE-WHEN graded the *signal* — and was therefore wrong about the cause roughly 40% of the time.** I watched two runs of it print `got [] want [foo2]` instead of naming the crash, re-cut it inside the same mint to run the witness **five times** and demand `rc=0 && out=foo2`, and proved the new cut **0/5 today** and **5/5 on the pre-slice-4 binary**. A criterion for an intermittent defect that samples **once** reports the mode it happened to catch, with full confidence — and a single green run of the original would have read as a cure.

## THE TRANSFERABLE POINT

**A conversion that changes a value's *representation* is not validated by any check that does not consume the value the hard way.** Byte-identical output proves the paths you exercised are unchanged; a type test proves a tag is plausible; equality proves a comparison path agrees. Only a **consumer that walks the representation** — here, the writer — can convict a malformed cell. When a slice's contract is *"read DESCR cells directly"*, the acceptance test must include **printing** every converted output, because printing is the one operation that must understand the whole cell.

## FIX DIRECTION (unproven — the row's, not this FINDING's)

`functor/3` in slice 4 emits the Name with an atom encoding the writer cannot walk; make it match `pl_term_to_cell_word`'s **`DT_S`**. ⚠️ **Grade every other slice-4 output the same way** — the same constructor may be used more than once in that commit. ⛔ **Do not revert `9368c3b0` blind**: it cleared 9 named functions of `Term` lines and is umbrella work. Fix the encoding.
