# GOAL-SNOCONE-BEAUTY — beauty.sc Self-Beautifies via scrip

**Repo:** one4all
**Done when:** `./scrip --ir-run test/beauty-sc/beauty/beauty.sc < input.sno`
produces output byte-for-byte identical to SPITBOL running `beauty.sno` on
the same input. Gate script reports PASS.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh              # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh   # PASS=42 SKIP=3
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh       # PASS=44
```

## SB-4 Scripts (use these — no ad-hoc shell)

```bash
# 1. Assemble beauty/driver.sc from all subsystem .sc files:
bash scripts/util_assemble_beauty_driver.sh
#    writes test/beauty-sc/beauty/driver.sc
#    --output PATH   write to a different path
#    --dry-run       print to stdout only

# 2. Binary-search for the line that causes a hang:
bash scripts/util_bisect_beauty_hang.sh
#    --driver PATH   assembled driver (default: test/beauty-sc/beauty/driver.sc)
#    --lines N       single probe at line N instead of bisecting
#    --timeout N     seconds per probe (default: 5)
#    --mode MODE     --ir-run | --sm-run | --jit-run

# 3. Run SPITBOL oracle on a .sno input (cd to beauty/ include dir automatically):
bash scripts/util_run_beauty_oracle.sh --input FILE
#    --output FILE   write ref to file
#    --corpus PATH   corpus root (default: /home/claude/corpus)

# 4. Run beauty/driver.sc via scrip; optionally diff against oracle:
bash scripts/util_run_beauty_sc.sh --input FILE
#    --compare       also run oracle, print PASS/FAIL + diff
#    --ref FILE      diff against pre-baked .ref instead of running oracle
#    --mode MODE     --ir-run | --sm-run | --jit-run
```

---

## Current state (2026-04-16, one4all HEAD 18952c2d)

SB-1 DONE: 9 underflow sites diagnosed — dollar-quoted idents + scan+replacement.
SB-2 DONE: $'...' lexer fix — both lex loops patched. Gate passes.
SB-3 DONE: ~(subj ? pat) parser fix + scan+replacement lowerer fix. 0 underflows.
SB-4 IN PROGRESS: missing Snocone library ports written; assembly hang being fixed.

Gates: smoke PASS=5, beauty PASS=42 SKIP=3, broker PASS=44.
corpus repo cloned to /home/claude/corpus (oracle include files confirmed present).

New .sc files written this session (in test/beauty-sc/beauty/):
  Qize.sc    — Qize/SQize/DQize/SqlSQize/Intize/Extize/LEQ/Ucvt
  TDump.sc   — TValue/TDump/TLump
  XDump.sc   — XDump
  omega.sc   — TV/TW/TX/TY/TZ
  io.sc      — stub (INPUT/OUTPUT already built-in under scrip)

New scripts written (in scripts/):
  util_assemble_beauty_driver.sh  — assembles driver.sc from subsystem parts
  util_bisect_beauty_hang.sh      — binary-searches for hang line in assembled file
  util_run_beauty_oracle.sh       — runs SPITBOL oracle from correct include dir
  util_run_beauty_sc.sh           — runs beauty/driver.sc via scrip, optional compare

BLOCKER (active): util_assemble_beauty_driver.sh still produces a hang.
Root cause confirmed via util_bisect_beauty_hang.sh:
  ShiftReduce/driver.sc re-emits InitStack/Push/Pop/Top bodies already present
  from stack/driver.sc. Second definition of InitStack at assembled line ~169 hangs.
  struct link dedup works. Proc-body dedup in strip_stack_procs() awk is broken:
  single-line proc "procedure Foo() { ... }" — awk depth counter resets skip=0
  but outer `next` is never reached; multi-line bodies also not stripped correctly.

NEXT STEP (SB-4 continued):
  Fix strip_stack_procs() in util_assemble_beauty_driver.sh so it correctly
  strips all four proc bodies (single-line and multi-line) from ShiftReduce section.
  Then re-run util_bisect_beauty_hang.sh — should report "no hang found".
  Then run: bash scripts/util_run_beauty_sc.sh --input test/beauty-sc/beauty/beauty.sc
             bash scripts/util_run_beauty_oracle.sh --input corpus/programs/snobol4/demo/beauty.sno
             (note: oracle needs trivial .sno input, not beauty.sc itself at this stage)
  Then compare outputs.

---

## Steps

- [x] **SB-1** — Diagnose: confirmed 9 underflow sites — two categories:
  (a) `$'...'` dollar-quoted identifiers (lines 477,489,517,523,525)
  (b) `subject ? pattern = ;` scan+replacement (lines 21,25,28,64).
  Added line-number annotation to es_pop() for diagnosis. one4all HEAD db91b92c.

- [x] **SB-2** — Fix `$'...'` dollar-quoted identifier lexing.
  snocone_lex.c: intercept `$'` before operator longest-match in both lex
  loops; emit SNOCONE_IDENT with spelling `$<content>` (e.g. `$=`, `$Id`).
  Gate: `$'=' = 'hello'; OUTPUT = $'=';` prints `hello`. ✅

- [x] **SB-3** — Fix scan+replacement lowering (two fixes):
  1. snocone_parse.c parse_operand_into: grouping paren now fully recurses
     into balanced interior via snocone_parse() — fixes `~(subject ? pat)`.
  2. snocone_lower.c SNOCONE_ASSIGN handler: detects empty-LHS postfix and
     builds E_ASSIGN(E_SCAN, empty-repl); assemble_stmt unwraps into proper
     scan+replacement STMT. Fixes `subject ? pat = ;` form.
  Gate: `s ? SPAN('abc') = ; OUTPUT = s;` prints `def`. ✅
  beauty.sc: 0 underflows (was 9). one4all HEAD db91b92c.

- [ ] **SB-4** — Run beauty.sc on a trivial SNOBOL4 input, compare to SPITBOL oracle.
  ```bash
  echo '        X = 1' | ./scrip --ir-run test/beauty-sc/beauty/beauty.sc
  /home/claude/x64/bin/sbl -b /home/claude/one4all/test/beauty-sc/beauty/beauty.sno <<< '        X = 1'
  ```
  Gate: outputs match. (beauty.sno path TBD — may need corpus clone.)

- [ ] **SB-5** — Self-beautify: feed beauty.sc to itself, compare to SPITBOL oracle
  running beauty.sno on beauty.sc.
  Gate: diff is empty.

- [ ] **SB-6** — Write `scripts/test_snocone_beauty_self.sh`: end-to-end runner.
  Gate: PASS reported, integrated into CI.

- [ ] **SB-7** — Broker gate: `test_smoke_unified_broker.sh` PASS=36 FAIL=0.
  Commit. Push. Update PLAN.md ☑.

---

## Key constructs to fix

| Construct | Example | Fix location |
|-----------|---------|-------------|
| `$'...'` quoted identifier | `$'=' = *White && '=' && *White;` | `snocone_lex.c` |
| `*deref` in pattern/replacement | `ppArgs ? ('--' && *ppTokNamePat . cap) = ;` | `snocone_lower.c` |

---

## Invariants

- Gate = PASS=36 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- SPITBOL is the oracle. .ref from `sbl -b`.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
