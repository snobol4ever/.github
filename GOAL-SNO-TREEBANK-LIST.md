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

- [x] **TL-1** — Confirm `label_lookup` fix is on main (may be landed by
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

## Current state (2026-04-17, one4all HEAD f3d64bdb — post case-sensitivity commit)

TL-1 DONE. TL-2 IN PROGRESS: case-sensitivity refactor extended across function
registry; remaining divergence is deferred-arg evaluation for `*fn(var)` callcaps.
Full treebank-list: 1 line of 24 expected (was: empty). Smoke PASS=7, broker PASS=49.

---

## Session 2026-04-17 progress (latest)

**TL-1 DONE (carried from prior session).** `label_lookup` at `src/driver/interp.c:148`
uses `strcmp`. Smoke PASS=7, broker PASS=49.

**TL-2 partial — case-sensitivity refactor landed, remaining bug isolated.**

### Case-sensitivity fix (committed f3d64bdb)

Prior session hypothesized six `FUNC_*_fn` accessors needed `strcasecmp`→`strcmp`.
Root cause was broader: **`DEFINE_fn` at `snobol4.c:2630` also used `strcasecmp`** for
its "same function?" check, so `DEFINE('Push_list(vs)')` arriving after
`DEFINE('push_list(v)')` overwrote the first FNCBLK's `spec/fn/nparams/params/nlocals/locals`
in place — but left `e->name` unchanged. Result: one hybrid entry with `name="push_list"`
but `params=["vs"]`. `FUNC_ENTRY_fn("Push_list")` then returned the stored `"push_list"`,
and the now-case-sensitive `label_lookup` jumped to the wrong body.

Fix flipped 11 `strcasecmp(e->name, ...)` sites → `strcmp` in `snobol4.c`:
`DEFINE_fn` (2630), `DEFINE_fn_entry` (2653), `fn_has_builtin` (2516), `APPLY_fn` (2714),
`_ARG_` (2744), `_LOCAL_` (2766), `_FIELD_` (2813), `register_fn_alias` (2672, 2695),
and the six `FUNC_*_fn` accessors (2831, 2841, 2849, 2857, 2866, 2875).
`_func_hash` still uppercases so case-colliding names share a bucket — but they now
get distinct FNCBLKs and same-name checks distinguish them correctly.

22-line repro (`tl_repro.sno`, same as prior session):
```
before fix:   push_list called with v=""                 (wrong body)
              MATCH
after fix:    Push_list called with vs="tag"             (correct body)
              push_list called with v=""                 (new downstream bug)
              MATCH
oracle:       Push_list called with vs="tag"
              push_list called with v="NP"
              MATCH
```

Full treebank-list: `''` → `('ROOT')` — 1 line of 24 expected. Gates green.

### Remaining divergence — deferred-arg evaluation for *fn(var) callcaps

The residual `push_list called with v=""` is a separate bug from case-sensitivity.
Isolated to a clean 10-line repro with no double-function trick:

```snobol4
               &ANCHOR        =  0
               &FULLSCAN      =  1
               DEFINE('cb(x)')                              :(cb_end)
cb             OUTPUT         =  'cb called with x="' x '"'
               cb             =  .dummy                     :(NRETURN)
cb_end
               word           =  NOTANY('( )') BREAK('( )')
               pat            =  '(' (word . tag) . *cb(tag) ')'
               '(NP)'  pat                                  :F(nomatch)
               OUTPUT         =  'MATCH'                    :(END)
nomatch        OUTPUT         =  'NOMATCH'
END
```
```
oracle: cb called with x="NP"
        MATCH
scrip:  cb called with x=""
        MATCH
```

**Probe to confirm semantics** (`tl_probe.sno`, pre-assigns `tag="INITIAL"`):
```
oracle: tag before match: "INITIAL"
        cb called with x="NP"           ← flush-time lookup of tag
        tag after match: "NP"
        MATCH
```

Oracle evaluates `*cb(tag)` arg at **flush time** — after `(word . tag)` has
committed the capture. scrip currently snapshots args at pattern-build time
(which for embedded EVALs means when `tag` is still unset → empty string).

**Two code paths involved:**

1. **IR direct path** — `src/driver/interp.c:3077` and `:3090`:
   `av[i] = interp_eval(fnc->children[i])` at build time. Wrong semantics
   (eager), but not the immediate scrip `--ir-run` symptom since that path
   uses SM lowering, not direct IR exec, for this case.

2. **SM lowering path** (actual scrip `--ir-run` culprit) — `src/runtime/x86/sm_lower.c:282, 302`:
   **discards args entirely.** `SM_PAT_CAPTURE_FN` op carries only `a[0].s = fname` and
   `a[1].i = kind`. `h_pat_capture_fn` in `sm_codegen.c:382` and `sm_interp.c:474` both
   call `pat_assign_callcap(child, fname, NULL, 0)` — hardcoded NULL args, 0 nargs.
   That's why `ζ->fnc_args` is empty in `bb_callcap` `CC_γ_core`.

### Next session TL-2 plan

1. **Extend SM_PAT_CAPTURE_FN** to carry arg specs. For the common case
   `*fn(var1, var2, ...)`, arg specs are simple variable names. Storage:
   `a[2].s` = comma-separated arg names (or new `a[n].s` slots if count is bounded).
   For arbitrary sub-expressions, defer to a fallback or (future) thunk mechanism.
   Start with var-name-only support — that's what treebank-list needs.

2. **Extend `pat_assign_callcap` and `callcap_t`** to store unevaluated arg
   specs alongside (or in place of) the current `DESCR_t *fnc_args` snapshot.
   Add `char **fnc_arg_names; int fnc_nargs;` for the var-name-only path.

3. **Resolve args at flush time in `bb_callcap`'s `CC_γ_core`:** for each
   `fnc_arg_names[i]`, do `NV_GET_fn(name)` → DESCR_t, pass to `g_user_call_hook`.
   This is the flush-time lookup that matches oracle semantics.

4. **Update SM lowering** (`sm_lower.c:282/302`) to walk `var_expr->children[0]->children[]`
   (the args to the inner E_FNC) and emit their names into the new opcode slots.

5. **Update `h_pat_capture_fn`** in `sm_codegen.c` and `sm_interp.c` to read the
   arg-name slots and pass them through to `pat_assign_callcap`.

6. **Also fix the IR direct path** (`interp.c:3077, 3090`) to produce unevaluated
   arg-name specs when the child is a plain `E_VAR`, so both execution paths have
   consistent semantics. For non-E_VAR args, continue eager eval (best-effort until
   a thunk mechanism is added).

7. Gate: 22-line repro matches oracle; smoke PASS=7; broker PASS=49; treebank-list
   diff shrinks toward clean.

### State at end of session

- HEAD one4all `f3d64bdb` (this session's commit)
- No uncommitted changes in one4all, corpus, or .github
- Reproducers left at `/home/claude/tl_repro.sno` (22-line), `/home/claude/tl_simple.sno`
  (10-line isolation of the callcap-arg bug), `/home/claude/tl_probe.sno` (flush-time
  semantics probe) — NOT checked into corpus (per rule: no speculative test files;
  recreate from this doc if needed).
- SPITBOL + CSNOBOL4 both built locally at `/home/claude/x64/bin/sbl` and
  `/home/claude/csnobol4/snobol4`.
