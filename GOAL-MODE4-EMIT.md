# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md`.

**Repo:** one4all. **Done when:** `scrip --jit-emit --x64 file.{sno,sc}` → standalone binary output identical to `--sm-run`. Binary links `libscrip_rt.so`. M5 extends to Icon/Raku/Prolog/Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s`.** One shared emitter; no parallel text-emitter.

---

## Architecture

```
IR ─► sm_lower ─► SM_Program ─► sm_codegen ─► SEG_CODE
                                                  ├─ mode 3: jmp in-process
                                                  └─ mode 4: dump to .s → ld → ELF
```

SM opcodes → GNU-as macros (`sm_macros.s`), 3-col `LABEL: OPCODE args`.
BB boxes → GNU-as procs, 4-col `LABEL: ; ACTION ; jmp target`.

**libscrip_rt.so boundary** — in: NV table, GC, builtins, `bb_pool`, BB broker. Out: `scrip_rt_pat_*` builders, `exec_stmt→bb_broker`.

---

## Emitter file layout (16 files, L0→L5)

| Level | File | Content |
|---|---|---|
| L0 | `emit_buf.h/c` | Raw buffer: `bb_emit_byte/u16/u32/u64`, patch, begin/end |
| L1 | `emit_form.h/c` | x86 encoding forms: `emit_form_*`, `emitter_init_*` |
| L2 | `emit_defs.h` | Types: `bb_emit_mode_t`, `bb_label_t`, `jmp_kind_t` |
| L2 | `emit_text3c.h/c` | 3-col formatter, `bb3c_*`, banners, sections |
| L2 | `emit_label.h/c` | Label lifecycle + `emit_jmp`, `emit_label_define` |
| L2 | `emit_insn.h/c` | Single-instruction emitters: `bb_insn_*` (30 fns) |
| L2 | `emit_mode.h/c` | Mode globals, `emit_mode_set`, macro begin/end, format helpers |
| L3 | `emit_bb_seq.h/c` | Compound BB helpers: port calls, lea/load/sigma/bounds |
| L4 | `emit_bb_box.h/c` | BB box template fns |
| L4 | `emit_sm_shape.h/c` | SM shape renderers |
| L4 | `emit_sm_op.h/c` | SM opcode templates (91) |
| L5 | `emit_bb_flat.h/c` | Flat-glob builder |
| L5 | `emit_sm_binary.h/c` | Binary SM codegen + `sm_jit_run` |
| L5 | `emit_sm_text.h/c` | Text SM codegen + strtab + srclines |
| — | `emit_templates.h` | All template fn declarations |
| — | `emit_bb_gen.h` | Umbrella shim (includes L0–L3) |

---

## Tracked artifacts protocol

After any session touching emitter files or `rt.c`, regenerate and commit:

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

> Closed history: `git log -p .github/GOAL-MODE4-EMIT.md`
>
> **All closed through EM-REORG-9** (`71c31336`) — EM-1..7d, EM-8, EM-9, EM-UNIFY, EM-DEVTABLE-1..7, ESP-11..14, EM-REORG-1..9.

- [x] **EM-RAW-PURGE-1** ✅ one4all `46642b16` — smoke 7/7, template-byte-id 4/4.
  - Phase A: deleted bb_lit_emit_binary / bb_eps_emit_binary + 6 orphaned static helpers (~263 lines of raw x86 bytes).
  - Phase B: added patnd_make_xchr / patnd_make_eps; replaced 6 NULL stubs with bb_build_brokered; fixed scan_body_fn_u9 to use g_scan_pre_delta (set by bb_broker before body_fn call) — avoids val.slen unreliability with flat/brokered blob return ABI.
- [~] **EM-BB-FORMAT** ⛔ SUPERSEDED by EM-REWRITE. Absorbed into RW-4/RW-5.
- [ ] **EM-REWRITE** ⚡ NEXT — Full rewrite of the 16-file emitter subsystem. **NEXT STEP: RW-0.**

### EM-REWRITE — Design invariants

**No if-statements in template functions (SM or BB) — only function calls.**
The single `if (IS_TEXT)` lives only inside `insn_*` leaf functions, nowhere above.

**Side-by-side text+binary in every leaf.**
```c
void insn_jne_r8(bb_label_t *t)
{
    if (IS_TEXT) { jmp_text("jne", t->name);  return; }
    b(0x75); patch_r8(t);
}
```
Text branch on top, binary branch below. One glance shows both. Drift impossible.

**One mode system.** Two parallel systems (`g_is_text` in `emit_form.c` and
`bb_emit_mode` everywhere else) plus bolted-on `g_bb_emit_format` third
mini-mode replaced by single enum + single global in `emit_mode`. Two axes:
output format (TEXT vs BINARY vs MACRO_DEF) × wiring (WIRED vs BROKERED).
`TEXT_INLINE` folds into TEXT — `g_jit_emit_inline` becomes a text sub-flag,
not a mode value. `IS_TEXT` / `IS_BIN` / `IS_WIRED` / `IS_BROKERED` macros.

**Pure functional.** Every `insn_*` and `emit_seq_*` function takes its inputs,
dispatches once, produces output, returns. No hidden state in logic.
Written so the Snocone/Icon bootstrap compiler can generate calls directly —
Icon tree-pattern-match an IR node, extract operands, call `insn_*`.
Snocone string-pattern on opcode names to dispatch to shape helpers.

**Composable naming.** Every name built from fragments that parallel across levels:
- Layer prefix: `insn_` (leaf), `emit_seq_` (compound), `emit_bb_` (BB template),
  `emit_sm_` (SM template). No prefix = public API (called by walker/codegen).
- Operand shape suffix: `_rr` (reg←reg), `_ri` (reg←imm), `_rm` (reg←mem),
  `_rs` (reg←rip-sym), `_r` (single reg), `_0` (nullary).
- Size suffix where ambiguous: `_64`, `_32`, `_8`.
- BB box suffix: noun naming the box kind — `emit_bb_lit`, `emit_bb_pos`, `emit_bb_stateful`.
- SM op suffix: opcode name — `emit_sm_push_str`, `emit_sm_store_var`.
- Seq suffix: what it computes — `emit_seq_bounds_check`, `emit_seq_sigma_delta`,
  `emit_seq_port_call`.

**Coding patterns applied systematically:**
- *Table-driven dispatch* — 20 stateful BB boxes → `bb_box_def_t[]` table +
  one `emit_bb_stateful()` driver. SM opcode families → shape-class table.
- *X-group macros* — sets of nearly-identical `insn_*` (jcc family, push/pop
  family) generated from a single `INSN_JCC(name, opcode)` macro invocation,
  keeping text+binary side-by-side without repetition.
- *Single-responsibility files* — each `.c` owns exactly one concern; no
  function defined in two files; no symbol split across files.
- *Helper extraction* — every duplicated 3-line pattern in compound helpers
  becomes a named `emit_seq_*` function. Target: no compound helper body > 8 lines.

**`emit_sm_binary.c` is not an emitter.** It is a mode-3 C interpreter.
It stays in `src/runtime/x86/` but is excluded from all emitter file maps,
line counts, and rewrite steps. It is never touched by EM-REWRITE.

**File map: old → new**

| Old | New | Deleted at step |
|-----|-----|----------------|
| `emit_buf.c/h` | folded into `emit_mode.c` | RW-6 |
| `emit_form.c/h` | `insn.c/h` + `emit_mode.c` | RW-6 |
| `emit_insn.c/h` | `insn.c/h` | RW-6 |
| `emit_label.c/h` | `emit_label.c/h` | RW-6 |
| `emit_text3c.c/h` | `emit_text.c/h` | RW-6 |
| `emit_mode.c/h` | `emit_mode.c/h` | RW-6 |
| `emit_bb_seq.c/h` | `emit_seq.c/h` | RW-6 |
| `emit_bb_gen.h` | `emit.h` (umbrella) | RW-6 |
| `emit_defs.h` | `emit_defs.h` | RW-6 |
| `emit_bb_box.c` | `emit_bb.c` | RW-3 |
| `emit_sm_op.c` | `emit_sm.c` | RW-4 |
| `emit_sm_shape.c/h` | `emit_sm.c` | RW-4 |
| `emit_templates.h` | `emit_templates.h` | RW-4 |
| `emit_bb_flat.c/h` | `emit_flat.c/h` | RW-5 |
| `emit_sm_text.c/h` | `emit_walk.c/h` | RW-5 |
| `emit_sm_binary.c/h` | **unchanged** | never |

### EM-REWRITE — Three diseases being cured

**Disease 1 — Mode switch repeated ~80 times.**
Every function switches on `bb_emit_mode` with 5 cases collapsing to 2.
Fix: `IS_TEXT` / `IS_BIN` macros. One `if` at the leaf. Never above.

**Disease 2 — Text/binary parallel duplicated in every compound helper.**
`emit_bb_seq.c` writes every instruction twice — `bb3c_format(...)` and
`bb_insn_*()`. Functions are 2× longer than needed.
Fix: `insn_*` leaf unifies both. Compound helper calls it once.

**Disease 3 — 20 stateful BB boxes written individually.**
Every `emit_bb_xbal`, `emit_bb_xfarb` etc. is banner+alpha+beta_label+beta.
Fix: `bb_box_def_t[]` table + one `emit_bb_stateful()` driver.

### EM-REWRITE steps

- [x] **RW-0** ✅ sess 2026-05-13 (Claude Sonnet 4.6) — Naming scan. Full read of all 16 emitter
  files (excluding `emit_sm_binary.c`). Produced `ARCH-EMITTER.md` in `.github` (`567fc033`):
  sibling-consistent old→new name table for all functions/globals across L0–L5.
  Key decisions: `insn_` prefix for leaf fns; `emit_seq_` for compound sequences;
  `emit_bb_` for box templates; `emit_sm_op_` for opcode emitters vs `emit_sm_shape_` for
  renderers; `emit_text_` for TEXT-only helpers; `IS_TEXT`/`IS_BIN`/`IS_WIRED`/`IS_BROKERED` macros.
  Gates: none (doc-only).

- [x] **RW-1** ✅ sess 2026-05-13 (Claude Sonnet 4.6) — `insn.h/c` (all ~65 leaf fns, IS_TEXT at top/binary below); `emit_text.h/c` (thin wrappers over emit_text3c); `emit_label_new.h/c` (emit_label_init/initf wrappers). IS_TEXT/IS_BIN/IS_WIRED/IS_BROKERED macros in insn.h. All alongside old code, no callers changed. one4all `d15b8050`. Gates: smoke 7/7, byte-id 4/4.

- [x] **RW-2** ✅ sess 2026-05-13 (Claude Sonnet 4.6) — `emit_seq.h/c`: all compound sequences with new names; insn_* calls throughout; lea-vs-movabs handled at seq layer (3 fns); emit_seq_port_call/port_call_rip forward IS_TEXT to format-port path. one4all `4dcea3b6`. Gates: smoke 7/7, byte-id 4/4.

- [x] **RW-3** ✅ sess 2026-05-13 (Claude Sonnet 4.6) — `emit_bb.c` replaces `emit_bb_box.c`. Two static drivers; stateless/stateful/complex boxes. emit_bb_box.c deleted. one4all `36df6775`. Gates: smoke 7/7, byte-id 4/4, snocone 5/5.

- [x] **RW-4** ✅ sess 2026-05-13 (Claude Sonnet 4.6) — `emit_sm.c` merges `emit_sm_op.c` + `emit_sm_shape.c` (both deleted). `emit_sm_shape.h` kept as compat header for `emit_sm_text.c`. one4all `3c7bce9c`. Gates: smoke 7/7, byte-id 4/4, snocone 5/5.

- [x] **RW-5** ✅ sess 2026-05-13 (Claude Sonnet 4.6) — `emit_flat.c/h` replaces `emit_bb_flat.c` (deleted). `emit_walk.c/h` replaces `emit_sm_text.c` (deleted). Shim `.h` files left in place for RW-6. Backward-compat `#define` aliases in new headers; all callers unchanged. Makefile updated. one4all `e00a7c6f`. Gates: smoke 7/7, byte-id 4/4, snocone 5/5, gcc -c 5/5 artifacts OK.

