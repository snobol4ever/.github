# GOAL-NET-BEAUTY-SELF — snobol4dotnet Beauty Self-Hosting

**Repo:** snobol4dotnet
**Depends on:** GOAL-NET-BEAUTY-19 must be complete (19/19)
**Done when:** beauty.sno reads itself as INPUT, writes itself to OUTPUT, output matches input exactly

## What this means

beauty.sno is a SNOBOL4 beautifier. A beautifier is idempotent on already-beautified
source — feeding beauty.sno to itself should produce beauty.sno unchanged.

## Test command

```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
cd /home/claude/corpus/programs/snobol4/beauty
cp /home/claude/corpus/programs/snobol4/demo/beauty.sno ./beauty_selftest.sno
dotnet $SNO4 -b beauty_selftest.sno < beauty_selftest.sno > /tmp/beauty_self_out.txt 2>/tmp/beauty_self_err.txt || true
grep -v "^Unhandled\|^ at \|^Aborted" /tmp/beauty_self_err.txt > /tmp/beauty_self_clean.txt
diff /tmp/beauty_self_clean.txt beauty_selftest.sno && echo "SELF-HOST PASS" || echo "SELF-HOST FAIL"
rm -f beauty_selftest.sno
```

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

- [ ] **S-3** — Gate: `diff /tmp/beauty_self_clean.txt beauty_selftest.sno` is empty. Output: `SELF-HOST PASS`. ✅

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

