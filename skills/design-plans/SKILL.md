---
name: design-plans
description: How a design is written and stepped: DESIGN-PLAN steps, witnesses, STEPS.tsv, test_design_<name>_steps.sh, one row per step, the live plans' table. REQUIRED by the skill gate before editing a step table or a step harness.
---

# Design plans

A design is the cto's for SCRIP and the suites (CEO-2025/2029/2067; Lon 2026-10-28: the cto is the fleet's design brain) and the cio's for the fleet system and the test cycle (COO-481, Lon 2026-11-07: "You, CIO, and CTO are the designers"). It lands as a DESIGN-PLAN: numbered steps, each with an executor, a probe and witnesses, in a table a harness reads. The design text lives in the DESIGN section of the skill that owns the layer (the ARCH pages it lived on are retired, CEO-2115); the steps live in the table; the work lives in one row per step.

## 0. A design is finished before it leaves its designer (Lon 2026-11-13 10:0x CST, in the cto's window, verbatim: "let's do all as you suggest.")

Lon asked how the fleet gets finished, high-quality designs. MEASURED by the cto that hour (`QUEUE.tsv`, the batons): 163 live rows, 13 of them steps of a plan (4 plans), 11 that handed the design itself to a tier ("measured and cut into rows"), the rest one red a row with no design. The cto proposed four changes and Lon's word above is the go on all four. Two live here; the regression bisect is skill `fleet-bus` section 1 and the layer shapes are skill `fleet-bus` section 7.

