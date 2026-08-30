# FINDING — 2026-08-30 hq_C (`/home/claude_C`) — queue row `fuzz-nondeterminism-rootcause`

# THE SUITE CONVERTER DECIDES `xfail` FROM **ONE RUN PER MODE**. FOR AN ENTRY WHOSE VERDICT IS A
# DISTRIBUTION RATHER THAN A VALUE, THAT SINGLE SAMPLE PERMANENTLY PINS A LABEL THAT IS ONLY
# SOMETIMES TRUE — AND THE TWO BRANCHES ARE WILDLY ASYMMETRIC: THE XFAIL BRANCH IS HARMLESS, THE
# GREEN BRANCH PUTS A COIN-FLIP VERDICT INTO THE BLOCKING FLOOR. MEASURED: `fz_red_m4b`, THE ONE
# WITNESS `ALL.excluded.txt` HELD OUT, PASSES **9/10 (m3)** AND **6/10 (m4)** — SO IT HAD ROUGHLY A
# **54% CHANCE OF BEING CONVERTED GREEN**, AND IT IS THE ONLY ONE OF THE FIVE THAT NEEDED HOLDING OUT.

**WATERMARK:** `make pristine` clean (rc=0, HQ-27), SCRIP `50a3f76b`, corpus `4a67fcde`, .github `9da3b570`,
all three `merge --ff-only origin/main` at session start. Board on the pre-pull tree: m3 PASS=1672 FAIL=0 ·
m4 PASS=1672 FAIL=0 · master total=1726 · m3/m4 xfail=77 xpass=0. ⛔ Per the REBASE-BASELINE COROLLARY that
board is the PRE-pull arm and is cited only for the xfail/xpass counters, which this FINDING does not claim
to have moved.

## 0. FIRST, THE THING THAT BLOCKED EVERYTHING: THE ROW'S INSTRUMENTS POINTED AT A DELETED DIRECTORY

Both of this row's instruments — `util_fuzz_witness_stability.sh` and `util_fuzz_witness_predicate_ladder.sh`,
built last session precisely because "a witness set whose own stability is unmeasured cannot falsify anything" —
defaulted `FUZZ_DIR` to `corpus/tests/snobol4/probe_loose/fuzz`. **The one-flat-suite cutover (corpus `c06960a1`,
Lon 2026-08-29 total-conversion ruling) deleted that directory.** 4 of the 5 witnesses were absorbed into the
master suite as XFAIL block entries **under new names**; only the 5th survives as a loose pair.

✅ **The instruments refused correctly — `⛔ REFUSE(rc=2): witness dir missing` — they did not report an empty
set as a stable set.** That is the "a test that cannot measure REFUSES" law working exactly as written, and it
is the reason this cost an hour instead of a session's worth of false verdicts. ⛔ **But a refusal is not a
measurement.** The row was left with NO working instrument, and its baton's live NEXT block still directs the
next session to grade against a witness set by a path that no longer resolves.

⭐ **The witnesses did not become unavailable, only unreachable BY PATH.** `corpus_suite_harness.py extract`
reproduces each absorbed entry exactly. **CURED THIS SESSION:** `scripts/util_fuzz_witness_materialize.sh`
rebuilds all 5 into one directory and prints its path, so the documented usage composes:
```
FUZZ_DIR="$(bash scripts/util_fuzz_witness_materialize.sh)" bash scripts/util_fuzz_witness_stability.sh
```
Entry names are **derived from `ALL.csv`'s `family` column, never hardcoded** — absorption renamed every witness
(`fz_segv_09` → `fence_pos_len_replace_branch_2`), and a hardcoded list would rot at the next rename exactly the
way the `FUZZ_DIR` default just did. It refuses (rc=2) on anything but a full 5/5: an incomplete witness set is
not a smaller experiment, it is a different one. Both instruments' stale refusal now names this recipe.
⚠️ Verified byte-identical to a hand-driven `extract` of the same five (`cmp` on all 5 `.sno`) — extraction
goes through the harness's own verb because seat11 measured that hand-retyped copies give a FALSE-CLEAN signal.

## 1. WHERE THE FIVE WITNESSES ACTUALLY ARE

