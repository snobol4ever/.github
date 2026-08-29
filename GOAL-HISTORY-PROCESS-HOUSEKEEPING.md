# GOAL-HISTORY-PROCESS-HOUSEKEEPING.md — closed rename, dead-parser-removal, and session-convention work

This is a consolidated historical record, not a live design doc — **nothing in this file describes an open
task.** It replaces seven separate `GOAL-*.md` files, all now deleted, whose entire subject was a one-time
process or infrastructure initiative that finished and is no longer tracked anywhere else. Unlike the
`GOAL-HISTORY-INTERP-CHUNKS-BROKER.md` cluster (dead execution *architectures*), nothing here was ever about
how SNOBOL4/Icon/Prolog programs run — these are org/build/parser housekeeping closures. See RETIRED NAMES at
the end for the old→new mapping every stale cross-reference should resolve through.

Two more, `GOAL-CLI-3MODE.md` and `GOAL-AST-RENAME.md`, were added in a later landing (seat16, 2026-08-29,
same session as the `icon-pos-keyword-r14-not-zeroed-at-mode4-entry` row) — both carried a clean, unanimous
**100% HISTORICAL-CLOSED** verdict from seat09's survey pass with no reserved question, re-verified fresh
before folding rather than trusted from that pass (file existence, live-source grep, a commit-ancestry spot
check) — see their own sections below.

Landed via `goal-files-major-consolidation` (task file, `/home/resources/postoffice/tasks/`), executing Lon's
2026-08-28 ruling steps (1)/(3) — grade against live source, consolidate by clustering. The first four files
carried a clean, unanimous **HISTORICAL-CLOSED / safe-to-fold** verdict from the survey phase with no reserved
question attached; this landing independently re-ran the load-bearing checks rather than trusting the survey
blind (file existence, binary/symbol checks, a fresh commit-ancestry check on each cited hash) before folding.
The fifth, `GOAL-DE-INTERP.md`, is a later addition (this session) — see its own section below.

⛔ **`GOAL-DEAD-CODE-SWEEP.md` and `GOAL-SRC-REORG.md` were considered for this cluster, twice now, and both
times deliberately EXCLUDED — this session RE-CHECKED both rather than trust the prior "confidently
historical, pending one live check" framing, and found each has a reason it must NOT fold, not just a
pending nice-to-have:**
- **`GOAL-DEAD-CODE-SWEEP.md` is a live routing lane, not a closed project.** Its own 2026-06 worklist is
  genuinely done (verified again this session), but at least three OTHER files — `ARCH-SNOBOL4-RTX.md`,
  `GOAL-ICON-100.md`, `GOAL-SNOBOL4-100.md` — plus the `bb-fixup-az-cleanup` postoffice task file all
  actively say some variant of "flagged for `GOAL-DEAD-CODE-SWEEP.md`, not deleted here" about dead code
  discovered AFTER this file's own worklist closed (`bb_idx_get.cpp`/`bb_idx_set.cpp`, `bb_subject.cpp`,
  `bb_initial.cpp` — none of which appear in `GOAL-DEAD-CODE-SWEEP.md`'s own text). Folding this filename
  into a history file would silently break every one of those live pointers into a decision queue that no
  longer functions as one. Left standalone, with a fresh addendum — see its own file.
- **`GOAL-SRC-REORG.md` has one genuinely still-open item, not zero.** Its own watermark says "COMPLETE
  except GMR-8 part (b)" (evict the `Σ`/`Δ`/`Ω`/`Σlen` externs + `TEMPLATE_ADDR_*` from the emitter globals
  header). Verified fresh this session: `TEMPLATE_ADDR_SIGMA`/`_SIGLEN`/`_DELTA` are still live in
  `src/emitter/emit.h` today, and the `Σ`/`Δ`/`Ω` globals are referenced in 11 files. `PLAN.md`'s own
  `SRC REORG` row still says "Open GMR-8(b)" — correctly. This is real unfinished mechanical work, not a
  reserved policy question, and archiving the file would bury a task `PLAN.md` still tracks as active. Left
  standalone, with a fresh addendum — see its own file.

