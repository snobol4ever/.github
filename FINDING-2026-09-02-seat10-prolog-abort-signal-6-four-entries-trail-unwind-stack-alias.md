# FINDING prolog-master-red-class-abort-signal-6-four-entries — CURED

## SYMPTOM
Four Prolog master-board entries died on SIGABRT (rc=134) in both modes: `between_ite_naf_1`, `findall_dcg_directive_1`, `forall_ite_directive_1`, `list_directive_2`. All four print `*** stack smashing detected ***: terminated` — a `-fstack-protector` canary check firing, not a hand-written `abort()`/assert. `list_directive_2` (plain `member/2` + `fail`-loop, no ITE/NAF/findall at all) also hits it, on its 3rd backtrack — so the shared cause across the other three is NOT if-then-else/negation-as-failure as the baton's own hypothesis suggested; it is backtracking depth.

## ROOT CAUSE (gdb `-location` watchpoint on the canary slot, not guessed)
`pl_trail_unwind()` (`src/parsers/prolog/pl_cell.h:77`) restores a variable binding on backtrack via `*ents[t->top].addr = ents[t->top].old;`, where `.addr` is the address of a Prolog variable cell. Per the s273 design law, Prolog variable cells ride the C stack (spine/activation-frame), not the heap. `plc_dead_cstack()` exists specifically to detect when such a trail address has outlived its C-stack frame (so restoring through it would write into whatever now occupies that memory) and skip the restore — but it is a no-op whenever `g_plw_unwind_floor` is NULL, and `g_plw_unwind_floor` only gets set when `g_plw_floor_bypass` is 0. `scrip.c` sets `g_plw_floor_bypass = 1` for the whole duration of every Prolog zframe-graph run, so `plc_dead_cstack()` never actually runs for Prolog today (already flagged as an open, unproven-safety bypass on the `prolog-plw-floor-bypass-safety-unproven` row, hq_P's lane).

Watched `*(long*)($rbp-0x18)` (the canary slot of a live `dop_call_nothrow()` frame) across the crashing call on `list_directive_2`: it is written by `pl_trail_unwind`'s restore, from a trail entry whose `.addr` is `dop_call_nothrow`'s own `out` local (specifically `&out` + 8, landing inside the struct-copy write's range) — i.e. a stale trail address from an earlier, already-returned C frame, now aliasing this frame's `out` local and clobbering the adjacent canary when the (unrelated) old value is written back. This is a live, reproducible instance of exactly the class `prolog-plw-floor-bypass-safety-unproven` names as open and unproven.

## FIX (scoped to this row, not the general bypass question)
`dop_call_nothrow()` (`src/runtime/by_name_dispatch.c:1495`, the only two callers of which are `$trail_unwind`/`$unwind_nothrow`) now computes and arms its own `g_plw_unwind_floor` unconditionally for the duration of its own call, saving and restoring **both** `g_plw_unwind_floor` and `g_plw_floor_bypass` around the call — so `plc_dead_cstack()` is live only inside this one narrow leaf, for exactly the trail-unwind operation the bypass note already names as the risk, and `dop_call()` plus every other Prolog builtin keep today's bypass behavior untouched. This deliberately does **not** answer whether the bypass is safe to lift generally — that stays hq_P's row.

⛔ Tried first and rejected: forcing `g_plw_floor_bypass = 0` globally (e.g. once at program start) does stop the SIGABRTs but changes `list_directive_2`'s own behaviour into a long wrong-answer loop (repeated `_G0`) before exiting cleanly — the floor computed from whichever C frame happens to be current is evidently too coarse to leave armed across the *whole* run. Scoping the arm to just the two nothrow builtins' own call window avoids that; see the RESULT section for what still doesn't come out byte-correct even scoped.

## RESULT (SNOBOL4-blocking-corpus-style board, `corpus_suite_harness.py run … --lang prolog --modes m3,m4`, RT_OPT=-O0, pristine `make`)
Control arm, same tree, only this one file touched (`git stash` / `git stash pop`, rebuilt both times):

```diff
- SUITE_BOARD total=371 m3_pass=220 m3_fail=135 m3_crash=7 m4_pass=209 m4_fail=146 m4_crash=7   (before)
+ SUITE_BOARD total=371 m3_pass=221 m3_fail=138 m3_crash=3 m4_pass=209 m4_fail=150 m4_crash=2   (after)
```
- All 4 named entries: SIGABRT (signal 6) → non-signal exit, both modes. `findall_dcg_directive_1` m3 now byte-matches the oracle (`PASS`); the other three modes/entries move CRASH→FAIL (output mismatch) — an honest wrong answer, which the row's own DONE-WHEN explicitly accepts ("does NOT require them to PASS").
- Remaining crashes after the fix are the pre-existing, unrelated signal-11 class: `findall_directive_replace_{2,3,4}` — that's `C16 prolog-findall-directive-replace-segv`, a different row, untouched by this change.
- One board line moved `CRASH(signal 11)→HANG(10.0s)` for `findall_directive_replace_4` m4 on the after-run; re-tested that single entry directly 3x outside the harness and got a fast, consistent SIGSEGV every time (one run's core dump took ~10s to write under concurrent fleet load, which is what the harness's wall-clock timeout saw) — logged here per the FACT RULES rather than silently dropped, but it does not replicate standalone and is not attributed to this change.
- Prolog smoke: 5/5 both modes. Cross-language reach: `grep -rl "g_plw_floor_bypass\|dop_call_nothrow"` outside `by_name_dispatch.c`/`scrip.c` is empty — confined to Prolog dispatch, no SNOBOL4/Icon/other-frontend code path reaches either symbol.

## LINKS
LADDER:C · sibling C16 `prolog-findall-directive-replace-segv` (signal 11, untouched) · `prolog-plw-floor-bypass-safety-unproven` (hq_P) is the general question this does not answer · SCRIP commit: see this row's LEDGER.
