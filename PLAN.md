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

## ⛔ ALL BYRD BOXES — engine.c MUST NOT BE LINKED IN beauty_full_bin (mandatory, no exceptions)

**Lon's explicit requirement: every pattern in beauty_full_bin must be compiled Byrd boxes.
engine.c must not be linked. engine_stub.c only. No interpreter path in the compiled binary.**

### Canonical Architecture — Box Layout (decided Session 16, recorded SESSIONS_ARCHIVE.md)

Every pattern literal is compiled to a self-contained Byrd box:

```
Box layout:
┌─────────────────────────┐
│  DATA: cursor, locals,  │
│        captures, ports  │
├─────────────────────────┤
│  CODE: α/β/γ/ω gotos   │
└─────────────────────────┘
```

Boxes laid out linearly in memory:
```
DATA section:  [ box0.data | box1.data | box2.data | ... ]
TEXT section:  [ box0.code | box1.code | box2.code | ... ]
```

### *X (Dynamic Reference) Semantics

When `*X` fires at match time:
1. **Copy** the box block for X — both data and code sections
2. **Relocate** the code — patch internal jump offsets
3. The copy gets its own independent locals — that IS the new instance

No heap. No GC. No engine. ~20 lines of `mmap + memcpy + relocate`.
Code duplication is intentional — each instantiation is independent, cache-hot.

### What this means for sno2c / emit_byrd.c

- Every pattern assignment (`snoParse = ARBNO(*snoCommand)...`) → emit static Byrd box with named data+code layout
- Every `*varname` in a pattern → emit box-copy + relocate at match time
- `emit_pat()` generating `pat_cat()`/`pat_arbno()`/`pat_ref()` → **eliminated entirely**
- `snobol4_pattern.c` → interpreter only (EVAL). Not in compiled path.
- `engine.c` → interpreter only (EVAL). Not in compiled path.

### Every session: verify engine.c is NOT in the build command for beauty_full_bin.

```bash
gcc -O0 -g -I $R/snobol4 -I $R \
    beauty_full.c $R/snobol4/snobol4.c \
    $R/snobol4/snobol4_inc.c \
    $R/engine_stub.c -lgc -lm -o beauty_full_bin
```
If you find yourself typing `engine.c` — STOP. You are in the trap.

---

## ⛔ ARTIFACT RULE — SNAPSHOT beauty_full.c EVERY SESSION (mandatory, no exceptions)

**Claude failed to store artifacts/beauty_full_sessionN.c for multiple sessions (52→53 gap
spanned the sno_/SNO_ prefix eradication AND M-COMPILED-BYRD). This must never happen again.**

### The rule:

At the END of every session that touches `sno2c` or `emit*.c` or `runtime/`:
1. Run `sno2c -I $INC $BEAUTY > artifacts/beauty_full_sessionN.c` where N = last session number + 1
2. Record md5, line count, compile status, active bug in `artifacts/README.md`
3. Commit artifacts/ with message `artifact: beauty_full_sessionN.c — <one-line status>`

**Do this even if nothing changed** — the artifact confirms the compiler still produces
the same output. A matching md5 is useful data. A missing snapshot is a gap in the record.

### When to increment N:
- Look at the last `beauty_full_sessionN.c` filename in `artifacts/` and add 1.
- If unsure, check `git log --oneline -- artifacts/` for the last session number used.

### What to write in README.md:
- What changed since last artifact (commits, fixes)
- Line count + md5
- Compile status (0 errors / N warnings)
- Active bug / current symptom

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

### Decision (Lon Cherryholmes + Claude Sonnet 4.6, 2026-03-14)

**M-PYTHON-UNIFIED is retired.** The Python pipeline (`lower.py`, `byrd_ir.py`,
`emit_c_byrd.py`, `emit_jvm.py`, `emit_msil.py`) was the prototype — the scaffold
that proved the Byrd box architecture correct at 609/609 worm cases. `emit_byrd.c`
is the real implementation. The scaffold served its purpose and is now archaeological
reference, not a build dependency.

