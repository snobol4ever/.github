# BACKEND-X64.md — x64 ASM Backend Reference (snobol4x)

Pure reference. No session state here.
**Session state** → SESSION-snobol4-x64.md / SESSION-icon-x64.md / SESSION-prolog-x64.md
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

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
Deep sprint plan → `ARCH-x64.md`

---

## Key Files

| File | Role |
|------|------|
| `src/backend/x64/emit_byrd_asm.c` | Main x64 emitter |
| `src/runtime/asm/snobol4_asm.mac` | Byrd box macro library |
| `test/crosscheck/` | ASM corpus crosscheck |
