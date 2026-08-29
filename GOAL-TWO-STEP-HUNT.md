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
║  ⚠ ir_exec.c/lower_icn.c (this banner's original template pointer) are GONE (confirmed 2026-08-29).║
║  Current authority: RULES.md "NO C BYRD-BOX FUNCTIONS" — zero DESCR_t foo(void*,int entry),    ║
║  only icn_bb_dcg exempt; Byrd boxes are x86(...) emitted by the templates in src/templates/bb/.║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** All 4 failing beauty drivers pass + beauty self-host passes.

## The Two-Step Dance

**Step 1 — Monitor:** Diff SPITBOL vs scrip output on failing driver.
Find first diverging test. Identify which subsystem line causes it.

```bash
# ⚠ paths corrected 2026-08-29 (D-17 PORTABLE-HOME + s269-272 corpus re-grid): run from the sibling
# root, never a hardcoded /home/claude/*; the beauty suite moved programs/snobol4/ -> tests/snobol4/;
# the SPITBOL oracle is a SHARED resource, never per-seat-cloned -- use -bf, not -b (RULES.md § Oracles).
cd SCRIP
BEAUTY=../corpus/tests/snobol4/beauty_suite
SNO_LIB=$BEAUTY /home/resources/x64/bin/sbl -bf $BEAUTY/beauty_DRIVER_driver.sno 2>/dev/null \
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
| omega | test 2: TZ xTrace=1 returns STRING | omega.sno:41 | `EVAL(string)` — g_eval_str_hook wired → _eval_str_impl_fn → parse_expr_pat_from_str. **RE-VERIFIED LIVE 2026-08-29 (seat10, `goal-files-major-consolidation` row): FIXED, confirmed by actual repro run, not a doc read.** `SNO_LIB=$BEAUTY ./scrip --run $BEAUTY/omega_driver.sno` (both `--run` and `--compile`) produces output byte-identical to the committed `omega_driver.ref` — 15/15 `PASS:` lines, matching GOAL-REMOVE-CMPILE.md's own S-7 claim exactly. (A live SPITBOL oracle cross-check was attempted but not completed — `-I`/`SNO_LIB` include-path invocation for this specific oracle binary was not resolved in the time available; the scrip-vs-committed-`.ref` match stands on its own as the evidence here, flagged rather than silently treated as an oracle-verified run.) | ☑ |
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

## Dead fix-site filenames (flagged 2026-08-29, NOT resolved — needs a live repro, not a guess)
`eval_code.c`/`snobol4_pattern.c`, named above as the fix sites for `EVAL_fn`/`CONVE_fn`/`EXPVAL_fn`/
`eval_node`, no longer exist anywhere in `src/` (confirmed by grep). The functions themselves are still
live, now spread across `runtime_eval.c`/`pattern_match.c`/`core.c`/`by_name_dispatch.c`/`driver_hooks.c`
(per the `goal-files-major-consolidation` task's own seat07 verdict). **Whether this specific bug is
already fixed under one of those files, or still open, is NOT determined by this note** — the proposed
fix's own hook names (`interp_eval_pat`/`g_eval_str_hook`/`g_eval_pat_hook`) already exist live in
current source, which is ambiguous on its face (already-landed-under-this-name vs. an unrelated hook).
Resolving that needs an actual `omega_driver.sno` repro run against oracle vs scrip — out of scope for
a path-citation pass, deliberately not guessed here.

## Steps

- [x] **S-1** — Fix omega: route EVAL(string) through interp_eval_pat.
  Gate: omega driver PASS=15, all tests pass. **CONFIRMED 2026-08-29 (seat10) — see Bug Queue table
  above.** Whatever landed this (not identified by filename/commit this session — the fix-site functions
  moved across the RUNTIME-REORG dissolution per the note below) already satisfies the gate.

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
# ⚠ paths corrected 2026-08-29 (D-17 PORTABLE-HOME) -- run from the sibling root, not /home/claude/*.
# build_spitbol_oracle.sh is unverified current -- the oracle is now a SHARED resource
# (/home/resources/x64/bin/sbl), never per-seat-built; confirm this script is still the right step
# before relying on it, not chased here (out of this pass's path-citation scope).
bash SCRIP/scripts/install_system_packages.sh
bash SCRIP/scripts/build_scrip.sh
bash SCRIP/scripts/build_spitbol_oracle.sh
```
