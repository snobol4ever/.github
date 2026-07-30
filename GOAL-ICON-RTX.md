# GOAL-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29).** Contract: **`ARCH-ICON-RTX.md`** — read before any rung. Runs concurrently with `GOAL-ICON-BB.md` and `GOAL-SNOBOL4-RTX.md`; three-way ownership in `ARCH-ICON-RTX.md` §7.

⛔⛔ **SYMBOL OWNERSHIP IN `RTX-CLAIMS.md`, NOT HERE.** Run `scripts/util_rtx_claims.sh` at session start and close. This ladder is `ICON-RTX`.

---

## ⛔ LIVE CURSOR — s224-ICN (2026-07-30)

**NEXT RUNG: the table MISS / key-INSERT path — ⭐ MEASURED HOT (200,000 arrivals / 200,000 bailed / 0
commits on a table-BUILDING workload). ⛔ It must BAIL-equivalent, i.e. it must MINT C's key-insert trap,
NOT return FAILDESCR (s223 finding 3) — and it calls `rt_ws_strdup_c`, so expect an allocation-dominated
ceiling. RTX-25-ICN remains ⛔ BLOCKED ON LON (design rung + template territory).**

⛔ **CORRECTION TO MY OWN s224 REASONING, RECORDED SO IT IS NOT REPEATED:** I proposed skipping the MISS
path as ceremony because s223's census showed **1** bail in 2,000,001. **That 1 was a property of that
WINDOW (one fresh key), not of the path.** A table-building workload takes 200,000 misses. **A cold
reading on one window is not a cold path** — the static-count trap one level down.

**s224 landed TWO rungs on `rt_subscript_var`, which now carries FIVE arms on one gate:**
**RTX-28-ICN** (`DT_A` array, SNOBOL4 traffic, 1.160× OVERLAPPING, no disjoint claim) and
**RTX-29-ICN** (`DT_T` table keyed by `DT_I` — `t[3]` — **ICON-NATIVE**, 400,008/8 bailed/400,000 commits,
**1.296× median / 1.276× min-min** on a **97.6%-dominant** window, one bimodal ON outlier disclosed ⇒
labelled OVERLAPPING though 9/10 ON rounds are disjoint).

**Watermarks** (re-derived s224 from a fresh clone + full rebuild before any edit, never hand-copied):
Icon **252/11/30** · SNOBOL4 **m3 329/5 · m4 324/2**. All three re-derived AFTER the s224 edit and
**unmoved**.
⚠ **Prolog watermark NOT obtained (third consecutive session):** `scripts/test_corpus_prolog_parser.sh`
FAILs at gate ON and OFF alike ⇒ the differential is an **identity**, pre-existing/environmental, not
s224's. Use ON/OFF/PRISTINE differentials until that harness is repaired.

