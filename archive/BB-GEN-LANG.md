# BB-GEN-LANG.md — Language BB Generators (C, JS, WASM, Java, C#)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE DESIGN — C and Java done ✅, others stub

Generates Byrd Box implementations as source code in each target language.
Each language gets one function per box implementing the α/β/γ/ω protocol.

---

## The Canonical Box Layout — One Function Per Box

The ground truth is the C reference implementations: `test_sno_*.c`, `test_icon.c`.
Each box is ONE C function. The layout inside is pure three-column SNOBOL4:

```
    LABEL:          ACTION                          GOTO
    ───────────────────────────────────────────────────────
    BIRD_α:         if (Σ[Δ+0] != 'B')             goto BIRD_ω;
                    BIRD = str(Σ+Δ, 4); Δ += 4;    goto BIRD_γ;
    BIRD_β:         Δ -= 4;                         goto BIRD_ω;
```

Labels are real C labels. Gotos are real gotos. No call/return overhead on the hot path.

### The Three-Column Law

Every generated line follows three columns:

- Column 1 (label): starts at col 0, width 22. Real C labels.
- Column 2 (action): starts at col 22, width 40. The operation.
- Column 3 (goto): starts at col 62. Always `goto X;` or `return`.

Comments are `/*---...---*/` separator lines between logical sections.

### Full C Box Example

```c
str_t BIRD(bird_t **ζζ, int entry) {
    bird_t *ζ = *ζζ;
    if (entry == α) { ζ = enter(ζζ, sizeof(bird_t)); goto BIRD_α; }
    if (entry == β) {                                  goto BIRD_β; }
    /*------------------------------------------------------------------------*/
    str_t         BIRD;
    BIRD_α:       if (Σ[Δ+0] != 'B')                  goto BIRD_ω;
                  if (Σ[Δ+1] != 'i')                  goto BIRD_ω;
                  if (Σ[Δ+2] != 'r')                  goto BIRD_ω;
                  if (Σ[Δ+3] != 'd')                  goto BIRD_ω;
                  BIRD = str(Σ+Δ, 4); Δ += 4;          goto BIRD_γ;
    BIRD_β:       Δ -= 4;                               goto BIRD_ω;
    /*------------------------------------------------------------------------*/
    BIRD_γ:       return BIRD;
    BIRD_ω:       return empty;
}
```

Box function signature: `typedef str_t (*box_fn_t)(box_t *ζ, int entry);`
Entry is α (0) or β (1). ALL ports are real C labels inside ONE function.

---

## What Was Wrong with the mac_* Approach

The previous design split each box into four separate C functions
(one per port: mac_LIT_α, mac_LIT_β, mac_LIT_γ, mac_LIT_ω). This is wrong:

1. The box body spans four function calls — α/β/γ/ω labels are not in the same scope.
2. Stray x86 instruction preambles — each mac_* function set up its own context.
3. Not one function per box — the canonical form is one function per named pattern.

---

## Language Generator Table

| Language | Generator | Output | Status |
|----------|-----------|--------|--------|
| C        | `bb_gen_c.c` | `bb_*.c` source files | ✅ done (src/runtime/dyn/) |
| Java     | `bb_gen_java.c` | `bb_*.java` classes | ✅ done (src/runtime/boxes/) |
| JS       | `bb_gen_js.c` | `bb_*.js` functions | ⬜ stub |
| WASM     | `bb_gen_wasm.c` | `bb_*.wat` text | ⬜ stub |
| C#       | `bb_gen_net.c` | `bb_*.cs` classes | ⬜ stub |

---

## File Layout (C path)

```
src/runtime/dyn/bb_box.h            bb_node_t / box_fn_t typedefs
src/runtime/dyn/bb_lit.c            LIT box: one function, all ports ✅
src/runtime/dyn/bb_alt.c            ALT box ✅
src/runtime/dyn/bb_seq.c            SEQ box ✅
src/runtime/dyn/bb_pos.c            POS/RPOS box ✅
src/runtime/dyn/bb_arbno.c          ARBNO box ✅
src/runtime/dyn/bb_build.c          graph assembler: wires boxes together ✅
```

ALT β bug: fix in DYN-3 (one line — ALT_β must ω not advance to next branch).

---

## References

- `BB-GRAPH.md` — the graph structure these functions implement
- `BB-GEN-X86-TEXT.md` — NASM counterpart (same three-column law)
- `BB-GEN-X86-BIN.md` — binary x86 counterpart
