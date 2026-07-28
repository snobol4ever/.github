# FINDING 2026-07-28 — Z4-0: BASELINE LANDED; FIVE OF SEVEN PORTS ARE ROTTED AT HEAD; THREE DEFECTS ISOLATED TO 4-LINE REPROS

**Goal:** `GOAL-ZETA-FOUR.md` rung Z4-0. **Trees:** SCRIP `cca948c5` · corpus `4be103f5` · .github `59e12e05`. **RT_OPT=-O0** (O2-DIRECTED-ONLY rule; all timings relative-only). Nothing in `src/` was edited this session — probes + docs only.

## 1. THE HEADLINE FOR THE GOAL: THE POINT-IN-TIME EXTRACTION IS NOT OPTIONAL, IT IS FORCED
Lon's instinct ("clone at a point in time when the program was working its best") is now MEASURED, not assumed. A single capture program (`C1`, below) was run under all seven `--zeta-port` values at HEAD:

| port | value | C1 capture result |
|---|---|---|
| plain | 0 | **SEGV** |
| instrumented | 1 | **SEGV** |
| alloc | 2 | **SEGV** |
| inline | 3 | **SEGV** |
| **cstack** | **4** | **SEGV** |
| **forth** | **6** | runs (wrong by +1, see §3) |
| heap | 7 | **SEGV** |

**ONLY THE COMPILED DEFAULT SURVIVES.** The other six ports are not "dormant but intact" — they are rotted. This is the predicted Z4-2/Z4-6 rot made concrete and it lands squarely on **config 2 (FRAME-RSP = cstack/port 4)**: it CANNOT be reconstructed from HEAD's residual arms, because those arms no longer run. The `879a0d37`-era worktree is therefore the real source, exactly as the plan's COMMIT-SELECTION LAW anticipated. Same conclusion applies a fortiori to config 1 (R12), whose label was deleted outright at `c26a398a`.

Mechanism, stated honestly: these ports sat unselected while HEAD moved through the FLATDISP/scanbase/capture ladders (s188→s206). Nothing kept them green — there is no gate over non-default ports. That absence is itself a finding: **any config the four-config selector keeps MUST be covered by Z4-10's gate, or it will rot again by exactly this mechanism.**

## 2. Z4-0 BASELINE — the goal's watermark (best-of-3; first run is COLD and must be discarded)
Probe set committed at `corpus/probe/*.sno` + `.ref` (SPITBOL oracle, `/home/claude/x64/bin/sbl -b`).

| probe | SPITBOL | SCRIP m3 | SCRIP m4 | m3 | m4 | SCRIP vs sbl |
|---|---|---|---|---|---|---|
| z4_arith | 221ms | 43ms | 38ms | OK | OK | **5.1× faster** |
| z4_span | 98ms | 116ms | 107ms | OK | OK | 0.85× (slower) |
| z4_arbno | 45ms | 23ms | 21ms | OK | OK | **2.0× faster** |
| z4_fib | 43ms | 98ms | 89ms | OK | OK | **0.44× — 2.3× SLOWER** |
| z4_capture | 23ms | 27ms | 25ms | DIFF | DIFF | 0.85×, and WRONG |

**⭐ THE PERF SIGNAL THAT MATTERS TO THIS GOAL: `z4_fib` (DEFINE recursion) is 2.3× SLOWER than SPITBOL while straight-line arithmetic is 5.1× FASTER.** Call/activation cost is the outlier, and activation storage is precisely what the four configs differ on. If any config is going to win on "faster," this is the probe that will show it. m3 and m4 agree on every verdict and track within ~10% on every timing — the 1:1 mode correspondence holds across the whole probe set.

**COLD-START WARNING, measured:** `z4_arith` timed **873ms** on its first invocation and **6ms** on its third at the pre-scaling size — a 145× cold/warm ratio (dynamic linking + arena first-touch). Any Z4 timing taken from a single run is worthless. Best-of-3 minimum, always.

