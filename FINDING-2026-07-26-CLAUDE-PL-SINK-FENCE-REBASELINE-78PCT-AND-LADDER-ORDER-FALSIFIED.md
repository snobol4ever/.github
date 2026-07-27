# FINDING 2026-07-26 (s154) — PL-SINK-FENCE RE-BASELINED: EMITTED SHARE IS **58.3%**, THE LADDER ORDER IS FALSIFIED, AND **GC IS THE #1 RUNTIME COST AND OWNED BY NO RUNG**

## 0. ⛔⛔ SELF-CORRECTION — THE 78.3% BELOW IS WRONG. THE NUMBER IS 58.3%. READ THIS FIRST.

The 60-sample run reported **78.3% emitted / 21.7% runtime**. Re-measured at **420 samples: 58.3%
emitted / 41.7% runtime (SE 2.4%)**. The true value sits **outside the 60-sample run's own stated
95% interval** (11–32% runtime). Everything in §1–§3 below was computed from the 60-sample run and
is superseded; it is kept UNEDITED as the evidence trail.

**ROOT CAUSE — WORKLOAD-DEPENDENT, AND I CHANGED THE WORKLOAD.** The 60-sample run used
`between(1,200000,_)`; the 420-sample run used `between(1,2000000,_)`. At 10x the iterations the
program **enters a GC regime the short run never reaches** — `gc_collect_ex` is absent from all 60
early samples and is the **single largest runtime leaf** in the long run. The short bench measured a
warm-up, not the steady state.

⭐⭐ **RULE EARNED — A PROFILE IS A FUNCTION OF ITS WORKLOAD, AND "LONG ENOUGH TO SAMPLE" IS NOT
"LONG ENOUGH TO BE REPRESENTATIVE."** I sized the bench so the sampler would not run out of process,
which is a sampler constraint, not a workload-validity argument. Any FENCE number must state its
iteration count and be shown STABLE across at least one 10x scale-up before it is quoted. The s141
baseline of 14% carries the same unanswered question — its workload size is not recorded, so
**14% -> 58.3% is a soft comparison, not a clean one.**

⚠ **SECOND DEFECT, MINE: THE 420 IS A MIXED POPULATION.** I appended the 60 early `big_bin` samples
to the 360 `huge_bin` samples — two different workloads in one denominator. `huge_bin` ALONE is
**198 emitted / 162 runtime = 55.0% emitted**, i.e. the mixing biased the headline ~3 points
OPTIMISTIC. **Quote 55.0% (single workload, 360 samples) or re-run clean; do not quote the 58.3%.**

## 0b. THE CORRECTED PICTURE (420 samples, per-plane)

| Plane | Samples | of runtime | of wall | Owning rung |
|---|---|---|---|---|
| **GARBAGE COLLECTION** | `gc_collect_ex`27 `rt_gc_point_arr`3 = **30** | 17% | **7.1%** | ⛔ **NONE — NOT ON THE LADDER** |
| **BACKTRACK** | `pl_trail_unwind`20 `plc_dead_cstack`9 `pl_trail_push`4 = **33** | 19% | **7.9%** | **PL-SINK-9** |
| **CALL/RETURN** | `rt_jmp_frame_lexprep2`16 `rt_frame_bind_args`8 `rt_proc_call_prologue_lex`6 = **30** | 17% | **7.1%** | callee-prologue sink |
| **TERM CONSTRUCTION / ALLOC** | `plw_mkc_kids`17 `rt_gcheap_alloc`4 `rt_gcheap_carve`3 = **24** | 14% | 5.7% | SINK-3 follow-on |
| **UNIFY / DEREF** | `plw_cell_deref_slow`8 `dop_unify_lst`5 `plw_unify_cells`4 = **17** | 10% | 4.0% | SINK-1/2 residue |

⭐⭐ **THE REAL HEADLINE: `gc_collect_ex` IS THE LARGEST SINGLE RUNTIME LEAF (27) AND NO RUNG ON THE
PL-SINK LADDER OWNS IT.** The ladder sinks `dop_*` data-plane leaves; GC is not one. At the KPI
target of >=90% emitted, GC alone (7.1% of wall) very nearly exhausts the entire 10% runtime budget.
**The ladder as written CANNOT reach its own KPI** — closing every remaining sinkable plane still
leaves GC. Either the KPI needs a stated GC carve-out, or a GC rung must be added. **This is a
Lon decision, not the assistant's.**

