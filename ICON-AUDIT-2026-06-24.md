# Icon Construct Audit vs JCON — 2026-06-24 (Claude)

Scrutiny of every major Icon construct implemented to date against the canonical
JCON `irgen.icn` port-topology and the Icon `*.r` runtime, plus a BB-discipline
review and the global-variable storage question.

Method: read `refs/jcon-master/tran/irgen.icn` (the `ir_a_*` chunk emitters),
`refs/icon-master/src/runtime/{fscan,fstranl,oasgn,ovalue}.r`, and every Icon
lowerer arm (`src/lower/lower_icon.c`) + its BB template, then verified behavior
empirically at HEAD (suite 147/283, smoke 12/12 both modes).

---

## A. BB-DISCIPLINE REVIEW — all green

| Rule | Result |
|------|--------|
| No value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`) in any Icon template | ✅ none — `test_gate_icn_no_stack` = 0 |
| All RW state in the one-register ζ-frame `[r12+off]` | ✅ `bb_alt`/`bb_to` use `FRQ(off)`; gate `icn_one_reg_frame` = 0 |
| No C byrd-box `(void*ζ, int entry)` functions | ✅ grep = 0 |
| Four ports = α/β/γ/ω, jumps not calls | ✅ every box ends `def β; jmp …` |
| RO operand constants IP-relative `[rip+disp]` | ✅ `ROQ`/`LS` sealed adjacency in `bb_alt`, `bb_var_global` |
| Semicolon-required, no newline processing | ✅ prison green (3 locks) |

The architecture is faithful: in JCON every construct is just `ir_Goto` chunk
wiring with a few value ops; SCRIP mirrors this — e.g. `bb_every` is a bare
`jmp ω / def β / jmp ω` (no instructions), exactly as JCON's `ir_a_Every` emits
only `ir_Goto` chunks. The real work lives in `flat_drive_*` port wiring + the
generator producer chain. Correct.

---

## B. CONSTRUCT-BY-CONSTRUCT vs JCON

Legend: ✅ matches canonical · ⚠ works but deviates/partial · ✗ missing/broken.

| Construct | JCON `ir_a_*` | SCRIP IR / box | Status | Notes |
|-----------|---------------|----------------|--------|-------|
| `every` | `ir_a_Every` (309) | `IR_EVERY` / `bb_every` + `flat_drive_every` | ✅ | gen.success→body.start, body.success→gen.resume, body.failure→gen.resume — matches the canonical loop. Generator-arg userproc now resumes correctly (ICN-CALL-GEN-ARG). |
| `|` alternation | `ir_a_Alt` (167) | `IR_ALT` / `bb_alt` | ✅ | per-arm counter in `[ζ+off+16]`, arm value in `[ζ+off]`; β re-dispatches next arm; exhaust→ω. Bounded/unbounded both via the counter. JCON uses MoveLabel/IndirectGoto for the unbounded resume label; SCRIP folds that into the counter — equivalent, simpler. Limit: ≤5 literal arms (`alt_arms_all_simple_lit`); non-literal arms still excise (queens). |
| `to`/`to by` | `ir_a_Binop` op `..`/Sectionop | `IR_TO`/`IR_TO_BY` / `bb_to` | ✅ | from/to operand slots read `[ζ]`; counter slot; real step via `"ar"` tag. `every write(1 to 3)`→1,2,3 verified. |
| `\` limit | `ir_a_Limitation` (113) | `IR_LIMIT` / **no `bb_limit`** | ✗ | `flat_drive_limit` is pure port-wiring — NO counter, NO result pass-through. rung14 ×3 FAIL (rc=124 hang). Canonical needs `t:=#limit; c:=1; expr.resume: if t>c {c++; goto expr.resume} else fail`. **TOP open construct bug.** |
| `if`/`if-else` | `ir_a_If` (577) | `IR_IF` / `flat_drive`(bounded) | ✅ | cond.success→then.start, cond.failure→else.start (else defaults to ω/fail). Bounded-resume label handled. Works as expr and stmt. (if-then-else **as an assignment RHS** still parse/gate-blocked — options.icn.) |
| `while`/`until` | `ir_a_While`/`Until` (1008/981) | `IR_WHILE`/`IR_UNTIL` | ✅ | cond drives body; body.success/failure → cond.start (re-test). `loop_exit`/`loop_next` threaded for break/next. |
| `repeat` | `ir_a_Repeat` (847) | `IR_REPEAT` | ✅ | body.success/failure → body.start (infinite); break exits. |
| `not` | `ir_a_Not` (140) | `IR_NOT` | ✅ | expr.success→failure, expr.failure→success(&null). Matches. |
| `case` | `ir_a_Case` (232) | `IR_CASE`/`IR_CASE_ARM` | ⚠ | structurally present; selector + arms lowered. Not stress-tested vs JCON's tmp-compare chain. Benchmarks don't exercise it deeply yet. |
| `suspend` | `ir_a_Suspend` (937) | `IR_SUSPEND` (subgraph) | ⚠ | lowered as subgraph (`dval=1.0`, expr in `.counter`, body in `.ival`); `icn_body_has_suspend` flags the proc as a generator. rung03 ×3 FAIL — suspend resumption into caller not fully wired. Canonical `ir_Succeed(susp,t)` + scan-swap interplay is subtle. **2nd open construct bug.** |
| `return`/`fail` | `ir_a_Return` (867) | `IR_RETURN`/`IR_FAIL` | ✅ | return value via operand; fail→pfail. `return` bare/with-value both parse now. |
| `?` scan | `ir_a_Scan` (95) | `IR_GEN_SCAN` + `IR_SCAN_*` | ✅ (partial) | subject saved/restored; body retag to `IR_SCAN_TAB/UPTO/...`; cursor Σ/δ/Δ. `s ? write(tab(many(&letters)))`→abc verified. Gaps: `tab(0)` (gate rejects lit 0=end-of-string), builtins-in-scan (`integer`/`put`), nested scan bodies. Subject model matches `fscan.r` (k_subject/k_pos). |
| scan fns `tab/move/pos/any/many/upto/match/find/bal` | `fscan.r`/`fstranl.r` | `bb_scan_*` | ✅ | each box mirrors its `.r` (e.g. `move` saves oldpos, reverses on resume; `upto`/`many` use cset). cset-keyword args (`&letters`) supported. |
| assignment `:=` | `ir_a_Binop` op `:=` | `IR_ASSIGN`/`IR_IDX_SET` | ✅ | var → name slot; subscript → `IR_IDX_SET`. RHS shapes broad ([], call, subscript, concat, unop). Gaps: chained `a:=b:=c`, builtin-as-value `x:=write`. |
| augmented `op:=` | `ir_augmented_assignment` | desugar→ASSIGN(BINOP) | ✅ | rewrites to `x := x op y` at lower time. |
| `:=:` swap / `<-` revassign | `oasgn.r` rasgn/swap | `IR_SWAP`/`IR_RASGN` | ⚠ | `bb_swap`/`bb_rasgn` templates exist; plain-var case wired. Subscript-lvalue `<-` (queens `rows[r]<-1`) and non-var `:=:` (shuffle `!x:=:?x`) NOT done. |
| section `x[i:j]` | `ir_a_Sectionop` (333) | `IR_SECTION` | ⚠ | lowered (3 operands + ±mode); not benchmark-proven; gate still excises in alt-graphs. |
| field `x.f` | `ir_a_Field` (32) | `IR_FIELD_GET` | ✅ | record field read. |
| list `[...]`/`!x` | `ir_a_ListConstructor` (1313) | `IR_MAKELIST`/`IR_LIST_BANG` | ✅ | `MAKELIST` → DT_DATA list(frame_elems,frame_size,gen_type); `!x` generates elements. `*L` size now reads `frame_size` (ICN-SIZE fix). |
| `create`/coexpr | `ir_a_Create` (1035) | — | ✗ | not implemented (micro.icn parse-fails on `create`). Lower scope — coexpressions are a big feature. |
| `initial` | `ir_a_Initial` (624) | `IR_INITIAL` / `bb_initial`(dead) | ✗ | needs a persistent-writable-static facility (see §D). Currently EXCISES. |
| `static` decl | (runtime) | `TT_STATIC_DECL`→`IR_SUCCEED` no-op | ✗ | same missing facility as `initial`; static gets no persistent slot. |

