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
  - [x] **slice 3 — `runtime_init`** (SCRIP `0655bd4`): `rt_gc_init`/`rt_set_lang`/`rt_finalize` (+ its private
    read-only statics `g_halt_rc`/`g_halt_set`, never written ⇒ constant-0)/`rt_bomb`/`rt_unhandled_op` pulled from
    grab-bag `rt/rt.c` + `rt_main_init` re-homed from `unification.c` → new `runtime/runtime_init.c`. Move-only; no
    new `.h` (rt.h decls + the `xa_file_header.cpp` PLT strings unchanged). **`rt_init` DEFERRED** — its body is a
    convergence point dragging file-local statics owned by OTHER subsystems (`_rt_IDENT`/`_rt_DIFFER` = comparison
    builtins; `_rt_usercall`→`chunk_reg_lookup`/`call_native_chunk` = native-chunk invocation); moving it now would
    break move-only or recreate the grab-bag. It moves cleanly once invocation + comparison builtins have homes.
  - [ ] **NEXT (cleanest-first):** `io_format` (`rt_write_*` + core
    `output_*`) → `arithmetic` (`rt_arith`/`rt_acomp`/`rt_lcomp`/`rt_unop_*` + the core `add/sub/mul/...` block) →
    `pattern_match` (whole-file `git mv` of `core/pattern.c` + `core/eval_pat.c` + `scan_builtins.c`, then pull
    `rt_pat_*` in + `patnd_*` from `stmt_exec.c`) → the LANGUAGE-NAMED files (`gen_runtime.c`/`resolve_runtime.c`/
    `script_builtins*.c`) split by capability into `backtrack`/`unification`/`resolution`/`by_name_dispatch`/
    `keywords`/`name_binding` (intricate file-local statics ⇒ each is its own multi-slice effort, move whole
    coherent blocks) → `core/core.c` (3449 lines, the biggest split) → leave SNO-residue in `core/` (LI-CORE).
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
**Watermark.** SCRIP `0655bd4` · .github this commit. (RS-1 done; RS-2 slices 1-3 landed gated byte-identical — runtime_eval, unification, runtime_init; `rt_init` deferred until invocation+comparison-builtins homes; remaining subsystems queued above + in the RS-1 HANDOFF.)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
