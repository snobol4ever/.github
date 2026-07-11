# HANDOFF — 2026-07-10 (Claude) — beauty suite partial progress, session 2

**STATUS: IN PROGRESS — 3 additional drivers green, commit pushed to SCRIP. BLOCKED on ARBNO/NOTANY in runtime-recipe context + '*'-prefix want-name abort.**

SCRIP HEAD: `6749c97c` (after rebase onto `d05b2028`)

## PROGRESS THIS SESSION

### Landed (all green both m3+m4, no regressions):
1. **global_driver GREEN** — &ALPHABET: `rt_keyword_read_snobol4` now intercepts "alphabet" before delegating to `kw_read("cset")`, returns true 256-char `BSTRVAL(alphabet, 256)` (manual p194). Embedded-NUL string pipeline: `IS_NULL_fn` changed from `slen != 0xFFFFFFFF && (!s || !*s)` to `slen == 0 && (!s || !*s)` so DT_S with recorded slen>0 is never null. `rt_match_enter`, `rt_match_replace`, `rt_scan_enter`, `rt_scan_needle` all use pointer-identity guard: `sv.v==DT_S && sv.slen && s==sv.s ? sv.slen : strlen(s)`.
2. **tree_driver GREEN** — `sno_array_from_proto("1:0")` triggered: ARRAY zero-size fix (`hi < lo - 1` returns FAILDESCR; `hi == lo-1` = 0 elements is valid). Also: SORT/RSORT now build nested-row representation (outer N-array of 2-elem row arrays) matching the live chained-subscript model; `a->proto` set so PROTOTYPE returns "N,2". DATATYPE DT_A → "ARRAY" (was "list"; Icon `type()` keeps "list").
3. **ReadWrite_driver GREEN** — multi-literal DEFINE prototype: `sno_qlit_fold` helper folds `TT_CAT`/`TT_SEQ` of `TT_QLIT` children into one string at compile time; all four `sno_parse_define` call sites use it.

### Corpus delta (vs session start `7fe04a1a`):
- m3: PASS 287→290 FAIL 17→14
- m4: PASS 286→289 FAIL 8→8 SKIP 10→7 (ReadWrite/tree/global cleared)

### Regressions: NONE (icon 12/12×2, prolog 115/115×3 unchanged)

## BLOCKED: TWO OPEN BUGS

### BUG 1: ARBNO/NOTANY/FENCE in runtime-recipe expression context (tree kind 25 = TT_ARBNO)
**Symptom:** `FATAL expression form not in the landed subset: tree kind 25` when compiling omega/Qize/TDump/XDump/Gen drivers.
**Root cause:** These drivers use patterns like `ARBNO(NOTANY(...))` as part of pattern expressions stored in variables (runtime-recipe context). The recipe path routes through `sx_lower` (expression lowerer) which has a `default: sno_fatal(...)` arm covering TT_ARBNO, TT_NOTANY, etc.
**What's needed:** In `sx_lower` (or before it), when the expression is a pattern-kind node (TT_ARBNO, TT_FENCE, TT_NOTANY, TT_ANY, TT_SPAN, TT_BREAK, etc.) occurring in a VALUE context (not a direct pattern-match subject), route through the B-RE recipe builder (`SNO$PBK`, `SNO$PBALT`, `SNO$PB0` etc.) the same way `sno_pat_node` does — or redirect these nodes to call `pat_arbno()`, `pat_notany()` etc. runtime constructors. Look at how `str_concat_d`'s DT_P branch works and trace `sno_is_pattern_rhs` → the recipe builder routing in the assignment arm (`SNO$MKPAT` at lower_snobol4.c:1331). The issue is that TT_ARBNO etc. in EXPRESSION position (not subject-pattern position) need to produce a DT_P value, not be lowered as control-flow pattern matchers.

### BUG 2: '*'-prefix want-name path aborts (rt_assign_var: lvalue not a variable)
**Symptom:** rt_assign_var bombs when called from `rt_cap_assign_cursor` with a '*'-prefixed varname and the carved proc returns a DESCR that isn't a DT_N name.
**Probe:** `/tmp/p_dcap.sno` (created this session — repro if it still exists, else recreate: `DEFINE('assign(name,val)') :(assign_end); assign $name = val :(RETURN); assign_end; pat = SPAN('abc') . *assign(.part, *'word'); 'aabbcc' pat; OUTPUT = 'part=' part`).
**Root cause:** The carved EXPR$N proc for `.part` — when called with `rt_g_want_name=1` — returns a DT_DATA or DT_N slen=2 NAMEPTR that rt_assign_var doesn't handle. Check what `.part` (name-operator over a field ref `.part`) actually returns when called as `rt_call_named_proc(EXPR$0)` with want-name set. The name-operator carve calls the existing `*` path but the return type may differ from the simple-var DT_N slen=0 case that rt_assign_var expects. Look at `rt_nret_fix` and the DT_N slen=2 NAMEPTR arm in `rt_deref` — rt_assign_var needs the same three-arm handling.

## BUILD STATE
All changes in SCRIP commit `6749c97c`. No corpus changes. SCRIP builds clean.

## BEAUTY SUITE STATUS
| Driver | Status |
|--------|--------|
| ShiftReduce | ✅ GREEN |
| assign | ✅ GREEN |
| case | ✅ GREEN |
| counter | ✅ GREEN |
| fence | ✅ GREEN |
| global | ✅ GREEN (this session) |
| match | ✅ GREEN |
| stack | ✅ GREEN |
| trace | ✅ GREEN |
| tree | ✅ GREEN (this session) |
| ReadWrite | ✅ GREEN (this session) |
| Gen | ❌ capture target not simple var (BUG 1 + BUG 2) |
| Qize | ❌ ARBNO in expression context (BUG 1) |
| TDump | ❌ capture target not simple var (BUG 1 + BUG 2) |
| XDump | ❌ ARBNO in expression context (BUG 1) |
| omega | ❌ ARBNO in expression context (BUG 1) |
| semantic | ❌ EVAL (deeper, unrelated) |

## NEXT SESSION PLAN
1. Fix BUG 2 first (simpler: rt_assign_var needs DT_N slen=1 NAMEPTR arm, same as rt_deref has).
2. Fix BUG 1: add TT_ARBNO/TT_FENCE/TT_ANY/TT_NOTANY/TT_SPAN/TT_BREAK/TT_BREAKX/TT_REM/TT_ARB/TT_BAL to `sx_lower` by routing them to the recipe runtime constructors (pat_arbno, pat_notany, etc. in pattern_match.c). These are value-producing calls, not control-flow — their lowering is just `IR_CALL` to the right constructor.
3. Run full corpus gate + beauty suite. Push.
4. beauty.sno self-host: depends on omega/Qize/Gen (all blocked on BUG 1).

## HANDOFF NOTES
- `GOAL-SCRIP-BEAUTY.md` is stale ("10/18 passing") — ignore its step list, use `scripts/test_corpus_snobol4.sh` for the gate.
- The `scripts/handoff_status.sh` script checks corpus too; credential needed for both repos.
- SPITBOL oracle: `/home/claude/x64/bin/sbl` (clone `snobol4ever/x64` if fresh container).
