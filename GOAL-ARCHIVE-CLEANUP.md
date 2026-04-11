# GOAL-ARCHIVE-CLEANUP — Clean the Archive

**Repo:** .github (archive/ folder only)
**Catch phrase:** "clean the archive"
**Done when:** all content extracted into live GOAL/REPO/ARCH files deleted from archive/

## Already done (do not repeat)

- ✅ S-1: `git rm` 6 superseded MILESTONE files (SS-BLOCK-FORWARD, SS-BLOCK-BACKWARD, SS-MONITOR, NET-BEAUTY-19, NET-BEAUTY-SELF, NET-SNIPPET-FACTORY)
- ✅ S-2: `git rm` 3 superseded REPO files (REPO-one4all, REPO-snobol4dotnet, REPO-snobol4jvm)
- ✅ S-3: Removed Gap 1/2/3 sections + Implementation order table from `MILESTONE-SN4X86-SCRIP-TRACE.md` (lines 48-222 deleted)
- ✅ S-4: Removed BP-1 through BP-5 from `MILESTONE-SN4X86-BEAUTY-PREREQS.md` (lines 74-239 deleted)
- ✅ S-5: Removed M-NET-OPT-CACHE/EMIT/FULL rows + D-217/218/219 sprint rows from `MILESTONE-NET-SNOBOL4.md`

## Steps remaining

---

### S-6 — archive/SESSION-silly-snobol4.md

Extracted into: `ARCH-SILLY.md` and `REPO-one4all.md`

Delete these sections (exact line numbers as of last check — verify with grep before cutting):

```bash
# Verify current line numbers first:
grep -n "^### What this is\|^### Architecture\|^### Naming conv\|^### Build (2026\|^### Cherry-picks\|^### Build command — NO\|^### Platform layer\|^### Milestone seq\|^### sil_data_init\|^### Naming conventions — C trans\|^### Three-way diff method" archive/SESSION-silly-snobol4.md
```

Sections to delete:
- `### What this is (2026-04-06)` through end of that block (~lines 11-26) → in ARCH-SILLY.md
- `### Architecture (2026-04-06)` through end (~lines 42-61) → in ARCH-SILLY.md
- `### Naming conventions (2026-04-06)` through end (~lines 27-41) → in ARCH-SILLY.md
- `### Cherry-picks from one4all (2026-04-06)` through end (~lines 62-75) → in REPO-one4all.md
- `### Build (2026-04-06)` — the build command block (~lines 76-83) → in REPO-one4all.md
- `### Build command — NO -m32` (~lines 167-173) → in REPO-one4all.md
- `### Naming conventions — C translation rules (2026-04-06)` (~lines 202-212) → in ARCH-SILLY.md
- `### Three-way diff method` (~lines 268-305) → in ARCH-SILLY.md

Keep: Platform layer (SS-19), Milestone sequence, sil_data_init status, M-SS-DIFF punch-list, M-SS-DIFF-RECHECK watermark, handoff rule, §NOW — these are historical session state not extracted.

```bash
cd /home/claude/.github
# Edit archive/SESSION-silly-snobol4.md — delete the sections listed above
git add archive/SESSION-silly-snobol4.md
git commit -m "archive-cleanup S-6: remove extracted sections from SESSION-silly-snobol4"
git pull --rebase origin main && git push
```

---

### S-7 — archive/SESSION-snobol4-net.md

Extracted into: `REPO-snobol4dotnet.md`

```bash
grep -n "^## §BUILD\|^## §TEST\|^## §KEY FILES\|^## §SUBSYSTEMS\|^## §NOW" archive/SESSION-snobol4-net.md
```

Delete:
- `## §BUILD` section (lines ~23-50) → in REPO-snobol4dotnet.md
- `## §TEST` section (lines ~51-67) → in REPO-snobol4dotnet.md
- `## §KEY FILES` table (lines ~68-90) → in REPO-snobol4dotnet.md

Keep: §SUBSYSTEMS, §NOW, everything after §NOW — session state not extracted.

```bash
git add archive/SESSION-snobol4-net.md
git commit -m "archive-cleanup S-7: remove §BUILD §TEST §KEY FILES from SESSION-snobol4-net"
git pull --rebase origin main && git push
```

