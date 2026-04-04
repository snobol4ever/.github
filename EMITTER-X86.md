# EMITTER-X86.md — x64 ASM Emitter (one4all)

Pure reference. No session state here.
**Session state** → SESSION-snobol4-x64.md / SESSION-icon-x64.md / SESSION-prolog-x64.md
**Deep reference:** all ARCH docs cataloged in `PLAN.md`

---

## The Core Insight — CODE shared, DATA per-invocation

Byrd boxes are naturally reentrant. CODE (α/β/γ/ω goto sequence) never changes.
Only DATA (locals: cursor, captures, params) differs between invocations.

α allocates a DATA copy → that IS the save.
γ/ω discards the copy → that IS the restore.
Byrd boxes running forward and backward ARE save and restore.

---

## Status

| Phase | What | Status |
|-------|------|--------|
| Near-term bridge | Per-invocation C stack frames | M-ASM-RECUR ✅ |
| Technique 2 | mmap+memcpy+relocate | M-T2-FULL — implement now |

**Key (B-238):** Technique 2 does NOT require self-hosting.
`emit_byrd_asm.c` can emit relocation tables at compile time.
Deep sprint plan → `EMITTER-X86.md`

---

## Key Files

| File | Role |
|------|------|
| `src/backend/x64/emit_byrd_asm.c` | Main x64 emitter |
| `src/runtime/asm/snobol4_asm.mac` | Byrd box macro library |
| `test/crosscheck/` | ASM corpus crosscheck |

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — ⬜ needs SM_Program input (currently tree-walks IR)

Pure reference. No session state here.
**Session state** → `SESSION-snobol4-x64.md` / `SESSION-icon-x64.md` / `SESSION-prolog-x64.md`

---

## The Core Insight — CODE shared, DATA per-invocation

Byrd boxes are naturally reentrant. CODE (α/β/γ/ω goto sequence) never changes.
Only DATA (locals: cursor, captures, params) differs between invocations.

α allocates a DATA copy → that IS the save.
γ/ω discards the copy → that IS the restore.
Byrd boxes running forward and backward ARE save and restore.

---

## Status

| Phase | What | Status |
|-------|------|--------|
| Near-term bridge | Per-invocation C stack frames | M-ASM-RECUR ✅ |
| Technique 2 | mmap+memcpy+relocate | M-T2-FULL — implement after SM_Program |
| SM_Program input | Replace tree-walk with SM_Program walk | ⬜ not written |

**Architecture reset (DYN-82):** The emitter must walk `SM_Program` instructions,
not tree-walk IR. When the INTERP passes the full corpus on a given SM_Program,
the emitter for that same SM_Program is correct by construction.

---

## Key Files

| File | Role |
|------|------|
| `src/backend/x64/emit_byrd_asm.c` | Main x64 emitter |
| `src/runtime/asm/snobol4_asm.mac` | Byrd box macro library (151 macros) |
| `test/crosscheck/` | ASM corpus crosscheck |

---

## Near-Term Bridge — Per-Invocation Stack Frames (M-ASM-RECUR ✅)

**Problem:** The ASM backend had ONE `rbp` frame for the entire program. All
`[rbp-8/16/32/48]` temporaries were shared globals. Recursive calls corrupted them.

**Fix:** Each user-defined function's α port establishes its own stack frame.

```c
/* emit_asm_named_def(), is_fn branch, α label: */
asmL(np->alpha_lbl);
A("    push    rbp\n");
A("    mov     rbp, rsp\n");
A("    sub     rsp, 56\n");

/* γ label: */
asmL(gamma_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_gamma);

/* ω label: */
asmL(omega_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_omega);
```

**Acceptance test:** `roman.sno` runs correctly (recursive Roman numeral conversion).

**Optimization note (Lon):** Do NOT skip to Technique 2 prematurely. Prove correctness first.

---

## Technique 2 — mmap + memcpy + relocate (post SM_Program)

When `*X` fires or a function is called:
1. `memcpy(new_text, box_X.text_start, len)` — copy CODE section
2. `memcpy(new_data, box_X.data_start, len)` — copy DATA section
3. `relocate(new_text, delta)` — patch relative jumps + absolute DATA refs
4. Load `r12 = new_data`
5. Jump to `new_text[α]`

TEXT: PROTECTED (RX). DATA: UNPROTECTED (RW). One copy per live invocation.
Reclamation: LIFO — discard `new_data` on γ/ω return. No GC needed. ~20 lines of runtime.

**No longer gates on M-BOOTSTRAP.** `emit_byrd_asm.c` knows every box's structure at
compile time and emits relocation tables as NASM data sections directly.

### Milestone Chain

| ID | Deliverable |
|----|-------------|
| M-T2-RUNTIME | `t2_alloc/free/mprotect` runtime; unit test |
| M-T2-RELOC   | `t2_relocate()` patches jumps+DATA refs; unit test |
| M-T2-EMIT-TABLE | emitter writes per-box relocation tables as NASM data |
| M-T2-EMIT-SPLIT | emitter splits TEXT+DATA sections; `r12` = DATA-block ptr |
| M-T2-INVOKE  | emitter generates T2 call-sites; γ/ω emit `t2_free` |
| M-T2-RECUR   | recursive functions correct; stack-frame bridge removed |
| M-T2-CORPUS  | 106/106 corpus |
| M-T2-FULL    | all three backends clean; `v-post-t2` tag |

---

## SPITBOL LOAD/UNLOAD — Second Oracle Sprint (M-X64-FULL)

See `MISC-SPITBOL-LOAD.md` for the full sprint plan.

Goal: Make SPITBOL x64 a fully working LOAD/UNLOAD host so it can participate in
the 5-way monitor as a second oracle.

---

## References

- `SCRIP-SM.md` — the SM_Program this emitter must walk
- `EMITTER-COMMON.md` — shared emitter architecture, SIL naming, CNode IR
- `BB-GEN-X86-TEXT.md` — NASM .s text generation for Byrd boxes
- `BB-GEN-X86-BIN.md` — binary x86 generation for Byrd boxes
- `INTERP-X86.md` — interpreter; when it passes corpus, emitter is correct by construction
