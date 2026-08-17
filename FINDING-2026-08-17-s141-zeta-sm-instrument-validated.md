# FINDING s141 — THE ζ-SM INSTRUMENT IS VALIDATED, AND ITS FIRST HONEST READING OF BEAUTY IS **ZERO VIOLATIONS**

**Session:** 2026-08-17 s141 (Claude Opus 5). SCRIP: 3 files, all OUTSIDE the template layer. Default arm byte-identical, regens ×3 zero changed bytes.

---

## ⛔ THE HEADLINE, STATED AS A NEGATIVE ON PURPOSE

`beauty.sno < beauty.sno`, mode 3, under `SCRIP_ZSM=1`: **0 violations · 0 β-without-α · 192 covered ports.**
The instrument has convicted **NOTHING**. It is a *validated* instrument, not a *productive* one. No seat should
inherit this as "the RBP class is closed" — see COVERAGE below for exactly what it cannot see.

## ⛔ THREE PRIOR CUTS THIS SESSION WERE WRONG. EVERY NUMBER THEY PRODUCED IS VOID.

The session first reported **38 (m3) / 37 (m4) MISMATCH + 1437 UNDERFLOW** on beauty. **THAT REPORT IS RETRACTED.**
Three independent defects, each caught only because the next gate was run:

1. **GLOBAL LIFO PAIRING (void).** Banked at α, popped at β on one global stack — assumes α:β is 1:1. It is not:
   a box runs α ONCE, leaves via γ, and its β re-fires MANY times on backtrack. Pops outnumber pushes, the stack
   drains, and every surviving comparison was a β against **some other box's** banked α. The 1437 "UNDERFLOW" was
   that arity, **NOT** evidence of β-reached-without-α.
