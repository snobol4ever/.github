# FINDING 2026-08-12 (s29, Opus 5) — A PATTERN-VALUED VARIABLE IS SILENTLY DROPPED INSIDE A STORED PATTERN, AND s27's HANG IS THE LOUD ARM OF A MOSTLY SILENT CLASS

**Fingerprint:** SCRIP `fc5b0754` UNTOUCHED — **ZERO src bytes** · corpus `30838929` (⛔ NOT s27's `6c601c19` — origin moved under this seat; caught by handoff_status.sh, not by orientation) + 4 new witnesses in `probe/earn0/` with oracle-baked refs · `.github` this commit. **Measurement only.**
**Rung:** EARN-0, item (3) of s27's NEXT SEAT list — root-cause the `earn0_stored_varref` divergence. **Instrument:** SPITBOL oracle `x64/bin/sbl -b` vs `scrip --run` (m3), build green at HEAD (`make scrip` rc=0, `make libscrip_rt` rc=0, zero `error:`, zero 0-byte `.o`).
⛔ **NOT ADOPTED BY GOAL-RBP-EARN.** Root-causing it does not bill it here. Ownership is still open — see §6.

---

## 0. THE ONE-LINE RESULT

**A PATTERN-VALUED variable referenced inside a STORED pattern is read as NULL.** s27 filed this as "a stored pattern referencing a pattern-valued variable does not run at head," which named the crash but understated the class: **the crash is the minority arm.** The majority arm exits 0, prints plausible output, and is invisible to the entire corpus.

## 1. THE TWO ARMS, AND WHAT SELECTS BETWEEN THEM

The selector is **what the variable reference is concatenated with**, and it is visible in `--dump-ir`:

| composite | lowers to | HEAD behaviour |
|---|---|---|
| `Q = P` (bare) | `VAR P` → `ASSIGN Q` | **SILENT WRONG ANSWER** (P reads null) |
| `Q = P P` | `BINOP binop=11` over two `VAR P` | **SILENT WRONG ANSWER** |
| `Q = P 'bc'` | `BINOP binop=11` over `VAR P` + `LIT_STRING` | **SILENT WRONG ANSWER** |
| `Q = P LEN(2)` | `CALL "SNO$MKPAT"` PAT$1 + snapshot `PAT$1$V0` | **HANG rc=124, deterministic 8/8** |
| `Q = LEN(2) P` | same blob path | **SEGV rc=139** |
| `P = 'a'` ; `Q = P LEN(2)` | blob path, string operand | **CORRECT** ✅ |

⇒ **A sibling that is a PATTERN FUNCTION CALL routes the composite onto the BLOB path; anything else keeps it a plain BINOP concat.** On the BINOP path the pattern operand evaporates. On the BLOB path it does not evaporate — it hangs or faults instead.

**The last row is the control that scopes the defect:** the identical syntax with a STRING-valued variable is correct, so this is not "variables in stored patterns are broken," it is **pattern-valued** variables specifically.

## 2. ⭐⭐⭐ THE IR SHOWS THE ASSIGNMENT IS NEVER EMITTED

For `Q = P P` and `Q = P 'bc'`, statement 1 — `P = LEN(1)` — lowers to an **EMPTY STATEMENT**:

```
1@     2@   4@   STATEMENT_BEGIN        []
2@     3@   .    GOTO                   []
3@     4@   4@   STATEMENT_END          []
```

No `CALL SNO$MKPAT`, no `ASSIGN var="P"`. **P is never assigned at all**, so every later `VAR P` reads null and the composite degenerates to the null pattern — which matches everywhere, which is exactly the observed false MATCH.

For `Q = P LEN(2)` the SAME source statement DOES emit:

```
2      3    51@  LIT_STRING             [] "PAT$0"
3      4    51@  CALL                   [2] "SNO$MKPAT"
4      5@   51@  ASSIGN                 [3] var="P"
```

⇒ **The same statement compiles differently depending on how a LATER statement consumes the variable.** Whatever decides that is the first place to look. ⛔ **I did not identify the deciding code** — this is measured lowerer output, not a convicted line. Candidates worth a grep, in order: the `SNO$MKPAT`/`PAT$n$V0` snapshot construction in `lower_snobol4.c`, and `src/optimizer/dead_pure.c` / `copy_prop.c` (an assignment dead-stored because its only consumer looked value-less).

## 3. ⛔⭐⭐⭐ CORRECTION ON MYSELF — THREE OF MY FOUR CONTROLS WERE VACUOUS, AND THE VACUOUS READING IS THE ONE THAT MATCHES s27's

My first ladder recorded `Q = P P`, `Q = P 'bc'` and bare `Q = P` as **GREEN**, and I wrote a paragraph concluding the defect needed a pattern-function sibling. **All three were vacuous passes.** With subject `'abc'`, a compiler that honours P and a compiler that drops P **both print MATCH** — the arms predicted the same output, so the test could not discriminate.

Re-run with subjects where the two hypotheses diverge (`'a'` for `P P`, `'bc'` for `P 'bc'`, `''` for bare `P`), all three **DIVERGE**. That is a 3× swing in the size of the defect, produced entirely by choosing the subject correctly.

⛔ **This is the fifth conviction of the vacuous-A/B class in this goal** (s24's classifier, s37's killswitch A/B, s23's dead board, s27's own ARB control — and now mine). s27 wrote the rule down *one session ago* and I reproduced the error anyway. The rule as stated ("a control whose two arms predict the same output is not a control") is correct but is evidently not self-applying; what actually caught it was reading the IR and noticing the assignment was missing, i.e. **an instrument that could see the mechanism rather than the answer.** ⭐ **Recommend the sharper operational form: when a witness's expected result is MATCH/success, assume the control is vacuous until the arithmetic is shown to separate.** Every vacuous control in this file's history has been a success-expecting one.

⇒ **The new witnesses in `probe/earn0/` carry the discriminating subject and a comment saying not to "simplify" it.** A future seat that normalises them back to `'abc'` will silently re-hide the defect.

## 4. THE HANG IS INSIDE ONE STATEMENT, AND IT IS NOT CONSTRUCTION

Two bounded probes, both cheap, both decisive, neither needing gdb (which is dark on the hang class per s20):

- **`&STLIMIT = 25` does not stop it.** Still rc=124. A statement-level loop would have aborted at the limit. ⇒ **the loop is inside a single statement's execution — the match itself.**
- **Construction alone is GREEN.** `P = LEN(1)` ; `Q = P LEN(2)` ; `OUTPUT = 'BUILT'` with **no match statement** prints `BUILT`, rc=0. ⇒ **the defect is at MATCH time, not build time**, so `SNO$MKPAT` builds something; it is the consumption that diverges.

## 5. ⭐ THE rc=134 ARM IS NOT A GENERIC ABORT — IT NAMES ITSELF

s27 recorded `earn0_stored_capture` as flipping to "rc=134 SIGABRT (`Aborted`)". The abort carries a diagnostic worth recording verbatim, because it is a mechanism claim:

> `[ZHP] heap exhausted (512 MB, 0 blocks) after storage regeneration — raise ZC_HEAP_MB or build with -DZC_HEAP_STRINGS=0`

**A four-line program matching `'abc'` exhausting 512 MB is unbounded allocation**, and it sits in the same family as the deterministic hang. ⇒ **hang and heap-exhaustion are plausibly one mechanism (an unterminated match loop, one arm allocating per iteration and one not), not two defects.** ⛔ Plausible, NOT established — I did not instrument the allocation site.

**Reproduction note, correcting s27 on a detail:** `earn0_stored_varref` is **DETERMINISTIC on this build** — 8/8 rc=124, never SEGV. s27 saw it flip. `earn0_stored_capture` **is** genuinely nondeterministic (measured 8 runs: 3× rc=139, 2× rc=134, 3× rc=0-with-wrong-bind). So the nondeterminism is real but **per-witness, not class-wide** — the hang witness is a stable bisect target and the capture witness is not.

## 6. WHY THIS MATTERS TO RBP-EARN EVEN THOUGH IT IS NOT RBP-EARN's

EARN-0's rung text requires the table be hand-checked against witnesses compiled at HEAD, including a **fully constant-folded pattern**. Per manual p.122 construction is BY VALUE — only `*` defers — so these programs carry **NEITHER** hazard and EARN predicts **zero frames** in all of them. They are the law's simplest case.

⇒ **EARN-0 cannot be marked done while its simplest case is wrong at HEAD**, and the blocker is now characterised rather than merely reported. Two concrete consequences for the ladder:

- **EARN-1 should not consume `pat_static` blindly.** `IR_t.pat_static` is the OPAQUE test, computed as "transitive closure over spine-position VAR refs contains zero `TT_DEFER`." The BINOP arm shows a spine-position VAR ref that **the lowerer does not resolve to a pattern at all**. Whatever `pat_static` reports for these graphs, it is reporting it over an operand that has already been dropped. **Check what it returns on `earn0_varref_cat_dropped` before wiring it into `frame_need_of()`.**
- **EARN-2's census is unaffected.** It counts rbp establishments in emitted `.s`; a dropped operand does not move one. The s27 exoneration stands.

## 7. THE BOARD (m3, HEAD `fc5b0754`, oracle-baked refs, this container)

| witness | expected | got | rc | verdict |
|---|---|---|---|---|
| `earn0_varref_bare_dropped` | `NOMATCH/DONE` | `MATCH/DONE` | 0 | **FAIL — silent** |
| `earn0_varref_cat_dropped` | `NOMATCH/DONE` | `MATCH/DONE` | 0 | **FAIL — silent** |
| `earn0_varref_blob_hang` | `MATCH/DONE` | *(nothing)* | 124 | **FAIL — hang** |
| `earn0_varref_strvar_control` | `NOMATCH/DONE` | `NOMATCH/DONE` | 0 | **PASS — control** |
| `earn0_inline_control` (s27) | `MATCH V=[a]/DONE` | same | 0 | PASS |
| `earn0_stored_varref` (s27) | `MATCH/DONE` | *(nothing)* | 124 | FAIL |
| `earn0_stored_capture` (s27) | `MATCH V=[a]/DONE` | varies | 0/134/139 | FAIL |

## 8. NEXT SEAT, IN ORDER

1. **MONITOR-FIRST on `earn0_varref_cat_dropped`** — the silent arm, not the hang. It is 6 lines, exits 0, and its divergence is a WRONG ANSWER, which is the divergence class the 2-way sync-step monitor is actually good at. ⛔ **The hang witness is the WRONG first target** despite being louder: gdb is dark on the hang class (s20, ASLR falsified as cause) and a monitor on a program that never terminates has no second trace to align against. **Hunt the quiet one.**
2. **Find what makes `P = LEN(1)` emit nothing.** §2 names the candidates. This is very likely ONE decision and both arms fall out of it.
3. **Re-check whether the corpus is blind to the silent arm the same way it was blind to §8 of `FINDING-2026-08-11f`.** That one was blind because every passing capture test binds after fixed-length `LEN`; this one is blind because every passing stored-pattern test uses a **success-expecting subject**. Same shape of blindness, second instance in two sessions. **A sweep for success-expecting pattern assertions in `crosscheck/patterns` would size it.** Not run here.
4. **Then finish EARN-0's stored-form rows**, which are blocked on exactly this.

**Debts unchanged by this session:** regen ×3 owed from s24 (**zero src bytes here, adds none**) · ζ-MECH watermark re-baseline + H31/X01/X10 bisect · off-path r10/r11 residue · `board_demos_zeta.sh` m4 arm wrong as written · EARN-0b's generator row discharged by Lon ruling (0), s28.

**ENV:** `x64` oracle clones in ~15 s and `sbl -b` bakes refs directly — no reason to work without it. `install_system_packages.sh` rc=0 clean. `setsid` detached build confirmed necessary and sufficient again (`make scrip` + `make libscrip_rt`, ~3 min at nproc=1, rc=0 both, zero 0-byte `.o`). `scrip --dump-ir` was the instrument that broke this open — **it shows a dropped assignment that no amount of output-watching would have revealed.** `--help` is not a flag (`scrip: cannot open '--help'`); the flag list lives in `src/driver/scrip.c`.

---

# s29 CONTINUATION — THE STAGE IS BISECTED, THE OPTIMIZER IS EXONERATED, AND THE CLASS SPLITS INTO **TWO** INDEPENDENT DEFECTS THAT WERE MASKING EACH OTHER

## 9. STAGE BISECT — IT IS LOWER, NOT THE OPTIMIZER, AND NOT THE PARSER

⛔ **§2's candidate list was WRONG and is retracted here.** It named `dead_pure.c` / `copy_prop.c` — optimizer passes. **Both are exonerated by measurement**, not by argument:

| stage | instrument | `ASSIGN var="P"` present? |
|---|---|---|
| PARSE | `--dump-ast` | **YES** — `(STMT :eq :subj (TT_VAR P) :repl (TT_LEN (TT_ILIT 1)))` |
| LOWER + OPTIMIZER (default) | `--dump-ir` | **NO** |
| LOWER, OPTIMIZER OFF | `SCRIP_OPT=0 --dump-ir` | **NO — byte-identical to default** |

⇒ **The assignment never reaches IR. LOWER drops it, and the optimizer never sees it to drop.** ⭐ The stmt-1 AST is **CHARACTER-IDENTICAL** across the emitting (blob) and non-emitting (BINOP) arms, so the decision is driven entirely by **how a LATER statement consumes the variable** — the parser hands both arms the same tree.

⭐ **NOTE ON INSTRUMENT CHOICE, because RULES says MONITOR-FIRST.** The monitor is the WRONG instrument for this sub-question and that is not a licence to skip it — it is a class fact. The monitor aligns two engines' RUNTIME traces; the question here is why a COMPILER STAGE emitted nothing. There is no runtime to align, because the code was never generated. The correct mechanical instrument is the stage-by-stage dump bisect above, which is still measurement and still not code-reading. **Monitor-first resumes at the consumer defect (§11), which IS a runtime divergence.**

## 10. ⭐⭐⭐ THE PRODUCER IS NOT LOST — IT IS INLINED, AND THE INLINER IS CONVICTED BY KILLSWITCH

`M2`: `P = LEN(1)` then `'' P` used **DIRECTLY in match position**. The assignment is **NOT emitted** here either — **yet the program is CORRECT** (subject `''` chosen to discriminate: a dropped P would match null and print MATCH; scrip prints NOMATCH, agreeing with the oracle).

⇒ LOWER is **eliding the assignment and INLINING the pattern at its use site.** That is not a bug on its own; it is this goal's own invariant/constant-folded pattern machinery working. **The bug is that the inlining reaches a direct match position but NOT a use inside another stored pattern's construction**, where the reference falls back to reading a variable that was never assigned.

**CONVICTED BY KNOB, NOT BY READING** (`SCRIP_PAT_INLINE=0`, one command, no source read):

```
ASSIGN var="P" in IR:   default = 0        SCRIP_PAT_INLINE=0 = 1
```

**BY-SET BOARD, both arms, same container, same binary:**

| witness | default | `PAT_INLINE=0` |
|---|---|---|
| `earn0_varref_bare_dropped` | FAIL (silent, rc=0) | **PASS** ✅ |
| `earn0_varref_cat_dropped` | FAIL (silent, rc=0) | FAIL — **rc=124 HANG** |
| `earn0_stored_capture` | FAIL (wrong bind, rc=0) | FAIL — **rc=134 heap exhausted** |
| `earn0_varref_blob_hang` | FAIL rc=124 | FAIL rc=124 (**unchanged**) |
| `earn0_stored_varref` | FAIL rc=124 | FAIL rc=124 (**unchanged**) |
| `earn0_varref_strvar_control` | PASS | PASS (**inert**) |
| `earn0_inline_control` | PASS | PASS (**inert**) |

**1 REPAIRED · 0 BROKEN · 2 CONVERTED FROM SILENT TO LOUD · 2 UNCHANGED · inert on both controls.**

⛔ **THIS IS NOT A FIX AND MUST NOT BE SHIPPED AS ONE.** RULES: nothing may depend on a killswitch, and this file already records `SCRIP_PAT_INLINE=0` as **not a revert path**. It is used here strictly as a **diagnostic discriminator**.

## 11. ⭐⭐⭐ THE DECOMPOSITION — TWO DEFECTS, AND THE FAST ONE WAS HIDING THE SLOW ONE

- **DEFECT A — PRODUCER ELISION (LOWER).** The pattern-valued assignment is elided in favour of use-site inlining; a consumer inside another stored pattern's construction is **not** an inlining site, so it reads an unassigned variable ⇒ **null pattern ⇒ silent false MATCH, rc=0.** Convicted: `PAT_INLINE=0` restores the `ASSIGN` and repairs the bare case outright.
- **DEFECT B — CONSUMER PATH.** With the assignment **restored**, matching a stored composite that references a pattern-valued variable **HANGS** (`cat_dropped` rc=0 → rc=124) or **exhausts the heap** (`stored_capture` rc=0 → rc=134). The blob-arm hangs are **identical in both arms**, so B is **independent of the inliner**.

⭐⭐ **THE STRUCTURAL POINT, AND IT INVERTS HOW THE BOARD READS:** Defect A was **MASKING** Defect B. Dropping the operand made the program produce a fast wrong answer instead of running the broken consumer path at all. ⇒ **Fixing A ALONE WILL LOOK LIKE A REGRESSION** — silent rc=0 passes will become hangs. Any seat that repairs the elision and reads the resulting rc=124s as its own breakage will revert a correct fix. **Judge BY SET against this table, and expect the hang count to RISE when A is fixed.** That is the mask coming off, not new damage.

⛔ **AND IT GENERALISES BEYOND THIS WITNESS SET:** wherever the inliner elides a producer whose consumer is not an inlining site, the failure is a **fast plausible wrong answer**, which is the cheapest possible thing for a corpus to score as a pass. **The silent class is systematically under-counted by construction.**

## 12. NEXT SEAT — REVISED, SUPERSEDES §8

1. **MONITOR-FIRST on `earn0_varref_cat_dropped` UNDER `SCRIP_PAT_INLINE=0`.** ⭐ This is the change: at the default the program exits 0 with a wrong answer; with the knob off it HANGS, which is worse for the monitor. **So run the monitor at the DEFAULT** (terminating, wrong-answer divergence — the class the 2-way sync-step monitor is actually good at) to convict Defect A's consumer site, and keep the knob purely as the A/B discriminator.
2. **Defect A is a LOWER question:** why is a use inside a stored composite not treated as an inlining site, and why is the producer elided before that is known? ⛔ Candidate location `src/lower/lower_snobol4.c` (`SNO$MKPAT` / `PAT$n$V0` snapshot construction) — **UNCONVICTED, named as a starting grep only.**
3. **Defect B needs its own witness and its own owner** — it is reachable only with the knob off today, which means it has **no default-arm reproducer** until A is fixed. Record it now or it will be re-derived from scratch after A lands.
4. **Corpus blindness, second structural instance in two sessions.** `FINDING-2026-08-11f` §8: every passing capture test binds after fixed-length `LEN`. Here: every passing stored-pattern test uses a success-expecting subject. **A sweep of `crosscheck/patterns` for success-expecting assertions would size it.** NOT run here.
5. Then EARN-0's stored-form rows, blocked on exactly this.

**⛔ SECOND SELF-CORRECTION THIS SESSION.** My first killswitch board scored **every** witness FAIL rc=1 — including a control that passes at the default. The uniform failure across a known-good control was the tell: I had dropped the `.sno` extension, so every invocation was file-not-found, and rc=1 was the shell reporting a missing file rather than the compiler reporting anything. **A board on which the control fails is measuring the harness, not the program** — same family as s23's dead board and s20's `SCRIP_WREG` no-op arm. ⭐ **Cheap standing guard, recommend adopting: every by-set board must carry a known-PASS control row, and a run in which the control fails is VOID, not a result.** It cost one command to catch here because the control was already in the table.

---

# s29 CONTINUATION (2) — THE BLAST RADIUS IS CENSUSED, MY OWN CENSUS INSTRUMENT IS DARK ON THE CLASS IT WAS BUILT FOR, AND TEN PASSING PROGRAMS CANNOT BE CLEARED — FOUR OF THEM CARRY A LANDED REPAIR CLAIM

## 13. THE A/B SWEEP — 183 PROGRAMS, BOTH ARMS, SAME BINARY, SAME CONTAINER

`SCRIP_PAT_INLINE` default vs `=0` over `crosscheck/patterns` + `crosscheck/capture` + `probe` + `probe/earn0`:

| quantity | value |
|---|---|
| scored | **183** |
| PASS at default | 113 |
| PASS at `PAT_INLINE=0` | 114 |
| behaviour **DIFF** between arms | **5** |
| REPAIRED by the knob | **1** |
| BROKEN by the knob | **0** |

The 5 whose behaviour the inliner changes: `128_pat_recursive_grammar_right_rec` (139→124) · `dc_nest_bt` (rc=0 FAIL→139) · `earn0_stored_capture` (139→0) · `earn0_varref_bare_dropped` (**FAIL→PASS**) · `earn0_varref_cat_dropped` (rc=0→124). **All five already FAIL at the default**, so no landed pass depends on the elision.

⭐ **A quotable side fact: the elision buys ZERO correctness across 183 programs (0 BROKEN by turning it off) and costs at least one (1 REPAIRED).** It is presumably a performance mechanism, so no correctness benefit is expected — but it is worth recording that it is not load-bearing for correctness anywhere in these corpora, because that is what makes it safe to change.

## 14. ⛔⭐⭐⭐ THIRD SELF-CORRECTION — I BUILT A CENSUS THAT IS BLIND TO THE CLASS IT WAS BUILT FOR

I ran §13 to size the SILENT class and reported "**0 vacuity suspects**." **That number is not evidence of absence, and the instrument cannot produce evidence of absence.**

> **A vacuous pass is BY DEFINITION one where correct behaviour and defective behaviour produce the same output.** So flipping the knob does not change its output, it scores **SAME**, and it is invisible to an A/B sweep. **The knob detects exactly the programs that are NOT vacuous.**

⇒ **§13 answers a different question than the one I built it for.** It measures *programs whose observable output the inliner changes* (5). It says **NOTHING** about *programs that pass vacuously*, which is the entire silent class. ⛔ **Do not cite "0 vacuity suspects" as a clean bill of health — it is a DARK BOARD in the s26 sense, and the darkness is structural, not fixable by running it longer.**

**This is the THIRD instance of one error in one session** — vacuous controls (§3), a board whose control row failed (§12 close), and now a census whose arms coincide on the target class. All three are the same shape: **an instrument whose two arms agree precisely where the defect lives.** ⭐ The generalisation worth adopting house-wide: **before trusting any A/B, state what the defective arm would print and confirm it DIFFERS from what the correct arm prints, FOR THE CLASS UNDER TEST.** If they coincide, the A/B is measuring something else, however green it looks.

## 15. ⭐⭐⭐ THE POPULATION AT RISK, MEASURED STATICALLY — AND TEN PROGRAMS THAT CANNOT BE CLEARED

Since the knob is structurally blind, the population was sized by the **static trigger shape** instead: a variable assigned a pattern-producing expression, later referenced on the RHS of **another** assignment (consumed inside a stored composite rather than at a match site).

| quantity | value |
|---|---|
| programs scanned | 185 |
| carry the **trigger shape** | **47** |
| of those, **PASS at default AND SAME across arms** | **10** |

**Those 10 cannot be cleared by any instrument used in this session.** Each needs a discriminating subject. Classified by whether its own `.ref` is self-discriminating (a `.ref` expecting a NOMATCH/failure line could not be produced by a degenerate null pattern, which matches everywhere):

| program | ref | verdict |
|---|---|---|
| `108_pat_fence_via_var_basic` | `star-cmd matched LEN(1) then continued` | **SUSPECT** |
| `117_pat_arbno_of_star_var_fence` | `arbno-star-cmd matched aaa` | **SUSPECT** |
| `118_pat_arbno_of_star_var_fence_seal_blocks` | `arbno-star-cmd FENCE sealed` | **SUSPECT** |
| `119_pat_arbno_of_fence_via_var_via_outer` | `triple-indirect FENCE sealed` | **SUSPECT** |
| `123_pat_regex_alt_class` | `token: abc` | **SUSPECT** |
| `125_pat_json_literal` | `lit=true` | **SUSPECT** |
| `129_pat_arbno_star_var_fence_with_alts` | `beauty-class FENCE seal held` | **SUSPECT** |
| `148_pat_arbno_star_var_fence_short` | `seal blocks ab retry` | **SUSPECT** |
| `149_pat_arbno_star_var_fence_outer_pre_match` | `arbno-star-cmd FENCE sealed` | **SUSPECT** |
| `pt_inline_1_full` | `hit=A` | **SUSPECT** |

**10 of 10 are purely success-shaped** — a single success string, no failure line anywhere. **Not one of them can distinguish an honest pass from a vacuous one.** This is the corpus blindness of `FINDING-2026-08-11f` §8 measured rather than asserted, and it is the **third structural instance in two sessions** (that one: every passing capture test binds after fixed-length `LEN`).

## 16. ⛔⭐⭐ THE FLAG THAT MATTERS MOST — FOUR OF THE TEN CARRY A LANDED REPAIR CLAIM

**`119` · `129` · `148` · `149` are exactly the four programs s22's cursor bills as REPAIRED by W-MAP (3)**, recorded there as *"one coherent class (ARBNO × FENCE × deferred `*var` = suspension-and-resume through a deferred reference)."*

All four carry the trigger shape. All four are success-shaped-ref-only. All four are SAME across both knob arms.

⛔ **THIS IS NOT A CLAIM THAT s22's REPAIR IS FALSE.** They may well pass honestly, and W-MAP (3) may have repaired exactly what it says. **The measured statement is narrower and it is still serious: their tests are structurally incapable of telling the difference, so "4 repaired" rests on assertions no instrument in the tree can currently check.** Given that this session found three of its own A/Bs blind for this precise reason, and that this file has convicted the vacuous-A/B class five times, **the four should be re-verified with discriminating subjects before "119/129/148/149 repaired" is treated as settled.** Cheap: one added `.ref` line each that a null pattern could not produce.

⭐ `pt_inline_1_full` is in the same list and is a **named WREG-5 gate witness**. A gate witness that cannot fail for the right reason is a weak gate. Same remedy.

## 17. NEXT SEAT — SUPERSEDES §12's ORDERING ONLY WHERE IT CONFLICTS

1. **UNCHANGED AND STILL FIRST:** MONITOR-FIRST on `earn0_varref_cat_dropped` **at the DEFAULT arm** (terminates there; hangs under the knob).
2. **NEW, AND CHEAP:** give the 10 programs of §15 a discriminating assertion — one `.ref` line a degenerate null pattern could not produce. **Start with `119/129/148/149`** (§16, landed repair claim) then `pt_inline_1_full` (gate witness). This is corpus work, no compiler edit, and it converts 10 unclearable programs into 10 that can be graded.
3. Defect A (LOWER elision) and Defect B (consumer path) per §11–§12, unchanged.
4. ⛔ **Do not cite §13's "0 vacuity suspects."** Cite §14 instead: the instrument is structurally dark on that class.

---

# s29 CONTINUATION (3) — THE FOUR ARE MEASURED, NOT SUSPECTED: THEY ASSERT A **FAILURE**, SCRIP PRODUCES THAT FAILURE FOR THE WRONG REASON, AND s22's "4 REPAIRED" DOES NOT SURVIVE A DISCRIMINATING SUBJECT

## 18. ⛔ CORRECTION TO MY OWN §15 RATIONALE — THE VERDICT WAS RIGHT, THE REASON WAS WRONG

§15 classified the ten as SUSPECT because their `.ref` text is *success-shaped prose*. Reading the programs shows the real and far worse reason. `119` / `129` / `148` / `149` are all:

```
        cmd   = FENCE('a' | 'ab')
        outer = ARBNO(*cmd)
        s POS(0) *outer RPOS(0)          :S(BAD)F(GOOD)
```

**They assert on the FAILURE branch.** The expected outcome is that the match FAILS; the "GOOD" string is printed by `F(GOOD)`. My keyword classifier scored them SUSPECT for finding no failure word in the ref — correct verdict, wrong mechanism, because the authors gave the failure branch positive-sounding prose.

> ⭐⭐⭐ **THE GENERAL LAW, AND IT IS SHARPER THAN THE ONE I WROTE IN §14: A TEST THAT ASSERTS A FAILURE IS PASSED BY EVERY DEFECT THAT CAUSES FAILURE.** Total loss of the pattern is such a defect: `ARBNO(null)` matches only the empty string, so `POS(0) … RPOS(0)` cannot span a multi-character subject and fails — printing the identical GOOD string. **Honest FENCE sealing and total pattern loss are indistinguishable in all four.** ⛔ Note this also kills the poison-the-variable discriminator: poisoning still yields failure, so it too agrees on both arms.

## 19. ⭐⭐⭐ THE POLARITY-INVERTED WITNESS — MEASURED, WITH ITS SEPARATION PROVEN

Same idiom, subject `'aa'`, chosen so the CORRECT answer is a **MATCH**:

- honest: `ARBNO(FENCE('a'|'ab'))` takes `'a'` then `'a'` → cursor 2 → `RPOS(0)` → **MATCH**
- degenerate: `ARBNO(null)` matches only empty → `POS(0)…RPOS(0)` on `'aa'` → **FAIL**

| witness | oracle | scrip | verdict |
|---|---|---|---|
| `earn0_disc_arbno_star_fence_positive` | `arbno-star-cmd spanned aa` | `FAILED: pattern did not span aa` | ⛔ **DIVERGE** |
| `earn0_disc_arbno_star_fence_poisoned` (separation proof) | `FAILED: pattern did not span aa` | same | AGREE — **required** |

⭐ **The separation is PROVEN, not assumed:** the poisoned control draws the OPPOSITE answer from the oracle, so the subject genuinely discriminates. (A discriminator whose arms give the oracle the same answer is not one — the trap this session hit three times.)

⇒ **AT HEAD, SCRIP CANNOT SPAN `'aa'` WITH THE `ARBNO(*cmd)` IDIOM.** Its behaviour on the polarity-inverted witness is exactly what a degenerate null pattern produces. Deterministic, rc=0, wrong answer.

## 20. ⛔⭐⭐⭐ CONSEQUENCE FOR s22's LANDED REPAIR CLAIM

s22's cursor bills `119 · 129 · 148 · 149` as **REPAIRED by W-MAP (3)**, *"one coherent class (ARBNO × FENCE × deferred `*var` = suspension-and-resume through a deferred reference)."*

**MEASURED:** SCRIP fails this idiom's match even where the match must succeed. Therefore those four pass **because SCRIP fails the match**, which it does for this shape regardless of whether the FENCE seal works. **Their passing is not evidence that suspension-and-resume through a deferred reference was repaired.**

⛔ **STATED PRECISELY, because the distinction matters:** the four programs **do** pass, and W-MAP (3) **may** have repaired something real. What is falsified is the **evidentiary basis**: a failure-asserting test cannot witness a repair whose failure mode is also failure. **"4 REPAIRED" should be downgraded to UNWITNESSED until re-measured against `earn0_disc_arbno_star_fence_positive` or an equivalent polarity-inverted witness.** This is the fourth by-set claim in this file to fall to an instrument that could not discriminate, and the first to fall by a witness rather than by argument.

⭐ **AND THIS IS NOW THE BEST MONITOR TARGET IN THE GOAL** — better than `earn0_varref_cat_dropped`: it is 7 lines, **deterministic**, **terminates**, exits 0 with a **wrong answer** (the class the 2-way sync-step monitor is built for), and it sits in the ARBNO × FENCE × `*var` family this goal cares about most, with a proven-separating control beside it.

## 21. NEXT SEAT — SUPERSEDES §17 ITEMS 1–2

1. **MONITOR-FIRST on `earn0_disc_arbno_star_fence_positive`** (was: `earn0_varref_cat_dropped`). Same class, same instrument, but this one lands inside ARBNO × FENCE × `*var` and carries a proven separation control.
2. **Re-grade `119/129/148/149` and downgrade s22's "4 REPAIRED" to UNWITNESSED** in the s22 cursor. ⛔ Do NOT mutate those four in place — they are `board_patterns_set.sh` baseline members and s22's numbers are quoted against them. **Add polarity-inverted siblings**, as done here.
3. Remaining six of the ten (§15) still need the same treatment; `pt_inline_1_full` (WREG-5 gate witness) first.
4. Defects A and B (§11) unchanged.
