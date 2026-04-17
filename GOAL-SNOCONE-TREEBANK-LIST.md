# GOAL-SNOCONE-TREEBANK-LIST.md — treebank-list.sc under scrip

**Repo:** one4all + corpus
**Done when:** `scrip --ir-run treebank-list.sc < treebank4.input` produces
output matching `treebank-list.ref` exactly (diff zero), all three modes
(--ir-run, --sm-run, --jit-run).

**Oracle:** `csnobol4 -bf treebank-list.sno < treebank4.input` matches
`treebank-list.ref`. treebank-list.sno is the reference implementation.
treebank-list.sc must match it.

**Parallel session note:** This goal runs concurrently with
GOAL-SNOCONE-CLAWS5. Both probe the same SC-26 pattern engine bug from
different angles. Fix in one4all/runtime — share via main, no branches.

**treebank-array.sc note:** treebank-array.sc is a third goal (not yet
created). Once this goal and GOAL-SNOCONE-CLAWS5 are both DONE, the
treebank-array.sc goal will be started. It shares the same fix.

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
corpus/programs/snobol4/demo/treebank-list.sc    — Snocone program under test
corpus/programs/snobol4/demo/treebank-list.sno   — SNOBOL4 oracle reference
corpus/programs/snobol4/demo/treebank4.input     — 4 S-expression test input
corpus/programs/snobol4/demo/treebank-list.ref   — expected output (24 lines, pprint format)
corpus/programs/snobol4/demo/VBGinTASA.dat       — full treebank corpus (1977 lines)
```

---

## Architecture reminder

```
treebank-list.sc → snocone_compile() → Program* [LANG_SNO]
    --ir-run  → execute_program() → interp_eval()
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()

Key pattern construct (double-function trick in Snocone):
    (word . tag) . *push_list(tag)    — capture tag, push frame at match time
    (epsilon . *pop_list())           — zero-width hook, pop frame at match time
    (epsilon . *init_list('bank'))    — literal arg via nreturn procedure

LISP-style cons-list: children prepended, list_reverse corrects at pop time.
```

---

## Known blocker going in

SC-26: `(PAT . var) . *fn(var)` — the captured value of `var` is not correctly
passed as the argument to `fn` at match time. This is a pattern engine bug in
bb_boxes.c or snobol4_pattern.c. The `.sno` version works under csnobol4
because csnobol4 evaluates the capture before the indirect call. scrip does not.

---

## Step ladder

- [ ] **TB-1** — Diagnose SC-26 for treebank-list.sc.
  Run `scrip --ir-run treebank-list.sc < treebank4.input` and capture error.
  Identify which `(PAT . var) . *fn(var)` call fails first.
  Write a minimal isolated test case in `test/snocone/test_capture_call.sc`
  (coordinate with GOAL-SNOCONE-CLAWS5 — share the same test file if possible).
  Gate: understand exactly where arg value goes wrong in bb_boxes.c / snobol4_pattern.c.

- [ ] **TB-2** — Fix SC-26 in the pattern engine (coordinate with GOAL-SNOCONE-CLAWS5).
  The fix lives in one4all runtime. Once found, one fix serves both goals.
  Gate: `test/snocone/test_capture_call.sc` PASS all 3 modes.
  Gate: `test_smoke_snocone.sh` PASS=5.

- [ ] **TB-3** — treebank-list.sc PASS --ir-run.
  `scrip --ir-run treebank-list.sc < treebank4.input | diff - treebank-list.ref` → empty.
  Gate: zero diff.

- [ ] **TB-4** — treebank-list.sc PASS --sm-run and --jit-run.
  Gate: zero diff both modes.

- [ ] **TB-5** — Full corpus smoke: treebank-list.sc on VBGinTASA.dat.
  `scrip --ir-run treebank-list.sc < VBGinTASA.dat` — no crash, sane output.
  (No ref for full corpus — just verify no errors.)

---

## Current state (initial, corpus HEAD 71bedd0, one4all HEAD 1194e57d)

Goal created. treebank-list.sc has correct pprint-exact pp_node algorithm
(suffix-threading, no branches, matches treebank-list.sno exactly).
Blocker: SC-26 pattern engine bug — (PAT . var) . *fn(var) arg not passed correctly.
First step: TB-1 — diagnose and isolate.
