# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 61, 2026-06-15)

**Landed this session (SCRIP `src/emitter/emit_bb.c` ONLY — zero template/x86/binary/runtime changes): the `bb_gvar_assign call-result: op_a_slot==-1` BOMB (the prior handoff's named NEXT FRONTIER) is FIXED by converting the two emitter side tables from fixed-size static arrays to dynamic `realloc`-grown arrays — NO hard caps remain.** ROOT CAUSE: `BB_SLOTMAP_MAX 512` (`static g_bb_slotmap[512]`); every `bb_slot_alloc*`/`bb_slot_register` guarded its append `if (g_bb_slotmap_n < BB_SLOTMAP_MAX)`, so past 512 entries the append SILENTLY no-op'd → a large proc's call-result node never got a slot → `bb_slot_get` returned −1 → `op_a_slot==-1` → `x86_bomb`. Same latent-cap class as the `BB_PATCH_MAX` fix. FIX (per Lon's "use dynamic REALLOC arrays, don't hard-code limitations"): `g_bb_slotmap` → typed ptr + `_n` + `_max` grown by a new `bb_slotmap_push` helper using the SAME doubling idiom `emit_label_alloc` already uses in this subsystem (`new_max = max?max*2:512; realloc`); all 5 appenders + the one inline push (`flat_drive_gen_scan`) route through it. `g_bb_varslot` (was 256) likewise dynamic (`max?max*2:256`). Per-proc resets still set only `_n=0`; the `realloc`'d buffers persist at their `_max` and are reused (grow once to the largest proc, no per-proc churn). `BB_SLOTMAP_MAX`/`BB_VARSLOT_MAX` are GONE (grep==0). VALIDATED: Pascal **M3 123/0, M4 123/0** (unchanged, no regression); new canaries `charA N=90` AND `charbig N=300` print `[S][A][B][E]` in BOTH M3/M4 (prove the wall is GONE not moved — N≈90 was where this bomb began); SNOBOL4 M4 crosscheck 166/87/8 byte-identical; SNOBOL4 DEFINE `DOUBLE(21)=42` M3==M4 (shares the gvar driver+slotmap); Icon/Prolog `hello` clean; template-medium-invisible `--strict` 0 violations. Diff +28 −11, one file. Full writeup: **HANDOFF-2026-06-15-PASCAL-BB-DYNAMIC-SLOTMAP-AND-VARPARAM-AGGREGATE-FRONTIER.md**.

**NEXT FRONTIER (precisely diagnosed + POC-validated this session, NOT introduced by the fix — baseline bombs EARLIER at `op_a_slot==-1`): var-param of a heap-aggregate field.** With the slotmap fixed, `scrip --run pcom.pas < tiny.pas` (tiny=`program t(output); begin end.`) advances much further and hits a DIFFERENT runtime bomb: `marshal_varparam_addr: var-param arg is not a variable`. Exact culprit (instrumented): `procedure genlabel(var nxtlab: integer)` (pcom l.847) called as `genlabel(uprcptr^.pfname)` inside `with uprcptr^ do …` (pcom l.3787, l.3793) — the `with` on a DEREFERENCED pointer resolves field `pfname` to `arr_get(__pas_deref(uprcptr), idx)`, and because `nxtlab` is BY-REF, the marshaller's byref branch calls `marshal_varparam_addr` on that `arr_get` (op IR_CALL=9), which only handles `IR_VAR_FRAME`(162)/`IR_VAR_FRAME_REF`(164)/named `IR_VAR`(4) → falls to `x86_bomb`. (Of ALL pcom byref args: 91× IR_VAR_FRAME, 2× IR_VAR_FRAME_REF, 6× named IR_VAR, **2× arr_get(idx=0, callee=genlabel)** — only the 2 arr_get bomb.) **FIX IS A PURE AST/LOWERING REWRITE, ZERO EMITTER RISK** — `genlabel(p^.fld)` → `tmp := p^.fld; genlabel(tmp); p^.fld := tmp` (var-param then receives a frame-local `IR_VAR_FRAME`, already handled). **POC PROVEN M3+M4 this session:** the manual rewrite `t:=p^.fld; t:=42; p^.fld:=t; writeln(p^.fld); writeln(p^.other)` prints `42`/`99` (write-back lands in fld, sibling untouched) in BOTH modes — both legs (deref-field read; deref-field write-back via existing `__pas_deref_set`) already work, only the auto-rewrite is missing. Concrete 5-step plan + gated probe `vpfld.pas` (reproduces the bomb today, expects `42`/`99`) in the handoff. Byref mask available at lower time via `g_stage2.proc_table[pi].byref_mask`. **LESSON (logged): a failed `make -j4 scrip` leaves the PREVIOUS good `scrip` in place → runs use a stale binary → instrumentation appears not to fire. ALWAYS `rm -f scrip` AND confirm `[ -x scrip ]` + fresh build log after every edit.**

## ▶ PRIOR Session 60 (2026-06-14)

