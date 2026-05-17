# GOAL-PARSER-SC-TRANSPILE.md — Six parser_*.sc producing AST trees via Snocone→SNOBOL4 transpile + 2-way sync-monitor harness

**Repo:** one4all + corpus + .github
**Parent:** Independent goal complementing `GOAL-PARSER-PURE-SYNTAX-TREE.md` and `GOAL-PST-REBUS.md`
**Author:** Lon Jones Cherryholmes · Claude Opus 4.7
**Date opened:** 2026-05-17

---

## ⛔ Session Start Protocol (every session, no exceptions)

Before touching any code in this goal, the session must:

1. **Clone the standard three repos** (`.github`, `corpus`, `one4all`) per the global `PLAN.md` protocol. Optional: clone `harness` if you need the SPITBOL build recipe, and clone `x64` if you need to build SPITBOL itself. See "How-to: clone and bring up a fresh session" below for one-shot commands.
2. **Extract the SPITBOL manual** to plain text and consult the verified map: `pdftotext /mnt/user-data/uploads/spitbol-manual-v3_7.pdf /tmp/spitbol.txt`. Then read using the **§"SPITBOL Manual Reading Index & Map"** in this file (below) — line numbers there are verified against the actual PDF, not the stale numbers that lived in older goal files. Required minimum:
   - Ch 14 — Statement form (line 9017+)
   - Ch 15 — Operator priority table (line 9540+)
   - Ch 18 — Patterns and pattern-match algorithm (line 10606+)
   - Ch 8 — Program-defined functions and the **Gimpel template** (line 5806+; template at 5973)
   - Appendix C — Differences from SNOBOL4 (line 13651+)
3. **Read `corpus/SCRIP/parser_snocone.sc` in full** — canonical reference for Snocone's exact syntax as accepted by SCRIP today. The grammar declared there is the language we are transpiling FROM.
4. **Read `corpus/SCRIP/README.md`** for the runtime-file load order and the role of each `.sc` file in the shared infrastructure.
5. **Read `.github/ARCH-SNOCONE.md`** for the implementer-level Snocone semantics view, especially §"Lowering map" (line ~319) which is the master template for control-flow lowering.

Without these reads completed, the session is not qualified to make grammar or semantics decisions. Don't skip.

If continuing prior work (SCT-1b and beyond), also read **§"How-to" sections** at the bottom of this file — they distill what previous sessions learned about SCRIP's SNOBOL4-parser quirks, file layout, and the build environment.

---

## 📖 SPITBOL Manual Reading Index & Map

**Source:** `spitbol-manual-v3_7.pdf` (Mark B. Emmer & Edward K. Quillen, Catspaw 2000) — 368 pages, 19,700 lines when extracted via `pdftotext` to `/tmp/spitbol.txt`. Line numbers below are **body** anchors in that extracted text (not PDF page numbers; PDF page numbers are in the TOC at the top of the file). The map below was verified against the actual PDF on 2026-05-17 (Opus 4.7).

This index supersedes the placeholder "cheatsheet from GOAL-PST-REBUS" reference in SCT-0a step 2. There is no separate cheatsheet — the map below IS the cheatsheet.

### How to use this index

`pdftotext /mnt/user-data/uploads/spitbol-manual-v3_7.pdf /tmp/spitbol.txt` (run once per session). Then `view /tmp/spitbol.txt` with the ranges below. The Reference Manual chapters (12–20) are the authoritative ones; the Tutorial chapters (3–11) help build intuition but are looser.

### Chapter anchors (body lines in /tmp/spitbol.txt)

| Ch | Line | Title | Why it matters for the transpiler |
|----|------|-------|-----------------------------------|
| 2  |  809 | First Program | Skip — intro |
| 3  |  995 | Fundamentals (datatypes, operators, variables) | Tutorial-level intro; covered formally in Ch 15/17 |
| 4  | 1680 | Control Flow and Functions | Tutorial-level — Ch 8 is the formal source |
| 5  | 2313 | Input/Output and Keywords | Out of scope for parsers (they read INPUT, write OUTPUT — trivial) |
| 6  | 3113 | Pattern Matching (tutorial) | Builds intuition for Ch 18 |
| 7  | 4550 | Additional Operators & Datatypes (indirect, unevaluated, immediate assign, arrays, tables) | **Important** — `$`, `*`, `$=`, `.=`, alternative-evaluation `(e1, e2, …)` semantics |
| 8  | 5663 | **Program-Defined Objects** | **CRITICAL** — Gimpel template for `DEFINE('fn(args)locals') :(fn_end) / fn body / :(RETURN) / fn_end`. This is exactly what Snocone `function fn(args) { … }` must lower to. |
| 9  | 6722 | **Advanced Topics** | **CRITICAL** — `ARBNO`, recursive patterns via `*VAR`, quickscan/fullscan, `EVAL`/`CODE` rules, `?` interrogation, `~` negation, alt-eval traps |
| 10 | 7677 | Debugging | Out of scope |
| 11 | 8340 | Concluding Remarks | Skip |
| 12 | 8407 | Reference Introduction | Brief |
| 13 | 8512 | Running SPITBOL | Out of scope for emitted code (only matters for harness invocation) |
| 14 | 9017 | **SPITBOL Statements** | **CRITICAL** — `LABEL SUBJECT ? PATTERN = REPLACEMENT :GOTO` form, label rules, continuation `+`/`.` at column 1, `;` for multi-stmt-per-line, `END` statement. Conditional goto syntax `:S(L)`, `:F(L)`, `:(L)`, `:S(L)F(M)`. |
| 15 | 9540 | **Operators** | **CRITICAL** — Full unary + binary operator priority/associativity table. Reproduced below. |
| 16 | 9761 | **Keywords** | **CRITICAL** — `&ANCHOR`, `&FULLSCAN`, `&CASE`, `&MAXLNGTH`, `&LCASE`/`&UCASE`/`&ALPHABET`, &ABORT/&ARB/&BAL/&FAIL/&FENCE/&REM/&SUCCEED as pattern primitives. |
| 17 | 10135 | **Data Types and Conversion** | **CRITICAL** — Conversion matrix. String↔integer↔real↔pattern↔name↔code↔expression auto-conversion rules. |
| 18 | 10606 | **Patterns and Pattern Matching** | **CRITICAL** — Primitive patterns `ABORT`/`ARB`/`BAL`/`FAIL`/`FENCE`/`REM`/`SUCCEED` and the pattern-match algorithm (stack-backtracking, `&ANCHOR` checked at match start only). |
| 19 | 10958 | **SPITBOL Functions** | **CRITICAL** — Alphabetical reference for every built-in. Pattern-builder functions: `ANY`, `ARBNO`, `BREAK`, `BREAKX`, `LEN`, `NOTANY`, `POS`, `RPOS`, `RTAB`, `SPAN`, `TAB`. Predicates: `EQ`/`NE`/`LT`/`LE`/`GT`/`GE` (numeric), `LEQ`/`LNE`/`LLT`/`LLE`/`LGT`/`LGE` (lexical), `IDENT`/`DIFFER` (identity). Construction: `DEFINE`, `DATA`, `OPSYN`, `CONVERT`. |
| 20 | 12978 | Programming Notes (space, speed) | Useful for future optimization, not for SCT-1 |

