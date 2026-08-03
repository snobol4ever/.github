# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-ZW13 — the canonical frame was dark since s24a and nblob==0 is the key

**Session:** s32 (2026-08-03, Sonnet). **Rung:** ZW-13 (blob clause restoration). **Commit:** SCRIP `96ddd335`.

---

## §1 THE DISCOVERY

Opening census at bracket (`a2cd7b09`, merged head after ALPHA A-5+s31 finding) showed that the three notes unique to the `op_zw` canonical-frame arm — `match_frame`, `cas_base`, `anchor_snapshot` — appear **zero times across all 318 crosscheck programs**, while 175/318 emit the legacy marker arm.

`SCRIP_ZWS_DIAG=1` across 318 programs returned zero `[ZWS]` lines. The instrument only printed on arm; zero arms produced zero lines and read as "no news."

## §2 ROOT CAUSE — git-bisected

`git log -S'nblob == 0'` → the predicate changed in ALPHA's **`bd08c7a3`** (s24a, "ZD-5b design + has_blob gate").

Before s24a, the `zws` planner line (emit.cpp, grep `RUNG ZW-12 verdict`) read:

```
zw_frame_on() && Kc > 0 && hpos >= 0 && nblob == 0 && !g_emit.flat_stmt_frame
```

That is ZW-12 clause (b) verbatim: "no PAT$ BLOB members."

After s24a, the substituted form:

```
zw_frame_on() && Kc > 0 && hpos >= 0 && !has_blob && !g_emit.flat_stmt_frame
```

`has_blob` is ALPHA's ZD-5b claim-span predicate (emit.cpp lines 2012–2013). It is set TRUE whenever a run holds ANY ordinary pattern element: LIT/LEN/ANY/NOTANY/SPAN/TAB/RTAB/POS/RPOS/REM/BREAK/BREAKX/ARB/BAL/ALTERNATE/SEQUENCE/ASSIGN_SAVE/ASSIGN_COND/ASSIGN_IMM. Every real match run holds at least one. So `!has_blob` is never true in practice, and `zws` has been permanently zero since s24a.

## §3 IMPACT ON PRIOR RUNGS

Rungs O-3 (s25a, ZW-1 canonical frame), O-4's ω twin (s25a, ZW-2 match_end frame-pop), O-5s2 (s29, r12 cas_base cell reload deletion), and O-7's `fence_whack_commit` fix (s30, `[rbp+0]` activation floor) all edited code that **never executes** at runtime. Their "BY SET IDENTICAL / zero regressions" gates were accurate because those rungs were no-ops on emitted output.

The diag's on-arm-only design is what hid it: a predicate that arms nothing prints nothing, which reads as "no programs qualified" rather than "the predicate is broken."

## §4 THE FIX

New gate function in `emit.h`:

```c
static inline int zw_nblob_ok(int nblob, int has_blob) {
    static int v = -1;
    if (v < 0) { const char *e = getenv("SCRIP_ZW_NBLOB"); v = (e && *e == '0') ? 0 : 1; }
    return v ? (nblob == 0) : (!has_blob);
}
```

Default ON (`v=1`): restores the documented `nblob == 0` clause.
Killswitch `SCRIP_ZW_NBLOB=0`: reverts to `!has_blob` (arms nothing — byte-identical to before).

`has_blob` at the Kc span consumer (emit.cpp:2013) is UNTOUCHED — one authority per kind.

Additional changes in emit.cpp:
- `zws` blob clause routes through `zw_nblob_ok(nblob, has_blob)`.
- Graph-scope DEFER/PATREF seal scan added (see §5).
- `SCRIP_ZWS_DIAG` now attributes DECLINE with failing conjunct (`why=blob-clause | killswitch | Kc<=0 | stf | seal/no-END/window`).

## §5 DEFER/PATREF SEAL

With the blob clause restored, 22 of the initial 23 armed programs pass both modes. The sole regression was `161_pat_defer_fn_nested_match`:

