# GOAL-SNOBOL4-PAT-IR — SNOBOL4 pattern primitives as first-class IR nodes

**Repo:** one4all
**Done when:** The SNOBOL4 frontend emits `E_ANY`, `E_SPAN`, `E_LEN`, `E_POS`,
`E_RPOS`, `E_TAB`, `E_RTAB`, `E_NOTANY`, `E_BREAK`, `E_BREAKX`, `E_ARB`,
`E_ARBNO`, `E_REM`, `E_FAIL`, `E_SUCCEED`, `E_FENCE`, `E_ABORT`, `E_BAL`
directly — no `E_FNC("ANY",...)` name-string dispatch anywhere in the pipeline
for these nodes. All backends and the interpreter consume the typed nodes.
Regression: PASS count on `run_interp_broad.sh` does not drop.

---

## Problem

`ir.h` declares 18 pattern primitive IR nodes (`E_ANY`, `E_SPAN`, etc.) as
first-class kinds, each with distinct Byrd box wiring. The SNOBOL4 parser
(`snobol4.y` / `snobol4.tab.c`) emits them as `E_FNC` nodes with a string name
(`sval = "ANY"`, etc.) instead. Every backend then re-identifies them by
`strcasecmp(e->sval, "ANY")` — string matching at emit time, not kind dispatch.

Consequences:
- Pattern primitives are not typed — a typo in `sval` silently misfires.
- Icon scanning shares the same Byrd box wiring but cannot reuse SNOBOL4
  pattern nodes because they arrive as untyped `E_FNC`.
- The interpreter (`scrip.c`) has a split: `case E_ANY:` in `interp_eval_pat`
  works only if the node is typed; SNOBOL4 reaches it via a separate
  `E_FNC`→name-match path. Dead code risk.
- Future frontends (Rebus, Snocone) that want pattern primitives must
  re-implement the same name-match hack.

The fix: add a lowering pass in the SNOBOL4 frontend that rewrites
`E_FNC("ANY",args)` → `E_ANY(args)` (and so on for all 18) immediately after
parsing, before IR reaches any backend.

---

## Architecture note

Icon scanning (`?` operator, `E_SCAN`) drives the same cursor/Byrd machinery as
SNOBOL4 pattern matching. Once pattern primitives are typed IR nodes, Icon can
emit `E_ANY`, `E_LEN`, etc. directly in scanning contexts — sharing one
implementation across both frontends. This is the long-term motivation; it is
**not** in scope for this goal. This goal is SNOBOL4-only: get the frontend
clean first.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/snobol4.y` | Parser — currently emits `E_FNC` for pattern prims |
| `src/frontend/snobol4/snobol4_lower.c` | Lowerer — add rewrite pass here |
| `src/driver/scrip.c` | Interpreter — `interp_eval_pat` already has `case E_ANY:` etc.; remove the redundant `E_FNC` name-match path after rewrite |
| `src/backend/emit_x64.c` | x64 emitter — replace `strcasecmp(e->sval,"ANY")` with `case E_ANY:` |
| `src/backend/emit_c.c` | C emitter — same |
| `src/backend/emit_jvm.c` | JVM emitter — same |
| `src/backend/emit_net.c` | .NET emitter — same |
| `src/backend/emit_wasm.c` | WASM emitter — same |
| `src/ir/ir.h` | Already correct — 18 nodes declared |

---

## Steps

- [ ] **S-1** — Audit: list every `strcasecmp`/`strcmp` on pattern prim names
  across all backends and `scrip.c`. Produce a count of sites to fix.
  Gate: count documented here as state variable `SITES=N`.

- [ ] **S-2** — Add `snobol4_lower_pat()` in `snobol4_lower.c`:
  walk the IR tree after parse, rewrite every `E_FNC` whose `sval` matches a
  pattern primitive name to the corresponding typed `E_*` node, preserving
  `children` and freeing `sval`.
  Mapping (case-insensitive):
  `ANY→E_ANY  NOTANY→E_NOTANY  SPAN→E_SPAN  BREAK→E_BREAK  BREAKX→E_BREAKX`
  `LEN→E_LEN  POS→E_POS  RPOS→E_RPOS  TAB→E_TAB  RTAB→E_RTAB`
  `ARB→E_ARB  ARBNO→E_ARBNO  REM→E_REM  FAIL→E_FAIL  SUCCEED→E_SUCCEED`
  `FENCE→E_FENCE  ABORT→E_ABORT  BAL→E_BAL`
  Call this pass from `prolog_compile()` equivalent in `snobol4_driver.c` /
  `CMPILE.c` after the parse returns a `Program*`.
  Gate: `make scrip` clean.

- [ ] **S-3** — Update `scrip.c` `interp_eval_pat()`: remove the `E_FNC`
  name-match fallback for pattern primitives. All 18 now arrive as typed nodes.
  Gate: `bash test/smoke.sh` PASS; `bash test/run_interp_broad.sh` no regression.

- [ ] **S-4** — Update `emit_x64.c`: replace all `strcasecmp(e->sval,"ANY")`
  (and siblings) with `case E_ANY:` dispatch. Remove `PAT_FNC_NAMES` array if
  it becomes dead.
  Gate: `make scrip` clean; x64 emit regression test PASS.

- [ ] **S-5** — Update `emit_c.c`, `emit_jvm.c`, `emit_net.c`, `emit_wasm.c`:
  same pattern — kind dispatch replaces name-string matching.
  Gate: `make scrip` clean; each backend smoke test PASS.

- [ ] **S-6** — Verify no `strcasecmp`/`strcmp` on pattern prim names remains
  anywhere in the pipeline (grep gate).
  Gate: `grep -r "strcasecmp.*ANY\|strcmp.*ANY\|strcasecmp.*SPAN" src/` → zero hits.

- [ ] **S-7** — Full regression: `bash test/run_interp_broad.sh`.
  Gate: PASS count ≥ pre-goal baseline.

- [ ] **S-8** — Update PLAN.md ☑ done.

---

## State variables

```
SITES=?          # count of strcasecmp/strcmp pattern prim sites (set in S-1)
BASELINE=?       # run_interp_broad.sh PASS count before this goal (set in S-1)
```

---

## Rules
- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- No ad-hoc builds — use `make scrip` and scripts in `one4all/build/`.
- Do not modify corpus `.sno` source to work around any regression.
