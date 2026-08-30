# FINDING 2026-08-30 (ceo) — N-2: the legacy zframe/FR generator machinery is deleted (DONE-WHEN clause 1 met, byte-identical across three witness shapes); D2 ALL-GREEN at REPS=20 both modes; the umbrella's 9 remaining rung reds each decomposed to a named owning row

Row `icon-n2-generator-activation-frames` (ceo, resumed via `next`).

## Measured first, worked second

- **Armed D2 witness set: ALL-GREEN, 9/9 witnesses CORRECT, REPS=20, BOTH modes, 0 crashes in 360 runs** — suspend_single/multi/loop/nested/after/scan/apply + ctl_return/ctl_every. The harness's own verdict line: "the gate may flip." Tree 41730a7f.
- The regime default is **already ON** (`icn_genframe2()` defaults 1; `SCRIP_ICN_GENFRAME2=0` survives only as the killswitch; the Icon-only key `icn_cells_graph` guards the s283f prolog-regression class).
- The fifth census class the GOAL said awaits Lon is **LANDED AND GRANTED** — `test_gate_icn_rbp_census_ratchet.sh:60` cites "Lon grant 2026-08-29"; measured this sitting: drift=0, C_data=0 zero-assert holds, E_activation=961 == pinned baseline, gate GREEN. The AWAITING-LON prose in GOAL-ICON-100/the task GOAL is stale; nobody should re-ask.

## The deletion (the GOAL's own clause, executed)

The whole legacy generator side-table machinery was reachable **only under `SCRIP_ICN_LEGACY=1`** — lower_icon.c set `icn_cells_graph = 1` unconditionally otherwise, `zframe_graph` was set only for `!icn_cells_graph` Icon graphs, and `icn_zframe_gen` only for generators on such graphs. Dead by construction in every default build. Deleted in one commit: rt.c's `g_gen_pending_*` four shadow globals + the `icn_gen_state_t` stack + `rt_gen_save_wires/save_cont/get_cont/get_gamma_wire/get_omega_wire/get_fb` (77 lines); xa_flat's FR-5 epilogue-γ/ω and save-wires arms; bb_suspend/bb_return cont-save arms; bb_call_proc_staged's four constant-false `zf_resume` sites (the Prolog `pl_zf_resume` path preserved with identical emission); emit.cpp's SUSPEND stage latch and `_zk3` LEGACY env read; scrip.c's `_icn_zframe_gen` read; the `IR_t.icn_zframe_gen` field; `zls_g_icn_zframe_gen_by_name`; and the `SCRIP_ICN_LEGACY` / `SCRIP_ICN_CELLS` / `SCRIP_ICN_ZFRAME` switches — the same experiment-residue class as the same-day define purge. `grep g_gen_pending_cont src/runtime/rt/rt.c` = 0: **the row's DONE-WHEN first clause is met.**

**Honesty arms:** (a) stash-A/B on exactly this diff — `generators.icn`, `rung36_jcon_genqueen.icn` (suspend host), `sendmore.pl` (Prolog zf) all **byte-identical across the deletion**; (b) pristine floor receipts in the landing commit. ⚠️ Method note: `tests/icon/generators.s` looked like a free control arm and is NOT one — it is a stale abolished-class artifact the artifact sweep missed (the sweep was keyed on pre-re-grid names), predating the N-2 landings. Committed test-tree `.s` files must never be used as control arms; RULES.md:113 abolished them for exactly this reason.

## The umbrella's remaining reds, decomposed by measurement (rung board FAIL=9 · BADEXIT=1 · MISSING=0; bar is ≤5/≤1/0)

Each failing rung was run by hand and its failure shape attributed:

| rung | shape | owner |
|---|---|---|
| level | prints 1/1 for 1/2 — &level entry-side increment pending (exit half landed, SCRIP 41730a7f) | seat01, implementation-ready |
| genqueen | loud GENHOST refusal: recursive generator callee — refused BY DESIGN pending per-activation storage | row icon-n2-recursive-generator-per-activation-storage (seat08) |
| recogn | same designed refusal (mutually recursive states); its `.stdin` IS fed by the harness — red is real, not stdin-shaped | same row (seat08) |
| scan, scan2 | generators inside scan envs yield first results only (missing resume sequences in deep diff) | N-3 icon-n3-scan-one-depth-authority |
| cxprimes | coexpr NULL-activate rc=134 | coexpr lane (seat06 family) |
| var | emit_drive IR_ASSIGN guard refusal (nameless 2-operand assign) | emitter lane |
| args | variadic/apply args not delivered (p1..p7 lose their args) | apply/varargs lane |
| proto | BADEXIT only, stdout correct: parse error on unary `^x` (coexpr refresh) at line 47 | icon parser gap |

Plus one stale marker promoted on the harness's own instruction: `rung36_jcon_every.xfail` removed (was XPASS).

**Conclusion:** the N-2 umbrella has zero unknown work left — it closes arithmetically as seat01's and seat08's rows land, or ceo re-cuts the ≤5 bar against this decomposition (the pascal-restore-prezeta named-exceptions pattern). The re-cut is flagged, not taken unilaterally.
