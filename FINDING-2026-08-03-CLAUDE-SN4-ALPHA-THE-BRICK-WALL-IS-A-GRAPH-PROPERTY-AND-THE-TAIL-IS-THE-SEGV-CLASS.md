# FINDING 2026-08-03 · SN4 ALPHA — THE BRICK WALL IS A GRAPH PROPERTY, NOT A CONSTRUCT LIST; AND ITS TAIL IS THE rc=139 CLASS

**Seat:** ALPHA. **Parent:** SCRIP `c0c77585`. **Landed:** SCRIP `d2146360` (census, default OFF).
**Directive (Lon, 2026-08-03c):** *"Continue this for every box and every construct until you hit a BRICK WALL and realize, oh I need a register RBP stable base pointer for what I'm doing... Several constructs we know we'll want RBP for are STATEMENT, FUNCTION and ARBNO and FENCE1."* + *"All your choices."*

---

## 1. THE CLAIM

The brick wall is **not a construct**. It is a **graph property**.

Sliding RSP offsets are well-defined exactly when every box has ONE static entry depth. The wall is a **JOIN whose predecessors arrive at DIFFERENT accumulated depths** — because no `[rsp+k]` spelling can name the same cell down both edges. RBP is needed there and only there.

Consequence: the standing four-construct list (STATEMENT / FUNCTION / ARBNO / FENCE1, s21x-c law 4) should be the **OUTPUT** of a test, not its input. If the measured set is wider, the list was never the rule — it was a sample of the rule.

## 2. THE INSTRUMENT — `SCRIP_ZD_DEPTH=1`

Read-only census in `emit.cpp`, called immediately after `zd_plan`. Zero `g_emit` writes, zero emission, zero `zd_*` mutation. Default OFF ⇒ **318/318 `.s` byte-identical**.

**Arrival-depth model, taken verbatim from the UNWIND four-clause law (HQ 2026-08-03b)** so the census cannot drift from the emission it audits:

| edge | arrives at | law |
|---|---|---|
| γ | `zout[i]` | clause 1 — roll up forward, cell SUSPENDED |
| ω | `zout[i] − K` | clause 2 — box N's ω frees N's OWN K only |

Two edges into one target at unequal depth = **WALL**.

⛔ **DECLINED nodes (`zon=0`) are SKIPPED, not assumed depth 0.** Their depth lives in the UCLAIM wholesale claim — the very regime this census exists to help retire. Counting them as 0 would manufacture disagreements that are artifacts of the claim, not of the graph.

## 3. MEASURED — 318 crosscheck programs

```
nodes 17115 · armed 13397 · joins 12510 · walls 1410
```

**88.7% of all joins already agree on depth — they are RSP-flat-safe today.** Lon's "99.999%" is directionally right; the measured figure is ~89% of joins, and ~92% of programs carry no tail wall at all.

Wall concentration:

| kind | walls | share |
|---|---|---|
| `IR_STATEMENT_BEGIN` | 1197 | 84.9% |
| `IR_MATCH_BEGIN` | 85 | 6.0% |
| `IR_SAVE_RESTORE` | 58 | 4.1% |
| `IR_MATCH_ASSIGN_SAVE` | 31 | 2.2% |
| **tail (8 kinds)** | **39** | **2.8%** |

**Top three = 95%.** They map onto Lon's list almost exactly: STATEMENT_BEGIN → STATEMENT, SAVE_RESTORE → FUNCTION, MATCH_BEGIN → the match head where ARBNO/FENCE1 live. **The four-construct list is CONFIRMED as the dominant answer.**

On roman specifically: 10 walls, **every one** of them `IR_STATEMENT_BEGIN` or `IR_SAVE_RESTORE`. Not one value-spine box, not one matcher leaf, not one LIT/VAR/BINOP. The spine is already flat.

## 4. ⭐⭐⭐ THE TAIL IS NOT NOISE — IT IS THE SEGFAULT CLASS

39 walls across **14 programs** fall OUTSIDE the four-construct list, in three structurally distinct classes:

- **(a) LABEL-JOIN, `first_depth=0`, preds 5–16** — `IR_LIT_STRING` / `IR_GOTO_DEFERRED`. Programs: `expr_eval`, `test_stack`, `213_indirect_name`, `216_indirect_goto_computed`, `140`/`141_pat_eval_double_fn_*`, `1013_func_nreturn`. These are EVAL/CODE/indirect-goto programs where many `:(LABEL)` edges converge on one landing box and **at least one arrives mid-statement** — a third statement exit, which clause 4 says must not exist.
- **(b) MATCHER BACKTRACK, `first_depth=128/160`, preds=2** — `BREAK`/`TAB`/`SPAN`/`RTAB` in `153_pat_operand_edge_matrix`, `154_pat_construction_time_hoist`, `test_string`. A forward γ and a retry β arriving at different depths.
- **(c) CALL/LIT** — `082_keyword_stcount`, `IR_CALL` preds=2 @16, `IR_LIT_INTEGER` preds=4 @32.

