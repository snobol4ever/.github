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
one4all: fe195613   (EC-UNI-14(b) closed — JVM + x86 walkers folded into emit_sm_dispatch)
corpus:  5fc1427    (demo/beauty/ canonical; beauty_suite/ apparatus separated)
.github: (this commit — HQ cleanup pass: trim closed-rung narratives in PLAN.md + HQ + GOAL files)
smoke icon:    5/0    smoke prolog: 5/0    smoke rebus: 4/0
smoke raku:    5/0    smoke snobol4: 7/0    smoke snocone: 5/0
broker:        23/26
icon rungs:    194/36/35
matrix gate:   0/365 PASS
firewall lower:   9/6   firewall runtime: 16/8   firewall stage2: 10 (token gate)
beauty.sno --compile md5:           40df9e004c3e963c99af716c65f2c970  (882901 bytes)
beauty.sno --compile assembled .o:  3adbb73f88edcc5416d38baade6faf97  (494336 bytes)
                                    both identical under SCRIP_UNIFIED_DISPATCH={0,1}
emit_io self-test: 6/6 PASS
EC-UNI-14 ladder: 14-PREREQ d6e5c8f1 → 14(a) 66cf8506 → 14(b) dc4e6a9d/5dc52dd4/fe195613.
                  14 proper NEXT (delete silo walkers + dispatch_one_x86 + retire flag).
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

Closed sub-rungs trail: EC-UNI-10..13(e), 14-PREREQ, SUSPEND_VALUE fix, 14(a), 14(b). See git log for per-commit detail.

#### Open sub-rungs

- [ ] **EC-UNI-14 proper (NEXT)** — delete the five silo walkers + `dispatch_one_x86` wrapper + ~30 `emit_sm_<op>_dispatch` helpers; flip `SCRIP_UNIFIED_DISPATCH` default-ON then delete the flag. Expand `emit_bb_node(void)` to all 21 BB kinds (includes wiring the four `bb_pl_*` from 13(e)). Open follow-up: split `sm_push_null()` template into `sm_push_null()` and `sm_push_null_noflip()` so x86 doesn't need the exclusion list in `dispatch_one_x86` (other backends collapse the two; x86 distinguishes the emitted mnemonic). Net LOC at full close: −2500 to −3500.

- [ ] **EC-UNI-15** — top-level shape: each template fn is a verbose `if (IS_<BE>)` five-arm switch, one screen per fn. Done family-by-family (one commit per family file). Multi-statement arms fine; no helper extraction yet.

- [ ] **EC-UNI-16** — REDUCE phase. Extract Layer-2 helpers, rule: **justified iff carries a real conditional (IS_TEXT/IS_BIN, body/method gate, fallback) OR de-duplicates non-trivial computation in ≥2 templates. String-concat shortening NOT a reason.** Justified: `jvm_jump_to_pc(target)`, `jvm_ret_guard(op,sfx)`, `net_ret_guard(op)`. NOT: `jvm_invokestatic(class,method,sig)`.

- [ ] **EC-UNI-17** — Layer-3 primitives audit. Add only if multi-line pattern recurs in ≥3 sites across ≥2 backends. Skipping is the expected answer.

- [ ] **EC-UNI-18** — table-driven dispatch where it earns its keep. x86's `g_sm_nullary`/`g_sm_arith` work; extend to JVM/NET/JS/WASM for nullary + arith only.

- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`). Mechanical patch + revert. Records LOC cost.

- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`). Mechanical patch + revert. Records LOC cost.

- [ ] **EC-UNI-21** — beauty.sno byte-identity gate matrix. `scripts/test_gate_ec_uni_complete.sh` runs all five gates + baseline md5 + M1 oracle md5 (`abfd19a7a834484a96e824851caee159`, currently drifted). Re-converge or formally retire M1.

- [ ] **EC-UNI-22** — close: update `ARCH-IR.md`, `ARCH-SCRIP.md`, invariant block to reflect three-layer cake + `g_emit`. Update four per-backend GOAL files. Mark EC-UNI complete; Phase B opens.

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
