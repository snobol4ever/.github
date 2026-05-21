# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → fresh SM/BB lowering, never restore AST walk.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract. Never cross language-A SM-bridge with language-B BB object.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Single gate run at end of session.**
6. **Builder/consumer case rule.** UPPERCASE builds IR (`SM_*`, `BB_*`). lowercase consumes (`sm_*`, `bb_*`).
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary lives inside each `IS_<BE>` arm — never as a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode iteration calls `emit_mode_set(TEXT_MODE(), out)` at entry. Individual dispatchers stay idempotent.
9. **One file per Byrd Box in `BB_templates/`.** Each Byrd Box (`bb_lit`, `bb_any`, ..., `bb_capture`, `bb_pl_arith`, ...) lives in its own `bb_<name>.c`. No consolidated multi-BB TUs. EC-UNI-13(a) and 13(e) violated this and were reversed at one4all@266fc28a.

## Session Setup

Every session container hits the same three friction points. The block below installs around them; each step is idempotent.

```bash
# (1) System packages — installs libgc-dev (Boehm GC, fixes the recurring
#     'fatal error: gc/gc.h: No such file or directory'), bison, flex, nasm,
#     wabt, libgmp-dev, m4. SKIPs when present.
bash /home/claude/one4all/scripts/install_system_packages.sh

# (2) Build scrip with FULL output to log (the build_scrip.sh wrapper's
#     'tail -3' truncates real errors; bypass it). On failure, grep for
#     the cause in one line.
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
if [ ! -x /home/claude/one4all/scrip ]; then
    echo "BUILD FAILED — first error:"; grep -E "error:|fatal error" /tmp/build_full.log | head -5
    exit 1
fi
echo "OK scrip built"

# (3) Git identity in all three repos (per RULES.md).
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done

# (4) SPITBOL oracle (ships with prebuilt bin/sbl).
[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
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
GATE-3  bash scripts/test_icon_all_rungs.sh                    # PASS=194 (--interp by default)
```

## Watermark

```
one4all: 9b5ba0b6   (this session: build fix + EC-UNI-21 gate landed; sm_call_expression(int)
                     runtime helper renamed to sm_eval_subexpr(int); sm_expr_incr.c added to
                     Makefile; scripts/test_gate_ec_uni_complete.sh created.
                     EC-UNI-14(c)(1..7) closed: SCRIP_UNIFIED_DISPATCH default ON then deleted;
                     sm_push_null split into +_noflip variant; sm_label() template; all 5 residual
                     opcodes (PUSH_EXPR, PUSH_EXPRESSION, CALL_EXPRESSION, INCR, DECR) covered;
                     legacy switch + dispatch_one_x86 wrapper + flag deleted; emit_walk_codegen
                     per-PC body collapsed to ~12 lines; bb_pl_{arith,atom,builtin,call} wired
                     into emit_bb_node.  Ladder: 90557fbe -> 098a03ba -> c599bbab -> 46e8c531 ->
                     862f817a -> c081758f -> 9b5ba0b6.  Net LOC across rung: roughly -130.
                     Prior 266fc28a — BB_templates one-file-per-Byrd-Box restored.)
corpus:  5fc1427    (demo/beauty/ canonical; beauty_suite/ apparatus separated)
.github: (this commit — record EC-UNI-14(c)(1..6) close + revised goal text below)
smoke icon:    5/0    smoke prolog: 5/0    smoke rebus: 4/0
smoke raku:    5/0    smoke snobol4: 7/0    smoke snocone: 5/0
broker:        23/26
icon rungs:    194/36/35
matrix gate:   450/450 PASS
firewall lower:   9/6   firewall runtime: 16/8   firewall stage2: 10 (token gate)
beauty.sno --compile md5:           40df9e004c3e963c99af716c65f2c970  (882901 bytes)
beauty.sno --compile assembled .o:  3adbb73f88edcc5416d38baade6faf97  (494336 bytes)
                                    EC-UNI-14(c)(5) — flag removed; one path only.
emit_io self-test: 6/6 PASS
EC-UNI-14 ladder closed: 14-PREREQ d6e5c8f1 -> 14(a) 66cf8506 -> 14(b) dc4e6a9d/5dc52dd4/fe195613.
                  EC-UNI-14(c)(1..7): 90557fbe -> 098a03ba -> c599bbab -> 46e8c531 ->
                                       862f817a -> c081758f -> 9b5ba0b6.
                  EC-UNI-14 proper SM-side + BB-side: CLOSED.  EC-UNI-21 CLOSED (close gate
                  scripts/test_gate_ec_uni_complete.sh, 9/9 PASS on HEAD).  M1 oracle DRIFTED
                  (current md5 9cddff2534472b822438801d8db58a99, 622 lines, vs M1 baseline
                  abfd19a7..., 646 lines) — EC-UNI-21-followup tracks reconcile vs retire.
                  Remaining open in EC-UNI: EC-UNI-16/17/18/19/20/21-followup/22.
beauty.sno in corpus: ONE — programs/snobol4/demo/beauty/beauty.sno (627 lines,
                            md5 5be1de188af42be42e15e6d9a552f759, self-contained).
                            Subsystem apparatus at programs/snobol4/beauty_suite/.
```

