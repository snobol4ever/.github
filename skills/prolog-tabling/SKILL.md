---
name: prolog-tabling
description: SCRIP Prolog's tabling: IR_TABLE_HDR, answer tries, semi-naive rounds, moded and incremental tables, well-founded negation, the XSB loader. REQUIRED by the skill gate before editing tabling.pl, xsb_tables.pl or bb_table_hdr.cpp.
---

# Prolog tabling

Detail is in `reference.md` beside this file; the language's oracles and suites are skill `prolog`.

## 1. The rule (CEO-1885 (a): compiled Prolog IS boxes)

**The memory of a tabled evaluation is the state of the box doing it.** A table's ANSWERS outlive every call, so they live on the heap in the answer trie (`HB_TRIE`, traced, rooted off the variant table; the `pl_trie_*` leaves). An EVALUATION in progress lives exactly as long as the generator evaluating it, so it lives in that generator's HEADER: the cells of an `IR_TABLE_HDR` box (`src/templates/bb/bb_table_hdr.cpp`) in its clause's frame. No global holds evaluation state: no `nb_setval` on a `$tbl_` name, no list of tables in progress beside the header chain, no worklist off the machine stack.

## 2. The engine (prelude `src/parsers/prolog/prelude/tabling.pl`, compiled with the program)

- A tabled `p/N` is renamed to `'$tbl p'/N` (lower's `pl_table_rewrite` and `pl_table_wrapper`; the run-time loader's twins) and its entry is `'$tbl_call'(G, I)`, routed to `'$tbl_icall'` or `'$tbl_mcall'` by the declaration's kind.
- The first tabled call LEADS (`'$tbl_lead'`): it evaluates its table, then repeats semi-naive rounds over every in-progress table until a round adds no answer and no table, then completes them all. The header cells: the leader owns 1-4, one table's evaluation (`'$tbl_eval1'`, `'$tbl_eval1n'`) owns 5, one pass (`'$tbl_eval'`) owns 6-9; the leaves `'$tbh_get'`, `'$tbh_set'`, `'$tbh_bset'` (trailed), `'$tbh_own'`, `'$tbh_close'`, `'$tbh_leading'` reach the nearest owning header.
- **Moded tables** (answer subsumption: `:- table p(max)`) aggregate through `'$tbl_madd'`.
- **The incremental dependency graph**: each table's node lives in its trie's meta term (its kind, dependencies, dependents, falsecount, lazy queue, forced flag). A call to a dynamic predicate declared incremental or monotonic is rewritten by the lowerer to `'$tbl_dcall'`; every change enters `'$tbl_dchange'`. Incremental tables invalidate and re-evaluate (the old answer set kept until the new one compares); monotonic eager tables take a delta-seeded semi-naive step (`'$tbl_mono_step'`); lazy ones queue the delta and force at the next call. A transaction is an activation whose undo log is rooted from its own local (`'$tx_cur'`).
- **Well-founded negation**: the alternating fixpoint (Van Gelder) over the rounds with `tnot/1` read against the previous round, then one residual pass that builds the delay lists.
- **Call subsumption**: `:- table p/N as subsumptive` and the file-wide `:- use_subsumptive_tabling.`; XSB's `-S` is the entry's oracle and compile argument, mapped by the driver to that prepended directive (CEO-2110).

## 3. The XSB package (`/home/corpus/packages/prolog/xsb_tests`, the oracle XSB 5.0.0 through `xsb_bin()`)

The XSB dialect is the program's own (`xsb_dialect.pl`, `xsb_builtins.pl`, `xsb_tables.pl`, `xsb_ordsets.pl`); the entry runs the package's own driver as XSB's `test.sh` does, refs compared ignoring white space. Ruled: tabling engine scale is its own row, not call subsumption (CEO-2112: `sub_tests_decker` needs an SCC of about ten thousand tables inside the declared 128 MB and 4 MB, so per-table memory, an iterative leader and a trie-walk subsumer lookup instead of `'$tbl_sfind'` materialising `'$trie_entries'` per call).

