# RULES.md — Mandatory Rules (L3)

Every rule here exists because a violation caused real damage.

---

## ⛔ TOKEN — Never write or display the token anywhere

The GitHub PAT was committed to a file on 2026-03-13. GitHub push protection
blocked the push. History had to be rewritten. **Never again.**
On 2026-03-16 the token was reconstructed and displayed in plain text in chat. Same exposure risk. **Never again.**
On 2026-03-18 the token was written repeatedly in chat handoff summaries. **Never again.**

- Token lives in Lon's memory only. Provided at session start. Used in shell only, never on disk.
- **Never reconstruct, quote, echo, or display the token in chat** — not even to confirm format. Acknowledge receipt silently and move on.
- **Never include a "Token: ..." line in handoff summaries, next-session start blocks, or any chat output.** Ever. For any reason.
- Write `TOKEN=TOKEN_SEE_LON` as placeholder in any file that references it.
- If token appears in a commit: notify Lon immediately. Token rotation and history rewriting are Lon's decisions only — Claude never rotates the token.

## ⛔ SESSION NUMBERS — globally unique, per-session-type prefix

Each concurrent session type has its own numbering namespace. No two sessions
ever share a number. Format: `PREFIX-NNN` where NNN increments within that
namespace only.

| Session type | Prefix | Example | Owns in PLAN.md NOW |
|---|---|---|---|
| TINY backend (ASM) | `B` | B-197, B-198 | **TINY backend** row |
| TINY JVM backend   | `J` | J-195, J-196 | **TINY JVM** row |
| TINY NET backend   | `N` | N-195, N-196 | **TINY NET** row |
| TINY frontend (SC) | `F` | F-192, F-193 | **TINY frontend** row |
| DOTNET             | `D` | D-156, D-157 | **DOTNET** row |

**Rules:**
- Commit messages: `B-198: M-ASM-R11 — data/ PASS`
- SESSIONS_ARCHIVE.md entries: `## Session B-198 — ...`
- HEAD fields in PLAN.md NOW table: `d832a86 B-198`
- Each session increments only its own counter — never touch another session's number
- The last known number per namespace lives in the NOW table HEAD column

**Migration:** pre-prefix sessions (1–196) are legacy. First session after this
rule uses the prefix. The PLAN.md NOW table HEAD column shows last known number
per namespace so the next session can find its starting point.

## ⛔ CONCURRENT SESSIONS — rebase before every .github push

Four chats may work simultaneously on snobol4x (backend, JVM, NET, frontend)
plus one on snobol4dotnet. All push .github. They WILL collide unless every
chat does:

```bash
cd /home/claude/.github
git pull --rebase origin main   # always, immediately before push
git push
```

Each chat edits only its own files and its own row in PLAN.md NOW:
- TINY backend   → TINY.md  + PLAN.md **TINY backend** row only
- TINY JVM       → JVM.md   + PLAN.md **TINY JVM** row only
- TINY NET       → BACKEND-NET.md + PLAN.md **TINY NET** row only
- TINY frontend  → FRONTEND-SNOCONE.md + PLAN.md **TINY frontend** row only
- DOTNET         → DOTNET.md + PLAN.md **DOTNET** row only

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

## ⛔ ARTIFACTS — Three canonical ASM samples tracked every session

Every session that changes `emit_byrd_asm.c`, `snobol4_asm.mac`, or any `.sno → .s` path MUST regenerate all three canonical ASM artifacts and check if they changed. **Update only if changed — do not commit unchanged files.**

