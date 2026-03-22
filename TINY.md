# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-t2` — M-T2-FULL
**HEAD:** `50a1ad0` B-247 (asm-t2)
**Milestone:** M-T2-CORPUS ✅ → M-T2-FULL (next)
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — Session B-248:**

```bash
cd /home/claude/snobol4x && git checkout asm-t2
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-t2   # HEAD should be B-247
export INC=/home/claude/snobol4corpus/programs/inc
export CORPUS=/home/claude/snobol4corpus/crosscheck

# Invariant check first:
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # expect 106/106

# M-T2-FULL trigger: read BACKEND-X64.md for definition
```

## Last Session Summary

**Session B-247 (2026-03-22) — M-T2-CORPUS: 106/106 ALL PASS:**
- Fix 1: `scan_start` advance moved before `SET_CAPTURE` loop in gamma path for `?` stmts.
  `SET_CAPTURE` calls `stmt_set_capture` (C ABI), trashing `rax`; advance was emitted after,
  so `scan_start` got garbage and `?` matches never advanced position → infinite output.
- Fix 2: `fail_target` for all 5 assignment branches (E_VART/KW, E_DOL/INDR, E_IDX, E_FNC
  field, E_FNC ITEM) now checks `is_special_goto(tgt_f)` in addition to `id_f >= 0`.
  `:F(END)` was silently falling through to next statement (END not in label registry).
- Fix 3: omega scan_fail for pure-pattern `:F(END)` stmts emitted `L_unk_-1` (invalid NASM
  label). Fix: when `scan_fail_tgt` is a special goto and no trampoline needed, use
  `L_SNO_END` directly. Resolves 064_capture_conditional NASM_FAIL.
- Harness: `run_crosscheck_asm_corpus.sh` now feeds `.input` to stdin; `/dev/null` otherwise.
  Previous behaviour blocked on terminal read → misreported as timeout/`[runtime exit 0]`.
- `50a1ad0` B-247 pushed; artifacts regenerated (claws5: 3 undef β labels unchanged).
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
| M-T2-CORPUS     | ✅ `50a1ad0` B-247 |
| M-T2-FULL       | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `asm-t2` | M-T2-INVOKE |
| J-next | `jvm-t2` | TBD |
| N-next | `net-t2` | TBD |
| F-next | `main`   | TBD |
