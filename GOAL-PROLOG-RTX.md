# GOAL-PROLOG-RTX.md — The Prolog Runtime in Optimized x86-64 Assembly

**Minted s221-PL (2026-07-30) on Lon's directive:** *"Notice how GOAL-SNOBOL4-RTX and GOAL-ICON-RTX are
proceding with replacing the C runtime with highly optimized register-aware ASM code. You do the same.
Join the coordination that is setup by the two, and y'all will be come three."*

**Ladder name:** `PL-RTX` — the **third** RTX ladder, running CONCURRENTLY with `GOAL-SNOBOL4-RTX.md`
(`SN4-RTX`), `GOAL-ICON-RTX.md` (`ICON-RTX`), and `GOAL-PROLOG-BB.md` (the ζ / PL-SINK ladder).

**Contract:** `ARCH-PROLOG-RTX.md` — read it before any rung. It does NOT restate step 0; it points at
`ARCH-SNOBOL4-RTX.md` §7, which is the shared checklist, and records only Prolog's deltas.

---

## ⛔⛔ SYMBOL OWNERSHIP IS NOT IN THIS FILE — IT IS IN `RTX-CLAIMS.md`

The runtime is SHARED (~20,000 lines, one `.so`, six languages). **Three** RTX ladders now work it.
Check a symbol OUT in that ledger — **and PUSH the claim before the work, not with it** — before writing
code. Run `CUR_SESSION=<n> bash scripts/util_rtx_claims.sh` at session start and session close.

⭐ **Prolog's advantage: its hot surface is almost entirely Prolog-EXCLUSIVE** (`rt_pl_dop_*`), so this
ladder can run for many sessions with **no arbitration against SN4-RTX or ICON-RTX at all.**
⛔ **Prolog's disadvantage, and it is the whole scope problem: its hot surface COLLIDES with its own BB
ladder's PL-SINK rungs.** See §SCOPE below. That collision, not inter-RTX contention, is this ladder's
governing constraint.

---

## ⛔ LIVE CURSOR — s223-PL (2026-07-30): **⭐⭐ RTX-1-PL LANDED. THE ASM EXECUTES IN BOTH MODES AND BAILS TO C ZERO TIMES. THE PERF ANSWER IS A NULL — AND THE REASON IS THAT ALL THREE SHARED RTX INSTRUMENTS FAIL ON PROLOG, SO THE CLAIM IS UNFALSIFIABLE, NOT DISPROVEN.**

SCRIP `b1ca896e` + this session. RT_OPT=`-O0`.
FINDING: `FINDING-2026-07-30-CLAUDE-PL-RTX-1-LANDED-GREEN-AND-VACUOUS-BY-VOLUME-AND-ALL-THREE-SHARED-RTX-INSTRUMENTS-FAIL-ON-PROLOG.md`

⛔⛔ **SAME-SESSION CORRECTION (supersedes items 6 and 7 below — newest at top):**
**(a) THE ARM CENSUS WAS NEVER BROKEN.** `chat_parser`/`boyer`/`browse`/`crypt`/`derive` exit **rc=134 with NO `LD_PRELOAD` at all** — `[IBB] FATAL: mode-3 driver: main BB graph not found`, **5 of 5 van Roy programs.** The census's own message *"check that the program runs at all"* was exactly right; I promoted a true report about the PROGRAM into a false accusation against the TOOL, for want of one command. **Item 7(c) is STRUCK; 7(a) and 7(b) stand.**
**(b) ITEM 6's PERF TABLE IS VOID — IT TIMED A CRASHING PROGRAM**, i.e. ~100% compile phase, so all three arms agreed to 1% by construction. ⭐⭐ **This is the ICON-RTX s220 compile-phase confound, on the exact family `ARCH-PROLOG-RTX.md` §2 warns is NOT covered by the `dop` zero-floor result** (*"Non-`dop` targets (`rt_proc_*`…) are not covered — re-measure per family"*) — **I wrote that caveat at s221 and walked into it at s223.** ⛔ And I shipped it INSIDE a correction of the cold-cache artifact: **fixing one confound is not evidence the number is clean.** ⇒ **verify rc==0 AND that the workload reaches the symbol BEFORE timing.**
**(c) ⭐⭐ THE REAL NUMBER — RTX-1-PL IS A WIN, NOT A NULL.** On `corpus/programs/prolog/rung10_programs_puzzle_19.pl` (rc=0, ~2.5 s): census **ENTRIES 13,850,337 / BAILED_C 0 / COMMITS 13,850,337** (≈1000× `queens.pl`); warmed interleaved 5 rounds, medians, `-O0`: PRISTINE **2557** · OFF **2536** · ON **2424** ⇒ **ON/PRISTINE ≈ 1.055×**, gate tax **1.008× ≈ nil**, ON fastest in **5/5 rounds**. ⚠ Under the ~1.10× trust floor, so it rests on four weak agreements not one strong claim: three arms, 5/5 direction, ~0 tax, and an arithmetic bracket (~10 instr × 13.85 M ≈ 139 M instr ≈ 2–4% of a 2.5 s `-O0` run). **"VACUOUS-BY-VOLUME" is WITHDRAWN.**
**(d) ⛔⛔ THE FINDING THAT OUTLIVES THE RUNG: THE VAN ROY CORPUS THIS LADDER'S WHOLE RANKING RESTS ON DOES NOT EXECUTE IN MODE 3.** s221 reports 2,060,043 arrivals across 19/22 of those programs, yet every RTX rung is graded through `--run` — **the ranking and the grading instrument are not in the same mode.** That is a defect one level above any rung and it is now item 0.

