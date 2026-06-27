# GOAL-RUNTIME-REORG.md — Runtime Subsystem Reorg (dissolve the language silos)

**Split out of GOAL-SNOBOL4-BB.md 2026-06-02 (Lon).** Authoritative partition map + per-slice findings:
`SCRIP/HANDOFF-2026-06-02-SONNET46-SNOBOL4-BB-RS-1-CLUSTER.md` (RS-1 inventory + RS-2 progress).
Completed-slice detail lives in git history + that HANDOFF — this file points at what's NEXT.

---

## ⛔ SESSION START
1. Read this file in full.
2. Clone `.github`; read `PLAN.md`, `RULES.md`.
3. Read the RS-1 HANDOFF (the 17-subsystem `subsystem→{symbols}` / `subsystem→filename` map + 3 key findings).
4. The five byte-identical FACT RULES (NO VALUE STACK, NO C BYRD-BOX, PER-BOX LOCAL STORAGE, SHARED-LOWERER,
   X86-64 REGISTER) live in `GOAL-{SNOBOL4,ICON,PROLOG}-BB.md` and apply unchanged. This reorg is
   MOVE-ONLY / RENAME-ONLY ⇒ behavior-neutral by construction.
5. Run `## Session Setup`. Find the first incomplete RS step. Do it as ONE gated slice.

---

## THE DIRECTIVE (Lon)

`src/runtime/**` is partitioned BY LANGUAGE (`core/`=SNOBOL model, `builtins/gen_runtime.c`=Icon generators,
`resolve_runtime.c`=Prolog resolution, `script_builtins*`=Raku by-name, `rt/rt.c`=grab-bag). REORGANIZE so each
FILE is a SUBSYSTEM (a CS capability), NOT a language. The languages contributed IDEAS; SCRIP uses ALL ideas
TOGETHER. Breaking the file↔language coupling removes the standing invitation to write a parallel
language-specific copy of a capability that already exists.

PUSH THE ENVELOPE on "language builtins" — most generalize (Icon `find`/Raku `index`/SNOBOL pattern-scan = one
search; Prolog `findall`/Icon generator-collect = one solution-gathering; Prolog backtracking / Icon
goal-direction / Raku junctions = ONE backtracking engine, the highest-value unification). Default to
generalizing; keep a thing language-private only when it genuinely cannot be shared.

---

## METHOD
1. **RS-1 — CLUSTER** (analysis). ✅ DONE. Inventory + capability tagging + partition map. No moves.
2. **RS-2…RS-N — PARTITION.** One subsystem per gated slice. `git mv` for whole files; for grab-bag symbol
   splits cut+paste the def into the new file, add the decl to the subsystem header, leave call sites untouched.
   MOVE-ONLY, zero behavioral change. Update the Makefile (`RT_PIC_SRCS` + `scrip:` per-`.o` rule) in LOCKSTEP.
   Gate byte-identical; commit; never start a split you can't finish+gate+commit.
3. **RS-FENCE.** `scripts/test_gate_runtime_subsystems.sh` asserting the partition; wire into Session Setup.

---

