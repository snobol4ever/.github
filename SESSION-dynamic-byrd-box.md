# SESSION-dynamic-byrd-box.md — DYNAMIC BYRD BOX (SNOBOL4 × x86 / sno4parse)

**Session prefix:** DYN- · **Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** x86
**Deep reference:** `GENERAL-BYRD-DYNAMIC.md` — open only when needed, grep sections, do NOT cat in full.

---

## ⛔ §INFO — session invariants (append-only, read every session)

### CSNOBOL4 oracle — do NOT rebuild from scratch
**Date:** 2026-04-04 (DYN-89)

Patches are checked in. Copy and build — never re-instrument:
```bash
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0"
```
Files: `one4all/csnobol4/stream.c`, `main.c`, `README.md`, `dyn89_sweep.sh`

### Two-way MONITOR correctness criterion
**Date:** 2026-04-04 (DYN-89)

Correctness = **agreement with CSNOBOL4**, not independent correctness:
- CS succeeds + sno4parse succeeds → OK
- CS errors + sno4parse errors → OK (both reject — positive AND negative tests count)
- CS succeeds + sno4parse errors → **BUG**
- CS errors + sno4parse succeeds → **BUG** (too permissive)

For hard bugs: `SNO_TRACE=1` on both, diff `/tmp/sno_csno.trace` vs stderr. First divergence = root cause.

### sno4parse build and -I flags
**Date:** 2026-04-04 (DYN-89)

```bash
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c

# Corpus sweep with include search paths:
IFLAGS="-I/home/claude/corpus/programs/lon/sno \
  -I/home/claude/corpus/programs/lon/rinky \
  -I/home/claude/corpus/programs/lon \
  -I/home/claude/corpus/programs/beauty \
  -I/home/claude/corpus/programs/gimpel \
  -I/home/claude/corpus/programs/include \
  -I/home/claude/corpus/programs/aisnobol \
  -I/home/claude/corpus/programs/snobol4/beauty \
  -I/home/claude/corpus/programs/snobol4/demo \
  -I/home/claude/corpus/programs/snobol4/smoke \
  -I/home/claude/corpus/lib \
  -I/home/claude/corpus/crosscheck/library/lib"
```

### Sweep baselines (DYN-89)
**Date:** 2026-04-04

| Sweep | OK | FAIL | Notes |
|-------|----|------|-------|
| No -I, after ? fix | 487 | 64 | pre -INCLUDE |
| No -I, after -INCLUDE | 486 | 65 | INFINIP transitive |
| All -I flags | 449 | 102 | real bugs, not missing files |

199 unique missing include paths — not sno4parse bugs.

---

## The one-line model

Everything is `stmt_exec_dyn`. Pattern statements compile to:
subject-name → `emit_pat_to_descr` → `call stmt_exec_dyn` → `:S`/`:F`.
No inline NASM Byrd boxes. No named-pattern trampolines. One path.

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/sno4parse.c` | Single-file SNOBOL4 parser / stream oracle |
| `one4all/csnobol4/` | CSNOBOL4 STREAM trace patches (oracle) |
| `src/backend/emit_x64.c` | Pattern statement emission |
| `src/runtime/snobol4/stmt_exec.c` | `stmt_exec_dyn` — five-phase executor |
| `src/runtime/asm/bb_pool.c` | mmap pool (M-DYN-0 ✅) |
| `src/runtime/asm/bb_emit.c` | byte/label/patch primitives (M-DYN-1 ✅) |
| `src/runtime/dyn/` | bb_*.c — 25 C box implementations (DYN-23 ✅ frozen) |
| `src/driver/scrip-interp.c` | tree-walk interpreter |

---

## §NOW — DYN-89

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **DYNAMIC BYRD BOX** | DYN-89 | one4all `280329f` · corpus `8d5cc6a` | **M-SN4PARSE-VALIDATE Phase 3**: two-way STREAM trace — fix arg-whitespace → Phase 1 0 errors |

**DYN-89 work done this session:**
- Binary `?` scan operator fix (SIL PLB32) — ~66 files fixed
- `-INCLUDE` directive: recursive `compile_file()`, relative path resolution, case-insensitive
- `-I` flag: multi-path include search, case-insensitive dir scan
- INFO protocol: merged into SESSION doc (this file); INFO-snobol4-x64.md deleted

**DYN-90 first actions:**
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/SESSION-dynamic-byrd-box.md   # §INFO + §NOW
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c
# Build CSNOBOL4 oracle (patches already in one4all/csnobol4/ — copy+build only)
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0" 2>&1 | tail -3
cd /home/claude
# Run two-way MONITOR on a failing file to find next bug class
```
