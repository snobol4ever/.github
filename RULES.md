# RULES.md — snobol4ever Working Rules

---

## Rules belong in RULES.md

⛔ Do **not** add rules to `PLAN.md`. Global rules live in `RULES.md` only.
`PLAN.md` is navigation and state. `RULES.md` is rules.

---

## Never touch DATATYPE case behavior

⛔ Do **not** modify DATATYPE return case in any runtime. This is intentional per architecture:
- **SPITBOL / snobol4dotnet**: returns lowercase — `"integer"`, `"string"`, `"pattern"`, etc.
- **one4all / snobol4jvm**: returns uppercase — `"INTEGER"`, `"STRING"`, `"PATTERN"`, etc.

`.sno` source that compares DATATYPE results must handle both cases portably using
`REPLACE(DATATYPE(x), &LCASE, &UCASE)` before comparing against uppercase literals.

---

## Never patch corpus source to work around runtime bugs

⛔ Do **not** modify `.sno` or `.inc` source files to work around a problem in the runtime
unless the source itself is syntactically or semantically wrong **and** that wrongness is
confirmed by running the program under SPITBOL (the oracle). If SPITBOL runs it correctly,
the bug is in the runtime — fix the runtime, not the source.

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

Never write the token to disk.

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

Handoff checklist:
1. Update state variables in the Goal file (steps, watermarks, HEAD hash, pass counts)
2. Update Current Step in PLAN.md goals table
3. `git add -A && git commit` on all touched repos
4. `git pull --rebase && git push` — code repos first, .github last
5. Write a clear commit message on .github — this IS the session record

---

## Oracles — SPITBOL x64 (primary) and CSNOBOL4 (secondary)

### SPITBOL x64 — primary oracle
```
/home/claude/x64/bin/sbl          # binary
/home/claude/x64/                 # repo (snobol4ever/x64)
```
Build: `bash /home/claude/one4all/scripts/build_spitbol_oracle.sh`

Derive .ref output: `/home/claude/x64/bin/sbl -b file.sno > file.ref`
With includes: `/home/claude/x64/bin/sbl -I/home/claude/corpus/programs/snobol4/demo/inc file.sno`

SPITBOL is the **primary oracle for all goals and all testing** across the project.

### CSNOBOL4 2.3.3 — second oracle
```
/home/claude/csnobol4/snobol4     # binary
/home/claude/csnobol4/            # repo (snobol4ever/csnobol4)
```
Build: `bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh`

CSNOBOL4 is a **second oracle** — used alongside SPITBOL in the sync-step monitor harness
and for any goal where CSNOBOL4 compatibility is explicitly required.
When SPITBOL and CSNOBOL4 agree: correct. When they disagree: investigate; SPITBOL wins
on ambiguous cases unless the goal explicitly targets CSNOBOL4 behaviour.

**Silly exception:** CSNOBOL4 is the sole oracle for Silly SNOBOL4 goals (SS-MONITOR,
GOAL-SILLY-*) because Silly is a faithful C rewrite of CSNOBOL4's SIL source.

DATATYPE rules (authoritative):

- **SPITBOL** (primary oracle): returns lowercase — `"integer"`, `"pattern"`, `"string"`, etc.
- **CSNOBOL4** (second oracle): returns uppercase — `"INTEGER"`, `"PATTERN"`, `"STRING"`, etc.
- **snobol4dotnet**: returns lowercase — same as SPITBOL. This is intentional.
- **one4all**: returns uppercase — `"NAME"`, `"PATTERN"`, `"STRING"`, etc. This is intentional — SIL SNOBOL4 spec.

**Valid test rule:** Any test that checks a DATATYPE result must be portable across case.
Do NOT hardcode `IDENT(DATATYPE(x), 'string')` or `IDENT(DATATYPE(x), 'STRING')`.
Instead compare against a runtime-derived token: `dSTRING = DATATYPE('')`, `dNAME = DATATYPE(.x)`, etc.
Tests that hardcode DATATYPE case strings are **invalid** and must be rewritten.

