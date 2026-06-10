# HANDOFF-2026-06-10-OPUS-ICON-NL-BETA-CHAIN.md

**Session:** 2026-06-10 · Claude (Opus)
**Goal:** GOAL-ICON-FULL-PASS — diagnose the m2 regression, begin recovery
**HEAD (SCRIP):** `aff86df`
**m2:** 150 → **155** (+5)

---

## What this session did

Inherited the prior handoff's open question: m2 had dropped from 193 (`15608cf`) to 150 (HEAD), and the prior session *guessed* the cause was BB-FIXUP/Pascal commits touching shared IR infra, recommending a bisect.

### 1. Bisect — TWICE — overturned the guess

- **Pass 1 (NL path, default):** first-bad = `c3b1dbb` (the NL flip). But `c3b1dbb` changes ONE line (`nl_on(0)`→`nl_on(1)`).
- The 21 regressed tests produce **byte-identical `--dump-bb`** under NL and SCRIP_NL=0 at HEAD — so the lowerer output is not the discriminator.
- **Pass 2 (SCRIP_NL=0 path):** first-bad = **`3546ea2` ("DELETE lower_icon.c")**.

**Key realization:** after `3546ea2` removed `lower_icon.c`, `SCRIP_NL=0` no longer selects an old lowerer — it selects *nothing different*. So the flip-gate cross-checks in `c3b1dbb`'s message ("icn corpus execution cross-check m2 7/8 SAME") were comparing the NL lowerer **against itself**. The conversion passed its gate vacuously.

### 2. Root cause — the generator β-chain

`3546ea2` also deleted this line from `lower.c`:
```c
if (cx.lang == IR_LANG_ICN) { ... lower_icn(cx, e, γ, ω, ...) ... }
```
The old `lower_icn` (and the `lower.c` value path it shared — `v_binop`, `v_to`, `emit_leaf`) threaded a **β-chain** the NL lowerer never replicated:

- BINOP lowers RIGHT operand with ω = LEFT's β.
- `v_to` lowers HI bound with ω = LO's β.
- β(TO) = the TO node itself · β(leaf) = inherited ω · β(BINOP) = right child's β.

Effect: when an inner generator exhausts, it re-pumps the **outer generator** (jumps to its β), producing the cross-product. NL passed the caller's ω to every child, so the inner generator jumped to the enclosing EVERY instead — only the first combination emitted.

Proof: `rung01_paper_mult` `(1 to 3) * (1 to 2)`:
- oracle (15608cf): inner TO `[8] ω=5β` (node 5 = outer TO)
- NL before fix:    inner TO `[8] ω=2β` (node 2 = EVERY) ← wrong

### 3. Fix landed (`aff86df`)

Added `IR_t * beta` to `icx_t`. Threaded it:
- `lower()` entry: `cx->beta = ω` (leaf default).
- BINOP: capture `lβ = cx->beta` after left; lower right with ω=`lβ`.
- `lower_to`: hi gets ω=`lβ`; set `cx->beta = to` on exit.
- `lower_call`: chain each arg's ω through `aω = cx->beta`; reset `cx->beta = ω` (det-call); subgraph path also resets.
- `lower_every`: `gen_node` (loop_back) = the threaded β when present — the true resume point. Fixes assign-generator `every total := total + (1 to n)` (proc_locals → 15).

`rung01_paper_mult` dump now byte-identical to the 15608cf oracle.

**Recovered (+5):** rung01_paper_compound, rung01_paper_mult, rung02_arith_gen_nested_add, rung02_arith_gen_nested_filter, rung02_proc_locals.

---

## State (all gates green)

- m2 icon rung suite: **155**/247 (was 150)
- icon smoke m2 12/12 HARD · m3 10/12 · m4 10/12 (same 2 pre-existing: proc_zeroarg, proc_recursion)
- prolog smoke m2 5/5 HARD ×3
- one-box gate PASS · no value stack · no C byrd-box · no bb_bin_t

---

## Open — 16 regressions remain

Same β-contract not yet applied to: **UNOP (`!x`), SECTION, SUSPEND arg-blocks, GEN_SCAN (`?`), `not`, REPEAT/BREAK, the bang generator.**

Tests: rung03_suspend_gen{,_compose,_filter}, rung01_paper_nested_to, rung06_cset_any_fail, rung07_control_not, rung07_control_repeat_break, rung08_strbuiltins_find_gen, rung08_strbuiltins_match, rung10_augop_break_repeat, rung11_bang_augconcat_bang_{concat,str}, rung13_table_iterate, rung20_section_seqexpr_section_{basic,full,var}.

**Recipe (diff-driven):** the deleted `lower_icon.c` is still in git — `git show 15608cf:src/lower/lower_icon.c` reads it; `git stash && git checkout 15608cf && build` gives the byte oracle via `--dump-bb prog.icn`. Make NL match node-for-node, then verify m2.

**Flag for Lon:** future lowerer flips need full-corpus execution parity as the gate, not 8-program samples — the broken `SCRIP_NL=0` oracle let a deficit-carrying flip through. Consider restoring a real oracle (keep one old lowerer behind the switch, or snapshot expected `--dump-bb` per rung) before the next conversion.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
