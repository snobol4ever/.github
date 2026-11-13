---
name: snocone-parser-patterns
description: Writing the bootstrap parsers (SCRIP/bootstrap/parser_*.sc) as one Snocone pattern: Shift and Reduce by conditional assignment, the counter stack, FENCE and ARBNO, the token tables. REQUIRED by the skill gate before editing a .sc parser.
---

# Parsers as patterns in Snocone

A parser matches a WHOLE FILE with ONE closed set of mutually referential patterns and builds the pruned parse tree by conditional assignment (Lon 2026-10-31). The law is RULES.md (THE TREE IS THE PRUNED PARSE TREE, RAW SHIFT AND REDUCE ALONE, A PARSER MOVES NOTHING, ONLY tree_t CROSSES; CEO-1322/1369/1371/1377/1378/1532); the design is `reference.md` § 8. Quoted lines, file positions and receipts are in `reference.md` beside this file.

## 1. The oracle and the rule

- SPITBOL semantics: `sbl -bf` runs the transpiled `.sno` twin (`scrip --transpile`); for the oracle, `FLUSH` is `FENCE`. The parser's own oracle is its language's C parser, graded tree for tree.
- One closed set: every pattern is a global assigned once at init and referenced only as `*name`; never by value, never a function the grammar calls.
- The tree is built once, in recognition order, by raw Shift and Reduce: a leaf `(pat) . thx . *Shift(kind, thx)`, a node `. *Reduce(kind, n[, v])`. Nothing walks, reorders or rewrites a node afterwards.

## 2. The manuals

`/home/resources/manuals/snobol4/spitbol-manual-v3.7.txt` (`.` deferred and `$` immediate assignment, `*e`, `FENCE`, `ARBNO`, `POS`/`RPOS`, the 130-character literal limit), `green-book.txt`, `/home/resources/manuals/byrd-boxes/`; the Snocone surface in `corpus/tests/snocone/report.md`. Probe a construct in five lines on `sbl -bf` and `./scrip` before writing it.

## 3. The source map

- Parsers: `SCRIP/bootstrap/parser_{snobol4,snocone,rebus,icon,prolog,pascal,raku}.sc`.
- Library (Makefile `SC_MOD_LIB`, concatenated before a parser): `global.sc`, `tree.sc`, `stack.sc` (`$'@S'`), `counter.sc` (`$'#N'`), `ShiftReduce.sc` (Shift, Reduce, PushVal, PopVal), `semantic.sc` (`nTop`), `tdump.sc`, and the rest.
- Module wrapper: `mod_head.sc`, `mod_tail.sc`, generated `out/sc_mod/scmod_<lang>.sc`; the C entry is `src/runtime/rt/rt_sc_module.c` (cells `ModSrc ModLinked ModTree ModInited`).

## 4. The design this skill carries, and the related skills

The module design (each parser a compiland with its own namespace: SNOBOL4's INCLUDE shares one namespace, Snocone's IMPORT links a library into the caller's; one entry, one exit, the tree bridged to `tree_t` by `src/runtime/rt/rt_sc_module.c`) and the zero-functions finish are in `reference.md` § 8. Related skills: `snobol4` (SPITBOL semantics, the oracle), `scrip-architecture` (where the bootstrap sits in the pipeline), `pascal` (the dialect global tested in `parser_pascal.sc`), the language skill of the parser touched, `gates-and-witnesses`.

## 5. The patterns and the proof

- The file is one match of `Compiland`: `POS(0) ARBNO(*Command FLUSH) ... RPOS(0) . *Reduce('Parse', nTop())`; `FLUSH` after each command replays its queued actions so memory stays linear.
- `.` is DEFERRED (replays after the match or at FLUSH, in queue order); `$` is IMMEDIATE (scan time). A value a Shift carries comes from a MEMO TABLE keyed by the raw text, read through its own capture (`*Shift('TT_ILIT', IcnIV[thx])`), never a global (a global holds its last value by replay time).
- Variable arity: `epsilon . *PushCounter()`, `*IncCounter()` on each child arm, `*Reduce(kind, nTop())`, `*PopCounter()`. `PushVal`/`PopVal` carry a name to its Reduce across the arguments' actions.
- Left association is a TAIL LOOP (`Expr6t = FENCE(... *Expr7 . *Reduce('TT_ADD', 2) ... *Expr6t | epsilon)`); right association is RIGHT RECURSION; precedence is the chain `Expr0 → ... → Expr14`.
- `$' '` is optional white space, `$'  '` required; an operator is a pattern named by its spelling; a keyword is `*Id $ tx *IDENT(tx, 'if')` or an exactly sized `TABLE` lookup.
- `FENCE` wherever a choice is final. `ARBNO` is SHORTEST FIRST: match-time work after an ARBNO'd capture runs on every prefix, so place two cursors around the body and do the work after the closing delimiter. A nested match that must consume is ANCHORED: `X ? (POS(0) ARBNO(P) RPOS(0))`.
- White space and a statement list are TAIL FORMS, never ARBNO: `White = *white FENCE(*White | epsilon)`, `StmtStar = FENCE(*StmtRest *StmtStar | epsilon)`. Under ARBNO a FENCE'd continuation takes one blank only, and a refusal late in an ARBNO'd statement list backtracks 2^n through the statements before it.
- THE PREPROCESS STAGE and THE DRIVER TAIL are labelled top-level code outside the match: the directive line is replaced in `Src` and the scan restarts; the driver resets the stacks, matches `Src ? *Compiland` and hands `ptree` on.
- Prove it with `harness/scripts/`: `run_scrip_parser.sh <lang> [file]`, `util_parser_sc_census.py --lang <l>`, `test_bootstrap_parsers.py`, `util_parser_sc_parity.sh`, `test_gate_bootstrap_parse_stage_ir_identity.sh`, `util_parser_sc_grade.sh`, `test_gate_bootstrap_parsers_define_no_functions.sh`.

## 6. Debugging a parser red

1. `bash harness/scripts/monitor_run.sh prog.sno --oracle` on the transpiled twin when a library or language question is suspected.
2. The tree first: `out/parser_<lang> file` against the `.sc` dump (`util_parser_sc_grade.sh` names the smallest differing file); `xTrace = 3` prints every Shift and Reduce as it replays.
3. A five-line probe and a sibling one ingredient apart. A check that reads the stack inside the match reads it empty: queued actions have not run.
4. Slow file: an ARBNO prefix explosion; read `PARSER-METRICS`.
5. Only then `scrip --dump-ast`, asm-diff, gdb.

## 7. What a parser may not do

- DEFINE NO FUNCTIONS (CEO-1532; floors only fall, finish 0): use F1 inline, F2 pattern with a memo table, F3 action chain (`*DIFFER(x = e)`), F4 labelled top-level code.
- Evaluate, check meaning or desugar nothing (that is the lowerer's); re-order nothing (CEO-1371); invent no wrapper nodes; keep no side table past the tree (CEO-1322/1715).
- SPITBOL's limits: string literals of at most 130 characters; `SUBSTR(S, I, 0)` is the rest of S.
- Style: names of at most 16 characters, the column rule of skill `scrip-c-code` section 1 (CEO-1565), comments only as `/* */` blocks above a pattern.
- Never rewrite a `parser_*.sc` (Lon: "At most a few characters will need to be changed to fix a bug.").