Both addenda also record a related, freshly-confirmed fact: `src/parser/` → `src/frontend/` (documented,
2026-08-26, `cf1f2961`/`d4312e86`/`c8ed9953`) → `src/parsers/` (2026-08-29, `96665b70`, Lon in-chat) — a THIRD
name for the same directory in about a month. `GOAL-SRC-REORG.md`'s own target tree (`parser/contracts/
machine/`) was already two renames behind before this session; root `CLAUDE.md`'s current text (`src/frontend/`)
is now one rename behind too. Neither is this row's file to fix; noted so whoever next touches either doesn't
re-derive it.

## The one4all → SCRIP rename

- **`GOAL-SCRIP-RENAME.md`** (was: 136 ln) — carved 2026-05-30 after Lon's directive to eradicate the `one4all`
  name (the product's former private-repo identity, since deleted) in favor of the public `SCRIP` org repo.
  Seven gated rungs (RN-1 through RN-7), all checked off: build/test scripts, source, docs, `.github`
  operational docs, two literal file renames (`REPO-one4all.md`→`REPO-SCRIP.md`,
  `GOAL-README-ONE4ALL.md`→`GOAL-README-SCRIP.md`), corpus, and a final zero-check. **Re-verified this
  landing:** `REPO-SCRIP.md` exists, `REPO-one4all.md` is gone. The file's own "Session State" claimed
  `one4all` hits at "SCRIP 0 / corpus 0 / .github 0-except-this-file" — **that specific bookkeeping line had
  already gone stale by the survey phase** (63 live `.github` hits and 2 corpus hits by the time of survey,
  all confirmed to be sanctioned frozen historical narration, not live operational refs — the RENAME's actual
  policy was honored, only its own self-reported counter drifted as later documents accumulated the token in
  historical prose). Commit `c334861` (SCRIP) is a confirmed real ancestor of current SCRIP HEAD, re-checked
  directly by this landing (`git merge-base --is-ancestor`); `ec8bbbe` (corpus) and the `.github` hash do not
  resolve by exact hash today (same hash-drift class as elsewhere in this project's history — content-level
  verification is what actually proves the rename landed, not the recorded hash).

## CMPILE removal — unifying on the bison/flex parser

- **`GOAL-REMOVE-CMPILE.md`** (was: 189 ln) — excised `CMPILE.c`, a hand-written recursive-descent parser that
  ran in parallel with the bison/flex parser (`snobol4.tab.c`/`snobol4.lex.c`) and produced a separate
  `CMPND_t`/SIL-`stype` tree whose bridge into `EXPR_t` (`cmpnd_to_expr()`) was incomplete, silently misrouting
  some expressions (the immediate trigger was an omega-driver `EVAL(string)` bug leaking a raw `BINGFN` stype
  into an `EXPR_t` kind field). All 8 steps (S-1 through S-8) checked off: `parse_expr_pat_from_str` and
  `sno_parse_string` added to `snobol4.tab.c` as the bison-path replacements for the three CMPILE parse entry
  points (program / expression / statement-block), `eval_code.c`/`snobol4_pattern.c`/`scrip.c` migrated off
  CMPILE, omega driver 15/15, beauty suite ≥15/18. **Re-verified this landing:** the `scrip` binary in this
  checkout carries zero `cmpile` symbols (`nm scrip | grep -i cmpile` — empty) and zero `#include.*CMPILE`
  anywhere in `src/` — both of the file's own literal S-6 done-when checks, run fresh rather than trusted from
  the doc. Commit `476fd067` does not resolve in this checkout (hash-drift class), but the binary-level and
  source-grep checks are the stronger proof and both pass. **Cross-reference to fix in place of this file**:
  the still-live `GOAL-TWO-STEP-HUNT.md` names this file as a blocker ("blocks on `GOAL-REMOVE-CMPILE.md`") and
  a separate survey pass already established that block reads as resolved — `parse_expr_pat_from_str`/
  `g_eval_str_hook`/`interp_eval_pat` are this file's own completed deliverables, not a coincidentally-identical
  unrelated hook. Whoever next touches `GOAL-TWO-STEP-HUNT.md` should update its dependency note to point here
  rather than to a live file that no longer exists.