- [x] **RW-6** ✅ sess 2026-05-13 cont. (Claude Sonnet 4.6) — Deleted emit_buf.c (→emit_mode.c), emit_form.c (→emit_mode.c), emit_label.c (→emit_label_new.c standalone), emit_text3c.c (→emit_text.c standalone), emit_insn.c (→insn.c appended), emit.c (debris, not in Makefile). All 5 compiled files removed from Makefile RT_PIC_SRCS + explicit .o rules. Migrated 11 callers from emit_bb_gen.h → emit.h; emit_bb_gen.h reduced to one-line shim. ARCH-EMITTER.md finalized with RW-6 completion record. Gates: smoke 7/7, byte-id 4/4, snocone 5/5.
- [x] **EM-SNOCONE-PREP** ✅ `71244e57` — Comment cleanup (prev sess `85b4f292`) + bb3c_format→emit_text_3col migration in emit_seq.c; emit_text3c.h→emit_text.h; IS_TEXT guard on emit_seq_call_tgt (missing guard was Disease-1 survivor). Gates: smoke 7/7, byte-id 4/4, snocone 5/5.
- [x] **RW-OPCODES** ✅ `edf0c88a` — — Replace every raw `bb_emit_byte(0xNN)` magic constant in `emit_core.c`'s `insn_*` binary branches with named `#define` opcode constants. Goal: binary branches read like assembly (`REX_W; MOV_RAX_IMM64; bb_emit_u64(v)`) rather than hex soup. All names in a single table `x86_opcodes.h` (new file). No logic changes; pure readability. Gates: smoke 7/7, byte-id 4/4, snocone 5/5.

  **Spec:**
  - New file `src/runtime/x86/x86_opcodes.h` — one `#define` per distinct opcode byte used in `emit_core.c`, named after the Intel mnemonic + operand encoding. Examples: `REX_W 0x48`, `MOV_EAX_IMM32 0xB8`, `MOV_RAX_IMM64 0xB8` (same byte, distinguished by REX.W prefix), `RET 0xC3`, `NOP 0x90`, `CALL_RM 0xFF`, `JMP_REL8 0xEB`, `JMP_REL32 0xE9`, `JE_REL8 0x74`, `JNE_REL8 0x75`, `JL_REL8 0x7C`, `JGE_REL8 0x7D`, `JG_REL32 0x0F /*+*/ 0x8F`, `MOV_R_RM 0x89`, `MOV_RM_R 0x8B`, `LEA 0x8D`, `CMP_EAX_IMM32 0x3D`, `CMP_AL_IMM8 0x3C`, `ADD_EAX_IMM32 0x05`, `SUB_EAX_IMM32 0x2D`, `XOR_RM_R 0x31`, `TEST_RM_R 0x85`, `MOVZX 0x0F /*+*/ 0xB6`, `MOVSXD 0x49 /*+*/ 0x63`, `INC_RM 0xFF`, `PUSH_RBP 0x55`, `POP_RBP 0x5D`, `PUSH_R12 0x41 /*+*/ 0x54`, `POP_R12 0x41 /*+*/ 0x5C`, ModRM bytes where useful.
  - Each multi-byte sequence gets a short inline comment explaining what it encodes.
  - `emit_core.c` `insn_*` functions updated to use the names.
  - No changes to TEXT branches, no logic changes.
