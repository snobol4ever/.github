# MILESTONE-BOX-UNIFY — Single-Source Box Definitions

**Session:** DYN- · **Sprint:** DYN-25 onward
**Status:** PLANNED — DYN-24 did the 11 easy boxes; this finishes the job.

---

## Problem Statement

Every Byrd box currently has up to three representations:

| Form | Location | Owner |
|------|----------|-------|
| C text (canonical) | `src/runtime/boxes/bb_*.c` | Linked by scrip-interp + test harness |
| asm text (NASM) | `src/runtime/boxes/bb_*.s` | Linked by snobol4_x86 runtime |
| asm binary | (not yet implemented) | Planned for JIT path |

**Current duplication after DYN-24:**
- 11 simple boxes ✅ de-duplicated — `bb_box.h` owns typedefs, `bb_*.c` is canonical
- 3 complex boxes (`bb_atp`, `bb_capture`, `bb_deferred_var`) still duplicated:
  - Live in `stmt_exec.c` as `static` (need `bb_node_t`, `DESCR_t`, `bb_build`)
  - Also have stub `bb_atp.c`, `bb_capture.c`, `bb_dvar.c` that don't compile cleanly

---

## Phase 1 — Fix DYN-24 linker error (DYN-25 first task)

`bb_build()` in `stmt_exec.c` references `bb_atp`, `bb_capture`, `bb_deferred_var`
as function-pointer targets. When `bb_atp.c`/`bb_capture.c`/`bb_dvar.c` are
excluded from the build, these symbols are undefined.

**Fix options (pick one):**
A. Keep complex boxes as `static` in `stmt_exec.c`; delete `bb_atp.c`,
   `bb_capture.c`, `bb_dvar.c` stub files entirely. Cleanest for now.
B. Extract `bb_node_t` + `bb_build` prototype into `runtime/dyn/bb_build.h`,
   include in `bb_dvar.c` / `bb_atp.c` / `bb_capture.c`. More work, cleaner long-term.

**Recommendation:** Option A for DYN-25 (delete stubs), Option B as part of
the full unification below.

---

## Phase 2 — Full single-source architecture (future milestone)

### Target layout

```
src/runtime/boxes/
  bb_box.h          — spec_t, ports (α/β/γ/ω), ALL state typedefs, bb_box_fn
  bb_build.h        — bb_node_t, bb_build() prototype (extracted from stmt_exec.c)
  bb_lit.c          — C implementation (canonical logic)
  bb_lit.s          — asm-text implementation (hand-written NASM, matches C)
  bb_lit_emit.c     — asm-binary emitter: writes bb_lit machine code into mmap pool
  ... (25 boxes × 3 files)
```

### Port wiring diagram (top level — same for all three forms)

```
         ┌─────────────────────────────┐
         │       bb_NAME(ζ, entry)     │
         │                             │
  α ────►│  α port: match forward      │────► γ (success, spec_t)
  β ────►│  β port: backtrack          │────► ω (failure, spec_empty)
         │                             │
         │  state: NAME_t *ζ           │
         └─────────────────────────────┘
```

C form: `spec_t bb_NAME(void *zeta, int entry)` — three-column goto style
asm-text form: NASM with `bb_NAME:` global, same port logic as C
asm-binary form: `void bb_NAME_emit(uint8_t *buf, size_t *len, NAME_t *ζ)` —
  writes machine code for one box invocation into mmap pool

### Single logic rule

**One English description of the box's matching logic → three mechanical
derivations.** Any change to box semantics touches `bb_NAME.c` first;
`bb_NAME.s` and `bb_NAME_emit.c` are then derived/updated to match.

### Macro-formatted C source

All `bb_*.c` files use the three-column macro style already established:

```c
spec_t bb_lit(void *zeta, int entry)
{
    lit_t *ζ = zeta;
    spec_t LIT;
    if (entry==α)                                                               goto LIT_α;
    if (entry==β)                                                               goto LIT_β;
    LIT_α:  if (Δ + ζ->len > Ω)                                                goto LIT_ω;
            if (memcmp(Σ+Δ, ζ->lit, (size_t)ζ->len) != 0)                      goto LIT_ω;
            LIT = spec(Σ+Δ, ζ->len); Δ += ζ->len;                              goto LIT_γ;
    LIT_β:  Δ -= ζ->len;                                                        goto LIT_ω;
    LIT_γ:                                                                      return LIT;
    LIT_ω:                                                                      return spec_empty;
}
```

No mixing of styles. All 25 boxes look identical in structure.

---

## Gate

- snobol4_x86 **142/142** maintained throughout
- `scrip-interp` links and passes M-INTERP-A01 smoke tests (20 corpus programs)
- `bb_test` harness: 25/25 C boxes pass, 25/25 S boxes match

---

## Files to create/modify

```
src/runtime/dyn/bb_build.h          — extract bb_node_t + bb_build prototype
src/runtime/boxes/bb_box.h          — already updated (DYN-24); add bb_build.h include
src/runtime/boxes/bb_atp.c          — rewrite to use bb_build.h (or delete if Option A)
src/runtime/boxes/bb_capture.c      — rewrite (or delete if Option A)
src/runtime/boxes/bb_dvar.c         — rewrite (or delete if Option A)
src/runtime/dyn/stmt_exec.c         — remove remaining static bb_* bodies
```

---

*Written DYN-24 2026-04-02. Supersedes ad-hoc box notes in SESSIONS_ARCHIVE.*