**Landed this session (SCRIP runtime+driver — `rt.c`, `rt.h`, `emit_bb.c`, `scrip.c`; frame allocation ONLY, ZERO template/x86/emit changes): the per-procedure FRAME-SLOT-ARENA overflow is FIXED via a dynamic running-offset (stack) frame allocator sized per-proc by the actual slot peak, with a 4096-byte floor.** ROOT CAUSE of the Session-59 "pcom M3 emits nothing, rc=0, no abort" frontier: per-proc frame slots accumulate MONOTONICALLY across a whole proc body (`bb_slot_alloc16` only `+=16`, never reused between statements), so `g_flat_slot_count` at body-end = the PEAK frame-bytes the emitted `[reg+off]` code needs; but the runtime gave EVERY nested-proc frame a FIXED 4096-byte slice (`PROC_FRAME_NEST_QWORDS=512`, `fb=&arena[depth*512]`). A proc past 4096 B wrote into the next frame → corrupted the static link/return → returned FAILDESCR → caller's `cmp eax,99; je ω` dropped the rest of its chain. First overflow in pcom is `chartypes` (~64 `array[char]` assigns × 64 B = exactly 4096); measured worst peaks **pcom 13008 B, pint ≥11152 B** (3.2× the slice). FIX (5 edits): `emit_bb.c` exposes `g_last_flat_frame_bytes` (peak after `codegen_gvar_flat_chain_body`); `rt.c` adds `frame_bytes` to `rt_proc_t` + `rt_proc_set_frame_bytes` + a 1-D 64 MB running-cursor arena, rewriting `rt_call_named_proc`/`_sl` to reserve `max(4096, frame_bytes)` per frame (overflow-guarded); `scrip.c` plumbs the peak in BOTH the shared M3 gvar branch and the M4 `proc_startup` emit. THE FLOOR (`max(4096,·)`) makes the change a STRICT SUPERSET of baseline — frames only ever GROW, never shrink — so regression is impossible by construction (neutralises any emit-time peak UNDER-count, e.g. SNOBOL4 prebuild slots). VALIDATED: Pascal M2/M3/M4 all **122/0 XFAIL=1** (unchanged); minimal reproducer charA N=64 now PASSES in M4 (was dropping); SNOBOL4 mode-4 crosscheck **166/87 BYTE-IDENTICAL** before/after; Icon 4/0; Prolog 102/38 (pre-existing). **pcom is STILL NOT self-hosting — it is gated by FOUR further INDEPENDENT bugs (none a frame issue): (1) M3 in-process call does NOT reach the sized-frame dispatcher (charA N=64 passes M4 but still drops M3 — the MEDIUM_BINARY `outer→ctypes` call emits `mig=1` and `frame_bytes` IS registered, yet `ctypes` never hits `rt_call_named_proc_sl` at runtime; bb_call.cpp l.408 binary path vs l.391 text path); (2) `bb_gvar_assign call-result: op_a_slot==-1` BOMB at extreme statement counts (charA N≥150, pint); (3) M4 duplicate-label collision `'.Lcallfn6716' is already defined` blocks pcom assembly (`.Lcallfn%d`/`.Lprocfn%d` ids collide across procs); (4) pint SEGFAULTS during emission. Full signatures + reproducers + next steps in HANDOFF-2026-06-14-PASCAL-BB-FRAME-ARENA-OVERFLOW-FIX.md. Suggested order: (3) mechanical → unblocks reading pcom M4 output; (1) → unblocks M3; then (2),(4).**

