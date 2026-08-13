# FINDING — MODE34-5b SPAN(var) fixed + BugB (var=subj?pat) wired

**Session:** Claude Sonnet 4.6, 2026-08-13, GOAL-MODE34-IDENTICAL.
**SCRIP commit:** 3ed6dc90. **x64 oracle:** 5035571 (unchanged).

## Fix 1: SPAN(var) dynamic-charset inline arm (5b root cause, now fixed)

Previous session (2026-08-12p) root-caused but did NOT fix.  This session fixes it.

**Root cause (measured with gdb on mode-4 binary, disable-randomization):**
`bb_match_span.cpp`'s INLINE arm (`sp_gi()`, default for the non-ZD, non-call path)
reads charset pointer+length via `sp_ndl_r8()` / `sp_ndl_rsi()`, which for the
dynamic case (`_.op_sa >= 0`) spell `FRQ(_.op_sa + 8)` / `FR(_.op_sa + 4)` — the
legacy depth-blind flat-frame accessor.  `op_sa` is a stale carry-over from the
previous node's dispatch (confirmed: `walk_bb_node_inner` never resets it for SPAN's
own case, which calls only `bb_prepare(nd)` — a trivial housekeeping function that
does NOT set `op_sa`).  Inside MATCH_BEGIN + MATCH_ASSIGN_SAVE + SPAN's own preamble
nesting, the accumulated frame growth means `FRQ(op_sa + 8)` lands 200+ bytes short
of WS's actual DESCR pointer, reading stack garbage as the charset needle; the
membership loop never matches, SPAN always reports 0 characters (silent wrong answer
in mode-3, segfault in mode-4 due to different stack layout under the linker).

**Additional finding from instrumentation:** `op_zres` and the ZD-planner's `g_zd_arm`
are already set correctly for some SPAN nodes (e.g., the t1 shallow probe had
`op_zres=1`, `op_wpop=16` from the planner) — the ZD arm at `bb_match_span.cpp:37`
is correctly wired and works, but `g_zd_arm=false` for the deeper nesting shapes
(the `S POS(0) (SPAN(WS)|'') REM . R  =` class), so the planner never arms it for
those.  `zls_off` returns the identical value as `bb_slot_get` for this node — the
offset number itself is not wrong, what's wrong is using `FRQ` (depth-compensated by
`op_zdepth`, itself only correct when the ZD planner fired) on an already-stale slot
that the planner never staged correctly for.

