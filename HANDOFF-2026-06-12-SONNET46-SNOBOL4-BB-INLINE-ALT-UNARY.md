# HANDOFF 2026-06-12 · Sonnet 4.6 · SNOBOL4-BB duplicate-label fix landed

**SCRIP HEAD:** `4c65b17`
**.github HEAD:** (this commit)

---

## What this session did

### Fix landed: duplicate proto labels in 5 builder templates (commit `4c65b17`)

All five pattern builder templates (`bb_pattern_lit`, `bb_pattern_arb`, `bb_pattern_nullary`, `bb_pattern_unary_i`, `bb_pattern_unary_s`) had a `xx_bump()` counter function declared but never called. Each invocation of the same box kind within one compilation emitted the same local label (`.Lpb0_s`, `.Lpb0_desc`, etc.), causing the assembler to reject programs with multiple builders of the same kind (e.g. `P = ('a' | 'b' | 'c')`).

**Fix:** Added `xx_bump()` call at the start of each exported template function (inside the `if (PLATFORM_X86)` block, restructured to a proper `{ }` body).

**Gate met:** smoke 7/7/7 · pat-rung **19/19/19 no-SKIP** (was 18 PASS + 1 SKIP) · fence HARD.

---

## _wγ/_wω ARBNO link error — investigated, NOT fixed this session

### What was learned

The `_wγ`/`_wω` undefined-reference link errors in Qize/XDump/omega beauty programs come from `bb_match_arbno` emitting `jmp Qize_c0_wγ`/`_wω` in child body epilogues, but the ARBNO match box (which defines those labels) never being reached during flat emission.

**Actual IR structure** (from `--dump-bb` of Qize): entry is `PAT_POS[9]`, followed by a γ-chain of `PAT_ASSIGN_COND` nodes, terminating at `PAT_CAT[2]` with `nkids=0`. The ARBNO node `[6]` is NOT in the γ-chain — it is a sub-operand of `ASSIGN_COND[5]`.

`flat_drive_match` calls `gather_lowered_cat_arms(POS[9], stop=NULL)`, which walks POS→ASSIGN_COND[5]→ASSIGN_COND[3]→PAT_CAT[2] and returns `catn=3`, `catnd=PAT_CAT[2]`. `flat_drive_cat_arms` is called, which walks `walk_bb_flat(ASSIGN_COND[5])` → `flat_drive_capture`.

Inside `flat_drive_capture`, `ch = bb_match_kid(ASSIGN_COND[5], 0)` = `PAT_BREAK[8]`. The inner γ-chain is BREAK[8]→LIT[7]→ARBNO[6]→ASSIGN_COND[5] (= stop = pBB). `gather_lowered_cat_arms(BREAK, stop=ASSIGN_COND[5])` currently returns 0 because the terminal `c == stop` is an ASSIGN_COND, not an IR_PAT_CAT with nkids==0 (the only success condition in the current code).

**Attempted fix:** Added `if (n >= 2 && stop && c == stop) { *cat_out = entry; return n; }` to `gather_lowered_cat_arms`. This correctly fires for the Qize case. However, `flat_drive_cat_arms` with `catnd=entry` (a PAT_BREAK node, not a real CAT) reaches `EMIT_PAIR_FILL(catnd, ...)` at the end, which emits the PAT_BREAK template's wiring — this does NOT define the `xcat_ω` label that `flat_drive_cat_arms` allocates internally, causing linker "undefined reference to xcat10_ω" errors.

**Root cause of the label gap:** `flat_drive_cat_arms` allocates `xcat_ω` etc. and expects `EMIT_PAIR_FILL(catnd, ...)` at the end to define them (via the IR_PAT_CAT template). When catnd is not a real CAT node, they remain undefined.

### What next session must do

The fix requires one of:

**(A) Inline the cat-arm chaining in flat_drive_capture for the stop-terminated case.** When gather returns n>=2 arms with c==stop, emit the arms using the same left→right chaining logic as flat_drive_cat_arms but WITHOUT the trailing EMIT_PAIR_FILL. This avoids needing a real catnd. The logic is: walk arm[0] to mid_γ, define mid_γ, walk arm[1] to lbl_γ (for n=2); for n>2, chain through intermediate γ labels.

**(B) Add a "no-fill" variant of flat_drive_cat_arms** that skips the trailing EMIT_PAIR_FILL and instead explicitly defines `xcat_ω → lbl_ω` and `lbl_β → left_β` inline.

Either approach must: (1) not disturb the stop=NULL code path in flat_drive_match, (2) pass all 19/19/19 pat-rung tests, (3) fix the Qize link error so beauty gate improves from 4→7+ PASS.

**Probe to use:** compile `corpus/programs/snobol4/beauty_suite/Qize_driver.sno` — assemble, link. Should not produce `undefined reference to Qize_c0_wγ`.

---

## Gates at session end

- smoke: **7/7/7** HARD ✓
- pat-rung: **19/19/19 no-SKIP** ✓
- fence: **HARD** ✓
- SCRIP: `4c65b17`
