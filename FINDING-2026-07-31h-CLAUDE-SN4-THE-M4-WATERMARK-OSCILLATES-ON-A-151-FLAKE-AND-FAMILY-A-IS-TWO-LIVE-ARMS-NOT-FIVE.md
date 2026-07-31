# FINDING 2026-07-31h — THE m4 WATERMARK OSCILLATES ON A `151` FLAKE, AND FAMILY A IS **TWO LIVE ARMS, NOT FIVE**

**Session:** s22l (Claude). **HEAD:** SCRIP `417add3c` (= s22k close), corpus `c46eee1f`, tree clean, nothing behind origin.
**Class:** MEASUREMENT SESSION — **ZERO CODE COMMITS**. Three results, each of which corrects a number the board was
carrying as exact. Nothing here required an emitter edit; two of the three would have CORRUPTED the next rung's gate
had they not been measured first.

---

## 1 ⭐⭐⭐ THE RECORDED WATERMARK IS ONE FACE OF A COIN FLIP — `151` IS NONDETERMINISTIC ON **m4**

s22k recorded, as exact: **m3 276/41 · m4 276/40 · DIV=3 {140, 151, W04_arbno_basic}**.

Re-proven at the same HEAD, three consecutive full crosscheck runs:

| run | m3 | m4 | DIV |
|---|---|---|---|
| 1 | 276/41 | **275/41/1** | **2** |
| 2 | 276/41 | **275/41/1** | **2** |
| 3 | 276/41 | **276/40/1** | **3** ← s22k's record exactly |

**m3's fail set is BYTE-IDENTICAL across all three runs. m4's varies by EXACTLY ONE member —
`151_pat_arbno_inline_fence_backtrack` — with no canceling pairs** (`comm` diff of the sorted fail sets: a single
line, both directions checked).

Isolated, compiled once, run 8×:

```
run1 rc=135  run2 rc=139  run3 rc=0 MATCH  run4 rc=135
run5 rc=0 MATCH  run6 rc=0 MATCH  run7 rc=135  run8 rc=0 MATCH
```

**4/8 exit 0 with output byte-matching the ref; 4/8 die on SIGBUS(135)/SIGSEGV(139) with ZERO output.** Same binary,
same input, no env difference. So the honest watermark at `417add3c` is **m3 276/41 (stable) · m4 275–276 / 41–40 / 1
skip · DIV 2–3**, and `140_pat_eval_double_fn_trick` is a PERMANENT m4 compile-SKIP (not a run failure).

⚠ **THE STANDING LAW'S RATIONALE IS INVERTED AT THIS HEAD.** `GOAL-SNOBOL4-BB.md` carries **"⛔ COMPARE m4, NEVER m3,
WHEN GATING"**, justified by `test_string` segv-ing nondeterministically on m3. That justification does not describe
this HEAD: **m3 was the stable mode across three runs and m4 was the one that wobbled.** The RULE may still be right
for other reasons (m4 is the byte-inspectable mode), but the REASON printed beside it is now false, and a session that
trusts "m4 is the deterministic one" will read a phantom ±1 as a rung result. **State the flake set with every
watermark; do not quote 276/40 as exact.**

⛔ **THIS ALREADY ALMOST CORRUPTED THIS SESSION'S OWN INSTRUMENT.** The NOFC A/B set-diff (§2) reports
`151` in the **"FIXED by NOFC"** column — i.e. it reads as *NOFC repairs a program*. It does not. It is the coin
flip landing the other way inside the A run. Had §1 not been measured first, this session would have recorded
"SCRIP_NOFC=1 fixes 151_pat_arbno_inline_fence_backtrack" as a finding about the FC arm. **A ±1 on m4 is now
uninterpretable without a repeat run.**

---

## 2 ⭐⭐ THE NOFC BREAK SET AT MERGED HEAD IS **21 PROGRAMS, A=15 / B=6** — BOTH FAMILIES GREW

s22k measured 19 (A=14/B=5) pre-rebase at `9df6c5d3` and explicitly flagged **"RE-MEASURE AT MERGED HEAD BEFORE
SPENDING A RUNG ON IT."** Done. `SCRIP_NOFC=1` vs default, m4 fail-set diff:

