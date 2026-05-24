# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Repo:** one4all + corpus + .github

## Invariants

1. **No AST walking in modes 2/3/4.**
2. **Zero C Byrd-box functions.** Only permitted: `icn_bb_dcg`.
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL.
5. **Single gate run at end of session.**
6. **Builder/consumer case rule.** UPPERCASE builds IR. lowercase consumes.
7. **EC-UNI matrix.** Backends are columns. Text-vs-binary inside each `IS_<BE>` arm.
8. **Unified dispatch owns mode-setting.**
9. **One file per Byrd Box in `BB_templates/`.**
10. **Grouped templates allowed.**
11. **INLINE-ALL complete.** Every SM/BB code-gen path lives in `SM_templates/*.c` and `BB_templates/*.c`.
12. **No shadow locals in templates.**
13. **Entry labels belong to their template.**
14. **x86 only for BB template ladder.** IS_JVM/JS/NET/WASM arms are stubs.
15. **All code emission goes through the template system via an XA_* opcode.**
16. **THE RULE (2026-05-24q) — NO code is emitted unless it carries a BB, SM, or XA opcode.** Every emitting function outside a template body MUST be deleted and its body inlined at every call site. Where the call site is a driver/walker, mint a new composable XA building-block. End state: 100% of code emission lives inside SM/BB/XA template bodies; the only non-template functions left are orchestrators, relocation/patch infra, byte/text sinks, and atomic string builders.

---

## Session State (2026-05-25 — NO-SNPRINTF COMPLETE)

**one4all HEAD: `3785ffd1`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN.

**THE RULE holds. OOD ladder + OOD-PHASE-2 + NO-SNPRINTF all complete.**

### OOD ladder (all rungs ✅)
OOD-1…14 complete — all bare emission helpers deleted/inlined into SM/BB/XA template bodies. See prior session watermarks in git log for detail.

### OOD-PHASE-2 (all steps ✅)
Goal: move emitting function *bodies* from `emit_bb.c`/`emit_sm.c` into their template source files.

- **P2-A ✅ `025ca819`** — `emit_flat_entry_dispatch`, `emit_entry_dispatch_xa`, `emit_flat_prologue_xa`, `emit_flat_epilogue_xa` inlined into `xa_flat.cpp`; deleted from `emit_bb.c`/`emit_bb.h`.
- **P2-B ✅ `6fdd8a39`** — `strtab_emit_rodata`, `emit_expression_registry`, `pl_pre_intern_pred_names`, `emit_pl_predicate_registry` promoted from static in `emit_sm.c`; `_xa` shims deleted; `xa_rodata.cpp` calls promoted fns directly.
- **P2-C+D ✅ `3edd387e`** — `emit_pattern_blobs` promoted + new `XA_PATTERN_BLOBS` opcode; `xa_pattern_blobs.cpp` owns the body; driver calls `xa_dispatch(XA_PATTERN_BLOBS)`. P2-D grep: `emit_bb.c` has only the pre-existing 4-byte brokered prologue inline (`bb_build_brokered` infra, KEEP-list). THE RULE verified.

**NEXT: Lon directs.** ⛔ Beauty gate SUSPENDED. ⛔ PENDING Lon: TEMPLATE PURE-PROJECTION.

Every template fn must drive ONLY from `g_emit` global struct. No complicated traversals, no recursion, no pointer-chasing into AST/BB node graph inside a template. Known violators when this opens:
1. `sm_nreturn` walks `prog->instrs[j]` backward for enclosing SM_LABEL.
2. `bb_pat_alt`/`bb_pat_cat`/`bb_pat_fence` RECURSE via `emit_flat_ir(pBB->c[i],…)` + allocate labels + patch jumps.
3. Most templates still take `const SM_t*`/`BB_t*` param + deref instead of reading `g_emit.instr`/`g_emit.node`.

Open question for Lon: is "template may iterate a g_emit collection with a simple for (no node-graph deref, no recursion)" the allowed end-state, or stricter?

---

## Active Rungs

### ⚡ OPCODE-OR-DELETE (OOD) — COMPLETE ✅
All rungs OOD-1…14 gate-green. THE RULE holds.

### ⚡ THREE-MEDIUM — COMPLETE ✅
Every PLATFORM_X86 block has MEDIUM_MACRO_DEF + MEDIUM_BINARY + MEDIUM_TEXT sections.