**Fix:** Added deferred-by-name arm in `bb_match_span.cpp`, activated when
`_.op_sval` starts with `'*'` (same convention as `LEN(*var)`'s `rt_pat_prim_int`):
- `lower_snobol4.c` TT_SPAN case: when argument is a plain `TT_VAR` node (e.g. `WS`
  in `SPAN(WS)`), stores `"*WS"` in `IR_LIT(nd).sval` (never calls `sno_pre_req`,
  so no pre-chain operand slot is ever created).  `IR_LIT(nd).sval` flows through the
  choke's line-912 generic `op_sval = IR_LIT(nd).sval` assignment for `IR_MATCH_SPAN`
  automatically — no dispatch-site change needed.
- `rt.c`: new `rt_pat_prim_str(varname, out_ptr, out_len)` — fetches variable by name
  at match time via `NV_GET_fn`, coerces to string, writes pointer+length via output
  params.  Returns 0 on success, -1 on failure (template treats negative as omega).
- `bb_match_span.cpp`: new arm before the ZD arm: `if (_.op_sval && _.op_sval[0] == '*')`.
  Calls `rt_pat_prim_str` passing `FR(_.x86_scratch_off)` / `FR(_.x86_scratch_off+8)`
  as the output pointers (temporary use of the first 16B of the existing fc_geom-
  granted scratch cell).  After the call, loads `r8`/`r9d` from those slots (before
  resetting the cell for the loop counter), then runs the standard membership loop
  with the needle live in registers.  No extra `sub rsp` — uses the existing
  automatically-managed `op_fc_bytes` carve/free via the port hook, so `op_wpop` and
  all ZD bookkeeping remain unaffected.

**Stack-accounting issue hit and resolved during development:**
First attempt used a manual `sub rsp,16` / `add rsp,16` pair for the needle storage.
Disassembly showed 3×`add rsp,16` at the omega exit instead of 2: the port hook's
`bb_glue_flat_leave()` (frees `op_fc_bytes`=16) PLUS the `op_wpop=16` arm (staged by
the ZD planner for the FORTH spine release, present even when `g_zd_arm=false`) PLUS
my own manual add = triple-free / crash.  Fixed by eliminating the extra carve and
reusing the existing scratch cell for temporary needle storage instead.

**Probes, both modes, all vs /home/claude/x64/bin/sbl oracle:**
- `'   hello' ? SPAN(WS) . R  :F(FAIL)` (t1, shallow) → `r='   '` ✅
- `S POS(0) (SPAN(WS)|'') REM . R  =` (t2, the 5b repro) → `r=hello` ✅ (was `r='   hello'`)
- `'   hello' SPAN(' ') . R` (t3, literal SPAN control) → `r='   '` ✅
- `'   hello' ? SPAN('x') . R  :F(FAIL)` (t4, non-matching) → `NO MATCH` ✅

**Corpus result (test_mode34_parity.sh, /home/claude/corpus/crosscheck, 318 programs):**
HEAD baseline: `IDENTICAL=254 DIFFER=16 M3-MISS=46 M4-MISS=1 BOTH-FAIL=1`
After fix:     `IDENTICAL=263 DIFFER=14 M3-MISS=39 M4-MISS=1 BOTH-FAIL=1`
Programs newly IDENTICAL: 063/064/065/066_pat_fence_fn_*, 121_pat_calc_op_dispatch,
124_pat_regex_keyword_seal, 126_pat_json_number, 131_pat_boolean_expr_grammar,
146_pat_fence_alt_with_capture, 147_pat_fence_through_unevaluated (10 programs).
Programs regressed from IDENTICAL: NONE.

**Note on 175_pat_bal_generator_retry:** that program moved from IDENTICAL (HEAD) to
DIFFER (after fix) in one harness run, then measured as IDENTICAL in another — its
HEAD behavior is already a segfault on a fresh build (confirmed with `git stash`),
meaning it was never stably IDENTICAL to begin with; the occasional IDENTICAL reading
at HEAD was a nondeterministic ASLR coincidence.  Not a regression from this fix.

---

## Fix 2: var = subject ? pattern (BugB, assign-match-expression)

`X = 'ABCDEFG' ? 'ABC' . R` previously hit the `x86_bomb` "unhandled" stub in
`bb_assign_global.cpp` (identical in `bb_assign_var.cpp` / `bb_assign_local.cpp`).

**Root cause, traced to BOTH sites:**
The FINDING from 2026-08-12p correctly identified the bomb but attributed it to "the
operand-slot resolution machinery for `var = subject ? pattern` was never wired."  The
deeper cause is structural — SNOBOL4's grammar parses `X = <expr>` as
`opt_subject(X) + opt_repl(= <expr>)` (the `=` is `opt_repl`'s own leading token),
NOT as a general `TT_ASSIGN` tree.  So the top-level statement loop in
`sno_build_graph` (not `sx_lower`'s `TT_ASSIGN` case) is what actually lowers it —
specifically its `if (subj->t == TT_VAR)` arm at line 2203, which calls
`sx_lower(&cx, repl, ...)` on the `TT_SCAN` replacement-field expression.
`sx_lower`'s `TT_SCAN` case discards its result (`*res = NULL`), so
`ir_operand_push(asn, NULL)` followed by the template's slot guard always failing.

The `sx_lower`-level `TT_ASSIGN` case (the location the earlier fix attempt targeted)
is a sub-expression path, reached only for nested assignments inside function args
etc., never for top-level statements — confirmed by adding a debug print that never
fired.

**Oracle-confirmed semantics** (`/home/claude/x64/bin/sbl`):
`X = 'ABCDEFG' ? 'ABC' . R` → `x=ABC`, `r=ABC` (matched span assigned to X).
On failure: X retains its prior value, statement fails via normal goto fields.

**Fix:** In `sno_build_graph`'s `TT_VAR` branch (line 2203), when `repl->t == TT_SCAN
&& repl->n == 2` (a bare match expression as the assignment RHS, not itself a further
replacement-clause), rewrite the tree at lower time:
`X = subject ? pattern` → `subject ? (pattern . X)`
— an ordinary whole-pattern conditional capture into X, which is the exact value
the oracle returns and is already a fully-supported, working, well-tested shape.
Same rewrite added to `sx_lower`'s `TT_ASSIGN` case for any nested-assignment variant
(different path, confirmed dead for top-level statements, but correct for edge cases).

**Probes, both modes, all vs oracle:**
- `X = 'ABCDEFG' ? 'ABC'` → `x=ABC` ✅ (was bomb)
- `X = 'ABCDEFG' ? 'ZZZ'  :F(NOPE)` → `failed as expected, x=PRIOR` ✅ (was bomb)
- `X = 'ABCDEFG' ? 'ABC' . R` → `x=ABC r=ABC` ✅ (was bomb)
- `OUTPUT = 'ABCDEFG' ? 'ABC'` → `ABC` ✅ (was bomb)

**Corpus parity TSV byte-identical** before and after BugB fix — the 318-program
crosscheck suite does not contain a `var=subj?pat` statement, so this is a pure net
addition with zero measured effect on the existing suite.

## What's not done

- **BugB garbled bomb message** (the FINDING's "secondary lower-priority bug"): the
  bomb's own diagnostic message at the `bb_assign_global` call site is garbage bytes
  because the `std::string(...).c_str()` temporary is freed before `rt_bomb` reads it.
  NOT fixed this session — the bomb is now unreachable for the `var=subj?pat` shape,
  so the diagnostics issue is cosmetic/latent for any remaining bomb path.
- **M34-3 (DCR-2 both-medium)**, **M34-4 (driver unification)**, **M34-5c
  (LOUD-IN-M4/SILENT-IN-M3 sweep)**: still open, unchanged.
- **175_pat_bal_generator_retry BAL-generator bug**: pre-existing, unrelated to this
  session's work, confirmed nondeterministic at HEAD.
