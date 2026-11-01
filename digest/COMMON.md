## ⛔ STANDING LAW, ONE LINE PER RULING (the text, Lon's verbatim words and the receipts are in RULES.md and GOAL-CEO.md under each number)

- **ORDER OF WORK** (CEO-1886): (1) completeness, (2) correctness, (3) speed. The RSP/RBP placement programme is CORRECTNESS (CEO-1895). SPEED is OPEN for SNOBOL4 and Icon only, measured by INSTRUCTION COUNT (CEO-2035: `util_instr_count.sh`; a clock only inside `util_quiet_slice.sh`), behind each seat's correctness rows; CLOSED for Prolog, Pascal and Raku (CEO-1914). Raku builds at rank 9 (CEO-1931) and climbs the cto's rung ladder, not the suites, until half the rungs are green (CEO-2070).
- **THE GO** (CEO-2071, Lon 2026-10-31): an `assign` on the bus, or a SendMessage from the ceo naming a row, IS Lon's go for that row. No seat waits for Lon's word in its own window to start assigned work; a question never stops the work (record it, state the assumption, `ask`, carry on). A PERMISSION PROMPT is a different thing: only Lon, in that seat's own window, answers one.
- **THE MEMORY MODEL** (CEO-1895, the three zetas): placement is decided ONCE, in the PLANNER (`src/planner/`, after lower, before the emitter; `ARCH-THREE-ZETAS-EMISSION.md`). A RETRY NEVER RESTORES RSP; no RSP reset or reload at any β (CEO-1759/1814/1841); a γ pops only a fenced construct's cells (CEO-1843). `test_gate_no_rsp_reset_at_beta.sh` blocks at 0.
- **THE LIFETIME RULE** (CEO-1354): construct lifetime → stack; outlives its scope → heap. Out of stack → a bigger declared `-s` on the attribute row, never data moved to the heap.
- **NO GLOBAL HOLDS A STACK** (CEO-1542/1543): the machine stack is the stack; the only stacks outside RSP/RBP are the two r12 islands (SNOBOL4 conditional assignment, Prolog trail/choice points).
- **NO FRAME MARKERS, NO SECOND STACK, THE MAPS STAY** (CEO-1368/1371/1492): compile-time frame maps (ARCH-GC § 7 FROZEN); THE COLLECTOR GUESSES NOTHING: one static map per frame, typed visitors, no conservative scan.
- **NO C FUNCTION ENTERS A BOX** (CEO-1576); LOGIC LIVES IN EMITTED BOXES: Byrd boxes are maximally preferred, no C where possible (CEO-2045).
- **THE TREE IS THE PRUNED PARSE TREE** (CEO-1369/1371/1377/1378/1322): only `tree_t` crosses to lower; the lowerer places what a parser recognised; every runtime table is built by LOWER.
- **NO LANGUAGE FLAG PAST THE DRIVER** (CEO-1838/1840): after lower every variance is an IR fact; a deletion carries its re-expression in the same landing.
- **ONE TESTING OFFICER** (CEO-1342, amended CEO-1671/1673/1893/1926/1928/2068): the coo runs suites, boards, the blocking set and the `.s` regeneration (its loop up to FOUR tests at once, one run slot left free, CEO-2068) and alone writes the SUITE TABLE rows. A lander fixes ONE program, re-grades THAT program in both modes, runs `test_feature_reps.sh` (≤8 core entries, CEO-1677) and `test_smoke_<lang>.sh` for every language its diff touches (all eight for shared code) BEFORE the push. `make preflight` is NOT a per-push check. Heavy verification once per batch of 3-4 (CEO-1316). Named tests: `s4e_test_request.sh <suite-key> <entry>...` (≤8 programs), verdicts by telegram.
- **A DIRTY-TREE READING IS UNREAD** (CEO-2060): a reading stamped `-dirty` never assembles a row; grade in a clean worktree outside the root; never edit the tree a loop or a measurement is running on. Your measurements are void if you touch the tree under them.
- **STORED PARTITIONS** (CEO-1676): every suite table has a `PARTITION.tsv`; a landing that changes `ALL.csv` rebuilds it (`util_suite_partition.py build`).
- **NO ORACLE ANSWER → EXCLUDED, NEVER DEBT** (CEO-1696/1934): no output, a refusal, a crash, a hang or an unknown answer leaves the denominator as `NO_ORACLE_ANSWER`. Everything the oracle answers stays as debt (CEO-749/1518).
- **NO PLANTED BREAKAGE** (CEO-1680): a criterion fails once before it is trusted (a ref cut from the oracle shown red against a corrupted ref, or red on `<cure>^`). **THERE IS NO XFAIL**; a test that cannot measure REFUSES rc 2; never edit a test to return 0.
- **A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS** (CEO-1386): `mint` refuses a prose DONE-WHEN; a DONE-WHEN never pins a population count, reads the denominator it grades, is graded on origin, and loses when the measurement contradicts it (CEO-555); a criterion a deletion satisfies is false (CEO-553).
- **LARGE CHUNKS** (CEO-1478..1484/1488): a scheme change rolls out once small with a smoke, then everywhere in the seat's own lane, then Lon's ultracode.
- **HARNESS, SIBLINGS, NO SYMLINKS** (CEO-1817/1819/1820/1853): every root holds `SCRIP corpus harness .github` as siblings; no code, build or seat creates a symlink (`test_gate_no_symlinks.sh`, blocking).
- **DECLARED SIZES** (CEO-1353/1281): every test unit stores `heap_kb`/`stack_kb` (and `oracle_env`/`oracle_args`); runners pass `-d<kb>k -s<kb>k`, never `SCRIP_HEAP_KB`; shipped defaults are SPITBOL's `-d128m -i1m -s4m -m16m` (CEO-1261); the declared size is a HARD CAP.
- **NO DELIMITER-JOINED AGGREGATES** (CEO-1349); **NO FIXED LIMITS** (`audit_fixed_caps_census.py` is the ratchet); **NO `-O2` BUILDS** (`RT_OPT`); **NO NEW GLOBAL** without Lon's in-chat grant that session; **NO SUBAGENTS IN THE REPOS** (CEO-1926).
- **CODE STYLE** (CEO-1565): hand-written `.c/.h/.inc` under `src/` on Lon's 200-column hierarchy rule, zero comments and zero blank lines; templates and `.cpp` LINE-ORIENTED. `util_reflow_200.py --check <paths>` and `strip_comments.py --check` on every file a landing touches.
- **THE OFFICERS** (CEO-2025/2026/2029/2067): ceo cto cfo coo cao cqo. The cto DESIGNS; while the roster is small it also takes the toughest jobs of any kind (CEO-2067). A failed HQ escalates to an officer. A Lon word to the seats is a ROW PER SEAT with its WITNESS as the DONE-WHEN; THE CHAT IS NOT THE RECORD: a ruling lands in its GOAL file's LIVE CURSOR on origin before the sitting ends.
- **ANNOUNCEMENT** (postoffice `ANNOUNCEMENT.md`, ceo custody) is the scope authority: all seven languages on x86-64; 100% means 100% of the industry-standard language; benchmarks and demos are suite rows (CEO-1221).

