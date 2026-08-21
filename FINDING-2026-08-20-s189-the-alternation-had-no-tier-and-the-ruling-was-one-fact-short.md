# FINDING — s189 (seat7) · TIER 3 IS THE RIGHT CLASSIFICATION AND IT IS NOT SUFFICIENT ON ITS OWN: THE ADMISSION NEEDED TWO MEASURED PRECONDITIONS HQ-73 DID NOT CARRY, AND EACH WAS PAID FOR BY A CRASH

**Row:** `alt-seam-tier` (QUEUE rank 1), ruling HQ-73, restated in the brief after HQ minted the ruling without minting the row.
**Tree:** SCRIP **`28e2122a`** (rebased onto seat2's `4a3f8606` ATP-CURSOR-ASSIGN-RETRY and `47135a86` ARBNO-SEAL-OMEGA) · corpus **`df918253`** · pristine rebuild, RT_OPT `-O0` (O0-DEV).
⭐ **RE-PROVEN IN FULL AFTER THE REBASE, AND IT WAS NOT A FORMALITY:** both incoming commits touch this lane — `4a3f8606` tiered the cursor operator `@` in **this same function**, arriving at the same shape independently, and `47135a86` changed the FENCE-rooted ARBNO seal. The conflict in `zeta_depth.c` was resolved by **composing both arms** (`IR_MATCH_ATP → 2` with its `SCRIP_ATP_SEAMTIER` switch, `IR_MATCH_ALTERNATE → 3` with `SCRIP_ALT_SEAM_TIER`), never by taking a side. Post-rebase pristine re-proof is identical to pre-rebase, line for line.
**Disposition: LANDED, killswitched, and DELIBERATELY NARROWER THAN THE RULING'S LETTER** — the narrowing is a measurement, not a judgement call (§3).

---

## 0. FIRST STEP FIRST — HQ'S CONSUMER GREP RE-VERIFIED AT HEAD, AND IT HOLDS

The brief ordered this before anything else, because HQ has been wrong twice this campaign. At `87ffd0b5`:

`zdp_seam_tier` appears **once** inside `src/contracts/zeta_depth.c` — its own definition at `:38`. **Zero internal callers.**
Every live consumer is a seam/resume site: `resume_carrier_ok` (`emit.cpp:2471-2473`), the FENCE-RESUME carrier scan
(`lower_snobol4.c:2612`), the `_f1r` fence arm (`emit.cpp:3367`), and two `getenv`-gated diagnostics. `zdp_out_gamma` /
`zdp_out_omega` / `zdp_carve` are file-static and never reach it. **It has not gained a depth-planner consumer. No STOP-and-ask.**

## 1. THE MOTION, FROM THE TWO AUTHORITIES THAT SETTLE IT

HQ-73 defined tier 3 as *"beta RE-YIELDS at the same cursor (a different alternative): no leftward walk, no backup THROUGH
anything."* Both authorities say exactly that, and neither had been quoted into the lattice before:

* **SPITBOL's own engine** — `v37.min:13502` `p$alt`: `mov wb,-(xs)` (stack the **current** cursor), `mov parm1(xr),-(xs)`
  (stack a pointer to the alternative), `brn succp`. Failing back into it restores the cursor it was **entered** with and
  enters the next arm. There is no leftward motion in the node at all.
* **The manual's bead diagram, v3.7 p.58** — *"if the needle cannot pass through a component, it will try the next alternative
  **in that column**"*, and only when the column is exhausted is *"the needle pulled back to the previous column."* Trying the
  next arm is the in-column motion; the leftward walk is the other one. Two motions, and tier 2's doc describes only the second.
* **SCRIP already spelled it the same way and nobody had connected it** — `emit.cpp:2140`: ALTERNATE's β is `jmp [resume_ptr]`,
  "re-enters the NEXT arm on backtrack", `K == 0`.

**The fence arm admits tier 3 on the manual's own ground** (v3.7 p.126 / p.204: FENCE fails when the scanner has to **back up
through** it): re-offering an arm at the cursor the ALT was entered with backs up through nothing. That is the identical
argument s182's FENCE-RESUME already won for ARBNO's extend.

## 2. THE EDIT — 9 INSERTIONS / 7 DELETIONS, THREE FILES, ONE KILLSWITCH