1. ⭐⭐ **RTX-1-PL IS ASSEMBLY.** `src/runtime/rtx/rtx_plcall.S`, family gate `PLCALL`, C body → `c_rt_proc_call_open_det`. **Three of four C levels absorbed ⇒ the success path has NO CALL:** `prologue_lex`'s `fbytes` is discarded by every caller on this path so its computation is ELIDED entirely; `rt_pcall_grow` inlined as a capacity compare with a cold out-of-line arm (hot path frameless); `rt_value_trail_mark` inlined as one load. `rt_pcall_grow` de-static'd → `visibility("hidden")` (the s187 `rt_nret_fix` precedent). Linkage split read from `rt.o`, never the `.so` (s209): 7 hidden globals rip-direct, 4 exported via `@GOTPCREL`. Every baked offset anchored by `_Static_assert` in the owning TU ⇒ **a struct move breaks the COMPILE, not the runtime.**
2. **GATES ALL GREEN.** Prolog watermark **164/164 interp + 164/164 compile at PRISTINE *and* at ON**. SNOBOL4 **7/0**, Icon **14/14 m3 + 14/14 m4** (cited as no-regression for the C-side de-static ONLY). Arm census `queens.pl`: ENTRIES **12,957** / BAILED_C **0** / COMMITS **12,957**.
3. ⭐⭐ **THE FALSIFICATION PROBE IS THE EVIDENCE, NOT THE GREENNESS** (§7 step 2b). Deliberately broken asm moves the Prolog battery **164/0 → 111/53 in BOTH modes** ⇒ the asm executes, coverage is **53/164 = 32 percent**, and **m4 is real evidence** — the s214 "never close on m3 alone" trap is discharged by measurement rather than assumed.
4. ⭐⭐ **s221 ITEM 8 / PROPOSED RTX-13-PL IS SETTLED AND WAS MISCONCEIVED.** `_det0…_det4` measure zero **not** because a `det_fuse` conjunct fails but because the hot sites **never evaluate `det_fuse` at all**: `bcps_spine_gen_arm` — whose own in-tree comment says every nondet Prolog predicate is dispatched there — has **no fused family and no fuse test**, only `gi_idx >= 0 ? rt_proc_call_open_det : rt_proc_call_open`. ⇒ the arity, `"$call/N"`-name and frame-regime hypotheses all have no referent. ⭐ **And it RAISES this rung: the generator arm calls the ported symbol directly BY INDEX, so RTX-1-PL is the live hot arm and cannot be mooted by any det-arm eligibility fix.** The real successor rung is "extend the fused family to the generator arm."
5. ⛔⛔ **I NEARLY REPORTED 3.4×.** `queens.pl` first read PRISTINE 204 ms → ON 60 ms. That was **entirely cold page-cache on whichever arm ran first.** Warmed and interleaved, the same program reads 53 / 51 / 52 ms. **Nothing but re-measuring caught it.** ⇒ never report a number from a non-interleaved loop; this is why the contract mandates the harness.
6. **THE HONEST NUMBER** (`chat_parser.pl` ~576 ms, 7 warmed interleaved rounds, medians, `RT_OPT=-O0`): PRISTINE **576** · OFF **583** · ON **569** ⇒ **ON/PRISTINE 1.01× = NULL**; kill-switch tax **0.99× ≈ 0**, so the port is **FREE TO KEEP**. Census reports only **12,957** arrivals on the `queens.pl` it can grade vs the board's **430,081** — a **33× disagreement**, most likely two different files both named `queens`. At ~13 k arrivals × ~10 instructions saved the port is invisible **by construction**.
7. ⛔⛔ **THE REAL BLOCKER — ALL THREE SHARED RTX INSTRUMENTS FAIL ON PROLOG, THREE DIFFERENT WAYS.** (a) `test_gate_rtx_killswitch_sets.sh` was hardcoded `*.sno` ⇒ **no Prolog and no Icon arm at all** — ✅ FIXED, added an `EXT` parameter (default `sno`, every existing invocation byte-unmoved); ⚠ the Prolog sweep was launched and **NOT COMPLETED**, still owed. (b) `bench_rtx_3arm.sh` requires a self-timed `ms:` window and **no Prolog program emits one** ⇒ it prints `NOT GRADED` for every program; item 6's table is hand-rolled wall clock and is labelled as such rather than dressed up as the harness's output. (c) `util_rtx_arm_census.sh` **SIGABRTs (rc=134) under `LD_PRELOAD` on the van Roy corpus** (`chat_parser`, `boyer` — 2 of 2 tried; it works on `corpus/programs/prolog/queens.pl`) ⇒ **the census cannot grade the corpus the s221 ranking was built from**, so the 2,060,043 board figure is single-instrument and item 6's 33× gap is unresolvable until this is fixed. ⇒ **RTX-1-PL's PERF claim is UNFALSIFIABLE; its CORRECTNESS claim is fully discharged. ⛔ Do NOT read the null as "the port does not help" — read it as "this tree cannot yet measure whether it helps."**

