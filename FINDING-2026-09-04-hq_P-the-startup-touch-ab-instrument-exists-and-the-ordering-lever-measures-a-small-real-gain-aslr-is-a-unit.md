# FINDING: the startup-touch A/B instrument now exists and answers the row's question — the `-ffunction-sections` + link-ordering lever measures a small REAL gain (m3 minflt 1.022x, maxrss 1.107x), the ordering does the work rather than the flag, and ASLR turns out to be a UNIT that no prior number on this campaign named

Seat: hq_P · MODE `FLEET-16` · 2026-09-04 · Row: `rtx-startup-linker-ordering` (rank 2, ASSIGNED:hq_P by ceo)
Tree: SCRIP `3dbb5aefe` (measured at parent `59589ee97`) · corpus `34cf6472d` · incremental `make` · `RT_OPT=-O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`
Landed: `SCRIP/scripts/bench_startup_touch_ab.sh` (the row's DONE-WHEN is this script exiting 0)

## 1. Why this row needed a script and not another measurement

The campaign had four separate hand-run passes across four sessions and could not answer its own question, for two reasons the GOAL names: seat14 measured arm A at `minflt 248.9` on one tree while seat01 and seat07 measured `743.6` on another, so any subtraction across them manufactures a ~495-fault "saving" out of a tree difference; and `-ffunction-sections` alone is not the A/B, so the one arm anybody could cheaply run would have read ~zero and retired a live lever. The instrument makes both impossible by construction: **both arms are built and measured in ONE process, on ONE tree, with ONE instrument**, and the flag-only build is present but labelled a control.

## 2. The measurement

7 runs per cell, m3 and m4, do-nothing witness (`OUTPUT = 1` / `END`), `/usr/bin/time -f '%R %M'` under `setarch -R`. Multiples are `A/arm` on the faster axis, so above `1.00x` means fewer faults or less RSS than arm A.

| mode | arm | minflt mean (min–max) | maxrss kB mean (min–max) | x faults | x rss |
|---|---|---|---|---|---|
| m3 | A — the tree's own build | 815.9 (814–817) | 8817.7 (8648–8884) | 1.000x | 1.000x |
| m3 | B0 — flag only, **control** | 813.0 (813–813) | 8895.4 (8716–8960) | 1.004x | 0.991x |
| m3 | **B — flag + ordering, THE LEVER** | **798.4 (797–799)** | **7966.9 (7768–8000)** | **1.022x** | **1.107x** |
| m4 | A | 312.6 (311–315) | 4796.0 | 1.000x | 1.000x |
| m4 | B0 | 311.4 (311–312) | 4775.4 | 1.004x | 1.004x |
| m4 | B | 311.3 (311–312) | 4770.3 | 1.004x | 1.005x |

**VERDICT: GAIN — small, real, and m3-only.** Arm B's entire spread (797–799) sits below arm A's best run (814), so the fault delta is not sampling noise. ⭐ **Arm B0 is the load-bearing row of this table:** the flag alone moves faults 1.004x and RSS *backwards* (0.991x, the split's own padding), so **the ordering does the work, not the flag** — exactly what seat14 predicted and deliberately refused to measure half of. The m4 arm barely moves, which is consistent: a mode-4 binary touches far less of the RT (312 faults against 816).

Section layout, arm B: `.text` 5,358,898 → 4,536,994 bytes plus `.text.startup_hot` 821,899 bytes (201 pages), covering the **500 functions callgrind saw execute inside the `.so`** on the witness. ⛔ Pages are an upper bound, never a fault saving (seat07's rule, and this measurement is why it stands: 201 pages clustered bought 17 faults).

## 3. ⭐ ASLR IS A UNIT, AND NO NUMBER IN THIS CAMPAIGN EVER NAMED IT

Isolated on the *same canonical binary*, same witness, same instrument, three runs each:

| arm | minflt |
|---|---|
| `./scrip` with ASLR on (no `setarch`) | 742–744 |
| `setarch -R ./scrip` (ASLR off) | 815 (×3, no spread) |
| the script's own relinked arm-A driver, ASLR on | 742–744 |

So **disabling ASLR costs ~73 minor faults here**, and the relinked driver costs nothing — the difference is entirely the ASLR setting. ⛔ **An absolute startup floor quoted without naming its ASLR state is not comparable to one that names it.** This is the "mode is a unit" clause (seat07's near-miss, where m3 237 pages and an m4 237-fault figure looked like the same number) wearing a third costume: a hidden axis that shifts the absolute number while leaving every within-arm delta intact. It does **not** explain seat14's 248.9-vs-743.6 discrepancy — that is a 3x gap and this is 10% — but it does mean the campaign's three floors were never strictly comparable even before trees are considered. The A/B is unharmed: all arms are measured under one setting, which is the whole design.

## 4. What the instrument refuses to do, proven in the FAIL direction

Exit codes follow `lib_gate.sh`: 0 measured (a GAIN verdict and a NO-GAIN verdict are both green — the row asked for the number, not for the lever to win), 1 the lever breaks the witness, 2 could not measure. Tested **unpiped**, because a verdict read through a pipe is the pager's: `RUNS=2` rc=2 · `RUNS=abc` rc=2 · missing `WITNESS` rc=2 · **an empty scratch root rc=2** (the V2-5 can-it-say-no meta-gate standard). Correctness is checked before any timing on every arm in both modes against arm A's own output — a wrong answer is never a fast answer.

Two portability repairs made before the first real run, both caught by reading rather than by a red: `readelf` section sizes are parsed **without gawk's `strtonum`** (this box runs mawk 1.3.4, where that function does not exist and the arithmetic would have silently yielded 0, i.e. a false "the fragment matched nothing" refusal), and the `[N]` index column is stripped before fields are counted.

## 5. What was NOT done, deliberately

**The lever is not landed.** Arm B lives entirely in a scratch directory; the tree's canonical `out/libscrip_rt.so` is never re-pointed and arm B0 carries its own `RT_TAG`, so no arm can disturb another or the seat's own build (verified after the run: the symlink still names `libscrip_rt-f65f143e2f.so` and `./scrip` still prints `1`). Landing `-ffunction-sections` plus an ordering fragment in the Makefile is a **separate, gated decision** — it touches the object every frontend links, so it owes the SHARED-NODE battery: SNOBOL4 blocking set FAIL=0 over the printed denominator plus the Icon pinned watermark. On a 2.1% fault gain that trade is a judgement, not an obvious yes, and it belongs in its own row with its own control arms.

No SCORE.md row is rewritten: this is a startup-floor instrument on a do-nothing witness, not a suite run, and no cell on the board grades it.