### Runtime-method spot-checks
- Arithmetic/relops route through the shared `binop_apply` (rt_runtime.c) — one
  implementation for all languages. ✅ (not re-implemented per-language in templates).
- List `put`/`push`/`get` maintain `frame_size` as the live count; `*L` reads it.
  ✅ (ICN-SIZE fix this session; was reading record `nfields`=3).
- Scan subject/cursor uses the Σ/δ/Δ register trio per the locked convention. ✅

---

## C. GLOBAL VARIABLES — ICON STILL USES THE HASH ARENA, NOT THE DATA-SECTION ARRAY

**This is the concrete migration Lon asked for.** Status: NOT done for Icon.

### How SNOBOL4 does it now (PERF-GVA, `ef7594d` / `9222a33`)
- Driver emits a `.bss` array `__gva: .space n*16` (one 16-byte DESCR cell per
  global) + a `.rodata __gva_names` table.
- At startup: `gva_register(__gva_names, __gva, n)` binds each name to its `.bss`
  cell and returns the base → `mov rbx, rax`. **`rbx` = the `__gva` array base.**
- Read/write a global = `[rbx + k*16]` (k = compile-time index from
  `gva_index_of`). NO hash lookup, NO `NV_GET_fn` call.
- Gated by `g_gva_active`, set ONLY in the SNOBOL4 `gvar_flat_chain_build_text` path.

