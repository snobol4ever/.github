# RULES.md — Mandatory Rules

Every rule exists because a violation caused real damage. Read section headers first (`grep "^## " RULES.md`), then only sections relevant to your session.

---

## ⛔ TOKEN — Never write or display the token

Token is provided once by Lon at session start. Use in shell only. Never on disk, never in chat, never in commit messages, never in handoff summaries. Write `TOKEN_SEE_LON` as placeholder in any file that references it. If token appears in a commit: notify Lon immediately — rotation and history rewriting are Lon's decisions only.

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
- `"ICON frontend"` alone = I-session (x64 ASM backend, `icon_emit.c`)
- `"ICON frontend with JVM backend"` = IJ-session (`icon_emit_jvm.c`, Jasmin)
- `"Icon JVM"` = IJ-session
- The phrase "JVM backend" is the deciding signal. When in doubt: check which emitter file is active. `icon_emit.c` → I. `icon_emit_jvm.c` → IJ.
- **HQ MD files are the only reliable memory.** Always read the relevant doc (FRONTEND-ICON.md vs FRONTEND-ICON-JVM.md) to confirm session type before doing any work.

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
1. Update platform MD (TINY.md / FRONTEND-PROLOG-JVM.md / etc.) — HEAD, sprint status, §NOW next action.
2. Update PLAN.md NOW table row (your row only).
3. If milestone fired: move its row to MILESTONE_ARCHIVE.md.
4. `git add -A && git commit && git push` every touched repo.
5. `git pull --rebase origin main` on .github, then commit + push .github last.
6. Append session entry to SESSIONS_ARCHIVE.md.

---

## ⛔ GIT IDENTITY — Set before first commit

```bash
git config user.email "SESSION_PREFIX@snobol4ever.dev"
git config user.name "Claude SESSION_ID"
```
Do this in every repo at session start. Commits without identity fail.

---

## ⛔ BYRD BOXES — mock_engine.c only, no interpreter

The Byrd-box four-port model (α/β/γ/ω) is emitted as labels + gotos — never as an interpreter loop. Any logic that "runs" IR nodes at emit-time is wrong. Emit code; don't execute it.

---

## ⛔ THREE-AXIS ORIENTATION — Repo × Frontend × Backend

Every session is defined by three values. Pick them, read three docs, work.

**Axis 1 — Repo** (build, paths, invariants):

| Repo | Doc |
|------|-----|
| snobol4x | `REPO-snobol4x.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |

**Axis 2 — Frontend** (language, parser, AST):

| Frontend | Doc |
|----------|-----|
| SNOBOL4 | `FRONTEND-SNOBOL4.md` |
| Icon | `FRONTEND-ICON.md` |
| Prolog | `FRONTEND-PROLOG.md` |
| Snocone | `FRONTEND-SNOCONE.md` |
| Rebus | `FRONTEND-REBUS.md` |

**Axis 3 — Frontend × Backend → SESSION doc** (§NOW sprint state lives here):

| | x64 ASM | JVM | .NET |
|--|:-------:|:---:|:----:|
| SNOBOL4 | `SESSION-snobol4-x64.md` | `SESSION-snobol4-jvm.md` | `SESSION-snobol4-net.md` |
| Icon | `SESSION-icon-x64.md` | `SESSION-icon-jvm.md` | — |
| Prolog | `SESSION-prolog-x64.md` | `SESSION-prolog-jvm.md` | — |

**Special sessions**: `SCRIP_DEMOS.md` (SD) · `BEAUTY.md` (beauty sprint)
**Pure backend ref** (no session state): `BACKEND-X64.md` · `BACKEND-JVM.md` · `BACKEND-NET.md`
**Deep reference**: `ARCH-*.md` — open only when you hit something you don't understand.

**Session start — three steps:**
1. `tail -80 SESSIONS_ARCHIVE.md` — your handoff. Do this FIRST.
2. Read `PLAN.md` — NOW table, confirm next milestone.
3. Read `REPO-*.md` + your `SESSION-*.md`. §NOW lives in the SESSION doc.

---

## ⛔ NOW TABLE ROW FORMAT — Three fields only

Each row in PLAN.md NOW table: `| **Session name** | sprint-id — milestone-status | HEAD-hash session-id | Next milestone |`

No narrative beyond a short status phrase. No substeps. No bullet points. One row per session type, owned by that session exclusively.

---

## ⛔ REPO PATHS — Canonical clone locations

```
/home/claude/snobol4x/        ← compiler + backends (main working repo)
/home/claude/.github/         ← HQ docs
/home/claude/snobol4corpus/   ← test corpus (clone if needed)
/home/claude/snobol4jvm/      ← JVM/Clojure backend (clone if needed)
```
Always clone fresh at session start. Never use symlinks. First action is always clone.

---

## ⛔ TEST INVARIANT — Confirm before any work

- **TINY/ASM sessions:** `run_crosscheck_asm_corpus.sh` must show 106/106 before any work begins. Fix regressions before starting new work.
- **All sessions:** run the relevant rung/corpus check for your frontend+backend and confirm baseline before touching code.

---

## ⛔ FRONTEND/BACKEND SEPARATION — Emitter gaps queue via .xfail

When the frontend produces an IR node the backend cannot yet emit, do not add a special-case silent skip. Add an `.xfail` entry so the gap is visible and tracked. Fix the emitter gap in a dedicated milestone.

---

## ⛔ SCRIP DEMO PROGRAMS ARE THE SPEC — Never rewrite to cover compiler limits

The `.md` source blocks in `demo/scrip/demoN/` are the specification. They define what the compilers must handle. If a demo fails, the bug is in the compiler (sno2c, icon_driver, JVM emitter, Prolog emitter) — never in the demo source. Do not simplify, restructure, or otherwise modify a demo block to work around a compiler limitation. Fix the product.

---

*RULES.md = L3 reference. ~10 rules, each ≤10 lines. No session playbooks. No artifact status tables. No war stories beyond one-line root-cause citations.*
