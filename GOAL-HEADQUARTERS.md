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

## Session State (2026-05-25 — PP-A1..A5 COMPLETE)

**one4all HEAD: `ae7e7abd`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, prolog 124/0/0.

**XA driver/template split complete.** Six XA templates corrected: traversal→drivers, emission→templates. xa_rodata + xa_pattern_blobs deleted; xa_macro_library/xa_wasm_main split to open/close pairs; xa_flat emit_label_define_bb moved to driver; xa_js_label_register iterates g_emit collection. PP complete (PP-C Σ ruling pending).

**CORRAL-EMIT COMPLETE ✅ `b27c5f66`.** All `emit_*` in driver files are sanctioned primitives. **one4all HEAD: `111422a3`** ✅ GATE-PK 442/0/612. RP-1..12 ✅. RP-14 ✅ (audit GREEN — walk-internal JVM/NET/JS/WASM deferred to RP-13). **NEXT: RP-13 or PP-B (Lon directs).** ⛔ Beauty gate SUSPENDED.

---

## Session State (2026-05-25 — NO-SNPRINTF COMPLETE)

**one4all HEAD: `3785ffd1`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN.

**THE RULE holds. OOD ladder + OOD-PHASE-2 + NO-SNPRINTF all complete.**

## Session State (2026-05-24 — RP-2..9+RP-14 COMPLETE)

**one4all HEAD: `111422a3`** ✅ GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, prolog 124/0/0.

**THE-RULE-ALL (RP) complete through RP-14.** All G1 (Prolog registry), G2 (strtab rodata), G4 (cap fixup) fprintf eliminated. Nine new XA templates: xa_pl_kids_rodata, xa_pl_sub_builder, xa_pl_builder, xa_pl_registry_table, xa_strtab_rodata, xa_cap_fixup (plus RP-1 xa_expression_registry from prior session). RP-13 (walk-internal JVM/NET/JS/WASM per-instruction) deferred — Lon direction needed. PP-B/C/D open.

**NEXT: PP-B (R4 conversion-locals) or RP-13 (Lon directs).**

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

### ⚡ PURE-PROJECTION (PP) — templates are pure CONCAT/IF/FOR — OPEN
Tracker: `.github/TRACK-PURE-PROJECTION.md`.

**Principle (Lon, 2026-05-25).** A template is a pure function `state → one string`, no side
effects. Its body is ONE expression built from three constructs only:
- **CONCAT** — `X_literal + Global + Y_literal + …`
- **IF(cond, code1, code2)** — conditional emission inline in the concat; `cond` is a global SCALAR.
- **FOR(i, lo, hi, … code … )** — iterate a global COLLECTION, concatenating per element.

A template switches off global scalars and iterates global collections. It has NO knowledge of
anything but "what switches my output" and "what lists of work I iterate." Templates are CALLED by
drivers; they never drive. Forbidden in a template body: recursion, child-graph deref
(`emit_flat_ir`, `pBB->c[i]` into sub-templates), label allocation, jump patching, backward/forward
scans of `prog->instrs[]`, any `emit_*` call with a side effect, returning `std::string()` after
doing work as side-effects.

**Order: traversals/side-effects FIRST, then locals, then globals shape.**

#### PP-A — DE-DRIVE the self-driving templates (the severe violators)
The driver (`emit_flat_ir` / the BB-graph walker) must do the child-recursion + label minting +
jump patching, land the resulting child-strings into a `g_emit` COLLECTION and the port/label names
into `g_emit` SCALARS, THEN call the template. The template's x86 arm becomes CONCAT/IF/FOR over
those — emitting label definitions and jumps as TEXT, not via `emit_label_define_bb`/`emit_jmp_label`.

