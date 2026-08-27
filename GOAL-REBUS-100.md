# ⛔⭐⭐⭐ GOAL-REBUS-100 — SCRIP REBUS: NATIVE FRONTEND LADDER + SELF-HOSTED SNOCONE PARSER, ONE PLAN, ONE FILE

**RETIRED NAMES — this file REPLACES** (consolidated 2026-08-27, full text in `.github` git history before this commit): `GOAL-LANG-REBUS.md` · `GOAL-PARSER-REBUS.md` · `GOAL-PST-REBUS.md`. Any reference to one of those three names, anywhere in `.github`/SCRIP/corpus, resolves HERE. Consolidated on Lon's order ("We want one GOAL file for each language at this point"), on the exact pattern of `GOAL-{SNOBOL4,ICON,PROLOG}-100.md`; minted by ceo, `GOAL-CEO.md` CEO-30. Their laws that still bind are restated below; their rungs are dispositioned in the LEDGER near the bottom.

⛔ **Rebus is the 7th frontend and is explicitly NOT part of the six-language x86/ζ conversion campaign** that `GOAL-{SNOBOL4,ICON,PROLOG}-100.md` track (confirmed: `FINDING-2026-08-23-hq_P-six-language-baseline-pinned-pre-strip.md` line 56 — "clean (7th frontend, not in the six)"). There is no THE-THREE-ZETAS section in this file for that reason — it is an intentional omission, not a gap.

---

## ⛔⭐⭐ GOAL PIVOT ON RECORD — 2026-05-07 (operator directive) — SELF-HOSTED PARSER-REBUS TARGETS REAL-PROGRAM PARSING, NOT `tree_equal`

**Previous goal:** `parser_rebus.sc` produces trees byte-identical to `scrip --dump-ast` for every fixture; gate = `tree_equal` against the native (C) Rebus frontend.

**Current goal (operator directive, in-session substance recorded at the time):** `parser_rebus.sc` parses **full, real Rebus programs** — the three corpus programs (`syntax_exercise.reb`, `word_count.reb`, `binary_trees.reb`, now at `corpus/tests/rebus/`) and any other valid `.reb` source — and emits **simplified, stripped-down trees** that are syntactically correct (no parse abort, no "Parse Error") for every construct in the Rebus grammar. Tree fidelity to `--dump-ast` is **no longer required**; `tree_equal` is retired as this track's gate. New gate: every target program parses to completion and emits at least one tree node per top-level declaration (`scripts/test_full_rebus.sh` at pivot time — **that script no longer exists in `scripts/`, re-derive or rewrite it before trusting this gate description**, see THE INSTRUMENT).

Simplified tree model adopted at the pivot: `(STMT :subj <expr>)` for expression statements, `(STMT :subj <lhs> :repl <rhs>)` for assignment, `(FUNC fname params body)`, `(REC name fields)`, `(IF cond body [else])`, `(WHILE cond body)` — no label/goto generation in the surface tree; the old `lower_*` pass that emitted labelled STMTs is dropped in favor of a single `TDump` walk per top-level child. Full construct-by-construct notes: see `## RUNGS § RB-FULL-1` below.

---

## ⛔ FACT RULES (RULES.md is the authority; locally relevant)
- **⛔⛔⛔ NO NEW GLOBAL VARIABLES without Lon's explicit in-chat permission that session; the ask must be a big unmissable banner** (name, type, owning file, purpose, why registers/stack cannot carry it). State rides registers and the stack.
- **⛔ ZERO C BYRD BOX FUNCTIONS.** No `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω in C, ever, anywhere Rebus code touches. All Byrd boxes are x86 assembly emitted by the templates (`src/templates/`, formerly `src/templates/bb_*.cpp` — confirm current path per `CLAUDE.md`'s srcreorg note before citing). Only `icn_lazy_box`/`icn_bb_dcg` are exempt, and neither is Rebus's.
- **⛔ NO AST WALKING past the parser/lower boundary.** Originally stated as "modes 2/3/4"; modes 1 and 2 are since DELETED project-wide (see `CLAUDE.md` root) — restated for the current two media: no `tree_t*` dereference in SM/emitter code (mode-3 `--run`) or in emitted output (mode-4 `--compile`). If a gate breaks with `[NO-AST] FOO`, write fresh SM/BB lowering for FOO; do not restore AST-walking or route through a back-door that hands a `tree_t*` to mode-3/4 code.
- **⛔ NO `-O2` BUILDS. EVER.** `RT_OPT` is `-O0` for development, benchmarks, and demos alike. See `RULES.md` § NO `-O2` BUILDS for the full reasoning; it binds here exactly as it binds the other three `-100` files.

## ⭐⭐⭐ THE MODEL — REBUS: A GOAL-DIRECTED, SNOBOL4-PATTERNED LANGUAGE, TWO PARALLEL FRONTENDS

Rebus (Griswold, TR 84-9) is goal-directed like Icon but uses SNOBOL4-style pattern primitives. Key constructs:

| Construct | Meaning |
|-----------|---------|
| `function f(args) ... end` | Function definition |
| `expr ? pat` | Pattern match (→ `BB_SCAN`, shared with SNOBOL4) |
| `expr ? pat <- repl` | Pattern replace |
| `expr \| expr` | Alternation generator (→ `BB_PUMP` / `icn_bb_alt_gen`, shared with Icon) |
| `record R(f1,f2)` | Record type |
| `OUTPUT := expr` / `x := expr` | Print / assignment |
| `if cond then stmt` / `while cond do stmt` | Conditional / loop |
| `return expr` / `fail` | Function exit |

**Two independent, parallel implementations are tracked by this one file — do not conflate their status:**

1. **Native (C) frontend** — `src/frontend/rebus/rebus.y` (Bison) + `rebus.l` (Flex, auto-semicolon via `needs_semi()`, same discipline as Icon's) + `rebus_lower.c` (IR lowering). Feeds the SAME pipeline every other language uses: parse → lower → `optimizer_run` → emitter + `src/templates/` → x86-64. Shares `BB_SCAN`/`BB_PUMP` with SNOBOL4/Icon and `interp_eval` `E_IF`/`E_WHILE`/`E_RETURN` fixes with Snocone — bugs fixed there benefit Rebus for free, share via main, no branches.
2. **Self-hosted Snocone parser** — `SCRIP/bootstrap/parser_rebus.sc`, one of six sibling PARSER-* frontends (SN/SC/RB/RK/IC/PR) written **in Snocone itself**, sharing one `Compiland`/`Shift`/`Reduce`/counter runtime. This is a bootstrapping/self-hosting effort under Lon's CARVE-OUT A program ("we will carve out the front end parsers and replace them with the Snocone `parser_*.sc` (Compiland pattern) for all languages" — `PLAN.md` line 18), **not yet the shipped default** — it is a parallel implementation being proven out, sequenced by Lon SNOBOL4→Icon→Prolog→Pascal→Raku with **Rebus and Snocone placed opportunistically outside that named sequence, by technical readiness** (`CARVEOUT-A-LADDER.md` line 38).

`SCRIP/bootstrap/` (moved here from `corpus/SCRIP/` by the **s267 ruling** — that old path is stale, do not cite it) holds the shared Snocone runtime (`tree.sc` general tree type, `stack.sc` value stack, `counter.sc` n-ary fold counters, `ShiftReduce.sc` the `Shift`/`Reduce` engine, `semantic.sc` build-time pattern helpers + the `~`/`&` OPSYN bindings, `tdump.sc` tree printer, `global.sc` prelude) plus the six `parser_<lang>.sc` drivers and `run_scrip_parser.sh`. Per `SCRIP/bootstrap/README.md`: **"Today only `parser_rebus.sc` is genuinely sidecar-free (no `rebus_helpers.sc` exists); the others still need theirs."** — Rebus's self-hosted parser is, as of that README, the cleanest of the six on that one axis.

## ⛔ DEFINITION OF DONE — TWO SEPARATE TRACKS, NEITHER IS "100%" BY ITSELF

1. **Native frontend (ex-`GOAL-LANG-REBUS.md` lineage).** Rebus programs pass under mode-3 (`--run`) and mode-4 (`--compile`) [modernized from the file's original "three modes" wording — mode 1/2 are deleted project-wide, see `CLAUDE.md`]; core language features (functions, pattern match, generators, records) work; a 20+-program test suite passes (RB-11/RB-13/RB-15). **Current status: RB-1 only** — basic output/arith/var/concat, PASS=4, last independently verified **2026-08-23** via `test_smoke_rebus.sh` (`FINDING-2026-08-23-hq_P-six-language-baseline-pinned-pre-strip.md`). RB-2 through RB-15 (control flow, functions, pattern match, replace, alternation, records, builtins, `fail`/`stop`/`exit`/`next`) are **not started**; the ladder's own last touch is **2026-04-14**, predates the mode-1/2 deletion and the D-17b sibling-root path rewrite. See `## LON RULINGS WANTED` — this ladder's continued relevance under CARVE-OUT A is genuinely open.
2. **Self-hosted parser (ex-`GOAL-PARSER-REBUS.md` lineage).** `parser_rebus.sc` parses real Rebus programs to completion, no crash, no "Parse Error", per the GOAL PIVOT above. **Current status: essentially complete, one well-scoped bug open.** RB-0..RB-6 + RB-FW-1..12 landed (PASS=96/96 under the since-retired `tree_equal` gate); the pivot's own first rung, RB-FULL-1, is blocked on **`BUG-RB-FULL1-D`** (multi-line `if`/`while` bodies parse the keyword as a bare identifier) — **confirmed still open 2026-08-24** (`CARVEOUT-A-LADDER.md` line 48/74: "repro written, fix not landed... a single, well-scoped parse bug... similarly opportunistic"). This is the single actionable item on this whole file — see `## RUNGS`.
3. **PST — Pure Syntax Tree (ex-`GOAL-PST-REBUS.md` lineage).** ✅ **COMPLETE 2026-05-19.** `parser_rebus.sc` was audited against the three §⛔ PST rules and found already clean (zero violations) at Phase 2 start. Parent umbrella `GOAL-PARSER-PURE-SYNTAX-TREE.md` (still a live, separate file — not retired by this consolidation) tracks this across all six languages.

