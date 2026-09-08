# FINDING 2026-09-07 (cto, MODE EXECUTIVE) — Lon ruled a newline is NOT a semicolon in SCRIP Icon; the lexer gap I filled was the design, and the large-integer row landed with Icon `&trace`

Row: `icon-arizona-jcon-class-large-integers-and-numeric-overflow` (ceo, rank 0, ASSIGNED:cto). DONE-WHEN: lgint, large, radix, checkfpc, overflow, mega, tprintf, arith match their `.std` in both modes through `test_icon_arizona_suite.sh`, Icon master no worse.

## The ruling, and what I had done before it

While curing the row I found that `icn_lex_next` (`src/parsers/icon/icon_lex.c`) has never inserted a semicolon at a newline (a shell since `713c581b4`), that the parser's expression-statement rule requires `;` unless the previous token is `}`, and that the lexer test at `icon_lex_test.c:353` asserts NO semicolon for `"1\n2"`. Every Arizona, ladder and corpus Icon program is written with `;`. I implemented Icon's Beginner/Ender newline rule and flipped the test. **Lon 2026-09-07 13:4x CDT, verbatim: "Ensure that SCRIP does NOT accept new-lines as replacements for semi-colon."** Reverted before landing: `icn_lex_next`, the `IcnLexer` fields and the test are HEAD's text again; a newline-terminated program is refused with `expression statement: expected ;` as before. The witness `scratchpad/big/r1.icn` (`write(1)` newline `write(2)`) is the refusal's proof. The parser's line-stamping of body and brace statements (needed by `&trace`) stays; it is not a terminator rule.

## What else the row needed (each with its witness under `scratchpad/big/`)

- Scan under assignment: `t := move(-4)` did not restore `&pos` on backtrack — `icn_tree_is_cursor_mover` did not see through `TT_ASSIGN` (`lower_icon.c`); d3 (8 shapes) and mega's `_003F` hex underscore.
- `ishift` by ±64 and beyond: x86 masks the count; saturate (arith line 58).
- `ishift` with string operands: coerce through `rt_bitop_operand` (large).
- Bitwise ops on a real: `big_route_operand` now truncates DT_R (lgint `&|!`).
- Real-vs-big comparison value: `rt_relop_val_coerce` tests real-ness before bigness (lgint `compares(5.0, big)`).
- Real base, integer exponent: Icon's `ripow` (square-and-multiply), not `pow()`; `pow(10,23)` from glibc is one ulp high of the correctly rounded value and iconx never calls it there. Three sites: `POWER_fn`, `rt_num_arith_impl` (POW and POW_PROMOTE), the compile-time fold in `lower_icon.c`. The emitter pre-coerced the exponent to a double through `IR_COERCE_NUMERIC`; new code bit `COERCE_KEEP_INT` (descr.h) honoured in `c_rt_coerce_num2_d` AND its asm twin `rtx_icnnum.s` (which bails to C on that bit). tprintf's `%.3f` of 1e23 row.
- `big || string`: `str_concat_fracdigit_d` stringifies DT_BIG (large's `2^100 || ":"`).
- Icon `&trace` (large's call/fail lines): the runtime already had SNOBOL4's TRACE table; Icon's setter (`rt_keyword_trace_set`) now registers a wildcard `*` entry tagged `icn`, `rt_trace_event_args` falls back to it and prints iconx's `showline`/`showlevel` format on stderr (stdout flushed first); taps: the Icon procedure prologue (after the `&level` increment, args read from the carved frame at `rsp`), the zframe γ/ω epilogues, and the root graph's two exits (`main failed`). Line numbers: `ICN$LINE` hook (new builtin id, table entry hand-inserted in `builtin_ids.h` at djb2 slot 395 — the generator only reads `strcmp` sites and cannot run on today's file) emitted per statement, per brace-block element and at each procedure's `end` line ONLY when the program mentions `&trace` (tree scan); the parser now stamps a line on body and brace statements and the `end` line into `TT_PROC_DECL.slen`. `&file` is the source path (driver sets it for every frontend). Template guards on `g_trace` were `jle` (SNOBOL's ≤0 = off); Icon's `-1` needs `je`.

## Measured

- The eight: PASS both modes, `IPATH=$SUITE` (the ceo's DONE-WHEN line lacks IPATH; tprintf/mega link printf/hexcvt).
- Arizona board, this tree (1dcc65cae-dirty, scouting datum): m3 61/90, m4 61/90; the last clean stamp f0101614c reads 60/90 both modes.
- Icon master: 705/705 both modes (no worse). Six smokes green. `strip_comments.py --check`: 0.
- `make test` and the gimpel board were SIGTERM'd mid-run at 13:20 by something outside the chain; re-run pending, then merge onto origin/main (six commits ahead of my base) and re-measure before push.

## Residuals (named)

- Icon trace through the C call path (`rt.c` slim/APPLY) prints one bar fewer (level counted before the increment there); `suspended`/`resumed` events not emitted.
- A string-literal vs real-literal compare as the MIDDLE argument of a three-argument call reads a wrong spine slot (witness d9: `write("[", ("2" = 2.0), "]")` raises 102; every other shape passes). Emitter slot accounting; not in the eight.

## Landed (2026-09-08 17:5x CDT, cto)

SCRIP `51cbcf5db` (the class) and `3bb0a210c` (the runner) on origin/main, rebased twice on the way: onto the ceo's one-oracle `19162985f` (two conflicts -- `rt_ipow_promote_descr` keeps the overflow-promoting loop and drops the retired `SCRIP_IPOW_CSNOBOL4` line; `rt_trace_event_args` keeps the ceo's `&FTRACE` arm but its new `g_trace <= 0` guard became `== 0`, because Icon's `&trace := -1` is the ON value and the `icn`-tag guard below it already covers SNOBOL4's negative case) and onto `b2660262e` (clean, scripts only).

