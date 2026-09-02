# FINDING g-stage2-bbp-reads-may-blind-icon-generators-and-prolog-bb-dispatch-under-compile — CENSUS DONE ON 3/5, ONE OPEN LEAD FLAGGED, NOT CURED

## CONTEXT
Working row `prolog-g-stage2-runtime-reads-may-be-blind-under-compile` (the by-name-lookup census sibling-gap minted off C47, see `FINDING-2026-09-02-seat14-prolog-static-predicate-check-reads-compile-time-only-table.md`). That row's own brief scoped itself to `grep -n g_stage2 src/runtime/by_name_dispatch.c src/runtime/runtime_eval.c` — two files. This finding is about what turned up outside that scope.

## SCOPE WAS UNDERCOUNTED
`grep -rl 'g_stage2\.' src/runtime/` returns **5** files, not 2: the brief's `by_name_dispatch.c`/`runtime_eval.c`, plus `src/runtime/invocation.c`, `src/runtime/builtins/resolution.h`, `src/runtime/builtins/gen_runtime.h`. Worth naming as its own small lesson: a row's own illustrative grep command is not automatically its true boundary — re-run it unrestricted before trusting a brief's file list, especially on a census-shaped row where the whole point is exhaustiveness.

## 3 OF 5 FILES: CENSUSED, NO LIVE BUG
Full detail lives in the task baton (`prolog-g-stage2-runtime-reads-may-be-blind-under-compile.task.md`, ## CENSUS section), summarized here:
- **by_name_dispatch.c** (~16 g_stage2 call sites): every one is either (a) gdb-CONFIRMED safe — a `rt_proc_has_native_fn`/registry check already succeeds for every real user procedure at m4 runtime, verified directly (witness below), so the g_stage2 fallback is dead-but-harmless; or (b) dead code with zero live callers (`proc_as_value()` and everything downstream of the entry_pc-tagged value encoding it alone constructs — the live constructor, `rt_proc_value()` in `src/runtime/rtx/rtx_icncall.s:53-57`, uses an entirely different, always-safe name-sentinel encoding instead).
- **runtime_eval.c** (3 sites): all inside SNOBOL4's `EVAL()`/`CODE()` runtime-metaprogramming machinery, all self-referential (`pc0 = g_stage2.proc_count` captured immediately before this process's own `lower_snobol4()` call, only ever iterate forward from there) — correct in both modes by construction, never assumes g_stage2 holds the original program's procs.
- **invocation.c** (1 site, `proc_table_call()`): the g_stage2 read is provably inert — the enclosing `if` returns `FAILDESCR` on both branches unconditionally. Comment confirms this is an intentional "behaviour-preserving" stub left after a genuinely dangerous predecessor (`sm_call_proc`, an unconditional-abort landmine) was deleted 2026-08-27.

**Method note for whoever measures the open lead below:** the one gdb witness that mattered most here was proving `rt_proc_is_registered`/`rt_proc_has_native_fn`/`rt_proc_index_of`/`rt_proc_nparams` all correctly see an ordinary user proc in an m4 binary, DESPITE `g_stage2.proc_count` being simultaneously and correctly 0 in the same process:
```
$ scrip --compile -o w.s w.sno && as -o w.o w.s && gcc -no-pie -o w w.o -Lout -lscrip_rt -lm -Wl,-rpath,.../out
$ gdb -batch -ex 'break exit' -ex run -ex 'print rt_proc_index_of("DOUBLE")' -ex 'print rt_proc_is_registered("DOUBLE")' \
      -ex 'print rt_proc_has_native_fn("DOUBLE")' -ex 'print rt_proc_nparams("DOUBLE")' -ex 'print g_stage2.proc_count' ./w
$1 = 0      # index found
$2 = 1      # registered = true
$3 = 1      # has_native_fn = true
$4 = 1      # nparams correct (DOUBLE takes 1 arg)
$5 = 0      # g_stage2.proc_count -- simultaneously empty, exactly as C47's own finding measured
```
i.e. C47's fix commit's claim ("g_rt_gen_procs is populated identically in both modes") is not just plausible, it's independently gdb-verified true for the general case, not only for the one predicate C47 happened to test.

## OPEN LEAD, NOT MEASURED — the actual reason for this FINDING

`resolution.h` and `gen_runtime.h` (both under `src/runtime/builtins/`) each define a `static inline` function reading a **different g_stage2 field**, `.bbp` (not `.proc_table`/`.proc_count` — so NOT covered by C47's fix, and structurally outside what "g_stage2.proc_count/proc_table" in this row's own GOAL text describes):
```c
// resolution.h ~line 25 -- Prolog side
static inline IR_graph_t *bb_graph_of_pred(const Resolve_PredEntry_BB *e) {
    if (!e) return NULL;
    if (e->bb_idx >= 0 && e->bb_idx < g_stage2.bbp.count) return g_stage2.bbp.table[e->bb_idx];
    return NULL;
}
// gen_runtime.h ~line 40 -- Icon side (same file as GenFrame/suspend_val/every_gen[]/GeneratorState)
static inline IR_graph_t *bb_graph_of_proc(const ProcEntry *e) {
    if (!e) return NULL;
    if (e->bb_idx >= 0 && e->bb_idx < g_stage2.bbp.count) return g_stage2.bbp.table[e->bb_idx];
    return NULL;
}
```
Same shape as the C47 bug (index into a g_stage2 sub-table that is compiler-internal, populated only during lowering). **Not yet gdb-measured whether `g_stage2.bbp.count` is 0 in an m4 binary the way `.proc_count` was proven to be** (very likely, same struct, same population story — but C47's whole lesson is that "very likely" is exactly the failure mode the INSTRUMENT LAWS exist to catch, so this is explicitly NOT being asserted as fact here).

**Why this could be more severe than anything C47 or the rest of this census covered, if it measures live:** `gen_runtime.h` is Icon's generator/coexpression frame header. If `bb_graph_of_proc` is on the path Icon's `suspend`/`every`/generator-resume machinery uses at runtime to re-enter a generator body, this would mean Icon generators are silently broken under `--compile` for any program exercising that path — not a narrow introspection builtin, a core language feature. Same reasoning for `resolution.h`'s Prolog twin (`Resolve_PredEntry_BB`, cut barriers, trail) and whatever dynamic-predicate-dispatch path uses it.

**Equally plausible, not ruled out:** both functions are called only from compiler-internal code (codegen deciding how to emit a call), in which case this is a non-issue, same as `proc_as_value` turned out to be. The two hypotheses are genuinely open. Caller trace is the needed next step: `grep -rn 'bb_graph_of_pred\|bb_graph_of_proc\|resolve_bb_graph_at\|bb_proc_entry' src/`, sort callers into src/runtime/ (runtime-reachable → suspect, needs the gdb witness) vs src/emitter/ or src/templates/ (compiler-internal → likely safe, same as C47's own exonerated `rt_proc_call_open_det` red herring).

**Deliberately NOT minted as its own queue row by seat09** — it is recorded here and in the working row's own ## NEXT so whoever picks up either has full context; ceo/hq may want to re-rank it given the severity ceiling described above, or fold it into the same row's continuation. Not blocking; recorded and moving on per protocol.

## LINKS
Row: `prolog-g-stage2-runtime-reads-may-be-blind-under-compile` (still OPEN, claimed by seat09 at time of writing) · sibling/parent: `FINDING-2026-09-02-seat14-prolog-static-predicate-check-reads-compile-time-only-table.md` (C47) · SCRIP HEAD at time of this census: `d9e4ac2a1`.