### Appendix anchors

| App | Line | Title | Why it matters |
|-----|------|-------|----------------|
| A | 13163 | Distribution Media | Skip |
| B | 13504 | Programs from String and List Processing | Useful idioms (`bnf.spt`, `bintree.inc`, `concord.spt`) but not required |
| C | 13651 | **Summary of Differences (vs SNOBOL4 / SNOBOL4+)** | **CRITICAL** — Portability boundary. Features absent in SPITBOL: redefining standard functions, `VALUE` function, `&STFCOUNT`. Features different: `&ANCHOR` checked at match start only, ABORT/ARB/FAIL/REM/SUCCEED are write-protected pattern variables, recovery via `SETEXIT()`, FORTRAN I/O absent, `TABLE()` hashing model. |
| D | 13968 | Error Messages | Useful when diagnosing failed transpiled programs |
| E | 14720 | The HOST Function | Out of scope |
| F | 15884 | External Functions | Out of scope |
| G | 17877 | Configuring SPITBOL | Out of scope |

### Binary operator priority (verbatim from Ch 15, line 9830+)

| Op | Assoc | Pri | Definition |
|----|-------|-----|------------|
| `=`           | right | 0  | Assignment |
| `?`           | left  | 1  | Pattern match (**explicit form**) |
| `\|`          | right | 3  | Pattern alternation |
| *space*       | right | 4  | **Concatenation or match** (the implicit pattern-match form in standard SNOBOL4) |
| `+`           | left  | 6  | Addition |
| `-`           | left  | 6  | Subtraction |
| `/`           | left  | 8  | Division |
| `*`           | left  | 9  | Multiplication |
| `^` `!` `**`  | right | 11 | Exponentiation |
| `$`           | left  | 12 | Immediate assignment (pattern context) |
| `.`           | left  | 12 | Conditional assignment (pattern context) |

**Available for OPSYN:** `&` (pri 2 left), `@` (pri 5 right), `#` (pri 7 left), `%` (pri 10 left), `~` (pri 13 right).

### Unary operators (Ch 15, line 9740+)

All equal priority, higher than any binary, right-to-left:

| Op | Name | Definition |
|----|------|------------|
| `@` | at sign       | Assigns cursor position to its operand |
| `~` | tilde         | Negates failure/success |
| `?` | question mark | Interrogation — returns null if operand succeeds |
| `&` | ampersand     | Keyword reference |
| `+` | plus          | Positive numeric |
| `-` | minus         | Negate numeric |
| `*` | asterisk      | Defer evaluation |
| `$` | dollar sign   | Indirection |
| `.` | period        | Returns a name |

**Available for OPSYN:** `!` `%` `/` `#` `=` `|`.

### Statement form (Ch 14, line 9461+)

```
LABEL  SUBJECT  ?  PATTERN  =  REPLACEMENT  :GOTO
```

Elements separated by blank or tab. **Label** at column 1 (letter or digit start, blank/tab/semicolon terminates). **Continuation** marks `+` or `.` at column 1 glue line to previous. **Semicolons** allow multi-statement-per-line. **Comments** = `*` at column 1. **`?` between subject and pattern is the explicit form**; in standard SNOBOL4 the implicit form (space-as-match at priority 4) is used. **For portable transpiler output, prefer space-as-match** since SPITBOL accepts both but standard SNOBOL4 only accepts the implicit form.

### Goto syntax (Ch 14, line 9576+)

- `:(LABEL)` — unconditional
- `:S(LABEL)` — on success
- `:F(LABEL)` — on failure
- `:S(L1)F(L2)` — combined
- `:<VAR>` — direct goto to `CODE()` block
- `:($expr)` — computed label (expr evaluates to a string, indirect dispatch)

### Function definition form (Ch 8, line 5806+; "Gimpel template" line 5973)

The canonical Gimpel template — this is the form Snocone `function fn(args) { body }` MUST lower to:

```
*       FN(arg1, arg2) — description
*
        DEFINE('FN(arg1,arg2)local1,local2')        :(FN_END)
FN      ; body statements
        ; ...
        FN = result_expression                       :(RETURN)
FN_END
```

Returns: `:(RETURN)` = success, `:(FRETURN)` = failure, `:(NRETURN)` = name return (rare; LHS-of-assignment return). The variable named `FN` (same as function) carries the return value.

### Pattern primitives — quick map

