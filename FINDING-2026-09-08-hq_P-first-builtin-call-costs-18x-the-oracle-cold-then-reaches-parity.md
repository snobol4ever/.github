# FINDING 2026-09-08 hq_P — the FIRST builtin call in a SCRIP program costs ~18x the oracle's; every call after it is at parity

## Claim

SCRIP's first SNOBOL4 builtin call costs **~6300 ns** against `sbl -bf`'s **~350 ns** (medians of 25
runs). Every subsequent builtin call is at parity: **50–90 ns** against the oracle's **40–90 ns**.
The gap is a one-time cold cost on the shared builtin-dispatch path, not a per-call throughput
deficit, and it is invisible to every instrument we own because no benchmark measures a program's
FIRST call.

## How it surfaced

`packages/snobol4/gimpel/RESOLUTI_driver.sno` was m3 RED, third line absent. Gimpel's `RESOLUTI.sno`
defines `RESOLUTION()` as a spin on the clock's own granularity:

```
RESOLUTION      T  =  TIME()
RESOLUTION_1    RESOLUTION  =  TIME() - T
        GT(RESOLUTION,0)                        :S(RETURN)F(RESOLUTION_1)
```

`TIME()` counts NANOSECONDS on both implementations (measured, not assumed — see below), so the
loop exits on its FIRST iteration and the value returned is simply *how long one iteration took*.
That makes `RESOLUTION()` an accidental but unusually clean microbenchmark of a cold builtin call,
which is why an 18x gap that no board had ever reported showed up in a correctness suite.

## The unit determination (this is load-bearing; everything else rests on it)

The SPITBOL v3.7 manual (`:10278`) says TIME() "returns the execution time in milliseconds". **It is
nanoseconds in this build.** A 2,000,000-iteration loop:

| implementation | user CPU | TIME() delta | units per second |
|---|---|---|---|
| `sbl -bf` (x64 oracle) | 0.071 s | 68,632,000 | 9.7e8 |
| SCRIP m3 | 0.034 s | 28,742,750 | 8.5e8 |

Both land on 1e9. Do not trust the manual's unit here.

## The measurements

Cold = first builtin call in the process. 25 runs each, `SCRIP 13c3cf588`, `RT_OPT=-O0`, mode 3,
oracle `/home/resources/x64/bin/sbl -bf`. The axis is `oracle / ours`.

| | oracle (ns) | SCRIP (ns) | × vs SPITBOL |
|---|---|---|---|
| first builtin call (cold) | 351 (median) | 6292 (median) | 0.056x |
| calls 2..10 (steady) | 40–90 | 50–90 | ~1.0x |
| per-call marginal, 200k calls | 25.2 | 40.8 | 0.62x |

## What is and is not cold — the discriminating arms

Each arm warms something, then measures `RESOLUTION()`:

| arm warmed first | SCRIP result (ns) |
|---|---|
| nothing | 12533 |
| `TIME()` | 321 |
| `SIZE('abc')` + `DATATYPE(1)` | 391 |
| `DATE()` | 371 |
| a user-defined `NOOP()` call | 5090 |

**Warming ANY builtin collapses the cost; warming a user function call does not.** So the cold thing
is shared by all builtins and is not the user-function/activation-frame machinery.

## Hypotheses tested and REFUTED — record so nobody re-runs them

- **Lazy PLT binding.** `LD_BIND_NOW=1` changes nothing (3326–4138 vs baseline 3056–4488).
- **The 512MB heap slab / `madvise(MADV_HUGEPAGE)`** in `rt_gcheap_init` (`src/runtime/rt/gc_heap.c:122`),
  which `strace` does show firing late, right at execution. `SCRIP_NOHUGE=1` changes nothing;
  `SCRIP_HEAP_MB=8` changes nothing. It is visible in the trace and it is not the cost.
- **`clock_gettime` itself.** `CLOCK_MONOTONIC` is vDSO; the steady-state 50–90 ns bounds it.

The cause is therefore still OPEN and lives somewhere on the shared builtin path
(`register_fn` table lookup / `by_name_dispatch.c` / first `_usercall_hook` entry). It is NOT
diagnosed here — this FINDING establishes the phenomenon, the magnitude, and five dead ends.

## Why no instrument sees it

Every benchmark we run measures a loop, so a one-time 6 µs is divided away to nothing. The cost is
paid once per PROCESS. It matters exactly where SCRIP is invoked many times on small inputs — which
is precisely how every corpus board runs (one process per entry, ~1890 entries for the SNOBOL4
master alone). It is plausibly a real component of board wall-clock that nobody has attributed.

⛔ It also means a program that calls one builtin and exits is graded on a path that never reaches
the steady state our benchmark numbers describe.

## Routing

Shared builtin-dispatch path — the shared engine is `hq_U`'s lane, so the CURE is not taken here.
Per the corrected SHARED-NODE law (ceo CEO-405, `.github ce687e83`): the carriers of this state are
the builtin registration table and the by-name dispatch, which every frontend reaches, so a cure
owes boards on more than the lowerer census would name.

⭐ The RED that exposed this was NOT caused by the gap and is cured separately: `RESOLUTI_driver`'s
bound read `LE(R, 1000)` under a header saying "milliseconds", i.e. it asserted a ONE-MICROSECOND
completion. That bound is not reproducible on its own oracle — `sbl -bf` exceeded it in 3 of 100
runs (min 180, p50 380, p95 661, max 1163). Fixed to `LE(R, 1000000000)` at corpus `2df26fdb6`;
40/40 deterministic on both implementations afterwards. **Fixing the flake did not close this gap
and must not be read as having closed it.**
