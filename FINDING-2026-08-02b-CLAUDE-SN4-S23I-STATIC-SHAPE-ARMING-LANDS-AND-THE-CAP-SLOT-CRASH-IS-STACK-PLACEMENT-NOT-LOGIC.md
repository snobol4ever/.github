# FINDING — ZD-5 static-shape DEFER/PATREF arming LANDS, and the blob cap-slot crash is STACK-PLACEMENT-DEPENDENT, not logic

**Session:** s23i (2026-08-02) · **Directive (Lon):** complete the NON-POPPING FORTH-style RSP ZETA stack, C-style RBP only when absolutely necessary; *"All your choices. I'm with you on this. Continue."*

**VERDICT:** the s23h-named next rung is LANDED. `pat_static` (new IR_t field, calloc-0 conservative) carries lower's TRANSITIVE DEFER-FREE proof over the `g_sno_seal` single-write table to zd_plan's dynamic-box scan: a DEFER/PATREF whose target provably cannot re-enter any blob no longer vetoes the statement quartet. **Armed population: 17 of 122 pattern programs** (fence-via-var 108–113, non-recursive star-vars, calc/regex/json-literal grammars, 117). FENCE1-in-statement still declines unconditionally. `SCRIP_ZD_DYNARM` is the measurement mask (=0 ≡ the s23h regime, proven byte-identical to committed HEAD artifacts; bits force-arm per kind for A/B).

## WATERMARK (crosscheck 318, TIMEOUT=8, setarch -R)

**m3 281/26/10 · m4 266/39/10/2L** vs record 280/27/10 · 266/39/10/2L. m4 EXACT BY SET incl. the LERR pair {test_string, 1017_arg_local}. m3 +1 = the LAWS-named 213_gc_exhaustion_churn harness flake on its pass side (absent from the non-pass set). Armed-17: m3/m4 verdicts agree pairwise; the 5 armed fails (070/072/074/180/181) are red→red at =0. **Zero attributable P→F.** Regen ×4: benchmark/feature/demo unchanged; crosscheck churned exactly the 17, 257+/326− (armed code is NET SMALLER), emit-fail 15, as-fail 2.

## MEASURED LAWS (chronological, each with a witness)

1. **The spine/argument VAR distinction is load-bearing:** in primitive-argument position (LEN(N)'s N) a VAR is a value read; in spine position it is a pattern name resolved through the seal table. Without it, every LEN(var) target classifies dynamic and the population is near-empty. TT_FNC conservative-0 (a build-time call can return a pattern carrying defers); unlisted kinds conservative-0; depth cap 48 breaks bare-name chase cycles.
2. **The recursive class declines byte-verbatim:** 135/136's `B = '(' FENCE(*B | eps) ')'` stamps 0, .s identical to HEAD. 142 (statement FENCE1) identical. Degrade never die, by construction not by luck.
3. ⭐⭐⭐ **THE CAP-SLOT BRACKET (core.3397, 127_pat_json_keyvalue):** armed 127 died rc=139 at `rt_cap_push(slot=rsp+0xB0)` — the literal `lea rdi,[rsp+176]` raw claim spelling, slot contents DESCR-tag garbage. The capture lives INSIDE the referenced blob; blob code is compiled ONCE but a claim-relative spelling is ENTRY-REGIME-DEPENDENT, so an armed statement enters at a shifted depth and the slot read lands on stale stack residue. **The flip variable is ABSOLUTE STACK PLACEMENT:** `SCRIP_NO_SEGV_HANDLER=1` "cured" it — but that env is READ BY NOTHING in the live tree (grep 0); its only effect is shifting initial rsp by the string length. ANY dummy env of any length flips 127 to a 3/3 deterministic pass with correct output, ASLR already pinned. The "passing" placements survive on deterministic garbage — a stale-but-valid cap-stack pointer from a prior statement at the same depth. This is the s23h flake-ledger disease (identical-bytes rc=139 flicker) caught with its hand on the exact instruction, and it names 126/131/145/180/181's baseline reds as the same defect at other placements. 127's m3 verdict flipped F in the full sweep at HEAD-IDENTICAL bytes — it was never a stable green.
4. **The narrowing is the mechanism, not a guess:** capture kinds (TT_CAPT_COND/IMMED/CURSOR) in the TARGET tree → decline (25→17). The sound blob spelling is a wire/anchor-carried claim base (the CARRIED-OPEN r9 park-address item), not rsp arithmetic — that design rung is the recorded fix; until it lands, capture-bearing targets stay declined.

## INSTRUMENT LAWS

- **An unread env var is still an instrument:** it moves initial rsp by strlen. Any placement-sensitive verdict must be re-rolled across env paddings before belief — this generalizes the ledger's ASLR law to setarch -R worlds.
- gdb "fixing" a crash means the crash is placement/timing, not logic — go to `core_pattern=core.%p` + post-mortem, never conclude from the live-debug pass.

## HONEST RESIDUE

- 070/072/074/180/181 red→red (baseline star-var/arbno-defer defects, out of this rung's scope).
- The r9/wire claim-base design rung is OPEN — it is what re-admits capture-bearing targets AND is a step toward retiring every raw `[rsp+K]` blob spelling (the corpse-deletion direction).
- The record's per-program m3 fail set is not on disk (counts only), so the 213-flake attribution of the m3 +1 rests on the LAWS entry naming it, plus its absence from my non-pass set.
