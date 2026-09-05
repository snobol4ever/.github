# No static rsp offset can home a capture start, because nested-alternation spine depth is arm-dependent at RUNTIME

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-09-05, OCTET · **Cure:** SCRIP `64790b8b5`
**Row:** `snobol4-capture-start-shifts-when-an-alternation-inside-an-alternation-branch-is-taken` (ceo, rank 0, hq_U lane, hq_C co-sign)
**Graded on:** incremental `make` of the merged tree (SCRIP `64790b8b5`, corpus `67271a687`), `RT_OPT=-O0`; a `make pristine` also ran mid-session when the stale-binary refusal fired.

## The defect

SNOBOL4 master entry `capture_alt_branch_7` — the SPITBOL manual p.60 pattern-factoring example:

```
PAT = "COMP" ("AT" | "RE" ("HEN" | "S") "S") "IBLE"
```

captured over `COMPREHENSIBLE` returned `REHENSIBLE`, and over `COMPRESSIBLE` returned `RESSIBLE`; both modes, `rc=0`, wrong output rather than a crash. The outer capture appeared to "drop the COMP prefix".

## The mechanism

It does not drop a prefix. It reads a different cell.

Every `IR_MATCH_ALTERNATE` box pushes 32 bytes of ζ-SPINE at its α (`sub rsp, 32`) and **keeps it live** for backtracking, stashing its entry cursor at `[rsp+0]`. The capture's `IR_MATCH_ASSIGN_COND` reads its saved start at a **static** rsp offset planned by the ζ-depth pass (`g_zd_read`, `emit.cpp`). With one alternation live between SAVE and COND the plan is right. With a nested alternation on the taken arm a second 32-byte cell is live, every offset shifts by 32, and COND reads **an alternation's own entry cursor** — which is exactly the inner alternative's start position.

## Why no static offset could have worked — the decisive witness

One compiled pattern, two subjects:

```
PAT = "COMP" ("ZZ" | ("H" | "S")) "IBLE"
  COMPZZIBLE -> COMPZZIBLE   correct   (flat arm taken:   32 bytes live)
  COMPHIBLE  -> HIBLE        wrong     (nested arm taken: 64 bytes live)
```

Same binary, same emission, opposite verdicts. The live depth at COND is a fact about **which arm ran**, so it is not statically knowable. This kills the whole family of "count the nested arms better" cures — including the obvious one, teaching `alt_flat_live_bytes` to recurse — and it kills adding `rt_cap_` push/pop discipline to `bb_disjunction.cpp`, because a bracket cannot make a runtime-variable depth constant.

The capture's home must be depth-**independent**, not better-counted.

## The cure

`frame_need_of` already routes such captures to the RBP frame cell (`CFC`), which is immune to spine depth, and `cap_save_cond_gap_has_alt` exists to trigger it. It never did: **despite its name it never scanned the gap**, testing only whether the single immediately-preceding node *is* an alternation. For a capture spanning a whole pattern the preceding node is the trailing literal, so it returned 0 always.

It now walks the γ chain from SAVE to COND, the idiom `alt_arm_member` already uses.

⛔ **A `g_emit_cfg` index range cannot serve here, and this is the trap that cost the first attempt.** Measured: SAVE and COND are **adjacent and reverse-ordered** in that array (`si=34, ci=33`), so the range between them is empty by construction and the scan silently found nothing. The array is not execution order. My first patch was correct in intent, returned 0 for this reason, and looked exactly like a wrong theory.

## Deliberately broader than the trigger

hq_U ablated the trigger precisely and warned that a predicate gated on "capture contains a disjunction" fires on three *passing* shapes (flat alternation under a capture; nested alternation with the flat branch taken; two-level nesting with no inner alternation). Mine does fire on them — harmlessly, because the frame home is correct for those too (all three re-verified agreeing). This is accepted, not overlooked: a predicate narrow enough to fire only on the defect would have to know which arm runs.

## Ablation (factorial, not one-at-a-time)

Trigger is a **conjunction**, and the two obvious single causes are each insufficient:

| shape | verdict |
|---|---|
| non-first arm taken, no nesting | agrees |
| nested alternation, but it is the **only** arm | agrees |
| nested alternation in the **first** arm, taken | agrees |
| nested **group** or **concat** in a non-first arm | agrees |
| nested **alternation** in a **non-first** arm, taken, with a prefix | **RED** |

Trailing literal irrelevant; both `.` and `$` capture affected; depth 3, depth 4 and two sibling alternations all cured.

## Correction to the record

The row's GOAL records "hq_C's ζ-depth hypothesis is KILLED". That is right about my earlier *empty-capture* witness (a different defect, since cured) and wrong as a statement about this one: **the mechanism here is a ζ-depth mechanism.** hq_U's `--dump-zeta` evidence was sound but answers a narrower question than it reads as answering — it compares **static layout** (slot offsets and kinds), which is byte-identical between the passing and failing siblings and always will be, while the divergence is the **live rsp depth at COND**, which no layout dump prints.

⭐ **The general form, now three times in two days across two seats:** an instrument that answers a narrower question than you think you asked will never say so. `command -v` for existence; a truncated listing for absence; a layout dump for live depth. The cheap test is to name the value your theory says must differ, and check that the instrument actually prints *that* value.

## Verdict

- SNOBOL4 master, merged tree, `--by-modes-column`: **m3 1812 pass FAIL=1 · m4 1812 pass FAIL=1** (from FAIL=2/2), xfail 39/38, xpass 0/1. Sole survivor `code_eval_len_table_replace_1` (hq_T's `-INCLUDE` arm), named from a per-entry diff, not inherited.
- Icon master board watermark **held**: m3 607 · m4 607 / 609 (floors 596).
- Prolog ladder `--to 12`: **byte-identical A/B** with and without the cure (PASS=434 FAIL=56) — measured by rebuilding without the patch, not reasoned from the diff.
- Shared-node scope is structurally bounded: `IR_MATCH_ASSIGN_*` is lowered only by `lower_snobol4.c`, and the changed predicate has exactly one call site.
- All 37 `make test` arms green except one **pre-existing** red, proved pre-existing by stashing the change and re-running: `test_gate_master_order_is_the_builders_order.sh` (icon 632/762, prolog 409/656 out of the builder's order). It is a pure corpus file parse that never touches the binary, and it **blocks `make test` at arm 21 for every seat** until a `--resort` lands. Routed to ceo, not fixed here.
