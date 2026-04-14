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

- [ ] **S-2** — Fix root cause: self-host Parse hangs on label-only statements.
  FIXED (partial, a39f9c3): UnevaluatedPattern infinite backtrack loop.
  Root cause was UnevaluatedPattern._reScan=true calling SaveAlternate unconditionally;
  zero-length match created infinite C# loop. Fix: guard with mr.PostCursor > 0.
  Beauty suite still 18/18. No longer hangs.
  REMAINING: Parse("START\n") now returns "Parse Error" instead of hanging.
  The Stmt pattern still does not match label-only statements correctly under dotnet.
  Next: debug why *Stmt fails on "START\n" (no RPOS constraint) and fix.

- [ ] **S-3** — Gate: `diff /tmp/beauty_self_clean.txt beauty_selftest.sno` is empty. Output: `SELF-HOST PASS`. ✅

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.
