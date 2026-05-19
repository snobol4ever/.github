# GOAL-PST-REBUS.md — Pure Syntax Tree: Rebus + parser_*.sc stabilization

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 5)
**Status:** Rebus PST rewrite ✅ done. Active work: stabilize parser_*.sc execution.

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

---

## ⛔ Binding rules

1. **SCRIP-mirror invariant** — every C-parser/lower change touches both C side AND the matching `corpus/SCRIP/parser_*.sc` / `lower.sc` (now deleted; lowering only on C side) in the same commit. Post-parse `tree_t` shape must match.
2. **Left-to-right child order** — all children in source token order.
3. **Never edit corpus to work around SCRIP behavior.** The corpus has run under SPITBOL for decades and is the oracle. Workflow:
   - Write the construct as `.sno`, run `qemu-i386-static /home/claude/sbl32 prog.sno` (install via `one4all/scripts/install_spitbol_x32_runner.sh` + `apt-get install -y qemu-user-static libc6-i386`).
   - SPITBOL output is canonical. If SCRIP differs, fix SCRIP source in `one4all` (parser / lowering / SM interp / runtime). Never the corpus.
4. **Pure-syntax allowed**: `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`, `ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.
   **Forbidden**: building `RExpr*`/`RStmt*`/`RProgram*`; scope lookup during parse; child reordering for positional semantics.

**⛔ Three Phase-1 facets** (per `GOAL-PARSER-PURE-SYNTAX-TREE.md § "The three Phase-1 facets"`):

- **F1 — `tree_t` is the sole information channel.** Rebus has the heaviest historical F1 burden of the six frontends: it built `RProgram` / `RDecl` / `RCase` / `RExpr` / `RStmt` C-structs as parser output, never touching `tree_t` in early designs. The PST-RB-5 / PST-RB-DECL-1..5 ladder has eliminated most of this; what remains is **all information must pass inside the tree — no side hustles** (binding 2026-05-19, see § PST-RB-DECL section below). RDecl/RCase still carry name/params[]/locals[]/initial/body as separate C struct fields; those must move onto `tree_t` children. The four audit-promoted rungs RB-C-2 (unless), RB-C-3 (case-IF wrapping), RB-C-4 (augop desugar), RB-C-5 (postfix-call inspect-and-mutate) are also F1 fixes — each replaces parser-side desugaring or kind-inspection with a pure tree shape.
- **F2 — `tree_t` has exactly four fields `t`, `v`, `n`, `c`.** Cross-cutting `PST-FIELD-1`/`PST-FIELD-2`. Rebus is not a primary `_id` consumer (no Rebus production sets `node->_id`), so PST-FIELD-2 is not gated on Rebus.
- **F3 — Children L→R in source-token order.** RB-C-1 ✅ (stmt_list_ne always-wrap). RB-C-5 (postfix-call inspect-`$1->t`-and-mutate-or-wrap) is F3-rule-2 violation — same fix pattern.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
# SPITBOL oracle (one-time):
apt-get install -y qemu-user-static libc6-i386
bash /home/claude/one4all/scripts/install_spitbol_x32_runner.sh
```

Gates (run after every rung):
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh             # expect 4/0
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh   # expect 2/0
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh      # baseline 4/2
bash /home/claude/one4all/scripts/test_beauty_snocone_subsystems.sh \
    global case assign match counter stack tree ShiftReduce TDump Gen \
    Qize ReadWrite XDump semantic omega trace arith roman strings fence
# Expect ≥15/20 at HEAD `4df6933b`. Goal: drive to 19/20 (Qize stays blocked by SL-3).
```

---

## 📖 SPITBOL manual — navigation cheatsheet (`spitbol-manual-v3_7.pdf`, 368 pp)

The manual is **scanned-quality TOC, clean body**. Extracting the whole thing wastes context. Use this map.

**One-time extraction:**
```bash
pdftotext -layout spitbol-manual-v3_7.pdf /tmp/spitbol.txt   # ~15k lines
```

**TOC lives at lines 147–290.** Ignore the page numbers in the TOC — they refer to printed pages, not text lines. Use the section-name jumps below instead.

**Where the actually-useful content sits in `/tmp/spitbol.txt`:**

| Need this | Section / Chapter | Anchor line(s) | grep query |
|---|---|---:|---|
| Operator priority tables (THE one canonical reference) | Ch 15 Operators | 7757, 7774 | `grep -n "Operator      Association"` |
| Unary `?` interrogation, `~` negation semantics | Ch 9 Unary Operators | ~5741 | `grep -n "Other Unary Operators"` |
| Pattern primitives (ABORT, ARB, BAL, FAIL, FENCE, REM, SUCCEED) | Ch 18 | 8683 | `grep -n "^Primitive Patterns$"` |
| Pattern-match algorithm + bead diagram | Ch 18 | 8718–8814 | `grep -n "Pattern-match.*algorithm"` |
| `&FULLSCAN`, `&ANCHOR`, `&MAXLNGTH`, etc. keyword effects | Ch 16 | 8074, 8141 | `grep -n "Unprotected Keywords"` |
| SUBJ ? PAT = REPL statement layout (SNOBOL4 column form) | Ch 14 | 7695 | `grep -n "Pattern-match"` |
| Pattern functions (ANY/ARBNO/BREAK/BREAKX/LEN/NOTANY/POS/RPOS/RTAB/SPAN/TAB) | Ch 19 | search by name | `grep -n "^      [A-Z]*$"` then narrow |
| Goto field `:S(LBL)` / `:F(LBL)` semantics | Ch 14 | 7768 | `grep -n "Goto field"` |
| EVAL/CODE run-time compile rules | Ch 9 | ~5187 | `grep -n "EVAL function"` |
| Data-type conversion matrix (string↔pattern↔code↔name) | Ch 17 | 8509+ | `grep -n "String Ü"` (Ü = arrow glyph) |
| Operator extensions: `A = B = C`, embedded `(B ? C = D)`, alt-eval `(LT(I,J) I, GT(I,J) J)` | Ch 15 tail | ~7820 | `grep -n "Operator.*Extensions"` |
| `Differences from SNOBOL4+` (gotchas) | Appendix C | 14580+ | `grep -n "Features Implemented Differently"` |

**Operator priority (memorize this; it's THE table the parser cascade must mirror):**

| Pri | Op | Assoc | Meaning |
|---:|---|:---:|---|
| 0 | `=` | right | Assignment |
| 1 | `?` | left | **Pattern match** |
| 2 | `&` | left | OPSYN-able |
| 3 | `|` | right | Pattern alternation |
| 4 | space | right | Concatenation / pattern subsequent |
| 5 | `@` | right | OPSYN-able |
| 6 | `+`, `-` | left | Add / subtract |
| 7 | `#` | left | OPSYN-able |
| 8 | `/` | left | Divide |
| 9 | `*` | left | Multiply |
| 10 | `%` | left | OPSYN-able |
| 11 | `^`, `!`, `**` | right | Exponentiation |
| 12 | `$`, `.` | left | Immediate / conditional pattern-assign |
| 13 | `~` | right | OPSYN-able |

Unaries: all equal priority, higher than any binary. Set: `?`, `~`, `+`, `-`, `*`, `$`, `.`, `!`, `%`, `/`, `#`, `@`.

