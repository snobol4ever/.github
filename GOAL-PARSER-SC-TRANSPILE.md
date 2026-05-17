# GOAL-PARSER-SC-TRANSPILE.md — Six parser_*.sc producing AST trees via Snocone→SNOBOL4 transpile + 2-way sync-monitor harness

**Repo:** one4all + corpus + .github
**Parent:** Independent goal complementing `GOAL-PARSER-PURE-SYNTAX-TREE.md` and `GOAL-PST-REBUS.md`
**Author:** Lon Jones Cherryholmes · Claude Opus 4.7
**Date opened:** 2026-05-17

---

## ⛔ Session Start Protocol (every session, no exceptions)

Before touching any code in this goal, the session must:

1. **Clone the standard three repos** (`.github`, `corpus`, `one4all`) per the global `PLAN.md` protocol.
2. **Read the SPITBOL manual** (`spitbol-manual-v3_7.pdf`) using the cheatsheet in `GOAL-PST-REBUS.md` — at minimum:
   - Ch 15 operator priority table (`/tmp/spitbol.txt` line 7757)
   - Ch 18 pattern primitives + pattern-match algorithm (lines 8683, 8718)
   - Ch 16 keywords `&FULLSCAN`, `&ANCHOR`, `&MAXLNGTH` (line 8074)
   - Ch 14 SUBJ ? PAT = REPL layout (line 7695)
   - Ch 17 datatype conversion matrix (line 8509)
   - Ch 9 EVAL/CODE rules (~line 5187)
   - Appendix C "Differences from SNOBOL4+" (line 14580+)
3. **Read `corpus/SCRIP/parser_snocone.sc` in full** — this is the canonical reference for Snocone's exact syntax as accepted by SCRIP today. The grammar declared there is the language we are transpiling FROM.
4. **Read `corpus/SCRIP/README.md`** for the runtime-file load order and the role of each `.sc` file in the shared infrastructure.
5. **Read `.github/ARCH-SNOCONE.md`** for the implementer-level Snocone semantics view.

Without these reads completed, the session is not qualified to make grammar or semantics decisions. Don't skip.

---

## 🎯 Goal (one sentence)

Get all six `parser_*.sc` programs producing AST trees that match the C-side `--dump-ast` reference output, by **transpiling each parser_*.sc to a portable .sno program**, then comparing the .sno output under SCRIP vs. SPITBOL via the existing two-way IPC sync-step monitor.

---

## 💡 Architectural Insight (Eureka)

The current PST-REBUS approach treats parser_*.sc as **first-class input** to SCRIP and pushes through every SCRIP runtime bug encountered (`rt_bb_arbno` ζ corruption, BB pattern emission stack issues, deferred-var rebuild paths). That gauntlet is long and each bug is expensive to find because we have no oracle for what Snocone "should" do.

