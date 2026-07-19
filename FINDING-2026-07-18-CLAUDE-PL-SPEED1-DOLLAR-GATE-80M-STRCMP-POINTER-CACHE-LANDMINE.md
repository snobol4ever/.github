# FINDING 2026-07-18 — PL-SPEED-1 landed + the 80M-strcmp dispatch ladder killed by a one-line $-gate; the strdup'd-name pointer-cache land mine found and defused; RSP-F-3 validate+measure completed; the crypt "regime tradeoff" re-bracketed to the accrual cliff

Session s98 (Claude Fable 5). Follows s97 (`d52fdaac`, RSP-F-2). Session HEAD at start: `f405c6a7`
(the parallel ICN dead-GOTO reap had landed on top of s97's cursor hash; Prolog board holds through it —
measured, not assumed).

## 1. RSP-F-3 VALIDATE + MEASURE — completed first, at pristine HEAD

VALIDATE: rung 138/138 ×3 (three consecutive runs), smoke 5/5 ×3 modes, 4-way consensus 21/22
(sole divergent = queensn, the tracked WS leak), gprolog 1.4.5 + SWI 9.0.4 oracles, refs/ symlinked
from the uploaded gprolog/swipl zips.

MEASURE (full vanroy rail, same container/CPU class as the s95 baseline — Xeon 2.80GHz ×1):

**GEOMEAN m4/GNU: 199× → 184.96× · m4/SWI: 144× → 117.49×** (s95 baseline → post-RSP-F-2 HEAD).

Per-row headlines vs the s95 README table (within-run ratios are the honest cross-session metric; GNU's own
per-iter times drifted up to 2.6× between runs = shared-tenancy noise on identical nominal hardware):
ham 3899× → 209× (m4 absolute 160.6s → 6.3s/iter, ~25× — the trail death-tidy killed the WS storm's
biggest component); deriv 312× → 101× (~4× absolute); tak 117× → 76× (guard-complementarity DET);
fib m4 420 → 206 ms/iter; crypt absolute IMPROVED 93.25 → 81.25 ms/iter even though its ratio "worsened"
80× → 130× (GNU ran 1.9× faster that run).

⚠ NEW ANOMALY BANKED: **ham m3 = 168 s/iter vs m4 = 6.3 s/iter — a 26× m3/m4 split**, breaking the
"m3 ≡ m4 on every row" README invariant. Shape hypothesis (unproven): m3 shares the process heap with the
compiler's own allocations and an allocation-storm bench pays in-process costs m4 does not. Needs its own
bracket; not chased.

## 2. The crypt/deriv "det-regime tradeoff" (s97 banked) — RE-BRACKETED to the accrual cliff, regime exonerated below it

Measured wall(N) for crypt m3, det-on vs SCRIP_PL_DET=0, failure-driven loop:

| N   | det on   | det off  |
|-----|----------|----------|
| 4   | 503 ms   | 347 ms   |
| 8   | 678      | 664      |
| 16  | 1355     | 1342     |
| 32  | 2645     | 2638     |
| 64  | 5298     | 5320     |
| 96  | >90 s TIMEOUT | >90 s TIMEOUT |
| 128 | >100 s TIMEOUT | >100 s TIMEOUT |

Linear and REGIME-IDENTICAL (~83 ms/iter marginal) through N=64; BOTH regimes explode between N=64 and
N=96. The cliff is defect (b) — the fail-loop WS accrual — and it is REGIME-INDEPENDENT. s97's 65-vs-130
window counts were taken AT the cliff edge, where a 30 s window is maximally variance-sensitive; the rail's
small-N per-iteration numbers (crypt m4 81 ms, BETTER than the pre-regime 93) agree. Conclusion: there is no
per-iteration det-regime cost on crypt to hunt; the lever is the accrual itself (PL-WS-2 streams / SPEED-3
reclamation). deriv's rail row (4× absolute better than baseline) says the same for deriv. The s97 candidate
mechanisms (a)/(b)/(c) stand un-hunted but the payoff bracket moved.

## 3. PL-SPEED-1(i) O(1) proc registry — LANDED, honest result: correctness/complexity win, NOT a geomean mover

