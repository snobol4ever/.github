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

  NEXT SESSION must complete:
    1. Add Scanner.Graft(Pattern, int successorNode) -> int graftedStart
    2. Handle GOTO in Scanner.Match loop
    3. Rewrite UnevaluatedPattern.Scan to use Graft + MatchResult.Goto
    4. Build + verify minimal repro passes
    5. Run beauty suite gate (must stay 18/18)
    6. Run unit tests + commit + push

- [ ] **S-3** — Gate: `diff /tmp/beauty_self_clean.txt beauty_selftest.sno` is empty. Output: `SELF-HOST PASS`. ✅

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.
