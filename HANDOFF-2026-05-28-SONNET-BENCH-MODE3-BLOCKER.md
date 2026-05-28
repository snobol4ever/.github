# HANDOFF-2026-05-28-SONNET-BENCH-MODE3-BLOCKER.md

**Session:** Sonnet 4.6, 2026-05-28
**one4all HEAD:** `4ce8c385` (unchanged — no new commits this session)
**.github HEAD:** `20e62662`

---

## What happened this session

### 1. MEDIUM_BINARY audit — all clear
All MEDIUM_BINARY arms that return empty do so correctly. Zero real gaps found. Audit GATE OK.

### 2. Mode-3 native attempt — REVERTED
Attempted to make `sm_run_native` the unconditional mode-3 runner (remove `SCRIP_M3_NATIVE` env gate in `scrip.c`). This caused crashes (SIGILL, SIGSEGV) on SNOBOL4 programs using SPAN, ARB, and pattern opcodes.

**Root cause identified:** `sm_pat_nullary.cpp` BINARY arm dispatches `SM_PAT_SPAN`, `SM_PAT_ANY`, `SM_PAT_NOTANY`, `SM_PAT_BREAK`, `SM_PAT_BREAKX` via `sm_pat_nullary_rt_fn()` which returns the rt function pointer, but the BINARY arm only emits `movabs rax, rt_fn; call rax` — **no `rdi` argument**. These functions all take `const char *chars`. Similarly `SM_PAT_LEN`, `SM_PAT_POS`, `SM_PAT_TAB` etc. take integer args.

The fix requires splitting the BINARY arm in `sm_pat_nullary.cpp` into three groups:
- **No-arg:** ARB, REM, FENCE0/1, FAIL, SUCCEED, ABORT, BAL, EPS, DEREF, CAT, ALT, ARBNO → `call rt_fn` with no setup
- **String-arg:** ANY, NOTANY, SPAN, BREAK, BREAKX → `movabs rdi, pSM->a[0].s; call rt_fn`
- **Int-arg:** LEN, POS, RPOS, TAB, RTAB → `movabs rdi, pSM->a[0].i; call rt_fn`

`scrip.c` was reverted via `git checkout` — no commit was made.

### 3. Benchmark run — partial results only
Mode 4 compile+link is slow (~30s per bench), causing timeout. Two results captured:

| bench | m2(ms) | m3(ms) | m4(ms) | equiv |
|-------|--------|--------|--------|-------|
| arith_loop | 2124 | 2179 | 1692 | OK(3) |
| eval_dynamic | 7711 | 7617 | 6948 | OK(3) |

Mode 3 (`--run`) is currently `sm_interp_run` (not `sm_run_native`) — so m2≈m3 is expected. Mode 4 is ~20% faster due to compiled native binary.

---

## Next session priorities

### Priority 1 — Fix `sm_pat_nullary.cpp` BINARY arm (blocks mode-3 native)
File: `src/emitter/SM_templates/sm_pat_nullary.cpp`
The BINARY arm (around line 99) needs:
```cpp
IF(MEDIUM_BINARY, [&]() -> std::string {
    const char *s = pSM->a[0].s ? pSM->a[0].s : "";
    int64_t i = pSM->a[0].i;
    void (*fn)(void) = sm_pat_nullary_rt_fn((int)pSM->op);
    if (!fn) return std::string();
    /* string-arg group */
    if (op == SM_PAT_ANY || op == SM_PAT_NOTANY || op == SM_PAT_SPAN
     || op == SM_PAT_BREAK || op == SM_PAT_BREAKX)
        return bytes(2,"\x48\xBF") + u64le((uint64_t)(uintptr_t)s)
             + bytes(2,"\x48\xB8") + u64le((uint64_t)(uintptr_t)fn) + bytes(2,"\xFF\xD0");
    /* int-arg group */
    if (op == SM_PAT_LEN || op == SM_PAT_POS || op == SM_PAT_RPOS
     || op == SM_PAT_TAB || op == SM_PAT_RTAB)
        return bytes(2,"\x48\xBF") + u64le((uint64_t)(int64_t)i)
             + bytes(2,"\x48\xB8") + u64le((uint64_t)(uintptr_t)fn) + bytes(2,"\xFF\xD0");
    /* no-arg group */
    return bytes(2,"\x48\xB8") + u64le((uint64_t)(uintptr_t)fn) + bytes(2,"\xFF\xD0");
}())
```
After this fix, remove the `SCRIP_M3_NATIVE` env gate in `scrip.c:449` and make `sm_run_native` unconditional for `mode_run`.

### Priority 2 — Run full benchmark suite
After mode-3 native works, run `scripts/test_bench_snobol4_modes.sh`. Mode 4 compile is slow — consider adding `-j` or pre-compiling all benches before timing. Expected result: m4 fastest, m3 close-to-m2 today (sm_interp_run), m3 much faster after sm_run_native.

### Priority 3 — GOAL-SNOBOL4-BB next step
Enable combinator flat-wire in mode-3 (extend `patnd_needs_xlate` to handle XCAT/XALT/XFNCE).

---

## Gates at handoff

```
one4all HEAD       = 4ce8c385 (no new commits — scrip.c reverted)
audit_m3_native    = GATE OK (zero BOMs)
GATE-1 smoke       = 13/13
GATE-2 broker      = 35/53
GATE-3 mode-4      = 175/280
GATE-4 mode-2      = 238/280
NATIVE corpus      = 165/280
Rung suite         = M2=19/M4=15
FACT RULE          = 0
```
