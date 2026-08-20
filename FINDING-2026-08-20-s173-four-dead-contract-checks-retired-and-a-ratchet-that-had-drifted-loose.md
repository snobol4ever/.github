# FINDING s173 — THE FOUR DEAD-CONTRACT CHECKS ARE RETIRED, AND THE GATE THEY LIVED IN HAD BEEN RED FOR SO LONG A GOAL FILE DOCUMENTED THE RED AS NORMAL

**Seat:** local `/home/claude6` (seat6), Claude Opus 5. **Picked up:** postoffice `QUEUE.tsv` row 18
`gates-retire-4` (HQ-55 ruling **"RETIRE ALL FOUR"**, recorded `GOAL-SCRIP-HQ.md:193`; census =
seat1's `FINDING-2026-08-19-s169-eight-audit-gates-were-scanning-a-tree-that-no-longer-exists.md` §3–§4).
**SCRIP** `3da13598` → **`9c97b89f`** (pushed) · **.github** this commit. Scripts and docs only — **zero compiler
source touched** (`git diff --name-only | grep ^src/` == 0), so no `.s` regen debt (RULES.md step 4).

## 1. THE RULING WAS EXECUTED, BUT EVERY CONTRACT WAS RE-MEASURED DEAD FIRST

s169 declared these four dead and s169's own §4 records that two of its repairs were **wrong on first
measurement**. So none of the four was deleted on the strength of the census alone. Re-measured at
`bd183811`, re-proven green after rebase onto `3da13598`:

| # | check | contract it enforced | re-measured s173 | disposition |
|---|---|---|---|---|
| 1 | `test_gate_em_template_matrix.{py,sh}` | every template fn carries an `IS_<BE>` arm for X86/JVM/JS/NET/WASM | **0** `IS_<BE>` tokens of any spelling in **all of `src/`**; **0 fns extracted from 144 files**; `rc=2 VACUOUS` | **DELETED** (186 lines) |
| 2 | `util_three_section_audit.sh` | every `PLATFORM_X86` block carries `MEDIUM_MACRO_DEF`+`MEDIUM_BINARY`+`MEDIUM_TEXT` | 140 audited, 3 OK, **137 MISSING — of which 129 are `bb_*.cpp`** | **DELETED** (44 lines) |
| 3 | `audit_concurrency_invariants.sh` check (a) | one `case TT_` per `lower_(value\|pattern\|goal)` role switch | **0** role dispatchers across all **7** lowerers; 0 occurrences of **any** spelling under `src/lower/` | **EXCISED** |
| 4 | `audit_concurrency_invariants.sh` check (d) | FACT-RULE blocks byte-identical across `GOAL-{SNOBOL4,ICON,PROLOG}-BB.md` | all **4** anchors grep == 0 in all **3** `-100` files; the three `-BB.md` files do not exist | **EXCISED** |

## 2. ⭐ THE SHARPEST FACT IS #2, AND IT GOT SHARPER AFTER s169 MEASURED IT

`util_three_section_audit.sh` demanded `MEDIUM_*` sections in **129 `bb_*.cpp` files**. RULES.md
**NO MEDIUM_\* IN TEMPLATES** demands **zero** `MEDIUM_*` in `bb_*.cpp` — and since s172 that is no longer
a shrinking known-red ratchet but a **hard ceiling of 0, negative-tested by injection**
(`test_gate_template_medium_invisible.sh`, verified green at ceiling 0 this session).

So the two checks were not merely disagreeing — **satisfying the audit would have failed the live gate, on
the same files, in the same tree.** s169 could still call the 137 "compliance, not debt" while the ratchet
sat at 3; at ceiling 0 the audit had become a machine that could only ever instruct a seat to commit a
RULES.md violation. That is a stronger reason to delete than "its contract is superseded", and it is why
this one could not have been left "red and loud" as s169 originally proposed.

**The doctrine had already propagated.** `GOAL-COMMAND-CENTRAL.md:328` carries a `[x]` CC-3 entry whose
stated lesson is *"even an empty arm must keep its `IF(MEDIUM_x, …)` slot so the three-section audit stays
GREEN"* — a seat following it today writes a guard the live gate rejects. The entry is history and stays,
but it now carries a ⛔ **THIS LESSON IS REVERSED** banner naming the ceiling-0 gate. **A retired check does
not take its doctrine with it; the doctrine has to be hunted down separately.**

## 3. THE GATE WAS PERMANENTLY RED, AND A GOAL FILE HAD NORMALISED THE RED

`audit_concurrency_invariants.sh` did not merely carry two dead checks. Check (d) emitted **6 VIOLATIONs**
on every run — two `check_block` calls × three `-100` files, each failing extraction — so the whole gate
exited **rc=1 unconditionally**. Measured before/after, same tree, same commit:

```
BEFORE: NOTE (a): 0 lower_(value|pattern|goal) role switches ... VACUOUS
        VIOLATION: LOWER FACT RULE: extraction EMPTY in GOAL-SNOBOL4-100.md   (×3 files)
        VIOLATION: EMITTER FACT RULE: extraction EMPTY in GOAL-SNOBOL4-100.md (×3 files)
        rc=1
AFTER:  OK: concurrency invariants hold (EMITTER one-dispatch, no stray bytes). rc=0
```

⭐ **THE COST IS VISIBLE IN THE RECORD.** `GOAL-RAKU-BB.md:666` (2026-07-10) had to write the red into a
handoff as weather: *"audit_concurrency_invariants (goal-doc anchors) + template_purity violations are
byte-identical at clean HEAD — pre-existing, stash-A/B-proven, not this change."* A seat spent A/B work
proving a **permanently-red gate wasn't its fault**, and every seat after inherited a gate whose rc=1 meant
nothing. **This is the s169 class inverted:** s169 found gates that printed GREEN while scanning nothing;
this one printed RED regardless of the tree. Both destroy the same thing — the exit code's meaning — and
the red one is worse, because a green vacuous gate is at least silent, while a permanent red actively
trains seats to ignore a channel. **A gate that cannot go green is not a gate, and its rc=1 is not a
verdict.** The green now printed is honest: the two surviving checks are live and were both negative-tested
this session (below).

## 4. THE SURVIVING CHECKS WERE NEGATIVE-TESTED, BECAUSE EXCISION CAN BLIND AS EASILY AS MIS-PATHING

Removing (a) and (d) also removed `HQ`, `LOWER_GLOB`, `goalfiles`, `check_block` and `CONCURRENCY_SKIP_D`.
Under `set -u` a missed reference would abort the script — which under a careless reading looks like a
failing gate, and under a worse one gets "fixed" by deleting the check that trips it. Both survivors were
therefore proven to still fire, not merely to still run:

- **EMITTER one-dispatch (dup `case IR_` within one switch).** Injected a duplicate `case IR_MATCH_ARBNO`
  into its own switch in a **scratch copy** of `emit.cpp` (isolated tree under the scratchpad — the real
  `src/` was never edited) → `VIOLATION: emit.cpp: case IR_ label duplicated WITHIN a single switch:
  IR_MATCH_ARBNO`, `rc=1`. Control arm on the unmodified copy: `rc=0`.
- **Template purity ratchet.** At ceiling 2 → `VIOLATION: template purity REGRESSED: 3 side-effects
  outside templates > baseline 2`, `rc=1`. At the shipped ceiling → `rc=0`.

## 5. ⛔ RIDER FOUND WHILE VERIFYING: THE PURITY RATCHET HAD DRIFTED LOOSE, 4 → 3

Not in the brief; found because §4 required measuring the true count rather than trusting the ceiling.
`PURITY_BASELINE` stood at **4** (s169's re-base from the doubled 8). The true count is now **3**:

```
bb_call.cpp:532  ·  bb_call_write_slot.cpp:60  ·  bb_match_replace.cpp:31
```

The s169 four **minus `bb_define.cpp`** — which is exactly the file seat6's own s172 `ab-cell-hoist`
(`51b73ce9`) emptied by moving the AB fn-cell store into `emit.cpp`. The drop is a real gain, not a
blinded scanner: the audit still prints `file:line` receipts for all three survivors.

**This is the s169 defect one notch quieter.** There, a doubled count *matched* a stale ceiling so the
ratchet never fired. Here the ceiling merely sat one above the truth — so a genuine regression back to 4
would have passed silently, and the gain from `ab-cell-hoist` was never locked in. **Re-based 4 → 3**,
negative-tested at 2. ⭐ **THE GENERAL RULE THIS EARNS: a ratchet is only sound if it is lowered every time
the count drops.** A ratchet is a claim about the true count, and the moment the code improves without the
ceiling following, the ceiling is a lie in the safe direction — which is still a lie, and still hides the
next regression. Ratchets need a *reason to be re-measured*; the medium gate got there by **computing** its
number (s169 §5), and every remaining typed ratchet is carrying this same latent drift.

## 6. REFERENCE SWEEP — WHAT A RETIRED SCRIPT LEAVES BEHIND

`PLAN.md` and `RULES.md` were already clean of all four (verified, not assumed — the brief's "sweep
PLAN/RULES references" resolved to a no-op). The live references were in goal files, and two were
**standing instructions to run a script that no longer exists**:

| where | what it was | action |
|---|---|---|
| `GOAL-RAKU-BB.md:447` | `test_gate_em_template_matrix.sh` named in a **mandatory before-every-commit** gate list | removed from the list; retirement noted inline |
| `GOAL-TEXTF-TEMPLATES.md:113` | `bash scripts/test_gate_em_template_matrix.sh   # 855/855` in a **Gates (every group)** block | line deleted |
| `GOAL-COMMAND-CENTRAL.md:377` | `bash scripts/util_three_section_audit.sh` → AUDIT GREEN in a gate list | line deleted |
| `GOAL-COMMAND-CENTRAL.md:328` | the reversed `IF(MEDIUM_x, …)` lesson (§2) | ⛔ REVERSED banner appended; history kept |
| `GOAL-SCRIP-HQ.md:195` | **"⛔ FOUR HQ DECISIONS OWED"** | marked ✅ DISCHARGED with the ruling + this rung's receipt; census kept |

Note the stale expected value in the second row — `# 855/855`, for a gate that had been extracting **0
functions**. Nobody had run it in long enough for a four-digit expectation to survive beside a script that
matched nothing.

**Deliberately NOT rewritten:** the s169 and s166 FINDINGs (8 + 1 hits). FINDINGs are the durable record of
what was true when written; editing them to match today's tree destroys the only evidence of the class.
**Queue-table row 18 in `GOAL-SCRIP-HQ.md` left to HQ** — the sanctioned close signal is
`s4e_msg.sh done gates-retire-4`, and the SELF-SELECT table is HQ's channel under the TWO-CHANNEL LAW.

**Final grep — zero live invocations of either deleted script remain anywhere in the tree.** All surviving
hits are the two FINDINGs, HQ's census, and the retirement notices minted here.

## 7. THE HEADER IS THE DEFENCE AGAINST RE-MINTING

Deleting a check deletes the reasoning that killed it, and the next seat to notice "LOWER has no
one-case-per-role check" is one grep from rebuilding check (a) against a shape that has not existed since
the src reorg. `audit_concurrency_invariants.sh`'s header therefore carries both retirements with their
measurements and an explicit **do NOT re-mint either from this header** — plus, for (a), the one line that
makes a future check correct rather than resurrected: *a LOWER check for the current shape must be written
against that shape.* The retirement is only finished when the corpse cannot be mistaken for a gap.

## 8. HANDOFF

Row 18 `gates-retire-4` DONE-WHEN met: **files gone or respec'd per the HQ-55 ruling** (2 deleted, 2
excised, all four re-measured dead first) · **reference grep clean** (§6, zero live invocations) · **this
FINDING**. Gate green and negative-tested; `test_gate_template_medium_invisible.sh` and
`test_gate_emit_no_lang.sh` re-run green. Rider §5 (purity ratchet 4 → 3) landed in the same commit and is
flagged here rather than folded in silently.

**⛔ FOR HQ — TWO ITEMS THIS RUNG EARNS.** (1) **Every typed ratchet in the tree should be audited for the
§5 drift** — `PURITY_BASELINE` had been one loose since s172 and nothing would have reported it; the cure
that already works is the s169 one, *compute the number, never type it*. (2) **`test_gate_template_medium_invisible.sh`'s
other half still reports 8 raw-byte producers in `xa_flat.cpp`** — different file, different shape, never
in the medium ratchet's scope (already named as residue on seat6's s172 board line); it wants its own row.
