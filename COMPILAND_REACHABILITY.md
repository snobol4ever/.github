# Sprint 20 — Compiland Reachability Analysis
## beautiful.c symbol accounting

*Generated 2026-03-10 by analysis of beauty_run.sno → beautiful.c*

This document lists every symbol reachable from the Sprint 20 compiland
(beauty_run.sno → beautiful.c) and its implementation status.

---

## 1. Pattern constructors  (snobol4_pattern.c)

| Symbol | Uses in beautiful.c | Status |
|--------|-------------------|--------|
| `sno_pat_alt` | 13 | ✅ implemented |
| `sno_pat_any_cs` | 5 | ✅ implemented |
| `sno_pat_arbno` | 3 | ✅ implemented |
| `sno_pat_assign_cond` | 53 | ✅ implemented |
| `sno_pat_assign_imm` | 1 | ✅ implemented |
| `sno_pat_break_` | 10 | ✅ implemented |
| `sno_pat_cat` | 116 | ✅ implemented |
| `sno_pat_epsilon` | 23 | ✅ implemented |
| `sno_pat_len` | 21 | ✅ implemented |
| `sno_pat_lit` | 34 | ✅ implemented |
| `sno_pat_pos` | 56 | ✅ implemented (POS-adjusted for scan offset) |
| `sno_pat_ref` | 13 | ✅ implemented (deferred var lookup) |
| `sno_pat_rpos` | 13 | ✅ implemented |
| `sno_pat_rtab` | 3 | ✅ implemented |
| `sno_pat_span` | 6 | ✅ implemented |
| `sno_pat_user_call` | 10 | ✅ implemented (dispatches via sno_apply) |
| `sno_match_pattern` | 80 | ✅ implemented (unanchored scan) |
| `sno_match_and_replace` | 18 | ✅ implemented |
| `sno_var_as_pattern` | 41 | ✅ implemented |

**Smoke test: smoke_gaps.c Gap 1 — 19/19 PASS**

---

## 2. Runtime API  (snobol4.c)

| Symbol | Uses | Status |
|--------|------|--------|
| `sno_add` | 64 | ✅ |
| `sno_apply` | 623 | ✅ |
| `sno_array_create` | — | ✅ (snobol4_pattern.c) |
| `sno_char_fn` | 382 | ✅ |
| `sno_concat` | 758 | ✅ |
| `sno_data_define` | — | ✅ |
| `sno_datatype` | 12 | ✅ |
| `sno_define_spec` | 84 | ✅ (snobol4_pattern.c) |
| `sno_dupl_fn` | — | ✅ |
| `sno_eq` | — | ✅ |
| `sno_eval` | — | ✅ stub (snobol4_pattern.c) |
| `sno_field_set` | — | ✅ |
| `sno_ge` | — | ✅ |
| `sno_gt` | 24 | ✅ |
| `sno_ident` | — | ✅ |
| `sno_le` | — | ✅ |
| `sno_lpad_fn` | — | ✅ |
| `sno_lt` | 26 | ✅ |
| `sno_make_tree` | — | ✅ (snobol4_pattern.c) |
| `sno_mul` | 110 | ✅ |
| `sno_opsyn` | — | ✅ stub (snobol4_pattern.c) |
| `sno_output_val` | 34 | ✅ |
| `sno_pop_val` | — | ✅ alias (snobol4_pattern.c) |
| `sno_push_val` | — | ✅ alias (snobol4_pattern.c) |
| `sno_top_val` | — | ✅ alias (snobol4_pattern.c) |
| `sno_register_fn` | — | ✅ (snobol4_pattern.c) |
| `sno_replace_fn` | — | ✅ |
| `sno_rpad_fn` | — | ✅ |
| `sno_runtime_init` | 1 | ✅ |
| `sno_size_fn` | 18 | ✅ |
| `sno_sort_fn` | — | ✅ stub (snobol4_pattern.c) |
| `sno_sub` | 47 | ✅ |
| `sno_subscript_get` | 74 | ✅ (snobol4_pattern.c) |
| `sno_subscript_set` | 137 | ✅ (snobol4_pattern.c) |
| `sno_substr_fn` | — | ✅ |
| `sno_table_new` | — | ✅ |
| `sno_to_int` | 95 | ✅ |
| `sno_to_str` | 1772 | ✅ |
| `sno_var_get` | 1387 | ✅ |
| `sno_var_set` | 414 | ✅ |
| `sno_apply_val` | — | ✅ stub (snobol4_pattern.c) |

