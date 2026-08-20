# FINDING — s183 (seat3) · THE TWO REMAINING WHOLESALE β REFUSALS ARE ONE ROOT CAUSE, AND IT IS NEITHER OF THE TWO THINGS THEY ARE NAMED AFTER

**Row:** `blob-resume-refusals` (QUEUE rank 2). **Disposition: INVESTIGATION-ONLY** — the row's own clause ("fix only if
killswitch-clean, else investigation-only") fires, and it fires on a *measurement*, not on a judgement call: the fix that the
row's framing implies was built behind a throwaway gate and **measured inert**. See § THE EXPERIMENT.

**Tree:** SCRIP `1fb48eba` + this rung · corpus + the six witnesses below · pristine rebuild, RT_OPT `-O0` (O0-DEV).

---

## 1. WHAT THE ROW ASKED, AND WHAT IS ACTUALLY THERE

`SCRIP_RESUME_WHY=1` on beauty names five stored patterns that publish `body_root=NULL` and therefore concede wholesale at β
(`PAT$N_β: jmp PAT$N_ω`). The row split them into two classes by their reported refusal:

| blob | beauty source | signature | named class |
|---|---|---|---|
| `PAT$12` `PAT$20` | `Real` (beauty.sno:55) · `White` (:70) | `right_sealed=0 pfenced=1 rn=0` | (a) pure fence refusal the s182 tier-1 narrowing did not reach |
| `PAT$13` `PAT$22` `PAT$28` | `Id` (:62) · `X4` (:128) · `Commands` (:217) | `right_sealed=1 pfenced=1 rn=0` | (b) refused by `sno_pat_right_sealed`, a second refusal the fence work does not touch |

Both classes are real and both now have their own witnesses. **But neither class is refused for the reason its name says.**
The instrument had to be widened one field to see it (§ 2), and once widened it says the same thing about all five blobs.

## 2. THE INSTRUMENT, WIDENED BY ONE FIELD (`lower_snobol4.c`, diagnostic-only, byte-inert)

`[RESUME-NIL]` now also prints the FIRST REAL BODY NODE the carrier scan actually looks at, its `zdp_seam_tier`, and the first
four nodes in ALLOCATION order. That is the whole finding:

```
[RESUME-NIL] pat=PAT$12 ... rn=0 brt=0 fb=IR_MATCH_ALTERNATE fbtier=0      <- class (a), beauty
[RESUME-NIL] pat=PAT$20 ... rn=0 brt=0 fb=IR_MATCH_ALTERNATE fbtier=0      <- class (a), beauty
[RESUME-NIL] pat=PAT$13 ... rn=0 brt=0 fb=IR_MATCH_FENCE1    fbtier=0      <- class (b), beauty
[RESUME-NIL] pat=PAT$22 ... rn=0 brt=0 fb=IR_MATCH_FENCE1    fbtier=0      <- class (b), beauty
[RESUME-NIL] pat=PAT$28 ... rn=0 brt=0 fb=IR_MATCH_FENCE1    fbtier=0      <- class (b), beauty
ptw_min_rseal_arbno    fb=IR_MATCH_FENCE1    chain=IR_MATCH_FENCE1|IR_MATCH_ALTERNATE|IR_MATCH_LIT|IR_MATCH_DEFER
ptw_min_fence_alttop   fb=IR_MATCH_ALTERNATE chain=IR_MATCH_ALTERNATE|IR_MATCH_FENCE1|IR_MATCH_DEFER|IR_MATCH_LIT
```

**TWO FACTS, BOTH MEASURED:**

**(i) ALLOCATION ORDER IS RIGHT-TO-LEFT, so "the first real body node" is the RIGHTMOST element, not the leftmost.**
`ptw_min_rseal_arbno` is `ARBNO('a') FENCE('b' | epsilon)`. Its `ARBNO` — the only tier-1 generator in the blob and the only
node that can extend — **is not among the first four allocated nodes at all**. `sno_seq_nary`'s own doc ("R first-allocated ⇒
R.β IS resume") is describing a graph whose ends are the other way round from the one the fenced path builds.

