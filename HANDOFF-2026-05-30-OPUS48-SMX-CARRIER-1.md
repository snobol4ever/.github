# HANDOFF-2026-05-30-OPUS48-SMX-CARRIER-1

**Session:** Opus 4.8, 2026-05-30
**one4all HEAD:** `e06b5201`  (== origin/main)
**.github HEAD:** `857061dc` (== origin/main)
**Goal:** GOAL-ICON-BB (SMX track) — prerequisite for the new "delete SM entirely + SNOBOL4→BB directed graph" directive.

---

## Lon's directive this session (supersedes old SMX-5)

1. New code base posture: SNOBOL4 is NOT 100% BB yet; there is to be **no Stack Machine and no value stack**.
2. **Literally delete all `SM_t` and `SM_sequence_t` references.** Any code that traverses an SM gets deleted. KEEP the low-level reusable functions (emit_core byte/label/patch primitives; `rt_*` runtime helpers).
3. SNOBOL4 lowers AST → a **directed graph of `BB_t`** (linked four-port boxes), like `lower_icn.c` — NOT a flat SM array. Four-attribute AG: α/β inherited (fresh-entry/retry), γ/ω synthesized (success/failure). Each BB is pure and frozen once correct.
4. **Ensure Icon does not break** — it runs concurrently, building BBs.
5. First program target: **`OUTPUT = "hello world"`** on the pure-BB path.

This SUPERSEDES the prior SMX-5 plan ("slim SM_sequence_t but keep bb_table inside it"). The new plan moves the BB-graph table OUT of SM_sequence_t so SM_sequence_t can be deleted whole.

---

## What was done — SMX-CARRIER-1 ✅ (one4all `e06b5201`)

The **keystone decoupling**: the BB-graph table is now a standalone carrier, fully independent of `SM_sequence_t`. This is what makes the SM deletion safe; it is NOT the deletion itself.

Key fact that makes it transparent: **`lower_icn.c` emits ZERO SM** (`grep -c SM_emit` = 0). Icon only ever used `SM_sequence_t` as a *bag* holding its `BB_graph_t*` graphs (`bb_table/bb_count/bb_cap`), appended via `SM_seq_bb_add`. So lifting that triple out changes nothing for Icon.

Changes (11 files, +102/−64, net +38):
- **`src/include/bb_program.h` (NEW):** `bb_program_t { BB_graph_t **table; int count, cap; }` + `bb_program_add` / `bb_program_free`.
- **`src/lower/scrip_ir.c`:** implement `bb_program_add`/`bb_program_free` next to `BB_alloc`/`BB_free`; `#include "bb_program.h"`.
- **`src/include/stage2.h`:** `stage2_t` gains `bb_program_t bbp` (the live carrier). The old `SM_sequence_t sm` field is **kept TEMPORARILY** — the not-yet-deleted SM codegen/interp still read `s2->sm`. It dies in SMX-4.
- **`src/lower/sm_prog.c` `stage2_reset`:** `bb_program_free(&g_stage2.bbp)` each pass.
- **`src/lower/lower.c`:** all 16 `SM_seq_bb_add(g_p, …)` → `bb_program_add(&g_stage2.bbp, …)`.
- **`src/driver/scrip.c` / `scrip_sm.c`:** every `sm->bb_table`/`sm->bb_count` reader → `s2->bbp.table`/`.count`; dropped the now-unused `SM_sequence_t *sm` decls in the interp/run/dump-bb paths; `stage2_free_sm_bb`/`stage2_free_bb_after_emit` now call `bb_program_free`.
- **`icn_runtime.h` / `pl_runtime.h`:** `bb_graph_of_proc`/`bb_graph_of_pred` shims → `bbp`.
- **`sm_bb_invoke.cpp` / `sm_interp.c`** (SM corpses, still compiled): `bb_table` reads → `bbp`, purely so the build stays green until those files are deleted.

