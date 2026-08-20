# FINDING s168 (HQ, Fable 5) — B1c ROOT CAUSE, CURED IN M3: D-18b's blanket fragment TINY-decline is OVER-BROAD post-D-18a; the slim/legacy fallback's pushed-landing protocol mismatches the callee's exit protocol (rsp climbs past the stack top / dead-wire pc=0x1)

**Front:** GOAL-SNOBOL4-100 · M1 beauty self-host · wall B1c. Build: pristine SCRIP `25d8970c` + this fix, `-O0`. Oracle `x64/bin/sbl`. Continues FINDING-2026-08-19-s164 (which ruled out `jmp_entry`-alone and `g_flat_frame_floor`-alone).

## The mechanism (asm-diff proven, gdb receipts)
1. **Main-built** EXPR$ thunks call a deferred target through the **staged record protocol** (m4 text, `m_plain.s` n1_call): `lea rcx,[rip+sig-record]; jmp target_α` — NO stack pushes; the sig record's quads carry both continuations; the landing discriminates success/fail by sentinel (`cmp eax,104`).
2. **Fragment-built** thunks (runtime_eval.c `eval_thunks_emit_from`) hit `bb_call_proc_staged`'s D-18b consult (`g_rt_fragment_emit=1` ⇒ DECLINE TINY) and fall to the **slim/legacy call**: TWO landing cells PUSHED + γ/ω in r10/r11 + `jmp *rax`. The callee never consumes the pushed cells under the record/wire regimes main bodies actually use, so each match round leaks +0x10 of stack upward; on retreat loops **rsp climbs past the stack VMA top** (measured: fault at thunk+0xaf, `mov (%rsp),%rax`, rsp=0x7ffffffff000). Entered without `jmp_entry`, the same body instead ran its sub/wire prologue on garbage rcx/rdx and jumped a dead wire — **the s164 `pc=0x1`** (rt.c:899's own comment describes this crash verbatim).
3. **D-18b's justification is obsolete**: it declined because fragment callees "carry no <name>_α staging label / alpha$ MISS" — but D-18a (same session) added `bb_ab_seal_entry_cells` to the fragment loop, so every fragment proc's alpha$ cell IS sealed, and cross-chain main callees were always sealed by the driver.

## The fix (killswitch `SCRIP_B1C_PARITY`, **LANDED DEFAULT OFF** — behavior-neutral commit; `=1` arms the cure; the `b1c-flip` seat owns the A/B + default flip per Lon's s168 ruling: HQ finds, seats fix)
- `src/templates/bb_call_proc_staged.cpp` (both TINY sites, ZD + non-ZD): decline now only when `g_rt_fragment_emit && !SCRIP_B1C_PARITY`. Main emission truth-table-identical (`g_rt_fragment_emit=0` ⇒ condition unchanged), so mode-4 `.s` output is byte-identical by construction.
- `src/runtime/runtime_eval.c` fragment loop brought to driver parity: `rt_proc_set_jmpentry` (necessary: moves entry to the wire regime — measured, crash site moved), SN4-FLAT-PROC floor, PL-DC arming, and the post-emit registrations `rt_proc_set_frame_bytes` / `rt_proc_set_zstatic` / `emit_patzeta_register` / `rt_proc_set_dcfn` (scrip.c:1664–1686 twins).
- **RULED OUT by asm-diff:** emitting the fragment body from `proc_entry_node` (bb_proc_entry) — it drops the thunk's entry prologue (0x70 carve + rcx/rdx wire save) and the body falls into slab zeros; fragment graphs are self-owned, never main-shared, so the s176 shared-graph rationale does not apply. Reverted in-tree with a comment.

## Receipts (minimal pair from s164, `e_plain` = `P = EVAL("'x' *PC()")`)
| witness | before (both arms) | after, ON | after, `=0` |
|---|---|---|---|
| e_plain m3 | SEGV pc=0x1 after body | **PASS** (`PC ran / match`, oracle-identical) | SEGV (legacy reproduced) |
| b1c_cross_medium_concat_seam m3 | SEGV | **PASS** | SEGV |
| b1c_eval_fn_pattern_retreat m3 | SEGV | runs clean, **`match` vs oracle `nomatch`** | SEGV |
| b1c_patvalued_formal_retreat m3 | SEGV | runs clean, `match` vs `nomatch` | SEGV |
| b1_eval_pattern_defer_call m3 | SEGV | runs clean, `match` vs `nomatch` | SEGV |
| all five, m4 | SEGV after body | **still SEGV** (residue R1) | SEGV |

## Beauty movement (the point of all this)
- **m3 self-input** (`./scrip beauty.sno < beauty.sno`): emits its 7-line header **byte-correct against the input**, then SEGV — deepest m3 watermark yet; suspect B2c (the named m3 carve-zeroing wall), not B1c.
- **m4 self-input**: **NO CRASH for the first time** (rc=0) — the Shift/Reduce machine RUNS, echoes `START`, then clean `Parse Error` on input line 2 (`-INCLUDE …`) — the documented F-path symptom of residue R1.

## Residues, named
- **R1 (m4 seam remains):** hypothesis — in an m4 process the fragment's TINY admission (`bb_tiny_shim_ok`/`bb_scc_probe`) consults emit-side proc knowledge that only exists in-process at m3 (`g_stage2` holds only fragment procs at m4 runtime), so calls to main-program callees still decline to slim/legacy. Next: diag the admission verdicts inside an m4 process, then either admit via runtime-registered facts or fix the slim/legacy landing protocol itself.
- **R2 (m3 retreat wrong-answer):** three `*_retreat` witnesses now run clean but report `match` where SPITBOL retreats to `nomatch` — the deferred call's failure is not propagating as pattern retreat through the staged sentinel path in fragment context.
- **R3:** corpus A/B (ON vs `=0`) gate owed before the landing verdict — this FINDING precedes the commit; the A/B table lands in the cursor with the push.
