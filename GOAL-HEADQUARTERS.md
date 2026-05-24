# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** `[NO-AST] FOO` → fresh SM/BB lowering, never restore AST walk.
2. **Zero C Byrd-box functions.** No `DESCR_t foo(void *zeta, int entry)`. Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Single gate run at end of session.**
6. **Builder/consumer case rule.** UPPERCASE builds IR (`SM_*`, `BB_*`). lowercase consumes.
7. **EC-UNI matrix.** Backends are columns (X86/JVM/JS/NET/WASM). Text-vs-binary inside each `IS_<BE>` arm — never a matrix dimension.
8. **Unified dispatch owns mode-setting.** Per-opcode calls `emit_mode_set(TEXT_MODE(), out)` at entry.
9. **One file per Byrd Box in `BB_templates/`.** Each in its own `bb_<name>.c`.
10. **Grouped templates allowed.** N opcodes sharing emit shape → single `sm_<group>()`/`bb_<group>()` with inner `switch(op)`. All emission stays in that TU. No external helpers.
11. **INLINE-ALL complete.** Every SM/BB code-gen path lives exclusively in `SM_templates/*.c` and `BB_templates/*.c`. Adding a backend = adding `IS_NEW` arms inside existing template files only.
12. **No shadow locals in templates.** Use `_.instr->`, `_.out`, `(int)_.instr->op` inline. Loop-counter locals and computed values are fine.
13. **Entry labels belong to their template.** Each XA/SM/BB template that begins a named asm block emits its own entry label on the first line. No separate `XA_PC_LABEL` opcode — the template owns its label.
14. **x86 only for BB template ladder — 2026-05-22 (Lon directive).** All new BB_ICN_* and BB_PL_* template bodies target x86 exclusively. IS_JVM/JS/NET/WASM arms are stubs. Non-x86 opens only when Lon directs.
15. **All code emission goes through the template system via an XA_* opcode — 2026-05-22 (Lon directive).** No C function emits asm outside an SM/BB/XA template. New code blocks get a new `XA_*` opcode in `XA.h` + `XA_templates/xa_<name>.c` + `xa_dispatch()`. Direct `fprintf`/`emit_textf` outside a template = violation.

## Session State (2026-05-24d — GATE GREEN ✅ — TSX-SM-1/2/3 done)

**one4all HEAD: `dedca98f`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0.

**⚡ RUNG PURPOSE (Lon 2026-05-24d): DELETE every binary-byte-emitting function.** End state: NO `insn_*`, NO `bb_emit_byte` sink, NO `emit_seq_*`/`emit_call_sym_plt`/`emit_sym_lea_*`. Raw bytes live inline as `std::string` data in each template's `MEDIUM_BINARY` arm. `capture_bytes()` is DISCOVER scaffolding, deleted at TSX-DELETE. See TSX rung Goal block.

**NEXT: TSX-SM-4** — three-x86 SM templates: `sm_defines`, `sm_expr_incr`, `sm_returns`. Same DISCOVER pattern (capture_bytes scaffold in BINARY, MACRO_DEF + TEXT guards, one return each). Then TSX-SM-5 (sm_push_pop_lits ×4, sm_pat_combine ×5). Run `bash scripts/util_three_section_audit.sh` for the live RED list.

**Done this session (TSX-SM-1/2/3):**
- TSX-SM-1 (`734031de`+`d0ab64e2`): capture_bytes() infra in emit_str.{h,cpp} + sm_halt/calls/pat_anchors/pat_nullary three-section.
- TSX-SM-2 (`c801…`/this session): sm_exec_bb three-section (MACRO_DEF stub added).
- TSX-SM-3 (`dedca98f`): sm_jumps/arith/bb_calls/compare three-section.
- ⚠ Flagged TSX-WIRE gaps (BINARY arms emit only determinable bytes or are flagged-empty): strtab `rdi` loads (sm_calls, pat_anchors, sm_bb_once_proc), code-label rel32 (sm_jumps JUMP*, sm_bb_pump_proc), .data state-ptr (sm_exec_bb). All explicitly commented, none silent.
- Arms unreached (emit_sm.c forces TEXT_MODE) → output unchanged, GATE-PK 442/0/612 throughout.

**Remaining in DISCOVER phase:** SM-4 (sm_defines/expr_incr/returns), SM-5 (push_pop_lits/pat_combine), B1 (BB stragglers), X1 (XA). Then TSX-AUDIT → TSX-INLINE → TSX-DELETE → TSX-WIRE.

**What was found earlier (2026-05-24c — TSX-0):**
- **The binary detour is real and located.** `emit_sm.c` forces `emit_mode_set(TEXT_MODE(), out)` before every SM dispatch (lines 1280/1298/1329/1344/1361) → SM templates run ONLY in MEDIUM_TEXT. The x86 *bytes* come from a separate path: `emit_bb.c` sets `EMIT_BINARY_BROKERED`/`EMIT_BINARY_WIRED` (lines 591/596) and drives the `insn_*` family in `emit_core.c`.
- Audit tool added: `scripts/util_three_section_audit.sh` (RED until every x86 block has all three sections).

**What was done (2026-05-24b):**
- STRING-CONCAT-ALL rung added (Lon directive): finish the emitter consolidation — every low-level `emit_*()` returns std::string; callers rewired to `+` concat; walk up until every SM/BB/XA template arm is ONE `return <big concat>`; then delete all FILE*/char buf[]. One space everywhere (normalizer is whitespace-insensitive). Supersedes/completes ER wave. insn_*/reloc left for ER-8.
- SC-0 ✅ (`0a906d83`): `scripts/util_emit_inventory.sh` classifies 18 TEXT-BUILDER fns to convert vs 52 insn_* to leave. ~380 fprintf/fputs sites: emit_core.c 268, emit_sm.c 105, emit_io.c 6, emit_bb.c 1. Sharp edge: `emit_jmp` appears in both text + binary contexts — SC-converter must split it.

**Prior (2026-05-24a — THREE-MEDIUM COMPLETE) one4all HEAD: `a2324982`** ✅ 442/0/612. TM-1→TM-12 ✅. See below.

## Session State (2026-05-24 — GATE GREEN ✅ — THREE-MEDIUM rung COMPLETE)

**one4all HEAD: `a2324982`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0. Prolog BB honest 124/0/0.

**What was done (2026-05-24 — this session):**
- TM-9-fix (`6da39b14`): bb_arbno + bb_capture had no real MEDIUM_MACRO_DEF section and fired emit_comment("# BOX ...") unconditionally, leaking the banner into BOTH the binary stream and the text_macro column. Added MACRO_DEF stub ("# no macro form — NAME"); banner gated to MEDIUM_TEXT. Binary column banner bytes correctly removed. Text (non-macro) byte-identical. 6 stale baseline cells refrozen (binary + text_macro for ARBNO/ASSIGN_COND/ASSIGN_IMM).
- TM-10 (`f5521d63`): all six bb_pl_* Prolog templates (var/atom/seq/arith/builtin/unify) got MEDIUM_MACRO_DEF stub sections (rule 3). var/atom/seq fall-through TEXT arms wrapped in explicit if(MEDIUM_TEXT). Multi-branch arith/builtin/unify got MACRO_DEF stub at top of PLATFORM_X86, per-branch BINARY/TEXT splits intact. Binary + text columns byte-identical; 6 text_macro cells refrozen (full body → stub).
- TM-11 + TM-12-fix (`a2324982`): sm_halt MEDIUM_MACRO_DEF nested inside PLATFORM_X86 (was top-level, rule 5). sm_compare 2nd fn already correct; sm_stno banner is medium-aware + ER-wave scope, not a structural violation; sm_exec_bb clean single-return. TM-12 audit surfaced + fixed one real rule-5 violation: bb_capture naked top-level `if(MEDIUM_BINARY) return` (dead — MEDIUM_BINARY always implies PLATFORM_X86). TM-12 final audit: zero real violations outside PLATFORM_X86 blocks.