| witness | now | marker |
|---|---|---|
| `fz_red_m1b_arbno_defer_blob` | master entry `arbno_fence_tab_replace_branch_1` | XFAIL |
| `fz_red_m4a_blob_alt_fence_defer` | master entry `fence_pos_len_replace_branch_1` | XFAIL |
| `fz_segv_09` | master entry `fence_pos_len_replace_branch_2` | XFAIL |
| `fz_segv_24` | master entry `arbno_bal_tab_replace_branch_1` | XFAIL |
| `fz_red_m4b_blob_defer_fence` | **loose pair, held out** | `ALL.excluded.txt` |

## 2. STABILITY ON TODAY'S PRISTINE TREE — 8 OF 10 PAIRS UNSTABLE, WORSE THAN THE BATON'S 6/10

`util_fuzz_witness_stability.sh`, N=10, both modes, (stdout,rc) as a pair, SCRIP `50a3f76b`:

| witness | m3 | m4 |
|---|---|---|
| `fz_red_m1b` | **UNSTABLE** 6× rc=0 / 4× rc=124 | **UNSTABLE** 4× rc=0 / 6× rc=124 |
| `fz_red_m4a` | **UNSTABLE** 2× rc=132 / 8× rc=139 | STABLE rc=139 |
| `fz_red_m4b` | **UNSTABLE** 4× rc=0 / 6× rc=139 | **UNSTABLE** 7× rc=0 / 3× rc=139 |
| `fz_segv_09` | **UNSTABLE** 1× rc=132 / 9× rc=139 | STABLE rc=139 |
| `fz_segv_24` | **UNSTABLE** 7× rc=0 / 3× rc=124 | **UNSTABLE** 5× rc=0 / 5× rc=124 |

⛔ **The baton's retained arm is VOID.** It recorded 4 usable pairs — `fz_segv_09` m3+m4, `fz_red_m4a` m3+m4 —
of which **`fz_segv_09` m3 and `fz_red_m4a` m3 are now unstable**. Only the two m4 pairs survive. This is the
third tree in three days on which `fz_segv_24` reads differently; do not cite any of these without re-measuring.

## 2b. ⚠️ N=6 AND N=10 DISAGREE ON THIS SET, IN-SESSION, ON ONE BINARY — AND N=6 GIVES THE FLATTERING ANSWER

Immediately after the N=10 table above I ran `util_fuzz_witness_predicate_ladder.sh` at **N=6** against the
identical materialized set and the identical binary (SCRIP `50a3f76b`, only my own shell edits dirty):

| pair | N=6 ladder verdict | N=10 stability verdict |
|---|---|---|
| `fz_segv_09` m3 | `139:6` → **P1, strictest** | **UNSTABLE** 1× rc=132 / 9× rc=139 |
| `fz_red_m4a` m3 | `139:6` → **P1, strictest** | **UNSTABLE** 2× rc=132 / 8× rc=139 |

⛔ **The N=6 run would have handed the row FOUR usable pairs instead of two**, and the two extra ones are the
two that flip to `SIGILL` about 10–20% of the time. Nothing is wrong with either instrument: at a 10% minority
arm, P(N=6 misses it) = 0.9⁶ ≈ **0.53**, so missing it is the *coin-flip likely* outcome. ⭐ This is hq_B's own
*"a sample that detects a coin is not a sample that measures it"* reproduced live on the very set that produced
the aphorism — and note the direction: **the cheaper sample was the one that said "go ahead and grade on this."**
⛔ The two m3 pairs are therefore NOT in this FINDING's surviving arm, and any future run of the ladder on these
witnesses at N<10 should be read as unable to see the minority arm rather than as evidence of stability.

## 3. ⭐⭐ THE FINDING — A SINGLE SAMPLE PINS A PERMANENT LABEL, AND ONE BRANCH IS SEVERE

