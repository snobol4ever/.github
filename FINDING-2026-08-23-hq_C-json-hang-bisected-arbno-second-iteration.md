# FINDING: json hang bisected — ARBNO with a separator hangs on its SECOND iteration; 5-byte witness `[1,2]`

**Seat:** hq_C · **Date:** 2026-08-23 (s263, at handoff — row OPEN, not cured) · **Tree:** SCRIP `1257d56c` (post no-pin GC; hq_P verified the hang is identical at `b7d88465`, pre-TABLE-rewrite — pre-existing, unrelated to both)

## The row
hq_P (s262): json/json-match hang on ANY input (37 bytes to 631 KB, identically); json-match-fence returns MATCH-FAILED where the oracle succeeds. Blocks the JSON workhorse benchmark, the most table- and pattern-intensive of Lon's four.

## Reproduced, then bisected by input shape
Program: `corpus/benchmarks/snobol4/demo/json.sno` verbatim minus ZCHK/ZBUD/ZFLR and the harness `-INCLUDE`, plus `OUTPUT = 'check: ' ZBODY(1)` / `END` (hq_P's recipe). Oracle `/home/resources/x64/bin/sbl -bf` answers every case in milliseconds. SCRIP m3, 5s timeout per probe:

| input | scrip | oracle-consistent output |
|---|---|---|
| `1` · `"x"` · `true` · `null` | ✅ rc=0 | ✅ |
| `[]` · `[1]` | ✅ rc=0 | ✅ |
| **`[1,2]`** | ⛔ **HANG** (rc=124) | oracle: fine |
| `{}` · `{"a":1}` | ✅ rc=0 | ✅ |
| **`{"a":1,"b":2}`** | ⛔ **HANG** (rc=124) | oracle: fine |
| `[[1]]` · `{"a":[1]}` | ✅ rc=0 | ✅ |

## The shape of the defect
- **Nesting is innocent** (`[[1]]`, `{"a":[1]}` pass) — the `*jelement` unevaluated-expression recursion works.
- **One element is innocent** (`[1]`, `{"a":1}` pass) — ARBNO taking its empty arm, or zero iterations, works.
- **The second separated element hangs, in BOTH productions**: `jarray`'s `ARBNO(',' *jelement)` and `jobject`'s `ARBNO(',' jmember)`. The witness is 5 bytes: `[1,2]`.

So `ARBNO(sep item)` fails to terminate once it has completed one real iteration and must then stop (next char is `]`/`}`). Same family smell as the standing front red **160_pat_alt_inner_gen_resume** (inner generator resume under alternation) and the deliberate red `demo_treebank` (row vlist-expr-alternation): ARBNO here wraps an alternation-bearing element (`jvalue` is a 7-arm alternation reached through `*jelement`), and the hang begins exactly when ARBNO must recede/settle after iterating across it. Note also the ARBNO pend-cursor banking cure of s263 (`ba628703`, calculator-2) touched the ARBNO-FRAME arm — adjacent machinery, different symptom (that was a double-fire, this is non-termination), possibly the same frame state family.

## Next session starts here
1. Mint the standalone witness: a ≤10-line .sno with `P = '[' *E ARBNO(',' *E) ']'`-shaped grammar (E an alternation with a recursive arm) against `[1,2]` — confirm it hangs outside json.sno entirely (ASM-DIFF-FIRST wants the smallest witness before any tracing).
2. Ablate the element: replace `*jelement` with a literal (`ARBNO(',' '1')` over `1,2`?) — if that completes, add back alternation, then recursion, one ingredient at a time; the first ingredient that hangs names the class.
3. Then diff `--dump-bb`/emitted `.s` of passing-vs-hanging witness pair around the ARBNO ports (α/β/γ/ω wiring), only then gdb with a spin count.
4. Fix belongs wherever ARBNO's recede path resumes the inner generator — check against 160's analysis before assuming a new class.
