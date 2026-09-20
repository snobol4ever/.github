# FINDING 2026-09-20 hq_snobol4 — 30 of the 31 SNOBOL4 `no_layout` entries are the census materializing them without their includes, and the bucket printed a cause it never measured

**TREE OF EVERY NUMBER:** SCRIP `fff6d8a82` (plain `origin/main`) · corpus `86574b2bf` · `.github` `cfdc051b` · `RT_OPT=-O0` · RT_TAG `f65f143e2f` · one box, incremental build, `make buildinfo` read before measuring.
**BRANCH (superseded):** SCRIP `55d2ab49e` on `hq_snobol4/zls-census-materializes-entries-without-their-companions`.
**LANDED ON MAIN:** the companion half is the `cto`'s **`83fb80ee7` (CTO-96)**, landed while I was measuring it; the member-naming half is mine, **`5b5f0e236`**, on top of theirs.

## 0. ⛔ CREDIT AND A CONCURRENCY LESSON, BEFORE ANY OF MY NUMBERS

**THE `cto` REACHED THE SAME CAUSE AND LANDED IT FIRST.** `83fb80ee7`'s own subject is *"THIRTY of the seventy-two no_layout entries were the instrument, not the compiler"* — the same 30, the same mechanism. I measured it independently and only discovered theirs when my branch would not fast-forward. **I reproduced their landing on `553678ec2` before adding a line:** `graded=1981 graphs=4506 words=314812 no_layout=1 holes=0 unkinded=0`, identical to my branch's numbers. Their cure copies companions from `corpus/tests/<lang>` **and** `corpus/include` into the shared temp dir, which reaches the same place my `SNO_LIB` arm did.

⛔ **WHAT I ACTUALLY ADDED IS SMALL AND I AM NOT GOING TO DRESS IT UP:** the `NO-LAYOUT` row printed a bare `(rc=1)`. Everything in §5 below — the classification of the *remaining* 42 across three languages — was only obtainable because I printed the refusal's first line. That is `5b5f0e236` and it is the whole of my code delta.

⛔ **AND THE PROCESS LESSON IS MINE TO PAY FOR:** I measured for most of an hour before telling anyone, so the `ceo` read my seat as idle and the `cto` spent their own hour on a cause I already had in hand. **A measurement that has not been telegrammed does not exist to the fleet**, and the digest already says it in another voice — *write the measurement before it leaves your head; a telegram is not a landing* — but the converse is the half that bit here: **a landing is not a telegram either, and the telegram is the cheaper of the two to send first.** The four-arm A/B in §3 was worth sending at arm A.

⭐ **ONE THING THE DUPLICATION BOUGHT, SO IT IS NOT A TOTAL WASTE:** two seats reached `30 of 31` independently, by different routes (theirs a companion-path declaration, mine a four-arm ablation), and got byte-identical census lines. That is a stronger result than either pass alone.

## 1. Why this row at all