- **Run-scope DEFER seal** (scanning only run members) left 161 armed. Its `*P()` deferral lowers into a *sibling chain*, not the outer match run, so member scan sees no deferral.
- **Graph-scope DEFER/PATREF seal** (`for (_g = 0; _g < n; _g++)` over all graph nodes) correctly declines: the outer run's head now declines because any node in the same graph is `IR_MATCH_DEFER` / `IR_MATCH_PATREF`.

Law: graph-scope evidence driving a run-scope verdict is sound (the s21x-r law's reasoning: graph-scope flag→run-scope decision is the opposite of the s21x-r defect, which was a process-scope flag driving a graph-scope regime — the directionality matters).

DEFER/PATREF admission to the canonical frame is a separate future rung requiring the nested-frame re-entry protocol.

**Measured re-confirmation:** 161 with graph-scope seal:
- m3 = PASS (rc=139) — pre-existing post-output SEGV, harness-invisible (stdout matches ref before exit).
- m4 = FAIL — pre-existing at bracket, unchanged.
Both identical to baseline. ZW-13 introduces zero behavioral change in 161.

## §6 MEASUREMENTS

**Bracket** (merged head `a2cd7b09`): m3 282/24F/11T/1N · m4 275/30F/11T/1N/1L.

**Gate-ON arm** (before default flip): 23 programs arm (`match_frame` note 0→32 sites). All 23 PASS m3. 22 PASS m4 (161 pre-existing FAIL unchanged). Default arm: 0/318 `.s` differ — byte-identical.

**After default flip** (SCRIP `96ddd335`):
- m3 **282/24F/11T/1N** BY SET IDENTICAL to bracket.
- m4 **275/30F/11T/1N/1L** BY SET IDENTICAL to bracket.
- Bench **18/21 EXACT HOLD** (roman + eval_dynamic + eval_fixed = pre-existing).
- Regen ×4: 8 feature artifacts + 29 crosscheck artifacts changed (canonical frame emit for the 23 armed programs).

**Census at s32 close (default ON):**
- match_frame programs: **23/318**
- legacy marker programs: **156/318** (was 175; DEFER/PATREF declines shift some to sealed)
- push_rbp sites: **283** (was 252; +31 from the canonical frame's push rbp × ~23 programs × ~1-2 match runs each)
- fused-terminal proxy: **0** (unchanged)
- stmt_claim programs: **175** (unchanged — UCLAIM debt, ZD work)
- r12 sites: **317** (unchanged)

## §7 INSTRUMENT LAW (appended to the finding record)

The `SCRIP_ZWS_DIAG` pattern of printing only on success is the exact instrument gap that let this hide for 8 sessions. The lesson: a verdict-testing diag MUST attribute BOTH arm and decline; "no output" must mean "no programs were evaluated," not "no programs passed." Fixed in this commit for `ZWS`. The same pattern should be audited for `ZD-GAP`, `LP_DIAG`, and any other verdict instrument — if silence reads as "qualified but passing," it masks the predicate-always-failing class.

## §8 NEXT

- O-4 REMAINING: delete `rsp_mark`/`patstk_mark` reads + marker scans from the ZW-armed population (23 programs now confirmed clean under canonical frame). `g_patstk_sp` readers: begin ×4, end ×2 in template + rtx_match.S lazy-init. Gate: crosscheck BY SET + bench 18/21.
- O-5 ZW-3 R12-CAS-LIVE: the canonical frame cell `[rbp-32] = cas_base` is already being saved in bb_match_begin.cpp's op_zw arm (line 50 as confirmed); O-5s2 deleted the reload at match entry. The remaining r12 wiring (6 emitted sites + 2 m4 wrapper seeds + `rt_outer_call` thunk) can now be measured against an actually-armed population.
- ALPHA NOTIFICATION: ZW-13 finding implies that O-3/O-4/O-5s2/O-7 delivered correct code but into a dead arm. ALPHA's A-9 reconciliation cursor should be updated to reflect this before the O-9 RECONCILIATION rung closes both ladders.
