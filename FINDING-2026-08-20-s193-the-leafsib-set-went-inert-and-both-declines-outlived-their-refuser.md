# FINDING — s193 (seat1) · THE ROW'S CURE ALREADY LANDED; THE WITNESS SET THAT SHOULD HAVE SAID SO WENT **INERT**, AND BOTH "DECLINED BY DESIGN" REFUSALS OUTLIVED THE FUNCTION THAT MADE THEM

**Row:** `alt-arb-bal-witness` (QUEUE rank 24). **Disposition: WITNESSES MINTED + CLASS RE-DATED — NO COMPILER FIX,
AND THE ROW'S OWN `fix ONLY if killswitch-clean` BRANCH IS WHY.** The class the row exists to pin is **already cured on
the shipped default**; the three repairs this rung landed are a harness label, a stale code comment and a README, all
proven inert (0 `.s` movers / 40).

**Tree:** measured at SCRIP `408aab34` · corpus `f7ce61c3`; ⭐ **RE-PROVED IN FULL AT SCRIP `c52f3529` / corpus
`fba29912` AFTER REBASING ONTO seat6's CONST-NEST FLIP (`c512089a`), WHICH LANDED MID-RUNG ON THIS CLASS'S OWN
TERRITORY** — `lower_snobol4.c:1327` records that arming `SCRIP_CONST_NEST` was *blocked on* `SCRIP_SPAN_FRAME`
precisely because lifting the limit *"turns an ALT arm's `IR_MATCH_DEFER` into a scratch-cell leaf, which re-arms the
s130/s131 LEAF-SUSPENSION class"*. **Everything below re-measured IDENTICAL**: instrument 12/12 default · 10/12 under
`=0`, the eight originals still 8/8 byte-identical across the arms, the four padded still DIFFER across them, board
unchanged, both gates green. `make pristine` **EXIT=0 three times** (pre-edit, post-edit, post-rebase), RT_OPT `-O0`
(O0-DEV). Oracle `x64/bin/sbl -bf` present and used for every `.ref`.

---

## 1. ⛔ THE ROW'S PREMISE IS HALF TRUE, AND THE FALSE HALF DIED THREE SESSIONS BEFORE THE ROW WAS PICKED

The brief (seat8, s170): *"an ALT arm holding ARB or BAL takes the same wild write and `leaf_frame_candidate` REFUSES
both, so `SCRIP_SPAN_FRAME` cannot cure it on either arm."*

| half | verdict at `408aab34` | evidence |
|---|---|---|
| an ALT arm holding ARB or BAL takes the same wild write | ⭐ **TRUE** | `leafsib_{arb,bal}_flat_red`, `SPAN_FRAME=0`: m4 **rc=139** |
| `leaf_frame_candidate` REFUSES both | ⛔ **THE FUNCTION DOES NOT EXIST** | deleted s174, `44b8b82c` |
| `SCRIP_SPAN_FRAME` cannot cure it on either arm | ⛔ **FALSE — IT CURES BOTH** | `=1`: pass, both ops, **both media** |

Two landings between the brief and the pick dissolved the refusal:

- **s174 `44b8b82c`** — Lon's NO-PER-OP-FILTER ruling deleted `leaf_frame_candidate` outright. `leaf_frame_member()` is
  now **location-only** (`zdp_scratch_cell(nd) && ((sn4_span_frame() && alt_arm_member(nd,0)) || …)`), `zdp_scratch_cell`
  names ARB and BAL as ordinary members of the retreat-scanning leaf family, and **every leaf claims two consecutive
  16B registry slots**.
- **s188 `d3251f23`** — `SCRIP_SPAN_FRAME` flipped **default ON**. The cure is not merely available; it is what ships.

## 2. ⛔⭐⭐⭐ THE WITNESS SET BUILT FOR EXACTLY THIS CLASS IS INERT — ALL EIGHT, BOTH ARMS, BYTE-IDENTICAL

`probe/leafsib/` is eight witnesses, one per member of the scratch-cell leaf family, built at s131 to measure this
killswitch. At HEAD it reads **8/8 m3 · 8/8 m4 under `SPAN_FRAME=0` AND under `=1`** — and the reason is not that the
arms agree about the class:

```
span tab rtab rem arb bal break breakx   --compile output, SPAN_FRAME=0 vs =1:   8 / 8  IDENTICAL
```

**The set cannot see the mechanism it was built for.** It would report 8/8 GREEN straight through a full regression.

