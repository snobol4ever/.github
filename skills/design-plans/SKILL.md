---
name: design-plans
description: How a design is written and stepped: DESIGN-PLAN steps, witnesses, STEPS.tsv, test_design_<name>_steps.sh, one row per step, the live plans' table. REQUIRED by the skill gate before editing a step table or a step harness.
---

# Design plans

A design is the cto's for SCRIP and the suites (CEO-2025/2029/2067; Lon 2026-10-28: the cto is the fleet's design brain) and the cio's for the fleet system and the test cycle (COO-481, Lon 2026-11-07: "You, CIO, and CTO are the designers"). It lands as a DESIGN-PLAN: numbered steps, each with an executor, a probe and witnesses, in a table a harness reads. The design text lives in the DESIGN section of the skill that owns the layer (the ARCH pages it lived on are retired, CEO-2115); the steps live in the table; the work lives in one row per step.

## 1. The parts of a plan

- **The witnesses are ENTRIES OF THE LANGUAGE'S CONTAINER, never loose files** (CIO-24, 2026-11-10; Lon's law of 2026-08-29/30, corpus 11a36c87f: a language folder is flat, the container files and one `config/`, every program absorbed; Lon 2026-11-10: "Why are these folders not organized properly."): a small program added to `corpus/tests/<lang>/ALL.<ext>` with the plan's name in its `family` column, its answer cut from the language's oracle twice (SPITBOL `sbl -bf`, Arizona Icon, unicon, swipl, XSB, fpc `-Miso`, Rakudo), never from our output, so the cycle grades it every lap and its suite row counts it. This page told designers until 2026-11-10 to make a folder `corpus/tests/<lang>/<design>/` of loose pairs; `util_tests_layout_census.py` measured 365 such pairs no cell grades, and no new one is made. The folders that stand are absorbed under CIO-24's rows; a plan whose folder still stands reads its witnesses there until its row lands.
- **`STEPS.tsv`** (for a new plan `harness/designs/<plan>/STEPS.tsv`: a step table is an instrument, not a test; the tables under `corpus/tests/` move there with their plan's absorption): a `#` header naming the plan, the ruling numbers, the harness and the probe-token vocabulary, then one row per step: `step slug executor depends probe witnesses`, and in most plans `ruling landing_files`. A step's `depends` names the steps it waits on.
- **`harness/scripts/test_design_<name>_steps.sh`**: `--list` prints the table; `--step N` grades step N's witnesses in both modes (some plans also under `SCRIP_GC_STRESS=1`) and then its probe tokens; `--cut` re-cuts every ref from its oracle; some plans add `--rows0` (record SUITES.tsv's rows for a `rows=` probe) and `--out DIR`.
- **The probe tokens are each harness's own** (read the `#` header of its table): for example `gate=NAME`, `smoke=L|ALL`, `nosym=a,b`, `sym=`, `nofile=`, `grepmax=REGEX@REL:N`, `tsvmin=FILE:N`, `rule5=N`, `rspmoves=N`, `layoutcheck=N`, `rows=`, `entries=e1,e2`, `census=`, `kind=`.

## 2. The rows

- One row per step, minted by the designer (the cto or the cio) or the coo: `<plan>-step-<N>-<slug>` (a ruling it answers is cited in the GOAL as CTO-NNNN or R-NNNN, never in the name), queued to tier-haiku or a worker's seat tube under THE HAIKU BAR (skill `fleet-bus` section 1), `DONE-WHEN: cd "${S4E_HOME:?}" && bash harness/scripts/test_design_<name>_steps.sh --step N`, `PREMISE-WHEN` that the table names the step and the step reads red (CEO-2016).
- Executors: the ladder of skill `fleet-bus` section 1 (COO-481): a step starts at a worker and climbs by escalation after one honest try; a design gap comes to the designer by telegram, answered in the skill's DESIGN section the same sitting.
- **An entry the step alone does not flip moves to the row that does** (CEO-2112): a step closes on its own probe; an entry that needs other work leaves its `entries=` list in the same landing, citing the ruling, and a row for that work is minted.
- Step 0 of a plan is the baseline: the witnesses and probes read today, recorded so every later step is a measured move.

## 3. Writing a plan (the cto)