## THE INSTRUMENT (boards are RUN, never transcribed; re-derive every count fresh)
```bash
bash scripts/test_smoke_rebus.sh              # native frontend, PASS=4/4 — last verified 2026-08-23, EXISTS
bash scripts/test_smoke_unified_broker.sh     # shared broker, PASS=31 target — EXISTS
bash scripts/test_crosscheck_rebus.sh         # divergence check — EXISTS ("3-mode" in its own description is stale wording, only m3/m4 exist)
bash scripts/run_scrip_parser.sh rebus <file.reb>   # CURRENT self-hosted-parser runner — EXISTS, supports rebus as a --lang value
```
⚠ **`test_parser_rebus.sh` and `test_full_rebus.sh` (the two gate scripts named by the original PARSER-REBUS ladder and the GOAL PIVOT) NO LONGER EXIST in `scripts/` as of 2026-08-27** — verified by direct `ls`. `parser_rebus.sc` itself also moved, from `corpus/SCRIP/parser_rebus.sc` to `SCRIP/bootstrap/parser_rebus.sc` (s267 ruling). Re-derive a gate via `run_scrip_parser.sh rebus` against `corpus/tests/rebus/{syntax_exercise,word_count,binary_trees}.reb` and `corpus/tests/rebus/parser/` (144 fixtures) before trusting any PASS number in this file — none of the PASS=96/FAIL=0 or PASS=4 numbers above have been re-measured against the current `bootstrap/` location by this consolidation.

## ⛔ LAWS THAT BIND EVERY RUNG (both tracks)
- **The Rubric (`## Rubric` below, 12 items) and the Style Guidelines (`## Style Guidelines for parser_*.sc` below, 12 items) are normative for `parser_rebus.sc` and for every sibling `parser_<lang>.sc`.** Preserved in full further down this file — this is very likely the last complete copy: the file it was originally cross-referenced as canonical from, `GOAL-PARSER-SNOBOL4.md`, was itself absorbed into `GOAL-SNOBOL4-100.md` without carrying this section forward (verified: `grep -n "Style Guidelines for parser" GOAL-SNOBOL4-100.md` — zero hits). `CARVEOUT-A-LADDER.md` line 66 already cites `GOAL-PARSER-REBUS.md §1-12` as "canonical... cross-referenced by every other parser" for Pascal's future work — that citation is repointed to this file as part of this consolidation. See `## LON RULINGS WANTED`.
- **No goto, no labels — Snocone control flow only**, in the self-hosted parser (Rubric item 3).
- **No C Byrd box functions**, in the native frontend (FACT RULES above).
- **Divergence-driven rungs**: where the self-hosted parser's n-ary trees diverge from the native frontend's binary-folded trees (`a | b | c` as one 3-child node vs. nested 2-child nodes), that is intentional — full procedure in `## Divergence-driven rungs` below. Do not fold to binary "to make the gate pass."
- **Cross-pollination is bidirectional and real**: `BB_SCAN`/`BB_PUMP` fixes benefit SNOBOL4↔Icon↔Rebus; `interp_eval` `E_IF`/`E_WHILE`/`E_RETURN` fixes benefit Snocone↔Rebus; all six self-hosted `parser_*.sc` share one runtime in `SCRIP/bootstrap/` — a runtime fix belongs there first, never duplicated into one driver.

## ⛔ STANDING CONDITION — OTHER GOAL FILES RUN CONCURRENTLY, SAME REPOS
Same text as `GOAL-ICON-100.md`/`GOAL-SNOBOL4-100.md`/`GOAL-PROLOG-100.md` § STANDING CONDITION, binding verbatim here too: separate clones default · `git fetch` before trusting a watermark; pin `git rev-parse HEAD` + clean status to every number · a sibling goal's commits can move shared files (`src/templates/`, `SCRIP/bootstrap/*.sc`) silently · verify HEAD + zero tracked-modified AT MEASUREMENT, not at session start.

---

## LIVE CURSOR — 2026-08-27 seat16 (FLEET-16, THE LOOP queue row `goal-consolidate-rebus`) — CONSOLIDATION ONLY, NO ENGINEERING PROGRESS

Merged `GOAL-LANG-REBUS.md` + `GOAL-PARSER-REBUS.md` + `GOAL-PST-REBUS.md` into this file per Lon's one-goal-file-per-language order. **No Rebus code or test was touched this session.** What changed versus the retired files' own last word: verified via fresh `ls`/`grep`/`git log` that (a) `parser_rebus.sc` now lives at `SCRIP/bootstrap/parser_rebus.sc`, not `corpus/SCRIP/parser_rebus.sc` (s267 ruling, confirmed independently and via `PLAN.md` line 18); (b) `test_parser_rebus.sh`/`test_full_rebus.sh` no longer exist, `run_scrip_parser.sh rebus` is the current runner; (c) `BUG-RB-FULL1-D` is independently confirmed still open as of 2026-08-24 by `CARVEOUT-A-LADDER.md`, corroborating the 2026-05-07 session's own last word rather than superseding it; (d) the native-frontend smoke gate (RB-1, PASS=4) was independently re-verified 2026-08-23, also corroborating rather than superseding. Reference sweep performed (STEP 4 of the consolidation procedure): 5 files outside the three retired ones cited them by name (`PLAN.md`, `GOAL-PARSER-PURE-SYNTAX-TREE.md`, `CARVEOUT-A-LADDER.md`, `GOAL-PARSER-SC-TRANSPILE.md`, `PST-LR-AUDIT.md`) — all repointed to this file in the same commit.

