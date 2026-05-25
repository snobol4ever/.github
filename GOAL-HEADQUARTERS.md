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

## Session State (2026-05-25 — CAPS-CONCAT CC-1/CC-2 ✅; X86 arms folding into IF()-concat)

**one4all HEAD: `c4b8c880`.** GATE-PK **504/0/625** NEW=0 GONE=0, AUDIT GREEN, prolog 124/0/0 — byte-identical after CAPS-CONCAT CC-1..CC-4 + bytes() arg-flip + CC-5 partial (5 SM fns).

**THIS SESSION:** CAPS-CONCAT rung (see Active Rungs). Added `IF(c,...)` (variadic — handles top-level commas, e.g. embedded `FOR(...)`) + `FOR(lo,hi,f)` macros to `emit_str.h`; `emit_for` kept as a thin alias of `FOR`. Collapsed the `PLATFORM_X86` block of **21 of 24** BB templates from a sequence of `if (MEDIUM_x){…return…}` into ONE `return IF(MEDIUM_MACRO_DEF,…)+IF(MEDIUM_BINARY,…)+IF(MEDIUM_TEXT,…);`, with `bin` set unconditionally (or via ternary) at the top of the X86 block. Branchy arms (`rpos`/`rtab`/`bb_pl_ls`/`n==0`/`xa_bb_ep_n>0`) folded via `?:` ternaries; charset-FOR family (`any`/`notany`/`break`/`span`) and `cat`/`alt`/`fence` use `FOR(...)`. Helper `scripts/consolidate_x86_arm.py` (brace-parser; SKIPs branchy arms). Every batch built + gated byte-identical.

**LESSONS:** (1) function-style `IF` chokes on top-level commas → made it variadic. (2) Folding `alt`/`cat` dropped their empty `MEDIUM_BINARY` arm → three-section AUDIT went RED; restored as `IF(MEDIUM_BINARY, std::string())`. Even empty arms must keep their `IF(MEDIUM_x,…)` slot. (3) **Real obstacle:** `bb_pl_arith`/`bb_pl_unify`/`bb_pl_builtin` compute `bin` offsets from `(int)b.size()` of a variable-length byte prefix built INSIDE the binary arm — `bin` is data-dependent, can't be hoisted. Left as explicit medium blocks pending Lon's call on an IIFE-with-side-effect fold (CC-3 details).

**GATES (end of CAPS-CONCAT pass):** GATE-PK **504/0/625** NEW=0 GONE=0, AUDIT GREEN, prolog 124/0/0. Byte-identical. ⛔ Beauty gate SUSPENDED.

**NEXT:** Lon's call on the 3 pl_* obstacle files (CC-3), then optional CC-5 (extend to SM/XA + non-x86 arms). Icon BB-construction (`SM_BB_EVAL`/`PUMP_EVERY`/`PUMP_CASE`) remains the standing HQ target.

---

## Previous Session State (2026-05-25 — SM_PUMP_BB deleted; SM opcode/macro/template inventory recorded)

**one4all HEAD: `db4c355f`.** GATE-PK **504/0/625** NEW=0 GONE=0, AUDIT GREEN, prolog 124/0/0, PURITY GREEN. Byte-identical.

**THIS SESSION:** LP-7-NONX86 closed LOCAL-PURGE (PURITY GREEN, `7164247b`). Then audited SM opcode coverage and deleted one dead opcode.

**SM_PUMP_BB DELETED (`db4c355f`)** — it was the LAST enum value before `SM_OPCODE_COUNT`, so removal renumbered nothing (baselines safe). No lowering site emitted it. Removed enum entry + dead `sm_interp.c` case + `g_handlers` NULL line.

**⚠ ENUM IS POSITIONAL** — only `SM_LABEL = 0` is explicit; all others implicit/sequential. Deleting any MID-enum opcode renumbers everything after it → invalidates frozen per-kind baselines, `g_handlers[]`, name tables, serialized SM. Mid-enum deletions require a full baseline re-freeze — NOT a quick edit.

