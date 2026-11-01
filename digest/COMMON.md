## ⛔ STANDING LAW, ONE LINE PER RULING (the text and Lon's words are in RULES.md and GOAL-CEO.md under each number)

- ORDER OF WORK (CEO-1886): completeness, correctness, speed; placement is correctness (CEO-1895); speed only for SNOBOL4 and Icon, by instruction count (CEO-2035); Raku climbs the rung ladder (CEO-1931/2070).
- THE GO (CEO-2071): an `assign` or a SendMessage from the cto or the coo naming a row IS Lon's go; a question never stops the work; only Lon answers a permission prompt.
- THE MEMORY MODEL (CEO-1895): placement decided ONCE in the planner; a retry never restores RSP (CEO-1759/1814/1841); a γ pops only a fenced construct's cells (CEO-1843). Lifetime rule (CEO-1354): construct → stack, outlives its scope → heap, out of stack → a bigger declared `-s`. No global holds a stack (CEO-1542/1543); no frame markers, the maps stay, the collector guesses nothing (CEO-1368/1371/1492).
- NO C FUNCTION ENTERS A BOX (CEO-1576); logic lives in emitted boxes (CEO-2045). THE TREE IS THE PRUNED PARSE TREE, only `tree_t` crosses, every runtime table is built by LOWER (CEO-1322/1369/1371/1377/1378). NO LANGUAGE FLAG PAST THE DRIVER; a deletion carries its re-expression (CEO-1838/1840).
- ONE TESTING OFFICER (CEO-1342 as amended): the coo runs suites, boards, the blocking set and the `.s` regeneration and alone writes suite rows; a lander fixes ONE program, re-grades it in both modes, runs `test_feature_reps.sh` and `test_smoke_<lang>.sh` for every language touched (all eight for shared code); named tests by `s4e_test_request.sh` (≤8).
- A DIRTY-TREE READING IS UNREAD (CEO-2060); STORED PARTITIONS (CEO-1676); NO ORACLE ANSWER → EXCLUDED, NEVER DEBT (CEO-1696/1934); NO PLANTED BREAKAGE, NO XFAIL, a test that cannot measure refuses rc 2 (CEO-1680); A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS SO, a DONE-WHEN a deletion satisfies is false (CEO-1386/553/555).
- LARGE CHUNKS (CEO-1478..1488); HARNESS, SIBLINGS, NO SYMLINKS (CEO-1817..1853); DECLARED SIZES, the declared size is a hard cap (CEO-1353/1281/1261); NO DELIMITER-JOINED AGGREGATES (CEO-1349); NO FIXED LIMITS; NO `-O2`; NO NEW GLOBAL without Lon's in-chat grant; NO SUBAGENTS IN THE REPOS (CEO-1926).
- CODE STYLE (CEO-1565): 200-column hierarchy rule, zero comments, zero blank lines; templates and `.cpp` line-oriented; `util_reflow_200.py --check` and `strip_comments.py --check` on every file touched.
- THE OFFICERS (CEO-2025..2067/2095): cto designs and takes the toughest jobs; coo is the admin half; THE CHAT IS NOT THE RECORD: a ruling lands in its GOAL file's LIVE CURSOR on origin before the sitting ends. ANNOUNCEMENT.md (cto custody) is the scope authority (CEO-1221).

## EVERY SITTING, IN ORDER (the SOP)

