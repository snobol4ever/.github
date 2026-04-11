# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

---

## ⛔ SESSION START — every session, no exceptions

1. Read this file top to bottom.
2. Find your active Goal in the table below.
3. Open that Goal file. Find the first incomplete Step. Do it.
4. If you need invariants, tool paths, or don't-do-X warnings for your repo: read the REPO file for that repo (see Repos section below).

That is your entire orientation. Do not read archive/ unless a step explicitly says to.

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

## Active Goals

| Goal | File | Repo | Current Step | Done? |
|------|------|------|--------------|-------|
| *(none yet — goals to be defined)* | — | — | — | — |

---

## Rules

- Commit as `LCherryholmes / lcherryh@yahoo.com`. Never as Claude.
- Never write the token to disk or commit it.
- Rebase before every `.github` push: `git pull --rebase origin main && git push`
- Append to `SESSIONS_ARCHIVE.md` (in archive/) at handoff. Never prune it.
- A Goal is done or not done. No other status.

---

## Architecture (one paragraph)

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR.
SM-LOWER compiles IR to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks the same SM_Program and emits
native code (x86, JVM, .NET, JS, WASM). Interpreter and emitter share one instruction set.

---

*archive/ holds all prior HQ docs. Content is extracted from there as needed to populate Goal and Repo files.*
