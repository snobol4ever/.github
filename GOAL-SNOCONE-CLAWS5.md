# GOAL-SNOCONE-CLAWS5.md — claws5.sc under scrip

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
**Done when:** `scrip --run claws5.sc < claws5.input` produces output
matching `claws5.ref` exactly (diff zero), all three modes
(--run, --run, --run).

**Oracle:** `csnobol4 -bf claws5.sno < claws5.input` matches `claws5.ref`.
claws5.sno is the reference implementation. claws5.sc must match it.

**Parallel session note:** This goal runs concurrently with
GOAL-SNOCONE-TREEBANK-LIST. Both probe the same SC-26 pattern engine bug
from different angles. Fix in SCRIP/runtime — share via main, no branches.

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
corpus/programs/snobol4/demo/claws5.sc        — Snocone program under test
corpus/programs/snobol4/demo/claws5.sno       — SNOBOL4 oracle reference
corpus/programs/snobol4/demo/claws5.input   — 4-sentence test input
corpus/programs/snobol4/demo/claws5.ref       — expected output (95 lines, pprint format)
corpus/programs/snobol4/demo/CLAWS5inTASA.dat — full corpus (989 lines, needs -P 34000)
```

---

## Architecture reminder

```
claws5.sc → snocone_compile() → CODE_t* [LANG_SNO]
    --run  → execute_program() → interp_eval()
    --run  → sm_lower() → SM_Program → sm_interp_run()
    --run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()

Key pattern construct:
    ARBNO( (header . *new_sent()) | (token . *add_tok()) )
    where header/token use (PAT . var) . *fn(var) capture+call chains
