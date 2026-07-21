# FINDING-2026-07-21-CLAUDE-SNOCONE-CONSTRUCT-COVERAGE-LADDER-12-DEFECTS

**Session:** Claude Opus, 2026-07-21. Goal: GOAL-SNOCONE-BB (no file by that exact name;
treated GOAL-SNOCONE-IR-BB.md as the goal). Task: climb the ladder to 100% coverage of Snocone
language constructs, native `scrip --run` (mode-3) vs SPITBOL oracle.

## METHOD
- Built SCRIP from source this session (apt: libgc-dev flex nasm libgmp-dev m4; `make scrip` clean).
- Oracle: `git clone .../x64`, `sbl` prebuilt. Candidate: `scrip --run`. Oracle path:
  `scrip --transpile | sbl -b`, or a hand-written `.oracle_ref.sno` where the transpiler is broken.
- 66 construct probes derived directly from `parser_snocone.sc` (every Expr tier + every statement
  form + integration programs). Blank-insensitive compare (see D5).
- Harness + probes + captured I/O preserved at `/home/claude/ladder/` (sandbox-only, as before —
  copy into corpus if we want it versioned; prior session's ladder was lost the same way).

## HEADLINE
**66 probes, 55 PASS, 11 FAIL → 12 distinct defects.** Native runtime is CORRECT for the large
majority of the language: all literals, arithmetic + precedence + right-assoc `^`, concat, every
numeric/lexical comparison predicate AND the infix `< > == != <= >=` operators, IDENT/DIFFER,
builtin string fns, pattern matching in boolean/if context (SPAN/BREAK/LEN/ANY/NOTANY/BREAKX/
POS/RPOS/TAB/RTAB/REM/ARBNO), `.`/`$` capture (+ chaining), alternation, match-with-REPLACEMENT,
recursive pattern defs with deferred `*List`, ALL control flow (if/elif/else, while, do-while,
for, break, continue, switch/case/default), functions (params, return, freturn, recursion,
folded locals), struct + accessors + setters, indirection `$`, array, table (incl multi-dim
`a[i,j]`), augmented assign, multiple assign, unary `.`/`~`/`@`, comments, DATATYPE/CONVERT.

## THE CONSEQUENTIAL CLUSTER — match-result flowing into value/condition position
These four are almost certainly ONE root cause in native codegen: how a `TT_SCAN` (match) result
unwinds when consumed as a value or a loop/branch condition. HUNT WITH MONITOR-FIRST (not done this
session — flagged context budget; the 2-way sync-step monitor is the sanctioned next step).

- **D12 (most consequential)** — `while (s ? pat) { ... }`: a bare match as loop condition breaks
  control flow entirely. `while (s ? 'a') {OUTPUT='in'; s='xyz';}` between two OUTPUTs → only the
  first OUTPUT prints; body never runs, post-loop stmt never runs, rc=0. This is the backbone
  tokenizer idiom of every `parser_*.sc`. Workaround: predicate-wrap the condition, match in body
  (`while (GT(n,0)){...; s?pat='';...}` → correct).
- **D2** — match VALUE in expression position: `OUTPUT=(s?'hel')'X'` → silent empty (want `helX`);
  `r=(s?'hel')` → `libscrip_rt: BOMB bz` / abort (want `hel`). Oracle confirms values.
- **D3** — unanchored FENCE commit-unwind: `'1AB+' ? ANY('AB') FENCE '+'` (fails after cursor
  advanced past 0) drops the `else` branch and SEGFAULTS when two such stmts chain. Anchored FENCE
  and no-FENCE both fine → isolated to the unanchored-commit unwind.
- **D4** — ABORT chained after unanchored advance: second use mis-unwinds; segfault when chained.

## NATIVE-SUBSET PENDING (honest FATAL, oracle handles)
- **D6** — goto/label: FATAL "tree kind 127 not in landed subset".
- **D9** — unary interrogation `?expr`: FATAL "tree kind 9 not in landed subset".
- **D11** — `LEN(*n)` computed/deferred count: FATAL "LEN with deferred/missing count outside
  operand-edge subset". (The state-dependent-length idiom from the primer.)

## PARSE-LEVEL GAP (confirms goal-file open gap #1)
- **D10** — OPSYN-slot BINARY operators `& ~ @ # %` have NO grammar production → "snocone parse
  error: syntax error" at any binary use-site, in native AND transpile. UNARY `~`/`@` parse fine.
  Blocks the `semantic.sc` `OPSYN('~','shift',2)`/`OPSYN('&','reduce',2)` idiom in native Snocone.

## OTHER
- **D8** — alternative-eval `(e1,e2,e3)` fall-through: value dropped when the first alternative
  fails and a later one should supply it (`(LT(5,3)'a', GT(5,3)'b', 'c')` → native empty, want 'b').
- **D1** — `--transpile` SEGFAULTS on every real literal (TT_FLIT); native formatting is
  byte-identical to SPITBOL (`1000.`, `0.25e-1`). Backend-only.
- **D5** — `--transpile` emits spurious empty `OUTPUT =` at every if/loop-end label → stray blank
  lines under sbl. Backend-only; native correct. (Inflated apparent FAILs before harness fix.)
- **D7** — nreturn+name transpiles to malformed SNOBOL (`ERROR 239 indirection operand not name`);
  native also empty. Needs isolation; partly test-idiom-sensitive.

## INCIDENTAL CORRECTION TO PRIMER
DATATYPE returns UPPERCASE (STRING/INTEGER/REAL) in BOTH `scrip --run` and this `sbl` build — no
case divergence observed this session, contra the primer's "SPITBOL returns lowercase" caution.

## RECOMMENDED NEXT RUNG
D2/D3/D4/D12 as ONE hunt via the 2-way sync-step monitor (`test_monitor_2way_sync_step_bin.sh`),
starting from the D12 minimal repro (`while (s ? 'a') {...}`) — smallest trigger, backbone idiom.
Bracket → gdb hit-count spin → land mine, per RULES MONITOR-FIRST. Then D6/D9 (subset landings)
and the backend trio D1/D5/D7 are independent, parallelizable.
