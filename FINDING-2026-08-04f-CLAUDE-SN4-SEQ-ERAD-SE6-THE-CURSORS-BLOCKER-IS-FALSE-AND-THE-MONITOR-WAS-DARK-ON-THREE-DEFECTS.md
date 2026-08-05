# FINDING 2026-08-04f — SEQ-ERAD SE-6: the LIVE CURSOR's stated blocker is FALSE, and the 2-way monitor was DARK on three independent defects

Session: Opus, HQ seat, GOAL-SNOBOL4-BB (LADDER W / SEQ-ERAD).
Start state: SCRIP `a1caa5b6`, gate 78 pass / 31 xfail / 15 XPASS / 17 REGRESSION — NOT GREEN.
End state: gate UNCHANGED 78/31/15/17. SCRIP diff = 2 lines in `src/emitter/emit.cpp`, both codegen-NEUTRAL (proved by byte-compare against pristine HEAD).

---

## ⛔ HEADLINE 1 — THE CURSOR'S BLOCKER IS FALSIFIED. DO NOT SPEND BUDGET THERE.

The LIVE CURSOR at `a1caa5b6` named the blocker as:

> *"the φ-fixup in `sno_seq_nary` uses a range-based scan `lo[i]..hi[i]` that misses tagged edges allocated by nested sub-calls (ARBNO body sequences, FENCE seam sub-runs) … N03 outputs `a a b c d` … suggesting the σ edge for the inner ARBNO body's first element resolves to ARBNO.α instead of ASSIGN_SAVE.α."*

**This is wrong.** Measured, not argued: an env-gated `SCRIP_SEQDBG` dump inside `sno_seq_nary` shows it fires **exactly once** on N03 — for the top-level spine `POS(0) ARBNO(...) RPOS(0)` — and its wiring is CORRECT (`ARBNO.ω→MATCH_POS(β)`, `RPOS.ω→ARBNO(β)`).

The ARBNO body never reaches `sno_seq_nary` at all. `--dump-ast` on N03:

```
(TT_ARBNO (TT_CAPT_IMMED_ASGN (TT_LEN (TT_ILIT 1)) (TT_VAR OUTPUT)))
```

`LEN(1) $ OUTPUT` parses as ONE `TT_CAPT_IMMED_ASGN` node, **not** a `TT_SEQ`. There is no nested sequence, no nested sentinel, and therefore no nested-allocation φ-fixup problem on N03's path. The capture-pair arm (`lower_snobol4.c:1349`) is the site, not `sno_seq_nary`.

---

## ⛔ HEADLINE 2 — ALLOCATION POLARITY IS THE OPPOSITE OF WHAT IT LOOKS LIKE

`lc_build` mints the **construct** node FIRST and the arm RETURNS the **argument** as the entry (control flows arg → construct). Ground truth from the SEQDBG dump on N03:

```
[SEQ]   i=0 lo=26 ent=27(IR_LIT_INTEGER) res=26(IR_MATCH_POS)
[SEQ]   i=1 lo=28 ent=28(IR_MATCH_ARBNO) res=28(IR_MATCH_ARBNO)
[SEQ]   i=2 lo=32 ent=33(IR_LIT_INTEGER) res=32(IR_MATCH_RPOS)
```

So `res[i] = g->all[before]` (first-allocated) **already IS** the construct node = the correct β/resume surface. `ent[i]` is the ARGUMENT.

⚠ **TRAP, MEASURED BOTH WAYS:** "fixing" this to `res[i] = ei` takes the gate from **17 → 30 regressions** (breaks ALT-backtrack A07/A08/A09/A13, ARBNO-retry N05/N06/N12/N15/N19/N21, D09, H12/H13). Reverted. `res[]` is local to `sno_seq_nary` and its ONLY consumer is `prv`; the fence path's `sno_resume_ω_to` uses its own local `r_tail`, so "keep `res[]` for the fence path, change `prv`" is a NO-OP distinction — the two edits are identical.

⚠ **READING TRAP:** `--dump-ir` is **spine-ordered, not `g->all`-ordered**. Do not read allocation order off it (cost me one false diagnosis: read `ARBNO.ω=16` when it is 15).

---

## ⛔ HEADLINE 3 — ARBNO's RESUME OPERAND IS FINE (second falsification)

Hypothesis: ARBNO's `ir_operand_push(R, ri)` with `ri = g->all[before]` picks the ASSIGN node instead of the body resume, because the capture pair mints `ASSIGN_IMM` before `SAVE` — explaining N03's doubled leading element.

**Falsified by counterexample.** N20 and N17 have the IDENTICAL shape — a capture node as operand[1] — and both PASS:

| probe | ARBNO operands | result |
|---|---|---|
| N02 | `[41,41,41]` (one-node body) | PASS |
| N20 | `[52,55,54]` resume=`ASSIGN_COND` | PASS |
| N17 | `[52,54,57]` resume=`ASSIGN_COND` | PASS |
| N03 | `[41,43,42]` resume=`ASSIGN_IMM` | FAIL |

