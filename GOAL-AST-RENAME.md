# GOAL-AST-RENAME.md — `EXPR_t` → `AST_t`, `E_*` → `AST_*`, in lockstep across C runtime + Snocone parsers + oracle .ref files

**Repos:** one4all (C side) + corpus (parser_*.sc + .ref oracles) + .github (this file, PLAN.md, RULES.md)
**Tracker:** Lon's call — single rung sequence (AR-1 + AR-2 lockstep + AR-3) carved sess 2026-05-09 (this session). Execution next session.

**Done when:**
- No `EXPR_t`, `EXPR_e`, or `expr_e_name` identifier remains in `one4all/src/`.
- No bare `E_*` enum-value identifier (where `*` is an uppercase kind name) remains in `one4all/src/`.
- No `'E_*'` or `"E_*"` string literal remains in `corpus/programs/scrip/parser_*.sc` or any `.ref` oracle file.
- `PLAN.md` architecture paragraph and prose use **AST** for the source-faithful tagged tree and reserve **IR** for `SM_Program` (the lowered form).
- `RULES.md §"Snocone parser style"` references `AST_*` strings instead of `E_*`.
- All gates byte-identical to baseline across the rename: smoke ×6, isolation, unified_broker, csnobol4 Budne, Icon corpus 186/47/30, PARSER-* fixtures (modulo the renamed strings, which are part of the change).

---

## Truth-telling preamble — what this rename exists to fix

Recorded so future sessions don't slip back into wishful framing.

1. **The codebase calls the AST "IR" and calls the IR "SM_Program."** This
   is backwards from standard compiler vocabulary. `EXPR_t` is built
   directly by frontends from source — `kind` + `sval`/`ival`/`dval` +
   `children[]`/`nchildren`. That is an AST. `SM_Program` is a flat array
   of stack-machine instructions emitted by `sm_lower` and consumed by the
   interpreter and emitters. That is the IR. The names should match what
   the data is. CPython gets this right (`expr_ty`, `stmt_ty`, with
   `_kind`-suffixed enums for kind values); Clojure gets this right (AST
   nodes are maps with `:op` keyword, kinds like `:fn-expr` `:const`).
   one4all is the outlier today; this rename closes that gap.

2. **The Snocone `parser_*.sc` files and the C runtime build the same tree.**
   Six parsers (`parser_{snobol4,icon,prolog,raku,rebus,snocone}.sc`)
   emit s-expression trees tagged with the C-side `E_*` strings —
   `'E_FNC'`, `'E_VAR'`, `'E_CHOICE'`. Different skin (string tags vs.
   C enum), same data, same kind set. RULES.md §"Snocone parser style"
   makes this binding: *"IR node tags MUST be the exact strings `expr_dump`
   emits."* The parsers and the C runtime are two views of one AST,
   joined by string equality. Renaming one without the other splits the
   vocabulary and breaks the rule.

3. **`.ref` oracle files capture parser output.** 164 `.ref` files across
   `corpus/` contain ~1688 `E_*` references — they are byte-identical
   gates for PARSER-* tests. After the rename they must contain `AST_*`
   strings or the gates fail. This is mechanical; the issue is doing it
   in lockstep with the parser source changes so no intermediate state
   leaves oracle and parser disagreeing.

4. **The CHUNKS Step 17 work needs this rename to clear runway.** CHUNKS
   moves toward a future state where compiled SM chunks (addressed by
   `entry_pc`) replace today's `SM_PUSH_EXPR`-shipped raw `EXPR_t*`
   pointers. The eventual name for the chunk-side type is `EXPRESSION_t`
   (per Lon, sess 2026-05-09; next rename after this one lands). That
   rename is clean only if `EXPR_t` is gone — otherwise `EXPRESSION_t`
   and `EXPR_t` cohabit and read confusably. Doing AST-RENAME *first*
   unblocks the terminal rungs of CHUNKS Step 17.

