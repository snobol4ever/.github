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

- [ ] **SN-6** -- Full corpus: PASS=223/225. IN PROGRESS.

```bash
bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
```

- [ ] **SN-7** -- beauty.sno self-host bootstrap: all 6 drivers x 3 modes = 18 combos,
  diff=0 vs SPITBOL oracle for each. Has never passed.
  Gate: smoke PASS=7, broker PASS=49, all 18 combos diff=0.

- [ ] **SN-17** -- Porter stemmer under one4all -- close the SPITBOL gap.

  | Mode             | Accuracy |
  |------------------|----------|
  | SPITBOL (oracle) | 100.00%  |
  | --ir-run         | 83.46%   |
  | --sm-run         | 60.64%   |

  Root cause: commit-time *fn() dispatch; NAM rollback missing NAM_KIND_CALLCAP.
  Fix SN-6 Bug #1d first; Porter gap expected to close as a side-effect.

  Gate:
  ```bash
  cd /home/claude/corpus/programs/snobol4/demo
  /home/claude/one4all/scrip --ir-run porter.sno < porter.input | diff - porter.ref | wc -l
  /home/claude/one4all/scrip --sm-run porter.sno < porter.input | diff - porter.ref | wc -l
  ```

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
| src/runtime/x86/bb_boxes.c | SNOBOL4 pattern boxes |
| src/runtime/x86/snobol4_nmd.c | NAM_push / NAM_commit / NAM_discard |
| src/runtime/x86/stmt_exec.c | exec_stmt, bb_capture, flush_pending |
| corpus/programs/snobol4/beauty/ | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-19 -- SN-6 session 12, PASS=223/225)

**HEAD:** one4all 2c8d4a79 -- stmt_exec.c XNME/XFNME NAMEVAL-aware varname
extraction (Bug #1d fix). word1 now passes under --sm-run.

**Gates:** Smoke PASS=7, broker PASS=49, broad 223/225.

### SN-6 remaining failures (2 of 225)

- `expr_eval` -- 1+2*3 -> 2 (ir); "Bad input, try again" (sm).
  Commit-time *fn() dispatch (Bug #1 family). Separate from word1.
- `demo_claws5` -- see GOAL-SNO-CLAWS5.md (separate goal).

### word1 diagnosis -- RESOLVED (session 12, 2026-04-19)

Probes on NAM_push / NAM_commit revealed --sm-run passed
`varname=NULL, var_ptr=non-NULL` where --ir-run passed
`varname="OUTPUT", var_ptr=NULL`. At the build site, `p->var.s`
contained "OUTPUT" on BOTH paths; the difference was `p->var.v`
(DT_S on ir-run vs DT_N on sm-run).

The old XNME/XFNME construction in stmt_exec.c only read `.s` when
`v==DT_S`, dropping the varname whenever `v==DT_N`. The commit then
took the `*var_ptr = val` path, writing into a raw cell and bypassing
NV_SET_fn's I/O hook -- OUTPUT writes vanished.

Fix mirrors bb_build.c bb_nme_emit_binary / bb_fnme_emit_binary
NAMEVAL-aware logic: DT_N with slen==0 carries name string in `.s`,
DT_N with slen==1 carries raw pointer in `.ptr`. Both cases preserved.

### Next: expr_eval (Bug #1 family, distinct root cause)
