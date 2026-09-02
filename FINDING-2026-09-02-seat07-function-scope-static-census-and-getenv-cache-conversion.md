# FINDING — `census-function-scope-mutable-statics-under-src`: compile-time population discarded under scope re-cut (and independently found to regress a corpus witness); runtime-only census (108 sites) + gate landed

**Seat:** seat07 · **Date:** 2026-09-02 · **Row:** `census-function-scope-mutable-statics-under-src` (minted hq_P under FLEET-16, on ceo's 2026-09-01 RULES.md line 169 clarification that a function-scope mutable `static` is "or equivalent" under NO-NEW-GLOBALS)
**Tree:** SCRIP `b297334b` (final, post-pull, nothing of mine touches tracked source) · corpus `e7bbc675` · runtime-scoped gate verified, `RT_OPT=-O0`

## ⛔⛔ AMENDMENT, same day, before anything below was pushed — READ THIS FIRST

Everything under "Original finding" below was written against the ROW'S ORIGINAL BRIEF, which read "census EVERY function-scope mutable static under src/, compiler AND runtime." That reading was itself an overshoot, and **ceo re-cut the row's scope (routed through hq_B) before this work was pushed** — verified: `git log`/origin showed none of this session's files present, so the re-cut landed in time.

**Lon, in-chat, verbatim (the ruling): "You can always add as many `g_emit` values as you want. Those were never part of the no global rule. Fix that non-sense that started that mess."** Generalized by the re-cut: **compile-time working state (`src/emitter`, `src/lower`, `src/parsers`, `src/optimizer`, `src/driver`, `src/ir` — everything that runs once per *compilation*, never inside a compiled program's own execution) was never covered by NO-NEW-GLOBALS at all.** Only `src/runtime/` — the tree that becomes `libscrip_rt.so` and is executed by every *compiled* program at *its own* runtime — is genuinely "or equivalent" state in the sense RULES.md line 169 means.

**Consequence for the work below:**
- The **270-site compile-time getenv-cache conversion is DISCARDED, not pushed.** Salvage patch (for provenance, not for reuse): `/home/resources/postoffice/salvage/seat07-census-function-scope-mutable-statics-under-src-compile-time-DISCARDED-2026-09-02.patch`.
- **Independently of the scope question, that conversion also measurably broke something**, found while root-causing an unexpected corpus board result before this FINDING could even be closed: the SNOBOL4 blocking board came back `mode-3 PASS=1678 FAIL=1` (mode-4, the script's hard gate, was clean). The one failure, `pos_rpos_alt_branch_5` (a recursive self-referential deferred pattern, `&R = 'q' *&R | 'z'`), was a **deterministic runtime `ERROR 246` stack overflow** on the converted tree — reproduced 3/3 runs. Bisected cleanly by rebuilding the pre-conversion tree from a `git stash` and re-running the identical witness: **2/2 clean passes**, correct output both times. So the conversion — despite every individual site being a textually-verified pure `static`-keyword deletion with no other byte touched — broke something for real, most likely in `bb_match_defer.cpp` (one of its getenv-cache flags plausibly selects a code-generation strategy that needs to stay *consistent* across `bb_match_defer()`'s two compile-time invocations for this program's two deferred-pattern sites, and de-static-ing let that drift). Root cause not fully traced — moot for landing purposes since the whole batch is discarded, but recorded because **"the transform is provably safe in isolation" and "270 simultaneous applications of that transform are safe" turned out to be different claims**, and a future session must not treat this specific conversion recipe as pre-validated.
- **What survives and IS pushed:** the census instrument (general-purpose, unaffected by the scope question — it takes `--root`), rebuilt and reproven against **`src/runtime/` only** (108 mutable sites, not 529), and the extended gate, re-scoped and re-proven (selftest + a fresh real-tree inject/fail/remove/pass cycle, done again against an actual `src/runtime/` file since the original real-tree proof used the now-out-of-scope `emit.cpp`).

The rest of this document is left as originally written (the census methodology, the three scanner bugs found and fixed, and their numbers are all real and still true statements about the instrument) — read every count and "converted"/"270" claim below as **historical**, superseded by the runtime-only numbers in this amendment and in `scripts/func_scope_static_baseline.tsv`.

## Original finding (compile-time scope, DISCARDED — see amendment above; kept for the instrument's own provenance)

## The number is the finding — but the instrument had to be proven first

The row's own brief says it plainly: "census EVERY function-scope mutable static under src/ ... report the count and the per-file breakdown BEFORE changing anything, because the number is the finding." A naive `grep '^\s+static'` cannot do this in this tree: the codebase's own 200-char/zero-blank-line style routinely crams a whole function — signature, locals, and logic — onto one physical line (`static int zd_omega_test_kind(IR_e op) { static int _tf = -1; ... }`, `src/ir/zeta_depth.c`), so a function-local static is frequently **not the first token on its own line**. A real scanner was required: `scripts/util_census_function_scope_statics.py`, a brace-depth-tracking walker (after stripping comments/string/char literals) that only reports a `static` whose enclosing scope is a genuine function body.

**Per the TWO-PART PROOF fact rule, the scanner itself was watched fail three separate ways before its count was trusted — each is a permanent regression case in `--selftest` (10 cases, all passing):**

1. **Declaration terminator not depth-aware.** The first version stopped at the *first* `;` after `static`, which truncates `static const struct { const char * n; int code; } table[] = {...};` at the struct body's own field separator and reports a struct **field** name (`n`) as if it were the static variable. Fixed by tracking `([{`/`)]}` depth and only accepting a `;` at depth 0.
2. **`extern "C" { ... }` wrapper transparency was broken twice over — and this was the big one.** `src/emitter/emit.cpp` is a file where nearly the *entire* body (line 10 to line ~3767) lives inside one file-spanning `extern "C" { ... }`. The scanner's first fix (making `effective_top()` see past TRANSPARENT frames) still reported only 2 hits, because the SECOND bug is that `EXTERN_C_RE` was matching against the comment/literal-*stripped* text — and the stripper blanks a string literal's quote characters along with its contents, so `extern "C" {` becomes `extern     {` post-strip and a regex looking for the literal text `"C"` can never match, ever. Fixed by reconstructing the "preceding text" window from raw source (offset-sliced, not token-accumulated) so the quotes survive. **Measured effect: emit.cpp went from 2 reported hits to 137** — every function directly nested under that wrapper had been silently invisible to the census.
3. **Array-size name extraction.** `static const char *labels[SMX_STRTAB_CAP];` has no `=`, so "last identifier before the first `=`" degenerated to "last identifier, period" and returned the size constant `SMX_STRTAB_CAP` instead of the variable `labels`. Fixed by locating the name relative to the first top-level `[`.

A global sanity check (raw `{`/`}` count balances to exactly 0 in every one of the 401 scanned files) and a random 20-hit manual sample across files confirm no further desync of this kind survives.

## The census

```
python3 scripts/util_census_function_scope_statics.py
```

**547 total function-scope static declarators under `src/`** (compiler + runtime, all `.c`/`.cpp`/`.h`/`.hh` under the tree) — **529 mutable** (in scope), **18 immutable** (`static const` scalars/arrays and const-qualified anonymous-struct lookup tables — correctly excluded; see bug 1 above for why that exclusion needed its own fix).

Shape breakdown of the 529, computed by checking each declaration's 3-line window for a `getenv(` call assigning the declared name (this is the exact shape RULES.md's cited precedent — `zd_plan`'s `_zd`/`_dg`/`_zoh`/`_zbe`/`_zvd`/`_zo`/`_zs`/`_lp` plus 5 more siblings the precedent hadn't named — is built from):

| bucket | count | disposition |
|---|---:|---|
| getenv lazy-init cache, in **compile-time** dirs (emitter/lower/ir/driver/optimizer/templates/parsers — run once per *compilation*) | 270 | **converted this session** (below) |
| getenv lazy-init cache, in **`src/runtime/`** (becomes `libscrip_rt.so`, executed by *compiled programs* at *their* runtime) | 57 | **left alone** — see Scope guard |
| generated parser/lexer output (`*.tab.c`, `*.lex.c` — bison/flex boilerplate) | 5 | out of scope, not hand-edited |
| test-fixture statics (`*_test.c`) | 5 | lower priority, flagged not converted |
| everything else (scratch buffers, accumulators, near-const tables missing a `const` qualifier, …) | 192 | **needs individual review** (below) |

Full per-file breakdown and every individual declaration: `scripts/func_scope_static_baseline.tsv` (post-conversion ceilings) and a fresh `python3 scripts/util_census_function_scope_statics.py --csv <path>` reproduces the raw list at any time.

## Scope guard: why 57 sites were deliberately NOT converted

The row's own brief: *"Do NOT convert a static that a measurement shows is load-bearing in a HOT RUNTIME path just to satisfy the census."* `src/runtime/**` compiles into `out/libscrip_rt.so`, which is linked into and executed by **every compiled SNOBOL4/Icon/Prolog/… program**, not by the compiler itself. The precedent's own justification for converting — "`zd_plan` runs per graph **at COMPILE time** and getenv walks a few dozen env entries" — does not transfer: a getenv-cache inside `pattern_match.c`, `by_name_dispatch.c`, `rt.c`, `gc_heap.c`, etc. is on a path that can run millions of times inside a single compiled program's own execution, and de-static-ing it would turn a one-time lookup into a per-call syscall paid by somebody else's program. Converting these needs a measurement first, not a census. The 57 sites are listed in the shape-breakdown output above (re-run the classifier snippet in the LEDGER to regenerate the list) and are explicit **not-converted, flagged-for-individual-review** state, per the brief's instruction to "say so loudly rather than minting one retroactively."

## Converted: 270 sites, 265 distinct `static` keywords, 31 files

`scripts/util_convert_getenv_cache_statics_to_read_at_use.py` (dry-run by default, `--apply` to write) performs the transform, and it is a pure deletion: `static int _zd = -1; if (_zd < 0) { _zd = ...; }` behaves identically with `static` removed — the sentinel/lazy-init guard still fires and still sets it correctly, just fresh every call/every loop-reentry instead of once ever, which **is** "read at the point of use." No other byte on any touched line changes. The script edits by the census's own byte offset (not by re-deriving "where is `static`" with a second, potentially-disagreeing text search) and — proven by its own first dry run — a **built-in sanity check refused mid-edit** rather than corrupting anything: several comma-joined declarators sharing one `static` keyword (`static int _zd=-1, _dg=-1, ...;`) were initially recorded once per *declarator*, so the second and third removal attempts landed on text the first had already shifted left, and the script printed `⛔ REFUSED` and stopped rather than mangling the line. Root cause was a missing de-dupe by `(file, offset)`; fixed before any real write.

```
git diff --stat: 31 files changed, 252 insertions(+), 252 deletions(-)
```

## Verified

| check | result |
|---|---|
| `make pristine` (full clean rebuild, `-O0`) | **clean**, zero errors, only a pre-existing unrelated linker note (`missing .note.GNU-stack`, from a hand-written `.S`, not touched this session) |
| `test_smoke_icon.sh` | PASS=14/14 both modes (unchanged) |
| `test_smoke_prolog.sh` | PASS=5/5 all three modes (unchanged) |
| `test_smoke_snocone.sh` | PASS=5/5 (unchanged) |
| `test_smoke_rebus.sh` | PASS=4/4 (unchanged) |
| `test_gate_emit_no_lang.sh` | PASS |
| `test_gate_icn_no_stack.sh` | PASS (0/0) |
| `test_gate_icn_one_reg_frame.sh` | PASS (both locks) |
| `test_gate_icn_semicolon_required.sh` | PASS (all 3 locks) |
| `test_gate_template_medium_invisible.sh` | PASS (0 violations, self-tests OK) |
| `test_gate_pl_no_new_global.sh` | PASS (unaffected — different mechanism, symbol-name based) |
| SNOBOL4 blocking corpus (`test_corpus_snobol4.sh`, the primary FAIL=0 gate) | mode-4 (hard gate) clean, FAIL=0. mode-3: **1 FAIL** (`pos_rpos_alt_branch_5`) — see the AMENDMENT above; this is the regression that, together with the scope re-cut, is why the compile-time conversion below is discarded rather than landed |

None of the converted files are on the Icon/Prolog/Snocone/Rebus-exclusive path (SHARED-NODE VERDICT SCOPE: `src/` is shared by every frontend), so the four smokes are the meaningful control arms for language-specific breakage; the SNOBOL4 corpus is the volume/depth check given 26 of the 31 touched files are SNOBOL4-heavy (`lower_snobol4.c`, the `bb_match_*.cpp` family, `x86_asm.h`).

## The extended enforcement gate

`scripts/test_gate_no_new_function_scope_static.sh` — the "extend the enforcement grep" half of the row's DONE-WHEN. **Mechanism: a per-file ratchet**, not a single scalar total and not a symbol-name allowlist (unlike `test_gate_pl_no_new_global.sh`'s `g_*` SANCTIONED list) — function-scope statics are overwhelmingly named with short, non-unique locals (`v`, `on`, `m`, `p`, …), so a name is not a stable identity across functions; a per-file **count**, checked against a checked-in baseline (`scripts/func_scope_static_baseline.tsv`, generated from this session's post-conversion state: 259 mutable sites across 64 files), is stable under line-number churn elsewhere in the file and catches a genuinely new site without depending on a growing-corpus total (the INSTRUMENT LAWS' count-only-criteria warning is about a *global* total measuring the corpus instead of the work; a *per-file ceiling* that starts at the current true state does not have that failure mode — a new site in File A cannot hide behind a conversion in File B). A file absent from the baseline has an implicit ceiling of **zero**. A declaration line containing the literal marker `GRANT:` is excluded from the count entirely — the function-scope sibling of the file-scope SANCTIONED-list comment blocks, for the "genuine required state, needs a cited grant" bucket the brief calls for; **zero sites use it yet**, since none of the 259 remaining mutable sites have been individually adjudicated as genuinely-required.

**Watched fail, then watched pass — twice over, per the brief's explicit instruction:**
- `--selftest` (embedded, re-runnable any time): 3 cases against a sandboxed tree — clean tree passes, one injected offending static is correctly counted (would fail against a ceiling-0 baseline), a `GRANT:`-marked line is correctly identified as excludable.
- **Against the real, live tree**: one deliberate `static int _fss_gate_negative_test_witness = 0;` was inserted into `bb_emit_end()` in `src/emitter/emit.cpp` (ceiling 18) — the gate printed `FAIL emitter/emit.cpp: 19 function-scope mutable static(s) > ceiling 18` and exited 1. Removed; the gate printed `PASS` and exited 0, and `git diff` on the file shows zero leftover artifact from the injection.

## Scope correction compliance (Lon's `g_emit` note, added to this row's baton mid-session)

The task baton carries a 2026-09-02 addition: `g_emit` fields need no grant and this census "must not touch them" — an earlier overshoot on the same RULES.md clarification cost five seats cycles pricing a permission that was never required. Checked before writing this up: **zero occurrences of `g_emit` in the census CSV** (it only ever scans function-scope `static` declarations, and `g_emit`/`g_emit_cfg` are pre-existing file-scope globals, never a function-local static, so they were structurally never reachable by this instrument); **every `-`/`+` line in the applied diff is the `static` keyword removal itself** — `g_emit`/`g_emit_cfg` appear only as unchanged surrounding context in a few hunks (e.g. `bb_classify_node`, `frame_need_of`), never touched.

## What's NOT done under the compile-time reading (moot — kept for the record only)

The four items originally listed here (review the 57 runtime sites, classify the 192 "everything else," lower the baseline per conversion, wire the gate into `make test`) are superseded by the re-cut NEXT block in the task baton. Do not work from this list; work from the baton.

## What actually landed (runtime-only scope, final)

- **Census, scoped to `src/runtime/` only:** `python3 scripts/util_census_function_scope_statics.py --root src/runtime` → **113 total, 108 mutable, 5 immutable**, across 17 files. Per-file ceilings: `scripts/func_scope_static_baseline.tsv`.
- **Gate, re-scoped:** `scripts/test_gate_no_new_function_scope_static.sh` now defaults `CENSUS_ROOT` to `$ROOT/src/runtime` (override with `FSS_ROOT`). Re-proven both directions AGAIN against the real tree post-re-cut (the original real-tree proof used `emit.cpp`, now out of scope): injected `static int _fss_gate_negative_test_witness` into `src/runtime/rt/bbprof.c` (ceiling 1) → gate printed `FAIL rt/bbprof.c: 2 function-scope mutable static(s) > ceiling 1`, exit 1; removed → `PASS`, exit 0, `git diff` on the file empty.
- **Nothing else is pushed.** No tracked source file changes ship from this row this session — `git status` on SCRIP shows only the new scripts + baseline TSV as untracked additions. The 270-site compile-time conversion never left the stash/salvage patch.
- **Salvage:** `/home/resources/postoffice/salvage/seat07-census-function-scope-mutable-statics-under-src-compile-time-DISCARDED-2026-09-02.patch` — the discarded diff, kept for provenance and as the cautionary witness described in the amendment. Also referenced from `util_convert_getenv_cache_statics_to_read_at_use.py`'s own header, since that script's default targeting still points at the now-out-of-scope compile-time dirs and must not be `--apply`'d as-is.

## AMENDMENT 2, same day, after the DONE-WHEN instrument was confirmed pushed — the 96 remaining runtime sites, classified

Picked back up after confirming `e534efdc` (the census+gate landing) was on `origin/main` and re-proving DONE-WHEN fresh
post-pull (commit `72c7ec09` absorbed in between, one runtime touch — `by_name_dispatch.c`'s `dop_call_nothrow` floor
fix — verified to add no function-scope statics). This amendment covers NEXT items 4 and 5 from the re-cut baton: measure
the 57 getenv-cache sites, classify the 39 "everything else" sites (the row's 192-count shrank to this once re-scoped to
`src/runtime/` only: 108 mutable − 57 getenv = 51 everything-else at the time, minus 12 reclassified below = 39).

**Method for the 57 getenv sites:** grouped by enclosing function (a brace-depth walker reusing the census's own
`looks_like_function_opener`, skipping `if`/`while`/`for`/`switch` blocks to find the true outer function), then measured
call-site count per function (`grep -c` across `src/`) and read each function's file/name/immediate context. **Verdict:
all 57 are hot-path, none converted.** No file among the 13 involved (`aggregates.c`, `by_name_dispatch.c`, `keywords.c`,
`pattern_match.c`, `runtime_eval.c`, `runtime_init.c`, `core/core.c`, `rt/bbprof.c`, `rt/gc_heap.c`, `rt/portcount.c`,
`rt/rt.c`, `rt/rt_arena.c`, `rt/zeta_alloc.c`) is init-only — every one is reachable from pattern matching, GC, eval-chain
construction, by-name dispatch, or Prolog term/cell allocation, i.e. code whose call count scales with the COMPILED
PROGRAM's own workload, not with compilation count. Concrete evidence, not just file-level vibes: `NV_SET_fn` (named-
variable store, `core/core.c`) has 48 call sites and an adjacent comment already measuring it at **17,600 calls in a
single benchmark** (`roman.sno`); its own `_xd` getenv-cache already carries an inline WHY-comment citing a real row
(`perf-match-begin-beta-cure`) — this is the row's OWN cited-precedent shape, just without the literal `GRANT:` token.
`runtime_init.c`'s `zsm_aexp_on()` looked plausibly init-time from the filename alone but is read from a per-α-port-entry
RSP assertion (`runtime_init.c:119`) — i.e. every box activation, not process start; reading the actual call site rather
than trusting the filename mattered here. Full per-function call-count table: reproduce via the query in AMENDMENT-2
REPRODUCE below (`by_func.json` intermediate not checked in — regenerate, don't hunt for it).

**The 51 everything-else sites split into two groups on inspection:**

1. **12 near-const lookup tables, reclassified (not GRANTed) — landed this commit (`0dfeca9f`):** `static const char
   *name[] = {...}` / `static const char *name = "...";` tables/strings that the census correctly calls MUTABLE (the
   binding itself isn't const-qualified) but that are, in fact, never written after their initializer — verified by
   grepping every one of the 12 for `name =` / `name[N] =` outside the declaration line (zero hits, all twelve) before
   touching anything. Tightened to `static const char *const name...`; the compiler, not just the grep, now enforces it
   — a future write would fail to build rather than silently regress. Sites: `icn_known`, `known`, `builtins`, `op2`,
   `op1`, `UCASE`, `LCASE` (`by_name_dispatch.c`), `names`, `feats` (`keywords.c`), `known_kw` (`core/core.c`), `S`
   (`rt/rt.c`), `graphic` (`unification.c`). This is the row's own predicted bucket — "near-const tables merely missing
   a const qualifier (tighten the declaration instead of converting or granting)" — landing exactly as anticipated.
   Runtime census: 108 → 96 mutable, 5 → 17 immutable. Verified: `make pristine` clean; smokes icon 14/14, prolog 5/5,
   snocone 5/5, rebus 4/4 unchanged; 6 invariant gates clean; SNOBOL4 blocking corpus **mode-3 PASS=1679 FAIL=0, mode-4
   PASS=1679 FAIL=0 SKIP=0** — strictly cleaner than the discarded compile-time pass, which had a mode-3 regression.
   Baseline re-lowered same commit (manual ratchet, per the TSV's own header law): `by_name_dispatch.c` 27→20,
   `core/core.c` 9→8, `keywords.c` 12→10, `rt/rt.c` 11→10, `unification.c` 1→0 (row dropped — its only mutable site is
   gone, and the TSV's own convention is that an absent file has an implicit ceiling of 0, so the row was removed
   rather than written as an explicit 0).

2. **39 genuine-state sites, classified by shape, NONE converted or GRANT-marked — not committed, this is a reading, not
   a diff.** Sub-buckets, with the two riskiest confirmed by reading the actual code rather than inferred from the name:
   - **One-time registration / idempotency guards (6):** `done` (`keywords.c:213` `kwb_init_once`, `runtime_init.c:94`
     `rt_zdp_sm_init`), `already` (`core/core.c:222` `mon_at_exit`), `armed` (`core/core.c:2641`
     `rt_dump_atexit_arm`), `primed` (`keywords.c:82` `kw_cset_prime`), `hooked` (`rt/portcount.c:58`). Converting any
     of these to read-at-use does not just cost perf — it breaks the guard, running one-time setup on every call. Not
     a judgment call.
   - **`_reg`-suffix one-time `DEFDAT_fn` registration guards (5), confirmed by reading all five, same idiom exactly:**
     `list_reg3` (`by_name_dispatch.c:4992` `rt_make_list`), `list_reg2` (`by_name_dispatch.c:6523`
     `try_call_builtin_by_name_bl`), `list_empty_reg`, `list_slice_reg` (`pattern_match.c:377,385` `rt_list_view`),
     `so_list_reg` (`string_ops.c:26` `so_is_list`) — all five are `if (!X) { DEFDAT_fn("list(...)"); X = 1; }`,
     registering the same `list(...)` frame-datatype once per process, not a cache of a computed value. Same bucket as
     the idempotency guards above, not the "needs individual judgment" scratch-buffer bucket a name-only guess
     ("_reg" reads like "cached register") would have placed them in.
   - **Monotonic unique-ID counters (2):** `opq_uid` (`pattern_match.c:51`), `arb_uid` (`pattern_match.c:81`) —
     converting these to read-at-use breaks uniqueness, i.e. a correctness bug, not a perf question.
   - **Lazy-init cache, same risk profile as the 57 getenv sites (1 function, 2 declared names but really one site
     read twice in a comma-declarator):** `dot_sl` (`by_name_dispatch.c:1431` `dop_unify_lst`, and `1455`
     `dop_ix_g` — two different functions, same name and shape) memoizes a `prolog_atom_intern(".")` result packed
     with an arity into one `uint32_t`, guarded by `if (!dot_sl)`, on Prolog **unification** — as hot a path as this
     codebase has. Should have been caught by the getenv-shaped classifier and wasn't, because it isn't `getenv(
     )`-shaped; same disposition as the 57 (flagged, not converted) applies here by the identical reasoning, not by
     the shape match.
   - **`cs` × 2 (`keywords.c:318,336`):** `static const char *cs = NULL;`, confirmed reassigned elsewhere in the
     same function (`cs = stable;`) — a genuine lazy pointer cache, correctly excluded from the Bucket-1 "never
     reassigned" tightening (this is exactly why every Bucket-1 candidate was grepped individually rather than
     pattern-matched on declaration shape alone).
   - **Small rotating/scratch state, read in context but not exhaustively call-counted (6):** `g_rm`/`g_rm_off`
     (`by_name_dispatch.c:5380-5381`, `bn_replace` — REPLACE builtin; sits directly below an existing WHY-comment
     about a measured 26,400-call/run killswitch-hoisting fix in the same function, strong circumstantial evidence
     this is hot too) and `stress_n`/`stress_c` (`rt/gc_heap.c:182`, GC stress-testing counters).
   - **Scratch/accumulator buffers, shape-classified only, not individually read (13):** `a`×2, `ascii_str`,
     `cset_str`, `hbuf` (`keywords.c`, 128B–256B char buffers, formatting/charset scratch), `ub` (`by_name_dispatch.c`,
     32B), `acc_names`/`acc_types`/`acc_idx`/`acc_var`/`acc_fixed` (`by_name_dispatch.c:869,2718` — the largest,
     `[256][192]` and `[256][8][32]` accumulator tables, tens of KB each, baked permanently into `libscrip_rt.so`'s
     BSS). The large `acc_*` tables in particular are exactly the SUPERSEDED-NEXT's "larger accumulator buffers —
     needs individual judgment" bucket, not a rubber-stamp GRANT: why 256 slots, why static instead of stack or
     heap, is a real design question this session did not chase.
   - **Test-fixture (5, matches the original FINDING's own precedent bucket, lower priority):** `rtx_str_test.c`
     (`big`, `big2`), `rtx_varval_test.c` (`abc`, `empty`, `longs`) — both inside `main()` of a `*_test.c` file.

   **Why none of the 39 got a `GRANT:` comment this session, even the unambiguous ones:** the gate is a per-file
   *ratchet* against the checked-in baseline, not a per-site allowlist — it already passes with all 96 remaining sites
   present and does not require an individual grant to stay green. Minting `GRANT:` on 39 sites (or even just the 8
   unambiguous guard/counter ones) without an actual citation would be manufacturing the citation after the fact — the
   row's own brief calls this out by name ("if none exists say so LOUDLY rather than minting one retroactively"). This
   amendment IS the loud say-so; a `GRANT:` marker citing it is a defensible next step for whoever has ruling authority
   to bless, not something to self-issue.

## AMENDMENT-2 REPRODUCE
```bash
cd SCRIP
python3 scripts/util_census_function_scope_statics.py --root src/runtime --csv /tmp/rc.csv   # 113/96/17 post-tightening
bash scripts/test_gate_no_new_function_scope_static.sh                                        # 96/96, zero slack
# per-function call-site counts for the 57 (hot-path) getenv/atom-intern sites: group AMENDMENT 2's CSV rows whose
# 3-line window contains `getenv(` (or, for dot_sl, `prolog_atom_intern(`) by enclosing function, then
#   grep -rn '\bFNNAME\s*(' src/ | wc -l   per function name.
```

## REPRODUCE
```bash
cd SCRIP
python3 scripts/util_census_function_scope_statics.py --selftest              # 10/10 PASS, general-purpose, root-agnostic
python3 scripts/util_census_function_scope_statics.py --root src/runtime     # THE current census, post-tightening: 113/96/17
bash scripts/test_gate_no_new_function_scope_static.sh --selftest            # gate self-proof, both directions
bash scripts/test_gate_no_new_function_scope_static.sh                       # the gate itself, runtime-scoped, 96/96
```

## LEDGER
- [seat07 · 2026-09-02, AMENDMENT 2] Resumed the claim: confirmed `e534efdc` (census+gate) was already on `origin/main`,
  pulled fresh (`72c7ec09`, one runtime touch verified to add no statics), re-proved DONE-WHEN fresh post-pull. Measured
  and classified all 96 remaining runtime mutable sites (57 getenv/atom-intern hot-path caches by call-site count +
  context; 51 everything-else by shape, 12 confirmed never-reassigned and read). Landed `0dfeca9f`: tightened the 12
  near-const lookup tables to `const`, re-lowered the baseline (96/96, zero slack), rebased clean over 5 more concurrent
  commits (none touching statics), re-proved DONE-WHEN a third time post-rebase, pushed. Full verification: `make
  pristine` clean, 4 smokes unchanged, 6 invariant gates clean, SNOBOL4 blocking corpus PASS=1679/1679 both modes
  FAIL=0 (cleaner than the discarded compile-time pass). Remaining 84 non-tightened sites documented by bucket with
  evidence in AMENDMENT 2 above; none converted or GRANT-marked — several would be correctness bugs if silently
  converted, and minting GRANT: without a real citation is the retroactive-minting the row's own brief forbids. Routed
  the GRANT-marking question to ceo/Lon rather than deciding it unilaterally; task baton NEXT updated accordingly.
- [seat07 · 2026-09-02] Census instrument built, 3 bugs found and fixed in it (all now permanent `--selftest` regression cases; general-purpose, unaffected by the later scope question). First pass censused all of `src/` (547/529/18) and converted 270 compile-time getenv-cache sites (31 files) — build clean pristine, 4 smokes + 6 invariant gates unchanged, but the SNOBOL4 corpus board came back mode-3 FAIL=1 (`pos_rpos_alt_branch_5`), bisected cleanly to the conversion (stash + rebuild + rerun: pre-conversion 2/2 clean, converted 3/3 broken, deterministic `ERROR 246` stack overflow). Independently, before that regression was fully chased down, ceo (routed hq_B) re-cut the row's scope to `src/runtime/` only, on Lon's ruling that compile-time state was never covered by NO-NEW-GLOBALS — verified not yet on origin, so in time. Discarded the compile-time conversion (salvage patch saved), re-censused and re-baselined `src/runtime/` only (108 mutable / 17 files), re-scoped the gate's default root, re-proved it in both directions again against a real runtime file (`rt/bbprof.c`). Pulled fresh (`b297334b`, absorbing hq_C's large concurrent Term-eradication landing) and re-confirmed the runtime census is byte-identical before finalizing. Nothing but new, additive tooling files ships from this session.
