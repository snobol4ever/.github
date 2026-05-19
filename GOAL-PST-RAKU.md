# GOAL-PST-RAKU.md — Pure Syntax Tree: Raku

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ Phase 1 C COMPLETE. Phase 2 PRF-14 ✅ COMPLETE.

---

## Phase 2 — `corpus/SCRIP/parser_raku.sc` ✅

**Rung:** `PRF-14` — full rewrite, mirrors `raku.y` exactly.
Style matches sibling parsers (`parser_snocone.sc`, `parser_rebus.sc`).

**Approach (derived from sources per the rewrite protocol):**

- Token-level mirror of `raku.l`: each KW/OP gets a `$'token'` rule.
  Keywords use the canonical `$' ' Id $ tx *IDENT(tx, 'name')` idiom
  (whole-Id capture + value-space test) so identifier-prefix matches
  like `myvar` cannot be parsed as `my` + `var`.
- All `TT_*` kind names declared as string constants at top so each
  grammar rule reads like `reduce(TT_ADD, 2)` — same readability tactic
  parser_rebus.sc uses.
- Leaf-pushers (`push_var_scalar`, `push_ident_as_qlit`, etc.) are
  pure pattern definitions that combine `assign(.tmp, …) shift(tmp, K)`.
  These are not `function` defs — they are pattern variables.
- One permitted pure-string preprocessor: `strip_sigil(s)` —
  chops one leading `$`/`@`/`%` byte, mirrors raku.y's C helper.
- `block` always wraps body as `TT_SEQ_EXPR(stmts…)`. C path's
  sub_decl/method/class flatten this; SCRIP path passes the wrapper
  through and lower flattens. F1-compliant: parse delivers the tree
  shape verbatim, no side-channel.
