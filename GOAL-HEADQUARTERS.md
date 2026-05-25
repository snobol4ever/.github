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

## Session State (2026-05-25 — LOCAL-PURGE-6 ✅ — pl_* intern driver-lifted, shared-buffer aliasing fixed)

**one4all HEAD: `07708564`.** GATE-PK **504/0/625** NEW=0 GONE=0, AUDIT GREEN, prolog 124/0/0, smoke parity 188 / run 190/71. Byte-identical.

**LOCAL-PURGE-6 ✅** — `bb_pl_atom`/`bb_pl_arith`/`bb_pl_unify`/`bb_pl_builtin` driver-lifted. `emit_intern_str` returns a SHARED static buffer (`g_intern_str_buf`), so the simultaneously-live `ls`/`rs`/`op_lbl` in arith/unify all aliased it — every label rendered as the LAST operand's `.S` (latent bug, masked by per-kind coverage). New `bb_prepare_pl(BB_t*)` (emit_bb.c, X86-gated) interns each operand up-front and copies its label into a distinct `g_emit` field (`bb_pl_ls`/`bb_pl_rs`/`bb_pl_op_lbl`, backed by `bb_pl_{ls,rs,op}_buf[64]`), wired in `walk_bb_node` before each pl_* dispatch (mirrors the LP-5 `bb_prepare_capture_arbno` pattern). All four bodies now hold ZERO `emit_intern_str` calls — pure reads of the lifted fields.

**NEXT: LOCAL-PURGE-7** (optional deeper purge — drive remaining `std::string` value-builders into fields if Lon wants strict "loop-index-only" bodies; current remaining locals are benign accumulators / node-ptr aliases / size-offsets, NOT the shared-state hazard). Or proceed to the next HQ rung. ⛔ Beauty gate SUSPENDED.

---

## Previous Session State (LOCAL-PURGE-5 ✅ — bb_arbno + bb_capture driver-lifted, all template bodies pure)

**one4all HEAD: `59e94d41`.** GATE-PK **504/0/625** NEW=0 GONE=0, AUDIT GREEN, prolog 124/0/0, smoke parity 188 / run 190/71. Byte-identical.

**LOCAL-PURGE-5 ✅** — `bb_arbno` + `bb_capture` driver-lifted. New driver fn `bb_prepare_capture_arbno(BB_t*, int imm)` in emit_bb.c (gated `PLATFORM_X86` — non-x86 arms never built rt objects, so the gate is required) computes the rt-object (`rt_bb_arbno_new`/`bb_cap_new`), emits the `# BOX` banner, dispatches `XA_BB_PTR_SLOT`, resolves the child label, and registers `g_cap_fixup_cb` — all the side-effects formerly in the template TEXT arm. Wired in `walk_bb_node` (emit_core.c) before `bb_arbno`/`bb_capture` — the single chokepoint for both the per-kind audit and real dispatch. New `g_emit` fields `bb_rt_obj` (void*) + `bb_child_lbl` (const char*). `cap_bin` reads `_.bb_rt_obj`; both template bodies now pure reads of `g_emit.bb_rt_obj` / `bb_ptr_slot_lbl` / `lbl_*`.

**FINDING:** the CALLCAP branch (`op_name2`-gated) was dead in the flat/text path — the driver always sets `op_name2 = NULL` for ASSIGN nodes, and `cap_text()`/`cap_bin()` were identical for both branches. Collapsed; behavior-preserving.

**NEXT: LOCAL-PURGE-6** (final audit — grep all `_str()` bodies for non-loop locals; only loop indices may remain). Then `bb_pl_atom`/`bb_pl_arith`/`bb_pl_unify`/`bb_pl_builtin` — DEFERRED: `emit_intern_str` returns a SHARED static buffer (`g_intern_str_buf`), so `ls`/`rs`/`op_lbl` alias it; simple-inline is unsafe. Needs driver-lift to distinct `g_emit` fields. (`xa_epilogue`(1) benign `_str` call — sanctioned.) ⛔ Beauty gate SUSPENDED.

---

## History (completed — see git log for detail)

