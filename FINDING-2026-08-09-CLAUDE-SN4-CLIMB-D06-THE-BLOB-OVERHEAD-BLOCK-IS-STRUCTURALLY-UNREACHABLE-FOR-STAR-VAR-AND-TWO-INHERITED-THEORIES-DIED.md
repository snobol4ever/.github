# FINDING 2026-08-09 (CLIMB s24, Opus 4.5) — D06: THE BLOB-OVERHEAD ADJUSTMENT IS STRUCTURALLY UNREACHABLE FOR `*VAR`, AND TWO MORE THEORIES DIED ON MEASUREMENT

**Rung:** C-6 DEFERRED EVAL (GOAL-SN4-ZETA-CLIMB). **Tree:** SCRIP `d01137ac` · corpus `8be3ef87` — CLEAN, zero commits to code repos. **Watermark:** m3 120/1/0/22 at open AND close (unmoved). m4 119/4/0/20 at open, 118/4/0/21 at close on IDENTICAL BYTES — see §5.

## 1. The measurement that ends the offset debate

`SUBJ ? POS(0) *P $ OUTPUT` with P reassigned between matches. Three probes, each falsifying the theory before it:

| # | Theory | Verdict | Instrument |
|---|--------|---------|-----------|
| 1 | The fc-cell arm (`cfc()`) needs an `op_fc_disp` adjustment | **FALSE** — `fc_disp=-1, zres=1`. The cfc arm is not live; the **ZD arm** is. | `SCRIP_CAP_DIAG` in the IMM dispatch case |
| 2 | `_fb` is 0 because `rt_proc_get_fn` runs before `proc_startup` | **TRUE BUT NOT THE BLOCKER** — forcing `_fb=48` moved the emitted offset ZERO bytes | `--compile` + grep of the IMM read |
| 3 | The guard itself never admits this shape | **CONFIRMED** — `dfr_nops=0` | same diag, extended to print `_dfr->n_operands` |

## 2. Root cause

`emit.cpp:989` (`IR_MATCH_ASSIGN_IMM`; `:988` COND is the identical twin) guards the blob-overhead adjustment with:

```c
if (_dfr && _dfr->n_operands > 0 && _dfr->operands[0])
```

**A `*VAR` deferred-pattern DEFER node carries ZERO operands.** The variable name lives in the node's OWN literal — the emitted asm proves it (`.S0: .string "P"`, loaded by `n48_match_defer_α` straight from the GVA slot). The guard fails at the second conjunct, so the entire block — including the `_adj` computation that exists precisely for this hazard — **never executes for the `*VAR` family**. It was written for a DEFER carrying a `PAT$N` proc name in `operands[0]` (the `pat_static` shape). The GVA-variable form has no operands to carry it.

Compounding defect (real, but downstream of the above): `_pn` feeds `rt_proc_get_fn()`, which cannot resolve a pattern proc at emit time (`proc_startup` has not run) and for `*VAR` is handed a GVA variable name (`"P"`), never a proc name. `_fb` is 0 on both counts. The correct constant is **48** — every static pattern proc carries `flat_frame_bytes = (48 + jcon_value_region + 15) & ~15` with `jcon_value_region == 0` (`emit.cpp:2895`). Forcing it changes nothing while guard #1 stands.

## 3. Why the wrong offset produces exactly `'c'`

SAVE stores the cursor at `[rsp+0]` of its own 16B cell. DEFER adds 16. The sealed direct-call arm then `jmp rax` into `proc_PAT$N_α`, which carves `sub rsp,96`; on success `proc_PAT$N_γ` does `push rbp` + `push res_addr` — 16 more — and jumps to the caller's γ-wire **without unwinding any of it** (`proc_PAT$N_res`, the pushed landing, is never reached via `ret` on this path; those two pushes are vestigial here). Net undisclosed depth between SAVE and IMM: **96 + 16 = 112**. SAVE's cell is therefore at `[rsp+128]`; IMM reads `[rsp+16]`, i.e. inside the dead proc frame.

First match reads 0 there **by luck** and passes. Second reads 2 — stale bytes from the prior activation — giving `saved=2 cur=3` → `'c'` instead of `'abc'`. **A passing D05/first-match is not evidence the offset is right; it is evidence that slot happened to hold 0.**

## 4. ⛔ DO NOT ASSUME 128 FIXES IT

s23 recorded D05-passing and D06-failing both emitting `[rsp+128]` at `e3ef8f7d` — and D06 still failed. At `d01137ac` both emit `[rsp+16]`. Either the offset regressed across those HEADs, or 128 was reached by another route and a **second defect** sits downstream. Reaching SAVE's cell is necessary, not proven sufficient. Emit the corrected offset, then re-measure `rt_cap_open`'s `saved`/`cur` BEFORE claiming the rung.

## 5. The m4 watermark oscillated by one program on identical bytes

119/3/0/20 at open, 118/4/0/21 at close, same HEAD, tree reverted to pristine, nothing committed. Consistent with the two-flaky-test class in `FINDING-2026-08-08-...-SN46-ICN-WATERMARK-IS-NOT-A-NUMBER`. Recorded, not averaged away. **A single m4 run is not a watermark for this suite.**

## 6. Next session

1. Read the name from `IR_LIT(_dfr).sval` (the DEFER's own literal); drop the `n_operands > 0` conjunct for the GVA form. Use the 48 floor — the runtime lookup cannot work here by construction.
2. Confirm `op_zread[1]` moves 16 → 128 in the emitted asm for **both** D05 and D06 before running either.
3. Re-measure `rt_cap_open`. If D06 still reports `saved=2`, the offset class is exonerated a THIRD time — record it and STOP; do not edit further.

Instruments (both reverted, both one minute to rebuild): `fprintf` at the top of `rt_cap_open` in `pattern_match.c` printing `saved`/`cur`; a `SCRIP_CAP_DIAG` line in the IMM dispatch printing `nops/op0/dfr_nops/sval/zread1`. The second one is what cracked this — **print the guard's own conjuncts, not the value you expect the guard to produce.**

## 7. Process note

MONITOR-FIRST was honoured in the negative: the monitor is dark on D06 (exits 0, stdout-only divergence), and rather than re-derive s23's dead ends this session went to compile-time diagnostics at the dispatch site — the emitter's own decision point — which is where the defect was. The s23 anti-pattern block's standing instruction (measure the failing probe against its nearest passing sibling before editing) is what caught theory #2 in one `--compile`; without it the `_fb=48` change would have been committed as a fix that changes no bytes.
