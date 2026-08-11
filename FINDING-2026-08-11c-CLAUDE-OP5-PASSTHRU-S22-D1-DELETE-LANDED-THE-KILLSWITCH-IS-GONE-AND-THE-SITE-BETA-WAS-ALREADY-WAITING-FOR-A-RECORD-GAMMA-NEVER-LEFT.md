# FINDING 2026-08-11c — s22 (Opus 5) — PASSTHRU/DEL-T1

## ⭐⭐⭐ HEADLINE
**D-1 DELETE LANDED PHYSICALLY (`855a12a5`) AND THE `SCRIP_WREG` KILLSWITCH IS GONE WITH IT — THERE IS NO OFF ARM LEFT TO FALL BACK TO.** Then W-MAP(3) landed (`7c903000`): **the site's β was ALREADY `jmp qword ptr [rsp+0]` with a zero-guard, waiting for a resume record that γ never left.** A bare `jmp r10` meant the site jumped through whatever the granted pad held. That is the SIGSEGV class, and it was a *missing* emission, not a wrong one.

## WHAT WAS PHYSICALLY DELETED (`855a12a5`, one isolated commit, 130 deletions / 3 files)
Lon, verbatim: *"the body of garbage asm code there … that code will be gone … SCRIP will no longer output that garbage."* Deleted, no predicate, no env gate:
- α shim (BLOB-GRANT): `sub rsp,kt` carve + wire spill + the 6-instruction `g_zctx` push
- resume-slot store (`mov [rbp+K],rax` — the phantom-rbp scribble s19 convicted) + its init arm
- both scan blocks, the `scanhit`/`scanfail` trampolines, the `_attempt` label, and the `SCRIP_SCAN_OFF` hatch
- CLASS D γ/ω `g_zctx` exits → γ `jmp r10`, ω `jmp r11`, unconditionally
- the `flat_pat` res stub (the r10/r11-scratch landmine — **deleted before it could arm**)
- `wreg_on()` itself: definition, declaration, all 7 gate sites
**Keepers untouched and verified:** MAIN bracket · AB activation · FRAMED enter/leave · Icon zframe · `flat_lcl_proc` · gen-proc resume.
`claws5-match.s` at HEAD: `proc_PAT$0_α:` falls straight into the pattern spine. Zero carve, zero `g_zctx`, zero stubs.

## ⛔⭐⭐ THE FIX-FORWARD FACT THAT COST THE LEAST AND PAID THE MOST
`bb_match_defer.cpp:169` — the site's β is `x86_jmp_mem("rsp", 0)`, guarded: read `[rsp+0]`, zero ⇒ `zrelease` + ω, non-zero ⇒ `jmp rax`. **The comment already says it: *"a real γ-record resumes the blob as ever."*** The site never needed an edit. The blob owed a record and stopped leaving one the moment the carve died.
**W-MAP(3) as landed:** γ = `sub rsp,8 · push r11 · push r10 · lea rax,[rip+res] · push rax · jmp r10` (32B, 16-aligned, `[rsp+0]`=res) · res = `mov r10,[rsp+8] · mov r11,[rsp+16] · add rsp,32` → falls into β. **The wires are saved PER-ACTIVATION ON THE SPINE** — this is the s14 routing question answered by construction, not by ruling: a flat global cell cannot serve a LIFO discipline, the spine can, and r10/r11 are **destinations only** in res (never scratch — the landmine cannot arm).
**LIFO geometry verified:** interior carves sit ABOVE the record (`[rsp+32…]`), so res drops 32B and resumes an interior whose cells are intact.

## MEASURED, BY SET, crosscheck/patterns 122, m3, same container
| | PASS | SEGV | HANG | DIFF |
|---|---|---|---|---|
| after D-1 delete | 73 | 26 | 12 | 11 |
| after W-MAP(3) | **76** | 28 | **6** | 12 |
⭐ **The delete reproduces s19/s20's ON arm almost exactly (26/11-12/11)** — as it must: deleting the OFF arm leaves the ON arm. s20's numbers travel a third time.
⛔ **W-MAP(3) IS A PARTIAL, NOT A CURE, AND I AM NOT CLAIMING THE SEGV CLASS IS CLOSED.** Net +3 PASS and hangs halved; SEGV +2 and DIFF +1 mean it also moved programs *between* failure classes. **The per-name delta was NOT computed** (context ran out) — the next seat must diff by name before billing any of it.

