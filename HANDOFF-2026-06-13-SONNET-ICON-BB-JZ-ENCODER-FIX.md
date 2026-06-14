# HANDOFF 2026-06-13 — Sonnet — Icon m3 `jz`/`js` encoder fix (BINARY-vs-TEXT divergence)

**Author:** Claude Sonnet (with Lon Jones Cherryholmes · Jeffrey Cooper M.D.)
**Goal:** GOAL-ICON-FULL-PASS — get modes 3 and 4 working (mode 2 left as the oracle).
**SCRIP HEAD pushed:** `521ab64` (rebased over concurrent Prolog/SNOBOL4/Raku landings).

## What landed

One-file fix to `src/emitter/BB_templates/x86_asm.h` (`x86_jcc_op`). **m3 76→82 (+6), now at parity with m4.**

### Root cause
`x86_jcc_op(mnem)` mapped only `je/jne/jl/jge/jle/jg` and fell through to `return 0x85` (JNZ) for
everything else. There was **no `"jz"` case**, so in the in-process BINARY medium `x86("jz",…)` emitted
`0F 85` = **JNZ — the inverted condition**. The TEXT medium emits the literal mnemonic string `" jz …"`,
which GAS assembles correctly as JZ. So the two media diverged — a direct ONE-MEDIUM-INVISIBLE violation.

The visible victim was the string-relop arm of `bb_binop_relop` (`call rt_jct_relop; test eax,eax; jz ω`):
rung12 seq/sge/slt/sne + rung37 str_relop/strrelop_hello (6 programs) ran **inverted in m3 only**. m4 was
already correct, which is exactly why the suite showed m4 six ahead of m3.

`js` (1 use) had the same latent bug (silent 0x85 instead of 0x88). `jnz` (5 uses) was accidentally correct
because the silent default happened to be 0x85.

### Fix
Completed the standard Jcc opcode table (`jz/jnz/js/jns/jb/jae/jbe/ja` + signed aliases
`jnae/jnb/jna/jnbe/jnge/jnl/jng/jnle`) and replaced the silent `return 0x85` default with a **loud
`abort()`** carrying the offending mnemonic, so any future missing condition code fails at emit time rather
than mis-encoding into JNZ.

## Diagnosis method (reusable for future BINARY-vs-TEXT bugs)
1. `rt_jct_relop` was returning the CORRECT strcmp result in m3 (confirmed by env-gated instrumentation —
   reverted) — so the relop runtime was innocent.
2. Numeric relops use `cmp`+`jge/jne` (never `test`+`jz`) and PASSED m3 → isolated the fault to the
   `test eax,eax`/`jz` pair, which only the STRING arm emits.
3. `as --64` + `gcc -no-pie -lscrip_rt` on the mode-4 `.s`, then running the linked binary, produced the
   CORRECT output while m3 inverted → proved a BINARY-only encoder bug, not graph/logic.
4. Grepped `x86_jcc_op` → found the missing `jz` case and the silent default.

## Verification (all green, zero regressions)
- m2 **202** (HARD, unchanged) · m3 76→**82** · m4 **82** (unchanged — already correct)
- icon smoke 12/12/12 · prolog smoke 5/5/5
- `test_gate_icn_no_stack`=0 · `test_gate_icn_one_reg_frame`=0
- `test_gate_bb_one_box` 45 FAIL (PRE-EXISTING baseline, untouched)
- unified broker PASS=36 (≥35 floor)

## Leverage map captured for next sessions (m3 non-passing, excluding 102 EXCISED)
- 14 rc124 timeout — the EVERY-box retry cluster. The `bb_every` template is logic-empty; canonical
  `ir_a_Every` topology (start→expr; expr.γ→body; body.γ/ω→expr.β loop; expr.ω→ir.ω) is in
  `refs/jcon-master/tran/irgen.icn`. Architectural rebuild.
- ~26 rc134 bombs — real-arith (LIT_F operands unslotted at `descr_binop_opnd_slot`, emit_bb.c:1420; arith
  template int-only) and scattered per-builtin call shapes (read/find/detab/put/push, ≤2 each).
- EXCISED first-cause tally (from env-gated `ICN_EXCISE_WHY` probe, reverted): unsupported assignment-RHS
  ~41 (dominant — note `dval` on `IR_CALL` is a call-KIND tag, 3.0 = subgraph call, not arg count), ALT
  family ~29, GEN_SCAN subgraph 8, IR_CASE 4, unassigned-var ~16.

## Immediate NEXT (fully scoped in GOAL-ICON-FULL-PASS Watermark): native `IR_SWAP` for `:=:`
2 programs. Reuse `bb_assign_local` FRQ store idiom; 3 frame slots; semantics at IR_interp.c:2353. Five
implementation steps listed in the goal Watermark. Deferred only for context budget — it is a clean,
well-understood multi-file change, good to start fresh.

## Notes
- The ICON/JCON refs were extracted to `SCRIP/refs/{icon-master,jcon-master}` at session start.
- All debug instrumentation (env-gated `JCT_DBG` in `by_name_dispatch.c`, `ICN_EXCISE_WHY` in `scrip.c`)
  was reverted before commit — the pushed diff is the single `x86_asm.h` file.
