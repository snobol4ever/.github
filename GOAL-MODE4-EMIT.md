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
mini-mode replaced by single enum + single global in `em_mode`. Two axes:
output format (TEXT vs BINARY vs MACRO_DEF) × wiring (WIRED vs BROKERED).
`TEXT_INLINE` folds into TEXT — `g_jit_emit_inline` becomes a text sub-flag,
not a mode value. `IS_TEXT` / `IS_BIN` / `IS_WIRED` / `IS_BROKERED` macros.

**Pure functional.** Every `insn_*` and `em_seq_*` function takes its inputs,
dispatches once, produces output, returns. No hidden state in logic.
Written so the Snocone/Icon bootstrap compiler can generate calls directly —
Icon tree-pattern-match an IR node, extract operands, call `insn_*`.
Snocone string-pattern on opcode names to dispatch to shape helpers.

**Composable naming.** Every name built from fragments that parallel across levels:
- Layer prefix: `insn_` (leaf), `em_seq_` (compound), `em_bb_` (BB template),
  `em_sm_` (SM template). No prefix = public API (called by walker/codegen).
- Operand shape suffix: `_rr` (reg←reg), `_ri` (reg←imm), `_rm` (reg←mem),
  `_rs` (reg←rip-sym), `_r` (single reg), `_0` (nullary).
- Size suffix where ambiguous: `_64`, `_32`, `_8`.
- BB box suffix: noun naming the box kind — `em_bb_lit`, `em_bb_pos`, `em_bb_stateful`.
- SM op suffix: opcode name — `em_sm_push_str`, `em_sm_store_var`.
- Seq suffix: what it computes — `em_seq_bounds_check`, `em_seq_sigma_delta`,
  `em_seq_port_call`.

**Coding patterns applied systematically:**
- *Table-driven dispatch* — 20 stateful BB boxes → `bb_box_def_t[]` table +
  one `em_bb_stateful()` driver. SM opcode families → shape-class table.
- *X-group macros* — sets of nearly-identical `insn_*` (jcc family, push/pop
  family) generated from a single `INSN_JCC(name, opcode)` macro invocation,
  keeping text+binary side-by-side without repetition.
- *Single-responsibility files* — each `.c` owns exactly one concern; no
  function defined in two files; no symbol split across files.
- *Helper extraction* — every duplicated 3-line pattern in compound helpers
  becomes a named `em_seq_*` function. Target: no compound helper body > 8 lines.

**`emit_sm_binary.c` is not an emitter.** It is a mode-3 C interpreter.
It stays in `src/runtime/x86/` but is excluded from all emitter file maps,
line counts, and rewrite steps. It is never touched by EM-REWRITE.

**File map: old → new**

| Old | New | Deleted at step |
|-----|-----|----------------|
| `emit_buf.c/h` | folded into `em_mode.c` | RW-6 |
| `emit_form.c/h` | `insn.c/h` + `em_mode.c` | RW-6 |
| `emit_insn.c/h` | `insn.c/h` | RW-6 |
| `emit_label.c/h` | `em_label.c/h` | RW-6 |
| `emit_text3c.c/h` | `em_text.c/h` | RW-6 |
| `emit_mode.c/h` | `em_mode.c/h` | RW-6 |
| `emit_bb_seq.c/h` | `em_seq.c/h` | RW-6 |
| `emit_bb_gen.h` | `em.h` (umbrella) | RW-6 |
| `emit_defs.h` | `em_defs.h` | RW-6 |
| `emit_bb_box.c` | `em_bb.c` | RW-3 |
| `emit_sm_op.c` | `em_sm.c` | RW-4 |
| `emit_sm_shape.c/h` | `em_sm.c` | RW-4 |
| `emit_templates.h` | `em_templates.h` | RW-4 |
| `emit_bb_flat.c/h` | `em_flat.c/h` | RW-5 |
| `emit_sm_text.c/h` | `em_walk.c/h` | RW-5 |
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
Fix: `bb_box_def_t[]` table + one `em_bb_stateful()` driver.

### EM-REWRITE steps

- [ ] **RW-0** ⚡ NEXT — Naming scan. Scan every function in all 16 emitter
  files (excluding `emit_sm_binary.c`). Produce canonical name table in
  `ARCH-EMITTER.md`: old name → new name, layer, operand-shape suffix, notes.
  Every subsequent step writes code using names from this table.
  No code changes. No callers changed.
  Deliverable: `ARCH-EMITTER.md` committed to `.github`.
  Gates: none (doc-only step).

- [ ] **RW-1** — Foundation layer: write alongside old code, no deletions.
  `em_mode.h/c`: single enum (TEXT/BINARY/MACRO_DEF) × wiring flag
  (WIRED/BROKERED). `IS_TEXT`/`IS_BIN`/`IS_WIRED`/`IS_BROKERED` macros.
  `g_jit_emit_inline` becomes `em_set_inline(int)` sub-flag on TEXT mode.
  `em_label.h/c`: all label symbols in one file (currently split across
  `emit_label.c` + `emit_form.c`). `em_text.h/c`: rewrite `emit_text3c.c`
  — pending-label/cjmp machinery, 4-col BB port format.
  `insn.h/insn.c`: all ~60 leaf functions with X-group macros for jcc/push/pop
  families. Each function: `if (IS_TEXT) { text; return; }` / binary below.
  ~180 lines total for `insn.c`. Old files still compiled, no callers changed.
  Gates: `gcc -c` clean, smoke 7/7 unchanged.

