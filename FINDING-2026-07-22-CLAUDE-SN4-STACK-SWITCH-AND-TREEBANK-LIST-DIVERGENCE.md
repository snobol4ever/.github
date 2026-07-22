# FINDING 2026-07-22 (Claude) — SPITBOL `-s`/`-m` memory switches LANDED; treebank-list/array capture-path divergence ISOLATED

## PART 1 — LANDED: SPITBOL-compatible memory switches + default stack floor (fixes treebank-match crash both modes)

### Problem
`treebank-match.sno` on the full `VBGinTASA.dat` (1977 lines / 100155 bytes) **segfaulted in BOTH modes**
(m3 in-process, m4 compiled binary), while SPITBOL produced `matched bytes=100155`. Root cause: the deep
recursive `*group`/`*delim` ARBNO backtracking rides the C machine stack (ζ-on-RSP / FORTH port), which is
capped by `RLIMIT_STACK` (OS default 8 MB). SPITBOL uses a heap-sized pattern stack (`-s256m -d512m` in the
program's own run-comment), so it scales. **Empirical boundary:** binary-searched the smallest crashing input
= 900 lines / 45 KB. ulimit sweep: 8 MB → segfault, 16 MB → segfault, **20 MB → works**, 64 MB → works.
Below 900 lines SCRIP AGREES with SPITBOL byte-for-byte (incl. correct `Pattern match failed` on
truncated-paren inputs), so the pattern *logic* was already correct — this was pure stack exhaustion.

### Discovery: the SPITBOL memory switches did not exist yet
The driver (`src/driver/scrip.c`) parsed only `--`-prefixed long options (the loop required `argv[i][1]=='-'`),
and there was **no `setrlimit` anywhere in the tree**. So the SPITBOL-style single-dash memory switches
Lon referenced had to be implemented.

### Manual spec (SPITBOL manual v3.7, Running SPITBOL / Command Line Options, p.163-164)
Options precede input files; numeric args may append `k` or `m` (decimal, no embedded punctuation; `8m`=8388608):
- **`-sN`** max stack space (SPITBOL default `-s32k`)
- **`-dN`** max dynamic heap area (default `-d64m`)
- **`-iN`** heap growth increment / min start (default `-i128k`)
- **`-mN`** max object size → `&MAXLNGTH` (default `-m4m`)

### Change (driver + runtime, NO emitter/template/lower touch → no `.s` regen per RULES step 4)
`src/driver/scrip.c`:
- `#include <sys/resource.h>`.
- `parse_mem_arg()` — k/m-suffix decimal parser (returns bytes, -1 on bad).
- `apply_stack_limit()` — raises `RLIMIT_STACK` soft limit (never lowers; clamps to hard limit). Hard limit
  in this container is `unlimited`, so an unprivileged raise succeeds and the kernel grows the stack on demand.
- A single-dash parse loop AFTER the long-switch loop: `-sN` → `apply_stack_limit`; `-mN` → sets
  `extern long g_maxlngth` (`&MAXLNGTH`, keywords.c); `-dN`/`-iN` accepted for SPITBOL-invocation
  compatibility (documented as NOT resizing SCRIP's unified GC arena, which is not byte-sized — honest, not faked).
- Usage text updated with a "Memory options (SPITBOL-compatible)" block.

`src/runtime/core/core.c`:
- `#include <sys/resource.h>`; `int core_stack_floor_raised = 0;`.
- At the TOP of `core_lib_init()` (which runs first in BOTH modes — m3 driver call + m4 emitted `.s` call),
  a one-time **default stack floor of 64 MB** (env-overridable via `SCRIP_STACK`, k/m suffix). Never lowers an
  already-higher limit, so an explicit driver `-s256m` (mode-3, applied before core_lib_init) wins. This is why
  mode-4 (which does not parse scrip flags) also gets the fix.

### Design decision (Lon granted "all your choices")
Default raise lives in the runtime so BOTH modes "just work" out of the box (benchmarks run without a flag),
`-s` is the explicit mode-3 override, `SCRIP_STACK` is the env knob (and can LOWER for testing — verified:
`SCRIP_STACK=8m` reproduces the crash, proving the env is honored). The rlimit is a lazy ceiling (Linux grows
the stack VMA on fault), so a 64 MB floor costs nothing unless used. Faithful to SPITBOL (whose own docs invoke
`-s256m`) while removing per-invocation friction that fought the "benchmarks working" goal.

### Verification
- treebank-match FULL, **out of the box, NO flags**: m3 `matched bytes=100155`, m4 `matched bytes=100155`,
  both byte-identical to `treebank-match.ref` and SPITBOL. ✓
- `-s256m` override ✓; `-s 20m` separate-arg form ✓; `-m8m` → `&MAXLNGTH`=8388608 ✓; bad value rejected ✓;
  `-d512m -i64m` accepted ✓; `SCRIP_STACK=8m` → crash (env honored) ✓.
- claws5.sno / claws5-match.sno / treebank-match.sno all green both modes.
- **sno smokes 7/7 × 2** (m3 + m4). **crosscheck m3 302/8, m4 302/6, DIVERGE=0** — byte-identical to the s126
  watermark, same pre-existing fail set, ZERO regression.
- House style: all edited lines ≤ 200 cols (pre-existing `--zeta` 420/678-col dispatch lines untouched); no
  `//`, no blank lines introduced.

---

## PART 2 — ISOLATED, NOT YET FIXED: treebank-list.sno / treebank-array.sno produce wrong output (capture/deferred-side-effect path)

### The divergence (a WRONG-VALUE bug, distinct from Part 1's crash and distinct from oracle flags)
Running the FULL programs `treebank-list.sno` / `treebank-array.sno`:
- **Oracle-flag caveat first (ruled out):** SPITBOL `-b` throws `ERROR 217 -- duplicate label` (×10) because
  SPITBOL case-FOLDS labels by default and these programs use mixed-case labels (`Init_list` vs `init_list`,
  etc.). **`sbl -bf` (no-fold) compiles clean** and produces the full parse tree. SCRIP is case-sensitive
  (RULES: "SCRIP IS CASE-SENSITIVE"), so it never collides — SCRIP's posture is arguably more correct, and the
  correct oracle invocation for these programs is `sbl -bf`. The `.ref` files match `sbl -bf`.
- **The real bug:** with the correct oracle (`sbl -bf`) and the shipped `.ref`, SCRIP DIVERGES:

  | input | SPITBOL -bf / .ref | SCRIP m3 | SCRIP m4 |
  |-------|--------------------|----------|----------|
  | one tree `(S (NP (DT The) (NN cat)) (VP (VBZ sits)))` | `( 'BANK', ( 'ROOT', ('S', ('NP', ('DT', 'The'), ('NN', 'cat')), ('VP', ('VBZ', 'sits'))))) ` | `()` | (list) `Pattern match failed` |
  | treebank.input (4 trees) | full nested tree (see `treebank-list.ref`) | `()` | list: `Pattern match failed`; array: per-tree `Parse failed on: ...` then `('BANK', ('ROOT'), ('ROOT'), ('ROOT'), ('ROOT'))` |

### Isolation already done (the bracket is narrow)
**The pure matcher is NOT the problem.** `treebank-match.sno` (same grammar, captures + `(epsilon . *fn())`
side-effects STRIPPED) accepts the exact same one-tree input identically in both engines (`matched bytes=43`
each). So the pattern-matching ENGINE is correct. The divergence is entirely in what `treebank-list`/`-array`
ADD on top of the match:
- conditional-assignment captures on the recursive `*group`/`*delim` deferred VARIABLES, and
- the list/array BUILDING via `EVAL("epsilon . *push_list(" vs ")")` etc. — i.e. deferred-expression
  `epsilon . *fn(args)` bare-call side effects WITH ARGUMENTS.

This lands squarely on the **already-open ZS-3 / deferred-expr work** in the SNOBOL4-BB LIVE CURSOR:
`pattern_match.c:670` is annotated "the arg-bearing EXPR$ path is STILL broken (ZS-3)", and the crosscheck's
own persistent fails `140_pat_eval_double_fn_trick` / `141_pat_eval_double_fn_arbno` are the reduced form of
exactly this shape (arg-bearing `*fn()` inside a deferred/ARBNO pattern). treebank-list/array are the
full-scale manifestation.

### MONITOR-FIRST starting point for the next session (RULES.md)
This is a wrong-VALUE divergence where the engines agree up to a first point → the 2-way sync-step monitor
brackets it. Recommended:
1. `scripts/test_monitor_2way_sync_step_bin.sh` (or 3way `PARTICIPANTS="spl scr"`) on **treebank-list.sno with
   the ONE-tree `/tmp/one.input`** (`(S (NP (DT The) (NN cat)) (VP (VBZ sits)))`) — smallest input that already
   shows `()` vs the full tree. Read the first-divergence table; the bug is bracketed between it and the prior
   agreeing event.
2. Expect the divergence at the first `epsilon . *push_list(...)` / `*push_item(...)` deferred arg-bearing call
   (the capture that should append to the growing list). Cross-reference `pattern_match.c:670` and the
   140/141 reduced repro before single-stepping.
3. Fixing 140/141 (the reduced ZS-3 arg-bearing EXPR$ path) very likely fixes treebank-list/array as a
   by-product — verify by re-running the one-tree repro, then the 4-tree `treebank.input`, then diff vs
   `treebank-list.ref` / `treebank-array.ref`.

### Scope note
Part 1 (stack switches) is a clean, fully-gated, self-contained landing and is committed. Part 2 is documented
here as the next rung rather than rushed — it is a meatier deferred-side-effect defect that deserves a proper
monitor-first session, and it shares a root with ZS-3 / 140-141 already on the ladder.
