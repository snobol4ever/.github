# FINDING-2026-08-12k — HOME-RBX X-3 slice-2 entry point: drive_value_slot() is port-blind, and FR() takes its word for it

**Seat:** RBX · **Rung:** X-3 slice-2 (the "make locals reside" work § A named and predicted, never
run before this session) · **Session:** Sonnet 5, s35, continuation of `FINDING-2026-08-12j` in the
same session. **Zero code changed** — mechanism named, fix NOT landed, exactly the discipline X-2's
finding modeled.

## MONITOR-FIRST, not a re-sweep

Per RULES' law ("the bug lives between the FIRST DIVERGENT trace event and the previous one"), pointed
`test_monitor_3way_sync_step_auto.sh` (`PARTICIPANTS="spl scr"`, `SCRIP_ZETA_PORT=7`) at the witness
`FINDING-2026-08-12j` named (`crosscheck/patterns/041_pat_span.sno` — passes FORTH, SIG11s HEAP):

```
[ctrl] PARTIAL EOF step 4: ['scr'] done, others still running
  spl: still emitting @2 VALUE V = STRING(5)='12345'
  scr: EOF
```

First divergence is exactly the capture write (`V = SPAN(...)`) — SCRIP-under-HEAP dies at the exact
step SPITBOL emits the captured value. This also lines up with `FINDING-2026-08-12j`'s census
(`MATCH_ASSIGN_SAVE`/capture sites are among the 26 `ZC_PORT_FORTH`-gated consumers).

## gdb, not guessing from source

`gdb` wasn't installed (`apt-get install -y --no-install-recommends gdb` — the plain install failed on
an unrelated missing `libc6-dbg` package). With `SCRIP_NO_SEGV_HANDLER=1` (RULES' own instrument
lesson — SCRIP's handler swallows the fault otherwise):

```
Program received signal SIGBUS, Bus error.
0x00007ffff160047c in ?? ()
#1  0x00007ffff4723d74 in rt_outer_call () at core.h:32   ← JIT trampoline, no symbols beyond it (expected, dynamically emitted code)
```
`x/20i $pc-30` at the fault:
```
=> 0x7ffff160047c: mov %r14d,0x7f004(%rsp)     ; 0x7f004 = 520196 decimal
```
Not a garbage pointer — a garbage **offset**. `rbp`/`rsp` themselves are both ordinary, in-range stack
addresses; the write target is `rsp + 508KB`, walking clean off the mapped stack.

## Correlated against the compiler's own text output — the exact instruction, the exact field

Compiled the same witness both ports (`--compile … -o`) and diffed the SPAN box's own-cell save
(the r14d spill/restore around the scan loop):

**FORTH** (`n8_match_span_α`):
```
sub   rsp, 16                    ← the box carves its own small frame
...
mov   dword ptr [rsp + 20], r14d ← own-cell write lands INSIDE that carve
```
**HEAP** (`n8_match_span_α`):
```
                                  ← no carve at all (correctly suppressed — matches § A's port promotion)
...
mov   dword ptr [rsp + 520196], r14d   ← SAME [rsp+off] addressing, but off is now 520196
```
**The carve-suppression is port-aware. The addressing base is not.** Under HEAP the box correctly stops
reserving RSP space (consistent with locals moving to the heap-resident block per § A), but its own-cell
read/write instructions still emit `[rsp+off]` through the SAME `FR()` macro, with `off` now carrying a
value from a completely different numbering scale.

## The exact chain, source-line-precise

- `bb_match_span.cpp:56-ish`: `x86("mov", FR(_.x86_scratch_off), "r14d")` and the mirrored read — `FR()`
  is unconditionally RSP-relative; it has no port check (correctly so, if fed a port-appropriate value —
  see below).
- `emit.cpp:940` (and eight siblings: BREAK/BREAKX/TAB/RTAB/REM/ARB/BAL, all the SN4-PAT-3/ZB-FC family):
  `g_emit.op_fc_base = g_emit.x86_scratch_off;` — the FORTH-cell grant machinery reads this same field.
- `emit.cpp:1428` / `:1435`: **`g_emit.x86_scratch_off = drive_value_slot(nd);`** — the actual
  assignment. `drive_value_slot()` is the function whose return value is 520196 under HEAP for this
  node. Not yet read this session — this is the named next step, not a diagnosis of `drive_value_slot`
  itself.

**Working hypothesis, stated as hypothesis, not fact:** § A already established that FORTH's `sub rsp,K`
and HEAP's `add rbx,K` spend the *same* static-K grant (`fc_geom`, port-blind by design — "port-blind
geometry, port-selected flavor"). `drive_value_slot()` plausibly computes a cumulative offset against
that same K-tracking, which is small and per-statement-scale under FORTH's fixed small carve, but under
HEAP a live cumulative offset into a growing 1MB block can legitimately reach hundreds of KB (§ G: heap
blocks are 1MB, refills are monotone). If `drive_value_slot()` doesn't distinguish "small RSP-relative
in-frame offset" from "large HEAP-relative in-block offset," and `FR()` always renders its argument as
`[rsp+off]` regardless of which scale produced it, that mismatch is sufficient to produce exactly this
crash shape on every FORTH-gated own-cell site the moment the port changes — not just SPAN's.
**Falsifiable, not yet checked:** read `drive_value_slot()`, confirm whether it branches on
`x86_port_mode()` at all.

## Scope check — is this SPAN-only or the whole family?

Not verified this session. The same `g_emit.x86_scratch_off` pattern at `emit.cpp:940-950` feeds BREAK,
BREAKX, TAB, RTAB, REM, ARB, BAL identically — all nine are one code shape, so a fix (or a falsification
of the hypothesis) at one likely generalizes to all nine. Named as the acceptance surface for whoever
takes X-3 slice-2 next, not claimed as proven.

## What this does NOT do
No fix attempted. This is real codegen surgery under TEMPLATE-ONLY (`FR()`/`x86()` internals) and
BOTH-MEDIUM (must be correct in TEXT and BINARY, and `drive_value_slot()` is called at emit time for
both) — it needs its own gate-proving cycle, not a same-turn patch bolted onto a diagnosis. Zero `.s`
regen triggered; own-HEAD floors from `FINDING-2026-08-12j` stand unchanged.

## FILED OUTWARD
- **→ this seat, next rung (X-3 slice-2):** read `drive_value_slot()` (`emit.cpp`, called from the two
  sites at ~1428/1435); confirm or falsify the port-blindness hypothesis above; if confirmed, the fix
  shape is almost certainly "make `FR()`'s caller pick RSP-relative vs a heap-block-relative addressing
  form based on `x86_port_mode()`" — a template-internal change, TEMPLATE-ONLY/BOTH-MEDIUM discipline
  applies, gate-prove against all nine `x86_scratch_off` consumers before calling it closed.

**UNBLOCKS: RBX X-3 slice-2**, source-line-named, ready for a session with runway to spend on the actual
fix + its gate cycle rather than one more turn of reconnaissance.
