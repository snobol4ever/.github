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
one4all: cb1738f6     (PARSE-TO-LOWER A/B/C — parse->lower carries only tree_t*; firewall gates land)
corpus:  b10933c
.github: (this commit — watermark advanced; new ISOLATION rung recorded below)
--interp:      PASS (hello.sno)
smoke icon:    5/0    smoke prolog: 5/0    smoke rebus: 4/0
smoke raku:    5/0    smoke snobol4: 7/0    smoke snocone: 5/0
broker:        23/26
icon rungs:    194/36/35
matrix gate:   0/365 PASS
DAI-BOMB fires: 0
firewall lower:   9 includes / 6 allowlisted
firewall runtime: 16 includes / 8 allowlisted
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

### IR-CONSOLIDATE-DCG — single-structure lowering output

**Goal:** all BB graphs produced by lowering reach engines via the single `SM_sequence_t`. Carve-out: mode-4 standalone binaries keep `ir_body` fallback (no `SM_sequence_t` at runtime; `pl_dcg_register` wires predicates at standalone startup).

- [x] IR-CD-1/2/3 — `bb_idx` field + populate + strangler helpers. `419fce29`.
- [x] IR-CD-RENAME — Category A rename across 15 files. `a97be4b0`. Category B (true Prolog DCG grammar) and C (`icn_bb_dcg`, `pl_bb_dcg`, `lower_pat_dcg.*`, `*_dcg_state_t`) deferred.
- [x] IR-CD-4 — 19 consumer read sites migrated to `bb_graph_of_*(entry)` across 5 files. `b97b267b`.
- [ ] **IR-CD-5 (NEXT)** — Delete `ir_body` field from both struct typedefs. Delete fallback branch in strangler helpers. Delete `ir_body = …` assignments in `lower.c` and `pl_runtime.c`. Mode-4 standalone policy: register stub `SM_sequence_t` at startup, or accept carve-out permanently. Decide before delete.
- [ ] IR-CD-6 — Update `ARCH-IR.md` (single-structure invariant + mode-4 carve-out). Update PLAN watermark.
- [ ] IR-CD-7 — Close-out: full gate floor run.

### IR Rename — builder/consumer case scheme

**Rule:** UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`). lowercase consumes (`sm_interp_*`, `bb_print`, `bb_broker`, all `SM_templates/` dispatchers). Case at the call site tells you which side of the pipeline you're on.

- [x] IR-RN-0 — Bulk rename in 3 sed passes. 48 files. Headers `IR.h`→`BB.h`, `sm_prog.h`→`SM.h`. `9ce69899`.
- [x] IR-RN-1 — Audit `lower.c` post-rename. `c710506f`. Single finding: `sm_pat_capture_fn_arg_names` (builder helper, lowercase by mistake from IR-RN-0 Phase 3 sm_pat_* lowercase sweep) → `SM_pat_capture_fn_arg_names`. File-local, 2 sites. Sibling `lower_*.c` files clean.
- [x] IR-RN-2 — Audit emitters (`emit_bb.c`, `emit_sm.c`, `emit_core.c`). `92417a85`. Single cluster: 4 stale `ir_*` consumers (`ir_node_id`, `ir_is_generator`, `ir_walk`, `ir_walk_rec`) → `bb_*` (consume `BB_t`/`BB_graph_t`/`BB_op_t`). 18 files, 32 call sites + 1 header (`src/include/emit_ir.h`) + 4 defs. emit_bb.c and emit_sm.c clean. Apparent builder calls in emit_sm.c (BB_alloc/BB_node_alloc/BB_free, SM_seq_free) are legitimate pattern-window IR construction + destructors.
- [ ] **IR-RN-3 (NEXT)** — Audit runtime (`sm_interp.c`, `sm_jit_interp.c`, `ir_exec.c`).
- [ ] IR-RN-4 — Update arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`).
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

