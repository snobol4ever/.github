# FINDING — 2026-09-04 (hq_T, QUARTET #5; queue row `snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries`)
# THE FENCE BODY BRACKET WAS NEVER THE BODY — IT WAS THE OUTER CAPTURE PAIR, SO EVERY STACKED CAPTURE INSIDE A FENCE WAS CLASSIFIED AS NEEDING NO FRAME

**Tree at measurement:** SCRIP `7d7ff2dc5` + this change, incremental `make`, `RT_OPT` `-O0` (read from `Makefile:43`, not typed). corpus `fc9c0a4ac`. .github `eae35b7e`. Oracle `/home/resources/x64/bin/sbl -bf` (the 18:19 swap). Box clock 2026-09-04 22:11 CDT. Measurer `hq_T`.

## 0. WHAT IS CURED, STATED BEFORE THE STORY

`cap_in_repeat_body()` (`src/emitter/emit.cpp:706`) decides whether a capture lies inside a repeat/fence body; a `1` earns the capture a real frame slot. For a FENCE carrier it bracketed the body as `[index(operands[0]), index(operands[1])]`. **Those two operands are not the body's extent.** Read the lowering (`src/lower/lower_snobol4.c:1493-1507`):

```c
int before_p = g->n;
IR_t * pe = sno_pat_node(cx, t->c[0], F, F);              /* body nodes land at [before_p, g->n) */
IR_t * p_tail = (before_p < g->n) ? g->all[before_p] : pe;
ir_operand_push(F, pe);        /* operands[0] = the entry node the body returned  */
ir_operand_push(F, p_tail);    /* operands[1] = the FIRST node built in the body   */
```

Both operands sit at the **start** of the body; neither is its end. The capture cases `return save`, so for a body whose first construct is a capture, `operands[0]`/`operands[1]` are exactly that capture's `SAVE` and `IMM`/`COND` — **the bracket is the outer capture pair and nothing else**. With one capture in the body that is accidentally the whole body and the predicate is right by luck. Add a second, stacked capture and the inner pair falls outside its own body's bracket.

**Measured on `'ab' FENCE(('ab' . v0) $ v0)`** (`SCRIP_CAPREPEAT_DIAG`, a temporary probe, removed before landing): body nodes at CFG indices 18,19,20,21 (`MATCH_ASSIGN_IMM`, `MATCH_ASSIGN_SAVE`, `MATCH_ASSIGN_COND`, `MATCH_ASSIGN_SAVE` — confirmed by `--dump-bb`); carrier bracket `lo=18 hi=19`; inner pair `ni=20 si=21` → `out` → `NO CARRIER COVERS IT`. `SCRIP_EARN_DIAG` before: outer pair `need=1`, **inner pair `need=0`**. After: all four `need=1`, and `--dump-zeta` shows two `capture.stack` slot pairs (`+144/+152`, `+192/+200`) where before there was one.

**The cure** — record the body's true extent out of band at lowering and consult it in the predicate:

- `src/lower/lower_snobol4.c` — `fc_pair_extent_register(F, g->n)` after the body is built, at **all three** FENCE1 sites (1493, 1675, 1692).
- `src/emitter/emit.cpp:715` — `{ int fe = fc_pair_extent(C); if (fe > 0 && fe - 1 > hi) hi = fe - 1; }`.

⛔ **Why not a third operand on the FENCE node, which is the obvious move:** FENCE1 operands are walked *generically* — `RPO_PUSH` pushes every operand (`emit.cpp:2773`), `zdp_has_pairs` declares FENCE1 pair-shaped (`zeta_depth.c:32`), and `emit.cpp:3038/3182` gate on `n_operands > 0`. A third operand would be read as half of a pair by code that never asked what it meant. That is the same overloading trap seat12 hit from the other side on ARBNO's `operands[1]` — the reason this fix is deliberately **out of band** in the existing `fc_pair_extent` registry (an existing global; no new global was introduced, per the ABSOLUTE RULE) rather than in the operand vector.