5. **All sessions wait for this rename to complete.** Per Lon, sess
   2026-05-09. No parallel work on `src/runtime/x86/`, `src/driver/`,
   `src/frontend/*/`, or `corpus/programs/scrip/parser_*.sc` while AR-1
   + AR-2 are mid-flight. The rename touches 73 C files and 6 parsers;
   an intervening commit on any of them creates merge conflicts at every
   rename site. Sessions that need to do unrelated work in those areas
   wait until the AR-1 + AR-2 commits land and push.

6. **Why ALL_CAPS `AST_t` despite RULES.md §"Naming conventions"
   discouraging it.** The rule reads *"Never ALL_CAPS for new C
   types (exception: `RESULT_t`)."* Today the codebase has 15 ALL_CAPS
   `_t` SIL-derived typedefs (`EXPR_t`, `DESCR_t`, `STMT_t`, `CMPILE_t`,
   `CMPND_t`, `CODE_t`, `DATINST_t`, `DTYPE_t`, `FNCPTR_t`, `PATND_t`,
   `RESULT_t`, `TBBLK_t`, `TBPAIR_t`, `TREEBLK_t`, `ARBLK_t`). `AST_t`
   joins this established class. The rule needs updating to reflect
   actual practice; AR-3 of this goal handles that.

---

## Naming, locked

| Today | After rename |
|---|---|
| `EXPR_t` (C struct typedef) | `AST_t` |
| `EXPR_e` (C enum typedef) | `AST_e` |
| `E_VAR`, `E_FNC`, `E_CHOICE`, … (180 distinct names, 4554 references) | `AST_VAR`, `AST_FNC`, `AST_CHOICE`, … |
| `E_KIND_COUNT` (sentinel) | `AST_KIND_COUNT` |
| `expr_e_name[]` (name table in `ir.h`) | `ast_e_name[]` |
| `'E_VAR'`, `'E_FNC'`, … (parser string tags, 6 files, 647 refs) | `'AST_VAR'`, `'AST_FNC'`, … |
| `E_VAR` etc. in `.ref` oracle files (164 files, 1688 refs) | `AST_VAR` etc. |
| "the IR" in PLAN.md prose (when it means the tree) | "the AST" |
| "the IR" / "SM_Program" (when it means the lowered form) | unchanged — that **is** the IR |
| `SM_Program` (struct) | unchanged |
| Variable names like `EXPR_t *e`, `EXPR_t *node` | unchanged — only the type renames; locals stay |

