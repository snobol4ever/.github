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
**HEAD:** `9790efe` B-246 (asm-t2)
**Milestone:** M-T2-RECUR ✅ → M-T2-CORPUS (next)
**Invariants:** 99/106 ASM corpus (064 NASM_FAIL + word1-4/cross/wordcount)

**⚡ CRITICAL NEXT ACTION — Session B-247:**

```bash
cd /home/claude/snobol4x && git checkout asm-t2
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-t2   # HEAD should be B-246
export INC=/home/claude/snobol4corpus/programs/inc
export CORPUS=/home/claude/snobol4corpus/crosscheck

# Invariant check first:
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # expect 99/106

# Remaining failures:
# - 064_capture_conditional: NASM_FAIL — investigate generated .s
# - word1-4, cross, wordcount: runtime exit 0 (no output)
#   ROOT CAUSE KNOWN: ? operator (no-replacement match) does not advance
#   scan_start on gamma — only applies when s->has_eq == 0 AND pure ? match.
#   The scan_start advance fix in B-246 was reverted because it unconditionally
#   applied to all match stmts, regressing inline patterns.
#   Correct fix: find the flag that distinguishes ? from = in STMT_t, apply
#   scan_start advance only to ? stmts (no subject reassignment).
```

## Last Session Summary

**Session B-246 (2026-03-22) — bref pool, E_CONC left-fold, named-pat r12; 99/106:**
- `bref()`/`bref2()`: rotating pool of 8 buffers — single static `_bref_buf` caused
  `ARB_α r12+32, r12+32` (both args aliased) when two `bref()` calls in one `A()` format
- n-ary `E_CONC`: replaced right-fold with inline left-fold (push/pop per child);
  avoids slot aliasing at arbitrary concat depth
- 2-child `E_CONC` generic fallback: push/pop instead of `conc_tmp0` (.bss slot
  clobbered by recursive right-side evaluation)
- `emit_named_ref`: `lea r12, [rel box_NAME_data_template]` before α and β jumps
  for non-function named patterns — fixes r12 undefined on entry to pattern body
- Fixed: 022_concat_multipart, 055_pat_concat_seq, 053_pat_alt_commit
- 99/106 corpus (up from 96); `9790efe` B-246 pushed
- Diagnosed word1-4/cross/wordcount: ? operator gamma path never advances scan_start
  (only APPLY_REPL_SPLICE does); fix attempted but reverted (regressed 26 tests);
  correct fix needs flag distinguishing ? stmt from = stmt in STMT_t

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
