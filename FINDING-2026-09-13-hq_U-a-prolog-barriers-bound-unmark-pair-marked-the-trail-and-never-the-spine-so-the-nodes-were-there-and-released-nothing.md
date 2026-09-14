# FINDING — A PROLOG BARRIER'S BOUND/UNMARK PAIR MARKED THE TRAIL AND NEVER THE SPINE, SO THE NODES WERE THERE AND RELEASED NOTHING

**hq_U, 2026-09-13. MODE NONET. Concern 3, ZETA STORAGE, across all seven languages.**
**Branch `hq_U-pl-gamma-fence-on-b6b42eee1` at SCRIP `53ae73b64`, cut from clean `b6b42eee1` · corpus
`48796211a` · .github `960f7831` · `RT_OPT=-O0`. Ordered by CEO-690 (Lon 2026-09-13, verbatim: *"do a
whack-free on GAMMA for a FENCE d (i.e. cut !) or otherwise FENCE d operation."*). The cto measured the
population and owns the instrument; hq_U owns the build.**

## 1. THE DEFECT, AND WHY READING THE LOWERER SAID IT WAS ALREADY CURED

`IR_BOUND` and `IR_UNMARK` sit at every Prolog barrier site — `pl_lower_ite` (which `once/1`, `(->)/2`,
`(\+)/1`, `forall/2` and `ignore/1` all lower through) and `pl_lower_catch`. I read that and told the cto
the obvious cure was already in the tree and would move zero rows. **Half right, and the wrong half was the
one that mattered.**

`bb_bound.cpp` has **three arms and they do two different things**:

| arm | taken by | what it marks |
|---|---|---|
| cells (`_.op_zres`) | Icon | `mov FRQ(off), rsp` / `mov rsp, FRQ(off)` |
| default | the rest | the same — **rsp** |
| **pinned** (`x86_fb_pinned()`) | **Prolog** | `mov FRQ(off), r12` / `rt_pl_tr_unwind` — **the TRAIL** |

So a Prolog barrier's BOUND/UNMARK pair was **a trail mark wearing the name of a frame mark**. The nodes
were present, correctly paired, correctly wired — and pointed at the wrong resource. Nothing in a Prolog
barrier had ever released a byte of spine.

⭐⭐ **THE GENERAL FORM: A NODE THAT IS PRESENT, PAIRED AND NAMED FOR THE JOB IS NOT EVIDENCE THAT THE JOB IS
DONE.** Every structural check a reader applies — does the node exist, is it at both sites, is it paired,
does the frame layout carve it a slot — returned yes, and the field the layout carves is *literally named*
`bound.saved rsp`. The one question none of them asks is **which arm of the template runs on this
frontend**. A shared node with per-frontend arms will answer a structural audit truthfully and still do
something else entirely. The cto's depth measurement was right and my reading was wrong, and the
disagreement was only visible because they insisted on the number.

## 2. THE INTERMEDIATE RESULT THAT WOULD HAVE READ AS "THE MECHANISM IS WORTH 27%"

The first cure banked the rsp frontier at `IR_BOUND` and, at the fence, walked the choice chain through
`F.B0` at `[B+24]` — one step of which is exactly what `rt_pl_cut_barrier` does at rung 4 — up to that
frontier, then restored rsp. Measured: `once(q(_))` went **1141 B → 838 B and stalled there**. Three rows
moved about a third and two got *worse* by exactly 16 B, the cost of the fence node's own slot.

⛔ **The reason is one line of `rt_pl_disj_open`: it raises B to THIS frame's `H`, and `H` sits above every
frontier a fence can release to.** So the walk stopped at `H` on the first comparison and left the frame it
had just emptied **pinned as its own current choice**. The cure is to bank B at `IR_BOUND` *before* the open
raises it, and restore that. With one variable changed, the same four rows go from ~840 B to **reclaimed**.

⭐⭐ **A PARTIAL CURE IS NOT A WEAK SIGNAL, IT IS A CONFIDENT WRONG ONE.** 1141 → 838 is a real,
reproducible, correctly-signed 27% improvement. Shipped as the answer it says *the barrier retains
something else too, and the gamma fence is a minor optimisation* — a conclusion that is false, arrived at
from true numbers, and expensive to come back from. The tell that it was not the whole cure was not in the
numbers at all: it was that **the model predicted `reclaimed` and the measurement said 838**, and a model
that predicted the other rows correctly does not get to be ignored on one.

## 3. THE TABLE (cto's `util_pl_rung9_gamma_fence_witness_set.sh`, unmodified, m3, stack pinned 8192 KB, bisected)

| body | before | after |
|---|---|---|
| `once(q(_))` | 7348 · 1141 B | **400000+ reclaimed** |
| `( q(_) -> true ; true )` | 7348 · 1141 B | **400000+ reclaimed** |
| `forall(q(X), r(X))` | 8568 · 979 B | **400000+ reclaimed** |
| `\+ (q(_), fail)` | 10204 · 822 B | **400000+ reclaimed** |
| `once(between(1,2,X))` | 8837 · 949 B | **400000+ reclaimed** |
| `catch(once(q(_)), _, true)` | 6689 · 1254 B | 8568 · 979 B — **named, not swept** |
| `findall(X, between(1,2,X), _)` | 7787 · 1077 B | 7787 · 1077 B — **unmoved to the byte** |
| `q(_)` (anchor, un-fenced) | 8031 · 1044 B | 8031 · 1044 B — untouched, as it must be |
| SAFETY CONTROL | `cp(8) once(1)` | `cp(8) once(1)`, and swipl agrees |

**The two survivors are rows, not residue.** `catch/3` is backtrack-**transparent** — a later failure may
re-enter its goal — so its success edge is **not** a fence and correctly gets none; its remaining 979 B is
its own row. `findall`'s reclamation is its own path and covers clause-defined goals only (cto, measured:
50 clause solutions free, 2 builtin-generator solutions not).

