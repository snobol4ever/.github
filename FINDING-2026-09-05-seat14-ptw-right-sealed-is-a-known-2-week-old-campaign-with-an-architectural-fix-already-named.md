# FINDING — the ptw right_sealed xfail trio is not fresh territory: a 2+-week-old documented campaign already named the mechanism and the architectural fix

**Seat:** seat14 · **Date:** 2026-09-05 ~13:10–13:35 CDT (box clock) · **Mode:** FLEET-20

**Found off:** row `snobol4-xfail-class-passthrough-window-ptw-5-entries` (owner hq_T), while re-verifying
seat13's twice-repeated census before adding to it. seat13's mechanism split (ledger entries 2026-09-04
19:1x and ~20:0x) had already flagged the "right_sealed-family" grouping of 3 of the 5 entries as "a
hypothesis from flag behavior only, not a code-read" — twice, unresolved both times.

## The claim

That hypothesis is correct, and it was resolvable from things already sitting in the tree: an actual
code-read of `sno_pat_right_sealed`, in-corpus witness comments that already state the mechanism almost
verbatim, and a `GOAL-SNOBOL4-100.md` history entry from s182/s183 (~2026-08-20) that investigated this
exact defect class in much greater depth than this row's own history shows. None of the three had been
consulted by this row before now.

## Measured

**1. Code-read, `src/lower/lower_snobol4.c` (current tip, commit `674319235`):** `sno_pat_right_sealed`
(~line 1876) recurses on `t->c[1]` ONLY for `TT_SEQ`/`TT_CAT`. A pattern `A B` where `B` is (or reduces to)
a `FENCE` is marked fully sealed — `gp->body_root = NULL` at both call sites (`sno_pat_publish_body_root`
~2519, `sno_pat_tree_graph_rt` ~2775) — discarding any resume surface for `A`'s own alternatives too, not
just `B`'s. `SCRIP_FENCE_IGNORE` only zeroes `pfenced` inside the structurally disjoint
`sno_pat_carrier_build` (~2503); it cannot touch this path. This is a real, mechanical reason `1858`
(`arbno_fence_pos_replace_branch_4`) goes green under the flag while `1849`-family siblings do not.

**2. Pre-existing in-corpus comments say the same thing, unquoted by this row until now.** Extracted via
`corpus_suite_harness.py extract`:
- `arbno_fence_pos_replace_branch_3` (current name; positionally 1859 today, drifts): *"sno_pat_right_sealed
  seals the WHOLE blob because its RIGHTMOST element is a fence form, but the manual's seal only forbids
  re-offering the FENCE'S OWN alternatives -- the ARBNO to the fence's LEFT still has instances to give...
  SCRIP_FENCE_IGNORE=1 does not cure it (right_sealed short-circuits the carrier the fence path computed)."*
- `arbno_fence_pos_replace_branch_4`: *"Identical to ptw_min_rseal_arbno with a trailing epsilon appended,
  which moves the fence off the right end: right_sealed flips 1 -> 0... SCRIP_FENCE_IGNORE=1: GREEN. So the
  seal and the fence verdict are two independent refusals on the same blob."*

These match the code-read exactly and predate this row.

**3. `GOAL-SNOBOL4-100.md` already has a deeper account, from s182/s183 (~2026-08-20), never referenced by
this row.** Quoting its "THE FINDING" entry: *"The row split beauty's five `body_root=NULL` blobs into (a)
`PAT$12/PAT$20` pure fence refusal and (b) `PAT$13/PAT$22/PAT$28` `sno_pat_right_sealed`. Both classes are
real; **neither is refused for the reason its name says.**"* — allocation runs right-to-left, and an
untiered seam-tier disjunction is implicated; the "wholesale seal" story above, while true, is not
necessarily the *complete* story. A cure landed at the time for adjacent witnesses (`floor`, `pp_L2`,
`pp_L3`, `defer2_arbno`, `depth9`, `ptw_min_fence_left_altresume`) but explicitly did **not** close
`rseal_arbno`/`rseal_commands`/`rseal_unsealed_ctl` — this row's own three right_sealed entries are that
campaign's documented, still-open remainder, not new territory.

