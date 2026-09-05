# FINDING — `LABEL()` and `FUNCTION()` both lose their registration data in mode-4, by the same mechanism, independently

**Seat:** seat10 · **Date:** 2026-09-05 · **Mode:** FLEET-16 (hq_P lane, SNOBOL4 ONLY)
**Row:** `snobol4-csnobol4-label-function-lost-output-in-compiled-mode`
**Tree:** SCRIP `1d7ec524` (pre-fix) · corpus `edd942262` · oracle `/home/resources/x64/bin/sbl -bf`

## 1. The shape, found once and then found again

Both builtins fail in `--compile` (mode-4) for the same reason: something that is populated by
walking the AST **inside the `scrip` compiler process itself** during compilation, and that table's
contents happen to survive into execution **only because mode-3 keeps running in that same process**.
A `--compile` binary is a second, separate process with none of that state — it starts cold, and
nothing in its own startup path ever repopulates the table.

### 1a. `LABEL(name)` — always FAILDESCR in mode-4

`_LABEL_` (`core.c:1410`) asks `_label_exists_hook`, a function pointer set exactly once, at
`scrip.c:1101-1102`, as part of the `scrip` driver's OWN mode-3 execution setup. `_label_exists_fn`
(`driver_hooks.c`) answers from `label_lookup()`, which walks `g_stage2.label_table` — built by
`label_table_build()` from the AST, called once per compile via `polyglot_init` → `sm_preamble`.
A `--compile` binary's generated `main:` never runs any of `scrip.c`'s mode-3 setup, so
`_label_exists_hook` stays NULL for the binary's whole life and `_LABEL_` returns `FAILDESCR`
unconditionally — proven with `label.sno` reduced to one call (`t2_label_builtin.sno` in the LEDGER
below): m3 prints `TEST`, m4 prints nothing, rc=0 both times.

### 1b. `FUNCTION(name)` — always FAILDESCR in mode-4, independently

`_FUNCTION_` (`core.c:1400`) asks `FNCEX_fn(name)`, which walks `_func_buckets` — populated by
`DEFINE_fn()`, called (among other places) from `prescan_defines()` (`driver_label.c`), which ALSO
only ever runs once, during compilation, inside the `scrip` process. The runtime execution of a real
`DEFINE(...)` statement, in **either** mode, goes through `rt_define_site()` (`rt.c:1770`), confirmed
by breakpoint in both m3 and m4 (see LEDGER) — and `rt_define_site` only ever touches `rt_proc_t`
(`rt_proc_register`/`rt_proc_find`), never `_func_buckets`. So `_func_buckets` never contains a
user-DEFINE'd name in **either** mode; mode-3 only looks correct because `FNCEX_fn` happens to be
called from inside the same process that ran `prescan_defines` moments earlier at compile time.
Confirmed by breakpoint on `FNCEX_fn`: `FNCEX_fn("TEST")` returns **1** in the `scrip` process (m3),
**0** in the standalone compiled binary (m4), same call site, same argument, same build.

## 2. The fix — two small, independent patches, same idea: give mode-4 its own copy of what it needs

**No new global variables in either patch** — both reuse existing storage (`g_stage2.label_table`,
`rt_proc_t`) and existing accessors (`_label_exists_fn`, `rt_proc_find`).