`cmd_convert` runs the original **once per mode** and pins the marker from that one observation:
```python
orig_verdicts = run_all_modes(paths, sno_path, expected_text, tmp_root, modes, stdin_text=stdin_text)
orig_green    = all(v.kind == "PASS" for v in orig_verdicts.values())
...  Entry(..., xfail=not orig_green)
```
`cmd_run` then buckets:
```python
if e.xfail:
    if kind == "PASS": counts[m]["XPASS"] += 1 ; fails.append(...)
    else:              counts[m]["XFAIL"] += 1          # ANY non-PASS arm lands here
else:
    counts[m][kind] += 1
    if kind != "PASS": fails.append(...)                # FAIL/CRASH/HANG -> reds the board
```
⭐ **Read those two together and the asymmetry is the whole finding:**
- **Sampled non-PASS → marked XFAIL → HARMLESS.** The XFAIL bucket absorbs *every* non-PASS arm without
  distinguishing them, so an entry that flips FAIL↔HANG↔CRASH counts as XFAIL on every run. Its counters do
  not move. **This is why all four converted fuzz witnesses are safe today and `xpass=0` is stable for them** —
  measured: none of the four has an arm whose stdout matches its `.ref`.
- **Sampled PASS → marked GREEN → SEVERE.** The entry joins the graded floor. Any later non-PASS arm becomes a
  real `CRASH`/`FAIL`/`HANG`, `m3_fail+m3_crash > 0`, and `test_corpus_snobol4.sh` reds — **the SNOBOL4 blocking
  floor, the control arm every shared-node cure in this fleet is graded against, goes red on a coin toss.**

**THE MEASUREMENT THAT MAKES IT CONCRETE.** `fz_red_m4b`'s `.ref` is `nomatch`, and its clean arm *produces
exactly that*:
```
fz_red_m4b   m3 PASS=9/10   m4 PASS=6/10      (stdout compared to its own .ref, N=10 each, pristine 50a3f76b)
```
The converter needs **both** modes PASS to mark an entry green, so P(green) ≈ 0.9 × 0.6 ≈ **0.54**. ⛔ **It was
approximately a coin flip whether `fz_red_m4b` was converted into the blocking floor as a green entry that
crashes 10–40% of the time.** It is the only one of the five whose distribution straddles PASS, and it is the
only one that was held out.

## 4. ⭐ THE CRITERION IS NOT "IS IT NONDETERMINISTIC" — IT IS "CAN ANY ARM OF IT **PASS**"

`ALL.excluded.txt` holds `fz_red_m4b` out for *"fuzz nondeterministic-crash class — a captured ref is one sample
of a distribution"*. **That reasoning is correct and the call was right, but it under-describes what it caught.**
Nondeterminism alone is *not* the hazard: `fz_red_m1b` (rc=0↔124 at 6/4 and 4/6) and `fz_segv_24` (7/3 and 5/5)
are **more** unstable than `fz_red_m4b` on the rc axis, and they are harmless, because XFAIL absorbs every
non-PASS arm. What makes `fz_red_m4b` different is the one property the note does not name: **its distribution
crosses the PASS boundary, and only a PASS arm can move a counter.**

