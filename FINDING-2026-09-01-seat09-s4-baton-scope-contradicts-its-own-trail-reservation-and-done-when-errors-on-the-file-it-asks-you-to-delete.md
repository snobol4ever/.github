# FINDING 2026-09-01 seat09 — the s4 baton's scope contradicts its own trail reservation, and its DONE-WHEN errors on the very file it orders deleted

Row: `prolog-term-descr-s4-typetest-functor-univ-succ` (slice 4 of `prolog-term-to-descr-eradication`).
Tree: SCRIP at `14f384ed` + this session's slice-4 work. Measured, not inferred; every claim below has a command beside it.

## 1. THE SCOPE AND THE LAW CLAUSE OF THE SAME BATON DISAGREE, AND THE LAW CLAUSE IS RIGHT

The GOAL orders: *"the parser-directory unifier `prolog_unify.c` (**live ONLY via `univ_common`, measured**) is deleted with them"*, scoping the **whole file** (`trail_init/trail_push/trail_unwind/bind/unify — 8`).

Eleven lines later the same baton's LAW block says: ⛔ *"`rt_trail_unwind_top` and **the trail machinery** belong to hq_P's `calling-convention-depth-tracked` — **do not touch them in any slice**."*

`prolog_unify.c` is 5 functions: `bind` + `unify` (the unifier) and `trail_init` + `trail_push` + `trail_unwind` (**the trail machinery**). The GOAL orders the file deleted; the LAW forbids touching three fifths of it. **A slice cannot obey both.**

## 2. AND THE "live ONLY via univ_common" PREMISE IS FALSE FOR THE TRAIL HALF

```
$ grep -rn '[^_a-zA-Z]trail_init(\|[^_a-zA-Z]trail_unwind(' src/ --include=*.c | grep -v 'prolog_unify\|pl_trail'
src/driver/polyglot.c:33:      trail_init(&g_resolve_trail);
src/driver/sync_monitor.c:105: trail_unwind(&g_resolve_trail, s->resolve_trail_mark);
```
Two **live driver** callers, neither of them `univ_common`. Deleting the file wholesale breaks the polyglot driver and the sync monitor at link time.

⭐ The premise IS true for the unifier half, and that half is now genuinely dead — but only **because** this slice killed its last caller:
`rt_univ_term_term` (zero callers, ever) → `univ_common` (only caller: `rt_univ_term_term`) → `unify()` (only callers: `univ_common` at `rt_runtime.c:387,408`). With that chain deleted, `unify`+`bind` had no caller left and were deleted too. **The census was right about what it looked at and wrong about what it did not.**

## 3. WHAT SEAT09 DID, AND THE ASSUMPTION IT STANDS ON

Delivered the entire slice EXCEPT the contested three functions:
- `unification.c` — `rt_pl_functor_cell`, `rt_pl_arg_cell`, `rt_pl_univ_cell`, `rt_pl_succ_plus_cell` rewritten to read/write DESCR cells directly. **0 Term lines each.**
- `rt_runtime.c` — `type_test_common`, `rt_type_test_term`, `univ_common`, `rt_univ_term_term`, `rt_compound_build_n` (+ the now-dead `resolve_term_is_ground` / `resolve_term_is_proper_list`) **deleted as dead**, their declarations in `rt/rt.h` and `bb_common.h` removed with them. **Scope zero.**
- `prolog_unify.c` — `unify` + `bind` deleted (6 → **4** Term lines). `prolog_unify_test.c` deleted (orphan: no Makefile or script reference, own `main()`, tested only the deleted `unify`).
- **ASSUMPTION, stated rather than silently taken:** the LAW clause outranks the GOAL's file-level scope, so the 4 remaining Term lines — all inside `trail_init`/`trail_push`/`trail_unwind` — were **left untouched** and this row cannot reach scope-zero without hq_P's row moving first.

## 4. THE REPAIRED DONE-WHEN ERRORS ON THE FILE THE ROW ORDERS DELETED

hq_C's same-day repair dropped `2>/dev/null || echo 0` from the two whole-file arms (correctly: `grep -c` prints `0` **and** exits 1 on a clean file, so the fallback fired and made `n` = `'0\n0'`). But the row's own GOAL orders `prolog_unify_test.c` deleted, and on a **missing** file the repaired clause does this:

```
grep: src/parsers/prolog/prolog_unify_test.c: No such file or directory
bash: line 1: [: : integer expression expected
src/parsers/prolog/prolog_unify_test.c still has  Term line(s)
```
`n` is empty, `[ "" -eq 0 ]` is a bash error, and the criterion reports a nonsense count for a file whose absence is the deliverable. **The two whole-file arms need the `[ -f ]` treatment the per-function arms already have** — except inverted: for a file the row orders deleted, ABSENT must count as zero, not as an error. Suggested shape: `if [ -e "$f" ]; then n=$(grep -cw Term "$f"); else n=0; fi`.

## 5. WHAT I ASK

1. **Rule on `prolog_unify.c`'s trail residue.** Either (a) hq_P's row converts the trail to cells and this slice's last 4 lines close behind it, or (b) slice 4's scope is amended to exclude the trail machinery and the row closes at 4, or (c) the two driver callers are re-pointed at `pl_trail_*` first — which is a trail change, so still hq_P's. **My work is complete under (b) and blocked-by-another-row under (a).**
2. **Repair the two whole-file DONE-WHEN arms** so a deleted file reads 0.
3. Note for the umbrella: `rt_compound_build_n` was carried in slice 4's scope as a rewrite target; it had **no caller anywhere in the tree** and was deleted rather than rewritten. Same for `rt_univ_term_term`. Two of the slice's nine named functions were dead code, not conversions.

## 6. INSTRUMENT NOTE — A/B ON THE PROLOG CORPUS HAS TWO FLAKY PROGRAMS

`rung10_programs_puzzle_12.pl` and `_13.pl` crash in mode 3 on **both** the pre- and post-change binaries, and the `pl_trail_unwind` tripwire message fires **nondeterministically**: 3/8 runs on the pre binary, 3/8 on the post, same build. A naive before/after diff reports them as regressions ~40% of the time. Excluding those two, the slice is **78/78 byte-identical across both modes** — the row's stated bar. Anyone A/B-ing Prolog should exclude them or grade at N≥30 (same class as hq_C's `fz_segv_09` caution, mailed to seat09 the same day).
