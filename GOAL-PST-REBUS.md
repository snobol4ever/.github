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

## Active rungs

- [x] **PST-RB-5h — Snocone-port subsystem suite to 19/20.** ✅ 2026-05-17 (Opus 4.7)
  15/20 → **19/20** PASS (Qize stays SKIPped under SL-3 as designed). The narrative "5 separate failures" (match, Gen, semantic, trace, Qize) collapsed: **one root cause flipped 4 of them.**
  Root cause: `lower_scan` in `src/lower/lower.c` unconditionally emitted Icon scanning-environment opcodes (`ICN_SCAN_PUSH`/`ICN_SCAN_POP`) for `TT_SCAN`. Both Icon and Snocone parsers reduce `?` to `TT_SCAN` — but Snocone `s ? pat` is **SNOBOL4 pattern matching** per SPITBOL Ch. 18 (binary op priority 1, left-assoc), not Icon scan-env. Wrong dialect meant `if (s ? p)` never set `last_ok`, so the subsequent `SM_JUMP_F` always fell through.
  Fix: dispatch on `g_lang` in `lower_scan`. Icon keeps `ICN_SCAN_PUSH/POP`; non-Icon mirrors the statement-level match path at `lower_stmt` line ~1306 (`SM_EXEC_STMT` with pattern DCG), then pushes an empty placeholder so `lower_if_stmt`'s `SM_VOID_POP` has something to consume. Flipped: match (3 tests), trace (1 test), Gen (used `?` internally, hit same wrong-branch path), semantic (same). Subsystems passing: 16 → 19.
  Sweep also landed: `snocone_parse.y` AST_* → TT_* (29 names, 89 occurrences; bridge `#define`s deleted from regenerated `.tab.c`); `snocone_lex.c` AST_* goto-labels → LX_* (45 names, 101 occurrences — they were lexer-state labels, never AST kinds).
  Watermark: one4all `1e6557c1`. Gates green (smoke_rebus 4/0, smoke_scrip 2/0, smoke_icon 5/0, smoke_snocone 5/0, smoke_snobol4 6/1 baseline with pre-existing `pattern` test fail unrelated to this rung, crosscheck_snobol4 4/2 baseline, unified_broker 19/30 baseline).

- [ ] **⛔ PST-RB-5i-PRE — CASE-SENSITIVE-ONLY sweep (BLOCKS 5i finish). NEXT SESSION STARTS HERE.**
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
2. `rebus.y` builds only `tree_t` — `RExpr*`/`RStmt*`/`RProgram*` gone. ✅
3. Subsystem suite 19/20 PASS (Qize SKIP under SL-3).
4. All six parser_*.sc emit `tree_t`-shape-equivalent AST dumps matching `--dump-ast` C reference.
5. Snocone `INCLUDE` statement lands; `parser_*.sc` loaded as single source.
6. Beauty self-host byte-identical (Milestone 1 protected).
7. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 5 ✅.

---

## State

```
watermark:  PST-RB-5i partial committed 2026-05-17 (one4all PENDING, .github PENDING)
status:     Subsystem suite 19/20 at HEAD (Qize SKIP under SL-3 — acceptance met).
            SL-5 root cause fixed: _builtin_DATA/_DATA_ split-registration.
            Parser_*.sc now load past Error 5 and begin executing Src ? Compiland,
            but segfault in BB pattern runtime (rt_bb_arbno with corrupted ζ).
            C-side `--dump-ast` now works for all six frontends (was lang_snocone only).
            BB pattern buffer caps raised: FLAT_BUF_MAX 16K→256K, BB_POOL_SIZE 4MB→64MB.
next:       **PST-RB-5i-PRE (CASE-SENSITIVE-ONLY sweep, CSO-1..CSO-8 inline above). MUST RUN BEFORE PST-RB-5i finish.**
            After CSO-8: PST-RB-5i finish (debug rt_bb_arbno ζ corruption) → 5j (6-fn trace) → 5k.

SL-2 closed. SL-5 partial (downstream BB runtime crash). SL-3/4 open.

Authors:
  5a–5d            Sonnet 4.6  2026-05-16
  5e–5g            Opus 4.7    2026-05-17 (three sessions)
  5h               Opus 4.7    2026-05-17
  5i partial       Opus 4.7    2026-05-17 (this session)
```
