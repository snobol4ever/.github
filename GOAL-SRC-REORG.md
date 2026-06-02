# GOAL-SRC-REORG.md — Physical re-partition of `SCRIP/src` by pipeline role

**Lon directive (2026-06-02):** "I am so tired of not being able to find things and being mis-labeled.
Let's fix this." Re-slice the physical `src/` tree so every folder names its ROLE in the pipeline, and so a
type's DEFINITION and its ALLOCATOR live together. This is a `grand master reorg` (touches Makefile + PLAN +
every `#include`). **ALL OTHER SESSIONS ON HOLD** until this rung is parked or done.

## ⛔ WHY (the diagnosis, proven from the `*.h` scan 2026-06-02)

1. **`include/` is a grab-bag** mixing SIX unrelated roles: the AST contract (`ast.h`), the IR contract
   (`IR.h`), the DEAD Stack-Machine opcodes (`SM.h`), the compiled-program struct (`stage2.h`/`bb_program.h`),
   the mode-2-oracle pattern types + LEGACY subject globals (`bb_box.h`), the DESCR value type (`descr.h`),
   and the XA emitter opcodes (`XA.h`). "Where is this type?" has no predictable answer.
2. **`runtime/interp/` is NOT the interpreter.** It is the language-builtin + Prolog-resolution layer
   (`gen.h` is wall-to-wall generator-state structs; `resolve_runtime.c` is the WAM resolver;
   `scan_builtins`/`script_builtins*` are builtin tables). The name reads like "the mode-2 interpreter" and
   has misled multiple sessions. **The real mode-2 interpreter is `lower/bb_exec.c`** — hiding in `lower/`.
3. **The IR contract is split + polluted.** `IR_t`/`IR_e`/`IR_graph_t` are in `include/IR.h` but the
   allocator (`IR_alloc`/`IR_node_alloc`/`bb_reset`) is in `lower/scrip_ir.c` — different folders. And
   `IR.h` carries mode-2 EXECUTION-STATE structs (`bb_arbno_state_t`, `bb_choice_state_t`, `bb_goal_state_t`,
   `bb_ite_state_t`, `bb_findall_state_t`, `sno_prog_t`, the `RESOLVE_IDX_*` Prolog macros) that are NOT the
   IR — they belong with the interpreter.
4. **The interpreter header leaks runtime.** `lower/bb_exec.h` declares dozens of `rt_pl_atom_concat` /
   `rt_pl_findall` / … — Prolog runtime builtins declared in the interpreter's header.
5. **Modes 3 and 4 are NOT separate code bodies.** `emit_core.h`: `g_medium ∈ {BB_MEDIUM_TEXT,
   BB_MEDIUM_BINARY}`. Mode-3 = EMITTER(BINARY) + RX slab + ~30 lines driver wiring; mode-4 =
   EMITTER(TEXT) + as/gcc + ~30 lines driver wiring. They share ONE emitter; only mode-2 (`bb_exec.c`) is a
   separate body. So A/B/C are DRIVER WIRING + a medium switch over ONE emitter + ONE interpreter — NOT
   three partitions.

## 🎯 TARGET TREE (the decided slicing)

```
src/
  parser/            ← was frontend/   (the 6 language front-ends: snobol4 icon prolog raku rebus snocone)
  contracts/         ← the pipeline SPINE: the types that flow stage→stage, each beside its allocator
      descr.*        (DESCR_t — the universal value)
      ast.*          (tree_t + tree_e + ast allocator/print/verify; was include/ast.h + src/ast/)
      ir.*           (IR_t + IR_e + IR_graph_t + IR_alloc/IR_node_alloc/bb_reset; was include/IR.h + lower/scrip_ir.c)
      stage2.*       (stage2_t + bb_program_t; was include/stage2.h + include/bb_program.h)
      name_t.* descr-adjacent value helpers as needed
  lower/             ← AST→IR ONLY (lower*.c). IR-def, bb_exec, sm_prog all MOVE OUT.
  emitter/           ← the per-box templates (BB_templates + XA_templates) + dispatch + x86 encoders.
                       Serves BOTH mode-3 (BINARY) and mode-4 (TEXT).
  interp/            ← the mode-2 BB-graph interpreter ONLY (was lower/bb_exec.{c,h}) + the bb_*_state_t
                       execution-state structs evicted from ir.h.
  machine/           ← the in-memory machine substrate: the mmap'd RX slab (was processor/bb_pool.*,
                       bb_boxes.c) + the preamble that builds stage2_t (was lower/sm_prog.c).
  runtime/           ← the runtime LIBRARY, as its 3 honest sub-layers:
      core/          (the SNOBOL execution model: core.c pattern.c eval_* name tables; UNCHANGED)
      rt/            (the shared low-level rt_* helpers templates call @PLT; UNCHANGED)
      builtins/      ← was runtime/interp/  (generator/scanner/resolver/builtin-table)
  driver/            ← the CLI + the A/B/C mode SELECTOR (scrip.c) + polyglot + the interp_* csnobol4 shim
  backends/          ← all non-x86, dormant under the X86-ONLY rule: was driver/{js,jvm,net,wasm} +
                       runtime/{js,jvm,net,wasm} + backend/jasmin.jar + the emitter JVM/JS/NET/WASM arms
  attic/             ← the DEAD Stack Machine: was include/SM.h + driver/scrip_sm.* + processor/smx_dead_stubs.c
                       (quarantine; delete only after confirming stage2 no longer needs any SM type)
  tools/             ← proof/scaffolding, NOT the product: prove_lower2.c, tmatch_proto.c, tools/emit_per_kind_audit,
                       emitter/test_template_byte_identity.c, emitter/demo_template_productions.c
```