## FINDINGS (save real time)
1. **Build lockstep = the Makefile ONLY** (`build_scrip.sh` just calls `make scrip`). Per new `.c`: ONE line in
   `RT_PIC_SRCS` (~71–148) + ONE compile rule in the `scrip:` target (~221+). Link is a `$(OBJ)/*.o` glob — no
   per-`.o` link prereq; delete any stale `/tmp/si_objs/*.o` to avoid double-define. Per removed `.c`: remove from
   both. **Always test BOTH `make scrip` AND `make libscrip_rt`** (different include flags — see #2).
2. **INCLUDE GOTCHA** for files in `src/runtime/` (sibling of core/rt/builtins): the `scrip:` per-`.o` build has
   `-I.../runtime` + `-I.../runtime/core` but NOT `-I.../runtime/rt`. Use RELATIVE includes: `"rt/rt.h"`,
   `"builtins/resolution.h"`, `"../parser/prolog/prolog_atom.h"`. `"core.h"` brings `<gc/gc.h>`;
   `"builtins/resolution.h"` brings `Term`/`Trail`/`resolve_choice`/term API. `libscrip_rt` is more forgiving.
3. **The `IS_*` macros live in `emitter/sil_macros.h`, NOT `core.h`** — any core.c-derived file must include BOTH
   `"core.h"` + `"sil_macros.h"` or the `scrip` per-`.o` build fails at LINK on implicit `IS_*` refs. (Grab-bag
   value-stack helpers often also need a file-local `STACKLESS_ABORT` macro — arithmetic.c precedent.)
4. **PROLOG BUILTINS ARE OUT OF SCOPE.** `rt_findall`/`rt_compound_build_n`/`rt_atom_*`/`rt_copy_term`/`rt_sort_*`/
   `rt_catch`/`rt_throw`/`rt_type_test`/`rt_char_type`/`rt_numbervars`/`rt_is*` are DEFINED in
   `src/interp/IR_interp.c`, NOT `src/runtime/**`. Definition-location authoritative ⇒ not runtime's to move.
   `resolution.c` draws ONLY from the old `resolve_runtime.c`.

---

## CARVE-OUTS
- **Frontend-contract dispatch-name STRINGS stay** (`ICN_*`/`__rk_*`/`set_prolog_flag`/`current_prolog_flag`):
  parser mints them, runtime strcmp-dispatches them. The dispatch TABLE may move; the string values can't change
  without the out-of-scope frontends.
- **Parser/driver-DEFINED symbols stay** (definition-location authoritative).
- **`core/` SNOBOL-lib (LI-CORE)** — `SNO_INIT_fn` + save/restore frame; genuine SNOBOL execution model where a
  generic name would be vague. Cluster members out into subsystems; the SNO-specific residue stays in `core/`.
  Naming questions → Lon, no blanket sed.
- **Genuinely-private language builtins** may keep a small marked file — the EXCEPTION to justify, not the default.

---

## GATES (move/rename-only ⇒ byte-identical, EVERY commit)
```
m2 SNOBOL4 7/7 HARD · m2 Icon 12/12 HARD · m2 Prolog 5/5 HARD
prove_lower2 67 · no_bb_bin_t 0 · audit_concurrency_invariants OK · test_gate_no_lang_names.sh (LI-FENCE) holds
make scrip rc=0 AND make libscrip_rt rc=0 after each file move (Makefile updated in lockstep)
```
ANY gate delta = a real bug ⇒ revert that slice and diagnose. NEVER leave the tree broken between slices.

---

## RS CHECKLIST

- [x] **RS-1 — CLUSTER.** 562-fn inventory + 17-subsystem map (RS-1 HANDOFF). No moves.
- [~] **RS-2 — PARTITION.** Slices 1–24 landed, each gated byte-identical (full detail: git + RS-1 HANDOFF):

  | done | subsystem | source → dest |
  |------|-----------|---------------|
  | s1 | `runtime_eval` | `core/eval_code.c` → `runtime/runtime_eval.c` |
  | s2 | `unification` | WAM core (`rt_unify_*`/`rt_trail_*`/`rt_env_*`/`rt_choice_cut_*`/`rt_node_to_term`) from `rt/rt.c` |
  | s3 | `runtime_init` | `rt_gc_init`/`rt_set_lang`/`rt_finalize`/`rt_bomb`/`rt_unhandled_op`/`rt_main_init` from `rt/rt.c` |
  | s4 | `io_format` | value + Prolog-term output (`rt_write_*`, serializers) from `rt/rt.c` + `core/core.c` |
  | s5–6 | `arithmetic` ✅ | core ops + `coerce_numeric` from `core/core.c`; `rt_arith` dispatch from `rt/rt.c` |
  | s7–11 | `pattern_match` ✅ | `git mv core/pattern.c`; fold `eval_pat.c`; `rt_pat_*`+capture from `rt.c`; `patnd_*` from `stmt_exec.c`; `cset_*` from `scan_builtins.c` (new `pattern_match.h`) |
  | s12–18 | `by_name_dispatch` ✅ | `git mv script_builtins.c`; `scan_try_call_builtin` (dissolved `scan_builtins.c`); `rt_builtin_is_known` from `rt.c`; merged `script_builtins_byname.c` (Raku silo GONE); `rt_call_arr`/`rt_jct_relop`/`call_builtin` + `proc_as_value` + the ~1300-line `try_call_builtin_by_name` giant from `gen_runtime.c`; header consolidation (new `by_name_dispatch.h`, folded + `git rm` `script_builtins.h`+`scan_builtins.h`) |
  | s19 | `resolution` | `git mv builtins/resolve_runtime.{c,h}` → `builtins/resolution.{c,h}` (de-language the resolver; kept in `builtins/` to preserve relatives) |
  | s20 | `keywords` ✅ | `&NAME` keyword-var system (`g_error`/`g_trace`/`g_dump`/`g_random`/`g_jcon` + `kw_assign`/`kw_can_assign`/`kw_read`/`kw_cset_*`/`make_kw_cset`) from `builtins/gen_runtime.c` → `runtime/keywords.{c,h}` |
  | s21 | `string_ops` ✅ | `str_concat_d`/`lconcat_d`/`real_str` from `builtins/gen_runtime.c` → `runtime/string_ops.{c,h}`; `gen_value.h` decls → `#include`. (`string_section_assign` LEFT — frame-coupled) |
  | s22 | `name_binding` | Icon globals/statics/scope (`global_*`/`is_global`/`static_ent_t`+`static_*`/`scope_*`) from `builtins/gen_runtime.c` → `runtime/name_binding.c`; added missing `static_get`/`static_set` protos to `gen_runtime.h` (callers relied on TU-order). Header-less (arithmetic precedent) |
  | s23 | `values` | `descr_identical` (generalized `DESCR_t` structural identity; `===`/`~===` consumers self-extern in `by_name_dispatch.c`) from `builtins/gen_runtime.c` → `runtime/values.c`. Header-less; proto stays in `gen_runtime.h`. SCRIP `ae76122` |
  | s24 | `invocation` | `sm_call_proc`/`proc_table_call` from `builtins/gen_runtime.c` → `runtime/invocation.c`. Frame storage (`frame_stack`/`frame_depth`) STAYS in `gen_runtime.c` (already extern in `gen_runtime.h`) — invocation references it; single-def confirmed. Header-less; protos stay in `gen_runtime.h`. SCRIP `4aa19d7` |
  | s25 | `aggregates` ✅ | **FIRST `core/core.c` carve-out.** array (`array_new`/`array_new2d`/`array_get`/`array_set`/`array_get2`/`array_set2`/`array_ptr`) + table (`_tbl_hash` static/`table_new`/`table_new_args`/`table_get`/`table_set`/`table_set_descr`/`table_has`/`table_ptr`) from `core/core.c` → `runtime/aggregates.c` (155 lines out; core.c 3327→3172). Generic container data-structures — NOT SNOBOL exec-model, so legitimately leaves `core/`. Header-less: all 15 protos already in `core.h`, call sites (the `_ARRAY_`/`_TABLE_`/`_CONVERT_`/`_COPY_` builtins + pattern_match.c/by_name_dispatch.c/interp_ref.c) UNTOUCHED. Includes `core.h`+`sil_macros.h`+`<string.h>`. SCRIP `97f807f` |
  | s26 | `tree` ✅ | n-ary tree / treebank node from `core/core.c` → `runtime/tree.c` (55 lines out; core.c 3172→3117). `expr_new` (TREEBLK_t node ctor) + `tree_new0` + `_tree_ensure_cap` static + `tree_append`/`tree_prepend`/`tree_insert`/`tree_remove` — one cohesive cluster (BODIES read: `tree_new0` wraps `expr_new`, so the `expr_`-named ctor moved WITH the `tree_*` ops). Header-less: all 6 protos already in `core.h`, call sites (snocone parser `snocone_parse.y`/`.tab.c` + lower_sno + scrip.c) UNTOUCHED. Same include set as s25. SCRIP `92b3b08` |
  | s27 | `string_builtins` ✅ | scalar/string builtin IMPLEMENTATIONS from `core/core.c` → `runtime/string_builtins.c` (177 lines out; core.c 3117→2940). `SIZE_fn`/`DUPL_fn`/`REPLACE_fn`/`SUBSTR_fn`/`TRIM_fn`/`lpad_fn`/`rpad_fn`/`REVERS_fn`/`BCHAR_fn` (string ops) + `INTGER_fn`/`real_fn`/`string_fn` (conversions) + `ident`/`differ` (identity) — one contiguous block (sibling to existing `string_ops.c`). Header-less: all 14 protos already in `core.h` (incl. `ident`/`differ` @198–199); call sites (the `_SIZE_`/`_DUPL_`/… builtin wrappers in core.c + prolog test harnesses) UNTOUCHED. Needs `utf8.h` (the `utf8_*` are `static inline` in `core/utf8.h`, resolves via the runtime `-I` path), so a FRESH file was cleaner than merging into `string_ops.c` (which lacks `utf8.h`). Includes `core.h`+`sil_macros.h`+`utf8.h`+`<string.h>`+`<stdlib.h>`. **Caveat:** conversions (`INTGER`/`real`/`string`) + `ident`/`differ` ride along by contiguity; could later regroup to a conversions/comparison home when those clusters are carved. SCRIP `5893518` |

  **State:** `arithmetic`, `pattern_match`, `by_name_dispatch` (.c + header) COMPLETE; `keywords`/`string_ops`
  (.c + header) + `name_binding` (.c) + `values` (.c) + `invocation` (.c) COMPLETE. `gen_runtime.c` **654 → 209 lines**:
  holds ZERO by-name members and zero keyword/string-op/name-binding/values/invocation members. Silos dissolved:
  `scan_builtins.c`, `script_builtins_byname.c`. `gen_runtime.c` now = the Icon generator/frame engine
  (`frame_*`/`sm_yield_to_caller`/`is_suspendable`/`gen_bb_pump_proc_by_name`/`drive_val`) + scan-state globals +
  the `string_section_assign` straggler.

  - [ ] **NEXT — pick one:**
    - **ⓐ resolver dissolution:** relocate `builtins/resolution.{c,h}` → `runtime/` (rewrite the file's
      `../../parser/…` → `../parser/…` + the 12 includers' `builtins/`-prefixed paths + Makefile —
      **Lon to confirm layout first**: sibling subsystems live in `runtime/`, but PLAN's architecture text also
      lists `builtins/` as the resolver-tables home), and/or the **`backtrack`/`unification` static-split** out of
      `resolution.c` (hard multi-slice: WAM choice-point/trail → `backtrack`, term/unify/env → `unification`;
      tightly-coupled shared statics — scope the static surface, one bounded sub-slice at a time).
    - **ⓑ `gen_runtime.c` remainder** — `keywords`/`string_ops`/`name_binding` (s20–22), `values` (s23,
      `descr_identical`), `invocation` (s24, `sm_call_proc`/`proc_table_call`) all DONE. What's LEFT is the
      tightly-coupled **generator/frame engine = the `backtrack` subsystem** (`frame_*`/`sm_yield_to_caller`/
      `is_suspendable`/`gen_bb_pump_proc_by_name`/`drive_val`; frame storage `frame_stack`/`frame_depth` stays here,
      already extern-exposed in `gen_runtime.h`) — this OVERLAPS ⓐ's backtrack split, so do them together. The
      `string_section_assign` straggler → `name_binding`/`control_flow` when one of those lands.
    - **`core/core.c`** (now **2940 lines** after s25–s27; biggest remaining split) → leave SNO-exec-model residue in
      `core/` (LI-CORE). **Cluster map (bodies read this session, def-line order):** `aggregates` ✅ s25 (array+table) +
      `tree` ✅ s26 (`expr_new`+`tree_*`/TREEBLK_t) + `string_builtins` ✅ s27 (SIZE/DUPL/REPLACE/SUBSTR/TRIM/pad/REVERS/
      BCHAR/INTEGER/REAL/STRING/ident/differ) EVICTED. REMAINING capability clusters still in core.c: **`monitor`/`ipc`** (~29–509: `mon_*`/`trace_*`/`comm_*`/
      `load_names_file_bin`/`intern_name_bin`/`_b_MON_*` wire-protocol+tracing — clean but has `kw_stcount`/`kw_stno`
      keyword globals interleaved @106–107 + exported `comm_*` called from driver/interp, so wider surface); **comparison
      + arith builtin wrappers** (~509–768: `_GT_`/`_LT_`/.../`_b_add`/.../`_IDENT_`/`_DIFFER_` — note `_IDENT_`/`_DIFFER_`
      are the canonical pair per the DELETE-dup open item); **datatypes/records** (`_data_ctor_fn`/`_make_ctor`/CTOR_FN/
      FACC_FN/`_make_fget`/`_make_fset` ~1239–1350 + `DEFDAT_fn`/`DATCON_fn`/`FIELD_GET_fn`/`FIELD_SET_fn` ~2230–2317);
      **NV_\*** variable model (~2317–2660: `NV_*`/`INDR_*`/`NAME_fn`/`ASGNIC_fn` + N-stack `NPUSH/NINC/...` — likely LI-CORE SNO
      residue, STAYS); **DEFINE/function-registry** (~2704–3044: `core_fn_registered`/`_parse_define_spec`/`DEFINE_fn`/
      `register_fn_alias`/`APPLY_fn`/`FUNC_*` — note `fn_has_builtin` open-item delete lives here). **INPUT/OUTPUT**
      (~3224–3316: `input_read`/`_INPUT_`/`_OUTPUT_`/`_io_*` — pairs with existing `io_format.c`; note `_input_fp`/`_input_buf`
      statics sit right after `differ` @former-3011, and `_io_chan_*` helpers are earlier ~former-778, so I/O is split — two sub-slices). Method: read bodies,
      one capability per gated slice, def already in `core.h` ⇒ usually header-less + call-sites-untouched (s25 precedent).
      **NOTE:** line numbers above are ORIGINAL-file (pre-s25) approximate — re-grep current positions before slicing
      (core.c shrank 387 lines across s25–s27, so clusters below ~line 2019 have shifted up).

- [ ] **RS-FENCE.** `scripts/test_gate_runtime_subsystems.sh` asserts the partition; wire into Session Setup.

### Open items for Lon (NOT moves — decide before/independently of the slices)
- **`fn_has_builtin` (core.c)** — `static` (decl `core.c:1463`, def `2704`), ZERO callers tree-wide; vestigial
  near-dup of exported `core_fn_registered` (differs only by `e->fn != NULL`). Relocating drags core.c's
  `_func_buckets`/`_func_init`/`_func_hash` registry statics ⇒ not a clean move. Likely **delete** (out of
  move-only scope).
- **`scan_try_call_builtin` dup decl** at `interp_private.h:124` — identical pre-existing decl (NOT an orphan).
  Harmless (`WARN := -w`, no `-Werror`). One-line follow-up if a single decl-site is wanted.
- **`kw_anchor`** — RS-1 map lists it under BOTH `pattern_match` and `keywords.c`; pick a home.
- **`_rt_IDENT`/`_rt_DIFFER` — NOT a "home" decision; a DELETE-the-DUPLICATE decision (Opus 2026-06-03).** Reading the
  bodies revealed `IDENT`/`DIFFER` are **DOUBLE-REGISTERED**: `core/core.c:1663-64` `register_fn("IDENT",_IDENT_,0,2)` /
  `register_fn("DIFFER",_DIFFER_,0,2)` AND `rt/rt.c:186-87` `register_fn("IDENT",_rt_IDENT,1,2)` /
  `register_fn("DIFFER",_rt_DIFFER,1,2)` — same names, two impls, conflicting min-args (0 vs 1), and NOT equal:
  core.c's `_IDENT_`/`_DIFFER_` (defs `core.c:641-50`) are **type-correct** (delegate to `ident()`/`differ()`, min 0 =>
  proper `IDENT(X)`-vs-null); rt.c's `_rt_IDENT`/`_rt_DIFFER` (defs `rt.c:68-82`) are an **inferior STRING-ONLY copy**
  (`VARVAL_fn`+`strcmp`, so integer `5` would equal string `"5"` — WRONG under SPITBOL), min 1. This is exactly the
  "parallel copy of a capability that already exists" the reorg targets. **Resolution: DELETE rt.c's `_rt_IDENT`/
  `_rt_DIFFER` + their two `register_fn` lines; keep core.c's canonical pair** (already in the SNOBOL model — its proper
  home). Dissolves the open item WITHOUT any values.c/arithmetic.c/comparison.c move, and clears the
  `_rt_IDENT`/`_rt_DIFFER` half of the `rt_init` blocker (below). It is a **DELETE = behavioral** (if the inferior copy
  currently wins the registration race) — a Lon call, NOT a move-only slice. (A values.c move WAS prototyped this session
  + gated byte-identical, then REVERTED: relocating one half of a dup just entrenches it.)
