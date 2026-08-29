# FINDING 2026-08-29 hq_C — the ARBNO reentry proxy is TWO questions landing on TWO DIFFERENT NODES; the discriminator is measurable, is still insufficient, and the fact seat13 called unresolvable IS resolvable at IR level

**Row `fuzz-nondeterminism-rootcause`, taken by hq_C on Lon's direct ruling** (*"It appears to be a very tough one and is being passed around. You should take the difficult ones."*) after six sessions (hq_B, seat13 ×3, seat11, seat16, seat09) with no landed fix. **This session's candidate is ALSO REJECTED** — measured, reverted, tree clean. What is new is structural, and it retires two beliefs the row had been running on.

## ⭐⭐ 1. THE PROXY IS NOT ONE QUESTION MIS-ANSWERED — IT IS TWO QUESTIONS THAT LAND ON DIFFERENT NODES

`arbno_frame_candidate()` answers **"does this ARBNO need its own frame slot"** (storage). `resume_carrier_ok()` reads that answer as **"is this ARBNO a backtrack-reentry hazard"**. Every prior session treated this as one predicate needing better tuning. **Measured, it is two predicates whose correct answers land on two different ARBNOs in the same program.**

`fz_segv_24` is `G0 = ARBNO(TAB(1) BAL)` · `P = ARBNO(*G0)` · `'aa a' POS(0) *P RPOS(0)`. It compiles to **three graphs**, and `arbno_frame_candidate` is called for **both** ARBNOs:

| graph | node | body | why it needs what |
|---|---|---|---|
| `proc PAT$0` | `ARBNO(TAB BAL)` | `MATCH_TAB` (zd_k=16), `MATCH_BAL` (zd_k=16) | **needs its FRAME** — genuine storage need |
| `proc PAT$1` | `ARBNO(*G0)` | `MATCH_DEFER pat_static=0 seal=2 name="G0"` | **needs the reentry GUARD** — the composition hazard |

⛔ **THIS EXPLAINS seat11's RESULT THAT LOOKED SELF-CONTRADICTORY.** seat11 measured that the narrow predicate (`op==DEFER && !pat_static`) fixes patterns 143/145 but **loses the original fuzz witnesses**, which reads as "the hazard is not defer-shaped". It is defer-shaped. The narrow predicate correctly guards `PAT$1` **and simultaneously un-frames `PAT$0`**, whose frame was never about defers at all. One predicate was carrying two loads; removing the wrong load dropped the right one. **Collapsing the two questions is what fails, not the choice of test.**

## ✅ 2. THE DISCRIMINATOR THE ROW BELIEVED DID NOT EXIST — MEASURED ON ALL THREE WITNESSES

seat13 concluded *"no cheap predicate can tell that apart from a genuine hazard today"*. Measured with a temporary instrumented build (`HQC_HAZ`, since removed):

| witness | body defer | `pat_static` | name | contains `$` | verdict |
|---|---|---|---|---|---|
| `fz_segv_24` / `fz_red_m1b` (`PAT$1`) | yes | **0** | `G0` | no | **HAZARD** |
| `143_pat_regex_quantified_class` | yes | **1** | `LP` | no | not a hazard — statically resolved |
| `145_pat_left_assoc_via_arbno_fence` | yes | **0** | `PAT$1$V1` | **yes** | not a hazard — synthesized capture plumbing |

`IR_MATCH_DEFER && !pat_static && !strchr(name,'$')` separates all three, each excluded by a *different* clause.

⭐ **THE `$` TEST IS A NAMESPACE INVARIANT, NOT A HEURISTIC.** `snobol4.l`'s `IDCONT` is `[A-Za-z0-9_.\x80-\xFF]` — **`$` cannot occur in a user-written SNOBOL4 identifier** — so any defer name containing `$` is compiler-generated *by construction*. The same reserved namespace is already load-bearing in `zd_k`'s `PATV$` carve-out (SCRIP `2e7685db`).

## ⛔ 3. AND IT IS STILL NOT SUFFICIENT — REJECTED ON A MEASURED REGRESSION

Wired as a separate predicate into `resume_carrier_ok` (leaving `arbno_frame_candidate` untouched for the storage question):

