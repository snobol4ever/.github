# SESSION-snobol4-x64.md — SNOBOL4 × x86 (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** x86

There is no such thing as a "DYN session" or "B session". There is only
**SNOBOL4 × x86**. The milestone track (sno4parse, Byrd box, TINY/beauty)
is clear from the sprint number and the NOW table. Session prefixes are
for sprint numbering only — they do not define separate session types.

---

## ⛔ §INFO — session invariants (append-only, read every session)

### CSNOBOL4 oracle — do NOT rebuild from scratch
**Date:** 2026-04-04

Patches are checked in. Copy and build — never re-instrument from scratch:
```bash
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0"
```
Files: `one4all/csnobol4/stream.c`, `main.c`, `README.md`, `dyn89_sweep.sh`

### Two-way MONITOR correctness criterion
**Date:** 2026-04-04

Correctness = **agreement with CSNOBOL4**, not independent correctness:
- CS succeeds + sno4parse succeeds → OK
- CS errors + sno4parse errors → OK (both reject — positive AND negative tests count)
- CS succeeds + sno4parse errors → **BUG**
- CS errors + sno4parse succeeds → **BUG** (too permissive)

For hard bugs: `SNO_TRACE=1` on both, diff `/tmp/sno_csno.trace` vs stderr. First divergence = root cause.

### sno4parse build and -I flags
**Date:** 2026-04-04

```bash
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c

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

### Sweep baselines
**Date:** 2026-04-04

| Sweep | OK | FAIL | Notes |
|-------|----|------|-------|
| No -I, after ? fix | 487 | 64 | |
| No -I, after -INCLUDE | 486 | 65 | INFINIP transitive |
| All -I flags | 449 | 102 | real bugs exposed |

199 unique missing include paths — not sno4parse bugs.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/sno4parse.c` | Single-file SNOBOL4 parser / stream oracle |
| `one4all/csnobol4/` | CSNOBOL4 STREAM trace patches |
| `src/backend/emit_x64.c` | Pattern statement emission |
| `src/runtime/snobol4/stmt_exec.c` | `stmt_exec_dyn` — five-phase executor |
| `src/runtime/asm/bb_pool.c` | mmap pool ✅ |
| `src/runtime/asm/bb_emit.c` | byte/label/patch primitives ✅ |
| `src/runtime/dyn/` | bb_*.c — 25 C box implementations ✅ frozen |
| `src/driver/scrip-interp.c` | tree-walk interpreter |
| `src/backend/emit_x64.c` | x64 emitter |

---

## §NOW

One track. Current sprint is whatever Lon is working on — the sequence is
rearrangeable at any time. Past sprints live in SESSIONS_ARCHIVE.md.

| Sprint | HEAD | Next milestone |
|--------|------|----------------|
| 89 | one4all `280329f` · corpus `8d5cc6a` | **M-SN4PARSE-VALIDATE Phase 1** → 84/84 OK on corpus/programs/snobol4/ |

**Current milestone docs:**
- `MILESTONE-SN4PARSE-VALIDATE.md` — active; Phase 1 at ~73/84 OK
- `MILESTONE-SN4PARSE.md` — complete (SIL-faithful parser built)

**Next session first actions:**
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/SESSION-snobol4-x64.md        # §INFO then §NOW
cat .github/MILESTONE-SN4PARSE-VALIDATE.md  # current milestone phases + remaining bugs
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0" 2>&1 | tail -3
cd /home/claude
```

*(TINY/beauty: sprint B-292, one4all `acbc71e`, next: M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR — parked)*

**sno4parse next session first actions:**
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/SESSION-snobol4-x64.md   # §INFO then §NOW
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0" 2>&1 | tail -3
cd /home/claude
# Run two-way MONITOR on a failing file to find next bug class
```
