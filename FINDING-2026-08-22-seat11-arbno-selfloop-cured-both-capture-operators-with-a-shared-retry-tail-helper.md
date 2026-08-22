# FINDING 2026-08-22 seat11 — `rung-arbno-selfloop` CURED IN BOTH CAPTURE OPERATORS: THE MISSING RETRY TARGET WAS `out_rtail`, NOT A SENTINEL-SKIP OVER `pe`

**Row:** `rung-arbno-selfloop` (QUEUE.tsv rank 0), HQ's direct dispatch, root-caused at source level in `FINDING-2026-08-22-s256-hq-arbno-selfloop-is-a-missing-sentinel-skip-in-both-capture-operators.md`. That FINDING named the defect exactly (`lower_snobol4.c:1463`/`:1439-1442`, `itail` taking the group's own bookkeeping sentinel as if it were a real box) and flagged the open design question as "which sentinel predicate" — **the predicate turned out not to be the fix.** A sentinel-skip cures the infinite loop but not the semantics; the correct retry target is a different piece of information (`sno_seq_nary`'s `out_rtail`) that the general `sno_pat_node` API never exposes.

## 1. HQ's prediction, falsified as instructed (HQ LAW 17), then confirmed

HQ's FINDING §3 predicted the byte-identical `TT_CAPT_COND_ASGN` (`.`) site should hang on the same shape as `TT_CAPT_IMMED_ASGN` (`$`), and asked the curing seat to test it before assuming so. Minted `corpus/probe/retry/rty_arbno_leftctx_cond.sno` (`(BREAK(' ') ARBNO(LEN(1))) . OUTPUT '.'`, oracle-refed via `x64/bin/sbl -bf` → `this is a test `) — **hung** (`timeout 5` rc=124, zero output, silent because conditional assignment never fires on an unterminated match). Prediction confirmed: both operators carry the defect.

## 2. Why a sentinel-skip alone is insufficient — traced against the live IR graph

First attempt (matching HQ's own framing): detect when `g->all[before_i]` is exactly the bogus zero-operand `IR_GOTO` `sno_seq_nary` mints as its first act (`γ.node == nd && ω.node == save`, the precise, provably-safe predicate — `sno_seq_nary`'s `S` is wired to those exact values at construction and never touched again in the loop that follows, so the check has no false positives against `TT_FAIL`/`TT_SUCCEED`'s own bare-`IR_GOTO` shapes, which differ on `γ` or `ω`), and fall back to `pe` (`sno_pat_node`'s return value) instead.

**This cured the hang but not the answer.** `--dump-ir` on the RED witness after this first fix:
```
17     18   16   MATCH_BREAK
18     19   17   MATCH_ARBNO      [26,26,26]
19     20   17   MATCH_ASSIGN_IMM [17,16]      <- ω=17 (BREAK), WRONG
```
`nd.ω` (node 19's retry port) resolved to node 17 = **BREAK**, not node 18 = **ARBNO**. Re-entering BREAK on backtrack re-scans from the CURRENT (already-advanced) cursor position instead of asking the generator for its next length — `rty_arbno_leftctx_inline` terminated but printed only `this` (one line, not the 12-line extension ladder); `rty_arbno_leftctx_cond` terminated with **no output at all** instead of `this is a test `. Silently wrong, exactly the failure mode HQ's FINDING warned about — just from a different cause than the one it named.

**The correct retry target, confirmed by the GREEN control:** `ARBNO(LEN(1)) $ v` has no wrapping group (`sno_pat_node` dispatches straight into `TT_ARBNO`, no `sno_seq_nary` involved), so `pe == g->all[before_i] == R` (the `MATCH_ARBNO` node itself) — retry re-enters ARBNO's own node directly, which is how it currently (correctly) works. The RED case needs the exact same thing — `itail` = ARBNO's own node — but ARBNO is *element 1 of 2* inside a group, and that value (`res[ne-1]` in `sno_seq_nary`'s own terms) is computed entirely inside `sno_seq_nary` and thrown away: its `out_rtail` parameter is called with `NULL` from `sno_pat_node`'s `TT_SEQ` case for the common (no-fence) path.

## 3. The fix: a shared helper that gets `out_rtail` instead of guessing at it

`sno_pat_node`'s signature (used at ~40 call sites across every pattern-construct case) was not touched — too wide a blast radius for this rung. Instead, a new static helper, used identically by both capture operators (NO-PER-OP-FILTER):

```c
static IR_t * sno_capt_body(scx_t * cx, const tree_t * t, IR_t * succ, IR_t * fail, IR_t ** out_itail) {
    IR_graph_t * g = cx->g;
    const tree_t * eff = t;
    if (eff && eff->t == TT_VAR && eff->v.sval) { /* same stored-pattern-variable inline resolution TT_VAR's own case uses */ }
    if (sno_pat_eff_kind(eff) == TT_SEQ) {
        /* flatten; if no fence and >1 element, call sno_seq_nary DIRECTLY with a real out_rtail, use that as itail */
    }
    /* else: original behavior, PLUS the sentinel-detection safety net from the first attempt, as defensive fallback */
}
```

For the common, now-fixed shape (a flat, unfenced, multi-element captured group), this calls `sno_seq_nary` itself — the exact function `sno_pat_node`'s own `TT_SEQ` case would have called — with a real `out_rtail` pointer instead of `NULL`, and uses `res[ne-1]` (ARBNO's own node in the witness case) as `itail`. This is not a new mechanism; it is the file's own existing per-element retry-chain output, previously computed and discarded.

**Two things this fix had to get right that a naive port would have missed, both caught by testing, not by inspection:**
- **Stored patterns route through `TT_VAR` inlining first** (`rty_arbno_leftctx_stored`, pattern assigned to a variable before the match statement) — `sno_pat_eff_kind` does *not* see through this (it only remaps bare keyword-shaped `TT_VAR`s like `ARB`/`BAL`, not user pattern variables). The helper replicates `TT_VAR`'s own inline-resolution condition (`SCRIP_PAT_INLINE`, `sno_encl_hostile`, `sno_fz_tree`, `sno_pat_inline_ok`) before testing for `TT_SEQ`, or this exact witness silently falls back to the old (wrong) behavior. First build without this passed the inline witness and failed the stored one — caught by the ladder, not assumed away.
- **Declaration order:** `sno_capt_body` calls `sno_pat_inline_ok`, which (unlike `sno_fz_tree`) has no forward declaration in this file — placing the helper before `sno_pat_inline_ok`'s own definition produced `error: static declaration of 'sno_pat_inline_ok' follows non-static declaration` (an implicit-declaration conflict). Relocated the helper to immediately before `sno_pat_node`'s definition (after every function it calls). Caught by the compiler, not guessed.

Both `TT_CAPT_IMMED_ASGN` and `TT_CAPT_COND_ASGN` now read identically:
```c
int before_i = g->n;
IR_t * itail = NULL;
IR_t * pe = sno_capt_body(cx, t->c[0], nd, save, &itail);
lc_γ_to(save, pe);
sno_ω_to(nd, itail);
```

## 4. Verification

`make pristine` EXIT=0 throughout.

**The full retry-family ladder, `corpus/probe/retry/` (15 witnesses, both modes for the 5 in the original table):**
- `rty_arbno_leftctx_inline`, `rty_arbno_leftctx_stored`, `rty_arbno_leftctx_cond` (new, this session) — all **RED→GREEN**, exact oracle byte-match, m3≡m4, confirmed by `--dump-ir` that `nd.ω` now resolves to ARBNO's own node.
- `rty_arbno_noleft_ctl`, `rty_break_nogen_ctl` — unchanged GREEN (no regression on the no-group / no-generator controls).
- `rty_fail_bal_inline`, `rty_fail_bal_stored_ctl`, `rty_fail_arb_inline`, `rty_deadlit_arb_ctl`, `rty_fail_span_ctl`, `rty_fence_arbno_defer`, `rty_fence_arbno_inline_ctl`, `rty_fence_arbno_stored`, `rty_fence_arbno_stored_1iter`, `rty_nofence_stored_ctl` — all MATCH, including every FENCE'd-capture witness (the fallback path, deliberately left untouched by the fast path, confirmed still correct).

**`breakx.sno` itself** (the program that started this whole chain, `corpus/programs/csnobol4-suite/breakx.sno`, previously a 9.5M+-line runaway): now **terminates and matches its `.ref` in both modes** (`this`/`this is`/`this is a`/`this is a test` ×2, once per statement).

**Corpus** (`test_corpus_snobol4.sh`): **m3 PASS=357 FAIL=2 · m4 PASS=355 FAIL=2 SKIP=2 (359 total)** — byte-identical to this session's own earlier same-tree measurement (taken before this fix, for the unrelated `free-r11` rung), same two pre-existing named failures (`160_pat_alt_inner_gen_resume`, `demo_treebank`). **Crosscheck** (`test_crosscheck_snobol4.sh`): **m3 322/1 · m4 321/1/1skip · DIVERGE=0**, the one failure being the same pre-existing `160_pat_alt_inner_gen_resume`. Both live gates green (`emit_no_lang` OK; `template_medium_invisible --strict` ratchet unchanged at 0, the informational `xa_flat.cpp` WIP count untouched).

**`.s` regen** (RULES.md order, `lower_snobol4.c` is a named codegen file): benchmark/feature — no changes (none of those 35 programs exercise a multi-element captured group). Demo — `claws5.s` changed (2 lines; claws5 is pattern-heavy and legitimately hits this shape). Programs (icon/prolog/rebus) — `changed=0` (confirms the fix is SNOBOL4-only, as designed; the pre-existing 15 EMIT-FAIL/42 AS-FAIL entries are unchanged, unrelated WIP debt, same set as earlier in this session's `free-r11` regen). Prolog-bench — `changed=0`. Crosscheck — **2 files changed**: `184_pat_cond_assign_defer_double_fire.s` and `185_pat_cond_assign_defer_seq_minimal.s`, the two witnesses from this seat's own earlier-today `cond-assign-double-fire` row (a different bug, same general neighborhood — deferred/conditional capture over a sequence). Both re-verified directly: **still MATCH their `.ref`** in mode-3 — the emitted bytes shifted (this fix changes what `itail` resolves to whenever the captured pattern is a multi-element group, and these two witnesses are exactly that shape) but the observable behavior is unchanged and correct.

## 5. Scope note (HQ FINDING §5)

HQ flagged `json-alternate-af-spin` as "the same failure signature, must not be assumed to fold into this." Not investigated this session — out of scope, a different queue row, no evidence either way beyond what HQ already recorded.

## 6. Files touched

`src/lower/lower_snobol4.c` only (new static helper `sno_capt_body`; both capture-operator cases call it instead of the old inline `before_i`/`g->all[before_i]` computation). `corpus/probe/retry/rty_arbno_leftctx_cond.{sno,ref}` (new witness, oracle-refed). `.s` regen commits to `corpus` as detailed above (auto-committed by the regen scripts).
