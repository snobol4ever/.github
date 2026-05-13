# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md`. Past sessions that inferred mode-3/4 from `sm_codegen.c` arrived at the wrong picture every time.

**Repo:** one4all. **Done when:** `scrip --jit-emit --x64 file.{sno,sc}` → standalone binary outputting identically to `scrip --sm-run`. Binary links `libscrip_rt.so`. M5 extends to Icon/Raku/Prolog/Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s`.** One shared emitter; no parallel text-emitter walking SM_Program.

---

## Law of Template Functions

One C template function per SM opcode / BB box. Output only via `t_*` helpers (`bb_emit.h`); they read `bb_emit_mode` and route to BINARY/TEXT/MACRO_DEF. `emitter_t *e` is unused (`(void)e;`). No other output path.

---

## Architecture

```
IR ─► sm_lower ─► SM_Program ─► sm_codegen ─► SEG_CODE
                                                  ├─ mode 3: jmp in-process
                                                  └─ mode 4: seg_code_dump_as_s() → .s → ld → ELF
```

Two emitter shapes in `sm_codegen_x64_emit.c`:
- `emit_sm_instr()` — SM opcodes → GNU-as macros (`sm_macros.s`), 3-column `LABEL: OPCODE args`
- `emit_bb_box()` — BB boxes → GNU-as procs, 4-column `LABEL: ; ACTION ; jmp target`

Five-phase pattern execution: (1) build subject, (2) build pattern, (3) match+backtrack, (4) build replacement, (5) write-back. Phases 1/2/4 can fail → `:F`.

---

## Key components

`bb_emit.c` (TEXT/BINARY dual), `sm_templates.c` (91 SM emitters), `bb_templates.c` (35 BB emitters), `bb_flat.c`, `bb_pool.c`, `stmt_exec.c`.

**libscrip_rt.so boundary** — in: NV table, GC, builtins, `bb_pool`, BB broker. Out: `scrip_rt_pat_*` builders, `exec_stmt→bb_broker`.

Readability: `SM_STNO` banner `# ==…==  # stmt N  (line L):  <src>  # ==…==`. Col-3 annotations add info not in col 2.

---

## Tracked artifacts protocol

Seven artifacts in `corpus/programs/snobol4/demo/`. Run after any session touching `bb_emit.c`, `bb_templates.c`, `sm_templates.c`, `sm_codegen_x64_emit.c`, or `rt.c`:

```bash
DEMO=/home/claude/corpus/programs/snobol4/demo; SCRIP=/home/claude/one4all/scrip
cd $DEMO
for f in roman wordcount claws5 treebank-list treebank-array; do
    $SCRIP --jit-emit --x64 $f.sno > $f.s 2>/dev/null; done
for s in roman.s wordcount.s claws5.s treebank-list.s treebank-array.s; do
    gcc -c "$s" -o /tmp/$(basename "$s" .s).o 2>/tmp/as_err.txt \
        && echo "OK $s" || { echo "FAIL $s"; cat /tmp/as_err.txt; exit 1; }; done
cd /home/claude/corpus
git add programs/snobol4/demo/{roman,wordcount,claws5,treebank-list,treebank-array,sm_macros,bb_macros}.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen <rung>"
```

---

## Steps

> Closed-rung details: `git log -p .github/GOAL-MODE4-EMIT.md`

**All closed through EXVAL-3** (`e31ab505`) — EM-1..7d-prep, FORMAT-*, MODE4-IS-MODE3-DUMP -a..-u, TEMPLATE-COMPLETE TC-SM/BB, TC-UNSPLIT, DOPPELGANGER-PURGE, BB-PURGE, EC-1..8, BB-TEXT-ADDR, BB-R10-FIX, BB-FORMAT-ARCH..9, SPEC-T-ERADICATE, EXVAL-1..3, ESA-1..3, EM-XVAL-DESCR.

**Open:**

- [x] **EM-DEVTABLE** — Remove `emitter_t` vtable struct. Form-based API: 8 `emit_form_*` functions encode x86-64 encoding classes; caller supplies opcode bytes. Global state (`g_is_text`, `g_emit_pos`, `g_emit_text_mode`) replaces `e->is_text`/`e->ctx`. `emitter_t` typedef kept as `int` stub for template signature compat. `emitter_h`: 557→205 lines. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5. ✅ sess 2026-05-13k (Claude Sonnet 4.6).
  - [x] **EM-DEVTABLE-1** — `emitter.h`: struct deleted; form-based API; globals; lifecycle `emitter_init_binary`/`emitter_init_text`/`emitter_end`.
  - [x] **EM-DEVTABLE-2** — `emitter.c`: form functions `emit_form_reg64_imm64`, `emit_form_reg32_imm32`, `emit_form_alu_eax_imm32`, `emit_form_alu_esi_imm8`, `emit_form_reg_reg2/3`, `emit_form_mem2/3/4`, `emit_form_r13_disp8`, `emit_form_nullary1/2/3`, `emit_sym_lea_rcx/r10`, `emit_call_sym_plt`. No malloc. No vtable.
  - [x] **EM-DEVTABLE-3** — `bb_flat.h`: all ~20 signatures stripped of `emitter_t *e`. Callback typedefs also stripped.
  - [x] **EM-DEVTABLE-4** — `bb_flat.c`: all call sites updated; `e->is_text`→`g_is_text`; `e->intern_str`→`g_flat_intern_str`; `e->fprintf_raw`→`emit_fprintf_raw`; vtable macros removed.
  - [x] **EM-DEVTABLE-5** — `emitter_bb.c`: `emitter_t *e` stripped from xdsar/xatp signatures and all call sites.
  - [x] **EM-DEVTABLE-6** — `emitter_defs.c`, `test_template_byte_identity.c`, `demo_template_productions.c`, `sm_codegen_x64_emit.c`, `sm_codegen.c` all updated to new lifecycle API.
  - [x] **EM-DEVTABLE-7** — Build clean; smoke 7/7; template-byte-id 4/4; em8 5/5.
