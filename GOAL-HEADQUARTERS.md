# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → fresh SM/BB lowering, never restore AST walk.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Single gate run at end of session.**
6. **Builder/consumer case rule.** UPPERCASE builds IR (`SM_*`, `BB_*`). lowercase consumes.
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary inside each `IS_<BE>` arm — never a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode calls `emit_mode_set(TEXT_MODE(), out)` at entry.
9. **One file per Byrd Box in `BB_templates/`.** Each in its own `bb_<name>.c`.
10. **Grouped templates allowed.** N opcodes sharing emit shape → single `sm_<group>()`/`bb_<group>()` with inner `switch(op)`. All emission stays in that TU. No external helpers.
11. **INLINE-ALL complete.** Every SM/BB code-gen path lives exclusively in `SM_templates/*.c` and `BB_templates/*.c`. Adding a backend = adding `IS_NEW` arms inside existing template files only.
12. **No shadow locals in templates.** Use `_.instr->`, `_.out`, `(int)_.instr->op` inline. Loop-counter locals and computed values are fine.
13. **Entry labels belong to their template.** Each XA/SM/BB template that begins a named asm block emits its own entry label on the first line. No separate `XA_PC_LABEL` opcode — the template owns its label.
14. **x86 only for BB template ladder — 2026-05-22 (Lon directive).** All new BB_ICN_* and BB_PL_* template bodies target x86 exclusively. IS_JVM/JS/NET/WASM arms are stubs. Non-x86 opens only when Lon directs.
15. **All code emission goes through the template system via an XA_* opcode — 2026-05-22 (Lon directive).** No C function emits asm outside an SM/BB/XA template. New code blocks get a new `XA_*` opcode in `XA.h` + `XA_templates/xa_<name>.c` + `xa_dispatch()`. Direct `fprintf`/`emit_textf` outside a template = violation.

## Session State (2026-05-23e)

**one4all HEAD: `88cb6fe2`** — SJ-1c: reverted SJ-1b-sweep's wrongful funnel conversion of IS_JS/IS_WASM arms (it had violated the x86-only directive — routed JS/WASM through asm funnels + sm_returns.c WASM_FNRET* macros, added spurious leading space, destroyed WASM 10-space indent, and changed sm_returns WASM bytes). Restored all JS/WASM arms to pre-sweep (336cb7e1) one-emit_textf-per-line form; restored js/wasm per-kind baselines from 336cb7e1; removed orphaned WASM_FNRET* macros. x86/JVM/NET funnel work preserved. 26 source files + 142 baseline cells. GATE-PK 419/0/635 NEW=0 GONE=0. GATE-M (11 misses) / GATE-E (gate1_beauty, gate4_icon) unchanged from f6b0be23 — pre-existing. ⛔ Beauty gate remains SUSPENDED (Lon directive 2026-05-23e: do not enable; snocone beauty self-host times out at 30s).

**Prior (2026-05-23d) one4all HEAD: `f6b0be23`** — SJ-1b-reindent: restored C source indentation in the 18 SM/BB/XA template files where SJ-1b-sweep split multi-line `emit_textf` blobs into per-line funnel calls but dropped leading whitespace. Brace-depth 4-space re-indent, whitespace-only. 18 files, 1448/1448. GATE-PK 419/0/635.

**Prior (2026-05-23c) one4all HEAD: `326a4fac`** — SJ-1b-sweep COMPLETE. All emit_textf in SM_templates (14 files), BB_templates (22 files), XA_templates (4 files) converted to emit_io funnels (x86/JVM/NET; JS and WASM untouched per Lon directive — ⚠ but in fact JS/WASM WERE wrongly touched; fixed in SJ-1c). Baselines refrozen. 593 files changed, 7679 ins / 6329 del.

**Gate: GATE-PK PASS=419 FAIL=0 STUB=635 ✅**

**STYLE-FUNNEL-ALL-ASM (SJ-1) STATUS:**
- ✅ SJ-1a funnels landed (`2ef4847f`)
- ✅ SJ-1b funnel rework + six-function API
- ✅ SJ-1b-sweep: ALL backends (x86/JVM/NET) routed through funnels; baselines refrozen

