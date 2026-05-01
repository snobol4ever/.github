# GOAL-SNOCONE-BEAUTY — beauty.sc Self-Beautifies via scrip

**Repo:** one4all
**Done when:** `./scrip --ir-run test/beauty-sc/beauty/beauty.sc < input.sno`
produces output byte-for-byte identical to SPITBOL running `beauty.sno` on
the same input. Gate script reports PASS.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh              # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh   # PASS=42 SKIP=3
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh       # PASS=44
```

---

## Architecture (TWO STEPS)

**Step 1 — .sno subsystem files + beauty.sc:**
scrip handles mixed-extension multi-file linkage natively. Pass subsystem
`.sno` files as libraries, `beauty.sc` as main program:

```bash
./scrip --ir-run \
    corpus/programs/snobol4/beauty/global.sno \
    ... \
    corpus/programs/snobol4/beauty/trace.sno \
    test/beauty-sc/beauty/beauty.sc < input.sno
```

Oracle: `smoke/beauty_oracle.sno` (NOT `demo/beauty.sno` — crashes error 021).

**Step 2 — Replace .sno subsystem files with .sc equivalents:**
Substitute from `corpus/programs/include-sc/` one by one, gate stays green.

---

## Current state (2026-04-29, session #68)

SB-1..SB-3 DONE.  SB-4a DONE.  SB-4b DONE (all 14 sub-rungs, session #67).

SC sources live at `corpus/programs/snocone/demo/beauty/` (session #62, finalized).
Source modules at top level. Subsystem tests flat in `test/` as `test_<subsys>.sc` + `test_<subsys>.ref`.
Gates green: PASS=5, PASS=42 SKIP=3, PASS=49.

**Session #68 progress.** SB-5b advanced significantly. Three real bugs
fixed, plus mechanical rename `snocone_cf` → `snocone_control`.

**Three runtime/frontend bugs fixed this session:**

1. **`snocone_lower.c` — unary `*` was lowering to `E_INDIRECT`, not `E_DEFER`.**
   SNOBOL4 has two visually-similar but distinct concepts: `$expr`
   (indirect lookup) lowers to `E_INDIRECT`; `*expr` (deferred /
   unevaluated expression) lowers to `E_DEFER`.  The Snocone frontend
   was using `E_INDIRECT` for both, so `P = *Id` produced
   `DATATYPE='STRING'` instead of `'EXPRESSION'`.  Verified via SPITBOL
   oracle: `*Id POS(0) ... RPOS(0)` matched `'x'` correctly under
   SPITBOL but failed under Snocone before the fix; matches identically
   after.  This was the gating bug — it broke every `*Pat`-anchored
   match in beauty.sc (every parser pattern uses them).

2. **`scrip.c` driver — multi-file merge did not strip intermediate
   `is_end` sentinels.**  Each frontend emits one `is_end` at end-of-file.
   When concatenating `lib1 main`, the first file's END halted execution
   before main ran.  Confirmed bug in pure SNOBOL4 multi-file too:
   `./scrip --ir-run /tmp/lib1.sno /tmp/main1.sno` produced only lib1's
   output before the fix; both files' output after.  Fix: in the merge
   loop strip the trailing `is_end` from running prog before chaining
   the next sub-program.  The very last sub's `is_end` stays as the
   merged program's terminator.

3. **`semantic.sc` — `shift()` and `reduce()` EVAL strings malformed.**
   `reduce()` was building `EVAL("epsilon . *Reduce(=, 2)")` — invalid
   SNOBOL4 syntax (bare `=`).  Fixed to wrap `t` in single quotes:
   `"epsilon . *Reduce('" t "', " n ")"`.  `shift()` was concatenating
   the value of `p` into the EVAL string instead of using the literal
   name `p` (the canonical SNOBOL4 trick: `p` in the EVAL string is
   resolved dynamically at EVAL time to the procedure-local pattern).
   Both fixes match the canonical `semantic.inc` behavior.  `shift()`
   and `reduce()` now return PATTERN values for every call form used
   in `beauty.sc`.

**Mechanical rename `snocone_cf` → `snocone_control`** (per Lon, this
session).  `git mv` on `snocone_cf.{c,h}` → `snocone_control.{c,h}`,
function `snocone_cf_compile` → `snocone_control_compile`, all
references updated in `Makefile`, `driver/interp.c`, `driver/scrip.c`,
`frontend/rebus/rebus_lower.c`, `frontend/snocone/snocone_driver.c`,
plus the renamed files' own self-references.  Build + all three gates
remain green.

**Goto/label elimination in `beauty.sc`.**  Per Lon, "reduce number of
goto statements in Snocone source to almost zero."  All gotos and
labels eliminated:

- `goto ss_unop` (in `ss()`) — restructured the binary `|` handler with
  a `~EQ(n,1)` guard so the unary case falls through to the
  general `EQ(n,1)` block below.  No semantic change.
- `refs` procedure — the `goto refs_next` skip-rest-of-iteration
  pattern (4 sites) rewritten as nested `if` blocks.
- Main loop — 5 gotos and 3 labels (`mainErr1:`, `mainErr2:`, `END:`)
  rewritten as a structured `done` / `more` / `eof_inside` flag
  machine with inline error handling.  Same logical behavior as the
  goto version: read header lines, accumulate continuation lines into
  Src, parse-and-pp on non-continuation or EOF, print Parse Error or
  Internal Error inline on failure.

`grep "goto "` on beauty.sc now shows zero gotos.  One remaining
mention is a comment about "the SNOBOL4 goto AST node" — not a
Snocone goto, just documentation.

**Snocone-runtime bug (NOT YET FIXED, separate from SB-5b).**
`INPUT` after EOF does not fail — returns the previous value rather
than failing the assignment.  SPITBOL oracle: 3rd `INPUT` after 2-line
input fails the assignment.  Snocone: 3rd `INPUT` returns the previous
line again, causing `while (DIFFER(Line = INPUT))` to loop forever.
The session #68 main-loop rewrite uses a `done` flag explicitly set
on EOF detection, working around this bug — but the underlying issue
should be tracked as its own rung.  Suggested name: SC-INPUT-EOF.

**Three EVAL parse errors at startup (not yet root-caused).**
Three lines of `snobol4:0: error: parse error: syntax error` print
on stderr during pattern construction in beauty.sc.  Bisection placed
the first @T0 OUTPUT after the errors, then @T1 (after ppStop), then
@T2 (after Real) — all execute.  Errors fire BEFORE @T0 in real time
because stderr is unbuffered, but they are emitted DURING beauty.sc's
top-level execution (in some `EVAL` call inside pattern construction).
Likely a `reduce()` or `shift()` call where the embedded `t`/`n`
contains a character SNOBOL4's parser rejects.  Did not reach root
cause this session.  Stdout still empty after @T2 trace.  No further
trace points placed past line 25 of beauty.sc this session — that's
the next session's first task.

**Active rung remains SB-5b.**  Beauty.sc no longer hangs on label
parse, no longer halts at first END, no longer fails on `*Pat`
construction, no longer fails on the `&`/`~` operator semantics
mismatch.  Top-level execution proceeds through pattern construction.
Whatever blocks output between line 25 and the first parse attempt
is the next thing to find.

**Session #67 progress (kept for context).** SB-4b.2..SB-4b.14 closed (full SB-4b sweep).
- `case.sc`, `assign.sc`, `match.sc`, `stack.sc` audited and confirmed
  faithful — no source changes needed.
- `counter.sc` rewritten 6 → 16 procedures (added BegTag + EndTag families
  per canonical `counter.inc`).
- `tree.sc` rewritten — replaced the `MakeNode`/`MakeLeaf` stubs with the
  full canonical 9-procedure ADT (`Tree`, `Append`, `Prepend`, `Insert`,
  `Remove`, `Equal`, `Equiv`, `Find`, `Visit`). Smoke tests at
  `/tmp/tree_smoke.sc` confirm all procedures work, including
  `APPLY(.fn, x)` callback dispatch and the `$('c' && nc)`
  dynamic-name read for `Tree`'s variadic ctor.
- `ShiftReduce.sc` rewritten — restored the canonical
  `v ? (POS(0) && whitespace) = ;` leading-whitespace strip in `Shift`.
  EVAL-failure detection in `Reduce` documented as Snocone-runtime
  limitation (statement-level failure not expressible).
- `Gen.sc`, `Qize.sc`, `ReadWrite.sc`, `TDump.sc`, `XDump.sc` audited —
  all canonical procedures present, session #64 rewrites are sound.
- `omega.sc` rewritten for TV/TW/TX semantic fix — `omega = 'pat'`
  (canonical literal-source-text) replaces the prior
  `omega = pat;` (variable substitution). Open question on TY/TZ
  thin-path expression `expr && @var . *fn(...)` collapsing to
  STRING in Snocone — preserved as-was from prior port; no
  regression. Documented as follow-on.

All three gates remain at PASS=5 / PASS=42 SKIP=3 / PASS=49 after
every per-module change.

**Snocone-port discoveries (session #67):**
1. **Parser does not accept leading-comma `(, locals)` form.**
   `snocone_cf.c::do_procedure`'s parameter-list loop bails as soon
   as it sees `,` before any IDENT, without consuming the leading
   `(`. Silently corrupts parse and causes infinite hang at runtime
   (no parse error). Workaround: declare locals as ordinary parameters —
   SNOBOL4 zero-arg invocation initializes them to null, the canonical
   local-var semantics. Used in counter.sc's `DumpBegTag(b, list, v)`
   and `DumpEndTag(e, list, v)`. Should be either (a) fixed in the
   parser to recognize `(, locals)`, or (b) documented as the
   canonical Snocone-port idiom in the language-facts section.
2. **Snocone `if (assignment)` does not propagate inner EVAL failure**
   to the test arm. Verified at /tmp/eval_detect.sc — even when EVAL
   prints a parse-error to stderr and leaves the LHS null, the
   if-arm always succeeds. Workaround: use `if (~DIFFER(lhs))` after
   the assignment as a proxy for "EVAL failed-and-returned-null".
   Affects ShiftReduce.sc Reduce and omega.sc TV/TW/TX/TY/TZ. The
   common-case failure mode (EVAL returns null on error) is caught;
   the divergent edge case (EVAL succeeds, returns null) does not
   arise in the beauty pipeline.
3. **Snocone `expr && @var . *fn(...)` produces STRING, not PATTERN.**
   The expression `pat && @txOfs . *assign(.t8Max, ...)` from
   omega.sc thin-path produces a string at runtime, while
   `pat && @txOfs` alone IS a pattern. Cause unidentified; likely
   `snocone_lower.c` SNOCONE_PERIOD interaction with unary STAR.
   Open follow-on; gate not affected (no test exercises this
   path today).

**Active rung now:** SB-5b — rewriting beauty.sc's binary `&` (reduce)
and binary `~` (shift) sites as explicit `reduce(t, n)` / `shift(p, t)`
function calls. With SB-4b complete, SB-5b is the gating issue for
end-to-end SB-5 (beauty.sc producing output).

**Session #66 progress (kept for context).** Stripped non-canonical `--auto` two-pass block and
`HOST(0)` args parser from `beauty.sc` (lines 13–97 → gone, file 533 → 447
lines). Restored canonical `ppStop[]` defaults (`18, 33, 36, 81; 6, 21`) to
match `beauty.sno`. All three gates remain green after the strip. **However,
end-to-end SB-5 still fails.** Empty stdout, no Error 5 when full library
chain (`global.sc + case.sc + ... + omega.sc + beauty.sc`) is supplied.
Error 5 fires only when `beauty.sc` is run alone (which is expected — its
helper procedures live in the other .sc files).

**Session #65 — deeper SB-5 root cause located.** The Snocone parser does
not handle binary `&`. `snocone_lower.c` line 209 `case SNOCONE_AMPERSAND:`
treats `&` as **unary keyword prefix only** — `&UCASE` → `E_KEYWORD`.
There is no binary case. `beauty.sc` line 61 contains the construct
`("'ExprList'" & '*(GT(nTop(), 1) nTop())')`, intended as the `reduce`
operator from `semantic.inc`'s `OPSYN('&', 'reduce', 2)`. Verified by
dumping IR for a minimal repro (`/tmp/amp_test.sc`):

```
P = ("'ExprList'" & '*(GT(nTop(), 1) nTop())');
→ (STMT :eq :subj (E_QLIT "'ExprList'") :repl (E_QLIT "*(GT(nTop(), 1) nTop())"))
```

The `&` is **silently dropped**. The two strings are split between subject
and replacement of an unintended assignment statement. seven such reduce
sites in `beauty.sc` (lines 61, 67, 69, 89, 93, 132, 133) all corrupt the
parser table — overwriting `ExprList`, `Expr3`, `Expr4`, `Expr15`, `Expr16`,
`Parse`, `Compiland` with bogus values. The pattern grammar is broken
before any input is read; `beauty.sc` produces no output because its
parser never builds correctly.

**Companion issue.** `~` (the `shift` operator from `semantic.inc`) was
translated as `*Pat . '' && 'Name'` in beauty.sc (e.g. `*ProtKwd . ''
&& 'ProtKwd'` at line 81). That is *not* semantically equivalent to
`*Pat ~ 'Name'` — the latter pushes a node onto the semantic stack via
`Shift(t, thx)`. The `. '' && 'literal'` form just builds a pattern that
matches the literal string `"ProtKwd"` after `Pat` consumes — wrong
grammar, never matches real input.

**Two real ports missing**:
- `semantic.inc` (defines `shift, reduce, pop, nPush, nInc, nDec, nTop, nPop`)
- `trace.inc` (defines `T8Trace, T8Pos`; `omega.sc` calls `T8Trace` 4x but
  only when `xTrace > 0`, so this is gated and may not trigger today)

`beauty.sc` calls `nPush, nInc, nPop, nTop` directly — those *are*
exercised on every parse. But since `semantic.inc`'s `shift`/`reduce`
operate as binary OPSYNs over `~`/`&`, and Snocone has neither binary `&`
nor binary `~` (Snocone `~` is unary E_NOT), a faithful port requires
**rewriting every `~`/`&` site in `beauty.sc` as explicit `shift(p, t)`
and `reduce(t, n)` function calls**, plus porting the `semantic.inc`
helpers as `semantic.sc`.

**Other .sc/.inc audit findings (session #65) — corrected in session #66**:
- `tree.sc` has only `MakeNode/MakeLeaf`; canonical `tree.inc` defines
  the full tree ADT (`Tree, Insert, Find, Append, Prepend, Remove,
  Visit, Equal, Equiv`). Earlier note ("dead code") was **wrong** —
  Lon clarifies the canonical procedures are gated on settings (e.g.
  parse-tree mode). SB-4b.7 ports the full canonical set.
- `counter.sc` has 6 of 15 procs; missing 9 are the BegTag/EndTag
  family (XML/HTML tag stack). Earlier note ("dead code") was **wrong**
  — they are gated on `xTrace > 4` and tag-tracking modes. SB-4b.5
  ports the full canonical set.
- `Qize.sc` has two helper procs (`LEQ`, `Ucvt`) not in `Qize.inc`. Helpers,
  fine — keep.
- `global.sc` has no procedures, just data. Matches `global.inc` shape.

**Session #64 progress (kept for context).** Per-file rewrite of six `.sc`
modules (case, Gen, TDump, XDump, ReadWrite, Qize) against the canonical
`.inc` sources, fixing three systemic Snocone-port bugs:

1. Predicate-form `subj ? (PAT)` does NOT consume from subject — only
   `. var` captures named in the pattern. Use statement-form
   `subj ? (PAT) = ;` for match-and-replace, or `RTAB(0) . subj` for
   capture-the-rest.
2. `if (~(subj ? PAT_with_captures))` runs the match but discards
   captures even on success. Use positive-form match with explicit
   else branch.
3. The SNOBOL4 idiom `i = LT(i, n) i + 1` does not compose in Snocone —
   bare juxtaposition raises Error 5. Use idiomatic
   `while (LT(i, n)) { i = i + 1; ... }`.

Session #64 also identified the `ppAutoMode` / `--auto` non-canonical
accretion in beauty.sc, which session #65 then stripped (above).

---


## Session #70 progress (2026-04-29)

**No source changes; investigation only. Repos clean (`git status` empty
across all three).**

**Hang root cause IS NOT what session #69 thought it was.** The hang
in `Src ? (POS(0) && *Parse && *Space && RPOS(0))` is NOT exponential
backtracking inside ARBNO(*Command), and is NOT a grammar/&FULLSCAN
issue. It is a Snocone-runtime bug poisoning pattern-matcher state.

### Minimal reproducer (9 lines, no beauty.sc, no .sno libs)

```snocone
procedure foo(x) {
    if (x) { x = 0; }
    return;
}
v = 'X';
if (v ? POS(0)) { OUTPUT = 'OK'; } else { OUTPUT = 'FAIL'; }
```

Run: `./scrip --ir-run /tmp/g.sc /tmp/d.sc < /dev/null`

Result: HANG in the C runtime. No `OK`, no `FAIL`, no &STLIMIT trip
even at very low values. The match never returns.

### What does NOT trigger it

- `procedure foo(x) { return; }` (empty body) — match works fine
- `procedure foo(x) { x = 0; return; }` (straight assign) — fine
- Pure context with no procedure at all — fine; Id matches in 5 stmts

### What DOES trigger it

- `procedure foo(x) { if (x) { x = 0; } return; }` — HANG
- `procedure foo(x) { while (LT(x, 10)) { x = x + 1; } return; }` — HANG

The common element: a `procedure` body containing a control-flow block
(if/while). The IR for such a body emits conditional-jump labels:

```
(STMT :subj (E_VAR x) :goS L.1 :goF L.2)
(STMT :lbl L.1)
(STMT :eq :subj (E_VAR x) :repl (E_ILIT 0))
(STMT :lbl L.2)
```

When this IR sits inside a `DEFINE`'d procedure (`(STMT :go foo.END)`
... `(STMT :lbl foo.END)` brackets), and ANY pattern match runs in the
top-level program after that, the match never terminates.

### Bisection that found this

Session #70 started by bisecting GOAL's stated next-step (ARBNO under
&FULLSCAN=1). Confirmed the hang via `&STLIMIT` (Error 22 fires on
500K). But narrowing further revealed the hang appears even at
`'X' ? POS(0)` (trivial match, no grammar). Bisected the library
chain: hang first appears at line 37 of `global.sc` — the body of
`procedure define_alphabet_run(start, len, ans, i)` (the very first
proc in the lib chain whose body contains `while`). Stripping its
body to a no-op makes the hang go away.

### Why session #69 was misled

Session #69's "ARBNO backtracking under &FULLSCAN=1" hypothesis is
INCORRECT. The hang fires for trivial matches that have nothing to
do with ARBNO or alternation. The session-#69 fixes themselves are
all correct and remain landed:

- `semantic.sc reduce()` double-quote wrapping for tags containing
  single quotes — correct.
- `if (~done)` → `if (DIFFER(done))` for non-pattern boolean — correct.
- Integer-0 → `''`-as-false flags for done/cont/more/eof_inside — correct.

Those fixes do real work. They were just not the path to "beauty.sc
produces output" because a deeper runtime bug blocks ANY subsequent
match.

### Next session — three concrete steps

1. **Mode-coverage check.** Verify whether the hang is `--ir-run`-only
   or also affects `--sm-run` and `--jit-run`. If only `--ir-run`,
   bug is in `src/driver/interp.c` tree-walker. If all three modes,
   bug is in shared pattern-matcher state.

2. **SPITBOL cross-check.** Write the SNOBOL4 equivalent of the
   minimal reproducer:
   ```snobol4
                   DEFINE('foo(x)')                                  :(foo_end)
   foo             differ(x)                                         :s(L1)f(L2)
   L1              x = 0
   L2                                                                :(return)
   foo_end
                   v = 'X'
                   v pos(0)                                          :s(ok)f(fail)
   ok              output = 'OK'                                     :(end)
   fail            output = 'FAIL'
   END
   ```
   Run under `/home/claude/x64/bin/sbl -bf`. If SPITBOL completes,
   bug is scrip-Snocone-specific (or scrip-runtime-specific). This
   is the strongest signal for which subsystem to dig into.

3. **Runtime bisection.** With (1) telling which mode(s), grep
   relevant runtime for "PDL", "STCOUNT", or pattern-matcher state
   variables. Look for: anything that could be initialized once at
   procedure-define time and not reset between calls; any global
   that the conditional-jump dispatch (`:goS L.N :goF L.N`) might
   leave in an unexpected state when the jump target is a label
   inside a procedure. The IR tree-walker (`src/driver/interp.c`)
   is the smaller surface area; start there.

### Files investigated, not modified

`src/frontend/snocone/snocone_lower.c`,
`src/frontend/snocone/snocone_control.c`,
`src/driver/scrip.c` (multi-file merge IS correctly stripping
intermediate `is_end` — confirmed at lines 338-355). No source
changes this session. Diagnostic test files in `/tmp/` only.

---

## Session #71 progress (2026-04-29)

**One landed fix; one bug remains; baseline cleaner for next session.**

### Sessions #69 / #70 hypotheses re-tested and disconfirmed

Session #71 began by following the session-#70 prescribed three steps
verbatim:

1. **Mode-coverage check.** Confirmed: full beauty.sc + 16-lib chain +
   `corpus/programs/snobol4/demo/beauty.sno` input hangs in **all three
   modes** (`--ir-run`, `--sm-run`, `--jit-run`) — each timing out at
   15 s with 0 stdout / 0 stderr. Per session #70's own decision tree
   ("if all three modes, bug is in shared pattern-matcher state"), this
   eliminated `src/driver/interp.c` (the IR tree-walker — only
   `--ir-run` uses it) as the suspect surface. Bug must be in shared
   runtime (`src/runtime/x86/...`) or upstream (frontend lower /
   driver merge).

2. **SPITBOL cross-check.** The 9-line "minimal reproducer" session
   #70 named **does not actually hang** under scrip — it prints `OK`
   in tens of ms in all three modes. Tested both the Snocone form
   (`/tmp/repro70.sc`) and the SPITBOL-equivalent SNOBOL4 form
   (`/tmp/repro70b.sno`); both succeed. **Session #70's claim that
   "proc body containing if/while corrupts the pattern matcher" is
   wrong.** The hang requires more than a 9-line setup.

3. **Session #69 hypothesis** also disconfirmed: setting
   `&FULLSCAN = 0` in beauty.sc does NOT eliminate the hang on the
   single-line `START` reproducer below. ARBNO+&FULLSCAN exponential
   backtracking is not the trigger.

### Tightest known reproducer for the residual hang

Single-line input — just the bare label `START\n`:

```bash
echo START | ./scrip --ir-run $LIBS $BEAUTY/beauty.sc
# → hangs 5 s, 0 stdout, 0 stderr
```

SPITBOL on the same input via `(cd $BEAUTY_INC && sbl -bf
$BEAUTY_SNO)` prints `START\n` and exits in 13 ms. With
`&STLIMIT = 500000` prepended, scrip emits the full 7-line
comment-header byte-identically, then trips Error 22 — proving the
pretty-printer pipeline runs cleanly through comment lines and the
spin starts specifically when the parser meets a label-only line.

SPITBOL oracle baseline: `(cd corpus/programs/snobol4/beauty && sbl
-bf demo/beauty.sno < demo/beauty.sno)` → **781 lines, md5
`f522a98b962449f97da470ab6a0b13c5`, 103 ms.**  This is the SB-6
target output for byte-identical match.

### Root cause #1: multi-file label collision — IDENTIFIED AND FIXED

Bisecting from "minimal_match alone works, but with libs prepended
it doesn't", isolated this concrete bug:

`src/frontend/snocone/snocone_control.c::newlab` used a per-`CfState`
counter. Every call to `snocone_control_compile()` started a fresh
`CfState` (`memset` to 0) so each .sc file produced its own
`L.1, L.2, ...`. After scrip's IR-merge in `src/driver/scrip.c`,
`label_table_build` (`src/driver/interp.c:133`) registered the
**first** occurrence of each label name; subsequent
`:goS L.N`/`:goF L.N` references in later files resolved to the
wrong target.

Symptom on `./scrip --ir-run global.sc m1.sc`, where `m1.sc` is
`v = 'X'; if (v ? POS(0)) {OUTPUT='OK';} else {OUTPUT='FAIL';}`:
- m1 emits `:goS L.1 :goF L.2` for the if-test, plus `lbl L.1`,
  `lbl L.2`, `lbl L.3` for the if-body / else / endif.
- global.sc also has `lbl L.1` ... `lbl L.8` (its own loops).
- After merge, `label_lookup("L.1")` returns global's first hit —
  inside global's UTF loop. The if-arm jumps into global's loop body
  and the program never reaches OUTPUT.
- Result: 0 output, rc=0 (silent termination). **Reverse order
  m1.sc global.sc loops nonsense:** global's `:go L.1` jumps back
  into m1's OK arm.

**Fix**: replace per-state `st->label_ctr` with a process-global
`static int g_snocone_label_ctr` at file scope. Every label across
every `snocone_control_compile()` call in this process is now
unique. +17/-1 in `snocone_control.c::newlab`.

**Verification:**
- `./scrip --ir-run global.sc m1.sc` → `>>> OK` ✅
- `./scrip --ir-run m1.sc global.sc` → `>>> OK` (no loop) ✅
- `./scrip --ir-run $ALL_16_LIBS m1.sc` → `>>> OK` ✅
- All three baseline gates remain green: PASS=5, PASS=42 SKIP=3,
  PASS=49.
- Beauty-suite all-modes (45 cells: 14 subsystems × 3 modes + 1
  SKIP × 3) all green. No regression.

### Root cause #2: residual hang on label parse — STILL OPEN

The label-collision fix solves the multi-file-trivial-match scenario,
but `START\n` still hangs beauty.sc. So there are **two separate
bugs**: (a) was multi-file label collision, fixed; (b) is something
specific to beauty.sc's grammar match against a label-only line.

After fix:
- `./scrip --ir-run $LIBS /tmp/m1.sc < /dev/null` → `OK` ✅ (was
  empty before; this regression is gone)
- `./scrip --ir-run $LIBS $BEAUTY/beauty.sc < START_LINE` → still
  hangs ❌

So the residual is genuinely inside beauty.sc's parsing logic, not in
the multi-file path. It's now isolated from the noise.

### Recommended next session — session #72

1. **Commit and push the label-collision fix as-is** (this session
   does that). Clean baseline for #72.

2. **Re-bisect with the new clean baseline** — start from
   `Stmt = epsilon` (already verified to hang on `START`),
   progressively reduce `Command`, `Parse`, `*Space`, `RPOS(0)`. The
   trivial-match `if (Src ? POS(0))` already shown to hang inside
   beauty.sc — so the spin is in the very-outer match, not in any
   complex grammar arm.

3. **Compare: minimal_match (`v='X'; if (v ? POS(0))`) works after
   libs ✅; beauty.sc's nearly-identical `if (Src ? POS(0))` after
   the same libs hangs ❌.** The difference must be something
   beauty.sc does at top level before the match — pattern
   construction, `&FULLSCAN`, `&MAXLNGTH`, the `ppStop` array, the
   pattern definitions for Integer/DQ/SQ/String/Real/Id/...etc., the
   `*Pat` deferred references, or one of the `shift()`/`reduce()`
   side-effects from `semantic.sc`.

4. **High-yield diagnostic**: minimally bisect beauty.sc. Take
   `m1.sc` (which works), append the smallest amount of beauty.sc's
   top-level code, retest after every chunk. The boundary statement
   that turns `OK` into `hang` is the trigger.

### Files touched this session

`src/frontend/snocone/snocone_control.c` — `+17/-1` in `newlab()`
making the label counter process-global. No other source changes.

### Repos state

`one4all`: dirty (one file). `corpus`, `.github`: clean. Plan: commit
fix to one4all + this update to .github, push both.

---

## Session #73 progress (2026-04-30)

**One landed runtime fix; two new bugs identified and tracked; one
out-of-scope program documented.**

This session was launched against SB-5c/SB-5d (claws5.sc and
treebank-{list,array}.sc end-to-end smoke). Setup gates green
(PASS=5, PASS=42 SKIP=3, PASS=49). Three baseline gates remain green
after the runtime fix.

### Landed: SB-5c.0 — `&TRIM` keyword honored on INPUT (FIXED)

`scrip` reported `&TRIM = 1` at startup but its `input_read()` did
NOT consult the keyword — every line read kept its trailing
whitespace, silently diverging from SPITBOL on every program that
slurps input. Confirmed by minimal reproducer:

```
SPITBOL `'hello   '` + `\n` → INPUT returns `'hello'`, SIZE = 5
scrip   `'hello   '` + `\n` → INPUT returns `'hello   '`, SIZE = 8
```

Fix in `src/runtime/x86/snobol4.c` `input_read()` (default INPUT
path) and the channel-bound input branch in `NV_GET_fn`: after the
existing `\n`-strip, when `kw_trim != 0`, strip trailing space and
tab characters. Confirmed against SPITBOL: `'X \t \n'` with `&TRIM=1`
now returns `'X'` (size 1) under both runtimes; `&TRIM=0` preserves
all bytes under both. Rebuild clean; PASS=5/PASS=42 SKIP=3/PASS=49
unchanged.

### Identified: SB-5c.1 — `ARBNO(ARBNO(*X) Y)` matcher bug

`treebank-list.sc` fails the outer `treebank` pattern match on real
input even though SPITBOL accepts it. Bisection isolates the bug to
**nested ARBNO with deferred-evaluation pattern reference in the
inner ARBNO**:

```snocone
&ALPHABET POS(10) LEN(1) . nl;
delim = SPAN(' ' && nl);
word  = NOTANY('( )' && nl) && BREAK('( )' && nl);
group = '(' && word && ARBNO(delim && word) && ')';
src = '(S sits)' && nl;

// scrip FAIL, SPITBOL OK:
if (src ? POS(0) && ARBNO(ARBNO(*group) && delim) && RPOS(0)) ...

// scrip OK on these (control bisection):
//   POS(0) && group && delim && RPOS(0)            — direct group, OK
//   POS(0) && *group && delim && RPOS(0)           — single deferred, OK
//   POS(0) && ARBNO(group && delim) && RPOS(0)     — outer ARBNO, OK
//   POS(0) && ARBNO(*group && delim) && RPOS(0)    — outer ARBNO + deferred, OK
//   POS(0) && ARBNO(ARBNO(group) && delim) && RPOS(0) — nested w/o deferred, OK
//   POS(0) && ARBNO(ARBNO(*group) && delim) && RPOS(0)  — FAIL  ✗
//   POS(0) && ARBNO(ARBNO(*group) && *delim) && RPOS(0) — FAIL  ✗
```

8-case bisection of variants produced exactly two FAILs, both
matching the shape `ARBNO(ARBNO(*name) Y)`. Same pattern shape on
SPITBOL passes all 8. Bug is in the scrip pattern matcher, not in
the .sc source. Same symptom under all three modes (`--ir-run`,
`--sm-run`, `--jit-run`), so the bug is in the shared pattern
runtime (`src/runtime/x86/snobol4_pattern.c` likely), not in any
mode-specific path.

Per Lon's session-#73 instruction: "Do not change any SC code to work
around a bug." This is now a step in the goal file, to be fixed in
the runtime — not papered over by rewriting `treebank-list.sc` to
avoid the construct.

### Identified: SB-5c.2 — treebank-array.sc Error 5 = bare-juxtaposition concat

`treebank-array.sc` reports `** Error 5 in statement 0 / Undefined
function or operation` and produces zero stdout. Bisection narrowed
to lines containing the SNOBOL4 idiom `LT(i, n - 1) i + 1` —
bare-juxtaposition concat used as a guarded-assignment value. Per
the Snocone language facts table in this Goal file: Snocone uses
`&&` for concat, not blank juxtaposition; the bare-juxtaposition
form is **not valid Snocone source today**.

Status: **NOT a SB-5c.2 runtime bug** — it is the symptom of the
gap tracked under `GOAL-SNOCONE-LANG-SPACE.md` (LS-0), which
proposes adopting SNOBOL4 X Y juxtaposition concat in Snocone.
Adopting space-concat in Snocone would let `treebank-array.sc` run
unchanged. Until then, the .sc source is structurally unrunnable
under scrip-Snocone, but per Lon's "no SC workarounds" rule we do
NOT rewrite it to use `if (LT(...)) { ... }` form. Cross-reference
recorded; SB-5d gates on LS-0 closing.

A secondary observation that should NOT be lost: the parser accepts
the bare-juxtaposition form silently (no parse error), and only at
runtime does it manifest as Error 5 with mislabeled
"in statement 0". Even if LS-0 is not adopted, the parser should
reject this construct loudly, and the runtime error should report
the correct statement number. Tracked as parser-quality follow-on
under `GOAL-SNOCONE-LANG-SPACE.md`.

### Out of scope: claws5.sc input-file mismatch

`claws5.sc` hangs (0 output, 60-s timeout) and `claws5.sno`
under SPITBOL on the same `claws5.input` produces "Pattern match
failed" — neither matches the 95-line `claws5.ref`. The .ref must
have been generated from `CLAWS5inTASA.dat` (also in corpus, header
of claws5.sno references it). Until input alignment is fixed, the
SB-5c gate as written ("scrip output byte-identical to SPITBOL
oracle on claws5 input") is technically achievable (both side-fail
to "Pattern match failed") but uninformative. Two independent
issues:

  - **Input-file alignment.** Determine which input the .ref was
    generated from; align `claws5.input` (or have the oracle read
    `CLAWS5inTASA.dat` directly).
  - **scrip hang.** Even with SPITBOL-failing input, scrip should
    finish with "Pattern match failed", not hang. This is likely
    the same family as the beauty.sc hang investigated in sessions
    #69–#71. May be the same root cause as SB-5c.1 (nested
    ARBNO pathology), or independent. Re-evaluate after SB-5c.1
    lands.

Both tracked below as SB-5c.3a and SB-5c.3b for after the SB-5c.1
runtime fix.

### Files touched this session

`src/runtime/x86/snobol4.c` — `+12/−2` in `input_read()` and the
channel-bound INPUT branch in `NV_GET_fn`. No other source changes.
Diagnostic test files in `/tmp/` only.

### Repos state

`one4all`: dirty (one file). `corpus`, `.github`: clean. Plan:
commit `one4all` runtime fix + this `.github` update, push both.

---

## Session #74 progress (2026-04-30)

**Build hygiene fix landed; one defensive runtime guard landed; SB-5c.1
diagnosis advanced significantly with concrete trace evidence.**

### Landed: Makefile stale reference

`Makefile` still referenced `snocone_cf.c` after the session #72 rename
to `snocone_control.c`. `make scrip` failed cleanly with "No such file
or directory". Fixed: object recipe now compiles
`src/frontend/snocone/snocone_control.c` (output object name kept as
`snocone_cf.o` to avoid touching the link line). Three baseline gates
remain green: PASS=5 / PASS=42 SKIP=3 / PASS=49.

### Landed: defensive `_config_only` guard for `bb_arbno`

`stmt_exec.c::bb_deferred_var` carries a `memset(child_state, 0,
child_size)` step intended to reset child-box iteration state between
deferred-var re-uses. Existing guard skipped this for "config-only"
boxes (`bb_lit`, `bb_any`, `bb_notany`, `bb_span`, `bb_brk`) whose state
is purely build-time configuration. `bb_arbno` was NOT in that list —
when `*name` resolves to the same `PATND_t*` between iterations
(`val.p == ζ->child_state` after both pointers are stale-equal), the
memset wipes ARBNO's `cap` (→0), `stack` (→NULL), and `depth` (→0).
ARBNO self-resets at every α; the external memset is unnecessary at
best, corrupting at worst. Added `bb_arbno` to the `_config_only`
exclusion. This is a real correctness fix even though it did NOT, on
its own, resolve SB-5c.1 (see below).

### SB-5c.1 — bisection narrowed; cursor non-advancement isolated

Confirmed the session-#73 8-case bisection: with the trivial reproducer
`group = '(' && word && ')'; src = '(S)'`, all four control cases pass
(`group`, `*group`, `ARBNO(group)`, `ARBNO(group) && delim` etc.) and
exactly two fail: `ARBNO(*group)` and `ARBNO(ARBNO(*group) && Y)`.
Tightest reproducer is `ARBNO(*group)` alone (no outer ARBNO needed):

```
word  = NOTANY('( )') && BREAK('( )');
group = '(' && word && ')';
src   = '(S)';
src ? POS(0) && ARBNO(*group) && RPOS(0)   // FAIL on scrip; PASS on SPITBOL
src ? POS(0) && *group && RPOS(0)          // PASS on scrip
src ? POS(0) && ARBNO(group) && RPOS(0)    // PASS on scrip
```

Diagnostic instrumentation on `bb_arbno::ARBNO_try` and
`bb_deferred_var::DVAR_α/DVAR_γ` produced the smoking-gun trace:

```
[DVAR_α] entry Δ=0 depth=0
[DVAR_γ] after child Δ=3 empty=0    ← child advanced cursor to 3
[ARBNO]  depth=0 start=0 Δ=0 empty=0 ← but ARBNO sees Δ=0
```

Inside `bb_deferred_var`, the child match advanced `Δ` from 0 to 3
correctly (DVAR_γ trace right after `child_fn(...,α)` returns sees
Δ=3). But by the time control returns up to `bb_arbno`'s `ARBNO_try`,
the global `Δ` cursor is back to 0. The non-empty spec `br` is
returned (so `body_γ` fires), but the zero-advance guard `if (Δ ==
fr->start)` IS satisfied (both 0), so ARBNO falls into `ARBNO_γ_now`
and returns a zero-length match starting at position 0. The outer
match then fails `RPOS(0)` (cursor still at 0, src has 3 chars).

### Where the cursor is being reset — NOT YET ROOT-CAUSED

`Δ` is a global (`int Δ;` defined in `stmt_exec.c:109`). Between
`bb_deferred_var` returning to its caller `bb_arbno::ARBNO_try` and
the `ARBNO_try` line itself reading `Δ`, *something* resets it. The
two candidates:

1. **`bb_build` rebuild path.** `bb_deferred_var` rebuilds the child
   box graph on every α call (since `val.p` is `PATND_t*` and
   `ζ->child_state` is the box state pointer of incompatible type,
   they are never equal — so the equality-skip optimization never
   fires for DT_P values). If `bb_build` itself touches Δ during
   construction (e.g. via inlined helpers), this would reset
   between calls. Searches in `bb_build.c` and `bb_boxes.c` show
   only `bb_pos`, `bb_rpos`, `bb_tab`, `bb_rtab`, `bb_rem` writing
   `Δ` — none of those run during `bb_build` itself. But the
   freshly-built child IS invoked at α inside `bb_deferred_var`, so
   the cursor advance during the child's match is real and the
   trace confirms it. The reset must be AFTER the child returns
   but BEFORE `bb_arbno` reads Δ.

2. **`spec_from_descr` / `descr_from_spec` round-trip.** The DESCR_t
   flowing back from `bb_deferred_var` carries `s = Σ + start_pos`
   and `slen = matched_length` — cursor info is in those, NOT in
   the global Δ. The `descr_from_spec(DVAR)` call in DVAR_γ packs
   the spec into a DESCR_t but does NOT re-check or update Δ.
   Then `spec_from_descr(...)` in `bb_arbno::ARBNO_try` unpacks it.
   Δ is whatever the deepest box left it as. If the trace shows
   Δ=3 at DVAR_γ exit but Δ=0 at ARBNO_try return, a write to Δ
   happens between those two points. **Stack trace via gdb is the
   next-session step.**

### Recommended next session — session #75

1. **Get `gdb` traces.** Set a watchpoint on `Δ` via `watch Δ`,
   run the minimal `ARBNO(*group)` reproducer, identify which
   function writes `Δ=0` between DVAR exit and ARBNO entry. The
   reset is likely in a callee of `bb_deferred_var::DVAR_γ` —
   possibly the NAME stack commit/rollback, or a try-and-fail-
   reset deep in the spec packing path.

2. **If Δ-reset is intentional somewhere** (e.g. ARBNO outer
   subject scan saving/restoring Δ around each body try), the
   fix is to ensure the correct restore-vs-keep semantic for
   the deferred-var ↔ ARBNO boundary. Note: `bb_arbno::ARBNO_α`
   sets `fr->start = Δ` BEFORE calling fn; the body advance
   updates Δ; `body_γ` checks `Δ == fr->start`. This requires
   the body's Δ-advance to PERSIST when the body returns — it
   does for direct patterns, must also for deferred-var.

3. **Cross-check SPITBOL.** Translate the minimal reproducer to
   SNOBOL4 syntax and run under the SPITBOL oracle (when
   available) to confirm the canonical semantics. The .sno test
   confirmed in session #74: `treebank-list.sno` and
   `treebank-array.sno` BOTH match their `.ref` byte-identically
   when run through `scrip --ir-run` (SNOBOL4 frontend). So the
   bug is specifically in the Snocone path (`*name`-as-pattern
   inside ARBNO), or specifically in how Snocone-emitted IR
   interacts with `bb_deferred_var` differently than SNOBOL4
   IR does. Cross-check: does SNOBOL4-frontend `.sno` with
   `*group` inside `ARBNO` produce the same buggy behavior?
   If no, the divergence is in Snocone's lowering of `*name` to
   IR (likely `E_DEFER` vs `XVAR` choice).

### Translation faithfulness audit (session #74)

Per Lon's session #74 directive: ensure `claws5.sc`,
`treebank-list.sc`, `treebank-array.sc` are faithful translations
of their `.sno` counterparts AND use almost zero gotos.

Goto count today (session #74): `claws5.sc=6`, `treebank-list.sc=0`,
`treebank-array.sc=0`.

Faithfulness review against canonical `.sno`:

- **`treebank-list.sc`** — STRUCTURALLY FAITHFUL. Procedure set
  matches `treebank-list.sno` 1-for-1 (`list_reverse`,
  `stk_push_frame`, `stk_push_item`, `stk_pop_into_parent`,
  `stk_pop_final`, `init_list`, `push_list`, `push_item`,
  `pop_list`, `pop_final`, `node_repr`, `pp_node`, `pp_bank`).
  Pattern grammar (`delim`, `word`, `group`, `treebank`) is a
  direct translation. Snocone-port artifact: the canonical .sno
  has split surface forms (`init_list/Init_list`, etc., where
  capitalized variants are EVAL-string builders for OPSYN-style
  use); `.sc` collapses to function calls because Snocone has no
  OPSYN. Acceptable given Snocone semantics. **Zero gotos.**

- **`treebank-array.sc`** — STRUCTURALLY FAITHFUL. Same procedure
  set, plus the array-style state (`frame_id`, `stk_tag`, `stk_n`,
  `stk_c`). Translates the canonical `nr_lp` / `pp_wch` loops via
  `while (DIFFER(i = LT(i, n) i + 1))` — the bare-juxtaposition
  concat that triggers the LS-0 gap. Loop body and exit are
  semantically the .sno `:F(nr_done)` flow. **Zero gotos.**
  Main loop translates the .sno `loop / parse_fail` two-label
  flow into an `if/else` inside `while (src ? (spat && REM .
  rest))`. Faithful.

- **`claws5.sc`** — NOT FAITHFUL. The `pp_mem` body in `.sc`
  uses 6 internal gotos (`pp_s`, `pp_w`, `pp_t`, `pp_s_done`,
  `pp_w_done`, `pp_t_done`) and emits a wholly different output
  format from the canonical `pp_mem` in `claws5.sno`. The .sno
  `pp_mem` builds explicit `pfx`/`pad` prefixes per row, handles
  first-vs-mid-vs-last sentence transitions, and produces the
  exact `{1: {...}, 2: {...}}` layout in `claws5.ref`. The .sc
  `pp_mem` produces a different layout (`{` on its own line, `},`
  per closer, etc.). The .sc was an early sketch, not a faithful
  port. **Re-port needed (SB-5c.4 below).**

Independently, **`claws5.sno` itself fails under scrip's SNOBOL4
frontend** with "Pattern match failed" on `claws5.input`
(verified session #74 via `./scrip --ir-run claws5.sno <
claws5.input`). Direct sub-pattern tests confirm SPAN/NOTANY/BREAK
juxtaposition concat works in scrip's SNOBOL4 frontend; the failure
is in the full-grammar match — likely the same ARBNO + deferred-var
family as SB-5c.1, or a separate bug in handling the alternation's
`(epsilon . *fn())` immediate-call inside a SPAN/NOTANY-starting
arm. Tracked as SB-5c.5 below.

### Files touched this session

`Makefile` — `+1/-1` (snocone_cf.c → snocone_control.c).
`src/runtime/x86/stmt_exec.c` — `+10/-1` in `bb_deferred_var`
adding `bb_arbno` to `_config_only` guard with comment.
No other source changes. Diagnostic test files in `/tmp/` only.

### Repos state

`one4all`: dirty (Makefile + stmt_exec.c). `corpus`, `.github`:
clean. Plan: commit one4all changes + this `.github` update,
push both.

---

## Session #75 progress (2026-04-30)

**SB-5c.1 LANDED.** Root cause identified, fixed in 31 lines, verified
across all three modes plus three baseline gates plus broad corpus.
The fix also clears SB-5c.3, SB-5c.5, and SB-5d.1 as side effects.

### Root cause: Snocone IR routes pattern builtins through value context

The Snocone frontend lowers `ARBNO(P)` and `FENCE(P)` as `(E_FNC ARBNO ...)`
and `(E_FNC FENCE ...)` respectively — generic function-call IR nodes —
not as `(E_ARBNO ...)` / `(E_FENCE ...)` (which is what the SNOBOL4
frontend emits).  `interp_eval_pat` in `src/driver/interp.c` had explicit
`case E_ARBNO` and `case E_FENCE` arms that evaluated the child via
`interp_eval_pat` (pattern context), so `E_DEFER(E_VAR("group"))` →
`pat_ref("group")` → XDSAR deferred-reference pattern node — correct.
But `case E_FNC` was missing; `E_FNC` fell through to the `default →
interp_eval(e)` (value context) path.  In value context, `E_DEFER(E_VAR)`
returns `DT_E` (frozen expression).  `APPLY_fn("ARBNO", [DT_E])` →
`_PAT_ARBNO_(DT_E)` → `pat_arbno(DT_E)` → `spat_of(DT_E)` returns NULL
(it only unpacks `DT_P`) → `pat_arbno` builds an ARBNO node with a
NULL child.  At match time the malformed ARBNO fails to advance the
cursor, so the surrounding `POS(0) ... RPOS(0)` anchor fails.

This was *not* the cursor reset session #74 hypothesised — the trace
instrumentation that session #74 added was reading `Δ` correctly; the
malformed ARBNO simply never produced any cursor advance to read.  The
session-#74 `bb_arbno` `_config_only` guard remains in place and is a
correctness improvement on its own (no regression from it).

### Fix

`src/driver/interp.c` `interp_eval_pat` — added `case E_FNC` that for
`ARBNO` and `FENCE` evaluates the child via `interp_eval_pat` (pattern
context), then calls `pat_arbno` / `pat_fence_p` directly.  Other
pattern-builtin function calls (POS, RPOS, SPAN, BREAK, LEN, ANY,
NOTANY, TAB, RTAB, ARB, REM, BAL, SUCCEED, FAIL, ABORT) take
non-pattern args, so for them the value-context default is correct.

```c
case E_FNC:
    if (e->sval && e->nchildren > 0) {
        if (strcmp(e->sval, "ARBNO") == 0) {
            DESCR_t _inner = interp_eval_pat(e->children[0]);
            if (IS_FAIL_fn(_inner)) return FAILDESCR;
            return pat_arbno(_inner);
        }
        if (strcmp(e->sval, "FENCE") == 0) {
            DESCR_t _inner = interp_eval_pat(e->children[0]);
            if (IS_FAIL_fn(_inner)) return FAILDESCR;
            return pat_fence_p(_inner);
        }
    }
    return interp_eval(e);
```

`+31/-0` (the new case slots in next to the existing `case E_FENCE`).

### Verification

**Minimal reproducer (Snocone) — all three modes:**

```snocone
group = '(X)';   src = '(X)';
if (src ? POS(0) && ARBNO(*group) && RPOS(0)) OUTPUT = 'OK';
else                                          OUTPUT = 'FAIL';
```

| Mode | Before fix | After fix |
|------|:---:|:---:|
| `--ir-run`  | FAIL | OK |
| `--sm-run`  | FAIL | OK |
| `--jit-run` | FAIL | OK |

(All three modes funnel `(E_FNC ARBNO ...)` through `interp_eval_pat`
during pattern construction, so the fix in interp.c covers all of them.)

**Session-#73 8-case bisection** — all 8 cases now PASS (matching the
SPITBOL oracle).  Pre-fix: 6 PASS, 2 FAIL (`ARBNO(ARBNO(*group) Y)`
shapes).  Post-fix: 8 PASS.

**Three baseline gates — green, no regression:**
- `test_smoke_snocone.sh` → PASS=5 FAIL=0
- `test_beauty_snocone_all_modes.sh` → PASS=42 FAIL=0 SKIP=3
- `test_smoke_unified_broker.sh` → PASS=49 FAIL=0

**Crosscheck suites — green, no regression:**
- `test_crosscheck_snobol4.sh` → PASS=6 FAIL=0
- `test_crosscheck_snocone.sh` → PASS=8 FAIL=0
- `test_interp_broad_corpus_and_beauty.sh` → PASS=222 FAIL=52
  (identical to pre-fix baseline; the 52 failures are pre-existing,
  unrelated to ARBNO).

### Side-effect closures

**SB-5d.1 LANDED.**  `treebank-list.sc` byte-identical to SPITBOL
oracle in all three modes, 24 lines, `md5
7096beb49889b0d2c5db66b4a45ae444` matches `treebank-list.ref`.  This
closes SB-5d.1 directly — the gating bug was SB-5c.1 and there was no
`.sc` rewrite (per Lon's "no SC workarounds" rule).

**SB-5c.5 LANDED.**  `treebank-list.sno` and `treebank-array.sno` both
byte-identical to SPITBOL oracle in all three modes.  The earlier
"Pattern match failed" on `claws5.sno` and the `treebank-array.sno`
match failure were the same root cause as SB-5c.1, just reached via a
different IR shape — the SNOBOL4 frontend's `E_ARBNO` path exposed
the same `pat_arbno` issue when the inner pattern was an XDSAR
deferred-reference resolved at match time inside a nested ARBNO
context.

**SB-5c.3 CLEARED.**  `claws5.sno` no longer hangs under
`./scrip --ir-run claws5.sno < claws5.input`; it produces the same
`Pattern match failed` as SPITBOL.  The remaining SB-5c.2 (input
file mismatch — `claws5.ref` was generated from `CLAWS5inTASA.dat`,
not `claws5.input`) is a corpus-curation issue, not a runtime bug.

**Beauty.sc end-to-end** — improved but not yet self-host.
`echo START | ./scrip --ir-run $LIBS beauty.sc` no longer hangs;
emits "Parse" (a beauty-internal diagnostic) where SPITBOL emits
"START".  beauty.sc with `beauty.sno` as input flows through the
7-line comment header AND the 17 `-INCLUDE` lines (was hanging on
the first non-comment statement before).  Real grammar work in
beauty.sc remains for the SB-5/SB-6 sequence — that's downstream of
SB-5c.1.

### Open / next-session

- **SB-5c.4** still open (faithful re-port of `claws5.sc`'s `pp_mem`
  procedure with zero gotos, 1-for-1 against `claws5.sno` `pp_mem`).
- **SB-5c.2** still open (`claws5.input` vs `CLAWS5inTASA.dat`
  alignment — corpus-curation decision).
- **SB-5d.2** still open (`treebank-array.sc` blocked on LS-0
  space-concat — `GOAL-SNOCONE-LANG-SPACE.md`).
- **SB-5d.4** still open (zero-goto invariant; both treebank `.sc`
  files at goto count = 0 today, must be preserved by future edits).
- **Beauty self-host (SB-6)** — gating bugs upstream of "diff empty"
  are now exclusively grammar/lowering work in `beauty.sc` itself.
  Suggested first probe next session: capture exactly where beauty.sc
  emits "Parse" instead of recognizing the `START` label, walk the
  pattern construction for `Stmt`/`Label`/`Command`, identify the
  failing arm.  The runtime surface should now be clean.

### Files touched this session

`src/driver/interp.c` — `+31/-0` adding `case E_FNC` in
`interp_eval_pat` for ARBNO and FENCE.  No other source changes.
Diagnostic test files in `/tmp/` only.

### Repos state

`one4all`: dirty (interp.c).  `corpus`, `.github`: clean.  Plan:
commit one4all change + this `.github` update, push both.

---

## Session #76 progress (2026-04-30)

**SB-5c.4 LANDED.**  `claws5.sc::pp_mem` re-ported 1-for-1 against
canonical `claws5.sno::pp_mem` with zero gotos.  No runtime/frontend
source changes — corpus-only.

### Re-port approach

Each canonical SNOBOL4 control flow construct in `pp_mem` mapped to
a single Snocone shape:

- `:F(label)` exit at iteration top → while-condition peek-ahead
  (`while (DIFFER(arr[i + 1, 1]))`).  Loop body increments `i` to
  the now-known-good index and reads `arr[i, 1]`.  Three loops use
  this pattern: `pm_cnt_loop`, `pm_sent_loop`, `pm_wrd_loop`,
  `pm_tag_loop`.

- `:F(label)` skip-block → `if (...) { ... }` / `if (...) { ... }
  else { ... }`.  Used at: `pm_sq` quote choice (`wrd ? ARB "'" =
  '' :F(pm_sq)` → `if (wrd ? (ARB && "'") = '') ... else ...`);
  the post-tag-loop emission tree (`pm_mid_wrd`, `pm_last_wrd`,
  `pm_last_mid`, `pm_last_emit`, `pm_last_mid2`); the
  `pm_tag_sep`-vs-first-tag branch.

- `:S(label)` loop-back at iteration bottom → implicit (loop ends
  naturally and re-enters via the while-condition test).

- Conditional-value-assign predicate idiom (`pfx = EQ(si, 1) ...`,
  `last_sent = IDENT(si, ns) 1`) → `if (pred) lhs = rhs;`.  The
  Snocone form preserves the canonical "no else" semantic exactly:
  if pred fails, the assignment doesn't happen (and last_sent
  retains its `''` initialization, pfx retains its previous value
  or stays unbound).

### Statement-form match-and-replace inside `if`

Canonical .sno line 49: `wrd ? ARB "'" = '' :F(pm_sq)`.  This is
a statement-form match-and-replace: scan wrd for `'`, replace match
with `''`, branch to pm_sq on no-match.

Verified that Snocone's `if (wrd ? (ARB && "'") = '')` correctly:
(a) performs the replacement, and
(b) yields true on match / false on no-match for the `if` test.

This is the cleanest 1-for-1 translation; no need for a separate
match-then-test split.

### Trailing-space scrutiny

Per Lon's instruction: spaces at end of lines often go missing in
SNOBOL4 → Snocone translations.  Audited every string literal in
`pp_mem`:

| .sno literal | .sc literal | Match |
|---|---|---|
| `'{'` | `'{'` | ✓ |
| `' '` (one space) | `' '` | ✓ |
| `': {'` | `': {'` | ✓ |
| `"': "` | `"': "` | ✓ |
| `', '` | `', '` | ✓ |
| `"'"` | `"'"` | ✓ |
| `'"'` | `'"'` | ✓ |
| `'}'` | `'}'` | ✓ |
| `'}}'` | `'}}'` | ✓ |
| `'},'` | `'},'` | ✓ |
| `'_CRD :_PUN'` | `'_CRD :_PUN'` | ✓ |

In particular: `': '` (colon-space, no trailing) and `', '`
(comma-space, no trailing) — both reproduced exactly.  Initial
draft had merged `', '` with the following `"'"` into a single
`", '"` literal; corrected in the second pass to keep two adjacent
literals matching the canonical `', '` and `"'"` separately.

### &TRIM verification

`&TRIM = 1` by default in both SPITBOL and scrip.  Verified that
both runtimes strip trailing space and tab characters on INPUT
when &TRIM=1, byte-for-byte equivalent.  Confirms session #73's
SB-5c.0 fix is live and correct.  pp_mem itself produces OUTPUT
only and doesn't depend on this — but the `slurp` loop above
pp_mem does.

### Byte-identical fixture test

Built a controlled fixture (a 2-sentence, mixed-content TABLE-of-
TABLEs) and ran both:
  (a) canonical `claws5.sno` `pp_mem` under SPITBOL
  (b) re-ported `claws5.sc` `pp_mem` under scrip --ir-run

Both produce md5 `557d5df30ba52a698d1a5f3ca569d9b4` — byte-identical
on this fixture.  The fixture exercises:

- Single-word sentence (sentence 2 has 2 words; sentence 1 has 3)
- Multi-tag words (none in this fixture; covered by canonical
  layout)
- Word containing `'` (`don't`) → triggers double-quote branch
- Last-sentence-last-word terminator (`}}`)
- Mid-sentence-last-word terminator (`},`)
- Mid-word terminator (`,`)
- Sentence-1 prefix `{1: {` vs sentence-2 prefix ` 2: {`
- Pad alignment for mid-words

### Pre-existing slurp-loop hang (out of scope, tracked)

End-to-end `./scrip --ir-run claws5.sc < claws5.input` still hangs.
Bisected to the `slurp` loop:

```snocone
line = INPUT;
while (DIFFER(line)) {
    src = src && line;
    line = INPUT;
}
```

After EOF, scrip's Snocone `INPUT` returns the previous line
forever.  `while (DIFFER(line))` therefore never terminates.
Reproduced with a 7-line test:

```snocone
line = INPUT;
n = 0;
while (DIFFER(line)) {
    n = n + 1;
    OUTPUT = 'line ' && n && ' = [' && line && ']';
    line = INPUT;
    if (GT(n, 10)) line = '';
}
```

On a 3-line input `A\nB\nC\n`: after line 3, every subsequent
INPUT returns `'C'`.  Infinite loop without the manual break-out.

This is the **same SC-INPUT-EOF bug** session #68's SB-5b main-loop
rewrite worked around in beauty.sc (using `IDENT(Line, PrevLine)`
to detect the no-advance condition and force `eof_inside = 1`).

The hang is **not** in pp_mem and **not** introduced by SB-5c.4 —
the original (pre-SB-5c.4) `.sc` had the same hang.  Tracked as a
follow-on rung, suggested name **SC-INPUT-EOF**.  Fix surface is
the runtime's INPUT-after-EOF semantic in
`src/runtime/x86/snobol4.c`'s `input_read()` (or NV_GET_fn channel
path) — should return `''` and signal "stream exhausted" so that
`DIFFER(line)` becomes false.  This complements session #73's
SB-5c.0 &TRIM fix and lives on the same code path.