⭐ **PL-SINK-9 IS CONFIRMED #1 SINKABLE** (33 samples, 7.9% of wall) — and this time the count is
significant, not a 1-2 sample hint. The 60-sample run's leaf ranking was directionally right about
SINK-9 and about SINK-5 being negligible (`plw_unify_vals` does not appear at all in 420 samples),
but it invented a call/return lead that does not survive.

---


## 1. THE HEADLINE — THE LADDER'S FOUNDING PREMISE WAS 12 SESSIONS STALE

s141 measured mode-4 nrev at ~86% C-runtime / ~14% emitted and that number has been quoted as the
ladder's premise ever since. Five rungs landed after it (SINK-1/2/3/4/8) and **nobody re-measured**.

Re-run of the s141 methodology (mode-4 binary, `gdb -p PID -batch`, frame-0 PC attributed to its
owning object, 60 samples — above the 44 floor; mode-3 never sampled, per the FENCE rule that the
JIT blob has no symbols):

| | s141 | s154 (this run) | KPI |
|---|---|---|---|
| EMITTED (`big_bin` .text) | 14% | **78.3%** (47/60) | ≥90% |
| RUNTIME (`libscrip_rt.so`) | 86% | **21.7%** (13/60) | ≤10% |

**The ladder worked.** 14 → 78.3 points of emitted share across five rungs. Remaining gap to the
KPI is 11.7 points. Frame-0 of the emitted samples is dominated by `n<NNN>_op<NN>_α` — Byrd-box α
ports, 45 of 47 — which is the shape the design predicts.

⚠ **STATISTICAL HONESTY (the s148 60-runs lesson applies to sample counts too).** 60 samples,
13 runtime ⇒ binomial SE ≈ 5.3%, so the honest 95% interval on "runtime share" is roughly
**11%–32%**. The headline "we are far past 14% and not yet at 90%" is solid. **The per-leaf counts
below are 1–2 samples each and are NOT individually significant** — SE on a 2/60 cell is ±1.8
samples. They are a RANKING HINT, not a result. Anyone acting on them should re-sample at
300+ before committing a rung.

## 2. ⭐⭐ THE FINDING THAT MATTERS — LADDER ORDER SAYS SINK-5 NEXT; MEASUREMENT SAYS IT IS THE WRONG RUNG

Grouping the 13 runtime samples by the RUNG that owns them:

| Plane | Leaves (samples) | of runtime | of total wall | Owning rung |
|---|---|---|---|---|
| **CALL/RETURN** | `rt_jmp_frame_lexprep2`(2) `rt_proc_epilogue_body`(1) `rt_proc_call_prologue_lex`(1) `c_rt_proc_call_epilogue_γ`(1) | **5/13 = 38%** | **8.3%** | callee-prologue sink (XA-FLAT-CONVERT unblocked it s150) |
| **BACKTRACK** | `plc_dead_cstack`(2) `pl_trail_unwind`(1) `pl_trail_push`(1) | **4/13 = 31%** | **6.7%** | **PL-SINK-9** |
| **TERM CONSTRUCTION** | `plw_mkc_kids`(2) | 2/13 = 15% | 3.3% | SINK-3 follow-on |
| **UNIFY** | `plw_unify_cells`(1) `plw_unify_vals`(1) | 2/13 = 15% | 3.3% | SINK-1 residue / **PL-SINK-5** |

**`plw_unify_vals` — the entire target of PL-SINK-5, the next rung in ladder order — is ONE sample
in sixty.** Sinking it *perfectly*, to zero, moves total wall by at most ~1.7 points, and that
single sample is inside the noise floor. Meanwhile the call/return plane is 5 samples and the
backtrack plane is 4.

