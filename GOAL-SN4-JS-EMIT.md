# GOAL-SN4-JS-EMIT.md — SNOBOL4 → JavaScript Emitter (IR_t-based)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md, ARCH-JS.md, ARCH-EMITTER.md.
⛔ **Prereq:** GOAL-IR-EMITTER-PREREQ.md (IEP-1..6 all ✅).

**Repo:** one4all + .github
**Goal:** `scrip --target=js file.sno` emits a `.js` file; `node` runs it correctly.
**Done when (original target):** beauty.sno byte-identical to SPITBOL oracle.
**PIVOT (active):** climb the SNOBOL4 + Snocone test-suite ladders — beauty self-host is on hold.

---

## Pipeline

```
tree_t  →  lower  →  IR_t  →  emit_js.c  →  .js file
```

This emitter reads IR_t (and walks SM_Program for scalars). It produces:
- Scalar nodes → JS statements inside a `switch (_pc)` dispatch loop.
- Generator nodes (IR_PAT_*) → JS factory functions allocated before the loop and called at SM_EXEC_GEN sites.

---

## Reference implementations — all BB work is already done

Every SNOBOL4 BB is already implemented in JavaScript. Before writing any BB emitter template, read the corresponding factory in `src/runtime/js/bb_boxes.js`. Single-file forms: `git show 660339cd:src/runtime/boxes/NAME/bb_NAME.js`.

| IR_t node kind | Reference factory |
|---|---|
| IR_PAT_LIT / SPAN / BREAK / ANY / NOTANY | bb_lit / bb_span / bb_brk / bb_any / bb_notany |
| IR_PAT_LEN / POS (rpos=0/1) / TAB (rtab=0/1) | bb_len / bb_pos / bb_rpos / bb_tab / bb_rtab |
| IR_PAT_REM / ARB / ARBNO | bb_rem / bb_arb / bb_arbno |
| IR_PAT_CAT / ALT | bb_seq / bb_alt |
| IR_PAT_ASSIGN_IMM / COND | bb_capture(child,var,1or0,vars) |
| IR_PAT_FENCE / ABORT | bb_fence / bb_abort |

Also read: `src/lower/ir_exec.c` IR_exec_node() — the per-node-kind authoritative semantics.

---

## JS emission model