## 1. WHAT IT MOVES, MEASURED — AND WHAT IT DOES NOT

Fresh census of all 19, both modes, oracle `-bf`, **under `setarch -R`** (see §2):

| entry | before | after |
|---|---|---|
| `arbno_fence_span_replace_branch_1` | m3 rc=0 **wrong output**, m4 rc=0 wrong output | **m3 + m4 match the ref — CURED, both modes** |
| `fence_capture_imm_capture_replace_branch_1` | m3 SIG11, m4 SIG11 | **m4 matches the ref**; m3 still SIG11 |

No other entry of the 19 changed state, and **none regressed**. The m4 cure generalises across the whole stacked-capture-in-FENCE family — `FENCE(('ab' . v0) $ v0)`, `FENCE(('ab' . v0) . v1)`, `FENCE(('ab' $ v0) $ v1)` all now print `match` in m4 and agree with the oracle.

⛔ **THE CLASSIFIER FIX IS NECESSARY AND NOT SUFFICIENT FOR m3, AND I AM NAMING THAT RATHER THAN LETTING THE m4 GREEN IMPLY A CURE.** With all four captures now correctly framed, m3 still dies at a wild jump (`rip` inside the JIT slab, backtrace destroyed). It is a **second, independent defect**: the green sibling `'ab' (FENCE('ab' . v0)) $ v1` has *identical* frame geometry (`slots=17 region_end=272`) and passes, so frame sizing is exonerated; and five killswitches — `SCRIP_OPT=0`, `SCRIP_CAP_SLICE=0`, `SCRIP_CAP_NEST=0`, `SCRIP_PAT_INLINE=0`, `SCRIP_FENCE_IGNORE=1` — are all **inert** on it. That m3 defect is open and is the next seat's ground.

## 2. ⛔⭐ THE NONDETERMINISM IN THIS CLASS IS ASLR-DEPENDENT, AND `setarch -R` MAKES ALL 19 REPRODUCIBLE

Several xfail reasons in this class carry an own-noise caveat ("read any single run as one draw, not a verdict"), and seat12's census and mine disagreed on exactly two entries. **Both disagreements are explained and neither census was wrong.** Measured, 6 draws with ASLR on and 3 with it off:

- **17 of 19 are deterministic.** Same label every draw, ASLR on or off.
- **2 of 19 are nondeterministic — and ASLR-dependent**: `arbno_bal_tab_replace_branch_1` and `arbno_fence_tab_replace_branch_1` give `0/HANG` at roughly even odds with ASLR on, and **hang 6/6 under `setarch -R`**. Not slow-near-the-timeout: the outcome is bimodal, 0.00 s or unbounded (measured to 120 s).

⭐ **The general form, and the reason this outranks the entry-level result:** an outcome that depends on ASLR is an outcome that depends on an *address*, so something in this family is consuming an address, or an uninitialised value that happens to hold one, **as data**. hq_B independently hit the same shape from the allocator side tonight on `fence_bal_rtab_branch_1` — "ZHP heap exhausted (512 MB, **0 blocks**)", a claim of exhaustion with nothing allocated. Two symptoms, one smell.

⭐⭐ **The practical consequence is a measurement lever the whole box can use today: run this family under `setarch -R` and every one of the 19 becomes a stable verdict.** A census of this class taken without it is a sample, not a measurement — which is precisely how two careful sessions produced two different tables from one tree.

## 3. WHAT THIS DOES NOT CLAIM

The row's DONE-WHEN is **still RED** — this is 1 entry cured outright, 1 half-cured, and 17 open; nothing was reclassified, deleted, or had a `.ref` re-cut. The m3 wild jump is open. The ARBNO null-recede mechanism is untouched here and seat12's falsification of the obvious fix stands (`FINDING-2026-09-04-seat12-arbno-null-recede-…`): it needs a genuinely new operand with `flat_drive_match_alt` PAIR-renumbering, not a reinterpretation of `operands[1]`.
