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


---

## 8. ⭐ POST-REBASE: THE FIX IS CROSS-LANGUAGE, AND THE s196 PROPOSAL WAS INSUFFICIENT

Rebased onto the parallel sessions' pushes (SCRIP `84ea9f85` SN4-SCANBASE, `.github` `3360c13c`
PROLOG s157) and re-measured everything. **All three languages were broken by the SAME drift and
three separate sessions were independently chasing it.**

### A/B — gating on raw `flat_gen` (what s196 proposed) is NOT enough

| variant | Icon | SNOBOL4 m3/m4 | Prolog rung (x3 arms) | rbp ratchet |
|---|---|---|---|---|
| baseline (`84ea9f85`) | 236 | 221 / 219 FAIL=94 | 120 FAIL=44 | 113 = 113 PASS |
| **A — `flat_gen` only** | **239** (+3) | 221 / 219 (+0) | not run | 113 PASS |
| **B — `emit_jmp_pin_rbp()`** ⬅ LANDED | **250** (+14) | **295 / 294** (+74/+75) | **164 FAIL=0** (+44) | 1100 vs 113 FAIL |

⭐ **Raw `flat_gen` closes only 3 of the 14.** The other 11 need `flat_pat` / `flat_deep_arrival`
too — Icon scanning programs (`scan_alt`, `jcon_recogn`) go through pat blobs. Had this session
implemented the s196 next-rung note literally, it would have measured +3, concluded the class was
harder than believed, and missed a 132-test cross-language fix. **The predicate that repairs the
drift is the predicate that CAUSES the pin — nothing narrower.**

### Prolog: `120 FAIL=44` → `164 FAIL=0`, all three arms

Measured at the parent and at the fix, clean builds both times. This is the regression
`GOAL-PROLOG-BB` s157 is bisecting — its own cursor names `62aaf9ff` BAD, the same FLATDISP range.
Prolog's crosscheck was ALREADY green (189/0) and hid it; the rung suite is where it shows.

### SNOBOL4's own s198 note describes this defect

`a9d5a189`: *"stored-pattern segv localized (bb_match_release RSP cross-box read, dynamic 16-byte
depth mismatch, fix-attempt reverted)"* — an RSP cross-box read with a dynamic depth mismatch IS
this defect. That fix-attempt was reverted; this one is the root-cause form.

## 9. ⛔ OPEN — NOT MINE TO DECIDE: `test_gate_rbp_census_ratchet.sh`

`84ea9f85` tightened the ratchet 119 → 113. Variant B measures **NET=1100**. **GATE FAILS.**

This is a real conflict of DIRECTION, not a bug in either change. The SNOBOL4 FC-conversion ladder
drives rbp references DOWN; restoring the pin drives them UP for `flat_pat`. The honest reading:
**the 113 baseline was achieved while the configuration was broken** — some of that rbp→rsp
conversion moved reads onto a register that is NOT the base for a suspending activation, which is
exactly why 74 SNOBOL4 tests were failing. Optimizing toward 113 was optimizing a broken frame.

⛔ **The ratchet belongs to the SNOBOL4 goal. A session must not silently re-baseline another
session's gate.** Options for Lon: (a) re-baseline the ratchet and keep +132 tests; (b) narrow to
`flat_gen` and forfeit +74 SNOBOL4 / +44 Prolog / 11 of 14 Icon; (c) split the ratchet so
`flat_pat` graphs are counted separately from FC-converted boxes. **Recommend (a) or (c)** —
correctness before a codegen-quality metric — but it is Lon's call.

⚠ Note also that rbp-relative addressing is not inherently slower than rsp-relative; the FC ladder's
real object was the granted-window LIFO discipline (`fc_leaf`), and `test_gate_fc_no_residual_rbp.sh`
is STILL GREEN under variant B. The ratchet is the only red.


---

## 10. ⛔ MEASURED INTERACTION: SN4 DEFER-STAR (`9b19bb5a`) COSTS 27 TESTS ONCE THE PIN IS LOAD-BEARING

Rebased again onto `9b19bb5a` *"SN4 DEFER-STAR (s199): deep-arrival narrowed to star-sourced defer
only -- rbp census 113 -> 48"*. It touches NEITHER `x86_asm.h` NOR `emit.h` (no textual conflict);
it narrows `flat_deep_arrival` in `emit.cpp`/`lower_snobol4.c` — which FEEDS `emit_jmp_pin_rbp()`,
which feeds this session's selector.

**Same FLATDISP-8 commit, two bases, clean builds both:**

| base | Icon | Prolog rung | SNOBOL4 m3/m4 |
|---|---|---|---|
| on `84ea9f85` (pre-DEFER-STAR) | 250 | 164/0 | **295 / 294** FAIL=20/19 |
| on `9b19bb5a` (post-DEFER-STAR) | 250 | 164/0 | **268 / 267** FAIL=47/46 |

⭐ **DEFER-STAR costs 27/27 SNOBOL4 tests — but ONLY in combination.** Neither change is wrong
alone. The premise *"deep arrival can be narrowed to star-sourced defer only"* was measured on a
base where `x86_fb()` was unconditionally rsp, so the pin affected NOTHING but a dead save/seed
pair — narrowing it looked free (census 113→48) because it WAS free there. Under FLATDISP-8 the pin
is **load-bearing for addressing**: narrowing it puts genuinely deep-arriving graphs back on an rsp
base that is not their frame base.

⚠ **THIS IS THE CONCURRENCY HAZARD IN ITS EXACT FORM, AND IT IS NOT DETECTABLE BY EITHER SESSION
ALONE.** No file conflicts. Both sessions' own suites stay green in their own trees. The loss
appears only when the two land together, because one session changed the MEANING of a predicate the
other session started depending on mid-flight. Grepping for file overlap would not have caught it.

Combination is still a large net win over the true baseline (SNOBOL4 221/219 → 268/267, +47/+48;
Icon +14; Prolog +44). **Recommend the SNOBOL4 session re-derive DEFER-STAR's narrowing ON TOP OF
FLATDISP-8** — the 27 are the graphs whose deep arrival is real; the census target should be
re-established against a correct frame, not the broken one. ⛔ Lon's call.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
