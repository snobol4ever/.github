# FINDING 2026-07-17 (Claude Opus 4.8) — Raku ζ BUMP_LIFO flip is MODE-INVARIANT (RK-ZETA-3 gate GREEN); the s65 RSP proc-ABI "209/74" is STALE PROSE — REG-7 rbp already fixed it

**Session type: DIAGNOSTIC. No tracked source file changed by the experiment; the committed defaults are untouched (`ZC_ALLOC=MALLOC`, `ZC_PORT=FORTH`, `ZC_FRAME=RSP`).** The value of the session is this finding + the RK-ZETA cursor/ladder update in `GOAL-RAKU-BB.md`.

## The directive being executed (Lon, standing)
*"Move all BB's ZETA to the RSP-topped FORTH-like stack, except so-called escapee-type BB's which go on the heap."* = the ARCH-ZETA §13 two-flavor law applied to Raku (the **RK-ZETA ladder**). Template = SNOBOL4's proven ZB-FC method (`FINDING-2026-07-14-CLAUDE-RK-ZETA-RSP-MODE-INVARIANCE-PROVEN.md`).

## GROUND-TRUTH BASELINE at the committed default (measured this session — the docs were stale)
Fresh clone of `.github`, `corpus`, `SCRIP`, `x64`; toolchain installed; `make -j4 scrip && make libscrip_rt` at the committed default. Compiled-in config confirmed in `src/contracts/zeta_choices.h`: `ZC_ALLOC ZC_ALLOC_MALLOC` (L14), `ZC_PORT ZC_PORT_FORTH` (L123), **`ZC_FRAME ZC_FRAME_RSP` (L166)**.

| Suite | mode-3 | mode-4 |
|-------|--------|--------|
| **Raku** `test_smoke_raku.sh` | **PASS=283 FAIL=0** | **PASS=283 FAIL=0** |
| SNOBOL4 `test_crosscheck_snobol4.sh` | PASS=305 FAIL=2 | PASS=304 FAIL=2 SKIP=1 (DIVERGE 1: `1017_arg_local`) |
| Icon `test_crosscheck_icon.sh` | PASS=4 FAIL=0 | OK=4 |

Raku fails = **0**, both modes. The two SNOBOL4 fails (`expr_eval`, `141_pat_eval_double_fn_arbno` / `1017_arg_local`) are the pre-existing non-ζ tails.

## THE STALE PROSE — corrected per the STALE-ORIENTATION rule (source/measurement is truth)
`FINDING-2026-07-15-CLAUDE-RK-RSP-DEFAULT-PROC-ABI-REGRESSION.md` and the s2026-07-15e LIVE CURSOR assert that the committed `ZC_FRAME_RSP` default breaks the Raku proc-call ABI (args arrive empty, `return` propagates nothing) → **Raku 209/74**, and recommend reverting the default to `ZC_FRAME_R12`.

**That number is now false.** The finding's own reproduction probe:
```raku
sub five() { return 5; }
sub main() { my $x = five(); say($x); }
main();
```
prints **`5`** (the finding's stated CORRECT output; broken-RSP printed empty). The whole Raku smoke is **283/0**, not 209/74, and not the R12-era 264/19 either — the 19 OO/multi-dispatch tails are also gone.

**WHY:** the **REG-7 rbp frame-base split** landed in `x86_asm.h` (s87–s90, commits dated 2026-07-17 — *after* the 2026-07-15 regression finding). `x86_zr()`→`rsp` (FORTH bump/anchor cursor) and `x86_fb()`→**`rbp`** (stable frame base, seeded at every activation boundary; `x86_fr32/fr64_prefix` → `[rbp+…]`). This is exactly the mechanism the 2026-07-14 blocker said was missing ("a consumer can't reach a producer's rsp cell by a fixed offset — r12 is the stable common base"). **rbp is now that stable base; rsp is the Forth data stack.** The proc-call arg/return slots ride `[rbp+off]` and are correct cross-boundary. **⟹ DO NOT revert the default to R12 — the "RSP not ready" finding is obsolete; RSP+rbp is live and clean for Raku.**

## THE RESULT — RK-ZETA-3 mode-invariance gate, GREEN for Raku
Flip recipe (flags are NOT a make prereq — `rm` first): `rm -f scrip out/libscrip_rt.so && make ZCFLAGS='-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO' scrip libscrip_rt`. Built clean. Per-test verdicts captured under both allocators and `diff`ed:

- **Raku, MALLOC vs BUMP_LIFO: `diff` EMPTY — 283/0 both modes, DIVERGE = 0.** Non-escapee Raku ζ on the RSP bump-LIFO spine (escapees heap-promoted) is byte-identical to all-heap MALLOC.
- **SNOBOL4 peer: identical to MALLOC baseline** (305/2 · 304/2, same fail names).
- **Icon peer: identical** (4/0).

Same theorem as the SNOBOL4 proof: if any Raku ζ that must heap-promote were wrongly riding the LIFO spine it would corrupt and the fail-set would diverge; it does not. The flip is **proven safe for the currently-exercised Raku surface — measured, not asserted.**

## SCOPE / HONEST CAVEAT (do not oversell)
The proof covers the ζ that the **suite exercises**. Raku's escapee family (RK-ZETA-2) is **block/closure values with a captured ζ-env + EVAL/deferred thunks** — and Raku **lexical capture is not implemented yet** (RK-BLK-c is a future rung; RK-BLK-a landed block-as-value with NO ζ-env pointer). So the escapee heap-promotion path is largely *un-exercised because un-built*, not proven correct. **The mode-invariance gate MUST be re-run when RK-BLK-c (capture) and EVAL land** — that is where a wrong-flavor placement would first bite. The open blocker `FINDING-2026-07-13-CLAUDE-SN4-DEFER-RSP-64KB-DONATION-IS-THE-BLOCKER.md` sits in exactly this escapee/deferred-thunk path (RK-ZETA-2 relevant).

## LADDER STATE after this session
- **RK-ZETA-1** (non-escapee Raku BBs on the FORTH rsp/rbp spine, under MALLOC): **functional gate MET** — the committed default already routes Raku's shared value-slot boxes through the rsp/rbp REG-7 spine; Raku 283/0 both modes, no glibc abort under MALLOC (a wrong-ω free would abort mode-3). Full ASan-instrumented rebuild across CRT+CXXRT not performed this session (mode-3 jumps into emitted code ASan can't instrument; runtime-sink ASan pass deferred).
- **RK-ZETA-3** (flip + mode-invariance): **PROVEN for the exercised surface** (above). Formally re-open when escapees are built.
- **RK-ZETA-2 / -4**: unchanged (escapee heap-promotion; shim retirement) — both gated on RK-BLK-c/EVAL existing.

## Housekeeping
Nothing committed by the experiment; the source defaults in `zeta_choices.h` are unchanged (MALLOC/FORTH/RSP). The workspace binary was left as the `BUMP_LIFO` diagnostic build (gitignored, regenerated on next `make` at the MALLOC default). All three code repos clean throughout; `.github` carries only this finding + the cursor update.
