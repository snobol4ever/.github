# CARVEOUT-A-LADDER.md — per-language ladder for CARVE-OUT A (front-end parsers → Snocone `parser_*.sc`)

**Row:** `carveout-a-decompose` (rank 1). **Produced by:** seat13, 2026-08-24. **This row's own DONE-WHEN asked for:** "a PER-LANGUAGE ladder, one rung per language, each rung independently dispatchable and sized to ONE session, each with its own DONE-WHEN... State which language should go FIRST and why... Deliver the ladder as a file plus one ready-to-fire brief for rung 1." This file is that deliverable. Rung 1's brief is in full task-baton shape near the bottom — ready to paste into a new `postoffice/tasks/*.task.md` when HQ mints it.

**THIS ROW PRODUCES THE LADDER, NOT THE PORT** — nothing below is a code change. Everything here is read/measured, nothing written except this file and the PLAN.md correction it calls for.

---

## 0. The headline correction: this is not greenfield, and the per-language state is wildly uneven

The brief's own framing ("HQ expects the smallest C parser with a drafted `.sc`, but that is a hypothesis you may falsify") undersells how far along this already is. **Every one of the six languages except Pascal already has its Phase-2 shift/reduce grammar rewrite (`parser_<lang>.sc`) DONE** — this was completed on **2026-05-19**, three months ago, and mostly never resurfaced since (three of the six per-language tracking files were deleted 2026-08-15/16 and folded into the consolidated `GOAL-<LANG>-100.md` files without carrying the carve-out status forward). What's actually blocking each language differs completely — engine bugs, unverified smoke status, a self-flagged architecture defect, or (Pascal) not started at all. The ladder below is sequenced accordingly, not by raw file size.

## 1. Line-count figures — both existing citations are now wrong, corrected here

**PLAN.md line 18** currently says *"`corpus/SCRIP/parser_{snobol4,icon,prolog,snocone,rebus,raku}.sc`, 1,933 lines... against 41,589 lines... A 21:1 compression."* **Two problems**: the path is stale (`corpus/SCRIP/` was moved to `SCRIP/bootstrap/` in commit `e727c6eb6`, Lon s267 ruling: "SCRIP repo carries compiler source, corpus carries programs — these 56 .sc files ARE the compiler"), and 41,589 undercounts the current C tree by ~6%.

**This row's own BRIEF also cited a number** (44,083 across 79 files, with a per-language breakdown) that **is internally inconsistent — its own seven per-language figures sum to 53,707, not 44,083.** Not trustworthy as handed down; re-measured from scratch below.

**Freshly measured 2026-08-24** (SCRIP `ab9c087c`, corpus `fea43840`): `SCRIP/bootstrap/parser_*.sc` = **1,933 lines across 6 files, confirmed exactly** (253+374+337+276+267+426). The C side depends entirely on methodology — pick the one that matches what you're arguing:

| Methodology | C lines (6 langs, excl. Pascal) | Ratio vs 1,933 .sc lines |
|---|---|---|
| Raw literal file totals (`find \| wc -l`, as-is) | 47,171 | 24.4:1 |
| Excluding 2 dead files found in `src/parser/prolog/` (`prolog_emit_jvm.c.bak` 9,073 + `prolog_lex.c.bak` 424 — confirmed unreferenced anywhere, not part of the live parser) | 37,674 | 19.5:1 |
| **Hand-written only** (excludes bison/flex-*generated* C and the `.y`/`.l` grammar sources themselves — per `.github/survey-src-2026-08-23/14-loc-checkpoint.md`) | **9,646** | **5.0:1** |

⭐ **The hand-written-only row is the honest comparison if the point being made is "how much hand-authorship does this save."** Icon and Prolog are ~100% hand-written C (no generated parser); raku/rebus/snobol4/snocone/pascal are mostly bison/flex output — comparing 1,933 hand-written `.sc` lines against machine-generated `.c` output overstates the win by ~5x. **Recommend PLAN.md cite the hand-written figure (9,646, 5.0:1) as the honest headline**, with the raw 47,171/24.4:1 figure available as a footnote for "total surface area being replaced." Pascal (6,417 C lines, no `.sc` at all) is excluded from every ratio above since there's nothing on the other side to compare — see §7.

**PLAN.md line 18 correction applied by this row** (see diff below): path fixed to `SCRIP/bootstrap/`, headline changed to the hand-written figure with the raw figure as a parenthetical, ratio corrected.

