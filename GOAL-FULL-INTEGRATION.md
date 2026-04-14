# GOAL-FULL-INTEGRATION.md — Full Parallel-Session Integration

**Repo:** one4all  
**Done when:** Six frontend sessions can develop simultaneously with zero shared-file
conflicts on the hot path. Every frontend plugs into scrip at the same interface.
Every frontend goes lex → parse → IR directly (no intermediate AST). scrip.c is
replaced by a driver + per-language runtime modules. The gate is per-frontend clean
and a full-suite gate for merge commits.

---

## Motivation

After GOAL-ONE-EVAL the shared foundation is sound: one IR, one `interp_eval`,
one `polyglot_execute`, one `bb_broker`. The remaining integration gaps are:

1. **scrip.c is a 4175-line god file.** Icon runtime (lines ~160–570), Prolog
   runtime (lines ~237–3014), the interpreter loop (lines ~1197–2539), polyglot
   init/execute (lines ~640–3430), and `main()` (lines ~3430–4175) all share one
   translation unit. Six sessions touching different frontends will collide on it
   constantly.

2. **Icon and Raku have a redundant AST layer.** Icon: `icon_parse` → `IcnNode`
   tree (`icon_ast.c`) → `icon_lower` → `EXPR_t`. Raku: `raku.tab` → `RakuNode`
   tree (`raku_ast.c`) → `raku_lower` → `EXPR_t`. SNOBOL4 is the correct model:
   grammar actions build `EXPR_t`/`STMT_t` directly; no intermediate struct.
   Snocone and Prolog are also direct (or close to it).

3. **Rebus is not wired into scrip dispatch.** `rebus_lower()` exists and produces
   `Program*` but there is no `lang_rebus` flag, no `.reb` detection, no call in
   `main()`. The frontend is dead from scrip's perspective.

4. **Frontend pipeline styles are inconsistent.**

   | Frontend | Technique | Intermediate AST? | Wired? |
   |----------|-----------|-------------------|--------|
   | SNOBOL4  | Bison/Flex → IR direct | No ✓ | Yes ✓ |
   | Snocone  | Hand lex + CF lowerer → IR direct | No ✓ | Yes ✓ |
   | Prolog   | Hand lex + hand parse → IR direct | No ✓ | Yes ✓ |
   | Icon     | Hand lex + hand parse → IcnNode → IR | **Yes ✗** | Yes ✓ |
   | Raku     | Bison/Flex → RakuNode → IR | **Yes ✗** | Yes ✓ |
   | Rebus    | Bison/Flex → IR (via rebus_lower) | No ✓ | **No ✗** |

5. **`polyglot_init` initialises all six language runtimes for every program.**
   A single `.sno` file initialises the Icon frame stack, Prolog predicate table,
   Raku proc table, etc. Harmless now; will slow session startup as runtimes grow.

6. **No per-frontend test gate.** Every session runs the full 31-test broker suite.
   Sessions need a fast per-language smoke (< 2s) for inner-loop development and
   the full suite only at merge time.

---

## Steps

### Phase 1 — Wire Rebus (unblocks Rebus frontend session)

- [ ] **FI-1** — Wire Rebus into scrip `main()`.
  Add `lang_rebus` flag (`.reb` extension detection). Add
  `extern Program *rebus_compile(const char *src, const char *filename);`
  to scrip.c (or expose via a header). In the parse dispatch block add:
  ```c
  } else if (lang_rebus) {
      prog = rebus_compile(src, input_path);
  ```
  Add `polyglot_execute` routing for `LANG_REBUS` in `polyglot_execute()`.
  Gate: `make scrip` clean; smoke_unified_broker PASS=31 FAIL=0;
  at least one `.reb` file runs without crashing.

---

### Phase 2 — Eliminate redundant AST layers (unblocks clean frontend work)

- [ ] **FI-2** — Eliminate `IcnNode` / `icon_ast.c` from Icon frontend.
  Rewrite `icon_parse.c` so grammar actions build `EXPR_t`/`STMT_t` directly,
  the same way `snobol4.y` does. `icon_lower.c` and `icon_ast.c` are deleted.
  `icon_ast.h` is deleted. `icon_driver.c` calls `icon_parse()` → `Program*`
  directly.
  The `IcnKind → EKind` mapping table in `icon_lower.c` is the translation guide;
  move that logic inline into the new grammar actions.
  Gate: `make scrip` clean; Icon rung01-11 59/59; smoke PASS=31 FAIL=0.

