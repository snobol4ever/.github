# BACKEND-X64.md — x64 ASM Backend Reference (snobol4x)

Pure reference. No session state here.
**Session state** → `SESSION-snobol4-x64.md` / `SESSION-icon-x64.md` / `SESSION-prolog-x64.md`

---
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`
---

## The Core Insight — CODE shared, DATA per-invocation

Byrd boxes are naturally reentrant. CODE (α/β/γ/ω goto sequence) never changes.
Only DATA (locals: cursor, captures, params) differs between invocations.

```
┌────────────────────────┐  ┌────────────────────────┐
│  CODE (RX, shared)     │  │  CODE (RX, shared)     │
│  P_ROMAN_α:            │  │  P_ROMAN_α: ← same     │
│    mov rax,[r12+OFF_N] │  │    mov rax,[r12+OFF_N] │
├────────────────────────┤  ├────────────────────────┤
│  DATA₁ (invocation 1) │  │  DATA₂ (invocation 2) │
│  r12 → N='12', cur=0  │  │  r12 → N='1',  cur=0  │
└────────────────────────┘  └────────────────────────┘
```

α allocates a DATA copy → that IS the save.
γ/ω discards the copy → that IS the restore.
Byrd boxes running forward and backward ARE save and restore.

---

## Status

| Phase | What | Status |
|-------|------|--------|
| Near-term bridge | Per-invocation C stack frames | M-ASM-RECUR ✅ |
| Technique 2 | mmap+memcpy+relocate | M-T2-FULL — implement now |

**Key (2026-03-21 B-238):** Technique 2 does NOT require self-hosting.
`emit_byrd_asm.c` already knows full box structure — can emit relocation tables
at compile time as NASM data sections.

---

## Key Files

| File | Role |
|------|------|
| `src/backend/x64/emit_byrd_asm.c` | Main x64 emitter |
| `src/runtime/asm/snobol4_asm.mac` | Byrd box macro library |
| `test/crosscheck/` | ASM corpus crosscheck |

---

## Deep Reference

| Topic | Doc |
|-------|-----|
| Technique 2 sprint plan (M-ASM-RECUR, mmap details) | `ARCH-x64.md` |
| M-X64-FULL SPITBOL LOAD/UNLOAD sprint | `ARCH-x64.md` |
