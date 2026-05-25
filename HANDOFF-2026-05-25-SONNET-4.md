# HANDOFF — 2026-05-25 — Claude Sonnet 4.6 Session (fourth)

**one4all HEAD:** `eff53b7e`
**.github HEAD:** `f667d0bb`
**Gates:** smoke_prolog 5/5 ✅ · smoke_snobol4 7/7 ✅ · smoke_icon 5/5 ✅ · crosscheck_prolog 128/0 ✅

---

## Work completed this session

### PJ-13 — Mass rename lbl_back/succ/fail → lbl_β/γ/ω (`6f4996f7`)

The rule was always: four ports = four one-character Greek names, everywhere. The codebase used `lbl_succ`/`lbl_fail`/`lbl_back` (English synonyms). Renamed 34 files, 222 occurrences:
- `lbl_succ_p` → `lbl_γ_p`, `lbl_fail_p` → `lbl_ω_p`, `lbl_back_p` → `lbl_β_p`
- `lbl_succ` → `lbl_γ`, `lbl_fail` → `lbl_ω`, `lbl_back` → `lbl_β`
- `flat_lbl_succ`/`flat_lbl_fail` → `flat_lbl_γ`/`flat_lbl_ω` (these are also port names)

Scope: `emit_globals.h`, all `BB_templates/*.cpp`, `emit_bb.c/.h`, `emit.h`, `xa_*.cpp`, `sm_template_common.h`, `emit_per_kind_audit.c`. RULES.md updated.

### PJ-14 — Explicit α label on every BB template (`eff53b7e`)

α was implicit — the broker fell into boxes by position; nothing could reliably jump to a fresh-call entry by name. All four ports are now explicit and jumpable.

Three coordinated changes:
1. `emit_globals.h`: `lbl_α` / `lbl_α_p` added to `g_emit_t` alongside β/γ/ω.
2. `emit_bb.c`: `bb_fill_alpha(BB_t *nd)` — uses a static ring of 8 `bb_label_t` (single-threaded emit, safe), initialises `"bb<id>_α"` via `bb_node_id(nd)`, sets `g_emit.lbl_α`/`lbl_α_p`. Called from `FILL`, `EP_FILL`, and `walk_bb_flat` null-path.
3. Every BB template TEXT arm: emits `s_1asm(emit_fmt("%s:", _.lbl_α))` as the first instruction.

The broker now does `jmp _.lbl_α` for a fresh call and `jmp _.lbl_β` for a retry. No implicit fall-through.

### RULES.md updated

"FOUR PORTS = FOUR ONE-CHARACTER GREEK NAMES. ALWAYS." — struct fields, emitter C/C++ code, and emitted assembly labels. `lbl_α`/`lbl_β`/`lbl_γ`/`lbl_ω` everywhere.

---

## State of the project

All GOAL-PROLOG-BB steps complete (PJ-1 through PJ-14). The goal file now contains a full architecture reference section explaining how bb_exec.c maps to x86 templates.

**Next work is in GOAL-BB-TEMPLATE-LADDER:**
- ICN-T-4: `bb_proc_gen.cpp` — `BB_PROC_GEN`
- ICN-T-6: `bb_gen_alt.cpp` — `BB_GEN_ALT`
- PL-T-4: `bb_pl_call.cpp` — `BB_PL_CALL` (predicate call, inline x86, no rt_*)
- PL-T-5: `bb_pl_choice.cpp` — `BB_CHOICE` (multi-clause, inline x86, no rt_*)

For PL-T-4/5: translate `bb_exec.c` cases `BB_PL_CALL` (line ~1814) and `BB_CHOICE` (line ~1783) directly to x86 TEXT. No new `rt_*` functions. Reference the architecture section in GOAL-PROLOG-BB.md for `BB_t` field layouts and the method.

---

## Key invariants to remember

- `_.lbl_α` = fresh entry label (broker jumps here for new call)
- `_.lbl_β` = retry entry label (broker jumps here for resume)
- `_.lbl_γ` = success exit
- `_.lbl_ω` = failure exit
- BB templates emit x86 TEXT only — no `rt_*` port-logic helpers, no C Byrd box functions
- `bb_fill_alpha` sets lbl_α from `bb_node_id(nd)` before `walk_bb_node` — templates receive it as `_.lbl_α`

## Watermark

```
one4all: eff53b7e
.github: f667d0bb
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
smoke_snobol4: 7/7 ✅
smoke_icon: 5/5 ✅
```
