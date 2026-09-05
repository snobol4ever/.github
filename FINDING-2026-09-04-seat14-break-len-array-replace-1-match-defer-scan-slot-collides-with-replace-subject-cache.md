# FINDING 2026-09-04 seat14: `break_len_array_replace_1` remaining defect — root cause fully bottomed out (stack-slot collision, not a register clobber)

Row: `snobol4-xfail-class-arbno-fence-deferred-pattern-5-entries` (hq_T), item (a) of the task's `## NEXT`.
Continues `FINDING-2026-09-04-seat14-deferred-construct-row-two-cured-one-partial-plus-new-replace-span-defect.md`
section 3b, which left this "root cause not bottomed out past [ruling out an r14-clobber theory], next step
is a register/stack-level gdb trace across the `rt_call_proc_descr` call boundary." This FINDING is that
trace, carried all the way to the single offending instruction. **Not cured this session** — see "Why this
session did not fix it" below; XFAIL stays, reason line updated to this mechanism.

## Recap of the symptom

Witness `break_len_array_replace_1` (`A=ARRAY(3); PAT=LEN(1).*A<I>` matched/replaced against `S='xyz'` for
`I=1,2,3` in turn). Minimal single-statement reproduction used here (no loop needed — see below):

```
        A  =  ARRAY(3)
        I  =  1
        S  =  'xyz'
        PAT  =  LEN(1) . *A<I>
        S  PAT  =
        OUTPUT  =  '[S=' S '][A1=' A<1> ']'
END
```