- [x] **PP-A0 — driver contract.** ✅ Carrier approach chosen: lift driving INTO the driver (`emit_bb.c` flat_drive_* fns) + shared predicate `bb_kind_is_driver_owned()`; scalar fields `enclosing_fname`/`prev_instr_name` added to `sm_emit_t` for SM neighbor reads.
- [x] **PP-A1 — `bb_pat_cat`.** ✅ x86 driving → `flat_drive_cat`; template x86 arm deleted; audit routes driver-owned x86 kinds through `emit_flat_ir`. GATE-PK 442/0/612.
- [x] **PP-A2 — `bb_pat_alt`.** ✅ → `flat_drive_alt`; shared predicate added. GATE.
- [x] **PP-A3 — `bb_pat_fence`.** ✅ with-children traversal → `flat_drive_fence`; pure macro/zero-child emission stays in template. GATE.
- [x] **PP-A4 — `sm_nreturn` backward scan.** ✅ scan lifted to SM driver loop → `g_emit.enclosing_fname`; dropped side-effecting `emit_mode_set` in template. smoke parity 184 / run 186/75.
- [x] **PP-A5 — `sm_define` neighbor + `sm_exec_bb` self-pc.** ✅ `g_emit.prev_instr_name` scalar + `_.i`; SM audit primes new scalars (contamination-proof). GATE-PK 442/0/612, audit GREEN, prolog 124/0/0.
- [x] **PP-A6 — Prolog operand derefs (bb_pl_arith/unify/builtin `pBB->c[0]/c[1]`).** RULING: pBB->c[0]/c[1] are sub-records of the DATA struct passed in — direct field reads are legal template body operations (Snocone DATA() model). No driver flattening needed. Ruling-resolved no-op. GATE-PK 442/0/612.
- [x] **PP-A7 — audit.** grep templates for `emit_flat_ir`, `emit_label_define_bb`, `emit_jmp_label`, `emit_label_initf`, `alloca`, `prog->instrs`, `pBB->c[` → all hits ruling-resolved or comment-only. No template returns `std::string()` after side-effects (BINARY medium imperative idiom is correct by design). GATE-PK 442/0/612, AUDIT GREEN, PROLOG 124/0/0.

#### PP-B — R4 conversion-locals (after de-drive)
Inline every `const char *x = x_s.c_str();` (33: 26 BB active x86, 7 SM stub arms). GATE.

#### PP-C — R3 string-globals shape
`Σ` (`const char *` + `Σlen`) → `std::string` for direct concat; preserve emitted-asm ABI for
`&Σ`/`Σlen` (`TEMPLATE_ADDR_SIGMA`). Per Lon ruling. GATE.

#### PP-D — R1/R2 scope tighten + final audit
Each SM template reads only SM_t-fields + sanctioned globals; each BB template only BB_t-fields +
sanctioned globals. Confirm CONCAT/IF/FOR-only across all active arms. GATE-PK 442/0/612 NEW=0 GONE=0.

### ⚡ THE-RULE-ALL (RP) — ALL emission into BB/SM/XA templates — OPEN

**Principle.** THE RULE: no code is emitted unless it carries a BB, SM, or XA opcode. Complete scan (one4all `b27c5f66`) found the following `fprintf`/`fputs`/`fputc`/`fwrite` offenders in non-template driver files. Every one must move into a template body.

**Offender groups:**

| Group | Functions | Location | Fix |
|---|---|---|---|
| **G1 — Prolog predicate registry** | `codegen_expression_registry`, `codegen_pl_predicate_registry`, `codegen_pl_builder_fn`, `codegen_pl_sub_builder_fn`, `codegen_pl_b_node_call`, `codegen_pl_b_kids_call`, `codegen_pl_kids_rodata_for_pred` | `emit_sm.c` | New XA templates (RP-1..5) |
| **G2 — String table rodata** | `walk_strtab_rodata` | `emit_sm.c` | New `XA_STRTAB_RODATA` template (RP-7) |
| **G3 — Pattern blobs** | `walk_bb_pattern_blobs` | `emit_sm.c` | New `XA_PATTERN_BLOBS` template (RP-8) |
| **G4 — Cap fixup** | `codegen_cap_fixup_init_calls` | `emit_sm.c` | New `XA_CAP_FIXUP` template (RP-9) |
| **G5 — SM x86 walker inline labels** | `codegen_sm_x86` (2 stray fprintf for `.L%d:` labels + UNHANDLED) | `emit_sm.c` | Route through `emit_textf` / SM template (RP-10) |
| **G6 — JVM/NET/JS helpers called from templates** | `jvm_class_hdr`, `jvm_push_int2`, `jvm_emit_ldc_string`, `net_class_hdr`, `net_escape_ldstr`, `net_α_hdr`, `net_β_hdr`, `net_fail_ret`, `net_cursor_load`, `net_spec_of`, `net_charset_class`, `net_push_i4`, `js_escape`, `js_escape_string` | `emit_core.c` | `_str` twins already exist in `emit_str.cpp`; delete fprintf variants, replace call sites with `_str` calls + `emit_text_n` (RP-11) |
| **G7 — WASM data segments** | `wasm_emit_data_segments` | `emit_core.c` | Convert to `std::string` return or route through `emit_textf`; called from `xa_epilogue` template (RP-12) |
| **G8 — Walk-internal fprintf** | `walk_sm_jvm`, `walk_sm_jvm_instr`, `walk_sm_jvm_range`, `walk_sm_net`, `walk_sm_js`, `walk_sm_wasm`, `walk_bb_node` | `emit_core.c` | These walkers call codegen_sm_dispatch per node which goes through SM templates; their own `fprintf` are JVM/NET/JS/WASM per-instruction emission that needs XA or SM template wrappers (RP-13, future) |

