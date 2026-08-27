# FINDING — N-2 item 1 LANDED: generator ζ re-homed to the RBP activation frame — and the rung's ordered work was mis-scoped a second time, because generator ζ is TWO addressing families that print identically in the `.s`

**Date:** 2026-08-27 · **Seat:** hq_P (`/home/claude_P`) · **Topic:** row `icon-n2-generator-activation-frames` (the cure) / `icon-bench-correct-zero-of-eight` (the blocked acceptance row).
**Landed:** SCRIP `e637707d`, `src/templates/x86/x86_asm.h` only, 20 insertions / 6 deletions. Gate `SCRIP_ICN_GENFRAME2` **default OFF**.
**Shared axes:** `RT_OPT=-O0` · pristine build · SCRIP `e637707d` · corpus `8e85e50d9` · oracle `/home/resources/icon-master/bin/icont`.

---

## 1. WHAT LANDED, AND THE ONE PROPERTY THAT MAKES IT SAFE

On the armed four-line witness, ζ references in the generator body `FN__gen:`…`gen_ω:` move from the RSP spine to the RBP activation frame:

| | ζ refs via `[rsp+off]` | refs via `[rbp+off]` |
|---|---|---|
| before | 8 (+1 protocol) | 3 |
| after | **1** (+1 protocol) | **10** |

⭐ **The rebase is EXACT, not approximate, and that is the whole argument for its safety.** The N-2 α carve is `push rbp; mov rbp,rsp; sub rsp,frame_total`, and **rsp does not move again between α and γ** — measured: zero pushes in the body. So `[rsp + off]` and `[rbp + off - frame_total]` are *the same address*. Verified in the emitted asm at `frame_total=96`: `[rsp+16]→[rbp-80]`, `[rsp+24]→[rbp-72]`, `[rsp+32]→[rbp-64]`, `[rsp+0]→[rbp-96]`, `[rsp+8]→[rbp-88]`.

⛔ **THIS IS NOT THE CURE AND MUST NOT BE READ AS ONE.** The frame still lives on the shared stack below the point the caller resumes to, so `bb_call_proc_staged.cpp:733`'s `lea rsp,[rax+32]` still discards it. Item 1 is the **prerequisite** that turns item 2 (re-point rbp at the heap island `e->frame`) from an emitter-wide change into a one-register change: once every ζ reference is rbp-relative, moving the frame is moving one register.

✅ **Its correctness test is therefore "nothing moved", and nothing moved:**

| control arm | result |
|---|---|
| SNOBOL4 corpus (the mandated control) | `m3 PASS=365 FAIL=0 · m4 PASS=365 FAIL=0 SKIP=0 · MISSING=0`, **script rc=0** — run twice, before and after the rebase |
| Icon smoke | m3 14/14 · m4 14/14 |
| D2 witness, gate OFF | all five `CRASH 5/5`, m3=m4, controls CORRECT — **identical to the pinned baseline** |
| D2 witness, ARMED | `suspend_single` WRONG 0/10, other four `CRASH 10/10`, controls CORRECT — **identical to the pinned baseline** |

## 2. ⛔⭐⭐ THE RUNG'S ORDERED WORK NAMED THE WRONG HALF — ζ IS TWO ADDRESSING FAMILIES, AND THEY ARE INDISTINGUISHABLE IN THE `.s`

The rung's NEXT said, concretely: *"`flat_gen` graphs need their own membership into the `xop_frame_slot` re-homing (or a parallel one) so `ZOPQ`/`ZRES` emit `RDQ("rbp", …)`."* ⛔ **Carrying that out literally would have re-homed the half that does not hold the yielded value.**

| family | reached by | rendered as | had an rbp arm? |
|---|---|---|---|
| **SPINE** | `ZRES`/`ZRESD`/`ZOPQ`/`ZOPD`/`ZLOC` → `x86_zref` | `qword ptr [rsp# + N]` (XK_RSP) | ✅ yes, via `op_xf_off` / `op_zread_xf[]` |
| **FRAME** | `FRQ`/`FR` → `x86_zop` | `qword ptr [rsp + N]` (XK_FR) | ⛔ **none, anywhere** |

⭐ **And the FR half is the one carrying the yielded value.** On the witness the literal's result descriptor lands at `[rsp+16]`/`[rsp+24]` through `bb_lit_scalar.cpp:19`'s `FRQ(_.op_off + w)` arm — **proven by elimination**, since `ZRES`'s base is 0 and could not have produced 16. The `IR_SUSPEND` box then reads exactly those two cells via `ZOPQ(0,0)`/`ZOPQ(0,8)` and writes its own at `ZRES(0)`/`ZRES(8)`.

⛔⭐ **WHY THIS SURVIVED A CAREFUL MEASUREMENT: BOTH FAMILIES PRINT THE SAME STRING.** `x86_fr64_prefix()` is the literal `"qword ptr [rsp + "` and the spine form is `"qword ptr [rsp# + "`, and the `#` is gone by the time anything is written out — both parse to the same operand kind and both appear in the `.s` as `qword ptr [rsp + N]`. So s275's `.s`-grep — *"9 of 9 ζ references emit `[rsp + off]`"* — was **correct as a count and wrong as a diagnosis**: it saw one homogeneous problem where there are two families with two different cures. ⭐ **The instrument could not have distinguished them; the distinction only exists upstream of the text.** That is the same shape as this root's `command -v icont` and "the `perf` CLI fails" errors: **a true measurement answering a narrower question than the one it was read as answering.**