```bash
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
ROMAN=/home/claude/snobol4corpus/benchmarks/roman.sno
WORDCOUNT=/home/claude/snobol4corpus/crosscheck/strings/wordcount.sno

src/sno2c/sno2c -asm -I$INC $BEAUTY   > /tmp/beauty_new.s
src/sno2c/sno2c -asm -I$INC $ROMAN    > /tmp/roman_new.s
src/sno2c/sno2c -asm -I$INC $WORDCOUNT > /tmp/wordcount_new.s

# Verify all three assemble with zero warnings/errors
nasm -f elf64 -I src/runtime/asm/ /tmp/beauty_new.s   -o /dev/null
nasm -f elf64 -I src/runtime/asm/ /tmp/roman_new.s    -o /dev/null
nasm -f elf64 -I src/runtime/asm/ /tmp/wordcount_new.s -o /dev/null

# Copy only if changed
diff -q /tmp/beauty_new.s   artifacts/asm/beauty_prog.s          || cp /tmp/beauty_new.s   artifacts/asm/beauty_prog.s
diff -q /tmp/roman_new.s    artifacts/asm/samples/roman.s        || cp /tmp/roman_new.s    artifacts/asm/samples/roman.s
diff -q /tmp/wordcount_new.s artifacts/asm/samples/wordcount.s   || cp /tmp/wordcount_new.s artifacts/asm/samples/wordcount.s

git add artifacts/asm/beauty_prog.s artifacts/asm/samples/roman.s artifacts/asm/samples/wordcount.s
git diff --cached --quiet || git commit -m "sessionN: artifacts — beauty/roman/wordcount updated"
```

**Never commit unchanged artifacts — git history is the archive, not noise.**



Git history is the archive. No numbered session copies (`foo_sessionN.ext`).
Overwrite the canonical file and commit. `git log -p` shows the evolution.

```
artifacts/
  asm/    — x64 NASM output (.s)       beauty_prog.s + fixture files
  c/      — C backend output (.c)       beauty_prog.c + trampoline fixtures
  jvm/    — JVM Jasmin text (.j)        hello_prog.j + samples/
  net/    — .NET CIL text (.il)         hello_prog.il + samples/
```

## ⛔ ARTIFACTS — NET canonical samples tracked every session

Every session that changes `net_emit.c` or any `.sno → .il` path MUST regenerate
the canonical NET artifacts and check if they changed. **Update only if changed.**

```bash
INC=/home/claude/snobol4corpus/programs/inc
NULL_SNO=/home/claude/snobol4x/test/crosscheck/null.sno      # simplest program

# After N-R1+ milestones fire, add beauty/roman/wordcount here too:
# BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
# ROMAN=/home/claude/snobol4corpus/benchmarks/roman.sno

cd /home/claude/snobol4x

# Generate
./sno2c -net $NULL_SNO > /tmp/null_new.il

# Verify assembles clean
ilasm /tmp/null_new.il /output:/tmp/null_new.exe 2>&1 | grep -E "error|Error" && echo FAIL || echo OK

# Copy only if changed
mkdir -p artifacts/net/samples
diff -q /tmp/null_new.il artifacts/net/hello_prog.il 2>/dev/null \
    || cp /tmp/null_new.il artifacts/net/hello_prog.il

git add artifacts/net/
git diff --cached --quiet || git commit -m "sessionN: artifacts/net — hello_prog.il updated"
```

**After N-R1 (OUTPUT='hello' works), extend to:**
```bash
./sno2c -net $BEAUTY  -I$INC > /tmp/beauty_new.il
./sno2c -net $ROMAN   -I$INC > /tmp/roman_new.il
# verify ilasm clean, copy if changed, commit
```

## ⛔ ARTIFACTS — JVM canonical samples tracked every session

Every session that changes `emit_byrd_jvm.c` or any `.sno → .j` path MUST regenerate
the canonical JVM artifacts and check if they changed. **Update only if changed.**

```bash
cd /home/claude/snobol4x
NULL_SNO=test/crosscheck/null.sno

./sno2c -jvm $NULL_SNO > /tmp/null_new.j

# Verify assembles (requires jasmin.jar — skip verify until J1)
mkdir -p artifacts/jvm/samples
diff -q /tmp/null_new.j artifacts/jvm/hello_prog.j 2>/dev/null \
    || cp /tmp/null_new.j artifacts/jvm/hello_prog.j

git add artifacts/jvm/
git diff --cached --quiet || git commit -m "sessionN: artifacts/jvm — hello_prog.j updated"
```