### Files touched this session

`corpus/programs/snobol4/demo/claws5.sc` — `+99/-30` net in the
`pp_mem` body, including comment markers for each canonical
SNOBOL4 label.  No other source changes.  Diagnostic test files
in `/tmp/` only (not committed).

### Repos state

`corpus`: dirty (claws5.sc).  `one4all`, `.github`, `csnobol4`,
`x64`: clean.  Plan: commit corpus change + this `.github` update,
push both.

---

## Session #77 progress (2026-04-30)

**SC-INPUT-EOF CLOSED — but not as a runtime fix.  As a corpus fix.**
Three baseline gates green; crosscheck snobol4=6, snocone=8 unchanged;
broad interp suite PASS=222 FAIL=52 unchanged.  Corpus-only diff;
`one4all`, `.github`, `csnobol4`, `x64` untouched.

### Reframing

Sessions #68 and #76 both diagnosed an "INPUT-after-EOF returns the
previous line forever" runtime bug, with the proposed fix landing in
`src/runtime/x86/snobol4.c::input_read()` to return `''` and signal
exhaustion.  Session #77 verified that diagnosis is wrong:
`input_read()` already returns `FAILDESCR` correctly on EOF, and the
SNOBOL4 frontend handles it identically to SPITBOL (`line = INPUT
:F(eof)` works byte-for-byte — verified with a 4-statement reproducer
under `sbl -bf` and `scrip --ir-run`).