**PRIOR Session 59 landed (SCRIP `emit_bb.c`, ONE line): the EMPTY-PROCEDURE-CALL chain-drop bug (the Session-58 "live pcom BLOCKER", open item #1) is now CLOSED in M3/M4.** Root cause: `codegen_gvar_flat_chain_body` (the gvar flat-chain proc-body driver Pascal/SNOBOL4 run on) defines `<proc>_α_body:` then emits the statement chain; for an EMPTY body (`begin end`) all nodes are `IR_SUCCEED`/`IR_FAIL` → `gvar_chain_is_real` rejects them → `n==0` → nothing emits between `α_body:` and `β:`, so `α_body` FELL THROUGH into `β: jmp ω` (the GZ-10 PROC FAIL EXIT, which writes FAILDESCR/eax=99 to frame[0] and returns). `rt_call_named_proc` then saw `IS_FAIL_fn(fret)` true → returned FAILDESCR → the CALLER's `cmp eax,99; je ω` took ω → the caller's whole statement sequence FAILED, silently dropping every statement after the empty-proc call. Fix: `if (n == 0) emit_jmp_label(&lbl_γ, JMP_JMP);` right after the node-emission loop, so an empty body jumps to SUCCESS (γ) instead of falling into FAIL (β/ω). No-op for any non-empty body (`n>0`); semantically a `begin end` block always succeeds. The fix is in the chain-WIRING driver (not a `bb_*.cpp` template); `emit_jmp_label` is the sanctioned medium-complete jump emitter used throughout that function — zero raw bytes, zero `MEDIUM_*`, zero language names. All three Pascal gates 121→122 (+1 probe `emptyproc.pas`, two interleaved empty procs → `3`, M2-ref'd width-10). Cross-language clean: SNOBOL4 7/0 ×3 (incl. empty-DEFINE canary, shares the gvar driver), Icon 12/0 ×3, Prolog 5/0 ×3, Raku 37/0 m2 (EXCISED=2 pre-existing). **pcom re-driven on the tiny `begin end` program: M2 now emits the full 3-line source listing; M3 still emits NOTHING (rc=0, no abort) and M4 compiles (234K lines asm, no error). So pcom has a DEEPER M3-specific divergence beyond empty-proc — its first output (the source-listing `write`) never reaches stdout in M3. That is the new pcom frontier; pcom is NOT gated and deserves a fresh context budget.**

**PRIOR Session 58 landed: PART B of the pcom NEXT BLOCKER — the in-place NESTED-AGGREGATE STORE, plus the F2 disambiguation. The pcom NEXT BLOCKER (open item #1) is now CLOSED. All three Pascal gates 115→121 (+6 gated probes), full M2/M3/M4 parity, zero regressions. Cross-language smoke clean (SNOBOL4/Icon/Prolog + DEFINE DOUBLE(21)=42 canary). Files touched: `pascal.y`, `pascal_driver.h`, `lower_pascal.c`, `by_name_dispatch.c` (+ regenerated `pascal.tab.{c,h}`). ZERO emitter/template/machine/interp/contracts files; template purity preserved (no x86 emission added). pcom's fatal `kind=172`/`kind=9` emit-time abort is GONE — pcom now runs its real logic (with a const-decl program it emits the source listing line `1   9 program t(output);`, then stops at the separately-tracked empty-procedure-call runtime bug, which is now the live pcom blocker).**

**WHAT LANDED (the F1/F2/F3 plan from Session 57, executed together):**
- **(F2 disambiguation — `pascal.y`):** a node-pointer side-table `g_pas_nrec_marks[512]` + `pas_nrec_mark_add` + exported `pas_is_nrec_idx`. `pas_nested_field_resolve` now calls `pas_nrec_mark_add(e)` on every nested-record `TT_IDX` it builds, so the nested-record index is distinguishable from a packed-char-array deref-field index (which is shape-identical). Did NOT overload `v.ival` (it holds the enum mark). Reset in `pascal_parse_string`.
- **Store lowering — `pascal.y` `mk_assign`:** a NEW FIRST-priority branch (before the deref-char-field branch) detects the marked nested `TT_IDX`. Deref base (`ptr^.fld.sub := v`) → `__pas_nrec_deref_set(ptrkey, fi, ei, rhs)`. Gvar base (`g.fld.sub := v`) → `TT_ASSIGN(base, __pas_nrec_update(base, fi, ei, rhs))` (read-modify-write of the whole record string, stored back into the gvar by name — frame-local record vars also work via lower_assign_var by name).
- **Read lowering — `lower_pascal.c` TT_IDX case:** marked nested read → 3-arg `__pas_nrec_get(base, fi, ei)` IR_CALL (dval 2.0 by-name) instead of `arr_get(arr_get(…))`. `base` is the gvar or `__pas_deref(p)` (both evaluate to the whole record string). Added `#include "../parser/pascal/pascal_driver.h"`.
- **(F3 storage — `by_name_dispatch.c`):** SEPARATOR is `\x05` (ENQ — confirmed unused anywhere in the file; STX `\x02` was avoided as it's used by the KV/table paths). One static helper `pas_nrec_subrec_set(cur, fi, ei, val)` (read field fi via SOH walk, split that field's value by `\x05`, set element ei with auto-grow filling missing earlier elements with "0", rejoin, splice back into the parent SOH segment). Three Pascal-name-scoped builtins in `script_try_call_builtin_by_name` (right after `__pas_deref_set`): `__pas_nrec_get` (read → `elem_to_descr` so digit strings become INTVAL), `__pas_nrec_update` (gvar RMW → returns new record STRVAL), `__pas_nrec_deref_set` (heap RMW on `__heap_N`). Additive — other frontends never call `__pas_nrec_*`; `try_call_builtin_by_name` delegates to `script_try_call_builtin_by_name` at the tail (verified line ~3469), the same path `arr_get`/`__pas_field_idx_set` use, so NO proc_as_value entry and NO emitter work needed. Ran `make libscrip_rt` (M4 links the external `.so`).

**WHY F1 IS SOLVED:** the nested sub-record lives inside the parent's single SOH slot as a `\x05`-separated string, so the parent still sees exactly one segment — `arr_get(parent, sibling_idx)` and whole-record copy (`min := values`, a verbatim opaque string copy) stay correct. The SOH-count torture probe `nestcheck` (outer{x, c:inner{a,b}, y}, all four leaves r/w including RMW `g.c.a := g.c.a+1`) confirms no sibling corruption.

**GATED PROBES ADDED (all pass M2/M3/M4, refs from M2 width-10, fpc-value-cross-checked):** `nestrec1` (gvar nested int, 4 fields), `nestptr1` (`new(p); p^.c.a := …` deref nested int), `nestwith1` (`with lcp^ do values.ival := 55` — the exact Session-57 read-back-0 repro, now correct), `nestcheck` (SOH-count torture), `nestpv` (single-level pointer field + deref), `nestpv2` (the exact pcom:2889 shape — `gattr.cval.ival := 42` + `gattr.cval.valp := lvp` nested pointer subfield + `gattr.cval.valp^.num` deref read).


**PRIOR SESSION (56) — for reference, all three Pascal gates 112→115 (+3). Two fixes, each regression-protected by a new gated probe.**
(1) **Enum `writeln`** (+2: `pb36` enum field in array-of-record `d[0].occur`; `pb37` `array[char] of enum` `chartp[ch]`). Both now print the enum constant NAME (`blck`, `letter`) matching the fpc oracle in M2/M3/M4. Parser (`pascal.y`): new enum-type→constant-names CSV table `g_pas_enumnames` (built in the `(a,b,c)` enum rule, committed in `type_decl`); a parallel `fldenum[]` channel threaded pend→rectype→arrrec so a record field's enum type survives field-name erasure (`pas_pend_add` captures it from `g_pas_pend_typename`; `record_case_opt` sets the typename for the case-selector field); an `enumarr` table for plain `array[<idx>] of enum`; node-marking via the otherwise-unused `TT_IDX.v.ival` (= enum-names-index+1) at the two selector reductions (`[ ]` for enum arrays, `.field` for enum fields of array-of-record AND record variables). `mk_call`'s writeln/write loop reads the mark and wraps the value `__pas_enum_name(val, "csv")`. **`ord` clears the mark** on its unwrapped `TT_IDX` (it wants the ordinal) — this fixed a `chararr3` regression (`writeln(ord(chartp['a']))` was printing the name). Runtime (`by_name_dispatch.c`): `__pas_enum_name(ord, csv)` returns the nth comma-separated token as `DT_S` (flows through writeln's no-padding string path); registered in `proc_as_value`'s list + `try_call_builtin_by_name`, mirroring `__pas_chr`.
(2) **CALL-vs-CALL char-array ordering** (+1: `chararrcvc`, `rw[i] < rw[j]` on an array-of-char-arrays — pcom's reserved-word compare). ONE-LINE parser fix: `pas_is_strtyped` now also recognizes `TT_IDX(TT_VAR v, …)` where `pas_is_chararr(v)`, so indexed char-array operands carry the string-type hint → `lower_binop` sets `IR_LIT(op).dval=1.0` → the existing type-polymorphic descriptor arm (`bb_binop_gvar_relop.cpp`) fires for all six relops. SAFE for flat char-array elements (`s[i] < s[j]`): the descriptor arm's `DT_I` fallback gives the same result as the int fast path (single-char lexical == ordinal). M3 `notless/notless` → `less/notless`, matching M2/oracle. No emitter change — the arm already existed (session 51); only the parser hint was missing.
**`array[char] of T`** (former open item #2): needed NO work — `pb37` confirmed char-indexed array access already works end-to-end; its only gap was the enum `writeln` now closed.
**Two LEARNINGS (apply every session):** (A) **M4 "Error 5 / Undefined function" can be a STALE `out/libscrip_rt.so`, NOT an emitter bug.** M2/M3 use the in-process runtime compiled into `scrip`; M4 links the external `.so`. After ANY runtime (`by_name_dispatch.c`/`rt/`) edit you MUST `make libscrip_rt` — rebuilding only `scrip` leaves M4 on the old runtime. (`rt_call_arr` already falls through to `try_call_builtin_by_name`, so new `__pas_*` builtins need no emitter work.) (B) **`.ref` files follow SCRIP's width-10 integer convention, NOT fpc's unpadded integers.** Generate refs with integer output from M2 (value-cross-checked against fpc); taking integer output straight from fpc false-fails the gate. String-only output (enum names) is safe to take from fpc directly.
**Known gap (noted, not a regression):** bare `writeln(enumVar)` (a plain enum-typed variable, not indexed/field) still prints the ordinal — marking covers indexed/field access only, which is what pcom uses. To generalize: track enum-typed scalar VARs and mark `TT_VAR` reads the same way.

**Prior session (55) (SCRIP parser + runtime): two pcom-porting fixes; gate watermark UNCHANGED at 112/0 ×3 (pcom/pint not gated). Commit b0a54e9. pcom.pas advanced PAST the `kind=9` deref-field-index abort (Session 54's NEXT BLOCKER) to a new null-sval nested-aggregate-store abort — see NEXT BLOCKER below.**
(1) **`ptr^.field[i] := val` deref-field-index store into a packed-char-array field** (pcom `lvp^.rval[i] := '+'`). LHS lowered to nested `TT_IDX(TT_IDX(__pas_deref(ptr),fidx),eidx)`; `lower_assign` TT_IDX path saw a non-TT_VAR base (`bname==NULL`), built a null-sval `IR_ASSIGN` + `arr_set_pure` IR_CALL → aborted in `flat_drive_assign` (`kind=9`); M2 silently no-op'd it. Fix = runtime helper `__pas_field_idx_set(ptr,fidx,eidx,val)` (`by_name_dispatch.c`, right after `__pas_field_set`): read-modify-write of the record's SOH-field as a PACKED CHAR STRING (no SOH → nests cleanly inside the record's SOH fields; `arr_get`'s packed-char path reads it back), auto-grows with spaces. Emitted by a new FIRST branch in `mk_assign` (`pascal.y`) detecting that exact nested shape → 4-arg `TT_FNC`. No emitter/template/alloc changes; the new branch fires ONLY on the shape that previously aborted (112 tests untouched). Additive + Pascal-name-scoped in the shared runtime (other frontends never call that name). Verified M2/M3/M4.
(2) **Record-VARIABLE pointer-field resolution** (pcom `val.valp^.rval[i]`, `fvalu.valp^.rval[i]`). `(rec.ptrfield)^.field` left `.field` unresolved → `TT_FIELD`, because `pas_ptrexpr_target` resolved the deref target via the weaker `pas_selector_rectype` (NULL for a record variable's indexed field). Fix = `pas_ptrexpr_target`'s TT_IDX-ILIT branch now calls the capable `pas_with_sel_rtype` (matches a recvar's fields to its rectype), so `rec.ptrfield` resolves to the pointed-to record type and `.field` to a numeric index, feeding fix (1)'s clean shape. One-line change + a forward decl. Verified M2/M3/M4 112/0.
**ATTEMPTED + REVERTED this session — do NOT naively re-apply:** nested-record-field type resolution (`fldrec[]` per-field record-type tracking + `recordvar.field.subfield` selector resolution). Passed all gates only after fixing an array-of-record regression (first cut front-ran the arrrec-flattening branch — the `_anf>0` arrrec path at `pascal.y` selector.field MUST keep priority), but yielded NO net pcom progress: it resolves only TT_VAR-base nested fields, while pcom's failing sites have deref/deeper bases (`fconst^.values.ival`) the resolution never reaches, AND where the name does resolve it merely shifts the abort to the unhandled nested record-in-record store (`gattr.cval.ival` → `kind=9`). Reverted to a minimal verified unit. The fldrec idea is sound but belongs INSIDE the full nested-aggregate-store feature (NEXT BLOCKER), not as a standalone half-step.

**Session 54 (2026-06-13) landed (SCRIP emitter + lower + parser): three pcom-porting fixes; pcom passed three previously-fatal emit-time aborts.**
(1) **Frame-var as RHS of a global assign** (`g := nested_proc_local`): `IR_ASSIGN` whose `operands[0]` is `IR_VAR_FRAME`/`IR_VAR_FRAME_REF` was unhandled at all three dispatch layers and aborted in `flat_drive_assign` (`kind=172`). Fix = 3 coordinated edits: add `IR_VAR_FRAME`/`_REF` to the layer-1 flat dispatch (`emit_bb.c` ~2917) and layer-2 `walk_bb_node` dispatch (`emit_core.c` ~451) so both route to `flat_drive_gvar_assign`/`bb_gvar_assign`, plus a new `IR_VAR_FRAME`/`_REF` arm in `bb_gvar_assign.cpp` that loads the materialized 16-byte descriptor from `FRQ(op_a_slot)`/`FRQ(op_a_slot+8)` and calls `rt_gvar_assign_descr` (same shape as the IR_CALL arm). Template-only, language-blind. Verified M3+M4.
(2) **Recovered prior-session `g_pas_recbody_depth` field-resolution fix that was never compiled in.** `pascal.y` had the depth-guard (only call `pas_rectype_to_pend` when `g_pas_recbody_depth==0`, so a record-typed field inside a variant — e.g. `konst: (values: valu)` in `identifier` — does not clobber the enclosing record's pend list), but `rm -f scrip` leaves `pascal.tab.o` stale, so the fix wasn't in the binary. A `bison -d -o pascal.tab.c pascal.y` regen forced recompilation; `identifier.name` now resolves (`fi=0`). Re-validated all three gates 112/0 with the corrected parser. **LESSON: after editing `pascal.y` you MUST `bison` regen, and the rebuild must recompile `pascal.tab.o` — `rm -f scrip` alone is insufficient (it leaves the stale object).**
(3) **Unary minus in a value position.** `lower_unop` (unlike `lower_binop`) set no aux operands, so `-X` as an arg to `arr_set_pure`/`arr_get` either hit a missing-operand abort or produced an 8-byte raw int with no DT_I tag → corrupt 16-byte descriptor read by the marshaller (BINOP arith args carry the tag; UNOP did not). Fix: lower `-X` as the binary `0 - X` (`lower_pascal.c` `lower_unop`, TT_MNS only; TT_PLS/TT_NOT/TT_SIZE keep IR_UNOP), reusing the proven tag-carrying BINOP arith path. Min repros `arr[1] := -arr[1]`, `v.x := -v.x` → match M2. Gates 112/0 ×3.
(4) **Fixed a Pascal nested-proc emission regression from upstream `f9e6c02`** (SNOBOL4 DEFINE "abolish per-proc VIEW sub-graphs"). That commit routed the **Pascal** proc-emit loop (`scrip.c`) through new `gvar_flat_chain_build_at`/`_text_at` wrappers passing `proc_table[].sno_entry_idx`, which `sm_prog.c` defaults to **-1** for non-SNOBOL4 procs (intent: "resolve to `g->entry`"). But the wrappers `return NULL/1` (emit nothing) when `entry_idx < 0` — so **every Pascal proc body emitted nothing → empty output**, dropping 39 frame/nesting/param tests (M3 112→73). The fallback was in `bb_proc_entry()` but missing from the build wrappers. **Fix (`emit_bb.c`):** wrappers use `g->all[entry_idx]` only when in range, else keep `g->entry`. SNOBOL4 (`entry_idx≥0`) unchanged; verified SNOBOL4 DEFINE `DOUBLE(21)=42` M3==M4. Bisected cleanly (a06554a 112/0 → f9e6c02 73/39). **NOTE for all sessions: f9e6c02 ran SNOBOL/Icon/Prolog gates but NOT the 112-test Pascal gate — RUN ALL FOUR LANGUAGE GATES before pushing shared `emit_bb.c`/`emit_core.c`/`scrip_ir.c`/`scrip.c` changes.**

**pcom.pas NEXT BLOCKER (where to resume):** `flat_drive_assign: lhs must be IR_VAR (got kind=172 = IR_VAR_FRAME)` — a null-sval `IR_ASSIGN` whose operand[0] is `IR_VAR_FRAME` (a proc-local read used as RHS). DISTINCT from Session 54 fix (1), which handled the *global-target* `g := framelocal` (sval SET, routes to gvar_assign); here sval is NULL so it falls to `flat_drive_assign`. A DBGV2 probe in `lower_assign` (print LHS when `vname==NULL`) isolated 5 sites of shape `TT_FIELD(TT_IDX(...), TT_VAR("ival"|"valp"))` — nested-aggregate stores `recordvar.field.subfield := framelocal` and `ptr^.field.subfield := …` (e.g. `gattr.cval.valp := lvp` pcom:2889; `values.ival := …`). A complete fix needs TWO coordinated pieces done together: **(A) general field-name resolution for arbitrarily-nested bases** (not just TT_VAR): add `fldrec[PAS_FIELD_MAX]` per-field record-type tracking to `g_pas_rectypes` (+ pend array `g_pas_pend_fldrec` + `g_pas_pend_rectarget`, set in the type-IDENT rule when the field's type names a rectype `pas_rectype_nf>0`, copied in `pas_rectype_add` and `pas_rectype_to_pend`); add `pas_rectype_field_rectype_by_index`; have `pas_with_sel_rtype`'s TT_IDX-ILIT branch try fldrec (then ptrto); and let the selector.field rule resolve via `pas_with_sel_rtype` for ANY unresolved TT_IDX/deref base — but ONLY in the `_anf<=0` (non-arrrec) else, so array-of-record flattening keeps priority (THIS is the regression that bit Session 55's reverted attempt; arrrec1/arrrec2 → 110/2). **(B) nested-aggregate store lowering:** once names resolve, `outer.inner.field := val` is `TT_IDX(TT_IDX(base,i),j)` with a non-TT_VAR/non-deref base, which `lower_assign` (`lower_pascal.c` ~214) still turns into a null-sval assign → abort (kind=9 if RHS is a CALL/idx, kind=172 if RHS is a frame local). Needs an in-place nested-store helper analogous to `__pas_field_idx_set` but for a record-FIELD container rather than a heap deref. Min repro pattern: `gattr.cval.ival := N` (record-in-record) and `fconst^.values.ival := N` (deref-then-nested-field). **Also still pending: empty-procedure-call runtime bug** — calling a `begin end` proc breaks M3 chain continuation; pcom's `mark`/`release` (~line 300) are empty, matters once compile-time aborts clear. **Separate pre-existing bug:** `--dump-ast` SEGFAULTS on pcom (deep recursion in the AST printer), independent of `--run`.

**GATE STATUS (Session 61, 2026-06-15):**
- M3 (--run):    **PASS=123 FAIL=0 XFAIL=1** ✓ — must not regress
- M4 (--compile): **PASS=123 FAIL=0 SKIP=0 XFAIL=1** ✓ (proper gate: `scrip --compile` → `gcc -c` → link `out/libscrip_rt.so` (`-no-pie -lscrip_rt -lgc -lm -Wl,-rpath`) → run → cmp .ref)
- **NOTE: the M2 (`--interp`) gate is OBSOLETE** — a concurrent DE-INTERP push deleted `--interp` from the driver. The Pascal gate is M3/M4 ONLY. The Icon/Prolog *crosscheck scripts* still diff against `--interp` and report spurious failures (stale-harness artifact, NOT a regression); verify those two via direct `--run` until those scripts are de-interp'd.

**(RESOLVED) The Session-60 `2fa5086` regression (M3 122→119) was fixed in the prior 2026-06-15 patch-table handoff via the `emit_core.c` gvar-assign guard admitting stamped call-kinds; gate restored to 122/0 then, now 123/0.**

**M4 GATE NOTE:** `--compile` emits GAS `.intel_syntax noprefix` text — assemble+link+run before comparing to .ref. Do NOT compare the raw asm text to .ref (false-fail), and do NOT trust a watermark "M4 N/0" that wasn't produced by an assemble+link+run gate. The `/tmp/run_gate_m4.sh` recreated each session uses the link-and-run recipe above.

**Still open (next-session candidates):**
1. **var-param of a heap-aggregate field — THE LIVE pcom FRONTIER (Session 61).** `genlabel(uprcptr^.pfname)` (pcom l.3787/3793, callee `genlabel(var nxtlab)`) bombs `marshal_varparam_addr: var-param arg is not a variable` because the byref arg lowers to `arr_get(__pas_deref(ptr), idx)` (no addressable cell). **Fix is a PURE AST/LOWERING rewrite, zero emitter risk** — `genlabel(p^.fld)` → `tmp := p^.fld; genlabel(tmp); p^.fld := tmp`. POC PROVEN M3+M4 (manual rewrite prints `42`/`99` correctly). Concrete 5-step plan + gated probe `vpfld.pas` + the stale-binary LESSON in **HANDOFF-2026-06-15-PASCAL-BB-DYNAMIC-SLOTMAP-AND-VARPARAM-AGGREGATE-FRONTIER.md**. Byref mask available at lower time via `g_stage2.proc_table[pi].byref_mask`.
2. **Generalize enum `writeln` to bare enum variables** — currently only indexed/field enum reads print the name (`writeln(enumVar)` still prints the ordinal). Track enum-typed scalar VARs; mark `TT_VAR` reads like the indexed/field paths. Low priority (pcom uses indexed/field).

**Prior session (53): all three Pascal gates 106→112 (+6). Native-mode `if`-without-`else`-in-proc fix — a false `if`-without-`else` fell through to the proc FAIL port (`proc_ω`), spuriously failing the caller's stmt sequence so later stmts silently never ran. Root cause: `snoch` gvar flat-chain driver (`emit_bb.c` `codegen_gvar_flat_chain_body` ~3517) had γ→`IR_SUCCEED`→success but lacked the symmetric ω rule. One-line fix `else if (w && w->op == IR_SUCCEED) node_ω = &lbl_γ;`. Language-blind: also SNOBOL4 M3 162→168 / M4 152→158. Two sibling drivers (`xargsub` ~1846, `xchain` ~3061) share the shape, left untouched.**

**Prior session (52): M4 72→106 — `rt_proc_register` ABI fix (4-reg→3-arg SysV), landed upstream as `e089608` (this session's duplicate deduplicated by rebase).**



## ▶ GATE SCRIPTS (recreate in /tmp on each session)

```bash
cat > /tmp/run_gate.sh << 'EOF'
#!/bin/bash
cd /home/claude/corpus/programs/pascal
PASS=0; FAIL=0; XFAIL=0; FAILS=""
for f in *.pas; do
    case "$f" in pcom.pas|pint.pas|ppp.pas) continue ;; esac
    base="${f%.pas}"
    [[ "$f" == "recursion.pas" ]] && { XFAIL=$((XFAIL+1)); continue; }
    [[ ! -f "${base}.ref" ]] && { echo "SKIP (no ref): $f"; continue; }
    inp=/dev/null; [[ -f "${base}.in" ]] && inp="${base}.in"
    expected=$(cat "${base}.ref")
    got=$(timeout 6s /home/claude/SCRIP/scrip --interp "$f" < "$inp" 2>/dev/null)
    if [[ "$expected" == "$got" ]]; then PASS=$((PASS+1))
    else FAIL=$((FAIL+1)); FAILS="$FAILS $f"; fi
done
echo "PASS=$PASS FAIL=$FAIL XFAIL=$XFAIL"
[[ -n "$FAILS" ]] && echo "FAILING:$FAILS"
EOF
chmod +x /tmp/run_gate.sh

cat > /tmp/run_gate_m3.sh << 'EOF'
#!/bin/bash
cd /home/claude/corpus/programs/pascal
PASS=0; FAIL=0; XFAIL=0; FAILS=""
for f in *.pas; do
    case "$f" in pcom.pas|pint.pas|ppp.pas) continue ;; esac
    base="${f%.pas}"
    [[ "$f" == "recursion.pas" ]] && { XFAIL=$((XFAIL+1)); continue; }
    [[ ! -f "${base}.ref" ]] && continue
    inp=/dev/null; [[ -f "${base}.in" ]] && inp="${base}.in"
    expected=$(cat "${base}.ref")
    got=$(timeout 6s /home/claude/SCRIP/scrip --run "$f" < "$inp" 2>/dev/null)
    if [[ "$expected" == "$got" ]]; then PASS=$((PASS+1))
    else FAIL=$((FAIL+1)); FAILS="$FAILS $f"; fi
done
echo "PASS=$PASS FAIL=$FAIL XFAIL=$XFAIL"
[[ -n "$FAILS" ]] && echo "FAILING:$FAILS"
EOF
chmod +x /tmp/run_gate_m3.sh

cat > /tmp/run_gate_m4.sh << 'EOF'
#!/bin/bash
cd /home/claude/corpus/programs/pascal
RT_DIR=/home/claude/SCRIP/out
SCRIP=/home/claude/SCRIP/scrip
PASS=0; FAIL=0; SKIP=0; XFAIL=0; FAILS=""
for f in *.pas; do
    case "$f" in pcom.pas|pint.pas|ppp.pas) continue ;; esac
    base="${f%.pas}"
    [[ "$f" == "recursion.pas" ]] && { XFAIL=$((XFAIL+1)); continue; }
    [[ ! -f "${base}.ref" ]] && continue
    inp=/dev/null; [[ -f "${base}.in" ]] && inp="${base}.in"
    expected=$(cat "${base}.ref")
    tmp=$(mktemp -d)
    if ! "$SCRIP" --compile "$f" > "$tmp/p.s" 2>/dev/null; then SKIP=$((SKIP+1)); rm -rf "$tmp"; continue; fi
    if ! gcc -c "$tmp/p.s" -o "$tmp/p.o" 2>/dev/null; then SKIP=$((SKIP+1)); rm -rf "$tmp"; continue; fi
    if ! gcc -no-pie "$tmp/p.o" -L"$RT_DIR" -lscrip_rt -lgc -lm -Wl,-rpath,"$RT_DIR" -o "$tmp/p.bin" 2>/dev/null; then SKIP=$((SKIP+1)); rm -rf "$tmp"; continue; fi
    got=$(timeout 6s "$tmp/p.bin" < "$inp" 2>/dev/null)
    if [[ "$expected" == "$got" ]]; then PASS=$((PASS+1))
    else FAIL=$((FAIL+1)); FAILS="$FAILS $f"; fi
    rm -rf "$tmp"
done
echo "PASS=$PASS FAIL=$FAIL SKIP=$SKIP XFAIL=$XFAIL"
[[ -n "$FAILS" ]] && echo "FAILING:$FAILS"
EOF
chmod +x /tmp/run_gate_m4.sh
```

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x scrip ] || { grep "error:" /tmp/build_full.log | head -5; exit 1; }
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash /tmp/run_gate.sh    # must be 122/0
bash /tmp/run_gate_m3.sh # must be 122/0
bash /tmp/run_gate_m4.sh # must be 122/0 (assemble+link+run; -no-pie). NEVER trust an M4 watermark not produced by this recipe.
```

---

## Mechanism inventory

- **Rail:** `LANG_PASCAL`=6, `IR_LANG_PAS`=7, body walker `lower_pascal_body`. Mode-2 = `!is_icon && !is_prolog` → `IR_interp_once`.
- **Frame-as-BB:** `[fb+0]`=SL, `[fb+16+k*16]`=DESCR slot k. VAR params = cell addresses (IR_VAR_FRAME_REF/IR_ASSIGN_FRAME_REF). Migration: `decl_level>1 || byref_mask`; main stays NV.
- **2D array indexing:** parser grammar rule `selector '[' expression_list ']'` for 2-element lists: creates flat index `BINOP_ADD(BINOP_MUL(i, ncols), j)` and `TT_IDX(a, flat_expr)` (2 children). Both operands of each BINOP point to the BINOP as their γ (non-linear chain). PEERS aux (`bb_operand_aux_set` in lower_binop) correctly records both operands — the ONLY place to get them. `walk_bb_flat case IR_BINOP:` wires PEERS aux → direct children when `bb_child0==NULL` using `g_emit_cfg` (saved/restored to the arg's subgraph before `flat_emit_arg_subchain`). `lc_arg_block` creates **isolated subgraphs** (separate `IR_graph_t*` from main); PEERS aux keyed to that subgraph, not main graph.
- **Calls:** dval=2.0 → `bb_call_byname_str` → `rt_call_arr`; dval=3.0 registered → `bb_call_gvar_userproc_str` → `rt_call_named_proc(_sl)`. `gvar_drive_call_arg_slots`: pre-evaluates all non-null arg entries. Terminal: `walk_bb_flat + bb_slot_get`. Non-terminal ending in CALL: `flat_emit_arg_subchain + bb_slot_get(res_last)` with `g_emit_cfg` set to arg subgraph. Non-terminal ending in arith BINOP: SKIP (leave slots[i]=-1; `marshal_call_arg` inline-arith handles correctly). `marshal_call_arg` dispatch (gvar): (1) `op_arg_slot[i]≥0` → pre-computed DESCR slot; (2) gvar inline-arith (`fin!=lf && arith_binop`) → compute + wrap DT_I; (3) gvar relop; (4) `bb_slot_get(lf)≥0` → nested slot; (5) `marshal_single_call` for terminal CALL; (6) LIT_I/S/F/NUL; (7) `bb_varslot` (BAD fallback). **Known issue**: `marshal_single_call` (called from step 5 OR from inline-arith when operand is a CALL) calls `bb_slot_alloc16(subs[j]->entry)` for argbase without going through gvar_drive_call_arg_slots → fresh empty slots → zeros.
- **Booleans:** INTVAL(1/0). `pas_cond` = `expr≠0`; and/or = TT_MUL/TT_ADD; not = `pas_flip_rel`. Relop→VAR: parser IF rewrite; other → `pas_bool` diamond. **Polymorphic relop, all six (< <= > >= = <>), char-array/string-aware:** the `IR_BINOP_GVAR_RELOP` descriptor arm in `bb_binop_gvar_relop.cpp` reconstructs both 16-byte DESCRs and calls `rt_relop_descr2`→`binop_apply` (M2's SOH-normalized string memcmp; DT_I falls through to integer cmp; the arm body passes `op_ival` straight through, so one arm serves all six relops). Operand sources: IR_CALL from slot [op_sa]/[op_sa+8]; named IR_VAR via `rt_gvar_get_descr`; IR_LIT_S built inline as DT_S (lo=DT_S/slen0, hi=`lea [rip+sealed]`, sealed via `bb_intern_into`). `emit_bb.c` sets `g_emit.op_relop_descr` when op∈[LT..NE] AND both operands ∈ {CALL, named-VAR, LIT_S} AND (string-type hint `IR_LIT(nd).dval==1.0` OR a LIT_S operand present OR EQ/NE-with-≥1-CALL). The **string-type hint** is set by the parser (`pas_rel`/`pas_is_strtyped` flag a relop AST node `v.ival=1` when both operands are string-typed: whole char-array VARs, string literals, OR — added Session 56 — `TT_IDX(TT_VAR v,…)` where `pas_is_chararr(v)`, i.e. indexed char-array exprs) and carried `lower_binop` → `IR_LIT(op).dval=1.0`. Integer VAR-vs-VAR and VAR-vs-LIT_I keep the inline integer fast path. **CALL-vs-CALL ordering** (`rw[i] < rw[j]` on an array-of-char-arrays) is CLOSED (Session 56, probe `chararrcvc`): the indexed-char-array hint routes it to the descriptor arm for all six relops; flat char-array elements (`s[i] < s[j]`) stay correct via the arm's DT_I fallback (single-char lexical == ordinal).
- **goto/label:** pass-1 pre-registers IR_SUCCEED landings; intra-proc only.
- **I/O:** `__pas_writeln/__pas_write` interleaved (value,width). Default int=10, real=20, char=-2.
- **Char:** ordinals. charvar args wrapped `mk_chr_wrap → TT_FNC(__pas_chr, val)`.
- **Arrays/records/pointers:** TT_IDX → `arr_get`; `a[i]:=v` → `arr_set_pure`. Records = field-index arrays. Sets = `__pas_set*/in`.
- **Functions:** body ends `IR_RETURN(dval 0)` reading `IR_VAR(funcname)`.

## Target dialect — P4 subset
`pcom.pas` + `grammar/pascalp.y`. integer=16-bit; array, record, set(0..58), pointer; value+var params; nested routines; goto intra-proc only. If pcom rejects a probe, out of scope.

## ⚖ Provenance
`pcom.pas`/`pint.pas` = behavioral oracle only — never transliterated.

## Invariants
No AST walking in modes 2/3/4. Zero C Byrd-box functions. Four ports (α β γ ω). Modes 3/4 emit no byte outside `bb_emit_x86`.

## Where things live
| Thing | Path |
|-------|------|
| Oracle | `corpus/programs/pascal/pcom.pas` / `pint.pas` |
| Grammar | `corpus/programs/pascal/grammar/pascalp.{l,y}` |
| Probes | `corpus/programs/pascal/*.pas` |
| Frontend | `src/parser/pascal/pascal.{l,y}` |
| Lowering | `src/lower/lower_pascal.c` + `lower_program.c` |
| Mode-2 interp | `src/interp/IR_interp.c` |
| BB templates | `src/emitter/BB_templates/` |

Start every Pascal session reading the reference grammar for constructs in play.

## ⚠ Landmines
1. `rm -f scrip` before `make scrip` — no prerequisites.
2. Pascal regen ONLY: `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`. NEVER full regen.
3. `touch` templates before `make scrip` after any template edit.
4. fpc: `apt-get update` first.
5. Every `git pull --rebase` → `rm -f scrip && make` → full gate re-run.
6. TEXT internal labels on gvar flat chain: shared `_.x86_uid`; key by `bb_node_id`.
7. `lc_arg_block` creates ISOLATED subgraphs (separate `IR_graph_t*`). PEERS aux is keyed to that graph. Save/restore `g_emit_cfg` around `flat_emit_arg_subchain` to use the correct graph for aux lookup.