## Session-setup and self-contained-script conventions

Two files that together established how a session decides what to build/install and how test/build scripts
behave once written — both now fully absorbed into standing, currently-enforced policy rather than being
live projects in their own right.

- **`GOAL-SESSION-SETUP-REFINEMENT.md`** (was: 142 ln) — replaced the old one-size-fits-all
  `build_full_session_environment.sh` (which built packages/scrip/spitbol/csnobol4 regardless of what a given
  goal actually needed) with a per-goal-file `## Session Setup` block convention, plus a categorized setup
  table in the REPO file. All 5 steps (SR-1 through SR-5) checked off, including the rename to
  `install_everything_full_stack.sh` and RULES.md/PLAN.md updates. **Re-verified this landing:**
  `install_everything_full_stack.sh` exists; the old `build_full_session_environment.sh` name is gone. The
  policy this file created is not just historically closed but **still the literal live rule today** — root
  `CLAUDE.md`'s own "Session start — mandatory protocol" step 7 ("Run the goal file's `## Session Setup`
  scripts") is this file's SR-4/SR-5 outcome, word for word.
- **`GOAL-SELF-CONTAINED-SCRIPTS.md`** (was: 131 ln) — audited `SCRIP/scripts/` (then `SCRIP/test/`) for three
  recurring failure modes (required env vars, stdin hangs on programs that read `INPUT`, unhandled missing
  prerequisites) and fixed each named script to derive its own paths from `$0`, redirect `< /dev/null`
  unconditionally, and SKIP rather than hang or error when a prerequisite is absent. All 8 steps (SC-1 through
  SC-8) checked off. **Re-verified this landing:** all 7 scripts the file names as fixed or as the model
  template (`test_smoke_scrip_all_modes.sh`, `test_csnobol4_budne_suite.sh`,
  `test_interp_broad_corpus_and_beauty.sh`, `test_icon_all_rungs.sh`, `test_smoke_unified_broker.sh`,
  `test_broad_unified_broker.sh`, `build_parse_expr_unit_test.sh`) exist today under
  `SCRIP/scripts/` exactly as named. Its "scrip blocks on stdin only when the running program reads INPUT"
  finding is the same rule root `CLAUDE.md` states today ("Always redirect `< /dev/null` on scrip calls").

## The interp-misnomer rename (DE-INTERP)

