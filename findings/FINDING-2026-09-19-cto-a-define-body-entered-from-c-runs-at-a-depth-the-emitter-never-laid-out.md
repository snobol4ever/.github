# FINDING 2026-09-19 (cto) — a DEFINE'd body entered from C runs at a depth the emitter never laid out; the deferred-capture pump is now box-driven on Lon's word

Row: `gc-the-blob-frame-interior-takes-one-static-layout-and-its-cross-frame-dependency-is-named` (ceo-minted 2026-09-19, rank 0 under MODE DUO). The measured claims below are folded into that row's LEDGER and into `GOAL-CTO.md` CTO-83, because this file has a deletion date (CEO-859).

## The question the row asked

Overnight a runtime landing with the emitted asm BYTE-IDENTICAL (SCRIP `0a6f75394`, `uint8_t src_node[3]` in `DESCR_t`) took `user_function_eval_pos_replace_branch_1` to SIGSEGV in both modes: `mov [r12+0], rcx` in an `IR_MATCH_ASSIGN_COND` with r12 = 0x70 = `DT_DATA`. The ceo cured the trigger (three named bytes, no array, no canary) and asked one question first: **who last wrote r12** — the thunk's own blob, a movaps on a misaligned callee frame, or a reload through a foreign rbp.

## The answer, measured in mode 4 with symbols

Same emitted `w.s` (21569 lines) linked against the green runtime (HEAD) and the red one (HEAD with the array `descr.h`, rebuilt in a worktree).

1. **r12's last writer** is `n653_match_end_α`'s cas_mark reload, `mov r12, [rbp-8]`, in the OUTER match `'ab' ? p` — with rbp = `n651_match_begin`'s own frame (rbp traced from n651's entry to that instruction: every write is a balanced C prologue/`leave`). None of the three candidates. The frame was right; the cell was wrong.
2. **The cell's writer** (hardware watchpoint on n651's `[rbp-8]` from its `push r12` to the reload): `n233_call_α+15: mov qword ptr [rsp + 2288], rax` — the `a(x)` field-call box in `ListInsert4` (source line 39) staging its argument DESCR `x` (v = 0x70 = `DT_DATA`) into `call.argv`, with rsp 2288 bytes BELOW the cell.
3. **Why 2288.** `--dump-zeta`: `call.argv` of that box is main-frame slot **+2288** and the operand it copies from (`IR_VAR x`) is +2304. The emitter emitted `[rsp + off + op_zdepth]` with `op_zdepth = 0` (`x86_zref` → `[rsp# + off]` → `XK_RSP64` → `off + _.op_zdepth`). **A DEFINE'd body is a GROUP scope inside the ONE graph `main` (65544-byte frame), not a graph of its own, and it assumes rsp == main's statement level.** It never is.

| entry path into a body | rsp below main's statement level |
|---|---|
| direct in-graph call `ListSize(bank)` (α carve + wires) | 96 (mini program `f(1)`: 112) |
| deferred-capture chain, green runtime | 2112 |
| deferred-capture chain, red runtime (five C frames + a canary each) | 2192 |
| `EVAL('f(2)')` | 7920 |
| `APPLY('f', 3)` | 7664 |

The body's slot block is shifted DOWN by exactly the entry depth: coherent within the body (answers stay right), landing on whatever sits there — other statements' dead slots (green: main+80, a dead `IR_DEFINE` result) or, when the depth exceeds the scope's offset, BELOW main's rsp on the spine cells of the statement that is running (red: main−16 = n651's saved r12). The chain, frame by frame: `n653 call rt_match_end_all` → `c_rt_match_end_all` → `c_rt_dcap_end_ok_open` → `rt_dcap_pump` → `rt_sno_dtx_value` → `rt_call_proc_descr` → `rt_proc_enter` (asm) → `ListInsert_α: sub rsp,144` → `LBL__ListInsert`. Five C frames, each holding a `DESCR_t` local; the array member turned the canary on in each; 80 bytes is the whole difference between a dead slot and the saved r12. § 6.2c's "carve depth contract" is the same mechanism: +16/32/48 on the blob carve moved every body entered from inside the match by that much; +64 put the block back on dead slots.

## Lon's three words, in-chat to the cto, verbatim

1. *"If it was entered via C through a deferred-capture thunk chain, then REMOVE the C code. I want ASM code there."*
2. *"It is disallowed to enter a BB via a C function except the very FIRST one inside the SCRIP, the ORIGINAL program invocation."*
3. *"If a C function must be called, then it must return the data needed for the BB to perform the direct jump, i.e. the C function must return before the BB is jumped into."*

(2) is law for RULES.md § ABSOLUTE (the ceo seats it). (3) is the protocol `bb_match_defer` already uses for a deferred pattern's user call.

## The cure (SCRIP, this landing)

`rt_match_end_all` and the old `rt_dcap_step` are deleted (C and rtx). `bb_match_end` has ONE pump: `call rt_dcap_end_ok_open` returns 0 (done), 1 (strict refuse) or the ENTRY ADDRESS of the next `*name` capture target; the box does `push rbx; push r12; push ω; push γ; lea rcx,γ; lea rdx,ω; jmp rax` — `rt_proc_enter`'s own convention — and `rt_dcap_land_γ(frame0)` / `rt_dcap_land_ω()` run the epilogue, finish the capture and return the next target. `rt_dcap_call_prepare` (rt.c) is the pre-entry half of `rt_call_proc_descr` for the box-entered arms and aborts loudly on a C-frame procedure. The dead `thunk()` arm (no writer in the tree) goes with it. `rt_dcf_t` 40 → 64 bytes, asserted; `rtx_match.s` strides `shl 6`.

**Verdicts.** Witness green both modes on HEAD; **the red runtime reads green in both modes** (the fail-once); **+16/+32/+48 on the blob carve run clean** — the carve gate is rewritten with that inverted arm and a pump-shape arm proven on a doctored emission; entry depth 2112 → 1568, all of it emitted frames; the only C→BB entry left in the witness's dynamic trace is `EVAL(...)` at pattern-build time; preflight 56/0; seven smokes; rtx unit ALL PASS; allocating table regenerated, gate PASS; callee-saved copy ceiling 133 → 185 (same copies at +2 sites per match end, reason in the gate header). `conservative total` 24, unchanged.

## What the law does not close

The body-slot regime is still `[rsp + main-frame offset]` at depth 0. The cure made the depth a constant of emitted frames, not zero; a body whose scope starts below the depth still writes into the chain's frames. That cure is a frame base for bodies (`x86_fb_pinned`, or a per-activation carve) and needs Lon's word on which. The remaining C→BB entry sites in the runtime, the denominator of the law: 14 (`runtime_eval.c` :298 :301 :532; `rt.c` :994 :1007 :1010 :1014 :1015 :1233 :1709 :1714 :1843 :1845 :1856).
