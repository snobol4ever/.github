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
  Run beauty.sno on itself. Compare output to SPITBOL.
  Gate: diff empty.

- [ ] **SN-2** — beauty omega driver: --ir-run PASS.
  Two-step monitor to find divergence. Fix root cause in interp.c.
  Known blocker: EVAL(string) via interp_eval_pat (see GOAL-TWO-STEP-HUNT).
  Gate: diff /tmp/spitbol.out /tmp/scrip.out is empty.

- [ ] **SN-3** — beauty gen driver: --ir-run PASS.
  Known blocker: ARBNO upstream null DT_E (see GOAL-TWO-STEP-HUNT).
  Gate: diff empty.

- [ ] **SN-4** — beauty tdump driver: --ir-run PASS.
  Known blocker: DATA field ordering t/v (see GOAL-TWO-STEP-HUNT).
  Gate: diff empty.

- [ ] **SN-5** — beauty alpha + beta + gamma drivers: --ir-run PASS.
  Gate: all three diffs empty.

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

- [ ] **SN-14** — Pattern primitives as typed EKind nodes (E_ANY, E_SPAN, etc.).
  Rewrite parser actions: E_FNC("ANY",...) → E_ANY(...) immediately post-parse.
  Gate: make scrip clean; PASS=31; no strcasecmp(e->sval,"ANY") anywhere.

- [ ] **SN-15** — Verify all three modes still pass after SN-14.
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

## Current state (2026-04-14, one4all HEAD 43dc03da)

SN-1 through SN-13 all open. beauty.sno self-host fails.
Known blockers: EVAL(string), ARBNO null DT_E, DATA field ordering.
See GOAL-TWO-STEP-HUNT for detailed bug queue.
Next: SN-2 — fix EVAL(string) in interp.c via two-step monitor.