- **`GOAL-DE-INTERP.md`** (was: 141 ln) — Lon's 2026-06-15 mandate: the IR-graph interpreter was already
  deleted (`IR_interp_node`/`_once`/`_resume`/`_pump` excised to attic; mode-2 `--run` removed from the
  driver), so every surviving `interp` token in a live file/dir/function/variable/guard/Makefile-target name
  was a lie about what the code actually is — rename each to its true role. Four substrings are explicitly
  NOT the interpreter and were never touched: `reinterpret_cast` (C++ keyword), Raku string
  **interp**olation (`lower_interp_str` + the grammar's own term), the English word "interprets" in prose,
  and bomb-tombstone strings naming the dead interpreter as provenance.
  **Self-stamped `✅ DE-INTERP DONE — ALL 8 STEPS LANDED` (2026-06-15, SCRIP `6e87566`+`1d113eb`+`f60bb08`+
  `4c9b6bd`)** — the whole driver `interp_*.c`/`.h` family renamed to `driver_*` (six files + two headers,
  one atomic commit since they cross-include), `src/interp/` relocated and deleted (`rt_runtime.c` →
  `runtime/`, `IR_interp_state.h` → `emitter/box_state.h`), `pl_interp.h` → `pl_resolve.h`, the eval rail
  renamed `interp_eval*` → `eval_ast*`, and the `-Wl,--wrap=interp_eval` linker-wrap landmine in
  `build_scrip_rs23_diag.sh` moved in lockstep so the diagnostic wrap didn't silently no-op.
  **Independently re-verified this landing, not trusted from the file's own claim:** `src/interp/`,
  `src/driver/interp.h`, `src/driver/interp_private.h`, `src/parsers/prolog/pl_interp.h` (checked at the
  CURRENT `src/parsers/` path, post the frontend→parsers rename below, not the file's own stale
  `src/parser/`) are all confirmed absent. A fresh completion grep does turn up more raw `interp` hits than
  the file's own four-item allowlist names verbatim — `"the SM interpreter"` in two `scrip.c` abort
  messages, an `interp.r` comment reference in `zeta_storage.c`, and `rk_interp_primary`/`rk_interp_subexpr`
  in `raku.tab.c` — but every one is either the Raku-interpolation survivor by another name or plain English
  prose, not a residual name of the deleted graph interpreter; none is a live file/dir/symbol/guard the rung
  was chartered to rename. Disposition: 100% closed, nothing to route anywhere.

## Four-mode-to-two, and the AST-interp deletion (CLI-3MODE)

- **`GOAL-CLI-3MODE.md`** (was: 31 ln) — closed 2026-05-18. Deleted mode 1 (`--ast-run`, the AST-walking
  tree interpreter) and its `interp_eval.c`/`interp_exec.c`/`interp_call.c` files outright, collapsing what
  the file describes as a 4-mode lineup down to 3 (an SM emulator under `--run`, an SM/BB JIT also under
  `--run`, and `--compile`), gated by CLI-3M-1 through CLI-3M-12 (alias sweep → BB-strategy gates →
  deprecation → the actual file deletion → a 104-file alias-removal sweep → docs pass). **Re-verified this
  landing:** `interp_eval.c`/`interp_exec.c`/`interp_call.c` are confirmed gone, exactly as claimed. ⚠️ **But
  the file's own "End state" table is now doubly stale, not just historically accurate-then-superseded — its
  NAMED SUCCESSOR files are gone too:** `icn_runtime.c`/`interp_globals.c`/`interp_hooks.c`/`interp_data.c`
  (what it says the live runtime "moved to") all return zero hits in the tree today, and the `SM_Program`/
  `--bb=brokered`/`--bb=wired` vocabulary its End-state table centers on returns zero hits anywhere in
  `src/` — the 3-mode/BB-strategy-axis architecture this file closes with was itself later replaced by
  today's 2-mode (`--run` flat-wired x86 slab / `--compile` text asm) pipeline, most of that further
  collapse landing via `GOAL-REWRITE-SCRIP.md`'s and the DE-INTERP family's own work (both already folded,
  above and in `GOAL-HISTORY-INTERP-CHUNKS-BROKER.md`). **Not carrying the End-state table forward as
  current-state description** (same discipline this project's history files have applied every time a
  folded file's own diagram/table describes an architecture since replaced) — the load-bearing, still-true
  fact is narrower than the file's own table: mode 1 (AST-interp) is gone, and there is no surviving
  `--ast-run`/multi-alias mode confusion to rename around. Commits `a6efc60d`/`b65882ea` do not resolve by
  exact hash today (same hash-drift class as every other file this row has folded); the file-existence check
  is the real proof and it passes. Downstream note preserved: this file's own AR-3 item ("`tree_t`→`PARSE_t`
  rename... `tree_t` no longer an execution vehicle") is the same rename `GOAL-AST-RENAME.md` tracks below —
  the two files were always one lineage, now one section.

## `EXPR_t` → `AST_t` rename (AST-RENAME)

- **`GOAL-AST-RENAME.md`** (was: 34 ln) — closed 2026-05-09. Renamed `EXPR_t`/`EXPR_e`/`E_*` to `AST_t`/
  `AST_e`/`AST_*` across both SCRIP and corpus: AR-1 (C side, SCRIP `4c96e9e7`), AR-2 (Snocone parsers +
  `.ref` oracles, corpus `734bb92`), AR-3 (doc pass — PLAN.md, RULES.md, GOAL-* prose). All gates recorded as
  byte-identical at closure. **Re-verified this landing:** zero `EXPR_t`/`EXPR_e` hits anywhere in `src/`
  today; `src/ir/ast.h` and `src/ir/ast_print.c` both confirmed present at the current path (this file itself
  predates the `src/ir/` reorg and doesn't cite a path at all, so there was nothing to correct). Commit
  `4c96e9e7` does not resolve by exact hash today (same hash-drift class as elsewhere); the source-grep check
  is the stronger proof and it passes clean. The file's own opening banner (the "ZERO C BYRD BOX FUNCTIONS"
  block) is boilerplate shared verbatim across many unrelated `GOAL-*.md` files, not content specific to this
  rename — already stated as a permanent hard rule in root `CLAUDE.md`, so not duplicated here.

## RETIRED NAMES

Seven source files, all deleted, replaced entirely by this one file:

| Retired name | Where its content now lives |
|---|---|
| `GOAL-SCRIP-RENAME.md` | § The one4all → SCRIP rename |
| `GOAL-REMOVE-CMPILE.md` | § CMPILE removal — unifying on the bison/flex parser |
| `GOAL-SESSION-SETUP-REFINEMENT.md` | § Session-setup and self-contained-script conventions |
| `GOAL-SELF-CONTAINED-SCRIPTS.md` | § Session-setup and self-contained-script conventions |
| `GOAL-DE-INTERP.md` | § The interp-misnomer rename (DE-INTERP) |
| `GOAL-CLI-3MODE.md` | § Four-mode-to-two, and the AST-interp deletion (CLI-3MODE) |
| `GOAL-AST-RENAME.md` | § `EXPR_t` → `AST_t` rename (AST-RENAME) |

**Symbols/paths from the retired files that a stray grep might still turn up** (all confirmed dead or
superseded, listed once here rather than per-section): `CMPILE.c`/`CMPILE.h`, `cmpile_file`, `cmpile_lower`,
`cmpile_eval_expr`, `cmpnd_to_expr`, `cmpile_string`, `cmpile_init`, `cmpile_add_include`, `eval_via_cmpile`,
`CMPND_t`, `build_full_session_environment.sh` (renamed to `install_everything_full_stack.sh`),
`REPO-one4all.md` (renamed to `REPO-SCRIP.md`), `GOAL-README-ONE4ALL.md` (renamed to
`GOAL-README-SCRIP.md`), `one4all` / `ONE4ALL` / `One4all` as a live path/URL/var token (the bare word still
appears, correctly, inside frozen migration-history prose elsewhere — that is sanctioned, not a residual bug);
`src/interp/` (dir, gone), `src/driver/interp.h`/`interp_private.h`/`interp_globals.c`/`interp_label.c`/
`interp_hooks.c`/`interp_data.c`/`interp_call.c`/`interp_ast_stubs.c` (renamed to the `driver_*` family),
`src/parsers/prolog/pl_interp.h` (renamed `pl_resolve.h`), `interp_eval`/`interp_eval_pat`/`interp_eval_ref`
(renamed `eval_ast`/`eval_ast_pat`/`eval_ast_ref`), `__real_interp_eval`/`__wrap_interp_eval`/
`-Wl,--wrap=interp_eval` (renamed in lockstep), `scrip-interp` Makefile target (deleted); `--ast-run`/
`----run` (mode-1 flag, deleted), `interp_call.c` (deleted), `icn_runtime.c`/`interp_globals.c`/
`interp_hooks.c`/`interp_data.c` (CLI-3MODE's own claimed successors — also gone, further collapsed by
later work, see § CLI-3MODE above), `SM_Program`/`--bb=brokered`/`--bb=wired` (dead vocabulary, zero live
hits); `EXPR_t`/`EXPR_e`/`E_*` (renamed `AST_t`/`AST_e`/`AST_*`, see § AST-RENAME above).
