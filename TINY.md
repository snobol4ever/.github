# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-286 (arch decisions D-001–D-005 + 4-bug fix)
**HEAD:** commit pending push (snobol4x)
**B-session:** SPITBOL-primary target declared. 4 bugs fixed by one patch. 19/19 beauty PASS. Bootstrap Parse Error open.
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-287:**

Fix M-BUG-BOOTSTRAP-PARSE: beauty_asm outputs 10-line header then `Parse Error` on first non-comment line.
Oracle (SPITBOL) produces 784 lines. Investigate the parser/ARBNO loop in the bootstrap path.

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
