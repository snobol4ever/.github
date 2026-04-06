# MILESTONE-P2F-SEMI — Semicolon Statement Separator

**Status:** ⬜ deferred  
**Blocks:** 1012_func_locals (1 test, currently FAIL in PASS=178 baseline)  
**Track:** SNOBOL4 × x86 / CMPILE parser

---

## The bug in one line

```snobol4
        a = 'aa' ; b = 'bb' ; d = 'dd'
```

Only `a = 'aa'` is compiled. `b = 'bb'` and `d = 'dd'` are dropped.

## Root cause (RT-139, 2026-04-06)

`FORWRD()` inside `CMPFRM` calls `forrun()` which reads the **next physical
card** into `g_io_linebuf`, clobbering the `; b='bb' ; d='dd'` remainder that
`TEXTSP.ptr` still points into.  The outer P2F loop in `cmpile_file_internal`
correctly checks `BRTYPE==EOSTYP && TEXTSP.len>0` after `compile_one_stmt()`
returns, but always sees `TEXTSP.len=0` because the buffer was overwritten.

## v311.sil mechanism (authoritative)

```
XLATNX  STREAM XSP,TEXTSP,CARDTB   ← re-classify remaining TEXTSP
        RCALL  ,NEWCRD              ← process card type
        RCALL  ,CMPILE,,(COMP3,,XLATNX)  ← compile; RTN3 → XLATNX again
```

After CMPILE parses `a='aa'` and FORBLK consumes `;`, TEXTSP = ` b='bb' ; d='dd'`.
RTN3 goes back to XLATNX → CARDTB sees leading space → NEWTYP → NEWCRD → CMPILE.
**No semicolon logic inside CMPILE itself.**

## Fix

In `cmpile_file_internal`, **snapshot TEXTSP before calling `compile_one_stmt()`**:

```c
/* XLATNX mirror: snapshot remainder so forrun() clobber can be detected */
const char *semi_saved_ptr = NULL;
int         semi_saved_len = 0;
```

Inside `compile_one_stmt()` (or via a wrapper), before `FORWRD()`/`EXPR()` inside
`CMPFRM`, save `TEXTSP` to a buffer that `forrun()` cannot touch (not `g_io_linebuf`).
After CMPILE returns, restore that snapshot as TEXTSP if `BRTYPE==EOSTYP`.

Alternatively: **find the exact `return s` path** inside CMPILE() that handles
`a='aa'` — add `SNO_SEMI=1` probes at every `return s` on a one-line test file:

```bash
printf "        a = 'aa' ; b = 'bb' ; d = 'dd'\nend\n" > /tmp/semi1.sno
SNO_SEMI=1 ./scrip --dump-parse /tmp/semi1.sno 2>&1
```

Fix that one path to not drain TEXTSP past `;`.

## Test monitor note

The CMPILE stream trace (`SNO_TRACE=1`) already runs against all 500+ corpus
sources via `one4all/csnobol4/dyn89_sweep.sh`.  Once the fix is in, strap
`--dump-parse` against the full corpus sweep to catch regressions:

```bash
# Gate: all 500+ files parse without error; stmt count matches reference
CORPUS=/home/claude/corpus bash one4all/csnobol4/dyn89_sweep.sh 2>/dev/null | grep FAIL
```

## Gate

```bash
cd /home/claude/one4all
./scrip --dump-parse corpus/crosscheck/rung10/1012_func_locals.sno | grep "stmt 1[012]"
# Must show: stmt 10 = a='aa', stmt 11 = b='bb', stmt 12 = d='dd'
./scrip --interp corpus/crosscheck/rung10/1012_func_locals.sno   # → PASS
CORPUS=/home/claude/corpus bash test/run_interp_broad.sh 2>/dev/null | grep "^PASS"
# PASS=179 (was 178)
```

## Regression note (RT-139b)

The P2F loop was originally in `sno4parse.c` (commit `174d77eb`, sprint 93) and
**worked** — 84/84 sweep confirmed.  It was copied verbatim to `cmpile_file_internal`
when CMPILE became the default parser (RT-113/114), but in CMPILE.c `TEXTSP.len==0`
when the loop checks it.  Something in the CMPILE path between `compile_one_stmt()`
returning and the loop check drains TEXTSP.  **This is a one-line regression**, not
a design problem.  Bisect: `git log --oneline 174d77eb..HEAD -- src/frontend/snobol4/CMPILE.c`
and find the commit that broke `TEXTSP.len`.
