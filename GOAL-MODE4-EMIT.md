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
- [~] **EM-BB-FORMAT** ⛔ SUPERSEDED by EM-REWRITE plan below. The 4-col format goal is absorbed into RW-4/RW-5.
- [ ] **EM-REWRITE** ⚡ NEXT — Full rewrite of the 16-file emitter subsystem. Multi-session plan below. **NEXT STEP: RW-1.**

### EM-REWRITE — Design invariants

**No if-statements in template functions (SM or BB) — only function calls.**
The single `if (IS_TEXT)` lives only inside `insn_*` leaf functions, nowhere above.

**Side-by-side text+binary in every leaf.** Each `insn_*` function has one
`if (IS_TEXT)` branch (text on top, return) and the binary encoding below.
Both sides are visible on adjacent lines — drift is impossible.

**One mode system.** The two parallel systems (`g_is_text` in `emit_form.c`
and `bb_emit_mode` everywhere else) plus the bolted-on `g_bb_emit_format`
third mini-mode are replaced by a single enum and single global in `em_mode`.

**Pure functional.** Every `insn_*` and `em_seq_*` function takes its inputs,
dispatches once, produces output, returns. No hidden state in logic.
Written so the Snocone/Icon bootstrap compiler can generate calls to it
directly — match an IR node, extract operands, call the named `insn_*`.
Naming is composable from operand-kind fragments (`_rr`, `_ri`, `_rm` etc).

**File map: old → new**

| Old | New | Deleted at step |
|-----|-----|----------------|
| `emit_buf.c/h` | folded into `em_mode.c` | RW-10 |
| `emit_form.c/h` | `insn.c/h` + `em_mode.c` | RW-10 |
| `emit_insn.c/h` | `insn.c/h` | RW-10 |
| `emit_label.c/h` | `em_label.c/h` | RW-10 |
| `emit_text3c.c/h` | `em_text.c/h` | RW-10 |
| `emit_mode.c/h` | `em_mode.c/h` | RW-10 |
| `emit_bb_seq.c/h` | `em_seq.c/h` | RW-10 |
| `emit_bb_box.c` | `em_bb.c` | RW-6 |
| `emit_sm_op.c` | `em_sm.c` | RW-7 |
| `emit_sm_shape.c/h` | `em_sm.c` | RW-7 |
| `emit_bb_flat.c/h` | `em_flat.c/h` | RW-8 |
| `emit_sm_text.c/h` | `em_walk.c/h` | RW-9 |
| `emit_bb_gen.h` | `em.h` (umbrella) | RW-10 |
| `emit_defs.h` | `em_defs.h` | RW-10 |
| `emit_templates.h` | `em_templates.h` | RW-7 |

### EM-REWRITE — Three diseases being cured

**Disease 1 — Mode switch repeated ~80 times.**
Every function switches on `bb_emit_mode` with 5 cases collapsing to 2.
Fix: `IS_TEXT` / `IS_BIN` macros in `em_mode.h`. One `if` at the leaf. Never above.

**Disease 2 — Text/binary parallel duplicated in every compound helper.**
`emit_bb_seq.c` writes every instruction twice — once as `bb3c_format(...)` and
once as `bb_insn_*()`. Functions are 2× longer than they need to be.
Fix: `insn_*` leaf unifies both. Compound helper calls it once. `em_seq.c` is
half the size of `emit_bb_seq.c`.

**Disease 3 — 20 stateful BB boxes written individually.**
Every `emit_bb_xbal`, `emit_bb_xfarb`, etc. is banner+alpha+beta_label+beta —
the same four calls with different names and state constructors.
Fix: one `bb_box_def_t` table + one `em_stateful()` driver. 20 wrappers → table rows.

### EM-REWRITE steps

