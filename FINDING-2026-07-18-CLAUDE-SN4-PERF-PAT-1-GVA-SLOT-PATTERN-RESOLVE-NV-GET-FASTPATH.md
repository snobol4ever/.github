# FINDING — SN4 PERF-PAT-1: GVA-Slot Pattern Resolution + NV_GET Fast Path
**Session:** s93 (2026-07-18, Claude Sonnet 4.6)
**Commit:** SCRIP `f0914867`
**Status:** LANDED — gates at watermark, not regressed

---

## THE SYMPTOM

`pattern_bt` (500k iterations, alternation+SPAN backtracking): SCRIP 1040ms vs SPITBOL 244ms (4.4×).
`string_pattern` (BREAK, repeated subject rescan): SCRIP 5278ms vs SPITBOL 811ms (6.5×).
Output byte-identical in both cases — pure speed gap.

Instrumented `rt_defer_get_pat_fn` with a call counter: **5,500,011 calls** in one `pattern_bt` run
(11 anchor positions × 500,000 iterations). At ~140ns/call = ~770ms wasted. This is the gap.

---

## ROOT CAUSE (Lon diagnosis, confirmed by instrumentation and code archaeology)

`S PAT` was **two bugs stacked**:

### Bug 1 — wrong lowering for a bare TT_VAR pattern operand

`lower_snobol4.c` TT_VAR arm (introduced `1d205f46` "SN4-PAT-FOLD") routes a bare variable in
pattern position to `IR_MATCH_DEFER`. This was a stub — DEFER already existed for `*P` and already
knew how to resolve+invoke a variable's pattern value, so it was the quickest way off the
"SN4-PAT wall". The correct shape for `S PAT` is a value-read (once, at statement entry, from the
GVA slot) + invoke. `S *PAT` (deferred) is the right home for DEFER. The two became conflated.