**(a) LABEL** — the emitter already tracks every compile-time-known label (`g_stage2.label_table`,
filled at compile time regardless of target mode). `src/driver/scrip.c`'s mode-4 `main:` prologue
(the `is_icon || is_raku || is_sno_bb || is_prolog` shared BB path) now also emits a `.rodata` table
of every label name plus one call, mirroring the existing `__gva_names`/`gva_register` pattern used
right above it for the same class of problem:
```
lea rdi, [rip + __label_names]
mov esi, <label_count>
call rt_label_table_install@PLT
```
The new runtime function (`driver_hooks.c`, linked into `libscrip_rt.so` same as everything else this
prologue calls) re-derives exactly what `label_table_build()` would have built, then arms the
existing hook: `stage2_label_grow` + set `.name`; `.stmt` is set to a non-NULL sentinel (`(tree_t*)1`,
never dereferenced by mode-4 code — only `label_lookup`'s `!= NULL` test reads it) because
`label_lookup` returns `.stmt` itself and a NULL `.stmt` would silently make every label look absent
again. Then `core_set_label_exists_hook(_label_exists_fn)` — same hook, same reader, now armed from
inside the compiled binary instead of from `scrip.c`.

**(b) FUNCTION** — deliberately NOT fixed by replaying `prescan_defines`-style bookkeeping (that would
mean re-deriving DEFINE spec strings in the emitter and calling `DEFINE_fn` per proc — more moving
parts, more places to get nparams/locals subtly wrong for a value nothing downstream actually reads
in the common path). Instead, `FNCEX_fn` (`core.c`) falls back to the table that mode-4 ALREADY
populates correctly at runtime — `rt_proc_t`, via a one-line wrapper `rt_proc_name_exists()`
(`rt.c`, beside its siblings `rt_proc_decl_level` etc.) added to `rt_proc_find`, which is a cached
O(1) hash lookup (verified: no recursion back into `FNCEX_fn`, so no cycle risk). This is the more
general fix — it also strengthens `_usercall_hook`'s own `if (FNCEX_fn(name))` fallback dispatch for
every frontend sharing this driver code, not just SNOBOL4's `FUNCTION()`.

## 3. Verified, in order

1. Task's own DONE-WHEN: PASS (`label.sno` mode-4 → `foo/TEST/END/BAR`; `function.sno` mode-4 →
   `foo/BAR/TEST/DEFINE`, both exact).
2. `make test`: all gates green except `test_corpus_snobol4.sh`'s REFUSAL on 4 programs hitting the
   120s per-program bound under fleet load (load 15.7 on 16 cores at the time) — the script's own
   documented false-refusal class, not a correctness signal; not re-chased further because (3) and (4)
   below are the properly-scoped, fast, directly-relevant tests for this change.
3. `bash scripts/test_snobol4_csnobol4_suite.sh` (the suite `label.sno`/`function.sno` actually live
   in — NOT the master `ALL.sno`, which contains zero `LABEL(`/`FUNCTION(` call sites): RED-M3 and
   RED-M4 are the **same set of 51 entries**, name for name; the one count difference (m3 FAIL=24
   CRASH=2, m4 FAIL=25 CRASH=1) is one pre-existing entry reclassified crash→fail, same total red,
   unrelated to this fix. `label`/`function` remain individually red on a **byte-exact full-`.ref`
   diff only** — full diff confirms the sole remaining divergence is the last, already-documented,
   permanently-out-of-scope case-fold line (`GOAL-SNOBOL4-100.md`'s note on this exact row: "both
   `label.ref` and `function.ref` end in lines that need case-insensitive lookup"); **m3 and m4 now
   produce byte-identical output on both programs**, which they did not before this fix.
4. `bash scripts/board_icon_master.sh` (the other lane sharing this exact codegen path): watermark
   HELD AND MOVED UP (m3/m4 599 vs. pinned floor 596); the 2 remaining FAILs
   (`procedure_write_image_1`, `procedure_record_every_replace_2`) are unrelated pre-existing entries,
   identical between modes.
5. `.s` artifacts regenerated per the codegen-touch handoff rule (`util_regen_benchmark_s_artifacts.sh`,
   `util_regen_demo_s_artifacts.sh` — both purely additive, new label-table lines only;
   `util_regen_prolog_bench_s_artifacts.sh` — 0 changed, Prolog's ladder-refused demos untouched).

## LEDGER

- Minimal repros used to bisect (ASM-DIFF-FIRST, per RULES.md): `t1_basic.sno` (plain OUTPUT, works
  both modes — rules out a general m4 multi-OUTPUT defect) → `t2_label_builtin.sno` (adds `LABEL()`,
  breaks m4 only) isolated § 1a; `f1_one_call.sno` (single `FUNCTION()` call) isolated § 1b directly,
  independent of § 1a (confirmed by gdb: `FNCEX_fn` breakpoint returns 1 in m3, 0 in m4, same binary
  build, same call).
- Not chased further, out of scope for this row: whether `_usercall_hook`'s OTHER fallback consumers
  of `_func_buckets` (`FUNC_NPARAMS_fn`/`FUNC_PARAM_fn`/etc., used by `call_user_function`) have the
  same gap for a truly dynamic/indirect by-name call in mode-4 — this row's fix only guarantees
  `FNCEX_fn`'s EXISTENCE answer is now correct in mode-4, not that every richer consumer of
  `_func_buckets` is. No corpus witness in this suite exercises that path; flagging so it isn't
  re-discovered as a mystery if one ever does.
