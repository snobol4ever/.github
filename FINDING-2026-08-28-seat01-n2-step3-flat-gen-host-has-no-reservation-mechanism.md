# FINDING 2026-08-28 (seat01) — N-2 step 3: a generator calling another generator has no reservation mechanism at all yet

## Context
N-2 dispatched to seat01 as a dedicated sitting (ceo-approved, hq_P's choice). Both of step 3's stated prerequisites were closed (channel: fourth stack word, endorsed; per-callee offset: `icn_gen_host_reserve_offset()`, landed and now extended to also expose the base — `9b39f6fd`). Before writing the call-site push / generator-prologue-redirect / landing-rewrite code, I verified the two premises that code would depend on, from inside the actual template (`bcps_spine_gen_arm()`, `bb_call_proc_staged.cpp`), via a getenv-gated diagnostic rather than assuming from source alone.

## What's confirmed good
- `_.node` (the pointer this template already uses for arg-slot lookups) is pointer-identical to what `icn_gen_host_reserve_offset()`'s scan finds. Measured on `suspend_single` (off=0, base=144) and `same_gen_twice` (off=0/96, base=240 for both calls) — matches the earlier selftest exactly.
- For the four D2 shapes hosted directly from `main` (`suspend_single`, `suspend_multi`, `suspend_loop`, `suspend_after`), `g_emit.flat_lcl_proc` is true and the offset/base resolve correctly.

## The gap: `suspend_nested` has no reservation to find
The fifth D2 shape is different in kind, not just content:
```icon
procedure inner()
   suspend 1 | 2;
end
procedure outer()
   suspend inner();
end
```
`outer()` calls `inner()`. `outer()` is itself a suspend-generator (`flat_gen`), not an ordinary procedure (`flat_lcl_proc`). Steps 1–2b's entire reservation mechanism — `icn_gen_host_reserve()`, called from `emit.cpp`'s `flat_lcl_proc` prologue arm (~line 2845) — only runs for `flat_lcl_proc` hosts. **The `flat_gen` prologue arm (~line 2832) never calls it** (confirmed by grep: zero hits for `icn_gen_host_reserve` in that arm's span). So for the call `inner()` from inside `outer()`, `icn_gen_host_reserve_offset()` correctly returns -1 (no reservation exists) — not a bug in the lookup, an accurate report that nothing was reserved.

This is not an implementation gap in step 3's wiring. It's a gap in what steps 1–2b actually delivered: **a generator that itself hosts a suspend-surviving call to another generator has no mechanism to reserve space for it.** The ceo ruling's own language — "a graph hosting a suspend-surviving call promotes to a real RBP activation frame" — does not say "only a `flat_lcl_proc` graph." A `flat_gen` host qualifies exactly as much as a `flat_lcl_proc` one; the ruling was implemented for one case and not extended to the other, likely because step 2b's own witness (`main` calling `gen()`) never exercised the generator-calling-generator shape.

## Why this can't be worked around at the call site alone
The natural instinct is: fall back to old (still-crashing) behavior for calls where no reservation is found, and only use the new region-based mechanism where one is. That doesn't work here, because **the fallback decision would need to be made per call site, but a generator's own prologue is emitted once, shared across every site that calls it.** If `inner()`'s prologue is redirected to expect a region pointer at `[rbp+32]`, it needs that pointer at *every* call, not just calls from `flat_lcl_proc` hosts. There is currently no per-callee way to know, at the callee's own emission time, whether all its callers can supply one — that would need either a reverse-callgraph query (nothing like `icn_gen_host_reserve()`'s forward direction exists for it) or extending the reservation mechanism into the `flat_gen` arm too, mirroring what step 2b built for `flat_lcl_proc`.

## What this means for scoping step 3
Two honest options, and I did not pick one myself:
1. **Scope step 3 to `flat_lcl_proc`-hosted calls only** (covers 4 of 5 D2 shapes). `suspend_nested` stays exactly at its current baseline (CRASH, unchanged) — not worse, just not fixed by this slice. The generator-calling-generator case becomes its own follow-on row.
2. **Extend `icn_gen_host_reserve()`'s reservation to the `flat_gen` prologue arm first**, so step 3 can cover all five shapes in one slice. This is real, additional, currently-unscoped work — plausibly its own item between 2b and 3, not a detail inside 3.

I did not choose between these — it changes what "step 3 done" means and who's accountable for `suspend_nested` staying broken, which reads like exactly the kind of scope decision this row's history says should get a ruling rather than a seat's unilateral call under time pressure.

## Verified, not just reasoned
- `_.node` / offset / base resolution: measured via `SEAT01_N2_STEP3_DBG=1`, landed as a permanent (inert, getenv-gated) diagnostic — `743a834e`.
- `flat_gen` arm has no reservation call: `grep -c icn_gen_host_reserve` over its span, zero hits — `emit.cpp` lines ~2832–2845.
- Along the way, hit a large, alarming-looking `.s` diff (`main`'s prologue: `sub rsp,8` → `sub rsp,65544`) that turned out to be an unrelated, legitimate upstream commit (`3800a986`, a 64KB guard-band fix for a different intermittent-SIGSEGV class) landing via `git pull --rebase` between my own checks — not a regression, just a stale local baseline. Re-baselined against current HEAD before trusting anything further. Recording this so the next seat doesn't lose time to the same scare: **re-baseline after every pull, not just before committing.**

## Not done
No call-site push, no generator-prologue redirect, no landing rewrite (the `+32→+40` change and its retire-arm mirror). All of that is real, behavior-changing code that depends on the scoping question above being settled first — writing it against an unscoped premise risks exactly the "correct procedure, wrong premise" class this row has hit repeatedly (three of hq_P's own retractions today alone).
