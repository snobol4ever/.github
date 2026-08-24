# FINDING — THE SIX-LANGUAGE BASELINE, PINNED (pre-strip acceptance oracle)

**Seat:** `hq_P` (HQ-PERFORMANCE) · **Session:** s268 · **Date:** 2026-08-23
**Brief:** ceo `baseline-and-scoreboard-go` — *"YOUR FIRST DELIVERABLE GATES EVERYTHING"*
**Status:** ⭐ **PINNED.** This is BOTH the strip acceptance oracle AND the README summary table.

---

## What this is, and the one rule for using it

Every number below is **MEASURED THIS SESSION** on a `make pristine` tree, never quoted from a
ledger (LAW 0). It exists so the strip/reorg can be accepted or rejected mechanically: re-run these
same instruments after the strip and diff against this table.

⛔ **The acceptance rule (Lon, verbatim in substance, relayed by ceo):** the 4 main languages are
**not broken beyond what they already were**; Pascal and Raku **keep some level**. That is a
NO-REGRESSION test against this table — it is not a demand that any red here be cured first.

## Pinned tree

| repo | HEAD at measurement |
|---|---|
| `SCRIP` | `6571d23f` (baseline) → `11c89219` (after this session's Phase-1 build strip; **numbers identical across both**) |
| `corpus` | `0c33f6775` |
| `.github` | `9bc7d77a` |

**Shared axes for the whole table:** `RT_OPT = -O0` (s262 FACT RULE — no `-O2` arm exists) ·
`make pristine` before any verdict (HQ-27) · ζ selector = compiled default (`cell-stack`) ·
SNOBOL4 oracle `/home/resources/x64/bin/sbl -bf` · Icon oracle `/home/resources/icon-master/bin`.
⭐ This is a **CORRECTNESS** scoreboard — pass counts, not multiples. No perf number appears here,
so the `x`-multiple FACT RULE has nothing to format; the speed column is a separate deliverable.

---

## THE TABLE

| # | Language | Instrument | m3 (`--run`) | m4 (`--compile`) | Reds, and whose |
|---|---|---|---|---|---|
| 1 | **SNOBOL4** | `test_corpus_snobol4.sh` | **363 / 364** | **363 / 364** (0 SKIP) | `demo_treebank` only — **deliberate**, row `vlist-expr-alternation` |
| 2 | **Icon** | `scorecard_icon.sh` | **META 69.0** / Σw=95 — full block below | | `bench_correct` 0/8 is the whole gap |
| 3 | **Prolog** | `test_smoke_prolog.sh` | **3 / 5** | **3 / 5** | `clause`, `recursion` — pre-existing, matches ledger |
| 4 | **Snocone** | `test_smoke_snocone.sh` | **4 / 5** | — | `procedure` (empty output) — pre-existing, matches ledger |
| | | `test_crosscheck_snocone.sh` | **6 / 8** | — | 2 Fibonacci rows |
| 5 | **Pascal** | `test_gate_pascal_m3/m4.sh` | **98 / 153** | **86 / 153** | +23 NOREF (no oracle output pinned), 0 XFAIL |
| 6 | **Raku** | `test_smoke_raku.sh` | **705 / 724** | **705 / 724** | 19 FAIL, same set both modes |
| | | `test_crosscheck_raku.sh` | **51 / 51** | — | clean |
| | | `raku_roast_scoreboard.sh` | **3 / 986 in-tier (0.3%)** | — | 929 PARSE-FAIL — the parser is the wall |
| — | *(Rebus)* | `test_smoke_rebus.sh` | **4 / 4** | — | clean (7th frontend, not in the six) |

### Icon block — `scorecard_icon.sh`, weighted META

Oracle `/home/resources/icon-master/bin` (reached via `ORACLE_BIN`, which resolves correctly here —
`S4A` → `/home/resources`, since this root correctly owns no `x64`).

| Suite | Score | weight | % |
|---|---|---|---|
| `rungs_m3` | 232 / 293 | 25 | 79.2 |
| `rungs_m3_cells` | 232 / 293 | 10 | 79.2 |
| `rungs_m4` | 218 / 293 | 20 | 74.4 |
| `bench_correct` | **0 / 8** | 15 | **0.0** |
| `smoke` | 28 / 28 | 10 | 100.0 |
| `crosscheck` | 4 / 4 | 5 | 100.0 |
| `gates` | 8 / 10 | 10 | 80.0 |
| **META** | | **Σw=95** | **69.0** |

⭐ **`bench_correct` 0/8 is HONEST — I checked, because a weight-15 zero is exactly the shape that
turned out false elsewhere in this same session.** Re-run standalone against the oracle it is
**6 DIVERGE + 2 RUNAWAY**, every one a real defect, not an instrument artifact:

| program | oracle lines | SCRIP lines | verdict |
|---|---|---|---|
| `concord` | 1345 | **0** | DIVERGE |
| `geddump` | 12568 | **0** | DIVERGE |
| `ipxref` | 1230 | **0** | DIVERGE |
| `micsum` | 2 | **0** | DIVERGE |
| `tgrlink` | 3239 | 2 | DIVERGE |
| `rsg` | 5000 | 4893 | DIVERGE (tail truncated at 4893) |
| `deal` | 17000 | 6 | RUNAWAY — hit the 64MB cap |
| `queens` | 16653 | 1525198 | RUNAWAY — hit the 64MB cap |

Note the **shape**: four programs emit **nothing at all** while the oracle emits thousands of lines,
and two emit unbounded output. That is not a scattering of wrong answers — it reads as whole-program
failure (early exit / generator never driving) plus an unterminated generator, i.e. probably **two
root causes, not eight**. ⛔ Recovering this suite is worth **15 of the 95 weight — the single largest
Icon lever on the board**, and Icon META cannot pass ~82 while it sits at zero.

⛔ **Do not read `smoke 28/28` beside `bench_correct 0/8` as a contradiction.** The smoke programs are
self-graded against pinned `.ref` files; the bench programs are graded IDENTICAL against a live
oracle on real inputs. They measure different things, and the gap between them is the finding.

### Blocking gates — all green

| Gate | Verdict |
|---|---|
| `test_gate_emit_no_lang.sh` | ✅ PASS — LANG-BLIND, no language identifier in `src/emitter` or `src/templates` |
| `test_gate_template_medium_invisible.sh` | ✅ PASS — **0** BOTH-MEDIUM sites in `bb_*.cpp` (ratchet ceiling 0, target 0) |

### Non-blocking gate red, recorded so the strip is not blamed for it

`test_gate_raku_zframe.sh` (RK-ZC-8) **FAILs at baseline**: its INVARIANT B demands the Raku smoke
suite be `719/0` in both modes; the suite actually stands at `705/19`. The gate's class-b witness
reproduces as designed (`rc=139`). ⛔ This red **predates the strip** — do not read it as strip damage.

---

## ⛔ THE LEDGER IN CLAUDE.md IS STALE — SNOBOL4 IS 363/364, NOT 339/341

The expected-totals line in every root's `CLAUDE.md` reads *"m3 339/341, m4 338/341 + 1 SKIP"*, with
`160_pat_alt_inner_gen_resume` as a standing front red and `132_pat_fence_eps_recur_shallow` as a
compile/link SKIP. **All three of those statements are now false**: the corpus is 364 programs, both
modes score 363, the two named reds are CURED and the SKIP is gone. Only `demo_treebank` remains, and
it is deliberate. ceo has corrected the ceo root's copy; the other roots' copies still mislead, and a
seat matching against them will "confirm" a regression that is really a cure. Digest propagation to
the remaining roots is queued behind this deliverable.

---

## ⛔⭐ A FALSE ALL-FAIL I GENERATED, CAUGHT, AND KILLED — READ THIS BEFORE TRUSTING ANY BOARD

The first Icon scorecard run of this session produced `smoke: 0 28` and `bench_correct: 0 8`. Both
were **entirely false**, and the cause was mine: I had started `make pristine` **while the scorecard
was still running**. `pristine` removes `./scrip` and `out/libscrip_rt.so` (deliberately, since s258),
so every Icon program the board launched mid-window ran against a **missing binary** and scored zero.

The tell that saved it: `smoke: 0 28` is not a plausible shape next to `crosscheck: 4 4` and
`gates: 7 10` from the same run. Running `test_smoke_icon.sh` by hand returned **14/14 in both modes
in 1 second**. The whole first run was discarded and re-run on a quiescent tree.

⭐ **The two runs side by side — this is the receipt, and it shows the corruption was NOT uniform:**

| suite | run 1 (overlapped a rebuild) | run 2 (quiescent) | |
|---|---|---|---|
| `rungs_m3` | 232 / 293 | 232 / 293 | identical — finished **before** the rebuild started |
| `rungs_m3_cells` | 232 / 293 | 232 / 293 | identical — same reason |
| `rungs_m4` | **196 / 293** | **218 / 293** | ⛔ **22 programs silently lost** |
| `gates` | **7 / 10** | **8 / 10** | ⛔ one gate silently lost |
| `smoke` | **0 / 28** | **28 / 28** | ⛔ total wipeout |
| `bench_correct` | 0 / 8 | 0 / 8 | genuinely 0 in both — see the Icon block |
| `crosscheck` | 4 / 4 | 4 / 4 | identical |

⛔ **The dangerous row is `rungs_m4`, not `smoke`.** A `0/28` screams. **196/293 does not** — it is an
entirely plausible Icon score, it sits right next to the honest 218, and had the run not also
produced an absurd `0/28` beside it I would have pinned it and never known. A partially-corrupted
board is more dangerous than a fully-corrupted one, because only the fully-corrupted one announces
itself. ⭐ That is the real lesson here, and it generalises past Icon: **when one suite in a run is
provably false, the whole run is void — never salvage the plausible-looking rows from it.**

⭐ **The rule this earns:** *a rebuild is not a background activity.* `make pristine` is destructive to
every concurrently-running harness in the same tree, and the harness cannot tell a deleted compiler
from a failing one. Never overlap a build with a board; never publish a board that overlapped one.
This is the "non-empty is not alive" class wearing a new hat — the table was full, plausible, and wrong.

⭐ Two instrument defects were also confirmed while chasing it, and are **NOT** the cause:
- `ORACLE_BIN` defaults to `$S4A/icon-build/bin`; `S4A` resolves to `/home/resources` here (this root
  correctly owns no `x64`), so the Icon oracle **does** reach PATH. Exonerated.
- `scorecard_icon.sh`'s `bench_correct` suite was cured of "zero-examined is indistinguishable from
  all-fail" (it now reports `UNPROVEN`). ⛔ Its `smoke`, `crosscheck` and `gates` siblings were **not**
  — each still collapses a timeout to `0 0` through `awk`'s always-printing `END` block, scoring a
  timeout as total failure at weight 10/5/10. Cure filed below.

---

## Environment notes for whoever re-runs this

- ⭐ **`refs/` was empty and two boards silently depended on it.** `raku_roast_scoreboard.sh` refused
  outright (good — it names the missing path instead of scoring 0). Repopulated this session:
  `refs/rakudo-main` → `/home/resources/rakudo-main`, `refs/roast` → the unpacked
  `/home/resources/roast-master.zip`. `refs/` is gitignored, so this is per-session work, not a commit.
- **Icon oracle** is `/home/resources/icon-master/bin/{icont,iconx}`; `/home/resources/icon-build` is a
  SYMLINK to it, not a second tree (hq_C, s266). Reach both only through `lib_oracle_flags.sh`.
- `icont`/`iconx`/`swipl`/`gprolog`/`bison`/`flex` are **not on PATH** in this root. Icon is fine via the
  accessors above. ⛔ bison/flex absent is why snocone regeneration waits for Phase 2.
- **Disk:** seat03 escalated `/` at 100% (163M free). Re-measured this session: `/` is **75%, 31G free**;
  the alarm has cleared. `/home/satirical` is 113G but sits on `/home` (503G, 29%) — it was never what
  filled `/`, and it is the host user's tree: do not triage it, do not scan it.

---

## The paired LOC before-picture (ceo `loc-checkpoint-pinned`)

Pinned separately at `survey-src-2026-08-23/14-loc-checkpoint.md`, measured at SCRIP `f110760f`:

| category | LOC |
|---|---|
| **hand-written `src` (minus backends)** | **74,437** ⭐ *the shrink denominator Lon wants* |
| generated | 29,106 |
| grammars | 5,309 |
| backends | 25,899 |
| total | 134,751 |

⛔ **Three constraints on the after-picture, all easy to lose six sessions from now:**
1. Re-measure with the **same four-category instrument** — not a fresh line count.
2. The backends move reports as a **MOVE, not a strip**. 25,899 lines leaving `src/backends/` is not
   shrink and must never be quoted as such.
3. ⛔ **The LOC pin and this scoreboard are NOT the same tree** — `f110760f` vs `6571d23f`/`11c89219`.
   The delta is small (my Phase-1 strip removed no source lines — only Makefile flags and two dead
   `.PHONY` targets) but it is **not zero**, and a tree is part of a number's label. The after-picture
   should re-measure BOTH halves on the post-strip tree so they share one instrument *and* one tree.

## Build-side strip, Phase 1 — LANDED this session (`SCRIP 11c89219`)

Delivered against ceo's *"make-test wiring + test-ir/test-all deletion + the two dead -D deletes are
yours and ride Phase 1"*:

1. ⛔ **`-DDYN_ENGINE_LINKED` and `-DIR_DEFINE_NAMES` deleted.** Both were passed on every compiler and
   runtime compile line (`CXXRT`, `CRT`, and all three `RT_OBJDIR` pattern rules) and read by **no source
   file in the tree** — the only mentions left are a `docs/` sample and a comment in `test/`. Pristine
   rebuild green; **SNOBOL4 corpus 363/364 in both modes before AND after**, so the strip is
   behaviour-neutral by measurement, not by argument.
2. ⛔ **The `make test` false-green trap is cured.** `test`, `test-ir` and `test-all` were named in
   `.PHONY` with **no recipe anywhere**, so each exited 0 having run nothing while reading as a full
   green suite. `test` now runs the real blocking set (SNOBOL4 corpus + the two live gates) and fails on
   the first red. `test-ir` and `test-all` are **deleted, not wired** — nothing was ever behind them —
   and both now stop with `No rule to make target`, verified.
3. **`RT_OPT`'s comment corrected.** It still advertised the superseded `O0-DEV-O2-BENCH` rule and told
   the reader how to pass `RT_OPT="-O2 …"`. That contradicts Lon's s262 **NO `-O2` BUILDS, EVER** FACT
   RULE. The default was already `-O0`; only the comment changed, so no rebuild semantics moved.

---

## Cures filed, not yet shipped (next rungs, this seat)

- **`scorecard_icon.sh` smoke/crosscheck/gates zero-collapse** — port `bench_correct`'s `UNPROVEN`
  treatment to its three siblings so a timeout can never again be scored as 0%. ⭐ Worth more than it
  looks: `bench_correct` was already cured of exactly this and the cure is a known-good pattern to copy.
- **Icon `bench_correct` 0/8** — the largest single Icon lever (weight 15). The four zero-output
  programs should be triaged as ONE class before anyone opens eight rows.
- **`--zeta-port` needs a per-VALUE ruling under the switch rule**, not a per-flag one: four of its
  seven values still route to `rt_zeta_port_set_mode` while three are aliases into the decided-winner
  four-config selector. A flag-level sweep would take the live selector with the residue.
- **Digest propagation** of the corrected SNOBOL4 expected-totals line to the remaining roots' `CLAUDE.md`.
- **`ZCFLAGS` / `RT_TAG` design at one ζ config** — the remaining build-side strip question.

## Routing

Per CEO brief: replied to `ceo` on `baseline-and-scoreboard-go`, and sent `hq_C` the pointer to this
file — **hq_C holds the strip until this lands**, so the pointer is the release.
