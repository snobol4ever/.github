# GOAL-ARCHIVE-CLEANUP — Clean the Archive

**Repo:** .github (archive/ folder only)
**Done when:** all content that was extracted into live GOAL/REPO/ARCH files has been
deleted from its source location in archive/. No live content duplicated in archive/.

## What was extracted and where it came from

| Extracted into | Source in archive/ | What to delete |
|---------------|-------------------|----------------|
| `GOAL-SILLY-SWEEP-FORWARD.md` | `archive/MILESTONE-SS-BLOCK-FORWARD.md` | Entire file — fully superseded |
| `GOAL-SILLY-SWEEP-BACKWARD.md` | `archive/MILESTONE-SS-BLOCK-BACKWARD.md` | Entire file — fully superseded |
| `GOAL-SILLY-SYNC-MONITOR.md` | `archive/MILESTONE-SS-MONITOR.md` | Entire file — fully superseded |
| `GOAL-SCRIP-BEAUTY.md` | `archive/MILESTONE-SN4X86-SCRIP-TRACE.md` | Implementation order table (T-0 through T-4) + Gap sections |
| `GOAL-SCRIP-BEAUTY.md` | `archive/MILESTONE-SN4X86-BEAUTY-PREREQS.md` | BP-1 through BP-5 step descriptions |
| `GOAL-NET-BEAUTY-19.md` | `archive/MILESTONE-NET-BEAUTY-19.md` | Entire file — fully superseded |
| `GOAL-NET-BEAUTY-SELF.md` | `archive/MILESTONE-NET-BEAUTY-SELF.md` | Entire file — fully superseded |
| `GOAL-NET-SNIPPETS.md` | `archive/MILESTONE-NET-SNIPPET-FACTORY.md` | Entire file — fully superseded |
| `GOAL-NET-OPTIMIZE.md` | `archive/MILESTONE-NET-SNOBOL4.md` | M-NET-OPT-* rows from milestone chain table |
| `REPO-one4all.md` | `archive/SESSION-silly-snobol4.md` | §INFO build command, §INFO architecture block, §INFO naming conventions |
| `REPO-one4all.md` | `archive/REPO-one4all.md` | §BUILD and §TEST sections |
| `REPO-one4all.md` | `archive/SETUP-tools.md` | Backend requirements table, combination matrix |
| `REPO-snobol4dotnet.md` | `archive/REPO-snobol4dotnet.md` | §BUILD, §TEST, NOW section |
| `REPO-snobol4dotnet.md` | `archive/SESSION-snobol4-net.md` | §BUILD and §TEST sections |
| `REPO-snobol4jvm.md` | `archive/REPO-snobol4jvm.md` | Entire file — fully superseded |
| `ARCH-SILLY.md` | `archive/SESSION-silly-snobol4.md` | §INFO architecture block, naming conventions table |
| `ARCH-SNOBOL4.md` | `archive/SESSION-snobol4-x64.md` | §INFO parser notes, monitor hooks |
| `ARCH-IR.md` | `archive/IR.md` | EXPR_t struct, EKind table, STMT_t struct, five phases table |
| `ARCH-x86.md` | `archive/BB-GEN-X86-BIN.md` | ABI section |
| `ARCH-x86.md` | `archive/SCRIP-UNIFIED.md` | scrip modes table |
| `ARCH-JVM.md` | `archive/REPO-snobol4jvm.md` | Pipeline stages, oracle role section |
| `ARCH-NET.md` | `archive/SESSION-snobol4-net.md` | §KEY FILES table |
| `RULES.md` | `archive/GENERAL-RULES.md` | All rules that were copied verbatim |

## Method

For each row above:
1. Open the archive source file
2. Locate the extracted section
3. Delete that section (or the entire file if marked "fully superseded")
4. Commit with message: `archive-cleanup: remove <what> from <source file>`

For "entire file" deletions: `git rm archive/<filename>`
For partial deletions: edit the file, remove the section, save.

## Steps

- [ ] **S-1** — Delete fully superseded milestone files:
  `git rm archive/MILESTONE-SS-BLOCK-FORWARD.md archive/MILESTONE-SS-BLOCK-BACKWARD.md archive/MILESTONE-SS-MONITOR.md archive/MILESTONE-NET-BEAUTY-19.md archive/MILESTONE-NET-BEAUTY-SELF.md archive/MILESTONE-NET-SNIPPET-FACTORY.md`

- [ ] **S-2** — Delete superseded repo files:
  `git rm archive/REPO-one4all.md archive/REPO-snobol4dotnet.md archive/REPO-snobol4jvm.md`

- [ ] **S-3** — Remove extracted sections from `archive/MILESTONE-SN4X86-SCRIP-TRACE.md`: delete the Implementation order table (T-0 through T-4) and the three Gap sections.

- [ ] **S-4** — Remove extracted sections from `archive/MILESTONE-SN4X86-BEAUTY-PREREQS.md`: delete BP-1 through BP-5 step descriptions.

- [ ] **S-5** — Remove M-NET-OPT-* rows from milestone chain table in `archive/MILESTONE-NET-SNOBOL4.md`.

- [ ] **S-6** — Remove extracted §INFO sections from `archive/SESSION-silly-snobol4.md`: build command block, architecture block, naming conventions table.

- [ ] **S-7** — Remove extracted §BUILD and §TEST sections from `archive/SESSION-snobol4-net.md` and §KEY FILES table.

- [ ] **S-8** — Remove extracted §BUILD, §TEST, NOW section from `archive/SESSION-snobol4-x64.md`.

- [ ] **S-9** — Remove backend requirements table and combination matrix from `archive/SETUP-tools.md`.

- [ ] **S-10** — Remove EXPR_t struct, EKind table, STMT_t struct, five phases table from `archive/IR.md`.

- [ ] **S-11** — Remove ABI section from `archive/BB-GEN-X86-BIN.md`. Remove scrip modes table from `archive/SCRIP-UNIFIED.md`.

- [ ] **S-12** — Audit: scan all remaining archive/ files for any content that duplicates live GOAL/REPO/ARCH files. Delete any found. Gate: no live content duplicated in archive/.

## Rules

- Edit archive/ files carefully — do not delete content that was NOT extracted into the new system.
- Commit after each step. Message: `archive-cleanup: <description>`
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- See RULES.md for full rules.