## 🔧 INCLUDE-PATH STRATEGY (the key to keeping every slice GREEN)

- **The Makefile is the ONLY build config.** `scripts/build_scrip.sh` just runs `make -j4 scrip`. The
  `make libscrip_rt` target's source list is ALSO in the Makefile. So a move = edit the Makefile (source
  lists at the `RT_PIC_SRCS`-style block + the per-`.o` compile rules) + fix `#include`s. Nothing else.
- **`-I` paths (Makefile lines ~35/37/194-195):** today
  `-I$(SRC) -I$(SRC)/include -I$(SRC)/lower -I$(SRC)/processor -I$(SRC)/emitter -I$(SRC)/runtime/core -I$(RT) [-I$(RT)/rt -I$(SRC)/frontend/snobol4 -I$(SRC)/frontend/raku]`.
  **TACTIC: when you move a header, ADD its new dir to the `-I` list in the SAME slice.** A bare
  `#include "ir.h"` then resolves no matter where the file physically sits. Most includes here are BARE
  (`#include "IR.h"`, `"descr.h"`, `"core.h"`) and survive a move purely via `-I`.
- **RELATIVE includes break on a move** (`#include "../ast/ast.h"`, `"../../frontend/snobol4/scrip_cc.h"`,
  `"../runtime/interp/gen.h"` — seen in `lower.h`). Each must be rewritten when the depth/path changes.
- **SAME-DEPTH directory renames are safe for INTERNAL relatives.** `runtime/interp` → `runtime/builtins`
  keeps every `../foo` inside those files valid; only references FROM ELSEWHERE + the Makefile change.
- **Header-rename caution:** if you rename `IR.h`→`ir.h` on a case-insensitive checkout it can collide; keep
  the include-guard (`SCRIP_IR_H`) and prefer ADDING `-I` over renaming the basename unless the rung says to.

## ⛔ GATE (run after EVERY slice — a reorg is behavior-neutral BY CONSTRUCTION, so ANY delta = a real bug)

```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh                          # rc=0 (make scrip)
make libscrip_rt >/tmp/rt.log 2>&1; tail -1 /tmp/rt.log   # "Built: out/libscrip_rt.so"
bash scripts/test_smoke_snobol4.sh 2>&1 | grep -E 'mode-2|PASS='   # m2 7/7 HARD
bash scripts/test_smoke_icon.sh    2>&1 | grep -E 'mode-2|PASS='   # Icon m2 12/12 HARD
bash scripts/prove_lower2.sh       2>&1 | tail -1                  # 67 PASS
bash scripts/audit_concurrency_invariants.sh 2>&1 | tail -1       # OK
bash scripts/test_gate_no_bb_bin_t.sh 2>&1 | tail -1              # 0
```
Baseline at rung start (SCRIP `10fbe32`): m2 SNOBOL4 **7/7**, Icon **12/12**, Prolog **5/5**, prove_lower2 **67**,
no_bb_bin_t **0**, concurrency OK. m3/m4 counts are tracked-not-gated; they must not DROP.
**If a slice goes red and you lack the budget to fix it: `git reset --hard` that slice and hand off — never
commit a red tree.**

## 🪜 THE LADDER (lowest-risk first; each slice independently builds GREEN + commits)

- [x] **GMR-0 — write THIS ladder + register in PLAN.** Add a PLAN.md row pointing here. (DONE this session.)