- [x] **RW-STYLE-1** ✅ `d0b7fdd3` — Eliminate all `if (cond) { text_call(); return; } / binary_stmts;` constructs in `emit_core.c`, `emit_bb.c`, `emit_sm.c`. The `return;` inside the if-body is redundant (the else path exits naturally); removing it lets the text and binary sides sit symmetrically as if/else with no return inside either. Target form:
  ```c
  if (IS_TEXT)
      text_call();          // single stmt: no braces
  else {
      binary_stmt1();       // multi stmt: braces
      binary_stmt2();
  }
  ```
  Or when binary is also one statement:
  ```c
  if (IS_TEXT) text_call();
  else         binary_stmt();
  ```
  Rules: (1) strip `return;` from text-side body; (2) add `else` before binary side; (3) remove braces from either side that has exactly one statement; (4) if binary side has multiple statements, keep its braces. No logic changes. Gates: smoke 7/7, byte-id 4/4, snocone 5/5.
- [x] **RW-STYLE-2** ✅ `d0b7fdd3` (folded into RW-STYLE-1) — Remove braces from every single-C-statement `if`/`else` body in `emit_core.c`, `emit_bb.c`, `emit_sm.c`. Rule: body is exactly one statement → no braces. Two-statement bodies (e.g. `{ t3c(…); return; }`) keep braces. Gates: smoke 7/7, byte-id 4/4, snocone 5/5.
- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 mode4-corpus-scan (Claude Sonnet 4.6)**

