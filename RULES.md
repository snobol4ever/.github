# RULES.md — Mandatory Rules (L3)

Every rule exists because a violation caused real damage. Read section headers first (`grep "^## " RULES.md`), then only sections relevant to your session.

---

## ⛔ SIX THINGS — Run SESSION_BOOTSTRAP.sh first, every session, no exceptions

```bash
# At session start — provide the GitHub token Lon gave you:
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

`SESSION_BOOTSTRAP.sh` does all six things automatically:

| # | Thing | What it does |
|---|-------|-------------|
| 1 | **WHO** | Sets `git config user.name/email` to LCherryholmes — every commit, every repo |
| 2 | **WHAT** | Prints project summary: 6 frontends × 4 backends, current reorg phase, ref docs |
| 3 | **WHERE (repos)** | Clones or pulls: `.github` · `snobol4x` · `corpus` · `harness` |
| 4 | **WHERE (tools)** | Installs `nasm` · `mono-complete` · `java` · confirms `jasmin.jar` · builds `sno2c` |
| 5 | **WHY** | Prints current milestone from PLAN.md and the four docs to read before coding |
| 6 | **HOW** | Runs all three invariants: `x86 106/106 · JVM 106/106 · .NET 110/110` |

Script location: `/home/claude/.github/SESSION_BOOTSTRAP.sh`
Never say a tool is unavailable. The script installs everything. You have a network connection.

After the script passes, read (in order):
```
tail -80 /home/claude/.github/SESSIONS_ARCHIVE.md   # your handoff
cat /home/claude/.github/RULES.md                   # this file
cat /home/claude/.github/PLAN.md                    # NOW table + next milestone
cat /home/claude/.github/GRAND_MASTER_REORG.md      # phase detail
```


## ⛔ TOKEN — Never write or display the token

Token is provided once by Lon at session start. Use in shell only. Never on disk, never in chat, never in commit messages, never in handoff summaries. Write `TOKEN_SEE_LON` as placeholder in any file that references it. If token appears in a commit: notify Lon immediately — rotation and history rewriting are Lon's decisions only.

**Bootstrap blocks in SESSIONS_ARCHIVE.md and all other HQ docs must use `TOKEN_SEE_LON` as the placeholder — never the real token. This applies to every `git clone https://...@github.com/...` line without exception. GitHub Push Protection will block the push and force a rewrite if a real PAT is committed.**

---

## ⛔ SESSION NUMBERS — Globally unique per session type

Format: `PREFIX-NNN` where NNN increments within that namespace only.

| Session type | Prefix | Owns in PLAN.md NOW |
|---|---|---|
| Grand Master Reorg | `G` | **GRAND MASTER REORG** row |
| TINY backend (ASM) | `B` | **TINY backend** row |
| TINY JVM backend | `J` | **TINY JVM** row |
| TINY NET backend | `N` | **TINY NET** row |
| TINY frontend | `F` | **TINY frontend** row |
| DOTNET | `D` | **DOTNET** row |
| README | `R` | **README** row |
| ICON frontend | `I` | **ICON frontend** row |
| Prolog JVM | `PJ` | **Prolog JVM** row |
| Icon JVM | `IJ` | **Icon JVM** row |
| Scrip Demo | `SD` | **Scrip Demo** row |

Each session increments only its own counter. Commit messages: `PJ-5: M-PJ-BACKTRACK — fix suffix_fail`.

**⚠ ICON vs IJ DISAMBIGUATION — common source of error:**
- `"ICON frontend"` alone = I-session (x86 backend, `icon_emit.c`)
- `"ICON frontend with JVM backend"` = IJ-session (`icon_emit_jvm.c`, Jasmin)
- `"Icon JVM"` = IJ-session
- The phrase "JVM backend" is the deciding signal. When in doubt: check which emitter file is active. `icon_emit.c` → I. `icon_emit_jvm.c` → IJ.
- **HQ MD files are the only reliable memory.** Always read the relevant SESSION doc (`SESSION-icon-x64.md` vs `SESSION-icon-jvm.md`) to confirm session type before doing any work.

---

## ⛔ CONCURRENT SESSIONS — Rebase before every .github push

Four sessions may push `.github` simultaneously. Always:
```bash
cd /home/claude/.github
git pull --rebase origin main   # immediately before push
git push
```
Each session edits only its own row in PLAN.md NOW and its own L3 docs. **Never `git push --force` on .github.**

---

## ⛔ HANDOFF — Push must succeed before handoff is declared

A committed-but-not-pushed session lives only on a throwaway container — it is a lost session. Never say "handoff complete" until `git log origin/main --oneline -1` shows your commit hash on the remote. If push fails for any reason: fix it. Ask for credentials if needed. Do not declare done and move on.