**(ii) `IR_MATCH_ALTERNATE` AND `IR_MATCH_FENCE1` HAVE NO SEAM TIER (`fbtier=0`).** `zdp_seam_tier`
(`src/contracts/zeta_depth.c:38`) is a TWO-motion lattice: tier 1 = leaf generators whose β EXTENDS; tier 2 = deterministic
elements whose β is a self-undo that walks LEFT along the seam. A disjunction's β is a THIRD motion — TRY THE NEXT ARM — and
the lattice does not model it, so an `ALTERNATE` scores 0 and is refused by *both* consumers: the s182 tier-1 test in the
lowerer (`zdp_seam_tier(x2) == 1`) and `resume_carrier_ok` (`emit.cpp:2447`) downstream.

## 3. THE EXPERIMENT — THE FIX THE ROW IMPLIES WAS BUILT AND MEASURED INERT

Class (b) is named after `sno_pat_right_sealed`, so the implied cure is to narrow or drop that seal. It was gated off behind a
throwaway `SCRIP_RSEAL_OFF` and measured. **It does not cure a single witness — not alone, and not even stacked with
`SCRIP_FENCE_IGNORE=1`:**

```
                             default    RSEAL_OFF   RSEAL_OFF + FENCE_IGNORE
ptw_min_rseal_arbno          nomatch    nomatch     nomatch
ptw_min_rseal_commands       nomatch    nomatch     nomatch
ptw_min_rseal_unsealed_ctl   nomatch    nomatch     match
```

Because with the seal gone the carrier that gets published is the `FENCE1` (first-allocated = rightmost), tier 0 — which
concedes at β exactly as `NULL` did. **The seal is a real second refusal and it is not the load-bearing one.** The experiment
was reverted; only the widened diagnostic is committed.

## 4. WITNESSES (six, oracle-refed `sbl -b`, all RED in BOTH modes, m3 ≡ m4)

| witness | pattern | class | what it proves |
|---|---|---|---|
| `ptw_min_fence_left_altresume` | `FENCE(epsilon) ( 'a' \| 'aa' )` | (a) shape-first | `SCRIP_FENCE_IGNORE=1` **CURES** it ⇒ here the fence verdict really is the whole refusal |
| `ptw_min_fence_alttop` | `( 'a' FENCE(epsilon) \| 'aa' )` | (a) beauty-second (`Real`/`White` shape) | `FENCE_IGNORE` **does NOT cure** ⇒ the ALT-top wall is behind the fence wall |
| `ptw_min_alttop_nofence_ctl` | `( 'a' ('b' \| epsilon) \| 'aa' )` | control / THIRD CLASS | **no fence anywhere**, carrier published, still RED ⇒ the untiered-disjunction wall stands alone |
| `ptw_min_rseal_arbno` | `ARBNO('a') FENCE('b' \| epsilon)` | (b) shape-first | the generator left of the seal has instances the seal throws away |
| `ptw_min_rseal_unsealed_ctl` | same + trailing `epsilon` | control | ONE TOKEN flips `right_sealed` 1→0; `FENCE_IGNORE` then cures ⇒ the two refusals are independent |
| `ptw_min_rseal_commands` | `Commands = *Command FENCE(*Commands \| epsilon)` | (b) beauty-second (`Commands`:217 verbatim) | beauty's own shape, with `Command` given the alternatives beauty's `Command` has |

⛔ **A NEGATIVE RESULT WORTH KEEPING:** beauty's `Id` (`ANY(..) FENCE(SPAN(..) | epsilon)`) transcribed verbatim **agrees with
the oracle** (`nomatch = nomatch`). Its left element is a single `ANY` with no alternatives, so the blob genuinely has nothing
to resume and the wholesale seal costs nothing there. The seal only bites when something to the fence's LEFT can still extend —
which is `X4` and `Commands` in beauty, not `Id`.

## 5. WHAT THE MANUAL LICENSES (why the seal is over-broad even though it is not the blocker)

v3.7 Ch.9/18: `FENCE(P)` refuses to re-offer **P's own** alternatives on backup. It does **not** forbid the scanner retreating
to the LEFT of `FENCE(P)`; that motion never backs up *through* the fence. So a blob `G FENCE(Q)` with `G` a generator must
still expose `G`'s β. `sno_pat_right_sealed` seals the WHOLE blob on the rightmost element alone — the same wholesale shape
refusal (law 0d) that s182 already convicted for the fence half, one screen further down the same function.

## 6. THE RUNG THIS BECOMES (owed to Lon/HQ — NOT landable from a worker seat)

