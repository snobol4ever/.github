# GOAL-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29).** Contract: **`ARCH-ICON-RTX.md`** — read before any rung. Runs concurrently with `GOAL-ICON-BB.md` and `GOAL-SNOBOL4-RTX.md`; three-way ownership in `ARCH-ICON-RTX.md` §7.

⛔⛔ **SYMBOL OWNERSHIP IN `RTX-CLAIMS.md`, NOT HERE.** Run `scripts/util_rtx_claims.sh` at session start and close. This ladder is `ICON-RTX`.

---

## ⛔ LIVE CURSOR — s222-ICN (2026-07-30)

**NEXT RUNG: RTX-25-ICN (newly minted, see Queue) or RTX-23-ICN if Lon grants the §7 re-assignment.**

**Watermarks** (re-derived s222 from a fresh clone + full rebuild, never hand-copied): Icon **252/11/30** · SNOBOL4 m4 **324/2**.
⚠ **Prolog watermark NOT obtained this session:** `scripts/test_corpus_prolog_parser.sh` reports **737/737 crash** — and it reports the SAME at gate ON and gate OFF, so the differential is an identity and it is **pre-existing/environmental, not s222's**. The absolute Prolog gate is unavailable until that harness is repaired; use the three-way ON/OFF/PRISTINE differential (the s210 substitute) until then.

**s222 landed RTX-24-ICN — `rt_subscript_var`, gate `SCRIP_RTX_ICNSUB` (fourteenth family gate), 1.376×.**

