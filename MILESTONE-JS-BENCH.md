# MILESTONE-JS-BENCH.md — JS Engine Benchmark: one4all vs spipatjs

**Session:** SJ · **Created:** SJ-5, 2026-04-01 · **Author:** Claude Sonnet 4.6

---

## Goal

Measure and compare pattern matching throughput between:
- **one4all engine** (`src/runtime/js/sno_engine.js`) — 532-line iterative
  frame engine (Clojure match.clj model, immutable frames, GC-owned Ω stack)
- **spipatjs** (`github.com/philbudne/spipatjs`) — 3090-line PE node-graph
  engine (GNAT model, pthen-linked nodes, explicit match classes)

Run both **at the same time** in the same Node.js process on the same corpus
of patterns, so JIT warmup and GC conditions are equivalent.

---

## Line counts (as of SJ-5)

| Engine | File | Lines | Model |
|--------|------|-------|-------|
| one4all JS | `sno_engine.js` | 532 | Iterative frame, tagged-union tree |
| spipatjs | `spipat.mjs` | 3090 | PE node graph, pthen links |

Ratio: **~6× smaller**. Architectural difference: spipatjs pre-compiles pattern
graphs at build time (pthen links = O(1) next-node); one4all climbs Ψ parent
stack on every success (O(depth) per node). Hypothesis: spipatjs faster on
simple/linear patterns; one4all competitive on deep-backtrack patterns (ARBNO,
BAL) where the Ω stack allocation advantage matters.

---

## Benchmark suite

Run each pattern × subject pair N=10000 times; report ops/sec.

| ID | Pattern | Subject | Notes |
|----|---------|---------|-------|
| B01 | `'HELLO'` (literal) | `'HELLO WORLD'` | Baseline literal |
| B02 | `BREAK(' ') SPAN(alpha)` | `'the quick brown fox'` | Classic word scan |
| B03 | `ARB 'x'` | `'aaaaaaaaaaax'` | ARB backtrack depth 12 |
| B04 | `ARBNO(SPAN(alpha))` | `'hello world foo'` | ARBNO multi-rep |
| B05 | `BAL` | `'(a(b(c)d)e)rest'` | Balanced parens |
| B06 | `ALT('foo','bar','baz','qux') SPAN(alpha)` | 100-char mixed string | Wide ALT |
| B07 | Nested SEQ 10-deep | 50-char string | Deep sequence |
| B08 | `SPAN(alpha) . WORD` (capture) | `'hello world'` | Capture overhead |

---

## Benchmark harness location

`test/js/bench_engine.js` — standalone Node.js script, no external deps.

Output format (one line per benchmark × engine):
```
B01  one4all   9823456 ops/sec
B01  spipatjs  11234567 ops/sec
```

---

## Gate

- All 8 benchmarks run to completion (no crash, no wrong output)
- Results committed to `test/js/bench_engine_results.txt`
- Summary table added to this file under `## Results`

---

## Implementation notes

- spipatjs is GPL-3 + GCC Runtime Exception — **do not copy code into one4all**
- Import spipatjs as an ES module (`await import(...)`) alongside our CJS engine
- Wrap both in a thin adapter so benchmark loop is identical for both
- Use `performance.now()` for timing; warm up 1000 iterations before measuring

---

## Results

*(to be filled in at milestone completion)*


---

## Results — SJ-6, 2026-04-01

**Node:** v22.22.0  **WARMUP:** 2000  **MEASURE:** 20000

| ID  | one4all (ops/sec) | spipatjs (ops/sec) | ratio | desc |
|-----|------------------:|-------------------:|------:|------|
| B01 | 207,510 | 6,354 | 32.7x | Literal match |
| B02 | 23,578 | 6,072 | 3.9x | BREAK+SPAN word scan |
| B03 | 28,602 | 6,418 | 4.5x | ARB backtrack depth 12 |
| B04 | 232,160 | 6,875 | 33.8x | ARBNO multi-rep |
| B05 | 179,353 | 6,457 | 27.8x | BAL balanced parens |
| B06 | 9,196 | 6,379 | 1.4x | Wide ALT (4 alternatives) |
| B07 | 163,845 | 6,268 | 26.1x | Deep SEQ (10 literals) |
| B08 | 415,434 | 6,406 | 64.9x | CAPT_IMM capture overhead |

**one4all wins all 8 benchmarks.** Range: 1.4x–64.9x faster.

### Analysis

spipatjs throughput is nearly flat (~6,000–6,900 ops/sec) across all patterns
regardless of complexity. Root cause: `Pattern.umatch()` calls `Object.freeze(m)`
on the Match result object on every successful match — this is an O(n) GC write-
barrier operation that dominates the timing. The PE node-graph pthen advantage
is completely masked by this per-call freeze cost.

one4all's advantage is largest on:
- **B08 CAPT_IMM (64.9x)**: short fast path, no freeze overhead
- **B04 ARBNO (33.8x)**: lazy expansion via GC-owned frame tree is cheaper
  than spipatjs's stack management inside freeze-gated match objects
- **B01 Literal (32.7x)**: pure allocation/startup cost dominates spipatjs

**B06 Wide ALT (1.4x)** is the closest: our string-concatenated switch key
`(λ + '/' + action)` pays for itself vs spipatjs's class dispatch only when
pattern complexity is high enough to amortize the freeze cost.

### Conclusion

The Clojure-model engine (immutable frame arrays, GC-owned Ω stack, zero
post-match allocation) is decisively faster in Node.js v22 than the GNAT PE
node-graph model with result freezing. For production use: one4all engine.

Gate: ✅ All 8 benchmarks ran, results committed.