### How Icon does it today (the gap)
- Icon globals lower to plain `IR_VAR`/`IR_ASSIGN` and emit through the **descr**
  flat-chain path (`descr_flat_chain_build`), whose `bb_var_global` template does
  `mov rdi, &name; call NV_GET_fn` — the **name-table HASH in the memory arena**
  (the `rbp`/`NV_*` side channel).
- `g_gva_active` is never set for Icon; `gva_register`/`__gva`/`mov rbx,rax` are
  never emitted on the Icon path. `rbx` is **free** in the Icon m4 `main:`
  (it does `push rbp; …; call main_α` and never touches rbx) — so the SNOBOL4
  mechanism is directly reusable.
- Result: `counter := counter + 1` across procs (rung25) WORKS but pays a hash
  lookup per access instead of a single `[rbx+k*16]` move.

### Migration plan (GVA-for-Icon) — reuse the existing facility, do NOT rebuild it
1. **Scope the names.** SNOBOL4 has flat scope, so "any non-excluded name" is a
   global. Icon does NOT — only names in `global` decls (and proc names) are true
   globals; an undeclared proc var defaults to LOCAL. So Icon must seed the GVA
   set from the `TT_GLOBAL` declaration list ONLY (collect at parse/lower), not
   from every `IR_VAR`. (Feeding every IR_VAR to `gva_collect_var` would wrongly
   promote locals.) This is the one real design difference from SNOBOL4.
2. **Emit the array on the Icon path.** In the descr m4 `main:` block
   (scrip.c ~2736) and the m3 descr build, mirror scrip.c:2922-2941: collect the
   Icon global names, emit `.bss __gva` + `.rodata __gva_names`, `gva_register`,
   `mov rbx, rax`, set `g_gva_active=1` around the descr chain build.
3. **Route the box.** `bb_var` / `bb_var_global` / `bb_assign`: when
   `g_gva_active && gva_index_of(name)>=0`, emit `[rbx+k*16]` load/store instead
   of the `NV_GET_fn` call. The SNOBOL4 templates `bb_gvar_assign.cpp` already
   show the exact `RDQ("rbx", k*16)` form — Icon's `IR_VAR`/`IR_ASSIGN` boxes get
   the same arm under `g_gva_active`.
4. **Keep NV in sync only where needed.** `NV_bind_gva` already lets a name's
   cell live in the array while still being reachable by `NV_GET_fn` for any
   reflective path (image/EVAL). So builtins that look a global up by name still
   work.
5. **Gates.** No-stack/one-reg unaffected (the array is `.bss`, not a stack, and
   reached via rbx not r12). rung21/rung25 stay green; the `.s` shows
   `[rbx+k*16]` instead of `call NV_GET_fn`.

Risk: low — the facility is proven on SNOBOL4 (262-program crosscheck, 14/16
bench). The only Icon-specific work is the name-scoping in step 1.

---

## D. `initial` / `static` — the persistent-writable-static gap (separate prereq)

Confirmed (and matches the 2026-06-23 finding): `initial expr` runs once across
ALL activations, so its done-flag and any `static` var need storage that is
(a) persistent across calls and (b) writable. Today there is none:
- ζ-frame `[r12+off]` is per-activation (resets each call).
- The m3 RX slab is `PROT_READ|PROT_EXEC` (bb_pool.c) — writing sealed RO in the
  code stream SEGFAULTs.
- `static` lowers to `IR_SUCCEED` (no storage); `bb_initial.cpp` is a dead,
  unwired file.

**The GVA `.bss __gva` array is exactly the writable-static region this needs.**
Once GVA-for-Icon lands, `initial`/`static` can allocate a persistent slot in the
same `.bss` arena (one extra cell per `initial` site / `static` var), addressed
`[rbx+k*16]`, and the gate's defensive `IR_INITIAL` excise can finally lift for
the proven shape. So **GVA-for-Icon is the prerequisite that also unblocks
`initial`/`static`** (queens/deal/post/tgrlink/ipxref all need `initial`).

---

## E. RECOMMENDED ORDER (smallest-blast-radius first)

1. **GVA-for-Icon** (this is Lon's explicit ask; also the `initial`/`static`
   prerequisite). Reuse the SNOBOL4 facility; only new work is global-name scoping.
2. **`bb_limit` counter** (rung14 ×3, fully scoped, canonical `ir_a_Limitation`).
3. **`initial`/`static`** on the new `.bss` arena (unblocks 5 benchmarks' gate).
4. **`suspend` resumption** (rung03 ×3) — the trickiest; canonical `ir_Succeed`.
5. Richer alternation (non-literal arms, arm-scoped `alt_safe_kind`) — 6 benchmarks.

Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
