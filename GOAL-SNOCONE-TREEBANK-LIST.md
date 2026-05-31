# GOAL-SNOCONE-TREEBANK-LIST.md — treebank-list.sc under scrip

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

**Repo:** SCRIP + corpus
**Done when:** `scrip --interp treebank-list.sc < treebank4.input` produces
output matching `treebank-list.ref` exactly (diff zero), all three modes
(--interp, --interp, --run).

**Oracle:** `csnobol4 -bf treebank-list.sno < treebank4.input` matches
`treebank-list.ref`. treebank-list.sno is the reference implementation.
treebank-list.sc must match it.

**Parallel session note:** This goal runs concurrently with
GOAL-SNOCONE-CLAWS5. Both probe the same SC-26 pattern engine bug from
different angles. Fix in SCRIP/runtime — share via main, no branches.

**treebank-array.sc note:** treebank-array.sc is a third goal (not yet
created). Once this goal and GOAL-SNOCONE-CLAWS5 are both DONE, the
treebank-array.sc goal will be started. It shares the same fix.

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
bash /home/claude/SCRIP/scripts/test_smoke_snocone.sh   # PASS=5
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
treebank-list.sc → snocone_compile() → CODE_t* [LANG_SNO]
    --interp  → execute_program() → interp_eval()
    --interp  → sm_lower() → SM_Program → sm_interp_run()
    --run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()

Key pattern construct (double-function trick in Snocone):
    (word . tag) . *push_list(tag)    — capture tag, push frame at match time
    (epsilon . *pop_list())           — zero-width hook, pop frame at match time
    (epsilon . *init_list('bank'))    — literal arg via nreturn procedure

LISP-style cons-list: children prepended, list_reverse corrects at pop time.
```

---

## Correct model for immediate vs conditional assignment

Per the SPITBOL manual and SIL spec:

**Immediate assignment (`$`)** — written on every γ during match, even during
backtracking. The variable is set right away as the pattern advances.

**Conditional assignment (`.`)** — queued into the SIL naming list (NMD).
At Phase-5 (overall match success) ALL queued entries flush left-to-right in
the order they were pushed during the match. Only then are variables assigned
and nreturn functions called.

The naming list is a list of **lvalue expressions**:
- Plain variable name — `NV_SET_fn` at flush time.
- Deferred function `*fn()` — call `fn()` at flush time to get a NAME
  (via NRETURN), then assign the matched substring into that NAME.
  Side effects of `fn()` (e.g. `stk_push_frame(tag)`) fire at flush time.
- Plain function call `fn()` (no `*`) — evaluated at pattern BUILD time
  (Phase 2), never reaches the naming list.

**Key consequence for treebank-list.sc:**
`(word . tag) && (epsilon . *push_list())` queues two entries:
1. CAPTURE: assign matched word to `tag`
2. CALLCAP: call `push_list()`, assign epsilon ("") to the returned NAME

At flush time, entry 1 runs first (tag = "NP"), then entry 2 runs
(push_list() reads `tag` = "NP" correctly). Left-to-right order is essential.

---

## SC-26 root cause (fully diagnosed)

Three bugs, all in the runtime/frontend:

**Bug 1 — snobol4_nmd.c:** The naming list stored CAPTURE entries only.
CALLCAP events were stored in a separate `g_cc_events` array in stmt_exec.c
and flushed AFTER all captures. This broke left-to-right ordering: every
`push_list()` call saw the last value of `tag`, not the value captured
immediately before it.
FIX: Unified the two lists. `snobol4_nmd.c` now holds both CAPTURE
(NAM_KIND_CAPTURE) and CALLCAP (NAM_KIND_CALLCAP) entries in a single
oldest-to-newest linked list. `NAM_commit` walks it left-to-right,
dispatching each entry in order. `NAM_push_callcap()` added to public API.
`dedup_callcaps()` and `flush_pending_callcaps()` removed from Phase-5.

**Bug 2 — interp.c `E_CAPT_COND_ASGN`:** Snocone's `*fn()` lowers as
`E_INDIRECT(E_FNC(...))` not `E_DEFER(E_FNC(...))`. The existing check only
recognised `E_DEFER` as a deferred callcap target. `E_INDIRECT(E_FNC)`
fell through to the `$'name'` path which called `interp_eval(ichild)`,
executing `fn()` at pattern BUILD TIME (Phase 2) — wrong.
FIX: Added check for `E_INDIRECT(E_FNC)` before the existing `E_INDIRECT`
block; routes it to `pat_assign_callcap()` → `XCALLCAP` node, same as
`E_DEFER(E_FNC)`.

**Bug 3 — stmt_exec.c `bb_callcap`:** Declared `static spec_t bb_callcap(...)`
but cast to `bb_box_fn` which expects `DESCR_t` return. This is UB — the
sequence combinator misreads the return value and treats a successful match
as failure.
FIX (PENDING): Change `bb_callcap` return type to `DESCR_t`, wrapping
internal `spec_t` values with `descr_from_spec()` at each return point.

---

## Step ladder

- [x] **TB-1** — Diagnose SC-26 for treebank-list.sc.
  DONE. Three bugs identified and located (see above). treebank-list.sc
  rewritten using claws5-style capture-to-global idiom (no double-function
  trick needed). treebank4.input renamed to treebank.input.
  Bugs 1 and 2 fixed in snobol4_nmd.c and interp.c. Bug 3 identified
  (bb_callcap return type mismatch) — fix pending TB-2.

- [ ] **TB-2** — Fix Bug 3 (bb_callcap return type) and verify end-to-end.
  Change `bb_callcap` in stmt_exec.c from `spec_t` to `DESCR_t` return.
  Remove temporary fprintf traces added during diagnosis (stmt_exec.c lines
  with "bb_callcap CC_α" and snobol4_nmd.c NAM_push_callcap trace).
  Gate: `(word . tag) && (epsilon . *push_list())` probe PASS.
  Gate: `scrip --interp treebank-list.sc < treebank.input | diff - treebank-list.ref` → empty.
  Gate: `test_smoke_snocone.sh` PASS=5.
  Coordinate with GOAL-SNOCONE-CLAWS5 — same fix applies there.

- [ ] **TB-3** — treebank-list.sc PASS --interp and --run.
  Gate: zero diff both modes.

- [ ] **TB-4** — Full corpus smoke: treebank-list.sc on VBGinTASA.dat.
  `scrip --interp treebank-list.sc < VBGinTASA.dat` — no crash, sane output.
  (No ref for full corpus — just verify no errors.)

---

## Current state

TB-1 DONE. corpus HEAD pending commit (treebank-list.sc rewritten, treebank4.input→treebank.input).
SCRIP: snobol4_nmd.c (unified NAM list, Bug 1), interp.c (E_INDIRECT(E_FNC) → XCALLCAP, Bug 2)
committed. Bug 3 (bb_callcap spec_t→DESCR_t return type mismatch) identified, fix pending.
Temporary diagnostic fprintfs in stmt_exec.c and snobol4_nmd.c must be removed before TB-2 gate.
smoke PASS=5. Next: TB-2.
