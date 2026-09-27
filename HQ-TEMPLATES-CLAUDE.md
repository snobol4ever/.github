# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

⛔⭐ **THIS ROOT IS `/home/claude_templates` (identity `hq_templates`), THE SEAT HQ-TEMPLATES, opened 2026-09-27 by Lon (in-chat to the ceo, verbatim: *"I think we will need one more HQ to handle keeping C++ templates clean regarding the rules of construction. Let's call it HQ-TEMPLATES"*; GOAL-CEO CEO-1321). Your officer is the cto (your postoffice `HQ` file reads `cto`: asks route there, the cto reviews your landings). The mode stays TENET with you as its eleventh working seat.**

⛔ **`.github/RULES.md` is the only law; anything here that contradicts it is void.** This file is a digest of MECHANICS and POINTERS, written by the ceo from `.github/HQ-TEMPLATES-CLAUDE.md` (edit that source, not this copy). Numbers below were measured 2026-09-27 at SCRIP `6c8992978` (re-measured unchanged at `7cafd69c0` the same day: 135 files, 61 clean, 74 dirty, GRAND 1517); re-measure before quoting.

## ⛔⭐⭐⭐ YOUR ONE THING — THE WATCH LOOP (read `.github/GOAL-HQ-TEMPLATES.md` first, every sitting)

Lon, verbatim: *"So the HQ-TEMPLATES will probably not work from A-Z if it can detect from the whole set the violations. But it will just run in a loop always looking for seats creating bad code so it can scoop it up and fix it."* Every tick: pull all three repos and `make`; census the WHOLE template set (`bash scripts/audit_bb_fixup_rank.sh` — 135 files, 74 dirty, GRAND 1517 on 2026-09-27); attribute every file whose count rose to the landing and seat that raised it (`git log <last>..HEAD -- <file>`); cure it behavior-neutral and telegram the lander the rule it broke; between arrivals, drive the standing debt down WORST FIRST; write the tick into `GOAL-HQ-TEMPLATES.md`'s LIVE CURSOR.

**And beyond the rule count** (Lon, verbatim: *"This template code health reaches beyond fixing any BB for the many IR's it handles, but to consider having other IR/BB broken out properly by form/pattern."*): the health target is ONE FORM PER BOX — a template that branches on sub-kind, operand shape or neighbour to decide its code is split in LOWER into one box per form (ONE-IR-ONE-LOGIC, TIER S in `GOAL-BB-FIXUP.md`); the loop censuses the FORMS as well as the violations.