- **LP-1/2/3/4 ✅** SM + XA + BB simple-inline + charset driver-lift (`82fc7560`, `c793cca8`). xa_bb_ptr_slot body pure, side-effects to wrapper (`760b3edc`, LP-5 prereq).
- **NB-1..3g ✅** Buffer family eliminated. `bb_bin_t {sites,labels,is_def,bytes}` replaced `bb_asm`; all MEDIUM_BINARY arms return pure `(string, bb_bin_t)`. `xa_flat` + `xa_bb_macro_library` fully pure. BRIDGE: `bb_emit_asm_result` + `bb_emit_buf`/`bb_emit_pos`/`bb_emit_size` + `bb_patch_list` ARE permanent relocation infra (rel32 forward-ref back-patch) — they STAY.
- **IFT-1..7 ✅** Templates are pure `state → string`, zero I/O. `FILE* out` removed from `sm_emit_t` (→ `g_emit_sink` in emit_io.c). `flat_drive_cat/alt/fence` de-driven through BB templates via `g_emit.xa_bb_ep_*` collection. `util_template_purity_audit.sh` is the advisory checker.
- **HQ items (b)(c) ✅** SM x86/binary baselines frozen; all SM binary arms wired. `.bin` normalizer masks movabs imm64 + imm32 ≥ 0x100000 (bitwise masked compare).
- **THE-RULE-ALL (RP-1..14) ✅** All Prolog-registry / strtab / cap-fixup / pattern-blob fprintf → XA templates. RP-13 (walk-internal JVM/NET/JS/WASM per-instruction) DEFERRED — awaits Lon.
- **CORRAL-EMIT, RENAME-EMIT (RE-1..5), OOD-1..14, OOD-PHASE-2, THREE-MEDIUM, NO-SNPRINTF, S200-EMITTER, STRIP-INTERIOR-COMMENTS, DM-1..7, TSX ✅** All complete.


## Active Rungs

### ⚡ LOCAL-PURGE — eliminate all non-loop locals from every `_str()` function — CURRENT

**Principle.** Every `_str()` body has zero local declarations except loop indices. All inputs read inline from `g_emit`/`pBB`/`pSM`. Enforces Invariant 12 mechanically. **WHOLE-TEMPLATE** (Lon): every arm (X86/JVM/JS/NET/WASM, every MEDIUM), not just X86. Three fix classes: (1) simple-inline trivial aliases; (2) `char lbl[64]`→`strtab_label_s()`; (3) driver-lift side-effecting/allocating locals to a new `g_emit` field, then inline the pure read.

- **LP-1 ✅** SM simple-inline + strtab (sm_compare/expr_incr/defines/pat_anchors/pat_combine/push_pop_lits/returns/pat_nullary).
- **LP-2 ✅** XA simple-inline (xa_pl_builder/kids_rodata/sub_builder/flat).
- **LP-3 ✅** BB simple-inline (abort/rem/len/pos/tab/alt/cat/fence/pl_var). pl_atom/arith/unify/builtin DEFERRED → LP-6 (see below).
- **LP-4 ✅** BB charset driver-lift (any/break/span/notany/arb) — `g_emit.bb_cs_id`/`bb_cs_zeta`, `rt_cs_new` ctor, `gas_escape_str`. `82fc7560`+`c793cca8`.
- **LP-5 ✅** BB arbno/capture driver-lift — `bb_prepare_capture_arbno()` (emit_bb.c, X86-gated) lifts rt-obj/banner/XA_BB_PTR_SLOT/child-lbl/cap-fixup; new `g_emit.bb_rt_obj`+`bb_child_lbl`; bodies pure. CALLCAP branch was dead (op_name2 always NULL) — collapsed. `59e94d41`. GATE-PK 504/0/625, smoke 188/190-71.

