# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle.

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

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Architecture reminder

```
.sno -> sno_parse() -> Program* [LANG_SNO]
    --ir-run  -> execute_program() -> interp_eval()   tree-walk
    --sm-run  -> sm_lower() -> SM_Program -> sm_interp_run()
    --jit-run -> sm_lower() -> SM_Program -> sm_codegen() -> sm_jit_run()
```

Pattern matching uses BB_SCAN. Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol

Step 1 (--monitor) runs EVERY iteration, unconditionally.
Steps 2 and 3 only if Step 1 shows DIVERGE or IR vs CSN.

```bash
# Build once per session:
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Step 1 -- ALWAYS:
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

# Step 2 -- only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40

# Step 3 -- only if Step 1 shows problem: OUTPUT probe -> fix -> rebuild -> repeat
# Rebuild: make scrip && make scrip-monitor CSN_A=...
# Broker gate: bash scripts/test_smoke_unified_broker.sh
```

---

## Rung ladder

### Phase 1 -- IR-run  DONE (SN-1..SN-5, SN-14, SN-15, SN-16, SN-19)
### Phase 2 -- SM-run  (SN-7..SN-9, gated on SN-6)
### Phase 3 -- JIT-run (SN-10..SN-12, gated on SN-9)

- [x] **SN-20** -- NAM push/pop self-unwinding (`*var-holds-DT_E` thaw folded
      into `name_commit_value` at SN-21e).  HEAD `8964586e`.

- [x] **SN-21** -- Unified `NAME_t` + flat NAM stack; one lvalue concept,
      one push/pop API, one `bb_cap` box for `.` / `$` / `NRETURN` / `*fn()`.
      Ladder SN-21a..e landed across multiple sessions; full design rationale
      in the SN-21a..e commit messages.  HEAD `8964586e` (SN-21e).

- [ ] **SN-17** -- **CURRENT.** Porter stemmer gap.

  **Measured at HEAD `8964586e`:**
  - `--ir-run`: 19674 / 23531 matched = **83.60%** (baseline 83.46%)
  - `--sm-run`: 14317 / 23531 matched = **60.84%** (baseline 60.64%)
  - Broad corpus: PASS=223/225 (unchanged).

  **SN-21e did not move Porter.**  Verified byte-identical output
  at pre-SN-21e `13fc94dd` and post-SN-21e `8964586e`.  The DT_E
  thaw fold is live but no test in the gap reaches it — Porter is
  not a `*var-holds-DT_E` case.

  **Gap shape** (first divergences, SPITBOL vs ours):
  ```
  abate     → abat   vs  ab
  abated    → abat   vs  ab
  abatement → abat   vs  (empty)
  abates    → abat   vs  (empty)
  absence   → absenc vs  abs
  ```
  Consistent over-stripping.  Porter's measure tests (`m>0`, `m>1`)
  count vowel/consonant sequences via patterns; when they mis-fire,
  step-1c / step-5 strips suffixes that should be kept.  Likely
  `bb_cap` × ARBNO-wrapped alternation in the measure pattern.

  **Next action:** instrument `abate` through the measure-test path
  in both SPITBOL and scrip `--ir-run`, compare each match attempt.

  ```bash
  cd /home/claude/corpus/programs/snobol4/demo
  /home/claude/one4all/scrip --ir-run porter.sno < porter.input | diff - porter.ref | wc -l
  /home/claude/one4all/scrip --sm-run porter.sno < porter.input | diff - porter.ref | wc -l
  ```

- [ ] **SN-6** -- Full corpus: PASS=223/225 default, 224/225 --ir-run.
  Remaining: `expr_eval` (two separate bugs — see below), `demo_claws5`
  (GOAL-SNO-CLAWS5.md).
  ```bash
  bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
  ```

  **expr_eval diagnostic (measured at `8964586e`):**
  - `--ir-run`: 4/5 inputs → `snobol4:0: error: parse error: syntax error`.
    That is the SNOBOL4 *frontend parser*, not a pattern-match error —
    `EVAL(op arg)` is probably compiling the evaluated string as SNOBOL4
    statements.  The 2 lines that do parse produce wrong values:
    `(1+2)*3` → `3` (expected 9), `-3+10` → `10` (expected 7).  Two
    layered bugs: EVAL call path + operator precedence / Pop() ordering.
  - `--sm-run`: 5/5 → `Bad input, try again`.  The top-level
    `POS(0) expr RPOS(0)` pattern fails for every input.  Recursive
    `primary = constant | '(' *expr ')'` via bb_cap / NM_CALL is the
    likely fault line.

  Not DT_E (verified identical at pre-SN-21e).

- [ ] **SN-7** -- beauty.sno self-host: 6 drivers × 3 modes = 18 combos,
  diff=0 vs SPITBOL. Gate: smoke PASS=7, broker PASS=49, all 18 diff=0.

---

## Key files

| File | Role |
|------|------|
| src/frontend/snobol4/snobol4.y | Bison grammar |
| src/frontend/snobol4/snobol4.l | Flex lexer |
| src/driver/interp.c | --ir-run tree-walk |
| src/runtime/x86/sm_lower.c | IR -> SM |
| src/runtime/x86/sm_interp.c | SM interpreter |
| src/runtime/x86/sm_codegen.c | x86 JIT |
| src/runtime/x86/bb_boxes.c | SNOBOL4 pattern boxes (incl. `bb_cap`) |
| src/runtime/x86/snobol4_nmd.c | Flat NAM stack: NAME_push/pop + NAME_top/pop_above |
| src/runtime/x86/stmt_exec.c | exec_stmt, bb_deferred_var |
| src/runtime/x86/name_t.h | NAME_t, NameKind_t, name_commit_value |
| src/runtime/x86/name_t.c | name_commit_value dispatch + name_init_as_* builders |
| corpus/programs/snobol4/beauty/ | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state

**HEAD:** one4all @ `8964586e`. Gates: Smoke 7, Broker 49.
**Next step:** SN-17 Porter stemmer — trace `abate` through measure-test path.