### ⚡ NO-SNPRINTF — COMPLETE ✅ `01123236`
Remove all `snprintf` from BB/SM/XA templates; replace with `emit_fmt`/string concat.
71 snprintf across 19 template files → 0. GATE-PK 442/0/612 NEW=0 GONE=0.
Steps:
- [x] **NS-0** — inventory + helper check.
- [x] **NS-1** — `bb_capture.cpp` (19).
- [x] **NS-2** — charset family: any/span/break/notany (9+4+4+4). Also: esc[] char buffer → std::string.
- [x] **NS-3** — `sm_returns.cpp` (7), `sm_calls.cpp` (4), `sm_jumps.cpp` (2), `sm_defines.cpp` (2).
- [x] **NS-4** — XA: `xa_bb_macro_library.cpp` (4), `xa_bb_ptr_slot.cpp` (2 via emit_fmt+strncpy).
- [x] **NS-5** — remaining BB singletons: bb_pat_pos/alt/len/cat/arb/tab/arbno/lit.
- [x] **NS-6** — audit: grep snprintf in templates returns zero (comment only in xa_bb_ptr_slot).
### ⚡ S200-EMITTER — COMPLETE ✅ `7857f6fc`
200-col style pass: zero blank lines, zero trailing inline comments across all emitter and template files.
Scope: `src/emitter/*.c`, `src/emitter/*.h`, `src/emitter/*.cpp`, all `BB_templates/`, `SM_templates/`, `XA_templates/`. Long JS/WASM string literals accepted as-is (semantically indivisible). GATE-PK 442/0/612 NEW=0 GONE=0.
Steps:
- [x] **S200-E1** — strip blank lines: 12 template files + emit_core.c, emit_str.cpp, emit_str_builders.h, sil_macros.h.
- [x] **S200-E2** — strip trailing inline `/* */` comments: 30 files.
- [x] **S200-E3** — replace UTF-8 box-drawing chars with ASCII in sil_macros.h.
- [x] **S200-E4** — wrap >200-col WASM/JS string literals at `\n` boundaries where possible.
- [x] **S200-E5** — audit: zero blank lines, zero trailing comments, zero fixable >200-col lines.

### ⚡ STRIP-INTERIOR-COMMENTS — COMPLETE ✅ `3785ffd1`
Remove all `/* ... */` block comments that appear inside function bodies in emitter and template files.
Scope: `src/emitter/*.c`, `src/emitter/*.h`, `src/emitter/*.cpp`, all `BB_templates/`, `SM_templates/`, `XA_templates/`.
Keep: separator lines (`/*---*/`, `/*===*/`), file-header one-liners (line 1 of each file).
Strip: TSX-*, OOD-*, P2-*, PIVOT, PST-*, FLAGGED notes, and all other interior block comments.
Survey: ~472 interior comment lines across ~40 files.
Steps:
- [x] **SIC-0** — inventory: count interior `/* */` lines per file, confirm separators excluded.
- [x] **SIC-1** — BB_templates/ (all .cpp).
- [x] **SIC-2** — SM_templates/ (all .cpp).
- [x] **SIC-3** — XA_templates/ (all .cpp).
- [x] **SIC-4** — emitter root: emit_bb.c, emit_sm.c, emit_core.c, emit_str.cpp, emit_io.c.
- [x] **SIC-5** — emitter headers: emit_*.h, x86_opcodes.h, sil_macros.h.
- [x] **SIC-6** — audit: grep for interior `/* */` returns zero (separators only remain).
ER-8: relocation rethink (abs-addr PLT fallback vs rel32 — future session).

### ⚡ DECOMPOSE-MODE (DM) — DM-1…7 COMPLETE ✅
DM-8 (emit_text_and_binary_in_one) deferred.

### ⚡ TSX (THREE-SECTION-X86) — COMPLETE ✅
TSX-INLINE, TSX-DELETE, TSX-WIRE, TSX-CHARSET all done. insn_* family eliminated.

---

## Oracle (every gate)
`bash scripts/test_per_kind_diff.sh` → PASS=442 FAIL=0 STUB=612 NEW=0 GONE=0
`bash scripts/util_three_section_audit.sh` → AUDIT GREEN
`bash scripts/test_prolog_bb_honest.sh` → 124/0/0
Smoke (`test_smoke_snobol4_jit.sh`) only when binary paths touched: parity 184 / `--run` 186/75.

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
```

## ⚠️ CRITICAL RULE: UTF-8 Greek Letters in CPP String Literals

Write actual UTF-8 Greek characters directly in C++ source — **not** octal escapes. Affected: `α β ω Δ Σ`. In C++ string literals, `\\316\\261` emits literal backslash-digits, not bytes.

---

## Architecture

```
AST --(lower)--> SM_sequence_t  [SM_BB_XXX bridge opcodes]
                 BB_graph_t*    [pre-built per bridge op]
```

Mode 2 (`--interp`) = reference. Mode 4 (`--compile`) emits wired x86 via SM/BB/XA templates.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