**⚠️ Pre-existing (NOT introduced this session):** `out/sm_codegen_x64_emit_test` harness fails to build (SM.h include path) — confirmed identical at clean HEAD via stash-test. Likely earlier header-reorg fallout. Future cleanup, out of TM scope.

**Prior (2026-05-23r) one4all HEAD: `22b2ad21`** ✅ GATE GREEN 444/0/610.

**What was done (2026-05-23p/q):**
- DM-7 (`d60c890c`): IS_* shim macros deleted from emit_core.h. All template code now uses PLATFORM_xx/MEDIUM_xx.
- Nesting fix (`3604d252`): MEDIUM_MACRO_DEF nested inside PLATFORM_X86 in sm_jumps, sm_push_pop_lits, sm_returns. No output change. NEW=0 GONE=0.

**What was done (2026-05-23r — this session):**
- THREE-MEDIUM rung opened (Lon directive). Plan written and committed: every PLATFORM_X86 block gets exactly MEDIUM_MACRO_DEF + MEDIUM_BINARY + MEDIUM_TEXT sections, each with one return. Binary detour through templates eliminated. 12 steps surveyed.
- TM-1 (`21137875`): bb_eps, bb_fail — three-section structure + binary `insn_` wiring.
- TM-2 (`ef1801d1`): bb_pat_abort, bb_pat_rem, bb_pat_pos — MACRO_DEF stubs; BINARY cleaned to label-pointer API (no text-banner-in-binary detour). Baselines refrozen.
- TM-3 (`67262e23`): bb_pat_len, bb_pat_tab — real BINARY sections using `insn_*`/`emit_add_delta_imm`/`emit_store_delta`. Baselines refrozen.
- TM-4 (`22b2ad21`): bb_pat_arb — removes `!MEDIUM_TEXT` bail; BINARY stub→fail (no rt_bb_arb yet). Baselines refrozen. GATE 444/0/610.

**DM rung status:**
- [x] DM-1 through DM-7 ✅ complete
- [ ] DM-8 — add `emit_text_and_binary_in_one()` (deferred; unblocked after TM rung lands)

**THREE-MEDIUM rung status:**
- [x] **TM-1 ✅ `21137875`** — bb_eps, bb_fail.
- [x] **TM-2 ✅ `ef1801d1`** — bb_pat_abort, bb_pat_rem, bb_pat_pos. Baselines refrozen.
- [x] **TM-3 ✅ `67262e23`** — bb_pat_len, bb_pat_tab. Baselines refrozen.
- [x] **TM-4 ✅ `22b2ad21`** — bb_pat_arb. Baselines refrozen. GATE 444/0/610.
- [x] **TM-5 ✅ `1057a3e7`** — bb_pat_fence: three-section PLATFORM_X86.
- [x] TM-6 ✅ `cc3341f6` — charset family (break/span/any/notany)
- [x] TM-7 ✅ folded into TM-6/TM-8 (cat/alt covered)
- [x] TM-8 ✅ `f868b9b9` — bb_lit naked MEDIUM_BINARY merged into PLATFORM_X86
- [x] TM-9 ✅ `e1602529`+`6da39b14` — bb_capture, bb_arbno (real MACRO_DEF, banner gated to TEXT)
- [x] TM-10 ✅ `f5521d63` — bb_pl_* family MACRO_DEF stubs
- [x] TM-11 ✅ `a2324982` — sm_halt nest; sm_compare/sm_exec_bb verified
- [x] TM-12 ✅ `a2324982` — audit clean, zero real violations. RUNG COMPLETE

**ER rung status:**
- [x] ER-0 through ER-7 ✅
- [ ] ER-8 — relocation rethink (future session). ⛔ Beauty gate SUSPENDED.

**Prior (2026-05-23l) one4all HEAD: `ace2d3ba`** — DM-1+DM-2 clean. GATE-PK 419/0/635 ✅.

**Prior (2026-05-23i) one4all HEAD: UNCOMMITTED** — ALL BB templates now return std::string. ER-3 (INLINE-TEXT) and ER-4 (DELEGATING + JVM/NET arms) complete for all BB_templates. Seven .c files converted to .cpp and old .c files deleted: bb_pat_notany, bb_pat_span, bb_pat_break, bb_lit, bb_pat_alt, bb_pat_cat, bb_arbno. Normalizer upgraded. GATE-PK 419/0/635 ✅.

**Prior (2026-05-23f) one4all HEAD: `8a3b4b39`** — CPP rung opened (return-String emitter conversion, Lon-amended: skip mechanical CPP-0, go straight to return-String). Four BB templates converted to C++ returning std::string: bb_pat_abort (`bc83802c`, + emit_str.{h,cpp} infra + emit_text_n + g++ link + shared-header C++ fixes), bb_pat_fence (`8db542bb`), bb_pat_rem (`90425d4a`), bb_pat_len (`8a3b4b39`, first data-computed, via baseline-shape method). Shape: text arms concatenate (`s_comment(...) + s_2asm(...) + ...`); IS_BIN/relocation/jvm_*/net_* arms stay imperative. Loop-fold shape proven in isolation. Terrain mapped (INLINE-TEXT vs DELEGATING x86 arms — see CPP-2). GATE-PK 419/0/635 NEW=0 GONE=0. GATE-M 11 / GATE-E gate1_beauty+gate4_icon — pre-existing, no new regressions. ⚠ MERGE-GATED shared headers touched (byte-neutral): BB.h, emit_core.h, snobol4.h — self-tag typedefs + rename typename param for C++ compat. ⛔ Beauty gate remains SUSPENDED.

**Prior (2026-05-23e) one4all HEAD: `88cb6fe2`** — SJ-1c: reverted SJ-1b-sweep's wrongful funnel conversion of IS_JS/IS_WASM arms (it had violated the x86-only directive — routed JS/WASM through asm funnels + sm_returns.c WASM_FNRET* macros, added spurious leading space, destroyed WASM 10-space indent, and changed sm_returns WASM bytes). Restored all JS/WASM arms to pre-sweep (336cb7e1) one-emit_textf-per-line form; restored js/wasm per-kind baselines from 336cb7e1; removed orphaned WASM_FNRET* macros. x86/JVM/NET funnel work preserved. 26 source files + 142 baseline cells. GATE-PK 419/0/635 NEW=0 GONE=0.

**Prior (2026-05-23d) one4all HEAD: `f6b0be23`** — SJ-1b-reindent: restored C source indentation in the 18 SM/BB/XA template files where SJ-1b-sweep split multi-line `emit_textf` blobs into per-line funnel calls but dropped leading whitespace. Brace-depth 4-space re-indent, whitespace-only. 18 files, 1448/1448. GATE-PK 419/0/635.

