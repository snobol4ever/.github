# GOAL-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29).** Contract: **`ARCH-ICON-RTX.md`** — read before any rung. Runs concurrently with `GOAL-ICON-BB.md` and `GOAL-SNOBOL4-RTX.md`; three-way ownership in `ARCH-ICON-RTX.md` §7.

⛔⛔ **SYMBOL OWNERSHIP IN `RTX-CLAIMS.md`, NOT HERE.** Run `scripts/util_rtx_claims.sh` at session start and close. This ladder is `ICON-RTX`.

---

## ⛔ LIVE CURSOR — s221-ICN (2026-07-30)

**NEXT RUNG: RTX-23-ICN. Both prereqs done — RTX-16 landed, grading window seeded and characterized.**

**Watermarks** (re-derived s221 vs pristine rebuilds): Icon **252/11/30** · SNOBOL4 m3 **329/5**, m4 **324/2/8** · Prolog **164/0** interp + **164/0** compile.

**s221 key findings:**
1. **RTX-16 is TEMPLATE work, not C.** `c_str_concat_d` already returns `BSTRVAL`; the defect was `bb_lit_scalar.cpp`'s `IR_LIT_STRING` arm writing `slen=0` for a compile-time-constant. Landed under Lon's explicit §7 grant. One line, mirroring the `IR_LIT_CHARSET` arm below it. SCRIP `93912f64`.
2. **0 → 1,999,999 commits on `str_concat_d`; 194→59ms (~2.4–3.3×) on the dispatch-dominant window.**
3. ⭐⭐ **A BAIL COUNT CANNOT PREDICT BENEFIT** (s188's law extended). Same fix: `concat_table` NULL (198→195ms, overlapping); `concat_dispatch` 2.4–3.3×. The bails in `concat_table` cost `strlen("x")` O(1); real cost was O(n²) growth + `rt_str_alloc`. **0(d2): run-phase-dominant is necessary, not sufficient — the window must be dominated by the thing being ported.**

⚠ **Pre-existing ledger rot (not mine, not fixed):** `util_rtx_claims.sh` BLOCKED, 3 fatal — `rt_frame` is a phantom (no `.so` definition, no live `@PLT`); `rt_defer_open`/`rt_defer_close` are asm with rows not `DONE` (SN4-RTX's to close).

---

## Queue

### ▶ PHASE 1 — PORTS

- [ ] **RTX-23-ICN — `DT_S || DT_I` concat arm. ⬅ NEXT.** `bench_icnstr_concat_int_dispatch.icn` (corpus benchmarks) isolates the `tag` bail: 2,000,000 / 2,000,000 bailed / **0 commits**. RTX-16 gives the left operand `slen=8`, so DT_I is the sole remaining bail cause. `ON==OFF` today is expected — nothing to grade until the arm exists.
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

⛔ Already claimed by SN4-RTX: `rt_call_arr` · `rt_num_arith` · `rt_subscript_var`.

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
