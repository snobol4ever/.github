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
8. **Unified dispatch owns mode-setting.** Per-opcode iteration calls `emit_mode_set(TEXT_MODE(), out)` at entry.
9. **One file per Byrd Box in `BB_templates/`.** Each lives in its own `bb_<name>.c`. No consolidated multi-BB TUs.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh   # libgc-dev, bison, flex, nasm, wabt, libgmp-dev, m4 (idempotent)

cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/one4all/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }

for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done

[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64

bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=399 FAIL=0 STUB=660 NEW=0 GONE=0  (at one4all 44a5f9a5).
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, single-structure via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) is the reference path for Icon at 194/265. Mode 4 (`--compile`) emits wired x86 — no `bb_broker`.

## Gates

### ALWAYS test in --run for emitter work

`--run` is the only mode that exercises the x86 emitter through the JIT path. `--interp` runs the SM dispatch interpreter and NEVER touches x86 emission. For work touching `emit_bb.c`, `emit_sm.c`, `BB_templates/`, `sm_*.c` templates, x86 lowering, or byte-emission primitives: test under `--run` (or `--compile` for byte-identity), not `--interp`.

Use for emitter work:
- `scripts/test_crosscheck_icon.sh` — three modes including `--run` (JIT).
- `scripts/test_smoke_snobol4_jit.sh` — three-mode parity, `--run` baseline 186.
- `scripts/test_gate_ec_uni_complete.sh` — beauty.sno `--compile` md5 + 9-gate roll-up.
- `scripts/test_gate_em_template_matrix.sh` — structural invariant.

### Cadence (per Lon, 2026-05-21)

Per-kind diff is the **primary per-slice invariant** (~5–10s, 1059 cells, byte-level filter+diff). Subsumes most of what matrix + beauty caught indirectly. Legacy gates are session-end / escalation only.

**Per-slice fast cycle:**
```
make -j4 scrip
bash scripts/test_per_kind_diff.sh
```

**Session-end:**
```
bash scripts/test_per_kind_diff.sh
bash scripts/test_gate_em_template_matrix.sh
bash scripts/test_gate_ec_uni_complete.sh
```

**Escalate mid-session ONLY when:** per-kind-diff reports FAIL/GONE; the slice touches LIVE PATH dispatchers (`emit_flat_ir`, `emit_walk_codegen`, `dispatch_one_x86`, WASM/JS/NET silo walkers); the slice changes `g_emit` shape; the slice deletes any `emit_bb_x*` / `emit_sm_*` fn.

### Gate commands

```
GATE-PK bash scripts/test_per_kind_diff.sh                # PRIMARY per-slice
GATE-M  bash scripts/test_gate_em_template_matrix.sh      # session-end
GATE-E  bash scripts/test_gate_ec_uni_complete.sh         # session-end
GATE-J  bash scripts/test_crosscheck_icon.sh              # escalation
GATE-S  bash scripts/test_smoke_snobol4_jit.sh            # escalation
```

Legacy --interp gates (interpreter work only):
```
bash scripts/test_smoke_icon.sh                  # PASS=5
bash scripts/test_smoke_unified_broker.sh        # PASS≥23
bash scripts/test_icon_all_rungs.sh              # PASS=194
```

### Re-freezing the per-kind baseline

When a change is INTENTIONAL (refactoring, new backend cell, fix to a known-wrong emission), per-kind diff will FAIL because the baseline is stale:
```
bash scripts/freeze_per_kind_baseline.sh
bash scripts/test_per_kind_diff.sh                # confirm PASS=N FAIL=0 NEW=0 GONE=0
```
Commit `baselines/per_kind/` with the source change. The diff IS the regression-test record of what intentionally moved.

## Watermark

