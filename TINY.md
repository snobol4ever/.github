# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `t2-impl` — M-T2-CORPUS
**HEAD:** `66b7148` B-245 (asm-t2)
**Milestone:** M-T2-RECUR ✅ → M-T2-CORPUS (next)
**Invariants:** 96/106 ASM corpus (9 known failures + 053 runtime)

**⚡ CRITICAL NEXT ACTION — Session B-245:**

```bash
cd /home/claude/snobol4x && git checkout asm-t2
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-t2   # HEAD should be B-244
export INC=/home/claude/snobol4corpus/programs/inc
export CORPUS=/home/claude/snobol4corpus/crosscheck

# Invariant check first:
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # expect 96/106

# M-T2-CORPUS: 106/106 ASM corpus under T2 — 9 known failures fixed by construction.
# The 9 known failures are: 022, 055, 064, cross, word1-4, wordcount.
# Investigate each: run individually with STOP_ON_FAIL=1 FILTER=022 to get actual error.
# Goal: no per-bug patches — T2 per-invocation DATA should fix them by construction.
# Then run: bash test/crosscheck/run_crosscheck_asm_corpus.sh  # expect 106/106
```

## Last Session Summary

**Session B-245 (2026-03-21) — T2 codename removed from all source:**
- `t2_alloc/t2_free/t2_mprotect_*` → `blk_alloc/blk_free/blk_mprotect_*`
- `t2_relocate/t2_reloc_kind/t2_reloc_entry/T2_RELOC_*` → `blk_relocate/blk_reloc_kind/blk_reloc_entry/BLK_RELOC_*`
- `emit_t2_reloc_tables()` → `emit_blk_reloc_tables()`
- Files: `t2_alloc.c/h` → `blk_alloc.c/h`; `t2_reloc.c/h` → `blk_reloc.c/h` (old files deleted)
- `test/t2/` → `test/blk/`; test files renamed
- All "T2:" / "Technique 2" comments scrubbed; section headers → "BOX RELOCATION TABLES" / "BOX DATA TEMPLATES"
- 96/106 invariant holds; `66b7148` B-245 pushed

## Active Milestones

| ID | Status |
|----|--------|
| M-T2-INVOKE     | ✅ `1cf8a0a` B-243 |
| M-T2-RECUR      | ✅ `1cf8a0a` B-244 |
| M-T2-CORPUS     | ❌ next |
| M-T2-FULL       | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `asm-t2` | M-T2-INVOKE |
| J-next | `jvm-t2` | TBD |
| N-next | `net-t2` | TBD |
| F-next | `main`   | TBD |
