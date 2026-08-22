# FINDING — seat2, breakx-no-extend-runaway: BREAKX itself is cured; the runaway is ARBNO's own retry wiring collapsing into a self-loop when ARBNO has a left neighbour

**Date:** 2026-08-22 · **Seat:** seat2 (`/home/claude2`, Claude Sonnet 5) · **Topic:** `breakx-no-extend-runaway` · **Status:** DEDUPE VERDICT DELIVERED, ROOT CAUSE LOCALIZED TO EXACT WRONG IR FIELDS, NOT CURED THIS SESSION — checked in RED with a 4-witness ladder

## 1. The dedupe verdict the brief asked for: NO, this does not fold into `rty-fail-inline-retry`

That row is **CLOSED**. Its s192 fix (SCRIP `ed61196c`, `zd_plan`'s γ-release membership test widened to `(k > r || gib)`) is live in the current tree — reproven here, not trusted:

```
rty_fail_bal_inline.sno    -> MATCH (A/AB/ABC/done)
rty_fail_bal_stored_ctl.sno -> MATCH
rty_fail_arb_inline.sno    -> MATCH
```

**And it cured BREAKX too, as a side effect, exactly as NO-PER-OP-FILTER predicts for a same-family fix.** `breakx.sno`'s first statement — bare `subj BREAKX(' ') $ OUTPUT '.'` — now prints exactly the correct 4 lines (`this` / `this is` / `this is a` / `this is a test`) and terminates. The brief's framing ("BREAKX is ARCH-PASSTHRU CLASS 2... whose whole definition is that beta RE-ENTERS and extends") is no longer the live defect — that box is fine.

**The runaway breakx.sno still exhibits (9.5M+ lines) comes entirely from its SECOND statement**, `subj (BREAK(' ') ARBNO(LEN(1) BREAK(' '))) $ OUTPUT '.'` — a different box (ARBNO), not touched by the s192 fix, and not one of the witnesses that fix's blast-radius sweep covered.

## 2. Ablation ladder — the exact minimal ingredient

Four probes checked in at `corpus/probe/retry/`, all against `subj = "this is a test ."`, `&ANCHOR=1`:

| probe | shape | SCRIP | oracle (`sbl -bf`) |
|---|---|---|---|
| `rty_arbno_leftctx_inline` | `(BREAK(' ') ARBNO(LEN(1))) $ v '.'` | **hangs — prints `this` forever** | terminates, extends t/th/thi/this/... |
| `rty_arbno_leftctx_stored` | same, pattern stored in a variable first | **hangs identically** | terminates identically |
| `rty_arbno_noleft_ctl` | `ARBNO(LEN(1)) $ v '.'` (no left neighbour) | **correct, terminates** | terminates |
| `rty_break_nogen_ctl` | `BREAK(' ') $ v '.'` (no ARBNO at all) | **correct, terminates** | terminates |

Two things this rules out immediately: **(a) not inline-vs-stored** (unlike the BAL/ARB s192 defect, the stored road is equally broken — `rty_arbno_leftctx_stored` hangs byte-for-byte the same as the inline twin); **(b) not BREAK's own semantics** (BREAK alone, and BREAK *inside* the ARBNO body — tested separately, not shown in the table — both work; only a BREAK *before* the ARBNO in the same `$`-captured group breaks it). ARBNO's own retry is sound in isolation (`rty_arbno_noleft_ctl` is green). The one ingredient that flips it: **something precedes the ARBNO inside a group that a trailing element forces to retry.**

⛔ **Run the two RED probes only under `timeout` with stdout redirected to a file** — same hazard as `breakx.sno` itself.

## 3. Root cause, localized to two exact wrong field values (IR-diff, not asm-diff — asm diff found the site, IR dump named the fields)

`--dump-ir` on the RED minimal witness vs. the GREEN no-left-neighbour control (`rty_arbno_noleft_ctl`):

**GREEN** (`ARBNO(LEN(1)) $ v '.'` — ARBNO is element 0):
```
17  MATCH_ARBNO       γ=18  ω=16   ; exhaustion retreats to MATCH_ASSIGN_SAVE (correct: no left neighbour)
18  MATCH_ASSIGN_IMM  γ=19  ω=17   ; retry retreats DIRECTLY into MATCH_ARBNO (its β/retry port)
```

**RED** (`(BREAK(' ') ARBNO(LEN(1))) $ v '.'` — ARBNO is element 1, BREAK is element 0):
```
17  MATCH_BREAK       γ=18  ω=16
18  MATCH_ARBNO       γ=19  ω=16   ; ⛔ exhaustion retreats to MATCH_ASSIGN_SAVE(16), SKIPPING BREAK(17) ENTIRELY
19  MATCH_ASSIGN_IMM  γ=20  ω=26@  ; ⛔ retry retreats into node 26@, a stray GOTO(γ=19,ω=16)...
26@ GOTO              γ=19  ω=16   ; ...whose γ points BACK AT 19 — an infinite self-loop, ARBNO's β is never reached
```

The asm confirms it symbol-for-symbol: `n14_match_assign_imm_β: jmp n14_match_assign_imm_α` (RED) where the GREEN sibling has `n13_match_assign_imm_β: jmp n12_match_arbno_β`. `assign_imm`'s retreat never reaches `arbno_β` at all — it loops on itself, re-emitting the same `$OUTPUT` value (`this`) every pass, forever. This is the runaway, mechanically, not just structurally.

**What SHOULD hold, by the general contract `sno_seq_nary` implements everywhere else:** element *i*'s exhaustion/retry ports resolve to `res[i-1]` (the immediately preceding element's own retreat entry) — for RED that's `res[0]` = the BREAK node (17), not 16. And the box immediately after ARBNO should retreat straight into ARBNO's own port, not through an intermediary that loops on itself.

