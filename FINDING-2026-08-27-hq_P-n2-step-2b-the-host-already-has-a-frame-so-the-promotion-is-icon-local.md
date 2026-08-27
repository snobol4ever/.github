# FINDING — N-2 item 2 step 2b: the host ALREADY has an activation frame, so the promotion is Icon-local, not shared-node

**hq_P, 2026-08-27 · SCRIP `150767ae1` · isolated checkout (the seat root had up to FOUR concurrent builds)**

## ⭐⭐ THE HEADLINE: THE ROW'S OWN RISK ASSESSMENT IS REFUTED BY MEASUREMENT

Step 2b's brief names two live traps. **Trap (i) does not hold for the canonical host, and it was the one carrying all the risk.** Verbatim, the brief:

> **`x86_main_prologue()` RETURNS AN EMPTY STRING** (`x86_asm.h:1784`, gutted by the RBP-ERADICATION wave) and `bb_glue_framed_enter()` is a bare `sub rsp,…`. The host in the canonical witness (`main`) has **no frame machinery to extend**, and `grep -c rbp` over all of `main` is **0**. Adding `push rbp; mov rbp,rsp` there is a **SHARED-NODE change touching every frontend's glue/main path** — boards owed are SNOBOL4 + Icon + Prolog + Snocone.

Both halves of the premise are true in isolation and the conclusion drawn from them is still wrong. **`main` never reaches the glue path at all.** `g_glue_o_sup` (`emit.cpp:2869`) suppresses the glue enter for any graph without `emit_rec_pin()`, which is exactly this host. It reaches the **`flat_lcl_proc` arm** (`emit.cpp:2831`) instead, and that arm **already carves a real per-graph activation frame**:

```
main_α:  sub rsp, 144
         mov rdi, rsp
         mov esi, 0 ; mov edx, 0
         call rt_icn_zframe_args_install@PLT
```

⭐ **So the host frame EXISTS and step 2b EXTENDS it — 144 → 240, exactly the callee's measured 96 bytes.** `x86_main_prologue()` and `bb_glue_framed_enter()` were never touched. The arm is gated on `flat_lcl_proc` and the reservation on `icn_genframe2()` (default OFF), so the blast radius is **Icon-only by construction**.

⛔ **WHY THE BRIEF GOT IT WRONG, AND IT IS THE REUSABLE PART: IT ASKED WHERE THE FRAME MACHINERY *IS DEFINED* AND READ THE ANSWER AS WHERE THE HOST *GOES*.** `x86_main_prologue()` really is empty; `bb_glue_framed_enter()` really is a bare `sub rsp`. Both facts are about a path this host does not take. This is `RULES.md:107` shape — the same class as the `command -v` oracle probe: **a correct instrument answering a narrower question than the one it was read as answering, with no way to say so.** The cure is the same: ask the compiler what it EMITS (`--compile`, ASM-DIFF-FIRST), never the source what it COULD emit.

## THE MECHANISM, AND WHY NOTHING ELSE MOVES

The reserved region goes at the **TOP** of the frame, `[old_frame_total, new_frame_total)`. Every ζ slot in the graph is addressed **bottom-relative** as `[rsp + off]` with `off < old_frame_total`, so growing the carve upward leaves every existing offset spelled exactly as before. **No `op_zdepth` threading and no constant-offset rebase** — which is what trap (ii) (the host's rsp moves, so a constant rebase is wrong-by-construction) was warning against. Trap (ii) is real; this shape simply never incurs it.

- **Forward reference reserves NOTHING and says so out loud.** Step 1 measured that a host which is itself a proc calling a generator declared later is not yet registered. Reading that as 0 bytes would give a carve **silently too small** — the class ceo refused worst-case reservation over — so the whole host is declined, loudly.
- **SUM, not max**: two generators live at once in one host each need their own region.

## MEASURED

| instrument | result |
|---|---|
| unarmed `.s` byte-identity, pre vs post | **31/31 identical** across Icon (12) · SNOBOL4 (5) · Prolog (8) · Snocone (6) |
| SNOBOL4 board (blocking set) | **m3 615/615 · m4 615/615 · FAIL=0 SKIP=0 MISSING=0**, rc=0 |
| Icon rungs | PASS=247 FAIL=15 BADEXIT=1 XFAIL=30 MISSING=2 TOTAL=293 |
| Snocone smoke | 5/5 · **Prolog smoke** 4/5 (pre-existing) |
| armed host carve | `sub rsp,144` → `sub rsp,240` (= callee's 96) |

⭐ Unarmed identity is **by construction**, not merely by sample: `icn_genframe2()` is default OFF, so `icn_gen_host_reserve()` returns 0 before scanning and the carve is untouched. The 31-program sweep confirms it empirically.

## ⛔ WHAT STEP 2b DOES *NOT* DO — AND A SAMPLING TRAP I WALKED INTO AND BACK OUT OF

**The armed D2-suspend set is UNCHANGED.** That is expected: nothing CONSUMES the reserved region until steps 3–4.

⛔⭐ **I NEARLY REPORTED AN IMPROVEMENT THAT WAS A LUCKY SAMPLE.** At the row's default `REPS=5`, `suspend_single` moved from `m3=CRASH (1/5), m4=WRONG, m3⛔≠m4` to `m3=WRONG, m4=WRONG, m3=m4` — a vanished crash *and* the restored m3≡m4 design invariant. Both readings evaporated at `REPS=20`:

| arm | `suspend_single` @ REPS=20 |
|---|---|
| baseline (pre-2b) | m3=WRONG (crash **0/20**) · m4=CRASH (crash **1/20**) · m3⛔≠m4 |
| post-2b | m3=CRASH (crash **1/20**) · m4=CRASH (crash **2/20**) · m3=m4 |

**1 crash event versus 3, on a witness whose measured rate across seven independent samples is 0/10, 1/10, 2/10, 0/5, 1/5, 1/20, 2/20.** No improvement is claimed and no regression is claimed; the arms are indistinguishable.

⭐⭐ **THE INSTRUMENT'S RESOLUTION IS WORSE THAN THE EFFECTS BEING REPORTED AGAINST IT, AND THAT IS A FINDING ABOUT THE LANE, NOT ABOUT THIS ROW.** Prior sessions recorded this witness's rate as `2/10 → 0/10 → 1/10` and read movement into it. At these counts that sequence is noise. **`one crash condemns the row` is a sound RELEASE gate and a useless COMPARISON gate** — as a release criterion it is exactly right and must stay; as evidence that an arm improved, it needs far more reps than any session has run. ⛔ Do not accept a REPS=5 delta on this witness from anyone, including a future me.

## PROVENANCE
Code: SCRIP `150767ae1` (`src/emitter/emit.cpp` only). Boards re-proven after rebase onto `48d838a01`, corpus `4103159b5`. RT_OPT=`-O0`.
⚠️ Measured in an **isolated checkout outside the seat root**: `/home/claude_P/SCRIP` had up to **four concurrent `make pristine`/`make` runs** from other sessions throughout, and a binary built there segfaulted. Reported to ceo. The isolated tree gets its own objdir by construction, so these numbers are uncontended.