**NEXT:** ⚡ CPP — C++ conversion of the emitters (FIRST rung; start at CPP-0 build spike). Then STYLE-NO-SHADOW-LOCALS (SNS-1/2/3) or per Lon. (SJ-1c ✅ done — JS/WASM defunneled.)

## Active Rungs

### ⚡ CPP — C++ conversion of the emitters (FIRST / NEXT rung, 2026-05-23e Lon directive)

Convert all emitter source under `src/emitter/` (currently ~69 `.c` + 18 `.h`, pure C, gcc) to C++. This is now the **first active rung** of GOAL-HEADQUARTERS — do it before ISO and before resuming the STYLE steps.

**Why it's non-trivial:** the build is ONE linked program (`scrip`, 136 TUs via the Makefile's flat source list, `CC := gcc`). The emitter is not a standalone library — its TUs link directly against the C runtime / lower / processor. So this is not a per-file rename; it's: (a) make the emitter TUs compile as C++, (b) keep them linkable against the rest of the C program (extern "C" boundaries), (c) keep emitted bytes identical (GATE-PK 419/0/635 unchanged at every step).

**INVARIANT (overrides nothing, adds one):** the C++ conversion must be **byte-output-neutral**. GATE-PK 419/0/635 NEW=0 GONE=0 after every committed sub-step. No emitted asm/JS/WASM byte may change. This is a source-language migration, not a behavior change.

**Suggested sub-steps (next session refines; each atomic, gate-green):**
- [ ] **CPP-0 — build spike.** Add `CXX := g++` and a C++ compile path in the Makefile for emitter TUs only. Rename ONE leaf emitter file (e.g. `emit_io.c` → `emit_io.cpp`), wrap its header decls the rest of the C program calls in `extern "C"`, compile that one TU with g++, link whole program, GATE-PK 419/0/635. Proves the toolchain boundary before bulk work. ⚠ Decide: `.cpp` extension vs compile-`.c`-as-C++ flag — recommend real `.cpp` rename so the language is explicit. ⚠ Decide with Lon: full C++ (allow classes/templates later) vs "C-with-g++" (compile-clean C++ first, idiomatic later). Default assumption pending Lon: stage 1 = compile-clean as C++ only, NO idiom changes, byte-identical; idiomatic C++ (replacing the `_.instr->`/`IS_X86` macro layer, the emit funnels, the per-opcode dispatch) is a SEPARATE later rung.
- [ ] **CPP-1 — extern "C" surface.** Audit every emitter header included by non-emitter C TUs (`emit.h`, `emit_core.h`, `emit_sm.h`, `emit_bb.h`, `emit_io.h`, `emit_globals.h`, `emit_defs.h`, `emit_form.h`, `emit_templates.h`, `sil_macros.h`, `x86_opcodes.h`, `sm_codegen_x64_emit.h`). Add `#ifdef __cplusplus / extern "C" { ... }` guards so the C side links unchanged. GATE-PK green.
- [ ] **CPP-2 — bulk rename, leaves first.** Rename `BB_templates/*.c`, `SM_templates/*.c`, `XA_templates/*.c` → `.cpp` in waves (BB, then SM, then XA), updating the Makefile source list each wave. C++ is stricter than C: expect `void*`→typed-cast errors, implicit-int, designated-init order, `α/β` UTF-8 identifier handling, and the `_` template-context struct. Fix to compile-clean WITHOUT changing emitted bytes. GATE-PK green per wave.
- [ ] **CPP-3 — core + glue.** `emit_core.cpp`, `emit_sm.cpp`, `emit_bb.cpp`, `emit_globals.cpp`, `emit_io.cpp`, `sm_codegen_x64_emit.cpp`, `sm_emit_template.cpp`, the `test_*.c`, `demo_template_productions.c`. GATE-PK green; also run GATE-M / GATE-E to confirm no regression beyond the pre-existing (gate1_beauty SUSPENDED, gate4_icon).
- [ ] **CPP-4 — warnings clean.** Build emitter TUs with `-Wall -Wextra` under g++ with zero warnings. Commit.