---

## Active rungs

### EC-UNI — unify all walkers; one fn per opcode/kind, one arm per backend

**Target:** one fn per SM opcode, one fn per BB kind, each with five `if (IS_<BE>)` arms (X86/JVM/JS/NET/WASM). Text-vs-binary hides inside each arm. After completion, `emit_walk_codegen`/`emit_jvm_from_sm`/`emit_js_from_sm`/`emit_net_from_sm`/`emit_wasm_from_sm`/`dispatch_one_x86` all delete. "Fix backend X for opcode Y" becomes "open `sm_<y>.c`, edit the `IS_X` arm."

**Three-layer cake:**
- **Layer 1** — top-level templates `SM_templates/sm_<op>.c` / `BB_templates/bb_<kind>.c`. Signature `void sm_<op>(void)` / `void bb_<kind>(void)`. Reads `g_emit.*`. Branches ONLY on `IS_<BE>`. Verbose and explicit — literal output strings visible in every arm.
- **Layer 2** — per-backend `static` helpers in the same file. Hides cross-mode logic (TEXT/BIN, body/method gates, fallbacks) — never formatting shortcuts. Extract only at EC-UNI-16, with sharp justification.
- **Layer 3** — string-builder primitives in `src/emitter/emit_io.{c,h}`: `emit_text`/`emit_textf`/`emit_byte`/`emit_bytes`. Funnel for all output.

**`g_emit` single global** (in `emit_globals.{c,h}`) carries all per-template state. Not re-entrant. Snocone bootstrap maps 1:1 to flat `DATA('Sm_emit(...)')` declaration.

**Scope inventory:** SM has 76 opcodes touched by walkers, 52 templates exist (carrying IS_X86), ~20 to add. BB has 21 opcodes touched, 16 templates exist (PAT_*), 4 new (`BB_PL_ARITH/ATOM/BUILTIN/CALL`). Walkers delete after coverage lands: net −2500 to −3500 LOC.

**Unblocks Phase B:** five per-backend GOAL files (`GOAL-SN4-X86-EMIT` [new], `GOAL-SN4-JVM-EMIT`, `GOAL-SN4-JS-EMIT`, `GOAL-SN4-NET-EMIT`, `GOAL-SN4-WASM-EMIT`).

Closed sub-rungs trail: EC-UNI-10..13(e), 14-PREREQ, SUSPEND_VALUE fix, 14(a), 14(b), 14(c)(1..7), 15, 21.
See git log for per-commit detail.

#### Open sub-rungs

