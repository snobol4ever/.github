# GOAL-DE-INTERP.md — Eradicate the "interp" misnomer (the interpreter is GONE)

**Mandate (Lon 2026-06-15):** The IR-graph interpreter was DELETED (`IR_interp_node`/`IR_interp_once`/
`_resume`/`_pump` excised to `src/attic/IR_interp.c`; mode-2 `--interp` removed from the driver). Nothing
on any run path walks an IR/AST graph to interpret it. **Therefore the token `interp` is now a LIE
wherever it survives in a live file name, directory name, function name, variable name, header guard, or
Makefile target.** Rename every such token to what the code REALLY is, and MOVE the surviving code into
the file/dir that matches its true role. When this rung is done, `grep -rn interp src --include='*.c'
--include='*.h' --include='*.cpp' | grep -v src/attic` returns ONLY the four legitimate English words
below — zero interpreter references.

## ⛔ THE FOUR LEGITIMATE SURVIVORS (do NOT touch — these are NOT the interpreter)

The substring `interp` appears inside real words that have nothing to do with the deleted interpreter.
These are CORRECT and must remain:

1. **`reinterpret_cast`** (C++ keyword) — 5 sites in emitter/template `.cpp`.
2. **`lower_interp_str`** + the Raku grammar's **string interp**olation (`interpolation`/`interpolated`)
   — `src/parser/raku/raku.tab.c` + `raku.lex.c`. This is Raku double-quote string INTERPOLATION, a
   language feature. (If desired for total clarity it MAY be renamed `lower_str_interpolation`, but that
   is OPTIONAL polish, NOT part of the interpreter eradication — track separately if taken.)
3. **`interprets`** in prose comments describing behavior ("this box interprets the operand as …").
   Reword only if it reads as a reference to THE interpreter; plain English usage stays.
4. Any bomb-message STRING that NAMES the deleted interpreter to explain a tombstone
   (e.g. `"[NO-IR-INTERP] … walked IR via IR_interp_pump"`) — these are PROVENANCE for a dead symbol and
   may stay verbatim, OR be reworded to past tense. They are not live interpreter code.

A pre-excision grep that does NOT exclude these four will show ~58 hits; the interpreter-misnomer set is
the remainder.

## THE TRUE-ROLE MAP (what each "interp" thing REALLY is — do-not-re-derive)

Established by reading the live tree 2026-06-15 (the interpreter is already deleted; these are its
orphaned NAMES):

| Current name | What it REALLY is now | Rename to |
|---|---|---|
| `src/interp/` (dir) | holds the surviving Prolog/scan RUNTIME + a box-state header; NO interpreter | **DELETE the dir** — move contents per rows below |
| `src/interp/rt_runtime.c` | already correctly named: `rt_scan_lit` + non-IR-walking Prolog runtime helpers | move → `src/runtime/rt_runtime.c` (it IS runtime) |
| `src/interp/IR_interp_state.h` (`bb_node_state_t`, guard `SCRIP_IR_INTERP_STATE_H`) | per-box EMIT-TIME / runtime execution-state struct (value/counter/state + choice-point fields) — box state, NOT interpreter state | → `src/emitter/box_state.h`, `typedef bb_node_state_t` kept (already right), guard `SCRIP_BOX_STATE_H` |
| `src/driver/interp.h` | the DRIVER's program-execution interface (`execute_program`, `label_table_build`, `polyglot_init`, builtins) | → `src/driver/driver.h` (or `exec.h`), guard `INTERP_H`→`DRIVER_H` |
| `src/driver/interp_private.h` | the DRIVER's private umbrella include | → `src/driver/driver_private.h`, guard updated |
| `src/driver/interp_globals.c` | driver/program global state (`stmt_init`, exec globals) | → `src/driver/driver_globals.c` |
| `src/driver/interp_label.c` | the driver's LABEL TABLE builder | → `src/driver/driver_label.c` (or `label_table.c`) |
| `src/driver/interp_hooks.c` | driver eval/pattern HOOK shims | → `src/driver/driver_hooks.c` |
| `src/driver/interp_data.c` | driver DATA()-statement setup | → `src/driver/driver_data.c` |
| `src/driver/interp_call.c` | driver call/scan dispatch | → `src/driver/driver_call.c` |
| `src/driver/interp_ast_stubs.c` | tombstones for the deleted AST evaluator (`interp_eval`, `execute_program_steps` removed) | → `src/driver/driver_ast_stubs.c` (or fold the lone surviving stub elsewhere — see Step 4) |
| `interp_eval` / `interp_eval_pat` / `interp_eval_ref` (fns) | the deleted AST-walk evaluator's entry points; now BOMB stubs on the EVAL/pattern-eval rail | rename `eval_ast` / `eval_ast_pat` / `eval_ast_ref` (they are AST eval, currently dead-bombed pending the DT_P/EVAL-emit rung) **OR** delete if the EVAL-emit rung (GOAL-SNOBOL4-BB EVAL section) lands first and removes the last caller |
| `__real_interp_eval` / `__wrap_interp_eval` (rs23_diag.c) | linker `--wrap` shim around the above | rename in lockstep with the wrapped symbol; update `-Wl,--wrap=` in Makefile |
| `src/parser/prolog/pl_interp.h` (guard `PL_INTERP_H`) | the Prolog RESOLVE/runtime interface (trail, resolve_env, pred table) — the deleted resolution interpreter's header, now the Prolog runtime API | → `src/parser/prolog/pl_resolve.h` (or `prolog_resolve.h`), guard `PL_RESOLVE_H` |
| Makefile `-I$(SRC)/interp`, `scrip-interp` phony, `--interp`/`run-ir`/`test-ir` comments | dead include dir + dead target + stale doc | drop the include once dir is gone; delete `scrip-interp`; delete the `--interp` comment block |
| `lower_common.c` comment "IR_interp goto landing" | stale comment referencing deleted interpreter | reword to "stage2 goto landing" |

