# GOAL-PST-REBUS.md — Pure Syntax Tree: Rebus Rewrite

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 5)
**Split from:** `GOAL-PST-REBUS-PROLOG.md` — Rebus half only
**Status:** DONE — PST-RB-5a through 5d all complete 2026-05-16

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

Rebus previously built a separate `RProgram` / `RStmt` / `RExpr` IR and
never touched `tree_t`. The entire pipeline has been redirected to `tree_t`.

**⛔ SCRIP mirror invariant:** Every rung touches both C-side parser/lower
AND `corpus/SCRIP/parser_rebus.sc` / `lower.sc` in the same commit.
Post-parse `tree_t` shape must match.

---

## ⛔ Pure-syntax rules (binding)

**Allowed:** `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`,
`ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.

**Forbidden:** Building `RExpr*` / `RStmt*` / `RProgram*` from parser actions;
scope lookup during parse; child reordering for positional semantics.

**⛔ Left-to-right child order:** All children in source token order.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate scripts:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
```

---

## REKind → TT_* mapping (verified in 5a)

| REKind           | tree_t kind      | Notes                              |
|------------------|------------------|------------------------------------|
| RE_LIT_S         | `TT_QLIT`        | `v.sval = string`                  |
| RE_LIT_I         | `TT_ILIT`        | `v.ival = integer`                 |
| RE_LIT_F         | `TT_FLIT`        | `v.dval = double`                  |
| RE_VAR           | `TT_VAR`         | `v.sval = name`                    |
| RE_ASSIGN        | `TT_ASSIGN`      | `c[0]=lhs, c[1]=rhs`              |
| RE_BINOP(op)     | `TT_ADD` etc.    | per-operator kind                  |
| RE_UNOP(op)      | `TT_MNS` etc.    | per-operator kind                  |
| RE_CALL          | `TT_FNC`         | `v.sval=name, c[]=args`           |
| RE_SEQ           | `TT_SEQ`         | concatenation                      |
| RE_BLOCK         | `TT_PROGRAM`     | statement list                     |
| RE_IF            | `TT_IF`          | `c[0]=cond, c[1]=then, c[2]=else?`|
| RE_WHILE         | `TT_WHILE`       | `c[0]=cond, c[1]=body`            |
| RE_DEFINE        | `TT_DEFINE`      | `v.sval=name, c[]=params+body`    |
| RE_RETURN        | `TT_RETURN`      | `c[0]=value?`                     |

---

## Rungs

- [x] **PST-RB-5a** — Map `REKind` → `TT_*` equivalents. Read `rebus.y`,
  `rebus.h`, `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c` in full.
  Complete the mapping table above. Add any missing `TT_*` to `ast.h`.
  Record findings in State block. **No code changes yet.**