---

### S-8 — archive/SESSION-snobol4-x64.md

Extracted into: `REPO-one4all.md` and `ARCH-SNOBOL4.md`

```bash
grep -n "^## Key files\|^## §NOW" archive/SESSION-snobol4-x64.md
```

Delete:
- `## Key files` table (~lines 248-262) → in REPO-one4all.md

Keep: all §INFO sections (tool paths, sprint notes, bug findings) — session history not extracted. Keep §NOW.

```bash
git add archive/SESSION-snobol4-x64.md
git commit -m "archive-cleanup S-8: remove Key files table from SESSION-snobol4-x64"
git pull --rebase origin main && git push
```

---

### S-9 — archive/SETUP-tools.md

Extracted into: `REPO-one4all.md`

```bash
grep -n "^## Backend req\|^## Combination matrix\|^## Always req\|^## Rebus frontend\|^## Frontend oracle" archive/SETUP-tools.md
```

Delete:
- `## Backend requirements` table → in REPO-one4all.md
- `## Combination matrix` table → in REPO-one4all.md

Keep: `## Always required`, `## Rebus frontend only`, `## Frontend oracle requirements` — referenced by SESSION_SETUP.sh logic.

```bash
git add archive/SETUP-tools.md
git commit -m "archive-cleanup S-9: remove backend requirements + combination matrix from SETUP-tools"
git pull --rebase origin main && git push
```

---

### S-10 — archive/IR.md

Extracted into: `ARCH-IR.md`

```bash
grep -n "^## What It Is\|^## EXPR_t\|^## EKind\|^## STMT_t\|^## Five phases\|^## SM_Program\|^## The Five" archive/IR.md
```

Delete:
- `## What It Is` section → in ARCH-IR.md
- `## EXPR_t` section (struct + accessor macros) → in ARCH-IR.md
- `## EKind` table → in ARCH-IR.md
- `## STMT_t` section → in ARCH-IR.md
- Five phases table → in ARCH-IR.md

Keep: anything beyond the five phases table — lower-level SM_Program detail not yet extracted.

```bash
git add archive/IR.md
git commit -m "archive-cleanup S-10: remove EXPR_t/EKind/STMT_t/five-phases from IR.md (moved to ARCH-IR)"
git pull --rebase origin main && git push
```

---

### S-11a — archive/BB-GEN-X86-BIN.md

Extracted into: `ARCH-x86.md` (ABI section)

```bash
grep -n "^## ABI\|^### ABI\|rdi.*entry\|esi.*alpha\|r10.*scratch\|Prologue.*mov" archive/BB-GEN-X86-BIN.md | head -10
```

Delete the ABI block (inline blob ABI description) → in ARCH-x86.md

```bash
git add archive/BB-GEN-X86-BIN.md
git commit -m "archive-cleanup S-11a: remove ABI section from BB-GEN-X86-BIN (moved to ARCH-x86)"
git pull --rebase origin main && git push
```

---

### S-11b — archive/SCRIP-UNIFIED.md

Extracted into: `ARCH-x86.md` (scrip modes table)

```bash
grep -n "^## Modes\|^| --interp\|^| --gen\|scrip.*mode\|three modes" archive/SCRIP-UNIFIED.md | head -10
```

Delete the scrip modes table → in ARCH-x86.md

```bash
git add archive/SCRIP-UNIFIED.md
git commit -m "archive-cleanup S-11b: remove scrip modes table from SCRIP-UNIFIED (moved to ARCH-x86)"
git pull --rebase origin main && git push
```

---

### S-12 — Final audit

```bash
# Check no live content duplicated across archive/ and live files
# Spot-check key terms that appear in live files:
grep -rl "set_and_trace\|GOAL-\|## Session Start\|watermark 6749\|watermark 6438" archive/ | head -20
```

For any hits: read the context, determine if it's duplication of live content, delete if so.

```bash
git add -A
git commit -m "archive-cleanup S-12: final audit, remove remaining duplicates"
git pull --rebase origin main && git push
```

## Rules

- Verify line numbers with grep before every delete — line numbers shift after each edit.
- Never delete content that was NOT extracted into the new system.
- One commit per step. Push after each commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
