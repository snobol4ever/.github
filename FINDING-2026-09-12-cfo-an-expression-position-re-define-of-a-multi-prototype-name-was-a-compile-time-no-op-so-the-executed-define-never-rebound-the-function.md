# FINDING 2026-09-12 (cfo): an expression-position re-DEFINE of a multi-prototype name was a compile-time no-op, so the executed DEFINE never rebound the function

**Row:** `snobol4-gimpel-recursive-list-functions-overflow-the-call-stack-where-spitbol-completes` (CEO-630 route; gate `test_gate_sno_define_prototype_follows_the_executed_define.sh`).
**Witness:** the master entries `user_function_26`, `user_function_replace_10`, `user_function_replace_branch_1` (the 1011_func_redefine shape):

```
        DEFINE('myfunc(n)')                            :(myfunc_end)
myfunc  myfunc = n * 2                                 :(RETURN)
myfunc_end
        DIFFER(DEFINE('myfunc(myfunc)', 'myfunc2'))    :f(e002)
e002    :(myfunc2_end)
myfunc2 myfunc = NE(myfunc, 1) myfunc * myfunc(myfunc - 1) :(RETURN)
myfunc2_end
        NE(myfunc(4), 24)                              :f(e003)
```

SPITBOL prints `PASS 1011_func_redefine (3/3)`: after the second DEFINE runs, `myfunc(4)` is 24. On the tree where the executed DEFINE's prototype and entry bind the name (the SITE-ENTRY seal of this landing), both modes printed `FAIL 1011/003` with `myfunc(4)=8` -- the FIRST body, the one the first executed DEFINE bound, was still in force.

## The mechanism, measured

1. `src/lower/lower_snobol4.c` lowers a literal-prototype DEFINE in EXPRESSION position (here the subject of `DIFFER(...)`) whose name was already registered at prescan to a bare `LIT_STRING ""` -- a compile-time no-op, on the design that the hoisted textual DEFINE had already bound the winner (last-textual-wins). `--dump-ir` shows `DIFFER [LIT_STRING "", LIT_STRING ""]` and no DEFINE node in the statement; a gdb trace on the run shows `rt_define_site` and `rt_define_site_entry` once (the first DEFINE) and `_DEFINE_`/`DEFINE_fn_entry`/`rt_sno_runtime_define` never.
2. Before this landing the witness PASSED by accident: a multi-prototype name gets no compiled proc, so `p->fn` stayed NULL, and the call fell to `rt_call_proc_descr`'s dynamic branch, which resolves `core_define_entry_label(name)` -- an entry-label table filled at startup in TEXTUAL order, so the LAST textual DEFINE's entry (`myfunc2`) won. The right answer for the wrong reason: the same table gives the wrong answer for every program whose executed order differs from the textual order, which is exactly what the row's gate measures.
3. With the SITE-ENTRY seal (the executed DEFINE resolves its entry BY NAME when the statement runs and writes it into `p->fn`), the first DEFINE binds `LBL__myfunc`, the second DEFINE never runs (item 1), and `myfunc(4)` is 8.
4. Lowering the expression-position DEFINE of a multi-prototype name as the real runtime call (`IR_CALL "DEFINE"` -> `_DEFINE_`) reached the next hole: `rt_sno_runtime_define` cleared `p->fn` to NULL and the call site (`rt_proc_call_open` -> `rt_proc_fn` -> `jmp rax`) jumped through `rt_ab_undef_fn_stub` -- `error 22: Undefined function called`, both modes. The dynamic branch in `rt_call_proc_descr` that would have resolved the entry label is not on this call site's path.

## The cure (SCRIP, this landing)

- `lower_snobol4.c`: a literal DEFINE in expression position for a name the prototype census marks MULTI-PROTOTYPE is no longer shortcut to `""` and no longer refused as "outside the landed subset"; it lowers as the generic builtin call so `_DEFINE_` runs when the statement runs.
- `rt.c` `rt_sno_runtime_define`: after the re-DEFINE clears the record, it resolves `core_define_entry_label(name)` through `rt_entry_resolve` and, for a non-fragment entry, writes it into `p->fn` with `jmp_entry = 1` -- the same binding `rt_define_site_entry` writes for a literal site, so the compiled call site enters the executed DEFINE's body.
- `bb_define.cpp` + `emit.cpp/.h` + `rt.c`: the SITE-ENTRY seal (a multi-prototype literal DEFINE resolves its entry by name when it runs) and the per-site prototype replacement in `rt_define_site` (the executed DEFINE's formals replace the record's), from the earlier part of this sitting.

**Measured:** `myfunc(4)=24`, `PASS 1011_func_redefine (3/3)` in m3 and m4; the three master entries PASS in m3 from the include directory; the row gate, `test_gate_define_alternate_entry.sh` and `test_gate_sno_define_redefinition_per_binding_dispatch.sh` GATE OK; the 40 `test_gate_sno_*` arms censused with the exit captured FIRST (`rc=$?` before any echo -- the CFO-63 instrument error corrected): see the landing's cursor line for the count.

## Not this landing

`test_gate_snocone_returns_codegen.sh` (row `snocone-returns-codegen`, FREE) is red on origin/main before and after this diff with an m4 LINK error: `fn_freturn.sc` references `body_cell$pos` (the M4-BODY-SEAL at the DEFINE site) and no compiled proc emits the cell's data. Whether today's define landings changed that gate's failure shape is being measured on a worktree at `4bcd6bd21^`; the result goes to the cursor, not here.
