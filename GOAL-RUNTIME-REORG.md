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
    - **then `core/core.c`** (3449 lines, biggest split) → leave SNO-residue in `core/` (LI-CORE).

- [ ] **RS-FENCE.** `scripts/test_gate_runtime_subsystems.sh` asserts the partition; wire into Session Setup.

### Open items for Lon (NOT moves — decide before/independently of the slices)
- **`fn_has_builtin` (core.c)** — `static` (decl `core.c:1463`, def `2704`), ZERO callers tree-wide; vestigial
  near-dup of exported `core_fn_registered` (differs only by `e->fn != NULL`). Relocating drags core.c's
  `_func_buckets`/`_func_init`/`_func_hash` registry statics ⇒ not a clean move. Likely **delete** (out of
  move-only scope).
- **`scan_try_call_builtin` dup decl** at `interp_private.h:124` — identical pre-existing decl (NOT an orphan).
  Harmless (`WARN := -w`, no `-Werror`). One-line follow-up if a single decl-site is wanted.
- **`kw_anchor`** — RS-1 map lists it under BOTH `pattern_match` and `keywords.c`; pick a home.
- **`_rt_IDENT`/`_rt_DIFFER` home (the "comparison" builtins)** — surfaced trying to clear `rt_init` (below). NOT a
  clean slice. Bodies ARE self-contained (SNOBOL string-identity: `VARVAL_fn`+`strcmp`, NOT `descr_identical`), but
  the **RS-1 map defines no `comparison` subsystem** — it folds comparison into `arithmetic.c` ("numeric ops,
  comparison"), yet lists `ident`/`differ` on their OWN "Identity/differ" row (≠ the numeric "comparison" rows).
  Three defensible homes: (1) `arithmetic.c` (map says comparison→arithmetic, but these are string not numeric);
  (2) `values.c` (identity kinship with s23 `descr_identical`); (3) new `comparison.c` (contradicts the 17-subsystem
  partition). Also needs de-staticizing the two `static` fns in `rt.c` (body-neutral linkage change). **Pick a home.**

### Deferred micro-slices (pending destination homes)
- **`rt_init`** (slice-3) — convergence point dragging OTHER subsystems' statics (`_rt_IDENT`/`_rt_DIFFER` =
  comparison [home decision in Open-items above, OPEN]; `_rt_usercall` → `chunk_reg_lookup`/`call_native_chunk` =
  native-chunk invocation). `invocation` now HAS a home (s24); `rt_init` still blocked on the comparison-builtins home.
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
**Watermark.** SCRIP `4aa19d7` (2 slices landed this session, each gated byte-identical, PUSHED) ·
.github this commit = watermark + checklist update for the 2 slices (no SCRIP code re-touched here;
`.github` is a different repo from SCRIP). RS-1 done; RS-2 slices 1–24 landed gated byte-identical.
`arithmetic` / `pattern_match` / `by_name_dispatch` / `keywords` / `string_ops` (.c + header) + `name_binding`
/ `values` / `invocation` (.c) COMPLETE; resolver renamed to `resolution`. This session (Opus, rebased onto
`4501209` — upstream Pascal PB-8 was runtime-disjoint; combined tree re-built + re-gated green before push):
s23 `values` (`descr_identical`) `ae76122`, s24 `invocation` (`sm_call_proc`/`proc_table_call`) `4aa19d7` — both
carved from `builtins/gen_runtime.c` (654 → 209 lines). The clean move-only slices are now EXHAUSTED; every
remaining target needs a Lon decision: (a) the `_rt_IDENT`/`_rt_DIFFER` **comparison-home** call (arithmetic.c vs
values.c vs new comparison.c — see Open items; unblocks `rt_init`); (b) resolution `builtins/`→`runtime/` layout;
(c) the hard `backtrack` cluster (gen_runtime.c remainder, overlaps the resolution split); (d) `core/core.c` (3449
lines, LI-CORE). Open Lon calls: `fn_has_builtin` (likely delete), `scan_try_call_builtin` dup decl, `kw_anchor`
home, comparison-home.
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