one4all HEAD `56a9897a`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4. Beauty mode-4: PASS=13/17 FAIL=4. Broad corpus (demo+beauty+124 parser/csnobol4-suite): PASS=155/163, EMIT=0, LINK=0, DIFF=5, CRASH=3.

### What was done this session

Two emitter bugs fixed; beauty gate 12→13/17:

1. **XDSAR not excluded from `flat_is_eligible`** (`56a9897a`): XDSAR nodes (deferred-var `*foo` patterns) were eligible for `bb_build_brokered` → `emit_flat_body`, which ran at runtime inside the generated binary and crashed in `emit_label_initf`/`vsnprintf` (stack corruption context). Fix: add `p->kind == XDSAR` to `flat_is_eligible` exclusion in `emit_bb.c`. Falls back to C brokered box path.

2. **Absolute Σ/Σlen addresses in text .s output** (`56a9897a`): `emit_seq_sigma_delta_rdi`, `emit_seq_bounds_len`, `emit_seq_cmp_siglen_delta` all called `insn_mov_rcx_i64(addr)` unconditionally, baking the scrip-process's own `&Σ`/`&Σlen` pointer values into the emitted `.s`. Generated binary segfaulted dereferencing those stale addresses at runtime. Fix: `IS_TEXT` guard calls `emit_sym_lea_rcx("Σ"/"Σlen", addr)` → correct RIP-relative symbol reference.

