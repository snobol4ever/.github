# FINDING-2026-07-26g — SN4 ZB-VAL-8b-USE: **LANDED**. THE USE PREDICATE ALREADY EXISTED; ONLY THE CONSUMERS WERE MISSING

**Session:** s182 (2026-07-26) · **Baseline:** SCRIP `92e926cf`, corpus `3df944f3` · **Code landed:** YES (5 source files + 3 artifact sets)
**Build:** `rm -f scrip && make -j4 scrip` rc=0; `make libscrip_rt` rc=0.
**Directive (Lon, this session):** *"Have each BB allocate its RESULT value, IF it has one and if it is used. Have each BB allocate its LOCAL STORAGE needs, IF it has any. One instruction, decrement RSP. Sliding offsets, index operands from RSP not RBP. Continue until a BRICK WALL, then add the RBP/RSP dance. FUNCTION and ARBNO are walls, maybe more."*

---

## ⭐ HEADLINE 1 — s181's BLOCKER 2 WAS HALF WRONG. THE ANALYSIS PASS ALREADY EXISTED SINCE s133.

s181 concluded: *"ZB-VAL-8b requires a NEW ANALYSIS PASS, not a predicate tweak."* **The IR half of that is correct and confirmed** — `IR.h` has no `n_uses`/`use_count`/`consumed`, and `ir_node_produces_value()` is opcode-keyed. **But the pass it asks for was already written and already running.**

`zls_mark_value_refs` (`zeta_storage.c:266`, SLOT-ELIDE S1, s133) computes exactly the operand-vs-wire distinction s181 specified — an `operands[]` reference is a VALUE use; a γ/ω wire is a CONTROL use and marks nothing — with the wiring-exclusion list already tuned by crosscheck (ALT/SEQ/FENCE1/MOVE_LABEL excluded; ARBNO deliberately kept in the reader class because its `operands[2]` geometry bracket IS a real slot read, per the s133 075/164/167/W04 catch).

⛔ **It died as a local `lv[]` array inside `zls_build` and steered flat layout alone.** Nothing outside that loop could ask the question. **The work was not writing the analysis — it was persisting it and giving it consumers.**

**LESSON, generalized:** before specifying a new pass, grep for the fact you want. This tree has a decade of half-wired machinery; s180 and s181 both surveyed this exact rung and neither found `zls_mark_value_refs`, because both reasoned from `IR.h` outward instead of from the layout code inward.

---

## ⭐ HEADLINE 2 — THE DIRECTIVE'S "IF IT IS USED" REPRODUCED FROM SCRATCH, AND CONFIRMED AGAINST THE MANUAL

s181's measurement re-derived independently (fresh clone, fresh build, exhaustive grep — not trusted from prose):

| program | shape | CMP result cell | verdict |
|---|---|---|---|
| `lt1.sno` | `LT(A,B) :S(YES)F(NO)` | `[rbp+64]`/`[rbp+72]` — **2 writes, 0 reads** | DEAD |
| `lt2.sno` | `OUTPUT = LT(A,B) 'yes'` | same kind, **read** by `str_concat_d` | LIVE |

Both agree with the SPITBOL oracle (`sbl -b`). **The opcode is `IR_CMP_TEST` (op 77); the coercions are `IR_COERCE_NUMERIC` (op 75).** Both print as `(null)` in `--dump-ir` — *the IR name table has a gap at 75/77*; identity was recovered from the `.s` labels (`n14_op77_α`). Minor, but it cost time twice now and is worth a one-line fix.

**SPITBOL manual p.33 (read this session, as the rule requires):** *"When any of these functions succeed, they produce a null string value."* The canonical idiom the manual gives is `N = LT(N,10) N + 1` — **the value form is idiomatic, not exotic.** This is the documentary proof that blanket zero-granting the predicate would have been a silent wrong-code bug, and it is why the grant must be a per-INSTANCE test. s181 called this correctly.

---

## ✅ WHAT LANDED

**The fact:** `zls_entry_t` gains `int live`, **defaulting to 1**. Only the elide path stamps a measured 0. Any entry site the analysis never visited stays conservatively READ, so the predicate can only ever remove work proven dead — it can never assume deadness it did not measure.

**The query:** `int zls_result_live(const IR_t *)` — returns 1 for unknown nodes. Declared in `zeta_storage.h`, promoted into `g_emit.op_res_live` at ONE dispatch site (`emit.cpp:1305`, the `COERCE_NUMERIC`/`CMP_TEST` arm), deliberately **not** in `DRIVE_FILL` — that runs for every box in the tree, where a wrong answer would be a silent wrong-code bug across 120 templates at once.

**Two consumers, two different wins:**

