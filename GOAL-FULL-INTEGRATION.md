# GOAL-FULL-INTEGRATION.md — Full Parallel-Session Integration

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** Six frontend sessions can develop simultaneously with zero shared-file
conflicts on the hot path. Every frontend plugs into scrip at the same interface.
Every frontend goes lex → parse → IR directly (no intermediate AST). scrip.c is
replaced by a driver + per-language runtime modules. The gate is per-frontend clean
and a full-suite gate for merge commits.

---

## Architecture: what we are building toward

```
source file
    │
    ▼  (per-language: lex + parse → EXPR_t/STMT_t direct, no intermediate AST)
 frontend/
    snobol4/   .sno  → sno_parse()       → CODE_t*   [LANG_SNO]  ✅ direct
    snocone/   .sc   → snocone_compile() → CODE_t*   [LANG_SNO]  ✅ direct
    rebus/     .reb  → rebus_compile()   → CODE_t*   [LANG_REB]  🔴 unwired, needs wrapper
    icon/      .icn  → icon_compile()    → CODE_t*   [LANG_ICN]  ⚠️  has IcnNode AST layer
    prolog/    .pl   → prolog_compile()  → CODE_t*   [LANG_PL]   ✅ thin AST, acceptable
    raku/      .raku → raku_compile()    → CODE_t*   [LANG_RAKU] ⚠️  has RakuNode AST layer
    │
    ▼  CODE_t* = linked list of STMT_t, each holding one EXPR_t tree in ir/ir.h EKind
 ir/ir.h  — one EXPR_t struct, one EKind enum, ALL languages, ALL backends
    │
    ├──▶  --interp:   interp_eval()  tree-walk in driver/interp.c   [correctness ref]
    │
    ├──▶  --interp:   sm_lower()  → SM_Program  → sm_interp_run()   [x86 default]
    │
    └──▶  --run:  sm_lower()  → SM_Program  → sm_codegen()  → sm_jit_run()   [x86 JIT]
```

**Pattern primitives in EKind are correct and intentional.**
E_ANY, E_SPAN, E_BREAK, E_ARB, E_FENCE, etc. are NOT pollution.
Each has a distinct bb_box_fn with different Byrd-box wiring (bb_any, bb_span, bb_arb...).
Encoding them as E_FNC("ANY",...) would force string-matching in the emitter — exactly
what pat_prim_kind() exists to avoid. They are semantic primitives, not SNOBOL4-specific
names. Rebus already uses E_ARBNO. Any language that uses patterns gets them for free.
Do NOT change this.

**What is actually cancer (the things this goal removes):**
1. scrip.c — 4175-line god file doing 6 jobs, causes merge collisions every session
2. IcnNode AST layer in Icon — gratuitous; IcnKind→EKind is a 1-to-1 rename table
3. RakuNode AST layer in Raku — same diagnosis; RakuKind→EKind is a 1-to-1 rename table
4. Rebus not wired — rebus_lower() exists, no LANG_REB, no .reb dispatch, frontend is dead
5. EXPR_T_DEFINED guard + scrip_cc.h EXPR_t duplicate — ir.h must be the single truth
6. LANG_REBUS missing — only 5 LANG_* constants; Rebus is invisible to the whole system
7. polyglot_init initialises ALL runtimes for every program — lazy init is correct
8. SM layer missing 32 EKinds — --interp is SNOBOL4-only today; should cover all 6 languages
9. No per-frontend smoke scripts — every session runs the full 31-test suite

---

## Phase 0 — Foundation: unify types, add LANG_REB (prerequisite for everything else)

**Do Phase 0 before any other phase. Header-only changes, zero logic change, zero risk.**

- [x] **FI-0A** — Unify `EXPR_t` definition: `ir.h` is the sole owner.
  Problem: `scrip_cc.h` defines its own `EXPR_t` guarded by `EXPR_T_DEFINED`; `ir.h`
  defines a second copy with the same guard. Two definitions of the same struct is a lie.
  Fix: remove the `EXPR_t` struct body from `scrip_cc.h`; add `#include "ir.h"` (with a
  relative path) so `scrip_cc.h` gets `EXPR_t` from `ir.h`. Remove the `EXPR_T_DEFINED`
  guard from `ir.h` entirely — it no longer needs one. Verify `dval` field name is
  consistent (it is: both use `dval`).
  Gate: `make scrip` clean; PASS=31 FAIL=0.

