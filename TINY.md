# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-283 (BEAUTY)
**HEAD:** `23c0261` B-283 (snobol4x)
**B-session:** M-BEAUTIFY-BOOTSTRAP ❌ — all 19 subsystems ✅; bootstrap fails: ARBNO(*Command) takes 0 iterations when *Parse materialised via CALL_PAT_α path
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-284:**

```bash
cd /home/claude/snobol4x
# Root cause: beauty.sno assigns Parse = nPush() ARBNO(*Command) nPop()
# When *Parse is used in pattern position (stmt line 773), it goes through
# CALL_PAT_α → stmt_match_descr → match_pattern_at → materialise (C runtime).
# Inside ARBNO, *Command is XDSAR("Command"). NV_GET_fn("Command") returns DT_P,
# but Command's DT_P PATND_t was built by the ASM Byrd-box emitter at compile time
# using pat_* C constructors. The XDSAR materialise path calls spat_of(v) to get
# the PATND_t — but the ASM runtime may not store a real PATND_t in Command at all;
# it may store a sentinel DT_P with p==NULL (no PATND_t tree).
#
# DIAGNOSTIC: Add fprintf to XDSAR case in materialise() to print the resolved
# DT_P pointer and its kind. Run beauty_asm with PAT_DEBUG=1 on simple input.
#
# EXPECTED FIX: When scan_named_patterns registers Command as a named pattern (Byrd box),
# it must also call NV_SET_fn("Command", spat_val(patnd_for_Command)) so that
# NV_GET_fn("Command") from the C runtime materialise path gets a real PATND_t.
# Check emit_byrd_asm.c: does it call NV_SET for named patterns? If not, add it.

# Verify after fix:
WORK=$(mktemp -d /tmp/beau_XXXXXX); RT=src/runtime; INC=demo/inc
for f in asm/snobol4_stmt_rt.c snobol4/snobol4.c mock/mock_includes.c \
          snobol4/snobol4_pattern.c engine/engine.c asm/blk_alloc.c asm/blk_reloc.c; do
  gcc -O0 -g -c "$RT/$f" -I"$RT/snobol4" -I"$RT" -I"$RT/asm" \
      -Isrc/frontend/snobol4 -w -o "$WORK/$(basename $f .c).o"
done
./sno2c -asm -I"$INC" demo/beauty.sno > "$WORK/prog.s"
nasm -f elf64 -Isrc/runtime/asm/ "$WORK/prog.s" -o "$WORK/prog.o"
gcc -no-pie "$WORK"/*.o -lgc -lm -o "$WORK/beauty_asm"
snobol4 -f -P256k -Idemo/inc demo/beauty.sno < demo/beauty.sno > /tmp/oracle.sno
"$WORK/beauty_asm" < demo/beauty.sno > /tmp/asm_out.sno 2>/tmp/asm_err.txt
diff /tmp/oracle.sno /tmp/asm_out.sno | head -30
```

**All 19 subsystems PASS after B-283:** global ✅ is ✅ fence ✅ io ✅ case ✅ assign ✅ match ✅ counter ✅ stack ✅ tree ✅ ShiftReduce ✅ TDump ✅ Gen ✅ Qize ✅ ReadWrite ✅ XDump ✅ semantic ✅ omega ✅ trace ✅

---

## Last Two Sessions (3 lines each)

**B-283 (2026-03-24) — M-BEAUTY-MATCH ✅ + all 19 subsystems ✅; bootstrap ARBNO bug found; 106/106:**
(1) Rewrote match driver (TxInList→pattern-based); fixed FAIL α-port missing jmp ω; added nPush/nInc/nPop/nTop C wrappers in mock_includes.c.
(2) All 19 subsystems now PASS 3-way monitor. M-BEAUTY-MATCH ✅ (12 steps).
(3) M-BEAUTIFY-BOOTSTRAP: ARBNO(*Command) takes 0 iterations via CALL_PAT_α path — XDSAR("Command") likely gets DT_P with NULL PATND_t. HEAD `23c0261`.

**B-282 (2026-03-24) — 3 bugs fixed; M-BEAUTY-GLOBAL/IS/ASSIGN PASS; 106/106:**
(1) stmt_match_descr FAILDESCR guard; stmt_setup_subject stale subject_len_val; E_NAM DT_N fix.
(2) M-BEAUTY-GLOBAL ✅ M-BEAUTY-IS ✅ M-BEAUTY-ASSIGN ✅. HEAD `c16c575`.
