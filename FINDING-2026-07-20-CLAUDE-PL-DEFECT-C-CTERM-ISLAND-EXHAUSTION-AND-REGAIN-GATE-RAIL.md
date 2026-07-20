# FINDING 2026-07-20 (Claude Sonnet 4.6, s107) — PL DEFECT-(c) CTERM ISLAND EXHAUSTION FIXED + REGAIN-GATE FIRST COMPLETE RAIL

## 1. Defect-(c) diagnosis

Defect-(c) was the abort `rt_pl_cterm: island exhausted (16777216 used)` during queens_8 fail-driven ×512 (24,966/47,104 lines printed then SIGABRT), and the family including the s99 ~773-iter qsort/ham SIGSEGV under full-enumeration loops. The cterm island (16 MB bump allocator, PL-WS-1 step 1) had zero release callers — step 2 was never landed. Every `$write` on a PLREF/PLVAR cell walks `rt_pl_cell_to_term` → `term_new_int/compound` → `rt_pl_cterm_alloc`: roughly 670 B of Term tree per printed solution, never freed, 16 MB cliff at ~25K solutions (queens_8 emits 92 lines/solution).

gdb sample (3/3 frames identical): `out_write_descr → rt_pl_cell_to_term → term_new_int/compound → rt_pl_cterm_alloc`.

## 2. Survivor audit before the fix

Transient vs. survivor distinction is load-bearing — a release inside the converter would corrupt `findall` bags and the dynamic DB:

- `rt_findall_add` (by_name_dispatch.c:960): calls `rt_pl_cell_to_term` and stashes the returned Term* in a bag that outlives the call — SURVIVOR, no bracket here.
- `$op`/list-walk (by_name_dispatch.c:1478): list walk over `$op` argument atoms, Term* live only inside the call — TRANSIENT but path rarely taken; bracket harmless.
- `out_write_descr` (by_name_dispatch.c:3748): all Term* consumed immediately by `pl_write` — TRANSIENT, hot path.
- `rt_pl_write_cell/writeq_cell/write_canonical_cell/write_term_cell` (unification.c:97-133): all Term* consumed by the printer, none escape — TRANSIENT.
- `rt_pl_format_cell` (unification.c:490-523): Term* for the format arg list and per-directive args — TRANSIENT.
- `rt_term_cmp_terms` (rt_runtime.c:394-404): T0/T1 consumed by `resolve_term_compare`, never escape — TRANSIENT.
- `rt_pl_char_type_cell/rt_pl_write_cell` in unification.c: additional wrappers — TRANSIENT.
- Intern tables (`prolog_atom_intern`) are WS-hosted; releasing the cterm mark cannot dangle atom names.

## 3. Fix (5 files, runtime-only, zero emitter/template changes)

`rt_pl_cterm_mark()` / `rt_pl_cterm_release()` already existed (declared in rt_arena.h, implemented in rt_arena.c). Added:

- `rt_pl_ctr_on()` in rt_arena.c: function-local-static env check (`SCRIP_NO_CTR=1` = hatch off, same pattern as `rt_pl_cterm_poison`); declared in rt_arena.h.
- 7 bracket sites: `out_write_descr` (by_name_dispatch.c), `rt_pl_write_cell` / `rt_pl_writeq_cell` / `rt_pl_write_canonical_cell` / `rt_pl_write_term_cell` / `rt_pl_format_cell` (unification.c), `rt_term_cmp_terms` (rt_runtime.c). Each: `arena_mark_t cm = rt_pl_cterm_mark();` before first conversion, `if (rt_pl_ctr_on()) rt_pl_cterm_release(cm);` after last use.

## 4. Notarization

| check | result |
|---|---|
| q512 m4 post-fix | rc=0, **47,104 lines** (512×92), 11.8s |
| q512 m3 post-fix | rc=0, 47,104 lines, **m3==m4 byte-identical** |
| q64 pre/post fix | byte-identical |
| `SCRIP_NO_CTR=1` hatch | reproduces abort at 24,966-line / 16 MB cliff |
| qsort fail-driven ×4096 | rc=0, 4,096 lines, 1.8s (s99 ~773-iter death gone) |
| qsort/nrev recursion ×512 @8MB | still SIGSEGV — **separate member**: C-stack exhaustion from retained NONDET rsp-carved frames (correct behavior; fix = RSP-F-4 / SPEED-5 class) |
| rung suite | 135/138 ×3 — 3 fails = pre-existing float-writer trio (rung23, rung29×2) |
| smoke pl 5/5 ×3, sno 7/7, icn 14/14 ×2 | PASS |
| no-new-global | PASS floor 14 |

## 5. REGAIN-GATE first complete rail

With queens_8 now runnable, the A/B rail (`bench_prolog_ab_pregut.sh`) completed for the first time:

| prog | GNU ms/it | OLD ms/it | old/GNU | NEW ms/it | new/old |
|---|--:|--:|--:|--:|--:|
| fib | 2.642 | 3.203 | 1.21× | 11.406 | **3.56×** |
| tak | 9.562 | 10.031 | 1.05× | 41.625 | **4.15×** |
| qsort | 0.034 | 0.484 | 14.2× | 0.337 | **0.70×** ✅ beats OLD |
| nrev | 0.007 | 0.194 | 27.7× | 0.298 | **1.54×** |
| deriv | 0.002 | 0.029 | 14.5× | 0.038 | **1.31×** |
| queens_8 | 3.169 | 17.773 | 5.61× | 18.453 | **1.04×** ✅ beats OLD |

Geomean new/old (6 programs): **1.67×** — gate target ≤1.3× **UNMET**. Remaining gap is fib (3.56×) and tak (4.15×): the recursion class still pays rt_call_arr + dop ceremony per call vs OLD's direct `call gzpN_α` + inline arg registers. qsort and nrev now BEAT OLD (REGAIN-5B list-unify paid off). queens_8 matches OLD.

## 6. Recovery summary (REGAIN-0 through this session, s107)

| prog | s100 new/old | s107 new/old | recovery |
|---|--:|--:|--:|
| fib | 17.9× | 3.56× | 5.0× recovered |
| tak | 26.5× | 4.15× | 6.4× recovered |
| qsort | 15.1× | 0.70× | 21.6× recovered |
| nrev | 13.2× | 1.54× | 8.6× recovered |
| deriv | 6.8× | 1.31× | 5.2× recovered |
| queens_8 | SIGSEGV | 1.04× | fixed + matches OLD |

## 7. Next rungs for the REGAIN-GATE

Geomean 1.67× vs OLD gap is dominated by fib/tak (recursion class, 3.56×/4.15×). ROOT CAUSE: rt_call_arr overhead per call (the strcmp-gate, the dop_call ceremony) vs OLD's direct emitted `call gzpN_α`. REGAIN-1 SLICE C (direct cross-box `call procN_α` / `jmp procN_β`) is the remaining lever — it was deferred behind REGAIN-1 SLICE B (g_call_args residency design call), but the 3.56× fib gap makes REGAIN-1C a higher priority than further unify micro-opts. SPEED-5 (first-arg indexing) will close the qsort/nrev DET gap and bring nrev/deriv below 1.0×.