## 4. THE PREDICTION, MADE BEFORE THE LANDING, KEPT IN BOTH DIRECTIONS

Sent to the cto before any of this was built: *the barrier cure will green `once(between(1,2,X))` and leave
`findall(X, between(1,2,X), _)` red at roughly its 1077 B, because nothing in a Prolog barrier released
spine, so the KIND of the inner goal cannot matter there — while findall's teardown is a different path my
change does not touch.* Both halves held; the findall row did not move by a single byte.

⭐ **That is what the cto's four builtin-generator arms bought, and they were added to the instrument
BEFORE the cure landed rather than after.** Without them this landing greens every row in the table and
reports a class fully cured, with the generator half untouched and nothing saying so. **An instrument
extended after a cure grades the cure's own idea of the population.**

## 5. WHAT IS PINNED, AND HOW THE CRITERION WAS PROVEN TO SAY NO

`test_gate_pl_an_opaque_goal_barrier_releases_the_frame_its_goal_carved.sh` — 11/11 in **3.3 s** (5
witnesses × 2 modes + the safety control), run once, **then** wired into `test-sequential` and adopted into
the ratchet floor (CEO-381). ⛔ **It grades CAPACITY, not answers, which is why this class outlived every
board we own: every answer these five programs produce was RIGHT throughout the defect.** They simply ran
out of machine stack between 6,689 and 10,204 levels where the same call lexically fenced with `!` reaches
400,000+.

`SCRIP_PL_FENCE` is the killswitch, default ON, and it is **total** — the lowerer's fence node, both
template halves, and the frame-layout widen. At `=0` the witness set reproduces the pre-change tree **row
for row, all 18 rows**, and all five gate witnesses die with `ERROR 246` at N=50000 and complete at `=1`.
Fail-once/pass-once, both directions, **on one binary, with no second tree**.

⛔⭐⭐ **A CAPACITY INSTRUMENT CANNOT SEE A CORRECTNESS DEFECT IN THE RESOURCE IT IS MEASURING (cto, 2026-09-13, sharper than the warning it came from).** The cto warned before the cut that the pinned arm has ONE slot and it is already spoken for by r12, so banking rsp into `FRQ(_.op_off)` destroys the trail mark — and the failure would present as **wrong ANSWERS on backtracking, not as a byte count**. Avoided here (off = trail, off+8 = frontier, off+16 = the banked choice, off+24 = pad), but the general form is the part to keep: **a cure that touches a mark slot owes an answers arm on principle, not because someone predicted a collision.** Nothing in the depth table could have caught it; the arm that would have is the safety control, which is graded by answers and reads `cp(8) once(1)` in both killswitch positions.

## 6. SHARED-NODE VERDICT SCOPE — THE BOARDS OWED, AND WHAT IS AND IS NOT EVIDENCE

