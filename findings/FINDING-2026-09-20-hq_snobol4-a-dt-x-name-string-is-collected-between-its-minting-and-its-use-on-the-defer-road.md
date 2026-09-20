# A DT_X NAME STRING IS COLLECTED BETWEEN ITS MINTING AND ITS USE ON THE DEFER ROAD

`hq_snobol4`, 2026-09-20, row `snobol4-the-pattern-replacement-class-prints-a-wrong-answer-under-collection-and-changes-its-fingerprint-per-poll-set` (CEO-979, GC-only order).

**TREE OF EVERY NUMBER BELOW:** SCRIP `76ef697a9` (plain `origin/main`, `merge --ff-only`, NO local patch) · corpus `9a69dfcc2` · `.github` `66eccbfc` · `RT_OPT=-O0` · RT_TAG `f65f143e2f`.
⛔ **NOTHING IN THIS FINDING IS LANDED.** Both named sites are SHARED nodes (the collector; the by-name dispatch region the `ceo` owns under MODE line 2), so this is an ASK with the measurement, never a landing. The SCRIP tree is clean — every probe quoted here was reverted and the base readings re-measured on the restored origin binary.

## 1. THE ROW'S PREMISE IS STALE, AND THE DEFECT IS REAL — THESE ARE TWO SEPARATE FACTS

The row says `user_function_eval_arbno_replace_branch_2` is "red in every SnoM run" and is "the last SNOBOL4 class the tiny arena names". Measured on this tree:

| entry | arena-sensitive | stress-sensitive | on the board |
|---|---|---|---|
| `user_function_eval_arbno_replace_branch_2` | **no** | **YES** | **GREEN** |
| `dupl_size_replace_branch_1` | no | no | RED |
| `size_keyword_replace_branch_1` | no | no | RED |

SnoM master at `SCRIP_HEAP_MB=1`: **1963/1974, FAIL=2, xfail=9** — the `ceo`'s numbers reconcile exactly. The two reds are `dupl_size_replace_branch_1` and `size_keyword_replace_branch_1`, and **the assigned entry is not one of them.** The same two, and only those two, are red at the DEFAULT arena, so they are **not tiny-arena reds and not GC reds** — they are static reds that happen to share the generated `*_replace_branch_*` family name with the assigned entry.

⛔ **`3b192bd3` IS THE `.ref`'s OWN FINGERPRINT.** The harness's fingerprint is `md5(stdout)[:8]` (`corpus_suite_harness.py:2972`); `md5sum < w.ref` is `3b192bd3d045…`. CFO-107 recorded `3b192bd3` as "the same patch at the default arena with no stress" alongside two wrong answers — **that reading was the entry PASSING.** A fingerprint diffed against other fingerprints instead of against the ref cannot tell a cure from a corruption.

**What IS true:** at `SCRIP_GC_STRESS=0` the entry is byte-equal to its ref in both modes at both arenas; at `SCRIP_GC_STRESS>=1` it prints one line, `nomatch`, in both modes at both arenas. The ten-line body is all pattern side-effect output from conditional value assignments, and `.` assignments fire only when the WHOLE match succeeds — so `nomatch` alone is not a truncated answer, **it is the match failing end to end.**

## 2. THE WITNESS — 9 LINES, NO INCLUDES, NO ARBNO, NO CONDITIONAL ASSIGNMENT

```snobol4
                  lvl1           =  LEN(2)
                  lvl2           =  *lvl1
                  subj           =  'AA'
                  subj           POS(0) lvl2 RPOS(0)                             :F(no)
                  OUTPUT         =  'match'                                      :(done)
no                OUTPUT         =  'nomatch'
done
END
```
`SCRIP_GC_STRESS=0` → `match` · `SCRIP_GC_STRESS=1` → `nomatch`. Ablation, each step divergence-preserving: the deferred-name target `. *shx(...)`, the conditional assignment, `ARBNO`, `BREAK` and the 16 `-INCLUDE` companions are **all irrelevant**. The one load-bearing ingredient is **a pattern variable whose entire value is a bare deferred expression** (`lvl2 = *lvl1`). Making that value a concatenation (`*lvl1 LEN(1)`) or an alternation (`*lvl1 | 'ZZ'`) **masks** the defect.

## 3. THE WORD THAT IS LOST, NAMED