- `LIT_STR` and `LIT_INTERP_STR` both emit plain `TT_QLIT` with the
  raw string content. Lower handles escape unfold + `$`-interpolation
  (same call path as the C parser's `lower_interp_str`).
- `LitSubst` builds the `pat \x01 repl \x01 (g|-)` payload via
  `tx_subp CHAR(1) tx_subr CHAR(1) tx_subg` to match the C lexer's
  byte format byte-identically.

---

## Steps

- [x] **PRF-14-1** — Read sources (semantic.sc, parser_snocone.sc,
  parser_snobol4.sc, raku.y, raku.l).

- [x] **PRF-14-2** — Identify structural fit. Decision: token-with-Id
  capture for keywords; per-kind leaf-pusher pattern variables;
  TT_* constants up top; one `strip_sigil` preprocessor.

- [x] **PRF-14-3** — Rewrite `parser_raku.sc` from scratch (426 LOC,
  mirrors all 116 RHS alternatives across 27 raku.y non-terminals).

- [x] **PRF-14-4** — Grep verify:
  ```
  grep -nE 'shift_val|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_raku.sc   # → 0
  grep -nE '\b(Push|Pop|Tree|tree|Append|IncCounter|TopCounter)\(' parser_raku.sc   # → 1 (driver-tail Pop, permitted)
  grep -nE '^function ' parser_raku.sc                                              # → 1 (strip_sigil, permitted)
  ```
  All three gates pass per Phase 2 rules.

- [ ] **PRF-14-5 — Smoke test.** ⚠ MIRROR-GAP-PRF-14-5: blocked in this
  container by the pre-existing `&ALPHABET` segfault in `scrip --interp`
  (same blocker as PST-SC-SC-5 — `global.sc` line 3
  `&ALPHABET ? (POS(0) LEN(1) . nul);` crashes SM interp at
  one4all `e1c8a4ac` / EC-3f). Per the parent goal's strict rule —
  "Mechanical deletion and rewrite first; tree-shape conformance
  debug after, in a separate later session" — the rewrite is committed
  now and the smoke debug deferred to a separate session.

---

## Closed rungs (Phase 1 C — history)

All 25 PRF-12 sub-rungs closed across many sessions: program, my-type,
say, print, arr-hash-ops, try, unless, given, smatch, new, mcall, die,
hof, capture, twigil, sub, class, for, gather, self, gather-splice
(R19), gather-hoist (R27). R15 rescoped 2026-05-19 as parser-local-
scratch idiom (PRF-12-R15-DISPOSITION).

PRF-13 (2026-05-19, Sonnet 4.6): REVERTED. assign+shift mechanical
substitution was wrong — `shift_val` pushes computed values while
`shift` consumes input.

PRF-14-CLEAN, PRF-14-GRAMMAR, PRF-14-GRAMMAR-RR, PRF-14-GRAMMAR-RR-FIX
(2026-05-19, prior Sonnet 4.6 sessions): collectively stripped tree
actions and aligned recognizer to raku.y, but never re-attached tree
actions. The 316-line "recognizer skeleton" produced "Parse OK" /
"Parse Error" only — F1 violation (no tree on the channel).

PRF-14 (2026-05-19, Opus 4.7, this session): tree actions re-attached
in one sweep using the right architecture. 426 LOC. PST-PL-SC is now
the only outstanding Phase 2 rewrite (the other five sibling parsers
are ✅).

---

## State

```
watermark:   2026-05-19 (Opus 4.7) — PRF-14 ✅. parser_raku.sc 426 LOC,
             mirrors raku.y exactly (116 RHS alternatives, 27 non-
             terminals). All gates pass except smoke (⚠ MIRROR-GAP-
             PRF-14-5: pre-existing container segfault on &ALPHABET).
next:        PRF-14-5 smoke debug — same root cause as PST-SC-SC-5:
             fix &ALPHABET handling in sm_interp.c keyword path; then
             re-run test_smoke_raku.sh. Cross-frontend fix, not Raku-
             specific.
heads:       one4all @ e1c8a4ac · corpus @ 87f99f6 ·
             .github @ (this commit)
```

---

## Handoff note — 2026-05-19 session (Opus 4.7) — PRF-14 LAND

**Investigation:**
1. Cloned the three repos and read PLAN.md, RULES.md, the parent goal
   `GOAL-PARSER-PURE-SYNTAX-TREE.md`, this file, the PRIMER, and
   relevant SPITBOL manual chapters (6, 7, 9).
2. Audited `parser_raku.sc` against `raku.y` production by production
   — 116 alternatives across 27 non-terminals. Found the file had
   become a recognizer skeleton with zero tree actions (F1 violation).
3. Traced commit history: PRF-14-CLEAN stripped tree actions
   intending to re-add; PRF-14-GRAMMAR aligned recognition to raku.y
   exactly (correctly deleted ~345 lines of speculative full-Raku
   scaffolding that raku.y never accepts); PRF-14-GRAMMAR-RR converted
   binary-op chains to right-recursive; PRF-14-GRAMMAR-RR-FIX restored
   ARBNO on list-collectors. Tree actions never reattached.
4. Searched web for an official Raku BNF — confirmed real Raku has no
   flat BNF (NQP grammars in Rakudo). The project's `raku.y` is a
   deliberately small hand-written subset and IS the source of truth.

**What was done:**

Rewrote `parser_raku.sc` from scratch in one sweep. 426 LOC. Style
matches `parser_rebus.sc` and `parser_snocone.sc` (two-column token
table, TT_* constants up top, `nTop_count` constant, `X_*` recursive
helpers, identical driver tail). Every raku.y production has its
exact tree action attached. All audit greps pass.

**Files modified this session:**
- `corpus/SCRIP/parser_raku.sc` — full rewrite, 316 → 426 LOC.
- `.github/GOAL-PST-RAKU.md` — this file (PRF-14 marked complete).
- `.github/GOAL-PARSER-PURE-SYNTAX-TREE.md` — Raku row marked ✅.
- `.github/PLAN.md` — PST: Raku row updated.

**What next session must do:**

Either:
(a) Debug the `&ALPHABET` segfault in `scrip --interp` to unblock
    BOTH PRF-14-5 and PST-SC-SC-5 smoke tests (cross-frontend fix);
(b) Move to Stage 2 — PST-LR-0 bulk rename `SM_*` → `IR_SM_*`,
    `IR_*` → `IR_BB_*` per the parent goal; or
(c) Whichever Lon names.
