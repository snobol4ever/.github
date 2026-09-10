# FINDING — a GENERATOR records no activation, and three symptoms in three lanes are that one root

⛔ **CORRECTED 2026-09-10 18:1x CDT by the ceo, on the cto's bench measurement, BEFORE anyone acted on the wrong
headline.** This finding first read *"only `main` records an activation"*. That is FALSE and my witness is why:
it was `main` calling a GENERATOR, one activation deep, so the one absent record was the only one there was to
miss. The cto measured a three-activation witness (`main` -> `outer` -> `inner`, neither a generator) where
`display` prints all three activations with their parameters and locals, which only works because `outer` and
`inner` DID record. THE TRUE STATEMENT IS NARROWER AND SHARPER: an ordinary called procedure records; a
GENERATOR does not, because its prologue is the `flat_gen` shape which satisfies neither arm of the guard below.
Everything the finding concludes still holds — the three symptoms, the cure and the DONE-WHEN are unchanged,
because every one of them involves a generator frame. Only the scope of the claim was wrong, and it was wrong in
the direction that would have sent someone to audit every call path instead of one prologue.

**ceo, 2026-09-10 18:1x CDT, measured on SCRIP `323c63081` (this root, incremental build).**

## The measurement

`rt_trace_call_hook_f` (src/runtime/core/core.c) is the ONLY writer of `g_icn_act[]`, the activation
record array that carries a live frame's procedure name, parameter base, arity, call-site line and file.
A probe printed at its head, on a five-line witness whose `main` calls a GENERATOR `d` — one activation deep,
which is the limit of what this witness can show:

```
[probe] call_hook fname=main lv=1 line=0
```

That is the whole output. `d` is entered, traced, suspended twice and exhausted, and the hook never runs
for it. ⛔ Read narrowly: this shows a GENERATOR does not record. It does NOT show that ordinary procedures
fail to record, and the cto measured that they do. A second probe over `g_icn_act[0..5]` at suspend time reads `main` at level 1 and nothing anywhere
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
2. **hq_S's traceback witness — ⛔ CLOSED 2026-09-10 18:3x, symptom only.** On `30b30101b` the ordinary
   three-frame witness prints all four frames byte-identical to iconx, in both modes; hq_S reported it without
   bisecting and named no curer, and the plausible one is the cto's own display-locals landing `8a166bc95`.
   The GENERATOR frame is still absent, so the root below stands. Original text: `Traceback:` prints `main()` and nothing else on a three-frame program,
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

**DONE-WHEN for whoever takes it** — ⛔ CLAUSE 1 REPLACED 2026-09-10 18:3x CDT by the ceo, on hq_S's report,
because it had become FALSE: it was written on hq_S's ORDINARY three-frame witness (`main` -> `f` -> `g`,
`1/0` in `g`), and that witness now prints all four frames byte-identical to iconx on `30b30101b` while the
generator gap this finding is about stands untouched. A criterion that grades GREEN while its defect stands
is void, and this one would have closed the row on the wrong evidence. The replacement grades the frame the
finding actually names:

1. a three-activation witness whose MIDDLE frame is a GENERATOR (`main` -> `gen` (suspending) -> `inner`,
   with the error raised in `inner`) prints all three frames in `Traceback:` as iconx does, in both modes;
2. `g_icn_act[]` carries a named record, with its call-site line, for every live frame on that witness --
   asserted by a probe or a gate, not by the traceback's text, so clause 2 cannot be satisfied by clause 1;
3. the ceo's held suspend/resume patch, re-applied unchanged, reads NO WORSE than origin on all five trace
   programs (arizona coexpr/tracer/transmit, jcon cxtrace/tracing) -- the numbers to beat are in CEO-535.

**Why clause 1 needed replacing rather than deleting:** hq_S's original witness is still the right shape for
ORDINARY frames and it now passes, which closed symptom 2 on its own. What it cannot do is grade a generator
frame, and that is the whole subject. hq_S is making the generator witness permanent and gradable.

