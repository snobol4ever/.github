# FINDING 2026-07-31f — CLAUDE — SN4: EVERY PAIR DEFINE WAS A BETA ENTRY, SO EVERY ALTERNATION SEGVD

**Session:** s22j · **Watermark:** m3 232/85 → **241/76** · m4 230/86 → **240/76** · **REGRESSIONS: 0 (both modes)** ·
DIVERGE 1 → 2 (explained below; nothing got worse) · Benchmarks unchanged at OK=17 CRASH=4 (the remaining
four are a DIFFERENT, pre-existing defect — see §5).

---

## 1. THE DEFECT, IN ONE LINE

`x86_deflabel_pair` reported every PAIR label define as `x86_port_hook(X86H_DEF, X86P_BETA)`, so the
carve-only bracket treated **all 2N+3 of an N-ary box's pair defines as beta ENTRIES** and carved at each one.

## 2. WHY THAT IS FATAL FOR ALTERNATE AND NOT FOR MOST BOXES

The carve-only discipline (`x86_asm.h`, ZW-1) is:

> both entries allocate (alpha AND beta), both exits free (gamma AND omega) — rsp-neutral at every box boundary

That is rsp-neutral **only for a box entered through exactly ONE of {α, β} and left through exactly ONE of
{γ, ω}.** `IR_MATCH_ALTERNATE`'s pair defines are not alternative entries at all — they are **internal rejoin
points inside a SINGLE traversal**. One pass runs α → arm → sigma stub → merge:

| step | site | rsp |
|------|------|-----|
| `n4_match_alternate_α` | α def → carve | −32 |
| `n4_match_alternate_s0` (sigma stub) | PAIR def → *reported as β* → carve | −64 |
| `n4_match_alternate_as` (merge) | PAIR def → *reported as β* → carve, then γ frees | −64 |

**Three carves, one free, −64 net per traversal.** `bb_match_release` then reads `bb_match_head`'s saved-rsp
unwind base (`[rsp+16]`) at the wrong depth, loads garbage, and executes `mov rsp, <garbage>`. Measured
`rsp = 0x0`, immediate SIGSEGV. Minimal repro — **crashes at N=1, so it was never stack exhaustion**:

```
    S = 'aaaxx'
    S ('aaa' | 'bbb')     :F(NO)      * SEGV.  A bare literal `S 'bbb'` is fine.
```

⭐ It fires even when the FIRST alternative matches at cursor 0 with zero backtracking, which is what proves
the fault is in the carve bracket and not in the backtracking topology.

## 3. THE FIX — A SITE CODE, NOT A KIND TEST IN THE ENCODER

`X86H_DEF_PAIR = 3` added beside `X86H_DEF/JMP/JCC`. `x86_deflabel_pair` reports it in **both media** (TEXT and
BINARY arms edited together, per BOTH-MEDIUM MANDATORY). Only two hook arms key on `X86P_BETA`: the carve
(now split so pair defines take the `!op_pair_rejoin` arm) and the `ZC_PORT_OWNED` mark, which was widened to
accept both spellings so OWNED-mode behavior is untouched. **Every other hook arm is alpha-keyed**, so this
cannot perturb anything else.

⛔ **THE SUPPRESSION IS KIND-GATED AND MUST NOT BE WIDENED BY SHAPE.** Kind dispatch lives at emit.cpp's ONE
choke (`op_pair_rejoin`, promoted scalar, appended at struct end per the s141 ABI law); `x86_asm.h` consumes
the scalar and stays encodings-only per the standing taxonomy.

## 4. ⛔ TWO ARMS FALSIFIED BY MEASUREMENT — DO NOT RETRY EITHER

**(a) Excluding `IR_MATCH_ALTERNATE` from `zw_carve_k`.** The obvious fix, and it *is* directionally right
(fc_geom already declines ALT; the template's own ALT-FLAT header says "the box moves rsp nowhere"). Measured
**m3 243 / m4 241 — better than the landed fix — but it REGRESSED `135_pat_balanced_parens_shallow` +
`136_pat_balanced_parens_deep`.** Root cause: `zw_carve_k` also **sizes the pattern blob frame**. Diffing
against the committed artifact, `PAT$0` shrank 80 → 48 bytes and every offset shifted by 32. It changes the
carve AND the layout; the recursive `'(' FENCE(*B | eps) ')'` shape does not survive the relayout. Reverted.

**(b) Suppressing the pair-define carve for ALL N-ary kinds.** Measured **m3 240 / m4 239, DIVERGE 0** — but it
REGRESSED `065_capture_then_arbno` + `164_pat_arbno_nested`. **`IR_MATCH_ARBNO`'s pair entries are GENUINE
per-iteration claims** — the rsp linked-frame chain named in `ARCH-SNOBOL4.md` §"ARBNO iteration frames". ALT
and ARBNO look like the same shape and are not: ALT's pair defines are rejoins within one traversal, ARBNO's
are fresh iterations. **Do not re-derive "they are both N-ary, so treat them alike."**

## 5. WHAT THIS DID **NOT** FIX — THE BENCHMARK CRASHES ARE A SECOND, PRE-EXISTING DEFECT

Benchmarks stay `OK=17 FAIL=0 CRASH=4` (`pattern_bt`, `pattern_bt_deep`, `roman`, `eval_dynamic`).
`pattern_bt`/`_deep` are the SAME program at different iteration counts. Their alternation is now correct
inline, but they assign the pattern to a variable first (`PAT = (...) ; S PAT`), which routes through the
**pattern-blob RBP regime**, and that path has an independent bug:

```
proc_PAT$0_α:  sub rsp, 48        # frame = 48 bytes
               mov [rsp + 40], rbp
               mov rbp, rsp       # rbp = frame base
proc_PAT$0_α_body:
               mov qword ptr [rbp + 64], rax   # ⛔ 16 BYTES PAST THE FRAME END
```

The ALT's own quads then land on `[rbp+24]`/`[rbp+32]`, **colliding with the prologue's saved RCX/RDX**, with
saved RBP at `[rbp+40]`. Observed `rbp = 0x0`, then an indirect jump through an rbp slot to address 0.

⭐ **PROVEN PRE-EXISTING, NOT A REGRESSION:** the COMMITTED artifact `corpus/benchmarks/snobol4/pattern_bt.s`
(HEAD's own honest output, before this session) has the identical shape — `sub rsp, 48` / `mov rbp, rsp` with
references reaching **`[rbp + 568]`**. Verified by reading the artifact, not by inference.

This is the whole-graph carve corpse disagreeing with what the boxes actually address, exactly as THE MODEL
describes. It is its own rung and wants the monitor, not another read of the emitter.

## 6. SIDE OBSERVATION, NOT A CLAIM

`mixed_workload` fell 4941 ms → 2670 ms across this change at RT_OPT `-O0`. Plausible (spurious carves
deleted) but **single unrepeated runs, cold, one core** — per the O2-DIRECTED-ONLY rule and the s220 warm/cold
lesson this is NOT a benchmark result and must not be quoted as one until measured MIN-OF-N warm.

## 7. NEXT

1. ⭐⭐ **The pattern-blob frame (§5)** — gates `pattern_bt`, `pattern_bt_deep`, and the PAT-variable class generally.
2. The 76 remaining crosscheck reds are still overwhelmingly `pat_*`; `IR_MATCH_HEAD` (247 declines) is unmoved.
3. `151_pat_arbno_inline_fence_backtrack` now passes m4, still fails m3 — this is the ENTIRE DIVERGE 1→2 delta.
   The divergence rose because **m4 improved and m3 did not**; no program got worse in either mode.
