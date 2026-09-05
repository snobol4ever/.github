# FINDING — the six lexical comparators truncate at a NUL byte in THREE compare sites, and one cure lands (ceo, 2026-09-05 16:00 CDT)

**Row:** `snobol4-lgt-fails-comparing-a-replace-translated-value-against-its-own-prefix` (minted seat05, root-caused seat10, re-verified seat12, cured by the ceo under MODE CEO — Lon 2026-09-05 15:15, verbatim: *"Go to CEO only mode."*; the flip to OCTET at 15:42 found the cure in hand). Lane by cure: hq_S (HQ-SUSTAIN, the SNOBOL4 runtime) — told.

## THE CLAIM

`LGT`, `LLT`, `LGE`, `LLE`, `LEQ`, `LNE` compared their operands as NUL-terminated C strings. Any SNOBOL4 value containing a NUL byte — `CHAR(0)`, a `REPLACE` through a table whose image begins at `&ALPHABET[0]`, a captured slice whose backing buffer carries one — ended the comparison at that byte, so two different values read equal and a longer value read not-greater than its own prefix. The gimpel `LEXGT_driver` witness (`LEX_TT = REPLACE(&ALPHABET, ALPHA, &ALPHABET)` sends `a` to NUL, `b` to STX, `c` to EOT) was the field report; `A = CHAR(0) CHAR(2) CHAR(4)`, `B = CHAR(0) CHAR(2)`, `LGT(A,B)` failing was seat10's minimal witness.

## WHAT THE MEASUREMENT ADDED TO SEAT10'S ROOT CAUSE

seat10 named `core.c` `_LGT_` and its five siblings (`strcmp` on `VARVAL_fn` pointers). That is one of THREE compare sites, and it is the one the compiled program never reaches:

1. **The compiled path.** `lower_snobol4.c` `sx_pred_cmp` lowers all six names to `IR_CMP_TEST` over two `IR_COERCE_STRING` operands. `bb_cmp_test.cpp` calls `rt_cmp_d` in the hand-written asm runtime (`src/runtime/rtx/rtx_arith.s`); its string arm (`.Lcd_strloop`) was a byte loop that stopped at the first zero byte and never read `slen` at descriptor offset 4 — even though `rt_coerce_str_d` had just written a correct `slen` into both operands. Witness: 7 wrong lines of 17 in both modes against `sbl -bf` (the direct-call witness below).
2. **The APPLY/OPSYN path.** `APPLY('LGT', A, B)` does not reach `core.c` either: `rt_call_arr_bl` handles `BID_APPLY` inline and calls `try_call_builtin_by_name`, whose length-and-first-letter switch sends every 3-letter `L`-name to `bn_lexrel` (`by_name_dispatch.c`) — a fourth `strcmp`. Found by a gdb executed-line trace after breakpoints on `_LGT_`, `core_call_registered_fn`, `rt_call_value` and `rt_cmp_d` all stayed silent; a grep for the literal `"LGT"` cannot find it because the arm is spelled `fn[1]=='G'&&fn[2]=='T'`.
3. **The registered-function path.** `core.c` `_LGT_` … `_LNE_`, reached through `APPLY_fn`'s hash bucket only when the by-name dispatcher declines.

## THE CURE (SCRIP `cc7aae51e`, one commit; witnesses corpus `c4fcc3093`)

- `rtx_arith.s` `rt_cmp_d`: for a `DT_S` operand read `slen` from `[reg+4]`; `0` or `0xFFFFFFFF` keeps the old NUL scan (an unset producer keeps today's behaviour — the same `slen==0` fallback hq_P chose for LPAD/RPAD in `7e190f16a`); compare `min(la, lb)` bytes unsigned, then the lengths. Registers stay within `rax rcx rdx rsi rdi r10 r11`; the `x86_asm.h` RTCC leaf contract for `rt_cmp_d` (`R10|R11`) is unchanged, so no emitted code changes and no `.s` artifact is owed.
- `core.c`: one exported helper `lex_cmp_pair(DESCR_t, DESCR_t)` (declared in `core.h`) — `memcmp` over `min` then length tie-break, `slen` honoured when `v == DT_S && slen && slen != 0xFFFFFFFF`, else `strlen`; the six `_L*_` functions call it.
- `by_name_dispatch.c` `bn_lexrel`: calls the same helper.

## THE INSTRUMENT

`scripts/test_gate_sno_lex_compare_binary_safe.sh`, wired into `make test` after `test_gate_sno_runtime_define.sh` (~5 s). Witnesses `corpus/tests/snobol4/lexcmp_nul_1.sno` (direct calls: the six on NUL-leading values, prefix pairs, `CHAR(255)` vs `CHAR(1)`, integer operands `LGT(3,12)`) and `lexcmp_nul_2.sno` (`APPLY` and `OPSYN` forms), refs cut from `/home/resources/x64/bin/sbl -bf` and re-cut live by the gate so oracle drift reads red. **Proven to fail once:** with the four source files stashed and the tree rebuilt, RED on 4 of 4 arms (14 + 16 differing lines per mode); unstashed and rebuilt, GREEN; the row's own DONE-WHEN (gimpel `LEXGT_driver`, both modes) rc=0.

## CONTROL ARMS (cured tree, RT_OPT=-O0, incremental make)

Icon smoke m3 15/15 · m4 15/15 (`test_smoke_icon.sh`) · Prolog smoke 5/5 (`test_smoke_prolog.sh`) · SNOBOL4 smoke 7/7 (`test_smoke_snobol4.sh`) · `strip_comments.py --check` 0 offenders / 383 files · `test_gate_our_files_are_lf.sh` 0 of 4507 · `test_gate_template_medium_invisible.sh`, `test_gate_rtx_inventory_live.sh`, `test_gate_corpus_coverage_classified.sh`, `test_gate_emit_no_lang.sh` green. `grep -c IR_CMP_TEST src/lower/lower_*.c` names ONE lowerer (snobol4), so the SNOBOL4 master is the board owed; `rt_cmp_d` has no other caller in the tree (`pattern_match.c`'s sort compare is its own). The SNOBOL4 master runner's receipt is on the CEO-294 line.

## THE LESSON, FOR THE RULES

A root cause named from the C source is a root cause for the C path. **Before curing a builtin, list every path that reaches its NAME:** the lowerer (grep the name in `lower_<lang>.c` — a special-form arm means the compiled program never calls the C function), the by-name dispatcher (whose arms are spelled by length and first letter, so grep the switch, not the literal), and the registered table. gdb with breakpoints on every candidate, run to exit, is a five-second census of which one fires; the ASM-DIFF-FIRST order still holds — the emitted `.s` showed `call rt_cmp_d` and no `_LGT_` at once.
