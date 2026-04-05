# RULES.md — Mandatory Rules (L3)

Every rule exists because a violation caused real damage. Read section headers first (`grep "^## " RULES.md`), then only sections relevant to your session.

---

## ⛔ LIVE DOC UPDATE — significant clarifications written immediately, consolidated not appended

Claude has no memory between sessions. HQ MD files ARE the memory.

**Rule:** When the human corrects a wrong assumption or clarifies something
architecturally significant — update the appropriate doc IMMEDIATELY.
Not at handoff. Rewrite/consolidate the relevant section. Do not append.

**Threshold:** Only if a future Claude reading the doc would be meaningfully
misled without the update. Passing remarks, tactical decisions, session-specific
findings → SESSIONS_ARCHIVE handoff only.

**ARCH doc size limit — 20KB hard cap per file.**
ARCH docs are read in full during session start. Every KB added is context burned.
- Consolidate: if adding a new section, remove or compress an older one that is now settled.
- Do NOT append brainstorm sections that were useful when being worked out but are now resolved.
- Resolved design questions → one-line summary in the relevant section, not a new section.
- If an ARCH doc exceeds 20KB, trim it before the next handoff. `wc -c ARCH-*.md` at handoff.
- `GENERAL-BYRD-DYNAMIC.md` is currently over-limit (58KB). DYN-20 must trim it to ≤20KB.

**SESSION doc is the context budget:**
Each session type must have a `SESSION-*.md` that is ≤2KB and replaces full ARCH reads.
The SESSION doc says which ARCH sections to grep for which tasks — not cat the whole file.

| What changed | Where it goes |
|---|---|
| Architecture / design insight corrected | Rewrite relevant section in `ARCH-*.md` |
| Process / gate / rule changed | Rewrite relevant section in `RULES.md` |
| NOW table / milestone changed | Update `PLAN.md` NOW row |
| Session finding / tactical detail | `SESSIONS_ARCHIVE.md` handoff only |

**Do not append to ARCH docs speculatively.** If unsure whether something is
significant enough — ask. A doc that grows every session becomes unreadable.

## ⛔ TWO SCRIPTS — SESSION_SETUP.sh then test scripts, every session, no exceptions

**Setup (once per fresh environment) — ALWAYS pass FRONTEND and BACKEND:**
```bash
FRONTEND=snocone BACKEND=x64 TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
```
See `SETUP-tools.md` for the full FRONTEND × BACKEND matrix and what each combination installs/skips.

**⛔ Never omit FRONTEND= and BACKEND=.** Omitting them installs everything (bison, flex, java, mono, swipl, icont, spitbol) — wastes 5–15 min and signals the wrong mental model. The correct switches for each session are in that session's §START block.

**Gate (every session after setup) — runtime invariants ONLY, snobol4_x86 only:**
```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86
```

**⛔ emit-diff (run_emit_check.sh) is RETIRED for all sessions until M-DYN-S1 is complete.**
The emitter is mid-migration to 5-phase `stmt_exec_dyn`. Static inline NASM Byrd box
bodies, named-pattern trampolines, and scan loops are dead code being removed.
Emit-diff pins artifacts of the wrong architecture. Do not run it. Do not chase it.
It will be restored when the emitter stabilizes after M-DYN-S1 lands across all 5
languages × 6 platforms.

**⛔ ALL emit/compiler sessions except DYNAMIC BYRD BOX (snobol4 × x86) are FROZEN.**
No development on JVM, .NET, WASM, JS, Icon, Prolog, Snocone *emitters* until M-DYN-S1
is complete. The only active gate for emit sessions: `snobol4_x86` runtime invariants.

**⛔ INTERPRETER SESSIONS ARE EXEMPT FROM THE FREEZE AND FROM scrip-cc/emit-diff GATES.**
`scrip-interp.c` (DYN-) and `scrip-interp.cs` (NET INTERP) are pure tree-walk interpreters.
They do not invoke scrip-cc, do not emit IL/NASM/JVM, and are not affected by emitter state.
Gate protocol for interpreter sessions:
- **Do NOT run `run_invariants.sh` or `run_emit_check.sh`** — they test the scrip-cc emitter pipeline, which is irrelevant to interpreter work.
- **Gate = broad corpus pass count** for the interpreter under development (e.g. `169p/9f`).
- Run the interpreter's own test harness only (see the session's §TEST block).
- Interpreter regressions are isolated: a failure in scrip-interp.cs never affects scrip-cc or emitters.

