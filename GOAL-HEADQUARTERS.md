# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → write fresh SM/BB lowering, do not restore AST-walking call.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract. Never invoke language-A SM-bridge with language-B BB object.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL. Zero call sites depend on NULL α/β as sentinel.
5. **Three orthogonal constructs per session max**, separate commits, single gate run at end.
6. **Builder/consumer case rule.** UPPERCASE prefix builds IR (`SM_*`, `BB_*`). lowercase consumes it (`sm_*`, `bb_*`).
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary lives inside each `IS_<BE>` arm in the encoder layer below — never as a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode iteration calls `emit_mode_set(TEXT_MODE(), out)` at entry. Individual dispatchers stay idempotent.

## Session Setup

```
cd /home/claude/one4all && bash scripts/build_scrip.sh
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, single-structure via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) is the reference path for Icon at 194/265. Mode 4 (`--compile`) emits wired x86 — no `bb_broker`.

## Gates

```
GATE-1  bash scripts/test_smoke_icon.sh                        # PASS=5
GATE-2  bash scripts/test_smoke_unified_broker.sh              # PASS >= 23
GATE-3  bash scripts/test_icon_all_rungs.sh --interp           # PASS=194
```

## Watermark

```
one4all: b733dd13    (ST2-2 stage2 isolation firewall gate; ST2 rung COMPLETE — ST2-1/1b/1c/2 all landed this session)
corpus:  b10933c
.github: (this commit — ST2 rung close-out ledger)
--interp:      PASS (hello.sno, hello.icn)
smoke icon:    5/0    smoke prolog: 5/0    smoke rebus: 4/0
smoke raku:    5/0    smoke snobol4: 7/0    smoke snocone: 5/0
broker:        23/26
icon rungs:    194/36/35
matrix gate:   0/365 PASS
DAI-BOMB fires: 0
firewall lower:   9 includes / 6 allowlisted
firewall runtime: 16 includes / 8 allowlisted
firewall stage2:  10 allowlist entries (token gate; honest-scope: not link-time)
beauty.sno --compile md5: 40df9e004c3e963c99af716c65f2c970  (baseline 2026-05-20, 882901 bytes)
```

---

## Active rungs

### ISOLATION — parse->lower / parse->runtime boundary firewalls

**Goal:** lex/parse produces exactly `tree_t *` and nothing else.  Two boundaries to enforce: parse->lower (consumed by `lower()`) and parse->runtime (referenced by interpreters and emitters).  Today the boundaries are partially porous; ratchet shrinks the porosity.

- [x] **ISO-1** — `lower()` signature `lower(const tree_t *prog)`.  `ParserOutput` struct + `parser_output.{c,h}` deleted; sidecar build (`label_table_build`, `prescan_defines`, `polyglot_init`) folded into the top of `lower()`.  Callers (`scrip.c` `dump_sm`/`mode_monitor`, `scrip_sm.c` `sm_preamble`, `sync_monitor_run`) simplified.  `261ff13d`.
- [x] **ISO-2** — `scripts/test_gate_lower_isolation.sh`: header firewall enforcing no `#include` from `src/lower/` into `src/frontend/` except via allowlist.  Initial state: 10 includes / 7 allowlist entries, each entry documenting why it exists and an owning relocation goal.  `1691f44f`.
- [x] **ISO-3** — Relocate `icon_gen.h` (pure Icon Byrd-box generator runtime) from `src/frontend/icon/` to `src/runtime/interp/`.  Lower firewall: 10/7 → 9/6.  Add companion `scripts/test_gate_runtime_isolation.sh` (no `src/runtime/` include into `src/frontend/` except allowlist).  Initial state: 16 includes / 8 allowlist entries.  `cb1738f6`.
- [ ] **ISO-4 (NEXT)** — `scrip_parse` subprocess: break six parsers out into a separate executable.  `scrip_parse` reads stdin (source) and writes stdout (TDump/TLump S-expression, 120 max line length).  SCRIP forks/execs and reads back, then deserializes the S-exp into a `tree_t` to pass to `lower()`.  Hardest unsolved sub-question: TDump format (defined) but no C-side *deserializer* exists yet — that has to be written.  Other sub-question: where exactly the sidecar build runs after the split (in parent after deser, or replayed via S-exp on the wire).  Recommended first sub-step: write the deserializer + roundtrip self-test on existing programs.  Do NOT introduce the process boundary until roundtrip is proven.
- [ ] **ISO-5** — Shrink lower firewall allowlist toward 0:
  - `frontend/icon/icon_lex.h` — extract `IcnTkKind` enum to `src/include/icon_tk.h`.
  - `frontend/raku/raku_driver.h` — split into `raku_parse.h` (stays) + `raku_runtime.h` (move to `src/runtime/`).
  - `frontend/prolog/{term,prolog_runtime,prolog_atom}.h` — relocate to `src/runtime/interp/prolog/`.
  - `frontend/snobol4/scrip_cc.h` — rename + relocate to `src/include/scrip_lang.h` (54 includers tree-wide; mechanical move).
