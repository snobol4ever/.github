# GOAL-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29).** Contract: **`ARCH-ICON-RTX.md`** — read before any rung. Runs concurrently with `GOAL-ICON-BB.md` and `GOAL-SNOBOL4-RTX.md`; three-way ownership in `ARCH-ICON-RTX.md` §7.

⛔⛔ **SYMBOL OWNERSHIP IN `RTX-CLAIMS.md`, NOT HERE.** Run `scripts/util_rtx_claims.sh` at session start and close. This ladder is `ICON-RTX`.

---

## ⛔ LIVE CURSOR — s225-ICN (2026-07-30)

**NEXT RUNG: RTX-21-ICN** — extend run-phase workload set (list/set/scan/IO). First unblocked survey rung.
RTX-23-ICN: ⛔ BLOCKED ON LON (§7 re-assignment of `str_concat_d`/`rtx_str.S` from SN4-RTX).
RTX-25-ICN: ⛔ BLOCKED ON LON (design rung + template territory, fires `.s` regen ×3).

**s225 landed RTX-30-ICN** — `rt_subscript_var` table MISS / key-INSERT trap, same gate `SCRIP_RTX_ICNSUB`, sixth arm. SCRIP `b85f0303`. 0(j) **2,000,001 / 0 bailed / 2,000,001 commits** (was 200,001/200,001/**0**). **1.164× median / 1.154× min-min, OVERLAPPING — ⛔ NO DISJOINT SPEED CLAIM.** (d2) dominance ~94%; ratio is the two-allocation floor (`rt_agg_alloc` + `rt_ws_strdup_c`). Serves both key shapes (DT_S and RTX-29 DT_I) from `.Lsub_hash_init`. Full write-up: `FINDING-2026-07-30-CLAUDE-ICN-RTX-30-TABLE-MISS-KEY-INSERT-TRAP-LANDED-AND-THE-OBVIOUS-KEY-SHIFT-PROBE-IS-VACUOUS-BY-SYMMETRY.md`.

⚠ **SNOBOL4 watermarks NOT confirmed s225:** m4 read 332/2 vs documented 324/2, m3 did not complete. No pristine SN4 baseline taken. **Re-derive SN4 m3 329/5 and m4 324/2 from pristine at next session start before any edit.**

**Watermarks:** Icon **252/11/30** (re-derived s225 from pristine stash before edit and after — unmoved). SNOBOL4 m3/m4: ⚠ UNCONFIRMED s225, use s224 values (m3 329/5 · m4 324/2) until re-derived. Prolog: harness FAILs identically ON and OFF — pre-existing/environmental (fourth consecutive session).

**s224 transferable finding:** ⛔ **UNIFORM-OFFSET FALSIFICATION PROBE IS VACUOUS BY SYMMETRY** on any NAMETRAP-minting symbol (confirmed on `DT_A` arm). A shift moves the WRITE and READ together; use an ASYMMETRIC break instead (collapse two subscripts to slot 0). Applies to `rt_assign_var`, `rt_field_var`, `rt_list_bang_var_at` — boarded to SN4-RTX. Full write-up: `FINDING-2026-07-30-CLAUDE-ICN-RTX-28-DT-A-ARRAY-ARM-LANDED-AND-THE-UNIFORM-OFFSET-PROBE-IS-VACUOUS-BY-SYMMETRY.md`.

---

## Queue

### ▶ PHASE 1 — PORTS

- [ ] ⛔ **RTX-23-ICN — `DT_S||DT_I` concat arm. BLOCKED ON LON:** needs §7 re-assignment of `str_concat_d`/`rtx_str.S` from SN4-RTX. Measured s222: 2M entries / 2M bailed / 0 commits. Window is ~⅓ dispatch (integer coercion allocates); tag-only arm ≈1.15×, formatting arm ≈2×+. Bench: `bench_icnstr_concat_int_dispatch.icn` in `corpus/benchmarks/icon/`.
- [ ] **RTX-21-ICN — extend run-phase workload set** (list/set/scan/IO). Seeds landed s221: `bench_icnstr_concat_dispatch.icn` (str‖str) and `bench_icnstr_concat_int_dispatch.icn` (str‖int). Need list/set/scan/IO equivalents.
- [ ] **RTX-17-ICN — widen `str_concat_d` asm arm.** SN4-RTX's symbol; needs §7 re-assignment. RTX-16 already removed half the bails.
- [ ] **RTX-22-ICN — `rt_gcheap_alloc`:** 29,582 bails / 98 entries. SN4-RTX's, ALLOC gate.
- [ ] ⛔ **DO NOT TAKE `rt_ws_alloc`.** Probed twice, null both times.
- [ ] **RTX-4-ICN — I/O: `rt_write_any_nl` (566, #3).** Reaches libc `printf`; keep C ABI at the libc boundary.
- [ ] **RTX-5-ICN — SCAN/generator family** (`rt_scan_leave` 120 · `rt_scan_enter` 69 · `rt_substr` 109). ⛔ **→ BB TEMPLATE, not `.S`** (§6 ruling): spills/reloads Σ/δ/Δ (r13/r14/r15). Template work fires `.s` regen ×3 — **SERIALIZE WITH LON.**
- [ ] **RTX-6c-ICN — coercion family remainder.** ⛔ BLOCKED ON LON.
- [ ] **RTX-7-ICN — `rt_jmp_frame_lexprep2` (209) + `rt_pl_dc_prep` (202).** ⛔⛔ Dual-entry territory — read FLATDISP findings before touching.
- [ ] **RTX-10-ICN — `NV_GET_fn` (109).** ⚠ Coordinate with DB-1 (write-barrier choke point); two variable backends kept side-by-side (Lon directive) — must not collapse the switch.
- [ ] **RTX-14-ICN — list construction allocates 3× per list.** Design change in `core.c`/`by_name_dispatch.c` (not asm). `DATCON_fn` serves all languages; owes all three watermarks. Canonical: `refs/icon-master/src/runtime/fstruct.r:264`.
- [ ] **RTX-13-ICN — field access by integer index.** ⛔ PHASE 2 / TEMPLATE TERRITORY — fires `.s` regen ×3. SERIALIZE WITH LON.
- [ ] ⭐⭐ **RTX-25-ICN — rvalue subscript allocates a VCELL it discards. ⛔ SERIALIZE WITH LON** (design rung; `bb_subscript.cpp` is template territory, `.s` regen ×3). `t := L[i]` carves a 72-byte VCELL purely to name a cell that `rt_deref` immediately throws away — 2M unnecessary `rt_agg_alloc` calls measured s222. RTX-24's lvalue arm is not wasted: it remains the `L[i]:=v` path.

- [ ] **RTX-26/27/28/29 — `rt_subscript_var` remaining arms (see sublist below).**

### ▶ RTX-26/29 REMAINDER — triaged s224, 0(h) pre-done; do not re-derive

- [x] ⭐ **RTX-30-ICN — table MISS / key-INSERT.** s225. SCRIP `b85f0303`. 1.164× OVERLAPPING. See LIVE CURSOR + FINDING doc.
- [ ] ⛔⛔ **DO NOT PORT `DT_R` or `DT_DATA` table keys.** CLOSED BY MEASUREMENT s224 (200K arrivals each, 100% bailing). `tbl_key_str` routes both through `snprintf` formatters — reproducing `%.17g` in asm is high-risk and self-concealing on miss. Keep C at the libc formatting boundary.
- [ ] ⚠ **`DT_SNUL`/`slen==0` string subscript — LIVE BUT PURE FAILURE PATH.** 200,000/200,000 bailed/0 commits on `s:=""; s[1]` (fails by construction). Take for completeness only; claim no speed.
- [ ] ⚠ **`slen==2` VARREF / non-integer subscripts** — unmeasured; run 0(h) before opening.

### ▶ PHASE 0 — SURVEY (open items)

- [ ] **RTX-0-RULING** ⛔ LON'S CALL: (a) `rt_call_arr` — 87% of `string_manip` window (SN4 measurement; Icon 0(d) still owed); (b) SCAN family destination (blocks RTX-5/RTX-2).
- [ ] **RTX-0b-ICN — measurement instrument.** `&time`-based self-timing discharges compile-phase confound. Prototype: `bench_icnstr_concat_dispatch.icn`. Need list/set/scan/IO equivalents (RTX-21).
- [ ] **STEP 0(g)** — for any symbol with internal dispatch, identify which arm the emitted code takes before porting. One compile + one template grep.
- [ ] **STEP 0(h)** — before opening a rung, run `util_rtx_arm_census.sh`; `COMMITS==0` ⇒ unfalsifiable, must not write.

### ▶ PHASE 2 — CONVENTION (⛔ SERIALIZE WITH LON; template territory, `.s` regen ×3)

- [ ] **RTX-11-ICN — registerized ABI / fusion.** Proc-setup cluster fused; S/F in EFLAGS. Must not run concurrently with ICON-BB ζ ladder.
- [ ] **RTX-12-ICN — eradication.** Delete `c_*` bodies once each family is watermark-proven. Requires all three watermarks green. Cross-language: deletion for Icon = deletion for SN4 and Prolog.

---

## Landed

- [x] ⭐ **RTX-30-ICN** s225 — `rt_subscript_var` table MISS / key-INSERT trap, sixth arm on `SCRIP_RTX_ICNSUB`. SCRIP `b85f0303`. 0(j) **2,000,001 / 0 / 2,000,001**. **1.164× median / 1.154× min-min, OVERLAPPING.** Two-allocation floor (`rt_agg_alloc` + `rt_ws_strdup_c`). Serves DT_S and DT_I key shapes from `.Lsub_hash_init`. Falsified by asymmetric result break (`vc->tbl := 0`); key-shift probe reasoned vacuous by symmetry before use. Icon 252/11/30 unmoved. SN4 unconfirmed — re-derive at next session start.

- [x] ⭐ **RTX-24-ICN** s222 — `rt_subscript_var` DT_DATA list arm, gate `SCRIP_RTX_ICNSUB` (14th gate). 1.376×/1.373× DISJOINT. 0(j) 2M/0/2M. Inlines `rt_list_view` (two strcmps → inline compare).
- [x] ⭐ **RTX-26-ICN** s223 — `rt_subscript_var` DT_T table arm (DT_S key). SCRIP `8ae3483a`. 1.569×/1.567× DISJOINT. 0(j) 2,000,001/1/2,000,000 (the 1 bail is the MISS path, deliberately left to C).
- [x] **RTX-27-ICN** s223 — `rt_subscript_var` DT_S substring-trap arm. SCRIP `a4df13c4`. Completeness only, no disjoint claim.
- [x] ⭐ **RTX-28-ICN** s224 — `rt_subscript_var` DT_A array arm (SNOBOL4 traffic, bare DT_A entry). 1.160×/1.152× OVERLAPPING. 0(j) 2,000,001/0/2,000,001. `_Static_assert`s added for `ARBLK_t` offsets + `DT_A`.
- [x] **RTX-29-ICN** s224 — `rt_subscript_var` DT_T table arm (DT_I key). ICON-NATIVE. 1.296×/1.276× OVERLAPPING. 0(j) 400,008/8/400,000.
- [x] **RTX-1b-ICN** s209c — `rt_assign_var` asm, `SCRIP_RTX_ICNVAR`. +12% median.
- [x] **RTX-6-ICN** s211 — `rt_coerce_num2_d` asm, `SCRIP_RTX_ICNNUM`. 1.783×.
- [x] **RTX-6b-ICN** s212 — `rt_jct_relop` asm, `SCRIP_RTX_ICNREL`. 1.761×.
- [x] **RTX-8c-ICN** s216 — `dat_field_get` asm. 1.333×.
- [x] **RTX-8d-ICN** s216 — `rt_make_list` REFUSED. Ceremony-only, structurally ungradeable. Do not reopen.
- [x] **RTX-16-ICN** s221 — `bb_lit_scalar` IR_LIT_STRING arm populates `slen`. SCRIP `93912f64`. `str_concat_d` 0→1,999,999 commits; 194→59ms.
- [x] ⛔ **RTX-1/2/3-ICN** — CLOSED BY LEDGER, NOT WORK. `rt_proc_set_fn` FLAT, `rt_arg_stage` ZERO, `rt_call_proc_descr` ZERO, `rt_frame` phantom. See RTX-CLAIMS.md.

---

## Concurrency

| ladder | owns | must not touch |
|---|---|---|
| ICON-BB (ζ) | `emit.cpp`, `templates/*.cpp`, `x86_asm.h`, `zeta_storage.c` | `runtime/rtx/*.S` |
| SN4-RTX | `runtime/rtx/*.S` + family C, by claimed symbol | templates |
| ICON-RTX | `runtime/rtx/*.S` + family C, by claimed symbol | templates (except §6-ruled SCAN, serialized) |

⛔ **`RTX-CLAIMS.md` IS THE SINGLE SOURCE OF TRUTH for symbol ownership — not this table.**

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
```

Verify Icon watermark before touching anything: `bash scripts/test_icon_all_rungs.sh` → **252/11/30**.

---

## Permanent notes

**⛔ ORACLE IS `icont`/`iconx` — NEVER JAVA/JVM.**

**⚠ HARNESS:** `test_icon_all_rungs.sh` grades stdout only; exit code discarded. A crash that prints first reads PASS. Use crash-aware split for RTX gates.

**⚠ REAL FORMATTING IS JCON'S** — reals carry Java `Double.toString`. Do not correct toward `rtos()`; cost 252→250 once.

**⚠ NO `gdb`/`perf`/`valgrind`/`ltrace`/`strace`.** Differential + falsification is the substitute; LD_PRELOAD interposer is the 0(d) instrument.

**⚠ `x86_asm.h` IS A HEADER — `make` DOES NOT TRACK IT.** `rm -rf out /tmp/si_objs` before any rebuild touching it.

**⛔ A rung is `[x]` only when commits are ancestors of `origin/main`.** Check: `git rev-list --count origin/main..<branch>` == 0.

**⚠ `micro` and `deal` are nondeterministic.** Output-md5 differential not valid on them.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON-RTX.md` · `ARCH-ICON.md` · `ARCH-SNOBOL4-RTX.md`

## Session-close / push protocol
See RULES.md — `scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim.
