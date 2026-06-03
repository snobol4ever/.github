# HANDOFF 2026-06-03 (Opus 4.8) — RAKU-BB: fuzz-found epsilon-loop SIGSEGV fixed (IR_NFA_* walker)

## TL;DR

- A **differential verdict-fuzz** between the two mode-2 Raku regex matchers caught the IR-graph
  backtracking walker (`raku_nfa_bb.c nfa_bt_ir_cap`, selected by `RK_NFA_BB=1`) **SIGSEGV-ing on
  82/100 fuzz seeds** while the parallel-NFA oracle (`RK_NFA_BB=0`) ran clean. No verdict divergence
  on the seeds that completed — the walker simply crashed.
- **ROOT CAUSE:** a quantifier over an empty-matchable subpattern — `(a?)*`, `(a*)*`, `()*`, `(|a)*`,
  `(\d*)*`, and the same shapes under a backtrack-forcing suffix (`(a?)*$` on "aab", `(a+)+$`,
  `((a|b|c)*)*$`) — builds an **epsilon loop** in the NFA (`SPLIT → … → back to SPLIT`, no char
  consumed). The recursive backtracker spun on the zero-width cycle and overflowed the C stack. The
  `if (depth > 100000) return -1;` guard is useless here: the stack dies of frame exhaustion long
  before depth 100000. The parallel oracle survives because its eps-closure (`raku_re.c ss_add`) uses
  a per-step `visited[]` array that breaks cycles.
- **FIX:** a **(node,pos) visited memo** mirroring the oracle, in `nfa_bt_ir_cap`. Node id is stashed
  in `IR_t.counter`; a `char` grid of size `n*(slen+1)` (stride = slen+1) is cleared per leftmost-
  sweep iteration in `raku_nfa_bb_exec` and threaded through the recursion. On entry to a node:
  `vi = counter*stride + pos; if (vis[vi]) return -1; vis[vi] = 1;` — **set without restore**.
- **Why (node,pos), not just node:** a single per-node stamp (the rejected first attempt) gets
  OVERWRITTEN when a node is legitimately in-progress at several positions during backtracking
  (stamp set at pos 0, then pos 1, then a pos-0 revisit is no longer cut), re-opening the cycle and
  still overflowing. A 2-D (node,pos) bit never overwrites and cuts every true revisit.
- **Soundness:** for the VERDICT and for ordered (`||`-style) leftmost captures, the first arrival at
  (node,pos) is the highest-priority path; a winning path returns before any sibling re-arrival, and
  a failed (node,pos) subtree yields nothing new on revisit. This is exactly the oracle's per-step
  visited discipline. As a bonus the memo bounds total work at `n*(slen+1)`, so the ordered walk no
  longer degrades to exponential backtracking — catastrophic shapes on 18-20-char subjects that would
  have hung/crashed now finish instantly.
- **Verification:** ~9200 differential probes (100×22 then 250×28) — **0 crashes, 0 divergences**;
  minimal + backtrack-forcing + catastrophic repros all rc=0 and == oracle; new 12-probe epsilon-loop
  TERMINATION battery added to `test_gate_raku_nfa_oracle.sh` (requires both matchers rc=0 AND
  identical); curated RK-NFA-1/2/3 captures stay byte-identical.
- **ISOLATED** to the Raku-only IR_NFA_* walker: SNOBOL4 7/7 / Icon 12/12 m2 byte-unchanged,
  prove_lower2 67/0, FACT md5 ×3 unchanged, concurrency OK. Mode-2 only (leaf templates SHELVED).

## COMMITS

- SCRIP `<this commit>` — fix in `src/parser/raku/raku_nfa_bb.c` + epsilon-loop battery in
  `scripts/test_gate_raku_nfa_oracle.sh`. (Builds on `00ef311` = RK-NFA-2.)
- .github `<this commit>` — GOAL-RAKU-BB.md watermark (RK-NFA hardening note + STATE headline) + handoff.

## THE FIX (precise)

`src/parser/raku/raku_nfa_bb.c`:

1. `nfa_bt_ir_cap` signature gains `(…, char *vis, int stride)` and `s` is now non-const `IR_t *`.
   Immediately after the depth guard:
   ```c
   int vi = (int)s->counter * stride + pos;
   if (vis[vi]) return -1;          /* (node,pos) already explored -> cut (mirrors oracle visited[]) */
   vis[vi] = 1;
   ```
   All 10 recursive calls + the SPLIT case thread `vis, stride`.

