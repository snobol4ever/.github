# GOAL-RUNTIME-REORG.md — Runtime Subsystem Reorg (dissolve the language silos)

**Split out of GOAL-SNOBOL4-BB.md 2026-06-02 (Lon directive) so it runs as its own session.**
The authoritative partition map + per-slice findings live in
`SCRIP/HANDOFF-2026-06-02-SONNET46-SNOBOL4-BB-RS-1-CLUSTER.md` (RS-1 inventory + RS-2 progress).

---

## ⛔ SESSION START
1. Read this file in full.
2. Clone `.github`; read `PLAN.md`, `RULES.md`.
3. **Read the RS-1 HANDOFF** (`SCRIP/HANDOFF-2026-06-02-SONNET46-SNOBOL4-BB-RS-1-CLUSTER.md`) — the full
   `subsystem→{symbols}` / `subsystem→filename` map (17 subsystems) + the three key findings.
4. The five byte-identical FACT RULES (NO VALUE STACK, NO C BYRD-BOX, PER-BOX LOCAL STORAGE, SHARED-LOWERER,
   X86-64 REGISTER) still live in `GOAL-SNOBOL4-BB.md` / `GOAL-ICON-BB.md` / `GOAL-PROLOG-BB.md` and apply
   unchanged. This reorg is MOVE-ONLY / RENAME-ONLY ⇒ behavior-neutral by construction.
5. Run `## Session Setup`. Find the first incomplete RS step. Do it as ONE gated slice.

---

## THE DIRECTIVE (Lon, verbatim intent)

**SCRIP unifies 6+ languages (SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus) into ONE consolidated multi-language
system. The runtime must reflect that.** Today `src/runtime/**` is partitioned *by language*: `core/` is the SNOBOL
execution model, `builtins/gen_runtime.c` is Icon generators, `builtins/resolve_runtime.c` is Prolog resolution,
`builtins/script_builtins*.c` is the Raku-flavored by-name layer, `rt/rt.c` is a grab-bag. **REORGANIZE the entire
`src/runtime/**` so each FILE is a SUBSYSTEM (a CS capability), NOT a language.** The languages contributed IDEAS;
SCRIP now uses ALL ideas in ALL languages TOGETHER. Breaking the file↔language coupling removes the standing
invitation to write a parallel language-specific copy of a capability that already exists.

**PUSH THE ENVELOPE even on "language builtins":** far more generalize than first appears (Icon `find`/Raku
`index`/SNOBOL pattern-scan = one search; Prolog `findall`/Icon generator-collect = one solution-gathering; Prolog
backtracking / Icon goal-direction / Raku junctions = ONE backtracking engine — the highest-value unification).
Default to generalizing; keep a thing language-private only when it genuinely cannot be shared.

---

## METHOD (the whole rung)
1. **RS-1 — CLUSTER (analysis, DONE).** Full inventory + capability tagging + written partition map. NO moves.
2. **RS-2…RS-N — PARTITION.** One subsystem per gated slice. `git mv` for whole-file relocations; for symbols
   split out of a grab-bag (`rt.c`/`core.c`), cut+paste the definition into the new file, add the decl to the
   subsystem header, leave call sites untouched. **MOVE-ONLY — zero behavioral change.** Update the build system
   (Makefile `RT_PIC_SRCS` + the `scrip:` per-`.o` rule) IN LOCKSTEP with every file add/move/delete. One subsystem
   at a time; gate byte-identical; commit; **never start a split you can't finish+gate+commit.**
3. **RS-FENCE.** `scripts/test_gate_runtime_subsystems.sh` asserting the partition; wire into Session Setup.

---

