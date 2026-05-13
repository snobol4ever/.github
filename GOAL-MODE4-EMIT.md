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

- [ ] **EM-RAW-PURGE-1** ⚡ NEXT — ⛔ PHASE A DONE, PHASE B NEEDED. Build broken (smoke 5/7, template-byte-id 3/4). one4all `10796587`.
  - **Phase A complete (this session):** deleted `bb_lit_emit_binary`, `bb_eps_emit_binary`, `emit_descr_fail`, `emit_load_int_global/ptr/add/sub`, `emit_descr_success_from_stack`, `bb_build_binary_node` fwd decl, `bb_build_binary` dead decl, `#include emit_bb_flat.h` from stmt_exec.c. All ~263 lines of raw-byte code gone.
  - **Phase B (next session):** 6 NULL stubs in `stmt_exec.c` must be replaced with `patnd_make_xchr(s)` / `patnd_make_eps()` + `bb_build_flat()` (fallback `bb_build_brokered()`). Add `patnd_make_xchr` / `patnd_make_eps` to `snobol4_patnd.h` + `snobol4_pattern.c` (GC_MALLOC, set kind=XCHR/XEPS, set STRVAL_fn for XCHR). Search `stmt_exec.c` for `TODO Phase B`.
  - ⚠️ `bb_build_flat` returns NULL if `flat_is_eligible` fails — always fall through to `bb_build_brokered`. Mirror null-check pattern at stmt_exec.c line ~845.
  - ⚠️ `bb_build_brokered` still has raw prologue bytes (0x55, 0x48 0x89 0xE5 = push rbp / mov rbp,rsp) — replace with `emit_brokered_prologue()` call. This is also Phase B.
- [ ] **EM-BB-FORMAT** — each BB port = one 4-column `;`-separated GAS line, widths 24/16/32/free. ⛔ No if-statements in template functions. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, `gcc -c` clean, beauty ≥10.
- [ ] **EM-REWRITE** ⏳ HELD — Full rewrite of the 16-file emitter subsystem. Held until Lon signs off. Gates TBD at sign-off.
- [ ] **EM-SNOCONE-PREP** — ESP-1..10: stale names, comments, dead code in emitter files. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.
- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13v (Claude Sonnet 4.6)**

one4all HEAD `10796587` ⛔ BROKEN — smoke 5/7, template-byte-id 3/4. Phase B of EM-RAW-PURGE-1 not yet done.

### What was done this session

- Full scan of source base for raw x86 byte emission outside the template system.
- **Phase A of EM-RAW-PURGE-1:** Deleted all raw-byte emitter code (~263 lines):
  - `bb_lit_emit_binary` and `bb_eps_emit_binary` implementations from `emit_bb_flat.c`
  - `emit_descr_fail` static helper (used only by above)
  - `emit_load_int_global/ptr/add/sub` orphaned EDP-9 statics
  - `emit_descr_success_from_stack` orphaned helper
  - `bb_build_binary_node` forward decl (no implementation existed)
  - `bb_build_binary` dead declaration from `bb_build.h`
  - `#include "../x86/emit_bb_flat.h"` from `stmt_exec.c` (only existed for deleted fns)
- 6 call sites in `stmt_exec.c` stubbed to `NULL` with `/* TODO Phase B */` comments.
- Build is clean. Gates broken due to NULL stubs causing segfault on pattern match.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md.
2. Confirm one4all HEAD `10796587`. Build will succeed; gates will show 5/7 + 3/4.
3. **Phase B — EM-RAW-PURGE-1:** Search `stmt_exec.c` for `TODO Phase B` (6 sites).
   - Add `patnd_make_xchr(const char*)` and `patnd_make_eps(void)` to `snobol4_patnd.h` and `snobol4_pattern.c` (GC_MALLOC, memset, set kind, set STRVAL_fn for XCHR).
   - Replace each NULL stub with: `PATND_t *p = patnd_make_xchr(s)` or `patnd_make_eps()`, then `bb_box_fn fn = bb_build_flat(p); if (!fn) fn = bb_build_brokered(p);`
   - Also fix `bb_build_brokered` raw prologue in `emit_bb_flat.c`: replace `bb_emit_byte(0x55); bb_emit_byte(0x48); bb_emit_byte(0x89); bb_emit_byte(0xE5);` with `emit_brokered_prologue()` (add that helper using `emit_form_*` calls, not raw bytes).
4. Build clean. Gates must reach smoke 7/7, template-byte-id 4/4 before committing.