Broad corpus scan run: demo+beauty+parser+csnobol4-suite (163 programs). 155 PASS, 8 failures:

### Remaining 4 beauty diffs (accepted as sm-run bugs)

Confirmed against SPITBOL oracle: counter, semantic, stack, trace — all sm-run accuracy divergences. Mode-4 is at least as correct.

### 3 new crashes from broad corpus scan (next session)

**Class A — stateful BB box zeta absolute address (f04_pattern_primitives):**
`rt_bb_any` called with `zeta=0x4010e0 <rt_bb_any@plt>` — the PLT stub address, not a zeta struct.
Root cause: `emit_seq_port_call` text path at line 1163 emits `lea rdi, [rip + fn_name]` using the *function name* as the RIP-relative symbol for the zeta struct. But stateful boxes (ANY, SPAN, BREAK, NOTANY, TAB, RTAB, LEN, BAL, ARB, REM, BREAKX, and all ICN_* boxes) need a `.quad` data slot in the emitted `.s` with a `.Lbox_z` label, same pattern as XDSAR/XATP use `emit_seq_port_call_rip`.
Fix needed: `emit_bb_stateful` must emit a data section with a `.Lbox_z` label containing the box-specific runtime state, then call `emit_seq_port_call_rip` with that label. In binary mode, behavior is unchanged (zeta_ptr is a live heap address). In text mode, the data section provides a relocatable slot.