`FZ-5` (`ea0fbb2a`) noticed the symptom ("per-match name→fn fetch") and tried to inline the
resolved fn at emit time for once-assigned-invariant variables. It removed the name-resolve cost
but left the variable **still going through the DEFER box**, which carries a per-visit ZLS
allocation on the callout path. Its own measurement: "no benchmark win — noise. The eliminated
per-match name→fn fetch is dwarfed by the per-match rt_zls_alloc(65536)+rt_zls_release pair."
(This session's `pattern_bt` does NOT hit the callout path — it takes the fast DT_P jmp-rax arm —
so the ZLS cost doesn't apply here; the pure resolver cost IS the bottleneck here.)

### Bug 2 — DEFER resolves by name through a slow path instead of reading the GVA slot

`rt_defer_get_pat_fn(name)` calls `NV_GET_fn(name)`. `NV_GET_fn` runs, per call:
- `_io_chan_find_by_var(name)` — scans all 32 IO-channel slots
- then ~20 sequential `strcmp` calls against keyword names (STLIMIT, ANCHOR, STCOUNT, …)
- then the hash-bucket walk that actually finds the variable

~140ns × 5.5M = ~770ms for `pattern_bt`. The *write* side already uses the GVA slot directly
(`mov [1879052288], rax` for `PAT = (...)`). The read side went through the name→dictionary path.

`op_gva_k` was populated for `IR_VAR` / `IR_ASSIGN` but NOT for `IR_MATCH_DEFER` (emit.cpp line 698
`nm_op` set). So the DEFER node always saw `op_gva_k = -1` even though the GVA slot address was
baked into the assignment code for the same variable.

---

## FIXES APPLIED (SCRIP `f0914867`)

### Fix 1 — `NV_GET_fn` fast path (runtime/core/core.c)

Added `_var_bucket_find(name)` static helper (hash-bucket walk, returns `NV_t*`). In `NV_GET_fn`,
when `!g_call_fastpath_off && name[0] != '&' && name[0] != 'I'`, call it first. A hit returns
immediately (`e->is_gva ? *e->cell : e->val`) — skipping the IO-channel scan and the ~20 failed
keyword strcmp calls. A miss falls through to the full existing path unchanged.

**Safety:** keywords are never in `_var_buckets` (NV_SET intercepts them before hash-store); IO-assoc
vars set `g_call_fastpath_off` on association (lines 2772/2800 of core.c). The `name[0] != 'I'`
guard skips `INPUT` without an extra strcmp. General: every plain variable read benefits.

### Fix 2 — GVA-slot pattern resolution (emitter/emit.cpp + templates/bb_match_defer.cpp)

**emit.cpp:** Added `IR_MATCH_DEFER` with non-`*` name to the `op_gva_k` population (guarded:
`nd->op == IR_MATCH_DEFER && sval && sval[0] != '*'`). Now a bare `S PAT` carries `op_gva_k = 0`
(PAT's GVA slot index) into the template.

**bb_match_defer.cpp:** Added `extern int g_gva_active` and `extern "C" void *dtp_fn_of(void *)`.
Added a GVA-slot resolution arm at the top of the return concat, guarded by
`IF(g_gva_active && _.op_gva_k >= 0, ...)`:
```
mov rax, ABSQ(RT_GVA_VA + op_gva_k * 16)     # load descriptor low qword (tag in eax)
mov rdx, ABSQ(RT_GVA_VA + op_gva_k * 16 + 8) # load pointer half
cmp eax, DT_P (3)                              # is it a compiled pattern?
jne L(9)                                        # no -> xor eax,eax (NULL -> existing L0 callout)
mov rdi, rdx                                    # pattern head ptr as arg
call dtp_fn_of                                  # -> compiled fn ptr (caches h->fn lazily)
jmp L(10)
def L(9): xor eax, eax
def L(10):
```
The by-name `rt_defer_get_pat_fn` path is kept as `IF(!(g_gva_active && _.op_gva_k >= 0), ...)`
fallback, covering `*expr`, indirect (`$`), locals, and keywords. Internal label ids 9/10 (per-box
unique, both-medium correct via XK_ILBL mechanism).

**Emitted assembly (pattern_bt, before/after):**
```
BEFORE:  lea rdi,[rip + .S6]  ;  xor esi,esi  ;  call rt_defer_get_pat_fn@PLT
AFTER:   mov rax,[1879052288] ;  mov rdx,[1879052296]  ;  cmp eax,3  ;  jne .Lx48_9
         mov rdi,rdx  ;  call dtp_fn_of@PLT  ;  jmp .Lx48_10
```
`rt_defer_get_pat_fn` is **completely absent** from the compiled `pattern_bt` binary.

---

## MEASURED RESULTS (best-of-3, byte-identical to oracle)

| Benchmark | Baseline | Fixed | SPITBOL | Ratio fixed/SPITBOL |
|---|---:|---:|---:|---:|
| `pattern_bt` m4 | 1040ms | **335ms** | 240ms | 1.40× |
| `pattern_bt` m3 | 1114ms | **346ms** | 240ms | 1.44× |
| `string_pattern` m4 | 5278ms | 4405ms | 799ms | 5.51× |
| `string_pattern` m3 | 5115ms | 4469ms | 799ms | 5.59× |

`string_pattern`'s remaining gap is BREAK inner-loop subject-rescan (separate rung, not this fix).

**Gates (UNCHANGED from s92 watermark):**
sno smoke 7/7×2 · crosscheck m3 305/2 · m4 304/2/1 · DIVERGE=1 (1017_arg_local) EXACT.

---

## WHAT THIS DOES NOT FIX (next rung)

**Per-anchor re-resolution still fires.** The DEFER box resolves `dtp_fn_of` on every entry —
once per anchor position per iteration. For `pattern_bt` (11 anchor positions × 500k iters) that's
still 5.5M `dtp_fn_of` calls. After `h->fn` is cached on the pattern object (first call), these
are a fast pointer load + return (~3ns each = ~16ms) — cheap enough that the remaining 95ms gap
to SPITBOL is dominated by the pattern-match work itself, not the resolver. But the architecturally
correct fix is to hoist the resolution out of the anchor loop to statement-entry scope (resolve
once, thread the fn pointer into MATCH_HEAD). That's a structural rung touching MATCH_HEAD / DEFER
interaction — spec it before landing.

**The bare TT_VAR ≠ TT_DEFER structural issue remains.** `S PAT` still lowers to `IR_MATCH_DEFER`
rather than a value-read IR node. Fix 2 papers over this at emit time with a by-slot fast path,
but the node conflation is still there. Splitting TT_VAR off onto its own IR node (read-once,
no per-anchor DEFER semantics) is the clean long-term fix; it's held because the DEFER box's ZS-2
invoke protocol is load-bearing and a wrong split would break recursion/backtracking broadly.