**The rules of construction live in:** `.github/GOAL-BB-FIXUP.md` (TEMPLATE SPEC v2, the FACT RULES, the CONVERSIONS CV1–CV10, tiers H and S, the laws of the loop) · `.github/GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (R1–R13, three gated FACT RULES) · `.github/ARCH-X86-ASM-ENCODER.md` (every instruction through `x86(...)`, BOTH-MEDIUM MANDATORY) · `RULES.md` § ERADICATE C→BB→C→BB, § LOGIC LIVES IN EMITTED BOXES, NOT IN C, § MODES MAY DIVERGE · `GOAL-SNOBOL4-100.md` § BB-FIXUP SWEEP (still-binding findings). Read the ARCH pages before touching BB or ζ code (Lon's standing order): `ARCH-LANGUAGES.md`, `ARCH-X86-ASM-ENCODER.md`.

## Session start

0. `.github/GOAL-HQ-TEMPLATES.md` (LIVE CURSOR) → `.github/GOAL-BB-FIXUP.md` → `.github/RULES.md` (⚠ ~430 KB: `grep -n '^## ' RULES.md` for the map, page it in ≤50-line chunks; `grep -n 'FACT RULE —' RULES.md` is the second map) → `.github/PLAN.md` § SESSION START. **The chat is not the record:** every ruling, discovery or retraction goes into a file the moment it lands (your cursor, or a row's baton).
1. `git -C <repo> fetch origin && git -C <repo> merge --ff-only origin/main` in SCRIP, corpus, .github — then an incremental `make` in SCRIP (every runner refuses on a binary older than the tree; the first `make` after a reboot is a full rebuild).
2. `cd SCRIP && bash scripts/s4e_msg.sh check` — read what it displays; `clear` deletes exactly that. The hook shows at most 24 lines: with more waiting, run `check` by hand.
3. `bash scripts/s4e_msg.sh next` — serves your rows (the picker admits `hq_templates` under TENET, CEO-1321).

## Build and test

```bash
cd SCRIP
make                 # ./scrip + out/libscrip_rt.so; objdir /tmp/si_objs<tree-path>
make preflight       # the cheap hermetic arms -- part of EVERY landing verdict
make test            # THE blocking set (hundreds of arms, tens of minutes) -- HEAVY: once per batch of 3-4 landings (CEO-1316)
make test-sequential # the same arms, stopping at the FIRST red -- for bisecting a batch, never a verdict
bash scripts/test_gate_<name>.sh                      # ONE arm; every arm is a standalone script; grep <name> Makefile finds its line
./scrip --compile -o out.s prog.sno < /dev/null      # mode 4 text: the A/B witness of a template edit
./scrip prog.sno < /dev/null                          # mode 3 (default)
bash scripts/audit_bb_fixup_rank.sh                   # whole-set census (your loop's instrument)
bash scripts/audit_bb_fixup_file.sh src/templates/bb/bb_X.cpp   # one file; rc 0 = conformant
python3 scripts/strip_comments.py --check             # zero comments in C/C++/asm
```

- ⛔⭐ **HEAVY VERIFICATION RUNS ONCE PER BATCH OF THREE TO FOUR CHANGES** (Lon 2026-09-27, CEO-1316): per landing = the file's audit rc 0 + the gates it touched + `make preflight`; a batch red is bisected within the batch. You run NO language board — the language HQs' next batch passes read your landings on their suites (CEO-1232); an HQ that bisects a red to your commit asks you to cure or revert within the tick.
- ⛔ **THE TWO AUDITS COUNT DIFFERENT CLASSES.** The census (`audit_bb_fixup_rank.sh`) omits `cv9_param_str` and `cv10_graph`, which the per-file audit counts: at `7cafd69c0`, `bb_match_abort.cpp` prints CLEAN in the census and is rc 1 per file (`cv10_graph` 2). A census GRAND of 0 is therefore not "the whole set at rc 0" — this is the still-binding sweep finding "rank TOTAL ≠ per-file TOTAL". The census's column abbreviations (`eb nw bs rb mt ef lc bl pe lv rp hc sd cl ml xc bp lb`) are spelled out in the header and print lines of `audit_bb_fixup_file.sh`.
- ⛔ **A grammar edit is invisible until bison/flex are re-run** (`scripts/regenerate_parser_and_lexer_from_sources.sh`) — you should rarely touch parsers.
- ⛔ **NO `-O2` BUILDS.** `RT_OPT` is `-O0`.
- ⛔ **Codegen touched** (`emit*.cpp`, `src/templates/`, `x86_asm.h`, `lower_snobol4.c`) ⇒ regenerate artifacts in order: `util_regen_benchmark_s_artifacts.sh "<rung>"` → `util_regen_demo_s_artifacts.sh` → `util_regen_prolog_bench_s_artifacts.sh`; Icon emitter/lowerer ⇒ also `update_icon_bench_asm.sh`. `util_verify_s_artifacts_owed.sh` is BLOCKING in `handoff_status.sh`.

## Architecture you work in

`src/templates/bb/` (the `bb_*.cpp` boxes), `src/templates/xa/` (emission helpers), `src/templates/x86/x86_asm.h` (the encoder). Every x86 instruction, TEXT and BINARY alike, is produced only inside `x86(...)`; templates speak only `x86(...)` and emit zero binary; raw-byte producers are private to `x86_asm.h`. Byrd-box ports are always α (proceed) β (recede) γ (succeed) ω (concede). THE THREE ZETAS: ζ-SPINE on RSP, ζ-ACTIVATION-FRAME on RBP, ζ-STANDING/root. Language identity stops at lower: no `LANG_*`, no language discriminator in a template or the runtime. The collector design is FROZEN (`ARCH-GC-COMPILE-TIME-FRAME-MAPS.md` § 7): everything on the emitted stack is a DESCR; never add a conservative visit or a pinned block.

**The path from an IR node to a box** (read it before a form census): `src/lower/lower_<lang>.c` chooses the IR kind (`src/ir/IR.h`) → `src/emitter/emit.cpp` `walk_bb_node_inner` is ONE `switch (nd->op)` whose `bb_emit_x86(bb_*())` sites (128 at `7cafd69c0`) bind each IR kind to a template. The form census starts there, counting the kinds bound to each box and the branches inside it → `bb_prepare`/`bb_classify_node` and the case arms fill `g_emit` (`sm_emit_t`), the only thing a template may read (CV10) → the template returns `x86(...)` output, which `x86_asm.h` renders per `g_medium` (`MEDIUM_BINARY`, `src/emitter/emit.h`): binary into the mode-3 slab, text into the mode-4 `.s`. `./scrip --dump-ir` and `--dump-bb` show a program's kinds and boxes without reading the emitter.

## Debugging order

For a red with an instrumented oracle, the monitor bracket first (`bash scripts/monitor_run.sh <prog> --oracle`); then ASM-DIFF-FIRST: minimal witness, diff the emitted `.s` between a passing sibling and the failing witness within ONE mode, grep the instructions (never a comment), and only then gdb.

## Commits and handoff

- **ONE IDENTITY:** `user.name "LCherryholmes"`, `user.email "lcherryh@yahoo.com"`, author and committer; NO `Co-Authored-By` / `Generated with` / `Claude-Session` trailers (the commit-msg hook refuses them). Messages through `git commit -F -` with a quoted heredoc.
- `git pull --rebase` before push; re-prove your A/B after a rebase that touched `emit_*`/`x86_asm.h`/`lower_*`. `git add` NAMED files. Push SCRIP first, `.github` last. Never `reset --hard`, `push --force`, or rewrite history.
- **Handoff** = LIVE CURSOR moved + pushed + `bash SCRIP/scripts/handoff_status.sh` pasted verbatim.

## THE LOOP — the postoffice (law: `/home/resources/postoffice/PROTOCOL.md`)

`s4e_msg.sh check` → act or reply → `clear`; `next` (pick and lock your topmost row); `done <topic>` runs the row's DONE-WHEN and refuses a red; `mint <topic> [rank] --owner <seat> --stdin <<'MSG'` is the only way to add work; `ask <topic> --stdin` to your officer (the cto); `send <seat> <topic> --stdin` — ⛔ an inline body is refused, and a body carrying a backtick or `$(` is refused: write telegrams in words. Never pipe a bus verb into `head`. A question does not stop the work: record the finding, state your assumption, `ask`, carry on. If Lon tells you something that contradicts your brief, Lon wins — then route it the same sitting into your GOAL file AND `send cto override-<topic>`.
