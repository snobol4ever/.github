# FINDING s200 — `+` IS ALREADY INLINED AND ALREADY 8.1× SPITBOL; `LT`, THE NULL-CONCAT AND THE VARIABLE STORE ARE UNCONDITIONAL C CALLS
**HQ (Claude Fable 5), 2026-08-21 s200, Lon-directed ("every benchmark does LT() and + — put just those two on the examining table; we want to INLINE and avoid the RT call, PURE ASM"). `RT_OPT=-O0`, oracle `sbl -bf -s16m`, harness-driven micros, all checks correct on both engines.**

## THE EXPERIMENT — payload scaling separates loop control from arithmetic
Three micros identical but for the number of `A = A + 1` statements inside one harness loop (k = 1, 5, 10; checks 1000/5000/10000, correct on both engines). `T(k) = loop_control + k·add`, and the fit is **linear to 0.2%** on the oracle (17.27 vs 17.23 per add across the two intervals), so the decomposition is sound.
| | SPITBOL | SCRIP | verdict |
|---|---:|---:|---|
| **one `A = A + 1`** | 17.25 | **2.12** | ⭐ **SCRIP 8.1× FASTER** |
| **loop control** (`ZI = LT(ZI,ZKN) ZI + 1` + branch) | 25.87 | 6.02 | SCRIP 4.3× faster |
| loop-control share of the minimal loop | 60% | **74%** | |
| whole-loop ratio at k=1 / k=5 / k=10 | | | **5.30× / 7.02× / 7.28×** |
*(Units are the harness's own; only ratios and shares are quoted, and both engines are measured through the identical accounting.)*

## ⛔ THE INSTRUMENT WAS CHALLENGED AND RE-VALIDATED WITHOUT THE HARNESS (Lon, in-chat: *"those tests are wrapped in a FUNCTION call — are they invalid?"*)
**The challenge was legitimate and it targeted the right term.** The harness measures `ZBODY(ZK)` calls (`harness.inc:26–27`, `ZN = ZN + ZK`, so `iters` counts INNER iterations), and any per-call overhead lands in the **constant** of the fit — i.e. in "loop control", exactly the number the conclusion rests on. The **slope** (per-add) is immune to any constant by construction, but the constant was not defensible on the harness alone.
**So it was re-measured with NO harness, NO `DEFINE`, NO function call of any kind** — a bare `ZBL` loop, timed externally, **differencing 5M against 10M iterations so process startup AND SCRIP's own compile time cancel exactly** (min-of-3):
| | SPITBOL | SCRIP | |
|---|---:|---:|---|
| k=1 loop | 47.80 ns/iter | 7.80 ns/iter | 6.13× |
| k=5 loop | 119.60 ns/iter | 17.00 ns/iter | 7.04× |
| **fit: one add** | **17.95 ns** | **2.30 ns** | ⭐ **SCRIP 7.8× FASTER** |
| **fit: loop control** | **29.85 ns** | **5.50 ns** | SCRIP 5.4× faster |
| loop-control share | 62% | **71%** | |
**The two instruments agree**: per-add 17.25 vs 17.95 (4%) and 2.12 vs 2.30 (8%); loop control 25.87 vs 29.85 (15%) and 6.02 vs 5.50 (9%). ⇒ **`ZBODY` is amortized over `ZK` and did not invalidate the suite**, and every conclusion below stands — now in real nanoseconds rather than harness units. **Ceiling if loop control were free: k=1 goes 6.13× → 20.8×.**

### ⭐ THE PROCEDURE BOUNDARY, PRICED DIRECTLY — IT IS FREE IN SCRIP
Lon pressed further (*"there can not be a harness — these double loops must be inlined for each source"*). Measured, same differential method, three shapes of the identical loop:
| shape | SPITBOL ns/iter | SCRIP ns/iter | ratio |
|---|---:|---:|---:|
| top-level, **literal** bound | 47.80 | 7.80 | 6.13× |
| top-level, **variable** bound | 40.20 | 7.60 | 5.29× |
| **`DEFINE`-wrapped, parameter bound (= the harness shape)** | 38.00 | 7.60 | 5.00× |
⇒ **The `DEFINE` boundary costs SCRIP NOTHING — 7.60 vs 7.60 ns, identical** — and SPITBOL ~5%. **The harness is not invalidating anything; if anything it is CONSERVATIVE**, reporting 5.00× where a clean top-level loop reports 5.29×. ⛔ So inlining the timing loop into every source would re-spell the harness ~30 times to chase a ≤5% instrument effect that already runs in the ORACLE's favour. ⭐⭐ **THE REAL CAUTION THIS EXPERIMENT FOUND IS ELSEWHERE:** changing the loop bound from a LITERAL to a VARIABLE moved **SPITBOL by 16%** (47.80 → 40.20) while moving SCRIP by 2.6% — **the source idiom of a benchmark matters far more than the harness that wraps it**, and the two engines are not equally sensitive to it. A benchmark rewritten "equivalently" can move the oracle much more than it moves SCRIP. ⛔ My first version of this experiment confounded the wrapper with the literal→variable change and would have blamed the boundary for a 20% effect that was 16% operand idiom; the control above separates them.

## ⭐⭐ WHAT THE EMITTED ASM SAYS — HALF THE HYPOTHESIS IS ALREADY DONE
**`+` IS ALREADY INLINE.** `--compile` of the loop shows an inline arithmetic fast path — `cvtsi2sd` / `addsd` / `movq rax, xmm0`, result tag stored, then `jmp` straight to the assign — with **`call rt_add@PLT` on a COLD branch** (`.Lx46_0:`) reached only when the fast path declines. That is why an add measures 2.12 units and beats SPITBOL 8.1×. **There is no win available on `+`; it is finished work.**

**THE OTHER THREE ARE UNCONDITIONAL CALLS WITH NO FAST PATH AT ALL** — each block opens and goes straight to `call`:
- `n19_cmp_test_α:` → `sub rsp,16` · `lea rdi` · `lea rsi` · bank · **`call rt_cmp_d@PLT`** ⇒ **`LT` and every relational predicate is a C call.** An integer compare should be `cmp`+`jcc` inline.
- `n23_binop_α:` → marshal 4 registers · bank · **`call str_concat_d@PLT`** ⇒ **the null-concatenation is a C call.** ⛔ In the idiom `ZI = LT(...) ZI + 1` the predicate's result is **the null string on success**, so this call concatenates NULL with a number — *semantically a no-op* — on every single iteration of every benchmark in the suite. This is the cheapest win on the board: it can be elided at LOWER time, not merely inlined.
- `n28_assign_α:` → marshal · bank · **`call NV_SET_fn@PLT`** ⇒ **every natural-variable store is a C call.**

⇒ **Lon's premise is right about the loop tax and wrong about its cause.** The tax is real (74% of a minimal loop) and every benchmark pays it, but it is not `+`; it is **`LT` + the null-concat + the store**.

## ⭐ THE CEILING — why this raises every row
Loop control is 74% of SCRIP's minimal-loop time. If it were free, the k=1 ratio goes **5.30× → ~20×**, and the k=5/k=10 rows (already 7.0–7.3×) rise toward the pure-arithmetic 8.1×. ⛔ **But it will NOT move the demo/real-program rows**: FINDING s199 measured those at **91.6% table construction**, where loop control is noise. **This is a microbenchmark-headline lever, not a real-program lever** — both are worth having, and they must not be confused for one another.

## THE RTCC VENEER (Lon: *"those sequences of register save and restore are killing us"*) — REAL, BUT SECOND-ORDER, AND MEASURED
The veneer at each call site in this witness is **one store before and one-to-two loads after** (`mov [rip+rtccb+40], r8` … `mov r8, [rip+rtccb+40]` / `r9, +48`). The whole program touches `rtccb` **21 times across exactly 2 slots** (r8, r9) — the residue after s195 freed r10/r11 (7,352 → 520 fleet-wide). Two facts decide the priority:
1. **On `rt_add` the veneer is on the COLD path** (it sits after the inline fast path has already jumped away) — removing it there gains **nothing**.
2. **On `rt_cmp_d` / `str_concat_d` / `NV_SET_fn` it is on the HOT path**, because those calls are unconditional. There the veneer is ~2–3 instructions against a PLT call plus 4-register marshalling — **roughly 10% of the call site.**
⇒ **Stripping the veneer is worth ~10%; removing the CALL is worth ~10×.** Do the veneer where the callee is provably pure-asm/non-clobbering, but do not let it outrank inlining. ⛔ And do not strip it by a per-callee name list — that is a per-op filter under another name (RULES); it must key on a declared property of the callee.

## RANKED BY MEASUREMENT (what actually raises which number)
1. **`str_concat_d` on a null operand — elide at LOWER** (every benchmark, every iteration, provably a no-op). Cheapest, largest, lowest-risk.
2. **`rt_cmp_d` → inline integer compare** for LT/GT/LE/GE/EQ/NE as one family (⛔ no per-op filter).
3. **`NV_SET_fn` → inline store** for the natural-variable case (the GVA/pinned-slot machinery already exists).
4. **RTCC veneer** on the remaining unconditional calls (~10% each).
5. ⛔ **`+` — NOTHING TO DO.** Already inline, already 8.1× SPITBOL. Named here so no session is spent on it.
6. ⛔ **Real-program rows are unaffected by all of the above** — they need the s199 table path (7×, 91.6%).
