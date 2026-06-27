# GOAL-SELF-CONTAINED-SCRIPTS.md — All test/build scripts self-contained

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

**Repo:** SCRIP (test scripts), .github (doc)
**Done when:** Every script under `SCRIP/scripts/` runs
correctly with zero setup: no env vars to export, no stdin to pipe, no
external paths to configure. Run the script, get a result. That's it.

---

## Problem

Scripts currently have three failure modes:

1. **Env vars** — `CORPUS=...`, `INTERP=...`, `SCRIP=...` must be set by caller
2. **Stdin hangs** — programs that read INPUT block forever without piped input
3. **Missing prerequisites** — corpus/oracle not cloned, packages not installed

All three are solved the same way: the script itself handles it.

---

## Rules for self-contained scripts

1. **Paths are derived from `$0`**, never from env vars.
   ```bash
   HERE="$(cd "$(dirname "$0")" && pwd)"
   ROOT="$(cd "$HERE/.." && pwd)"
   SCRIP="$ROOT/scrip"
   ```
2. **Every `scrip` call gets `< /dev/null`** unless the test explicitly needs stdin,
   in which case the stdin data is embedded inline in the script via heredoc or printf.
3. **Every `scrip` call gets `timeout N`** (8s for unit tests, 30s for corpus runners).
4. **Corpus path is hardcoded to `/home/claude/corpus`**. If missing, the script
   clones it (using the build script), or SKIPs with a clear message — never fails silently.
5. **Oracle path is hardcoded to `/home/claude/csnobol4/snobol4`**. Same rule.
6. **build_* scripts are idempotent** — running twice is safe. They check before building.
7. **No script sources another script's env** — each is fully standalone.

---

## Steps

- [x] **SC-1** — Audit all scripts under `SCRIP/test/` for the three failure modes.
  Produce a list: script name, failure mode(s), fix needed.
  Gate: audit list committed to this goal file as a state table.

  **SC-1 Audit Results** (scripts now in `SCRIP/scripts/`):

  | Script | Failure Mode(s) | Fix Needed |
  |--------|----------------|------------|
  | `test_smoke_scrip_all_modes.sh` | **Stdin** — no `< /dev/null` on scrip calls | Add `< /dev/null` + `timeout 8` to --run and --run calls |
  | `test_csnobol4_budne_suite.sh` | **Env vars** — `CORPUS`, `INTERP`, `TIMEOUT`, `SUITE`, `FENCE` set via `:-` defaults only; no auto-clone if corpus missing | Derive paths from `$0`; add corpus SKIP-or-clone guard |
  | `test_interp_broad_corpus_and_beauty.sh` | **Env vars** + **Stdin** — `INTERP`, `CORPUS`, `INC`, `BEAUTY`, `DEMO` via `:-` only; `run_test` does not pass `< /dev/null` when no input file given | Derive paths from `$0`; add `< /dev/null` to all no-input scrip calls |
  | `test_icon_all_rungs.sh` | **Env vars** — uses `CORPUS_REPO` (non-standard); exits with error if corpus missing | Switch to `$0`-derived default; degrade to SKIP if corpus absent |
  | `test_smoke_unified_broker.sh` | ✅ already self-contained — model for all others | none |
  | `scripts/build_*.sh`, `scripts/install_*.sh` | SC-7 audit pending | see SC-7 |

- [x] **SC-2** — Fix `test_smoke_scrip_all_modes.sh` — add `< /dev/null` and `timeout 8` to all scrip calls. Header updated to reflect new location.
  Gate: ✅ runs from any directory with no env vars.

- [x] **SC-3** — Fix `test_csnobol4_budne_suite.sh` — hardcode paths from `$0`, corpus SKIP guard.
  Gate: ✅ runs from repo root, no setup; exits 0 with SKIP if corpus absent.

- [x] **SC-4** — Fix `test_interp_broad_corpus_and_beauty.sh` — hardcode paths from `$0`, corpus SKIP guard, `< /dev/null` on all no-input scrip calls.
  Gate: ✅ runs from repo root, no setup, no hang.

- [x] **SC-5** — Fix `test_icon_all_rungs.sh` — `$0`-derived defaults, SKIP (not error) if scrip or corpus absent. Timeout raised to 8s.
  Gate: ✅ runs from repo root, no setup.

- [x] **SC-6** — Write `test_broad_unified_broker.sh` (replaces deleted broken version).
  Calls SC-3/SC-4/SC-5 scripts directly. Adds inline Prolog suite (6 tests).
  Enforces non-regression floors: Icon PASS>=48, csnobol4 PASS>=34.
  Gate: ✅ written; runs from repo root, no setup, < 60s.

- [x] **SC-7** — Audited `SCRIP/scripts/` build_ and install_ scripts.
  Fixed: `build_parse_expr_unit_test.sh` had hardcoded `/home/claude/SCRIP` paths — now `$0`-derived.
  `install_clone_snobol4ever_repos.sh`: `TOKEN` via env/arg is correct per RULES (never on disk).
  Gate: ✅ all build_* and install_* scripts are idempotent and derive paths from `$0`.

- [x] **SC-8** — RULES.md updated: old "No ad-hoc builds" section replaced with full
  "Self-contained scripts" rule block covering naming convention, 7 self-containment rules,
  and the verified `< /dev/null` rationale (scrip only blocks when program reads INPUT).
  Gate: ✅ RULES.md updated and pushed with SCRIP/scripts/ reorganization commit.

---

## Current state

**DONE.** SC-1 through SC-8 complete.

Verified scrip stdin behavior: scrip blocks on stdin only when the running *program* reads `INPUT`. It does not read source from stdin when a file argument is given. `< /dev/null` is still applied unconditionally on all test harness calls — zero cost, prevents hangs on unknown corpus programs.

---

## Key files

| File | Status |
|------|--------|
| `scripts/test_smoke_unified_broker.sh` | ✅ self-contained — model template |
| `scripts/test_smoke_scrip_all_modes.sh` | ✅ SC-2 fixed |
| `scripts/test_csnobol4_budne_suite.sh` | ✅ SC-3 fixed |
| `scripts/test_interp_broad_corpus_and_beauty.sh` | ✅ SC-4 fixed |
| `scripts/test_icon_all_rungs.sh` | ✅ SC-5 fixed |
| `scripts/test_broad_unified_broker.sh` | ✅ SC-6 written |
| `scripts/build_parse_expr_unit_test.sh` | ✅ SC-7 fixed |
| `scripts/build_*.sh`, `scripts/install_*.sh` | ✅ SC-7 audited — all idempotent |
