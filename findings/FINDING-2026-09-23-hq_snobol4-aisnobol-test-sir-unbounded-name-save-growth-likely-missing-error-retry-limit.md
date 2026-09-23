# FINDING — aisnobol's TEST/SIR regressed 5/7→4/7 under the new heap hard cap; root shape is unbounded `rt_name_save` growth, not a capacity gap (hq_snobol4, 2026-09-23)

Found while re-running the aisnobol package suite fresh (SCRIP `9dc4d12d4`, corpus `00de9e950`) per
Lon's 100%-suites order. `SCORE.md`/`SUITES.tsv` already carry the honest fresh number (aisnobol
4/7, superseding the 2026-09-16 5/7 reading) — this finding is the diagnosis behind that drop, not a
landed cure.

## Symptom

- `TEST.sno`: PASS on 2026-09-16 (`8f567e685`) → now FAIL m3 (crash after 20s timeout on that older
  binary — see below) / CRASH m4 (SIGABRT) on `9dc4d12d4`.
- `SIR.sno`: FAIL m3 (output mismatch, not investigated further here) / CRASH m4 (SIGABRT).
- Both crashes are the *same* signature: `[ZHP] heap exhausted AT THE HARD CAP`, requesting exactly
  **2097152 payload bytes of block kind 215**, with a nonzero collection count (20–34 collections
  already run) — i.e. NOT a zero-collections "missing safe point" shape, and not `demo_json`'s
  shape either (see below).

## It is NOT the demo_json class (declared-arena gap)

`demo_json` (fixed this session, SCRIP `9dc4d12d4`) needed a bigger *declared* arena and then ran
clean. Tried the same here: `SCRIP_HEAP_MB=8/16/32/64` against `TEST.sno` — every size **changes the
failure to `ERROR 246 -- stack overflow`** instead of passing. Growing the heap just lets the same
mechanism run further before hitting the real C stack limit. That rules out "just needs a bigger
window" — the growth looks unbounded, not merely underprovisioned.

## Traced with gdb (`c_rt_gcheap_alloc` → abort, live backtrace)

```
#5  c_rt_gcheap_alloc (type=215, payload_bytes=2097152) at src/runtime/rt/gc_heap.c:315
#6  rt_wsb_alloc (n=2097152) at src/runtime/rt/gc_heap.c:338
#7  rt_wsb_realloc (p=..., n=2097152) at src/runtime/rt/gc_heap.c:394
#8  rt_name_save_grow () at src/runtime/rt/rt.c:1326
#9  rt_name_save_push (names=..., cells=..., args=<g_call_args>, nargs=1, n=1) at rt.c:1340
#10 rt_proc_call_prologue (p=..., args=<g_call_args>, nargs=1, wn=0) at rt.c:1403
#11 rt_call_proc_descr (name="ATOM", nargs=1) at rt.c:1021
#12 core_apply_runtime_proc (name="ATOM", ...) at core.c:3879
#13 APPLY_fn (name="ATOM", ...) at core.c:3902
#14 rt_call_arr_impl (fn="ATOM", ..., sn4=1) at by_name_dispatch.c:5764
#15 rt_call_arr_bl_s (...) at by_name_dispatch.c:5680
#16 rt_call_arr_bl_sn4 (...) at by_name_dispatch.c:5675
#17..23 (compiled BB frames, no symbols)
#24 rt_proc_enter_named () at rt.c:1530
```

`g_name_save[]` (`rt_name_save_push`/`_grow`/`rt_name_restore`, rt.c ~1320-1350) is a global
doubling array, pushed on procedure-call prologue and popped (LIFO, back to a saved mark) on return
— this is the SNOBOL4-lane by-name/dynamic call dispatcher (`rt_proc_call_prologue`,
`rt_call_proc_descr`, `rt_proc_enter_named`; see rt.c:380's own comment: "the SNOBOL4 procedure
dispatcher that carries the C->BB population" — `by_name_dispatch.c`'s `_sn4` suffix confirms this
call path is SNOBOL4-specific, not shared with Icon/Prolog/Pascal/Raku). **Ownership: SNOBOL4 lane,
landable directly, not a collector ask** — `rt_name_save_grow`'s allocation itself goes through the
GC heap (`rt_wsb_realloc`) so it is subject to the new hard cap, but the growth policy and the
call site are pure SNOBOL4 dispatch code.

Because this is a proper push/pop stack, its peak size tracks **call depth**, not total call count —
so this reading is either (a) genuinely very deep recursion SPITBOL tolerates and SCRIP's per-frame
`name_save` overhead does not, or (b) the recursion itself is not supposed to go this deep and
something is failing to terminate it.

## The likely mechanism: an unterminated error-retry loop, not legitimate depth

stdout, before every crash, repeats the *same* diagnostic hundreds of times:

```
Argument number 1 to FAIL.IF.NIL.ELSE.SUCCEED (X)
has illegal datatype INTEGER.
Datatype CONS was expected.
```

`FAIL.IF.NIL.ELSE.SUCCEED` is an AI-SNOBOL library type-check helper; a genuine algorithm does not
call it hundreds of times with the same bad argument. This reads like a retry/error-recovery path
in the library (or in SCRIP's error routing under it) that never gives up — each retry recurses one
level deeper via `APPLY("ATOM", ...)`, growing `g_name_save` by one more frame's worth every time,
which is exactly the shape "heap keeps growing, collections keep reclaiming what they can, but the
*live* recursion depth itself keeps climbing" would produce. This is thematically adjacent to (but
not verified identical to) today's own `core: SETEXIT takes priority over EVAL's own error-swallowing
guard` landing (`a22f9c6ed`) — both are about whether an error path correctly stops instead of
silently continuing/retrying.

**Confirmed pre-existing, not a today regression**: the *same* `TEST.sno` invocation on the
pre-rebase tree `a22f9c6ed` (last week's baseline behavior, tested in a scratch worktree, since
removed) does not crash — it **hangs** (rc=124 at a 20s timeout) instead. Same defect, two different
terminal shapes: the old unlimited-growth heap let it run (slowly) forever instead of hitting a
cap; the new hard cap (CEO-1101) turns the same runaway growth into a fast, loud abort. The hard cap
did not cause this bug — it just changed a silent hang into a loud, attributable crash, which is
arguably a diagnostic improvement even though it moved the suite's number down.

## Next step, not done here (out of this session's remaining budget)

Find where in `core.c`/the by-name dispatch path `APPLY_fn`'s retry-on-type-mismatch behavior is
decided, and whether SPITBOL's own `&ERRLIMIT`/error-trap semantics bound it where SCRIP's does not.
`SIR.sno`'s identical block-215/2097152-byte signature should be re-checked against the same fix
once found — very likely the same root cause, not a second bug.
