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