**Update beauty_prog.s (every session touching emit_byrd_asm.c or .mac):**
```bash
src/sno2c/sno2c -asm -I$INC $BEAUTY > artifacts/asm/beauty_prog.s
nasm -f elf64 -I src/runtime/asm/ artifacts/asm/beauty_prog.s -o /dev/null
git add artifacts/asm/beauty_prog.s && git commit -m "sessionN: artifacts — beauty_prog.s updated (reason)"
```

**Never create** `foo_sessionN.ext`. Overwrite `foo.ext` and commit.

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

## ⛔ MILESTONE ORDER — TINY.md sprint must match PLAN.md dashboard order

**The sprint in TINY.md NOW must always be the next ❌ milestone in PLAN.md's milestone dashboard, in sequence.**

- PLAN.md is the authoritative source of milestone order. Never skip ahead.
- When writing the "CRITICAL NEXT ACTION" block at the end of a session, look up the next ❌ in PLAN.md — do not invent or reorder.
- If TINY.md NOW and PLAN.md dashboard disagree: PLAN.md wins. Fix TINY.md.
- This rule exists because B-204 wrote M-ASM-BEAUTY as next sprint, skipping RUNG8/9/10/11 and LIBRARY and ENG685 entirely.

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

## ⛔ PUSH — Handoff is not complete until git push succeeds

**Never say "handoff complete", "session done", or any equivalent until `git push` output confirms success on every touched repo.**

A committed-but-not-pushed session lives only on a throwaway container. It is a lost session.

If the token has not been provided: say explicitly "I cannot push — please provide the token before this session closes." Do not declare the session done. Do not move on.

This rule has no exceptions.

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
4. `git add -A && git commit && git push` every touched repo (not .github yet).
5. `git pull --rebase origin main` on .github.
6. Append session entry to SESSIONS_ARCHIVE.md — what happened, state at handoff, next session start block.
7. `git add -A && git commit -m "sessionN: TINY.md + SESSIONS_ARCHIVE — <summary>" && git push` .github.

Steps 5–7 are automatic. No prompting needed. Claude does not wait to be asked.

**SNAPSHOT:** `git add -A && git commit -m "WIP: <what>" && git push` every touched repo.

**HANDOFF:** run SNAPSHOT, then update platform MD and PLAN.md, then append SESSIONS_ARCHIVE, then push .github.

**EMERGENCY:** `git add -A && git commit -m "EMERGENCY WIP: <state>"` every touched repo →
push all → one-line pivot log entry in platform MD.

**SWITCH REPO:** run HANDOFF on current repo first, then read the new platform MD.

## ⛔ FRONTEND/BACKEND SEPARATION — emitter gaps queue via .xfail

The frontend session (snocone) and backend session (ASM emitter) share the same repo
but must not edit each other's source directories:
- **Frontend session owns:** `src/frontend/snocone/` · `test/crosscheck/sc_corpus/` · `test/frontend/`
- **Backend session owns:** `src/backend/x64/emit_byrd_asm.c` · `src/runtime/asm/` · `test/crosscheck/crosscheck/`

**When the frontend hits an emitter gap** (a `.sc` test that fails because the ASM
backend doesn't handle the construct yet):

1. Commit the `.sc` + `.ref` as normal.
2. Add a `.xfail` file alongside with one line describing the root cause:
   ```
   echo "E_INDR left/right: sc_lower uses ->left, emitter expects ->right" \
       > test/crosscheck/sc_corpus/assign/014_assign_indirect_dollar.xfail
   ```
3. The `run_sc_corpus_rung.sh` runner treats `.xfail` as SKIP (not FAIL) and prints the reason.
4. File a milestone `M-SC-EMITTER-GAP-N` in PLAN.md pointing at the test and root cause.
5. **Frontend session does NOT touch** `src/backend/` — ever.

**Backend session** picks up `M-SC-EMITTER-GAP-N` on next recycle:
1. Fix the emitter.
2. Delete the `.xfail` file.
3. Confirm the test now PASS via `run_sc_corpus_rung.sh`.
4. Mark milestone ✅ in PLAN.md.

**Net effect:** frontend and backend sessions never conflict on source files.
The `.xfail` file is the contract between them.
