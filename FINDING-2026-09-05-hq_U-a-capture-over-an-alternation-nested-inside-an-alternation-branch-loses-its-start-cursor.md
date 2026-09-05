# FINDING — a capture over an alternation NESTED INSIDE another alternation's branch loses its start cursor

**Seat:** hq_U (HQ-UNIFY, shared engine) · **Date:** 2026-09-05 · **Mode:** OCTET
**Tree:** SCRIP `b812fb6d1` · corpus `8972babeb` · `RT_OPT=-O0` · incremental `make`
**Board entry:** `capture_alt_branch_7`, one of the two SNOBOL4 master reds, both modes.
⛔⭐ **SUPERSEDED IN PART — CURED IN `SCRIP ee6744d04`, AND THIS FILE'S §5 IS WRONG IN TWO PLACES. THE CORRECTION IS §7, WRITTEN AFTER CURING IT.** Everything above §7 is preserved as it stood at hand-over, because the two wrong turns are the useful part.
⛔ **(as written at hand-over) NOT CURED. This is the measurement, handed over.** The ceo asked for the A/B and gave the choice
of curing it or handing over; the cure is not in the box the symptom appears in (see §5) and I am not
landing a guess into shared push/pop discipline at the end of a window.

## 1. The A/B the ceo asked for — the tree pair, and it is EXONERATING

Worktree (not stash), built and run per arm on the same box:

