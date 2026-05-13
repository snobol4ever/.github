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

- [ ] **EM-RAW-PURGE-1** ⚡ NEXT — Finish removing `bb_lit_emit_binary` / `bb_eps_emit_binary` from `stmt_exec.c`. Replace all 5 remaining call sites with `patnd_make_xchr`/`patnd_make_eps` + `bb_build_flat`. Remove declarations from `bb_build.h`. Delete `bb_lit_emit_SIDECAR.c`. Build clean. Gates: smoke 7/7, template-byte-id 4/4.
  - Remaining call sites in `stmt_exec.c`: lines 660, 871, 878, 888, 894, 1166.
  - `bb_build.h` lines 23 + 30 — remove both declarations.
  - `patnd_make_xchr` / `patnd_make_eps` already added to `snobol4_patnd.h` + `snobol4_pattern.c` this session.
  - `bb_build_brokered` raw-byte prologue already fixed → `emit_brokered_prologue()` this session.
  - 221-line raw-byte block already removed from `emit_bb_flat.c` this session (saved in sidecar for cherry-pick reference).
  - ⚠️ `bb_build_flat` returns NULL if `flat_is_eligible` fails. All replacement sites must handle NULL return (fall through to epsilon or error) — mirror the existing null-check pattern at line 844.
- [ ] **EM-BB-FORMAT** — each BB port = one 4-column `;`-separated GAS line, widths 24/16/32/free. ⛔ No if-statements in template functions. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, `gcc -c` clean, beauty ≥10.
- [ ] **EM-REWRITE** ⏳ HELD — Full rewrite of the 16-file emitter subsystem. Held until Lon signs off. Gates TBD at sign-off.
- [ ] **EM-SNOCONE-PREP** — ESP-1..10: stale names, comments, dead code in emitter files. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.
- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13u (Claude Sonnet 4.6)**

one4all HEAD `b0729299` (partial work in tree, not yet committed — see EM-RAW-PURGE-1). Gates at session start: smoke 7/7, template-byte-id 4/4, em8 5/5.

### What was done this session

- Diagnosed `bb_lit_emit_binary` / `bb_eps_emit_binary` as raw-byte doppelgangers that slipped EDP-12 (audit script only matched `XKIND_t` / `SM_*` names, not function-level raw emitters).
- Removed 221-line raw-byte block from `emit_bb_flat.c` (lines 1138–1359); saved to `src/runtime/x86/bb_lit_emit_SIDECAR.c` for cherry-pick reference.
- Fixed `bb_build_brokered` raw prologue bytes → `emit_brokered_prologue()`.
- Added `patnd_make_xchr(const char*)` and `patnd_make_eps(void)` to `snobol4_patnd.h` + `snobol4_pattern.c`.
- Converted 2 of 7 `stmt_exec.c` call sites (lines ~641, ~650) to use `patnd_make_xchr`/`patnd_make_eps` + `bb_build_flat`.
- Added `EM-RAW-PURGE-1` step documenting remaining work.
- **NOT committed** — build not yet verified clean. Next session must finish EM-RAW-PURGE-1 before committing.

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, em8 5/5. one4all HEAD `b0729299`.
3. Current step: **EM-RAW-PURGE-1** — finish all remaining call sites, remove `bb_build.h` declarations, delete sidecar, build clean, run gates, commit.
4. ⚠️ KEY LESSON: `bb_lit_emit_binary` / `bb_eps_emit_binary` are raw-byte BB emitters — they bypass the template system entirely. Every x86 byte emitter (BB or SM) must go through `emit_bb_*` / `emit_sm_*` template functions. No exceptions.
5. ⚠️ KEY LESSON: when moving functions that call `emit_macro_begin`, check TEXT-mode branches include `if (bb_emit_mode == EMIT_TEXT && g_in_text_macro_body) return;` to suppress body instructions after macro invocation.
