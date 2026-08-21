# FINDING s191 (HQ, beauty lane) — ⭐⭐⭐ A FAILING GUARD COULD NOT SHORT-CIRCUIT THE OPERAND IT GUARDS: THE PATTERN PRE-CHAIN RAN BACKWARDS, AND IT WAS BEAUTY'S FIRST WALL

**Date:** 2026-08-20 · **SCRIP `008c2264`** (fix) · **corpus `d901e0f2`** (witnesses) · `make pristine`, RT_OPT `-O0` · oracle live `sbl -bf`.
**Lon, in-chat:** *"I want you to take over BEAUTY SELF HOST after the FLEET finished the one bug. Let's get it 100%."* The fleet finished it (seat3's computed-goto cure; `216_indirect_goto_computed` green, independently corroborated by seat5's 318-program census as *the only row of 318 that moved*). This is the first rung of the HQ-owned lane after that handover.

## 1 · THE LADDER MOVED — 3/10 → 5/10, FIRST RED 10 → 40

`board_beauty_m1.sh --modes m3`, pristine both readings. The 10- and 20-line rungs went red→green.

## 2 · THE WITNESS, SEVEN LINES

```
        A = 0
        'abcdef'       GT(A, 0) LEN(A - 10) . ind          :S(M)F(NM)
```
**Oracle:** `nomatch` — evaluation is left-to-right, `GT(0,0)` FAILS, the statement fails, **`LEN` is never evaluated**.
**SCRIP (pre-fix):** `** Error 121 — len argument is negative or too large`, fatal.

**Beauty is this shape verbatim.** `Gen.inc:42`:
```
indent   GT($'#L', 0) LEN($'#L' - SIZE($'$X')) . ind
```
The guard exists *precisely* to keep the LEN argument non-negative. Feeding beauty the single line `START` went `** Error 121` → `START`, the oracle's answer exactly.

## 3 · ROOT CAUSE — AND THE COMMENT ABOVE THE LOOP WAS THE TELL

`lower_snobol4.c`, the OPERAND-EDGE HOIST drain. Each entry is built with `after` as its **continuation**, so the chain **executes in reverse loop order**. The header asserts:

> *"Chains splice between the subject chain and head; SEQ lowers right-first so forward iteration here yields left-to-right construction order."*

**That premise is false at this HEAD, and the IR proves it.** For `GT(A,0) LEN(A-10)`:
```
15-17  VAR A · LIT 10 · BINOP      ← LEN's argument
18     COERCE_INTEGER              ← ⛔ Error 121 raised HERE
19-23  VAR A · LIT 0 · CMP_TEST    ← the GT guard, evaluated SECOND
```
Manual **p.85–86**: primitive arguments are captured at pattern **construction**, left to right, and a failure **aborts the statement**. The ω edges were already correct — every hoisted node routes failure to the statement's fail exit — so **only the order was wrong**, which is why the cure is one loop direction behind a killswitch (`SCRIP_PRE_ORDER`, default ON; `=0` restores the defect exactly).

⭐ **This is the third instance this campaign of the same species: a candid comment recording an assumption, which later became false, and was thereafter read as a ruling** (s180's *"ASSIGN_IMM stays 0: unmeasured"*, s187's `dtx_used` cap, and now this). The comment is now corrected in place rather than deleted, so the false premise cannot be re-derived.

## 4 · THE MIRROR-IMAGE WITNESS — ONE ROOT CAUSE, TWO OPPOSITE WRONG ANSWERS

`probe/preord/pre_unsafe_then_guard` writes the unsafe `LEN` **first**:
- **Oracle:** ERROR 121 (it evaluates left-to-right and reaches the bad LEN).
- **SCRIP pre-fix:** `nomatch` — it evaluated the guard first, failed cleanly, and **never errored**.

So the same defect produced a spurious fatal error in one direction and a spuriously clean answer in the other. Post-fix both engines error. ⛔ **That witness deliberately carries NO `.ref`:** the residual difference is the two engines' error-*text* format (SPITBOL prints a `file(line)` banner plus a dump; SCRIP prints `** Error N in statement M`), a separate global divergence that must not be silently pinned into a corpus ref (seat2's s191 vacuous-pin lesson).

## 5 · RECEIPTS

Corpus board **m3 333/4 · m4 326/10 SKIP 1**, fail-set **IDENTICAL** armed vs `SCRIP_PRE_ORDER=0`. ⭐ The board's +1 versus the previous reading is **seat3's `216_indirect_goto_computed` cure, not this rung** — attributed by diffing the fail lists, not assumed. Smoke **7/7 both modes**. Regens benchmark/feature/demo/programs: **ZERO `.s` movers**, corpus tree clean. Killswitch proven **non-vacuous** on two witnesses (`nomatch` vs `Error 121`; beauty `START` vs `Error 121`). Six witnesses at `corpus/probe/preord/` (5 oracle-refed green, 1 documented-unrefed).

## 6 · THE NEXT WALL, ALREADY LOCATED (not yet cured)

A real statement (`L       X = 1`) still SIGSEGVs at the 40-line rung, **jumping into `rtccb`** — the RTCC register bank, a *data* symbol. The ZSM ring (with the s189 `st=` column) names the trail: `Shift`/`Reduce` (`ShiftReduce.inc`, both `:(NRETURN)`) → `PopCounter` (`counter.inc:26`, `:(NRETURN)`) → `TopCounter` (`counter.inc:27`, `:F(FRETURN)`) → wild jump. **Killswitch sweep, 12 knobs: only `SCRIP_RTSEQ_RESUME=0` moves it**, and it moves it *backwards* to the pre-s183 `Parse Error` — so this wall sits strictly **downstream** of the composed-pattern resume cure and is reached only because beauty now gets further. ⛔ Standalone construction of the shape (three attempts: FRETURN-on-failure, plain DIFFER failure, guarded OUTPUT with `:(RETURN)`) **all pass** — beauty's include context is load-bearing, exactly as the `m1-composed-wild-jump` row warns after HQ failed nine times. Reduce DOWNWARD with `util_beauty_override.sh`, never build up.