- **`IDENT`/`DIFFER` mode-2 dispatch anomaly (pre-existing — NOT caused by any reorg work).** A 4-case `--run` probe
  (`IDENT("a","a")`, `IDENT("a","b")`, `DIFFER("a","b")`, `DIFFER("x","x")`) shows the two should-SUCCEED cases FAILING.
  NEITHER body explains it (both return success for `("a","a")`), so the fault is upstream in mode-2 builtin dispatch;
  reproduced on the clean tree after the revert. Worth a separate diagnosis; out of move-only scope.

### Deferred micro-slices (pending destination homes)
- **`rt_init`** (slice-3) — convergence point dragging OTHER subsystems' statics (`_rt_IDENT`/`_rt_DIFFER` =
  comparison [home decision in Open-items above, OPEN]; `_rt_usercall` → `chunk_reg_lookup`/`call_native_chunk` =
  native-chunk invocation). `invocation` now HAS a home (s24); `rt_init` still blocked on the comparison-builtins — now a DELETE-dup call (see updated Open-item), not a home.
- **`rt_unop_*`** (slice-6) — capability-split: `unop_size` → `string_ops`; `unop_not`/`null_test`/`nonnull` → a
  logical/control home; `unop_neg`/`unop_pos` → `arithmetic`. Lands with those homes (don't strand a half-block).

**Method reminder:** definition-location authoritative; move/rename-only, no behavior change; Makefile in lockstep;
gate byte-identical after each slice; never start a split you can't finish+gate+commit. READ THE BODIES before
clustering — never guess a function's subsystem from its filename (that filename is the language lie we're removing).

