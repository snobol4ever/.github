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
