# FINDING — four pattern ops aborted on a template arm that was already built and had never been reachable

**hq_C · 2026-08-29 · MODE FLEET-8 · SCRIP `41178ab8` · row `snoflake-suite-scrip-only-gap`**

## The defect

A deferred **expression** pattern argument — `POS(*(2 * N))` — lowers inside the PAT graph to:

```
0  LIT_STRING "EXPR$0"
1  CALL [0]   "SNO$MKEXPR"
2  MATCH_POS [1]          <- bb_slot_get(node 1) == -1
```

That call owns **no bb slot** but **does** own a ZLS offset. `IR_MATCH_LEN` already handled precisely this, falling
back to `zls_off()` and setting `op_zres`. `IR_MATCH_POS`, `IR_MATCH_RPOS`, `IR_MATCH_TAB` and `IR_MATCH_RTAB` did
not — they went straight to `drive_unowned()` and `abort()`ed rc=134, in **both** modes.

## ⭐ The part worth reading: the arm existed and was dead

`bb_match_pos.cpp` and `bb_match_rpos.cpp` each carry **three** live arms:

```cpp
IF(_.op_sa >= 0 &&  _.op_zres, x86("mov", "rax", ZOPQ(0, 8)))      // never reachable until this commit
IF(_.op_sa >= 0 && !_.op_zres, x86("mov", "rax", FRQ(_.op_sa + 8)))
IF(_.op_sa <  0,               x86("mov", "rax", (long)_.op_sb))
```

`bb_match_tab`/`rtab` have their own `if (_.op_zres)` branch. **The capability was fully built. Only the caller
never fed it**, so the emitter refused before reaching the code written for exactly this case. The cure needed no
template change whatsoever — one fallback in the caller, mirroring the sibling op four cases above it.

⛔ **The lesson: a dead arm in a template is not proof the case is unsupported — it can equally mean the caller is
refusing before it gets there.** Reading `drive_unowned` fired and concluding "POS doesn't support this" would have
been exactly backwards; `POS` supported it and `emit_drive` never asked.

## Why it hid

| form | result | why |
|---|---|---|
| `POS(2)` | ok | literal — `IR_LIT_INTEGER` branch |
| `POS(N)` | ok | evaluated at pattern-construction time |
| `POS(*N)` | ok | ⭐ deferred **bare variable** emits `MATCH_POS` with **zero operands** (carried via `sval`) |
| `POS(*(2 * N))` | **rc=134** | deferred **compound expression** — the only form that reaches the slot path |
| `LEN(*(2 * N))` | ok | LEN already had the fallback |

`sbl -bf` accepts **all five**. ⭐ The near-miss form `POS(*N)` looking healthy is what kept the class hidden: it
never reaches the failing path at all, so any spot-check of "does deferred POS work" answers yes.

## Scoped deliberately — and an assert is the only reason

The identical `else { int sl = bb_slot_get(a0); … }` line occurs **four** times in `emit.cpp`, not two. The other two
are **`IR_SCAN_MOVE`** and **`IR_SCAN_POS`** — Icon's scanning. Same latent defect, **no witness this session**, so
they are **left alone and named here** rather than speculatively patched.

⛔ **A blind `replace_all` would have changed Icon codegen with nothing testing it.** The patch script asserted on the
expected occurrence count, got 4 where it expected 2, and aborted before writing. **Assert the count, not just the
text** — the text matching in more places than you think is exactly the case that a text-only assert waves through.
Worth a row if anyone can mint an Icon witness for a deferred scanning argument.

## Result

**m3 PASS 75 → 76** · **m4 PASS 74 → 75** · SKIP(cc) 52 → 51 · defect surface (c) **34 → 33**. `fullscan-overlap`
`@expect` is `NO MATCH` and SCRIP now produces it, matching `sbl`. ⭐ **Compile-time crashes across all 180 fixtures:
3 at session start → 0** (swept, not sampled). Unlike this morning's TT_NOT cure, this one *is* a board gain and is
reported as one.

## Graded

Pristine `-O0`. `emit.cpp` is every frontend's codegen spine, so all are arms: SNOBOL4 `m3 1299/1299 · m4 1299/1299 ·
FAIL=0 SKIP=0 MISSING=0`; `emit_no_lang` rc=0; `template_medium_invisible` rc=0; `corpus_coverage_classified` rc=0;
icon 14/14 m4; snocone 5/5; rebus 4/4; prolog 5/5; raku 51/51.

⚠️ **Re-proved after a REAL merge.** The `pull --rebase` brought in Icon N-2 step-3 work touching
**`src/emitter/emit.cpp` — the same file** — plus `bb_call_proc_staged.cpp` and `x86_asm.h`. Verified mechanically
that both `ZLS FALLBACK` sites survived and both `SCAN_*` sites stayed bare, then re-ran the **entire** grade on the
merged tree. The two changes had never been graded together before that run — which is the whole point of the
rebase-baseline rule, and the one case where "the incoming commit says it graded green" is not enough.

⚠️ All three `.s` regen scripts reported *"already current"*, which is itself evidence: the fix altered no benchmark,
demo or prolog codegen — only the previously-aborting path.
