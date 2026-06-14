# HANDOFF — 2026-06-14 · Opus 4.8 · SNOBOL4-BB
## PB-RB-5 single-variable cset half + correction of the 064/065 misdiagnosis

**SCRIP base:** `4d37dcc` (B7 FENCE) → **+1 commit this session `1e3f30b`**
**Goal:** GOAL-SNOBOL4-BB.md · **Ladder:** SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md
**Gates (all green at handoff):** smoke 7/7/7 HARD · pat-rung 19/19/19 no-SKIP (m2==m3==m4) · fence TIER1=0 TIER2=0 HARD · corpus M2=186 M3=171 M4=166 SKIP=8

---

## TL;DR

The prior watermark named the next item as *"064/065 = FENCE(P) with a `. N` CAPTURE → route `flat_drive_capture` through diamond-collapse,"* an M4-only emit fix. **Verify-first against sbl proved that diagnosis wrong.** The actual bug was operand-variance in the character-set pattern family, present in **M2 and M3**, nothing to do with FENCE or capture. I landed the single-variable half of the fix (one commit), validated it against sbl, and re-scoped the remainder. **No goal regressed; M2 +4, M3 +2, M4 held.**

---

## What was wrong

A cset primitive with a **variable** argument — `SPAN(var)`, `ANY(var)`, `BREAK(var)`, `BREAKX(var)`, `NOTANY(var)` — read **no operand**. It treated the variable's *name* as if it were the literal cset.

Evidence (all `[want] sbl vs M2/M3 before fix`):
- `SPAN(digits) . N` over `"42rest"`, anchored → want `2`; sbl `2`; **M2/M3 empty**.
- same, unanchored → want `42`; sbl `42`; **M2/M3 `st`** — the only run of the *letters* `{d,i,g,t,s}` in `42rest`. Smoking gun: the cset literally was the string `"digits"`.
- `POS(0) SPAN(d) RPOS(0)` over `"789"` → want consumed-all; sbl consumed-all; **M2/M3 did-not-consume** (cset `{d}`).
- `ANY(s) . C` /`"xQy"` → `x` vs **empty**; `BREAK(b) . C` /`"ab,cd"` → `ab` vs **`a`**; `BREAKX(s)` → `ab` vs **empty**.
- literal-cset controls (`SPAN("0123456789")`, `LEN(n)` with var `n`) were always correct.

`LEN(var)`/`POS(var)`/`TAB(var)`/`RTAB(var)` already worked — cut-#2 rung-2 gave the **integer** family the `dval != 0` deferral; the cset family was left out.

## Root cause (code-level)

`src/lower/lower_snobol4.c`, scan-element lowering `lower_pat_node`:
- **Integer family** (POS/RPOS/LEN, lines ~195-215) discriminated the arg: `if (arg->t==TT_VAR||TT_KEYWORD) { IR_LIT(nd).sval = arg->v.sval; IR_LIT(nd).dval = …; } else IR_LIT(nd).ival = …;` → variable stored as **name + flag** for late lookup. Correct.
- **Cset family** (SPAN/ANY/BREAK/BREAKX/NOTANY, lines ~182-194) did `IR_LIT(nd).sval = t->c[0]->v.sval` **unconditionally** → for a TT_VAR arg that's the **name**, with **no flag**. Bug.

The interpreter was **already equipped** to look the variable up; the flag just never got set:
- `IR_PAT_SPAN` reads `IR_LIT(bb).ival == 1` (IR_interp.c:4300)
- `IR_PAT_ANY` / `BREAK` / `BREAKX` / `NOTANY` read `dval == 1.0` (3599 / 4272 / 4389)
- SPAN must use `ival` (not `dval`) because **BREAKX already uses `ival == 1` for its regenerate state** (4286). So the cset variable-flag is split: **SPAN → `ival`**, the rest → **`dval`**.

## The fix (commit `1e3f30b`, 2 files)

1. `src/lower/lower_snobol4.c` — cset cases now mirror the integer family:
   - `TT_VAR`/`TT_KEYWORD` arg → `IR_LIT(nd).sval = arg->v.sval` + flag (`ival=1` for SPAN; `dval=1.0` for ANY/BREAK/BREAKX/NOTANY).
   - literal arg → `IR_LIT(nd).sval = arg->v.sval` — **byte-identical to before**.
