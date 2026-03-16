# RULES.md — Mandatory Rules (L3)

Every rule here exists because a violation caused real damage.

---

## ⛔ TOKEN — Never write or display the token anywhere

The GitHub PAT was committed to a file on 2026-03-13. GitHub push protection
blocked the push. History had to be rewritten. **Never again.**
On 2026-03-16 the token was reconstructed and displayed in plain text in chat. Same exposure risk. **Never again.**

- Token lives in Lon's memory only. Provided at session start. Used in shell only, never on disk.
- **Never reconstruct, quote, echo, or display the token in chat** — not even to confirm format. Acknowledge receipt silently and move on.
- Write `TOKEN=TOKEN_SEE_LON` as placeholder in any file that references it.
- If token appears in a commit: notify Lon immediately. Token rotation and history rewriting are Lon's decisions only — Claude never rotates the token.

## ⛔ GIT IDENTITY — Every commit in every repo

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
Run immediately after every clone, before any commit. No exceptions across all repos:
SNOBOL4-tiny, SNOBOL4-corpus, SNOBOL4-harness, SNOBOL4-jvm, SNOBOL4-dotnet, .github.

## ⛔ BYRD BOXES — mock_engine.c only, no interpreter

Every pattern in beauty_full_bin is a compiled Byrd box.
`mock_engine.c` is the only engine file linked. `engine.c` is fully superseded.
If a build links engine.c: stop and diagnose — something is wrong.

## ⛔ ARTIFACTS — Snapshot generated C every session

At end of every session that touches sno2c, emit*.c, or runtime/:
```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp_candidate.c
LAST=$(ls artifacts/beauty_tramp_session*.c 2>/dev/null | sort -V | tail -1)
# Compare md5:
md5sum $LAST /tmp/beauty_tramp_candidate.c
# If CHANGED: cp /tmp/beauty_tramp_candidate.c artifacts/beauty_tramp_sessionN.c
# If SAME: update artifacts/README.md with "no change" note only
```
artifacts/README.md must record: session N, date, md5, line count, compile status, active bug.

## ⛔ TEST INVARIANT — 106/106 rungs 1–11 before any work

```bash
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh
```
If not 106/106: fix the regression before touching anything else. Regressions are bugs.

## ⛔ HQ HIERARCHY — edit downstream files, not PLAN.md

```
L1: PLAN.md        ← index only, ~3KB max. Never add content here.
L2: TINY/JVM/DOTNET/CORPUS/HARNESS.md  ← platform state, sprints, build commands
L3: ARCH/TESTING/RULES/SESSIONS_ARCHIVE/PATCHES/MISC.md  ← deep reference
```
When Lon says "update HQ" or "update the plan": identify which L2 or L3 file owns
that content, and update that file. PLAN.md changes only when: milestone status changes,
active repo/sprint changes, or the platform map needs a new entry.

## Session Lifecycle

**Start:**
1. Read PLAN.md — know what repo/sprint/HEAD/next-action without reading anything else.
2. **Read RULES.md** — mandatory every session. Token, identity, artifact, invariant, and chat rules apply immediately.
3. Read the active platform MD (TINY.md etc.) — get build commands and invariant.
4. `git log --oneline -3` — verify HEAD matches platform MD. If stale: read SESSIONS_ARCHIVE.md.
5. Run invariant check. If failing: fix before any other work.

**End:**
1. Run artifact check (see ARTIFACTS rule above).
2. Update platform MD — HEAD, sprint status, next action, pivot log entry if anything shifted.
3. Update PLAN.md milestone dashboard if a milestone fired.
4. `git add -A && git commit && git push` every touched repo.
5. Push .github last.

**SNAPSHOT:** `git add -A && git commit -m "WIP: <what>" && git push` every touched repo.

**HANDOFF:** run SNAPSHOT, then update platform MD and PLAN.md, then push .github.

**EMERGENCY:** `git add -A && git commit -m "EMERGENCY WIP: <state>"` every touched repo →
push all → one-line pivot log entry in platform MD.

**SWITCH REPO:** run HANDOFF on current repo first, then read the new platform MD.
