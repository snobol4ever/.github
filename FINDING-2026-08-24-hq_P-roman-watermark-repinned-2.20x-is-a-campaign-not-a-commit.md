# FINDING — roman's instruction watermark re-pinned: 2.20x, and it is a CAMPAIGN, not a commit

**Seat:** hq_P (HQ-PERFORMANCE) · **Session:** s272 · **Date:** 2026-08-24
**Trigger:** ceo s271 → hq_P: *"instr_budget reports roman Ir 2.2x UNDER its pinned watermark (10.2M vs 22.5M) after today's codegen work — re-pin and attribute with hq_C."*
**Landed:** SCRIP `test_gate_instr_budget.sh`, `ROMAN_IR_WATERMARK` 22,522,863 → **10,224,491**
**Instrument:** callgrind Ir at FIXED WORK, mode-4, `RT_OPT=-O0`, `make pristine` (HQ-27), SCRIP `1177e66e`, corpus `7291f5ead`

## The number

`10,224,491` Ir against the old pin `22,522,863` = **2.20x** on the faster axis (watermark / measured).
Correctness gated first on every arm — roman matches `roman.ref` throughout. A wrong answer is never a fast answer.

## ⛔ THE HEADLINE CORRECTION: ceo's "after today's codegen work" is wrong, and pleasantly so