**s224 landed RTX-28-ICN — `rt_subscript_var` `DT_A` array arm, same gate `SCRIP_RTX_ICNSUB`, which now
carries FOUR arms.** 0(j) **2,000,001 entries / 0 bailed / 2,000,001 commits** (was 200,001/200,001/**0**).
**1.160× median / 1.152× min-min, OVERLAPPING — ⛔ NO DISJOINT SPEED CLAIM**, RT_OPT=-O0, 10 interleaved
rounds, warmup discarded; expectation stated before measuring (1.05–1.35×) and the result fell inside it.
(d2) window dominance **~78%** (104 ms with the subscript vs 23 ms with it deleted) ⇒ the modest ratio is
**not** a window artifact. Full write-up:
`FINDING-2026-07-30-CLAUDE-ICN-RTX-28-DT-A-ARRAY-ARM-LANDED-AND-THE-UNIFORM-OFFSET-PROBE-IS-VACUOUS-BY-SYMMETRY.md`

**s224 key findings:**
1. ⭐⭐⭐ **THE UNIFORM-OFFSET FALSIFICATION PROBE IS VACUOUS BY SYMMETRY ON THIS SYMBOL — AND IT IS
   RTX-24's OWN RECORDED PROBE.** Shifting the computed cell address by one element (verbatim RTX-24's
   *"dropped the `dec`"*) moved the board by ZERO: ON 22, OFF 22. It was NOT a dead arm — census 3/3
   commits, `objdump` showed the `inc` live in the `.o`. **Cause: `rt_subscript_var` serves BOTH the
   lvalue and rvalue path, so a uniform shift moves the WRITE and the READ together and they still
   agree.** RTX-24's identical probe only worked because its list was built by a constructor that
   bypasses the arm. Fixed with an ASYMMETRIC break (collapse all subscripts to slot 0 ⇒ two indices
   alias ⇒ ON 33 / OFF 22). ⛔ **Applies to every `NAMETRAP`-minting symbol either ladder ports —
   `rt_assign_var`, `rt_field_var`, `rt_list_bang_var_at`. Message-boarded to SN4-RTX.**
2. ⭐⭐ **THE ARM WAS DEAD FOR THE EXACT OPPOSITE REASON RTX-24's WAS.** Traffic arrives `base.v=4`
   (**bare DT_A**), never the `DT_N` varref shape, so it died at the first pre-frame `cmp edi, DT_N`.
   RTX-24 had to stop REJECTING varrefs; this arm had to stop REQUIRING them. ⇒ The transferable rule is
   neither slogan: **the entry gate's shape is an EMPIRICAL question per arm, and the instrument is the
   arriving descriptor, not the C source read top-to-bottom.**
3. ⚠ **THE INDEX RULE IS NOW THE THIRD DISTINCT ONE IN ONE FUNCTION.** list wraps on `i < 0`, string on
   `i <= 0`, **array NOT AT ALL** (`off = i - lo`, fail if `off < 0 || off >= hi-lo+1`). Explicitly
   regression-tested. **Do not "tidy" these into one.** `ndim != 1` bails (C ignores `ndim`; a bail
   re-enters the same C body so the flat 2-D path is preserved exactly).
4. ⭐⭐ **RTX-25's PREMISE NOW HOLDS ON A FOURTH ARM.** `rt_agg_alloc` fires 2,000,001× in the array
   window too. The four arms form a measured series that is a statement about WINDOWS, not asm quality:
   table 1.569× (hash+strcmp) · list 1.376× (two strcmp) · **array 1.160× (nothing to remove but the
   allocation)** · string 1.132× (allocation ×2). **The array arm is the cheapest-dispatch arm, so it
   sits nearest the allocation floor. RTX-25 dominates this family by construction — fourth independent
   measurement saying so.**
5. ⭐ **`rt_frame` FATAL CLOSED WITH ITS CAUSE NAMED** (gate 3 fatal → 2). Not merely "phantom":
   **eradicated at RUNG ZS-1 s57** when the main ζ frame moved from an arena memo to the driver stack —
   the only two references left in the tree are comments recording the removal. ⛔ The other two fatals
   (`rt_defer_open`/`rt_defer_close`, already asm with non-`DONE` rows) are **SN4-RTX's and were not
   touched** — hard rule 1 includes *"I'm only reading it."*

## Queue

### ▶ PHASE 1 — PORTS

- [ ] ⛔ **RTX-23-ICN — `DT_S || DT_I` concat arm. BLOCKED ON LON: needs the §7 re-assignment of `str_concat_d`/`rtx_str.S` from SN4-RTX (row is `DONE:SN4-RTX`).** Premise RE-VERIFIED s222: 2,000,000 entries / 2,000,000 bailed / 0 commits, and `rt_str_alloc` fires 4,000,000 (2×/iteration), confirming the ⅓-dispatch constraint below. `bench_icnstr_concat_int_dispatch.icn` (**`corpus/benchmarks/icon/`** — corrected s222; it is NOT under `benchmarks/icon/rtx/`) isolates the `tag` bail: 2,000,000 / 2,000,000 bailed / **0 commits**. RTX-16 gives the left operand `slen=8`, so DT_I is the sole remaining bail cause. `ON==OFF` today is expected — nothing to grade until the arm exists.
  ⛔ **DESIGN CONSTRAINT (measured s221):** window is only **~⅓ dispatch** — `rt_str_alloc` fires 4,000,000 (2×/iteration) vs 2,000,000 (1×) in `str||str`, because integer coercion allocates. **A tag-only arm captures ~⅓; a formatting arm that produces the integer into the result buffer in asm removes one allocation and captures ~2×+.** State expectation before measuring: tag-only ≈ 1.15×, formatting arm ≈ 2×+. ⚠ 781ms outlier seen in 3 rounds — use more rounds. ⚠ `rtx_str.S` is SN4-RTX's file; needs same §7 re-assignment as RTX-17.
- [ ] **RTX-21-ICN — extend run-phase workload set** (list/set/scan/IO). Two dispatch-dominant seeds landed s221: `bench_icnstr_concat_dispatch.icn` (str‖str, 2.4–3.3×) and `bench_icnstr_concat_int_dispatch.icn` (str‖int, see above). Need: list/set/scan/IO equivalents.
- [ ] **RTX-17-ICN — widen `str_concat_d` asm arm.** SN4-RTX's symbol; needs §7 re-assignment. Note: RTX-16 already removed half the bails without touching SN4's file.
- [ ] **RTX-22-ICN — `rt_gcheap_alloc`:** 29,582 bails / 98 entries. SN4-RTX's, ALLOC gate.
- [ ] ⛔ **DO NOT TAKE `rt_ws_alloc`.** Probed twice, null both times. Port is possible (RTX-18a de-staticed `g_wsi*`); nothing measured says it is worth it.
- [x] ⛔ **RTX-1-ICN — CLOSED BY THE LEDGER, NOT BY WORK.** `rt_proc_set_fn` is `BLOCKED:MEASURED-FLAT` in `RTX-CLAIMS.md`. 0(d) was ALREADY RUN and came back flat; this row said "Step 0(d) first" for eight sessions and would have sent a session to re-derive it (s223 finding 1). Do not reopen without a new measurement that contradicts the ledger.
- [x] ⛔ **RTX-2-ICN — CLOSED BY THE LEDGER, NOT BY WORK.** `rt_arg_stage` is `BLOCKED:MEASURED-ZERO`. The "897 sites, #2" static rank is exactly the `rt_call_arr` trap (2157 sites, 8 calls flat) one symbol over. 0(d) already run, already zero (s223 finding 1).
- [x] ⛔ **RTX-3-ICN — CLOSED BY THE LEDGER, NOT BY WORK.** `rt_call_proc_descr` is `BLOCKED:MEASURED-ZERO`; `rt_proc_value` is `DONE:ICON-RTX:s214`; `rt_frame` is a phantom (no `.so` definition, no `@PLT`). Nothing live remains in this row (s223 finding 1).
- [ ] **RTX-4-ICN — I/O: `rt_write_any_nl` (566, #3).** Reaches libc `printf`; keep C ABI at the libc boundary.
- [ ] **RTX-5-ICN — SCAN/generator family** (`rt_scan_leave` 120 · `rt_scan_enter` 69 · `rt_substr` 109). ⛔ **→ BB TEMPLATE, not `.S`** (§6 ruling): `call rt_scan_enter@PLT` spills/reloads Σ/δ/Δ (r13/r14/r15), which the design pins. Porting to `.S` makes the wrong thing faster. Template work fires `.s` regen ×3 and collides with the ζ ladder — **SERIALIZE WITH LON.**
- [ ] **RTX-6c-ICN — coercion family remainder.** ⛔ BLOCKED ON LON — one line.
- [ ] **RTX-7-ICN — `rt_jmp_frame_lexprep2` (209) + `rt_pl_dc_prep` (202).** ⛔⛔ Dual-entry territory — read FLATDISP findings before touching.
- [ ] **RTX-10-ICN — `NV_GET_fn` (109).** ⚠ Coordinate with DB-1 (write-barrier choke point). ⚠ Two variable backends kept side-by-side (Lon directive) — port must not collapse the switch.
- [ ] **RTX-14-ICN — list construction allocates 3× per list.** Every `rt_make_list` costs 3 `rt_ws_alloc` calls (1 element vector + 2 inside `DATCON_fn`). Canonical Icon allocates header + one `b_lelem` block (`refs/icon-master/src/runtime/fstruct.r:264`). Design change in `core.c`/`by_name_dispatch.c`, not asm — runtime-side so no ζ collision, no `.s` regen. ⚠ `DATCON_fn` serves all languages; owes all three watermarks.
- [ ] **RTX-13-ICN — field access by integer index, not by name.** `bb_field_get.cpp` emits `dat_field_get(fname, obj)` with a per-field string compare at runtime. Canonical Icon resolves to integer indices at translate time. ⛔ PHASE 2 / TEMPLATE TERRITORY — fires `.s` regen ×3, collides with ζ ladder. SERIALIZE WITH LON.

- [ ] ⭐⭐ **RTX-25-ICN — THE RVALUE SUBSCRIPT ALLOCATES A VCELL IT THROWS AWAY. ⬅ RECOMMENDED NEXT; worth multiples of RTX-24.** `t := L[i]` in an RVALUE context calls `rt_subscript_var`, which carves a **72-byte `VCELL_t` purely to NAME a cell**, and `bb_subscript`'s consumer immediately `rt_deref`s it and discards it. Measured s222: 2,000,000 subscripts ⇒ **2,000,000 `rt_agg_alloc` calls**, none needed, and at 8M iterations the resulting ~576 MB of carve makes the window BIMODAL (finding 4 above). Canonical Icon does not allocate to fetch a list element (`refs/icon-master/src/runtime/fstruct.r`, `oasgn.r`). ⛔ **This is a DESIGN rung of the RTX-14-ICN class, not an asm port** — an rvalue arm that returns the VALUE and never mints a VCELL. Runtime-side + template-side; ⚠ `bb_subscript.cpp` is a template ⇒ `.s` regen ×3 and ζ-ladder collision ⇒ **SERIALIZE WITH LON.** RTX-24's asm arm is not wasted by this: it remains the lvalue path (`L[i] := v`).
- [ ] **RTX-26-ICN — the remaining `rt_subscript_var` arms.** ⭐ **s223 LANDED THE `DT_T` TABLE ARM (`DT_S` key), 1.569× disjoint, SCRIP `8ae3483a`, AND THE `DT_S` SUBSTRING-TRAP ARM (RTX-27-ICN, SCRIP `a4df13c4`, completeness only, no disjoint claim).** ⭐ **s224 LANDED THE `DT_A` ARRAY ARM (RTX-28-ICN) — measured SNOBOL4-only for this symbol (0 Icon arrivals, 2,000,001 SNOBOL4), 1.160× OVERLAPPING, no disjoint claim.** Remaining: non-integer subscripts · the `slen==2`/`slen==0` VARREF forms · the table MISS/insert path (`rt_ws_strdup_c`) · `DT_SNUL`. RTX-24 ported VARREF(slen==1)→DT_DATA-list with a DT_I subscript. Still C: **DT_A** arrays · **DT_T** tables (`tbl_key_str` + `table_find_pair` + `rt_ws_strdup_c`) · **DT_S/DT_SNUL** string subscripting · non-integer subscripts · the `slen==2`/`slen==0` VARREF forms. ⚠ **Measure which are live before porting any — s222's whole lesson.** ⚠ The DT_S arm wraps on `i <= 0` while the DT_DATA arm wraps on `i < 0`; two arms, two rules, one function. Do not "tidy" that.

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

- [x] ⭐ **RTX-24-ICN** s222 — `rt_subscript_var` asm, gate `SCRIP_RTX_ICNSUB` (**fourteenth family gate**). **1.376× median / 1.373× min-min, DISJOINT** (ON 83-110 ms vs OFF 114-336 ms, 10 interleaved rounds, warmup discarded, RT_OPT=-O0). Ported arm: VARREF(slen==1) → `rt_deref` → DT_DATA list, DT_I subscript; the inlined `rt_list_view` replaces **two `strcmp` calls per subscript** with inline compares (the RTX-13 by-name disease in a second family). 0(j) **2,000,000 / 0 bailed / 2,000,000 commits**; two-sided falsification by RESULT break (ON 22, OFF 11). Icon 252/11/30 and SNOBOL4 m4 324/2 both unmoved. ✅ **VOIDED s223 — THIS BANNER WAS FALSE. RTX-24 IS on `origin/main`:** adding commit `b38e31d8`, verified from a fresh clone before any s223 edit, `git rev-list --count origin/main..HEAD` == 0, `rtx_icnsub.o` in the `.so` link line. Push status must never be written into a doc (`RULES.md` s47 rule (a)); `handoff_status.sh` is the only ground truth. ⚠ Expectation was stated before measuring (1.3-1.8×) and the result fell inside it; the allocation is NOT removed, which is why the ceiling is what it is — see RTX-25-ICN.

- [x] ⭐ **RTX-28-ICN** s224 — `rt_subscript_var` `DT_A` array arm, existing gate `SCRIP_RTX_ICNSUB` (**no new gate**), fourth arm on the symbol. 0(j) **2,000,001 / 0 bailed / 2,000,001 commits** (was 200,001/200,001/**0** — the arm died at the first pre-frame `cmp edi, DT_N` because the traffic arrives **bare DT_A**, RTX-24's error inverted). **1.160× median / 1.152× min-min, OVERLAPPING — ⛔ NO DISJOINT SPEED CLAIM**; (d2) dominance ~78%, so the ratio is the ALLOCATION floor, not a window artifact. Falsified two-sided by an **asymmetric** RESULT break (slot-0 collapse: ON 33 / OFF 22) **after the uniform-offset probe proved VACUOUS BY SYMMETRY** — see finding §2, this is owed to every NAMETRAP-minting port. Icon 252/11/30 · SNOBOL4 m3 329/5 · m4 324/2 all re-derived and unmoved. `ARBLK_t` offsets + `DT_A` pinned by new `_Static_assert`s in `rtx_init.c`.
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
