# ARCH-harness.md — snobol4harness Reference

**Repo:** https://github.com/snobol4ever/snobol4harness  
**What it is:** Double-trace monitor, cross-engine oracle harness, benchmark pipeline.

---

## Current State

**Active priority:** Stable. Used as diagnostic tool when debugging snobol4x.

---

## The Ladder — Primary Testing Methodology (Session 89 Pivot)

**Decided 2026-03-15. This is the canonical testing protocol for all repos.**

Start small. Go large. One step at a time. Never run the full suite until every rung below it passes.

### The Ladder Structure

```
Rung 1:   1 token   — OUTPUT = 'hello world'
Rung 2:   assign    — X = 'foo'  /  X =  (null assign)
Rung 3:   concat    — OUTPUT = 'a' 'b'
Rung 4:   arith     — OUTPUT = 1 + 2
Rung 5:   control   — goto, :S(), :F()
Rung 6:   patterns  — LIT, ANY, SPAN, BREAK, LEN, POS, RPOS, ARB, ARBNO
Rung 7:   capture   — . and $ operators
Rung 8:   strings   — SIZE, SUBSTR, REPLACE, TRIM, DUPL
Rung 9:   keywords  — IDENT, DIFFER, GT/LT/EQ, DATATYPE
Rung 10:  functions — DEFINE, RETURN, FRETURN, recursion
Rung 11:  data      — ARRAY, TABLE, DATA types
Rung 12:  beauty.sno — the full program, small inputs first (1 token → 20 tokens → full)
```

### The Rule

**Stop at the first failing rung. Fix it. Move up.**

Never skip ahead. A failure at rung 4 (arith) means rungs 5–12 are meaningless — they depend on rung 4 being correct.

### Tools

| Tool | What it does | When to use |
|------|-------------|-------------|
| `crosscheck/run_crosscheck.sh` | Compile+run corpus .sno files, diff vs .ref | First pass at any rung |
| `probe/probe.py` | `&STLIMIT=1..N`, `&DUMP=2` frame-by-frame | When a test fails — bisect to exact statement |
| `TRACE()` + `DUMP()` | Variable/label/function trace in instrumented .sno | When probe isolates the statement — see what diverges |
| `&STLIMIT` / `&STCOUNT` | Execution budget + counter | Stop infinite loops, count statements executed |

### The TRACE gotcha

`TRACE(...,'KEYWORD')` is non-functional on both CSNOBOL4 and SPITBOL.
Use `TRACE('varname','VALUE')` on a probe variable instead.
`&STCOUNT` broken in CSNOBOL4 (always 0) — use `&STLIMIT` values for binary search.

### Corpus lives in snobol4corpus

Every repo uses the same corpus. Test programs are never duplicated into engine repos.
The corpus crosscheck runner lives in `snobol4corpus/crosscheck/run_all.sh`.
The per-engine adapter lives in `test/crosscheck/run_crosscheck.sh` in each repo.

### Current crosscheck results (snobol4x, Session 89, `29c0a4b`)

```
output:   7/8  — FAIL: SIZE(&ALPHABET) returns 0 instead of 256
assign:   7/8  — FAIL: null assign (X =) does not clear variable
concat:   ?    — not yet run
arith:    ?    — not yet run
...
```

**Active rung: assign/012 (null assign bug) and output/006 (&ALPHABET size bug).**

## The Double-Trace Monitor

Run the oracle interpreter and the compiled binary side by side, emit the same event stream from both, compare event by event. First divergence = root cause. Not a symptom — the actual bug, identified automatically.

**Oracle event stream** (from `beauty.sno` with TRACE hooks):
```snobol4
        TRACE('snoLine','VALUE')
        TRACE('snoSrc','VALUE')
```
CSNOBOL4 → stderr. SPITBOL → stdout. Monitor separates these.

**TRACE gotcha:** `TRACE(...,'KEYWORD')` is non-functional on both CSNOBOL4 and SPITBOL. Use VALUE trace on a probe variable. `&STCOUNT` broken in CSNOBOL4 (always 0) — use literal `&STLIMIT` values for binary search.

## Oracle Hierarchy

| Oracle | Role | Invocation |
|--------|------|-----------|
| CSNOBOL4 2.3.3 | **Primary** — `beauty.sno` reference | `snobol4 -f -P256k -I $INC file.sno` |
| SPITBOL x64 4.0f | Secondary reference | `spitbol -b file.sno` |

**SPITBOL disqualified for beauty.sno** — error 021 at END (indirect function call semantic difference).

## Install (if not present)

```bash
# CSNOBOL4
./configure && make && make install   # → /usr/local/bin/snobol4

# SPITBOL x64
apt-get install nasm
git clone https://github.com/spitbol/x64 spitbol-x64
cd spitbol-x64 && make && cp sbl /usr/local/bin/spitbol
```

## Benchmark Pipeline

Cross-engine grid: SPITBOL / CSNOBOL4 / Interpreter / Transpiler / Stack VM / JVM bytecode.  
Times include ~15ms process-spawn overhead for SPITBOL/CSNOBOL4 — subtract for fair comparison.

**Key results (2026-03-10):**

vs PCRE2 JIT — `(a|b)*abb`: snobol4x **2.3×** faster (33 ns vs 78 ns)  
vs PCRE2 JIT — `(a+)+b` pathological: snobol4x **7–33×** faster (0.7 ns vs 21 ns)  
vs Bison LALR(1) — `{a^n b^n}`: snobol4x **1.6×** faster (44 ns vs 72 ns)