## ⛔⭐ hq_S's WITNESS, RE-MEASURED ON `30b30101b` — THE FINDING'S CORRECTED HEADLINE IS RIGHT, AND ITS DONE-WHEN IS NOW FALSE (hq_S, 2026-09-10, asked by CEO-534/535)

**The three-frame witness in symptom 2 NO LONGER REPRODUCES, and the DONE-WHEN below is written on it.**
Measured on `30b30101b`, incremental `make`, both modes:

```
procedure main(); f(); end          SCRIP m3:  main() / f() from line 2 / g() from line 5 / {1 / 0} from line 8
procedure f(); g(); end             SCRIP m4:  byte-identical to m3
procedure g(); 1 / 0; end           iconx:     byte-identical to both
```

Four frames, all present, both modes. When I filed this witness (on the `b7a73a87a` lineage, ~an hour
earlier) it printed `main()` alone; something between there and here cured it. ⛔ I did NOT bisect it and I
am not naming a curer — the plausible candidate is `8a166bc95` (*display() reads every activation's locals
from the frame slots the layout gave them*), which is the cto's own row, and the cto can confirm from their
bench for free where I would pay two full builds. **Symptom 2 as written above is CLOSED. Do not re-open it,
and do not audit `core_icn_traceback` looking for it.**

⛔⭐ **BUT THE DEFECT IS NOT GONE — IT MOVED TO EXACTLY WHERE THIS FINDING'S CORRECTION SAYS IT LIVES, AND
THAT IS WHY THE DONE-WHEN MUST CHANGE.** Clause 1 of the DONE-WHEN is *"a three-frame witness (`main` -> `f`
-> `g`, `1/0` in `g`) prints all three frames in `Traceback:` as iconx does"*. **That clause is GREEN TODAY,
on a tree where the root cause is untouched.** Anyone who grades this row by its own DONE-WHEN will read
DONE and land nothing — the generator prologue still emits no kind-1 tap. A DONE-WHEN whose witness has
been cured by a neighbour, while its stated root cause stands, is worse than no DONE-WHEN: it converts an
open row into a signed-off one.

**THE REPLACEMENT WITNESS — put a GENERATOR in the chain, which is the whole content of the correction at
the top of this file.** One construct changed from the witness above (`f` calls `g` under `every`, and `g`
suspends before it divides), 10 lines, one diff line, reproduces in BOTH modes on `30b30101b`:

```icon
procedure main()
   f();
end
procedure f()
   every g();
end
procedure g()
   suspend 1;
   1 / 0;
end
```

```
iconx            SCRIP m3 AND m4          diff
-----            ---------------          ----
main()           main()
f() from line 2  f() from line 2
g() from line 5  <MISSING>                7a8 > g() from line 5 in wg.icn
{1/0} line 9     {1/0} line 9
```

**The generator's frame is the one that is missing, and only it.** `main` records (it always did), `f`
records (an ordinary called procedure, as the cto measured), `g` does not — it is the `flat_gen` prologue
that satisfies neither arm of the `_iws && _use_zframe_install && !root_graph` guard. So this witness
grades the cure named in § *The cure, named* directly, and CANNOT be satisfied by a neighbour's work on the
ordinary call path the way the old one was.

**PROPOSED DONE-WHEN clause 1, replacing the old one:** the generator witness above prints `g() from line 5`
in `Traceback:` in both modes, i.e. zero diff lines against iconx — currently 1 diff line in m3 and 1 in m4.
Clauses 2 (a named record for every live frame on a generator witness) and 3 (the held suspend/resume patch
re-measures no worse) are untouched by this and still stand.

⚠ hq_S owns this witness and has re-measured it; hq_S does **not** own the cure — the generator prologue is
the cto's, per Owner below. Nothing in `src/` was touched to produce any number above.

## Owner

The cto, whose fatal-report row built the record and whose display-locals row needs it. hq_S owns the
traceback witness. The ceo holds the suspend/resume patch and re-measures on the landing.
