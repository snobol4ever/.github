# GOAL-NET-BEAUTY-SELF — snobol4dotnet Beauty Self-Hosting

**Repo:** snobol4dotnet
**Depends on:** GOAL-NET-BEAUTY-19 must be complete (19/19)
**Done when:** `dotnet Snobol4.dll -bf beauty.sno < beauty.sno` runs to
completion with exit 0, produces ≥500 lines of beautified output, and
emits no `error ` lines on stderr — matching the SPITBOL `-bf` baseline.

## ⛔ Read this first — every session

1. **Source location:** `/home/claude/corpus/programs/snobol4/demo/beauty/`
   contains `beauty.sno` and all its `.inc` files in **one folder**.
   That folder is the only one that works for self-host because beauty.sno
   uses `-INCLUDE 'global.inc'` etc. with no path prefix.
   Do **not** use `/home/claude/corpus/programs/snobol4/demo/beauty.sno`
   (that one uses `-INCLUDE 'global.sno'` and lives next to demo siblings,
   not its includes — different program).

2. **Invocation flag is `-bf` (not `-b`).**
   beauty.sno relies on **case-sensitive labels** — `shift` vs `Shift`,
   `reduce` vs `Reduce`, `pop` vs `Pop`, etc. — to wire the parser's
   semantic-action callbacks. With `-b` (default fold-to-upper) those
   pairs collide as duplicate labels or the callbacks misroute silently.
   SPITBOL `-bf` is the canonical run.

3. **PASS criterion is "runs cleanly", not byte-identical.**
   Even SPITBOL's own self-host output drifts ~19 lines from the input
   (semicolon comments, whitespace alignment). Convergence is a future
   goal; this goal stops at "runs end-to-end without errors".

4. **Do not grep stdout for "Parse Error" or "Internal Error"** to
   detect failure — those strings appear in beauty.sno's own source as
   user-printed messages (`mainErr1`, `mainErr2`). A correct run echoes
   them. Detect failure via exit code + line count + stderr-clean.

5. **OUTPUT goes to stderr in snobol4dotnet** (per `REPO-snobol4dotnet.md`),
   but to stdout in SPITBOL/CSNOBOL4. The gate for snobol4dotnet must
   measure stderr (after filtering the dotnet exception trace prefix).

## Canonical oracle invocations

```bash
cd /home/claude/corpus/programs/snobol4/demo/beauty

# SPITBOL x64 — primary oracle
SETL4PATH=".:/home/claude/corpus/programs/include" \
    /home/claude/x64/bin/sbl -bf beauty.sno < beauty.sno

# CSNOBOL4 — secondary oracle
/home/claude/csnobol4/snobol4 -bf -P 64k -S 64k \
    -I. -I/home/claude/corpus/programs/include \
    beauty.sno < beauty.sno
```

## What this means

beauty.sno is a SNOBOL4 beautifier. A beautifier is idempotent on
already-beautified source — feeding beauty.sno to itself should produce
beauty.sno unchanged. SPITBOL's own output is not byte-identical due to
minor formatting drift (it is a future goal to converge), so the
**self-host gate is "runs to completion with exit 0 and produces
non-empty beautified output"**, matching what SPITBOL `-bf` does today.

## Test command

snobol4dotnet sends `OUTPUT` to stderr (per `REPO-snobol4dotnet.md`),
so the beautified self-host result lands on stderr — not stdout. The
gate counts stderr lines (after filtering the dotnet exception trace
prefix) and confirms no compile-time error markers appear. SPITBOL,
by contrast, sends OUTPUT to stdout — both are correct for their
runtimes. The gate below works for snobol4dotnet specifically.

```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
cd $BEAUTY
dotnet $SNO4 -bf beauty.sno < beauty.sno \
    > /tmp/beauty_self_out.txt 2>/tmp/beauty_self_err.txt
RC=$?
# Strip dotnet runtime crash prefix lines if any. Real OUTPUT is on stderr.
grep -v "^Unhandled\|^ at \|^Aborted" /tmp/beauty_self_err.txt \
    > /tmp/beauty_self_clean.txt
LINES=$(wc -l < /tmp/beauty_self_clean.txt)
echo "exit=$RC stderr-lines=$LINES"
# PASS: clean exit, plenty of beautified output, no compiler error markers,
#       and no Parse Error/Internal Error from beauty's mainErr paths.
[ $RC -eq 0 ] && [ $LINES -gt 500 ] \
    && ! grep -qE "error [0-9]+ --" /tmp/beauty_self_clean.txt \
    && ! grep -q "^Parse Error$\|^Internal Error$" /tmp/beauty_self_clean.txt \
    && echo "SELF-HOST PASS" || echo "SELF-HOST FAIL"
```

### Oracle baselines (verified Sun Apr 26 2026, x64 build)

| Oracle | Invocation | Result on this clone |
|--------|------------|----------------------|
| SPITBOL  | `SETL4PATH=… sbl -bf beauty.sno < beauty.sno` | exit 0, 646 stdout lines, stderr clean — **PASS** ✅ |
| CSNOBOL4 | `snobol4 -bf -P 64k -S 64k -I. -I… beauty.sno < beauty.sno` | exit 1, 32 stdout lines, `beauty.sno:616: Caught signal 11 in statement 1074 at level 0` — **segfault** |
| snobol4dotnet | `dotnet Snobol4.dll -bf beauty.sno < beauty.sno` | exit 0, mainErr1 path — **current S-2 bug** |

