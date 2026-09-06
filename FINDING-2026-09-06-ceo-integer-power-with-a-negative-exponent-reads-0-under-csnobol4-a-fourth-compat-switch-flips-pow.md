# FINDING 2026-09-06 (ceo) — integer ^ negative integer reads 0 under CSNOBOL4 and a real under SPITBOL; SCRIP followed SPITBOL even under `--compat=csnobol4`; a fourth compat switch flips Budne's `pow.sno`

**Row:** `flip-csnobol4-pow` (rank 0, owner hq_S, claimed and landed by the ceo under Lon's 2026-09-06 15:5x "everyone is on bug fixing package suite programs … Pick a program and fix it"). **Landed:** SCRIP `e7c45454e` (corpus unchanged, `7fba27c82`).

**The witness.** `corpus/packages/snobol4/csnobol4_suite/pow.sno` (55 lines, Budne's suite, oracle csnobol4) read FAIL in both modes at SCRIP `449b1e522`: one line of its 25-line ref differed — the ref prints `9^-1 = 0`, SCRIP printed `9^-1 = 0.111111111111111`.

**The oracles, measured on a seven-case witness (`ipow.sno`):**

| expression | csnobol4 | sbl -bf (SPITBOL) | SCRIP before | SCRIP after, `--compat=csnobol4` | SCRIP after, default |
|---|---|---|---|---|---|
| `2 ^ -1` | 0 | 0.5 | 0.5 | 0 | 0.5 |
| `(-2) ^ -3` | 0 | -0.125 | -0.125 | 0 | -0.125 |
| `1 ^ -5` | 0 | 1. | 1. | 0 | 1. |
| `(-1) ^ -3` | 0 | -1. | -1. | 0 | -1. |
| `2. ^ -1` | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| `0 ^ -1` | Error 2 | 0. | 0. | 0. (residual) | 0. |

CSNOBOL4's rule is not truncated division (`1 ^ -5` would be 1): a negative integer exponent on an integer base yields integer 0, and a zero base raises Error 2 (fatal at level 0). SPITBOL promotes to a real. Both are correct for their dialect; the suite's oracle is csnobol4.

**The cure (two files, one arm).** `--compat=csnobol4` now also sets `SCRIP_IPOW_CSNOBOL4` (`src/driver/scrip.c`), baked into mode-4 binaries beside the other three switches by `emit_compat_bake_data`/`emit_compat_bake_code` (the module-init `setenv` sequence), and `rt_ipow_promote_descr` (`src/runtime/arithmetic.c`) returns `INTVAL(0)` for a negative exponent with a non-zero integer base when the switch is set. The existing integer arm `rt_ipow_descr` (BINOP_POW) was NOT reused: it returns 1 for `1 ^ -n` and ±1 for `(-1) ^ -n`, which csnobol4 does not. No new global; the switch is read with `getenv` on the negative-exponent path only.

**Control arms.** The default-dialect witness is byte-identical before and after (SPITBOL's reals). `pow.sno` matches its ref in m3 and m4 after the cure, re-proven after two rebases. `strip_comments.py --check` 0 offenders.

**Boards on the cured tree** (`5c308ad6f` + the cure, corpus `7fba27c82`, RT_OPT=-O0, incremental make, 16:04 CDT): csnobol4 board `total=120 m3_PASS=68 m3_FAIL=21 m3_REJECT=30 m3_CRASH=1 · m4 identical` — `pow` no longer among the RED-M lines (the DONE-WHEN); SNOBOL4 master m3 1854/1855 · m4 1854/1855, the one red `user_function_keyword_branch_3` = THE INHERITED SET (hq_P's fnclevel row; `bal_arb_keyword_branch_1` was cured on origin by hq_U's `5637f0a3b` meanwhile). The computed `done` re-runs the csnobol4 board on the clean pushed tree and rewrites the SCORE row.

**Residual, named not cured.** `0 ^ -n` under the switch stays on the SPITBOL path (`0.`) where csnobol4 raises Error 2. No program in the csnobol4 pool exercises it; a cure needs the csnobol4 error-number mapping, which is a class of its own.

**The transferable half.** A dialect switch that "ADDS CSNOBOL4-only behaviour" must be checked per BEHAVIOUR: three switches existed (SETEXIT on end, legacy I/O association, real formatting) and integer power was a fourth behaviour nobody had measured. The cheap way to find the next one is the pool file: every csnobol4 FAIL whose diff is one line is a candidate dialect behaviour, and the oracle table above is the shape of the proof.
