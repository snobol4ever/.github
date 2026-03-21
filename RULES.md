# RULES.md — Mandatory Rules (L3)

Every rule here exists because a violation caused real damage.

---

## ⛔ TOKEN — Never write or display the token anywhere

The GitHub PAT was committed to a file on 2026-03-13. GitHub push protection
blocked the push. History had to be rewritten. **Never again.**
On 2026-03-16 the token was reconstructed and displayed in plain text in chat. Same exposure risk. **Never again.**
On 2026-03-18 the token was written repeatedly in chat handoff summaries. **Never again.**

- Token is provided once by Lon in the opening prompt of each session. Used in shell as needed throughout. Never on disk.
- **Never ask Lon for the token.** It was given at session start. If it wasn't, wait — do not prompt.
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

Every session that changes `emit_byrd_jvm.c` or any `.sno → .j` path MUST run:

```bash
bash /home/claude/snobol4x/test/crosscheck/jvm_artifact_check.sh
```

This script regenerates all three canonical JVM artifacts, verifies they assemble
clean, diffs against committed versions, copies and stages any that changed, then
exits nonzero if anything was updated (forcing you to include the artifacts in
your commit). It exits 0 only when all artifacts are already current.

**The script IS the rule. Run it. If it exits nonzero: add the staged files to
your commit before pushing. Never commit emit_byrd_jvm.c changes without running
this script first.**