**A table's answer ORDER is graded only where it is the program's** (the coo 2026-11-12 22:47 CST): XSB's order for a completed table is its implementation's (newest first to 8 siblings, hash order from 9, varying between runs for atoms), so no cure emulates it; an entry whose one measured divergence is that order carries the compare token `sorted-lines` (skill `suites-and-grading` section 4, the compare cell). A program that sorts or prints its own order is still graded byte for byte.

## 4. DESIGN: xsb-tabling-wfs (CEO-2005; `/home/harness/designs/xsb_tabling_wfs/STEPS.tsv`, `test_design_xsb_tabling_wfs_steps.sh`; the witnesses in `/home/corpus/packages/prolog/xsb_witnesses/xsb_wfs/`, the package the six xsb_* witness folders moved to whole, the coo's ruling 2026-11-12)

Steps 1-7 DONE (the loader reads table directives; the WFS driver as XSB runs it; the XSB reading; auto_table and suppl_table; the table builtin surface; one body one run; the SCC depth number). Step 8 (delay lists as XSB prints them), 9 (the cut over an incomplete table) and 11 (the finish) FREE; step 10 (call subsumption) CLAIMED by the cao, closing on xw11, sg1, lrtc1 and drtc1 with decker moved to the engine-scale row (CEO-2112).

**The trail header's top is where the collector's trail walk ends (SCRIP cfe269557, 2026-11-04).** `rt_gc_trail_roots_run` walks each registered trail from its header to header word 0, which only `rt_pl_tr_gc_sync` writes; compiled-code polls do not carry r12. The parked-segment road moves the trail top outside any leaf: `rt_pl_pseg_next` copies a segment's trail records back onto the live trail and `rt_pl_pseg_switch` then sets r12 to the segment's top (or to the resumer's). So `rt_pl_pseg_next` syncs the header to `b->r12` on a resume and to `s->r12` on the return to the resumer. Without it a collection at the first poll after a resume stops short of the restored entries, never forwards their cells, and the next `rt_pl_pseg_park` copies a stale cell: `[ZGC-STALE]` SIGSEGV at `rt_pl_pseg_park+0x3fe`. MEASURED: `delay_tests_przy1` m3 crashed 3 of 3 on 7cda8c6a0 and on f88559a7f^ (so the trail floor cure was not the cause), header top `0x...340` against a live top `0x...3c0` at collection 1, the stale slot the keep entry of the `$tbl_dl` box that `rt_pl_b_set` pushed; after the cure `--step 6` reads m3=5/5 m4=5/5 entries=3/3 GREEN (was entries=2/3). Open, unmeasured: `rt_pl_pseg_ball_c` returns with the header at the ball's r12 while `rt_pl_pseg_ball` resumes with `PSCH_R12`; a witness that collects right after a ball would show it. Any new asm or leaf that sets r12 from a saved value owes the same sync.

## 5. DESIGN: tabling-one-engine (CIO-104; `/home/harness/designs/tabling_one_engine/STEPS.tsv`, the witnesses family `one_engine` of `/home/corpus/tests/prolog/ALL.pl`, `test_design_tabling_one_engine_steps.sh`)

Every table of every kind is evaluated by the one suspend-and-resume scheduler and the round engine is deleted; a kind is what a table remembers, never how it is evaluated. Measured 2026-11-10: an incremental 3-cycle runs its rule body 15 times where swipl runs it 3, and a plain table calling an incremental or subsumptive one raises a type error (the cto's run). Five laws, four steps in a line (every kind crosses in ONE landing), the witnesses `oe1` to `oe10` cut from swipl: the full text is `reference.md` section 5. Until step 6 lands, section 2 above describes both engines; a new tabling feature is written against the scheduler only.
