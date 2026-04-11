# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

---

## ⛔ SESSION START — every session, no exceptions

1. Read this file top to bottom.
2. Find your active Goal in the table below.
3. Open that Goal file. Find the first incomplete Step (`- [ ]`). Do it.
4. If you need invariants, tool paths, or don't-do-X warnings: read the REPO file (see Repos below).

That is your entire orientation. Do not read archive/ unless a step explicitly says to.

---

## Active Goals

| Goal | File | Repo | Current Step | Done? |
|------|------|------|--------------|-------|
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | watermark 6749 → next: DMPK1 | ☐ |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | watermark 6438 → next: COLECT | ☐ |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 (infrastructure) | ☐ |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-1 (set_and_trace) | ☐ |
| NET Beauty 19/19 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-1 (FENCE redef) | ☐ |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-1 (diagnose error 021) | ☐ |
| NET Snippets | `GOAL-NET-SNIPPETS.md` | snobol4dotnet | S-1 (@N fix) | ☐ |
| NET Optimize | `GOAL-NET-OPTIMIZE.md` | snobol4dotnet | S-1 (ExecutionCache) | ☐ |

---

## Repos

| Repo | File | Clone path |
|------|------|------------|
| one4all | `REPO-one4all.md` | `/home/claude/one4all` |
| snobol4dotnet | `REPO-snobol4dotnet.md` | `/home/claude/snobol4dotnet` |
| snobol4jvm | `REPO-snobol4jvm.md` | `/home/claude/snobol4jvm` |
| snobol4python | `REPO-snobol4python.md` | `/home/claude/snobol4python` |
| snobol4csharp | `REPO-snobol4csharp.md` | `/home/claude/snobol4csharp` |
| corpus | `REPO-corpus.md` | `/home/claude/corpus` |
| harness | `REPO-harness.md` | `/home/claude/harness` |

---

## Rules

- Commit as `LCherryholmes` / `lcherryh@yahoo.com`. Never as Claude.
- Never write the token to disk or in any commit.
- Rebase before every `.github` push: `git pull --rebase origin main && git push`
- A Goal is done or not done. No other status.

---

## Architecture (one paragraph)

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR.
SM-LOWER compiles IR to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks SM_Program and emits native code
(x86, JVM, .NET, JS, WASM). Interpreter and emitter share one instruction set.

---

*archive/ holds all prior HQ docs. Full git history is the permanent record.*