#### RP-1 — XA_EXPRESSION_REGISTRY (new opcode + template)

Driver (`codegen_sm_x86`) walks `prog->instrs[]` collecting expression-label names + entry PCs into `g_emit` collection (`xa_expr_names`, `xa_expr_pcs`, `xa_expr_count`), then calls `xa_dispatch(XA_EXPRESSION_REGISTRY)`. Template `xa_expression_registry.cpp` emits the `.section .data` + `.Lexpression_registry:` + `.quad` pairs + sentinel. Delete `codegen_expression_registry`.

- [x] **RP-1** — implement; wire opcode; driver fills collection + `xa_dispatch`; delete `codegen_expression_registry`. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RP-2 — XA_PL_KIDS_RODATA (new opcode + template)

Driver fills `xa_pl_pred_idx`, per-node kids arrays into `g_emit` collection. Template emits `.section .rodata` + `.align 4` + `.Lpl_kids_P_N:` labels + `.int` arrays + `.text`. Delete `codegen_pl_kids_rodata_for_pred`.

- [x] **RP-2** — implement; wire opcode; driver fills + `xa_dispatch`; delete. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RP-3 — XA_PL_SUB_BUILDER (new opcode + template)

Driver fills scalars: pred_idx, node_idx, sub-graph node list into `g_emit` collection. Template emits optional rodata kids block + function label + prologue + `rt_pl_b_sub_*@PLT` call sequence + `ret`. Delete `codegen_pl_sub_builder_fn`.

- [x] **RP-3** — implement; wire opcode; driver fills + `xa_dispatch`; delete. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RP-4 — XA_PL_BUILDER (new opcode + template)

Driver fills: pred_idx, cfg node list, entry_idx, predicate name label, arity. Template emits builder function body. Delete `codegen_pl_builder_fn`, `codegen_pl_b_node_call`, `codegen_pl_b_kids_call`.

- [x] **RP-4** — implement; wire opcode; driver fills + `xa_dispatch`; delete. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RP-5 — XA_PL_REGISTRY_TABLE (new opcode + template)

Driver fills: `xa_pl_reg_names`, `xa_pl_reg_arities`, `xa_pl_reg_fn_labels`, `xa_pl_reg_count`. Template emits `.section .data` + `.Lpl_registry:` + quad table. Delete `codegen_pl_predicate_registry` body emission; loop becomes pure walker.

- [x] **RP-5** — implement; wire opcode; driver fills + `xa_dispatch`; delete. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RP-6 — final audit (Prolog + expression registry)

`grep -n "fprintf" src/emitter/emit_sm.c` returns zero emission fprintf calls in G1 functions. GATE.

- [x] **RP-6** — audit G1 clean. GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, prolog 124/0/0.

#### RP-7 — XA_STRTAB_RODATA (walk_strtab_rodata → template)

`walk_strtab_rodata` emits `.section .rodata` + `.S%d: .string %s` entries + `.text`. Driver calls `xa_dispatch(XA_STRTAB_RODATA)`; template iterates `g_emit.xa_strtab` collection. `XA_STRTAB_RODATA` opcode replaces direct call in `codegen_sm_x86`.

- [x] **RP-7** — implement `xa_strtab_rodata.cpp`; wire opcode; driver fills strtab collection into `g_emit`; delete fprintf from `walk_strtab_rodata`. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RP-8 — XA_PATTERN_BLOBS (walk_bb_pattern_blobs → template)