Same shape, opposite outcomes ⇒ the operand triple is not the discriminator. A derivation-from-`ei->ω` fix was written, built, and measured: **operand list unchanged, zero effect** (SAVE's ω is the OUTWARD exhaust = R, never inside the body range). Reverted.

---

## THE REAL WORK PRODUCT — THE MONITOR WAS DARK ON THREE INDEPENDENT DEFECTS

RULES.md mandates MONITOR-FIRST. The monitor could not bracket ANYTHING: it reported `DIVERGE step 1` on **passing** programs (N02) identically to failing ones. Three separate causes, all found:

### Defect A — VALUE tracepoint dark on `scr` ✅ CAUSE FOUND (harness fix NOT yet applied)
`comm_var` (core.c:446) requires `kw_trace > 0`, set only by `SCRIP_TRACE`. The `scr` launch block in `test_monitor_3way_sync_step_auto.sh` sets `MONITOR_BIN`/`READY_PIPE`/`GO_PIPE`/`NAMES_OUT` — **but never `SCRIP_TRACE`**, even though the script's OWN header comment says the catch-all is "activated via SCRIP_TRACE/SCRIP_FTRACE only".
With `SCRIP_TRACE=99999` steps 1–2 agree BYTE-FOR-BYTE where step 2 previously diverged.
**ACTION FOR NEXT SEAT:** add `SCRIP_TRACE="${SCRIP_TRACE:-99999}"` to the `want_scr` block. One line.

### Defect B — stno base mismatch ✅ ROOT-CAUSED (not fixed)
`snobol4.y:233` — `s->stno = ++pp->prog->nstmts` — numbers only GRAMMAR-REDUCED statements.
SPITBOL (per `scripts/monitor/build_stno_map.py`'s own documented rules) increments for EVERY line except `*` comments and `-` directives — **INCLUDING BLANK LINES**.
Every probe opens with 3 comment lines + a blank, so all 169 diverge at step 1 on numbering alone, regardless of correctness. Verified: a comment-free/blank-free equivalent agrees at step 1.

### Defect C — the second LABEL carries a wrong stno ⛔ EMITTER EXONERATED, wire-side unresolved
On `nc.sno` (comment-free, 6 statements, stno == lineno 1:1 per `build_stno_map.py`): spl emits `LABEL stno=2`, scr emits `LABEL stno=6`.
**The emitter is NOT at fault.** A `SCRIP_TAPDBG` print inside `emit_mon_label_tap` shows all five taps bake CORRECTLY AND IN ORDER: `stno=1,2,3,4,5`. Statement 2 does get a tap carrying 2.
⇒ The `stno=6` is a RUNTIME/WIRE fact, not codegen. **This is where the next seat starts.**

⚠ Two of my own sub-hypotheses here were also falsified: (1) "the `IR_GOTO` tap emits spurious LABELs at wiring nodes" — gated it, **no change**, still 6; (2) "SCRIP's LABEL wire is spine-ordered vs SPITBOL source-ordered" — FALSE, the `STATEMENT_BEGIN` nodes are in correct source order and the taps bake in order.

---

## LANDED EDITS (both codegen-NEUTRAL, proved by byte-compare)

1. **`emit.cpp:858` — `op_stno` promotion restricted** to `IR_STATEMENT_BEGIN/END/STATEMENT`. It was `g_emit.op_stno = (int32_t)IR_LIT(nd).ival;` for EVERY kind — but that field is the shared payload union (LEN counts, POS offsets, ARBNO's `ival=1`, ALT arity), so `op_stno` was clobbered continuously during the walk and the tap's `op_stno > 0` guard was selecting ACCIDENTS, not statements. `op_stno` has NO other consumers (grep: only the two taps, both `MONITOR_BIN`-gated), so this is neutral outside the monitor. **A real defect independent of the monitor; keep.**
2. **`emit.cpp:991` — `IR_GOTO` label tap gated** behind `MONITOR_GOTO_TAP`. ⚠ **LON DECISION NEEDED:** RULES.md's LIVE CURSOR block explicitly calls this site "the 2-way monitor's trace anchor". It is env-gated (old behaviour = one variable) and did NOT fix defect C, so it is a candidate for reversion. Flagged, not defended.

---

## ⚠ PRE-EXISTING DEBT SURFACED: THE `.s` ARTIFACTS WERE STALE AT `a1caa5b6`

Handoff step 4 regen produced large diffs (benchmark 5 files, feature 27 files, demo 18 files). **This is NOT from this session's edits.** Proved by byte-compare at PRISTINE HEAD with my change stashed: pristine compiler emits 2463 lines for `roman.s`, the COMMITTED artifact had 2533 — they already disagreed. With my edit restored the output is byte-identical to pristine. So the previous session (which left the tree NOT GATE-GREEN) skipped step 4, and this handoff pays that debt. The artifacts are honest current output per the rule; they are NOT a gate.

---

## SCOREBOARD — FIVE HYPOTHESES, FIVE FALSIFIED BY MEASUREMENT

1. Cursor's φ-fixup/nested-allocation theory → FALSE (`sno_seq_nary` not on N03's path)
2. `res[i] = ei` resume-surface fix → FALSE (17→30 regressions, reverted)
3. ARBNO operand[1] resume theory → FALSE (N20/N17 same shape, pass)
4. `IR_GOTO` tap emits spurious LABELs → FALSE (gated, no change)
5. Tap's missing register-save bracket corrupts scanner state (r13/r14/r15) → FALSE (outputs byte-identical with/without `MONITOR_BIN`; taps sit at statement boundaries, not inside matches). **Latent hazard if that tap is ever moved inside a match region — it has no save/restore bracket around a C call.**

The lesson is the one RULES.md already states: five falsifications in one session is the price of working while the mandated instrument is dark. **Finish the monitor (defects A/B/C) before attacking the remaining 17.**
