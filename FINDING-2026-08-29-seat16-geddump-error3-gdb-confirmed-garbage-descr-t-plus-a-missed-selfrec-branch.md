# FINDING — `geddump.icn`'s Error-3 gdb-confirmed as a corrupted `DESCR_t` (garbage type tag, invalid pointer), and the exact code path that lets it get that far

**Seat:** seat16 · **Date:** 2026-08-29 · **Row:** `icon-n2-recursive-generator-per-activation-storage`

## SELF-CORRECTION FIRST — MY OWN FIRST PASS ON THIS WAS WRONG, CAUGHT ONLY BY INSISTING ON A PRISTINE BUILD

seat12's LEDGER flagged, not chased down: `geddump.icn`'s `SCRIP_ICN_N2_SELFREC=1` run hits *"an unrelated
Error 3 (array/table reference) before reaching either root cause."* My first attempt to confirm this used
a binary built **before** a fresh `git pull` (a genuine staleness lapse, the same class this project
already has a named rule for — HQ-27). On that stale binary, armed and unarmed runs produced **byte-identical
output** (both just the `[GENHOST]` host-reserve refusal) — which, combined with an incomplete code trace
(I'd read `icn_gen_host_reserve()`'s outer shell and its doc comment, but not the full body of its recursive
helper `icn_gen_host_slice()`), led me to draft a FINDING claiming arming the flag "can make no observable
difference to `geddump.icn`, ever." **That draft was never committed. `make pristine` on a fresh pull
reversed the empirical result entirely**: armed and unarmed now diverge, and armed reaches a real,
reproducible Error 3 — exactly what seat12 reported. Recording this prominently because it is the second
time this exact session that a stale build silently produced a false reading (the first was hq_B's earlier
`&pos` false-regression report on a different row) — the discipline of rebuilding pristine before trusting
*any* empirical claim, not just before a formal gate verdict, is what caught this one before it left the
machine.

## THE MISSED MECHANISM

The transitive-reserve walk (`icn_gen_host_reserve()`, `x86_asm.h:950`) delegates to a mutually-recursive
pair, `icn_gen_host_reserve_walk`/`icn_gen_host_slice` (`x86_asm.h:913-940`). Inside `icn_gen_host_slice`,
when the walk finds a callee that is its own most-recent ancestor on the current path (direct
self-recursion — exactly `gedwalk`'s shape):
```c
if (icn_genframe2_selfrec() && i == nvisited - 1) {
    *out_bytes = (N2_SELFREC_SLOTS - 1) * (((fb + 15) & ~15) + 48); return 1;
}
return 0;   /* cn is its own ancestor on this path: cycle, refuse loudly by the caller */
```
**This is where `SCRIP_ICN_N2_SELFREC` actually enters the transitive-reserve computation** — I'd read the
outer function's doc comment and the call-site refusal in `bcps_spine_gen_arm()` (neither of which mention
`icn_genframe2_selfrec()` at all) but not this helper's body, and concluded the flag was invisible to the
host-reserve path entirely. It isn't: `gedload`'s walk into `gedwalk` recurses into `gedwalk`'s own graph
(since `gedwalk` is `flat_gen` with a `suspend`), finds `gedwalk` calling `gedwalk` again, and — armed —
computes a bounded reservation instead of refusing. `gedload`'s call into `gedwalk` then proceeds into real
execution, which the unarmed run never reaches.

## THE ERROR-3 SITE, GDB-CONFIRMED

Reproduces on a small (200-line) truncated `.dat`, not just the full file — cheap to isolate. Broke on
`core_runtime_error` (pending, since it isn't resolved until `libscrip_rt.so` loads):
```
Breakpoint 1, core_runtime_error (code=3, msg=0x0) at .../core/core.c:2081
#1  subscript_get (arr=..., idx=...) at .../pattern_match.c:276
#2  c_rt_subscript_var (base=..., idx=...) at .../pattern_match.c:1473
#3  0x00007fffeb406bc5 in ?? ()   -- compiled BB code, no symbol, expected
```
`subscript_get` (`pattern_match.c:230-276`) falls through every recognized shape (record-with-`c`-field,
string-keyed, array-via-`FIELD_GET_fn`) to the catch-all `core_runtime_error(3, NULL)` at line 276 when
`arr` isn't any of them. **The actual value at that frame:**
```
arr = {v = 64 '@', mod_op = 224 '\340', ..., {s = 0x70 <error: Cannot access memory at address 0x70>, ...}}
```
`v = 64` is not a valid `DT_*` tag (they're small, densely-packed enum values — `DT_A`/`DT_T`/`DT_S` etc.,
nowhere near 64), and the pointer variant reads `0x70` — 112 decimal, an implausibly small address, not a
real heap pointer, and gdb can't even read memory there. **This is memory corruption, not a semantically
wrong-but-valid Icon value** — a genuinely bad program would subscript a real string or integer and hit a
*different*, type-specific error, not a `DESCR_t` whose own type tag is nonsense.

## RELATIONSHIP TO ROOT CAUSE 1 — CONSISTENT, NOT PROVEN IDENTICAL

This is exactly the *shape* seat12's root cause 1 predicts (a garbage stack/header read manifesting as
nonsense downstream), and it fires immediately (small input, shallow recursion) rather than needing deep
accumulation — consistent with root cause 1's own measurement that corruption starts as early as the
*second* recursive call (`depth-1's banked value reads as 4213421 instead of 1`). **Not chased further to a
full proof** (tracing `arr`'s value backward through the compiled BB code to the exact corrupted stack slot
would need the same full-session instruction-tracing depth seat12 used for `genqueen` — out of scope for
this pass, flagged as the concrete next step rather than attempted in a hurry).

## DISPOSITION

Not fixed — same discipline as every prior session on this shared code; no source touched. Two things now
change for whoever continues:
1. **The `icn_gen_host_slice` direct-self-recursion branch above is the mechanism that lets `SCRIP_ICN_N2_SELFREC`
   affect a host-mediated call at all** — worth knowing before assuming (as I first did) that the flag is a
   no-op outside a self-recursive generator's own body.
2. **`geddump.icn`'s Error-3 is now localized to an exact, gdb-reachable line with a concrete garbage value**,
   reproducible on a small input — a much cheaper starting point than the full 24432-call trace for whoever
   confirms or refutes the root-cause-1 connection next.