**SPITBOL is the canonical oracle for this gate.**

CSNOBOL4 segfault discrepancy: another session reports CSNOBOL4 self-hosts
cleanly with the same invocation. On this clone (csnobol4 HEAD `b3aeb9f`,
binary built fresh) it segfaults at stmt 1074. Could be platform-specific
(stack guards, signal handling, libc differences). Not investigated; not
a blocker for this goal — snobol4dotnet must match SPITBOL.

## Current diagnosis (supersedes all prior notes below)

**Sun Apr 26 2026, evening.** Three runtime fixes landed in
snobol4dotnet @ `0914fbf` that unblock the deferred-expression path
through user-defined functions.  Beauty 17/17 still PASS.  Self-host
no longer raises any `error 109 -- ge first argument is not numeric`
(the prior-session blocker); it now reaches "Parse Error" on simple
assignments without any runtime exceptions in between.  The remaining
work is the parser pattern itself — the ARBNO(*Command) graft issue.

**Bugs fixed this session (snobol4dotnet @ 0914fbf):**

1. **Var.cs `ToNumeric`** — when the arg is an `ExpressionVar`, run its
   `DeferredCode`, pop the resulting top-of-stack value, then continue
   numeric extraction (recursing through NameVar resolution as needed).
   Mirrors SPITBOL semantics: a deferred `*(...)` evaluates on demand
   whenever a numeric value is needed.

2. **NumericComparisonHelper.cs `BinaryComparison`** — when `ToNumeric`
   returns false because the deferred expression itself failed
   (`Failure` already set), call `NonExceptionFailure()` rather than
   `LogRuntimeException(errorLeft/errorRight)`.  A failed `*(...)` in
   numeric-comparison position yields a SNOBOL match-failure, not a
   fatal "first/second argument is not numeric" error (errors 101–150).

3. **NumericHelper.cs `BinaryNumericOperation`** — same propagation
   rule for `+`, `-`, `*`, `/`, `^` (errors 1, 2, 12, 16, 26, 32).

**Verification:**
- Beauty 17/17 gate still PASS.
- Self-host: `error 109` (in ShiftReduce.inc and counter.inc) and
  `error 1` (addition in counter.inc) — all gone.  Output is now
  clean up to `Parse Error` on the first non-comment statement.
- Minimal Reduce-with-`*(GT(nTop(),1) nTop())` repro confirmed:
  evaluates correctly, no runtime exception.

**Remaining bug (the actual S-2 work) — Parse Error on assignment:**

```
$ cat > /tmp/tiny2.sno << 'EOF'
              x = 1
END
EOF
$ dotnet Snobol4.dll -bf beauty.sno < /tmp/tiny2.sno
Parse Error
              x = 1
```

`Parse = nPush() ARBNO(*Command) *Top()` only succeeds on input that
the grammar already accepts at zero-Commands (comment-only input,
label-only `START\n`).  Real statements (`x = 1\n`, `&FULLSCAN = 1\n`)
trip Parse Error.  No runtime errors fire — the pattern just fails.
This is the ARBNO(*Command) graft territory from prior sessions:
multiple sessions have noted that `'AB' POS(0) *Parse RPOS(0)` works
when `Parse = nPush() ARBNO(LEN(1))` (Graft fix landed) but fails
when the inner pattern is `*Command` — semantic actions inside the
ARBNO body don't fire and/or backtracking alternates are dropped.

**Likely fix sites for next session:**
1. `Snobol4.Common/Runtime/Pattern/ArbNoPattern.cs` — verify the Graft
   fix (826d4ff) applies correctly when inner is `*X` returning a
   pattern that itself contains `*Y` (nested star-expressions, which
   is what `*Command` ultimately expands to via the `&` OPSYN chain).
2. `Snobol4.Common/Runtime/Pattern/UnevaluatedPattern.cs` — `Scan`
   uses `Graft` on the outer scanner.  When it grafts a pattern whose
   nodes themselves contain `*` references, those inner stars
   themselves Scan via the outer scanner — does that re-graft path
   preserve ARBNO's alternates?
3. Test target: a minimal `Parse = nPush() ARBNO(*X) *Top()` where
   `X = ('a' . *push) | ('b' . *push)` (i.e. *X picks tokens with
   semantic actions on each), feed it `'aab'`, expect 3 push calls.
   If that fails, the graft + ARBNO loop has the same root cause as
   beauty's Parse failure.

The runtime is now SPITBOL-compatible enough for deferred expressions
in numeric/comparison contexts; the pattern engine is the next layer.

---

## Prior diagnosis (superseded by above; preserved for history)

**Sun Apr 26 2026, late afternoon.** Three infrastructure bugs in
snobol4dotnet were fixed (CommandLine.cs concatenated boolean flags,
SourceCode.cs IsEndStatement uppercase END, MainConsole.cs debug print
removed); committed as `13bfcc0`.  After those fixes the program ran
end-to-end but tripped `mainErr1` (Parse Error).  See git log for
detail.

**Original repro that drove this session** — now passes after `0914fbf`:
the `*Shift` resolution failure was a symptom of `AmpCaseFolding`
default; that was already fixed in `13bfcc0`.


---

## Steps

