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

## REPRODUCE
```bash
cd SCRIP
python3 scripts/util_census_function_scope_statics.py --selftest              # 10/10 PASS, general-purpose, root-agnostic
python3 scripts/util_census_function_scope_statics.py --root src/runtime     # THE current census: 113/108/5
bash scripts/test_gate_no_new_function_scope_static.sh --selftest            # gate self-proof, both directions
bash scripts/test_gate_no_new_function_scope_static.sh                       # the gate itself, runtime-scoped
```

## LEDGER
- [seat07 · 2026-09-02] Census instrument built, 3 bugs found and fixed in it (all now permanent `--selftest` regression cases; general-purpose, unaffected by the later scope question). First pass censused all of `src/` (547/529/18) and converted 270 compile-time getenv-cache sites (31 files) — build clean pristine, 4 smokes + 6 invariant gates unchanged, but the SNOBOL4 corpus board came back mode-3 FAIL=1 (`pos_rpos_alt_branch_5`), bisected cleanly to the conversion (stash + rebuild + rerun: pre-conversion 2/2 clean, converted 3/3 broken, deterministic `ERROR 246` stack overflow). Independently, before that regression was fully chased down, ceo (routed hq_B) re-cut the row's scope to `src/runtime/` only, on Lon's ruling that compile-time state was never covered by NO-NEW-GLOBALS — verified not yet on origin, so in time. Discarded the compile-time conversion (salvage patch saved), re-censused and re-baselined `src/runtime/` only (108 mutable / 17 files), re-scoped the gate's default root, re-proved it in both directions again against a real runtime file (`rt/bbprof.c`). Pulled fresh (`b297334b`, absorbing hq_C's large concurrent Term-eradication landing) and re-confirmed the runtime census is byte-identical before finalizing. Nothing but new, additive tooling files ships from this session.
