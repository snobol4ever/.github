# GOAL-CLI-3MODE — Collapse 4 modes to 3, delete AST-interp

**Owner:** Lon Jones Cherryholmes
**Author of this goal file:** Claude Opus 4.7 (session 2026-05-17)
**Repos:** one4all + .github

**Status update (2026-05-17j, Opus 4.7):** CLI-3M-8 and CLI-3M-10
landed in one commit pair (`b65882ea` scripts+docs sweep, `730da38e`
scrip.c argv-parser rewrite). The deprecated alias surface is now
GONE from the entire codebase except for historical text in this and
related goal files. Variable `mode_ir_run` deleted from scrip.c.
`test_icon_sm_no_ast_walk.sh` deleted. CLI-3M-9 (`interp_*.c` big
rip) remains open and is now the next major step — see GOAL-ICON-BB-JCON
DAI-7 for a scout-tier dead-code sweep that informs CLI-3M-9 scope.

NOTE: in the text below, sed-mangling collapsed many `--ast-run`,
`--ir-run`, `--sm-run`, `--jit-run` references to bare `--interp`.
The semantics of the original text are preserved where the canonical
flag is still correct (the deprecated alias had become the canonical
name). Where the original referred specifically to mode 1 vs mode 2
distinctions, the text now reads tautologically; in such cases the
reader should infer "the old --ir-run / --ast-run flag (mode 1)" from
context.

---

## Target shape (per Lon, session 2026-05-17)

Three execution modes, one orthogonal BB strategy axis (under `--interp` only):

| Flag | Meaning | BB strategy |
|------|---------|-------------|
| `--interp` | SM emulator (interprets `SM_Program`) | `--bb=brokered` (default) or `--bb=wired` |
| `--run` | SM/BB emit to memory, execute in-process (JIT) | wired only (forced) |
| `--compile` | SM/BB emit asm → assemble+link → separate process | wired only (forced) |

**Mode 1 (the AST-interp flag pair `--ast-run` / `--ir-run`) was deleted in CLI-3M-10** (commit `730da38e`). The
`interp_eval.c` / `interp_exec.c` / `interp_call.c` / etc. C files
still exist on disk but are unreachable from any CLI flag — CLI-3M-9
will rip them out.

---

## Steps

- [x] **CLI-3M-1** — Add `--interp` / `--run` / `--compile` / `--bb={brokered,wired}` as canonical flags alongside the legacy aliases `--ast-run` / `--ir-run` / `--sm-run` / `--jit-run` / `--jit-emit` / `--bb-driver` / `--bb-live`. Help text updated. *Commit `a6efc60d`.*
- [x] **CLI-3M-2** — Sweep 68 scripts/docs to new flags (Group A). The remaining sites with legacy aliases were left for CLI-3M-10. *Commit `c91de33c`.*
- [x] **CLI-3M-3** — Reject `--bb=brokered` under `--run` and `--compile`. Default-resolve: `--interp` → brokered, `--run`/`--compile` → wired. *Commit `00dc6cd7`.*
- [x] **CLI-3M-4** — Tty-only deprecation warnings on legacy flags. `SCRIP_NO_DEPRECATION=1` silences; `SCRIP_DEPRECATION=1` forces on. *Commit `4aadcf1e`. Removed entirely in CLI-3M-10.*
- [x] **CLI-3M-5** — Audit AST-interp dependencies. *See findings below.*
- [x] **CLI-3M-6** — Triage CLI-3M-5 findings. *Result: no closures needed; see "CLI-3M-6 resolution" below.*
- [x] **CLI-3M-7** — `--monitor` kept; demoted from 3-way (mode-1 AST-interp vs mode-2 SM-interp vs mode-3 JIT-run) to **2-way (mode-2 SM-interp vs mode-3 JIT-run)**, since mode 1 is gone. *Lon decision, session 2026-05-17j (Opus 4.7).* Implementation note: `sync_monitor_run(ast_prog, 1, input_path)` in `scrip.c::main` is the entry point; the second arg appears to be a participant-count signal. After CLI-3M-9 deletes the `interp_*.c` files, the monitor's AST-interp comparator path is dead — the 3-way comparison collapses to 2-way naturally. Concrete work item for next session: audit `sync_monitor.c` for any explicit reference to mode-1 / AST-interp / `execute_program` and remove those branches; verify the 2-way SM-vs-JIT comparison still produces useful DIVERGE reports. Not blocking on CLI-3M-9 — the cleanup can land before or after.
- [x] **CLI-3M-8** — Delete the AST-interp flag pair (legacy `--ast-run` / `--ir-run`). Variable `mode_ir_run` removed from scrip.c. Test case in `test_smoke_sn26_label_flow.sh` (lines 88-90) removed in earlier session. *Landed jointly with CLI-3M-10, commits `b65882ea` + `730da38e`, 2026-05-17j.*
- [x] **CLI-3M-9 (partial)** — `interp_exec.c` deleted (378 LOC). `188475d7` 2026-05-18. The pure AST-walk top-level loop (`execute_program`, `execute_program_steps`) is gone. `interp_eval.c` kept (contains live Icon builtins dispatcher + `interp_eval` AST walker — splitting is CLI-3M-9 follow-up). All other `interp_*.c` kept: they provide live runtime infrastructure. `interp_ast_stubs.c` provides `g_exec_prog=NULL` and `execute_program_steps` stub. See commit message for full accounting.
- [x] **CLI-3M-10** — Delete deprecated aliases (`--ast-run` / `--ir-run` / `--sm-run` / `--jit-run` / `--jit-emit` / `--sm-emit` / `--bb-driver` / `--bb-live` / `--dump-ir` / `--dump-ir-bison` / `--x64`). One name per concept. scrip.c internal variables renamed to match CLI flag names (`mode_sm_run` → `mode_interp`, `mode_jit_run` → `mode_run`, `opt_jit_emit`+`opt_emit_x64` → `mode_compile`+`mode_compile_x86`, `dump_ir` → `dump_ast`). 104 files swept in `b65882ea`; argv parser rewritten in `730da38e`. *Commits `b65882ea` + `730da38e`, 2026-05-17j (Opus 4.7).*
- [ ] **CLI-3M-11** — Update PLAN.md, RULES.md (especially the "Mode 1 stays" rule in the third box), ARCH-SCRIP.md, REPO files, all forward HANDOFF-*.md. **Most of this landed in CLI-3M-10's docs sweep; finishing pass after CLI-3M-9.**
- [ ] **CLI-3M-12** — Update AR-3 framing (IR↔AST rename can proceed once mode-1 is gone).

