# RATIONALE-INDEX — symbol/function -> recovered design rationale

**What this is.** `e25a5daf` (2026-08-20, GOAL-STYLE-200COL REACTIVATION 4) stripped 6,919 comments across 162 files enforcing the C style rule (RULES.md: 200-char lines, zero blank lines, exactly one comment form). Most of that was decoration; a real fraction was the project's hardest-won measured rationale — the only record of *why* a piece of code refuses the case it refuses. RULES.md's comment restriction is not being relitigated (do not put prose back in the source); this index is the promised alternative home: an "indexed appendix" mapping a symbol name to wherever its rationale now lives, so a session grep on the *symbol* finds the doc instead of needing to know a doc exists first. See `.github/FINDING-2026-08-22-recover-stripped-design-rationale-classification.md` for the recovery methodology and counts.

**How to use this file.** Looking for "why does X do Y": `grep -n "^- \`X\`" .github/RATIONALE-INDEX.md`. Adding a new relocation: append one line per symbol it covers, pointing at the doc (ARCH file, FINDING, or this file's own inline section for something too small to deserve a standalone doc).

## Index

- `sn4_blob_choice_scan` -> `.github/ARCH-ENGINE.md` §3.2
- `resume_carrier_ok` -> `.github/ARCH-ENGINE.md` §3.3 (the seat04 cluster: tier-3 admission, `lf`/`fn`/`nc` witnesses)
- `blob_choice_rbp_scan` -> `.github/ARCH-ENGINE.md` §3.4
- `sn4_choice_rbp_off` -> `.github/ARCH-ENGINE.md` §3.4
- `sn4_alt_carrier` -> `.github/ARCH-ENGINE.md` §3.1
- `blob_frame_bytes` -> `.github/ARCH-ENGINE.md` §3.5
- `zdp_tier` / ZDP lattice (`zeta_depth.c`/`.h`) -> `.github/ARCH-ENGINE.md` §3.6 (⛔ verified NOT the live admission path for the choice-carrier decisions as of the recovery commit — re-verify before trusting either way)

### `src/templates/x86/x86_asm.h` — the sole `x86(...)` encoder (relocated hq_P 2026-09-11, row `rationale-x86-asm-h`)

- `x86_tabs_on` -> `.github/ARCH-X86-ASM-ENCODER.md` §2 (TAB RECORD: tab-delimited fields, occupancy-keyed `x86_rec_kind`, `SCRIP_ASM_TABS=0` killswitch)
- `x86_rec` -> `.github/ARCH-X86-ASM-ENCODER.md` §2
- `x86_rec_kind` -> `.github/ARCH-X86-ASM-ENCODER.md` §2 (⛔ keys off FIELD OCCUPANCY, never off text)
- `x86_rec_split` -> `.github/ARCH-X86-ASM-ENCODER.md` §2 (the no-TAB legacy fallthrough — additive, not a cutover)
- `x86_rtcc_wb_bin` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (writeback order; R11 restored last in BINARY only)
- `x86_rtcc_rl_bin` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (PARTIAL RELOAD: scratch tier only — arg-tier reload would restore BSS zero over the return value)
- `x86_rtcc_wb_text` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (rip-addressed slots: the "R11 last" constraint does NOT apply in TEXT)
- `x86_rtcc_rl_text` -> `.github/ARCH-X86-ASM-ENCODER.md` §1
- `x86_rtcc_call` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (void/int/ptr form; CLASS N decline)
- `x86_rtcc_call_descr` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (⛔ RETURN-BEFORE-RELOAD LAW — capture RAX:RDX before reload or read a stale VM global as the return value)
- `x86_rtcc_clob` / `x86_rtcc_clob_raw` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (per-CALLEE decline, not a per-op filter)
- `x86_rtcc_live_mask` / `x86_rtcc_veneer_mask` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (`SCRIP_RTCC_VENEER`; R9 dropped when `gva_count()==0`)
- `rtccb` / `RTCC_SLOT_R9` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (slot-offset table; ⛔ H2 — the R9/GVA slot is deliberately NOT written back, and skipping the store is what makes the documented BLOCK-CANONICAL EXCEPTION true)
- `GVARQ` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (`RC-5-GVA` disp8 form, 4B vs 7B for `ABSQ`)
- `rtcc_anchor_cmp` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (`RC-5-ANCHOR`: `test r8, r8`, 3 bytes, identical ZF semantics)
- `RTCC_GLOBAL_R8_ANCHOR` / `RTCC_GLOBAL_R9_GVA` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (⛔⭐ the `s11` defect: duplicated unguarded macros + tree-wide `-w` meant no `-D` reached the emitter, and TWO GRADED RUNGS were decided on arms that were the same binary)
- ⛔ `x86_rtcc_writeback` / `x86_rtcc_reload` -> **names no longer exist**; see `.github/ARCH-X86-ASM-ENCODER.md` §1 last subsection (superseded by the `_bin`/`_text` medium split)

### `src/ir/frame_layout.c` (was `src/contracts/zeta_storage.c`) — the fixed-cell authority family (relocated cto 2026-09-16, row `rationale-zeta-storage-c`; verified at SCRIP `6f5ac9175`)

- `fc_cells_on` / `fc_cells_active` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §1 (THE ONE PORT OPINION, Z4-6; ⛔ the port axis is gone, the predicate is `return 1` and the discipline is what survives)
- `fc_geom` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §2 (the per-box fixed-cell geometry authority; per-kind MEASURED verdicts; LEN/ANY/NOTANY zero-cell IS the grant; Icon UPTO/FIND/BAL NOT-YET)
- `zls_fc_cell` / `FL_FC_SYNTH` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §3 (PAT$N REGION NET-OUT s191; unconditional arms only; the loud synthetic window base)
- `zc_nofc` / `fc_subj_member` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §4 (NOFC-SYM: the killswitch lives on ONE line of `fc_geom`, never at its head; the five-program category error)
- `SCRIP_ALT_CAP` (the `fc_geom` arm-member guard) -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §4 (ALT-CAP s66: the ALT carves 32 at α, so a denied arm-resident SAVE lands 32 too low; THE GRANT IS THE FIX)
- `fc_arm_member` / `fc_alt_register` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §5 (ALT-FLAT s202; ORDER IS LOAD-BEARING; N≤10 from the 3N+2 stub budget)
- `fc_seq_active` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §5 (⛔ stub: SEQ owns no cell and no datum, the LIFO position IS the sequence position; `IR_MATCH_SEQUENCE` deleted)
- `fc_save_active` / `fc_cond_fp` / `fc_cond_register` / `fc_pair_extent_register` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §5 (captures are TWO boxes, ZB-FC-3c; FLATDISP-LEAF-ORDER, the 039 `0xffff9b20` witness)
- `fc_head_fp` / `fc_head_register` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §5 (HEAD is not hook-shaped, ZB-FC-3d PARTITION; ALT-free v1 fence)
- `zw_node_k` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §6 (ZW-1 UNIVERSAL K AUTHORITY; v0 carve-only by design)
- `zw_carve_k` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §6 (THE ONE CARVE AUTHORITY; the split IS the displacement; ⭐ s137: stop numbering when the number is not wanted)
- `fc_tables_reset` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §7 (stale node-pointer keys across runtime compiles, the 140/test_case wild jump; ⚠ resets only `fct_n` at HEAD)
- `fc_frameless_fpr_rsp` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §8 (the ONE ADDRESS-MODE AUTHORITY; the N21 `POS(0) ARBNO ... RPOS(0)` witness)
- `fc_call_ok` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §9 (⛔ retired stub: CALL2BB 3b, the one-arg user-proc value-spine admission)
- `rt_proc_is_registered` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §9 (the row's anchor symbol: in CALL2BB it was the fail-safe registry consult at plan time; at HEAD its live use in this file is `zls_callee_is_gen`, `frame_layout.c:10`, deciding the staged call's `callgen.act` grant)
- `zls_callee_is_gen` -> `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §9
- ⛔ `zls2_geom` / `ZLS2_*` / `rt_zeta_port_mode` / `ZC_PORT_*` -> **names no longer exist**; `.github/ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §10 routes them (ZLS2 history is in the remainder row's material, `git show e25a5daf^:src/contracts/zeta_storage.c`)

### `src/runtime/rt/rt.c` — the procedure call protocol (relocated cto 2026-09-16, row `rationale-rt-c`; verified at SCRIP `db4a6b1fc`)

- `rt_outer_call` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §1 (the mode-3 entry thunk: r12 = live dcap top seeded from 0x70000000; ONE-SHOT-BRIDGE-M3, the adjuster is 16 not 8, the `002_output_integer_literal` movaps witness; ✅ now also reserves 4 MB ZLS headroom and pushes the landing pair)
- `rt_outer_call_delta0` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §1 (ICN-FR-5: zero r14 once, a separate symbol so every other language is byte-identical; push/pop, never tail-jmp, because r14 is callee-saved)
- `rt_proc_t` / `nformals` / `rest_kind` / `jmp_entry` / `zstatic` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §2 (NPSPLIT formals-only bound per SPITBOL Ch.8; rest_kind names WHAT differs, never which language; the regime is RECORDED, never re-derived; offsets baked by the runtime asm, `_Static_assert`ed)
- `rt_k_level_p` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §2 (RTX-FUNC-1: hidden visibility is load-bearing for the in-.so PC32 asm, the pointer alias crosses the boundary)
- `rt_proc_register_rec` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §2 (ONE-REG s119: replays the pre-s119 startup sequence exactly; 64-byte record pinned)
- `rt_call_named_proc` / `rt_call_proc_direct` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §3 (NCB-1 LEAF SPLIT: LIFO context is sound by the language definition) and §6 (SPELLED-TWICE s117: the sealed alpha$ arm; the third path is a suspected twin left verbatim)
- `rt_proc_open_fn` / `rt_frame_prep` / `rt_jmp_frame_lexprep` / `rt_jmp_frame_lexprep2` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §3 (⛔ stubs since GLOBALS-GONE s55, each with its OWED note; FN-RET OPEN s104: two consumers jumped 0 for a hundred commits)
- `rt_proc_call_open_fnret` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §3 (the s55 rax-channel contract: admitted == nonzero == the transfer target)
- `rt_proc_call_open` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §4 (the OPEN LEAF; cells resolved ONLY on the dyn path or the lexical frontends mint spurious globals)
- `rt_proc_call_open_det` / `rt_proc_call_open_det0` .. `_det4` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §4 (PL-REGAIN-1/4 fused det open: caller-frame cell pointers, one crossing; ⭐ ICN-ARG-NULL s239: `g_call_args` is a process-lifetime medium and nothing else rewrites the tail, the `atan(x,10.0)` witness)
- `g_call_args` / `CALL_ARGS_MAX` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §0, §4 (the staged-args medium; the tail above nparams is what the collector's root walk reads stale)
- `rt_proc_call_open_slim` / `rt_c2b_arm_trap` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §4 (BP-7 SCC slim leaves: guards before any side effect, so a 0 return falls back with nothing to undo)
- `rt_proc_call_prologue` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §4 (NPSPLIT clamp; the save push null-inits every remaining name)
- `rt_proc_call_prologue_lex` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §4 (ICN-VARARG: the one site holding both the record and the true nargs; ⛔ `jmp_entry` is the load-bearing discriminator or the tail list nests inside itself)
- `rt_pl_dc_ok` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §4 (PL-DC: the ONE eligibility predicate; `p->fn` deliberately untested; `LBL__` excluded structurally s119; ⚠ the vtmark frame-cell arithmetic as recovered no longer greps)
- `rt_proc_enter` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §5 (PROC-CONV two landings, EXACTLY FIVE PUSHES; EXPR-THUNK RESULT/EXITS s96; ⭐ WIRE-STACK rung 2: a pushed pair because `rtccb` is a flat global with no nesting, FAIL deeper)
- `rt_chain_enter` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §5 (⛔ no longer defined in rt.c; survives as assert text in `runtime_eval.c`)
- `rt_tiny_record_enter` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §6 (the five-quad record, args reversed above the result cell and PINNED at [rsp+16); the s104-s117 three-quad record published nargs=0)
- `rt_dyn_alpha_fn` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §6 (⭐ D-18c: an unsealed cell is not a target; the stub is the allocator's own sentinel; s108 default ON)
- `rt_nret_fix` / `rt_nret_fix_tiny` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §6-§7 (SN4-CAP-NAME-STRICT s170; ⛔ the s178-c re-arm is gone from `_tiny`, now a pass-through)
- `rt_proc_call_epilogue_γ` / `rt_proc_call_epilogue_ω` / `rt_proc_call_epilogue_ret` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §7 (γ is RETURN and NRETURN, ω is FRETURN, no fifth port; the lex arm's port-agnostic read preserved pending a ruling)
- `rt_proc_save_count` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §7 (NAMED γ/ω TWINS s112: the non-slim arm returned NULL and never restored, `probe/mon/mon_return_contract.sno`; restore base DERIVED, no new global)
- `rt_define_returns_by_frame` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §7 (ICN-WIRE-PAIR s244: ⛔ the discriminator is `dyn_scope`, not `jmp_entry` alone; `every p(1|2|3)` and `1010_func_recursion`)
- `rt_genp_entry_c` / `rt_genp_lookup` -> `.github/ARCH-RT-CALL-PROTOCOL.md` §8 (GENP slice-2: generator procedures on their own stack per instance; the s94 five-pop repair; ONE-POP; list membership is the discriminator)
- `rt_zeta_cstack` -> ⛔ name no longer exists (the storage-axis switch around the C-side frame push); `.github/ARCH-RT-CALL-PROTOCOL.md` §9 routes it to `ARCH-FRAME-LAYOUT-FIXED-CELLS.md` §1
- `g_pl_retry` / `g_pl_cp_stack` / `g_pl_zf3_stack` / `g_pl_zf_pending_*` / `icn_gen_state_t` / `rt_gen_get_fb` -> ⛔ names no longer exist; `.github/ARCH-RT-CALL-PROTOCOL.md` §9 (PL-FR-4 and ICN-FR-5 history; live designs in `ARCH-PROLOG-THREE-ZETAS.md` and `ARCH-ICON-RTX.md`)

## Remaining clusters, not yet relocated (see QUEUE.tsv / tasks/ for the dispatched rows)

Ranked by stripped-RATIONALE-comment count (heuristic classifier, see the FINDING above for the caveat that this is a lower bound):

| rank | file | stripped RATIONALE (est.) | queue row |
|---|---|---|---|
| 1 | `src/emitter/emit.cpp` (remainder, beyond §3 above) | ~600 | `rationale-emit-cpp-remainder` |
| ~~2~~ | `src/templates/x86/x86_asm.h` (⭐ path moved; **RC-4/RC-5 + TAB RECORD relocated 2026-09-11** -> `ARCH-X86-ASM-ENCODER.md`) | 186 blocks recovered, ~20 relocated | `rationale-x86-asm-h` ✅ CLOSED · remainder row `rationale-x86-asm-h-objnote-remainder` |
| 3 | `src/lower/lower_snobol4.c` | 232 | `rationale-lower-snobol4-c` |
| ~~4~~ | `src/contracts/zeta_storage.c` (⭐ path moved twice, now `src/ir/frame_layout.c`; **the fixed-cell authority family relocated 2026-09-16** -> `ARCH-FRAME-LAYOUT-FIXED-CELLS.md`) | 199 blocks recovered, ~40 relocated | `rationale-zeta-storage-c` ✅ CLOSED · remainder row `rationale-frame-layout-c-remainder` |
| 5 | `src/emitter/emit.h` | 119 | `rationale-emit-h` |
| ~~6~~ | `src/runtime/rt/rt.c` (**the procedure call protocol relocated 2026-09-16** -> `ARCH-RT-CALL-PROTOCOL.md`) | 156 blocks recovered, ~70 relocated | `rationale-rt-c` ✅ CLOSED · remainder row `rationale-rt-c-remainder` |
| 7 | `src/driver/scrip.c` | 105 | `rationale-scrip-c` |
| 8 | `src/templates/bb_call_proc_staged.cpp` | 81 | `rationale-bb-call-proc-staged` |

Each row's baton carries the file, the recovery method (`scripts/` extraction under `/tmp/.../scratchpad/rationale/` this session — not yet promoted to a checked-in script; see the FINDING), and the same DECORATION/RATIONALE split instructions as this row. Row-factory rule carried forward: a session picking one of these should relocate its highest-value sub-cluster and spin off further rows rather than trying to clear an entire file's ~100-600 comments in one sitting.

⚠️ **Two of this table's provenance links are now DEAD, for two different and both legitimate reasons (found by hq_P 2026-09-11 while working row 2).** `FINDING-2026-08-22-recover-stripped-design-rationale-classification.md` — the methodology file every one of these rows names as a prerequisite — was removed by `f78d8b3f` under Lon's 2026-09-04 order *"Remove old FINDING-\*.md files"* (826 August FINDINGs), and `ARCH-PATTERN-CHOICE-CARRIER.md`, the worked precedent, was folded into `ARCH-ENGINE.md` by `9e0e624a`. ⛔ **The remaining rows in this table still cite both in their batons.** Neither loss is an error — but a row whose STEP 2 says *"read the parent FINDING before trusting a DECORATION verdict"* now names a file nobody can open, and **a prerequisite nobody can satisfy is either a blocker or a dead letter.** ⭐ **What survives is enough:** this file's own header carries the methodology summary, and `ARCH-ENGINE.md` §3 is the live precedent shape. Use those.