- [ ] **ISO-6** — Shrink runtime firewall allowlist toward 0: same headers; coordinated with ISO-5 since they overlap.
- [ ] **ISO-7** — Stronger guarantee than the header firewall: link-time isolation test (`lower.o` + `lower_*.o` linked against a tree with all `src/frontend/*.o` absent).  Any unresolved symbol = real leakage.  Deferred from this session — proxies (signature + firewall) are weaker than a real link test, and we should be honest about that until ISO-7 lands.

**Honest scope statement (recorded so the next session does not over-trust the gates):** the firewalls are *header* firewalls.  They catch direct `#include` regressions in seconds.  They do **not** prove that `lower` reads only the AST passed to it; symbols reachable through an allowlisted header (most acutely through `scrip_cc.h`) are not detected.  ISO-7 closes that gap.

### ST2 — Stage 2 handoff (lower → interp/emit) is a named struct, not a pile of globals

**Goal:** the output of lower() is one struct, `stage2_t`, containing the SM opcode array PLUS the category-B sidecars (label_table, proc_table, pl_pred_table, module_registry, lang) that interp/emit previously read from process globals.  The struct is the global value `g_stage2` — single, .bss-resident, no allocator dance, no pointer to track.  Mirror of ISO on the output side.

**Authorship history (ST2-1, this session, 2026-05-20):** Lon walked Claude through three honest pivots — first an additive `s2_*` fields kludge ("populate at end" — kludgy, retracted), then a `typedef stage2_t = SM_sequence_t` alias (two pointers to synchronize — retracted), finally the right shape: `SM_sequence_t` stays the pure opcode array as originally designed, `stage2_t` is its own struct that embeds the SM sequence and owns the sidecars, and `g_stage2` is a global value not a pointer.  RULES.md SR-15c lesson respected throughout — lower's internal pass state stays file-scope `static`; ST2 addresses output-side handoff only.