`rt.c`: FNV-1a open-address hash (`g_proc_hsl`/`g_proc_hcap`, index+1 slots, ×2 growth at 75% load,
rebuilt-on-grow, cleared by `rt_proc_reset`), seeded at both registration appends; ALL 20 hand-rolled
linear strcmp scans over `g_rt_gen_procs[]` converted to `rt_proc_hash_lookup`/`rt_proc_find`;
`rt_proc_call_gen_h`'s second per-call lookup (`rt_proc_is_generator(name)`) collapsed onto the already-held
`p->is_generator`. Registration goes O(n²)→O(n); every by-name query is O(1) worst case.

MEASURED A/B (fib/qsort/deriv/crypt, m3): ±5% = container noise, NO speedup. The det call path
(`rt_proc_call_open` → `rt_proc_find`) was ALREADY absorbing its lookup in the pointer-identity cache; the
s97 cursor's "rt_proc_call_open strcmp is still on every det call" named the right function but the scan was
not hot at van-Roy proc counts. Kept because it is strictly better (bridge names with fresh pointers no
longer fall to linear; gen_h double scan gone; big-program registration no longer quadratic).

## 4. THE REAL HOT PATH — measured, not guessed: 80.4M strcmps in two fib(20) iterations

perf (the versioned `/usr/lib/linux-tools-6.8.0-136/perf`; the `perf` wrapper refuses this container's
kernel string) put ~63% of fib m3 samples in libc strcmp + the two by-name dispatchers. fp call-graphs
through emitted blobs resolve to .rodata garbage (0x72f0d8 = the port-name strings), so attribution came
from an LD_PRELOAD strcmp shim histogramming return addresses:

**TOTAL = 80,447,781 strcmp calls for fib(20) ×2 iterations (~44K predicate calls ≈ 1,800 strcmps/call)**,
with a flat run of consecutive sites at exactly 399,209 hits each — the signature of a FULL LADDER WALK per
builtin goal. Route: every emitted Prolog builtin goal (`$is_*`, `$cmp_*`, `$unify`, `$trail_*`, ...) is a
`call rt_call_arr` (21 sites in fib.s); `rt_call_arr` walks ~30 operator strcmps (fn[0]='$' enters the
non-identifier block) then `try_call_builtin_by_name`'s ~201-arm general ladder — ALL MISSES, the general
ladder contains ZERO '$'-prefixed arms (grepped) — before the Prolog dispatcher is ever consulted.

## 5. THE FIX — one line: '$'-prefix fast-route in rt_call_arr

`by_name_dispatch.c` `rt_call_arr`, before the operator block:
`if (fn[0] == '$' && fn[1]) { if (script_try_call_builtin_by_name(fn, args, nargs, &out)) return out; out = FAILDESCR; }`

