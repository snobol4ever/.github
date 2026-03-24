# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-277 (BEAUTY) · F-223 (Prolog) concurrent
**HEAD:** `bd9d6e3` B-277 (snobol4x) / `468c507` B-277 (.github)
**B-session:** M-BEAUTY-TRACE ❌ — next subsystem after omega ✅
**F-session:** M-PROLOG-CORPUS ❌ — rung05 encoding fix attempted, reverted clean; see F-CRITICAL below
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-277 (M-BEAUTY-TRACE):**

```
NEXT: INC=demo/inc bash test/beauty/run_beauty_subsystem.sh trace

If test/beauty/trace/ does not exist:
  1. Write test/beauty/trace/driver.sno — exercises T8Trace/T8Pos/xTrace
  2. Generate oracle: INC=demo/inc snobol4 -f -P256k -Idemo/inc driver.sno > driver.ref
  3. Write tracepoints.conf with scan-visible DEFINE stubs for T8Trace/T8Pos
  4. Run 3-way monitor — fix any ASM divergences
  5. On PASS: corpus check (106/106), commit B-277: M-BEAUTY-TRACE ✅, push

PATTERN from B-276 (omega):
  - scan-visible DEFINE stubs needed for functions in -INCLUDE'd files
  - tracepoints.conf: INCLUDE ^FnName$ (anchored), EXCLUDE local vars
  - Binary E_ATP (pat @var) now fixed in emit_byrd_asm.c — no related bug expected

After trace: M-BEAUTIFY-BOOTSTRAP sprint begins.
```

**⚡ F-CRITICAL NEXT ACTION — F-224 (M-PROLOG-CORPUS):**

```
BUG: rung05 backtrack FAIL — prints a\nb instead of a\nb\nc.
ROOT CAUSE: prolog_emit.c emit_body last-goal user-call branch (~line 692).
  PG(γ) returns clause_idx (e.g. 1). Caller increments to 2. switch(2) hits
  default → ω. Inner _cs lost. On retry _cs resets to 0, re-finds b not c.

F-223 ATTEMPTED: encoding scheme (ci + nc*_lcs - 1 in γ, default: decode → retry).
  Got a\nb but env reset in case 1: preamble corrupted third solution.
  Reverted prolog_emit.c to b4507dc — repo clean at b4507dc.

RECOMMENDED FIX — inner_cs out-param (cleanest, no encoding):
  Change _r signature: int pl_F_r(args, Trail*, int _start, int *_ics_out)
  In emit_body last-goal branch: after _cr = pl_F_r(..., _lcs, &_ics);
    *_ics_out = _ics; goto γ;   ← γ returns ci as before
  In emit_choice: _r functions get extra int* param.
  Caller retry loop: pass &_ics, on retry call with _start=ci and _ics pre-set.
  The _r function uses *_ics_out as initial _lcs when _start==ci via hoisted var.

After fix: run all 10 rungs → M-PROLOG-CORPUS fires.
Then: M-PZ-14 → M-PZ-17 → ... in order.
```

---

## Last Two Sessions (3 lines each)

**F-223 (2026-03-24) — rung05 fix attempted, reverted clean:**
Tried encoding scheme: ci+nc*_lcs-1 in γ labels, default: decode → retry label. Got a\nb but third solution corrupted by env reset in case 1: preamble. Reverted prolog_emit.c to b4507dc — repo clean, no new snobol4x commit.

**F-222 (2026-03-23) — puzzle stubs + milestones; no source fix:**
Split puzzles.pro into 16 stub files puzzle_03..20. Added M-PZ-03..20 milestones. Updated FRONTEND-PROLOG.md sprint plan. HEAD `b4507dc`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–16: global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump
- ✅ 17: semantic
- ✅ 18: omega
- ❌ 19: trace ← **now**