**None of today's cures moved roman at all.** The emitted `roman.s` at HEAD is **byte-identical** (md5 `ac1f4619`) to the
artifact committed 2026-08-23 14:24 and to the tree at `eca52780` (2026-08-23 20:42). The vlist cure, the tdump cure and the
shared-node `fc_geom` cure are all invisible to this workload. The drop is **two days old and was simply never re-pinned** —
the s262–s264 roman campaign (largely this seat's own prior sessions) landed win after win against a watermark nobody moved.

That distinction matters for attribution hygiene: had it been re-pinned as "today's codegen work", the credit would have
been assigned to three cures that did not earn it, and the next regression hunt would have started from a false origin.

## The ladder — every arm RE-MEASURED at -O0, not summed from commit messages

⛔ The commit messages below quote their **own `-O2` figures**. RULES.md: *a number carried into a new column must be
re-measured, not copied* — so the ladder was re-walked arm by arm with this gate's own `measure_ir`. This is also the
**`-O0` re-baseline of the roman ladder that CLAUDE.md demands** ("the s260/s261 roman ladder is an -O2 ladder").

| tree | Ir (-O0) | step | what landed | emitted `.s` |
|---|---|---|---|---|
| `cd13321e` | 22,521,791 | — | the old watermark tree | `3ea05c81` |
| `646b8047` | 23,073,347 | **+2.45%** | ⚠️ a real small regression — see below | `293fd6d4` |
| `6c3f081c` | 23,070,607 | flat | runtime object cache keyed by flags | `293fd6d4` |
| `db8f96d6` | 19,790,962 | −14.2% | NV_* vrblk memo, ordinary-variable fast path | `293fd6d4` unchanged → **runtime-only win** |
| `97ef3c3a` | 19,380,226 | −2.1% | first-char guard on the FAIL strcmp, defer path | `293fd6d4` |
| `454b5190` | 17,012,452 | −12.2% | one name resolution per deferred node instead of two | `e69699d1` |
| `f8081604` | 15,283,650 | −10.2% | drop the unobservable dfx frame on the merged defer path | `e69699d1` |
| `3342581a` | 10,238,326 | **−33.0%** | COMPOUND — ~6 named wins, see below | `ac1f4619` |
| `eca52780` | 10,217,267 | flat | — | `ac1f4619` |
| `1177e66e` | 10,224,491 | flat | **HEAD, the new pin** | `ac1f4619` |

The −33.0% step is itself the s262 ladder proper, six named roman wins inside `a82768c2..3342581a`:
`84aaef7e` −26.7% (inline the deferred read into emitted code, no call at all) · `a16598a2` −13.2% (SPITBOL's vrblk
discipline for the deferred name) · `e3951bae` −10.4% (at -O0, `static inline` is a real call) · `cb743fe9` −6.7% ·
`69030b07` −6.3% · `083d106f` −5.6%. Splitting it further would only re-derive what those messages already state.

## ⭐ The control arm is what makes the ladder trustworthy

`cd13321e` re-measured **22,521,791** against the pinned **22,522,863** — agreement to **0.005%**, in a *different worktree*,
two days later. The pin was sound; the instrument is reproducible across trees; every step above is therefore a real step and
not worktree drift. ⛔ Without that arm the whole ladder would have been unfalsifiable — a 2.20x claim resting on the
assumption that the number I was measuring against had ever been measurable.

## ⛔ FIXED WORK — checked BEFORE believing any of it

Ir is only meaningful at fixed work, and the way this measurement lies is a shrunken workload. `demo/roman.sno` is unchanged
since 2026-08-18 and `roman.ref` since April (345 conversions); only path moves touched either. Verified, not assumed —
this was the single most likely way a "2.2x win" turns out to be a board reading a smaller denominator, which is exactly the
shape hq_C caught twice today on the corpus board.

## ⚠️ Noted and NOT chased: +2.45% between `cd13321e` and `646b8047`

A real regression of ~551k Ir entered in a 16-commit window on 2026-08-22 and was never chased — it was swamped within hours
by the campaign that followed. It is recorded here rather than cured because it is 5% of a workload that has since improved
2.20x, and chasing it now would cost more than it returns. Flagged for ceo/hq_C: if a future roman arm looks 2–3% odd, this
window is where an unexplained 2.45% already lives.

## ⛔⭐ THE SECOND WATERMARK THAT OUTLIVED ITS WORKLOAD — beauty, and it nearly took the credit with it

Beauty first measured −1.24%, inside the band, and I left it pinned deliberately. **Then the rebase changed the answer.**
Mid-session, `git pull --rebase` brought in seat01's RTX runtime work *and* a corpus in which **Lon had hand-edited
beauty.sno the same day** (`b131a913d` deleted the DECLARED_CONSTANT beauty.sno; `e63689fae` is Lon's 4-line edit) —
630 → 618 lines, **266 lines changed**. On the re-proven tree beauty read **−14.4%**, and the gate duly printed
*"improved; consider re-pinning down"*.

⛔ **That invitation was a trap, and it is the same defect class as roman's, in the more dangerous direction.** Roman's
stale pin under-credited a real campaign; beauty's stale pin would have **over-credited a hand edit as a 14.4% compiler
win**. Both are one bug: *a watermark that has outlived the workload it measured.*

Decomposed rather than re-pinned blindly, by re-measuring the **pin-era beauty.sno** (corpus `8e309aa4`, extracted with
its own `.inc` set) on **today's compiler** — the only apples-to-apples arm available:

| arm | Ir | reading |
|---|---|---|
| pin-era program, pin-era compiler | 2,215,545,392 | the 2026-08-22 pin |
| **pin-era program, TODAY's compiler** | **2,185,743,429** | **−1.35% — the only real compiler delta**, still a FIXED POINT |
| new program, today's compiler | 1,897,159,187 | **−13.2% of the drop is the edited workload** |

So the honest reading of that −14.4% NOTE: **−1.35% earned, −13.2% a different program.** Re-pinned to `1,897,159,187`
as an explicitly labelled **workload rebase, not a win**, with the decomposition in the gate header so no future seat
can read the new basis as a 14.4% gain. ⛔ No cross-workload comparison may be made against the old pin. Beauty remains
the Milestone-1 self-host fixed point under Lon's new source — verified, not assumed.

table_access tracks seat01's same-day re-pin (`12,986,627` vs `12,986,443`) and array_sum holds (+0.08%).

## ⭐ The clean A/B of the two beauty forms (ceo s271 task 1) — ONE tree, ONE sitting

ceo measured classic `1,886,099,406` vs constants `2,177,847,305` but flagged the weakness himself: *"my two runs were
hours apart with script commits between"*. Re-run properly — one pristine `-O0` build at SCRIP `22971235`, **no src change
between arms**, each form fetched from git history, **all three verified self-host fixed points**:

| form | lines | Ir | provenance |
|---|---|---|---|
| DECLARED_CONSTANT | 630 | 2,185,743,429 | corpus `8e309aa4` |
| classic, frozen | 622 | 1,888,454,918 | corpus `1ce15a5ac`, the pre-BEAUTY-CN snapshot |
| classic + Lon's 4-line edit | 618 | **1,897,159,187** | corpus `e63689fae` — what ships, and what is now pinned |

⭐ **The multiple, faster axis, reference = the constants form: classic is `1.16x`.** As percentages **with the basis
named**, because a percent without its basis is the trap: the constants form spends **+15.7% more** instructions than
classic (percent *of classic*); equivalently classic spends **−13.6%** (percent *of the constants total*). ceo's
across-trees reading of 1.15x / ~13% **agrees to 0.2%** — it was sound, and is now tight enough to pin.

⛔ **Lon's 4-line edit is NOT resolvable by this instrument.** +0.46% against a workload whose own run-to-run jitter is
~0.4%. It sits *at* the noise floor, so it must not be quoted as a cost in either direction — reporting it as a number
would be reading three digits off an instrument that only has one here.

## ⛔ A REBASE IS A NEW TREE — and this session is the worked example

My roman pin was measured, committed and **pushed** against `1177e66e`. The rebase onto `22971235` brought two runtime
`.S` files (`rtx_icnsub.S`, `rtx_icnvar.S`). I rebuilt `make pristine` and re-proved rather than assuming those
table-subscript fast paths were irrelevant to roman — they are, but that is now **measured**: `10,224,807`, **+0.003%**,
pin holds. Had I assumed it, the beauty trap above would have shipped unnoticed in the same breath, because it arrived
in the very same rebase.

Also caught and NOT "fixed": the rebased gate had `BEAUTY_DIR=$CORPUS_ROOT/demo`, which looked like a stale-path
regression against my checkout — my *corpus* was simply behind. Re-pulled and verified before touching anything. In a
session where two seats were sweeping corpus paths in opposite directions all day, PULL-BEFORE-TRUST is what kept a
correct line from being "repaired" into a broken one.

## Jitter, measured rather than assumed

roman **0.007%** run to run (709 Ir); beauty **~0.4%** (1,890,181,588 / 1,897,159,187 / 1,898,412,363 across three runs).
Both sit far inside ±2%, so pinning exactly at a measured value carries no false-red risk for either — but the order-of-
magnitude difference between them is worth knowing before anyone reads a 0.5% beauty move as signal.

## Gate proven in BOTH directions after the re-pin

- **positive:** `OK roman: Ir=10224491 within budget 10224491 ±2% [10020001,10428980]`, `GATE OK`, rc=0
- **negative:** `ROMAN_IR_WATERMARK=1000000` → `FAIL roman: Ir=10225200 > budget 1000000 (+2% = 1020000) -- REGRESSION`, rc=1

The negative arm also measures run-to-run jitter on this instrument: **709 Ir, 0.007%** — three orders inside the ±2% band,
so pinning exactly at the measured value carries no false-red risk.

## Blocking set at `make pristine`, RT_OPT=-O0, SCRIP `22971235`, corpus `e63689fae`

- `test_corpus_snobol4.sh` — **m3 PASS=362 FAIL=0 · m4 PASS=362 FAIL=0 SKIP=0**
- `test_gate_emit_no_lang.sh` rc=0 · `test_gate_template_medium_invisible.sh` rc=0 (bb_ ratchet 0)
- `test_gate_instr_budget.sh` rc=0 (all four workloads), proven in both directions

## ⛔⭐ STOP PINNING THE CORPUS TOTAL — IT MOVED THREE TIMES TODAY, ALL WITH FAIL=0

I measured this board twice in one session and got **two different denominators**, and ceo's brief carried a third:

| total | tree | what moved it |
|---|---|---|
| 364 | hq_C, earlier today | before the library quartet went |
| 360 | corpus `7291f5ead` (my first run) | `crosscheck/library` quartet deleted **with its subject** (`library/` became the Snocone import home) |
| **362** | corpus `e63689fae` (my re-prove) | beauty resolution — the DECLARED_CONSTANT beauty.sno deleted, beauty landed in `demo/` |

**FAIL=0 in every one of them.** ⛔ So the pinned-total idiom now does more harm than good: CLAUDE.md pins 364 and warns
against matching 363, ceo's brief says 360, the tree says 362 — and a seat that matches any of those against a board it
just ran will read a *legitimate corpus reorganization* as a regression and go hunting. **The durable invariant is
`FAIL=0` plus `SKIP=0`; the denominator is a fact to be READ from the run, never matched against a remembered number.**
That is the same lesson as this FINDING's two watermarks, one level up: roman's pin outlived its workload, beauty's pin
outlived its workload, and 364 outlived its corpus. **A pinned number is only as good as the basis it was pinned to, and
on this project the basis moves hourly.** hq_C's cure for the board — REFUSE on a missing subtree rather than silently
shrink — is the right shape; this is the reporting-side twin of it.

⛔ Recommend to ceo: strike the specific total from CLAUDE.md's SNOBOL4 line and replace it with `FAIL=0 SKIP=0, read the
printed total`. I have not edited CLAUDE.md myself — it is not mine to rewrite unilaterally.

## What this seat owes the record

The gate now carries the ladder in its own header, so the next seat to see a roman number that disagrees can tell in one
read whether it is drift, a cure, or an unpinned campaign — without re-running any of this.
