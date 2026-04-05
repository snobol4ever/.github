# INFO-snobol4-x64.md — DYN session invariants (SNOBOL4 × x86)

**Read at every DYN session start. Append-only. Never prune.**
**Format:** one entry per invariant. Each entry: date, what, why.

---

## ⛔ CSNOBOL4 oracle — do NOT rebuild from scratch

**Date:** 2026-04-04 (DYN-89)

The CSNOBOL4 2.3.3 oracle is already patched and the patches are checked into:

```
one4all/csnobol4/stream.c   — TRACE_STREAM instrumentation (matches sno4parse SNO_TRACE format)
one4all/csnobol4/main.c     — opens /tmp/sno_csno.trace when SNO_TRACE=1
one4all/csnobol4/README.md  — apply + build instructions
one4all/csnobol4/dyn89_sweep.sh — corpus sweep script
```

**To build the oracle** (apply patches then compile — do NOT re-instrument from scratch):

```bash
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0"
```

**To use the oracle (two-way STREAM diff):**

```bash
# CS trace → /tmp/sno_csno.trace
SNO_TRACE=1 ./snobol4-2.3.3/snobol4 /tmp/test.sno

# sno4parse trace → stderr
SNO_TRACE=1 ./sno4parse /tmp/test.sno 2>/tmp/sn.trace

# Diff — first divergence = root cause
diff /tmp/sno_csno.trace /tmp/sn.trace | head -30
```

**Why:** Rebuilding from scratch wastes tokens and reapplies the same patches.
The checked-in files ARE the oracle — trust them, copy them, build.

---

## ⛔ sno4parse — current binary location and build command

**Date:** 2026-04-04 (DYN-89)

```bash
# Source (single file):
one4all/src/frontend/snobol4/sno4parse.c

# Build:
cd /home/claude
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c

# Run with include search paths:
./sno4parse -I<dir1> -I<dir2> <file.sno>
```

Binary is at `/home/claude/sno4parse` (not checked in — always rebuild from source).

---

## ⛔ Two-way MONITOR discipline

**Date:** 2026-04-04 (DYN-89)

The correctness criterion is **agreement with CSNOBOL4**, not independent correctness:

- CS succeeds + sno4parse succeeds → OK (even if IR differs)
- CS gives syntax error + sno4parse gives syntax error → OK (both reject)
- CS succeeds + sno4parse errors → **BUG in sno4parse**
- CS errors + sno4parse succeeds → **BUG in sno4parse** (too permissive)
- Divergence in STREAM trace → first diff line = root cause

For hard-to-find bugs: run both with `SNO_TRACE=1` and diff the trace files.
The two-way MONITOR is the gold standard — not the corpus sweep alone.

---

## ⛔ -I include search paths for corpus sweep

**Date:** 2026-04-04 (DYN-89)

Missing includes in the corpus are NOT sno4parse bugs. Standard -I flags for
full corpus coverage:

```bash
IFLAGS="\
  -I/home/claude/corpus/programs/lon/sno \
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

199 unique missing include paths documented in DYN-89 session.
Case-insensitive filename matching is implemented (e.g. `sqrt.sno` finds `SQRT.sno`).

---

## ⛔ Sweep baseline (DYN-89)

**Date:** 2026-04-04

| Sweep | OK | FAIL | Notes |
|-------|----|------|-------|
| No -I flags, pre-DYN-89 | 487 | 64 | after ? operator fix |
| No -I flags, post -INCLUDE | 486 | 65 | INFINIP.sno inherits include errors |
| With all -I flags | 449 | 102 | more content → more real bugs exposed |

Failures with -I flags are genuine parse bugs, not missing-file issues.
Primary remaining bug class: complex Gimpel library patterns (tab-label context).

---

## ⛔ Commit identity

**Date:** ongoing

Always commit as:
```bash
git config user.name "Lon Jones Cherryholmes"
git config user.email "lon@snobol4ever.com"
```