Scalar nodes emit into a switch/dispatch loop (required because SNOBOL4 GOTO can jump backward). Generator nodes emit as factory functions before the switch loop, returning `{succ, fail, alpha(), beta()}`; wiring functions allocate all nodes for one statement and connect succ/fail.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
node --version
bash /home/claude/one4all/scripts/test_sn4_js_ladder_safe.sh
```

---

## Steps

Closed rungs: **SJ4-JS-1 / 2 / 3 / 4a / 4b / 4c** — pattern emitters, SM-compatible runtime, SM_Program walker, instruction indexing, keywords, DEFINE / user-fn dispatch. See git log for details (commits `63adaaa4`, `a72c9b6d`, `c92aaf6b`, `6f9799e1`).

### SJ4-JS-4d — Ladder climbing (ACTIVE)

Steady-state climb of the SNOBOL4 corpus ladder (csnobol4-suite + snobol4/demo + snobol4/feat = 129 programs). Each rung is "find a class of failures, fix the root cause in the runtime or test runner, measure, commit." See git log on `src/runtime/js/sno_runtime.js` and `scripts/test_sn4_js_ladder_safe.sh` for the trail.

**Closed sub-rungs (this session, 2026-05-15, Claude Opus 4.7):**
- `a6c9b0e8` INPUT EOF/blank distinction; `_FAIL` propagation through shape-preserving builtins; `call` / `call_or_jump` set `_last_ok`; runner uses post-END data as stdin when no `.input` file. 31→41.
- `04d01f7d` arith ops return `_FAIL` instead of throwing on non-numeric or div-by-zero; `arith()` sets `_last_ok`. 41→42.
- `284310c8` `_builtin_pat_global()` helper + real `CONVERT` for INTEGER/REAL/NUMERIC/STRING. 42→43.
- `e795385d` Removed FAIL/SUCCEED/ABORT/FENCE/ARB/REM/BAL from `_kw_store` — they were `''` placeholders shadowing the real pattern objects and breaking `S BAL . B` capture. Newly passing: any, bal, case2, conv2, factor, len, loop, repl, space, trim0, trim1, words, f14_dyn_opt, longrec. 43→44 (script counter).

**Closed sub-rungs (this session, 2026-05-16, Claude Sonnet 4.6):**
- `ad035b1c` DEFERRED/succeed fix + ORD + VDIFFER builtins. Fixed critical missing case in sno_engine.js: DEFERRED/succeed wasn't propagating child-pattern success upward, silently failing all *H (variable reference in pattern) matches. Added ORD() builtin (ASCII value of first char), VDIFFER() builtin (conditional differ by value). Ladder: 44 → 47 → 49. uneval.sno, vdiffer.sno, ord.sno now PASS.
- `e19a3f87` LABEL(name) builtin added (checks if label exists, returns name or FAIL). No ladder gain — indicates label.sno is semantically complex beyond just missing builtin.

**Remaining open sub-rungs (in order of expected leverage):**
- [ ] **pattern-backtrack** — `pat $ output FAIL` should backtrack to enumerate matches. Engine doesn't loop on top-level fail. Blocks `breakx` (2nd line missing) and variants.
- [ ] **comment.sno semantics** — certain patterns matching when they shouldn't (e.g., Q1 matching ' *' when it should not). Pattern matching semantic gap, not name-stringify.
- [ ] **eval-code** — `EVAL()` / `CODE()` not implemented. Needs JS-side SNOBOL4-expression evaluator.
- [ ] **setexit** — SPITBOL `SETEXIT()` error-trap extension (6-7 tests).
- [ ] **table-sort** — `TABLE()`, `SORT()`, `RSORT()`, `CONVERT(t,"array")` stubs only. Blocks `tab.sno`, `dump.sno`.
- [ ] **file I/O** — `-include`, `LOAD`, `UNLOAD`, file operations. Test runner also has issue with custom-named `.in` files vs `.input`.
- [ ] **SJ4-JS-4e (scanerr segfault)** — Compiler-side emit error, not runtime. Doesn't block the safe runner.

---

## State (Session 2026-05-16 handoff)

```
watermark: SJ4-JS-4d (ladder climbing, "pattern-backtrack" next)
head:      one4all e19a3f87
ladder:    PASS=49 FAIL=80 TOTAL=129 (safe runner, script counter)
trajectory: prior session end 44 → this session 49 (+5 tests)
```

Session commit trail (this session):
1. `e19a3f87` — LABEL(name) builtin (investigation, no gain)
2. `ad035b1c` — DEFERRED/succeed fix + ORD + VDIFFER builtins (44→49)

---

## Key invariants

- **Reads IR_t for BB factories; walks SM_Program for scalars.** Never re-derefs the AST in modes 2/3/4.
- **19 BB kinds, all pre-implemented** in `src/runtime/js/bb_boxes.js`. Read the JS reference before writing any C emitter.
- **Switch/dispatch loop is mandatory.** SNOBOL4 GOTO can jump backward.
- **Flag:** `--target=js` (NOT `--compile --js`).
- **Runtime location:** `src/runtime/js/sno_runtime.js`. Emitted JS hardcodes the absolute path in the require() prologue.

---

## Runtime gotchas (read before debugging)

- `_vars` is a JS Proxy over `_store` that normalizes keys to uppercase. `_store['B'] = 'A'` is what actually holds the value when emitted code does `rt.store_var('B')`. Use `_store` for direct introspection.
- `push_var(name)` lookup order: `_kw_store[upper(name)]` (true keywords only) → `_vars[name]` (user bindings) → `_builtin_pat_global(upper(name))` (SNOBOL4 standard pattern globals) → `_vars[name]` again (yields null = SNOBOL4 null).
- `_FAIL` is a frozen sentinel `{_sno_fail: true}`. NEVER let it leak into JS arithmetic — the `_fail_propagate` set in `_apply` and the explicit guards in `_add/_sub/_mul/_div/_pow/arith` are the defense.
- `INPUT` getter distinguishes true EOF (zero bytes ever read) from blank line (newline immediately). True EOF returns `_FAIL`; blank line returns `''`. Honors `&TRIM` for trailing whitespace.
- Test runner pipes the post-END portion of the `.sno` as stdin when no `.input` file present (classic SNOBOL4 convention).

---

## Demo Artifacts Maintenance

**At session handoff:** regenerate all demo JavaScript artifacts and commit them if changed.

```bash
cd /home/claude/one4all
DEMO=/home/claude/corpus/programs/snobol4/demo
for sno in $DEMO/*.sno; do
  base=$(basename "$sno" .sno)
  [ "$base" = "beauty" ] && continue
  ./scrip --target=js "$sno" > "$DEMO/${base}.js" 2>/dev/null
done
cd $DEMO && for js in *.js; do node --check "$js" 2>&1 | grep -v "^$" && echo "ERROR: $js"; done
cd /home/claude/corpus && git add programs/snobol4/demo/*.js && git commit -m "Handoff: regenerated demo artifacts" 2>&1
git push
```
