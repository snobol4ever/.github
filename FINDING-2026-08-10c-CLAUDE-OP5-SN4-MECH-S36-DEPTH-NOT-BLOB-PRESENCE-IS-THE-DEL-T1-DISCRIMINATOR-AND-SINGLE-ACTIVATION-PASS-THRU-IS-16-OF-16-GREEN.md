# FINDING 2026-08-10c (s36, Claude Opus 5) — MEASUREMENT ONLY, ZERO CODE TOUCHED

**Goal:** `GOAL-SN4-ZETA-MECH` · **Container:** fresh, 1 CPU, RT_OPT=`-O0` · **No `src/` edit, no regen, no commit to SCRIP/corpus.** Only this file + the MECH cursor.

Measured at SCRIP `a5533659` (3 commits past the s35 cursor HEAD `c7e085fd`; `c7e085fd`, `a5c22641`, `26bdc332` all confirmed ancestors). Oracle: `/home/claude/x64/bin/sbl -b`.

---

## 0. WATERMARK RE-PROVED — DIGIT-IDENTICAL TO s35, BOTH MODES

`run_suite.sh`, all 151 probes: **m3 133/15/0/3** · **m4 132/16/0/3**. REGRESSION set both modes = **D12 · D13 · H31**, none listed in either XFAIL. This reproduces the s35 cursor exactly on a different container — the counts are stable, not a container artifact.

⭐ **m4 is now measured.** Both prior DEL-T1 findings (08-10b ×2) explicitly disclosed *m3 only*. The three regressions are present in **both** media, so this is not a TEXT/BINARY asymmetry.

## 1. ⛔ THE s35 BISECT PRESCRIPTION IS VOID — DO NOT SPEND THE ~6 BUILDS

s35 routes the next seat to `git bisect start main a5c22641` with D12 as discriminant. That search is unnecessary: two parallel seats already convicted the DEL-T1 trio on 2026-08-10 (`1af93e3a` D-1 · `1f96143c` D-2 · `ef8a3052` D-3), and this session independently confirms the mechanism from the source at HEAD. s35's inherited framing ("op_flat_disp correctness for the capture-δ interior") came from the **s9 cursor, which the 08-10b findings had already falsified**; s35 did not have them.

## 2. ⛔⭐ "EVERY BLOB-BEARING PROGRAM FAILS" IS FALSE — THE DISCRIMINATOR IS DEPTH, NOT BLOB PRESENCE

`FINDING-2026-08-10b-...-DEL-T1-BROKE-EVERY-ENTERED-BLOB...` states *"Every blob-bearing program fails at HEAD … Correlation with blob presence: perfect, 4 of 4."* **Falsified by two probes already in the suite:**

| probe | stored pats | `g_blob_ctx` refs | `proc_PAT` defs | re-entrant? | result |
|---|---|---|---|---|---|
| D10 `ARBNO(*P . W)` | 1 | 6 | 18 | **no** | **PASS both modes** |
| D11 `ARBNO(*P)`, P alternation | 1 | 6 | 17 | **no** | **PASS both modes** |
| D12 / D13 `*LIST` mutual recursion | 2 | 12 | 37 | yes | SEGV 139 |
| H31 FENCE-over-ALT, 7 stored | 7 | 42 | 129 | yes | SEGV 139 |

D10 carries **18 PAT$ blob defs and 6 `g_blob_ctx` refs and is green in both media.** Blob presence does not predict failure.

**Constructed witnesses settle count-vs-depth** (all oracle-compared; `sbl` answer first):

| witness | stored | ctx refs | re-entrant | sbl | scrip | class |
|---|---|---|---|---|---|---|
| `W1_seq` — `*A *B` sequential | 2 | **0** (PT-3 inlines invariant `*name`) | no | `=S` | `=S` | AGREE |
| `W2_nest` — `LIST = '(' *ITEM ')'`, no recursion | 2 | 12 | **yes (depth 2)** | `=S` | **`=F` rc=0** | ⛔ **SILENT WRONG** |
| `W3_selfrec` — one self-recursive pattern | **1** | **6** | **yes** | `=S` | HANG 124 | ⛔ |

⭐ **`W3_selfrec` is the conviction:** ONE stored pattern, the *identical* 6-ref cell footprint as the passing D10, and it hangs — purely because it re-enters. **Depth, not count, not presence.**

**Witness sources** (inlined so the next seat need not reconstruct them; **deliberately NOT promoted** to `corpus/probe/` — a known-fail `.ref` moves the watermark other seats gate on, per the s5 precedent the 08-10b seat cites. Promote inside the rung that fixes them):