- [x] **FI-0B** — Add `LANG_REB` constant to `scrip_cc.h`.
  Add after LANG_SCRIP = 4:
    `#define LANG_REB   5   /* Rebus   */`
  Update the comment on `STMT_t.lang` to list all six languages.
  Gate: `make scrip` clean; PASS=31 FAIL=0.

---

## Phase 1 — Wire Rebus (unblocks Rebus frontend session)

- [x] **FI-1A** — Write `rebus_compile()` wrapper.
  In `rebus_lower.c`, add function `rebus_compile(const char *src, const char *filename)`:
  call `rebus_parse()` then `rebus_lower()`, set `st->lang = LANG_REB` on each STMT_t,
  return `CODE_t*`. Mirror the pattern of `icon_compile()` exactly.
  Expose in `rebus_lower.h`: `CODE_t *rebus_compile(const char *src, const char *filename);`
  Gate: `make scrip` clean (Rebus not yet callable from main but must link cleanly).

- [x] **FI-1B** — Wire Rebus into `scrip.c` `main()` and `polyglot_execute()`.
  In `scrip.c`:
  - Add `#include "../frontend/rebus/rebus_lower.h"` to includes.
  - Add `lang_rebus` flag via `.reb` extension detection (same 2-line pattern as lang_icon).
  - In parse dispatch block: `lang_rebus ? rebus_compile(src, input_path) : ...`
  In `polyglot_execute()`: add LANG_REB routing (same shape as LANG_ICN).
  In `polyglot_init()`: add LANG_REB to init block (shares icn_proc_table path for now).
  In `parse_scrip_polyglot()` tag parser: add `"Rebus"` → `LANG_REB`.
  Gate: `make scrip` clean; smoke_unified_broker PASS=31 FAIL=0;
  at least one `.reb` file runs under `--interp` without crashing.

---

## Phase 2 — Eliminate redundant AST layers

**The answer to "is lex→parse→AST→IR necessary?" is No.**
SNOBOL4 and Snocone prove it: grammar actions build EXPR_t directly.
The IcnKind→EKind and RakuKind→EKind tables are 1-to-1 renames — move them inline.

- [x] **FI-2** — Eliminate `IcnNode` / `icon_ast.c` from Icon frontend.
  Rewrite `icon_parse.c` so parser actions build `EXPR_t`/`STMT_t` directly.
  The `IcnKind → EKind` mapping in `icon_lower.c` is the translation guide; move it
  inline into the new parser actions. `icon_runtime.c` (frame/generator state) is untouched.
  Delete: `icon_ast.c`, `icon_ast.h`, `icon_lower.c`, `icon_lower.h`.
  `icon_driver.c` calls `icon_parse()` → `CODE_t*` directly; lower step disappears.
  Gate: `make scrip` clean; Icon rung01-11 59/59; smoke PASS=31 FAIL=0.

- [x] **FI-3** — Eliminate `RakuNode` / `raku_ast.c` from Raku frontend.
  Rewrite `raku.y` grammar actions to build `EXPR_t`/`STMT_t` directly.
  The `RakuKind → EKind` table in `raku_lower.c` is the translation guide.
  Delete: `raku_ast.c`, `raku_ast.h`, `raku_lower.c`, `raku_lower.h`.
  `raku_driver.c` calls Bison parse → `CODE_t*` directly.
  Gate: `make scrip` clean; Raku smoke PASS=12 FAIL=0; smoke_unified_broker PASS=31 FAIL=0.

---

## Phase 3 — Split scrip.c into focused modules (enables parallel sessions)

**This is the most important phase. Without it, six sessions = six-way merge war.**
All steps are pure mechanical moves. No logic changes. Gate breaks = missing extern, not logic bug.