1. Measure first: the population the plan serves, read from `results.tsv` or the tree, with the tree named.
2. Write the rulings the plan is under (Lon's words verbatim, the CEO numbers) and the design in the owning skill's DESIGN section.
3. Add the witnesses to the container, cut from the oracle (`util_add_ladder_witness.py`; a step names them as `entries=e1,e2` and the harness grades `--partition entry:<name>`); each red today at its named class.
4. Write `STEPS.tsv` and the harness; prove every probe token fail-once and pass-once (CEO-1680).
5. Mint the step rows; telegram the executors; record the plan in the designer's GOAL file (`GOAL-CTO.md` or `GOAL-CIO.md`) LIVE CURSOR.

## 4. The live plans and where their design text lives

A skill's DESIGN section in SKILL.md may be a two-line stub (since 2026-11-06, Lon: "Go and trim any skill that needs it."): the heading and its number stay, so every "section N" citation resolves, and the full text is in that skill's `reference.md` under the same heading. A design is written or amended there, never in the stub.

| plan | table | harness | design text |
|---|---|---|---|
| builtin-table | `corpus/tests/shared/builtin_table/` | `test_design_builtin_table_steps.sh` | skill `runtime-calls` DESIGN |
| exceptions | `corpus/tests/shared/exceptions/` | `test_design_exceptions_steps.sh` | skill `runtime-calls` DESIGN |
| zeta-layout | `corpus/tests/shared/zeta_layout/` | `test_design_zeta_layout_steps.sh` | skill `scrip-memory-model` DESIGN |
| planner-finish | `harness/designs/planner_finish/STEPS.tsv` (witnesses: snobol4 entries `planner_finish__*` of its master; icon, pascal, prolog loose until their rows absorb them) | `test_design_planner_finish_steps.sh` | skill `scrip-memory-model` DESIGN |
| templates-zero | `harness/designs/templates_zero/` | `test_design_templates_zero_steps.sh` | skill `box-templates` DESIGN |
| prolog-lifo | `corpus/tests/prolog/lifo/` | `test_design_prolog_lifo_steps.sh` | skill `prolog-engine` DESIGN |
| xsb-tabling-wfs | `corpus/tests/prolog/xsb_wfs/` | `test_design_xsb_tabling_wfs_steps.sh` | skill `prolog-tabling` DESIGN |
| tabling-one-engine | `harness/designs/tabling_one_engine/STEPS.tsv` (witnesses: prolog entries `one_engine__*` of its master) | `test_design_tabling_one_engine_steps.sh` | skill `prolog-tabling` section 5 (reference) |
| clpr-chr | `corpus/tests/prolog/clpr_chr/` | `test_design_clpr_chr_steps.sh` | skill `prolog-constraints` DESIGN |
| consulted-clause-source-record | `corpus/tests/prolog/clause_source_record/` | `test_design_clause_source_record_steps.sh` | skill `prolog` DESIGN |
| prolog-gnu-gaps | `harness/designs/prolog_gnu_gaps/STEPS.tsv` (witnesses: prolog entries `gnu_gaps__*`, dialect `gnu`; `gg_listing_0` loose) | `test_design_prolog_gnu_gaps_steps.sh` | skill `prolog` reference section 8 |
| icon-scanning-asm | `corpus/tests/icon/scanning_asm/` | `test_design_icon_scanning_asm_steps.sh` | skill `icon` DESIGN |
| unicon | `harness/designs/unicon/` (steps 1-5 the surface, 6-16 UniTests to 100; its witnesses entries `unicon__<name>` of the icon master, the six package ones in `harness/fixtures/unicon/` until the oracle cuts a multi-file package) | `test_design_unicon_steps.sh` | skill `unicon` sections 1-2 and 7 |
| random-codegen-scope | `corpus/demos/scriptix/infinite_snobol4/` (with `COVERAGE.tsv`) | `test_design_random_codegen_scope_steps.sh` | skill `snobol4` DESIGN |
| pascal-front-end | `corpus/tests/pascal/front_end/` | `test_design_pascal_front_end_steps.sh` | skill `pascal` DESIGN |
| raku-rewrite, raku-to-100 | `corpus/tests/raku/rewrite/`, `corpus/tests/raku/LADDER.tsv` | `test_design_raku_rewrite_steps.sh`, `test_raku_ladder.sh` | skill `raku` DESIGN |
| shared-development | the step rows `shared-dev-step-*` | `util_seat_census.py` | skill `shared-box` |
| batch-grader | `corpus/tests/shared/batch_grader/` | `test_design_batch_grader_steps.sh` | skill `suites-and-grading` section 5 |
| fleet-control | `harness/designs/fleet_control/` | `test_design_fleet_control_steps.sh` | skill `shared-box` section 9 (supersedes box-scheduler, fleet-queue, test-cycle, box-budget, shared-development, batch-grader) |
| test-cycle | `harness/designs/test_cycle/` | `test_design_test_cycle_steps.sh` | skill `suites-and-grading` section 7 |
| box-budget | `harness/designs/box_budget/` | `test_design_box_budget_steps.sh` | skill `shared-box` section 7 |
| box-scheduler | `harness/designs/box_scheduler/` | `test_design_box_scheduler_steps.sh` | skill `shared-box` section 8 |
| fleet-queue | `harness/designs/fleet_queue/` | `test_design_fleet_queue_steps.sh` | skill `fleet-bus` section 8 (reference) |
| skills-complete | `harness/designs/skills_complete/` | `test_design_skills_complete_steps.sh` | skill `fleet-bus` section 9 (reference) |
| run-switches | `harness/designs/run_switches/` | `test_design_run_switches_steps.sh` (probes `s4e_probe_run_switches.sh N`) | skill `suites-and-grading` section 8 (reference) |
| bus-one-queue | `harness/designs/bus_one_queue/` | `test_design_bus_one_queue_steps.sh` (probes `s4e_probe_bus_one_queue.sh N`) | the step table header (CIO-8 phase two, the cio; cut by officer_05; GOAL-CIO.md CIO-8 to CIO-10) |