## 2. Sequencing signal found, and its actual provenance (read this before trusting the order below)

PLAN.md line 4 (Lon 2026-08-22 s257, **two days before this row**, in the middle of a sentence about *performance targets*, not the carve-out): *"...order: SNOBOL4 (Snocone) → Icon → Prolog → Pascal & Raku."* **This is not a carve-out-specific ruling** — it's phrased as a performance-focus priority. But three independent signals converge on the same order, which is why this ladder adopts it rather than re-deriving from scratch:
1. This s257 targets-order.
2. CLAUDE.md's own "Session start" protocol names the three consolidated goal files in the same order: `GOAL-SNOBOL4-100.md`, `GOAL-ICON-100.md`, `GOAL-PROLOG-100.md`.
3. It matches SNOBOL4's status as the language with the deepest carve-out validation already done (§3) — a live-first candidate independent of Lon's ruling.

**Falsifying the brief's own hypothesis** ("smallest C parser with drafted `.sc` goes first"): by raw or hand-written C size, Icon is smaller/cleaner than SNOBOL4 on several axes (§3 — cleanest close, smoke 5/0, 0 audit violations) and would win a pure "smallest + most done" contest. **Overridden in favor of Lon's named order** — not a technical judgment call to leave for whoever picks up rung 1. Rebus and Snocone are **not named in the s257 list at all** and are placed by technical readiness instead (§5, §6) — both are close enough to done that either is a legitimate opportunistic pick independent of the main sequence.

## 3. Current per-language status (measured 2026-08-24, see full research digest in this row's LEDGER for sourcing)

