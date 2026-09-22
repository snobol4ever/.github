# FINDING 2026-09-22 hq_snocone — commit `c6009782862886bd35d89b71648b4460f96e03cb` corrupts output under forced collection, bisected to four shared templates

**Context:** ceo-1129/1130 DECTET ask, component 4 of the GC acceptance bar (WORKING — does the collector produce right answers, not merely avoid crashing). Rebuilt incrementally at SCRIP `156ef964d`, re-ran the Snocone master (clean: `SUITE_BOARD family=ALL total=336 shipped=336 m3_pass=336 m4_pass=336`, unforced) and this lane's own forced-collection gate (`test_gate_snocone_gc_share_named_and_master_clean_under_forced_collection.sh`, band `1 3 5 8 16` × arena `{1MB,shipped}` × m3/m4). That gate read fully clean (zero divergent pairs) at SCRIP `77922bcf8` two sittings ago — full receipt in `tasks/snocone-gc-zero-gradings-lost-to-the-collector-across-the-arena-and-stress-axes-named-not-counted.task.md`. On `156ef964d` it is RED.

## The symptom

One entry, `arb_span_break_replace_1` (origin `pattern_suite__pattern_suite`, a 112-line ARB/SPAN/BREAK/ANY/LEN pattern-match suite exercising conditional-assignment captures, e.g. `s ? (ANY('hxz') . v)`), prints **garbled binary bytes** in place of several `OUTPUT` lines under `SCRIP_GC_STRESS=1`, at both arena sizes. Not a crash (rc=0 throughout), not a clean wrong value — corrupted payload bytes. Named in the gate's NAME-SET at every stress point tested (1, 3, 5, 8, 16): m3+m4 both fail at stress 1/3/5, m4-only at 8/16. Which output lines corrupt is stress-dependent, not fixed — consistent with a collection landing on a live-but-unrooted value rather than a fixed lexical defect.

Isolated standalone with `corpus_suite_harness.py extract --origin pattern_suite__pattern_suite`, reproduces directly:

```
SCRIP_GC_STRESS=1 SCRIP_HEAP_MB=1 ./scrip witness.sc < /dev/null
```

diverges from the SPITBOL-oracle `.ref` starting right after `ANY-2 FAIL expected` — `ANY-3`, `LEN-1`, `LEN-2` corrupted, `LEN-3`/`LEN-4` clean, then `COMBO-1`..`COMBO-4` corrupted again.

## The bisection

`git bisect start 156ef964d 77922bcf8`, test = rebuild (`make`, incremental) + diff the extracted witness's `SCRIP_GC_STRESS=1 SCRIP_HEAP_MB=1` output against its oracle `.ref`. 7 steps.

**First bad commit: `c6009782862886bd35d89b71648b4460f96e03cb`** — "gc safe points: four DESCR-returning sites take a bare poll after their store -- 152 of 253 to 156, cleared on identical name sets". Parent `e42cc0909867eb873409a87a9b38c31f710a1060` is clean on this witness.

The commit adds `x86_rt_gc_poll()` immediately after the descriptor store, in four templates:

| template | site | commit's own note |
|---|---|---|
| `bb_var_ref.cpp:70` | after `if`/`else` writes ZRES or FRQ | shared node, named as such in the commit message |
| `bb_deref.cpp:19` | ZRES arm, after the ZRES pair is stored | shared node |
| `bb_unop.cpp:46` | after both halves land in FRQ | shared node |
| `bb_binop_concat_slot.cpp:64` | after ZRES pair, **deliberately before `rtcc_rl`** | not called shared in the message, but reached by every frontend's `&&`/concat lowering |

The commit's own message states: *"bb_deref, bb_unop and bb_var_ref are SHARED nodes, so the other frontends' arms are OWED: batch open since `e42cc0909`."* That owed cross-frontend verification is exactly what this finding is — it never happened until this sitting, 90 commits and roughly 11 hours after landing.

## What is and isn't established

- **Established:** this exact commit is causal (bisection is deterministic given the same witness and build). The four sites it touches are shared across every frontend that lowers to `IR_VAR_REF`, `IR_DEREF`, `IR_UNOP`, or `BINOP_LCONCAT`.
- **Not established — this lane does not touch `src/templates`:** which of the four sites is actually wrong, or whether the defect is (a) poll placement relative to `rtcc_rl`/register-cache reload (the commit's own stated concern for `bb_binop_concat_slot`, called out as deliberate), or (b) the compile-time frame map at that program point not yet describing the ZRES/FRQ slot as a live descriptor (which would matter under the frame-map-only collector per `ARCH-GC-COMPILE-TIME-FRAME-MAPS.md` § 7 FROZEN, CEO-812). My witness's corrupted lines all use `&&` concatenation (`'ANY-3 c=' && c`), so `bb_binop_concat_slot.cpp` is the prime suspect for THIS witness, but that is not proof the other three sites are innocent — not tested in isolation.
- **Not checked:** Icon or Raku populations (SNOBOL4 and Snocone share `lower_snobol4.c` and were the closest-to-hand comparison; Icon/Raku lower through different paths but reach the same shared templates for these IR kinds).

## Overlap

`hq_snobol4` claimed a row this same window, `snobol4-the-pattern-replacement-class-prints-a-wrong-answer-under-collection-and-changes-its-fingerprint-per-poll-set` — title strongly suggests the same root cause reached independently from the SNOBOL4 side. Told them directly with this measurement rather than let two lanes re-isolate the same defect. ASK sent to the cfo (reviewer map: icon/snobol4/snocone/pascal) with the same evidence; no cure landed by this lane — shared templates are outside lane scope by this project's own rule.

## Raw evidence

Witness `.sc`/`.ref`, full bisect transcript, and both the unforced-master and forced-collection-gate raw logs are session-scratchpad artifacts (not committed — copy before any sweep, per this project's own standing warning about session-local logs).