`zeta_depth.c` gains `case IR_MATCH_ALTERNATE: return zdp_cap_alttier() ? 3 : 0;` and tier 3's definition in the doc.
`resume_carrier_ok`, the lowerer's carrier scan, and the `_f1r` fence arm each admit it. **`SCRIP_ALT_SEAM_TIER=0` collapses
the tier to 0 at the lattice, so all four consumers revert in lockstep** (the s124 two-reader law) — one switch, not four.

⛔ **`zdp_cap_alttier` is deliberately UNMEMOIZED**, unlike `zdp_cap_seamtier` beside it. A `static int v` cache is
static-duration mutable state and the NO-NEW-GLOBALS rule is written broadly enough to cover it; this reads the environment at
the site, the shape the FENCE-RESUME arms already use and give the reason for ("getenv at the site so nothing can be left
half-armed"). **This rung adds no file-scope state of any kind.**

⛔ **`IR_DISJUNCTION` is deliberately not admitted, and that is not a per-op filter.** It is a different family with a
different template (`bb_disjunction.cpp` — the Icon nary / Prolog gate form), not another member of this one. The whole of
`IR_MATCH_ALTERNATE` is admitted on one predicate; no member is named or excepted.

## 3. ⛔ THE RULING WAS TWO FACTS SHORT, AND EACH MISSING FACT COST A SIGSEGV — MEASURED, THEN CURED

Tier 3 as ruled — admitted unconditionally beside tier 1 — **cured two witnesses and SIGSEGV'd a third.**
`ptw_min_alttop_nofence_ctl` went from a wrong answer (`nomatch`) to **rc=139**, with the tier admitted and nothing else changed.

The instrument that named the cause was the `[RESUME-WHY]` diagnostic widened by the choice-scan triple (`getenv`-gated,
byte-inert). **Three witnesses, one field apart:**

| witness | nc | lf | fn | cro | tier 3 as ruled |
|---|---|---|---|---|---|
| `ptw_min_fence_left_altresume` | **1** | 0 | 1 | 0 | **CURE** |
| `ptw_min_fence_alttop` | **1** | 0 | 1 | 0 | **CURE** |
| `ptw_min_alttop_nofence_ctl` | **2** | 0 | 0 | 0 | **SIGSEGV** |

`lf=0` and `fn=1` on **both** cures, so neither `leaf_ok` nor `has_fence` separates a cure from the crash. **The unsealed
choice-node COUNT alone does.** `( 'a' ('b' | epsilon) | 'aa' )` is an ALT arm carrying a **nested ALT**, whose own
`sub rsp,32` shifts the frontier under the outer record that β reads at `[rsp+8]`.

⭐ **THIS IS s121'S ALT-DEPTH CONVICTION, RE-MEASURED AND STILL LIVE — AND ALT-FLAT DID NOT RETIRE IT.** s202's ALT-FLAT makes
arm **interiors** footprint-0, which is not the same claim as "an arm contains no other carving choice node". It is also
s126's finding verbatim: *one-deep records compose by contiguity, two-deep do not yet.*

**THE ADMISSION NEEDED TWO EARNED CONJUNCTS, AND EACH ONE WAS PAID FOR BY A CRASH:**

**(a) `_nc == 1` — one unsealed choice node.** The table above. Without it `ptw_min_alttop_nofence_ctl` SIGSEGVs.

**(b) `!sealed_defer` — no `seal==1` DEFER in the blob.** Paid for by a SECOND crash, found only because the corpus board was
run: **`crosscheck/patterns/150_pat_star_var_fence_alts_no_arbno`** — a standing corpus GREEN whose own header says
*"Any future FENCE fix must keep this passing"* — went to **rc=139** with conjunct (a) in place and `nc=1`. Its diagnostic
reads **`sd=1`**. Its `outer = (*cmd | *cmd *cmd | *cmd *cmd *cmd)` over `cmd = FENCE('a' | 'ab')` gives **every arm a
right-sealed DEFER**, and s177 PF-1b had already written down why such an arm cannot be re-entered from outside: *a `seal==1`
DEFER's β IS the fence-demarcation frame unwind, correct only in its own activation context.* Re-entering the ALT stamps
per-arm β targets, and an arm ending in that unwind jumps it against a foreign activation.
The fact is **not re-derived**: `_sd` is already computed at `resume_carrier_ok`'s single caller and is **passed in**, so the
sealed-defer classification keeps exactly one spelling. Tier 1 and tier 2 ignore the parameter and stay byte-identical.

⛔ **AN HONEST NOTE ON METHOD.** Both conjuncts were found by a crash, not by reading — which is precisely how a ratchet ends up
one syntax behind the code. The defensible statement is not "these two conjuncts": it is that **tier 3 answers only "can this
node's β still yield", and admission additionally requires the blob's resume machinery to be sound for a re-entered ALT.** The
two facts that establish that were already established, for this same motion, by the s127/s128 sibling admission; this rung
reuses its preconditions rather than inventing new ones.

⛔ **THE SIBLING ADMISSION (s127/s128) IS NOT COLLAPSED INTO THIS ONE, AND MUST NOT BE.** Its other two conjuncts —
`!_fn && (_lf || cro)` — would have **refused both cures here** (both read `lf=0 fn=1`). The two arms share the two
depth/activation preconditions and differ on the rest; merging them would trade this rung's cures for its own.

**With both conjuncts, `150` returns to green, both cures hold in m3 AND m4, and the whole named 7-mover FENCE class
(114/119/129/130/148/149/150) is green.**

⛔ **AND THE `!sealed_defer` CONJUNCT IS WIDER THAN ITS OWN MECHANISM — SAID HERE SO IT IS NOT INHERITED AS A LAW.** s177's
hazard is specifically *an arm that **ends** in a sealed defer*, whose β is the foreign-activation unwind. This rung refuses on
**any** `seal==1` DEFER **anywhere in the blob**, which is strictly broader. It measurably costs two witnesses that the
narrower predicate would likely keep: `probe/fuzz/fz_diff_13` and `probe/fuzz/fz_segv_15` were **cured** by the `_nc == 1`-only
build (`fz_segv_15` went rc=139 → PASS in BOTH modes) and are refused again by the wider conjunct. That is the honest price of
landing 150 green in the same rung, and narrowing it to the arm-tail is named as its own row in §7.

## 4. ⭐ THE BLAST RADIUS IS FIFTEEN PROGRAMS AND SEVENTEEN JUMP INSTRUCTIONS, AND EVERY ONE IS THE SAME EDGE

Sweep: **1348 programs** (`crosscheck` + `probe` + `programs/snobol4` + `benchmarks`), `--compile` + md5, **1330 comparable**
(18 NOEMIT). ⛔ `corpus/programs/lon/` excluded **by construction** in the sweep script — never enumerated, never compiled.

* **NOISE FLOOR MEASURED, NOT CITED:** each arm swept **twice** and self-diffed. **Exactly 1 flaky row —
  `programs/snobol4/parser/unary_not.sno`**, the program s172 independently recorded as nondeterministic at a fixed arm.
  A sweep without a same-arm control reports its own noise as signal.
* **NET MOVERS: 15 / 1330** (raw 16). Suites: 1 `crosscheck/patterns` (`147_pat_fence_through_unevaluated`), 4 `probe/fuzz`,
  4 `probe/passthru/ptc5b_*`, the 2 cured witnesses, and `calculator-1` + `json-match-fence` in both their `benchmarks/` and
  `programs/` copies.
* ⭐⭐⭐ **HQ-60-GRADE ACCEPTANCE, LINE BY LINE OVER ALL 15: `nonconforming = 0`.** Every changed line in the entire blast
  radius is one half of this pair, and there is nothing else in it:

```
-   jmp   PAT$0_ω                    <- concede wholesale
+   jmp   n0_match_alternate_β       <- offer the next arm
```

  13 movers change **exactly one instruction**; the two `calculator-1` copies change two each (two blobs retargeted) — **17 instructions total**. **Zero carves,
  zero displacement changes, zero re-homes, zero spelling changes.** HQ predicted "confined to seam/resume sites"; it is
  confined to **one edge** inside them.
* **KILLSWITCH PROVEN, NOT ASSERTED:** `SCRIP_ALT_SEAM_TIER=0` vs base = **0 net movers / 1330** (raw 1 = the proven-flaky row).

### 4c. RE-MEASURED AFTER THE REBASE AGAINST A REAL `HEAD~1` BUILD — SAME ANSWER, BIGGER TREE

The numbers above are corpus **`9ba9ed5a`** (1348 swept / 1330 comparable). After the rebase the corpus had grown, so the A/B was
redone at corpus **`df918253`** (**1384 swept**) against a **`HEAD~1` (`47135a86`) worktree built pristine** — not against a
remembered baseline:

| arm | result |
|---|---|
| noise floor (same arm swept twice) | **1** (`parser/unary_not.sno`) |
| **killswitch** — `SCRIP_ALT_SEAM_TIER=0` vs `HEAD~1` | **0 net movers / 1384** |
| movers — `HEAD` vs `HEAD~1` | **19 net**, **21 instructions**, **`nonconforming = 0`** |

The 19 are the same 15 plus **four alt/fence witnesses other seats added since the baseline** —
`fzr_07_breakx_alt_fence`, `fzr_07_control_lit_arm1`, `fzr_22_nested_arbno_not_first`,
`fz_red_m4a_blob_alt_fence_defer` — every one of them in this rung's own class, and every changed line still one half of the
same jump pair.

⛔ **AN INSTRUMENT-HYGIENE LESSON WORTH MORE THAN THE RUNG, RECORDED SO IT IS NOT RE-LEARNED.** `pgrep -f`/`pkill -f` on a
box running eight seats matches **other seats' processes AND the matching shell's own command line**. Three separate times this
session an instrument read something other than what it named: a wait loop on `make pristine` blocked on **seat5's** build;
a `pkill -f "cc1 "` was machine-wide rather than seat-scoped; and `pkill -f "ssweep.sh"` **killed itself before its targets**,
leaving five stale sweeps alive — one of which wrote into the same output file as a new sweep and produced a file with
**2093 rows and 1384 unique paths**. ⭐ **THE CHEAP GUARD THAT CAUGHT IT: compare `wc -l` against `cut -f2 | sort -u | wc -l`
on every sweep file before believing any diff of it.** All ten pre-rebase sweep files audited clean (1348/1348) and the
corruption was confined to the one shared filename; had that check not been run, a duplicated baseline would have reported
phantom movers. Wait on a **log marker or a file**, never on a process name.

### 4b. THE BOARDS — TWO CURES, ZERO REGRESSIONS, WATERMARK HELD

| board | base | tier 3 | delta |
|---|---|---|---|
| **corpus** | m3 **332/5** · m4 **325/11** SKIP 1 | m3 **332/5** · m4 **325/11** SKIP 1 | **fail-set IDENTICAL BY NAME** |
| **passthru** (175 rows × 2) | m3 162 · m4 148 | m3 **164** · m4 **150** | **+2 / +2 — the two cures, nothing else** |
| **probe/fuzz** (25 × 2) | m3 1 · m4 1 | m3 **2** · m4 **2** | +1 (`fz_diff_07`, both modes) |

⛔ **TWO FUZZ ROWS CHANGED CRASH-FLAVOUR AND NEITHER IS THIS RUNG — PROVEN, NOT ASSERTED.** `fz_segv_15` and `fz_segv_24` are
**not in the mover set** and their emitted `.s` is **byte-identical** across arms (`cmp` clean). Run 8× each on one fixed arm
from one binary: `fz_segv_15` → `139 139 139 139 139 139 132 139` (SIGSEGV *and* SIGILL); `fz_segv_24` →
`139 139 0 0 0 0 0 0`. **Both are self-noise at a fixed arm.** A board row read once on a program like this is an arbitrary draw.

## 5. THE SIX WITNESSES — 2 GREEN, AND THE OTHER 4 ARE THREE DIFFERENT REFUSALS THAT TIER 3 CANNOT REACH

⛔ **THE BRIEF'S DONE-WHEN ASKED FOR SIX GREEN. IT IS TWO, AND THE OTHER FOUR ARE NOT THIS CLASS.** Each was read off the
`[RESUME-NIL]` / `[RESUME-WHY]` instrument at baseline, so the owner of each refusal is named by measurement, not by argument:

| witness | baseline signature | owner of the refusal | tier 3 |
|---|---|---|---|
| `ptw_min_fence_left_altresume` | `fb=ALTERNATE fbtier=0` | the missing tier | ⭐ **CURED, m3 ≡ m4** |
| `ptw_min_fence_alttop` | `fb=ALTERNATE fbtier=0` | the missing tier | ⭐ **CURED, m3 ≡ m4** |
| `ptw_min_alttop_nofence_ctl` | `body_root_op=54 tier=0`, **nc=2** | the ALT-depth story, §3(a) | unmoved — **refused on purpose** |
| `ptw_min_rseal_arbno` | **`right_sealed=1`** | `sno_pat_right_sealed` forces `body_root=NULL` **before any tier is consulted** | unreachable |
| `ptw_min_rseal_commands` | **`right_sealed=1`** | same | unreachable |
| `ptw_min_rseal_unsealed_ctl` | `fb=IR_MATCH_DEFER **fbtier=2**` | the fence arm's carrier scan admits tier 1 (now 1 or 3) and **refuses tier 2** | not this class |

The two `right_sealed=1` witnesses cannot be reached by any tier: `sno_pat_publish_body_root` short-circuits
`gp->body_root = (... && !rs) ? ... : NULL`, so the lattice is never consulted. s183 §3 already built and measured the
seal-removal experiment and found it inert on its own; **the seal is a real second refusal and it is still the load-bearing one
for those two.** They need s183 §6's second half — carrier selection reading the correct end of an allocation order that runs
right-to-left — which is a separate rung with its own blast radius.

## 6. ⛔ `145_pat_left_assoc_via_arbno_fence` IS **NOT** THIS CLASS — NAMED WITH EVIDENCE, AS THE DONE-WHEN ALLOWS

```
[RESUME-NIL] pat=PAT$1 right_sealed=0 pfenced=1 rn=0 fb=IR_MATCH_ASSIGN_COND fbtier=2
```

Its first body node is a **capture wrapper at tier 2**, not an alternation. It is refused by the FENCE-RESUME carrier scan's
tier-1-only test — the same refusal that owns `ptw_min_rseal_unsealed_ctl` (`fbtier=2`) — and it is **unmoved by this rung**
(`fail`, before and after). This is s183 §8's point restated with a measurement: *the tier-1 test is not the right predicate;
"can this node's β still yield" is.* **Widening the fence arm to tier 2 is a different rung with a different blast radius and
is deliberately not attempted here** (s180 admitted the capture wrappers to tier 2 for the *seam walk*; admitting them at the
*fence arm* is a separate question that owns the 7-mover fence class).

## 7. THE RUNGS THIS LEAVES, NAMED SO THEY CANNOT BE ORPHANED AGAIN

1. **`rseal-carrier-selection`** — s183 §6's second half: `sno_pat_right_sealed` seals the whole blob on its rightmost element,
   and allocation runs right-to-left, so "the first real body node" is the RIGHTMOST one. Owns `ptw_min_rseal_arbno` and
   `ptw_min_rseal_commands`, and beauty's `X4` (:128) and `Commands` (:217).
2. **`fence-arm-tier2`** — the fence arm admits tier 1 and 3; tier 2 is refused. Owns `145_pat_left_assoc_via_arbno_fence` and
   `ptw_min_rseal_unsealed_ctl`.
3. **`alt-nested-depth`** — the `_nc == 1` conjunct of §3(a) is a floor, not a law: a two-deep choice record needs its own
   depth story before `ptw_min_alttop_nofence_ctl` can go green.
4. **`sealed-defer-arm-tail`** — narrow §3(b) from "no `seal==1` DEFER anywhere in the blob" to s177's actual mechanism, "no
   ARM ENDS in one". Priced in this rung: `probe/fuzz/fz_diff_13` and `probe/fuzz/fz_segv_15` were cured by the
   `_nc == 1`-only build and are given back by the wider conjunct.

---

## 8. WHAT A LATER SEAT SHOULD TAKE FROM THIS

**A tier is a claim about ONE motion, and admission is a claim about the MACHINE that executes it.** HQ-73 got the first
exactly right — the manual and `p$alt` both say β re-yields at the entry cursor — and the rung still crashed twice, because
"this node's β can still yield" does not by itself say "and the record it reads is where it was written" or "and no arm's β is
a foreign-activation unwind". Those are separate facts, they were already written down by s121/s126 and s177, and the tier did
not make them go away. **Classify the motion in the lattice; keep the machine's preconditions at the admission.** The
alternative — folding the preconditions into the tier — would make the lattice lie again, which is the exact failure HQ-73
opened this row to end.