**is.sno invalid:** `IsSnobol4()` / `IsSpitbol()` use `IDENT/DIFFER(.NAME, 'NAME')` to
discriminate dialect. This check is no longer valid — snobol4dotnet uses lowercase DATATYPE
like SPITBOL but `.NAME` yields `'NAME'`. The `.NAME` trick cannot reliably distinguish
SNOBOL4 from SPITBOL in snobol4dotnet. Any test depending on `IsSnobol4()` or `IsSpitbol()`
to gate behavior is invalid for snobol4dotnet.

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

---

## Session setup — run only what the Goal file lists

Session setup is defined in the Goal file's `## Session Setup` section.
Run exactly those scripts, no more.
Do **not** run `install_everything_full_stack.sh` for a specific goal unless the Goal file explicitly lists it.
If the Goal file has no `## Session Setup` yet, fall back to the matching category in `REPO-one4all.md ## Session Setup`.

---

## Self-contained scripts — all scripts in one4all/scripts/

All scripts live in `one4all/scripts/`. One flat directory. No scripts elsewhere except fixture-local glue scripts co-located with their test assets.

⛔ Do **not** build or test anything by typing ad-hoc shell commands. Every action must be driven by a checked-in script in `one4all/scripts/`. If no script exists, write one, check it in, then run it.

**Naming — prefix declares type, snake_case, descriptive phrases:**

| Prefix | Meaning |
|--------|---------|
| `install_` | Fetch packages, clone repos, set up environment |
| `build_` | Compile source, produce binaries |
| `regenerate_` | Derive generated files from source (parser/lexer) |
| `run_` | Compile + execute a single file via a specific backend |
| `test_` | Run a test suite, report PASS/FAIL |
| `util_` | Ad-hoc developer tools, sweeps, one-off runners |

**Every script must be self-contained:**

1. **Paths derived from `$0`**, never from env vars:
   ```bash
   HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   SCRIP="${SCRIP:-$HERE/scrip}"
   ```
2. **Every `scrip` call gets `< /dev/null`** unless the test explicitly needs stdin — scrip only blocks when the *program itself* reads `INPUT`. Use `< /dev/null` unconditionally; it's zero cost and prevents hangs on unknown corpus programs.
3. **Every `scrip` call gets `timeout N`** — 8s for unit/smoke tests, 30s for corpus runners.
4. **Corpus path hardcoded to `/home/claude/corpus`**. If missing: print a clear SKIP message and exit 0. Never fail silently, never fail hard.
5. **Oracle paths hardcoded**: SPITBOL = `/home/claude/x64/bin/sbl`, CSNOBOL4 = `/home/claude/csnobol4/snobol4`. Same SKIP rule.
6. **`build_*` and `install_*` scripts are idempotent** — running twice is safe. Check before acting.
7. **No script sources another script's env** — each is fully standalone.

---



## SNOBOL4 pattern matching globals — always set both

Always set both of these at program start, no exceptions:

```snobol4
               &ANCHOR         =  0
               &FULLSCAN       =  1
```

⛔ Do **not** set `&ANCHOR = 1` anywhere. Ever. Not in test code, not in production.
⛔ Do **not** omit `&FULLSCAN = 1`. It must always be set.

`bison` and `flex` are installed by `build_packages.sh` and are available in every session.

**When you edit a `.y` or `.l` file:**
1. Run `bash scripts/regenerate_parser_and_lexer_from_sources.sh` — regenerates `.tab.c`, `.tab.h`, `.lex.c`.
2. Commit the `.y`/`.l` source AND the updated generated files together in one commit.
3. Never edit `.tab.c` or `.lex.c` directly for grammar/lexer logic — edit the `.y`/`.l` source.
   Exception: epilogue functions hand-written directly in `.tab.c` (e.g. `sno_parse_string`)
   should be migrated to the `.y` epilogue section so they regenerate correctly.