- [ ] **FI-3** — Eliminate `RakuNode` / `raku_ast.c` from Raku frontend.
  Same pattern: rewrite `raku.y` grammar actions to build `EXPR_t`/`STMT_t`
  directly. Delete `raku_ast.c`, `raku_ast.h`, `raku_lower.c`.
  `raku_driver.c` calls Bison parse → `Program*` directly.
  Gate: `make scrip` clean; Raku smoke PASS=12 FAIL=0; smoke_unified_broker
  PASS=31 FAIL=0.

---

### Phase 3 — Split scrip.c into focused modules (unblocks parallel sessions)

This is the prerequisite for six parallel sessions. scrip.c is split into:

```
src/driver/
    scrip.c          ← main() only: arg parse, frontend dispatch, mode dispatch
    interp.c         ← interp_eval(), interp_eval_pat(), execute_program()
    polyglot.c       ← polyglot_init(), polyglot_execute(), ScripModule registry
src/runtime/interp/
    icn_runtime.c    ← IcnFrame stack, icn_call_proc, icn_drive, icn_eval_gen,
                       icn_proc_table, icn_global_names, icn_scan state
    pl_runtime.c     ← Pl_PredTable, g_pl_env, g_pl_trail, g_pl_cut_flag,
                       pl_pred_table_insert/lookup, pl_unify, pl_box_choice
```

- [ ] **FI-4** — Extract Icon runtime to `src/runtime/interp/icn_runtime.c`.
  Move from scrip.c: `IcnFrame`, `icn_frame_stack`, `icn_frame_depth`, `ICN_CUR`,
  `icn_gen_*`, `icn_scan_*`, `icn_global_*`, `icn_proc_table`, `icn_call_proc`,
  `icn_drive`, `icn_eval_gen`, `icn_oneshot_box`.
  Create `icn_runtime.h` with public declarations needed by `interp.c`.
  `interp_eval` Icon EKind cases call through `icn_runtime.h` interface.
  Gate: `make scrip` clean; Icon rung01-11 59/59; PASS=31 FAIL=0.

- [ ] **FI-5** — Extract Prolog runtime to `src/runtime/interp/pl_runtime.c`.
  Move from scrip.c (lines ~237–3014): `Pl_PredTable`, `Term`, `g_pl_env`,
  `g_pl_trail`, `g_pl_cut_flag`, `g_pl_active`, `pl_pred_table_*`,
  `pl_unify_*`, `pl_box_choice`, `pl_trail_*`, all `pl_` helpers.
  Create `pl_runtime.h`.
  Gate: `make scrip` clean; Prolog smoke PASS intact; PASS=31 FAIL=0.

- [ ] **FI-6** — Extract interpreter loop to `src/driver/interp.c`.
  Move `interp_eval()` (~lines 1197–2539), `interp_eval_pat()`, and
  `execute_program()` from scrip.c.
  Create `interp.h` with their declarations.
  `scrip.c` `#include`s `interp.h`, `icn_runtime.h`, `pl_runtime.h`, `polyglot.h`.
  Gate: `make scrip` clean; PASS=31 FAIL=0; no regression.

- [ ] **FI-7** — Extract polyglot layer to `src/driver/polyglot.c`.
  Move `polyglot_init()`, `polyglot_execute()`, `ScripModule`, `g_registry`,
  `parse_scrip_polyglot()` from scrip.c.
  Create `polyglot.h`.
  After this step scrip.c is `main()` + arg parsing only (~400 lines).
  Gate: `make scrip` clean; PASS=31 FAIL=0; no regression.

---

### Phase 4 — Lazy runtime init (correctness / startup)

- [ ] **FI-8** — Make `polyglot_init` language-selective.
  Add a `lang_mask` bitmask to `polyglot_init(prog, lang_mask)`.
  `lang_mask` is computed from the actual languages present in `prog`.
  Icon frame stack is only reset if `lang_mask & LANG_ICN`.
  Prolog pred table is only built if `lang_mask & LANG_PL`. Etc.
  Gate: `make scrip` clean; PASS=31 FAIL=0; single-lang `.sno` does not
  touch Prolog or Icon init paths (verify with a counter or flag).

