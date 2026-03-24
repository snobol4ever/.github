# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — M-BEAUTY-* sprint
**HEAD:** `fe86477` B-275 (main)
**Milestone:** M-BEAUTY-SEMANTIC ❌ — driver+ref ready (8/8 CSN); ASM segfaults on DATA/`$'#N'`
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — B-276 (M-BEAUTY-SEMANTIC):**

```bash
cd /home/claude/snobol4ever
# bootstrap: see snobol4x/PLAN.md §START (clones + setup.sh → 106/106)

# BUG: ASM segfaults on semantic/driver.sno
# Root cause: DATA('link_counter(next,value)') + $'#N' indirect computed variable
# Fix target: snobol4.c — DEFDAT_fn / NV_GET_fn / NV_SET_fn for DATA object values
# Debug: compile semantic/driver.sno via -asm, run under ASAN/gdb, find crash site

INC=snobol4x/demo/inc bash snobol4x/test/beauty/run_beauty_subsystem.sh semantic
# → 8/8 PASS → commit "B-276: M-BEAUTY-SEMANTIC ✅" → advance to M-BEAUTY-OMEGA
# omega.sno: write driver → oracle → fix ASM → commit
```

---

## Last Two Sessions (3 lines each)

**B-275 (2026-03-23) — M-BEAUTY-XDUMP ✅:**
`stmt_aref2/aset2` (2D subscripts); `PROTOTYPE` now returns `lo:hi`; `table_set_descr` preserves integer key type through SORT; `expr_flatten_str` for multi-line DEFINE. Semantic driver+ref committed; ASM segfault on DATA/`$'#N'` is B-276 blocker. HEAD `fe86477`.

**B-274 (2026-03-23) — M-BEAUTY-READWRITE ✅:**
`expr_flatten_str()` — multi-line DEFINE (E_CONC spec) was silently skipping `Read` as user fn; `fn_Read_γ/ω` now emitted; FRETURN routes correctly. 8/8 ASM PASS. HEAD `eeeb5ad`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–16: global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump
- ❌ 17: semantic ← **now**
- ❌ 18: omega
- ❌ 19: trace
