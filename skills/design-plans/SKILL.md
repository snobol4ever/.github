---
name: design-plans
description: How a design is written and stepped through: the DESIGN-PLAN (numbered steps, witnesses with oracle-cut refs under corpus/tests/<lang>/<design>/, a STEPS.tsv, a test_design_<name>_steps.sh with --list, --step N, --cut), one row per step whose DONE-WHEN is the literal --step N, the executor's duties, and where each live plan's design text lives (the owning skill's DESIGN section). Load it before writing, stepping, minting or closing a design step, or answering a design ask.
---

# Design plans

A design is the cto's (CEO-2025/2029/2067; Lon 2026-10-28: the cto is the fleet's design brain). It lands as a DESIGN-PLAN: numbered steps, each with an executor, a probe and witnesses, in a table a harness reads. The design text lives in the DESIGN section of the skill that owns the layer (the ARCH pages it lived on are retired, CEO-2115); the steps live in the table; the work lives in one row per step.

## 1. The parts of a plan

- **The witnesses**: small programs under `corpus/tests/<lang>/<design>/` (or `corpus/tests/shared/<design>/` for a cross-language plan), each beside a `.ref` cut from the language's oracle (SPITBOL `sbl -bf`, Arizona Icon, swipl, XSB, fpc `-Miso`, Rakudo), never from our output.
- **`STEPS.tsv`** beside them: a `#` header naming the plan, the ruling numbers, the harness and the probe-token vocabulary, then one row per step: `step slug executor depends probe witnesses`, and in most plans `ruling landing_files`. A step's `depends` names the steps it waits on.
- **`harness/scripts/test_design_<name>_steps.sh`**: `--list` prints the table; `--step N` grades step N's witnesses in both modes (some plans also under `SCRIP_GC_STRESS=1`) and then its probe tokens; `--cut` re-cuts every ref from its oracle; some plans add `--rows0` (record SUITES.tsv's rows for a `rows=` probe) and `--out DIR`.
- **The probe tokens are each harness's own** (read the `#` header of its table): for example `gate=NAME`, `smoke=L|ALL`, `nosym=a,b`, `sym=`, `nofile=`, `grepmax=REGEX@REL:N`, `tsvmin=FILE:N`, `rule5=N`, `rspmoves=N`, `layoutcheck=N`, `rows=`, `entries=e1,e2`, `census=`, `kind=`.

## 2. The rows

- One row per step, minted by the cto or the coo: `<plan>-step-<N>-<slug>-<ceo-number>`, owner the step's executor, `DONE-WHEN: cd "${S4E_HOME:?}" && bash harness/scripts/test_design_<name>_steps.sh --step N`, `PREMISE-WHEN` that the table names the step and the step reads red (CEO-2016).
- Executors follow the lanes (CEO-1996); the cfo takes a step an HQ cannot; a step that founders escalates to the officer named, and a design gap comes to the cto by telegram, answered in the skill's DESIGN section the same sitting.
- **An entry the step alone does not flip moves to the row that does** (CEO-2112): a step closes on its own probe; an entry that needs other work leaves its `entries=` list in the same landing, citing the ruling, and a row for that work is minted.
- Step 0 of a plan is the baseline: the witnesses and probes read today, recorded so every later step is a measured move.

## 3. Writing a plan (the cto)

1. Measure first: the population the plan serves, read from `results.tsv` or the tree, with the tree named.
2. Write the rulings the plan is under (Lon's words verbatim, the CEO numbers) and the design in the owning skill's DESIGN section.
3. Cut the witnesses from the oracle (`--cut`, or `util_add_ladder_witness.py` for a rung); each red today at its named class.
4. Write `STEPS.tsv` and the harness; prove every probe token fail-once and pass-once (CEO-1680).
5. Mint the step rows; telegram the executors; record the plan in `GOAL-CEO.md`'s cursor.

## 4. The live plans and where their design text lives

| plan | table | harness | design text |
|---|---|---|---|
| builtin-table | `corpus/tests/shared/builtin_table/` | `test_design_builtin_table_steps.sh` | skill `runtime-calls` DESIGN |
| exceptions | `corpus/tests/shared/exceptions/` | `test_design_exceptions_steps.sh` | skill `runtime-calls` DESIGN |
| zeta-layout | `corpus/tests/shared/zeta_layout/` | `test_design_zeta_layout_steps.sh` | skill `scrip-memory-model` DESIGN |
| planner-finish | `corpus/tests/snobol4/planner_finish/` | `test_design_planner_finish_steps.sh` | skill `scrip-memory-model` DESIGN |
| templates-zero | `corpus/tests/shared/templates_zero/` | `test_design_templates_zero_steps.sh` | skill `box-templates` DESIGN |
| prolog-lifo | `corpus/tests/prolog/lifo/` | `test_design_prolog_lifo_steps.sh` | skill `prolog-engine` DESIGN |
| xsb-tabling-wfs | `corpus/tests/prolog/xsb_wfs/` | `test_design_xsb_tabling_wfs_steps.sh` | skill `prolog-tabling` DESIGN |
| clpr-chr | `corpus/tests/prolog/clpr_chr/` | `test_design_clpr_chr_steps.sh` | skill `prolog-constraints` DESIGN |
| consulted-clause-source-record | `corpus/tests/prolog/clause_source_record/` | `test_design_clause_source_record_steps.sh` | skill `prolog` DESIGN |
| icon-scanning-asm | `corpus/tests/icon/scanning_asm/` | `test_design_icon_scanning_asm_steps.sh` | skill `icon` DESIGN |
| unicon | `corpus/tests/icon/unicon/` (steps 1-5 the surface, 6-16 UniTests to 100) | `test_design_unicon_steps.sh` | skill `unicon` sections 1-2 and 7 |
| random-codegen-scope | `corpus/demos/scriptix/infinite_snobol4/` (with `COVERAGE.tsv`) | `test_design_random_codegen_scope_steps.sh` | skill `snobol4` DESIGN |
| pascal-front-end | `corpus/tests/pascal/front_end/` | `test_design_pascal_front_end_steps.sh` | skill `pascal` DESIGN |
| raku-rewrite, raku-to-100 | `corpus/tests/raku/rewrite/`, `corpus/tests/raku/config/LADDER.tsv` | `test_design_raku_rewrite_steps.sh`, `test_raku_ladder.sh` | skill `raku` DESIGN |
| header-split | `.github/scripts/headers/` | the header ratchet gates | skill `scrip-build` DESIGN |
| shared-development | the step rows `shared-dev-step-*` | `util_seat_census.py` | skill `shared-box` |
