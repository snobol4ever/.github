# GOAL-PST-RAKU.md — Pure Syntax Tree: Raku

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ Phase 1 C COMPLETE. Phase 2 OPEN — PRF-14 ready.

---

## Phase 2 — `corpus/SCRIP/parser_raku.sc`

**Rung:** `PRF-14` — complete rewrite from scratch. Estimated 4–6 h.

**Why a full rewrite, not a mechanical substitution:**
PRF-13 (2026-05-19) attempted to replace every `shift_val(EXPR, KIND)`
with `assign(.t_imm, EXPR) shift(t_imm, KIND)`. This was wrong.
`shift_val` in `semantic.sc` is `epsilon . *Shift(KIND, v)` — it pushes
a computed value without consuming input. `shift(p, KIND)` matches
pattern `p` against the source and pushes the *matched text* — a
fundamentally different operation. There is no one-line substitution.
The architecture of the file must change so that `shift` can do the
work directly. **Do not invent the approach — derive it from the
sources listed in the steps below.**

---

## Steps

- [ ] **PRF-14-1 — Read sources. No coding yet.**

  Read all four in this order:

  1. `corpus/SCRIP/semantic.sc` — understand exactly what `shift`,
     `reduce`, `nPush`, `nPop`, `nInc`, `nTop`, `assign` do at the
     Snocone/SPITBOL level. Do not assume. Read the code.

  2. `corpus/SCRIP/parser_snocone.sc` — the largest clean parser.
     Study how it pushes leaf values: what patterns feed `shift`,
     how token text is captured, how computed names are handled.

  3. `corpus/SCRIP/parser_snobol4.sc` — another clean parser with
     different leaf-value patterns. Note specifically how string
     literals and identifiers become `TT_QLIT` / `TT_VAR` nodes
     without `shift_val`.

  4. `one4all/src/frontend/raku/raku.y` — the Phase 1 C parser.
     This is the ground truth for every tree shape PRF-14 must
     reproduce. Every node kind, every child count, every value
     field. The SCRIP rewrite must match this exactly.

  Only after reading all four: look at `corpus/SCRIP/parser_raku.sc`
  and understand what each `shift_val` site is actually doing in terms
  of the tree node it produces.

- [ ] **PRF-14-2 — Identify the structural problem and the fix.**

  From the reading in PRF-14-1, determine:

  - Which `shift_val` sites push a string literal (`'die'`,
    `'raku_write'`, etc.) vs. a runtime-captured variable
    (`capvf capvr`, `colnmf colnmr`, etc.).
  - What the clean parsers do in analogous situations.
  - What restructuring (if any) of the token-capture patterns
    (`VarScalar`, `VarArray`, `BareIdent`, etc.) is needed so
    `shift` can capture the right value directly.

  Write nothing yet. Document the findings as a comment block at
  the top of the new file in PRF-14-3.

- [ ] **PRF-14-3 — Rewrite `parser_raku.sc` from scratch.**

  Using the approach determined in PRF-14-2 and the tree shapes
  from `raku.y`, write a new `parser_raku.sc` that:

  - Uses only permitted primitives: `shift`, `reduce`, `nPush`,
    `nPop`, `nInc`, `nTop`, `assign`. Pure string preprocessors
    (`dq_unescape`) permitted.
  - Produces identical tree shapes to the C parser for every
    construct.
  - Contains zero `shift_val`, `foldop`, `reduce_call`,
    `reduce_prim`, `reduce_opsyn`.
  - Contains zero `function` definitions that call `Push`, `Pop`,
    `Tree`, `tree`, `Append`.

  Do not preserve the old file's structure out of habit. If the
  token-capture layer needs to change, change it. Follow the
  evidence from PRF-14-1 and PRF-14-2.

- [ ] **PRF-14-4 — Grep verify.**

  ```
  grep -nE 'shift_val|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_raku.sc
  grep -nE '\b(Push|Pop|Tree|tree|Append|IncCounter|TopCounter)\(' parser_raku.sc
  grep -nE '^function ' parser_raku.sc
  ```

  First two: zero hits (comments excepted).
  Third: only `dq_unescape` (or zero if eliminated).

- [ ] **PRF-14-5 — Smoke test.**

  ```
  bash /home/claude/one4all/scripts/test_smoke_raku.sh
  ```

  If passes, commit. If fails, file `⚠ MIRROR-GAP-PRF-14-5` and
  commit anyway — debug in a separate session. Record exact failure
  output in the State block.

---

## Closed rungs (Phase 1 C — history)

All 25 PRF-12 sub-rungs closed across many sessions: program, my-type,
say, print, arr-hash-ops, try, unless, given, smatch, new, mcall, die,
hof, capture, twigil, sub, class, for, gather, self, gather-splice
(R19), gather-hoist (R27). R15 rescoped 2026-05-19 as parser-local-
scratch idiom (PRF-12-R15-DISPOSITION).

PRF-13 (2026-05-19, Sonnet 4.6): REVERTED. assign+shift approach wrong.
corpus restored to 380da41 (111 × shift_val intact). See above.

---

## State

```
watermark:   PRF-13 reverted (2026-05-19, Sonnet 4.6). corpus @ 8dea9a9.
             PRF-14 written: full rewrite, derive approach from sources.
next:        PRF-14-1 — read semantic.sc, parser_snocone.sc,
             parser_snobol4.sc, raku.y. No coding until PRF-14-2 done.
heads:       one4all @ 50dee1c2 · corpus @ 8dea9a9
```

---

## Handoff note — 2026-05-19 session (Sonnet 4.6)

**What happened this session:**

1. Scanned all six `parser_*.sc` files — found PRF-13 (Raku) was the
   only incomplete Phase 2 rung.
2. Deleted `FoldOp`, `ReduceCall`, `ReducePrim`, `ReduceOpsyn` from
   `ShiftReduce.sc` — library side clean. corpus `ec82c70`.
3. Attempted PRF-13: replaced 111 × `shift_val` with
   `assign(.t_imm, EXPR) shift(t_imm, KIND)`. **Wrong approach.**
   `shift` matches input; `shift_val` pushes a computed value without
   consuming input. The two are not substitutable.
4. Reverted PRF-13. corpus restored to `8dea9a9` (380da41 content).
5. Wrote PRF-14: full rewrite step that instructs next session to read
   `semantic.sc`, `parser_snocone.sc`, `parser_snobol4.sc`, `raku.y`
   before writing a line, then derive the correct architecture.

**What next session must do:**
Start at PRF-14-1. Read the four sources. Do not skip ahead.
