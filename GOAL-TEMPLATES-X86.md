# GOAL-TEMPLATES-X86.md — x86 backend, all languages

**Repo:** SCRIP + corpus + .github
**Backend:** x86 — native binary. Modes: `--sm-native` (mode-3, in-process JIT) and `--compile --target=x64` (mode-4, GAS `.s` → assemble → link).
**Read first:** `ARCH-x86.md` · `ARCH-EMITTER.md` · `ARCH-IR.md` · `RULES.md`

---

## Premise

The six frontends (SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus) all lower to the
shared SM/BB IR. This backend's job is to fill every SM opcode and every BB box-kind
that the IR can carry with x86 template emitter code, so that **every language runs on
x86**. The frontends produce opcodes; this backend supplies the x86 arm for each one.

x86 is the reference backend: the SM interpreter and the x86 emitter execute the same
SM_Program, so the emitter is correct by construction when the interpreter passes.

## Done when

Every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub
x86 template arm (`IS_X86` in `SM_templates/` / `BB_templates/`), and every language's
corpus runs green on both mode-3 (`--sm-native`) and mode-4 (`--compile --target=x64`),
byte-identical to the mode-2 oracle where an oracle exists.

## All-languages coverage

| Language | mode-3 (`--sm-native`) | mode-4 (`--compile --target=x64`) |
|---|---|---|
| SNOBOL4 | live state in `GOAL-SNOBOL4-BB.md` | live state in `GOAL-SNOBOL4-BB.md` |
| Snocone | — | — |
| Icon | live state in `GOAL-ICON-BB.md` | live state in `GOAL-ICON-BB.md` |
| Prolog | live state in `GOAL-PROLOG-BB.md` | live state in `GOAL-PROLOG-BB.md` |
| Raku | live state in `GOAL-RAKU-BB.md` | live state in `GOAL-RAKU-BB.md` |
| Rebus | — | — |

The per-language x86 frontend ladders are the `GOAL-*-BB.md` files. This backend goal is
the destination they all feed; per-language progress lives in those frontend files.

## Backend-specific notes (detail in ARCH-x86.md)

- Byrd boxes are stackless CODE+DATA blobs in `bb_pool`; four ports α/β/γ/ω; DATA per-invocation, CODE shared.
- Two emission forms: flat BBs (`EMIT_BINARY_WIRED`, jmp-threaded, ζ=`[r12]`) and brokered BBs (`EMIT_BINARY_BROKERED`, C-ABI, `rdi=ζ`).
- mode-4 TEXT path: GAS `.s` → assemble → link `libscrip_rt.so` → run.
- Templates are pure functions of `g_emit` (see ARCH-EMITTER.md); byte production lives only inside template files (RULES.md TEMPLATE-ONLY EMISSION).
