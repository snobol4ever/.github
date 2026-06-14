# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 57, 2026-06-14)

**Landed this session (SCRIP parser ONLY — zero runtime/emitter/template/lower/interp/machine files touched): Part (A) of the pcom NEXT BLOCKER — general nested-record-field NAME RESOLUTION. Gates UNCHANGED at 115/0 ×3 (verified M2/M3/M4 clean build). Part A is regression-safe but yields NO net pcom progress on its own (the nested STORES still silently drop — see findings below); committed anyway because the name-resolution machinery is the prerequisite for Part B and is independently correct. The next session does Part B + a third piece I discovered, then this is done.**

**WHAT LANDED (Part A — nested field-name resolution, exactly the GOAL's documented piece A):** Added `fldrec[PAS_FIELD_MAX]` per-field record-type tracking to `g_pas_rectypes` (parallel to the existing `fldptrto[]`/`fldenum[]` channels). Pieces: (i) pend array `g_pas_pend_fldrec[]`; (ii) `pas_pend_add` captures it — `fldrec[k] = (g_pas_pend_typename && pas_rectype_nf(typename)>0) ? typename : NULL` (uses the fwd-decl of `pas_rectype_nf` at line 59); (iii) copied in `pas_rectype_add` AND `pas_rectype_to_pend`; (iv) accessor `pas_rectype_field_rectype_by_index`; (v) `pas_with_sel_rtype`'s `TT_IDX(base, ILIT)` branch now tries `fldrec` FIRST (field is itself a record), then falls back to `ptrto`; (vi) new helper `pas_nested_field_resolve(base, fld)` = resolve `pas_with_sel_rtype(base)` then `pas_rectype_field_index`, building `TT_IDX(base, ilit(idx))` (+ enum mark) or `TT_FIELD` fallback; (vii) wired into BOTH non-arrrec `TT_FIELD` fallbacks in the `selector PERIOD IDENT` rule — the arrrec-flattening branch keeps priority (the `_anf>0` path is untouched, so arrrec1/arrrec2 don't regress). VERIFIED: `gattr.cval.ival` → `TT_IDX(TT_IDX(gattr,1),0)`, `p^.values.ival` → `TT_IDX(TT_IDX(__pas_deref(p),1),0)`. Reads of nested fields now resolve; stores do not yet write back (Part B). Parser regen done (`bison -d -o pascal.tab.c pascal.y`); `pascal.tab.{c,h}` committed.

**THREE FINDINGS THAT RESHAPE PART B (read before resuming):**
- **(F1) The flat single-SOH record model genuinely CANNOT nest records.** A record-typed field occupies ONE slot; the whole-record init (`mk_array_fill`) gives it a single `"0"`. Writing a multi-field sub-record (`"5\x017"`) into that slot makes the parent `"…\x015\x017\x01…"` — the parent's SOH-segment COUNT breaks, so `arr_get(parent, sibling_idx)` reads the wrong segment and corrupts siblings. Confirmed empirically (`o.x`/`o.y` work while `o.c` is untouched `"0"`; both break the instant a 2-field sub-record is stored into `o.c`). So Part B is NOT just lowering — it needs a storage scheme for the nested slot.
- **(F2) Part A EXPOSES a latent `mk_assign` mismatch (invisible to the 115 gate, lives only in pcom).** A nested-record subfield now has shape `TT_IDX(TT_IDX(__pas_deref(ptr), fi), ei)` with BOTH indices ILIT — which collides with `mk_assign`'s FIRST branch (line ~338), built for **packed-char-array deref-fields** (`ptr^.rval[i] := c`, where the INNER index is a 1-based runtime char position). That branch emits `__pas_field_idx_set(ptr, fi, ei, val)`; with `ei=0` (a 0-based record subfield index) the runtime helper early-returns (`eidx<1`) → SILENT DROP. This is exactly why `with lcp^ do values.ival := 5` then `lcp^.values.ival` reads back 0. **Part B MUST disambiguate** nested-record access from char-array indexing before `mk_assign`/`lower` act — they are shape-identical otherwise. The single `tree_t` union `v` is already consumed by the enum-name mark on these nodes, so a second mark needs care (consider a wrapper node or a distinct TT_ kind for nested-record index, or thread a side-table keyed by node pointer).
- **(F3) A viable Part-B storage design exists and is non-invasive.** Dedicated `__pas_nrec_get(container, fi, ei)` / `__pas_nrec_set(container, fi, ei, val)` runtime helpers that store the nested sub-record in the parent slot using a SEPARATOR DISTINCT FROM SOH so the parent still sees one segment. `\x02`(STX) is used by the table/KV runtime paths (lines ~1749–1935) but NEVER by record/array slots, so it's almost certainly safe; to be 100% isolated, pick a control char unused anywhere in `by_name_dispatch.c` (\x05/\x06/\x1e/\x1f are unused — `grep` them). `arr_get`/`arr_set_pure` and all other languages stay UNTOUCHED (the nested slot is opaque to them; whole-record copy `min := values` is a verbatim opaque string copy and stays correct). Only the marked nested-field reads/writes route through `__pas_nrec_*`. The nested slot's init must grow from `"0"` to the right sub-width on first write (auto-grow like `__pas_field_idx_set` does).

**PART B — THE PLAN FOR NEXT SESSION (do all of this together; a half-step regresses or no-ops):**
1. **Mark** the nested-record `TT_IDX` from `pas_nested_field_resolve` distinctly (per F2). Cleanest: a dedicated marker that `mk_assign` and `lower`'s TT_IDX arm both read. Because `v.ival` holds the enum mark, prefer a node-pointer side-table (a small static array of "this TT_IDX is a nested-record index") OR a new lightweight TT_ kind. Do NOT overload `v.ival`.
2. **`mk_assign`:** add a FIRST-priority branch (before the deref-char-field branch) detecting the MARKED nested shape → emit `__pas_nrec_set(container, fi, ei, rhs)` where `container` is the named gvar (`TT_VAR`) OR the deref arg for `ptr^…`. Pass enough to identify the container kind (gvar name vs heap key).
3. **`lower` TT_IDX arm / a read helper:** marked nested read → `__pas_nrec_get(container, fi, ei)` instead of `arr_get(arr_get(…))`.
4. **Runtime `by_name_dispatch.c`:** implement `__pas_nrec_get`/`__pas_nrec_set` (Pascal-name-scoped, additive — other frontends never call them; `rt_call_arr` already falls through to `try_call_builtin_by_name` so NO emitter work). RMW: read parent slot `fi` (whole, via SOH walk), treat its value as a `<SEP>`-separated sub-record, get/set element `ei` (auto-grow), write the sub-record back into parent slot `fi`. **After the runtime edit you MUST `make libscrip_rt`** (Session 56 LEARNING A — M4 links the external `.so`; rebuilding only `scrip` leaves M4 stale).
5. **Min repros (add as gated probes once passing):** `nestrec1` (`g.cval.ival := 42; writeln`), `nest3`/`pcomlike` (`new(p); p^.values.ival := 99` / `with lcp^ do values.ival := 5`), `nestcheck` (`outer{x, c:inner{a,b}, y}` — all four leaves r/w, the SOH-count torture test). They live in `/tmp/*.pas` this session; regenerate. Generate `.ref` from M2 value-cross-checked against fpc (Session 56 LEARNING B — `.ref` uses SCRIP width-10 integers, NOT fpc's unpadded).
6. **Then** the deeper pcom sites (`gattr.cval.ival := lcnt`, `lsp^.max := lvalu`, `min := values`) should store correctly; re-drive pcom past the const-decl point (it currently stops mid-`const lim = 5` because `constant()`'s nested stores drop). Watch for the still-pending **empty-procedure-call runtime bug** (pcom's `mark`/`release` ~line 300) once stores work.

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

**GATE STATUS:**
- M2 (--interp): **PASS=115 FAIL=0 XFAIL=1** ✓ STABLE — must not regress
- M3 (--run):    **PASS=115 FAIL=0 XFAIL=1** ✓ PARITY WITH M2
- M4 (--compile): **PASS=115 FAIL=0 SKIP=0 XFAIL=1** ✓ FULL PARITY — stable across repeated runs (proper gate: `scrip --compile` → `gcc -c` → link `out/libscrip_rt.so` (`-no-pie -lscrip_rt -lgc -lm -Wl,-rpath`) → run → cmp .ref)

**M4 GATE NOTE:** `--compile` emits GAS `.intel_syntax noprefix` text — assemble+link+run before comparing to .ref. Do NOT compare the raw asm text to .ref (false-fail), and do NOT trust a watermark "M4 N/0" that wasn't produced by an assemble+link+run gate. The `/tmp/run_gate_m4.sh` recreated each session uses the link-and-run recipe above.

**Still open (next-session candidates):**
1. **pcom NEXT BLOCKER — nested-aggregate STORE (Part B + the F2 disambiguation).** Part (A) nested field-NAME resolution LANDED this session (Session 57) and is regression-safe at 115/0 — see CURRENT STATE. What remains: Part (B) the in-place nested store, PLUS a third piece (F2) that Part A exposed — nested-record subfield access is now shape-identical to char-array deref-field indexing and silently mis-routes through `__pas_field_idx_set`. Full plan (mark → `mk_assign`/`lower` route to `__pas_nrec_get`/`__pas_nrec_set` → runtime RMW with a non-SOH sub-record separator) is in the CURRENT STATE "PART B — THE PLAN" list. F1 (flat SOH can't nest records natively) and F3 (the non-invasive `\x02`-class separator design) are in CURRENT STATE "THREE FINDINGS". Do Part B + F2 TOGETHER; min repros listed. Deserves a fresh context budget. Sites: `gattr.cval.valp := lvp` pcom:2889, `values.ival := lcnt` pcom:1051, `lsp^.max := lvalu`, `min := values`.
2. **Generalize enum `writeln` to bare enum variables** — currently only indexed/field enum reads print the name (`writeln(enumVar)` still prints the ordinal). Track enum-typed scalar VARs; mark `TT_VAR` reads like the indexed/field paths. Low priority (pcom uses indexed/field).
3. **Empty-procedure-call runtime bug** — calling a `begin end` proc breaks M3 chain continuation (pcom's `mark`/`release` ~line 300 are empty); matters once compile-time aborts clear.

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
bash /tmp/run_gate.sh    # must be 106/0
bash /tmp/run_gate_m3.sh # must be 106/0
bash /tmp/run_gate_m4.sh # must be 106/0 (assemble+link+run; -no-pie). NEVER trust an M4 watermark not produced by this recipe.
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
