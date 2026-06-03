# HANDOFF 2026-06-03 — Claude Opus — ICON-BB: native `IR_ALT` generator (`bb_alt`)

**Goal:** GOAL-ICON-BB.md — the two "big boxes" `IR_ALT` and `IR_GEN_SCAN`.
**SCRIP HEAD:** `eca2dcb` (local == origin/main, clean, rebased on peer `1b4e0fe` Pascal PB-8).
**.github HEAD:** this commit.

---

## One-line summary

`every write(1|2|3)` and `every write("a"|"b"|"c")` now run **m2 == m3 == m4**. The native
`IR_ALT` alternation generator (`bb_alt.cpp`) is live — a stackless counter-driven generator
mirroring `bb_to`. `IR_ALT` removed from `icn_kind_native_stub`; emittability precisely gated so
nested/multi-feature alt programs cleanly EXCISE instead of miscompiling. m3/m4 corpus PASS 10→12.

---

## The reuse question (answered, grounded)

Lon asked: "IR_ALT and IR_GEN_SCAN are already done for SNOBOL4 — are they identical? Can you
reuse ALL the SNOBOL4 pattern BB?" The honest, code-checked answer:

- **Shared (infrastructure):** Icon `IR_ALT`, SNOBOL4 `IR_PAT_ALT`, Prolog `IR_DISJ` all lower
  through the SAME `wire_alt()` in `lower.c` (same port topology, matches canonical `ir_a_Alt` in
  `refs/jcon-master/tran/irgen.icn` — all arms share one `target`, success→alt-success,
  failure→next-arm). The fan-out emitter (`x86_pair_loop` / `EMIT_PAIR_*`) is common code.
- **NOT identical (leaf):** Icon alt arms produce VALUES into a shared slot; SNOBOL4 pattern-alt
  arms thread a CURSOR. So `bb_pat_alt` is NOT drop-in. I wrote a purpose-built `bb_alt` that reuses
  the generator-β re-pump edge + the `bb_to` slot pattern (genuine infrastructure reuse).
- **IR_GEN_SCAN (next): same lesson, stronger.** `refs/icon-master/src/runtime/fstranl.r` proves
  Icon scanning funcs RETURN positions and `upto`/`find`/`bal` are GENERATORS (`function{*}`),
  unlike SNOBOL pattern leaves. Reuse the cset-scan inner loops + Σ/δ/Δ registers; write Icon
  value-return wrappers + generator re-pump for the `{*}` ones. Details in the Watermark's NEXT.

## What landed (SCRIP `eca2dcb`)

`src/emitter/BB_templates/bb_alt.cpp` (NEW)
- Counter-driven generator. Arms read from `operand_aux`; each arm constant sealed RO
  (`x86_ro_seal_q`/`_str`, internal idx 0..n-1); frame counter at `[r12+op_off+16]` indexes arms
  (`cmp`/`je L(n+1+i)`), loads `arm[i]` DESCR into SHARED result slot `[r12+op_off]`, `inc`, `jmp γ`;
  β → dispatch label `L(n)`. Pure `x86()`, zero stack, zero raw-byte producers (FACT-clean).
  ≤5 arms, `IR_LIT_I`/`IR_LIT_S` only.

`src/emitter/emit_core.c` — `case IR_ALT: bb_alt(nd)`.

`src/emitter/emit_bb.c`
- `flat_drive_alt_icn_gen` (descr-flat-chain `IR_ALT` arm; allocs result+counter slot, sets `g_emit.node`).
- `ir_node_is_alt_arm` / `ir_skip_alt_arms` — chain BFS redirects entry past bare arms and skips them
  (subsumed by `bb_alt`; must not be emitted as standalone lit boxes).
- `IR_ALT` arity-0 in `descr_chain_arity` (consumer resolves its operand slot to the alt node).
- `flat_drive_gen_alt` kept for the SNOBOL/gvar path (the `else` arm).

`src/driver/scrip.c`
- `IR_ALT` removed from `icn_kind_native_stub`.
- `g_emit_cfg` set at the 4 ICN build sites (proc/main × text/binary) — was NULL on the ICN path;
  `bb_operand_aux_get` needs it to read the arms.
- `icn_graph_native_emittable` precisely gated: a graph with any `IR_ALT` emits ONLY if every node
  is in the safe generator set (IR_ALT/CALL/EVERY/FAIL/SUCCEED/LIT_I/S/F/NUL) AND each alt's arms are
  ≤5 simple literals. Nested-alt + alt-plus-other-construct cleanly EXCISE (loud, never silent).

`Makefile` — `bb_alt.cpp` in source list + compile rule.

## Gates at handoff (all green)

- m2 corpus **130 (HARD)** · Icon smoke m2 **12/12 (HARD)** · Prolog smoke m2 **5/5 (HARD)** · unified-broker **32**
- m3/m4 corpus PASS **10 → 12** · EXCISED **37 → 45** (symmetric m3==m4) · FAIL **190** unchanged (no new silent fails)
- All 10 baseline m3 passes intact (verified by stash/compare)
- bb_bin_t=0 · no-handencoded `--strict` OK · g_vstack=0 · no-stack 10≤127 · one-reg-frame 0≤21
  · prove_lower2 PASS · FACT (bytes outside templates)=0
- Verified m2==m3==m4: `1|2|3`, `"a"|"b"|"c"`, `10|20`, `1|2|3|4|5`, `1|"x"|3`
- Verified clean EXCISE (no miscompile): `("a"|"b")||("x"|"y")` (nested alt)

## NEXT (recommended)

**`IR_GEN_SCAN`** — the larger of the two big boxes, 27 corpus programs. Read `fscan.r` (scan
environment / `&subject`/`&pos`) and `fstranl.r` (each primitive) FIRST. Build non-generator
`any`/`match`/`many` value-wrappers first (reuse cset matchers in `bb_pat_span`/`any`/`break`), gate
with the same precise-shape discipline as alt, then the `{*}` generators (`upto`/`find`/`bal`) using
the `bb_alt`/`bb_to` re-pump. Also open: `bb_binop_gen` (Fig-1), `!x`, relop/control tiers, GZ-DEFER.

**Systemic note (pre-existing, not this commit):** ~150 corpus programs abort (rc=-6/-11) in
`walk_bb_node` rather than EXCISING — `icn_graph_native_emittable` is too permissive for
`IR_IF`/`IR_RETURN`/`IR_CONJ`/generator-`IR_BINOP`. A decline-gate pass would make the harness FAIL
bucket reflect real miscompiles, not loud aborts.

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git  /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
# canonical sources: unzip uploaded icon-master.zip / jcon-master.zip into refs/
bash scripts/test_smoke_icon.sh        # m2 12/12 HARD; m3/m4 5/12
bash scripts/test_icon_rung_suite.sh   # interp 130 HARD; run/compile 12 PASS, 45 EXCISED
```
