# FINDING s21x-u (2026-07-30, Claude) — THE "ORDERING DEFECT" IS THE LOAD-BEARING DISCRIMINATOR, AND STEP 2 IS 46 TEMPLATES OF REAL PLUMBING

Rung: `GOAL-SNOBOL4-BB.md` → CARVE-ERAD. Tree at SCRIP `1c0124f1` throughout; **nothing landed, tree clean.**

---

## 1. WATERMARK RE-PROVEN AT OPEN, UNCHANGED AT CLOSE

`m3 229/88 · m4 227/88/2 · DIVERGE=1 (W04_arbno_basic)` — exactly the s21x-t cursor.

⚠ **m3 oscillates 229/230 run-to-run.** The mover is `test_string`, the nondeterministic segfault s21x-s logged (ASLR + rsp sensitivity, ~27% of environment sizes). **m4 is stable at 227/88/2 and is the number to compare against.** A session reporting m3 230/87 has not gained a program.

---

## 2. ⛔ CURSOR STEP 1 IS FALSIFIED BY MEASUREMENT — DO NOT RETRY

s21x-t's NEXT(1) reads: *"set `op_zdepth` from the FINAL `op_fc_bytes` (after the case arms) so the two classes stop differing by accident — a real behaviour change, measure it ALONE."*

**Implemented faithfully and measured alone: m3 229 → 59. A −170 program regression.** REVERTED.

Implementation was the derived-at-read-time form (`x86_zdepth()` = the same formula as `emit.cpp:825`, evaluated at consumption so it sees the value the case arms left). That is the strongest possible reading of "the FINAL `op_fc_bytes`", and it is catastrophic.

### THE MECHANISM — WHY IT COST 170 PROGRAMS

The ordering is **not** an accident to be cleaned up. It IS the discriminator between the two carve classes, and it is currently correct:

- `emit.cpp:1063` resets `op_fc_bytes = 0` per node.
- `zeta_storage.c:1078` — `if (fc_geom(nd, &_d)) return 0;` — `zw_carve_k` returns 0 for granted nodes (the DISJOINTNESS s21x-t already measured).

Therefore at the `walk_bb_node_inner` choke (`emit.cpp:825`):

| node class | `zw_carve_k` | `op_fc_bytes` at choke | `op_zdepth` | reader adds | correct? |
|---|---|---|---|---|---|
| **fc_geom-GRANTED** | 0 | still 0 (reset) | **0** | 0 | ✅ (rebased via `op_fc_base`, arm 2) |
| **carve-only** | K | K (set at `:819`) | **K** | K | ✅ (own carve compensation) |

**The source-line order already implements exactly the granted-vs-carve-only split that step 2 proposes to build.** Making `op_zdepth` consistent collapses the discrimination — granted nodes begin adding their own K on top of an `op_fc_base` rebase that already accounts for it — and that double-add is the 170.

⛔ **The ZTOS-1 claim that "the allocator and the accessor CANNOT hold two opinions" is FALSE at HEAD, but the two opinions are LOAD-BEARING, not a bug.** The field comment and s21x-t both read the divergence as the defect. It is the feature. Any future change that unifies `op_zdepth` across the two classes without first landing the step-2 discriminator will reproduce the −170.

---

## 3. ⭐ THE 88 REDS ARE NOT UNIMPLEMENTED SHAPES — ZERO BOMBS

Hypothesis tested (and **falsified — it was mine, stated at the top of this session**): that the 88 are dominated by mid-design pattern shapes emitting bomb stubs, i.e. not addressing debt at all.

**MEASURED over all 88 m4 failures: `BOMB=0 · NOCOMPILE=0 · CLEAN_COMPILE_WRONG_ANSWER=88.`**

Every failing program emits complete, assembler-accepted code and returns a wrong answer. Method: `scrip --compile` each failure, grep the `.s` for `.Lbomb_msg_` (`emit_str.cpp:38`). **This is a genuine narrowing: the 88 are semantic/addressing divergences, and the family-by-family template crawl is the right shape of work.**

---