**Hypothesis, not yet proven by a source-level fix (flagged PLAUSIBLE, not CONFIRMED):** the parenthesized group `(BREAK ARBNO)` under a trailing `$` is very likely lowered as a *nested* `sno_seq_nary` call — the immediate-assign is built as its own node (`lower_snobol4.c` around the `IR_MATCH_ASSIGN_IMM` construction site) with the group recursively lowered via `sno_pat_node`, and node 26@'s shape (`γ=<the assign node>, ω=<the outer sentinel's eventual target>`) matches exactly what that inner call's own local `S` sentinel would look like (`lower_snobol4.c:1174-1175`). If so, the bug is in how that inner call's local sentinel gets resolved against the ARBNO's own `sno_ω_to(R, fail)` write (`lower_snobol4.c:1386`) across the nesting boundary — plausibly the inner call's φ-tag resolution for ARBNO's exhaustion port, or for the node that follows it, reaches for the *outer* call's original fail target instead of the correct local predecessor once nesting is introduced. **This was not chased further into a confirmed fix** — the mechanism is `sno_seq_nary` (`lower_snobol4.c:1172-1218`) interacting with the `TT_ARBNO` construction case (`lower_snobol4.c:1382` onward), and is exactly the kind of hand-rolled pointer/UTF-8-marker graph surgery (`φ`/`σ` bytes as sentinel tags) this file uses throughout — a wrong guess here risks a *different* wrong wiring elsewhere in the same shared, NO-PER-OP-FILTER mechanism, which is why this session stopped at "named and evidenced" rather than "patched."

## 4. Corpus/gates impact

No compiler source touched — four new corpus probe files only (`corpus/probe/retry/rty_arbno_leftctx_inline.{sno,ref}`, `rty_arbno_leftctx_stored.{sno,ref}`, `rty_arbno_noleft_ctl.{sno,ref}`, `rty_break_nogen_ctl.{sno,ref}`), refs minted from the live oracle (`x64/bin/sbl -bf`). `breakx.sno`/`.ref` themselves are untouched (existing corpus convention: don't hand-edit checked-in witnesses). `.s` regen: N/A, no codegen file moved. `test_gate_*` scripts: unaffected (no emitter/template/lowerer edit landed). `breakx.sno` remains a known-red, `timeout`-bounded hang in the csnobol4 suite — same accepted shape as the s189 `fuzz-hang-batch` family, not a new hazard.

## 5. Recommended next row

`arbno-left-neighbor-retry-selfloop` (or HQ's preferred name) — owns: confirm the nested-`sno_seq_nary` hypothesis above with `--dump-ir` on the actual `lc_build` call sequence (a print/trace at construction time would settle it faster than reading the graph after the fact), fix the retreat wiring for a non-first ARBNO under `$`, re-verify all four probes here flip to MATCH, re-verify `breakx.sno` matches its `.ref` in both modes and terminates, re-run the `rty-fail-inline-retry` family (BAL/ARB/BREAKX) to confirm no regression, sweep the corpus for the same left-neighbour shape on other generator boxes (ARB/BAL preceded by a non-generator element under `$` — the s192 fix's own witnesses were all generator-first, so this may be a second, previously-unexercised face of the same family).