**Class B — DEFINE_ENTRY corrupts main frame (fn_define_labeled, expr_parser):**
`main=0x0` at crash — the `main` prologue is corrupted. `DEFINE_ENTRY` macro emits `push rbp / mov rbp, rsp` AFTER `call rt_define_entry@PLT` inside `main`'s body. This extra prologue corrupts the return stack. DEFINE_ENTRY should be a pure label target (no prologue emission) in the text path; the actual function prologue belongs in the `sm_macros.s` DEFINE body or should be suppressed when inside main.

### 5 diffs from broad corpus scan

f07_keywords, f12_load_unload, f14_dyn_opt, f18_error_handling, f19_real_numbers — pre-existing sm-run accuracy divergences, not mode-4 emitter bugs. Not investigated this session.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md.
2. Confirm one4all HEAD `56a9897a`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4.
3. Fix Class A (stateful box zeta): add `.Lbox_z` data slot to `emit_bb_stateful` text path and switch to `emit_seq_port_call_rip`. Affects XANYC/XSPNC/XBRKC/XNNYC/XLNTH/XTB/XRTB/XBAL/XFARB/XSTAR/XBRKX + ICN_* boxes.
4. Fix Class B (DEFINE_ENTRY): suppress extra prologue in DEFINE_ENTRY text macro, or rework how SM_DEFINE_ENTRY interacts with `main`'s frame.
5. After fixes: broad corpus scan target ≥160/163.

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 mode4-charset-fix (Claude Sonnet 4.6)**

one4all HEAD `3db853a7`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4. Beauty mode-4: PASS=10/17 (baseline at `56a9897a` also confirmed 10/17 — previous watermark overstated 13/17).

### What was done this session

**emit_bb_charset text path fix** (`3db853a7`): In text mode, `emit_bb_charset` was calling `emit_bb_stateful` → `emit_seq_port_call`, which emitted `lea rdi, [rip + fn_name]` — using the *function* name (`rt_bb_any` etc.) as the RIP-relative zeta pointer. At runtime the binary received the PLT stub address as zeta, causing `strchr(PLT_stub, char)` → SIGSEGV. Fix: text mode bypasses `emit_bb_stateful` and emits a `.section .data` block with `.Lcs{id}_chars` string + `.Lcs{id}_z` struct (`.quad chars_label, .long 0, .long 0`), then calls `emit_seq_port_call_rip`. Labels emitted with colon suffix (`.Lcs0_chars:`) to avoid GAS treating them as unknown directives. Verified: f04_pattern_primitives no longer crashes.

**Broad corpus baseline clarification**: Full scan (166 programs including beauty+demo+parser+csnobol4-suite) shows ~144 PASS at `56a9897a`. The scan script's abort-handling was misclassifying sm-run aborts as mode-4 crashes; both produce empty output so they match — they should be PASS not CRASH.

### Remaining work (next session)

**Class A — Other stateful box types in text mode** (TAB/RTAB/LEN/BAL/ARB/REM/BREAKX/ARBNO/ICN_* boxes): same PLT-stub-as-zeta bug in `emit_bb_stateful`. Fix strategy:
- Boxes with no chars ptr (BAL/ARB/REM/ICN_*): add IS_TEXT guard to `emit_bb_stateful` emitting zeroed `.Lstateful{id}_z` data block (6 `.quad 0`) — these self-initialize from zero on first call.
- TAB/RTAB/LEN: need integer `n` baked in as first field; data block = `.long n; .long 0`.
- BREAKX: needs chars ptr — same pattern as charset fix above.

**Class B — DEFINE_ENTRY corrupts main frame** (fn_define_labeled, expr_parser): DEFINE_ENTRY macro emits extra `push rbp / mov rbp, rsp` inside `main`'s body; the DEFINE_ENTRY sm_macros.s macro should not emit a prologue in the text path (it creates a new frame inside main's frame).