**Gate for the whole rung:** GATE-PK 419/0/635 at every commit; full session-end GATE-M/GATE-E unchanged from `88cb6fe2` baseline (which has pre-existing GATE-M 11 misses, GATE-E gate1_beauty + gate4_icon). ⛔ Beauty gate stays SUSPENDED.

### ISO — parse→lower / parse→runtime firewalls

- [ ] **ISO-4** — `scrip_parse` subprocess: parsers in separate executable, stdin=source, stdout=TDump S-expression. Deserializer + roundtrip self-test first.
- [ ] ISO-5, ISO-6, ISO-7 — shrink firewall allowlists toward 0.

### STYLE steps

**SJ-1 design (2026-05-23, commit `2ef4847f`):** All line-by-line ASM emission routes through fixed-arity funnels in `emit_io.{c,h}`, replacing per-string indentation.

**SPACING MODEL (authoritative — Lon, 2026-05-23). Read this before touching funnels:**
- **Column 1 is where every line starts.** A JVM/asm line has up to four parts in order: **label, opcode, operands, comment**, with exactly ONE space between adjacent present parts.
- **Labels always sit at column 1, no leading space** — always have, unchanged.
- **The single leading space on an instruction line is the placeholder for an ABSENT label** — it keeps the opcode in the same column whether or not a label precedes it. `foo: aload_0` (label present, column 1) vs ` aload_0` (no label → one space holds the label's column).
- **Directives** (`.method`, `.limit`, `.field`, `.end method`, `.class`, `.super`, `.inner`) sit at column 1, no leading space — they have no label slot.
- So the funnels are NOT "always prepend a space." The leading space appears ONLY when the label slot is empty on an instruction line. ⚠ The current `2ef4847f` funnel impl hardcodes a leading space unconditionally and a separate `emit_Ndir` family — this is WRONG per the model above and MUST be reworked in SJ-1b: the label should be the first part (empty/NULL = emit one-space pad at column 1; present = emit label text at column 1), opcode/operands/comment follow with single spaces. Directives = no label slot, start at column 1. Do not carry forward the emit_Nasm-always-spaces / emit_Ndir split as if it were correct.

`emit_1asm..emit_4asm` join N pre-formatted parts. No printf formatting inside funnels — callers `snprintf` any `%`-interpolation first. Conversion = classify each emitted line into label/opcode/operands/comment and place each in its slot; operand strings keep internal spaces as a single part.

- [x] **STYLE-FUNNEL-ALL-ASM (SJ-1)** — ✅ SJ-1a funnels landed (`2ef4847f`). ✅ SJ-1b funnel rework + six-function API. ✅ SJ-1b-sweep COMPLETE (`326a4fac`): all x86/JVM/NET arms in SM/BB/XA templates route through funnels; JS/WASM untouched; baselines refrozen; GATE-PK 419/0/635.

- [x] **STYLE-JS-WASM-DEFUNNEL (SJ-1c)** — ✅ COMPLETE (`88cb6fe2`, 2026-05-23). Reverted SJ-1b-sweep's wrongful funnel conversion of IS_JS/IS_WASM arms (and sm_returns.c WASM_FNRET* macros) to pre-sweep one-emit_textf-per-line form; restored js/wasm baselines from 336cb7e1; removed orphaned macros. 26 source files + 142 baseline cells. GATE-PK 419/0/635. Decision taken: restored pre-sweep no-leading-space (JS/WASM have no label column). x86/JVM/NET funnel work preserved.

  **TARGET (the "nice" form):** every emitted JS or WASM line = exactly ONE `emit_textf` call ending in `\n`. One emit call per emitted line — no funnels, no multi-line `\n`-cramming. This is *also* cleaner than the PRE-sweep state (`336cb7e1`), where some JS arms packed 3+ `\n`-separated lines into a single `emit_textf` (e.g. `bb_pat_fence.c` JS arm had `"α()...,\\nβ()...\\n}; return self; }\\n"` in one call). Split those too: one line, one call.

  **SCOPE:** all `IS_JS` and `IS_WASM` arms in SM_templates / BB_templates / XA_templates. ~24 files contain contaminated funnel calls inside JS/WASM arms (per-file counts surveyed 2026-05-23d; xa_prologue.c 60, sm_arith.c 12, sm_calls.c 11, sm_push_pop_lits.c 8, bb_arbno.c 7, … down to bb_capture.c/xa_epilogue.c 2). Leave x86/JVM/NET funnel calls exactly as they are.

  **RECIPE (per file):**
  1. In each `if (IS_JS)` / `if (IS_WASM)` arm, replace every `emit_1asm/2asm/3asm/L*asm/emit_comment/emit_directive` call with a single `emit_textf("<exact line>\n", ...)` that reproduces the SAME emitted bytes. The funnels emit ` %s %s\n` (one leading space, single-space join) — so `emit_2asm("α()", "{ ... },")` currently emits ` α() { ... },\n`. Preserve those exact bytes in the `emit_textf` literal unless the byte output for JS/WASM should change — **decide leading-space policy with Lon** (JS/WASM previously had NO leading space pre-sweep; the funnels added one). If output bytes change, JS/WASM baselines must be refrozen.
  2. Also split any pre-existing multi-`\n` `emit_textf` blobs in those arms into one call per line.
  3. C source indentation: funnel-call lines in these arms were also slammed to col 0 by the sweep (SJ-1b-reindent `f6b0be23` fixed BB/SM/XA template indentation tree-wide, but verify JS/WASM arms read cleanly after rewrite).
  4. `make scrip`; GATE-PK must stay 419/0/635 (JS/WASM are STUB in the gate, so PASS unchanged; confirm NEW=0 GONE=0). If JS/WASM byte output intentionally changed, refreeze JS/WASM baselines per `scripts/freeze_per_kind_baseline.sh` and re-run.
  5. Commit per file or per backend (atomic). ⚠ OPEN DECISION FOR LON: leading-space policy on JS/WASM lines (keep sweep's added leading space, or restore pre-sweep no-leading-space). Default assumption pending Lon: restore pre-sweep no-leading-space, since JS/WASM have no label column.

  **FUNNEL API (authoritative, in `emit_io.{c,h}`):**
  - `emit_1asm(op)` / `emit_2asm(op,operand)` / `emit_3asm(op,operand,comment)` — UNLABELED instruction lines. One leading space holds the empty label column; opcode begins at the same column a labeled line's opcode would.
  - `emit_L1asm(label,op)` / `emit_L2asm(label,op,operand)` / `emit_L3asm(label,op,operand,comment)` — LABELED lines. Label (incl. trailing `:`) at column 1, one space, then the rest. The suffix counts parts AFTER the label (the `L` stands in for it), so `emit_1asm`/`emit_L1asm`, `emit_2asm`/`emit_L2asm` etc. line up — same part count past the label column.
  - `emit_directive(line)` (in `emit.h`) — ALL directive lines. Whole line, column 1, internal spaces verbatim (e.g. `.inner class ... outer ...`).
  - `emit_comment(line)` (in `emit.h`) — ALL comment/banner lines (e.g. `# BOX FOO()` GAS, `; ...` Jasmin). Whole line, column 1; caller supplies the marker.
  - Suffix number = count of REAL parts; `L` prefix = part 1 is a label. No NULL sentinels. Callers `snprintf` any `%`-interpolation (incl. building `label:`) into a local buffer first — funnels take final strings only.

  **SPACING (unchanged from model):** labels & directives at column 1; unlabeled instructions get exactly ONE leading space (the absent-label placeholder). This DOES reformat x86 (currently column-0 instructions → column-1) and JVM (currently 4-space → 1-space). Refreeze bakes the new spacing as standard.

  **SWEEP RECIPE (per backend, atomic — partial = red gate):**
  1. In each template arm for that backend, split every multi-line `emit_textf` blob into one funnel call per line. Classify each line: directive → `emit_directive`; comment/banner → `emit_comment`; labeled instruction → `emit_LNasm`; unlabeled instruction → `emit_Nasm`. Operand strings with internal spaces (type descriptors, `getfield a/b/c I`, `[rip + X]`) stay ONE part.
  2. For shared helpers that emit asm (the 6 `jvm_*` in `emit_core.c`: `jvm_push_int2`, `jvm_class_hdr`, `jvm_init_ms_only`, `jvm_init_ms_str`, `jvm_init_ms_int`, `jvm_val_helper`; plus `jvm_emit_ldc_string` leading-space fix), convert together with the arms — they ripple across all cells sharing them.
  3. `bash scripts/freeze_per_kind_baseline.sh` (wholesale; non-converted backends regenerate identical). 4. GATE-PK must return 419/0/635. 5. Commit. Then next backend.

  **PROVEN PILOT** (`bb_pat_abort` x86, this session, reverted to keep gate green):
  ```c
  char lbl_back_c[128]; snprintf(lbl_back_c, sizeof lbl_back_c, "%s:", lbl_back);
  emit_comment("# BOX ABORT()");
  emit_2asm("jmp", lbl_fail);              /*  jmp L_fail_audit            */
  emit_L2asm(lbl_back_c, "jmp", lbl_fail); /* L_back_audit: jmp L_fail_audit */
  ```
  Verified: only delta vs frozen baseline = the intended one-space pad. Order to do backends: x86 (reference) → JVM → NET → JS → WASM.
- [ ] **STYLE-CONCAT-BUILDER (SJ-2)** — Convert all SM/BB/XA template arms from funnel calls to C string concatenation, mirroring the future Snocone translation. **Rationale:** Snocone has the `.` concat operator; the right C intermediate is explicit string building (`" " . op . " " . operand . "\n"`) not fixed-arity funnels. The funnels (SJ-1) were the right intermediate to land clean spacing; SJ-2 replaces them with a single `emit_line(str)` primitive where `str` is built by concatenation. In C this means a variadic `scat(buf, sz, part1, part2, ..., NULL)` helper, so each template line reads `emit_line(scat(b, sz, " ", op, " ", operand, "\n", NULL))` — isomorphic to Snocone `emit(" " . op . " " . operand . "\n")`. **Gate:** GATE-PK 419/0/635 after refreeze. **Prereq:** SNS/STL/SOP/SCE/SNC complete (source clean before mechanical concat rewrite).
- [ ] **STYLE-NO-SHADOW-LOCALS (SNS-1/2/3)** — Remove `const SM_t *instr`/`FILE *out` aliases from sm_pat_combine, sm_calls, sm_jumps, sm_template_common.h.
- [ ] **STYLE-NO-TRANSFORM-LOCALS (STL-1..7)** — Inline trivial locals (`int sid=0`, `int lineno=`, `int val=`, etc.) across BB/SM templates.
- [ ] **STYLE-NO-OUT-PARAM (SOP-1..4)** — Remove `FILE *out` from all 20+ emitter helpers in `emit_core.c`; replace `fprintf(out,…)` with `emit_textf(…)`.
- [ ] **STYLE-SWITCH-TO-EXPR (SCE-1..7)** — Collapse name-only op switches to ternary/table in SM_templates.
- [ ] **STYLE-NO-COMMENTS (SNC-1..6)** — Remove all comments from SM_templates and BB_templates source.

## Gates

```
GATE-PK   bash scripts/test_per_kind_diff.sh          # PRIMARY — every change
GATE-M    bash scripts/test_gate_em_template_matrix.sh # session-end
GATE-E    bash scripts/test_gate_ec_uni_complete.sh    # session-end
GATE-J    bash scripts/test_crosscheck_icon.sh         # escalation
GATE-S    bash scripts/test_smoke_snobol4_jit.sh       # escalation
```
**⛔ BEAUTY GATE SUSPENDED** during BB template consolidation.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/one4all/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=419 FAIL=0 STUB=635
```

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) = reference. Mode 4 (`--compile`) emits wired x86.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
