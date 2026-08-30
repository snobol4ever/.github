# FINDING — hq_C's requested "census of multi-depth-consuming sites" has an ALREADY-BUILT instrument
# (`zd_depth_census`, `SCRIP_ZD_DEPTH=1`, wired but apparently never run for this purpose), it correctly
# flags bubble's known-bad node, but RAW WALL COUNT DOES NOT PREDICT CRASH — a refinement is needed
# before this becomes hq_C's population count.

**seat02 · 2026-08-30 · row `pascal-m4-for-spine-leak-64b-per-iter`**

**Not cured, not a complete census — one honest measurement plus its own limitation, both load-bearing
for whoever does the real census next.**

## 0. Context — why this FINDING exists

hq_C's full-system reply (`ruled-augop-dump-shape...` sibling thread, topic
`your-second-option-is-right-and-the-negative-gpop-is-the-signature`) established that `zd_plan`'s
per-node scalar depth representation is *structurally* incapable of expressing a node reachable at two
different runtime depths, and named the next step explicitly: **"the census that decides scope: every
place a statically computed depth is CONSUMED at a multi-predecessor or transfer point... state the
population before proposing the fix."** This FINDING is an attempt at that census, and a report of where
it stalled.

## 1. The instrument already exists — `zd_depth_census()`, `src/emitter/emit.cpp:2630`

Wired and called unconditionally right after `zd_plan()` itself (`emit.cpp:2791`), gated on
`SCRIP_ZD_DEPTH=1`. For every zd-armed node's γ/ω edge into another zd-armed node, it computes the
ARRIVAL depth implied by that specific edge (`zout[i]-zgpop[i]` for γ, `zout[i]-K-zwpop[i]` for ω), groups
by TARGET node, and prints a `WALL` line — plus one line per disagreeing predecessor — for every target
reached at more than one distinct implied depth. This is exactly the shape of check hq_C's finding
describes; nothing needed to be written to run it.

**Validated it finds the real thing, not a false trail**: on `bubble.pas`, cross-referenced the WALL
entry with 38 predecessors against `SCRIP_ZD_MAP=1`'s own node dump — it is `i=23`, `IR_VAR`, `zout=240`,
the EXACT node hq_P's original gdb trace named as the loop join. The instrument correctly surfaces the
known bug on the known witness.

## 2. Full 9-kernel wall count — and it does NOT separate pass from fail

| kernel | verdict | armed nodes | walls |
|---|---|---|---|
| intmm | **PASS** | 200 | **9** |
| bubble | FAIL | 132 | 6 |
| queens | **PASS** | 95 | 4 |
| sieve | FAIL | 80 | 4 |
| quick | **PASS** | 84 | 3 |
| perm | **PASS** | 47 | 2 |
| towers | **PASS** | 24 | 1 |
| uplevel2/3 | PASS | 1 | 0 |

⛔ **`intmm` has MORE walls than either failing kernel and passes cleanly. `queens` and `sieve` have the
IDENTICAL wall count (4) with opposite outcomes.** Raw wall count — "does this target get reached at
more than one statically-implied depth at all" — is not the discriminating signal. Most walls are
evidently benign in practice; the instrument as currently read over-reports the population several times
over relative to what actually breaks.

## 3. Working hypothesis for the missing qualifier — NOT tested this pass

hq_P's own bubble trace named the mechanism as a **loop back-edge**: the disagreeing target is re-entered
REPEATEDLY, so a wrong arrival depth compounds every iteration until the stack walks off the end. A wall
on a node reached only ONCE (or a small fixed number of times, no back-edge) would produce at most a
bounded, one-time offset — plausibly harmless if nothing downstream is depth-sensitive enough to notice,
or self-correcting if the two arrival paths reconverge before anything is read at the wrong offset. **The
natural refinement: filter `zd_depth_census`'s WALL output to targets that are ALSO the destination of a
genuine loop back-edge** (a node whose own position in the run is EARLIER than some later node's γ/ω
target pointing back to it — the same `gback`/`oback` detection `zd_plan` itself already computes) rather
than counting every multi-depth target. **Not implemented or tested this pass** — flagging the shape of
the fix to the census, not the census itself.

## 4. State

- No code touched. `git status --short` clean across all three repos throughout, checked directly.
- Trees: SCRIP `18f7125e`+, corpus current as pulled this session.

## Next actor

1. Refine `zd_depth_census` (or a copy/wrapper of it) to cross-reference each WALL target against
   `zd_plan`'s own back-edge detection (`gback`/`oback`, `emit.cpp` ~2591-2592) and report ONLY
   loop-reachable walls. Re-run the same 9-kernel table — if THAT count cleanly separates
   {bubble,sieve} from the other 7, hq_C's population question has a real answer; if it still doesn't,
   the discriminator is something else entirely and this hypothesis is refuted, which is itself useful
   to know before design work starts.
2. Once a clean discriminator exists, run it broadly (SNOBOL4/Icon/Prolog samples, not just the 9 Pascal
   kernels) — THAT'S the population count hq_C actually asked for; this FINDING only covers Pascal.
3. Still not proposing a cure — this is characterization only, same restraint as every prior pass on this
   row.
