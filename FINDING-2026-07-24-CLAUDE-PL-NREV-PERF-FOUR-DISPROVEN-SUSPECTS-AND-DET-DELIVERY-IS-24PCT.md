# FINDING 2026-07-24 (Claude, s141) — nrev perf: four allocation-side suspects DISPROVEN by measurement; first-arg DET-delivery is the confirmed ~24% win

## TL;DR

Continuing the s140 perf push on `nrev` (the worst van-Roy cell). s140's cursor named "(A) attack the
cons-cell allocation constant" as the highest-payoff NEXT item. **This session DISPROVES that hypothesis by
direct measurement**, disproves three other allocation-side suspects, LANDS the Prolog SLOT-ELIDE Lon directed,
and — the biggest result — **shows most of the reported deficit was an `-O0` MEASUREMENT ARTIFACT**:

- **LANDED (SCRIP, gated green): SLOT-ELIDE for Prolog builtin-goal result quads.** Lon directive: "only BBs
  whose result is USED get an allocation." `IR_CALL_BUILTIN_PROLOG` added to the ZLS S4a elide whitelist
  (`zls_s4_ok`) — a builtin called as a GOAL (its success/fail flows through the γ/ω ports, its result DESCR is
  dead) no longer gets a 16B result quad; its argv locals are preserved (S4a shifts them to the entry offset).
  26 dead builtin-result quads identified in nrev's graphs; frames shrank (nrev app-class −48B, fib recursion
  −240B/15 slots). Gated: **Prolog rung 164/164 × 3 modes + smoke 5/5 × 2; Icon 14/14 × 2; all-langs matrix 6/6
  no drift** (zeta_storage.c is shared — SNOBOL4/Icon unaffected because the op is Prolog-only). **HONEST perf:
  ~1% on nrev/fib** — because **Prolog is NOT store-bound the way SNOBOL4 pattern-matching is** (their SLOT-ELIDE
  got treebank −20% precisely because the match phase is 63% stores; frame-zeroing, which this eliminates, was
  never Prolog's bottleneck — see the disproven cons-zeroing suspect below). It is the correct architecture and
  the right thing to have, and it will help frame-heavy / builtin-goal-heavy Prolog more than nrev; it is simply
  not where nrev's time goes. Follow-ons `IR_CALL_PROC_STAGED` (5 dead) and `IR_DISJUNCTION` (5 dead) are further
  candidates, untested (each has entangled resume/self-state — validate individually).
- **The runtime at `-O1` (the sanctioned perf-comparison level) is 47% faster than `-O0` on nrev**
  (mode-4: 1.367 s → 0.727 s). Every prior session's headline deficit was measured with an `-O0` runtime and
  is roughly DOUBLE the real `-O1` gap. At `-O1`, nrev is ~8× gprolog, not ~15×.
- **Mode-3 is STRUCTURALLY CAPPED at `-O0`.** Its runtime (deref/unify/alloc) is compiled INTO the `scrip`
  binary at `-O0` (`CBASE := -O0`, `CRT := $(CBASE)`, Makefile lines 513/514/544), so an `-O1` `.so` helps
  ONLY mode-4. Mode-3 leaves ~47% on the table, recoverable purely by BUILD CONFIG — the single biggest lever
  here, and it is not a code change. (Proof needs no scrip rebuild: mode-4 runs the identical runtime source
  at `-O1` and is 47% faster.)
- **First-arg-indexing DET-delivery (PL-SPEED-5 lever 2) is worth ~24–29% and STACKS on top of `-O1`**
  (mode-4 `-O1`: 0.727 s → 0.526 s with a base-clause cut, which is exactly what indexing produces). That half
  is a codegen/CP rung (correctness-critical, not landed this session).

Roadmap from the `-O0` baseline to the achievable stack: 1.367 s (`-O0`) → 0.727 s (`-O1`, build config)
→ 0.526 s (`-O1` + DET-delivery) = **2.6× total, ~15× → ~5.8× gprolog.** The residual ~5.8× is the
boxed-cell-vs-WAM structural gap (register residency / deferred HB).

**Tree state at close: SCRIP has the 1-line SLOT-ELIDE change; corpus has 22 regenerated Prolog bench `.s`
(frames shrank); `.github` has this finding + cursor.** Rung suite 164/164 × 3 modes green; `out/` is gitignored
so the `-O1` `.so` build is not a tree change.

**ALL PERF NUMBERS ARE LABELED WITH THEIR `-Ox` LEVEL** per the 2026-07-24 FACT RULE. The `-O0`→`-O1` runtime
switch used the mandatory `rm -f out/rt_pic/*.o out/libscrip_rt.so` first (timestamp trap); the `-O1` `.so`
build ran ~4.5 min detached via `setsid` (154 template TUs + runtime C — they compile INTO the `.so`, which is
why it is the slow part the FACT RULE warns about).

---

## THE METHODOLOGY TRAP THAT MISLED PRIOR SESSIONS (read this first)

**gdb steady-state sampling of a MODE-3 run mis-attributes leaf frames and cannot be trusted for Prolog perf.**
Mode-3 JITs x86 into an anonymous `mmap` with NO symbols and NO unwind info, so when gdb interrupts inside the
emitted Byrd-box blob it produces `??` frames (measured: 18/40 leaf, then 421/1200 across-frame in one run) and
attributes the visible leaf to whatever C sink the PC happens to be near. In this session a mode-3 sample showed
`rt_proc_hash_lookup`/`rt_proc_fnv`/`rt_proc_find` as ~12% of leaf time — which is exactly the "red herring" the
s140 cursor already warned about. **Direct call-count instrumentation proved `rt_proc_hash_lookup` runs FEWER
than 300 000 times in nrev ×20000 (~10 M proc-calls) — i.e. it is NOT a per-call path at all.** The pointer-keyed
2048-entry cache (`g_proc_idx_key`, `rt_proc_find`) works; the sampler simply lied.

**THE RELIABLE METHOD: profile the MODE-4 binary.** `scrip --compile f.pl` emits real `.s`; assemble+link and you
get an ELF with real symbols and unwind info for BOTH the emitted boxes (proc labels) and the runtime `.so`. gdb
sampling of that binary gives trustworthy backtraces (`??` dropped from 421 → 9). Recipe:
```
scrip --compile f.pl > f.s
as --64 -o f.o f.s
gcc -no-pie -o f.bin f.o out/libscrip_rt.so -lm -lstdc++ -Wl,-rpath,out
# then: run f.bin in background, gdb -p PID -batch -ex "bt 8" in a loop, aggregate frame-0.
```
CAVEAT: a longer run inflates GC frames. nrev ×5000 does ZERO collects (see below); nrev ×400000 churns ~9.5 GB
through the 512 MB heap and so DOES collect — sampling the long run over-weights `gc_collect_ex`. Discount GC
frames when the real benchmark size doesn't collect.

**RULE OF THUMB, reinforced:** when a perf claim rests on a sample, confirm the hot symbol with a call-count or
timing instrument before optimizing it. Three of this session's four dead ends were sampler ghosts.

---

## THE FOUR DISPROVEN SUSPECTS (each with the measurement that killed it)

Baseline (this machine, `-O0`, failure-driven `between/1`+`fail` harness so backtracking reclaims each iteration,
`app/3` renamed from `append/3` to dodge the gprolog builtin and give a fair user-code comparison):

| | startup | nrev ×5000 (best) | work | ratio |
|---|---|---|---|---|
| gprolog 1.4.5 | ~9 ms | ~94 ms | ~85 ms | 1× |
| SCRIP mode-3 | ~5 ms | ~1308 ms | ~1303 ms | ~15.3× |

1. **Proc-name resolution — NOT hot.** Call-count instrument on `rt_proc_hash_lookup`/`rt_proc_find`: < 300 k calls
   in nrev ×20000. The pointer cache hits. (Confirms s140's own note; the gdb sample was the ghost.)

2. **Per-alloc init CONSTANT — NOT the bottleneck (this kills s140's "(A)").** `rt_gcheap_alloc`'s fast path pays
   four never-taken-after-first init guards per call (`!g_hp_report_reg` atexit, `!g_hp_arena` init,
   `stress_n<0` getenv, `budget<0` getenv) plus a fifth per-carve (`zfull<0` getenv). I consolidated all five into
   one boot constructor with cached flags + fast-carve-first (semantics-neutral; env features verified still
   functional; nrev output byte-identical). **Measured result: 1.319 vs 1.308 s — within `-O0` noise, i.e. ZERO.**
   The refactor was reverted (perf-neutral churn on the delicate allocator is not worth the review burden). The
   `-O0` per-call load/branch tax is real but is dwarfed by the per-cons unify/deref/bind work.

3. **GC — runs ZERO times for nrev ×5000.** Env-gated collect counter: 0 collects. 2.475 M conses × 48 B = 118 MB
   accumulates in the 512 MB heap with no reclaim and no collection (failure-driven backtracking does NOT retreat
   `g_hp_top` — HB is deferred, ARCH-PROLOG.md — but the heap is large enough that it never matters at this size).
   So GC is not a cost here, and heap-top-retreat-on-backtrack (HB) would help only LARGER/longer runs that
   actually exhaust. The `gc_collect_ex` leaf samples were long-run + JIT-mis-attribution artifacts.

4. **Cons-cell zeroing — NOT the bottleneck.** `rt_gcheap_carve` memsets the 32-byte HB_PLJ payload that
   `plw_mkc_kids`/the cons sites overwrite immediately (79 MB of "wasted" zeroing across the run). Env-gated skip
   of HB_PLJ zeroing (measurement only): **1.340 vs 1.316 s — no improvement.** A 32-byte sequential cache-resident
   memset is effectively free; the surrounding box overhead dominates. (Also: skip-zero is UNSAFE in general — 2 of
   the 6 `rt_plj_alloc` callers over-allocate one cell on the `ar==0` edge and leave it unwritten, which the
   conservative scanner would misread. Not worth it even if it had helped.)

Allocation volume itself is real and inherent: `SCRIP_ALLOC_HIST` confirms **2 475 000 HB_PLJ (type 209) allocs,
79.2 MB, ~495 conses/iteration, O(n²)** — but that is naive-reverse's intrinsic shape, and every *per-alloc*
lever above is either noise or unsafe. Reducing the volume means changing the algorithm, which the benchmark
forbids.

---

## THE BIGGEST RESULT: HALF THE DEFICIT IS AN `-O0` ARTIFACT; MODE-3 IS CAPPED AT `-O0`

The whole baseline above is `-O0`. The 2026-07-24 FACT RULE makes `-O1` the sanctioned perf-comparison level
("more representative than `-O0` without `-O2`'s build cost"). Measured at `-O1` (mode-4, which links the `.so`):

| nrev ×5000 | time (best) | note |
|---|---|---|
| mode-4 `-O0` | 1.367 s | the inflated baseline every session has used |
| mode-4 `-O1` | **0.727 s** | **−47% — just the build level, ZERO code change** |
| mode-4 `-O1` + DET-delivery (base-clause cut) | **0.526 s** | **−29% more; DET-delivery STACKS on `-O1`** |
| gprolog 1.4.5 | 0.091 s | |

So `-O1` alone nearly HALVES the mode-4 deficit (~15× → ~8×), and `-O1` + DET-delivery is a **2.6× total**
speedup over the `-O0` baseline (~15× → ~5.8×). **Every prior cursor's headline number (s139 "nrev 38.4×",
s140 "33×") is roughly double the real `-O1` figure** because it timed an `-O0` runtime.

### Mode-3 cannot see this — and that is the single biggest recoverable lever

`scrip --run` (mode-3, the primary in-process mode) does NOT link the `.so`. Its runtime — `by_name_dispatch.c`
(deref/unify), `gc_heap.c` (alloc), `unification.c` — is compiled straight INTO the `scrip` binary at `-O0`:
```
CBASE := -O0 -g …            # Makefile:34
CRT   := $(CBASE) …          # Makefile:37
… $(CC) $(CRT) -c src/runtime/by_name_dispatch.c …   # Makefile:513  (-O0)
… $(CC) $(CRT) -c src/runtime/unification.c …        # Makefile:514  (-O0)
… $(CC) $(CRT) -c src/runtime/rt/gc_heap.c …         # Makefile:544  (-O0)
```
`ldd scrip` shows no `libscrip_rt`, so rebuilding the `.so` at `-O1` does nothing for mode-3. **Mode-3 runs its
hot runtime at `-O0` and therefore pays the full ~47% penalty the mode-4 `-O1` measurement quantifies.** This is
NOT a code change and NOT an algorithm — it is a build-configuration cap.

**RECOMMENDATION (next session — the biggest, safest single win):** add a perf build variant that compiles
`scrip`'s RUNTIME translation units (the `$(CRT)`/`$(CXXRT)` runtime `.c`/`.cpp`, NOT the parser/emitter — keep
those `-O0` for dev-loop speed) at `-O1`, gated behind an explicit flag so the O0-DEV default is untouched. Then
re-measure mode-3; expect ≈ the mode-4 `-O1` win (~47% on nrev). This session did NOT land it: it is a
build-system change touching the FACT-RULE-protected `-O0` default, `scrip` rebuilds are ~5 min (same heavy
template TUs), and a half-tested Makefile edit is worse than a clear, measured recommendation. The 47% is
already PROVEN (mode-4, identical runtime source, `-O1`); landing the mode-3 variant is mechanical from here.

CAVEAT/OPEN QUESTION for whoever lands it: `-O1` on the runtime is representative but `scrip` itself stays `-O0`,
so the emitted BOX code (the JIT'd x86) is unaffected either way — the `-O1` win is entirely in the C runtime
sinks the boxes `call` into (deref/unify/carve/trail), which is consistent with those being the reliable-profile
hot leaves. The residual ~5.8× after `-O1`+DET-delivery is the boxed-cell-vs-WAM structural gap (per-cons call +
arg-marshal overhead into those sinks, vs gprolog's in-register WAM), addressed by register residency (RSP-F-4)
and the deferred HB.

---



Direct, decisive, SOURCE-ONLY experiment (no code change): add a cut to `app/3`'s base clause. A cut after the
`[]` head matches prunes the clause-2 choice point — which is EXACTLY what first-arg indexing's DET-delivery would
produce automatically (arg0 `[]` vs `[_|_]` selects a unique clause ⇒ no CP).

| program (nrev ×5000, `-O0`) | SCRIP best | gprolog |
|---|---|---|
| plain nrev (nondet `app`) | 1.350 s | 0.092 s |
| nrev + cut on `app` base clause | **1.026 s (−24%)** | 0.092 s |
| nrev + cut on both base clauses | 1.079 s | 0.092 s |

And it STACKS with `-O1` (mode-4): plain nrev `-O1` 0.727 s → nrev+cut `-O1` **0.526 s (−29%)**. So DET-delivery
is a real ~24–29% regardless of optimization level (it removes work `-O1` cannot: the armed CP + trail churn).

gprolog is UNAFFECTED by the cut (0.092 either way) because its first-arg indexing already makes `app`
deterministic — the cut is redundant there. **That is the whole point: gprolog gets DET-delivery for free via
indexing; SCRIP pays the choice-point tax unless the programmer hand-writes a cut.** DET-delivery would give SCRIP
this ~24% automatically.

### Why the CP tax exists — the emitted evidence

In the mode-4 `.s`, `proc_app$2F3_α` arms the choice point **unconditionally at entry**, BEFORE any arg0
discrimination:
- stores the clause-2 resume address (`lea …xchain200_n25_β; mov [rbp+1632], rax`), and
- takes a `trail_mark` (`call rt_pl_dop_trail_mark`) as box `n0`.

The first-arg guard (`rt_pl_dop_ix_g` / `dop_ix_g`, slice-A, landed s113) IS present and DOES cheaply fast-fail
clause 2's redo on the `[]`/cons tag mismatch — but the CP is already armed and the trail already marked, so on the
failure-driven backtrack every armed `app` CP is redone (guard fails) and its trail span unwound. The measured
`pl_trail_unwind` leaf cost (~9% in the reliable mode-4 profile) is the direct signature of this: trail-unwind only
runs on backtrack, so a deterministic `app` would produce none.

Even WITH the cut, SCRIP is 1.026 s vs gprolog 0.092 s ≈ 11×, so DET-delivery closes ~24% and the remaining ~11×
is still structural (boxed-cell model + per-cons unify/deref/bind at `-O0` vs gprolog's WAM registers). DET-delivery
is a real, measured, worthwhile chunk — not the whole gap.

---

## IMPLEMENTATION SKETCH for PL-SPEED-5 lever 2 (next session)

Per the s139 cursor's own analysis, the det/nondet split is WHOLE-PREDICATE at lower time
(`lower_prolog.c:826` `suspend_deliver`), but which clause is unique is a RUNTIME property of arg0. `app` is
correctly classified NONDET (genuinely nondet with unbound arg0); the fix is a per-DELIVERY runtime decision.
Three candidate shapes (s139): (a) two clause-tail copies with a guard selecting; (b) caller-side mode analysis;
(c) **runtime CP-collapse when the arg0 guard proved a sole candidate** — the most localized.

Shape (c): the `dop_ix_g` guard already computes arg0's discriminator at α. Extend the emitted α so that, when the
guard proves arg0 selects exactly one clause, the just-armed CP is COLLAPSED (resume → fail-through, trail-mark
dropped) so backtracking cannot redo it. **Correctness-critical**: collapsing a CP that still had a viable
alternative loses a real solution ⇒ SILENT WRONG ANSWERS. Gate hard: rung suite 164/164 × 3, the full ISO tracker,
bench 22/22, and specifically the nondet-`app`-with-UNBOUND-arg0 cases (the CP must NOT collapse there).

PREREQUISITE per PLAN.md step 6: read the BB-CODEGEN DESIGN SET (ARCH-ICON.md register/layout source of truth +
GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md) before touching any α template or `x86_asm.h` encoder — this touches the
shared list-unify emission path.

---

## HARNESS ARTIFACTS (in /tmp/abwork, disposable — reproduce from the recipes above if needed)

- `nrevfd.pl` — failure-driven nrev ×5000 (`between/1`+`fail`, `app/3` user-defined). The steady-state probe.
- `nrev_cut.pl` / `nrev_cut2.pl` — the DET-delivery experiment (cut on base clause(s)).
- Mode-4 profiling: `scrip --compile` → `as` → `gcc -no-pie … libscrip_rt.so` → gdb `-p PID -batch -ex "bt 8"` loop.

## TOOLING NOTE

gprolog 1.4.5 / nasm / gdb installed via `apt-get update` then `apt-get install --no-install-recommends` (a plain
install hit a 404 on an unrelated `libpoppler-glib8t64` recommend; `--no-install-recommends` sidesteps it).

---

## THE ARCHITECTURAL VERDICT (Lon, s141 late): the -O1 win means the SPLIT IS WRONG — Prolog is CALL-THREADED and needs PL-SINK

Lon's ruling on seeing the -O1 result: "if most of the speed improvement is in optimizing the C runtime, we did
it WRONG — 90% of Prolog runtime should be inside the emitted code, not the RT." He is right, and the -O1
experiment is precisely the audit that proves it. **Measured leaf split (mode-4 nrev, gdb 44 samples, runtime
at `-O1`): ~86% of leaf time in the C runtime (31/44 named rt/plw/dop/pl leaves + 7 libc memset/memcpy on
runtime paths), ~14% in emitted BB code.** SNOBOL4's SPD-0a audit after its sink program: **97.7% emitted,
runtime ≈2%.** Prolog is the exact inverse. Corroboration: a 47% TOTAL speedup from -O1 on ONLY the C runtime
back-computes to a 70–94% runtime cycle share at -O0; and SLOT-ELIDE moved SNOBOL4 −20% but Prolog ~1% — same
signature (SN4's cost was in emitted stores; Prolog's is in C calls).

WHAT IS in BBs vs NOT: the GDE **control** skeleton IS 100% emitted BBs — the four Byrd ports, CP arm/resume,
conjunction/disjunction, cut, clause try/retry chains (the .s shows it: `proc_app$2F3_α` arms its CP, γ routes
redo). What is NOT in BBs is the entire **data plane** — and in Prolog, unification IS the evaluation:
`plw_cell_deref`/`_slow` (by_name_dispatch.c:85), `plw_unify_cells`/`plw_unify_vals`, `dop_unify_lst` (:1391 —
the whole READ/WRITE-mode list head-unify as one C leaf), `plw_bind`+trail (`rt_pl_dop_trail_mark`,
`pl_trail_unwind`), cons alloc (`rt_plj_alloc`→`rt_gcheap_carve`), int arith (`is`/compare dop leaves),
`dop_ix_g` (:1419, a ~5-instruction tag test done as a C call), frame init (`rt_jmp_frame_lexprep2`, rt.c:1404),
arg marshal (`rt_arg_stage` — visible in the samples: pure call-threading tax). Each emitted BB body is
"stage argv into frame slots → `call dop_*` → test → route": SUBROUTINE-THREADED code. by_name_dispatch.c
(6784 lines) became the de facto Prolog instruction set.

WHY it happened (honest root cause): bring-up sequencing. C leaves were the fastest route to rung-ladder
correctness — one implementation serves modes 3+4, debuggable, oracle-diffable — and the template revamp
effort went into port/flavor wiring, so "leaf = C call" stayed the default cell body. SNOBOL4 had the same
shape early and only reached 97.7%-emitted through its explicit sink program (s106 literal/table/range/chain
emission, s137 seal). Prolog never got its equivalent phase, and nobody ran the SPD-0a Ir-attribution KPI on
Prolog until now.

**THE FIX = PL-SINK (the SN4-proven playbook), priority by measured frequency; C leaves stay as slow-path
fallback + differential oracle; gate each rung on 164×3 + gprolog oracle; KPI = emitted-Ir share ≥90% (SPD-0a):**
1. **Deref chase emitted** — the 2–3 instruction tag-test/follow loop, on every operand touch (highest frequency).
2. **unify_lst fast paths emitted** — READ mode (bound cons: tag cmp + two kid bind/unify) and WRITE mode
   (inline bump-alloc + stores + bind + trail-push); `plw_unify_cells` remains the rare structural fallback.
3. **bind + trail-push emitted** — store + CP-watermark cmp + append.
4. **cons carve emitted** — inline bump-pointer (limit cmp / add / header store), C only on slow path/GC;
   kills the 2.475M call+marshal round-trips.
5. **int/int arith fast path emitted** for `is`/compares — untag, op, retag; C fallback for overflow/float/type.
Plus: `dop_ix_g` becomes an emitted tag compare. DET-delivery (lever 2) COMPOSES: it removes redundant CP/trail
work, sinking removes per-op call overhead — together they are the road to WAM-class emitted code. The mode-3
`-O1`-runtime build variant is downgraded to a legitimate INTERIM measure only: at the target split (runtime
≈2–10%), -Ox on the runtime barely matters — exactly as on SNOBOL4 today.

---

## PL-SINK PLAN (s141 close, Lon-approved direction): rung ladder + BB inventory

TARGET: emitted-Ir ≥90% (SPD-0a KPI); stretch ≈97% on det/list-heavy code. Residual C = the irreducible class
(GC, deep-structural-unify fallback, bignum/float, I/O, intern) — the SAME class that is SN4's 2%.

SHARED EMITTED FRAGMENTS (x86_asm.h helpers, used by every BB below):
- `x86_pl_deref` — the 2–5 instr tag-test/follow chase (replaces plw_cell_deref calls)
- `x86_pl_trail_push` — CP-watermark cmp + append (~5 instr)
- `x86_pl_carve` — bump-pointer with limit cmp; slow path calls C; inline gc-flag check replaces rt_gc_point calls

NEW/EXTENDED BB TEMPLATES (~8; the first 5 cover the nrev class):
1. `bb_pl_ix_guard` — emitted tag switch (replaces dop_ix_g). PURE TEST, no binds/trail → SAFEST FIRST.
2. `bb_pl_unify_const` — atom/int/[] head args: deref + cmp | bind + trail (head VAR args ride the bind fragment).
3. `bb_pl_unify_lst` — READ mode (tag cmp + 2 kid bind/unify) and WRITE mode (carve + stores + bind + trail);
   deep-structure kids → plw_unify_cells C fallback (kept as oracle).
4. `bb_pl_cons` — '.'/2 build inline (replaces plw_mkc_kids + alloc call round-trip ×2.475M on nrev).
5. α-prologue change (not a new BB): emitted arg staging + exact-slot zeroing — kills rt_arg_stage +
   rt_jmp_frame_lexprep2 (both visible in the leaf samples). SLOT-ELIDE already shrank what must be zeroed.
6. `bb_pl_unify_stc` — general f/n structure (tier 2).
7. `bb_pl_arith_int` + `bb_pl_cmp_int` — is/compare int fast paths, γ-fused branch; float/bignum/expr → C.
8. `bb_pl_type_test` — var/nonvar/atom/integer/atomic as one parameterized tag-test template.

RUNG LADDER (each rung: 164×3 green + gprolog oracle diff + per-rung kill-switch, SCRIP_PL_SINK bitmask;
READ THE BB-CODEGEN DESIGN SET FIRST — rule):
SINK-0 KPI harness (SPD-0a analog over the Prolog bench) + per-bench baseline splits.
SINK-1 deref fragment + ix_guard (pure-test, zero risk of wrong answers).
SINK-2 unify_const. SINK-3 unify_lst READ (the clause-try hot path).
SINK-4 cons + unify_lst WRITE — ⚠ the delicate one: HB/safepoint discipline; heap must stay parseable at
safepoints; carve slow path re-enters C.
SINK-5 bind+trail fragment everywhere — ⚠ a missed trail entry = SILENT WRONG ANSWERS on backtrack; gate
with trail-count differential vs the C path.
SINK-6 arith/cmp. SINK-7 α-prologue arg-stage + zeroing.
Then DET-delivery (lever 2) COMPOSES on top; then RSP-F-4 register residency for the last stretch.

EXPECTED: per-op cost drops from ~30–50 cycles (marshal + call + C prologue + ret + test) to the 2–20 instr
work itself. With DET-delivery, a credible landing is 2–4× gprolog on the van-Roy set (from ~8× at -O1 today);
parity needs the 16B-DESCR-vs-8B-WAM-word and register-residency work. CAN WE HIT 2–3% RUNTIME LIKE SN4:
YES, on the same terms SN4 did — after SINK-1..7 the remaining C is the irreducible class; note alloc-heavy
runs add a REAL GC share (gc_collect_ex in the x300000 samples is genuine collection work, stays in C, and is
where the -O1 interim build variant keeps paying). Estimated effort: 6–10 gated sessions (SN4's sink program
spanned s106→s137).
