# FINDING — FLATDISP-8: the frame base must follow the rbp PIN; SNOBOL4 was broken at HEAD too

**Session:** s197 (2026-07-27) · **SCRIP:** `8d9b8d50` → `0e008a85`
**Headline:** Icon `236/25/32` → **`250/11/32`**. SNOBOL4 crosscheck `221/219 FAIL=94` → **`295/294 FAIL=20/19`**.
**⚠ READ THIS IF YOU OWN THE SNOBOL4 OR PROLOG GOAL.** The SNOBOL4 gain was not a SNOBOL4 change.

---

## 1. The fix — one selector, five accessors

s196 closed the FLATDISP-1 dual-entry regression and left **14 residual failures, ONE class:
suspended generators**. Its next-rung note proposed gating the frame base on `flat_gen`.

Landed instead on **`emit_jmp_pin_rbp()`** — the predicate `xa_flat.cpp` ALREADY uses to decide
whether the prologue emits `mov [rsp+kt-8], rbp; mov rbp, rsp`.

⭐ **THE DEFECT WAS A DRIFT, NOT A MISSING FEATURE.** s188/s189 made `x86_fb()` return `"rsp"`
unconditionally, but `xa_flat` **kept seeding rbp** for every pinned class. So the base a
reference NAMES and the base the prologue ESTABLISHES became two decisions. `emit.h:599` already
states the rule — *"every jmp-entry gate site reads THIS, never the raw fields, so save/seed/
read/restore cannot drift apart"* — and the five accessors were simply not obeying it. Gating on
raw `flat_gen` would have re-created the same drift one class over (`flat_pat`/`flat_deep_arrival`
seed rbp but would still read rsp).

Three consequences, all in `x86_asm.h`:

1. `x86_fb()`/`x86_fb_num()`/`x86_fr32_prefix()`/`x86_fr64_prefix()` return the rbp spellings
   when pinned. **BOTH MEDIA read the one selector, so R10 holds by construction.**
2. `x86_frame_off()` returns the offset **UNCOMPENSATED** when pinned. `op_flat_disp` is the
   running rsp-depth prefix sum; **rbp does not move**, so adding it would double-count the very
   depth the pin exists to neutralize.
3. `FRQB()` suppresses its live rsp bump when pinned — a template-local `sub rsp,K` does not
   displace an rbp-relative read. (This is exactly the case the original FRQB note recorded as
   *"under the old always-seeded rbp frame the non-window read was depth-immune"*, now live again.)

**The encoder needed NOTHING.** `x86_r12_modrm`'s `b != 5` guard already spells the rbp
mod=00/RIP-relative trap correctly and `x86_frame_rex` already drops the B bit. **s189 deleted only
the SELECTION, not the arm** — so this is a re-enable, per-graph, not a rewrite.

## 2. ⚠ SNOBOL4 WAS BROKEN AT HEAD AND ITS WATERMARK HAD ABSORBED THE DAMAGE

This is the s196 Icon story repeating one language over, and it is the important part of this
session.

| suite | baseline (re-measured, unmodified HEAD, clean build) | after |
|---|---|---|
| Icon `--run` | 236 / 25 / 32 | **250 / 11 / 32** |
| SNOBOL4 m3 | 221 FAIL=94 | **295 FAIL=20** |
| SNOBOL4 m4 | 219 FAIL=94 | **294 FAIL=19** |

**+74 / +75, ZERO newly-broken in either mode.** `221/219 FAIL=94` was carried in
`GOAL-ICON-BB.md`'s watermark as the healthy SNOBOL4 number. It was not healthy — it was the
s188/s189 breakage, recorded as the new normal and then used as the comparison point for
subsequent work. `flat_pat` blobs seed rbp and were reading rsp.

⭐ **A WATERMARK MEASURED AFTER A SHARED-SPINE CHANGE RECORDS THE DAMAGE AS THE BASELINE.** s196
proved a parallel session can silently falsify another goal's watermark; this proves the falsified
number then becomes the *reference* number. Neither session was wrong to write it down. The
failure mode is structural: nothing re-derives a baseline after someone else touches the spine.

⛔ **DO NOT re-baseline SNOBOL4 against 221/219.** The number is 295/294 as of `0e008a85`.

## 3. Icon: the +14 is exactly the predicted list

`suspend_gen`, `suspend_gen_compose`, `suspend_gen_filter`, `suspend_return`, `jcon_genqueen`,
`subscript_genproc`, `jcon_coerce`, `jcon_htprep`, `jcon_level`, `jcon_meander`, `jcon_mffsol`,
`jcon_recogn`, `jcon_wordcnt`, `scan_alt` — the s196 §5 residual list, item for item, zero
regressions.

One-line repro, before → after:
`procedure upto(n); local i; i := 1; while i <= n do suspend i do i := i + 1; end`
→ was `1` + **rc=139**, now `1 2 3 4` rc=0. The generator yielded its FIRST value correctly and
died on RESUME: γ retains with rsp at the deep frontier, so every rsp-relative frame read after
`proc_upto_res` was displaced. Emitted body went 7 rbp-refs → 112.

## 4. Other languages — FAIL=0, so no regression is POSSIBLE

Prolog **189/0/0 ORACLE_MISS=0** · Raku **51/0** · Rebus **4/0** · Snocone **8/0**, all rc=0 with
the fix. A suite at FAIL=0 and SKIP=0 cannot have regressed — that is the ceiling — so these need
no separate baseline build. Recorded because `emit_jmp_pin_rbp()` includes `flat_deep_arrival`,
which is NOT Icon-specific and did warrant the check.

⚠ Prolog's pre-existing `rc=134` recursion probe (s196 §6) is NOT in this crosscheck corpus and
was not exercised. It remains unmeasured, not cleared.

## 5. DIVERGE 1 → 3 is partial improvement, not damage

New: `140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`. **Both were failing in BOTH
modes at baseline** and now pass m4 while still failing m3 — fail/fail → fail/pass. `W06_tab` is
the pre-existing one. **No program that agreed before disagrees now.** Grade DIVERGE deltas against
the per-program baseline state, not the count: a rising count can mean a mode got BETTER first.

## 6. Build discipline — the s126 lesson bit again, one layer down

The first rebuild after the edit produced a **byte-identical binary** and the repro still SEGV'd.
`x86_asm.h` is a HEADER and `make` does not track it as a dependency. `rm -rf out /tmp/si_objs`
is mandatory for any change to it.

⚠ **A second trap sits right behind it:** the emitter lives in **`out/libscrip_rt.so` (23MB)**, not
in the 182KB `scrip` driver. `strings scrip | grep 'qword ptr \[rbp'` returns 0 **whether or not
the change landed**. Verify against the `.so`.

## 7. Concurrency

`x86_asm.h` is the shared spine. SNOBOL4 and Prolog sessions were live during this one. RULES'
*"safe for CODE (different files)"* was already falsified by s196 for this exact file; this session
is the second instance and the first where the collateral was a **74-test IMPROVEMENT** — the
concurrency hazard is not only breakage, it is that a parallel session's baseline silently stops
meaning what it says.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