- [ ] **RW-1** ⚡ NEXT — `insn.h / insn.c`: all ~60 leaf `insn_*` functions.
  Shape: `if (IS_TEXT) { text; return; }` / binary below. ~180 lines total.
  No callers changed. Old `emit_insn.c` + `emit_form.c` still compiled.
  Also write `em_mode.h / em_mode.c`: single enum, `IS_TEXT`/`IS_BIN` macros,
  replaces `g_is_text` + `bb_emit_mode` + `g_bb_emit_format`.
  Also write `em_label.h / em_label.c`: all label symbols in one file
  (currently split across `emit_label.c` + `emit_form.c`).
  Also write `em_text.h / em_text.c`: rewrite of `emit_text3c.c`.
  Gates: `gcc -c` clean, smoke 7/7 unchanged.

- [ ] **RW-2** — `em_seq.h / em_seq.c`: rewrite `emit_bb_seq.c` using only
  `insn_*` / `em_mode` / `em_label` / `em_text`. No if-statements — only calls.
  Three code paths collapse to one. ~90 lines replaces ~660.
  Old `emit_bb_seq.c` still compiled alongside.
  Gates: `gcc -c` clean, smoke 7/7 unchanged.

- [ ] **RW-3** — `em_bb.c`: rewrite `emit_bb_box.c`. Table-driven stateful boxes
  (`bb_box_def_t[]` + one `em_stateful()` driver). No if-statements in any
  template function. Delete old `emit_bb_box.c`. ~80 lines replaces ~259.
  Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5.

- [ ] **RW-4** — `em_sm.c`: rewrite `emit_sm_op.c` + `emit_sm_shape.c`.
  One shape-class helper per opcode family; no if-statements in templates.
  Delete old files. Update `emit_templates.h` → `em_templates.h`.
  Also rewrite `emit_bb_flat.c` → `em_flat.c` and `emit_sm_text.c` → `em_walk.c`.
  ~300 lines replaces ~1,292 + ~1,241 + ~1,763.
  Gates: full suite + `gcc -c` on emitted artifacts.

- [ ] **RW-5** — Delete old layer: `emit_insn.c`, `emit_form.c`, `emit_mode.c`,
  `emit_label.c`, `emit_text3c.c`, `emit_bb_seq.c`, `emit_buf.c`, `emit_bb_gen.h`,
  `emit_defs.h`. Umbrella `emit_bb_gen.h` → `em.h`. Update Makefile.
  Write `ARCH-EMITTER.md`: layer structure, naming conventions, IS_TEXT/IS_BIN
  pattern, Snocone/Icon bootstrap notes.
  Gates: full suite, `gcc -c` all artifacts, beauty ≥10.
- [ ] **EM-SNOCONE-PREP** — ESP-1..10: stale names, comments, dead code in emitter files. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.
- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13z (Claude Sonnet 4.6)**

one4all HEAD `d894c021`. .github HEAD `see push`. Gates: smoke 7/7, template-byte-id 4/4.

### What was done this session

- Full emitter scan (all 16 files excluding large SM/BB template files).
- Diagnosed three diseases: 80× repeated mode switch, 2× text/binary duplication
  in compound helpers, 20 individually-written stateful BB boxes.
- Designed EM-REWRITE with Lon: 5-session plan, old code stays live until cutover.
- Key invariants: no if-statements in template functions; one `if (IS_TEXT)` at
  leaf only; side-by-side text+binary; one mode system; pure functional;
  Snocone/Icon bootstrap-friendly composable naming.
- Projected: ~500 lines replaces ~2,400 lines in the affected files (>2× reduction).
- Consolidated 11-step plan into 5 steps. Wrote into this file. Updated PLAN.md.

### Emitter file inventory (8,920 lines total — target: ~5,000 after rewrite)

| File | Lines | New file | Target |
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
| emit_sm_binary.h/c | 1423 | unchanged | 1423 |

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md.
2. Confirm one4all HEAD `d894c021`. Gates: smoke 7/7, template-byte-id 4/4.
3. Current step: **RW-1** — write `em_mode.h/c`, `em_label.h/c`, `em_text.h/c`,
   `insn.h/insn.c` alongside old files. No callers changed.
   Gate: `gcc -c` clean, smoke 7/7 unchanged.
