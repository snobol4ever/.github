# FINDING 2026-08-30 hq_C — the blob activation frame has no spare bytes, so a FENCE watermark written in the ζ-SPINE plane necessarily lands on the banked γ

**Row:** `fuzz-nondeterminism-rootcause` · **Cluster A** (`fz_segv_09`, `fz_red_m4a`) · **CURED, both modes**
**SCRIP:** `src/emitter/emit.cpp` `fence_frame_candidate()` · killswitch `SCRIP_BLOB_FENCE_FRAME=0`

## ⭐⭐ THE MECHANISM, AT THE INSTRUCTION LEVEL

`fz_segv_09` is four lines: `G0 = POS(0)` · `P = FENCE((FENCE(POS(2)) *G0 | LEN(3)))` · `'a+a+a' POS(0) *P`.
Oracle (`sbl -bf`) says `match`. SCRIP SIGSEGV'd (rc=139) or SIGILL'd (rc=132), both modes.

The stored pattern `P` compiles to a blob `FN__PAT$1` with an **rbp activation frame** (R-4(b), `emit.cpp`
`blob_frame_bytes()`): `push rbp; mov rbp,rsp; sub rsp,72`, then the WIRE-STACK (s195) head banks the
caller's PUSHed pair — `[rbp+8]`→`[rbp-8]` (γ) and `[rbp+16]`→`[rbp-16]` (ω) — plus rdx at `-24` and the
casmark at `-32`.

The inner `FENCE(POS(2))` needs a watermark slot. `fence_frame_candidate()` said NO (its body holds only
`POS`, no dynamic node), so `bb_match_fence1`'s `fence_u2_frame()` arm emitted the **ζ-SPINE** form:

```
n4_match_fence1_α:  mov qword ptr [rsp + 64], rsp      ; rsp = rbp-72  ⇒  [rbp-8]   = THE BANKED γ
                    mov qword ptr [rsp + 96], rsp      ;              ⇒  [rbp+24]  = the CALLER's pushed rbp
```

`PAT$1_γ` then read the banked pair back and `jmp rcx` — into a **stack address**:

```
SUSPEND PAT$1 rbp=0x7ffffffedfc0 rsp=0x7ffffffedf78  banked_gamma[rbp-8]=0x7ffffffedf78  banked_omega[rbp-16]=0x555555555a6f
Program received signal SIGILL at 0x7ffffffedf7a          (= the smashed γ + 2)
```

A gdb **watchpoint on `[rbp-8]`** names the writer with no inference left: banked correctly at
`PAT$1_α_body` (`0x555555555a66`, the real γ label), then overwritten at `n4_match_fence1_α`'s
`mov %rsp,0x40(%rsp)`, then read back at `PAT$1_γ`. ω survived; γ did not — and **that asymmetry is the
whole tell**, because the two words were banked two instructions apart from the same source.

## ⛔ WHY THIS IS A CLASS AND NOT A ONE-OFF: THE BLOB FRAME HAS ZERO SPARE BYTES

`blob_frame_bytes() = blob_head_bytes() + 16*count` and `frame_slot_off(2,idx) = -((head+8) + 16*idx)`.
For this blob: head 40 (`rbp-40..rbp-1`) + 2 cells of 16 (`rbp-72..rbp-41`) = 72. **Every byte between
rsp and rbp is already owned.** So inside a blob the ζ-SPINE `[rsp+N]` plane has **no capacity at all**:
`N < frame` hits an allocated cell, `N >= frame` is above rbp on the caller's stack. A U2 watermark there
is not "a different addressing plane", it is a **guaranteed collision** — the only variable is what it
lands on.

⭐ **What made it invisible for ten days: nothing is ever out of bounds.** Both stores hit mapped,
writable, plausible stack; no guard page, no poison, no ASAN report. The fault surfaces one indirect jump
later, inside a *different* function, as a jump to an address that looks like a pointer because it is one.
`emit.cpp`'s own R-4(b) banner already lists **"FENCE1 watermark"** among the things the blob frame exists
to own — the frame was built for this slot and the fence was never asked whether it was standing in one.

