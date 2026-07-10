# FINDING 2026-07-10 — CLAUDE — PL-BENCH 12→20; ham/meta_qsort recycled-arena channel bracketed, open

## Headline
Prolog bench suite (corpus/benchmarks/prolog/bench, 22 programs, gprolog-oracle-verified `.expected`)
went **green 12 → 20, broken 10 → 2** in five landed rungs, m3≡m4 throughout, rung suite 109→**110**/115
(the +1 is rung30_dcg_pushback_rest; the remaining 5 are the rung28 exception family, untouched —
catch/throw is still ⛔ NEEDS NEW-WAY DESIGN awaiting Lon's sign-off).
Remaining broken: **ham, meta_qsort** — one shared crash class, bracketed to a minimal instance and
two proven mechanisms, one fixed, one open.

## Landed (SCRIP commits, this session, in order)
1. `2ccdea5` multi-arity predicate-indicator naming: proc_table/g_rt_gen_procs were bare-name keyed;
   `d/1`+`d/2` collapsed to one slot (rt_proc_set_fn dedupes by name → second arity overwrites first's
   fn → wrong body under wrong frame → SEGV). Fix: pl_pi_name mangles `name/arity` at all three
   IR_CALL_PROC_STAGED build sites + both registration sites ("main"/0 stays bare = driver entry alias);
   driver asm_sym_name sanitizes `/`→`$` at the four proc_%s SYMBOL formations (the `.Lpn` runtime-key
   .strings stay raw). nrev/queens/queens_8 closed.
2. `6c0b1ca` TT_PROGRAM goal blocks thread directly: the parser wraps an ITE arm's conjunction as
   TT_PROGRAM; goal()'s case still built the amputation-era conj-OWNER box (payload-less IR_OP_COUNT →
   emit_drive FATAL op=106). collect_conj now flattens TT_PROGRAM like `,`. sendmore closed;
   rung30 pushback closed (its main is exactly `-> A, B ;`).
3. `2ed323c` **clause redo targets the LAST pending resumable** (the deep one): lower_pl_clause_into
   captured cx->beta after thread_goals, but the descending build loop leaves cx->beta = rz[0] — the
   FIRST goal's call. Every deeper pending generator was orphaned on redrive (p3 repro: 3-generator
   body yields 2 of 8 tuples; g1e drops the middle solution). Fix: thread_goals publishes
   `cx->beta = last_res_beta ? last_res : NULL` after its wiring loop. Both findall forced-fail sites
   get the same correction for free; CUT falls out right (post-cut reset zeroes last_res_beta →
   committed clause publishes NULL). mu + queensn closed.
4. `91d07b3` Prolog integer arithmetic: pl_is_op_code mapped `idiv`→BINOP_DIV, whose shared int÷int is
   SNOBOL exact-or-float (19//4 → 4.75 → whole nested chain floats → cal's mod-7 = 6.0 ≠ 5).
   pl_arith2 shim in by_name_dispatch: int-int `//` truncates (C division; -7//2=-3 ✓gprolog),
   int-int `mod` floored/sign-of-divisor (-7 mod 3=2, 7 mod -3=-2 ✓); all else delegates to
   rt_num_arith untouched (language-blind). Routed through both $is_ and $ax_ arms. cal + crypt closed.
   ⚠ OPERATIONAL: by_name_dispatch.c links into BOTH scrip (m3) AND libscrip_rt.so (m4) — rebuild BOTH
   or you get phantom m3/m4 divergence (cost us one confusing sweep).
5. `ecd2261` dead-activation-handle contract (hardening, correct regardless): released frame's fn word
   nulled; resume of null-fn = clean FAIL; new rt_proc_resume_frame_h(void**) clears the CALLER's act
   slot on exhaust; bb_call_proc_staged β passes the slot ADDRESS in both mediums.

## The open channel (ham, meta_qsort)
Symptom class: SEGV at 0s (corruption, not exhaustion). Two flavors observed, one root class:
crash inside `plw_cell_deref(c=0x1)` unifying against a cell chain that lands in **recycled ZLS arena
memory** (full ham), and `GC_free` abort inside `rt_zls_release` from resume's FAIL branch (ham-k6).

Bracketing ladder (all reproducible in /tmp of a fresh container):
- ham-k list-shrink against the FULL 20-node Petersen fact base: k∈{3,4,5} clean-fail ✓, **k=6 crash**,
  k=10 SOLVES correctly, k∈{8,14,20} crash — shape-dependent (which dead-ends get explored), not size.
- k=6 died in GC_free (double-release). The dead-handle contract (commit 5) converts k=6 to
  **terminating with the CORRECT answer** (no 6-cycle exists in that induced subgraph) — proving the
  double-resume mechanism existed and is now closed.
- Full ham STILL crashes: the surviving channel is a term-cell chain reaching **released-then-reused
  arena memory** (ZC_ALLOC GC mode: GC_MALLOC per activation, GC_free on FAIL → block recycled while
  still reachable). At the crash the poisoned DESCR parses as a DT_N slen=2 nameptr whose "VCELL" is
  wholesale garbage (cellp=0x1, key=0x6) — i.e., recycled bytes, NOT a real NV fallback (bb_var_ref
  BOMBS on NV fallback at emit time, so that path is excluded).

Ruled OUT by direct experiment: GC collection of live frames (GC_DONT_GC=1 still crashes);
stack-region binds (conditional breakpoint on plw_bind never fired before the crash);
$mkc child arrays (GC_MALLOC heap ✓); zls growth-direction bind inversion (arena grows UP,
hi→lo binds newer→older ✓); garbage-handle resume as first event (conditional breakpoint never fired).

Open question, precisely: **which live reference (term cell, trail entry, or handle) still reaches an
activation frame after its release-on-FAIL, given that the global trail is LIFO-unwound to the callee's
entry mark on that same failure path?** Candidate worth checking first next session: bindings/handles
recorded through channels that do NOT ride pl_trail (e.g., act-slot writes are raw stores; result-slot
DESCRs copied between frames; g_call_args staging) and structure built in a frame that yielded
solutions RETAINED by an outer findall/collector. meta_qsort (meta-interpreter, `clause/2`-style
dispatch over stored bodies) crashes in the same class — likely the cleaner reproducer once shrunk,
since it has no graph-search noise.

Recommended next-session play: (a) shrink meta_qsort the same way; (b) instrument rt_zls_release to
memset the block to a poison byte (0xDD) in a debug env-gate — first deref of poison under gdb names
the holder; (c) audit every raw (untrailed) store of frame-interior pointers.

## Also banked
- refs convention extended: `SCRIP/refs/gprolog-master` + `refs/swipl-devel-master` (gitignored, user-
  supplied source zips) — consulted for catch/throw semantics (gprolog catch.pl `$catch`/`$catch_a_throw`
  choice-point-relative handler + throw_c.c cut-to-saved-B) and DCG translation (expand_c.c
  Dcg_Body_On_Stack ≡ SCRIP's dcg_expand_body difference-list shape ✓).
- Pascal gate recipe /tmp scripts recreated per GOAL-PASCAL-BB §Session Setup; inputs are `$b.in`
  (NOT .inp — cost one false alarm). Full board green at session end:
  prolog rung 110/115 ×3 · smoke 5/5 HARD · bench 20/22 · icon 12/12×2 HARD · sno 7/7 HARD ·
  rebus 4/4 · snocone 5/5 · pascal 128/0 M3+M4 full recipe · emit_no_lang OK · pl no-new-global 14/14.
