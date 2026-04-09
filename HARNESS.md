# HARNESS.md — harness Reference

**Repo:** https://github.com/snobol4ever/harness  
**What it is:** Double-trace monitor, cross-engine oracle harness, benchmark pipeline.

---

## Current State

**Active priority:** Stable. Used as diagnostic tool when debugging one4all.

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

`TRACE(...,'KEYWORD')` is non-functional on SPITBOL.
Use `TRACE('varname','VALUE')` on a probe variable instead.
`&STCOUNT` — use `&STLIMIT` values for binary search.

### Corpus lives in corpus

Every repo uses the same corpus. Test programs are never duplicated into engine repos.
The corpus crosscheck runner lives in `corpus/crosscheck/run_all.sh`.
The per-engine adapter lives in `test/crosscheck/run_crosscheck.sh` in each repo.

### Current crosscheck results (one4all, Session 89, `29c0a4b`)

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
SPITBOL → stdout.

**TRACE gotcha:** `TRACE(...,'KEYWORD')` is non-functional on SPITBOL. Use VALUE trace on a probe variable. `&STCOUNT` was broken in old CSNOBOL4 builds (always 0) — use literal `&STLIMIT` values for binary search. (CSNOBOL4 is source reference only; not run as oracle.)

## Oracle Hierarchy

| Oracle | Role | Invocation |
|--------|------|-----------|
| SPITBOL x64 4.0f | **Sole execution oracle** (D-005) | `/home/claude/x64/bin/sbl -b file.sno` |

**CSNOBOL4 is NOT an oracle** — SOURCE REFERENCE ONLY. Do not build or invoke for test purposes.

## Install (if not present)

```bash
# SPITBOL x64 — clone snobol4ever/x64; binary is pre-built
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
# Oracle: /home/claude/x64/bin/sbl -b file.sno
```

## Benchmark Pipeline

Cross-engine grid: SPITBOL / Interpreter / Transpiler / Stack VM / JVM bytecode.  
Times include ~15ms process-spawn overhead for SPITBOL — subtract for fair comparison.

**Key results (2026-03-10):**

vs PCRE2 JIT — `(a|b)*abb`: one4all **2.3×** faster (33 ns vs 78 ns)  
vs PCRE2 JIT — `(a+)+b` pathological: one4all **7–33×** faster (0.7 ns vs 21 ns)  
vs Bison LALR(1) — `{a^n b^n}`: one4all **1.6×** faster (44 ns vs 72 ns)
