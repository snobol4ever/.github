## ⛔ STANDING LAW, ONE LINE PER RULING (the text and Lon's words are in RULES.md and GOAL-CEO.md under each number)

- ORDER OF WORK (CEO-1886): completeness, correctness, speed; placement is correctness (CEO-1895); speed only for SNOBOL4 and Icon, by instruction count (CEO-2035); Raku climbs the rung ladder (CEO-1931/2070).
- THE GO (CEO-2071): an `assign`, or a SendMessage from the cto or the coo naming a row, IS Lon's go; a question never stops the work; only Lon answers a permission prompt.
- THE MEMORY MODEL (CEO-1895/1354/1542/1368): placement decided ONCE in the planner; a retry never restores RSP; a γ pops only a fenced construct's cells; construct → stack, outlives its scope → heap, out of stack → a bigger declared `-s`; no global holds a stack; no frame markers, the collector guesses nothing.
- NO C FUNCTION ENTERS A BOX, logic lives in emitted boxes (CEO-1576/2045); only the pruned parse tree (`tree_t`) crosses to lower and LOWER builds every runtime table (CEO-1369/1377); no language flag past the driver, a deletion carries its re-expression (CEO-1838/1840).
- ONE TESTING OFFICER (CEO-1342): only the coo runs suites, boards, the blocking set and the `.s` regeneration and writes suite rows; a lander re-grades its ONE program in both modes and runs `test_feature_reps.sh` and `test_smoke_<lang>.sh` per language touched (all eight for shared code); named tests by `s4e_test_request.sh` (≤8).
- MEASUREMENT (CEO-2060/1676/1696/1680/1386): a `-dirty` reading is UNREAD; partitions are stored; no oracle answer → excluded, never debt; no planted breakage, no XFAIL, a test that cannot measure refuses rc 2; a row exists only while a measurement says so, and a DONE-WHEN a deletion satisfies is false.
- CODE AND TREE (CEO-1565/1817/1353/1349/1478/1926): 200-column hierarchy rule, zero comments, zero blank lines, templates and `.cpp` line-oriented; no symlinks; declared sizes are hard caps; large chunks; no delimiter-joined aggregates, no fixed limits, no `-O2`, no new global without Lon's in-chat grant, no subagents in the repos.
- THE OFFICERS (CEO-2025..2095): the cto designs and takes the toughest jobs; the coo is admin and testing. THE CHAT IS NOT THE RECORD: a ruling lands in its GOAL file's LIVE CURSOR on origin the same sitting. ANNOUNCEMENT.md is the scope authority (CEO-1221).

## EVERY SITTING, IN ORDER (the SOP)

