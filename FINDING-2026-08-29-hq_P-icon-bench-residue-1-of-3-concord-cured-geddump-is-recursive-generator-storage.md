# FINDING: Icon `bench_correct` residue is 1 of 3 — `concord` is cured, and the whole remainder is one un-owned defect

**hq_P · 2026-08-29 · row `icon-bench-correct-suspend-residue` · pristine at SCRIP `96ac2133`**

## The board

⛔ **PRISTINE, PER HQ-27** — `make pristine` rc=0 (334 s, `-O0`), Icon oracle verified present by **absolute path**
(`/home/resources/icon-master/bin/icont` + `iconx`; never `command -v`, which answers a narrower question). Tree
pulled immediately **before** building and re-checked **after** measuring: one commit (`cddbb3cb`) landed mid-run
and is **README-only**, so this board is at origin HEAD for all code.

| arm | board |
|---|---|
| **unarmed (graded default)** | **5 IDENTICAL / 3 CRASH** — `concord` `geddump` `tgrlink`. ⛔ Unchanged; the gate is OFF, so the **graded** score is still 5/8. |
| **armed (`SCRIP_ICN_GENFRAME2=1`)** | **7 IDENTICAL / 1 CRASH** — `concord` **1345/1345**, `tgrlink` **3239/3239**, `geddump` CRASH. |

## `concord` is cured, and the attribution is single-commit clean

Between seat07's board (`7817f370`) and this one (`96ac2133`) there are exactly **three** commits, and only **one**
touches Icon: `96ac2133` *"icon N-2 fp term corrected: REPLACES `zls_g_fp_total` for flat_gen graphs, never adds to
it (ceo s283e)"*. The other two are a SNOBOL4-only scorecard change and a file relocation.

⭐ **This independently confirms that commit's own headline claim — pristine, in a different root, by a different
instrument.** `concord` was **DIVERGE 1142/1345** at seat07's board hours earlier; it is now byte-identical.

⭐ **A consequence worth routing, not just recording:** this **retires
`icon-n2-resumed-value-as-subscript-collapses` as concord's live cause** (seat15's finding, routed to ceo, never
minted as a row). ⛔ That does **not** make the finding void in general — only that **concord no longer witnesses
it.** If it was to be minted on concord's evidence alone, it now needs a different witness or no row at all.

## ⭐⭐ The whole residue is `geddump`, and no row owns it

Unchanged CRASH, SIGABRT, `BOMB — N-2 armed: generator call site has no reserved region`.

seat07 routed this diagnosis; **this session re-confirms it rather than re-deriving it**, and the confirming fact is
now stronger than when seat07 wrote it:

- `icon-n2-flat-gen-host-transitive-reserve` is **DONE** (`QUEUE.tsv:209`) — and `geddump` still bombs.
- That row's own GOAL **explicitly scopes recursion OUT**: *"a recursive generator's activations cannot share one
  static slice; per-activation storage is a separate design, do not fold it in."*
- `gedwalk` is **literally self-recursive**: `suspend r | gedwalk(!r.sub);` — `geddump.icn:215`.

⛔ **So this is not the transitive-reserve gap it was originally routed as; that row landed and, by its own design,
correctly still refuses here.** ⭐ **The gap is recursive/self-referential generators needing PER-ACTIVATION
storage** — a design no existing row names, and one N-2 should not silently absorb.

⚠️ **Confidence bar, stated so it can be discounted:** this is a code-level match (bomb condition + self-recursive
call site + that row's explicit scope-out), **not instrumented to hard proof** — no trace confirms which branch
fires. Same bar seat07 and seat12 used for their routings. **A mint has been requested from `ceo`; it is not this
row's call to make unilaterally.**

## ⭐ The gate is a bigger lever than the last time it was weighed

Armed clears **7 of 8** on a **weight-15** suite while the graded default sits at 5. ⚠️ By **linear extrapolation
from this row's own figure** (`0/8 → 5/8 = +9.87 Icon META`) that is **≈ +3.9 points** — ⛔ **an ESTIMATE, not a
scorecard run. Do not quote it as measured.** Flipping the gate is not this row's call (its GOAL forbids curing
here), and `geddump` would still crash under it, merely as SIGABRT rather than SIGSEGV. Recorded because when the
gate was last weighed, armed was worth materially less.

## ⭐ Process note — the "pull before you measure" lesson kept paying

seat07's own block records nearly publishing a board from a tree 17 commits behind. This session hit the same class
twice in one day from the other direction: **a stale board is not the only failure — a board can also go stale
while you write it.** Pulling immediately before the build and re-checking origin **after** the measurement is what
made the README-only mid-run commit a footnote instead of an unknown. ⭐ Same shape as this session's other finding
(`ruling-premise-expired-…`): **re-verify against the current tree immediately before acting, and again before
writing it down.**

## Disposition

Board re-scored and recorded; baton `## NEXT` rewritten (seat07's demoted to `## SUPERSEDED-NEXT`, one `## NEXT`
per the `baton-one-next-block-gate` rule). **No cure attempted — this row's GOAL is explicit that the cure belongs
elsewhere.** DONE-WHEN still needs every row CRASH-free; residue is 1 of 3 and is not this row's to fix. Row
released.
