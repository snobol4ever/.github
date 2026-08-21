# FINDING — s189 (seat6) · THE ALT'S CHOICE RECORD IS ADDRESSED OFF THE **LIVE RSP**, SO ANY ARM-INTERIOR CARVE MOVES IT — AND THE CURE IS ALREADY BUILT, ALREADY DOCUMENTED "DEPTH-IMMUNE", AND ADMITTED FOR EXACTLY THE SHAPES THAT DO NOT NEED IT

**Row:** `alt-resume-carrier-selection` (QUEUE rank 1). **Disposition: INVESTIGATION-ONLY, MECHANISM NAMED** — the row's own
else-branch fires, and it fires on a MEASUREMENT: the row's "if killswitch-clean" test comes back **negative**. No existing
killswitch reaches any of the four witnesses (§5). Lon ruled investigation-only in-chat this session.

**Tree:** SCRIP `3dc52576` · corpus `7aa87e81` · `make pristine` EXIT=0, RT_OPT `-O0` (O0-DEV). **NO FILE TOUCHED** — tree clean
at handoff; this rung is measurement only.

---

## 1. ⛔ THE ROW'S SUSPECT ROAD IS FALSIFIED — THE CARRIER PUBLISHER IS NOT THE SITE

The brief names `sno_pat_carrier_build` / `sno_pat_publish_body_root` and asserts the fix is that the publisher "must publish the
arm's RESUMABLE node (the inner alternation), not the arm head." **Both halves are wrong, and the second is backwards.**

`SCRIP_RESUME_WHY=1` on the primary and on its GREEN barer twin print the **same carrier**:

```
twin    ( 'a' | 'aa' )                  GREEN   rn=1 brt=0 body_root_op=54 tier=0 n=3
primary ( 'a' ('b'|epsilon) | 'aa' )    RED     rn=1 brt=0 body_root_op=54 tier=0 n=7
```

Op 54 is `IR_MATCH_ALTERNATE` — **the OUTER alternation, in both.** A green case and a red case that publish an identical carrier
cannot be discriminated by carrier selection. And the brief's proposed cure — publish the inner alternation — would publish the
**exhausted** node: the inner alternation is precisely the thing that has nothing left to offer. ⭐ Two further controls confirm
the publisher is inert here: `( 'a' 'b' | 'aa' )` and `( 'aa' | 'a' ('b'|epsilon) )` are GREEN with the same `body_root_op=54`.

## 2. ⭐⭐⭐ THE MECHANISM, READ OUT OF THE EMITTED ASM (ASM-DIFF-FIRST, step 2 — no gdb needed)

`bb_match_alternate` carves a **32-byte choice record on the spine** at α and addresses it as a fixed offset from the **live
rsp**: `[rsp+0]` saved cursor · `[rsp+8]` β re-entry into the arm that succeeded · `[rsp+16]` next-arm continuation.

**The twin never moves rsp inside an arm, so those spellings are correct.** (Its arms are bare literals; on this shape the
locals even land in the flat rbp frame — `[rbp-56]/[rbp-64]/[rbp-72]`.)

**The primary moves rsp inside arm 1, and the outer box's own handlers then read someone else's 32 bytes:**

```
n0_match_alternate_α:   sub rsp, 32          <- OUTER record carved
                        mov [rsp+16], .Lx8_21 ;  jmp n3_match_lit_α        (arm 1 = 'a')
n3_match_lit_α:         ... add r14d,1 ;      jmp n4_match_alternate_α     (arm 1's tail = INNER alt)
n4_match_alternate_α:   sub rsp, 32          <- INNER record carved; rsp now 32 LOWER
n4_match_alternate_as:                       jmp n0_match_alternate_s0     <- ⛔ NO `add rsp,32`
n0_match_alternate_s0:  mov [rsp+8], .Lx8_40 <- ⛔ OUTER's β-resume WRITTEN INTO THE INNER RECORD
n0_match_alternate_β:   mov rax,[rsp+8] ; jmp rax      <- external β reads the INNER record
n0_match_alternate_af:  mov r14d,[rsp+0] ; jmp [rsp+16] <- and the INNER cursor / INNER next-arm
```

The inner alternation deliberately does **not** pop on the success path (β may need to re-enter it — only its all-arms-exhausted
exit `.Lx15_19` does `add rsp,32`). That is correct for the inner box and fatal for the outer one: **a box's state address is
computed from the live rsp, but the box's own cell is wherever rsp was when IT carved.** Every arm-interior carve silently
re-points the enclosing ALT's record.

## 3. THE PREDICTION THE MECHANISM MAKES, AND THE MEASUREMENT (subject `'aa'`, anchored, stored)

If the defect is "arm 1 succeeds while holding a carve", then arm 1 succeeding **with** a carve must be red and **without** one
green, regardless of which box does the carving:

| pattern | arm 1's tail carves? | oracle | SCRIP |
|---|---|---|---|
| `( 'a' POS(1) \| 'aa' )` | no | match | **match** |
| `( 'a' LEN(0) \| 'aa' )` | no | match | **match** |
| `( 'a' RTAB(1) \| 'aa' )` | no | match | **match** |
| `( 'a' ('b'\|epsilon) \| 'aa' )` | **yes** (32B inner ALT record) | match | **nomatch** |
| `( 'a' ARBNO('z') \| 'aa' )` | **yes** | match | ⛔ **SIGSEGV rc=139** |

⭐ **THE SIGSEGV IS THE SAME DEFECT, NOT A SECOND ONE** — `n0_match_alternate_β` does `jmp [rsp+8]`, so a record read at the wrong
depth is an **indirect jump through a foreign 8 bytes**. Wrong answer and wild jump are the benign and malignant faces of one
mechanism, which is why this class produces both.