- [x] **PST-RB-5b** — Action bodies in `rebus.y` build `tree_t` directly.
  For each grammar rule currently building `RExpr*` / `RStmt*`:
  replace with `ast_node_new(TT_*)` + `expr_add_child` calls.
  Keep `RExpr*` downstream consumers unchanged for now (they will break
  at link/runtime — that's expected until 5d).
  SCRIP mirror: `parser_rebus.sc` produces the same `tree_t` shape.

- [x] **PST-RB-5c** — Delete `RExpr` / `RStmt` / `RProgram` structs and
  helpers: `rexpr_new`, `SAL`, `EAL`, `STAL`, and any `rexpr_free` /
  `rprogram_free` functions. `rebus.h` shrinks to the `TT_*` mapping and
  any remaining lexer helpers.

- [x] **PST-RB-5d** — Update downstream consumers to `tree_t`:
  `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`. Each walks `tree_t`
  nodes by `t` (kind) instead of `REKind`. `rebus_lower.c` grew
  significantly — it now handles all the control-flow lowering that the
  old `RStmt` struct carried implicitly.
  SCRIP mirror: `lower.sc` handles Rebus `tree_t` lowering.

- [x] **PST-RB-5e** — `parser_rebus.sc` reduced to pure-syntax statements
  only: 696 → 266 lines, **zero functions**. Tree is built solely from
  `shift`, `reduce`, plus the counter primitives `nPush`/`nInc`/`nPop`/
  `nTop`. All helper functions (`push_qlit`, `Push_qlit`, `decompose_call`,
  `decompose_sub`, `push_call_id`, `push_keyword`, `push_cursor` and their
  `Push_*` / `Decompose_*` wrappers) deleted; all SCRIP-side lowering
  (`lower_atom`, `lower_stmt`, `lower_function_decl`, `lower_record_decl`,
  `lower_case`, `lower_decl`, `new_label`, `emit_subj`, `emit_go`,
  `emit_lbl`, `emit_assign`, `emit_match`, `emit_subj_goSF`,
  `emit_subj_goS`, `emit_replace`) deleted. Driver replaced with simple
  `TDump` walk over the parse-root children (mirrors `parser_prolog.sc`
  / `parser_snocone.sc`). String body extracted by consuming the
  delimiting quote before `shift`, so `shift(*DQ_body, 'TT_QLIT')`
  captures the body alone. Uppercase normalization of identifiers
  dropped from parser; the future IR_SM/IR_BB lowering will handle case.

- [x] **PST-RB-5g** — Snocone-port subsystem suite triage.  Two runtime
  bugs fixed at one4all that were blocking the test_*.sc subsystem suite
  from passing.  Suite went from 13/20 to 15/20.

  **Bug 1 (sm_prog.c opnames[] table)**: a spurious `"SM_GEN_TICK"` entry
  at array position 65 shifted every name from position 65 onwards by 1.
  All `--dump-sm` output for `SM_CALL_FN` printed as `SM_SUSPEND_VALUE`,
  for `SM_RETURN` as `SM_CALL_FN`, for `SM_NRETURN` as `SM_FRETURN`, etc.
  This had been documented as "cosmetic" in `emit_net.c` but was
  actively misleading diagnosis.  Fix: remove the spurious entry; update
  the stale comment in emit_net.c.

  **Bug 2 (lower.c lower_name)**: `.fn(args)` lowered as
  `NAME_PUSH("fn")` instead of evaluating the call.  AST shape
  `(TT_NAME (TT_FNC value (TT_INDIRECT "@S")))` was being treated as
  if it were `(TT_NAME (TT_VAR foo))`, ignoring the function call.
  Effect: `Top = .value($'@S'); nreturn;` returned the *literal string
  "value"* wrapped as a NAMEVAL instead of dereferencing through the
  field accessor.  Fix: when the TT_NAME child is TT_FNC, lower as a
  plain call; the nreturn deref path then handles the value correctly.
  This is the minimum-viable fix — a fuller "function-result name
  handle" encoding (so `.fn(x) = newval` properly writes back through
  the field) is left for future work.

  Subsystem suite at HEAD after fix:
    PASS: global, case, assign, counter, stack, tree, ShiftReduce,
          TDump, ReadWrite, XDump, omega, arith, roman, strings, fence
          (15/20)
    FAIL: match (`notmatch` returns success on miss),
          Gen (statement-limit hit — likely real infinite loop),
          Qize (pre-existing SKIP via SL-3 SQize infinite loop),
          semantic (tests 5/6/8 — nInc/nTop interaction),
          trace (single-line output diff: `0  upd` vs `0? pd`)
          (5/20)

  Smoke gates protected: `smoke_rebus` 4/0, `smoke_scrip_all_modes` 2/0.

  one4all files touched: `src/lower/sm_prog.c`, `src/lower/lower.c`,
  `src/emitter/emit_net.c`.

Gates per rung: `smoke_rebus`, `smoke_scrip_all_modes`, `crosscheck_snobol4`.

---

## Done criterion

1. PST-RB-5a through 5d all checked [x]. ✅ COMPLETE.
2. `rebus.y` produces only `tree_t` — `RExpr*` / `RStmt*` / `RProgram*` gone.
3. All gate scripts green at baseline.
4. Beauty self-host byte-identical (Milestone 1 protected).
5. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 5 checked [x].

---

## Risks

- **`rebus_lower.c` growth** — it currently has thin lowering because
  `RStmt` carried implicit control flow. A new `lower_rebus_ctrl.c`
  may be opened if needed.

---

## State

