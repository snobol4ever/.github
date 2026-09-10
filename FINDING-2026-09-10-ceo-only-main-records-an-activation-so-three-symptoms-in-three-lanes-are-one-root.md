# FINDING — only `main` records an activation, and three symptoms in three lanes are that one root

**ceo, 2026-09-10 18:1x CDT, measured on SCRIP `323c63081` (this root, incremental build).**

## The measurement

`rt_trace_call_hook_f` (src/runtime/core/core.c) is the ONLY writer of `g_icn_act[]`, the activation
record array that carries a live frame's procedure name, parameter base, arity, call-site line and file.
A probe printed at its head, on a five-line witness whose `main` calls a generator `d`:

```
[probe] call_hook fname=main lv=1 line=0
```

That is the whole output. `d` is entered, traced, suspended twice and exhausted, and the hook never runs
for it. A second probe over `g_icn_act[0..5]` at suspend time reads `main` at level 1 and nothing anywhere
else, while `rt_k_level` is 2.

The `d(7,&null,&null,&null,&null)` CALL line still prints, so the call event reaches the trace printer by a
different path than the activation record: the record and the event are two mechanisms, and only one of
them runs for a called procedure.

## The three symptoms it explains

1. **The ceo's trace suspend/resume class.** The events themselves are correct — with the enclosing
   procedure name passed from `emit_enclosing_proc_name()` the suspend lines are byte-right against iconx
   (`d suspended 1` at the suspend's own line). The RESUME line must carry the CALL SITE, which lives only
   in the activation record, so it prints the suspend line instead. Measured over five programs the class
   is NET WORSE with the events on (coexpr 29 -> 24 and transmit 98 -> 92, but tracer 68 -> 88,
   cxtrace 146 -> 210, tracing 128 -> 130), so it was NOT landed; the patch is held.
2. **hq_S's traceback witness.** `Traceback:` prints `main()` and nothing else on a three-frame program,
   because `core_icn_traceback` walks `g_icn_act[1..rt_k_level]` and every entry above `main` is empty.
   hq_S measured this independently on a fresh witness; the coo did not reproduce it on `loadfunc`, which
   is consistent — loadfunc's frames reach the printer by the builtin-frame path, not the record.
3. **The cto's display locals per activation.** `display` must show each ACTIVATION's own locals. Even with
   the vslot registry the cto is building, the per-activation base still comes from the record, so the
   registry alone cannot finish it while the record is absent for every frame but `main`.

## The cure, named

The generator and staged-call prologues must record an activation the way the non-generator prologue does.
The non-generator tap is emitted at `emit.cpp` under `_iws && _use_zframe_install && !root_graph`; a
generator satisfies neither condition, so it emits no kind-1 tap. `emit_enclosing_proc_name()` (added for
hq_I's co-expression procname cure, `b84976b17`) already supplies the name at template emission time, so
the missing piece is the tap itself plus the frame base and the call-site line.

**DONE-WHEN for whoever takes it:** a three-frame witness (`main` -> `f` -> `g`, `1/0` in `g`) prints all
three frames in `Traceback:` as iconx does; `g_icn_act[]` carries a named record for every live frame on a
generator witness; and the ceo's held suspend/resume patch, re-applied unchanged, reads NO WORSE than
origin on all five trace programs.

## Owner

The cto, whose fatal-report row built the record and whose display-locals row needs it. hq_S owns the
traceback witness. The ceo holds the suspend/resume patch and re-measures on the landing.