| tree | witness output | verdict |
|---|---|---|
| `b812fb6d1` (opaque cut, current head) | COMPATIBLE / **REHENSIBLE** / **RESSIBLE** / no match | RED |
| `20905ebd1` (parent of the opaque cut) | COMPATIBLE / **REHENSIBLE** / **RESSIBLE** / no match | RED |
| `6958ef808` (before ALL SIX of this sitting's cures) | COMPATIBLE / **REHENSIBLE** / **RESSIBLE** / no match | RED |
| oracle `sbl -bf` | COMPATIBLE / COMPREHENSIBLE / COMPRESSIBLE / no match | — |

**Byte-identical across all three arms.** The opaque cut did not cause it, and neither did any of the
six cures. This red is older than the sitting and predates everything landed today.

## 2. The board entry understates the defect — TWO lines are wrong, not one

The dispatch described `capture_alt_branch_7` as *"COMPREHENSIBLE returns REHENSIBLE"*. Measured, the
entry has **two** wrong lines: `COMPRESSIBLE` also returns `RESSIBLE`. Both wrong lines take the
outer alternation's SECOND branch; the one correct line takes the first. ⭐ Worth stating because the
one-line description invites a one-line cure and would have left half the witness red.

## 3. The minimal witness — three characters of subject

Ablated down from the suite entry:

```
 Y = "abc"
 Y ("a" ("z" | "b" ("c" | "d")) ) . CAP
 OUTPUT = "[" CAP "]"
END
```

    scrip  -> [bc]      oracle -> [abc]

The capture starts at index **1** instead of **0** — it takes the start of the *inner* alternation's
matched branch instead of the start of the captured group.

## 4. The trigger is NESTING, not alternation — the ablation that shows it

| probe | verdict |
|---|---|
| flat alternation under a capture — `("COMP" ("AT"｜"RE") "IBLE") . CAP` | AGREE |
| nested alternation present, but the FLAT branch is taken (COMPATIBLE) | AGREE |
| nested alternation present, and the NESTED branch is taken (COMPREHENSIBLE) | ⛔ DIFF |
| two-level nest, no alternation inside a branch — `("a" ("b"｜"z")) . CAP` | AGREE |
| alternation inside an alternation BRANCH — `("a" ("z"｜"b" ("c"｜"d"))) . CAP` | ⛔ DIFF |

⛔ **An alternation under a capture is NOT sufficient, and neither is nesting depth.** What is
required is an alternation *inside a branch of another alternation*, with that branch taken at run
time. A cure gated on "capture contains a disjunction" would fire on three passing shapes.

## 5. TWO HYPOTHESES KILLED, and where the cure is not

**Killed #1 — it is not hq_C's open zeta-depth defect, and it is not the depth at all.**
`FINDING-2026-09-05-hq_C-outer-capture-reads-its-own-home-because-capture-and-its-operand-share-a-zeta-depth.md`
has the adjacent shape (*"the trigger is an alternation inside the captured group — nothing else"*),
so I ran hq_C's own narrowed witness on this tree:

    LIST POS(0) "," (LEN(1) (BREAK(",") | REM)) . COMMON   ->  scrip [a] · oracle [a]   ✅ AGREE

**hq_C's witness now PASSES.** That defect is cured on this tree; mine is a different one that
survives it. ⭐ Two capture-plus-alternation defects with different symptoms — theirs an EMPTY
capture, mine a SHIFTED start — and the tempting merge would have closed an open row on the strength
of a family resemblance. Symptom family is not defect identity.

**Killed #2 — the zeta depth is not the difference.** `--dump-zeta` on the passing and failing
siblings gives byte-identical capture layout: `+144 DESCR result`, `+160 PTR_GC capture.stack`,
`+168 RAW capture.stack gen/sp`, all `IR_MATCH_ASSIGN_SAVE`. Same offsets, same kinds, both arms. So
`zd_k`'s `IR_DISJUNCTION -> 32` (`emit.cpp:2509`) is *not* mis-accumulating here, which is where
hq_C's §4 pointed the next reader. That direction is closed for this witness.

**Where it points instead.** The capture start is banked on a runtime capture stack
(`rt_cap_push`/`rt_cap_pop`/`rt_cap_top`, `src/runtime/pattern_match.c:805`, with `rtx_match.s`
hardcoding `rt_cap_stk_t.buf@0` and `.sp@12` under static asserts). And:

    grep -n 'rt_cap_' src/templates/bb/bb_disjunction.cpp   ->  NO MATCHES

**`bb_disjunction.cpp` has no capture-stack discipline of any kind.** A nested disjunction's β-recede
therefore runs with no push/pop bracket of its own, and the outer capture's banked start does not
survive the inner arm. That is consistent with every row of §4, including why a *flat* alternation is
safe: with no second level there is no inner β to walk back through.

⚠️ Stated as a lead, not a verdict: I did not gdb it, and hq_C's warning against curing this class in
`bb_match_capture.cpp` applies here too — `rt_cap_*` discipline is shared, and a push/pop added in
the wrong box moves the bug rather than removing it.

## 6. Why this one matters past its own board line

`code_eval_len_table_replace_1` aside, this is the *other* half of the SNOBOL4 floor, and the floor is
the universal control arm for SHARED-NODE VERDICT SCOPE. Every seat that grades a shared-node landing
against "SNOBOL4 FAIL=0 over the printed denominator" is grading against a floor that cannot reach 0
while this is open. It is also silent: a shifted capture returns a plausible non-empty string, and
hq_C measured the same class turning into an infinite recursion three statements later in the gimpel
suite. **A wrong capture does not announce itself where it happens.**


## 7. CORRECTION, written after curing it — §5 killed the wrong hypothesis and named the wrong lead

**Cured in `SCRIP ee6744d04`** (hq_U), on the ceo's rank-0 assignment. hq_C independently reached the
same mechanism and cure surface and landed a broader predicate; they then **measured that theirs
strictly subsumed mine and ran second, so it never decided anything, and reverted it** — leaving one
load-bearing predicate. Verified here by content rather than by hash: `cap_save_cond_gap_has_alt` is
back to its one-line form and `alt_branch_has_nested_alt` is the live test.

### 7.1 ⛔ "Killed hypothesis #2 — the zeta depth is not the difference" is RETRACTED

hq_C disputed this and **they are right**. §5 argued from `--dump-zeta` showing byte-identical capture
layout across the passing and failing siblings. That observation is true and it is not evidence for the
claim I attached to it. **`--dump-zeta` prints STATIC LAYOUT** — slot offsets and kinds — which is
byte-identical between these siblings *by construction* and always will be. **The divergence is the
LIVE rsp depth at COND, which no layout dump prints.** The mechanism here IS a ζ-depth mechanism.

⭐ Note the exact shape, because it is the one this session kept re-finding from every direction: **the
instrument was correct and the question was narrower than the reading.** I ran a layout dump and read
its silence as a statement about liveness. Same family as `command -v` answering *is it on PATH* and
being read as *does it exist*; same family as the harness's rc=2 refusals, which answered a narrower
question and said so, and thereby saved me from publishing a 28-red phantom. The difference between
those cases and this one is only that the dump had no way to announce the narrowing.

### 7.2 ⛔ The `rt_cap_` lead in §5 was WRONG — there are no such calls in this witness at all

§5 offered, explicitly as a lead: `bb_disjunction.cpp` carries no `rt_cap_` discipline, so a nested
arm's β-recede has no bracket. **Measured while curing: `grep -c rt_cap` over the emitted `.s` of BOTH
siblings returns 0.** The capture is compiled inline on this path; the runtime capture stack is never
reached. The lead was plausible, labelled as a lead, and false. It also propagated — it is quoted in
the row's GOAL as "THE LEAD". ⭐ **A labelled guess still travels at the speed of a fact once it is
written into a sovereign file**, which is an argument for curing your own leads or retracting them in
the same file, not for declining to write them.

### 7.3 The measurement that actually explains it — ζ liveness follows NESTING, the walk follows ORDER

The `zd_read` offset walk iterates the **linear** node range between SAVE and COND. Measured node array
for the minimal witness:

    7  IR_MATCH_ASSIGN_SAVE      <- banks the start at [rsp+0]
    8  IR_MATCH_LIT
    9  IR_MATCH_ALTERNATE        <- the outer one; the walk sees this
    10 IR_MATCH_ASSIGN_COND      <- reads the start at a STATIC [rsp+32]
    ...
    14 IR_MATCH_ALTERNATE        <- THE NESTED ONE. Never in range (7,10).

Branch bodies are emitted after the statement chain, so the offender sits **outside** the interval the
walk can see. **ζ liveness follows the NESTING; the walk follows the LINEAR ORDER; they disagree
exactly when an alternation sits inside a branch.** hq_C's `si=34 / ci=33` note (SAVE and COND adjacent
and reverse-ordered in `g_emit_cfg`) is the same fact from the other array — that one states the
symptom, this one states the cause.