```
one4all: f6e4968a  (PPV-7: fix RPOS/RTAB --compile segfault. emit_flat_invariant
                     + pre_build_children_text + pre_build_children all walked
                     nd->c[i] for i<nd->n without guarding nd->c==NULL.
                     pat_node_intarg sets nd->n=1 as reverse-flag, not child
                     count. Guard: if (!nd->c) return. All gates unchanged.)
one4all: 1c47a59a   (PPV-2: lower-time SM_PAT_* substitution for protected names
                     in lower_pat_expr TT_VAR arm.  Also: normalize_per_kind_cell.py
                     normalizer hole fixed (lookahead in sid_nid regex); baseline
                     re-frozen PASS=399.  Beauty md5 → 6bf2e9daa777f54f04c8f7160da435d1
                     (882524 bytes).  PPV-3/4/5/6 verified and closed.
                     GATE-PK PASS=399 FAIL=0; GATE-M 855/855; GATE-E 9/9;
                     --run smoke 186 unchanged.)
one4all: 44a5f9a5   (PPV-1: protect REM/ARB/FENCE/FAIL/SUCCEED/ABORT/BAL.
                     ERROR 042 on user-reassign, matching SPITBOL.  Closes
                     HQ-BUG-PROTECTED-PATTERN-VARS.  Guard at NV_SET_fn
                     chokepoint with init-phase flag g_protected_pat_vars_armed.
                     New helper module src/runtime/rt/rt_protected.{h,c}.
                     Discovery: --interp h_store_var calls NV_SET_fn
                     directly, bypassing rt_nv_set — NV_SET_fn is the
                     only universal chokepoint.  PK PASS=399 unchanged;
                     SNOBOL4 smoke --run 186 unchanged.)
.github: afa893a0   (PPV-0 inventory.  Deliverable: PPV-0-INVENTORY.md.
                     7 pat-name enums confirmed.  Substitution site
                     lower.c:373; protection site NV_SET_fn:2462.)
one4all: 9b905d26   (EC-UNI-PER-KIND-DIFF harness.  5 backends × submode:
                     x86/{text,binary,text_macro}+jvm+net+js+wasm text.
                     1059 cells.  Baseline PASS=399 STUB=660 FAIL=0.
                     baselines/per_kind/ 3.4 MB committed.  Regression
                     detection verified empirically.)
corpus:  5fc1427    (demo/beauty/ canonical; beauty_suite/ apparatus separated)

smoke icon: 5/0    smoke prolog: 5/0   smoke rebus: 4/0
smoke raku: 5/0    smoke snobol4: 7/0  smoke snocone: 5/0
broker: 23/26      icon rungs: 194/36/35
matrix gate: 855/855 PASS
beauty.sno --compile md5:           40df9e004c3e963c99af716c65f2c970  (882901 bytes)
beauty.sno --compile assembled .o:  3adbb73f88edcc5416d38baade6faf97  (494336 bytes)
EC-UNI-21 9/9 PASS.  M1 oracle DRIFTED (9cddff25, 622 lines vs M1 abfd19a7, 646 lines).
beauty.sno in corpus: programs/snobol4/demo/beauty/beauty.sno (627 lines,
  md5 5be1de188af42be42e15e6d9a552f759, self-contained).
```

---

## Active rungs

### EC-UNI — unify all walkers; one fn per opcode/kind, one arm per backend

**Target:** one fn per SM opcode, one fn per BB kind, each with five `if (IS_<BE>)` arms (X86/JVM/JS/NET/WASM). Text-vs-binary hides inside each arm. After completion, `emit_walk_codegen` / `emit_jvm_from_sm` / `emit_js_from_sm` / `emit_net_from_sm` / `emit_wasm_from_sm` / `dispatch_one_x86` all delete.

**Three layers:**
- **Layer 1** — `SM_templates/sm_<op>.c` / `BB_templates/bb_<kind>.c`. `void sm_<op>(void)` / `void bb_<kind>(void)`. Reads `g_emit.*`. Branches ONLY on `IS_<BE>`.
- **Layer 2** — Deferred (Lon, 2026-05-20). No static helpers in templates, no cross-template factoring. Future "one-source-line-per-output-line" expansion is Phase B.
- **Layer 3** — `src/emitter/emit_io.{c,h}`: `emit_text` / `emit_textf` / `emit_byte` / `emit_bytes`. Funnel for all output.

`g_emit` (`emit_globals.{c,h}`) carries all per-template state. Not re-entrant. Maps 1:1 to flat `DATA('Sm_emit(...)')` in Snocone bootstrap.

---

### ⚡ EC-UNI LIFT PATTERN

**Lon directive (2026-05-21):** Methodical lift, respect existing abstraction boundaries. Friction was gate cadence, not methodology.

**Job:** For each x86 codegen fn still in `emit_sm.c` / `emit_bb.c`, lift into its template's `IS_X86` arm. Self-contained body (calls only widely-visible helpers) → verbatim paste. Body depending on file-static plumbing (`render_call_line`, `sm_template_lookup`, `emit_sm_args_t`, etc.) → DO NOT un-static; the existing one-line wrapper IS the lift.

