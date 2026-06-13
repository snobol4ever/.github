# HANDOFF 2026-06-13 · Opus 4.8 · SNOBOL4-BB — gvar UNOP/POW-as-operand (rung (a) closed)

**SCRIP HEAD:** db2ad0e (rebased onto concurrent d884849)
**.github HEAD:** (this commit)

---

## What this session did

Closed watermark rung **(a) BINOP/UNOP-AS-FLAT-CHAIN-OPERAND**, both halves. Two
commits, M3/M4-only (M2 was already correct on every probe). No new runtime calls.

**Baseline entering:** M2=182 M3=168 M4=157 · smoke 7/7/7 · pat-rung 19/19/19 · fence HARD
**Result:** M2=182(=) M3=168(=) M4=158(+1) · all gates HARD · ICON smoke 12/12/12

---

## Commit A — c0253bc · gvar UNOP-as-operand

**Root cause.** In the gvar flat chain (`g_gvar_flat_chain`), a `UNOP(NEG/POS)` never
produced a slotted value — `bb_unop` is gated on `g_descr_flat_chain` (Icon's chain).
So `-1+3` = `ADD(UNOP(NEG,1), 3)`: the ADD's left operand had no slot, the standalone
arith-slot binop arm (`emit_bb.c ~2764`, which needs both operands LIT_I/VAR/slotted)
did not fire, the ADD fell to `flat_drive_binop_tree` (emits nothing in gvar), and the
ASSIGN bombed `op_a_slot==-1`. Separately, bare `OUTPUT=-X` hit `walk_bb_node`'s
IR_ASSIGN default (`kind=5 unhandled`, silently dropped) because `op_a` was `IR_UNOP`,
absent from the accepted-child list.

**Fix (language-blind; gvar bare-int slot convention, mirrors IR_BINOP_GVAR_ARITH_SLOT).**
Made UNOP a first-class slotted-value producer in the gvar chain, so the *existing*
arith-slot arm picks it up automatically:
- `IR.h` / `scrip_ir.c`: new kind `IR_UNOP_GVAR_SLOT` adjacent to IR_BINOP_GVAR_ARITH_SLOT.
- `bb_unop_gvar_slot.cpp` (new): NEG/POS from LIT_I / gvar (`rt_gvar_get_int`) / slot
  operand → `mov FRQ(op_off), rax` (bare int). One return/platform, IF() conditionals,
  real Greek ports, no MEDIUM_*, no raw bytes, one comment separator, zero blank lines.
- `bb_templates.h`: decl. `emit_core.c`: dispatch + add IR_UNOP to the gvar ASSIGN
  accepted-child list (line ~450).
- `emit_bb.c`: standalone gvar UNOP arm (the IR_UNOP case ~2922) routes
  NEG/POS(LIT_I|VAR|slot) → IR_UNOP_GVAR_SLOT; `flat_drive_gvar_assign_binop` now skips
  re-walking c0 when `bb_slot_get(c0) >= 0` (already walked standalone) and just emits
  the ASSIGN reading the slot.
- `bb_gvar_assign.cpp`: new IR_UNOP rhs arm reads bare-int slot → `rt_gvar_assign_int`
  (verbatim mirror of the IR_BINOP arm).

Probes (M2==M3==M4==sbl): `-1+3`=2, `3+-1`=2, `-2*-3`=6, `10--5`=15, `-1+-2+-3`=-6,
`-X+10`=3, `-X`=-7, `X+Y*2`=15.

---

## Commit B — db2ad0e · gvar POW-as-operand

Extends the **fused standalone-POW arm** (`emit_bb.c ~2727` — POW whose γ-successor is
the gvar ASSIGN; it emits `IR_BINOP_GVAR_ARITH` against the ASSIGN node = fused
eval+assign-to-gvar) and the `bb_binop_gvar_arith` POW template. All via existing
`POWER_fn` + `rt_gvar_assign_descr`.

Three fixes:
1. **const-fold UNOP(NEG/POS, LIT_I) operands → signed int** → `(-2)**3`=-8 (was
   `kind=7 unhandled`: POW with a UNOP base missed the int-int arm, fell to
   flat_drive_binop_tree → `binop_slot_kind(POW)`=IR_BINOP → walk_bb_node default).
2. **LIT_F operands → DT_R descr (tag + IEEE bits) passed to POWER_fn** → `2.0**8`=256.,
   `2**0.5`=1.41…, `3.4**2`=11.56 (was 0./kind=7). **Real bits carried in `bb_li`/`bb_ri`
   (int64) — they survive walk_bb_node's clobber of op_dval/op_a_dval. DO NOT use op_dval
   as a carrier across FILL/EMIT_PAIR_FILL** (the first cut did, got 0.).
3. **set `op_sval` on the fused arm** so `bb_fill_alpha` derives `op_parts_lbl[2]` →
   fixes the M4 `lea rdi,[rip + ??]` junk in the POW path (`2**8` M4 assembly was broken,
   pre-existing). This flipped `027_arith_exponent` M4 → the +1.

SPITBOL POW typing preserved (966bb35 POWER_fn convention): int**nonneg-int→int,
any-real-operand→real, int**neg-int→real.

Probes (M2==M3==M4==sbl): `2**8`=256, `(-2)**3`=-8, `2.0**8`=256.,
`2**0.5`=1.4142135623731, `9**0.5`=3., `3.4**2`=11.56, `2**-1`=0.5, `10**9`=1000000000,
`(-3)**2`=9.

---

## Gates at session end (verified post-rebase, before push)

- SNO smoke **7/7/7** HARD ✓
- pat-rung **19/19/19 no-SKIP** ✓
- fence **TIER1=0 TIER2=0** HARD ✓
- ICON smoke **12/12/12** ✓ (shared bb_binop_gvar_arith touch safe — Icon uses the
  descr chain, not this gvar POW arm)
- broad corpus **M2=182(=) M3=168(=) M4=158(+1)**, SKIP 25→24, zero regress any mode

Both new/touched templates language-blind (TT_MNS/TT_PLS are shared AST op-token
constants, like binop_slot_kind's BINOP_*), both-medium via x86().

---

## NEXT (do-not-re-derive)

- **(b) ADD-WITH-STRING coercion** — `''+''` / `''+1` / `1+''`. `flat_drive_binop_tree`
  → `binop_slot_kind` emits empty for a string-operand ADD, ASSIGN then `call rt_bomb;ud2`
  (no value slot), line dropped in M3 (literals.sno 13-15). SPITBOL (Ch.3 p.21): null
  string → 0 in arithmetic; null-string CONCAT returns the other operand UNCHANGED (no
  coerce). Needs a runtime-coerce slot path (slot templates only handle int/var). **M3/M4
  only — fits the ignore-M2 steer; recommended next.**
- **(c) 084 concat-with-CALL** — `S=S bump(2*J)`: `gvar_seq_flatten` can't flatten a call
  part → 'no parts' bomb; eval the call into a ζ-slot then concat.
- **(d) 091/092 array `A<i>` assign+access, 093 table** — M2 ALSO fails (all-mode; only
  ARRAY()/TABLE() create emitted, subscripts dropped). LOWER-PRIORITY under ignore-M2.
- **(e) 094/095 DATA field-set** — 095 field write not persisting (10|20|10 vs 99); 094
  M4 compile-abort. (Concurrent 2831781 const-folds const^const→IR_LIT_F but only in
  lower_icon.c — Icon, not SNOBOL4.)
- **(f)** bare `OUTPUT=&LCASE` cset-as-gvar-value aborts M3 at cset-print (pre-existing;
  no corpus test hits it).
- **(g)** `kw_read` lacks distinct 'alphabet'/'stno' rows — NV fallback; add exact-value
  rows if a test needs precise semantics.
