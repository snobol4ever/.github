# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: SWIPL study + WAM-CP pivot (PLANNING)

**Goal:** GOAL-PROLOG-BB.md. This session was a Lon-directed PIVOT: study SWI-Prolog's
engine, learn the real WAM model, and lay a non-breaking incremental rung ladder toward
it. **No engine code committed this session — this is planning + a reference study doc.**

## State at handoff
- HEAD `58c7cab9`, tree clean.
- CAT-A-3 B–C work (r12 resume-buffer, the prior session's uncommitted WIP) is preserved
  in **`git stash@{0}`** ("CAT-A-3-BC-wip-resumable-r12-cursor"). NOT abandoned — absorbed
  by rung WAM-CP-5. It still has the pending build fix: `rt_pl_env_current` decl in
  `src/runtime/rt/rt.h` uses `Term**` but rt.h doesn't include the Term type → use
  `void*` in the rt.h decl (rt.c keeps `Term**`; it includes term.h).
- New files this session (untracked, to be committed):
  - `SCRIP/doc/SWIPL-STUDY-2026-05-28-OPUS.md` — the engine study.
  - `.github/SWIPL-STUDY-2026-05-28-OPUS.md` — HQ copy.

## What landed (docs only)
1. **SWIPL study** — seven load-bearing ideas, dependency order, what-we-do-right,
   direct implications for the stashed CAT-A-3 work. Read it before any CP work.
2. **GOAL-PROLOG-BB.md** — new `## ⏳ WAM-CP` CURRENT section with rungs WAM-CP-1..8,
   each gate-preserving and bisectable. LOWER-PIVOT demoted to "COMPLETE, superseded."
   Mandatory-read header now points at the study doc.
3. **PLAN.md** — Prolog BB row rewritten to the WAM-CP pivot + GNU-Prolog-next note.

## The core finding (one paragraph)
Our stashed r12 resume-buffer is a single choice-point record without the parent link.
SWIPL's `struct choice { type; parent; mark; frame; value }` on a parent-linked stack
with one `BFR` register is the genuine model: cut = truncate to barrier (one assignment),
`;`/multi-clause/retry all share it, and it's the prerequisite for Last-Call Optimization
(the principled SEGFAULT-CLUSTER fix). Build it on our existing `Term*` boxes FIRST
(every rung small, nothing breaks); the tagged-word/global-stack migration (SWIPL idea
#1, which also gives free instant backtrack reclamation) is a separate LATER track the CP
model is designed to survive.

## NEXT session (Lon's directive)
1. **Analyze GNU Prolog** — its WAM compiles to native and is register-based, closer to
   what we emit in mode-4 than SWIPL's threaded VM. Compare CP record layout + cut +
   indexing before locking our `pl_choice` struct. Write a sibling study doc.
2. Then **WAM-CP-1** (CP record + `g_pl_bfr` substrate, no callers, byte-identical gates).

## Verify-before-commit (this handoff's commits are docs only)
Docs touch no buildable code. Sanity: `bash scripts/build_scrip.sh` still green,
GATE-1 5/5 (already confirmed this session). Then commit the two study docs + PLAN.md +
GOAL-PROLOG-BB.md per RULES.md handoff sequence (code repos first, .github last).

## Gates at HEAD (unchanged — no engine code touched)
GATE-1 5/5 · GATE-2 132/0 · GATE-3 mode-2 91/107 · GATE-4 4/4 · full mode-4 28/107 ·
FACT RULE 0 · sibling smokes icon 5/5 snocone 5/5 raku 5/5 rebus 4/4 snobol4 13/13.