**⛔ OWN-BACKEND-ONLY INVARIANT POLICY (all sessions, no exceptions):**
Each session runs invariant cells **only for the backend it owns**. Never install tools
for, or run invariant cells from, a backend you are not working on this session.

| Session type | Invariant cells to run |
|---|---|
| snobol4 × x86 | `snobol4_x86` only |
| snobol4 × wasm | `snobol4_wasm` only |
| snobol4 × jvm | `snobol4_jvm` only |
| snobol4 × net | `snobol4_net` only |
| icon × x86 | `icon_x86` only |
| icon × jvm | `icon_jvm` only |
| icon × wasm | `icon_wasm` only — do NOT run snobol4_wasm, prolog_wasm, or any x86/jvm cells |
| prolog × x86 | `prolog_x86` only |
| prolog × jvm | `prolog_jvm` only |
| prolog × wasm | `prolog_wasm` only — do NOT run snobol4_wasm, icon_wasm, or any x86/jvm cells |
| snocone × x86 | `snobol4_x86` · `snocone_x86` (snocone is additive over snobol4) |
| G-sessions | all active cells — reorg touches all emitters |

Rationale: Each session owns one backend column. Running other backends wastes context,
installs unneeded tools, and adds noise. Cross-session regressions are caught by each
session running its own column. Do not run x86 cells in a WASM session, JVM cells in an
x86 session, etc.

`SESSION_SETUP.sh` does all tool installation: apt packages, source builds (scrip-cc), SnoHarness compile, git identity. **The test scripts do NOT install tools** — they
verify tools are present and exit immediately with a clear message if anything is missing.

**Never pre-check or pre-install tools manually.** SESSION_SETUP.sh is the environment setup.
Never run apt-get or build scrip-cc by hand before a script. Wasting steps pre-checking is
a context burn and signals the wrong mental model.

**⛔ NEVER install bison or flex — not for any session, including Rebus.** `rebus.tab.c`,
`rebus.tab.h`, and `lex.rebus.c` are committed and always current. `scrip-cc` builds from
`make` with no parser-generator tools needed. If you modify `rebus.y` or `rebus.l`
(Rebus-session only), regenerate on your own machine and commit the C files. See RULES.md.
SESSION_SETUP.sh never installs bison/flex.

**⛔ ORACLE: SPITBOL x64 is the sole oracle for all sessions.**
SPITBOL (snobol4ever/x64, installed at `/usr/local/bin/spitbol`) is the authoritative oracle.
CSNOBOL4 is not installed, not used, not needed. Do not attempt to build it.
When deriving `.ref` output for any test: `spitbol -b file.sno > file.ref`.
**DATATYPE exception:** SPITBOL returns lowercase datatype names (`"name"`, `"pattern"`, etc.). one4all returns uppercase (`"NAME"`, `"PATTERN"`). This is intentional per SNOBOL4 spec — see GENERAL-DECISIONS.md D-003.
Note: `.ref` files are pre-baked in corpus — SPITBOL is not required to run the gate.

---

## ⛔ SETUP DOES NOT RUN TESTS — Test scripts do not install

`SESSION_SETUP.sh` — installs, builds, clones. No tests.
`run_emit_check.sh` — emits and diffs. Verifies tools, does NOT install.
`run_invariants.sh` — runs 7-cell matrix. Verifies tools, does NOT install.

If a test script reports a missing tool, re-run `SESSION_SETUP.sh`. Do not install manually.
```
tail -80 /home/claude/.github/SESSIONS_ARCHIVE.md   # your handoff
cat /home/claude/.github/RULES.md                   # this file
cat /home/claude/.github/PLAN.md                    # NOW table + next milestone
cat /home/claude/.github/GRAND_MASTER_REORG.md      # phase detail
```


## ⛔ TOKEN — Never write or display the token

Token is provided once by Lon at session start. Use in shell only. Never on disk, never in chat, never in commit messages, never in handoff summaries. Write `TOKEN_SEE_LON` as placeholder in any file that references it. If token appears in a commit: notify Lon immediately — rotation and history rewriting are Lon's decisions only.

**Bootstrap blocks in SESSIONS_ARCHIVE.md and all other HQ docs must use `TOKEN_SEE_LON` as the placeholder — never the real token. This applies to every `git clone https://...@github.com/...` line without exception. GitHub Push Protection will block the push and force a rewrite if a real PAT is committed.**

