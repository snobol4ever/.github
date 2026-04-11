# MILESTONE-NET-BEAUTY-SELF.md — Beauty Self-Hosting in snobol4dotnet

**Session prefix:** D
**Repo:** snobol4dotnet
**Depends on:** MILESTONE-NET-BEAUTY-19.md (19/19 gate)
**Goal:** beauty.sno reads itself as INPUT and writes itself to OUTPUT — output matches input exactly.

---

## What "self-hosting" means here

beauty.sno is a SNOBOL4 beautifier. A beautifier is idempotent on already-beautified source:
feeding beauty.sno to itself should produce beauty.sno unchanged (modulo whitespace normalization).

The test:
```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
cd /home/claude/corpus/programs/snobol4/demo/inc

dotnet $SNO4 -b beauty.sno < beauty.sno > /dev/null 2>/tmp/beauty_self.txt || true
grep -v "^Unhandled\|^ at \|^Aborted" /tmp/beauty_self.txt > /tmp/beauty_self_clean.txt
diff /tmp/beauty_self_clean.txt beauty.sno && echo "SELF-HOST PASS" || echo "SELF-HOST FAIL"
```

**Gate:** diff is empty — output equals input. ✅

---

## Current status: FAIL

beauty.sno crashes with error 021 ("function called by name returned a value") after
outputting only the first 7 comment lines. It processes a handful of statements (777 executed)
then aborts.

**Confirmed with SPITBOL oracle:** SPITBOL also fails with error 021 on beauty.sno self-input.
This is not a snobol4dotnet-only bug — it is a bug in beauty.sno itself triggered by feeding
it SNOBOL4 source containing `-INCLUDE` directives and pattern definitions with `*funcname`.

---

## Prerequisite: beauty 19/19

Self-hosting cannot be verified until all beauty subsystems pass. The error 021 occurs
in the main beauty.sno loop when processing non-trivial SNOBOL4 statements. Most likely
caused by one of:
- FENCE redefinition (B-BEAUTY-0)
- `*funcname` side-effect returning value in wrong context (related to NRETURN handling)
- Pattern grammar in beauty.sno triggering an edge case in the match engine

---

## Milestone ladder

### B-SELF-0 — Prerequisite: beauty 19/19
Complete MILESTONE-NET-BEAUTY-19.md B-BEAUTY-0 through B-BEAUTY-9.

### B-SELF-1 — Diagnose error 021 on self-input
Run beauty.sno < beauty.sno with STLIMIT tracing to find exactly which statement
triggers error 021. Compare with SPITBOL behavior line by line.
**Gate:** know exactly which line/pattern causes the crash.

### B-SELF-2 — Fix error 021
Error 021 = "function called by name returned a value" — a `*funcname` pattern
side-effect function returned non-null when called via name. Fix the relevant
NRETURN path in snobol4dotnet's function call machinery.
**Gate:** beauty.sno < beauty.sno runs to END without error.

### B-SELF-3 — Output matches input
After running to completion, verify output equals input.
**Gate:** `diff output beauty.sno` is empty → **SELF-HOST PASS** ✅

---

*MILESTONE-NET-BEAUTY-SELF.md — created D-214b, 2026-04-11, Claude Sonnet 4.6*
