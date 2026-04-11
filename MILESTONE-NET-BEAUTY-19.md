# MILESTONE-NET-BEAUTY-19.md — Beauty Suite 19/19 in snobol4dotnet

**Session prefix:** D
**Repo:** snobol4dotnet
**Baseline established:** D-214b (2026-04-11)
**Baseline:** 7/19 pass (after SourceCode.cs fix)
**Gate:** 19/19 pass — all beauty drivers produce output matching .ref

---

## How to run

```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
cd /home/claude/corpus/programs/snobol4/beauty   # includes symlinked here from demo/inc

PASS=0; FAIL=0
for driver in beauty_*_driver.sno; do
    name="${driver%_driver.sno}"
    dotnet $SNO4 -b "$driver" > /dev/null 2>/tmp/err.txt || true
    grep -v "^Unhandled\|^ at \|^Aborted" /tmp/err.txt > /tmp/actual.txt
    if diff -q /tmp/actual.txt "${driver%.sno}.ref" > /dev/null 2>&1; then
        PASS=$((PASS+1))
    else
        echo "FAIL: $name"; FAIL=$((FAIL+1))
    fi
done
echo "$PASS/19"
```

**Note:** OUTPUT goes to Console.Error (stderr) in snobol4dotnet. The CWD line goes to stdout. Filter stderr, strip exception stack lines.

**Note:** Include files must be findable from the driver's directory. Symlink `demo/inc/*` into `corpus/programs/snobol4/beauty/` once per machine.

---

## Current status: 7/19 pass

### Passing (7)
- beauty_Qize ✅
- beauty_assign ✅
- beauty_case ✅
- beauty_counter ✅
- beauty_global ✅
- beauty_match ✅
- beauty_stack ✅

### Failing (12) — root causes

| Driver | Error | Root cause |
|--------|-------|------------|
| **fence** | error 248 — redefinition of system function | `DEFINE('FENCE(FENCE)')` — snobol4dotnet rejects FENCE redefinition |
| **Gen** | error 248 — redefinition of system function | same FENCE issue (Gen includes FENCE.sno) |
| **io** | error 248 — redefinition of system function | same FENCE issue |
| **ReadWrite** | error 117 — input file cannot be read | Unit-file INPUT association (`.rdInput`) not supported |
| **ShiftReduce** | UNEXPECTED EXCEPTION | unhandled runtime exception — needs investigation |
| **TDump** | FAIL: TLump leaf/node format | TLump output format mismatch — `.x.42` vs `(BinOp x 42)` |
| **XDump** | error 108 — FIELD first arg not datatype name | `FIELD(objType, i)` — FIELD function not working correctly |
| **is** | FAIL: neither IsSnobol4 nor IsSpitbol | `&VERSION` keyword not recognized or wrong value |
| **omega** | FAIL: 1–15 patterns | Advanced pattern features (FENCE/ABORT semantics in omega context) |
| **semantic** | FAIL: 1–3 | Semantic analysis failures — needs investigation |
| **trace** | FAIL: 4–6 datatype=name | NAME datatype not returned correctly by DATATYPE() |
| **tree** | error 67 — array dim zero/negative | `ARRAY('1:0')` — zero-size array not supported |

---

## Milestone ladder

### B-BEAUTY-0 — FENCE redefinition (3 drivers: fence, Gen, io)
**Fix:** In `ThreadedExecuteLoop.cs` / function definition handler — allow `DEFINE('FENCE(FENCE)')` to redefine FENCE as a user function (SPITBOL allows this).
**Gate:** fence + Gen + io pass → **10/19**

### B-BEAUTY-1 — ARRAY('1:0') zero-length array (1 driver: tree)
**Fix:** Allow upper bound < lower bound to create zero-element array dimension.
**Gate:** tree passes → **11/19**

### B-BEAUTY-2 — DATATYPE() returns 'name' for NAME values (1 driver: trace)
**Fix:** `DATATYPE()` must return `'name'` when argument is a NAME (indirect reference).
**Gate:** trace passes → **12/19**

### B-BEAUTY-3 — &VERSION / IsSnobol4 keyword (1 driver: is)
**Fix:** `&VERSION` or equivalent keyword must identify snobol4dotnet correctly so `is.sno` IsSnobol4 check passes.
**Gate:** is passes → **13/19**

### B-BEAUTY-4 — FIELD function (1 driver: XDump)
**Fix:** `FIELD(datatypeName, index)` must return the field name at given index for a DATA-defined type.
**Gate:** XDump passes → **14/19**

### B-BEAUTY-5 — TLump format (1 driver: TDump)
**Fix:** Tree dump node format — `(BinOp x 42)` not `.x.42`. Investigate TDump.sno rendering.
**Gate:** TDump passes → **15/19**

### B-BEAUTY-6 — Unit-file INPUT association (1 driver: ReadWrite)
**Fix:** `INPUT(.varName, unit, filename)` file association for reading.
**Gate:** ReadWrite passes → **16/19**

### B-BEAUTY-7 — omega patterns (1 driver: omega)
**Fix:** Investigate omega driver failures — likely FENCE/ABORT interaction in complex patterns.
**Gate:** omega passes → **17/19**

### B-BEAUTY-8 — semantic (1 driver: semantic)
**Fix:** Investigate semantic driver — tests 1-3 fail.
**Gate:** semantic passes → **18/19**

### B-BEAUTY-9 — ShiftReduce (1 driver: ShiftReduce)
**Fix:** Investigate UNEXPECTED EXCEPTION in ShiftReduce driver.
**Gate:** ShiftReduce passes → **19/19** ✅

---

*MILESTONE-NET-BEAUTY-19.md — created D-214b, 2026-04-11, Claude Sonnet 4.6*
