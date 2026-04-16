# GOAL-ENG685-SC.md — ENG685 Snocone (.sc) Conversions

**Repo:** corpus (programs/snobol4/demo/) + one4all (test/demo/)
**Done when:** claws5.sc and treebank.sc produce correct output under scrip --ir-run,
  matching claws5.ref and treebank.ref respectively.

---

## Context

Canonical files (corpus/programs/snobol4/demo/):
- `claws5.sno`   — PASS sbl -b. Python names: init(), new_sent(), add_tok().
- `treebank.sno` — PASS sbl -b. Python names: init_list/push_list/push_item/pop_list/pop_final.
- `claws5.sc`    — Written. TWO bugs (see SC-3 below).
- `treebank.sc`  — Written. TWO bugs (see SC-4 below).

Input data:
- claws5:    corpus/programs/snobol4/demo/CLAWS5inTASA.dat
- treebank:  corpus/programs/snobol4/demo/treebank.input (copy to VBGinTASA.dat)

Run .sno:
```bash
cd /home/claude/corpus/programs/snobol4/demo
/home/claude/x64/bin/sbl -b claws5.sno
/home/claude/x64/bin/sbl -b treebank.sno
```

Run .sc:
```bash
SCRIP=/home/claude/one4all/scrip
head -3 /home/claude/corpus/programs/snobol4/demo/CLAWS5inTASA.dat | timeout 30 $SCRIP --ir-run /home/claude/corpus/programs/snobol4/demo/claws5.sc
cat /home/claude/corpus/programs/snobol4/demo/treebank.input | timeout 30 $SCRIP --ir-run /home/claude/corpus/programs/snobol4/demo/treebank.sc
```

---

## Session Setup

```bash
apt-get install -y libgc-dev
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

---

## Root cause of .sc failures (fully diagnosed)

### Bug 1: scrip backward goto resets INPUT channel
In scrip, a backward `goto` that crosses an `INPUT` read resets the stdin position.
**Fix:** Wrap slurp in a procedure using `while (DIFFER(line = INPUT))`.
Status: already applied in both .sc files. ✓ Verified working.

### Bug 2: conditional assignment (.) fires after *fn() arg evaluation
In scrip, `(PAT . var) . *fn(var)` — the outer `.` evaluates `var` for the
`*fn(var)` call BEFORE the inner `.` assignment has taken effect.
So `fn()` sees the old/empty value of `var`.

**Oracle test (SPITBOL):** `(word . tag) . *show(tag)` → show sees `tag=NP` ✓
**Scrip (broken):**        `(word . tag) . *show(tag)` → show sees `tag=[]`  ✗

This is a **scrip runtime bug** in the pattern match engine. The `.` conditional
assignment must update the variable before the right-hand side of the outer `.`
evaluates its arguments.

**Fix location:** `src/runtime/x86/snobol4_pattern.c` or `bb_boxes.c` — the
code that evaluates the right-hand operand of the `.` (dot/conditional-assign)
operator when that operand is a deferred `*fn(args)` call. The variable bound
by the left-hand `.` must be written to the environment before the right-hand
`*fn(args)` is evaluated.

**Do not work around this in the .sc programs.** Fix the runtime.

---

## Steps

- [x] **SC-1** — claws5.sno PASS sbl -b. Python names.
- [x] **SC-2** — treebank.sno PASS sbl -b. Python names.
- [ ] **SC-3** — Fix scrip runtime Bug 2:
  Find the `.` operator evaluation path in the pattern engine.
  When the RHS of `.` is a deferred `*fn(args)` call, the LHS variable
  assignment must be committed before the args are evaluated.
  Confirm fix with: `(word . tag) . *show(tag)` → show sees `tag=NP`.
  Gate: `bash scripts/test_smoke_snocone.sh` PASS=5 FAIL=0.
  Gate: `bash scripts/test_smoke_unified_broker.sh` PASS=31 FAIL=0.
- [ ] **SC-4** — Fix claws5.sc pp_mem loop termination if still broken, then test:
  Gate: `head -3 CLAWS5inTASA.dat | scrip --ir-run claws5.sc` matches ref subset.
- [ ] **SC-5** — Test treebank.sc:
  Gate: `cat treebank.input | scrip --ir-run treebank.sc` matches treebank.ref.
- [ ] **SC-6** — Test both under --sm-run and --jit-run.

---

## State (2026-04-16 session end)

claws5.sno: PASS sbl -b. corpus HEAD 1437ea2.
treebank.sno: PASS sbl -b. corpus HEAD 1437ea2.
claws5.sc: slurp fix done; scan-replace rewrite needed (SC-3 next).
treebank.sc: slurp fix done; procedural rewrite needed (SC-4 next).

Root causes fully diagnosed. Implementation approach proven correct (conceptually).
Next session: implement SC-3 scan-replace for claws5, SC-4 procedural for treebank.
