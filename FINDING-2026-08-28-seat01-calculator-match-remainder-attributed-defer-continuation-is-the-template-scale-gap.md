# FINDING — calculator-1/2-match's remainder ATTRIBUTED: the manual push/push/jmp*rax continuation convention for `*X`-style deferred pattern recursion is the dominant cost and is BRANCH-PREDICTOR HOSTILE; one small RT-side cure landed, one build-config lever tested and REFUTED

**Seat:** seat01 · **Date:** 2026-08-28 · **Task:** `perf-calc-match-remainder-dig` (ceo, FLEET-6 PATTERN lane, Lon's calculator-1/2 campaign addition, CEO-38) · **Trees:** SCRIP (pristine `-O0`, freshly built and gate-verified this session), corpus at `perf-attribution-20260828T033014Z.tsv` · **Instruments:** `perf stat` (instructions/cycles/branches/branch-misses, `/usr/lib/linux-tools-6.8.0-138/perf` — the ONLY working `perf` binary on this kernel per `FINDING-2026-08-27-seat06-perf-counters-work-cli-was-broken...`, `/usr/bin/perf` still fails `WARNING: perf not found for kernel 6.17.0-1032`) + `perf record --call-graph=fp -F 4000` cycle-attribution; harness `bench_rep_loop_demos_snobol4.sh` (convergence-ramped reps, never committed); oracle `sbl_clean_bin()` = `/home/resources/spitbol-bench-oracle/sbl -bf`; programs `corpus/demo/snobol4/calculator/calculator-{1,2}-match.sno` (the CANONICAL rep-loop-harness pair — NOT `corpus/benchmarks/snobol4/demo/calculator-1-match.sno`, an older `DEFINE`-wrapped variant with the same filename that the live harness does not use; a stale-path trap worth naming so the next seat doesn't profile the wrong file). No wall-clock multiple is quoted anywhere below (box independently confirmed under concurrent fleet load this session — `hq_P`'s own `test_corpus_snobol4.sh` A/B was running from `/home/claude_P` while this row's `make pristine` ran) — every number is instructions or converged aspect-2 ns, per the task's instrument law.

## THE NUMBERS (Ir, fixed work, never shared with a wall column)

```diff
  kernel               engine  reps  insn_total       insn/match     vs SPITBOL clean (Ir)
- calculator-1-match   m4      64    47,641,135,618   744,392,744    0.4295x (before)
+ calculator-1-match   m4      64    47,634,166,331   744,283,849    0.4296x (after rt_dfx_push inline)
  calculator-1-match   sbl     64    20,464,578,734   319,758,730    1.000x  (reference)
- calculator-2-match   m4      1024  8,017,228,822    7,829,325      0.3534x (before)
+ calculator-2-match   m4      1024  7,941,528,724    7,755,399      0.3567x (after rt_dfx_push inline)
  calculator-2-match   sbl     1024  2,833,235,505    2,766,831      1.000x  (reference)
```

Aspect-2 (in-program bracket, convergence-ramped by the harness, ns/match — NOT wall, NOT a multiple, cited only to show these Ir numbers land in the same neighborhood the task described): calculator-1-match m4 90,794,023.6 ns/match (0.351x sbl's 31,906,043.6) at reps=64; calculator-2-match m4 1,147,589.8 ns/match (0.291x sbl's 333,772.1) at reps=1024 — both converged (two ramp steps within 8% tol), both cross-engine ANSWER-checked (`matched bytes=32512` on both kernels, both engines, both before and after the cure).

