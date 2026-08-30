# FINDING — sieve's leak is not "1x or 2x per marking cycle": it is a constant +352 bytes on every
# flags[i]=FALSE (skip) outer-loop iteration and exactly 0 on every flags[i]=TRUE iteration, regardless
# of the inner while-loop's trip count. Root cause located in the emitted .s: node 69 is a two-
# predecessor join whose "skip" arrival computes its release from the WRONG run's own local depth. A
# third distinct site, not Site 1 or Site 2. Also: node 38 was never in this row's own candidate list
# because its defect lives in wpop, and that census was gpop-only.

**seat14 · 2026-08-30 · row `pascal-m4-for-spine-leak-64b-per-iter`**, continuing this row's own CURRENT
NEXT block (hq_C's routed message: "if anyone wants to keep MEASURING... the sharpest open question...
what picks 1x vs 2x per marking-cycle... hq_C reads this as the SAME question as which predecessor
arrived"). Fresh `make pristine` first (SCRIP HEAD `ae078681`, `RT_OPT=-O0` confirmed in the build log).

**Not a cure — diagnosis only, same restraint as every prior actor on this row and its siblings.**
Nothing committed to SCRIP or corpus; this FINDING is the only change. Per hq_C's own explicit routed
ruling on this row's current NEXT block, no per-node `zd_plan` patch was attempted here.

## 0. Re-verified the grid fresh first

All 9 kernels built m4 (`--compile` + `gcc -no-pie`, linked `out/libscrip_rt.so`) and run under
`setarch -R`:

| kernel | rc | vs .ref |
|---|---|---|
| bubble | 139 (3/3) | FAIL |
| sieve | 139 (3/3) | FAIL |
| quick | 0 | wrong output — `pascal-quick-wrong-checksum-m3`, independent, not touched here |
| intmm / queens / perm / towers / uplevel2 / uplevel3 | 0 (3/3 each) | MATCH `.ref` |

Unchanged from every prior session on this row — the tree has not drifted on this specific point.

## 1. The "1x/2x per marking cycle" framing is wrong — it's per SKIP iteration, not per prime

gdb (`setarch -R`, `echo 1 |` stdin, standalone `--compile` + `gcc -g -no-pie` build), breakpoints at
`n31_var_bx` (the outer `for i` / `i<=limit` test — fires every outer iteration) and `n39_var_bx`
(fires only when `flags[i]` is TRUE, i.e. only when the `if` body is entered). Logged `$rsp` at every
`n31` hit and tagged each inter-hit interval by whether `n39` fired inside it, plus an `n50_var_bx`
(while-body) count to capture inner trip count per interval:

- **Every interval where `flags[i]` was FALSE (no `n39` hit): Δrsp = +352. 198/198, zero exceptions.**
- **Every interval where `flags[i]` was TRUE (`n39` fired): Δrsp = 0. 45/45, zero exceptions —
  independent of inner `while`-loop trip count (observed 12 to 2730 inner iterations across those 45
  intervals).**

This fully explains the "352 or 704" delta this row's own standing FINDING measured between successive
*prime-found* groups
(`FINDING-2026-08-30-seat05-pascal-sieve-m4-leak-quantized-352-or-704-per-marking-cycle-n76-n79-unreached.md`):
it is **(number of skip-iterations between two found primes) x 352** — one skip between them gives 352,
two gives 704. Nothing about the marking/while loop's own iteration count matters; that part of the
mechanism is provably self-consistent (net zero, confirmed across roughly three orders of magnitude of
trip counts). **hq_C's question — "what picks 1x vs 2x, same question as which predecessor arrived" —
has a precise answer: it is not the marking loop's predecessor at all.** The real discriminating join is
at the *outer* loop's if-check, detailed in §2.

Trace: `n31`/`n39`/`n50` breakpoint log, 13,685 lines, 312 outer-loop cycles captured before the same
SIGSEGV (`n31_var_bx`, `mov qword ptr [rsp+0],rax`, past the mapped stack top — matches every prior
session's crash site and direction).

## 2. Root cause, located in the emitted .s: node 69 is entered at two different depths by construction

Static CFG (`SCRIP_ZD_MAP=1 SCRIP_ZD_DIAG=1 SCRIP_ZD_BACKEDGE=1 ./scrip --compile sieve.pas`),
cross-referenced to source line-by-line:

- `i=38` `IR_BINOP_TEST` (`flags[i] <> 0`, i.e. `if flags[i] then`), run `claim=29` (h=29), `g=39 o=69`.
  `K=16 zout=144 gpop=0 wpop=128`.
- `i=69` `IR_VAR` (start of `i := i + 1`), run `claim=65` (h=65 — `count:=count+1` then the increment),
  entered two structurally different ways:
  - **gamma from `i=68`** (`count := count+1`'s own ASSIGN, same run h=65, straight-line): emits **no**
    `add rsp` at all — `n68_assign_alpha` (`sieve.s:1329`) falls straight through to
    `n69_var_alpha` (`sieve.s:1338`), zero pops.
  - **omega from `i=38`** (the `flags[i]` FALSE/skip arm): emits `add rsp,16` + `add rsp,128` = **144**
    total (`sieve.s:671-672`; the `rt_jct_relop`-fallback arm of the same node agrees on the identical
    144, confirmed by direct read).

Both land at the **identical instruction**, `n69_var_alpha: sub rsp,16 ...` (`sieve.s:1338`). **A single
physical target is entered 0 bytes short one way and 144 bytes over-released the other way.**

Why: `i=38` belongs to run `h=29`; its omega-target (`i=69`) belongs to run `h=65`. Pass-0 processes run
heads in ascending node-index order, so `h=29` is planned *before* `h=65`. At the moment `i=38`'s
`zwpop` is computed, node 69 is not yet `zon` (armed) — so `zd_plan`'s own back-edge detector
(`_zbe && ot && zon[tk]`, `emit.cpp:2592`) never fires for this edge: it is not recognized as a
back-edge at all, and falls through to the plain forward formula (`emit.cpp:2604`,
`zwpop[i] = _wzdepth - K + kc`) — computed entirely from run `h=29`'s own local accumulator, with **no
reference whatsoever to what run `h=65`'s own later, independent walk will assume at that same node.**
This is exactly hq_C's structural diagnosis, routed onto this row's current NEXT block ("per-node scalar
filled by one forward accumulator... a node reachable at two runtime depths has nowhere to put the
second value") — here located to an exact node pair and exact byte counts, not just the general shape.

## 3. Arithmetic fully reconciled — gdb measurement matches independent instruction counting to the byte

Split-measured via a second gdb pass (breakpoints at `n31_var_bx` and `n69_var_bx`, same methodology):

- `n31`-entry -> `n69`-entry (via the skip arm, one representative cycle): **+16** measured.
  Independent check from the `.s`: nodes 31,32,33,34,35,36,37,38 each carve 16 (128 total — confirmed
  directly for 31/32/33/34/35/37/38, and for 36, an `IR_CALL` with its own internal fast/slow-path
  scratch, by closing the equation: -128+144 must equal +16 for the measurement to hold, and it does).
  Released 144 at `i=38`'s exit. Net: -128+144 = **+16.** Matches.
- `n69`-entry (same cycle) -> next `n31`-entry: **+336** measured.
  Independent check: `n69`,`n70`,`n71` each carve 16 (48 total; `n71`'s own internal binop temp is
  released only on a rare integer-overflow arm that exits directly to `n73`, bypassing `n72` entirely —
  not the arm taken on this path, confirmed by reading `sieve.s:1352-1397`). `n72` carves nothing of its
  own and releases the for-loop's own back-edge constant, **384**, jumping to `n31`
  (`sieve.s:1406`). Net: -48+384 = **+336.** Matches.
- **16 + 336 = 352**, matching §1's measured per-skip delta exactly, via two independent methods (direct
  gdb measurement and static instruction accounting) that agree to the byte.

## 4. This is a third distinct site, not Site 1 or Site 2

- **Site 2** (`zd_omega_head`/per-op-filter) landed clean and gate-confirmed this session (seat06's
  FINDING, cited on the sibling row `pascal-m4-site1-forloop-backedge-64byte-excess`) — and sieve is
  still red under that same clean tree (reconfirmed §0), so Site 2 is not this.
- **Site 1** (seat09's FINDING, same sibling row): a same-*run* diamond (`i=89` on bubble.pas — both the
  taken and skipped arms are claimed by the *same* pass-0 run) whose own back-edge/exit constant was
  computed assuming the walk's gamma-only path (the bigger arm) always runs. That row's own DONE-WHEN is
  scoped to `bubble`/`quick` only; sieve was never in its population.
- **This mechanism**: the two disagreeing arrivals are in **different runs** (`h=29` and `h=65`), and
  the edge that gets it wrong (`i=38`'s omega) is a **forward reference, by node index, into a run that
  has not been claimed/armed yet** — not a back-edge to an earlier run. (That case — genuine back-edges
  — works correctly here: both `i=64->45` [288] and `i=72->31` [384] are real back-edges via the
  `gback`/`oback` mechanism and are internally self-consistent, confirmed by §1's "prime cycles net 0"
  result holding across 12-2730 inner trip counts.) Site 1's mechanism (embedded diamond, one run) and
  this one (cross-run forward reference into an unarmed run) are different failure shapes inside the
  same accumulator design; a fix for one is not guaranteed to cover the other. Tentatively labeling this
  **Site 3** for reference below — not an HQ-ratified name, just so the next actor has a handle for it.

## 5. A correction to this row's own standing candidate list

`i=38` does **not** appear in seat02's earlier "5 non-zero-gpop nodes" census (28, 64, 72, 76, 79 — this
row's own prior FINDING,
`FINDING-2026-08-30-seat02-pascal-m4-grid-drifted-quick-fixed-sieve-newly-fails-not-bubbles-single-node-shape.md`)
or seat05's own `SCRIP_ZD_SKIP` sweep over those same 5 — which is exactly why none of those five,
tested individually, ever cured sieve. **The reason: that census was, implicitly, `gpop`-only. Node
38's `gpop` is 0 — its defect lives entirely in `wpop` (128, confirmed above).**
`SCRIP_ZD_DIAG=1`'s own raw output already prints both columns unconditionally (`emit.cpp:2605`); the
earlier reading filtered on the wrong one. Confirmed directly from this session's own diagnostic dump:
`[ZD] h=29 r=9 i=38 IR_BINOP_TEST K=16 zout=144 gpop=0 wpop=128`.

## 6. Feeds the standing design question directly

hq_C's option (c) ("normalize arrivals so a join has one depth by construction, touching no template",
routed onto both this row's and `calling-convention-depth-tracked`'s current NEXT blocks) now has a
second, precisely-measured worked example beyond Site 1: node 69 needs its two arrivals (0 and 144)
reconciled to one, and the mechanism producing each side is now fully traced. Not proposing a
normalization design — per this row's standing authorization (routed from hq_C) and
`calling-convention-depth-tracked`'s ownership of the actual cure, that is out of scope here.

## 7. Not attempted

No code touched — `git status --short` clean across all three repos throughout, checked directly before
and after. No `zd_plan` patch attempted, per hq_C's explicit routed ruling on this row's current NEXT
block.

## State

SCRIP HEAD `ae078681`, fresh `make pristine`, `RT_OPT=-O0` confirmed in the build log. corpus/`.github`
pulled current at session start and re-pulled immediately before this write (no drift on this row's own
task file during the session; heavy unrelated fleet activity landed on `.github` elsewhere in the
meantime, pulled clean via rebase). Traces: `sieve.pas` compiled standalone (`--compile` -> `gcc -g
-no-pie`, linked against `out/libscrip_rt.so`) for gdb, matching seat05's own methodology; the 9-kernel
grid in §0 separately re-verified through the full corpus-style build+run, not just the gdb witness.

## Next actor

1. This row's own standing item (node 76's negative `gpop=-48`, unreached before the crash per seat05's
   own FINDING) remains open but low priority — still just a latent curiosity, not this mechanism.
2. The actual cure is out of scope on this row per hq_C's ruling — route through
   `calling-convention-depth-tracked` once that design is runnable; this FINDING is intended as one of
   its concrete worked examples (§6). Whoever designs the normalization should look at Site 1 (embedded
   diamond) and this "Site 3" (cross-run forward reference to an unarmed run) side by side — they may
   need the same fix or two different ones; not determined here.
3. Re-verify the grid fresh regardless before trusting any of this — HEAD moves fast on this repo, as
   every session on this row (including this one) has found.
