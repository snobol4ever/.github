# FINDING 2026-09-20 hq_prolog — THE MANDATORY TINY-ARENA COLLECTOR PASS DEFINES ITS POPULATION BY NAME, SO EIGHT COLLECTOR-GRADING GATES ARE STRUCTURALLY INVISIBLE TO IT

**Measured** on SCRIP `ac1970678`, this root, 2026-09-20 by hq_prolog while wiring
`test_gate_pl_atom_name_survives_a_collect_mid_operation.sh`.

## THE CLAIM

`make test-arena` is **"LON'S TINY-ARENA PASS, MANDATORY PER COLLECTOR LANDING"** (Lon 2026-09-19, CEO-938/939,
RULES.md batch 28 clause 2). Its recipe says, in its own printed summary line, that **"every red here is a
collector finding and owes a ROW."**

It cannot say that, because it does not run every collector gate. Its population is the shell glob

    for g in scripts/test_gate_gc_*.sh; do ...

so membership is decided by **the first eight characters of a filename**, never by what the gate grades.

## THE NUMBERS

- Gates matching the arena glob: **37**
- Gates that grade the collector (they reference `SCRIP_GC_STRESS`, `SCRIP_GC_POISON`, `SCRIP_HEAP_MB`,
  `rt_gc_*` or `gc_collect`) and do **not** match it: **8**

The eight, by name:

    test_gate_dispatch_gc_safepoint_inline.sh
    test_gate_icn_a_spine_opened_plain_procedure_fails_forward_on_redo.sh
    test_gate_pas_heap_table_is_a_movable_root.sh
    test_gate_pl_an_asserted_atom_survives_a_collection.sh
    test_gate_pl_atom_name_survives_a_collect_mid_operation.sh
    test_gate_rc8a_gc_coverage.sh
    test_gate_rtcc_block_coverage.sh
    test_gate_zd_a_run_keeps_no_producer_whose_consumer_is_outside_it.sh

So the mandatory collector pass measures **37 of 45**, and reports as though it measured all of them.

## WHY IT HAPPENED, AND IT IS NOT CARELESSNESS

The naming convention splits gates **by lane** (`pl_`, `pas_`, `icn_`, `zd_`, `rtcc_`, `dispatch_`), and the
arena pass keys on **subject** (`gc_`). Both conventions are reasonable and they are incompatible. A Prolog
seat writing a Prolog collector gate names it `test_gate_pl_...` by every convention the tree teaches, and in
doing so makes it permanently invisible to the pass that exists to run exactly that kind of gate. **Nobody has
to make a mistake for this to happen; following the conventions produces it.**

## THE CLASS, WHICH IS THE POINT

This is the third instrument in one sitting that reported a number that was true while the thing it stood for
was false, and all three are the same shape — **a population defined by a NAME rather than by a PROPERTY**:

1. This gate's own clause 1 was a **denylist of four allocator spellings**. Storage moved from `rt_pinned_*`
   to `rt_heap_strdup_c` — the same heap under a different name — and the clause read CLEAN on a tree where the
   exposure was strictly worse. Cured this landing into a fail-closed allowlist that resolves the allocator
   actually producing the pointer and REFUSES rc=2 on a line it cannot parse.
2. The cto's slot-kind census **printed the count and swallowed the names** for two months, which is how thirty
   missing include files sat in the fleet suite table as a product gap (cured SCRIP `83fb80ee7`; the consumer
   now refuses rc=2 if the names printed do not equal the count reported).
3. This: the arena pass's `test_gate_gc_*` glob.

CLAUDE.md already names the general form — *"any instrument that answers a narrower question than you think you
asked will never say so"* — and lists unanchored globs beside `command -v` and truncated listings. This is that
entry, live, in a mandatory pass.

## WHAT I AM NOT CLAIMING

I have **not** run the eight under the tiny arena, so I do not know how many are red there. The finding is the
**hole in the population**, not a count of defects behind it. Seven of the eight are other seats' lanes and it
is not my call to add them: the arena pass is the cfo's/coo's node under MODE line 2 (SEPTET), so this is
routed with the measurement rather than cured here.

## THE CURE SHAPE, OFFERED NOT IMPOSED

Select by property, not by prefix — the same move `preflight` already made when a static grep could not classify
its own population in either direction, and it declared `scripts/preflight_arms.txt` instead. Either a declared
arena-arms file, or a content test (the gate names a GC knob), or a marker line the gate carries. Any of the
three makes a new collector gate joinable; the glob makes it joinable only by being renamed.

**Folded into:** `GOAL-PROLOG-100.md` LIVE CURSOR 2026-09-20, and the baton for
`prolog-atom-names-live-in-71-c-locals-...`, in the same landing — because findings are deleted periodically and
a measurement living only here has a deletion date.