⚠️ Minor correction to the same s275 line: of those 9, **8 are ζ**. The ninth, `mov rbp, qword ptr [rsp + 24]` in the resume landing, is the protocol read of record word 3 and is *correctly* rsp-relative — it must not be re-homed.

## 3. ⭐ A SIMPLER IMPLEMENTATION THAN THE ONE THE RUNG PROPOSED — AND IT AVOIDS THE s272 HAZARD ENTIRELY

The rung proposed granting `flat_gen` graphs membership in `xop_frame_slot`. That routes generators through `xop_frame_member` → `sn4_pt_opframe()` → `blob_frame_scope()` → `frame_slot_scan`, all of it **SNOBOL4-pattern machinery anchored on `IR_MATCH_BEGIN`** — and the rung's own text flags it: *"a language-blind widening here is the exact shape that cost 47 Icon programs at s272."*

✅ **Rebasing in the two leaf functions instead needs none of it** — no slot allocator, no `frame_slot_scan`, no `MATCH_BEGIN` anchoring, and **not one line of pattern machinery touched.** The whole change is `icn_gen_zeta_ft()` plus one early-return in `x86_zop` and one in `x86_zref`. It is keyed on the **consuming ζ regime** — `icn_genframe2() && _.flat_gen` — two conditions no SNOBOL4 or Prolog graph can satisfy, the first of which is default OFF, so an unarmed build is unchanged **by construction** rather than by measurement. ⭐ The SNOBOL4 board is then a genuine control arm rather than a hope, which is exactly what the SHARED-NODE VERDICT SCOPE rule asks for.

## 4. ⛔ THE REMAINING GAP, NAMED PRECISELY — ONE SLOT IS NOW WRITTEN THROUGH BOTH BASES

One ζ reference did not re-home: the **graph-α β-port seed**, emitted at `gen_α:` before the first node —
```
gen_α:   lea rax, [rip + n1_suspend_β]
         mov qword ptr [rsp + 32], rax        <- NOT re-homed
```
while the `IR_SUSPEND` box's own seed of **the same slot** now reads `mov qword ptr [rbp + -64], rax` (−96+32 = −64).

⛔⛔ **That is a split base on one cell, and it is a live hazard for item 2, not a cosmetic leftover:** the moment rbp points at the heap island, the α seed writes the **stack** and the box reads the **island**. It must be closed *before* item 2, not after.
⭐ **Not yet root-caused, and deliberately not guessed at.** What is established: it is a *different emitter* from `bb_suspend.cpp:49`'s `x86_lea_tgt("rax", X86T_TGT1) + x86("mov", FRQ(_.op_sb), "rax")` — the α form uses a plain `lea` and carries no `mov r11, <n>` node prologue, so it is not that box's output hoisted. It is not in `emit.cpp` under any `lea`+`β` grep. **Next step: instrument `icn_gen_zeta_ft()` to log `flat_gen`/`flat_frame_bytes` per call and identify the caller — one 40 s build cycle settles it.** The leading hypothesis, untested, is that the seed is emitted while the per-graph frame size is not yet set, so `ft` is 0 there.

## 5. TWO PROCESS NOTES WORTH MORE THAN THE CODE

- ⛔ **`board rc=0` was a lie, and CLAUDE.md predicted it.** The first re-prove printed `⛔ GATE REFUSES: 2 hardcoded corpus path(s) no longer resolve` and *also* `board rc=0`, because the run was piped through `tail` — so `$?` was **tail's** status, not the script's. Re-run as `out=$(...); rc=$?` it reports honestly. **Read the verdict line, never a pipeline's `$?`.**
- ⭐ **The REFUSE itself was correct and the cause was the documented one: a stale `corpus` checkout.** SCRIP `f7af8606` added `crosscheck/rung10` to the suite family list; the corpus commit carrying `rung10.{sno,ref}` had not been pulled. `git pull` in `corpus/` cleared it and the board returned 365/365. ⭐ **The denominator stayed 365 across a suite-list change** — more evidence that `FAIL=0 / SKIP=0 / MISSING=0` is the invariant and the total is not.
- ⚠️ **s274's armed-m4 intermittency REPRODUCES and stands unretracted.** Armed `suspend_single` read m4 `crash 1/10` with `m3⛔≠m4` on the post-rebase tree, having read `0/10` on the pre-rebase tree in this same session. Across sessions the rate now reads **2/10 (s274) · 0/10 (s275) · 0/10 then 1/10 (s276)**. ⛔ It **predates this change** — s274 measured it before the change existed — so it is not attributable here; and a 10-rep sample cannot characterize a ~10% rate in either direction. A 50-rep characterization run is recorded in the task LEDGER.