## ⛔ TWO INSTRUMENT CORRECTIONS (both caught on myself)
**(a) MY FIRST BLOB-INTERIOR ATTRIBUTION WAS WRONG AND I PUBLISHED THE CORRECTION BEFORE ACTING ON IT.** A crude `awk` marking "in blob" from the first `proc_PAT$*_α` to `main_α` swept whole `proc_LBL__*` regions in. It named `json.s` (32), `json-match*.s` (10 each), `claws5.s` (4), `calculator-1-match-fence.s` (4). **Those counts are void.** The census script's own rule — class = last top-level label seen — is the only correct attributor.
**(b) ⛔⭐ THE PAT-BLOB CENSUS ROSE AFTER W-MAP(3) AND IT IS AN ATTRIBUTION ARTIFACT, NOT A REGRESSION.** demo PAT-BLOB est 16→28, crosscheck 0→8. **The record pushes `r10`/`r11`/`rax` — it never pushes `rbp` and never writes `rbp`.** Defining `_res` for `flat_pat` blobs *extends the PAT$-labelled region* over following `_wire_stub` code that does push rbp. **A census that classifies by nearest preceding label cannot distinguish a new establishment from a moved label.** Do not read these two numbers as T1 debt.

## ⛔⭐⭐ THE RESIDUAL T1 SUB-CLASS IS NOT WHAT LON POINTED AT — AND IT IS NAMED
The blobs still establishing rbp are the ones taking `_wire_stub`, not `_blob_wire`: `_wire_stub = (flat_jmp_entry && g_flat_frame_floor > 0) || …`, and `_blob_wire = !_wire_stub && …`. **A PAT$ blob with a non-zero frame floor never reaches the pass-thru arm at all** — it takes `bb_glue_wire_γ()` and pushes rbp. Witness at HEAD: `json.s` `proc_PAT$9_γ` = `push rbp · lea rax,[rip+res] · push rax · mov rax,[rbp+424] · mov rbp,[rbp+440] · jmp rax`. These are the frame-floor-bearing blobs; **their frames are still keepers-by-accident, and PT-2b's retraction ("hostile-name BLOBS are keepers, their FRAMES are not") applies to them unchanged.** Killing this needs the floor's locals re-homed to the spine — a rung, not a drive-by.

## NEXT SEAT, IN ORDER
1. ✅ **BY-NAME DELTA COMPUTED (this session, after the above was written) — W-MAP(3) IS 4 REPAIRED / 1 BROKEN, NOT A WASH.** Repaired: `119_pat_arbno_of_fence_via_var_via_outer` · `129_pat_arbno_star_var_fence_with_alts` · `148_pat_arbno_star_var_fence_short` · `149_pat_arbno_star_var_fence_outer_pre_match` — **one coherent class: ARBNO × FENCE × deferred `*var`, i.e. exactly suspension-and-resume through a deferred reference, which is what the record exists to carry.** The gross SEGV/DIFF rises were reclassified survivors, as suspected. Broken: **`181_pat_arbno_defer_tail_stressors` only.**
1b. ⛔⭐⭐ **`181` IS CONVICTED TO A SPECIFIC MECHANISM, NOT LEFT AS "a SEGV".** It prints `T1 MATCH` (correct) then faults. T1 is a SUCCEEDING `ARBNO(*P)`; **T2 (`S2="abcab"`, expected `T2 NOMATCH`) is the EXHAUSTION path.** So the success path is right and the fail path is not. **HYPOTHESIS (falsifiable, cheap): γ pushes 32B PER BLOB ENTRY, and `ARBNO(*P)` enters the blob once PER ITERATION — so N iterations leave N records on the spine, while the fail-cascade/ω unwind consumes NONE of them.** rsp then desyncs by 32×N at the ARBNO ω edge and `jmp r11` transfers wild. ⭐ This is precisely s20's SCRUTINY 2 probe re-aimed: **watch rsp at the ARBNO ω edge per retry; drift of ONE RECORD WIDTH (32B) per iteration convicts, zero drift exonerates and routes it elsewhere.** ⛔ **The record is per-ENTRY but the consumer is per-SUSPENSION — those are not the same count under ARBNO, and that asymmetry is the thing to fix, not the record size.** (Lon s20 routing: "you own the ARBNO.")
2. **The 6 remaining HANGs** — WREG-4's retry-advance. ⛔ **The unanchored scan-retry loop was DELETED with the scan blocks**: an unanchored pattern now has no advance-and-retry path anywhere. Manual p.204 step 6 requires it (&ANCHOR=0 ⇒ advance start cursor, go to step 2). **That stub is now unpaid at the SITE and is a correctness gap, not an optimisation.**
3. **`_wire_stub` blobs** (§ above) — the last T1 sub-class.
4. m4 column untouched this session (m3 only). Regen ×4 paid twice, same session, both commits.
5. `n32b` / `iso_nest` from s21 remain open; 2-way monitor first, per RULES.

