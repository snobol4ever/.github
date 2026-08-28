# FINDING 2026-08-28 (seat07): `zd_plan`'s `[ZD]` diagnostic node index `i` is CHAIN-LOCAL, not a stable node identity — cross-referencing it against `.s` label numbers (`n<i>_...`) silently picks the wrong node on any multi-procedure/multi-chain program

**Build:** SCRIP `afe050e1`, `make` (`-O0`, incremental over pristine HEAD). Discovered while testing `pascal-m4-for-spine-leak-64b-per-iter`'s storage-class hypothesis on `corpus/benchmarks/pascal/{bubble,queens,quick,perm}.pas` — full context and consequences in that row's own LEDGER; this file documents only the reusable instrument bug so nobody re-pays it.

## The trap

`zd_plan(IR_t **nodes, int n, ...)` (`src/emitter/emit.cpp:2484`) is called once per emission **chain** (roughly: once per procedure/program-block). Its own `[ZD]` diagnostic prints `i`, the position within **that call's own** `nodes[]` array — 0-based, and it **restarts at 0 for every chain** in the program.

The `.s` file's labels (`n<N>_<opkind>_α`, etc.) instead number nodes via `int _uid = g_flat_node_id++;` (`emit.cpp:2946`) — a single **global** counter, declared once (`emit.cpp:510`), reset only at the start of a whole compile (`scrip.c:1469`, `emit.cpp:3564`), **never per chain**.

These two numbers are identical **only for the first chain processed in a compile** (where the global counter happens to still read 0 when that chain's local `i` also starts at 0). For every later chain, the `.s` label number equals `i + base`, where `base` is however many nodes every **earlier** chain already consumed — a different, silent offset per program.

## Why this went unnoticed

`sieve.pas` and `intmm.pas` are flat, procedure-less programs — exactly **one** chain each — so `i == uid` trivially, always. Every prior session on this row that validated "read the target node straight off the `[ZD]` dump, look up `n<i>_var_α` in the `.s`" did so **only on these two witnesses**, where the bug cannot manifest. The technique was trusted as general; it was only ever exercised on the one case where the trap is invisible.

## Symptom when it bites

On `queens.pas` (one recursive procedure, `place`, plus the main block — two chains), looking up `[ZD]`'s `i=88` (reported op `IR_VAR`, `vn=rep`) as `n88_...` in the `.s` resolves to `n88_call_α` / `n88_call_bx` / `n88_call_β` — a **`CALL` node**, not the intended `IR_VAR`. Silent wrong-node lookup, no error, no crash — the kind of mistake that only surfaces if you happen to notice the op-kind doesn't match.

## The fix

Capture the base once, at `zd_plan`'s own entry, before anything in that chain has consumed an id:

```diff
 static void zd_plan(IR_t **nodes, int n, unsigned char *zon, int *zout, int *zgpop, int *zwpop, int *zarm) {
     extern const char * bb_src_of(const IR_t *);
+    int _uidbase = g_flat_node_id;
```

then print `_uidbase + i` (not `i`) as the field to cross-reference against `.s` labels. Verified directly: with the fix, `queens.pas`'s `i=88` reports `uid=339`, and `n339_var_α` in the `.s` is genuinely an `IR_VAR` node (`sub rsp, 16` self-carve on entry, matching `vn=rep`). Confirmed `uid` is stable for a shared node across `SCRIP_ZD_OMEGA_HEAD=0` vs default compiles of the same source (`i=0` reports `uid=251` identically in both arms of `queens.pas`) — nothing between the RPO chain-array build and `zd_plan`'s call touches `g_flat_node_id`, so this holds for any chain, not just the first.

## Scope / what this does NOT affect

- Nothing landed — this was a diagnostic-only addition (`SCRIP_ZD_DIAG=1` gated), applied and reverted in the same session alongside the row's own three-pass-split patch. `git status --short` clean, vanilla rebuilt to match.
- Does not affect any **prior** sieve/intmm-only result on `pascal-m4-for-spine-leak-64b-per-iter` — single-chain programs were never exposed to this bug.
- Does affect the credibility of any *future* attempt to eyeball `n<i>_...` in a `.s` file using a raw `[ZD]` (or similarly chain-scoped) index, on any program with more than one procedure, unless it also carries this fix or an equivalent global-id field.

## Recommendation

If this diagnostic pattern gets re-added permanently rather than as one-off throwaway instrumentation, bake the `uid` field in rather than re-deriving it per session.
