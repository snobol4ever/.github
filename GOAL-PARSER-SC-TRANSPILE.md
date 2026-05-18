# GOAL-PARSER-SC-TRANSPILE.md — Six parser_*.sc producing AST trees via Snocone→SNOBOL4 transpile + 2-way sync-monitor harness

**Repo:** one4all + corpus + .github
**Parent:** Independent goal complementing `GOAL-PARSER-PURE-SYNTAX-TREE.md` and `GOAL-PST-REBUS.md`
**Author:** Lon Jones Cherryholmes · Claude Opus 4.7
**Date opened:** 2026-05-17

---

## ⛔ Session Start Protocol (every session, no exceptions)

Before touching any code in this goal, the session must:

1. **Clone the standard three repos** (`.github`, `corpus`, `one4all`) per the global `PLAN.md` protocol, **plus `snobol4ever/x64` to `/home/claude/x64`** for the SPITBOL oracle. `x64` contains a prebuilt binary at `/home/claude/x64/bin/sbl` — no build step required for routine validation work; just clone and the oracle is live. Only clone `harness` if you need the build recipe (`oracles/spitbol/BUILD.md`) to rebuild SPITBOL from source — not needed for this goal's day-to-day work. See "How-to: clone and bring up a fresh session" below for one-shot commands.
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
- **The 2-way sync-step monitor (already built) becomes a Snocone debugger.** `parser_<lang>.sc → parser_<lang>.sno → SPITBOL + SCRIP --interp/--run side by side`, divergence reported at the first differing CALL/RETURN/VALUE event. Each bug in SCRIP's Snocone runtime shows up as a clean divergence with a 5-line repro.
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
   - SCRIP `--interp`, `--interp`, `--run` (all three modes)
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

A separate path runs the original `.sc` through SCRIP directly (`--interp corpus/SCRIP/...` chain), and compares its output to the transpiled `.sno`-via-SPITBOL output. That's the **outer** Snocone-runtime oracle. The sync-monitor handles the **inner** divergence-when-running-the-same-.sno cross-mode test.

---

## 🪜 Rungs (execute in order; one construct per commit unless documented as composite)

### Phase 0 — Reading & Snocone fluency

- [x] **SCT-0a** ✅ 2026-05-17 (Opus 4.7) — Session-start reading complete: SPITBOL manual via /tmp/spitbol.txt (Ch 8/9/14/15/17/18/19, App C), `parser_snocone.sc` (931 lines), `corpus/SCRIP/README.md`, `.github/ARCH-SNOCONE.md`. Output: §"SPITBOL Manual Reading Index & Map" added to this file (verified line numbers, supersedes the missing GOAL-PST-REBUS cheatsheet). No source touched. one4all and corpus untouched.
- [ ] **SCT-0b** — Hand-write a 5-line `.sc` "echo" program that exercises: literal pattern, ANY/SPAN/BREAK, `shift(lit, 'TT_QLIT')`, `reduce('TOP', 1)`, `nPush/nInc/nTop/nPop`. Confirm runs cleanly under existing SCRIP shared-runtime chain. This is the lowest-common-denominator surface for SCT-1 to target. Commit: the test file under `corpus/SCRIP/tests/sct_echo.sc` + matching `.ref` SPITBOL would produce if hand-translated.

### Phase 1 — Transpiler MVP

- [x] **SCT-1 — Bootstrap: `parser_snobol4.sc` → `parser_snobol4.sno`.** ✅ 2026-05-17 (Opus 4.7).
  Implemented `src/lower/lower_sno.{c,h}` (not `src/transpile/sc_to_sno.c` — placement updated per Lon directive: lives as peer to `lower_icn.c`/`lower_pl.c`). Reads `tree_t*` produced by any frontend, walks it, emits SNOBOL4 on stdout. Wired as `--dump-sno` (mirrors `--dump-ast`/`--dump-sm`/`--dump-bb` family). Handles ~30 TT_* tags including atoms, all unary operators, binary arithmetic, pattern composition (TT_SEQ/CAT/ALT/VLIST), pattern captures (`.`/`$`), function calls, indexing, named pattern primitives (ARB/REM/BAL/FAIL/SUCCEED/ABORT/FENCE/ARBNO), embedded assign/scan, and the Gimpel function template (TT_DEFINE → `DEFINE(proto) :(fn_end)` / label / body / `:(RETURN)` / end-label). Landed in one4all `f2e0dd81`.