- **THE BAR.** No row of a design goes down until its designer has: (a) the ruling and the design text in the owning skill's DESIGN section; (b) one witness program per step, its answer cut from the oracle, red today on origin at its named class; (c) the file and the function each step changes, named in the step's row; (d) the proof commands the executor runs. A row that fails the bar is the designer's own row, not a tier's.
- **The designer measures.** A row whose work is to measure a population and cut it into rows is design, and it is never queued to a tier. The ten such rows of 2026-11-13 went back to the cto's tube the same hour.
- **A witness joins the container in its cure's landing.** A red entry is a work order: the coo's feeder deals it to a junior as a point cure that collides with the design. Until the cure lands the witness stands in the step's row and the plan's fixtures.
- **An officer may draft a design for one cause class.** A Fable seat (the cto, the cio, the cfo) reads it against the bar before its rows are minted.
- **Designs are chosen by cause class, the largest first.** The census of a suite's reds by cause (`/home/resources/progress/causes-2026-11-13/cause_census.py`: each red rerun once, classed by its first error line) names the classes; one design serves one class, and the class's bug rows park `BLOCKED-ON:` the design's step so no junior chases its members one at a time. A cluster of reds with the same empty-output fingerprint is not one cause (915 alike in fpc-source were about 300 causes).
- **A top-rung escalation to a Fable seat returns a ruling and a row to build**, written in the skill the same sitting; the seat builds the cure itself only when it is a few lines.

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
| builtin-table | `harness/designs/builtin_table/STEPS.tsv` (witnesses: the entries `builtin_table__*` of each language's master) | `test_design_builtin_table_steps.sh` | skill `runtime-calls` DESIGN |
| exceptions | `harness/designs/exceptions/STEPS.tsv` (witnesses: the entries `exceptions__*` of each language's master) | `test_design_exceptions_steps.sh` | skill `runtime-calls` DESIGN |
| zeta-layout | `harness/designs/zeta_layout/STEPS.tsv` (witnesses: the entries `zeta_layout__*` of each language's master) | `test_design_zeta_layout_steps.sh` | skill `scrip-memory-model` DESIGN |
| planner-finish | `harness/designs/planner_finish/STEPS.tsv` (witnesses: the entries `planner_finish__*` of each language's master) | `test_design_planner_finish_steps.sh` | skill `scrip-memory-model` DESIGN |
| templates-zero | `harness/designs/templates_zero/` | `test_design_templates_zero_steps.sh` | skill `box-templates` DESIGN |
| prolog-lifo | `harness/designs/prolog_lifo/STEPS.tsv` (witnesses: prolog entries `lifo__*`) | `test_design_prolog_lifo_steps.sh` | skill `prolog-engine` DESIGN |
| xsb-tabling-wfs | `harness/designs/xsb_tabling_wfs/STEPS.tsv` (witnesses: `corpus/packages/prolog/xsb_witnesses/xsb_wfs/`) | `test_design_xsb_tabling_wfs_steps.sh` | skill `prolog-tabling` DESIGN |
| tabling-one-engine | `harness/designs/tabling_one_engine/STEPS.tsv` (witnesses: prolog entries `one_engine__*` of its master) | `test_design_tabling_one_engine_steps.sh` | skill `prolog-tabling` section 5 (reference) |
| clpr-chr | `harness/designs/clpr_chr/STEPS.tsv` (witnesses: prolog entries `clpr_chr__*`) | `test_design_clpr_chr_steps.sh` | skill `prolog-constraints` DESIGN |
| consulted-clause-source-record | `harness/designs/clause_source_record/STEPS.tsv` (witnesses: prolog entries `clause_source_record__*`) | `test_design_clause_source_record_steps.sh` | skill `prolog` DESIGN |
| prolog-gnu-gaps | `harness/designs/prolog_gnu_gaps/STEPS.tsv` (witnesses: prolog entries `gnu_gaps__*`, dialect `gnu`; `gg_listing_0` the fixture `harness/fixtures/prolog_gnu_gaps/`) | `test_design_prolog_gnu_gaps_steps.sh` | skill `prolog` reference section 8 |
| icon-scanning-asm | `corpus/tests/icon/scanning_asm/` | `test_design_icon_scanning_asm_steps.sh` | skill `icon` DESIGN |
| unicon | `harness/designs/unicon/` (steps 1-5 the surface, 6-16 UniTests to 100; its witnesses entries `unicon__<name>` of the icon master, the six package ones in `harness/fixtures/unicon/` until the oracle cuts a multi-file package) | `test_design_unicon_steps.sh` | skill `unicon` sections 1-2 and 7 |
| random-codegen-scope | `corpus/demos/scriptix/infinite_snobol4/` (with `COVERAGE.tsv`) | `test_design_random_codegen_scope_steps.sh` | skill `snobol4` DESIGN |
| pascal-front-end | `harness/designs/front_end/STEPS.tsv` (witnesses: pascal entries `front_end__*`, pf20d and pf20e with dialect `fpc`, pf30 with its unit as a file fence) | `test_design_pascal_front_end_steps.sh` | skill `pascal` DESIGN |
| pascal-helpers | `harness/designs/pascal_helpers/STEPS.tsv` (witnesses: `harness/fixtures/pascal_helpers/` until each step lands its own as a pascal entry `helpers__*`) | each step's entries through `corpus_suite_harness.py run` (the table's header) | skill `pascal` section 13 |
| raku-rewrite, raku-to-100 | `harness/designs/raku_rewrite/STEPS.tsv` (witnesses: raku entries `rewrite__*`), `corpus/tests/raku/LADDER.tsv` | `test_design_raku_rewrite_steps.sh`, `test_raku_ladder.sh` | skill `raku` DESIGN |
| raku-core, raku-roast-causes | `harness/designs/raku_core/`, `harness/designs/raku_roast_causes/` (witnesses: raku entries `core__*`, `roast_causes__*`) | `test_design_raku_core_steps.sh`, `test_design_raku_roast_causes_steps.sh` | skill `raku` sections 8 and 9 |
| shared-development | the step rows `shared-dev-step-*` | `util_seat_census.py` | skill `shared-box` |
| batch-grader | `harness/designs/batch_grader/STEPS.tsv` (witnesses: the entries `batch_grader__*` of each language's master; bg08, which no oracle answers, the fixture `harness/fixtures/batch_grader/`) | `test_design_batch_grader_steps.sh` | skill `suites-and-grading` section 5 |
| fleet-control | `harness/designs/fleet_control/` | `test_design_fleet_control_steps.sh` | skill `shared-box` section 9 (supersedes box-scheduler, fleet-queue, test-cycle, box-budget, shared-development, batch-grader) |
| test-cycle | `harness/designs/test_cycle/` | `test_design_test_cycle_steps.sh` | skill `suites-and-grading` section 7 |
| box-budget | `harness/designs/box_budget/` | `test_design_box_budget_steps.sh` | skill `shared-box` section 7 |
| box-scheduler | `harness/designs/box_scheduler/` | `test_design_box_scheduler_steps.sh` | skill `shared-box` section 8 |
| fleet-queue | `harness/designs/fleet_queue/` | `test_design_fleet_queue_steps.sh` | skill `fleet-bus` section 8 (reference) |
| skills-complete | `harness/designs/skills_complete/` | `test_design_skills_complete_steps.sh` | skill `fleet-bus` section 9 (reference) |
| run-switches | `harness/designs/run_switches/` | `test_design_run_switches_steps.sh` (probes `s4e_probe_run_switches.sh N`) | skill `suites-and-grading` section 8 (reference) |
| bus-one-queue | `harness/designs/bus_one_queue/` | `test_design_bus_one_queue_steps.sh` (probes `s4e_probe_bus_one_queue.sh N`) | the step table header (CIO-8 phase two, the cio; cut by officer_05; GOAL-CIO.md CIO-8 to CIO-10) |