**s222 key findings:**
1. ⭐⭐ **THE ARM CENSUS IS STRUCTURALLY BLIND TO AN UNPORTED SYMBOL, AND IT REPORTS THAT BLINDNESS AS A ZERO.** `util_rtx_arm_census.sh` splits traffic by counting `sym` vs `c_sym`; an unported symbol has no `c_` half, so it is **omitted entirely** and the tool's own footer reads "symbols with zero entries are omitted: this workload cannot grade them at all." Run on a subscript-saturated window it therefore showed **no `rt_subscript_var` row at all** while the symbol was in fact taking 2,000,000 calls per run. ⇒ **Step 0(d) on an UNPORTED symbol MUST use the LD_PRELOAD interposer; step 0(j) is a POST-port instrument only.** These are two different instruments for two different phases and the ladder has been citing one name for both.
2. ⭐⭐ **PORT THE ARM THE GUARD REJECTS — RTX-6's LESSON, RE-LEARNED THE EXPENSIVE WAY.** The arm was first written to reject VARREF bases, reasoning that a varref is `DT_N` so the `DT_DATA` test excludes it for free. **The live traffic is 100% varref** (measured `base.v=9 base.slen=1`, a frame-slot cell pointer) because `rt_subscript_var`'s own first act is `if (IS_VARREF_fn(base)) base = rt_deref(base)`. First census: **2,000,000 entries / 2,000,000 bailed / 0 COMMITS.** The fix was to call the already-asm `rt_deref` at entry and keep the four original arg registers spilled so every bail still tail-jumps with byte-identical arguments.
3. ⭐⭐⭐ **AN INSTRUMENT THAT EXCEEDS WALL TIME IS NOT AN INSTRUMENT, AND ITS ANSWER WAS CONVENIENT.** An rdtsc self-cost interposer attributed **813,676,867 cycles (~271 ms)** of inclusive time to `rt_subscript_var` inside a program whose entire uninstrumented run is **36 ms**. It yielded a very quotable "SELF = 91.8% of inclusive". It was **DISCARDED, not reported.** The replacement is a wall-clock DIFFERENTIAL — run the window, then run the identical window with the construct deleted and the arithmetic retained — which **cannot** exceed wall time by construction and gave ~90% independently. ⇒ **Add to §8: any cost-share instrument must be bounded by a wall-clock total that is measured in the same session.**
4. ⚠ **AN ALLOCATION-SCALING WINDOW GOES BIMODAL AND MORE ROUNDS CANNOT FIX IT (s211's condition, reconfirmed).** The 8M-iteration window carves 8M × 72 B ≈ 576 MB of VCELLs and its spreads are **OFF 3.44× / ON 1.93×** with 3187 ms and 1770 ms outliers — the `RTX-0C` hugepage-compaction instability. The 2M window is disjoint with spread 1.33×. **Grade the smaller window; a multiplicative spread is not a rounds problem.**
5. ⛔ **`DT_DATA` IS ABSENT FROM `rtx_abi.inc` AND THE OMISSION IS A LIVE TRAP.** The tag list stops at `DT_FAIL 99`. With `DT_DATA` undefined, `cmp edi, DT_DATA` **assembles cleanly** as a relocation against an undefined external symbol; only the memory-operand form is ambiguous enough to be rejected. One line of two was caught by accident. Defined locally in `rtx_icnsub.S` (not in the shared header, to avoid a needless rebase point) and pinned by `_Static_assert`.
6. ⚠ **GNU as Intel syntax parses `k*CONST` inside brackets as index\*scale, not a constant fold.** `[r9 + 0*DESCR_SIZE]` is "index register 0, scale 16" and fails to assemble. Use precomputed literal offsets.
7. ⭐ **THE LEDGER AND THIS FILE DISAGREED ON ALL THREE CONCURRENCY ROWS, AND THE LEDGER WINS.** This file's §Concurrency said SN4-RTX owns `rt_call_arr` · `rt_num_arith` · `rt_subscript_var`; `RTX-CLAIMS.md` — the declared single source of truth — says `rt_call_arr` is **ICON-RTX's by Lon's s208 ruling** and the other two were **RELEASED at s214**. Following this file would have parked a symbol that was ours for eight sessions. Corrected below. (RULES.md s47 class (a): stale prose in a file nobody re-reads.)
8. ⚠ **The s221 benchmark seeds are in `corpus/benchmarks/icon/`, NOT `benchmarks/icon/rtx/`** as RTX-23/RTX-21 state. Corrected below.

⛔⛔ **HANDOFF IS BLOCKED, NOT COMPLETE: NO CREDENTIAL WAS AVAILABLE IN s222.** Every commit below is LOCAL ONLY, on a disposable sandbox. Per RTX-CLAIMS the claim on `rt_subscript_var` was committed **ahead of** the port but **not pushed ahead of it**, so the protective property — another session seeing the claim before spending itself — was **NOT obtained**. The s202 ancestry check (`git rev-list --count origin/main..HEAD == 0`) is **unsatisfiable**. Do not read RTX-24-ICN's `[x]` as landed on origin.

⚠ **Pre-existing ledger rot (not mine, not fixed, reproduced exactly):** `util_rtx_claims.sh` BLOCKED, 3 fatal — `rt_frame` is a phantom (no `.so` definition, no live `@PLT`); `rt_defer_open`/`rt_defer_close` are asm with rows not `DONE` (SN4-RTX's to close).

---

## Queue

### ▶ PHASE 1 — PORTS

- [ ] ⛔ **RTX-23-ICN — `DT_S || DT_I` concat arm. BLOCKED ON LON: needs the §7 re-assignment of `str_concat_d`/`rtx_str.S` from SN4-RTX (row is `DONE:SN4-RTX`).** Premise RE-VERIFIED s222: 2,000,000 entries / 2,000,000 bailed / 0 commits, and `rt_str_alloc` fires 4,000,000 (2×/iteration), confirming the ⅓-dispatch constraint below. `bench_icnstr_concat_int_dispatch.icn` (**`corpus/benchmarks/icon/`** — corrected s222; it is NOT under `benchmarks/icon/rtx/`) isolates the `tag` bail: 2,000,000 / 2,000,000 bailed / **0 commits**. RTX-16 gives the left operand `slen=8`, so DT_I is the sole remaining bail cause. `ON==OFF` today is expected — nothing to grade until the arm exists.
  ⛔ **DESIGN CONSTRAINT (measured s221):** window is only **~⅓ dispatch** — `rt_str_alloc` fires 4,000,000 (2×/iteration) vs 2,000,000 (1×) in `str||str`, because integer coercion allocates. **A tag-only arm captures ~⅓; a formatting arm that produces the integer into the result buffer in asm removes one allocation and captures ~2×+.** State expectation before measuring: tag-only ≈ 1.15×, formatting arm ≈ 2×+. ⚠ 781ms outlier seen in 3 rounds — use more rounds. ⚠ `rtx_str.S` is SN4-RTX's file; needs same §7 re-assignment as RTX-17.
- [ ] **RTX-21-ICN — extend run-phase workload set** (list/set/scan/IO). Two dispatch-dominant seeds landed s221: `bench_icnstr_concat_dispatch.icn` (str‖str, 2.4–3.3×) and `bench_icnstr_concat_int_dispatch.icn` (str‖int, see above). Need: list/set/scan/IO equivalents.
- [ ] **RTX-17-ICN — widen `str_concat_d` asm arm.** SN4-RTX's symbol; needs §7 re-assignment. Note: RTX-16 already removed half the bails without touching SN4's file.
- [ ] **RTX-22-ICN — `rt_gcheap_alloc`:** 29,582 bails / 98 entries. SN4-RTX's, ALLOC gate.
- [ ] ⛔ **DO NOT TAKE `rt_ws_alloc`.** Probed twice, null both times. Port is possible (RTX-18a de-staticed `g_wsi*`); nothing measured says it is worth it.
- [ ] **RTX-1-ICN — proc-setup family** (`rt_proc_set_fn` 361 + `rt_proc_set_nparams`/`_jmpentry`/`_frame_bytes`/`_dcfn` 210×4). Step 0(d) first. `SCRIP_RTX_ICNCALL`.
- [ ] **RTX-2-ICN — `rt_arg_stage` (897, #2).** Step 0(d) first.
- [ ] **RTX-3-ICN — `rt_call_proc_descr` (542) + `rt_proc_value` (126) + `rt_frame` (255).** ⚠ `rt_frame` was rank 7 / 255 sites at s203 but is now a **phantom** (no `.so` definition, no `@PLT`) — re-run step 0(f) before claiming. Live portion may be just `rt_call_proc_descr`.
- [ ] **RTX-4-ICN — I/O: `rt_write_any_nl` (566, #3).** Reaches libc `printf`; keep C ABI at the libc boundary.
- [ ] **RTX-5-ICN — SCAN/generator family** (`rt_scan_leave` 120 · `rt_scan_enter` 69 · `rt_substr` 109). ⛔ **→ BB TEMPLATE, not `.S`** (§6 ruling): `call rt_scan_enter@PLT` spills/reloads Σ/δ/Δ (r13/r14/r15), which the design pins. Porting to `.S` makes the wrong thing faster. Template work fires `.s` regen ×3 and collides with the ζ ladder — **SERIALIZE WITH LON.**
- [ ] **RTX-6c-ICN — coercion family remainder.** ⛔ BLOCKED ON LON — one line.
- [ ] **RTX-7-ICN — `rt_jmp_frame_lexprep2` (209) + `rt_pl_dc_prep` (202).** ⛔⛔ Dual-entry territory — read FLATDISP findings before touching.
- [ ] **RTX-10-ICN — `NV_GET_fn` (109).** ⚠ Coordinate with DB-1 (write-barrier choke point). ⚠ Two variable backends kept side-by-side (Lon directive) — port must not collapse the switch.
- [ ] **RTX-14-ICN — list construction allocates 3× per list.** Every `rt_make_list` costs 3 `rt_ws_alloc` calls (1 element vector + 2 inside `DATCON_fn`). Canonical Icon allocates header + one `b_lelem` block (`refs/icon-master/src/runtime/fstruct.r:264`). Design change in `core.c`/`by_name_dispatch.c`, not asm — runtime-side so no ζ collision, no `.s` regen. ⚠ `DATCON_fn` serves all languages; owes all three watermarks.
- [ ] **RTX-13-ICN — field access by integer index, not by name.** `bb_field_get.cpp` emits `dat_field_get(fname, obj)` with a per-field string compare at runtime. Canonical Icon resolves to integer indices at translate time. ⛔ PHASE 2 / TEMPLATE TERRITORY — fires `.s` regen ×3, collides with ζ ladder. SERIALIZE WITH LON.

- [ ] ⭐⭐ **RTX-25-ICN — THE RVALUE SUBSCRIPT ALLOCATES A VCELL IT THROWS AWAY. ⬅ RECOMMENDED NEXT; worth multiples of RTX-24.** `t := L[i]` in an RVALUE context calls `rt_subscript_var`, which carves a **72-byte `VCELL_t` purely to NAME a cell**, and `bb_subscript`'s consumer immediately `rt_deref`s it and discards it. Measured s222: 2,000,000 subscripts ⇒ **2,000,000 `rt_agg_alloc` calls**, none needed, and at 8M iterations the resulting ~576 MB of carve makes the window BIMODAL (finding 4 above). Canonical Icon does not allocate to fetch a list element (`refs/icon-master/src/runtime/fstruct.r`, `oasgn.r`). ⛔ **This is a DESIGN rung of the RTX-14-ICN class, not an asm port** — an rvalue arm that returns the VALUE and never mints a VCELL. Runtime-side + template-side; ⚠ `bb_subscript.cpp` is a template ⇒ `.s` regen ×3 and ζ-ladder collision ⇒ **SERIALIZE WITH LON.** RTX-24's asm arm is not wasted by this: it remains the lvalue path (`L[i] := v`).
- [ ] **RTX-26-ICN — the remaining `rt_subscript_var` arms.** RTX-24 ported VARREF(slen==1)→DT_DATA-list with a DT_I subscript. Still C: **DT_A** arrays · **DT_T** tables (`tbl_key_str` + `table_find_pair` + `rt_ws_strdup_c`) · **DT_S/DT_SNUL** string subscripting · non-integer subscripts · the `slen==2`/`slen==0` VARREF forms. ⚠ **Measure which are live before porting any — s222's whole lesson.** ⚠ The DT_S arm wraps on `i <= 0` while the DT_DATA arm wraps on `i < 0`; two arms, two rules, one function. Do not "tidy" that.

### ▶ PHASE 0 — SURVEY (open items)

- [ ] **RTX-0-RULING** ⛔ LON'S CALL: (a) `rt_call_arr` — 87% of `string_manip` window (SN4 measurement; portable fraction unmeasured, Icon 0(d) still owed); (b) SCAN family destination (blocks RTX-5/RTX-2).
- [ ] **RTX-0b-ICN — measurement instrument.** `&time`-based self-timing inside Icon programs discharges the compile-phase confound. `bench_icnstr_concat_dispatch.icn` is the prototype; needs list/set/scan/IO equivalents (RTX-21).
- [ ] **STEP 0(g)** — for any symbol with internal dispatch, identify which arm the emitted code takes before choosing what to port. One compile + one template grep.
- [ ] **STEP 0(h)** — before opening a rung, run `util_rtx_arm_census.sh` on the workload; `COMMITS==0` ⇒ port is unfalsifiable there, must not be written.

### ▶ PHASE 2 — CONVENTION (⛔ SERIALIZE WITH LON; template territory, `.s` regen ×3)

- [ ] **RTX-11-ICN — registerized ABI / fusion.** Proc-setup cluster fused to one entry; S/F in EFLAGS. Changes template call sequences. Must not run concurrently with ICON-BB ζ ladder.
- [ ] **RTX-12-ICN — eradication.** Delete `c_*` bodies once each family is watermark-proven. Cross-language: deletion for Icon is deletion for SNOBOL4 and Prolog too. Requires all three watermarks green.

---

## Landed

- [x] ⭐ **RTX-24-ICN** s222 — `rt_subscript_var` asm, gate `SCRIP_RTX_ICNSUB` (**fourteenth family gate**). **1.376× median / 1.373× min-min, DISJOINT** (ON 83-110 ms vs OFF 114-336 ms, 10 interleaved rounds, warmup discarded, RT_OPT=-O0). Ported arm: VARREF(slen==1) → `rt_deref` → DT_DATA list, DT_I subscript; the inlined `rt_list_view` replaces **two `strcmp` calls per subscript** with inline compares (the RTX-13 by-name disease in a second family). 0(j) **2,000,000 / 0 bailed / 2,000,000 commits**; two-sided falsification by RESULT break (ON 22, OFF 11). Icon 252/11/30 and SNOBOL4 m4 324/2 both unmoved. ⛔ **LOCAL COMMIT ONLY — NOT ON origin, no credential s222; the `[x]` does NOT satisfy the s202 ancestry check.** ⚠ Expectation was stated before measuring (1.3-1.8×) and the result fell inside it; the allocation is NOT removed, which is why the ceiling is what it is — see RTX-25-ICN.

- [x] **RTX-1b-ICN** s209c — `rt_assign_var` asm, `SCRIP_RTX_ICNVAR`. +12% median.
- [x] **RTX-6-ICN** s211 — `rt_coerce_num2_d` asm, `SCRIP_RTX_ICNNUM`. 1.783×.
- [x] **RTX-6b-ICN** s212 — `rt_jct_relop` asm, `SCRIP_RTX_ICNREL`. 1.761×.
- [x] **RTX-8c-ICN** s216 — `dat_field_get` asm. 1.333×.
- [x] **RTX-8d-ICN** s216 — `rt_make_list` REFUSED. Ceremony-only, structurally ungradeable. Do not re-open as `.S` port.
- [x] **RTX-16-ICN** s221 — `bb_lit_scalar` `IR_LIT_STRING` arm populates `slen`. SCRIP `93912f64`. Template edit under Lon §7 grant. `str_concat_d` 0→1,999,999 commits; 194→59ms dispatch-dominant. All three watermarks unmoved vs pristine rebuilds.

---

## Concurrency

| ladder | owns | must not touch |
|---|---|---|
| ICON-BB (ζ) | `emit.cpp`, `templates/*.cpp`, `x86_asm.h`, `zeta_storage.c` | `runtime/rtx/*.S` |
| SN4-RTX | `runtime/rtx/*.S` + family C, by claimed symbol | templates |
| ICON-RTX | `runtime/rtx/*.S` + family C, by claimed symbol | templates (except §6-ruled SCAN, serialized) |

⛔ **CORRECTED s222 — THIS LINE WAS STALE ON ALL THREE ROWS. `RTX-CLAIMS.md` IS THE SINGLE SOURCE OF TRUTH; CHECK IT, NOT THIS TABLE.**
· `rt_call_arr` → **ICON-RTX** (Lon ruling s208), row reads `OUT:ICON-RTX`.
· `rt_num_arith` → `RELEASED:s214 unclaimed` (ABANDON rule, nine sessions unworked) — **free for either ladder**.
· `rt_subscript_var` → released s214 to **ICON-RTX**, and **`DONE:ICON-RTX:s222`** (gate `SCRIP_RTX_ICNSUB`).
Still genuinely SN4-RTX's: `str_concat_d`/`rtx_str.S` (`DONE`, and RTX-17/RTX-23 need a §7 re-assignment to widen).

---

## Session Setup

```bash
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
git clone https://github.com/snobol4ever/.github.git /home/claude/.github
git clone https://github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://github.com/snobol4ever/corpus.git  /home/claude/corpus
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt
# Icon oracle: cd icon-master && make Configure name=linux && make
```

Verify Icon watermark before touching anything: `bash scripts/test_icon_all_rungs.sh` → **252/11/30**.

---

## Permanent notes

**⛔ ORACLE IS `icont`/`iconx` — NEVER JAVA/JVM.** Run under `scrip --run` / `scrip --compile`+link, diff against `icont -s prog.icn -x`.

**⚠ HARNESS:** `test_icon_all_rungs.sh` grades stdout only, exit code discarded. A crash that prints first reads PASS. Use crash-aware split for RTX gates.

**⚠ REAL FORMATTING IS JCON'S** — `&version: Jcon Version 2.2`; reals carry Java `Double.toString`. Do not correct toward `rtos()`; cost 252→250 once.

**⚠ NO `gdb`/`perf`/`valgrind`/`ltrace`/`strace`.** Differential + falsification is the substitute; LD_PRELOAD interposer is the 0(d) instrument.

**⚠ `x86_asm.h` IS A HEADER — `make` DOES NOT TRACK IT.** `rm -rf out /tmp/si_objs` before any rebuild that touches it. Emitter lives in `out/libscrip_rt.so`, not `scrip`.

**⛔ A rung is `[x]` only when its commits are ancestors of `origin/main`.** Check: `git rev-list --count origin/main..<branch>` == 0.

**⚠ `micro` and `deal` are nondeterministic** (3 different hashes in 3 runs). Output-md5 differential is not valid on them.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON-RTX.md` · `ARCH-ICON.md` · `ARCH-SNOBOL4-RTX.md`

## Session-close / push protocol
See RULES.md — `scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim.