⭐ **So the general rule, stated for the consolidation the whole fleet is on:** an entry must stay a file iff
**any arm of its distribution PASSes while another does not.** Applied as "exclude the unstable ones" the
predicate is simultaneously too broad (it would have stranded four harmless witnesses as permanent loose-file
exceptions, which Lon's total-conversion ruling voids) and — this is the half that bites — **too narrow, because
it invites you to judge instability on whatever axis you happened to sample.** Three of these five are unstable
on rc and safe; one is unstable on the *verdict* and dangerous. The axis that matters is the verdict, and it is
the only one the converter actually reads.

⛔ **This is a property of the converter, not of these five witnesses**, and the fleet is mid-consolidation:
any family containing a distribution-valued entry has the same ~coin-flip exposure. **Not yet measured across
the other families** — stated as the next thing to measure, not as a finding. The cheap sweep exists now:
`util_fuzz_witness_stability.sh` accepts any `FUZZ_DIR`.

## 5. ⚠️ MY OWN INSTRUMENT ANSWERED A NARROWER QUESTION THAN MY SENTENCE — CAUGHT, BUT ONLY BY LUCK OF A SECOND CHECK

Mid-session I grepped `ALL.xfail` for `fz_segv_09` / `fz_red_m1b` / `fz_segv_24` / `fz_red_m4a`, got **zero
hits**, and concluded in writing that *"the four are in the graded blocking floor, not xfail"* — i.e. that the
floor was already contaminated. **It was false.** `ALL.xfail` is keyed by **entry** name (`fence_pos_len_replace_branch_2`),
and I searched by **origin** name (`fz_segv_09`). The absorption renamed them and my key predated the rename.
Nothing in the grep could have reported the mismatch: an absent match and a wrong key are the same empty output.
I caught it only because I went on to read `ALL.csv`'s column header and saw an `xfail` column reading `1`.
⭐ **This is hq_P's own pooled class — a census scoped to the wrong NAME — and it is the fourth measured
instance** (theirs: nearly the wrong name; seat14's: the wrong field, `gpop`-only when the defect was in `wpop`;
mine here: the wrong key across a rename). ⛔ It also inverts the direction the row keeps getting bitten in:
this one made the situation look **worse** than it was, so alarm rather than complacency was what needed
checking. **A false alarm and a false all-clear come from the identical defect.**

## 5b. ⭐⭐ CLUSTER A: THE s195 RESUME-RECORD CONTRACT IS VIOLATED IN THE EMISSION, CONFIRMED — AND ONE PROGRAM CARRIES BOTH ARMS AS ITS OWN CONTROL

I opened §7.3 below as a labelled hypothesis and then measured it. **It is confirmed at the instruction
level, and the ASM-diff needed no sibling program: `fz_segv_09` emits TWO defer boxes with DIFFERENT
landing shapes.**

`emit.cpp`'s ω arm states the contract in prose and enforces it nowhere: *"a γ-SUSPEND leaves the blob's
resume record on top of the pair, so a landing-side add would eat the record instead (Lon s195: yielding is
different from returning)."* The producer emits exactly that record (`--compile`, verbatim):
```asm
PAT$1_γ:  mov rcx,[rbp-16] ; push rbp ; push rcx ; mov rcx,[rbp-8] ; push rcx
          lea rax,[rip+PAT$1_res] ; push rax ; mov rbp,[rbp+0] ; jmp rcx
```
and `PAT$1_res` reads it back at `mov rbp,[rsp+24]; add rsp,32` — **an offset that is CORRECT for that
record** ([rsp+0]=res, +8=γ, +16=ω, +24=rbp). ⛔ **The consumer is the defect.** The two defer landings in
the same file:
```asm
.Lmatch_defer_α_12_4:                      jmp .Lmatch_alternate_γ_2_s0     # box n5  — PRESERVES the record
.Lmatch_defer_α_61_4:  mov rsp,rbp
                       pop rbp ;           jmp n29_match_end_α              # box n61 — RELEASES it
```
`.Lmatch_defer_α_61_4/_5` are the exact labels seat09's gdb trace named. `mov rsp,rbp` resets rsp to the
defer box's own frame — **below all four words `PAT$1_γ` just pushed** — so a later backtrack to `PAT$1_res`
reads reclaimed stack. That is a *stronger* violation than the "landing-side add" the comment warns about.
⭐ **This answers seat09's §6.2 open question in the direction they could not choose between: `_res`'s offset
is RIGHT; a landing releases the frame the record sits above.** The two boxes differ on `dfrm()`, whose
`IR_MATCH_DEFER` arm is `((op_seal==1) || emit_defer_carve_rbp()) && emit_defer_rbp()` — so **`op_seal`
selects between a record-preserving and a record-destroying landing**, and nothing ties that choice to
whether a suspend record will actually arrive.
⚠️ **THAT LAST STEP IS A DEDUCTION, NOT AN OBSERVATION, AND THE REASON IS ITSELF WORTH RECORDING.**
`emit_defer_carve_rbp()` defaults 0 and `emit_defer_rbp()` defaults 1, so under the default environment
`dfrm() ≡ (op_seal == 1)`; both globals are process-wide constants, so two boxes in ONE program emitting
different arms must differ in `op_seal`. The deduction is airtight given those defaults — but ⛔ **`seal` is
exposed by NO dump**: `--dump-bb` prints the two `MATCH_DEFER` nodes (`b0_35` stmt:1, `b2_3` proc `PAT$1`)
and `--dump-ir-verbose` prints them, and neither shows the field that decides which landing they get.
⭐ A per-node flag that selects between a correct and an incorrect landing, and is invisible to every
instrument the compiler ships, is a debugging trap independent of this defect: the next person will have to
re-derive it from the predicate exactly as I did. Worth surfacing in a dump.

⚠️ **A/B ON THE EXISTING KILLSWITCH — IT MOVES THE SIGNATURE AND DOES NOT RESCUE THE PROGRAM, WHICH IS THE
INFORMATIVE OUTCOME.** `SCRIP_DEFER_RBP=0` replaces `mov rsp,rbp; pop rbp` with `mov rsp,[rsp+256]`:

| arm | m3 (N=10) | m4 (N=10) |
|---|---|---|
| default | `139`×10 | `139`×10 |
| `SCRIP_DEFER_RBP=0` | `132`×4 / `139`×6 | `139`×10 |

⛔ **Both landing shapes still RELEASE rsp**, one to `rbp` and one to a saved slot, so the record dies either
way and only the garbage differs — the m3 SIGILL rate moves ~10% → 40%. **The cure is therefore "the landing
must not release", not "release differently"**, exactly as the s195 comment already says in prose. ⛔ This is
a diagnostic A/B, NOT a candidate cure: `SCRIP_DEFER_RBP` is global and its SNOBOL4 blast radius is unmeasured.

## 5c. ⛔ AND N=10 IS NOT ENOUGH EITHER — THE SAME BINARY GAVE ME BOTH ANSWERS FOR `fz_segv_09` m3

The default arm above reads **`139`×10 — perfectly stable**. My §2 stability run, *same binary, same tree*,
read `132`×1 / `139`×9 — **unstable**. Both are correct samples of a ~10% minority arm: P(N=10 misses it) =
0.9¹⁰ ≈ **0.35**, so about a third of honest N=10 runs call this pair stable. ⭐ Combined with §2b (N=6 misses
it ~53% of the time) the honest statement is **a rate, not a verdict**: `fz_segv_09` m3 and `fz_red_m4a` m3
carry a ~10–20% SIGILL arm against a SIGSEGV majority. ⛔ **I have corrected my own baton accordingly** — it
briefly said those two pairs were simply "unstable", which is the same over-claim in the opposite direction
from calling them stable. Neither binary label survives the measurement; the rate does.

## 6. WHAT THIS DOES *NOT* CLAIM

- ✅ **The SNOBOL4 blocking floor is NOT contaminated today.** All four converted witnesses are XFAIL, every arm
  of each is non-PASS, `xpass=0`. Nothing here reds a board.
- The severe branch is a **near miss, measured**, not an incident: it did not happen, because `fz_red_m4b` was
  held out. Whether it was held out *because* someone measured the PASS arm or because "nondeterministic" was
  reason enough, I do not know and did not ask.
- No codegen was touched; no `.s` artifacts need regenerating. The two instrument edits change a refusal message
  and a header only, and the new script is additive.

## 7. WHAT THE NEXT SESSION INHERITS

1. **A working instrument again** — `util_fuzz_witness_materialize.sh` → `FUZZ_DIR` → either runner.
2. **The retained arm is down to two pairs** (`fz_segv_09` m4, `fz_red_m4a` m4), both Cluster A, both P1 rc=139.
   Cluster B still has none. The baton's 4-pair table is superseded by §2.
3. **The open design question, unchanged and now better supported:** seat09's Cluster-A root cause (`PAT$N_res`'s
   hardcoded `[rsp+0x18]` retry-reentry offset) is a **stack-depth contract asserted in one place and satisfied
   in another** — the same shape as `emit.cpp`'s own s195 WIRE-STACK comment, which states the contract in prose
   (*"a γ-SUSPEND leaves the blob's resume record on top of the pair, so a landing-side add would eat the record
   instead"*) and enforces it nowhere. ⚠️ `bb_match_defer.cpp`'s L(4)/L(5) landings emit `mov rsp,rbp; pop rbp`
   under `dfrm() && emit_defer_rbp()` (default ON), which is a frame release at exactly such a landing. **Stated
   as the hypothesis worth an ASM-diff, NOT as a measured cause — I did not diff the emitted `.s` for a witness
   pair, and the surrounding predicates (`dfrm()`, `_blob_wire`) may exclude this shape.**
4. ⭐ `g_emit.flat_res_p` (`emit.h`) is **assigned once and never read** — write-only residue. Hygiene, hq_B's
   lane, noted in passing; deleting it is safe *for the compiler*, but see CLAUDE.md's `g_zeta_mode` lesson
   before assuming a global with no compiler-side reader is dead.