- ✅ **Fuzz witnesses: 3 of 5 became DETERMINISTIC**, against a before-arm captured on the same tree with the change stashed. Baseline `fz_red_m1b` 6×empty/4×`nomatch`, `fz_segv_24` 4×empty/6×`nomatch`, `fz_red_m4b` 2×empty/8×`nomatch` — all three genuinely non-deterministic, which is the row's actual blocker (`convert`'s byte-equal check refuses a source that disagrees with itself). After: 10/10 identical each. **`fz_red_m4b_blob_defer_fence` also became CORRECT** (ref `nomatch`).
- ✅ **143 and 145 both correct** — `matched aabbcc`, `first=1 last=5`. Every prior candidate broke at least one.
- ⛔ **SNOBOL4 corpus m3 1327→1312, m4 1327→1312: FAIL=15.** Hard gate. Reverted.

**Every failing entry is a defer case** — `alt_captarm_defer_red`, `m1_beauty_arbno_defer_min`, `m1_defer_ALT`, `m1_defer_LEN0`, `m1_defer_SPAN`, `seam_gen_rightmost_green`, and six `passthru/ptc*_var*`. So the predicate is **necessary but too broad**: it fires on legitimate non-static user defers whose target is harmless. Name + `pat_static` identifies *a genuine user defer*; it does not identify *the hazardous composition*.

## ⭐⭐ 4. THE MISSING FACT IS ARBNO-INTO-ARBNO, AND IT IS RESOLVABLE AT IR LEVEL — WHICH THE ROW BELIEVED IT WAS NOT

The hazard is an ARBNO deferring to a pattern **that is itself an ARBNO** — reaching into another ARBNO's own RBP frame. seat13 ruled this out as unavailable: *"MATCH_DEFER carries only a name string at IR level; the existing name-to-pattern resolution, sno_const_pat / sno_seal_pat, lives in lower_snobol4.c only, and AST walking downstream of LOWER is forbidden."*

⛔ **That is true of the AST route and false of the graph route.** The binding is plainly present in the IR, in `main`'s own graph:

```
2   LIT_STRING  "PAT$0"
3   CALL   [2]  "SNO$MKPAT"
4   ASSIGN [3]  var="G0"        <- name -> PAT$N binding, at IR level
...
; proc PAT$0
0   MATCH_ARBNO [3,3,4]         <- the target's shape, inspectable
```

So `G0` → `PAT$0` → *that graph's root is an `IR_MATCH_ARBNO`* is answerable by walking **compiled graphs** (`g_stage2.bbp.table[]` / the proc table), with **no AST walking and no new IR field** — so it clears both the no-AST-walking law and the PEERS RULE that blocked seat13's option (a). **The information was never missing; the wrong resolver was consulted.**

## THE DESIGN, STATED FOR THE NEXT ACTOR
1. Keep `arbno_frame_candidate` **exactly as is** — it is the storage question and its current answer is right. ⛔ Do not merge the hazard test into it.
2. Add a separate hazard predicate for `resume_carrier_ok` only: body defer with `!pat_static`, name free of `$`, **and** whose target graph's root is `IR_MATCH_ARBNO`.
3. Grade against **all three** arms, because passing any two is what has repeatedly looked like success: the 5 fuzz witnesses (determinism, 10 runs each, before-arm on the same tree), crosscheck 143/145, and the full SNOBOL4 corpus at FAIL=0 — the 15 named regressions above are the specific control set.

## ⚠️ CLUSTER SEPARATION, CONFIRMED INDEPENDENTLY THE SAME HOUR
`fz_red_m4a_blob_alt_fence_defer` and `fz_segv_09` were **already deterministic** (10/10 empty) before and after, and are untouched by any of this — seat09's same-session Cluster A finding (`PAT$N_res` hard-coded stack offset, `FINDING-2026-08-29-seat09-...`) is the mechanism for those two. **The row is two independent defects and the 5 witnesses split 3/2.** Six sessions all converged on Cluster B; nobody had partitioned the witness set, so Cluster A's two were silently counted as evidence about Cluster B's predicate the whole time.

## ⚠️ CORRECTION TO §3, BY hq_C, SAME SESSION — MY DETERMINISM CLAIM WAS MODE-3-ONLY AND I DID NOT SAY SO

hq_B (relayed via seat11) flagged that `fz_red_m4b_blob_defer_fence` and `fz_red_m4a_blob_alt_fence_defer` are **unsafe as A/B witnesses** — an A/B they ran read *"all identical"* by luck and was only caught by a disagreeing run minutes later. That lands directly on my own numbers, so I re-measured at **30 runs** on the reverted tree:

| witness | baseline, 30 runs, **mode 3** |
|---|---|
| `fz_red_m4b_blob_defer_fence` | **17 empty / 13 `nomatch`** — strongly non-deterministic |
| `fz_red_m4a_blob_alt_fence_defer` | 30/30 empty — stable **in m3** |
| `fz_segv_09` | 30/30 empty — stable **in m3** |

**What survives:** `fz_red_m4b` really is ~50/50 at baseline, so the post-change 10/10 identical is not luck (p ≈ 0.002 if the coin were unchanged). The §3 result stands *as far as it goes*.

⛔ **What does NOT survive is the word "deterministic" unqualified.** Every run in §3 was **mode 3**. hq_B's instability for the Cluster A pair is a **mode-4 crash-signal** effect, which m3-only runs cannot see — which is why their measurement and mine disagree while both are correct. ⭐ **My instrument answered a narrower question than my sentence claimed**, which is the exact family this FINDING is about, committed by its own author two hours after writing it up. The honest statement is: *10 of 10 identical in mode 3*, not *deterministic*.

✅ **ENDORSED AS A PREREQUISITE FOR THIS ROW:** hq_B's ask for an N-repeat-refuse-on-disagreement runner over the whole `probe/fuzz/` set, **covering both modes**, before anyone grades a cure against these witnesses. A witness set whose own stability is unmeasured cannot falsify anything, and this row has spent six sessions grading candidates against it.

## ⚠️ SECOND CORRECTION, SAME DAY — I WAS WRONG ABOUT `fz_red_m4a` TOO, AND THE RUNNER I BUILT IS WHAT CAUGHT IT

The prerequisite runner is now built (`scripts/util_fuzz_witness_stability.sh`, SCRIP `4026774a`): N repeats, **both modes**, **(stdout, rc) compared as a pair**, refusing on any disagreement. Its first run, N=10 at SCRIP `f5231fa6`, over 5 witnesses × 2 modes:

| | pairs | detail |
|---|---|---|
| **UNSTABLE** | 5 | `fz_red_m1b` **m3+m4** (rc 0 vs **124** — a HANG, not a wrong answer) · `fz_red_m4a` **m3** (rc **132/133/139**) · `fz_red_m4b` **m3+m4** (rc 0 vs 139) |
| **STABLE** | 5 | `fz_red_m4a` m4 · `fz_segv_09` m3+m4 (rc=139, a *deterministic* SEGV) · `fz_segv_24` m3+m4 (rc=0) |

⛔ **In the correction above I wrote that `fz_red_m4a` was "30/30 empty — stable in m3". It is not stable.** Its **stdout is constant empty while its rc cycles 132/139** — re-confirmed directly (8 runs: rc=132 ×1, rc=139 ×7, stdout empty every time). My 30-run sample compared **stdout only**, so it was structurally incapable of seeing the axis hq_B measured. hq_B was right, in both of the two exchanges we had about it.

⭐⭐ **NEITHER OF US WAS CARELESS, AND THAT IS THE POINT.** hq_B sampled rc; I sampled stdout; **each of us called our own instrument "the witness"**, and no step in either procedure could have reported the omission. This FINDING's own thesis — an instrument answering a narrower question than the sentence built on it — was then committed twice, within hours, by the two people writing it up. ⛔ **The cheap general test survives intact and would have caught both of us: *what would be different if my instrument were blind to half the answer?* If nothing observable, you are measuring a habit.**

⚠️ **`fz_segv_24` now reads stable rc=0 in both modes, where §3's same-day baseline had it 4×empty / 6×`nomatch`.** Do **not** resolve that by declaring one measurement wrong — **the tree moved between them**, other seats landed codegen, and that is the REBASE-BASELINE COROLLARY. It is why the runner stamps its SCRIP and corpus hashes on every run.

⛔ **CONSEQUENCE FOR THE ROW: every rejection in its ledger is partly suspect, §3's included.** Six sessions graded candidates against a set in which **5 of 10 witness×mode pairs disagree with themselves**. The order is now fixed — run the script, stabilise or explicitly exclude the unstable pairs, and only then grade a cure. ⭐ `fz_segv_09`'s deterministic rc=139 makes it the single witness that can falsify a **Cluster A** cure today; Cluster B has no usable arm until its three are stabilised.