### 7.4 Why no offset arithmetic could have worked

One compiled pattern, two subjects — `("a" ("z" | "b" ("c" | "d"))) . CAP`:

    "az"  -> [az]  CORRECT   (flat arm taken, 32 bytes live)
    "abc" -> [bc]  WRONG     (nested arm taken, 64 bytes live)

Same binary, same emission, opposite verdicts. Every `IR_MATCH_ALTERNATE` pushes 32 bytes of ζ-SPINE at
α and keeps it live for backtracking, so **the live depth at COND is an arm-taken-at-runtime fact.** A
static rsp offset cannot be right on both paths, so the home must be depth-INDEPENDENT — the RBP frame
cell, via the `frame_need_of` path that already existed for exactly this. That is the BB frame-placement
criterion as written: RESULT/LOCALS stay on the SPINE only while every consumer reaches them at a fixed
compile-time offset **on every path**.

### 7.5 Why the narrow predicate is sufficient — measured by hq_C, not assumed by me

I expected sibling (non-nested) alternations under one capture to need the broader test. **They do
not**: the existing flat-array gap walk already counts TOP-LEVEL alternations via
`alt_flat_live_bytes`, so only NESTED ones escape the count — exactly the set `alt_branch_has_nested_alt`
names. hq_C verified two- and three-sibling flat alternations pass on this cure alone, board
byte-identical. Recorded because it is the half I would otherwise have taken on faith.
