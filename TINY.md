# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-278 (BEAUTY) · F-223 (Prolog) concurrent
**HEAD:** `8e01e2a` B-278 (snobol4x) / `.github` pending
**B-session:** M-BEAUTIFY-BOOTSTRAP ❌ — CSNOBOL4 fixed point ✅; ASM _saved labels next
**F-session:** M-PROLOG-CORPUS ❌ — rung05 encoding fix attempted, reverted clean
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-279 (M-BEAUTIFY-BOOTSTRAP continued):**

```
CSNOBOL4 ORACLE: FIXED POINT ✅
  beauty.sno reads itself → 784-line canonical form
  oracle(oracle(beauty.sno)) == oracle(beauty.sno)
  demo/beauty.sno updated to canonical form. Committed 8e01e2a.

BUG FIXED in demo/beauty.sno:
  Goto pattern used *SorF (indirect). After :F(X) match, SorF='F' string.
  Next stmt's *SorF matched literal 'F' only → ':' consumed, 'S(label)' left
  → Parse Error on any stmt following :F(...) goto.
  Fix: replaced *SorF with (*SGoto | *FGoto) inline in Goto.

ASM BACKEND: ❌ NASM errors — seq_l69_α_saved + litvar71_saved undefined
  Root: emit_byrd_asm.c emits LIT_α1/LIT_VAR_α macros that reference
  a `_saved` .bss label, but that label is never declared in the output.
  File: artifacts/asm/beauty_prog.s line 7482.
  Context: seq_l69 is inside ioCmdDlmtPat2 pattern — LIT node in a SEQ.

NEXT SESSION MUST DO:
  1. Find _saved label generation in emit_byrd_asm.c
     grep -n "_saved\|LIT_α\|bss.*saved" src/backend/x64/emit_byrd_asm.c
  2. Find what declares _saved labels in working .s files (roman.s etc.)
     grep "_saved" artifacts/asm/samples/roman.s | head -5
  3. Fix emit_byrd_asm.c to emit the _saved .bss declaration for each LIT node
  4. nasm -f elf64 -I src/runtime/asm/ artifacts/asm/beauty_prog.s -o /dev/null
     → must show 0 errors
  5. Build beauty_asm_bin (see run_crosscheck_asm_prog.sh for link cmd)
  6. Run: beauty_asm_bin < demo/beauty.sno → diff against oracle → PASS
  7. Run SPITBOL: spitbol -I demo/inc demo/beauty.sno < demo/beauty.sno
  8. 3-way diff: CSNOBOL4 == SPITBOL == ASM → commit B-279: M-BEAUTIFY-BOOTSTRAP ✅
```

**⚡ F-CRITICAL NEXT ACTION — F-224 (M-PROLOG-CORPUS):**

```
BUG: rung05 backtrack FAIL — prints a\nb instead of a\nb\nc.
ROOT CAUSE: prolog_emit.c emit_body last-goal user-call branch (~line 692).
  PG(γ) returns clause_idx. Caller increments. switch hits default → ω.
  Inner _cs lost. On retry _cs resets to 0, re-finds b not c.

RECOMMENDED FIX — inner_cs out-param:
  Change _r signature: int pl_F_r(args, Trail*, int _start, int *_ics_out)
  After _cr = pl_F_r(..., _lcs, &_ics): *_ics_out = _ics; goto γ;
  Caller retry: pass &_ics, on retry call with _start=ci, _ics pre-set.

After fix: run all 10 rungs → M-PROLOG-CORPUS fires.
```

---

## Last Two Sessions (3 lines each)

**B-278 (2026-03-24) — Goto/*SorF bug found and fixed; CSNOBOL4 fixed point:**
FGoto left SorF='F' (string); next *SorF matched only 'F', eating ':' bare. Fixed by inlining (*SGoto|*FGoto) in Goto. beauty.sno now self-beautifies to fixed point 784 lines. ASM: seq_l69_α_saved undefined — _saved .bss label not emitted. HEAD `8e01e2a`.

**B-277 (2026-03-24) — M-BEAUTY-TRACE ✅ all 19 subsystems done:**
T8Trace/T8Pos helpers pass 3-way monitor; 9 tests PASS (CSNOBOL4+SPITBOL+ASM). GE(t8MaxLine,621) guard, DATATYPE case portability, TABLE var exclusion. Commit `22e291c`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–19: ALL subsystems PASS (global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump/semantic/omega/trace)
- ❌ M-BEAUTIFY-BOOTSTRAP: CSNOBOL4 ✅ · ASM ❌ (_saved labels) · SPITBOL untested
