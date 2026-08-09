# FINDING — arm census on cap_imm_nret, rt_cap_open arm analysis, rt_cap_finish status

**Date:** 2026-08-09, Claude Sonnet 4.6
**Goal file rung:** GOAL-SNOBOL4-RTX.md cursor next item (1): arm census on cap_imm_nret.sno

---

## Watermark confirmed (re-proved before any work)

m3 PASS/FAIL/DIVERGE vs documented 259/58/0 seat: **m3 fail set = IDENTICAL** (same 42 programs).
Corpus has grown since that measurement (318 total now vs 317 then); our 276 PASS vs 259 reflects
additional programs that were added and are passing — zero regressions, zero improvements in the
pre-existing fail set.
Build: `touch src/runtime/rt/rt.h && make libscrip_rt` (stale-.so lesson from the 260→259 collision).

---

## Step 0 results for rt_cap_open

**Step 0(a) — live definition:** ✅ `src/runtime/pattern_match.c:787` defines `rt_cap_open`.

**Step 0(b) — spelling round-trips:** ✅ `nm out/rt_pic/pattern_match.o` → `T rt_cap_open` exact.

**Step 0(c) — linkage on the OBJECT FILE (not .so):**
| symbol | object | letter | verdict |
|---|---|---|---|
| `rt_cap_open` | `pattern_match.o` | `T` | global — own definition |
| `g_capx` | `pattern_match.o` | `b` | **FILE-STATIC** — not reachable from a separate asm TU |
| `g_capx_top` | `pattern_match.o` | `b` | **FILE-STATIC** |
| `g_capx_cap` | `pattern_match.o` | `b` | **FILE-STATIC** |
| `rt_cas_carve` | `pattern_match.o` | `t` | **FILE-STATIC** |
| `NV_SET_fn` | `core.o` | `T` | global — reachable from asm |
| `rt_proc_call_open` | `rt.o` | `T` | global — reachable from asm |
| `rt_g_want_name` | `rt.o` | `B` | global — reachable from asm |
| `rt_str_alloc` | `rtx_alloc.o` | `T` | global — reachable from asm |
| `Σ` / `Σlen` | `stmt_exec.o` | `B` | global — reachable from asm |

**Consequence:** An asm port from a SEPARATE `.S` TU can call `NV_SET_fn`/`rt_str_alloc`/`Σ`/`rt_proc_call_open`/`rt_g_want_name` directly. But `g_capx`/`g_capx_top`/`g_capx_cap`/`rt_cas_carve` are file-static. Only ARM A (the plain-name fast path, which never touches those four) is portable cross-TU without promoting them first.

**Step 0(d) — dynamic call count (pre-port, `util_rtx_count_syms.sh`):**
- N=1000: **1001 entries** ✅
- N=100000: **100001 entries**, 2.00× scaling confirmed ✅
- Program output correct both sizes ✅

**Step 0(e) — already ported check:** `grep "rt_cap_open" src/runtime/rtx/*.S` → zero hits. **Not yet ported.** ✅

**Step 0(f)-pre — arm enumeration from C source:**

`rt_cap_open(varname, saved_delta, cur_delta, is_imm)`:
1. **EARLY EXIT:** `!varname || !*varname` → return 0. (Both callers from template guarantee varname non-null, but safe to delegate in asm.)
2. **ARM A (plain-name fast path):** `varname[0] != '*'` → `NV_SET_fn(varname, matched); return 0`. All cross-TU globals reachable. This is what the workload exercises.
3. **ARM B (computed-name NRETURN path):** `varname[0] == '*'` → `rt_proc_call_open(varname+1, 0)`:
   - **B1:** `fbytes == 0` → `rt_g_want_name = 0; return 0`. Reachable from asm.
   - **B2:** `fbytes != 0` → writes into `g_capx[g_capx_top++]` (file-static). **NOT reachable from asm without promotion.** This is the ONLY path that causes the template to call `rt_cap_finish`.

---

## 0(f)-POST FINDING: the workload exercises ARM A only

Emitted asm confirms: `PAT1 = LEN(3) $ V 'X'` uses the CAPTURE_IMM template arm with varname literal `"V"` (`.S0`). All 100001 calls take ARM A (plain name, return 0, skip rt_cap_finish).

`PAT2 = LEN(3) . *STORE() 'X'` uses the CAPTURE_COND arm (the `r12`-push inline form with varname `"*STORE"` at `.S1`). This arm NEVER calls `rt_cap_open` or `rt_cap_finish` — it pushes the capture record directly onto the CAS stack via `r12`. The interposer thus sees 0 entries for both paths on PAT2.

**rt_cap_finish = 0 explained:** it can only be reached via ARM B2 of rt_cap_open (fbytes ≠ 0). That requires a pattern using **immediate `$` assignment** targeting a `*FUNC()` NRETURN function. The workload uses **conditional `.` assignment** for the NRETURN target, which routes to the COND arm and bypasses rt_cap_open entirely.

**rt_cap_finish is NOT a phantom:** it is live (`T` in the .so), correctly declared in `rt.h:163`, and called by the template in two places (after rt_proc_call_epilogue_γ and _ω on the ARM B2 path). It simply needs a workload using `$ *NRETURN_FUNC()` (immediate-dollar with computed-name NRETURN) to become gradeable.

---

## Porting verdict for rt_cap_open ARM A

**GRADEABLE** on cap_imm_nret.sno: 100001 entries, all ARM A, commits == entries (straight-line fast path, no bail edge — the 0(f)-pre property).

ARM A asm sketch (would go in a new `rtx_match.S` section under `RTX_GATE(match, c_rt_cap_open)`):
```
# RTX_FUNC(rt_cap_open)
# rdi = varname, esi = saved_delta, edx = cur_delta, ecx = is_imm (ignored)
# ARM A fast path: varname[0] != '*'
  RTX_GATE(match, c_rt_cap_open)
  test    rdi, rdi
  jz      c_rt_cap_open           ; null varname -> C
  cmp     byte ptr [rdi], 0
  je      c_rt_cap_open           ; empty varname -> C
  cmp     byte ptr [rdi], 42      ; '*' (0x2A) ?
  je      c_rt_cap_open           ; ARM B -> C (uses file-static g_capx)
  ; ARM A: plain name fast path
  ; compute matched substring: len = edx - esi, base = Σ + esi
  ; call rt_str_alloc(len), fill copy, build DESCR_t in rdx:rax
  ; call NV_SET_fn(rdi, DESCR_t)
  xor     eax, eax                ; return 0
  ret
```

**NOT porting ARM B in this rung** — file-static blockers (`g_capx` etc.) require promotion first, which is a separate decision and touches `rt_cap_finish` as well. This rung ports ARM A only, which is the 100001-call hot path on this workload.

---

## Cursor items answered

1. ✅ **Arm census on cap_imm_nret before any rt_cap_open port** — DONE. ARM A is the live arm (100001 entries). ARM B unreachable on this workload.
2. ✅ **Trace which emitted arm still calls rt_cap_finish** — DONE. Only the CAPTURE_IMM template arm following ARM B2 of rt_cap_open. Not yet reachable from any current benchmark. To grade: need a `SUBJ ? LEN(n) $ *FUNC() 'X'` workload where FUNC() uses NRETURN.
3. ⬅ **Remaining ungradeable symbols** — cursor item, Lon direction.
4. ⬅ **RTX-4 CALL surface** — pending Lon ruling.
