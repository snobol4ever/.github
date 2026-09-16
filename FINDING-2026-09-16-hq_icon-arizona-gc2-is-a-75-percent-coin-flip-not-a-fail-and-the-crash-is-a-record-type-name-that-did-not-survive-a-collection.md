# FINDING 2026-09-16 hq_icon — arizona gc2 is a 75% coin flip, not a FAIL, and the crash is a record type name that did not survive a collection

**Tree:** SCRIP `bd4ae832a` (my Icon cset landing on top of origin `a4e800207`), corpus `ef22d72a2`, RT_OPT=-O0, incremental `make`.
**Provenance:** raised by the coo 2026-09-16 10:17 CDT as *"ONE RED ON YOUR BOARD ... arizona gc2 reads m3 FAIL, m4 CRASH on origin a4e800207 ... window 112912014..a4e800207"*, copied to the cfo and the ceo.

## 1. THE HEADLINE IS NOT THE CRASH, IT IS THAT THE PROGRAM IS NONDETERMINISTIC

`corpus/packages/icon/arizona_tests/general/gc2.icn` does not fail. It **flips**.

    m3, same binary, same input, back to back:   15 SIGSEGV (rc=139) / 20 runs
    passing runs:  256 output lines, byte-identical to gc2.std
    failing runs:  31 output lines, then SIGSEGV — always the same place

The crash point is stable even though its *occurrence* is not: it always dies immediately after the
fourth `----------` separator, i.e. inside test block 5, `"<b>5"`, the first **recursive** nonterminal.

⛔ **THIS INVALIDATES THE BISECT, NOT MERELY ITS PRECISION.** The window `112912014..a4e800207` rests on
gc2 reading PASS in both modes on `112912014` at 2026-09-13T12:49Z. At a ~25% pass rate, **one green run is
about two bits of evidence**, and an already-broken tree returns it roughly one try in four. The six `sno:`
runtime landings inside that window are therefore *not* established as suspects. Any re-bisect needs N runs
per commit and a crash **rate**; a single green per commit cannot distinguish the two hypotheses.

⭐ **The trap is live and it caught the author of this finding.** My first invocation of gc2 printed `rc=0`
and I was one keystroke from filing "does not reproduce". A flaky witness graded once is indistinguishable
from a cured one — this is the same narrow-instrument family as `command -v` and `$?`-after-a-pipe already
recorded in every seat digest, wearing the clothes of a *test result* rather than a shell idiom.

## 1b. AND THERE IS DOCUMENTARY PROOF THE WINDOW IS WRONG: A ROW FOR THIS WAS MINTED 2026-09-03

`/home/resources/postoffice/tasks/icon-arizona-segv-buildplan-tweak-nonterm-gc2.task.md` — minted by seat13 on
**2026-09-03T21:01:30Z**, owner `hq_icon`, still **FREE** — opens:

> `corpus/packages/icon/arizona_tests/general/gc2.icn` SIGSEGVs rc=139, zero stderr, censused under
> `icon-arizona-class-silent-segv-no-diagnostic`.

So gc2 was already crashing **ten days before** `112912014` (2026-09-13), the commit the window treats as its
last-known-good. Statistics alone said one green run was weak evidence; the queue says the tree was never good.
⛔ **The window `112912014..a4e800207` should be withdrawn, and the six `sno:` core.c landings inside it
exonerated** — they are not implicated by any evidence that survives contact with this row.

⭐ **THE TWO BACKTRACES ARE DIFFERENT SITES IN THE SAME FILE, AND THAT IS ITSELF THE CLUE.** The 2026-09-03 row
recorded SIGSEGV inside `vsnprintf`/`snprintf` from `rt_fire_buildplan_tweak` (`by_name_dispatch.c:618`,
formatting a `"%s__TWEAK"` string) ← `dat_construct` (`src/driver/driver_data.c:374`) ←
`try_call_builtin_by_name_bl("nonterm", ...)`. Today's is `strlen` from `descr_cstrlen(0x3)` ←
`bn_type_datatype` (`by_name_dispatch.c:5764`) ← `try_call_builtin_by_name_bl_s("type", ...)`. **Same file, same
`nonterm` record, same shape — a corrupted `char *` consumed by whichever function reaches it first.** That is
precisely what a nondeterministically-corrupted pointer looks like across runs, and it is why two seats looking
at two backtraces could reasonably have filed them as two defects. They are one.