- [x] **S-1** — Diagnose error 021 on beauty.sno self-input. Confirmed:
  - FENCE.sno deleted (CSNOBOL4 now has FENCE built-in; shim no longer needed)
  - io.sno fixed: OPSYN('INPUT','input_') guard added (SPITBOL rejects this with fatal error 248)
  - Beauty suite: dotnet 18/18, SPITBOL 15/18 (improved from 13/18)
  - Self-host infinite loop: snobol4dotnet loops; SPITBOL gets error 021 at stmt ~750
  - Root cause identified: nTop() uses RETURN (value return) but Parse pattern calls
    it via string evaluation ("'nTop()'" & ...) in a pattern context expecting NRETURN.
    ARBNO(*Command) also loops under snobol4dotnet — same root cause or related.
  - corpus HEAD: 0074bc5

- [ ] **S-2** — Fix root cause: self-host Parse fails on label-only statements.
  FRETURN PROPAGATION — PARTIAL FIX (snobol4dotnet 80381fb, INCOMPLETE):
    Confirmed bug: FRETURN from user-defined function does not abort calling statement.
    Two fix sites identified and partially patched:
    (A) BuilderEmitMsil.cs: earlyExit label added; after CallFuncBySlot emits
        Failure check + Brtrue earlyExit; earlyExit marked before FinalizeStatementMsil.
    (B) ThreadedExecuteLoop.cs: CallFunc/CallFuncIndirect now scan to next Finalize
        when Failure=true.
    BLOCKER: When function defined via runtime DEFINE() (not compile-time visible),
    it is absent from FunctionSlotIndex. MSIL emitter R_PAREN_FUNCTION returns false
    -> statement falls back to threaded opcodes. But ThreadIsMsilOnly=true for whole
    program -> fast path runs -> threaded CallFunc fix never fires; MSIL fix also
    never fires (statement not cached). Test still fails.

  NEXT SESSION — two options to complete the fix:
    Option 1 (preferred): Fix MsilHelpers.cs CallFuncBySlot() — after entry.Handler()
      sets Failure=true, pop SystemStack back to StatementSeparator immediately.
      Fires regardless of MSIL vs threaded path. Then remove threaded scan-forward.
    Option 2: When R_PAREN_FUNCTION falls back, emit a CallMsil wrapper that calls
      the runtime function then checks Failure, keeping ThreadIsMsilOnly=true.

  After fix: run /tmp/test_step2.sno ('D after ffail' must NOT print),
  beauty 17/17, then self-host.
  ROOT CAUSE CONFIRMED (826d4ff): UnevaluatedPattern.Scan creates a child Scanner
  to match *X. ARBNO's backtracking alternates are saved in the child scanner's state,
  then discarded when the child returns its first success. The outer scanner can never
  backtrack into ARBNO for more iterations. Result: nPush() ARBNO(*Command) always
  matches only one Command; 'START\n' (label-only statement) causes Parse Error.

  Minimal repro confirmed:
    'AB' POS(0) *Parse RPOS(0) FAILS when Parse = nPush() ARBNO(LEN(1))
    'AB' POS(0)  Parse RPOS(0) PASSES (direct, no * indirection)

  SIDE WORK THIS SESSION (snobol4dotnet d4e523f, corpus 4c044d2):
    - FENCE(p) sealing bug fixed: new SealPattern + ScannerState.SealAlternates() (-2 sentinel)
    - Structure now: AlternatePattern(ConcatenatePattern(p, SealPattern()), AbortPattern())
    - 7 new corpus tests added: crosscheck/patterns/068-074 (*var and FENCE coverage)
    - 061_pat_fence_fn_seal now PASSES; all 12 FENCE corpus tests pass (058-069)
    - Fixed pre-existing wrong assertions in TEST_Fence_064/065
    - Pre-existing failures unchanged: 14 TEST_Csnobol4_* unit tests, 099_keyword_rw
    - ALSO FOUND: ARBNO(*fn()) crashes Stack empty in ConditionalVariableAssociationPattern
      (separate bug, same Graft fix needed)

  FIX APPROACH - Graft (826d4ff, INCOMPLETE):
    UnevaluatedPattern.Scan evaluates *X, grafts the result's nodes into the
    RUNNING scanner's AST (remapped indices, dangling Subsequent=-1 wired to the
    node following *X), returns GOTO so Match jumps inline. All alternates stay
    in one unified stack. MatchResult.cs + AbstractSyntaxTree.cs scaffolded.

  SESSION WORK (corpus fixes, io.sno removal):
    - Removed -INCLUDE 'io.sno' from demo/beauty.sno, demo/expression.sno, smoke/beauty_oracle.sno
    - Deleted beauty_io_driver.sno + .ref (tested io.sno only)
    - Fixed feat/f10_io_basic.sno, feat/f11_io_file.sno: 4-arg SNOBOL4+ -> 3-arg SPITBOL protocol
    - Fixed demo/beauty.sno + smoke/beauty_oracle.sno: output__/input__ -> OUTPUT/INPUT (3-arg)
      This eliminated the InvalidCastException crash in --auto two-pass mode
    - Graft scaffolding (Scanner.Graft, GOTO in Match loop, UnevaluatedPattern.Scan) already
      complete in code from prior session (826d4ff). Beauty suite: 17/17 (was 18/18 with io driver).
    - Self-host: crash gone; now truncates at ARBNO(*Command) — known S-2 graft bug remains.
    - corpus HEAD: 7d26569

  SESSION WORK (prior session — diagnosis only, no code changes):
    - Minimal repro 'AB' POS(0) *Parse RPOS(0) where Parse = nPush() ARBNO(LEN(1))
      now PASSES — Graft fix is working for that case.
    - Self-host still FAILS with new symptom: InvalidCastException PatternVar→ProgramDefinedDataVar
      in GetProgramDefinedDataField (Data.cs:206) when pp(sno) calls t(sno) and sno is a PatternVar.
    - Root cause fully diagnosed (see below).

  SESSION WORK (this session — diagnosis deeper, no code committed):
    - Confirmed crash site: t(Pop()) in pp(), sno = Pop() returns PatternVar not tree node.
    - Mini repro confirmed: minimal program with Label/Command/Parse/ARBNO reproduces the bug.
    - DumpStack() after match shows $'@S' is EMPTY — Shift never pushed any tree nodes.
    - Attempted Graft fix in ArbNoPattern.Scan (two variants): first caused infinite loop (wired
      graft end back to ARBNO node itself), second gave only 1 iteration. Both reverted.
    - ArbNoPattern.Scan currently uses child scanner (reScan = new Scanner(scan.Exec)) —
      Exec IS shared, so $'@S' globals are accessible; Shift should fire correctly in child.
    - New hypothesis: FRETURN propagation bug in nested function call args. When $'@S' = '',
      DIFFER($'@S') → DIFFER('','') → fails → FRETURN from Pop(). But DATATYPE(Pop()) in
      the OUTPUT statement still outputs 'pattern' instead of failing silently. This suggests
      snobol4dotnet does not correctly propagate FRETURN through nested function-call arguments.
    - ALSO: confirmed $'@S' is empty after match — meaning Shift() was never called at all.
      The semantic actions inside ARBNO(*Command) are not firing.
    - snobol4dotnet HEAD: 080e19c (unchanged)
    - corpus HEAD: 7d26569 (unchanged)
    - beauty suite: 17/17 confirmed at session start

  NEXT SESSION must investigate TWO things:
    A. Why Shift() is never called inside ARBNO(*Command). Add OUTPUT tracing directly into
       Shift_ body (not guarded by xTrace) to confirm whether Shift fires at all during the
       ARBNO match. If it doesn't fire, the *Label ~ 'Label' semantic action isn't executing —
       meaning UnevaluatedPattern inside the child scanner is not triggering semantic side-effects.
    B. FRETURN propagation: write a standalone test:
         DEFINE('ffail()', 'ffail_')
         ffail_  :(FRETURN)
         OUTPUT = 'before: ' DATATYPE(ffail())
         OUTPUT = 'should not print'
       If 'before: pattern' prints, there is a FRETURN propagation bug in output/function-arg
       context. Fix would be in the function-call evaluation path (MsilHelpers or Executive).
    C. If (A) shows Shift does fire but $'@S' is still empty, check if child scanner's Graft
       for *Shift(...) is failing silently (error 103 from re_ EVAL) rather than executing Shift.
    - snobol4dotnet HEAD: 080e19c (unchanged this session)
    - corpus HEAD: 7d26569 (unchanged this session)

  ROOT CAUSE (newly diagnosed):
    When *P is used where P holds a pattern built by reduce() (e.g. the ("'Parse'" & '...') term),
    the UnevaluatedPattern compiled for *P re-evaluates the BUILD-TIME expression that created P
    at match time, rather than simply reading P's current value (the already-built PatternVar).
    This re-invokes re_ (the build-time reduce function) with pattern arguments instead of strings
    → error 103 in re_'s EVAL → no pattern returned → Shift is never called → $'@S' is empty
    → Pop() returns '' (empty string) → pp(sno) calls t('') → GetProgramDefinedDataField crashes
    casting StringVar to ProgramDefinedDataVar.

    Evidence:
      - Trace confirms re_ fires at match time (not build time) when *P is matched
      - Shift() is never called during the match — no tree nodes pushed
      - Pop() returns 'string' not 'treeNode'
      - Standalone EVAL tests confirm re_ and sh_ EVALs both work correctly when P is a global
        variable — the bug is specific to how ConvertUnaryStarOperatorsToDeferredExpressions /
        ExtractStarExpressions in Lexer.cs compiles *P references.

    Hypothesis: ExtractStarExpressions captures the full RHS expression tree that initialized P
    (the reduce(...) call) as the deferred expression for *P, rather than a simple variable load.
    This is correct for inline *EXPR but wrong for *P where P is a plain variable already holding
    a pattern.

  NEXT SESSION must:
    1. In Lexer.cs ExtractStarExpressions: verify what DeferredCode is generated for *P
       when P is a simple IDENTIFIER token (not a compound expression). It should emit
       a plain variable-load, not replay the expression that last assigned P.
    2. Write unit test: assign P = somePattern; match 'x' *P — verify P's value is read,
       not P's initializer re-evaluated.
    3. Fix ExtractStarExpressions (or the MSIL emitter) so *P for a simple variable
       emits a variable load, not expression replay.
    4. Run beauty suite gate (must stay 17/17).
    5. Run self-host test: SELF-HOST PASS.
    6. Run unit tests + commit + push snobol4dotnet.