Decision rationale (recorded so future sessions don't relitigate):
- `T_*` was rejected: collides with Prolog's `Term *` vocabulary (`T_VAR` next to `TERM_VAR` in `pl_runtime.c` causes reader-friction every time).
- `A_*` was rejected: shorter but requires a mnemonic translation ("A means AST"); `AST_*` is self-documenting at every reference.
- `AST_t` / `AST_e` / `AST_*` was chosen: one word, three places, zero ambiguity. The ~14KB source-byte inflation across ~6,889 occurrences is a rounding error; reader cognition is the actual constraint.

---

## Blast radius — measured, not estimated

Numbers from `grep` over fresh repos (sess 2026-05-09):

**C side (one4all/src/):**

| What | Count |
|---|---:|
| `EXPR_t` references | 1391 |
| `EXPR_e` references | 64 |
| `expr_e_name` references | 9 |
| Files containing `E_*` enum refs | 71 |
| Total `E_*` enum references | 4554 |
| Distinct `E_*` enum names | 180 |
| `'E_X'` / `"E_X"` string literals (in C debug/dump code) | 189 |
| Distinct `'E_X'` string literals (in C code) | 157 |

**Snocone parser side (corpus/programs/scrip/parser_*.sc):**

| File | Total `'E_X'` refs | Distinct |
|---|---:|---:|
| `parser_icon.sc` | 145 | 70 |
| `parser_prolog.sc` | 75 | 13 |
| `parser_raku.sc` | 255 | 38 |
| `parser_rebus.sc` | 57 | 26 |
| `parser_snobol4.sc` | 53 | 38 |
| `parser_snocone.sc` | 62 | 31 |
| **Total** | **647** | **107 distinct** |

**`.ref` oracle side (corpus/):**

| What | Count |
|---|---:|
| `.ref` files containing `E_*` | 164 |
| Total `E_*` refs across `.ref` | 1688 |
| Distinct names in `.ref` | 57 |

**Other corpus `.sc` files referencing `E_*`:**

| File | Total |
|---|---:|
| `corpus/programs/scrip/ShiftReduce.sc` | 10 |
| `corpus/programs/scrip/qize.sc` | 2 |
| `corpus/programs/scrip/semantic.sc` | 3 |
| `corpus/programs/scrip/smoke.sc` | 21 |
| `corpus/programs/scrip/tdump.sc` | 44 |

Grand totals: **~6,889 occurrences** across **~250 files** in two repos.

---

## Survey findings — known artifacts to handle

These are not blockers; the rename is mechanical and the regex strategy is safe. Documented so the executing session doesn't hit them as surprises.

### Finding 1 — 7 names exist in parsers that don't exist in C runtime

```
E_BANGPAT  E_DCG_IL  E_NOTPAT  E_PCT  E_RLIT  E_SLASH  E_VALUEPAT
```

These are parser-emitted tags whose runtime side hasn't been wired up yet (parser emits ahead of runtime — normal for parser-development work). They get renamed mechanically along with everything else: `'E_BANGPAT'` → `'AST_BANGPAT'`. The fact that they have no C-side enum value is irrelevant to the rename; whether they should ever be wired or removed is a separate, pre-existing question.

### Finding 2 — 80 names exist in C that don't exist in parsers

Some are real enum values used purely in runtime IR (no parser emits them — fine). Some are **comment-residue from old refactors** — names like `E_ARY`, `E_ASGN`, `E_BLOCK`, `E_BINOP` appear only in stale comments referencing old enum values that no longer exist. Spot-check (sess 2026-05-09):

| Name | Total refs | Comment-only | Real code |
|---|---:|---:|---:|
| `E_ABORT` | 21 | 2 | 19 (real enum value) |
| `E_AMP` | 2 | 0 | 2 (real) |
| `E_ARY` | 1 | 1 | 0 (comment-only — dead) |
| `E_ASGN` | 1 | 1 | 0 (comment-only — dead) |
| `E_BLOCK` | 1 | 1 | 0 (comment-only — dead) |
| `E_CALL` | 15 | 8 | 7 (real enum value) |
| `E_BINOP` | 2 | 2 | 0 (comment-only — dead) |

The mechanical rename catches comment-residue too, which is fine — comments mentioning `E_ARY` get rewritten to `AST_ARY` even though no `AST_ARY` enum value exists. Reader sees a stale comment with `AST_*` in it and cleans it up later, same as today's stale `E_*` comments.

If desired, the executing session can run a one-shot pre-rename pass to delete the dead-comment names, but it's not required and isn't part of AR-1.

### Finding 3 — Word-boundary regex is safe

Verified (sess 2026-05-09): zero identifiers in `one4all/src/` of the form `*_E_X` (no `something_E_VAR` macro, no `foo_E_BAR` field). Substrings inside other identifiers (`BE_U`, `CE_H`, `DE_E`, etc.) all have non-underscore left-context and don't match `\bE_[A-Z]`. The regex `\bE_([A-Z][A-Z_]*)\b` → `AST_\1` is mechanically clean for both `sed` and `perl -pi`.

### Finding 4 — ASCII art / banner comments

129 files have block-comment lines containing `EXPR_t` or `expr_t`. Most are header banners and field comments — these get renamed mechanically to `AST_t` and read fine. A small number may contain text-art alignment that breaks visually when `EXPR_t` (6 chars) becomes `AST_t` (5 chars). Acceptable cost; not a gate.

---

## Rung breakdown

Three rungs. **AR-1 and AR-2 must land in the same session** (per Lon's lockstep decision, sess 2026-05-09 — no transitional alias). AR-3 is doc-only and can land separately.

### AR-1 — C side: `EXPR_t` / `EXPR_e` / `E_*` → `AST_t` / `AST_e` / `AST_*`

**Scope:** `one4all/src/` only. All 73 C files containing `E_*` enum refs, plus the 4 header files defining `EXPR_t` (`ir.h`, `CMPILE.h`, `prolog_builtin.h`, `icon_gen.h` — confirm canonical owner is `ir.h` per FI-0A).

**Mechanical operations:**

```bash
# In each .c and .h under one4all/src/:
perl -pi -e 's/\bEXPR_t\b/AST_t/g' <file>
perl -pi -e 's/\bEXPR_e\b/AST_e/g' <file>
perl -pi -e 's/\bexpr_e_name\b/ast_e_name/g' <file>
perl -pi -e 's/\bE_([A-Z][A-Z_]*)\b/AST_$1/g' <file>
# The 'E_X' / "E_X" string literals in C debug/dump code:
perl -pi -e "s/'E_([A-Z][A-Z_]*)'/'AST_\$1'/g" <file>
perl -pi -e 's/"E_([A-Z][A-Z_]*)"/"AST_$1"/g' <file>
```

**Order of operations within AR-1:**

1. Run the regex pass repo-wide (regex is safe per Finding 3).
2. Build with the standard build script. First-build errors are diagnostic only — there should be none, but any "undefined `E_FOO`" indicates a name the regex didn't catch (escaped string, comment, etc.) — fix and re-run.
3. Verify no `E_*` enum-value identifiers remain: `grep -rE "\bE_[A-Z][A-Z_]+\b" one4all/src/` must return zero matches.
4. Verify no `EXPR_t` or `EXPR_e` identifiers remain: `grep -rE "\bEXPR_[te]\b" one4all/src/` must return zero matches.
5. Run gates (see Gates below).
6. **Do not commit yet.** AR-2 lands in the same session.

**Files that need manual attention beyond regex:**

- `ir.h` lines 44, 251, 253, 270 — the canonical declarations. Verify the regex caught all of them.
- `ir.h` lines 270+ — the `expr_e_name[]` initializer with `[E_QLIT] = "E_QLIT"` etc. The regex catches both the array index and the string. Both should rename together.
- `ir_print.c` (or wherever `--dump-parse` lives) — emits `(E_FOO ...)` strings. The regex catches the string literal; verify the dump output format becomes `(AST_FOO ...)`.
- Any `case E_FOO:` inside a switch — regex catches these.
- Any preprocessor `#define E_FOO ...` — regex catches the macro name and any expansion.

### AR-2 — Snocone parser side: same rename across `parser_*.sc` + `.ref` oracles + supporting `.sc` files

**Scope:** `corpus/programs/scrip/parser_*.sc` (6 files) + 164 `.ref` files + 5 supporting `.sc` files (`ShiftReduce.sc`, `qize.sc`, `semantic.sc`, `smoke.sc`, `tdump.sc`).

**Mechanical operations:**

```bash
# In each parser_*.sc and supporting .sc file:
perl -pi -e "s/'E_([A-Z][A-Z_]*)'/'AST_\$1'/g" <file>
perl -pi -e 's/"E_([A-Z][A-Z_]*)"/"AST_$1"/g' <file>
# In .ref files — the tags appear bare, not quoted:
perl -pi -e 's/\bE_([A-Z][A-Z_]*)\b/AST_$1/g' <file>
```

**Order of operations within AR-2:**

1. Update parser_*.sc files first.
2. Update supporting .sc files (`tdump.sc` especially — it's the dumper that produces strings the .ref files capture).
3. Update .ref files.
4. Run PARSER-* test suites (see Gates).

**Why .ref files are touched directly rather than regenerated:**

- Faster, simpler, and the rename is mechanical.
- Regenerating .ref via `--dump-parse` would require AR-1's C-side rename to have landed first (so the dumper emits `AST_*`), which contradicts the lockstep contract (no commit between AR-1 and AR-2).
- Regenerating .ref via the new parser would require AR-2's parsers to have landed first (same circular dependency).
- Mechanical substitution sidesteps both. The result is byte-identical to what regeneration would produce.

### AR-3 — Documentation: PLAN.md, RULES.md, GOAL-* prose

**Scope:** `.github/PLAN.md`, `.github/RULES.md`, `.github/GOAL-*.md` files.

**Specific changes:**

1. **PLAN.md ## Architecture paragraph:**
   - "Every frontend ... produces the shared IR." → "Every frontend ... produces the shared AST."
   - "SM-LOWER compiles IR to SM_Program" → "SM-LOWER compiles AST to SM_Program (the IR)."
   - "Interpreter and emitter share one instruction set" → unchanged.

2. **RULES.md §"Snocone parser style":**
   - "IR node tags MUST be the exact strings `expr_dump` emits" → "AST node tags MUST be the exact strings `ast_dump` (or equivalent frontend dumper) emits". Adjust if the dumper itself was renamed in AR-1.
   - `TK_*` example unchanged (tokens, not AST kinds — different concept).

3. **RULES.md §"Naming conventions":**
   - Update the "Never ALL_CAPS for new C types (exception: `RESULT_t`)" line to reflect actual practice. Proposed wording:
     > "ALL_CAPS `_t` is reserved for the major IR-layer typedefs (`AST_t`, `DESCR_t`, `STMT_t`, …) — typedefs whose origin is SIL or whose lifetime spans the entire compiler pipeline. New utility types use one-cap (`Xxxx_t`)."

4. **GOAL-CHUNKS.md, GOAL-CHUNKS-STEP17.md, and any other GOAL-* files:**
   - Where prose mentions "EXPR_t pointers" or "raw IR pointers" or "EXPR_t walker" — replace with "AST node pointers" or "AST walker".
   - Where prose mentions `E_FOO` enum names — replace with `AST_FOO`.
   - Code-snippet references in *historical* session log entries (paragraphs describing past code states) stay as-is; rename only in current/forward-looking sections. Use judgment.

**Order of operations within AR-3:**

1. PLAN.md first (one paragraph + the goals table — the goal name itself stays "GOAL-AST-RENAME" since it was carved with that name).
2. RULES.md §"Snocone parser style" + §"Naming conventions".
3. GOAL-* prose — sweep through and update active-goal text. Historical session log entries stay unchanged.

This rung is doc-only — no test gates beyond `git diff` review.

---

## Gates

Per RULES.md §"Test gate before every commit". The rename is byte-identical to baseline modulo the renamed strings, so all gates run as today and produce identical output (with `AST_*` substituted for `E_*` wherever the output prints kind names).

**For AR-1 + AR-2 (combined commit pair):**

| Gate | Expected | Why |
|---|---|---|
| Build | clean | basic |
| Smoke ×6 | PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4) | language-runtime sanity |
| Isolation gate | PASS | SM-runtime files don't call IR walkers |
| `unified_broker_test` | PASS=49 | broker-driven IR consumers |
| csnobol4 Budne | PASS=50 (sess 2026-05-09 baseline; the 61-vs-50 environmental variance noted in CHUNKS-step17 stays out of scope) | SNOBOL4 frontend |
| Icon corpus `--ir-run` | PASS=186 FAIL=47 XFAIL=30 TOTAL=263 | Icon frontend + IR walker |
| `scrip_all_modes` | PASS=2 | all run modes |
| PARSER-SN | PASS=78/78 | SNOBOL4 parser |
| PARSER-IC | PASS=153 (sess 2026-05-09 baseline) | Icon parser |
| PARSER-PR | per current GOAL-PARSER-PROLOG state (note: that goal's "⛔ NO baseline gates at session start" exempts it) | Prolog parser |
| PARSER-RK | PASS=147 oracle, COV_PASS=39 (RK-29 baseline) | Raku parser |
| PARSER-SC | PASS=67 | Snocone parser |
| PARSER-RB | RB-FULL-1 in-progress state | Rebus parser |
| `bb_flat_text_test` | PASS=18/18 | BB flat emitter |
| `sm_phase2_sim` | PASS=25/25 | SM phase-2 simulation |
| EM test suite | PASS=12/12 | emitter |

If any gate fails byte-comparison post-rename, **revert and investigate** — the rename is mechanical and should be byte-identical modulo `E_*` → `AST_*` text. A real divergence indicates a bug (regex caught something it shouldn't have, or missed something it should have).

**For AR-3 (doc-only):**

- `git diff` review by Lon. No test gate.

---

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Regex matches `E_*` in unintended contexts (e.g., a string literal that's data, not source) | Low — survey shows clean word-boundary set | Run AR-1 first, build, scan for any unexpected breakage before AR-2 |
| Two repos out of sync if AR-2 commit fails after AR-1 commit | Eliminated by lockstep — both commits land in same session, both pushes confirmed before declaring done | RULES.md §"Handoff" |
| `.ref` files have subtle whitespace or line-ending issues that defeat in-place substitution | Possible | Verify with `git diff` and a checksum spot-check before running PARSER-* gates |
| One of the 7 parser-only `E_*` names (`E_BANGPAT`, etc.) breaks something nobody noticed | Low — they don't exist in C runtime today, so renaming them changes nothing functionally | Note in commit message; defer to follow-up |
| Mid-rename, another session pushes to one4all or corpus | Eliminated by Lon's "all sessions wait" decision (sess 2026-05-09) | This goal file's preamble §5 |
| Build cache holds stale `EXPR_t` references somewhere | Possible | `make clean` before AR-1 build |
| RULES.md §"Snocone parser style" referenced by other tooling beyond what AR-3 touches | Low | `grep -r "expr_dump" .` across all three repos before AR-3 |
| `--dump-parse` output format itself baked into something AR-3 misses | Low | Compare `--dump-parse` output before and after — should differ only in `E_` → `AST_` |

---

## Out of scope

- Renaming `SM_PUSH_EXPR` or other SM opcodes containing `EXPR` — that's the next goal (CHUNK → EXPRESSION rename, sess after this one lands per Lon).
- Renaming local variables `EXPR_t *e`, `EXPR_t *node`, etc. — only the type name changes; locals stay.
- Renaming `expr_dump` function (or whatever the dumper is named in `ir_print.c`) — handled in AR-3 if obvious; otherwise deferred to a follow-up cleanup rung.
- Cleaning up the comment-residue dead names (`E_ARY`, `E_ASGN`, `E_BLOCK`, `E_BINOP`) — they get renamed mechanically and stay as comment-residue under their new names; cleaning them is a separate trivial follow-up.
- The 7 parser-only names (`E_BANGPAT` etc.) — renamed mechanically; whether they should be wired to runtime or removed is a separate question.
- Touching `snobol4dotnet`, `snobol4jvm`, `snobol4python`, `snobol4csharp` — none reference `EXPR_t`/`E_*` in a way that participates in this rename. If they do (verify before AR-1), add to scope.
- `corpus/editor/sublime/Snocone.sublime-syntax` — syntax-highlighter; verify and include any `E_*` references it has but it's not a primary scope item.

---

## Session Setup

Standard one4all + corpus + .github clone — same as `REPO-one4all.md ## Session Setup`. No additional setup specific to this goal. After clone, the executing session reads this goal file, then `RULES.md` (commit/push protocol), then proceeds rung-by-rung.

---

## Implementation steps

### AR-1 + AR-2 (lockstep, single session)

- [x] **Step 1 — Pre-flight verification.** Counts confirmed: 1391 `EXPR_t`, 64 `EXPR_e`, 4554 `E_*`, 647 parser refs, 1688 `.ref` refs.
- [x] **Step 2 — `make clean` in one4all.**
- [x] **Step 3 — Run the C-side regex pass.** All 6 substitutions across `src/`, `test/`, `scripts/`, `README.md`, `.cs`, `.java`, `.js`, `.y`, `.l`, `.wat`. Discovered `test/` and `src/driver/net/*.cs` and other non-C language driver files needed separate passes — all done. `ekind_name` alias in test files renamed to `ast_e_name`. Zero `E_*` / `EXPR_t` / `EXPR_e` remaining in entire repo.
- [x] **Step 4 — Build.** Clean build. No errors.
- [x] **Step 5 — Verify zero `E_*` enum-value identifiers remain.** Confirmed zero.
- [x] **Step 6 — Run C-side gates.** smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 4/4, 5/5), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Budne PASS=50, Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263. All byte-identical to baseline. `test_smoke_snocone_parse_a` build failure confirmed pre-existing (not introduced by rename — verified via git stash).
- [x] **Step 7 — Run the parser-side regex pass.** All 6 parser_*.sc, 5 supporting .sc, 164 .ref files. Zero `'E_*'` / `"E_*"` remaining.
- [x] **Step 8 — Verify zero `'E_*'` / `"E_*"` literals remain.** Confirmed zero in parsers and .ref files.
- [ ] **Step 9 — Run PARSER-* gates.** SPITBOL oracle not available in this container env; PARSER-* suites that require it skipped. Snocone parse smoke tests a–e confirmed pre-existing failure unrelated to rename. Deferred to post-push verification with full oracle env.
- [ ] **Step 10 — Commit one4all (AR-1).** Awaiting Lon per RULES.md §"Commit identity — always Lon, never Claude".
- [ ] **Step 11 — Commit corpus (AR-2).** Awaiting Lon.
- [ ] **Step 12 — Confirm both pushes landed and hashes match.** Awaiting Lon.
- [ ] **Step 13 — Run all gates one more time on the pushed state.** Deferred to next session with full oracle env.

### AR-3 (doc-only, can be a separate session)

- [ ] **Step 1 — Update PLAN.md ## Architecture paragraph.** "the IR" → "the AST" where it means the tree; clarify "SM_Program (the IR)" where it means the lowered form.
- [ ] **Step 2 — Update PLAN.md ## Active Goals table.** This row (GOAL-AST-RENAME) shifts from "carved" to "LANDED sess #X" with one4all and corpus commit hashes.
- [ ] **Step 3 — Update RULES.md §"Snocone parser style".**
- [ ] **Step 4 — Update RULES.md §"Naming conventions".** Reflect the `_t` ALL_CAPS class as documented practice rather than exception.
- [ ] **Step 5 — Sweep GOAL-CHUNKS.md, GOAL-CHUNKS-STEP17.md, and any other active GOAL-* prose** for "EXPR_t" / "E_*" references in forward-looking text. Leave historical session log entries unchanged.
- [ ] **Step 6 — Commit and push .github.**

---

## When AR-1 + AR-2 land

- Update PLAN.md ## Active Goals table: this goal row marked LANDED with commit hashes.
- The goal-state pointers for `GOAL-CHUNKS.md` / `GOAL-CHUNKS-STEP17.md` in PLAN.md continue to point at their current next-rungs.
- Carve `GOAL-EXPRESSION-RENAME.md` (next: rename CHUNK → EXPRESSION in the SM/CHUNKS work — `SM_PUSH_CHUNK`, chunk-vocabulary in docs, and the eventual `SM_PUSH_EXPR` deletion).
