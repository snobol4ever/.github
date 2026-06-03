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
  - [ ] **NEXT (cleanest-first):** `pattern_match` (part 3+) — pull the big `rt_pat_*` family (~30 fns:
    `rt_pat_lit`…`rt_pat_usercall_args` + capture/`rt_dcap_*`/`rt_at_cursor`/`rt_defer_match`) out of grab-bag `rt.c`
    into `pattern_match.c` (READ THE BODIES — `rt.c` interleaves them with cut/backtrack that STAYS); then `patnd_*`
    classification helpers from `stmt_exec.c` (~9 predicates) + `cset_resolve`/`cset_has` from `scan_builtins.c`
    (its `scan_try_call_builtin` goes to `by_name_dispatch`, NOT here). → then the LANGUAGE-NAMED files
    (`gen_runtime.c`/`resolve_runtime.c`/`script_builtins*.c`) split by capability into `backtrack`/`unification`/
    `resolution`/`by_name_dispatch`/`keywords`/`name_binding` (intricate file-local statics ⇒ each is its own multi-
    slice effort, move whole coherent blocks) → `core/core.c` (3449 lines, the biggest split) → leave SNO-residue in
    `core/` (LI-CORE). **Deferred micro-slices to fold in along the way:** `rt_unop_*` (above; lands with
    `string_ops` + the logical home) and `rt_init` (slice-3 deferral; lands once invocation + comparison builtins
    have homes).
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
**Watermark.** SCRIP `0f817f9` · .github this commit. (RS-1 done; RS-2 slices 1-8 landed gated byte-identical — runtime_eval, unification, runtime_init, io_format, arithmetic-part-1, arithmetic-part-2, pattern_match-part-1 (`git mv core/pattern.c`), pattern_match-part-2 (fold `core/eval_pat.c`); **`arithmetic` subsystem COMPLETE; `pattern_match` whole-file moves COMPLETE** (`core/` pattern `.c` files relocated, only `patnd.h` stays). Deferred micro-slices pending homes: `rt_init` (slice-3) + `rt_unop_*` (slice-6). Next = `pattern_match` part 3+ (`rt_pat_*` family from grab-bag `rt.c`, then `patnd_*` from `stmt_exec.c` + `cset_*` from `scan_builtins.c`); remaining subsystems queued above + in the RS-1 HANDOFF.)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