**Rules of thumb:**
- For an operator/precedence question: jump to the Ch 15 table at line 7757 and stop. Don't re-read prose.
- For pattern semantics: Ch 18 short prose at 8683 + algorithm at 8718. Don't reload the bead diagram unless you forgot what backtracking looks like.
- For "does SPITBOL have feature X": Appendix C first (it's terse); body text only if Appendix C doesn't say.
- For a keyword's effect: Ch 16 (8074+) is denser than Ch 9's narrative.
- Skip Chapters 1–2 (installation), 10–11 (debugging/closing), 13 (running spitbol from a shell), 20 (perf notes), and the giant Appendix sections D–G unless you have a specific reason.

---

## ⛔ SCRIP mirror work — Rebus orientation

**C side must be clean before parser_rebus.sc mirror work.** The outstanding C violation is the in-place stmt_list append in `rebus.y` (see RB-C-1 below). Complete that rung first.

**When starting parser_rebus.sc mirror work:** Read `SNOBOL4-SNOCONE-PRIMER.md` in full. Learn Snocone expression syntax from the SPITBOL manual and control-flow syntax from `corpus/SCRIP/parser_snocone.sc`. The goal is to replace every tree-building function in `parser_rebus.sc` with pure `shift`/`reduce` calls only — no `Push`, `Pop`, `Append`, `Tree`, or helper functions that inspect children. Every grammar production: leaf tokens → `shift`/`shift_val`, then one `reduce(TT_KIND, n)`. Counter discipline (`nPush`/`nInc`/`nTop`/`nPop`) is permitted in grammar rules for variable-arity reduces.

---

## Active rungs

- [x] **RB-C-1 — Fix `stmt_list_ne` in-place append in `rebus.y` (C-side L-to-R prerequisite).** ✅ 2026-05-18 (Sonnet 4.6, one4all `0da9ec20`)
  `stmt_list_ne` currently mutates `$1` in place: the `stmt_list_ne compound_stmt` arm strips children from `$2` and appends them to `$1` via `expr_add_child($1, $2->c[i])` — a direct violation of the left-to-right always-wrap invariant.
  Fix: change both `stmt_list_ne` arms to always-wrap — every reduction produces a fresh `TT_PROGRAM` node wrapping the previous list and the new statement:
  ```c
  stmt_list_ne stmt ';'        { tree_t*p=ast_node_new(TT_PROGRAM); expr_add_child(p,$1); expr_add_child(p,$2); $$=p; }
  stmt_list_ne compound_stmt   { tree_t*p=ast_node_new(TT_PROGRAM); expr_add_child(p,$1); expr_add_child(p,$2); $$=p; }
  ```
  Produces a right-leaning chain; re-flattening is a lower concern.
  Also verify `RDecl` fully replaced by `tree_t` (PST-RB-5b claim — confirm no `RDecl*` remains as parser output).
  **Phase 1 only — no `parser_rebus.sc` changes in this rung.** Record `⚠ MIRROR-GAP-RB-C-1` in State.
  Gates: `test_smoke_rebus.sh` 4/0, `test_smoke_scrip_all_modes.sh` 2/0, `test_crosscheck_snobol4.sh` 4/2.

- [x] **RB-C-2 — `unless_stmt` synthesizes TT_NOT-wrapped condition (audit Rb3).** ✅ 2026-05-19 (Sonnet 4.6, one4all `83bc4ab3`)
  `rebus.y:317–328` builds `TT_IF(TT_NOT(cond), then)` from `unless cond then body`. The `TT_NOT` wrap is a synthesized kind — no `T_NOT` source token exists. Strict reading of §⛔ rule 3: synthesized non-source-token kind.
  **Fix:** introduce a dedicated `TT_UNLESS` kind in `tree_e` and produce `TT_UNLESS[cond, then]` directly. Let `lower_unless` (or a `lower.c` switch arm) desugar to negated branch at IR emit time. Parser stays syntax-faithful: the source token `unless` becomes the node kind directly.
  Same pattern as Raku R11 (PRF-12-unless).
  **Phase 1 only — no `parser_rebus.sc` changes.** Records `⚠ MIRROR-GAP-RB-C-2` in State.

- [x] **RB-C-3 — `case_stmt` synthesizes TT_IF per clause (audit Rb4).** ✅ 2026-05-19 (Sonnet 4.6, one4all `ccc11220`)
  `rebus.y:388–407` walks the off-tree `RCase` linked list and builds a fresh `TT_IF` node per clause: `TT_CASE[expr, TT_IF(guard, body), TT_IF(guard, body), …, TT_IF(TT_NUL, body_default)]`. Each `TT_IF` wrapper is synthesized — the source had only `guard:body` per clause (no `if`/`then` source tokens).
  **Fix:** flat alternating `TT_CASE[expr, guard0, body0, guard1, body1, …, TT_NUL, body_default]` shape. Lowerer stride-2 loop. Verified: named/default dispatch correct at runtime.
  **Phase 1 only — no `parser_rebus.sc` changes.** Records `⚠ MIRROR-GAP-RB-C-3`.

- [x] **RB-C-4 — Augmented-assignment operators desugar in parser (audit Rb5).** ✅ 2026-05-19 (Sonnet 4.6, one4all `0458da59`)
  `rebus.y:449–470` — `+:=` / `-:=` / `||:=` actions each build `TT_ASSIGN[TT_VAR(strdup($1->v.sval)), TT_ADD/SUB/CAT($1, $3)]`. Three violations: LHS duplicated; sval stolen from `$1`; parser-side desugaring.
  **Fix:** `TT_AUGOP(lhs, rhs)` with `v.ival = AUGOP_ADD/SUB/CONCAT`. `lower_tree_expr` TT_AUGOP arm clones lhs and builds `TT_ASSIGN(lhs, TT_op(lhs_clone, rhs))`. Verified: `x+=5`, `x-=3`, `s||=' world'` all correct.
  **Phase 1 only — no `parser_rebus.sc` changes.** Records `⚠ MIRROR-GAP-RB-C-4`.

- [x] **RB-C-5 — `postfix_expr '(' arglist ')'` inspects $1 kind and mutates $1 (audit Rb6).** ✅ 2026-05-19 (Sonnet 4.6, one4all `2a9aa511`)
  `rebus.y:551–569` — inspects `$1->t == TT_VAR` and forks: steals `$1->v.sval` for named-call path; different tree shapes for same source operator `(...)`.
  **Fix:** always `TT_FNC[callee=$1, arg0, arg1, ...]`. `lower_tree_expr` TT_FNC arm: when `v.sval=NULL` and `c[0]` is TT_VAR, extracts name and skips `c[0]` in children — preserving named-call semantics. Verified: `add(3,4)→7`, `SIZE("hello")→5`.
  **Phase 1 only — no `parser_rebus.sc` changes.** Records `⚠ MIRROR-GAP-RB-C-5`.

- [~] **PST-RB-PRE-BEAUTY — Fix beauty.sno self-host blockers (Milestone 1 unblock).**
  Lon directive 2026-05-17: "If beauty.sno demo does not work first, then you are wasting your time probably. Check it first and get it running first."
  
  **Status:** PARTIAL — first bug fixed (Opus 4.7 this session, 2026-05-17).
  
  **Bug #1 (FIXED, one4all `bad0fffd`): `upr(upr)` shadow-parameter recursion.**
  `interp_eval.c:2847` TT_VAR fall-through called `APPLY_fn(name, NULL, 0)` when `NV_GET_fn(name)` returned NULVCL. This broke the SNOBOL4 idiom `DEFINE('upr(upr)')` (function name = parameter name): when parameter set to NULVCL on entry, the fallback recursively called the outer function with no args → infinite recursion → segfault in beauty.sno self-host.
  Fix: added `is_current_frame_local()` helper in `interp_call.c` walking `CallFrame::saved_names[]` (which already records retname + params + locals). interp_eval suppresses the function-call fallback when the TT_VAR name is a current-frame param/local. Declared in `interp_private.h`. Total diff: +30 lines, 3 files.
  Verification: `upr('hello')` returns `HELLO`; `upr('')` returns empty. All gates hold floor at HEAD: smoke_snobol4 6/1, smoke_rebus 4/0, smoke_scrip 2/0, smoke_icon 5/0, smoke_snocone 5/0, smoke_prolog 5/0, smoke_raku 5/0, crosscheck_snobol4 4/2, subsystem_suite 19/1.
  Beauty self-host: still 0 lines, but the crash signature changed from segfault to infinite loop downstream (Bug #2). Net progress: the `upr` recursion no longer blocks beauty.
  
  **Bug #2 (REFRAMED CLI-3M-9 2026-05-18): SUBJ-PAT split for mode 2.**
  PST-SN4-1b (2026-05-16) moved the SUBJ-PAT-REPL statement layout split out of the SNOBOL4 parser and into `lower.c`. This runs in modes 2/3/4 (SM/JIT/emit). Mode 1 (`interp_exec.c`) is now **deleted** (CLI-3M-9). The fix no longer needs to mirror `lower.c` logic in `interp_exec.c` — that file doesn't exist. The real question is whether mode 2's `lower.c` SUBJ-PAT split correctly handles the `TT_SEQ-with-pattern-as-tail` shape in all cases. If `smoke_snobol4 pattern` still fails under `--interp`, the bug is in `lower.c`'s split logic or `sm_interp.c`'s handling of the lowered SM opcodes — not in a dead mode-1 path.
  
  **Bug #3+ (UNKNOWN):** Likely additional issues will surface after Bug #2 lands. SN-7 gate baseline this session start: 22/29. Goal: strictly increase.
  
  **Acceptance criteria for PST-RB-PRE-BEAUTY:**
  1. beauty.sno self-host (`scrip --interp beauty.sno < beauty.sno`) produces >0 lines of output.
  2. SN-7 gate `test_gate_sn7_beauty_self_host.sh` PASS count strictly increases from baseline 22/29.
  3. All PST-REBUS gates green at floor: smoke gates above + subsystem suite ≥19/1 + crosscheck 4/2.
  4. Milestone 1 byte-identity remains the long-term target (not gated here; this rung is "unblock to non-zero output").
  
  **Beauty test suite — explicit programs:**
  `corpus/programs/snobol4/demo/beauty/` contains 17 `*_driver.sno` programs + `beauty.sno` itself. Driver list: assign, case, counter, Gen, match, omega, Qize, ReadWrite, semantic, ShiftReduce, stack, TDump, trace, tree, XDump, global. The SN-7 gate (`test_gate_sn7_beauty_self_host.sh`) runs each × 3 modes (ir/sm/jit) = 51 total. Mode-4 (emit) is tracked separately via `test_gate_em_beauty_subsystems_mode4.sh`.

- [x] **PST-RB-5h — Snocone-port subsystem suite to 19/20.** ✅ 2026-05-17 (Opus 4.7)
  15/20 → **19/20** PASS (Qize stays SKIPped under SL-3 as designed). The narrative "5 separate failures" (match, Gen, semantic, trace, Qize) collapsed: **one root cause flipped 4 of them.**
  Root cause: `lower_scan` in `src/lower/lower.c` unconditionally emitted Icon scanning-environment opcodes (`ICN_SCAN_PUSH`/`ICN_SCAN_POP`) for `TT_SCAN`. Both Icon and Snocone parsers reduce `?` to `TT_SCAN` — but Snocone `s ? pat` is **SNOBOL4 pattern matching** per SPITBOL Ch. 18 (binary op priority 1, left-assoc), not Icon scan-env. Wrong dialect meant `if (s ? p)` never set `last_ok`, so the subsequent `SM_JUMP_F` always fell through.
  Fix: dispatch on `g_lang` in `lower_scan`. Icon keeps `ICN_SCAN_PUSH/POP`; non-Icon mirrors the statement-level match path at `lower_stmt` line ~1306 (`SM_EXEC_STMT` with pattern DCG), then pushes an empty placeholder so `lower_if_stmt`'s `SM_VOID_POP` has something to consume. Flipped: match (3 tests), trace (1 test), Gen (used `?` internally, hit same wrong-branch path), semantic (same). Subsystems passing: 16 → 19.
  Sweep also landed: `snocone_parse.y` AST_* → TT_* (29 names, 89 occurrences; bridge `#define`s deleted from regenerated `.tab.c`); `snocone_lex.c` AST_* goto-labels → LX_* (45 names, 101 occurrences — they were lexer-state labels, never AST kinds).
  Watermark: one4all `1e6557c1`. Gates green (smoke_rebus 4/0, smoke_scrip 2/0, smoke_icon 5/0, smoke_snocone 5/0, smoke_snobol4 6/1 baseline with pre-existing `pattern` test fail unrelated to this rung, crosscheck_snobol4 4/2 baseline, unified_broker 19/30 baseline).

- [x] **PST-RB-5i-PRE — CASE-SENSITIVE-ONLY sweep.** ✅ 2026-05-17 (Opus 4.7, emergency handoff)
  one4all `d432ed6f`. CSO-1..CSO-7 landed as a single commit (emergency
  handoff — combined what was intended as two orthogonal commits). All
  gates held at baseline floor: smoke_rebus 4/0, smoke_scrip 2/0,
  smoke_icon 5/0, smoke_snocone 5/0, smoke_snobol4 6/1, crosscheck 4/2,
  beauty_snocone_subsystems 19/1.
  - **CSO-1** ✅ baseline snapshot captured.
  - **CSO-2** ✅ fold infra deleted in snobol4.l + scrip_cc.h.
  - **CSO-3** ✅ sno_fold_name() calls stripped from rt.c, eval_code.c,
    snobol4.c, interp_{ref,call,exec,eval}.c, prolog_driver.c,
    rebus_lower.c, raku_driver.c, icon_driver.c, sm_jit_interp.c,
    sm_interp.c (47 changes).
  - **CSO-4** ✅ strcasecmp/strncasecmp → strcmp/strncmp across all
    identifier-shaped comparisons: snobol4.y (pat_prim_kind),
    snobol4_stmt_rt.c, raku_builtins.c, icn_value.c,
    interp_{call,eval,data}.c, CMPILE.c (now archived), prolog_lower.c,
    rebus.l (else/do/then keyword check), icon_lex.c (IMPORT/EXPORT),
    icn_main.c (import/IMPORT directive), sm_jit_interp.c (_SET suffix),
    lower.c (return-kind dispatch, ITEM, RETURN/FRETURN/NRETURN),
    polyglot.c (polyglot block tags). resolve_include_path's
    case-insensitive directory-walk fallback deleted entirely (was
    identifier-folding at the filesystem boundary).
  - **CSO-5** ✅ _usercall_hook uppercase-fallback (toupper loop at
    interp_hooks.c:64-68) deleted.
  - **CSO-6** ✅ --case-sensitive becomes a no-op (still accepted for
    backward-compat in test scripts); --fold-case is rejected with a
    stderr message; opt_case_sensitive var and sno_set_case_sensitive()
    call removed; help text cleaned.
  - **CSO-7** ✅ &CASE is read-only (per Lon directive 2026-05-17):
    reads return INTVAL(0) [polarity per SPITBOL Ch.16 line 7891:
    &CASE=1 means folding ON, 0 means folding OFF — scrip is
    permanently folding-OFF]. Writes raise Error 10 ('&CASE is
    read-only; SCRIP is case-sensitive only'). kw_case global fully
    deleted (snobol4.{c,h}, snobol4_argval.c VARVUP_fn simplified,
    polyglot.c kw_case=1 init removed).
  - **CSO-8** ✅ rebuild + gate sweep + push. CMPILE.c/CMPILE.h moved
    to archive/frontend/snobol4/ alongside util_compare_cmpile_vs_bison_ir.sh
    (CMPILE was already disconnected from the build; util script
    invoked a non-existent --dump-ast-cmpile flag).
  Generated .tab.c/.lex.c regenerated via
  regenerate_parser_and_lexer_from_sources.sh (bison 3.8.2, flex 2.6.4).
  VERIFIED zero strcasecmp/strncasecmp/sno_fold_*/fold_strbuf/kw_case
  remain in src/.

- [ ] **PST-RB-5i-PRE-CORPUS — Corpus case-canonicalization sweep. NEXT.**
  Lon prediction 2026-05-17: 'I bet now you must fix a slew of *.sno,
  *.inc, and *.sc files which fail due to the case restriction.'
  Sweep every .sno/.inc/.sc/.icn/.pl/.reb/.raku in SCRIP-owned corpus
  paths (corpus/programs/snobol4/{beauty,demo,crosscheck},
  corpus/programs/snocone/demo/beauty, etc.). Any file triggering
  Error 5 (Undefined function or operation) or Error 7 (Unknown
  keyword) post-CSO is a candidate. Triage rule: (a) if SPITBOL
  `sbl -bf` runs it cleanly, the identifier reference is already
  case-consistent — re-run scrip to confirm; (b) if SPITBOL with `-bf`
  also fails, source uses mixed-case references that worked only under
  &CASE=1 folding — canonicalize to one consistent case at every use
  site, preferring whichever case the definition site uses. Never
  tolerate &CASE=0 in source (now a no-op at runtime); &CASE=1
  assignments raise Error 10 at runtime (correct — caller must remove).
  Acceptance: gates at floor, no .sno/.inc/.sc triggers Error-5-from-
  fold-loss, new test_corpus_case_audit.sh lands.
  Known specifics already surfaced:
  - beauty.sno + Qize.inc/case.inc/global.inc: `:F(error)`,
    `:F(err)` references where no `error`/`err`/`ERROR` label is
    defined. SPITBOL tolerates these (F-branch never taken in normal
    runs); scrip's labtab_resolve is more pessimistic. See PST-RB-NEXT-LABTAB.

- [ ] **PST-RB-NEXT-BB-CACHE — Cache pattern EXEC blocks; separate
    DATA allocation; never re-emit BB sequences for `*Var`, `*(expr)`,
    EXPRESSION, CODE datatypes.**
  Lon directive 2026-05-17. Root cause of Qize subsystem failure:
  bb_build_flat / bb_build_brokered (emit_bb.c:1658-1685) allocate
  FLAT_BUF_MAX=256KB per pattern compilation from a non-recyclable
  bump pool (bb_pool.c). They are called from stmt_exec.c every time
  a statement executes — including inside while-loops with pattern
  matches — so 256MB pool / 256KB = 256-pattern hard cap. Qize's
  while-loop bodies hit this. SPITBOL on Qize_driver.sno gives the
  canonical 5-PASS output; the test_Qize.ref had been quietly edited
  to print 'SKIP: blocked by SB-6.E.7-H rollback bug' (a corpus
  workaround that violates 'fix SCRIP not the corpus' rule).

  Two-phase fix:
  - **Phase A** — Add structural-hash cache for pattern ASTs in
    emit_bb.c. bb_build_flat/bb_build_brokered consult cache first
    (key = recursive hash of kind + child count + child hashes +
    literal values). Hit → return cached bb_box_fn + freshly allocate
    only a DESCR_t scratchpad; miss → emit/seal/insert. Per-statement
    re-execution reuses EXEC; only scratch is new.
  - **Phase B** — For the four named datatypes (`*PATRN_var`,
    `*(expr)`, EXPRESSION, CODE), route to a dedicated builder that
    knows the EXEC template is type-fixed, takes the value's DESCR_t
    as an argument, and allocates only the local data slots. Avoid
    the pattern-emitter path entirely. Rationale (per Lon):
    'all they need is new local allocations, not both EXEC and DATA
    parts recreated.'

  Acceptance: Qize subsystem passes 5/5 under restored canonical
  test_Qize.ref; subsystem suite 20/20; bb_pool headroom >50% on full
  beauty self-host; Milestone 1 byte-identity preserved (or improved).

- [ ] **PST-RB-NEXT-LABTAB — labtab_resolve undefined-label policy.**
  lower_ctx.c:50-64 (labtab_resolve) routes undefined-label patches
  to `p->count - 1` (end-of-program) and warns. SPITBOL with `-bf`
  on the same corpus produces correct output despite the same
  undefined labels because the F-branch is never taken in practice
  (the labels exist as 'this should never happen' fail-throughs).
  scrip should either: (a) route to a runtime-failure trap that
  matches SPITBOL semantics, or (b) defer the label-undefined error
  to first execution rather than at lower-time. Surfaced during
  Milestone 1 verification on beauty.sno self-host post-CSO; scrip
  produces 0 lines whereas SPITBOL produces 622. Pre-existing
  breakage (GOAL-LANG-SNOBOL4.md lines 270-285), not a CSO regression.


  Lon command 2026-05-17, recorded as ABSOLUTE RULE in `RULES.md` ("SCRIP IS CASE-SENSITIVE. NO FOLDING. ANYWHERE."). Execute this sweep before resuming any further parser_*.sc work — the `rt_bb_arbno` ζ corruption that blocks 5i acceptance lives downstream of pattern-matcher code that may itself touch fold paths during EVAL, and a clean case-only baseline removes a class of noise from that diagnosis.

  **Done when:**
  1. `grep -rn "sno_fold_name\|sno_fold_on\|fold_strbuf\|strcasecmp\|strncasecmp\|sno_set_case_sensitive\|sno_get_case_sensitive\|--case-sensitive\|--fold-case" src/` returns only legacy oracle directories (SPITBOL, CSNOBOL4 — exempt) and removal commit's own comment trail.
  2. `&CASE` keyword assignment is rejected or no-op-with-warning; reads return 1 sentinel.
  3. All gates green: smoke_rebus 4/0, smoke_scrip 2/0, smoke_icon 5/0, smoke_snocone 5/0, smoke_snobol4 ≥6/1 baseline, crosscheck_snobol4 4/2 baseline, beauty_snocone_subsystems 19/20.
  4. **Milestone 1 invariant** — beauty.sno self-host byte-identical, md5 `abfd19a7a834484a96e824851caee159`, 646 lines. MUST hold across every sub-rung.

  **Sites to sweep** (file → action):
  - `src/frontend/snobol4/snobol4.l` — delete `sno_fold_on`, `sno_set_case_sensitive`, `sno_get_case_sensitive`, `sno_fold_name`, `fold_strbuf` and every call site. Lex passes identifiers through verbatim.
  - `src/runtime/snobol4/snobol4.c` — delete `sno_fold_name` calls in `sno_DATA_register` (~lines 1506, 1518, 1527), `_VALUE_` (~1671), `register_fn` path (~2793, 2805).
  - `src/runtime/snobol4/eval_code.c` — delete `sno_fold_name` calls at lines 118, 129, 239, 281.
  - `src/runtime/rt/rt.c` — delete `sno_fold_name` calls at lines 933, 940, 962, 976, 1109.
  - `src/driver/interp_data.c` — `strcasecmp` → `strcmp` in `sc_dat_find_type` (line 48), `sc_dat_find_field` (line 55). **First non-no-op site; may surface test regressions for triage.**
  - `src/driver/interp_hooks.c` — delete `_usercall_hook` uppercase-fallback at lines 64-68 (toupper loop + second `label_lookup(_uf)`). **Second non-no-op site; same triage rule.**
  - `src/driver/scrip.c` — delete `--case-sensitive` arg parsing (line 115), `--fold-case` arg parsing (line 116), `sno_set_case_sensitive(opt_case_sensitive)` call (line 119), the `opt_case_sensitive` variable (line 88), help text mentioning these (line 176).
  - `&CASE` keyword in `src/runtime/snobol4/snobol4.c` — assignment becomes no-op-with-warning; reads return 1 sentinel.

  Also incidentally:
  ```bash
  grep -rn 'toupper\|tolower' src/ | grep -v 'UCASE\|LCASE\|alphabet\|test_\|demo_'
  ```
  Triage each; delete loops operating on identifier-shaped strings (keep ones building `&UCASE`/`&LCASE` keyword values — those are legitimate strings).

  **Sub-rungs (execute in order, single commit each):**
  1. CSO-1 — snapshot baseline gates. The numbers are the floor; sweep must hold them.
  2. CSO-2 — delete fold infrastructure in `snobol4.l`. Rebuild. Gates expected green (default was already `sno_fold_on=0` since SN-31).
  3. CSO-3 — delete `sno_fold_name` calls in `snobol4.c`, `eval_code.c`, `rt.c`. Rebuild. Gates.
  4. CSO-4 — `strcasecmp` → `strcmp` in `interp_data.c`. **Real behavior change.** Gates; triage failures (corpus tests using mixed-case field references either get case-corrected or moved to a future `legacy/` subdir).
  5. CSO-5 — delete `_usercall_hook` uppercase-fallback in `interp_hooks.c`. **Real behavior change.** Same triage.
  6. CSO-6 — delete `--case-sensitive`/`--fold-case` CLI in `scrip.c`. Update help text. Gates.
  7. CSO-7 — `&CASE` keyword: assignment no-op-with-warning, reads return 1.
  8. CSO-8 — final acceptance: full gate sweep, **beauty.sno byte-identity check** (the invariant), push.

  **Risks:**
  - **EVAL'd strings with mixed-case identifiers** — `EVAL("foo() + Foo()")` is now two distinct names. Search corpus for EVAL with embedded identifiers; canonicalize at source.
  - **Cross-language polyglot statements** — a `.sno` block calling a Snocone `foo()` as `FOO()` was fold-resolved; now it's a missing-name error. Build-time grep + manual triage.
  - **Milestone 1** is the must-not-break invariant. beauty.sno corpus has been running case-sensitive since SN-31, so it should hold — but verify at CSO-8.

  After CSO-8 lands → return to PST-RB-5i below and resume rt_bb_arbno ζ-corruption triage.


- [ ] **PST-RB-5i 🔄 — Parser AST validation: parser_*.sc dump matches C-side tree_t dump.**
  **Status (2026-05-17, Opus 4.7):** SL-5 root cause identified and partially fixed; downstream parser-runtime crash blocks acceptance. **BLOCKED behind PST-RB-5i-PRE (CSO sweep).**
  Landed this session:
  1. **C-side `--dump-ast`** now works for rebus / icon / prolog / raku / snocone / snobol4 (was lang_snocone only at `scrip.c:273`). With this fix, 5 of 6 frontends emit usable canonical `tree_t` trees. Prolog frontend segfaults on `:- initialization(...)` / `findall` files — separate frontend bug, not 5i. `rung01_hello_hello.pl` is the working prolog sample.
  2. **BB pattern buffer caps raised** so parser_*.sc compound patterns fit:
     - `FLAT_BUF_MAX` 16K → 256K (`src/emitter/emit_bb.c`).
     - `BB_POOL_SIZE`  4MB → 64MB (`src/processor/bb_pool.h`).
     Without these, `parser_snocone.sc` hits `bb_emit_byte: buffer overflow at pos=16384` at load.
  3. **SL-5 ROOT CAUSE: `_builtin_DATA` did not register field-accessor functions.**
     `_builtin_DATA` (`src/driver/interp_data.c`) populates `sc_dat_types[]` only. `_DATA_` in `src/runtime/snobol4/snobol4.c` populates `_func_buckets[]` (the SNOBOL4 function table) with each field-accessor closure. Both are registered as the `"DATA"` builtin via `register_fn` — `_builtin_DATA` wins because `scrip.c:327` runs after `SNO_INIT_fn()`. Net effect: `struct link_counter { next, value }` registered `value` in sc_dat_types[] only, while `APPLY_fn` (called from SM_CALL_FN) searches `_func_buckets[]` first. Hence "Error 5: Undefined function or operation" with `name='value'` from every `IncCounter()` invocation in parser_*.sc.
     Fix: extracted `_DATA_`'s body into non-static `sno_DATA_register` and chained `_builtin_DATA` through it. Both tables now populated. `value()` resolves. Per RULES "casing belongs at the ingress layer" the `sno_fold_name(spec)` at `_builtin_DATA` ingress was also removed; the remaining `sno_fold_name` calls in `sno_DATA_register` are no-ops under default `--case-sensitive` mode (the project default since SN-31) and left in place pending broader audit.
  4. **APPLY_fn diagnostic** added: `SCRIP_DEBUG_APPLY=1 ./scrip ...` prints `[apply-err5] unresolved '<name>' (nargs=N)` before raising Error 5. Stays silent under normal runs. (`src/runtime/snobol4/snobol4.c`).
  Remaining wall (not fixed this session — separate rung):
  - **parser_rebus.sc / parser_snocone.sc segfault in BB pattern runtime** during `Src ? Compiland` match. Crash signature: `rt_bb_arbno` called with garbage `zeta` after `bb_deferred_var → bb_build_brokered → emit_label_initf → __vsnprintf_internal` on a corrupted ζ struct. The Error-5 cliff was hiding this — it is now visible because patterns execute further. Either ARBNO state-machine reentry, or BB pattern descriptor corruption when the brokered builder runs on a top-level compound pattern referenced via `*` deferred eval. Needs Byrd-box runtime triage.
  - Steps 1–5 of original 5i procedure still TBD: with the runtime crash, no parser_*.sc emits a tree yet for diff against C-side `--dump-ast`. Sample picks (≤10-line each) recorded for future session:
    | Lang | Sample | C-side `--dump-ast` |
    |---|---|---|
    | rebus | `corpus/programs/rebus/parser/paren.reb` | ✅ 13-line tree |
    | snobol4 | `corpus/programs/snobol4/parser/unary_not.sno` | ✅ 2-line tree |
    | snocone | `corpus/programs/snocone/corpus/sc1_literals.sc` | ✅ 3-line tree |
    | icon | `corpus/programs/icon/parser/fail_stmt.icn` | ✅ 11-line tree |
    | prolog | `corpus/programs/prolog/rung01_hello_hello.pl` | ✅ 2-line tree (avoid `findall`/`initialization` files — segfault prolog_compile) |
    | raku | `corpus/programs/raku/parser/str_chars.raku` | ✅ 15-line tree |
  Acceptance unchanged: each parser_*.sc emits a `tree_t`-shape-equivalent dump for its chosen sample, validation script `scripts/test_parser_ast_match.sh` lands.

- [ ] **PST-RB-5j — 6-function parser trace.**
  Instrument the six critical primitives — `shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop` — with stderr trace lines gated by env `SCRIP_DEBUG_PARSE`. Implement once in `corpus/SCRIP/semantic.sc` (`shift`, `reduce`) and `corpus/SCRIP/counter.sc` (`nPush`/`nInc`/`nTop`/`nPop`). Run each parser against trivial input with `SCRIP_DEBUG_PARSE=1` and watch the parse unfold; this is the diagnostic foundation for fixing remaining parser_*.sc bugs once subsystem suite is green.
  Acceptance: traces emit; documented sample trace for `parser_rebus.sc` on `x = 1` checked in to a `docs/` location.

- [ ] **PST-RB-5k — Snocone `INCLUDE` statement.**
  Add `INCLUDE 'file.sc'` (or `-INCLUDE`, mirroring SNOBOL4) to the Snocone parser so the multi-file `run_scrip_parser.sh` load list collapses to a single source. Eliminates the entire load-order question. Implementation parallels `sno_add_include_dir` / SNOBOL4 lex `INCL` state.
  Acceptance: `parser_rebus.sc` plus a small `parser_rebus_main.sc` that pulls in `global.sc`, `counter.sc`, etc. via INCLUDE produces the same behavior as the current shell-loaded chain. Gate: subsystem suite, smoke, crosscheck, plus a new `test_parser_include.sh`.

---

## ⛔ PST-RB-DECL — Convert `RDecl` / `RCase` info fully into the tree

**Audit reference:** `PST-LR-AUDIT.md § Scan 5 (Rebus)`, sections 5.1 (off-tree machinery) and 5.4 (case_stmt synthesizing TT_IF per clause).

**The §⛔ principle (binding 2026-05-19):** **all information must pass inside the tree — no side hustles.** The parser's output is `tree_t` and only `tree_t`. Auxiliary structs that carry parser-output data (off-tree linked lists, RDecl chains, RCase clause lists, name+arity+local+initial+body strung together as struct fields) are side channels — they violate the principle. They must be eliminated, with every field's information re-encoded as `tree_t` children or `v.sval/ival/dval` value-decoding at a fresh leaf.

**Background — what was closed in PST-RB-5a–5d (2026-05-16):**

| Removed | How info moved into the tree |
|---------|------------------------------|
| `RExpr*` | All expression productions now build `tree_t` directly via `ast_node_new(TT_*)` / `expr_add_child`. |
| `RStmt*` | All statement productions now build `tree_t`. |
| `RProgram*` (the outer-most type — distinct from the **inner** `RProgram` struct that survives as the off-tree wrapper around the decl list — see below) | Statements emit `tree_t` directly. |

**What still survives off-tree** (per `rebus.h`):

```c
typedef struct RCase RCase;
struct RCase {
    int       is_default;
    tree_t   *guard_tree;
    tree_t   *body_tree;
    RCase    *next;
};

typedef struct RDecl RDecl;
struct RDecl {
    RDKind    kind;        /* RD_FUNCTION | RD_RECORD */
    int       lineno;
    char     *name;
    char    **params;      /* off-tree string array */
    int       nparams;
    char    **locals;      /* off-tree string array */
    int       nlocals;
    tree_t   *initial_tree;
    tree_t   *body_tree;
    char    **fields;      /* off-tree string array */
    int       nfields;
    RDecl    *next;
};

typedef struct {
    RDecl  *decls;
    int     ndecls;
} RProgram;
```

**Three §⛔ violations against the "all info in the tree" principle:**

1. **RDecl** carries `name`/`params[]`/`locals[]`/`fields[]`/`initial_tree`/`body_tree`/`lineno` as separate C struct fields. Those are source-token-derived facts that must live as `tree_t` children (or `v.sval` value-decoding) on a single decl node.
2. **RCase** carries `guard_tree`/`body_tree`/`is_default`/`next` — a linked-list spine and a default-arm marker, both off-tree. `case_stmt` builds these per clause then **synthesizes a `TT_IF` per clause** at the case_stmt reduction (line 388–406 of `rebus.y`) — audit violation Rb4 ("each clause wrapped in synthesized TT_IF where the source had only `guard:body`").
3. **RProgram** is the outer linked-list spine of decls. Each decl in the list lives off-tree. There is no top-level `TT_PROGRAM` produced by the parser — `rebus_parse_init` allocates a `RProgram*` and stores it in the global `rebus_parsed_program`.

**The fix:** eliminate all three. The parser outputs **one** `tree_t` (a top-level `TT_PROGRAM`) and nothing else. `rebus_parsed_program` becomes `tree_t *`. Every downstream consumer (`rebus_driver.c`, `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`) reads only `tree_t` — no `RProgram*` / `RDecl*` / `RCase*` types referenced.

### Sub-rung ladder

- [x] **PST-RB-DECL-1 — Add new TT_* kinds and confirm naming with parent goal.** ✅ 2026-05-19 (Sonnet 4.6, one4all `b4bb0a9c`)

  Added to `tree_e` in `src/include/ast.h` and name table:
  - `TT_FUNCTION` — Rebus function decl. Children L→R: `[TT_VAR(name), TT_VLIST(params), TT_VLIST(locals), TT_PROGRAM(initial) | TT_NUL, TT_PROGRAM(body)]`. `v.ival` = lineno.
  - `TT_RECORD_DECL` — Rebus record decl. Children L→R: `[TT_VAR(name), TT_VAR(field1), TT_VAR(field2), ...]`.
  Divergence note: `TT_RECORD` (Icon/Raku) and `TT_DEFINE` (Snocone) already exist; Rebus-specific kinds avoid collision. Build-only gate.

- [x] **PST-RB-DECL-2 — Eliminate `RDecl` from `rebus.y`. Phase 1 C.** ✅ 2026-05-19 (Sonnet 4.6, one4all `8af2e2e1`)

  **Files changed:** `rebus.h`, `rebus.y`, `rebus.l`, `rebus_lower.h`, `rebus_lower.c`, `rebus_print.c`, `rebus_emit.c`, `rebus_main.c` + generated `rebus.tab.c/.h`, `lex.rebus.c`.

  `rebus.h`: `RDecl`, `RDKind`, `RProgram`, `rdecl_new` deleted. `rebus_parse()` return type → `tree_t*`. `rebus_print()` sig → `tree_t*`. `RCase` kept as parser-local scratch (Option A).

  `rebus.y`: `prog` global `RProgram*` → `tree_t*`. `%union` `decl` field removed. `%type <decl>` → `%type <tree>`. `decl_list` appends `tree_t` children. `function_decl`/`record_decl` → `TT_FUNCTION`/`TT_RECORD_DECL`. `rebus_parse_init` allocates `TT_PROGRAM`.

  `rebus_lower.c`: `lower_decl(RDecl*)` → `lower_decl(tree_t*)`, switches on `d->t`. `rebus_lower` iterates `prog->c[i]`. `rebus_compile` uses `tree_t* rp`.

  **Phase 1 only.** Records `⚠ MIRROR-GAP-RB-DECL-2`.
  **Gates:** smoke_rebus 4/0, scrip_all_modes 2/0, crosscheck baseline held.

  **Where (`rebus.y` lines 152–187, 189–203, 231–239):**

  Replace the `record_decl` action (lines 152–163):
  ```c
  /* Currently — off-tree RDecl */
  RDecl *d   = rdecl_new(RD_RECORD, yylineno);
  d->name    = $2;
  SAL *sl    = $4;
  d->fields  = sl->a;
  d->nfields = sl->n;
  free(sl);
  $$ = d;
  ```
  with a `tree_t` build:
  ```c
  tree_t *rec = ast_node_new(TT_RECORD_DECL);
  expr_add_child(rec, leaf_sval(TT_VAR, $2));   /* name */
  SAL *sl = $4;
  for (int i = 0; i < sl->n; i++) expr_add_child(rec, leaf_sval(TT_VAR, sl->a[i]));
  free(sl->a); free(sl);
  $$ = rec;
  ```

  Replace the `function_decl` action (lines 165–187):
  ```c
  tree_t *fn = ast_node_new(TT_FUNCTION);
  fn->v.ival = yylineno;                                  /* or TT_ATTR(":line") */
  expr_add_child(fn, leaf_sval(TT_VAR, $2));              /* name */
  /* params */
  tree_t *params_node = ast_node_new(TT_VLIST);
  SAL *ps = (SAL*)$4;
  for (int i = 0; i < ps->n; i++) expr_add_child(params_node, leaf_sval(TT_VAR, ps->a[i]));
  free(ps->a); free(ps);
  expr_add_child(fn, params_node);
  /* locals */
  tree_t *locals_node = ast_node_new(TT_VLIST);
  SAL *ls = (SAL*)$7;
  for (int i = 0; i < ls->n; i++) expr_add_child(locals_node, leaf_sval(TT_VAR, ls->a[i]));
  free(ls->a); free(ls);
  expr_add_child(fn, locals_node);
  /* initial — TT_NUL filler if absent */
  expr_add_child(fn, $8 ? $8 : ast_node_new(TT_NUL));
  /* body */
  expr_add_child(fn, $9);
  $$ = fn;
  ```

  **Yacc declarations** (`%type` block, line 90): change `%type <decl> decl function_decl record_decl` to `%type <tree> decl function_decl record_decl`. Remove `RDecl *decl;` from the `%union`.

  **Update consumers:**
  - `rebus.h`: delete `RDecl`, `RDKind`, `rdecl_new`. Keep `SAL` (still useful as a parser-local string accumulator for params/locals/fields).
  - `rebus_driver.c`, `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`: switch from `RDecl*` traversal to `tree_t` traversal by kind. Every loop `for (RDecl *d = prog->decls; d; d = d->next)` becomes `for (int i = 0; i < prog->n; i++) { tree_t *d = prog->c[i]; switch (d->t) { case TT_FUNCTION: ...; case TT_RECORD_DECL: ...; } }`.

  Phase 1 only — record `⚠ MIRROR-GAP-RB-DECL-2` in State.

  **Gates:** `smoke_rebus` 4/0, `scrip_all_modes` 2/0, `crosscheck_snobol4` floor.

- [x] **PST-RB-DECL-3 — Eliminate `RCase` from `rebus.y`. Phase 1 C.** ✅ 2026-05-19 (Sonnet 4.6, one4all `90658061`)

  §⛔ violation (synthesized TT_IF per clause) already closed by RB-C-3 `ccc11220`.
  This rung: added free loop `{ RCase *c = $5; while (c) { RCase *nx = c->next; free(c); c = nx; } }` at end of case_stmt action. Updated comment: "parser-local scratch only — freed here, never escapes." Stale '5c will remove it' comment replaced with Option A rationale. `rebus.h` RCase doc comment updated.
  **Phase 1 only.** Records `⚠ MIRROR-GAP-RB-DECL-3`.

  **Where (`rebus.y` lines 388–433):**

  Replace the `case_stmt` action (which currently walks the `RCase` linked list and synthesizes a `TT_IF` per clause — audit Rb4) with direct `TT_CASE` construction:

  ```c
  case_stmt
      : T_CASE expr T_OF '{' caselist '}'
          {
              /* Children L→R: [discriminant, guard0, body0, guard1, body1, ..., (TT_NUL, body_default)?] */
              tree_t *cs = ast_node_new(TT_CASE);
              expr_add_child(cs, $2);
              for (RCase *c = $5; c; c = c->next) {
                  if (c->is_default)
                      expr_add_child(cs, ast_node_new(TT_NUL));
                  else
                      expr_add_child(cs, c->guard_tree);
                  expr_add_child(cs, c->body_tree);
              }
              $$ = cs;
          }
      ;
  ```

  Note this still uses `RCase` as a parser-local accumulator inside the `caselist` reduction. That is **acceptable as a working-stage scratch type** (same as `SAL` for string arrays and `TAL` for `tree_t*` arrays) **provided no `RCase*` survives in the output tree.** After the `case_stmt` reduction completes, every `RCase` node must be freed.

  Add the free loop at the end of the case_stmt action:
  ```c
  RCase *c = $5; while (c) { RCase *next = c->next; free(c); c = next; }
  ```

  **Then either:**

  **Option A — keep RCase as a local scratch.** Document explicitly in `rebus.h` and the audit that RCase is a parser-internal accumulator with no off-tree output role. SAL and TAL are accepted on the same grounds.

  **Option B — eliminate RCase entirely.** Replace the `caselist` accumulator with a `TAL` of alternating `tree_t*` items (guard, body, guard, body, ..., or NULL-marker followed by body for default), so the linked-list spine is gone. The case_stmt action then unpacks the TAL into TT_CASE children directly.

  **Recommended: Option A** for minimal scope. Option B is a follow-on cleanup.

  **The §⛔ violation closed by this rung is the synthesized TT_IF per clause** (audit Rb4) — that goes away regardless of which option. The principle "all info in the tree" is satisfied because the **output** of the case_stmt reduction is a single TT_CASE with all children in source order; whatever happened in the intermediate `caselist` accumulator is parser-local scratch.

  **Update `rebus.h`:** under Option A, add an explicit comment that RCase is parser-local scratch and **must not survive in any tree_t output**. Under Option B, delete RCase, rcase_new.

  Phase 1 only — record `⚠ MIRROR-GAP-RB-DECL-3` in State.

  **Gates:** `smoke_rebus`, `scrip_all_modes`, `crosscheck_snobol4`.

- [x] **PST-RB-DECL-4 — Eliminate `RProgram` outer wrapper. Phase 1 C.** ✅ superseded by DECL-2 `8af2e2e1`

  All DECL-4 goals accomplished as part of DECL-2: `prog` global is `tree_t*`, `rebus_parse_init` allocates `TT_PROGRAM`, `rebus_parsed_program` is `tree_t*`, all consumers use `prog->c[]` tree-walk. `RProgram` struct deleted from `rebus.h`. Records `⚠ MIRROR-GAP-RB-DECL-4`.

- [x] **PST-RB-DECL-5 — Audit cleanup.** ✅ 2026-05-19 (Sonnet 4.6)

  **Where (`rebus.y` lines 120–140, 632–635):**

  Replace `RProgram *prog` global and `rebus_parse_init` allocator with `tree_t *prog` (a `TT_PROGRAM` node). Rewrite the `program` and `decl_list` rules:

  ```c
  program
      : decl_list             { }    /* nothing — prog is built incrementally in decl_list */
      ;

  decl_list
      :                        { prog = ast_node_new(TT_PROGRAM); }
      | decl_list decl         { if ($2) expr_add_child(prog, $2); }
      | decl_list ';'          { }
      | decl_list error ';'    { yyerrok; }
      ;
  ```

  Change the global declaration at the top of `rebus.y`:
  ```c
  static tree_t *prog;
  extern tree_t *rebus_parsed_program;
  ```

  Update `rebus_parse_init`:
  ```c
  void rebus_parse_init(void) {
      prog = NULL;                 /* allocated lazily by first decl_list reduction */
      rebus_parsed_program = NULL;
  }
  ```

  And the post-parse fixup (or use `%initial-action`): assign `rebus_parsed_program = prog` after `yyparse()` returns.

  **Delete from `rebus.h`:** `RProgram` struct entirely.

  **Update consumers:** `rebus_driver.c` (`rebus_parsed_program` is now `tree_t*`); `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c` — switch from `prog->decls` linked-list walk to `prog->c[]` tree-children walk.

  Phase 1 only — record `⚠ MIRROR-GAP-RB-DECL-4` in State.

  **Gates:** `smoke_rebus`, `scrip_all_modes`, `crosscheck_snobol4`.

- [x] **PST-RB-DECL-5 — Audit cleanup.** ✅ 2026-05-19 (Sonnet 4.6)

  `PST-LR-AUDIT.md § Scan 5` re-graded: all 6 Rb violations marked ✅ with commit hashes.
  "Net Rebus status" updated to 0 retained violations, Phase 1 C COMPLETE.
  `GOAL-PARSER-PURE-SYNTAX-TREE.md` Phase 1 table: Rebus row updated to ✅.

  **No code changes — audit-update only.**

### Done criterion for PST-RB-DECL family

1. `RDecl`, `RProgram` (outer wrapper) **deleted** from `rebus.h`.
2. `RCase` either deleted (Option B) or explicitly documented as parser-local scratch with audit confirmation that no RCase pointer escapes the case_stmt reduction (Option A).
3. `rebus_parsed_program` is `tree_t *` of kind `TT_PROGRAM`.
4. Every `RDecl*` / `RProgram*` reference in `rebus_driver.c`, `rebus_lower.c`, `rebus_emit.c`, `rebus_print.c` gone.
5. **No information that was carried as an `RDecl` / `RProgram` field is still off-tree.** Every name, every param string, every local string, every field string, every initial-block, every body-block of every decl now lives somewhere as a `tree_t` child or `v.sval` value-decoded leaf.
6. Audit re-grade (DECL-5) signed off.
7. Gate floors held throughout.

---

## Open SL tickets (blocking parser_*.sc)

- **SL-3** — `SQize` infinite loop on apostrophe-free input. Loop condition + replacement interaction in `corpus/SCRIP/qize.sc:46-58` doesn't reduce `str`. Workaround: `_qtag` fast-path bypasses for the parser tag idiom. Real fix belongs in SCRIP runtime if SPITBOL handles this correctly (check first).
- **SL-4** — SCRIP runtime pattern-matcher spuriously succeeds on `BREAK("'")` / `ARB "'"` / `ARB ANY("'")` when input contains no apostrophe. Workaround: use `REPLACE` for apostrophe-presence checks. SPITBOL-oracle this first.
- **SL-5 partial 🔄 (2026-05-17)** — _Root cause identified and fixed._ "Error 5: Undefined function or operation" with `name='value'` was a `_builtin_DATA` vs `_DATA_` split-registration bug: only `sc_dat_types[]` was populated, not `_func_buckets[]`. Fix: `_builtin_DATA` now chains through `sno_DATA_register`. Downstream issue remaining: parser_rebus.sc and parser_snocone.sc now load and start executing `Src ? Compiland` but segfault in BB pattern runtime (`rt_bb_arbno` with corrupted ζ). Tracked as a separate runtime ticket — see PST-RB-5i remaining wall.

---

## Closed rungs (history; do not re-open)

- **5a–5d** ✅ 2026-05-16 (Sonnet 4.6) — `REKind`→`TT_*` mapping; `rebus.y` action bodies rewritten to `ast_node_new(TT_*)` + `expr_add_child`; `RExpr`/`RStmt`/`RProgram` structs deleted from `rebus.h`; downstream consumers (`rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`) walk `tree_t` by kind. `RE_* → TT_*` mapping table (LIT_S→QLIT, LIT_I→ILIT, LIT_F→FLIT, VAR→VAR, ASSIGN→ASSIGN, BINOP→TT_ADD etc., UNOP→TT_MNS etc., CALL→FNC, SEQ→SEQ, BLOCK→PROGRAM, IF→IF, WHILE→WHILE, DEFINE→DEFINE, RETURN→RETURN).
- **5e** ✅ 2026-05-17 (Opus 4.7) — `parser_rebus.sc` 696→266 lines, zero functions; shift/reduce + counter primitives only; `lower.sc`/`lower_driver.sc` deleted from corpus. Driver = `TDump` walk over parse-root children. SCRIP-side lowering moved entirely to C.
- **5f** ✅ 2026-05-17 (Opus 4.7) — **SL-2 closed**: heap UAF in `sc_finalize_if_else_pst` triggered by 3+ chained `else if`. Fix: per-`if_head` allocation via `sc_if_head_new`; bison `%type <expr> if_head` → `<ifhead>`. `snocone_parse.tab.c` regenerated. `_qtag` SL-3/4 workaround via identifier-shape fast-path in `semantic.sc`. Sidecar audit fixed wording in `GOAL-PST-ICN-RAKU.md`, `PLAN.md`, `corpus/SCRIP/README.md`.
- **5g** ✅ 2026-05-17 (Opus 4.7) — Two one4all bugs fixed: (1) `sm_prog.c` opnames[] mis-aligned by spurious `"SM_GEN_TICK"` — every dumped opcode from position 65+ wrong (e.g. SM_CALL_FN printed as SM_SUSPEND_VALUE). (2) `lower.c` `lower_name` ignored `TT_FNC` children — `.value($'@S')` lowered as `NAME_PUSH("value")` instead of evaluating the call. Fix: when TT_NAME child is TT_FNC, lower as plain call (nreturn deref handles the value). SPITBOL-verified. Subsystem suite 13/20 → 15/20 (stack, ShiftReduce flipped PASS). Files: `src/lower/sm_prog.c`, `src/lower/lower.c`, `src/emitter/emit_net.c`.

---

## Done criterion (parent goal)

1. PST-RB-5a–5e all ✅, 5g ✅, 5h/5i/5j/5k all `[x]`.
2. `rebus.y` builds only `tree_t` — `RExpr*`/`RStmt*`/`RProgram*` (outer) gone. ✅
3. **PST-RB-DECL-1..5 all `[x]`** — `RDecl`/`RProgram` (the lingering inner decl wrapper) eliminated; `RCase` either deleted (Option B) or documented as parser-local scratch with no off-tree output (Option A); all decl info passes inside the tree.
4. Subsystem suite 19/20 PASS (Qize SKIP under SL-3).
5. All six parser_*.sc emit `tree_t`-shape-equivalent AST dumps matching `--dump-ast` C reference.
6. Snocone `INCLUDE` statement lands; `parser_*.sc` loaded as single source.
7. Beauty self-host byte-identical (Milestone 1 protected).
8. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 5 ✅.

---

## State

```
watermark:    2026-05-19 (Sonnet 4.6) — Phase 1 C COMPLETE. All §⛔ violations closed.
              DECL-3 ✅ 90658061 (RCase freed; Option A documented).
              DECL-4 superseded by DECL-2 (RProgram already eliminated).
              DECL-5 ✅ (PST-LR-AUDIT.md Scan 5 re-graded; parent goal table updated).
status:       ✅ **Phase 1 C COMPLETE 2026-05-19 (Sonnet 4.6)**
              0 §⛔ violations. RDecl/RDKind/RProgram deleted. RCase is parser-local scratch.
              rebus_parsed_program is tree_t* of kind TT_PROGRAM.
next:         Phase 2 SCRIP mirror BLOCKED until all six C parsers Phase 1 clean.
              When unblocked: parser_rebus.sc mirror for RB-C-1..5 + DECL-2/3.
mirror gaps:  ⚠ MIRROR-GAP-RB-C-1..5, ⚠ MIRROR-GAP-RB-DECL-2, ⚠ MIRROR-GAP-RB-DECL-3.
heads:        .github @ (pending push) · one4all @ 90658061 · corpus (no changes)

**PST-SC-SCRIP-AUDIT 2026-05-19 (Sonnet 4.6):** parser_rebus.sc scanned against
strict permitted list (shift, reduce, nPush, nInc, nPop, nTop, assign only).
✅ CLEAN — zero violations. No forbidden calls (shift_val, foldop, reduce_call,
reduce_prim, reduce_opsyn, Push, Pop, Append, Tree, tree). No function definitions.
All nPush/nPop are counter discipline in grammar rules. Pop() in driver is result
extraction. parser_rebus.sc is already at the Phase 2 endpoint.
Session PST-RB-SC action: verify gates pass, stamp as complete. Smallest Phase 2 job.
```

### Session-end note — 2026-05-19 (Opus 4.7 session 4)

HQ session — PST-LR-AUDIT-1 closed and three-facet block added across all six
PST goal files. No Rebus-specific code changes this session. Next session:
open `rebus.y:317–328`, apply RB-C-2 fix sketch above (add TT_UNLESS kind +
lower arm), regenerate `.tab.c`, run gates (smoke_rebus 4/0, smoke_scrip 2/0,
crosscheck_snobol4 4/2). Rebus's heavy F1 lift is the PST-RB-DECL ladder
(eliminate off-tree RDecl/RCase) — but RB-C-2..5 are smaller wins to
sequence first.

## Authorship

Drafted Sonnet 4.6, 2026-05-16. Subsequent rungs by Opus 4.7 and Sonnet 4.6 across the 2026-05-17/18 session cluster. PST-RB-DECL ladder added by Claude Opus 4.7, 2026-05-19, per Lon directive "all info in the tree, no side hustles". State block compacted 2026-05-19 — full per-rung history preserved in git log per RULES.md.