**Smoke test: smoke_gaps.c Gap 2 + Gap 3 — 21/21 PASS**

---

## 3. Inc-layer C functions  (snobol4_inc.c)

These are called via `sno_apply("Name", ...)` from beautiful.c.
All registered in `sno_inc_init()`.

| Function | Source inc | Uses | Status |
|----------|-----------|------|--------|
| `assign` | assign.inc | — | ✅ registered |
| `DecLevel` | Gen.inc | — | ✅ registered |
| `Gen` | Gen.inc | — | ✅ registered |
| `GenSetCont` | Gen.inc | — | ✅ registered |
| `GenTab` | Gen.inc | — | ✅ registered |
| `GetLevel` | Gen.inc | — | ✅ registered |
| `IncLevel` | Gen.inc | — | ✅ registered |
| `icase` | case.inc | — | ⚠️ MISSING — needs registration |
| `IsSnobol4` | is.inc | — | ⚠️ MISSING — needs registration |
| `lwr` | case.inc | — | ✅ registered |
| `match` | match.inc | — | ✅ registered |
| `Pop` | stack.inc | — | ⚠️ MISSING — needs registration (alias sno_pop_val) |
| `Push` | stack.inc | — | ⚠️ MISSING — needs registration (alias sno_push_val) |
| `Qize` | Qize.inc | — | ✅ registered |
| `SetLevel` | Gen.inc | — | ✅ registered |
| `SqlSQize` | Qize.inc | — | ⚠️ MISSING — needs registration |
| `T8Pos` | trace.inc | — | ✅ registered |
| `TDump` | TDump.inc | — | ✅ registered |
| `TLump` | TDump.inc | — | ⚠️ MISSING — needs stub |
| `TopCounter` | counter.inc | — | ⚠️ MISSING — needs registration |
| `TValue` | TDump.inc | — | ⚠️ MISSING — needs stub |
| `TZ` | omega.inc | — | ✅ registered |
| `upr` | case.inc | — | ✅ registered |
| `Visit` | tree.inc | — | ⚠️ MISSING — needs registration |
| `bVisit` | tree.inc | — | ⚠️ MISSING — needs registration |
| `Equal` | tree.inc | — | ⚠️ MISSING — needs registration |
| `Equiv` | tree.inc | — | ⚠️ MISSING — needs registration |
| `Find` | tree.inc | — | ⚠️ MISSING — needs registration |
| `Insert` | tree.inc | — | ⚠️ MISSING — needs registration |
| `XDump` | XDump.inc | — | ✅ registered |

**Missing count: 10 functions need adding to snobol4_inc.c**

---

## 4. SNOBOL4 DEFINE'd functions (called via computed goto $('name'))

These are called via `sno_apply("name", ...)` where the name is computed
at runtime from a SNOBOL4 expression. They are DEFINE'd by the program
itself during startup (`DEFINE('pp(x)...')` etc.) and dispatched via
`sno_apply`. They do NOT need C implementations — they are SNOBOL4
functions compiled into beautiful.c as C labels.

**Key insight**: `sno_apply("pp", ...)` must dispatch to the C label
`SNO_pp` in beautiful.c. This requires a runtime DEFINE mechanism that
maps function names to C label addresses via `setjmp`/function pointers.

