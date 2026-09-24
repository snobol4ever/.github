# FINDING 2026-09-23 cto — no veneer on any call into the asm runtime; the RTX entries keep r8–r11 themselves

Row `spine-no-rtccb-veneer-on-any-call-into-the-asm-runtime-the-rtx-abi-preserves-r8-to-r11` (CEO-1223/1224). Lon, in-chat to the ceo, verbatim: *"get rid of veneer for all RT ASM instances."*

Everything measured here is also folded into the row's baton ledger and GOAL-CTO.md's CTO-161, per the findings law. This file is the long form.

## 1. What was true before (SCRIP 8a2e9bdff)

- The row's DONE-WHEN read **RED: 958 veneered calls into the asm runtime across 13 witnesses** (control: 2817 veneered calls into the C runtime).
- `x86_rtcc_clob_raw()` hand-listed thirteen asm callees (a LEAF table and a T table). Every other symbol got the full `rtccb` spill (r8/r10/r11 written back before the call) and reload (r8–r11 after it). The asm files themselves held no veneer: it was all call-site code.
- **The asm runtime defines 272 entries, not 72.** A grep of `RTX_FUNC(` lines sees 72. The objects define 272: 74 written with `RTX_FUNC`, 197 expanded by the Prolog shim macros (`PL_CTX_LEAF`, `PL_CTX_LEAF_BALL`, `PL_ROOT_LEAF`, `PL_ROOTCTX_LEAF`, `PL_AX_VENEER`, `PL_CMP_LEAF`) through token pasting, and `rt_cap_open_plain` as a second entry inside `rt_cap_open`. The census had to be taken over the **preprocessed and assembled** code: the raw source hides `RTX_REAL_FINITE_OR`'s r11 and every macro-expanded body.
- On the parent tree's objects, the new walker proves **16 of 272** entries (the 13 clean bodies and the 3 zd probes, which already saved everything) and reports **413 violations**.

## 2. Four facts that decided the design

1. **Nothing reads r8 as ANCHOR.** `rtcc_anchor_cmp` has no user; `bb_match_begin` reads `rt_anchor_g`. r8 only has to survive.
2. **r9 is the GVA base everywhere in emitted code except while it carries a sixth argument** (`rt_match_replace`). The veneer's reload was what handed it back, so the entry owes r9 = GVA.
3. **A lazily bound PLT slot clobbers r10/r11 before the callee runs.** `_dl_runtime_resolve` jumps to the target through r11 after running `_dl_fixup`. So the FIRST call of every symbol would hand the callee a clobbered r10/r11 to "preserve", and a bare `call sym@PLT` could never keep the promise. Therefore:
   - mode 4 emits `call qword ptr [rip + sym@GOTPCREL]` for an entry (GLOB_DAT, filled eagerly);
   - mode 3 already calls by address;
   - RTX-to-RTX calls and tail jumps use `RTX_CALL` / `RTX_JMP` through the GOT.
4. **The diagnostic register gate's negative arm withheld the call-site veneer, which no longer exists for asm entries.** Its negative arm is now a plant: `SCRIP_RTX_PLANT_CLOBBER=1` makes the emitter write −1 into r10/r11 after every bare asm call, which is what a callee that broke the contract would leave.

## 3. The contract (stack-based; the RTX bodies no longer touch rtccb)

An RTX entry returns r8, r10 and r11 as it received them, and r9 as rtccb slot 6. A body keeps the promise in one of three ways:

- **It never writes them.** These bodies were renamed onto free registers: `rt_cmp_d`, `rt_jct_relop`, `rt_assign_var`'s fast path, `rt_match_enter`, `rt_defer_close`, the allocator (`rt_gcheap_alloc`/`rt_str_alloc`/`rt_agg_alloc`), `rt_translate_bytes`, `rt_cap_match_begin`/`pop`/`top`, `rt_match_ctx_restore`, the Prolog ball macros and `RTX_REAL_FINITE_OR`.
- **It opens with `RTX_SAVE` and leaves by `RTX_RET`** (or `RTX_RET_GVA` when r9 came in as an argument): `rt_subscript_var`, `table_find_pair_d`, `str_concat_d`, `dat_field_get`, `rt_coerce_num2_d`, `rt_match_replace`, `rt_cap_open_plain`, `rt_pl_goal_gen_h`.
- **It keeps its own push/pop pairs** (the zd probes).

Every exit into C is wrapped, because gcc-compiled C clobbers all four:

- `RTX_CCALL` for a call inside an unsaved body;
- a local `RTX_CTAIL` stub for a tail exit, or `RTX_CTAIL_SAVED` inside a saved body (it reloads the fifth and sixth arguments from the save area first);
- `RTX_GATE`'s gate-off arm lands on such a stub.

The entry list is **derived**: `RTX_FUNC` / `RTX_ENTRY` write the name into section `rtx_entry_names`, `rtx_entry_is()` scans it, and `x86_rtcc_clob_raw()` asks it. The LEAF and T tables are deleted. Calls into the C runtime keep the veneer unchanged.

## 4. The GC instruments: a blind spot the row surfaced