**Recipe:**
1. Identify fn.
2. Inspect body. Public helpers only → step 3-6. File-static deps → "already-lifted-as-helper", next.
3. Find matching template.
4. Copy body into `if (IS_X86) { ... return; }`. Rewrite parameters as `g_emit` reads: `s/f/b` → `g_emit.lbl_succ/lbl_fail/lbl_back`; `n` → `nd->ival`; `lit` → `nd->sval`; `out` → `g_emit.out`.
5. Helpers stay. Do not move, extract, or factor.
6. Leave original. Dispatcher still calls it; two paths coexist.
7. Fast cycle: `make -j4 scrip` → `test_per_kind_diff.sh`. Commit.

**Canonical example:** `71bd8b6f` lifted `emit_bb_xstar` → `bb_rem` IS_X86 arm and `emit_bb_xlnth` → `bb_len` IS_X86 arm. `g_emit` gained `lbl_succ` / `lbl_fail` / `lbl_back`.

**Mistakes to avoid:**
- Static helpers inside templates collapsing opcodes (slice 1, reverted).
- Layer-2 helpers in `emit_core.c` factoring across templates (slice 2, reverted).
- "Fn fits on a screen" — rule removed.
- Un-static file-private machinery to fit verbatim paste.
- Running full regression per slice (cadence problem, not methodology).

**Lift queue status:**

- **BB-side: COMPLETE** through slice 7 (one4all `045baf4a`). All 17 pat-level `emit_bb_x*` fn bodies physically in `BB_templates/`. Remaining x86 in `emit_bb.c` is dispatcher trio `emit_flat_ir_alt` / `_cat` / `_fence` — control-flow-assembly slice, not lift sweep.
- **SM-side: COMPLETE.** All 36 `emit_sm_*_(dispatch|line|template)` fns are already-lifted-as-helper (31 small wrappers + 5 larger bodies, all depending on `emit_sm.c`'s file-private machinery: `sm_op_template_t`, `emit_sm_args_t`, `sm_template_lookup`, `render_call_line`).

**Verification per commit:** matrix 855/855; beauty.sno --compile md5 `40df9e004c3e963c99af716c65f2c970`.

**Scope:** SM has 91 opcodes in enum, 76 dispatched (15 runtime/sentinel — not template work). BB has 97 kinds, all dispatched by `emit_bb_node` (21 pat+Prolog carry real code, 76 honest no-op stubs awaiting Phase B). Walkers delete after coverage lands: net −2500 to −3500 LOC.

**Unblocks Phase B:** five per-backend GOAL files (`GOAL-SN4-X86-EMIT` [new], `-JVM-`, `-JS-`, `-NET-`, `-WASM-`).

Closed sub-rungs: EC-UNI-10..13(e), 14-PREREQ, SUSPEND_VALUE, 14(a)(b)(c)(1..7), 15, 16, 21. See git log for per-commit detail.

---

### ⚡ EC-UNI-PER-KIND-DIFF (one4all `9b905d26`)

Harness: `tools/emit_per_kind_audit.c` + `scripts/{freeze_per_kind_baseline,test_per_kind_diff,normalize_per_kind_cell}` + `baselines/per_kind/`.

For every (SM op × backend) and every (BB kind × backend × submode) cell, audit constructs synthetic instance, emits via current path, captures text/binary, normalizes (strips label numbers, addresses, node ids), diffs against frozen baseline. 1059 cells per run; baseline PASS=399 STUB=660 FAIL=0.

**Live path notes:**
- BB-side: `emit_flat_ir` → direct `emit_bb_x*` calls is still the live path; `emit_bb_node` does not yet fill `g_emit` fields, so templates' IS_X86 arms are dormant. This is the structural invariant the next rungs (REFAITH, REWIRE-ALL) operate on.
- x86_bin: process-local addresses (memcmp@PLT, rodata literal pointers) get baked in; ASLR randomizes. Bit-identity impossible. Per-kind-diff applies structural comparison for x86_bin (same byte count = same shape); full byte-level via assembled-md5 path on x86_text.

---

### ⚡ Open EC-UNI rungs

- [ ] **EC-UNI-REFAITH** — re-lift FAILing kinds byte-faithfully against per-kind diff baseline. Gate must show 100% PASS.
- [ ] **EC-UNI-REWIRE-ALL** — with per-kind diff 100% PASS, route `emit_flat_ir` through `emit_bb_node` for all kinds in IS_TEXT. **Path-a/b decision required from Lon:** (a) text-first staged (cheap, dual-path interlude), (b) name-keyed binary primitives first (one rewire for both modes).
- [ ] **EC-UNI-NAMEKEY-BIN** — name-keyed binary primitives for `--run`; rewire binary; delete `emit_bb_x*` originals.
- [ ] **EC-UNI-17** (deferred) — Layer-3 primitives audit. Parked.
- [ ] **EC-UNI-18** — table-driven dispatch where it earns its keep. Extend x86's `g_sm_nullary` / `g_sm_arith` pattern to JVM/NET/JS/WASM for nullary + arith.
- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`). Mechanical patch + revert. Records LOC cost.
- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`). Mechanical patch + revert. Records LOC cost.
- [ ] **EC-UNI-21-followup** — reconcile or retire M1 oracle baseline. Choose (a) re-converge to `abfd19a7...` (646 lines), or (b) retire M1, record new baseline `9cddff25...` (622 lines), re-stamp Milestone 1.
- [ ] **EC-UNI-22** — close: update `ARCH-IR.md`, `ARCH-SCRIP.md`, invariants. Update four per-backend GOAL files. Mark EC-UNI complete; Phase B opens.