- [x] **GMR-1a — `runtime/interp/` → `runtime/builtins/` ✅ DONE (SCRIP `06091ca`).** `git mv` + literal
  `interp/`→`builtins/` in 18 sources + 10 Makefile lines; residual `runtime/interp` = 0. Gates byte-identical
  (SNOBOL4 m2 7/7, Icon m2 12/12, prove_lower2 67, concurrency OK, no_bb_bin_t 0). Recipe below for reference:
  Mechanics (same-depth → internal relatives safe):
  1. `git mv src/runtime/interp src/runtime/builtins`
  2. Rewrite the literal path `interp/`→`builtins/` in the 18 referencing source files (the trailing slash
     guarantees you hit ONLY the directory, never the driver `interp_*`/`interp.h` files):
     `grep -rl 'interp/' src --include=*.c --include=*.cpp --include=*.h | xargs sed -i 's|interp/|builtins/|g'`
     ⚠ VERIFY FIRST that every hit is a `runtime/interp/` path and not some unrelated `interp/` — at
     baseline the only directory named `…interp/` is `runtime/interp`, so this is clean; re-grep to confirm.
  3. Makefile: `sed -i 's|runtime/interp/|runtime/builtins/|g' Makefile` (7 lines: the src-list block ~143-147
     + the per-`.o` rules ~314-318; the `.o` names like `gen_runtime.o` stay).
  4. GATE. Commit `GMR-1a: runtime/interp → runtime/builtins (it is the builtin/resolver layer, not the interpreter)`.
  **STATUS: see watermark — this is the first executable step.**

- [x] **GMR-1b — `lower/bb_exec.{c,h}` → new top-level `interp/` ✅ DONE (SCRIP `7c87379`).** `src/interp/` is a
  SIBLING of `src/lower/` (same depth) so every `../`/`../../` relative include in `bb_exec.c` stayed valid;
  only the 3 `runtime/builtins/` referrers (`../../lower/bb_exec.h`→`../../interp/bb_exec.h`) + 2 Makefile
  paths changed; `-I$(SRC)/interp` added (forward-friendly). Gates byte-identical. Recipe below for reference:
  `mkdir src/interp; git mv src/lower/bb_exec.c src/lower/bb_exec.h src/interp/`.
  Add `-I$(SRC)/interp` to the 3 `-I` lines. Fix `bb_exec.{c,h}`'s own relative includes (depth changed
  lower→interp, same level, so `../ast/...`→still `../ast/...` OK; `IR.h` is bare via -I OK; check `#include
  "scrip_ir.h"`-style local ones). Update Makefile source-list + `.o` rule paths (`lower/bb_exec.c`→`interp/bb_exec.c`).
  Fix the ~6 `#include "bb_exec.h"` referrers if any used a relative `../lower/` form (most are bare). GATE.
  Commit `GMR-1b: bb_exec (mode-2 BB-graph interpreter) lower/ → interp/`.

- [ ] **GMR-2 — `contracts/` spine.** `mkdir src/contracts`. Move + add ONE `-I$(SRC)/contracts`:
  - `git mv src/include/descr.h src/contracts/descr.h`
  - `git mv src/include/ast.h src/contracts/ast.h` ; fold `src/ast/{ast_print.c,ast_verify.c}` →
    `src/contracts/` (these are the AST allocator/printer; `ast/ast.h` was a 1-line redirect — delete it).
  - `git mv src/include/IR.h src/contracts/ir.h` (keep guard `SCRIP_IR_H`); move `src/lower/scrip_ir.c`
    → `src/contracts/ir.c` (the IR allocator) + `src/lower/scrip_ir.h` redirect handled.
    ⚠ Decide basename: KEEP `IR.h` (just move it) to avoid touching ~80 `#include "IR.h"` sites — only ADD
    `-I$(SRC)/contracts` and `git mv` the file; do NOT rename to `ir.h` unless you also sed all includers.
    (Recommended: KEEP basenames, move files, add `-I`. Rename is a separate cosmetic rung if Lon wants it.)
  - `git mv src/include/stage2.h src/include/bb_program.h src/contracts/`
  - Remove `-I$(SRC)/include` ONLY after `include/` is empty (it still holds SM.h, XA.h, bb_box.h, emit_ir.h).
  GATE after each file-group. Commit `GMR-2: contracts/ spine (descr+ast+ir+stage2, types beside allocators)`.

- [ ] **GMR-3 — `machine/` substrate.** `mkdir src/machine`; `git mv src/processor/* src/machine/`
  (bb_pool.*, bb_boxes.c, bb_box.h, bb_build.h, smx_dead_stubs.c → but smx_dead_stubs goes to attic in GMR-5);
  `git mv src/lower/sm_prog.c src/machine/`. Swap `-I$(SRC)/processor`→`-I$(SRC)/machine`; fix Makefile
  source-list + `.o` rules. GATE. Commit `GMR-3: machine/ (RX slab + stage2 preamble)`.

- [ ] **GMR-4 — `parser/` (was `frontend/`).** `git mv src/frontend src/parser`. This is the biggest
  include churn: swap `-I$(SRC)/frontend/snobol4`→`-I$(SRC)/parser/snobol4` (+ raku), and rewrite every
  `frontend/`→`parser/` include + every Makefile `frontend/` path. Per-language subdirs keep their internal
  relatives (same depth). GATE (build the full parser set). Commit `GMR-4: frontend/ → parser/`.

