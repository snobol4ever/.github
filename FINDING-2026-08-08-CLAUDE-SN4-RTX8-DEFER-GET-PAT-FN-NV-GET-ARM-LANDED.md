# FINDING-2026-08-08-CLAUDE-SN4-RTX8-DEFER-GET-PAT-FN-NV-GET-ARM-LANDED.md

## Summary

`rt_defer_get_pat_fn` NV_GET hot arm ported to asm in `rtx_match.S`. 5,500,011 COMMITS / 0 bails on `pattern_bt` (N=500K). Gate PASS both modes N=4. Watermark holds exactly. SCRIP `8ecb5cd7`.

## Step-0 Six-Check (ARCH §7)

**(a) Live definition:** `T rt_defer_get_pat_fn` confirmed in `nm -D out/libscrip_rt.so`. ✅

**(b) Spelling round-trips byte-identically:** `rt_defer_get_pat_fn` — verified against tree. ✅

**(c) Linkage (run on `/tmp/pm_check.o`, NOT the `.so`):**
| symbol | object-file type | asm treatment |
|---|---|---|
| `NV_GET_fn` | `U` external | `@GOTPCREL` call via r10 |
| `dtp_fn_of` | `T` exported (same TU) | `@GOTPCREL` tail call via r10 |
| `g_spk` / `g_spk_n` / `g_spk_cap` | `b` static | unreferenceable → bail arm |
| `rt_cas_carve` | `t` static | unreferenceable → bail arm |

**(d) Executes in the timed window:** 5,500,011 entries at N=500K; 11,011 at N=1K; 22,011 at N=2K — **exactly 2.00× scaling.** ✅

**(e) Not already asm:** `grep 'RTX_FUNC(rt_defer_get_pat_fn)' src/runtime/rtx/rtx_match.S` → 0 hits before this commit. ✅

**(f) Arm check (pre-port source read + post-port census):**
- `pattern_bt` exercises `.W` conditional assignment — `varname` has no leading `*` — **NV_GET arm only.**
- Post-port census: COMMITS=5,500,011 / BAILED_C=0. Arm that runs is the arm that was ported. ✅

## Arm Map

**BAIL arm (star-var, cold):** `varname[0]=='*'` → touches static `g_spk`/`g_spk_n`/`g_spk_cap`/`rt_cas_carve` — unreferenceable from `.S` without static promotion. Bails immediately to `c_rt_defer_get_pat_fn`. Bail-before-mutate: nothing above `.Ldfpf_mutate` writes memory.

**HOT arm (NV_GET):** `NV_GET_fn(varname ?: "")` → if `val.v==DT_P && val.p` → `dtp_fn_of(val.p)` (tail call). `ival_flag` dead on the emitted path (template always passes `xor esi,esi`). `IS_NAMEVAL`/`IS_NAMEPTR`/`NAME_DEREF_PTR` are pure macros — no extra calls.

## Scope

ERADICATION slice (RTX-12). No speed number claimed — the s224 rail refuses every window on this machine (hugepage bimodality). Saving: one -O0 frame per call on 5.5M calls/run, below the ±3% null floor even if the rail worked. Grade on correctness and C deleted.

## Phantoms Struck This Session

`rt_cap_assign_cursor` — not in `nm -D out/libscrip_rt.so`. Phantom, eliminated from ladder consideration.
`rt_defer_match` — not in `nm -D out/libscrip_rt.so`. Phantom, eliminated.

## Ungradeable on Current Corpus (step-0(d) zero)

`rt_match_value_get_pat_fn`, `rt_match_value_open`, `rt_scan_splice_empty`, `rt_dcap_flush`, `rt_dcap_end_ok`, `rt_cap_push`, `rt_cap_open`, `rt_cap_finish`, `rt_match_capture`, `rt_defer_step` — all measured zero on `pattern_bt` and `json.sno` (stdin-dependent, no `.input`). Not portworthy without a workload that reaches them.

## Gates

- Kill-switch: `test_gate_rtx_killswitch_sets.sh match` → m3 IDENTICAL=154 QUARANTINE=1 MOVER=0 · m4 IDENTICAL=148 QUARANTINE=2 MOVER=0 SKIP=5. GATE PASS. Quarantine set (`053`, `056`) is pre-existing non-determinism.
- Full crosscheck: m3 **260/57/0** · m4 **243/73/1 SKIP** · DIVERGE **16** — watermark holds exactly. Zero regression.

## SCRIP Commit

`8ecb5cd7` — `RTX-8 DEFER-GET-PAT-FN: NV_GET hot arm ported to asm`

Changed files: `src/runtime/rtx/rtx_match.S` (+75 lines) · `src/runtime/pattern_match.c` (rename only) · `src/runtime/rt/rt.h` (+2 decls)
