# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle. Two-step
monitor + extended probe finds and fixes all remaining divergences.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup (must be clean before any work):
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=31
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh       # 3-mode divergence check
```

---

## Architecture reminder

```
.sno → sno_parse() → Program* [LANG_SNO]
    --ir-run  → execute_program() → interp_eval()   tree-walk
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()
```

Pattern matching uses BB_SCAN (the Byrd-box broker in scan mode).
Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol — PRIMARY TOOL FOR EVERY LADDER RUN

⛔ **Step 1 (`scrip-monitor --monitor`) is run EVERY iteration, unconditionally, no exceptions.**
⛔ **Steps 2 and 3 are only run if Step 1 finds a problem (DIVERGE or IR vs CSN).**
⛔ **Never skip Step 1. Never jump straight to the SPITBOL diff.**

**Build scrip-monitor once per session (after build_scrip.sh):**
```bash
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a
```

**Step 1 — ALWAYS: `scrip-monitor --monitor` (IR vs SM vs JIT vs CSNOBOL4)**
Run unconditionally every iteration. If clean → done, move on. If DIVERGE → continue to Step 2.
```bash
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"
```

**Step 2 — Only if Step 1 shows a problem: SPITBOL diff (measure output correctness)**
SPITBOL is the primary oracle. Shows what the correct output looks like and how far off we are.
```bash
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b \
    $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
    $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40
```

**Step 3 — Only if Step 1 shows a problem: Inline OUTPUT probe (Technique C)**
Isolate root cause in the diverging subsystem file. Revert probes after diagnosis.
Fix in interp.c / bb_boxes.c / sm_lower.c as appropriate.

**After fix — rebuild, then Step 1 again:**
```bash
make -C /home/claude/one4all scrip && \
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a
# Then: Step 1 → if clean → broker gate → commit
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh
```

**SM-run and JIT-run (after IR-run Step 1 is clean):**
Run Step 1 for each mode. Only proceed to Steps 2+3 if Step 1 shows a problem.
```bash
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --sm-run \
    $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/sm.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --jit-run \
    $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/jit.out 2>/dev/null
diff /tmp/spitbol.out /tmp/sm.out | head -20
diff /tmp/spitbol.out /tmp/jit.out | head -20
# Any divergence → back to Step 1 on that mode
```

---

## Rung ladder — all modes, x86

Each rung must pass under --ir-run, --sm-run, and --jit-run before
the next rung starts. Gate = diff vs SPITBOL is empty.

### Phase 1 — IR-run (tree-walk interpreter)

- [ ] **SN-1** — beauty omega driver: --ir-run PASS.
  Two-step dance every iteration unconditionally until diff is empty.
  Known blocker: EVAL(string) via interp_eval_pat (see GOAL-TWO-STEP-HUNT).

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty

  # Repeat: Step 1 every time; Steps 2+3 only if Step 1 shows a problem.

  # Step 1 — ALWAYS: scrip-monitor --monitor (IR vs SM vs JIT vs CSNOBOL4)
  SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
      $BEAUTY/beauty_omega_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"
  # If clean → broker gate → done. If DIVERGE → continue:

  # Step 2 — only if Step 1 shows problem: SPITBOL diff
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_omega_driver.sno \
      > /tmp/spitbol.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty_omega_driver.sno > /tmp/scrip.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/scrip.out | head -40

  # Step 3 — only if Step 1 shows problem: OUTPUT probe (Technique C) → fix
  # Fix in interp.c / bb_boxes.c / sm_lower.c; revert probes after diagnosis
  # Rebuild: make scrip && make scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a
  # Broker gate: bash scripts/test_smoke_unified_broker.sh
  # Commit; go back to Step 1

  # When Step 1 is clean for --ir-run — run SM and JIT (Step 1 for each):
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --sm-run \
      $BEAUTY/beauty_omega_driver.sno > /tmp/sm.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --jit-run \
      $BEAUTY/beauty_omega_driver.sno > /tmp/jit.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/sm.out | head -20
  diff /tmp/spitbol.out /tmp/jit.out | head -20
  ```

  Gate: all three diffs (--ir-run, --sm-run, --jit-run vs SPITBOL) are empty.