---

### ⚡ EC-UNI-PROTECTED-PAT-VARS (PPV) — in progress

Recognize REM/ARB/FENCE/FAIL/SUCCEED/ABORT/BAL as protected PATTERN-typed names (SPITBOL ERROR 042) and substitute `SM_PAT_<KIND>` at lower-time for bare names in pattern context. Unlocks BB-lower coverage 4→8 active pat-kinds from portable corpus.

| Name      | TT_*        | SM_PAT_*       | BB_PAT_*    | Template          |
|-----------|-------------|-----------------|-------------|-------------------|
| REM       | TT_REM      | SM_PAT_REM      | BB_PAT_REM  | `bb_rem.c`        |
| ARB       | TT_ARB      | SM_PAT_ARB      | BB_PAT_ARB  | `bb_arb.c`        |
| FENCE     | TT_FENCE    | SM_PAT_FENCE0   | BB_PAT_FENCE| `bb_fence.c`      |
| FAIL      | TT_FAIL     | SM_PAT_FAIL     | (no BB pat) | (Phase B)         |
| SUCCEED   | TT_SUCCEED  | SM_PAT_SUCCEED  | (no BB pat) | (Phase B)         |
| ABORT     | TT_ABORT    | SM_PAT_ABORT    | BB_PAT_ABORT| `bb_abort.c`      |
| BAL       | TT_BAL      | SM_PAT_BAL      | (no BB pat) | (Phase B)         |

(Bare `FENCE` → `SM_PAT_FENCE0`; 1-arg variant uses `SM_PAT_FENCE1` per existing `TT_FENCE` arm in `lower.c`.)

Sites (PPV-0):
- Substitution: `src/lower/lower.c:373` — sole TT_VAR pat-context arm.
- Runtime protection: `src/runtime/snobol4/snobol4.c::NV_SET_fn` (universal chokepoint; --interp h_store_var calls it directly, bypassing rt_nv_set).
- Helper: `src/runtime/rt/rt_protected.{h,c}` — `is_protected_pat_name(name)`, `protected_pat_name_to_sm_op(name)`. Single source of truth for the 7-name → SM_op_t table.
- Error: `sno_runtime_error(42, NULL)`.

**Steps:**

