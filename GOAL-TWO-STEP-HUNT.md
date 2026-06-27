# GOAL-TWO-STEP-HUNT — Systematic Bug Hunt via Monitor + Probe

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
**Done when:** All 4 failing beauty drivers pass + beauty self-host passes.

## The Two-Step Dance

**Step 1 — Monitor:** Diff SPITBOL vs scrip output on failing driver.
Find first diverging test. Identify which subsystem line causes it.

```bash
cd /home/claude/SCRIP
BEAUTY=/home/claude/corpus/programs/snobol4/beauty_suite
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_DRIVER_driver.sno 2>/dev/null \
    > /tmp/spitbol.out
SNO_LIB=$BEAUTY timeout 10 ./scrip --run $BEAUTY/beauty_DRIVER_driver.sno 2>/dev/null \
    > /tmp/scrip.out
diff /tmp/spitbol.out /tmp/scrip.out
```

**Step 2 — Inline Probe (Technique C):** Replace the diverging line
in-place with OUTPUT probes. Run under both. Compare.

```python
lines = Path(subsys_file).read_text().splitlines()
lines[target_line - 1] = probe_outputs  # exact line replacement
```

No stlimit tricks. No sentinel injection. The function runs naturally to
that line, probe fires in its place, exits. Context is exact.

**Sub-expression detail:** If the inline probe shows values match but
result diverges, use the SSA gauntlet on that line:

```bash
python3 test/beauty_subexpr_gen.py \
    --source SUBSYS.sno --driver DRIVER.sno \
    --line N --stlimit SL \
    --out corpus/.../subexpr/ --verbose
./scrip --run corpus/.../subexpr/TEST.sno
# FAIL K → SNBtK is the broken node
```

## Bug Queue

| Driver | First diverging test | Subsystem:line | Bug | Status |
|--------|---------------------|----------------|-----|--------|
| omega | test 2: TZ xTrace=1 returns STRING | omega.sno:41 | `EVAL(string)` — g_eval_str_hook wired → _eval_str_impl_fn → parse_expr_pat_from_str. BLOCKED on GOAL-REMOVE-CMPILE S-1: parse_expr_pat_from_str returns null (wrong wrapper). Fix: pass src direct to bison, return s->pattern else s->subject. | ☐ |
| Gen | test ? | ? | ARBNO upstream null DT_E | ☐ |
| TDump | test ? | ? | DATA field ordering t/v | ☐ |
| XDump | test ? | ? | Array bounds format `1` vs `1:1` | ☐ |
| beauty self-host | ? | ? | Unknown — apply dance | ☐ |

## omega bug detail — next session

**omega.sno:41:** `TZ = EVAL(omega) :S(RETURN)F(error)`

omega contains (when xTrace=1):
```
@txOfs $ *T8Trace(1, '?' 'lbl', txOfs) pat $ tz @txOfs $ *T8Trace(1, 'lbl: ' tz, txOfs)
```

SPITBOL: `EVAL(omega)` → PATTERN.
scrip: `EVAL(omega)` → silent fail (no output, takes :F branch).

Probe showed omega value is IDENTICAL in both runtimes.
The divergence is in `EVAL(string)` itself.

**Root cause chain:**
1. `EVAL(omega)` → `interp_eval` E_FNC intercept → `EVAL_fn(STRVAL(omega))`
2. `EVAL_fn` → `CONVE_fn(omega)` → compiles to DT_E (EXPR_t tree)
3. `EXPVAL_fn(DT_E)` → `eval_node(tree)` → **FAILDESCR**
4. `eval_node` fails because omega string contains:
   - `*T8Trace(...)` — the `*` is E_DEFER (deferred call) in eval_code.c
   - `$ tz` — pattern cursor-assign operator
   - These operators are NOT handled in eval_code.c eval_node

**Fix options:**
A. Add E_DEFER and `$`-operator cases to `eval_code.c eval_node`
B. Route `EVAL(string)` through `interp_eval` instead of `eval_node`
   (interp_eval already handles all operators including E_DEFER, `$`, etc.)

Option B is simpler and more correct — `interp_eval` is the authoritative
evaluator for scrip. The fix:

```c
/* In EVAL_fn (snobol4_pattern.c), after CONVE_fn: */
/* Instead of EXPVAL_fn(compiled), call interp_eval on the frozen tree */
extern DESCR_t interp_eval_pat(EXPR_t *e);  /* in scrip.c */
if (IS_FAIL_fn(compiled)) return FAILDESCR;
/* Route through scrip.c interp_eval_pat which handles all operators */
return interp_eval_pat((EXPR_t *)compiled.ptr);
```

OR: add a global hook `g_eval_str_hook` that scrip.c sets to point to
`interp_eval_pat`, analogous to `g_eval_pat_hook` for DT_P input.

## Steps

- [ ] **S-1** — Fix omega: route EVAL(string) through interp_eval_pat.
  Gate: omega driver PASS=15, all tests pass.

- [ ] **S-2** — Apply dance to Gen driver: monitor → first diverging test
  → inline probe → identify exact sub-expression → fix.
  Gate: Gen driver passes ≥1 additional test.

- [ ] **S-3** — Apply dance to TDump driver. Same protocol.

- [ ] **S-4** — Apply dance to XDump driver. Same protocol.

- [ ] **S-5** — Apply dance to beauty self-host:
  ```bash
  SNO_LIB=$INC ./scrip --run beauty_driver.sno
  ```
  Monitor vs SPITBOL. Find first divergence. Fix.

- [ ] **S-6** — All 4 failing drivers pass. Beauty suite PASS=18/18.

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```