```
W2_nest.sno  — depth 2, NO recursion        W3_selfrec.sno — depth>1 at COUNT 1
        SUBJ = '(12)'                               SUBJ = '((7))'
        ITEM = SPAN('0123456789')                   LIST = '(' (SPAN('0123456789') | *LIST) ')'
        LIST = '(' *ITEM ')'                        SUBJ ? POS(0) *LIST RPOS(0)      :F(NO)
        SUBJ ? POS(0) *LIST RPOS(0)   :F(NO)        OUTPUT = '=S'                    :(EN)
        OUTPUT = '=S'                 :(EN)   NO    OUTPUT = '=F'
NO      OUTPUT = '=F'                         EN
EN                                            END
END
```
`sbl -b` answers **`=S`** for both. scrip: `W2_nest` → **`=F` at rc=0**; `W3_selfrec` → **HANG 124**. `W1_seq` (the control: `A`/`B` used sequentially, `SUBJ ? POS(0) *A *B RPOS(0)`) emits **zero** blobs — PT-3 inlines invariant `*name` — and agrees.

## 3. ROOT CAUSE, READ FROM THE SOURCE AT HEAD (not inherited)

The per-activation cell **already exists and is correct**. `emit.cpp:2359+` α carve writes this activation's header into its **own spine cell**: `sub rsp,kt` then `[rsp+kt-24]`=γ wire · `[rsp+kt-16]`=ω wire · `[rsp+kt-32]`=scan flag · `[rsp+kt-40]`=attempt δ0. That part is sound and depth-correct.

The defect is the **mirror**. α then publishes the same quad *plus the cell base* into the process-global `uint64_t g_blob_ctx[5]` (`pattern_match.c:624`), and **every reader re-bases off the global, never off its own cell**: scanhit `2734` · scanfail `2738` · β res-stub `2763/2773` · CLASS-D γ `2815` · CLASS-D ω `2832` — each does `mov rcx,[rdx+0]` where `rdx` = `&g_blob_ctx`. On nesting, the inner α's publication overwrites the mirror; the outer's γ/ω then restore a base belonging to a **different activation**.

The contradiction is self-documented. `pattern_match.c:624`'s own comment licenses the single cell only under a **"NON-NESTING assumption … TT_DEFER is excluded from invariance"** — while the arming gate `emit.cpp:2358` keys on `flat_pat` alone and never tests defer-freedom or nesting. D12's `*LIST` **is** `TT_DEFER`.

**Manual concurrence (independently read this session):** Ch.9 p.123 — *"SPITBOL saves information on a stack during the pattern match process. Heavily recursive patterns … can result in stack overflow"* — and the p.122 `ITEM/LIST` example is D12 **verbatim**. The matcher is specified as a pushdown; one global cell cannot represent a stack of activations.

## 4. ⭐ THE REPAIR IS SAVE-BY-VALUE ON THE SPINE — AND `[kt-8]` ALONE IS **NOT** ENOUGH (self-correction)

`emit.cpp:2367` says *"`[kt-8]` is now dead pad where the caller-rbp save lived,"* which invites the obvious fix: park a **dynamic link** there. ⛔ **Measured and rejected — two independent reasons:**

1. **Width.** The readers consume five words (`[+0]` base · `[+8]` γ · `[+16]` ω · `[+24]` scan flag · `[+32]` δ0). `[kt-8]` is ONE 8-byte slot.
2. **`kt` is NOT uniform, so a link/pointer cannot be dereferenced.** Distinct `sub rsp,N` carve sizes measured in one program: **D12 → 64, 80, 128, 224; H31 → 64, 80, 144, 160, 176, 192; D10 → 96, 112.** A parent's header lives at `[parent_base + parent_kt - 24]` etc., and **`parent_kt` is not knowable at the restoring blob's compile time.** Chaining to the previous cell therefore cannot restore it.

⭐ **Corrected design — save the five words BY VALUE, in a block addressable from the blob's OWN base with its OWN `kt`:**

1. **α**, before the existing carve: `sub rsp,48` (48 not 40 — preserve 16-byte alignment; C-ABI ALIGN is a licensed raw-rsp use per LAWS) and store `g_blob_ctx[0..4]` → `[rsp+0..32]`. Then the existing `sub rsp,kt` + header fills + publish (base = post-carve rsp). The save block now sits at **`[base+kt .. base+kt+32]`**.
2. **γ (suspend) · ω (total failure) · β (res-stub)** — each already obtains the base via `mov rcx,[rdx+0]`; add `g_blob_ctx[0..4] ← [rcx+kt .. rcx+kt+32]` before leaving/republishing. **Every site uses its own `kt` and its own base — no cross-blob knowledge required.** That is what makes this work where the link does not.

