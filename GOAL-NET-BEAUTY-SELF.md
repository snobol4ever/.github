# GOAL-NET-BEAUTY-SELF — snobol4dotnet Beauty Self-Hosting

**Repo:** snobol4dotnet
**Depends on:** GOAL-NET-BEAUTY-19 must be complete (19/19)
**Done when:** beauty.sno reads itself as INPUT, writes itself to OUTPUT, output matches input exactly

## What this means

beauty.sno is a SNOBOL4 beautifier. A beautifier is idempotent on already-beautified
source — feeding beauty.sno to itself should produce beauty.sno unchanged.

## Known issue

SPITBOL also fails on beauty.sno self-input with error 021 ("function called by name
returned a value") after 777 statements. This is a bug in beauty.sno itself triggered
by SNOBOL4 source containing `-INCLUDE` directives and `*funcname` pattern definitions.
The fix may require changes to beauty.sno, not just snobol4dotnet.

## Test command

```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
cd /home/claude/corpus/programs/snobol4/demo/inc

dotnet $SNO4 -b beauty.sno < beauty.sno > /dev/null 2>/tmp/beauty_self.txt || true
grep -v "^Unhandled\|^ at \|^Aborted" /tmp/beauty_self.txt > /tmp/beauty_self_clean.txt
diff /tmp/beauty_self_clean.txt beauty.sno && echo "SELF-HOST PASS" || echo "SELF-HOST FAIL"
```

## Steps

- [ ] **S-1** — Diagnose error 021 on beauty.sno self-input. Confirm whether bug is in beauty.sno or snobol4dotnet. Run same test under SPITBOL to establish oracle behavior.

- [ ] **S-2** — Fix root cause. If beauty.sno bug: patch beauty.sno (with SPITBOL confirming fix). If snobol4dotnet bug: fix in runtime.

- [ ] **S-3** — Gate: `diff /tmp/beauty_self_clean.txt beauty.sno` is empty. Output: `SELF-HOST PASS`. ✅

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`. This bit us in bc19645 (200+ Windows test failures). Every string built with newlines must use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.
