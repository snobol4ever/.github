# FINDING 2026-09-03 hq_C — the runtime clause define was missing six registration steps, and mode 4 only ever needed `bb_pool_init()`

**Row:** `prolog-rung-10b-assert-retract-abolish-clause-the-dynamic-database` (REOPENED by ceo 22:12 on Lon's override: *"The clauses are compiled to Byrd Boxes, so then should the dynamic calls to add and remove the code. It is all code not data."*)
**Tree:** SCRIP `wip/prolog-compiled-clause-db-r2` (`6d62b64be`, rebased onto main `31a2feca7`) · corpus `a0fd13004` · incremental `make`, `RT_OPT=-O0`.

## What was measured

`pl_runtime_define_pred` (`src/lower/lower_prolog.c`) performed **5** of the **20** per-proc steps the mode-3 driver performs at `src/driver/scrip.c:1684-1710`, and **inverted the two arguments it did pass**:

| | compile-time (m3 driver) | runtime (before) |
|---|---|---|
| `emit_jmp_entry_for_proc` | `(pname, dyn_scope=0, is_generator=1, g)` | `(key, 1, 0, g)` — **both inverted** |
| `rt_proc_set_generator` / `_jmpentry` / `_dyn_scope` | yes | **missing** |
| `g_gen_proc_active` around the emit | `= is_generator` | **missing** |
| `g_flat_frame_floor` seed | yes | **missing** |
| `g_flat_dc_np`, `rt_proc_set_dcfn` | yes | **missing** |
| `rt_proc_set_zstatic`, `emit_patzeta_register` | yes | **missing** (both `extern`-declared in the function and never called) |

`pl_new_proc` sets `is_generator = 1` for **every** Prolog proc and never sets `dyn_scope`, so the correct pair is `(0, 1)`. Those two feed `g_emit.flat_lex` and `g_emit.flat_gen` (`emit.cpp:3634-3635`), i.e. the fragment was emitted under the wrong frame discipline.

⭐ **The template already existed.** `src/runtime/runtime_eval.c:149-193` is SNOBOL4 CODE/EVAL's runtime compile — the sanctioned, landed sibling for *build a graph at run time and register it*. The cure was to mirror it step for step, not to invent a sequence.

## Mode 4 was a one-line defect wearing a scary hat

`eval_build_chain` calls `bb_pool_init()`; `pl_runtime_define_pred` did not. Without it the first `assertz` aborted with `bb_alloc: pool not initialised`, which the ladder reads as **NOBUILD** — indistinguishable from *the compiler refuses this construct*. With it, **mode 4 runs the dynamic database correctly, unbound argument included**.

## What is still red, and it is exactly one thing

`test_gate_prolog_dynamic_db_both_modes.sh` (added on the branch) runs four arms — {ground, unbound} × {m3, m4}. **Three PASS; `m3 unbound` is the sole red.**

- `assertz(p(1)), q(1)` → ground argument, m3 **correct**.
- `assertz(p(1)), p(X)` → unbound argument, m3 **ERROR 246 stack overflow**; gdb shows infinite recursion in `c_VARVAL_fn` (`src/runtime/core/core.c:1987`) — a **self-referential binding**, the arg cell holding a var-ref to itself.

**Exonerated by measurement, so nobody re-chases them:** the emitted body (a *within-mode* text diff of the runtime fragment against the compile-time emission of the same predicate is identical but for node ids); the direct-call path (`SCRIP_NO_DC=1` still fails, and `rt_pl_dc_ok` requires `!is_generator`, false for every Prolog proc); the const-unify leaf (`SCRIP_NO_CU=1` still fails); the optimizer (`SCRIP_OPT=0` still fails); proc registration (now mirrors the sibling exactly).

**The lead:** `SCRIP_PL_TRACE=1` **and** `SCRIP_PORT_COUNTS=1` *both* make the failing witness print the right answer. Two independent instruments sharing only *emit more instructions at port sites* — which points at **uninitialised or stale frame storage** in the mode-3 fragment's frame, consistent with m4 (different frame allocation) being clean.

## ⭐ The general form — A CROSS-MODE ASM DIFF IS NOT EVIDENCE, AND IT LIES CONFIDENTLY

My first root cause was wrong in a way worth recording. I diffed the **m4** compile-time emission of `p/1` against the **m3** runtime fragment and found what looked decisive: the unify arg pair at `[rbp+48/56]` in one and `[rbp+16/24]` in the other — where `[rbp+16]` is exactly the parameter cell, so it read as *the scratch allocator is overwriting the argument*. It was a complete, mechanical, plausible story, and it was an artifact of comparing two modes that are **permitted to diverge** (RULES.md § MODES MAY DIVERGE). Re-scoped **within m3**, the two emissions are identical.

CLAUDE.md already carries the rule — *"SCOPED TO ONE MODE since MODES MAY DIVERGE"* — and I walked into it anyway, because the diff produced a *better* story than a null result would have. **A cross-mode diff does not fail loudly; it hands you a defect-shaped answer.** The cheap guard is the one the law states: before believing an emission diff, name the mode of both arms.

The instrument that makes the correct diff cheap is now in the tree: `SCRIP_PL_RTASM=1` dumps the emission as text on **both** the runtime and the compile-time path, so the within-mode comparison is one `diff`.

## ⭐⭐ ROOT CAUSE FOUND AND CURED — a runtime-built graph inherited another graph's frame offsets

**`ze[]`/`zx[]` are a GLOBAL, append-only index keyed by NODE POINTER**, and `zx_find` resolves purely by that pointer (`src/ir/zeta_storage.c`). A graph built at **run time** — an asserted clause — is built *after* earlier graphs have come and gone, so a **recycled node address silently inherits the earlier graph's offset**.

Measured, with the instrument added on the branch:

```
[RTASM] p/1: nodes=7 nparams=1 zls_region=128 max_granted_cell=160 *** CELL OUTSIDE REGION ***
[RTASM]   node[6] op=49 off=160 scope=1 root_scope=3 *** STALE ENTRY FROM ANOTHER GRAPH ***
```

The asserted clause's `IR_LIT_INTEGER` resolved to an entry in **scope 1** while its own graph's root scope was **3**, taking offset **160** into a graph whose region is **128** — and 160 is exactly `main/0`'s `+160` local in the `--dump-zeta` listing.

**Why an out-of-region cell is fatal.** The prologue saves `r13` at `[rsp+168]`; `p/1_γ` compares `[rbp+168]` against `r13` and `p/1_ω` restores `r13` from it. The literal's payload overwrote that slot, so `p/1_ω` restored **`r13 = 1`** and the backtrack register was destroyed — surfacing as a self-referential binding and an unbounded `c_VARVAL_fn` deref (ERROR 246). `rt_jmp_frame_lexprep2(fb, 128, 144)` memsets exactly `[0,144)`, so nothing zeroes or protects `[144,208)`.

**Cure:** `zls_forget_graph_nodes()` drops a graph's nodes from the index before granting, so every node is granted fresh in its own scope. **Additive** — compile-time graphs never meet this (all are built before any is emitted, nothing is freed between) and no existing caller invokes it, so no other frontend's behaviour changes. Gate now **GREEN on all four arms**, rungs 0-9 at 56/56.

## ⭐ Why it read as a heisenbug, and what that shape means

Whether an address is recycled depends on allocation history, so **anything** that shifts allocation moved the colliding cell onto something benign: `SCRIP_PL_TRACE=1`, `SCRIP_PORT_COUNTS=1`, and merely writing `write(a), nl,` before the assert each "cured" it. Two *independent* instruments cured it, which is what finally ruled out the instruments themselves and pointed at storage.

⛔ **The trap this sets:** every one of those cures is a plausible fix. Switching on a trace and seeing the right answer invites "the trace is fine, ship it". The discriminator was the **control**: a static clause (`p(1).`) passes the *canonical* unbound variable — a 2-hop chain ending in a zeroed cell — while the failing run passed a **self-reference**. Without that control arm, the self-reference reads as the normal WAM representation of *unbound* and the whole investigation goes the wrong way.

## Handoff

Rank-0 row `prolog-rung-10b-m3-unbound-arg-self-binds-when-the-clause-is-runtime-compiled` minted and assigned to **seat06**, DONE-WHEN = the gate above, proven RED as written.
