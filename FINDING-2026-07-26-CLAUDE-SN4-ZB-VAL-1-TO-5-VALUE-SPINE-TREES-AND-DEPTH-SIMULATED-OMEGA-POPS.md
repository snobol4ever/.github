# FINDING — ZB-VAL-1..5: the value spine reaches arbitrary arith trees with typed var leaves (s178, 2026-07-26)

**SCRIP commits:** `9ed464c8` (ZB-VAL-1/2/3) · `3098b016` (ZB-VAL-4) · `d87db590` (ZB-VAL-5) · `0c2c96d6` (feature artifacts).
**Corpus:** `bb5bd087` (benchmarks) · `fd7108fa` (demos).
**Watermark: m3 332/2 · m4 323/1 — WATERMARK-EXACT after EVERY rung** (test_case, omega_driver pre-existing).
icon 14/14×2 · prolog 5/5×3 · raku 17/17 · all-langs hello 6/6 ROWS_DRIFT=0 (run after each zeta_storage touch — the scan runs for every language's graphs).

## What landed (Lon directive: each BB allocates its RESULT if used + LOCALS if any, ONE instruction, offsets from RSP)

1. **ZB-VAL-1** — `assign(binop(lit,lit))`, ADD/SUB/MUL. Both lits get 16B fc cells; the binop fc arm reads
   lhs `[rsp+24]` / rhs `[rsp+8]` and performs the ONE-INSTRUCTION net allocation: `add rsp,16` = release both
   operand cells + carve its own RESULT cell, store `{DT_I,val}` at `[rsp+0/8]`. Registered binops SUPPRESS the
   imm fast path so values ride the spine as first-class cells. DIV/MOD decline (lean arm has no idiv fault path).
2. **ZB-VAL-2** — pair scan widened to STRING/REAL/CHARSET lits. Zero template change: the cell is a type-blind
   16B DESCR and all four `bb_lit_scalar` arms are `FRQ(op_off)`-relative, so the `x86_fc_hit` rebase serves them.
3. **ZB-VAL-3** — global-routed `IR_VAR` producers join the pair. Zero template change: `bb_var_global`'s
   conditional NV `DT_FAIL` exit is served by the EXISTING invert+pop+jmp omega synth. The registration gate
   MIRRORS the walk's routing predicate (`is_global && !graph_has_local`, write/writes builtins, `&` excluded)
   so registration ⇔ the one template with hook-served exits.
4. **ZB-VAL-4** — ARBITRARY arith trees over int-lit leaves. **The geometry is SHAPE-INVARIANT**: post-order
   emission makes every binop's operands the TOP TWO cells, so `[rsp+24]/[rsp+8]` + net `add rsp,16` are
   identical bytes whether operands are lit/lit, lit/result, or result/result (byte-verified in `(1+2)*(3+4)`:
   three binops, three structural roles, one geometry). The registrar proves the γ-chain IS the post-order walk;
   `fc_vtree_scan` is depth-capped at 24 (384B max rsp excursion).
5. **ZB-VAL-5** — GLOBAL-VAR leaves inside trees. Two problems solved at once:
   - **Types:** a var cell holds whatever the global holds, so the fc binop arm carries the flat arm's FULL
     structure reading from CELLS: DT_DATA→overload (`r9 = lea` into the DEEPER operand cell, which BECOMES the
     result cell after the top release — `rt_binop_overload` writes `*out` only on success, so a failed attempt
     leaves the cell intact for the generic reload), non-DT_I→generic `rt_num_arith`, else DT_I fast. Cells stay
     LIVE until each exit's net so rt paths can reload.
   - **Failure depth:** a fallible box's ω must release EVERY live statement cell. The registrar runs a depth
     SIMULATION (d = cells live before each node's α): a var leaf's own 16B rides the fc hook, wpop = d·16;
     a binop carves nothing at α so wpop = d·16 covers everything. Spent via the EXISTING BP-9 `op_wpop` arm
     inside the ω synth (`+=` at walk so the driver's trampoline ΣK composes). Byte-verified: `2*(X+3)-X` —
     inner add releases 48 (3 cells), mul/sub release 32. GVA-active var reads take the absolute-load arm
     (infallible, no synth); NV-path vars carry it.

**New encoder arm (R7):** `lea reg, XK_RSP32/64 → x86_reg_disp32_lea64(reg,"rsp",off)` — `x86_rd32_modrm`
already emitted the mandatory SIB for base low3==100; the fatal-abort placeholder (ZB-FC-1 silent-drop class)
is retired for rsp kinds. mod10+disp32 stays that family's uniform-shape convention.

## Two ZB-VAL-0 latents CLOSED
(a) Registration is now capacity-ATOMIC (`fc_vcap`, all-or-nothing per statement) — a partial quartet at the
array cap could grant a cell nobody releases. (b) The consumer gate now REQUIRES the `bb_assign_global` route —
a local-assign consumer has no release arm and would strand the carve (green today only because flat SNOBOL4
has no statement-level locals; Icon/Raku shapes were exposed).

## THE WALL — observed shape, not yet hit
The value spine ran five rungs with ZERO rbp dependency: offsets are rsp-relative and STATIC because the
compile-time depth simulation IS the sliding-offset tracking (true FORTH: runtime-variable depth never occurs
on a validated spine). The wall's existing outline, confirmed in source: the SPD-2 scanfail retry block does
**`rsp = rbp` ("post-carve frontier: every element grant sits below")** — pattern-scan RETRY already anchors
its frontier restore on rbp, exactly the ARBNO/FUNCTION territory Lon named. The spine will meet it when value
cells coexist with scan retries in one statement; the ω-merge-depth problem (one label, two arrival depths) is
the same wall seen from the failure side — currently fenced away by construction (registration proves single-
depth arrival).

## LATENT (noted, not chased)
- SCRIP `rt_num_arith` COERCES non-numeric strings to 0 where SPITBOL raises ERROR 001 ("addition left operand
  is not numeric") — PRE-EXISTING (flat path + stashed HEAD probed identical). The fc arm reproduces flat
  semantics bit-for-bit (this rung's contract). Consequence: the emitted DT_FAIL ω unwind is byte-verified but
  not runtime-exercisable from SNOBOL4 source today.
- Registered producers still receive their (now-unread) flat rbp slots — the diet is a later elision rung, same
  class as the s174 ASSIGN-result note.
- `x86("comment",…)` does not render in mode-4 `.s` output — cosmetic, noticed while probing.

## NEXT RUNG CANDIDATES
**ZB-VAL-6a CONCAT** (`bb_binop_concat_slot` on the spine — THE SNOBOL4 operation; rt call with cells live is
proven safe by v5) · **ZB-VAL-6b UNOP** (unary minus: one operand cell, net ZERO — release 16 + carve 16 =
rsp untouched, store negated in place) · **ZB-VAL-7 relops** (`IR_BINOP_TEST` — zero-or-one-result, ω at depth) ·
then the DIET (elide registered producers' flat slots).