**THE CORRELATION:**

| population | rc=139 |
|---|---|
| 14 tail-wall programs | **9/14 = 64%** |
| other 304 programs | 42/304 = 14% |

**4.6× enrichment.** `test_stack` is the signature shape: verdict PASS, rc=139 — prints correct output, then segfaults. That is exactly the disease HQ named in the U-1a cursor ("value-spine fail-path programs print correct output then rc=139 at HEAD").

⛔ This makes the census an **instrument, not just a design note**: a depth disagreement outside the four constructs is a *predictor* of the segfault class. Class (a) in particular is the one the four-name list does not cover at all, and SNOBOL4 is built on label gotos.

## 5. WHAT THIS SAYS ABOUT SEQUENCING

Class (a) says: a `:(L)` goto that leaves mid-statement without unwinding to statement-entry depth is the defect. The UNWIND law already prescribes the fix on the fail side (ω → pred β → STATEMENT_BEGIN.β). The forward `:(L)` side needs the same treatment: **whack to statement-entry depth, then jump**, which makes every label target arrive at depth 0 uniformly — and that is *why* STATEMENT_BEGIN is 85% of walls. It is already the place the whack lands.

So the wall reduces, essentially, to **ONE construct (the statement bracket) plus the match head**, and the tail is programs where the goto does not whack first.

## 6. ELIDE — THE KILLSWITCH ALREADY EXISTS AND IS NOT THE BLOCKER

Lon: *"You might want to remove temporarily the ELIDE OPTIMIZATION which eliminates RESULTS that are unreferenced."*

`SCRIP_SLOT_ELIDE=0` already exists (`zeta_storage.c:494`) and is **LIVE**: roman 2713 → 2847 lines (+4.9%). Second elide `SCRIP_BETA_ELIDE_OFF=1` (BP-9 dead-β) also exists.

⭐ **MEASURED: the wall set is INVARIANT under elide-off** (roman: 10 walls either way). The elide is orthogonal to depth disagreement and is **not** what is blocking the accumulated-offset traversal. Recorded so the next session does not spend the rung. This corroborates `zeta_storage.c:494`'s own s21x-r note that the "hole-free accumulated-offset traversal" rationale for forcing elide-off "is NOT load-bearing at HEAD."

## 7. `proc_LBL__ROMAN_α` — THE HOLD-UP, MEASURED

Lon: *"In roman.s, get rid of `proc_LBL__ROMAN_α` already. What is the hold up?"*

The hold-up is on record and was **awaiting exactly this ruling**. s26 HQ cursor, residue (a): the `_α_body` alias line was left standing because suppressing it for `is_lbl` means conditionally skipping a define while the jmp-entry `res` machinery sits between α and α_body in the binary medium — judged a media-divergence risk "not worth 1 cosmetic line without a ruling." The `.globl` suppression already landed (s26, `scrip.c:887`/`:1348`).

**RE-MEASURED AT HEAD (this session) — residue (b) is the real target and is still live:**

```
roman.s = 2713 lines.  LBL section (lines 4–899) = 896 lines = 33% of the file.
LBL chain emits 69 boxes; main emits 189; the LBL 69 ARE main's last 69, re-emitted with fresh uids.
```

**The whole LBL section is a duplicate.** Its only real job is to provide an entry point at label ROMAN — i.e. it should be the 2-line trampoline s26 proposed, or nothing at all.

⛔ **NOT ATTEMPTED THIS SESSION, DELIBERATELY.** The fix needs main's landing-node label name at LBL-emission time, but `uid` = emission-order counter and LBL is emitted FIRST. The cheap correct version is *emit main first, then LBL sections as trampolines* — which reorders every `.s` artifact in the tree and touches the jmp-entry `res` machinery. That is a 33%-of-file restructure; starting it with a third of the session's context left and a 93-second gate cycle is how a broken commit happens. **Recipe is above; it wants a fresh session and it is HQ/OMEGA-adjacent terrain (`scrip.c` proc loops + `emit_chain`), not the ALPHA admission cluster.**

## 8. GATE

- `.s` **318/318 byte-identical** (default OFF).
- m3 **BY SET IDENTICAL modulo `127_pat_json_keyvalue`** (281→282 PASS).
  ⛔ **That flip is the NAMED s23i env-pad flake, not a fix.** ALPHA cursor s23q item 6: 127's `.s` is byte-identical gate-on/gate-off and *anything* shifting initial rsp flips it. Adding a function changed the compiler binary's layout. **Fourth witness to that flake. No credit claimed.**
- Census cost: full 318-program sweep = **2 seconds**.

## 9. CHEAP GATES DISCOVERED (worth reusing)

`--compile` md5 over all 318 = **4s**; m3 verdict sweep = **93s**. So `.s` byte-identity is essentially free and should be run on *every* edit, not just at handoff.