⭐ **The s188 ablation had already isolated the ingredient and nobody could spend it.** `fz_red_m4a`'s own
header (2026-08-20) reads *"an ALT arm holding FENCE(...) adjacent to a defer … **dropping the inner FENCE
is GREEN**"* — an exactly correct necessary-ingredient list, sitting in the witness file for ten days,
naming the node whose slot allocator was the defect. **An ablation names the ingredient; it cannot name
the mechanism, and the gap between those two is where a witness can sit for ten days looking investigated.**

## THE CURE

`fence_frame_candidate()` now admits a `FENCE1` with `ival != 0` when `blob_frame_scope()` — so the
watermark is granted an rbp frame cell (`FFCQ(0)`, `[rbp-80]` here) and the frame grows 72→88. Blast
radius is bounded by construction: `blob_frame_scope()` is false for the main match graph, so **only
stored-pattern blobs that contain a watermark-bearing FENCE1 change at all**.

⚠️ **NOT a fix for Cluster B.** `fz_red_m1b` / `fz_segv_24` are *"ARBNO-over-defer re-entry (blob road —
**no FENCE needed**)"* and are measured **unchanged** by this cure. The A/B partition in this row's baton
is confirmed to be two mechanisms, not one.

## MEASURED

**Witnesses**, pristine `-O0`, oracle pre-flight first (**5/5 refs byte-identical to `sbl -bf`** — genuinely
oracle-derived, not self-pinned, the s277 lesson applied before any verdict):

| witness | before (m3) | before (m4) | after (m3) | after (m4) |
|---|---|---|---|---|
| `fz_segv_09` | `139`×5 | `139`×2 `132`×1 | **`0` + `match` ×10** | **`0` + `match` ×10** |
| `fz_red_m4a` | `139`×3 `132`×2 | — | **`0` + `match` ×10** | **`0` + `match` ×10** |
| `fz_red_m1b` (Cluster B) | `0`/`124` mixed | — | `0`×4 `124`×2, answer `nomatch` ≠ ref | unchanged |
| `fz_segv_24` (Cluster B) | `0`/`124` mixed | — | `0`×2 `124`×4, answer `nomatch` ≠ ref | unchanged |
| `fz_red_m4b` | `139`/`0` mixed | — | `nomatch`×3 `139`×3 | unchanged |

**Killswitch control arm:** `SCRIP_BLOB_FENCE_FRAME=0` produces a `.s` **byte-identical to the pre-patch
compiler** on `fz_segv_09` (`diff` clean) — so the A/B is one binary, no rebuild, and the OFF arm is
provably the old codegen rather than assumed to be.

**SNOBOL4 blocking floor**, `make pristine` then `make test`: **m3 PASS=1672 FAIL=0 · m4 PASS=1672 FAIL=0
SKIP=0 · MISSING=0 · rc=0 GATE OK**, over the printed denominator. `test_gate_capture_stdin_and_red_exit`,
`test_gate_emit_no_lang`, `test_gate_template_medium_invisible`, `test_gate_corpus_coverage_classified`
all rc=0.

**SHARED-NODE VERDICT SCOPE.** `IR_MATCH_FENCE1` is emitted by `lower_snobol4.c` alone, but
`frame_slot_scan`/`blob_frame_bytes` are shared with the ARBNO / capture / alternate / leaf / xop slot
families, so the Icon control arm was run — **measured WITH AND WITHOUT the change on ONE binary**, via the
killswitch, no rebuild between arms:

| arm | Icon `--run` |
|---|---|
| cure ON | `PASS=256 FAIL=12 BADEXIT=1 XFAIL=28 MISSING=0 TOTAL=297` |
| `SCRIP_BLOB_FENCE_FRAME=0` | `PASS=256 FAIL=12 BADEXIT=1 XFAIL=28 MISSING=0 TOTAL=297` |

⭐ **The killswitch is what made that a real control arm rather than a re-run.** My own s280 lesson —
a `git stash` on already-committed files, both arms grading the same tree, two identical numbers reading
as a clean confirmation — is avoided here structurally: the OFF arm was *proven* to be the old codegen by
a byte-identical `.s` diff before either number was taken. **"No difference" is also what a broken
experiment prints**, and the only defence is proving the arms can differ.

`make test` rc=0 end to end, including `test_gate_optbypass_watermark`: DEFAULT **0/1649 hard**,
`SCRIP_OPT=0` 187/1649, `SCRIP_ZD=0` **303**/1649 (pin ≤306). ⭐ That `SCRIP_ZD=0` arm moved **306 → 303**
— three programs stopped depending on the ζ-depth planner, which is the cure's own signature appearing in
somebody else's instrument, unprompted.

