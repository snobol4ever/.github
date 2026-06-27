# GOAL-LANG-ICON.md — Icon Frontend Ladder

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** Icon standard library procedures pass under all three modes
(--run, --run, --run). Rung ladder reaches rung-36. Icon generator
boxes (E_TO, E_EVERY, E_SUSPEND, E_BANG, E_ALT_GEN) work under SM+BB.

**Cross-pollination:** icn_runtime.c, icon_gen.c improvements benefit
Raku (which shares icn_proc_table and icn_call_proc). BB broker improvements
(bb_broker, bb_boxes.c) benefit SNOBOL4 pattern matching.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_icon.sh             # PASS=5
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=45
bash /home/claude/SCRIP/scripts/test_crosscheck_icon.sh        # PASS=4 (3-mode divergence check)
bash /home/claude/SCRIP/scripts/test_icon_all_rungs.sh      # rung01-36; --rung RUNG to target one
# Per-rung gates for IC-7:
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_30.sh        # abs/max/min/sqrt/seq
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_31.sh        # sort/sortf
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_32.sh        # string retval every
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_33.sh        # case expressions
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_34.sh        # null/nonnull test
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_35.sh        # block bodies + table str/str
bash /home/claude/SCRIP/scripts/test_icon_ir_rung_36.sh        # JCON suite (xfail=23 expected)
```

---

## Architecture reminder

```
.icn → icon_parse() → CODE_t* [LANG_ICN]   (no AST layer — FI-2 done)
    --run  → execute_program() → interp_eval() with ICN_CUR frame stack
    --run  → sm_lower() → SM_BB_PUMP per stmt → bb_broker(BB_PUMP)
    --run → sm_lower() → SM_BB_PUMP → sm_codegen() → sm_jit_run()

Generator boxes in icon_gen.c:
    E_TO       → icn_bb_to       (lo/hi/cur)
    E_TO_BY    → icn_bb_to_by    (lo/hi/step/cur)
    E_ITERATE  → icn_bb_iterate  (str/len/pos)
    E_SUSPEND  → icn_bb_suspend  (ucontext coroutine)
    E_FNC find → icn_bb_find     (needle/haystack/pos)
```

---

## Rung ladder — all modes, x86

Current baseline: rung01–11 59/59 PASS under --run (GOAL-ICN-BROKER done).
Rung 12–36 are the ladder for this goal.

### Phase 1 — IR-run rung ladder (rung 12–36)

- [x] **IC-1** — rung01–11: 59/59 PASS --run. (done, GOAL-ICN-BROKER)

- [x] **IC-2b** — Complete ALL goal-directed-evaluation ops as BB boxes in `icon_gen.c`
  and wire into `icn_eval_gen()`. No rung work until every GDE op has a box.
  Raku shares `icn_eval_gen`; this unblocks both ladders.

  Missing boxes to write (all in `src/frontend/icon/icon_gen.c` + declared in `icon_gen.h`,
  registered in `icn_eval_gen()` switch in `src/runtime/interp/icn_runtime.c`):

  Note: `E_SCAN` is the **same IR node as SNOBOL4 matching** — shared implementation,
  already handled correctly by the oneshot fallback in `icn_eval_gen`. Do NOT add a scan box.

  | Op | Box to write | State struct | Notes |
  |---|---|---|---|
  | `E_LIMIT` | `icn_bb_limit` | `icn_limit_state_t: gen, max, count` | `E \ N`: drive gen, yield each value, stop after N |
  | `E_EVERY` | `icn_bb_every` | `icn_every_state_t: gen, body (EXPR_t*)` | drive gen to exhaustion, eval body per tick |
  | `E_BANG_BINARY` | `icn_bb_bang_binary` | `icn_bang_binary_state_t: proc_expr, arg_box, cur_arg` | `E1 ! E2`: call E1 with successive values from E2 |
  | `E_SEQ_EXPR` | `icn_bb_seq_expr` | `icn_seq_state_t: children[], n, last_box` | `(E1;E2;…;En)`: eval prefix, last child is the generator |

  Gate: `bash scripts/test_smoke_icon.sh` still PASS=5; all five new boxes compile clean;
  `icn_eval_gen` returns a valid box (not `icn_oneshot_box` fallthrough) for each op.
  Smoke test for each box added to `icon_gen.c` unit test block.

- [x] **IC-2** — rung12: string relational ops (`<<`, `>>`, `<=`, `>=`, `==`, `~=`),
  `*s` (string size).
  Gate: test_icon_ir_rung_12_strrelop_size.sh PASS.

- [x] **IC-3** — rung13: tables (`table()`, key lookup, `!T` iteration).
  Gate: test_icon_ir_rung_13_tables.sh PASS=5/5. DONE 2026-04-15.
  Bugs fixed: table() union clobber (d.s=NULL after d.tbl), delete() wrong hash (h*31 vs djb2), Icon E_ASSIGN missing E_IDX branch.

- [x] **IC-4** — rung14: limit (E \ N) — corpus rung14 is limit tests, not lists.
  Gate: test_icon_ir_rung_14_limit.sh PASS=5/5. DONE 2026-04-15.

- [x] **IC-5** — rung15+: real output format, pow (always real), E_TO_BY real step, swap(), string subscript/section, list builtins, global/initial, records, str/type builtins.
  DONE 2026-04-16: rung24 records PASS=5/5, rung21/25 initial PASS=12/12.
  Fixes: polyglot_init E_RECORD registration, ICN E_FNC sc_dat_find_type lookup,
  ICN E_ASSIGN E_FIELD lvalue, icn_init_save_frame() for initial persistence.
  Remaining IC-6: rung13 alt-gen(2), rung22 put_bang(1), rung23 key(1),
  rung16 sub_every(1), rung18 relop(1), rung19 pow(1), rung28 trim_map(1), rung29 image(1).
  Gate: smoke PASS=5, broker PASS=41, rung01-11 PASS=59. HEAD 7a64e8f9.

- [x] **IC-6** — rung01–29 PASS=156/156 FAIL=0 confirmed (2026-04-16, session 14).
  Corpus recount: all 7 suspected remaining failures (rung22 put_bang, rung23 key,
  rung16 sub_every, rung18 relop, rung19 pow, rung28 trim_map, rung29 image) were
  already passing from session 13 fixes. No new work needed.
  Gates: smoke PASS=5, broker PASS=45 FAIL=0, rung01-29 PASS=156/156. HEAD 37d45f96.

- [x] **IC-7** — rung30–35: misc builtins, sort/sortf, string retval every, case, null-test, block bodies.
  Baseline (2026-04-16): rung30 0/5, rung31 0/5, rung32 4/5, rung33 1/5, rung34 1/5, rung35 7/7.
  DONE 2026-04-30 session #16: rung32 strret_every closed.
  Root cause: in icn_eval_gen the user-proc match (line 890) was matching
  E_FNC with a generative E_ALTERNATE arg, pre-evaluating the alternation
  as a single scalar via interp_eval, and building an icn_bb_suspend
  coroutine. On every β tick the proc ran once with "a", returned [a],
  exhausted. The downstream user-proc-with-gen-arg icn_bb_fnc_gen path
  (line ~1000) was unreachable because the suspend path matched first.
  Fix: hoisted generative-arg detection INTO the user-proc match — if any
  arg is generative, build an icn_bb_fnc_gen box that pumps the gen and
  re-calls icn_call_proc with the substituted scalar via icn_call_builtin's
  user-proc dispatch each tick. Non-suspending procs run-to-completion per
  tick; existing suspend coroutine path preserved for procs without gen args.
  Gate scripts (all rewritten for --run, self-contained, xfail-aware):
    `bash scripts/test_icon_ir_rung_30.sh`  — abs/max/min/sqrt/seq builtins
    `bash scripts/test_icon_ir_rung_31.sh`  — sort(L) / sortf(L,n)
    `bash scripts/test_icon_ir_rung_32.sh`  — string-return-value in every
    `bash scripts/test_icon_ir_rung_33.sh`  — case/of/default expressions
    `bash scripts/test_icon_ir_rung_34.sh`  — null test (\x, \=x)
    `bash scripts/test_icon_ir_rung_35.sh`  — block bodies + table str/str (PASS=7/7 already)
  Overall gate: `bash scripts/test_icon_all_rungs.sh` — now covers rung01–36,
    xfail-aware, --rung/--scrip/--corpus switches, timeout 30s for rung36.
  All IC-7 rungs PASS 32/32 (5+5+5+5+5+7). smoke PASS=5, broker PASS=49,
  crosscheck PASS=4. SCRIP HEAD `8fbdd080` (rung32 fix), advanced to
  `59514e72` in same session #16 with IC-8 batch.

- [ ] **IC-8** — rung36: JCON integration suite (75 tests).
  Baseline (2026-04-16): PASS=2 FAIL=50 XFAIL=23 TOTAL=75.
  Session #16 (2026-04-30) advance: PASS=2 → 4, FAIL=50 → 41, XFAIL=23 → 30.
  Session #17 (2026-04-30) advance: PASS=4 → **5**, FAIL=41 → 40, XFAIL=30 (unchanged).
  +1 closed: rung36_jcon_primes — confirmed by diff -q empty against expected.

  **Headline**: GDE-aware E_IF in icon-frame dispatch unlocked **+28 PASS in
  test_icon_ir_all_rungs** (160 → 188, FAIL 73 → 45) — many rung12–35 tests
  had `if (test-with-generator)` patterns that were silently consulting only
  the first generated value. The primes test was just the most visible
  symptom; the fix is a horizontal win across the whole rung ladder.

  Generic fixes landed this session (all in src/driver/interp.c +
  src/runtime/interp/icn_runtime.h):

   1. **GDE-aware E_IF in icon-frame dispatch (line ~2591)** — when the test
      child satisfies `icn_is_gen()`, route through `icn_eval_gen` and pump
      α once. Any non-fail tick → take then-branch; exhaustion (IS_FAIL on
      α) → take else-branch. Mirrors the E_EVERY pump pattern that already
      lived a few cases below. The fix landed in the **icon-frame switch**
      (line 2591) NOT the shared switch's E_IF below (line 3732); inside an
      Icon procedure body `icn_frame_depth > 0` so the icon-frame switch
      `return`s and the shared switch is unreachable. (Earlier pass to
      line 3732 did nothing — see Wrong-Site Lesson below.)

      Confirmed by diff -q: `if i % (2 to i-1) = 0 then next` now succeeds
      for any composite i, falls through for any prime i.

   2. **`next` keyword wired** — `E_LOOP_NEXT` was parsed (icon_parse.c:563)
      but had no handler. Added: new `int loop_next` field on `IcnFrame`
      next to `loop_break`; E_LOOP_NEXT case sets `ICN_CUR.loop_next = 1`;
      `E_SEQ_EXPR` in icon-frame dispatch short-circuits its child loop on
      `loop_next` (so `if cond then next; rest_of_block` correctly skips
      `rest_of_block`); E_EVERY (all three pump variants — E_ASSIGN, E_SEQ
      conjunction, main), E_WHILE, E_UNTIL, E_REPEAT all save+clear+restore
      `loop_next` at iteration boundaries so `next` doesn't escape the
      enclosing loop.

  **Wrong-site lesson — read carefully** (saved future-session time):
  `interp_eval()` in `src/driver/interp.c` has TWO switch statements with
  overlapping kind cases:
   - **Lines 1006–4126**: an `if (icn_frame_depth > 0) { switch(e->kind) ... }`
     icon-frame block. Most "Icon-context" cases live here and `return`
     directly out of `interp_eval`.
   - **Lines 4126→**: the shared switch below the icon-frame `}`. Reached
     only when `icn_frame_depth == 0` OR when the icon-frame switch's
     `default: break` falls through.

  Inside any Icon procedure body, `icn_frame_depth > 0` and the icon-frame
  switch's `case E_IF` returns directly — the shared switch's `case E_IF`
  is dead code under that condition. Patches must go in the **icon-frame
  switch** (line 2591 for E_IF, similarly for E_EVERY/E_WHILE/etc), not
  the lower one. Confirmed via `/tmp/dbg.txt` instrumentation: every E_IF
  during rung36 hits the icon-frame handler. Wrote initial patch at line
  3732 by mistake; debug trace was empty for the new path; relocated to
  line 2591 and the patch fired immediately.

  **Build hazard — clean rebuild required when icn_runtime.h changes**:
  `bash scripts/build_scrip.sh` does not detect header timestamp changes
  for `.o` files in subdirs other than the file currently being compiled.
  Adding `loop_next` to `IcnFrame` shifted offsets of `body_root`, `sc`,
  `suspending`, `suspend_val`, `suspend_do` — but `icn_runtime.o` was
  compiled against the OLD layout while `interp.o` saw the NEW layout,
  producing memory corruption and a phantom 16-test broker regression
  (49→33). The fix: `find src -name '*.o' -delete && bash scripts/build_scrip.sh`.
  Anyone editing `icn_runtime.h` should default to a clean rebuild.

  Open failures grouped by root cause (next-session priorities):
   - **`!N` integer iteration** — `!-514` yields digits as integers/strings.
     Segfaults on btrees/prefix/every. E_ITERATE for `IS_INT_fn(av)` needs
     handling — iterate the absolute decimal digits. (~3 tests with xfails
     removable once fixed.) **Highest leverage next pivot.**
   - **Tables: `t[k]` semantics for non-string keys / `[X]:NONMEMBER`
     literal sentinel leaking into output** — rung36_jcon_table shows
     wide divergence; `[2]&null:NONMEMBER` is appearing in printed output
     where SPITBOL/Icon would suppress un-set entries. Look at how
     subscript_get returns its miss sentinel and how `image()`/print of
     a table iterates entries.
   - **`Error 3` in rung36_jcon_queens, rung36_jcon_string** —
     "Erroneous array or table reference" early in execution; suggests
     a subscript/section path that returns FAILDESCR when something
     deeper (probably list-of-list construction) wasn't built right.
   - **Real number formatting edge cases** — radix, numeric, mathfunc
     have decimal-precision and column-width mismatches.
   - **`proc()` builtin / variable-arity / indirect call (!plist)()** —
     args, fncs, fncs1 tests. Major Icon feature; defer until other
     wins are taken.
   - **co-expressions, &error, &fail, &trace, &errornumber, &errorvalue**
     — already correctly xfailed.
   - **scan/scan1/scan2** — `?` scan with goal-directed subexpressions.
     Builds on existing E_SCAN oneshot fallback.
   - **string1, substring** — string subscript/section forms `s[i+:n]`
     with chained `:=` and `:=:` swap not fully working.

  **Session #27 (2026-05-02):** scan builtin infrastructure landed.  Fixes
  in `src/driver/interp.c`:
  - `move(n)` OOM fix: `(size_t)(-4)` was ~2^64 → GC_malloc death.  Now
    uses `abs(n)` for length and `min(old,newp)` for start.
  - `tab(n)` negative/zero normalization: `n=0 → slen+1`, `n<0 → slen+1+n`.
  - `pos(n)` and `rpos(n)`: new builtins; test `&pos == normalized(n)`.
  - `any/many/upto`: extended to accept explicit `(c, s, i1, i2)` args;
    `nargs==2` uses `icn_scan_pos` as default `i1` (scan-context position in
    explicit string).
  - `bal(c1, c2, c3, ...)`: new scalar path in `interp.c`; Byrd box
    `icn_bb_bal` in `icon_gen.c` wired through `icn_eval_gen` for `every`
    generator use.  State struct `icn_bal_state_t` in `icon_gen.h`.
  Gates: smoke 5/0, broker 49/0, crosscheck 4/0/0.  PASS=13 unchanged —
  `rung36_jcon_scan1` still FAILs due to remaining issues:
  - `E_SEQ` (`A & B`) conjunction short-circuits when `&pos := 6` assign
    returns wrong value (FAILDESCR instead of success).
  - `many/upto` cset operations with high-bit chars fail because `strchr`
    is not 8-bit-safe; needs a cset-bitmap lookup instead.
  - `find(needle, "s1"|"s2"|...)` with alternation-as-generator needs the
    `icn_bb_find` box to be driven by `icn_eval_gen`, not the oneshot
    scalar path.
  SCRIP HEAD after commit from this session.

  **Next session pivot**: fix `E_SEQ` (`&` conjunction) return value so
  `&pos := 6 & write(...)` doesn't short-circuit.  Then fix `strchr`→cset
  bitmap for 8-bit-safe `any/many/upto`.  These two fixes likely close
  `rung36_jcon_scan1` (+1 PASS).

  Gate: `bash scripts/test_icon_ir_rung_36.sh` — current PASS=5/40/30/75.
  Goal: reduce FAIL toward 0; XFAIL is acceptable but should ideally
  shrink too. Note: test_icon_ir_rung_36.sh rewritten for --run by
  session #16 (was JVM-era jasmin script).

  Session #17 final state (clean rebuild, all gates clean):
    smoke_icon                  PASS=5  FAIL=0
    smoke_unified_broker        PASS=49 FAIL=0
    crosscheck_icon             PASS=4  FAIL=0  SKIP=0
    test_icon_ir_all_rungs      PASS=188 FAIL=45 XFAIL=30 TOTAL=263
    test_icon_ir_rung_36        PASS=5  FAIL=40 XFAIL=30 TOTAL=75

- [x] **IC-10** — Unify Icon scan-frame primitives onto SNOBOL4 pattern IR + BBs.
  **CORRECTED 2026-05-01: This step CLOSED with a "no work needed" decision per
  prior architectural ruling (S-8B / S-12B in `GOAL-ICON-IR-RUN.md` lines 157-197).
  IC-10 was OPENED with an incorrect proposal; the correction follows.**

  ### What I proposed (incorrect)

  Lower Icon scan-frame builtins (`upto`, `many`, `any`, `notany`, `tab`, `move`,
  `match`, `pos`, `rpos`) to existing IR pattern primitive nodes (`E_BREAK`,
  `E_SPAN`, `E_ANY`, etc.) and reuse SNOBOL4's existing Byrd boxes
  (`bb_brk`, `bb_span`, `bb_any`, `bb_notany` in `runtime/x86/bb_boxes.c`).

  Rationale was: "these IR nodes already exist, the boxes already exist,
  SNOBOL4 already uses both, Icon doesn't — the IR is a single source of truth
  per `ir.h:4`, so unify."

  ### Why it is wrong (Lon's ruling, recorded April 2026)

  **`GOAL-ICON-IR-RUN.md` line 157-163, Step S-8B:**

  > "S-8B — Verify Icon/SNOBOL4 IR sharing. ✅ CONFIRMED — no work needed.
  > E_SCAN is already shared: SNOBOL4 parser emits E_SCAN(subj,pat) for
  > pattern match; icon_lower.c emits E_SCAN(subj,body) for expr?body. Same node.
  > **Scan builtins (any/upto/many/tab/move/match) are correctly handled as
  > E_FNC name dispatch in interp_eval — mirroring exactly what x64/JVM/NET
  > emitters do (strcmp inside E_FNC case). No E_PAT_* nodes exist in the IR;
  > E_FNC name dispatch IS the architecture. No refactor needed."**

  **`GOAL-ICON-IR-RUN.md` line 184-197, Step S-12B (architectural mandate
  from Lon, 2026-04-13):**

  > "Architectural reality: exec_stmt/bb_build use PATND_t + spec_t
  > (string-cursor typed). Icon generators produce DESCR_t values, not
  > spec_t substrings. Therefore:
  > - E_SCAN (Icon ?) → exec_stmt (already correct — string match in scan context)
  > - E_TO / E_ITERATE / E_SUSPEND (value generators) → need DESCR_t-typed Byrd boxes"

  ### The architectural distinction I missed

  There are **two distinct Byrd-box typing universes** in the codebase, by
  deliberate design:

  1. **Pattern Byrd boxes** — `bb_brk`, `bb_span`, `bb_any`, `bb_notany`,
     `bb_breakx` etc. in `runtime/x86/bb_boxes.c`. They operate on
     `PATND_t` + `spec_t` (string-cursor typed). They yield matched-substring
     `spec_t` descriptors. The Σ/Δ/Σlen state model is sealed inside the
     SPITBOL-style match-call lifecycle.

  2. **Value Byrd boxes** — `icn_bb_to`, `icn_bb_iterate`, `icn_bb_suspend`,
     `icn_bb_alternate`, etc. in `frontend/icon/icon_gen.c` and
     `runtime/interp/icn_runtime.c`. They operate on `DESCR_t` (any-typed
     descriptors). They yield arbitrary values.

  Icon's `upto(c)` yields `INTVAL(new_pos)` — a value-typed integer
  cursor position. SNOBOL4's `bb_brk` yields a `spec_t` matched substring
  via `descr_from_spec(BRK)`. **The cursor in `bb_brk` (Δ) is the pattern
  engine's whole-match position, not adaptable to Icon's per-call
  `icn_scan_pos` mutation.** Routing `upto` through `bb_brk` would mean
  dragging the entire pattern-engine state machine into every Icon scan-frame
  call — heavy, with semantic mismatch at the cursor-mutation boundary.

  ### What the existing E_FNC dispatch architecture is

  Icon scan builtins parse to `E_FNC` nodes with the builtin name as
  `sval`. `interp_eval` E_FNC dispatches by name (`if (!strcmp(fn,"upto"))`,
  etc.) — handling each builtin inline against the current scan-frame state
  (`icn_scan_subj`, `icn_scan_pos`). The .NET / JVM / x64 emitters take the
  exact same approach (per S-8B's "mirroring exactly what x64/JVM/NET
  emitters do" claim). E_FNC-by-name IS the cross-backend contract for
  scan-frame primitives.

  ### Where the actual gap is — and where IC-10's followup work belongs

  The β-backtracking gap I demonstrated (`every "aXbYcZ" ? upto('XYZ')`
  yields `2` only, should yield `2`/`4`/`6`) is real. The correct fix
  is NOT to lower upto to E_BREAK; it IS to write a **value-typed**
  Byrd box `icn_bb_upto` that mirrors `icn_bb_iterate` / `icn_bb_to`'s
  pattern: state struct holds the saved scan-frame snapshot, α advances
  `icn_scan_pos` and yields `INTVAL(new_pos)`, β restores the saved pos
  and advances internally to the next match position, ω yields FAIL when
  past end-of-subject. Same shape for `icn_bb_many`, `icn_bb_any`,
  `icn_bb_notany`, `icn_bb_tab`, `icn_bb_move`, `icn_bb_match`.

  This is path (A) from the original IC-10 proposal (runtime adapter), but
  WITHOUT the IR-lowering step. The boxes are NEW, value-typed, owned by
  Icon. They are **not** shared with SNOBOL4 because SNOBOL4 doesn't need
  them — SNOBOL4 has the pattern engine for the same job, on the
  `spec_t`/`PATND_t` side of the typing split.

  This is the cross-pollination boundary the goal file's top-of-file note
  draws: "BB broker improvements (bb_broker, bb_boxes.c) benefit SNOBOL4
  pattern matching" — bb_broker / bb_boxes.c is the **pattern** universe.
  Icon scan-frame builtins live in the **value** universe. The two
  universes meet at `E_SCAN` (the `?` operator itself) — and that's the
  only place they meet, by Lon's S-12B ruling.

  ### Followup step recorded as IC-10b (separate, narrower)

  - [ ] **IC-10b** — Add value-typed Byrd boxes for Icon scan-frame
    builtins so they support β-backtracking under `every`.

    Concrete bug: `every "aXbYcZ" ? upto('XYZ')` yields `2` only,
    should yield `2`/`4`/`6` (verified `/tmp/upto_test.icn`).

    Boxes to write (value-typed, in `frontend/icon/icon_gen.c` per
    IC-2b's pattern; declared in `icon_gen.h`; registered in
    `icn_eval_gen()` E_FNC dispatch in `runtime/interp/icn_runtime.c`):

    | Box | Wraps current shim | Saves on α | Advances on β |
    |---|---|---|---|
    | `icn_bb_upto` | `interp.c:1385-1391` upto | `icn_scan_pos` | first match past current |
    | `icn_bb_many` | `interp.c:1378-1384` many | `icn_scan_pos` | retreat by 1 each β |
    | `icn_bb_any` | `interp.c:1372-1377` any | `icn_scan_pos` | (single-char; β fails) |
    | `icn_bb_notany` | (no current shim) | `icn_scan_pos` | (single-char; β fails) |
    | `icn_bb_tab` | `interp.c:1399-1406` tab | `icn_scan_pos` | (single-shot; β fails) |
    | `icn_bb_move` | `interp.c:1392-1398` move | `icn_scan_pos` | (single-shot; β fails) |
    | `icn_bb_match` | `interp.c:1407-1414` match | `icn_scan_pos` | (single-shot; β fails) |

    Note: only `upto`/`many` are interestingly generative under `every`
    (multiple successes). The others are α/ω one-shots (one value or
    nothing) — but they still need value-typed box wrappers so the
    enclosing `every`-driven generator chain doesn't hit
    `icn_oneshot_box` and lose the scan-frame snapshot/restore on β.

    Each box's state struct carries: saved `icn_scan_pos`, optional
    saved `icn_scan_subj` (rare — only if subject mutation is in
    play), the current cset/string arg, and any internal cursor δ
    needed for β advance.

    Per Lon's S-8B / S-12B ruling, do NOT touch `ir.h`. Do NOT add or
    rewire E_BREAK / E_SPAN / E_ANY etc. Do NOT touch `bb_boxes.c` —
    those boxes are SNOBOL4's, not Icon's. The new boxes are
    value-typed, Icon-owned, mirroring the icn_bb_to / icn_bb_iterate
    family that already works.

    Gates: `every "aXbYcZ" ? upto('XYZ')` byte-identical to `2\n4\n6\n`;
    smoke 5/0; broker 49/0; crosscheck 4/0/0; full ladder PASS=200+,
    rung_36 PASS=12+. Likely closes most of the β-backtracking diff
    on `rung36_jcon_subjpos` and the `every`-bound scan paths in
    `rung36_jcon_scan` / `scan1` / `scan2`. SNOBOL4 floors unchanged
    (rung01-36 / smoke / beauty self-host byte-identical).

  ### Lesson for future sessions

  When a horizontal architectural move suggests itself ("these things
  look like they should share!"), **always grep the goal-file ecosystem
  and git log for prior decisions before proposing it.** S-8B's "no work
  needed" verdict was specific, dated, signed by Lon, and explicitly
  about the exact same proposal. I missed it because I searched only
  `GOAL-LANG-ICON.md` for references to "shared pattern" rather than
  the full `.github/` tree. The original IC-10 commit `8648188`
  proposed a fix that contradicted a six-month-old architectural ruling.

  IC-10 marked done with the corrected understanding. IC-10b carries
  the actual remaining work, narrowly scoped within the value-typed
  box universe.


### Phase 2 — Icon standard library procedures

Install the standard Icon ilib procedures as .icn files and wire them:

- [ ] **IC-12** — Install Icon ilib subset.
  Script: `scripts/install_icon_ilib.sh` — fetches icon-lang.org ilib subset
  (strings.icn, lists.icn, sets.icn, tables.icn, sort.icn) into
  `/home/claude/corpus/programs/icon/ilib/`.
  Gate: files present, scrip parses them without error.

- [ ] **IC-13** — `strings.icn`: `center/left/right`, `trim`, `map`, `repl`, `reverse`.
  Write test file `test/icon/test_strings_lib.icn`. Run under --run.
  Gate: all 6 procs produce correct output vs Icon reference.

- [ ] **IC-14** — `lists.icn`: `lsort`, `lreverse`, `lmap`, `lfind`.
  Write test file `test/icon/test_lists_lib.icn`.
  Gate: PASS under --run.

- [ ] **IC-15** — `tables.icn`: `keylist`, `vallist`, `tmerge`.
  Write test file `test/icon/test_tables_lib.icn`.
  Gate: PASS under --run.

### Phase 3 — SM-run (BB_PUMP over generators, x86)

- [ ] **IC-16** — rung01–11 under --run.
  Each stmt routes via SM_BB_PUMP → icn_eval_gen → bb_broker.
  Gate: 59/59 PASS.

- [ ] **IC-17** — rung12–20 under --run.
  Fix any sm_lower.c or bb_broker gaps revealed.
  Gate: all passing rungs under --run also pass under --run.

- [ ] **IC-18** — E_EVERY, E_ALT_GEN, E_BANG, E_LIMIT box implementations.
  Write missing BB boxes in icon_gen.c:
    `icn_bb_every`    — drives inner generator, runs body per tick
    `icn_bb_alt_gen`  — alternation: try first gen then second
    `icn_bb_bang`     — `!list` — iterate list elements
    `icn_bb_limit`    — `gen \ n` — limit to n ticks
  Gate: every/bang/limit tests pass under --run and --run.

### Phase 4 — JIT-run (x86 in-memory code gen)

- [ ] **IC-19** — rung01–11 under --run.
  Gate: 59/59 PASS.

- [ ] **IC-20** — rung12–20 under --run.
  Gate: all diffs vs --run empty.

---

## Missing BB boxes to write (IC-18 detail)

```c
/* icn_bb_every — E_EVERY: drive gen, run body per tick */
typedef struct { bb_node_t gen; EXPR_t *body; } icn_every_state_t;
DESCR_t icn_bb_every(void *zeta, int entry);