1. **Don't WRITE a dead cell.** `bb_cmp_test.cpp` folds its two null stores behind `IF(_.op_res_live, ...)` — conformant to R6 (variance inline in the one concat), no medium branch, no new encoder. `lt1` loses exactly two instructions; `lt2` is **byte-identical**.
2. **Don't OWN a dead cell.** `IR_CMP_TEST` and `IR_ASSIGN` admitted to `zls_elide_ok`. Both audited to own **zero locals** (`zls_grant_locals` → `case IR_ASSIGN: return 0;`; `IR_CMP_TEST` absent entirely), so the locals@+16 layout law is untouched.

---

## ⭐ HEADLINE 3 — MEASURED RESULT

| program | frame before | frame after | saved |
|---|---|---|---|
| `lt1.sno` | 216 | **152** | 64 B (4 quads) |
| `lt2.sno` | 200 | **168** | 32 B (2 quads) |

`lt1`'s 64 B matches the SLOT-CENSUS floor (`rq_bytes 208 -> 144`) **exactly**. Across the demo artifacts: **91 changed frame-carve sites**, e.g. `1192→1032`, `328→248`, `216→152`; demo `.s` net **−82 lines** of emitted code.

⚠ **On the aggregate:** summing the diff's ± frame immediates gives ~77 KB, but that counts the same frame once per artifact file and mixes per-box `sub rsp,16` carves with main frames. **Quote the per-frame numbers, not the sum** — the sum is not a defensible figure and should not enter a watermark.

**CORPUS-WIDE OPPORTUNITY REMAINING (census over 52 demo+feat programs, 643 graphs):** 13,970 result quads · 9,963 read · **4,007 DEAD (28.7%) = 64 KB.** The two kinds admitted here are a slice of that; the rest is the ladder below.

---

## ✅ REGRESSION EVIDENCE — MEASURED BOTH SIDES, NOT ASSUMED

- **Crosscheck: `m3 314/1 · m4 312/1 · DIVERGE=0`** — watermark **exactly** preserved. Sole FAIL `test_case` is the pre-existing one.
- **Gates: 28 PASS / 24 FAIL — and the 24 are BYTE-IDENTICAL to baseline.** Established by `git stash` → rebuild → run → restore → rebuild → `diff` of the two failure lists. **Zero gate regression.** (Those 24 are a pre-existing debt spanning `pl_gz*`, `icn_*`, isolation and beauty gates — untouched here, but somebody should know they are red.)

---

## ⛔ HEADLINE 4 — THE ASSIGN ELIDE IS SAFE, BUT ITS SAFETY IS NOT YET PROVEN BY A GATE

`bb_assign_global` is **the only vfc release arm** (`fc_vread_register`). Aliasing a dead assign's slot to the shared scratch could in principle push an `FRQ` offset outside the fc window, where `x86_fc_hit` fails and `FR()` **silently emits `[rbp+off]`** — s181 HEADLINE 6's hazard. Measured: `lt1`'s residual `[rbp+` count is **unchanged (32)**, and the crosscheck is clean, so no fallback fired here.

**That is evidence, not proof.** `test_gate_fc_no_residual_rbp.sh` (s181's proposal) is now a **prerequisite, not a nicety** — the elide widened the population that can trip it, and the failure mode is silent by construction. **Build the gate before admitting another kind to `zls_elide_ok`.**

---

## NEXT RUNGS

1. ✅ **`test_gate_fc_no_residual_rbp.sh` LANDED s182** — baseline 0 misses / 52 programs. `x86_fc_hit` separates GRANTED from HIT; `SCRIP_FC_AUDIT=1` narrates each. Widening is now falsifiable.
2. **Widen the use predicate to the remaining dead 28.7%.** Method is now mechanical: census → identify dead kinds → confirm `zls_grant_locals` returns 0 → admit → crosscheck. Each kind is one line + an audit.
3. **The write-side consumer for the assign family** — `bb_assign_global/local/var` fold their `FRQ(op_off)` stores behind `_.op_res_live` exactly as `bb_cmp_test` now does. Slot elide landed; store elision did not.
4. **ZB-VAL-8c** — per-node computed `op_fc_wbytes` (never a constant; `lt1`≠`lt2` layout proves it).
5. **Statement-root spine entry** — the vfc gate is still `a->op == IR_ASSIGN` (`zls_build`). s181's falsification (`lt1` spine carves 64 not 80) is **still open and untested** — this session moved the FLAT frame, not the rsp spine.
6. Then the walls (`xa_flat` FUNCTION · retry frontier · fence commit · statement bracket).

**Gate docs read this session:** `PLAN.md`, `RULES.md`, `GOAL-SNOBOL4-BB.md`, `CORPUS-LOCATIONS.md`, `ARCH-ICON.md`, `REPO-SCRIP.md`, **`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (read in full BEFORE the template edit, per PLAN.md step 6 — s181 left this unread and it gated exactly the edit made here)**, SPITBOL manual p.33.

**WATERMARK:** m3 314/1 · m4 312/1 · DIVERGE=0 (unchanged — this rung is a size/quality win, not a coverage win). `handoff_status.sh` is the push truth, not this block.