**WATERMARK:** SCRIP local commit (6 files) / corpus `<none>` / `.github` FINDING + this file + `RTX-CLAIMS.md` — **PUSH BLOCKED, credential needed.**

**NEXT:** ⭐ **(0) Establish which mode the s221 van Roy ranking was measured in — those 22 programs ABORT under `--run`, so the ranking and the grading instrument are not in the same mode. Re-rank on programs that execute if the counts do not transfer; `rung10_programs_puzzle_19.pl` is the first known-good member.** Then (1) complete `test_gate_rtx_killswitch_sets.sh PLCALL <prolog corpus> 4 both pl`; (2) name the exact file behind each of 12,957 and 430,081; (3) give `bench_rtx_3arm.sh` a Prolog timing arm (or self-time the Prolog benchmarks); (4) then rule on whether RTX-1-PL stays — note it is FREE to keep at a 0.99× tax; (5) the §SCOPE ruling is still open and still not blocking.

**BANKED (inherited from `GOAL-PROLOG-BB.md`, all still live):** `unary_not.sno` emits a `.string` from
uninitialised memory (poisons every `.s` byte-identity sweep); engine-wide silent-fail on undefined
predicates; int/float standard-order conflation; lexer escape three-site/two-behaviour; NO-LCO segfault;
nested-`\+` binding leak; `retractall/1` gaps.

---

## ⛔⛔ SCOPE — THE RULING THIS LADDER NEEDS FROM LON

Nine of the top eleven Prolog symbols are already-SINK'd or claimed by an **OPEN** PL-SINK rung in
`GOAL-PROLOG-BB.md`, which is a **concurrently running session**:

| RTX rank | symbol | corpus calls | reach | PL-SINK rung | SINK status | PL-RTX |
|---:|---|---:|---|---|---|---|
| 1 | `rt_pl_dop_trail_unwind` | 2,114,931 | 10/22 | **SINK-9** | ⏳ OPEN | ⛔ COLLISION |
| 2 | `rt_proc_call_open_det` | 2,060,043 | **19/22** | **none** | — | ✅ **CLEAR** |
| 3 | `rt_pl_dop_unify` | 1,108,786 | **22/22** | SINK-1 | ✅ s142 | ⚠ reduced |
| 4 | `rt_pl_dop_mkc` | 1,018,100 | 19/22 | SINK-3 | ✅ s145 | ⚠ reduced |
| 5 | `rt_pl_dop_cmp_ne` | 880,792 | 5/22 | **SINK-7** | ⏳ OPEN | ⛔ COLLISION |
| 6 | `rt_pl_dop_unwind_nothrow` | 873,060 | 16/22 | **SINK-9** | ⏳ OPEN | ⛔ COLLISION |
| 7 | `rt_pl_dop_is_v` | 735,898 | 14/22 | **SINK-5** | ⏳ OPEN | ⛔ COLLISION |
| 8 | `rt_pl_dop_ax_sub` | 731,498 | 12/22 | **SINK-6** | ⏳ OPEN | ⛔ COLLISION |
| 9 | `rt_pl_dop_unify_cs` | 622,812 | 12/22 | SINK-1 fam | ✅ | ⚠ reduced |
| 10 | `rt_pl_dop_ax_add` | 573,678 | 6/22 | **SINK-6** | ⏳ OPEN | ⛔ COLLISION |
| 11 | `rt_pl_dop_ix_g` | 289,004 | 15/22 | SINK-4 | ✅ s148, **kk==4 deferred** | ✅ deferred arm CLEAR |
| — | `rt_pl_dop_trail_mark` | **22** | 22/22 | SINK-8 | ✅ s146 | ⛔ **VESTIGIAL** |

**THE QUESTION.** When a Prolog symbol is hot and has an open SINK rung, does it get
**(a)** SINK (emitter inline fast path), **(b)** RTX (runtime body in asm), or
**(c)** SINK for the guarded fast arm **+ RTX for the arm SINK deliberately defers to C**?

⭐ **RECOMMENDED: (c)** — the only option under which both ladders keep working. SINK's inline path takes
the arrivals it guards, so **RTX's honest scope is the residue SINK refuses**, which is already
enumerated in `GOAL-PROLOG-BB.md`: SINK-4's `kk==4` per-site intern cache, SINK-7's out-of-2⁵³ range
arm, SINK-6's `div`/`idiv`/`mod` guard arms (`b==0`, `b==−1`) and any `DT_R`, SINK-5's non-`{I,R}` tags —
**plus every symbol with no SINK rung at all**, which is where rung 1 lives.
Under (a) this ladder has ~2 live rungs. Under (b) two concurrent sessions fight over one
emitter/runtime boundary per symbol, and per RULES.md concurrency that is safe for FILES and **not** safe
for a shared performance claim.

⛔ **UNTIL RULED: this ladder works ONLY symbols with no SINK rung, or SINK-deferred arms.** Rung 1
satisfies both.

---

## THE LADDER

### - [x] ✅ RUNG RTX-1-PL — `rt_proc_call_open_det` — **LANDED s223-PL. Green both modes, 12,957 commits / 0 bails, **~1.055× measured on 13.85 M arrivals / 0 bails** (see the SAME-SESSION CORRECTION atop the cursor; items 6-7 are superseded).**
**WHY IT IS FIRST, AND IT IS FIRST UNDER EVERY SCOPE OPTION:** rank **2** by execution (2,060,043),
rank **1 by REACH (19/22 programs — the broadest of any Prolog symbol)**, **no PL-SINK rung**, **not a
`dop`** so structurally outside SINK's `$op` territory, **Prolog-dominant** (5,291 static sites),
**absent from `RTX-CLAIMS.md` entirely**, and in the CALL family where SN4-RTX has already paid for the
lessons (`rt_proc_call_epilogue_γ/ω` are `DONE:SN4-RTX:881ea03d`).
⭐ **Its sibling `rt_proc_call_open` measures ZERO calls in 22/22 programs** despite 5,626 static sites —
**the `_det` variant takes the entire path, and only the dynamic sweep could show that.**

**STEP 0 STATUS — PARTIALLY DONE s221; THE REST IS OWED BEFORE ANY ASM:**
- [x] **0(a) live definition exists** — exported `T` in `out/libscrip_rt.so`.
- [x] **0(b) spelling round-trips** — taken from `nm -D --defined-only`, not from prose. ⚠ Note the
  neighbouring `rt_proc_call_epilogue_γ/ω` carry literal UTF-8 GREEK; **this symbol does not**, but any
  new sibling in the family must be taken as the tree spells it (RTX-4 s165 truncation class).
