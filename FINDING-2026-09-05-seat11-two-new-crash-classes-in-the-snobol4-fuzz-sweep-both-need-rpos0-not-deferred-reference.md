# FINDING 2026-09-05 seat11 — two NEW SNOBOL4 pattern-fuzz crash classes, both keyed on `RPOS(0)` anchoring a nullable compound arm, NEITHER dependent on deferred reference (`*name`)

Row `fuzz-crash-class-and-port-trace-refs-over-the-three-open-languages` (hq_U task, FLEET-12).
WITNESSES ONLY, NEVER COMPILER FIXES per the row's own brief and per FLEET-12 (Sonnet seats walk and
witness; Opus HQs cure) — nothing in `src/` was touched for this finding.

## Run

Continuing seat20's SNOBOL4 pattern fuzz sweep (`FINDING-2026-09-05-seat20-snobol4-pattern-fuzz-sweep-36-reds-arbno-deferred-reference-is-the-dominant-crash-class.md`,
n=3000 seed=42 depth=4). This run went one grammar level deeper: `python3 scripts/util_pattern_fuzz.py
--n 3000 --seed 7 --depth 5`, graded against `sbl_correctness_bin()` (`/home/resources/x64/bin/sbl -bf`),
tree SCRIP `7cbc49406` / corpus `f33c822c3`.

```
AGREE          2722
ORACLE-BAD      244   (SPITBOL itself errored/SIGSEGV'd -- never a SCRIP verdict, per the tool's own design)
DIFF             11
HANG              9
FALSE-ACCEPT      5
rc1               5
SEGV              3
SIG6              1
=== 34 distinct red shapes from 34 red runs ===
```

Full shape list is in the sweep log (not re-pasted here); most still involve `*name` (seat20's class, still
real and still the single most common ingredient by raw count). But a calibration run at n=200 before the
full sweep turned up two shapes with **no `*name` anywhere**, and hand-ablation below shows they are
genuinely different triggers, not a smaller instance of the deferred-reference class.

## Witness A (SEGV, both modes) — nested `ARBNO(ARBNO(...))` under an outer nullable alternation, anchored by `RPOS(0)`

Reduced from `pf_01223.sno` (`ARBNO(ARBNO(BREAKX('ab'))) | ''`, subject `'aaa'`, `POS(0) *P RPOS(0)`).

```
          'aa' (ARBNO(ARBNO(BREAKX('a'))) | '') RPOS(0)          :S(OK)F(NO)
OK        OUTPUT = 'match'                      :(END)
NO        OUTPUT = 'nomatch'
END
```

- Oracle (`sbl -bf`): `match`, rc=0.
- SCRIP m3 (`--run`): **SIGSEGV**, rc=139.
- SCRIP m4 (`--compile`+as+gcc): compiles and links cleanly; the binary **SIGSEGVs** at runtime, rc=139
  (same signal in both modes here, unlike seat20's ARBNO(*name) witness where the fault type diverged
  by mode).
- **Stable 10/10 in both modes** (`util_fuzz_witness_stability.sh`, N=10, `(stdout,rc)` pair).
- gdb: `SIGSEGV` at `RIP=0x0`, both backtrace frames unwind to `0x0`. This reads as a call/jump through a
  NULL function pointer (unwired Byrd-box port, most likely), not a stack-guard fault — `rsp`/`rbp`
  (`0x7fffffbf9390` / `...9418`) sit at a normal mid-stack depth, nowhere near a guard page. Not gdb'd
  further than this one data point: identifying which box's port is left unwired is diagnosis, not
  witnessing, and belongs to whoever cures this.

### Ablation (all run m3, oracle in brackets where it differs from `match`)

| variant | change from witness A | result |
|---|---|---|
| A | as above | **SEGV** |
| direct `P` instead of `*P` (named, non-deferred) | drops the `*name` mechanism entirely | **STILL SEGV** — proves this is NOT the deferred-reference class |
| inline the pattern, no `P` variable at all | drops named storage entirely, not just deferral | **STILL SEGV** |
| single `ARBNO(BREAKX('a'))`, not nested | drops the double-nesting | clean, matches oracle |
| drop the outer `(... \| '')`, keep double nesting + `RPOS(0)` | drops the nullable-alternation wrapper | clean, matches oracle — **the outer nullable alternation is load-bearing, not incidental** |
| `POS(0)` instead of `RPOS(0)` | swap anchor | clean, matches oracle — **`RPOS` specifically, not `POS`** |
| both `POS(0)` and `RPOS(0)` | add `POS(0)` back alongside `RPOS(0)` | clean (`[nomatch]`) — adding `POS(0)` back **suppresses** the crash |
| `ARB` instead of `BREAKX('a')` | swap the repeated primitive | clean, matches oracle — a dynamic/set-scanning primitive is needed, plain `ARB` is not enough |
| subject `'a'` (1 char) instead of `'aa'` | shorten subject | clean — subject must be >= 2 chars |
| subject `''` (empty) | shorten further | clean |

