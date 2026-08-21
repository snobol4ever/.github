# FINDING s192 — `PROTOTYPE` WAS SPELLED TWICE, AND THE ERROR IT REFUSED TO RAISE WAS HIDING TWO DEAD `CONVERT` ARMS

**Seat8 `/home/claude8`, Claude Opus 5, 2026-08-20. Queue row `prototype-spelled-twice` (rank 2).**
**SCRIP `49b65ced` · corpus `8bd5e327`. Four runtime files, two corpus files. ⛔ ZERO emitter / template / lowerer / machine / optimizer files touched — `.s` regen not applicable.**

---

## ⭐ THE ROW WAS EXACTLY WHAT THE BRIEF SAID IT WAS. THE INTERESTING PART IS WHAT THE CURE MADE AUDIBLE.

The brief was right in every particular and the first step took two minutes: both checked-in probes reproduced RED in both modes, and the oracle reproduced their `.ref`s byte-for-byte. The split was where it was said to be — `nargs==1` took `by_name_dispatch.c`'s `BID_PROTOTYPE`, everything else fell through to `core.c`'s `_PROTOTYPE_`, and the two disagreed on **value and datatype at once**:

| call | SCRIP before | oracle `sbl -bf` |
|---|---|---|
| `PROTOTYPE(ARRAY(3))` | `3` / INTEGER | `3` / INTEGER |
| `PROTOTYPE(ARRAY(3),1)` | **`1:3` / STRING** | `3` / INTEGER |
| `PROTOTYPE(TABLE())` | **statement FAILS** | `11` / INTEGER |
| `PROTOTYPE('abc')` | **statement FAILS** | **ERROR 164**, terminates |

