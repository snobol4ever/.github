# FINDING 2026-09-30 — parser_prolog.sc tree-identical to the C parser on all 522 corpus files, the C brought to the plain tree, three C defects cured on the way

**Author:** cto (Fable 5.1), 2026-09-30 19:1x CDT (`date`-read), MODE QUARTET (CEO-1380). **Cursor:** GOAL-CTO.md CTO-212 carries the measured claims; this file holds the evidence. **Law:** RULES.md § FACT RULE — THE TREE IS THE ONE THE PATTERN BUILDS IN ORDER, WITH RAW SHIFT AND REDUCE ALONE (CEO-1378). Row `parser-sc-all-seven-to-the-c-tree` (rank 0, cto). Landing SCRIP `b1cde82b2`; corpus `7b5efc0c6` (the seven parser demos) and `5e13b5785` (the Prolog benchmark `.s`).

## 1. The reading

| instrument | population | the shelf (`cto/prolog-term-tree-wip`, 18:0x) | this landing |
|---|---|---|---|
| `util_parser_sc_grade.sh prolog` (C dumps one process per file, from each file's directory) | 522 corpus `.pl` | 520 match; test_locale.pl differs, test_arith.pl refused by the .sc | **522 match, 0 diff, 0 one-sided, 0 crash** |
| tree gate, `GATE_LANGS=prolog GATE_POPULATION=corpus` (hash mode, default window) | 522 | RED: 455 MATCH, 1 DIFF, 1 refused by the .sc, 1 .sc crash (sendmore.pl), 64 refused by both | **MATCH: 458 hashes compared, 458 MATCH, 64 refused by both, 0 one-sided, 0 crash** |
| tree gate, the other arms | snobol4 793, rebus 6, icon 1715, snocone 108, pascal 1071 | — | snobol4 MATCH 728, rebus MATCH 6, icon 1579 of 1671 (unchanged), snocone 0 of 98 and pascal 0 of 517 (unchanged) |

The 64 refused by both are C coverage gaps — 33 `packages/prolog/swi_tests`, 25 `packages/prolog/gnu_fd` (constraint syntax), 4 `benchmarks/prolog/src`, 1 logtalk_iso, 1 rung10 — agreement by the gate's rule, not trees.

## 2. The shelf's 141 reds did not reproduce

CTO-211 shelved the branch because the Prolog area smoke read 141 m3 FAIL and m4 SKIP in tests/prolog. Rebased onto `fef61c805` and rebuilt, the same branch read 563 of 563 in both modes, and again after every cure below and after the rebase onto `d6c9fc2f2`. An m4 SKIP across a whole table is the shape of a missing or half-built runtime library during the run, not of a parser defect; no bisect was owed.

## 3. The three C defects (each found by a .sc disagreement, each cured at the source)

1. **A radix literal beyond 64 bits was converted to decimal in the lexer** (`lex_radix_to_decimal`, deleted). The plain tree carries the literal as written: `(TT_FNC $pl_big (TT_QLIT "-0b1000…"))`, group marks stripped as `span_text` strips them; `rt_pl_dop_big` reads an optional sign and a `0x`/`0o`/`0b` prefix through `rt_big_from_str_base`. Values equal swipl on seven witnesses (2^63 in binary, its negation, a 72-bit hex, a negative 75-bit octal, arithmetic on them).
2. **`1.5NaN` and `1.0Inf` read as 1.5 and 1.0**: `S_FRAC_END` built the token from the text before the suffix and took `atof` of it. It is NaN and infinity now, mode 3 and mode 4 identical; the C dump prints `nan`/`inf`/`-inf` as `%g` does and `tdump.sc` mirrors it. The runtime's handling of those values is still not SWI's (it writes `nan` where SWI writes `1.5NaN`; `max(1, nan)` and `1.5 == 1.5NaN` disagree; the float flags of test_ieee754 are absent) — the same on origin, and four package programs that use the syntax (test_arith, test_ieee754, test_rational, test_real) give the same verdicts on origin and here.
3. **`read/1` and `atom_to_term/3` of a big integer returned a `'$pl_big'(Digits)` compound**: `pl_tree_cell` (by_name_dispatch.c) built the parser's `$pl_big` node as a term. It now goes through `rt_pl_dop_big`; five witnesses equal swipl in both modes.

## 4. The grammar side

- `test_locale.pl`: the shared dumper printed `-0.0` as `0`; a TT_FLIT whose text is a negative zero prints `-0` (the ceo's word recorded at CTO-211).
- `test_arith.pl`, three constructs in turn (bisected by the shortest failing prefix ending at a clause end): `-0b1000…` (64 binary digits), `-0b10000000 00000000 …` (space-separated groups), `1.5NaN`. The first exposed the shape fault: `primary` is a fenced level that never retries a primary once one matched, so when the `0x…` alternative failed on overflow the decimal rule matched the bare `0` and the parse was lost. The radix forms are now their own rule (`RadixVal`) tried before `RadixBig` and the decimal `IntVal`.

## 5. The collector, met and not cured

On the shelf tree the chain's hash mode died on `sendmore.pl` at the shipped 1 MB window (SIGSEGV in `rt_call_name_sn4`; error 41 at 64 KB) and passed at 4 MB and above with zero collections — which is why the grader (`-i64m`) read it green. `SCRIP_GC_MAPS=1` met 1–2 ghost frame-map cells in the collections before each failure: the mechanism of the cfo's rank-0 row `collector-the-prolog-sc-chain-mode-4-dies-zgc-stale-on-three-files-first-bad-da1b3a85a`. On the landed tree the plain runs meet 0 ghosts and pass; under `SCRIP_GC_STRESS=1` sendmore meets 101, crypt 111, meta_qsort 163, test_body_index 76, all rc 0. The green prolog arm is the depth lottery until that row lands.

## 6. Verified with the landing

Preflight 68/0; strip_comments 0; allocating table FRESH (regenerated: the parser's new functions); C-allocator ratchet 8 of 8; 11 Prolog gates the diff touches green; the parser-demo drift gate green after `util_regen_parser_demos.sh --cut-refs` (only parser_prolog.ref changed); the 23 Prolog benchmarks equal their refs in mode 3 and from the regenerated `.s` in mode 4. Red on origin too and not this landing's: `test_gate_dyn_caps_ratchet` function-scope 408 vs 407 (red before `ae0a91289`; this landing returns the fixed-bound population to its baseline 262 by the if-stack cv_t), `test_gate_runtime_isolation` (exits 1 under `pipefail` when its grep finds no include at all), `test_gate_no_lang_names` 3827, `test_gate_pl_no_new_global` (the same list).