Semantics-preserving by construction: the general ladder has no '$' arms; `script_try`'s miss path is
side-effect-free and returns 0, falling through to the ENTIRE unchanged chain (so pathological '$' names —
multi-char '$' OPSYN aliases, dat fields — keep today's behavior); bare "$" (fn[1]==0) is excluded to leave
the SNOBOL4 indirect-ref operator name untouched. Per-language behavior in the by-name runtime is the
sanctioned place (LANGUAGE-BLIND rule constrains templates/emitter, not runtime dispatch).

**MEASURED: fib N=8 m3 1751 → 668 ms (2.62×); crypt N=64 m3 5298 → 2109 ms (2.51×).**

## 6. ⚠ THE LAND MINE — strdup'd-name pointer reuse vs the rt_proc_find pointer-identity cache

Routing `rt_call_proc_descr`/`rt_proc_call_gen_h` through `rt_proc_find` (step 3) broke exactly ONE test:
raku `rk_class26` (stash-A/B pristine fail-set 21, mine 22, delta = rk_class26, FAIL ×3 in isolation —
consistent, not flake; symptom: `scale` lost its `* $factor`, `greet` vanished — wrong METHOD dispatched).
A verify shim (hash lookup cross-checked against linear scan on every call) reported ZERO divergences and
STILL failed → the lookups were right; the cache was the bug: `rt_proc_find`'s direct-mapped cache is keyed
on the NAME POINTER (`g_proc_idx_key[h] == name`), and the Raku method bridge passes strdup'd names
(`s->pi = strdup(pib)`, freed per call) — malloc reuses the SAME ADDRESS for a DIFFERENT method name, the
cache hits, and the WRONG proc is returned. Pristine's call paths dodged it only because they used raw
content scans; the cache's pre-existing users pass RO names. **This was a LATENT PRE-EXISTING bug for
`rt_call_named_proc`'s bridge callers** — any strdup'd name could mis-dispatch given address reuse.

FIX (defuses the latent bug too, one comparison): a cache hit now ALSO requires the registry's stored
pointer to equal the query pointer — `g_rt_gen_procs[ci].name == name` — in BOTH `rt_proc_find` and
`rt_proc_index_of`. RO names (registered and queried with the same pointer) still hit; heap names never
false-hit and fall to the O(1) content hash. rk_class26 PASS; raku fail-set pristine-identical (21).

## 6b. ⚠ RAIL ARTIFACTS FOUND WHILE MEASURING THE GATE — read before trusting any rail row

(1) **meta_qsort's rail row is INVALID on every rail run, pre- and post-diff — the rail is blind to aborts.**
Verified with an output-counted wrapper run: `l__(1000)` prints ok ×8 then SIGABRT (~550 ms wall) — the
PRE-EXISTING nondet retained-frame abort (s95 defect (c), s97 "meta_qsort still SIGSEGVs"). Stash-A/B:
PRISTINE also dies at exactly ok-count=8 — this session's diff did not move the knee. The rail times the
short abort wall as if N iterations completed → phantom per-iter (post-diff row printed 0.0038 ms/iter =
"100× faster than GNU", impossible; rail1's 33.5 ms/iter @N=16 row is the same artifact class with a
different abort-wall). RAIL DEFECT to fix in bench_prolog_vanroy.sh: count an output token (or require rc=0)
per attempt; abort ⇒ DNF, never a datapoint.
(2) **ham is accrual-dominated at N=1 and swings multi-× between runs of the SAME binary class**
(s95 160 s → rail1 6.3 s → rail2 47.5 s per iter, m4) — treat ham's per-iter as order-of-magnitude only
until defect (b) lands.
(3) PROCESS NOTE, self-inflicted: rail2's tail (queens_8..zebra) SKIPped because this session ran the
meta_qsort stash-A/B — rebuilding scrip — UNDER the running rail; its 52.13 "geomean" spans a partial row
set and is VOID. The first 13 rows (cal..qsort, final binary, pre-meddling) are valid and are quoted above.
Rail3 (clean, untouched machine) is the number of record below. RULE RESTATED FOR NEXT SESSION: nothing
rebuilds or benches while a rail is live.

## 6c. Number of record — full clean rail on the final diff (rail3)

RAIL3_RESULTS_PLACEHOLDER

## 7. Board at the final diff (2 files: rt.c, by_name_dispatch.c)

rung 138/138 ×3 · prolog smoke 5/5 ×3 modes · 4-way 21/22 (queensn only) · icon smoke 14/14 ×2 ·
sno smoke 7/7 + crosscheck at watermark (single known DIVERGE 1017_arg_local, pre-existing per HEAD commit
message) · raku full suite fail-set PRISTINE-IDENTICAL (21, stash A/B) · `test_gate_pl_no_new_global`
PASS floor 14. The two new rt.c statics (`g_proc_hsl`/`g_proc_hcap`) are registry infrastructure beside the
existing three registry globals, outside the pl gate's scan set — flagged here for visibility, same class
as `g_rt_gen_procs` itself.

## 8. Next levers, in measured-payoff order

(1) **defect (b) WS/trail accrual** — owns the crypt/qsort/log10 cliffs AND fib's fail-loop wall;
(2) **the by-name dispatch ladders themselves** — post-gate, `script_try`'s own arm order + `pl_arith2`'s
strcmp chains are the next strcmp mass (the gate removed the 231-arm dead walk, not the live arms);
(3) SPEED-2 frame-init elision (`rt_jmp_frame_lexprep` was 3.2% of fib pre-gate, larger share now);
(4) the ham m3/m4 26× split.