Manual Ch.8 (and `stage2.h`'s `nformals`): only FORMALS bind arguments, and **excess arguments are evaluated then ignored**. `PROTOTYPE(a,1)` is required to be `PROTOTYPE(a)`. SPITBOL obeys; SCRIP changed spelling.

## ⭐⭐ THE CURE — ONE BODY, TWO FACES, AND THE ARITY TEST DELETED RATHER THAN WIDENED

`agg_prototype()` in `aggregates.c` is now the one authority; `BID_PROTOTYPE` and `_PROTOTYPE_` are both faces over it. **The brief's prohibition — *do not special-case an argument count* — is load-bearing and was followed literally: the arity test is gone, not relaxed.** A count-conditioned admission is what produced the split in the first place, so the faces normalise a *missing* argument to the null string and hand the **value** down. The body never learns how many arguments were written, so no arity can reach a different answer, and neither face can drift from the other.

Three answers, every one measured on `sbl -bf`, none inferred:

- **ARRAY** → its creating prototype; all-digits ⇒ INTEGER, otherwise STRING. **Byte-identical to the arm it replaces** — the old `lo==1 ⇒ INTVAL(hi)` shortcut is the same function of the same data, so the brief's requirement 3 holds by construction, not by luck.
- **TABLE** → its hash-header count as an INTEGER. `TABLE()`⇒11, `TABLE(5)`⇒5, `TABLE(5,7)`⇒5 (arg 2 is the value-block size), and `COPY` and `CONVERT` carry it (measured 5 and 3). **The live `BID_TABLE` was discarding its arguments entirely** — `table_new()`, no args — so there was nothing for `PROTOTYPE` to report.
- **anything else** → `ERROR 164 prototype argument is not valid object`, for STRING, INTEGER, REAL, a DATA object and the null string alike.

⛔ **NO NEW FIELD FOR THE HEADER COUNT.** `TBBLK_t.init` was *already* the one record of the creating first argument — nothing sizes on it (`TABLE_BUCKETS` is a fixed 256), it is only ever read back. Minting a second field would have been the row's own disease wearing a struct. Its default moves **10 → 11** (SPITBOL; the old 10 was CSNOBOL4's, reaching through `c_VARVAL_fn`'s `TABLE(%d,%d)` image), and the **three** places that re-typed that default collapse to one. The only `.ref` that pinned `TABLE(10,10)` is `csnobol4-suite/diag1.ref`, which has not compiled since long before this rung.

## ⛔⛔ FINDING 2 — THE 164 TURNED A GREEN TEST RED, AND THE TEST DESERVED IT

`crosscheck/rung11/1113_table` went red the moment PROTOTYPE stopped failing silently. **It had been passing vacuously.**

```
        ta = CONVERT(t, 'ARRAY')
        DIFFER(PROTOTYPE(ta), '2,2')      :f(e005)
```

`CONVERT` **failed**. `ta` stayed null. `PROTOTYPE(null)` failed the statement — and a failed statement takes **the same `:f` branch the correct answer takes**. The assertion could not tell success from total collapse. This is a general hazard of the `:f(label)`-guarded assertion, not a property of this one file, and it is worth naming: **a `:f` guard on an assertion silently accepts any upstream failure in the same statement.**

Two one-line defects underneath it, **both the same spelled-twice disease, one builtin over**:

1. **`BID_CONVERT` was answering `*out = FAILDESCR; return 1`** — *"I handled it, and the answer is failure"* — for every target type it does not implement. `return 1` is the by-name chain's **claimed**, so it shadowed `core.c`'s `_CONVERT_`, the spelling that *does* implement ARRAY / TABLE / PATTERN. It admits `nargs==2`, which is **every legal `CONVERT` call**. `CONVERT(t,'ARRAY')` and `CONVERT(a,'TABLE')` were therefore **dead on the live path across the whole corpus.** Now `return 0` — the chain's designed fallthrough — placed *after* the three arms it does implement, so a genuinely failed INTEGER/REAL/STRING conversion still answers FAIL here and never reaches `_CONVERT_`'s laxer coercion (`to_int('abc')` is 0 there; falling those through would turn a correct failure into a wrong answer of `0`).
2. **`_CONVERT_`'s array→table arm keyed the table with `VARVAL_fn(kd)`** — the plain string — while every table read and write in the runtime keys through `tbl_key_str`, which **type-tags** the key. INTEGER `7` was stored under `"7"` and looked up under `"\001i7"`, so an integer key survived the conversion into a bucket no subscript could ever reach. One more fact spelled twice, and the second copy was the wrong one.

SCRIP now matches the oracle byte-for-byte on the entire round-trip:

```
proto(ta)   = 2,2 / STRING      int key = 45      str key = dog      proto(ata) = 2 / INTEGER
```

## ⭐ THE MEASUREMENT — THE BLAST RADIUS IS ONE FALSE GREEN, AND IT WAS MEASURED, NOT ARGUED

Every number pristine (HQ-27), RT_OPT `-O0`, broad corpus (`test_corpus_snobol4.sh`; **not** `scorecard_snobol4.sh`, which runs the `programs/lon/` suite RULES.md forbids running).

| build | m3 | m4 | movers |
|---|---|---|---|
| pristine baseline, unpatched | **334/3** | **327/9** SKIP 1 | — |
| + prototype cure + 164, `CONVERT` untouched | 333/4 | 326/10 SKIP 1 | **exactly one, `1113_table`** |
| + both `CONVERT` repairs | **334/3** | **327/9** SKIP 1 | fail-set **identical by name** to baseline |

⛔ **THE MIDDLE ROW IS THE POINT AND IS WHY IT WAS BUILT AT ALL.** Landing the whole change at once would have shown 334/3 → 334/3 and proved nothing about *where* the risk was. The intermediate build isolates it: the entire rung perturbs **one program in each mode**, and that program is the vacuous pass. A pre-existing stale binary also cost a bogus `216_indirect_goto_computed` red on the first, non-pristine baseline — HQ-27 earning its keep in one command.

**Also green:** probes `proto_excess_arg` · `proto_table` · `proto_faces` in **both modes**; crosscheck rung11 **1110 / 1112 / 1113** in both modes, 1113 now for real; gates `emit_no_lang` · `template_medium_invisible` (0, ceiling 0) · `icn_no_stack` · `icn_one_reg_frame`.

**A third face proves the unification is real, not cosmetic.** A *runtime* `OPSYN` alias of `PROTOTYPE` resolves through `register_fn_alias`, i.e. through the registry — the wrong spelling. It answered `1:3` where the direct call answered `3`. Alias, `APPLY` and direct call now all answer `INTEGER 3`. **This is why `_PROTOTYPE_` was kept as a face instead of deleted:** the registry is a reachable entry point, and deleting the entry would have broken the alias rather than fixing it.

## ⛔ KNOWN, DELIBERATE, AND NOT HALF-DONE HERE — THE 164 DOES NOT HONOUR `&ERRLIMIT`

It terminates. That is a property of `core_runtime_error`, which is how **every** other builtin error code in this runtime is raised (22, 35, 42, 251, 341, 342 all call it). The Ch.16 error-to-statement-failure conversion lives in `keywords.c`'s `kwb_error`, which is `static` there and today serves only the keyword-assignment codes 208/209/210/287. **Measured, not assumed:** `&ERRLIMIT = 5` then `PROTOTYPE('abc')` still terminates. Routing the builtin codes through the ERRLIMIT-aware raiser is one general question for one rung — half-doing it inside `PROTOTYPE` would make this builtin **the only one in the runtime that converts**, which is a worse inconsistency than the one the row cures.

## ⭐ FOR THE NEXT SEAT — THREE THINGS THIS ROW PAID FOR

1. **`return 1` from the by-name chain is a CLAIM, and a claim with a `FAILDESCR` in it is a lie that shadows a working implementation.** `BID_CONVERT` is unlikely to be the last one. The audit is mechanical: grep the chain for arms that end `*out = FAILDESCR; return 1` on an **unrecognised sub-case** (as opposed to a genuinely failed one) and check whether `core.c` registers a richer spelling of the same name.
2. **A `:f(label)` guard on an assertion cannot distinguish the right answer from an upstream collapse.** Both 1113/005 and 1113/006 were vacuous for this reason, and the crosscheck corpus is written in this style throughout.
3. **When a builtin's answer depends on a creating argument, find where that argument is already recorded before adding a field.** `TBBLK_t.init` was sitting there with the wrong default; the fix was two characters and a comment, not a new struct member.

## OPEN, FILED, NOT TAKEN

- **`BID_TABLE` still ignores its third argument**, the value returned for a missing key (`TABLE(1000,,'No such word')`, manual). `TBBLK_t.dflt` exists and is unwired on the live path. Out of this row's lane; named here so it is not rediscovered.
- **`BID_TABLE` does not raise ERROR 195/196** for a non-integer or out-of-range first argument; `to_int('abc')` is 0, which silently means "default".
- **The `kwb_error` question above** — one rung, all builtin error codes, or none.
