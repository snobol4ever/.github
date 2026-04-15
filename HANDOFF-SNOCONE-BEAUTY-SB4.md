# HANDOFF — GOAL-SNOCONE-BEAUTY SB-4 (INPUT EOF infinite loop)

**Date:** 2026-04-15
**Goal:** GOAL-SNOCONE-BEAUTY.md, step SB-4
**Repos:** one4all HEAD db91b92c, corpus, x64, csnobol4 — all built, no rebuild needed.
**Context at handoff:** ~79%

---

## What Was Accomplished This Session

SB-1, SB-2, SB-3 all DONE (previous sessions). This session diagnosed the SB-4 blocker completely.

---

## The Bug (diagnosed, NOT yet fixed)

### Symptom
Running beauty.sc with `echo "* a comment" | ./scrip --ir-run beauty.sc` produces **no output** and hangs (infinite loop).

The inner `while (Line ? (POS(0) && ANY('*-')))` loops forever — `Line` stays `'* a comment'` and is never updated because `Line = INPUT` inside the loop body keeps returning the old value after EOF.

### Confirmed root cause

`INPUT` past EOF in `--ir-run` mode **does not fail** — it keeps returning the last line read.

**Verified with test:**
```
echo "* a comment" | scrip --ir-run /tmp/test_multi_input.sc
# where test_multi_input.sc calls INPUT in a loop 5 times
# ALL 5 iterations return '* a comment' — INPUT never fails
```

**C-level getline is correct** — confirmed with a direct C test that `getline()` returns -1 repeatedly past EOF. So `input_read()` in `snobol4.c` does return `FAILDESCR` correctly.

### The actual bug location

The bug is in how the **Snocone --ir-run interpreter uses the deferred NV variable `INPUT`** inside a loop body. Specifically in `stmt_exec.c` / `eval_code.c`.

When `NV_GET_fn("INPUT")` is called inside an inner while loop body, **it is NOT calling `input_read()` each time** — it appears to be returning a cached/stale value. This is the DYN-4 deferred NV fetch mechanism.

### Key source files to investigate

```
/home/claude/one4all/src/runtime/x86/stmt_exec.c       ← NV_GET_fn, deferred vars
/home/claude/one4all/src/runtime/x86/eval_code.c       ← E_VAR handler (line ~115)
/home/claude/one4all/src/runtime/x86/snobol4.c         ← input_read() at line ~3184
```

The `E_VAR` handler in `eval_code.c` line ~115:
```c
case E_VAR:
    if (e->sval && *e->sval)
        return NV_GET_fn(e->sval);
    return NULVCL;
```

And `NV_GET_fn("INPUT")` calls `input_read()` per `snobol4.c` line ~2075:
```c
if (strcasecmp(name, "INPUT") == 0) return input_read();
```

The question is: **why does `NV_GET_fn("INPUT")` inside the loop body not call `input_read()` on each iteration?** Look for any caching, memoization, or deferred-var snapshot logic in `stmt_exec.c` (DYN-4 comments, `capture_t`, `deferred_var_t`, `nv_snapshot`, `nv_restore`).

---

## Next Action (SB-4 fix)

1. **Find the caching layer**: search `stmt_exec.c` for how NV deferred vars are fetched inside loop bodies. Look for `DYN-4`, `nv_get`, `capture`, `snapshot`, or any mechanism that would cache `INPUT`'s value across iterations.

2. **Fix**: ensure `NV_GET_fn("INPUT")` is called fresh on every `E_VAR` eval — either by marking INPUT as non-cacheable, or by flushing the cache on each loop iteration.

3. **Verify fix**:
```bash
cd /home/claude/one4all
export SNO_LIB=/home/claude/corpus/programs/snobol4/beauty
echo "* a comment" | ./scrip --ir-run test/beauty-sc/beauty/beauty.sc
# expected: "* a comment"

# Run all 6 crosscheck cases:
for case in 101_comment 102_output 103_assign 104_label 105_goto 109_multi; do
  input=/home/claude/corpus/crosscheck/beauty/${case}.input
  ref=/home/claude/corpus/crosscheck/beauty/${case}.ref
  got=$(./scrip --ir-run test/beauty-sc/beauty/beauty.sc < "$input" 2>/dev/null)
  expected=$(cat "$ref")
  [ "$got" = "$expected" ] && echo "PASS $case" || echo "FAIL $case"
done
```

4. After all 6 PASS, run broker gate:
```bash
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh  # expect PASS=36+
```

5. Commit with identity `LCherryholmes / lcherryh@yahoo.com`, push one4all, then push .github.

---

## Key paths

| File | Purpose |
|------|---------|
| `/home/claude/one4all/src/runtime/x86/snobol4.c` | `input_read()` at line ~3184 |
| `/home/claude/one4all/src/runtime/x86/stmt_exec.c` | NV_GET_fn, DYN-4 deferred vars |
| `/home/claude/one4all/src/runtime/x86/eval_code.c` | E_VAR → NV_GET_fn path |
| `/home/claude/one4all/test/beauty-sc/beauty/beauty.sc` | The Snocone program under test |
| `/home/claude/corpus/crosscheck/beauty/` | 6 crosscheck cases (input + .ref) |
| `/home/claude/corpus/programs/snobol4/beauty/` | Include files (set SNO_LIB here) |
