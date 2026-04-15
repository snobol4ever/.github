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

## Two-Step Monitor Protocol (use this every session)

**Step 1 — Monitor diff:**
```bash
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
DRIVER=omega   # or: gen, tdump, alpha, beta, gamma, ...
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno \
    > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
    $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40
```

**Step 2 — Inline probe (Technique C):**
Replace the diverging line in the subsystem file with OUTPUT probes.
Run under both oracles. Compare. Never stlimit tricks.

**Step 3 — SM-run diff:**
```bash
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --sm-run \
    $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/sm.out 2>/dev/null
diff /tmp/spitbol.out /tmp/sm.out | head -40
```

**Step 4 — JIT-run diff:**
```bash
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --jit-run \
    $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/jit.out 2>/dev/null
diff /tmp/spitbol.out /tmp/jit.out | head -40
```

---

## Rung ladder — all modes, x86

Each rung must pass under --ir-run, --sm-run, and --jit-run before
the next rung starts. Gate = diff vs SPITBOL is empty.

### Phase 1 — IR-run (tree-walk interpreter)

- [ ] **SN-1** — beauty.sno self-host: --ir-run.
  Run beauty.sno on itself under scrip-monitor. Cycle through all divergences
  until diff vs SPITBOL is empty. Full loop per divergence:

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty

  # Step A — find first divergence (IR vs SM vs JIT vs CSNOBOL4):
  SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
      $BEAUTY/beauty.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE"

  # Step B — compare one4all vs SPITBOL output:
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty.sno \
      > /tmp/spitbol.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty.sno > /tmp/scrip.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/scrip.out | head -40

  # Step C — isolate with OUTPUT probes in the diverging subsystem file
  #          (Technique C — never stlimit tricks, never modify corpus source
  #           except temporary OUTPUT probes that are reverted after diagnosis)

  # Step D — fix root cause in interp.c / bb_boxes.c / sm_lower.c
  # Step E — make scrip && make scrip-monitor; re-run Step A and Step B
  # Step F — broker gate: bash scripts/test_smoke_unified_broker.sh (PASS=35)
  # Step G — commit; repeat from Step A until diff is empty
  ```

  Gate: `diff /tmp/spitbol.out /tmp/scrip.out` is empty.

- [ ] **SN-2** — beauty omega driver: --ir-run PASS.
  Same divergence-cycling loop as SN-1 but on beauty_omega_driver.sno.
  Known blocker: EVAL(string) via interp_eval_pat (see GOAL-TWO-STEP-HUNT).

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty

  # Outer loop — repeat until diff is empty:

  # Step A — find first divergence:
  SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
      $BEAUTY/beauty_omega_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE"

  # Step B — compare one4all vs SPITBOL:
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_omega_driver.sno \
      > /tmp/spitbol.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty_omega_driver.sno > /tmp/scrip.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/scrip.out | head -40

  # Step C — OUTPUT probe in diverging subsystem to isolate root cause
  # Step D — fix in interp.c / bb_boxes.c
  # Step E — rebuild: make scrip && make scrip-monitor
  # Step F — broker gate: PASS=35 FAIL=1
  # Step G — commit; go back to Step A

  # When diff is empty: Step H — run SM and JIT too:
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --sm-run \
      $BEAUTY/beauty_omega_driver.sno > /tmp/sm.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --jit-run \
      $BEAUTY/beauty_omega_driver.sno > /tmp/jit.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/sm.out | head -20
  diff /tmp/spitbol.out /tmp/jit.out | head -20
  ```

  Gate: all three diffs (--ir-run, --sm-run, --jit-run vs SPITBOL) are empty.

