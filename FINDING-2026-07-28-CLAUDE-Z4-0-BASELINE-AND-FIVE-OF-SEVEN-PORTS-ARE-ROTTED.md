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

---

# ADDENDUM — Z4-1 STARTED SAME SESSION: THE R12 EPOCH BUILDS, RUNS, AND IS THE ONLY 5/5-CORRECT CONFIG MEASURED

Worktree `f7de3863` (s65 R12-ERAD, the anchor the COMMIT-SELECTION LAW predicted). **It builds on today's toolchain** after installing `libgc-dev` — the epoch's OWN dependency, which HEAD dropped at GC-U-4 s67 (`REPO-SCRIP.md` records the removal). Extraction-by-reading was NOT needed. Both `scrip` and `libscrip_rt.so` built; each epoch's compiler was paired with its own runtime, never mixed across epochs.

## THE CROSS-EPOCH TABLE (RT_OPT=-O0, best-of-3, mode 3, same probe bytes, same oracle refs)
| probe | CONFIG 1 R12 (s65) | FRAME-RSP (s65 default) | CELL-STACK (HEAD) | SPITBOL |
|---|---|---|---|---|
| z4_arith | 46 OK | 45 OK | **43 OK** | 221 |
| z4_span | 380 OK | 346 OK | **116 OK** | 98 |
| z4_arbno | **35 OK** | **SEGV** | 23 OK | 45 |
| z4_fib | 71 OK | **60 OK** | **98 OK** | 43 |
| z4_capture | 105 OK | 96 OK | 27 **DIFF** | 23 |
| **correct** | **5/5** | 4/5 | 4/5 | 5/5 |

## WHAT THIS SAYS, PLAINLY
1. **⭐ CONFIG 1 (R12 island frames) IS THE ONLY 5/5-CORRECT CONFIGURATION MEASURED.** It passes `z4_arbno`, which SEGVs under the SAME epoch's RSP default, and it passes `z4_capture`, which is WRONG at HEAD. Reconstructing it is therefore worth more than a historical curiosity — it is a correctness reference oracle for the other three.
2. **⭐ THE CELL PIVOT'S LEDGER IS MIXED, AND BOTH HALVES ARE REAL.** WINS: span 380→116 (**3.3×**), capture 105→27 (**3.9×**), arbno fixed-and-faster. LOSS: **z4_fib 60→98 — DEFINE-recursion activation cost regressed 1.6× against the frame technique.** The "CELL is more performant than FRAME" premise holds decisively for pattern work and is FALSE for calls. Whichever config the campaign ends on, the call path is the thing to fix; `z4_fib` is its instrument.
3. **⭐ THE CAPTURE DEFECT IS A REGRESSION, BISECTABLE.** s65 computes `capture 1500000` (SPITBOL-exact) under BOTH its bases; HEAD computes 1350000. The defect entered between `f7de3863` and `cca948c5`, and the `.ref` is vindicated as truth rather than a probe-authoring error. Handing `GOAL-SNOBOL4-BB.md` a known-good epoch + a 4-line repro + a bisect range is worth more than any patch this session could have attempted.
4. **R12→RSP was a genuine perf win at s65** (~8-15% across every probe: 46/380/71/105 → 45/346/60/96), which is exactly the "hunt of faster" motive Lon described — and it cost `z4_arbno`, which SEGVs under RSP at that epoch. The trade was real and was paid in correctness.

## MECHANICS WORTH INHERITING (Z4-2 will need all four)
- `git worktree add <dir> <sha>` + `apt-get install libgc-dev` for any pre-s67 epoch.
- The R12 basis is selected by editing `#define ZC_FRAME ZC_FRAME_R12` in `src/contracts/zeta_choices.h`, then `rm -f scrip && make -j4 scrip && make libscrip_rt` — BOTH, or the compiler and runtime disagree about the basis.
- Old-epoch `--run` needs `< /dev/null` (RULES.md) and best-of-3 (cold start).
- Do NOT chase contemporaneous corpus SHAs: identical probe bytes across epochs is what makes the table legitimate.

## NEXT
Z4-1 remains OPEN for its documentation deliverable (`EXTRACT-Z4-R12.md`: island-cursor mechanics, zr/fb accessor shapes, and the era-arm → HEAD-arm PAIRING TABLE with a fresh recount of the s202 "17 arms" claim). The build/run/measure half is DONE and recorded above. Z4-3's cross-epoch table is effectively pre-populated by this addendum; Z4-2 (cstack anchor, `879a0d37..be4bb739^`) is the remaining unmeasured column.

---

# ADDENDUM 2 — Z4-2 DONE: THE TABLE IS COMPLETE, AND THE CALL PATH HAS DEGRADED MONOTONICALLY ACROSS ALL THREE GENERATIONS

