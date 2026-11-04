## ⛔ STANDING LAW (text and Lon's words: RULES.md; GOAL-CTO.md under each CTO-NNNN; GOAL-CEO.md under each CEO-NNNN, the fired seat's closed record)
- ORDER OF WORK (CEO-1886/1895/2035/1931): completeness, correctness (placement included), speed; speed only for SNOBOL4 and Icon, by instruction count; Raku climbs the rung ladder.
- THE GO (CEO-2071): an `assign`, or a SendMessage from the cto or coo naming a row, IS Lon's go; a question never stops the work; only Lon answers a permission prompt.
- MEMORY MODEL (CEO-1895/1354/1542/1368): placement decided ONCE in the planner; a retry never restores RSP; a γ pops only a fenced construct's cells; construct → stack, outlives scope → heap, out of stack → bigger declared `-s`; no global holds a stack; no frame markers.
- NO C FUNCTION ENTERS A BOX (CEO-1576/2045); only `tree_t` crosses to lower, and lower builds every runtime table (CEO-1369/1377); no language flag past the driver (CEO-1838/1840).
- ONE TESTING OFFICER (CEO-1342): only the coo runs suites, boards, the blocking set, `.s` regeneration and writes suite rows; a lander re-grades its ONE program in both modes plus `test_feature_reps.sh` and `test_smoke_<lang>.sh` per language touched (all eight for shared code); other tests by `s4e_test_request.sh` (≤8).
- MEASUREMENT (CEO-2060/1676/1696/1680/1386): `-dirty` is UNREAD; no oracle answer → excluded, never debt; no XFAIL, a test that cannot measure refuses rc 2; a DONE-WHEN a deletion satisfies is false.
- CODE (CEO-1565/1817/1353/1349/1478/1926): 200-column hierarchy, zero comments, zero blank lines; no symlinks; declared sizes are hard caps; no delimiter-joined aggregates, no fixed limits, no `-O2`, no new global without Lon's in-chat grant, no subagents in the repos.
- THE CHAT IS NOT THE RECORD: a ruling lands in its GOAL file's LIVE CURSOR on origin the same sitting. ANNOUNCEMENT.md is the scope authority (CEO-1221).
## EVERY SITTING, IN ORDER (the SOP)
1. Sync SCRIP, corpus, harness, .github (and the port repo): `git -C <repo> fetch origin && git -C <repo> merge --ff-only origin/main`, then `make -j8` in SCRIP (background past two minutes). Never pull half a cross-repo landing. Time labels from `date` in the same call.
2. MODE: `head -2 /home/resources/postoffice/MODE` and its keyed lines (`ROSTER:` `LANES:` `ORDER-OF-WORK:` `CONCERNS:` `REPORT-TO-LON:`).
3. This seat's GOAL file LIVE CURSOR, each held row's baton `/home/resources/postoffice/tasks/<topic>.task.md`, the rows: `grep -P '\t<seat>\t|:<seat>$' /home/resources/postoffice/QUEUE.tsv`.
4. `bash harness/scripts/s4e_msg.sh check` (long output into a file, read whole), act or reply, then `clear`.
5. Load the skills of the row's language and every layer touched; the skill gate hook refuses an edit until they are. Read the oracle's manual (`/home/resources/manuals/`) before ruling on a builtin or syntax.
6. ONE row at a time by THE LANDING RECIPE; at most two claims.
7. Hand off: baton NEXT rewritten, LIVE CURSOR moved, all pushed, `bash harness/scripts/handoff_status.sh` pasted verbatim. A waiting seat parks first (`park <topic> PARKED-AWAITING:<id>` or `BLOCKED-ON:<topic>`) (CEO-2107).
## THE LANDING RECIPE
1. Reproduce: `bash ../harness/scripts/monitor_run.sh <prog> --oracle` (the bug lies after the last agreed event); then ASM-DIFF against a passing sibling; only then gdb.
2. Cure in a clean `git worktree add` outside the root. Grammar edits: `harness/scripts/regenerate_parser_and_lexer_from_sources.sh`; generated tables (`gc_allocating_table.inc`, the rtx clobber table, `box_cell_shapes.inc`) are regenerated, never edited.
3. Prove: DONE-WHEN red before, green after; the program in both modes; `test_feature_reps.sh <lang> <feature>`; `test_smoke_<lang>.sh`; `util_reflow_200.py --check` and `strip_comments.py --check` per file.
4. Land: `git add` NAMED FILES; `git commit -F -` with a quoted heredoc; `git pull --rebase`, re-prove, push code repos first, `.github` last; a rejected push → `s4e_push_rejected.sh`. Identity `LCherryholmes` / `lcherryh@yahoo.com`, no trailers.
5. Record: baton LEDGER and NEXT; telegram the cto only for a ruling, the coo only for a cross-seat fact; close by `claim` + `done`.
## Workspace and oracles
Scripts run as `bash harness/scripts/X` from the root, `bash ../harness/scripts/X` from SCRIP. `SCRIP/` the compiler (`src/`, `bootstrap/` the Snocone parsers); `harness/` every fleet script; `corpus/tests/<lang>/` one master per language (`ALL.<ext>`, `ALL.ref`, `ALL.csv`, `PARTITION.tsv`), `packages/<lang>/` vendored suites; `.github/` RULES.md, `GOAL-*.md`, `SCORE.md`, skills, digest; `/home/resources/` oracles, `postoffice/`, `progress/`, `manuals/` (never a development clone).
Preflight `ls` the oracle (a missing one prints a plausible all-FAIL table): SNOBOL4/Snocone `/home/resources/x64/bin/sbl -bf`; Icon `/home/resources/icon-master/bin/icont`; Prolog swipl 9.0.4 and GNU Prolog 1.6.0, XSB 5.0.0 for `xsb_tests`, the program's dialect decides; Pascal `fpc -Miso`; Raku rakudo 2026.05.
## Build, run, test
```bash
cd SCRIP && make -j8                 # scrip + out/libscrip_rt.so; never above -j8
./scrip prog.sno < /dev/null         # mode 3, in-process; program args after --
./scrip --compile --out=prog.s prog.sno && gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog   # mode 4
./scrip --dump-ast|--dump-ir|--dump-bb|--dump-zeta|--dump-plan prog.sno
bash ../harness/scripts/util_run_slot.sh <cmd>...   # every hand run takes a run slot
python3 ../harness/scripts/corpus_suite_harness.py run ../corpus/tests/<lang>/ALL.<ext> ../corpus/tests/<lang>/ALL.ref --lang <lang> --modes m3,m4 --partition entry:<name>
bash ../harness/scripts/test_<lang>_ladder.sh --to N | --only N
```
A package program: its runner with `S4E_CHUNK=entry:<name>`. Never `pkill -f`; kill by pid. Instruction counts, not clocks.
## Architecture, bus, skills
parser → lower → optimizer → planner → one x86-64 emitter (`src/emitter/emit.cpp`, templates `src/templates/bb/`) → runtime `src/runtime/`. Every pattern or goal node is a four-port Byrd box (α β γ ω): SNOBOL4 patterns, Icon generators and Prolog backtracking are one machine. No `malloc`. More: `/scrip-architecture`.
The bus: `bash harness/scripts/s4e_msg.sh <verb>`, one verb at a time; `mint` is the only way to add work, `assign` the lock; `send` takes a quoted heredoc. More: `/fleet-bus`.
Skills: the gate names the one to load. A fact a language needs goes into its skill, not here. Edit this digest at `.github/digest/COMMON.md` and the seat block in `propagate_seat_digests_ceo_2071.py`, then re-run; never one root by hand.
