# GOAL-SNOCONE-BEAUTY — Get beauty.sc Working via scrip x86

**Repo:** one4all
**Done when:** `beauty.sc` self-beautifies correctly via `scrip --jit-emit --x64`,
producing output byte-for-byte identical to the SPITBOL oracle on `beauty.sc` itself.

---

## No prerequisite — starting now

`beauty.sno` success is NOT required first. We are doing this in parallel.
The Snocone x86 path is independent of the SNOBOL4 interpreter path.

---

## Current state (diagnosed at goal creation, 2026-04-12)

**The Snocone frontend is NOT wired into scrip.c.**

The pipeline exists in pieces but is not connected:

| Component | File | State |
|-----------|------|-------|
| Lexer | `src/frontend/snocone/snocone_lex.c` | ✅ exists |
| Parser (shunting-yard → RPN) | `src/frontend/snocone/snocone_parse.c` | ✅ exists |
| IR lowerer (RPN → EXPR_t/STMT_t) | `src/frontend/snocone/snocone_lower.c` | ✅ restored from git history |
| scrip.c wiring | `src/driver/scrip.c` | ✅ `.sc` extension → `snocone_compile()` |
| Makefile | `Makefile` | ✅ snocone files added |
| Subsystem runner | `test/beauty-sc/run_beauty_sc_subsystem.sh` | ✅ rewritten for `--ir-run` |

**Correct invocation (once wired):**
```bash
./scrip --jit-emit --x64 driver.sc -o driver.s
nasm -f elf64 -I src/runtime/x86/ driver.s -o driver.o
gcc -no-pie driver.o <rt_archive> -lgc -lm -o driver_bin
./driver_bin
```

**beauty.sc location:** `one4all/test/beauty-sc/beauty/beauty.sc`
Main program body only. Library procedures included via `-sc` include mechanism.

---

## Verification Technique

Claude presents each test result or diff line and asks: **T or F?**

- **T** — assessment correct. Proceed with fix.
- **F** — assessment wrong. Claude re-diagnoses before proceeding.

---

## Steps

- [x] **S-1** — Fix `run_beauty_sc_subsystem.sh`: replace `-sc -x86` flags with
  `--jit-emit --x64`. Update invocation line.
  Gate: script no longer errors on flag parsing (will still fail — Snocone not wired).

- [x] **S-2** — Add snocone files to Makefile:
  `src/frontend/snocone/snocone_lex.c` and `src/frontend/snocone/snocone_parse.c`
  added to the `scrip` object list. Rebuild clean.
  Gate: `make scrip` succeeds with snocone objects included.

- [x] **S-3** — Wire `.sc` extension detection in `scrip.c main()`:
  After `input_path` is known, detect `*.sc` suffix → set `lang_snocone = 1`.
  In parse block: if `lang_snocone`, call `snocone_lex()` + `snocone_parse()`
  instead of `sno_parse()`. Stub out IR lowering with a TODO for now.
  Gate: `./scrip --jit-emit --x64 driver.sc` reaches the snocone parser without
  crashing (parse result may be empty/stub).

- [x] **S-4** — Write `src/frontend/snocone/snocone_lower.c`:
  Takes `ScParseResult` (RPN token array from snocone_parse) → produces
  `EXPR_t/STMT_t` IR identical in shape to what `sno_parse()` produces.
  Start with the simplest subsystem driver (assign) and work up.
  Model: `src/frontend/snobol4/scrip_cc.c` (`cmpile_lower()`).
  Gate: `assign` subsystem driver compiles, assembles, links, runs, passes diff.

## Baseline (2026-04-12, one4all a8e8680e)

- assign ✅  fence ✅  roman ✅ — **3/14 PASS**
- counter/stack/ShiftReduce/semantic: logic correct, output mismatch — likely DATATYPE case issue in IDENT comparisons
- match/strings/arith/trace/global/ReadWrite: partial passes within suite

- [ ] **S-5** — Fix each remaining subsystem driver one at a time (simplest first):
  match, counter, stack, tree, ShiftReduce, TDump, ReadWrite, XDump,
  semantic, omega, trace, fence, global, strings, arith, roman.
  For each: run subsystem script, diagnose failure, fix lowerer or runtime, retest.
  Gate: all present subsystem drivers PASS (skipped ones noted).

- [ ] **S-6** — Run `beauty.sc` end-to-end self-beautification:
  ```bash
  cd /home/claude/one4all
  ./scrip --jit-emit --x64 test/beauty-sc/beauty/beauty.sc -o /tmp/beauty_sc.s
  nasm -f elf64 -I src/runtime/x86/ /tmp/beauty_sc.s -o /tmp/beauty_sc.o
  gcc -no-pie /tmp/beauty_sc.o out/rt_cache/snocone_rt.a -lgc -lm -o /tmp/beauty_sc_bin
  /tmp/beauty_sc_bin < test/beauty-sc/beauty/beauty.sc > /tmp/beauty_sc_out.sc
  /home/claude/x64/bin/sbl -b \
      /home/claude/corpus/programs/snobol4/beauty/beauty.sno \
      < /home/claude/corpus/programs/snobol4/beauty/beauty.sno \
      > /tmp/beauty_oracle.txt
  diff /tmp/beauty_sc_out.sc /tmp/beauty_oracle.txt
  ```
  Gate: diff is empty.

- [ ] **S-7** — Add `test/beauty-sc/run_beauty_sc_full.sh`: end-to-end runner
  that compiles, assembles, links, self-beautifies, diffs oracle. Reports PASS/FAIL.
  Gate: script runs clean, PASS reported.

- [ ] **S-8** — Update PLAN.md: mark ☑ done.

---

## Key files

| File | Role |
|------|------|
| `one4all/test/beauty-sc/beauty/beauty.sc` | Main program body (Snocone port of beauty.sno) |
| `one4all/test/beauty-sc/<sub>/driver.sc` | Per-subsystem Snocone test drivers |
| `one4all/test/beauty-sc/<sub>/driver.ref` | Expected output |
| `one4all/test/beauty-sc/run_beauty_sc_subsystem.sh` | Subsystem test runner (needs S-1 fix) |
| `one4all/src/frontend/snocone/snocone_lex.c` | Lexer ✅ |
| `one4all/src/frontend/snocone/snocone_parse.c` | Shunting-yard parser ✅ |
| `one4all/src/frontend/snocone/snocone_lower.c` | IR lowerer ❌ to be written in S-4 |
| `one4all/src/driver/scrip.c` | Main driver — needs `.sc` wiring in S-3 |
| `one4all/Makefile` | Needs snocone objects added in S-2 |

---

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- SPITBOL (`/home/claude/x64/bin/sbl`) is the oracle.
- No ad-hoc builds — use or extend `one4all/Makefile` and `test/beauty-sc/` scripts.
- Build gate before every commit: `make scrip` clean + `run_interp_broad.sh` PASS count
  must not regress.