**The runner half.** `large` read red under `test_icon_arizona_suite.sh` while passing the DONE-WHEN: `&file` is the source path AS GIVEN -- measured against icont 9.5.25a, the bare, `sub/` and absolute forms print `large.icn    :`, `sub/large.icn:`, `ral/large.icn:` in the `&trace` column, and SCRIP prints the same three -- and the runner handed scrip an absolute path where the `.std` files were cut with the bare name from inside the suite directory (the runner already `cd`s there). Both mode arms now pass `$name.icn`. Arizona 68 -> 69/90.

**Verdict on the pushed tree** (RT_OPT -O0, incremental make): DONE-WHEN `PASS: 8 Arizona programs match their .std in both modes`; Arizona m3 69/90 m4 69/90 (clean origin stamp `b7f48462a` 62/90; the row write waits for the corpus landing); Icon master 705/705 both modes; SNOBOL4 master 1858/1858 both modes; `make test` green to the ceo's named standing red (`test_gate_pl_meta_call_reaches_control_constructs.sh`, 2 of 23, red on origin without this change) and the 15 arms after it green by hand including `board_icon_master.sh`; seven per-language smokes green; `strip_comments.py --check` 0; the newline witness `r1.icn` still refuses with `expression statement: expected ;`.

**Lon's words this sitting, routed:** *"We are in EXECUTIVE mode, 4 officers, CEO, CTO, CFO, and COO."* (the cto digest corrected from three). *"Has the SPITBOL verified test sources been segregated from the SNOBOL4 specific one so that our score board reflect proper reality? If not make it so, number one."* and *"So, did you regrade each SNOBOL4 program with CSNOBOL4, Snoflake, and SPITBOL to properly mark the database of test suite programs?"* -- the answer to the second is NO, nobody had; `scripts/util_snobol4_oracle_census.sh` (next landing) runs every standalone SNOBOL4 program through sbl -bf and CSNOBOL4 and writes `ORACLE_ACCEPTANCE.tsv` beside each package; Snoflake is NOT installed under /home/resources, so its column reads NO_ORACLE until Lon says where it comes from.

**The census, first run (2026-09-08 17:5x CDT, `util_snobol4_oracle_census.sh`, sbl -bf and CSNOBOL4 2.3.3, Snoflake NO_ORACLE), one line per package; OK means compiled and ran to rc=0, never a compared output -- a program refused standalone is a fact about the program (a -INCLUDE library member, a driver wanting argv, a dialect) that the package inventory must name:**

```
ORACLE_ACCEPTANCE package=aisnobol n=10 sbl_ok=8 csnobol4_ok=5 both=5 sbl_only=3 csnobol4_only=0 neither=2 snoflake=NO_ORACLE
ORACLE_ACCEPTANCE package=csnobol4_suite n=130 sbl_ok=96 csnobol4_ok=113 both=93 sbl_only=3 csnobol4_only=20 neither=14 snoflake=NO_ORACLE
ORACLE_ACCEPTANCE package=dotnet n=14 sbl_ok=9 csnobol4_ok=7 both=5 sbl_only=4 csnobol4_only=2 neither=3 snoflake=NO_ORACLE
ORACLE_ACCEPTANCE package=gimpel n=290 sbl_ok=152 csnobol4_ok=136 both=136 sbl_only=16 csnobol4_only=0 neither=138 snoflake=NO_ORACLE
ORACLE_ACCEPTANCE package=snoflake_suite n=180 sbl_ok=124 csnobol4_ok=119 both=115 sbl_only=9 csnobol4_only=4 neither=52 snoflake=NO_ORACLE
ORACLE_ACCEPTANCE package=spitbol_testpgms n=8 sbl_ok=7 csnobol4_ok=7 both=6 sbl_only=1 csnobol4_only=1 neither=0 snoflake=NO_ORACLE
ORACLE_ACCEPTANCE package=snobol4 n=135 sbl_ok=107 csnobol4_ok=62 both=58 sbl_only=49 csnobol4_only=4 neither=24 snoflake=NO_ORACLE
```

Cross-check of the Budne package against its inventories: every program SPITBOL refuses is now named in `OUTSIDE_SPITBOL_BASELINE.tsv` (the 23 of 09-07, keytrace on the ceo's word, and alis, scanerr, genc by the same class -- their sbl-cut refs were fatal listings), and no program named outside reads OK under sbl.
