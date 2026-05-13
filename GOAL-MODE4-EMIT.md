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
- [ ] **EM-BB-FORMAT** ⚡ NEXT — each BB port = one 4-column `;`-separated GAS line, widths 24/16/32/free. ⛔ No if-statements in template functions. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, `gcc -c` clean, beauty ≥10.
- [ ] **EM-REWRITE** ⏳ HELD — Full rewrite of the 16-file emitter subsystem. Held until Lon signs off. Gates TBD at sign-off.
- [ ] **EM-SNOCONE-PREP** — ESP-1..10: stale names, comments, dead code in emitter files. Gates: smoke 7/7, template-byte-id 4/4, em8 5/5.
- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13y (Claude Sonnet 4.6)**

one4all HEAD `d894c021`. .github HEAD `829f7714`. Gates: smoke 7/7, template-byte-id 4/4.

### What was done this session

- Verified emitter architecture: mode-3 (`emit_sm_binary.c`) is a C stack machine interpreter — zero x86 emission, completely outside emitter scope. Confirmed correct.
- Verified SM ops: exactly one C template function per op in `emit_sm_op.c`; `emit_sm_text.c` always calls through them. No duplicates.
- Verified BB ops: exactly one C template function per op in `emit_bb_box.c`. No duplicates.
- Full emitter source inventory: 8,920 lines across 16 file pairs, L0–L5.
- Emitter cleanup STILL ACTIVE per Lon — continue scanning before EM-BB-FORMAT.

### Emitter file inventory (8,920 lines total)

| File | Lines | Layer |
|---|---:|---|
| emit_buf.h/c | 173 | L0 byte primitive |
| emit_defs.h/c | 58 | L0 type defs |
| emit_form.h/c | 445 | L1 encoding forms |
| emit_insn.h/c | 708 | L2 single insns |
| emit_label.h/c | 76 | L2 label lifecycle |
| emit_mode.h/c | 280 | L2 mode globals |
| emit_text3c.h/c | 306 | L2 3-col formatter |
| emit.h/c | 334 | L2 dual-mode forms |
| emit_bb_gen.h | 24 | L2 umbrella shim |
| emit_templates.h | 212 | L3/4 decls |
| emit_bb_seq.h/c | 660 | L3 compound BB helpers |
| emit_bb_box.c | 259 | L4 BB box templates |
| emit_bb_flat.h/c | 1241 | L5 flat glob builder |
| emit_sm_shape.h/c | 904 | L4 SM shape renderers |
| emit_sm_op.c | 388 | L4 SM op templates |
| emit_sm_text.h/c | 1763 | L5 text SM codegen walker |
| emit_sm_binary.h/c | 1423 | L5 mode-3 interpreter (no x86 emission) |

### Next session must

1. Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md.
2. Confirm one4all HEAD `d894c021`. Gates: smoke 7/7, template-byte-id 4/4.
3. Emitter cleanup still active — scan before EM-BB-FORMAT work.
4. Current step: **EM-BB-FORMAT** — each BB port = one 4-column `;`-separated GAS line, widths 24/16/32/free. No if-statements in template functions. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, gcc -c clean, beauty ≥10.
