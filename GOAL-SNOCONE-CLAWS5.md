# GOAL-SNOCONE-CLAWS5.md — claws5.sc under scrip

**Repo:** one4all + corpus
**Done when:** `scrip --ir-run claws5.sc < claws5_4.input` produces output
matching `claws5.ref` exactly (diff zero), all three modes
(--ir-run, --sm-run, --jit-run).

**Oracle:** `csnobol4 -bf claws5.sno < claws5_4.input` matches `claws5.ref`.
claws5.sno is the reference implementation. claws5.sc must match it.

**Parallel session note:** This goal runs concurrently with
GOAL-SNOCONE-TREEBANK-LIST. Both probe the same SC-26 pattern engine bug
from different angles. Fix in one4all/runtime — share via main, no branches.

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
bash /home/claude/one4all/scripts/test_smoke_snocone.sh   # PASS=5
```

---

## Key files

```
corpus/programs/snobol4/demo/claws5.sc        — Snocone program under test
corpus/programs/snobol4/demo/claws5.sno       — SNOBOL4 oracle reference
corpus/programs/snobol4/demo/claws5_4.input   — 4-sentence test input
corpus/programs/snobol4/demo/claws5.ref       — expected output (95 lines, pprint format)
corpus/programs/snobol4/demo/CLAWS5inTASA.dat — full corpus (989 lines, needs -P 34000)
```

---

## Architecture reminder

```
claws5.sc → snocone_compile() → Program* [LANG_SNO]
    --ir-run  → execute_program() → interp_eval()
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()

Key pattern construct:
    ARBNO( (header . *new_sent()) | (token . *add_tok()) )
    where header/token use (PAT . var) . *fn(var) capture+call chains
```

---

## Known blocker going in

SC-26: `(PAT . var) . *fn(var)` — the captured value of `var` is not correctly
passed as the argument to `fn` at match time. This is a pattern engine bug in
bb_boxes.c or snobol4_pattern.c. The `.sno` version works under csnobol4
because csnobol4 evaluates the capture before the indirect call. scrip does not.

---

## Step ladder

- [ ] **CL-1** — Diagnose SC-26 for claws5.sc.
  Run `scrip --ir-run claws5.sc < claws5_4.input` and capture error.
  Identify which `(PAT . var) . *fn(var)` call fails first.
  Write a minimal isolated test case in `test/snocone/test_capture_call.sc`.
  Gate: understand exactly where arg value goes wrong in bb_boxes.c / snobol4_pattern.c.

- [ ] **CL-2** — Fix SC-26 in the pattern engine (coordinate with GOAL-SNOCONE-TREEBANK-LIST).
  The fix lives in one4all runtime. Once found, one fix serves both goals.
  Gate: `test/snocone/test_capture_call.sc` PASS all 3 modes.
  Gate: `test_smoke_snocone.sh` PASS=5.

- [ ] **CL-3** — claws5.sc PASS --ir-run.
  `scrip --ir-run claws5.sc < claws5_4.input | diff - claws5.ref` → empty.
  Gate: zero diff.

- [ ] **CL-4** — claws5.sc PASS --sm-run and --jit-run.
  Gate: zero diff both modes.

- [ ] **CL-5** — Full corpus smoke: claws5.sc on CLAWS5inTASA.dat.
  `scrip --ir-run -P 34000 claws5.sc < CLAWS5inTASA.dat` — no crash, sane output.
  (No ref for full corpus — just verify no errors and output count is reasonable.)

---

## Current state (initial, corpus HEAD 71bedd0, one4all HEAD 1194e57d)

Goal created. claws5.sc has correct pprint pp_mem algorithm (matches claws5.sno).
Blocker: SC-26 pattern engine bug — (PAT . var) . *fn(var) arg not passed correctly.
First step: CL-1 — diagnose and isolate.