⭐ **THE CAUSE IS THE ROAD, NOT THE SWITCH.** All eight take the **STORED** road (`t = ('zz' . K | ARB . I)`), and on
the stored road the cell is *already* rbp-resident by **blob-frame** authority — independent of `leaf_frame_member`:

```
leafsib_arb, SCRIP_SPAN_FRAME=0 :   n2_match_arb_α:  mov dword ptr [rbp + -96], 0        <- ALREADY FRAMED
```

They are green for a reason unrelated to the switch they exist to test. s131 observed this of `arb`/`bal` alone and
filed it as a *decline*; it is now true of all eight, and a decline is not the same thing as an instrument that has
stopped measuring.

## 3. ⛔ AND THE INSTRUMENT WAS PRINTING AN **OFF LABEL OVER ON-ARM NUMBERS** FOR FIVE SESSIONS

`sn4_span_frame()` is `(e && *e == '0') ? 0 : 1` — **unset is ON**. `probe_leafsib_measure.sh:12` read
`ARM="${SCRIP_SPAN_FRAME:-0}"`, correct when written at s131 (default OFF) and **false from s188 onward**. Every
default-arm run since the flip printed `=== leafsib SCRIP_SPAN_FRAME=0 ===` above numbers measured with it **ON**.

This is line 590 of `GOAL-SNOBOL4-100.md` recurring verbatim — *"a killswitch outlives its arm, and the gates that
grade it keep scoring for years"* — one rung after that lesson was written down. **A flipped default silently
re-labels every instrument that hardcoded the old one**, and nothing goes red, because a label is not graded.

Repaired: the label is now **computed from the same rule the compiler uses**, never typed.

## 4. ⭐⭐⭐ THE MECHANISM, READ OUT OF THE EMITTED ASM (ASM-DIFF-FIRST step 2 — no gdb)

`leafsib_arb_flat_red`, `--compile`, `SPAN_FRAME=0` vs `=1`:

```
-                        sub  rsp, 24                              +                        sub  rsp, 56
- .Lx222_13:  lea  rsp, [rbp + -56]   # retry_whack                + .Lx222_13:  lea  rsp, [rbp + -88]   # retry_whack
- n89_match_arb_α:  mov  dword ptr [rsp + 480], 0                  + n89_match_arb_α:  mov  dword ptr [rbp + -80], 0
- n88_match_span_β: mov  r14d, dword ptr [rsp + 500]               + n88_match_span_β: mov  r14d, dword ptr [rbp + -108]
```

and `leafsib_bal_flat_red` the same, with BAL's **three** words visible:

```
- n89_match_bal_α:  mov  dword ptr [rsp + 464], 0 ; [rsp + 468] ; [rsp + 472]      + [rbp + -80]
```

`+32` on the carve is exactly the **two consecutive 16B slots** s174 granted every leaf, and `retry_whack` moves with
it. On the OFF arm the cell is a raw flat ZLS coordinate off the live rsp; the padding pushes it past the live frame
and the box writes above the stack.

⭐ **THE PAIR IS THE PROOF, AND IT IS A PROOF ABOUT MAGNITUDE, NOT ABOUT ARB OR BAL.** Within each pair the pattern is
identical and only the padding count differs:

| witness | cell, `SPAN_FRAME=0` | `=0` | `=1` |
|---|---|---|---|
| `leafsib_arb_flat_red` (20 pads) | `[rsp+480]` — **past** the live frame | m3 pass / **m4 rc=139** | pass both |
| `leafsib_arb_flat_grn` (5 pads) | `[rsp+240]` — inside it | pass both | pass both |
| `leafsib_bal_flat_red` (20 pads) | `[rsp+464]/+468/+472` — **past** it | m3 pass / **m4 rc=139** | pass both |
| `leafsib_bal_flat_grn` (5 pads) | `[rsp+224]` — inside it | pass both | pass both |

**A green on the OFF arm is luck, not correctness** — the same statement one padding assignment later is a SIGSEGV.