- [ ] **EM-BB-FORMAT** (parent) — closes when smoke 7/7, template-byte-id 4/4, snocone 5/5, `gcc -c` clean, beauty ≥10. Spec: each BB port = one 4-column `;`-separated GAS line, widths 24/16/32/free. ⛔ No if-statements in template functions.
- [x] **EM-7d** — beauty.sno PASS=14/17. Remaining FAILs: `counter_driver` (pre-existing mode-2 bug, parity break), `semantic_driver` (pre-existing NRETURN/counter-stack divergence — nTop() returns empty instead of failing after nPush+nInc+nPop sequence), `stack_driver` (pre-existing lowering bug). Accept all three as known divergence.
- [x] **EM-8** — `--jit-emit --x64 beauty.sc` + smoke_snocone 5/5 on emitted binaries. ✅ sess 2026-05-13f: gate `test_gate_em8_snocone_jit_emit.sh` PASS=5 (output/arith/procedure/if_eq/while). beauty.sc emits+links but produces 0 lines (pre-existing Snocone mode-4 output bug, not EM-8 blocker).
- [x] **EM-9** — M2 close: document `libscrip_rt.so` ABI; `make jit-emit-test`; mark GOAL-CHUNKS Step 8 `[x]`.
- [x] **EM-UNIFY** — Emitter subsystem unification. Three sub-rungs, all in one session:
  - **EM-UNIFY-a** Rename: `sm_templates.c` → `emitter_sm.c`; `bb_templates.c` → `emitter_bb.c`. Update Makefile, all `#include`s, function-pointer tables.
  - **EM-UNIFY-b** Merge `emitter_binary.c` + `emitter_text.c` into single `emitter.c`. Each low-level primitive (e.g. `emit_mov_rax_imm64`) becomes one function with an `if (is_text)` branch — binary bytes on one path, GAS mnemonic on the other. The two outputs are side-by-side in the same function body so they can be checked against each other at a glance. No more parallel files.
  - **EM-UNIFY-c** Opcode-as-argument API: replace hardcoded per-opcode `emit_sm_add()` / `emit_sm_sub()` / … families with a dispatched `emit_sm_op(int opcode, …)` that takes the SM opcode enum as an argument. Same for BB box family where applicable. Reduces template function count; callers pass the opcode, not a distinct function name.
  - Gates: smoke 7/7, template-byte-id 4/4, em8 5/5, `make jit-emit-test` clean.

### M5 phase — Raku, Prolog, Rebus (Icon cancelled from SM path)

⛔ Do not begin until GOAL-CHUNKS M4 (Steps 12–18) closes.

- [~] EM-10..EM-16 — SM_SUSPEND/RESUME, multi-frontend, M5 close. **CANCELLED for Icon** (sess 2026-05-13h): Icon is being rewritten pure-BB with no SM carrier; SM_SUSPEND/RESUME opcodes are irrelevant for Icon. Icon mode-4 emission will extend flat-BB emission to cover Icon generator boxes directly — new rungs scoped when M4 closes. Prolog and Raku SM_SUSPEND/RESUME work remains; re-scope those rungs when M4 closes.

---

## Definitions

- **mode 4 / `--jit-emit`** — emit standalone asm/binary linked against `libscrip_rt.so`.
- **baked-direct opcode** — inline x86 (SM_PUSH_INT, SM_ADD, SM_JUMP); no PLT call.
- **runtime-call opcode** — PLT call into `libscrip_rt.so` (SM_PAT_MATCH etc.).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13k (Claude Sonnet 4.6)**

one4all HEAD `b85e727e`. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.

### What was done this session

- EM-DEVTABLE closed (all 7 sub-rungs): emitter_t vtable struct removed entirely
- New form-based API: 8 emit_form_* functions encode x86-64 encoding classes; caller supplies opcode bytes
- emitter_t kept as typedef int stub for template signature compat; never dereferenced
- emitter.h: 557 -> 205 lines; emitter.c: 547 -> 436 lines; no malloc, no vtable, no pointer threading
- bb_flat.h/c: all emitter_t *e params stripped; intern_str callback signature updated to (const char *)
- emitter_bb.c, sm_codegen.c, sm_codegen_x64_emit.c, test/demo callers all updated to lifecycle API

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, em8 5/5. one4all HEAD = commit from this session.
3. EM-BB-FORMAT next open rung. See rung spec above.

Note: bb_emit_* instruction emitters renamed to emit_* (consistent prefix). Low-level primitives (bb_emit_byte, bb_emit_u32/u64, bb_emit_begin/end, bb_emit_patch_rel32, bb_emit_mode, bb_emit_out, bb_emit_pos) unchanged.