- [ ] **RW-2** — `em_seq.h/em_seq.c`: rewrite `emit_bb_seq.c` using only
  `insn_*`/`em_mode`/`em_label`/`em_text`. No if-statements — only calls.
  Every duplicated 3-line pattern becomes a named `em_seq_*` helper.
  No compound helper body > 8 lines. ~90 lines replaces ~660.
  Old `emit_bb_seq.c` still compiled alongside.
  Gates: `gcc -c` clean, smoke 7/7 unchanged.

- [ ] **RW-3** — `em_bb.c`: rewrite `emit_bb_box.c`. Table-driven stateful
  boxes (`bb_box_def_t[]` + `em_bb_stateful()` driver). No if-statements in
  any template function — only calls. Delete old `emit_bb_box.c`.
  ~80 lines replaces ~259.
  Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5.

- [ ] **RW-4** — `em_sm.c`: rewrite `emit_sm_op.c` + `emit_sm_shape.c`.
  One shape-class helper per SM opcode family; opcode families identified
  by shape (push-literal, push-var, binary-op, branch, call, etc).
  No if-statements in any template function. Delete old files.
  `em_templates.h` replaces `emit_templates.h`.
  Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5.

- [ ] **RW-5** — `em_flat.c/h`: rewrite `emit_bb_flat.c`. `em_walk.c/h`:
  rewrite `emit_sm_text.c`. Delete old files.
  Gates: full suite + `gcc -c` on all emitted artifacts.

- [ ] **RW-6** — Delete old foundation: `emit_insn.c`, `emit_form.c`,
  `emit_mode.c`, `emit_label.c`, `emit_text3c.c`, `emit_bb_seq.c`,
  `emit_buf.c`, `emit_bb_gen.h`, `emit_defs.h`.
  Umbrella `emit_bb_gen.h` → `em.h`. Update Makefile.
  Finalize `ARCH-EMITTER.md` with bootstrap notes for Snocone/Icon.
  Gates: full suite, `gcc -c` all artifacts, beauty ≥10.
- [ ] **EM-SNOCONE-PREP** — ESP-1..10: stale names, comments, dead code in emitter files. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.
- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13z (Claude Sonnet 4.6)**

one4all HEAD `d894c021`. .github HEAD `see push`. Gates: smoke 7/7, template-byte-id 4/4.

### What was done this session

- Full emitter scan (all 16 files, excluding `emit_sm_binary.c`).
- Diagnosed three diseases: 80× repeated mode switch; 2× text/binary duplication
  in compound helpers; 20 individually-written stateful BB boxes.
- Designed EM-REWRITE with Lon. Key decisions made and recorded:
  - `if (IS_TEXT)` at leaf only, never in template functions
  - Side-by-side text+binary: text branch on top, binary below, same function
  - Two-axis mode: format (TEXT/BINARY/MACRO_DEF) × wiring (WIRED/BROKERED);
    `TEXT_INLINE` folds into TEXT as a sub-flag, not a mode value
  - Composable naming: layer prefix + operand-shape suffix + size suffix
  - X-group macros for jcc/push/pop families (no repetition)
  - Table-driven stateful BB boxes: `bb_box_def_t[]` + `em_bb_stateful()`
  - SM opcode families dispatched by shape class, not individually
  - `emit_sm_binary.c` is NOT an emitter — excluded from rewrite entirely
  - Pure functional; Snocone/Icon bootstrap-friendly
- Projected: ~500 lines replaces ~2,400 in affected files (>2× reduction)
- Added RW-0 naming scan step (was missing — caught on review)
- Split overloaded old RW-4 into RW-4 (em_sm) + RW-5 (em_flat/em_walk) + RW-6 (delete)
- Updated PLAN.md

### Emitter file inventory (target after rewrite in parentheses)

| File | Lines | New | Target |
|---|---:|---|---:|
| emit_buf.h/c | 173 | → em_mode.c | folded |
| emit_defs.h/c | 58 | → em_defs.h | ~30 |
| emit_form.h/c | 445 | → insn.c/h | ~100 |
| emit_insn.h/c | 708 | → insn.c/h | ~180 |
| emit_label.h/c | 76 | → em_label.c/h | ~60 |
| emit_mode.h/c | 280 | → em_mode.c/h | ~80 |
| emit_text3c.h/c | 306 | → em_text.c/h | ~150 |
| emit_bb_gen.h | 24 | → em.h | ~20 |
| emit_templates.h | 212 | → em_templates.h | ~100 |
| emit_bb_seq.h/c | 660 | → em_seq.c/h | ~90 |
| emit_bb_box.c | 259 | → em_bb.c | ~80 |
| emit_bb_flat.h/c | 1241 | → em_flat.c/h | ~600 |
| emit_sm_shape.h/c | 904 | → em_sm.c | ~150 |
| emit_sm_op.c | 388 | → em_sm.c | (above) |
| emit_sm_text.h/c | 1763 | → em_walk.c/h | ~900 |
| emit_sm_binary.h/c | 1423 | **unchanged** | 1423 |

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md.
2. Confirm one4all HEAD `d894c021`. Gates: smoke 7/7, template-byte-id 4/4.
3. Current step: **RW-0** — naming scan. Read all 16 emitter files (exclude
   `emit_sm_binary.c`). Produce `ARCH-EMITTER.md` with full old→new name table,
   layer assignments, operand-shape suffixes. Commit to `.github`. No code changes.
