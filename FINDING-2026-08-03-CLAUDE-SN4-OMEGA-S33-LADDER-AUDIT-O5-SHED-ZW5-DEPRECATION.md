# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-S33-LADDER-AUDIT-O5-SHED-ZW5-DEPRECATION

**Session:** s33 (2026-08-03, Sonnet)
**SCRIP parent:** `7ba079e8` (ZW-13 s32, no code commits this session — audit only)

## Summary

Full ladder audit against HEAD. No code was written. All findings are MEASURED against the live tree, not inferred from documentation.

## O-5 ZW-3 R12-CAS-LIVE — state is further advanced than the cursor indicates

All three seeding sites are landed:
- Mode-4 wrapper seeds: `scrip.c` lines ~1242 and ~1439 each emit `mov r12, qword ptr [0x70000000]` before graph entry. **LANDED.**
- Mode-3 `rt_outer_call` thunk (`src/runtime/rt/rt.c`): `push r12 / mov r12,[0x70000000] / call / pop r12`. **LANDED.**

O-5s2 (remove redundant r12 reload in `bb_match_begin` op_zw arm) is **LANDED** (s29).

All 6 emission sites in `bb_match_capture.cpp` are **already split by `_.op_zw`**: the canonical-frame arm writes directly to `[r12+0/8/16]` and bumps r12; the legacy arm loads from `ABSQ(RT_CAS_TOP)` through r10. No template edits needed.

**Remaining for O-5 (genuine):**
1. `rtx_match.S` `rt_match_enter` still runs `g_patstk_sp` lazy-init unconditionally. For the 23 armed programs this is 3 cold-path instructions (GOT load + cmp + branch-not-taken). Cost negligible; removal requires either a runtime flag or a two-variant `rt_match_enter`. Deferred.
2. STACKLETS audit (written here): `rt_zcol_push` (`pattern_match.c:1309`) is the ARBNO per-iteration collection store. It operates on malloc/arena memory with no interaction with `g_dcap_top`/`RT_CAS_TOP`/r12. The ARBNO template (`bb_match_arbno.cpp`) does not use r12 or `op_zw`. ARBNO is excluded from the canonical frame arm by the seal gate. **r12 wiring is SAFE: zero interaction with the ARBNO stacklets axis.**
3. cap_gen deletion from `rt_match_enter` fast path: deferred, separate commit, needs proven r12 wiring corpus-wide first.

**Verdict: O-5 is `[~]` — the critical wiring is done; the cleanup (patstk cold path, cap_gen) is deferred.**

## O-6 ZW-6 GLUE-O — slice 2 (default flip) is CONFIRMED DONE

`emit.cpp:2261`: `_gluo = (e && *e == '0') ? 0 : 1` — default is 1 (ON). The s29 ladder audit confirmed this; re-measured s33. O-6 is `[~]` with the CLASS O population handled; CLASS C/PAT$N/FENCE0/FENCE1 relocation remains (per the ledger, CLASS C KEEPS its whack by ledgered decision; the others require ZW-2 population growth).

## O-8 RBP-SHED — census against HEAD

- **SHED-3** (stale-emission globals → per-graph `g_emit` mirror): `g_emit.flat_outer_nparams` is already in the struct (emit.h:620, comment "SHED-3 (s25a)") and copied at emit_chain choke (emit.cpp:2843). **DONE.**
- **SHED-1** (retire `g_flat_outer_nparams>=1` pin conjunct): `emit_jmp_pin_rbp()` does NOT use `flat_outer_nparams` — it gates only on `flat_deep_arrival || flat_pat || flat_gen`. The `flat_outer_nparams == 0` conjunct appears only in the GLUEO and STMT-FRAME guards, where it's correctly a SCOPE conjunct (not a pin). **DONE (was already correct at HEAD).**
- **SHED-2** (ABORT → statement fail exit): `bb_match_abort.cpp` is `x86_alpha() + x86_omega() + x86_beta_trampoline()`. Under STF (the current ruling design for fail-edge routing via `mov rsp,rbp`), ABORT already exits through `x86_omega()` which routes to the chain's fail label. The depth-independent cut from the STF bracket (`ZGPOP-STF`: `mov rsp,rbp` normalizes rsp regardless of arrival depth) is the correct mechanism per `FINDING-2026-08-02h`. SHED-2's per-depth stub ladder is SUPERSEDED — ZW-5 O-2 is DEFAULT OFF (see below). ABORT's current `x86_omega()` routing is CORRECT under the STF discipline. **DONE (design changed; no edit needed).**
- **SHED-4** (scanhit/scanfail hooks through x86()): `bb_match_begin.cpp` legacy arm's gate-1 fail exit uses `x86(...)` throughout. `x86_align_enter/leave` are NO-OPS under `ZC_FRAME_RSP` (the default) — `x86_align_enter()` returns empty string when `x86_zc_frame() == ZC_FRAME_RSP`. **DONE for the main path.**
- **SHED-5** (retire transient push-rbp alignment window): Same conclusion as SHED-4. `x86_align_enter()` is a no-op under `ZC_FRAME_RSP`. **DONE.**

**Measured rbp census at s33 HEAD:** 166 rbp-bearing programs / 310 push_rbp occurrences / 23 armed (canonical frame). s32 watermark: 132 bearing / 283 push_rbp. The discrepancy (166 vs 132) is harness-scope: our census includes test/snobol4/** .s artifacts not in the s32 crosscheck scope.

## ZW-5 O-2 DEPRECATION (critical design change)

`emit.cpp:2215` comment: "DEFAULT OFF (Lon 2026-08-02, observer seat): per-depth ω stub ladder DEPRECATED — 100 stubs/roman, and its wpop-steal wedged 067 post-output (rsp mispositioned into NV_SET, stdio wedge; SCRIP_ZW5=0 cures, ZD_MATCH exonerated). The ruled design is the STF rbp bracket... extended to the armed-pattern population this ladder covered."

**Implication for SHED-2 and the ladder:** The per-depth ω stub ladder (O-2's core mechanism) is deprecated. The STF rbp bracket (`mov rsp,rbp` = depth-independent cut, zero hand-counted pops) is the ruling design. O-1/O-2 are marked done but the O-2 mechanism has been superseded. The armed-pattern population (the 23 programs) uses the ZW canonical frame for match constructs; the STF bracket handles ordinary statement fails.

## O-4 REMAINING — deferral is correct

The `op_zw` arm already omits `rsp_mark`/`patstk_mark` entirely. The legacy `!op_zw` arm's readers are live for 144 programs NOT yet armed. Full deletion of `g_patstk_sp` must wait until the armed population covers those programs (ZW-1/ZW-2 full flip). O-4 is correctly `[~]`.

## BENCH HARNESS

Bench refs do not include `ms:` timing lines. Correct comparison: `| grep -v '^ms:'`. Measured s33: **18/21 EXACT HOLD** (eval_dynamic, eval_fixed, roman = pre-existing residue). Matches s32 watermark.

## NEXT STEPS

The cleanest next executable rung is **widening the canonical frame armed population** — either by relaxing the DEFER/PATREF seal (requires the nested-frame protocol design first) or by driving ZD admission further. ALPHA's A-9 reconciliation (per the O-9 rung) should precede closing both ladders.

**Immediate candidate:** O-4 cleanup of `g_patstk_sp` in `rtx_match.S` for the armed population via a fast-path flag (add a `g_zw_armed` process-scope flag set at first canonical-frame emission, skip `g_patstk_sp` lazy-init when set). This is measurable, bounded, and low-risk.