| SNOBOL4 function | Defined in | Notes |
|-----------------|-----------|-------|
| `pp` | beautiful.c label `SNO_pp` | Pretty-printer (recursive) |
| `ss` | beautiful.c label `SNO_ss` | Stringize (recursive) |
| `pp_` | beautiful.c computed dispatch | pp_snoId, pp_snoStmt etc. |
| `ss_` | beautiful.c computed dispatch | ss_snoId etc. |
| `c` | DATA('tree') field accessor | |
| `t` | DATA('tree') field accessor | |
| `v` | DATA('tree') field accessor | |
| `n` | DATA('tree') field accessor | |
| `nPush` | counter.inc | already in sno_npush |
| `nPop` | counter.inc | already in sno_npop |
| `nInc` | counter.inc | already in sno_ninc |
| `link` | stack.inc DATA | link(next,value) constructor |
| `next` | stack.inc DATA | field accessor |
| `value` | stack.inc DATA | field accessor |
| `link_counter` | counter.inc DATA | |
| `link_tag` | counter.inc DATA | |
| `list` | various | |
| `nl` | global.inc variable | called as function — BUG? |
| `tree` | tree DATA constructor | |
| `type` | various | |
| `snoExpr*` | pattern variables | deferred ref patterns |
| `snoWhite` etc | pattern variables | deferred ref patterns |
| `findRefs_1` | beauty_run.sno | local label used as fn name |
| `ioFileOptDash` | io.inc | file I/O helper |

**These work via DEFINE() dispatch already in beautiful.c — no extra C needed,
except the dispatch mechanism (sno_apply must find compiled labels).**

---

## 5. DATA() types used

| DATA spec | Source | Fields | Status |
|-----------|--------|--------|--------|
| `tree(t,v,n,c)` | tree.inc | t,v,n,c | ✅ sno_data_define'd at startup |
| `link(next,value)` | stack.inc | next,value | ✅ DEFINE'd in beautiful.c |
| `link_counter(next,value)` | counter.inc | next,value | ✅ DEFINE'd |
| `link_tag(next,value)` | counter.inc | next,value | ✅ DEFINE'd |

---

## 6. Action list before beautiful.c compiles

### 6a. Add to snobol4_inc.c (10 missing C registrations)

- `icase(str)` — case.inc: build case-insensitive pattern from string
- `IsSnobol4()` — is.inc: always RETURN (we are SNOBOL4-tiny)
- `Push(x)` — stack.inc: alias `sno_push_val`
- `Pop()` / `Pop(var)` — stack.inc: alias `sno_pop_val`
- `TopCounter()` — counter.inc: alias `sno_ntop`
- `SqlSQize(str)` — Qize.inc: SQL single-quote escaping
- `TLump(x,len)` — TDump.inc: tree-to-string, stub ok
- `TValue(x)` — TDump.inc: tree value, stub ok
- `Visit(x,fnc)` — tree.inc: pre-order traversal
- `bVisit(x,fnc)` — tree.inc: (same as Visit)
- `Equal(x,y)` — tree.inc: structural equality
- `Equiv(x,y)` — tree.inc: structural equivalence
- `Find(xn,y,f)` — tree.inc: tree search
- `Insert(x,y,place)` — tree.inc: tree insert

### 6b. Dispatch mechanism for SNOBOL4 DEFINE'd functions

`sno_apply("pp", args, n)` must call the C function that implements
`pp()`. Since beautiful.c compiles SNOBOL4 functions as C goto-label
blocks (not C functions), we need either:

**Option A**: Wrap each DEFINE'd function as a real C function in
beautiful.c. The emitter generates `int sno_fn_pp(SnoVal *args, int n)`
wrappers that use `goto` internally. This is the correct Sprint 20 approach.

**Option B**: Use `sno_define()` to register each SNOBOL4 function body
as a C function at DEFINE() time. Requires the emitter to generate
function wrappers.

→ **Decision: Option A.** emit_c_stmt.py must emit each DEFINE'd
function as a proper C function, not just a goto label. Sprint 21.

For Sprint 20: since beautiful.c was emitted with the old approach
(goto labels, not C functions), the `sno_apply("pp", ...)` calls
will return null. The binary will compile but pp/ss won't recurse.

**Sprint 20 goal is a compiling binary. Sprint 21 is correct output.**

---

## 7. Summary counts

| Category | Total needed | Implemented | Missing |
|----------|-------------|-------------|---------|
| Pattern constructors | 19 | 19 | 0 |
| Runtime API symbols | 41 | 41 | 0 |
| Inc C functions | 30 | 20 | 10 |
| SNOBOL4 DEFINE dispatch | ~40 | 0 | ~40 (Sprint 21) |

**To compile beautiful.c: add 10 missing inc registrations → done.**
**To run correctly: implement DEFINE dispatch → Sprint 21.**