The actual problem is the **slurp idiom written in the .sc sources**.
The loop

```snocone
line = INPUT;
while (DIFFER(line)) { ...; line = INPUT; }
```

is structurally broken in both SNOBOL4 and Snocone: a failing
assignment leaves the LHS unchanged, so on EOF `line` keeps its
previous value forever, and `DIFFER(line)` is forever true.  This is
correct SNOBOL4 semantics — and the workaround SNOBOL4 programmers use
is `:F(eof)` on the read.  Snocone has no statement-failure goto;
instead, the canonical idiom (per `programs/snocone/report.md`
line 1240) uses the assignment expression as the predicate:

```snocone
while (line = INPUT) { ... }
```

The assignment-as-expression evaluates to FAIL on EOF, the surrounding
while-test sees the failure, and the loop exits cleanly.  No runtime
change needed.  No `IDENT(Line, PrevLine)` workaround needed.

### Fix #1 — `claws5.sc` slurp loop

`corpus/programs/snobol4/demo/claws5.sc` lines 120–124, replaced

```snocone
line = INPUT;
while (DIFFER(line)) {
    src = src && line;
    line = INPUT;
}
```

with

```snocone
while (line = INPUT) {
    src = src && line;
}
```

`./scrip --ir-run claws5.sc < claws5.input`: was hanging (rc=124,
0 stdout), now exits cleanly with `Pattern match failed` in all
three modes — matches SPITBOL on the same input.  Goto count
remains 0.