---

## CLI-3M-5 audit findings (session 2026-05-17, Claude Opus 4.7)

### ⚠️ Correction notice

The initial audit of this section (committed in this same goal-file's first commit) reached a wrong conclusion — that Prolog and Rebus smoke gates fully collapse under `--interp`. That conclusion came from a probe-methodology bug: probe scripts were copied to `/tmp/`, which broke their `HERE=$(dirname BASH_SOURCE); SCRIP=$HERE/../scrip` resolution to `/scrip` (nonexistent). The "0/5 Prolog" and "0/4 Rebus" results were every test failing because no scrip binary was executing, not real semantic regressions.

Lon's decision in response to the (incorrect) audit — "accept the regression and proceed" — turned out to require less work than first stated. The corrected audit below shows mode-1 deletion is **near-net-positive** with one tiny regression.

### Scope of `--interp` usage

| Location | Files |
|----------|-------|
| `scripts/` | 84 (57 single-mode using only `--interp`, 27 multi-mode using `--interp` plus others) |
| `docs/` | 26 (informational — validation reports) |
| `test/` | 8 (7 comments in source, 1 actual subprocess invocation: `test/beauty_subexpr_gen.py`) |
| **Total** | **111** |

### Empirical per-smoke-gate probe (corrected methodology: in-place sed in `scripts/`)

| Smoke gate | `--interp` (baseline) | `--interp --bb=brokered` | `--interp --bb=wired` |
|------------|:--------------------:|:------------------------:|:---------------------:|
| `test_smoke_icon.sh` | 5/0 | **5/0** ✅ | **5/0** ✅ |
| `test_smoke_prolog.sh` | 5/0 | **5/0** ✅ | **5/0** ✅ |
| `test_smoke_raku.sh` | 5/0 | **5/0** ✅ | **5/0** ✅ |
| `test_smoke_rebus.sh` | 4/0 | **4/0** ✅ | **4/0** ✅ |
| `test_smoke_scrip_all_modes.sh` | 2/0 | 2/0 ✅ | 2/0 ✅ |
| **`test_smoke_snobol4.sh`** | **6/1** | **7/0** 🎉 | **7/0** 🎉 |
| `test_smoke_snocone.sh` | 5/0 | 5/0 ✅ | 5/0 ✅ |
| **`test_smoke_unified_broker.sh`** | **21/28** | **22/27** ✅ | **22/27** ✅ |
| `test_smoke_sn26_label_flow.sh` | 1/2 | 0/3 ⚠️ | 0/3 ⚠️ |
| `test_smoke_sn26_auto_binary.sh` | 1/0 | NORESULT * | NORESULT * |
| `test_smoke_sn26_scr_subscript_bridge.sh` | 1/0 | NORESULT * | NORESULT * |
| `test_smoke_snobol4_jit.sh` | NORESULT | NORESULT | NORESULT |

* These tests assert with Python rather than emit `PASS=N FAIL=N`. Both modes produce the same AssertionError output — they're broken upstream, not regressed by mode-2.

### Real findings

1. **Five frontend languages — Icon, Prolog, Raku, Rebus, Snocone — convert cleanly to `--interp`.** All smoke gates green in both BB modes.
2. **SNOBOL4 smoke gains a passing test** going from `--interp` (6/1) to `--interp` (7/0). The previously failing `pattern` test now passes under mode 2.
3. **Unified broker gains 1** (21/28 → 22/27).
4. **One real regression: `sn26_label_flow`** — diff shows mode 2 emits 4 LABEL records where mode 1 emits 3 (extra `LABEL name_id=4294967295 INTEGER(5)`). The test's other 2 cases fail in *both* modes (broken upstream). So the mode-1-only difference is exactly one extra label in the sync-monitor wire protocol.
5. **`test_smoke_snobol4_jit.sh`** runs a 3-way comparator (`--interp` 196 vs `--run` 195) and reports `--run < --interp` — that's the test's own check failing, not a CLI-3M regression. The list of failing programs is essentially identical between `--interp` and `--run`. This is independent work.

### Implication for CLI-3M-6

The PLAN's PST-RB Bug #2 sketch ("mode-1 interp_exec missing SUBJ-PAT split that lower.c does for modes 2/3/4") remains real but is *not* a CLI-3M-6 blocker. The Rebus smoke is green under `--interp`; PST-RB Bug #2 affects beauty.sno self-host territory, not basic smoke.

**Genuine CLI-3M-6 scope:**
1. Triage `sn26_label_flow`: 1 extra LABEL record in mode 2. Either fix mode 2 to emit one fewer label, or update the test to expect 4. Probably the latter (mode-2 is the future).
2. Audit the `--interp` invocations in the 27 multi-mode scripts and the 1 Python script — verify each is safe to convert. The single-mode 57 scripts and 26 docs files convert by bulk sed.
3. Decision on `--monitor` (CLI-3M-7) — its 3-way comparator becomes a 2-way comparator without mode 1, or it dies.

## CLI-3M-6 resolution (session 2026-05-17, Claude Opus 4.7)

**Result: no closures needed.** Investigating the items above showed each is benign:

1. **sn26_label_flow "regression" is not real.** Reading `test_smoke_sn26_label_flow.sh` (lines 88-94) shows the test explicitly encodes three independent SCRIP assertions: `--interp` expects 3 LABELs, `--interp` expects 5 LABELs, `--run` expects 5 LABELs. Baseline (1/2) was: mode 1 passes its 3-label expectation, modes 2/3 each fail their 5-label expectation (both currently emit 4). The "0/3" result under sed-rewrite is just that the rewrite turned line 90's mode-1 case into a mode-2 case (still expects 3, but mode-2 emits 4). When CLI-3M-8 deletes `--interp`, the right edit is to *remove lines 88-90 entirely* — not to patch any runtime semantics. Net change to smoke-tier totals: **−1 passing test case** for this gate, traded for **+1** each in `test_smoke_snobol4.sh` and `test_smoke_unified_broker.sh`. **Net: +1.**

2. **Multi-mode script audit (27 scripts).** All follow one of two patterns:
   - `for mode in --interp --interp --run; do ...; done` — 3-way iteration. CLI-3M-8 removes the `--interp` slot mechanically.
   - Independent invocations: `ir=$(scrip --interp ...)`, `sm=$(scrip --interp ...)`, `jit=$(scrip --run ...)`. CLI-3M-8 deletes the `ir=` line and any consumer.
   
   Both patterns are mechanical to handle in CLI-3M-8. No script has a *semantic* dependency on mode 1 beyond using it as one of several reference comparators.

3. **`test/beauty_subexpr_gen.py`** — Two subprocess calls use `--interp` (lines 235, 621). Both are generator workflows that could equivalently use `--interp`. Mechanical edit in CLI-3M-8.

**CLI-3M-6 closed. CLI-3M-7 is next.**

### Non-empirical observations

- The 27 multi-mode scripts that use `--interp` *alongside* other modes (e.g. `for mode in --interp --interp --run; do ... done`) are typically 3-way comparators. When mode 1 dies, these need to either lose the `--interp` slot or be deleted. Most should lose only that slot — the comparator stays useful for `--interp` vs `--run` vs `--compile`.
- `test/beauty_subexpr_gen.py` invokes `--interp` via subprocess (`test/beauty_subexpr_gen.py:235` and `:621`). It's a generator script, not a gate; conversion is safe.
- The 26 docs files are validation reports historically describing what was tested. Best practice: `sed`-replace at the end of CLI-3M, not before, so historical records keep their original commands as written.

---

## Open decisions for Lon

1. **CLI-3M-7 — `--monitor` fate.** Currently it's an AST-vs-SM-vs-JIT comparator. With mode 1 gone, salvage as sm-vs-jit (delete the AST leg) or delete the mode entirely? Defaulting to deletion unless told otherwise.

2. **CLI-3M-6 — `sn26_label_flow` regression.** Test expects 3 LABEL records; mode 2 emits 4. Fix mode 2 to match mode 1, or update test to expect 4? Mode 2 is the future, so updating the test reads as the right answer — but only if the extra label isn't actually wrong semantically. Need investigation of the SN-26 wire protocol intent.

3. **`BB_MODE_DRIVER` vs `BB_MODE_BROKERED`.** These are functionally identical at the runtime check site (`stmt_exec.c:434`). Consolidating to one enum value is a small cleanup that could ride along with CLI-3M or be its own micro-goal.


---

## Authorship

Steps CLI-3M-1 through CLI-3M-5 authored by **Claude Opus 4.7**, session 2026-05-17.