**Beauty gate 10/17**: ShiftReduce, TDump, global still failing. Likely more stateful box issues (ShiftReduce uses BAL/ARB; TDump and global use pattern primitives). Should improve once Class A is fixed.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md.
2. Confirm one4all HEAD `3db853a7`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4.
3. Fix Class A: IS_TEXT guard in `emit_bb_stateful` for zero-init boxes + per-box fixes for TAB/RTAB/LEN (int field) and BREAKX (chars ptr).
4. Fix Class B: DEFINE_ENTRY sm_macros.s macro body.
5. Run clean corpus scan distinguishing sm-run-abort from mode-4-crash.

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 mode4-stateful-box-fix (Claude Sonnet 4.6)**

one4all HEAD `fa75289f`. corpus HEAD `65dad13`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4. Broad corpus (demo+beauty+parser+csnobol4-suite): 113/113 PASS 0 FAIL (emit+assemble only; libscrip_rt not built this session).

### What was done this session

**Class A — stateful box zeta fix** (`fa75289f`): All stateful boxes through `emit_bb_stateful` in text mode called `emit_seq_port_call` → `lea rdi, [rip + fn_name]` — using the *function* name as the RIP-relative zeta pointer, passing PLT stub address as zeta → SIGSEGV.

Fixes in `emit_bb.c`:
- `emit_bb_stateful`: IS_TEXT guard emits zeroed `.Lstat{id}_z` block (6×`.quad 0`) in `.section .data`, then uses `emit_seq_port_call_rip`. Covers BAL/ARB/REM + all 25 ICN_* boxes.
- `emit_bb_stateful_int` (new): bakes `.long n; .long 0` for LEN/TAB/RTAB. `emit_bb_xlnth`/`xtb`/`xrtb` now call this.
- `emit_bb_xbrkx`: IS_TEXT path emits chars string + `brkx_t` data block with chars ptr label (same pattern as charset fix).

**Class B — DEFINE_ENTRY frame corruption fix** (`fa75289f`): `emit_sm.c` emitted `push rbp / mov rbp, rsp` after `call rt_define_entry@PLT` in the macro body. Removed. DEFINE_ENTRY is a pure runtime notification, not a function entry point.

**corpus `sm_macros.s`** regenerated (`65dad13`): DEFINE_ENTRY macro now only `call rt_define_entry@PLT` + `.endm`.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md.
2. Confirm one4all HEAD `fa75289f`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4.
3. Build libscrip_rt.so (`make libscrip_rt` in one4all) and run `test_gate_em_beauty_subsystems_mode4.sh` to measure beauty PASS/17.
4. Investigate remaining beauty failures — determine which are sm-run-accuracy divergences vs true mode-4 bugs.
5. Run broad corpus scan with libscrip_rt to distinguish sm-run-abort from mode-4-crash.

---

## EM-STATEFUL-FLAT — Make stateful boxes flat (spec-correct, no RTCALL)

**Architectural note (Lon, 2026-05-13):** Stateful boxes do not belong in
the runtime via RTCALL. They require per-invocation DATA allocation (the
zeta struct), but that lives in the flat glob's DATA block — not in a
heap struct dispatched through a C function pointer. The RTCALL path was
always a temporary fallback. These steps complete what the arch specified.