| SPITBOL | Snocone uses it as | Semantics |
|---------|--------------------|-----------|
| `ANY(s)` | `ANY('abc')` | match one char from set s |
| `NOTANY(s)` | | match one char NOT in set s |
| `SPAN(s)` | `SPAN(digits)` | match longest run of chars from set s (≥1 char) |
| `BREAK(s)` | `BREAK(nl)` | match up to (not including) any char in s |
| `BREAKX(s)` | | like BREAK but extends past s-chars on rematch |
| `LEN(i)` | `LEN(N)` | match exactly i characters |
| `TAB(i)` | | match up to cursor position i |
| `RTAB(i)` | | match up to i chars from end |
| `POS(i)` | `POS(0)` | match-zero-chars if cursor at i (anchor) |
| `RPOS(i)` | `RPOS(0)` | match-zero-chars if cursor i chars from end |
| `ARBNO(p)` | `ARBNO(*Command)` | zero or more occurrences of pattern p |
| `ARB` | (use `&ARB`) | zero or more chars, shortest first |
| `REM` | (use `&REM`) | remainder of subject |
| `BAL` | (use `&BAL`) | balanced parens substring |
| `FENCE` | `FENCE(…)` | succeeds going forward, fails on backtrack — prevents retry |
| `ABORT` | | immediately fail entire match |
| `FAIL` | | fail this branch (forces backtrack) |
| `SUCCEED` | | succeed matching null, no backtrack info |

### Pattern-capture binary operators (Ch 15 + Ch 6)

- `pat . var` — **conditional assignment** (capture). Assigns matched substring to `var` only if the entire enclosing match succeeds.
- `pat $ var` — **immediate assignment**. Assigns matched substring to `var` as soon as `pat` matches, even if the enclosing match later fails.

### The `*` deferred-evaluation operator (Ch 7 + Ch 9)

`*EXPR` (unary, priority above any binary) freezes EXPR as an unevaluated expression. When the pattern is **used** (not built), the deferred expression is re-evaluated. Two heavy uses in parser_*.sc:

1. **Forward references:** `ITEM = SPAN(digits) | *LIST` allows ITEM to reference LIST before LIST is defined.
2. **Per-match parameter capture:** `SHIFT_PAT = LEN(*N) . FRONT REM . REST` lets `LEN` see the **current** value of `N` at match time, not the value at pattern-build time.

The constraint in this goal says `*Var` where `Var` is itself a function is forbidden. `*Var` where `Var` is a simple variable or `*Var` where `Var` is a non-call pattern composition is the supported form.

### `&FULLSCAN` — the practical truth

Appendix C line 13932 says `&FULLSCAN` is "not implemented" — but Ch 9 line 6985 clarifies: the keyword is **retained, write-only, must be non-zero**. SPITBOL is always in fullscan mode; `&FULLSCAN = 1` is accepted (no-op), `&FULLSCAN = 0` produces an error. **For the transpiler:** emit `&FULLSCAN = 1` at top of file — Snocone parser_*.sc files all do this (line 1 of parser_snocone.sc), and the same line is portable to SPITBOL.

### Critical SPITBOL-vs-standard-SNOBOL4 differences (App C)

For the transpiler's "portable SNOBOL4" target:

1. `&ANCHOR` is read at match **start** in SPITBOL (changing it mid-match has no effect). Standard SNOBOL4 re-checks.
2. `ABORT`, `ARB`, `FAIL`, `REM`, `SUCCEED` are **write-protected pattern variables** in SPITBOL — assignment to them fails. Don't emit code that assigns to them.
3. **Same stack** is used for pattern matching and function calls — infinite pattern recursion presents as stack overflow.
4. `TABLE()` is hashed in SPITBOL — argument sets the hash header count, not a hard size.
5. No FORTRAN I/O, no `VALUE` function.
6. Recovery via `SETEXIT()` is available.

---

## 🎯 Goal (one sentence)

Get all six `parser_*.sc` programs producing AST trees that match the C-side `--dump-ast` reference output, by **transpiling each parser_*.sc to a portable .sno program**, then comparing the .sno output under SCRIP vs. SPITBOL via the existing two-way IPC sync-step monitor.

---

## 💡 Architectural Insight (Eureka)

The current PST-REBUS approach treats parser_*.sc as **first-class input** to SCRIP and pushes through every SCRIP runtime bug encountered (`rt_bb_arbno` ζ corruption, BB pattern emission stack issues, deferred-var rebuild paths). That gauntlet is long and each bug is expensive to find because we have no oracle for what Snocone "should" do.