- [x] **0(d) executed + scales** — 13,226 → 52,901 at nrev N=25→100 (**4.00× exact**); 2,060,043
  corpus-wide across 19/22 programs. ⚠ **ZERO on `fib`** — per cursor item 5, that is a statement about
  `fib`, not about the symbol.
- [x] **0(e) not already assembly** — grep run **with `--include=*.S`** (the load-bearing flag, s200).
- [x] ✅ **0(c) DONE — AND IT FIRED. SLICE 0 LANDED (SCRIP `1f91a433`).** `nm out/rt_pic/rt.o` showed **three of the five things the port needs were `static` and unreferenceable from `.S`**: `g_rt_gen_procs` `b`, `g_rt_gen_proc_count` `b`, `g_pcall_cap` `b` — plus TWO `static` FUNCTIONS, `rt_proc_call_prologue_lex` `t` and `rt_pcall_grow` `t`. **The `.so` reported all of them fine**, exactly as s209 said it structurally must. Promoted the three globals to `visibility("hidden")` after checking **s214 axis 2 first** (zero template/emitter refs ⇒ not named in emitted mode-4 TEXT ⇒ `hidden` is safe); verified **absent from the dynamic table** after ⇒ direct `[rip+sym]`. Now all nine cluster globals are `B`/`D`. Gates: **Prolog 164/164 + 164/164 · SNOBOL4 7/0 · Icon 14/14 m3 + 14/14 m4**, all green, visibility-only change.
- [x] ✅ **0(f-pre) DONE — NOT straight-line, so 0(f) is NOT discharged in advance.** All six family members share one shape: two decline guards (`idx` range; `!p->fn || p->dyn_scope`) → optional `g_call_args` copies → **a call to `rt_proc_call_prologue_lex`** → `return p->fn`. ⭐ **COST DECOMPOSITION, and it is FAVOURABLE — the opposite of the RTX-4/`rt_make_list` shape:** the callee chain bottoms out in cheap, inlinable work. `rt_proc_call_prologue_lex` is ~12 stores + 2 increments + `fbytes` arithmetic **whose result every caller DISCARDS via `(void)`** ⇒ dead work on this path. Its one call, `rt_pcall_grow`, is **`if (g_pcall_top < g_pcall_cap) return;`** — a capacity guard whose common case returns immediately ⇒ the ideal inline-with-bail arm. Its other call, `rt_value_trail_mark`, is **`{ return g_pl_trail.top; }`** — one global load. ⇒ **the entire cluster can be absorbed with NO call remaining in the success path.** Absorbing a `static` callee into a gated wrapper's asm is precedented TWICE (s211 `rt_parse_num_d`, s216 `data_field_ptr`) and needs no contract amendment.
- [x] ✅ **0(g) DONE — THE LIVE ARM IS THE GENERIC FORM, AND THE "OPTIMIZED" ARMS ARE DEAD.** `bb_call_proc_staged.cpp` emits a THREE-TIER ladder: (1) **PL-DC** direct `call proc_X_dcα` (no open crossing at all, gated `rt_pl_dc_ok`), (2) **fused `rt_proc_call_open_detN`** (≤4 args, `ZC_FRAME_RSP`), (3) **classic generic `rt_proc_call_open_det`**. ⭐⭐ **MEASURED on `queens.pl`: generic `_det` = 430,081 · `_det0`…`_det4` = ZERO, all five.** ⇒ **porting the generic form ports the live arm.** ⛔ **AND THE WHOLE PL-REGAIN-4 FUSED FAMILY IS DEAD ON THE HOTTEST PROLOG PROGRAM** — it exists to collapse `{rt_arg_stage × nargs + open_det}` into one crossing, and `rt_arg_stage` independently measures **8 calls across 22 programs**. Since `dc` requires `det_fuse`, **PL-DC is dead here too.** ⇒ **an entire shipped two-rung optimization pair is bypassed on the hot path, and only the dynamic sweep could show it.** ⚠ **OWED: WHY `det_fuse` is false for Prolog's hot sites** (`det_idx < 0` / frame regime / `nargs > 4`) — Prolog carries 5,291 static `_det` sites, so if the fused arm can be made to fire that may outrank the asm port entirely. **Measure before porting: this is a possible RTX-13-PL (fix the eligibility) that would beat RTX-1-PL.**
- [ ] ⛔ **REMAINING 0(c) for the port itself:** `rt.o`, not
  `libscrip_rt.so`: `B`/`D` = linkable, `b`/`d` = `static` and **unreferenceable from `.S`** (s209 —
  the `.so` is structurally incapable of separating `static` from `visibility("hidden")`).
  ⛔ **AND s214's second axis:** if any such global is ALSO named by a template in emitted mode-4 TEXT it
  must stay **DYNAMICALLY EXPORTED**, and then every `.so`-internal access must become `@GOTPCREL` or a
  `-no-pie` copy relocation silently makes it a DIFFERENT VARIABLE.
