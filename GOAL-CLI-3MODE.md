# GOAL-CLI-3MODE — Collapse 4 modes to 3, delete AST-interp

**Owner:** Lon Jones Cherryholmes
**Author of this goal file:** Claude Opus 4.7 (session 2026-05-17)
**Repos:** one4all + .github

---

## Target shape (per Lon, session 2026-05-17)

Three execution modes, one orthogonal BB strategy axis (under `--interp` only):

| Flag | Meaning | BB strategy |
|------|---------|-------------|
| `--interp` | SM emulator (interprets `SM_Program`) | `--bb=brokered` (default) or `--bb=wired` |
| `--run` | SM/BB emit to memory, execute in-process (JIT) | wired only (forced) |
| `--compile` | SM/BB emit asm → assemble+link → separate process | wired only (forced) |

**Mode 1 (AST-interp, `--ast-run` / `--ir-run`) is deleted** along with `interp_eval.c` / `interp_exec.c` / `interp_call.c` / etc.

---

## Steps

- [x] **CLI-3M-1** — Add `--interp` / `--run` / `--compile` / `--bb={brokered,wired}` as aliases of `--sm-run` / `--jit-run` / `--jit-emit --x64` / `--bb-driver` / `--bb-live`. Help text updated. *Commit `a6efc60d`.*
- [x] **CLI-3M-2** — Sweep 68 scripts/docs to new flags (Group A). `--ir-run` deliberately untouched. *Commit `c91de33c`.*
- [x] **CLI-3M-3** — Reject `--bb=brokered` under `--run` and `--compile`. Default-resolve: `--interp` → brokered, `--run`/`--compile` → wired. *Commit `00dc6cd7`.*
- [x] **CLI-3M-4** — Tty-only deprecation warnings on legacy flags. `SCRIP_NO_DEPRECATION=1` silences; `SCRIP_DEPRECATION=1` forces on. *Commit `4aadcf1e`.*
- [x] **CLI-3M-5** — Audit AST-interp dependencies. *See findings below.*
- [ ] **CLI-3M-6** — Close blockers from CLI-3M-5 (Prolog + Rebus lower.c gaps).
- [ ] **CLI-3M-7** — Decide `--monitor` fate (delete vs salvage as sm-vs-jit comparator).
- [ ] **CLI-3M-8** — Delete `--ast-run` / `--ir-run` flags. Variable `mode_ir_run` goes.
- [ ] **CLI-3M-9** — Delete `interp_eval.c` / `interp_exec.c` / `interp_call.c` / `interp_ref.c` / `interp_label.c` / `interp_data.c` / `interp_hooks.c` / `interp_globals.c` / `interp_private.h` / `interp.h`. Possibly `stmt_ast.c`. Big rip — link failures surface remaining hidden dependencies.
- [ ] **CLI-3M-10** — Delete deprecated aliases (`--sm-run` / `--jit-run` / `--jit-emit` / `--bb-driver` / `--bb-live`). One name per concept.
- [ ] **CLI-3M-11** — Update PLAN.md, RULES.md (especially the "Mode 1 stays" rule in the third box), ARCH-SCRIP.md, REPO files, all forward HANDOFF-*.md.
- [ ] **CLI-3M-12** — Update AR-3 framing (IR↔AST rename can proceed once mode-1 is gone).

---

## CLI-3M-5 audit findings (session 2026-05-17, Claude Opus 4.7)

### Scope of `--ir-run` usage

| Location | Files |
|----------|-------|
| `scripts/` | 84 (57 single-mode using only `--ir-run`, 27 multi-mode using `--ir-run` plus others) |
| `docs/` | 26 (informational — validation reports) |
| `test/` | 8 (7 comments in source, 1 actual subprocess invocation: `test/beauty_subexpr_gen.py`) |
| **Total** | **111** |

### Empirical per-language probe

For each language, ran the existing smoke gate twice: once with `--ir-run` (baseline), once with `--ir-run` mechanically replaced by `--interp`. Probed in-place in `scripts/` to preserve `$HERE/scrip` path resolution.