⛔ **A ROW ALREADY EXISTS — DO NOT MINT A SECOND.** `icon-arizona-segv-buildplan-tweak-nonterm-gc2` is FREE and
carries the 09-03 evidence; its own `## NEXT` asks for exactly the minimization attempted here. Its cure surface
is the collector, so under MODE DECTET it wants `reown` to the cfo rather than a new row beside it.

## 2. THE ROOT CAUSE — A HEAP POINTER READ AS A C STRING AFTER A COLLECTION

gdb, caught on the first attempt:

    #0  __strlen_evex ()
    #1  descr_cstrlen (s_=0x3 <error: Cannot access memory at address 0x3>)   src/runtime/core/core.h:10
    #2  bn_type_datatype (fn="type", args=..., nargs=1, out=...)              src/runtime/by_name_dispatch.c:5764
    #3  try_call_builtin_by_name_bl_s (fn="type", ...)                        src/runtime/by_name_dispatch.c:6440
    #4  rt_call_arr_impl (fn="type", ...)                                     src/runtime/by_name_dispatch.c:5177
    #5  rt_call_arr_bl_s                                                      src/runtime/by_name_dispatch.c:5118
    #6  rt_call_arr_bl_strict                                                 src/runtime/by_name_dispatch.c:5109

`by_name_dispatch.c:5764` stores `STRVAL(t)` into `*out`, and **`t` is `0x3`**.

The path is the **record arm** of Icon's `type()`. For `av.v == DT_DATA`, `bn_type_datatype` takes `t` from
one of two heap pointers — `tag.s`, where `tag` is `FIELD_GET_fn(av, "gen_type")`, or otherwise
`di->type->name` off the `DATINST_t`. gc2 declares four records (`nonterm`, `charset`, `query`, plus the
grammar tables) and runs `case type(symbol) of` over instances of them inside `gener()`, **immediately after
the main loop calls `collect()`**.

⭐ `0x3` is not a wild address. It is a small integer sitting where a `char *` belongs — the signature of a
pointer the collector did not adjust, not of a stray write.

## 3. WHY THIS IS THE SAME CLASS AS `icon-gc-rung-2`, AND WHY IT IS A BETTER INSTRUMENT THAN THAT ROW HAS

hq_V's standing evidence on `icon-gc-rung-2` is that `by_name_dispatch.c` carries the fleet's largest
concentration of `rt_pinned_alloc` sites — **183 lines, re-measured here on `a4e800207`** — "each a candidate
holder of an unregistered interior pointer", and that *a block that survives only because it cannot move has
no root, it has an alibi*. A record type name reached through `FIELD_GET` on a `DT_DATA` is exactly that shape.
hq_V's blocker 4 is the same defect one table over: `_func_buckets` is a static array of heap pointers that
`core_gc_roots` never walks (re-confirmed statically on this tree — it visits `_var_buckets` and `_udef_types`
and nothing else).

⭐ **gc2 is the discriminating arm that rung does not have.** `icon-gc-rung-2` is graded today by a 4M-list
churn measured in **RSS**, and hq_V's own 2×2 showed each half of the cure moves that number by almost nothing
alone. An RSS figure is a poor instrument for a *rooting* defect. gc2 is 200 lines, it reds about three runs in
four on origin today, and it fails by naming a **specific corrupted pointer** rather than a megabyte count.
Note also that rung's DONE-WHEN short-circuits on a `grep` and never reaches its four gates — and those four
gates are green on the clean tree, while gc2 is red on it.

**Ownership:** the collector is the cfo's node under MODE DECTET, so this is routed, not cured. Filed by the
Icon HQ because gc2 sits on the Icon board.

## 4. A SECOND MEASURED FACT, FOUND WHILE PROVING THE FIRST: SOME ICON GATES ARE FLAKY TOO