- [x] **PPV-0** (CLOSED 2026-05-21 session #4, .github `afa893a0`) — Inventory. Deliverable: `PPV-0-INVENTORY.md`.
- [x] **PPV-1** (CLOSED 2026-05-21 session #5, one4all `44a5f9a5`) — Runtime protection. New `rt_protected.{h,c}`. Init-phase flag `g_protected_pat_vars_armed` in `snobol4.c` (cleared during pre-binding, armed at end of `SNO_INIT_fn`). Guard at top of `NV_SET_fn` raises `sno_runtime_error(42, NULL)`. Verified vs SPITBOL: scrip ERROR 42 = SPITBOL ERROR 042 ✓. PK PASS=399, --run smoke 186 unchanged. **Closes HQ-BUG-PROTECTED-PATTERN-VARS.**
- [x] **PPV-2** (CLOSED 2026-05-21 session #6, Sonnet 4.6) — Lower-time substitution. `lower.c` TT_VAR arm in `lower_pat_expr` now calls `protected_pat_name_to_sm_op(t->v.sval)`; if ≥ 0 emits `SM_emit(g_p, (SM_op_t)op)` and returns. Confined to `lower_pat_expr`; `lower_expr` untouched. Also fixed normalizer hole in `normalize_per_kind_cell.py` (regex `_(\d+)_(\d+)\b` → `_(\d+)_(\d+)(?=_|\b)`) to canonicalize heap-address-derived label segments; re-froze baseline (PASS=399 unchanged).
- [x] **PPV-3** (CLOSED 2026-05-21 session #6) — `x = REM` → `DATATYPE(x)` = PATTERN ✓. `lower_expr` untouched.
- [x] **PPV-4** (CLOSED 2026-05-21 session #6) — All 7 names via `--dump-sm` emit `SM_PAT_*` directly (no `SM_PUSH_VAR`). `--compile` shows `# BOX REM/ARB/FENCE`; ABORT shows `# BOX FAIL()` (pre-existing: dispatches to `emit_bb_xfail`, not a regression). FAIL/SUCCEED/BAL: `SM_PAT_*` confirmed via `--dump-sm`.
- [x] **PPV-5** (CLOSED 2026-05-21 session #6) — Path (a) taken: new beauty md5 `6bf2e9daa777f54f04c8f7160da435d1` (882524 bytes, was `40df9e004c3e963c99af716c65f2c970` 882901 bytes). Assembled `.o` md5 changed (`01eda5b76d0641ad5db76edde694ef92` ← `3adbb73f88edcc5416d38baade6faf97`) — intentional: PPV-2 removes `SM_PUSH_VAR+SM_PAT_DEREF` pair for protected names, replacing with single `SM_PAT_*`. Gate script baseline updated. GATE-E 9/9 ✓.
- [x] **PPV-6** (CLOSED 2026-05-21 session #6) — Docs. GOAL-HEADQUARTERS.md updated. PLAN.md updated. RULES.md: HQ-BUG-PROTECTED-PATTERN-VARS was already marked CLOSED in PPV-1; no further change needed.
- [x] **PPV-7** (CLOSED 2026-05-21 session #6) — Bug closeouts. HQ-BUG-RPOS-COMPILE-SEGFAULT and HQ-BUG-RTAB-COMPILE-SEGFAULT both fixed. Root cause: `pat_node_intarg()` sets `nd->n = 1` as a reverse flag (RPOS/RTAB vs POS/TAB) but never allocates `nd->c[]`. Three callers walked `nd->c[i]` for `i < nd->n` without guarding `nd->c`: `emit_flat_invariant` (emit_sm.c), `pre_build_children_text` (emit_bb.c), `pre_build_children` (emit_bb.c). Fix: add `if (!nd->c) return;` guard before each loop. GATE-PK 399/0, GATE-M 855/855, GATE-E 9/9, --run 186 unchanged.

**Coverage delta projected after PPV-5:** 4 → 8 BB pat-kinds exercised from portable SNOBOL4 corpus.

**Sequencing:** PPV-* independent of EC-UNI-REFAITH / REWIRE-ALL / NAMEKEY-BIN. Per-slice gate: `test_per_kind_diff.sh` + matrix; beauty md5 explicitly accepted or assembled-`.o` md5 verified at PPV-5.

**Why not part of EC-UNI proper:** EC-UNI's scope is emitter unification. PPV changes frontend lowering + runtime protection, then exposes pre-existing SM_PAT_/BB_PAT_ opcodes to wider source-syntax footprint. Parallel coverage-gain rung, not a dependency.

---

### EC-UNI gate (every step from EC-UNI-10 on)

```
GATE-1  beauty.sno --compile  →  md5 40df9e004c3e963c99af716c65f2c970  (882901 bytes)
GATE-2  bash scripts/test_smoke_icon.sh                                  # PASS=5
GATE-3  bash scripts/test_smoke_unified_broker.sh                        # PASS≥23
GATE-4  bash scripts/test_icon_all_rungs.sh                              # PASS=194/36/35 (--interp by default)
GATE-5  bash scripts/test_smoke_{snobol4,snocone,prolog,rebus,raku}.sh   # 7/0 5/0 5/0 4/0 5/0
```

---

### ISOLATION — parse→lower / parse→runtime boundary firewalls

**Goal:** lex/parse produces exactly `tree_t *`. Two boundaries: parse→lower (consumed by `lower()`) and parse→runtime. Today partially porous; ratchet shrinks the gap.

Completed: ISO-1 `261ff13d` (`lower(const tree_t *)`, ParserOutput deleted), ISO-2 `1691f44f` (lower firewall 10/7), ISO-3 `cb1738f6` (relocated `icon_gen.h`; lower 9/6, runtime firewall 16/8).

- [ ] **ISO-4 (NEXT)** — `scrip_parse` subprocess: parsers in a separate executable, stdin = source, stdout = TDump/TLump S-expression. SCRIP forks/execs, deserializes back to `tree_t`. First sub-step: write deserializer + roundtrip self-test before introducing the process boundary.
- [ ] **ISO-5** — Shrink lower firewall allowlist toward 0: extract `IcnTkKind` to `src/include/icon_tk.h`; split `raku_driver.h` → `raku_parse.h` + `raku_runtime.h`; relocate `frontend/prolog/{term,prolog_runtime,prolog_atom}.h` to `src/runtime/interp/prolog/`; rename `scrip_cc.h` → `src/include/scrip_lang.h` (54 includers).
- [ ] **ISO-6** — Shrink runtime firewall allowlist toward 0 (overlaps ISO-5).
- [ ] **ISO-7** — Link-time isolation test.

### IR Rename — builder/consumer case scheme

UPPERCASE builds IR (`SM_t`, `BB_t`, `SM_seq_new`, `BB_alloc`). lowercase consumes (`sm_interp_*`, `bb_print`, `bb_broker`, `SM_templates/` dispatchers).

Completed: IR-RN-0 `9ce69899`, IR-RN-1 `c710506f`, IR-RN-2 `92417a85`, IR-RN-3 `4a1fcc63`.

- [ ] **IR-RN-4 (NEXT)** — Update arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`).
- [ ] **IR-RN-5** — Full cross-language gate run; close rung.

Reserved: `IR_LANG_*`, `SM_INTERP_*`, `SM_CALL_STACK_MAX`/`SM_GEN_LOCAL_MAX`/`SM_MAX_OPERANDS`, `BB_POOL_SIZE`, header guards, `SM_*` opcode tags, `SM_templates/`/`BB_templates/` dir names.

---

## Completed ledgers (audit trail)

Per-cluster detail in git log (authority per RULES.md). One-line summaries:

- **IJ-* / DAI-1..7 / IJ-HELLO matrix** — 6/6 wired hello-world matrix closed 2026-05-18. Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265; mode 1 deleted.
- **DAI-8 dead-code sweep C1–C17** — ~2700 LOC removed across 17 clusters. Final cluster C17 `d48681fb`.
- **EC (emitter consolidation) 0..WASM-SM** — three silo files + emit_ir.c + emit_ir_targets.c deleted. Unified `emit_program(ast_prog, out, mode)`. Net −2504 LOC.
- **EC-UNI 0..9d** — 52 SM templates with IS_X86 arms; matrix gate 0/365.
- **IR-CONSOLIDATE-DCG 1..7** — `ir_body` field deleted; mode-4 standalone uses `SM_seq_bb_add` lazy-alloc.
- **ST2** — `stage2_t` embeds `SM_sequence_t`; dynamic-grow tables; ~150KB .bss freed.
- **EC-UNI LIFT slices 1-7** — `045baf4a`. All 17 pat-level `emit_bb_x*` in `BB_templates/`. Matrix 855/855.
- **EC-UNI-PER-KIND-DIFF** — `9b905d26`. Harness operational; baseline PASS=399 STUB=660 FAIL=0.
- **PPV-0** — `afa893a0`. Inventory.
- **PPV-1** — `44a5f9a5`. Runtime protection ERROR 042. Closes HQ-BUG-PROTECTED-PATTERN-VARS.
- **PPV-2..6** — `1c47a59a`. Lower-time SM_PAT_* substitution in lower_pat_expr TT_VAR arm. Normalizer fix (sid_nid lookahead). Beauty md5 → 6bf2e9daa777f54f04c8f7160da435d1. GATE-PK 399/0, GATE-M 855/855, GATE-E 9/9.
- **PPV-7** — `f6e4968a`. RPOS/RTAB --compile segfault. nd->c guard in 3 sites (emit_flat_invariant, pre_build_children_text, pre_build_children).

**Authors (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.