| Language | `--ir-run` result | `--interp` result | Verdict |
|----------|---:|---:|---|
| SNOBOL4 (`test_smoke_snobol4.sh`) | 6/1 (pattern fail pre-existing) | 6/1 | ✅ no mode-1 dependency |
| Snocone (`test_smoke_snocone.sh`) | 5/0 | 5/0 | ✅ no mode-1 dependency |
| Icon (`test_icon_ir_all_rungs.sh`) | (PLAN: 194/265) | 194/36/35 of 265 | ✅ no mode-1 dependency (matches PLAN's "`--sm-run` measured 194/265 = `--ir-run` 194/265") |
| Raku (`test_raku_fileio.sh`) | 0/2 | 0/2 | ⚠️ neutral (Raku already broken pre-CLI-3M) |
| **Prolog (`test_smoke_prolog.sh`)** | **5/0** | **0/5** | ❌ **mode-1-dependent** |
| **Rebus (`test_smoke_rebus.sh`)** | **4/0** | **0/4** | ❌ **mode-1-dependent** |

### Implication for CLI-3M-6

Prolog and Rebus *both* have semantics implemented in `interp_exec.c` (mode 1) that have never been ported to `lower.c` (modes 2/3/4). The PLAN's existing PST-RB Bug #2 note ("mode-1 interp_exec missing SUBJ-PAT split that lower.c does for modes 2/3/4") covers part of this, but it was framed as a single ~30-LOC fix for Rebus only. The empirical evidence shows it's broader:

- **Rebus:** 4/4 smoke tests collapse — entire pattern execution path missing from mode 2.
- **Prolog:** 5/5 smoke tests collapse — likely the predicate-dispatch path or unification helper is mode-1-only.

Closing these is a multi-language `lower.c` implementation effort, likely spanning several sessions. Lon's decision (session 2026-05-17): **accept the regression**. Prolog and Rebus go dark for mode-1-related work; CLI-3M-6 is scheduled as a large goal that the project absorbs.

Icon's prior DAI-1..3 surgery (IJ-DEL-ICN-AST in GOAL-ICON-BB-JCON) is the template: it's exactly the same kind of work — port AST-interp paths into the lower.c → SM pipeline. Doing it for Prolog and Rebus follows the same playbook.

### Non-empirical observations

- The 27 multi-mode scripts that use `--ir-run` *alongside* other modes (e.g. `for mode in --ir-run --sm-run --jit-run; do ... done`) are typically 3-way comparators. When mode 1 dies, these need to either lose the `--ir-run` slot or be deleted. Most should lose only that slot — the comparator stays useful for `--interp` vs `--run` vs `--compile`.
- `test/beauty_subexpr_gen.py` invokes `--ir-run` via subprocess (`test/beauty_subexpr_gen.py:235` and `:621`). It's a generator script, not a gate; conversion is safe.
- The 26 docs files are validation reports historically describing what was tested. Best practice: `sed`-replace at the end of CLI-3M, not before, so historical records keep their original commands as written.

---

## Open decisions for Lon

1. **CLI-3M-7 — `--monitor` fate.** Currently it's an AST-vs-SM-vs-JIT comparator. With mode 1 gone, salvage as sm-vs-jit (delete the AST leg) or delete the mode entirely? Defaulting to deletion unless told otherwise.

2. **CLI-3M-6 ordering.** Within the Prolog+Rebus lower.c work, which language first? Suggestion: Rebus first (smaller surface area — 4 smoke tests — and PST-RB Bug #2 already has a ~30-LOC sketch in PLAN), then Prolog (larger — interplay with `pl_broker.c` and the registry mechanism from PJ-9d-partial). Reverse is also defensible if Prolog is closer to working under modes 2/3/4 than the Rebus pattern engine.

3. **`BB_MODE_DRIVER` vs `BB_MODE_BROKERED`.** These are functionally identical at the runtime check site (`stmt_exec.c:434`). Consolidating to one enum value is a small cleanup that could ride along with CLI-3M or be its own micro-goal.

---

## Authorship

Steps CLI-3M-1 through CLI-3M-5 authored by **Claude Opus 4.7**, session 2026-05-17.