2. `raku_nfa_bb_exec`:
   ```c
   int n = bbg->n, stride = slen + 1;
   for (i) bbg->all[i]->counter = i;                 /* node id for the memo */
   char *vis = GC_malloc((size_t)n * stride);
   for (sp = 0..slen) {
       memset(vis, 0, (size_t)n * stride);            /* fresh memo per leftmost-sweep iteration */
       … nfa_bt_ir_cap(start, subject, sp, slen, 0, &cap, vis, stride) …
   }
   ```
   (`start` is now non-const.) The old per-node `state`-stamp reset line was removed.

Safe because `raku_nfa_to_bb`'s `IR_graph_t` is private to the exec path (only caller; confirmed by
grep), so repurposing `IR_t.counter`/`.state` on those nodes touches nothing else.

## HOW IT WAS FOUND (repeatable)

Deterministic seeded generator `/tmp/rknfa2/gen_fuzz.py` (args: seed, n-patterns) emits a `.raku`
battery of `if (SUBJ ~~ /PAT/) say('i Y') else say('i N')` over the SUPPORTED subset only: char, `.`,
`\d \D \w \W \s \S`, `[...]`/`[^...]` with ranges + shorthands, `()`, `<name>()`, `^`, `$`, quant
`*/+/?`, alt `|` (never quantifies anchors; subjects avoid `/ ' \`). Compare VERDICTS only — they
always agree regardless of the `|` LTM vs `||` ordered SPLIT-resolution seam. Run each seed under
`RK_NFA_BB=0` and `=1`; flag any rc≠0 or any diff. Keep ≤30 statements/file (see driver-ceiling flag).

## FLAGS FOR THE TEAM (pre-existing, NOT this change — verified on the pristine tree)

- **Standalone corpus rot:** `test/raku/rk_re32.raku` (uses `raku_nfa_compile`; aborts with
  `[lower2] UNHANDLED role=0 kind=45`) and `rk_re37.raku` (global match/subst) DIFF their `.expected`
  on a pristine build (confirmed by stashing this C change + rebuilding). These files are not wired to
  any automated runner. `rk_re33/34/35/38` pass.
- **Shared mode-2 driver ceiling:** any program with **≥32 statements** aborts (rc=134) with the
  misleading `[SBB] FATAL: mode-2 driver: SNOBOL4 main BB graph not found` — a fixed-capacity IR-pool/
  driver overflow hit before the `RK_NFA_BB` branch, identically under both matchers. Worked around in
  fuzzing by capping files at ≤28-30 statements. Both are out of the isolated RK-NFA lane.
- The walker is a backtracking engine; the memo now bounds the eps-loop case, but very long non-cyclic
  inputs still recurse `O(match length)` deep (a pre-existing theoretical limit, not what the fuzz hit;
  the leaf templates are SHELVED so this walker is the mode-2 IR-graph reference only).

## GATE STATE AT HANDOFF (all green)

```
make scrip / libscrip_rt          rc=0 / rc=0
test_gate_raku_nfa_oracle.sh      RK-NFA-1 (30) + RK-NFA-2 (23 cset/anchor + safe-extent) +
                                  epsilon-loop (12, NEW) + RK-NFA-3 (captures) — all PASS
test_smoke_raku.sh                m2 25/25 HARD ✓ | m3 1/20/4  m4 2/19/4 (UNCHANGED)
test_smoke_snobol4.sh             m2 7/7 ✓ (byte-unchanged — NFA isolation intact)
test_smoke_icon.sh                m2 12/12 ✓
prove_lower2.sh                   67/0 ✓
audit_concurrency_invariants.sh   OK — FACT RULES byte-identical ×3
differential fuzz                 ~9200 probes, 0 crashes, 0 divergences
```

## FILES

- `src/parser/raku/raku_nfa_bb.c` — the (node,pos) visited-memo fix (backup: `/tmp/rknfa2/my_nfa_bb.c`)
- `scripts/test_gate_raku_nfa_oracle.sh` — epsilon-loop TERMINATION battery (12 probes)
- `.github/GOAL-RAKU-BB.md` — watermark RK-NFA-hardening note + STATE headline
- `.github/HANDOFF-2026-06-03-OPUS48-RAKU-BB-NFA-EPS-LOOP-SEGV-FIX.md` — this file

## NEXT (unchanged from RK-NFA-2 handoff)

RK-HY-4 + RK-HY-FENCE blocked on the Icon descr-mode `IR_ASSIGN` ζ-slot store. Otherwise: `map`/`grep`
native (`bb_rk_map.cpp`/`bb_rk_grep.cpp`, inline closure emission — the large lift), RK-GRAM-3 (subrule
seam via the generator PUMP), RK-LOWER-5c/5d (try/CATCH/die, class/method). RK-NFA-4/5 stay SHELVED.
Still deferred: the lockstep "three → four" FACT-RULE roster expansion.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
