# MILESTONE-CSNOBOL4-FENCE.md — Add FENCE() to CSNOBOL4

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Created:** 2026-04-09
**Milestone name:** M-CSNOBOL4-FENCE
**Repo:** snobol4ever/x64 (SPITBOL — semantic guide) · CSNOBOL4 2.3.3 source

---

## Why

CSNOBOL4 lacks `FENCE()`. This is the primary reason CSNOBOL4 cannot serve as an
execution oracle for general SNOBOL4 programs (D-005). Any test using `FENCE` produces
wrong answers under CSNOBOL4.

CSNOBOL4 is the oracle for the **Silly SNOBOL4** session by construction (it IS the
reference implementation). Adding FENCE closes the last major semantic gap between
CSNOBOL4 and SPITBOL, eventually making CSNOBOL4 usable as a secondary validation tool
for programs that do not rely on SPITBOL-specific extensions.

SPITBOL x64 (`/home/claude/x64/bin/sbl`) remains the **sole execution oracle** for all
sessions (D-005). This milestone does not change that rule.

---

## FENCE Semantics (from SPITBOL)

`FENCE` is a pattern primitive (nullary function). When placed in a pattern:

```
subject  PAT1 FENCE PAT2  =replacement  :S(x)F(y)
```

- **During forward match:** FENCE succeeds with null match, consuming no subject.
- **During backtrack:** FENCE is **opaque** — backtrack cannot pass through it.
  If the pattern engine attempts to back up past a FENCE, the entire match FAILS
  immediately (no further alternation attempted).

Byrd box model: FENCE's β port fires the match's ω (failure continuation) directly,
bypassing any remaining alternation stack below the FENCE point. See `SM_PAT_FENCE`
in SCRIP-SM.md and `E_CUT` / `XFNCE=35` in GENERAL-SIL-HERITAGE.md.

**FENCE vs ABORT:**
- `FENCE` — blocks backtrack past this point; match may still fail normally above.
- `ABORT` — unconditionally terminates the entire statement (no S/F branch fires).
- `FENCE()` with argument — same as bare `FENCE` but the argument is evaluated first.

**Test oracle:**
```bash
cat > /tmp/fence_test.sno << 'END'
*  FENCE: backtrack blocked — output should be: OUTER FAIL
        X = 'ABC'
        X ('A' | 'X') FENCE ('B' | 'Y')   :S(MATCH)F(FAIL)
MATCH   OUTPUT = 'MATCH'                   :END
FAIL    OUTPUT = 'OUTER FAIL'
END
/home/claude/x64/bin/sbl -b /tmp/fence_test.sno
# Expected: OUTER FAIL  (FENCE blocks backtrack to try 'X' alternative)
```

---

## Source Location in CSNOBOL4

CSNOBOL4 2.3.3 source (Phil Budne): `snobol4ever/x64` → compare SPITBOL's pattern
engine for the FENCE node.

Key files to study in CSNOBOL4 source:
- `pat.c` / `pat.h` — pattern node types and match dispatch
- `snobol4.c` — generated from `v311.sil` — look for `XFNCE` (SIL opcode 35)
- `v311.sil` — `XFNCE = 35` is defined but may not have a match handler

Key files in SPITBOL (snobol4ever/x64) to use as semantic guide:
- `pattern.c` or equivalent — FENCE node Alpha/Beta implementation
- Byrd box: `SM_PAT_FENCE` — β port immediately calls ω

---

## Milestone Steps

### M-CSNOBOL4-FENCE-0 — Confirm the gap
```bash
cat > /tmp/fence_smoke.sno << 'END'
        OUTPUT = FENCE
END
# SPITBOL: prints empty string (FENCE matched as null pattern)
/home/claude/x64/bin/sbl -b /tmp/fence_smoke.sno
# CSNOBOL4: error or wrong result
/home/claude/work/snobol4-2.3.3/snobol4 /tmp/fence_smoke.sno
```
Gate: confirm CSNOBOL4 differs from SPITBOL on FENCE.

### M-CSNOBOL4-FENCE-1 — Locate FENCE in SPITBOL source
```bash
grep -rn "FENCE\|fence\|XFNCE" /home/claude/x64/src/ | head -30
```
Understand the node struct, Alpha function (succeeds null), Beta function (fires ω).

### M-CSNOBOL4-FENCE-2 — Add FENCE node to CSNOBOL4 pat.c
- Add `P_FENCE` node type constant to `pat.h`
- Add Alpha handler: match succeeds, advances cursor 0.
- Add Beta handler: directly invoke match failure (no alternation retry).
- Wire `FENCE` name lookup in pattern compiler to emit `P_FENCE` node.

### M-CSNOBOL4-FENCE-3 — Wire `FENCE()` function name
- Add `FENCE` to the built-in function table (returns a `P_FENCE` pattern node).
- `FENCE(expr)` — evaluate expr (for side effects), return `P_FENCE` node.

### M-CSNOBOL4-FENCE-4 — Gate tests
```bash
# All three must match SPITBOL output exactly:
/home/claude/x64/bin/sbl -b /tmp/fence_test.sno    # OUTER FAIL
/home/claude/work/snobol4-2.3.3/snobol4 /tmp/fence_test.sno  # must also: OUTER FAIL

# ABORT still works:
cat > /tmp/abort_test.sno << 'END'
        'ABC' ('A' | 'X') ABORT :S(MATCH)F(FAIL)
MATCH   OUTPUT = 'MATCH'  :END
FAIL    OUTPUT = 'FAIL'
END
/home/claude/x64/bin/sbl -b /tmp/abort_test.sno   # (program aborts — no output)
/home/claude/work/snobol4-2.3.3/snobol4 /tmp/abort_test.sno  # must match
```
Gate: CSNOBOL4 and SPITBOL agree on all FENCE/ABORT test cases.

### M-CSNOBOL4-FENCE-5 — Rebuild and validate Silly SNOBOL4 monitor
After CSNOBOL4 gains FENCE, rebuild the instrumented monitor binary and confirm
the Silly SNOBOL4 sync-step tests still pass. FENCE gap in Silly is inherited
from CSNOBOL4 — closing it in CSNOBOL4 source exposes any matching gap in Silly.

---

## Status

| Step | Status | Notes |
|------|--------|-------|
| M-CSNOBOL4-FENCE-0 | ⬜ | Confirm gap |
| M-CSNOBOL4-FENCE-1 | ⬜ | Study SPITBOL source |
| M-CSNOBOL4-FENCE-2 | ⬜ | Add node to pat.c |
| M-CSNOBOL4-FENCE-3 | ⬜ | Wire FENCE() builtin |
| M-CSNOBOL4-FENCE-4 | ⬜ | Gate tests pass |
| M-CSNOBOL4-FENCE-5 | ⬜ | Silly monitor validated |

---

*MILESTONE-CSNOBOL4-FENCE.md — created 2026-04-09, Claude Sonnet 4.6.*
