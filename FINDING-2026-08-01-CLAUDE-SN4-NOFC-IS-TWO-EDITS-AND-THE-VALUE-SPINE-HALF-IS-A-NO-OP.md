# FINDING — s22r — `SCRIP_NOFC` IS TWO EDITS IN ONE ENV VAR, THE VALUE-SPINE HALF IS A VERIFIED NO-OP, AND THE NUMBERS THAT DEFERRED THE FLIP FOR TWO SESSIONS DIED WITH `xa_flat_prologue`

**Date:** 2026-08-01 · **Goal:** GOAL-SNOBOL4-BB.md · **Session:** s22r
**Commits:** SCRIP `f6ee055` (NOFC-ONE) · `259b9cd` (NOFC-DEFAULT-ON) · `b0dc0a8` (feature artifacts) · corpus `620b974` (benchmark artifacts) · `04ee04b` (demo artifacts)
**Lon directive:** *"Climb the ladder to NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. We allocate on ALPHA. We free on OMEGA. We whack at completion or FENCE checkpoint or other known sync point. We use dynamic glue for one-shot and pass-through access to completed BB graphs which have one entry and one exit."*

---

## RESULT

**The non-popping ζ spine is now the default regime.** Killswitch is `SCRIP_NOFC=0`.

Crosscheck 317, one binary, `setarch -R`, both modes:

| Regime | m3 | m4 | DIVERGE |
|---|---|---|---|
| old default | 199/118 | 186/130/1 | 13 |
| **new default (NOFC on)** | **204/113** | **188/128/1** | **16** |
| `SCRIP_NOFC=0` (killswitch) | 199/118 | 186/130/1 | 13 |

**Fixes 5 in m3** — `063_pat_fence_fn_optional`, `064_pat_fence_fn_capture`, `065_pat_fence_fn_decimal`, `116_pat_arbno_of_fence_inline`, `156_pat_cap_alt_abandon_pop` — **and 2 in m4** (`116`, `156`). **Breaks ZERO in either mode**, established by set diff, not by count. The +3 DIVERGE is arithmetic: three of the five m3 fixes have no m4 twin yet.

---

## THE FINDING — ONE ENV VAR, TWO INDEPENDENT EDITS, AND ONE OF THEM DOES NOTHING

`SCRIP_NOFC` has always gated two structurally unrelated things:

- **(a) the VALUE-SPINE half** — the `fc_geom` vlit grant suppression, `zeta_storage.c:730`. The producer half of the popping `vfc`/`vfcb`/`vfcc` read that the non-popping spine exists to replace.
- **(b) the CARVE half** — the ZW-1 universal carve suppression, `emit.cpp:820`. Takes the match family off its self-allocated `zls` extent.

`SCRIP_NOFC_CARVE=1` restores (b) while leaving (a) suppressed. That third regime had never been run. It is decisive:

> **`SCRIP_NOFC=1` + `SCRIP_NOFC_CARVE=1` is IDENTICAL BY SET to the old default, in BOTH modes.**

Therefore **(a) is a verified no-op at HEAD**. The reason is already recorded elsewhere in the goal file and simply had not been connected to this switch: *the value spine is fully ZD-armed*. Armed nodes are guarded by `!op_zres` and never reach `fc_geom`'s grant at all, so suppressing the grant for unarmed value nodes changes nothing — **there are no unarmed value nodes left.**

**100% of NOFC's delta is (b).**

⛔ **This RETIRES s22l-B's stated live question.** It wrote: *"THE LIVE QUESTION IS NOT 'SHOULD NOFC BE THE DEFAULT' — it is WHICH NODE KINDS' CARVE HELPS AND WHICH HURTS, and that is a per-kind bisect nobody has run."* For the whole-graph carve the answer is now measured: **it helps none and hurts five.** Do not spend a rung on that bisect.

---

## WHY EVERY NUMBER THAT DEFERRED THIS FLIP WAS STALE — AND THE GENERAL LESSON

s22l measured NOFC at **+32/+33 programs, costing 2**. s22l-B confirmed the trade and left the flip explicitly as a Lon ruling. Both were measured **while `xa_flat_prologue` still carved a whole-graph frame.**

Suppressing the ZW-1 carve took the match family off its self-allocated `zls` extent and back **onto a frame that still existed**. **s22n deleted that frame.** Both sides of the trade lost their premise simultaneously:

- the **win** collapsed 33 → 5, because the fallback those programs relied on is gone;
- the **cost** went 2 → 0 — `143_pat_regex_quantified_class` and `164_pat_arbno_nested` now fail in the default regime too, so they are **no longer NOFC's debt**.

⚠ **THE GENERAL LESSON, and it is the same shape as the STALE-ORIENTATION rule in RULES.md:** *a measurement's CONCLUSION expires when its SUBSTRATE is deleted, and nothing in the file marks it expired.* Both notes still read as live guidance eight sessions later, in a file whose own head rung was already known-falsified. **When a rung deletes a mechanism, the deleting session owes a sweep of every prior measurement that mechanism underwrote** — otherwise the next session inherits confident numbers about a world that no longer exists.

---

## THE LANDMINE DEFUSED FIRST — "ONE AUTHORITY" WAS A CLAIM, NOT A FACT

s22l declared `zc_nofc()` **"THE ONE AUTHORITY"** for the FC killswitch and moved the policy into `zeta_storage.c`, explicitly citing the s22k ZD-K *"spelled three times"* law.

**The three template-local `nofc()` copies survived it** — `bb_assign_global.cpp:14`, `bb_binop_concat_slot.cpp:17`, `bb_binop_arith.cpp:26` — each still carrying its **own `getenv("SCRIP_NOFC")`**. Four independent reads of one switch, agreeing only by coincidence of polarity.

