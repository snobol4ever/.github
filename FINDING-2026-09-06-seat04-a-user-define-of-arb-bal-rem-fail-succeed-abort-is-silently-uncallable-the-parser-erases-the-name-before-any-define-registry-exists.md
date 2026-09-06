# FINDING — a user DEFINE of ARB/BAL/REM/FAIL/SUCCEED/ABORT is silently uncallable: the parser erases the
name at parse time, before any DEFINE registry exists to consult

Seat: seat04 · 2026-09-06 · FLEET-12 · row `snobol4-sn4-is-system-fn-over-protects-sort-and-bal` (hq_S)
Build graded on: incremental `make` (RULES.md:118 FACT RULE). `RT_OPT=-O0`.
Witness: `corpus/packages/snobol4/snoflake_suite/gimpel-general-purpose-macro.sno` (via `GPM.INC` -> `BAL.INC`);
minimal repro below reproduces the identical symptom in 6 lines.

## 1. THE SYMPTOM, MEASURED

`gimpel-general-purpose-macro` fails `test_snoflake_suite.sh` in BOTH m3 and m4. The row this finding is filed
against assumed (per its own GOAL text and seat01's 2026-09-04 ledger analysis) that the gap was a missing
runtime check: real SPITBOL lets `DEFINE('BAL(...)...)` succeed (BAL was freed from ERROR 248 by SCRIP
`b1fb42fb1`) and only objects later, at runtime, when the function body's own return-value idiom
(`BAL = ...`, same name as the function) assigns to the bare protected name — SPITBOL raises
`ERROR 042 -- attempt to change value of protected variable`, and SCRIP does not.

**That premise is wrong.** SCRIP already has this exact check
(`src/runtime/core/core.c:2582`, `NV_SET_fn` -> `is_protected_pat_name` -> `core_runtime_error(42, ...)`), and
it already works: a plain top-level `BAL = 5` correctly halts with ERROR 042 in both modes, matching the
oracle (measured this session). The real defect sits earlier: **a call to a user-DEFINE'd `BAL` never reaches
the user's function body at all, in either mode** — it silently evaluates to the pre-existing built-in pattern
object instead. No error, no crash, wrong answer.

Minimal repro (`t2_ownname.sno`):
```
	DEFINE('BAL(X)')                                    :(OUT)
BAL	BAL = X
	$NAME = BAL                                         :(RETURN)
OUT	NAME = 'BAL_.1'
	OUTPUT = BAL('hi')
END
```
Expected (oracle, `sbl -bf`): halts with `ERROR 042` at the `BAL = X` line (BAL is DEFINE-able but the
own-name return-value assignment is still a protected-variable write). SCRIP m3 and m4 both: prints
`PATTERN`, rc=0 — the untouched built-in pattern object's string form, not the assigned value, not an error.

## 2. ROOT-CAUSED WITH gdb ON BOTH THE JIT'D m3 RUNTIME AND A LINKED m4 BINARY'S REAL ELF SYMBOLS

Confirmed empirically (not read off the .s) that the compiled function body is **never entered** in either
mode: breakpoints on `LBL__BAL` (the function's own entry label) and on the block containing its body's
`NV_SET_fn("BAL", ...)` call are never hit, in a linked `--compile` binary with real symbols. Tracing the
`OUTPUT = BAL('hi')` call site's own compiled block (`n22_call_bx` in this repro) shows it does not jump to
`LBL__BAL` at all — it calls a runtime helper with a fixed sentinel string:
```
lea   rdi, [rip + "SNO$MKPAT"]
...
call  rt_call_arr_bl@PLT
```
`SNO$MKPAT` is a real, dedicated builtin ID (`BID_SNOx24MKPAT`, `src/runtime/builtin_ids.h:55`, handled at
`src/runtime/by_name_dispatch.c:6072`) whose whole job is: build a compiled-pattern-object value from a
pattern registered at lowering time. The call is never a call to the user's proc at all — it was never
COMPILED as one.

## 3. THE ACTUAL MECHANISM: THE PARSER COLLAPSES THE CALL BEFORE ANY DEFINE IS KNOWN

Traced to `src/parsers/snobol4/snobol4.y:36-46` (`pat_prim_kind`) and `:27-34` (`tal_fnc_open`/`tal_fnc_close`):

```c
static tree_e pat_prim_kind(const char *s) {
    ...
    static const struct { const char *n; tree_e k; } m[] = {
        ...,{"ARB",TT_ARB},...,{"REM",TT_REM},{"FAIL",TT_FAIL},{"SUCCEED",TT_SUCCEED},
        {"FENCE",TT_FENCE},{"ABORT",TT_ABORT},{"BAL",TT_BAL},{NULL,TT_VAR}
    };
    for (int i = 0; m[i].n; i++) if (strcmp(s, m[i].n) == 0) return m[i].k;
    return TT_VAR;
}
static inline tree_t *tal_fnc_close(void) {
    int n=tal_count(); tree_e k=g_tal_kind[g_tal_depth-1]; char *sv=g_tal_sval[g_tal_depth-1];
    tree_t *e=ast_node_new(k==TT_VAR?TT_FNC:k);
    if (k==TT_VAR) e->v.sval=sv;                 /* <-- name is kept ONLY on the TT_FNC (fallthrough) path */
    for (int j=0;j<n;j++) expr_add_child(e,tal_child(j));
    tal_close(); return e;
}
```

Parsing `BAL(X)` (call syntax, any arg count) UNCONDITIONALLY produces a bare `TT_BAL` AST node, never a
`TT_FNC` node named `"BAL"`. The `if (k==TT_VAR) e->v.sval=sv;` guard means the name string is **only ever
attached when the node falls through to the generic call shape** — for the 7 recognised names (ANY, NOTANY,
SPAN, BREAK, BREAKX, LEN, POS, RPOS, TAB, RTAB, ARB, ARBNO, REM, FAIL, SUCCEED, FENCE, ABORT, BAL — 18 total in
this table; see below for which of these can ever collide with a user DEFINE) the string `"BAL"` is discarded
at the moment of parsing and **cannot be recovered downstream**. This happens in ONE pass, with no lookahead
and no DEFINE registry consulted — nor could it easily be, since SNOBOL4 permits a `DEFINE` to appear anywhere
relative to a call site and this grammar action fires the instant the closing paren is seen.

Everything downstream is correctly following its contract; it is simply never told this node used to be a
name. The dispatch actually taken for a plain `VAR = BAL('hi')` statement runs through
`src/lower/lower_snobol4.c:2225` (`sno_is_pattern_rhs(repl) && sno_pat_supported(repl)` — the "store a
first-class pattern value into a variable" idiom, e.g. the completely legitimate `P = ARBNO(BAL)`), which
consults `sno_pat_eff_kind()` (`lower_snobol4.c:1038-1048`, a SEPARATE, smaller 7-name table that reclassifies
a bare `TT_VAR`/`TT_KEYWORD` — moot here since the parser already handed it a `TT_BAL` node directly) and
`sno_is_pattern_rhs()`'s own switch (`lower_snobol4.c:1894-1910`, `case ... TT_BAL:` returns 1 unconditionally).
None of these three sites has, or could currently obtain, the string `"BAL"` to check against the DEFINE
registry (`sno_predef_registered()` / the `defs[]` array, both already built by the lowerer's prescan and
already used elsewhere in this same file) — the information was discarded two stages earlier.

**There is also a second, PATTERN-STATEMENT-CONTEXT table with the same property**, `lower_snobol4.c:1846`
(inside `sno_pat_node`'s `case TT_FNC:` arm) — but tracing confirms this arm is for when a call-shaped pattern
element survives AS a `TT_FNC` into pattern lowering (a different source shape than the one in this finding);
it was my first, less precise hypothesis last session and is a real but SEPARATE recognition point from the
one actually firing for `VAR = BAL(...)`. Both exist; both would need the same treatment; they are not the
same bug instance.

## 4. SCOPE: EXACTLY 6 NAMES CAN EVER REACH THIS AMBIGUITY

Of the 18 names in `pat_prim_kind`/the parallel `pm[]` table, only names that are BOTH (a) freed for user
`DEFINE` (SCRIP `b1fb42fb1`'s list of 18: ABORT ALT ARB BAL CONCAT FAIL FUNCTION LABEL LCASE NAME NUMERIC PLS
REAL REM SUCCEED UCASE VALUE VDIFFER) AND (b) present in the parser's pattern-primitive table can ever collide:
**ARB, BAL, REM, FAIL, SUCCEED, ABORT** (6). The other 12 in the parser table (ANY, NOTANY, SPAN, BREAK,
BREAKX, LEN, POS, RPOS, TAB, RTAB, ARBNO, FENCE) remain fully protected against redefinition (ERROR 248 at
DEFINE time) and can never reach this state in a compiling program. Ordinary bare-primitive usage of all 18
(the overwhelming common case — `X BAL Y`, `ARBNO(BAL)`, `FENCE`, etc., never redefined) is completely
unaffected by anything in this finding and must stay that way.

## 5. WHY THIS FINDING DOES NOT SHIP A FIX

This sits inside `src/lower/lower_snobol4.c` and `src/parsers/snobol4/snobol4.y`, in the immediate vicinity of
hq_S's own active, multi-part "four-term" DEFINE-dispatch series
(`FINDING-2026-09-06-hq_S-define-terms-0-1-2-...`, `FINDING-2026-09-06-hq_U-define-term-3-...`) — a RELATED
but DISTINCT mechanism (their terms are about multiple `DEFINE`s of the SAME name resolving to the correct
ENTRY LABEL; this finding is about a call being recognised as a pattern primitive before it is ever considered
a call at all). That series has already produced one revert this same day (`b1c267ca9`, undoing d067ceae4,
after it landed at m3 FAIL=299 / m4 FAIL=336 plus 76 crashes, ALL `user_function_*`) for a change in this
same neighbourhood. A correct fix here needs coordinated changes at MINIMUM at: the parser (preserve the name
string on these 18 nodes, at least when a DEFINE for that name might exist — or always, and let the lowerer
decide), `sno_is_pattern_rhs`, `sno_pat_node`'s `TT_FNC` arm, and `sno_pat_eff_kind`'s `TT_VAR`/`TT_KEYWORD`
path (for the bare-name-without-parens shape) — each needs its own reasoning about whether a live DEFINE
should override it, and the ordinary-usage case (§4) must be proven unaffected by the full regression battery
(SNOBOL4 master both modes, snoflake suite both modes) before landing, not sampled. Given the proximity and
recency of a real regression in the same file for a related reason, I judged writing this up precisely, for
hq_S or whoever next works this row, to be worth more than a rushed multi-site patch this sitting.

## 6. WHAT REMAINS, BY OWNER

 - The coordinated parser+lowerer fix described in §3/§5. Natural owner: hq_S (SNOBOL4 runtime lane, already
   deep in DEFINE-dispatch this same day) or whoever next claims
   `snobol4-sn4-is-system-fn-over-protects-sort-and-bal`.
 - Once the call reaches the user's function body, no further runtime work should be needed: the ERROR-042
   check (`core.c:2582`) already fires correctly for a plain protected-name assignment (§1); reachability is
   the only gap, not the check itself. Re-verify this assumption once the call actually lands in the body —
   it was not verified against the OWN-NAME idiom specifically, only against a top-level assignment.
 - Acceptance test: this row's own DONE-WHEN (`/home/resources/postoffice/tasks/snobol4-sn4-is-system-fn-over-protects-sort-and-bal.task.md`),
   plus the minimal repro in §1 should halt with ERROR 042 instead of printing `PATTERN`.