---

## ⛔ SESSION NUMBERS — Globally unique per session type

Format: `PREFIX-NNN` where NNN increments within that namespace only.

| Session type | Prefix | Owns in PLAN.md NOW |
|---|---|---|
| Grand Master Reorg | `G` | **GRAND MASTER REORG** row |
| TINY backend (ASM) | `B` | **TINY backend** row |
| TINY JVM backend | `J` | **TINY JVM** row |
| TINY NET backend | `N` | **TINY NET** row |
| TINY frontend | `F` | **TINY frontend** row |
| DOTNET | `D` | **DOTNET** row |
| README | `R` | **README** row |
| ICON frontend | `I` | **ICON frontend** row |
| Prolog JVM | `PJ` | **Prolog JVM** row |
| Icon JVM | `IJ` | **Icon JVM** row |
| Scrip Demo | `SD` | **Scrip Demo** row |

Each session increments only its own counter. Commit messages: `PJ-5: M-PJ-BACKTRACK — fix suffix_fail`.

**⚠ ICON vs IJ DISAMBIGUATION — common source of error:**
- `"ICON frontend"` alone = I-session (x86 backend, `icon_emit.c`)
- `"ICON frontend with JVM backend"` = IJ-session (`icon_emit_jvm.c`, Jasmin)
- `"Icon JVM"` = IJ-session
- The phrase "JVM backend" is the deciding signal. When in doubt: check which emitter file is active. `icon_emit.c` → I. `icon_emit_jvm.c` → IJ.
- **HQ MD files are the only reliable memory.** Always read the relevant SESSION doc (`SESSION-icon-x64.md` vs `SESSION-icon-jvm.md`) to confirm session type before doing any work.

---

## ⛔ CONCURRENT SESSIONS — Rebase before every .github push

Four sessions may push `.github` simultaneously. Always:
```bash
cd /home/claude/.github
git pull --rebase origin main   # immediately before push
git push
```
Each session edits only its own row in PLAN.md NOW and its own L3 docs. **Never `git push --force` on .github.**

---

## ⛔ HANDOFF — Push must succeed before handoff is declared

A committed-but-not-pushed session lives only on a throwaway container — it is a lost session. Never say "handoff complete" until `git log origin/main --oneline -1` shows your commit hash on the remote. If push fails for any reason: fix it. Ask for credentials if needed. Do not declare done and move on.