**SM OPCODE INVENTORY (89 total after deletion):**
- **WITHOUT a template function: 13** — `SM_BB_EVAL`, `SM_BB_ONCE`, `SM_BB_PUMP`, `SM_BB_PUMP_CASE`, `SM_BB_PUMP_EVERY`, `SM_BB_PUMP_SM`, `SM_ICMP_GT`, `SM_ICMP_LT`, `SM_LOAD_FRAME`, `SM_LOAD_GLOCAL`, `SM_STORE_FRAME`, `SM_STORE_GLOCAL`, `SM_SUSPEND`. (76 have one.)
- **WITHOUT a macro: 14** — same set minus the ICMP pair (which share `COMP`), plus `SM_EXEC_BB` (has a template fn `sm_exec_bb` but NO macro — its TEXT arm is raw inline asm; lone "fn-but-no-macro" case).

**Breakdown of the 13 missing-template opcodes:**
- **LIVE Icon generator scaffolding, SILENTLY DROPPED (3):** `SM_BB_EVAL`, `SM_BB_PUMP_EVERY`, `SM_BB_PUMP_CASE`. Lowering (`lower.c`) emits these across MOST of the Icon corpus (e.g. `rung36_jcon_ck.icn`:141, `_numeric`:111, `_augment`:127 occurrences) for every/limit/case/generator-in-value-context. The x86 emitter has NO case → they fall through `codegen_sm_dispatch` `default: return 0` and VANISH (no stub, no diagnostic). This is the cause of widespread Icon segfaults/aborts. ⚡ THESE ARE THE REAL TARGETS for the upcoming Icon BB-construction session — not dead, just unwired. (Note: simple Icon every-loops route through `SM_BB_PUMP_PROC`, which IS dispatched+macro'd and works; the bare ops are the unfinished richer-context path. `ICN_BB_EVAL(t)` macro in lower.c is now a NO-OP since DAI-3.)
- **DEAD, mid-enum (3):** `SM_BB_ONCE` (deleted PB-7, now FATAL if reached), `SM_BB_PUMP`, `SM_BB_PUMP_SM` — no live emit site. Deletable but need baseline re-freeze (positional enum).
- **INTERP-ONLY / lowering-rewritten (7):** `SM_ICMP_GT`, `SM_ICMP_LT` (share `COMP`), `SM_LOAD_FRAME`, `SM_STORE_FRAME`, `SM_LOAD_GLOCAL`, `SM_STORE_GLOCAL`, `SM_SUSPEND` — never reach x86 emission.

**ALSO FOUND (macro/inline toggle):** the old expanded-vs-macro'd `.s` view collapsed during template migration. Every SM `MEDIUM_TEXT` arm emits the macro INVOCATION; the expanded bodies live ONLY in `MEDIUM_MACRO_DEF` arms. `g_emit_inline`/`EMIT_TEXT_INLINE`/`USE_SM_MACROS` scaffolding survives but: no CLI flag sets `g_emit_inline=1`, and NO template reads `USE_SM_MACROS`. Probe-verified: forcing inline=1 skips the `.macro` preamble but still emits invocations → un-assemblable (`no such instruction: 'push_int 2'`). Reviving expanded view = add `--inline` flag + each TEXT arm branches `USE_SM_MACROS ? invocation : <MACRO_DEF body via shared _str helper>`.

**NEXT:** Icon + Prolog BB-construction sessions (Lon, imminent) — wire `SM_BB_EVAL`/`PUMP_EVERY`/`PUMP_CASE` to real x86 templates. Then batch-delete the 3 dead mid-enum ops with a baseline re-freeze. ⛔ Beauty gate SUSPENDED.

---

## Previous Session State (LOCAL-PURGE COMPLETE ✅ — TEMPLATE-PURITY GREEN, every arm pure)

**one4all HEAD: `7164247b`.** GATE-PK **504/0/625** NEW=0 GONE=0, AUDIT GREEN, prolog 124/0/0, smoke parity 188 / run 190/71. **TEMPLATE-PURITY GREEN.** Byte-identical.

**LP-7-NONX86 ✅** — `bb_capture` JVM + JS arms converted to pure-return (the last two side-effecting template arms), matching the NET arm's idiom. Mechanical byte-identical substitution: `emit_directive→s_directive`, `emit_1asm/2asm→s_1asm/2asm`, `jvm_class_hdr_str` side-effect-wrap → direct concat, `emit_textf→emit_fmt`, `js_escape_string_str` inlined. `util_template_purity_audit.sh` is now **TEMPLATE-PURITY GREEN** (was 45 violations, all in bb_capture). **This completes LOCAL-PURGE / HQ Invariant 16 at 100%: every BB/SM/XA template arm — x86/JVM/JS/NET/WASM, every medium — is a pure `state → std::string`; only the `extern "C"` dispatch wrappers + the sanctioned MEDIUM_BINARY rel32 patch idiom touch a sink.** No regression: JVM smoke 7/6 + JS smoke 0/6 both identical to pre-change baseline (failures are pre-existing JVM/JS emitter-rewrite gaps — see SJ4-JVM-4 / SJ4-JS-BB1a goals). ⚠ x86-only restriction was lifted by Lon for this conversion. ⛔ Beauty gate SUSPENDED.

**NEXT:** LOCAL-PURGE rung is CLOSED. Pick next HQ work or another active goal. The earlier LP-6 PL_ARITH 3-label coverage gap (below) remains an optional regression-cell task.

---

## Previous Session State (LOCAL-PURGE-6 ✅ — pl_* intern driver-lifted, shared-buffer aliasing fixed)

**one4all HEAD: `07708564`.** GATE-PK **504/0/625** NEW=0 GONE=0, AUDIT GREEN, prolog 124/0/0, smoke parity 188 / run 190/71. Byte-identical.

**LOCAL-PURGE-6 ✅** — `bb_pl_atom`/`bb_pl_arith`/`bb_pl_unify`/`bb_pl_builtin` driver-lifted. `emit_intern_str` returns a SHARED static buffer (`g_intern_str_buf`), so the simultaneously-live `ls`/`rs`/`op_lbl` in arith/unify all aliased it — every label rendered as the LAST operand's `.S` (latent bug, masked by per-kind coverage). New `bb_prepare_pl(BB_t*)` (emit_bb.c, X86-gated) interns each operand up-front and copies its label into a distinct `g_emit` field (`bb_pl_ls`/`bb_pl_rs`/`bb_pl_op_lbl`, backed by `bb_pl_{ls,rs,op}_buf[64]`), wired in `walk_bb_node` before each pl_* dispatch (mirrors the LP-5 `bb_prepare_capture_arbno` pattern). All four bodies now hold ZERO `emit_intern_str` calls — pure reads of the lifted fields.

**NEXT: LOCAL-PURGE-7** (optional deeper purge — drive remaining `std::string` value-builders into fields if Lon wants strict "loop-index-only" bodies; current remaining locals are benign accumulators / node-ptr aliases / size-offsets, NOT the shared-state hazard). Or proceed to the next HQ rung. ⛔ Beauty gate SUSPENDED.

**LP-6 COVERAGE FINDING (for whoever next touches PL_ARITH/PL_UNIFY):** the 3-simultaneous-label TEXT path in `bb_pl_arith`/`bb_pl_unify` is NOT reached by the per-kind harness (interning is inert there — `emit_per_kind_audit.c` never wires strtab/`g_is_text`/`lower_flat_set_intern_str`, so `emit_intern_str` returns NULL and the frozen cell shows all-NULL: `xor edx,edx`/`xor r9d,r9d`/`push 0`) NOR by any current corpus program (`X is foo+bar` lowers via the Prolog *builder* path `rt_pl_b_node`, not the PL_ARITH BB template). That coverage gap is WHY the shared-buffer aliasing stayed latent. The fix is verified byte-identical on every path that DOES exercise these templates (GATE-PK + smoke + prolog all green). A future cell that drives PL_ARITH with three distinct live svals would lock the fix in — but it requires bootstrapping the intern/strtab subsystem inside the isolated harness (invasive, risks all 504 cells), so DEFERRED.

**PURITY-AUDIT FINDING (`util_template_purity_audit.sh`, 2026-05-25):** advisory audit is GREEN for x86/binary/TEXT. The only remaining non-binary side-effect violations are the **JVM + JS arms of `bb_capture.cpp`** (lines ~88–111): they call `emit_directive`/`emit_2asm`/`emit_1asm`/`emit_textf`/`emit_text_n` directly and `return std::string()` (empty), instead of building+returning the string (pre-existing — IFT-2 converted only the NET arm; LP-5 did x86/binary). The former `xa_epilogue.cpp:21` flag was a FALSE POSITIVE (regex matched the pure `_str` twin `wasm_emit_data_segments_str`); FIXED in `f5fafb68` by anchoring the regex token to `(` (the side-effecting form no longer exists). Audit now reports a clean worklist: 45 violations, all in `bb_capture.cpp`. ⚠ Converting the bb_capture JVM/JS arms is BLOCKED on RULES "X86 ONLY FOR NOW — do not write JVM/JS/NET/WASM arms until explicitly directed" AND there is no non-x86 byte-identity gate to protect the rewrite. AWAITS LON: convert these two arms to pure-return (LP-7-NONX86) or leave until the JVM/JS emitters are reactivated.

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

### 🔄 CAPS-CONCAT — one `return` per X86 arm via `IF(...)`/`FOR(...)` selectors

**Principle.** Every template's `PLATFORM_X86` block collapses from a sequence of
`if (MEDIUM_x) { … return …; }` statements into ONE return: a big concat of
`IF(MEDIUM_MACRO_DEF, …) + IF(MEDIUM_BINARY, …) + IF(MEDIUM_TEXT, …)`. The medium
selector is now visible at a glance and mirrors the eventual Snocone port (`+`→`.`).
`bin` is set UNCONDITIONALLY at the top of the X86 block (only read on the binary
path, harmless elsewhere) — this dodges the side-effect-in-expression problem.
Only the X86 arm is consolidated this pass; JVM/JS/NET/WASM left untouched.

**Macros (emit_str.h):** `IF(c, ...) ((c) ? (__VA_ARGS__) : std::string())` — variadic
so the string expression may contain top-level commas (e.g. a `FOR(0,n,lambda)` call).
`FOR(lo,hi,f)` = pure concat loop `f(lo)+…+f(hi-1)`; `emit_for` kept as a thin alias
during migration (call sites flip to `FOR`, then alias is deleted).

- [x] **CC-1** `IF`/`FOR` macros added to `emit_str.h`; `emit_for`→`FOR` alias. Pilot `bb_pat_len` consolidated. GATE-PK 504/0/625 byte-identical.
- [x] **CC-2** Simple uniform X86 arms consolidated (one each MACRO_DEF/BINARY/TEXT, single bin assign): `bb_eps`, `bb_fail`, `bb_pat_abort`, `bb_pat_rem`, `bb_pl_var`, `bb_arbno`, `bb_capture`. Plus FOR-only arms hand-edited: `bb_pat_alt`, `bb_pat_cat`. Helper `scripts/consolidate_x86_arm.py` (parses brace structure; SKIPs branchy arms). GATE-PK 504/0/625 byte-identical.
- [x] **CC-3** Branchy X86 arms — internal `if` inside a medium lifted into the string expr (`?:`) before folding. **DONE (11/14):** `bb_lit`, `bb_pat_any`, `bb_pat_arb`, `bb_pat_break`, `bb_pat_notany`, `bb_pat_span`, `bb_pat_pos`, `bb_pat_tab`, `bb_pat_fence`, `bb_pl_atom`, `bb_pl_seq`. (`rpos`/`rtab`/`bb_pl_ls`/`n==0`/`xa_bb_ep_n>0` structural branches → ternaries; `bin` set via ternary at top of X86 block.) GATE-PK 504/0/625, AUDIT GREEN, prolog 124/0/0 — byte-identical throughout.
      **⚠ AUDIT REGRESSION CAUGHT+FIXED:** folding `bb_pat_alt`/`bb_pat_cat` dropped their (empty) `MEDIUM_BINARY` arm → `util_three_section_audit.sh` went RED (MISSING-BINARY). Restored as `IF(MEDIUM_BINARY, std::string())` — AUDIT GREEN again. Lesson: even an empty arm must keep its `IF(MEDIUM_x, …)` slot so the three-section audit stays GREEN.
      **💡 FUTURE IDEA (Lon, 2026-05-25) — `SIZE(&len, expr)` selector:** the data-dependency CAN be expressed inside one concat with a new helper `SIZE(int* out, std::string s) { *out = (int)s.size(); return s; }`. Then the binary arm becomes, e.g., `IF(MEDIUM_BINARY, SIZE(&len, IF(_.bb_pl_ls, movabs(lhs)) + IF(_.bb_pl_rs, movabs(rhs)) + call_indirect) + SET_BIN(len, …) + tail_bytes)` — `len` is captured mid-concat, then the `bin` offsets are computed from it. Needs a tiny `SET_BIN(...)` (or IIFE) that writes `bin` by ref and returns `""`. This keeps the one-return shape AND handles the size-dependent offsets. Deferred — try on `bb_pl_arith` first as the prototype, then `unify`/`builtin`.
- [x] **CC-4** All real `emit_for(` call sites flipped to `FOR(` (during CC-2/CC-3). `emit_for` alias retained in emit_str.h (harmless; delete is cosmetic). Remaining grep hits are `emit_form.h` substring false-positives, not calls.
- [ ] **CC-4** Flip remaining `emit_for`→`FOR` (bb_pat_break/span/fence/any/notany + bb_template_common.h), then delete the `emit_for` alias.
- [ ] **CC-5** Extend `IF()`-concat fold to SM_templates (and later XA + non-x86 arms). **DONE (5 fns):** `sm_halt`, `sm_exec_bb`, `sm_pat_anchors`, `sm_pat_nullary`, `sm_compare`. SM templates have NO `bin` param (pure `(const SM_t*)→std::string`; binary arm just returns bytes) — simpler than BB, no bin-hoist. GATE-PK 504/0/625, AUDIT GREEN — byte-identical.
      **SM-specific gotchas / remaining work (per-block, not per-file — one file holds several `_str` fns, each its own X86 block):**
      - **`std::pair<std::string,int>` return shape (SKIP for plain IF):** `sm_calls` (sm_call_str), and blocks in `sm_jumps`, `sm_returns`. Their arms return `{string, flag}` — `IF(c,s)` yields `std::string()` on false, which won't compose with a pair. Needs a pair-aware selector or restructure; left as explicit medium blocks.
      - **Side-effecting TEXT arm (SKIP or IIFE):** `sm_stno` (in sm_compare.cpp) calls `emit_text_stno_banner(...)` BEFORE its return — two statements, can't fold into `IF(MEDIUM_TEXT, expr)` without dropping the banner. Same pattern likely in `sm_defines`/`sm_expr_incr`/`sm_pat_combine`/`sm_push_pop_lits` (each has 2–5 side-effect calls in X86 arms — inspect per block). Fold only the blocks whose arms are single pure returns.
      - **Clean multi-block candidates to finish:** re-inspect `sm_arith`(2), `sm_bb_calls`(2), `sm_jumps`(2, minus pair block), `sm_pat_combine`(5), `sm_push_pop_lits`(4), `sm_expr_incr`(3), `sm_defines`(1) block-by-block; fold the pure-return blocks, leave pair/side-effect ones. Then XA_templates, then (much later) the JVM/JS/NET/WASM arms.

---

### ✅ LOCAL-PURGE — COMPLETE (every `_str()` arm pure; TEMPLATE-PURITY GREEN)

**Principle.** Every template arm is a pure `state → std::string` — no side-effecting emission, no shared-buffer/aliasing locals. Enforces Invariants 11/12/16 mechanically. Done across ALL arms (X86/JVM/JS/NET/WASM, every MEDIUM).

- **LP-1 ✅** SM simple-inline + strtab (sm_compare/expr_incr/defines/pat_anchors/pat_combine/push_pop_lits/returns/pat_nullary).
- **LP-2 ✅** XA simple-inline (xa_pl_builder/kids_rodata/sub_builder/flat).
- **LP-3 ✅** BB simple-inline (abort/rem/len/pos/tab/alt/cat/fence/pl_var). pl_atom/arith/unify/builtin DEFERRED → LP-6 (see below).
- **LP-4 ✅** BB charset driver-lift (any/break/span/notany/arb) — `g_emit.bb_cs_id`/`bb_cs_zeta`, `rt_cs_new` ctor, `gas_escape_str`. `82fc7560`+`c793cca8`.
- **LP-5 ✅** BB arbno/capture driver-lift — `bb_prepare_capture_arbno()` (emit_bb.c, X86-gated) lifts rt-obj/banner/XA_BB_PTR_SLOT/child-lbl/cap-fixup; new `g_emit.bb_rt_obj`+`bb_child_lbl`; bodies pure. CALLCAP branch was dead (op_name2 always NULL) — collapsed. `59e94d41`. GATE-PK 504/0/625, smoke 188/190-71.
- **LP-6 ✅** BB pl_* intern driver-lift — `bb_prepare_pl()` (emit_bb.c, X86-gated) lifts ls/rs/op_lbl into distinct `g_emit.bb_pl_{ls,rs,op_lbl}` buffers, fixing the `emit_intern_str` `g_intern_str_buf` shared-buffer aliasing. `07708564`. Audit false-positive (xa_epilogue) fixed `f5fafb68`.
- **LP-7-NONX86 ✅** bb_capture JVM + JS arms → pure-return (NET-arm idiom). Last side-effecting arms. `7164247b`. **TEMPLATE-PURITY GREEN.** x86-only restriction lifted by Lon for this conversion.

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
