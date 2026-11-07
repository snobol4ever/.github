---
name: raku
description: SCRIP's Raku (rakudo 2026.05 the oracle, the roast the spec): src/parsers/raku, lower_raku.c, the setting and kernel boxes, the Seq pull protocol, the RakRungs, Roast, RakBench suites. REQUIRED by the skill gate before editing the Raku fron
---

# SCRIP Raku

The record is GOAL-RAKU-100.md (LIVE CURSOR on top); the design is `reference.md` § 8. Raku builds at rank 9 (CEO-1931) and climbs the cto's rung ladder, not the suites, until half the rungs are green (CEO-2070). Suite tables, file maps and receipts in full are in `reference.md` beside this file.

## 1. The oracle

- **rakudo 2026.05; the spec is the roast** (`/home/resources/roast-master`). The binary through `rakudo_bin()` in `harness/scripts/lib_oracle_flags.sh`; the `raku` on PATH (2022.12) is never the oracle. One dialect, no switch.
- A ref is cut from rakudo; a ref cut from our output is a SELF-PIN, not an oracle; no XFAIL. Refusal, crash or hang (`timeout -k 5`) is `NO_ORACLE_ANSWER` (CEO-1696); an implementation accident is no answer (CEO-1934). Gotchas: `OUTER` is a pseudo-package, a mid-line `}` needs `;`, EVAL of a string needs `MONKEY-SEE-NO-EVAL`.
- Interim (the re-design's layer (c), `reference.md` § 8): the program's own names win; a lib-path export does not beat the setting until F05's typed multi dispatch lands.
- Test is Rakudo's `src/parsers/raku/setting/Test.rakumod`, vendored as the setting's first file.

## 2. The manuals

`/home/resources/manuals/raku/` (Rakudo 2026.05 docs, the NQP 6model and ops docs); the roast `S*/` directories (`ROAST-RUNG-MAP.tsv` maps each file to its rung); Rakudo's `src/Perl6/Grammar.nqp` and `src/core.c/*.rakumod` under `/home/resources/rakudo-2026.05/`. Before ruling: grep the setting source, then run `rakudo_bin -e '...'` on a three-line probe.

## 3. The source map

- Parser `src/parsers/raku/`: `rk_syntax.c` (the recognizer translated from Grammar.nqp), `rk_tree.c`, `rk_regex.c`, generated `rk_core_names.inc` and `raku_setting.inc` (from `setting/*.rakumod`), `raku_driver.c`; the bootstrap `parser_raku.sc`.
- Lowering `src/lower/lower_raku.c`: every construct to the kernel boxes (`bb_rk_coerce`, `bb_rk_scalar`, `bb_rk_aggr`, `bb_rk_iter`, `bb_rk_sig`, `bb_rk_dispatch`, `bb_rk_smartmatch`, `bb_rk_junction`, and the rest; the regex boxes `bb_match_rk*`) and the shared boxes.
- Runtime: `rk_rat.c`, `bignum.c`, the generated case and Unicode tables, `rx.c` (retiring), the `rtx_rk_*` leaves.
- `--dump-ast|--dump-ir|--dump-plan prog.raku`; `--syntax` for the recognizer alone.

## 4. The related skills

`lowering`, `box-templates`, `scrip-memory-model` (the cell kinds, `box_cell_shapes.tsv`), `runtime-calls` (the builtin table's Raku step, the error protocol for die, try and CATCH), `icon` (the generator and suspend road Raku reuses), `snocone-parser-patterns` (`parser_raku.sc`). The re-design, the ladder and the rewrite are in `reference.md` § 8-9.

## 5. The suites

- Keys and runners in `harness/scripts/`: `raku-rungs` (`test_raku_ladder.sh --list|--to N|--only N`), `roast` (`raku_roast_scoreboard.sh`), `raku-bench-ref`, `raku-demos`.
- One program: `corpus_suite_harness.py run ../corpus/tests/raku/ALL.raku ../corpus/tests/raku/ALL.ref --lang raku --modes m3,m4 --partition entry:<name>`. The master is a container.
- A rung: at most 20 lines, one construct, ref cut from rakudo, red once on the base binary (`util_add_ladder_witness.py`); rung N+1 opens when N is green in both modes; `util_raku_ladder_status.py` reads the ladder.
- Per landing: the DONE-WHEN, `test_feature_reps.sh raku <feature>`, `test_smoke_raku.sh`; then `s4e_test_request.sh` for the coo. Speed is CLOSED for Raku (CEO-1914).

## 6. Debugging a red

1. `bash ../harness/scripts/monitor_run.sh prog.raku --oracle` (the rakudo-mon fork); never a Raku-private monitor.
2. Asm-diff the smallest repro beside a passing sibling within one mode.
3. Parse questions: `util_raku_syntax_agreement.py` (scrip `--syntax` against `raku -c`); roast reds ranked by `util_raku_roast_ablation_ranker.sh`.
4. gdb last, with a breakpoint and a hit count.

## 7. Rulings a landing must not break

- Every Raku value is ONE DESCR; a lexical's slot holds its value; `:=` in one scope is a compile-time alias; a run-time binding holds a REF to a heap Scalar, dereferenced in the box, never in C.
- One four-port pull protocol, Icon's generator pump; no second iterator machinery.
- The setting is Raku: a core method is written in Raku and its C body deleted in the same landing; no leaf that calls a box or loops over user code (CEO-1576).
- Never lower a construct to a C function by name, add an `IR_CALL <name>`, a `strcmp` chain or by-name table, or a desugar in `rk_tree.c`/`rk_syntax.c` (§ 10).
- The parser reaches 100% first; the recognizer is translated from Rakudo's grammar.
- A kernel box is born with its family's first rung; a Roast file is cured by its rung, never by its name; RakRungs and RakBench never fall below 100 at a landing.
- S17 (concurrency) stays closed until Lon opens it. No global, side table, frame marker, second stack or fixed limit; the Raku smoke before every push (all eight for shared code).

## 8. DESIGN: Roast to 100, the triage framework and four rulings (CTO-514, 2026-11-05; the cao triages every red under this frame, hq_raku lands, the coo grades)

The full text of this section (about 10 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

## 9. DESIGN-PLAN raku-core: the core prelude in Raku and the C roads into user code deleted (CTO-517, 2026-11-05; hq_raku lands, the coo grades)

The full text of this section (about 4 KB) is in `reference.md` beside this file, under the same heading, moved there verbatim on 2026-11-06 so the skill loads light (Lon: "Go and trim any skill that needs it."). Read it before executing, cutting or ruling on a step of this design.