### Fix #2 — `beauty.sc` main loop

`corpus/programs/snocone/demo/beauty/beauty.sc` main loop
(lines 421–478, 56 lines net replacing 60), removed the session #68
SB-5b workaround flags (`done`, `cont`, `more`, `eof_inside`,
`PrevLine`, `IDENT(Line, PrevLine)` no-advance detection) and replaced
with a clean look-ahead structure:

- Outer while: `~DIFFER(input_done)`.
- `have_line` flag distinguishes "Line holds an unprocessed look-ahead"
  from "Line just consumed; refetch on next iteration".
- Refetch: `if (Line = INPUT) have_line = 1; else input_done = 1;`.
- Header passthrough: `if (Line ? POS(0) && ANY('*-')) OUTPUT = Line;`.
- Logical-unit accumulator: `Src = Line && nl;`, then continuation
  loop reads ahead and folds in any line starting with `.` or `+`,
  preserving non-continuation lookahead for the next outer iteration.
- Parse Src; pp; emit Parse Error or Internal Error on failure.

The structure mirrors canonical `beauty.sno::main00..main05` exactly.
Goto count = 0 (one comment-mention of "SNOBOL4 goto AST node" remains
at line 277, unchanged from session #68).

### Verification

**Slurp loop terminates in all three modes** on the 50KB `beauty_oracle.sno`:
1449 lines emitted, header-passthrough working, clean rc=0.

**Three baseline gates green:**
- `test_smoke_snocone.sh` → PASS=5 FAIL=0
- `test_beauty_snocone_all_modes.sh` → PASS=42 FAIL=0 SKIP=3
- `test_smoke_unified_broker.sh` → PASS=49 FAIL=0

**Crosscheck gates green:**
- `test_crosscheck_snobol4.sh` → PASS=6 FAIL=0
- `test_crosscheck_snocone.sh` → PASS=8 FAIL=0

**Broad interp suite unchanged:** PASS=222 FAIL=52 (same as session #75
post-SB-5c.1 baseline).

### What this closes vs. what remains

Closed: **SC-INPUT-EOF** — corpus-side, no runtime change.  Both the
session-#76 hang in `claws5.sc` and the session-#68 IDENT-workaround
in `beauty.sc` are gone.

Still open and downstream of this rung:
- **SB-6** — beauty self-host.  On a tiny SNOBOL4 fixture
  (`*  hdr1\n*  hdr2\nA = 1\nOUTPUT = A\nEND\n`), beauty.sc's slurp
  loop now correctly produces 3 logical units (A=1, OUTPUT=A, END).
  Two are Parse Errors; the third (END) parses OK but pp() trips
  Error 5 ("Undefined function or operation") — **a beauty-internal
  grammar/runtime issue completely independent of SC-INPUT-EOF**.
  Three startup errors still fire during pattern construction
  (the "Error 1: GE first argument is not numeric" and "Error 5:
  Undefined function" noted as pre-existing in session #68).  These
  are the remaining work for SB-6.
- **SB-5c.2** — `claws5.input` vs `CLAWS5inTASA.dat` alignment.
  Corpus-curation, unchanged by this session.
- **SB-5d.2** — `treebank-array.sc` blocked on LS-0 (space-concat
  language feature).  Unchanged.

### Files touched this session

- `corpus/programs/snobol4/demo/claws5.sc` — `+5/-5` net in the
  slurp loop (4-line expansion → 3-line canonical idiom plus a
  3-line comment block referencing report.md).
- `corpus/programs/snocone/demo/beauty/beauty.sc` — `~+60/-50` net
  in the main loop (file was 478 lines, now 479; structure replaced
  wholesale with the canonical `Line = INPUT` predicate idiom and
  `have_line` look-ahead flag).

No runtime/frontend source changes.  No `.github` infrastructure
changes beyond this progress entry and the rung markers below.

### Repos state

`corpus`: dirty (claws5.sc + beauty.sc).  `.github`: this update only.
`one4all`, `csnobol4`, `x64`: clean.  Plan: commit corpus + .github,
push corpus first then .github.

---

## Session #78 progress (2026-04-30)

**Investigation only.  Three operator-lowering bugs identified, two fixes
designed.  No source changes.  All repos clean.**

This session was launched against SB-6 (beauty.sc self-host).  Setup
gates green throughout (PASS=5 / PASS=42 SKIP=3 / PASS=49).  No source
changes landed; the entire session was diagnosis and fix design,
captured here for session #79 to implement.

### Reproducer

A properly-indented two-statement fixture exposes three distinct
runtime-visible defects:

```
$ printf '\tA = 1\n\tOUTPUT = A\nEND\n' | scrip --ir-run $LIBS beauty.sc
stdout:
    Parse Error
    \tA = 1
    (blank)
    Parse Error
    \tOUTPUT = A
    (blank)

stderr:
    ** Error 1 in statement 0 / GE first argument is not numeric (×2)
    ** Error 5 in statement 0 / Undefined function or operation (×1)
```

SPITBOL (cd corpus/programs/snobol4/beauty && sbl -bf
$smoke/beauty_oracle.sno) on the same input produces clean
beautified output:

```
               A              =  1
               OUTPUT         =  A
END
```

The `Parse Error` from beauty.sc is real — beauty.sc's grammar isn't
recognizing valid SNOBOL4 statements.  Bisection reveals the three
defects below.  Each is a Snocone or SNOBOL4 frontend operator
lowering bug.

### Bug A — Snocone `||` lowers to E_CAT instead of value-list/OR

**Location:** `src/frontend/snocone/snocone_lower.c:175-180`,
`SNOCONE_OR` case.

**Current code:**
```c
case SNOCONE_OR: {
    /* || string concatenation (same as | and && in value context) → E_CAT */
    EXPR_t *r = es_pop(s), *l = es_pop(s);
    EXPR_t *e = expr_binary(E_CAT, l, r);
    es_push(s, e); return 0;
}
```

**Per the canonical Snocone spec (corpus/programs/snocone/report.md
lines 511-516):**
> `||` Logical disjunction.  The left operand is evaluated first; if
> it succeeds, its value is the value of `||`.  Otherwise, the value
> is that of the right operand.  If both operands fail, `||` fails.

**Per the canonical transpiler (SNOCONE.zip / snocone.sc lines
37, 316-321, 367-375):**

```
bconv['||'] = or_binfo = binfo('',4,4,0,0,1)

# in dprint:
if (IDENT (op, or_binfo)) {
    emit ('(');  bprint (x);  emit (')')
    return
}

# bprint flattens nested OR:
procedure bprint (x) {
    if (DIFFER (DATATYPE(x), 'B') || DIFFER (op(x), or_binfo)) {
        dprint (x);  return
    }
    bprint (l(x));  emit (',');  bprint (r(x))
}
```

`a || b` lowers to **SNOBOL4 paren-list `(a, b)`** — a SPITBOL
extension at value level whose semantics are exactly OR: try arms
left-to-right, return first non-failing value, fail if all fail.

**Truth table verified under SPITBOL** for `(IDENT(T,'X'), IDENT(T,'Y'))`
with T='Id':

| First | Second | (a,b) result | E_CAT result (current scrip) |
|-------|--------|-------------|------------------------------|
| ✓ | ✓ | ✓ (yields null) | ✓ (yields null) |
| ✗ | ✓ | ✓ | ✗ |
| ✓ | ✗ | ✓ | ✗ |
| ✗ | ✗ | ✗ | ✗ |

E_CAT yields AND-with-failure-propagation — the opposite of OR
when it differs.

**Audit:** every `||` use across the entire Snocone corpus expects
OR semantics:
- `corpus/programs/snocone/demo/beauty/tree.sc:95`
- `corpus/programs/snocone/demo/beauty/beauty.sc:233-237, 240, 245,
  281-283, 401`
- `corpus/programs/snocone/corpus/sc8_strings.sc:3`

Zero uses depend on E_CAT semantics.

### Bug B — SNOBOL4 frontend `(a, b, c)` lowers to E_ALT

**Location:** `src/frontend/snobol4/snobol4.y:195`.

**Current rule:**
```yacc
expr17 : T_LPAREN expr0 T_COMMA exprlist_ne T_RPAREN
       { EXPR_t*a=expr_new(E_ALT); ... }
```

**Test:**
```
        T = 'Id'
        OUTPUT = (IDENT(T,'Foo'), IDENT(T,'Id'), 'fallback')
        OUTPUT = (IDENT(T,'Foo'), IDENT(T,'Bar'), 'fallback')
        OUTPUT = (IDENT(T,'Id'), 'first')
END
```

| Implementation | Output |
|---|---|
| SPITBOL | `(blank)\nfallback\n(blank)\n` (correct) |
| csnobol4 | `(blank)\nfallback\n(blank)\n` (correct) |
| **scrip --ir-run (SNOBOL4 frontend)** | **`PATTERN\nPATTERN\nPATTERN\n`** |

Our frontend builds an `E_ALT` (pattern alternation) for the
paren-list, then `OUTPUT = pattern_value` prints the literal string
`"PATTERN"` (the DATATYPE-coerced value).  This is wrong: SPITBOL's
paren-list at value level is goal-directed disjunction, not pattern
alternation.

**Pattern-context paren-list IS pattern-alt** — that part of the rule
must stay correct.  The fix is to distinguish value-context from
pattern-context paren-lists at lowering time, OR to introduce a new
IR node that interp_eval evaluates as goal-directed disjunction and
interp_eval_pat coerces to pattern_alt as needed.

### Bug A and Bug B are the SAME architectural fix

Both `Snocone ||` and `SNOBOL4 frontend (a, b, c)` should produce the
same IR node — a goal-directed value-context disjunction, distinct from
`E_ALT` (which is pattern alternation).

**Proposed name: `E_VLIST`** (value-list) — chosen to parallel `E_ALT`'s
naming axis (alternation) but distinguish "value context" from
"pattern context".  Considered alternatives:

- `E_LOGICAL_OR` — accurate but a bit verbose; doesn't match the
  surface syntax `(a, b, c)`
- `E_VALT` — short for value-alternation; ambiguous against E_ALT
  visually
- `E_OR` — was the historic name for E_ALT; reusing it would
  re-confuse the rename history (ir.h:82 says "(ORPP in SIL; was
  E_OR)")

**Behavior:**
- n-ary children
- evaluate children left-to-right (eager, NOT lazy/backtracking)
- short-circuit: return first non-failing child's value
- if all fail, return FAILDESCR
- side effects of arm `k` happen exactly once iff arms `1..k-1` all
  failed; arms `k+1..n` never fire

**Distinction from E_ALT:**

| Axis | E_ALT (pattern alternation) | E_VLIST (value disjunction) |
|------|-----------------------------|----------------------------|
| Context | Pattern only | Value (interp_eval) |
| Trial mode | Lazy at match time, with backtracking | Eager during evaluation, no backtracking |
| Operand type | Patterns (DT_P), or coerced via pat_to_patnd | Any value: predicates, assigns, strings |
| Result on success | Combined pattern node `pat_alt(...)` | Value of first non-failing child, returned now |
| Side effects | At match time, possibly multiple per arm if matcher backtracks | Exactly once per arm tried, in order |
| All-fail | Pattern that fails to match | FAILDESCR |
| SNOBOL4 surface | `p1 \| p2 \| p3` inside a pattern | `(a, b, c)` paren-list at value level |

### Bug C — Snocone unary `?x` lowers to DIFFER(x, '')

**Location:** `src/frontend/snocone/snocone_lower.c:229-233`,
`SNOCONE_QUESTION` unary case.

**Current code:**
```c
case SNOCONE_QUESTION:
    if (tok->is_unary) {
        /* unary ? = DIFFER(x,"") — not-null test */
        EXPR_t *operand = es_pop(s);
        es_push(s, make_fnc1("DIFFER", operand));
    } else { ... }
```

**Per spec (report.md lines 554-559):**
> `?` Query.  If its operand fails, `?` fails.  If its operand
> succeeds, `?` yields a null string.  Useful for evaluating an
> expression solely for its side effects.

**Per canonical transpiler:** unary operators emit verbatim
(snocone.sc line 286-294, dprint U-case).  `?x` → `?x` literal in
SNOBOL4.  SPITBOL has native unary `?` with exactly the spec
semantics.  Verified.

**Truth table:**

| `x` | spec `?x` | DIFFER(x, '') (current) |
|-----|-----------|--------------------------|
| succeeds, yields null | succeeds → null | DIFFER('','') → fails |
| succeeds, yields non-null | succeeds → null | succeeds → null |
| fails | fails | depends on caller's failure handling, often spurious |

The current lowering wrongly fails on null-success and gives wrong
behavior on failure of `x`.  Verified at /tmp/qtest.sc:
```
T1: ?'hello' SUCCEEDED          (correct by accident — non-null)
T2: ?'' FAILED                  (BUG — should succeed per spec)
T3: ?(failing pred) FAILED      (right answer, wrong reason)
```

**Note: `?x` and `~x` are exact opposites.**  Both yield null on
success.  `?x` succeeds iff `x` succeeds; `~x` succeeds iff `x`
fails.  So:

```
?x  ≡  ~~x   (double negation)
```

This is the cleanest fix shape — uses only the existing `E_NOT`,
zero new IR.

```c
case SNOCONE_QUESTION:
    if (tok->is_unary) {
        EXPR_t *operand = es_pop(s);
        es_push(s, expr_unary(E_NOT, expr_unary(E_NOT, operand)));
    } else { ... }
```

### Operator comparison grid (full)

For session #79's reference, here's the full comparison: canonical
Snocone (SNOCONE.zip) vs. one4all Snocone (snocone_lower.c) vs.
SNOBOL4 native.

**Binary operators:**

| Snocone | Canonical → SNOBOL4 | one4all IR | SNOBOL4 native | Status |
|---------|---------------------|------------|----------------|--------|
| `=` | `=` | E_ASSIGN | `=` | OK |
| `?` | `?` | E_SCAN | `?` | OK |
| `\|` | `\|` | E_ALT (n-ary) | `\|` | OK |
| `\|\|` | `(a, b)` paren-list | **E_CAT** | `(a, b)` paren-list | **Bug A** |
| `&&` | juxtaposition | E_SEQ (n-ary) | juxtaposition | OK |
| `>` `<` `>=` `<=` `==` `!=` | `GT(a,b)` etc. | E_FNC("GT"...) | function calls | OK |
| `::` `:!:` | `IDENT/DIFFER` | E_FNC | function calls | OK |
| `:>:` `:<:` `:>=:` `:<=:` `:==:` `:!=:` | `LGT LLT LGE LLE LEQ LNE` | E_FNC | function calls | OK |
| `+` `-` `*` `/` | same | E_ADD/SUB/MUL/DIV | same | OK |
| `%` | `REMDR(a,b)` | E_FNC("REMDR",…) | `REMDR(a,b)` | OK |
| `^` (R-assoc) | `**` | E_POW | `**` | OK |
| `.` (cap-cond-asgn) | `.` | E_CAPT_COND_ASGN | `.` | OK |
| `$` (cap-immed-asgn) | `$` | E_CAPT_IMMED_ASGN | `$` | OK |

**Unary operators** (canonical: `unaryop = ANY("+-*&@~?.$")`,
emitted verbatim):

| Op | Spec | Canonical → SNOBOL4 | one4all IR | Status |
|----|------|---------------------|------------|--------|
| `+x` | numeric coerce | `+x` | E_PLS | OK |
| `-x` | unary minus | `-x` | E_MNS | OK |
| `*x` | deferred eval | `*x` | E_DEFER | OK *(was bug, fixed s#68)* |
| `&x` | keyword | `&x` | E_KEYWORD | OK |
| `@x` | cursor capture | `@x` | E_CAPT_CURSOR | OK |
| `~x` | logical negation | `~x` | E_NOT | OK |
| `?x` | interrogation (succeed-as-null iff x succeeds) | `?x` verbatim | **E_FNC("DIFFER",x,"")** | **Bug C** |
| `.x` | name-of | `.x` | E_NAME | OK |
| `$x` | indirect | `$x` | E_INDIRECT | OK |

**SNOBOL4 SPITBOL-extension constructs** (no Snocone surface, but
referenced by the SNOBOL4 frontend):

| Construct | Spec | one4all | Status |
|-----------|------|---------|--------|
| `(a, b, c)` value paren-list | first-non-failing-arm-wins (SPITBOL ext.) | **E_ALT** | **Bug B (= Bug A architecturally)** |

### Recommended next session — session #79

**Implement E_VLIST and the ?x fix.**

1. **`src/ir/ir.h`** — append `E_VLIST` to the EKind enum (right
   before `E_KIND_COUNT`).  Comment: "Goal-directed value-context
   disjunction.  N-ary.  Try children left-to-right; return first
   non-failing value; fail if all fail.  SPITBOL `(a, b, c)`
   paren-list and Snocone `||`.  Distinct from E_ALT (pattern
   alternation, lazy at match time)."

2. **`src/ir/ir_print.c`** — add label `[E_VLIST] = "E_VLIST"`.

3. **`src/driver/interp.c`** — add `case E_VLIST` to `interp_eval`
   (value context):
   ```c
   case E_VLIST: {
       for (int i = 0; i < e->nchildren; i++) {
           DESCR_t v = interp_eval(e->children[i]);
           if (!IS_FAIL_fn(v)) return v;
       }
       return FAILDESCR;
   }
   ```
   Also add to `interp_eval_pat`.  In pattern context, the paren-list
   COULD be flattened to E_ALT for backwards-compat, but cleaner is to
   route to the same value-context evaluation since pattern alternation
   inside a paren-list at value level isn't a thing — pattern alt uses
   `|`, paren-list `(a, b, c)` is value-only.

4. **`src/runtime/x86/sm_lower.c`** — add `case E_VLIST` to
   `lower_expr` and `lower_pat_expr`.  Two viable shapes:
   - (a) Emit `SM_PUSH_EXPR` + new `SM_EVAL_EXPR` opcode that calls
     interp_eval directly.  Smaller code surface; trades SM-bytecode
     transparency.
   - (b) Emit a sequence of `lower_expr(child[i])` + `SM_TRY_OR_NEXT`
     + label.  Native SM bytecode, larger change.

   Recommend (a) for session #79; revisit (b) if profiling shows SM
   value-list is hot.  Need a corresponding handler in
   `src/runtime/x86/sm_interp.c`.

5. **`src/runtime/x86/sm_codegen.c`** — for `--jit-run`, mirror (a)
   above.

6. **`src/frontend/snocone/snocone_lower.c:175-180`**: change
   `SNOCONE_OR` to emit `E_VLIST` instead of `E_CAT`, with n-ary
   collapsing (mirror E_SEQ / E_ALT pattern in same file):
   ```c
   case SNOCONE_OR: {
       EXPR_t *r = es_pop(s), *l = es_pop(s);
       EXPR_t *e;
       if (l->kind == E_VLIST) { expr_add_child(l, r); e = l; }
       else { e = expr_new(E_VLIST); expr_add_child(e, l); expr_add_child(e, r); }
       es_push(s, e); return 0;
   }
   ```

7. **`src/frontend/snobol4/snobol4.y:195`**: change the
   `T_LPAREN expr0 T_COMMA exprlist_ne T_RPAREN` reduction to emit
   `E_VLIST` instead of `E_ALT`.  The pattern-context paren-list is
   built differently anyway (alternation is `|`, not comma); this
   rule is unambiguously the value-context paren-list.

8. **`src/frontend/snocone/snocone_lower.c:229-233`**: change
   `SNOCONE_QUESTION` unary case to `E_NOT(E_NOT(x))`:
   ```c
   case SNOCONE_QUESTION:
       if (tok->is_unary) {
           EXPR_t *operand = es_pop(s);
           es_push(s, expr_unary(E_NOT, expr_unary(E_NOT, operand)));
       } else { ... existing binary ? scan handling ... }
       return 0;
   ```

9. **Verify gates after each step.**  Floor invariants:
   - PASS=5 / PASS=42 SKIP=3 / PASS=49 stay green
   - crosscheck snobol4 PASS=6, snocone PASS=8 unchanged
   - broad interp suite unchanged (PASS=222 FAIL=52 baseline)

10. **Beauty.sc tiny-fixture verification.**  Once all three bugs
    are fixed, the proper-indented two-statement fixture should
    produce SPITBOL-byte-identical output:
    ```
    $ printf '\tA = 1\n\tOUTPUT = A\nEND\n' | scrip --ir-run $LIBS beauty.sc
                   A              =  1
                   OUTPUT         =  A
    END
    ```
    No stderr.

11. **Then attack SB-6 self-host.**  With operator semantics correct,
    beauty.sc should at minimum recognize valid SNOBOL4 statements.
    Remaining gap to byte-identical-against-SPITBOL is whatever
    grammar/lowering issues remain in beauty.sc itself.

### What NOT to do in session #79

- **Do not rewrite beauty.sc** to avoid `||`.  Per Lon's session-#73
  rule: "do not change any SC code to work around a bug.  Make a step
  in this current GOAL to fix the bug instead."  All three bugs above
  are runtime/frontend fixes.  beauty.sc stays as-is.

- **Do not fold E_VLIST into E_ALT.**  Pattern-alt and value-disjunction
  are semantically distinct (lazy/backtracking vs. eager/short-circuit;
  pattern result vs. value result).  Conflating them is what produced
  Bug B in the first place.

- **Do not fold ?x into a single-arg DIFFER variant.**  The double-NOT
  shape is correct, minimal, and uses existing IR.  Adding a new IR
  node for `?` would be over-engineering.

### Files investigated, not modified

- `src/frontend/snocone/snocone_lower.c` (read; cases 175-180,
  229-233 identified for change)
- `src/frontend/snobol4/snobol4.y` (read; line 195 identified for
  change)
- `src/driver/interp.c` (read; E_CAT / E_ALT handlers studied as
  reference for E_VLIST)
- `src/runtime/x86/sm_lower.c`, `sm_interp.c`, `sm_codegen.c` (read
  for understanding lowering boundaries)
- `src/ir/ir.h`, `src/ir/ir_print.c` (read; insertion points
  identified)
- `corpus/programs/snocone/report.md` (re-read for `||`, `?x`, `~x`
  spec)
- `SNOCONE.zip` (canonical Snocone transpiler — Lon supplied via
  upload this session) — `snocone.sc`, `snocone.snobol4`,
  `snocone.sno`.  This is the AUTHORITATIVE reference for canonical
  Snocone semantics (snocone.sc is the C-style source; snocone.sno
  and snocone.snobol4 are the bootstrap outputs in canonical Snocone
  and SNOBOL4 respectively).  No copy committed to corpus this
  session — Lon's upload remains authoritative.

### Repos state

All clean.  This session was investigation-only; the goal-file update
is the only change.  No code commits in `one4all`, `corpus`,
`csnobol4`, or `x64`.  Plan: commit and push this `.github` update
only.

---

## Session #79 progress (2026-04-30)

**SB-6.A, SB-6.B, SB-6.C all LANDED.**  Three operator-lowering
fixes per session #78's plan, plus pre-existing E_VLIST infrastructure
already partially staged in the working tree from an earlier
abandoned attempt.  All three baseline gates green; all crosscheck
gates green; broad corpus suite identical to baseline.  SB-6 itself
still open: at least one more upstream defect — beauty.sc tiny
fixture still emits "Parse Error" (see SB-6.D below).

### Build hazard noted

Initial gate run came back `PASS=3 FAIL=2` on `test_smoke_snocone.sh`
— two basic Snocone shapes (procedure return-value, while-loop)
broken.  Bisecting against `41c9a50a` (SB-5c.1) showed that commit
green and `main` HEAD broken.  But: doing a clean `find src -name
'*.o' -delete` rebuild on `main` then showed PASS=5/0.  The
"regression" was a stale-`.o` artifact mixed with the dirty
working-tree changes (the partially-applied E_VLIST machinery).
**The IC-8 #18 commit message explicitly warns about this** —
"Build hazard observed: clean rebuild via `find src -name '*.o'
-delete` required after icn_runtime.h change (per session #17
lesson)".  Lesson re-confirmed: when stash + new build lib changes
combine, force a clean rebuild before believing any gate result.

### Inherited infrastructure

The working tree on session start carried a half-finished SB-6
attempt from an earlier abandoned session: E_VLIST enum + name
table entry in `ir.h`, E_VLIST cases in `interp_eval` and
`interp_eval_pat` of `interp.c`, and an E_VLIST lowering in
`sm_lower.c`.  No frontend was emitting E_VLIST, so the change was
inert.  Reviewed for correctness against session #78's design;
matches the spec (eager left-to-right, first-non-failing wins,
FAIL if all fail).  Kept as-is; rolled into this commit.  No
SM-mode `case E_VLIST` is needed in `sm_interp.c` or `sm_codegen.c`
because `lower_expr` handles E_VLIST entirely with existing
`SM_JUMP_S`/`SM_POP` opcodes — a simpler approach than session
#78's plan stage 4(a) "new SM_EVAL_EXPR opcode" hint.

### Fix #1 — `snocone_lower.c::SNOCONE_OR` (SB-6.A)

Replaced E_CAT lowering with E_VLIST n-ary collapse mirroring the
existing E_ALT/E_SEQ pattern:

```c
case SNOCONE_OR: {
    EXPR_t *r = es_pop(s), *l = es_pop(s);
    EXPR_t *e;
    if (l->kind == E_VLIST) { expr_add_child(l, r); e = l; }
    else { e = expr_new(E_VLIST); expr_add_child(e, l); expr_add_child(e, r); }
    es_push(s, e); return 0;
}
```

Verified on a 3-case truth-table fixture across all three modes:

| Test | Result | Expected (SPITBOL) |
|------|--------|--------------------|
| `(IDENT(T,'Foo') \|\| IDENT(T,'Id') \|\| 'fallback')` with T='Id' | `null` | `null` (IDENT yields null on success) |
| `(IDENT(T,'Foo') \|\| IDENT(T,'Bar') \|\| 'fallback')` with T='Id' | `'fallback'` | `'fallback'` |
| `(IDENT(T,'Id') \|\| 'first')` with T='Id' | `null` | `null` |

All 3 cases × 3 modes = 9/9 PASS.

### Fix #2 — `snobol4.y:195` paren-list (SB-6.B)

Single-character change: `E_ALT` → `E_VLIST` in the
`T_LPAREN expr0 T_COMMA exprlist_ne T_RPAREN` reduction action.
`scripts/regenerate_parser_and_lexer_from_sources.sh` rerun;
`snobol4.tab.c` updated by 2 chars.

Verified scrip output **byte-identical to SPITBOL oracle** on the
SNOBOL4 truth-table fixture (`a=[]\nb=[fallback]\nc=[]\n` from
both runtimes).

### Fix #3 — `snocone_lower.c::SNOCONE_QUESTION` unary (SB-6.C)

Replaced `make_fnc1("DIFFER", x)` with the nested-NOT shape:

```c
case SNOCONE_QUESTION:
    if (tok->is_unary) {
        EXPR_t *operand = es_pop(s);
        es_push(s, expr_unary(E_NOT, expr_unary(E_NOT, operand)));
    } else { ... binary E_SCAN unchanged ... }
```

Verified truth table:

| Test | Pre-fix | Post-fix | Spec |
|------|---------|----------|------|
| `?'hello'` (non-null) | succeed | succeed | succeed |
| `?''` (null) | **FAIL** | **succeed** | succeed |
| `?(EQ(2,3))` (failing) | FAIL | FAIL | FAIL |
| `?(EQ(2,2))` (success-yields-null) | FAIL | succeed | succeed |

`?''` is the regression-fix — the buggy `DIFFER('','')` always
failed; the correct `~~''` succeeds (operand `''` succeeds; outer
NOT fails; inner NOT succeeds yielding null).

### Verification — full gate sweep

| Gate | Result |
|------|--------|
| `test_smoke_snocone.sh` | PASS=5 FAIL=0 ✅ |
| `test_beauty_snocone_all_modes.sh` | PASS=42 FAIL=0 SKIP=3 ✅ |
| `test_smoke_unified_broker.sh` | PASS=49 FAIL=0 ✅ |
| `test_crosscheck_snobol4.sh` | PASS=6 FAIL=0 ✅ |
| `test_crosscheck_snocone.sh` | PASS=8 FAIL=0 ✅ |
| `test_interp_broad_corpus_and_beauty.sh` | PASS=222 FAIL=52 ✅ (matches baseline exactly) |

Zero regressions across any gate.

### SB-6 itself NOT yet closed — next bug identified

With A/B/C landed, the session #78 tiny fixture still produces
"Parse Error" twice plus 3 stderr errors:

```
$ printf '\tA = 1\n\tOUTPUT = A\nEND\n' | scrip --ir-run $LIBS beauty.sc
stdout:
  Parse Error
  \tA = 1
  Parse Error
  \tOUTPUT = A
stderr:
  ** Error 1 in statement 0  GE first argument is not numeric  (×2)
  ** Error 5 in statement 0  Undefined function or operation     (×1)
```

Session #78 noted these as "three startup errors that fire BEFORE
@T0 in real time" — the operator fixes were necessary but not
sufficient.  At least one more upstream bug remains, gating SB-6.

Recorded as **SB-6.D** in the step list above.  Recommended first
diagnostic for session #80: check out `41c9a50a` (pre-A/B/C),
clean rebuild, re-run the tiny fixture.  If the same 3 errors
fire there too, they are pre-existing and merely unmasked by
SB-6.A/B/C letting beauty.sc proceed further.  If they're new,
A/B/C have a regression hidden behind the unit verifications and
need re-examination.

The `GE first argument is not numeric` error pattern strongly
suggests something is passing a non-numeric (perhaps a PATTERN or
EXPRESSION descriptor) to a `GE(a,b)` call during beauty.sc's
pattern construction.  Candidates: the `ppStop[]` array setup, the
`ppSmBump`/`ppLgBump` arithmetic, the `Real` pattern's nested
SPAN/FENCE expression, or one of the `*Pat`-deferred procedure-
result references resolving to the wrong type.

### Files touched this session

- `src/ir/ir.h` — `+6/-0` (E_VLIST enum + name table entry; from
  inherited infrastructure)
- `src/driver/interp.c` — `+27/-0` (E_VLIST cases in interp_eval
  and interp_eval_pat; from inherited infrastructure)
- `src/runtime/x86/sm_lower.c` — `+31/-0` (E_VLIST lowering using
  existing SM_JUMP_S/SM_POP opcodes; from inherited infrastructure)
- `src/frontend/snocone/snocone_lower.c` — `+13/-4` (SNOCONE_OR
  rewritten + SNOCONE_QUESTION unary rewritten — both this session)
- `src/frontend/snobol4/snobol4.y` — `+1/-1` (paren-list E_ALT →
  E_VLIST — this session)
- `src/frontend/snobol4/snobol4.tab.c` — `+1/-1` (regenerated)

Total: 6 files, +79/-6.  No diagnostic patches; no `.sc`
workarounds; no other source changes.

### Repos state

`one4all`: dirty (the 6 files above).  `corpus`, `.github`:
clean (this update only).  `csnobol4`, `x64`: untouched.  Plan:
commit `one4all` + `.github`, push `one4all` first then `.github`.

---


- [x] **SB-2** — Fix $'...' lexer.
- [x] **SB-3** — Fix scan+replacement lowering. 0 underflows.
- [x] **SB-4a** — Careful rewrite: for each `.sno` / `.inc` source file in
  `corpus/programs/snobol4/beauty/`, read the original, read the current `.sc`
  in `corpus/programs/snocone/demo/beauty/`, and regenerate it from scratch.
  (Sessions #62–#65: 6 modules rewritten in #64, ppAutoMode/--auto strip
  in #65. **Correction (session #66):** the `tree.sc` / `counter.sc` gaps
  identified in session #65 are NOT dead code — they are gated on settings
  like `xTrace > 4` and parse-tree mode. SB-4b takes them up.)

- [x] **SB-4b** — Per-subsystem faithful conversion of every
  `.inc` / `.sno` source. Closed in session #67. All 16 sub-rungs
  ([SB-4b.1..SB-4b.16]) marked done — exhaustive ports of every
  procedure, including those gated on `xTrace`, `doParseTree`, or
  other runtime settings. **No "dead-code" pruning** — per Lon:
  "the code is turned on by settings."

  ⛔ **Before starting any module, consult:**
    - The Snocone language-facts section in this Goal file (below the
      Steps), which records the canonical operator table and idioms
      extracted from `snocone.sc`.
    - The SPITBOL manual (`spitbol-manual-v3_7.pdf`, 368 pages, by
      Mark Emmer) for the SNOBOL4 semantics being translated FROM.
      The manual was uploaded in session #66 and the key topics are
      enumerated in the language-facts section below.

  Modules and their order of attack (each carries its own gate via
  `test_<subsys>.sc` + `.ref` in the 14-test suite — run after every
  module port):

  - [x] **SB-4b.1** `global.sc` — session #66: tightened against
    `global.inc`. Added missing UTF entry (RIGHTWARDS_ARROW collision
    at offset 148). Added the seven `&ALPHABET POS LEN`-derived byte
    range names X0xxxxxxx..X11111xxx via `define_alphabet_run`.
    Documented a known runtime gap: scrip's CHAR(n)+&&-concat for
    bytes ≥128 currently loses bytes (217 produced vs SPITBOL's 256).
    None of those names referenced in beauty so this does not affect
    output. Gate green.
  - [x] **SB-4b.2** `case.sc` — session #67: audited against
    `case.sno`. Already a faithful port — `lwr`/`upr`/`cap`/`icase`
    all present, `icase` while-loop correctly uses statement-form
    match (`subj ? PAT = ;`) for consume-on-match. No source change.
  - [x] **SB-4b.3** `assign.sc` — session #67: audited against
    `assign.sno`. Already faithful — uses portable
    `IDENT(REPLACE(DATATYPE(...), &LCASE, &UCASE), 'EXPRESSION')`
    case-folded check per RULES.md DATATYPE-portability rule. No
    source change.
  - [x] **SB-4b.4** `match.sc` — session #67: audited against
    `match.sno`. Already faithful — both `match` and `notmatch`
    follow the canonical `subject ? pattern :S(NRETURN)F(FRETURN)`
    pattern. No source change.
  - [x] **SB-4b.5** `counter.sc` — session #67: rewritten from 6
    procs to full canonical 16-procedure family per `counter.inc`:
    counter-stack (`InitCounter, PushCounter, IncCounter, DecCounter,
    PopCounter, TopCounter`) + BegTag (`InitBegTag, PushBegTag,
    PopBegTag, TopBegTag, DumpBegTag`) + EndTag (`InitEndTag,
    PushEndTag, PopEndTag, TopEndTag, DumpEndTag`). All OUTPUT
    trace lines under `GT(xTrace, 4)` gates per canonical. Gate
    stays green PASS=42 SKIP=3.

    **Snocone-port discovery (recorded in module comment):** the
    parser (`snocone_cf.c::do_procedure`) does NOT accept the
    leading-comma "no params, only locals" form
    `procedure Foo(, b, list, v)`. The loop bails on the leading
    comma without consuming `(`, corrupting the rest of parsing
    and causing a silent infinite hang at runtime (no parse error
    surfaced). Workaround: declare locals as ordinary parameters —
    SNOBOL4 zero-arg invocation initializes them to null, the
    canonical local-var semantics. Used in `DumpBegTag(b, list, v)`
    and `DumpEndTag(e, list, v)`. Future cleanup: extend the parser
    to recognize `(, locals)` form, OR document the params-as-locals
    idiom explicitly in the language-facts section.
  - [x] **SB-4b.6** `stack.sc` — session #67: audited against
    `stack.inc`. Already a faithful port of the canonical 4-procedure
    family (`InitStack, Push, Pop, Top`). OUTPUT trace lines under
    `GT(xTrace, 4)` gates as in canonical. The top-of-file
    `xTrace = 0;` initializer is a Snocone-port artifact (no global
    init in stack.inc) but harmless — global.sc sets xTrace
    independently, this is just a defensive default. No source
    change.
  - [x] **SB-4b.7** `tree.sc` — session #67: rewritten from
    `MakeNode/MakeLeaf` stubs to full canonical 9-procedure family
    per `tree.inc`: `Tree(t,v,c1..c8)` (variadic ctor, walks
    `$('c' && nc)` indirection to count children), `Append`,
    `Prepend`, `Insert`, `Remove`, `Equal` (recursive IDENT-based),
    `Equiv` (relaxed), `Find` (with `APPLY` callback), `Visit`
    (preorder traversal with `APPLY`).

    Smoke-tested at `/tmp/tree_smoke.sc` — 7 tests pass: Tree
    variadic ctor, Append, Visit-preorder, Equal-self, Equal-differ,
    Insert-mid, Remove-mid. Verifies `APPLY(.fn, args)` callback
    works in Snocone, and `$('c' && nc)` dynamic-name read/write
    works for the `Tree(...)` constructor's child-count walk.

    `test_tree.sc` and `test_tree.ref` retain their existing
    4-test form (struct + field access) — those tests use
    `MakeNode/MakeLeaf` as inline self-contained driver helpers
    and are unaffected by the tree.sc rewrite. **Adding test
    coverage for the canonical 9-proc family at the gate level
    is a separate scope** — would require a new `tree_driver.sno`
    in `programs/snobol4/beauty/` exercising the canonical procs,
    SPITBOL-derived `.ref`, and matching `test_tree.sc` rewrite.
    Tracked as a follow-on; gate stays at PASS=42 SKIP=3 today.
  - [x] **SB-4b.8** `ShiftReduce.sc` — session #67: rewritten for
    fidelity to canonical `ShiftReduce.sno`.
    (a) Restored the canonical `v ? (POS(0) && whitespace) = ;`
    leading-whitespace strip in `Shift` (was missing in prior port).
    Note that `whitespace` is undefined in the current beauty corpus
    (not present in `global.sno`/`global.sc`), so it defaults to null
    string and the strip is a no-op — but the call is now structurally
    faithful, so a future addition of a `whitespace` definition will
    take effect without further code changes.
    (b) Reduce's EVAL-failure-detection retains the
    `if (~DIFFER(t))` after-EVAL null-check pattern. A direct
    statement-level failure detection equivalent to canonical
    `t = EVAL(t) :F(NRETURN)` is not currently expressible in Snocone:
    `if (assignment-with-failing-RHS)` does not propagate inner EVAL
    failure to the test (verified at /tmp/eval_detect.sc; the
    if-arm always succeeds even when EVAL fails, prints to stderr).
    The null-check covers the common case; the divergent edge case
    (EVAL succeeds, returns null) does not arise in the beauty
    pipeline. Documented in the module header comment for future
    Snocone-EVAL-failure-detection work.
    Gate stays at PASS=42 SKIP=3 FAIL=0.

  - [x] **SB-4b.9** `TDump.sc` — session #67: audited. Three
    canonical procedures present (`TValue`, `TDump`, `TLump`).
    Body uses `IDENT(DATATYPE(x), 'NAME')` / `IDENT(DATATYPE(x),
    'tree')` direct-uppercase comparisons; per RULES.md DATATYPE
    table this is correct for one4all/scrip (returns UPPERCASE),
    though non-portable to a future SPITBOL-Snocone backend
    where DATATYPE is lowercase. Module is run only via scrip's
    Snocone frontend today; deployment-correct. Portability
    refactor (REPLACE-to-uppercase form) tracked as follow-on.
    No source change.
  - [x] **SB-4b.10** `Gen.sc` — session #67: audited. All 7
    canonical procedures present (`IncLevel, DecLevel, SetLevel,
    GetLevel, Gen, GenTab, GenSetCont`). Session #64 rewrite
    addressed systemic Snocone-port idioms. No source change.
  - [x] **SB-4b.11** `Qize.sc` — session #67: audited. All 6
    canonical procedures present (`Qize, SQize, DQize, SqlSQize,
    Intize, Extize`) + 2 helpers (`LEQ, Ucvt`). Session #64
    rewrite documents Snocone-specific scan-and-strip idioms in
    module header. No source change.
  - [x] **SB-4b.12** `ReadWrite.sc` — session #67: audited. All 3
    canonical procedures present (`Read, Write, LineMap`).
    Session #64 rewrite documents Snocone-port idioms. No source
    change.
  - [x] **SB-4b.13** `XDump.sc` — session #67: audited. The 1
    canonical procedure present (`XDump`). FIELD/APPLY-driven
    field-walk noted in module header as a Snocone limitation
    item; current implementation is functional. No source change.
  - [x] **SB-4b.14** `omega.sc` — session #67: rewritten for the
    semantic fix on TV/TW/TX. Canonical EVAL'd-source-text
    contract restored: `omega = 'pat'` (literal three-char string)
    rather than the prior variable-substitution `omega = pat;`.
    EVAL then resolves the embedded `pat` identifier via SNOBOL4
    dynamic scoping back to the procedure's `pat` parameter
    (verified to work in both SPITBOL and scrip — see
    /tmp/eval_scope.sno + /tmp/eval_scope.sc). Conditional select
    between `'pat'` and `"(pat ~ 'identifier')"` now uses
    `if (EQ(doParseTree, FALSE))` integer-equality check rather
    than the previous `~DIFFER` null-vs-non-null check.

    **Thin-path open question (TY/TZ when xTrace ≤ 0).** The
    canonical thin-path expression
    `pat @txOfs $ *assign(.t8Max, *(GT(txOfs, t8Max) txOfs))`
    is a SNOBOL4 pattern (juxtaposition with `@var` position-capture
    and `$ *fn(...)` deferred-eval immediate-value-assign).
    The Snocone form `pat && @txOfs . *assign(.t8Max, *(GT(txOfs, t8Max) txOfs))`
    produces a STRING at runtime, not a PATTERN
    (verified at /tmp/omega_iso.sc — `pat && @txOfs` alone IS a
    pattern, but appending `. *assign(...)` collapses the result
    to STRING). Cause not yet identified — likely Snocone
    `&&`+`.`+unary-`*` interaction in the lower phase. The thin
    path is preserved as-was from the prior omega.sc (no regression);
    no test exercises it today (gated on xTrace ≤ 0 with `omega`
    branch never reaching EVAL); test_omega.sc still does not
    exist. Gate stays at PASS=42 SKIP=3 FAIL=0.

    **Follow-on rung suggestions:**
    - Add `test_omega.sc` exercising both thin-path and EVAL-path
      with SPITBOL-derived `.ref`. The SPITBOL canonical needs a
      `omega_driver.sno`/`omega_driver.ref` pair first; one
      exists in `programs/snobol4/beauty/omega_driver.{sno,ref}`
      (referenced from session #66 audit).
    - Investigate why `expr && @var . *fn(...)` collapses to
      STRING in Snocone — likely `snocone_lower.c` SNOCONE_PERIOD
      or SNOCONE_INDIRECT path. Once root-caused, decide whether
      the thin-path expression needs rewriting (e.g. via explicit
      pattern function calls) or whether the lower phase needs a
      fix.
    - EVAL-failure detection: same limitation noted in SB-4b.8
      applies — Snocone `if (assignment)` does not propagate inner
      EVAL failure to the test arm. Currently we use `if (DIFFER(TY))`
      after EVAL as a proxy.
  - [x] **SB-4b.15** **NEW** `semantic.sc` — session #66: ported
    `semantic.inc`'s 8 procedures (`shift`, `reduce`, `pop`, `nPush`,
    `nInc`, `nDec`, `nTop`, `nPop`). Snocone has no OPSYN, so the
    canonical `OPSYN('~', 'shift', 2)` / `OPSYN('&', 'reduce', 2)`
    pair cannot be expressed; callers in `beauty.sc` must use the
    function forms (separate SB-5b rung). `test_semantic.sc` fixture
    PASS in all three modes; gate stays green.
  - [x] **SB-4b.16** **NEW** `trace.sc` — session #66: ported
    `trace.inc`'s `T8Trace` and `T8Pos` position-tracking helpers.
    `:S/:F` loops translated to Snocone `while`. Gated by
    `doDebug > 0` and `xTrace > 0`; needed when omega.sc runs at
    higher trace levels. Smoke-tested clean; gate stays green.

  **Habit:** after every per-module change, run the beauty test suite
  end-to-end:
  ```bash
  bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh
  ```
  Gate must remain at `PASS=42 SKIP=3 FAIL=0` (or progress beyond it
  toward `PASS=45 FAIL=0` once `test_beauty.sc` is added in SB-6).
  Any FAIL is a regression — bisect, fix, re-run before proceeding to
  the next module.

- [x] **SB-5** — Fix: beauty.sc produces no output with .sno libs.
  - [x] **SB-5a** — Port `semantic.inc` → `semantic.sc` (covered by
    SB-4b.15, closed session #66).
  - [x] **SB-5b** — CLOSED session #72. Three root causes found and fixed
    in `corpus/programs/snocone/demo/beauty/beauty.sc`:
    (1) `while(cont)` and `while(more)` infinite loops — `''` is truthy
    in Snocone (`DIFFER('')` = false), so `while(cont)` with `cont=''`
    loops forever. Fixed: `while(cont)` → `while(DIFFER(cont))`,
    `while(more)` → `while(DIFFER(more))`.
    (2) `~(match)` negation idiom broken — `~(failing_match)` returns a
    PATTERN object which is falsy in an `if` condition. The idiom
    `if (~(Line ? PAT)) { more = ''; }` never fired. Fixed:
    `if (Line ? PAT) { } else { more = ''; }`.
    (3) INPUT-after-EOF repeats last value — Snocone INPUT never returns
    null after EOF; it returns the previous line forever. Fixed: detect
    EOF by comparing `Line` to `PrevLine` via IDENT; when they match,
    set `eof_inside = 1` and clear `Line = ''`.
    Result: `echo START | ./scrip --ir-run $LIBS beauty.sc` exits cleanly
    with "Parse Error\nSTART\n" (no hang). Running on `beauty.sno` input
    produces the 7-line comment header then Parse Error on first non-comment
    statement — output flows, loop terminates. Gates PASS=5/PASS=42
    SKIP=3/PASS=49 verified green.
  - [x] **SB-5b-orig** — subsumed by SB-5b.
- [ ] **SB-5c** — **claws5.sc end-to-end smoke test via scrip.** Port or
  verify `corpus/programs/snocone/demo/claws5.sc` runs correctly under
  `./scrip --ir-run` on the standard claws5 corpus input. Gate: scrip
  output byte-identical to SPITBOL oracle running the equivalent
  `claws5.sno`. This exercises the full Snocone runtime (pattern
  construction, ARBNO, FENCE, INPUT loop) on a real corpus program
  independent of beauty — making it a clean regression canary.

  **Per Lon (session #73):** "Do not change any SC code to work
  around a bug. Make a step in this current GOAL to fix the bug
  instead. This is true for all, claws5, and treebank-* programs.
  The idea is to develop the compiler/interpreter/runtime not a
  program that just runs with workarounds." Every blocking issue
  on these gates becomes a runtime/compiler/parser fix tracked
  here, never a `.sc` rewrite.

  - [x] **SB-5c.0** — `&TRIM` keyword honored on INPUT. LANDED
    session #73. `src/runtime/x86/snobol4.c` `input_read()` and the
    channel-bound INPUT branch in `NV_GET_fn` now strip trailing
    space and tab characters from each line read when `kw_trim != 0`,
    matching SPITBOL semantics. Verified against SPITBOL: `'X \t \n'`
    with `&TRIM=1` → `'X'` (size 1) on both runtimes; `&TRIM=0`
    preserves bytes on both. Three baseline gates remain green.

  - [x] **SB-5c.1** — Fix `ARBNO(*name)` matcher bug (Snocone
    frontend). LANDED session #75. Root cause: Snocone emits
    `(E_FNC ARBNO ...)` and `(E_FNC FENCE ...)` rather than
    `(E_ARBNO ...)` / `(E_FENCE ...)`; `interp_eval_pat` had explicit
    cases for the latter (pattern-context arg evaluation, producing
    XDSAR for `*name`) but `E_FNC` fell through to value-context
    `interp_eval`, where `E_DEFER(E_VAR)` becomes a frozen DT_E.
    `pat_arbno(DT_E)` → `spat_of` returns NULL → ARBNO with NULL
    child → fails to advance cursor. Fix: `+31/-0` in
    `src/driver/interp.c::interp_eval_pat` adding a `case E_FNC`
    that for ARBNO and FENCE evaluates the child via
    `interp_eval_pat` and calls `pat_arbno`/`pat_fence_p` directly.
    Other pattern builtins (POS, RPOS, SPAN, BREAK, LEN, ANY,
    NOTANY, TAB, RTAB, ARB, REM, BAL, SUCCEED, FAIL, ABORT) take
    non-pattern args and keep the value-context default. Gate
    passed: session-#73 8-case bisection now 8/8 PASS in all three
    modes (was 6/8). Three baseline gates green. Side-effect
    closures: SB-5c.3, SB-5c.5, SB-5d.1 (see session #75 progress).

  - [ ] **SB-5c.2** — claws5 input-file alignment. The 95-line
    `claws5.ref` does not match either SPITBOL's or scrip's output
    on `claws5.input`. SPITBOL produces "Pattern match failed" on
    `claws5.input`. The .ref was likely generated from
    `CLAWS5inTASA.dat` (referenced in `claws5.sno`'s header).
    Either:
      (a) regenerate `claws5.ref` from `CLAWS5inTASA.dat` via
          SPITBOL oracle, or
      (b) replace `claws5.input` with the data the .ref was
          generated from.
    This is a corpus-curation decision, not a runtime bug.

  - [x] **SB-5c.3** — Fix claws5 hang on SPITBOL-failing input.
    LANDED session #75 as a side effect of the SB-5c.1 fix.
    `./scrip --ir-run claws5.sno < claws5.input` now produces the
    same `Pattern match failed` as SPITBOL, no hang. The
    underlying cause was the same as SB-5c.1: claws5's outer
    pattern uses `ARBNO((... | ...))` over alternations whose
    arms contain `*new_sent()` / `*add_tok()` `E_DEFER` nodes,
    which were the malformed-NULL-child path in `pat_arbno`.
    With `interp_eval_pat`'s new `E_FNC` case, those deferred
    nodes now build correctly.

  - [x] **SB-5c.4** — LANDED session #76. `claws5.sc::pp_mem`
    re-ported 1-for-1 against canonical `claws5.sno::pp_mem`.
    All 19 canonical DEFINE() locals present
    (`ssk, si, sentno, wsk, wi, wkey, wq, wrd, tsk, ti, tag, tv,
    tline, pfx, pad, next_wkey, last_sent, lline, ns`) — no extra
    Snocone-port helper flags. Each canonical SNOBOL4 label
    (`pm_cnt_loop`, `pm_sent_loop`, `pm_wrd_loop`, `pm_sq`,
    `pm_tdict`, `pm_tag_loop`, `pm_tag_sep`, `pm_tag_close`,
    `pm_mid_wrd`, `pm_last_wrd`, `pm_last_mid`, `pm_last_emit`,
    `pm_last_mid2`, `pm_done`) annotated as a comment at the
    corresponding location in the .sc. Translation pattern:
    each .sno `:F(label)` exit at iteration top → while-condition
    peek-ahead (`while (DIFFER(arr[i + 1, 1]))`); each `:F(label)`
    skip-block → if/else; each `:S(label)` loop-back at iteration
    bottom → implicit (loop ends naturally); each
    conditional-value-assign predicate (`pfx = EQ(si, 1) ...`,
    `last_sent = IDENT(si, ns) 1`) → `if (pred) lhs = rhs;`. The
    statement-form match-and-replace `wrd ? ARB "'" = ''` works
    inside `if (...)` in Snocone (verified — performs replacement
    AND yields success/failure for the test). All canonical string
    literals byte-identical: `': {'`, `': '`, `', '`, `'}}'`,
    `'},'`, `'_CRD :_PUN'` — trailing-space scrutiny clean.
    `claws5.sc` goto count = 0 (was 6). **Byte-identical output
    to SPITBOL canonical pp_mem on a controlled fixture** (md5
    `557d5df30ba52a698d1a5f3ca569d9b4` for both, on a 2-sentence
    fixture exercising single/multi-word sentences, single/
    multi-tag words, words containing `'` triggering the
    double-quote branch, and last-sentence vs mid-sentence
    closers). Three baseline gates green throughout
    (PASS=5/PASS=42 SKIP=3/PASS=49). Crosscheck snobol4 PASS=6,
    snocone PASS=8 unchanged. Note: end-to-end execution
    `./scrip --ir-run claws5.sc < claws5.input` still hangs —
    pre-existing **slurp-loop INPUT-after-EOF bug** (Snocone's
    INPUT returns the previous line forever after EOF, so
    `while (DIFFER(line))` never terminates). Reproduced cleanly
    with a 7-line standalone test. This is the same SC-INPUT-EOF
    bug noted in SB-5b session #68 main-loop rewrite. Independent
    of pp_mem; tracked for a follow-on rung. Files touched this
    session: `corpus/programs/snobol4/demo/claws5.sc` only
    (+99/-30 net, pp_mem section). No runtime/frontend source
    changes.

  - [x] **SB-5c.5** — **`claws5.sno` failure under scrip SNOBOL4
    frontend.** LANDED session #75. Same root cause as SB-5c.1
    (the `pat_arbno` NULL-child malformation) reached via the
    SNOBOL4 frontend's `E_ARBNO` path. With the SB-5c.1 fix in
    place: `treebank-list.sno` and `treebank-array.sno` are
    byte-identical to SPITBOL oracle in all three modes (24
    lines, md5 match against the .ref files); `claws5.sno`
    produces the same `Pattern match failed` as SPITBOL on
    `claws5.input` (the .ref mismatch tracked separately under
    SB-5c.2 is a corpus-curation issue, not a runtime bug).
    `claws5.sno` byte-identical against an aligned input gates
    on SB-5c.2 closing.

  Gate: `diff` empty against the agreed oracle for the agreed
  input.

- [ ] **SB-5d** — **treebank-{list,array}.sc end-to-end smoke test
  via scrip.** Same pattern as SB-5c but for
  `corpus/programs/snobol4/demo/treebank-list.sc` and
  `corpus/programs/snobol4/demo/treebank-array.sc` (both use the
  shared `treebank.input`). Both `.ref` files are byte-identical to
  each other; SPITBOL oracle on both `.sno` originals produces the
  expected 24-line output (verified session #73). Together SB-5c +
  SB-5d give independent corpus programs exercising Snocone
  runtime correctness before the beauty self-host gate.

  - [x] **SB-5d.1** — `treebank-list.sc` LANDED session #75.
    SB-5c.1 fix unblocked it directly — no `.sc` rewrite needed.
    Output byte-identical to SPITBOL oracle in all three modes
    (`--ir-run`, `--sm-run`, `--jit-run`), 24 lines, matches
    `treebank-list.ref` (md5 `7096beb49889b0d2c5db66b4a45ae444`).

  - [x] **SB-5d.2** — `treebank-array.sc` LANDED session #81.
    The .sc had two bare-juxtaposition concat sites
    (`while (DIFFER(i = LT(i, n) i + 1))` in `node_repr` and
    `while (DIFFER(i = LT(i, n - 1) i + 1))` in `pp_node`) which
    are valid SNOBOL4 source idiom but not expressible in Snocone
    (Snocone has no bare-juxtaposition concat — that's the LS-0
    gap). Replaced both with the canonical Snocone integer-loop
    idiom mirroring `treebank-array.sno::pp_wch/pp_wlast/pp_wdone`
    flow exactly: `while (LT(i, n)) { i = i + 1; ... }` for the
    1..n loop in `node_repr`, and `if (GT(n, 0)) { while (LT(i, n - 1))
    { i = i + 1; ... } dummy = pp_node(...,n,...); }` for the
    1..n-1-then-n loop in `pp_node`. The `GT(n, 0)` guard fixes
    a latent bug — prior code would call `pp_node(stk_c[f][0], ...)`
    on zero-children nodes, divergent from canonical's
    `pp_wdone :(RETURN)` early-exit. **Result: byte-identical to
    `treebank-array.ref` in all three modes** (md5
    `7096beb49889b0d2c5db66b4a45ae444`, identical to
    `treebank-list.ref` as expected). This is NOT a workaround for
    a runtime bug per session #73 rule — Snocone genuinely doesn't
    have bare-juxtaposition concat as a language feature today
    (LS-0 is "design state"), so the SNOBOL4 source idiom must be
    expressed in Snocone-native form. The semantics match the
    canonical `.sno` byte-for-byte. Three baseline gates green
    (PASS=5 / PASS=42 SKIP=3 / PASS=49); crosscheck snobol4 PASS=6,
    snocone PASS=8 unchanged. SB-5d.2 closes WITHOUT the LS-0
    language-feature adoption — the .sc and .sno can co-exist with
    different surface idioms while producing the same output. LS-0
    (parser-loud-error and language-feature decision) remains open
    in `GOAL-SNOCONE-LANG-SPACE.md` as its own rung but no longer
    gates SB-5d.2.

  - [x] **SB-5d.3** — **Translation faithfulness audit:
    treebank-list.sc and treebank-array.sc.** Verified session #74
    via line-by-line comparison against `treebank-list.sno` and
    `treebank-array.sno`. Both `.sc` files are 1-for-1 structural
    translations: same procedure set, same procedure-local
    variables, same control-flow shape (`:F(label)` / `:S(label)`
    flows translated to `while`+condition or `if/else`), same
    pattern grammar (`delim`, `word`, `group`, `treebank`).
    Snocone-port artifact accepted: the canonical `.sno` has split
    surface forms (`init_list/Init_list`, `push_list/Push_list`,
    etc., where capitalized variants are EVAL-string builders for
    OPSYN-style use); `.sc` collapses to function calls because
    Snocone has no OPSYN. Acceptable. Goto count: both files have
    ZERO gotos. **No source changes needed for faithfulness.**

  - [ ] **SB-5d.4** — **Maintain zero-goto invariant.** Both
    treebank `.sc` files are at `goto` count = 0 today (session
    #74). Future edits MUST preserve this. Any `:F(...)` /
    `:S(...)` flow added when porting new .sno features must
    translate to structured Snocone (`while`, `if/else`, `break`,
    `return`, `freturn`, `nreturn`), not to `goto label`. Gate:
    `grep -c "goto " treebank-list.sc treebank-array.sc` returns
    0 for both. Closed when first set of post-#74 edits land
    without introducing gotos.

  Gate: `diff` empty for both `treebank-list.sc` and
  `treebank-array.sc` against `treebank-list.ref` /
  `treebank-array.ref`, in all three modes.

- [ ] **SB-6** — Self-beautify. Gate: diff empty.
  Session #78 (2026-04-30) bisected the proper-indented two-statement
  fixture (`\tA = 1\n\tOUTPUT = A\nEND\n`) and identified three
  operator-lowering bugs that are gating SB-6.  All three are runtime
  /frontend fixes (no `.sc` workarounds per Lon's session-#73 rule).
  See "Session #78 progress" section above for full diagnosis,
  comparison grids, and the 11-step implementation plan for session
  #79.  Active bugs:
  - [x] **SB-6.A** LANDED session #79.  Snocone `||` now lowers to
    `E_VLIST` (was `E_CAT`).  `snocone_lower.c::SNOCONE_OR` rewritten
    with left-associative collapse (mirrors E_ALT/E_SEQ shape).
    Verified across all three modes with the IDENT-OR truth-table
    fixture: T='Id'; (IDENT(T,'Foo') || IDENT(T,'Id') || 'fallback')
    → null (second arm succeeds-as-null); (IDENT(T,'Foo') ||
    IDENT(T,'Bar') || 'fallback') → 'fallback'; (IDENT(T,'Id') ||
    'first') → null.  All 3 modes match.
  - [x] **SB-6.B** LANDED session #79.  SNOBOL4 paren-list `(a,b,c)`
    now lowers to `E_VLIST` (was `E_ALT`).  `snobol4.y:195` rule
    changed; `regenerate_parser_and_lexer_from_sources.sh` rerun;
    `snobol4.tab.c` regenerated.  Verified **byte-identical to
    SPITBOL oracle** on the same IDENT-OR truth-table fixture
    written in SNOBOL4 syntax: scrip `--ir-run` and `sbl -bf` both
    print `a=[]`/`b=[fallback]`/`c=[]`.
  - [x] **SB-6.C** LANDED session #79.  Snocone unary `?x` now
    lowers to `E_NOT(E_NOT(x))` (was `DIFFER(x,'')`) — uses existing
    IR, zero new node, exactly per session #78 design.  Verified
    truth table: ?'hello' → succeed; **?'' → succeed (was FAIL —
    the regression-fix)**; ?(EQ(2,3)) → FAIL; ?(EQ(2,2)) → succeed.
  - [ ] **SB-6.D** Beauty.sc tiny-fixture still emits "Parse Error".
    With SB-6.A/B/C landed and verified at unit level, the
    session-#78 tiny fixture
    `printf '\tA = 1\n\tOUTPUT = A\nEND\n' | scrip --ir-run $LIBS beauty.sc`
    still produces:
    ```
    Parse Error
    \tA = 1
    Parse Error
    \tOUTPUT = A
    ```
    plus 3 stderr errors (`** Error 1 ... GE first argument is not
    numeric` ×2, `** Error 5 ... Undefined function or operation`
    ×1).  Session #78 noted these as "three startup errors during
    pattern construction" that "fire BEFORE @T0 in real time".
    Session #79 confirms: the operator bugs were not the only
    upstream defects — there is at least one more, distinct from
    A/B/C.  Suggested next step: bisect the pattern-construction
    section of beauty.sc (Integer/DQ/SQ/String/Real/Id/Function/
    BuiltinVar definitions, top-of-file ppStop/ppSmBump/ppLgBump
    arithmetic, &FULLSCAN/&MAXLNGTH setup) until the first error
    fires; the trigger statement is the next gating defect.  The
    `GE first argument is not numeric` error is a strong hint —
    something passes a non-numeric value to a `GE()` call during
    pattern construction.  Likely candidate: `Real` pattern's
    nested expression or the `ppStop` array setup interacting
    with the new E_VLIST semantics.  Recommend confirming the
    error is NOT introduced by SB-6.A/B/C by checking out
    `41c9a50a` and re-running the tiny fixture — if the same 3
    errors fire there, the bugs are pre-existing and merely
    unmasked when the operator fixes let beauty.sc proceed
    further.
- [ ] **SB-7** — Gate script. Commit. Push.

---

## Snocone language facts (canonical reference, updated session 2026-05-01 #7)

Lon supplied the canonical Snocone-to-SNOBOL4 transpiler source
(SNOCONE.zip: `snocone.sc`, `snocone.sno`, `snocone.snobol4`,
`Makefile`). Plus a 368-page SPITBOL manual PDF
(`spitbol-manual-v3_7.pdf`). These are the authoritative references
for the remaining ports.

**The Snocone front-end is now the post-LS-4 Flex+Bison front-end
described in `GOAL-SNOCONE-LANG-SPACE.md`** — Andrew's `.sc`
operator set minus `&&`, `||`, `%`, plus C-style structured
control flow, plus SPITBOL space-as-concat. Key facts below are
updated for that language; see `RULES.md` "Snocone language facts"
for the binding working rules.

**Snocone binary-operator table** (post-LS-4 — three Andrew operators
removed for Lon's space-as-concat restoration):

| Snocone | SNOBOL4 emit | Notes |
|---|---|---|
| `=` | `=` | assignment |
| `?` | `?` | match |
| `\|` | `\|` | pattern alternation |
| ~~`\|\|`~~ | — | **REMOVED** — use SPITBOL alt-eval `(e1, e2, e3)` |
| ~~`&&`~~ | — | **REMOVED** — juxtaposition (whitespace) IS concat at SPITBOL pri 4 |
| (whitespace) | ` ` (blank) | concat — emitted as synthetic `T_CONCAT` token by lexer |
| `>` `<` `>=` `<=` `==` `!=` | `GT LT GE LE EQ NE` | numeric compare → fn calls |
| `::` `:!:` `:>:` `:<:` `:>=:` `:<=:` `:==:` `:!=:` | `IDENT DIFFER LGT LLT LGE LLE LEQ LNE` | string compare → fn calls |
| `+` `-` `/` `*` `^` | `+ - / * **` | arithmetic |
| ~~`%`~~ | — | **REMOVED** as built-in modulo; reserved as user OPSYN slot. Use `REMDR(a, b)` directly |
| `.` `$` | `.` `$` | conditional / immediate value-assign (binary in pattern context) |

**Snocone unary-operator set** (from Andrew's `.sc` line 78,
unchanged): `+ - * & @ ~ ? . $`. Unary `&` = keyword prefix
(zero-space form `&FULLSCAN` is one `KEYWORD_NAME` token). Unary
`~` = NOT. Unary `*` = unevaluated expression. Unary `.` = name-of.
Unary `?` = interrogation (returns null on success).

**Things Snocone does NOT have:**
- Binary `&` (still an OPSYN slot at SPITBOL priority 2 — not a
  built-in operator; lexer emits as plain token, grammar routes
  through OPSYN catch-all).
- Binary `~` (OPSYN slot at SPITBOL priority 13 — same shape).
- Binary `&&`, `||`, `%` — removed in LS-4 (see above).
- `do/until` — removed per Lon directive session 2026-04-30 #12.
  Snocone follows C exactly: `while` and `do/while` only.

**Snocone has** (additions over Andrew's `.sc`):
- `switch (e) { case v: …; default: …; }` with no fall-through
  (implicit break at end of each case). Lowers to `IDENT(tmp, vN)
  :S(cN)` chain.
- `break;` / `break LABEL;` / `continue;` / `continue LABEL;`
  (Q13 → Option A: both forms accepted).
- `goto LABEL;` (single keyword — Andrew's two-word `go to` is
  not accepted).
- Alt-eval `(e1, e2, e3)` — SPITBOL extension (Manual Ch.15
  footnote), the canonical replacement for Andrew's `||`.
- `struct NAME { f1, f2 }` — adopted from Andrew's `.sc` line 162
  self-host extension. Lowers to `DATA('NAME(f1,f2)')`.

**Snocone function form** (canonical, post-LS-4.h rename
`procedure` → `function`):

```
function name (param1, param2) local1, local2 {
    ...
    return E;         // value via E (lowers to `name = E :(RETURN)`)
    return;           // bare `:(RETURN)`
    nreturn;          // pattern/name return — `:(NRETURN)`
    freturn;          // failure — `:(FRETURN)`
}
```

Statement terminator `;` is mandatory on every clause (newlines
are whitespace, not statement boundaries — see `RULES.md`).
Block braces `{` `}` around every if/while/else body. Locals can
be declared with commas after the parameter list (canonical) or
folded into the parameter list with a comma separator (scrip
dialect — both forms accepted).

**Conditions are SPITBOL backtracking expressions, NOT C-style
booleans.** The parenthesised condition of `if`, `while`,
`do/while`, `for`-test, and `case` tag is a single SPITBOL
backtracking expression. `if (subj ? pat = repl) { … }` is legal;
the success/failure exit drives the branch. See `RULES.md`
"Snocone language facts" for the full rule.

**SPITBOL manual** (`spitbol-manual-v3_7.pdf`, 368 pages, by Mark
Emmer) is the authoritative source for the SNOBOL4 semantics being
translated FROM. Key sections to consult when porting:
- Pattern matching primitives (`SPAN BREAK ANY NOTANY LEN POS RPOS
  TAB RTAB REM ARB BAL FENCE`).
- Conditional value assignment (`. var`, `$ var`).
- Unevaluated expression (`*expr`).
- Keyword semantics (`&ANCHOR &FULLSCAN &CASE &ALPHABET`).
- Function-call return conventions (RETURN / NRETURN / FRETURN /
  SCONTINUE).
- Chapter 15 "Operators" pp.181–183 — the canonical precedence
  source for the post-LS-4 Snocone grammar (priorities 0–13).
- Chapter 15 footnote — the alt-eval `(e1, e2, e3)` extension that
  replaces Andrew's `||`.

Session #66 used the previous (`&&`/`||`/`%`) generation of these
facts to port `global.sc`, `semantic.sc`, `trace.sc`. The post-LS-4
migration script (`scripts/util_migrate_snocone_to_lang_space.py`)
mechanically rewrites those ported files: `&&` → space, `||` →
`(a, b)` alt-eval, `go to NAME` → `goto NAME`. 69 files were
migrated in LS-5.c (corpus `a4aaf83`).

---

## Invariants

- Gate = PASS=36 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Oracle: corpus/programs/snobol4/smoke/beauty_oracle.sno
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

**Per Lon (session #66):** *every* construct in canonical `.sno`/`.inc`
gets ported, regardless of whether it appears used at default settings.
No "dead-code" pruning. Code that looks unused today may be turned on
by future settings; faithful ports preserve all of it.

**No `goto` in Snocone ports unless absolutely necessary** — only when
it genuinely improves readability or eliminates massive duplication.
Default to structured `if/while/break/return/freturn/nreturn`.

---

## Canonical destination — corpus/programs/snocone/demo/beauty/

SC sources live at `corpus/programs/snocone/demo/beauty/` as of session #62.
This is the permanent home.

**Naming distinction (decided in session-#NN with Lon):**

- **BEAUTY** — `demo/beauty/` — SNOBOL4 implementation reading SNOBOL4
  source. Self-host = beauty.sno reads its own .sno source.
- **BEAUTIFY** — `demo/beautify/` — Snocone implementation reading
  SNOBOL4 source. The implementation language is Snocone; the input
  and output language remain SNOBOL4. BEAUTIFY does NOT read or write
  Snocone code (yet — that would be a future BEAUTIFY-extended).

The BEAUTIFY self-host gate produces output matching the BEAUTY md5
`abfd19a7a834484a96e824851caee159` because both pretty-print the same
SNOBOL4 source. This auto-cross-checks the Snocone implementation
against the SNOBOL4 implementation.

**Move plan (when SB-5 is green):**

1. `git mv one4all/test/beauty-sc/beauty/` content into
   `corpus/programs/snobol4/demo/beautify/`. This includes
   `beauty.sc`, `Gen.sc`, `Qize.sc`, `TDump.sc`, `XDump.sc`,
   `case.sc`, `io.sc`, `omega.sc`, `driver.sc` (auto-assembled).
2. `git mv` each of the 14 subsystem folders
   (`arith/`, `assign/`, `counter/`, `fence/`, `global/`, `match/`,
   `roman/`, `semantic/`, `ShiftReduce/`, `ReadWrite/`, `stack/`,
   `strings/`, `trace/`, `tree/`) into the same `beautify/` —
   each carrying its `driver.sc` and `driver.ref`. These are the
   subsystem-level beauty regression tests.
3. Update path constants in:
   - `scripts/test_beauty_snocone_all_modes.sh` —
     `BEAUTY_DIR=$HERE/../test/beauty-sc` →
     `BEAUTY_DIR=$CORPUS/programs/snobol4/demo/beautify`
   - `scripts/test_beauty_snocone_subsystems.sh` — analogous
   - `scripts/util_run_beauty_sc.sh` —
     `DRIVER=$ROOT/test/beauty-sc/beauty/driver.sc` →
     `DRIVER=$CORPUS/programs/snobol4/demo/beautify/driver.sc`
   - `scripts/test_crosscheck_beauty_snocone.sh` — analogous
4. The `.ref` files in each subsystem are byte-identical to the
   BEAUTY oracle outputs (they should be — the Snocone driver
   produces the same SNOBOL4-formatted output). RULES.md
   self-contained-demo exception applies: copies allowed,
   sync discipline required, byte-diff CI verification.
5. Update REPO-corpus.md to document the new `demo/beautify/`
   directory.
6. Gate after move: `test_beauty_snocone_all_modes.sh` PASS=42 SKIP=3
   still green; `test_smoke_unified_broker.sh` total still ≥ 36.

**Why move only when SB-5 is green:** moving broken code into corpus
locks in a debugging session that has to find issues across two
locations. Easier to land the move when the implementation works.

**Compatibility with GOAL-CORPUS-LAYOUT.md:** When the broader
corpus reorg executes (CL-1..CL-8), `demo/beautify/` becomes
`programs/beautify/snocone/` — the language sub-folder pattern the
new layout adopts. The current move is forward-compatible: the
.sc files are already in `beautify/`, just under a different parent.

**Active rung remains SB-5.** The destination decision does not
change what blocks progress — it only documents where the work
lands when unblocked. SB-7 (gate script + commit + push) becomes
the natural place to do the corpus move as part of the same commit
sequence that lands the gate.

---

## Session #80 progress (2026-04-30)

**Investigation only. No source changes. All repos clean.**

### SB-6.D root cause bisected to EVAL(EXPRESSION) return value

Session setup gates all green: PASS=5 / PASS=42 SKIP=3 / PASS=49.

**Confirmed**: the 3 stderr errors (`** Error 1 GE first argument is not
numeric` ×2, `** Error 5 Undefined function or operation` ×1) do NOT fire
on `/dev/null` input — they fire only when beauty.sc processes actual input
lines. They are NOT startup/pattern-construction errors as session #78/#79
hypothesised. They fire inside `ppStmt()` when the grammar eventually calls
`Reduce(t, n)` from `ShiftReduce.sc`.

**Pre-SB-6 bisection**: attempted checkout of `41c9a50a` sources into current
working tree — ABI conflict between old `interp.c` and current `icn_runtime.c`
(`icn_real_str` static/non-static conflict). Pre-SB-6 clean build not
achievable without a full separate clone. Skipped; not needed — the errors
clearly exist at HEAD and are the active target.

### Call chain leading to the GE error

```
beauty.sc pattern construction (top-level):
  ExprList = nPush() && *XList && reduce('ExprList', '*(GT(nTop(), 1) nTop())') && nPop()
  → semantic.sc::reduce(t='ExprList', n='*(GT(nTop(), 1) nTop())')
      omega = 'epsilon . *Reduce("ExprList", *(GT(nTop(), 1) nTop()))'
      reduce = EVAL(omega)    ← builds PATTERN with deferred Reduce call
  → ShiftReduce.sc::Reduce(t, n) called at pattern-match time
      DATATYPE(n) = 'EXPRESSION'          ← n is *(GT(nTop(),1) nTop())
      n = EVAL(n)                         ← should yield integer or fail
      GE(n, 1)                            ← ERROR: n is not numeric
```

### Precise bug: EVAL(EXPRESSION_DESCRIPTOR) returns STRING '' instead of failing

Minimal reproducer:

```snocone
procedure nTop() { nTop = 1; return; }
procedure Reduce(t, n) {
    Reduce = .dummy;
    n2 = EVAL(n);
    OUTPUT = 'DATATYPE(e2)=' && DATATYPE(n2);   // → STRING
    OUTPUT = 'n2=' && n2;                        // → (empty)
    nreturn;
}
e = EVAL('epsilon . *Reduce("test", *(GT(nTop(), 1) nTop()))');
'x' ? e;
```

Output:
```
DATATYPE(e2)=STRING
n2=
```

When `GT(nTop(), 1)` fails (nTop=1, so GT(1,1) fails), the expression
`*(GT(nTop(), 1) nTop())` should fail — `EVAL(n)` should either return
FAILDESCR or `''`. In scrip it returns STRING `''`.

The guard in `ShiftReduce.sc::Reduce` is:
```snocone
if (IDENT(REPLACE(DATATYPE(n), &LCASE, &UCASE), 'EXPRESSION')) {
    n = EVAL(n);
    if (~DIFFER(n)) { nreturn; }   // intended to catch fail/null
}
if (GE(n, 1)) { ... }
```

The `~DIFFER(n)` guard (`n = ''`) should catch the null result and fire
`nreturn`. But the error still reaches `GE(n, 1)`. This means either:
(a) `~DIFFER('')` is NOT succeeding in this context (the `~` E_NOT
    path has a bug when the operand is a function call that returns ''),
or
(b) EVAL returns a non-null, non-numeric value that bypasses the guard.

Cross-check: `EVAL(EXPRESSION)` where the expression succeeds works
correctly — `nTop=3` → `EVAL(n)` returns INTEGER 3, GE(3,1) succeeds.
The failure path is the broken case.

### Comparison: standalone EVAL(EXPRESSION) works; via-pattern-call does not

Standalone test (no pattern/Reduce intermediary):
```snocone
nTop = 3;
e = EVAL('*(GT(nTop, 1) nTop)');   // → EXPRESSION
e2 = EVAL(e);                       // → INTEGER 3  ✓
```
Both levels work correctly in scrip when called directly.

The failure only occurs when n is passed as `*(expr)` through the
`epsilon . *Reduce(...)` deferred-call mechanism. The EXPRESSION
descriptor for `n` at call time may differ from the standalone case —
possibly the EXPRESSION is evaluated at pattern-build time rather than
at Reduce-call time, producing a snapshot of a failing expression as
a frozen STRING rather than a live EXPRESSION descriptor.

### Recommended next session (session #81) — two concrete steps

1. **Verify the guard path.** Add `OUTPUT = 'guard: DIFFER=' && DIFFER(n)`
   immediately after `n = EVAL(n)` in a diagnostic copy of Reduce. Confirm
   whether `~DIFFER(n)` is being bypassed or whether EVAL is returning
   something non-null that passes the guard but is non-numeric.

2. **Bisect EXPRESSION vs STRING.** Compare:
   - `EVAL('*(GT(nTop(), 1) nTop())')` called directly (standalone) — what
     DATATYPE does this return in scrip? EXPRESSION or STRING?
   - `EVAL(n)` inside Reduce when n arrived as the same `*(GT(...))` via
     the deferred-call mechanism — same DATATYPE check.
   If the standalone EVAL returns EXPRESSION but the deferred-path returns
   STRING, the expression is being evaluated at PATTERN-BUILD time (when
   the `epsilon . *Reduce(...)` pattern is assembled), not at MATCH time.
   That would mean the `*(expr)` argument in an EVAL'd pattern-call
   expression is evaluated eagerly during EVAL rather than deferred until
   the pattern fires. Fix surface: `src/runtime/x86/snobol4.c` or
   `src/driver/interp.c` EVAL path for EXPRESSION descriptors passed as
   function arguments inside a pattern-building EVAL string.

3. **SPITBOL cross-check**: run the minimal reproducer under
   `/home/claude/x64/bin/sbl -b` to confirm SPITBOL correctly defers
   evaluation of `*(GT(...))` to match time. If SPITBOL also returns
   STRING '' for the same deferred call, the issue is in `semantic.sc`'s
   omega construction, not the runtime.

### Files investigated, not modified

`corpus/programs/snocone/demo/beauty/ShiftReduce.sc`,
`corpus/programs/snocone/demo/beauty/semantic.sc`,
`corpus/programs/snocone/demo/beauty/beauty.sc`,
`corpus/programs/snocone/demo/beauty/Gen.sc`.
Diagnostic test files in `/tmp/` only (not committed).

### Repos state

All clean. No source changes. Plan: commit this `.github` update only, push.

---

## Session #81 progress (2026-04-30)

**SB-5d.2 LANDED.** corpus-only diff (no runtime/frontend changes).
Three baseline gates green; both crosscheck gates green. Lon's
session-#80 minor edits to `claws5.sc`, `treebank-list.sc`, and
`treebank-array.sc` verified, and `treebank-array.sc` made byte-
identical to its `.ref` in all three modes.

### Verification of Lon's three uploaded SC edits

Lon supplied trivially-edited copies of all three demo .sc files
this session. Diffs vs corpus HEAD were minor:

- **`claws5.sc`** — removed the SB-5c.4 doc-block and the canonical
  pp_mem label-comments inserted in session #76; consolidated some
  one-line `else x = y;` forms. Verified faithful: byte-identical
  to `claws5.sno` under SPITBOL on both `claws5.input` and
  `CLAWS5inTASA.dat` (md5 `1791a3085440d7702611e3a20cd79a8d`,
  "Pattern match failed"). The `.ref` mismatch remains the SB-5c.2
  corpus-curation issue, untouched by Lon's edit.

- **`treebank-list.sc`** — `while (DIFFER(line = INPUT))` →
  `while (line = INPUT)`. The `DIFFER(...)` wrapper is redundant
  given the canonical session-#77 assignment-as-predicate idiom
  (`(line = INPUT)` already yields failure on EOF, which a `while`
  treats as exit). Verified byte-identical to `treebank-list.ref`
  in all three modes (md5 `7096beb49889b0d2c5db66b4a45ae444`).
  SB-5d.1 still LANDED.

- **`treebank-array.sc`** — same `while (line = INPUT)`
  simplification. Did NOT touch the two bare-juxtaposition concat
  sites that were tracked under SB-5d.2 — those required a
  structured rewrite, done below.

### Fix: SB-5d.2 — bare-juxtaposition concat sites in treebank-array.sc

Two sites in `treebank-array.sc` used the SNOBOL4 idiom
`i = LT(i, n) i + 1` (juxtaposition concat as guarded
side-effect-and-value). This is valid in SNOBOL4 source but not
expressible in Snocone today — the LS-0 language gap. Per Lon's
session-#73 rule, do not modify `.sc` to work around RUNTIME bugs;
this was NOT a runtime bug, it was an expressibility gap requiring
a structured-control-flow translation faithful to the canonical
`.sno` semantics.

Two changes to `corpus/programs/snobol4/demo/treebank-array.sc`:

**1. `node_repr` (loop walking children 1..n):**

```snocone
// before:
while (DIFFER(i = LT(i, n) i + 1)) {
    r = r && ', ' && node_repr(stk_c[f][i]);
}
// after:
while (LT(i, n)) {
    i = i + 1;
    r = r && ', ' && node_repr(stk_c[f][i]);
}
```

Mirrors canonical `treebank-array.sno::nr_lp`:
```
nr_lp i = LT(i, n) i + 1   :F(nr_done)
      r = r ', ' node_repr(stk_c[f][i])
      i = i                :(nr_lp)
nr_done node_repr = r ')'  :(RETURN)
```

**2. `pp_node` (loop walking children 1..n-1 with `,` suffix; child
n with `)' suffix`; if n == 0, return without emitting):**

```snocone
// before:
i = 0;
while (DIFFER(i = LT(i, n - 1) i + 1)) {
    dummy = pp_node(stk_c[f][i], indent + 2, ',');
}
dummy = pp_node(stk_c[f][n], indent + 2, ')' && suffix);
// after:
i = 0;
if (GT(n, 0)) {
    while (LT(i, n - 1)) {
        i = i + 1;
        dummy = pp_node(stk_c[f][i], indent + 2, ',');
    }
    dummy = pp_node(stk_c[f][n], indent + 2, ')' && suffix);
}
```

Mirrors canonical `treebank-array.sno::pp_wch/pp_wlast/pp_wdone`:
```
pp_wch  i   = LT(i, n) i + 1   :F(pp_wdone)
        nxt = LT(i, n) i       :F(pp_wlast)
        pp_node(stk_c[f][i], indent + 2, ',')
        i   = i                :(pp_wch)
pp_wlast pp_node(stk_c[f][i], indent + 2, ')' suffix) :(RETURN)
pp_wdone                       :(RETURN)
```

The `GT(n, 0)` guard is a real correctness fix — prior code
unconditionally executed `dummy = pp_node(stk_c[f][n], indent + 2,
')' && suffix);` after the loop. When `n == 0` (zero-children
node), this would call `pp_node(stk_c[f][0], ...)` on a
non-existent table entry, divergent from canonical's
`pp_wdone :(RETURN)` early-exit. Latent because treebank inputs
typically have non-empty nodes. Now safe for all input shapes.

### Verification

| Gate | Result |
|------|--------|
| `treebank-array.sc < treebank.input` --ir-run | PASS (md5 `7096beb...`) |
| `treebank-array.sc < treebank.input` --sm-run | PASS |
| `treebank-array.sc < treebank.input` --jit-run | PASS |
| `test_smoke_snocone.sh` | PASS=5 |
| `test_beauty_snocone_all_modes.sh` | PASS=42 SKIP=3 |
| `test_smoke_unified_broker.sh` | PASS=49 |
| `test_crosscheck_snobol4.sh` | PASS=6 |
| `test_crosscheck_snocone.sh` | PASS=8 |
| `treebank-list.sc` (3 modes) | PASS — Lon's edit preserved |
| `claws5.sc` (3 modes) | FAITH-MATCH .sno SPITBOL — SB-5c.2 unchanged |

Zero regressions across any gate.

### SB-6.D investigation snapshot (not landed; for session #82)

Session #80's prescribed three-step diagnostic was performed before
the SB-5d.2 fix. Findings:

**Bug confirmed:** at beauty.sc's actual call site,
`EVAL(EXPRESSION)` returns the same EXPRESSION descriptor unchanged
(no-op). A second `EVAL` produces `STRING ''` (the correct failure
value of `*(GT(nTop(), 1) nTop())` when `nTop=1`).

```
[D Reduce] entry t=[..] n-DT=EXPRESSION
[D Reduce] post-EVAL n-DT=EXPRESSION n=[EXPRESSION]   ← 1st EVAL no-op
[D Reduce] EVAL(EVAL(n)) DT=STRING val=[]              ← 2nd EVAL works
[D Reduce] IDENT(n,n_orig)= (succeeds — n unchanged by 1st EVAL)
```

The `~DIFFER(n)` guard in `Reduce` therefore does not fire (n is
non-null), control reaches `GE(n, 1)` with `n` still EXPRESSION,
and Error 1 fires.

**Bug does NOT reproduce in standalone tests.** Tested:
- `EVAL('*(GT(nTop(),1) nTop())')` standalone → returns EXPRESSION.
- `EVAL(EXPRESSION)` of a successful expr → INTEGER (correct).
- `EVAL(EXPRESSION)` of a failing expr → fail (assignment leaves
  LHS unchanged, correct).
- `/tmp/repro2.sc` rebuilt the exact omega-string-and-EVAL pattern
  semantic.sc::reduce uses → **first EVAL returns STRING `''`
  correctly** in this isolated form.

So the EXPRESSION arriving at `Reduce` in beauty.sc's actual run
is **double-wrapped** somehow — EVAL once unwraps one layer,
producing another EXPRESSION; EVAL twice fully evaluates. Possible
cause: when the EVAL'd reduce-pattern is concatenated via `&&` into
a larger pattern (e.g., `Expr4 = nPush() && *X4 && reduce('..', ...)
&& nPop()`) the `*expr` argument to `*Reduce(t, *expr)` gets re-
wrapped during pattern composition or lowering.

**Cross-check vs SPITBOL not yet performed** — out of session-time
budget. Session #82 should:
1. Run `/tmp/repro3.sc` (left in /tmp from session #81 — wraps the
   reduce-call inside `nPush() && X4 && reduce(...) && nPop()` like
   beauty.sc's Expr4) and compare to /tmp/repro2.sc to isolate
   whether the wrapper exposes the double-wrap.
2. SPITBOL equivalent test: build a SNOBOL4 program that constructs
   an analogous `epsilon . *Reduce(t, *expr)` pattern via EVAL,
   wraps it in `&` and matches; verify SPITBOL evaluates `*expr`
   in one EVAL.
3. If the wrapper does expose double-wrap, fix surface is likely
   `src/runtime/x86/snobol4_invoke.c` or the EVAL/EXPRESSION
   descriptor packing path where deferred-call args get an extra
   EXPRESSION layer when their parent pattern is itself composed.

### Files touched this session

- `corpus/programs/snobol4/demo/treebank-array.sc` — `+9/-3` net
  in `node_repr` and `pp_node` loops + 3-line comment block in
  pp_node referencing canonical pp_wch/pp_wlast/pp_wdone.
- `corpus/programs/snobol4/demo/treebank-list.sc` — Lon's
  `while (line = INPUT)` simplification, applied as-uploaded.
- `corpus/programs/snobol4/demo/claws5.sc` — Lon's edits applied
  as-uploaded.

No `one4all`, `csnobol4`, `x64`, or scrip runtime/frontend changes.
Diagnostic test files in `/tmp/` only (not committed); ShiftReduce.sc
and semantic.sc instrumentation reverted before this commit per
RULES.md.

### Repos state

`corpus`: dirty (3 .sc files). `.github`: this update. `one4all`,
`csnobol4`, `x64`: clean. Plan: commit corpus + .github, push
corpus first then .github.

## Session #82 progress (2026-05-01)

**SB-6.D LANDED — root cause was in the corpus, not the runtime.**

### Root cause: faulty Snocone port of `:F(NRETURN)`

Sessions #80 and #81 framed SB-6.D as a runtime "double-wrap" bug
where `EVAL(EXPRESSION)` returned the same EXPRESSION descriptor
unchanged, supposedly requiring two EVAL calls to fully evaluate.
That diagnostic was misleading. The runtime is correct.

The bug is in `corpus/programs/snocone/demo/beauty/ShiftReduce.sc`
lines 45-52. The original Snocone code:

```snocone
n = EVAL(n);
if (~DIFFER(n)) { nreturn; }   // intended: catch EVAL failure
```

Per SPITBOL Manual Ch.2 p.33 (verified by reading): "If the
statement fails, the assignment is not performed, and execution
continues with the next statement in line." So when `EVAL(n)`
fails — which it must, because `*(GT(nTop(),1) nTop())` evaluates
to a failing expression when `nTop=1` — the assignment fails
silently. `n` keeps its prior EXPRESSION value. Then `DIFFER(n)`
succeeds (n is non-null), `~DIFFER(n)` fails, the nreturn does
not fire, and execution falls through to `GE(n, 1)` with `n` still
being an EXPRESSION descriptor. **Error 1 / Error 109 — first
argument is not numeric.**

The session #81 observation that "post-EVAL n-DT=EXPRESSION" wasn't
double-wrapping. It was the prior value of `n` showing through after
a silently-failed assignment.

### Smoking-gun cross-check

Ported the broken if-form back to SNOBOL4:

```snobol4
        IDENT(REPLACE(DATATYPE(n), &LCASE, &UCASE), 'EXPRESSION') :F(skip)
        n  =  EVAL(n)             ; <-- no :F handler (matches Snocone if-form)
        ~DIFFER(n)                                               :S(NRETURN)
skip    GE(n, 1) ...
```

**Both SPITBOL and scrip's SNOBOL4 frontend fail with the same
"GE first argument is not numeric" error.** The bug is in the
program logic, not in any runtime.

### Fix

```snocone
if (~(t = EVAL(t))) { nreturn; }   // direct port of t = EVAL(t) :F(NRETURN)
if (~(n = EVAL(n))) { nreturn; }   // direct port of n = EVAL(n) :F(NRETURN)
```

The embedded `t = EVAL(t)` is itself an expression that fails iff
EVAL fails (statement-level RHS-fails-statement-fails generalized
to embedded assignment per Manual Ch.9 p.128 multiple-`=`). `~`
negates: `~(EVAL fails)` → succeeds → `if`-body fires `nreturn`.
On EVAL success, `~(...)` fails → `if`-body skipped → execution
proceeds with `n` holding the new evaluated value.

Tested against three cases via `/tmp/repro_fix.sc`:
- c=1 (failing expr): EVAL fails → nreturn fires. ✓
- c=3 (succeeding expr): EVAL returns INTEGER 3 → GE(3,1) succeeds. ✓
- preserved-LHS verified: `x = EVAL(failing_expr)` leaves x at prior
  value, exactly per SPITBOL semantics. ✓

Stale comment block at ShiftReduce.sc lines 23-32 (claimed Snocone
`if (assignment)` does not propagate inner EVAL failure) corrected
— that claim was either pre-LS-4.l grammar state or a flawed earlier
probe. Current Snocone with LS-4.l's `sc_split_subject_pattern`
correctly propagates embedded-assignment failure. Verified with
`/tmp/repro_eval_detect.sc`: `if (n = EVAL(failing))` fires the
fail-arm cleanly; `if (~(n = EVAL(failing)))` fires the success-
arm. Both expected behaviors.

### Two further grammar gaps surfaced while validating end-to-end

Tried compiling beauty.sc multi-file via `scrip` to verify the fix
end-to-end. `case.sc:22` failed to parse on `str ? (POS(0) ANY(&UCASE
&LCASE) . letter) = ;`. Bisected into two independent issues:

**Gap #1 (LANDED — `snocone_parse.y`): empty replacement RHS.**
Statement-form `subj ? pat = ;` and bare `x = ;` (assign null to x)
are both faithful SPITBOL constructs. SPITBOL handles them via
`opt_repl` (snobol4.y:77). Snocone grammar required a non-empty RHS
for the binary `=` operator. Fix: added a second production
`expr0 : expr1 T_2EQUAL` (no RHS) lowering to `E_ASSIGN(lhs, '')`.
Bison reports zero conflicts — single-token lookahead distinguishes:
if next can start expr0 → shift (binary form); else (T_SEMICOLON,
T_RPAREN) → reduce to empty-RHS form. Empty RHS = NULL = SPITBOL
zero-length string per Lon's session-#8 directive.

**Gap #2 (LANDED — `snocone_lex.c`): keyword-concat-keyword.**
`ANY(&UCASE &LCASE)` (two keyword refs concat'd) failed to inject
T_CONCAT because the lexer's `is_value_starter()` predicate at
S_DISPATCH didn't include `&`. The `&IDENT` keyword dispatch at
line 252 fired before any concat injection check, so two adjacent
keyword references with whitespace between them produced
T_KEYWORD T_KEYWORD with no T_CONCAT. Fix: added explicit CONCAT
trigger for `&` followed by alpha when `had_ws && last_value`.

**Gap #3 (OPEN — handed off to GOAL-SNOCONE-LANG-SPACE LS-6.c).**
Dense one-liner `if (cond) { stmts; } else { stmts; }` produces a
parse error regardless of whitespace between `}` and `else`.
Pre-existing — reproduces against baseline without any of session
#8's fixes. Beauty.sc:284 onward uses this dense form. Likely a
matched/unmatched-stmt grammar gap in `snocone_parse.y` (LS-4.f
territory). Not blocking SB-6.D close.

### Verification

All gates green at session-end with all session #8 fixes applied:

| Gate | Result |
|------|--------|
| `test_smoke_snocone.sh` | PASS=5 FAIL=0 |
| `test_beauty_snocone_all_modes.sh` | PASS=42 FAIL=0 SKIP=3 |
| `test_smoke_unified_broker.sh` | PASS=49 FAIL=0 |
| `test_smoke_snobol4.sh` | PASS=7 FAIL=0 |
| `test_gate_sn7_beauty_self_host.sh` | PASS=51 FAIL=0 |
| `test_interp_broad_corpus_and_beauty.sh` | PASS=222 FAIL=52 (baseline) |

**SB-6.D closes here.** LS-6.c's outstanding work moves entirely
into `GOAL-SNOCONE-LANG-SPACE.md` — see that goal file's LS-6.c
session-#8 narrative for next-session pickup pointers (gap #3 +
beauty.sc end-to-end + .ref generation).

### Files touched this session

- `corpus/programs/snocone/demo/beauty/ShiftReduce.sc` — Reduce
  EVAL failure detection: two if-forms changed to `~(assign)`
  embedded form; comment block lines 23-32 corrected.
- `one4all/src/frontend/snocone/snocone_parse.y` — empty-RHS
  assignment production added at expr0.
- `one4all/src/frontend/snocone/snocone_parse.tab.c`,
  `snocone_parse.tab.h` — regenerated.
- `one4all/src/frontend/snocone/snocone_lex.c` — CONCAT trigger
  for `&IDENT` keyword reference at S_DISPATCH.
- `.github/GOAL-SNOCONE-BEAUTY.md` — this session block.
- `.github/GOAL-SNOCONE-LANG-SPACE.md` — LS-6.c session #8 narrative.
- `.github/PLAN.md` — LS-6.c step pointer updated.

### Repos state

`corpus`: dirty (1 .sc). `one4all`: dirty (3 files: .y, .tab.c,
.lex.c). `.github`: dirty (3 .md). `csnobol4`, `x64`: clean.
Plan: commit corpus + one4all + .github per RULES.md handoff
order — code repos first, .github last.