## RUNG — DE-INTERP

Rename every interpreter-misnomer file/dir/symbol/guard/target to its true role (per the map), and
relocate the surviving code into the file/dir matching that role, so that the deleted interpreter leaves
ZERO naming residue. The rename is **mechanical and behavior-neutral** — the only artifact that changes
is identifiers, paths, and the Makefile; emitted code and runtime behavior are byte-for-byte unchanged.
The full gate suite is the proof of neutrality: any gate drop means a rename broke an include or a symbol
edge, not a semantic change → fix the edge, re-run.

**Scope guard:** this rung does NOT change logic, does NOT delete the bomb tombstones' behavior (they
keep failing loudly), and does NOT touch the four legitimate survivors. It is a pure de-misnaming.

## STEPS (run in order; each step = build + full gates + commit; never a broken commit)

Gates after EVERY step (HARD floors, non-decreasing): smoke M4 7/7 · pat-rung M4 19/19 0-SKIP ·
fence TIER1=TIER2=0 · all-language hello matrix row-match vs base-env (rebus drift pre-existing — ignore).
A rename batch that drops a gate has a broken include/symbol edge — restore and fix, do not paper over.

1. **BASELINE + SNAPSHOT.** Build scrip + libscrip_rt clean; capture gate floors; snapshot the base-env
   binaries to `/tmp/base_env/` for the emit-identity check. Record the pre-rung grep count:
   `grep -rn interp src --include='*.c' --include='*.h' --include='*.cpp' | grep -v src/attic | wc -l`.

2. **BOX-STATE HEADER (smallest, most isolated — do first to prove the method).**
   `git mv src/interp/IR_interp_state.h src/emitter/box_state.h`; rewrite the guard
   `SCRIP_IR_INTERP_STATE_H`→`SCRIP_BOX_STATE_H`; update every `#include ".../IR_interp_state.h"` to the
   new path; add `-I$(SRC)/emitter` is already present so the include resolves. Build + gates + commit.

3. **RUNTIME FILE OUT OF THE DEAD DIR.** `git mv src/interp/rt_runtime.c src/runtime/rt_runtime.c`;
   update the Makefile `RT_PIC_SRCS` entry + the per-obj `$(SRC)/interp/rt_runtime.c` recipe line to the
   new path. `src/interp/` is now EMPTY → `rmdir`/`git rm -r` it, and drop `-I$(SRC)/interp` from CBASE,
   CXXRT, and the scrip recipe include lines (3 sites). Build + gates + commit. (After this the `interp`
   DIRECTORY is gone.)