**m4 255/61/1 under NOFC vs 275/41/1 default. BREAK SET = 21.**

**FAMILY A — 15, reach `zd_plan`, decline at STATEMENT level** (decline-line count in parens):
`test_math`(1) · `084_define_loop_call`(2) · `086_define_locals`(2) · `090_define_entry_label`(2) ·
`212_gc_args_in_flight`(2) · `test_stack`(2) · `083_define_simple_return`(3) · `085_define_two_args`(3) ·
`097_define_capture_return_d2probe`(3) · `1012_func_locals`(3) · `161_pat_defer_fn_nested_match`(4) ·
`204_gc_recursive_frames`(4) · `216_indirect_goto_computed`(5) · `088_define_recursive_fib`(6) · `100_roman_numeral`(7)

**FAMILY B — 6, print NO decline line, declined WHOLESALE at graph level by `flat_jmp_entry`:**
`1016_eval` ⭐**NEW** · `1019_eval_string` · `1020_code_label_transfer` · `1021_code_direct_goto` ·
`214_indirect_goto` · `215_indirect_goto_cond`

Split confirmed **by measurement, not filename** (s22k's own warning): `216_indirect_goto_computed` is Family A again
despite its name (5 declines); `1016_eval` moved INTO B, consistent with the EVAL/CODE fragment protocol.

Aggregate first-blocker kinds over the break set: **`IR_CALL` 31 · `IR_SAVE_RESTORE` 14 · `IR_MATCH_HEAD` 4.**
CALL and SAVE_RESTORE travel together in every Family A program — **Lon's law 6 reconfirmed as a measurement.**

---

## 3 ⭐⭐⭐ THE FAMILY A RUNG IS **TWO LIVE PLACES**, NOT "FIVE ARMS / 7 SITES / 21 FRQ" — THE SIZING WAS ~3.5× TOO BIG

s22k sized the rung: *"`bb_call_proc_staged.cpp` = 590 lines, 7 `bcps_arg_slot` sites across the 5 arms
(SCC :275 / fused `open_detN` :305,:310,:316 / classic `stage_arg_inline` :452 / dc :517 / legacy :553), 21 `FRQ(` sites."*
That counts the arms that EXIST. It does not count the arms that FIRE. Measured across **all 21 break-set programs**:

| arm | signature | programs live in |
|---|---|---|
| **SCC** (`:276`/`:278`) | `rt_proc_call_open_slim` | **15 / 15 of Family A** |
| **`stage_arg_inline`** (`:56–72`, ONE fn, called `:311 :453 :518`) | `g_gc_pending`+`g_call_args`+`rt_arg_stage` | **14 / 15** |
| fused `open_detN` (`:305`,`:316`) | `rt_proc_call_open_det[0-9]` | **0** |
| `dc` (`:517` arm) | `rt_pl_dc` | **0** |
| legacy `bcps_txt_gen_arm` (`:553`) | `rt_arg_stage@PLT` w/o `g_call_args` | **0** |

⚠ **THE OBVIOUS DISCRIMINATOR IS WRONG AND I NEARLY USED IT.** Grepping emitted `.s` for `rt_arg_stage@PLT` returns
**74 hits across 14 programs** and reads as "the legacy arm is hot." It is not: `stage_arg_inline`'s SLOW path also
calls `rt_arg_stage`, and in TEXT medium **both render `@PLT`**. The discriminating signature is the SINK fast path —
`stage_arg_inline` emits a `g_gc_pending` test + `g_call_args` stores beside every stage; the legacy arm emits
neither. **Measured `g_call_args` == `rt_arg_stage` in 21/21 programs, zero mismatches ⇒ every single `rt_arg_stage`
emission in the break set comes from `stage_arg_inline`, and the legacy arm contributes ZERO.**

⭐ **CONSEQUENCE — AND THE LIKELY EXPLANATION OF THE −63.** s22k records *"s22g measured that conversion at −63."* A
conversion driven off the 7-site census necessarily edits **five sites that never execute for these programs** while
perturbing the two that do. The two live places are also the two that are HARDEST to edit blind, because they are the
only ones carrying depth compensation:

- **SCC (`:276`/`:278`) is the ONLY arm that already knows about cells and depth** — it runs a three-way ladder
  (`c2farm()` window → `x86_fc_hit(slot)` cell → flat `FRQB(slot, scc_sb)`) and threads `scc_sb` through every read.
  Its own in-tree comment records a bug of exactly this class already fixed once (*FLATDISP-LIVE-BUMP: "the non-window
  read was 32 short … arg staged at [rsp+128] pre-sub, read at [rsp+128] post-sub = zeroed frame → s=0"*).
- **`stage_arg_inline` (`:57`) is depth-BLIND** — bare `x86("mov","rsi",FRQ(slot))` / `FRQ(slot+8)`, no ladder, no
  compensation. Under ZD admission `FRQ` gains `+op_zdepth` (K=16 via `zd_k`) and every arg address skews by 16 —
  which is precisely the mechanism `emit.cpp:1853`'s exclusion comment already names and MEASURED (085/086/087 blank).

**They must land together.** A single call site emits the SCC fast path AND the `stage_arg_inline` fallback (SCC's
runtime decline routes `je L(5)` into it), so arming one and not the other is the 017 falsification shape with extra
steps, on the same statement.

**RE-SIZED RUNG:** `stage_arg_inline` (one function, 3 call sites, currently 2 `FRQ` reads) + the SCC ladder's two
reads = **two places**. `detN`/`dc`/legacy need NO edit for the break set and should be left alone —
touching them is unmeasurable by this corpus and was 5/7 of the old size estimate.

---

## 4 STATE / NON-CLAIMS

- **ZERO code commits.** `emit.cpp:1853` NOT flipped; `bb_call_proc_staged.cpp` UNTOUCHED. No `.s` artifact regen was
  owed or run (nothing changed codegen) — the s22k TWICE-WITNESSED regen rule is satisfied vacuously, not skipped.
- The ZD infrastructure for `IR_CALL` is already complete and dormant: `zd_nops` returns `n_operands`, `zd_k` returns
  16, `op_zread[i]` staging is automatic. **The only missing piece is the template arm** — confirmed by reading, not
  assumed.
- **NOT claimed:** that arming the two live places will land green. That is the next rung and it is unmeasured. The
  `−63` is explained only as a HYPOTHESIS consistent with the arm census; it was not reproduced this session.
- **NOT claimed:** any watermark movement. Nothing moved; three runs bracket the same two faces.
- `151`'s crash itself is UNDIAGNOSED. Per RULES.md it is a MONITOR job (2-way sync-step), not an emitter read.
  It is an m4 nondeterministic SIGBUS/SIGSEGV in an arbno/fence/backtrack program — plausibly related to the
  s22j pattern-blob RBP frame defect (`proc_PAT$0_α` carving 48 and addressing past it), but that link is
  UNTESTED and must not be inherited as fact.

## 5 NEXT — ORDERED

1. ⭐⭐⭐ **FAMILY A, re-sized: arm `stage_arg_inline` + the SCC ladder TOGETHER**, then flip `emit.cpp:1853`.
   Gate on the m4 fail set **BY SET, with `151` excluded or the run repeated 3×** (§1).
2. ⭐⭐ **DIAGNOSE `151` WITH THE MONITOR** — it is now blocking the INSTRUMENT, not just a red. Until it is fixed,
   every m4 ±1 needs a repeat run to be readable.
3. **FAMILY B (6)** — `flat_jmp_entry` EVAL/CODE fragment protocol; no `zd_wl_kind` widening can reach them.
4. THEN `SCRIP_NOFC=1` reaches the watermark ⇒ delete the FC arm + the five pops (`vfc`/`vfcb`/`vfcc` in
   `bb_assign_global` / `bb_binop_arith` / `bb_binop_concat_slot`).
5. ZD-5 / `IR_MATCH_HEAD` (4 first-blockers in THIS break set, 247 corpus-wide) · CARVE-ERAD per THE MODEL's
   three-step order.