---

## Session Setup
```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```
Gates:
```bash
bash scripts/test_smoke_snobol4.sh   | grep mode-2     # 7/7 HARD
bash scripts/test_smoke_icon.sh      | grep mode-2     # 12/12 HARD
bash scripts/test_smoke_prolog.sh    | grep mode-2     # 5/5 HARD
bash scripts/prove_lower2.sh         | grep -c PASS    # 67
bash scripts/test_gate_no_bb_bin_t.sh                  # OK (0)
bash scripts/test_gate_no_lang_names.sh                # LI-FENCE OK
bash scripts/audit_concurrency_invariants.sh           # OK
```

---

**Repo:** SCRIP + .github
**Watermark.** SCRIP `5893518` (RS-2 **s27 string_builtins**, gated byte-identical, this session) · prior `92b3b08`
(s26 tree) · `97f807f` (s25 aggregates) · `8970924` (LI-FENCE) · RS watermark `4aa19d7` (RS-2 s1–s24). RS-1 done;
RS-2 slices 1–27 landed: `arithmetic` / `pattern_match` / `by_name_dispatch` / `keywords` / `string_ops` (.c + header)
+ `name_binding` / `values` / `invocation` (.c) + **`aggregates` + `tree` + `string_builtins` (.c — three `core.c`
carve-outs this session)** COMPLETE; resolver renamed to `resolution`; `gen_runtime.c` 654 → 209 lines; `core/core.c`
**3327 → 2940 lines** (array+table+tree+string/scalar-builtin-impls evicted — 387 lines / 4 capabilities out).

