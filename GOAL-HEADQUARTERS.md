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

## Session State (2026-05-23b)

**one4all HEAD: `7932a0d0`** — SJ-1b funnel rework landed. Six-function instruction-line API + emit_directive now match the SPACING MODEL (corrected two bugs: the `2ef4847f` unconditional-leading-space, then a double-space in the first NULL-sentinel rework). Pilot `bb_pat_abort` x86 arm verified byte-correct (only delta vs baseline = intended one-space pad) then reverted to keep gate green. No template arm calls the funnels yet on `main`.

**Gate entering next session: GATE-PK PASS=419 FAIL=0 STUB=635.** smoke_prolog 5/5.

**NEXT: SJ-1b-sweep** — route ALL ASM-type output (every backend, not just JVM — Lon directive 2026-05-23) through the funnels. ~1,168 `emit_textf` sites across 47 template files x 5 backends. Per-backend-atomic: convert one backend's arms fully, refreeze that backend's cells wholesale, GATE-PK 419/0/635, commit; then next backend. Start x86 (reference). The pilot pattern is proven — this is mechanical volume.

## Active Rungs

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

- [ ] **STYLE-FUNNEL-ALL-ASM (SJ-1)** — ✅ SJ-1a funnels landed (`2ef4847f`). ✅ SJ-1b funnel rework + six-function API (this session). 🔄 SJ-1b-sweep: route ALL backends' ASM through the funnels.

  **FUNNEL API (authoritative, in `emit_io.{c,h}`):**
  - `emit_1asm(op)` / `emit_2asm(op,operand)` / `emit_3asm(op,operand,comment)` — UNLABELED instruction lines. One leading space holds the empty label column; opcode begins at the same column a labeled line's opcode would.
  - `emit_L2asm(label,op)` / `emit_L3asm(label,op,operand)` / `emit_L4asm(label,op,operand,comment)` — LABELED lines. Label (incl. trailing `:`) at column 1, one space, then the rest.
  - `emit_directive(line)` (in `emit.h`) — ALL directive lines AND comment banners. Whole line, column 1, internal spaces verbatim. Use for any line with more tokens than the part slots (e.g. `.inner class ... outer ...`, `# BOX FOO()`).
  - Suffix number = count of REAL parts; `L` prefix = part 1 is a label. No NULL sentinels. Callers `snprintf` any `%`-interpolation (incl. building `label:`) into a local buffer first — funnels take final strings only.

  **SPACING (unchanged from model):** labels & directives at column 1; unlabeled instructions get exactly ONE leading space (the absent-label placeholder). This DOES reformat x86 (currently column-0 instructions → column-1) and JVM (currently 4-space → 1-space). Refreeze bakes the new spacing as standard.

  **SWEEP RECIPE (per backend, atomic — partial = red gate):**
  1. In each template arm for that backend, split every multi-line `emit_textf` blob into one funnel call per line. Classify each line: directive/banner → `emit_directive`; labeled instruction → `emit_LNasm`; unlabeled instruction → `emit_Nasm`. Operand strings with internal spaces (type descriptors, `getfield a/b/c I`, `[rip + X]`) stay ONE part.
  2. For shared helpers that emit asm (the 6 `jvm_*` in `emit_core.c`: `jvm_push_int2`, `jvm_class_hdr`, `jvm_init_ms_only`, `jvm_init_ms_str`, `jvm_init_ms_int`, `jvm_val_helper`; plus `jvm_emit_ldc_string` leading-space fix), convert together with the arms — they ripple across all cells sharing them.
  3. `bash scripts/freeze_per_kind_baseline.sh` (wholesale; non-converted backends regenerate identical). 4. GATE-PK must return 419/0/635. 5. Commit. Then next backend.

  **PROVEN PILOT** (`bb_pat_abort` x86, this session, reverted to keep gate green):
  ```c
  char lbl_back_c[128]; snprintf(lbl_back_c, sizeof lbl_back_c, "%s:", lbl_back);
  emit_directive("# BOX ABORT()");
  emit_2asm("jmp", lbl_fail);              /*  jmp L_fail_audit            */
  emit_L3asm(lbl_back_c, "jmp", lbl_fail); /* L_back_audit: jmp L_fail_audit */
  ```
  Verified: only delta vs frozen baseline = the intended one-space pad. Order to do backends: x86 (reference) → JVM → NET → JS → WASM.
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
