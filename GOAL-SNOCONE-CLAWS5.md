# GOAL-SNOCONE-CLAWS5.md — claws5.sc under scrip

**Repo:** one4all + corpus
**Done when:** `scrip --ir-run claws5.sc < claws5.input` produces output
matching `claws5.ref` exactly (diff zero), all three modes
(--ir-run, --sm-run, --jit-run).

**Oracle:** `csnobol4 -bf claws5.sno < claws5.input` matches `claws5.ref`.
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
corpus/programs/snobol4/demo/claws5.input   — 4-sentence test input
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

SC-26: `(PAT . var) . *fn(var)` — the chained outer indirect call `*fn`
is NOT invoked at match time under scrip. Both SPITBOL and CSNOBOL4 do
invoke it. Earlier description ("arg not passed correctly") was wrong;
the call itself never fires. Bug lives in the pattern engine —
likely bb_boxes.c (XCALLCAP lowering) or snobol4_pattern.c (match-time
side-effect firing).

---

## Step ladder

- [ ] **CL-1** — Diagnose SC-26 for claws5.sc.
  Run `scrip --ir-run claws5.sc < claws5.input` and capture error.
  Identify which `(PAT . var) . *fn(var)` call fails first.
  Write a minimal isolated test case in `test/snocone/test_capture_call.sc`.
  Gate: understand exactly where arg value goes wrong in bb_boxes.c / snobol4_pattern.c.

- [ ] **CL-2** — Fix SC-26 in the pattern engine (coordinate with GOAL-SNOCONE-TREEBANK-LIST).
  The fix lives in one4all runtime. Once found, one fix serves both goals.
  Gate: `test/snocone/test_capture_call.sc` PASS all 3 modes.
  Gate: `test_smoke_snocone.sh` PASS=5.

- [ ] **CL-3** — claws5.sc PASS --ir-run.
  `scrip --ir-run claws5.sc < claws5.input | diff - claws5.ref` → empty.
  Gate: zero diff.

- [ ] **CL-4** — claws5.sc PASS --sm-run and --jit-run.
  Gate: zero diff both modes.

- [ ] **CL-5** — Full corpus smoke: claws5.sc on CLAWS5inTASA.dat.
  `scrip --ir-run -P 34000 claws5.sc < CLAWS5inTASA.dat` — no crash, sane output.
  (No ref for full corpus — just verify no errors and output count is reasonable.)

---

## Current state (2026-04-17 post-probe — corpus 5d75439, one4all 6c63908)

**CL-1 diagnosis from prior session was based on a false positive.**

**Bug A — SC-26 is NOT fixed.** The prior snapshot read `test_capture_call.sc`
test 3 as PASS. That was spurious — see Bug B. The real behavior of
`(PAT . var) . *fn(var)`:
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

**Bug B — Snocone `==` on strings is broken in --ir-run.**
  * Minimal repro `/tmp/eq_sanity.sc`:
      `'' == 'foo'`    → TRUE  (wrong — should be FALSE)
      `'ZZZ' == 'foo'` → TRUE  (wrong — should be FALSE)
      `'foo' == 'foo'` → TRUE  (coincidentally right)
  * Root cause located: `snocone_lower.c:242` lowers `==` to
    `make_fnc2("EQ", l, r)` — the SNOBOL4 numeric-EQ function. Two
    non-numeric strings both coerce to 0, so `EQ(0,0)` is TRUE.
  * Correct lowering: `==` on strings must dispatch to IDENT (string
    equality). Choices: (a) always lower to a new `SEQ` runtime
    helper that dispatches on type, (b) lower to IDENT and let it
    coerce integers via SPITBOL semantics, (c) keep EQ but have
    the runtime fall back to IDENT on non-numeric args. (a) is the
    cleanest per SNOBOL4 type model.
  * Side note: direct call `r = EQ('ZZZ', 'foo')` silently
    terminates the Snocone program — EQ fails and failure propagates.
    Bug B needs fixing before test_capture_call.sc can diagnose
    anything reliably; every `==` check in the test was spurious.

**Bug C (Lon-confirmed non-bug):** I initially speculated Snocone had
local procedure scope. Wrong. All Snocone vars are global, SNOBOL4
style. Retracted. The appearance of "local scope" was Bug A masquerading
as a scope issue — since the procedure body never runs, no assignment
ever happens, and the outer variable naturally keeps its initial value.

---

## Order of attack for CL-2 (revised)

1. Fix Bug B (`==` lowering) FIRST. One-site change in
   `snocone_lower.c:240-262`. Without it, no test can be trusted.
2. Re-run `test_capture_call.sc` with real equality. If SC-26 still
   reproduces (likely), proceed to step 3.
3. Fix Bug A (SC-26 — callcap not firing in chained form). Trace:
   `snocone_lower.c` → IR E_CALLCAP (if it exists) → `bb_build.c`
   BB_CALLCAP → `bb_boxes.c` bb_callcap. Previous session's CL-1
   said "truncated last session at line 155" of bb_boxes.c —
   continue that read.
4. Rewrite claws5.sc pp_mem to match .sno pp_mem output format
   (unchanged from prior plan).
