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

## 6. OWED/NEXT (item 1 amended by §7 below — not retracted, ADVANCED; read §7 before acting on item 1 as written here)

1. Mint a **minimal** witness for "deferred CALL target, pattern compiled at runtime via EVAL from a concatenated string" — smaller than this 16-`-INCLUDE` corpus entry — and reproduce the stress-0 crash on it alone. Until that exists, this finding's witness is the real corpus entry (3/3 deterministic, companions required), not yet an ablated one.
2. Once minimal, find the actual C holder (where the DT_X-or-sibling descriptor for a deferred *call* is stashed between mint and `rt_defer_probe_run`) and route it to the `cfo` as an ASK — `gc_heap.c` is a shared node, and if the fix is a missing visit in the collector's walk this is not mine to land, matching how the DT_X case went (CFO-138).
3. Characterize the SCRIP_GC_TRAP-alone sensitivity at stress 0 (§2, row 2) on at least one more witness before treating it as a property of this entry rather than a property of the trap; flagged to the `cfo` in the open rather than silently adjusted for.
4. `python3 scripts/util_gc_acceptance.py`'s ITEM 4 SnoM line still reads **"-26 gradings both-modes, plus 4 HANGS"** — the reading I withdrew on 2026-09-20 (the hangs were a `TIMEOUT=120`-at-`load 21` artifact; the corrected reading is 19 entries, `hang=0 crash=0`). Flagged, not edited — I do not own that script.

## 7. 2026-09-21 (same sitting, after MODE flipped EXECUTIVE→TENET and back, ceo-1051/ceo-1055) — ABLATION: 16 → 11 `-INCLUDE`S, SAME FINGERPRINT, A WIDER BAND, AND A CORRECTION TO §2 ROW 4