Canonical artifacts tracked:
```
artifacts/jvm/hello_prog.j          ← null.sno (simplest program)
artifacts/jvm/samples/roman.j       ← roman.sno benchmark
artifacts/jvm/samples/wordcount.j   ← wordcount.sno strings test
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

## ⛔ SHARED RUNTIME INVARIANT — NET crosscheck when touching src/runtime/snobol4/

The files under `src/runtime/snobol4/` (`snobol4.c`, `snobol4_pattern.c`, etc.) are
linked by **all four backends** — C, ASM, JVM, and NET. Changes there can silently
break JVM or NET even when the C and ASM crosschecks pass. This has happened.

**Rule:** Any session that modifies any file under `src/runtime/snobol4/` MUST also
run the NET crosscheck before pushing:

```bash
cd /home/claude/snobol4x
bash test/crosscheck/run_crosscheck_net.sh   # must not regress vs last known NET baseline
```

If the NET baseline is unknown, record the current count before your change and
confirm it does not drop after. A drop is a regression — fix it before pushing.

JVM is best-effort (requires jasmin + JVM runtime, may not be present). NET is
mandatory because `mono`/`ilasm` are available on standard containers.

This rule applies regardless of which session type (B/J/N/F/D) is doing the work.

## ⛔ MILESTONE ORDER — TINY.md sprint must match PLAN.md dashboard order

**The sprint in TINY.md NOW must always be the next ❌ milestone in PLAN.md's milestone dashboard, in sequence.**

- PLAN.md is the authoritative source of milestone order. Never skip ahead.
- When writing the "CRITICAL NEXT ACTION" block at the end of a session, look up the next ❌ in PLAN.md — do not invent or reorder.
- If TINY.md NOW and PLAN.md dashboard disagree: PLAN.md wins. Fix TINY.md.
- This rule exists because B-204 wrote M-ASM-BEAUTY as next sprint, skipping RUNG8/9/10/11 and LIBRARY and ENG685 entirely.

## ⛔ L2 DOC SIZE — replace, never append; hard limit 10 KB

**L2 docs (TINY.md, JVM.md, DOTNET.md) have a hard size limit of 10 KB.**

TINY.md ballooned from ~5 KB to 155 KB because each session *prepended* a new
"CRITICAL NEXT ACTION" block without deleting the previous one. DOTNET.md hit
57 KB the same way. This is the failure mode: "update" interpreted as "add to top."

**The rule:** When writing the end-of-session "CRITICAL NEXT ACTION" and summary:
1. **DELETE** the previous session's "CRITICAL NEXT ACTION" block entirely.
2. **DELETE** the previous session's summary — or keep at most the last TWO summaries.
3. **REPLACE** the NOW section — do not prepend to it.
4. Session history → **SESSIONS_ARCHIVE.md only**. Never accumulate in L2.
5. Sprint plans for **completed** sprints → delete from L2. They are in SESSIONS_ARCHIVE.
6. Root cause notes for **fixed** bugs → delete from L2. They are in SESSIONS_ARCHIVE.

**Check before every push:**
```bash
wc -c /home/claude/.github/TINY.md      # must be under 10240
wc -c /home/claude/.github/JVM.md       # must be under 10240
wc -c /home/claude/.github/DOTNET.md    # must be under 10240
```
If any L2 doc exceeds 10 KB: trim it before pushing. No exceptions.

**What belongs in L2:**
- Current HEAD + branch + session number
- Current sprint name + 3–5 concrete next steps (the CRITICAL NEXT ACTION block)
- Last 1–2 session summaries (3–5 lines each) for continuity
- Active milestone status table (next 5 milestones only)
- Concurrent session table
- Pointers to L3 docs

**What does NOT belong in L2:**
- Completed sprint plans
- Fixed bug root causes
- Architecture notes (→ ARCH.md or BACKEND-X64.md)
- Old CRITICAL NEXT ACTION blocks
- Session summaries older than 2 sessions (→ SESSIONS_ARCHIVE.md)

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

## ⛔ NEW FILES — Any file created for the project belongs in a repo immediately

On 2026-03-19 (B-205): claws5.sno and treebank.sno were written to the container
filesystem and not committed. They were nearly lost. The session had to be extended
to recover them.

**The rule:** Creating a project file and committing it to the correct repo are the
same act. There is no such thing as a project file that lives only on the container.

- `.sno` program for ENG685/corpus → `snobol4corpus` → commit + push immediately
- `.s` ASM artifact → `snobol4x/artifacts/asm/` → commit + push
- `.c` C artifact → `snobol4x/artifacts/c/` → commit + push
- Any other project output → find its repo → commit + push

**The test:** Before closing any session, ask: "Did I create any files this session?"
If yes: are they all in a repo? If not: `git add -A` will catch them.

`git add -A` is not just about modified files. The `-A` exists precisely to catch
new files you might have forgotten. Run it. Every time. On every touched repo.

**A file on the container that is not in a repo does not exist.**

## ⛔ REPO PATHS — Canonical clone locations (use these, never symlinks)

All repos are cloned into `/home/claude/` as siblings:

```
/home/claude/snobol4x/          ← compiler + backends
/home/claude/snobol4corpus/     ← test corpus
/home/claude/snobol4harness/    ← harness
/home/claude/snobol4jvm/        ← JVM/Clojure backend
/home/claude/.github/           ← HQ docs
```

Derived canonical paths — **always set these env vars before running any test script:**

```bash
export CORPUS=/home/claude/snobol4corpus/crosscheck
export INC=/home/claude/snobol4corpus/programs/inc
export BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
export ROMAN=/home/claude/snobol4corpus/benchmarks/roman.sno
export WORDCOUNT=/home/claude/snobol4corpus/crosscheck/strings/wordcount.sno
```

**Never create symlinks. Ever. For any reason.**
**Never patch scripts to hardcode paths.** Set the env vars. That is the correct and
only fix.

Scripts and their path behavior — always pass CORPUS= when the default is wrong:

| Script | Default CORPUS | Needs CORPUS= ? |
|--------|---------------|-----------------|
| `snobol4x/test/crosscheck/run_crosscheck.sh` | derived via `$TINY/../..` → `/home/snobol4corpus` | **YES** |
| `snobol4x/test/crosscheck/run_crosscheck_asm.sh` | `/home/snobol4corpus/crosscheck` | **YES** |
| `snobol4x/test/crosscheck/run_crosscheck_asm_corpus.sh` | `/home/claude/snobol4corpus/crosscheck` | no |
| `snobol4x/test/crosscheck/run_crosscheck_asm_prog.sh` | `/home/claude/snobol4corpus/crosscheck/beauty` | no |
| `snobol4x/test/crosscheck/run_crosscheck_asm_rung.sh` | args passed explicitly | no |
| `snobol4x/test/crosscheck/run_crosscheck_jvm_rung.sh` | args passed explicitly | no |
| `snobol4x/test/crosscheck/run_crosscheck_net.sh` | `/home/claude/snobol4corpus/crosscheck` | no |
| `snobol4harness/crosscheck/crosscheck.sh` | `$HOME/snobol4corpus/crosscheck` = `/root/...` | **YES** |
| `snobol4harness/crosscheck/bench.sh` | `$HOME/snobol4corpus` = `/root/...` | **YES** |
| `snobol4harness/adapters/tiny/run.sh` | derives from `$TINY_REPO` — set that var | **YES** |
| `snobol4harness/adapters/dotnet/run_crosscheck_dotnet.sh` | `$HOME/snobol4corpus/crosscheck` = `/root/...` | **YES** |

All scripts that support `${CORPUS:-...}` honor `CORPUS=` as an env override.
All scripts that take explicit dir args (jvm_rung, asm_rung) — pass full paths directly.
