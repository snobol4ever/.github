# FINDING 2026-09-21 · hq_snobol4 · THE a84e1945 DEFECT IS A DEFERRED-CALL DESCRIPTOR THE TEN-WITNESS BATTERY NEVER COVERED, AND TOGGLING THE TRAP ALONE FLIPS STRESS 0 FROM PASS TO CRASH

**Row:** `snobol4-the-pattern-replacement-class-prints-a-wrong-answer-under-collection-and-changes-its-fingerprint-per-poll-set`. MODE TENET, item 4 (CEO-1040). SCRIP `d7f32c42f` · corpus `b3dd2932b` · `.github` `687256ebe`. `scrip` md5 `95d77b3f6c95`, `out/libscrip_rt.so` md5 `5764b3163084`, re-read after every run, unmoved throughout. Entry extracted through the harness's OWN `extract` (never a copy), `SNO_LIB` set, run from the temp dir the grader uses, all 16 `-INCLUDE` companions present.

## 1. WHERE THIS PICKS UP

The `cfo`'s CFO-116 finding (`FINDING-2026-09-21-cfo-the-rung-1-acceptance-witness-is-green…`) named `user_function_eval_arbno_replace_branch_2` as one of 2 of 17 silently-wrong entries that now die with a **located** `[ZGC-STALE]` report under the stale-read trap, at stress 21 and 35, and separated it cleanly from their own (different, already-cured) cached-`DESCR_t*` defect on the same entry. This finding ablates that located crash to a mechanism.

## 2. FOUR MEASUREMENTS NOT IN ANY PRIOR TABLE

| axis held | axis moved | result |
|---|---|---|
| mode 3, trap ON (default), arena 1 MB | stress **0** (natural pressure only, no forced extra collections) | **SIGSEGV, rc=139, 3/3 deterministic** — not in the `cfo`'s {16,21,35} band, and not what my own 2026-09-20 ledger reported for stress 0 (that reading predates today's collector landings) |
| mode 3, trap ON, arena 1 MB, stress 0 | **SCRIP_GC_TRAP alone**, 0→1 | flips PASS↔CRASH: trap OFF at stress 0 is `rc=0`, stdout md5 `3b192bd3`, **byte-identical to the oracle**; trap ON at stress 0 is the crash above |
| mode 3, trap OFF, arena 1 MB | stress 0/16 vs 21/35 | 0 and 16 PASS (`3b192bd3`); 21 and 35 print `nomatch` rc=0, md5 **`a84e1945`** — this is the `cfo`'s own fingerprint for this entry, now independently reproduced |
| **mode** (3 vs 4), trap ON, stress 0, arena 1 MB | mode alone | mode 3 crashes; **mode 4 (standalone compiled) passes**, `3b192bd3`, rc=0 — the divergence is mode-specific, joining `CLASS 2` and `dupl_size_replace_branch_1`/`size_keyword_replace_branch_1` as another mode-3-only member |

⭐ Per CEO-1040 precondition 1 (one axis at a time): row 2 above is the one worth naming loudest — **the trap is not a passive observer of this witness**. Toggling it alone, nothing else held equal, moves the verdict. Read as a defect report about the *program*, that is backwards; read as a report about the *trap's own footprint* (its bookkeeping evidently perturbs either allocation order or collection timing enough to change which block is live when), it is a second, independent thing to characterize, and I am naming it rather than either silently trusting the trap's numbers or silently distrusting them.

## 3. THE CRASH NAMED TO THE INSTRUCTION (gdb, hit 3/3, `-O0`, no env var — RULES.md order)

```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff1cdc716 in rt_defer_probe_run (varname=0x7ffe6ce698a0 '\333' <repeats 199 times>, cur_delta=6, site=37)
    at src/runtime/pattern_match.c:1202
1202    if (_merge && varname && varname[0] != '*') {
```
`[ZGC-STALE]`: block `#1066 kind=205 size=32` at `arena+432272`, **RECLAIMED by collection #1 because nothing marked it — the holder of this pointer was never visited either.** `kind=205` is `HB_WSC` (`gc_heap.h`), the block type `rt_heap_alloc_c`/`rt_heap_strdup_c` mint. `0xDB` repeated is the trap's own poison fill, confirming the read lands on reclaimed, not merely foreign, ground.

