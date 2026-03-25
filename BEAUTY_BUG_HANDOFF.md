# M-BUG-BOOTSTRAP-FENCE — FENCE Pattern Matching Broken in ASM Backend

**Date:** 2026-03-24  
**Sprint:** M-BEAUTIFY-BOOTSTRAP  
**Status:** BLOCKED — root cause identified, fix not yet implemented  
**Invariant:** 106/106 ASM corpus ALL PASS ✅

---

## Summary

`FENCE(pat)` always fails when used as a pattern match in the ASM backend. This is the **actual root cause** of the "Parse Error" in beauty.sno's bootstrap. All other fixes (NAMED_PAT_MAX, buffer bumps, E_NAM binary, stmt_concat DT_N) are correct and necessary but not sufficient.

---

## How to Reproduce

```bash
cd /home/claude/snobol4ever/snobol4x
cat > /tmp/fence_test.sno << 'SNOEOF'
               'hello world' FENCE('hello')  :F(FAIL)
               OUTPUT = 'OK'   :(END)
FAIL           OUTPUT = 'FAIL'
END
SNOEOF

./sno2c -asm /tmp/fence_test.sno -o /tmp/fence_test.asm
nasm -f elf64 -I src/runtime/asm/ -o /tmp/fence_test.o /tmp/fence_test.asm
WORK=/tmp/beauty_build
RT_OBJS="$WORK/stmt_rt.o $WORK/snobol4.o $WORK/mock_includes.o $WORK/snobol4_pattern.o $WORK/mock_engine.o $WORK/blk_alloc.o $WORK/blk_reloc.o"
gcc -no-pie /tmp/fence_test.o $RT_OBJS -lgc -lm -o /tmp/fence_bin
echo "" | /tmp/fence_bin
# Expected: OK
# Actual:   FAIL
```

---

## Root Cause Chain

The Parse Error in beauty.sno traces back through this chain:

1. **beauty.sno** uses `Command = FENCE(*Comment | *Control | *Stmt)`
2. `Parse = ARBNO(*Command)` — depends on Command working
3. `FENCE(...)` always fails → Command never matches → Parse fails → "Parse Error"

### Why FENCE fails

`FENCE('hello')` is compiled as:
```asm
CALL1_STR   S_FENCE, S_hello    ; calls APPLY_fn("FENCE", "hello") → DT_P
CALL_PAT_α  cpat0_t, ...        ; calls stmt_match_descr with that DT_P
```

`stmt_match_descr` → `match_pattern_at` → `try_match_at` → `engine_match_ex`.

With `PAT_DEBUG=1`, every cursor position returns `matched=0 end=0`. The `XFNCE` node type is not being handled correctly by `engine_match_ex` / `materialise`.

### Where to look

The bug is in `src/runtime/snobol4/snobol4_pattern.c` in the `materialise()` function or `engine_match_ex()`. Search for `XFNCE`:

```bash
grep -n "XFNCE\|case.*XFNCE\|T_FENCE\|FENCE" src/runtime/snobol4/snobol4_pattern.c
```

The `materialise()` function handles `XFNCE` and must produce a `T_FENCE` pattern node for `engine_match_ex`. Check whether:
- `materialise` returns epsilon for XFNCE (wrong)
- `T_FENCE` is handled in `engine_match_ex` 
- The `XFNCE` node's `left` child is being set but not materialised

### Note: FENCE is not in the corpus

The 106/106 corpus tests do NOT exercise `FENCE` — so this bug was latent and never caught. The beauty bootstrap is the first test that hits it.

---

## What Has Been Fixed (Do Not Revert)

All changes in `src/backend/x64/emit_byrd_asm.c` since B-288:

| Fix | What it does |
|-----|-------------|
| `NAMED_PAT_MAX 64→512` | Was silently dropping Parse/Command/Compiland |
| `MAX_BOXES 64→512` | Was silently missing DATA block templates |
| `call_slots 256→4096` | Was silently dropping BSS slots for user function calls |
| `MAX_VARS/LITS/STRS/LABELS` bumped | General capacity for beauty's 420 named patterns |
| `E_NAM binary case` in `emit_expr` | `epsilon . *PushCounter()` now calls `stmt_concat` correctly |
| `stmt_concat DT_N` fix | Treats name-refs as capture targets in pattern concat |

All fixes confirmed: **106/106 corpus ALL PASS**.

---

## Current State of beauty Build

```bash
cd /home/claude/snobol4ever/snobol4x
WORK=/tmp/beauty_build
./sno2c -asm -Idemo/inc -I./src/frontend/snobol4 demo/beauty.sno -o $WORK/beauty.asm
nasm -f elf64 -I src/runtime/asm/ -o $WORK/beauty.o $WORK/beauty.asm
# Runtime objects (rebuild stmt_rt.o with DT_N fix):
RT=src/runtime; SNO2C_INC=src/frontend/snobol4
gcc -O0 -g -c "$RT/asm/snobol4_stmt_rt.c" -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/stmt_rt.o"
gcc -O0 -g -c "$RT/snobol4/snobol4.c"         -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/snobol4.o"
gcc -O0 -g -c "$RT/mock/mock_includes.c"       -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/mock_includes.o"
gcc -O0 -g -c "$RT/snobol4/snobol4_pattern.c" -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/snobol4_pattern.o"
gcc -O0 -g -c "$RT/mock/mock_engine.c"         -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/mock_engine.o"
gcc -O0 -g -c "$RT/asm/blk_alloc.c"            -I"$RT/asm"                              -w -o "$WORK/blk_alloc.o"
gcc -O0 -g -c "$RT/asm/blk_reloc.c"            -I"$RT/asm"                              -w -o "$WORK/blk_reloc.o"
RT_OBJS="$WORK/stmt_rt.o $WORK/snobol4.o $WORK/mock_includes.o $WORK/snobol4_pattern.o $WORK/mock_engine.o $WORK/blk_alloc.o $WORK/blk_reloc.o"
gcc -no-pie "$WORK/beauty.o" $RT_OBJS -lgc -lm -o "$WORK/beauty_bin"
# Run:
$WORK/beauty_bin < demo/beauty.sno > $WORK/beauty_asm_out.sno
diff /tmp/beauty_oracle.sno $WORK/beauty_asm_out.sno
# Still shows Parse Error — blocked on FENCE bug
```

---

## Next Steps

1. **Fix XFNCE in `materialise()`** — inspect `snobol4_pattern.c` around line 176 and in `materialise()`. Add a test case:
   ```c
   // In materialise(), case XFNCE:
   // Must produce T_FENCE with inner child properly materialised
   ```

2. **Add FENCE to corpus** — add `test_fence.sno` / `test_fence.ref` to the crosscheck corpus so this never regresses.

3. **Re-run beauty bootstrap** — after fixing FENCE, diff against oracle.

4. **Add corpus test for `epsilon . *Var` pattern** — the E_NAM binary fix should also be regression-tested.

---

## Oracle

```bash
# Verified oracle (CSNOBOL4):
INC=demo/inc snobol4 -f -P256k -Idemo/inc demo/beauty.sno < demo/beauty.sno > /tmp/beauty_oracle.sno
# /tmp/beauty_oracle.sno = 784 lines, fixed-point ✅
```
