# FINDING 2026-09-06 hq_U — the return tap's view of a by-name slot and the caller's return value are two consumers of one restore, and every previous attempt bought one by spending the other

**Row 521** `defined-proc-own-name-blank-via-byname-lookup-mid-return`. Landed with the row's gate re-cut so it
can no longer be satisfied by the trade that got the last attempt reverted fleet-wide (CEO-333).

## The mechanism, read off the template rather than inferred from symptoms

`bb_define_sr()`'s γ continuation ends a DEFINE'd call in this order:

```
mov rdi, GQ(rgx,0)   ; the proc's own-name cell -> rdi:rsi   (the return value)
mov rsi, GQ(rgx,8)
FRESTORE(80)         ; writes GQ(gk4[...],0/8): restores EVERY saved GVA cell
mov rcx, SIGQ(8)     ; return address (rcx is FRESTORE's own scratch, so it must be loaded after)
add rsp, F4
mov rax, rdi         ; stage the return value for the caller
mov rdx, rsi
<TRACE RETURN tap -> rt_trace_return_hook>
jmp rcx
```

`FRESTORE` is the whole story: it restores the proc's own-name GVA cell to its **pre-call** value. The registers
carry the return value out safely, but the tap fires *after* the restore, and a callback doing `$NAME` reads
**memory**, not `rax:rdx`. So the callback sees the restored (blank) cell. That is the row's literal symptom.

⛔ **The two consumers are the point.** The by-name tap wants the own-name cell *un-restored*; the caller wants
`rax:rdx` *staged*. `FRESTORE` sits between them and clobbers `rax`/`rdx` as scratch. Move the tap earlier and
the caller loses its value; leave it late and the tap loses its view. Every attempt so far picked one.

## The cure

Fire the tap **before** `FRESTORE`, then **re-stage** `rax:rdx` from `rdi:rsi` after it:

```
mov rdi/rsi <- own-name cell
mov rax, rdi ; mov rdx, rsi        ; the tap's contract: rax:rdx hold the return value
<TRACE RETURN tap>                 ; own-name cell still live -> $NAME resolves
FRESTORE(80)                       ; clobbers rax, rdx, rcx, r8
mov rcx, SIGQ(8) ; add rsp, F4
mov rax, rdi ; mov rdx, rsi        ; RE-STAGE -- seat11's clobber, paid once
jmp rcx
```

`rdi:rsi` are the invariant that makes this work: `FRESTORE` uses `rax`/`rdx`/`rcx`/`r8` and never touches them,
and the tap saves and restores them across its call. The tap's `rsp`-relative reads (`+48`, `+56`) address its
**own** pushes, so moving it above `add rsp, F4` does not move them, and its push/pop set is balanced on both
the traced and untraced paths — so `rsp` is unchanged when `FRESTORE` runs.

## Why the gate was re-cut, and the proof that the re-cut is load-bearing

The old DONE-WHEN graded one output line: `tf tagR F = 2`. **d067ceae4 satisfied it while every DEFINE'd
function returned blank**, and was reverted fleet-wide. The gate now grades the **discriminator** beside the
target — an ordinary `DEFINE('G(X)'); G = 7; OUTPUT = G(...)` return value, both modes, same oracle.

⭐ **Falsified rather than asserted.** I rebuilt with the re-stage removed — d067ceae4's exact shape — and ran
the new gate:

```
PASS m3 byname-mid-return: [tagR F = 2]        <- the OLD gate's whole criterion, green
PASS m4 byname-mid-return: [tagR F = 2]
RED  m3 ordinary-return-value(discriminator)   <- blank return value
RED  m4 ordinary-return-value(discriminator)
GATE FAIL(1) ... (examined 4)
```

So the gate now rejects the commit it previously accepted. **A DONE-WHEN that names one output line cannot
notice what the cure spent to get it**; grading the discriminator, not the target, is the structural fix.

## Measured

- **Row gate** `test_gate_sno_proc_own_name_byname_mid_return.sh` — `GATE PASS(0)`, examined **4** pairs.
- **hq_P's canary** `.github/probes/trace/trace_trunk.sno`, the witness whose adjacent lines traded places
  across d067ceae4 — **both green, both modes**, which no previous attempt achieved:
  line 3 `tf tagR F = 2` and line 4 `tf tagN N = 2`. (`lastno=4` vs `12` is hq_P's own pre-existing gap,
  ruled not mine.)
- **SNOBOL4 master** and the Prolog control arm: see the landing commit; both hashes named there.

⛔ **A refusal I caused and am recording because the instrument was right and I was wrong.** My first master
board for this row printed `GATE REFUSES: harness produced no SUITE_BOARD line` — because I rebuilt `scrip`
twice underneath it while running the falsification. The board refused instead of publishing a number graded
on two binaries. The ceo's hazard rule reads "never run a handoff while anything measures in your root"; the
symmetric half is the one that bit me: **never build while anything measures in your root**, including your
own next command.

## Shared-node scope

`grep -c IR_DEFINE src/lower/lower_*.c` — snobol4 **9**, prolog **1**, everything else **0**. Prolog's single
occurrence is a *read* (`g->entry->op == IR_DEFINE && IR_LIT(g->entry).ival == 3`), not a construction — but
`emit.cpp:2960` maps `ival == 3` to `op_define_role = 0`, which **is** `bb_define_sr`, so the Prolog board is
genuinely owed rather than waved off on the grep's shape. Icon lowers no `IR_DEFINE` and rides as a watermark.

⭐ **The transferable half:** a `grep -c` naming the boards owed counts *mentions*, and a mention can be a read
rather than a lowering. Reading the one hit was the difference between "Prolog is owed a board" and "Prolog
cannot reach this node" — and here the read still reached the node, through a constant two files away.