`SNO$MKEXPR` (`by_name_dispatch.c:7958`) mints the unevaluated-expression descriptor:
```c
DESCR_t xd; xd.v = DT_X; xd.slen = (uint32_t)strlen(nm); xd.s = rt_heap_strdup_c(nm);
*out = xd; return 1;
```
`rt_heap_strdup_c` puts the name **on the GC heap**. Ordered trace of the witness at stress 1 (probes since reverted):
```
[MKEXPR]      out=0x7ffc16d74650  xd.s=0x7e931b60c7d0  name="EXPR$0$lvl1"
[visit DT_X]  d=0x70001010        d->s=0x7e931b60c7d0  inheap=1  str=<garbage>   <-- FIRST visit, already dead
[DT_X arm]    nm=0x7e931b60c7d0   bytes=20c8601b937e000058000000  registered=0
nomatch
```
The 12 bytes at the use site are a pointer followed by `0x58` — **the block has been re-issued by the arena as a `DESCR_t`.** At stress 0 the same address still reads `"EXPR$0$lvl1"` and the match succeeds.

The consequence is silent by construction: `rt_defer_resolve` (`pattern_match.c:1062`) takes the `DT_X` arm, `rt_proc_is_registered(<garbage>)` is false, so it falls to `NV_GET_fn(<garbage>)`, which is simply **an undefined variable → the null string** (`DT_SNUL`). A null pattern matches empty, `RPOS(0)` is then two characters short, and the match fails **with no error of any kind**.

## 4. TWO HOLES, ONE SYMPTOM — AND THE FIRST IS A CLASS DEFECT

**(a) `gc_visit_one` has no `DT_X` case.** Its switch covers `DT_S, DT_SNUL, DT_A, DT_T, DT_DATA, DT_N, DT_P, DT_PLVAR, DT_PLREF, DT_BIG`, then `default: return;`. `DT_N` (NAME) already does exactly the right thing for its `d->s`; `DT_X` is the same kind of thing and has nothing. Adding the `DT_S`-shaped case, **measured base vs head, one binary at a time:**

| stress | base (origin) | with `case DT_X` |
|---|---|---|
| 0 | match | match |
| 1 | nomatch | nomatch |
| **3** | **nomatch** | **match** |
| 5 | match | match |

⭐ **Necessary, not sufficient** — and I am reporting it as exactly that rather than as a cure.

**(b) The value is already dead before any `DT_X` is ever visited.** The first `DT_X` the collector sees in the whole run already carries the clobbered address. So the string dies at the collection that fires **at the return of the allocating call**, while its only reference is the dispatch's `out` descriptor — before it reaches any home the collector walks. ⭐ **This is the hazard the `coo` named to me by mail before I had a witness:** *"`rt_gc_point_arr` registers the args array ONLY, not the frame — at `dop_call_ax` the `void **` ball crosses raw and the address of the `DESCR_t out` crosses too, and `out` holding FAILDESCR today is a fact about today, not a property."* `SNO$MKEXPR` is the counter-example to "today": it puts a freshly allocated heap pointer in `out`, and it dies there.

## 5. TWO INSTRUMENT DEFECTS PAID FOR ON THE WAY

- ⛔ **The row's own DONE-WHEN cannot go green and does not grade the program.** It sources `lib_master_extract.sh` with no `MASTER_LANG`, which refuses `rc=2` ("a missing language is a refusal, never a quiet snobol4"); and once that is fixed it still runs `./scrip "$W/w.sno"` from `SCRIP/` with none of the entry's **16 `-INCLUDE` companions** copied, while the real harness runs with `cwd` = the source's own directory and the companions beside it. As written it grades 17 lines of `cannot open include` (fp `154bff0f`) as the program's answer. A corrected materializer is in this finding's scratch and the DONE-WHEN needs replacing.
- ⛔ **Do not drop this witness into `scripts/gc_witnesses/`.** `test_gate_orphaned_witnesses_do_not_grow.sh` fails on witnesses no gate references, so an unwired witness file trips a gate that has nothing to do with this defect. The witness is inline above; wiring it belongs with the cure.

## 6. WHAT I AM ASKING FOR

Both sites are shared nodes, so the ASK is: **(a)** may the `DT_X` case be added to `gc_visit_one` as a class fix beside `DT_N` — and **(b)** who owns making the by-name dispatch's `out` descriptor live across the collection at the allocating call's return, given MODE line 2 puts that file's dispatch region with the `ceo`. `SNO$MKEXPR` is SNOBOL4's builtin but the mechanism is every language's.
