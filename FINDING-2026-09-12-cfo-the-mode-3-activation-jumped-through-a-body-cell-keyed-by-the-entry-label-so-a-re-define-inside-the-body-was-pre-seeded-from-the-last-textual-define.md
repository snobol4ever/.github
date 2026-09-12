# FINDING 2026-09-12 cfo — the mode-3 activation jumped through a body cell keyed by the ENTRY label, so a DEFINE executed inside a function body was pre-seeded from the last TEXTUAL DEFINE

**Seat** cfo · **Mode** TRIO (CEO-619, SNOBOL4 to 100%) · **Tree** SCRIP `3e99f5306` + this cure · **Oracle** `sbl -bf`
**Row** `snobol4-define-alternate-entry-binds-one-entry-for-the-whole-program` (hq_P's, rank 0, served by `next` as the blocker of `snobol4-gimpel-recursive-list-functions-overflow-the-call-stack-where-spitbol-completes`).

## What the row said, and what was left of it

hq_V's finding of 09-08 and the cto's 4bcd6bd21 (09-12 10:44) cured the whole-program bake: the dentry table now reads each bind node's own entry operand, and mode 3 binds BY NAME at run time through `rt_define_bind_body`. The cto's gate `test_gate_sno_define_entry_label_rebinds_at_runtime.sh` is green in both media. **The row's own gate `test_gate_define_alternate_entry.sh` was still RED in mode 3 and green in mode 4** on origin `47c2fba7a` (measured 13:2x CDT, first thing):

| witness (three DEFINEs, alternating entries, each executed INSIDE the body of the previous entry) | `sbl -bf` | m3 before | m4 before |
|---|---|---|---|
| `alt3.sno` (the gate's) | `E0 v · E1 v · E2 v · done` | `E2 v · done` | `E0 v · E1 v · E2 v · done` |

⭐ **Why the cto's gate could not see it.** Its witness's last TEXTUAL DEFINE is `DEFINE('G(L)T')`, the DEFAULT entry. hq_V's original witness ends on `DEFINE('F(X)', 'F')`, the default entry too. A defect of the shape "the binding is pre-seeded from the last textual DEFINE before any DEFINE executes" reads CORRECT on both of those by accident. The row's gate ends on `F_2`, so it reads it. The minimal witness that isolates the seeding (no recursion at all):

```
	DEFINE('F(X)')                  :(FEND)
F	OUTPUT = 'A ' X                 :(RETURN)
F1	OUTPUT = 'B ' X
	DEFINE('F(X)', 'F1')             :(RETURN)
FEND
	F('one')
END
```
oracle `A one` · m3 before **`B one`** · m4 before `A one`. The second DEFINE never executed and still won.

## Where it was, measured not guessed

A two-line `fprintf` in `rt_define_site` and `rt_define_bind_body` (reverted before the build that was graded) showed mode 3 doing the RIGHT thing at the runtime edge: the first DEFINE execution called `rt_define_bind_body("F","F")` and wrote `LBL__F`'s address into the cell keyed `body$F`. The call still landed at `F1`. So the activation was not reading `body$F`.

`src/templates/bb/bb_define.cpp` role 4 (the activation): the text medium jumps through **`body_cell$<fn4>`**, keyed by FUNCTION name, initialised `.quad LBL__<entry>`; the binary medium's twin pointer was **`bb_ab_fn_cell_ptr("body$" + en4)`**, keyed by the ENTRY label `en4 = lbl_t0 ? lbl_t0 : fn4`, and for the proc-graph DEFINE that emits the activation `lbl_t0` is the last textual entry (`F_2`, `F1`). `rt_define_bind_body` writes `body$<fname>`; the driver's `m3_seal_entry_cells(_ln + 5, fn, 0)` seeds `body$<label>` <- `LBL__<label>` for every label. So in mode 3 the activation jumped through `body$F1` (seeded to F1, never rewritten) while every DEFINE execution rewrote `body$F`. **Text and binary keyed the same cell by two different names** -- the same (pointer,label) pair class 4bcd6bd21 named one line further up, in the line below it.

## The cure (one key)

`bb_define.cpp:574`: the binary pointer is now `bb_ab_fn_cell_ptr("body$" + fn4)` -- the function name, the text medium's key and `rt_define_bind_body`'s key. The initial value is the default entry because the driver seeds `body$<fn>` from the function's own label; the first executed DEFINE rewrites it before any call can succeed. One line, one file. The dentry table in `src/driver/scrip.c` is untouched.

## Measured after

| witness | m3 | m4 |
|---|---|---|
| `alt3.sno` (row gate) | oracle-equal | oracle-equal |
| `hoist.sno` (the seeding isolate above) | oracle-equal | oracle-equal |
| hq_V's 09-08 witness (`A one B two A three`) | oracle-equal | oracle-equal |

Row gate green both modes (was RED m3 on the pre-cure binary, the fail-once arm); the cto's sibling gate stays green; `make preflight` 33/0. The row gate is WIRED into `test-sequential` and promoted RULING -> WIRED in `gate_wiring.tsv` by `util_gate_wiring.py adopt`, exactly as its RULING said ("wired in the commit that makes it green").


## ⭐ The master, per entry, pre-cure against cured -- and three passes that were arithmetic coincidences

Both binaries graded through the harness under the CEO-619 override, both modes. **Mode 4 is identical entry for entry.** Mode 3 moves exactly five entries:

| entry | m3 before | m3 after | m4 (both) |
|---|---|---|---|
| user_function_replace_4 | XFAIL | **PASS** (marker promoted, corpus `87363f181`) | XPASS -> PASS |
| user_function_replace_7 | XFAIL | **PASS** (promoted) | XPASS -> PASS |
| user_function_26 | PASS | **FAIL** | FAIL |
| user_function_replace_10 | PASS | **FAIL** | FAIL |
| user_function_replace_branch_1 | PASS | **FAIL** | FAIL |

⛔ **The three were passing by coincidence, not by being right.** Each checks its FIRST definition at n=3 (`rd(3) = 6`, `myfunc(3) = 6`) and its REDEFINITION is factorial: 3! = 3*2 = 6. A mode 3 that ran the last textual prototype's body for every call (the pre-cure seeding) prints the wanted number on both checks and cannot be told from a right one at that operand. Measured with the key behind a one-build env switch (both arms off one binary, the runner header's own advice): pre-cure arm `rd(3) = [6]`, cured arm `rd(3) = [0]`, mode 4 `[0]` -- the cured arm runs the RIGHT body (`rd = n * 2`) and finds `n` unbound, because the activation binds the argument into the LAST textual DEFINE's formal name (`rd`, from `DEFINE('rd(rd)', 'rd2')`): `bb_scc_probe(fn4)` reads the prototype the compile-time registration ended on, and the formal/local NAMES are baked exactly the way the entry was. **So the entry is cured and the prototype is not** -- one defect with COPYL's re-DEFINEd locals list, and the reason those three fail in mode 4 today. The published row is the AND of both modes: it gains two and loses nothing; mode 3 alone loses three coincidences into mode 4's honest verdict, named here so nobody bisects them to this commit as a regression.

**The next cure, precisely:** each DEFINE site must carry its own prototype (formal and local names, `sno_def_t` has them at lowering and the bind node does not), and the activation a call reaches must bind by the prototype of the DEFINE that executed last -- either one activation variant per distinct prototype with the DEFINE site selecting it (the entry cell's twin), or an activation that reads `p->pnames` at run time. `rt_define_site` already updates `p->nparams`/`nformals` but never `pnames`, and the DEFINE site passes the compile-time `rt_define_query` csv, not its own.

## ⛔ What this does NOT cure, and it is the unblocked row's real subject

`gimpel-linked-list-functions` (snoflake) still fails in BOTH modes, now identically and later: `ERROR 235 -- subscripted operand is not table or array` at statement 28, `COPYL = T<L>`. Gimpel's `COPYL.INC` re-DEFINEs `COPYL(L)T` as `COPYL(L)` (entry `COPYL_1`) -- it changes the LOCALS LIST as well as the entry, so that the inner calls no longer save-and-null `T` and the memo table set in the outer activation stays visible. Our activation's save list (`np4/ns4/nf4`, the frame layout `T4 = 16*xt4+32`) is computed once per function at emit time; the inner call still saves and nulls `T`, so `T<L>` reads null. `rt_define_site` already updates `p->nparams`/`p->nformals` for the re-DEFINE, and `p->redefined` is never set now that both media rebind through the cell (fn is the same activation), so nothing routes the call to the runtime prologue that would honour the new list. That is a second defect with its own witness and belongs to the row this one unblocked; snoflake stays 117/124 across this cure (runner-measured, both modes, nothing traded).

## A note on a control witness that is NOT this row

A call BEFORE any DEFINE has executed (`X = F('a')` above the DEFINE): oracle `ERROR 022 -- undefined function called`; SCRIP runs the function in both modes. Pre-existing -- MEASURED identical on the pre-cure binary (stash, rebuild, both modes) -- compile-time registration; not cured here, named so nobody reads it as fallout.
