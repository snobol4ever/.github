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

## Session State (2026-05-23h)

**one4all HEAD: `1cc7ebea`** — EMIT-RETURNS-STRING infrastructure (ER-0, ER-1) complete. All low-level emit_*() helpers now have string-returning versions (s_comment, s_directive, s_Nasm family, emit_fmt; jvm_*/net_* charset/class/init helpers). All byte-identical to originals. Ready for ER-4/ER-5 template conversion. GATE-PK 419/0/635 ✅.

**Prior (2026-05-23f) one4all HEAD: `8a3b4b39`** — CPP rung opened (return-String emitter conversion, Lon-amended: skip mechanical CPP-0, go straight to return-String). Four BB templates converted to C++ returning std::string: bb_pat_abort (`bc83802c`, + emit_str.{h,cpp} infra + emit_text_n + g++ link + shared-header C++ fixes), bb_pat_fence (`8db542bb`), bb_pat_rem (`90425d4a`), bb_pat_len (`8a3b4b39`, first data-computed, via baseline-shape method). Shape: text arms concatenate (`s_comment(...) + s_2asm(...) + ...`); IS_BIN/relocation/jvm_*/net_* arms stay imperative. Loop-fold shape proven in isolation. Terrain mapped (INLINE-TEXT vs DELEGATING x86 arms — see CPP-2). GATE-PK 419/0/635 NEW=0 GONE=0. GATE-M 11 / GATE-E gate1_beauty+gate4_icon — pre-existing, no new regressions. ⚠ MERGE-GATED shared headers touched (byte-neutral): BB.h, emit_core.h, snobol4.h — self-tag typedefs + rename typename param for C++ compat. ⛔ Beauty gate remains SUSPENDED.

**Prior (2026-05-23e) one4all HEAD: `88cb6fe2`** — SJ-1c: reverted SJ-1b-sweep's wrongful funnel conversion of IS_JS/IS_WASM arms (it had violated the x86-only directive — routed JS/WASM through asm funnels + sm_returns.c WASM_FNRET* macros, added spurious leading space, destroyed WASM 10-space indent, and changed sm_returns WASM bytes). Restored all JS/WASM arms to pre-sweep (336cb7e1) one-emit_textf-per-line form; restored js/wasm per-kind baselines from 336cb7e1; removed orphaned WASM_FNRET* macros. x86/JVM/NET funnel work preserved. 26 source files + 142 baseline cells. GATE-PK 419/0/635 NEW=0 GONE=0.

**Prior (2026-05-23d) one4all HEAD: `f6b0be23`** — SJ-1b-reindent: restored C source indentation in the 18 SM/BB/XA template files where SJ-1b-sweep split multi-line `emit_textf` blobs into per-line funnel calls but dropped leading whitespace. Brace-depth 4-space re-indent, whitespace-only. 18 files, 1448/1448. GATE-PK 419/0/635.

**Prior (2026-05-23c) one4all HEAD: `326a4fac`** — SJ-1b-sweep COMPLETE. All emit_textf in SM_templates (14 files), BB_templates (22 files), XA_templates (4 files) converted to emit_io funnels (x86/JVM/NET; JS and WASM untouched per Lon directive — ⚠ but in fact JS/WASM WERE wrongly touched; fixed in SJ-1c). Baselines refrozen. 593 files changed, 7679 ins / 6329 del.

**Gate: GATE-PK PASS=419 FAIL=0 STUB=635 ✅**

**STYLE-FUNNEL-ALL-ASM (SJ-1) STATUS:**
- ✅ SJ-1a funnels landed (`2ef4847f`)
- ✅ SJ-1b funnel rework + six-function API
- ✅ SJ-1b-sweep: ALL backends (x86/JVM/NET) routed through funnels; baselines refrozen

