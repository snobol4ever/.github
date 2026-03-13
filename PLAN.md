# SNOBOL4ever — HQ

**SNOBOL4 everywhere. SNOBOL4 now. SNOBOL4 forever.**

Lon Jones Cherryholmes (compiler, architecture) and Jeffrey Cooper M.D. (SNOBOL4-dotnet, MSIL)
building full SNOBOL4/SPITBOL implementations on JVM, .NET, and native C — plus Rebus, Snocone,
and a self-hosting native compiler. Claude Sonnet 4.6 is the third developer and author of SNOBOL4-tiny.

---

## Two Levels

**Milestones** are proof points — mathematical claims about what the system *is*. Each has a
trigger condition, not a time estimate. When the trigger fires, Claude writes the commit.

**Sprints** are bounded work packages that move a repo toward the next milestone. Each repo
tracks its own sprints independently. Sprints can be paused and resumed across repos.

---

## Org-Level Milestones

| ID | Trigger | Repo | Status |
|----|---------|------|--------|
| **M0** | `beauty_full_bin` self-beautifies — diff empty | TINY | ⏸ Paused (Sprint 26) |
| **M1** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | TINY | ✅ Done |
| **M2** | Compiled binary self-beautifies — diff empty | TINY | ❌ |
| **M3** | `snoc` compiles `snoc` itself (self-hosting) | TINY | ❌ Future |
| **MREBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | TINY | ❌ Active |
| **MJVM** | JVM inline EVAL! complete (Sprint 23E) | JVM | ❌ |
| **MNET** | .NET Step 14 — `Instruction[]` eliminated | DOTNET | ❌ |

---

## Active Repos

| Repo | MD File | Active Sprint | Milestone Target |
|------|---------|--------------|-----------------|
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | [TINY.md](TINY.md) | Rebus R3 — emitter | MREBUS |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | [JVM.md](JVM.md) | Sprint 23E — inline EVAL! | MJVM |
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | [DOTNET.md](DOTNET.md) | Step 14 — eliminate Instruction[] | MNET |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | [CORPUS.md](CORPUS.md) | Stable — add Rebus oracle .sno files | MREBUS |
| [SNOBOL4-harness](https://github.com/SNOBOL4-plus/SNOBOL4-harness) | [HARNESS.md](HARNESS.md) | Stable | — |

---

## Commands

Five directives. Use them by name in any session.

### SNAPSHOT
Push everything now. Container-safe. WIP commit is fine.
1. `git add -A && git commit -m "WIP: <what>"` (or clean message if tests green)
2. `git push` — every touched repo
3. Confirm each: `git log --oneline -1`
4. Push `.github` last.

### HANDOFF
End of session. Next Claude starts cold from this.
1. Run **SNAPSHOT** first.
2. Update the active repo's MD file: last commit, current sprint, current blocker, next action.
3. Update `SESSION.md`: active repo pointer + one-line state.
4. Push `.github`.

### EMERGENCY HANDOFF
Time's up or something broke. Speed over completeness.
1. `git add -A && git commit -m "EMERGENCY WIP: <state>"` on every touched repo.
2. `git push` all. Confirm each.
3. Append one line to `SESSION.md`: what's broken, what's next.
4. Push `.github`.

### SWITCH REPO `<repo>`
Change active repo.
1. Run **HANDOFF** on current repo first (leaves it clean).
2. Read `<REPO>.md` → Current State section.
3. Update `SESSION.md`: new active repo pointer.
4. Do the session-start checklist in that repo's MD file.

### PRIORITY SHIFT `<repo>` `<new focus>`
Pause current sprint, declare new priority within a repo.
1. Record paused sprint in `<REPO>.md` → Current Sprint (mark PAUSED + last commit).
2. Write new sprint/priority into Current Sprint.
3. Commit `.github`: `"priority shift: <repo> — <new focus>"`

---

## Session Start (every session, no exceptions)

```
1. Read SESSION.md — what repo, what sprint, what's next.
2. Read that repo's MD file — Current State section.
3. git log --oneline --since="1 hour ago"  (fallback: -5)
4. find src -type f | sort
5. git show HEAD --stat
```

---

## File Index

| File | What it is |
|------|------------|
| [SESSION.md](SESSION.md) | Active repo pointer + live handoff state |
| [TINY.md](TINY.md) | SNOBOL4-tiny — milestones, sprints, Rebus, hand-rolled parser, arch |
| [JVM.md](JVM.md) | SNOBOL4-jvm — milestones, sprints, design decisions |
| [DOTNET.md](DOTNET.md) | SNOBOL4-dotnet — milestones, MSIL steps, solution layout |
| [CORPUS.md](CORPUS.md) | SNOBOL4-corpus — what lives there, how all repos use it |
| [HARNESS.md](HARNESS.md) | Test harness — double-trace monitor, oracle protocol, benchmarks |
| [STATUS.md](STATUS.md) | Live test counts and benchmarks — updated each session |
| [PATCHES.md](PATCHES.md) | Runtime patch audit trail (SNOBOL4-tiny) |
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | Full session history — append-only |
| [MISC.md](MISC.md) | Origin story, JCON reference, keyword tables, background |