The allocating derivation (`util_gc_census.allocating_entries_from_binary`, read by both the safe-point census and the emitter's allocating table) followed `call` and `jmp` edges only. Two edge kinds were invisible to it:

- **Conditional tail exits.** Every asm entry whose only road to an allocating C twin was a conditional exit read NON-ALLOCATING: `VARVAL_fn`, `rt_size_d`, `rt_str_coerce`, `rt_match_enter`, `rt_defer_close`, `table_find_pair_d`, `rt_cap_open`. So did 67 functions that depend on them.
- **Calls through a GOT slot.** objdump labels such a slot with the nearest symbol rather than the target, so the walk now resolves the slot through its GLOB_DAT relocation.

The row's stubs turn each conditional exit into a call, which is how the gap surfaced. With the fixed walk, measured on the parent 8a2e9bdff and again on origin 527120834 (each tree with its own binary), the same numbers both times:

| measure | before | after |
|---|---|---|
| allocating table (symbols) | 1698 | 1765 (none removed) |
| allocating call sites | 230 | 236 |
| polled | 230 | 232 |
| unpolled | 0 | **4** |

The four unpolled sites are pre-existing allocating calls with no safe point after them:

- `bb_match_begin.cpp` `rt_match_enter`
- `bb_match_defer.cpp` `rt_defer_close`
- `bb_match_value.cpp` `rt_defer_close`
- `bb_unop.cpp` `rt_size_d`

The census baseline records unpolled 4 in the same landing (the CEO-1119 shape: the instrument getting honest about a standing tree). The cure tree reads exactly the census of its control, so the ABI change itself moves no GC instrument.

## 5. Evidence

- **DONE-WHEN:** RED 958 before; PASS after (0 veneered asm-entry calls; the C runtime still has 2594).
- **`test_gate_rtx_entries_keep_the_rtcc_four.sh`** (preflight, hermetic, ~3 s): 272 of 272 proven. The walker checks the four registers and the stack slot by slot along every path, and call alignment. Its self-test proves 9 truthful forms and catches 10 planted lies by name.
- **`test_gate_rtx_calls_carry_no_veneer.sh`** (blocking, ~1.7 s): 0 veneered and 0 PLT calls into an entry, 1634 GOT calls, 2602 veneered C calls as the control, and the veneer plant is seen.
- **`test_gate_diag_regs_survive.sh`:** r10 = 2 bare, −1 under the clobber plant.
- **Population machine, pass 1** (control 8a2e9bdff against the cure; all seven masters; both modes; arms `nogc` and `s0` at the shipped arena): **19,704 cells, every one the same kind on both trees, 0 PASS cells with different stdout.**

  | language | cells |
  |---|---|
  | SNOBOL4 | 7928 |
  | Icon | 3304 |
  | Prolog | 2252 |
  | Raku | 3716 |
  | Snocone | 1348 |
  | Pascal | 984 |
  | Rebus | 172 |

- **Pass 2** (control 527120834 against the rebased cure), which adds every RTX gate off (all stubs into C twins) at `nogc`, and stress 1: **Pass 2, gates off** (every `RTX_GATE` family off, so every stub into a C twin is exercised; all seven masters; `nogc`; both modes): **9,852 cells identical** (SNOBOL4 3964, Icon 1652, Prolog 1126, Raku 1858, Snocone 674, Pascal 492, Rebus 86).

  **Pass 2, stress 1** (SNOBOL4, Icon, Prolog; `nogc` and `s1`; both modes): 13,484 cells, **13,480 identical**. The four that differ sit at the harness's 120-second budget and are not a difference between the trees:

  | cell | pass | re-read | direct timing (m4, stress 1) |
  |---|---|---|---|
  | `user_function_eval_span_replace_branch_1` s1/m3 | control HANG, cure PASS | control PASS 105 s, cure HANG 120 s | 0.1 s standalone on both, identical stdout |
  | `benchmark_meta_qsort` s1/m4 | control PASS, cure HANG | control hangs too | rc 0, REF, 10,420 collections on both; 138 vs 158 s; **paired under one load 125.7 vs 126.4 s** |
  | `test_rung10_programs_puzzle_12` s1/m4 | control PASS, cure HANG | cure HANG | rc 0, REF, 298,594 collections on both; 119 vs 90 s |
  | `test_rung10_programs_puzzle_13` s1/m4 | control PASS, cure HANG | control hangs too | rc 0, REF, 298,594 collections on both; 57 vs 86 s |

  The emitted mode-4 asm of `meta_qsort` differs between the two trees by exactly the veneer: 1,485 `rtccb` stores and 3×495 reloads gone, 710 PLT calls turned into GOT calls, nothing else..
- **Smokes:** 7 of 7 green.
- **`make preflight`:** 61 arms, 1 red, which is the pre-existing `test_gate_every_graded_suite_has_an_attribute_csv.sh` refusal on the `snc-bench` key. It refuses identically on origin.
- **GC gates:** the census ratchet 7/7; the allocating-set gate (table 1765 = census 1765); the bare-poll witness gate 162 sites, 84 witnessed, 78 unwitnessed at its ceiling of 78. The one arrival is `bb_unop.cpp` `rt_size_d`. The rewrite also absorbed the emit.cpp / bb_define.cpp line drift that had the gate red on origin at 86.
- **Artifacts regenerated:** SNOBOL4 benchmarks 23 files (−2277 lines net), demos 25 (−23,992), Prolog benchmarks 23 (−53,725), Icon benchmarks 17 (−2151). That is code size, not speed: the benchmark re-run is parked on Lon's word, and nothing here claims a time.

## 6. What this row leaves open

- **The four unpolled allocating calls of section 4**, each a GC row. `bb_unop.cpp` `rt_size_d` is the easy one: its sibling arm already polls after the same call.
- **Faster hot paths.** The saved bodies (`rt_subscript_var`, `table_find_pair_d`, `str_concat_d`, `dat_field_get`) pay four pushes and four pops where the call-site veneer paid three stores and four loads. They are equal-cost today and renamable later, one body at a time, under the same walker.