## LIVE CURSOR — 2026-05-07 (session continuation, RB-FULL-1 partial) — 3 BUGS FIXED, ONE OPEN (`BUG-RB-FULL1-D`), NOT SUPERSEDED SINCE

The pivot's first rung. Official grammar spec cross-checked: `src/frontend/rebus/rebus.y` (704-line Bison) + `rebus.l` (lexer, auto-semicolon via `needs_semi()`); TR 84-9 (Griswold 1984) grammar appendix pages 13-15 confirmed — "Semicolon insertion is performed automatically at the ends of lines as it is in Icon."

Three bugs fixed this session (corpus `40ddfed`): **BUG-RB-FULL1-A** — `blank = nl` dropped `# comment\n` lines at top level; fixed via `blank = $' ' nl` (Gray absorbs the comment before the newline). **BUG-RB-FULL1-B** — `opt_locals` required a literal `;` but real programs newline-terminate (lexer auto-inserts `;`); fixed via `FENCE($';' | epsilon)`. **BUG-RB-FULL1-C** — `$'do'`/`$'then'`/`$'else'` had trailing required whitespace (`$'  '`) but real programs put a newline immediately after the keyword; fixed by changing the trailing requirement to Gray (`$' '`) and adding `opt_nl = (nl | epsilon)` before `stmt_body`.

**Open: `BUG-RB-FULL1-D`** — `while i < 5 do\n    i := 1\n` still parses `while` and `do` as bare `E_VAR` identifiers; `while 1 do y := 1` (same-line body) works. Only next-line bodies fail. A minimal reproduction outside the shift/reduce stack also fails — structural issue in `func_body_stmt`'s `FENCE` interaction with `opt_nl` consuming the post-`do` newline and `stmt`'s own trailing `(nl|epsilon)`. **Approach recorded for whoever picks this up:** instead of `opt_nl` inside `while_stmt`/`if_stmt`, restructure so `func_body_stmt` drives the multi-line body directly (the body can itself BE a `func_body_stmt` recursion, not a single `stmt_body` match) — or eliminate `stmt`'s trailing `nl` entirely and have `func_body_stmt` consume the newline at the end of each matched statement sequence, once.

State at this session's end: corpus `40ddfed` · SCRIP/parser branch `b9b31884` (⚠ that branch no longer exists — `git branch -a | grep parser` is empty as of 2026-08-27; work happens on `main` now, re-verify before assuming a branch checkout step). Gate: PASS=96 FAIL=0 under the old `tree_equal` gate, unchanged this session (this session touched only RB-FULL code, not the RB-0..RB-6/RB-FW-* surface).