Preserves D-1's charter (`mov rbp,rsp` = 0 in blobs; the `.s` evidence is unchanged) and stays register-free, which was the entire reason the global was introduced.

⚠ **Risk to price before starting:** the extra 48 bytes shifts the spine. Interior readers speak `rsp+op_flat_disp` relative to post-carve rsp (= base, unchanged) and should be unaffected, but the ω *drain-to-entry-depth* accounting and any **ΣK ZPOP fold** must absorb the +48. Verify against MODEL-THE-POP (γ=zout−zgpop, ω=zout−K−zwpop) before trusting a green suite.

**Both media mandatory, ~8–10 arms.** Not attempted this session — see §6.

## 5. ⭐ BLAST RADIUS RE-MEASURED AGAINST THE ORACLE — AND STRATIFIED

`corpus/crosscheck/patterns`, 122 programs, `scrip --run` vs `sbl -b`, same container, same HEAD:

**AGREE 69 · CRASH 41 · SILENT-WRONG (rc=0, diverges) 12.**

Stratified by cell footprint — **internally controlled, no second build required**:

| footprint | programs | broken | rate |
|---|---|---|---|
| no blob | 70 | 20 | 29% — background/pre-existing |
| single activation (ctx≤6) | 18 | 2 | 11% |
| nested (ctx>6) | 34 | 31 | **91%** |

The 2 "single-activation" casualties are `066_pat_fence_fn_**nested**` and `115_pat_fence_via_var_**recursive**` — **both re-entrant with one stored pattern**, i.e. the `W3` shape. The footprint proxy counts *patterns*, not *depth*, and it fails exactly where the law predicts.

⭐ **Corrected: true non-re-entrant blob programs are 16 of 16 GREEN.** Single-activation pass-thru **works**.

⭐ **FALSIFICATION ATTEMPTED AND SURVIVED — and it sharpens the predictor.** The three nested-footprint survivors were inspected specifically to break the law; all three are **non-re-entrant in execution**:

- `113` — `*cmd1 *cmd2`: two stored patterns **side by side**, never one inside the other. Depth 1.
- `181` — four independent patterns (`P`,`Q`,`R`,`W`), each in its own sequential match. No cross-reference. Depth 1.
- `118` — `outer = ARBNO(*cmd)` is assigned on the line **after** the match statement, so at match time `outer` is still null; `*outer` defers to the null string and **`cmd`'s blob never activates inside `outer`'s**, though both exist statically.

⭐ **Therefore the predictor is DYNAMIC re-entrancy, not static blob structure**, and both directions of proxy error fall out of that one distinction: `066`/`115` are static count 1 but dynamically re-entrant (**broken**); `118` is static count 2 but dynamically depth 1 (**green**). Any future census that ranks by static blob count — as the ctx-ref footprint does — will misclassify in both directions. Rank by re-entrancy.

**Honest correction to my own first reading:** the SILENT-WRONG class is real and demonstrable inside the DEL-T1 zone (`W2_nest`, oracle-verified; `066` in corpus), **but 11 of the 12 corpus silent-wrongs carry ZERO blobs** — the `fence_fn` and `BAL` families — so they are pre-existing defects, not DEL-T1 casualties. Crash-only counting does undercount, but by less than I first implied. The standing law still bites: **exit 0 is not exoneration.**

## 6. ROUTING — THE REVERT-vs-FIX-FORWARD CALL HAS CHANGED

The 08-10b seat recommended **revert the DEL-T1 trio**, reasoning that no blob entry works at all. That premise is falsified (§2, §5). A full revert would hand back `mov rbp,rsp` in **every** blob to repair a defect confined to the re-entrant class, discarding 16-of-16 working, charter-compliant pass-thru.

⭐ **Recommendation: fix forward with the §4 dynamic link.** Narrow, register-free, uses an already-dead slot, satisfies the design of record, and keeps Lon's "never want to see that code again" directive discharged. Revert remains the fallback if the link proves it needs more than `[kt-8]` can hold.

**Not done / disclosed:** no pre-D-1 build, so no BY-SET delta of my own (the §5 stratification is within-HEAD and needs none). Repair not implemented. No regen (no codegen touched). `broad-336` not run. gdb not used — the sibling-pair discriminator settled it before any code was read, per RULES' cheapest-experiment clause.

**Carried, unowned:** `GOAL-PASSTHRU-RBP-ERAD` is still absent from PLAN.md's Active Goals and from the CONCURRENT SET (9) while landing commits that touch `lower_snobol4.c` — s35 flagged it and it is still unrouted. `bb_match_end.cpp` 12×r10 TIER-2 · `128_pat_recursive_grammar` · regen ×3 window.
