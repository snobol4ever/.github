# HANDOFF-2026-05-30-OPUS48-LANG-INDEP-RENAME-SLICE-0-1

**Session:** Opus 4.8, 2026-05-30
**one4all HEAD:** `d7f64afa` (== origin/main) — was `2b6394e1` (SMX-4) at session start
**.github HEAD:** `f2b212b7` (== origin/main)
**Goal:** GOAL-LANG-INDEPENDENT-RENAME.md (PIVOT this session from GOAL-SNOBOL4-BB Track B)

---

## What this session did

Lon's directive (PIVOT): everything **from the shared AST (`tree_t`) onward** —
`lower → emitter → interpreter/runtime` — must be **language-independent** in file/function/
variable/macro names. Frontend (parser+lexer) stays language-named. Cultural FEATURE names
(`TABLE`, `SUSPEND`, `unify`, `cut`, `cset`) are kept; only source-language prefixes
(`icn_/pl_/sno_/raku_/sc_/reb_`) are banned. Carved the goal, audited scope (~25 files +
~2,400 symbols), and landed the first slices.

### ✅ Slices DONE (all gate-green, all pushed)
- **Slice 0** (`5370695f`) — `sc_dat → dat`, `ScDatType → DatType` (62 hits; shared
  record/datatype facility used by Icon `record` + Snocone `DATA`). Proved the harness.
- **Slice 1a** (`7d57c6bd`) — `runtime/snobol4/ → runtime/core/`; 9 files de-prefixed
  (`snobol4.c→core.c`, `snobol4_argval/invoke/nmd/pattern→argval/invoke/name_save/pattern`,
  `snobol4_patnd/utf8/runtime_shim.h→patnd/utf8/runtime_shim.h`); 41 `#include` sites + 23
  Makefile path refs + the `-I` flag updated.
- **Slice 1b** (`d7f64afa`) — `sno_ → core_`, 67 runtime symbols (incl. `sno_pat_*`,
  `sno_runtime_error`, `sno_fn_registered`, `g_sno_err_*`, `_sno_abort_*`). 8 frontend
  parser-API symbols EXEMPT (still `sno_`): `sno_parse`, `sno_parse_ast`, `sno_parse_string`,
  `sno_parse_string_ast`, `sno_add_include_dir`, `sno_error`, `sno_nerrors`, `sno_reset`.

**Slice 1 (core runtime) is COMPLETE.**

### Gates — held green the entire session (every slice)
`make scrip` rc=0 · `make libscrip_rt` rc=0 · **Icon smoke m2 6/6 (HARD)**, m3 2/6 · FACT=0 ·
sm_dead 1/1. Baseline at carve was identical, so **zero regression**.

---

## Gotchas discovered (all recorded in the GOAL — read before any slice)

1. **Frontend entry points are NOT in scope even when called from the driver.** `rebus_lower`,
   `snocone_driver/compile`, `sno_parse*` are parser-stage (defined in `src/frontend/*`). Judge
   by DEFINITION site, not call site.
2. **Duplicate basenames across stages.** A *frontend* `src/frontend/snobol4/snobol4.h` (defines
   `Token`) coexisted with the runtime `snobol4.h`. The basename `#include` sed hit both →
   3 frontend files wrongly redirected to `core.h`; reverted. After any header rename, re-check
   frontend files still point at their LOCAL header.
3. **Collision scans are noisy** — `grep '\bWORD\b'` counts struct fields/locals/comments, not
   link symbols. Too-generic stripped names (`error/init/path/call/reset/parse`) need a namespace
   (hence `sno_→core_`, not a bare strip), not a literal collision.
4. **⚠⚠ grep `-I` SILENTLY SKIPS "binary" files — use `grep -a` for EVERY slice.** Post-AST
   sources contain UTF-8 port names **α/β/γ/ω** (RULES: FOUR PORTS = FOUR GREEK NAMES) → grep
   calls them binary. `core.c` (was `snobol4.c`), and almost certainly `bb_exec.c`, `lower_icn.c`,
   `icn_runtime.c`. `grep -rlI`/`-rlIE` (selection) and `grep -rhoI` (verify) all carry `-I` and
   skip them. **This caused Slice 1b's two build failures** (`g_sno_err_stmt` undeclared): core.c
   was never sed'd and the "0 remaining" check was blind. **Always `grep -a` for selection AND
   verification.** `sed -i` itself handles the files fine.

---

## Parked for AFTER the rename (Lon idea, captured in GOAL §"🎉 PARKED — POST-RENAME FUN")

- **32-bit pointer compression** via a base register (R15/RBP): pointers as 32-bit offsets,
  `--ptr32` CLI switch, 99% encapsulated in `DESCR_t` + `sil_macros.h`. **Gating caveat: Boehm GC
  can't trace 32-bit offsets** — decide GC strategy first.
- **Per-language R13/R14/R15 roles** (SMX-4 just freed r13) + a LOCAL/frame register for
  function-local scope; all behind the uniform "all BBs return `DESCR`" ABI.

---

## NEXT — pick up here

1. **Slice 2 — Icon** (prep notes in GOAL Session State): files `icn_runtime→gen_runtime`,
   `icn_value→gen_value`, `icon_box_rt→box_rt`, `icon_gen→gen`, `lower_icn→lower_graph`; ~438
   `icn_/icon_` symbols → prefer a `gen_` namespace for runtime symbols (mirror `core_`), feature
   words where unambiguous (`icn_cset→cset`). Check Icon frontend exemptions first. Watch the
   `bb_*` box-name collisions, and DON'T take the names reserved for Slice 3.
2. **Slice 3 — Prolog** (1109 symbols). Collision boxes RATIFIED: `bb_pl_alt→bb_disj`,
   `bb_pl_seq→bb_conj`, `bb_pl_call→bb_goal`, `bb_pl_var→bb_logicvar`; 8 free `bb_pl_*` strip
   cleanly; `bb_pl.cpp→bb_clause.cpp`.
3. **Slice 4 — Raku** (300). **Slice 5 — backend output libs** (`.il/.j/.wat/.cs`), deferred.

**OPEN QUESTION for Lon:** `lower_sno.c` (the `--dump-sno` transpiler whose OUTPUT is SNOBOL4
source) — treated as EXEMPT (output-target name, like `emit_c`). Confirm or rename.

**Each slice:** `grep -a` selection → sed (symbols globally; files via git mv + Makefile +
includes) → rebuild → HARD gate (Icon m2 6/6, FACT 0, sm_dead ≤1) → commit → push. Never a
broken commit.

---

## Session setup for next time
```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all  /home/claude/one4all
cd /home/claude/one4all && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_icon.sh        # MUST be m2 6/6 (HARD); m3 2/6
bash scripts/test_gate_sm_dead.sh      # 1 (MAX 1)
# Read GOAL-LANG-INDEPENDENT-RENAME.md — esp. Gotcha 4 (grep -a) before touching anything.
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
