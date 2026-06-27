# GOAL-SNO-TREEBANK-ARRAY.md — demo_treebank-array PASS

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Parallel:** This goal runs in its own session simultaneously with GOAL-SNO-TREEBANK-LIST
and GOAL-SNO-CLAWS5. All three sessions share main — pull --rebase before every push.
Fixes to shared files (interp.c, bb_boxes.c, stmt_exec.c) benefit all sessions immediately.

**Done when:** `demo_treebank-array` passes in `test_interp_broad_corpus_and_beauty.sh`;
output matches `corpus/programs/snobol4/demo/treebank-array.ref` under `--run`.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Program

```
corpus/programs/snobol4/demo/treebank-array.sno
Input:  corpus/programs/snobol4/demo/VBGinTASA.dat
Ref:    corpus/programs/snobol4/demo/treebank-array.ref
Oracle: CSNOBOL4 -bf -P 200k  (double-function trick; SPITBOL -f is broken)
```

Run to test:
```bash
DEMO=/home/claude/corpus/programs/snobol4/demo
timeout 30 /home/claude/SCRIP/scrip --run $DEMO/treebank-array.sno \
    < $DEMO/VBGinTASA.dat 2>/dev/null | diff - $DEMO/treebank-array.ref
```

---

## Known state (2026-04-17)

**BAL is implemented** — `bb_bal` in `bb_boxes.c`, `XBAL` wired in `stmt_exec.c`.
This fix is already on main; pull it at session start.

**Remaining blocker: double-function trick / case-sensitive label dispatch.**
treebank-array.sno uses `Push_list`/`push_list`, `Push_item`/`push_item`,
`Pop_list`/`pop_list` (uppercase = EVAL-wrapper, lowercase = body).
`label_lookup()` in `src/driver/interp.c` line 148 uses `strcasecmp` — so
`Push_list` resolves to `push_list`. Fix: change `label_lookup` to `strcmp`
(exact match). Special labels `RETURN`, `FRETURN`, `NRETURN`, `END` are caught
before `label_lookup` in the goto-dispatch path and are unaffected.

Also check `FUNC_ENTRY_fn` / `FNCEX_fn` registration — function names are stored
via `DEFINE_fn`; verify they are keyed case-sensitively.

Current symptom: `('ROOT')` with no children — push/pop fire but route to wrong
function, so children are never appended.

---

## Steps

- [x] **TA-1** — Fix `label_lookup` in `src/driver/interp.c`: change `strcasecmp`
  to `strcmp`. Already done on main at session start. Confirmed by inspection.

- [x] **TA-2** — Diff treebank-array output against ref. Fix any remaining
  divergences. DONE: diff=0; two fixes in SCRIP HEAD 25ab6fe7.

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | `label_lookup`, `call_user_function` |
| `src/runtime/x86/bb_boxes.c` | `bb_bal` (already implemented) |
| `src/runtime/x86/stmt_exec.c` | XBAL wiring (already done) |
| `corpus/programs/snobol4/demo/treebank-array.sno` | Program under test |
| `corpus/programs/snobol4/demo/treebank-array.ref` | Expected output |

---

## Invariants

- CSNOBOL4 `-bf -P 200k` is oracle (SPITBOL `-f` broken for case-sensitive labels).
- Never patch corpus source. Fix the runtime.
- Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Pull --rebase before every push (parallel sessions active).

---

## Current state (2026-04-17, SCRIP HEAD 25ab6fe7 — TA-2 DONE)

GOAL COMPLETE. treebank-array --run diff=0 vs treebank-array.ref.

Two fixes landed:
1. bb_usercall (stmt_exec.c): deferred *fn() via NAM_push_callcap (Bug #1d).
2. bb_bal (bb_boxes.c): removed premature break at depth==0 — BAL now scans all
   sibling balanced groups. This was the primary blocker for spat extraction.

smoke PASS=7, broker PASS=49, broad corpus PASS=172 (unchanged).