**This session (Opus, 2026-06-03) — resumed post-compaction; performed hand off.** Continued GOAL-RUNTIME-REORG
with three clean `core/core.c` carve-outs, all MOVE-ONLY and gated byte-identical (7/7 · 12/12 · 5/5 · 67 · no-bb-bin-t
· LI-FENCE · concurrency), each PUSHED: **s25 `aggregates`** (array+table → `runtime/aggregates.c`, SCRIP `97f807f`),
**s26 `tree`** (`expr_new`+`tree_*` n-ary/treebank node → `runtime/tree.c`, `92b3b08`), **s27 `string_builtins`**
(SIZE/DUPL/REPLACE/SUBSTR/TRIM/pad/REVERS/BCHAR + INTEGER/REAL/STRING + ident/differ → `runtime/string_builtins.c`,
`5893518`). `core/core.c` **3327 → 2940 lines** (387 out / 4 capability clusters). Each was header-less (all protos
already in `core.h`) ⇒ **zero call sites changed** — behavior-neutral by construction. Body-read catches the method
exists to surface: s26 — `tree_new0` wraps `expr_new`, so the `expr_`-named ctor had to move WITH the `tree_*` ops
(real boundary wider than the `tree_*` names); s27 — block uses `utf8_strlen`/`utf8_char_offset`/`utf8_char_bytes`
(`static inline` in `core/utf8.h`), so a FRESH file `#include`-ing `utf8.h` was cleaner than merging into `string_ops.c`
(which lacks it). **Paused after s27:** the trivially-clean veins are picked — every remaining `core.c` cluster carries
an entanglement (full map in NEXT): monitor/ipc (interleaved `kw_*` globals + exported `comm_*` + `_b_MON_*`
registration), comparison/arith (tied to the IDENT/DIFFER dup decision), datatypes (X-macros, two non-contiguous
ranges), DEFINE/registry (`fn_has_builtin` open-item), NV_* (likely LI-CORE, STAYS), INPUT/OUTPUT (split tail+early).
These want a fresh session's budget or a Lon decision on the open items. Both repos clean & pushed: SCRIP `5893518`,
`.github` watermark-of-record.