- [ ] **GMR-5 — `attic/` (dead Stack Machine).** `mkdir src/attic`; `git mv src/include/SM.h
  src/driver/scrip_sm.c src/driver/scrip_sm.h src/machine/smx_dead_stubs.c src/attic/`.
  ⚠ `stage2.h` `#include "SM.h"` + uses `SM_op_t`/`bb_program_t`-via-SM — CONFIRM what stage2/bb_program
  actually still need from SM.h before moving; if they need the opcode enum, leave a minimal `sm_opcodes.h`
  in contracts/ and move only the dead `.c`. Add `-I$(SRC)/attic` if anything still includes SM.h. GATE.
  Commit `GMR-5: attic/ — quarantine dead Stack Machine`.

- [ ] **GMR-6 — `backends/` (non-x86, dormant).** `mkdir src/backends`; `git mv src/driver/{js,jvm,net,wasm}
  src/runtime/{js,jvm,net,wasm} src/backend src/backends/`. These are not in the live build (X86-ONLY), so
  the Makefile likely doesn't reference them — verify, then move. GATE (build unaffected). Commit
  `GMR-6: backends/ — consolidate dormant non-x86 trees`.

- [ ] **GMR-7 — `tools/` (harnesses).** `git mv src/lower/prove_lower2.c src/lower/tmatch_proto.c
  src/emitter/test_template_byte_identity.c src/emitter/demo_template_productions.c src/tools/`.
  ⚠ `prove_lower2.sh` compiles `prove_lower2.c` by path — update that script's path. (NOT the Makefile.)
  GATE (incl. prove_lower2.sh from its new path). Commit `GMR-7: tools/ — proof + scaffolding`.

- [ ] **GMR-8 — DE-POLLUTE the contracts.** Evict from `contracts/ir.h` the mode-2 execution-state structs
  (`bb_node_state_t`, `bb_arbno_state_t`, `bb_conj_state_t`, `bb_ite_state_t`, `bb_catch_state_t`,
  `bb_choice_state_t`, `bb_goal_state_t`, `bb_findall_state_t`, `bb_pat_kids_state_t`, `sno_prog_t`,
  `sno_stmt_t`, `RESOLVE_IDX_*`) into a new `interp/bb_exec_state.h` included by `bb_exec.c`. Evict the
  legacy `Σ/Δ/Ω/Σlen` C globals + `TEMPLATE_ADDR_*` from `emitter/emit_globals.h` (the REG ladder is
  deleting these anyway — coordinate, do not duplicate). Move the `rt_pl_*` declarations out of
  `interp/bb_exec.h` into `runtime/rt/rt.h` (or a `runtime/builtins/*.h`). GATE. Commit
  `GMR-8: de-pollute — interp state out of ir.h, legacy subject globals out of emit_globals.h`.

- [ ] **GMR-FENCE — verify + PLAN refresh.** `find src -maxdepth 1 -type d` shows exactly the target set;
  `grep -rn 'runtime/interp\|lower/bb_exec\|src/frontend\|src/processor' src Makefile scripts` == 0.
  Update PLAN.md's Architecture paragraph + Repos/clone notes to the new layout. Update GOAL-*-BB.md
  "Architecture references" path lists (bb_exec.c → interp/, etc.). GATE. Commit + push (code repos first,
  `.github` last) per RULES handoff sequence.

## ⚠ NOTES FOR WHOEVER CONTINUES
- The reorg changes NO logic — it is `git mv` + include-path + Makefile-path edits. If a behavioral gate
  moves, you broke an include or dropped a source-list line; revert the slice and diff.
- Prefer ADD-an-`-I` + move-the-file over renaming basenames (renaming a header forces touching every
  includer). Basename renames (`IR.h`→`ir.h`) are an OPTIONAL cosmetic rung, last, only if Lon asks.
- After the moves, the GOAL-*-BB.md "Architecture references" sections (bottom of each) point at OLD paths
  (`bb_exec.c`, `emit_bb.c`, `lower/lower.c`). GMR-FENCE refreshes them.

## Watermark
SCRIP `7c87379` (GMR-1a `06091ca` + GMR-1b `7c87379` landed; gates byte-identical to baseline `10fbe32`) · .github
this commit. **Next executable step: GMR-2 (contracts/ spine).** `src/` now: ast backend driver emitter frontend
include **interp** lower machine? processor runtime(+**builtins**) tools — `interp/` = real mode-2 interpreter,
`runtime/builtins/` = builtin/resolver layer. The two worst-named parts are fixed; the `include/` grab-bag (GMR-2)
and `frontend→parser` (GMR-4) are the next big findability wins.
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