- [ ] **SN-2** — beauty gen driver: --ir-run PASS.
  Two-step dance every iteration unconditionally.
  Known blocker: BREAK(nl) fails when subject is $'$B' (indirect variable) in
  exec_stmt pattern match. NV_GET_fn("$B") returns descriptor where
  descr_slen/Ω is wrong. BREAK with plain var works; only fails for $'name'
  indirect subject. Next probe: compare descr_slen(NV_GET_fn("$B")) vs plain var.

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty
  # Repeat: Step 1 every time; Steps 2+3 only if Step 1 shows a problem.

  # Step 1 — ALWAYS: scrip-monitor --monitor (IR vs SM vs JIT vs CSNOBOL4)
  SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
      $BEAUTY/beauty_Gen_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"
  # If clean → broker gate → done. If DIVERGE → continue:

  # Step 2 — only if Step 1 shows problem: SPITBOL diff
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_Gen_driver.sno \
      > /tmp/spitbol.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty_Gen_driver.sno > /tmp/scrip.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/scrip.out | head -40

  # Step 3 — only if Step 1 shows problem: OUTPUT probe → fix → rebuild → repeat
  # Fix → rebuild (make scrip && make scrip-monitor CSN_A=...) → broker gate → commit → Step 1
  # When Step 1 clean for --ir-run: run --sm-run and --jit-run (Step 1 each)
  ```
  Gate: diff empty (all three modes).

- [ ] **SN-3** — beauty tdump driver: --ir-run PASS.
  Two-step dance every iteration unconditionally. Known blocker: DATA field ordering t/v.

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty
  # Repeat: Step 1 every time; Steps 2+3 only if Step 1 shows a problem.

  # Step 1 — ALWAYS: scrip-monitor --monitor (IR vs SM vs JIT vs CSNOBOL4)
  SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
      $BEAUTY/beauty_TDump_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"
  # If clean → broker gate → done. If DIVERGE → continue:

  # Step 2 — only if Step 1 shows problem: SPITBOL diff
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_TDump_driver.sno \
      > /tmp/spitbol.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty_TDump_driver.sno > /tmp/scrip.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/scrip.out | head -40

  # Step 3 — only if Step 1 shows problem: OUTPUT probe → fix → rebuild → repeat
  # Fix → rebuild (make scrip && make scrip-monitor CSN_A=...) → broker gate → commit → Step 1
  # When Step 1 clean for --ir-run: run --sm-run and --jit-run (Step 1 each)
  ```
  Gate: diff empty (all three modes).

- [ ] **SN-4** — beauty alpha + beta + gamma drivers: --ir-run PASS.
  Two-step dance every iteration unconditionally, for each driver in turn.

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty
  for DRIVER in alpha beta gamma; do
    # Step 1 — ALWAYS: scrip-monitor --monitor
    SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
        $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

    # Step 2 — ALWAYS: SPITBOL diff
    SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b \
        $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol_${DRIVER}.out 2>/dev/null
    SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
        $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip_${DRIVER}.out 2>/dev/null
    diff /tmp/spitbol_${DRIVER}.out /tmp/scrip_${DRIVER}.out | head -20
  done
  # For each non-empty diff: fix → rebuild (make scrip && make scrip-monitor CSN_A=...) → commit → repeat
  ```
  Gate: all three diffs empty (all three modes).

- [ ] **SN-5** — beauty.sno self-hosts: ALL drivers pass + self-host, all three modes.
  Run-ups (SN-1..SN-4) must all be green first. Then confirm beauty.sno
  self-hosts (runs beauty.sno on itself) and all drivers pass:

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty

  # Self-host check:
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty.sno \
      > /tmp/spitbol_self.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty.sno > /tmp/scrip_self.out 2>/dev/null
  diff /tmp/spitbol_self.out /tmp/scrip_self.out | head -40

  # Full 18-combination gate (all drivers × all modes):
  ALL_PASS=1
  for DRIVER in omega gen tdump alpha beta gamma; do
    for MODE in --ir-run --sm-run --jit-run; do
      SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b \
          $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/ref.out 2>/dev/null
      SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip $MODE \
          $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/out.out 2>/dev/null
      DIFF=$(diff /tmp/ref.out /tmp/out.out)
      if [[ -n "$DIFF" ]]; then
        echo "FAIL $DRIVER $MODE"; ALL_PASS=0
      else
        echo "PASS $DRIVER $MODE"
      fi
    done
  done
  [[ $ALL_PASS -eq 1 ]] && echo "BEAUTY SELF-HOSTS"
  ```

  Gate: self-host diff empty AND all 18 driver combinations PASS.
  Script prints "BEAUTY SELF-HOSTS".

