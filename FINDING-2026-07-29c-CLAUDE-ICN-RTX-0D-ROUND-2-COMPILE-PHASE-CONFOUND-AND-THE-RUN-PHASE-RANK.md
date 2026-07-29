# FINDING-2026-07-29c-CLAUDE-ICN-RTX-0D-ROUND-2 — THE queens/deal PROFILE IS MEASURING THE COMPILER; THE RUN-PHASE RANK IS DIFFERENT AND ICON'S #1 IS SN4-RTX's

**Session:** s210-ICN · **Rung:** RTX-0d-ICN round 2 (post-RTX-1b re-rank) · **Landed:** measurement only.
**Gate:** Icon watermark **252/11/30** re-derived fresh before and after. `src/` untouched;
`out/libscrip_rt.so` restored and **md5-verified byte-identical to pristine**
(`93498e12f6075fad7e1836ee6b818679`). Two new files under `tools/`, linked into nothing.

---

## ⭐⭐ FINDING 1 — THE STATIC INVENTORY IS STRUCTURALLY BLIND TO C→C TRAFFIC

`ARCH-ICON-RTX.md` §5 counts `call sym@PLT` in emitted `.s` artifacts. That measures **exactly one
boundary: EMITTED-CODE → RUNTIME.** Any runtime function whose callers are *other runtime C functions* is
invisible to it at any heat. The profiler below sees 707 runtime functions; the static table ranks 28.

**This is a new member of the phantom taxonomy, and unlike the previous five it is not a naming defect at
all.** Prior members: DEAD names (RTX-2), INVENTED names (RTX-3), MISRECORDED names (RTX-4), COLD names
(s188), ALREADY-ASM names (s200), NOT-A-RUNTIME-SYMBOL names (s203, the `@PLT` filter). **This one is a
name the inventory cannot see because the inventory only looks at one of the two call boundaries.**

---

## ⛔⛔ FINDING 2 — AND IT INVALIDATES THE FIRST PROFILE I TOOK. THE `queens`/`deal` BOARD IS COMPILE-DOMINATED.

Profiling `queens` and `deal` gave a top three that beats everything else by ~20×:

| symbol | queens | deal |
|---|---:|---:|
| `rt_zc_frame_live` | 46,578 | 45,025 |
| `rt_zeta_storage_get` | 46,578 | 45,025 |
| `rt_zeta_port_mode` | 15,275 | 15,070 |

**None of them is runtime traffic. All three are the EMITTER.** `zeta_storage.c` belongs to the ICON-BB
ζ ladder (`ARCH-ICON-RTX.md` §7 ownership table), and mode 3 compiles and runs **in one process**, so a
whole-process profile mixes both phases.

**Separated by scaling the RUN work 4× while holding the COMPILE work identical:**

| symbol | N=20k | N=80k | ratio | verdict |
|---|---:|---:|---:|---|
| `rt_zc_frame_live` | 2,109 | 2,109 | **1.00** | **COMPILE-PHASE** |
| `rt_zeta_storage_get` | 2,109 | 2,109 | **1.00** | **COMPILE-PHASE** |
| `rt_zeta_port_mode` | 615 | 615 | **1.00** | **COMPILE-PHASE** |
| `rt_add` | 20,000 | 80,000 | **4.00** | RUN-PHASE |

⇒ **On a 13 ms benchmark, compilation dominates the profile.** This is the BOGUS-WINDOW finding
(s210-ICN, prior doc) resurfacing as a *correctness* defect rather than a timing one: **the corpus is not
merely too short to TIME, it is too short to PROFILE.** Any Icon dynamic rank taken over whole-process
counts on `benchmarks/icon/` is contaminated, and the contamination is ~20:1.

⭐ **METHOD OF RECORD — THE DELTA CANCELS IT EXACTLY.** Rank by `count(4N) − count(N)`. The compile-phase
component is a constant and subtracts to zero identically; no estimate, no threshold, no judgement call.

---

## ⭐⭐ FINDING 3 — THE CLEAN RUN-PHASE RANK (compile-phase cancelled, three workload shapes)

| run-phase Δ | symbol | proc | scan | list | ownership / state |
|---:|---|---:|---:|---:|---|
| **315,000** | **`rt_subscript_var`** | 0 | 0 | 315,000 | ⛔ **SN4-RTX's** (`OUT:SN4-RTX:s204`) |
| **240,000** | **`rt_coerce_num2_d`** | 0 | 240,000 | 0 | ⭐ **ICON-RTX, `FREE`** |
| **240,000** | **`rt_substr`** | 0 | 240,000 | 0 | ⭐ **ICON-OWN, SCAN family** |
| 195,000 | `rt_add` | 60,000 | 120,000 | 15,000 | ARITH |
| 60,000 | `rt_mod` | 60,000 | 0 | 0 | ARITH |
| 60,000 | `rt_pl_dc_prep` | 60,000 | 0 | 0 | ⛔ RTX-7-ICN dual-entry |
| 60,000 | `rt_pl_dc_leave_γ` | 60,000 | 0 | 0 | RTX-7-ICN family |
| 60,000 | `rt_value_trail_mark` | 60,000 | 0 | 0 | unclaimed |
| 60,000 | `rt_value_trail_tidy_dead_window` | 60,000 | 0 | 0 | unclaimed |
| 15,000 | `rt_scan_enter` / `rt_scan_leave` | 0 | 15,000 ea | 0 | ICON-OWN, SCAN family |