1. `git -C <repo> fetch origin && git -C <repo> merge --ff-only origin/main` for SCRIP, corpus, harness AND .github (and this seat's port repo where it has one), then `make -j8` in SCRIP (background it if it may pass two minutes). Never pull one repo of a cross-repo landing without its twin; a reboot empties `/tmp` and every runner refuses rc 2 on a stale `./scrip` until `make` runs. Every time label comes from `date` in the same tool call.
2. MODE: `head -1 /home/resources/postoffice/MODE` (the mode), `sed -n '2p'` (each seat's business, newest block first; find the clause that names this seat), and the keyed lines `ROSTER:` `LANES:` `ORDER-OF-WORK:` `CONCERNS:` `REPORT-TO-LON:`. Never trust a value restated in prose.
3. This seat's GOAL file's LIVE CURSOR (newest first), then the baton of every row this seat holds: `/home/resources/postoffice/tasks/<topic>.task.md`, its NEXT at the top. `bash harness/scripts/s4e_msg.sh assigned` lists them.
4. `bash harness/scripts/s4e_msg.sh check` (it must DISPLAY; over 24 lines, run it into a file, read it whole, then `clear`, which archives exactly what `check` displayed).
5. Load the skills of the row's language AND of every layer the cure will touch (THE SKILL TABLE below; `/<name>`), and read the ARCH page before touching code in its area; THE SKILL GATE (`s4e_skill_gate.sh`, a PreToolUse hook in every root) refuses an Edit or Write under `src/`, `bootstrap/`, a test or a witness until the session has loaded the skill that owns it, and names the one to load. Look the oracle's own manual up under `/home/resources/manuals/` before ruling on any builtin or syntax.
6. Work ONE row at a time, by THE LANDING RECIPE below. A seat holds at most two claims.
7. Hand off: the baton's NEXT rewritten, this seat's LIVE CURSOR moved, everything pushed, `bash harness/scripts/handoff_status.sh` pasted verbatim. Never leave a landing unpushed across a sitting. THE WAKE RULE (CEO-2107, Lon 2026-11-01: "wake a seat only if it has not finished its row"): a seat that stops because it waits PARKS THE WAIT first (`park <topic> PARKED-AWAITING:<request-id>` for the coo's verdict, `park <topic> BLOCKED-ON:<topic>` for another seat's row); the coo's wake list (`s4e_msg.sh wake`, `postoffice/WAKE.txt`, ARCH-SHARED-DEVELOPMENT § 12) names who holds advanceable work; a seat with an unfinished row may be woken by a SendMessage naming it, a seat that has finished its row is started only by Lon's /clear+next (the coo assigns its next row AHEAD so the row is there); a fact or an ask goes by telegram and waits for the next sitting.

## THE LANDING RECIPE (one program at a time)

1. Reproduce: THE MONITOR BRACKET first (`bash ../harness/scripts/monitor_run.sh <prog> --oracle`; the bug lies between the last event both agree on and the first they diverge on), then ASM-DIFF-FIRST (the smallest repro beside a passing sibling, `--compile` both, diff within one mode), only then gdb with a breakpoint and a hit count. Validate an instrument by running it; a null result bounds the probe; check a clean, consistently pulled tree before routing a red.
2. Cure the ONE program's class in a clean worktree outside the root (`git worktree add`), never in the measured tree, with the skill of every layer the diff touches loaded first (THE SKILL TABLE; the gate refuses the edit otherwise). A grammar edit is invisible until `regenerate_parser_and_lexer_from_sources.sh` runs; generated tables (`gc_allocating_table.inc`, the rtx clobber table, `box_cell_shapes.inc`) are regenerated, never edited.
3. Prove: the row's DONE-WHEN red before and green after; re-grade that program in both modes (`corpus_suite_harness.py run ... --modes m3,m4 --partition entry:<name>`, or the package runner with `S4E_CHUNK=entry:<name>`); `test_feature_reps.sh <lang> <feature>`; `test_smoke_<lang>.sh` for every language touched (all eight for shared code); `util_reflow_200.py --check` and `strip_comments.py --check` on every file touched; the ratchets the diff's area owns (fixed caps, flags, gc table check).
4. Land: `git add` NAMED FILES only; `git commit -F -` with a quoted heredoc (never `-m` with backticks); `git pull --rebase`, re-prove after the rebase, push code repos first and `.github` last; a rejected push is reported with `s4e_push_rejected.sh`. ONE IDENTITY: `user.name "LCherryholmes"`, `user.email "lcherryh@yahoo.com"`, no trailers.
5. Record: the baton's LEDGER and NEXT; a telegram to the cto only for a ruling ask, to the coo only for a cross-seat fact; the coo re-grades the suite (`s4e_test_request.sh`), and the row closes by `claim` + `done` (which runs the DONE-WHEN and refuses a red).

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