- [ ] **S-3** — Gate: see "Test command" section above. Output: `SELF-HOST PASS`.

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.

  SESSION WORK (this session — deep diagnostic, no code changes, HEAD unchanged ec59eeb):
    - Beauty gate confirmed 17/17 at session start (HEAD ec59eeb)
    - Self-host crash with 'START\n' as input: same InvalidCastException at Data.cs:206

    KEY FINDING: ARBNO + *fn() semantic actions are NOT broken in general.
    Exhaustive tests show all these work correctly:
      - ARBNO(LEN(1) *inc()) on 'ABC' POS(0)..RPOS(0) → count=3 ✓
      - ARBNO(*cmd) where cmd = LEN(1) *inc() → count=3 ✓
      - *Parse where Parse = *Push() ARBNO(*Command) *Top() → stack correct ✓
      - FENCE + alternates inside ARBNO → correct ✓
      - *Parse (via Graft) with ARBNO inside → correct ✓
    The prior session's "ARBNO(*P) semantic actions never fire" finding was
    a test artifact: 'ABC' ARBNO(p) (no anchoring) succeeds with 0 iterations
    because ARBNO(epsilon) matches at position 0. With POS(0)/RPOS(0) forcing
    full-string match, it works correctly. The Graft fix is sound.

    ROOT CAUSE IS ELSEWHERE — narrowed to beauty.sno's Stmt/Command/Reduce interaction:
    - Command = nInc() FENCE(*Comment~'Comment'(..)nl | *Control~'Control'(..)nl | *Stmt(..)7 nl)
    - *Stmt arm calls Reduce('Stmt', 7) — pops 7 items from the tree stack
    - For input 'START\n' (label-only statement), some of the 7 slots are empty/wrong type
    - Reduce() pops a PatternVar (one of the OPSYN'd operators stored as pattern)
      instead of a tree node — that PatternVar lands in a tree child slot
    - Later pp() calls t(x) → GetProgramDefinedDataField → PatternVar cast crash

    ARCHITECTURE NOTE — semantic.sno OPSYN design:
    - OPSYN('~', 'shift', 2): p ~ 'Label' calls shift(p, 'Label') at BUILD TIME
      → returns pattern: p . thx . *Shift('Label', thx)
    - OPSYN('&', 'reduce', 2): p & 'nTop()' calls reduce(p, 'nTop()') at BUILD TIME
      → returns pattern: epsilon . *Reduce('Parse', nTop())  [n is a string, evaluated at match time]
    - nPush/nInc/nTop/nPop all return PATTERNS (epsilon . *PushCounter() etc.)
      evaluated at BUILD TIME; side effects fire at MATCH TIME via *fn()

    NEXT SESSION must:
    1. Instrument Reduce() in ShiftReduce.sno to OUTPUT the DATATYPE of each
       popped item when xTrace > 0. Run self-host on 'START\n' with xTrace=1.
       Identify which of the 7 pops returns a PatternVar.
    2. Trace which sub-pattern of Stmt produces the bad value. Stmt parses:
       Label + White + Expr14 + (pattern|assignment) + Goto + Gray → 7 slots.
       For 'START\n': Label='START', everything else is epsilon/empty.
       Verify each ~ 'tag' call correctly produces a tree node for empty matches.
    3. Fix: ensure epsilon ~ 'tag' produces a proper null/empty tree node,
       not a PatternVar, when the matched value is empty.
    4. ALTERNATIVELY (simpler): harden GetProgramDefinedDataField in Data.cs:206
       to handle PatternVar gracefully (return null/empty tree) rather than crashing,
       then check if beauty output becomes correct.
    5. Run beauty gate (must stay 17/17), then self-host.

    - snobol4dotnet HEAD: ec59eeb (unchanged)
    - corpus HEAD: 7d26569 (unchanged)

  SESSION WORK (this session — crash localized to BuildMain, not match time):
    - Beauty gate confirmed 17/17 at session start (HEAD ec59eeb)
    - FRETURN investigation: confirmed FRETURN works for standalone calls with
      explicit :S/:F goto. For calls embedded in RHS with no goto, statement
      correctly fails and falls through. No FRETURN bug affecting self-host.
    - Added stack-unwind in CallFuncBySlot (MsilHelpers.cs) after handler sets
      Failure=true: unwinds SystemStack to StatementSeparator. Beauty 17/17 still
      passes. Committed as dcf6457.
    - KEY FINDING: crash at Data.cs:206 fires at BUILD TIME (BuildMain), not
      during match. Confirmed by xTrace experiment: crash happens before any
      Reduce/Shift trace fires, during parser pattern construction in beauty.sno.
    - Stack trace: BuildMain → ExecuteLoop → (pattern build stmt) →
      CallFuncBySlot → ExecuteProgramDefinedFunction → ExecuteLoop →
      (treeNode field accessor t/v/n/c) → CallFuncBySlot →
      GetProgramDefinedDataField → PatternVar cast crash at line 206.
    - The crash is during OPSYN/reduce()/shift() calls that build patterns at
      load time — something in the pattern construction chain calls t()/v()/n()/c()
      with a PatternVar argument.
    - Prior session hypothesis about *P reading P's build-time initializer is
      likely correct; needs confirmation in Lexer.cs ExtractStarExpressions /
      CreateSimpleStarExpression.

  SESSION WORK (this session — Data.cs hardened, self-host now reaches Parse Error):
    - Data.cs:206 hardened: guarded pattern match replaces hard cast.
      PatternVar (or any non-ProgramDefinedDataVar) now returns FRETURN cleanly.
    - Beauty gate: 17/17 PASS (unchanged)
    - Self-host: InvalidCastException eliminated. Now outputs 26 lines then
      'Parse Error' — mainErr1 path fires on 'START\n' (label-only statement).
    - Root cause: ARBNO(*Command) fails to parse label-only stmt in Parse pattern.
      Stmt has epsilon ~ '' for all optional slots; Reduce('Stmt', 7) may receive
      a bad type (PatternVar?) for one of the 7 slots when all are epsilon.
    - snobol4dotnet HEAD: 1c27d52
    - corpus HEAD: 7d26569 (unchanged)

  NEXT SESSION must:
    1. Instrument Reduce() in ShiftReduce.sno: add OUTPUT of DATATYPE of each
       popped item when xTrace > 0. Run self-host on 'START\n' with xTrace=1.
       Identify which of the 7 Reduce('Stmt',7) pops returns a PatternVar.
    2. Trace which sub-pattern of Stmt produces the bad value for empty match.
       Stmt slots: Label, White, Expr14, (pattern|assignment), Goto, Gray → 7.
       For 'START\n': Label='START', all else epsilon.
       Verify epsilon ~ 'tag' produces a proper null/empty tree node, not PatternVar.
    3. Fix: ensure epsilon ~ 'tag' gives a correct tree node for empty matches.
    4. Run beauty gate (must stay 17/17), then self-host gate (SELF-HOST PASS).

    - snobol4dotnet HEAD: 1c27d52
    - corpus HEAD: 7d26569 (unchanged)


  SESSION WORK (this session — MINIMAL REPRO FOUND, prior theory invalidated):
    Beauty gate 17/17 confirmed at session start (HEAD 1c27d52).

    INSTRUMENTATION RESULT invalidates prior hypothesis:
      Added unconditional OUTPUT trace to both Shift() and Reduce() in ShiftReduce.sno.
      Ran self-host with input '&FULLSCAN = 1\n' (simpler than 'START\n' — same failure).
      Confirmed "DEBUG: ShiftReduce.sno loaded" fires at load time.
      Then Parse Error fires.
      NEITHER Shift NOR Reduce is ever called. Zero semantic actions during Parse.
      Prior "Reduce('Stmt',7) pops a bad PatternVar" hypothesis is WRONG —
      Reduce never runs, so it can't pop anything.

    BISECTED TO SHARP MINIMAL REPRO — 2-arg DEFINE kills pattern callbacks:

    REPRO-FAILS (Shift callback never fires during match):
           DEFINE('Shift(t,v)')
           DEFINE('shift(p,t)','shift_')                         :(setup_end)
    Shift  OUTPUT = 'SHIFT(' t ', v=[' v '])'                    :(NRETURN)
    shift_ shift = EVAL("p . thx . *Shift('" t "', thx)")        :(RETURN)
    setup_end
           x = 'ABC' CHAR(10)
           L1 = shift(BREAK(' ' CHAR(10) ';'), 'Label')
           x POS(0) L1                                           :S(ok)F(fail)
    ok     OUTPUT = 'match passed'                               :(END)
    fail   OUTPUT = 'match failed'
    END
    Result: prints 'match passed' but never 'SHIFT(...)'.

    REPRO-WORKS (identical body, only DEFINE form differs):
           DEFINE('Shift(t,v)')
           DEFINE('shift1(p,t)')                                 :(setup_end)
    Shift  OUTPUT = 'SHIFT(' t ', v=[' v '])'                    :(NRETURN)
    shift1 shift1 = EVAL("p . thx . *Shift('" t "', thx)")       :(RETURN)
    setup_end
           x = 'ABC' CHAR(10)
           L1 = shift1(BREAK(' ' CHAR(10) ';'), 'Label')
           x POS(0) L1                                           :S(ok)F(fail)
    Result: prints 'SHIFT(Label, v=[ABC])' then 'match passed'.

    QUIRK — when BOTH 1-arg and 2-arg defined functions appear in the same program,
    BOTH fire correctly regardless of call order. Feels like MSIL / ExecutionCache
    decides something on the whole-program function set. Consistent with prior
    session's "R_PAREN_FUNCTION falls back / ThreadIsMsilOnly=true / MSIL fix
    never fires" note.

    CONCLUSION — THIS is S-2's root cause.
    semantic.sno uses 2-arg DEFINE for EVERY helper:
      DEFINE('shift(p,t)',  'shift_')
      DEFINE('reduce(t,n)', 'reduce_')
      DEFINE('pop()',       'pop_')
      DEFINE('nPush()',     'nPush_')   etc.
    So every *Shift, *Reduce, *PushCounter, *IncCounter, *TopCounter, *PopCounter,
    *PopDummy callback embedded in every parser pattern built via ~ or & silently
    fails to fire during match. Parse matches structurally (ARBNO accepts 0 Commands),
    stack stays empty, Pop() returns '', pp('') crashes or errors downstream.

  NEXT SESSION must:
    1. Instrument the runtime to confirm: what's different in the pattern graph
       compiled for a 2-arg vs 1-arg DEFINE'd function that returns a pattern with
       a *Callback reference?
       Likely places:
         - Builder.cs / DefineImpl — how the function entry is registered
         - FunctionSlotIndex — is 2-arg slot populated differently?
         - BuilderEmitMsil.cs R_PAREN_FUNCTION — prior session noted the MSIL
           fallback doesn't wire properly when function is DEFINE'd at runtime
           (2-arg form is runtime DEFINE).
         - ExecutionCache.cs — is the pattern being cached with a stale version
           missing the callback?
    2. Try: run snobol4dotnet with MSIL cache / ThreadIsMsilOnly disabled on
       repro19.sno. If Shift then fires, that confirms MSIL is the culprit.
    3. Minimal fix attempt: in DefineImpl, ensure 2-arg form creates the same
       FunctionSlotIndex entry shape as 1-arg form.
    4. Beauty gate 17/17 must still pass after fix.
    5. Self-host gate: SELF-HOST PASS.

    - snobol4dotnet HEAD: 1c27d52 (unchanged — this session diagnosis only, no code)
    - corpus HEAD: 7d26569 (unchanged)
    - Beauty gate: 17/17 PASS (verified end-of-session)


  SESSION WORK (this session — ROOT CAUSE FIXED for prior repros, new error 109 surfaces):

    PRIOR THEORY INVALIDATED.  The "2-arg DEFINE breaks pattern callbacks" theory
    from last session was wrong.  Both 1-arg and 2-arg DEFINE forms had the SAME
    bug.  Real root cause:

    BUG: `AmpCaseFolding` field defaults to `1` (fold ON) and was never seeded
    from the `-f` command-line flag.  When `EVAL` runs, it does:
        Parent.BuildOptions.CaseFolding = AmpCaseFolding != 0;
    to restore the user's `&CASE` keyword setting.  This temporarily flipped
    CaseFolding back to `true` even with `-bf`, folding identifiers like
    `Shift` to `SHIFT` inside the EVAL'd pattern.  At match time, *Shift's
    function call looked up `'SHIFT'` in FunctionTable -> not found -> error 22.

    FIX (snobol4dotnet 13bfcc0):  ApplyStartupOptions seeds AmpCaseFolding=0
    when -f is set.  8-line minimal diff in Builder.cs.

    VERIFICATION:
      - Beauty 17/17 PASS (unchanged, no regression)
      - Original S-2 minimal repros from goal file (REPRO-FAILS and REPRO-WORKS):
        BOTH PASS now; output matches SPITBOL exactly:
          SHIFT(Label, v=[ABC])
          match passed
      - Isolated EVAL+star repros (t3, t4, t10, t11, t13, t17, t18 — see
        instrumented test sequence in commit message of 13bfcc0): ALL PASS
      - Self-host PROGRESS: was 16-line output (Parse Error on START),
        now 35-line output reaching `&FULLSCAN = 1` before failing with
        new bug -- error 109 in ShiftReduce.inc

    NEW BUG SURFACED (now the actual S-2 blocker):

    Self-host on `&FULLSCAN = 1` input fails with:
      ShiftReduce.inc(3/3/3): error 109 -- ge first argument is not numeric
                     c              =    GE(n, 1) ARRAY('1:' n)

    Reduce trace shows `n` arrives as DATATYPE(n)='expression' (an
    ExpressionVar), not integer.  The expression is `*(GT(nTop(),1) nTop())`
    which IS what beauty's grammar passes via the `&` OPSYN reduce wiring:
        ("'|'" & '*(GT(nTop(),1) nTop())')
    -> reduce("'|'", "*(GT(nTop(),1) nTop())")
    -> EVAL("epsilon . *Reduce('|', *(GT(nTop(),1) nTop()))")

    Inside that EVAL'd pattern, `*(GT(nTop(),1) nTop())` is in function-arg
    position to `*Reduce`.  snobol4dotnet pushes it as ExpressionVar (deferred)
    rather than evaluating it eagerly.  When *Reduce fires, `n` is the
    ExpressionVar.  ShiftReduce.inc tries `IDENT(DATATYPE(n), 'EXPRESSION')`
    to detect this and EVAL it -- but DATATYPE returns lowercase 'expression'
    while the test compares uppercase 'EXPRESSION', so the IDENT fails under
    case-sensitive `-f` mode and falls through to `GE(ExpressionVar, 1)` ->
    error 109.

    THREE POSSIBLE FIX APPROACHES (none committed this session):

    A. Make snobol4dotnet evaluate ExpressionVar args eagerly when calling
       user-defined functions (matches SPITBOL semantics).  Tried this:
       added EvaluateExpressionArgs in Function() and CallFuncBySlot().
       BLOCKER: also fires during BUILD-TIME grammar construction calls
       like `reduce(t, n)` where n is a string -> EVAL builds the pattern
       -- but the pattern is then used as left-side of an assignment
       `snoStmt = reduce_result`, which evaluates left-side ExpressionVars
       in Assign().  That sub-thread runs OUTSIDE Scanner so a ScanDepth
       gate doesn't help: ScanDepth=0 when Reduce ultimately fires inside
       the grafted pattern.  All revert: no code changes survived.

    B. Fix ExpressionVar's PATTERN conversion to evaluate eagerly when the
       result is non-pattern (integer, string).  Likely the cleaner fix.
       In IntegerConversionStrategy.cs, the EXPRESSION case wraps integers
       as ExpressionVar by re-compiling them as star-expressions.  This is
       wrong direction; a star-expression that yielded an integer should
       BE the integer when used as a function argument.

    C. Patch beauty source: change `IDENT(DATATYPE(n), 'EXPRESSION')` to
       compare case-insensitively.  Per RULES.md "Portable tests only"
       (DATATYPE Portable Tests goal), this is what corpus tests are
       supposed to do anyway:
           dEXPR = REPLACE(DATATYPE(*(0)), &LCASE, &UCASE)
           ...
           IDENT(REPLACE(DATATYPE(n), &LCASE, &UCASE), dEXPR)
       But RULES.md ALSO says "never patch corpus to work around runtime
       bugs" -- and SPITBOL handles this case without needing the EXPRESSION
       branch (it never produces ExpressionVar from `*(integer)`).  So this
       is a runtime bug, not a corpus bug.

    RECOMMEND APPROACH B for next session: make IntegerConversionStrategy
    (and similar) convert to PATTERN by producing a SucceedPattern (or
    proper terminal) wrapping the value, NOT wrapping as another
    ExpressionVar.  Then `*(GT(nTop(),1) nTop())` evaluates to integer 7,
    which when needed as a pattern wraps to a pattern-of-int-7, and when
    needed as a function arg passes as integer 7.

    SIDE NOTE: Three corpus include files (is.inc, FENCE.inc, io.inc) had
    to be copied into demo/beauty/ for self-host to find them, since
    snobol4dotnet's -INCLUDE searches CWD only (no -I or SETL4PATH support).
    These copies were temporary and cleaned up at session end.  Adding
    -I include-path support to snobol4dotnet's CommandLine.cs is a
    follow-on (independent of S-2).

    - snobol4dotnet HEAD: 13bfcc0 (committed and pushed)
    - corpus HEAD: 7d26569 (unchanged)
    - Beauty gate: 17/17 PASS (verified end-of-session)
    - Self-host: now reaches `&FULLSCAN = 1`, fails with error 109 on
      ExpressionVar arg to Reduce

  SESSION WORK (Sun Apr 26 evening — runtime errors fixed, parser still blocks):

    Approach B (from prior session's recommended fixes) implemented:
    on-demand evaluation of ExpressionVar in non-pattern conversion
    contexts.  Three small changes in snobol4dotnet (commit 0914fbf):

      • Var.cs ToNumeric: ExpressionVar arg → run DeferredCode, pop
        result, recurse for numeric extraction.
      • NumericComparisonHelper.cs BinaryComparison: when ToNumeric
        fails because Failure was already set by the deferred eval,
        use NonExceptionFailure() instead of error 109/110/etc.
      • NumericHelper.cs BinaryNumericOperation: same propagation rule
        for +, -, *, /, ^ (errors 1, 2, 12, 16, 26, 32).

    Approach A (eager-evaluate ExpressionVar in ExtractArguments) was
    tried first and **regressed Qize/XDump/omega** drivers.  Root
    cause: the *assign(.part, *'literal') idiom in Qize.inc relies on
    `expression` arriving at the user-defined `assign` function as
    EXPRESSION so it can `EVAL(expression)` later.  Eager evaluation
    in ExtractArguments breaks that idiom.  Reverted; replaced with
    the on-demand strategy in conversion sites only.  Build-time
    `reduce(t, n)` calls are also unaffected because their args are
    StringVar (the EVAL'd source string), not ExpressionVar.

    Also discovered: `_reusableArgList` is shared across recursive
    Function/Operator calls; running DeferredCode mid-ExtractArguments
    corrupts the list (ArgumentOutOfRangeException).  Documented but
    not exploited — the on-demand fix sidesteps the issue.

    Self-host result on this clone:
      • All `error 109` lines: gone.
      • All `error 1` lines: gone.
      • Output is now clean up to "Parse Error" on the first
        non-comment statement.
      • Tiny inputs that succeed: comment-only, label-only `START\n`,
        `END`-only.
      • Tiny input that fails (Parse Error): `              x = 1`.

    Conclusion: the runtime is now SPITBOL-compatible enough for the
    Reduce/EVAL deferred-expression chain.  The remaining S-2 work is
    the **pattern engine** — `nPush() ARBNO(*Command) *Top()` only
    matches at zero-Command count.  Same territory as multiple prior
    sessions; the Graft fix from 826d4ff handles direct `*P` but not
    the nested-star case that `*Command` ultimately compiles to via
    the `&` OPSYN chain.

  NEXT SESSION must:
    1. Write a minimal repro outside beauty: e.g.
         X = ('a' . *push) | ('b' . *push)
         Parse = nPush() ARBNO(*X) *Top()
         'aab' POS(0) *Parse RPOS(0)
       Expect 3 push calls.  If <3, that's the same root cause.
    2. Re-investigate ArbNoPattern.Scan + UnevaluatedPattern.Scan
       interaction.  Specifically: when an ARBNO body is `*X` and
       `X` itself contains `*Y` callbacks, do those callbacks run
       AND does ARBNO see the alternates needed for backtracking?
    3. After fix: beauty 17/17 must pass; self-host gate must produce
       SELF-HOST PASS (≥500 stderr lines, exit 0, no error markers).
    4. Side task (independent): add `-I` include-path support to
       CommandLine.cs so beauty.sno can self-host without copying
       is.inc/FENCE.inc/io.inc into demo/beauty/.  Goal-file already
       notes the temp-copy trick is not the answer.

    - snobol4dotnet HEAD: 0914fbf (committed and pushed)
    - corpus HEAD: 7d26569 (unchanged)
    - Beauty gate: 17/17 PASS (verified end-of-session)
    - Self-host: runtime errors eliminated; Parse Error on assignment
      remains (graft + ARBNO interaction)