scrip (m3 and m4, identical): `[S=][A1=x]`. Oracle: `[S=yz][A1=x]`. The capture itself is now CORRECT
(`A<1>` = `x`, thanks to 3a's fix) — the only remaining wrongness is that the match-replace deletes the
*entire* subject instead of just the matched `LEN(1)` span. **This reproduces on the very first and only
`S PAT =` in a single-statement program** — the "loop"/"second iteration" framing in the original witness
and in the prior FINDING is not load-bearing; it was never a multi-iteration/cumulative bug, it just also
breaks iterations 2/3 as a side effect of iteration 1 leaving `S` empty.

## Isolating the trigger (A/B, single mode, per ASM-DIFF-FIRST)

Three single-statement siblings, identical shape (`LEN(1)` match-and-replace over `S='xyz'`), differing
only in the capture target:

| capture target | goes through a compiled-thunk commit (`rt_call_proc_descr`)? | result |
|---|---|---|
| `. X` (plain, no defer) | no | `[S=yz][X=x]` — correct |
| `. A<I>` (subscript, no defer) | — | doesn't compile: unrelated pre-existing "runtime-built pattern" subset limit (GZ#5), not this bug |
| `. *Y` (deferred simple name) | no — `sno_capt_name`'s `TT_VAR` fast path bypasses the thunk entirely | `[S=yz][A=]` — correct |
| `. *F()` (deferred zero-arg function, `F = .G :(NRETURN)`) | **yes** | `[S=yz][G=x]` — correct |
| `. *A<I>` (deferred subscript — our witness) | **yes** | `[S=][A1=x]` — **wrong** |

This was the key result: `*F()` *also* invokes the exact same commit-time thunk mechanism
(`rt_dcap_pump`'s `*`-branch → `rt_call_proc_descr`) inside the exact same match-replace context, and it
works. So the bug is not "thunk call during match-replace is unsafe" in general (that was this session's
first hypothesis, and it's wrong) — it's specific to *something* the array-subscript container path
(`sx_idx_container()` / the `TT_IDX` capture-target thunk body, added by today's earlier 3a fix) does
differently from a plain function-call thunk body.

## Root cause, verified byte-for-byte with gdb

Built the witness for mode-4, and used `rt_match_replace`'s own arguments (real extern C function,
`src/runtime/rtx/rtx_match.s:293`, signature `(name, sub_lo, sub_hi, start, end, replp)`) as ground truth:

```
Breakpoint: rt_match_replace
sub_lo=12884901888 (0x0000000300000000)   <- WRONG: byte0 (tag) = 0x00 = DT_SNUL
start=0 end=1                              <- CORRECT (the LEN(1) span)
```

`start`/`end` are exactly right (0,1) — `bb_match_replace.cpp` computed the correct span. The subject
descriptor itself is corrupted: tag byte reads `DT_SNUL` (0) instead of `DT_S` (2), but the length field
packed in the same qword's high 32 bits still reads `3` (the original `"xyz"` length). A tag-only
corruption with the length intact is the signature of a **narrow (4-byte) write landing on part of a wider
live value**, not a wholesale wrong-address read.

Bisected with sequential breakpoints (`rt_match_enter` → `rt_defer_probe_run` → `rt_match_end_all` →
`rt_dcap_pump` → `rt_call_proc_descr` → `rt_match_replace`), checking the subject descriptor's tag byte at
each: **correct (tag=2) through `rt_defer_probe_run`'s return, already wrong (tag=0) by `rt_match_end_all`'s
entry.** Nothing else is called in between (confirmed against the `.s`: the only two calls in that whole
span are `rt_defer_probe_run` and, later, `rt_match_end_all`) — so the corruption is in the *inline* code
emitted between them.

Single-stepped that inline span (`stepi` in a loop, breaking on the first change to the watched byte).
The corrupting instruction:

```
0x555555555b1c: mov dword ptr [rsp + 192], eax      # source label .Lmatch_defer_α_102_4
```

At that exact program point, `$rsp = 0x7ffffffee000`, so `[rsp+192] = 0x7ffffffee0c0`. Independently
confirmed (via a breakpoint at `rt_match_replace` earlier in the same debugging session) that
`0x7ffffffee0c0` **is** the address `bb_match_replace.cpp` reads the cached subject `S` from
(`mov rsi, qword ptr [rsp+32]` at the call site, adjusted for the intervening `call`'s return-address
push). Same address, verified twice, independently, both ways.

`eax` here holds the low 32 bits of the global `g_scan_hit_start` (`src/runtime/pattern_match.c:609`). The
emitting code is `src/templates/bb/bb_match_defer.cpp:272-275` (byte-identical pattern also present in
`src/templates/bb/bb_match_value.cpp:31-34`):

```cpp
IF(_.op_scan && _.op_scan_head_off >= 0 && !emit_match_owns_startd(),
      x86("lea",  "rcx", "[rip + __]", ..., &g_scan_hit_start, "g_scan_hit_start")
    + x86("mov",  "rax", "[rcx]")
    + x86("mov",  emit_match_begin_stfh_k() > 0 ? "dword ptr [rsp# + 0]" : FR(_.op_scan_head_off), "eax"))
```

`emit_match_begin_stfh_k()` returns 0 whenever `emit_match_rbp()` is true (`emit.cpp:2226`), which it is
throughout this box graph — so the destination is `FR(_.op_scan_head_off)`, which resolved to `[rsp+192]`
in this witness. `_.op_scan_head_off` is a ZLS slot granted during lowering (`ir_drive_slot_assign`,
retrieved at emit time via `drive_value_slot()`, `emit.cpp:3239`) — it is **not** an ad-hoc offset computed
locally in this template.

**The collision**: the outer "S PAT =" statement caches its subject (`S`) on the stack once, early
(a plain, non-ZLS-tracked `sub rsp,16` in the generic var-read box), specifically so it survives the whole
match for `bb_match_replace.cpp` to read *after* the match completes. For a plain match (no replace), that
raw cache is dead/unneeded by the time any later box runs, so nothing cares what overlaps it. For a
match-**and-replace** statement, that cache must stay alive across the *entire* match, including whatever
scan/backtrack bookkeeping happens inside it — but the ZLS slot allocator that grants `op_scan_head_off`
does not appear to know about, or reserve around, that extended liveness. The result: `op_scan_head_off`
gets granted a depth that happens to land exactly on the subject cache's tag byte, in this witness's
specific stack shape.

This is consistent with why `*F()` doesn't trigger it: `*F()`'s capture-target thunk is invoked via the
exact same `rt_call_proc_descr` mechanism, but the *surrounding* match (no scan bookkeeping write at all in
that witness's simpler pattern shape, or a different `op_scan_head_off` depth) never emits this particular
colliding store. The bug is not "thunk calls are unsafe here" (ruled out this session) and not specific to
array-subscript capture targets *per se* — it's a stack-depth-dependent collision between two unrelated
things that both, correctly by their own local logic, believe they own that stack slot.

**Corroborating, pre-existing evidence that the project already knows of this class of issue**:
`bb_match_end.cpp`'s `stfh()` macro explicitly excludes replace-participating graphs
(`!has_replace_l()`) from its own fast stack-slot path, with no comment explaining why beyond the exclusion
itself — i.e. there is already a guard for an analogous "don't take the compact-slot path when a replace
box is in this graph" situation one template over. `bb_match_defer.cpp` / `bb_match_value.cpp`'s
`g_scan_hit_start` write has no equivalent guard.

## Why this session did not fix it

The write in `bb_match_defer.cpp:275` (and `bb_match_value.cpp:34`) is not decorative — it is gated on
`!emit_match_owns_startd()`, i.e. it exists specifically to hand off scan-start bookkeeping to whatever
FENCE/backtrack machinery reads it back later when the *initial* match position fails and a scan must
retry at a later position. This witness's match succeeds on the first try, so I cannot tell from it alone
whether the write is safe to skip or redirect in general.

Two candidate fixes, neither attempted:

1. **Redirect-on-collision** (narrow, template-local): add a `&& !has_replace_l()`-style guard to this
   write, mirroring `bb_match_end.cpp`'s existing precedent, so it's skipped or moved when a replace box
   coexists in the graph. Risk: unverified whether skipping it silently breaks a *scan-retry-plus-replace*
   program (e.g. a pattern needing to backtrack the top-level scan position through a match-and-replace
   statement) — no such witness exists in the corpus today as far as this session found, so "it still
   passes the blocking gate" would not actually prove this path safe.
2. **Allocator-level** (broad): extend whatever accounts for the subject cache's liveness in the ZLS slot
   allocator (`ir_drive_slot_assign`, spanning `src/emitter/emit.cpp`, `src/lower/lower_snobol4.c`,
   `src/lower/lower_prolog.c`, `src/ir/scrip_ir.c` — **confirmed shared with Prolog lowering**, and this is
   core BB-graph infrastructure Icon also lowers through) to reserve depth around a live match-replace
   subject cache before granting slots like `op_scan_head_off`. Correct in principle, but touches
   cross-language shared infrastructure I have no basis to validate beyond this one SNOBOL4 witness within
   this session — exactly the SHARED-NODE VERDICT SCOPE class of change the owning task/GOAL calls out,
   and the kind of change that per this project's law needs broader-than-one-row testing (at minimum a
   constructed scan-retry-plus-replace witness, plus the Icon watermark, plus a Prolog sanity pass given
   PROLOG REBUILDS FROM RUNG 0 is live and the instrument lane is supposed to stay out of `src/`) before
   landing.

Left for whoever picks this up with room to build and verify a scan-retry-plus-replace witness (or to
reason out from `ir_drive_slot_assign`'s allocation algorithm directly why it doesn't already reserve
around this liveness) rather than risk trading a well-understood, narrowly-triggered bug for a
worse-understood one under time pressure.

## Reproduction assets

Minimal witnesses (not corpus-committed, scratch only): single-statement `*A<I>` (broken), `. X` (plain,
control), `. *Y` (deferred-name, control), `. *F()` (deferred-function-thunk, control) — all under
`/tmp/seat14_probe/` this session, not preserved on disk beyond the session; the corpus's own
`break_len_array_replace_1` entry (`corpus/tests/snobol4/ALL.sno`) remains the canonical witness and needs
no changes.

## Files referenced (none modified this session)

- `src/templates/bb/bb_match_defer.cpp:272-275` — the colliding write (also structurally in `bb_match_value.cpp:31-34`).
- `src/emitter/emit.cpp:2226` (`emit_match_begin_stfh_k`), `:3239` (`op_scan_head_off` grant retrieval), `:1325` (`drive_value_slot`).
- `src/templates/bb/bb_match_end.cpp:25` (`stfh()`/`has_replace_l()` — the existing analogous guard, one template over).
- `src/runtime/pattern_match.c:609` (`g_scan_hit_start`), `rtx_match.s:293` (`rt_match_replace`, used as the verification oracle for the runtime call args).
