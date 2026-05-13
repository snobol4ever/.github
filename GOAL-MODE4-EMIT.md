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

- [ ] **RW-1** ⚡ NEXT — Foundation layer: write alongside old code, no deletions.
  `emit_mode.h/c`: single enum (TEXT/BINARY/MACRO_DEF) × wiring flag
  (WIRED/BROKERED). `IS_TEXT`/`IS_BIN`/`IS_WIRED`/`IS_BROKERED` macros.
  `g_jit_emit_inline` becomes `emit_set_inline(int)` sub-flag on TEXT mode.
  `emit_label.h/c`: all label symbols in one file (currently split across
  `emit_label.c` + `emit_form.c`). `emit_text.h/c`: rewrite `emit_text3c.c`
  — pending-label/cjmp machinery, 4-col BB port format.
  `insn.h/insn.c`: all ~60 leaf functions with X-group macros for jcc/push/pop
  families. Each function: `if (IS_TEXT) { text; return; }` / binary below.
  ~180 lines total for `insn.c`. Old files still compiled, no callers changed.
  Gates: `gcc -c` clean, smoke 7/7 unchanged.

- [ ] **RW-2** — `emit_seq.h/emit_seq.c`: rewrite `emit_bb_seq.c` using only
  `insn_*`/`emit_mode`/`emit_label`/`emit_text`. No if-statements — only calls.
  Every duplicated 3-line pattern becomes a named `emit_seq_*` helper.
  No compound helper body > 8 lines. ~90 lines replaces ~660.
  Old `emit_bb_seq.c` still compiled alongside.
  Gates: `gcc -c` clean, smoke 7/7 unchanged.

- [ ] **RW-3** — `emit_bb.c`: rewrite `emit_bb_box.c`. Table-driven stateful
  boxes (`bb_box_def_t[]` + `emit_bb_stateful()` driver). No if-statements in
  any template function — only calls. Delete old `emit_bb_box.c`.
  ~80 lines replaces ~259.
  Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5.

- [ ] **RW-4** — `emit_sm.c`: rewrite `emit_sm_op.c` + `emit_sm_shape.c`.
  One shape-class helper per SM opcode family; opcode families identified
  by shape (push-literal, push-var, binary-op, branch, call, etc).
  No if-statements in any template function. Delete old files.
  `emit_templates.h` replaces `emit_templates.h`.
  Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5.

- [ ] **RW-5** — `emit_flat.c/h`: rewrite `emit_bb_flat.c`. `emit_walk.c/h`:
  rewrite `emit_sm_text.c`. Delete old files.
  Gates: full suite + `gcc -c` on all emitted artifacts.

- [ ] **RW-6** — Delete old foundation: `emit_insn.c`, `emit_form.c`,
  `emit_mode.c`, `emit_label.c`, `emit_text3c.c`, `emit_bb_seq.c`,
  `emit_buf.c`, `emit_bb_gen.h`, `emit_defs.h`.
  Umbrella `emit_bb_gen.h` → `emit.h`. Update Makefile.
  Finalize `ARCH-EMITTER.md` with bootstrap notes for Snocone/Icon.
  Gates: full suite, `gcc -c` all artifacts, beauty ≥10.
- [ ] **EM-SNOCONE-PREP** — ESP-1..10: stale names, comments, dead code in emitter files. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.
- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13 (Claude Sonnet 4.6)**

one4all HEAD `7ad43ba3`. .github HEAD `567fc033`. Gates: template-byte-id 4/4.

### What was done this session

- Full source read of all 16 emitter files (excluding `emit_sm_binary.c`).
- Produced `ARCH-EMITTER.md`: complete old→new name table, sibling-consistent across all families.
- Key naming decisions:
  - `insn_` — leaf fns (one x86 instruction, IS_TEXT at top, binary below)
  - `emit_seq_` — compound sequences (L3); no if-statements in body
  - `emit_bb_` — BB box templates (L4); table-driven via `bb_box_def_t[]`
  - `emit_sm_op_` — SM opcode emitters; `emit_sm_shape_` — shape-class renderers
  - `emit_text_` — TEXT-only helpers; `emit_label_` — label lifecycle; `emit_mode_` — mode globals
  - `emit_flat_` — flat-glob builder; `emit_walk_` — text SM codegen walker
  - `IS_TEXT`/`IS_BIN`/`IS_WIRED`/`IS_BROKERED` macros replace scattered `bb_emit_mode` checks
  - `emit_sm_nullary_rt` (static) → absorbed into opcode dispatch table
  - `emit_add_delta_imm` / `emit_sub_delta_imm` → promoted to `insn_` layer (multi-insn but always-together)
  - `emit_pad_to_blob_size` deleted (no-op in all modes)
- Marked RW-0 complete in GOAL-MODE4-EMIT.md.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md.
2. Confirm one4all HEAD `7ad43ba3`. Gates: template-byte-id 4/4.
3. Current step: **RW-1** — Foundation layer: write `emit_mode.h/c`, `emit_label.h/c`,
   `emit_text.h/c`, `insn.h/insn.c` alongside old code. No deletions, no caller changes.
   Use names from ARCH-EMITTER.md exclusively.
