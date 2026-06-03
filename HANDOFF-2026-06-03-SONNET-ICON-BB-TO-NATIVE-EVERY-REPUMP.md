# HANDOFF 2026-06-03 — Claude Sonnet — ICON-BB: native `to`/`to_by` + `every` re-pump

**Goal:** GOAL-ICON-BB.md — finish the ICN-HY-4 `bb_to` rung (it was STAGED-DORMANT at `8570c97`).
**SCRIP HEAD:** `b48f0cd` (local == origin/main, clean)
**.github HEAD:** this commit

---

## One-line summary

`every write(1 to N)` and `every write(1 to N by k)` now run **m2 == m3 == m4**. The
staged-dormant `bb_to` generator template is LIVE; `IR_TO`/`IR_TO_BY` removed from
`icn_kind_native_stub`. The blocker was the `every`→generator re-pump back-edge; fixed in
three layers (lowerer wiring flag, chain-walker resume resolution, bodyless-every landing pad).

---

## The bug (verified, three layers)

`every write(1 to 3)` printed only `1` in m3/m4 (silent miscompile) when `IR_TO` was un-stubbed.
Root cause was three distinct things, all required:

1. **`g_icn_postfix_resume` was `--interp`-only.** It is the flag that makes the SHARED lowerer
   (`lower.c` icon call arm, ~line 1258: `call_resume = g_icn_postfix_resume ? aβ : ω_in`) wire
   `expr.success → generator.resume`. With it off (m3/m4), `write.γ → IR_EVERY`, so the generator
   pumped exactly once. **Confirmed by `--dump-bb`:** with the flag the write node's γ flips from
   `[2] IR_EVERY` to `[4] IR_TO` (the generator). Canonical authority: `ir_a_Every` in
   `refs/jcon-master/tran/irgen.icn` lines 325-330 — `p.expr.ir.success → p.body.ir.start`,
   `p.body.ir.{success,failure} → p.expr.ir.resume`; for bodyless every (`body = a_Key("fail")`)
   that collapses to `expr.success → expr.resume`.

2. **The chain walker resolved every `→γ` to the target's α (fresh) label.** A re-pump must land
   on the generator's **β (resume)** label, or `bb_to`'s α reseeds the cursor to `lo` and the loop
   never advances. Fix in `codegen_flat_chain_body`: a BACKWARD edge (`i > k`) into a generator
   node resolves to `betas[k]` not `lbls[k]`.

3. **The bodyless-`every` arm re-walked `pBB->α`,** double-emitting the operand chain (a stray
   second `IR_LIT_I(1)` was visible in the disassembly). Fixed: when α is already in the outer
   chain it is a success landing pad; re-walk kept only as the nested-every fallback.

## What landed (SCRIP `b48f0cd`)

`src/driver/scrip.c`
- Set `extern int g_icn_postfix_resume; if (is_icon) g_icn_postfix_resume = 1;` at the TOP of the
  `--run`, `--compile` (mode_compile_x86), and `--dump-bb` blocks — BEFORE `sm_preamble` (which
  runs the lowerer). Previously only `--interp` set it.
- Removed `IR_TO` / `IR_TO_BY` from `icn_kind_native_stub`.

`src/emitter/emit_bb.c`
- New `ir_is_generator_kind(IR_e t)` (kind-only mirror of `gen_bb_is_gen_arg`).
- New `g_flat_chain_set[]` + `flat_chain_set_has()`; populated from the BFS `nodes[]` in
  `codegen_flat_chain_body`; reset (`g_flat_chain_set_n = 0`) in BOTH `descr_flat_chain_build`
  and `descr_flat_chain_build_text`.
- `codegen_flat_chain_body` γ-resolution: `node_γ = (i > k && ir_is_generator_kind(nodes[k]->t)) ? betas[k] : lbls[k];`
- `flat_drive_every` bodyless `ival==0`: `if (flat_chain_set_has(pBB->α))` → EMIT_PAIR_JMP(lbl_γ)
  landing pad; else the prior re-walk.

## Gates at handoff (all green)

- m2 corpus **130 (HARD)** · Icon smoke m2 **12/12 (HARD)** · Prolog smoke m2 **5/5 (HARD)**
- m3/m4 corpus PASS **6 → 10** · EXCISED **59 → 37** (symmetric m3==m4) — pure forward progress
- Icon smoke m3/m4 **4 → 5**
- bb_bin_t=0 · no-handencoded `--strict` OK · g_vstack=0 · no-stack 10≤127 · one-reg-frame 0≤21
  · prove_lower2 PASS · FACT (bytes outside templates)=0 · unified-broker PASS 27 (unchanged)
- Rebased cleanly onto peer `00ef311` (Raku RK-NFA-2) and `d1e881b` (Pascal PB-7) — orthogonal;
  m2 HARD re-verified after the rebase + rebuild.

## NEXT (recommended)

**`bb_binop_gen` cross-product (Proebsting Fig-1)** — `every write(N < (1 to A)*(1 to B))`. The
chain-walker now has the generator-β re-pump edge, so the inner-generator re-pump is likely
already handled; the work is the stackless cross-product template + removing `IR_BINOP_GEN` from
`icn_kind_native_stub` + confirming `icn_graph_native_emittable` admits nested-`IR_TO`-operand
graphs. Read `ir_a_Sectionop` / `ir_a_Binop` in `refs/jcon-master/tran/irgen.icn` FIRST
(CONSULT-CANONICAL-SOURCES). `IR_ALT` would benefit from the same edge. Then the unchanged open
tiers: native `!x`, the relop tiers (`bb_var` operand-slot gap), `rt_call_builtin`, GZ-DEFER.

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git  /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh        # m2 12/12 HARD; m3/m4 5/12
bash scripts/test_icon_rung_suite.sh   # interp 130 HARD; run/compile 10 PASS, 37 EXCISED
# canonical sources: unzip the uploaded icon-master.zip / jcon-master.zip into refs/
```