Python has no place in the compiler pipeline. The JVM and MSIL backends will implement
the four-port Byrd box lowering natively in their own languages (Java, C#), not by
calling into Python.

The replacement milestone is **M-BYRD-SPEC**: a language-agnostic written specification
of the four-port lowering rules (α/β/γ/ω wiring per node type) that all three backends
implement independently but consistently. The spec lives in HQ. It is the shared
contract, not shared code.

---

## Two Levels

**Milestones** are proof points — trigger conditions, not time estimates. When the trigger fires, Claude writes the commit.

**Sprints** are bounded work packages named by what they do. Each repo tracks its own sprints independently.

---

## Org-Level Milestones

| ID | Trigger | Repo | Status |
|----|---------|------|--------|
| **M-SNOC-COMPILES** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | TINY | ✅ Done |
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty | TINY | ⏳ sprint 3/4 `beauty-runtime` next |
| **M-REBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | TINY | ✅ Done `bf86b4b` |
| **M-COMPILED-BYRD** | `sno2c` emits labeled goto Byrd boxes — `engine.c` not linked | TINY | ✅ Done `560c56a` |
| **M-BYRD-SPEC** | Language-agnostic written spec of four-port Byrd box lowering rules — all backends (C, JVM, MSIL) implement independently against it | HQ | ❌ |
| **M-COMPILED-SELF** | Compiled binary self-beautifies — diff empty | TINY | ❌ |
| **M-BOOTSTRAP** | `snoc` compiles `snoc` (self-hosting) | TINY | ❌ Future |
| **M-JVM-EVAL** | JVM inline EVAL! complete (sprint `jvm-inline-eval`) | JVM | ❌ |
| **M-NET-DELEGATES** | .NET `Instruction[]` eliminated (sprint `net-delegates`) | DOTNET | ❌ |

---

## Active Repos

| Repo | MD File | Active Sprint | Milestone Target |
|------|---------|--------------|-----------------|
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | [TINY.md](TINY.md) | `beauty-runtime` (3/4 toward M-BEAUTY-FULL) | M-BEAUTY-FULL |
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

### Sprint 2 of 4 — `compiled-byrd-boxes` ✅ Complete `560c56a`

**What:** `sno2c` emits labeled-goto Byrd box C. Validated against sprint0–22 oracles.
`engine.c` dropped from compiled binary path via `engine_stub.c`.

**M-COMPILED-BYRD fired `560c56a`.**

**What:** `sno2c` emits labeled-goto Byrd box C. Validated against sprint0–22 oracles.
`engine.c` and `snobol4_pattern.c` dropped from the compiled binary path.

**Why smoke-tests was retired (2026-03-14):** It validated `sno_pat_*` / `engine.c` —
the stopgap interpreter — not the compiled Byrd box path. 15–20 hours lost chasing
interpreter bugs that don't matter. The Python pipeline (lower.py + emit_c_byrd.py)
already proved correctness at 609/609 worm cases. `emit_byrd.c` is a C port of that.

**Steps:**
1. Read `src/ir/byrd_ir.py`, `src/ir/lower.py`, `src/codegen/emit_c_byrd.py` — prototype reference
2. Read `test/sprint0/` through `test/sprint5/` — correctness gate
3. Write `src/sno2c/emit_byrd.c` — LIT, CAT, ALT, EPSILON first; sprint0–5 passing
4. Add ARBNO, CAPTURE, FENCE, POS, TAB, RPOS, RTAB; sprint6–15 passing
5. Add USER_CALL (nInc, nPush, nPop, Reduce); sprint16–22 passing
6. Wire into emit.c, drop sno_pat_* from compiled path

**Commit when:** sprint0–22 all pass. Binary links without engine.c. **M-COMPILED-BYRD fires.**

---

### Sprint 3 of 4 — `compiled-byrd-boxes-full` ⏳ Active (REPLACES beauty-runtime)

**What:** Inline ALL pattern variables as static Byrd boxes. engine.c dropped entirely.
engine_stub.c only. No `pat_cat()`/`pat_arbno()`/`pat_ref()` in the init section of
beauty_full.c. No `match_pattern_at()` calls. No E_DEREF runtime dispatch.

`snoParse`, `snoCommand`, `snoLabel`, `snoStmt`, `snoComment`, `snoControl` — all
emitted as labeled-goto C by emit_byrd.c. ARBNO wiring static.

**Why beauty-runtime was wrong:** Chased engine.c interpreter bugs — same smoke-test
trap. engine.c is broken for *snoParse. Fixing it is the wrong path.

**Commit when:** beauty_full.c has zero pat_cat/pat_arbno/pat_ref in init section.
Binary links with engine_stub.c only. Runs on beauty.sno input without crash.

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