2. **WRONG PORT (Lon's correction, in-chat).** *"It is not BETA that tears down, since BETA can go to GAMMA. It's
   the transition from that box from BETA out to OMEGA that tears down."* The frame's lifetime is **α..ω**. β is an
   ENTRY port and the box is SUPPOSED to still hold its frame there. An equality test at β **convicts
   correctly-working boxes**. Confirmed by the design of record: ζ-ACTIVATION FRAME = *"push rbp at α · self-pop at ω"*.
   ω is a **TRANSFER**, so it never reached the `x86_deflabel` seam the α/β probes ride — **the teardown half of the
   invariant had never been measured at all.**
3. **FRAME-RESIDENT DATUM (Lon's correction, in-chat: *"I was WRONG... at BETA if RBP is wrong it is unaccessible.
   Chicken and the egg"*).** A cut banked the identity at `[rbp-8]` and re-read it at β — circular: validating `rbp`
   by dereferencing `rbp` needs `rbp` already correct to discover it is not. **The datum must be global side state.**

## ⛔ THE GATE THAT MAKES IT TRUSTWORTHY — AND THAT THE FIRST THREE CUTS ALL FAILED

**FALSE-POSITIVE GATE: known-PASSING programs must report ZERO.** Cuts 1–3 each convicted `m1_defer_LEN0`,
`m1_inline_ALT`, `m1_nodefer_ALT` — **all three produce oracle-correct output.** An instrument that convicts
passing programs cannot testify about failing ones. Root cause of that arm: `emit.cpp:1019` stages `op_zdp_rbp=1`
for **every** `IR_MATCH_BEGIN`/`IR_MATCH_DEFER` — that is the node **KIND**, not whether **this instance emits
`push rbp`**. Both templates gate the real push behind further conditions. Cured by re-deriving the predicate from
the SAME authorities the templates consult (`emit_match_rbp()`; `((op_seal==1)||emit_defer_carve_rbp()) &&
x86_port_cstack() && emit_defer_rbp()`) — never a second opinion.

Gate now green 5/5: `m1_defer_LEN0` · `m1_inline_ALT` · `m1_nodefer_ALT` · `m1_alt_arm1_cap` · `m1_alt_arm2_cap`.

## THE DESIGN (Lon in-chat: *"build a monitor harness around the BB execution ... A system that measures itself"*)

Three layers, **ZERO template `.cpp` edits**:
- **Emit:** two existing seams. `x86_deflabel()` → α, β (label defines). `x86_jmp()` → ω (transfer). ~11 instrs/port.
- **Shim `rt_zdp_ev` (hand asm, `rtx_zdp.S`):** saves the ENTIRE caller-saved set + rflags — **r10/r11 (γ/ω WIRES)
  and r8/r9 (RTCC/GVA tier) included** — aligns, calls C, restores. This is why C is safe here; a bare C callee
  would clobber the wires and measure a DIFFERENT program (the s132 monitor lesson).
- **SM (C, `runtime_init.c`):** `g_zsm[node & 65535]` = `{node, E, F, rsp_a, live}` + 64-port trace ring dumped on
  violation. α: `E=rbp`, `F=rsp-8`. β: activation live AND `rbp==F`. ω: `rbp==E` AND `rsp>=rsp_a`. Abort on first.
- **`F = rsp-8` IS A PREDICTION, NOT A READING** (template's first act is `push rbp; mov rbp,rsp`). It is validated
  BY the false-positive gate, never asserted — a wrong prediction lights up the passing probes.

⛔ **NEW GLOBALS: GRANTED IN-CHAT BY LON THIS SESSION**, verbatim: *"So it must be a global. You'll want to use the
node ids. You'll want to maintain housekeeping information to keep track of the state."*

## ⛔ COVERAGE — WHAT THIS TOOL CANNOT SEE (read before trusting a zero)

- **γ IS NOT INSTRUMENTED.** Three ports, not four. γ is where a leak would be caught **at departure**; today a bad
  frame is only noticed one hop later at β, with the guilty box already gone.
- **CONDITIONAL EXITS UNCOVERED.** `x86_omega("js")` / `x86_gamma(mnem)` skipped: a flag-clobbering probe ahead of a
  `jcc` destroys the condition, and probing unconditionally reports a port that was not taken.
  **Measured gap: ~64 instrumented nodes vs ~100 `push rbp` sites in beauty's `.s` — about a third invisible.**
- **RECURSION ALIASES** one slot per (node & 65535); innermost α wins. Not a census.
- **THE R-4(b) BLOB ACTIVATION** (emit.cpp:2891) attaches at the graph-entry origin hook, not the s136 choke — outside this gate.
- **BEAUTY DIES AFTER 10 LINES OF 622.** The SM can only testify about code that EXECUTED. Most of beauty never ran.

## NEXT SEAT — pick up exactly here

**(a) LAND γ + THE FOUR-STATE FSM.** `FRESH ─γ→ SUSPENDED ─β→ RESUMED ─γ→ SUSPENDED`, `─ω→ DEAD`. Cheap (γ already
rides `x86_jmp`, no label minting). Two new finding classes independent of register values: **illegal transitions**
(β from non-SUSPENDED, γ from DEAD, two ω for one α) and **LEAKED ACTIVATIONS** (SUSPENDED, never resumed, never torn
down) — the shape that would actually explain a wrong rbp later. Plus `rbp==F` at γ localizes to the departing box.
**(b) CONDITIONAL-PORT COVERAGE via CONDITION INVERSION** at the `x86_jcc` seam: `j<inv> .Lskip / <probe> / jmp ω /
.Lskip:`. Semantics identical, no template touched, closes the ~1/3 gap. ⛔ Needs a unique label per site — **draw
from the existing `g_flat_node_id` uid stream; do NOT add a counter** (NO-NEW-GLOBALS without a fresh in-chat grant).
**(c) RE-RUN THE FALSE-POSITIVE GATE AFTER EVERY WIDENING, BEFORE READING ANY NUMBER.** Three cuts died here.
**(d) ONLY THEN sweep the failing corpus.** A zero from a tool with (a)/(b) open is not an acquittal.

## MEASURED

Non-vacuity 192 sites in beauty / 3 in probes · OFF emits 0, default output byte-identical to pristine HEAD (stash-rebuild diff)
· regens ×3 **zero changed bytes** · false-positive gate 5/5 zero · beauty m3 **0 violations, 0 β-without-α** · zero
template `.cpp` files touched · `grep MEDIUM_ src/emitter/BB_templates/` == 0.
