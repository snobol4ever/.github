---
name: runtime-calls
description: How emitted code calls procedures and the runtime: rt_proc_t, the call protocol, by-name calls, generator stacks, the one builtin table and the one error protocol. REQUIRED by the skill gate before editing rt.c, lower_call_forms.c or builti
---

# Runtime calls: procedures, builtins, errors

Detail is in `reference.md` beside this file. The leaf ABI itself (the rtcc four, clobbers, CFI) is skill `rtx-asm-leaves`; placement of the call's cells is skill `scrip-memory-model`.

## 1. The rulings this layer obeys

- **No C function enters a box** (CEO-1576): a C road that would transfer control returns an address and the box jumps; `longjmp` into or across emitted frames is a transfer and is forbidden in new code.
- **Logic lives in emitted boxes, not in C** (CEO-985); a runtime entry is named on the node as data (CEO-1836); language identity stops at lower (CEO-1838): the runtime never decides by a name's spelling.
- **No interpreter**: one hash lookup for a run-time name is a lookup, never a dispatch loop.
- **A port transfer carries no value**; only procedure-exit wiring promotes rax:rdx to the returned DESCR (skill `scrip-architecture` § 5).
- **One error voice, spoken once, at the root** (CEO-625: `core_error_voice`, its equivalences in `util_render_error_voice.py`).

## 2. The procedure call protocol as built (`src/runtime/rt/rt.c`)

- **The record** `rt_proc_t` (`src/runtime/rt/rt_proc_block.h`): name, function, `nformals` (formals only: they bind) against `nparams` (every name saved and nulled, SPITBOL ch. 8), `rest_kind`, `jmp_entry` (the regime: a jmp-entry blob against a call-regime body, recorded, never re-derived), `zstatic`, the generator and dynamic-scope bits. Offsets the asm reads are `_Static_assert`ed; new fields are appended last. Mode 4 registers each procedure at startup through `rt_proc_register_rec`.
- **A call** is open, frame, transfer, epilogue: the open families (`rt_proc_call_open`, `_det`, `_det0` to `_det4`, `_fnret`, `_p`, `_pn`; `rt_call_open_staged`, `_tail`, `_tail_lex`, `rt_call_open_by_name`, `rt_call_named_open`), the prologues (`rt_proc_call_prologue`, `_lex`), the landings (`rt_call_land_γ`, `rt_call_land_ω`) and the epilogues (`rt_proc_call_epilogue_γ` and `_ω`, their `_named_` and `_idx_` twins). RETURN and NRETURN are γ, FRETURN is ω; there is no fifth port.
- **Arguments** ride the staged-arguments medium `g_call_args` (`rt_call_args_need`, `rt_call_args_clear_from`).
- **Generator procedures** (`rt_genp_*`): each activation runs on its own pthread stack (`rt_genp_thread_entry`), delivering by `rt_genp_yield` and `rt_genp_deliver_γ`/`_ω`; destroy joins the parked thread.
- **Mode 3's entry** is the thunk `rt_outer_call` (and `rt_outer_call_root`) in `src/driver/scrip.c`: it saves the caller's r12, seeds r12 from `RT_DCAP_TOP`, reserves headroom, and enters the graph with the landings pushed.
- **A declining leaf** returns `RTX_NOT_HANDLED` (0xFF in al, never a tag's low byte) with its arguments as received; the box then calls the C twin itself under the C convention (the verdict road; first built for the arith leaves).

## 3. DESIGN: the one builtin table (CEO-2016; `corpus/tests/shared/builtin_table/STEPS.tsv`)

A builtin call is decided once, in lower, and the runtime re-decides nothing by name. `harness/scripts/builtins.tsv` (one row per builtin per vocabulary: `bid vocab name min max entry conv recv flags op`; `conv` is one of `leaf`, `gen`, `open`, `inline`) generates `src/runtime/builtin_table.inc` and `builtin_table.h` (`g_builtins`, `bt_bid_of`) by `util_gen_builtin_table.py`, gated by `test_gate_builtin_table_is_current.sh`. A bid is never renumbered or reused. The lowerer resolves a literal name in its own vocabulary after the program's own definitions, pads arity, and picks the call kind from `conv`; a name with no row and no definition takes the one dynamic road. On 2026-11-01: step 1 (the table) DONE; step 2 (every chain arm a leaf) ASSIGNED to hq_runtime; steps 3-6 BLOCKED in order (SNOBOL4 resolution in lower, Icon, Raku, the dynamic road and the deletion).

## 4. DESIGN: the one error protocol (CEO-2020; `corpus/tests/shared/exceptions/STEPS.tsv`)

The Prolog road, made the law for every language. **P1** one ball record in the context (`{class, code, text, value, src_node, stno, exit_code}`, a GC root; class FATAL, HANDLED or CONVERTED). **P2** a raise records the ball and RETURNS `FAILDESCR`; every C caller returns the verdict; no `setjmp`, `longjmp`, snapshot or `exit`. **P3** a box that can receive a ball tests the class at the head of its ω road and jumps to its enclosing catch gate's ball entry, wired at compile time. **P4** a catch construct is BOUND + body + UNMARK + a GATE whose ball entry restores rsp to the gate's planned depth, unwinds the islands to the BOUND's marks and runs the handler. **P5** the chain root's ball exit is the one voice site and exits with the oracle's code. **P6** SNOBOL4's SETEXIT and `:(CONTINUE)` are if-type gates through stored slots. **P7** an exhausted stack or a refused heap request is a raise where the language makes exhaustion an error term (Prolog's `resource_error`), and stays fatal where it is fatal (SNOBOL4's ERROR 246). None of it is built yet: on 2026-11-01 step 1 (the ball record and the root) is ASSIGNED to the cfo and steps 2-9 are BLOCKED behind it; the three resource steps are FREE.
- **The catch record (resource S1)** (CTO-508, 2026-11-04): five raw words (prev, resume_pc, rbp, rbx, r14) of the catch-marked BOUND's cell after its mark and banked B, residence the plan row's; linked from the trail header's CATCH word at the BOUND's alpha and the gate's beta, unlinked at the goal arm's gamma and omega UNMARKs; the handler resumes at the omega UNMARK's alpha with RBP, RBX, R14, R13 from the record, RSP the record's rbp (the UNMARK restores the depth itself; no rsp word), R15 and the header slot the overflow ball; resumable only when the pc is emitted code (the code pool or the adopted mode-4 text), a C pc stays fatal 246 until S2's rt_stack_refuses covers the leaves.
- **The rows probe is the coo's board, not the lander's gate** (CTO-507, 2026-11-04): rows= is struck from steps 1-8 and stays on the finish, comparing pass rate against ROWS0.tsv (a denominator move never reads red, a row at 100 percent is never below); ROWS0 is never re-recorded lower; a step lands on its witnesses, smokes and the test request to the coo. The ball's value is rooted in core_gc_roots by rt_gc_visit_descr, not a root range (CTO-506 amended).