The original Snocone (Mark Emmer's, the source of `sb.sno` etc.) was **a Snocone-to-SNOBOL4 transpiler**: Snocone source → SNOBOL4 source → SPITBOL. We are reinventing that.

**Once we have a transpiler:**

- **A Snocone oracle exists for the first time.** Currently SCRIP is the only thing that can run Snocone — there is nothing to compare against. Post-transpiler, the same `.sc` file produces SNOBOL4 that SPITBOL runs, and SPITBOL becomes a Snocone oracle by transitivity.
- **The 2-way sync-step monitor (already built) becomes a Snocone debugger.** `parser_<lang>.sc → parser_<lang>.sno → SPITBOL + SCRIP --sm-run/--jit-run side by side`, divergence reported at the first differing CALL/RETURN/VALUE event. Each bug in SCRIP's Snocone runtime shows up as a clean divergence with a 5-line repro.
- **The transpiler itself stress-tests `lower.c`.** Each construct in parser_*.sc forces a Snocone→AST→SNOBOL4 path that today only roundtrips Snocone→AST→IR. Bugs found in lower.c during transpiler development feed back into the main GOAL-PST-REBUS work.
- **We trust the LOWER step.** Per Lon: "we must just trust our LOWER step, and find bugs in lower while we are at it going along." LOWER produces the `tree_t` we transpile from. If LOWER is correct, the transpiler emits semantically-faithful SNOBOL4. If the transpiled SNOBOL4 diverges from SCRIP's direct execution of the .sc, the bug is in **one of**: LOWER, SM/BB runtime, transpiler. Sync-monitor tells us which.

This is the right shape of the problem.

---

## ⛔ Implementation Constraints (binding)

Per Lon directive 2026-05-17:

1. **`parser_<lang>.sc` files may use ONLY six functions from the shared `corpus/SCRIP/` runtime:** `shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop`. (Defined in `semantic.sc` and `counter.sc`.)
2. **No language-specific helpers.** Today `icon_helpers.sc` (4 leaf-push helpers + `notmatch`) and `raku_helpers.sc` (`push_interp_str`, `dq_unescape`, 9 `finish_*` variable-arity assemblers) exist. These must be **eliminated** — their logic either folds into grammar rules expressed in terms of the six allowed primitives, or migrates into the C-side `lower.c` / `rebus_lower.c` / `icon_lower.c` paths.
3. **`pop`, `foldop`, `nDec`, `reduce_opsyn`, `reduce_prim`, `reduce_call`, `nPushName`** — currently exported by `semantic.sc` — must NOT be called from any `parser_*.sc`. Their use in current grammars must be replaced with combinations of the six allowed.
4. **No `*Var` deferred references**, where Var is itself a Snocone function. Pattern composition is allowed (`*Letter *Letter`), but `*foo()` constructs that defer call-time evaluation must be re-expressed using the shift/reduce stack and counter primitives. Rationale: per GOAL-PST-REBUS.md remaining wall, `*Var` deferred references trigger `bb_deferred_var` rebuild paths and the JIT-stack pointer bug — eliminating them removes that bug from the parser-side surface entirely.
5. **The transpiler's output is portable SNOBOL4.** No SPITBOL-only extensions. The transpiled `.sno` must run on:
   - SCRIP `--ir-run`, `--sm-run`, `--jit-run` (all three modes)
   - SPITBOL x64 (`/home/claude/x64/bin/sbl -bf`)
   - CSNOBOL4 (only if Silly target, otherwise not required)

---

## 🔧 Architecture

```
parser_<lang>.sc                                  (Snocone source — shared shape)
       │
       │  SCRIP frontend (existing)
       ▼
   tree_t AST                                     (pure-syntax tree — LOWER trusts this)
       │
       │  NEW: src/transpile/sc_to_sno.c
       ▼
parser_<lang>_transpiled.sno                      (portable SNOBOL4 source)
       │
       │  [SCRIP modes 1/2/3]            [SPITBOL]
       ▼                                            ▼
    SCRIP exec                                   SPITBOL exec
       │                                            │
       │  IPC binary trace                          │  IPC binary trace
       ▼                                            ▼
       └────────► 2-way sync-step monitor ◄─────────┘
                  (existing: scripts/run_monitor_sync_bin.sh)
                  reports FIRST divergence, last-agree line + first-disagree line
```

For the SCRIP side, the input is **transpiled to SNOBOL4** rather than executed as Snocone. This:
- Removes SCRIP's Snocone runtime from the equation on the SPITBOL-comparison path.
- Validates LOWER end-to-end (LOWER → tree_t → transpile → SNOBOL4 must match SPITBOL).
- Allows running the parser through SPITBOL today (no Snocone runtime in SPITBOL world).

A separate path runs the original `.sc` through SCRIP directly (`--ir-run corpus/SCRIP/...` chain), and compares its output to the transpiled `.sno`-via-SPITBOL output. That's the **outer** Snocone-runtime oracle. The sync-monitor handles the **inner** divergence-when-running-the-same-.sno cross-mode test.

---

## 🪜 Rungs (execute in order; one construct per commit unless documented as composite)

### Phase 0 — Reading & Snocone fluency

- [ ] **SCT-0a** — Session-start reading complete: SPITBOL manual cheatsheet sections, `parser_snocone.sc`, `corpus/SCRIP/README.md`, `.github/ARCH-SNOCONE.md`. Commit message: `SCT-0a: reading-only session, no code change`. The "commit" is a single one-line note in `corpus/SCRIP/README.md` recording the reading-completed timestamp; no source touched.
- [ ] **SCT-0b** — Hand-write a 5-line `.sc` "echo" program that exercises: literal pattern, ANY/SPAN/BREAK, `shift(lit, 'TT_QLIT')`, `reduce('TOP', 1)`, `nPush/nInc/nTop/nPop`. Confirm runs cleanly under existing SCRIP shared-runtime chain. This is the lowest-common-denominator surface for SCT-1 to target. Commit: the test file under `corpus/SCRIP/tests/sct_echo.sc` + matching `.ref` SPITBOL would produce if hand-translated.

### Phase 1 — Transpiler MVP

- [ ] **SCT-1 — Bootstrap: `parser_snobol4.sc` → `parser_snobol4.sno`.**
  Implement `src/transpile/sc_to_sno.c` (new file). Reads a `tree_t*` AST produced by SCRIP's Snocone frontend, walks it, emits SNOBOL4 source on stdout. Target: handles the 25-construct subset that `parser_snobol4.sc` (253 lines) uses. Reuses literal/ID/var nodes verbatim; lowers Snocone pattern definitions to SNOBOL4 pattern assignments verbatim; lowers `function fn(a,b)` to `DEFINE('fn(a,b)') :(fn_end)` + label + `:(RETURN)` + `fn_end`; lowers `while (cond) { body }` to `loop_N stmts :(test_N); test_N cond :S(loop_N); ...`; etc.
  Wire as `--sc-to-sno` flag on `scrip`. Acceptance: `scrip --sc-to-sno corpus/SCRIP/parser_snobol4.sc | sbl -bf -` produces output bytewise-identical to `scrip --ir-run corpus/SCRIP/global.sc ... parser_snobol4.sc < sample.sno`. Test sample: `corpus/programs/snobol4/parser/atom_id.sno`.

- [ ] **SCT-2 — `parser_rebus.sc` → `parser_rebus.sno`.**
  Same as SCT-1 but for Rebus parser. New constructs to handle in transpiler: `OPSYN`, `&FULLSCAN` setter (pass through verbatim), `epsilon` (already known), counter idioms (`nPush/nInc/nTop/nPop` → SNOBOL4 stack manipulation already in `counter.inc`). Sample: `corpus/programs/rebus/parser/paren.reb`.

- [ ] **SCT-3 — `parser_snocone.sc` → `parser_snocone.sno`.**
  The hardest one: parser_snocone.sc is 931 lines and uses constructs the others don't (record declarations, function returns). May expose `lower.c` gaps that surface as `[NO-AST]` stubs in transpile mode — fix those in `lower.c`, never in the transpiler. Sample: `corpus/programs/snocone/corpus/sc1_literals.sc`.

- [ ] **SCT-4 — `parser_icon.sc` → `parser_icon.sno`.**
  Sub-rung blocker: `icon_helpers.sc` must be deleted FIRST. Its 4 leaf-push helpers + `notmatch` get inlined into the grammar (`push_qlit` and friends become `shift(*X, 'TT_QLIT')` directly; `notmatch` was `~match` — express via OPSYN'd `~`). Sample: `corpus/programs/icon/parser/fail_stmt.icn`.

- [ ] **SCT-5 — `parser_raku.sc` → `parser_raku.sno`.**
  Sub-rung blocker: `raku_helpers.sc` must be deleted FIRST. The 9 `finish_*` variable-arity assemblers fold into `reduce` with `nTop()` argument. `push_interp_str` / `dq_unescape` migrate to C-side `raku_lower.c`. Sample: `corpus/programs/raku/parser/str_chars.raku`.

- [ ] **SCT-6 — `parser_prolog.sc` → `parser_prolog.sno`.**
  Independent of GOAL-PST-PROLOG's frontend work. The Prolog parser_*.sc is largest at 1040 lines; some constructs may need `lower.c` fixes. Sample: `corpus/programs/prolog/rung01_hello_hello.pl`.

### Phase 2 — Two-way harness

- [ ] **SCT-7 — Build the harness driver `scripts/run_parser_sync_monitor.sh`.**
  Wraps the existing IPC infrastructure (`monitor_sync_bin.py`, `monitor_ipc_bin_csn.c`, `x64/monitor_ipc_bin_spl.c`). Inputs: `<lang> <sample-file>`. Runs:
  1. `scrip --sc-to-sno parser_<lang>.sc > /tmp/parser_<lang>.sno`
  2. SCRIP side: `scrip --sm-run /tmp/parser_<lang>.sno < <sample>` with `MONITOR_READY_PIPE` set
  3. SPITBOL side: `sbl -bf /tmp/parser_<lang>.sno < <sample>` with `MONITOR_READY_PIPE` set (requires SPITBOL IPC patch — separate sub-rung if not yet landed)
  4. `monitor_sync_bin.py` orchestrates step-comparison
  
  Outputs: PASS if both produce same AST dump and same trace events; FAIL with last-agree + first-disagree line numbers if not.

- [ ] **SCT-8 — Triage and fix first divergence found by SCT-7 for each parser.**
  Each parser's first divergence in the 2-way harness becomes one ticket. Per Lon: "find bugs in lower while we are at it going along." Expect bugs in: (a) transpiler emission for some construct, (b) `lower.c` for some construct, (c) SCRIP's SM/BB runtime for some pattern construct. Fix per-bug.

### Phase 3 — Closure

- [ ] **SCT-9 — All six parser_*.sc produce AST trees matching C `--dump-ast` reference.**
  Validation script: `scripts/test_parser_sc_transpile.sh`. For each `(lang, sample)`:
  1. Run transpiled `.sno` via SCRIP (3 modes) — collect AST output
  2. Run transpiled `.sno` via SPITBOL — collect AST output
  3. Run C `scrip --dump-ast` on the sample — collect reference AST
  4. All three must match (modulo whitespace).
  Acceptance: 6 langs × 4 sources × matching = 24/24 PASS.

- [ ] **SCT-10 — Delete sidecar helpers permanently.**
  `corpus/SCRIP/icon_helpers.sc` and `corpus/SCRIP/raku_helpers.sc` removed from corpus. `run_scrip_parser.sh` no longer loads them. README updated. Gate: SCT-9 still passes.

- [ ] **SCT-11 — Document the Snocone subset.**
  `corpus/SCRIP/SNOCONE-SUBSET.md` — the formal grammar of "the Snocone the parser_*.sc files use", enumerated from observed constructs across all six grammars after they're stable. This becomes the spec the transpiler targets and the surface area the SCRIP runtime must support.

---

## 📊 State

```
status:    OPEN. No rungs landed. Goal opened 2026-05-17 by Lon.
watermark: N/A
next:      SCT-0a (reading-only session) → SCT-0b (echo test) → SCT-1 (parser_snobol4 transpile)
authors:   Goal authored by Lon Cherryholmes + Opus 4.7, 2026-05-17.
```

---

## 🧭 Relationship to other goals

| Goal | Relationship |
|------|--------------|
| `GOAL-PST-REBUS.md` | This goal **does not block** PST-REBUS. PST-REBUS continues fixing the direct Snocone-runtime path (`rt_bb_arbno` ζ corruption, BB-cache, labtab). This goal builds an **alternate path** that doesn't depend on those bugs being fixed — it transpiles around them. When PST-REBUS lands, the two paths converge: SCRIP runs `.sc` directly AND transpiles correctly; both produce identical AST. |
| `GOAL-PARSER-PURE-SYNTAX-TREE.md` | This goal **depends on** that one's invariant that LOWER produces `tree_t` correctly. The transpiler walks the same `tree_t`. If LOWER is wrong, transpiler is wrong by transitivity — but the sync-monitor will reveal that as a divergence. |
| `GOAL-LANG-SNOCONE.md` | This goal **defines** the Snocone subset. The post-SCT-11 spec becomes input to LANG-SNOCONE acceptance criteria. |
| `GOAL-PST-PROLOG.md` | Orthogonal. SCT-6 (Prolog) can land independently. |

---

## 📝 Notes for future sessions

- **The transpiler is a C program**, not Snocone. Lives in `src/transpile/sc_to_sno.c`. Walks `tree_t*` produced by SCRIP's existing Snocone frontend. Outputs SNOBOL4 to stdout. Driven by new `scrip --sc-to-sno` flag. Per RULES.md "case-sensitive only": no folding anywhere; identifiers pass through verbatim.
- **Trust LOWER.** If transpiler emits `oops`, LOWER probably emitted `oops` first. Fix LOWER, the transpiler stays correct. The transpiler is mechanical — it must not "smart-correct" anything from the AST.
- **The 2-way harness already exists.** `scripts/monitor_sync_bin.py` + `monitor_ipc_bin_csn.c` + `x64/monitor_ipc_bin_spl.c` were built in session #19 (per RULES.md "Sync-step monitor — keyword catch-alls only"). Reuse, don't rebuild.
- **6 functions, no more.** `shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop`. Any rung that introduces a seventh primitive must be a separate `.github` issue documenting why — never silent. The discipline is the spec.