---

### Phase 5 — Per-frontend test gates (enables parallel sessions)

- [ ] **FI-9** — Add per-frontend smoke scripts.
  One script per frontend, each < 2s, testing only that frontend:
  ```
  scripts/test_smoke_snobol4.sh    — existing SNO tests extracted
  scripts/test_smoke_icon.sh       — Icon rung01-11 subset (fast rungs only)
  scripts/test_smoke_prolog.sh     — Prolog phase 1 rungs
  scripts/test_smoke_raku.sh       — Raku 12 tests
  scripts/test_smoke_snocone.sh    — Snocone tests
  scripts/test_smoke_rebus.sh      — Rebus smoke (after FI-1)
  ```
  Gate: each script exits 0 in < 2s on a clean build.

- [ ] **FI-10** — Document parallel session protocol in RULES.md.
  Add section: "Parallel frontend sessions".
  Rules: each session runs only its per-frontend smoke during development.
  Full broker suite (`test_smoke_unified_broker.sh`) is the merge gate.
  Commits to `icn_runtime.c`, `pl_runtime.c`, `interp.c`, `polyglot.c`
  require full suite to pass before push. Commits to a single frontend's
  `src/frontend/<lang>/` files require only that frontend's smoke.
  `EKind` additions require coordination — open an issue in .github first.

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
| `src/runtime/interp/icn_runtime.c` | Icon session (owns it after FI-4) |
| `src/runtime/interp/pl_runtime.c` | Prolog session (owns it after FI-5) |
| `src/driver/interp.c` | Shared — coordinate |
| `src/driver/polyglot.c` | Shared — coordinate |
| `src/driver/scrip.c` | Shared — rarely touched after split |
| `src/ir/ir.h` (EKind enum) | Shared — coordinate before adding kinds |
| `src/runtime/x86/sm_lower.c` | Shared x86 backend |
| `src/runtime/x86/sm_interp.c` | Shared x86 backend |
| `src/runtime/x86/bb_broker.c` | Frozen — do not modify |

---

## Invariants — never break these

- `make scrip` clean after every step.
- `test_smoke_unified_broker.sh` PASS=31+ after every step.
- `bb_broker.c` is not modified.
- `ir/ir.h` EKind additions require a comment naming the frontend and goal.
- No intermediate AST structs after Phase 2 — frontends build IR directly.
- No scrip.c function additions after Phase 3 — new runtime code goes in the
  appropriate split module.

---

## Key files

| File | Current role | Post-split role |
|------|-------------|----------------|
| `src/driver/scrip.c` | 4175-line god file | ~400-line main() + dispatch only |
| `src/driver/interp.c` | (new) | interp_eval, execute_program |
| `src/driver/polyglot.c` | (new) | polyglot_init, polyglot_execute, registry |
| `src/runtime/interp/icn_runtime.c` | (new) | Icon frame/proc/gen/scan runtime |
| `src/runtime/interp/pl_runtime.c` | (new) | Prolog pred table, unify, trail |
| `src/frontend/icon/icon_ast.c` | IcnNode constructors | deleted after FI-2 |
| `src/frontend/icon/icon_lower.c` | IcnNode→EXPR_t lowering | deleted after FI-2 |
| `src/frontend/raku/raku_ast.c` | RakuNode constructors | deleted after FI-3 |
| `src/frontend/raku/raku_lower.c` | RakuNode→EXPR_t lowering | deleted after FI-3 |
| `src/frontend/rebus/rebus_lower.c` | rebus_lower() — unwired | wired after FI-1 |

---

## Rules

- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- One step per commit. Gate before committing.
- New C files get a standard header: authors, date, one-line purpose.
- Phase 3 steps (FI-4 through FI-7) are pure mechanical moves — no logic changes.
  If the gate breaks during a move, it is a missing `extern` or header, not a
  logic bug.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

---

## Current state (created 2026-04-14, one4all HEAD 9d062108)

No steps started. Gate baseline: PASS=31 FAIL=0.
Start with FI-1 (Rebus wiring — isolated, low risk) then FI-9 (per-frontend
smokes — needed before parallel sessions begin). Phase 3 (scrip.c split) is
the highest-impact work and should be done in a dedicated session with no other
concurrent commits.
