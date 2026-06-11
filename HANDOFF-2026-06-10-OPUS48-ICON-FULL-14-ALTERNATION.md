# HANDOFF-2026-06-10-OPUS48-ICON-FULL-14-ALTERNATION.md

**Session:** 2026-06-10 · Claude (Opus 4.8)
**Goal:** GOAL-ICON-FULL-PASS — FULL-14 alternation lowering
**HEAD (SCRIP):** `2dd9a2a`
**m2:** 178 → **184** (+6) · m3 27 → 29 · m4 30 → 32

---

## Baseline verification (before any edit)

The repo HEAD was `1c687d2`, two Icon-neutral commits past the Icon watermark `f5072d0`
(`1a1eeb6` Prolog arity-3, `1c687d2` Pascal LAD-2d). The Pascal commit touched **shared
`binop_apply`** (added a string-relop arm) — exactly the class of change that moved the Icon
count before — so the inherited m2=178 was re-measured, not trusted. Full rung suite at
`1c687d2` confirmed **m2=178 / m3=27 / m4=30** unchanged: the Pascal `binop_apply` arm is
Icon-neutral. All HARD gates green (icon m2 12/12, prolog m2 5/5, one-box PASS).

## The fix (one file, +12 lines: `src/lower/nl/lower_icon_nl.c`)

`TT_ALTERNATE` (`a | b | …`) was in `is_resumable` but had **no `lower()` case**, so it fell to
`default`→IR_SUCCEED — `write(1 | 2)` produced no value (empty output; oracle: `1`).

Added `lower_alt`, mirroring the oracle `wire_alt` (`lower.c:124`):

- Arms lowered **right-to-left**; arm *j*'s ω = arm *j+1*'s entry, last arm's ω = inherited ω_in.
- `arm_succ` = the ALT node; each arm lowered with γ = ALT node (defensive `γ_to` if unset).
- Arms array deposited via **`bb_operand_aux_set`** — verified the HEAD interp `IR_ALT`
  (`IR_interp.c:3021`) reads `bb_operand_aux_get`, which is the **opposite** of the
  `ir_operand_push` convention the NOT/SECTION/BANG fixes used. This asymmetry was the one real
  trap; getting it wrong yields an empty arms array and silent failure.
- entry = arm[0]'s entry; `cx->beta = node` (self-resume), so an enclosing `every` re-pumps the
  ALT and the interpreter advances exhausted arms via `arms[ci]->ω`.
- Routed `case TT_ALTERNATE: return lower_alt(...)`.

Canonical-source rule honored: read JCON `ir_a_Alt`, the SCRIP `wire_alt` transcription, AND the
HEAD interp `IR_ALT` consumer, plus confirmed the AST is flat n-ary (`1|2|3` → one `TT_ALTERNATE`
with three children) before writing a line.

## Verification

- m2 **178 → 184 (+6)**, m3 27 → 29, m4 30 → 32, **zero regression**.
- HARD gates green: icon m2 12/12, prolog m2 5/5, one-box PASS.
- Manual proofs (all match oracle semantics):
  - `write(1 | 2)` → `1`; `write(1 | 2 | 3)` → `1`
  - `every write(1 | 2 | 3)` → `1 2 3` (β=node self-resume re-pumps each arm)
  - `"world" ? write(match("xyz") | 0)` → `0` (scan-in-alt: the original-16 `rung08_strbuiltins_match` residual)
- **FULL-18 progress:** `rung13_alt_nested` (alt cross-product) now PASSES.

## Open — residual (next step)

**`rung13_alt_filter`**: `every (x := (1|2|3|4)) > 2 & write(x)` still prints nothing (oracle: `3` `4`).

Decomposed — **this is NOT an alternation bug**:
- `every write((1|2|3|4) > 2)` → `2 2` — **correct** (Icon relops return their *right* operand; `3>2`
  and `4>2` each yield `2`). The alt works fine inside a relop.
- `every write((x := (1|2|3|4)) > 2)` → empty — the gap. The **assign-generator** `x := alt` does not
  propagate its self-resume β up through the chaining `write` call to the enclosing `every`. Trace: the
  alt correctly leaves `cx->beta = alt-node`, the BINOP preserves it, but `lower_call`'s chaining-call
  path then resets `cx->beta = ω` unless `g_icn_postfix_resume` is set (the `c9ec94c` gate). So `every`
  cannot re-pump the buried generator.

This is the β-chain family, distinct from alt lowering. **Do not loosen the `c9ec94c` gate blindly** — it
was added to fix the write-chaining tests and may regress them. The fix needs its own step: propagate a
generator β through the chaining-call path when the last arg is itself resumable, without disturbing the
single-shot write-chaining case.

Other untouched goal items: FULL-12 coerce, FULL-13 keyword residuals, FULL-14 scan-alt, FULL-15 str
relop, FULL-16 mutual recursion, FULL-17 sort().

## State invariants (all hold)

- No value stack, no C byrd-box functions, no `bb_bin_t`.
- `lower_icon_nl.c` is the sole Icon lowerer; one-box gate PASS.
- icon m2 12/12 HARD · m3 10/12 · m4 10/12 smoke (same 2 pre-existing: proc_zeroarg, proc_recursion).
- prolog m2 5/5 HARD.

## Reproduce the oracle (if needed for the β residual)

`git worktree add /tmp/oracle 15608cf && cd /tmp/oracle && make -j4 scrip`
(`build_scrip.sh` hard-codes `$ROOT/SCRIP`, so `make` directly). Confirm by **output**, not `--dump-bb`
alone — `operand_aux` is invisible in the dump.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
