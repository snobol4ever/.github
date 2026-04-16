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

## Current state (2026-04-16, one4all HEAD 311ec18c)

SB-1 DONE: 9 underflow sites diagnosed.
SB-2 DONE: $'...' lexer fix.
SB-3 DONE: scan+replacement lowerer fix. 0 underflows.

PIVOT (this session): No assembly. No awk. No Python. No preprocessing.
scrip --ir-run takes multiple .sc files natively — each compiled as a separate
module, IR merged in source order. DEFINE_fn already handles redefinition
(replaces, does not hang). The plan: write clean per-subsystem .sc files by
hand, pass them all to scrip in order with beauty.sc last.

Removed this session:
  scripts/util_assemble_beauty_driver.sh  — deleted
  scripts/util_bisect_beauty_hang.sh      — deleted
  snocone_lex export/import additions     — reverted (premature)

Existing .sc files in test/beauty-sc/beauty/:
  Gen.sc, Qize.sc, TDump.sc, XDump.sc, omega.sc, io.sc, case.sc

Still needed as clean hand-written .sc files (no driver bodies):
  global.sc, assign.sc, match.sc, counter.sc, stack.sc, tree.sc,
  ShiftReduce.sc (Shift+Reduce only), ReadWrite.sc, semantic.sc, trace.sc

Gates: smoke PASS=5 FAIL=0.

NEXT STEP: SB-4 — write the missing clean .sc files by hand; run full
  scrip --ir-run global.sc ... beauty.sc < trivial_input; compare to oracle.

---

## Steps

- [x] **SB-1** — Diagnose underflows. HEAD db91b92c.
- [x] **SB-2** — Fix $'...' dollar-quoted identifier lexing. ✅
- [x] **SB-3** — Fix scan+replacement lowering. 0 underflows. ✅

- [ ] **SB-4** — Write clean per-subsystem .sc files by hand in test/beauty-sc/:
  global.sc, assign.sc, match.sc, counter.sc, stack.sc, tree.sc,
  ShiftReduce.sc (Shift+Reduce only — stack procs live in stack.sc),
  ReadWrite.sc, semantic.sc, trace.sc.
  No driver test bodies. No &STLIMIT. Procedures only.
  Gate: each file runs without hang under scrip --ir-run with /dev/null input.

- [ ] **SB-5** — Run beauty.sc end-to-end:
  ```bash
  ./scrip --ir-run \
      test/beauty-sc/global.sc test/beauty-sc/case.sc test/beauty-sc/io.sc \
      test/beauty-sc/assign.sc test/beauty-sc/match.sc test/beauty-sc/counter.sc \
      test/beauty-sc/stack.sc test/beauty-sc/tree.sc test/beauty-sc/ShiftReduce.sc \
      test/beauty-sc/beauty/Gen.sc test/beauty-sc/beauty/Qize.sc \
      test/beauty-sc/ReadWrite.sc \
      test/beauty-sc/beauty/TDump.sc test/beauty-sc/beauty/XDump.sc \
      test/beauty-sc/semantic.sc test/beauty-sc/beauty/omega.sc \
      test/beauty-sc/trace.sc \
      test/beauty-sc/beauty/beauty.sc < trivial_input.sno
  ```
  Compare to SPITBOL oracle. Gate: outputs match.

- [ ] **SB-6** — Self-beautify: feed beauty.sc to itself. Gate: diff empty.

- [ ] **SB-7** — Write scripts/test_snocone_beauty_self.sh. Broker gate PASS=44+.
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
