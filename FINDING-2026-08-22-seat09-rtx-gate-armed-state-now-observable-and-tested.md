# FINDING — seat09: RTX_GATE family armed-state is now observable, and the static-archive constructor-drop hazard is negative-tested for real

**Date:** 2026-08-22 · **Seat:** seat09 (`/home/claude09`) · **Topic:** queue row `rung-static-archive-ctor-drop` (rank 1, HQ-redirected mid-session — see `answer-callout-m3-ladder-ruling` inbox message)
**Status:** DONE-WHEN met. Two new files, zero product source touched, zero new globals.

## 0. The hazard this closes

`FINDING-2026-08-22-seat01-kill-the-plt-measured-real-but-tiny-and-a-static-archive-constructor-trap.md` §5: a naive `ar rcs libscrip_rt.a *.o` static archive silently drops `rtx_init.o` (nothing else references any symbol inside it — its `rtx_gates_init()` constructor is reached only via `.init_array` registration, never by name), so its `__attribute__((constructor))` never runs, all 14 `RTX_GATE_*` fast-path family bytes stay at their `.byte 0` link-time default, and every one of ~14 hand-written-asm fast paths silently falls back to its (correct, ~2.05x slower) C implementation — program-correct, no error, no warning, nothing anywhere says so. This row's brief: **"YOUR ROW IS THE GENERAL HAZARD, not the static link"** — make the armed/disarmed state observable, make a dropped-constructor build fail a test for it, and prove that test can actually catch the drop by dropping one for real.

## 1. New file 1 — `SCRIP/scripts/probe_rtx_gate_armed.c`

A ~30-line standalone C probe: `extern`-declares all 14 `rtx_gate_*` bytes (the exact set from `rtx_init.c`'s own extern list — `misc alloc str leaf arith icnvar icnnum icnrel icnagg match icngen icncall icnsub plunify`), prints each name/value/ARMED-or-DISARMED, and exits `0` iff all 14 are nonzero, `1` if any are zero. No new global state — the only storage is a `main()`-local array. This is the "make it observable" half of the brief, usable standalone (`gcc probe_rtx_gate_armed.c <link-inputs> -o probe && ./probe`) independent of the gate script below.

## 2. New file 2 — `SCRIP/scripts/test_gate_rtx_ctor_armed.sh`

Three link arms, run for real, not reasoned about:

| arm | link style | result (this session) |
|---|---:|---|
| **A** (control) | probe.o + `out/rt_pic/*.o` listed **directly** (no archive) | **14/14 ARMED**, rc=0 |
| **B** (the trap) | probe.o + `ar rcs` archive of the same objects, plain link | **0/14 DISARMED**, rc=1 |
| **C** (the fix, seat01's arm C2) | probe.o + same archive, `-Wl,--whole-archive` | **14/14 ARMED**, rc=0 |

Gate passes iff A=ARMED, B=DISARMED, **C=ARMED** — three assertions, not two, matching this codebase's own QUARANTINE philosophy (`test_gate_rtx_killswitch_sets.sh`'s header): a negative test that cannot demonstrate its own negative (arm B reading ARMED would mean the probe can't detect the hazard at all) is worse than no test, so the script FAILS LOUDLY rather than silently passing if that ever happens.

### Why arm A isn't "link against `out/libscrip_rt.so`" — checked, not assumed

The gate bytes are deliberately `.hidden` (`rtx_abi.inc:71-76`: *"scrip links dynamically against libscrip_rt.so... hidden visibility makes `[rip+sym]` direct and interposition-proof"*) — hidden visibility suppresses **dynamic** symbol export, so an externally-linked probe cannot `extern` + link against the prebuilt `.so` to read them (verified: that link fails with `undefined reference to 'rtx_gate_misc'`, not a runtime answer — tried first, in `git`-untracked scratch, before settling on arm A's current form). A **plain** multi-object static link (objects listed directly, never through an `.a`) sidesteps both problems at once: hidden visibility only blocks *dynamic* export, and every directly-listed `.o` — `rtx_init.o` included — is unconditionally pulled in, the same object-inclusion property that (along with the dynamic loader's own unconditional constructor-running behavior, well-established ELF semantics, not re-verified here) is what makes today's actual `out/libscrip_rt.so` build safe. Arm A is the correct, meaningful control for "nothing is artificially excluding `rtx_init.o`," reachable the one way this probe design can reach it.

## 3. What this does NOT do, and why that's the right scope

Does not modify `rtx_init.c`, any `rtx_*.S` file, or the Makefile — the hazard's fix (if static linking is ever adopted for real) is `-Wl,--whole-archive`, already known from seat01's work and now independently re-confirmed by arm C; wiring it into the actual build is a decision for whoever revisits static linking, not this row (`kill-the-plt` itself was already recommended against — seat01 §7 — so there is no live static-link target to protect today). Does not add this script to the SNOBOL4-FIRST blocking gate set (`test_corpus_snobol4.sh` + `test_gate_emit_no_lang.sh` + `test_gate_template_medium_invisible.sh`) — that list is a Lon/HQ policy call, not a seat's to expand unilaterally; flagging it as a candidate for HQ, not deciding it here. Does not touch any existing file — `git status` in `SCRIP` shows exactly the two new files, nothing else.

## 4. Verification

`git status --porcelain` in `SCRIP`: two untracked files, nothing else. `test_gate_emit_no_lang.sh` rc=0 (unaffected — no compiler source touched). The gate script itself is self-verifying by construction (§2's table); re-run: `bash scripts/test_gate_rtx_ctor_armed.sh`.
