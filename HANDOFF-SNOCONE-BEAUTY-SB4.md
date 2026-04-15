# HANDOFF — GOAL-SNOCONE-BEAUTY SB-4 (beauty.sc parse truncation)

**Date:** 2026-04-15
**Goal:** GOAL-SNOCONE-BEAUTY.md, step SB-4
**Repos:** one4all HEAD db91b92c (unchanged), corpus, x64, csnobol4 — all built.
**Context at handoff:** ~87%

---

## What Was Accomplished This Session

SB-1, SB-2, SB-3 all DONE (previous sessions). This session diagnosed the SB-4
blocker completely and ruled out several false leads.

---

## The Bug (diagnosed, NOT yet fixed)

### Symptom
Running beauty.sc with any input produces **no output** — complete silence.
Execution reaches line 44 (end of args-parsing while loop) but never reaches
line 45 onward.

### Root cause (confirmed by binary search)

`beauty.sc` line 45 — `if (DIFFER(ppAutoMode)) {` — opens a block that is
**never closed at the parser level** as far as the Snocone frontend is concerned.
Something inside the `if` block (lines 45–97) contains a construct that the
Snocone parser **silently fails on**, causing it to discard everything from that
point forward (including the closing `}` at line 97 and all subsequent code).

The **sentinel test** (append `OUTPUT = 'SENTINEL';` after line N) confirmed:
- Lines 1–44 + sentinel: SENTINEL fires ✅
- Lines 1–45 + sentinel: SENTINEL does NOT fire ❌

This is NOT a missing `}` — the file is syntactically complete. It is a
**silent parse error** inside the if block that causes the Snocone parser to
drop the rest of the file without any error message.

### What was ruled out

- `input_read()` EOF caching — NOT the issue (basic INPUT loops work fine)
- `DIFFER()` semantics — correct (ppAutoMode is '' → block should be skipped)
- `ReadWrite.sno` hang — separate issue (`err` label unresolved in sm_lower);
  ReadWrite.sno is NOT needed by beauty.sc (beauty.sc never calls Read/Write)
- Polyglot multi-file approach — works for all other .sno libs; ReadWrite.sno
  excluded from the invocation to avoid the hang

### What's inside lines 45–97 that might cause silent parse failure

Lines 45–97 are the `--auto` two-pass mode block. Key constructs:
- Line 47: `ppSpOrEps = SPAN(' ' && ppTab) | epsilon;`
- Line 51: `ppGSfx = *ppSpOrEps && ':' && *ppSFOrEps && *ppBrOrEps && REM;`
- Line 52: `ppGPat = BREAK(':') . ppGCon && *ppGSfx;`
- Line 55: `ppTmpFile = '/tmp/beauty_auto_' && HOST(1) && '.sno';`
- Line 56: `output__(.ppTmp, 3, '', ppTmpFile);`
- Line 96: `input__(.INPUT, 1, '', ppTmpFile);`
- Line 91: multiline string continuation with `&&`

Individual constructs tested in isolation all work. The failure is triggered by
**something in the combination** — most likely a multi-line expression or an
unusual pattern construct that confuses the Snocone parser within an if block
body when preceded by the args-parsing while loop code.

### Next Action (SB-4 fix)

**Step 1 — Find the exact failing construct:**

```bash
cd /home/claude/one4all
python3 << 'PYEOF'
import subprocess

lines = open('test/beauty-sc/beauty/beauty.sc').readlines()

# We know failure starts inside lines 45-97.
# Now bisect WITHIN that range using complete blocks:
# Strategy: take lines 1-44, add lines 45..N one at a time, close any open
# block with "}", then add sentinel. Find first N where sentinel doesn't fire.

for n in range(45, 98):
    # Build: lines 1-44, then lines 45..n, then close block, sentinel
    chunk = lines[:44] + lines[44:n] + ['}\n', "OUTPUT = 'SENTINEL';\n"]
    with open('/tmp/bisect.sc', 'w') as f:
        f.writelines(chunk)
    result = subprocess.run(
        ['./scrip', '--ir-run', '/tmp/bisect.sc'],
        input=b'x\n', capture_output=True, timeout=5
    )
    fired = b'SENTINEL' in result.stdout
    print(f"n={n}: {'OK' if fired else 'FAIL'} -- {lines[n-1].rstrip()}")
    if not fired:
        print(f"\n*** First failing line: {n}")
        print(f"*** Content: {lines[n-1].rstrip()}")
        break
PYEOF
```