**Flipping `zc_nofc`'s default alone would have re-armed, in three templates at once, the exact producer/consumer asymmetry s22l had just finished diagnosing:** producer suppressed, consumers still reading the old polarity. The regression would have looked like the flip failing.

Sequence taken instead: collapse to one delegating authority **first** (`f6ee055`), prove it **TRANSPARENT** (all four fail sets diff IDENTICAL against pre-collapse, both regimes), and only then flip. `getenv("SCRIP_NOFC")` is now **1 site tree-wide, was 4**.

⭐ **THE LAW: "one authority" is a claim ABOUT THE SOURCE, and it is greppable in one command. Verify it before relying on it.** The ZD-K law was declared closed one session before its own instance survived in three files.

⚠ **Linkage trap, recorded so the next session does not re-derive it:** `zeta_storage.c` is compiled as **C++ in the `scrip` driver** (hence `emit.cpp`'s plain `extern int zc_nofc(void);` links) and as **C in `libscrip_rt.so`**. The templates compile into **both**. The only spelling that resolves in both is a **file-scope** `extern "C" int zc_nofc(void);` — block-scope `extern "C"` is a syntax error, and plain `extern` fails the `.so` link.

---

## ⚠ THE PERFORMANCE ARGUMENT IS UNMEASURABLE HERE — NOT CONFIRMED, NOT FALSIFIED

s22l-B attached a performance argument to the flip: *"the pops were costing 20–48%"* — roman 554→287 ms, pattern_bt 119→74, pattern_bt_deep 1612→1184, string_manip 2301→1850, var_access 290→232, op_dispatch 32→25.

**At HEAD this cannot be measured in this container, because within-regime variance exceeds the claimed between-regime effect:**

| program | regime | three runs (ms) |
|---|---|---|
| `string_manip` | `SCRIP_NOFC=0` | **1861 / 3831 / 1828** |
| `string_manip` | `SCRIP_NOFC=1` | 3187 / 1857 / 3696 |
| `table_access` | `SCRIP_NOFC=1` | **5252 / 1411 / 1622** |
| `table_access` | `SCRIP_NOFC=0` | 1398 / 1568 / 1439 |

A single first run per arm showed `table_access` at 4744 vs 1382 ms and **looked like a 3.4× slowdown caused by the flip.** It was cold-cache noise. I had drafted that as a regression before the repeat falsified it.

⭐ **INSTRUMENT LAW — the timing twin of s22l's ASLR law: NEVER report a SCRIP timing delta from one run per arm. Three runs minimum, report the spread, and if the within-arm spread covers the between-arm delta, the honest answer is UNMEASURABLE.** The flip therefore stands on its **correctness** measurement alone, which is deterministic, ASLR-off, and set-diffed.

Separately: **`roman`, `pattern_bt` and `pattern_bt_deep` — three of the programs s22l-B quoted by name — now crash rc=139 in BOTH regimes.** Those figures cannot be reproduced at all.

RT_OPT was **`-O0`** (the default; O2-DIRECTED-ONLY honored, no `-O1`/`-O2` used anywhere this session).

---

## ⚠ 8 OF 21 BENCHMARKS ARE BROKEN AT HEAD, IN BOTH REGIMES

Independent of this rung, mode-3, `setarch -R`:

- **rc=139 (SIGSEGV):** `eval_fixed`, `func_call`, `func_call_overhead`, `pattern_bt`, `pattern_bt_deep`
- **rc=1:** `fibonacci`, `roman`
- **60s timeout:** `eval_dynamic`

**The benchmark rail is not a usable performance instrument until these are fixed**, and any past session quoting benchmark milliseconds without stating `rc` was quoting the runtime of a crash.

---

## WHAT THIS RUNG DID *NOT* TOUCH

The **~1054 unarmed `FR`/`FRQ`/`FRQB` reader sites**. s22q proved they write through live process state (`envp`), and that ~76 of m4's 130 failures are that one corruption class (`max_rsp_off` > 344B headroom). **NOFC-default-on does not convert a single one of them.** It removes a *customer* of the carve; it does not convert a *reader*. That remains the whole game, and per THE MODEL the metric is the monotone emptying of the >344 bucket.

---

## NEXT — ORDERED

1. ⭐⭐⭐ Re-run s22q's static triage instrument (`max_rsp_off` vs the 344B headroom) at the new default; confirm the >344 bucket is unmoved and use it as the CARVE-ERAD progress metric.
2. ⭐⭐ **DYNAMIC GLUE / THE DYNAMIC BOX** — `α: jmp <supplied entry>` / `β: jmp <caller landing>`, FLAT and FRAMED flavors, replacing `bb_pat_build.cpp`'s emitter-mode reconfiguration. Dissolves family B (`1016_eval`, `1019_eval_string`, `1020`/`1021`, `214`/`215_indirect_goto`). ⚠ Lon's open question unsettled: the discriminator may be RELEASING vs NON-RELEASING rather than flat vs framed.
3. ⭐ **WHACK AT FENCE CHECKPOINT.** The fail set is dominated by `pat_fence_*`. SPITBOL semantics support this directly — manual Ch.18 makes the match a pushdown stack of (alternative, cursor) pairs, and `FENCE(pattern)` (p.222) specifies that backup through it does **not** abort the match; alternatives *inside* the fenced pattern simply are not examined when the scanner backs up. That is a **discard-to-checkpoint**, which is exactly what a whack is.
4. JOIN-POINT RULE still unstated — `δ_out` is well-defined only if every path into a box arrives at the same accumulated depth; the FAIL edge from deep inside a pattern is unnamed.
5. TREEBANK H11 `Pop_list` RSP imbalance — s22q reframed it as possibly a PARITY question rather than release-accounting.