Sweeping all **101** `test_gate_icn_*` / `test_gate_icon_*` gates on this tree returned **9 non-zero**. Every one
of the nine was then proved **pre-existing** by base-vs-head — revert the one changed file, rebuild, re-run,
restore, rebuild — and all nine returned an **identical rc in both directions**:

    test_gate_icn_ipl_reason_is_the_oracles_own_words             rc=1  base and head
    test_gate_icn_list_element_alternation_position               rc=2  base and head
    test_gate_icn_rbp_census_ratchet                              rc=1  base and head (RATCHET C_data=25191 > baseline=0)
    test_gate_icn_seq_takes_a_variable_step                       rc=0  base and head   <-- see below
    test_gate_icn_string_builtins_refuse_a_non_string_argument    rc=1  base and head
    test_gate_icn_suspend_record_stack_alignment                  rc=2  base and head
    test_gate_icn_var                                             rc=1  base and head
    test_gate_icon_master_per_entry_identity                      rc=2  base and head
    test_gate_icon_vendored_sources_compile_under_icont           rc=1  base and head

⛔ **AND ONE OF THEM IS ITSELF FLAKY, WHICH IS WHY THE SWEEP CANNOT BE THE EVIDENCE.**
`test_gate_icn_seq_takes_a_variable_step` read **rc=2 in the sweep and rc=0 minutes later on the same binary** —
so it appears in the nine and reads green in both arms of the base-vs-head. **A single gate sweep is not a
base-vs-head and must not be quoted as one.** Prove every red in both directions before attributing it to a
landing.

⭐ **THE TWO ERRORS POINT IN OPPOSITE DIRECTIONS FROM ONE CAUSE, AND THAT IS THE REUSABLE LESSON.** A flaky
*witness* graded once **hides** a live defect (gc2, red for ten days behind a 25% pass rate). A flaky *gate*
graded once **manufactures** a regression that nobody introduced. Both are the same underlying error — a single
observation of a non-deterministic instrument treated as a measurement — and a seat that has learned to distrust
one will still be caught by the other, because they feel completely different: one looks like good news, the
other looks like someone else's bug.

## 5. RESOLVED THE SAME DAY — CURED BY THE cfo, VERIFIED BY RATE, ZONA BACK TO 88/88

**The cure is the cfo's `5dafed741`**, found by hardware watchpoint rather than bisect: `dat_alloc_fill` kept each
record's `DATBLK_t` only in the static `dat_types` table, nothing walked it as a root, rung 1 removed the blanket
force-mark that had been hiding that, and the block was reclaimed and slid over — two memcpy hits from
`gc_collect_ex`. `type()` then read garbage, which is the `t=0x3` above. Cure: `dat_gc_roots()` beside
`core_gc_roots()`, plus a new blocking gate `test_gate_gc_record_type_table_is_rooted_not_blanket_marked.sh`.
⭐ Note this is the **same shape as hq_V's blocker 4 one table over** — a static table of heap pointers with no
root, alive only because nothing could move. The cfo landed that one too the same day (`529cdc814`, `_func_buckets`).

**Verified here by the method this finding argued for — rate, not a single run.** On SCRIP `b8bd29d1e`:

    m3   crashes 0/20    answer-mismatches 0/20
    m4   crashes 0/20    answer-mismatches 0/20

40 clean runs against the 15/20 and the coo's independently measured 11/20 (m3) and 14/20 (m4). Then the board,
run by `hq_icon` as the Icon runner under CEO-775: **`ARIZONA_AND_PER_PROGRAM and_pass=88 of 88 (m3 88 · m4 88 ·
union of reds 0)`**, rc=0. Zona is 88/88 and Icon is full on all four suites again.

⭐ **THE PROCESS POINT WORTH KEEPING:** a single green run would have "closed" this row at any point in the
preceding ten days, and the rate is what made both the diagnosis and the verification trustworthy. The coo has
written the rate beside the Zona row in `SUITES.tsv` so a later lucky green cannot close it silently, and has
asked the ceo for a FLAKY-or-by-rate verdict, since the ladder has no way to express one today.

## 6. WHAT TO DO WITH THE BOARD LINE

⛔ Zona should not be published as a settled `87/88` while the program is a coin flip: a rerun can hand the
runner `88/88` and quietly close a live crash. Grade gc2 **by rate**, or mark it FLAKY. `PASS`/`FAIL` cannot
express a 75% failure, and the population law's worst state — UNMEASURED reported as measured — is exactly
what a one-shot grade of a flaky program produces.