⛔ **THE m3/m4 ASYMMETRY IS NAMED, NOT ROOT-CAUSED HERE.** On the OFF arm m3 passes while m4 dies. m3 ≡ m4 is a design
invariant about *emitted code*, and it is not violated: what differs is what occupies the overshot address in the two
processes. This reproduces the s170 asymmetry on the SPAN witness (`cn_alt_leaf_flat_red`, *"default arm m3 PASS / m4
rc=139"*) exactly; this rung measured it and did not chase it, because it exists only on a killswitch arm.

## 5. THE MANUAL IS WHY ARB AND BAL ARE IN THIS FAMILY AT ALL

SPITBOL v3.7 **p.207**: *"patterns such as ARB and BAL have implicit alternatives which are tried before your explicit
ones. ARB behaves as if it were `(LEN(0) | LEN(1) | LEN(2) | LEN(3) | …)`"*, and (p.124/p.203) BAL matches the
**shortest** non-null balanced string, extending likewise. That extension is precisely a **β that resumes an advancing
scan through a suspension cursor** — `zdp_scratch_cell`'s behavioural definition — so ARB and BAL are members by
semantics, not by an admission list. ⭐ The manual's own worked example (p.207) is **`'ABCDEF' ? 'A' (ARB | 'D') 'E'`**:
this row's shape, an ARB on an ALT arm, is the example the manual uses to teach the feature.

The four `.ref` are minted from the **live** oracle through `util_ref_mint.sh` → `scorecard_snobol4.sh oracle`, the
same door the board grades through; all four classified `LIVE`, all four `match`.

## 6. BOTH s131 DECLINES ARE DEAD, AND EACH DIED A DIFFERENT DEATH

- **`leafsib_bal`** — *"BAL spends `+0/+4/+8` and `d=8` is the neighbour's granule floor."* The **spend is still real**
  (§4 shows all three words). The **law that made it a refusal is gone**: the 8-byte usable-window law died at s174 and
  every leaf now claims 32B, so BAL's third word is inside its own claim and there is no neighbour to rob.
- **`leafsib_arb`** — *"a DIFFERENT DEFECT CLASS … the match FAILS OUTRIGHT, so ARB never resumes … its cell is never
  re-entered."* True of **that witness**, false of the op: on the inline road the cell is re-entered on every implicit
  alternative, and `leafsib_arb_flat_red` crashes through exactly that resume.
- ⛔ Both declines name `leaf_frame_candidate` as the refuser. **It has not existed since s174.** A decline whose
  refuser has been deleted cannot be re-checked by reading it — only by measuring.

## 7. WHAT LANDED, AND WHAT DELIBERATELY DID NOT

**Landed (all killswitch-clean, blast radius measured):**
1. `corpus/probe/leafsib/leafsib_{arb,bal}_flat_{red,grn}.sno` + live-oracle `.ref` — the row's deliverable.
2. `scripts/probe_leafsib_measure.sh` — arm label **computed** from `sn4_span_frame()`'s rule; the four padded
   witnesses added to the default sibling set. The instrument now reads **12/12 default · 10/12 under `=0`**: it
   discriminates the arms again.
3. `src/emitter/emit.cpp:1710` — the staging comment claiming *"BAL SELF-REFUSES INSIDE `leaf_frame_member()`"*
   replaced with the measured truth. **Comment-only, and proven so: 0 movers / 40 comparable `.s`** across the pristine
   rebuild (20 programs × both arms).
4. `corpus/probe/leafsib/README.md` — the s131 table, the two declines and the run line re-dated.

**Not done, on purpose:** no compiler change. The row's `fix ONLY if killswitch-clean` test resolves to *nothing to
fix* — the class is cured at the shipped default, and the OFF arm is the documented legacy revert. Widening anything
to make the OFF arm green would be arming a killswitch's dead side.

⛔ **NOT CLAIMED:** this rung does **not** cure `probe/cn/cn_alt_leaf_flat_red` or `cn_alt_leaf_lit_red` — they are
**already** green at the default and red only under `=0`, measured here as controls, and they were not mine.

## 8. GATES

`make pristine` **EXIT=0 three times** · `test_gate_emit_no_lang.sh` **OK** · BOTH-MEDIUM ratchet **0 (ceiling 0)** ·
`.s` A/B across the only source edit **0 movers / 40** · all six RULES step-4 regens **`changed=0`** (623 + 484 + 22
programs) · four `.ref` minted `LIVE` through the board's own oracle door · oracle present and exercised (`sbl -bf`) ·
**no new global, no new killswitch, no template touched, no opcode added** · broad corpus **m3 335/2 · m4 328/8 SKIP 1**
= seat3's s192 watermark exactly, **measured twice — before and after the rebase — fail-set identical by name**.

## 9. ⭐ GENERALISABLE

**A witness set is not evidence that a class is watched — it is evidence only while it still discriminates the arms.**
The cheap, mechanical test is the one this rung ran first: *diff the emitted code across the two arms*. Eight witnesses
byte-identical across the killswitch they exist to test is a dead instrument, and it fails **green**, which is the
direction nobody audits. Run it whenever a killswitch flips default — and flip the instrument's label in the **same
commit**, because a hardcoded `:-0` becomes a lie the moment the default moves.
