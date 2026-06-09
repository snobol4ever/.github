# HANDOFF 2026-06-06 — Opus 4.8 — ICON-BB ICN-VAR-3: SCAN-13b adoption — var-subject scans + GEN_SCAN slot adoption

## What landed (one gated rung)

**ICN-VAR-3** — the deferred SCAN-13b slice: local-var scan subjects admitted, GEN_SCAN made a value
producer any chain consumer reads. Probe `s := "hello"; s ?:= tab(3); write(s)` → `he` **m2==m3==m4**.
Corpus m3 **22→25**, m4 **32→35** (flips: `rung05_scan_scan_{var,nested,restores}` ×2 modes — nested
var-subject scans lit up too), **all EXCISED→PASS, zero →FAIL**; m2 **129 HARD byte-identical**.
Diff: `src/driver/scrip.c` + `src/emitter/emit_bb.c` + `scripts/test_gate_icn_scan.sh` — template-free.

## The discovery that shaped the rung

`descr_chain_arity` returned **-1 for IR_GEN_SCAN** — the RPN resolver RESET its stack and never pushed
the scan, so a chain consumer (`write(s ? tab(4))`) got no α → `op_a_slot=-1` → the generic `bb_call`
→ the abolished `rt_call_builtin` **runtime bomb**. The bomb pre-existed at HEAD for literal subjects
too (`write("world" ? tab(4))` aborted rc=134 — masked in the corpus FAIL bucket). The rung-probe shape
only worked because the lowerer pre-wires `ASSIGN.α=GEN_SCAN` directly. The fix is the goal file's own
phrase made literal: **`case IR_GEN_SCAN: return 0;`** — an arity-0 slot producer. That one line plus
the slot adoption repaired the pre-existing lit-subject bomb as a side effect.

## Changes

`src/emitter/emit_bb.c`:
- `flat_drive_gen_scan`: after the body subchain emits, slotmap-aliases the GEN_SCAN node to
  `bb_slot_get(descr_chain_terminal(body_sg->entry))` (guarded: body slot ≥ 0, node not yet mapped).
  Zero instruction bytes — driver bookkeeping only; canonical per `ir_a_Scan` (`?` op: rv := target —
  the scan's value IS the body's value).
- `descr_chain_arity`: `IR_GEN_SCAN → 0` (was default -1 / stack reset).

`src/driver/scrip.c` (admission):
- `icn_scan_subgraph_safe(s2, gi, g, sg, depth)`: admits non-`&` local `IR_VAR` **only when
  assigned-or-param in the parent graph** (`icn_graph_var_assigned_or_param`) — subgraph vars escape
  the main-graph line-244 check because `lower_value_subgraph` blocks are standalone unregistered
  graphs (verified); `state==1` NV-globals stay rejected (no subgraph read arm).
- `icn_assign_safe_kind` += `IR_GEN_SCAN`.
- New `icn_gen_scan_body_slotful()` — body chain terminal ∈ {LIT_I, LIT_S, local VAR, CALL to
  tab/move/pos/any/match/many/upto/find/bal} — used by `icn_local_assign_rhs_ok` (GEN_SCAN rhs) AND
  by a new consumer-side fence: `GEN_SCAN.γ == IR_CALL` requires the lens (kills the
  slotless-body-consumed bomb class, e.g. `write(s ? write(...))`, with a clean EXCISE).

`scripts/test_gate_icn_scan.sh`:
- `augop_scan` / `augop_scan_fail` promoted **X34 → STRICT** (the X34 header doc literally named
  "the SCAN-13b bb_var deferral"; the deferral is lifted, so the pin is lifted with it).
- Bucket ratchet floors m3/m4 **7 → 11**. Header annotation updated.

## Gates (all green)

Probes: rung probe + `?:=move` + `write(var ? tab)` + `write(lit ? tab)` + statement scans —
three-mode agreement; unassigned-subject EXCISEs rc=0. Corpus stash/set-diff vs **verified** baseline
(the VAR-2 lesson applied: baseline binary confirmed to EXCISE the rung probe BEFORE its sweep;
baseline columns matched the VAR-2 watermark exactly): m2 129 HARD · m3 22P+82F+143E→25P+82F+140E ·
m4 32P+136F+79E→35P+136F+76E. Scan fence **GATE: PASS** (probes 28/28; bucket m3=m4=11 at the new
floors; `scan_simple`/`scan_var` FAIL=2 confirmed **pre-existing at baseline** — both have empty
`.expected` files, m2 FAILs them too). Smoke Icon 12/12 · 10/12 · 10/12 (remaining 2 = userproc lane,
standing flag) · Prolog 5/5 · broker 32 · bb_bin_t 0 · handencoded `--strict` 0 · icn_no_stack 0 ·
one-reg-frame 0 · g_vstack 3 (pre-existing rt.c/rt.h) · prove_lower2 PASS · medium-invisible 347
(unchanged — diff is template-free).

## Next

**ICN-VAR-AUGOP-PREREQ** — the `x +:= e → x := x + e` lowerer desugar (Rebus `rebus_lower.c`
precedent; SCAN-13a's AUGOP_SCAN arm at lower_value is the in-file pattern to extend); the 11 fenced
m4 augop/swap programs (rung10/11/15/36/37) are its ready probe set. Then **ICN-VAR-FENCE**.