- [ ] **SN-3** — beauty gen driver: --ir-run PASS.
  Same divergence-cycling loop. Known blocker: ARBNO upstream null DT_E.

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty
  # Repeat until diff empty:
  SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
      $BEAUTY/beauty_gen_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE"
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_gen_driver.sno \
      > /tmp/spitbol.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty_gen_driver.sno > /tmp/scrip.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/scrip.out | head -40
  # Fix → rebuild → broker gate → commit → repeat
  ```
  Gate: diff empty (all three modes).

- [ ] **SN-4** — beauty tdump driver: --ir-run PASS.
  Same divergence-cycling loop. Known blocker: DATA field ordering t/v.

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty
  # Repeat until diff empty:
  SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
      $BEAUTY/beauty_tdump_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE"
  SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_tdump_driver.sno \
      > /tmp/spitbol.out 2>/dev/null
  SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
      $BEAUTY/beauty_tdump_driver.sno > /tmp/scrip.out 2>/dev/null
  diff /tmp/spitbol.out /tmp/scrip.out | head -40
  # Fix → rebuild → broker gate → commit → repeat
  ```
  Gate: diff empty (all three modes).

- [ ] **SN-5** — beauty alpha + beta + gamma drivers: --ir-run PASS.
  Same divergence-cycling loop on each driver in turn.

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty
  for DRIVER in alpha beta gamma; do
    SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b \
        $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol_${DRIVER}.out 2>/dev/null
    SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run \
        $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip_${DRIVER}.out 2>/dev/null
    diff /tmp/spitbol_${DRIVER}.out /tmp/scrip_${DRIVER}.out | head -20
  done
  # For each non-empty diff: scrip-monitor --monitor → fix → rebuild → commit → repeat
  ```
  Gate: all three diffs empty (all three modes).

- [ ] **SN-5b** — beauty.sno self-hosts: ALL drivers pass, all three modes.
  This is the "beauty self-hosts" completion gate for Phase 1.
  Run every driver and confirm all diffs empty:

  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/beauty
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

  Gate: all 18 combinations PASS, script prints "BEAUTY SELF-HOSTS".

- [ ] **SN-6** — Full corpus --ir-run: run test_interp_broad_corpus_and_beauty.sh.
  Gate: PASS count matches or exceeds prior baseline; no new failures.

### Phase 2 — SM-run (stack machine interpreter, x86)

- [ ] **SN-7** — beauty.sno self-host: --sm-run.
  Gate: diff vs SPITBOL empty.

- [ ] **SN-8** — beauty omega driver: --sm-run PASS.
  Fix any sm_lower.c or sm_interp.c divergence. Use Step 3 protocol above.
  Gate: diff empty.

- [ ] **SN-9** — beauty gen + tdump drivers: --sm-run PASS.
  Gate: both diffs empty.

- [ ] **SN-10** — Full corpus --sm-run.
  Gate: PASS count matches --ir-run baseline.

### Phase 3 — JIT-run (in-memory x86 code generation)

- [ ] **SN-11** — beauty.sno self-host: --jit-run.
  Gate: diff vs SPITBOL empty.

- [ ] **SN-12** — beauty omega + gen + tdump drivers: --jit-run PASS.
  Gate: all diffs empty.

- [ ] **SN-13** — Full corpus --jit-run.
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

## Current state (2026-04-15, one4all HEAD 099fe2d4)

SN-1 through SN-13 all open. beauty.sno self-host fails.
SN-14 and SN-15 DONE: pattern primitives fully wired as typed EKind nodes
through parser → sm_lower → sm_interp → sm_codegen. No E_FNC fallback for
pattern names anywhere active. Gate: PASS=35 FAIL=1, PASS=7 FAIL=0.
Known blockers for SN-1/SN-2: EVAL(string), ARBNO null DT_E, DATA field ordering.
See GOAL-TWO-STEP-HUNT for detailed bug queue.

Next session: SN-2 — use scrip-monitor + beauty_omega_driver.sno divergence
cycling loop (see "--monitor with CSNOBOL4" section above).
Broker gate: PASS=35 FAIL=1 (cross_lang.scrip pre-existing Icon gap).

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


