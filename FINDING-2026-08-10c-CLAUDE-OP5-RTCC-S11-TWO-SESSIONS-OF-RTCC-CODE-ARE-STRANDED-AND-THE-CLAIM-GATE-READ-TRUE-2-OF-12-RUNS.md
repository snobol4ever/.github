# FINDING — s11 (2026-08-10, Claude Opus 5): TWO SESSIONS OF RTCC CODE ARE STRANDED ON A DEAD WORKTREE, THE CLAIM GATE READ TRUE IN 2 OF 12 RUNS, AND RC-6's INHERITED OPENING RANK IS THE STATIC RANK CONVICTED THREE TIMES

**Goal:** `GOAL-RTCC.md` · **Rung:** RC-0 class (scripts + census only, ZERO emitter bytes, no regen owed, CONCURRENCY-SAFE)
**SCRIP:** `a5533659` at open → `9f451e55` → `405009cd` at close.
**Class:** two landed script fixes + one census correction + one recovered-state alarm.

---

## 0. HEADLINE

1. **s9 and s10's SCRIP commits do not exist in the repository.** Their `.github` FINDINGs are pushed; their code is not. The s10 cursor's HEAD (`7d67fd90`) and s9's close (`1fa5f0c5`) are `unknown revision`. **The claim-gate v2 that s9 recorded as landed is NOT in the tree** — the tree carries v1, the nondeterministic one.
2. **The v1 gate was measured reading TRUE in 2 of 12 runs** on an unchanged tree. Independently reproduced, and the undercount is worse than s9 recorded (new low of 5 vs s9's 6). Fixed and falsified both directions.
3. **RC-6's inherited opening recommendation (`rt_call_arr`, "99 emitted sites") is a STATIC call-site rank** — the exact ranking shape this repo has convicted as anti-correlated with hotness **three times, in two languages**. RC-6's own charter says "ordered purely by *measured* hotness."
4. **RC-6's instrument was BUILT and the inherited target is falsified by five orders of magnitude:** `rt_call_arr` ("99 emitted sites, top of the hotness rank") executes **4 times** on fibonacci while `rt_arg_stage` executes **2,692,537**. And the hot set is **workload-dependent** — on roman the top is `rt_defer_*` and `rt_call_arr` is 100,005. There is no single hotness rank to order RC-6 by.

---

## 1. THE STRANDED WORK — DOCS PUSHED, CODE NOT

Checked every commit hash s8/s9/s10 recorded:

| hash | session | in repo? |
|------|---------|----------|
| `2af35d7d` | s7 fix | EXISTS |
| `5b435458` | s8 close (H2 hardening) | EXISTS |
| `4a0102e9` | s8 in-session fix | absent as a hash — **content present** (rebase renamed it) |
| `c7e085fd` | s9 open | EXISTS |
| `1fa5f0c5` | s9 close (claim-gate v2) | **ABSENT** |
| `7d67fd90` | s10 (cursor HEAD) | **ABSENT** |

A missing hash alone proves nothing — `git pull --rebase` at handoff rewrites hashes, which is exactly what happened to s8's `4a0102e9` (hash gone, `AB_TC_REG` content present in `src/templates/bb_func_activate.cpp`). **So the test is CONTENT, not hash.** By content:

- s8's work: **PRESENT** (`AB_TC_REG` r10 fix live at `bb_func_activate.cpp:25,26,207`).
- s9's claim-gate v2: **ABSENT.** No CHECK 2 (crossing-carry), no CHECK 3 (macro coherence). Line 73 still carries the v1 defect verbatim.

Meanwhile all five `OP5-RTCC` FINDINGs sit in `.github`. **The docs were pushed and the code was not** — the STALE-ORIENTATION conviction shape from s19–s26, recurring. Note this is *not* the RULES.md §6b failure of never asking for a credential; whatever happened, the asymmetry (one repo pushed, another not) is the diagnostic, and it is exactly what `handoff_status.sh` exists to catch across *every* repo with an origin remote.

⚠ **Everything s9 and s10 claim as landed must be treated as unlanded until re-proved by content.** Their *reasoning* stands on its own merits and this session corroborates the central one; their *tree state* does not exist.

⛔ **CONSEQUENCE FOR THE CURSOR:** s10's line *"Watermark re-proved at open and close: claim-gate `--strict` PASS"* describes a tree nobody can check out. And on the tree that does exist, that PASS was a coin flip — see §2.

---

## 2. THE CLAIM GATE READ TRUE IN 2 OF 12 RUNS

### 2.1 Reproduced, and worse than recorded
`scripts/test_gate_rtcc_claimed_regs.sh`, unchanged tree, N=12, counting `GVARQ READERS`:

```
6 5 6 6 6 6 6 8 8 6 7 7          truth = 8
```

Correct in **2/12 runs (17%)**. s9 recorded `8,6,7,6,6,7` (min 6); this session found a **new low of 5**. Since `COLLISION CLASS = writers ∩ readers`, an undercounted readers list can empty the intersection and print `PASS` on a tree that should `FAIL`.

### 2.2 Mechanism — TWO regimes, both probed
Line 73 was `strip_comments "$f" | grep -q "GVARQ("`, where `strip_comments` is `sed | perl`, under `set -uo pipefail`. `grep -q` exits on first match, closing the pipe; upstream perl takes SIGPIPE (141); `pipefail` propagates the non-zero — **a MATCH reads as a MISS**.

**Regime A — deterministic loss above the pipe buffer.** Synthetic probe, match on line 1, upstream padded:

| upstream lines | match read correctly |
|---|---|
| 1 | 20/20 |
| 100 | 20/20 |
| 10,000 (~48 KB) | 20/20 |
| 100,000 (~588 KB) | **0/20** |

Sharp threshold at the 64 KiB pipe capacity: below it the upstream's write completes into the buffer and it exits 0; above it the upstream blocks and is killed by the reader's early exit.

**Regime B — scheduling race below the buffer.** No template exceeds 64 KB stripped, so the gate lives here. Per-file, 20 runs each:

| file | stripped bytes | correct | first match |
|---|---|---|---|
| `bb_var_global.cpp` | 1,812 | 20/20 | line 20 |
| `bb_assign_global.cpp` | 3,579 | 20/20 | line 27 |
| `bb_call.cpp` | 28,733 | **14/20** | line 85 |
| `bb_func_activate.cpp` | 15,778 | **13/20** | line 142 |
| `bb_call_proc_staged.cpp` | 51,780 | **16/20** | line 196 |

Flip rate tracks how long perl is still in flight when grep matches. **3 flippers over 5 stable files predicts a 5–8 range — exactly the range observed.** The mechanism is fully accounted for.

⭐ **The sharpest point: the worst flipper (13/20) is `bb_func_activate.cpp` — the very file s8 CONVICTED of a real SIGSEGV.** The gate was least reliable precisely where it mattered most.

### 2.3 Fix and falsification (`9f451e55`)
Fix mirrors the scan at line ~67, already stable because `grep -c` reads to EOF and cannot SIGPIPE its upstream. After: **20/20 runs report 8.**

Falsified BOTH directions — a gate that only ever passes is worthless:
- Synthetic template writing `r9` and reading `GVARQ` ⇒ `COLLISION CLASS: zz_probe_collision.cpp`, `[UNCLEARED]`, `GATE: FAIL (strict)`, exit 1.
- Removed ⇒ exit 0.

Corroboration: `HAZARD SURFACE : 19` independently matches s8's "19 remaining `lea r9, FRQ(..)` sites".

### 2.4 The portable sweep (s9's open action, now done)
Swept `scripts/` for `| grep -q` under `pipefail`. Raw grep yields ~20 sites, but **the hazard requires an EXTERNAL upstream still writing**, so the list must be classified, not counted:

- **SAFE — no pipeline:** `grep -qx PATTERN FILE` (`util_rtx_claims.sh:242`, `wl_has()` line 50). grep reads the file directly; nothing upstream to signal.
- **SAFE in practice — builtin upstream:** `echo "$var" | grep -q` / `printf '%s' "$out" | grep -q` (the large majority: `test_emit_diff_invariant_check.sh`, `test_invariants_3x3_harness.sh`, `test_gate_icn_*`, `test_prolog_rung_suite.sh`, ...). A builtin writing a small string completes into the buffer before the reader exits. ⚠ Becomes Regime A if the variable ever exceeds 64 KB.
- **REAL RISK — external upstream, unbounded output:** `build_spitbol_archive.sh:47,106` — `nm "$OUT" | grep -q spitbol_main`. `nm` over a linked object easily exceeds 64 KB ⇒ Regime A ⇒ **`spitbol_main` present would read as absent**. Not this goal's file; flagged for its owner, not silently edited.

⇒ **LAW (minted): `cmd | grep -q` under `pipefail` is a defect whenever the upstream is external and its output may exceed the pipe buffer; `grep -c` + a count test is the portable form. `grep -q FILE` (no pipe) is always fine.** The discriminator is the upstream, not the `-q`.

---

## 3. RAIL INSTRUMENT — ASLR DEFAULT (`405009cd`)

RC-0(a)'s exit criterion is written *"…at N=12 with `ASLR=off` (`setarch -R`)"*, but `bench_min_of_n.sh` defaulted to `ASLR=on` — **its default run was not the configuration its own acceptance test is defined on.** Flipped to `off`.

The rationale is mechanical: min-of-N is justified by the min being a stable *floor*, but that holds only **within one address layout**. Across layout draws the min statistic itself moves, so an unpinned min-of-N is not the quantity the rationale describes.

Second edit is the load-bearing one. **`setarch` is now CAPABILITY-PROBED, not assumed** — present *and* `setarch -R /bin/true` actually succeeds — because it can be absent or have its personality syscall blocked by seccomp in a container. A silently-ignored `setarch -R` prints rows labelled `ASLR=off` while measuring `ASLR=on`: a **mislabelled number**, the one thing this instrument exists to prevent. It now degrades loudly and relabels the arm `on(forced)`.

Verified here: `setarch` present, `-R` succeeds, and it genuinely pins — stack base identical across 3 runs vs randomized without it.

### 3.1 ⛔ MEASURED — "PINNING REDUCES SPREAD" IS FALSIFIED, AND MY OWN FIRST MEASUREMENT MISLED ME (`de2f9920`)

The build completed late in the session, so this *was* measured. s10 claimed pinning cuts spread 12.7% → 3.1%. **It does not, on this box.**

**INTERLEAVED** (arms alternated run-by-run so drift is shared, not confounded), fibonacci, unchanged binary, N=12:

| arm | series | min | max | max/min |
|---|---|---|---|---|
| `ASLR=on` | 446 446 440 439 427 441 443 459 444 449 450 451 | 427 | 459 | **1.075** |
| `ASLR=off` | 451 473 458 448 476 476 486 473 467 474 473 472 | 448 | 486 | **1.085** |

Spreads are indistinguishable at N=12 (7.5% vs 8.5%), and `ASLR=off` is consistently **~5% slower in absolute terms**. ⇒ **Pinning does not remove layout variance; it converts it into a fixed unknown BIAS.** A single pinned layout is ONE sample from the layout distribution and can be systematically unlucky — this box drew a slow one.

⭐ **METHOD, and my own error caught in-session:** a first **SEQUENTIAL** measurement (all `on`, then all `off`) suggested pinning was *twice* as bad. Its `off` series ended `…476 458 468 456 | 441 443 442` — a downward step, i.e. **drift fully confounded with the arm**, because the arms ran in blocks. On a 1-core box, arm-ordered runs are a design error. **INTERLEAVE, OR DO NOT COMPARE.** I nearly filed the sequential number.

⛔ **RC-0(a)'s EXIT CRITERION IS NOT MET IN THIS CONTAINER.** It requires `max/min ≤ 1.05×` at N=12 with `ASLR=off`; this box gives **1.085× pinned, 1.075× unpinned**. ⇒ **No ratio below ~1.09× is trustworthy here** — independent corroboration of `RATIO_FLOOR=1.10`, and a hard bound on every RC-5/RC-6/RC-7 rail claim made on this box. **The rail is not yet an accepted instrument here**, which retroactively supports s9/s10's conclusion that the RC-5 numbers (1.036×/1.028×) were void — they sat far below this floor.

The default stays `off`: RC-0(a) is *written* at `ASLR=off`, and for an A/B **ratio** a shared fixed layout removes layout as a variable that *differs between arms*, even though it does not shrink within-arm spread.

---

## 4. RC-6 — DO NOT OPEN IT ON THE INHERITED RANK

s6/s8/s10 all recommend opening RC-6 on `rt_call_arr`, "99 emitted sites, top of the s6 hotness rank." **That is a STATIC call-site count.** This repo has convicted static call-site ranking three times:

- `FINDING-2026-07-29-CLAUDE-ICN-RTX-0D-STATIC-RANK-IS-WRONG-AND-THE-TOP-THREE-ARE-COLD`: *"the hottest unported C symbol sits at static rank 20"* — and it beat **`rt_call_arr`'s** 1,822 by **8.7×**. `rt_call_arr` is named in the very finding that falsifies ranking by static count.
- `FINDING-2026-07-30-...-RTX-8-SLICE7-STATIC-CALL-SITE-RANKING-IS-ANTI-CORRELATED-WITH-HOTNESS`: *"the ladder's own next-rung list was aimed at three dynamically dead symbols"*, and the reason is **STRUCTURAL, not workload-specific** — a hot symbol sits in a loop body, so the emitter needs exactly ONE call site for millions of entries, while a cold setup symbol needs many. Static count therefore measures roughly the *inverse* of loopiness.
- `FINDING-2026-07-30-...-RTX-4-SLICE3A-...-STATIC-RANK-IS-ANTI-CORRELATED` (third occurrence).

An independent static census this session (65 benchmark `.s`, all languages) also **does not reproduce the inherited ordering**: `rt_arg_stage` 1031 · `rt_call_arr` 760 · `rt_pl_dop_mkc` 655 · `rt_pl_dop_unify` 495 · `rt_proc_call_epilogue_` 468. Even taken on its own terms the inherited rank is stale — `rt_call_arr` is not first.

⇒ **RC-6 must open on a DYNAMIC census.** Its charter already says so ("ordered purely by measured hotness"); the recommendation drifted to static because static is cheap. Per SLICE7: *a census is not evidence until it covers the artifact's whole unported call set* — partial censuses do not read as partial, they read as a finished answer with a clean shape.

### 4.1 RESOLVED — THE INSTRUMENT WAS BUILT, AND IT NEARLY GAVE THE INVERSE ANSWER (`5962917e`)

`valgrind`/`perf`/`ltrace` are all absent, so `profile_callgrind.sh` cannot run. Built one instead: `scripts/util_rtcc_crossing_audit.c`, an **`LD_AUDIT`** library counting `rt_*` calls per symbol with **zero signature knowledge** — which is what makes a whole-call-set census tractable where `util_rtx_icn_0d_census.c` (one hand-written signature per symbol) does not scale.

⛔ **IT CARRIES A TRAP THAT INVERTS ITS ANSWER, AND I WALKED INTO IT BEFORE CATCHING IT.** `la_pltenter` sees only **PLT-routed** calls. Mode-3 runs generated code from an **RX slab with no PLT**, not a link_map object — so generated→C crossings are **invisible**, and what you measure is intra-C traffic inside `libscrip_rt.so`: the *complement* of the wanted quantity. Measured in mode-3:

| symbol | emitted call sites | mode-3 audit |
|---|---|---|
| `rt_call_arr` | 4 | **0** |
| `rt_arg_stage` | 5 | **0** |
| `rt_chain_enter` | **0** | 2,692,537 |
| `rt_gc_point` | **0** | 2,692,537 |

An exact **inverse** correlation. Filing that as hotness would have aimed RC-6 at symbols generated code never calls — **vacuous by construction**, the failure shape this ladder has hit repeatedly. What saved it was the numbers being *too clean*: five straight zeros is a property of the instrument, not of the program.

**Fix:** run on a **mode-4** binary, where the emitted `.s` links into a real ELF and `call rt_foo` goes through the PLT (verified: 4 `rt_call_arr@plt` sites). Arm-match is mandatory — a mode-4 binary emitted under `RTCC=1` and run under `RTCC=0` **SIGSEGVs**, independently reproducing s9's probe (templates-ON + runtime-OFF ⇒ `r9=0`).

### 4.2 TRUE CROSSING COUNTS (mode-4, arm-matched, exact — not sampled)

- **fibonacci:** `rt_gc_point_arr` 2,692,543 · `rt_arg_stage` / `rt_proc_get_fn` / `rt_proc_open_fn` / `rt_goto_transfer` / `rt_flat_wire_adopt` / `rt_sub` 2,692,537 each · `rt_add` 1,346,268 · **`rt_call_arr` = 4**
- **roman:** `rt_defer_open` / `rt_defer_get_pat_fn` / `rt_defer_close` 2,200,022 each · `rt_sxt_break` 400,022 · **`rt_call_arr` = 100,005**

⭐ **(1) Static rank is anti-correlated — fourth confirmation, sharpest numbers yet.** `rt_arg_stage` and `rt_call_arr` sit **1.36×** apart statically (1031 vs 760 sites) and **673,000×** apart dynamically on fibonacci. The inherited RC-6 target executes **four times**.

⭐ **(2) THERE IS NO SINGLE HOTNESS RANK — THE HOT SET IS WORKLOAD-DEPENDENT.** fibonacci is the procedure-call path (`rt_arg_stage`, `rt_proc_*`, `rt_flat_*`); roman is the deferred-eval pattern path (`rt_defer_*`). They share almost nothing, and `rt_call_arr` moves **4 → 100,005** between them. **RC-6 must be ordered against a STATED workload mix, or per-family against the workload that exercises that family.** A single benchmark's rank is exactly the "partial census reads as a finished answer" shape SLICE7 convicted — and this time the partial answer would have been off by five orders of magnitude.

---

## 5. WHAT THIS SESSION DID **NOT** PROVE

Discipline note, because the failure mode above is precisely inherited claims outrunning their evidence:

- ✅ **RESOLVED LATE IN SESSION — the watermark WAS re-proved.** The `-O0` build finished (1-core, `nproc=1`; a first attempt was killed when a tool timeout took its process group, hence the detached relaunch). **`fibonacci` m3 `result: 832040` at BOTH `SCRIP_RTCC=0` and `SCRIP_RTCC=1`; claim-gate `--strict` PASS at open and close; tree clean; killswitch arms differ as expected (RTCC=1 emits the veneer).**
- **No SPEED claim is made.** §3.1 reports only the *noise band of an unchanged binary* — an instrument-characterisation number, not an A/B result. No RTCC arm was graded for performance this session, and on the §3.1 numbers this box cannot grade one below ~1.09×.
- **RC-6 was NOT opened, but it is now openable.** §4 falsifies the inherited target and lands the instrument. What remains before opening: agree the STATED workload mix (§4.2 shows a single benchmark misranks by 10^5), and confirm the mode-4 ranking transfers to mode-3 — the two modes are chartered 1:1, but that is an assumption this session did not test, and mode-3 is where the veneer actually runs.
- The five duplicated RTCC constants in `x86_asm.h` were **not touched** (NOT-CONCURRENCY-SAFE; needs Lon's routed window). A one-sided guard remains strictly worse than none.

---

## 6. LAWS MINTED / STRENGTHENED

- **`cmd | grep -q` UNDER `pipefail` IS A DEFECT WHEN THE UPSTREAM IS EXTERNAL** (§2.4). Two regimes: deterministic loss above the 64 KiB pipe buffer, scheduling race below it. Portable form is `grep -c` + count test. `grep -q FILE` (no pipe) is always safe. **The discriminator is the upstream, not the `-q`.**
- **CONTENT, NOT HASH, IS THE TEST FOR "DID IT LAND"** (§1). Rebase at handoff rewrites hashes, so an absent hash is not absent work — and, more dangerously, a *present* hash in a cursor is not present work. Verify by grepping for the artifact.
- **A PUSHED FINDING IS NOT A PUSHED FIX** (§1). The repos are pushed separately and can diverge; `.github` landing while SCRIP does not is a silent, self-concealing failure, because the next session orients off the FINDING and inherits a tree state that never existed. `handoff_status.sh` covers *every* repo for this reason.
- **PROBE THE CAPABILITY, DON'T ASSUME THE TOOL** (§3). A silently-ignored `setarch -R` yields a mislabelled measurement, which is worse than a refused one.
- **INTERLEAVE, OR DO NOT COMPARE** (§3.1). Two arms measured in BLOCKS confound the arm with thermal/scheduler drift, and on this 1-core box that confound was large enough to *invert* the conclusion — the sequential run said pinning was 2× worse, the interleaved run said the arms are indistinguishable. Any two-arm comparison alternates run-by-run. This applies to every A/B on the rail, not just ASLR.
- **PINNING CONVERTS VARIANCE INTO BIAS; IT DOES NOT REMOVE IT** (§3.1). `setarch -R` gives one layout, not the average layout, and a single layout can be systematically unlucky (~5% slow here). Pinning is justified for *ratios* (shared layout cancels between arms), NOT as a spread reduction — the spread-reduction claim is falsified.
- **AN INSTRUMENT THAT FAILS ITS OWN EXIT CRITERION CANNOT GRADE A RUNG** (§3.1). RC-0(a) demands ≤1.05× on an unchanged binary; this box gives 1.075–1.085×. Every rung graded on this rail below ~1.09× is ungraded, whatever number it printed.
- **A STATIC CALL-SITE RANK IS NOT A HOTNESS RANK — FOURTH OCCURRENCE** (§4). The mechanism is structural: hot code is loop-resident and needs one site; cold setup code needs many. Any rung ordered "by hotness" whose evidence is a `grep -c` over `.s` files is aimed by the inverse of the quantity it names.

---

## 7. NEXT (recommended)

1. **Re-prove the watermark at open** (this session could not). Then decide whether s9/s10's lost work is worth re-deriving — §2 re-derives the load-bearing half of it; CHECK 2/CHECK 3 remain lost and would need re-deriving from the s9 FINDING's prose.
2. **Ask Lon to route the `x86_asm.h` window** for the five-constant guard in ONE commit (unchanged from s9/s10). Better end state remains: delete the `x86_asm.h` copies, include `rtcc.h`.
3. **Do not open RC-6 until a dynamic instrument exists.** Settle the `LD_AUDIT` question (§4.1) or provision `valgrind` in the container; either is a prerequisite, not a nicety.
4. Re-measure the noise band on a **quiet, multi-core** box. The 1-core environment warning in the cursor (intra-arm spreads to 275%) is still the governing constraint on every RTCC rail claim, and it is why RC-7's fold decision cannot be made here.
