# BACKEND-X64.md — x64 Assembly Backend (L3)

x64 ASM is a planned backend for snobol4x.
Target: native x86-64 machine code via Byrd Box Technique 2 (mmap+memcpy+relocate).

*Session state → TINY.md. C backend (current) → BACKEND-C.md.*

---

## Status: Planned (post-M-BOOTSTRAP)

No sprints active. Architecture specified, not implemented.

## Technique 2 — mmap + memcpy + relocate

When `*X` fires at match time:
1. `memcpy(new_text, box_X.text_start, len)` — copy CODE section
2. `memcpy(new_data, box_X.data_start, len)` — copy DATA section (locals)
3. `relocate(new_text, delta)` — patch relative jumps + absolute DATA refs
   - Relative refs: add `delta = new_addr - orig_addr`
   - Absolute DATA refs: patch to point at new DATA copy
4. Jump to `new_text[PROCEED]`

TEXT: PROTECTED (RX). mprotect→RWX during copy+relocate, back to RX after.
DATA: UNPROTECTED (RW), one copy per dynamic instance.
No heap. No GC. ~20 lines. LIFO discipline = discard copy on backtrack failure.

Gates on: M-BOOTSTRAP (need self-hosting sno2c first, then target ASM directly).