- [ ] **SN-6** — Full corpus --ir-run: run test_interp_broad_corpus_and_beauty.sh.
  Gate: PASS count matches or exceeds prior baseline; no new failures.

### Phase 2 — SM-run (stack machine interpreter, x86)

- [ ] **SN-7** — beauty omega + gen + tdump drivers: --sm-run PASS.
  Fix any sm_lower.c or sm_interp.c divergence. Same cycling loop.
  Gate: all diffs empty vs SPITBOL.

- [ ] **SN-8** — beauty alpha + beta + gamma drivers + self-host: --sm-run PASS.
  Gate: all diffs empty.

- [ ] **SN-9** — Full corpus --sm-run.
  Gate: PASS count matches --ir-run baseline.

### Phase 3 — JIT-run (in-memory x86 code generation)

- [ ] **SN-10** — beauty omega + gen + tdump drivers: --jit-run PASS.
  Gate: all diffs empty vs SPITBOL.

- [ ] **SN-11** — beauty alpha + beta + gamma drivers + self-host: --jit-run PASS.
  Gate: all diffs empty.

- [ ] **SN-12** — Full corpus --jit-run.
  Gate: PASS count matches --sm-run baseline.

### Phase 4 — Pattern IR typing (GOAL-SNOBOL4-PAT-IR prerequisite)

- [x] **SN-14** — Pattern primitives as typed EKind nodes (E_ANY, E_SPAN, etc.).
  Rewrite parser actions: E_FNC("ANY",...) → E_ANY(...) immediately post-parse.
  Gate: make scrip clean; PASS=31; no strcasecmp(e->sval,"ANY") anywhere.

