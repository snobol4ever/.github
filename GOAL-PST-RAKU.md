# GOAL-PST-RAKU.md — Pure Syntax Tree: Raku

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ Phase 1 C COMPLETE 2026-05-19. Phase 2 ready
(reference rung for all Phase 2 sessions).

---

## Phase 2 — `corpus/SCRIP/parser_raku.sc` (680 LOC)

**Rung:** `PRF-13` — bulk mechanical `shift_val → assign+shift`, 111
sites. Estimated 2–3 h. **This is the reference rung for the
`shift_val` idiom** — every other parser's `shift_val` work follows
the same template.

Per `PST-SCRIP-AUDIT.md § parser_raku.sc`: 111 `shift_val` calls. One
helper `dq_unescape` is permitted (pure string preprocessor — touches
zero tree state). No other function bodies exist that build tree state.

### Permitted primitives (binding)

`shift(p, kind)` · `reduce(kind, n)` · `nPush()` · `nInc()` · `nPop()` ·
`nTop()` · `assign(.var, val)`. Pure string preprocessors like
`dq_unescape` also permitted. Forbidden: `shift_val` (all other
forbidden primitives too — verify nothing else has crept in).

### The mechanical pattern

Every `shift_val(EXPR, KIND)` becomes:

```
assign(.t_imm, EXPR) shift(t_imm, KIND)
```

where `EXPR` may be a literal string, concatenation, or function call.
`t_imm` is a single shared parser-scratch variable. Avoid name
collisions with existing captures: `capstr`, `capvf`, `capvr`, `capmf`,
`capmr`, `capclsf`, `capclsr`, `capncname`, `capidx`, `capkey`,
`capnamedkey`, `capmtf`, `capmtr`, `captwf`, `captwr`, `colnmf`,
`colnmr`.

### Examples

```
shift_val('die', 'TT_VAR')
→ assign(.t_imm, 'die') shift(t_imm, 'TT_VAR')

shift_val(capvf capvr, 'TT_VAR')
→ assign(.t_imm, capvf capvr) shift(t_imm, 'TT_VAR')

shift_val(capstr, 'TT_FLIT')
→ assign(.t_imm, capstr) shift(t_imm, 'TT_FLIT')

shift_val('raku_arr_get', 'TT_VAR')  shift_val(colnmf colnmr, 'TT_VAR')
→ assign(.t_imm, 'raku_arr_get') shift(t_imm, 'TT_VAR')
  assign(.t_imm, colnmf colnmr) shift(t_imm, 'TT_VAR')
```

The `assign` lifetime ends in the very next match step, so `t_imm`
reuse across adjacent sites is safe.

### Steps

- [x] **PRF-13-1** — Read `parser_raku.sc` end to end. Locate every
  `shift_val` site:
  ```
  grep -nE 'shift_val' parser_raku.sc
  ```
  Expected: 111 hits (or close — count may include 1–2 comments).

- [x] **PRF-13-2** — Rewrite every site using the template above.
  Sweep linearly through the file; don't try to skip ahead.

- [x] **PRF-13-3** — Grep verify:
  ```
  grep -nE 'shift_val|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_raku.sc
  ```
  Expected: zero hits (except possibly comments that mention `shift_val`
  in the deletion log — those can be left as historical references or
  cleaned up).

- [x] **PRF-13-4** — Confirm `dq_unescape` is the only `function`
  definition remaining:
  ```
  grep -nE '^function ' parser_raku.sc
  ```
  Expected: one hit (`dq_unescape`).

- [x] **PRF-13-5** — Run smoke test:
  ```
  bash /home/claude/one4all/scripts/test_parser_raku.sh
  ```
  If passes, commit. If fails, file `⚠ MIRROR-GAP-PRF-13-5` and commit
  the rewrite anyway — debug in a separate session per the audit's
  strict rule.

### Done

`parser_raku.sc` is pure shift/reduce; per-language goal closed; the
mechanical template is now battle-tested for use in PST-ICN-SC.

---

## Closed rungs (Phase 1 C — history)

All 25 PRF-12 sub-rungs closed across many sessions: program, my-type,
say, print, arr-hash-ops, try, unless, given, smatch, new, mcall, die,
hof, capture, twigil, sub, class, for, gather, self, gather-splice
(R19), gather-hoist (R27). R15 rescoped 2026-05-19 as parser-local-
scratch idiom (PRF-12-R15-DISPOSITION).

---

## State

```
watermark:   Phase 2 PRF-13 ✅ COMPLETE (2026-05-19, Sonnet 4.6, corpus @ 70c063c).
             111 × shift_val → assign(.t_imm,…) shift(t_imm,…). Added t_imm = ''.
             PRF-13-3: zero live shift_val. PRF-13-4: dq_unescape only. ✅
             ⚠ MIRROR-GAP-PRF-13-5: scrip binary not buildable in container
             (EC-3f pre-existing build failure). Smoke deferred; rewrite clean.
next:        All 6 Phase 2 SCRIP mirrors complete. Stage 2 (lower rename) ready.
             See GOAL-PARSER-PURE-SYNTAX-TREE.md § Stage 2 (PST-LR-0..5).
heads:       one4all @ 50dee1c2 · corpus @ 70c063c
```
