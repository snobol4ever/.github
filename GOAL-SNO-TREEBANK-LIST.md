# GOAL-SNO-TREEBANK-LIST.md — demo_treebank-list PASS

**Repo:** one4all
**Parallel:** This goal runs in its own session simultaneously with GOAL-SNO-TREEBANK-ARRAY
and GOAL-SNO-CLAWS5. All three sessions share main — pull --rebase before every push.
Fixes to shared files (interp.c, bb_boxes.c, stmt_exec.c) benefit all sessions immediately.

**Done when:** `demo_treebank-list` passes in `test_interp_broad_corpus_and_beauty.sh`;
output matches `corpus/programs/snobol4/demo/treebank-list.ref` under `--ir-run`.

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

## Program

```
corpus/programs/snobol4/demo/treebank-list.sno
Input:  corpus/programs/snobol4/demo/VBGinTASA.dat
Ref:    corpus/programs/snobol4/demo/treebank-list.ref
Oracle: CSNOBOL4 -bf -P 500k  (double-function trick; SPITBOL -f is broken)
```

Run to test:
```bash
DEMO=/home/claude/corpus/programs/snobol4/demo
timeout 30 /home/claude/one4all/scrip --ir-run $DEMO/treebank-list.sno \
    < $DEMO/VBGinTASA.dat 2>/dev/null | diff - $DEMO/treebank-list.ref
```

---

## Known state (2026-04-17)

**BAL is implemented** — `bb_bal` in `bb_boxes.c`, `XBAL` wired in `stmt_exec.c`.
This fix is already on main; pull it at session start.

**Blocker 1: case-sensitive label dispatch (same as GOAL-SNO-TREEBANK-ARRAY).**
treebank-list.sno uses `push_list`/`Push_list`, `init_list`/`Init_list`.
`label_lookup()` in `src/driver/interp.c` line 148 uses `strcasecmp`.
Fix: `strcmp`. GOAL-SNO-TREEBANK-ARRAY may land this fix first — pull before
starting work and check if it is already done.

**Blocker 2: CSNOBOL4 reports Error 16 (overflow) with default stack.**
treebank-list.sno builds deeply recursive list structures. CSNOBOL4 needs
`-P 500k` to run it without overflow. scrip has no pattern-stack size limit of
this kind, so this should not be a blocker for scrip — but watch for deep
recursion in the interpreter (call stack depth in `call_user_function`).

Current symptom (scrip): `''` — empty output. Program runs but produces no output,
likely because push/pop mis-dispatch (same root as treebank-array).

---

## Steps

- [ ] **TL-1** — Confirm `label_lookup` fix is on main (may be landed by
  GOAL-SNO-TREEBANK-ARRAY session). If not, apply it: change `strcasecmp` to
  `strcmp` in `label_lookup` in `src/driver/interp.c`. Rebuild. Run smoke + broker.

- [ ] **TL-2** — Run treebank-list under scrip --ir-run. Diff against ref.
  Fix any divergences. Watch for interpreter stack overflow on deep list recursion;
  if hit, raise `DVAR_MAX_DEPTH` in `interp.c` or investigate the recursion path.
  Gate: diff clean; smoke PASS=7; broker PASS=49;
  `test_interp_broad_corpus_and_beauty` PASS improves.

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | `label_lookup`, `DVAR_MAX_DEPTH` recursion cap |
| `src/runtime/x86/bb_boxes.c` | `bb_bal` (already implemented) |
| `corpus/programs/snobol4/demo/treebank-list.sno` | Program under test |
| `corpus/programs/snobol4/demo/treebank-list.ref` | Expected output |

---

## Invariants

- CSNOBOL4 `-bf -P 500k` is oracle (SPITBOL `-f` broken).
- Never patch corpus source. Fix the runtime.
- Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Pull --rebase before every push (parallel sessions active).

---

## Current state (2026-04-17, one4all HEAD — post-BAL commit)

TL-1 next. BAL on main. label_lookup fix pending (may arrive from treebank-array session).

---

## Session 2026-04-17 progress

**TL-1 DONE.**
- `label_lookup` in `src/driver/interp.c:148`: `strcasecmp` → `strcmp`.
- Smoke PASS=7, Broker PASS=49. Committed on main.

**TL-2 IN PROGRESS — blocker found, partial fix applied.**

Root cause of empty output: `*fn(args)` called via `pat . *fn(args)` in pattern context
was prepending the matched substring as `args[0]`, shifting all explicit args by 1.
So `*set_it('bank')` called `set_it("", "bank")` → `var=""` instead of `var="bank"`.

Fixed in two callcap dispatch sites (NAM_commit in snobol4_nmd.c,
flush_pending_callcaps in stmt_exec.c). These sites are now correct.

**Remaining blocker:** `epsilon . *fn(vs)` inside a SNOBOL4 function body called
from pattern does NOT go through NAM_commit or flush_pending_callcaps.
It fires through a third path — likely `bb_callcap` in `bb_boxes.c` or
a separate cc_event path in stmt_exec.c (around the XCALLCAP/CC_γ_core area).
Debug confirmed: NAM_commit never fires for `epsilon . *set_it(vs)`.

**Next session TL-2:**
1. Add debug stderr print inside CC_γ_core (stmt_exec.c ~line 593) to confirm
   that path fires and identify which sub-branch handles `epsilon . *fn(vs)`.
2. Apply same no-prepend fix to that path.
3. Re-run treebank-list diff.