**Give the resume-carrier lattice its third motion: a tier for `IR_MATCH_ALTERNATE` meaning "β tries the next arm".** That is a
one-line-looking change to `zdp_seam_tier`, which is **also the ζ-depth planner's authority** (`zdp_out_gamma`/`zdp_out_omega`,
`zd_plan`) — so it moves stack depth planning corpus-wide, not just carrier admission. It needs its own rung with a full
`.s` blast radius, and the ruling is Lon's. The second half (carrier selection must read the correct END of an allocation
order that runs right-to-left, and must skip trailing fence forms to the last live extender) rides with it.

⛔ **NOT ON M1'S CRITICAL PATH** and this rung does not change that: `SCRIP_FENCE_IGNORE=1` leaves beauty bit-for-bit unchanged
(s182 addendum 3), and beauty's `Parse` never becomes a blob at all — the M1 wall is the runtime-composed `TT_SEQ` β, row 31.

## 7. GATES — MEASURED, THEN RE-PROVEN AFTER A REBASE THAT PULLED THE M1 LANDING

Mid-rung this tree rebased onto `0b7b8d29` (HQ Fable's **RT-CARRIER — the M1 wall is down**) and `943e404a`
(seat1's RTSEQ-RESUME), which also refactored the publish into `sno_pat_publish_body_root()`, the ONE AUTHORITY now shared
with the JIT road. The diagnostic was **re-applied inside that function** (not restored inline), and every number below is
from a **pristine rebuild after the rebase**:

* **Byte-identity:** 272 programs (`probe/passthru` + `crosscheck/patterns` + `demo`) swept `--compile`+md5, `HEAD~1` vs
  `HEAD`: **0 movers.** Hold-the-arm-fixed control (base swept twice): **0** — this set is deterministic, so the diff means
  what it says. (Contrast s172: `parser/unary_not.sno` is nondeterministic at a fixed arm; it is not in this set.)
* **Corpus:** **m3 332/5 · m4 325/11 · SKIP 1** — the s182 watermark exactly, fail-set identical by name.
  ⛔ ONE FALSE READING, RECORDED SO IT IS NOT INHERITED: an earlier run of this same script read m3 298/39 with 35 m4 SKIPs.
  That was **my own A/B binary swap racing the runner**, not a regression — the corpus runner reads `./scrip` and
  `out/libscrip_rt.so` live. Re-run after the binaries settled: 332/5 · 325/11. Never trust a corpus board taken while an
  A/B is rebuilding in the same tree.
* **7-mover fence class** 114/119/129/130/148/149/150: **green** before the rung, after the rung, and after the rebase.
* **passthru board:** m3 **119/126** · m4 **111/126**. The six new rows are RED in both modes and are the only rows this
  rung adds; no pre-existing row moved *because of this rung* (`ptw_min_compose`/`fncat`/`poison_eval` went GREEN under the
  rebase — that is the M1 landing's win, not this one's).
* **Beauty census reproduces verbatim post-rebase:** the same five blobs, the same two classes, and now every one of them
  reading `fbtier=0`.

## 8. THE RUNG HAS A CORPUS CONSEQUENCE, NOT ONLY PROBE WITNESSES

`145_pat_left_assoc_via_arbno_fence` — a **standing m3 corpus red** through this whole watermark — is class (a) by signature,
and it is beauty-shaped in the same way:

```
expr = num . FIRST ARBNO(FENCE('+') num . LAST)          oracle: first=1 last=5      scrip: fail
[RESUME-NIL] pat=PAT$1 right_sealed=0 pfenced=1 rn=0 fb=IR_MATCH_ASSIGN_COND fbtier=2
                       chain=IR_GOTO|IR_MATCH_ASSIGN_COND|IR_MATCH_ASSIGN_SAVE|IR_MATCH_DEFER
SCRIP_FENCE_IGNORE=1 -> fail   (not cured, exactly like ptw_min_fence_alttop)
```

Its first body node is tier **2**, so the s182 tier-1-only test refuses it. This is the cheapest corpus-visible statement of
the narrowing's cost: *the tier-1 test is not the right predicate; "can this node's β still yield" is.*

⛔ **NOT CLAIMED:** `160_pat_alt_inner_gen_resume` (`('a' ARB . V | 'q') 'b'`) sits in the same neighbourhood by name and shape,
but it **SIGSEGVs** rather than answering wrong, and it publishes no `[RESUME-NIL]` at all (it is inline, not a stored blob).
Different failure mode; it is named here only so the next seat does not assume it rides along. It needs its own minimization.
