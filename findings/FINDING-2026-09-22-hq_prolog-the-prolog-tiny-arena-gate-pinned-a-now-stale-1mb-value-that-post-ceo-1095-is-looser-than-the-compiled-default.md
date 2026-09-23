# FINDING 2026-09-22 hq_prolog: the Prolog tiny-arena gate pinned a now-stale `SCRIP_HEAP_MB=1`, which post-CEO-1095 is LOOSER than the compiled default, not tighter

## WHAT WAS WRONG

`scripts/test_gate_pl_master_is_clean_at_the_tiny_arena.sh` (mine, row
`prolog-gc-the-prolog-share-of-the-unmapped-slot-population-censused-by-name-and-the-master-clean-at-one-megabyte`)
pinned its "arena" and "stress:N" arms at `SCRIP_HEAP_MB=1` (1024 KB), written 2026-09-20 when that value
genuinely was the exasperating/tiny setting relative to the then-shipped default.

**CEO-1095 (Lon, 2026-09-21, in-chat: "So let's take the default GC arena down to 128 KB.") changed the
compiled-in default (`GC_HEAP_KB` in `src/runtime/rt/gc_heap.c`) to 128 KB and made it, by design, the
exasperating value.** Measured directly from source (`gc_heap.c:191`): `SCRIP_HEAP_MB=1` sets `kb = 1024`,
so a 1 MB pin is now **8x LOOSER** than the compiled default and collects **13x LESS** (buildinfo's own
citation: 1613 collections at 1 MB against 21362 at 128 KB, on `bench_icnstr_concat_table.icn`). A pin that
used to mean "tiny" now means close to the opposite.

This gate's own "control" arm (`unset SCRIP_HEAP_MB SCRIP_GC_STRESS`) therefore silently became the
exasperating arm post-CEO-1095, while "arena"/"stress:N" (explicit `SCRIP_HEAP_MB=1`) became the looser one
— roles swapped underneath the script with no line of evidence anywhere, purely because a shared compiled
default moved. This is the exact "one axis reads green over the whole class" trap this row's own ledger has
hit three times already (arena-vs-stress, band-vs-point, window-vs-poll-set), now recurring one level up: an
UNPINNED default is not immune to drifting out from under a script that assumed a fixed relationship to it.

## THE FIX (landed, same session, this row)

`test_gate_pl_master_is_clean_at_the_tiny_arena.sh` now:
- **"control"** is an EXPLICIT loose pin, `SCRIP_HEAP_MB=512` (renamed `CONTROL_MB`, matching the value the
  gate's own DECIDABILITY probe loop already assumed for it, which was itself inconsistent with the old
  `unset` control before this fix — a latent bug this correction also resolves).
- **"arena" / "stress:N"** now leave `SCRIP_HEAP_MB`/`SCRIP_HEAP_KB` UNSET ON PURPOSE, so they always track
  WHATEVER Lon's current tiny-arena default is, with zero maintenance owed here when it moves again — the
  same `?=`-over-`:=` reasoning the Makefile already uses for `SCRIP_HEAP_KB_TINY`.
- `collect_probe()` updated to support the unset/compiled-default case instead of always forcing an explicit
  MB value, so the DECIDABILITY positive-control probe now measures the SAME configuration `run_arm` actually
  uses (previously the probe hardcoded `_mb=512` for control while the real control arm ran fully unset —
  those only agreed by coincidence when the compiled default happened to be 512-ish; post-CEO-1095 they
  would have silently disagreed).

**Verified manually before the full re-run** (quick probes, not the full gate): compiled default + stress=1
→ 8001 `[GC-WALK]` collections; `SCRIP_HEAP_MB=512` + stress=0 → 0 collections; compiled default alone at
stress=0 → 571 collections (vs. the old 1 MB arena's prior measurement of only 4/23 benchmark kernels ever
collecting at all — the corrected arena arm is now genuinely engaged, not merely nominal).

## WHY THIS DID NOT INVALIDATE THE PRIOR (RETIRED) READING

The row's actual gating defect — the exception-ball unrooted-across-collection class — was found and cured
via the **stress axis** (`SCRIP_GC_STRESS`), which forces collection **orthogonal to window size**
(`gc_heap.c` `c_rt_gcheap_alloc` reads the stress counter independent of the committed window). The prior
1 MB pin did not invalidate that finding or its cure's verification (SCRIP `5fc6ae1bc`, 0/216 divergent,
closed 2026-09-21) — arena-insensitivity for that class was independently measured (identical failure at
1 MB and 512 MB). What the stale pin DOES affect is any conclusion this gate's ARENA axis specifically (not
its stress axis) was drawing about "the tiny arena" — that axis was, until this fix, measuring the corpus at
a now-loose window, not the collector at the mandated tiny one.

## STATUS

Fix landed in `scripts/test_gate_pl_master_is_clean_at_the_tiny_arena.sh` on tree SCRIP `56504708a` (pre-fix)
/ rebuilt post-fix, this session. Full 6-arm re-measurement (control, arena, stress:{2,5,16,25}) launched in
background to confirm Prolog's GC share is clean at the NOW-correct tiny arena definition; result to be
folded into the row's baton `## LEDGER` and `## NEXT` in the same landing per findings/README.md.

⭐ **General form, worth another seat's five minutes**: any gate that pins an arena value CHOSEN to sit in a
known relationship to a compiled-in default (tighter/looser, above/below) has a hidden dependency on that
default staying still. When the default itself is the thing under active tightening (CEO-931 → CEO-1095, and
presumably not the last word), an explicit numeric pin is the one thing guaranteed to eventually mean the
opposite of what it meant when written. Track the LAW ("the tiny arena"), never the NUMBER, wherever a script
can express that as unset-tracks-the-default instead of a literal.