**Step 2 — Fix the Snocone parser** to handle whatever construct fails.
The fix will be in `src/frontend/snocone/snocone_parse.c` or `snocone_lex.c`.

**Step 3 — Verify fix:**
```bash
cd /home/claude/one4all
INC=/home/claude/corpus/programs/snobol4/beauty
for case in 101_comment 102_output 103_assign 104_label 105_goto 109_multi; do
  input=/home/claude/corpus/crosscheck/beauty/${case}.input
  ref=/home/claude/corpus/crosscheck/beauty/${case}.ref
  got=$(./scrip --ir-run \
    $INC/global.sno $INC/case.sno $INC/assign.sno $INC/match.sno \
    $INC/counter.sno $INC/stack.sno $INC/tree.sno \
    $INC/ShiftReduce.sno $INC/TDump.sno $INC/Gen.sno $INC/Qize.sno \
    $INC/XDump.sno $INC/semantic.sno \
    $INC/omega.sno $INC/trace.sno \
    test/beauty-sc/beauty/beauty.sc < "$input" 2>/dev/null)
  expected=$(cat "$ref")
  [ "$got" = "$expected" ] && echo "PASS $case" || echo "FAIL $case"
done
```

**Step 4 — Broker gate before commit:**
```bash
bash scripts/test_smoke_unified_broker.sh  # expect PASS=38 FAIL=0
```

**Step 5 — Commit and push:**
```bash
cd /home/claude/one4all
git add -A && git commit -m "SB-4: fix Snocone parser silent failure in beauty.sc if block"
git pull --rebase && git push
```

Then update GOAL-SNOCONE-BEAUTY.md SB-4 checkbox and PLAN.md state, commit .github.

---

## Task 2 (parallel, can start after SB-4 fix)

Convert each `.sno` library to `.sc` (Snocone port). Files in order:
```
/home/claude/corpus/programs/snobol4/beauty/global.sno  → test/beauty-sc/global/global.sc
/home/claude/corpus/programs/snobol4/beauty/case.sno    → test/beauty-sc/case/case.sc
... (one per subsystem)
```
Note: ReadWrite.sno has an unresolved `err` label (`:F(err)` in Write with no
`err` label defined). This is NOT a corpus bug — SPITBOL treats undefined goto
targets as program termination. The `.sc` port should use `freturn;` instead.
The sm_lower unresolved-label issue is a separate runtime bug to fix eventually.

---

## Key paths

| File | Purpose |
|------|---------|
| `test/beauty-sc/beauty/beauty.sc` | The Snocone main program (line 45 = parse failure start) |
| `src/frontend/snocone/snocone_parse.c` | Parser — where to fix |
| `src/frontend/snocone/snocone_lex.c` | Lexer — may also need fix |
| `/home/claude/corpus/crosscheck/beauty/` | 6 crosscheck cases (input + .ref) |
| `/home/claude/corpus/programs/snobol4/beauty/` | SNOBOL4 .sno include files |
| `scripts/test_smoke_unified_broker.sh` | Gate: PASS=38 FAIL=0 |

## Invocation (without ReadWrite.sno)
```bash
cd /home/claude/one4all
INC=/home/claude/corpus/programs/snobol4/beauty
./scrip --ir-run \
  $INC/global.sno $INC/case.sno $INC/assign.sno $INC/match.sno \
  $INC/counter.sno $INC/stack.sno $INC/tree.sno \
  $INC/ShiftReduce.sno $INC/TDump.sno $INC/Gen.sno $INC/Qize.sno \
  $INC/XDump.sno $INC/semantic.sno \
  $INC/omega.sno $INC/trace.sno \
  test/beauty-sc/beauty/beauty.sc
```
