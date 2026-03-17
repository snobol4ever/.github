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

## ⛔ CONCURRENT SESSIONS — rebase before every .github push

Two chats may work simultaneously on different repos (e.g. snobol4x + snobol4dotnet).
Both will push .github. They WILL collide unless every chat does:

```bash
cd /home/claude/.github
git pull --rebase origin main   # always, immediately before push
git push
```

This is safe because each chat edits different files:
- TINY chat   → TINY.md + PLAN.md TINY milestone rows
- DOTNET chat → DOTNET.md + PLAN.md DOTNET milestone rows
- JVM chat    → JVM.md + PLAN.md JVM milestone rows

Line-level conflicts are structurally impossible given this discipline.
RULES.md and SESSIONS_ARCHIVE.md are append-only — rebase handles them.

**Never `git push --force` on .github. Ever.**

## ⛔ GIT IDENTITY — Every commit in every repo

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```
Run immediately after every clone, before any commit. No exceptions across all repos:
snobol4x, snobol4corpus, snobol4harness, snobol4jvm, snobol4dotnet, .github.

## ⛔ BYRD BOXES — mock_engine.c only, no interpreter

Every pattern in beauty_full_bin is a compiled Byrd box.
`mock_engine.c` is the only engine file linked. `engine.c` is fully superseded.
If a build links engine.c: stop and diagnose — something is wrong.

## ⛔ ASM ARTIFACTS — Place generated ASM in artifacts/asm/

Every `.s` file that fires a milestone or serves as a sprint oracle must be
archived in `snobol4x/artifacts/asm/` and recorded in `artifacts/README.md`.

```
artifacts/asm/null.s          — Sprint A0, M-ASM-HELLO ✅ session145
artifacts/asm/lit_hello.s     — Sprint A1, M-ASM-LIT   ✅ session146
artifacts/asm/pos0_rpos0.s    — Sprint A2, M-ASM-SEQ   (next)
artifacts/asm/cat_*.s         — Sprint A3
artifacts/asm/alt_*.s         — Sprint A4
```

Entry format in artifacts/README.md:
```
### artifacts/asm/FOO.s  (Sprint AX — M-ASM-BAR ✅)
- status: PASS — <what it does>
- milestone: M-ASM-BAR fires sessionN
- assemble: nasm -f elf64 FOO.s -o FOO.o && ld FOO.o -o FOO && ./FOO
- design: <key design notes — labels, .bss layout>
```

## ⛔ ARTIFACTS — Snapshot generated C every session

At end of every session that touches sno2c, emit*.c, or runtime/:
```bash
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
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

**Structural model:**
```
Goal → Milestone → Sprint → Step
```
- **Goals** live in PLAN.md (3 goals, stable)
- **Milestones** live in PLAN.md dashboard + platform L2 doc milestone map
- **Sprints** live in platform L2 docs (TINY.md / JVM.md / DOTNET.md) or MONITOR.md
- **Steps** live inside sprint definitions in those same L2/L3 docs

```
L1: PLAN.md        ← Goals · Milestone Dashboard · 4D Matrix · L2/L3 index
                     ~3KB max. NO sprint content. NO step content. Ever.
L2: TINY/JVM/DOTNET/CORPUS/HARNESS.md  ← HEAD, build commands, active sprint + steps, milestone map, pivot log
L3: ARCH/TESTING/MONITOR/RULES/SESSIONS_ARCHIVE/PATCHES/MISC.md  ← deep reference
```

When Lon says "update HQ": identify which level owns that content and update there.
PLAN.md changes only when: milestone status changes, NOW block changes, or 4D matrix cell flips.

## Session Lifecycle

**Start:**
1. Read PLAN.md — know what repo/sprint/HEAD/next-action without reading anything else.
2. **Read RULES.md** — mandatory every session. Token, identity, artifact, invariant, and chat rules apply immediately.
3. Read the active platform MD (TINY.md etc.) — get build commands and invariant.
4. `git log --oneline -3` — verify HEAD matches platform MD. If stale: read SESSIONS_ARCHIVE.md.
5. Run invariant check. If failing: fix before any other work.
6. **If sprint is `asm-backend`:** read `artifacts/asm/` to orient — last `.s` file is the prior milestone oracle.

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
