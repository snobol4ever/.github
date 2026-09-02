# FINDING 2026-09-02 (ceo, TRIO, on Lon's order "Do some Icon work while you wait") — `upto(!x)`/`find(!x)` outside a scan body loop forever because the one-argument by-name generator arm is not resumable; cured in the Icon lowerer by filling Icon's own defaults `&subject, &pos`

**Row:** `icon-upto-with-generator-argument-infinite-loops` (seat06 mint, rank 2). **Trees:** measured on SCRIP `f4532dea` (pristine `-O0`, `/home/claude/SCRIP`) and re-measured on `db299d41` (rung 0) in a worktree; landed as SCRIP `5934802b`. **Oracle:** `/home/resources/icon-master/bin/icont` v9.5.25a + `iconx`. **Box clock** 14:35–15:10 CDT.

## The measurement (ASM-DIFF-FIRST, then the runtime)

| witness (all `&subject := "badc"` unless a scan body is shown) | scrip m3 before | oracle |
|---|---|---|
| `every write(upto(!&lcase))` | `2 2 2 2 …` (hang) | `2 1 4 3` |
| `every write(upto(!"abcd"))` | hang | `2 1 4 3` |
| `tab(2); every write(upto(!&lcase))` | hang | `2 4 3` |
| `every write(find(!"abcd"))` | hang | `2 1 4 3` |
| `every write(any(!&lcase))` · `many(!&lcase)` | `2` · `2` | `2` · `2` |
| `"badc" ? every write(upto(!&lcase))` (scan body) | `2 1 4 3` | `2 1 4 3` |
| `"badc" ? every write(find(!"abcd"))` | `2 1 4 3` | `2 1 4 3` |
| `"xbadc" ? { tab(2); every write(upto(!&lcase)) }` | `3 2 5 4` | `3 2 5 4` |

- The baton blamed `bb_scan_upto.cpp`'s "var cset" β arm. `--dump-bb` shows the top-level witness never reaches that template: outside a scan body `upto` lowers as `CALL_BUILTIN_GEN "upto"` with ONE operand (the `ITERATE` over the cset), and the emitted box (`n4_call_builtin_gen_bx` in the `--compile` output) calls `rt_call_arr_gen("upto", args, 1, &state)` at α with the state cell zeroed, and re-calls it from β with the same state cell. The wiring is correct: `write.γ → upto.β`, `upto.ω → iterate.β`, `iterate.γ → upto.α`.
- `rt_call_arr_gen` (`by_name_dispatch.c:4835`) makes `find`/`upto` resumable ONLY for `nargs >= 2 && nargs <= 4` (`*resume` advances `i1`, `*resume = out.i + 1` on success). With `nargs == 1` it falls through to `rt_call_arr(fn, args, 1)` — the plain call, which returns the FIRST position on every β and never reads `*resume`. That is the hang, exactly, for every one-argument scanning generator: `upto`, `find` (and `bal` by the same arm, not measured).
- Inside a scan body `icn_retag_scan_body` retags the one-operand call to `IR_SCAN_UPTO`/`IR_SCAN_FIND`, whose templates carry their own cursor at `[off+16]` and resume correctly — which is why the scan-body witnesses were green and the row's "the template's β path" diagnosis was aimed at code the failing witness never runs.

## The cure (lowerer only, Icon-only file, 8 lines in `src/lower/lower_icon.c:lower_call`)

Icon defines `upto(c, s, i, j)` with `s` defaulting to `&subject` and `i` to `&pos` when `s` is defaulted (Griswold & Griswold, `find` identically). The lowerer now lowers the one-argument `find(x)`/`upto(x)` OUTSIDE a scan body (`cx->scan_sp == 0`) as the three-argument form by appending two `IR_KW_ICON` operands `&subject` and `&pos` behind the real argument (threaded `arg.γ → &subject.α → &pos.α → call`), so the resumable two-to-four-argument arm of `rt_call_arr_gen` applies unchanged and the generator restarts from the current `&pos` on every fresh α. Inside a scan body nothing changes: the call keeps one operand and the `IR_SCAN_*` retag path stays (the fast template arm is not lost). No runtime file is touched — `by_name_dispatch.c` is inside hq_C's rung-0 cut and the ruling of 15:35 keeps other seats off it.

## Verdicts on the patched tree (worktree of `db299d41`, `-O0`)

- All nine witnesses above: scrip m3 = oracle (SAME ×9); m4 (`--compile` + `gcc` + `libscrip_rt.so`) on the top-level and `tab(2)` witnesses: `2 1 4 3` and `2 4 3`.
- The row's DONE-WHEN as minted could never pass — its program ends `end;` and both SCRIP and Arizona reject a trailing `;` after `end` (`invalid declaration`); re-cut on the baton without the semicolon (the same instrument class as the three rung-0 defects: run a minted DONE-WHEN once before trusting it). Re-cut DONE-WHEN: PASS.
- Icon smoke `PASS=14 FAIL=0` both modes. Icon STRICT rung suite `test_icon_rung_suite.sh` against the patched binary with the real corpus: `PASS=264 FAIL=6 BADEXIT=1 XFAIL=27 TOTAL=298` in every mode — identical to the pinned watermark on `f4532dea` (the six reds `rung36_jcon_{cxprimes,genqueen,level,recogn,var}` + `proto` BADEXIT are the owned rows named in `GOAL-ICON-100.md`, untouched). `strip_comments.py --check` 0; `test_gate_emit_no_lang.sh` OK.
- SNOBOL4: not a consumer of `lower_icon.c`; `make test` on the landing tree in the receipt below.

## Population and limits

One lowering site; two builtins (`find`, `upto`) in the one-argument, no-scan-body shape. `bal` shares the by-name arm and is NOT cured here (its default-filling needs `c1,c2,c3` semantics — its own row if a witness shows it). The `IR_SCAN_*` templates were not changed and their "var cset" β arm was not measured as defective — the baton's diagnosis is retracted by this FINDING, not confirmed.