## 4. ⛔ THE ROW IS TWO CLASSES, NOT THREE-PLUS-A-CANDIDATE — AND THE 4th JOINS THE *OTHER* ONE

The brief brackets three witnesses as one class and offers `rseal_unsealed_ctl` as a candidate 4th. `SCRIP_FENCE_IGNORE=1`
splits them **2/2**, and the split disagrees with the bracketing (it agrees with the witnesses' own headers):

| witness | default | `FENCE_IGNORE=1` | class |
|---|---|---|---|
| `ptw_min_alttop_nofence_ctl` | nomatch | **nomatch** | **IN** — rsp-depth (this FINDING). Fence-free; publishes a carrier (`rn=1`). |
| `ptw_min_fence_alttop` | nomatch | **nomatch** | **IN** — rsp-depth, with the s182 fence refusal stacked ON TOP (`RESUME-NIL`, `pfenced=1`); remove the fence verdict and the depth defect is what is left. |
| `ptw_min_fence_left_altresume` | nomatch | **match** | **OUT** — pure s182/s121 fence refusal. Not this class. |
| `ptw_min_rseal_unsealed_ctl` | nomatch | **match** | **OUT** — pure fence refusal (`fb=IR_MATCH_DEFER fbtier=2`). **Classified OUT with evidence, as the row asked.** |

⛔ **So the row's own primary is the ONLY fence-free member**, and two of its four witnesses belong to a class that already has a
disposition. A seat that "fixes the three together" would be chasing two mechanisms with one cure.

## 5. ⭐⭐⭐ THE CURE IS ALREADY BUILT — AND ITS ADMISSION EXCLUDES EXACTLY THESE SHAPES

`bb_match_alternate.cpp:38` documents `sn4_choice_rbp_off()`: the choice record moved off the rsp frontier into the blob's
activation frame at a **negative rbp base**, so *"every spelling below is **depth-immune under arm-interior carves**"* — this
defect, named in the tree, with a cure already written. `emit.cpp:67` shows the carve is conditional: `IF(!cro, x86("sub","rsp",32L))`.

Its admission `blob_choice_rbp_scan` (`emit.cpp:2488`) is:

```c
if (_nc != 1 || _fn) return 0;      /* _nc = count of ALTERNATE/DISJUNCTION; _fn = any FENCE */
```

**All four witnesses fall in the two refused classes**, and the refusals are documented decisions, not oversights: `_nc>1` is
*"the refused two-record-composition class (s126)"* and `_fn` is *"the FENCE semantic refusal (manual p.125/p.204)"*.
- `ptw_min_alttop_nofence_ctl` → `_nc=2` (outer + inner) → refused by `_nc != 1`.
- the other three → `_fn=1` → refused by `_fn`.

**MEASURED, both directions:** `SCRIP_CHOICE_RBP=1` and `=0` leave **all four unchanged at `nomatch`** — the scan refuses before
the killswitch is consulted. The single-choice twin, the one shape the cure DOES admit, is green. **That is the row's
"killswitch-clean" test, and it is negative: there is no switch that cures these, so investigation-only is the correct branch.**

## 6. WHAT A CURING RUNG MUST ACTUALLY DECIDE (not a predicate edit)

Widening `blob_choice_rbp_scan` is **not** a one-line admission change, and it must not become one:
- `_nc>1` was refused because **two choice records must compose** in one blob frame. The rbp-resident record is a single 32B slot
  carved by `blob_frame_bytes`; admitting two means the frame must carry (and the template must address) **one record per choice
  node**. That is the real work the s126 refusal is standing in front of.
- ⛔ **NO-PER-OP-FILTER (Lon, 2026-08-20) binds here.** The cure must be a property of the ALT box family — *a choice record is
  addressed relative to the record, never to the live rsp* — never an admission list of blessed shapes. The present predicate is
  already close to the shape that rule forbids; widening it shape-by-shape would walk straight into it.
- The honest alternative is to make the **legacy rsp-carved path depth-correct** (the arm's exit re-seats rsp, or the enclosing
  handlers address through a saved base like `n3_match_fence1_β`'s `mov rsp,[rbp-48]` already does) rather than to grow the
  rbp-resident exception.

## 7. GATES

`make pristine` EXIT=0 · **no file touched, both trees clean** · barer twin `( 'a' | 'aa' )` GREEN · **ptc3 grid 8/8 GREEN** ·
corpus board **m3 332/5 · m4 325/11 · SKIP 1 (337)**, fail-set identical **by name** · `.ref`s of all four witnesses re-derived
from the LIVE oracle and identical under **both** `sbl -b` and `-bf` (the rank-0 folding hazard does not touch them) · ⛔ the
SNOBOL4 scorecard was NOT run (it executes `corpus/programs/lon/`, which RULES.md forbids).

## 8. CROSS-REFERENCE — THIS IS THE SAME WALL AS THIS SESSION'S OTHER ROW

seat6's `fuzz-diff-batch` FINDING (same session) reduced five fuzzer wrong-answers to *"a retreat that must cross an ALTERNATE
boundary to reach a generator that still has alternatives"* and split them D-1/D-2 by inline-vs-stored. **This FINDING names the
byte-level mechanism behind that description**, and the two agree on a detail neither needed the other to see: the class produces
**both** silent wrong answers and SIGSEGVs (`fuzz-diff-batch` D-2 inline SIGSEGV; here `( 'a' ARBNO('z') | 'aa' )`), which §3
explains as one mechanism seen through `jmp [rsp+8]`. The standing corpus witness for the class remains
`crosscheck/patterns/160_pat_alt_inner_gen_resume` (`'aXb' ? ('a' ARB . V | 'q') 'b'`, SIGSEGV rc=139 both modes) — a curing rung
should turn it green.
