# SESSION-snobol4-x64.md — SNOBOL4 × x86 (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** x86

There is no such thing as a "DYN session" or "B session". There is only
**SNOBOL4 × x86**. The milestone track (sno4parse, Byrd box, TINY/beauty)
is clear from the sprint number and the NOW table. Session prefixes are
for sprint numbering only — they do not define separate session types.

---

## ⛔ §INFO — session invariants (append-only, read every session)

### v311.sil and two-way MONITOR script locations
**Date:** 2026-04-05

When a STREAM table sequence is unknown: **read v311.sil first**, then syn.c for bytes:
```bash
/home/claude/snobol4-2.3.3/v311.sil      # SIL procedure bodies
/home/claude/snobol4-2.3.3/syn.c         # chrs[] table bytes (authoritative)
/home/claude/snobol4-2.3.3/syn_init.h    # action put/act/go assignments
```

Two-way MONITOR scripts are checked in beside the csnobol4 patches:
```bash
one4all/csnobol4/dyn89_sweep.sh   # sweep corpus/programs/snobol4/
one4all/csnobol4/stream.c         # CSNOBOL4 patch → /tmp/sno_csno.trace
one4all/csnobol4/main.c           # CSNOBOL4 patch
one4all/csnobol4/README.md        # full workflow
```

Standard diff workflow:
```bash
SNO_TRACE=1 /home/claude/snobol4-2.3.3/snobol4 /tmp/x.sno 2>/dev/null  # → /tmp/sno_csno.trace
SNO_TRACE=1 /home/claude/sno4parse /tmp/x.sno 2>/tmp/sn.trace
diff /tmp/sno_csno.trace /tmp/sn.trace | head -30
```



Patches are checked in. Copy and build — never re-instrument from scratch:
```bash
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0"
```
Files: `one4all/csnobol4/stream.c`, `main.c`, `README.md`, `dyn89_sweep.sh`

### True streaming — no linebuf, no pre-joining (sprint 92)
**Date:** 2026-04-04

CSNOBOL4 XLATNX keeps TEXTSP = one physical line. FORWRD/FORBLK call FORRUN on ST_EOS
to fetch the next card. NEWCRD dispatches: CNTTYP → strip '+', re-drive; NEWTYP → save
as pending. We do the same. linebuf pre-join is permanently banned.

SIL STREAM 6-arg convention:
  `STREAM out, in, table, error_branch, eos_branch, stop_branch`
  C stream() returns: ST_ERROR→arg4, ST_EOS→arg5, ST_STOP→arg6 (omitted = fall through)

All five stream() call-site bugs fixed in sprint 92 (one4all `229b04e`):
- FORWRD: ST_EOS → forrun(), not BRTYPE=EOSTYP
- FORBLK: ST_EOS → forrun(); ST_ERROR = RTN1 (no blank) — leave BRTYPE as-is
- ELEMTB: ST_EOS + STYPE==0 → sil_error (ELEILI)
- GOTOTB: ST_EOS → sil_error (CERR12)
- LBLTB: ST_ERROR → sil_error (CERR1)

Result: 84/84 sweep.

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
| 92 | one4all `229b04e` · corpus `8d5cc6a` | **M-SN4PARSE-VALIDATE Phase 1 ✅ 84/84** — next: Phase 2 SPITBOL extensions (P2A binary `?`, P2C `[]` subscript, P2F semicolon) |

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

**sno4parse next session first actions (sprint 91):**
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/SESSION-snobol4-x64.md
cat .github/MILESTONE-SN4PARSE-VALIDATE.md
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0" 2>&1 | tail -3
cd /home/claude
# 1. g_error lifecycle: grep -n "g_error\|sil_error" one4all/src/frontend/snobol4/sno4parse.c | head -30
# 2. SNO_TRACE=1 ./sno4parse corpus/programs/snobol4/demo/inc/Qize.sno 2>&1 | grep "ret=ERROR"
# 3. BRTYPE=1 postfix subscript: sed -n around ELEFNC + expr_prec_continue '[' detection
```

### ✅ LINEBUF PRE-JOIN REMOVED (sprint 92)
**Date:** 2026-04-05 → implemented 2026-04-04

True streaming implemented. linebuf gone. forrun() is the canonical continuation handler.