End-of-session checklist (in order):
1. Update platform MD (TINY.md / ARCH-prolog-jvm.md / etc.) — HEAD, sprint status, §NOW next action.
2. Update PLAN.md NOW table row (your row only).
3. If milestone fired: move its row to MILESTONE_ARCHIVE.md.
4. `git add -A && git commit && git push` every touched repo.
5. `git pull --rebase origin main` on .github, then commit + push .github last.
6. Append session entry to SESSIONS_ARCHIVE.md.

---

## ⛔ ARTIFACT REFRESH — After every milestone fix, regenerate affected artifacts

Any time a frontend emitter or backend is modified, all artifacts for that frontend/backend combination must be regenerated and committed before handoff. Stale artifacts are worse than no artifacts.

**Trigger:** You touched `icon_emit_jvm.c` → regenerate `artifacts/icon/samples/*.j` and `artifacts/jvm/samples/*.j` for all passing demos. You touched `prolog_emit_jvm.c` → regenerate `artifacts/prolog/samples/*.j`. You touched `emit_byrd_jvm.c` → regenerate `artifacts/jvm/samples/*.j`. And so on.

**Rule:** If an artifact `.j` file would now produce different output than the committed version, regenerate it. If it now passes when it previously failed, promote it from source-only to source+`.j`. If it now fails, mark it with a comment and open a bug.

**Regen commands live in `artifacts/README.md`** — one block per frontend/backend. Run the relevant block, verify outputs, commit.

**At every milestone fire:** run the full demo harness (`bash demo/scrip/run_demo.sh demo/scrip/demoN/`) for all demos that touch the affected system. If additional demos now pass, fire their milestones too.

---

## ⛔ GIT IDENTITY — Always commit as Lon, never as Claude

**Every commit in every repo must be authored as Lon Cherryholmes.**
Claude is a tool, not an author. Never commit as `claude@anywhere.com`.

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

Set this in every repo at session start, before the first commit. This is not optional.
Violations require a history rewrite (`git filter-repo`) and force-push — expensive to fix.

**Wrong (never use):** `claude@anthropic.com`, `claude@snobol4ever.dev`, `SESSION@snobol4ever.dev`,
`session@snobol4ever`, `bot@snobol4ever.dev`, or any other Claude/session/bot address.

**Right:** `lcherryh@yahoo.com` / `LCherryholmes` — always, every repo, every session.

---

## ⛔ BYRD BOXES — mock_engine.c only, no interpreter

The Byrd-box four-port model (α/β/γ/ω) is emitted as labels + gotos — never as an interpreter loop. Any logic that "runs" IR nodes at emit-time is wrong. Emit code; don't execute it.

---

## ⛔ THREE-AXIS ORIENTATION — Repo × Frontend × Backend

Every session is defined by three values. Pick them, read three docs, work.

**1. Repo** → `REPO-snobol4x.md` / `REPO-snobol4jvm.md` / `REPO-snobol4dotnet.md`
**2. Frontend** → `FRONTEND-icon.md` / `FRONTEND-prolog.md` / `FRONTEND-snobol4.md` etc. (pure reference, no §NOW)
**3. Frontend × Backend** → `SESSION-icon-jvm.md` / `SESSION-prolog-x64.md` etc. (§NOW lives here)

**Deep reference** → `ARCH-*.md` — open only when you hit something unfamiliar. Full catalog in `ARCH-index.md`. Never read speculatively.

**Session start — four steps (mandatory, in order):**
1. `tail -80 SESSIONS_ARCHIVE.md` — your handoff. Do this FIRST.
2. Read `RULES.md` in full — 139 lines, mandatory before any file writes or commits.
3. Read `PLAN.md` — NOW table, confirm next milestone.
4. Read `REPO-*.md` + your `SESSION-*.md`. §NOW lives in the SESSION doc.

**§NOW and sprint state** live in SESSION-*.md only. Never in PLAN.md, RULES.md, or FRONTEND-*/BACKEND-* docs. SESSIONS_ARCHIVE.md is append-only.

---

## ⛔ NOW TABLE ROW FORMAT — Three fields only

Each row in PLAN.md NOW table: `| **Session name** | sprint-id — milestone-status | HEAD-hash session-id | Next milestone |`

No narrative beyond a short status phrase. No substeps. No bullet points. One row per session type, owned by that session exclusively.

---

## ⛔ REPO PATHS — Canonical clone locations

```
/home/claude/snobol4x/        ← compiler + backends (main working repo)
/home/claude/.github/         ← HQ docs
/home/claude/corpus/   ← test corpus (clone if needed)
/home/claude/snobol4jvm/      ← JVM/Clojure backend (clone if needed)
```
Always clone fresh at session start. Never use symlinks. First action is always clone.

---

## ⛔ TEST INVARIANT — Confirm before any work