Tree unchanged from §1 except SCRIP fast-forwarded to `f839e933b` (the `cfo`'s Pass-B auditor landed; unrelated files, rebuilt, re-confirmed 340/340 DT_X band and `make preflight` clean before touching anything). All work below is READS plus scratch files outside both repos — `git status` empty in SCRIP and corpus throughout, checked before writing this section.

**(a) Construction alone does not crash.** Truncating the master entry right after its `Parse = nP2() ARBNO(*Command) ("'Parse'" & 1) nQ2()` line (i.e. running all seven `shf2`/`EVAL` calls that BUILD `Label`/`Stmt`/`Command`/`Parse`, then stopping before `Src`/`*Parse` ever attempts a match) — trap ON, stress 0, 3/3 — is clean, rc=0, `built`. Matching against real input is a necessary ingredient, not just constructing the EVAL-compiled pattern values.

**(b) A match that SUCCEEDS does not crash, by two independent routes.** `("'Stmt'" & 7)` and `("'Parse'" & 1)` are not debug decoration: `semantic.inc:8` reads `OPSYN('&', 'reduce', 2)`, and `reduce(t,n) = EVAL("epsilon . *Reduce(" t ", " n ")")` (`semantic.inc:17`) is a **second instance of the identical defect-class construct** — an EVAL-compiled pattern containing a deferred CALL, `*Reduce(t,n)`, this time into `ShiftReduce.inc`'s real stack-popping `Reduce(t,n,c,i,r)`. Deleting both `& `-clauses turns the match from `nomatch`→`match` and the crash disappears at every stress point 0–35, trap on or off. Independently, dropping five of the sixteen `-INCLUDE`s down to nine (`global/case/assign/match/counter/stack/tree/ShiftReduce/semantic`, includes untouched otherwise) does the same thing — same `match` outcome, same absence of any crash — without touching the driver at all. **Conclusion: the crash needs BOTH EVAL-compiled deferred-call sites (SHX's and Reduce's) live AND the overall parse to end in FAILURE.** A failed parse makes SNOBOL4's backtracker retry `Stmt`'s alternatives and `Command`'s sequence repeatedly; a clean, quick match visits each site's cache too few times, in too benign an order, to read it back after the block housing it has already been reclaimed.

**(c) File-level bisection: 16 → 11 `-INCLUDE`s, same driver, same fingerprint.** Keeping the full original driver/grammar (unmodified `NRETURN`, unmodified `&`-clauses) and bisecting the sixteen include files:

| `-INCLUDE` set | result (trap ON, stress 0, 3 reps) |
|---|---|
| all 16 (original) | SIGSEGV 3/3, `rt_defer_probe_run`, `pattern_match.c:1202`, block `#1066 kind=205`, site=37 |
| 9: drop `TDump/Gen/Qize/ReadWrite/XDump/omega/trace` | clean, `match`, rc=0 — **not** reproducing |
| 13: 9 + `TDump+Gen+Qize+ReadWrite` | SIGSEGV 3/3 |
| 11: 9 + `Qize+ReadWrite` (drop `TDump/Gen/XDump/omega/trace`) | **SIGSEGV 3/3** — reproduces |
| 11 − `Qize` or 11 − `ReadWrite` (either alone) | clean, `match` — neither suffices alone, both are jointly required |
| 11 − `case.inc` − `assign.inc` (9: drop those two instead) | clean, `match` — `case.inc`/`assign.inc` are also jointly load-bearing |

**New minimal(er) witness, same driver, 11 of 16 `-INCLUDE`s:** `global.inc case.inc assign.inc match.inc counter.inc stack.inc tree.inc ShiftReduce.inc Qize.inc ReadWrite.inc semantic.inc`. `TDump.inc`, `Gen.inc`, `XDump.inc`, `omega.inc`, `trace.inc` are confirmed NOT needed. The exact mechanism by which `Qize.inc`/`ReadWrite.inc`/`case.inc`/`assign.inc` are load-bearing (almost certainly: real whitespace/tokenizing helpers that change whether `Shift`'s `POS(0) whitespace =` step and `Reduce`'s `IDENT`/`DIFFER` checks take the branch that ultimately fails the parse) was **not traced line-by-line this sitting** — named as unmeasured, not assumed.

gdb on the 11-include witness (same env, `-O0`, no env var, hit 3/3):
```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff1cdc716 in rt_defer_probe_run (varname=0x7fff4ce65880 '\333' <repeats 199 times>, cur_delta=6, site=27)
    at src/runtime/pattern_match.c:1202
1202    if (_merge && varname && varname[0] != '*') {
```
Identical function, identical line, identical 0xDB poison signature, identical block kind (205/`HB_WSC`) — only `site=27` vs `37` differs, exactly as expected with fewer EVAL sites minted from fewer includes. **This is the same defect, not a lookalike.**

**(d) A wider, denser band than previously swept, on this 11-include witness (mode 3, arena 1 MB):**

| stress | trap ON | trap OFF (md5, meaning) |
|---|---|---|
| 0 | SIGSEGV | `3b192bd3` — oracle-identical PASS |
| 1,2,3,5,8,21,25,35 | SIGSEGV (all eight) | `a84e1945` — **the same fingerprint that named this whole defect class**, independently reproduced at every one of these eight points, not just the `cfo`'s original {21,35} |
| 16 | PASS, `match` | `3b192bd3` — oracle-identical PASS |

Only stress ∈ {0, 16} are clean (trap off); every other sampled point 1–35 is bad. This is a much denser confirmation of the `a84e1945` fingerprint than the original witness had been swept for this sitting (previously known bad points: the `cfo`'s {21,35} plus my own stress-0 addition; the 16-include original's own full 0–35 sweep is still owed, separately from this one).

**(e) Correction to §2 row 4 above ("the divergence is mode-specific"): mode 4 is not categorically safe.** On this 11-include witness, mode 4 (`--compile`, standalone, linked against the same `libscrip_rt.so`) SIGSEGVs at **stress 16** — a `[ZGC-STALE]` quarantined-page report ("no block in the vacated ledger covers this address... this ground was vacated before the ledger's oldest entry, so the block is not nameable from here") — while stress 0 and stress 21 both print a correct `match` with all seven `SHX(...)` side-effect lines visible, oracle-consistent. §2 row 4's *measurement* (mode 3 crashes / mode 4 passes, at stress 0 specifically) stands unchanged and is not retracted; the *reading* drawn from it — that mode 4 is broadly immune to this class — does not hold. Mode 4 has its own bad cells on the (stress × mode) grid; they are simply not the same cells as mode 3's. Neither mode's bad-set has been fully mapped yet.

**(f) What I tried toward a from-scratch minimal witness, and why none of it worked.** Hand-writing the mechanism without the shift-reduce demo (no `-INCLUDE`s at all) was attempted first, bottom-up, before the file-level bisection above:
   - A single `DEFINE`d function `F`, called once via `*F(args)` written directly in source (no `EVAL`) — matches fine, no crash at stress 0–8 (expected: this is the already-known-safe static-name path, `_.op_sval` rodata, per §5).
   - The same, but with the pattern built via `EVAL("... *F(args) ...")` at runtime (the actual defect shape) — matched once, no loop, no crash at stress 0–35: too little allocation volume and too few site re-visits for a 1 MB arena's natural collection to land in the vulnerable window.
   - The same wrapped in `ARBNO(pat)` to force repeated re-entry into the one site — still no crash at stress 0–35: **one** EVAL-compiled defer site, however often re-matched, was insufficient in every variant tried.
   - Verified `.dummy`/`.dummyy` (unary-dot NAME references) do **not** behave as a null-string pattern the way I'd assumed — confirmed via oracle (`*G()` returning `.dummy` fails to match where the same call returning `''` succeeds identically on oracle and ours). Not the cause of anything, but a real trap for the next attempt: use an explicit `''` return, not `.dummy`, when hand-building a witness.
   - Confirmed empirically (oracle) that SNOBOL4 pattern concatenation is bare juxtaposition and `.` is immediate-value-assignment requiring a NAME on its right (`'a'.'b'` is ERROR 12, "value used where name is required"); `p . thy . *SHX(...)` therefore is NOT `p` concatenated with two things — it is `p` immediate-assigned into `thy`, and separately `thy`'s own match immediate-assigned through the *deferred call target* `*SHX(...)` resolves to (the "land" protocol — `rt_defer_land_γ`/`rt_defer_land_ω` in `pattern_match.c`). I did not fully reverse this protocol from source; it is why the bottom-up rebuild kept producing syntactically-valid-but-behaviorally-inert patterns instead of the crash.
   - **Conclusion, stated plainly so the next attempt does not re-spend it:** a single interacting EVAL-compiled deferred-CALL site, however matched, was NOT enough to reproduce this sitting, under every construction tried. Two were both necessary, and so far only demonstrated sufficient, in the presence of a parse that ultimately FAILS. Whether two sites and a failing match are achievable without any of the shift-reduce demo's supporting code is still open — named UNMEASURED, not ruled out and not assumed possible.

## 9. 2026-09-21, LATER — THE cfo's PASS-B SWEEP NARROWS THIS TO CLASS 3 (REGISTER-LIVE), REPORTED BY THE ceo (CEO-1066), NOT YET INDEPENDENTLY CONFIRMED BY ME

While the ablation in §7 was running, the `cfo` pointed the Pass-B conservative auditor (ARCH-GC rung 3) directly at this defect and got **findings=0** over 2234 in-heap words (every one MARKED), then widened the sweep to both writable `PT_LOAD` segments, the whole unceilinged C stack, and 1810 opaque block interiors — **still nothing.** Per the `ceo`'s framing (told to me, not independently re-derived this sitting): a conservative sweep that finds nothing after covering heap, both data segments, the full C stack and every opaque interior is a **silence that is itself a measurement** — by elimination, the stale holder is most plausibly live in a **register** at the instant of collection, a class-3 root no frame map can cover by construction (frame maps describe stack/heap slots at a safepoint, never register contents).

**What this changes for §5's candidate:** it does not contradict anything measured there — the deferred-call descriptor's *heap block* (`kind=205`/`HB_WSC`, confirmed by gdb in §3 and again in §7c) is real and is what gets reclaimed; class 3 answers a different question, namely *where the pointer TO that block was sitting, uncounted, at the moment of collection.* If correct, the fix is not "add a missing case to a heap/stack visitor" the way DT_X was — it is either (a) the emitter spilling this value to a mapped slot before any safepoint it is live across, or (b) the collector/frame-map format growing a way to describe live registers at a safepoint. Either is a `src/templates/x86` or `src/ir` matter, a shared node, and an ASK to the `cfo`/`ceo`, not a SNOBOL4-file landing, exactly as CFO-138 (DT_X) went.

**What I have NOT done:** independently reproduced or verified the Pass-B silence myself (I do not yet know how to invoke it — `gc_audit_b.c`/`.h` and `scripts/test_gate_gc_conservative_auditor_reports_and_cannot_ship.sh` landed in the SCRIP pull this sitting, unread by me before this addendum). Recorded here as **reported, not measured** — the distinction the whole repo's law insists on. If picked up next, invoking Pass-B on the 11-include witness from §7 myself, and reading the register-liveness claim off its own output rather than the `ceo`'s relay of it, is the first move before acting further on it.

## 8. UPDATED OWED/NEXT (supersedes §6 item 1 only; §6 items 2–4 stand unchanged)

1. The 11-`-INCLUDE` witness (§7c) is the new best repro — smaller than the 16-include original, same fingerprint, wider confirmed band — but is still "real, not small" by the shipped battery's own standard (all ten existing `gc_witnesses/hb_*` are include-free, single-digit-statement files). It is NOT wired into the battery and must not be, per the DT_X-row precedent (CFO-cure timing; ratchet-over-glob false positive risk) — there is no cure landed for this class yet.
2. Two concrete next moves, either of which would beat this sitting's result: (i) trace `Qize.inc`+`ReadWrite.inc`+`case.inc`+`assign.inc` line-by-line for the specific control-flow fact that makes the parse fail (§7c's open question) and replace whichever ones are load-bearing with a two-line stub, or (ii) resume the from-scratch bottom-up attempt (§7f) now armed with the corrected `.`/`*NAME(args)`-as-assignment-target semantics, aiming for a witness with two interacting EVAL-compiled defer sites and a deliberately-failing match, no `-INCLUDE`s at all.
3. Full 0–35 stress sweep of the ORIGINAL 16-include witness (this sitting's §7d table is for the 11-include reduction only) is still owed, for a clean apples-to-apples comparison of the two witnesses' bad-bands.
4. §6 items 2–4 (route the C holder to the `cfo` once minimal; characterize the trap-alone sensitivity on a second witness; the `util_gc_acceptance.py` stale-number flag) all stand, unchanged, and are now easier: the 11-include witness is a serviceable "second witness" for item 3 whenever picked up.