**NEXT:** ⚡ CPP-2 continue — remaining DELEGATING files (mechanical .c→.cpp, all arms imperative, use the recipe + two hazards + charset quirk recorded below): `bb_pat_notany`, `bb_pat_break`, `bb_pat_span`, `bb_lit`, `bb_pat_alt`, `bb_pat_cat`, `bb_arbno`. All INLINE-TEXT leaves are done. Then CPP-1 (extern "C" surface) / CPP-3 (core+glue) per the sub-step list, or STYLE-NO-SHADOW-LOCALS per Lon.


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
- [x] **ER-0 — build spike. ✅ COMPLETE 2026-05-23 (Sonnet).** Infrastructure: `emit_str.{h,cpp}` with `s_comment`, `s_directive`, `s_Nasm` family (N=1..3, L=label prefix), `emit_fmt` wrapper. Added `CXX`, `CXXRT`. Converted `bb_pat_abort.cpp` as proof-of-concept (abort has no data — pure literal concat).
- [x] **ER-1 — emit_str.h API complete. ✅ COMPLETE 2026-05-23 (Sonnet).** All JVM/NET/charset helpers have string-returning versions: jvm_class_hdr_str, jvm_init_ms_str_str, jvm_init_ms_only_str, jvm_init_ms_int_str, jvm_val_helper_str, net_escape_ldstr_str, net_class_hdr_str, net_α/β_hdr_str, net_fail_ret_str, net_cursor_load_str, net_ms_length_str, net_spec_of_str, net_charset_class_str, net_push_i4_str, net_ctor_none_str, net_spec_zw_str. Byte-identical to emit_core.c originals. GATE-PK 419/0/635 ✅.
- [ ] **ER-2 — helpers to string.** Convert `jvm_push_int2`, `jvm_class_hdr`, `jvm_init_ms_only`, `jvm_init_ms_str`, `jvm_init_ms_int`, `jvm_val_helper`, `jvm_emit_ldc_string` in `emit_core.cpp` to return `std::string`. Also `net_*` layer-2 helpers. Also `bb_charset_emit` in `bb_templates.cpp`. Callers concatenate the result. GATE-PK green.
- [x] **ER-3 — INLINE-TEXT templates to string. ✅ COMPLETE (prior rungs CPP-2a through CPP-2).** bb_pat_abort, bb_pat_fence, bb_pat_rem, bb_pat_len, bb_pat_arb, bb_pat_tab, bb_pat_rtab. All x86 arms return pure concat of s_*() calls + data-injected variables (labels, node-ids, arity). JS arms also return concat. JVM/NET arms stay imperative (return std::string()). Baseline-shape method verified byte-identical. GATE-PK 419/0/635 ✅.
- [ ] **ER-4 — DELEGATING templates to string.** `bb_pat_pos`, `bb_pat_rpos`, `bb_pat_any`, `bb_pat_notany`, `bb_pat_break`, `bb_pat_span`, `bb_pat_lit`, `bb_pat_alt`, `bb_pat_cat`, `bb_arbno`. These call relocation-aware helpers (emit_label_define, emit_jmp_label, insn_*) or bb_charset_emit. Convert callsites to concatenate: `return ... + bb_charset_emit(...) + emit_label_define(...) + ...;`. The helpers are STILL imperative internally (they patch relocation lists), but their outputs are strings. Each template arm returns ONE concat, or `std::string()` if it's pure-imperative (e.g., IS_BIN mode). **Approach:** For each DELEGATING file, convert JVM/NET arms to use the new `jvm_*_str()` and `net_*_str()` helpers instead of FILE*-based calls. x86 arm stays imperative (IS_BIN and relocation-patching). GATE-PK green per file. Start with bb_pat_any (simplest), then spread to the 9 others.
- [ ] **ER-5 — SM templates to string.** All SM_templates/*.cpp files. Same pattern: convert each template arm to return a single concat. Loops that emit multiple lines: `for(...) r += emit_fmt(...);` already works (proven in SJ-1b-sweep). Result: `return r;` (or `return concat(pieces...);`). GATE-PK green per file.
- [ ] **ER-6 — XA templates to string.** All XA_templates/*.cpp files. Same pattern.
- [ ] **ER-7 — delete FILE* / buffer.** Once every template returns string, audit all TUs: remove `FILE *out` parameters, remove `char buf[...]` locals, remove dead `fprintf`/`snprintf`. Helpers that are STILL imperative (relocation patch) keep their FILE* for now. GATE-PK green at session-end. Commit.
- [ ] **ER-8 — relocation rethink (future session).** Currently relocation is patched in-place via FILE* seek. Future: collect relocation records *alongside* the string output, apply patches in a second pass over the string. This unblocks pure-functional emitters.

```
**⛔ BEAUTY GATE SUSPENDED** during BB template consolidation.

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

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op, via SM_sequence_t.bb_table]
```

Mode 2 (`--interp`) = reference. Mode 4 (`--compile`) emits wired x86.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
