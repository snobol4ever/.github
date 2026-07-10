# FINDING — SN4 nested-blob DEFER callout is the single class behind 143 / 124 / 147
2026-07-10, Claude (s14 continuation). Probe-proven by 10-cell discriminator matrix vs the fork oracle; theory made one successful prediction before recording. Root NOT yet localized — next step is MONITOR/gdb per RULES.md (static stabs exhausted honestly).

## THE LAW (all ten probes, m3, oracle-agreeing refs)
A pattern match FAILS wrongly **iff a stored pattern's compiled blob itself contains a DEFER callout of another stored pattern (blob-in-blob)**. Callouts made from STATEMENT level — any number, any content — are green.

| probe | shape | SCRIP | oracle |
|---|---|---|---|
| A | inline `ARBNO(*LP)`, LP deterministic (`'a'`) | yes | yes |
| B | inline `ARBNO('a'\|'b'\|'c')` (v2, no defer) | yes | yes |
| C | statement `*LP`, LP = FENCE(alt), first alt taken | yes | yes |
| C2 | statement `*inner`, second forward alternative forced | yes | yes |
| D | statement `*inner *inner` (double callout, same blob) | yes | yes |
| E | statement `*inner *inner`, FENCE inside blob | yes | yes |
| G | **inline** `ARBNO(*LP)`, LP = generator blob (`'a'\|'b'\|'c'`) — the theory's prediction | yes | yes |
| p143 | `R = ARBNO(*LP)` **stored**, then `s ? R` | **no** | yes |
| pF | `outer = (*inner ' ' *inner)` **stored**, then `s ? outer` | **no** | yes |
| (124/147/143 corpus tests) | each contains a stored pattern whose blob defers another stored pattern | FAIL | ref |

Minimal repro (8 lines): `inner = ('a' | 'b')` · `outer = (*inner ' ' *inner)` · `'a b' POS(0) outer RPOS(0)` → SCRIP N, oracle Y. No fence, no ARBNO, no capture — pure one-level blob nesting.

## FRAMINGS CORRECTED EN ROUTE (do not resurrect)
1. "FENCE-in-blob" (test names suggest it) — exonerated twice: probe E (fence-in-blob double callout green) and pF (red with zero fence nodes).
2. "ARBNO × generator-blob" (this session's own first theory) — falsified by probe G: inline ARBNO of a generator blob is green; 143 is red only because `R` is itself stored.
3. NEXT BRACKETS' old grouping of 124/143/147 under the FENCE family — superseded; they are ONE nesting class.

## TEST MEMBERSHIP
- 143: `R = ARBNO(*LP)` — R's blob defers LP.
- 124: `token = (kw . K | ident . I)` — token's blob defers kw. (Note: also carries captures + outer-ALT resume; if the nesting fix alone doesn't flip it, THAT residual is the next bracket, not a refutation of this class.)
- 147: `outer = (*inner ' ' *inner)` — the minimal shape itself.

## MECHANISM SUSPECTS (unverified — bracket these with the monitor, do not stab)
The blob call protocol works at depth 0 and breaks at depth 1, so suspect state that is per-MATCH or static rather than per-INVOCATION: (a) callout re-entrancy — `rt_defer_get_pat_fn`/call-site scratch or cursor hand-off registers clobbered by the inner invocation before the outer blob resumes; (b) the blob's ok/no exit wiring assuming statement-level HEAD/RELEASE context that doesn't exist one level down; (c) the px-compile of the OUTER blob lowering its TT_DEFER nodes against blob-local succ/fail that the runtime callout then mis-threads. Distinct from 074/W07 (β-resume INTO a returned blob — a resume-direction gap); this is α-forward at depth 1. Relation to DP-7: non-recursive nesting is DP-7's prerequisite rung — `*group` self-reference needs depth-N; fix depth-1 first.

## NEXT STEP (per RULES.md MONITOR-FIRST — the static stab budget is spent)
`bash scripts/test_monitor_2way_sync_step_bin.sh` on the 8-line repro (fork oracle's patched TIME() is required and present at /home/claude/x64), bracket first divergence, gdb spin-counter at the callout entry, single-step the depth-1 invocation boundary.