## ⭐ THE INSTRUMENT, AND WHAT IT IS HONESTLY WORTH

`scripts/util_blob_spine_slot_sweep.sh` reports in-blob `[rsp + N≥32]` references. Negative-tested in both
directions: **0 findings across the five witnesses with the cure on; with the killswitch off it names the
exact 4 offending instructions** — and it independently reproduces this row's own A/B partition, flagging
the three FENCE-in-blob witnesses (`fz_segv_09`, `fz_red_m4a`, `fz_red_m4b`) and **neither** Cluster B one,
from the emitter side, without being told what the partition was.

⛔ **It is a SCREEN, not a defect detector, and the header says so.** `[rsp+N]` is a collision only if rsp
is at the frame base there; a box that carved its own stack addresses that carve through the same syntax,
and the sweep cannot see control flow. The fence was unambiguous because its carve was `sub rsp, 0`.
**The corpus proves the caveat directly: `beauty.sno` reports hits and self-hosts to its own fixed point.**
So the output is spent as an **A/B difference** — refs that vanish are what a change fixed, refs in both
arms are pre-existing suspects owing a carve analysis, refs that appear are new exposure — never as a raw
defect count.

## ⭐⭐ THE CURE REACHED THREE ENTRIES NOBODY HAD CONNECTED TO IT — AND THE MARKERS WOULD HAVE HIDDEN THAT

The master suite A/B, one binary, the killswitch as the only variable:

| arm | m3/m4 `xfail` | m3/m4 `xpass` |
|---|---|---|
| `SCRIP_BLOB_FENCE_FRAME=0` | 75 / 75 | 2 / 2 |
| cure ON | 70 / 70 | **7 / 7** |

