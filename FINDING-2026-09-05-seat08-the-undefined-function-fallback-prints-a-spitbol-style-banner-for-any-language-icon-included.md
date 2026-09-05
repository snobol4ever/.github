# FINDING — the shared "name not found anywhere" fallback prints a SPITBOL-style `ERROR NNN --` banner regardless of source language, Icon included

**Seat:** seat08 · **Date:** 2026-09-05 · **Mode:** FLEET-16 (hq_P lane)
**Row:** `snobol4-core-err-msgs-indexed-by-official-spitbol-error-numbers-compared-numerically`
**Tree:** SCRIP `f72ea9426` (pre-fix) / with this row's fix applied (post-fix), both measured

## 1. What was measured, and why it surfaced here

While fixing this row's two "wrong literal number" call sites (`driver_call.c:147`,
`core.c:2976` — both raised `core_runtime_error(5, NULL)` for "nothing by this name exists
anywhere", now `core_runtime_error(22, "Undefined function called")` per the manual, see this
row's LEDGER), I checked whether the SAME shared fallback is reachable from Icon — it is
architecturally shared (no `LANG_*` gate, per the project's own "language identity stops at
lower" rule), so a SPITBOL-specific number landing there could be wrong for an Icon caller.

Minimal witness, `probe_undef.icn`:
```
procedure main();
    x := nosuchproc(1);
    write("after");
end
```

**Before this row's fix** (SCRIP `f72ea9426`, `core_runtime_error(5, NULL)`):
```
(0) : ERROR 005 -- Undefined function or operation
in statement 0
```

**After this row's fix** (`core_runtime_error(22, "Undefined function called")`):
```
(0) : ERROR 022 -- Undefined function called
in statement 0
```

## 2. The actual defect — pre-existing, not introduced by this row

**Both numbers are wrong for Icon.** Icon has its own well-known runtime error numbering
(e.g. Icon's real "procedure or integer expected" class lives around runerr 106, a completely
different vocabulary from SPITBOL's Appendix D), and its own diagnostic format
(`run-time error N` / `Offending value: ...` / a call trace), not SPITBOL's
`(LINE) : ERROR NNN -- message` banner shape at all. **This row's fix does not create the
leak** — Icon already printed a SPITBOL-flavored banner through this exact fallback before
today, just with a different (also wrong) number. Confirmed by `git stash`/rebuild A/B on the
same witness: the banner *shape* is identical either side of this row's diff, only the number
changes (005 → 022). This is a pre-existing gap in how far "language identity stops at lower"
has actually been carried through — this ONE shared fallback (reached from `call_user_function`
in `driver_call.c` and from `APPLY_fn` in `core.c`, both serving ANY language's "name resolves
to nothing" case) has apparently never been taught to format or number its diagnostic
per-caller, because nothing in the corpus previously exercised an Icon call to a truly
undefined procedure through *this specific* path against a byte-exact Icon oracle.

## 3. Why this row's fix is still correct to land as-is

This row's own brief is specifically about SPITBOL/SNOBOL4 official error numbers ("22 being
the live instance" per hq_P's own framing) — Icon's error-reporting format is a different,
larger, pre-existing gap that a two-call-site numbering fix cannot and should not absorb.
Changing 5→22 does not make Icon's situation worse (same wrong banner shape, still not Icon's
own vocabulary) and does correctly fix the SNOBOL4/SPITBOL-facing case this row targets.

## 4. Scope for whoever picks this up — not claimed here

Correcting Icon's own diagnostic for "procedure not found" properly means either (a) giving
`call_user_function`/`APPLY_fn`'s fallback a way to know which diagnostic *shape* the calling
IR expects without a `LANG_*` flag (e.g., a caller-supplied error-reporting callback/vtable
already exists for some paths — `g_user_call_hook` — worth checking whether Icon's own driver
already installs one that should be handling this instead of falling through to
`core_runtime_error`), or (b) confirming Icon never legitimately reaches this fallback in a
correctly-lowered program and the real fix is upstream (Icon should raise its own runerr before
ever calling into this shared "by name" resolution path for a statically-undefined procedure
name). Not measured here which of the two is true — flagging for whoever owns Icon
correctness (hq_B's lane under the current FLEET-16 cut) to triage, not silently investigated
further on this row's budget.
