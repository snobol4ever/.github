# FINDING 2026-07-25 — ICN BID-2: jump table landed, and the measurement that reframes the perf ladder

**Session s160 (Claude Opus 4.5). SCRIP `ac92b5b6`. Suite PASS=249 FAIL=12 XFAIL=32 (zero regression).**
**Honest geomean vs iconx: 0.615× → 0.642× at `RT_OPT=-O0`.**

## What landed

**BID-2 jump table.** BID-1 (s159) replaced 197 `strcmp(fn,"lit")` tests with integer `_bid ==` tests but
left them a **linear chain**. The hot builtins sit LATE in it, so every dispatch walked ~100+ compares
before matching. Generated a `switch (_bid)` jump table mechanically: 125 cases → 123 labels, inserted
AFTER the preamble (field scan / dtax / `dat_find_type` / length-switch) so no live code is skipped;
first-arm-wins mapping preserves chain order exactly. Forward jumps pass only `MATH1()` name-conditional
macros and `extern` declarations — no side effects, and the compiler validates scope.

**`rt_num_arith` integer-pair fast path** ahead of the `setjmp` frame. Verified equivalent: `to_int` on
DT_I returns `.i` (see `rt_asm_helpers.S` — DT_I is type 6, two instructions), `IS_REAL_fn` is
`v.v == DT_R`, so `operand_is_real_str` returns 0 for ints. The impl was computing **both** the double and
the integer forms — two `to_real`, two `to_int`, two `operand_is_real_str` scans — for every integer add.
Integer add/sub/mul cannot raise, so the errjmp frame is unnecessary.

**BID histogram diagnostic** (`SCRIP_BID_PROF=1`, env-gated). This is what found the hot set; keep it.

## ⛔ THE MEASUREMENT THAT REFRAMES THE LADDER — DISPATCH IS NOT THE ELEPHANT

The s159 cursor said "~34% of the program is by-name dispatch even after `-O2`" and named finishing the
integer-ID work as the structural fix. **Measured, that framing is wrong, and the jump table proves it.**

`try_call_builtin_by_name` is 66.8% of tgrlink INCLUSIVE, 533,135 calls at ~2,911 Ir per dispatch. It is
easy to read that as 2,911 instructions of *dispatch overhead*. It is not. Removing the entire chain walk
(the jump table) bought only **55M Ir of 2,323M — 2.4%**. The chain was ~100 integer compares × 533K
calls ≈ 55M, exactly as removed. **The other 477M of that function's self-cost is the builtin BODIES,
which are written inline inside the function** — `right`, `get`, `put` etc. are real work, not dispatch.

**Corollary — do not spend another rung on making dispatch cheaper.** The by-name *scan* pathology was
already largely paid down by BID-1; BID-2 closes the remainder. What is left is the cost of the operations
themselves and the data representation they carry.

## WHERE THE REMAINING COST ACTUALLY IS (tgrlink, `-O0`, post-BID-2, 2,246M Ir)

| cost | % | what it is |
|---|---|---|
| `try_call_builtin_by_name` self 477M | 21.3% | **builtin bodies inlined in the function**, not dispatch |
| `VARVAL_fn` 253M | 11.3% | **6,630,400 calls = 12.4 per dispatch** |
| `__strcmp_avx2` 227M | 10.1% | NOT mainly the field scan (guard removed only 4.5%) — re-derive the caller |
| `__strcasecmp_avx2` 109M | 4.8% | `FIELD_GET_fn` O(nfields) scan, 528K calls |
| `bid_of` 64M | 2.8% | one hash per dispatch |

**`VARVAL_fn` at 12.4 calls per dispatch is the standing #1 lead** and matches s159's count exactly
(6,630,400). It converts a DESCR to a C string — DT_SNUL and DT_I arms **allocate** (`rt_ws_strdup_c`,
`snprintf`+strdup). The question to answer FIRST is not "make VARVAL faster" but **"why do the builtin
bodies call it 12 times per call, and can they work on the DESCR directly?"** An asm leaf (s159's
proposal) makes each call ~36→~10 instructions; eliminating calls removes the allocation too.

## NEGATIVE RESULTS — do not retry blind

- **First-char guard on the DT_DATA field scan in `try_call_builtin_by_name`:** removed only **4.5%** of
  that function's strcmps (5,188,974 → 4,956,003). The field names apparently share first characters with
  the callee name. Kept (free, harmless) but it is NOT a lever. **The 227M strcmp cost is still
  unattributed — the next session should re-derive its caller before touching it.**
- **⛔ Case-folded first-char guard in `FIELD_GET_fn`: MEASURED WORSE, REVERTED.** `strcasecmp` fell
  102M→80M but `FIELD_GET_fn` itself rose **62M→101M**, for a net **+1.8% total Ir**. Cause: `tolower()`
  is an out-of-line, locale-aware libc call at `-O0` — more expensive than the `strcasecmp` first-byte
  check it was meant to skip. **Any case-insensitive fast path must use an inline ASCII fold
  (`c|0x20` on a verified-alpha range), never `tolower()`.** `core.c` is untouched at HEAD.

## ⚠ METHOD NOTE — the wall-clock/Ir split, again

Wall-clock on this corpus is startup-dominated and noisy: `concord` moved 97→114ms across a change that
lowered instruction count, and `version` is 4ms of pure startup. **Ir (callgrind) is the honest metric for
a runtime change; wall-clock is only trustworthy on `tgrlink`/`geddump`** (the two with real workloads and
IDENTICAL oracle output). Report both, and label `RT_OPT` (s126).

## ▶ HONEST STATE OF THE 2–3× TARGET

Lon's target is 2–3× FASTER than iconx. Measured honest geomean is **0.642×**, i.e. SCRIP is ~1.56×
SLOWER. **The remaining gap is ~4×, and no single rung on the current ladder is worth 4×.** Arizona
`iconx` is a bytecode interpreter (`switch((int)lastop)` over `Op_*` in `interp.r`) — beating it 2–3×
requires the emitted code to stop routing scalar operations through the runtime at all, not a faster
runtime dispatch. Two structural tracks, in this order:

1. **Emit inline fast paths instead of calls (the real lever).** `a + b` on two integers currently costs:
   marshal args to a frame array → `rt_call_arr` (**`setjmp`**) → `rt_gc_point_arr` → `$`-prefix check →
   **~30-strcmp operator chain** → `rt_num_arith` (**second `setjmp`**) → impl. That is hundreds of
   instructions for an `add`. The template should emit a DT_I type test + native `add` and call out only
   on the slow shape. `dop_direct_fp` in `bb_call.cpp` is the in-tree precedent ("direct det leaf: no
   by-name dispatch") — the operator analog is sound **by construction** because operators (`+ - * [] ||`,
   relops) are not identifiers and can never be shadowed by a user procedure or record type. Name it by
   behavior, not language, per the no-language-identity FACT RULE.
2. **Then** `VARVAL_fn` call-count reduction (above), which is where the runtime cost concentrates once
   scalar ops stop calling out.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