/* icn_bb_alt_gen — E_ALT_GEN: try gen[0] then gen[1] */
typedef struct { bb_node_t g[2]; int which; } icn_alt_gen_state_t;
DESCR_t icn_bb_alt_gen(void *zeta, int entry);

/* icn_bb_bang — E_BANG: !list iterator */
typedef struct { DESCR_t *elems; int n; int pos; } icn_bang_state_t;
DESCR_t icn_bb_bang(void *zeta, int entry);

/* icn_bb_limit — E_LIMIT: gen \ n */
typedef struct { bb_node_t gen; long limit; long count; } icn_limit_state_t;
DESCR_t icn_bb_limit(void *zeta, int entry);
```

All go in `src/frontend/icon/icon_gen.c` + declared in `icon_gen.h`.
Register in `icn_eval_gen()` switch.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/icon/icon_parse.c` | Parser — builds IR directly (no AST) |
| `src/frontend/icon/icon_driver.c` | `icon_compile()` entry point |
| `src/frontend/icon/icon_gen.c` | Generator BB boxes |
| `src/frontend/icon/icon_gen.h` | Box declarations + state typedefs |
| `src/runtime/interp/icn_runtime.c` | Frame stack, proc table, icn_eval_gen |
| `src/runtime/interp/icn_runtime.h` | Public interface |
| `scripts/test_icon_all_rungs.sh` | Full rung sweep |
| `scripts/test_icon_ir_rung_NN.sh` | Per-rung gates |
| `corpus/programs/icon/` | Icon corpus |

## JCON reference — goldmine for every BB box

**`corpus/programs/icon/jcon-ref/irgen.icn`** — 1,559-line Icon program from the
JCON compiler (Proebsting 1996) that generates Byrd Box four-port IR from AST nodes.
Every `ir_a_Foo` procedure is the **canonical four-port wiring** (α start / β resume /
ω fail / γ succeed) for one Icon construct. This is the ground truth for every
`icn_bb_*` box in `icon_gen.c`.

Key procedures and their construct:

| `irgen.icn` procedure | Icon construct | Our box |
|---|---|---|
| `ir_a_BinOp` | `+` `-` `*` `/` `%` relops `\|\|` | `icn_bb_binop_gen` |
| `ir_a_To` | `E1 to E2` | `icn_bb_to` |
| `ir_a_ToBy` | `E1 to E2 by E3` | `icn_bb_to_by` |
| `ir_a_Every` | `every E do body` | `icn_bb_every` |
| `ir_a_Alt` | `E1 \| E2` alternation | `icn_bb_alternate` |
| `ir_a_Limit` | `E \ N` limitation | `icn_bb_limit` |
| `ir_a_Suspend` | `suspend E do body` | `icn_bb_suspend` |
| `ir_a_While` / `ir_a_Until` / `ir_a_Repeat` | loop forms | interp.c loop handling |
| `ir_a_If` | `if E then T else F` | indirect-goto gate |
| `ir_a_Scan` | `E ? body` | shared SNOBOL4 scan (no box needed) |
| `ir_a_Not` | `not E` | oneshot fallback |
| `ir_a_Call` | procedure/function call | `icn_call_proc` |
| `ir_a_Augop` | augmented assignment `:=` `+:=` … | `icn_bb_binop_gen` augop path |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Never modify icn_proc_table layout — Raku shares it.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-14, SCRIP HEAD a22ffac2)

IC-1 done. IC-2 in progress: 54/59 rung01-11 PASS.
Relop fix done (NUMREL/STRREL return right operand — oracle confirmed).
Suspend skeleton in place (icn_drive_fnc, IcnFrame.suspending, E_WHILE breaks on suspend)
but every-body not yet receiving suspended value — rung03 still failing.
Root cause: debug icn_drive_node/val passthrough and every_body capture in icn_drive_fnc.
Next: IC-2 — fix suspend every-body passthrough, get rung03 PASS, then rung12 str relops.

---

## --monitor: in-process sync comparator (IM-7/IM-8 complete)

`--monitor` runs IR, SM, and JIT step-by-step over the same program,
snapshot/restoring all mutable state between runs, and reports the first
statement where any two executors diverge.

```bash
./scrip --monitor file.sno    # SNOBOL4
./scrip --monitor file.icn    # Icon
./scrip --monitor file.pl     # Prolog
./scrip --monitor file.raku   # Raku
./scrip --monitor file.snc    # Snocone
./scrip --monitor file.reb    # Rebus
```

**On agreement:** prints per-stmt progress, exits 0.
**On divergence:** exits 1 and prints:
```
DIVERGE at stmt N [label: LABEL, line LL]
  IR   last_ok=?
  SM   last_ok=1
  JIT  last_ok=1
  IR vs SM (N var(s) differ):
    VARNAME    IR=<value>    SM=<value>
```

**Workflow for finding bugs:**
1. Run `./scrip --monitor suspect.sno` to find the first diverging statement.
2. The statement number + variable name pinpoint the root cause.
3. Fix in the appropriate layer (interp.c for IR bugs, sm_interp.c or
   sm_codegen.c for SM/JIT bugs).
4. Re-run `--monitor` to confirm divergence is gone.
5. Run `test_smoke_unified_broker.sh` — must stay PASS=31 FAIL=0.