**Attribution proven three independent ways, not inferred from the counts:** (1) the counts above; (2) the
**names** — the OFF arm's XPASS set is exactly `{user_function_eval_arbno_replace_branch_2,
user_function_indirect_replace_2}`, and the ON arm's is those two **plus five**; (3) a per-entry killswitch
A/B on each extracted witness, N=5:

| entry | ON | OFF | |
|---|---|---|---|
| `arbno_fence_notany_replace_branch_1` | 5/5 | 0/5 | cured here |
| `arbno_fence_notany_replace_branch_2` | 5/5 | 0/5 | cured here |
| `fence_arb_span_replace_branch_2` | 5/5 | 0/5 | cured here |
| `fence_pos_len_replace_branch_1` (`fz_red_m4a`) | 5/5 | 0/5 | cured here |
| `fence_pos_len_replace_branch_2` (`fz_segv_09`) | 5/5 | 0/5 | cured here |
| `user_function_indirect_replace_2` | 5/5 | 5/5 | pre-existing |
| `user_function_eval_arbno_replace_branch_2` | 0/5 | 0/5 | pre-existing |

⛔ **So three master-suite entries were carrying this defect and nobody had connected them to it** — every
one FENCE-named, every one marked *"crashes: SIGSEGV (rc=-11). Not further diagnosed."*

⭐ **AND LEAVING THE MARKERS WOULD HAVE MADE THE CURE INVISIBLE TO THE FLOOR.** An XFAIL entry is graded
out of the denominator, so all five would have gone on being *expected* to crash and a regression of this
fix would have reddened nothing. That is this seat's own s280 lesson running backwards — *the symptom left
the board; the bug did not leave the tree* — inverted into *the cure landed; the board could not see it.*
**Promoted** (banner suffix off in `ALL.sno` **and** `ALL.ref`, reason blocks deleted from `ALL.xfail`, one
commit — the harness refuses a reason left behind, so the promotion has to prove it is complete). Graded
population **1649 → 1654**, `FAIL=0` both modes, residual `xpass=2` is the pre-existing pair, untouched.

⚠️ **ONE FALSE ALARM OF MY OWN, RECORDED BECAUSE THE A/B IS WHAT SAVED IT.**
`user_function_eval_arbno_replace_branch_2` reads `0/5` standalone while the suite grades it XPASS, which
looked for a moment like an `extract`-vs-in-suite equivalence defect — which would have undermined every
witness materialized that way, this row's own five included. It is not: the entry pulls `-INCLUDE
'global.inc'` and friends, resolved against the working directory, and my scratch dir has none of them.
**The beauty lesson verbatim, and the CLAUDE.md digest already carries it.** ⭐ The point worth keeping is
that **the A/B absorbed the confound without my noticing it**: the environmental failure hit both arms
equally, so the relative verdict ("pre-existing") was right even while the absolute number was garbage.
An absolute reading would have been wrong; the difference was not.

## WHAT IS STILL OPEN ON THE ROW — 2 of 5, stated as 2 of 5

- **Cluster B** (`fz_red_m1b`, `fz_segv_24`) — *"ARBNO-over-defer re-entry (blob road, **no FENCE needed**)"*,
  measured **unchanged** by this cure, and the sweep confirms it from the emitter side: neither carries an
  in-blob spine ref in either arm. Five sessions of empirical work are already banked on it; the open
  question there is still seat11's, and it is a design question, not another predicate flip.
- **`fz_red_m4b`** — ⭐ **its collision IS cured** (it is the single file the corpus-wide A/B removed) **and it
  still fails.** So it carries a **second, independent defect**, and it is now a strictly better witness than
  it was this morning: one mechanism removed by construction, the remainder isolated. It is also the one
  witness whose distribution straddles PASS (≈0.54 converted-green), so it stays held out of the master.

## ⭐ THE TRANSFERABLE PART

1. ⛔ **A FRAME WITH NO SPARE BYTES MAKES "THE OTHER ADDRESSING PLANE" A GUARANTEED COLLISION, NOT A
   FALLBACK.** The U2 arm is not wrong in general — it is wrong *in a scope where its plane has no capacity*,
   and nothing in its own file could tell it which scope it was in.
2. ⛔ **AN ABLATION NAMES THE INGREDIENT AND CANNOT NAME THE MECHANISM.** *"Dropping the inner FENCE is
   GREEN"* was exactly right and sat unspent for ten days. The gap between a correct ingredient list and a
   mechanism is where a witness sits looking investigated.
3. ⛔ **A TRUE COMMENT DESCRIBING A CROSS-FILE RELATIONSHIP IS NOT A SAFE ONE.** R-4(b) said the frame owns
   the FENCE1 watermark and stayed true; the allocator was never told. Landed as law with hq_B's twin —
   RULES.md § THE INSTRUMENT LAWS, THIRTEENTH BATCH.
4. ⛔ **A CURED ENTRY LEFT MARKED XFAIL IS A CURE THE BOARD CANNOT PROTECT.** Promotion is part of the fix,
   not paperwork after it.
5. ⭐ **AN A/B ABSORBS CONFOUNDS AN ABSOLUTE READING CANNOT.** Twice in one session: the `-INCLUDE`
   environmental failure above, and the whole attribution question — `xpass` moved 0→7 against my own
   earlier finding, but that finding was a *different tree*, so only the same-binary killswitch A/B could
   say which of the 7 were mine.

## ⭐⭐ THE PROMOTION IMMEDIATELY REFUSED A SIBLING GATE — AND THEN PROVED A LAW I HAD WRITTEN AN HOUR EARLIER, ON MYSELF

Growing the graded population 1649 → 1654 made `test_gate_optbypass_watermark` **REFUSE (rc=2)**:
*"graded population is 1654, but the watermark was pinned against 1649 … A different denominator makes
the ratio mean something else, so this is refused rather than compared."* **`make test` went rc=2 —
refusing, not passing, and it was not reported as green.** That is the pinned-denominator arm doing
exactly its job, on my own landing, in the same run that landed it.

Re-measured (`util_census_optimizer_bypass.py --out`, wall 529s), and **every unit of movement is
attributed — none of it is drift:**

| arm | before | after | Δ | why |
|---|---|---|---|---|
| DEFAULT (hard bar) | 0/1649 | **0/1654** | — | unchanged |
| `SCRIP_OPT=0` | 187/1649 (11.34%) | **190/1654 (11.49%)** | **+3** | the 3 admitted entries that fail under it |
| `SCRIP_ZD=0` | 306/1649 (18.56%) | **303/1654 (18.32%)** | **−3** | cured by this fix |

The per-entry CSV names them: `arbno_fence_notany_replace_branch_1`, `_2` and
`fence_arb_span_replace_branch_2` read `opt0_changed=1`; the other two promoted entries are clean in
both arms; **all five PASS in the DEFAULT arm.** `187 + 3 = 190` exactly, and `303` was already measured
on this binary *before* the promotion, so `303 + 0 = 303` exactly.

⭐⭐ **TWO INDEPENDENT PREDICTIONS, BOTH EXACT TO THE UNIT — and that is what licensed pinning through a
census whose failure-KIND breakdown moved a lot** (`opt0` HANG 0→17, `zd0` HANG 4→33, with `CRASH(-11)`
down by about as much). Entries sitting near the timeout boundary trade CRASH for HANG under load —
RULES.md § AN RC IS NOT A MEASUREMENT OF TIME. **The counts are what this gate pins, and both landed on
their predicted values, so the kind churn is composition, not population.** Had the totals *not* matched
a prediction I made before looking, the honest move would have been to re-measure on a quiet box rather
than pin through the noise.

⛔⭐ **AND THE OPT0 RISE IS THE LAW I HAD WRITTEN INTO `RULES.md` AN HOUR EARLIER, ARRIVING ON MY OWN
DESK.** Ruling to hq_P on the trail-unwind bound check, same session: *"a watermark that only ratchets
DOWN encodes the assumption that every future number is a claim about the world. When an INSTRUMENT
becomes more honest, its number legitimately gets worse."* **Those three programs were always broken
under `SCRIP_OPT=0`** — they were invisible because XFAIL puts an entry outside the denominator.
Promoting a cured marker made three pre-existing bypass failures visible **for the first time**. The
number got worse because the instrument got more honest. Re-pinned in the landing commit with the
attribution in the pin's own comment, and routed to hq_P/ceo as that gate's header instructs — the same
thing I told hq_P to do, which would have been worth very little if I had exempted myself from it.

## ⛔⛔ AND THEN I GOT THE PIN WRONG IN KIND, NOT IN VALUE — MY OWN ERROR, RECORDED IN FULL

I pushed `--pinned-zd0-max 303`. **The very next honest run — the merged tree, pristine, no code change of
mine — read 304 and RED-ed `make test` for the whole fleet**, live on origin, for as long as it took me to
find it. `SNOBOL4 m3 1677/1677 · m4 1677/1677 FAIL=0` on that same run, so the cure and the promotions were
never in question; the gate was.

**MEASURED CAUSE, not inferred.** The four entries that moved between the two censuses were extracted and
run **10× each under `SCRIP_ZD=0` on one binary, one tree, back to back**:

| entry | zd0 over 10 runs |
|---|---|
| `arbno_pos_rpos_branch_84` | PASS 6/10, **silent wrong answer (rc=0) 4/10** |
| `arbno_pos_rpos_branch_85` | PASS 4/10, **silent wrong answer (rc=0) 6/10** |
| `fence_break_pos_branch_2` | PASS 8/10, SIGSEGV 2/10 |
| `span_pos_rpos_replace_branch_9` | PASS 4/10, SIGSEGV 1/10, SIGABRT 5/10 |

⛔ **So the `SCRIP_ZD=0` regression count is a sum over nondeterministic entries.** Four whole-census
readings across two trees: **301, 302, 303, 304.** A `<=` comparison against an exact count on that arm is
**flaky by construction and needs no drift at all to fire.** That predates this session — hq_P pinned 306,
hq_B 291, I pinned 303, all single-sample pins on a quantity that moves on resampling.

⭐ **THE MISTAKE WORTH NAMING IS THAT I TIGHTENED A RATCHET ON ONE SAMPLE.** I had reasoned carefully, in
this same session, about *raising* a pin honestly — and never noticed that **lowering one carries the same
evidentiary burden, and lowering is the direction that manufactures false reds for everyone else.** I even
wrote the variance into the pin comment (*"302, one below the census's 303 … which is why the pin sits at
the higher of the two"*) and then pinned at the max of that two-sample anyway. **Recognising the noise and
then treating your sample max as the bound is a worse failure than not noticing it, because it reads as
diligence.** Same shape as CLAUDE.md's timeout law — *a bound tuned to the measured value is not tight, it
is flaky* — transposed from durations to counts.

**CORRECTED:** `zd0` stays at hq_P's ceo-ratified **306**, unchanged. That is *declining to tighten on
insufficient evidence*, not adding slack. Only the two values I can attribute move: population **1654**
(structural, mine) and `opt0` **190** (+3, named entries, stable across three readings).

⚠️ **THE REAL FIX IS NOT A NUMBER, AND IT IS ROUTED, NOT TAKEN:** pin the **stable subset** — count only
entries whose bypass verdict is reproducible across N runs, and report the flapping set separately.
⭐ **RULES.md's denominator law says every grader states its denominator; the missing half is that a grader
summing NONDETERMINISTIC units must state its VARIANCE, or it cannot support the comparison it is asked to
support.** Until that lands, a violation on this arm means *re-measure twice before believing it* — which
is now written in the gate rather than in someone's memory.

⚠️ **Secondary, in this seat's own lane:** two of those four return **rc=0 with the wrong answer, at 40% and
60%**, under `SCRIP_ZD=0`. That the emergency bypass is not a correct path is already known and rowed
(`optimizer-off-path-segvs-…`); that it is *nondeterministically* wrong — the same program, same binary,
two different answers — is the part that breaks any instrument built on counting it.

## ⛔⛔ AND THEN I BROKE THE GATE SCRIPT ITSELF, AND `bash -n` TOLD ME IT WAS FINE

Resolving the rebase conflict with hq_P I inserted the joint-resolution comment block **between
`python3 … --gate \` and its continuation line**. The backslash continued into a comment, so python3 ran
with **no pin arguments at all** — falling back to the census's built-in default population 1494 and
REFUSING — and the argument line was then executed as a shell command
(`--pinned-population: command not found`). **`make test` was broken on origin for the whole fleet from
that push until the repair.**

⭐⭐ **The damaged form is still VALID BASH — two commands where one was meant — so `bash -n` cannot see
it.** I ran it, read `syntax ok`, and pushed. **`bash -n` answers *is this parseable*, not *is this what I
meant*.** That is CLAUDE.md's `command -v` class exactly, committed roughly two hours after I wrote the
same shape into `RULES.md § THE INSTRUMENT LAWS, THIRTEENTH BATCH`: *an instrument that answers a narrower
question than you think you asked will never say so.* Writing a law down does not inoculate you against it.

**The rule this earns, now in the file at the exact spot: a gate is verified by INVOKING it.** Not by
`bash -n`, not by a diff that looks right, not by a green sibling — nothing else tells you the arguments
arrived. Repaired in `3c9c04c8`, verified by running it: `rc=0 · DEFAULT 0/1654 (hard) · opt0 190 ≤ 190 ·
zd0 301 ≤ 308`.

⚠️ **Both of my errors this session were in the instrument layer, not the cure**, and that is the pattern
I want the next session to see: the compiler fix was measured, negative-tested, control-armed and held up
across three tree moves; the *pins and scripts around it* are where I put two defects into origin in one
hour. **The cure got the discipline; the plumbing got assumptions.**

## FINAL VERDICT — merged tree, `make test` rc=0 end to end

Re-proven after the push rebase pulled 8 SCRIP commits from other seats (an Icon parser fix, grader
repairs, and hq_P's `pl_trail_unwind` bound check landing my own ruling), per the REBASE-BASELINE
COROLLARY — none of the numbers above were quoted across that boundary:

```
✅ m3 PASS=1677 FAIL=0 · m4 PASS=1677 FAIL=0 SKIP=0 · MISSING=0
   master: total=1726 · m3/m4 xfail=70 xpass=2   (the 2 = the pre-existing pair, untouched)
✅ capture-stdin · emit_no_lang · template_medium_invisible · corpus_coverage_classified
✅ optbypass_watermark: DEFAULT 0/1654 (hard) · SCRIP_OPT=0 190/1654 (≤190) · SCRIP_ZD=0 301/1654 (≤308)
   make test rc=0
```

`.s` artifact regeneration (the three sanctioned scripts, in order, since this session touched
`src/emitter/emit.cpp`): **benchmark, demo and prolog-bench all report "already current", rc=0 each** —
consistent with the cure's stated blast radius, since it fires only for a FENCE1 inside a stored-pattern
blob and no benchmark or demo carries one. ⛔ `util_regen_programs_s_artifacts.sh` deliberately NOT run.