## ⛔⭐⭐⭐ LATE-SESSION: MY OWN `181` HYPOTHESIS IS FALSIFIED AND THE REAL ROOT CAUSE IS NAMED — THE RECORD COLLIDES WITH ARBNO'S RSP-RELATIVE CURSOR CELLS
**The bounded-iteration probe (s20 SCRUTINY 2's instrument, NOT gdb) killed the accumulation theory in one run.** Minimal witness `/tmp/it.sno`, `P = "a"`, three `POS(0) ARBNO(*P) RPOS(0)` tests over `"b"` / `"ab"` / `"aaab"`. **sbl oracle: `T1 NOMATCH · T2 NOMATCH · T3 NOMATCH · DONE`. SCRIP m3: `T1 NOMATCH` then SIGSEGV at T2.**
- **T1 (`"b"`) has ZERO successful blob entries** — the blob is entered, `P` fails, ω fires, NO record is ever pushed. **It passes.**
- **T2 (`"ab"`) has EXACTLY ONE successful entry** — `P` matches `"a"`, γ fires, ONE record is pushed. **It faults.**
⛔ **THE TRIGGER IS THE FIRST RECORD, NOT N OF THEM. "32×N drift" was wrong and is retracted; do not spend the ARBNO ω rsp-drift-per-retry probe on it.**

**ROOT CAUSE, CONFIRMED IN SHIPPED INSTRUCTIONS:** `n9_match_arbno_α` = `mov dword ptr [rsp + 0], r14d` · `mov dword ptr [rsp + 4], r14d`. **ARBNO addresses its OWN cursor cells RSP-RELATIVE at fixed small offsets** (s21's cursor already recorded the layout: `+0` DELTA0, `+4` yield, 16B cell). **γ's 32B record is pushed onto that SAME spine.** After one record exists, ARBNO's `[rsp+0]` is no longer DELTA0 — **it is the record's res-landing address**, so COMPARE 1 / COMPARE 2 compare a cursor against a code pointer and control goes wild.
⭐ **THIS IS THE FILE'S OWN SLIDING-OFFSET CLASS, NOT A NEW ONE** ("the head reads must SUBTRACT it not add it", C9 splice: "FRQ reads miss by the replacement subtree depth"). **An interior box that reads rsp-relative cannot tolerate ANYTHING pushed between its carve and its reads.**

**THEREFORE THE FIX IS NOT THE RECORD'S SIZE OR LAYOUT — IT IS THE RECORD'S PLACE.** Three candidates, in order of cheapness, for the next seat (⛔ none attempted — deliberately not landed at 92% context, per the standing "no deletion/edit at end-of-context" law):
1. **Push the record BELOW the interior frontier** so no interior box's rsp-relative window is displaced — i.e. γ carves the record where the blob's OWN cells already end, and the site's β reads it at a known offset rather than `[rsp+0]`. (Costs a site-side offset; the site is currently `jmp [rsp+0]`.)
2. **Have ARBNO speak `op_flat_disp` / the ONE selector instead of raw `[rsp+K]`** — the same cure the file applied when `flat_pat` left `emit_jmp_pin_rbp()`. Structurally right, wider blast radius.
3. Record in a per-activation slot carved at blob entry (NOT a flat global — s14) rather than pushed.
⛔ **DO NOT "FIX" THIS BY SHRINKING THE RECORD.** Any non-zero push reproduces it; 8 bytes collides exactly as 32 does.

## FINGERPRINT
SCRIP `855a12a5` (D-1) → `7c903000` (W-MAP 3) + 8 regen commits · corpus regen ×4 (both rungs) · `.github` this commit. ⛔ **NOTHING PUSHED — credential requested in chat, session held open at the ask.**