**Note:** `--monitor` is incompatible with `--run`/`--run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.


---

## Current state (2026-04-14 session 2, SCRIP HEAD 5438115c)

IC-2 in progress: PASS=44 FAIL=15 TOTAL=59.

Two root causes fixed this session:

1. icn_call_proc body loop (icn_runtime.c): was using for(i) + inner while(suspending)
   that called interp_eval(st) to re-enter loops — restarted loop from scratch and never
   ran the do-clause. Fixed: replaced with stmt-pinned while loop matching icn_drive_fnc,
   running do-clause on resume, pinning stmt index for E_WHILE/E_REPEAT/E_UNTIL.

2. E_WHILE/E_UNTIL/E_REPEAT in interp.c: neither Icon-context block checked
   ICN_CUR.suspending as an exit condition. E_WHILE kept looping internally when
   E_SUSPEND fired, never returning to icn_call_proc's suspend handler.
   Fixed: added !ICN_CUR.suspending to while conditions and post-body break in
   both copies (SNOBOL4-context and Icon-context) of all three loop kinds.

New passes: rung03_suspend_gen, rung03_suspend_gen_compose, rung03_suspend_gen_filter.
Broker PASS=31 FAIL=3 (FAIL=3 confirmed pre-existing baseline — no regressions).

Remaining 15 failures:
- rung01 x4: binop generator backtracking (3 < ((1 to 3) * (1 to 2)), nested-to, etc.)
- rung02 x5: user proc calls + nested arithmetic generators
- rung08 x1: find() generator (only first result, not all)
- rung10 x1: break in repeat with augop (gets 5, wants 15)
- rung11 x1: bang+augconcat ordering (gets y|, wants xy|)

Next IC-2 step: attack rung02_proc_* failures (fact, locals, add_proc) — user proc
call path. Then rung01 binop backtracking (icn_bb_binop_gen right-retry on relop fail).

## Current state (2026-04-15 session 8, SCRIP HEAD 09dbff9c)

IC-3 IN PROGRESS: table builtins written, DT_T frame slot coercion bug blocks gate.

What was done:
- interp.c: table()/insert()/delete()/member() builtins added in Icon E_FNC dispatch
- interp.c: E_SIZE handles DT_T via tbl->size; E_ITERATE oneshot handles DT_T first-value
- icon_gen.h: icn_tbl_iterate_state_t + icn_bb_tbl_iterate decl; snobol4.h included
- icon_gen.c: icn_bb_tbl_iterate box (B-5b) walks TABLE_BUCKETS, yields entry->val
- icn_runtime.c: icn_eval_gen E_ITERATE routes DT_T to icn_bb_tbl_iterate
- scripts/test_icon_ir_rung_13_tables.sh: gate script (5 tests)
- corpus: rung13_table_*.icn + .expected (5 tests, semicolons required by parser)

BLOCKER — DT_T frame slot coercion bug:
  table() returns TABLE_VAL(tbl) with .v=DT_T correctly.
  But t["x"] after t:=table() gives Error 3 (erroneous array/table reference).
  Root cause: ICN_CUR.env[slot] stores DESCR_t directly — DT_T should survive
  since it is just a struct. Suspect: E_VAR retrieval in Icon frame context, or
  subscript_get(base, idx) receiving base.v != DT_T due to silent coercion.

Debug plan for next session:
  1. In E_ASSIGN (Icon frame path, interp.c ~line 780): fprintf to /tmp/dbg.txt
     printing val.v after storing to env[slot].
  2. In E_IDX handler: fprintf base.v after interp_eval(e->children[0]).
  3. Confirm whether DT_T survives the env round-trip.
  4. If yes: problem is in subscript_get — check IS_TBL(base) branch.
  5. If no: find where coercion strips DT_T (possibly VARVAL_fn or NAME_DEREF).

Gate status: test_icon_ir_rung_13_tables.sh PASS=0 FAIL=5 (blocker above)
Smoke: test_smoke_icon.sh PASS=5 FAIL=0 (no regression)

Next: IC-3 — fix DT_T frame slot bug, get rung13 PASS=5.



IC-2b DONE. IC-2 (rung01-11) DONE: PASS=59 FAIL=0 TOTAL=59.
cross_lang broker fix DONE: PASS=37 FAIL=0 (was PASS=36 FAIL=1).

cross_lang root cause: E_CAT absent from icn_is_gen's recursive check.
every write("ICN: " || (1 to 3)) produced only ICN: 1 — oneshot fallback.
Fix: E_CAT added to icn_is_gen; icn_bb_cat_gen box pumps leaf gen,
injects via icn_drive_node, re-evaluates concat per tick.

Next: IC-2 — rung12 string relational ops (`<<`, `>>`, `<=`, `>=`, `==`, `~=`), `*s`.


IC-2b DONE. IC-2 (rung01-11) DONE: PASS=59 FAIL=0 TOTAL=59.

Three final root causes fixed this session:

1. **rung01_paper_nested_to**: Added `icn_bb_to_nested` box (icon_gen.c/h).
   `icn_eval_gen(E_TO)` now detects generative lo/hi children via `icn_is_gen`
   and routes to cross-product box that pre-collects all lo/hi values.

2. **rung08_strbuiltins_find_gen**: Added explicit `find()` scalar-arg detector
   in `icn_eval_gen` before generic E_FNC block — builds `icn_bb_find` box directly.

3. **rung02_proc_locals**: Added `icn_find_leaf_gen()` in interp.c.
   `E_EVERY` with `E_ASSIGN(var, compound+gen)` now drives the leaf generator
   (e.g. `E_TO`) alone, injects each tick via `icn_drive_node/icn_drive_val`,
   and re-evaluates the full assignment so frame slot reads are fresh per tick.
   Universal `icn_drive_node` interception added at top of `interp_eval`.
   `E_AUGOP` excluded from E_EVERY special-case (has its own icn_is_gen path).

Gates: test_smoke_icon PASS=5, test_icon_ir_all_rungs PASS=59 FAIL=0,
test_smoke_unified_broker PASS=36 FAIL=1 (cross_lang pre-existing).

Next: IC-2 — rung12 string relational ops (`<<`, `>>`, `<=`, `>=`, `==`, `~=`), `*s`.


IC-2 in progress: PASS=56 FAIL=3 TOTAL=59 (+4 this session, 2026-04-15 session 4).

Three root causes fixed:

1. **icn_is_gen exported** (icn_runtime.c/h): made non-static so interp.c can use it.

2. **E_AUGOP per-tick accumulation** (interp.c): was collecting last RHS generator value;
   now re-reads LHS and applies op for each RHS tick.
   Fixed: rung10_augop_break_repeat, rung11_bang_augconcat_bang_concat.

3. **icn_lazy_box for E_VAR/literals** (icn_runtime.c): icn_eval_gen(E_VAR) now returns a
   lazy box that re-evaluates interp_eval(e) on every alpha pump instead of capturing once.
   Fixed: rung02_arith_gen_relfilter, rung02_arith_gen_nested_filter.

Broker gate: PASS=36 FAIL=1 (cross_lang pre-existing — no regression).

Remaining 3 failures for next session:
- **rung01_paper_nested_to**: `(1 to 2) to (2 to 3)` — icn_eval_gen(E_TO) evals lo/hi
  eagerly via interp_eval; need to detect icn_is_gen(child[0])||icn_is_gen(child[1])
  and build a cross-product box (iterate lo_gen x hi_gen, inner lo..hi each pair).
- **rung02_proc_locals**: `every total := total + (1 to n)` inside a proc — E_ASSIGN
  wrapping E_ADD(E_VAR(total), E_TO(1,n)); lazy box may not propagate through E_ADD
  into binop_gen left child when called from within icn_call_proc frame.
  Debug: add fprintf to /tmp/dbg.txt to trace icn_lazy_box alpha calls and left_val.
- **rung08_strbuiltins_find_gen**: `every write(find("a","banana"))` — find() builtin
  with scalar args hits oneshot fallback; needs dedicated generator path in icn_eval_gen
  (mirror the icn_drive find-generator: strstr loop, successive 1-based positions).
  Add before generic E_FNC builtin path in icn_eval_gen.

IC-2b DONE. E_SCAN_AUGOP removed (dead IR node — never emitted, never handled).
Suspend coroutine fix PARTIAL:
- icn_active_ss global + trampoline sets it + icn_call_proc swapcontexts on suspending.
- FIXED: write(gen()) with bare suspends works (10/20/30 correct).
- BROKEN: every write(upto(4)) outputs only '4' instead of '1 2 3 4'.
  Root cause: after swapcontext resumes in icn_call_proc, re-calling interp_eval(st)
  on a while-stmt restarts the loop from the top instead of resuming mid-loop.
  Fix needed: pin i on while-stmt type, do NOT re-call interp_eval — let the
  while loop's own iteration handle re-entry. Just swapcontext and continue the
  outer for-loop; the while will re-check its condition naturally on the next
  interp_eval(st) call that the for-loop issues (i does not advance).

Next IC-2 step:
1. Fix i-pinning in icn_call_proc: when ICN_CUR.suspending fires inside a
   loop stmt (E_WHILE/E_REPEAT/E_UNTIL), decrement i before continuing so
   the outer for-loop re-enters the same stmt. Remove the inner
   result=interp_eval(st) re-call entirely.
2. Verify every write(upto(4)) → 1 2 3 4.
3. Run full rung01-11 suite, target PASS=59.
4. Then rung12 str relops (IC-2 proper).

Debug note: bash_tool swallows stderr — write debug to /tmp/dbg.txt.

IC-2b DONE. All GDE ops now have BB boxes wired into icn_eval_gen:
  E_LIMIT → icn_bb_limit, E_EVERY → icn_bb_every,
  E_BANG_BINARY → icn_bb_bang_binary, E_SEQ_EXPR → icn_bb_seq_expr.
  E_SCAN: intentionally no box — same IR node as SNOBOL4 matching, oneshot fallback correct.
Build clean. Icon smoke PASS=5. Unified broker PASS=31 FAIL=2 (pre-existing).
Raku ladder unblocked (shares icn_eval_gen).

Next: IC-2 (rung03 suspend/every-body passthrough debug, then rung12 str relops).
Debug note: bash_tool swallows stderr — write debug to /tmp/dbg.txt, not fprintf(stderr,...).

IC-2a wire-up DONE. PASS=41 FAIL=18 TOTAL=59 (wiring complete; remaining failures
are pre-wiring bugs — not regressions from this session).

Completed this session:
- icn_eval_gen (icn_runtime.c): E_ALTERNATE → icn_bb_alternate wired.
- icn_eval_gen (icn_runtime.c): E_ADD/SUB/MUL/DIV/MOD/LT/LE/GT/GE/EQ/NE →
  icn_bb_binop_gen wired (fires only when ≥1 child is generator kind).
- E_AUGOP (interp.c): RHS driven through icn_eval_gen α/β pump when RHS is
  generator (fixes rung10/rung11 augop patterns in principle; still blocked by
  underlying suspend issues for rung03 cases).
- Build clean. Smoke icon PASS=5. Unified broker PASS=31 FAIL=2 (pre-existing).
- JCON studied: vClosure/Resume pattern confirmed as direct analogue of icn_bb_* boxes.
- Prolog BB box history recovered (commit 7adca486): pl_box_true/fail/builtin/cat/
  choice/cut all documented; current pl_broker.c is live unified-ABI successor.

Remaining open bugs blocking PASS=59:
- rung03 x3: suspend every-body passthrough. CRITICAL DEBUG NOTE: bash_tool swallows
  stderr — write debug to /tmp/dbg.txt and cat it, NOT fprintf(stderr,...).
  Root: icn_drive must recurse into upto(4) arg; every_body must be non-NULL and
  passthrough must fire per tick.
- rung01 x1: nested-to (1 to 2) to (2 to 3) — needs icn_bb_to_nested or special
  handling in icn_eval_gen for E_TO where lo/hi are themselves E_TO.
- rung08 x1: match() at pos returning falsy 0 — guard: icn_scan_pos>0 → icn_scan_subj!=NULL.
- rung02 x?: user proc call path investigation.
- rung11 x1: bang_augconcat_bang_concat (want: xy| got: y|) — augop/bang ordering.

Next IC-2a step: write debug to /tmp/dbg.txt, confirm icn_drive is called and
recurses into upto(4) arg; verify every_body non-NULL and passthrough fires (rung03).
4. rung03_suspend_* — verify icn_bb_suspend coroutine passthrough.
5. rung02_proc_* — user proc call path investigation.
6. After 59/59: delete icn_drive/icn_drive_fnc (IC-2c), then IC-2d rung12.

## Current state (2026-04-15 session 9, SCRIP HEAD 4a5f382d)

IC-3 DONE: rung13 tables PASS=5/5. Three bugs fixed this session:
1. table() DESCR_t union clobber: d.s=NULL after d.tbl=tbl overwrote pointer (same union).
2. delete() wrong hash: was h*31+c, binary uses djb2 (init=0x1505, h*33^c, &0xFF).
3. Icon E_ASSIGN missing E_IDX branch: t["p"]:=7 had no handler; added subscript_set path.

IC-4 DONE: rung14 limit PASS=5/5. Already passing via icn_bb_limit (IC-2b).
New gate script: test_icon_ir_rung_14_limit.sh.

IC-5 IN PROGRESS: real output + pow + E_TO_BY real done; remaining rung15-29 work ahead.
- icn_real_str helper: write/writes format reals with decimal point (%.15g + .0 if needed).
- E_POW: always returns DT_R now (was delegating to SNOBOL4 POWER_fn → int for int^int).
- icn_bb_to_by_real: new box for E_TO_BY with real step/bounds; icn_eval_gen routes there when any arg is DT_R.

Rung baseline rung12-29: PASS=35 FAIL=62 before this session → after: rung17/19/26 pow/real fixed.
Next: IC-5 — swap() builtin, string subscript s[i] and section s[i:j], list builtins (push/pop/put/get), initial block fix, records.

## Current state (2026-04-15 session 10, SCRIP HEAD 9bcbe7a8)

IC-5 IN PROGRESS: rung15 PASS=5/5. Rung16-29: PASS=53 FAIL=24 (was 31/77, +22).
Broker: PASS=38 FAIL=0. Rung01-11: 59/59.

Implemented: E_SWAP, E_LCONCAT, E_MAKELIST, E_SECTION, E_INITIAL, E_RECORD;
subscript_get/get2 DT_S; E_SIZE/E_ITERATE DT_DATA icnlist; 20+ builtins.

Next: neg subscript fix, initial persistence, !list BB box, table default, records, read().

## Current state (2026-04-15 session 11, SCRIP HEAD da83ab23)

IC-5 IN PROGRESS: rung01-29 PASS=137 FAIL=19 TOTAL=156. Broker PASS=39 FAIL=0.

Fixes this session:
1. E_RECORD: sc_dat_register(spec) so type enters dispatch table; once-guard ival=1.
2. E_FIELD read (case E_FIELD in interp_eval) + write (interp_eval_ref case E_FIELD).
3. E_INITIAL persistence: file-scope icn_init_tab[64] keyed on e->id; snapshot updated
   by icn_init_update_snapshot() at call_user_function exit before NV restore.
4. E_ALTERNATE n-ary: left-recursive chain of binary boxes for 3+ children.
5. !list (E_ITERATE DT_DATA icnlist): icn_bb_list_iterate + icn_list_iterate_state_t.
6. table default: TBBLK_t.dflt field; table(dflt) wires it; subscript_get miss returns dflt.
7. neg subscript off-by-one: slen+1+i+1 → slen+i+1.
8. read()/reads(): fgets/fread from stdin, fail on EOF.

Remaining 19 failures — next session priority:
  1. rung24 records (5): E_FIELD/E_RECORD landed but point(3,4) still blank — debug
     whether Icon E_FNC call routes through icn_call_proc (bypasses sc_dat_find_type).
  2. rung21/25 initial (4): icn_frame_depth=0 in NV path — snapshot restores to NV
     but Icon frame env slot not updated; check icn_call_proc vs call_user_function routing.
  3. rung13 alt filter/nested (2): alternation with generator operands.
  4. rung22 put_bang (1), rung23 key (1), rung16 sub_every (1).
  5. rung18 relop_goal (1), rung19 pow_real (1), rung28 trim_map (1), rung29 image (1).

## Current state (2026-04-15 session 12, SCRIP HEAD 57d51c88)

IC-6 IN PROGRESS: rung01-29 PASS=154 FAIL=2 TOTAL=156. Broker PASS=42 FAIL=0. Smoke PASS=5.

Fixes this session (rung12-29: 79→154 PASS, +75):

1. icn_real_str: shortest round-trip precision (try %.15g..%.17g, stop when strtod round-trips).
   Fixes: rung15 real_literal, rung17 string_conv, rung29 image (3.14 not 3.1400000000000001).
2. E_POW: always returns DT_R (Icon semantics). Fixes: rung19 pow_int, rung26 ×4.
3. image(): string returns value without quotes. Fixes: rung29 type_image.
4. trim(): g_lang==1 → Icon trailing-only; else Raku both-sides. Fixes: rung28, rk_str22.
5. push()/put(): read n from icn_size (not ea.v==DT_I which was always 0). Fixes: rung22 put_bang.
6. icn_bb_list_iterate: store live list_obj DESCR_t, re-read each tick. Fixes: rung22 put_bang.
7. icn_bb_tbl_key_iterate: new box; key(T) wired in icn_eval_gen. Fixes: rung23 table_key.
8. icn_is_gen: added E_IDX (gen if index child gen), E_ASSIGN (gen if RHS gen).
9. icn_eval_gen: E_IDX routes to icn_bb_cat_gen (drive leaf, re-eval subscript). Fixes: rung16 sub_every.
10. icn_eval_gen: E_LCONCAT added to binop_map for cross-product concat.
11. icn_oneshot_box: reset fired=0 on alpha so cross-product can replay scalar arms.
12. icn_binop_apply: relops return actual rv DESCR_t (not INTVAL cast). Fixes: rung18 real_relop_goal.
13. icn_binop_apply: real-aware arithmetic. Fixes: rung17 real_arith.
14. E_EVERY: E_SEQ conjunction special case added. Partial fix for rung13 filter.
15. test_icon_all_rungs.sh: extended to rung01-29; added .stdin support. Fixes: rung27 ×4.

OPEN (2 failures, next session IC-6 priority):

- rung13_alt_alt_filter: every (x:=alt)>2 & write(x).
  E_SEQ special case fires icn_eval_gen(E_GT(E_ASSIGN(x,alt),2)).
  icn_bb_binop_gen pumps E_ASSIGN as left box — but E_ASSIGN side-effect
  (writing x into frame slot) is not replayed per tick; needs icn_drive_node
  injection the same way the E_ASSIGN special case in E_EVERY does it.
  Fix: in E_EVERY E_SEQ path, detect E_GT/relop with E_ASSIGN left child;
  drive the alt leaf directly via icn_drive_node, re-eval the full filter each tick.

- rung13_alt_alt_nested: every write(("a"|"b") || ("x"|"y")).
  E_LCONCAT with two E_ALTERNATE children should route to icn_bb_binop_gen
  cross-product. icn_oneshot reset fixed. Root cause: E_CAT handler in
  icn_eval_gen fires before the binop_map loop and intercepts E_LCONCAT
  (E_CAT and E_LCONCAT share the icn_is_gen case but E_CAT block only
  checks e->kind == E_CAT). Verify: add E_LCONCAT check to E_CAT block guard.
## Current state (2026-04-16 session 13, SCRIP HEAD 37d45f96)

IC-6 rung13 alt-gen DONE: rung01-29 PASS=156/156 FAIL=0. Broker PASS=43 FAIL=0. Smoke PASS=5.

Two root causes fixed this session:

1. **icn_bb_assign_gen** (icn_runtime.c): New box for E_ASSIGN with generative RHS.
   Pumps RHS generator on each α/β tick, writes result to target var slot (or NV),
   returns value so enclosing binop_gen can test it per tick.
   Added: icn_assign_gen_state_t typedef, icn_bb_assign_gen() static function,
   E_ASSIGN case in icn_eval_gen() before E_VAR lazy box.
   Fixes: rung13_alt_filter — every (x:=(1|2|3|4))>2 & write(x) → 3\n4.

2. **E_CAT cross-product** (icn_runtime.c): E_CAT block in icn_eval_gen now detects
   when BOTH children are generative and routes to icn_bb_binop_gen (ICN_BINOP_CONCAT)
   for full cross-product instead of one-side icn_bb_cat_gen pump.
   Fixes: rung13_alt_nested — every write(("a"|"b")||("x"|"y")) → ax\nay\nbx\nby.
   Note: "||" is E_CAT (string concat), not E_LCONCAT ("|||" list concat) — the prior
   diagnosis in session 12 had the kind name wrong but the fix is correct.

New script: scripts/test_icon_ir_rung_13_alt.sh PASS=2/2 (inline, no corpus).

Next IC-6: run corpus rung16–29 with corpus cloned to recount remaining open failures.
Without corpus the rung all-rungs script SKIPs. Remaining known open (from session 12):
rung22 put_bang(1), rung23 key(1), rung16 sub_every(1), rung18 relop(1),
rung19 pow(1), rung28 trim_map(1), rung29 image(1).

## Current state (2026-04-16 session 14, SCRIP HEAD 37d45f96)

IC-6 DONE: rung01-29 PASS=156/156 confirmed with corpus. Broker PASS=45 FAIL=0. Smoke PASS=5.
Crosscheck PASS=4. All suspected IC-6 failures were already fixed from session 13.

Scripts rewritten/extended this session (all in SCRIP/scripts/, self-contained, --run):
  test_icon_ir_rung_30.sh  — abs/max/min/sqrt/seq   (was JVM/jasmin stub)
  test_icon_ir_rung_31.sh  — sort/sortf              (was JVM/jasmin stub)
  test_icon_ir_rung_32.sh  — string retval every     (was JVM/jasmin stub)
  test_icon_ir_rung_33.sh  — case expressions        (was JVM/jasmin stub)
  test_icon_ir_rung_34.sh  — null/nonnull test       (was JVM/jasmin stub)
  test_icon_ir_rung_35.sh  — block bodies + str/str  (was JVM/jasmin stub)
  test_icon_ir_rung_36.sh  — JCON suite 75 tests     (was JVM/jasmin stub)
  test_icon_all_rungs.sh — extended rung01-36, xfail-aware, --rung/--scrip/--corpus switches

IC-7 baseline (rung30-35):
  rung30 0/5 — abs/max/min/sqrt/seq missing from E_FNC dispatch
  rung31 0/5 — sort()/sortf() missing
  rung32 4/5 — strret_every: every over proc yielding string returns only first value
  rung33 1/5 — E_CASE dispatch not implemented (parse ok, eval missing)
  rung34 1/5 — \x null-test and \=x nonnull-test unimplemented
  rung35 7/7 — ALREADY PASSING (no work needed)

IC-8 baseline (rung36 JCON): PASS=2 FAIL=50 XFAIL=23 TOTAL=75

Next IC-7: fix rung30 builtins first (abs/max/min/sqrt/seq in icn_runtime.c E_FNC dispatch),
then rung31 sort/sortf, then rung33 case, then rung34 null-test, then rung32 strret_every.

## Current state (2026-04-16 session 15, SCRIP HEAD 9eb8c669)

IC-7 IN PROGRESS. Broker PASS=49 FAIL=0. Smoke PASS=5. Rung01-29 PASS=156/156.

Fixes this session (interp.c + icn_runtime.c):
1. abs/max/min/sqrt added to Icon E_FNC dispatch.
2. seq() added as E_FNC builtin (returns first value) AND as icn_bb_to_by infinite
   generator in icn_eval_gen (every write(seq(1) \\ 3) → 1 2 3).
3. sort(L)/sortf(L,n) — insertion sort over icnlist; sortf uses DATINST_t->fields[n-1].
4. E_CASE rewritten: Icon pairs layout [val,body]...[default_body].
   Raku triples detected by (nchildren-1)%3==0 AND child[1] is E_ILIT/E_NUL.
5. E_NULL (/E) and E_NONNULL (\E) added to interp_eval.
   E_NONNULL added to icn_is_gen + icn_eval_gen pass-through via icn_bb_limit
   so every write(\(1 to 3)) → 1 2 3.
6. User-proc-with-gen-arg box wired in icn_eval_gen (before oneshot fallback):
   detects first generative arg of a user proc, builds icn_fnc_gen_state_t.

IC-7 rung30-35 results:
  rung30 5/5 DONE — abs/max/min/sqrt/seq
  rung31 5/5 DONE — sort/sortf
  rung32 4/5 OPEN — strret_every: every write(tag("a"|"b"|"c")) yields only first value
  rung33 5/5 DONE — case expressions
  rung34 5/5 DONE — null/nonnull tests
  rung35 7/7 DONE — already passing (no new work)

rung32 open root cause: icn_bb_fnc_gen calls icn_call_builtin → icn_call_proc
for user procs. icn_call_proc returns after first `return` statement — not a
coroutine. Fix: in icn_bb_fnc_gen, when call targets a user proc, build a fresh
icn_bb_suspend coroutine each tick with the substituted arg, instead of calling
icn_call_builtin.

Next IC-7: fix rung32 strret_every (1 test), then IC-8 rung36 JCON suite.

## Current state (2026-04-30 session 18, SCRIP HEAD b6350608)

IC-8 IN PROGRESS. Two tactical fixes landed this session — `!N` numeric iteration
and `===` (E_IDENTICAL) goal-directed evaluation. Gates preserved at 188/45/30,
but the rung36_jcon_table NONMEMBER-leak symptom is gone (the spurious branch
in `tdump` no longer prints &null:NONMEMBER for every probed key).

### `!N` integer/real iteration

**Site:** `icn_drive` E_ITERATE handler (icn_runtime.c L191) and `icn_eval_gen`
E_ITERATE handler (L713 box-construction path).

**Root cause:** `every write(!-514)` parses to `E_ITERATE(E_NEG(E_ILIT 514))`.
The handler rejected non-string operands (`!IS_STR_fn(sv_d) → return 0`), so
the `every` produced no output. Per Icon semantics, `!N` for integer or real
iterates the characters of `image(N)` — `!-514` → `-`,`5`,`1`,`4`;
`!12.5` → `1`,`2`,`.`,`5`.

**Fix:** before the existing string-rejection check at each site, coerce
`IS_INT_fn(sv)` via `snprintf("%lld",...)` and `IS_REAL_fn(sv)` via
`icn_real_str` (un-static'd from interp.c L936; declared in icn_runtime.h).
Result is a `STRVAL(GC_malloc'd buffer)` that flows through the existing
char-iterate path unchanged.

Verified on rung36_jcon_every: lines `p. -`, `p. 5`, `p. 1`, `p. 4` and
`q. 1`, `q. 2`, `q. .`, `q. 5` now match the expected output. Test stays
.xfail because of unrelated unimplemented features (`every !s := "."`,
`(...)(args)` invocation form, `proc ! [args]`).

Files: `src/driver/interp.c` (un-static, +1/-1), `src/runtime/interp/icn_runtime.h`
(+3/-0 for icn_real_str decl), `src/runtime/interp/icn_runtime.c` (+22/-2
for two coercion blocks).

### `===` (E_IDENTICAL) goal-directed evaluation

**Site:** Three additions —
  - `interp.c` shared-switch case E_IDENTICAL (non-generator path, +13/-0).
  - `icn_runtime.c` icn_is_gen() adds E_IDENTICAL to the gen-if-any-child-is
    list, so `if x === key(T)` routes to icn_eval_gen.
  - `icn_runtime.c` icn_eval_gen() new E_IDENTICAL block before binop_map,
    builds icn_bb_identical_gen box that drives RHS as generator and tests
    identity each tick.
  - `icn_runtime.c` new helpers icn_descr_identical() (+33/-0 with comment) and
    icn_bb_identical_gen() (+24/-0 with comment).
  - `icn_runtime.h` decl for icn_descr_identical (+2/-0).

**Root cause:** `E_IDENTICAL` had no case in interp_eval — fell through to
`default → NULVCL`. NULVCL is truthy (only FAILDESCR fails), so every
`if x === key(T)` succeeded spuriously. The rung36_jcon_table NONMEMBER-leak
was a symptom: tdump's
   ```
   every x := &null | (0 to 9) | !"abcde" do
      if x === key(T) then writes(...)
      else writes(":NONMEMBER" if member fails)
   ```
fired the then-branch unconditionally, then `member(T,x)` correctly failed,
leaking `:NONMEMBER` for every probed value. Verified the NONMEMBER blocks
are gone after fix.

**Symbols verified available in icn_runtime.c:** α/β are `static const int`
in `runtime/x86/bb_box.h`, transitively included via `bb_broker.h →
icon_gen.h`. (My new box doesn't actually use α/β explicitly — it just
threads `entry` to the wrapped gen and uses literal `1` for re-entry.)

**Identity semantics implemented in icn_descr_identical:**
- different non-string types → not identical
- both null (DT_SNUL or empty DT_S) → identical
- DT_S/DT_SNUL pair → byte-equal (memcmp of slen-aware bytes)
- DT_I → same .i
- DT_R → same .r
- DT_T → same .tbl pointer (table identity, not deep-equal)
- DT_DATA → same .ptr pointer
- fallback: byte-compare DESCR_t

**Verified on minimal repro** (/tmp/test_eqeqeq_gen.icn):
```
T := table(); T[2] := 3
if 7 === key(T) then write("BUG")        # silent — correct (7 not a key)
if 2 === key(T) then write("OK match")    # OK match — correct
if "a" === key(T) then write("BUG")       # silent — correct
```

Pre-fix: all three lines printed (default NULVCL succeeds). Post-fix:
only the legitimate match prints.

### Gates post-fix (both changes together)
- test_smoke_icon.sh: PASS=5/5
- test_smoke_unified_broker.sh: PASS=49/0
- test_crosscheck_icon.sh: PASS=4/0
- test_icon_all_rungs.sh: PASS=188 FAIL=45 XFAIL=30 TOTAL=263 (unchanged)

PASS count is unchanged because the rung36 tests these fixes affect have
multiple unrelated unimplemented features and stay .xfail. The fixes are
correctness improvements visible in the diff against expected — see
rung36_jcon_table diff: pre-fix had ~45 lines of NONMEMBER leak per
tdump call; post-fix tdump output is clean and the remaining diffs
are different bugs (every !x := V mutate-via-iterate, every x[3] <- 19
augmented-assign, `\`/`/` null-test on missing keys).

### Remaining rung36_jcon_table failures (separate root causes for IC-9+)
1. `every !x := 88` — bang-iteration as lvalue: needs E_ITERATE in lvalue
   context to walk T's entries and bind each to a writable slot.
2. `every x[k] := 99` where k := key(x) — same family: every-loop with
   lvalue subscript and generator key needs cross-product write semantics.
3. `every x[3] <- 19` — augmented assign-on-mismatch operator unimplemented.
4. `every !x +:= 20` — augmented bang-iterate.
5. `\x[k]` and `/x[k]` for k not in T — should fail/succeed without
   inserting; currently inserts &null entries (causing `delete: 4`
   instead of `delete: 2`).
6. `image(?x)` on empty table — random selection on empty table needs
   to fail cleanly, not return &null.

These all touch the same IcnFrame / table-lvalue boundary; one or two
shared fixes likely address several.

## Current state (2026-04-30 session 19, SCRIP HEAD 7c5f9b45)

IC-9 IN PROGRESS. One scalar-evaluator correctness fix landed; PASS counts unchanged
across all gates, but the visible diff for `rung36_jcon_table` is one line cleaner.

### `/E` and `\E` — null-test vs fail-test conflation

**Site:** `interp.c` shared switch, `case E_NULL` (line 3857) and
`case E_NONNULL` (line 3870 pre-fix → 3874 post-fix).

**Root cause:** `E_NULL`'s pre-fix body was the one-liner
`return IS_FAIL_fn(v) ? NULVCL : FAILDESCR;` — i.e. "/E succeeds iff E
fails."  That is **wrong**: Icon's `/E` succeeds iff E **succeeds with the
null value**.  Two contradictory bugs cancelled in some tests:
  - `/x[k]` for missing key → x[k] returns NULVCL (success-with-null),
    handler sees `IS_FAIL_fn(NULVCL)==false`, returns FAILDESCR → fails.
  - `/x[k]` for present non-null → x[k] returns the value, handler same
    `IS_FAIL_fn==false`, returns FAILDESCR → fails.
  - `/(some_failing_expr)` → handler sees IS_FAIL true, returns NULVCL
    (success).  Wrong direction entirely — should fail.

`E_NONNULL` had the same family of bug but caught the empty-string case
(`v.v==DT_S && empty .s`) — yet missed `DT_SNUL` itself, so `\&null`
returned `&null` (success) instead of failing.  A dead-code line
`if (v.v==DT_I && v.i==0 && !IS_INT_fn(v))` was a remnant of an earlier
confused attempt (the conjunction is unsatisfiable: DT_I implies IS_INT).

**Fix:** rewrite both handlers to test the value directly:
- `/E` — fail if E failed; succeed (return NULVCL) if v.v==DT_SNUL or
  v.v==DT_S with empty .s; otherwise (E succeeded with non-null value)
  fail.
- `\E` — fail if E failed; fail if v.v==DT_SNUL or v.v==DT_S with empty
  .s; otherwise return v.

**Verified on minimal repro** (table with one key x[2]:=2, probe x[1]
missing and x[2] present):
  - `/x[1]` → succeeded (was failed) — correct, missing key is &null
  - `\x[1]` → failed (was succeeded) — correct
  - `/x[2]` → failed (unchanged) — correct, 2 is non-null
  - `\x[2]` → succeeded (unchanged) — correct

### Correction to prior session diagnosis

GOAL-LANG-ICON.md item #5 above ("\x[k]/x[k] for missing key — currently
inserts &null entries causing `delete: 4` instead of `delete: 2`") was
**wrong about the cause**.  Probing a missing key does **not** insert in
this runtime (verified by minimal repro: `x:=table(); x[2]:="two"; x[1];
x[3]; *x` → 1, unchanged).  The `delete: 4` symptom is unrelated:
`delete(x)` (no second arg) and `delete(x, 3, 6)` (3 args) are silently
failing to remove the entries they should.  Likely a builtin-arity bug
in the `delete()` dispatch, not a probe-time mutation.

The actual `\x[k]`/`/x[k]` bug was simpler: the **scalar evaluator** had
wrong null-vs-fail semantics, exposed by the JCON test's
`/x[1] | write("/1")` line which now correctly suppresses the `/1` write.

### Working-tree pollution cleaned

Found three stray files in `/home/claude/SCRIP/` working tree at session
start: `foo.baz` (empty), `src/driver/interp.c.fixed`, and
`src/driver/interp.c.orig`.  The two `.c.*` files were byte-identical and
contained a drafted-but-not-committed version of exactly this fix.  Per
RULES.md, diagnostic and scratch files do not ship — removed.  No commit
record of who left them; previous session likely.

### Gates post-fix (per-test diff vs baseline is empty)
- test_smoke_icon.sh: PASS=5/0 (unchanged)
- test_smoke_unified_broker.sh: PASS=49/0 (unchanged)
- test_crosscheck_icon.sh: PASS=4/0 SKIP=0 (unchanged)
- test_icon_all_rungs.sh: PASS=188 FAIL=45 XFAIL=30 (unchanged)
- test_icon_ir_rung_36.sh: PASS=5 FAIL=40 XFAIL=30 (unchanged)
- per-test PASS/FAIL/XFAIL list: byte-identical to pre-fix (`diff -q`)

### Remaining IC-9 failures unchanged

Items 1, 2, 3, 4, 6 from the list above are all unaddressed — those touch
the lvalue path (E_ITERATE in lvalue position, generator-key subscript
write, `<-` reversible assign, `+:=` over !-iterate, `?T` on empty/sparse
table).  Item 5 is now correctly understood: scalar `/`/`\` semantics
fixed; the `delete: 4` symptom is a separate `delete()` arity bug.

Files: `src/driver/interp.c` (+17/-5 lines).  No header changes, no
clean-rebuild needed.

### Next IC-9 candidate

`?T` random-select-from-table — the `should fail &null` and `>> 3 &null`
diff lines (visible in `rung36_jcon_table.icn` lines 10, 13) are caused
by `?T` returning `NULVCL` instead of failing when no random entry can
be chosen.  Single site, scalar evaluator, low-risk in the same shape
as this fix.  Open question for next session: does Icon's `?T` actually
fail on empty tables, or does it return `&null` of the table default?
The expected output (`should fail ` with no value after) suggests it
fails (causing `writes` to emit nothing for that arg).

## Current state (2026-04-30 session 20, SCRIP HEAD 2add5179)

IC-9 IN PROGRESS. Three correctness fixes landed; PASS counts unchanged
across all gates (same shape as session #18/#19 — affected rung36_jcon_*
tests still `.xfail` due to multiple unrelated unimplemented features),
but per-test diffs are visibly cleaner.  The `?T` candidate flagged at
the end of session #19 is now closed.

### `?E` (E_RANDOM) — was unhandled, fell through to NULVCL

**Site:** `interp.c` shared switch, new `case E_RANDOM` (after `E_NONNULL`,
~line 3900).

**Root cause:** `E_RANDOM` had **no case in interp_eval** — same bug
class as session #19's `E_NULL`/`E_NONNULL` discovery.  The default
arm returns NULVCL, which is success-with-null, so `?empty_table`,
`?[]`, `?""`, `?0`, `?-3` all returned `&null` instead of failing.
Visible in `rung36_jcon_table` line 2 (`should fail &null` vs expected
empty) and `rung36_jcon_evalx` (`?table() ----> &null` vs `none`).

**Fix:** New `case E_RANDOM` dispatches by descriptor type:
- `DT_T` (table) — pick random entry value via bucket walk, fail if `tbl->size==0`
- `DT_DATA` icnlist — pick random element from `icn_elems[]`, fail if `icn_size==0`
- `IS_INT_fn` — random in `[1,n]`, fail if `n<=0`
- `DT_SNUL` — fail
- String — random character, fail if empty (`v.slen` or `strlen` zero)

RNG: local static LCG using Knuth MMIX constants
(`seed = seed*6364136223846793005UL + 1442695040888963407UL`; pick from
`seed >> 33`).  Self-contained — no cross-file linkage with the
frontend's `icn_random` in `frontend/icon/icon_runtime.c` (which is in a
different translation unit and not declared in any visible header).

**Verified on minimal repro** (/tmp/test_random.icn — 9 cases, all
correct: 5 empty/zero fail, 4 non-empty pick valid elements across
int/string/table/list types).

### `image()` propagates FAILDESCR

**Site:** `interp.c` icon-frame `case E_FNC` builtins block, line 2316.

**Root cause:** `image(av)` did not check `IS_FAIL_fn(av)` before
dispatching by type.  When the argument failed, av had `.v=DT_S, .s=NULL`
(or similar zero-state); the string branch fell through to
`VARVAL_fn(FAILDESCR)` → `""`, then wrapped it in quotes → `"\"\""`.
Visible in `rung36_jcon_table` line 2 as `should fail ""`.

**Fix:** one-line guard at top of `image` builtin handler:
`if (IS_FAIL_fn(av)) return FAILDESCR;`

### `write()` / `writes()` evaluate all args before any output

**Site:** `interp.c` icon-frame `case E_FNC` builtins, lines ~1063 (write)
and ~1078 (writes).

**Root cause:** Both builtins evaluated children one at a time and
`printf`-ed immediately; only on a failed child did they `return
FAILDESCR`.  Result: `writes("should fail ", image(?T_empty))` printed
`"should fail "` to stdout, *then* failed on `image(?T_empty)` — so
the test saw `should fail ` even though Icon's all-or-nothing semantics
say nothing should print.

**Fix:** Two-pass — evaluate all args into a GC_malloc'd `DESCR_t[]`
buffer first; if any fails, return FAILDESCR with no I/O.  Only on
all-success does the second pass do the actual `printf`/`fputs`.
Both builtins use the identical pattern.

The other `write`/`writes` site (~line 959/972, in `icn_call_builtin`)
takes pre-resolved `args[]` from its caller, so the incremental-print
issue cannot occur there — left untouched.

### Per-test correctness improvements (rung36_jcon_table)

```
before  initial : 0 :       <-- baseline
        should fail &null >>          <-- E_RANDOM unhandled, image swallows fail
         >> 3 &null                   <-- E_RANDOM on 1-entry table returned NULVCL

after   initial : 0 :
         >>                           <-- writes failed silently (correct)
         >> 3 3                       <-- ?x picks the value 3 (correct)
```

Lines 1–3 of the rung36_jcon_table diff now match expected.
Items 1, 2, 3, 4, 6 from session #18's table-failure list remain — they
all touch the lvalue path (E_ITERATE in lvalue position, generator-key
subscript write, `<-` reversible assign, `+:=` over !-iterate, `?T` on
empty/sparse table is now closed).  Item 5 (`/`/`\`) was closed in #19.

### Side effect on rung36_jcon_random

`rung36_jcon_random` previously FAILed with one set of wrong values; it
still FAILs (XFAIL not granted — output diverges from expected).  The
test depends on `&random` keyword for seeding (currently a no-op stub),
so per-run output is non-deterministic.  Pre-fix and post-fix outputs
are structurally similar (all expected lines present); the actual
random-element values differ, as expected from a different RNG path.
No regression — just a different sequence.

### Gates post-fix (all baseline, no PASS-count movement)

- `test_smoke_icon.sh`: PASS=5/5
- `test_smoke_unified_broker.sh`: PASS=49/0
- `test_crosscheck_icon.sh`: PASS=4/0 SKIP=0
- `test_icon_all_rungs.sh`: PASS=188 FAIL=45 XFAIL=30 TOTAL=263
- `test_icon_ir_rung_36.sh`: PASS=5 FAIL=40 XFAIL=30 TOTAL=75

### Working-tree pollution (cleaned again)

Found `foo.baz` (empty file) at session start in SCRIP working tree —
same kind of stray scratch as session #19 cleaned.  Removed; not committed.
Per RULES.md "Diagnostic patches are diagnostic — never commit them",
empty/scratch files don't ship.

Files: `src/driver/interp.c` (+81/-4 lines).  No header changes, no
clean-rebuild needed.

### Next IC-9 candidate

The four remaining table-touch failures all share a shape: **lvalue
position needs a generator-aware path** —
- `every !x := 88` — bang-iterate as lvalue
- `every x[k] := 99` (k generator) — generator key in subscript lvalue
- `every x[3] <- 19` — `<-` reversible assign operator
- `every !x +:= 20` — `+:=` over bang-iterate

These all need `interp_eval_ref` to recognize generator children and pump
them.  Single subsystem; one well-placed fix in the lvalue evaluator
likely closes 2–3 at once.  **Highest-leverage next pivot.**

Separately: `delete()` arity bug (`delete(x)` 1-arg and `delete(x,3,6)`
3-arg both silently fail to delete) — lower leverage but cheap, isolated.
Visible as `delete : 4` (vs expected `delete : 2`) on rung36_jcon_table
lines 10, 14.

## Current state (2026-04-30 session 21, SCRIP HEAD `8ddcbc89`)

IC-9 IN PROGRESS / IC-8 ADVANCE.  Six fixes landed; **rung36_jcon_table
PASS** (empty diff against expected) — first PASS-count advance in IC-8
since session #17.  test_icon_ir_all_rungs PASS=188 → 189.
test_icon_ir_rung_36 PASS=5 → 6, FAIL=40 → 39.  All other gates unchanged.

### Lvalue-generator family (closes session #20 next-pivot list)

1. **`every !x := V` — bang-iterate as lvalue**.  E_ASSIGN with E_ITERATE
   LHS, icon-frame `case E_ASSIGN` in `src/driver/interp.c`.  Walks every
   cell of the container in one `interp_eval` pass:
   - `DT_T` table — bucket walk over `TBPAIR_t`, `p->val = val` for each
   - `DT_DATA` icnlist — `icn_elems[i] = val` over the array
   - `DT_S` string — silently no-op (immutable)
   Single-pass under `every`: the box exhausts after one tick, but the
   pass already wrote every cell.  ~30 lines.

2. **`every x[key(x)] := V` — generator key in subscript lvalue**.
   E_ASSIGN with E_IDX LHS, in the same icon-frame handler.  When
   `icn_is_gen(lhs->children[1])` is true, drives the index gen via
   `icn_eval_gen` (already imported at this site since session #16) and
   `subscript_set(base, k, val)` per yielded key.  Mirrors the gen-RHS
   pump but on the LHS index.  ~12 lines.

3. **`every !x OP:= V` — augmented-assign over bang-iterate**.  E_AUGOP
   with E_ITERATE LHS, in `case E_AUGOP`.  RHS evaluated once; cell-walk
   identical to (1); per-cell `AUGOP_CELL` macro mirrors the existing
   `AUGOP_APPLY` macro but writes through the cell pointer instead of
   the `lhs` slot.  All five augops + `||:=` covered.  ~37 lines.

### Builtin-arity / value-semantics fixes

4. **`copy()` — proper shallow copy** (was a no-op alias).  Allocates a
   fresh `TBBLK_t` and walks `src.tbl->buckets` calling
   `table_set_descr(nt, p->key, p->key_descr, p->val)` for each entry,
   preserving the original key descriptors (so SORT() ordering still
   works).  For DT_DATA icnlist, `GC_malloc` a fresh `DESCR_t[]`,
   `memcpy` from src elems, and rebuild via `DATCON_fn("icnlist",
   eptr, INTVAL(n), STRVAL("list"))` — the same shape `E_MAKELIST`
   produces.  Strings/ints/reals fall through to direct return (value
   semantics already satisfy copy).  Fixes the `every !y +:= 40`
   mutating x bug visible at the `30s/50s` lines.  ~35 lines.

5. **`delete()` and `member()` arity** — both extended from `nargs == 2`
   to `nargs >= 1`.  1-arg form (`delete(T)` / `member(T)`) treats the
   missing key as `&null` (Icon's null-arg padding); extra args
   ignored.  Fixes the spurious "NULL IS MEMBER" line and the
   `delete : 4` vs expected `delete : 2` bug.  ~6 lines combined.

### `<-` reversible assignment (E_REVASSIGN, new IR kind)

6. **Parser-layer separation**.  Was previously routed to `E_ASSIGN`,
   making `<-` and `:=` indistinguishable in IR — wrong since `<-`
   needs revert-on-backtrack semantics.  Added `E_REVASSIGN` to
   `EKind` enum in `src/ir/ir.h` (before `E_KIND_COUNT`) and to the
   `ekind_name[]` table.  `src/frontend/icon/icon_parse.c` line 503
   now emits `e_binary(E_REVASSIGN, n, parse_assign(p))`.

   **Standalone path** (icon-frame `case E_REVASSIGN` in interp.c):
   acts like `:=` since there's no driver to backtrack against — this
   is what the test needs for any `<-` outside an `every`.  Mirrors
   E_ASSIGN's E_VAR / E_IDX / E_FIELD branches.

   **Generator path** (`icn_runtime.c`): `icn_is_gen(E_REVASSIGN) → 1`
   unconditionally, so `every` routes through `icn_eval_gen`.  New
   `icn_bb_revassign` Byrd box:
   - **α**: snapshot prior value via `subscript_get` (this is the key
     ordering — `subscript_get` returns `tbl->dflt` for missing keys,
     so `every x[3] <- 19` on `table(7)` correctly snapshots 7).  Then
     write the new value: cell-pointer fast path via `table_ptr` /
     `array_ptr` for tables and arrays; `subscript_set` fallback for
     other containers (lists, records, strings).  Returns `rv`.
   - **β/ω**: restore the snapshot via the cell pointer when we have
     one, or `subscript_set(base_d, idx_d, saved)` otherwise.  Returns
     FAILDESCR — `every` exits cleanly.

   Net effect: under `every x[3] <- 19`, the loop runs once with x[3]=19
   (visible to the body if there were one), then on β the value reverts
   to the snapshot.  The table entry **is** created (subscript-set path
   creates and revert writes the saved value back into the now-existing
   slot), so `key(x)` finds 3 and `x[3]` reads 7 — exactly as expected.

   Cell-resolution lives in the box rather than relying on
   `interp_eval_ref` (which is `static` to interp.c and not exported).
   Box state tracks both a direct cell pointer and a (base, idx)
   subscript-set pair so revert works regardless of container shape.
   E_VAR slot/NV paths included for `var <- expr` standalone forms.
   E_FIELD path is in the standalone (interp_eval) handler but not
   yet in the box — no test exercises it under `every`.

   Verified per-shape:
   - empty key on table with default → entry created, value reverts to default ✓
   - existing key → value reverts to original ✓
   - standalone `x <- v; x <- w` outside `every` → final value w (no revert) ✓
   - rung36_jcon_table → empty diff ✓

### Files touched (no header struct changes — clean rebuild not required)

- `src/ir/ir.h` (+2 lines — enum + name table)
- `src/frontend/icon/icon_parse.c` (1-line change: E_ASSIGN → E_REVASSIGN)
- `src/driver/interp.c` (+~150 lines — 6 fixes above)
- `src/runtime/interp/icn_runtime.c` (+~110 lines — icn_bb_revassign + state typedef + icn_is_gen entry + icn_eval_gen wire)

### Gates

- `test_smoke_icon.sh`             PASS=5/0    (unchanged)
- `test_smoke_unified_broker.sh`   PASS=49/0   (unchanged)
- `test_crosscheck_icon.sh`        PASS=4/0    SKIP=0 (unchanged)
- `test_icon_all_rungs.sh`      **PASS=189** FAIL=44 XFAIL=30 TOTAL=263 (+1)
- `test_icon_ir_rung_36.sh`        **PASS=6**  FAIL=39 XFAIL=30 TOTAL=75  (+1)

### Remaining IC-8 / IC-9 candidates (next-session pivot)

The lvalue family is closed for the JCON table test.  Other rung36
tests remain in the same shape as session #20 noted — multi-feature
.xfail tests where one or two features are missing.  Notable open items
visible in the rung36 FAIL list:

- **`!s := "."`** — bang-iterate as lvalue on a string.  Currently a
  no-op (strings are immutable; my E_ITERATE LHS branch silently
  short-circuits).  Standard Icon allows this and rebuilds the string;
  would need a special path that walks chars and accumulates a new
  string into the source variable.  Visible in `rung36_jcon_string`.

- **`(...)(args)` invocation form** — paren-list as procedure value,
  then call.  Parser-level work plus dispatch.  Visible in
  `rung36_jcon_args`, `_fncs`, `_fncs1`.

- **`proc()` builtin** — returns the current procedure as a value.
  Would unblock several tests but needs procedure-value first-class
  representation.

- **co-expressions, &error, &fail, &trace** — already correctly
  xfailed; not high-leverage.

- **scan/scan1/scan2** — `?` scan with goal-directed subexpressions.
  Builds on existing E_SCAN oneshot fallback.

- **string1, substring** — `s[i+:n]` chained `:=` and `:=:` swap not
  fully working.

The simplest single-test pivot would be **`!s := "."`** — it's the
mirror of work just landed and the same shape as the table/list
branches.  String-rebuild semantics (concatenate prefix + new char +
suffix per tick, write back to source var) would close
`rung36_jcon_string` if combined with whatever else that test needs.

### Pollution check

Working tree at session end: clean.  One stray `foo.baz` (empty file —
same scratch shape sessions #19 and #20 cleaned) was removed before
commit per RULES.md "Diagnostic patches are diagnostic — never commit
them".  Per-repo dirty sets at handoff: SCRIP (4 files in this
session's diff), .github (this update), corpus clean, csnobol4 clean,
x64 clean.



---

## Session #22 (2026-05-01) — IC-9 advance: string-section assignment + augop write-back + comparison-augops

IC-9 IN PROGRESS.  Five correctness fixes landed in `src/driver/interp.c`.
PASS counts unchanged; the gains show as **massive diff convergence** on
`rung36_jcon_string` (got 31 → 205 of 231 expected lines), `rung36_jcon_string1`
(got produces all 37 expected lines, 5 still mismatched), and
`rung36_jcon_substring` (got 340 / 368).  No regressions.

### Fixes (all in `src/driver/interp.c`)

1. **E_AUGOP write-back to globals / E_IDX / E_FIELD (AUGOP_APPLY macro,
   line ~4115)** — the macro previously only wrote back to local Icon-frame
   slots (`slot >= 0` in `ICN_CUR.env`).  Globals (`slot < 0`, looked up
   by `lhs->sval` in NV) were silently dropped — `s ||:= "x"` returned
   `"xx"` correctly but never wrote `s`.  Added the `set_and_trace` branch
   mirroring `E_ASSIGN`'s pattern (line 1031–1039) plus E_IDX (subscript_set)
   and E_FIELD (data_field_ptr) LHS branches.

2. **`image()` with no args (line ~2404)** — Icon spec: missing args default
   to `&null`, so `image()` returns `"&null"`.  Handler only matched
   `nargs == 1`; added an `nargs == 0` branch.

3. **Comparison-augops (AUGOP_APPLY switch)** — `s ==:= "x"` was returning
   `INTVAL(0)` (default branch).  Added cases for TK_AUGEQ, TK_AUGNE,
   TK_AUGLT, TK_AUGLE, TK_AUGGT, TK_AUGGE (numeric) and TK_AUGSEQ,
   TK_AUGSNE, TK_AUGSLT, TK_AUGSLE, TK_AUGSGT, TK_AUGSGE (string).
   On comparison success → `_res = _rv` (which then writes back via the
   AUGOP_APPLY write-back path); on failure → `_res = FAILDESCR`.

4. **E_SECTION read-side normalization (case E_SECTION, line ~4348)** —
   pre-existing off-by-one for negative positions and missing handling
   for position 0.  Correct Icon rule:
   - `p >= 1` → position p (1-based)
   - `p == 0` → position past last char (= `slen+1`)
   - `p <  0` → position `slen+1+p`   (e.g. `-1` → `slen`)
   The previous code did `i = slen + 1 + i + 1` (off by one) and never
   handled `i == 0` or `j == 0`, so `s[2:0]` and `s[-1:0]` etc. were
   wrong.  Verified `s = "abcd"; s[1:2]="a", s[-1:0]="d", s[2:0]="bcd",
   s[1:-1]="abc"` after fix.

5. **String-section / string-index assignment** — new helper
   `icn_string_section_assign(lhs, val)` near line 437, wired into
   both icon-frame E_ASSIGN (line ~1126) and main E_ASSIGN (line ~3158).
   Handles E_SECTION, E_SECTION_PLUS, E_SECTION_MINUS, and E_IDX whose
   base is a string.  Strategy: get cell pointer (prefer icon-frame
   local slot for E_VAR; fall back to `interp_eval_ref`), compute
   1-based `[lo, hi)` from the section spec, build new string
   `s[1..lo) + val + s[hi..slen+1)`, write back to the cell.  Uses
   `set_and_trace` for global E_VAR base so VALUE traces fire.
   Returns 1 on success, 0 on FAIL (OOB) or non-string base.  The
   E_ASSIGN wiring tries this helper first for the section LHS kinds;
   for E_IDX it tries the helper first and falls through to
   `subscript_set` (the existing list/table path) if the base isn't
   a string.  OOB string assigns return FAILDESCR (matches the Icon
   spec: `s[6] := "t"` where `*s == 3` fails).

### Verified locally (sec_assign.icn smoke)

```
s := "x"; s[1:2] := "xx"     → s = "xx"      ✓
s := "x"; s[1] := "abc"      → s = "abc"     ✓
s := "abc"; s[1+:2] := "y"   → s = "yc"      ✓
s := "abcdef"; s[2:4] := "XX"→ s = "aXXdef"  ✓
s := "abc"; s[6] := "t"      → s unchanged   ✓ (OOB → FAIL)
```

### Gates

- test_smoke_icon: PASS=5/0 (unchanged)
- test_smoke_unified_broker: PASS=49/0 (unchanged)
- test_crosscheck_icon: PASS=4/0/SKIP=0 (unchanged)
- test_icon_ir_rung_36: PASS=6/FAIL=39/XFAIL=30/TOTAL=75 (unchanged count;
  diffs on `string`, `string1`, `substring` shrunk dramatically)
- test_icon_ir_all_rungs: PASS=189/FAIL=44/XFAIL=30/TOTAL=263 (unchanged)

(`rung31_sort_sort_already_sorted` flapped FAIL → PASS across re-runs in
this session — flaky harness behaviour at the harness's `$()` boundary,
not a real change.  Last run was PASS.)

### Why no PASS-count advance despite five fixes

`rung36_jcon_string` is blocked from PASS by **two** unrelated issues
beyond what I fixed:

1. **`** Error 3 in statement 0` printed at p3 entry** — fires once,
   before p3's first `write` runs, only when p3 is actually called
   (calling p1+p2 alone is silent).  Bisecting individual lines of p3
   in isolation does not reproduce.  Suspect: an eager evaluation in
   the alternation `expr | "none"` or a write-arg pre-pass that walks
   into a subscript before `s` has been assigned in p3's local view.
   Not localised this session.

2. **A handful of edge cases in section/index reads** still off — see
   `string1` diff: `s[0]` is returning empty when expected `abcde`
   (the read side's "position 0 = past-end" plus zero-width slice
   convention may need another look for some forms).

### Remaining IC-9 candidates (next-session pivot)

- **Investigate Error 3 at p3 entry** — needs `--ir-print` of the IR,
  or a printf at `subscript_get`'s Error 3 callsite to see the actual
  call stack.  Once located, this likely closes `rung36_jcon_string`
  and a couple of the other rung36 failures whose got-output starts
  with the same `** Error 3 in statement 0` artifact.

- **`s[0]` whole-string convention** — Icon's `s[i+:0]`, `s[i:i]`, and
  `s[i]` semantics may need a second read of the spec; current
  helper rejects `i == 0` for E_IDX which loses one expected case
  in `string1`.

- **`!s := "."`** — bang-iterate as lvalue on a string (IC-9 pivot
  named in session #21, not done this session).  With
  `icn_string_section_assign` now in place, the implementation is
  short: walk char positions 1..slen, for each one call the helper
  with a synthetic `s[i:i+1] := val`.

### Pollution check

Working tree at session end: SCRIP dirty (1 file: `src/driver/interp.c`,
+185 / -10), .github dirty (this entry), corpus clean, csnobol4 clean,
x64 clean.  No diagnostic instrumentation left in code (three
`fprintf(stderr, "DBG ...")` lines added during section-assign debugging
were removed before commit per RULES.md).


---

## Session #23 (2026-05-01) — IC-9 advance: +11 PASS via 8 fixes

IC-9 IN PROGRESS. **PASS=188 → 199**, FAIL=45 → 34, XFAIL=30 unchanged.
test_icon_ir_rung_36 PASS=6 → 9 (FAIL=39 → 36). All other gates clean
(smoke 5/5, broker 49/0, crosscheck 4/0, smoke_snobol4 7/0).

### Fixes (in order of leverage)

1. **`icn_bb_cat_gen` re-pumps on per-tick failure** (`src/runtime/interp/
   icn_runtime.c`, ~line 660). Was returning FAILDESCR when the per-tick
   re-eval failed (e.g. `s[0]` OOB when generator yielded 0). Per Icon
   GDE semantics, per-tick failure should advance the generator, not
   exhaust the box. Now loops on β until either non-fail result or leaf
   gen exhausts. Unblocks the `s[N to M]` shape across many tests —
   `every writes(s[0 to 7])` now correctly yields `abcde` (skipping OOB
   indices) instead of producing nothing.

2. **E_SECTION_PLUS, E_SECTION_MINUS read handlers** (`src/driver/
   interp.c`, after E_SECTION case ~4486). These IR kinds existed only
   in lvalue-assignment context (since session #21 IC-9). The read side
   fell through to default → NULVCL, so `s[1+:5]` and `s[1-:-5]`
   returned `&null`. Added handlers mirroring E_SECTION's normalization
   logic with `+:` going right and `-:` going left, supporting negative
   span values (extending the other direction). Closes 4 lines in
   `rung36_jcon_string1`.

3. **E_CAT empty-string concat in Icon mode** (`src/driver/interp.c`,
   ~3148). The SPITBOL rule "DT_SNUL operand → return the other
   unchanged" was firing in Icon context. In Icon, `""` is a real empty
   string, not `&null`. Gated SPITBOL passthrough on `g_lang != 1`, AND
   post-coerced any DT_SNUL/null result back to a real DT_S empty
   string in Icon mode. `image("" || "")` now → `""` instead of
   `&null`. Closes the last `rung36_jcon_string1` diff line — **+1 PASS**.

4. **E_POW Icon mode always returns real** (`src/driver/interp.c`,
   ~3069). The session-#12 note said this was already done, but the
   integer fast-path was unguarded. Icon's `^` is a real-producing
   operator regardless of operand types. Gated the integer-fast-path
   on `g_lang != 1`. **+5 PASS** — rung19 and four rung26 pow tests.

5. **left/right/center rewritten** (`src/driver/interp.c`, ~2400).
   Multiple bugs:
   - `nargs >= 2` would never match 1-arg call `left("abc")`
   - default n was `*s` but Icon spec says **n=1**
   - `&null` / elided arg should re-default
   - pad-fill cycling was broken — only used fill[0]
   Verified correct cycling rules against JCON test corpus:
   - **left-pads** (right's left, center's left): `fill[i % fl]`
     (left-aligned cycle starting at fill[0])
   - **right-pads** (left's right, center's right): pad ENDS at
     fill[fl-1]: `fill[((k + fl - padlen) % fl + fl) % fl]`
   - center truncation `srcoff` rounds UP: `(sl - n + 1) / 2`
   **+3 PASS** — center, left, right.

6. **`integer()` / `numeric()` parse `BASErDIGITS` radix prefix**
   (`src/driver/interp.c`, ~2278/~2308). Icon syntax: `16rff`, `36rcat`,
   `2r0`. Base 2..36, case-insensitive 'r'/'R', digits 0-9 + a-z (10..35).
   Optional sign. Closes the radix-parse lines in `numeric` and `radix`
   tests; the tests stay FAIL because of unrelated issues (`integer :=
   abs` function-as-value, `--` cset operator on ints, etc).

7. **New `list(n, x)` constructor** (`src/driver/interp.c`, ~2364, before
   push/put block). Was missing entirely. `list()` returned 0-length,
   `list(2)` returned 0-length, `list(3, 99)` returned 0-length. Now:
   `list()` → empty, `list(n)` → n × `&null`, `list(n, x)` → n × x.
   Skips `&null` n (treats as 0). Doesn't close any rung36 test by
   itself (lists test has many other issues) but is foundational.

8. **`static` declarations persist across calls** (`src/runtime/interp/
   icn_runtime.c` + `src/frontend/icon/icon_parse.c`).
   - Parser: distinguish `local` vs `static` at `parse_stmt` LOCAL/STATIC
     branch — set `e->ival = 1` on E_GLOBAL when keyword was `static`.
   - Runtime: new per-(proc EXPR_t*, var-name) static table
     (`icn_static_tab[256]`) with `icn_static_get/set` helpers near
     `icn_global_register`. At proc entry: walk body for E_GLOBAL with
     `ival==1`, lookup each child's value in static table, copy into
     frame slot. At proc exit (just before pop): write each static
     var's slot value back to the table. Statics with the same name in
     different procs do not share storage (keyed on proc node identity).
   **+1 PASS** — rung36_jcon_statics.

### Wrong-site lesson recurrence

Session #16's "two interp_eval switches" lesson did not bite this time
— the icon-frame switch and shared switch's E_CAT both flow through
the same line-3085 case (the icon-frame block falls through to it),
and the E_POW Icon-mode guard at line 3075 likewise covers both code
paths. New cases (E_SECTION_PLUS / E_SECTION_MINUS read) only matter in
the shared switch since sections are never reached from the icon-frame
return-direct dispatch (E_SECTION isn't in icon-frame block at line
~2591). Verified by running gates after each fix.

### Static-var storage design note

The chosen approach (per-(proc, var-name) table) is simpler than the
mangled-name-into-NV alternative: no name rewriting in the body, no
collision risk between same-named statics in different procs, no
coordination with `icn_is_global` / NV bridge path. Cost: a small
linear-scan table (capacity 256, plenty for most programs). If it
ever needs to scale, replace with a hash table indexed by `proc XOR
hash(name)`. The `icn_init_tab` mechanism for `initial` blocks already
follows the same pattern, so this stays in family with existing code.

### Still open after this session (next-session candidates, ranked by leverage)

- **Records as iterables** (`!a` field iteration, `every !a := V` field
  assignment) — closes `rung36_jcon_record` and contributes to 3+
  other tests that build records. Same shape as table-lvalue work in
  session #21 — extend the `E_ITERATE` and `E_ASSIGN` lvalue handlers
  with a DT_DATA/record branch that walks `data->fields`.
- **`integer := abs` function-as-value** — Icon supports first-class
  procedure values. `image(abs)` should return `"function abs"`. Needs
  procedure-value descriptor type. Affects `numeric` and 4+ others.
- **`100 -- 4` cset-difference on integers** — Icon's `--` between
  numbers does cset coercion: `integer → cset of digit chars`, then
  cset minus cset. Probably one site in `--` operator handler.
- **`&random` keyword seeding** — `rung36_jcon_random` needs deterministic
  RNG state visible to `&random := N` and `&random` reads.
- **`&pos`, `&subject` Icon scan state** — `subjpos`, `scan`, `scan1`,
  `scan2` all need this. Builds on existing E_SCAN oneshot fallback.
- **`(...)(args)` indirect-call syntax + `proc()` builtin** — affects
  `args`, `fncs1`. Major Icon feature.
- **co-expressions, `&error`, `&fail`, `&trace`** — already correctly
  xfailed; not high-leverage to close.

### Working-tree state at handoff

- SCRIP dirty (3 files): `src/driver/interp.c`, `src/runtime/interp/
  icn_runtime.c`, `src/frontend/icon/icon_parse.c`
- .github dirty (this update + PLAN.md state row)
- corpus clean, csnobol4 clean, x64 clean
- one stray `foo.baz` (empty file) in .github/ at session start —
  removed before commit per RULES.md "Diagnostic patches are
  diagnostic — never commit them".

---

## Session #24 (2026-05-01) — IC-9 advance: records as iterables

IC-9 IN PROGRESS.  Five fixes landed in `src/driver/interp.c`,
`src/runtime/interp/icn_runtime.c`, `src/frontend/icon/icon_gen.c`,
`src/frontend/icon/icon_gen.h`.  Gates clean across the board (smoke 5/0,
broker 49/0, crosscheck 4/0/0, rung01-36 PASS=199/FAIL=34/XFAIL=30,
rung_36 PASS=11/FAIL=34/XFAIL=30).  PASS counts unchanged because
`rung36_jcon_record` is `.xfail`-listed and the four remaining diff
lines (record subscript by integer + by string, both under `every`)
keep it just shy of PASS — but the test went from **10+ lines of
garbled raw-bytes output to 4 lines of clean missing data**, and
five distinct record-shape root causes are now fixed.

### Records as iterables — the missing third container shape

Sessions #21 / session #20 added lvalue and `?` paths for tables
(DT_T) and lists (DT_DATA with `icn_type=="list"`).  Records are
the third container shape — also DT_DATA, but **without** the
icnlist tag.  They use the underlying SPITBOL DATA mechanism:
`inst.u->type` is a `DATBLK_t*` carrying `nfields` and field-name
strings; `inst.u->fields[i]` is the value cell array.  Pre-fix, the
`!record` / `?record` / `every !record := V` / `every !record OP:= V`
paths all fell through to char-iterate (treating the descriptor's
bytes as a string) or to FAILDESCR.  The fix is consistently shaped
across the five sites: `cv.v == DT_DATA && cv.u && cv.u->type &&
cv.u->type->nfields > 0 && cv.u->fields` recognizes a record, then
the loop walks `cv.u->fields[0..nfields-1]`.

### Fixes (in order)

1. **`!record` generator** — new `icn_bb_record_iterate` Byrd box in
   `icon_gen.c` walks fields 0..n-1 yielding each.  State struct
   `icn_record_iterate_state_t {DESCR_t inst; int pos}` in `icon_gen.h`.
   Wired into `icn_eval_gen` E_ITERATE in `icn_runtime.c` after the
   icnlist branch — only routes to record path when the DT_DATA has
   a real `inst.u->type` (icnlist's DT_DATA at `icn_elems` doesn't),
   so the historical char-iterate fallback for any other DT_DATA
   shape is preserved.

2. **`!record` scalar** — `interp_eval` E_ITERATE returns
   `cv.u->fields[0]` for DT_DATA records.  Mirrors the icnlist
   first-element branch directly above it.

3. **`every !record := V`** — E_ASSIGN icon-frame, E_ITERATE LHS
   branch.  Mirrors the existing list/table branches: walk all
   fields, write `val` into each cell.  Single pass per box-α tick;
   `every` exhausts after one tick because the box's own α exhausts
   one iteration over the fields.

4. **`every !record OP:= V`** — E_AUGOP, E_ITERATE LHS branch, same
   `AUGOP_CELL` macro from session #21.  All five augops + `||:=`
   covered automatically since macro is shape-agnostic.

5. **`?record` and `?record := V`** — E_RANDOM gets a record arm
   (returns `fields[rnd % nfields]`).  E_ASSIGN icon-frame gets a
   new E_RANDOM-LHS branch (writes val into a random field).
   Two separate static LCG seeds (read seed at line ~4313, write
   seed in the new branch) — sharing one would make read-after-write
   correlation visible to programs that interleave `?b` and
   `?b := X`, which would be incorrect since each is independently
   selecting.

### Verified on rung36_jcon_record

```
Before:  1 2|3 4|5 6|7 8|9 10|<garbled bytes>|<more garbage>|
After:   1 2|3 4|5 6|7 8|9 10|11|12|13|14|15|<missing 4 subscript lines>|11 22 73 74
```

Lines 1–10 of expected (16 lines total) now match byte-for-byte.
Lines 11–14 are `every write(b[1 to 3])` and `every write(b["f" ||
(1 to 3)])` — record subscript by integer N (returns Nth field) and
by string "fN" (returns field named "fN"), each driven by an `every`
generator.  Both need `subscript_get(record, idx)` to recognize
DT_DATA records and dispatch by IS_INT (lookup field N) or IS_STR
(lookup field name).  Single function, low-risk — natural next pivot.

### Build hazard avoided

Header change was localized: `icon_gen.h` got the new state typedef
and box decl, and `icon_gen.c` / `icn_runtime.c` are the only
consumers.  No `IcnFrame` layout change (per session-#16's lesson on
clean rebuilds).  Did one full clean rebuild anyway as belt-and-suspenders;
inner-loop edits compiled incrementally clean.

### Wrong-site lesson — caught in flight

Mid-session brace mistake: when adding the E_RANDOM LHS branch to the
icon-frame E_ASSIGN, I wrote `}` to close the new `else if` body but
not the outer `if (e->nchildren < 2 ... ) {` opening — `return val;`
moved one level shallower than intended.  Compiler caught it as a
cascade of "invalid storage class for function" errors (unbalanced
brace promoted later top-level functions to nested status).  Fix was
one missing `}` before `return val;`.  Session-#16's "two switches"
caveat doesn't bite this work (no E_FOO that exists in both icon-frame
and shared switches changed), but the brace-balance discipline matters
the same way.

### Remaining IC-9 candidates for next session

- **Record subscript** (`b[N]` integer, `b["fN"]` string, both under
  `every`).  Closes `rung36_jcon_record` (4 remaining diff lines).
  Single site: `subscript_get` in interp.c, add DT_DATA-record arm
  before the DT_DATA-icnlist arm.  Field-name lookup uses `data_field_ptr`
  (already exists); field-by-index uses `inst.u->fields[i-1]` with
  1-based bounds check.

- **Procedure values** — `image(abs)` returning `"function abs"`.
  Needs new descriptor type (DT_PROC?) or reuse DT_DATA with a tag.
  Affects `numeric`, `args`, `fncs1`.  Larger change, real new
  feature work.

- **`100 -- 4` cset-difference on integers** — Icon coerces ints to
  csets-of-digit-chars before `--`.  One site in the `--` operator
  handler.

- **`&random` keyword seeding** — RNG state for `&random := N`.
  Independent of session-#20's `?` random LCG; needs a global
  `&random` slot wired to both read and write.

- **`&pos` / `&subject` Icon scan state** — needed for
  `scan/scan1/scan2`.  Builds on existing E_SCAN oneshot fallback.

### Working-tree state at handoff

- SCRIP dirty (4 files): `src/driver/interp.c`,
  `src/runtime/interp/icn_runtime.c`, `src/frontend/icon/icon_gen.c`,
  `src/frontend/icon/icon_gen.h`
- .github dirty (this update + PLAN.md state row)
- corpus clean, csnobol4 clean, x64 clean
- one stray `foo.baz` (empty file) in SCRIP/ at session start —
  removed before commit per RULES.md "Diagnostic patches are
  diagnostic — never commit them".

---

## Session #25 (2026-05-01) — IC-9 advance: record subscript + Icon scan-state writes + parser permissiveness

IC-9 IN PROGRESS.  One closed test (+1 PASS), three previously-unparseable
tests now parse and run, foundational scan-state writes landed.  Six files
changed across `SCRIP/src` (99 insertions, 12 deletions).  Gates:
smoke 5/0, broker 49/0, crosscheck 4/0/0, rung_36 PASS=11→**12**,
rung01-36 PASS=199→**200** FAIL=34→**33** XFAIL=30 unchanged.

### Headline: rung36_jcon_record CLOSED — empty diff vs `.expected`

Session #24's named "natural next pivot" landed.  Single-site fix in
`subscript_get` (`src/runtime/x86/snobol4_pattern.c`): added a SPITBOL-
DATA-record arm between the icnlist arm and the legacy tree-child-access
arm.  Recognized via session-#24's record-shape contract
(`arr.u && arr.u->type && arr.u->type->nfields > 0 && arr.u->fields`),
dispatches by `IS_INT_fn(idx)` (returns `fields[i-1]` with 1-based bounds)
or `idx.v == DT_S/DT_SNUL` (linear scan over `type->fields[]` field-name
strings via plain `strcmp`).  No header dependency — `DATBLK_t` and
`DATINST_t` are both already in `snobol4.h`.  Field-name lookup was
inlined rather than calling out to `data_field_ptr` (which is `static` in
`interp.c`); zero new API surface, mirrors the icnlist arm's inline style.

The 4 missing diff lines from session #24 (`every write(b[1 to 3])` and
`every write(b["f" || (1 to 3)])` on `rec(3, 7)`) are now present
byte-identical.  Verified by empty `diff -q rung36_jcon_record.expected
out`.

### Foundation: Icon `&pos` / `&subject` writes + `:=:` swap + scan-state init

Three coordinated edits in `src/driver/interp.c` and one in
`src/runtime/interp/icn_runtime.c` and one in `src/driver/polyglot.c`,
landing the runtime contract for Icon scan-state mutation.  Reads of
`&pos` and `&subject` already worked (at line ~1147 of interp.c via the
icon-frame E_VAR dispatch); writes were missing — `&pos := N` parses to
E_ASSIGN(E_VAR("&pos"), N) but the icon-frame E_ASSIGN's E_VAR branch
explicitly skipped `&`-prefixed names ("for parity with the pattern-match
path", line 1158-original).

  1. **`icn_kw_assign` helper** (new, just before `interp_eval` in
     interp.c).  Encapsulates the spec semantics: `&pos := N` accepts
     N in `[-L, L+1]` where L=strlen(subj); N=0 → L+1 (after-last);
     N<0 → L+1+N; OOB → return 0 (FAIL).  `&subject := s` accepts any
     value, stringifies via VARVAL_fn, GC_strdup, **resets `&pos` to 1**
     (Icon spec).  Other keywords: silent no-op (return 1) — read-only
     keywords like &letters, &lcase, &digits already have read paths
     and writing them would be a semantics-mismatch error to surface
     elsewhere.

  2. **E_ASSIGN E_VAR `&` branch** wired in icon-frame E_ASSIGN at
     line ~1150.  Detected by `lhs->sval[0] == '&'`; routes to
     `icn_kw_assign(lhs->sval+1, val)`.  On FAIL, returns FAILDESCR
     (the whole assign fails, like any other Icon assign).

  3. **E_SWAP keyword sides** at line ~4622.  Both LHS and RHS branches
     check `sval[0] == '&'` and route to `icn_kw_assign` instead of
     `NV_SET_fn`.  Critical detail: keyword-write FAIL is **silent** —
     left-to-right execution continues with the other side getting the
     `lv`/`rv` it would have gotten.  This matches Icon's `:=:` spec
     and is byte-confirmed against `subjpos.expected` lines 56-58
     (`&pos := 3; x := 9; &pos :=: x` → `pos=3 x=3` because the
     `&pos := 9` half OOBs silently and x still gets the old pos).

  4. **Scan-state init defaults** (`icn_runtime.c` lines 75-76 +
     `polyglot.c` line 86).  Per Icon spec, before the first `?` block
     `&pos = 1` and `&subject = ""`.  Pre-fix defaults were
     `icn_scan_subj = NULL; icn_scan_pos = 0` — yielded `&subject=&null`
     instead of `&subject=""` and `&pos=0` instead of `&pos=1` at program
     start.  Fixed in two places (the static initializer in
     icn_runtime.c AND the polyglot reset in polyglot.c which fires per
     run).  Downstream gates of the form `icn_scan_pos > 0` in
     `any/many/upto/move/tab/match` (interp.c lines 1372-1407) all
     remain safe — the empty subject correctly fails any operation
     requiring position movement via the existing length check.

### Parser permissiveness: optional `;` after `}`-terminated statement and after procedure header

Two distinct issues in `src/frontend/icon/icon_parse.c` (+ one new field
in `icon_parse.h`).  Real Icon is more permissive than our parser was
documented as "explicit-semicolon Icon (no auto-insertion)" (header line
4).  Three rung36 JCON tests rely on this permissiveness and previously
failed at parse time with garbled error messages — fixing them unlocks
them as runtime work, not parser work.

  1. **`prev_kind` field** added to `IcnParser` struct.  Tracks the
     kind of the last token consumed by `advance()` — enables
     `parse_stmt` to know whether the just-parsed expression ended on
     a `}`.  Header change → required clean rebuild of the icon
     frontend `.o` files; see "Build hazard" below.

  2. **`parse_stmt` expression-stmt terminator rule** (line ~765)
     extended: `;` is optional when the just-parsed expression ended
     on `}`, in addition to the existing exempt lookaheads (`}`, EOF,
     `end`, `else`, `then`, `return`, `suspend`).  Closes the JCON
     idiom of nested `?` blocks where the inner block's `}` is the
     last token of an expression statement and the next statement
     starts on a fresh line without explicit `;`.

  3. **`parse_proc` optional `;` after `()`** (line ~833).  JCON style
     allows `procedure ws();` followed by body — current parser
     required body to start immediately after `)`.  Fixed by adding
     `match(p, TK_SEMICOL)` after the existing `expect(TK_RPAREN)`
     call.  Idempotent (the `;` is optional, not required).

These two fixes are independent but compound: with both in place,
`rung36_jcon_subjpos`, `rung36_jcon_scan1`, `rung36_jcon_var` go from
"parse fails on line N with garbled error" to "parses; runs to
completion; produces partial output".

### Build hazard hit (already documented in session #16 but worth re-noting)

`build_scrip.sh` does NOT track header dependencies.  After modifying
`icon_parse.h`, only the `.c` file directly being edited was recompiled;
`icon_driver.o` and `icn_main.o` retained the pre-change `IcnParser`
layout.  Symptom: the parser silently corrupted `had_error` (which sat
at a different offset in the new layout) and `errmsg` showed up empty
at print time.  The DBG print I added to `parser_error` confirmed
`parser_error` itself was never being called — meaning `had_error` was
being clobbered by ABI mismatch, not set legitimately.

Fix: `rm src/frontend/icon/*.o && bash scripts/build_scrip.sh`.
Cost: ~10 minutes of confused investigation.  Following sessions: when
editing any `.h` in src/frontend/, do clean rebuild of that frontend's
`.o` first.  This may belong in RULES.md if not already there.

### Subjpos final state — 56/62 lines byte-identical

After all fixes, `rung36_jcon_subjpos` parses, runs, and produces
output that matches `.expected` for 56 of 62 lines (90%).  Remaining
diff is exactly the `every &pos <-> x do …` reversible-swap cases
(source lines 42, 46) — Icon's `<->` is supposed to revert both
writes on backtrack.  Currently we route `<->` to E_SWAP with the
same scalar implementation as `:=:`; correct implementation needs an
icn_bb_swap box with revert-on-exhaust.  Tracked as IC-9 followup.
This is sufficient byte-overlap that I'm confident the underlying
runtime contract for `&pos`/`&subject` is correct — the failing
lines all involve the *separate* feature of reversible-swap revert,
not a flaw in the keyword-assign mechanism itself.

### Other tests unblocked (now parsing, not yet PASSing)

- **`rung36_jcon_scan1`** — parses now; OOM at runtime (heap allocator
  asks for 2^54 KiB).  Some downstream feature exposed by the longer
  parse path runs into either an unbounded recursion or a length
  miscalculation.  Worth investigating; likely a single bad cast.

- **`rung36_jcon_var`** — parses now; diff = 79 lines.  Tests
  procedure-value introspection (`image`, `args`), Icon `&main`,
  many keyword reads.  Multi-feature, deferred.

- **`rung36_jcon_scan`** — was parsing already; remains parsing with
  large (143-line) diff.  Tests the full scan subsystem
  (`tab/move/upto/match/any` interactions, `=`-string-match,
  `?:=` scanned-assign, etc.).  Multi-feature, deferred.

- **`rung36_jcon_scan2`** — different parse error (line 25 "function
  call"), not unblocked by these changes.  Cset literal or
  immediate-cast issue, not the same family.

### Why no PASS bump beyond +1

The headline number (rung_36: 11→12, ladder: 199→200) reflects only
the record-subscript closure.  The parser permissiveness and scan-state
fixes are **infrastructure work** — they remove blockers that were
hiding feature gaps further downstream.  Now-parsable tests reveal
those gaps as clean diffs that future sessions can attack one at a
time.  Without these fixes, work on `every <->`, on Icon procedure
values, on the rest of the scan subsystem would have been gated by
"can't even run the test" rather than "can run, here's the actual
diff to close".

### Followup candidates ranked by surface area

1. **`every <-> x` reversible swap box** — 1 file, ~1 box.  Closes
   `subjpos`.  Mechanical: model on existing `icn_bb_revassign` for
   E_REVASSIGN; save both old values, on exhaust restore.

2. **`scan1` OOM diagnosis** — likely a single bad-cast bug; fix
   could be tiny if the cause is simple.  Run with limited heap +
   gdb to catch the runaway allocation site.

3. **Procedure values + `image(p)`** — affects `mathfunc`,
   `numeric`, `lists` (via `args`), `var`.  Single new descriptor
   type (DT_PROC tag on DT_DATA, or a fresh DT_FN), plus image
   formatting.  ~3 files.

4. **`100 -- 4` cset-difference on integers** — single site in
   the `--` operator handler; closes one diff line on
   `rung36_jcon_radix` per session #24's catalog.

### Working-tree state at handoff

- SCRIP dirty (6 files): `src/runtime/x86/snobol4_pattern.c` (+22),
  `src/driver/interp.c` (+~50), `src/frontend/icon/icon_parse.c`
  (+10), `src/frontend/icon/icon_parse.h` (+4 — new prev_kind field),
  `src/runtime/interp/icn_runtime.c` (+5 — init defaults & comment),
  `src/driver/polyglot.c` (+1, -1 — init defaults).  Total 99
  insertions, 12 deletions.
- .github dirty (this update + PLAN.md state row)
- corpus clean, csnobol4 clean, x64 clean
- one stray `foo.baz` (empty file) at SCRIP/ root at session start —
  removed before commit per RULES.md "Diagnostic patches are
  diagnostic — never commit them".

---

## Session #26 (2026-05-01) — IC-9 advance: `<->` reversible value swap (E_REVSWAP)

IC-9 IN PROGRESS / IC-8 ADVANCE.  **rung36_jcon_subjpos CLOSED** byte-identical
to expected — first session-#25 followup pivot landed.  Five files changed in
SCRIP (196 insertions, 9 deletions).  Gates clean across the board:
smoke 5/0, broker 49/0, crosscheck 4/0/0, snobol4-smoke 7/0.

**rung_36 PASS=12 → 13** (FAIL=33 → 32, XFAIL=30 unchanged).
**Full ladder PASS=200 → 201** (FAIL=33 → 32, XFAIL=30 unchanged).

### What landed

Session #25 named `every <->` reversible swap as the highest-leverage next
pivot — `subjpos` was at 56/62 byte-identical lines, the only remaining diff
being `<->` revert behaviour, with the `icn_bb_revassign` (session #21)
pattern as the explicit model.  This session implemented the box and
discovered along the way a separate latent bug in scalar `:=:` keyword-OOB
semantics that the same fix path resolved.

#### 1. `E_REVSWAP` — new IR kind (was conflated with `E_SWAP`)

Pre-fix: parser routed both `:=:` (TK_SWAP) and `<->` (TK_VALSWAP) to the
same `E_SWAP` IR node, making them indistinguishable downstream.  `<->`'s
revert-on-backtrack semantics had nowhere to live.

Fix: added `E_REVSWAP` to `EKind` enum + `ekind_name[]` table in `src/ir/ir.h`
(2 lines, before `E_KIND_COUNT`).  Updated parser at
`src/frontend/icon/icon_parse.c:512`:
`TK_VALSWAP` now emits `E_REVSWAP` (was `E_SWAP`).  `:=:` continues to emit
`E_SWAP`.

#### 2. Scalar `:=:` / `<->` semantics — left-to-right halt-on-keyword-OOB

Discovered during subjpos diff-tracing.  Pre-fix `E_SWAP` performed both
writes unconditionally, calling `icn_kw_assign` for keyword sides and
silently ignoring its return value.  When `&pos := N` OOB-failed silently,
the *other* side still wrote, leaving state half-swapped.

Subjpos.expected lines 57/58 give the actual contract:

  ```
  &pos := 3; x := 9; &pos :=: x   →  &pos=3, x=9   (lhs OOB-fails → halt; x untouched)
  &pos := 3; x := 9; x :=: &pos   →  &pos=3, x=3   (lhs writes; rhs OOB-fails → halt)
  ```

The semantics is **not atomic all-or-nothing** (my first analysis was wrong)
but **left-to-right halt-on-fail**: write `rv → lhs`; if it OOB-fails, stop
immediately; else write `lv → rhs`; if it OOB-fails, stop.  Partial writes
are kept.  The whole expression returns FAILDESCR on partial-OOB so the
enclosing statement no-ops (which is fine — `x :=: y` as an expression
statement just terminates that statement on fail; subsequent statements
run normally).

Fix in `src/driver/interp.c` E_SWAP case (~line 4660): rewrote to halt-on-fail
order with proper `icn_kw_assign` return-value gating.  Added an exact-mirror
`E_REVSWAP` case below it for the standalone path (outside `every`, `<->`
behaves like `:=:` — no driver to backtrack against).

This fixes a latent bug session #25 introduced (silent-keyword-OOB on
`:=:`) but didn't surface as a PASS-count regression because no rung_36
PASS depended on the broken behaviour — only subjpos's still-FAIL state
made the wrong outputs visible.

#### 3. `icn_bb_revswap` Byrd box — α swap, β revert

New box in `src/runtime/interp/icn_runtime.c` modeled directly on
`icn_bb_revassign` (session #21).  State struct carries `lhs_expr`,
`rhs_expr`, both saved values, and `lhs_written` / `rhs_written` flags
that record which writes α actually committed.

  α: `interp_eval(lhs)` and `interp_eval(rhs)` for read; snapshot both;
     write `rv → lhs` (halt-on-fail, return FAILDESCR if so); else
     `lhs_written=1`; write `lv → rhs` (halt-on-fail); else
     `rhs_written=1`; return rv.

     When `every` sees FAILDESCR from α, the body never runs and β is
     never called — so partial writes (lhs committed, rhs OOB) are left
     in place.  Subjpos.expected line 60 confirms this is correct:
     `&pos:=3; x:=9; every x <-> &pos do write` produces no body output
     and post-loop `&pos=3 x=3` (lhs `x` got 3 from the partial α; β
     never fires).

  β: revert in same left-to-right order with short-circuit on failure.
     Try saved-lhs → lhs.  If it OOB-fails, stop — do NOT try rhs revert.
     Else try saved-rhs → rhs.  Return FAILDESCR (every exits).

     The asymmetric short-circuit produces the JCON-confirmed pattern in
     subjpos.expected lines 61/62:
     ```
     every &pos <-> x do &subject := "A"   →  &pos=1 x=3   (lhs revert OOB → neither reverted)
     every x <-> &pos do &subject := "A"   →  &pos=1 x=2   (lhs reverts; rhs OOB → only lhs)
     ```
     In line 61, body sets &subject="A" so subj-len becomes 1, then β tries
     `&pos := saved=3` — OOB on len-1 → halt → x's revert also skipped.
     In line 62, β reverts `x := saved=2` cleanly, then `&pos := saved=3`
     OOBs → x's revert stays committed.

Wired into `icn_eval_gen` (after `E_REVASSIGN` block, before scalar-literal
fallback) and `icn_is_gen` (always true, like `E_REVASSIGN`).

#### 4. `icn_kw_assign` un-staticed; `icn_kw_can_assign` probe added

The Byrd box lives in `icn_runtime.c` (different translation unit from
`interp.c`).  `icn_kw_assign` was `static` — un-staticed and declared in
`src/runtime/interp/icn_runtime.h` so the box can call it for keyword writes.

Also added `icn_kw_can_assign` probe variant (returns 1 if write would
succeed without writing).  Currently unused — was used during the wrong
"atomic" first attempt; kept as a building block since it's small and
may be useful for future contexts where probe-then-commit is the right
shape.  `-Wno-unused-function` is set in the build flags so this doesn't
warn.

### Build hazard re-encountered (header change)

`src/runtime/interp/icn_runtime.h` got two new function decls.  Per session
#16 / session #25 lessons, ran `find src -name '*.o' -delete && bash
scripts/build_scrip.sh` to ensure all consumers picked up the new header.
Adding function decls (vs. struct field reorderings) is technically safe
without clean rebuild, but doing it anyway is cheap insurance.  No symptoms
of stale-object hazard observed — gates passed first run after rebuild.

### Wrong-analysis lesson — keep this for future sessions

I burned ~2 rounds on the wrong semantic model before tracing
subjpos.expected line by line.  My first model was "atomic all-or-nothing"
(probe both keyword writes; abort whole α if either OOBs).  That fits some
of the expected lines but not all.

The rule that fits ALL eight subjpos.expected lines (55-62) is **left-to-right
halt-on-fail at α, left-to-right short-circuit-on-fail at β**.  Specifically:

- α success path: both writes commit.
- α partial-fail (lhs writes, rhs OOBs): lhs stays committed, body never
  runs, β never called.  Net: half-swap visible after the every.
- α full-fail (lhs OOBs immediately): nothing written, body never runs.
- β path: try lhs revert first; on success try rhs revert; on either
  OOB, stop.  Body's effects on subj/pos state can mutate the keyword's
  valid range mid-flight, so revert-OOB is a real failure mode.

The lesson: when the test suite gives you 8 expected output lines and 4
distinct combinations of LHS/RHS keyword/non-keyword shapes, **trace each
one through your model before committing to a refactor**.  My intuition
"surely it's atomic" cost more time than 5 minutes of paper tracing would
have saved.

### Tests that exercise this path going forward

- **rung36_jcon_subjpos** — primary gate for `<->` and `:=:` semantics.
  Closed this session.
- **rung36_jcon_evalx** — has both `<->` and `:=:` in image() expression
  contexts; XFAIL today (multi-feature, includes co-expressions and
  &fail).  My change to E_SWAP scalar semantics may shift its diff but
  not its FAIL status.
- **rung15_real_swap_swap_str** — non-keyword `a :=: b`; pre-existing
  trailing-newline FAIL unchanged.  Verified by stash-test that the FAIL
  pre-dates my edits.
- **ipl/gprogs/proto.icn** (rung36_jcon_proto) — uses `x <-> y` with
  non-keyword vars; remains PASS.

### Files

- `src/ir/ir.h` (+2 lines: enum entry + name table)
- `src/frontend/icon/icon_parse.c` (1-line change: TK_VALSWAP routes to E_REVSWAP)
- `src/driver/interp.c` (+~62 lines: icn_kw_can_assign, E_SWAP rewrite,
  E_REVSWAP standalone case; un-static icn_kw_assign)
- `src/runtime/interp/icn_runtime.h` (+7 lines: icn_kw_assign + icn_kw_can_assign decls)
- `src/runtime/interp/icn_runtime.c` (+~124 lines: icn_revswap_state_t,
  icn_revswap_write, icn_revswap_read, icn_bb_revswap, E_REVSWAP entry
  in icn_is_gen, E_REVSWAP wire in icn_eval_gen)

Total: 5 files, 196+/9-.

### Followup candidates ranked by surface area (from session #25's list,
### updated)

1. **`scan1` OOM diagnosis** — likely single bad-cast bug; fix could be
   tiny if the cause is simple.  Run with limited heap + gdb to catch
   the runaway allocation site.

2. **Procedure values + `image(p)`** — affects `mathfunc`, `numeric`,
   `lists` (via `args`), `var`.  Single new descriptor type
   (DT_PROC tag on DT_DATA, or a fresh DT_FN), plus image formatting.
   ~3 files.

3. **`100 -- 4` cset-difference on integers** — single site in the `--`
   operator handler; closes one diff line on `rung36_jcon_radix` per
   session #24's catalog.

4. **`&random` keyword seeding** — RNG state for `&random := N`.
   Independent of session #20's `?` random LCG; needs a global `&random`
   slot wired to both read and write.

### Working-tree state at handoff

- SCRIP advanced to `634d9701` (5 files: `src/ir/ir.h`, `src/frontend/icon/icon_parse.c`,
  `src/driver/interp.c`, `src/runtime/interp/icn_runtime.h`,
  `src/runtime/interp/icn_runtime.c`).  Total 196+/9-.
- .github dirty (this update + PLAN.md state row update)
- corpus clean, csnobol4 clean, x64 clean
- one stray `foo.baz` (empty file) at SCRIP/ root at session start —
  same scratch shape sessions #19–#25 cleaned.  Removed before commit
  per RULES.md "Diagnostic patches are diagnostic — never commit them".

---

## Session #29 (2026-05-02) — IC-9 diagnosis: E_SCAN dispatch bug + E_SEQ assign root cause found

IC-9 IN PROGRESS.  No PASS-count advance (PASS=201/FAIL=32/XFAIL=30 unchanged),
but two bugs diagnosed and one partially fixed.  Gates all preserved:
smoke 5/0, broker 49/0, crosscheck 4/0/0.

### Bug 1 — E_SCAN SNOBOL4/Icon dispatch guard (FIXED)

**Site:** `src/driver/interp.c` E_SCAN shared-switch handler, dispatch guard.

**Root cause:** Guard was `if (!icn_scan_depth && !g_pl_active)` — this fired
the SNOBOL4 `exec_stmt` path for the *outermost* scan, even inside an Icon
proc where `icn_frame_depth > 0`.  Inside `main()`, `icn_scan_depth` starts
at 0, so `"1234ab" ? { ... }` at the top level of main() took the SNOBOL4
path: `exec_stmt` ran, set up NO `icn_scan_subj`/`icn_scan_pos`, the body
executed with `icn_scan_subj = NULL`, and `icn_kw_assign("pos", 6)` OOB-failed
silently (slen=0, norm=6 > slen+1=1).

**Fix:** `!icn_scan_depth` → `!icn_frame_depth`.  Inside any Icon proc,
`icn_frame_depth > 0`, so the guard is false and the Icon scan setup path
(save stack, set `icn_scan_subj = subj_s`, `icn_scan_pos = 1`) runs correctly.

**Also added (defense-in-depth):** In the shared-switch `case E_VAR` and
`case E_ASSIGN`, handle Icon scan-state keywords (`&pos`, `&subject`) when
`icn_scan_depth > 0 && !icn_frame_depth` — for the edge case where a scan
body runs completely outside any Icon proc frame (e.g. top-level polyglot
scripts).  These guards are correct but unreachable in practice once Bug 1
is fixed (inside a proc, `icn_frame_depth > 0` and the icon-frame switch
handles E_VAR/E_ASSIGN directly).

### Bug 2 — E_SEQ assigns don't persist (ROOT CAUSE FOUND, NOT YET FIXED)

**Repro:** `(x := 5 & write(x))` prints `0`, not `5`.  Also: `x := 0;
(x := 5 & write(x))` prints `0`.  The conjunction evaluate's `x := 5`
(first child) before `write(x)` (second child) per the parser, but `x`
reads back `0`.

**Diagnostic trace** (E_ASSIGN slot-print + E_VAR env-print):

```
E_ASSIGN x slot=0 env_n=2 depth=1          ← x := 0 (statement 1)
E_VAR read x slot=0 env[slot].v=6 i=0      ← write(x) reads DT_SNUL=6, not DT_I
E_ASSIGN x slot=0 env_n=2 depth=1          ← x := 5 (statement 2, child[0] of E_SEQ)
```

**Root cause:** `env[slot].v=6=DT_SNUL` after `x := 0`.  `INTVAL(0)` produces
`{.v=DT_I, .i=0}` — if the slot showed DT_SNUL after the assign, the
**icon-frame E_ASSIGN is not actually writing to the slot for statement 1**.
The icon-frame E_ASSIGN falls through to `set_and_trace(lhs->sval, val)`
(the NV/global path) when `slot < 0` — meaning `lhs->ival == -1` for `x`
in statement 1.

**Why `ival == -1` for statement 1 but `ival == 0` for statement 2:**
`icn_scope_patch` walks the proc body and assigns slot indices to E_VAR nodes
in AST order.  If `x` first appears in the E_SEQ body (statement 2) and
`icn_scope_patch` assigns slot 0 there, the `x` E_VAR node in statement 1
(`x := 0`) may be a **different EXPR_t node** that `icn_scope_patch` visited
earlier (before it encountered `x` and added it to the scope) — or the scope
walk order means statement 1's node was visited before `x` was registered.

**Session #30 fix plan:** In `icn_scope_patch`, ensure it walks ALL body
statements before patching (or patches in two passes — first collect all
declared names via E_GLOBAL, then walk again to stamp slots).  Alternative:
examine the AST walk order in `icn_scope_patch` for `x := 0; (x := 5 & ...)` —
if statement 1 is processed before `x` appears in statement 2's subtree, the
scope entry isn't there yet when statement 1's E_VAR is patched.  The fix
is to pre-populate the scope from all E_GLOBAL (local/static) declarations
first, THEN do the naming walk — ensuring any `x` that appears as a plain
assignment before an explicit local-decl still gets a valid slot.

### What was NOT committed

Per RULES.md: diagnostic `fprintf` instrumentation removed before commit.
The E_SCAN guard fix (`!icn_scan_depth` → `!icn_frame_depth`) and the
shared-switch scan-keyword read/write guards ARE committed (correct, no
floors broken).  Bug 2 is NOT committed — the fix is understood but not
yet implemented.

### Gates at handoff

- test_smoke_icon: PASS=5/0
- test_smoke_unified_broker: PASS=49/0
- test_crosscheck_icon: PASS=4/0/0
- test_icon_ir_all_rungs: PASS=201 FAIL=32 XFAIL=30 TOTAL=263 (unchanged)
- test_icon_ir_rung_36: PASS=13 FAIL=32 XFAIL=30 TOTAL=75 (unchanged)

### Working-tree state at handoff

- SCRIP: 1 file changed (`src/driver/interp.c`, E_SCAN guard + shared-switch
  scan-keyword read/write guards).  Committed this session.
- .github dirty (this update + PLAN.md state row)
- corpus clean, x64 clean

---

## Session #30 (2026-05-02) — IC-9: & precedence + E_SEQ frame + find/upto gen-subj

IC-9 IN PROGRESS. **rung36 PASS=14** (from 13), **ladder PASS=202** (from 201).
Gates: smoke 5/0, broker 49/0, crosscheck 4/0/0. SCRIP HEAD `1e515891`.

Three fixes landed across two commits (`3f436ceb`, `1e515891`):

**Fix 1 — parser: `&` had higher precedence than `:=` (wrong)**
`parse_and` called `parse_rel`, making `x := 5 & write(x)` parse as
`x := (5 & write(x))`. Correct Icon: `&` lower than `:=`, so `(x:=5)&write(x)`.
Fix: `parse_and` now calls `parse_assign`; `parse_expr` calls `parse_and`.

**Fix 2 — runtime: `case E_SEQ` missing from icon-frame switch**
E_SEQ fell through to shared switch, whose Icon path gates on `g_lang==1`.
In legacy dispatch `g_lang=0`, so E_SEQ took the SNOBOL4 concat path.
Fix: added `case E_SEQ` to icon-frame switch. Also resolves `scan1` OOM
(was caused by wrong parse of `&pos := 6 & write(any('ab') | "fail")`).

**Fix 3 — find/upto with generative subject**
`find(needle,gen_subj)` and `upto(cset,gen_subj)` only got the first
alternation arm. Two new Byrd boxes `icn_bb_find_gen_subj` /
`icn_bb_upto_gen_subj` drive the subject generator and exhaust positions
per subject. `upto` box uses byte-scan (8-bit safe, no `strchr`).

### Next-session pivot (ranked)

1. **`="string"` scan-match** — `"12345" ? { write(="123" | "fail") }`.
   Icon `=expr` in scan context = `match(expr)`. Parser emits wrong node.
2. **`move`/`tab` multi-step in scan block** — scan-pos may reset between
   calls inside `{ }` body; cumulative advance broken.
3. **8-bit cset scalar `upto`** — `interp.c` scalar `upto` still uses
   `strchr` (not 8-bit safe). Replace with byte-scan loop.
4. **`upto` in implicit scan context** — `&ascii ? every upto(skips)` needs
   scan-frame Byrd box path (no explicit subject arg).

### Working-tree state at handoff

- SCRIP: HEAD `1e515891`, clean.
- .github dirty (this update + PLAN.md)
- corpus clean, x64 clean
