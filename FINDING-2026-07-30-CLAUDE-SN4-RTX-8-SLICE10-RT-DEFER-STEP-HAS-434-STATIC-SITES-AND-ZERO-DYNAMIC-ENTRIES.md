# FINDING s225 — RTX-8 SLICE 10: `rt_dcap_step` LANDED, AND THE SYMBOL IT REPLACED HAS 434 STATIC CALL SITES AND ZERO DYNAMIC ENTRIES

## 1. THE RESULT THAT OUTRANKS THE PORT
This rung was aimed at **`rt_defer_step`**, chosen because it is **#2 in the entire SNOBOL4 artifact census by static call sites (434)**, behind only `rt_call_arr`. Step 0(d) measured it at **ZERO dynamic entries** on `json.sno`+`twitter.json`, `calculator-1.sno` and `calculator-2.sno` — the three programs carrying 82/32/30 of those sites.
⇒ **A static call-site count measures the EMITTER'S REACH, not execution.** This is the s188 `rt_call_arr` class at 4x the site count, and every step-0 check EXCEPT 0(d) passed it: live definition, exact spelling, clean globals, not already asm. Had 0(d) been skipped, the port would have been built, gated green by a suite that never executes it, and recorded as a landing.

## 2. THE SECOND CENSUS SAVED THE RETARGET TOO
`rt_dcap_step` is hot (0(d): 26,967 / 29,573 / 31,184 / 85,035 across four workloads, scaling with input size). But 0(f-pre) enumerated four arms and an **LD_PRELOAD interposer measured the distribution BEFORE any asm was written** (the s216 `rt_cap_push` discipline):
- ARM A `g_dcf_top <= 0` -> return 0
- ARM B `nm.v == DT_FAIL` -> **0 of 56,540**
- ARM C `nm.v == DT_S|DT_SNUL` -> **0 of 56,540**
- ARM D `rt_assign_var(nm, c->pending)` then tail-jump the pump -> **56,540 of 56,540 = 100%**
Both cold arms are DELEGATED, not deleted. Delegating ARM C also keeps **`NV_SET_fn` untouched** — the goal file's concurrency contract names it as DB-1's planned write-barrier choke point, so reimplementing it here would have collided with an unlanded design.
WARNING - POPULATION STATED IN THE SAME SENTENCE (s224 rule): the arm census is **TWO PROGRAMS, NOT THE CORPUS**. It is a sample and is NOT a corpus-wide zero for arms B/C.

## 3. 0(c) SPLIT INSIDE ONE 15-INSTRUCTION FUNCTION
- `g_dcf`, `g_dcf_top`, `rt_dcap_pump`: ABSENT from `nm -D libscrip_rt.so` => hidden => direct `[rip+sym]`.
- `rt_g_want_name`: **PRESENT in the dynamic table** (`rt/rt.c:634`, no visibility attribute) => exported => PREEMPTIBLE => **`@GOTPCREL` mandatory**.
All read `B` in `out/rt_pic/*.o`; only the dynamic table separates them. This is the `g_hp_fr` link failure that cost RTX-2 a rung, live inside a single body. **ZERO `static`->`hidden` promotions were needed by this port.**

## 4. WHAT LANDED
`rt_dcap_step` in `rtx_match.S`, gate `SCRIP_RTX_MATCH`, C -> `c_rt_dcap_step` same commit. 15 instrs on the hot arm. Bail-before-mutate is free: ARM A's test and both delegation tests sit above `.Lrtx_dcs_mutate` and nothing above it writes memory. ZERO templates => no `.s` regen owed. `.so` `1188c597`, RT_OPT=`-O0`.
MANUAL (Ch.9 p.134, read this rung): the deferred-name case is the manual's own `'ABCDE' ? LEN(2) . *PUSH()` — the name is not known until flush time and computing it may run user code (NRETURN, p.133). That is why the pump and the STR arm stay in C: re-entrancy, ordering and the NRETURN edge are structurally unchanged.

## 5. GATES
Watermark re-proven at session start AND after the port, HELD EXACTLY: **m3 312/4/0 · m4 312/2/2 · DIVERGE=2**, fail sets `{test_case,140,141,160}`/`{test_case,160}` unchanged.
**Kill-switch hash sets `MODE=both`, N=4, 316 programs: GATE PASS, ZERO MOVERS.** Quarantine = `160_pat_alt_inner_gen_resume` only, and its OFF arm carries two hashes too, so the instability is C-side and cannot be the asm. Skips = the known 3 (m4 link).
Two-sided `ud2` at `.Lrtx_dcs_mutate`: **ON rc=132 SIGILL · SAME BUILD OFF rc=0 correct.** Probe sized from the COMMIT count per the s223 rule — ARM D is 100% of entries with no lazy-init latch, so the first call commits.
Revert proven: `grep ud2` = 0 and the `.so` returns **BIT-IDENTICAL** `1188c597`.

## 6. NO SPEED NUMBER, AND THE REASON IS THE INSTRUMENT
`bench_rtx_3arm.sh` REFUSES every window on this machine (s224: intra-arm spread 2.1-2.6x, the s201 hugepage bimodality). Nothing in this family is gradeable until the rail grows a min-of-N / hugepage mode. The saving here is one `-O0` frame plus branch ceremony on ~30K calls/run — below the +-3% null floor even if the rail worked. **ERADICATION slice serving RTX-12. The 3-arm rail was deliberately NOT run.**

## 7. OWED
`test_rtx_unit.sh` and the store-width gate were NOT run this session (context exhaustion, stated plainly rather than omitted). `util_rtx_count_syms.sh` returned rc=139 on `treebank-list.sno` — the known segfault rung; that zero was NOT read as "never called".