**⭐ THE PROC-CALL PATH COSTS SIX C CALLS PER ICON PROCEDURE CALL** — `rt_pl_dc_prep`,
`rt_pl_dc_leave_γ`, `rt_value_trail_mark`, `rt_value_trail_tidy_dead_window`, plus the body's arithmetic
— each scaling exactly 1:1 with calls. **`rt_call_arr` is not among them.** This is the positive form of
the prior session's negative result and it is where Icon's call overhead actually lives.

**⭐ `rt_scan_enter`/`rt_scan_leave` ARE 16× COLDER THAN `rt_substr`** on the same scan workload
(15,000 vs 240,000): once per scan ENVIRONMENT, not once per scan OPERATION. **RTX-5-ICN as written leads
with the two cold members of its own family.** Reorder it to lead with `rt_substr`.

---

## ⛔ WHAT THIS OWES LON — ONE ARBITRATION, AND THE RULE ITSELF IS AT ISSUE

**Icon's #1 run-phase symbol, `rt_subscript_var`, belongs to SN4-RTX.** It was allocated on a *static*
near-tie (Icon 177 / SN4 195 ⇒ "tie → SN4-RTX, claimed first"). **Dynamically it is 315,000 on an Icon
list workload — 21 per iteration, exactly the workload's 20 writes + 1 read.**

⇒ **The allocation rule is written over static counts, and this ladder has now falsified static counts
three separate times** (s188, s203-ICN, and the compile-phase confound above). **RECOMMEND: amend
`RTX-CLAIMS.md`'s rule to allocate on DYNAMIC count where one exists, static only as a prior.** I have
**not** opened the symbol — it is checked out to SN4-RTX and the protocol is explicit. ⛔ **Lon's call.**

**Meanwhile ICON-RTX's own uncontested targets are hot, so the ladder is not blocked on the arbitration:**

⭐ **`rt_coerce_num2_d` VINDICATES THE LEDGER'S OWN WARNING, WORD FOR WORD.** s208 SN4 data: *"ZERO
executions in 7 SNOBOL4 benchmarks despite 56 static sites. Cold for SN4; Icon UNMEASURED — do your own
0(d)."* **Icon: 240,000.** Same symbol, opposite answer, exactly as predicted. The cross-language
transfer prohibition is now evidenced in both directions.

⚠ **BUT ITS PORTABLE FRACTION IS SMALL — DO NOT OPEN IT BLIND.** The body (`rt.c:285-294`) is a 10-line
**wrapper**: two calls to `rt_parse_num_d` plus a DT_R/DT_I select. An asm port wins the `-O0` frame
ceremony and the branch, **not the parse.** ⇒ **the real target is `rt_parse_num_d`, and it is `static`,
therefore invisible to `nm -g` and absent from the rank above.** State that expectation before porting so
a null is informative (s188 rule).

⇒ **RECOMMENDED RTX-2-ICN := `rt_substr`** — 240,000, ICON-OWN, SCAN family, **zero ownership conflict**,
and a real body rather than a wrapper. ⛔ Destination is RTX-0-RULING(b) (`.S` vs BB template), still
open, and §6 rules the SCAN family to TEMPLATE — **so RTX-2-ICN is blocked on that ruling, not on
measurement.**

---

## INSTRUMENT — `tools/rtx_icn_profile.c` (NEW)

`-finstrument-functions` on `libscrip_rt.so` via **`RT_OPT` override — no Makefile edit, no `src/` edit**
— with `__cyg_profile_func_enter` resolved to a preloaded shim, counting by address in BSS with atomic
increments, symbolized once at exit by `dladdr`.

⭐ **IT NEEDS NO SIGNATURES, WHICH IS THE POINT.** The LD_PRELOAD interposer needs one hand-written
prototype per symbol; a wrong one **compiles clean and corrupts the ABI silently** (that happened to
`rt_arg_stage` in this session's prior doc). It also only ever sees symbols someone already suspected —
**the exact bias that made the static rank wrong.** This instrument inherits neither defect and sees all
707 runtime functions.

⚠ **COUNTS ONLY, NEVER TIME.** Instrumentation inflates every body; no ratio may be quoted from this
build. ⚠ **`nm -g` DROPS `static` FUNCTIONS** — `rt_parse_num_d` is missing from the rank for this
reason, and it may be the real elephant behind `rt_coerce_num2_d`. **Widen the filter to `nm --defined-only`
without `-g` before trusting a rank as complete.** ⚠ Reported counts are whole-process; only the **delta**
is run-phase.

---

## STATE

Nothing ported, nothing claimed, no ledger row moved, `src/` clean, `.so` md5-identical to pristine.
`GOAL-ICON-RTX.md` LIVE CURSOR and the RTX-0d checkbox corrected in this session (they pointed at a rung
closed at s203-ICN and caused a duplicated measurement — see the prior doc's proposed **step 0(h)**).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