4. **EVAL-RAIL SYMBOL RENAME (`interp_eval*`).** FIRST check whether the EVAL-emit rung
   (GOAL-SNOBOL4-BB.md EVAL section) has landed and deleted the last live caller; if so, DELETE
   `interp_eval`/`interp_eval_pat`/`interp_eval_ref` outright and skip the rest of this step. Otherwise
   rename in lockstep across ALL sites: the bomb defs (`pattern_match.c` `interp_eval_pat`,
   `interp_ast_stubs.c` `interp_eval`, `interp_private.h` `interp_eval_ref` decl), every caller
   (`polyglot.c`, `interp_call.c`, `interp_hooks.c`), the header decls (`interp.h`), AND the linker-wrap
   trio in `rs23_diag.c` (`__real_interp_eval`/`__wrap_interp_eval` + the `-Wl,--wrap=interp_eval` in the
   Makefile link line — grep `--wrap` to find it). New names: `eval_ast`/`eval_ast_pat`/`eval_ast_ref`.
   Build + gates + commit. ⚠️ The `--wrap` rename is the landmine: miss the Makefile flag and the wrap
   silently no-ops (rs23 diag dead) without a build error — verify `nm`/`objdump` shows the wrap edge
   re-bound, or that rs23_diag still intercepts.

5. **DRIVER FILE FAMILY.** `git mv` the six `src/driver/interp_*.c` + the two headers
   (`interp.h`, `interp_private.h`) to their `driver_*` names per the map; rewrite header guards
   (`INTERP_H`→`DRIVER_H`, `INTERP_PRIVATE_H`→`DRIVER_PRIVATE_H`); update EVERY `#include "interp.h"` /
   `"interp_private.h"` / `driver/interp_*` reference across the tree (consumers found 2026-06-15:
   `by_name_dispatch.c`, `gen_runtime.c`, `polyglot.h`, `sync_monitor.c`, `polyglot.c`,
   `interp_private.h` itself); update the Makefile `RT_PIC_SRCS` list (6 entries) + the 6 per-obj recipe
   lines. Build + gates + commit. (Do this as ONE atomic commit — the family cross-includes, so a partial
   rename won't link.)

6. **PROLOG RESOLVE HEADER.** `git mv src/parser/prolog/pl_interp.h src/parser/prolog/pl_resolve.h`;
   guard `PL_INTERP_H`→`PL_RESOLVE_H`; update includes. Build + gates + commit.

7. **MAKEFILE + COMMENT SWEEP.** Delete the `scrip-interp` phony + any orphaned recipe; delete the dead
   `--interp`/`run-ir`/`test-ir`/`make test (--interp …)` comment block at the Makefile head; reword the
   `lower_common.c` "IR_interp goto landing" comment to "stage2 goto landing"; reword any remaining
   bomb-string `IR_interp_pump`/`IR_interp` mentions to past tense if desired (optional). Build + gates +
   commit.

8. **COMPLETION TEST.**
   `grep -rn interp src --include='*.c' --include='*.h' --include='*.cpp' | grep -v src/attic` returns
   ONLY the four legitimate survivors (reinterpret_cast / Raku interpolation / English "interprets" prose
   / dead-symbol provenance strings) — ZERO interpreter file/dir/symbol/guard names. Plus: no `src/interp`
   dir, no `interp.h`/`pl_interp.h`, no `-I$(SRC)/interp`, no `scrip-interp` target. All gates green,
   all-language suites non-decreasing. Then DE-INTERP is DONE.

## ⛔ COMMITTED ≠ LANDED ≠ HANDED-OFF — `git push` OR IT NEVER HAPPENED
Per the standing rule (see GOAL-DEAD-CODE-SWEEP.md): the build container's git is EPHEMERAL. Nothing is
durable until `git push` succeeds for EVERY repo touched (here: SCRIP for the code, `.github` for this
goal file). Confirm `git rev-list --count @{u}..HEAD == 0` in each before declaring any step landed. Set
`git config user.name/user.email` per-repo before committing.

## Hard-won facts (do-not-re-derive)
- The interpreter is ALREADY deleted — this rung renames its corpse's NAMES, it does NOT delete logic.
- `lower_interp_str` / `interpolation` (Raku) and `reinterpret_cast` (C++) are NOT the interpreter — never
  blanket `sed s/interp//`. A naive global replace WILL corrupt `reinterpret_cast` and break the build.
- The `interp_eval*` family is on the EVAL rail and is currently BOMB-stubbed; coordinate Step 4 with the
  GOAL-SNOBOL4-BB EVAL-emit rung — whichever lands first dictates rename-vs-delete.
- The `rs23_diag.c` `--wrap` trio + the Makefile `-Wl,--wrap=` flag must move in lockstep or the diag wrap
  silently no-ops with no build error (the one rename in this rung that fails SILENTLY).
- The driver `interp_*` family cross-includes — rename it in ONE atomic commit, not piecemeal.