The generated files are committed so normal builds never require bison/flex at build time.
`build_regenerate.sh` is only needed after `.y`/`.l` changes.

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

## Parallel frontend sessions  (FI-11)

Each frontend now owns a distinct subtree. Six sessions can develop simultaneously
with zero shared-file conflicts on the hot path, provided these rules are followed.

### Inner-loop gate (per-session, before every commit)
Run only the smoke script for the frontend you are working on:

| Session | Gate script |
|---------|-------------|
| SNOBOL4 | `bash scripts/test_smoke_snobol4.sh` |
| Icon    | `bash scripts/test_smoke_icon.sh` |
| Prolog  | `bash scripts/test_smoke_prolog.sh` |
| Raku    | `bash scripts/test_smoke_raku.sh` |
| Snocone | `bash scripts/test_smoke_snocone.sh` |
| Rebus   | `bash scripts/test_smoke_rebus.sh` |

### Merge gate (required before pushing shared files)
Run the full suite before any commit that touches a shared file:

```bash
bash scripts/test_smoke_unified_broker.sh   # must be PASS=31+ FAIL=0
```

### File ownership — who touches what
| Path | Owner | Merge gate required? |
|------|-------|----------------------|
| `src/frontend/snobol4/` | SNOBOL4 session | No — smoke only |
| `src/frontend/icon/` | Icon session | No — smoke only |
| `src/frontend/prolog/` | Prolog session | No — smoke only |
| `src/frontend/raku/` | Raku session | No — smoke only |
| `src/frontend/snocone/` | Snocone session | No — smoke only |
| `src/frontend/rebus/` | Rebus session | No — smoke only |
| `src/runtime/interp/icn_runtime.c` | Icon session | Yes |
| `src/runtime/interp/pl_runtime.c` | Prolog session | Yes |
| `src/driver/interp.c` | Shared — coordinate | Yes |
| `src/driver/polyglot.c` | Shared — coordinate | Yes |
| `src/driver/scrip.c` | Shared — rarely touched | Yes |
| `src/ir/ir.h` | Shared — coordinate | Yes |
| `src/runtime/x86/sm_lower.c` | Shared x86 backend | Yes |
| `src/runtime/x86/sm_interp.c` | Shared x86 backend | Yes |
| `src/runtime/x86/bb_broker.c` | Shared x86 backend | Yes |

### EKind additions
Before adding a new EKind to `ir/ir.h`, open a `.github` issue naming:
- the frontend requiring the new kind
- the goal it belongs to
- the SM/BB classification (functional → SM opcode, generator → BB pump)

Coordinate with any session that touches `sm_lower.c` or `interp.c`.

### Commit discipline
- Commits to `src/frontend/<lang>/` only: smoke gate sufficient.
- Commits to any shared file: full broker suite must pass before push.
- Never force-push. Rebase before pushing `.github`.

---



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

---

## No duplicate corpus source files

⛔ Do **not** have two copies of the same source file anywhere in corpus.
Applies to all corpus source: `.sno`, `.inc`, `.pl`, `.icn`, and any other
program source extension.

If a duplicate is discovered: keep the more authoritative copy (beauty/ over demo/inc/,
crosscheck/ over a redundant subfolder, etc.) and delete the other. Never resolve
duplication with symlinks — symlinks break when targets move or are deleted.
Use real files only. The canonical location is wherever the test harness expects to find it.

---

## No symlinks in shell scripts

⛔ Do **not** use `ln -s` or any symlink creation in shell scripts, Makefiles, or CI.
Symlinks break silently when targets move or are deleted (see corpus fbab26b incident).
Use real files, copies, or path variables instead.
If a script currently creates symlinks, replace with `cp` or direct path references.

---

## snobol4dotnet DATATYPE always returns lowercase