- [x] **SN-15** — Verify all three modes still pass after SN-14.
  Gate: SN-6, SN-10, SN-13 gates still hold.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/snobol4.y` | Bison grammar — parser actions |
| `src/frontend/snobol4/snobol4.l` | Flex lexer |
| `src/driver/interp.c` | --ir-run tree-walk (shared with all frontends) |
| `src/runtime/x86/sm_lower.c` | IR → SM (shared) |
| `src/runtime/x86/sm_interp.c` | SM interpreter (shared) |
| `src/runtime/x86/sm_codegen.c` | x86 JIT (shared) |
| `src/runtime/x86/bb_boxes.c` | All SNOBOL4 pattern boxes |
| `corpus/programs/snobol4/beauty/` | Beauty test suite (oracle: SPITBOL) |

---

## Invariants — never break these

- SPITBOL is the sole oracle. If SPITBOL runs it correctly, fix the runtime.
- Never modify corpus .sno source to work around runtime bugs.
- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-15, one4all HEAD 01b3af41)

SN-14 and SN-15 DONE (prior session).
SN-1 DONE: omega driver PASS all three modes (IR/SM/JIT vs SPITBOL diff empty).
  Fix: ASGN_INDIR last_ok hardcoded=1 in sm_interp.c + sm_codegen.c.
  Also: subscript_set/set2 changed void→int with ARBLK bounds check.
  Broker gate after fix: PASS=37 FAIL=0.

SN-2 BLOCKED: Gen driver — pattern sequence failure in IR.
  Root cause isolated: BREAK(nl) . pre nl REM . post fails in IR but passes SPITBOL.
  Minimal repro confirmed:
    nl = CHAR(10)
    B = 'hello' nl 'world'
    B BREAK(nl) . pre nl REM . post   :F(FAIL)  → IR takes :F, SPITBOL takes :S
  Fixes this session (HEAD 01b3af41):
    - execute_program E_INDIRECT assignment: restructured to eval repl_val first,
      then eval child expr for variable name string (fixes $UTF_Array[i,2] = val).
    - Reverted erroneous !has_eq guard on S=PR split (broke pattern smoke test).
    - Comment clarifications to E_QLIT subj_name resolution ($'name' semantics).
  Still broken: exec_stmt BB pattern engine — sequential pattern
    BREAK(nl) . capture, nl, REM . capture fails at the nl literal match
    after BREAK advances cursor. Investigate bb_broker/seq_t cursor handling.
  Gate: PASS=7 FAIL=0 (smoke), PASS=37 FAIL=0 (broker)

Next session: SN-2 — fix BREAK(nl) . pre nl REM . post sequence in BB engine.

---

## --monitor with CSNOBOL4: beauty.sno divergence hunting (IM-16 technique)

`scrip-monitor` (built with `make scrip-monitor CSN_A=...`) adds CSNOBOL4 as a
4th in-process executor. At the final statement it compares one4all IR/SM/JIT NV
state against CSNOBOL4's NV state and reports any variable that differs.

**Build scrip-monitor (once per session):**
```bash
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a
```

**Run on a single beauty subsystem file:**
```bash
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
/home/claude/one4all/scrip-monitor --monitor $BEAUTY/beauty_omega_driver.sno
```

**What the output means:**
- `IR=SM=JIT agree` per-stmt → all three one4all executors match (good)
- `DIVERGE at stmt N` → one4all executors diverge from each other at stmt N
- `IR vs CSN (N var(s) differ)` → one4all IR final state differs from CSNOBOL4 at
  program end; lists each variable with IR value and CSN value side by side

**Workflow for beauty.sno divergences:**

1. Run the beauty smoke script to see which programs diverge:
   ```bash
   bash /home/claude/one4all/scripts/test_monitor_beauty_smoke.sh
   ```

2. For any DIVERGE, run `--monitor` directly on that file:
   ```bash
   /home/claude/one4all/scrip-monitor --monitor <file.sno> 2>&1 | grep -A5 "DIVERGE"
   ```
   The output names the exact statement number, label, line, and differing variables.

3. For beauty.sno with `SNO_LIB` includes, the driver file is the entry point:
   ```bash
   # beauty_omega_driver.sno INCLUDEs the subsystem files via SNO_LIB
   SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
       $BEAUTY/beauty_omega_driver.sno 2>&1 | grep -A 10 "DIVERGE"
   ```

4. Cross-check diverging variable against SPITBOL oracle:
   ```bash
   SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_omega_driver.sno \
       > /tmp/spitbol.out 2>/dev/null
   ```
   The CSNOBOL4 value in the `IR vs CSN` report is a second reference point.
   When IR≠CSN: one4all has a bug. When IR=CSN≠SPITBOL: CSNOBOL4 also has the bug
   (use SPITBOL as the authoritative oracle; CSNOBOL4 is secondary).

5. Use Technique C (inline OUTPUT probes) to isolate the root cause in the
   subsystem file, then fix in `interp.c`, `sm_lower.c`, or `bb_boxes.c`.

**Known limitations of scrip-monitor + beauty.sno:**
- CSN comparison is final-state only (not per-stmt) — identifies WHICH variable
  diverged but not exactly WHICH statement caused it for the CSN leg.
- OPSYN and indirect references may crash CSNOBOL4 (SKIP, not one4all bug).
- beauty.sno uses `SNO_LIB` for includes — pass the env var to scrip-monitor.
- Per-stmt IR/SM/JIT comparison still works fully for finding one4all-internal
  divergences even when the CSN leg is skipped.

**Known divergences from IM-16 session (2026-04-15):**
```
032_goto_loop_count.sno  — DIVERGE at stmt 4  [label: -, line 0]
1110_array_1d.sno        — DIVERGE at stmt 8  [label: e002, line 16]  (ARRAY indexing)
1113_table.sno           — DIVERGE at stmt 8  [label: e002, line 16]  (TABLE indexing)
```
These are one4all IR vs CSNOBOL4 NV-state gaps — investigate before fixing beauty.sno
subsystems that exercise ARRAY or TABLE operations.