- [x] **SCT-1b — Statement-position control flow + label-sanitize.** ✅ 2026-05-17 (Opus 4.7), one4all `e9ee90e4`.
  In `lower_sno.c::emit_stmt`, added dispatch when `:subj` carries one of: TT_IF / TT_WHILE / TT_DO_WHILE / TT_FOR / TT_RETURN / TT_PROC_FAIL / TT_NRETURN / TT_LOOP_BREAK / TT_LOOP_NEXT. Lowering per `ARCH-SNOCONE.md` §"Lowering map".
  - **TT_IF** allocates `_Lelse_NNNN` / `_Lendif_NNNN` via in-emitter `if_seq` counter (the C frontend's PST mode keeps TT_IF as a tree — no pre-allocation).
  - **TT_WHILE / TT_DO_WHILE / TT_FOR** read pre-allocated `_Ltop_NNNN` / `_Lcont_NNNN` / `_Lend_NNNN` from trailing TT_QLIT children stashed on the loop node by the C frontend.
  - **TT_LOOP_BREAK / TT_LOOP_NEXT** read top of a 64-deep loop-label stack in `sno_ctx_t`.
  - **TT_RETURN / TT_PROC_FAIL / TT_NRETURN** emit `:(RETURN)` / `:(FRETURN)` / `:(NRETURN)`.

  Also fixed two pre-existing bugs surfaced during this work: `:lbl` attr's label payload lives in `c[0]->v.sval` not the attr's own `v.sval`; `TT_GOTO_U`'s label same shape. Both fixed via new `label_of()` helper.

  Added `label_sanitize()` — strips leading underscore per SPITBOL Manual Ch.14 line 9335 ("Labels must begin with a letter or digit"). The Snocone PST mode pre-allocates `_Ltop_NNNN` which SPITBOL rejects with ERROR 230 and SCRIP `--interp` silently mangles. Threaded through every label emission site via a 4-deep buffer ring so multiple `label_sanitize()` calls in one printf format don't clobber.

  Padded label-only statements with `OUTPUT =` so SCRIP's SNOBOL4 parser (which rejects label-only lines) accepts them.

  Result: `parser_snobol4.sc` transpile: 4 placeholders → **0**. All six parser_*.sc → 0 placeholders.

- [x] **SCT-1c — SNOBOL4 line-continuation for >1024-char emissions.** ✅ 2026-05-17 (Opus 4.7), one4all `c1074e5f`.
  SPITBOL hard-fails with ERROR 226 (missing right paren) on any line over 1024 chars (Manual Ch.14 line 9022). `parser_snobol4.sc`'s `Expr17` is one 1908-char TT_ALT; `parser_raku.sc` was 2233; `parser_icon.sc` was 1323. Fix: redirected `emit()` through an in-context line buffer (16KB), `emit_nl()` scans backward from offset 900 for a space/tab outside quoted strings (`sno_in_quoted` walks from start because SNOBOL4 has no escape character — every quote is structural). Splits at safe positions, emits chunks separated by `\n+` per SPITBOL Manual Ch.14 line 9456+. Safe-split reliability comes from `emit_expr` parenthesising every binary op — every space between tokens IS a safe split point.
  Result on all 6 parsers: longest physical line drops to ≤899 chars (was up to 2233).

- [x] **SCT-1d — Multi-file `--dump-sno` + `-CASE 0` prelude + dedup tail `:(RETURN)` + wrapper.** ✅ 2026-05-17 (Opus 4.7), one4all `b31e72e4`+`f097651a`, corpus `c97eeb0`.
  Three orthogonal changes that together make `scrip --dump-sno <runtime files> parser_X.sc` produce a self-contained `.sno`:
  - **Multi-file mode** (`src/driver/scrip.c`): `--dump-sno` previously emitted the first file's AST and returned. Restructured to mirror `--dump-sm`: accumulate via `MERGE_AST` across all argv files, emit at end of multi-file loop. Applies to both the snocone/rebus/icon/raku/prolog branch and the SNOBOL4 branch.
  - **`-CASE 0` prelude** (`src/lower/lower_sno.c`): SPITBOL Manual Ch.14 line 9067+: case-fold-to-upper is the default. Without `-CASE 0`, `ShiftReduce.sc`'s `Shift(t,v,s)` collapses with `semantic.sc`'s `shift(p,t)` → SPITBOL ERROR 217 duplicate label. RULES.md mandates byte-for-byte case sensitivity, so `-CASE 0` enforces existing Snocone semantics on the emitted side. SCRIP's SNOBOL4 frontend already case-sensitive (no-op control directive).
  - **Suppress redundant tail `:(RETURN)`** (`src/lower/lower_sno.c`): when a function body ends with explicit `return;` we emit `:(RETURN)`, then the Gimpel template tail emits ANOTHER. Added `last_was_return` flag set in `emit_nl` when the buffered line ends with `:(RETURN)/:(FRETURN)/:(NRETURN)`. Template tail skips when set.
  - **Wrapper** (`scripts/run_parser_sync_monitor.sh`): now passes the full Snocone runtime prelude (`global.sc tree.sc stack.sc counter.sc ShiftReduce.sc semantic.sc tdump.sc`) alongside the parser. Added 1024-char line-length sanity warning.
  - **Corpus rename** (`corpus/SCRIP/semantic.sc`): `_qtag` → `qtag`. Only underscore-leading function name in the seven runtime `.sc` files. SPITBOL rejects underscore-leading identifiers in `DEFINE()` with ERROR 230.

  Result on `scrip --dump-sno <runtime> parser_snobol4.sc`: 885 lines, **SPITBOL accepts end-to-end with zero parse errors**, single runtime ERROR 041 at line 873 (`n(ptree)` on non-tree value — downstream parsing-execution, not transpile). SCRIP `--interp` segfaults during execution (also downstream).

- [x] **SCT-1e — Investigate the single SPITBOL runtime ERROR 041.** ✅ 2026-05-17 (Opus 4.7).
  **Root cause: transpiler bug in `lower_sno.c::emit_expr` TT_SCAN case** (option (a) from the original three candidates — but the actual misbehavior was inside the transpiler, not the source `.sc`). The case emitted `(SUBJ PAT)` (space-as-concat) instead of `(SUBJ ? PAT)` (explicit match operator). The author's comment claimed "space-as-match for standard-SNOBOL4 compatibility," which is wrong: inside an expression context, space is the binary CONCAT operator (SPITBOL Manual Ch.15 priority 4), NOT pattern-match. The match operator at expression level is the explicit `?` (Ch.15 priority 1).
  Consequently `if (Src ? Compiland)` was lowering to `if (Src CONCAT Compiland)`: the parens evaluated to a pattern value (Src concatenated with the Compiland pattern) which was then discarded. **No actual pattern-match ever happened.** The `:F` branch never fired (a pattern-valued expression as a statement-subject doesn't fail-by-default; it just evaluates and continues), so control fell into the "succeeded" path. `ptree = Pop()` then retrieved whatever stale value was on the runtime stack (most likely a counter return from a previous `nPop()`), and `n(stale_value)` triggered ERROR 041.
  **Fix:** changed the TT_SCAN expression-case emission from `(SUBJ PAT)` to `(SUBJ ? PAT)` with whitespace on both sides of `?` (required by SCRIP's lexer rule `{W}"?"{W}` → `T_2QUEST`, and by SPITBOL). Verified accepted as a binary expression operator by SCRIP's `snobol4.y:114` and by SPITBOL. The statement-form TT_SCAN path (handled separately via TT_STMT's `:subj` + `:pat` attribute tags in `emit_stmt`) is unaffected.
  **Verified:**
  - All six parsers transpile cleanly with the change (zero `?TT_` placeholders).
  - Each parser's transpiled `.sno` contains 9–15 explicit `?` operator emissions (snobol4=10, snocone=11, rebus=9, icon=10, raku=15, prolog=9).
  - `parser_snobol4.sno` under SPITBOL with various sample inputs (`atom_id.sno`, `arith_add_mul.sno`, hand-written) now runs to clean exit with no diagnostic. Previously failed at stmt 869 / line 873 with ERROR 041.
  - SNOBOL4 smoke gate: PASS=6 FAIL=1 (the FAIL is pre-existing `pattern (got: abc)`, present on baseline before fix).
  - Snocone smoke gate: PASS=5 FAIL=0.
  Two-line code change in `src/lower/lower_sno.c` plus comment rewrite.

- [ ] **SCT-1f — Drive the 2-way sync-monitor.**
  Requires SPITBOL IPC patch (SN-26-spl-bridge in x64 session #27 per goal-file Notes). With ERROR 041 above ironed out (or even with it present — the monitor's job is to FIND divergences), run:
  ```
  bash scripts/run_parser_sync_monitor.sh snobol4 corpus/programs/snobol4/parser/atom_id.sno
  ```
  Acceptance: monitor reports either PASS or first divergence with line numbers.

- [x] **SCT-2 — `parser_rebus.sc` → `parser_rebus.sno`.** ✅ 2026-05-17 (Opus 4.7), continuation.
  **Rebus + Icon now run to clean exit under SPITBOL.** Two surgical fixes landed:

  **Fix #1 — `corpus/SCRIP/semantic.sc` line 31 (`qtag`):** swapped `REPLACE(t, "'", "")` for `REPLACE(t, "'", 'x')`. SPITBOL `REPLACE` requires equal-length 2nd/3rd args (it's a character-mapping translation, not substring substitution); the empty 3rd arg crashes with ERROR 171. The new form is portable on both runtimes: substitutes `'` for `x` (any non-apos char of same length), then `IDENT(result, t)` succeeds iff `t` had no apostrophes. Tested under both SPITBOL and SCRIP `--interp` with 3 inputs (has-apos / no-apos / empty); all 6/6 PASS. The original comment in semantic.sc claimed bare `ANY("'")` would work as an alternative but `--interp` showed SL-4 affects ANY too (false positives on no-apos inputs), so REPLACE is the only portable path. **Followup:** the underlying runtime divergence — SCRIP's `REPLACE` accepts unequal-length args, SPITBOL's doesn't — is now tracked as **SN-REPLACE-EQ** in `GOAL-LANG-SNOBOL4.md` and listed in the "follow SPITBOL" rule's "Known OPEN divergences" subsection.

  **Fix #2 — `one4all/src/lower/lower_sno.c` TT_VAR case + `label_sanitize()` strategy upgrade:** apply `label_sanitize()` to every emitted identifier, not just labels. SPITBOL Manual Ch.14 line 9335 (the same constraint that motivated SCT-1b for labels and SCT-1d's `_qtag` rename) applies to identifiers in pattern-capture position too. `parser_prolog.sc` uses `_op_name` as a `. _op_name` capture target dozens of times; SPITBOL rejected at first use with ERROR 230 illegal character. Two changes: (a) one-line addition in `emit_expr` TT_VAR case to route through `label_sanitize`; (b) sanitizer strategy upgraded per Lon directive (2026-05-17): strip **all** leading underscores and **append one trailing underscore**, instead of just stripping a single leading. Rationale: trailing-underscore identifiers are valid in SPITBOL (verified by direct test) and almost nobody writes user identifiers ending in `_`, so the sanitized form `op_name_` is essentially collision-free with any user-written `op_name`. The previous strip-only rule was collision-unsafe for the general case. Now: `_op_name → op_name_`, `_Ltop_0001 → Ltop_0001_`, `__foo → foo_` — all unique, all portable. Verified in the transpiled output of all 6 parsers; smoke gates hold.

  **SPITBOL sweep after both fixes:**
  ```
  snobol4    exit=0  CLEAN  (was: CLEAN)
  snocone    exit=0  CLEAN  (was: CLEAN)
  rebus      exit=0  CLEAN  (was: ERROR 171 @line 473)  🎯
  icon       exit=0  CLEAN  (was: ERROR 171 @line 473)  🎯
  raku       exit=0  ERROR 022 @line 943   (was: ERROR 171 — qtag fix unmasked
                                            missing raku_helpers — already known
                                            as SCT-5 prereq)
  prolog     exit=0  ERROR 022 @line 1615  (was: ERROR 230 @766,27 — TT_VAR fix
                                            advanced past the syntax error to
                                            same missing-helpers wall as raku;
                                            this is SCT-6 prereq territory)
  ```

  Smoke gates hold: snobol4 6/1 (1 pre-existing baseline FAIL, identical to SCT-1e watermark), snocone 5/0. No regressions.

  **Followups owned by other rungs:**
  - `--interp` still segfaults on all 6 via `rt_bb_arbno` → `bb_deferred_var` rebuild path (rt.c:1217 / stmt_exec.c:303). Owned by GOAL-PST-REBUS.
  - Raku's ERROR 022 is `parser_raku.sc` referencing undefined helpers like `Push_fn_raku_die`, `Push_fn_map`, `Push_fn_capture`, etc. — these aren't in `raku_helpers.sc` either, they're meant to be implementation hooks. Per goal constraint #2 these are forbidden in `parser_*.sc`; the proper SCT-5 work re-expresses these in terms of the six allowed primitives (`shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop`) or migrates to C-side `raku_lower.c`.
  - Prolog's ERROR 022 is analogous: `Push_nil`, `Push_cut`, `Push_char_code`, `Push_hex_int`, `Push_bin_int`, `Push_oct_int`, `Push_atom_body`, `Push_neg_float`, `Push_neg_int`, `Reduce_compound_ns`, `Reduce_list`, `Reduce_unop`, `do_uminus` — all undefined in any loaded `.sc`. SCT-6 territory.
  - Cosmetic: `lower_sno.c` emits `&FULLSCAN = 1` twice when source also emits it (prelude + passthrough). Harmless no-op pair under SPITBOL. Worth a 3-line dedup in `lower_sno.c::tree_to_sno`.

  Sample: `corpus/programs/rebus/parser/paren.reb` ✅.

- [ ] **SCT-3 — `parser_snocone.sc` → `parser_snocone.sno`.**
  The hardest one: parser_snocone.sc is 931 lines and uses constructs the others don't (record declarations, function returns). May expose `lower.c` gaps that surface as `[NO-AST]` stubs in transpile mode — fix those in `lower.c`, never in the transpiler. Sample: `corpus/programs/snocone/corpus/sc1_literals.sc`.

- [ ] **SCT-4 — `parser_icon.sc` → `parser_icon.sno`.**
  Sub-rung blocker: `icon_helpers.sc` must be deleted FIRST. Its 4 leaf-push helpers + `notmatch` get inlined into the grammar (`push_qlit` and friends become `shift(*X, 'TT_QLIT')` directly; `notmatch` was `~match` — express via OPSYN'd `~`). Sample: `corpus/programs/icon/parser/fail_stmt.icn`.

- [ ] **SCT-5 — `parser_raku.sc` → `parser_raku.sno`.**
  Sub-rung blocker: `raku_helpers.sc` must be deleted FIRST. The 9 `finish_*` variable-arity assemblers fold into `reduce` with `nTop()` argument. `push_interp_str` / `dq_unescape` migrate to C-side `raku_lower.c`. Sample: `corpus/programs/raku/parser/str_chars.raku`.

- [ ] **SCT-6 — `parser_prolog.sc` → `parser_prolog.sno`.**
  Independent of GOAL-PST-PROLOG's frontend work. The Prolog parser_*.sc is largest at 1040 lines; some constructs may need `lower.c` fixes. Sample: `corpus/programs/prolog/rung01_hello_hello.pl`.
  **Pre-finding (Opus 4.7, 2026-05-17, updated):** transpile is clean (1753 lines, 0 placeholders). The original ERROR 230 (illegal character @line 766,27 — `_op_name` pattern-capture variable) was **fixed in SCT-2** by extending `label_sanitize()` to TT_VAR emissions in `lower_sno.c`. SPITBOL now accepts the syntax of `parser_prolog.sno` end-to-end. Next layer: ERROR 022 (undefined function called) at line 1615 — same class as SCT-5's raku problem. `parser_prolog.sc` references `Push_nil`, `Push_cut`, `Push_char_code`, `Push_hex_int`, `Push_bin_int`, `Push_oct_int`, `Push_atom_body`, `Push_neg_float`, `Push_neg_int`, `Reduce_compound_ns`, `Reduce_list`, `Reduce_unop`, and `do_uminus` — none of these are defined in any loaded `.sc` file. Per goal constraint #2 these "language-specific helpers" must be eliminated: either re-expressed in terms of the six allowed primitives (`shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop`), or migrated to C-side `lower_pl.c`. This is the bulk of SCT-6's work.

### Phase 2 — Two-way harness

- [ ] **SCT-7 — Build the harness driver `scripts/run_parser_sync_monitor.sh`.**
  Wraps the existing IPC infrastructure (`monitor_sync_bin.py`, `monitor_ipc_bin_csn.c`, `x64/monitor_ipc_bin_spl.c`). Inputs: `<lang> <sample-file>`. Runs:
  1. `scrip --sc-to-sno parser_<lang>.sc > /tmp/parser_<lang>.sno`
  2. SCRIP side: `scrip --interp /tmp/parser_<lang>.sno < <sample>` with `MONITOR_READY_PIPE` set
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

  **Sub-rungs (work-in-progress):**

  - [x] **SCT-9a** ✅ ARBNO lazy-iteration fix — added `POS(0)`/`RPOS(0)`
    sentinels to all six parser_*.sc Compilands. corpus `664d633`.
    snobol4 + snocone produce correct AST from SPITBOL.

  - [x] **SCT-9b** ✅ `AST_*` → `TT_*` rename across all 224 parser fixture
    .ref files. corpus `b64f6f1`.

  - [x] **SCT-9c** ✅ 2026-05-17 (Opus 4.7) — TDump-matching C formatter.
    Replaced `ast_print.c::print_node` always-multiline-for-n>=2 rule with
    TDump/TLump-equivalent length-budget rule. New helper `flat_length(e, b)`
    computes inline width; node prints inline if it fits in `ast_print_width
    - depth*2` chars (matches `TLump(x, 140 - GetLevel())`), multiline
    otherwise. New globals `ir_set_print_width(w)` / `ir_get_print_width()`
    plus `--dump-width N` flag in `scrip.c` for runtime tuning (default 140).
    one4all `616a372b`. Done so sessions can use checksum/simple diff instead
    of writing a tree-pattern matcher.

  - [x] **SCT-9d** ✅ 2026-05-17 (Opus 4.7) — n-ary flattening in C snocone
    frontend. Added `sc_flatten_arith(op, left, right)` in `snocone_parse.y`
    that absorbs the left child when it carries the same tag (left-recursive
    grammar's mirror of `parser_snocone.sc::flatten_arith`'s right-recursive
    unfold). Wired for TT_ADD/SUB/MUL/DIV (the `sc_flatten_ops` set in
    parser_snocone.sc line 243), plus TT_SEQ (concat) and TT_ALT (alternation)
    which are built n-ary natively in the .sc grammar via ARBNO counter loops.
    TT_POW stays binary right-assoc. Bison regenerated `snocone_parse.tab.c`.
    one4all `616a372b`.

  - [x] **SCT-9e** ✅ 2026-05-17 (Opus 4.7) — qize.sc `LEQ` dead-function
    purged. The user-defined `LEQ` in `qize.sc` (a string-min helper) shadowed
    SPITBOL's built-in `LEQ` lexicographic predicate, causing ERROR 248 at
    runtime when transpiled `.sno` included qize.sc. The function was never
    called outside qize.sc (omega.sc and sm_interp.sc use the SPITBOL builtin
    `LEQ` as a predicate, not the qize string-min). Removed entirely. corpus
    `1b24df4`. Result: parser_snocone.sno + qize.sc now runs CQize cleanly
    under SPITBOL, so TT_QLIT/TT_CSET nodes print properly via TDump.

  - [x] **SCT-9f** ✅ 2026-05-17 (Opus 4.7) — regenerate all 60 snocone
    parser-fixture .ref files from `scrip --dump-ast` after SCT-9c+9d landed.
    corpus `1b24df4`. Snocone fixture gate: PASS=24 FAIL=2 SKIP=41:
    - 24 pass: C --dump-ast and SPITBOL TDump produce byte-identical output
      via simple `diff`.
    - 2 fail: do_simple, do_with_stmt — C PST emits TT_DO_WHILE as a tree
      node; .sc parser emits lowered STMT sequence. Structural, not
      formatting. Either C PST or .sc parser needs alignment; see SCT-9i.
    - 41 skip: control-flow / function-call / switch fixtures blocked by
      the `$'(' = pattern` token-slot bug (SPITBOL can't assign through
      indirect to special-char names). Owned by SCT-9h below.

  - **SCT-9g — Precedence and associativity audit across ALL SIX languages.**
    (Lon directive 2026-05-17, scope-expanded 2026-05-17 Opus 4.7.) The
    transpiler covers six frontends (snobol4, snocone, rebus, icon, raku,
    prolog), each with a C-side parser in `src/frontend/<lang>/` AND a
    Snocone-side `parser_<lang>.sc`. Both sides must produce the same
    `tree_t` shape AND that shape must match the language's authoritative
    spec (SPITBOL Manual for snobol4/snocone, language reference for the
    others). Action items per language:
    1. Enumerate every binary operator in the C grammar and confirm its
       precedence + associativity vs the language spec.
    2. Cross-check `parser_<lang>.sc` against the same.
    3. For each operator, list the canonical 3-arg test (`a OP b OP c`) and
       the expected n-ary-flattened tree. Both grammars must produce the
       same shape after flatten.
    4. Document divergences in `.github/PRECEDENCE-AUDIT.md` (one section
       per language). Commit grammar-correction patches per Lon decision.

    Sub-rungs (one per language; each independent):

    - [x] **SCT-9g-snocone** ✅ 2026-05-17 (Opus 4.7).
      Spec: SPITBOL Manual v3.7 Ch.15 (operator priority table at line 9830+).
      Oracle: live `sbl` at `/home/claude/x64/bin/sbl`, verified by
      `probe_assoc.sno` and `mixed_op_truth.sno` (manual matches binary
      throughout). **Findings:**
      - `+ - * /` (pri 6/6/9/8) are LEFT-assoc per Manual + oracle. **C frontend
        (`snocone_parse.y`) is correct.** **`.sc` (`parser_snocone.sc`) is
        right-recursive — wrong** for mixed-op chains (`a+b-c` produces
        `(TT_ADD a (TT_SUB b c))` instead of `(TT_SUB (TT_ADD a b) c)`).
        Smoking-gun: `20 - 5 + 2` — SPITBOL = 17, C path = 17, `.sc` direct-exec
        path = 13.
      - POW (pri 11) correctly RIGHT-assoc in both.
      - CAPT `$` `.` (pri 12) LEFT-assoc in C; `.sc` hand-rolled 2-deep FENCE
        (accepts max `a.b.c`, rejects `a.b.c.d`). Low impact for current corpus.
      - `?` (pri 1) is right-assoc in both; Manual says LEFT. Low impact.
      - Snocone-extension binary `# % & ~ @` present only in `.sc`. C
        grammar-coverage gap.
      **Deliverable:** `.github/PRECEDENCE-AUDIT.md` (Snocone section in place).
      **Recommended fix:** Bring `.sc` to match SPITBOL Manual + C frontend
      (rewrite Expr6..Expr11 right-recursion to n-ary left-folding). **Lon
      decision required** before applying.
      **Bonus fix landed:** `src/lower/lower_sno.c::emit_expr` TT_ADD/SUB/MUL/DIV
      cases were emitting only `c[0] op c[1]`, silently dropping n-ary children
      `c[2..n-1]`. Rewrote as left-folded n-ary emission. Verified end-to-end:
      `--dump-sno | sbl` of `20-5+2` → 17 (was 5); `100-30+10-5` → 75 (was 65).
      Snocone fixture gate: 60/7/0 pre = 60/7/0 post (no regressions; the 7
      FAILs are pre-existing augmented_* and break_for/continue_for).
      Followup: `.sc` grammar fix per Lon decision.

    - [ ] **SCT-9g-snobol4** — Audit `parser_snobol4.sc` and `src/frontend/snobol4/`
      against SPITBOL Manual v3.7 (already in `spitbol-manual-v3_7.pdf`,
      authoritative for SNOBOL4 too via App C deltas). Same procedure as
      9g-snocone. Spec already on disk — no new doc needed from Lon.
      Anchor: Ch.15 operator table (manual line 9830+) and App C
      "Differences from SNOBOL4" (line 13651+).

    - [ ] **SCT-9g-rebus** — Audit `parser_rebus.sc` and `src/frontend/rebus/`.
      **Spec document needed from Lon.** Rebus is Mark Emmer's preprocessor;
      no public spec is on disk (the SPITBOL Manual line 9388 mentions
      "preprocessors such as Rebus and Snocone" but no grammar). Without
      a reference, the audit can only enumerate what's accepted, not what's
      *intended*. Ask Lon for a Rebus syntax/operator reference document.

    - [ ] **SCT-9g-icon** — Audit `parser_icon.sc` and `src/frontend/icon/`
      against the Icon Programming Language reference (Griswold's book or
      its operator-precedence table). **Spec document needed from Lon.**
      Icon's operator system differs substantially from SPITBOL/SNOBOL4
      (e.g. `:=` assignment, `<-` reversible assignment, `|` alternation
      with generator semantics rather than pattern alternation, augmented
      ops like `+:=`, comparison operators that return their second
      operand or fail). The audit must cite the Icon spec, not the SPITBOL
      manual.

    - [ ] **SCT-9g-raku** — Audit `parser_raku.sc` and `src/frontend/raku/`
      against Raku's operator table. **Spec document needed from Lon.**
      Raku has the richest operator system of the six (chained operators,
      hyper operators, meta operators, custom precedence levels). The
      current `parser_raku.sc` likely implements a subset; the audit must
      identify which Raku operators are in scope.

    - [ ] **SCT-9g-prolog** — Audit `parser_prolog.sc` and `src/frontend/prolog/`
      against the Prolog operator table (`op/3` declarations: standard
      operators like `,` (1000, xfy), `;` (1100, xfy), `:-` (1200, xfx),
      `is` (700, xfx), `=` (700, xfx), comparison ops, arithmetic).
      **Spec document needed from Lon.** ISO Prolog standard or
      SWI-Prolog operator table acceptable. Note: Prolog operator
      declarations come in three flavours (xfx, xfy, yfx) which encode
      both arity and associativity; the audit must cover all three.

    - [ ] **SCT-9g-cross — Cross-language consistency sweep.**
      After the six per-language audits land, sweep `.github/PRECEDENCE-AUDIT.md`
      for cases where the same operator appears in multiple languages with
      different precedence/associativity. Flag any cross-language symbol
      that needs a consistency call from Lon. Examples: `.` is unary
      "name" in SPITBOL/Snocone, member-access in Raku, list-cons in
      Prolog; `|` is pattern-alt in SPITBOL/Snocone, generator-alt in
      Icon, disjunction in Prolog; `,` is comma in argument lists in
      all but is also Prolog's high-priority conjunction operator. These
      are not bugs (each language has its own spec) but the cross-table
      must be explicit to avoid surprise in the transpiler.

  - [ ] **SCT-9h — Token-slot mangling: `$'(' = pat` → legal SNOBOL4 names.**
    SPITBOL can't assign through indirection to variables whose names contain
    special characters (segfaults on `($'(') = …`). Even legal-identifier
    keyword slots like `($'if') = …` segfault. Fix in `lower_sno.c`: when
    emitting a `TT_INDIRECT(TT_QLIT "str")` node in either expression or
    LHS-of-assignment position, mangle the QLIT body into a legal SNOBOL4
    identifier (`sc_tok_LPAREN`, `sc_tok_IF`, etc.) and emit that bare name
    instead of `($'str')`. The mangling table must be deterministic across
    all six parsers so the same token slot maps to the same name everywhere.
    Estimated impact: unblocks ~40 of the 41 currently-skipped snocone
    fixtures plus most rebus/icon/raku/prolog fixtures.

  - [ ] **SCT-9i — do/while PST structural alignment (C vs .sc).**
    Two snocone fixtures (`do_simple`, `do_with_stmt`) fail because:
    - C frontend (PST mode) emits `(STMT :subj (TT_DO_WHILE cond body))` —
      tree-shape, finalize_do lowering deferred to LOWER pass.
    - `.sc` parser (`finalize_do` in parser_snocone.sc line 363) emits a
      lowered STMT sequence: `(STMT :lbl Ltop)`, body stmts, `(STMT :subj
      cond :goS Ltop)`, `(STMT :lbl Lend)`.
    Decision needed: which is canonical? Likely C PST should also keep
    TT_DO_WHILE as a tree (matching TT_WHILE/TT_FOR which already do), and
    `.sc` should defer lowering. Lon decision required. Once aligned, both
    `do_*` fixtures pass.

  - [ ] **SCT-9j — Wire `scripts/test_parser_sc_transpile.sh`.**
    Per-language fixture gate. For each `(lang, fixture)`:
    1. Transpile parser_<lang>.sc → /tmp/parser_<lang>.sno via `scrip --dump-sno`
    2. Run fixture through SPITBOL with the transpiled parser → SPITBOL TDump output
    3. Run fixture through `scrip --dump-ast` → C reference output
    4. Compare via byte-identical `diff` (now possible after SCT-9c).
    Goal acceptance criterion: 24/24 PASS across (snobol4, snocone, rebus,
    icon, raku, prolog) × 4 sample fixtures each.

  - [ ] **SCT-9k — Cross-validate snobol4/rebus parsers' TDump output vs C.**
    The snobol4 transpiled parser currently produces `(TT_STMT () (TT_LABEL)
    (TT_EQ ...))` — different tree shape than C's `(STMT :eq :subj ...)`.
    This is the snobol4 parser's tree-construction itself, not formatting.
    Diagnose: is parser_snobol4.sc producing the canonical STMT shape, or
    a transitional form? Align before declaring SCT-9 complete.

- [ ] **SCT-10 — Delete sidecar helpers permanently.**
  `corpus/SCRIP/icon_helpers.sc` and `corpus/SCRIP/raku_helpers.sc` removed from corpus. `run_scrip_parser.sh` no longer loads them. README updated. Gate: SCT-9 still passes.

- [ ] **SCT-11 — Document the Snocone subset.**
  `corpus/SCRIP/SNOCONE-SUBSET.md` — the formal grammar of "the Snocone the parser_*.sc files use", enumerated from observed constructs across all six grammars after they're stable. This becomes the spec the transpiler targets and the surface area the SCRIP runtime must support.

---

## 📊 State

```
status:    SCT-9 partial 🔄 2026-05-17 (Opus 4.7, continuation of Sonnet 4.6).

           NEW THIS SESSION — Six sub-rungs landed; six more queued.

           SCT-9c ✅ TDump-matching C formatter (ast_print.c).  flat_length()
           + budget = ast_print_width - depth*2 inline threshold.  Default
           140 matches TLump(x, 140 - GetLevel()).  Runtime-configurable
           via ir_set_print_width() / --dump-width N.  one4all `616a372b`.

           SCT-9d ✅ n-ary flattening in snocone_parse.y.  sc_flatten_arith()
           absorbs left child when same op (left-recursive grammar mirror
           of parser_snocone.sc's right-recursive flatten_arith).  Wired
           for TT_ADD/SUB/MUL/DIV/SEQ/ALT.  TT_POW stays binary right-assoc.
           Bison regenerated.  one4all `616a372b`.

           SCT-9e ✅ qize.sc LEQ dead-function purged.  Was shadowing
           SPITBOL's built-in LEQ predicate, causing ERROR 248.  Never
           called outside qize.sc.  corpus `1b24df4`.

           SCT-9f ✅ All 60 snocone parser-fixture .ref files regenerated
           from `scrip --dump-ast`.  corpus `1b24df4`.

           Snocone fixture gate after SCT-9c/d/e/f:
             PASS=24  FAIL=2  SKIP=41   (was: PASS=6 FAIL=54 in last session)
             FAIL=2: do_simple, do_with_stmt  (TT_DO_WHILE structural; SCT-9i)
             SKIP=41: control-flow / call / switch fixtures, blocked by
                      $'(' = pattern token-slot bug under SPITBOL.  SCT-9h.

           QUEUED THIS SESSION (Lon directives):
             SCT-9g  Precedence/associativity audit vs SPITBOL Manual Ch.15.
                     Tree-children-by-shift-order is fixed; ordering of when
                     to flatten and the operator priority/assoc are NOT.
                     Output: .github/PRECEDENCE-AUDIT.md.
                     Known divergence: mixed-op `a+b-c` — C left-assoc
                     (TT_SUB (TT_ADD a b) c), .sc right-assoc grammar shape
                     (TT_ADD a (TT_SUB b c)).  Ch.15 says left-assoc for
                     pri 6 → C is correct.  .sc grammar needs fixing OR
                     documented exception.  Lon decision required.
             SCT-9h  Token-slot mangling in lower_sno.c.  Map
                     TT_INDIRECT(TT_QLIT "(") → bare name "sc_tok_LPAREN".
                     Unblocks ~40 fixtures.
             SCT-9i  do/while PST structural alignment between C and .sc.
                     Either C PST keeps TT_DO_WHILE tree (matching
                     TT_WHILE/TT_FOR), or .sc defers lowering.  Lon decision.
             SCT-9j  Wire scripts/test_parser_sc_transpile.sh (per-lang
                     fixture gate).  Now byte-diff possible after SCT-9c.
             SCT-9k  Cross-validate snobol4 parser TDump shape vs C.
                     Currently snobol4 transpiled emits (TT_STMT () (TT_LABEL)
                     (TT_EQ ...)) — different tree shape from C's STMT-attr
                     shape.  Diagnose and align.

           Prior partial work this date (Sonnet 4.6) carried forward:
           - SCT-9a (POS(0)/RPOS(0) ARBNO fix). corpus 664d633.
           - SCT-9b (AST_* → TT_* rename, 224 .ref files). corpus b64f6f1.

           Prior SCT-2 ✅ still stands.  Two surgical fixes landed:
           corpus `b64f6f1`.

           SPITBOL results after fix (with gen.sc in transpile chain):
             snobol4  ✅ produces correct AST — \tX=1\nEND → (TT_STMT...)
             snocone  ✅ produces correct AST — x=1+2; → (STMT :eq ...)
             rebus    ✅ 88/96 corpus fixtures produce AST (8 need helpers)
             icon     parse blocked — notmatch/Push_qlit from icon_helpers.sc
                      (SCT-4 prereq; icon_helpers.sc not yet in transpile chain)
             raku     ERROR 022 — missing helpers (SCT-5 prereq)
             prolog   ERROR 022 — missing helpers (SCT-6 prereq)

           Smoke gates: snobol4 6/1 (pre-existing), snocone 5/0. No regressions.

           Note: gen.sc must be included in --dump-sno chain alongside tdump.sc.
           TDump emits inline; fixture refs now use inline TT_* too (after rename).
           Remaining: wire test_parser_sc_transpile.sh; cross-validate against
           C --dump-ast; normalise TDump whitespace vs indented refs.

           Prior SCT-2 ✅ still stands (see below).
           Two surgical fixes landed:
             (1) corpus/SCRIP/semantic.sc line 31 — qtag's
                 REPLACE(t, "'", "") → REPLACE(t, "'", 'x') for
                 equal-length 2nd/3rd args.  Portable on both
                 SPITBOL and SCRIP.  Verified by 3-input test
                 program (has-apos / no-apos / empty) — 6/6 PASS.
             (2) src/lower/lower_sno.c TT_VAR case — apply
                 label_sanitize() to identifiers, not just labels.
                 SPITBOL's letter/digit-first rule (Ch.14 line 9335)
                 covers identifiers in pattern-capture position too.
                 Fixes parser_prolog.sc's pervasive `_op_name`
                 captures (was ERROR 230 at every reference site).
                 Comment on label_sanitize updated to document
                 dual use.

           Cross-parser SPITBOL sweep after fixes (sample inputs):
             snobol4    exit=0  CLEAN
             snocone    exit=0  CLEAN
             rebus      exit=0  CLEAN  🎯 (was: ERROR 171 @line 473)
             icon       exit=0  CLEAN  🎯 (was: ERROR 171 @line 473)
             raku       ERROR 022 @line 943   (was: ERROR 171 — qtag
                                               fix unmasked missing
                                               Push_fn_raku_die etc.
                                               Owned by SCT-5: delete
                                               raku_helpers.sc and
                                               re-express in 6-primitive
                                               vocabulary or migrate to
                                               C-side raku_lower.c.)
             prolog     ERROR 022 @line 1615  (was: ERROR 230 @766,27 —
                                               TT_VAR fix passed the
                                               syntax-error wall; now
                                               at same missing-helpers
                                               wall as raku.  Owned by
                                               SCT-6.)

           Smoke gates hold: snobol4 6/1 (matches SCT-1e baseline,
           1 pre-existing FAIL), snocone 5/0.  No regressions.
           SCRIP --interp still segfaults on all 6 via rt_bb_arbno →
           bb_deferred_var path (rt.c:1217 / stmt_exec.c:303).
           Owned by GOAL-PST-REBUS; this goal routes around.

           Prior SCT-1e ✅ stands: all six transpile cleanly; explicit-`?`
           fix in TT_SCAN case verified; parser_snobol4.sno accepted
           end-to-end by SPITBOL.

watermark: SCT-9g-snocone ✅ partial + n-ary arith emission fix ✅ 2026-05-17 (Opus 4.7).
           SCT-9g now per-language sub-rungs (a-f + cross).  Snocone audit
           landed as .github/PRECEDENCE-AUDIT.md.  Other five languages
           await spec documents from Lon (rebus/icon/raku/prolog) and
           require their own audit passes (snobol4 covered by SPITBOL
           manual already on disk).
           Bonus: lower_sno.c n-ary arith emission fixed (was binary-only;
           dropped c[2..n-1] silently).  End-to-end verified: SPITBOL
           value of `20-5+2`=17, `100-30+10-5`=75 match C-frontend tree
           and SPITBOL native evaluation.  Snocone fixture gate 60/7/0
           pre = 60/7/0 post (no regressions; 7 FAILs pre-existing).
           one4all HEAD 96d39c05+local-WIP.  corpus HEAD 1b24df4.

landed:
  - src/lower/lower_sno.{c,h}     (SCT-1 through SCT-2; label_sanitize on TT_VAR;
                                   SCT-9g n-ary arith TT_ADD/SUB/MUL/DIV emission)
  - src/driver/scrip.c            (--dump-sno flag, multi-file mode; --dump-width N)
  - src/driver/interp.h           (ir_set_print_width / ir_get_print_width)
  - src/ast/ast_print.c           (SCT-9c: flat_length + TLump-matching threshold)
  - src/frontend/snocone/snocone_parse.y  (SCT-9d: sc_flatten_arith for
                                           ADD/SUB/MUL/DIV/SEQ/ALT)
  - src/frontend/snocone/snocone_parse.tab.c (regenerated by bison 3.8.2)
  - Makefile                      (lower_sno.c entry + compile rule)
  - scripts/run_parser_sync_monitor.sh   (SCT-7 wrapper)
  - corpus/SCRIP/semantic.sc      (_qtag→qtag @ SCT-1d; REPLACE fix @ SCT-2)
  - corpus/SCRIP/parser_*.sc      (SCT-9a: POS(0)/RPOS(0) in all 6 Compilands)
  - corpus/SCRIP/qize.sc          (SCT-9e: dead LEQ function deleted)
  - corpus/programs/*/parser/*.ref       (SCT-9b: AST_* → TT_* rename, 224 files)
  - corpus/programs/snocone/parser-fixtures/*.ref  (SCT-9f: regenerated, 60 files)
  - .github/GOAL-PARSER-SC-TRANSPILE.md  (this file, session history;
                                          SCT-9g split into per-language sub-rungs)
  - .github/PRECEDENCE-AUDIT.md   (SCT-9g-snocone deliverable, 2026-05-17 Opus 4.7)
  - .github/PLAN.md, RULES.md, REPO-one4all.md, snobol4ever_clone.sh

next:      SCT-9g-snobol4   SPITBOL manual already on disk; can proceed.
           SCT-9g-rebus     Awaiting Rebus syntax spec doc from Lon.
           SCT-9g-icon      Awaiting Icon reference doc from Lon.
           SCT-9g-raku      Awaiting Raku operator-table doc from Lon.
           SCT-9g-prolog    Awaiting Prolog op/3 table doc from Lon (ISO
                            or SWI acceptable).
           SCT-9g-cross     After per-language audits land, cross-table sweep.
           SCT-9g-fix-sc    Apply .sc grammar fix per Lon decision (snocone
                            +-*/  right-rec → n-ary left-fold).
           SCT-9h  Token-slot mangling in lower_sno.c — unblocks 40 fixtures.
           SCT-9i  do-while PST alignment (C TT_DO_WHILE tree vs .sc lowered).
           SCT-9j  Wire scripts/test_parser_sc_transpile.sh now byte-diff works.
           SCT-9k  Snobol4 parser tree-shape alignment vs C.
           SCT-4   icon helpers elimination.
           SCT-1f  2-way sync monitor (needs SN-26-spl-bridge in x64).
           SCT-5/6 raku/prolog helper elimination.

authors:   Goal authored by Lon Cherryholmes + Opus 4.7, 2026-05-17.
           SCT-1 through SCT-1e landed same day, Opus 4.7.
           SCT-2 landed (continuation session), same day, Opus 4.7.
           SCT-9a/9b partial: Sonnet 4.6, 2026-05-17.
           SCT-9c/9d/9e/9f landed: Opus 4.7, 2026-05-17 (continuation).
           SCT-9g scoped + snocone audit + n-ary emission fix: Opus 4.7,
                  2026-05-17 (this session).
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

# Required fourth — SPITBOL oracle.  Clone to /home/claude/x64 (NOT
# /home/claude/spitbol-x64 — the latter is wrong, all scripts and the
# RULES.md "Oracles" section assume /home/claude/x64).  The repo ships
# with a prebuilt binary already at bin/sbl, so this clone IS the
# install — no build step needed for routine validation:
git clone https://TOKEN@github.com/snobol4ever/x64      /home/claude/x64
ls -la /home/claude/x64/bin/sbl     # → prebuilt SPITBOL, ready to use
/home/claude/x64/bin/sbl -b some_file.sno   # invocation form

# Optional fifth — only needed if you're touching cross-engine infra
# OR if you specifically need to rebuild SPITBOL from source.  Routine
# transpiler work does NOT need this:
git clone https://TOKEN@github.com/snobol4ever/harness  /home/claude/harness

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
echo "" | ./scrip --interp /tmp/foo.sno
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

### How-to: build SPITBOL x64 (rare — almost always unnecessary)

**The `snobol4ever/x64` repo ships with a prebuilt `sbl` binary** at `bin/sbl`.  Just clone the repo to `/home/claude/x64` and the oracle is live.  See the "How-to: clone" section above.  You only need to rebuild SPITBOL when:

- The shipped binary is broken on your platform (rare — it's an x86-64 ELF).
- You're patching the SPITBOL runtime itself (e.g. SN-26-spl-bridge for the IPC monitor wire).
- The source-of-truth files (`sbl.min`, `asm.sbl`, `lex.sbl`, `err.sbl`) have been edited.

Rebuild recipe (only if needed):

```bash
# Already cloned to /home/claude/x64 per "How-to: clone".  If not yet:
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
apt-get install -y build-essential nasm

cd /home/claude/x64
# Apply systm.c patch — clock_gettime nanoseconds → milliseconds.
# See harness/oracles/spitbol/BUILD.md for the exact PATCH heredoc.
make
# The Makefile writes the binary to bin/sbl, which is the canonical
# path every script and RULES.md "Oracles" reference expects.
```

**Important compatibility notes from harness BUILD.md:**
- SPITBOL has NO `&STNO` keyword (use `&LASTNO`)
- SPITBOL has NO `LOAD()` (EXTFUN=0)
- SPITBOL has NO `LABELCODE()`
- SPITBOL `DATA()` returns lowercase type names; CSNOBOL4 returns uppercase
- Invocation: `/home/claude/x64/bin/sbl -b program.sno` (the `-b` suppresses the banner, required for clean stdout diff)
- String literals: SPITBOL accepts both `'...'` and `"..."` but they have *different* semantics (single-quoted = literal, double-quoted = pattern with `*` deferred eval).  The transpiler emits single-quoted literals to keep the literal interpretation; double-quoted strings in source `.sc` translate to whatever the AST already encoded.

**For the monitor:** SPITBOL needs the SN-26-spl-bridge patch (landed in `x64` session #27). Without it the binary is silently no-op on the wire. The bridge activates only when `MONITOR_READY_PIPE` is set in env.

### How-to: round-trip-test a transpiled parser

```bash
# Quick smoke (don't drive SPITBOL yet, just see if SCRIP's own SNOBOL4 frontend
# accepts the output):
./scrip --dump-sno corpus/SCRIP/parser_<lang>.sc > /tmp/p.sno
echo "" | ./scrip --interp /tmp/p.sno 2>&1 | head -5

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