**4. The project's own architecture backlog already names the sanctioned fix, and it is not a local patch.**
`GOAL-SNOBOL4-100.md` R-4 item (h), quoting a Lon ruling from s121 ("You should make FENCE0 a BB"): FENCE0
is compile-time rewiring today, "forcing a SHADOW METADATA SYSTEM (`IR_t.seal`, `sno_pat_right_sealed`, the
seal==1 β-target ban) that is the root of fence-via-var failures." The prescribed ladder (h1 mint box, h2
migrate `TT_SEQ` to a uniform fail chain, h3 retire the s121 refuses, h4 demote the s137 whack to pure
optimization) has **not been started**.

**5. Both `.md` files every one of these 5 xfail reasons (and `board_passthru_combo.sh`'s own header) cite
as "the campaign's documentation" do not exist.** `ARCH-PASSTHRU.md`: absent from SCRIP, corpus, and
`.github` (re-confirmed 2026-09-05; seat13 already found this 2026-09-04). The FINDING file item 3 quotes
from — `FINDING-2026-08-20-s183-both-blob-resume-refusals-bottom-out-in-an-untiered-disjunction.md` — is
also absent; only `GOAL-SNOBOL4-100.md`'s own account of it survives on disk.

**6. Side note, not blocking:** `sno_pat_right_sealed`'s original rationale comment (the s137 Lon-ruling
text, dual-consumer explanation, transitive-through-VAR/DEFER note) was deleted wholesale by the
2026-08-20 comment-strip pass (`e25a5daf5`, "GOAL-STYLE-200COL REACTIVATION 4") and never rebuilt. Attempted
to restore an upgraded version of it (rationale + this finding's pointer) as a source comment; the
`commit-msg`-adjacent staged-file hook refused it — **`src/` carries a live, enforced ZERO-COMMENT
invariant** (`strip_comments.py --check`, first arm of `make test`), which contradicts this root's own
`CLAUDE.md` digest (which claims an "AMENDED 2026-08-30" WHY-comment policy reversal for exactly this kind
of ruling-encoding function). The hook is live, mechanical, enforced-on-every-seat ground truth; the digest
claim is stale. No source touched in the end — this FINDING is the correct medium instead, per the hook's
own suggested remedy.

## Not claimed

- Whether items (a) `PAT$12/PAT$20`-style pure fence refusal and (b) `sno_pat_right_sealed` interact only
  in the way the s182/s183 FINDING describes, or whether that account is itself now stale (it is 2+ weeks
  and many commits old). Nobody has re-run the `[RESUME-NIL]`/`SCRIP_RESUME_WHY` instrument against current
  `HEAD` for these specific 3 witnesses. That would be the right next step before anyone starts the R-4(h)
  ladder, not a repeat of the code-read this FINDING already did.
- Whether `arbno_fence_pos_branch_22` (`ptw_min_arbno_alt_fence_L1`, an `ARBNO(... FENCE(...))` shape one
  level of nesting different from the other two) shares the identical root cause or only the same symptom
  family — it carries no in-corpus explanatory comment the way the other two do, and I have not traced it
  as carefully.

## Recommendation

Route the right_sealed/fence-verdict group (current names `fence_pos_rpos_replace_branch_3`,
`arbno_fence_pos_replace_branch_3`, `arbno_fence_pos_replace_branch_4`, `arbno_fence_pos_branch_22`) to
whoever owns the R-4(h) FENCE0→BB ladder as a shared-node/architectural class, with this FINDING attached,
rather than having a fourth seat re-derive the same conclusion from zero. The fifth entry
(`arbno_pos_rpos_branch_81`, the hang) has no FENCE in its witness at all and reads as an unrelated
deferred-ARBNO-reentry non-termination bug — recommend splitting it into its own row.
