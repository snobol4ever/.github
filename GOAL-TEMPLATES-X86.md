# GOAL-TEMPLATES-X86.md — x86 backend, all languages

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**
**⛔ THE ASK ITSELF MUST BE A BANNER: any session requesting this permission MUST display the request in-chat as a large unmissable ⛔ banner — the proposed global's name, type, owning file, purpose, and why registers/the stack cannot carry it — so Lon cannot miss the ask.  A quiet or inline ask does not count as asking. (Lon 2026-08-13 s55, in-chat.)**


**Repo:** SCRIP + corpus + .github
**Backend:** x86 — native binary. Modes: `--run` (mode-3, DEFAULT, flat-wired in-process slab) and `--compile` (mode-4, GAS `.s` → assemble → link; `--target=x86` implies `--compile`). ⚠ was `--sm-native`/`--target=x64` — both flag spellings are gone from the current driver (confirmed 2026-08-29, `./scrip --help` has no output; usage prints on no args).
**Read first:** `ARCH-ENGINE.md` · `RULES.md`

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
x86 template arm (`IS_X86` in `src/templates/` — was `SM_templates/`/`BB_templates/`,
both retired by the src reorg, confirmed gone 2026-08-29), and every language's
corpus runs green on both mode-3 (`--run`) and mode-4 (`--compile`),
byte-identical to the mode-2 oracle where an oracle exists. ⚠ Modes 3/4 are graded
INDEPENDENTLY, not required to be byte-identical, per RULES.md § MODES MAY DIVERGE
(Lon 2026-08-28) — this file predates that ruling.

## All-languages coverage

| Language | mode-3 (`--run`) | mode-4 (`--compile`) |
|---|---|---|
| SNOBOL4 | live state in `GOAL-SNOBOL4-100.md` (retired name `GOAL-SNOBOL4-BB.md`) | live state in `GOAL-SNOBOL4-100.md` |
| Snocone | — | — |
| Icon | live state in `GOAL-ICON-100.md` (retired name `GOAL-ICON-BB.md`) | live state in `GOAL-ICON-100.md` |
| Prolog | live state in `GOAL-PROLOG-100.md` (retired name `GOAL-PROLOG-BB.md`) | live state in `GOAL-PROLOG-100.md` |
| Raku | live state in `GOAL-RAKU-100.md` | live state in `GOAL-RAKU-100.md` |
| Rebus | — | — |

The per-language x86 frontend ladders now live in the per-language `GOAL-*-100.md` files — corrected
2026-08-29; the `GOAL-*-BB.md` names above are confirmed gone (`ls`) and none of the three `-100` files
actually contain the string "GOAL-*-BB.md" (checked directly, no literal table entry exists), so this
routing rests on CLAUDE.md's general per-language promise ("every deleted Icon/SNOBOL4/Prolog GOAL-*
name resolves there") rather than a specific named lookup — flagging the gap rather than overclaiming
one. This backend goal is the destination they all feed; per-language progress lives there.

## Backend-specific notes (detail in ARCH-ENGINE.md)

- Byrd boxes are flat CODE+DATA blobs in `bb_pool` carrying no software value stack; four ports α/β/γ/ω; DATA per-invocation, CODE shared.
- Two emission forms: flat BBs (`EMIT_BINARY_WIRED`, jmp-threaded, ζ=`[r12]`) and brokered BBs (`EMIT_BINARY_BROKERED`, C-ABI, `rdi=ζ`).
- mode-4 TEXT path: GAS `.s` → assemble → link `libscrip_rt.so` → run.
- Templates are pure functions of `g_emit` (see ARCH-ENGINE.md); byte production lives only inside template files (RULES.md TEMPLATE-ONLY EMISSION).