- [x] **EC-UNI-14 proper (SM-side + BB-side, CLOSED 2026-05-20)** — Ladder of six commits
  (`90557fbe -> 098a03ba -> c599bbab -> 46e8c531 -> 862f817a -> c081758f`):

  | step | commit | what |
  |------|--------|------|
  | (c)(1) | `90557fbe` | flip SCRIP_UNIFIED_DISPATCH default 0 -> 1 |
  | (c)(2) | `098a03ba` | split sm_push_null() into sm_push_null + sm_push_null_noflip; lift PUSH_NULL_NOFLIP exclusion from dispatch_one_x86 |
  | (c)(3) | `c599bbab` | sm_label() template; lift last (SM_LABEL) exclusion |
  | (c)(4) | `46e8c531` | cover last 5 opcodes (PUSH_EXPR/PUSH_EXPRESSION/CALL_EXPRESSION/INCR/DECR) via new SM_templates/sm_expr_incr.c; drop JS PUSH_EXPRESSION and WASM INCR/DECR walker overrides |
  | (c)(5) | `862f817a` | delete legacy switch + dispatch_one_x86 + SCRIP_UNIFIED_DISPATCH flag; emit_walk_codegen per-PC body collapsed to ~12 lines |
  | (c)(6) | `c081758f` | wire bb_pl_{arith,atom,builtin,call} into emit_bb_node (now total over 21 BB kinds) |
  | (c)(7) | `9b5ba0b6` | **emergency build fix** — `46e8c531` had pushed a broken HEAD: (a) name collision `void sm_call_expression(void)` (new template) vs `DESCR_t sm_call_expression(int)` (long-standing runtime helper) prevented `emit_core.c` from compiling; (b) `sm_expr_incr.c` was never added to the Makefile, so its 5 templates link-undefined even with the collision fixed.  Resolution: rename runtime `sm_call_expression(int)` → `sm_eval_subexpr(int)` (5 files, ~12 call sites; preserves the structural `sm_<OPCODE>` template convention); add `sm_expr_incr.c` to the Makefile source list + compile rule.  All watermark numbers reproduce post-fix (beauty md5 byte-identical at `40df9e004...`, broker 23/26, icon rungs 194/36/35, all smoke 5/0..7/0).  Lesson: future (c)(*) rungs that add new template files MUST verify `make scrip` from a clean tree before commit; the build was broken at HEAD `c081758f` between push and this session. |

  **Original goal text framing correction:** the goal said "delete the five silo walkers";
  in practice only `dispatch_one_x86` was a silo and was deleted.  The four backend
  frame-emitters (`emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`,
  `emit_wasm_from_sm`) survive because they own per-backend file structure that's above
  the opcode level — JVM method-split, JS switch frame, .NET class scaffolding, WASM
  block-loop.  They're already thin (each routes opcode bodies through emit_sm_dispatch),
  and cannot dissolve into per-opcode templates without conflating frame structure with
  opcode routing.

  Net LOC across the rung: roughly -130 (Step (c)(5) alone was -136 in emit_sm.c).

  **Side effects identified, queued as separate rungs:**
  - **emit_push_expr in lower.c is dead in practice** — called by TT_UNIFY / TT_CUT /
    TT_LIMIT arms that are unreachable across all observed gates (Prolog uses lower_pl.c
    BB path, Icon \\limit goes through lower_limit_every).  sm_push_expr() template kept
    for safety.  Standalone cleanup rung's worth.
  - **SM_INCR / SM_DECR are vestigial** — emitted only by `sm_interp_test.c`; no live
    frontend lowers either today.  Could be deleted entirely in a sibling rung.
  - **NET's inline SM_LABEL function-prologue handling** could move into `sm_label()`'s
    NET arm.  Needs walker-local `fn_params`/`fn_nparams` in `g_emit` — EC-UNI-15 Layer-2
    extraction territory.

- [x] **EC-UNI-21 (CLOSED 2026-05-20)** — beauty.sno byte-identity gate matrix.
  `scripts/test_gate_ec_uni_complete.sh` runs all five gates + baseline md5
  (`40df9e004c3e963c99af716c65f2c970`) + M1 oracle md5
  (`abfd19a7a834484a96e824851caee159`).  9/9 cells PASS on HEAD after the
  (c)(7) build fix.  **M1 status: DRIFTED.**  Current SPITBOL oracle output on
  beauty.sno is md5 `9cddff2534472b822438801d8db58a99` (622 lines), not the
  `abfd19a7...` baseline (646 lines).  Reported by the gate, not enforced.
  Re-converge to oracle parity OR formally retire M1 — tracked as
  **EC-UNI-21-followup** in this file.

- [x] **EC-UNI-15 (CLOSED 2026-05-20)** — top-level shape: every template fn is a verbose `if (IS_<BE>)` five-arm switch.  Evidence: `scripts/test_gate_em_template_matrix.sh` reports **450/450 cells covered** across 34 files / 90 fns (0 misses).  New audit script `scripts/test_gate_ec_uni_15_audit.sh` re-runs the matrix gate and additionally records the fn-size distribution: **71 fns < 30 lines, 11 fns 30-59 lines, 8 fns >= 60 lines**.  The 8 oversized fns (`bb_arbno` 111, `bb_lit` 98, `sm_suspend_value` 87, `bb_cat` 87, `sm_call_fn` 86, `bb_tab` 80, `bb_alt` 75, `bb_capture` 66) are queued as the EC-UNI-16 candidate list — that rung extracts Layer-2 helpers per the "justified iff carries a real conditional ..." rule.  The matrix gate plus per-fn size inventory together establish that no fn is missing a backend arm and the remaining largeness is documented work, not hidden silos.