`walk_bb_pattern_blobs` emits pattern BB blobs. Driver calls `xa_dispatch(XA_PATTERN_BLOBS)`; template emits. Already has an opcode slot from prior work — resurrect it properly.

- [ ] **RP-8** — implement `xa_pattern_blobs.cpp`; wire opcode; delete fprintf from `walk_bb_pattern_blobs`. GATE.

#### RP-9 — XA_CAP_FIXUP (codegen_cap_fixup_init_calls → template)

`codegen_cap_fixup_init_calls` emits `lea`/`call rt_init_arbno@PLT` etc. New `xa_cap_fixup.cpp` template. Driver fills per-cap-fixup scalars into `g_emit` collection, calls `xa_dispatch(XA_CAP_FIXUP)` per entry.

- [x] **RP-9** — implement; wire opcode; driver fills + `xa_dispatch`; delete fprintf. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RP-10 — SM x86 walker stray fprintf (codegen_sm_x86 inline labels)

Two stray `fprintf(out, ".L%d:\n", pc)` and `fprintf(out, "UNHANDLED %s\n", ...)` in `codegen_sm_x86`. Replace with `emit_textf(".L%d:\n", pc)` and `emit_textf("UNHANDLED %s\n", ...)` — already inside the SM dispatch loop, so using `emit_textf` routes through the sanctioned primitive.

- [x] **RP-10** — replace 3 stray fprintf in `codegen_sm_x86` with `emit_textf`. GATE.

#### RP-11 — Delete fprintf variants of JVM/NET/JS helpers; use _str twins (G6)

`jvm_class_hdr`, `jvm_push_int2`, `jvm_emit_ldc_string`, `net_class_hdr`, `net_escape_ldstr`, `net_α_hdr`, `net_β_hdr`, `net_fail_ret`, `net_cursor_load`, `net_spec_of`, `net_charset_class`, `net_push_i4`, `js_escape`, `js_escape_string` — all have `_str` twins in `emit_str.cpp`. Three are called from BB templates (`jvm_class_hdr` from `bb_capture.cpp`, `js_escape` from `bb_capture.cpp`, `wasm_emit_data_segments` from `xa_epilogue.cpp`).

Fix: replace the template call sites with their `_str` twins + `emit_text_n`. Delete the fprintf variants from `emit_core.c`. Walk-internal uses (`walk_sm_jvm` etc.) are handled in RP-13.

- [x] **RP-11** — replace 3 template call sites with `_str` + `emit_text_n`; delete fprintf variants that are only called from walk_* functions (defer walk-internal calls to RP-13). GATE.

#### RP-12 — wasm_emit_data_segments → emit_textf (G7)

Called from `xa_epilogue` template. Convert `fprintf` calls to `emit_textf` so output routes through the sanctioned primitive. Or extract into a `std::string`-returning function called from the template body.

- [x] **RP-12** — convert `wasm_emit_data_segments` fprintf → `emit_textf`; it is called from a template so this completes the chain. GATE.

#### RP-13 — Walk-internal fprintf (G8, future)

`walk_sm_jvm`, `walk_sm_jvm_instr`, `walk_sm_jvm_range`, `walk_sm_net`, `walk_sm_js`, `walk_sm_wasm`, `walk_bb_node` emit per-instruction JVM/NET/JS/WASM assembly via fprintf inside their traversal loops. This is the deepest layer — each instruction emission needs its own SM or XA template. Large scope; tracked here for later session.

- [ ] **RP-13** — design per-instruction JVM/NET/JS/WASM SM template dispatch (mirrors x86 `codegen_sm_dispatch`). Awaiting Lon direction on scope/priority.

#### RP-14 — final audit (all groups)

`grep -rn "fprintf\|fputs\|fputc\|fwrite" src/emitter/emit_sm.c src/emitter/emit_bb.c src/emitter/emit_core.c` returns only: sanctioned primitives (`emit_label_define_bb`, `ef_t3c`, `emit_text_stno_banner`, `emit_text_rawf`, `bb_label_define` stderr path), infrastructure (error paths to stderr), and walk-internal per-instruction emission deferred to RP-13.

- [x] **RP-14** — final audit. GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, prolog 124/0/0. Remaining fprintf in drivers: sanctioned primitives (emit_core.c) + walk-internal JVM/NET/JS/WASM per-instruction emission (deferred to RP-13).

