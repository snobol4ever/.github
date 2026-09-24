# A call inside a scan body left the subject base in a register the collector never sees -- htprep's stress-5 garbage, cured

cto, 2026-09-24, MODE DECTET. Row `icon-gc-procedure-record-scan-replace-2-goes-crash-to-diff-across-fa1dc84a5-so-the-r13-staleness-was-only-part-of-it` (minted by the cfo on the ceo's order, CEO-1127; dispatched to the cto). Parent SCRIP 8b6cb3607. hq_icon's 15-line witness (FINDING-2026-09-24-hq_icon-htprep-stale-scan-subject-15-line-witness.md) is the same defect and is adopted as the gate's witness.

## What was measured before the cure (SCRIP 8b6cb3607)

The row's DONE-WHEN through the harness runner with the entry's 2106 bytes of stdin: `procedure_record_scan_replace_2` (htprep.icn from the IPL) PASS at stress 0, FAIL at stress 5, 128 KB window, forced relocation. The s5 stdout is wrong from byte 48 on line 3: `<title>` followed by seventeen NUL bytes where "Off the Beaten Path" belongs, and four runs give four different outputs. Every unclosed-tag warning at the end says the `}` was never seen: the scanned text read as zeros after the first tag.

hq_icon's witness (`braces` scans a line, `newtag()` is called from inside the scan and fails after `tab(many(&letters))`), at the shipped window: mode 3 DIFF at stress 3 and 11, mode 4 DIFF at 4, 8 and 16; identical to iconx unstressed.

Under the flip plant (SCRIP_GC_PLANT_FLIP=1) the wrong answer becomes a located fault at the same slab offset on every run:

- instruction: `movzx esi, byte ptr [r13+rcx]` -- the inline cset test of `upto('{}')` in `braces`, rcx = 4 (the position), r15 = 33 (the subject length)
- the ground: a 64-byte HB_WSB string block, 20 bytes in, MOVED by collection #6 (the birth ledger names it: allocated by rt_gcheap_alloc from try_call_builtin_by_name_bl_s, the `trim(read())` result that became the scan subject)
- the holder: r13 in `braces`, unchanged across `call newtag_dcα` because the callee never touches it; the emitted successor (`.Lcall_proc_staged_α_74_2`) carried the position back through `rt_scan_sync_in` and reloaded nothing else

`newtag` has no r13 reference at all: its `tab(many(&letters))` runs by name on the runtime's `scan_subj`, allocates the substring, the collection moves the subject and relocates `scan_subj` (rooted in gen_gc_roots) -- and the caller resumed on the old ground, because a C-saved register is not a root and the collector guesses nothing (CEO-812).

## The cure (SCRIP, one helper in x86_asm.h)

`x86_scan_sigma_reload()`: `call rt_scan_live_subj; mov r13, rax`, emitted by `x86_scan_sync_in_rr()` and, when the scan registers are live, by `x86_scan_sync_in_rr_force()`, right after the position reload. Every call successor inside a scan body (the staged procedure call, call_value, define, the by-name scan builtins) now hands the subject base back from the same rooted runtime state the position already travelled through. The length in r15 does not change under relocation. `rt_scan_live_subj` already existed (bb_gen_scan uses it on resume).

The plant `SCRIP_GC_PLANT_STALE_SIGMA=1` leaves the reload out at emit time and prints `[GC-STALESIGMA] plant:` once per process; it is declared in the plant table of `test_gate_gc_the_plant_says_whether_it_applied.sh`.

## What was measured after the cure

- the row's DONE-WHEN: GREEN, PASS at stress 0 and 5
- the 15-line witness: identical to iconx at m3 stress 0/3/11, m4 stress 0/4/8/16, and under the flip plant at m3 3/11 and m4 4/8
- the plant: DIFF at m3 stress 3 with the banner; with the flip plant on top, rc=139 and four ZGC-STALE lines -- the loss returns when the reload is removed
- the nested-scan sibling (an inner scan that allocates 3000 strings, then the outer subject read after leave): identical at stress 0/1/3 and under the flip plant -- not a second row

Gate: `test_gate_gc_the_scan_subject_base_is_reloaded_after_a_call_inside_a_scan.sh` (blocking, Makefile), arms (a) property both modes plus flip, (b) planted, (c) source; FAIL_ONCE=1 runs (a) under the plant.

The population machine (Icon master by name, control 8b6cb3607 vs the cure, arms nogc,r0,r1,s1,f1, both modes) is recorded in the row's ledger and in GOAL-CTO.md CTO-165 with the non-green name sets both directions.

## Found on the way, not this landing

The collector's stack walk faults under valgrind (hq_icon's finding): `gc_stack_region` takes the main stack from the `[stack]` line of /proc/self/maps, which under valgrind is the host's stack; the mapping containing `__libc_stack_end` is the real one in both settings. Minted as `gc-the-main-stack-top-is-the-mapping-holding-libc-stack-end-not-the-stack-label-so-a-collecting-run-survives-valgrind` (cto lane), next.