- [x] **ST2-1** — `stage2_t` is the baton; `g_stage2` is a global value.  `SM_sequence_t` restored to its sequence-only shape.  Six reader shim macros (label_table, proc_table, g_pl_pred_table, g_registry, label_count, proc_count) redirect legacy names into `g_stage2`.  `polyglot_init` takes a `stage2_t *s2` parameter (currently `(void)s2;` ignored — body writes via shim).  Canonical struct typedefs consolidated into `stage2.h`.  Renames: `ScripModule.proc_count` → `nprocs`; lower-internal `LabelEntry` → `LabTabEntry`.  `g_current_SM_seq` dissolved (40 sites).  All gates at baseline.  `871d2f0b`.
- [x] **ST2-1b ✅ COMPLETE** (2026-05-20) — All six reader shim macros burned down across four sub-steps.  Pattern: producers (s2-bearing) thread `s2->`; readers (deep dispatch, no s2) use `g_stage2.` literally; shim macros deleted after last reader migrates.
  - [x] **g_registry sub-step** (2026-05-20, `14655275`): swept 11 sites in `polyglot_init` to `s2->module_registry`; shim macro deleted from `interp.h`.  Single-file scope (only reader was `polyglot_init`).  Five shims remain.
  - [x] **label_table / label_count sub-step** (2026-05-20, `4f5d0512`): `label_table_build` threads `s2->label_table` / `s2->label_count`; `label_lookup` reads `g_stage2` literally (called from interp_call.c × 4 and interp_hooks.c × 2 — sites that don't carry `s2`; threading through them is a separate larger refactor).  Shim macros deleted from `interp.h`.  Four shims remain.
  - [x] **g_pl_pred_table sub-step** (2026-05-20, `d73cded0`): 17 sites across 5 files migrated.  polyglot.c (2) threads `s2->pl_pred_table`; pl_runtime.c (10), scrip_sm.c (1), interp_hooks.c (1), lower.c (1) read `g_stage2.pl_pred_table` literally.  Shim macro deleted from `pl_runtime.h`.  Three shims remain (proc_table/proc_count is the only remaining cluster).
  - [x] **proc_table / proc_count sub-step** (2026-05-20, this commit): 127 sites across 10 files migrated.  Producers (s2-bearing): polyglot.c (10 sites) threads `s2->proc_table` / `s2->proc_count`; scrip_sm.c sm_resolve_proc_entry_pcs signature changed from `(SM_sequence_t *p)` to `(stage2_t *s2)` and threads s2 (4 sites).  Readers (deep dispatch, no s2): lower.c (12 sites: emit_var_load × 2, lower_proc_skeletons × 10), sm_interp.c (21 sites), ir_exec.c (15 sites), emit_sm.c (10 sites), icn_runtime.c (32 sites), interp_hooks.c (2 sites: _usercall_hook), raku_builtins.c (3 sites: builtin call path) read `g_stage2.proc_table` / `g_stage2.proc_count` literally.  Both shim macros deleted from `icn_runtime.h`.  All gates at baseline (smoke 5/0×5+4/0+7/0; broker 23/26; icon-rungs 194/36/35; beauty.sno --compile md5 `40df9e004c3e963c99af716c65f2c970` byte-identical).
- [x] **ST2-1c ✅ COMPLETE** (2026-05-20, `b42b7979`) — `label_table` and `proc_table` in `stage2_t` converted from fixed-size inline arrays to dynamically-grown pointers + cap (mirror of `SM_sequence_t.instrs` `_grow` pattern).  `stage2_reset()` allocates the initial buffers at `STAGE2_LABEL_MAX` / `STAGE2_PROC_TABLE_MAX` (kept as initial-capacity hints, no longer hard limits).  `stage2_label_grow` / `stage2_proc_grow` helpers replace the writer-side cap checks at the two append sites (`polyglot.c` proc-table, `interp_label.c` label-table).  Reader sites unaffected — all use `[i]` indexing.  Net: ~150KB .bss freed; programs with >4096 labels or >256 procs no longer silently truncate.  All gates at baseline; beauty.sno --compile byte-identical.
- [x] **ST2-2 ✅ COMPLETE** (2026-05-20, `b733dd13`) — `scripts/test_gate_stage2_isolation.sh` written.  Token firewall: each of the six former ST2-1 shim-macro names (`g_registry`, `label_table`, `label_count`, `g_pl_pred_table`, `proc_table`, `proc_count`) must appear in source only as a qualified field reference (`.` or `->` prefix).  Allowlist of 10 entries covers `stage2.h` field declarations × 6, `interp_private.h` doc comment × 3, `scrip_sm.c` printf format string × 1.  Mirror of `test_gate_lower_isolation.sh` / `test_gate_runtime_isolation.sh` (same `ALLOW` array + grep style).  Honest scope statement in header records that it's a token firewall — link-time isolation analogous to ISO-7 remains a future rung.

**ST2 rung COMPLETE** (2026-05-20): ST2-1 / ST2-1b / ST2-1c / ST2-2 all landed.  `stage2_t` is the single named struct lower() hands to interp/emit, with no global shim macros, dynamically-grown sidecars, and a regression-catching firewall gate.

**Authors recorded per RULES.md "Three-construct" exception (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.

### IR-CONSOLIDATE-DCG — single-structure lowering output

**Goal:** all BB graphs produced by lowering reach engines via the single `SM_sequence_t`. Carve-out: mode-4 standalone binaries keep `ir_body` fallback (no `SM_sequence_t` at runtime; `pl_dcg_register` wires predicates at standalone startup).

- [x] IR-CD-1/2/3 — `bb_idx` field + populate + strangler helpers. `419fce29`.
- [x] IR-CD-RENAME — Category A rename across 15 files. `a97be4b0`. Category B (true Prolog DCG grammar) and C (`icn_bb_dcg`, `pl_bb_dcg`, `lower_pat_dcg.*`, `*_dcg_state_t`) deferred.
- [x] IR-CD-4 — 19 consumer read sites migrated to `bb_graph_of_*(entry)` across 5 files. `b97b267b`.
- [x] IR-CD-5 — Deleted `ir_body` field from `IcnProcEntry` and `Pl_PredEntry_BB`. Mode-4 standalone (Option A): `rt_pl_b_end_register` calls `SM_seq_bb_add(&g_stage2.sm, cfg)`; `SM_seq_bb_add` lazy-allocates `bb_table` when `bb_cap == 0`. `pl_bb_register` signature changed to `(name, arity, int bb_idx)`. Strangler helpers simplified to single-structure lookup. `489ff5b3`.
- [x] IR-CD-6 — `ARCH-IR.md` updated with IR-CONSOLIDATE-DCG invariant section and post-IR-CD file map.  PLAN watermark updated below.
- [x] IR-CD-7 — Close-out: full gate floor run.  Smoke 5/5/7/5/4/5 FAIL=0 each; unified_broker 23/26; test_icon_all_rungs 194/36/35; beauty md5 `40df9e004c3e963c99af716c65f2c970` unchanged.  Rung complete 2026-05-20.

### IR Rename — builder/consumer case scheme

**Rule:** UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`). lowercase consumes (`sm_interp_*`, `bb_print`, `bb_broker`, all `SM_templates/` dispatchers). Case at the call site tells you which side of the pipeline you're on.

- [x] IR-RN-0 — Bulk rename in 3 sed passes. 48 files. Headers `IR.h`→`BB.h`, `sm_prog.h`→`SM.h`. `9ce69899`.
- [x] IR-RN-1 — Audit `lower.c` post-rename. `c710506f`. Single finding: `sm_pat_capture_fn_arg_names` (builder helper, lowercase by mistake from IR-RN-0 Phase 3 sm_pat_* lowercase sweep) → `SM_pat_capture_fn_arg_names`. File-local, 2 sites. Sibling `lower_*.c` files clean.
- [x] IR-RN-2 — Audit emitters (`emit_bb.c`, `emit_sm.c`, `emit_core.c`). `92417a85`. Single cluster: 4 stale `ir_*` consumers (`ir_node_id`, `ir_is_generator`, `ir_walk`, `ir_walk_rec`) → `bb_*` (consume `BB_t`/`BB_graph_t`/`BB_op_t`). 18 files, 32 call sites + 1 header (`src/include/emit_ir.h`) + 4 defs. emit_bb.c and emit_sm.c clean. Apparent builder calls in emit_sm.c (BB_alloc/BB_node_alloc/BB_free, SM_seq_free) are legitimate pattern-window IR construction + destructors.
- [x] IR-RN-3 — Audit runtime (`sm_interp.c`, `sm_jit_interp.c`, `ir_exec.c`).  Two findings: `SM_label_pc_lookup` → `sm_label_pc_lookup` (read-only PC lookup; consumer disguised as builder by UPPERCASE; 13 call sites across 4 files + def in `sm_prog.c` + decl in `SM.h`) and `BB_reset` → `bb_reset` (per-node state reset; consumer-side runtime reset; 5 call sites in `ir_exec.c` + def in `scrip_ir.c` + decl in `BB.h`).  `SM_codegen` audited and kept UPPERCASE (codegen entry point, named-pipeline infrastructure; renaming would ripple beyond rung scope).  `4a1fcc63`.
- [ ] **IR-RN-4 (NEXT)** — Update arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`).
- [ ] IR-RN-5 — Full cross-language gate run; close rung.

Reserved (untouched): `IR_LANG_*`, `SM_INTERP_*`, `SM_CALL_STACK_MAX`/`SM_GEN_LOCAL_MAX`/`SM_MAX_OPERANDS`, `BB_POOL_SIZE`, header guards, `SM_*` opcode tags, `SM_templates/`/`BB_templates/` dir names.

### EC-UNI — x86 text/binary into SM_templates; unify all walkers

**Target:** one fn per SM opcode, one fn per BB kind; each carries one arm per backend (5 cols: X86/JVM/JS/NET/WASM). Text-vs-binary hides inside the encoder below the dispatcher. `emit_walk_codegen`, `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm` all delete.

Completed: EC-UNI-0 through EC-UNI-9d. 52 SM_template fns across 5 files carry `IS_X86` arms, reachable via `SCRIP_UNIFIED_DISPATCH=1`. Matrix gate passes 0/365. Commits: `f29c95e9`/`e2491770`/`fc9d0122`/`609dac51`/`bfa65968`/`b1711529`/`42908963`/`63708215`/`7d792c59`/`073f3711`/`8308a457`.

- [ ] **EC-UNI-3-beauty (NEXT)** — Close the rung with byte-identity gate on beauty.sno. WIP from last session reverted at handoff; ~60% done, ~1h to reproduce.

  Plan:
  1. Extend `sm_ctx_t` (in `src/emitter/SM_templates/sm_ctx.h`) with `const struct SM_sequence_t *prog;` and `const void *srclines;`.
  2. Add `#include "SM_templates/sm_ctx.h"` to `emit_sm.h`.
  3. Change signatures: `emit_sm_return_template(out, ins, ctx)`, `emit_sm_stno_template(out, ins, ctx)`. Pass `ctx->i` as pc, `(SM_sequence_t*)ctx->prog`, `(SrcLines*)ctx->srclines`.
  4. Promote `sm_stno` template to take `const sm_ctx_t *ctx` (mirrors `sm_jump`/`sm_halt`/`sm_return`).
  5. Update `dispatch_one_x86` signature to receive `prog` and `sl` from `emit_walk_codegen`. Fill `ctx.prog = prog; ctx.srclines = sl_loaded ? &sl : NULL;`.
  6. Build, gate, write `scripts/test_gate_em_ec_uni_3_beauty.sh`: compile `beauty.sno --compile` flag-off and flag-on, `diff -q` identical.

  Real divergences fixed by this (not "GAS-comments only" as previously assumed):
  - `SM_NRETURN[_S/_F]`: flag-off emits `NRETURN_VAR fname_lbl, cond, pc`; flag-on emits `RETURN_VARIANT 2, cond, 0` — different GAS macro, because shim's `prog=NULL` skips the `kind==2 && prog` branch.
  - `SM_FRETURN[_S/_F]`, `SM_RETURN_[S/F]`: third operand (`pc`) is a real macro arg, not annotational. Differs.
  - `SM_STNO`: comment annotation drift only.

  Affected files (uncommitted WIP, reverted): `src/emitter/SM_templates/sm_ctx.h`, `src/emitter/SM_templates/sm_returns.c`, `src/emitter/SM_templates/sm_templates.h`, `src/emitter/emit_sm.c`, `src/emitter/emit_sm.h`.

- [ ] EC-UNI-4 — Delete `emit_walk_codegen` / `sm_codegen_text` / `emit_sm_template` / `sm_op_template_t` table from `emit_sm.c`. `scrip.c` x86 compile path calls `emit_program(ast, out, EMIT_TEXT)`. Beauty.sno byte-identical vs SPITBOL oracle. Est −1500 LOC.
- [ ] EC-UNI-5 — Wire JVM/JS/NET inline switch arms in `emit_core.c` to call SM_template fns. Delete the three inline switch bodies. `emit_sm_dispatch` handles all 5 backends.
- [ ] EC-UNI-6 — x86 binary arms: `IS_X86` (binary path) stubs through `emit_sm_dispatch(EMIT_BINARY_WIRED)`. Byte-identity vs `--run`.
- [ ] EC-UNI-7 — Audit + close: strip remaining silo logic; full gate run; update ARCH-IR.md.
- [ ] EC-UNI-8.4-fix — Collapse 4 Category-A silo walkers (`emit_jvm_one_instr`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm`) into single `emit_sm_dispatch`. Findings in `EC-UNI-8.4-SILO-AUDIT.md`. Prereq: EC-UNI-3-beauty + EC-UNI-4.
- [ ] EC-UNI-8.5 — Add-a-backend test: `EMIT_NULL=99` + `IS_NULL` arms via mechanical patch. Prove "add backend = N template edits + 1 header". Revert.
- [ ] EC-UNI-8.6 — Add-an-opcode test: `SM_NOP` + `SM_templates/sm_nop.c`. Prove "add opcode = 1 new template file + 1 enum value". Revert.
- [ ] EC-UNI-8.7 — Docs + close: ARCH-IR.md, ARCH-SCRIP.md, this file's invariant block.

**Invariant (post EC-UNI):** one SM walk fn (`emit_sm_dispatch`). Every SM opcode = one template fn. Every backend adds exactly one arm per fn. Adding a backend = N template edits + 1 header enum + 1 macro. Adding an opcode = 1 new file + 1 enum value. Adding a new output format to an existing backend = encoder-layer change only, zero template edits.

### EC-PHASE-A — emitter refactor to 100% template coverage of currently-emitted ops

**Goal:** every opcode currently emitted by any of the five backend walkers (x86, JVM, JS, NET, WASM) is emitted *only* through its template function.  After Phase A: zero ad-hoc switches outside `emit_sm_dispatch` and `emit_bb_node`; the five walker fns are deleted; every backend arm lives explicitly inside its template, side-by-side with the others.  No new codegen.  Behavior-preserving.

**Phase A scope (measured 2026-05-20):**
- SM: 76 opcodes touched by at least one walker.  56 templates exist → **20 to add** (many are *_S/*_F variants foldable into kind-arg fns; ~10 truly new fns).
- BB: 21 opcodes touched.  16 templates exist (PAT_* via one-file-per-op) → **4 new templates** (BB_PL_ARITH/ATOM/BUILTIN/CALL absorbing ad-hoc arms in `emit_sm.c`) + reorg of 16 single-file PAT templates into one `bb_pat.c`.
- Walkers to delete after coverage lands: `emit_walk_codegen` (x86 legacy switch), `emit_jvm_one_instr` + `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm`, `dispatch_one_x86`.

**Phase A then unlocks Phase B:** five per-backend GOAL files (one per column) — GOAL-SN4-X86-EMIT (new), GOAL-SN4-JVM-EMIT, GOAL-SN4-JS-EMIT, GOAL-SN4-NET-EMIT, GOAL-SN4-WASM-EMIT.  Each fills the IS_<BE> arms across the full opcode set, including ops nobody emits today (BB_AUGOP, BB_GOTO, BB_UNOP, BB_PROC, BB_SCAN, BB_INTERROGATE, BB_PAT_CALLOUT, BB_ICN_EVERY).

**Design decisions taken up front (so they're not re-litigated step by step):**

1. **Context via globals, not threaded parameters.**  Snocone is the bootstrap target.  Threading a `ctx` struct through every template fn parameter in C means threading it through every Snocone fn parameter once translated — pure overhead that the bootstrap doesn't earn.  Snocone has globals; the emitter system uses them.  Each backend's per-instruction loop sets file-scope globals (`g_emit_pc`, `g_emit_n_total`, `g_jvm_in_body`, `g_jvm_in_my_method`, `g_jvm_fn_names`, `g_jvm_fn_count`, `g_net_pc_to_fn`, `g_net_fn_names`, `g_net_fn_count`, `g_emit_prog`, `g_emit_srclines`) before invoking the template; each template arm reads only the globals it cares about.  Eliminates the `const sm_ctx_t *ctx` parameter from every template signature.  The existing `sm_ctx_t` struct is removed; the field names live on as global names.

2. **Globals are still structured names that survive the Snocone port.**  Groups of related globals are documented as logical structs in `src/emitter/emit_globals.h`, with a comment block declaring the eventual Snocone shape `DATA('Sm_ctx_jvm(IN_BODY, IN_MY_METHOD, FN_NAMES, FN_COUNT)')` etc.  When the Snocone bootstrap runs, the C globals become Snocone globals one-to-one; the struct grouping translates to a single `DATA(...)` declaration that the Snocone code shapes around.  The grouping is for human reasoning; it has no C-level enforcement.

3. **File grouping.**  SM templates stay grouped by family (10 files today, expanding to ~12).  BB templates collapse from 16 single-file PAT templates into family files: `bb_pat.c` (17 fns), `bb_pl.c` (10 fns when Phase B fills them — Phase A populates 4), `bb_icn.c` (22 fns, mostly Phase B), `bb_core.c` (the 35 universal kinds — lit/var/assign/call/if/seq/every/while/…, mostly Phase B), `bb_cset.c` (4 cset fns).  `bb_templates.h` holds all forward decls.  Phase A creates `bb_pat.c` (consolidating the 16 existing files) and `bb_pl.c` (the 4 new fns); the remaining BB family files are Phase B work.

4. **`emit_sm_dispatch` is the only SM walker.**  Built fresh in `emit_core.c`.  Single switch, 91 arms.  All five backend silo walkers delete; `emit_program`'s SM walk becomes one loop that sets the per-iteration globals (PC, instruction index, etc.) then calls `emit_sm_dispatch(ins, out)`.

5. **`emit_bb_node` is the only BB walker.**  Already exists, expand to all 21 Phase A arms (later 98 in Phase B).

6. **Verbatim move, no behavior change.**  Every Phase A step preserves byte-identical beauty.sno and the full smoke matrix.  No optimization, no cleanup, no "while we're here" — those are Phase B.

7. **Emit-to-strings comes right after Phase A.**  Today every template arm calls `fprintf(out, ...)` directly.  EC-PA-8 redirects all template emission through two emit primitives — `emit_text(const char *)` for text backends (x86 GAS, JVM jasmin, JS, .NET ilasm, WASM wat) and `emit_byte(unsigned char)` / `emit_bytes(const unsigned char *, int len)` for binary x86 — both accumulating into per-backend buffers.  Buffer-to-FILE flush happens at the end of each `emit_program` call (or at SM/BB boundaries if memory pressure dictates).  This makes the templates a pure source-to-bytes function with no I/O side effects, which is what the Snocone bootstrap needs.

**Rungs (orthogonal, separate commits per RULES.md "Three-construct"):**

- [ ] **EC-PA-1 (NEXT)** — globals-based ctx.  Create `src/emitter/emit_globals.{c,h}` with the documented global set and the `DATA(...)` shape comments.  Delete `src/emitter/SM_templates/sm_ctx.h` (the struct, not the file — replace contents with a fwd-include of `emit_globals.h` for transition, or delete and update includers).  Drop the `const sm_ctx_t *ctx` parameter from every template fn that takes it today (`sm_jump`, `sm_jump_s`, `sm_jump_f`, `sm_halt`, `sm_return`, `sm_freturn`, `sm_nreturn`).  Each template arm reads `g_emit_pc`, `g_emit_n_total`, etc., directly.  Producer sites (four silo walkers in `emit_core.c` + `dispatch_one_x86` in `emit_sm.c`) set the globals before each template call.  Gates: full smoke + broker + beauty byte-identical.

- [ ] **EC-PA-2** — BB template file reorg.  Create `BB_templates/bb_pat.c` consolidating the 17 PAT fns (16 existing + new `bb_pat_callout` stub).  Delete the 16 single-file PAT templates.  Update `bb_templates.h` (no API change — same fn names).  `Makefile` glob already picks up `BB_templates/*.c`.  Gates: same.

- [ ] **EC-PA-3** — BB Prolog templates.  Create `BB_templates/bb_pl.c` with `bb_pl_arith`, `bb_pl_atom`, `bb_pl_builtin`, `bb_pl_call` — bodies moved verbatim from the four `case BB_PL_*:` arms in `emit_sm.c`.  Add to `bb_templates.h`.  Expand `emit_bb_node` switch.  Delete the arms from `emit_sm.c`.  Gates: same.

- [ ] **EC-PA-4** — Missing SM templates.  Add the ~10 new fns into existing family files (no new files unless natural): `sm_call_fn`/`sm_call_expression` → new `sm_calls.c`; `sm_incr`/`sm_decr` → `sm_arith.c`; `sm_define`/`sm_define_entry` → new `sm_defines.c`; `sm_push_expr`/`sm_push_expression`/`sm_push_null_noflip`/`sm_push_lit_cs`/`sm_label` → `sm_push_pop_lits.c`; `sm_suspend_value` → `sm_returns.c` or new `sm_suspend.c`; `sm_bb_once_proc`/`sm_bb_pump_proc` → new `sm_bb_calls.c`.  Variants `*_S/*_F` etc. fold into base fns via instruction-opcode discrimination (existing pattern in `sm_returns.c`).  Bodies copied verbatim from the union of all five walker arms — each new fn carries all five IS_<BE> arms it needs.  Gates: same.

- [ ] **EC-PA-5** — Build `emit_sm_dispatch` for real.  Single function in `emit_core.c`, 91-arm switch, each arm calls `sm_<name>(ins, out)` (no ctx param — globals carry context).  Caller in `emit_program` (or its delegates) sets the per-iteration globals (PC, N, opcode, etc.) for the active mode, then calls `emit_sm_dispatch(ins, out)`.  At this step, the five silo walkers still exist but are no longer called.  Gates: same — flip via `SCRIP_UNIFIED_DISPATCH=1` for one full gate run; default still off.

- [ ] **EC-PA-6** — Delete the silo walkers.  Remove `emit_walk_codegen`, `emit_jvm_one_instr`, `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm`, `dispatch_one_x86`, plus the per-op `emit_sm_*_dispatch` helpers in `emit_sm.c` that the legacy switch routes through (~30 helpers).  Switch `g_emit_use_unified_dispatch` to always-on, then delete the flag.  Caller in `emit_program` now unconditionally goes through `emit_sm_dispatch`.  Net LOC: estimated −2500 to −3500.  Gates: full smoke + broker + beauty byte-identical.

- [ ] **EC-PA-7** — Templates emit through `emit_text` / `emit_byte`, not `fprintf`.  Add `src/emitter/emit_io.{c,h}` with the four primitives: `emit_text(const char *)`, `emit_textf(const char *fmt, ...)` (sprintf wrapper for the existing fprintf-style call sites), `emit_byte(unsigned char)`, `emit_bytes(const unsigned char *, int len)`.  Internally each writes to a per-backend buffer (`g_text_buf`, `g_bin_buf`).  Sweep every template fn body: replace `fprintf(out, fmt, …)` → `emit_textf(fmt, …)`; replace any direct `fputc`/`fwrite` in binary x86 arms → `emit_byte`/`emit_bytes`.  Drop the `FILE *out` parameter from every template signature (after the sweep — `emit_io` flushes the buffer to whatever FILE* the caller wants at the end of `emit_program`).  This is the largest mechanical sweep of Phase A; do it as its own three-commit batch (text sweep / binary sweep / signature change).  Gates: same — beauty.sno byte-identical, all smoke green.

- [ ] **EC-PA-8** — Phase B handoff.  Create `GOAL-SN4-X86-EMIT.md` and update the four existing per-backend GOAL files to point at the now-stable template ABI (no `ctx`, no `FILE *out`, just globals + `emit_text`/`emit_byte`).  ARCH-SCRIP.md + ARCH-IR.md updated to reflect single-dispatcher + emit-primitive reality.  Mark EC-UNI rung complete; EC-PHASE-A rung complete; Phase B rungs become active.

**Phase A gate (must pass at every step):**

```
GATE-A1  beauty.sno --compile  →  md5 40df9e004c3e963c99af716c65f2c970  (882901 bytes; current baseline 2026-05-20; the M1 oracle md5 abfd19a7a834484a96e824851caee159 from 2026-04-28 has since drifted but the watermark below tracks current)
GATE-A2  bash scripts/test_smoke_icon.sh                                  # PASS=5
GATE-A3  bash scripts/test_smoke_unified_broker.sh                        # PASS=23 (current; rung tracks regression only)
GATE-A4  bash scripts/test_icon_all_rungs.sh --interp                     # PASS=194 (per HQ watermark)
GATE-A5  bash scripts/test_smoke_{snobol4,snocone,prolog,rebus,raku}.sh   # 7/0 5/0 5/0 4/0 5/0
```

**Why this is worth doing before Phase B:** the five existing per-backend GOAL files (JS/JVM/NET/WASM) all describe "fix backend X" work, but today there's no clean place to put that fix — it has to thread through a silo walker, ad-hoc dispatchers, and partial template arms.  After Phase A, "fix backend X for opcode Y" is literally "open `sm_<y>.c`, find the IS_X arm, edit it."  Single file, single fn, side-by-side with the four other backends' working code.

**Authors recorded per RULES.md "Three-construct" exception (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.

---

## Completed ledgers (audit trail)

### IJ-* / DAI-1..7 / IJ-HELLO matrix
All ✅. 6/6 wired hello-world matrix closed 2026-05-18.

**Key established facts:**
- Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265. Mode-1 flag deleted.
- Icon AST walker fully amputated (`bb_eval_value`/`bb_exec_stmt`/`icn_bb_build` gone).
- `rt_bb_once_proc` deleted; `rt_bb_pump_proc` never existed. Bridge shims = `rt_pl_once` + `icn_bb_dcg`.

### DAI-8 dead-code sweep — COMPLETE
All auditable dead code removed across C1–C17. Remaining dead-looking symbols are anchored live (Method 7 chains, @PLT references from emitter text).

| Cluster | What | Commit | LOC |
|---|---|---|---|
| C1 emit_bb.c | 75 fns + 22 decls | `a4fe1c21` | — |
| C2 emit_core+emit_sm byte-emit | ~198 fns | `895ab323` | −877 |
| C3a emit_form.h + ef_greek_port | 14 fns | `c3af9e23` | −23 |
| C3b rt.c | 7 fns + 7 decls | `a7259b9b` | −43 |
| C4 stmt_exec.c | 10 fns + typedef | `de6e7b77` | −248 |
| C5 snobol4_pattern.c | 16 fns + typedef + 9 decls | `af744aaa` | −197 |
| C6 prolog_builtin.c | 15 fns + 14 decls | `607b6aac` | −75 |
| C7 icon_runtime.c (frontend) | 12 fns + 2 globals | `2b7081c5` | −118 |
| C8 icn_runtime.c (interp) | 17 fns + state structs | `881d1a60` | −185 |
| C9 rt.c rt_pop_int | 1 fn | `ff9ee063` | −12 |
| C10 emit_wasm.c | 22 fns | `533c17c3` | −175 |
| C11 lower_icn.c | 9 fns | `04679f20` | −136 |
| C12 bb_boxes+emit_sm+scan_builtins | 20 fns | `5e854341` | −157 |
| C13 prolog_* + raku_re.c | 18 fns | `947ecd7a` | −234 |
| C14 icon_runtime+sm_interp+sm_jit_interp+stmt_exec | 20 fns | `50e025f6` | −168 |
| C15 bb_pool+lower+polyglot+snocone_lex | 10 fns | `06ea32b0` | −75 |
| C16 sm_interp.c every_table_lookup | binary-safe | `f82a34c9` | −324b |
| C17 snobol4_stmt_rt.c | 43 fns (whole file) | `d48681fb` | −447 |

**DAI-8 methodology** (kept for future audits):
- Method 1: `-ffunction-sections -fdata-sections` + `--gc-sections --print-gc-sections`, grep `.text.<name>` discards. Filter generated files + @PLT regex `"NAME(@PLT)?"`.
- Method 6: `grep -rn "\bNAME\b" src/` excluding own file. Zero hits + zero `&NAME` = safe.
- Method 7: linker-GC-dead public fn calling only other GC-dead fns → whole sub-graph deletes together.

### EC (emitter consolidation)
- [x] EC-0/1/2/2b/2c/3/4/5/6/7/WASM-SM — all ✅. Three silo files (emit_jvm.c, emit_js.c, emit_net.c) + emit_ir.c + emit_ir_targets.c deleted. Unified `emit_program(ast_prog, out, mode)`. IR walk + 3 SM-walk loops in `emit_core.c`. Net −2077 LOC at EC-5; further −427 at EC-6. ARCH-IR.md updated. Final commits: `8890d685` (EC-4), `e1c8a4ac` (EC-5), `7c33121c` (EC-6), `268619c1` (EC-WASM-SM).

### EC-UNI (template unification)
- [x] EC-UNI-0 through 9d — all ✅. Commits listed above. Axis correction (false 10-cell text/binary axis collapsed to 5-cell backend matrix) ratified in `63708215`/`7d792c59`/`073f3711`/`8308a457`. Matrix gate passes 0/365.

### IR-RN-0
- [x] Bulk rename in 3 sed passes. Builder/consumer case rule established. `9ce69899`.

### IR-CONSOLIDATE-DCG 1–4
- [x] IR-CD-1/2/3 (`419fce29`), IR-CD-RENAME (`a97be4b0`), IR-CD-4 (`b97b267b`). Side-finding `pl_broker.c:364` stale extern fixed in `a97be4b0`.

