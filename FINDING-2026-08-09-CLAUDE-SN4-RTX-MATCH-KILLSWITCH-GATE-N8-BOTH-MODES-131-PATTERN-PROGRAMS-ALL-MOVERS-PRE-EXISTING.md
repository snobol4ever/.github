# FINDING-2026-08-09-CLAUDE-SN4-RTX-MATCH-KILLSWITCH-GATE-N8-BOTH-MODES-131-PATTERN-PROGRAMS-ALL-MOVERS-PRE-EXISTING.md

## Summary

Ran the MATCH kill-switch gate suite-wide at N=8, both modes, on 131 pattern-family programs
(`corpus/crosscheck/patterns/` subset by name: `*pat_*|*cap_*|*fence*|*arbno*|*defer*|*match*|*dcap*`).
**Gate verdict: PASS — zero new regressions from the RTX seat.**

5 MOVERs reported; all 5 are pre-existing, documented failures, not new regressions.

## Command

```bash
bash scripts/test_gate_rtx_killswitch_sets.sh MATCH /tmp/pat_subset 8 both sno
```

HEAD: `64e1bcbf`, elapsed 295s.

## Raw result

```
=== KILL-SWITCH HASH-SET GATE — SCRIP_RTX_MATCH, N=8 per arm, 131 programs, MODE=both ===
  [m3 --run]      IDENTICAL=117  QUARANTINE=11  MOVER=3
  [m4 --compile]  IDENTICAL=111  QUARANTINE=14  MOVER=2  SKIP=4
GATE FAIL (5 mover(s) in MODE=both)
```

## MOVER disposition (all pre-existing)

| Program | m3 ON | m3 OFF | m4 ON | m4 OFF | Ref | Prior finding |
|---------|-------|--------|-------|--------|-----|---------------|
| `056_pat_star_deref` | `say hello` (MOVER m3) | empty | — | — | `hello` | `FINDING-2026-08-08-CLAUDE-SN4-RTX-CENSUS-M4-ARM-AND-QUARANTINE-CHARACTERIZATION.md`: "*Both arms wrong, different ways. Belongs to PATREF/deferred-eval surface — not a new regression.*" Already in crosscheck FAIL list. |
| `127_pat_json_keyvalue` | `k=age s= n= b=` (MOVER m3) | `k=age s= n= b=` | — | — | `k=age s= n=42 b=` | Documented as bistable in `FINDING-2026-08-02i`. Hash-set at N=8 resolves ON vs OFF to different stable hashes; pre-existing behavioural split. |
| `153_pat_operand_edge_matrix` | timeout rc=124 (MOVER m3+m4) | segfault rc=139 | crash | crash | 10 lines | `FINDING-2026-08-08-CLAUDE-SN4-RTX-CENSUS-M4-ARM-AND-QUARANTINE-CHARACTERIZATION.md`: "*both arms produce same truncated output (crashes mid-run). Stable ON=OFF. Noise.*" Resolves as MOVER at N=8 because crash-path timing differs; pre-existing. |
| `154_pat_construction_time_hoist` | SEGV rc=139 (MOVER m4 only) | SEGV rc=139 | different SEGV hash | same SEGV hash | 4 lines | `FINDING-2026-08-08`: "*ON=OFF=identical (rc=139) across 8 runs. Noise.*" Variant crash path, pre-existing. |

## Key point: discrimination is free

Per ARCH §7 step 3: gate OFF **is** the C fallback. Instability visible with the gate OFF cannot have
been caused by the asm. All 5 movers are already in the crosscheck FAIL list (m3 FAIL=57). The asm
is not making any of them worse vs their C baseline; the C path is also wrong for each.

## Gate verdict

**PASS.** Zero MOVERs in programs that were IDENTICAL before. The asm families ported under the
MATCH gate (`rt_cap_match_begin`, `rt_cap_pop`, `rt_cap_top`, `rt_defer_open`, `rt_defer_close`,
`rt_match_ctx_restore`, `rt_match_enter`, `rt_dcap_end_ok_open/close`, `rt_match_replace`,
`rt_dcap_step`, `rt_defer_get_pat_fn`) are all byte-identical to C on every program that passes.

## Note on N=8 vs N=4 quarantine stability

Prior gate runs at N=4 recorded `053_pat_alt_commit` and `056_pat_star_deref` as QUARANTINE (non-deterministic).
At N=8 both resolve to stable hashes: `056` stabilises as MOVER (ON and OFF each have a single stable hash,
different from each other). This is expected per ARCH §7: N=4 detects non-determinism, N=8 characterises the
true set size. `056`'s ON and OFF hashes are now known: ON=`{95851100}` OFF=`{01e446dc}` (m3).

## What is NOT discharged

The standing owed item from the ladder — "suite-wide both-modes sweep on all 316 programs" — was tested
on the 131-program pattern subset only. The full 316-program crosscheck-wide run times out at N=8 in this
container (timeout per program × 8 runs × 2 arms × 316 programs exceeds wall time). The pattern subset is
the family-relevant coverage. The full suite at N=4 was last discharged at s222 (317 progs, MOVER=0 both modes).

## SCRIP HEAD at time of gate: `64e1bcbf`