```

---

## Known blocker going in

SC-26: `(PAT . var) . *fn(var)` — the chained outer indirect call `*fn`
is NOT invoked at match time under scrip. Both SPITBOL and CSNOBOL4 do
invoke it. Earlier description ("arg not passed correctly") was wrong;
the call itself never fires. Bug lives in the pattern engine —
likely bb_boxes.c (XCALLCAP lowering) or snobol4_pattern.c (match-time
side-effect firing).

---

## Step ladder

- [ ] **CL-1** — Diagnose SC-26 for claws5.sc.
  Run `scrip --run claws5.sc < claws5.input` and capture error.
  Identify which `(PAT . var) . *fn(var)` call fails first.
  Write a minimal isolated test case in `test/snocone/test_capture_call.sc`.
  Gate: understand exactly where arg value goes wrong in bb_boxes.c / snobol4_pattern.c.

- [ ] **CL-2** — Fix SC-26 in the pattern engine (coordinate with GOAL-SNOCONE-TREEBANK-LIST).
  The fix lives in SCRIP runtime. Once found, one fix serves both goals.
  Gate: `test/snocone/test_capture_call.sc` PASS all 3 modes.
  Gate: `test_smoke_snocone.sh` PASS=5.

- [ ] **CL-3** — claws5.sc PASS --run.
  `scrip --run claws5.sc < claws5.input | diff - claws5.ref` → empty.
  Gate: zero diff.

- [ ] **CL-4** — claws5.sc PASS --run and --run.
  Gate: zero diff both modes.

- [ ] **CL-5** — Full corpus smoke: claws5.sc on CLAWS5inTASA.dat.
  `scrip --run -P 34000 claws5.sc < CLAWS5inTASA.dat` — no crash, sane output.
  (No ref for full corpus — just verify no errors and output count is reasonable.)

---

## Current state (2026-04-17 post Bug B fix)

**Design decision (Lon):** Keep three-tier comparison operators
(`== != < > <= >=` → numeric; `:==: :!=: :<: :>: :<=: :>=:` → lexical;
`:: :!:` → identity). Collapse was considered and rejected — users
practice discipline by selecting the right operator. So `==` stays
lowered to `EQ`. Bug B is therefore a runtime bug in `_EQ_`, not a
lowering bug.

**Bug B FIXED (runtime, shared by SNOBOL4 + Snocone).**
  * Root cause: `to_real()` in snobol4.c:1693 used `strtod(s, NULL)`,
    which swallows parse failures — any non-numeric string coerced
    to 0.0. `_EQ_` fell through `IS_INT` fast-path into
    `to_real(a)==to_real(b)`, so `EQ('foo','foo')` returned TRUE.
  * Fix: added `is_numeric_like(DESCR_t)` helper and `NUM_GUARD(fn)`
    macro at snobol4.c:157–210. Applied to all six numeric compare
    functions `_EQ_ _NE_ _LT_ _GT_ _LE_ _GE_`. Guard raises soft
    error 1 ("Illegal data type") with a SPITBOL-style message like
    "EQ first argument is not numeric" when args are non-numeric.
    `is_numeric_like` accepts DT_I, DT_R, DT_SNUL, whitespace-only
    strings (→ 0), and strings that `strtod` consumes fully up to
    trailing whitespace. DT_K resolved via NV_GET_fn and rechecked.
  * Verified: `EQ('42', 42)` succeeds, `EQ(' 42 ', 42)` succeeds,
    `EQ('foo','foo')` raises error 1 (no more silent TRUE),
    `EQ(42, 43)` fails normally.
  * Gates after patch:
      - test_smoke_snocone.sh         PASS=5   FAIL=0 (unchanged)
      - test_smoke_snobol4.sh         PASS=7   FAIL=0 (unchanged)
      - test_smoke_unified_broker.sh  PASS=49  FAIL=0 (unchanged)
      - test_interp_broad_corpus_and_beauty.sh PASS=172 FAIL=56
        (same as pre-patch — zero regressions from this fix)
      - demo_claws5: claws5.sno --run still byte-matches claws5.ref
        (diff=0) on full 989-line CLAWS5inTASA.dat — C5-4 preserved.

**Observation during probe (not part of this fix).** When `_EQ_`
raises soft error 1 inside a Snocone `if (EQ(s,t)) {A} else {B}`
block, neither A nor B runs — AND statements after the if do not run
either. The driver's `execute_program` setjmp loop in interp.c:4024
should take `:F` and continue, but in Snocone `--run` the longjmp
appears to abandon the tail of the program. Worth investigating when
attacking Bug A — means users currently must call IDENT() explicitly
for string equality inside an if, not rely on `==` to gracefully fail.

**Pre-existing state-of-world discrepancy (not caused by this fix):**
Goal file previously asserted broad corpus 219/228 at HEAD 6c63908a
(post C5-4). Today's HEAD 6e98862f (TL-2 landing) gives 172/228
pre-patch. Something between those two commits regressed ~47 tests
in the broad suite. Out of scope for this session; flagging for
awareness. The smoke/broker/claws5 gates are all still green.

**Bug A — SC-26 still UNFIXED.** The prior snapshot read
`test_capture_call.sc` test 3 as PASS. That was spurious (tied to
Bug B). The real behavior of `(PAT . var) . *fn(var)`:
  * Minimal repro `/tmp/body_ran.sc`: procedure body writes a constant
    global `body_ran = 'YES'`, ignoring its argument. After
    `'foobar' ? ((LEN(3) . w) . *show(w))`: top-level `body_ran` is
    still `'NO'` and `w` is still `''`. The procedure body never ran;
    even the inner capture didn't commit the value of `w` either.
  * Plain `(LEN(3) . w)` without the trailing `. *fn(...)` — writes
    `w = 'foo'` correctly. So `.` capture works; the chained callcap
    box breaks both the `*fn` call and its inner capture commit.
  * Commit f9995d0 (SN-6 Bug #1c, NAM_commit callcap writes matched
    text) did NOT fix SC-26 for Snocone. Scope of that fix was the
    immediate `$` path in SNOBOL4 only. SC-26 remains open.
  * Sister goal GOAL-SNOCONE-TREEBANK-LIST has diagnosed this as
    three sub-bugs; Bugs 1 and 2 fixed, Bug 3 (bb_callcap spec_t→
    DESCR_t return type UB) pending TB-2. Fixing Bug 3 should
    unblock both CLAWS5 and TREEBANK-LIST.

**Bug C (Lon-confirmed non-bug):** initial speculation about local
procedure scope was wrong. All Snocone vars are global, SNOBOL4
style. Retracted.

---

## Order of attack for CL-2 (revised)

1. ~~Fix Bug B (`==` lowering) FIRST.~~ DONE — Bug B fixed at runtime
   level, not lowering level. `==` still lowers to `EQ`; `_EQ_` now
   rejects non-numeric args per SPITBOL manual p.221.
2. Re-run `test_capture_call.sc` with real equality. If SC-26 still
   reproduces (likely), proceed to step 3.
3. Fix Bug A (SC-26 — callcap not firing in chained form). Trace:
   `snocone_lower.c` → IR E_CALLCAP (if it exists) → `bb_build.c`
   BB_CALLCAP → `bb_boxes.c` bb_callcap. Coordinate with TB-2 in
   GOAL-SNOCONE-TREEBANK-LIST — one fix serves both goals (change
   `bb_callcap` return type from `spec_t` to `DESCR_t`).
4. Rewrite claws5.sc pp_mem to match .sno pp_mem output format
   (unchanged from prior plan).
