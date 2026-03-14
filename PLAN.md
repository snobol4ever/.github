# SNOBOL4ever — HQ

**snobol4now. snobol4ever.**

Lon Jones Cherryholmes (compiler, architecture) and Jeffrey Cooper M.D. (SNOBOL4-dotnet, MSIL)
building full SNOBOL4/SPITBOL implementations on JVM, .NET, and native C — plus Rebus, Snocone,
and a self-hosting native compiler. Claude Sonnet 4.6 is the third developer and author of SNOBOL4-tiny.

---

## Architectural Note — The sno_pat_* Stopgap (recorded 2026-03-13)

**The `sno_pat_*` / `engine.c` interpreter is a stopgap. It is not the destination.**

### How we got here

The original Python pipeline (`emit_c_byrd.py` + `lower.py`) generated proper compiled
Byrd boxes — labeled goto C with explicit α/β/γ/ω ports wired statically per pattern node.
This is the correct target architecture, proven by `bench/test_icon.sno` (Proebsting's
`5 > ((1 to 2) * (3 to 4))` implemented as SNOBOL4 labeled statements) and the 28
hand-written oracle C files in `test/sprint0–22`.

When the compiler was rewritten from Python to C (`sno2c`), there was no C equivalent
of `lower.py` yet. Rather than block progress, `sno_pat_*` + `engine.c` was introduced
as a bridge: `emit.c` emits `sno_pat_cat()` / `sno_pat_user_call()` / etc. calls that
build a pattern tree at runtime, which `engine.c` then interprets via a `type<<2|signal`
dispatch switch. The Byrd boxes are implicit in that dispatch table — not generated.

### What the destination looks like

For a pattern like `snoCommand`, the compiled output should be static labeled C:

```c
snoCommand_alpha:   /* nInc() */  goto nInc_alpha;
nInc_gamma:                       goto FENCE_alpha;
FENCE_alpha:        ...
snoCommand_omega:   return empty;
```

No tree. No dispatch table. No interpreter. Direct gotos, all wiring resolved at
compile time by a C port of `lower.py`.

### The path forward (after M-BEAUTY-FULL)

Add a new sprint `compiled-byrd-boxes` between M-BEAUTY-FULL and M-COMPILED-SELF:
- Write `src/sno2c/emit_byrd.c` — C port of `lower.py` + `emit_c_byrd.py`
- Replace `emit_pat()` in `emit.c` with calls to `emit_byrd.c`
- Drop `engine.c` + `snobol4_pattern.c` from the compiled binary path entirely
- `sno_pat_*` API becomes interpreter-only (EVAL, dynamic patterns)

**Do not lose `engine.c` or `snobol4_pattern.c`.** They remain correct and necessary
for dynamic patterns (EVAL, runtime-constructed patterns). The compiled path bypasses
them; the interpreter path keeps them.

---

## Two Levels

**Milestones** are proof points — trigger conditions, not time estimates. When the trigger fires, Claude writes the commit.

**Sprints** are bounded work packages named by what they do. Each repo tracks its own sprints independently.

---

## Org-Level Milestones

| ID | Trigger | Repo | Status |
|----|---------|------|--------|
| **M-SNOC-COMPILES** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | TINY | ✅ Done |
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty | TINY | ⏳ sprint 2/4 `smoke-tests` active |
| **M-REBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | TINY | ✅ Done `bf86b4b` |
| **M-COMPILED-BYRD** | `sno2c` emits labeled goto Byrd boxes — `engine.c` not linked | TINY | ❌ |
| **M-COMPILED-SELF** | Compiled binary self-beautifies — diff empty | TINY | ❌ |
| **M-BOOTSTRAP** | `snoc` compiles `snoc` (self-hosting) | TINY | ❌ Future |
| **M-JVM-EVAL** | JVM inline EVAL! complete (sprint `jvm-inline-eval`) | JVM | ❌ |
| **M-NET-DELEGATES** | .NET `Instruction[]` eliminated (sprint `net-delegates`) | DOTNET | ❌ |

---

## Active Repos

| Repo | MD File | Active Sprint | Milestone Target |
|------|---------|--------------|-----------------|
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | [TINY.md](TINY.md) | `smoke-tests` (2/4 toward M-BEAUTY-FULL) | M-BEAUTY-FULL |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | [JVM.md](JVM.md) | `jvm-inline-eval` | M-JVM-EVAL |
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | [DOTNET.md](DOTNET.md) | `net-delegates` | M-NET-DELEGATES |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | [CORPUS.md](CORPUS.md) | Stable — add Rebus oracle .sno files | M-REBUS |
| [SNOBOL4-harness](https://github.com/SNOBOL4-plus/SNOBOL4-harness) | [HARNESS.md](HARNESS.md) | Stable | — |

---

## Sprint Detail — toward M-BEAUTY-FULL (TINY)

Four sprints. In order. Each gates the next. Each ends with a commit.

---

### Sprint 1 of 4 — `space-token` ✅ Complete `3581830`

**What:** Eliminate all parser conflicts. Return `_` (whitespace) as a real token so concat is unambiguous.

Root cause of 20 SR + 139 RR conflicts: `WS` was silently skipped. Fix: `{WS} { return _; }`. Token named `_` (Lon's choice — bison allows it, cleaner than SPACE). Subject restricted to `term` — first space always separates subject from pattern. 159 conflicts → 0.

**Commit:** `3581830` — `feat(snoc): space-token — 0 bison conflicts, unified grammar`

---

### Sprint 2 of 4 — `smoke-tests` ⏳ Active

**What:** Drive `test_snoCommand_match.sh` from 0/21 → 21/21.

Each of the 21 statement types in beauty.sno must be matched by `snoCommand`. Pure structural match — no captures, no side effects. Any failure means the parser or emitter is misrouting that construct.

```bash
bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin
```

**Commit when:** All 21 pass. Zero "Parse Error" lines.

---

### Sprint 3 of 4 — `beauty-runtime` ❌

**What:** `beauty_full_bin < beauty.sno` runs to completion without crashing.

Known runtime fixes already landed: `DATA()` (`e4595a7`), `NRETURN`→success (`66b7eab`), `sno_inc_init()` (`627a030`). Sprint 3 catches whatever surfaces after the parser is correct. Diagnose with `SNO_PAT_DEBUG=1` and `SNOC_DEBUG=1`. Output may still differ from oracle — that's sprint 4.

**Commit when:** Binary exits cleanly on beauty.sno input. No crash, no hang, no abort.

---

### Sprint 4 of 4 — `beauty-full-diff` ❌ → **M-BEAUTY-FULL**

**What:** Empty diff. Self-beautification is exact.

```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno
/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
```

**Commit when:** Diff is empty. Claude Sonnet 4.6 writes the commit message. **M-BEAUTY-FULL fires.**

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
| [RENAME.md](RENAME.md) | One-time rename plan — SNOBOL4-plus → snobol4ever, naming rules, 8-phase execution |
