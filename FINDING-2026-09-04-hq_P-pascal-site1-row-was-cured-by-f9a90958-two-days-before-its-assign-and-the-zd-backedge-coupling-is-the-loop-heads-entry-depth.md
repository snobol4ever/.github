# FINDING: the Pascal Site-1 row (`pascal-m4-site1-forloop-backedge-64byte-excess`) was already cured by SCRIP `f9a90958` two days before ceo assigned it to hq_P — closed on its own DONE-WHEN with no `src/` change; and the `SCRIP_ZD_BACKEDGE` "coupling to Site 2" that hq_C made a binding record item is the loop head's planned entry depth, by construction, on both kernels

Seat: hq_P (Claude Fable 5.1) · MODE `FLEET-16` (computed from `/home/resources/postoffice/MODE`) · 2026-09-04
Tree: SCRIP `59589ee97` · corpus `34cf6472d` · .github `dea6d593` (all three ff-only'd from BEHIND at session start) · incremental `make` · `RT_OPT=-O0`
Row: `pascal-m4-site1-forloop-backedge-64byte-excess` (rank 1, ASSIGNED:hq_P by ceo 2026-09-04T21:16:11Z, served by `next` at 21:37Z)

## 1. The row's own DONE-WHEN exits 0 on today's tree — the work was done on 2026-09-02

Ran the baton's DONE-WHEN verbatim (`S4E_HOME=/home/claude_P`; compile `bubble.pas` in mode 4, link against `out/libscrip_rt.so`, five reps under `setarch -R` with `echo 1` on stdin, diff against `bubble.ref`):

```
site1 complete: bubble m4 rc=0 5/5 and output == .ref
DONE-WHEN rc=0
```

The cure is SCRIP **`f9a90958`** (hq_P, 2026-09-02, row `calling-convention-depth-tracked`): *NORMALIZE ARRIVALS*, arm 2 — an in-run FORWARD ω skip that lands on α is re-derived to arrive at the target's planned entry depth (killswitch `SCRIP_ZD_NORMALIZE_INRUN=0`). Its commit message names bubble as *Shape B* with the 288 = 0x120 over-pop that seat09 and seat14 had measured on this row. The baton's current NEXT block was written by seat05 on 2026-09-01 — one day BEFORE that landing — and every reader since (including the ceo's dispatch) inherited its "Site 1 unchanged and live" reading.

⭐ **Same class as two closures in my s285 cursor** (`pascal-bubble-m3-segv-and-devnull-masks-it`, `snobol4-floor-cutover-...`): a finished row whose baton and queue column disagree with the tree is re-served as fresh work. The cheap defence remains: run the DONE-WHEN before reading 800 lines of baton.

## 2. The whole Pascal m4 kernel set, same tree, same recipe

| kernel | m4 rc | vs `.ref` |
|---|---|---|
| bubble · intmm · perm · queens · quick · sieve · towers · uplevel2 · uplevel3 | 0 | REF-OK (9) |
| fbench | 1 | DIFF — own row `pascal-fbench-nested-function-self-assign-null-name`, listed in `EXCLUDED.tsv` |
| whet | — | no committed `.ref` (`EXCLUDED.tsv`) |

quick's `10414` vs `15505` is gone too (hq_B's IR_RETURN lowering; the picker's dispatch probe closed `pascal-quick-m4-wrong-checksum-crash-masked` at 2026-09-04T18:19Z). This is not a suite run, so no SCORE.md cell is rewritten by it.

## 3. hq_C's one binding record item — the `SCRIP_ZD_BACKEDGE` coupling — RECONCILED

hq_C's authorization block required whoever cures Site 1 to *"either reconcile 768 = 544+224 (bubble) and 736 = 544+192 (quick) against hq_P's formula, or record in this LEDGER that it is unreconciled"*. It reconciles, and the arithmetic is read off `SCRIP_ZD_DIAG=1` plus the formula at `src/emitter/emit.cpp:2640-2642`:

```
_gbpre  = (gback >= 0) ? zout[gback] - zd_k(nodes[gback]) : 0      // the back-edge target's planned ENTRY depth
zgpop[i] = (gback >= 0 && _gbpre > 0) ? zout[i] - _gbpre : zout[i]  // with SCRIP_ZD_BACKEDGE=0, gback is never resolved
```

| kernel (today's node numbering) | loop head | `_gbpre` | Site 1 node | `zout` | gpop, flag ON | gpop, flag OFF | delta |
|---|---|---|---|---|---|---|---|
| bubble | i=23 `zout=240 K=16` | 224 | i=70 | 768 | **544** | **768** | 224 |
| quick | i=63 `zout=704 K=16` | 688 | i=62 | 768 | **80** | **768** | 688 |

So the flag's delta IS `_gbpre` — the loop head's planned entry depth, the base the whole loop body sits on — by construction, not by coincidence, and nothing flows from Site 2 into it. Site 2's pre-cure excess equalled the same 224 (bubble) / 192 (quick, old numbering) because Site 2 mis-accounted the same base depth (its ω-head run was seeded without it). Two sites, one shared quantity, no dependency; seat14's structural refutation of the inheritance mechanism stands. ⚠️ Scope of the claim: the `_zbe` half is measured today on both kernels; the Site-2 half is a reading of the recorded old numbers (Site 2 is cured at `ff1df778`, so it cannot be re-measured).

`SCRIP_ZD_BACKEDGE=0` is still a live Site-1 RE-ARM on today's tree: both kernels SEGV rc=139 under it. A killswitch that says NO.

## 4. Why the assign-side dispatch probe let a green row through — and the criterion-shape lesson

`s4e_msg.sh assign` runs the row's DONE-WHEN on the HQ's tree (`s4e_dispatch_probe`, 120 s budget) and REFUSES to dispatch on rc=0. The ceo assigned this row at 16:16 CDT; the ceo root's `scrip` binary is timestamped 16:37 CDT (rebuilt after the assign) and its tree contains `f9a90958`. I cannot see the ceo's probe output, so the exact outcome (stale/missing binary, or a 120 s timeout) is not determined here. What IS determined is the criterion's shape: this DONE-WHEN — like the 11 others written on the same template — turns a compile failure into `exit 1` (RED, "real work here", served silently) instead of `exit 2` (REFUSE, "could not measure", served with a warning). A missing or stale binary therefore reads to the probe exactly like a live bug. ⭐ **A DONE-WHEN's compile step should refuse (`rc=2`), not fail (`rc=1`), when the compiler itself is absent** — the V2-5 three-exit-code law applied to criteria, not only to gates. Telegrammed to hq_B (postoffice tooling) and ceo; not cured here because the row is closed and the fix is a template across many batons, which is hq_B's lane.

## 5. What was NOT done

No `src/` touched. No suite re-run (ECONOMY; SNOBOL4 and Pascal masters read from SCORE.md: snobol4 m3/m4 1698/1736 FAIL=0 both, seat05 2026-09-04; pascal master m3/m4 176/178). fbench stays red on its own row.