### ⚡ CORRAL-EMIT (CE) — corral all emission into BB/SM/XA templates — OPEN

**Principle.** Every `emit_*()` call that produces output must be reachable from the root of a BB, SM, or XA template. Driver/walker files (`emit_bb.c`, `emit_sm.c`, `emit_core.c`, `emit_io.c`) may contain orchestration, traversal, and infrastructure — but zero direct emission.

**Scan baseline (one4all `ae7e7abd`).** The following `emit_*` functions are defined in driver files and are NOT reachable from any template root. Each must either be wrapped in a new XA template (if it generates code that belongs to a named emission unit) or deleted (if it is dead or subsumed):

| Function | File | Disposition |
|---|---|---|
| `emit_prologue()` | `emit_core.c` | New `XA_PROLOGUE_BROKERED` or fold into `xa_prologue` |
| `emit_epilogue()` | `emit_core.c` | New `XA_EPILOGUE_BROKERED` or fold into `xa_epilogue` |
| `emit_banner_stno()` | `emit_core.c` | New `XA_BANNER_STNO` (called per-statement in SM walker) |
| `emit_byte()` | `emit_io.c` | Alias of `bb_emit_byte` — delete, use `bb_emit_byte` in templates |
| `emit_bytes()` | `emit_io.c` | Low-level sink — fold into `bb_sink_str` or new XA |
| `emit_text()` | `emit_io.c` | Alias of `emit_text_n` — delete, use `emit_text_n` in templates |
| `emit_3asm()` | `emit_io.c` | Emission helper — move into template common or delete if unused |
| `emit_L1asm()` | `emit_io.c` | Emission helper — same |
| `emit_L2asm()` | `emit_io.c` | Emission helper — same |
| `emit_L3asm()` | `emit_io.c` | Emission helper — same |

**Steps:**
- [ ] **CE-1 — verify dead/alias:** Confirm `emit_byte`, `emit_text`, `emit_3asm`, `emit_L1asm`, `emit_L2asm`, `emit_L3asm` have zero callers outside test files. Delete or alias-eliminate.
- [ ] **CE-2 — `emit_prologue` / `emit_epilogue`:** Audit callers. If only called from non-template brokered path, wrap in XA opcodes; driver calls `xa_dispatch(XA_PROLOGUE_BROKERED)` etc. Templates emit the `fprintf` bodies.
- [ ] **CE-3 — `emit_banner_stno`:** Called per-statement from SM walker. Wrap as `XA_BANNER_STNO`; driver primes `g_emit` scalars (stno, lineno, src_text), template emits the banner.
- [ ] **CE-4 — `emit_bytes`:** Audit callers. If reachable only from test files, leave. If in driver emission paths, wrap or inline into template via `bb_sink_str`.
- [ ] **CE-5 — gate.** GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, prolog 124/0/0. All `emit_*` in driver files are infrastructure/orchestration only.

### ⚡ RENAME-EMIT (RE) — reserve emit_* for template emission only — OPEN

**Principle.** The `emit_*` prefix is reserved exclusively for functions reachable from a BB, SM, or XA template root (i.e., template entry points and the primitives they call). All other `emit_*` functions are renamed to one of three new prefixes:

- **`codegen_*`** — top-level orchestrators and pass drivers (call walkers, dispatch templates, own a named code-generation unit)
- **`walk_*`** — pure SM/BB/AST traversals (iterate structures, call codegen/templates per node)
- **`lower_flat_*`** — flat-lowering helpers (eligibility, intern, reset — IR preparation, not emission)

`emit_flat_intern_str` is called from BB templates — it stays `emit_*` but is renamed `emit_intern_str` (removes the misleading `flat_` coupling).

#### RE-1 — `codegen_*` renames (orchestrators/drivers)