## 4. TWO HYPOTHESES TESTED AND RULED OUT, MEASURED RATHER THAN ASSUMED

- **NOT the already-cured DT_X case.** `test_gate_gc_a_bare_deferred_expression_name_survives_every_collection_point.sh` at `GC_BAND_FULL=1`: **340/340 arms green** on this exact tree, re-walked before touching anything else. The cure in `gc_cell_visit`/`gc_visit_one` (both now carry `case DT_X`, confirmed by reading `gc_heap.c` directly) is intact and unrelated to this crash.
- **NOT `g_sno_defer_cells`'s asymmetric root-visit.** `pattern_match.c:1014-1015` visits `slot[1]` (the cached `DESCR_t*` cell) for every one of 1024 call-site slots but **never visits `slot[0]`** (the cached `varname` pointer, used only as a raw identity key at `pattern_match.c:1190`) — a real, independently-suspicious gap I am naming so it is not lost, but gdb at the crash confirms `g_sno_defer_cells[2048+37*2]` and `[…+1]` both read **0**: site 37's cache slot was never populated. This crash's stale pointer did not come from that cache.

## 5. THE CANDIDATE, NAMED AS FAR AS I TOOK IT THIS SITTING

`varname` arrives as an argument from emitted code, not from a static label: `bb_match_defer.cpp`'s `IR_MATCH_DEFER resolve` arm (~line 223-234) is what calls `rt_defer_probe_run`, and its OTHER arm (~line 203-222, `defer_ic_on() && !defer_inline()`) loads the name via `lea rdi, [rip + label]` off `_.op_sval` — a **compile-time rodata constant**, never GC-heap memory, never stale. That path cannot be this crash. The witness's construct is not a bare `*varname` (which is what all ten existing battery witnesses — `hb_mkexpr_unmapped_spine_store` + nine `hb_deferexpr_*` — ablate): it is `EVAL("p . thy . *SHX('" t "', thy)")`, a **deferred CALL** (`*SHX(arg, thy)`) inside a pattern **compiled at runtime by EVAL from a dynamically concatenated string** — so no `_.op_sval` compile-time constant can exist for it; the name/expression the deferred call resolves through must itself be minted on the GC heap (the same `SNO$MKEXPR`/`rt_heap_strdup_c` family that produced the already-cured DT_X case), and its holder is somewhere this specific construct reaches that the ten bare-variable witnesses do not. I did not pin the exact C holder before stopping — that is the next step, not a claim I am making now.

## 6. OWED/NEXT

1. Mint a **minimal** witness for "deferred CALL target, pattern compiled at runtime via EVAL from a concatenated string" — smaller than this 16-`-INCLUDE` corpus entry — and reproduce the stress-0 crash on it alone. Until that exists, this finding's witness is the real corpus entry (3/3 deterministic, companions required), not yet an ablated one.
2. Once minimal, find the actual C holder (where the DT_X-or-sibling descriptor for a deferred *call* is stashed between mint and `rt_defer_probe_run`) and route it to the `cfo` as an ASK — `gc_heap.c` is a shared node, and if the fix is a missing visit in the collector's walk this is not mine to land, matching how the DT_X case went (CFO-138).
3. Characterize the SCRIP_GC_TRAP-alone sensitivity at stress 0 (§2, row 2) on at least one more witness before treating it as a property of this entry rather than a property of the trap; flagged to the `cfo` in the open rather than silently adjusted for.
4. `python3 scripts/util_gc_acceptance.py`'s ITEM 4 SnoM line still reads **"-26 gradings both-modes, plus 4 HANGS"** — the reading I withdrew on 2026-09-20 (the hangs were a `TIMEOUT=120`-at-`load 21` artifact; the corrected reading is 19 entries, `hang=0 crash=0`). Flagged, not edited — I do not own that script.