### Gates (all verified)
- scrip + `libscrip_rt.so` build clean.
- **Icon smoke m2 6/6 (HARD GATE), m3 1/6 — IDENTICAL to pre-change.**
- SNOBOL4 `--interp`/`--run` still detonate via `[SMX] FATAL` (by design; no silent fallback).
- FACT 0, no-stack ratchet 129, SM-death ratchet 11 — all unmoved.

---

## NEXT — pick up here

Two tracks, both teed up; recommend doing SMX-4 deletion first (removes temptation), then SNOBOL4 hello-world.

### Track A — SMX-4: delete SM entirely (the directive's "first order of business")
Order, building-green + Icon-6/6 after each cut:
1. Delete the **~589 `SM_emit*` sites in `lower.c`** (non-Icon SM lowering; already dead at runtime via SMX-1). These live in `lower_stmt`/expr handlers gated by `g_lang != LANG_ICN`. Icon's path is `lower_icn_proc_body` (separate, SM-free) — do not touch it.
2. Delete SM machinery files: `src/processor/sm_interp.c`, `sm_native.c`, `sm_codegen.c`, `sm_image.c`; `src/emitter/emit_sm.c`; `src/emitter/SM_templates/*`. Remove their Makefile/`build_scrip.sh`/`libscrip_rt` source-list entries.
3. Delete the `SM_t` and `SM_sequence_t` struct defs in `src/include/SM.h` and the `sm` field in `stage2_t`. Also `sm_prog.c` SM-array parts (`SM_emit`, `SM_seq_*`, `sm_seq_init/deinit`) — keep `stage2_*` helpers.
4. Driver: the `mode_compile` (x86) branch uses `sm_codegen_text(&s2->sm, …)` — that whole mode-4 SM path goes; the `dump_sm` path goes. Keep `mode_interp`/`mode_run` Icon BB branches.
5. KEEP per Lon: `emit_core.{c,h}` byte/label/patch primitives, `rt_*` runtime helpers, `bb_*` everything.
6. Death ratchet `scripts/test_gate_sm_dead.sh` should fall toward 0; lower its MAX as references vanish.

WATCH: some BB templates (`bb_to_by.cpp`, `bb_suspend.cpp`, `bb_iterate.cpp`, `emit_bb.c`) and `interp_hooks.c`, `rt.c`, `eval_code.c`, `icn_runtime.c` still `#include "sm_interp.h"` or reference `sm_interp_run` — audit each: most are dead refs that delete cleanly, but confirm none are on the live Icon `bb_exec_once` path before removing.

### Track B — SNOBOL4 → BB directed graph: `OUTPUT = "hello world"`
- Lower the single statement to one `BB_ASSIGN` node: target = global var `OUTPUT`, value source = a `BB_LIT_S "hello world"` node (use the AG operand-aux sidecar, PEERS RULE — no operand pointers on BB_t). Build a `BB_graph_t` (lang `BB_LANG_SNO`), register it as `main` in `proc_table` with its `bb_idx` from `bb_program_add`.
- Route the SNOBOL4 case in `scrip.c` `mode_interp` through `bb_exec_once(s2->bbp.table[main_bb_idx])` exactly like the Icon branch (generalize the `is_icon` gate to "has a main BB graph", or add an `is_snobol4` sibling branch).
- `bb_exec.c`: confirm/extend `case BB_ASSIGN` + `case BB_LIT_S` for the SNOBOL4 lang so the assign reads the literal's value and `NV_SET_fn`s OUTPUT. SNOBOL4 `OUTPUT` is the predefined stdout-wired variable: assignment writes value + newline (SPITBOL manual, confirmed). Verify the OUTPUT-association print path fires (`rt`/`snobol4.c` already has the OUTPUT comm-var hook).
- Four-port AG: assign box α does store+print, exits γ; ω unused for a total expression.
- Gate: `echo 'OUTPUT = "hello world"\nEND' | ./scrip --interp f.sno` ⇒ `hello world\n`. Keep Icon 6/6.

---

## Session setup for next time
```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all  /home/claude/one4all
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
git clone https://TOKEN@github.com/snobol4ever/x64      /home/claude/x64
cd /home/claude/one4all && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_icon.sh            # MUST be m2 6/6 (HARD); m3 1/6
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