| Language | Phase-2 grammar rewrite | Smoke-verified vs C oracle? | Deepest validation track | Concrete open blocker |
|---|---|---|---|---|
| **SNOBOL4** | ✅ done (2026-05-19) | **Unknown — not stated anywhere, no dedicated gate exists** | SCT transpile-via-SPITBOL: **PASS=88/88** | SCT-1f (needs `SN-26-spl-bridge` in `x64`, an HQ-only asset) / SCT-BEAUTY-SC-PARSE (fix written, awaiting Lon's choice of two options) |
| **Icon** | ✅ done — cleanest close, 0 audit violations | ✅ **PASS 5/0** | SCT track stalled (needs `icon_helpers.sc` eliminated) | SCT-4 never attempted |
| **Prolog** | ✅ done (PL-SC-1..7) | ❌ deferred (env segfault, 2026-05-19) | SCT track least progressed: undiagnosed SPITBOL ERROR 246 (stack overflow) @ line 2065 | PL-SC-8 smoke + SCT-6 diagnosis, both unstarted since |
| **Snocone** | ✅ grammar done, `PASS=67 FAIL=0` on its own SC-N ladder | ❌ blocked by a **concretely diagnosed, ready-to-implement** engine bug | SCT track blocked upstream (SCT-9-arbno-fence: `nPush`/`nPop` side effects not backtrack-safe under `ARBNO`) | `bb_build_patnd()` needed in the emitter for `PATND_t*`/`SM_PAT_REFNAME`/`bb_deferred_var` — exact fix already specified in `GOAL-PST-SNOCONE.md`, just not landed |
| **Rebus** | ✅ done, "already clean at Phase 2 start" | ✅ via its own RB-FW ladder, **PASS=96/96**, then pivoted to real-program parsing | minimal SCT coverage (not the validation path used) | `BUG-RB-FULL1-D`: multi-line `if`/`while` bodies parse the keyword as a bare identifier — repro written, fix not landed |
| **Raku** | ✅ per `PRF-14`, **but self-flagged broken**: 23 leaf-pusher functions misuse `shift()` (value-typed arg where a subject-consuming pattern is required); fix designed on the primitive, **never applied to `parser_raku.sc`** | ❌ blocked (env segfault) | Separate `RK-28..50` grammar-coverage pivot in progress (RK-28/28-A/29 done, RK-30 next) — **does not cross-reference the leaf-pusher defect**, so it's unknown whether that pivot's work sits on top of known-broken leaf-pushers | Two open, possibly-unrelated tracks that need reconciling before Raku's rung can even be sized honestly |
| **Pascal** | ❌ no `.sc` file exists, no goal file exists | N/A | N/A | Not started under this carve-out at all |

## 4. The ladder

Ordered per §2's rationale. Each rung is independently dispatchable — a seat can pick up any FREE rung without waiting on an earlier one, since none of the remaining blockers are cross-language.

### Rung 1 — SNOBOL4 (full brief below, §8)
Build the missing direct gate (nothing currently compares `parser_snobol4.sc` against the C oracle directly — the SCT track validates via transpile-then-SPITBOL, a different and weaker guarantee than AST comparison), then measure real cutover readiness against the actual corpus. **Not** attempting SCT-1f (needs an HQ-only `x64` asset) or ruling on SCT-BEAUTY-SC-PARSE's pending Lon decision — both routed to HQ, not blocking rung 1's own deliverable.

### Rung 2 — Icon
Mirror of rung 1's missing-gate problem, but starting from a stronger position (already smoke-verified 5/0, 0 audit violations). One session: build the same direct-comparison gate shape as rung 1 lands, run it against Icon's real corpus, land SCT-4 (`icon_helpers.sc` elimination) if time remains — that's the one genuinely unstarted piece.

### Rung 3 — Prolog
Weakest validation of the three named-first languages. One session: diagnose the SCT-6 SPITBOL ERROR 246 stack overflow (line 2065 — likely a `nPush`/`nPop` or recursive-pattern depth issue, same genus as Snocone's SCT-9-arbno-fence; worth checking if it's the *same* root cause before treating as a separate bug), then attempt PL-SC-8 smoke in a container where the prior env segfault doesn't reproduce (check whether that segfault is still live post-re-grid/post-bootstrap-move before assuming it still blocks).

### Rung 4 — Pascal (starts from zero, sized as a first-fixtures rung, not full parity)
No `.sc` counterpart exists. One session is NOT enough for full parity (Pascal's C parser is 6,417 lines, the largest of the six) — size rung 4 as "PST-PASCAL-0/1": stand up `parser_pascal.sc` against the smallest real Pascal fixtures only (`corpus/tests/pascal/` — confirmed to exist, ~90 `.pas`/`.ref` pairs post-re-grid), following the exact style precedent in `GOAL-REBUS-100.md §Style Guidelines for parser_*.sc, items 1-12` (canonical Style Guidelines, cross-referenced by every other parser; retired name `GOAL-PARSER-REBUS.md §1-12`). DONE-WHEN: first N fixtures passing (pick N after seeing what's in the corpus directory — don't guess a number now), not "Pascal done."

### Rung 5 — Raku
**Do not size this rung until the leaf-pusher-vs-RK-28..50 reconciliation is done first** — that reconciliation is itself the right-sized rung 5 STEP 1: read both `GOAL-PST-RAKU.md` (leaf-pusher defect) and the tail of `GOAL-PARSER-RAKU.md` (RK-29's actual diff, most recent commits) to determine whether RK-28/29 already touched the 23 broken leaf-pushers or left them broken. Only after that answer exists can a real DONE-WHEN for "fix Raku's carve-out" be written — attempting a fix before the reconciliation risks fixing the wrong layer.

### Opportunistic rungs — independent of the §2 sequence, pick up any time

- **Snocone**: the single most concretely-diagnosed, ready-to-implement item in this entire ladder. `GOAL-PST-SNOCONE.md` already specifies the exact fix (`bb_build_patnd()`, XKIND_t cases enumerated) for the engine bug blocking its smoke test. This is emitter work, not parser-authoring — likely genuinely small. Recommend whoever has spare capacity takes this first regardless of the main sequence; it's the highest-confidence, lowest-risk win on the board.
- **Rebus**: `BUG-RB-FULL1-D` (multi-line `if`/`while` body parsing) is a single, well-scoped parse bug with a written repro. Similarly small, similarly opportunistic.

## 5. What "sized to ONE session" excludes from every rung above

None of the five main rungs include: deleting the C parser, flipping SCRIP's default frontend, or any change to `src/driver/`. Every rung above is "measure real readiness and close the nearest concrete gap" — the actual cutover (C parser retired, `.sc` becomes the shipped frontend) is a later, separate rung per language, gated on that language's own rung above landing clean. Do not let a future session conflate "rung done" with "cutover done."

## 6. New-global-variable note

None of the work sized above should need a new C global (per CLAUDE.md's standing ⛔ ban) — every open blocker identified is either a missing gate/script, a diagnosis task, or (Snocone) an emitter fix already scoped around existing state (`PATND_t*` dispatch, not new storage). If a rung's implementer finds they need one, that's a fresh ⛔ banner ask to Lon that session, per standing doctrine — not pre-cleared by this ladder.

## 7. Pascal gap, named plainly (per the brief's explicit ask not to hide it)

Pascal has a C parser (6,417 lines, `src/parser/pascal/`) and a real fixture corpus (`corpus/tests/pascal/`, confirmed to exist post-re-grid) but **zero Snocone-side work has ever started** — no `.sc` file, no `GOAL-PARSER-PASCAL.md`, no `GOAL-PST-PASCAL.md`. It is the least-supported language in SCRIP generally (CLAUDE.md itself lists Pascal as "in progress" alongside Raku in the frontend list). Rung 4 above treats it as a from-zero start, not a gap-fill.

---

## 8. Rung 1, ready to fire — SNOBOL4 carve-out gate + cutover readiness measurement

*(Everything below this line is written in task-baton shape, ready to paste into a new `postoffice/tasks/carveout-a-snobol4.task.md` when HQ mints the row. Not minted by this row — LAW 2/3 reserves minting to HQ.)*

```
# TASK carveout-a-snobol4 · owner: unassigned · state: FREE
GOAL: CARVE-OUT A, rung 1 of 5 (see .github/CARVEOUT-A-LADDER.md). SNOBOL4's parser_snobol4.sc
(SCRIP/bootstrap/parser_snobol4.sc, 253 lines, Phase-2 shift/reduce rewrite DONE 2026-05-19) has
NEVER been directly gated against the C frontend, and its real-corpus cutover readiness is
UNMEASURED. The SCT track (PASS=88/88) validates via transpile-then-SPITBOL, a different and
weaker guarantee than direct AST comparison against the C --dump-ast oracle -- do not treat
SCT's 88/88 as equivalent to a smoke gate.
DONE-WHEN: a new gate script exists (name it test_gate_parser_snobol4_sc.sh or similar, matching
the shape of test_parser_snocone.sh) that runs parser_snobol4.sc via `scrip --run` with the
SCRIP/bootstrap library preamble, compares its output tree against `scrip --dump-ast` on the SAME
input, across a real sweep of corpus/crosscheck/rung*/[snobol4 rungs] (self-contained fixtures
only, per the primer's own constraint) PLUS a sample of corpus/tests/snobol4/ or wherever the
re-grid landed real SNOBOL4 programs (verify the live path -- do not trust any path cited in an
older doc without checking) -- and the gate exits non-zero on any mismatch. Report the resulting
PASS/FAIL count honestly, including if it's not 100% -- this rung's job is to MEASURE readiness,
not to fake a clean number.

## NEXT
STEP 1: `git pull --rebase` both SCRIP and corpus first -- the corpus re-grid landed 2026-08-24,
same day this rung was drafted; paths WILL have moved again by the time this is picked up. Locate
the current SNOBOL4 fixture/crosscheck corpus via `find`, not by trusting any hardcoded path here
or in any older GOAL file.
STEP 2: Read SNOBOL4-SNOCONE-PRIMER.md in full first (mandatory per CLAUDE.md's Session Start
protocol for any PARSER-* work) -- especially the `.` vs `$` execution model section, the #1
source of bugs per that file's own framing.
STEP 3: Build the direct-comparison gate per DONE-WHEN above. Use test_parser_snocone.sh as the
structural template (same repo, same shape of problem) but point it at parser_snobol4.sc and a
SNOBOL4 fixture set instead.
STEP 4: Run it. Report the real number. If less than 100%, characterize the failures by shape
(parse error vs tree mismatch vs crash) -- do not just report a percentage.
STEP 5: Do NOT attempt SCT-1f (blocked on an HQ-only x64 asset, `SN-26-spl-bridge`) or rule on
SCT-BEAUTY-SC-PARSE's two pending fix options (explicitly awaiting Lon's decision per
GOAL-PARSER-SC-TRANSPILE.md) -- both are out of this rung's scope, route status to HQ if either
turns out to block the DONE-WHEN gate itself.
STEP 6: Do NOT attempt the actual cutover (making parser_snobol4.sc the live/default frontend) --
that is explicitly a later, separate rung, gated on this one landing clean first.

## QA

## LEDGER
- [seat13·2026-08-24] Rung drafted as part of carveout-a-decompose's ladder deliverable. Not
  claimed/started -- this is the brief, not the work. See .github/CARVEOUT-A-LADDER.md for full
  per-language context and why SNOBOL4 goes first.

## BRIEF (verbatim, as it stood in the ladder)
Rung 1 of 5 in the CARVE-OUT A ladder. See .github/CARVEOUT-A-LADDER.md §8 for full context.
```