## 🔑 FINDINGS (from RS-2 slices 1-2 — save real time)
1. **Build lockstep = the Makefile ONLY.** `build_scrip.sh` just calls `make scrip`. Per new `.c`: ONE line in
   `RT_PIC_SRCS` (Makefile ~71–148) + ONE compile rule in the `scrip:` target (~221+). Linking is a `$(OBJ)/*.o`
   glob — no per-`.o` link prereq. Per emptied/removed `.c`: remove from both. **Always test BOTH `make scrip` AND
   `make libscrip_rt`** (different include flags — see #2).
2. **INCLUDE GOTCHA for files in `src/runtime/`** (sibling of core/rt/builtins): the `scrip:` per-`.o` build
   (`CRT`/`CBASE`) has `-I$(SRC)/runtime` + `-I$(SRC)/runtime/core` but **NOT `-I$(SRC)/runtime/rt`**. So use
   RELATIVE includes: `"rt/rt.h"`, `"builtins/resolve_runtime.h"`, `"../parser/prolog/prolog_atom.h"`. `"core.h"`
   brings `<gc/gc.h>`; `"builtins/resolve_runtime.h"` brings `Term`/`Trail`/`resolve_choice`/`g_resolve_*`/IR enum/
   term API. The `libscrip_rt` build DOES have `-I.../rt` (more forgiving) — test both.
3. **PROLOG BUILTINS ARE OUT OF SCOPE.** `rt_findall`, `rt_compound_build_n`, `rt_atom_*`, `rt_copy_term`,
   `rt_sort_msort`, `rt_catch/throw`, `rt_type_test`, `rt_char_type`, `rt_numbervars`, `rt_is*` are DEFINED in
   `src/interp/IR_interp.c` (the IR-graph interpreter), NOT in `src/runtime/**`. Definition-location authoritative ⇒
   NOT runtime's to move. The map's `resolution.c` draws ONLY from `builtins/resolve_runtime.c`.

---

## CARVE-OUTS
- **Frontend-contract dispatch-name STRINGS stay** (`ICN_NULL`/`ICN_CASE_EQ`/`ICN_SCAN_*`/`__rk_jct_*`/`__rk_arr`/
  `set_prolog_flag`/`current_prolog_flag`): the parser mints them, the runtime strcmp-dispatches them; the dispatch
  TABLE may move into a subsystem, the string values cannot change without the (out-of-scope) frontends.
- **Parser/driver-DEFINED symbols stay where they are** (definition-location authoritative).
- **`src/runtime/core/` SNOBOL-lib (LI-CORE)** — `SNO_INIT_fn` + save/restore frame; genuine SNOBOL execution model
  where a generic CS name would be vague. Members get clustered out into subsystems; the SNO-specific residue stays
  in `core/`. Surface naming questions to Lon, no blanket sed.
- **Genuinely-private language builtins** that survive the generalization attempt may keep a small language-private
  file (or marked section) — the EXCEPTION to justify, not the default.

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
- [x] **RS-1 — CLUSTER.** ✅ DONE (Sonnet 4.6, 2026-06-02). 562-function inventory + 17-subsystem partition map in
  the RS-1 HANDOFF. NO moves.
- [~] **RS-2…RS-N — PARTITION.** IN PROGRESS.
  - [x] **slice 1 — `runtime_eval`** (SCRIP `970dbf5`): `git mv core/eval_code.c → runtime/runtime_eval.c`. Validated the loop.
  - [x] **slice 2 — `unification`** (SCRIP `17e759e`): WAM core (`rt_unify_*`/`rt_trail_*`/`rt_env_*`/`rt_choice_cut_*`/
    `rt_node_to_term`/`rt_get_cut_flag`/`rt_main_init`) extracted from grab-bag `rt/rt.c` → `runtime/unification.c`.
    (residual `rt_main_init` ✅ re-homed in slice 3; trail/choice/cut may later split to `backtrack.c`.)
  - [x] **slice 3 — `runtime_init`** (SCRIP `458f8a3`): `rt_gc_init`/`rt_set_lang`/`rt_finalize` (+ its private
    read-only statics `g_halt_rc`/`g_halt_set`, never written ⇒ constant-0)/`rt_bomb`/`rt_unhandled_op` pulled from
    grab-bag `rt/rt.c` + `rt_main_init` re-homed from `unification.c` → new `runtime/runtime_init.c`. Move-only; no
    new `.h` (rt.h decls + the `xa_file_header.cpp` PLT strings unchanged). **`rt_init` DEFERRED** — its body is a
    convergence point dragging file-local statics owned by OTHER subsystems (`_rt_IDENT`/`_rt_DIFFER` = comparison
    builtins; `_rt_usercall`→`chunk_reg_lookup`/`call_native_chunk` = native-chunk invocation); moving it now would
    break move-only or recreate the grab-bag. It moves cleanly once invocation + comparison builtins have homes.
  - [x] **slice 4 — `io_format`** (SCRIP `5e92b35`): unified output formatting — `rt_write_str_nl`/`_int_nl`/
    `_any_nl`/`_strz_nl` + `rt_write_atom`/`_int`/`_float`/`_cstr` (+ static `rt_format_float`) + the Prolog term
    serializers `rt_write_var`/`_term_ptr`/`_writeq_term_ptr`/`_canonical_term_ptr` pulled from grab-bag `rt/rt.c`
    (around the interleaved `rt_cut_set`, which is cut/backtrack and stays) + `output_val`/`output_str` from
    `core/core.c` → new `runtime/io_format.c`. Move-only; rt.h/core.h decls + `bb_call.cpp` PLT refs unchanged; no
    new `.h`. SNOBOL/Icon value output + Prolog term output now ONE subsystem.
  - [x] **slice 5 — `arithmetic` (part 1/2)** (SCRIP `6899f7f`): contiguous core `add`/`sub`/`mul`/`DIVIDE_fn`/
    `POWER_fn`/`neg`/`pos`/`eq`/`ne`/`lt`/`le`/`gt`/`ge` block + private static `coerce_numeric` (used only by
    add/sub/mul) from `core/core.c` → new `runtime/arithmetic.c`. Move-only; core.h decls unchanged; `ident`/`differ`
    + `to_int`/`to_real` stay (latter RS-1 values.c). **BUILD LESSON:** the `IS_*` macros live in
    `emitter/sil_macros.h` not `core.h` — core.c-derived files must include BOTH `"core.h"` + `"sil_macros.h"` or the
    `scrip` per-`.o` build (fewer `-I` than libscrip_rt) fails at LINK on implicit `IS_*` function refs.
  - [x] **slice 6 — `arithmetic` (part 2/2)** (SCRIP `1adcf09`): the scattered grab-bag helpers `rt_arith` (the
    real operator-dispatch: bitwise `/\`/`\/`/`xor`/`<<`/`>>`/`\`, `mod`/`rem`/`gcd`/`div`/`//`, `**`/`^`, `min`/
    `max`/`abs`/`sign`, +the IR_LOGICVAR deref path) + 7 dead value-stack stubs (`rt_coerce_num`/`rt_exp`/`rt_neg`/
    `rt_incr`/`rt_decr`/`rt_acomp`/`rt_lcomp`) cut from `rt/rt.c` → existing `runtime/arithmetic.c`. Move-only;
    rt.h decls unchanged; no Makefile change (arithmetic.c already in RT_PIC_SRCS + scrip per-`.o` from slice 5).
    arithmetic.c gained `rt/rt.h`+`builtins/resolve_runtime.h`+`../parser/prolog/prolog_atom.h`+`<stdio.h>` (Term
    API for rt_arith, the proven `unification.c` include set) + the file-local `STACKLESS_ABORT` macro.
    **BODY-READ LESSON:** the names `rt_neg`/`rt_incr`/`rt_acomp`/… *look* like live arithmetic but are abort-stubs
    from the removed value stack — only `rt_arith` carries logic; the filename was the language/era lie. RS-1 map
    has `arithmetic.c = numeric ops + comparison`, so both `rt_acomp` (arith-cmp) and `rt_lcomp` (lexical-cmp) home
    here. **`rt_unop_*` LEFT in rt.c on purpose** — genuinely capability-split (`unop_size`=string-length →
    `string_ops`; `unop_not`/`null_test`/`nonnull`=logical → a logical/control home; `unop_neg`/`unop_pos`=arith),
    and those destinations aren't homed yet ⇒ splitting now would strand a half-block. **`arithmetic` subsystem now
    COMPLETE** (part 1 `6899f7f` + part 2 `1adcf09`). Gates byte-identical.
  - [x] **slice 7 — `pattern_match` (part 1)** (SCRIP `33fc8b3`): whole-file `git mv core/pattern.c →
    src/runtime/pattern_match.c` — de-silo the SNOBOL pattern-BUILDER layer out of `core/` into the language-
    independent `runtime/` subsystem. Fixed one relative include (`../../parser/` → `../parser/`, the slice-1
    mechanic). Makefile RT_PIC_SRCS + scrip per-`.o` updated in lockstep (relocated both into the moved-subsystems
    block; `.o` renamed `snobol4_pattern.o` → `pattern_match.o`). Move-only; decls live in `core/patnd.h` + `core.h`
    (unchanged). **way-station note:** the whole-file move carried a few non-pattern residents the RS-1 map assigns
    elsewhere — `subscript_*`/`sort_fn`/`rsort_fn` → `collections.c`; `EVAL_fn`/`opsyn`/`compile_to_expression` →
    existing `runtime_eval.c` — to be pulled out in those subsystems' slices. Gates byte-identical.
  - [x] **slice 8 — `pattern_match` (part 2)** (SCRIP `0f817f9`): fold `core/eval_pat.c` (the mode-2 pattern
    EVALUATOR — `interp_eval_pat` + static inline `NAME_DEREF`) INTO `pattern_match.c`, matching the RS-1 single-
    file target (builder + evaluator now one subsystem file). Bodies cut byte-identical; dropped the dup includes +
    dup `extern eval_node` (already present). Added two includes pattern_match.c now needs: `sil_macros.h` (the
    `IS_NAME`/`IS_FAIL_fn` macros, emitter dir via `-I`) + `builtins/gen_runtime.h` (relative `../builtins/` →
    `builtins/` for the new location). `git rm core/eval_pat.c` + removed its 2 Makefile entries in lockstep. Move-
    only; `interp_eval_pat` declared in `driver/interp.h` (unchanged). Gates byte-identical. **`pattern_match`
    parts 1-2 (the two whole-file moves) COMPLETE; `core/` pattern `.c` files both relocated (only `patnd.h` stays).**
  - [x] **slice 9 — `pattern_match` (part 3)** (SCRIP `ef53557`): pull the big `rt_pat_*` family out of grab-bag
    `rt.c` into `pattern_match.c` — the contiguous block `rt.c:519-789` (`rt_exec_stmt_pat`, `rt_match_blob`,
    `rt_pat_lit`…`rt_pat_rem`, `rt_pat_fence`…`rt_pat_usercall_args`, `rt_match_variant`; all dead value-stack
    abort-stubs whose symbols are preserved by relocating into the same binary) + the CAPTURE machinery
    `rt_dcap_record`(static)+`g_rt_dcap[]`/`_n` statics+exported `g_rt_dcap_active`, `rt_dcap_flush`/`_clear`,
    `rt_cap_assign`/`_cursor`, `rt_at_cursor`, `rt_defer_match`. The static `rt_dcap_record`+its statics travel with
    the block (sole callers `rt_cap_assign`/`_cursor` moved too); `g_rt_dcap_active` is referenced nowhere else in
    the tree. Added the file-local `STACKLESS_ABORT` macro (arithmetic.c precedent). No Makefile change (both files
    already wired). Capture fns reach `NV_*_fn` via `core.h`, `NAME_DEREF_PTR`/`IS_NAMEVAL`/`IS_NAMEPTR` via
    `sil_macros.h`, subject externs (`Σ`/`Σlen`/`Ω`/`Δ`)+`exec_stmt` as block-local externs; `rt.h` decls unchanged.
    Move-only; gates byte-identical. **`rt_pat_*` family DONE — grab-bag `rt.c` no longer holds any pattern ops.**
  - [x] **slice 10 — `pattern_match` (part 4)** (SCRIP `2997f12`): move the 9 `patnd_*` classification helpers
    (`contains_arbno`/`contains_defer`/`is_simple_atom`/`is_capture_wrapped_safe`/`tree_eligible`/
    `is_combinator_root`/`needs_xlate`/`is_pure_altcat_leaf`/`is_pure_altcat`) from `core/stmt_exec.c` →
    `pattern_match.c`. The 5 called by `exec_stmt` promoted to external linkage (decls added to `core/patnd.h`,
    already pulled in by both files via `core.h`); the 4 internal-only stay static. `exec_stmt` + call sites
    untouched (it goes to `control_flow.c` later). No files added/removed ⇒ no Makefile change. Move-only.
  - [x] **slice 11 — `pattern_match` (part 5)** (SCRIP `1d09cda`): move `cset_resolve`/`cset_has` from
    `builtins/scan_builtins.c` → `pattern_match.c` (de-static; `cset_has` de-inlined). **Created
    `src/runtime/pattern_match.h`** — the subsystem's own header (SUBSYSTEM 7) — declaring the two, chosen over
    stuffing them into `patnd.h` (they're cset primitives, not PATND-node ops; homing-by-convenience is the
    anti-pattern this reorg removes). Self-contained via `../contracts/descr.h`; included by both `.c`s; resolves
    both builds via `-I$(RT)`. Header-only ⇒ no Makefile change. **`pattern_match` subsystem COMPLETE** (parts
    1–5; ONLY `kw_anchor` open — map lists it under both pattern_match + `keywords.c`, a Lon call). `patnd.h`
    keeps the part-4 `patnd_*` decls (those genuinely operate on `PATND_t`).
  - [x] **slice 12 — `by_name_dispatch` (part 1)** (SCRIP `d7d7055`): `git mv builtins/script_builtins.c →
    src/runtime/by_name_dispatch.c` — opens SUBSYSTEM 13 with a whole-file move of its simplest source
    (`script_try_call_builtin`: single fn, only a function-local static, ZERO callers tree-wide / Raku ON HOLD).
    Slice-8 relative-include fix (5 paths: `builtins/` prefix for sibling headers; `../driver`/`../parser`; `core.h`
    unchanged). `script_builtins.h` stays in `builtins/` (shared with `script_builtins_byname.c`); no
    `by_name_dispatch.h` yet. Makefile lockstep (RT_PIC_SRCS + per-`.o` → `by_name_dispatch.o`); removed stale
    `/tmp/si_objs/script_builtins.o` (would double-define at the `*.o` glob link).
  - [x] **slice 13 — `by_name_dispatch` (part 2)** (SCRIP `8c75c83`): move `scan_try_call_builtin` →
    `by_name_dispatch.c`; after the part-5 cset move this **emptied `builtins/scan_builtins.c` ⇒ `git rm`** (Icon
    string-scan silo file GONE). Added `pattern_match.h` to by_name_dispatch.c (calls relocated `cset_*`).
    `scan_builtins.h` KEPT (decl-only; still included by `gen_runtime.c`, mirrored in `interp_private.h:124`).
    Makefile: removed scan_builtins.c from RT_PIC_SRCS + per-`.o`; removed stale `scan_builtins.o`. Move-only.
  - [x] **slice 14 — `by_name_dispatch` (part 3)** (SCRIP `fbd1412`): move `rt_builtin_is_known` + its static
    helper `builtin_is_generator` from grab-bag `rt/rt.c` → `by_name_dispatch.c` (shrinks the grab-bag; the
    function-local `known[]` table travels). Added `#include "rt/rt.h"` for `rt_proc_is_registered` (slice-2/6
    relative-include mechanic); `rt_builtin_is_known` decl stays in `rt.h:139` so emitter callers
    (`bb_call.cpp`/`emit_bb.c`) are untouched. **Behavior-neutral fix the move SURFACED:** dropped a loose
    block-local `extern void *dat_find_type` that conflicted with the canonical `DatType *dat_find_type`
    (`interp_private.h:115`) now in scope via the file's inherited includes — identical compiled call (same symbol,
    same truthiness test). No file added/removed ⇒ no Makefile change.
  - [x] **slice 15 — `by_name_dispatch` (part 4a)** (SCRIP `a149ce4`): merge whole `builtins/script_builtins_byname.c`
    (Raku junction/grammar/hash by-name — `script_try_call_builtin_by_name`, `script_try_mutating_builtin_by_name`,
    `script_try_hash_mutating_builtin`/`script_try_hash_builtin`, `script_hash_set_str`/`script_hash_delete_str`,
    `elem_to_descr`, `junction_is`/`jct_one_cmp_*`/`junction_collapse`, `gram_set`/`gram_get`/`gram_get_flavor`/
    `gram_expand`/`gram_n`, statics `itos`/`rtos`/`to_cstring`/`hash_find`) → `by_name_dispatch.c`, then `git rm` the
    emptied silo. WHOLE-coherent-block move: the file's statics are self-contained ⇒ travel as a unit, zero linkage
    promotion. Dropped the 9 redundant include lines (destination already includes the superset); the source's own
    `#define SOH`/`STX` … `#undef STX`/`#undef SOH` block is balanced + identical-valued, and by_name_dispatch.c's
    pre-existing `SOH` is already `#undef`'d (line 483) before the append point ⇒ no macro conflict. The non-headered
    externs `junction_is`/`junction_collapse` have callers in `rt.c`/`gen_runtime.c`/`lower_program.c` via local
    `extern` — unaffected (same symbol/linkage, `*.o`-glob link). `script_builtins.h` KEPT (still declares the two
    `*_by_name` entries, included by destination). Makefile lockstep (RT_PIC_SRCS line + scrip per-`.o` rule both
    removed); stale `/tmp/si_objs/script_builtins_byname.o` deleted. Move-only; all 7 gates byte-identical.
  - [x] **slice 16 — `by_name_dispatch` (part 4b-i)** (SCRIP `a149ce4`): move the contiguous tail cluster
    `rt_call_arr`/`rt_jct_relop`/`call_builtin` (gen_runtime.c L1802-1844) → `by_name_dispatch.c`. AUDIT (saved
    below, reuse it) proved the cluster clean: references ZERO gen_runtime.c file-level statics; uses NONE of the
    giant's five macros; no `NO_AST_WALK_GUARD`. Cross-TU deps all reachable: `rt_call_arr`→`try_call_builtin_by_name`
    (giant stays, decl `interp_private.h:121`); `call_builtin` decl `interp_private.h:120`; `rt_jct_relop` carries its
    own local `extern junction_is`/`junction_collapse` whose defs now live in by_name_dispatch.c (slice 15);
    `BINOP_*` via `gen_runtime.h`→`gen.h`, `TT_*`/`IS_INT_fn`/`VARVAL_fn`/`FAILDESCR` already used in destination.
    Both files already wired ⇒ no Makefile change. Move-only; all 7 gates byte-identical.
  - [x] **slice 17 — `by_name_dispatch` (part 4b-ii)** (SCRIP `a149ce4`): move `proc_as_value` (L369-394) + the
    ~1300-line dispatch giant `try_call_builtin_by_name` (L501-1800) → `by_name_dispatch.c`, TOGETHER (giant calls
    proc_as_value, which has no header decl; appended proc_as_value BEFORE giant ⇒ definition-before-use). Per the
    pre-done audit: zero file-level-static refs; the giant's five macros all `#define`+`#undef`'d within it (balanced,
    travel with it); function-local statics travel inside their fns. The mid-file `#include interp_private.h`+`<time.h>`
    (former L396-7) STAYED (serve `string_section_assign` et seq.); the giant needed NO new includes — uses no time/
    coerce symbols, externals resolve via `gen_runtime.h`, `script_try_call_builtin_by_name` same-file since slice 15.
    Seams: giant → `real_str`/sep/`g_error`; proc_as_value → `lconcat_d`/sep/includes/`string_section_assign`. Both
    files already wired ⇒ no Makefile change. Move-only; all 7 gates byte-identical. **✅ gen_runtime.c now holds ZERO
    by-name members — `by_name_dispatch` .c-consolidation (parts 1–4) COMPLETE.**
  - [ ] **NEXT (pick one):** the `by_name_dispatch` `.c` side has settled, so either **(A)** do its **HEADER
    CONSOLIDATION now** (see the bold HEADER CONSOLIDATION note just below — create `by_name_dispatch.h`, fold the
    decl-only orphans `builtins/script_builtins.h` + `builtins/scan_builtins.h`, repoint callers; this is a decl-reorg
    not pure move-only, so keep it behavior-neutral — same symbols/signatures — and gate all 7), **or (B)** proceed to
    the LANGUAGE-NAMED-file dissolution described below (start with `resolve_runtime.c` → `resolution`). ⚠ **`fn_has_builtin`
    (core.c) — STILL A FINDING FOR LON, not a move:** `static` (decl `core.c:1463`, def `2704`), **ZERO callers
    tree-wide** — vestigial near-dup of exported `core_fn_registered` (differs only by `e->fn != NULL`). Relocating it
    either moves dead code or drags core.c's `_func_buckets`/`_func_init`/`_func_hash` registry statics ⇒ not a clean
    move-only slice. Recommend Lon decide (likely delete = out of move-only scope). `rt_builtin_is_known`/
    `builtin_is_generator` DONE (slice 14).
    THEN the rest of the LANGUAGE-NAMED files: `resolve_runtime.c` → `resolution.c` (and split its WAM
    choice-point/trail → `backtrack`, term/unify/env → `unification`; tightly-coupled shared statics, genuine
    multi-slice), `gen_runtime.c` remainder → `string_ops`/`keywords`/`name_binding`/`collections`/`monitor_trace`.
    THEN `core/core.c` (3449 lines, biggest split) → leave SNO-residue in `core/` (LI-CORE). **`by_name_dispatch`
    HEADER CONSOLIDATION (do when the subsystem settles):** create `by_name_dispatch.h`, fold the now-orphaned
    decl-only `builtins/script_builtins.h` + `builtins/scan_builtins.h` into it, repoint callers (`gen_runtime.c`,
    `interp_private.h`). **Deferred micro-slices:** `rt_unop_*` (lands with `string_ops` + a logical/control home),
    `rt_init` (slice-3 deferral; lands once invocation + comparison builtins have homes).
