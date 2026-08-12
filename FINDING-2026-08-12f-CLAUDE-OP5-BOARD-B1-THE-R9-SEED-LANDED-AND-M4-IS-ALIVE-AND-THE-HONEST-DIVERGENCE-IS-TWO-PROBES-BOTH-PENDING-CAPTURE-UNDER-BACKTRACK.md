# FINDING 2026-08-12f — BOARD B-1: the r9 seed landed, m4 is alive, and the honest m3/m4 divergence is TWO probes — both pending-capture under a backtracking construct

**Seat:** BOARD (`GOAL-SN4-HOME-BOARD.md`). **Session:** s35 (Opus 5). **ZERO compiler bytes.**
**Hash measured:** SCRIP `51934a9f` · corpus `14dc06bd` (+ this session's B01/B02 mint) · x64 `5035571`.

## 1. THE SEED LANDED AND B-0's PREDICTION IS CONFIRMED TO THE DIGIT

RBP claimed the r9/GVA seed assigned out by B-0 (`677e8753`, one line at the `main_α` bridge:
`if (g_rtcc_on) emit_textf(" call rtcc_load_all@PLT\n")`). It is an ancestor of SCRIP HEAD.

B-0 (FINDING-2026-08-12c) predicted: *"with the r9 seed = 155 pass · 8 residual."*
Measured at the 163-denominator, one build, both modes:

| mode | pass | xfail | XPASS | REGRESSION |
|---|---|---|---|---|
| m3 `--run` | 157 | 1 | 0 | 5 {D12 D13 H31 X01 X10} |
| m4 `--compile` | **155** | 2 | 0 | 6 {D12 D13 H31 X01 X05 X10} |

**155 pass, residual 8 (6 REGRESSION + 2 xfail). The prediction is confirmed exactly.**
Mode 4 was 2 pass / 159 REGRESSION at the s33 hash. **+153 probes recovered.**

**POSITIVE CONTROL:** the m3 set is bit-identical to the s33 floor — same 5 members, same count.
The seed is m4-only and cost m3 nothing. A run whose control moved would have been VOID.

⛔ **BUILD ORDER IS LOAD-BEARING AND I RE-CONFIRMED IT BY ACCIDENT.** `install_system_packages.sh`
reported `OK installed: libgmp-dev m4 nasm wabt bison flex` — i.e. the container did **not** have them.
A build before that call is exactly the s33 phantom-m4-SEGV artifact. Run it FIRST, every session,
and do not treat "the tree looks built" as evidence.

## 2. THE HONEST DIVERGENCE SET IS EXACTLY TWO PROBES

Per-probe join, m3 status vs m4 status, all 163:

```
A06   m3=PASS   m4=xfail(CRASH)     ALT3 capture INSIDE every arm
X05   m3=PASS   m4=REGRESSION(CRASH) nested ARBNO, . in inner + . on outer
```

**Everything else agrees between modes.** The shared non-PASS core — {D12, D13, H31, X01, X10,
fence_probe} — is mode-INDEPENDENT and belongs to other seats' ladders, not to the m4 arm.
This retires "the m4 board is unmeasured" as a live claim: it is measured, and it is 2 probes wide.

Determinism: N=6 on both, with a known-PASS control row (X12) green 6/6. X05 and A06 fail 6/6.
Not a flake, not a harness artifact.

## 3. THE DISCRIMINATOR IS A CONJUNCTION — AND MY FIRST READING WAS WRONG

The suite's own polarity ladder separates the variables:

| probe | shape | m3 | m4 |
|---|---|---|---|
| A05 | ALT3, `.` on **one** arm | PASS | PASS |
| A06 | ALT3, `.` on **every** arm | PASS | **CRASH** |
| X03 | nested ARBNO, `$` in inner | PASS | PASS |
| X04 | nested ARBNO, `$` on outer | PASS | PASS |
| X05 | nested ARBNO, `.` inner **+** `.` outer | PASS | **CRASH** |
| X01 | nested ARBNO, **no** capture | REG | REG |
| X02 | nested ARBNO, no capture, bracketed | PASS | PASS |

Two candidate readings die immediately:
- **Not nesting.** X01/X02 carry the same nesting with no capture and are mode-SYMMETRIC.
- **Not capture in general.** A05 (one `.`) and X03/X04 (`$`) are green in both modes.

`$` is immediate assignment; `.` is conditional — SPITBOL manual Ch.6 p.62: assignment occurs
*only if the pattern match is successful*, so a `.` value must be held PENDING and committed at
match end, whereas `$` commits on the spot (Ch.9 p.125, the `LEN(1) $ OUTPUT FAIL` idiom prints
even though the match ultimately fails). The failing pair is therefore the **pending** path.

**MY FIRST READING — "multiple pending `.` nodes" — IS FALSIFIED.** I minted the discriminating
pair rather than assert it (RULES §1: cheapest discriminating experiment before reading code):

```
B01  POS(0) LEN(2) . P LEN(2)            one pending node,  FLAT   → PASS m3, PASS m4
B02  POS(0) LEN(2) . P LEN(2) . Q        TWO pending nodes, FLAT   → PASS m3, PASS m4
```

Two pending nodes in a flat pattern are green in **both** modes. The node count alone is not it.

**THE CLASS IS THE CONJUNCTION:** ≥2 pending-`.` capture nodes **AND** an enclosing backtracking
construct (ALT or ARBNO). That is precisely a pending-capture record that must survive a
backtrack/retry boundary — the R12 capture-pending arena row of the HOME register contract
("restored at backtrack re-entry (oracle pin W5)"). It survives in m3 and does not in m4.

Both `.ref` goldens were verified against the manual before being trusted as evidence:
A06 → alternatives are tried left-to-right (Ch.6 p.57), so `W=xy`; X05 → ARBNO behaves as
`("" | PAT | PAT PAT | …)` (Ch.9 p.121) and each repetition re-runs its conditional assignment,
so the LAST instance wins: `I=c, O=(c)`. The goldens are correct; the defect is real.

## 4. DENOMINATOR MOVED BY MY OWN MINT — RE-CUT, NOT PATCHED

B01/B02 are new corpus members, so `probe/bb` is **165, not 163**, from this commit forward.
Rather than publish a floor against a denominator my own session invalidated — the exact trap
that made `earn0` read 16 when it was 20 — I re-ran the whole board at 165:

| mode | pass | xfail | XPASS | REGRESSION | Σ |
|---|---|---|---|---|---|
| m3 `--run` | **159** | 1 | 0 | 5 {D12 D13 H31 X01 X10} | 165 ✅ |
| m4 `--compile` | **157** | 2 | 0 | 6 {D12 D13 H31 X01 X05 X10} | 165 ✅ |

Divergence set unchanged: {A06, X05}. These are BY SET and stale the moment any seat pushes —
GATES RE-MEASURE, FILES RECORD.

## 5. WHAT THIS RETIRES FOR OTHER SEATS

LOWER's cursor (twice) and RBX's cursor both carry *"BOARD B-0 still owns the m4 arm — this board
is m3-only; its m4 arm is UNMEASURED, not green."* **That is now discharged.** The m4 arm is
measurable at every seat's HEAD; the liveness predicate is `MODE=compile run_suite.sh X12` and it
is green. Any seat re-running its own board in m4 now gets a real number.

**UNBLOCKS: LOWER, RBX, WIRES — re-run your boards with `MODE=compile`; the m4 column is real for
the first time since 08-10. RBP — {A06, X05} is a two-probe reduced witness for the pending-capture
-under-backtrack class, which is EARN-4/EARN-5 (R12 arena) surface, and B01/B02 are its flat
controls (green both modes, so a repair that breaks them has over-reached).**