**Required baseline — 3×3 matrix (7 active, 2 not-yet-implemented):**

| | x86 | JVM | .NET |
|--|-----|-----|------|
| SNOBOL4 | `106/106` | `106/106` | `110/110` |
| Icon | `38-rung` | `38-rung` | SKIP (not impl) |
| Prolog | `per-rung PASS` | `31/31` | SKIP (not impl) |

- **x86 SNOBOL4:** `run_crosscheck_asm_corpus.sh` must show 106/106.
- **JVM SNOBOL4:** `run_crosscheck_jvm_rung.sh` against full corpus must show 106/106.
- **.NET SNOBOL4:** `run_crosscheck_net.sh` must show 110/110 (requires `harness`).
- **Icon x64:** all 38 `test/frontend/icon/run_rung*.sh` must PASS.
- **Icon JVM:** all 38 `test/frontend/icon/run_rung*.sh` via JVM path must PASS.
- **Prolog x64:** all `test/frontend/prolog/corpus/rung*/` must PASS.
- **Prolog JVM:** `run_prolog_jvm_rung.sh` per rung must PASS (31/31 baseline).
- **Icon .NET / Prolog .NET:** not yet implemented — always SKIP.
- **All sessions:** confirm baseline before touching code. Fix regressions before new work.
- **Never report only one backend.** If a backend cannot be run, state the last known count and the reason.
- **G-sessions always run all seven active invariants** — the reorg touches all emitters.

**Backend name:** The native backend is **x86** (not "ASM" or "x64 ASM"). Emitter file stays `emit_x64.c`; folder stays `backend/x64/`; the human name is x86.

---

## ⛔ FRONTEND/BACKEND SEPARATION — Emitter gaps queue via .xfail

When the frontend produces an IR node the backend cannot yet emit, do not add a special-case silent skip. Add an `.xfail` entry so the gap is visible and tracked. Fix the emitter gap in a dedicated milestone.

---

*RULES.md = L3 reference. ~10 rules, each ≤10 lines. No session playbooks. No artifact status tables. No war stories beyond one-line root-cause citations.*

---

## ⛔ HQ DOCS ARE THE ONLY RELIABLE MEMORY — Verify before asserting

Before making any factual claim about how a component works — lexer behaviour,
semicolons, calling conventions, corpus format, file layout, build commands — check
the relevant HQ doc first. Do NOT reason from training data or session memory.
Training data is wrong. Session memory drifts. HQ docs are ground truth.

**Failure mode:** Claude asserted Icon/JCON uses implicit semicolons (standard Icon
behaviour). Our lexer explicitly does NOT — "No auto-semicolon insertion" is line 4
of `icon_lex.c` and documented in RULES.md and ARCH-icon-jcon.md. This caused
wasted session time diagnosing a non-problem.

**Rule:** When in doubt about ANY system property: `grep` the relevant HQ doc first.
If the doc doesn't cover it, check the source. Never guess and assert.

---



All Icon source in SCRIP demos must use explicit semicolons between statements.
The parser requires **no semicolon after `procedure name(args)`** — the header line
takes no terminator. First statement of the body follows on the next line.

Correct:
```icon
procedure main()
    x := 1;
    write(x);
end
```

Wrong (parse error):
```icon
procedure main();   ← ERROR
```

`icon_semicolon` is an end-user tool only — never run in the pipeline.
When adding semicolons by hand to a demo `.md` block, skip the procedure header line.

**IPL programs from corpus require explicit semicolons added before they
can be compiled by our frontend.** Standard Icon has implicit semicolons; our
lexer (`icon_lex.c` line 4: "No auto-semicolon insertion — deliberate deviation")
does NOT. The rung36 corpus is pre-converted. Raw IPL files are NOT directly usable.
Do NOT claim otherwise. Verified in `icon_lex.c`; documented in `ARCH-icon-jcon.md §Auto-semicolon`.

---

## ⛔ JVM BACKEND — Null = uninitialized; coerce before string ops

`sno_array_get` returns Java `null` for uninitialized slots.
In SNOBOL4 semantics, uninitialized = empty string `""`.

**Rule:** Any JVM emitter path that calls `sno_array_get` and then invokes a String
method (`.equals`, `.contains`, concatenation) on the result **must** emit a
null→`""` coerce inline first (dup / ifnonnull / pop / ldc "").

`sno_indr_get` (variable lookup) already coerces internally — no guard needed there.
`sno_array_get` does **not** — guard required at every call site that uses the
result as a non-null String.

Also: array subscript assignment with `:S`/`:F` goto — the value may be null
(failed sub-expression). Null-check the value before `sno_array_put`; null → skip
put and take `:F` / fall through. Violation root cause: SD-10 NPE on `IDENT(t<key>)`.