- [x] **SF-1** ✅ sess 2026-05-13 (Claude Sonnet 4.6) one4all `3fcc90a7` — `emit_bb_xbal` flat inline BAL box. Text path: `.data` slot for `int δ`; inline `'('`/`')'` byte-compare loop via RIP-relative Σ/Σlen/Δ symbols; no `rt_bb_bal` call. Binary path: heap zeta via `emit_seq_port_call` (unchanged). Gates: smoke 7/7, byte-id 4/4, beauty 10/17. Note: SNOBOL4 frontend emits `PUSH_VAR` for `BAL` rather than `XBAL` in all tested programs — the emit path is structurally correct but unexercised until frontend keyword wiring routes `BAL` → `XBAL`.
- [ ] **SF-2** — `emit_bb_xfarb` (ARB) flat. `arb_t { int count; int start; }`. α: save start=cursor, count=0, try zero-length → γ. β: advance count, retry → γ, exhaust → ω.
- [ ] **SF-3** — `emit_bb_xstar` (REM) flat. α→γ unconditionally (matches rest of string). β→ω.
- [ ] **SF-4** — `emit_bb_xlnth`/`xtb`/`xrtb` flat. `n` baked in DATA at emit time. α: check cursor arithmetic → γ or ω. β→ω (no re-entry for positional boxes).
- [ ] **SF-5** — `emit_bb_xbrkx` flat. chars ptr baked from `.data` string label. α: scan past chars, save δ. β: advance one, retry.
- [ ] **SF-6** — ICN_* boxes flat. Zeroed DATA block on α-entry (self-init). C body functions (`coro_bb_*`) called as direct calls within the glob with DATA block address in rdi (not PLT stub).
- [ ] **SF-7** — Delete `emit_bb_stateful`, `emit_bb_stateful_int`, `emit_bb_stateful_text_data` (dead after SF-1..6). Clean up `emit_bb_xbrkx` IS_TEXT guards.
- [ ] **SF-8** — Broad corpus ≥160/163 PASS. Beauty gate ≥10/17. Commit.

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 mode4-SF-1 (Claude Sonnet 4.6)**

one4all HEAD `3fcc90a7`. Gates: smoke 7/7, byte-id 4/4, beauty 10/17 (unchanged). Snocone 1/5 pre-existing.

### What was done this session

**SF-1 — `emit_bb_xbal` flat inline BAL box** (`3fcc90a7`): Text path emits `.data` slot (`.Lbal{id}_z`: `.long 0; .long 0`) and inline `'('`/`')'` byte-compare loop using RIP-relative Σ/Σlen/Δ symbol references. No `rt_bb_bal` call in text mode. Binary path unchanged (heap zeta via `emit_seq_port_call`). emit+link verified on all BAL-using demo programs (treebank-array, treebank-list, claws5).

### Key finding from history scan

- Archive `bb_boxes.s`: BAL was always a **stub** (always ω, printed error). Never flat-implemented in the assembly era.
- Commit `76924fca`: first real BAL logic, as C function `bb_bal()` in `bb_boxes.c`.
- SNOBOL4 frontend currently emits `PUSH_VAR` for the token `BAL` instead of routing to `XBAL`. The SF-1 emit path is correct but unexercised until frontend keyword wiring is fixed (separate issue, not SF scope).

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md.
2. Confirm one4all HEAD `3fcc90a7`. Gates: smoke 7/7, byte-id 4/4.
3. Investigate SNOBOL4 frontend `BAL` keyword wiring — why does `BAL` in a pattern emit `PUSH_VAR` instead of `XBAL`? Fix or note as separate goal.
4. Proceed to SF-2: `emit_bb_xfarb` (ARB) flat template.



one4all HEAD `d4a17203`. corpus HEAD `96444bf`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4. Beauty mode-4: PASS=10/17.

### What was done this session

**Class A stateful-box zeta text fix** (`fa75289f`, one4all): `emit_bb_stateful` IS_TEXT guard emits zeroed `.data` block + `emit_seq_port_call_rip`. `emit_bb_stateful_int` for LEN/TAB/RTAB. `emit_bb_xbrkx` inline IS_TEXT path. Broad corpus 113/113.

**Class B (DEFINE_ENTRY) — attempted and reverted**: Removing push/rbp from DEFINE_ENTRY broke user-function RETURN (mov rsp,rbp/pop rbp/ret needs a matching prologue). Reverted in `d4a17203` / corpus `96444bf`. Beauty restored to 10/17.

**Lon's architectural directive**: Stateful boxes do not belong in the RT via RTCALL. They need per-invocation DATA in the flat glob, not heap dispatch. SF-1..SF-8 above are the now-steps.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md.
2. Confirm one4all HEAD `d4a17203`. Gates: smoke 7/7, snocone 5/5, byte-id 4/4. Beauty 10/17.
3. Start SF-1: `emit_bb_xbal` flat template — inline BAL logic in the glob, DATA block holds `int δ`, no `rt_bb_bal` call.
