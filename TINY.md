# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-279 (BEAUTY) · F-223 (Prolog) concurrent
**HEAD:** `4bc319c` B-279 (snobol4x)
**B-session:** M-BEAUTIFY-BOOTSTRAP ❌ — CSNOBOL4 ✅; ASM nasm 0 errors ✅; runtime segfault ❌
**F-session:** M-PROLOG-CORPUS ❌ — rung05 encoding fix attempted, reverted clean
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-280 (M-BEAUTIFY-BOOTSTRAP continued):**

```bash
cd /home/claude/snobol4x

# 1. Rebuild (emit_byrd_asm.c already fixed — 3 bugs patched in B-279)
cd src && make -j$(nproc) && cd ..

# 2. Build beauty ASM binary
WORK=$(mktemp -d /tmp/beau_XXXXXX); RT=src/runtime; INC=demo/inc
for f in asm/snobol4_stmt_rt.c snobol4/snobol4.c mock/mock_includes.c \
          snobol4/snobol4_pattern.c engine/engine.c; do
  base=$(basename $f .c)
  gcc -O0 -g -c "$RT/$f" -I"$RT/snobol4" -I"$RT" -Isrc/frontend/snobol4 -w -o "$WORK/$base.o"
done
gcc -O0 -g -c "$RT/asm/blk_alloc.c" -I"$RT/asm" -w -o "$WORK/blk_alloc.o"
gcc -O0 -g -c "$RT/asm/blk_reloc.c" -I"$RT/asm" -w -o "$WORK/blk_reloc.o"
./sno2c -asm -I"$INC" demo/beauty.sno > "$WORK/prog.s"
nasm -f elf64 -I"$RT/asm/" "$WORK/prog.s" -o "$WORK/prog.o"
gcc -no-pie "$WORK"/prog.o "$WORK"/*.o -lgc -lm -o "$WORK/beauty_asm"
echo "build: $?"

# 3. Run and diff against oracle
INC=demo/inc snobol4 -f -P256k -Idemo/inc demo/beauty.sno < demo/beauty.sno > /tmp/oracle.sno
"$WORK/beauty_asm" < demo/beauty.sno > /tmp/asm_out.sno 2>/tmp/asm_err.txt
echo "ASM exit: $?"; wc -l /tmp/asm_out.sno
diff /tmp/oracle.sno /tmp/asm_out.sno | head -20

# 4. Debug segfault with gdb if needed
# gdb -batch -ex run -ex bt "$WORK/beauty_asm" < demo/beauty.sno 2>&1 | tail -30
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

**B-279 (2026-03-24) — ASM nasm errors fixed; binary assembles+links; runtime segfault next:**
3 bugs in emit_byrd_asm.c: (1) fn-body pattern BSS slots routed into per-box DATA via box_ctx; (2) ANY/SPAN/BREAK expr-tmp tlab/plab use flat_bss_register (direct label required by macros); (3) MAX_VARS 512→2048. Result: 0 nasm undefined symbols. Segfault on runtime run. HEAD `4bc319c`.

**B-278 (2026-03-24) — Goto/*SorF bug found and fixed; CSNOBOL4 fixed point:**
FGoto left SorF='F' (string); next *SorF matched only 'F', eating ':' bare. Fixed by inlining (*SGoto|*FGoto) in Goto. beauty.sno now self-beautifies to fixed point 784 lines. ASM: seq_l69_α_saved undefined — _saved .bss label not emitted. HEAD `8e01e2a`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–19: ALL subsystems PASS (global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump/semantic/omega/trace)
- ❌ M-BEAUTIFY-BOOTSTRAP: CSNOBOL4 ✅ · ASM nasm 0 errors ✅ · ASM runtime segfault ❌ · SPITBOL untested
