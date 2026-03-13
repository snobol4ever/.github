# SNOBOL4ever — HQ

**SNOBOL4 everywhere. SNOBOL4 now. SNOBOL4 forever.**

Lon Jones Cherryholmes (compiler, architecture) and Jeffrey Cooper M.D. (SNOBOL4-dotnet, MSIL)
building full SNOBOL4/SPITBOL implementations on JVM, .NET, and native C — plus Rebus, Snocone,
and a self-hosting native compiler. Claude Sonnet 4.6 is the third developer and author of SNOBOL4-tiny.

---

## Two Levels

**Milestones** are proof points — trigger conditions, not time estimates. When the trigger fires, Claude writes the commit.

**Sprints** are bounded work packages named by what they do. Each repo tracks its own sprints independently.

---

## Org-Level Milestones

| ID | Trigger | Repo | Status |
|----|---------|------|--------|
| **M-SNOC-COMPILES** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | TINY | ✅ Done |
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty | TINY | ⏸ sprint `hand-rolled-parser` paused |
| **M-REBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | TINY | ❌ Active |
| **M-COMPILED-SELF** | Compiled binary self-beautifies — diff empty | TINY | ❌ |
| **M-BOOTSTRAP** | `snoc` compiles `snoc` (self-hosting) | TINY | ❌ Future |
| **M-JVM-EVAL** | JVM inline EVAL! complete (sprint `jvm-inline-eval`) | JVM | ❌ |
| **M-NET-DELEGATES** | .NET `Instruction[]` eliminated (sprint `net-delegates`) | DOTNET | ❌ |

---

## Active Repos

| Repo | MD File | Active Sprint | Milestone Target |
|------|---------|--------------|-----------------|
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | [TINY.md](TINY.md) | `rebus-emitter` | M-REBUS |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | [JVM.md](JVM.md) | `jvm-inline-eval` | M-JVM-EVAL |
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | [DOTNET.md](DOTNET.md) | `net-delegates` | M-NET-DELEGATES |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | [CORPUS.md](CORPUS.md) | Stable — add Rebus oracle .sno files | M-REBUS |
| [SNOBOL4-harness](https://github.com/SNOBOL4-plus/SNOBOL4-harness) | [HARNESS.md](HARNESS.md) | Stable | — |

---

## Commands

### SNAPSHOT
Push everything now. Container-safe. WIP commit is fine.
1. `git add -A && git commit -m "WIP: <what>"` (or clean message if tests green)
2. `git push` — every touched repo
3. Confirm each: `git log --oneline -1`
4. Push `.github` last.

### HANDOFF
End of session. Next Claude starts cold from SESSION.md alone.
1. Run **SNAPSHOT** first.
2. Update SESSION.md — all four fields, plus Pivot Log if anything shifted.
3. Update the active repo's MD file — Current State + Pivot Log.
4. Push `.github`.

### EMERGENCY HANDOFF
Time's up or something broke. Speed over completeness.
1. `git add -A && git commit -m "EMERGENCY WIP: <state>"` on every touched repo.
2. `git push` all. Confirm each.
3. Append one line to SESSION.md Pivot Log: what broke, what's next.
4. Push `.github`.

### SWITCH REPO `<repo>`
1. Run **HANDOFF** on current repo first.
2. Read `<REPO>.md` → Current State.
3. Update SESSION.md: new active repo, sprint, milestone, next action.

### PRIORITY SHIFT `<repo>` `<sprint-slug>`
1. Record paused sprint in repo MD Pivot Log (mark PAUSED + last commit).
2. Write new sprint into Current State.
3. Update SESSION.md.
4. Commit `.github`: `"priority shift: <repo> — <sprint-slug>"`

---

## Session Start (every session, no exceptions)

```
1. Read SESSION.md — fully self-contained. Repo, sprint, last thing, next action.
2. git log --oneline --since="1 hour ago"  (fallback: -5)
3. find src -type f | sort
4. git show HEAD --stat
5. If you need depth: read the repo's MD file.
```

---

## File Index

| File | What it is |
|------|------------|
| [SESSION.md](SESSION.md) | Self-contained handoff — all four fields, start here every session |
| [TINY.md](TINY.md) | SNOBOL4-tiny — milestones, sprint map, Rebus, hand-rolled parser, arch |
| [JVM.md](JVM.md) | SNOBOL4-jvm — milestones, sprint map, design decisions |
| [DOTNET.md](DOTNET.md) | SNOBOL4-dotnet — milestones, sprint map, MSIL steps |
| [CORPUS.md](CORPUS.md) | SNOBOL4-corpus — what lives there, how all repos use it |
| [HARNESS.md](HARNESS.md) | Test harness — double-trace monitor, oracle protocol, benchmarks |
| [STATUS.md](STATUS.md) | Live test counts and benchmarks — updated each session |
| [PATCHES.md](PATCHES.md) | Runtime patch audit trail (SNOBOL4-tiny) |
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | Full session history — append-only |
| [MISC.md](MISC.md) | Origin story, JCON reference, keyword tables, background |