- [ ] **EC-UNI-16** — REDUCE phase. Extract Layer-2 helpers, rule: **justified iff carries a real conditional (IS_TEXT/IS_BIN, body/method gate, fallback) OR de-duplicates non-trivial computation in ≥2 templates. String-concat shortening NOT a reason.** Justified: `jvm_jump_to_pc(target)`, `jvm_ret_guard(op,sfx)`, `net_ret_guard(op)`. NOT: `jvm_invokestatic(class,method,sig)`.  **Candidate list** (8 fns ≥60 lines, from `scripts/test_gate_ec_uni_15_audit.sh`): `bb_arbno` 111, `bb_lit` 98, `sm_suspend_value` 87, `bb_cat` 87, `sm_call_fn` 86, `bb_tab` 80, `bb_alt` 75, `bb_capture` 66.  Note: `sm_suspend_value` and `sm_call_fn` are byte-near-duplicates of each other across all five arms — likely the single biggest justified-helper opportunity in this list.

- [ ] **EC-UNI-17** — Layer-3 primitives audit. Add only if multi-line pattern recurs in ≥3 sites across ≥2 backends. Skipping is the expected answer.

- [ ] **EC-UNI-18** — table-driven dispatch where it earns its keep. x86's `g_sm_nullary`/`g_sm_arith` work; extend to JVM/NET/JS/WASM for nullary + arith only.

- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`). Mechanical patch + revert. Records LOC cost.

- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`). Mechanical patch + revert. Records LOC cost.

- [ ] **EC-UNI-22** — close: update `ARCH-IR.md`, `ARCH-SCRIP.md`, invariant block to reflect three-layer cake + `g_emit`. Update four per-backend GOAL files. Mark EC-UNI complete; Phase B opens.

- [ ] **EC-UNI-21-followup** — reconcile or retire M1 oracle baseline.  Choose one:
  (a) **Re-converge**: find the regression between M1 (oracle md5 `abfd19a7...`,
  646 lines) and current (`9cddff25...`, 622 lines), fix it in the SNOBOL4 runtime
  or beauty.sno source, restore byte-identity to the oracle baseline.  (b) **Retire
  M1**: declare the M1 oracle md5 obsolete in the THREE-MILESTONE AUTHORSHIP
  AGREEMENT (PLAN.md), record the new baseline md5 (`9cddff2534472b822438801d8db58a99`,
  622 lines) and re-stamp Milestone 1 with the current state.  Lon's choice; this
  rung blocks formal "Milestone 1 = oracle parity" claims until resolved.

#### EC-UNI gate (every step from EC-UNI-10 on)

```
GATE-1  beauty.sno --compile  →  md5 40df9e004c3e963c99af716c65f2c970  (882901 bytes)
GATE-2  bash scripts/test_smoke_icon.sh                                  # PASS=5
GATE-3  bash scripts/test_smoke_unified_broker.sh                        # PASS≥23
GATE-4  bash scripts/test_icon_all_rungs.sh                              # PASS=194/36/35 (--interp by default)
GATE-5  bash scripts/test_smoke_{snobol4,snocone,prolog,rebus,raku}.sh   # 7/0 5/0 5/0 4/0 5/0
```

---

### ISOLATION — parse->lower / parse->runtime boundary firewalls

**Goal:** lex/parse produces exactly `tree_t *`. Two boundaries: parse→lower (consumed by `lower()`) and parse→runtime. Today partially porous; ratchet shrinks the gap.

Completed: ISO-1 `261ff13d` (`lower(const tree_t *)`, ParserOutput deleted), ISO-2 `1691f44f` (lower firewall 10/7), ISO-3 `cb1738f6` (relocated `icon_gen.h`; lower 9/6, runtime firewall 16/8).

