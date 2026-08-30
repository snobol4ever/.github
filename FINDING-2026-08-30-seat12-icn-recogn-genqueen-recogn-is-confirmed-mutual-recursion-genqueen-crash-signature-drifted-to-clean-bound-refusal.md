# FINDING: fresh measurement on `icn-recogn-genqueen-suspend-shape` — `recogn` is a confirmed, structural mutual-recursion exclusion (no apply-call ambiguity); `genqueen`'s armed-mode crash signature has drifted from a wild SIGSEGV to a clean `N2_SELFREC_SLOTS`-bound refusal, plus a new lead on what the depth counter actually counts

## WHAT THIS ANSWERS
Two things this row's own baton and its dependency (`icon-n2-recursive-generator-per-activation-storage`) needed but didn't have: (1) the row's own STEP 1 instruction — "confirm the premise before working it… if icon-n2's landed wiring already cures recogn, this row closes by measurement, not by assumption" — re-checked fresh at HEAD `d403c283`; still red, both witnesses, both modes. (2) seat11's newest, explicitly-unfinished lead on the dependency row ("[geddump's self-call] is consistent with an indirect/apply-style dispatch… settle with a live gdb break on the actual call site before any implementation attempt… NOT yet done by me") — settled here, but for `recogn`/`genqueen` specifically (this row's own witnesses), not `geddump`.

