# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-291 (BSS heap fix; Sprint M5 unblocked)
**HEAD:** `309a2f9` B-291
**B-session:** Heap-allocated 4 large BSS statics in emit_byrd_asm.c (named_pats 1.9MB, str_table 2.8MB, call_slots 1.3MB, lit_table 352KB). BSS 8.4MB→2.0MB. sno2c -asm/-jvm beauty.sno no longer segfaults. beauty_asm_bin (1.1MB) builds, runs — produces 10 lines then "Parse Error" (r12 clobber confirmed). TRACE_SET_CAP 64→256. CSNOBOL4 oracle trace: 92,601 events, 784 lines output. ASM trace: silent (TERMINAL= fallback not reaching stderr before crash). 106/106 ✅.
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-292 (M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR):**

Sprint M5 is now runnable. Two steps to get first divergence:

1. **Get ASM trace stream flowing.** The instrumented beauty_asm_bin crashes before
   TERMINAL= trace output reaches stderr. Fix: redirect TERMINAL= writes to a file
   in snobol4.c comm_var, OR run the async monitor (oracle trace already captured:
   /tmp/csn_trace.txt, 92,601 events). The async approach works immediately:
   ```bash
   # Build instrumented ASM binary (beauty_instr.sno already at /tmp/)
   # Run: beauty_instr_asm < demo/beauty.sno 2>/tmp/asm_trace.txt
   # diff /tmp/csn_trace.txt /tmp/asm_trace.txt | head -20
   # First diverging line = exact variable + value where r12 clobber fires
   ```

2. **Fix the divergence.** The first diverging line names the variable that got
   corrupted. Per MONITOR.md: CSNOBOL4 + (if SPITBOL working) = living spec for fix.
   Fix is in emit_byrd_asm.c emit_named_ref — per-invocation DATA block via blk_alloc
   (M-T2-INVOKE), or zeroing at β call site.

**JVM mid-emission crash (also B-292):**
Apply nchildren bound fix in emit_byrd_jvm.c line 1133:
```c
for (int fi = 0; fi < dt->nfields; fi++) {
    JI("dup", "");
    char fnesc[256]; jvm_escape_string(dt->fields[fi], fnesc, sizeof fnesc);
    JI("ldc", fnesc);
    EXPR_t *arg = (fi < e->nchildren) ? e->children[fi] : NULL;
    if (arg) jvm_emit_expr(arg); else JI("ldc", "\"\"");
    ...
}
```
Then: beauty.j completes → Jasmin assembles → JVM beauty subsystem ladder begins.

**B-286 summary:**
- D-001: SPITBOL is primary compat target (CSNOBOL4 FENCE issue disqualifies it).
- D-002: DATATYPE() = UPPERCASE always. SPITBOL lowercase is an ignore-point.
- D-003: Test suite case-insensitive on DATATYPE output.
- D-004: .NAME = third dialect (DT_N). Matches SPITBOL observable behaviour.
- D-005: Monitor swapped — SPITBOL is participant 0 (primary oracle).
- Single-line fix in emit_byrd_asm.c (arg staging always -32): resolves M-BUG-IS-DIALECT,
  M-BUG-SEMANTIC-NTYPE, M-BUG-TDUMP-TLUMP, M-BUG-GEN-BUFFER. 19/19 beauty PASS.
- DECISIONS.md created in .github.
C backend: ☠️ DEAD — removed from matrix. 99/106, sno2c fails on word*/pat_alt_commit. Not maintained.

---

## Last Two Sessions (3 lines each)

**B-283 (2026-03-24) — M-BEAUTY-MATCH ✅ + all 19 subsystems ✅; bootstrap ARBNO bug found; 106/106:**
(1) Rewrote match driver (TxInList→pattern-based); fixed FAIL α-port missing jmp ω; added nPush/nInc/nPop/nTop C wrappers in mock_includes.c.
(2) All 19 subsystems now PASS 3-way monitor. M-BEAUTY-MATCH ✅ (12 steps).
(3) M-BEAUTIFY-BOOTSTRAP: ARBNO(*Command) takes 0 iterations via CALL_PAT_α path — XDSAR("Command") likely gets DT_P with NULL PATND_t. HEAD `23c0261`.

**B-282 (2026-03-24) — 3 bugs fixed; M-BEAUTY-GLOBAL/IS/ASSIGN PASS; 106/106:**
(1) stmt_match_descr FAILDESCR guard; stmt_setup_subject stale subject_len_val; E_NAM DT_N fix.
(2) M-BEAUTY-GLOBAL ✅ M-BEAUTY-IS ✅ M-BEAUTY-ASSIGN ✅. HEAD `c16c575`.