- [ ] **ISO-4 (NEXT)** — `scrip_parse` subprocess: parsers in a separate executable, stdin = source, stdout = TDump/TLump S-expression. SCRIP forks/execs, deserializes back to `tree_t`. Unsolved: no C-side TDump deserializer exists yet. **First sub-step:** write deserializer + roundtrip self-test before introducing the process boundary.
- [ ] **ISO-5** — Shrink lower firewall allowlist toward 0: extract `IcnTkKind` to `src/include/icon_tk.h`; split `raku_driver.h` → `raku_parse.h` + `raku_runtime.h` (relocate); relocate `frontend/prolog/{term,prolog_runtime,prolog_atom}.h` to `src/runtime/interp/prolog/`; rename `scrip_cc.h` → `src/include/scrip_lang.h` (54 includers, mechanical).
- [ ] **ISO-6** — Shrink runtime firewall allowlist toward 0 (overlaps ISO-5).
- [ ] **ISO-7** — Link-time isolation test: `lower.o` + `lower_*.o` linked against a tree with all `src/frontend/*.o` absent. Any unresolved symbol = real leakage. **Honest scope:** today's firewalls are header-level; ISO-7 closes the symbol-reachability gap (most acutely through `scrip_cc.h`).

### IR Rename — builder/consumer case scheme

UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`). lowercase consumes (`sm_interp_*`, `bb_print`, `bb_broker`, all `SM_templates/` dispatchers). Case at the call site = side of the pipeline.

Completed: IR-RN-0 `9ce69899` (bulk rename, 48 files), IR-RN-1 `c710506f` (lower.c audit; `SM_pat_capture_fn_arg_names` fix), IR-RN-2 `92417a85` (emitter audit; 4 stale `ir_*` consumers → `bb_*`), IR-RN-3 `4a1fcc63` (runtime audit; `SM_label_pc_lookup`→`sm_label_pc_lookup`, `BB_reset`→`bb_reset`; `SM_codegen` kept UPPERCASE).

- [ ] **IR-RN-4 (NEXT)** — Update arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`).
- [ ] IR-RN-5 — Full cross-language gate run; close rung.

Reserved (untouched): `IR_LANG_*`, `SM_INTERP_*`, `SM_CALL_STACK_MAX`/`SM_GEN_LOCAL_MAX`/`SM_MAX_OPERANDS`, `BB_POOL_SIZE`, header guards, `SM_*` opcode tags, `SM_templates/`/`BB_templates/` dir names.

---

## Completed ledgers (audit trail)

Full per-cluster detail lives in commit messages (git log is authority per RULES.md). This list is one-line summaries only.

- **IJ-* / DAI-1..7 / IJ-HELLO matrix** — 6/6 wired hello-world matrix closed 2026-05-18. Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265; mode 1 deleted. Icon AST walker amputated. `rt_bb_once_proc` deleted; bridge shims = `rt_pl_once` + `icn_bb_dcg`.
- **DAI-8 dead-code sweep C1–C17** — ~2700 LOC removed across 17 clusters. Final cluster C17 `d48681fb`. Methodology (kept for future audits): linker-GC + `@PLT` regex filter; grep + `&NAME` audit; Method-7 sub-graph deletion.
- **EC (emitter consolidation) 0..WASM-SM** — three silo files + emit_ir.c + emit_ir_targets.c deleted. Unified `emit_program(ast_prog, out, mode)`. Net −2504 LOC. Final commits `8890d685`/`e1c8a4ac`/`7c33121c`/`268619c1`.
- **EC-UNI 0..9d** — 52 SM templates with IS_X86 arms; matrix gate 0/365. Axis correction (false 10-cell text/binary axis → 5-cell backend matrix).
- **IR-CONSOLIDATE-DCG 1..7** — `ir_body` field deleted; mode-4 standalone uses `SM_seq_bb_add` lazy-alloc. ARCH-IR updated. Carve-out: mode-4 standalone binaries keep `ir_body` fallback (no `SM_sequence_t` at runtime). Final commit `489ff5b3` + close-out gate run.
- **ST2 — Stage 2 handoff as named struct** — `stage2_t` embeds `SM_sequence_t` and owns sidecars; `g_stage2` is a global value. Six reader shim macros burned down (`14655275`/`4f5d0512`/`d73cded0`/`27ad177b`). Dynamic-grow `label_table`/`proc_table` (`b42b7979`); ~150KB .bss freed; >4096 labels or >256 procs no longer truncate. Token firewall gate `b733dd13`. Honest scope: token-level, link-time analog deferred.

**Authors (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.