Branch behavior (the tell): **calculator-1-match m4 branch-miss rate 4.51-4.54%, calculator-2-match 2.55-2.67%, vs SPITBOL clean 0.53% / 2.45% on the same fixtures.** SCRIP's calc1 miss rate is **8.5x** the clean oracle's on the same work — the single largest cross-engine branch-behavior gap measured on any kernel in this campaign so far (pattern_bt/string_pattern's prior FINDING never exceeded ~2x).

## ATTRIBUTION (perf record --call-graph=fp -F 4000, m4 arm, self-time / cycles:P; ≥80% named both kernels)

**calculator-1-match** (27,512 samples, sum of all rows ≥0.3% = **91.88%**):
- `*_match_defer_α` (dozens of distinct box instances — n10, n11, n22, n37, n38, n41, n24, n57, n56, n60, n26, n43, n40, n62, n8, …): **≈51.4%**
- `*_match_alternate_*` (af/α/s2/as/β arms of n6, n21, n36): **≈19.6%**
- `PAT$N_{α_body,γ,ω,res}` (the compiled pattern-procedure entry/exit wrappers): **≈11.3%**
- `*_match_span_α/β`, `*_match_lit_α`, `*_match_any_α` (the actual matching primitives): **≈6.6%**
- `*_match_defer_β`: **≈2.5%**
- No RT function individually clears 0.3% in the top-55 list.

**calculator-2-match** (4,654 samples, sum ≥0.3% = **94.46%**):
- Named RT functions: `c_rt_defer_close` 10.78%, `rt_patv_defer_run_all` 10.05%, `rt_dfx_push` 3.43% (pre-cure), `rt_patv_defer_get_pat_dtp` 3.04%, `patv_slot` 2.15%, `__strncmp_evex` 1.07%, plus two `@plt` stub entries — **≈31.3% total**, this kernel's grammar (`ARBNO`/`BREAK`-shaped, per `n8_match_defer_β`, `n42_match_arbno_*` in the list) drives more of the deferred-recursion bookkeeping through the named C path than calc1's does.
- `*_match_defer_α/β` box instances: **≈29%**
- `PAT$N_*` wrappers: **≈10%**
- matching primitives (span/any/lit/arbno): **≈9%**

**Why the two kernels differ:** calc1's grammar (`A|T|F|X` mutual recursion via bare `*X`/`*F`/`*T`) resolves almost entirely through the box-local fast path (few RT symbols even reach 0.3%); calc2's grammar routes more traffic through the named `rt_patv_defer_*`/`c_rt_defer_close` C functions. Both share the SAME root mechanism (see below) — they differ in how much of its cost is visible as "RT function" vs "inlined box code," not in what the mechanism is.

## THE ROOT MECHANISM (source-confirmed, not inferred from symbol names alone)

Calculator's grammar is built entirely from **`*X`-style deferred pattern references** (`A = ... | '(' *X ')'`, `F = '+' *F | ... `, etc — zero `.`-captures anywhere in either program, so this is NOT the capture/defer-pump layer `FINDING-2026-08-27-ceo-patmatch-gap-answered-...` already cured; it is the OTHER deferred mechanism, star-var pattern recursion, `pattern_match.c`'s `pat_defer`/`c_rt_defer_get_pat_fn`/`rt_patv_defer_*` family). Because the referenced pattern is stored in a variable and can recurse to unbounded depth, it cannot be jump-wired at compile time the way a literal/span/alternate box can — SCRIP compiles each `*NAME` reference to a **box that manually manages its own continuations**: `perf annotate` on `n10_match_defer_α` (calc1's hottest self-time symbol) shows the exact shape —

```
  call   rt_patv_defer_get_pat_dtp@plt      ; resolve the target pattern's compiled entry fn ptr -> %rax
  lea    <alt-arm-s1>(%rip),%rcx ; push   %rcx      ; push the "success" continuation
  lea    <alt-arm-af>(%rip),%rcx ; push   %rcx      ; push the "fail" continuation
  jmp    *%rax                                       ; enter the callee with TWO addresses on the stack,
                                                       ; not one -- the callee's own γ/ω exit pops+jumps
                                                       ; to whichever one its internal match actually hit
```

This is a real, working, CPS-style calling convention for the case a plain wired jump can't cover (the target isn't known at compile time). But it defeats the CPU's return-address predictor (RSB): the callee is entered via `jmp`, not `call` (no matching return address is pushed the normal way), and it exits via a manufactured pop-and-jump into one of two caller-supplied addresses rather than a balanced `ret`. **82.85% of `n10_match_defer_α`'s own 12.16% self-time-share sampled on a single static, unconditional `jmp` instruction immediately following the `jmp *%rax`** — a bare direct jump should retire in ~1 cycle; sample counts piling up there rather than on the indirect jump or inside the callee is the signature of RSB-misprediction stalls being charged to the instruction where the pipeline resumes fetching, not to the branch that caused the stall. The elevated branch-miss rate (4.51% vs SPITBOL's 0.53%, measured independently via `perf stat`, not `perf record`) is the second, cross-validating instrument agreeing with the same conclusion — exactly the "two instruments, one answer" bar this campaign has used throughout.

**This is why match/alternate box self-time (≈71% of calc1, ≈39% of calc2) doesn't reduce to a short symbol list the way the capture/defer-pump layer did**: the cost isn't concentrated in a shared RT function that one cache fix can close — it's the constant per-recursion-site branch-misprediction tax of the calling convention itself, paid once per box instance, spread across every `*X`/`*F`/`*T` site in the compiled graph.

## CURE: WHAT IS SEAT-SCALE (landed, measured) VS TEMPLATE-SCALE (handed to hq_P)

**Landed — `rt_dfx_push` marked `static inline __attribute__((always_inline))`** (`src/runtime/pattern_match.c`, one line). Checked safe before landing: (1) not reached from `rtx_match.S` or any compiled BB template — `grep` for call/jump sites into it outside `pattern_match.c` returns none, so no ABI symbol is being removed; (2) it stores no `DESCR_t` in its own frame across a call (it only writes into the CAS-carved `g_dfx[]` array), so it does not carry the GC-stack-scan hazard `rt_patv_defer_get_pat_dtp`'s own comment already documents (`always_inline` on `descr.h`/`core.h` tag predicates broke three deferred-capture tests at s264 by moving descriptors out of GC-visible memory — checked and inapplicable here). Measured, same fixtures, before/after, pristine both times:
```diff
  kernel               insn_total before   insn_total after    Δ insn        Δ%
- calculator-1-match    47,641,135,618      47,634,166,331      -6,969,287    -0.0146%
- calculator-2-match     8,017,228,822       7,941,528,724     -75,700,098    -0.9440%
```
Small (calc2's `rt_dfx_push` self-time bucket was 3.43% of a 4,654-sample profile, consistent with the ~0.9% instruction-count win once call/frame overhead — not the work inside — is folded away), real, and — per the two-part-proof law — directly derived from the stated cause (a `-O0` call that shouldn't exist for a 4-line leaf) and confirmed to work by the measurement, not assumed. Both kernels re-verified byte-answer-identical (`matched bytes=32512`) before and after. Corpus board re-verified on pristine, post-change: see LEDGER.

**Tested and REFUTED — PLT indirection is NOT a material cost here.** `ARCH-PERF-TOOLING.md` §4 lever 4 ("Kill the PLT... free, structural, nobody has tried it") is directly visible in the disassembly (`call rt_patv_defer_get_pat_dtp@plt`, `call rt_patv_defer_run_all@plt` in the hottest box), so it looked like a strong candidate. Measured directly: linked a private, static (no `-shared`, no PLT) variant of both m4 binaries straight against the already-built `out/rt_pic-*/*.o` objects (no shared-file or Makefile change — `out/libscrip_rt.so` untouched, zero risk to concurrently-running seats), byte-answer-verified identical to the dynamic build, then `perf stat`:
```diff
  kernel               insn dynamic(PLT)   insn static(no PLT)   Δ%
  calculator-1-match    47,641,135,618      47,640,119,930        -0.0021%
  calculator-2-match     8,017,228,822       7,986,234,040        -0.3866%
```
Instruction count is essentially unchanged (PLT's per-call tax is 2-3 instructions; these calls do real work inside, so the constant overhead is noise against it); cycles moved in *opposite* directions between the two kernels (calc1 down ~3.4%, calc2 up ~0.9%), which is the signature of shared-box scheduling noise, not a real effect. **This is a documented negative result, not a shrug** — per the TWO-PART PROOF law (a stated mechanism must bear weight when tested), §4's PLT claim was written in 2026-08-21 and never empirically checked; it does not survive being checked on this workload class. Flagging for whoever owns `ARCH-PERF-TOOLING.md` to caveat lever 4 rather than let the next seat re-spend an afternoon on it.

**Handed to hq_P (template/design-scale, per this task's own routing instruction) — the push/push/jmp\*rax continuation convention itself.** This is the dominant, unattributed-until-now cost on both kernels (≈71% / ≈39% of self-time respectively) and it lives in `src/templates/bb_match_defer.cpp` + whatever `x86(...)` encoder emits the two-`push`-then-indirect-`jmp` sequence — squarely template/codegen architecture, not a seat-scale RT fix, and per `RULES.md`'s BB-CODEGEN reading requirement (`ARCH-LANGUAGES.md` + `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` non-negotiable before touching it) it is out of this row's remit to redesign solo. Routed via `s4e_msg.sh send hq_P` with this FINDING's path, the `perf annotate` excerpt above, and the branch-miss cross-check. No cure direction is prescribed here beyond naming the mechanism and the evidence — box fusion / a branch-predictor-friendly dispatch shape for star-var recursion is hq_P's call, matching Lon's own Q1 prediction in `ARCH-PERF-TOOLING.md` ("a backtracking matcher wired as jumps should be bad-speculation bound... the lever is box fusion and fewer unpredictable branches") almost exactly, now with a concrete instance and numbers instead of a prior.

## PROVENANCE

No pre-session number cited without re-measurement; Ir and converged-ns never share a column with wall; every multiple carries its oracle (`sbl_clean_bin()`, `-bf`); the durable store gained a new dated file (`perf-attribution-20260828T033014Z.tsv`), nothing was overwritten. `/usr/bin/perf` confirmed still broken on kernel `6.17.0-1032-oem` this session (re-hit the exact warning `FINDING-2026-08-27-seat06...` documented); `/usr/lib/linux-tools-6.8.0-138/perf` used throughout, as that FINDING recommends.