2. `src/emitter/emit_bb.c` — `scan_pat_m3_native_safe` gains two lines so **variable**-cset scans defer to `rt_scan` in M3 (which runs the now-correct interpreter), exactly as the integer family does:
   ```c
   if ((nd->op==IR_PAT_ANY||IR_PAT_NOTANY||IR_PAT_BREAK||IR_PAT_BREAKX) && IR_LIT(nd).dval != 0.0) return 0;
   if (nd->op==IR_PAT_SPAN && IR_LIT(nd).ival == 1) return 0;
   ```

**Why it's safe:** literal csets are provably byte-identical (the else-branch is unchanged, the guard only re-routes *variable* shapes), so no literal-cset regression is structurally possible. The only behavioral change is variable csets — which were broken.

## Semantics validated against sbl (important — it kills the obvious shortcut)

- **IMMEDIATE** `ANY(a)` binds at the match line (which *is* construction time for immediate): `a="xyz"; a="abc"; "bcz" ? ANY(a).C` → `b` in **M2 == M3 == sbl** ✓. My fix is correct here.
- **STORED** `P = ANY(a)` binds at **construction time**: `a="xyz"; P=ANY(a); a="abc"; "bcz" ? P.C` → sbl **`z`** (old set `{x,y,z}`), not `b`.

Consequence: a stored-pattern cset must be **evaluated-and-baked at runtime construction**, *not* looked up by name at match time. Doing the stored case the quick name+flag way would silently return `b` (stale binding) and could **pass the corpus while diverging from sbl**. Do not do it.

## Gates & probes at handoff

- smoke 7/7/7 · pat-rung 19/19/19 no-SKIP · fence TIER1=0 TIER2=0
- corpus **M2 182→186 (+4) · M3 169→171 (+2) · M4 166 (held) · SKIP 8 (=)**, zero regress any mode
- probes now M2==M3==sbl: `SPAN(digits).N` (2 / 42), `POS(0) SPAN(d) RPOS(0)`→consumed-all, `ANY(s).C`→x, `BREAK(b).C`→ab, `BREAKX(s).C`→ab, `ANY(&UCASE).C`→H
- **065** (single-var cset) M2/M3 now correct; M4 still link-fails `xcat15_right_β`
- **064** still fails all modes — different cause (computed-concat arg, below)

---

## NEXT — three rungs, all converging on construction-time value-chain-into-ζ (the genuine S2/PB-RB-5 build-out; fresh budget)

1. **STORED single-var cset** (`P = ANY(var)`). Builder `sno_build_leaf_ir` (lower_snobol4.c:526-532) builds a native `IR_PATTERN_*` node **only** when the arg is `TT_QLIT`; a `TT_VAR` arg falls through (`return NULL`) → the stored pattern uses the deferred runtime-construction path, which still has the bug. Fix must **evaluate-and-bake the cset at runtime construction** (per the validated construction-time binding), feeding the `IR_PATTERN_*` node — not a match-time name lookup. Touches the pattern-OBJECT path (every stored pattern) → land with the **full gate suite** as the net.
2. **COMPUTED-CONCAT cset** (`ANY(a b)`, `ANY(&UCASE &LCASE)` = what fails **064**). Lower the cset-arg expression into the value chain, evaluate at the right time, bake. Spans immediate + stored, M2/M3/M4.
3. **M4 native late-read + ALT cat-arm β** (`xcat15_right_β`). The native template `bb_pattern_unary_s` seals a compile-time literal cset slot; it needs ζ late-read for variable/computed csets, plus the `flat_drive_capture` diamond-collapse/β back-wire for the ALT form (the prior watermark's item — real, but only the M4-ALT slice). Closes 064/065 in M4.

Then the standing ladder continues: drop FENCE(P)-seal from `scan_pat_m3_native_safe` (M3 FENCE(P) native) → B9 ARBNO native → B10 defer/star-var → S1 subject → S5 replacement → S6 DELETE rt_scan → cut #3 alloc-registry + poison-bomb.

## Files touched this session
- `SCRIP/src/lower/lower_snobol4.c`
- `SCRIP/src/emitter/emit_bb.c`
- `.github/GOAL-SNOBOL4-BB.md` (watermark + M4-FENCE bullet correction)
- `.github/HANDOFF-2026-06-14-OPUS48-SNOBOL4-BB-CSET-OPERAND-VARIANCE-SINGLE-VAR.md` (this file)

## Manual references consulted
SPITBOL manual Ch.9 p.124-126 (FENCE/ABORT/FAIL/SUCCEED primitives) and Ch.19 (FENCE(P), SPAN/ANY/BREAK/NOTANY/BREAKX cset matchers). Construction-time vs match-time binding confirmed empirically against the x64 sbl oracle (not stated explicitly in-manual).
