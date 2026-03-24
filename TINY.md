# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-285 (BEAUTY accounting)
**HEAD:** `deae788` B-284 (snobol4x)
**B-session:** Full accounting done. 5 bug milestones filed. Next: fix is → semantic → TDump → Gen → bootstrap.
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-286:**

Fix M-BUG-IS-DIALECT first — likely same root as M-BUG-SEMANTIC-NTYPE. Both IsSnobol4+IsSpitbol true in ASM; nPush/nInc/nPop report STRING not PATTERN.

Beauty subsystem standalone ASM (B-285 re-run): 15/19 PASS.
- PASS: global fence io case assign match counter stack tree ShiftReduce Qize ReadWrite XDump omega trace
- FAIL: is TDump Gen semantic → milestones M-BUG-IS-DIALECT M-BUG-TDUMP-TLUMP M-BUG-GEN-BUFFER M-BUG-SEMANTIC-NTYPE

Bootstrap: beauty_asm outputs 10-line header + `Parse Error` (oracle=784 lines) → milestone M-BUG-BOOTSTRAP-PARSE.
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