## 4. ⭐ THE WITNESS, RE-READ — `028_arith_unary_minus` IS THREE LINES

```
*  028 - Unary minus
        OUTPUT = -5
END
```
Ref `-5`. **SCRIP mode-3 prints `5`.** SPITBOL semantics are not in question (Ch.15: unary `-` negates its numeric operand, unary priority above all binary; `OUTPUT = (-5)`).

⭐ **The negation is not corrupted — it is BYPASSED.** Not garbage, not a crash, not a sign error: the clean unnegated literal. That is the signature of the consumer reading the producer's **input** cell instead of its **output** cell, i.e. exactly one cell (16B) off. It corroborates s21x-t's `+16` witness table from the program's observable behaviour alone, with no instrumentation.

---

## 5. ⭐⭐ STEP 2 SIZED — THE DISCRIMINATOR NEEDS PLUMBING, AND THE MANIFEST IS 46 TEMPLATES

s21x-t's NEXT(2): *"split the two offset MEANINGS colliding in x86_zop arm 4 … The fields are already distinct, so the discriminator may need no new plumbing."*

**THE SECOND CLAUSE IS WRONG, AND THIS IS THE MAIN DELIVERABLE OF THIS SESSION.** The fields are distinct at the CALL SITE (`_.op_sa` vs `_.op_off`) and are erased at the accessor boundary: `FR`/`FRQ`/`FRQB` take a bare `int off` and cannot tell which meaning arrived. `bb_unop.cpp` proves it in one file — `FRQ(_.op_sa)` (cross-box read) and `FRQ(_.op_off)` (own-cell write) are the same call.

**CENSUS over `src/templates/bb_*.cpp`:**

| class | count | meaning |
|---|---|---|
| **COLLIDING — both `op_sa` and `op_off` through FR/FRQ/FRQB** | **46** | need the split |
| `op_sa` only (pure cross-box readers) | 15 | ⭐ **SAFE PILOT SET** — no own-cell writes to break |
| `op_off` only (pure own-cell) | 29 | already correct, do not touch |

Top colliders: `bb_binop_relop` (sa=18/off=18) · `bb_unop` (15/12) · `bb_to_by` (7/20) · `bb_to` (7/17) · `bb_match_arbno` (7/59) · `bb_binop_gvar_arith_slot` (7/5) · `bb_section` (6/6) · `bb_idx_get` (6/6).

**THE RULE TO IMPLEMENT** (from s21x-t's ZDUMP overturn 2, which this session did not disturb): `op_sa` is ALREADY carve-inclusive for a cross-box read ⇒ **must NOT add `op_zdepth`**; `op_off`/`x86_scratch_off` are 0-based within the box's own cell ⇒ **MUST add**.

⚠ **THE ORDER THAT MATTERS.** Land a cross-box accessor (`FRX`/`FRQX` sibling in `x86_asm.h`, adding `op_flat_disp` but not `op_zdepth`) and convert the **15 op_sa-only templates first** — they cannot regress own-cell writes, so the measurement is clean. Only then the 46. ⛔ **Do NOT begin the 46 without the pilot green:** a partial conversion of a colliding file leaves one meaning converted and the other not, in the same template — strictly worse than today, and the "half-finished eradication" the goal file names as the one outcome worse than the frame existing.

⛔ **AND DO NOT HAND-CONVERT 108 TEMPLATES.** s21x-r proposed that twice and was wrong twice. This is 15-then-46 targeted call-site edits against a NEW accessor, not a sweep.

---

## 6. WHAT THIS SESSION DID NOT DO

- Did not land a fix. **No net program gained.** Tree clean at `1c0124f1`.
- Did not run the 2-way monitor (RULES MONITOR-FIRST). 028's divergence is bracketed by *observable behaviour* (§4), not by the monitor; the monitor remains the sanctioned instrument for the pattern-family 84.
- Did not touch the pattern/fence/arbno cluster (~85% of the 88) beyond establishing §3 (all clean-compile).
- Did not build with `-O2` (RULES O2-DIRECTED-ONLY). All numbers `-O0`.