**Anchor chosen: `d79a427a`, NOT `879a0d37`.** The COMMIT-SELECTION LAW says "last commit at which the config was PROVEN green"; `d79a427a` is the LAST `ZC_PORT_CSTACK`-default commit before the OWNED per-BB pivot and its own message carries the proof (crosscheck byte-identical m3 284/7 · m4 283/7/1; smokes sno 7/7, icon 12/12×2, prolog 5/5×2). The plan's provisional `879a0d37` was merely the FIRST such commit. Builds clean on today's toolchain with `libgc-dev`; scrip + libscrip_rt paired from the same tree.

## THE COMPLETE CROSS-EPOCH TABLE (m3, RT_OPT=-O0, best-of-3, identical probe bytes + oracle refs)
| probe | CONFIG 1 R12 `f7de3863` | CONFIG 2 CSTACK `d79a427a` | CONFIG 3 CELL-STACK HEAD | SPITBOL |
|---|---|---|---|---|
| z4_arith | 46 OK | 47 OK | **43 OK** | 221 |
| z4_span | 380 OK | 358 OK | **116 OK** | 98 |
| z4_arbno | 35 OK | 33 OK | **23 OK** | 45 |
| z4_fib | **71 OK** | 83 OK | 98 OK | 43 |
| z4_capture | **105 OK** | 120 OK | 27 **DIFF** | 23 |
| **correct** | **5/5** | **5/5** | 4/5 | 5/5 |

## ⭐ THE FINDING THAT REFRAMES THE CAMPAIGN
**`z4_fib` (DEFINE recursion) has regressed MONOTONICALLY across every storage generation: 71 → 83 → 98 ms.** Not one bad pivot — a consistent, cumulative drift, each generation paying call cost to buy pattern-matching speed. Over the same three generations `z4_span` improved 380 → 358 → 116 (**3.3×**) and `z4_arbno` 35 → 33 → 23 (**1.5×**). Against SPITBOL, HEAD is **5.1× faster on arithmetic** and **2.3× slower on calls**.

**CONSEQUENCE FOR THE FOUR-CONFIG END STATE:** the campaign's premise ("CELL is more performant than FRAME") is TRUE for pattern work and FALSE for calls, and the falsity is now quantified across three independent trees rather than inferred. The activation/call path is where the remaining performance lives; `z4_fib` is its instrument and belongs in Z4-10's gate as a RATCHET, not merely a pass/fail — a config that regresses it should have to say so out loud.

**BOTH FRAME CONFIGS ARE 5/5 CORRECT; THE CELL CONFIG IS 4/5.** Configs 1 and 2 both compute SPITBOL-exact `capture 1500000`. This independently corroborates ADDENDUM 1's regression claim from a SECOND tree 130+ commits later: the capture defect entered AFTER `d79a427a`, tightening the bisect range from `f7de3863..cca948c5` to **`d79a427a..cca948c5`**.

## RULINGS TAKEN (Lon: "All your choices", 2026-07-28) — record, and overturn freely
- **R-A ACCEPTED — ONE 4-value selector.** Mixed regimes must be unrepresentable (the s188 disease); one enum buys that structurally, and the `SCRIP_CELLS`×`SCRIP_ZMODE` matrix that `GOAL-SN4-CELL-MACHINE.md` flags UNSPECIFIED collapses to four named points.
- **R-B ACCEPTED, ANCHOR CORRECTED — config 2 = the CSTACK embodiment at `d79a427a`** (measured 5/5 above), not `879a0d37`.
- **R-C ACCEPTED — config 1 via the parameterized `ZC_FRAME_R12` form**, re-expressed under current `x86()` rules. Justified beyond history: it is a 5/5 correctness ORACLE.
- **R-D ACCEPTED — coexpr = loud decline under configs 1-2** (their documented historical limit; never a silent wrong answer).
- **R-E STILL OPEN — ζ_self/VSP is Lon's architectural call.** Blocks Z4-8 only; deliberately NOT self-ruled, since it decides where results live rather than merely how the existing code is packaged.
- **R-F — keep `GOAL-ZETA-FOUR.md`; PLAN.md's Active-Goals row is Lon's edit** (RULES.md forbids editing that table on routine handoff).

## NEXT SESSION STARTS HERE
Z4-1's remaining deliverable is documentation only (`EXTRACT-Z4-R12.md` — island-cursor mechanics, zr/fb accessors, era-arm→HEAD-arm PAIRING TABLE, fresh recount of the s202 "17 arms"). Then **Z4-4 (selector spine, additive)** — all three rulings it depends on are now settled, and both worktrees exist and build, so the reconstruction has working reference implementations on disk rather than only in git.
