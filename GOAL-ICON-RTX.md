# GOAL-ICON-RTX.md — The Icon Runtime in Optimized x86-64 Assembly

**Minted s203-ICN (2026-07-29).** Contract: **`ARCH-ICON-RTX.md`** — read before any rung. Runs concurrently with `GOAL-ICON-BB.md` and `GOAL-SNOBOL4-RTX.md`; three-way ownership in `ARCH-ICON-RTX.md` §7.

⛔⛔ **SYMBOL OWNERSHIP IN `RTX-CLAIMS.md`, NOT HERE.** Run `scripts/util_rtx_claims.sh` at session start and close. This ladder is `ICON-RTX`.

---

## ⛔ LIVE CURSOR — s223-ICN (2026-07-30)

**NEXT RUNG: RTX-25-ICN (⛔ BLOCKED ON LON — template territory, must be serialized) or RTX-26-ICN's remaining arms (unblocked, but see the string-window caveat below).**

**Watermarks** (re-derived s223 from a fresh clone + full rebuild, never hand-copied): Icon **252/11/30** · SNOBOL4 **m4 324/2** (m3 329/5).
⚠ **Prolog watermark NOT obtained:** `scripts/test_corpus_prolog_parser.sh` FAILs (crash rate > 5%) at gate **ON and OFF alike** ⇒ the differential is an **identity**, pre-existing/environmental, **not s223's**. s222's condition, reproduced not inherited. Use the ON/OFF/PRISTINE differential until that harness is repaired.

**s223 landed RTX-26-ICN — `rt_subscript_var` `DT_T` table arm (`DT_S` key), same gate `SCRIP_RTX_ICNSUB`, 1.569× disjoint.** SCRIP `8ae3483a`. Full write-up: `FINDING-2026-07-30-CLAUDE-ICN-RTX-26-TABLE-ARM-LANDED-1p569X-AND-THE-QUEUE-HELD-THREE-RUNGS-THE-LEDGER-HAD-ALREADY-KILLED.md`.

**s223 key findings:**
1. ⭐⭐⭐ **THE QUEUE LISTED THREE RUNGS AS OPEN THAT THE LEDGER HAD ALREADY MEASURED DEAD.** RTX-1/2/3-ICN all carry "Step 0(d) first" in PHASE 1 while `RTX-CLAIMS.md` records `rt_arg_stage` = `BLOCKED:MEASURED-ZERO`, `rt_proc_set_fn` = `BLOCKED:MEASURED-FLAT`, `rt_call_proc_descr` = `BLOCKED:MEASURED-ZERO`. A session orienting off this ladder would have opened RTX-2 as the rank-2 prize and spent its 0(d) budget re-deriving a zero. **Third consecutive session to find the ladder disagreeing with the ledger** (s222 finding 7, different rows). Queue rows corrected inline below. ⇒ **PROPOSED, needs Lon: the queue should stop restating step-0 status entirely and point at `util_rtx_claims.sh`, the way §Concurrency was demoted at s222. Two files that both hold status will disagree.**
2. ⛔ **s222's "LOCAL COMMIT ONLY — NOT ON origin" BANNER ON RTX-24 WAS FALSE.** Measured s223 from a fresh clone before any edit: `rtx_icnsub.S` present, adding commit `b38e31d8`, `git rev-list --count origin/main..HEAD` == **0**, `rtx_icnsub.o` in the `.so` link line. **RTX-24 IS on origin.** This is `RULES.md` s47 rule (a) exactly — push status written into a doc is structurally incapable of being true and nobody edits it afterward. The banner has **no correct form**; it must not be written. `handoff_status.sh` is the only ground truth. Banner voided.
3. ⭐⭐ **THE TABLE MISS MUST BAIL, NOT FAIL, AND `FAILDESCR` WOULD HAVE BEEN SILENT.** On a chain miss the C body does not fail — it mints a key-**INSERT** trap (`key = rt_ws_strdup_c(ks)`) so `t[k] := v` on a fresh key has somewhere to land. An arm returning `FAILDESCR` reads correct on every rvalue workload and silently breaks lvalue insert. Census after the port: **2,000,001 entries / 1 bailed / 2,000,000 commits** — that one bail IS the fresh-key insert. A port showing 0 bails would have been wrong.
4. ⚠ **THE STRING ARM IS LIVE, UNPORTED, AND UNGRADEABLE.** `s[3]` measures 2,000,000 entries / 2,000,000 bailed / **0 commits** — as live as the table arm was — but its wall clock is **1717/180/1275 ms**, ~9.5× multiplicative spread, because `s[i]` mints a substring trapped variable whose deref allocates a 1-char string ⇒ **two** allocations per iteration ⇒ allocation-dominated. Per (d2)'s own prohibition, do not grade a dispatch port there. Rebuild the window first; more rounds cannot fix a multiplicative spread (s222 finding 4).
5. ⭐⭐ **RTX-25's PREMISE IS NOW MEASURED ON THREE ARMS AND IT DOMINATES RTX-26 BY CONSTRUCTION.** `rt_agg_alloc` fires **exactly 2,000,000 times in all three windows** (list, table, string) — one thrown-away 72-byte VCELL per rvalue subscript on **every** arm. Canonical `oref.r`'s `operator{0,1} [] subsc` returns `struct_var(&bp->lelem.lslots[i], bp)`, a pointer into the existing block — **canonical Icon does not allocate to fetch an element.** (The table arm is the one place it legitimately does: `alctvtbl`.) RTX-26 makes dispatch 1.57× cheaper and leaves the allocation; **RTX-25 removes it.** RTX-24/26 asm is not wasted — both remain the lvalue path.
6. ⚠ **`DT_T` IS defined in `rtx_abi.inc:63`** — checked, not assumed, because s222 finding 5 proved an undefined tag compare assembles cleanly as a relocation. It was **unpinned**; now pinned, with `TBPAIR_t`, `TBBLK_t.buckets` and `TABLE_BUCKETS == 256` (the `movzx eax, al` hash fold is valid only for 256).

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
- [ ] **RTX-26-ICN — the remaining `rt_subscript_var` arms.** ⭐ **s223 LANDED THE `DT_T` TABLE ARM (`DT_S` key), 1.569× disjoint, SCRIP `8ae3483a`.** RTX-24 ported VARREF(slen==1)→DT_DATA-list with a DT_I subscript. Still C: **DT_A** arrays · **DT_T** tables (`tbl_key_str` + `table_find_pair` + `rt_ws_strdup_c`) · **DT_S/DT_SNUL** string subscripting · non-integer subscripts · the `slen==2`/`slen==0` VARREF forms. ⚠ **Measure which are live before porting any — s222's whole lesson.** ⚠ The DT_S arm wraps on `i <= 0` while the DT_DATA arm wraps on `i < 0`; two arms, two rules, one function. Do not "tidy" that.

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
