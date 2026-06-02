# HANDOFF — SNOBOL4 BB: LI runtime de-name, slice 1 (`.so` runtime symbols → CS concepts)

**Author:** Opus 4.8 (third developer). **Date:** 2026-06-02.
**Repo tips:** SCRIP `origin/main` = `10fbe32` (base `3a39174`); `.github` = the commit carrying this file.

---

## Directive (Lon, this session)

Stay on the PIVOT. Do NOT chase the old `bb_subject`/`bb_match` NEXT pointer. In the **language runtime
(`libscrip_rt.so`)**, identify every symbol whose name is derived from one of the six languages (`sno`/`icn`/
`icon`/`pro`/`pl`/`prolog`/`raku`/`rk`/`rebus`/`reb`/`snocone`/`snoc`) and **eradicate the language tag** — rename
each to the **runtime / CS concept** it actually is, name chosen from its usage. The data structures have nothing
to do with the language; the goal is full code reuse/sharing. This is **NOT a refactor** — it is a rename.

Sequence Lon stated: the `.so` (identify) → the source of the `.so` → the runtime code → the emitters. **LOWER
and PARSER (frontend) are NOT in scope.** A new rung was added to `GOAL-SNOBOL4-BB.md` as the CURRENT (top) step
and is kept **ACTIVE** (not closed) — it continues through the deeper runtime pass and then the emitter sweep.

## Method that worked (and the trap to avoid)

**Definition-location is authoritative — a token's USE in runtime does not make it runtime-owned.** First pass
mis-attributed several symbols to runtime because they are *called* from runtime but *defined* in `src/frontend/`.
Always locate the actual definition (`grep` for the def line, not call sites) and bucket by the directory of the
**defining** file. Only symbols **defined under `src/runtime/**`** were renamed; their call sites everywhere
(lower/emitter/driver/frontend) were updated as reference fixes.

Collision-checked every target name against the full `nm` symbol set before applying (all free). Applied with a
word-boundary `sed` script (`\b<old>\b`) across the affected `.c/.cpp/.h` (generated `*.tab.c`/`*.lex.c` excluded);
0 residual old tokens after.

## What landed (SCRIP `10fbe32`, 14 files, rename-only)

27 runtime-defined exported symbols + the `icnlist` runtime datatype:

| Old | New | Concept |
|---|---|---|
| `rt_pl_write_int/var/atom/cstr/float/term_ptr` | `rt_write_*` | term serialization |
| `rt_pl_writeq_term_ptr` / `rt_pl_write_canonical_term_ptr` | `rt_writeq_term_ptr` / `rt_write_canonical_term_ptr` | term serialization (output modes) |
| `rt_pl_format_float` | `rt_format_float` | float formatting |
| `rt_pl_env_alloc` / `rt_pl_env_current` | `rt_env_alloc` / `rt_env_current` | environment frames |
| `rt_pl_cp_save_caller_env` | `rt_cp_save_caller_env` | choice-point save |
| `rt_pl_choice_cut_enter/exit/unwind` | `rt_choice_cut_*` | choice/cut control |
| `rt_pl_cut_set` / `rt_pl_get_cut_flag` | `rt_cut_set` / `rt_get_cut_flag` | cut barrier |
| `rt_pl_main_init` | `rt_main_init` | runtime init |
| `rt_rk_call_arr` / `rt_rk_jct_relop` | `rt_call_arr` / `rt_jct_relop` | array call / junction relop |
| `interp_exec_pl_builtin` | `interp_exec_builtin` | builtin dispatch |
| `is_pl_user_call` | `is_user_call` | call classification |
| `g_pl_last_ok` | `g_last_ok` | last-result flag |
| `g_icn_call_args` / `g_icn_proc_arena` / `g_icn_proc_depth` | `g_call_args` / `g_proc_arena` / `g_proc_depth` | call args / procedure-frame state |
| `descr_to_str_icn` | `descr_to_str` | descriptor→string coercion |
| datatype `"icnlist"` + guards `icnlist_*` | `"list"` + `list_*` | frame-backed list value (registered via DEFDAT, built via DATCON, dispatched via strcmp — all in runtime, zero `.ref` dependency) |

Files: `src/runtime/rt/rt.c`, `src/runtime/interp/{gen_runtime,resolve_runtime}.c`,
`src/runtime/core/{coerce,pattern}.c` (+ runtime headers); call-site updates in 2 emitter, 2 lower, 1 driver,
1 frontend file.

## Held (with reason)

- **frontend-DEFINED (out of scope):** `pl_arg`/`pl_univ`/`pl_functor`/`pl_write`/`pl_writeq`/
  `pl_write_canonical`/`pl_assert_term`/`pl_term_to_string` (`prolog_builtin.c`, `prolog_lower.c`);
  `prolog_atom_{init,name,intern}` (`prolog_atom.c`); `raku_nfa_{build,exec,free,bb_match,state_count}`
  (`raku_re.c`, `raku_nfa_bb.c`).
- **driver-DEFINED:** `g_raku_match` (`src/driver/interp_globals.c`) — Lon named runtime then emitters, not driver.
- **genuine / merge:** `SNO_INIT_fn` (SNOBOL runtime-library initializer), `sno_parse_string_ast` (calls the
  SNOBOL parser for `CODE`/`EVAL`), `rt_pl_arith` → `rt_arith` (a MERGE with the existing `rt_arith`; do with
  code, not a blind rename).

## Gates (byte-identical, exactly at baseline `3a39174`)

```
make scrip            rc=0
make libscrip_rt      rc=0
SNOBOL4 smoke         m2 7/7 HARD · m3 2/6 · m4 0/6
Icon smoke            m2 12/12 HARD · m3 3/12 · m4 3/12
Prolog smoke          m2 5/5 HARD · m3 2/5 · m4 0/5
prove_lower2          67
no_bb_bin_t           0
concurrency           OK (FACT RULES byte-identical x3)
```

## NEXT (the rung stays ACTIVE)

1. **Deeper runtime pass** — language-tagged STATICS and STRING literals still in `src/runtime/**` beyond the
   exported surface (datatype names, DEFDAT/DATCON registrations, debug/trace text). For each: confirm it is
   runtime-only (no `.ref` / output dependency) before renaming.
2. `rt_pl_arith` → `rt_arith` MERGE (inspect both, fold).
3. Then the identical sweep over **`src/emitter/**`** (the next layer Lon named).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