## SETUP
Fresh pull + `make pristine` at SCRIP `d403c283` (`-O0`). DONE-WHEN exactly as written in `icn-recogn-genqueen-suspend-shape.task.md`:
```
cd "$S4E_HOME/SCRIP" && for p in jcon_recogn jcon_genqueen; do
  bash scripts/test_icon_rung_suite.sh --rung rung36 --mode interp   2>&1 | grep -q "^PASS rung36_${p}$" || echo FAIL
  bash scripts/test_icon_rung_suite.sh --rung rung36 --mode compile  2>&1 | grep -q "^PASS rung36_${p}$" || echo FAIL
done
```
Both `jcon_recogn` and `jcon_genqueen` FAIL, both modes. `jcon_genqueen`'s signature has itself drifted since the task baton's own last note (was `ERROR 246` stack-overflow both modes, per the baton's STEP 1) — it is now a `rt_bomb` abort (rc=134), not a stack-guard hit. Confirms the row is genuinely still blocked, not closeable by assumption.

## `recogn`: real call sites traced, no apply-operator involved — this is squarely, and only, the untouched "(c) mutual recursion" bucket
`recogn`'s three generator call sites (`s()`→`s()`, `s()`→`t()`, `t()`→`s()`; compiled symbols `n35`/`n43`/`n75_proc_gen_bx`) all compile to ordinary parenthesized calls through the normal staged-call trampoline — **no `bb_call_value.cpp` apply-style dispatch anywhere in this witness.** All three hit an **unconditional `rt_bomb`**, byte-identical whether `SCRIP_ICN_N2_SELFREC=1` is armed or not (compiled and ran both arms; same rc=134, same message):
> `N-2 armed: generator call site has no reserved region (flat_gen host or forward reference) — transitive reserve is the follow-on row`

This is the `icon-n2-flat-gen-host-transitive-reserve` cycle refusal — **not** the depth-push/reservation-formula code (Root Causes 1/2) that essentially every prior session on the dependency row has centered its analysis on. Source confirms why arming can't help here, verified directly at current HEAD:
```
src/templates/x86/x86_asm.h:863   #define N2_SELFREC_SLOTS 64   /* row icon-n2-recursive-generator-per-activation-storage: bounded DIRECT-self-recursive generator storage (gedwalk-shaped...
src/templates/x86/x86_asm.h:914   an intermediary. That is the one narrow shape N2_SELFREC_SLOTS is sized for; a deeper i (mutual/multi-hop cycle) still refuses below exactly as before -- general recursion is explicitly [out of scope]
```
`recogn` is genuine mutual recursion (`s` calls `t`, `t` calls `s`) plus direct self-recursion — structurally excluded by the flag's own documented scope, not a bug hiding behind an unexplored code path. **Nothing new to chase here**: this is fully and precisely the "(c) mutual recursion, still squarely Lon/hq design territory" item every session on the dependency row has flagged as unattempted. It does not need further gdb archaeology — it needs the design ruling that's already been asked for.

## `genqueen`: same unarmed bomb, but a *different*, cleaner bomb when armed — a real signature change since 2026-08-29
Unarmed, `genqueen` hits the identical transitive-reserve bomb above, at `solvequeen(c+1)`'s call site (`n103_proc_gen_bx`). **Armed**, that site compiles ~100 lines of real staged-call/region-carving code instead of the 2-line bomb (confirmed via diff of armed vs unarmed `.s`) — i.e. `genqueen`'s self-recursion *does* enter the depth-push/reservation mechanism that `recogn` never reaches. Running the armed binary: rc=134 again, but this time it's
```
src/templates/bb/bb_call_proc_staged.cpp:733
x86_bomb("N-2 bounded self-recursion: depth exceeds the reserved N2_SELFREC_SLOTS table -- refusing loudly rather than silently reusing an in-use activation slot...")
```
— a **clean, loud, intentional bound-refusal (N=64, `x86_asm.h:863`)**, not the wild `rip=0x3`/`rsp=0xffffffffffffffde` SIGSEGV that the dependency row's most recent armed-mode entries (seat05, seat12, both 2026-08-29) recorded on this exact witness. **This is a real, verified crash-signature change**, not a re-description of the old one. I did not gdb the banked depth counter to find out why — out of this pass's time-box — so I am explicitly **not** claiming Root Cause 1 (the depth-push 8-byte-slot shortfall) is fixed, only that whatever changed, the failure mode is now a controlled bound-hit rather than corruption.

**New lead, unverified, worth stating precisely rather than chasing further this pass:** the default board is `n=6` (max live `solvequeen` recursion depth ≈6–7), yet it hits a 64-slot bound almost immediately. 64 is far larger than 6–7 concurrent activations, which is consistent with the counter tracking **cumulative/backtracked activations** (a 6-queens backtracking search visits many more than 6 nodes total over its run) rather than simultaneous recursion depth. If true, Root Cause 2's original framing ("depth ~2 overflow") describes the right defect class but an incomplete counting model — someone should gdb-trace the actual banked value across the run before revising the reservation formula, not assume either model.

## `hq_P`'s original `bb_call_proc_staged.cpp:733` citation (this row's own task baton, 2026-08-28) is stale
At `d403c283`, line 733 is the *new* `N2_SELFREC_SLOTS`-exceeded bomb quoted above — not the `lea rsp,[rax+32]` landing-arithmetic hq_P described. The file has grown/shifted since 2026-08-28; line numbers drifted. Moot regardless: **neither witness's crash currently reaches any landing code at all** — both die at earlier bomb sites (the transitive-reserve refusal for `recogn` and both unarmed-`genqueen`; the bound refusal above for armed `genqueen`). Flagging only so nobody re-cites the stale line number as current.

## NOT FIXED, no source touched, no design decision made
Per this row's and the dependency row's own standing discipline: Root Cause 2's formula and the mutual-recursion storage question are both explicitly Lon/HQ territory, not a unilateral call. This pass is measurement only.

## FOR WHOEVER RESUMES `icon-n2-recursive-generator-per-activation-storage` NEXT
1. `recogn` needs no more investigation — it is fully characterized as the mutual-recursion design gap. Resolving that design question resolves `recogn`, full stop; no separate mechanism to hunt.
2. `genqueen`'s new clean bound-refusal (vs. the previous wild SIGSEGV) is worth a deliberate gdb trace of the banked depth value across a full run, specifically to test the cumulative-vs-concurrent-depth hypothesis above before touching the reservation formula.
3. `geddump` (a different consumer, `icon-bench-correct-suspend-residue`) was NOT re-examined this pass — seat11's apply-vs-staged lead for `geddump` specifically remains open and separate from the findings here.

## THIS ROW (`icn-recogn-genqueen-suspend-shape`)
Re-parked `PARKED-AWAITING:icon-n2-recursive-generator-per-activation-storage` — same dependency as before, now confirmed current rather than assumed, with `recogn`'s piece of it fully diagnosed and `genqueen`'s piece re-characterized.