*(Everything before 2026-05-07 — sessions #62 through the RB-FW-1..12 ladder, 2026-05-03 through 2026-05-07 — compresses to git log; see `## LEDGER` for the carried-forward lessons.)*

---

## RUNGS

### Track 1 — Self-hosted Snocone parser (ex-`GOAL-PARSER-REBUS.md`)

- [x] **RB-0a — Style Guidelines audit & cleanup.** LANDED 2026-05-04. 6 violation classes found and fixed against `## Style Guidelines` below (White/Gray strewn through productions, missing `$'kw'` wrappers, leading-underscore identifiers, blank-line dividers, brace-block single statements, `nl_one` wrapping). One item (G3, `shift()`/`reduce()` vs infix `~`/`&`) deliberately deferred — the Snocone runtime did not parse infix `~`/`&` at the time; re-check whether it does now before re-opening.
- [x] **RB-0 — atom.** LANDED. PASS=3 (`atom_id`, `atom_int`, `atom_str`). Full worked example preserved verbatim in `## Worked atom example` below — read it before touching this parser again, it is the shape every rung follows.
- [x] **RB-1 — assignment `x := expr`.** LANDED. PASS=8.
- [x] **RB-2 — control flow `if/then`, `while/do`.** LANDED (under the old gate). Label generation deferred to a post-parse walk, mirroring how `rebus_lower.c` separates parse from lower. PASS=12.
- [x] **RB-3 — function decls + call sites.** LANDED. Two independent `nPush()/nPop()` counter scopes (params list, body-stmt list). PASS=18.
- [x] **RB-4 — pattern match `expr ? pat`.** LANDED. `pat_expr` aliases `expr` per `rebus.y` line 678 — no syntactic distinction, the `?` operator supplies context. PASS=25.
- [x] **RB-5 — alternation `a | b | c`, n-ary.** LANDED, divergence-pending on alt-bearing fixtures (existing native frontend folds binary; self-hosted parser produces flat n-ary — intentional, see Divergence-driven rungs). PASS=25 baseline + divergence-pending; final PASS=32 once/if the native frontend's `rebus_lower.c` flattens to match.
- [x] **RB-6 — record decls.** LANDED. Same n-ary fold as RB-3's params, `+1` for the leading record name. PASS=38 (or PASS=N+divergence-pending).
- [x] **RB-FW-1..12 — full-program hardening rungs beyond the original 38-fixture ladder.** LANDED across sessions 2026-05-04 through 2026-05-06/07 (comma/newline edge cases, compound statements, unary operators, multi-arg subscripts, augmented-assign-in-subscript, and more). PASS climbed 38→48→52→80→82→83→90→91→94→96, FAIL=0 throughout. Full session-by-session detail (bugs found, fixtures added) compresses to git log — see `## LEDGER` for the lessons worth keeping.
- [~] **RB-FULL-1 — parse real programs cleanly (the pivot's own rung). OPEN.** Simplify the driver (drop the labelled-lowering pass, emit raw `TDump` per top-level child), then run the three `corpus/tests/rebus/*.reb` programs and fix whatever gaps remain. Three sub-bugs fixed (A/B/C, see LIVE CURSOR above); **`BUG-RB-FULL1-D` (multi-line `if`/`while` bodies) is the one blocker, confirmed still open 2026-08-24.** This is the single actionable item in this file.

### Track 2 — Native (C) frontend (ex-`GOAL-LANG-REBUS.md`)

⚠ **This entire ladder's numbers predate the mode-1/2 deletion and the D-17b sibling-root rewrite (last touched 2026-04-14) and its continued priority under CARVE-OUT A is an open question — see `## LON RULINGS WANTED`.** Preserved here because it is a real, never-formally-retired ladder, not because its framing is known-current.

**Phase 1 — IR-run (interpreted):**
- [x] **RB-1** — output/arith/var/concat. PASS=4. Re-verified live 2026-08-23 (`test_smoke_rebus.sh`).
- [ ] **RB-2** — control flow (`if/then/else`, `while/do`). Verify Snocone's control-flow fixes reach Rebus via shared `interp_eval` `E_IF`/`E_WHILE`.
- [ ] **RB-3** — functions (`function f(args) ... return val ... end`), recursive-Fibonacci gate.
- [ ] **RB-4** — pattern match `expr ? pattern` → `BB_SCAN` (ARB, SPAN, BREAK, literal fixtures).
- [ ] **RB-5** — pattern replace `expr ? pat <- repl`.
- [ ] **RB-6** — alternation generator `expr | expr` → `icn_bb_alt_gen` (shared with Icon).
- [ ] **RB-7** — records: `record R(f1,f2)` / construction / field access.
- [ ] **RB-8** — string builtins (`size`, `type`, `image`) mapped to SNOBOL4's `SIZE`/`DATATYPE`/`IMAGE`.
- [ ] **RB-9** — `fail`/`stop`/`exit`/`next`.
- [ ] **RB-10** — `scripts/test_rebus_ir_suite.sh` running RB-2..RB-9.
- [ ] **RB-11** — 20-program corpus (fibonacci, palindrome, wordcount, pattern demos, record demos; `.ref` derived from equivalent SNOBOL4/Icon programs under SPITBOL/Unicon).

**Phase 2 — SM-run / Phase 3 — codegen (x86):**
- [ ] **RB-12/RB-14** — RB-1..RB-9 under mode-3/mode-4 [modernized from the original "SM-run"/"JIT-run" phase names, which describe modes since deleted].
- [ ] **RB-13/RB-15** — full 20-program corpus under mode-3/mode-4.

---

## ⛔ FALSIFIED / DO-NOT-REDO
- **Goto-driven, line-at-a-time state machine for `parser_rebus.sc`** — session #62 (Claude Sonnet 4.7, 2026-05-03) achieved PASS=38 tree-equivalence this way, but it violates the Rubric end-to-end (items 1, 2, 3, 5, 6, 7 all fail: no `Compiland`/`shift`/`reduce`/`nPush` spine, per-line matching, goto/labels, hand-rolled `Tree()` calls from procedural code). The PASS gate flagged tree equivalence but not architectural shape — that is a hole in the *old* gate, not a clearance to repeat the pattern. All rungs were reopened and rewritten as genuine Snocone patterns; the rewrite is what `## RUNGS Track 1` documents.
- **`tree_equal` against the native frontend as the self-hosted parser's gate** — not wrong exactly, but RETIRED by the 2026-05-07 operator directive (see GOAL PIVOT banner). Do not resurrect it as a gate without a fresh ruling; the current gate is "parses real programs, no crash, no Parse Error."

## ⛔ LON RULINGS WANTED
1. **Does the native-frontend Track 2 ladder (RB-2..RB-15) still matter, or has CARVE-OUT A superseded the need for a second, hand-written-in-C implementation path?** Nobody has touched it since 2026-04-14; CARVE-OUT A's stated direction is to *replace* native C frontends with the self-hosted `parser_*.sc` versions. If Track 2 is superseded, say so and this file drops to tracking Track 1 + PST only.
2. **Should this file's `## Rubric`/`## Style Guidelines` sections become the formally-designated canonical copy for all six `parser_*.sc` drivers**, given `GOAL-PARSER-SNOBOL4.md` (the file previously cross-referenced as canonical) was absorbed into `GOAL-SNOBOL4-100.md` without carrying that text forward, and this file's copy is very likely the last complete one? `CARVEOUT-A-LADDER.md` already cites it as canonical for Pascal's future work by pointing here.

## LEDGER — absorbed files + retired ladders (full text in git)

**RETIRED NAMES:** `GOAL-LANG-REBUS.md` · `GOAL-PARSER-REBUS.md` · `GOAL-PST-REBUS.md`. Every reference to any of the three, anywhere in `.github`/SCRIP/corpus, resolves HERE. Full text in `.github` git history immediately before this commit.

- **`GOAL-PST-REBUS.md`** (27 lines) — ✅ COMPLETE 2026-05-19. `parser_rebus.sc` (then at `corpus/SCRIP/`) was "already clean" at Phase 2 start — zero of the six §⛔ violation classes present. Closed step trail: RB-SC-1 (verify), RB-SC-2 (stamp), RB-SC-3 (smoke 4/0); Phase 1 C's six violations (`stmt_list_ne`, `unless`, `case TT_IF`, `augop`, `postfix-call`, `RDecl`/`RProgram`/`RCase` declarations) closed earlier still. Heads at closure: SCRIP `2a9aa511` · corpus `d1c08ff`.
- **`GOAL-LANG-REBUS.md`** (245 lines) — see `## RUNGS Track 2` above; last live edit 2026-04-14, SCRIP HEAD `43dc03da`. Carried a `--monitor` usage note (in-process IR/SM/JIT sync comparator, one line per language) that is generic project infrastructure, not Rebus-specific — see the equivalent note in whichever ARCH file now owns `--monitor` documentation project-wide, not reproduced here.
- **`GOAL-PARSER-REBUS.md`** (2852 lines) — see `## RUNGS Track 1`, the GOAL PIVOT banner, and the two LIVE CURSOR entries above for everything still load-bearing; Rubric/Style Guidelines/Worked Example carried forward in full below. **Lessons carried forward from the retired chronological session log** (2026-05-03 through 2026-05-07; full narrative, session-by-session, in git history before this commit):
  - Multi-statement-per-line is fragile in Snocone: `else if (...) { OUTPUT = "DBG"; emit_match(...); }` works, but a space between a function name and `(` in an unbraced single-statement body can silently fail to invoke the call — always use no-space `func(args)` or brace the body.
  - Bare tag globals (`RB_FOO = 'RB_FOO'`, read via `semantic.sc`'s `_qtag` auto-wrap) fail silently to an empty tag if the global declaration is forgotten — "node has empty tag" during debugging means check the tag-constants block first.
  - The two-phase pattern-match model from the SPITBOL manual is the right mental model for every `parser_*.sc`: Pass 1 (cursor movement, built-in primitives only, no user code) vs. Pass 2 (post-success linear `.`-actions: `Shift`/`Reduce`/counters, in match-path order). The Rubric's ban on `*helper(...)`/`Push(Tree(...))` from inside patterns is exactly this boundary, made enforceable.
  - `while (i = LT(i, n) i + 1)` **pre-increments** `i` before the loop body — initialize one less than the desired start, or use the explicit `while (GE(i,0) LT(i,n+1)) { body; i = i+1; }` form. Bit multiple sessions independently (recorded twice in the original log).
  - `stmt_body` and `stmt_inline` ("any single statement" in two different grammar contexts) must be kept in sync — a new statement form added to one and not the other fails silently in whichever context was missed.
  - All local variables used inside a recursive Snocone function must be in its parameter signature — globals used as scratch get clobbered across recursive calls.

## Architecture reference (the living contract)

**Native frontend pipeline:**
```
.reb → rebus_compile() → CODE_t*
    --run (mode-3)     → BB-based execution (Byrd boxes, x86 in-process)
    --compile (mode-4) → emitted x86-64 asm, linked against out/libscrip_rt.so
Pattern match: expr ? pat   → BB_SCAN (shared with SNOBOL4)
Generators:    expr | expr  → E_ALT_GEN → BB_PUMP (shared with Icon)
```
[The original diagram named modes 1/2/3/4 including `polyglot_execute()`/`sm_lower()`/`sm_codegen()` — those intermediate mode names are retired along with modes 1/2; re-derive the current dispatch path from `src/driver/` before citing specifics beyond the two-medium split above.]

**Self-hosted parser pipeline (via `scrip --parser-crosscheck` / `run_scrip_parser.sh`):**
```
scrip --parser-crosscheck parser_rebus.sc tiny.reb
```
`parser_rebus.sc` (which loads the shared `SCRIP/bootstrap/*.sc` runtime) produces tree t2 via `Compiland`; the native frontend produces t1. Compared/executed in memory — no subprocesses, no temp files. `Compiland` spine (identical across all six self-hosted parsers): `Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();`

**Native-frontend tree shapes (oracle, from `--dump-ast`):**

| Construct | Oracle `--dump-ast` (single-line form) |
|-----------|---------------------------------------|
| `function f() ... end` | `(STMT :subj (E_FNC DEFINE (E_QLIT "F()")))` then per-body STMTs, then `:go RETURN` `:lbl rb_N` |
| `record R(f1, f2)` | `(STMT :subj (E_FNC DATA (E_QLIT "R(F1,F2)")))` |
| `x` (bare atom) | `(STMT :subj (E_VAR X))` |
| `42` | `(STMT :subj (E_ILIT 42))` |
| `"hi"` | `(STMT :subj (E_QLIT "hi"))` |
| `x := y` | `(STMT :eq :subj (E_VAR X) :repl (E_VAR Y))` |
| `if c then s` | `(STMT :subj <c> :goS L_then :goF L_else)` then s, then merge label |
| `while c do s` | label, then `(STMT :subj <c> :goS body :goF after)` then s, loop back |
| `f()` | `(STMT :subj (E_FNC F))` |
| `x ? y` | `(STMT :subj (E_VAR X) :pat (E_VAR Y))` |
| `a \| b \| c` | left-assoc `(E_ALT (E_ALT a b) c)` per `rebus.y` `alt_expr` — **the self-hosted parser produces flat n-ary `(E_ALT a b c)` instead; this is the tracked divergence, see below** |

(These 11 shapes are covered by the 144 fixtures at `corpus/tests/rebus/parser/` — old docs cite `corpus/programs/rebus/parser/`, 38 fixtures; both the path and the count have moved since, re-`ls` before trusting either number.)

**Key files:**

| File | Role |
|------|------|
| `src/frontend/rebus/rebus.y` | Bison grammar (native frontend) |
| `src/frontend/rebus/rebus.l` | Flex lexer, auto-semicolon (native frontend) |
| `src/frontend/rebus/rebus_lower.c` | IR lowering — main native-frontend work site |
| `SCRIP/bootstrap/parser_rebus.sc` | Self-hosted Snocone driver (sidecar-free, see THE MODEL) |
| `SCRIP/bootstrap/{tree,stack,counter,ShiftReduce,semantic,tdump,global}.sc` | Shared self-hosted runtime, all six languages |
| `SCRIP/scripts/run_scrip_parser.sh` | Current self-hosted-parser runner (`--lang rebus`) |
| `corpus/tests/rebus/{syntax_exercise,word_count,binary_trees}.reb` | The GOAL PIVOT's three real-program targets |
| `corpus/tests/rebus/parser/` | 144 self-hosted-parser fixtures |

## Rubric — what makes this a pattern parser

Before writing any `.sc` code, confirm every item below. If any answer is "no", stop and rework.

1. **One root pattern, matched once against the entire source.** The driver reads stdin into a single string `Src` (concatenating all lines with newlines), then runs `Src ? Compiland`. **Exactly one `?` operator appears in the driver, ever.** Sub-patterns (`Command`, `expr`, `atom`, etc.) are referenced from inside `Compiland` via `*Sub`; they are never matched separately by the driver. There is no per-line slurp loop matching individual lines against patterns. After the single match, the driver walks the tree on the stack to call `TDump` per top-level child — that is emission, not parsing, and is allowed.

2. **`Compiland` has the canonical beauty.sc spine.** Literally:
   ```
   Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();
   ```
   `Command` is one big alternation of sub-patterns, one per recognized construct. **One `Compiland`, period.** No `Compiland_v1` / `Compiland_v2`. No alternative spines. No per-rung Compilands.

3. **No goto, no labels — Snocone control flow only.** Snocone has `if`/`else`, `while`, structured patterns, and pattern alternation. That is enough for everything in this parser. **Zero goto. Zero labels.** This applies to the driver's stdin slurp too: write it as a `while ((Line = INPUT)) { Src = Src Line nl; }`, not as `read_loop:` / `goto read_loop`. The only legacy goto-style code in any current `parser_*.sc` is grandfathered for unrelated reasons (FW-3 deferred-call workaround); new code does not copy it.

4. **Tree construction uses the OPSYN binary operators `~` and `&`.** `semantic.sc` defines:
   ```
   OPSYN('~', 'shift', 2);
   OPSYN('&', 'reduce', 2);
   ```
   Write `*Integer ~ "'E_ILIT'"` not `shift(*Integer, "'E_ILIT'")`. Write `"'E_ALT'" & 'nTop()'` not `reduce("'E_ALT'", 'nTop()')`. The infix forms are the canonical surface; the function-call forms are the implementation. **Use the operators.** Never call `Push(Tree(...))` from a pattern escape — that is the procedural shortcut the OPSYN forms exist to replace.

5. **No user-defined functions called from inside parsing patterns.** A pattern match is pure pattern composition. The only functions that may be invoked from inside `Compiland` or any of its sub-patterns are the OPSYN-bound parsing operators and their counter companions:
   - `Shift` / `Reduce` (called by the `~` and `&` operators)
   - `PushCounter` / `IncCounter` / `DecCounter` / `PopCounter` (called by `nPush()` / `nInc()` / `nDec()` / `nPop()`)
   - `TopCounter` (read inside reduce-target expressions)

   That is the entire allowed surface for *user code* called from inside patterns. **No** `*assign('_x', ...)`, **no** `*push_qlit_from_strbody()`, **no** `*next_label()`, **no** `*format_arglist()` — none of those from inside a pattern.

   Snocone's built-in pattern primitives (LEN, SPAN, BREAK, ANY, NOTANY, FENCE, ARBNO, POS, RPOS, TAB, RTAB, REM, etc.) remain fully available — they are part of the pattern grammar, not user functions. So is the structural-test family (IDENT, DIFFER, GT, LT, etc.) when used inside patterns as `*IDENT(x, y)` guards. The line is: built-ins that ship with Snocone = OK; functions defined by the parser author = NOT OK from inside a pattern.

   If you need to transform a captured value before it lands on the stack, structure the grammar so that the pattern alone produces the desired match-span (see "String body capture idiom" below); if you need post-parse transformation, do it in a function that walks the tree AFTER `Src ? Compiland` returns.

   **String body capture idiom.** To shift `(E_QLIT "hi")` from source `"hi"`, the body must reach Shift without the surrounding quotes. Achieve this structurally — the opening and closing quotes are matched by sibling sub-patterns; only the body goes through `~`:
   ```snocone
   DQ_open = '"';   DQ_close = '"';   DQ_body = BREAK('"');
   SQ_open = "'";   SQ_close = "'";   SQ_body = BREAK("'");
   qlit_dq = DQ_open *DQ_body ~ "'E_QLIT'" DQ_close;
   qlit_sq = SQ_open *SQ_body ~ "'E_QLIT'" SQ_close;
   String  = (*qlit_dq | *qlit_sq);
   ```
   Match for `"hi"`: `DQ_open` consumes `"`; `*DQ_body` matches `hi` (BREAK stops at the closing quote); `~` shifts `tree('E_QLIT', 'hi')`; `DQ_close` consumes the closing `"`. Pure pattern composition. Same idiom applies to any "matched span minus delimiters" capture. **No function calls.**

6. **No per-line state machine.** No `_rb_state = 0/1` toggle. No per-construct `_rb_*_kind` / `_rb_*_txt` global slots feeding hand-built `Tree(...)` calls in helper functions. Per-construct binding happens via the `~` operator's right operand (the tag) and the `&` operator's right operand (the child count, usually `nTop()`).

7. **All trees are n-ary. No left, no right.** Every fold of a variable-length list — alternation, concatenation, statement sequences, argument lists, parameter lists, body statements — uses the n-ary spine:
   ```
   X = nPush() *XList ("'X'" & 'nTop()') nPop();
   XList = nInc() *Item FENCE(<sep> *XList | epsilon);
   ```
   `a | b | c` becomes a flat `(E_ALT a b c)` with three children, NOT `(E_ALT (E_ALT a b) c)`. `f(a, b, c)` becomes a flat `(E_FNC f a b c)` with four children, NOT a nested chain. Hard-coded child counts in `&` (e.g. `"'E_ASSIGN'" & 2`) are reserved for genuinely fixed-arity productions like `lhs := rhs` — and even then, prefer the n-ary spine if the construction could plausibly grow. **The existing Rebus frontend produces binary E_ALT; that is a divergence to surface, not a constraint to conform to.** See `## Divergence-driven rungs` below.

8. **Counter helpers (`nPush`/`nInc`/`nTop`/`nPop`) appear at every n-ary fold site.** This is how the parser knows how many items to fold. The pair `nPush() ... reduce(t, 'nTop()') nPop()` opens a counter scope; `nInc()` inside the iteration body bumps it each pass.

9. **Sub-pattern names mirror `rebus.y`.** Use `function_decl`, `record_decl`, `pat_expr`, `expr`, `alt_expr`, etc. — the non-terminal names from `src/frontend/rebus/rebus.y`. Where a name conflicts with Snocone reserved syntax, suffix with `_pat`. Do not invent names like `MatchLine` / `BodyAltLine` / `IfLine` — those are line-fragments, not grammar non-terminals.

10. **One alternation in `Command` covers all top-level constructs.** In Rebus that is `function_decl | record_decl`. Statement-level forms (assign, match, alt, if, while, call, atom) live under a `stmt`-rooted sub-tree fired by `function_decl`'s body, not as peers of `function_decl`.

A grep that should produce zero hits in the rewritten parser:
```
grep -nE 'goto |^[a-z_]+:|_rb_state|_rb_atom_kind|emit_[a-z]|shift\(|reduce\(|Push\(Tree|\*[a-z_]+\(' parser_rebus.sc
```
The new `\*[a-z_]+\(` term catches function-call-from-pattern escapes (`*assign(...)`, `*push_*()`, etc.). Pattern references like `*Gray` or `*Compiland` use no parens and do not match.

A grep that should match exactly:
```
grep -c 'Src ? Compiland' parser_rebus.sc       # → 1
grep -c '?' parser_rebus.sc | <discounting ?'s in patterns>  # → 1 in driver
grep -c '^Compiland '   parser_rebus.sc         # → 1 (the definition)
grep -c '\*Compiland'   parser_rebus.sc         # → 0 (Compiland is the root, never referenced)
grep -c 'Compiland'     parser_rebus.sc         # → exactly 2 (def + driver use)
```

## Style Guidelines for parser_*.sc — canonical, derived from beauty.sno / beauty.sc

These guidelines are normative for every `parser_<lang>.sc` (PARSER-RB, PARSER-SC, PARSER-SN, PARSER-IC, PARSER-PL, PARSER-RK). They derive directly from `corpus/programs/snobol4/demo/beauty/beauty.sno` and its Snocone port `corpus/programs/snocone/demo/beauty/beauty.sc` — the reference pattern parsers in the canon. Read both end-to-end before writing any parser. Where this section and a per-language goal file disagree, this section wins.

### 1. White / Gray attached at token definitions, not at use sites

`White` matches a contiguous run of horizontal whitespace (space, tab, and per-language continuation conventions). `Gray` is `*White | epsilon` — optional whitespace. Both are defined ONCE, near the top of the parser file, beside the lex-token definitions:

```snocone
White = SPAN(' ' tab) FENCE(nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon) | epsilon)
      | nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon);
Gray  = *White | epsilon;
```

(Per-language continuation handling — beauty.sno's `+`/`.` glyphs in column 1 — adapts per the host language; the Rebus continuation rule is just `White = SPAN(' ' tab)` since the language has no continuation syntax.)

**White / Gray are absorbed into the `$'kw'` and atomic-token definitions, never written into grammar productions.** Look at `Expr0..Expr17` in beauty.sc lines 64-100: there is no `*Gray` or `*White` in the operator-tier ladder. All whitespace is already inside the `$'op'` wrappers.

### 2. `$'kw'` for operator and keyword tokens; identifier names for word tokens

Operator and punctuation tokens get `$'op'` syntactic wrappers that bake in the surrounding whitespace policy:

```snocone
// Binary operators — symmetric whitespace.
$'='  = *White '='  *White;   $'?'  = *White '?'  *White;
$'|'  = *White '|'  *White;   $'+'  = *White '+'  *White;
$'**' = *White '**' *White;   $'~'  = *White '~'  *White;
// Comma is gray-flanked (optional whitespace each side).
$','  = *Gray  ','  *Gray;
// Brackets are asymmetric: open paren absorbs trailing gray,
// close paren absorbs leading gray.
$'('  = '('  *Gray;   $')'  = *Gray ')';
$'['  = '['  *Gray;   $']'  = *Gray ']';
```

Snocone-reserved word tokens (`if`, `then`, `else`, `while`, `do`, `function`, `record`, `end`) also get `$'kw'` wrappers — required whitespace flanks where the language demands word boundaries:

```snocone
$'if'       = *Gray 'if'       *White;   // 'if' must be followed by whitespace
$'then'     = *White 'then'    *White;
$'function' = 'function' *White;          // at column-anchor positions
$'end'      = *White 'end'     *Gray;
```

Word tokens that are NOT Snocone-reserved get plain identifier names with the optional-/required-space prefix folded in. Beauty.sno's `SGoto`/`FGoto` (lines 192-193) is the model:

```snocone
S = $' ' 'S';     // optional leading whitespace, literal 'S'
F = $' ' 'F';
SGoto = ('S' | 's') . *assign(.sf, *'S');   // case-tolerant variant
```

**Convention:** `$' '` (single space) is optional whitespace; `$'  '` (two spaces) is required whitespace. This carries directly from beauty.sno.

**The grammar productions read clean.** No `*White` / `*Gray` strewn through `Expr0..Expr17` or `Stmt` or `Compiland`. Whitespace lives in the token wrappers, period.

### 3. AST decoration — beauty.sno's two equivalent forms

Beauty.sno presents two surface forms for stack-machine annotation, related by OPSYN:

**Form A — explicit dot-conditional + function call:**
```
primitive . tx                                      // capture into global tx
epsilon . func(literal, tx)                          // perform action with tx
```

**Form B — function-call shorthand (after OPSYN):**
```
primitive . tx Func(literal, "tx")                  // single helper call
```

**Form C — infix operator shorthand (after OPSYN ~ / &):**
```
*primitive ~ 'TAG'                                  // shift  (= Shift(*primitive, 'TAG'))
("'TAG'" & 2)                                       // reduce 2 children into TAG
("'TAG'" & 'nTop()')                                // reduce nTop() children into TAG
("'TAG'" & '*(GT(nTop(), 1) nTop())')               // reduce only if >1 (else passthrough)
```

The OPSYN bindings live in `semantic.sc`:
```
OPSYN('~', 'shift',  2);     // *p ~ 'TAG'      ≡  shift(*p, 'TAG')
OPSYN('&', 'reduce', 2);     // ("'TAG'" & N)   ≡  reduce("'TAG'", N)
```

**Use the infix operators (Form C) wherever supported.** beauty.sno uses them throughout `Expr14..Expr17`, `Command`, `Goto`. beauty.sc also uses `~` and `&` inline (lines 80-100, 132). When the host's Snocone runtime does not yet parse infix `~`/`&`, fall back to the function-call forms `shift(...)` / `reduce(...)` — both compile to the same `Shift`/`Reduce` engine calls.

### 4. n-ary tree counters via `nPush()` / `nInc()` / `nTop()` / `nPop()`

For variable-length list folds (alternation, concatenation, parameter/argument lists, statement sequences), use the n-ary spine. beauty.sno line 119 / beauty.sc line 61:

```snocone
ExprList = nPush() *XList ("'ExprList'" & '*(GT(nTop(), 1) nTop())') nPop();
XList    = nInc()  (*Expr | epsilon ~ '') FENCE($',' *XList | epsilon);
```

`nPush()` opens a counter scope; `nInc()` bumps it for each list element; `nTop()` reads the count at reduce time; `nPop()` closes the scope. These are pattern fragments returned by build-time helpers in `semantic.sc`:

```
function nPush() { nPush = epsilon . *PushCounter(); return; }
function nInc()  { nInc  = epsilon . *IncCounter();  return; }
function nTop()  { nTop  = TopCounter();             return; }
function nPop()  { nPop  = epsilon . *PopCounter();  return; }
```

Decorate the AST construction with these counter operations; they are the *only* match-time function-effects allowed inside a parsing pattern besides Shift/Reduce.

### 5. AST tree-tag names — match the IR `EXPR_t` enum

Tree tags emitted by `~` and `&` MUST match the language's IR kind names — the `E_*` strings from `src/ir/ir.h`'s `EXPR_t` / `STMT_kind_t`. Examples per language:

| Construct | Tag string |
|-----------|------------|
| Variable reference | `E_VAR` |
| Integer literal | `E_ILIT` |
| String literal | `E_QLIT` |
| Function call | `E_FNC` |
| Binary `+` | `E_ADD` |
| Binary `*` | `E_MUL` |
| Pattern alternation (n-ary) | `E_ALT` |
| Assignment | `E_ASSIGN` |
| Pattern match | `E_SCAN` |

For language-specific surface-syntax constructs that are lowered to canonical IR by a post-parse pass (see Rubric item 5 above), use the language-prefixed tag form: `RB_FUNC_DECL`, `RB_REC_DECL`, `IC_PROC`, `PL_CLAUSE`, etc. These tags live ONLY in the surface parse tree; post-parse lowering rewrites them into the canonical `E_*` / `STMT_*` shape that `tree_equal()` compares against.

### 6. Identifier naming — case discipline

| Kind | Convention | Examples |
|------|------------|----------|
| Pattern non-terminal (grammar production) | UpperCamelCase or matching BNF | `Expr`, `Stmt`, `Command`, `Compiland`, `function_decl`, `record_decl` |
| Token classifier | UpperCamelCase | `Id`, `Integer`, `Real`, `String`, `Function`, `BuiltinVar`, `ProtKwd` |
| Helper function (build-time, returns pattern fragment) | UpperCamelCase | `Shift`, `Reduce`, `RB_push_qlit` |
| Helper function (match-time effect) | snake_case or lowerCamel | `assign`, `match`, `rb_push_qlit`, `nInc` |
| Local pattern variable (intermediate) | lowerCamel or snake_case | `tx`, `sf`, `_kw_rest` (with caveat below) |
| Tag string constant | UpperCamelCase / `E_*` IR form | `E_VAR`, `RB_FUNC_DECL`, `Parse` |

**No symbols starting with underscore in source code.** Underscore prefixes are reserved for compiler-generated identifiers (the IR lowering pipeline emits `_g42`, `_lbl_3`, etc.). Existing `parser_*.sc` files that use names like `_sc_lbl_n` or `_kw_rest` are grandfathered but new code does not introduce them — replace with `scLblN` or `kwRest`.

**Variables start with a lowercase letter, snake_case for compounds.** Functions usually start with an uppercase letter, then snake_case afterwards. This matches beauty.sno conventions.

### 7. Names track the official language specification

Non-terminal pattern names MUST mirror the host language's official BNF. For Rebus that is `src/frontend/rebus/rebus.y` (Bison grammar based on Griswold TR 84-9): `function_decl`, `record_decl`, `expr_stmt`, `if_stmt`, `while_stmt`, `case_stmt`, `match_stmt`, `primary`, `postfix_expr`, `expr`, `pat_expr`, `cat_expr`, `alt_expr`, `assign_expr`.

For Icon: per `src/frontend/icon/icon.y` and the Icon Programming Language reference. For Prolog: per ISO/IEC 13211-1. Etc.

**Sources of truth, in order:**
1. The frontend's `.l` / lex header (token enum) and `.y` / parse module.
2. The lowering module's IR-tag enum and dumper.
3. The official BNF / language specification — only as a tiebreaker when (1) and (2) leave a name unspecified.

Invented names are reserved for the cross-PARSER spine (`Compiland`, `Command`, helpers like `Push`/`Pop`/`Top`, `tree`/`Tree`/`TDump`/`stack`). Per-language non-terminals are not invented.

### 8. Code layout — horizontal-first, 120 columns, no blank lines

| Rule | Style |
|------|-------|
| Maximum line length | 120 characters |
| Single-statement bodies | inline with semicolon: `if (x) action;` not `if (x) { action; }` |
| Multi-statement bodies | brace block `{ ... }` |
| Block separation | `//===` 120-char major divider, `//---` 120-char minor divider — NEVER a blank line |
| Multi-line wrapping | constant 2-space nested indentation |
| Vertical alignment | balance parentheses and binary operators vertically |
| Use of horizontal space | maximize — pack tokens onto one line where readable |

Single-statement `if`/`while`/`for` bodies always use the inline semicolon form:

```snocone
// Correct:
if (DIFFER(line)) line = line ' ';
while (i = LT(i, n) i + 1) sum = sum + a[i];

// Incorrect:
if (DIFFER(line)) {
    line = line ' ';
}
```

When a long pattern definition exceeds 120 columns, wrap with balanced parentheses and 2-space nested indent, lining up alternation bars with the opening paren:

```snocone
Expr14 = '@' *Expr14 ("'@'" & 1)
       | '~' *Expr14 ("'~'" & 1)
       | '?' *Expr14 ("'?'" & 1)
       | *ProtKwd ~ 'ProtKwd'
       | *UnprotKwd ~ 'UnprotKwd'
       | *Expr15;
```

Section dividers replace blank lines:

```snocone
//===================================================================================================================
//  Atomic tokens
//===================================================================================================================

Integer = SPAN(digits);
Id      = ANY(&UCASE &LCASE) FENCE(SPAN('.' digits &UCASE '_' &LCASE) | epsilon);

//-------------------------------------------------------------------------------------------------------------------
//  Operator wrappers
//-------------------------------------------------------------------------------------------------------------------

$'='  = *White '='  *White;
$'|'  = *White '|'  *White;
```

The exact divider widths are 120 characters of `=` (major) or `-` (minor), terminated by a comment line with the section title.

### 9. No goto, no labels

Snocone has structured `if`/`else`, `while`, `for`, structured pattern alternation, and pattern `FENCE`. That is enough for any `parser_*.sc`. **Zero `goto`. Zero labels.**

The driver reads stdin into a single `Src` string, runs ONE `Src ? Compiland`, then walks the resulting tree. No `read_loop:`/`mainErr:`/`mainEnd:` labels. beauty.sc has them only because it is a *mechanical* port from beauty.sno's SNOBOL4 goto-flow — that is grandfathered, not a model to copy.

### 10. Driver shape — stdin slurp, one match, walk

```snocone
&FULLSCAN  = 1;

InitCounter();
InitStack();

src = '';
while (line = INPUT) src = src line nl;

if (src ? Compiland) {
    parseRoot = Pop();
    if (DIFFER(parseRoot)) {
        i = 0;
        while (i = LT(i, n(parseRoot)) i + 1) lower(c(parseRoot)[i]);
    }
} else {
    OUTPUT = 'Parse Error';
}
```

`lower()` is the post-parse tree-walk that emits canonical STMT TDump lines. Match-time helpers it calls (`Tree`, `TDump`, etc.) live in `tree.sc`/`tdump.sc` and are not parsing functions.

### 11. The `nl` token — used directly, not wrapped

Snocone exposes `nl` as a single-character pattern primitive. Use it directly in patterns; do NOT define `nl_one = ANY(nl)` — that wrapping both costs a function-call indirection AND can introduce backtracking hazards under `ARBNO`.

```snocone
// Correct (beauty.sc style):
Comment = '*' BREAK(nl);
Command = nInc() FENCE(*Stmt reduce('Stmt', 7) (nl | ';'));

// Incorrect:
nl_one = ANY(nl);
stmt_line = ... *nl_one;
```

### 12. Self-check greps

A grep that should produce zero hits in any compliant `parser_*.sc`:

```
grep -nE 'goto |^[a-z_]+:|^_[A-Za-z]'      parser_*.sc   # → 0 (no goto/label/leading-underscore source ids)
grep -cE 'shift\(|reduce\('                 parser_*.sc   # → 0 IF runtime supports infix ~/&; otherwise OK
grep -cE 'Push\(Tree'                       parser_*.sc   # → 0 (no escape-hatch tree pushes from patterns)
grep -nE '^[A-Za-z_]+ *= *.*\*White'        parser_*.sc   # → only $'op' / token defs / White itself
grep -c '^(if|while)[^(]' -r parser_*.sc   # → 0 (always Snocone keyword usage with parens)
```

A grep that should match exactly:

```
grep -c 'src ? Compiland'  parser_*.sc      # → 1 (the ONE pattern match in driver)
grep -c '^Compiland '      parser_*.sc      # → 1 (the definition)
grep -cE ' ~ | & '          parser_*.sc      # → many (per construct)
grep -cE 'nPush|nInc|nTop|nPop' parser_*.sc # → ≥ counter-helper hits / parser table above
```

## Divergence-driven rungs — n-ary vs the native frontend's binary

The self-hosted parser produces n-ary trees. The native Rebus frontend (`src/frontend/rebus/rebus_lower.c`) uses `expr_binary(E_ALT, ...)` for `RE_ALT` — that is, every `|` is a binary node. So `a | b | c` in the native frontend is `(E_ALT (E_ALT a b) c)`, while the self-hosted parser produces `(E_ALT a b c)`. Same for `f(a, b, c)` arglist (the native frontend may or may not be n-ary there — re-verify per rung), statement sequences, parameter lists, etc.

**This is intentional divergence, not a bug in the self-hosted parser.** Per the DEFINITION OF DONE, `tree_equal(t1, t2)` was the original gate (now retired, see GOAL PIVOT); for any rung where the native frontend's tree is binary-folded but the self-hosted parser's is n-ary, that gate would fail. That failure was the rung's *output*: the self-hosted parser discovered that the native frontend should be flattened.

**Rung procedure when n-ary divergence is found:**

1. The self-hosted parser produces the n-ary tree per the canonical spine. Don't fold to binary "to make the gate pass."
2. The rung's commit message names the divergence explicitly: "existing frontend produces binary E_ALT; self-hosted parser produces n-ary E_ALT. Divergence reported — track upstream fix in the native-frontend rung."
3. Open/update the corresponding native-frontend rung (`## RUNGS Track 2`) to flatten the native frontend's lowering. Until that lands, `tree_equal` failure on alt-bearing fixtures is *expected*; mark those fixtures "divergence-pending" rather than counting them FAIL.
4. When the native-frontend fix lands, the divergence-pending fixtures become gating PASS without any change to the self-hosted parser.

The 144 fixtures at `corpus/tests/rebus/parser/` will not all clear with one push under this regime, by design — the self-hosted parser's job is not to mirror the native frontend's bugs.

## Worked atom example — the smallest correct rung

This is the shape RB-0 took (and the shape any new rung on the self-hosted parser should still take). Read it, follow it. **No functions are called from inside any pattern.** The grammar is pure pattern composition.

```snocone
// Lex tokens — drop into the file once, used by every rung.
ws_run = SPAN(' ' tab);
ws_opt = (ws_run | epsilon);
nl_one = ANY(nl);   // matches exactly one newline char, pure primitive

Id      = (ANY(&UCASE &LCASE '_')
           (SPAN(&UCASE &LCASE digits '_') | epsilon));

Integer = SPAN(digits);

// String body capture idiom — quotes matched by sibling sub-patterns;
// only the body goes through `~`. No function calls. The match span
// of `*DQ_body` is the body text (BREAK stops at the closing quote);
// `~ "'E_QLIT'"` shifts tree('E_QLIT', body) onto the stack.
DQ_open  = '"';   DQ_close = '"';   DQ_body = BREAK('"');
SQ_open  = "'";   SQ_close = "'";   SQ_body = BREAK("'");
qlit_dq  = DQ_open *DQ_body ~ "'E_QLIT'" DQ_close;
qlit_sq  = SQ_open *SQ_body ~ "'E_QLIT'" SQ_close;
String   = (*qlit_dq | *qlit_sq);

// atom — Rebus's expr17 slice (id | integer | string).
// `~` is OPSYN'd to shift; rhs is the tree-tag string.
atom = FENCE(  *String
             | *Integer ~ "'E_ILIT'"
             | *Id      ~ "'E_VAR'"
            );

// stmt — for RB-0, a statement is just an atom in :subj position.
// Overall STMT shape: (STMT :subj <atom>).
// `&` is OPSYN'd to reduce; rhs is the child count (1 here, fixed-arity).
stmt = ws_opt *atom ws_opt nl_one ("'STMT_SUBJ'" & 1);

// Command — single top-level alternation. At RB-0, only `stmt`.
Command = nInc() *stmt;

// Compiland — the canonical beauty.sc spine. ONE root pattern.
// `'nTop()'` is the n-ary count: however many Commands matched,
// that many children fold into the Parse node.
Compiland = nPush() ARBNO(*Command) ("'Parse'" & 'nTop()') nPop();

// Driver — read whole stdin into Src, ONE pattern match, walk the result.
// No goto. No labels. No per-line matching.
InitCounter();
InitStack();

Src = '';
Line = INPUT;
while (DIFFER(Line)) {
    Src = Src Line nl;
    Line = INPUT;
}

if (Src ? Compiland) {
    parse_root = Top();
    i = 0;
    while (i = LT(i, n(parse_root)) i + 1)
        TDump(c(parse_root)[i]);
} else {
    OUTPUT = 'PARSER-RB: parse failed';
}
```

**Self-check before committing a rung built on this shape:**

```
grep -c 'goto '              parser_rebus.sc  # → 0
grep -cE '^[a-z_]+:'         parser_rebus.sc  # → 0
grep -c '_rb_state'          parser_rebus.sc  # → 0
grep -cE 'shift\(|reduce\('  parser_rebus.sc  # → 0
grep -cE 'Push\(Tree'        parser_rebus.sc  # → 0
grep -cE '\*[a-z_]+\('       parser_rebus.sc  # → 0  (no fn-call-from-pattern;
                                              #      *Sub references take no parens)
grep -cE 'nPush|nInc|nTop|nPop' parser_rebus.sc  # → ≥2  (1 nPush, 1 nPop in
                                                  #       Compiland; ≥1 nInc in
                                                  #       Command; ≥1 nTop in
                                                  #       Compiland's reduce)
grep -cE ' ~ | & '           parser_rebus.sc  # → ≥4  (3 ~ in atom; 1 & in stmt;
                                              #      1 & in Compiland)
grep -c 'Src ? Compiland'    parser_rebus.sc  # → 1  (the ONE pattern match)
grep -c 'Compiland'          parser_rebus.sc  # → exactly 2 (def + driver use)
grep -cE '^function '        parser_rebus.sc  # → 0  (no helper functions for
                                              #      RB-0; later rungs may add
                                              #      lowering passes that consume
                                              #      the parse tree, but never
                                              #      functions called from
                                              #      inside patterns)
```

---

## Session Setup (every session)
```bash
git clone https://github.com/snobol4ever/.github /home/claude/.github; for r in SCRIP corpus x64; do git clone https://github.com/snobol4ever/$r /home/claude/$r; done
cd /home/claude/SCRIP && git config --local user.name LCherryholmes && git config --local user.email lcherryh@yahoo.com
bash scripts/install_system_packages.sh && rm -f scrip && timeout 1500 make -j8 scrip > /tmp/build.log 2>&1 && make libscrip_rt && ls -la scrip out/libscrip_rt.so
# ⛔ CONCURRENCY PRE-CHECK (STANDING CONDITION): git -C . log origin/main..HEAD ; git status --porcelain — non-empty ⇒ clone fresh and measure THERE
bash scripts/test_smoke_rebus.sh && bash scripts/test_smoke_unified_broker.sh && bash scripts/test_crosscheck_rebus.sh
bash scripts/run_scrip_parser.sh rebus corpus/tests/rebus/syntax_exercise.reb   # self-hosted parser smoke
```
⚠ The original PARSER-REBUS Session Setup checked out a dedicated `parser` git branch (`git checkout parser 2>/dev/null || git checkout -b parser origin/parser ...`) in the SCRIP repo. **That branch no longer exists** (`git branch -a` confirms, 2026-08-27) — work happens on `main`, consistent with the rest of the project's current single-branch convention. Do not resurrect the branch step without checking with hq_C/hq_P first.

## ⛔ SESSION-CLOSE RULES LIVE IN `RULES.md` — NOT DUPLICATED HERE
"HANDOFF COMPLETE" requires a confirmed push; `scripts/handoff_status.sh` verbatim is the only truth; credential missing ⇒ BLOCKED, ask Lon in-chat and WAIT. Move THIS file's LIVE CURSOR every session — no cursor move, no close.