- [ ] ⛔ **0(f-pre) READ THE C BODY AND ENUMERATE ITS ARMS.** If it is straight-line (no arm, no call, no
  early return) then entries==commits by construction and 0(f) is discharged before the asm exists
  (s217). Otherwise the ported arm's liveness must be established.
- [ ] ⛔ **0(g) READ THE EMITTING TEMPLATE FIRST (s211-ICN, and Prolog is the language where this bites
  hardest).** Grep the `bb_*.cpp` that emits the call for an inline `cmp`/`je` tag guard. **PL-SINK is
  an entire ladder of exactly such guards** — cursor item 1 is what happens when one lands. If a guard
  steers arrivals away from the arm I intend to port, **port the arm the guard REJECTS**, or refuse.
- [ ] Then, and only then: port behind gate `SCRIP_RTX_PLCALL`, C body → `c_rt_proc_call_open_det`.

**GATES OWED AT LANDING:** Prolog `test_prolog_rung_suite.sh` **164/164 + 164/164** (the watermark
established this session) · SNOBOL4 + Icon batteries as **no-regression only** (⛔ per
`ARCH-SNOBOL4-RTX.md` §7 step 2b, **an unmoved battery may NOT be cited as evidence the asm executes**) ·
`util_rtx_arm_census.sh` with `COMMITS > 0` · `test_gate_rtx_killswitch_sets.sh PLCALL` (N≥4 per arm,
hash SETS — the s217/s219 correction) · 3-arm `bench_rtx_3arm.sh` reporting **ON/PRISTINE** as the answer.

### - [ ] RUNG RTX-2-PL — the SINK-deferred arms (scope option (c) only)
Enumerated residue the SINK ladder explicitly leaves in C: SINK-4 `kk==4` (per-site intern cache),
SINK-7 out-of-2⁵³ range (the double-compare trap — `cvtsi2sd`/`comisd`, and `x86_asm.h` has only ~12 xmm
hits so **verify the encoder forms exist for BOTH media before choosing**), SINK-6 `div`/`idiv`/`mod`
guards (`b==0`, `b==−1` — `INT_MIN/−1` traps on x86) and any `DT_R`, SINK-5 non-`{I,R}` tags.
⛔ **Do not open before the §SCOPE ruling.**

### - [ ] RUNG RTX-0d-PL — extend the workload set beyond two backtracking programs
Cursor item 6: `queensn`+`queens` are ~78% of arrivals. The ranking needs list/arith/IO-shaped run-phase
workloads before any rung is prioritised **on rank alone**. ⚠ Mirrors ICON-RTX's RTX-21-ICN exactly.

### - [ ] RUNG RTX-12-PL — eradication (LAST)
Delete gate + `c_*` body. ⛔ Cross-language per ledger hard rule 4: requires **all three** watermarks
green and every beneficiary row `DONE`.

---

## ARCHITECTURE NOTE — WHY PROLOG'S SURFACE LOOKS DIFFERENT

Prolog's hot symbols are `rt_pl_dop_*`: the runtime sinks for lowered `$op` nodes emitted by
`lower_prolog.c` through the four-port (α/β/γ/ω, δ/ε) BB machine documented in `GOAL-PROLOG-BB.md`.
They are **emitted-code-only** — the compile phase never calls them (cursor item 4) — which is why
Prolog's absolute dynamic counts are already run-phase counts and why its surface is the largest of the
three languages (**112 distinct symbols** vs Icon's 90 and SNOBOL4's 54) while being almost entirely
uncontested.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
