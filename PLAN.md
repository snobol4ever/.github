# SNOBOL4ever — HQ

**snobol4now. snobol4ever.**

Lon Jones Cherryholmes (compiler, architecture) and Jeffrey Cooper M.D. (SNOBOL4-dotnet, MSIL)
building full SNOBOL4/SPITBOL implementations on JVM, .NET, and native C — plus Rebus, Snocone,
and a self-hosting native compiler. Claude Sonnet 4.6 is the third developer and author of SNOBOL4-tiny.

---

## ⛔ TOKEN RULE — NEVER WRITE THE TOKEN INTO ANY FILE (mandatory, no exceptions)

**Claude committed the GitHub PAT directly into SESSION.md on 2026-03-13. GitHub push
protection caught it and blocked the push. The commit had to be amended and force-pushed.
This must never happen again.**

### The rule:

**NEVER write the token string into any file in any repo — not SESSION.md, not HANDOFF
notes, not comments, not archive entries, not anywhere.**

The token lives in Lon's memory system only. It is provided at session start by Lon.
It is used in shell commands in-memory only. It is never persisted to disk in any file
that will be committed.

### What to write instead:

```
TOKEN=TOKEN_SEE_LON   ← placeholder only — Lon provides the real value at session start
```

### Why this matters:

GitHub push protection scans every commit for secrets. A blocked push requires amending
history, which is disruptive and leaves a dirty audit trail. More importantly, committing
a token to a repo is a security event — the token should be rotated after any exposure.

**Lon: if the token ever appears in a commit, rotate it immediately at
https://github.com/settings/tokens**

---

## Git Identity Rule (mandatory, no exceptions)

**Every commit across every SNOBOL4-plus repo must use:**

```
user.name  = LCherryholmes
user.email = lcherryh@yahoo.com
```

Set before every commit session:
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

Or per-commit:
```bash
git commit --author="LCherryholmes <lcherryh@yahoo.com>" -m "..."
```

**Pending:** SNOBOL4-tiny has 7 commits with wrong identity (5× `claude@anthropic.com`, 2× `lon@cherryholmes.com`) that need history rewrite via `git filter-repo` once confirmed safe with Lon.

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

### Agreement (Lon Cherryholmes + Claude Sonnet 4.6, 2026-03-13)

Once M-BEAUTY-FULL is complete there **must** be a milestone for switching the C
compiler over to proper compiled Byrd box emission AND unifying with the Python
pipeline. The Python work (`lower.py`, `byrd_ir.py`, `emit_c_byrd.py`, `emit_jvm.py`,
`emit_msil.py`) is intellectual property that must not be abandoned or orphaned.
It becomes the shared IR that all backends — C, JVM, MSIL — emit from.

That milestone is **M-PYTHON-UNIFIED**. It is locked in the roadmap above.
No future session may remove it or defer it without Lon's explicit instruction.

---

## Two Levels

**Milestones** are proof points — trigger conditions, not time estimates. When the trigger fires, Claude writes the commit.

**Sprints** are bounded work packages named by what they do. Each repo tracks its own sprints independently.

---

## Org-Level Milestones

| ID | Trigger | Repo | Status |
|----|---------|------|--------|
| **M-SNOC-COMPILES** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | TINY | ✅ Done |
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty | TINY | ⏳ sprint 2/4 `compiled-byrd-boxes` active |
| **M-REBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | TINY | ✅ Done `bf86b4b` |
| **M-COMPILED-BYRD** | `sno2c` emits labeled goto Byrd boxes — `engine.c` not linked | TINY | ⏳ Active — IS sprint 2/4 |
| **M-PYTHON-UNIFIED** | Python pipeline (`lower.py`, `emit_c_byrd.py`, `emit_jvm.py`, `emit_msil.py`) unified with C compiler — one IR, all backends | TINY | ❌ |
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

### Sprint 2 of 4 — `compiled-byrd-boxes` ⏳ Active (replaces retired `smoke-tests`)

**What:** `sno2c` emits labeled-goto Byrd box C. Validated against sprint0–22 oracles.
`engine.c` and `snobol4_pattern.c` dropped from the compiled binary path.

**Why smoke-tests was retired (2026-03-14):** It validated `sno_pat_*` / `engine.c` —
the stopgap interpreter — not the compiled Byrd box path. 15–20 hours lost chasing
interpreter bugs that don't matter. The Python pipeline (lower.py + emit_c_byrd.py)
already proved correctness at 609/609 worm cases. `emit_byrd.c` is a C port of that.

**Steps:**
1. Read `src/ir/byrd_ir.py`, `src/ir/lower.py`, `src/codegen/emit_c_byrd.py` — ground truth
2. Read `test/sprint0/` through `test/sprint5/` — correctness gate
3. Write `src/sno2c/emit_byrd.c` — LIT, CAT, ALT, EPSILON first; sprint0–5 passing
4. Add ARBNO, CAPTURE, FENCE, POS, TAB, RPOS, RTAB; sprint6–15 passing
5. Add USER_CALL (nInc, nPush, nPop, Reduce); sprint16–22 passing
6. Wire into emit.c, drop sno_pat_* from compiled path

**Commit when:** sprint0–22 all pass. Binary links without engine.c. **M-COMPILED-BYRD fires.**

---

### Sprint 3 of 4 — `beauty-runtime` ❌

**What:** `beauty_full_bin < beauty.sno` runs to completion without crashing.
Now using compiled Byrd boxes, not the interpreter. Sprint 3 catches runtime issues
in `snobol4.c` / `snobol4_inc.c` that surface when beauty actually runs.

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
