# GOAL-PARSER-PURE-SYNTAX-TREE.md — Six Frontends, One Pure tree_t

**Repo:** SCRIP + corpus + .github
**Status:** ✅ Phase 1 C COMPLETE all six languages (AUDIT-2 2026-05-19).
Phase 2 SCRIP mirror sessions ready to launch.

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                          ├──► interp / emitters
                                                            └─►  IR_bb_t  ──┘
```

Parsers may only: discard pure layout tokens; choose a node kind for an
operator. Everything else — rewrites, introduced nodes, labels, gotos,
augop expansion, control-flow lowering, slot allocation — belongs in
`lower`.

---

## ⛔ Three Phase-1 facets (binding)

**F1** — `tree_t` is the sole information channel between parse and
lower. No parser-side globals, off-tree linked lists, or synthesized
facts.

**F2** — `tree_t` is exactly `{t, v, n, c}`. No `_nalloc`, no `_id`.
Verified per AUDIT-2 §2i.

**F3** — All children of every node in left-to-right source-token
order. No mutate-in-place, no kind-inspection before wrap, no
reorderings. Always wrap fresh.

The three facets together make `corpus/SCRIP/parser_*.sc` reducible to
**Shift** (push next token's leaf onto working stack) and
**Reduce(kind, n)** (pop n items, wrap as children of new node of
kind, push). That is the Phase 2 endpoint.

---

## ⛔ Two-phase sequencing (binding 2026-05-18)

**Phase 1 — C parsers only. Phase 2 — SCRIP mirrors only. Never both in
the same session.**

Phase 1 complete for all six languages as of 2026-05-19. Phase 2 is the
current phase. Each Phase 2 session works one `parser_*.sc` file.

---

## Phase 2 — permitted primitives (binding)

Inside every grammar rule and `Compiland`:

| primitive   | purpose                                                              |
|-------------|----------------------------------------------------------------------|
| `shift(p, kind)` | match pattern `p`, push leaf of `kind` with matched text |
| `shift(p, '')`   | match-and-ignore: push empty leaf for missing slot |
| `reduce(kind, n)`| pop `n` items, wrap into new node, push back |
| `reduce(kind, 'nTop()')` | variable arity |
| `reduce(kind, '*(GT(nTop(),1) nTop())')` | n-ary or pass-through-single |
| `nPush()` / `nPop()` | open / close counter frame for variable-arity reduces |
| `nInc()` | bump current counter — one per L→R sibling |
| `nTop()` | read current counter |
| `assign(.var, val)` (or `*assign`) | set parser-scratch variable mid-match |

Pure string preprocessors with **no tree ops** (no `Push`/`Pop`/`Tree`/
`tree`/`Append`/`reduce`) are also permitted as `function` definitions:
`dq_unescape`, `unescape_q`, `sn_match`, `sn_upr`, `notmatch`.

**Forbidden:** `shift_value`, `foldop`, `reduce_call`, `reduce_prim`,
`reduce_opsyn`, `Push`, `Pop`, `Tree`, `tree`, `Append`, `IncCounter`,
`TopCounter`, `Body` wrapper, and every `function X() { ... }` that
calls any of those.

**The driver tail's `Pop()` (post-`if (Src ? Compiland)`) is permitted**
— it retrieves the root for `TDump`. Not a grammar action.

---

## Phase 2 sessions — one file each

| # | rung | file | size | est. |
|---|------|------|-----:|-----:|
| 1 | `PST-RB-SC`  | `parser_rebus.sc`   | 266 | 10 min |
| 2 | `PST-ICN-SC` | `parser_icon.sc`    | 373 | 30–60 min |
| 3 | `PRF-13`     | `parser_raku.sc`    | 680 | 2–3 h |
| 4 | `PST-SN4-SC` | `parser_snobol4.sc` | 263 | 1.5 h |
| 5 | `PST-PL-SC`  | `parser_prolog.sc`  | 1051 | 4–6 h |
| 6 | `PST-SC-SC`  | `parser_snocone.sc` | 934 | 4–6 h |

Each session reads:
1. `PLAN.md`, `RULES.md`
2. SPITBOL manual chapters 6, 7, 9, 15
3. `SNOBOL4-SNOCONE-PRIMER.md`
4. **Its per-language goal file** (`GOAL-PST-<LANG>.md`) — entry point;
   has the audit steps embedded as a numbered ladder.
5. Reference: `PST-SCRIP-AUDIT.md` (full per-file breakdown — already
   inlined into each goal file's step list).

**Handoff rule (mirrors RULES.md):** a per-language PST session updates its
own `GOAL-PST-<LANG>.md` only. Do NOT edit this parent file's tables on routine
handoff — they are a static index; live state lives in the per-language goal
file. Touch this file only on a `grand master reorg`.

---

## ⛔ Strict rule for every Phase 2 session

**Do not let the program failing to run stop the rewrite.** Delete every
forbidden function and rewrite every grammar rule per the per-language
goal file's steps, even if the resulting `.sc` does not pass smoke on
first run. Mechanical deletion and rewrite first; tree-shape
conformance debug after, in a separate later session. Record
`⚠ MIRROR-GAP-<rung-step>` in the State block when committing a
not-yet-running rewrite.

---

## ⛔ Beauty self-host (Milestone 1 — sacred)

`beauty.sno` self-host md5 `abfd19a7a834484a96e824851caee159` must
remain green throughout Phase 2. SCRIP-side changes do not threaten it
directly (beauty.sno goes through the C frontend); but if a Phase 2
session is tempted to alter `lower.c` or any C code to make a SCRIP
test pass, **stop and refile the work as a separate post-Phase-2
session**.

---

## Phase 1 closed — frontend status

**Live Phase-2 status lives in each per-language goal file — that is the single source of truth.**
Do not track ⏳/✅ progress here; this table is a static index only.

| Frontend | Phase 1 C | Per-language goal (live state) |
|----------|-----------|-------------------|
| SNOBOL4 | ✅ | `GOAL-PST-SNOBOL4.md` |
| Icon    | ✅ | `GOAL-PST-ICON.md` |
| Raku    | ✅ | `GOAL-PST-RAKU.md` |
| Snocone | ✅ | `GOAL-PST-SNOCONE.md` |
| Rebus   | ✅ | `GOAL-PST-REBUS.md` |
| Prolog  | ✅ | `GOAL-PST-PROLOG.md` |

**Recommended Phase 2 ordering** (smallest first, biggest last; lets
later sessions benefit from the idioms established in earlier ones):

1. PST-RB-SC (verify-and-stamp; confirms framework works)
2. PST-ICN-SC (4 × `shift_value`; teaches `assign+shift` idiom)
3. PRF-13 Raku (111 × `shift_value`; bulk mechanical)
4. PST-SN4-SC (`foldop`/`reduce_prim`/`reduce_opsyn`/`reduce_call`;
   introduces n-ary collect)
5. PST-PL-SC (delete ~64 helpers)
6. PST-SC-SC (delete ~110 helpers; biggest rewrite)

---

## Stage 2 — Lower (post-Phase-2)

After all six SCRIP mirrors are pure shift/reduce, the codebase
proceeds to the rename and per-construct lowering work:

- **PST-LR-0** — Bulk rename: `SM_*` → `IR_SM_*`, `IR_*` → `IR_BB_*`.
- **PST-LR-1..5** — Per-construct lowering: TT_AUGOP, TT_IF, TT_WHILE,
  TT_FOR, TT_CASE, TT_LOOP_BREAK/NEXT, TT_DEFINE, SNOBOL4 SCAN/SEQ
  split, TT_GOTO_*, Prolog slot allocation, Rebus lowering, cross-lang
  audit.

Full Stage 2 design lives in the historical archive of this file's
prior revision (see git log for commits before 2026-05-19); will be
restored as a fresh `GOAL-LOWER-REDESIGN.md` once Phase 2 lands.

---

## State

```
watermark:   2026-05-19 (Opus 4.7) — Phase 1 C ✅ all six. Phase 2:
             PST-RB-SC ✅, PST-ICN-SC ✅, PRF-14 (Raku) ✅ (this session),
             PST-SN4-SC ✅, PST-SC-SC ✅. PST-PL-SC remains ⏳ ready
             (only outstanding Phase 2 rewrite). Smoke tests for PRF-14
             and PST-SC-SC blocked by pre-existing container &ALPHABET
             segfault — debug-in-separate-session per audit's strict
             rule.