`grep -c IR_BOUND src/lower/lower_*.c`: **icon 1 · prolog 3 · everything else 0.** So the frontends that
lower the changed node are Prolog and Icon, and those two are the boards owed. ⛔ **SNOBOL4 builds zero
`IR_BOUND` nodes, so its master executes zero changed lines and is a collateral-damage check, not evidence**
(hq_V's rule: a control arm is only evidence if you can name an entry in it that executed the changed
lines). **Icon IS evidence** and not collateral: the frame-layout widen adds 16 bytes at its one `IR_BOUND`
site, so an Icon graph that uses a bounded expression changes shape even though no Icon instruction does. ⭐ **And if IcnM comes back unmoved, that is a measurement and not a relief** (cto): a widen that costs nothing observable is a fact about the Icon workload, not proof that the widen is free, and the next seat to widen the same struct will cite this row.

Green on this binary: prolog smoke 5/5 both modes · icon smoke 15/15 both modes · snocone 5/5 · rebus ·
`test_gate_no_unnamed_holes_in_an_activation_frame` 164 graphs tile exactly. **The masters are the coo's and
are asked, not run here** (ONE RUNNER, MODE line 2).

## 7. ⛔⭐⭐ I SHIPPED A REGRESSION IN THE FIRST COMMIT AND THE ONLY THING THAT CAUGHT IT WAS THE BASE-TREE COMPARISON

**`53ae73b64` broke the soft cut. `4add22403` cures it.** `test_gate_pl_iso_rung6_the_soft_cut_if_3_predicate.sh`
is **GREEN at `b6b42eee1` and RED at `53ae73b64`** — measured, both trees built, not inferred.

The first commit put the release on **every** pinned `IR_UNMARK`, on the reasoning that *a barrier which has
run out is as committed as one that succeeded*. That is true of an **opaque** barrier and false of `(*->)/2`,
which is backtrack-**TRANSPARENT** into its condition — every solution of C runs T — so its unmark is a
landing the machine **re-enters**, and the release whacked frames a redo was about to use. The witness reads
`[9]` where the oracle reads `[7,8,9]`, on

```
findall(Z, if((!, fail), b(_), c(Z)), L3)
```

one line of a twenty-six-line program: the **else arm's generator frames** were released by the condition's
failure landing. The cure is a bitmask — `IR_UNMARK`'s ival is 1 the ball guard, 2 the γ-fence form, **4 this
landing may release** — with bit 2 set by `pl_lower_ite` **only**. That is the rule `bb_cut` already states at
rung 4 for the opaque cut: **the lowerer is the only place that knows opacity**, so it travels as a bit and is
never inferred in a template. `catch/3` loses a release it should never have had and its number is unchanged
at 8568 · 979 B, so it was buying nothing. The capacity table above is unmoved by the fix.

⛔ **NOTHING IN THE LANDING LANE SAW IT.** Four per-language smokes, the entire capacity table, my own gate,
and every answer-graded arm I owned were **green on the broken build**. The instrument that reds it is
another seat's wired gate, and I only reached it because I built the base tree in a worktree to prove the
seventeen reds in my `make test` were *other people's*. **Sixteen were. The seventeenth was mine.**

⭐⭐ **THE CHECK THAT CAUGHT IT IS THE ONE I NEARLY SKIPPED AS BOOKKEEPING** — I was proving a negative about
somebody else's reds, not looking for my own. For a shared-node landing the base-tree gate-by-gate comparison
is not a courtesy owed to the reds list; it is the arm, and it belongs **before** the board is asked for, not
after.

⛔⭐⭐ **AND THE CONTROL I WROTE FOR IT COULD NOT FAIL, SO I DELETED IT.** I added a transparency control to my
own gate, then **reintroduced the bug on purpose** to test it: `findall` over `( q(X) *-> true ; X = none )`
and over `( fail *-> Z = t ; c(Z) )`, graded by **answer** against swipl — and the same shapes through `if/3`
standalone — **all read GREEN on the defect**. The divergence needs the rung-6 witness's whole program. **A
control that stays green on the defect it names is worse than no control, because the next reader counts it
as coverage.** It is removed; the gate header names the covering gate instead, and does not copy its fixture.
⭐ The general form, and it is the same shape as the `-O2`-habit and `command -v` lessons: **testing that a
criterion goes GREEN when you are right is half the proof; the half everyone skips is making yourself wrong
on purpose and checking it goes RED.**

## 8. ONE PROCESS ERROR, RECORDED BECAUSE IT COST A 272-ARM RUN

I edited the `Makefile` to wire the gate **while `make test` was running**. Every arm after that point hit
`util_require_fresh.sh` and REFUSED rc=2 — *binary older than the tree it names* — so the arms after it were
unmeasured and the run had to be killed and repeated. ⭐ **The freshness preflight is not only a guard
against a stale binary; it is a guard against a moving one, and a blocking set is a measurement whose
subject must hold still.** It did exactly its job, loudly, and the cost was mine.