- [ ] **RS-FENCE.** `scripts/test_gate_runtime_subsystems.sh` asserts the partition; wire into Session Setup.

**Method reminder:** definition-location authoritative; move/rename-only, no behavior change; update the build system
in lockstep with every file op; gate byte-identical after each slice; never start a split you cannot finish+gate+commit.
Read the BODIES before clustering — do not guess a function's subsystem from its current filename (that filename is
exactly the language lie we're removing).

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
**Watermark.** SCRIP `a149ce4` (PUSHED) · .github this commit. **Slices 15–17 were re-integrated as a SINGLE commit `a149ce4` on top of the concurrent push `d51a4e1`** (ICON-BB ICN-HY-2 + SNOBOL4 define groundwork + Pascal rail) — the three originally landed as separate local commits (gated byte-identical each), then on handoff were rebased onto `d51a4e1`; upstream's Pascal `__pas_writeln`/`__pas_write` additions sat INSIDE `proc_as_value` + the giant, so they moved WITH them into `by_name_dispatch.c` (present there, gone from `gen_runtime.c`, no duplication); rebuilt + all 7 gates re-confirmed byte-identical at the combined HEAD. (RS-1 done; RS-2 slices 1-17 landed gated byte-identical (slices 10-14 rebased onto a concurrent push `0b7a166` = ICON-BB bb_call/bb_unop x86() revamp; pre-slice-15 HEAD was `fbd1412`) — runtime_eval, unification, runtime_init, io_format, arithmetic ×2, pattern_match ×5 (`git mv pattern.c`; fold `eval_pat.c`; `rt_pat_*`+capture from `rt.c`; `patnd_*` classifiers from `stmt_exec.c`; `cset_*` from `scan_builtins.c`), by_name_dispatch ×7 (`git mv script_builtins.c → by_name_dispatch.c`; `scan_try_call_builtin` move **dissolving `scan_builtins.c`**; `rt_builtin_is_known`+`builtin_is_generator` from `rt.c`; **slice 15 = whole `script_builtins_byname.c` merged + `git rm`** — Raku junction/grammar/hash silo GONE; **slice 16 = `rt_call_arr`/`rt_jct_relop`/`call_builtin` cluster** from `gen_runtime.c`; **slice 17 = `proc_as_value` + the ~1300-line `try_call_builtin_by_name` giant** from `gen_runtime.c`). **`arithmetic` COMPLETE; `pattern_match` COMPLETE** (only `kw_anchor` open, Lon call); **✅ `by_name_dispatch` .c-CONSOLIDATION (parts 1–4) COMPLETE — `gen_runtime.c` now holds ZERO by-name members; both `scan_builtins.c` AND `script_builtins_byname.c` dissolved.** New header earlier this batch: `src/runtime/pattern_match.h`. Decl-only orphans awaiting consolidation: `builtins/script_builtins.h` (declares the two `*_by_name` entries), `builtins/scan_builtins.h`. Deferred micro-slices pending homes: `rt_init` (slice-3), `rt_unop_*` (slice-6). **NEXT (pick one):** (A) **`by_name_dispatch` HEADER CONSOLIDATION** now that its `.c` settled — create `by_name_dispatch.h`, fold `script_builtins.h`+`scan_builtins.h`, repoint callers (decl-reorg, keep behavior-neutral, gate all 7); or (B) resume LANGUAGE-NAMED-file dissolution: `resolve_runtime.c`→`resolution`(+`backtrack`/`unification` split), `gen_runtime.c` remainder → string_ops/keywords/name_binding/collections/monitor_trace, then `core/core.c` (3449 lines, biggest; leave SNO-residue per LI-CORE). ⚠ **`fn_has_builtin` (core.c) is a FINDING FOR LON, not a move:** static, ZERO callers tree-wide, vestigial near-dup of `core_fn_registered` (differs only by `e->fn!=NULL`); relocating drags core.c's `_func_*` registry statics ⇒ Lon decide (likely delete = out of move-only scope). See the RS CHECKLIST `NEXT` bullet + the RS-1 HANDOFF for the full map.)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