The original Snocone (Mark Emmer's, the source of `sb.sno` etc.) was **a Snocone-to-SNOBOL4 transpiler**: Snocone source → SNOBOL4 source → SPITBOL. We are reinventing that.

**Once we have a transpiler:**

- **A Snocone oracle exists for the first time.** Currently SCRIP is the only thing that can run Snocone — there is nothing to compare against. Post-transpiler, the same `.sc` file produces SNOBOL4 that SPITBOL runs, and SPITBOL becomes a Snocone oracle by transitivity.
- **The 2-way sync-step monitor (already built) becomes a Snocone debugger.** `parser_<lang>.sc → parser_<lang>.sno → SPITBOL + SCRIP --sm-run/--jit-run side by side`, divergence reported at the first differing CALL/RETURN/VALUE event. Each bug in SCRIP's Snocone runtime shows up as a clean divergence with a 5-line repro.
- **The transpiler itself stress-tests `lower.c`.** Each construct in parser_*.sc forces a Snocone→AST→SNOBOL4 path that today only roundtrips Snocone→AST→IR. Bugs found in lower.c during transpiler development feed back into the main GOAL-PST-REBUS work.
- **We trust the LOWER step.** Per Lon: "we must just trust our LOWER step, and find bugs in lower while we are at it going along." LOWER produces the `tree_t` we transpile from. If LOWER is correct, the transpiler emits semantically-faithful SNOBOL4. If the transpiled SNOBOL4 diverges from SCRIP's direct execution of the .sc, the bug is in **one of**: LOWER, SM/BB runtime, transpiler. Sync-monitor tells us which.

This is the right shape of the problem.

---

## ⛔ Implementation Constraints (binding)

Per Lon directive 2026-05-17:

1. **`parser_<lang>.sc` files may use ONLY six functions from the shared `corpus/SCRIP/` runtime:** `shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop`. (Defined in `semantic.sc` and `counter.sc`.)
2. **No language-specific helpers.** Today `icon_helpers.sc` (4 leaf-push helpers + `notmatch`) and `raku_helpers.sc` (`push_interp_str`, `dq_unescape`, 9 `finish_*` variable-arity assemblers) exist. These must be **eliminated** — their logic either folds into grammar rules expressed in terms of the six allowed primitives, or migrates into the C-side `lower.c` / `rebus_lower.c` / `icon_lower.c` paths.
3. **`pop`, `foldop`, `nDec`, `reduce_opsyn`, `reduce_prim`, `reduce_call`, `nPushName`** — currently exported by `semantic.sc` — must NOT be called from any `parser_*.sc`. Their use in current grammars must be replaced with combinations of the six allowed.
4. **No `*Var` deferred references**, where Var is itself a Snocone function. Pattern composition is allowed (`*Letter *Letter`), but `*foo()` constructs that defer call-time evaluation must be re-expressed using the shift/reduce stack and counter primitives. Rationale: per GOAL-PST-REBUS.md remaining wall, `*Var` deferred references trigger `bb_deferred_var` rebuild paths and the JIT-stack pointer bug — eliminating them removes that bug from the parser-side surface entirely.
5. **The transpiler's output is portable SNOBOL4.** No SPITBOL-only extensions. The transpiled `.sno` must run on:
   - SCRIP `--ir-run`, `--sm-run`, `--jit-run` (all three modes)
   - SPITBOL x64 (`/home/claude/x64/bin/sbl -bf`)
   - CSNOBOL4 (only if Silly target, otherwise not required)

---

## 🔧 Architecture

```
parser_<lang>.sc                                  (Snocone source — shared shape)
       │
       │  SCRIP frontend (existing)
       ▼
   tree_t AST                                     (pure-syntax tree — LOWER trusts this)
       │
       │  NEW LOWER stage: src/lower/lower_sno.c
       │  Driven by:        scrip --dump-sno
       ▼
parser_<lang>_transpiled.sno                      (portable SNOBOL4 source)
       │
       │  [SCRIP modes 1/2/3]            [SPITBOL]
       ▼                                            ▼
    SCRIP exec                                   SPITBOL exec
       │                                            │
       │  IPC binary trace                          │  IPC binary trace
       ▼                                            ▼
       └────────► 2-way sync-step monitor ◄─────────┘
                  (existing: scripts/test_monitor_2way_spitbol_vs_sm.sh
                   plus thin wrapper: scripts/run_parser_sync_monitor.sh)
                  reports FIRST divergence, last-agree line + first-disagree line
```

**Per Lon directive 2026-05-17 (architectural answer):** the transpiler is a new **LOWER stage** in the standard SCRIP pipeline, NOT a separate `src/transpile/` tool.  It lives at `src/lower/lower_sno.c` as a peer to `src/lower/lower.c` (SM), `lower_icn.c` (Icon-specific), and `lower_pl.c` (Prolog-specific).  Public entry: `int tree_to_sno(const tree_t *ast, FILE *out)`.  Driven by the new `--dump-sno` CLI flag in `src/driver/scrip.c`.

For the SCRIP side, the input is **transpiled to SNOBOL4** rather than executed as Snocone. This:
- Removes SCRIP's Snocone runtime from the equation on the SPITBOL-comparison path.
- Validates LOWER end-to-end (LOWER → tree_t → transpile → SNOBOL4 must match SPITBOL).
- Allows running the parser through SPITBOL today (no Snocone runtime in SPITBOL world).

A separate path runs the original `.sc` through SCRIP directly (`--ir-run corpus/SCRIP/...` chain), and compares its output to the transpiled `.sno`-via-SPITBOL output. That's the **outer** Snocone-runtime oracle. The sync-monitor handles the **inner** divergence-when-running-the-same-.sno cross-mode test.

---

## 🪜 Rungs (execute in order; one construct per commit unless documented as composite)

### Phase 0 — Reading & Snocone fluency

- [x] **SCT-0a** ✅ 2026-05-17 (Opus 4.7) — Session-start reading complete: SPITBOL manual via /tmp/spitbol.txt (Ch 8/9/14/15/17/18/19, App C), `parser_snocone.sc` (931 lines), `corpus/SCRIP/README.md`, `.github/ARCH-SNOCONE.md`. Output: §"SPITBOL Manual Reading Index & Map" added to this file (verified line numbers, supersedes the missing GOAL-PST-REBUS cheatsheet). No source touched. one4all and corpus untouched.
- [ ] **SCT-0b** — Hand-write a 5-line `.sc` "echo" program that exercises: literal pattern, ANY/SPAN/BREAK, `shift(lit, 'TT_QLIT')`, `reduce('TOP', 1)`, `nPush/nInc/nTop/nPop`. Confirm runs cleanly under existing SCRIP shared-runtime chain. This is the lowest-common-denominator surface for SCT-1 to target. Commit: the test file under `corpus/SCRIP/tests/sct_echo.sc` + matching `.ref` SPITBOL would produce if hand-translated.

### Phase 1 — Transpiler MVP

- [🔄] **SCT-1 — Bootstrap: `parser_snobol4.sc` → `parser_snobol4.sno`.** PARTIAL ✅ 2026-05-17 (Opus 4.7).
  Implemented `src/lower/lower_sno.{c,h}` (not `src/transpile/sc_to_sno.c` — placement updated per Lon directive: lives as peer to `lower_icn.c`/`lower_pl.c`). Reads `tree_t*` produced by any frontend, walks it, emits SNOBOL4 on stdout. Wired as `--dump-sno` (mirrors `--dump-ast`/`--dump-sm`/`--dump-bb` family). Handles ~30 TT_* tags including atoms, all unary operators, binary arithmetic, pattern composition (TT_SEQ/CAT/ALT/VLIST), pattern captures (`.`/`$`), function calls, indexing, named pattern primitives (ARB/REM/BAL/FAIL/SUCCEED/ABORT/FENCE/ARBNO), embedded assign/scan, and the Gimpel function template (TT_DEFINE → `DEFINE(proto) :(fn_end)` / label / body / `:(RETURN)` / end-label). Status: `parser_snobol4.sc` transpiles to 126 lines of SNOBOL4 that **parse cleanly** under `scrip --sm-run` and **begin executing** before hitting runtime Error 5 at statement 63. Remaining: TT_IF/TT_WHILE/TT_RETURN-in-stmt-pos as `'?TT_NN?'` string placeholders. See SCT-1b.

- [ ] **SCT-1b — Statement-position control flow (TT_IF, TT_WHILE, TT_RETURN-as-stmt).**
  In `lower_sno.c::emit_stmt`, add a branch (mirroring the TT_DEFINE-as-subject branch) for when `:subj` carries TT_IF / TT_WHILE / TT_RETURN. Lowering per `ARCH-SNOCONE.md` §"Lowering map":
  - `TT_IF(cond, then[, else])` → `cond :F(else) / then... :(after) / else else_body... / after`
  - `TT_WHILE(cond, body)` → `top cond :F(after) / body... :(top) / after`
  - `TT_RETURN(expr)` → `fname = expr :(RETURN)` where fname is the enclosing function's name (need stack/context for nested functions; simplest = pass through `pending_fname` in `sno_ctx_t` parallel to `pending_label`).
  Label generation: monotonic counter in `sno_ctx_t` (Snocone's own labels are already uniquified per `g_sc_label_seq`; only synthetic labels for goto-emission need generation here). Acceptance: `parser_snobol4.sc` transpile produces 0 `?TT_NN?` placeholders.

- [ ] **SCT-1c — Round-trip parser_snobol4.sno through SCRIP + SPITBOL.**
  Requires SPITBOL built (see Notes §"How-to: build SPITBOL x64"). Drive via `scripts/run_parser_sync_monitor.sh snobol4 corpus/programs/snobol4/parser/atom_id.sno`. Acceptance: both runtimes produce same AST dump and same trace events on the sample input, OR first divergence is reported with last-agree + first-disagree line numbers.

- [ ] **SCT-1 (full) — Acceptance retest.** `scrip --dump-sno corpus/SCRIP/parser_snobol4.sc | sbl -b -` produces output bytewise-identical to `scrip --ir-run corpus/SCRIP/global.sc ... parser_snobol4.sc < sample.sno`. Test sample: `corpus/programs/snobol4/parser/atom_id.sno`.

- [ ] **SCT-2 — `parser_rebus.sc` → `parser_rebus.sno`.**
  Same as SCT-1 but for Rebus parser. New constructs to handle in transpiler: `OPSYN`, `&FULLSCAN` setter (pass through verbatim), `epsilon` (already known), counter idioms (`nPush/nInc/nTop/nPop` → SNOBOL4 stack manipulation already in `counter.inc`). Sample: `corpus/programs/rebus/parser/paren.reb`.

- [ ] **SCT-3 — `parser_snocone.sc` → `parser_snocone.sno`.**
  The hardest one: parser_snocone.sc is 931 lines and uses constructs the others don't (record declarations, function returns). May expose `lower.c` gaps that surface as `[NO-AST]` stubs in transpile mode — fix those in `lower.c`, never in the transpiler. Sample: `corpus/programs/snocone/corpus/sc1_literals.sc`.

- [ ] **SCT-4 — `parser_icon.sc` → `parser_icon.sno`.**
  Sub-rung blocker: `icon_helpers.sc` must be deleted FIRST. Its 4 leaf-push helpers + `notmatch` get inlined into the grammar (`push_qlit` and friends become `shift(*X, 'TT_QLIT')` directly; `notmatch` was `~match` — express via OPSYN'd `~`). Sample: `corpus/programs/icon/parser/fail_stmt.icn`.

- [ ] **SCT-5 — `parser_raku.sc` → `parser_raku.sno`.**
  Sub-rung blocker: `raku_helpers.sc` must be deleted FIRST. The 9 `finish_*` variable-arity assemblers fold into `reduce` with `nTop()` argument. `push_interp_str` / `dq_unescape` migrate to C-side `raku_lower.c`. Sample: `corpus/programs/raku/parser/str_chars.raku`.

- [ ] **SCT-6 — `parser_prolog.sc` → `parser_prolog.sno`.**
  Independent of GOAL-PST-PROLOG's frontend work. The Prolog parser_*.sc is largest at 1040 lines; some constructs may need `lower.c` fixes. Sample: `corpus/programs/prolog/rung01_hello_hello.pl`.

### Phase 2 — Two-way harness

- [ ] **SCT-7 — Build the harness driver `scripts/run_parser_sync_monitor.sh`.**
  Wraps the existing IPC infrastructure (`monitor_sync_bin.py`, `monitor_ipc_bin_csn.c`, `x64/monitor_ipc_bin_spl.c`). Inputs: `<lang> <sample-file>`. Runs:
  1. `scrip --sc-to-sno parser_<lang>.sc > /tmp/parser_<lang>.sno`
  2. SCRIP side: `scrip --sm-run /tmp/parser_<lang>.sno < <sample>` with `MONITOR_READY_PIPE` set
  3. SPITBOL side: `sbl -bf /tmp/parser_<lang>.sno < <sample>` with `MONITOR_READY_PIPE` set (requires SPITBOL IPC patch — separate sub-rung if not yet landed)
  4. `monitor_sync_bin.py` orchestrates step-comparison
  
  Outputs: PASS if both produce same AST dump and same trace events; FAIL with last-agree + first-disagree line numbers if not.

- [ ] **SCT-8 — Triage and fix first divergence found by SCT-7 for each parser.**
  Each parser's first divergence in the 2-way harness becomes one ticket. Per Lon: "find bugs in lower while we are at it going along." Expect bugs in: (a) transpiler emission for some construct, (b) `lower.c` for some construct, (c) SCRIP's SM/BB runtime for some pattern construct. Fix per-bug.

### Phase 3 — Closure

- [ ] **SCT-9 — All six parser_*.sc produce AST trees matching C `--dump-ast` reference.**
  Validation script: `scripts/test_parser_sc_transpile.sh`. For each `(lang, sample)`:
  1. Run transpiled `.sno` via SCRIP (3 modes) — collect AST output
  2. Run transpiled `.sno` via SPITBOL — collect AST output
  3. Run C `scrip --dump-ast` on the sample — collect reference AST
  4. All three must match (modulo whitespace).
  Acceptance: 6 langs × 4 sources × matching = 24/24 PASS.

- [ ] **SCT-10 — Delete sidecar helpers permanently.**
  `corpus/SCRIP/icon_helpers.sc` and `corpus/SCRIP/raku_helpers.sc` removed from corpus. `run_scrip_parser.sh` no longer loads them. README updated. Gate: SCT-9 still passes.

- [ ] **SCT-11 — Document the Snocone subset.**
  `corpus/SCRIP/SNOCONE-SUBSET.md` — the formal grammar of "the Snocone the parser_*.sc files use", enumerated from observed constructs across all six grammars after they're stable. This becomes the spec the transpiler targets and the surface area the SCRIP runtime must support.

---

## 📊 State

```
status:    SCT-1 PARTIAL ✅ (2026-05-17, Opus 4.7).
           CLI flag + lower_sno.c skeleton + harness wrapper landed.
           parser_snobol4.sc transpiles to 126 lines of SNOBOL4 that
           parse and begin executing under `scrip --sm-run`.
           First runtime divergence at stmt 63 (Error 5: undefined
           function/operation) — this is the entry point for SCT-1b
           and the sync-step monitor.

watermark: scrip --dump-sno parser_snobol4.sc → 126 lines, 4 TT_*
           placeholders (TT_IF, TT_WHILE, TT_RETURN-in-expr-pos),
           parses cleanly, begins exec, fails at stmt 63 with Error 5.

landed (SCT-1 in-progress):
  - src/lower/lower_sno.h, src/lower/lower_sno.c     (~360 lines)
  - src/driver/scrip.c                               (--dump-sno flag,
                                                      4 insertion points)
  - Makefile                                          (lower_sno.c entry +
                                                      compile rule)
  - scripts/run_parser_sync_monitor.sh                (SCT-7 wrapper)

next:      SCT-1b — handle TT_IF / TT_WHILE / TT_RETURN as
           statement-position nodes (currently emit '?TT_NN?' string
           placeholders).  These are the three remaining unhandled
           tags in parser_snobol4.sc.  Implement per ARCH-SNOCONE.md
           "Lowering map" — TT_IF lowers to `cond :F(after) / body /
           after`, TT_WHILE to `top  cond :F(after) / body / :(top) /
           after`, TT_RETURN in statement position to assignment +
           :(RETURN).

authors:   Goal authored by Lon Cherryholmes + Opus 4.7, 2026-05-17.
           SCT-1 partial landed same day, Opus 4.7.
```

---

## 🧭 Relationship to other goals

| Goal | Relationship |
|------|--------------|
| `GOAL-PST-REBUS.md` | This goal **does not block** PST-REBUS. PST-REBUS continues fixing the direct Snocone-runtime path (`rt_bb_arbno` ζ corruption, BB-cache, labtab). This goal builds an **alternate path** that doesn't depend on those bugs being fixed — it transpiles around them. When PST-REBUS lands, the two paths converge: SCRIP runs `.sc` directly AND transpiles correctly; both produce identical AST. |
| `GOAL-PARSER-PURE-SYNTAX-TREE.md` | This goal **depends on** that one's invariant that LOWER produces `tree_t` correctly. The transpiler walks the same `tree_t`. If LOWER is wrong, transpiler is wrong by transitivity — but the sync-monitor will reveal that as a divergence. |
| `GOAL-LANG-SNOCONE.md` | This goal **defines** the Snocone subset. The post-SCT-11 spec becomes input to LANG-SNOCONE acceptance criteria. |
| `GOAL-PST-PROLOG.md` | Orthogonal. SCT-6 (Prolog) can land independently. |

---

## 📝 Notes for future sessions

### Core invariants

- **The transpiler is a C program**, not Snocone. Lives in `src/lower/lower_sno.c` + `src/lower/lower_sno.h`. Walks `tree_t*` produced by ANY of the six SCRIP frontends (Snocone, SNOBOL4, Icon, Prolog, Raku, Rebus). Outputs SNOBOL4 to stdout. Driven by `scrip --dump-sno`. Per RULES.md "case-sensitive only": no folding anywhere; identifiers pass through verbatim.
- **Trust LOWER.** If transpiler emits `oops`, LOWER probably emitted `oops` first. Fix LOWER, the transpiler stays correct. The transpiler is mechanical — it must not "smart-correct" anything from the AST.
- **The 2-way harness already exists.** `scripts/test_monitor_2way_spitbol_vs_sm.sh` (and the `test_monitor_3way_sync_step_auto.sh` it delegates to) were built in session #19. Reuse via the thin wrapper `scripts/run_parser_sync_monitor.sh`, don't rebuild.
- **6 functions, no more.** `shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop`. Any rung that introduces a seventh primitive must be a separate `.github` issue documenting why — never silent. The discipline is the spec.

### How-to: clone and bring up a fresh session

```bash
# Standard three repos
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
git clone https://TOKEN@github.com/snobol4ever/one4all  /home/claude/one4all

# Optional fourth — only needed if you're touching cross-engine infra or
# want SPITBOL build instructions on hand:
git clone https://TOKEN@github.com/snobol4ever/harness  /home/claude/harness

# SPITBOL x64 source lives in its own repo (NOT bundled with harness):
git clone https://TOKEN@github.com/snobol4ever/x64      /home/claude/spitbol-x64
# In Lon's environment the built binary is at /home/claude/x64/bin/sbl ;
# our scripts default to that path.  See "Building SPITBOL" below.

# Required packages on a fresh Ubuntu sandbox (one4all needs libgc):
apt-get install -y libgc-dev libgc1 build-essential
```

### How-to: build `scrip`

```bash
cd /home/claude/one4all && make scrip
# Build artifacts go to /tmp/si_objs/  ; binary is ./scrip
# The Makefile assumes libgc is on the linker path — `-lgc -lm` at link.
# Compile rule for lower_sno.c is at Makefile line ~288, between
# lower_pl.c and sm_image.c.
```

If you add a new C file under `src/lower/`, you must update **two** places in `Makefile`:
1. The SRC list around line 90+ (add `$(SRC)/lower/yourfile.c \`)
2. The explicit compile rule around line 286+ (`$(CC) $(CRT) -c ... -o $(OBJ)/yourfile.o`)

### How-to: use `--dump-sno`

```bash
# Any of the six frontends — extension determines language:
./scrip --dump-sno corpus/SCRIP/parser_snobol4.sc       # .sc → Snocone frontend
./scrip --dump-sno corpus/programs/snobol4/parser/atom_id.sno   # .sno → SNOBOL4 frontend
./scrip --dump-sno corpus/programs/icon/parser/fail_stmt.icn    # .icn → Icon frontend
# etc.

# Sanity self-test (round-trip):
./scrip --dump-sno foo.sc > /tmp/foo.sno
echo "" | ./scrip --sm-run /tmp/foo.sno
# If exit is 0 and no '** Error' lines, the transpile produced valid SNOBOL4.

# Count remaining unhandled node kinds in a given input:
./scrip --dump-sno corpus/SCRIP/parser_<lang>.sc | grep "?TT_" | sort -u
```

### How-to: where things are in `lower_sno.c`

Single file at `src/lower/lower_sno.c`. Structure top-to-bottom:
1. `sno_ctx_t` — emission state (FILE*, line counter, `pending_label`)
2. `emit`, `emit_nl`, `sval_or` — utilities
3. **`emit_expr(c, e)`** — recursive walker for tree_t in expression position. Big switch on `e->t`. Each case is one TT_* tag. Default emits `'?TT_NN?'` as a string literal so the surrounding statement still parses.
4. **`emit_stmt(c, s)`** — handles TT_STMT (a full SNOBOL4 statement line). Demuxes children by tag (`:subj`, `:pat`, `:repl`, `:eq`, `:goS`, `:goF`, `:go`, `:lbl`). Has a special branch for TT_DEFINE-as-subject that emits the Gimpel template.
5. **`emit_node(c, n)`** — top-level dispatch. Routes TT_STMT→emit_stmt, TT_PROGRAM→emit_program, TT_RETURN/TT_PROC_FAIL/TT_NRETURN→goto emission, default→bare-expr statement.
6. **`emit_program(c, p)`** — iterates children of TT_PROGRAM
7. **`tree_to_sno(ast, out)`** — public entry. Wraps with `&FULLSCAN = 1` prelude and `END` terminator.

To add support for a new TT_* tag:
- If it's expression-only (TT_NEW_OP combining sub-expressions): add a case in `emit_expr`'s switch.
- If it's statement-shape (TT_IF, TT_WHILE — has its own control flow): add a case in `emit_node`'s switch. The lowering pattern comes from ARCH-SNOCONE.md §"Lowering map".

### How-to: identify a `?TT_NN?` placeholder

The number is the C enum index of `tree_e` in `src/include/ast.h`:

```bash
# Enum starts at TT_QLIT=0 and runs through TT_KIND_COUNT.  Quick lookup:
python3 -c "
import re, sys
with open('/home/claude/one4all/src/include/ast.h') as f:
    txt = f.read()
m = re.search(r'typedef enum tree_e \{([^}]+)\}', txt, re.S)
tags = [t.strip() for t in m.group(1).split(',') if t.strip() and 'TT_' in t]
n = int(sys.argv[1])
print(f'TT_{n} = {tags[n]}')
" 95
# → TT_95 = TT_IF
```

Current known unhandled tags in `parser_snobol4.sc` post-SCT-1: TT_IF (95), TT_WHILE (90), TT_RETURN-in-expr-position (97).

### How-to: trick used to make label-lines parse

SCRIP's SNOBOL4 frontend REJECTS lines that are pure labels (label at col 1, no subject/pattern/repl/goto). Two techniques:
- **Function name label** → use `pending_label` field in `sno_ctx_t`; set before emitting body, the next `emit_stmt`/`emit_node` consumes it as col-1 label.
- **Trailing end-label** → pad with `OUTPUT =` (no-op empty assignment).

### How-to: unary operators must be tight

`(. dummy)` with a space → parse error. `(.dummy)` tight → OK. All unary operators in `emit_expr` emit tight: `(.X)`, `($X)`, `(*X)`, `(-X)`, `(+X)`, `(~X)`, `(?X)`, `(@X)`. Don't add spaces.

### How-to: TT_QLIT with embedded quotes

The emitter picks the delimiter that doesn't appear in the body:
- contains `'` only → emit as `"..."`
- contains `"` only → emit as `'...'`
- contains both → emit as `'...'/*BOTH-QUOTES*/` (no portable encoding; SNOBOL4 has no backslash escapes per ARCH-SNOCONE.md). The comment marker makes the problem visible; runtime use of `CHAR(34)`/`CHAR(39)` is the fix when this occurs.

### How-to: drive the 2-way sync-step monitor

```bash
# Wrapper does --dump-sno + delegate to existing harness:
bash scripts/run_parser_sync_monitor.sh snobol4 corpus/programs/snobol4/parser/atom_id.sno

# What it does internally:
#   1. ./scrip --dump-sno corpus/SCRIP/parser_snobol4.sc > /tmp/parser_snobol4.sno
#   2. exec bash scripts/test_monitor_2way_spitbol_vs_sm.sh /tmp/parser_snobol4.sno < sample
# The downstream test_monitor_*.sh scripts read MONITOR_READY_PIPE / MONITOR_GO_PIPE
# from env and drive the IPC wire defined in monitor_wire.h.

# Exit codes (wrapper):
#   0 — both runtimes agreed throughout
#   1 — divergence detected
#   2 — transpile or SPITBOL-launch failed
#   3 — usage error / missing parser_<lang>.sc or sample
```

The monitor compares **NAME / READY / GO** records on a binary wire defined in `scripts/monitor_wire.h`. Per `test_monitor_3way_sync_step_auto.sh` header, **no source preprocessing** — the .sno runs unmodified; both runtimes emit catch-all trace records inline.

### How-to: build SPITBOL x64 (if not already built)

Source repo: **`github.com/snobol4ever/x64`** (separate repo, not bundled with `harness`).
Build recipe lives in `harness/oracles/spitbol/BUILD.md`. Summary:

```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/spitbol-x64
apt-get install -y build-essential nasm

cd /home/claude/spitbol-x64
# Apply systm.c patch — clock_gettime nanoseconds → milliseconds.
# See harness/oracles/spitbol/BUILD.md for the exact PATCH heredoc.
make
cp sbl /usr/local/bin/spitbol     # or /home/claude/x64/bin/sbl per Lon's layout
```

**Important compatibility notes from harness BUILD.md:**
- SPITBOL has NO `&STNO` keyword (use `&LASTNO`)
- SPITBOL has NO `LOAD()` (EXTFUN=0)
- SPITBOL has NO `LABELCODE()`
- SPITBOL `DATA()` returns lowercase type names; CSNOBOL4 returns uppercase
- Invocation: `spitbol -b program.sno` (the `-b` suppresses the banner, required for clean stdout diff)

**For the monitor:** SPITBOL needs the SN-26-spl-bridge patch (landed in `x64` session #27). Without it the binary is silently no-op on the wire. The bridge activates only when `MONITOR_READY_PIPE` is set in env.

### How-to: round-trip-test a transpiled parser

```bash
# Quick smoke (don't drive SPITBOL yet, just see if SCRIP's own SNOBOL4 frontend
# accepts the output):
./scrip --dump-sno corpus/SCRIP/parser_<lang>.sc > /tmp/p.sno
echo "" | ./scrip --sm-run /tmp/p.sno 2>&1 | head -5

# Expected progressions on SCT-1 work:
#   a) "parse error: syntax error"      → emitter bug, syntax we generate
#                                          isn't accepted by SCRIP SNOBOL4
#   b) "undefined label 'XXX'"          → emitter bug, we reference a label
#                                          without emitting it
#   c) "** Error N in statement K"      → runtime divergence; this is what
#                                          the 2-way monitor is for

# To test against SPITBOL once it's available:
spitbol -b /tmp/p.sno < sample.txt
```

### Files this goal touches across the three repos

| Repo | Path | Role |
|------|------|------|
| one4all  | `src/lower/lower_sno.{c,h}` | The transpile pass itself |
| one4all  | `src/driver/scrip.c` | `--dump-sno` CLI wiring |
| one4all  | `Makefile` | Build rule + SRC list entry for lower_sno.c |
| one4all  | `scripts/run_parser_sync_monitor.sh` | SCT-7 thin wrapper |
| corpus   | `SCRIP/parser_*.sc` | The six inputs being transpiled |
| corpus   | `SCRIP/README.md` | SCT-0a reading-completed timestamp line lives here |
| corpus   | `programs/<lang>/parser/*.<ext>` | Sample inputs fed through the transpiled parsers |
| .github  | `GOAL-PARSER-SC-TRANSPILE.md` | This file |
| .github  | `ARCH-SNOCONE.md` | Lowering map authority (§"Lowering map") |
| harness  | `oracles/spitbol/BUILD.md` | How to build SPITBOL x64 if not already built |
| x64      | (source tree) | SPITBOL source — separate repo, snobol4ever/x64 |

### Open architectural decisions for next session

1. **TT_IF / TT_WHILE statement-position lowering** (SCT-1b). Three constructs from ARCH-SNOCONE.md "Lowering map", each ~30 lines of emit code. Order of work: TT_IF first (cleanest two-branch shape), then TT_WHILE (loop with break label), then TT_RETURN-as-stmt-subject (single goto emission already done for top-level; just thread through the STMT-wrapper path in emit_stmt).
2. **Whether to elide parens for non-ambiguous operator combinations.** Currently every binary op gets `(left op right)`. SPITBOL Manual Ch.15 priority table is ground truth for what's safe; a future SCT-1c rung could halve output size. Not necessary for correctness.
3. **Label uniquification.** Function bodies may contain labels (from goto/label_emit). If two functions both contain label `loop`, the transpiled .sno has a conflict. Snocone's frontend already uniquifies via the `g_sc_label_seq` counter (per README.md PARSER-SN-INFRA-5a) — so the AST should already have `_Ltop_0001` etc.  Verify when SCT-2 reads parser_snocone.sc's output.