Target layout after Phase 3:
```
src/driver/
    scrip.c          ← main() only: arg parse, extension detect, frontend dispatch (~400 lines)
    interp.c         ← interp_eval(), interp_eval_pat(), interp_eval_ref(), execute_program()
    polyglot.c       ← polyglot_init(), polyglot_execute(), ScripModule, g_registry, g_polyglot
src/runtime/interp/
    icn_runtime.c    ← IcnFrame stack, icn_call_proc, icn_drive, icn_eval_gen,
                       icn_proc_table, icn_global_names, icn_scan state, icn_scope_*
    pl_runtime.c     ← Pl_PredTable, g_pl_env, g_pl_trail, g_pl_cut_flag,
                       pl_pred_table_*, pl_unify, pl_box_choice, pl_trail_*, pl_ helpers
```

- [x] **FI-4** — Extract Icon runtime to `src/runtime/interp/icn_runtime.c`.
  Move from scrip.c: `IcnFrame`, `icn_frame_stack`, `icn_frame_depth`, `ICN_CUR`,
  `icn_gen_*`, `icn_scan_*`, `icn_global_*`, `icn_proc_table`, `icn_call_proc`,
  `icn_drive`, `icn_eval_gen`, `icn_oneshot_box`, `icn_scope_add`, `icn_scope_patch`.
  Create `icn_runtime.h` with all declarations needed by `interp.c` and `polyglot.c`.
  Gate: `make scrip` clean; Icon rung01-11 59/59; PASS=31 FAIL=0.

- [x] **FI-5** — Extract Prolog runtime to `src/runtime/interp/pl_runtime.c`.
  Move from scrip.c: `Pl_PredTable`, `g_pl_env`, `g_pl_trail`, `g_pl_cut_flag`,
  `g_pl_active`, `pl_pred_table_*`, `pl_unify_*`, `pl_box_choice`, `pl_trail_*`,
  all `pl_` helpers, Prolog Term→DESCR_t bridge functions.
  Create `pl_runtime.h`.
  Gate: `make scrip` clean; Prolog smoke PASS intact; PASS=31 FAIL=0.

- [x] **FI-6** — Extract interpreter loop to `src/driver/interp.c`.
  Move from scrip.c: `interp_eval()`, `interp_eval_pat()`, `interp_eval_ref()`,
  `execute_program()`, and all static helpers they call (label_table_*, prescan_defines,
  call_user_function, SC-1 DATA registry, g_lang, g_sno_err_*, etc.).
  Create `interp.h`. `scrip.c` #includes `interp.h`.
  Gate: `make scrip` clean; PASS=31 FAIL=0.

- [x] **FI-7** — Extract polyglot layer to `src/driver/polyglot.c`.
  Move from scrip.c: `polyglot_init()`, `polyglot_execute()`, `ScripModule`,
  `g_registry`, `parse_scrip_polyglot()`, `g_polyglot`.
  Create `polyglot.h`. After this step scrip.c is main() + arg parse + dispatch only (~400 lines).
  Gate: `make scrip` clean; PASS=31 FAIL=0.

---

## Phase 4 — Lazy runtime init

- [x] **FI-8** — Make `polyglot_init` language-selective.
  Signature: `polyglot_init(CODE_t *prog, uint32_t lang_mask)`.
  `lang_mask` computed from actual `STMT_t.lang` values present in `prog`.
  Icon frame stack only reset if `lang_mask & (1u << LANG_ICN)`.
  Prolog pred table only built if `lang_mask & (1u << LANG_PL)`. Etc.
  Gate: `make scrip` clean; PASS=31 FAIL=0; single-lang `.sno` does not
  touch Prolog or Icon init paths (verify with a counter or flag).

---

## Phase 5 — Per-frontend smoke scripts and SM coverage

- [x] **FI-9** — Add per-frontend smoke scripts.
  ```
  scripts/test_smoke_snobol4.sh
  scripts/test_smoke_icon.sh
  scripts/test_smoke_prolog.sh
  scripts/test_smoke_raku.sh
  scripts/test_smoke_snocone.sh
  scripts/test_smoke_rebus.sh
  ```
  Each < 2s, tests only its frontend. Gate: each exits 0 in < 2s on a clean build.

