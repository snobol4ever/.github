# FINDING 2026-09-05 hq_B — the DATA()-protection cure also skipped REGISTRATION, and that cost a snoflake pass, a mode-4 compile, and was misread by its own author as "an unrelated reason"

**Tree:** SCRIP `6e2b45a0d` (+ the one-line cure below) · corpus `fbfb7a707` · `RT_OPT=-O0` · incremental `make`
**Oracle:** `/home/resources/x64/bin/sbl -bf`, md5 `bc694a0cc699f91d06ff7fde01732000` — the POST-SWAP fixed build (CEO-282/CEO-284). 4/4 acceptance re-verified live this session.
**Row:** `snobol4-snoflake-suite-180-to-100-percent-by-class` (hq_B)

## The claim

`a865f4c32` ("snobol4: DATA() protection fires at runtime, not compile time") is **right about the abort and wrong about the registration**. It changed one prescan line from

```c
if (nb[0] && sn4_is_system_fn(nb)) { g_line = t->line; core_runtime_error(248, "..."); }  /* abort */
if (nb[0] && !dat_find_type(nb)) dat_register(sp);
```

to

```c
if (nb[0] && !sn4_is_system_fn(nb) && !dat_find_type(nb)) dat_register(sp);
```

Removing the compile-time abort was correct and is not disputed here. But the same edit added `!sn4_is_system_fn(nb)` to the **registration** condition, so a `DATA('ITEM(COUNT,TOP)')` whose *type name* is protected now registers **nothing** — the type's FIELD ACCESSORS never exist. Every later `.FIELD(x)` over that type then reaches the lowerer as a name operator over an unrecognised call and dies:

```
FATAL lower_snobol4 (GZ#5 subset): name operator over this form is outside the landed subset.
```

The runtime raise is untouched and independent (`src/runtime/core/core.c:1693`, `:3032` guard on `sn4_is_system_fn`), so registering for lowering does **not** lose ERROR 248.

## The cure (one line, `src/lower/lower_snobol4.c:2417`)

```c
if (nb[0] && !dat_find_type(nb)) dat_register(sp);
```

Register for LOWERING even when the type name is protected; the runtime still raises 248 and halts at the DATA statement.

## Measured, with corpus held constant

A control worktree at `1d7ec5246` (the commit before the regression window) with `corpus` symlinked to the SAME tree isolates the SCRIP variable exactly.

| snoflake board | m3 | m4 |
|---|---|---|
| control `1d7ec5246` | PASS=120 FAIL=53 | PASS=119 FAIL=37 SKIP(cc)=18 |
| `6e2b45a0d` (regressed) | **PASS=119 FAIL=54** | PASS=119 FAIL=37 SKIP(cc)=18 |
| `6e2b45a0d` + cure | **PASS=120 FAIL=53** | **PASS=120 FAIL=37 SKIP(cc)=17** |

FAIL-list diffs, not just counts: against control the regressed tree differs by exactly `topological-sort` in M3 (M4 lists byte-identical); the cured tree is **identical to control in M3** and **better by `topological-sort` in M4**. The cure is a net **+1 in each mode** over control and removes one compile failure.

## ⭐ The old 120 was a FALSE GREEN, and that is the half worth keeping

`topological-sort` passed before the regression **for the wrong reason**. The oracle raises `ERROR 248` at **line 20, statement 5** and halts. SCRIP printed:

```
(0) : ERROR 248 -- attempted redefinition of system function
in statement 0
(0) : ERROR 248 -- attempted redefinition of system function      <-- TWICE
```

— wrong line, wrong statement number, and emitted **twice** because SCRIP does not halt after 248 where SPITBOL does. It scored PASS only because the runner compares errors **by ERROR NUMBER** (a deliberate, documented normalization: error TEXT can never match byte-for-byte). So the board went from *passing for a hidden wrong reason* to *failing for a visible right reason*, and the cure returns it to passing while the double-print and the `(0)`/`statement 0` context remain open. **The number and the truth moved in opposite directions.** The residual double-print is exactly what the already-`DONE` row `snobol4-data-of-a-system-function-name-is-error-248-and-the-continuing-error-line` was named for.

## ⛔ The author's own witness told them, and it was read as unrelated

`a865f4c32`'s message says: *"SPITBOL testpgms test6.spt itself can't be used as this witness -- it fails to compile under mode 4 for an unrelated reason, a name-operator pattern-match/EVAL form outside the landed subset."*

It was **not unrelated** — it is this very defect. `test6.spt` contains `DATA('ITEM(...)')`. Measured:

- pre-`a865f4c32` (`1d7ec5246`): `--compile` → rc=1, compile-time 248 abort, no code emitted
- post-`a865f4c32`: `--compile` → the name-operator FATAL (the "unrelated reason")
- with the cure: `--compile` → **rc=0, compiles clean**

A witness that the change itself broke was recorded as a pre-existing limitation of an unrelated subsystem. ⭐ **The general form: when a change's own excluded witness fails, the first hypothesis must be the change, not the subsystem it names.**

## Blast radius — measured corpus-wide, not estimated

The new behavior differs from the old **only** when a DATA type name is a protected system function. Censused across every `.sno`/`.spt`/`.sc` in the corpus: **61 distinct DATA type names, exactly one protected — `ITEM`** — in exactly **4 files**:

- `packages/snobol4/snoflake_suite/topological-sort.sno` (this row — cured, +1 both modes)
- `packages/snobol4/spitbol_testpgms/test6.spt` (now compiles; **board unmoved** — that suite scores test6 as UNSCORED because the *oracle* refuses it, `ERROR 248` + post-mortem)
- `benchmarks/snobol4/testpgms.spt`, `benchmarks/snobol4/testpgms-test6.spt`

The SNOBOL4 **master** suite contains **16** distinct DATA type names, **none protected**, and **zero** computed (non-literal) DATA specs — the prescan only handles `TT_QLIT`. So the change is **structurally incapable** of moving the master board, and likewise gimpel / csnobol4 / dotnet / aisnobol, none of which contain a protected DATA type. ⭐ This is a stronger statement than "I ran those boards and they did not move": it says *why* they cannot.

## ⛔ How it escaped — the row closed on a gate too narrow to see it

Both owning rows (`snobol4-name-operator-over-this-form`, `snobol4-data-of-a-system-function-name-is-error-248-and-the-continuing-error-line`, hq_C) are `DONE`. The landing gate `test_gate_sno_data_protect_mode4.sh` compiles and runs a **minimal protected-DATA witness** and asserts 248 fires and execution stops — it passes both before and after the regression (verified: rc=0 on the cured tree too), because the minimal witness has **no field access after the DATA statement**. The defect lives precisely in what the witness omits. ⭐ Same family this row keeps hitting: an instrument that answers a narrower question than the one being asked, and never says so.
