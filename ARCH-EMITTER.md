# ARCH-EMITTER.md — Emitter Architecture (post RW-6)

EM-REWRITE complete (RW-0..RW-6, RW-OPCODES, RW-STYLE-1/2, EM-SNOCONE-PREP, S200-2..7). Full naming-scan history: `git log -p .github/ARCH-EMITTER.md`.

---

## Current compiled units (3 + 1 frozen)

| File | Role |
|---|---|
| `emit_core.c` | L0–L2: buf, form, insn, label, text, mode — all leaf infrastructure |
| `emit_bb.c` | L3–L4: BB box templates (flat + brokered) + macro library writer |
| `emit_sm.c` | L4–L5: SM opcode templates, shape renderers, text+walk codegen |
| `sm_jit_interp.c` | **frozen** — mode-3 C interpreter; never touched |

---

## Naming rules (active — used by SF-5..8 and future work)

**Layer prefix:**
- `insn_` — L0/L1 leaf: one x86 instruction, `if (IS_TEXT)` at top, binary below
- `emit_label_` — L2 label lifecycle
- `emit_text_` — L2 TEXT-only formatting (3-col, banners)
- `emit_mode_` — L2 mode lifecycle
- `emit_seq_` — L3 compound sequences (multi-instruction, all modes)
- `emit_bb_` — L4 BB box templates (one box kind per function)
- `emit_sm_` — L4/L5 SM opcode templates and shape renderers

**Key macros:** `IS_TEXT` · `IS_BIN` · `IS_WIRED` · `IS_BROKERED`

**Single `if (IS_TEXT)` at the leaf** — never in any `emit_seq_*`, `emit_bb_*`, or `emit_sm_*` body.

**200-col, zero blank lines, no inline/body comments, no single-stmt braces.**

---

## Template purity invariant (from GOAL-PURE-TEMPLATES, consolidated)

Every template `_str()` function is a pure function `g_emit → std::string`: no side
effects, no local variables except loop indices. Body = ONE expression built from
**CONCAT** (`A + B + C`), **IF** (`cond ? A : B`), and **FOR**
(`emit_for(lo, hi, [](int i){ return ...; })`, defined in `emit_str.h`). All inputs come
from the `g_emit` argument; no mutation inside `_str()`. Side effects (label allocation,
file writes) belong in the driver, before `xa_dispatch`. Helpers: `emit_for` in
`emit_str.h`; `strtab_label_s(s)→std::string` in `sm_template_common.h` (eliminates
`char buf[64]` locals). This pairs with the RULES.md TEMPLATE-ONLY EMISSION rule: byte
production lives only inside `*_templates/` files.

---

## Key globals

| Name | Role |
|---|---|
| `g_emit_mode` | Active `emit_mode_t` (EMIT_TEXT / EMIT_BINARY / EMIT_MACRO_DEF) |
| `g_emit_out` | FILE* for TEXT / MACRO_DEF output |
| `g_flat_node_id` | Monotone counter for unique flat-box label suffixes |
| `bb_emit_mode` | Legacy alias — same value as `g_emit_mode` (keep for existing callers) |

---

## Flat-box DATA pattern (SF-1..4 established; SF-5..8 follow)

TEXT path for a stateful box with N int-sized data words:
```
.section .data
.Lboxname%d_z:  .long 0    ; word 0
                .long 0    ; word 1 (etc.)
.section .text
.intel_syntax noprefix
; α-port inline code using [rip + .Lboxname%d_z + N*4]
; β-port inline code (emit_label_define(b); ...)
```
Binary path: unchanged — `emit_seq_port_call(zeta, fn_name, fn_fallback, port, s, f)`.