next:        PST-PL-SC (the last Phase 2 sibling), OR debug the
             container &ALPHABET segfault to unblock PRF-14-5 and
             PST-SC-SC-5 smoke simultaneously, OR Stage 2 PST-LR-0
             bulk rename SM_*→IR_SM_*, IR_*→IR_BB_*. Whichever Lon names.
audit ref:   PST-SCRIP-AUDIT.md (per-file violation list).
heads:       .github @ (this commit) · SCRIP @ e1c8a4ac ·
             corpus @ 87f99f6.
```

---

## Handoff note — 2026-05-19 session 7 (Opus 4.7) — PHASE 2 LAUNCH PACKAGE

**Session goal:** ready six parallel Phase 2 SCRIP mirror sessions.
Lon will fire each from its per-language goal file.

**What was done:**

1. **Audited all six `corpus/SCRIP/parser_*.sc` files** against the
   strict permitted-primitive list. Produced `PST-SCRIP-AUDIT.md`
   (705 lines): per-file violation counts, mechanical-replacement
   templates, helper-deletion lists, grammar-rewrite templates.

2. **Audited the PRIMER** against every construct actually used in
   parsers and includes (semantic.sc, ShiftReduce.sc, assign.sc,
   counter.sc, stack.sc, tree.sc, match.sc, qize.sc, global.sc, etc.).
   Identified 13 gaps; expanded PRIMER with a 350-line Phase 2
   authoring addendum covering: library load order, function-return
   mechanics (4 shapes not 3), unary-`.` vs binary-`.`, `$varname`
   indirect, `assign` rationale, OPSYN-as-shift/reduce, EVAL for
   captured-arg patterns, `epsilon . *fn()` canonical fire-side-effect,
   multi-assign-in-condition idiom, alt-eval `(e1, e2, e3)`, struct
   sugar, `Pop()` vs `Pop(.var)` dual signature, `$' '` punctuation-as-
   varname, `upr`/`lwr` runtime-not-library, plus a permitted-vs-
   forbidden cheat for grammar-rule writing.

3. **Rewrote every PST goal file terse.** Parent file 1227 → 176 lines.
   Per-language files 308/404/490/699/236/215 → 75/228/123/71/133/353
   lines. **Audit steps embedded as numbered ladders** in each file
   so each session is fully self-contained — reads SPITBOL manual +
   PRIMER + its own goal file + nothing else and starts work
   mechanically.

4. **Updated PLAN.md PST rows** to terse one-line summaries pointing
   at each per-language file.

5. **Installed strict rule** in every Phase 2 goal: "Do not let the
   program failing to run stop the rewrite." Mechanical deletion and
   rewrite first; tree-shape conformance debug after, in a separate
   later session. Smoke-test step always last; commit regardless of
   pass/fail with `⚠ MIRROR-GAP-<step>` notation.

**Files modified this session:**
- `GOAL-PARSER-PURE-SYNTAX-TREE.md` (1227 → 177 lines including this note)
- `GOAL-PST-REBUS.md` (rewritten — 71 lines)
- `GOAL-PST-ICON.md` (rewritten — 75 lines)
- `GOAL-PST-RAKU.md` (rewritten — 123 lines)
- `GOAL-PST-SNOBOL4.md` (rewritten — 133 lines)
- `GOAL-PST-PROLOG.md` (rewritten — 228 lines)
- `GOAL-PST-SNOCONE.md` (rewritten — 353 lines)
- `SNOBOL4-SNOCONE-PRIMER.md` (840 → 1191 lines; addendum at line 471)
- `PLAN.md` (PST rows updated)
- `PST-SCRIP-AUDIT.md` (NEW — 705 lines; reference; steps already in goals)

No code changes to SCRIP or corpus.

**Phase 2 launch criteria — six sessions ready:**

| # | rung | file | session size | first step |
|---|------|------|-------------:|------------|
| 1 | PST-RB-SC  | parser_rebus.sc   | 10 min  | RB-SC-1 grep verify |
| 2 | PST-ICN-SC | parser_icon.sc    | 30–60 m | ICN-SC-1 four `shift_value → assign+shift` rewrites |
| 3 | PRF-13     | parser_raku.sc    | 2–3 h   | PRF-13-1 read file + locate 111 `shift_value` |
| 4 | PST-SN4-SC | parser_snobol4.sc | 1.5 h   | SN4-SC-1 twelve `reduce_prim` rewrites |
| 5 | PST-PL-SC  | parser_prolog.sc  | 4–6 h   | PL-SC-1 delete ~64 helpers + state |
| 6 | PST-SC-SC  | parser_snocone.sc | 4–6 h   | SC-SC-1 delete ~110 helpers + state |

Each session reads:
1. PLAN.md, RULES.md (orientation)
2. SPITBOL manual chapters 6, 7, 9, 15 (mental model)
3. SNOBOL4-SNOCONE-PRIMER.md including the Phase 2 SCRIP authoring
   addendum at line 471 (library primitives)
4. Its `GOAL-PST-<LANG>.md` (entry point; audit steps as numbered ladder)

Phase 1 C parsers are clean (AUDIT-2 verified). Each `tree_t` shape in
the C parser is the target for the SCRIP rewrite. Beauty self-host md5
`abfd19a7a834484a96e824851caee159` must remain green throughout
(but Phase 2 changes touch only `corpus/SCRIP/parser_*.sc`, not the C
path beauty uses — so the risk is low and bounded).

**Stage 2 (post-Phase-2):** bulk rename `SM_*` → `IR_SM_*` and `IR_*` →
`IR_BB_*`, then per-construct lowering for TT_AUGOP/IF/WHILE/FOR/CASE/
LOOP_BREAK/NEXT/DEFINE/SCAN-SEQ-split/GOTO/Prolog-slot-alloc/Rebus.
Will be restored as `GOAL-LOWER-REDESIGN.md` once Phase 2 lands.

.github @ (this commit)