So the load-bearing recipe is: **double-nested `ARBNO(ARBNO(X))` for a dynamic-scan `X`, wrapped in an
outer `(... | '')`, anchored by a bare `RPOS(0)` with no accompanying `POS(0)`, against a subject of at
least 2 characters.** Every one of those six ingredients was independently shown necessary by removing it
alone and watching the crash disappear.

## Witness B (HANG, both modes) — nested alternation with the empty arm two levels deep, anchored by `RPOS(0)`

Reduced from `pf_01141.sno` (`P = SPAN('ab') | (BREAKX('ab') | ''); 'a+a+a' *P RPOS(0)`).

```
          'a+a+a' (SPAN('ab') | (BREAKX('ab') | '')) RPOS(0)     :S(OK)F(NO)
OK        OUTPUT = 'match'                      :(END)
NO        OUTPUT = 'nomatch'
END
```

- Oracle: `match`, rc=0.
- SCRIP m3 and m4: both **HANG** (rc=124 under an 8s timeout; confirmed genuinely unbounded, not merely
  slow, by the stability run below completing 10 timeout-bound samples per mode with an identical
  `(stdout,rc)` reading every time — an unbounded computation and "needs 9s" are indistinguishable by a
  single sample, per `lib_gate.sh`'s own duration-vs-hang caution, but are NOT indistinguishable by ten).
- **Stable 10/10 in both modes** (same tool, same N).

### Ablation

| variant | result |
|---|---|
| direct (non-deferred) reference to the stored pattern | **STILL HANGS** — again rules out `*name` |
| fully inlined, no variable at all | **STILL HANGS** |
| drop `RPOS(0)` (deferred or inline) | clean, matches oracle |
| shrink literals `'ab'`->`'a'` and subject `'a+a+a'`->`'aa'` together | clean — this pair's exact literal/subject sizing is load-bearing, unlike Witness A's subject which only needed to clear a length-2 floor |
| flatten to `(SPAN('a') | (ARB | ''))` (drop `BREAKX`, keep the nesting shape) | clean — `BREAKX` specifically matters here too, `ARB` does not reproduce either witness |
| trivial single-level nullable alternatives tried directly: `(ARB\|'')`, `('x'\|'')`, `(SPAN('a')\|'')`, `(BREAKX('a')\|'')`, even bare `('')`, each alone with `RPOS(0)` | **all five clean** — a top-level empty alternative plus `RPOS(0)` is NOT sufficient by itself |
| nested alternation shape without `ARBNO`, using `ARB` instead of `BREAKX` (`(SPAN('a')\|(ARB\|''))`) | clean — the nesting shape alone, without `BREAKX`'s dynamic scan, does not reproduce |

## The common thread across A and B, stated at the honest confidence level

Both witnesses need: **(1) `RPOS(0)` as the anchor (not `POS(0)`, and adding `POS(0)` alongside actively
suppresses Witness A's crash), (2) a nullable/empty alternative embedded inside a *compound* pattern
(double `ARBNO` nesting for A, alternation-nested-inside-alternation for B) — never a top-level
`(X | '')` for a simple `X`, which is clean in every combination tried, (3) a dynamic/set-scanning
primitive (`BREAKX`) somewhere in the non-empty arm — `ARB` alone never reproduces either witness.**

⛔ **What this finding does NOT claim.** It does not claim A and B share one root cause in the compiler —
only that both are real, both are independent of `*name`/deferred reference (which seat20's own class
does depend on), and both share the same three necessary ingredients above. Whether they bottom out in
the same mechanism (plausibly something in how `RPOS` reads a dynamic cursor position across a nested
backtracking/recede boundary — echoing the unrelated-but-similarly-shaped hq_S finding on `LEN` reading a
stale RSP-relative operand across a moved stack) is a hypothesis for whoever diagnoses this with
ASM-DIFF-FIRST, not a measured conclusion here.

## Scope and disposition

Neither witness is cured here. Both are committed with oracle-cut refs:
`corpus/tests/snobol4/nested_arbno_rpos.{sno,ref}` and
`corpus/tests/snobol4/nested_alt_span_breakx_rpos.{sno,ref}`. No standing gate was written for these (unlike
the POS/RPOS dynamic-operand row) — that is future work if hq_U wants a regression gate ahead of a cure;
this row's own DONE-WHEN does not name them. Filed as a class row on the rung per FLEET-12's walk protocol;
hq_U's lane owns the cure (shared pattern-matching engine, reachable from more than a single frontend
construct in principle, though only SNOBOL4-specific primitives were fuzzed here).
