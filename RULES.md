# RULES.md — snobol4ever Working Rules

---

## Rules belong in RULES.md

⛔ Do **not** add rules to `PLAN.md`. Global rules live in `RULES.md` only.
`PLAN.md` is navigation and state. `RULES.md` is rules.

---

## No append-only huge files

⛔ Do **not** create or maintain append-only accumulating files (e.g. `SESSIONS_ARCHIVE.md`).
The git commit log is the permanent session record. HQ docs are state, not history.

---

## Commit identity — always Lon, never Claude

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

Set in every repo at session start. Every commit in every repo.

---

## Token — never on disk

Token is provided by Lon at session start. Use freely in shell commands.
Never write to any file. Never in commit messages. Never in HQ docs.
Use `TOKEN_SEE_LON` as placeholder in any doc that references a clone URL.

---

## Rebase before every .github push

```bash
cd /home/claude/.github
git pull --rebase origin main
git push
```

Multiple sessions may push .github simultaneously. Never `git push --force`.

---

## Handoff — push must succeed

⛔ Do **not** push any repo until "perform hand off" is called. Hold all commits locally.
One clean commit at handoff — this IS the session record. No piecemeal pushes.
**Exception:** unless Lon specifically directs resuming periodic pushes.

A committed-but-not-pushed session is lost when the container dies.
Never declare handoff complete until `git log origin/main --oneline -1` shows
your commit hash on the remote. Confirm both the code repo and .github.

Handoff checklist:
1. Update state variables in the Goal file (steps, watermarks, HEAD hash, pass counts)
2. Update Current Step in PLAN.md goals table
3. `git add -A && git commit` on all touched repos
4. `git pull --rebase && git push` — code repos first, .github last
5. Write a clear commit message on .github — this IS the session record

---

## Oracle — SPITBOL x64 is the primary oracle for all testing

```
/home/claude/x64/bin/sbl          # binary
/home/claude/x64/                 # repo (snobol4ever/x64)
```

Derive .ref output: `/home/claude/x64/bin/sbl -b file.sno > file.ref`
With includes: `/home/claude/x64/bin/sbl -I/home/claude/corpus/programs/snobol4/demo/inc file.sno`

SPITBOL is the **primary oracle for all goals and all testing** across the project.

**Narrow exception:** CSNOBOL4 is the oracle for Silly SNOBOL4 *sync-step monitoring only*
(SS-MONITOR / GOAL-SILLY-SYNC-MONITOR), because Silly is a C rewrite of CSNOBOL4's SIL
source and the monitor compares them live. This exception does NOT extend to sweep goals
or any other goal — use SPITBOL there.

DATATYPE note: SPITBOL returns lowercase (`"name"`, `"pattern"`).
one4all returns uppercase (`"NAME"`, `"PATTERN"`). This is intentional — SNOBOL4 spec.
`.ref` files are pre-baked in corpus. SPITBOL not required to run test gates.

---

## Test gate before every commit

Run the gate for your goal before committing. Do not commit broken builds.
The gate is defined in the Goal file or REPO file for your repo.

---

## Three-way diff for sweep goals

For GOAL-SILLY-SWEEP-FORWARD and GOAL-SILLY-SWEEP-BACKWARD:
All three sources simultaneously, one SIL instruction at a time:
1. `v311.sil` — the spec
2. `snobol4.c` — generated C ground truth (resolves all branch ambiguity)
3. `src/silly/sil_*.c` — our translation

Two-way (SIL + ours only) is wrong. All three, every line, no exceptions.

---

## Watermarks — Goal file is sole authority

Watermarks live only in their Goal file. SESSIONS_ARCHIVE, commit messages,
other docs — all potentially stale. The Goal file wins.

---

## HQ docs are the only reliable memory

Before asserting anything about how a component works — build commands,
calling conventions, oracle location, file layout — check the relevant
REPO or ARCH file first. Training data is wrong. Verify before asserting.

---

## CSNOBOL4 — never build the executable

⛔ Do **not** build the CSNOBOL4 executable (`./configure && make`).

---

## bison and flex — never install

`rebus.tab.c`, `rebus.tab.h`, and `lex.rebus.c` are committed and always current.
Never run apt-get to install bison or flex. If you modify `rebus.y` or `rebus.l`,
regenerate on your own machine and commit the C files.

---

## C code style — compact, 120-column, horizontal-first

- 120 character line maximum
- Brace on same line: `if (x) {`
- Short bodies on one line: `if (!p) return NULL;`
- Section dividers exactly 120 chars: `/*====...*/` major, `/*----...*/` minor

---

## Naming conventions (one4all C code)

| Origin | Convention | Example |
|--------|-----------|---------|
| SIL label → C function | `NAME_fn` | `APPLY_fn`, `FINDEX_fn` |
| SIL DESCR global → C typedef | verbatim + `_t` | `DESCR_t`, `SPEC_t` |
| SIL named global → C global | verbatim UPPERCASE | `XPTR`, `NEXFCL` |
| SIL EQU constant → C `#define` | verbatim UPPERCASE | `FBLKSZ`, `OBSIZ` |
| New C struct/enum (no SIL origin) | `Xxxx_yyy` one-cap | `Invoke_entry`, `Scan_ctx` |
| New C function (no SIL origin) | `snake_case` | `arena_init`, `genvar_from_descr` |
| Procedure return typedef | `RESULT_t` | always |

Never CamelCase. Never ALL_CAPS for new C types (exception: `RESULT_t`).

---

## Session trigger phrases

**"perform hand off"** — normal end of session:
1. Mark completed steps in Goal file (`- [x]`)
2. Update state variables (watermark, HEAD hash, pass counts, current step)
3. Update Current Step in PLAN.md goals table
4. `git add -A && git commit -m "clear description of what was done"` on all touched repos
5. `git pull --rebase && git push` — code repos first, .github last
6. Confirm: `git log origin/main --oneline -1` shows your hash on remote
7. Done — the commit message IS the session record

**"perform emergency hand off"** — same as above but:
- Note what is broken or incomplete at the top of the commit message
- Mark any incomplete step clearly in the Goal file (leave as `- [ ]`, add a note below it)
- Still push everything — a broken push is better than no push

**"here we go"** — session starting, Lon has named a goal, execute session start protocol from PLAN.md

**"grand master reorg"** — the goal is improving the HQ system itself
