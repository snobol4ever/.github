# FINDING 2026-07-22 CLAUDE s126 — SN4 MATCH-ISOLATED BENCHMARKS + EVAL-ARG DEFERRED-CALL REPRODUCER

**New corpus programs (HEAD `abe72c93`, PURE per Lon s126 correction):** `programs/snobol4/demo/claws5-match.sno` + `treebank-match.sno` — the ONE BIG MATCH lifted from claws5.sno/treebank-list.sno with ALL side effects stripped: no `. var` captures, no `(epsilon . *fn())` deferred calls, no counters. Language recognized is identical (all removed elements match empty/transparently), so success/failure stays oracle-checkable; output is `matched bytes=N`. Refs from fork sbl `-CASE 0`. An INTERMEDIATE side-effect-counter version (captures + NRETURN workers + EVAL-arg deferred calls) exists at corpus `7d0c50e3` — kept in history as the bug reproducer below. Purpose of the pair-of-pairs: a cost LADDER — pure scan → +deferred-call machinery (7d0c50e3 versions) → +TABLE/SORT/print (the full originals).

## Benchmark ladder (ALL SCRIP NUMBERS ARE `-O0` RUNTIME per O2-DIRECTED-ONLY; officials optimized; 5-rep medians, this container)
| program | fork sbl | official csn | SCRIP m3 | SCRIP m4 |
|---|---|---|---|---|
| claws5-match PURE (HEAD) | 36ms | 146ms | 40ms | **38ms** |
| claws5-match +side-effect calls (7d0c50e3) | 42ms | 343ms | 59ms | 55ms |
| claws5 FULL (tables+SORT+print) | 60ms | 337ms | 166ms | 139ms |
| treebank-match PURE (HEAD) | 76ms | 192ms | 119ms | **117ms** |
| treebank-match +side-effect calls (7d0c50e3) | 94ms | 1389ms | BLOCKED (bug) | BLOCKED |

**Read (m4 vs fork sbl):** pure flat scan **1.05×** — SCRIP's emitted scanner is AT SPITBOL PARITY even with `-O0` runtime. Pure recursive parse (deferred `*group`/`*delim` variables) 1.54× — the recursive deferred-pattern eval is a real but modest gap. Adding the deferred-call machinery costs SCRIP +17ms (38→55) and CSNOBOL4 +197ms (146→343!). Adding TABLE/SORT/print costs SCRIP another +84ms (55→139) vs SPITBOL's +18ms — the dominant SCRIP loss is TABLE/SORT/OUTPUT-shaped, confirming the s125 "losses are C-library shaped" diagnosis with a controlled A/B/C.

## Reproducer for the PAT$-not-registered bug (owned by the parallel session — NOT pursued here, Lon directive)
`treebank-match.sno` on SCRIP (both modes): match SUCCEEDS, `pops=12332` CORRECT, but groups/grpchars/words/wrdchars/banks/sig all NULL + `SNO$MKPAT: compiled pattern blob 'PAT$5..9' not registered` on stderr.
**Reproducer location: corpus `7d0c50e3` `treebank-match.sno`** (superseded in HEAD by the pure version — check out that hash). **The delta is two forms in ONE program:** bare `Pop_grp = epsilon . *pop_grp()` (no EVAL, no arg) → fires 12332/12332. EVAL-built `Push_grp = EVAL("epsilon . *push_grp(" vs ")")` (arg-bearing) → NEVER fires, its blob is the unregistered PAT$. **Second data point from the PURE rewrite (HEAD): with the EVAL-arg workers stripped but recursive `*group`/`*delim` deferred VARIABLES kept, SCRIP passes 4-way on the full corpus — the recursive deferred-variable path is CLEAN; the fault is exclusively the EVAL-built arg-bearing deferred-call path.** (A ~15-line standalone snippet of the same delta hit an UNRELATED SCRIP parse error — not bisected, oracles print n=1 m=1; use the corpus reproducer.) Fingerprint sits at the join of s123 PAT$/EXPR$ dedup (`2b0c9bc3`) and the standing ZS-3 "arg-bearing EXPR$ path broken" note. Full treebank-list.sno additionally hard-fails the whole match ("Pattern match failed"), so treebank-match is the SMALLER repro.
**Also:** old `treebank-list`/`treebank-array` full-corpus runs (VBGinTASA.dat) fail on SCRIP the same way — the crosscheck suite never caught it because it runs the small `treebank.input`.

## Portability finding: SPITBOL raw-mode ONE-BIG-READ is a 3-engine dead end
Manual (v3.7, INPUT options): `[-rn]` raw mode reads exactly n chars incl. newlines, capped by `&MAXLNGTH`. Probe `INPUT(.src, 0, '[-r200000]')`: fork sbl misbehaves (blank output), **official csnobol4 SEGFAULTS on the option string**, SCRIP silently no-ops the association (reads null). So cross-engine "one big read" = slurp-into-memory before the match (what both programs do); true single-syscall read is per-engine work if ever wanted.

## Oracle/руnner notes (repeat of s126 chat, for the record)
Official spitbol/x64 v4.0f is **lowercase-native, no `-CASE` card** (folds by default; `-f` = case-sensitive but wants lowercase `end`) — corpus programs need the **fork** sbl. Official csnobol4 needs `-d 8m -P 4m -S 4m` for these (Error 16 pattern-stack overflow at defaults). `build_official_oracles.sh` idempotency hazard: an interrupted clone leaves `.git` with empty worktree and the `[ -d .git ]` guard then skips re-clone and `make`s an empty dir.