**Prior (2026-05-23c) one4all HEAD: `326a4fac`** — SJ-1b-sweep COMPLETE. All emit_textf in SM_templates (14 files), BB_templates (22 files), XA_templates (4 files) converted to emit_io funnels (x86/JVM/NET; JS and WASM untouched per Lon directive — ⚠ but in fact JS/WASM WERE wrongly touched; fixed in SJ-1c). Baselines refrozen. 593 files changed, 7679 ins / 6329 del.

**Gate: GATE-PK PASS=419 FAIL=0 STUB=635 ✅**

**STYLE-FUNNEL-ALL-ASM (SJ-1) STATUS:**
- ✅ SJ-1a funnels landed (`2ef4847f`)
- ✅ SJ-1b funnel rework + six-function API
- ✅ SJ-1b-sweep: ALL backends (x86/JVM/NET) routed through funnels; baselines refrozen

**NEXT:** ⚠️ Fix audit segfault (DM-3/4/5 broken at `e2fabcff`) — trace which BB kind/backend crashes, fix `emit_mode_set(NULL)` binary path, then gate green. ⛔ Beauty gate SUSPENDED.


## Active Rungs

### ⚡ EMIT-RETURNS-STRING — All emit_*() functions return std::string (2026-05-23g Lon directive)

**Goal:** Convert the emitter pipeline from imperative (write to FILE*/buffer) to functional (all functions return `std::string`). Then wire callsites to concatenate strings bottom-up until every SM/BB/XA template returns ONE BIG STRING combining all pieces.

**Why this matters:** (a) facilitates Snocone translation later (Snocone has `.` concat; C++ `+` is isomorphic). (b) makes emitted code testable as pure data (no FILE side-effects). (c) unlocks future parallelization (pure strings vs mutable FILE* patches). (d) eliminates all relocation-patch list machinery once string concat replaces FILE writes.

**Invariant:** GATE-PK 419/0/635 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged.

**Three-wave strategy:**

1. **WAVE-1: Convert low-level emit_*() helpers to return string.** Starts with `emit_str.h` (already started): `s_comment`, `s_directive`, `s_1asm`/`s_2asm`/`s_3asm`/`s_L1asm`/`s_L2asm`/`s_L3asm`, `emit_fmt` (variadic-wrapper around snprintf). These are the LEAF emitters — they concatenate fixed text + interpolated variables and return `std::string`. Imperative arms (FILE* write, relocation patch) stay as-is for now, return `""`.

2. **WAVE-2: Rewrite all BB/SM template callsites to use returned strings.** Each template function becomes `static std::string TEMPLATE_str(...)` that returns `s_comment(...) + s_1asm(...) + ... + s_fmt(...)`. The extern "C" wrapper stays imperative: `void TEMPLATE(...) { auto s=TEMPLATE_str(...); if(!s.empty()) emit_text_n(s.data(),s.size()); }`. Walk up the call chain: first convert leaves (INLINE-TEXT files like bb_pat_abort, bb_pat_fence, bb_pat_rem, bb_pat_len, bb_pat_arb, bb_pat_tab, bb_pat_rtab), then the DELEGATING helpers (bb_charset_emit, jvm_*/net_* layer-2 — these become string-returners; x86 arms call them and concat the result). Once a helper returns string, every caller that uses it must also return string (transitive).

3. **WAVE-3: Delete FILE* and buffer locals.** Once all code paths return string, delete `FILE *out`, `char buf[...]`, `fprintf`, `snprintf` (except in helpers that STILL need imperative mode for relocation). The template is ONE statement: `return concat(piece1, piece2, ..., pieceN);` where each piece is a helper call or string literal.

**Sub-steps (each atomic, gate-green):**
- [x] **ER-0 — build spike. ✅** Infrastructure: `emit_str.{h,cpp}` with s_comment, s_directive, s_Nasm family, emit_fmt. g++ link wired. bb_pat_abort proof-of-concept.
- [x] **ER-1 — emit_str.h API complete. ✅** All JVM/NET/charset helpers have string-returning _str versions. GATE-PK 419/0/635 ✅.
- [x] **ER-2 — normalizer upgraded. ✅ 2026-05-23i.** normalize_per_kind_cell.py now squeezes ALL whitespace (indent, newlines) to single spaces before compare. Only token order matters. Baselines refrosen. GATE-PK 419/0/635 ✅.
- [x] **ER-3 — ALL BB_templates converted to .cpp returning std::string. ✅ 2026-05-23i.** All 15 BB template files are now .cpp. Every backend arm (x86/JVM/NET/JS/WASM) returns std::string. IS_X86 arms that use imperative helpers (bb_charset_emit, emit_flat_ir, pointer laundering) return empty string after side-effecting. Extern "C" wrappers call emit_text_n. Old .c files deleted. GATE-PK 419/0/635 ✅.
- [x] **ER-5 — SM_templates to .cpp returning std::string. ✅ 2026-05-23j.** All 14 SM template files converted. Same pattern as BB. Imperative-insn hazard found and fixed: sm_defines DEFINE_ENTRY x86 path calls insn_push_rbp/mov_rbp_rsp which emit directly — wrapper emits string first, then fires insns. Old .c files deleted. GATE-PK 419/0/635 ✅. one4all `71d310c8`.
- [x] **ER-6 — XA_templates to .cpp returning std::string. ✅ 2026-05-23k.** 12 files converted. True string-returners: xa_prologue, xa_epilogue, xa_bb_ptr_slot, xa_exec_stmt_blob. Imperative (return ""): xa_file_header, xa_macro_library, xa_bb_macro_library, xa_rodata, xa_flat, xa_wasm_main, xa_js_label_register. Old .c files deleted. GATE-PK 419/0/635 ✅. one4all `26915a26`.
- [x] **ER-7 — delete FILE* / buffer locals. ✅ 2026-05-23k.** SM/BB templates confirmed clean. XA FILE* locals are all active imperative I/O — not dead, deferred to ER-8. GATE-PK 419/0/635 ✅.
- [ ] **ER-8 — relocation rethink (future session).** Collect relocation records alongside string output, apply patches in second pass. Unblocks pure-functional emitters.

