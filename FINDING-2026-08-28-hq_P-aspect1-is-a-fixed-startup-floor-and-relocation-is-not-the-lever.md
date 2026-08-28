# Aspect-1's loss is a FIXED startup floor every SCRIP program pays — and the relocation lever, tested, is not it

**Seat:** hq_P · **Date:** 2026-08-28 · **Mode:** DUO · **Row:** Lon tier-1 demo campaign (aspect 1)
**Status:** measurement + one **negative result**. No cure landed; two plausible levers killed cheaply, one confirmed.

## Why this exists

On aspect 1 (whole process, compile included) SCRIP loses **every** tier-1 row, 3–4x. `ceo` dug it and
attributed *"~80% is PAGE FAULTS not syscalls"*, naming the `x86()` encoder string path as the user-side
lever. This re-measures that attribution before anyone spends design-scale effort against it.

## 1. The split is ~55/45, not ~80/20

Best-of-5 CPU, `treebank-match`, via `tools/bench_rusage`:

| engine | user | sys | cpu |
|---|---|---|---|
| clean oracle | 0.00 ms | 0.88 ms | 0.88 ms |
| m4 | 1.16 ms | 2.31 ms | **3.47 ms** |
| m3 | 2.96 ms | 3.94 ms | 6.90 ms |

m4's gap over the oracle is 2.59 ms: **sys 1.43 ms (55%), user 1.16 ms (45%)**. Sys is the larger half —
so the direction was right — but **both halves are load-bearing and neither alone closes the gap.**
⚠️ Note `sys` here is not synonymous with page faults: it also carries exec, mmap and dynamic loading.

## 2. ⛔ NEGATIVE RESULT: dynamic relocation is NOT the lever, and it looked like it should be

`libscrip_rt.so` carries **`.rela.dyn` = 3.19 MB — 132,389 `R_X86_64_RELATIVE` entries** applied at every
process start, against an oracle that is a single 272 KB binary. That is an obvious suspect.

Tested properly rather than by wall-clock A/B (which sat in the noise at ~2–3% and would have been
over-read either way). Relinked the *same* objects with `-Wl,-z,pack-relative-relocs` (DT_RELR):
relative relocations **132,389 → 1,014**, `.so` 34.4 MB → 31.3 MB, output byte-identical.

`LD_DEBUG=statistics`, which measures the loader directly:

| | total loader startup | relocation time | relative relocs |
|---|---|---|---|
| baseline | 694,927 cycles | 458,769 | 133,403 |
| DT_RELR | 664,966 cycles | 427,759 | 1,014 |

⭐ **Packing away 132,389 relocations saved 31,010 cycles — about 0.01 ms, roughly 0.4% of the 2.59 ms
gap.** The loader's RELATIVE loop runs at ~3 relocations per cycle; the whole dynamic-loader startup is
only ~0.23 ms. **A 3.19 MB section that is processed 132,389 times per run costs almost nothing, and no
amount of staring at the section sizes would have told us that.** Not landing the flag: a build change
that buys 0.4% is not worth the link-line divergence.

## 3. ⭐ WHAT IT ACTUALLY IS: a fixed floor, paid before any work happens

| program | maxrss | minor faults |
|---|---|---|
| **tiny (m4)** — a program whose whole body is `OUTPUT = 1` | **9,044 kB** | **602** |
| treebank-match (m4) | 12,712 kB | 844 |
| tiny (m3) | 13,092 kB | 1,109 |
| treebank-match (clean oracle) | **1,948 kB** | **170** |

**A SCRIP program that does nothing already costs 9 MB resident and 602 minor faults.** The oracle's
entire real run costs 1.9 MB and 170. treebank-match's actual work adds only 3.7 MB and **242** faults on
top of the floor — so on these demos we are not losing on the work, **we are losing on the entry fee.**

That floor is the `-O0` runtime `.so` being paged in: `.text` **5.19 MB**, `.rodata` 1.38 MB,
`.data.rel.ro` 1.12 MB (fully written during relocation, so guaranteed touched). ⛔ `.bss` is 53.5 MB
declared but is zero-fill-on-demand and **not** the cost — the largest symbol, `dat_types` at 17.5 MB, is
indexed by a counter and only its used entries are ever touched. I checked that before blaming it,
because 17.5 MB sat suspiciously close to the 18 MB resident figure and the coincidence is a trap.

## 4. What follows

⛔ **The floor cannot be optimised away in C**: `RT_OPT` is `-O0` by Lon's standing FACT RULE, so `.text`
is unoptimised by mandate. **Shrinking it is structurally the RTX program's job** (replacing RT C with
ASM), which is exactly where `ceo` placed it — this measurement raises its priority from "long-term" to
"the larger half of the tier-1 aspect-1 loss."