```
watermark: PST-RB-5g complete 2026-05-17 (third session)
status: PST rungs 5a-5e ✅; 5g ✅ (opnames + lower_name fixes). Snocone subsystem suite 15/20 PASS at HEAD. SL-2 closed. SL-3/4/5 still open. Parser_*.sc still don't emit usable AST (SL-5).
next: per findings-5g "Next session" list — SPITBOL-test the 5 remaining subsystem failures (match, Gen, semantic, trace; Qize gated by SL-3), fix SCRIP source for each, then 6-function trace on parser_rebus.sc, then INCLUDE in Snocone parser.
findings-5a:
  - Mapping table above verified against rebus.y, rebus.h, rebus_lower.c.
  - No new TT_* kinds needed — all existing ast.h entries sufficient.
findings-5b:
  - rebus.y action bodies rewritten to ast_node_new(TT_*) + expr_add_child.
  - parser_rebus.sc SCRIP mirror updated to match tree_t shape.
findings-5c:
  - RExpr/RStmt/RProgram structs deleted. rexpr_new/SAL/EAL/STAL removed.
  - rebus.h now maps TT_* only.
findings-5d:
  - rebus_lower.c, rebus_emit.c, rebus_print.c all walk tree_t by t (kind).
  - lower.sc updated for Rebus tree_t lowering.
  - Gates: smoke_rebus green, smoke_scrip_all_modes green, crosscheck_snobol4 PASS=6.
findings-5e (2026-05-17):
  - parser_rebus.sc: 696 → 266 lines, zero functions, tree built solely via
    shift/reduce + counter primitives nPush/nInc/nPop/nTop.
  - parser_snobol4.sc: Lower_collect/Lower_run calls replaced by TDump for
    pure AST output (Snocone, Icon, Prolog, Raku, Rebus already AST-only).
  - corpus/SCRIP/lower.sc DELETED — will be re-translated from lower.c
    (which is changing rapidly) to produce IR_SM array and IR_BB tree.
  - corpus/SCRIP/lower_driver.sc DELETED — dead wrapper around removed lower().
  - one4all/src/frontend/prolog/prolog_lower.c: fixed missing
    `CODE_t *prolog_lower(PlProgram *pl_prog) {` function header on line 352
    that was orphaned by commit 8fee1957 (PST-PL-6d). Without this fix `make
    scrip` did not build.

findings-5f (2026-05-17, second session, Claude Opus 4.7 — SL-2 closed):
  SL-2 root cause was MISDIAGNOSED in 5e.  The earlier note "SCRIP Snocone
  runtime aborts with double-free heap corruption" pointed at the wrong
  layer.  The actual bug was a **heap use-after-free in snocone_parse.y's
  if-statement reduction**.  `sc_finalize_if_else_pst` read its CODE_t
  snapshot from `st->if_before_body` — a single shared slot on ScParseState
  that every nested `if_head` reduction overwrote.  With 3+ chained
  `else if` clauses (qize.sc's Qize function being the trigger that any
  parser loading qize.sc would crash on), the outer reduction's
  `sc_collect_body` walked STMTs that the inner reduction had already
  freed.  ASan pinned it at snocone_parse.y:840.  Fix: every `if_head`
  now allocates its own `struct IfHead` (via the already-existing
  `sc_if_head_new`), bison `%type <expr> if_head` → `%type <ifhead>`,
  finalizers read `h->cond` / `h->before_body` and free `h` on exit.
  Bison-regenerated `snocone_parse.tab.c`.

  `scripts/run_scrip_parser.sh` updated: qize.sc re-included, dead
  lower.sc / lower_driver.sc refs dropped, the stale "Append-through-
  function-parameter" comment replaced with the accurate post-mortem.

  Gates re-run: smoke_rebus 4/0, smoke_scrip_all_modes 2/0,
  crosscheck_snobol4 4/2.  The 4/2 is baseline — pattern_replace and
  beauty_omega fail without my changes too, confirmed via git-stash.

  AST dumps probe (Lon Q): all six SCRIP-hosted parsers were
  found to **hang silently at load time**, not error.  Bisected to
  `_qtag` (semantic.sc) falling through to SQize on identifier-shaped
  tag strings like 'TT_VAR' / 'TT_NUL' — and SQize has an infinite
  loop on inputs containing no apostrophe.  Fix: `_qtag` gained a
  fast-path `if (IDENT(REPLACE(t, "'", ""), t)) { _qtag = "'" t "'";
  return; }` that detects identifier-shape and wraps directly, bypassing
  SQize for the parser tag idiom.  REPLACE-based detection avoids a
  second SCRIP runtime bug (SL-4 below) where BREAK("'") / ARB "'" /
  ARB ANY("'") spuriously succeed on apostrophe-free input.

  After the `_qtag` fix all six parsers finish loading in under a
  second.  They do NOT yet produce valid AST dumps — snobol4/rebus/
  prolog/raku now emit "Error 5: Undefined function or operation" at
  load (1–10 occurrences depending on parser); snocone matches input
  but Pop returns null (no tree built by Shift/Reduce);
  parser_icon.sc:3 has a separate pre-existing snocone parse error.
  These remaining issues are downstream of SL-2 / SL-3, separate
  tickets.

  Sidecar audit (Lon Q): "zero functions" claims in this file and in
  GOAL-PST-ICN-RAKU.md were technically true of parser_*.sc files in
  isolation but misleading — icon_helpers.sc carries 5 functions
  (4 leaf-push + a notmatch redef), raku_helpers.sc carries 11
  (push_interp_str, dq_unescape, 9 finish_* counter-based assemblers).
  Today only parser_rebus.sc is genuinely sidecar-free.  Fixed wording
  in GOAL-PST-ICN-RAKU.md (rung PST-ICN-4b, §7 done-criterion, State),
  PLAN.md (PST: Icon+Raku row), and corpus/SCRIP/README.md (new
  "Per-language helper sidecars (transitional)" section).

  Three new SL tickets opened (in commit message + this State):
    SL-3: SQize infinite loop on apostrophe-free input
          (corpus/SCRIP/qize.sc:46-58).  Loop condition + replacement
          interaction doesn't reduce `str`.  Workaround: _qtag's new
          fast-path avoids triggering it for the common parser case.
    SL-4: SCRIP runtime pattern-matcher spuriously succeeds on
          BREAK("'") / ARB "'" / ARB ANY("'") when input contains no
          apostrophe.  Workaround: use REPLACE for apos-presence checks.
    SL-5: Parser AST dumps not yet correct.  Each parser_*.sc finishes
          loading after SL-2 fix but emits Error 5 ("Undefined function
          or operation") at load and/or fails to push a tree onto the
          value stack.  Likely shift/reduce wiring or EVAL-scope issue
          in semantic.sc's shift() builder.  No parser produces a
          usable AST dump today.

  Hand-off commit author: LCherryholmes (per RULES.md).
  Hand-off authored by: Claude Opus 4.7.

findings-5g (2026-05-17, Claude Opus 4.7 — Snocone subsystem suite triage):
  Strategy shift: instead of debugging the full parser_*.sc load stack
  end-to-end, get the smaller, self-contained Snocone-port subsystem test
  suite (~20 files at corpus/programs/snocone/demo/beauty/test/) green
  first.  Each test_<subsys>.sc inlines its own copies of the helpers it
  needs, so it isolates true runtime bugs from load-order issues.

  Baseline at HEAD: 13/20 PASS via
    bash scripts/test_beauty_snocone_subsystems.sh <subsys> ...

  Diagnosed and fixed two runtime bugs (see rung PST-RB-5g above):
    1. opnames[] table mis-aligned by spurious "SM_GEN_TICK" entry —
       every dumped opcode name from position 65 onwards was wrong.
       Documented as "cosmetic" in emit_net.c but actively misleading.
    2. lower_name treated TT_NAME(TT_FNC ...) the same as TT_NAME(TT_VAR),
       ignoring the function call entirely.  Caused .value($'@S') to
       lower as NAME_PUSH("value") instead of evaluating value($'@S').

  After fix: 15/20 PASS.  stack and ShiftReduce flipped from FAIL to PASS.

  Remaining failures (5):
    - match: notmatch test mis-classifies misses as PASS (negation bug).
    - Gen: statement-limit exceeded (suspected infinite loop in Gen body).
    - Qize: pre-existing — test_Qize.ref IS the SKIP placeholder for
            SL-3 (SQize infinite loop on apostrophe-free input).
    - semantic: nInc/nTop interaction tests 5/6/8 wrong; nTop type drift.
    - trace: single output diff: '0  upd' vs '0? pd' — likely a string
             escape / newline normalization quirk.

  Smoke gates protected: smoke_rebus 4/0, smoke_scrip_all_modes 2/0.

  Strategy for the parser_*.sc files: once the subsystem suite is fully
  green (or its remaining failures are diagnosed and isolated from the
  parser code path), instrument the 6 critical primitives —
  shift, reduce, nPush, nInc, nTop, nPop — with stderr trace lines
  (gated by SCRIP_DEBUG_PARSE env var) and run each parser against
  trivial input to watch the parse in action.  Then promote the
  multi-file load to a single file via an INCLUDE statement in the
  Snocone parser (parallel to SNOBOL4's -INCLUDE), removing the load-
  order question entirely.

  ⛔ RULE (binding on all future SCRIP/subsystem work in this goal):
  Never edit corpus .sc or .sno source to work around a SCRIP behavior.
  These programs have been working under SPITBOL for decades and are the
  oracle.  Workflow for every behavior question:
    1. Write the construct as a SPITBOL .sno program and run it under
       qemu-i386-static /home/claude/sbl32 prog.sno (install via
       one4all/scripts/install_spitbol_x32_runner.sh; needs
       qemu-user-static and libc6-i386).
    2. SPITBOL's output is the canonical truth.
    3. If SCRIP differs, fix SCRIP source in one4all (parser, lowering,
       SM interpreter, runtime — never the corpus).
  Both PST-RB-5g fixes were verified this way:
    • SPITBOL test /tmp/spitbol_test2.sno confirmed
      Top = .value($'@S'); :(NRETURN) returns INTEGER 42 to caller; my
      lower_name fix produces the same observable behavior in SCRIP.
    • Searched corpus for any `.fn(args) = rhs` write-side use of the
      name-handle form: zero hits.  So the minimum-viable read-side fix
      covers all corpus needs today.

  SPITBOL parity for the simpler `Top = value($'@S'); :(NRETURN)`
  (no leading dot): SPITBOL returns empty STRING; SCRIP at HEAD returns
  INTEGER 42.  SCRIP's nreturn handler is more lenient (passes non-name
  values through unchanged).  This existing divergence is unrelated to
  PST-RB-5g — no code in the corpus relies on it.  Flagged here for
  future SPITBOL-strict-mode work if Lon wants exact parity.

  one4all files touched (committed in PST-RB-5g hand-off):
    src/lower/sm_prog.c       — drop spurious "SM_GEN_TICK"
    src/lower/lower.c         — lower_name handles TT_FNC child
    src/emitter/emit_net.c    — update stale "cosmetic mismatch" comment

  Next session, in priority order:
    1. SPITBOL-test the 5 remaining subsystem failures and fix SCRIP for
       each:
         - match:    notmatch returns success on miss (negation logic).
         - Gen:      statement-limit exceeded; likely infinite loop in
                     Gen body — find the divergent loop.
         - semantic: nInc/nTop interaction tests 5/6/8 wrong; nTop type
                     drift (STRING vs INTEGER).
         - trace:    single output diff '0  upd' vs '0? pd' — likely a
                     newline/escape quirk in trace.sc output formatting.
         - Qize:     blocked by SL-3 (SQize infinite loop on
                     apostrophe-free input) — separate ticket.
    2. With suite at 19/20 (Qize still SL-3), apply the 6-function trace
       to parser_rebus.sc with tiny input; confirm AST emerges.
    3. Roll the trace to parser_snobol4 / snocone / icon / prolog / raku.
    4. Add INCLUDE statement support to the Snocone parser (mirror of
       SNOBOL4's -INCLUDE) so beauty.sc and parser_*.sc can replace the
       run_scrip_parser.sh load list with a single source file.

  Hand-off authored by: Claude Opus 4.7.
  Hand-off commit author: LCherryholmes (per RULES.md).
```

## Authorship

Drafted by Claude Sonnet 4.6, 2026-05-16.
PST-RB-5e + helpers by Claude Opus 4.7, 2026-05-17.
SL-2 fix + sidecar-claim corrections + _qtag SL-3/4 workaround by Claude Opus 4.7, 2026-05-17 (second session).
PST-RB-5g (opnames + lower_name, Snocone subsystem suite 13→15) by Claude Opus 4.7, 2026-05-17 (third session).