**Prior session (Opus, 2026-06-03).** Arrived with HEAD `5dff1a8` — TWO commits past `4aa19d7` from other goals
(GN-3 `7fc5ae9`, then Prolog-BB WAM-CP-7c `5dff1a8`). **Baseline was RED on LI-FENCE:** WAM-CP-7c put
`rt_pl_unify_var_var` into `unification.c` (an RS-2-de-languaged file); the `pl_` tag tripped
`test_gate_no_lang_names.sh` (their GATE-3 was green — this goal's fence is a *different* invariant; the fence exists to
catch exactly this cross-goal collision). **Fix — SCRIP `8970924`, PUSHED:** de-named to `rt_unify_var_var` (def +
extern decl + emit-call label/pointer in `bb_unify.cpp`); siblings are `rt_unify_terms`/`rt_unify_const`; NOT
allow-listed (allow-listed `pl_`/`prolog` names are all PARSER-side carve-outs; this is runtime-defined). Re-gated
byte-identical — all gates green, mode-2 == mode-4 var-var (`hello`). **HEADS-UP to Prolog-BB: `rt_pl_unify_var_var` is
now `rt_unify_var_var`.**

Then attempted comparison-home slice (a): prototyped moving `_rt_IDENT`/`_rt_DIFFER` → `values.c`, gated byte-identical
— but reading the bodies exposed that they are an inferior string-only DUPLICATE of core.c's canonical
`_IDENT_`/`_DIFFER_` (both register "IDENT"/"DIFFER"; see the rewritten Open-item). **Reverted the move** (relocating
half a dup entrenches it); the real fix is a DELETE-the-dup decision for Lon. Confirmed a pre-existing mode-2
IDENT/DIFFER dispatch anomaly along the way (Open-item). Tree restored to fence-fix-only; nothing else re-touched.

**Open Lon decisions** (NB: `core.c` clean carves are FLOWING — s25–s27 landed, 4 more clusters mapped in NEXT with entanglements noted; items below are the NON-move decisions): (a→) **DELETE rt.c `_rt_IDENT`/`_rt_DIFFER` dup**
(keep core.c canonical; unblocks `rt_init`; behavioral → Lon); (b) resolution `builtins/`→`runtime/` layout; (c) the
hard `backtrack` cluster (gen_runtime.c remainder, overlaps resolution split); (d) `core/core.c` (now **2940 lines**, actively carving — s25–s27 done, remaining clusters mapped in NEXT; LI-CORE residue STAYS).
Other open calls: `fn_has_builtin` (likely delete), `scan_try_call_builtin` dup decl, `kw_anchor`
home; IDENT/DIFFER mode-2 anomaly (Open-item).
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