✅ **`ceo`'s user-side lever stands unchallenged**: the `x86()` encoder string path at ~25% of user time,
cured by a string-free BINARY emission path with TEXT keeping strings — a helpers-first divergence under
the new MODES MAY DIVERGE law. That addresses the 45% half.

⚠️ **Stated rather than implied:** nothing here is a cure, and I am not claiming the two halves sum to a
plan. What it buys is that **nobody now spends a week on relocation packing**, and that the fixed-floor
half is sized (~600 faults, ~9 MB, paid by every program including one that prints a single character).

---

# ADDENDUM (same session): the floor is isolated to **library load**, three levers are dead, and one works

## The floor is `libscrip_rt.so` being loaded — 430 faults before any work

| program | maxrss | minor faults | cpu |
|---|---|---|---|
| C `main(){return 0;}`, RT **not** loaded | 1,252 kB | 67 | 0.34 ms |
| C `main(){return 0;}`, RT **loaded** (`--no-as-needed`) | 8,672 kB | **497** | **2.15 ms** |
| m4 program whose body is `OUTPUT = 1` | 9,044 kB | 531 | 2.22 ms |

**Merely loading the runtime costs 430 extra minor faults, 7.4 MB resident and ~1.8 ms.** The m4
program's own initialisation adds **34 faults**. The clean oracle's *entire real run* is 170 faults.

⛔⛔ **A CONTROL-ARM TRAP I FELL INTO AND CORRECTED, recorded because it nearly produced a published
reversal.** My first control linked `-lscrip_rt` and measured **0.34 ms**, which said the library was
free and my original attribution was wrong. It was the control that was wrong: **`--as-needed` is the
default, the control referenced no symbol from the library, and the linker dropped the `DT_NEEDED`
entry entirely** — so the "control that loads the RT" never loaded it. `ldd` shows 0 references.
Rebuilt with `--no-as-needed`: **2.15 ms**, and the original attribution stands. ⭐ **A control that
silently does not exercise the thing under test agrees with every hypothesis.**

## Three levers, measured dead

| lever | what it changed | effect |
|---|---|---|
| `-Wl,-z,pack-relative-relocs` (DT_RELR) | 132,389 relative relocs → 1,014 | **0.4%** of the gap (`LD_DEBUG`: 31,010 cycles) |
| `-Wl,-Bsymbolic-functions` | loader startup 601,580 → 483,879 cycles (−19.6%) | **~1.3%**, and end-to-end it was **+3.3% / −5.5%** on two programs — inside noise |
| `strip --strip-debug` | `.so` 34.4 MB → 12.5 MB (−64%) | **none** (debug sections are never mapped) |

⭐ Two of these look compelling on paper — a 3.19 MB relocation section applied 132,389 times, and a
64% file-size cut. **Neither survives measurement.** The loader's total startup is only ~0.20 ms of the
2.15 ms, so *every* link-level lever is bounded at ~9% before it starts.

## ✅ The lever that works: static linking

| | cpu | maxrss | minor faults |
|---|---|---|---|
| `OUTPUT = 1`, shared | 2.22 ms | 9,044 kB | 531 |
| `OUTPUT = 1`, **static** | **1.08 ms** | 4,632 kB | **194** |
| treebank-match, shared | 2.82 ms | 12,744 kB | 770 |
| treebank-match, **static** | **2.01 ms** | 8,100 kB | **418** |
| treebank-match, clean oracle | 0.48 ms | — | — |

Answers byte-identical in both forms. **Do-nothing floor −51%; treebank-match −29%, taking its aspect-1
multiple from 0.17x to 0.24x.** Static linking maps and touches only the objects actually pulled in,
which is exactly the pages-touched quantity the floor is made of.

⛔ **NOT LANDED, AND THE COST IS WHY — this is a Lon/ceo call, not mine.** The static binary is
**27,404 kB against 32 kB shared.** Every compiled program would carry ~27 MB. It also cuts against
`out/libscrip_rt.so` being the canonical path that 73 scripts reference by name, so it would be an
additional link mode, never a replacement. **It is a real lever with a real price, and the price is not
a perf question.**

⚠️ And it does **not** close the gap: 0.24x is still ~4x behind. The floor is code-size-shaped, `-O0` is
mandated, so the structural cure remains **RTX**. Static linking is worth roughly a third of the
aspect-1 loss for a price someone else has to agree to pay.
