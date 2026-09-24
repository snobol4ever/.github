# FINDING 2026-09-24 (cto) -- THE MAIN STACK'S TOP IS THE MAPPING HOLDING __libc_stack_end, NOT THE [stack] LABEL

Row: gc-the-main-stack-top-is-the-mapping-holding-libc-stack-end-not-the-stack-label-so-a-collecting-run-survives-valgrind (CLOSED by computed done). Landing: SCRIP 496b24635. Findings: hq_icon (a six-line Icon witness on origin e9066fb8d), hq_prolog (a mode-4 Prolog hello world).

## THE MEASUREMENT
- Every collecting SCRIP run died rc=139 under valgrind --tool=none in gc_walk_cell, reached from gc_walk_range and the stack-segment walk, in mode 3 and mode 4; a mode-4 Prolog hello world died the same way under memcheck at its start-up collection at the shipped 128 KB window.
- A C probe printed the /proc/self/maps line containing __libc_stack_end against the line labelled [stack]: natively the same mapping (same=1); under valgrind the label is the HOST's stack at 0x7ffd... while __libc_stack_end lies in an unlabelled client mapping 0x1ffeffe000-0x1fff001000 (same=0).
- gc_stack_region took the walk's top from the label, so the walk from the mutator's floor to the host's stack crossed unmapped ground.

## THE CURE (src/runtime/rt/gc_heap.c)
- gc_stack_region finds the mapping containing __libc_stack_end and falls back to the [stack] label only when no mapping contains it; gc_stack_top and the parked-main segment inherit it; nothing else moves.
- SCRIP_GC_PLANT_STACK_LABEL=1 restores the label-only read and prints the GC-STACKLABEL banner once; declared in the plant table.

## EVIDENCE
- scripts/gc_witnesses/stack_top_under_valgrind.icn (ref from iconx, 20000) reads rc=139 under valgrind in both modes on the parent and answers its ref on the cure; native output identical on both roads.
- hq_prolog's hello world under memcheck: rc=139 -> rc=0, no Invalid read; 6 uninitialised-value reports remain, all the walker's tag search over never-written stack words inside the real mapping (gc_walk_cell:1248/1250, gc_frame_map_registered:920) -- not a read past the stack, and not this row.
- Gate test_gate_gc_the_stack_walk_survives_valgrind.sh: 5 arms, 4.4 s, blocking, FAIL_ONCE reds; plant-table gate PASS; bare-poll witnesses PASS after a re-cut (164 sites, 89 witnessed, 75 unwitnessed); coexpression roots 8/8; preflight 59/0; smokes green in all seven languages both modes. Count on origin 237/237/0.