CEO-993 put **the 72 `no_layout` graphs** on the acceptance test as a DENOMINATOR HOLE and therefore first side; MODE line 2 gives **31 of the 72** to this seat. My own assigned row is blocked in the `ceo`'s/`cto`'s region (CFO-125 named the cure as the zeta local-slot planner's value region), so this is the other first-side GC thing my lane owns. It is GC: the population is the compile-time frame maps, ARCH-GC section 7 F1.

## 2. What the bucket actually holds

`util_zls_frame_map_census.py` materialized each master entry's text into **ONE FLAT temp dir** and ran `scrip --dump-zeta` there with **no companion copy and no `SNO_LIB`**. The grader — `corpus_suite_harness.run_suite_entry` — does **both**: it copies `-INCLUDE`/`open()`/`INPUT()` companions to transitive closure via `_copy_companions`, and it sets `SNO_LIB=<corpus>/include` on every m3 run and m4 compile. So every master entry naming a companion failed to **PARSE** inside the census and fell into `no_layout`.

⛔ **And `util_gc_census.py` prints that bucket as `no_layout=N NAMED AND UNCOUNTED (the compiler refused those entries; they are not a pass)`** — a **CAUSE THE TOOL NEVER MEASURED**, false for 30 of my 31. This is the `coo`'s own new bar failing in the field: *every bucket a fleet instrument prints should be answerable to "name one member of this count."*

## 3. The four-arm A/B, one variable at a time, same extraction authority the census uses

| arm | companions | `SNO_LIB` | recovered of 31 |
|---|---|---|---|
| A (reproduces the census — positive control) | no | no | **0** |
| B | yes | no | 8 |
| C | no | yes | 19 |
| D | yes | yes | **30** |

⭐ **Neither ingredient alone suffices and they are not nested** (8 and 19 overlap but neither contains the other). Arm A reproducing `graded=0 no_layout=31` exactly is what licenses the other three.

## 4. The census before and after, with the patch applied

```
BASE  ZLS-MAP lang=snobol4 graphs=4008 words=170578 unkinded=0 holes=0 graded=1951 no_layout=31
HEAD  ZLS-MAP lang=snobol4 graphs=4506 words=314812 unkinded=0 holes=0 graded=1981 no_layout=1
```

- ⭐ **`holes=0` and `unkinded=0` THROUGHOUT.** The 30 recovered entries add **498 graph instances / 231 distinct `(graph-name, region_end)` shapes / 144,234 words** and bring **no hole**. This is completeness evidence, not a new defect — the frame maps were already clean over a population nobody had censused.
- ⛔ **THE HONEST SIZE, AND ENTRY COUNT RADICALLY UNDERSTATES IT:** the bucket was **1.6% of entries (31/1982) but 45.8% of the censused words (144,234/314,812)**. These are the big multi-include programs — 290 words/graph against the rest of the master's 42.6.
- **Other six languages:** rebus, snocone, pascal byte-identical. **icon words 164,348 → 164,358** (+10; one graph grew — the census now materializes what the grader materializes). **raku 31 and prolog 10 DO NOT MOVE.**
- **Cost:** full seven-language sweep **34.7s → 37.4s**, same box, back to back.

## 5. The one real survivor, and the other two languages' buckets NAMED

Because the patch also prints `rc` **with its first line**, every `NO-LAYOUT` row now names its own reason:

- **snobol4, 1 real:** `trim_alt_keyword_replace_branch_1` — `rc=1: FATAL lower_snobol4 (GZ#5 subset): lambda(expr), the CONDITIONAL pattern lambda, is not implemented yet`. A red-on-purpose witness authored before its cure, per RULES.md THE INSTRUMENT LAWS clause 3. Honestly `no_layout`.
- **raku, 31, all real (NOT this shape):** `rc=1: raku parse error line 1: syntax error` — `test_stmt_pfx_BEGIN`, `_CHECK`, `_END`. A frontend gap in the statement-prefix family.
- **prolog, 10, all real (NOT this shape):** `rc=2` — `global_vars_b_setval_getval_1`, `builtin b_getval is not on the ladder yet -- rung 10 lands it`. Honest REFUSALS.

⛔⭐ **So the fleet's 72 is 42 REAL and 30 ARTIFACT, and the 42 are three NAMED unlanded-feature gaps, not a mystery.** ⛔ **And the bucket folded `rc=1` (a red) beside `rc=2` (a could-not-measure)** — the two classes the Makefile keeps apart everywhere else. That is the same defect one level out.

## 6. Why it landed, and the one hazard I checked and did NOT find

I had this as an ASK, not a landing — `util_zls_frame_map_census.py` is the `ceo`'s tool (CEO-820; `ZLS-MAP` token frozen CEO-821) and MODE line 2 gives the instruments to the `coo`. ⛔ **Lon overrode that in chat — *"put your work on the main branch"* — so it is on main, and this section is the override routed the same sitting** per THE MAIL LOOP clause 5. The `ZLS-MAP` token is untouched; only the `NO-LAYOUT` prose moved.

⛔ **A HAZARD I SUSPECTED IN THE LANDED CURE AND REFUTED RATHER THAN REPORTED:** both versions copy companions into **one flat temp dir shared by all 1982 entries**, so two entries naming the same basename with different content would collide and one would be censused against the wrong include. **MEASURED: 51 companion basenames referenced across the snobol4 master, ZERO with same-name-different-content across the two copied dirs.** The hazard is **latent, not live**, and it is recorded here as latent. My own branch used per-entry subdirs, which is immune — but immune to something that does not happen today is not a reason to land a bigger diff.

**GREEN ON THE BRANCH:** `test_gate_gc_raku_every_frame_slot_has_a_kind` PASS(0) · `test_gate_gc_pas_every_frame_slot_has_a_kind` PASS(0) · `test_gate_gc_instrument_censuses_are_wired_and_trip` PASS, 7 of 7 arms · the `SCRIP_TEST_PLANT_ZLS_HOLE` detector arm **still RED as it must be** (`holes=2`, rc=1) · `--files` path unchanged · `make preflight` 56 arms 0 red.

## 7. The generalisation

⭐⭐ **AN INSTRUMENT THAT RE-IMPLEMENTS ANOTHER INSTRUMENT'S SETUP WILL DRIFT FROM IT SILENTLY, AND THE DRIFT PRINTS AS A PROPERTY OF THE PROGRAM.** The census had the ONE extraction authority for *reading* entries — it imports the harness's own readers — and then hand-rolled the *materialization* the harness also owns. Reading and materializing are both part of "what the grader does", and taking one and not the other is what put 45.8% of the word population into a bucket labelled with the compiler's name. The cure is not "add includes"; it is **materialize through the grader's own function**, which is what the branch does (`H._copy_companions`, the same `SNO_LIB`, the entry's own cwd).

⭐ This is the same shape as the `coo`'s finding-counter cure this morning and my own `map_only` reading yesterday, and it **fails in the same direction as both: DOWNWARD.** A census that grades fewer entries than it could reports a *cleaner* frame-map world than it has measured, and nobody investigates a clean census.