## 3. THREE DEFECTS ISOLATED (all at HEAD, all pre-existing, NONE caused by this session)
Each was narrowed to a minimal repro by bisecting probe features, not by reading code.

**(a) STORED PATTERN SEGV — 4 lines, port-INVARIANT.**
```
        P = SPAN('abc')
        S = 'abc123'
        S P
END
```
SEGV at HEAD. Also SEGVs with a two-element stored pattern (`BREAK(...) SPAN(...)`). **Identical SEGV under all seven ports** ⇒ NOT a storage-regime defect ⇒ **OUT OF Z4 SCOPE** (it lives upstream, in the DT_P / PAT$ blob path). This tightens `GOAL-SNOBOL4-BB.md`'s "stored pattern SEGV localized" (s204) to a 4-line repro. The equivalent INLINE pattern runs green, which is what makes the probe set possible at all.

**(b) CAPTURE START IS WRONG — two opposite manifestations.**
Anchored (`&ANCHOR=1`), capture drops the FIRST character:
```
        &ANCHOR = 1
        S = 'abcdefghij0123456789'
        S SPAN('abcdefghij') . D
        OUTPUT = 'D=[' D '] SIZE=' SIZE(D)
```
SPITBOL `D=[abcdefghij] SIZE=10` · SCRIP `D=[bcdefghij] SIZE=9`. Confirmed on three subjects (`abcde`→`bcde`, `xy`→`y`) — always exactly one character, always from the FRONT, so it is a start-delta error, not a length error.
Unanchored, a capture PRECEDED by another element starts too EARLY instead: `S BREAK('0123456789') SPAN('0123456789') . D` on `'abc123def'` gives SPITBOL `D=123` vs SCRIP `D=abc123` (starts at 0, i.e. the documented "capture start zeroed" class). Only reachable under `forth` (every other port SEGVs first), so port-dependence is UNDETERMINED and must not be claimed either way.

**(c) `--compile` writes asm to STDOUT**, not to a file — mode-4 requires the explicit `gcc -no-pie $f.s -L<out> -lscrip_rt -Wl,-rpath,<out> -o $f.bin` step (canonical line lifted from `scripts/bench_prolog_*.sh`). Recorded because a Z4 walker WILL trip on it when building the m3/m4 matrix.

⛔ **NONE OF (a)/(b) IS FIXED HERE, DELIBERATELY.** RULES.md is MONITOR-FIRST: a divergence is bracketed with the 2-way sync-step monitor before a line is touched. Both belong to `GOAL-SNOBOL4-BB.md`'s ladder, not to Z4. They are recorded here because they (i) shaped the probe set and (ii) give that goal two free, minimal repros.

## 4. PROBE SET — design decisions, so nobody "fixes" them later
`z4_arith` (straight-line arith) · `z4_span` (BREAK/SPAN rescan) · `z4_arbno` (ARBNO backtrack, the RBP-pin/dynamic-housekeeping stressor) · `z4_fib` (DEFINE recursion, the activation-cost probe) · `z4_capture` (capture slots, the s206 defect class).
- **INLINE patterns ONLY** — stored patterns are excluded because of §3(a): including them would measure an unrelated upstream crash instead of the storage regime.
- **`z4_capture` is knowingly DIFF at HEAD** (1500000 expected vs 1500000−150000 actual = exactly one char per iteration, §3(b)). It is KEPT as a perf probe and as a live regression canary for the capture fix; its `.ref` is SPITBOL truth and is NOT to be re-baselined to SCRIP's wrong answer.
- Sized so SPITBOL runs 23–221ms and SCRIP 21–116ms — long enough to time, short enough that a full 4-config × 5-probe × 2-mode sweep stays cheap.

## 5. NEXT
Z4-0 is COMPLETE except the R-* rulings (Lon). Next rung Z4-1 (R12 archaeology worktree at `f7de3863`). **Newly load-bearing for Z4-9/Z4-10:** the cut must not keep a config the gate does not cover — §1 shows exactly what unguarded configs become.