## EVERY SITTING, IN ORDER (the SOP)

1. `git -C <repo> fetch origin && git -C <repo> merge --ff-only origin/main` for SCRIP, corpus, harness AND .github (and this seat's port repo where it has one), then `make -j8` in SCRIP (background it if it may pass two minutes). Never pull one repo of a cross-repo landing without its twin; a reboot empties `/tmp` and every runner refuses rc 2 on a stale `./scrip` until `make` runs. Every time label comes from `date` in the same tool call.
2. MODE: `head -1 /home/resources/postoffice/MODE` (the mode), `sed -n '2p'` (each seat's business, newest block first; find the clause that names this seat), and the keyed lines `ROSTER:` `LANES:` `ORDER-OF-WORK:` `CONCERNS:` `REPORT-TO-LON:`. Never trust a value restated in prose.
3. This seat's GOAL file's LIVE CURSOR (newest first), then the baton of every row this seat holds: `/home/resources/postoffice/tasks/<topic>.task.md`, its NEXT at the top. `bash harness/scripts/s4e_msg.sh assigned` lists them.
4. `bash harness/scripts/s4e_msg.sh check` (it must DISPLAY; over 24 lines, run it into a file, read it whole, then `clear`, which archives exactly what `check` displayed).
5. Load the skills of the row's language AND of every layer the cure will touch (THE SKILL TABLE below; `/<name>`), and read the ARCH page before touching code in its area; THE SKILL GATE (`s4e_skill_gate.sh`, a PreToolUse hook in every root) refuses an Edit or Write under `src/`, `bootstrap/`, a test or a witness until the session has loaded the skill that owns it, and names the one to load. Look the oracle's own manual up under `/home/resources/manuals/` before ruling on any builtin or syntax.
6. Work ONE row at a time, by THE LANDING RECIPE below. A seat holds at most two claims.
7. Hand off: the baton's NEXT rewritten, this seat's LIVE CURSOR moved, everything pushed, `bash harness/scripts/handoff_status.sh` pasted verbatim. Never leave a landing unpushed across a sitting.

## THE LANDING RECIPE (one program at a time)

1. Reproduce: THE MONITOR BRACKET first (`bash ../harness/scripts/monitor_run.sh <prog> --oracle`; the bug lies between the last event both agree on and the first they diverge on), then ASM-DIFF-FIRST (the smallest repro beside a passing sibling, `--compile` both, diff within one mode), only then gdb with a breakpoint and a hit count. Validate an instrument by running it; a null result bounds the probe; check a clean, consistently pulled tree before routing a red.
2. Cure the ONE program's class in a clean worktree outside the root (`git worktree add`), never in the measured tree, with the skill of every layer the diff touches loaded first (THE SKILL TABLE; the gate refuses the edit otherwise). A grammar edit is invisible until `regenerate_parser_and_lexer_from_sources.sh` runs; generated tables (`gc_allocating_table.inc`, the rtx clobber table, `box_cell_shapes.inc`) are regenerated, never edited.
3. Prove: the row's DONE-WHEN red before and green after; re-grade that program in both modes (`corpus_suite_harness.py run ... --modes m3,m4 --partition entry:<name>`, or the package runner with `S4E_CHUNK=entry:<name>`); `test_feature_reps.sh <lang> <feature>`; `test_smoke_<lang>.sh` for every language touched (all eight for shared code); `util_reflow_200.py --check` and `strip_comments.py --check` on every file touched; the ratchets the diff's area owns (fixed caps, flags, gc table check).
4. Land: `git add` NAMED FILES only; `git commit -F -` with a quoted heredoc (never `-m` with backticks); `git pull --rebase`, re-prove after the rebase, push code repos first and `.github` last; a rejected push is reported with `s4e_push_rejected.sh`. ONE IDENTITY: `user.name "LCherryholmes"`, `user.email "lcherryh@yahoo.com"`, no trailers.
5. Record: the baton's LEDGER and NEXT; a telegram to the ceo only for a ruling ask or a cross-seat fact; the coo re-grades the suite (`s4e_test_request.sh`), and the row closes by `claim` + `done` (which runs the DONE-WHEN and refuses a red).

## Workspace map

From the root a script is `bash harness/scripts/X`; from SCRIP, `bash ../harness/scripts/X`. A script reaches its siblings by fixed relative paths, never a link or an env override.

- `SCRIP/`: the compiler (`src/`, `Makefile`, `bootstrap/` the seven Snocone `parser_<lang>.sc`, `tools/`, `docs/`). One `scrip` binary compiles SNOBOL4, Snocone, Icon, Prolog, Rebus, Raku and Pascal to x86-64; the frontend comes from the extension (`scrip_exts[]` in `src/driver/scrip.c`). Objdir `/tmp/si_objs<tree-path>`; runtime objects cache in-tree under `out/rt_pic-<RT_TAG>`; ccache wraps every compile (shared across roots).
- `harness/`: every script of the fleet: the bus `s4e_msg.sh`, runners, gates (`test_gate_*`), smokes (`test_smoke_*`), censuses (`util_*`, `audit_*`), benchmarks (`bench_*`), libraries (`lib_*`), oracle builds. `S4E_ENGINE` in {`scrip`, `dotnet`, `jvm`} names the graded engine; a port's row is `<suite>@<port>`.
- `corpus/`: `tests/<lang>/` one flat master per language (`ALL.<ext>`, `ALL.ref`, `ALL.csv`, `PARTITION.tsv`, sidecars; `config/LADDER.tsv`); `demos/` and `benchmarks/` (the only trees with committed `.s`); `packages/<lang>/` vendored suites with their own tables. A master is a CONTAINER, never a program; the one extraction authority is `corpus_suite_harness.py extract`.
- `.github/`: the org brain. `RULES.md` is the only law (`grep -n '^## ' RULES.md` for its map, page it in ≤50-line chunks). `GOAL-CEO.md` (fleet rulings), `MASTER-PLAN.md`, `SCORE.md` (§ THE SUITE TABLE answers "what's the score"), the `GOAL-*.md` and `ARCH-*.md` pages, `findings/`, `board-lines/`, `scripts/`, `skills/` (the source of every seat's skills), `digest/` (the source of every seat's CLAUDE.md).
- `/home/resources/` (shared, never a development clone): the oracles, the monitor forks `{icon,gprolog,swipl,fpc,rakudo}-mon/`, `postoffice/`, `progress/` (`results.tsv`, `SUITES.tsv`, `SMOKE.tsv`), `branch-archive/`, the upstream drops read in place, and **`manuals/`: every manual, standard and paper on the box as searchable text** (`manuals/README.md` is the index; `grep -rn <term> /home/resources/manuals/<area>/`). Leave its contents as their authors laid them out.

## Oracles

SNOBOL4/Snocone: `/home/resources/x64/bin/sbl -bf` (via `lib_oracle_flags.sh:sbl_correctness_bin()`); benchmark oracle `/home/resources/spitbol-bench-oracle/sbl`. Icon: `icont`/`iconx` under `/home/resources/icon-master/bin/` (the SCRIP-dialect build). Prolog: the ISO-plus superset (CEO-391/1772) over `swipl` 9.0.4 and GNU Prolog 1.6.0 through `gprolog_bin()`/`gplc_bin()`, XSB 5.0.0 for `xsb_tests` only (`xsb_bin()`); the program's own dialect decides a conflict (`ARCH-PROLOG-DIALECTS.md`). Pascal: ISO 7185 wins over `fpc -Miso` (CEO-1225). Raku: rakudo 2026.05; the spec is the roast. One oracle per package, no `--compat` switch; when the oracle is broken we stop and fix it. ⛔ A missing oracle prints a plausible all-FAIL table; preflight `ls` the oracle binaries before trusting a board.

## Build and run

```bash
cd SCRIP && make -j8                         # ./scrip + out/libscrip_rt.so + out/scrip-ipp; never above -j8 (8 box-wide compile slots)
make parsers-sc | make pristine | make test  # the .sc parsers; wipe and rebuild; the blocking set (the coo's)
./scrip prog.sno < /dev/null                 # mode 3 --run (default): in-process; program args after --
./scrip --compile --out=prog.s prog.sno      # mode 4: asm (a bare -o FILE is refused)
gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog   # the harness's link (PIE, never -no-pie)
./scrip --dump-ast|--dump-ir|--dump-bb|--dump-zeta|--dump-plan prog.sno ; ./scrip --stlimit prog.sno
./scrip -d128m -i1m -s4m -m16m prog.sno      # SPITBOL's switches; a compiled program takes them before --
bash ../harness/scripts/util_run_slot.sh <cmd>...   # every hand run takes one of the box's 8 run slots
```

Put `< /dev/null` on runs that read no stdin, never on one fed by a pipe. Modes 1 and 2 are deleted; modes may diverge and each is graded against the oracle. The pools cap how many processes run; instruction counts while the box is busy, a clock only in a quiet slice; measurement loops write no outputs to /tmp.

## Testing mechanics

- One program by hand, from SCRIP: `python3 ../harness/scripts/corpus_suite_harness.py run ../corpus/tests/<lang>/ALL.<ext> ../corpus/tests/<lang>/ALL.ref --lang <lang> --modes m3,m4 --partition entry:<name>` (`--modes m3,m4` is MANDATORY); a package: its runner with `S4E_CHUNK=entry:<name>`.
- The construct ladders: `test_<lang>_ladder.sh --to N | --only N` over `corpus/tests/<lang>/config/LADDER.tsv`; a rung is ≤20 lines, one construct, its ref cut from the oracle; a declared rung not built is RED; rung N+1 opens when N is green in both modes. `util_add_ladder_witness.py` adds a witness with its oracle-cut ref.
- OUR FILES ARE LF; a data rewrite changes only the bytes it means to. Never `pkill -f` a pattern; kill by pid inside this root.

## Architecture (the essentials; the ARCH pages carry the rest)

parser (`src/parsers/<lang>/`) → lower (`src/lower/`) → `optimizer_run` → the PLANNER (`src/planner/`) → the ONE x86-64 emitter (`src/emitter/emit.cpp` + `src/templates/bb/` boxes on the `x86()` encoder) → x86-64. Runtime: `src/runtime/` (`rt/`, `core/`, `builtins/`, `rtx/` the hand-written asm leaves). Every pattern/goal node is a four-port Byrd box (α proceed, β recede, γ succeed, ω concede) wired at compile time into straight-line jumps; SNOBOL4 patterns, Icon generators and Prolog backtracking are three syntaxes over one machine. SCRIP calls no `malloc/calloc/realloc/free`; compile-time populations live in `src/ir/ct_arena.c`. SPITBOL semantics for SNOBOL4/Snocone; SCRIP Icon is semicolon-required; Prolog integers are unbounded. Before touching BB/ζ/planner code read `ARCH-THREE-ZETAS-EMISSION.md`, `ARCH-ZETA-ONE-COORDINATE.md`, `ARCH-GC-COMPILE-TIME-FRAME-MAPS.md`, `ARCH-RT-CALL-PROTOCOL.md`, `ARCH-X86-ASM-ENCODER.md`; the fleet's plan is `ARCH-FLEET-PLAN-TO-100.md`.

## The bus (`/home/resources/postoffice/PROTOCOL.md`)

`bash harness/scripts/s4e_msg.sh <verb>` from the root: `next done claim unclaim park reown assign mint send ask check clear board banner sweep whoami assigned`. `mint <topic> [rank] [--owner <seat>] --stdin` is the only way to add work (a GOAL text with its own `DONE-WHEN:` and `PREMISE-WHEN:` lines). `assign <seat> <topic>` is the lock and doorbell. `send <seat> <topic> --stdin` with a quoted heredoc (it refuses a backtick or `$(`). Never pipe a bus verb into a short read; run bus verbs sequentially with absolute paths. Shared state: `QUEUE.tsv` (the live state; `claims/` receipts are not live claims), `tasks/<topic>.task.md`, one inbox per seat. Other seats are ListAgents peers: a telegram is the record, a SendMessage the pointer.

## Skills and manuals

THE SKILL TABLE (Lon 2026-11-01: the language skills were loaded, the coding skills were not; now the gate asks). What you touch -> the skill to load first:
- any `.c`, `.h` or `.inc` under `SCRIP/src/` (parsers and generated tables excepted) -> `/scrip-c-code` (the 200-column rule, no comments, no malloc, no new global, no fixed limit)
- `src/lower/` -> `/lowering` plus the language skill (`lower_<lang>.c`); `src/parsers/<lang>/` or a prelude -> the language skill; `bootstrap/*.sc` -> `/snocone-parser-patterns`
- `src/templates/`, `x86_*.{h,cpp}`, `emit.cpp` -> `/box-templates`; `src/planner/`, `src/emitter/`, `src/runtime/rt/gc_*` -> `/scrip-memory-model`; `src/runtime/rtx/` -> `/rtx-asm-leaves`
- a `test_gate_*.sh`, `test_*.sh`, smoke, rung, witness, ref, `ALL.csv`, `STEPS.tsv`, `LADDER.tsv`, or a DONE-WHEN -> `/gates-and-witnesses`
- the language of the row, always: `/prolog` `/pascal` `/icon` `/raku` `/snobol4` (SNOBOL4, Snocone and Rebus)

Skills load on demand and carry what this digest does not: each language's oracle rulings, dialect rules, source map, runners, ARCH pages and pitfalls. `/prolog` `/pascal` `/icon` `/raku` `/snobol4` (SNOBOL4, Snocone and Rebus) and `/scrip-memory-model` (zetas, frames, the collector, the templates). Their source is `.github/skills/<name>/SKILL.md`, installed into every root by `.github/scripts/propagate_skills_ceo_2071.sh`; a seat that learns a fact every seat in its language needs lands it in the skill, not in a digest. The manuals are text under `/home/resources/manuals/<area>/` (`.github/scripts/util_manuals_to_text.sh` regenerates them). This digest is generated from `.github/digest/COMMON.md` and the seat block in `.github/scripts/propagate_seat_digests_ceo_2071.py`; edit those and re-run, never one root by hand; the previous digest is beside it as `CLAUDE.md.bak-2026-10-31-ceo-2071`.