End-of-session checklist (in order):
1. **Update `SESSION-<frontend>-<backend>.md` §NOW** — set sprint to NEXT session number, update HEAD hashes, rewrite first-actions for the next session. ⛔ THIS IS MANDATORY. A stale §NOW causes the next session to work on the wrong milestone. SESSIONS_ARCHIVE has the plan; §NOW in the SESSION doc must match it exactly.
2. **Append to `SESSION-<frontend>-<backend>.md` §INFO** any invariants stated mid-session (tool locations, oracle setup, don't-do-X, baselines). §INFO is append-only inside the SESSION doc. This is how facts survive across sessions.
3. Update PLAN.md NOW table row (your row only).
4. If milestone fired: move its row to MILESTONE_ARCHIVE.md.
5. `git add -A && git commit && git push` every touched repo.
6. `git pull --rebase origin main` on .github, then commit + push .github last.
7. Append session entry to SESSIONS_ARCHIVE.md.

---

## ⛔ ARTIFACT REFRESH — After every milestone fix, regenerate affected artifacts

**The design:** scrip-cc writes generated output (`.s`, `.j`, `.il`, `.js`, `.wat`) **side by side next to the source** when invoked without `-o`. `foo/bar.sno` → `foo/bar.s`. Every clean compile drops its output automatically. Commit corpus after any session that changes an emitter — git sweeps up changed generated files naturally.

**Promotion path:** compile clean → `.s` appears in corpus. Run passes → it is already an emit-diff oracle (emit-diff just compares committed vs fresh). Once all files are current, emit-diff can resume immediately with zero new work.

**At handoff — mandatory for any session that touches an emitter:**
```bash
CELLS=snobol4_x86 CORPUS=/home/claude/corpus bash test/run_emit_check.sh --update
cd /home/claude/corpus && git add -A && git commit -m "regen: update generated artifacts alongside sources"
```
Substitute `CELLS=` for the session's backend. Omit `CELLS=` to regen all backends.

**Rule:** Only non-empty output is kept — compile errors leave no file, stale oracles are never created. If a previously-compiling file now fails, delete its generated artifact from corpus and commit.

**`artifacts/` samples:** regen commands in `artifacts/README.md` — one block per frontend/backend. Run the relevant block, verify, commit.

**At every milestone fire:** run the full demo harness (`bash demo/scrip/run_demo.sh demo/scrip/demoN/`) for all demos that touch the affected system.

---

## ⛔ GIT IDENTITY — Always commit as Lon, never as Claude

**Every commit in every repo must be authored as Lon Cherryholmes.**
Claude is a tool, not an author. Never commit as `claude@anywhere.com`.

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

Set this in every repo at session start, before the first commit. This is not optional.
Violations require a history rewrite (`git filter-repo`) and force-push — expensive to fix.

**Wrong (never use):** `claude@anthropic.com`, `claude@snobol4ever.dev`, `SESSION@snobol4ever.dev`,
`session@snobol4ever`, `bot@snobol4ever.dev`, or any other Claude/session/bot address.

**Right:** `lcherryh@yahoo.com` / `LCherryholmes` — always, every repo, every session.

---

## ⛔ BYRD BOXES — two valid uses; emitter vs interpreter are different sessions

**Emitter sessions (x86/JVM/.NET emit):** Byrd-box ports (α/β/γ/ω) are emitted as labels + gotos — never as an interpreter loop. Any logic that "runs" IR nodes at emit-time is wrong. Emit code; don't execute it. Use `mock_engine.c` only.

**Interpreter sessions (scrip-interp.c / scrip-interp.cs):** Byrd boxes ARE executed at runtime as C/MSIL function calls. `ByrdBoxExecutor` (MSIL, in `boxes.dll`) and `stmt_exec_dyn` (C) are the trampolines. `bb_*.cs` are oracle/reference only — the canonical runtime boxes are `bb_*.il` assembled into `boxes.dll`. This is correct and intentional — the interpreter IS the runtime driver for the IByrdBox graph.

**Do not confuse the two.** Session type determines which model applies:
- DYN- session (snobol4 × x86 scrip-interp) → C boxes executed via stmt_exec_dyn
- NET INTERP session (scrip-interp.cs) → **MSIL `IByrdBox` objects from `boxes.dll`** (assembled from `bb_*.il` via `ilasm`). `bb_*.cs` are oracle/reference ONLY — never referenced by the interpreter build. `scrip-interp.csproj` must reference `boxes.dll` directly, NOT `bb_boxes.csproj`.
- All emit sessions → labels+gotos, no execution at emit-time

---

## ⛔ THREE-AXIS ORIENTATION — Repo × Frontend × Backend

Every session is defined by exactly two values: **Frontend × Backend**.
That pair determines the SESSION doc, the sprint sequence, and all the work.
There is no other session identity — no nicknames, no prefixes like "DYN" or "B".
**One track per frontend × backend combo.** One long sequence of sprints.
Lon rearranges priority by reordering the PLAN.md NOW table — not by switching session types.
Sprint prefixes are for numbering only; they do not define separate tracks.

**Session start — four steps (mandatory, in order):**
1. `tail -80 SESSIONS_ARCHIVE.md` — your handoff. Do this FIRST.
2. Scan RULES.md headers: `grep "^## " RULES.md` — then `cat` only sections relevant to your session. Never `cat` the whole file.
3. Read `PLAN.md` — NOW table, confirm next milestone.
4. Read your `SESSION-<frontend>-<backend>.md` — **§INFO first** (invariants), then **§NOW** (sprint state).

## ⛔ §NOW STALENESS — fix before any work

Compare the sprint number in `SESSION-*.md §NOW` against the sprint in your `SESSIONS_ARCHIVE` handoff.
If they differ, the SESSION doc was not updated at last handoff — **the SESSIONS_ARCHIVE handoff is authoritative**.
Rewrite `§NOW` from the SESSIONS_ARCHIVE before doing any work.

**§NOW and sprint state** live in SESSION-*.md only. Never in PLAN.md, RULES.md, or FRONTEND-*/BACKEND-* docs. SESSIONS_ARCHIVE.md is append-only.

## ⛔ SESSION ROUTING — one rule

**frontend × backend → `SESSION-<frontend>-<backend>.md`**

Frontends: `snobol4`, `snocone`, `rebus`, `icon`, `prolog`, `scrip`
Backends: `c`, `x64`, `jvm`, `net`, `js`, `wasm`

The human will say which frontend and which backend. Read the matching SESSION doc. That is all.

## ⛔ SESSIONS_ARCHIVE.md — APPEND ONLY, NEVER PRUNE

`SESSIONS_ARCHIVE.md` is a permanent historical record. Its size does not matter.
**Never** delete, truncate, move, or "archive" entries from it. Never suggest pruning it.
Only ever append to it. A large SESSIONS_ARCHIVE.md is correct and expected.

Files that ARE pruned when they grow too large:
- `PLAN.md` — 3KB max. Session content belongs in SESSIONS_ARCHIVE, not PLAN.md.
- `RULES.md` — trim war-story context, keep only the rule itself.
- `GRAND_MASTER_REORG.md` — completed phase detail moves to MILESTONE_ARCHIVE.md.

---

## ⛔ NOW TABLE ROW FORMAT — Three fields only

Each row in PLAN.md NOW table: `| **Session name** | sprint-id — milestone-status | HEAD-hash session-id | Next milestone |`

No narrative beyond a short status phrase. No substeps. No bullet points. One row per session type, owned by that session exclusively.

---

## ⛔ REPO PATHS — Canonical clone locations

```
/home/claude/one4all/        ← compiler + backends (main working repo)
/home/claude/.github/         ← HQ docs
/home/claude/corpus/   ← test corpus (clone if needed)
/home/claude/snobol4jvm/      ← JVM/Clojure backend (clone if needed)
```
Always clone fresh at session start. Never use symlinks. First action is always clone.

---

## ⛔ TEST INVARIANT — Confirm before any work

**Required baseline — 3×4 matrix (7 active x86/JVM/.NET, snobol4_wasm active, others not-yet-implemented):**

| | x86 | JVM | .NET | WASM |
|--|-----|-----|------|------|
| SNOBOL4 | `106/106` | `94p/32f` | `108p/2f` | `9/9` |
| Icon | `94p/164f` | `173p/44f` | SKIP (not impl) | SKIP (not impl) |
| Prolog | `13p/94f` | `106p/1f` | SKIP (not impl) | `0/0` (new — PW session) |

All failure counts above are **pre-existing, non-regressions** (confirmed G-9 s22). Any new
failure not in this table is a regression — fix before pushing.

**Session start:** run the full 7-cell suite once and confirm counts match the table.
**Mid-session (after each milestone commit):** run only the targeted backend column
(see gate section). Do not run the full suite mid-session — it is slow and unnecessary.
**Session end:** run the full 7-cell suite once more and confirm no regressions.

- **Icon .NET / Prolog .NET:** not yet implemented — always SKIP.
- **G-sessions always run all seven active invariants at START and END** — the reorg touches all emitters.

**Backend name:** The native backend is **x86** (not "ASM" or "x64 ASM"). Emitter file stays `emit_x64.c`; folder stays `backend/x64/`; the human name is x86.

---

## ⛔ FRONTEND/BACKEND SEPARATION — Emitter gaps queue via .xfail

When the frontend produces an IR node the backend cannot yet emit, do not add a special-case silent skip. Add an `.xfail` entry so the gap is visible and tracked. Fix the emitter gap in a dedicated milestone.

---

*RULES.md = L3 reference. ~10 rules, each ≤10 lines. No session playbooks. No artifact status tables. No war stories beyond one-line root-cause citations.*

---

## ⛔ HQ DOCS ARE THE ONLY RELIABLE MEMORY — Verify before asserting

Before making any factual claim about how a component works — lexer behaviour,
semicolons, calling conventions, corpus format, file layout, build commands — check
the relevant HQ doc first. Do NOT reason from training data or session memory.
Training data is wrong. Session memory drifts. HQ docs are ground truth.

**Failure mode:** Claude asserted Icon/JCON uses implicit semicolons (standard Icon
behaviour). Our lexer explicitly does NOT — "No auto-semicolon insertion" is line 4
of `icon_lex.c` and documented in RULES.md and MISC-ICON-JCON.md. This caused
wasted session time diagnosing a non-problem.

**Rule:** When in doubt about ANY system property: `grep` the relevant HQ doc first.
If the doc doesn't cover it, check the source. Never guess and assert.

---

*Icon semicolon rules → `MISC-ICON-JCON.md §Auto-semicolon`. JVM null-coerce rules → `SESSION-icon-jvm.md §JVM-NULL`.*

---

## ⚠️ Known deferred fragility: E_SEQ vs E_CONCAT in SNOBOL4 frontend

**M-DYN-SEQ** tracks this. Short version:

SNOBOL4 juxtaposition (`A B C`) is polymorphic at runtime — string concat OR
pattern sequence depending on operand types. The parser currently guesses context
using `fixup_val_tree`. This is **wrong** for variables holding DT_P.

**Do not add new uses of `fixup_val_tree`** or rely on `E_CONCAT` being reliably
"always string" in the SNOBOL4 frontend. In pattern context (`emit_pat_to_descr`)
both `E_SEQ` and `E_CONCAT` produce `pat_cat` — correct. In value context
(`emit_expr`), `E_CONCAT` calls `stmt_concat` which will break if an operand is DT_P.

Fix is `stmt_seq()` runtime dispatcher. See `GENERAL-DECISIONS.md D-010` and
`GENERAL-BYRD-DYNAMIC.md M-DYN-SEQ`.

## ⛔ §INFO — session invariants live in SESSION doc, not a separate file

Each `SESSION-<frontend>-<backend>.md` has a `## ⛔ §INFO` section at the top.
- **Read §INFO before touching anything** — tool locations, oracle build steps, sweep baselines, don't-do-X warnings.
- **Append to §INFO mid-session** when Lon states any operational fact. Write immediately. Commit at handoff.
- §INFO is append-only. Date every entry. Never re-derive what §INFO already records.
- Never rebuild a tool from scratch if §INFO says where the patches live.

"Update HQ" = append the new fact to §INFO in the SESSION doc + commit `.github`.

## ⛔ v311.sil — consult before asserting any syntab sequence

When the correct STREAM table sequence for any parser procedure is unknown or disputed,
**read v311.sil first**. It is the authoritative SIL source. CSNOBOL4 `syn.c` and
`syn_init.h` are the authoritative C translation. Both are on disk every session:

```bash
/home/claude/snobol4-2.3.3/v311.sil        # SIL source — procedure bodies
/home/claude/snobol4-2.3.3/syn.c           # chrs[] tables — authoritative bytes
/home/claude/snobol4-2.3.3/syn_init.h      # action assignments (put/act/go)
```

Usage pattern:
```bash
grep -n "PROCNAME\|TABLENAME" /home/claude/snobol4-2.3.3/v311.sil
sed -n '<start>,<end>p' /home/claude/snobol4-2.3.3/v311.sil
grep -n "BEGIN TABLENAME\|END TABLENAME" /home/claude/snobol4-2.3.3/syn.c
```

**Do not guess table byte values or action sequences from memory.**
The chrs[] arrays are authoritative and must not be modified in sno4parse.
All fixes are in code logic. v311.sil gives the procedure flow; syn.c gives the bytes.

## ⛔ TWO-WAY MONITOR — scripts are checked in beside the csnobol4 patches

The two-way STREAM trace oracle (sno4parse vs CSNOBOL4) uses scripts checked in at:

```
one4all/csnobol4/dyn89_sweep.sh   — sweep all corpus/programs/snobol4/ files
one4all/csnobol4/stream.c         — CSNOBOL4 patch: emits SNO_TRACE to /tmp/sno_csno.trace
one4all/csnobol4/main.c           — CSNOBOL4 patch: opens trace file, sets flag
one4all/csnobol4/README.md        — how to apply, build, and run
```

**Standard two-way MONITOR workflow for hard bugs:**
```bash
# 1. Run CSNOBOL4 oracle (with trace)
SNO_TRACE=1 /home/claude/snobol4-2.3.3/snobol4 /tmp/failing.sno 2>/dev/null
# trace → /tmp/sno_csno.trace

# 2. Run sno4parse (with trace)
SNO_TRACE=1 /home/claude/sno4parse /tmp/failing.sno 2>/tmp/sn.trace

# 3. Diff — first divergence is the root cause
diff /tmp/sno_csno.trace /tmp/sn.trace | head -30

# 4. Sweep
bash /home/claude/one4all/csnobol4/dyn89_sweep.sh
```

**Correctness criterion (from §INFO):**
- CS succeeds + sno4parse succeeds → OK
- CS errors + sno4parse errors → OK
- CS succeeds + sno4parse errors → BUG
- CS errors + sno4parse succeeds → BUG (too permissive)
