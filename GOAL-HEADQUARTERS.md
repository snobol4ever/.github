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

## Session State (2026-05-23)

**one4all HEAD: `2ef4847f`** — SJ-1a funnel infrastructure landed (emit_Nasm/emit_Ndir). GREEK-BB-1..4 ✅ + EAO-13 ✅ (commit `db558a72`). EAO, EAO-CONT, GREEK-BB, PARAM-PASS rungs all complete and removed from this file.

**Gate entering next session: GATE-PK PASS=419 FAIL=0 STUB=635.** smoke_prolog 5/5.

**NEXT: SJ-1b** — atomic JVM backend conversion (24 template arms + 7 jvm_* helpers through the funnels), then refreeze JVM cells, GATE-PK.

## Active Rungs

### ISO — parse→lower / parse→runtime firewalls

- [ ] **ISO-4** — `scrip_parse` subprocess: parsers in separate executable, stdin=source, stdout=TDump S-expression. Deserializer + roundtrip self-test first.
- [ ] ISO-5, ISO-6, ISO-7 — shrink firewall allowlists toward 0.

### STYLE steps

**SJ-1 design (2026-05-23, commit `2ef4847f`):** All line-by-line ASM emission routes through fixed-arity funnels in `emit_io.{c,h}`, replacing per-string indentation. `emit_1asm..emit_4asm` = instruction lines (one leading space, one space between parts, newline). `emit_1dir..emit_3dir` = directive/label lines (column 1, no leading space, one space between parts). No printf formatting inside funnels — callers `snprintf` any `%`-interpolation first. Conversion = classify each emitted line into label/opcode/operands/comment and route accordingly; operand strings keep internal spaces as a single part. **Shared `jvm_*` helpers in `emit_core.c` (`jvm_class_hdr`, `jvm_init_ms_only`, `jvm_init_ms_str`, `jvm_init_ms_int`, `jvm_val_helper`) emit asm too and ripple across every cell that calls them — so the whole JVM backend (24 template arms + ~7 helpers) converts as ONE atomic unit, then `freeze_per_kind_baseline.sh` once.** Funnels are committed and inert; the sweep is the next step. Then x86, JS, NET, WASM backends, each atomic + refrozen.

- [ ] **STYLE-JVM-ONE-SPACE (SJ-1)** — ✅ SJ-1a funnels landed (`2ef4847f`). 🔄 SJ-1b: convert all 24 JVM template arms + 7 jvm_* helpers via funnels, refreeze JVM cells, GATE-PK. (Verified correct on bb_pat_fence pilot.)

  **SJ-1b execution recipe (do as ONE atomic commit — helpers ripple to 37 cells; partial = red gate):**
  1. Convert the 7 whole-line `jvm_*` helpers in `emit_core.c` to funnels (proven correct this session): `jvm_push_int2` (iconst_m1/iconst_N→emit_1asm; bipush/sipush/ldc N→emit_2asm), `jvm_class_hdr` (.class public bb/bb_<name>→emit_3dir; .super/.inner→emit_1dir), `jvm_init_ms_only`, `jvm_init_ms_str`, `jvm_init_ms_int` (.method/.limit→emit_dir; aload/invokespecial/putfield/return→emit_asm; putfield operand keeps internal-space type descriptor as one part), `jvm_val_helper` (label `<name>_val_static:`→**emit_1asm** [Lon directive 2026-05-23: labels use emit_1asm, NOT emit_dir]; invokeinterface ...getAsInt()I 1→emit_3asm). Escape-builder `jvm_emit_ldc_string`: ONLY fix leading `"    ldc \""`→`" ldc \""` (do NOT funnelize the char loop — it serializes operand payload, not line structure).
  2. Convert all 24 BB_templates JVM arms + ~20 SM_templates JVM arms: split each multi-line `emit_textf` blob into one funnel call per line; classify each line: **directives only** (.method/.limit/.field/.end method)→emit_Ndir (col 1); **labels AND instructions**→emit_Nasm (1 leading space) [Lon: labels are emit_1asm]; operand strings with internal spaces (type descriptors, `getfield a/b/c I`) stay ONE part.
  3. `bash scripts/freeze_per_kind_baseline.sh` (wholesale — safe once ALL jvm cells converted; non-jvm cells regenerate identical). 4. GATE-PK must return 419/0/635. 5. Commit. The 37 rippled cells: BB_PAT_{ABORT,ANY,ARB,BREAK,FENCE,LEN,NOTANY,POS,REM,SPAN,TAB} + SM_{ACOMP,CALL_FN,FRETURN*,LCOMP,NRETURN*,PAT_CAPTURE*,PAT_LIT,PAT_REFNAME,PAT_USERCALL*,PUSH_LIT*,PUSH_VAR,RETURN*,STNO,STORE_VAR,SUSPEND_VALUE}.
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