```
**⛔ BEAUTY GATE SUSPENDED** during BB template consolidation.

---

### ⚡ DECOMPOSE-MODE — Replace bb_emit_mode with orthogonal globals (2026-05-23l Lon directive)

**Goal:** Decompose the single `bb_emit_mode` enum into five orthogonal boolean-flag globals so template arms read `if (PLATFORM_X86) { ... }` instead of `if (bb_emit_mode == EMIT_TEXT || ...)`. Eliminates the conflation of platform, medium, and sub-switches into one integer.

**Design (from Lon, 2026-05-23l session):**

**5 platforms** (outer shell, mutually exclusive):
- `PLATFORM_X86`, `PLATFORM_JVM`, `PLATFORM_NET`, `PLATFORM_JS`, `PLATFORM_WASM`

**3 mediums** (orthogonal to platform; JS/WASM are TEXT-only — no BINARY or MACRO_DEF):
- `MEDIUM_TEXT` — human-readable formatted assembly / bytecode text
- `MEDIUM_BINARY` — raw machine/bytecode instructions
- `MEDIUM_MACRO_DEF` — macro definition pass (preamble); parallel to TEXT/BINARY, same order across X86/JVM/NET

**X86-only sub-switches:**
- `BB_BROKERED` / `BB_WIRED` — BB connectivity mode
- `USE_SM_MACROS` — true: SM opcodes emit a macro call (human-readable); false: raw inline instructions per opcode
- `USE_BB_MACROS` — future: whole BB box gets one macro call (currently always false)

**BB rule (current):** BBs never use a macro for the whole box, never use macros inside a box, always formatted so Lon can read them. `USE_BB_MACROS` is always false for now.

**Key function:** `emit_text_and_binary_in_one(op, arg, ...)` — given an operation and arguments, produces:
- macro call text when `USE_SM_MACROS`
- raw instruction sequence when `!USE_SM_MACROS`
- macro definition body when `MEDIUM_MACRO_DEF`
All three representations live inside this one function — no gap between defining and calling macros.

**Predicate style — NO `==`, single flag tests only:**
```c
if (PLATFORM_X86)    { ... }   // not: if (platform == PLATFORM_X86)
if (MEDIUM_BINARY)   { ... }
if (USE_SM_MACROS)   { ... }
if (BB_BROKERED)     { ... }
```

**Old → new mapping:**
| old `bb_emit_mode`      | PLATFORM  | MEDIUM     | USE_SM_MACROS | BB_BROKERED |
|-------------------------|-----------|------------|---------------|-------------|
| `EMIT_TEXT`             | X86       | TEXT       | false         | false       |
| `EMIT_TEXT_INLINE`      | X86       | TEXT       | true          | false       |
| `EMIT_MACRO_DEF`        | X86       | MACRO_DEF  | —             | —           |
| `EMIT_BINARY_WIRED`     | X86       | BINARY     | —             | false       |
| `EMIT_BINARY_BROKERED`  | X86       | BINARY     | —             | true        |
| `EMIT_JVM`              | JVM       | TEXT       | —             | —           |
| `EMIT_JS`               | JS        | TEXT       | —             | —           |
| `EMIT_NET`              | NET       | TEXT       | —             | —           |
| `EMIT_WASM`             | WASM      | TEXT       | —             | —           |

**Invariant:** GATE-PK 419/0/635 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged throughout migration.

**Sub-steps (each atomic, gate-green):**
- [x] **DM-1 — add new globals/enums/defines to emit_core.h. ✅ ace2d3ba.** New enums: `bb_platform_t` (5 values), `bb_medium_t` (3 values). New extern globals: `g_platform`, `g_medium`, `g_bb_brokered`, `g_use_sm_macros`, `g_use_bb_macros`. New predicates: `PLATFORM_X86/JVM/NET/JS/WASM`, `MEDIUM_TEXT/BINARY/MACRO_DEF`, `BB_BROKERED`, `BB_WIRED`, `USE_SM_MACROS`, `USE_BB_MACROS`. Old `bb_emit_mode` + `IS_*` macros kept as compatibility shims. GATE-PK 419/0/635 ✅.
- [x] **DM-2 — implement globals + emit_mode_set() in emit_core.c. ✅ ace2d3ba.** All five globals defined. `emit_mode_set()` writes all five atomically from old `bb_emit_mode_t`. GATE-PK 419/0/635 ✅.
- [ ] **DM-3 — migrate BB_templates to new predicates. ⚠️ BROKEN e2fabcff.** sed sweep done (15 files). Audit segfaults — fix before gate. See session state for debug strategy.
- [ ] **DM-4 — migrate SM_templates to new predicates. ⚠️ BROKEN e2fabcff.** sed sweep done (14 files). Same commit as DM-3.
- [ ] **DM-5 — migrate XA_templates to new predicates. ⚠️ BROKEN e2fabcff.** sed sweep done (12 files). Same commit as DM-3.
- [ ] **DM-6 — migrate emit_core.c / emit_sm.c / emit_bb.c / emit_io.c helpers.** All remaining `IS_*` / `bb_emit_mode ==` sites in non-template emitter files.
- [ ] **DM-7 — delete bb_emit_mode shims.** Remove old enum values, old `IS_*` macros, old `bb_emit_mode` global. GATE-PK green. Build with `-Werror` to confirm no stragglers.
- [ ] **DM-8 — add emit_text_and_binary_in_one().** New function in emit_str.h/.cpp: given opcode + args, returns string representing macro-call, raw-inline, or macro-def body based on `USE_SM_MACROS` + `MEDIUM_*`. Migrate first SM template to use it as proof-of-concept. GATE-PK green.

---

### ⚡ THREE-MEDIUM — Every PLATFORM_X86 block has exactly three medium sections (2026-05-23r Lon directive)

**Goal:** Every `if (PLATFORM_X86)` block in every BB/SM/XA template must contain exactly three sub-sections in this order:
```cpp
if (PLATFORM_X86) {
    if (MEDIUM_MACRO_DEF) { /* macro definition text */   return ...; }
    if (MEDIUM_BINARY)    { /* insn_* byte emission */    return std::string(); }
    if (MEDIUM_TEXT)      { /* s_*asm string concat */    return ...; }
}
```
**Rules:**
1. Each medium section has **ONE and ONLY ONE** `return` statement.
2. `MEDIUM_BINARY` sections call `insn_*` / `emit_jmp` / `emit_label_define` / `emit_seq_*` — the real binary byte emitters — then `return std::string()`. No stubs, no `TODO`.
3. `MEDIUM_MACRO_DEF` sections emit macro-definition text (`.macro`/`.endm` wrappers). BB templates that have no meaningful macro form emit a comment stub: `return s_comment("# no macro form");`.
4. `MEDIUM_TEXT` sections return a `std::string` concatenation using `s_*asm` / `s_comment` / `emit_fmt` helpers.
5. No `MEDIUM_*` or `BB_WIRED`/`BB_BROKERED`/`USE_SM_MACROS` predicate appears **outside** a `PLATFORM_X86` block. Top-level naked guards are a structural error.
6. Early-exit guards (`if (!MEDIUM_TEXT) return std::string()`) are replaced by the three-section structure.
7. **Invariant:** GATE-PK 442/0/612 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged.

**Affected files (surveyed 2026-05-23r):**

BB templates missing MEDIUM_BINARY (binary detoured around template):
- `bb_eps.cpp`, `bb_fail.cpp` — X86 block is text-only; no binary section
- `bb_pat_len.cpp` — X86 block is text-only; no binary section
- `bb_pat_arb.cpp` — `if (!MEDIUM_TEXT) return` bail; MEDIUM_BINARY absent
- `bb_pat_fence.cpp` — X86 block unsplit; no medium sections
- `bb_pat_break.cpp`, `bb_pat_span.cpp`, `bb_pat_any.cpp`, `bb_pat_notany.cpp` — X86 unsplit
- `bb_pat_cat.cpp`, `bb_pat_alt.cpp` — X86 unsplit, multiple returns
- `bb_pat_tab.cpp` — X86 unsplit

BB templates with structural violations (naked top-level guards):
- `bb_lit.cpp` — naked top-level `if (MEDIUM_BINARY)` block outside PLATFORM_X86; must merge into X86 section
- `bb_capture.cpp` — naked top-level `if (MEDIUM_BINARY) return std::string()` guard; X86 block uses `!MEDIUM_BINARY` tangling

SM templates with structural violations:
- `sm_halt.cpp` — `MEDIUM_MACRO_DEF` at top level before any PLATFORM guard; must nest inside PLATFORM_X86
- `sm_compare.cpp` (first function) — X86 block unsplit
- `sm_exec_bb.cpp` — X86 block unsplit

**Sub-steps (each atomic, gate-green):**

- [x] **TM-1 ✅ `21137875` — simple BB stubs: eps, fail.** Add three-section structure. MEDIUM_BINARY: `emit_jmp(_.lbl_succ_p/fail_p, JMP_JMP)` + `emit_label_define(_.lbl_back_p)` + `emit_jmp(_.lbl_fail_p, JMP_JMP)`. MEDIUM_MACRO_DEF: `return s_comment("# no macro form")`. GATE-PK green.

- [x] **TM-2 ✅ `ef1801d1` — bb_pat_abort, bb_pat_rem, bb_pat_pos.** Already have MEDIUM_BINARY. Add MEDIUM_MACRO_DEF stub. Restructure to strict three-section order with one return each. GATE-PK green.

- [x] **TM-3 ✅ `67262e23` — bb_pat_len, bb_pat_tab.** Add MEDIUM_BINARY using `insn_*` sequence mirroring the TEXT arm logic. Add MEDIUM_MACRO_DEF stub. One return each. GATE-PK green.

- [x] **TM-4 ✅ `22b2ad21` — bb_pat_arb.** Remove `if (!MEDIUM_TEXT) return` bail. Add MEDIUM_BINARY (port the TEXT arm to `insn_*` calls). Add MEDIUM_MACRO_DEF stub. GATE-PK green.

- [x] **TM-5 ✅ `1057a3e7` — bb_pat_fence.** Three-section split of existing X86 block. MEDIUM_BINARY section: `emit_flat_ir` path already handles binary implicitly — verify then wire. GATE-PK green.

- [x] **TM-6 ✅ `cc3341f6` — bb_pat_break, bb_pat_span, bb_pat_any, bb_pat_notany.** Charset-family: all use `bb_charset_helper`. Add MEDIUM_BINARY section calling the binary charset helper path. MEDIUM_MACRO_DEF stub. One return each. GATE-PK green.

- [x] **TM-7 ✅ folded→TM-6/8 — bb_pat_cat, bb_pat_alt.** Structural split + single-return discipline. MEDIUM_BINARY sections use `emit_flat_ir` binary path. MEDIUM_MACRO_DEF stubs. GATE-PK green.

- [x] **TM-8 ✅ `f868b9b9` — bb_lit.** Merge naked top-level `if (MEDIUM_BINARY)` block into PLATFORM_X86 section. Restructure to strict three-section order. GATE-PK green.

- [x] **TM-9 ✅ `e1602529`+`6da39b14` — bb_capture, bb_arbno.** Fix naked top-level `if (MEDIUM_BINARY)` guards. Restructure X86 block to three-section order with one return each. GATE-PK green.

- [x] **TM-10 ✅ `f5521d63` — bb_pl_* family.** `bb_pl_var`, `bb_pl_atom`, `bb_pl_seq`, `bb_pl_arith`, `bb_pl_builtin`, `bb_pl_unify`. Already have MEDIUM_BINARY sections. Add MEDIUM_MACRO_DEF stubs. Enforce single-return discipline per section. GATE-PK green.

- [x] **TM-11 ✅ `a2324982` — SM violations: sm_halt, sm_compare, sm_exec_bb.** Move `sm_halt`'s top-level `MEDIUM_MACRO_DEF` inside `PLATFORM_X86`. Add MEDIUM_BINARY sections. Enforce three-section order. GATE-PK green.

- [x] **TM-12 ✅ `a2324982` — audit pass.** `grep -rn "MEDIUM_\|BB_WIRED\|BB_BROKERED\|USE_SM_MACROS"` across all template files; confirm zero hits outside a `PLATFORM_X86` block. GATE-PK green. Commit.

---

### ⚡ STRING-CONCAT-ALL — Every emit_*() returns string; every template is ONE concat per platform (2026-05-24 Lon directive)

**Goal (Lon, verbatim intent):** Make a consolidated emitter system. Rewrite ALL low-level `emit_*()` functions that build code so they RETURN `std::string`. Refactor every caller to use them via the `+` string-concatenation operator. Walk UP the chain — convert leaf emitters first, then their callers, transitively — until every top-level SM/BB/XA template function returns a string. Once every `emit_*()` returns a string, DELETE all `FILE *out` parameters/locals and every `char buf[...]` that was being filled (the returned string replaces them). Each template's per-platform arm collapses to exactly ONE statement: `return <ONE BIG CONCAT of helpers + emit_fmt() + globals>`. Structure stays `if (PLATFORM_X86) { return BIGCONCAT; } if (PLATFORM_JVM) { return BIGCONCAT; } ...` — one return per platform arm, no locals, no intermediate buffers.

**Formatting rule (Lon):** There is NO formatting to preserve. Do not worry about matching exact whitespace. ONE space wherever a space is needed, nothing more. The per-kind gate normalizer already squeezes all whitespace to single spaces (ER-2), so token order is the only invariant — NOT byte-exact spacing. This frees every step from whitespace-matching busywork.

**Relationship to prior waves:** This SUPERSEDES and completes EMIT-RETURNS-STRING (ER-0→7 built the `s_*`/`emit_fmt` leaf helpers and converted the templates to `.cpp` returning string, but ~380 imperative FILE writes remain in emit_core.c / emit_io.c / emit_sm.c / emit_bb.c, and the templates still CALL imperative middle-layer emitters — `emit_text_jmp`, `emit_text_label`, `emit_seq_port_call*`, `emit_comment`, etc. — that side-effect to FILE and return void). STRING-CONCAT-ALL finishes the job from the leaves all the way up, then deletes the imperative machinery.

**Two emitter populations — handle differently:**
1. **Text/format emitters** (the ~380 fprintf/fputs/emit_text_* sites): these BUILD code text. They are the target — convert to return string.
2. **Binary byte emitters** (`insn_*` family, 52 fns; relocation-patch writers): these patch a machine-code byte buffer for relocation. They are NOT text-builders. They stay imperative for now and are the ER-8 relocation-rethink concern. A MEDIUM_BINARY section may still call `insn_*` and `return std::string()`. Do NOT try to stringify binary byte emission in this rung.

**Invariant:** GATE-PK 442/0/612 NEW=0 GONE=0 after every committed sub-step (normalizer is whitespace-insensitive, so only token content matters). Prolog BB honest 124/0/0 where touched.

**Method — one piece at a time, leaves first:**
- For each imperative text emitter `void emit_X(FILE*, args)`: add a sibling `std::string emit_X_str(args)` that returns the text it would have written. Keep the old `void emit_X(...)` as a thin wrapper: `void emit_X(FILE *f, args){ std::string s = emit_X_str(args); fwrite(s.data(),1,s.size(),f); }` — so existing callers keep working while migration proceeds.
- Then rewrite each CALLER to use `emit_X_str(args)` inside its own returned concat, dropping the FILE* threading. When the last caller of an old `void emit_X` is gone, delete the wrapper.
- Walk up: a function is "done" when it returns string and all the emitters it calls return string. The transitive frontier moves from leaves (emit_str.h — already done) through the middle layer (emit_text_*, emit_seq_*, emit_comment) up to the templates (already string-returning shells, but still calling imperative middle-layer fns).
- Final collapse: once a template arm calls only string-returners, fold it into a single `return a + b + c + ... ;` with NO locals and NO `emit_text_n` side-effect call in the extern "C" wrapper beyond the final `emit_text_n(s.data(), s.size())`.

**Sub-steps (each atomic, gate-green; commit after each):**

- [ ] **SC-0 — inventory + classify.** Produce `scripts/util_emit_inventory.sh` (or a one-off audit) listing every `emit_*` / `s_*` symbol in emit_core.{c,h}, emit_io.{c,h}, emit_sm.{c,h}, emit_bb.{c,h}, emit_str.{h,cpp}, tagged TEXT-BUILDER (convert) vs BINARY/RELOC (leave). Output the call-graph depth so leaves are converted first. Commit the inventory doc. No code change. GATE-PK green (trivially).

- [ ] **SC-1 — middle-layer text emitters → _str siblings (batch 1: jmp/label/comment).** Add `emit_text_jmp_str`, `emit_text_label_str`, `emit_comment_str` (returning string) beside the existing void versions (void becomes a wrapper that writes the string). No callers rewired yet. GATE-PK green.

- [ ] **SC-2 — rewire BB template callers of batch-1 emitters.** In every BB template that calls `emit_text_jmp/label`+`emit_comment` inside a MEDIUM section, replace the side-effecting call with concatenation of the `_str` result into that section's single returned string. Delete the now-unused local string-then-emit_text_n patterns. GATE-PK green.

- [ ] **SC-3 — port-call sequence emitters → _str (batch 2).** `emit_seq_port_call_str`, `emit_seq_port_call_rip_str`. These currently emit a multi-instruction sequence to FILE; the _str version returns the full text sequence. (The binary-mode counterpart still routes through insn_*/reloc — leave it.) Wrapper preserved. GATE-PK green.

- [ ] **SC-4 — rewire arbno/capture/pl_* TEXT arms to batch-2 _str.** The MEDIUM_TEXT arms of bb_arbno, bb_capture, bb_pl_* currently call `emit_seq_port_call_rip` imperatively then `return std::string()`. Convert each to `return emit_seq_port_call_rip_str(...) + ...;` — one concat, no side-effect. MEDIUM_BINARY arms keep calling the imperative seq emitter (reloc). GATE-PK green. Prolog BB honest 124/0/0.

- [ ] **SC-5 — emit_core.c text helpers → _str (batch 3).** `emit_text_global`, `emit_text_stno_banner`/`emit_banner_stno`, `emit_directive`, and the remaining EMIT_TEXT/EMIT_MACRO_DEF arms of the ~380 fprintf sites that build TEXT (NOT the binary/reloc arms). Each gets a `_str`. sm_stno's banner side-effect (flagged in TM-11) is resolved HERE: `return emit_banner_stno_str(...) + s_2asm(...) + ...;`. GATE-PK green.

- [ ] **SC-6 — rewire SM template callers of batch-3.** All SM templates that still side-effect a banner/global/directive before returning: fold into the single returned concat. GATE-PK green.

- [ ] **SC-7 — XA template text emitters → _str + rewire.** xa_file_header, xa_macro_library, xa_rodata, xa_flat, xa_wasm_main, xa_js_label_register currently return "" after imperative FILE writes. Convert the text-building ones to return string; rewire xa_dispatch and callers. (Any that emit binary/reloc stay imperative.) GATE-PK green.

- [ ] **SC-8 — delete FILE* params/locals from converted paths.** Once a function and all it calls return string, remove its `FILE *out`/`FILE *f` parameter and any `char buf[...]`. Update signatures up the chain. The extern "C" wrapper is the ONLY place left that calls `emit_text_n(s.data(), s.size())`. Build with `-Werror=unused` to catch dead buffers. GATE-PK green.

- [ ] **SC-9 — collapse each template arm to ONE concat.** Final pass: every `if (PLATFORM_X) { ... }` arm in every SM/BB/XA template is rewritten to a single `return PIECE1 + PIECE2 + ... + PIECEN;` statement. No locals except loop counters / computed scalars feeding emit_fmt. No intermediate std::string locals that are built up line-by-line — fold them into the concat. GATE-PK green.

- [ ] **SC-10 — final audit + delete dead imperative emitters.** grep for any remaining `fprintf|fputs|fwrite` in emit_core/io/sm/bb OUTSIDE the binary/reloc paths and the single emit_text_n sink — confirm zero text-builder FILE writes remain. Delete every now-unused `void emit_X(FILE*,...)` wrapper. `insn_*` and relocation writers remain (ER-8 territory). GATE-PK green. Commit. RUNG COMPLETE → hands off to ER-8 (relocation rethink) for the binary side.

**Out of scope (explicitly):** binary byte emission (`insn_*`), relocation patch lists — those are ER-8. JVM/JS/NET/WASM build-out — those are Milestone 3 / RULES x86-only directive (their arms already return string from the ER wave; this rung keeps them string-returning but does not expand them).

---

### ⚡ THREE-SECTION-X86 (TSX) — DELETE all binary-byte-emitting functions; raw bytes go inline in each template's MEDIUM_BINARY arm (2026-05-24c Lon directive, purpose clarified 2026-05-24d)

**The defect (confirmed by audit 2026-05-24c):** THREE-MEDIUM (TM rung) closed having fixed the BB pattern/charset/pl families, but **the binary byte stream is detoured around the templates entirely.** Root cause in `emit_sm.c`: the SM walker hard-codes `emit_mode_set(TEXT_MODE(), out)` before EVERY dispatch (lines 1280/1298/1329/1344/1361), so SM templates are *only ever invoked in MEDIUM_TEXT.* The actual x86 bytes come from the separate `emit_bb.c` binary path (`EMIT_BINARY_BROKERED`/`EMIT_BINARY_WIRED`, lines 591/596) driving the `insn_*` family in `emit_core.c`. Consequence: **all 14 SM templates have a `MEDIUM_MACRO_DEF` section and a bare unguarded TEXT return, but ZERO `MEDIUM_BINARY` sections.** Most XA templates have no medium structure at all. A few BB templates also lack an explicit `MEDIUM_TEXT` guard or the charset binary section.

**Goal — THE PURPOSE IS DELETION:** The end state of this rung is that **every function that emits raw binary bytes is DELETED**, and at each former call site the **actual raw bytes themselves** appear inline as string-literal data folded into the template's `MEDIUM_BINARY` return concat. We do not want byte-emitting *functions* at all — not `insn_*`, not `bb_emit_byte`/`bb_emit_u32`/`bb_emit_u64`, not `emit_seq_port_call*`, not `emit_call_sym_plt`, not `emit_sym_lea_*`, not the binary arms of `emit_jmp`/`emit_label_define`. The binary form of an opcode is just *its bytes*, and bytes are data, so they belong in the string concat exactly like the text form's characters do — `MEDIUM_BINARY` returns a `std::string` of raw byte values, `MEDIUM_TEXT` returns a `std::string` of assembly characters, and they are the same kind of thing. When the rung completes, the entire `insn_*` family (52 functions per SC-0 inventory) and the byte-sink machinery underneath it are gone; the only place x86 bytes exist is as inline data inside the `MEDIUM_BINARY` arms of the templates.

Every compiled template (`.cpp` only — the `.c` siblings are stale, not in the Makefile) that has a `PLATFORM_X86` block must contain, INSIDE that block, exactly three sections in this order, each with **ONE and ONLY ONE** `return`:
```cpp
if (PLATFORM_X86) {
    if (MEDIUM_MACRO_DEF) { return <macro-def text concat>; }
    if (MEDIUM_BINARY)    { return <RAW BYTES as a std::string>; }   // data, not function calls
    if (MEDIUM_TEXT)      { return <s_*asm text concat>; }
}
```

**Two-phase method to get there (per template arm):**
1. **DISCOVER** (TSX-SM-*, TSX-B*, TSX-X*): temporarily express `MEDIUM_BINARY` as `return capture_bytes([&]{ insn_foo(); insn_bar(x); });`. `capture_bytes()` (emit_str.cpp) runs the existing `insn_*` emitters into a scratch buffer and hands back the produced bytes as a `std::string`. This is *scaffolding* — it lets us read off the exact byte sequence for each opcode using the already-trusted encoders, while keeping every step gate-green. It is NOT the destination.
2. **INLINE + DELETE** (TSX-INLINE, then TSX-WIRE): replace each `capture_bytes([&]{ insn_… })` with the literal bytes it produces, expressed as inline `std::string` data (e.g. a `bytes("\x48\xB8…\xFF\xD0")` helper or `emit_fmt`-built byte string for the parts that interpolate an address/immediate). Once no template arm references any `insn_*` (or `capture_bytes`, or the byte sink), **DELETE all of them**: the whole `insn_*` family, `bb_emit_byte`/`bb_emit_u32`/`bb_emit_u64`/`bb_emit_begin`, `emit_seq_port_call*`, `emit_call_sym_plt`, `emit_sym_lea_*`, the binary arms of `emit_jmp`/`emit_label_define`, and finally `capture_bytes` itself. Build with `-Werror=unused` / linker to confirm nothing references them.

**Addresses & immediates:** a raw-byte literal is fixed data EXCEPT where it embeds a runtime address (e.g. the 8-byte `rt_halt_tos` pointer in `mov rax,imm64`) or an instruction-relative displacement. Those bytes are produced by `emit_fmt`/byte-builder from the live value at emit time — still inline data construction in the template, still no helper function. (Relocation-style displacements that depend on final layout remain the ER-8/TSX-WIRE concern; flag them, do not invent a helper.)

**Then the detour is opened (TSX-WIRE):** `emit_sm.c` stops forcing `TEXT_MODE()` so that in a binary mode the SM walker dispatches templates in `MEDIUM_BINARY` and the inline bytes ARE the output. The old `emit_bb.c` binary path that drove `insn_*` is deleted along with the functions.

**Rules (inherit TM rules 1-6, plus):**
1. ONE and ONLY ONE `return` per medium section. Multi-branch opcodes (switch on `op`) collapse to a single return whose value is computed by the switch — no early returns inside a section.
2. **End state has NO byte-emitting functions.** During DISCOVER, `MEDIUM_BINARY` may call `capture_bytes(insn_*)` as scaffolding; by TSX-INLINE it must be raw inline byte data; by TSX-WIRE every `insn_*` and the byte sink are deleted. A stub-fail is permitted only where the runtime helper genuinely does not exist yet (e.g. `rt_bb_arb`) and must be explicitly flagged, never silent.
3. MEDIUM_MACRO_DEF with no meaningful macro form: `return s_comment("# no macro form — NAME");`.
4. No `MEDIUM_*`/`BB_*`/`USE_*` predicate outside a `PLATFORM_X86` block (TM rule 5).
5. The bare unguarded TEXT return in every SM template (the `return {s_2asm(...)...}` after the MACRO_DEF block) must be wrapped in `if (MEDIUM_TEXT) { ... }`.
6. **Invariant:** GATE-PK 442/0/612 NEW=0 GONE=0 after every committed sub-step. Output bytes unchanged (normalizer whitespace-insensitive). The binary path opening (TSX-WIRE) is the ONE step that can change emitted *binary* — gated separately by a mode-4 / byte-compare against the pre-deletion `insn_*` output, not GATE-PK text.

**Audit tool:** `bash scripts/util_three_section_audit.sh` — lists every compiled template's section presence; exits RED until all x86 blocks have three sections. Run at start and end of every sub-step.

**Work list (from audit 2026-05-24c — RED files only):**

*SM templates (all 14 missing BINARY + TEXT-guard — the core of the detour):*
- `sm_halt` (1 x86), `sm_calls` (1), `sm_pat_anchors` (1), `sm_pat_nullary` (1), `sm_exec_bb` (1, also missing MACRO_DEF)
- `sm_jumps` (2), `sm_arith` (2), `sm_bb_calls` (2), `sm_compare` (2)
- `sm_defines` (3), `sm_expr_incr` (3), `sm_returns` (3)
- `sm_push_pop_lits` (4)
- `sm_pat_combine` (5)

*BB templates (partial):*
- `bb_charset_helper` — missing MACRO_DEF + TEXT-guard (it is a helper, not a top-level op; may need exemption — decide in TSX-B1)
- `bb_pat_alt`, `bb_pat_cat` — missing BINARY + TEXT-guard (they delegate to emit_flat_ir; verify the binary really flows)
- `bb_pl_arith`, `bb_pl_builtin`, `bb_pl_unify` — have BINARY, missing explicit TEXT-guard (wrap bare TEXT return)

*XA templates (missing all medium structure):*
- `xa_macro_library` (has MACRO_DEF only), `xa_bb_macro_library`, `xa_bb_ptr_slot`, `xa_exec_stmt_blob`, `xa_file_header`, `xa_flat`, `xa_rodata` — these emit file-structural text/data, not per-opcode code; many are legitimately TEXT-or-MACRO_DEF-only. Each needs a ruling: does it participate in MEDIUM_BINARY at all? (XA = assembler-file scaffolding; likely most get a `MEDIUM_BINARY { return std::string(); }` no-op section + explicit TEXT guard, NOT real bytes.) Decide per-file in TSX-X.

**Sub-steps (each atomic, gate-green; commit after each):**

The TSX-SM-*/B*/X* steps are the **DISCOVER** phase — they give every x86 arm its three-section shape, with `MEDIUM_BINARY` expressed as `capture_bytes([&]{ insn_… })` scaffolding so the byte sequences are read off the trusted encoders while staying gate-green (the arms are unreached until TSX-WIRE, so output is unchanged). TSX-INLINE then turns that scaffolding into raw inline byte data, and TSX-DELETE removes every byte-emitting function. TSX-WIRE opens the detour so the inline bytes become the actual binary output.

- [x] **TSX-0 — audit tooling + inventory. ✅** `scripts/util_three_section_audit.sh` written; full RED inventory captured above; detour root-caused to `emit_sm.c` forced `TEXT_MODE()` + separate `emit_bb.c` binary path. No code change beyond the audit script. GATE-PK unchanged 442/0/612.
- [x] **TSX-SM-1 ✅ `734031de`+`d0ab64e2` — single-x86 SM templates + `capture_bytes()` infra.** Added `capture_bytes()` to emit_str.{h,cpp} (DISCOVER scaffold: runs an `insn_*` lambda in EMIT_BINARY_WIRED against a scratch buffer, returns produced bytes as std::string). `sm_halt`, `sm_calls`, `sm_pat_anchors`, `sm_pat_nullary` now three-section (md=1 bin=1 txt=1, one return each); TEXT arms wrapped in `if (MEDIUM_TEXT)`. Byte layout proven (HALT = `48 B8 <addr> FF D0`). `rt`-string-address `rdi` loads (sm_calls, anchors) flagged as TSX-WIRE strtab gap. Arms unreached → GATE-PK 442/0/612 unchanged.
- [x] **TSX-SM-2 ✅ `c-commit` — `sm_exec_bb`.** MACRO_DEF stub added; BINARY captures mov edi,bb_idx + call rt_exec_bb; rsi state-ptr + .data reservation flagged TSX-WIRE. TEXT guarded. GATE-PK 442/0/612.
- [x] **TSX-SM-3 ✅ `dedca98f` — two-x86 SM templates.** `sm_jumps` (JUMP*/rel32→flagged-empty binary; sm_label structural no-bytes), `sm_arith` (misc_nullary rt-select + arith mov edi,SM_op; +SM.h), `sm_bb_calls` (once_proc capture mov esi+call rt_pl_once, rdi strtab gap flagged; pump_proc rel32→flagged-empty), `sm_compare` (sm_stno MACRO_DEF stub+capture, sm_compare mov edi,0+call). All four audit OK. GATE-PK 442/0/612.
- [ ] **TSX-SM-4 — three-x86 SM templates.** `sm_defines`, `sm_expr_incr`, `sm_returns`. GATE-PK green.
- [ ] **TSX-SM-5 — `sm_push_pop_lits` (4), `sm_pat_combine` (5).** Largest. GATE-PK green.
- [ ] **TSX-B1 — BB stragglers.** `bb_pl_arith`/`bb_pl_builtin`/`bb_pl_unify` TEXT-guard wrap; `bb_pat_alt`/`bb_pat_cat` verify+add BINARY; rule on `bb_charset_helper` (helper exemption vs full structure). NOTE: the existing BB `MEDIUM_BINARY` arms already call `insn_*` directly (TM rung) — those become INLINE targets too in TSX-INLINE. GATE-PK green.
- [ ] **TSX-X1 — XA per-file rulings.** For each RED XA file, add explicit `MEDIUM_TEXT` guard and a `MEDIUM_BINARY { return std::string(); }` no-op (XA scaffolding emits no per-opcode bytes) OR real bytes where applicable. Document each ruling inline. GATE-PK green.
- [ ] **TSX-AUDIT — green the audit.** `bash scripts/util_three_section_audit.sh` exits GREEN. Manual return-count review: confirm exactly one return per medium section in every touched file. GATE-PK green.
- [ ] **TSX-INLINE — replace every `capture_bytes(insn_*)` and every direct `insn_*` call in a MEDIUM_BINARY arm with the RAW BYTES inline.** This is the heart of the rung's purpose. For each binary arm: read the captured byte sequence, express it as inline `std::string` data — fixed bytes as a byte-string literal, embedded addresses/immediates built with `emit_fmt`/a small `bytes()`/`u64le()` data-builder (NOT a byte-emitting function; pure string construction). After this step NO template arm calls `insn_*`, `capture_bytes`, `emit_seq_port_call*`, `emit_call_sym_plt`, `emit_sym_lea_*`, or the binary arm of `emit_jmp`/`emit_label_define`. Do it in batches mirroring TSX-SM-1..5/B1, gate-green each (still unreached → output unchanged). GATE-PK green.
- [ ] **TSX-DELETE — delete every binary-byte-emitting function.** With zero references remaining: delete the entire `insn_*` family (52 fns, SC-0 inventory), `bb_emit_byte`/`bb_emit_u32`/`bb_emit_u64`/`bb_emit_i32`/`bb_emit_begin`/`bb_emit_end`/the `bb_emit_buf`/`bb_emit_pos`/`bb_emit_size` sink, `emit_seq_port_call*`, `emit_call_sym_plt`, `emit_sym_lea_rcx`/`_r10`, the binary arms of `emit_jmp`/`emit_label_define`/`emit_store_delta`/`emit_add_delta_imm`, and `capture_bytes` itself. Remove `emit_str.cpp`'s `<functional>` include. Build clean with no unused-symbol/link errors. GATE-PK green (arms still unreached). This is the deletion the rung exists for.
- [ ] **TSX-WIRE — open the detour (inline bytes become the output).** In `emit_sm.c`, replace the forced `emit_mode_set(TEXT_MODE())` so that in a binary mode the SM walker dispatches templates in `MEDIUM_BINARY`, and the inline byte data IS the emitted binary. Delete the old `emit_bb.c` binary-driver path. Verify the template-produced bytes are byte-identical to a capture of the pre-TSX-DELETE `insn_*` output (snapshot that byte stream BEFORE TSX-DELETE for the comparison). ⚠ Only step that changes binary origin; gate with the byte-diff harness, after TSX-AUDIT+INLINE+DELETE. Multi-session; strtab-address `rdi` loads (flagged in SM-1) resolved here.

**Out of scope:** ER-8 relocation rethink for layout-dependent displacements; JVM/JS/NET/WASM binary (x86-only directive, rule 14). Note: snapshot the `insn_*` byte output for a mode-4 sample BEFORE TSX-DELETE so TSX-WIRE has a byte-identity oracle.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/one4all/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
[ -d /home/claude/x64 ] || git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=419 FAIL=0 STUB=635
```

