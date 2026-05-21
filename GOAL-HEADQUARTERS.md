# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → fresh SM/BB lowering, never restore AST walk.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract. Never cross language-A SM-bridge with language-B BB object.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Three orthogonal constructs per session max**, separate commits, single gate run at end.
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
one4all: (this commit — beauty artifacts cleanup; prior c01ac05f retargeted beauty.sno paths)
corpus:  5fc1427    (deleted feature-rich stray demo/beauty.sno; prior be6f478 renamed beauty/ → beauty_suite/)
.github: 0236e579   (prior — GOAL-NET-BEAUTY-SELF note + 13(e) handoff)
smoke icon:    5/0    smoke prolog: 5/0    smoke rebus: 4/0
smoke raku:    5/0    smoke snobol4: 7/0    smoke snocone: 5/0
broker:        23/26
icon rungs:    194/36/35
matrix gate:   0/365 PASS
firewall lower:   9/6   firewall runtime: 16/8   firewall stage2: 10 (token gate)
beauty.sno --compile md5: 40df9e004c3e963c99af716c65f2c970  (882901 bytes, baseline 2026-05-20)
emit_io self-test: 6/6 PASS
unified-dispatch divergence: see EC-UNI-14-PREREQ — flipping `g_emit_use_unified_dispatch=1` produces non-equivalent output (beauty.s 188416 bytes md5 `8edb301a9a720f30b53709bd797fe2e8`; beauty.o md5 `bd090e88a02c24e47bf4e8d2390159d1` 132696 bytes vs legacy `3adbb73f88edcc5416d38baade6faf97` 494336 bytes). Flag stays default-OFF until PREREQ closes.
beauty.sno files in corpus: ONE — `programs/snobol4/demo/beauty/beauty.sno` (627 lines, md5 5be1de188af42be42e15e6d9a552f759, self-contained with 16 .inc includes per RULES.md line 912). Feature-rich stray at `programs/snobol4/demo/beauty.sno` deleted 2026-05-20 (corpus@5fc1427). Subsystem test apparatus at `programs/snobol4/beauty_suite/` (renamed from `programs/snobol4/beauty/` for clarity, corpus@be6f478).
```

---

## Active rungs

### EC-UNI — unify all walkers; one fn per opcode/kind, one arm per backend

**Target:** one fn per SM opcode, one fn per BB kind, each with five `if (IS_<BE>)` arms (X86/JVM/JS/NET/WASM). Text-vs-binary hides inside each arm. After completion, `emit_walk_codegen`/`emit_jvm_from_sm`/`emit_js_from_sm`/`emit_net_from_sm`/`emit_wasm_from_sm` all delete. "Fix backend X for opcode Y" becomes "open `sm_<y>.c`, edit the `IS_X` arm."

**End-state: three-layer cake.**

- **Layer 1 — Top-level templates** in `SM_templates/sm_<op>.c` / `BB_templates/bb_<kind>.c`. Signature `void sm_<op>(void)` / `void bb_<kind>(void)`. Reads `g_emit.*`. Branches ONLY on `IS_<BE>`. Verbose and explicit — the literal output strings are visible in every arm.
- **Layer 2 — Per-backend helpers** in the same file, file-scope `static`. Hides cross-mode logic (TEXT/BIN, body/method gates, fallbacks) — never formatting shortcuts. Extracted at EC-UNI-16, only where they hide real conditionals or de-duplicate ≥2-template computations.
- **Layer 3 — String-builder primitives** in `src/emitter/emit_io.{c,h}`: `emit_text`/`emit_textf`/`emit_byte`/`emit_bytes`. Funnel for all output.

**x86's lesson** (the correction): helper C functions like `emit_macro_begin`/`emit_mov_rdi_imm64`/`emit_call_sym_plt` hide what string lands in the output. JVM/JS/NET/WASM arms today emit `fprintf(out, "...")` directly — readable. New templates follow the readable style; helpers are extracted only at EC-UNI-16, with a sharp justification rule.

**The single global structure `g_emit`** (in `emit_globals.{c,h}`) carries all per-template state. `emit_program` sets fields per iteration. Not re-entrant. Snocone bootstrap maps `g_emit` 1:1 to a flat `DATA('Sm_emit(...)')` declaration.

**Verbose then reduce — the two-phase shape:** EC-UNI-13 collects (verbatim union of silo arms wrapped in `if (IS_<BE>)`); EC-UNI-15 makes the top-level shape uniform; EC-UNI-16 extracts Layer-2 helpers carefully. Extracting before the verbose form exists leads to today's x86 macro-soup.

**Scope inventory** (2026-05-20): SM has 76 opcodes touched by walkers, 52 templates exist (carrying IS_X86), ~20 to add. BB has 21 opcodes touched, 16 templates exist (PAT_*), 4 new (`BB_PL_ARITH/ATOM/BUILTIN/CALL`). Walkers delete after coverage lands: net −2500 to −3500 LOC.

**Unblocks Phase B:** five per-backend GOAL files (`GOAL-SN4-X86-EMIT` [new], `GOAL-SN4-JVM-EMIT`, `GOAL-SN4-JS-EMIT`, `GOAL-SN4-NET-EMIT`, `GOAL-SN4-WASM-EMIT`).

#### Completed sub-rungs (EC-UNI-10 onward)
- [x] EC-UNI-10(a/b/c) `7835fb9d`/`5e607294`/`3088dcba` — `g_emit` single global; templates parameterless; sm_ctx.h deleted.
- [x] EC-UNI-11 — Layer-3 `emit_io.{c,h}` scaffold (4 primitives + buffered/passthrough mode + 6/6 self-test).
- [x] EC-UNI-12 — mechanical `fprintf(out,...)` → `emit_textf(...)` sweep, 862 call sites across 26 template `.c` files.
- [x] EC-UNI-13(a) `106f26a2` — 16 PAT BB templates → `bb_pat.c` (byte-identical).
- [x] EC-UNI-13(b) `8514facf` — `SM_templates/sm_calls.c` (SM_CALL_FN + SM_SUSPEND_VALUE).
- [x] EC-UNI-13(c) `ab2888bf` — `SM_templates/sm_defines.c` (SM_DEFINE_ENTRY + SM_DEFINE).
- [x] EC-UNI-13(d) `498a2eed` 2026-05-20 — `SM_templates/sm_bb_calls.c` (SM_BB_ONCE_PROC + SM_BB_PUMP_PROC). IS_X86 arms call existing dispatchers (now public) as black boxes — `sm_bb_once_proc` routes to PJ-9c's rt_pl_once; `sm_bb_pump_proc` does the `g_stage2.proc_table[]` entry_pc lookup and emits `call .L<entry_pc>` via SM_CALL_EXPRESSION (IJ-HELLO-3). IS_JVM/JS/NET/WASM are honest no-op stubs matching today's `default: break;` fallthrough. Phase B will fill those arms when frontends emit these opcodes.
- [x] EC-UNI-13(e) `8c01a32c` 2026-05-20 — `BB_templates/bb_pl.c` with `bb_pl_arith`/`bb_pl_atom`/`bb_pl_builtin`/`bb_pl_call`. Honest no-op stubs across all five backends — no frontend lowers a Prolog BB graph to native today; Prolog execution is via `IR_exec_node` in `src/lower/ir_exec.c` (runtime path). Even the x86 arm is a no-op because no `emit_bb_pl_*_dispatch` helper exists in `emit_sm.c` to delegate to (the spec's pointer to "case BB_PL_*: arms in emit_sm.c" was stale — those labels live in the `pl_ir_kind_uses_sval` type-classification predicate only). Not wired into `emit_bb_node` switch — wiring no-op stubs would silently swallow the existing `; [emit_bb_node: kind=%d unhandled]` warning that today correctly flags these as unhandled-for-emission. Wiring happens in EC-UNI-14 alongside silo-walker deletions.

#### Open sub-rungs

- [ ] **EC-UNI-14-PREREQ (NEXT)** — close the divergence between `dispatch_one_x86` (template path, behind `g_emit_use_unified_dispatch`) and the legacy switch in `emit_walk_codegen`. Discovery 2026-05-20: flipping the flag default to ON produces beauty.sno output that is **not byte-identical** to baseline — neither at the .s level (882901 → 188416 bytes, md5 `40df9e0…` → `8edb301…`) nor after assembling (.o files 494336 vs 132696 bytes, different md5s). The HQ note on EC-UNI-3 ("Byte-identical by construction since both paths terminate at the same dispatcher fn") was an optimistic prediction, not a measured property. Real situation today: the template path emits a compact macro-name form (`PUSH_INT 178`, `CALL_FN .S28, 1`, `CONCAT`) while the legacy switch emits expanded x86 mov/call/push sequences inline; the assembler does macro expansion in the first case but **the two object files are still substantively different sizes**, so it's not just textual representation drift. **Open architectural question:** which output is canonical — macro-form short emission (relies on `sm_macros.s` expansion) or inlined-long emission (legacy switch)? Both assemble to something runnable; today only the legacy form is on the gate path. First sub-step: per-opcode diff sweep — for each of the 52 SM templates, generate both forms and record where they differ and why. Until this rung closes, EC-UNI-14 cannot land because flipping the flag breaks GATE-1. Owner: next session.

- [ ] **EC-UNI-14** — single dispatcher `emit_sm_dispatch(void)` in `emit_core.c`: one 91-arm switch on `g_emit.instr->op`, each calling `sm_<name>()`. Expand `emit_bb_node(void)` to all 21 BB kinds (includes wiring the four `bb_pl_*` from 13(e)). Delete `emit_walk_codegen`/`emit_jvm_one_instr`/`emit_js_from_sm`/`emit_net_from_sm`/`emit_wasm_from_sm`/`dispatch_one_x86` + ~30 `emit_sm_<op>_dispatch` helpers. Flip `SCRIP_UNIFIED_DISPATCH=1` to always-on, then delete the flag. Net LOC: −2500 to −3500. **BLOCKED on EC-UNI-14-PREREQ** — today's template path is not equivalent to today's legacy switch (2026-05-20 measurement). Either close the gap (each template emits exactly what the legacy switch emitted) or formally re-baseline the gate to a new canonical form before deleting silos. The "Beauty byte-identical" promise survives only after PREREQ resolves.

- [ ] **EC-UNI-15** — top-level shape: each template fn is a verbose `if (IS_<BE>)` five-arm switch, one screen per fn. Done family-by-family per RULES.md three-construct (one commit per family file). Multi-statement arms fine; no helper extraction yet.

- [ ] **EC-UNI-16** — REDUCE phase. Extract Layer-2 helpers, with rule: **justified iff carries a real conditional (IS_TEXT/IS_BIN, body/method gate, fallback) OR de-duplicates a non-trivial computation in ≥2 templates. String-concat shortening is NOT a reason.** Examples justified: `jvm_jump_to_pc(target)`, `jvm_ret_guard(op,sfx)`, `net_ret_guard(op)`. Examples NOT: `jvm_invokestatic(class,method,sig)` (hides one line), x86 `emit_macro_begin`-style wrappers.

- [ ] **EC-UNI-17** — Layer-3 primitives audit. Add a primitive only if the multi-line pattern recurs in ≥3 sites across ≥2 backends. Skipping is the expected answer.

- [ ] **EC-UNI-18** — table-driven dispatch where it earns its keep. x86's `g_sm_nullary`/`g_sm_arith` work; extend to JVM/NET/JS/WASM for nullary + arith only (per-op variation in calls/returns/jumps is real, not table-shaped). Tables become `DATA(...)` arrays in the Snocone bootstrap.

- [ ] **EC-UNI-19** — add-a-backend test (`EMIT_NULL=99`). Mechanical patch + revert. Records LOC cost of adding a backend.

- [ ] **EC-UNI-20** — add-an-opcode test (`SM_NOP`). Mechanical patch + revert. Records LOC cost of adding an opcode.

- [ ] **EC-UNI-21** — beauty.sno byte-identity gate matrix. Single script `scripts/test_gate_ec_uni_complete.sh` runs all five gates + baseline md5 + M1 oracle md5 (`abfd19a7a834484a96e824851caee159` 2026-04-28, currently drifted). Document divergence; either re-converge or formally retire M1.

- [ ] **EC-UNI-22** — close: update `ARCH-IR.md`, `ARCH-SCRIP.md`, invariant block to reflect three-layer cake + `g_emit`. Update four per-backend GOAL files to the new template ABI. Create `GOAL-SN4-X86-EMIT.md`. Mark EC-UNI complete; Phase B opens.

#### EC-UNI gate (every step from EC-UNI-10 on)

```
GATE-1  beauty.sno --compile  →  md5 40df9e004c3e963c99af716c65f2c970  (882901 bytes)
GATE-2  bash scripts/test_smoke_icon.sh                                  # PASS=5
GATE-3  bash scripts/test_smoke_unified_broker.sh                        # PASS≥23
GATE-4  bash scripts/test_icon_all_rungs.sh                              # PASS=194/36/35 (--interp by default; flag rejected)
GATE-5  bash scripts/test_smoke_{snobol4,snocone,prolog,rebus,raku}.sh   # 7/0 5/0 5/0 4/0 5/0
```

**Authors per RULES.md "Three-construct" exception (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.

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

**Authors per RULES.md "Three-construct" exception (Three-developer agreement, Milestone 1):** Lon Jones Cherryholmes · Claude Sonnet 4.7.
