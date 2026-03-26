# RULES.md — Mandatory Rules (L3)

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
- **HQ MD files are the only reliable memory.** Always read the relevant L3 doc (FRONTEND-ICON.md vs FRONTEND-ICON-JVM.md) to confirm session type before doing any work.

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

## ⛔ DOC HIERARCHY — Five levels, strict reading discipline

| Level | Files | Size limit | Read when |
|-------|-------|-----------|-----------|
| **L1** | `PLAN.md` | 3KB hard | Every session, always — NOW table + milestone IDs only |
| **L2** | `TINY.md`, `JVM.md`, `DOTNET.md` | 10KB | Your platform session — HEAD, build, §NOW sprint |
| **L3** | `RULES.md`, `ARCH.md` | 10KB | Every session — invariant, never changes session-to-session |
| **L4** | `FRONTEND-*.md`, `BACKEND-*.md`, `MONITOR.md`, `TESTING.md`, `BEAUTY.md`, `GRAND_MASTER_REORG.md`, `SCRIP_DEMO*.md`, `PATCHES.md` | No hard limit | **Your pipeline or topic only** — read the one(s) matching your session type, no others |
| **L5** | `SESSIONS_ARCHIVE.md`, `MILESTONE_ARCHIVE.md` | Unlimited | `tail -80 SESSIONS_ARCHIVE.md` = step 1 of session start. Full read: never. Append only. |

**The session start protocol:**
1. `tail -80 SESSIONS_ARCHIVE.md` — find your session type's last entry; this is the handoff. Do this FIRST, before anything else.
2. Read L1 (`PLAN.md`) — NOW table + your next milestone ID only
3. Read L3 (`RULES.md` + `ARCH.md`) — skip if familiar
4. Read your L2 doc — if your session type has one
5. Read your L4 doc — the ONE file matching your frontend×backend or topic
6. Do not read any other L4 docs. Do not read GRAND_MASTER_REORG.md, TESTING.md, or MONITOR.md unless your milestone explicitly requires it.

**L4 owns all sprint content.** Session state, §NOW, §CRITICAL NEXT ACTION, step-by-step plans — all go in the L4 doc. Never in L1 or L3.

---



- **L1 PLAN.md:** 3KB max. NOW table + milestone IDs only. No sprint content, no step content, no completed rows. Ever.
- **L2 docs:** 10KB max. §NOW + §CRITICAL NEXT ACTION only.
- **L3 docs:** 10KB max. Invariant reference only — no session state, no step content.
- **L4 docs:** No hard limit. Replace sections; never append. Session summaries → L5 SESSIONS_ARCHIVE.md.
- When updating: **replace** the relevant section. Never append session summaries beyond §NOW.
- SESSIONS_ARCHIVE.md is append-only and has no size limit.

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

*RULES.md = L3 reference. ~10 rules, each ≤10 lines. No session playbooks. No artifact status tables. No war stories beyond one-line root-cause citations.*