- [x] **FI-10** — Extend SM lower to cover Icon, Prolog, Raku, Rebus EKinds.
  Currently sm_lower.c handles 73 of 105 EKinds. Missing 32 are all non-SNOBOL4 kinds.
  After this step --interp works for all six languages.
  Implement per language in sub-steps, guided by the icn_runtime.h / pl_runtime.h
  interfaces established in Phase 3.
  Gate: smoke_unified_broker PASS=31 FAIL=0; each frontend smoke passes under --interp.

- [x] **FI-11** — Document parallel session protocol in RULES.md.
  Add section: "Parallel frontend sessions".
  Per-frontend smoke = inner-loop gate. Full broker suite = merge gate.
  Commits to shared files (interp.c, polyglot.c, icn_runtime.c, pl_runtime.c) require
  full suite before push. Commits to src/frontend/<lang>/ require only that smoke.
  EKind additions require a .github issue first.

---

## Execution order

```
FI-0A → FI-0B    ← headers only, zero risk, unblocks everything
FI-1A → FI-1B    ← Rebus wiring, isolated, one session
FI-4  → FI-5     ← extract runtimes (can be parallel sessions after FI-0)
FI-6  → FI-7     ← extract interp + polyglot (must follow FI-4/FI-5)
FI-2             ← Icon AST elimination (own session, can run after FI-4)
FI-3             ← Raku AST elimination (own session, parallel with FI-2)
FI-8             ← lazy init (after FI-7)
FI-9             ← smoke scripts (parallel with FI-2/FI-3)
FI-10            ← SM coverage (after FI-2/FI-3/FI-4/FI-5)
FI-11            ← docs (after FI-9/FI-10)
```

---

## File ownership map (post-split)

| File | Owned by session |
|------|-----------------|
| `src/frontend/snobol4/` | SNOBOL4 session |
| `src/frontend/icon/` | Icon session |
| `src/frontend/prolog/` | Prolog session |
| `src/frontend/raku/` | Raku session |
| `src/frontend/snocone/` | Snocone session |
| `src/frontend/rebus/` | Rebus session |
| `src/runtime/interp/icn_runtime.c` | Icon session (after FI-4) |
| `src/runtime/interp/pl_runtime.c` | Prolog session (after FI-5) |
| `src/driver/interp.c` | Shared — coordinate |
| `src/driver/polyglot.c` | Shared — coordinate |
| `src/driver/scrip.c` | Shared — rarely touched after split |
| `src/ir/ir.h` | Shared — coordinate before adding EKinds |
| `src/runtime/x86/sm_lower.c` | Shared x86 backend |
| `src/runtime/x86/sm_interp.c` | Shared x86 backend |
| `src/runtime/x86/bb_broker.c` | Frozen — do not modify |

---

## Invariants — never break these

- `make scrip` clean after every step.
- `test_smoke_unified_broker.sh` PASS=31+ after every step.
- `bb_broker.c` is not modified.
- `ir/ir.h` EKind additions require a comment naming the frontend and goal.
- Pattern primitives (E_ANY, E_SPAN, E_ARB, etc.) stay as EKind nodes — do NOT
  convert to E_FNC. They have distinct Byrd-box wiring and are shared across languages.
- No intermediate AST structs after Phase 2 — frontends build IR directly.
- No scrip.c function additions after Phase 3 — new code goes in the split module.
- LANG_* constants live in scrip_cc.h. EXPR_t lives in ir.h. One truth each.

---

## Rules

- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- One step per commit. Gate before committing.
- New C files get a standard header: authors, date, one-line purpose.
- Phase 3 steps (FI-4 through FI-7) are pure mechanical moves — no logic changes.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

---

## Current state (updated 2026-04-14, SCRIP HEAD 43dc03da)

FI-0A through FI-11 done. ALL steps complete.
Smoke: PASS=31 FAIL=0. Raku --interp: PASS=12 FAIL=0.
scrip.c: 478 lines — main() + arg parse + frontend dispatch only.
interp.c: 2768 lines. polyglot.c: 301 lines. interp.h + polyglot.h: public interfaces.
FI-8: polyglot_init language-selective (lang_mask). FI-9: 6 per-frontend smoke scripts.
FI-10: SM+BB lowering for all 55 non-SNOBOL4 EKinds. FI-11: parallel session protocol in RULES.md.
GOAL COMPLETE.