1. Sync SCRIP, corpus, harness and .github (and the port repo): `git -C <repo> fetch origin && git -C <repo> merge --ff-only origin/main`, then `make -j8` in SCRIP (background it past two minutes). Never pull one half of a cross-repo landing; after a reboot every runner refuses rc 2 until `make` runs. Time labels come from `date` in the same call.
2. MODE: `head -1 /home/resources/postoffice/MODE`, `sed -n '2p'` (each seat's business, newest first) and the keyed lines `ROSTER:` `LANES:` `ORDER-OF-WORK:` `CONCERNS:` `REPORT-TO-LON:`; never trust a value restated in prose.
3. This seat's GOAL file LIVE CURSOR, then each held row's baton `/home/resources/postoffice/tasks/<topic>.task.md` (NEXT on top); the rows: `grep -P '\t<seat>\t|:<seat>$' /home/resources/postoffice/QUEUE.tsv`.
4. `bash harness/scripts/s4e_msg.sh check` (over 24 lines: into a file, read whole), act or reply, then `clear`.
5. Load the skills of the row's language and of every layer touched (THE SKILL TABLE); the skill gate (`harness/scripts/s4e_skill_gate.py`, a PreToolUse hook) refuses an edit under `src/`, `bootstrap/`, a test or a witness until its skill is loaded. Read the oracle's manual under `/home/resources/manuals/` before ruling on a builtin or syntax.
6. ONE row at a time, by THE LANDING RECIPE; at most two claims.
7. Hand off: the baton's NEXT rewritten, the LIVE CURSOR moved, everything pushed, `bash harness/scripts/handoff_status.sh` pasted verbatim. THE WAKE RULE (CEO-2107): a waiting seat parks first (`park <topic> PARKED-AWAITING:<request-id>` or `BLOCKED-ON:<topic>`); a seat with an unfinished row may be woken by a SendMessage naming it; a seat that finished its row is started only by Lon's /clear+next, so the coo assigns its next row ahead; a fact or an ask goes by telegram.

## THE LANDING RECIPE (one program at a time)

1. Reproduce: `bash ../harness/scripts/monitor_run.sh <prog> --oracle` (the bug lies between the last event both agree on and the first they diverge on); then ASM-DIFF against a passing sibling (`--compile` both, one mode); only then gdb with a breakpoint and a hit count. Confirm a clean, consistently pulled tree before routing a red.
2. Cure in a clean `git worktree add` outside the root, the owning skills loaded. A grammar edit needs `regenerate_parser_and_lexer_from_sources.sh`; generated tables (`gc_allocating_table.inc`, the rtx clobber table, `box_cell_shapes.inc`) are regenerated, never edited.
3. Prove: the DONE-WHEN red before and green after; that program re-graded in both modes; `test_feature_reps.sh <lang> <feature>`; `test_smoke_<lang>.sh` per language touched; `util_reflow_200.py --check` and `strip_comments.py --check` per file touched; the area's ratchets.
4. Land: `git add` NAMED FILES; `git commit -F -` with a quoted heredoc; `git pull --rebase`, re-prove, push code repos first and `.github` last; a rejected push goes to `s4e_push_rejected.sh`. Identity `LCherryholmes` / `lcherryh@yahoo.com`, no trailers.
5. Record: the baton's LEDGER and NEXT; telegram the cto only for a ruling, the coo only for a cross-seat fact; the row closes by `claim` + `done` (it runs the DONE-WHEN and refuses a red).

## Workspace

A script runs as `bash harness/scripts/X` from the root, `bash ../harness/scripts/X` from SCRIP; scripts reach siblings by fixed relative paths, never a link or env override.
- `SCRIP/`: the compiler (`src/`, `Makefile`, `bootstrap/` the seven Snocone `parser_<lang>.sc`, `tools/`, `docs/`). One `scrip` compiles SNOBOL4, Snocone, Icon, Prolog, Rebus, Raku and Pascal to x86-64; the frontend comes from the extension (`scrip_exts[]` in `src/driver/scrip.c`).
- `harness/`: every fleet script: the bus `s4e_msg.sh`, runners, `test_gate_*`, `test_smoke_*`, `util_*` and `audit_*` censuses, `bench_*`, `lib_*`. `S4E_ENGINE` ∈ {`scrip`, `dotnet`, `jvm`}; a port's row is `<suite>@<port>`.
- `corpus/`: `tests/<lang>/` one master per language (`ALL.<ext>` a container, `ALL.ref`, `ALL.csv`, `PARTITION.tsv`, `config/LADDER.tsv`); `demos/` and `benchmarks/` (the only committed `.s`); `packages/<lang>/` vendored suites. Extraction only by `corpus_suite_harness.py extract`.
- `.github/`: `RULES.md` the only law (`grep -n '^## '` for its map, page it in ≤50-line chunks), the `GOAL-*.md` pages, `SCORE.md` (THE SUITE TABLE), `scripts/`, `skills/` and `digest/`.
- `/home/resources/`: the oracles, the monitor forks, `postoffice/`, `progress/` (`results.tsv`, `SUITES.tsv`, `SMOKE.tsv`), `manuals/` (every manual as text, indexed by `README.md`). Never a development clone.

## Oracles

Preflight `ls` the oracle binary: a missing oracle prints a plausible all-FAIL table. SNOBOL4/Snocone `/home/resources/x64/bin/sbl -bf` (benchmarks: `/home/resources/spitbol-bench-oracle/sbl`); Icon `icont`/`iconx` in `/home/resources/icon-master/bin/`; Prolog swipl 9.0.4 and GNU Prolog 1.6.0 (`gprolog_bin()`/`gplc_bin()`), XSB 5.0.0 for `xsb_tests` only, the program's own dialect decides (CEO-391/1772); Pascal ISO 7185 over `fpc -Miso` (CEO-1225); Raku rakudo 2026.05, the roast is the spec. One oracle per package; a broken oracle is fixed before grading.

## Build and run

```bash
cd SCRIP && make -j8                 # scrip + out/libscrip_rt.so; never above -j8; targets parsers-sc, pristine, test (the coo's)
./scrip prog.sno < /dev/null         # mode 3, in-process; program args after --
./scrip --compile --out=prog.s prog.sno && gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog   # mode 4, PIE
./scrip --dump-ast|--dump-ir|--dump-bb|--dump-zeta|--dump-plan prog.sno
./scrip -d128m -i1m -s4m -m16m prog.sno      # SPITBOL's sizes; a compiled program takes them before --
bash ../harness/scripts/util_run_slot.sh <cmd>...   # every hand run takes one of the 8 run slots
```

`< /dev/null` only on runs that read no stdin. Each mode is graded against the oracle. Instruction counts while the box is busy, a clock only in a quiet slice; measurement loops write nothing to /tmp.

## Testing

- One program, from SCRIP: `python3 ../harness/scripts/corpus_suite_harness.py run ../corpus/tests/<lang>/ALL.<ext> ../corpus/tests/<lang>/ALL.ref --lang <lang> --modes m3,m4 --partition entry:<name>` (`--modes m3,m4` mandatory); a package: its runner with `S4E_CHUNK=entry:<name>`.
- Ladders: `test_<lang>_ladder.sh --to N | --only N`; a rung is ≤20 lines, one construct, an oracle-cut ref; rung N+1 opens when N is green in both modes; `util_add_ladder_witness.py` adds one.
- Files are LF; a rewrite changes only the bytes it means to. Never `pkill -f`; kill by pid inside this root.

## Architecture

parser (`src/parsers/<lang>/`) → lower (`src/lower/`) → `optimizer_run` → planner (`src/planner/`) → the one x86-64 emitter (`src/emitter/emit.cpp`, box templates in `src/templates/bb/` on the `x86()` encoder). Runtime: `src/runtime/` (`rt/`, `core/`, `builtins/`, `rtx/` asm leaves). Every pattern or goal node is a four-port Byrd box (α proceed, β recede, γ succeed, ω concede) wired at compile time into jumps: SNOBOL4 patterns, Icon generators and Prolog backtracking are one machine. No `malloc/calloc/realloc/free` (compile-time data in `src/ir/ct_arena.c`). SPITBOL semantics for SNOBOL4/Snocone; SCRIP Icon requires semicolons; Prolog integers are unbounded. The rest: `/scrip-architecture`.

## The bus (`/home/resources/postoffice/PROTOCOL.md`, `/fleet-bus`)

`bash harness/scripts/s4e_msg.sh <verb>`: `next done claim unclaim park reown assign mint send ask check clear board banner sweep whoami assigned`. `mint <topic> [rank] [--owner <seat>] --stdin` is the only way to add work (a GOAL text with `DONE-WHEN:` and `PREMISE-WHEN:`); `assign <seat> <topic>` is the lock and doorbell; `send <seat> <topic> --stdin` takes a quoted heredoc (it refuses a backtick or `$(`). Bus verbs run one at a time, by absolute path, never piped into a short read. `QUEUE.tsv` is the live state; a telegram is the record, a SendMessage the pointer.

## Skills (THE SKILL TABLE; the gate names the one to load)

- `.c/.h/.inc` under `SCRIP/src/` → `/scrip-c-code`; `src/lower/` → `/lowering` + the language; a parser or prelude → the language; `bootstrap/*.sc` → `/snocone-parser-patterns`
- templates, `x86_*`, `emit.cpp` → `/box-templates`; planner, emitter, `gc_*`, a poll, a root, `rtx_gc.s` → `/scrip-memory-model` + `/gc-collector`; `src/runtime/rtx/` → `/rtx-asm-leaves`; `rt.c`, a call template, `builtins.tsv`, a raise path → `/runtime-calls`; the Makefile or includes → `/scrip-build`; cross-layer work or an unrouted red → `/scrip-architecture`
- a test, gate, smoke, rung, witness, ref, `ALL.csv`, `STEPS.tsv`, `LADDER.tsv` or DONE-WHEN → `/gates-and-witnesses`
- languages: `/snobol4` (with Snocone and Rebus) `/icon` `/prolog` (`/prolog-engine` `/prolog-tabling` `/prolog-constraints`) `/pascal` `/raku`
- the fleet: `/fleet-bus` `/design-plans` `/suites-and-grading` `/shared-box` `/speed-measurement`; `/ports` (snobol4dotnet, snobol4jvm) is not `/scrip-backends` (SCRIP's future targets)

A fact every seat in a language needs goes into its skill (`.github/skills/<name>/SKILL.md`, installed by `propagate_skills_ceo_2071.sh`), not this digest. This digest is edited at `.github/digest/COMMON.md` and the seat block in `propagate_seat_digests_ceo_2071.py`, then re-run; never one root by hand.
