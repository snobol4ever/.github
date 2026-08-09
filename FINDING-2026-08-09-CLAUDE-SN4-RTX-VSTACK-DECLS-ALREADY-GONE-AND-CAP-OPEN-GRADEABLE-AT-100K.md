# FINDING — 2026-08-09 — SN4-RTX: the vstack declarations are already gone tree-wide, and rt_cap_open is now gradeable at 100K entries

**Session:** Claude (Fable), 2026-08-09. SCRIP HEAD `64e1bcbf`. Watermark re-proved this session: m3 260/57/0 · m4 222/66/29 SKIP · DIVERGE 14.

**⚠ CONCURRENCY COLLISION, RESOLVED BY THIS (REBASING) SESSION PER PROTOCOL:** a parallel RTX seat landed `.github f9e341a8` mid-session with the SAME Finding-1 discovery plus more — they named the deleting commit (`1b251a7d`), attempted deleting the 83 rt.h phantoms, REVERTED it unproven, and disputed this session's m3 watermark (claim: 260/57/0 is a stale-build artifact; 259/58/0 true; mover `161_pat_defer_fn_nested_match`). **This session spot-checked 161 on its own build immediately after the collision surfaced: FAIL.** That corroborates 259/58/0 — this session's earlier 260 caught 161 in a passing state (stale build or run-to-run instability; one run cannot distinguish, and 161 is a deferred-eval-family program, the class with known flake cousins). Finding 1 below stands as INDEPENDENT CONFIRMATION of their result, arrived at blind; `f9e341a8` has first-lander credit and the ladder strike. Finding 2 (the workload mint) is this session's alone and does not collide.

## Finding 1 — RTX-10's "delete the dead declarations" half is ALREADY DONE, by a concurrent seat, and the rung text still owed it

The rung read: "Remaining work on this rung is the live MISC/IO surface **plus deleting the dead declarations**" (the `rt_push_*`/`rt_pop_*`/`rt_halt_tos` set the s204 audit proved declaration-only). Measured this session:

```
grep -rn "rt_push_\|rt_pop_\|rt_halt_tos" src/ --include=*.c --include=*.h --include=*.cpp --include=*.S   → 0 hits
nm -D out/libscrip_rt.so | grep -c "rt_push_\|rt_pop_\|rt_halt_tos"                                        → 0
```

The 30 phantom `rt_pat_*` declarations (RTX-9's hazard, formerly `rt/rt.h:38-67`) are ALSO gone — the only surviving `rt_pat_` spelling in `rt.h` is `rt_pat_prim_int` (line 170), which is the LIVE D08-FIX symbol (`e3ef8f7d`), not a phantom.

**This is the RTX-6 phantom-rung shape again — planned work already done — caught this time by a two-minute grep before any session was spent.** A rung's premise decays when an unrelated rung succeeds; the deletion was presumably swept up by DEAD-CODE SWEEP or a runtime reorg seat. The rung text is struck in the same commit as this FINDING per ARCH §7 step 0's clause.

## Finding 2 — cap_imm_nret.sno mints rt_cap_open OUT of the ungradeable set: 100,001 entries, exact 2.00× scaling

The cursor's ungradeable list (step-0(d) zero on `pattern_bt` + `json.sno`) included `rt_cap_open` and `rt_cap_finish`. Read the C (`pattern_match.c:787`): `rt_cap_open` is the immediate (`$`) capture path plus the computed-name (`. *proc()`) transfer; `rt_cap_finish` completes only the computed-name (fbytes) branch.

Minted `corpus/benchmarks/snobol4/cap_imm_nret.sno` (corpus `b70e218a`): 100K-iteration loop over `LEN(3) $ V 'X'` (immediate) and `LEN(3) . *STORE() 'X'` (NRETURN computed-name), deterministic output, no TIME(), oracle `.ref` from SPITBOL x64, scrip m3 output byte-identical to ref.

Census (`util_rtx_count_syms.sh`):

| symbol | entries @N=100K | @N=200K | verdict |
|---|---|---|---|
| `rt_cap_open` | **100,001** | **200,001** | **GRADEABLE — exact 2.00×, +1 constant preserved** |
| `rt_cap_finish` | 0 | — | still ungradeable in m3 (see below) |
| `rt_dcap_flush` / `rt_dcap_end_ok` / `rt_match_value_open` | 0 | — | still ungradeable on this workload |

**The asymmetry is itself a measurement:** the `*STORE()` computed-name capture produced the CORRECT answer (`slot: abc`) while `rt_cap_open`'s entry count shows only the immediate arm's 100,001 — i.e. exactly one entry per `$` per iteration and ZERO from the `. *STORE()` clause. The m3 emitter routes the computed-name conditional capture through some path other than the `rt_cap_open` fbytes branch (plausibly the NCB-1b emitted capture box / rbp-dcap inline arm the C comment describes). ⇒ `rt_cap_finish` cannot be minted gradeable from SNOBOL4 source alone until someone establishes which emitted arm, if any, still calls it — its port priority should be re-derived from that answer, not from this null.

⚠ Caveats carried forward: (a) counts are m3-only — `util_rtx_count_syms.sh` has no m4 arm (the arm-census tool got one at `2d687dab`; this tool did not); (b) an entry count cannot name an arm — before any `rt_cap_open` port, run the interposer arm census on THIS workload to size the immediate-arm fraction (expected ~100%, but measure it).

## Cost
One session fraction. Two greps killed a dead half-rung; one 24-line .sno moved one symbol from unfalsifiable to gradeable.