`DATATYPE()` in snobol4dotnet always returns lowercase: `'string'`, `'integer'`,
`'pattern'`, `'array'`, `'table'`, `'name'`, `'code'`, `'expression'`.
User-defined DATA type names are also lowercased via `ToLowerInvariant()`.

⛔ Do **not** change this. It is intentional architecture.
⛔ Do **not** write tests that hardcode uppercase or lowercase DATATYPE strings.
Use case-portable comparisons:
```snobol4
dPATTERN = REPLACE(DATATYPE(LEN(1)), &LCASE, &UCASE)
...
IDENT(REPLACE(DATATYPE(x), &LCASE, &UCASE), dPATTERN)  :S(ok)F(fail)
```
Any `.ref` file or driver that hardcodes `'PATTERN'`, `'STRING'`, `'INTEGER'` etc.
in a DATATYPE comparison is **invalid** and must be rewritten before it can pass.

---

## Handoff sequence

The sequence is always: commit → push → confirm hash → THEN say handoff is done.

---

## SPITBOL oracle — always run with -b flag

Always invoke SPITBOL as:
```bash
/home/claude/x64/bin/sbl -b file.sno
```

`-b` suppresses the version/date banner. Never omit it.

SPITBOL `-f` (case-sensitive) is broken in v4.0f x86-64: causes "No END statement found".
Use CSNOBOL4 `-bf` for programs requiring case-sensitive labels (double-function trick).
See: **Case sensitivity — always run case-sensitive** section below.

---

## NRETURN functions — do not assign return value when called via *fn()

When a function is called via `*fn()` in a pattern (indirect call), assigning
to the function name triggers SPITBOL error 021 ("function called by name
returned a value"). Use a separate dummy variable or omit the assignment:

```snobol4
* WRONG — triggers error 021 when called as *push_list(v):
push_list   dummy = stk_push_frame(v)
            push_list = .dummy        :(NRETURN)

* RIGHT — used after . operator: (word . tag) . *push_list(tag)
push_list   dummy = stk_push_frame(v)
            push_list = .dummy        :(NRETURN)
```

Actually: assigning to the function name IS required when called via `. *fn()`
(the dot-star form) because `.` needs a NAME result. Use `.dummy` as the return.
Error 021 only triggers if the function is called as a bare `*fn()` without `.`.
Safe form: always use `(epsilon . *fn())` or `(pat . tag) . *fn(tag)`.

---

## Case sensitivity — always run case-sensitive

**Always use case-sensitive mode for both oracles.**

### CSNOBOL4 — use `-bf` always
```bash
/home/claude/csnobol4/snobol4 -bf file.sno
```
`-b` suppresses banner. `-f` toggles folding OFF → case-sensitive.
Default is case-insensitive (fold to upper). Always override with `-f`.

### SPITBOL x64 — `-f` is broken in v4.0f
`-f` (don't fold) causes "No END statement found" on all files in SPITBOL x64 v4.0f.
**Workaround:** SPITBOL cannot be used case-sensitively with this build.
Use CSNOBOL4 `-bf` as the case-sensitive oracle.
Use SPITBOL `-b` (no `-f`) only for programs that do not require case-sensitive labels.

### Always uppercase END
SNOBOL4 `END` statement must always be uppercase regardless of oracle or flag.
```snobol4
END          ← correct
end          ← never
End          ← never
```
This applies in all .sno files, all dialects, always.

### Double-function trick requires case-sensitive mode
The pattern:
```snobol4
               DEFINE('push_list(v)')
               DEFINE('Push_list(vs)')                      :(push_list_end)
push_list      dummy          =  stk_push_frame(v)
               push_list      =  .dummy                     :(NRETURN)
Push_list      Push_list      =  EVAL("epsilon . *push_list(" vs ")")  :(RETURN)
push_list_end
```
`push_list` and `Push_list` are distinct labels only under case-sensitive mode.
Run these programs with CSNOBOL4 `-bf`. Never with SPITBOL (broken `-f`).