#### LOCAL-PURGE-6 — pl_* driver-lift + final audit — NEXT
- [x] `bb_pl_atom`/`bb_pl_arith`/`bb_pl_unify`/`bb_pl_builtin`: `emit_intern_str` returns a SHARED static buffer (`g_intern_str_buf`) — `ls`/`rs`/`op_lbl` aliased it (latent bug: all three rendered the LAST operand's `.S` label). Driver-lifted into distinct `g_emit.bb_pl_ls`/`bb_pl_rs`/`bb_pl_op_lbl` (backed by `bb_pl_{ls,rs,op}_buf[64]`) via new `bb_prepare_pl(BB_t*)` (emit_bb.c, X86-gated), wired in `walk_bb_node` before each pl_* dispatch. All four bodies now hold ZERO `emit_intern_str` calls — pure reads of the lifted fields. (`bb_lit` already pure; `xa_epilogue` benign `_str` — sanctioned.)
- [x] Audit: `grep emit_intern_str` in the four bodies returns 0. Remaining locals are benign value-builders (`std::string b/load_*/hdr`, node ptrs `lhs/rhs/arg`, `int j` size-offsets) — not the shared-buffer hazard. GATE-PK 504/0/625 NEW=0 GONE=0, AUDIT GREEN, PROLOG 124/0/0, smoke 188 / 190-71.

---

---

### Completed Rungs (✅ — git log has detail)

- **IFT (IO-FREE-TEMPLATES) 1..7 ✅** Templates are pure `state → string`, zero I/O. `FILE* out` gone from `sm_emit_t` (→ `g_emit_sink`). `flat_drive_cat/alt/fence` de-driven via `g_emit.xa_bb_ep_*`. Advisory checker: `util_template_purity_audit.sh`.
- **PURE-PROJECTION (PP-A..D) ✅** De-drove self-driving templates (cat/alt/fence recursion → drivers); conversion-locals + string-globals resolved. Superseded by the pure-template work above.
- **THE-RULE-ALL (RP-1..14) ✅** All Prolog-registry/strtab/cap-fixup/pattern-blob/JVM-NET-JS helper fprintf → XA templates or `_str` twins. **RP-13 DEFERRED** — walk-internal JVM/NET/JS/WASM per-instruction emission (`walk_sm_jvm/net/js/wasm`, `walk_bb_node` per-instr) still fprintf; needs per-instruction SM/XA template dispatch. Awaits Lon scope ruling.
- **RENAME-EMIT (RE-1..5) ✅** `emit_*` reserved for template-reachable fns; orchestrators→`codegen_*`, traversals→`walk_*`, lowering→`lower_flat_*`. **RE-4 DEFERRED** — header file renames (`emit_sm.h`→`codegen_sm.h` etc.) pending Lon ruling; function names done.
- **CORRAL-EMIT (CE-1..5) ✅** Every `emit_*` in driver files is a sanctioned sink/infra/atomic-builder.
- **OOD-1..14 + OOD-PHASE-2 ✅** All bare emission helpers inlined into SM/BB/XA bodies. THREE-MEDIUM ✅ (every X86 block has MACRO_DEF+BINARY+TEXT). NO-SNPRINTF ✅ `01123236`. S200-EMITTER ✅ `7857f6fc`. STRIP-INTERIOR-COMMENTS ✅ `3785ffd1`. DM-1..7 ✅. TSX ✅.
- **ER-8** relocation rethink (abs-addr PLT fallback vs rel32) — future session.


## Oracle (every gate)

**⚡ REMINDER (Lon, 2026-05-25): the per-kind baselines ALREADY EXIST for every BB/SM/XA kind. Do NOT hunt for a test program or build a `.sno` probe to prove byte-identity.** `baselines/per_kind/x86/text/<KIND>.s.{norm,raw}` and `baselines/per_kind/x86/binary/<KIND>.bin.{norm,raw}` are frozen for every kind (e.g. `BB_PAT_ANY`, `BB_PL_SEQ`, `SM_RETURN`…). `scripts/test_per_kind_diff.sh` emits each kind in ISOLATION via the per-kind audit harness and diffs against its frozen cell — so GATE-PK IS the byte-identity oracle for any template change. Workflow after editing a template: build → `test_per_kind_diff.sh` → if that kind's PASS holds and NEW=0 GONE=0, the change is byte-identical. Only reach for a real program (or the smoke suite) when a change touches the *driver/walker layer* or runtime (where no per-kind cell exists), or to exercise the live JIT (`--run`) for binary-path execution. `ls baselines/per_kind/x86/text/ | grep <KIND>` confirms a cell exists before assuming you must construct one.

`bash scripts/test_per_kind_diff.sh` → PASS=504 FAIL=0 STUB=625 NEW=0 GONE=0
`bash scripts/util_three_section_audit.sh` → AUDIT GREEN
`bash scripts/test_prolog_bb_honest.sh` → 124/0/0
Smoke (`test_smoke_snobol4_jit.sh`) only when binary paths touched: parity 188 / `--run` 190/71.

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
