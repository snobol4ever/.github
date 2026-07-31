# FINDING 2026-07-31h — SN4 s22l — THE `SCRIP_NOFC` KILLSWITCH WAS ASYMMETRIC, AND WHEN MADE SYMMETRIC THE NON-POPPING ZETA SPINE FIXES 33 PROGRAMS — PLUS: ASLR IS A ±2 NOISE SOURCE IN EVERY m4 WATERMARK EVER RECORDED

**Session:** s22l · **Commits:** SCRIP `b5bc62cc` (ZD-SR) · `465a9bc8` (feature artifacts) · `78ead226` (NOFC-SYM) · corpus `1bba0b3d` + `af763851` (artifacts)
**Goal:** GOAL-SNOBOL4-BB — "get benchmarks working using the NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary" (Lon).

---

## ⭐⭐⭐ HEADLINE

`SCRIP_NOFC=1` — the instrument the ladder uses to ask *"what breaks if the FC arm and its five pops are deleted?"* — **was measuring its own asymmetry, not the regime.** Made symmetric, the non-popping spine does not merely match the FC regime; it beats it by **+32 crosscheck / +33 broad programs**, and the programs it fixes are **exactly the `pat_*` red objective** that ZD-5 had scoped as a 247-head, ~230-FRQ-site, "genuinely design-tier" campaign.

| gate (all `setarch -R`) | FC default | NOFC symmetric | Δ |
|---|---|---|---|
| crosscheck m3 | 276/41 | **308/9** | **+32** |
| crosscheck m4 | 275/41/1 | **306/10/1** | **+31** |
| crosscheck DIVERGE | 2 | **1** | −1 |
| broad m3 | 277/59 | **310/26** | **+33** |
| broad m4 | 276/54/6 | **308/22/6** | **+32** |
| benchmarks | 20/21 | **20/21** | identical |

Oracle-verified 5/5 (`052_pat_arbno`, `064_pat_fence_fn_capture`, `126_pat_json_number`, `167_pat_arbno_depth_20k`, `131_pat_boolean_expr_grammar` — byte-identical to `sbl -b`). One regression: `143_pat_regex_quantified_class`.

**SCRIP_NOFC remains OFF by default. Flipping it is Lon's call.**

---

## ⛔⭐⭐ INSTRUMENT LAW — ASLR PUTS ±2 OF PURE NOISE IN EVERY m4 FIGURE. RUN CORPORA UNDER `setarch -R`.

Three broad-corpus runs of **one unchanged compiler** gave m4 = **277 / 276 / 278**. Under `setarch -R` the same corpus is byte-stable across runs (only the TIME line differs).

**The mechanism, measured:** `fence_driver` and `151_pat_arbno_inline_fence_backtrack` fail **6/12** and **9/12** with ASLR on, and **10/10** with ASLR off. **ASLR-off is the *failing* side.** These are not flaky passes — they are **broken programs that sometimes get lucky** on stack garbage. Every green count containing them is inflated, and the deterministic floor is the honest number.

**CONSEQUENCES, and they are not small:**
1. **A rung claiming a ±1 m4 movement may be reading a coin flip.** s22k's ZD-9 claim "m4 275→276 (fixed `151_pat_arbno_inline_fence_backtrack`)" names one of the two flaky programs *by name*. That claim needs re-measurement under `setarch -R` before it is trusted.
2. It explains this session's start-of-session discrepancy: the LIVE CURSOR claimed m4 276/40 · DIV=3; I measured 275/41/1 · DIV=2. The differing program was `151_pat_arbno_inline_fence_backtrack`.
3. **I nearly billed a coin flip to my own rung.** The killswitch control run reported `fence_driver` breaking under ZD-SR. The `.s` files were **md5-identical** between killswitch arms — the regression was impossible by construction, and only the byte-check caught it.

⭐ **ADD `setarch -R` TO THE CORPUS RUNNERS.** It costs nothing and converts an unhuntable heisenbug class into a deterministic reproducer, which is exactly what RULES.md's monitor-first doctrine needs to work at all.

---

## THE ASYMMETRY, NAMED

`nofc()` lived in **three template copies** (`bb_assign_global` / `bb_binop_arith` / `bb_binop_concat_slot`), each its own `getenv` — the "spelled three times" shape the s22k ZD-K law was written about, found again one session later in a different file.

Each copy flipped **only the CONSUMER's read**. The PRODUCER kept its `fc_geom` grant and kept carving. So under NOFC a declined statement had:

```
n1_var_α:   sub rsp,16 ;  mov [rsp+0], rax      ← producer writes its OWN cell
n2_lit_α:   sub rsp,16 ;  mov [rsp+0], 6        ← producer writes its OWN cell
n3_binop_α: mov eax, [rsp+240]                  ← consumer reads the FLAT slot: NOBODY'S WRITE
```

Hence `func_call` printing `result: 0`, and 16B leaked per statement per iteration until loop-resident programs died. **The break set was the instrument's own artifact.**

`zc_nofc()` (zeta_storage.c) is now the one authority. Under it the ZB-VAL value-spine grant is withheld and the universal carve suppressed, so a non-armed node is **fully flat** and an armed node is untouched (its K comes from ZD staging; every dispatch `fc_geom` arm is already `!op_zres`-guarded). Two regimes, no third state.

## ⛔ THE KILLSWITCH BELONGS ON ONE LINE — MEASURED BOTH WAYS

A blanket `if (zc_nofc()) return 0;` at the head of `fc_geom` **fixed the entire DEFINE/EVAL break set** (func_call, func_call_overhead, indirect_dispatch, eval_fixed) **and broke five pattern programs that had been passing** (mixed_workload, pattern_bt, pattern_bt_deep, roman, string_pattern).

**The name "FC" invites the category error.** The ZB-FC-3c/ZB-FC-4 cells — `MATCH_ARB/SPAN/TAB/RTAB/BREAK/BREAKX/BAL/REM`, the `SCAN_*` Icon twins, granted `ASSIGN_SAVE` — are the match family's **real and only storage**; their templates are written against the cell, it is not a legacy alternative to anything. Only the **ZB-VAL-0/2/3 value-spine grant** is the arm the ladder is retiring. Only it answers to the killswitch.

---

## ZD-SR — `IR_SAVE_RESTORE` ADMITTED (SCRIP `b5bc62cc`)

`zd_plan` declines a whole run on its first non-whitelisted node. `INC = N + 1` lowers to `var → lit → binop → assign → save_restore` chained γ-wise, so **the trailing RETURN floater disqualified four value nodes that were all already whitelisted.**

Admitted roles 1/2/3 as a transparent protocol box (`zd_nops` 0, `zd_k` 0). Not new reasoning — the STMT_FRAME classifier already calls this kind "self-allocating by construction" in its `_callfam` arm. **Role 0 stays declined** (the only role with the CALL2BB arg-window preamble; exists only under `SCRIP_CALL2BB=1`, default 0 — exactly why ZD-2l deferred the kind). `zd_sr_role()` is one authority for the union-tag read.

Gates: IDENTICAL BY SET, both modes, both corpora. **ZD-SR alone does not move the NOFC gate** — it is a prerequisite, not a win, and was landed on that basis.

---

## ⭐⭐⭐ THE HYPOTHESIS THIS HANDS THE LADDER — TEST IT, DO NOT ADOPT IT

The fixed set is `arbno` / `fence` / `alternation` / `capture` — the backtracking family, wholesale. The mechanism this points at:

> **The POP is what breaks pattern backtracking.** A box that releases its operand cell on the success read destroys state a later β re-entry needs. Under the non-popping discipline the producer's cell survives to the run's release point, so re-entry finds it intact.

If that survives testing, **ZD-5 was aimed at a symptom**: the 247-head census would shrink not by converting 230 FRQ sites but by deleting the pop. ⛔ It is ONE session's inference from an aggregate, and 33 programs changing state at once is exactly when a wrong mechanism looks most convincing. **Falsify it on `143_pat_regex_quantified_class` first** — the single regression is the cheapest available discriminator, and a mechanism that cannot explain its own counter-example is not yet a mechanism.

---

## OPEN / NEXT

1. ⭐⭐⭐ **Lon ruling: flip `SCRIP_NOFC` to default-ON?** +32/+33 with one regression. Everything is behind the killswitch, so the flip is one line and reversible.
2. **Re-measure the recent m4 claims under `setarch -R`** — at minimum s22k's ZD-9 "+1".
3. `143_pat_regex_quantified_class` — the one regression, and the hypothesis' falsifier.
4. **ZD-9 residue:** `func_call` emits its proc body twice; the `main`-inline copy arms (`floor=704`), the standalone `proc_LBL__INC_α` blob does not (`floor=0`). One of the four proc-emission loops does not set the driver's stub verdict.
5. `eval_dynamic` remains a genuine timeout (EVAL ~150× SPITBOL), unrelated.
6. If NOFC goes default-ON, **the FC arm and the five pops become deletable** — the ladder's stated NEXT (5) — and `bb_call_proc_staged`'s 590-line ZD arm (NEXT (3)) may be unnecessary for the *correctness* gate, though still wanted for CARVE-ERAD.
