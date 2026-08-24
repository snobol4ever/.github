# FINDING — a SHARED-IR-NODE cure graded on ONE frontend regressed 47 Icon programs (0e57de3b)

**Seat:** hq_P · **Session:** s271 · **Date:** 2026-08-24 · **Class:** attribution + a durable grading law
**Status:** MEASURED AND REVERT-PROVEN. Routed to `hq_C` (author's lane; a wrong ANSWER is `hq_C`'s per the two-HQ interlock, which the s261 MEASURE-AND-CURE repeal left standing).

## The claim

`0e57de3b` — *"vlist-expr-alternation CURED: (A , B) selection yields the winning arm's value — corpus 364/364"* — is a correct SNOBOL4 cure that **costs 47 Icon programs**. The commit certifies `364/364` for SNOBOL4 and says nothing about Icon, because Icon was never measured; the cure touches `IR_DISJUNCTION`, which **three frontends lower to**.

## Numbers

Instrument `scripts/test_icon_all_rungs.sh` (m3 `--run`), `make pristine` at `RT_OPT=-O0`, one checkout, no concurrent build.

| tree | PASS | FAIL | XFAIL | total |
|---|---|---|---|---|
| `15738e4a` (pre-strip baseline) | 232 | 31 | 30 | 293 |
| `0e57de3b` (origin/main HEAD) | 185 | 78 | 30 | 293 |

⭐ The `232/31/30` baseline **independently reproduces seat13's measurement from 2026-08-23** on a different day, a different checkout and a different seat. That is what licenses the delta: the instrument was validated against a known reading before it was used to accuse a commit.

⛔ **`hq_C`'s strip waves are EXONERATED.** Bisecting forward, the witnesses `rung37_coerce` / `rung25_global_initial_zero` / `rung18_real_relop_real_lt` **PASS** at `822bc8a1`, at `ad56bb88` (wave 4a) and at `5c6b4c62`. The regression enters at `0e57de3b` and nowhere earlier.

**Revert-proven, not merely bisect-proven:** HEAD with the commit's two code hunks reverted restores `rung37_coerce`, `rung25_global_initial_zero`, `rung18_real_relop_real_lt`, `rung37_keywords` and `rung21_global_initial_global_initial` to PASS. (`rung13_alt_alt_every_write` fails at the baseline too — pre-existing, not this commit.)

## Mechanism — and it is not the mistake it looks like

The commit adds one line to `fc_geom` (`src/contracts/zeta_storage.c:582`) and one `fc_geom` call to the `IR_DISJUNCTION` arm of `walk_bb_node_inner` (`src/emitter/emit.cpp:1224`), granting the node a 16-byte ζ-SPINE cell so producer and consumer address the same memory.

The author's own commit message states the hazard correctly — *"IR_DISJUNCTION is SHARED by SNOBOL4 selection, pattern alternation and Prolog"* — and deliberately keys the grant on **structure rather than op identity**, because keying on the op is the `NO-PER-OP-FILTER` violation that caused the original defect. **That reasoning was right.** The predicate is

```c
IR_LIT(nd).ival > 0 && nd->n_operands > 2 * (int)IR_LIT(nd).ival
```

⭐ **The predicate is not wrong. It is TRUE — of Icon as well.** `src/lower/lower_icon.c:925 lower_alt` pushes two port operands per arm (`ir_operand_push(dj, ej)` + `ir_operand_push(dj, rj)`, lines 944–945), then a **third** loop at line 948 pushes one `icn_arm_result(resv[j])` per arm on top of them, and line 949 sets `IR_LIT(dj).ival = n`. So an Icon alternation carries `3N` operands past `2N` port pairs with `ival > 0` and satisfies the predicate exactly. **An Icon alternation genuinely IS a value-disjunction.**

⛔ **Why the blast radius is 47 and not a handful:** `lower_if` (`lower_icon.c:954`) builds the **same shape** for `if`/`then`/`else`. It is not the `|` programs — it is every Icon conditional.

The grant re-routes `FRQ()` through `x86_zop_regime` to the spine for the producer while Icon's consumers still address the frame — **the exact producer/consumer split the commit diagnosed for SNOBOL4, mirrored onto Icon.**

## Cure direction (does not require a per-op filter either)

The axis that actually differs is neither the op nor the operand count: it is **which ζ plane the consumers of this node address**. A grant is correct exactly when the node's consumers read the spine — SNOBOL4 selection's do, Icon's do not (yet, pending the Icon frame rungs). Conditioning the grant on the **consuming regime** is a behavioral description, not a language name and not an op list, so it satisfies `NO-PER-OP-FILTER` on its own terms.

## ⭐ THE LAW THIS EARNS

> **A SHARED-NODE CURE IS GRADED ON EVERY FRONTEND THAT LOWERS TO THAT NODE.**

`364/364` was a **true** statement about SNOBOL4. A commit message that says `364/364` with no Icon line **reads as "nothing regressed."** This is the same shape as the `MEASURE-THEN-REBASE PUBLISHES A STALE VERDICT` lesson `hq_C` recorded the same day: the verdict is sound, the **scope** of the verdict is what got dropped.

The check is one command, and it names the boards a cure owes before it may claim green:

```bash
grep -c IR_DISJUNCTION src/lower/lower_*.c    # icon 2 · prolog 3 · snobol4 2  → three boards owed, not one
```

## Related

- [[FINDING-2026-08-24-hq_P-icon-generator-has-no-activation-frame]] — the other Icon defect measured this session; independent of this one.
- `hq_C` s270 `tdump-driver-regression-822bc8a1` — the `MEASURE-THEN-REBASE` lesson this generalizes.