| Old name | New name | File |
|---|---|---|
| `emit_walk_codegen` | `codegen_sm_x86` | `emit_sm.c` |
| `emit_program` | `codegen_program` | `emit_core.c` |
| `emit_prologue` | `codegen_prologue` | `emit_core.c` |
| `emit_epilogue` | `codegen_epilogue` | `emit_core.c` |
| `emit_flat_body` | `codegen_flat_body` | `emit_bb.c` |
| `emit_flat_build` | `codegen_flat_build` | `emit_bb.c` |
| `emit_sm_dispatch` | `codegen_sm_dispatch` | `emit_core.c` |
| `emit_expression_registry` | `codegen_expression_registry` | `emit_sm.c` |
| `emit_pl_predicate_registry` | `codegen_pl_predicate_registry` | `emit_sm.c` |
| `emit_pl_builder_fn` | `codegen_pl_builder_fn` | `emit_sm.c` |
| `emit_pl_sub_builder_fn` | `codegen_pl_sub_builder_fn` | `emit_sm.c` |
| `emit_pl_b_node_call` | `codegen_pl_b_node_call` | `emit_sm.c` |
| `emit_pl_b_kids_call` | `codegen_pl_b_kids_call` | `emit_sm.c` |
| `emit_pl_kids_rodata_for_pred` | `codegen_pl_kids_rodata_for_pred` | `emit_sm.c` |
| `emit_banner_stno` | `codegen_banner_stno` | `emit_core.c` |
| `emit_cap_fixup_init_calls` | `codegen_cap_fixup_init_calls` | `emit_bb.c` |

- [x] **RE-1** — apply all `codegen_*` renames; update all call sites and headers. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RE-2 — `walk_*` renames (traversals)

| Old name | New name | File |
|---|---|---|
| `emit_js_from_sm` | `walk_sm_js` | `emit_core.c` |
| `emit_jvm_from_sm` | `walk_sm_jvm` | `emit_core.c` |
| `emit_jvm_one_instr` | `walk_sm_jvm_instr` | `emit_core.c` |
| `emit_jvm_sm_range` | `walk_sm_jvm_range` | `emit_core.c` |
| `emit_net_from_sm` | `walk_sm_net` | `emit_core.c` |
| `emit_wasm_from_sm` | `walk_sm_wasm` | `emit_core.c` |
| `emit_flat_ir` | `walk_bb_flat` | `emit_bb.c` |
| `emit_bb_node` | `walk_bb_node` | `emit_bb.c` |
| `emit_bb_register_child_label` | `walk_bb_register_child_label` | `emit_bb.c` |
| `emit_pattern_blobs` | `walk_bb_pattern_blobs` | `emit_sm.c` |
| `strtab_emit_rodata` | `walk_strtab_rodata` | `emit_sm.c` |

- [x] **RE-2** — apply all `walk_*` renames; update all call sites and headers. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RE-3 — `lower_flat_*` renames + `emit_flat_intern_str` → `emit_intern_str`

| Old name | New name | File |
|---|---|---|
| `emit_flat_eligible` | `lower_flat_eligible` | `emit_bb.c` |
| `emit_flat_invariant` | `lower_flat_invariant` | `emit_bb.c` |
| `emit_flat_reset` | `lower_flat_reset` | `emit_bb.c` |
| `emit_flat_set_cap_fixup` | `lower_flat_set_cap_fixup` | `emit_bb.c` |
| `emit_flat_set_intern_str` | `lower_flat_set_intern_str` | `emit_bb.c` |
| `emit_flat_intern_str` | `emit_intern_str` | `emit_bb.c` |

- [x] **RE-3** — apply renames; update all call sites including BB templates that call `emit_flat_intern_str`. GATE-PK 442/0/612 NEW=0 GONE=0.

#### RE-4 — header and file renames (cosmetic, post-code)

Rename `emit_sm.h` → `codegen_sm.h`, `emit_bb.h` → `codegen_bb.h`, `emit_core.h` → `codegen.h` (or keep filenames stable and update only function names — Lon decides). Update `sm_templates.h` comment that references `emit_sm_dispatch`.

- [x] **RE-4** (header file renames deferred — ruling pending) — Lon ruling on header renames. Apply or close as no-op. GATE.

#### RE-5 — final audit

`grep -rn "emit_" src/emitter/emit_bb.c src/emitter/emit_sm.c src/emitter/emit_core.c` returns only:
- `emit_*` functions reachable from template roots (primitives, sinks)
- `emit_io_*` infrastructure family
- `#include` directives for header files

No `emit_*` function *definitions* remain in driver/walker files except the sanctioned primitives.

- [x] **RE-5** — audit grep; confirm zero non-sanctioned `emit_*` defs in driver files. GATE-PK 442/0/612 NEW=0 GONE=0, audit GREEN, prolog 124/0/0.

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