## ⚠️ CRITICAL RULE: UTF-8 Greek Letters in CPP String Literals (ER-4+)

**Source files are UTF-8.** When you write actual Greek letters in a UTF-8 C++ source file, the compiler encodes them as UTF-8 bytes in the string literal. This is correct and byte-identical to the baseline.

**DO THIS:** Write actual UTF-8 Greek characters directly in the C++ source:
```cpp
// CORRECT — source is UTF-8, compiler sees actual bytes (0xCE 0xB1 for α):
s_directive(".method public α()Lbb/bb_box$Spec;")
s_1asm(emit_fmt("    if_icmpne %s_ω", tag))
s_directive(".method public β()Lbb/bb_box$Spec;")
```

**DO NOT DO THIS:** Do not attempt octal escapes like `\316\261` (which only work in C with raw byte sequences). In C++, when you write `\\316\\261` in a string literal, you get a literal backslash followed by the digits `316261`, NOT the UTF-8 bytes:
```cpp
// WRONG — outputs literal backslash-digits "\316\261" in the text:
s_directive(".method public \\316\\261()Lbb/bb_box$Spec;")
// This emits: .method public \316\261()... (WRONG)
```

**Why the difference:** 
- In **C string literals** with `const char*`, `\316` is an octal escape that the compiler interprets as a byte value.
- In **C++ string literals** passed to `std::string`, when the source file is UTF-8, the UTF-8 bytes are preserved as-is by the compiler. Writing `\\` in source becomes a single backslash in the output string.

**Test:** After conversion, run `bash scripts/test_per_kind_diff.sh`. If a JVM/NET arm fails with diff showing literal `\316` or `\262` characters in the output, this rule was violated — rewrite using actual UTF-8 characters.

**Affected characters (write these directly in source):**
- `α` (alpha) = U+03B1 = UTF-8 bytes `0xCE 0xB1`
- `β` (beta) = U+03B2 = UTF-8 bytes `0xCE 0xB2`
- `ω` (omega) = U+03C9 = UTF-8 bytes `0xCF 0x89`
- `Δ` (delta) = U+0394 = UTF-8 bytes `0xCE 0x94`
- `Σ` (sigma) = U+03A3 = UTF-8 bytes `0xCE 0xA3`

---

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) = reference. Mode 4 (`--compile`) emits wired x86.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