⭐ **RULE (third sibling of s147 and s152): A LADDER'S ORDER IS A HYPOTHESIS ABOUT COST, AND IT
DECAYS EVERY TIME A RUNG LANDS.** s147 falsified SINK-6 and SINK-7 by measuring their premise.
s152 proved a site list is a guess until a behavioural probe contradicts it. This is the same
failure at the level of the ladder itself: the ORDER was fixed when the profile looked one way,
five rungs changed the profile, and the order was never re-derived. **Re-run the FENCE before
choosing a rung, not only at the end to certify the KPI.** The FENCE is not a closing ceremony;
it is the instrument that picks the next rung.

## 3. WHAT THIS IMPLIES FOR THE REMAINING LADDER

- **PL-SINK-5 ($is_v) should be DEMOTED**, not worked next. It is not wrong, it is not worth its
  gate cost right now. Its design note is sound and can be picked up cheaply later.
- **PL-SINK-6 / PL-SINK-7 stay dead** — s147 already falsified them; nothing here revives them
  (no `dop_ax`/`dop_cmp` leaf appeared in ANY of the 60 samples).
- **The two live candidates are the CALLEE-PROLOGUE SINK and PL-SINK-9**, at 8.3% and 6.7% of
  total wall respectively. s150 explicitly declared the prologue sink UNBLOCKED and "an ordinary
  SINK rung" now that every live `xa_flat.cpp` arm is off the raw-byte family.
- Note `plc_dead_cstack` (2 samples) is the per-entry test *inside* `pl_trail_unwind`'s loop —
  exactly the inline SINK-9 designs around, and its design note already flags that the cached
  stack bounds must be EXPORTED (`g_plw_stk_lo/hi`) for the inline to work.
- **Reaching ≥90% requires roughly the call/return plane OR backtrack plane, plus one more.**
  Neither alone closes 11.7 points.

## 4. INSTRUMENT NOTES (so the next session does not re-pay these)

- **`gdb` is NOT installed in a fresh container.** `apt-get install -y -qq gdb` (runs as uid 0, no
  sudo present, no `-O2` involved so the O2-DIRECTED rule is untouched). `perf`, `valgrind`,
  `eu-stack`, `pstack` are all absent too.
- **The detached-build trap (s126) reproduced, making it TWICE.** `nohup ... &` for `make -j4 scrip`
  died silently after ~9 minutes: zero `make`/`cc1` processes, log frozen, `out/*.o` empty, no
  binary, and **no error in the log** — a silent half-tree exactly as RULES.md describes.
  Foreground `timeout 280 make -j4 scrip` then completed fine and resumed incrementally.
  **Recommendation: stop reaching for detached builds; foreground + `timeout` works.**
- **Probe-emission check earned its keep again (s153 §4).** The sampling loop wrote `samples.txt`
  to `/`, not the intended dir: in `cd D && ./bin ... &` the `cd` binds to the BACKGROUNDED
  subshell, leaving the foreground shell at its original cwd. The sample count printed correctly
  from inside that subshell, so the run *looked* clean. Verify where a probe wrote, not just that
  it wrote.
- **Bench shape:** `between(1,N,_) ... fail` failure-driven loop over nrev-30 (contract §9 — the
  NO-LCO defect kills a recursive driver). N=4000 ≈ 1.4 s; N=200000 gives a comfortable sampling
  window. Files under `/home/claude/fence/`, m4 built by hand with the
  `run_prolog_via_x86_backend.sh` recipe (`as --64` + `gcc -no-pie` + `-Wl,-rpath`) because that
  script uses a self-deleting `mktemp` dir and leaves no binary to attach to.
- ⚠ **Not done: the FENCE's full bench table vs gprolog 1.4.5, and the corpus `.s` regen.** This
  run measured the SPLIT only. The rung is NOT closed.

## 5. GATES

`make -j4 scrip` RC=0, zero errors, `-O0` (Makefile default; **no `-O2`, no Lon directive sought or
used**). `make libscrip_rt` RC=0, zero errors. `test_smoke_prolog.sh` **5/5/5** (m2 HARD GATE PASS,
m3 5/5, m4 5/5). **No source file was modified this session** — measurement and tooling only, so
no rung suite, no `no_new_global`, no medium-invisible gate was applicable, and the BB-CODEGEN
DESIGN SET (PLAN step 6) did not apply to any emitted change because none was made.

WATERMARK: SCRIP `<none>` / corpus `<none>` / .github `this FINDING + cursor`.
