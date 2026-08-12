# FINDING — D12 SEGV root cause: `bb_match_arbno()`'s live dispatcher has exactly two arms (FRAMELESS_K,
# gated on a real "sequence-only" body check, and plain FRAMELESS, gated on NOTHING) — any ARBNO body that
# fails the K16 sequence-only check (e.g. contains a deferred/recursive pattern reference) falls through to
# the unguarded plain-frameless arm even though that arm's own correctness comment requires a K0 body it
# was never checked for. D13's hang is the same shape, unconfirmed.
#
# ⛔ CORRECTION (same session, later pass): an earlier draft of this finding blamed `zd_k()`'s K=0 handling
# of IR_MATCH_DEFER directly. That was wrong — `zd_k()`'s DEFER clause is already narrow (pat_static +
# PATV$-prefix only) and correctly returns 16, not 0, for `*LIST`. Runtime diagnostic (SCRIP_ARBNO_DIAG=1)
# confirms `op_arbno_body_k0=0` (correctly declined) yet the arm selected is still plain FRAMELESS — so the
# bug is NOT in the K0/K16 classifiers' arithmetic, it's in the template dispatcher never consulting
# `op_arbno_body_k0` at all on the path that matters. See ROOT CAUSE section below for the corrected trace;
# the METHOD section's gdb work is unaffected and still the true mechanism of the crash.

**Author:** Claude Sonnet 5 · **Date:** 2026-08-12 (continuation session) · **SCRIP head:** `825ab0a4`
**Rung:** GOAL-SN4-HOME-WIRES W-2 (live witnesses D12/D13) — this finding is diagnostic, not a landed fix.
**Status:** Root cause pinned mechanically (gdb software watchpoint + objdump on the real RX slab). No
code changed this pass. The fix requires a design decision (see END) that is arguably this seat's (W-4,
"arena wire-pair slot — THIS SEAT OWNS THE LAYOUT") but touches `zd_k`'s K=0 classification for
`IR_MATCH_DEFER`, which is shared, product-wide, ONE-AUTHORITY code — flagging rather than editing solo.

## Reproduction
```
corpus/probe/bb/probes/D12.sno  (subject '(12,(3,45,(6)),78)', pattern POS(0) *LIST RPOS(0))
corpus/probe/bb/probes/D13.sno  (subject '(12,(34)'          , same pattern — negative control)
./scrip --run D12.sno   →  rc=139 SIGSEGV
./scrip --run D13.sno   →  rc=124 timeout (hang)
```
Both are already-named members of the standing 5-REGRESSION set `{D12,D13,H31,X01,X10}` (s33/s35 by-set
floor). Nothing here is a new failure; this is the first hand-trace of D12's actual mechanism.

## Method (MONITOR-FIRST, then mechanical)
1. Ran `PARTICIPANTS="spl scr" test_monitor_3way_sync_step_auto.sh D12.sno` first. It diverged at step 6
   on `LIST = UNKNOWN` (spl) vs `PAT$1$V1 = PATTERN` (scr) — but the `<lval>`/`UNKNOWN` sentinel is a
   **documented bridge-side limitation** (`scripts/monitor/monitor_sync_bin.py:204-282`, "less
   informative... treat as wildcard"), not a real semantic divergence. Discarded as a false lead rather
   than chased — this is exactly the class the goal file's own INSTRUMENT RULE warns about.
2. Went to gdb on the real SIGSEGV instead (ground truth, no bridge involved).
3. `info proc mappings` at crash time located the real mode-3 RX code slab: `0x7ffff1600000–0x7ffff1603000`
   (3 pages, one per sealed graph — confirmed via `break bb_seal` in `libscrip_rt.so`, where the function
   actually lives; it is NOT linked into the `scrip` binary itself, which is why an unqualified `break
   bb_seal` before process start fails to resolve — needs `start` first so the .so is loaded).
4. Dumped each sealed graph's bytes pre-mprotect (`dump binary memory ... buf buf+size`) and
   `objdump -D -b binary -m i386:x86-64 --adjust-vma=<base>`, per the FINDING-2026-08-12j method.
5. Crash PC and r10/r11 at fault time: PC=`0x11f1600482` (unmapped garbage), r10=`0x7ffff160152c`,
   r11=`0x7ffff1601531` — both r10/r11 land inside the real RX slab and disassemble to plain trampoline
   stubs (`jmp <γ-landing>` / `jmp <ω-landing>`). r10/r11 are NOT the corrupted values.
6. Dumped the stack: the crash PC's *low* 32 bits (`f1600482`) exactly match a real, valid res-landing
   stub address (`0x7ffff1600482`, confirmed by disassembly: `mov r10,[rsp+8]; mov r11,[rsp+16]` — the
   CLASS-D res-landing idiom from `emit.cpp:2690`). Only the *high* 32 bits are wrong. This ruled out
   "truncated pointer" and pointed at "valid pointer, top half stomped" instead.
7. Software watchpoint (`watch *(int*)<fixed-addr>` — HW watchpoints confirmed non-functional in this
   container, matching RULES.md) on the corrupted slot's high half, run to the actual write:
   ```
   Breakpoint at src-mapped 0x...13fc (bb_match_arbno.cpp's PAIR(2) retry landing)
   Before: [rsp+0..7] = 0x00007ffff1600482   (a live, currently-needed CLASS-D res-landing address)
   After single-step:  0x00000009f1600482   (top half stomped with a small int — 9 here, 17/18/etc.
                                              elsewhere — these are r14d, the ARBNO instance counter)
   ```
   Confirmed twice independently (two separate runs, two separate corrupted slots, same write site both
   times: `bb_match_arbno.cpp` PAIR(2), compiled to `mov [rsp+4], r14d` at slab offset `+0x3fc`).

## Root cause (CORRECTED — see header note)
`src/templates/bb_match_arbno.cpp`'s live entry point is `bb_match_arbno()` (line 207), which per its own
"D-1 DELETE" comment supersedes the old TAIL/DT/NARY-CHAIN arms — "every ARBNO now rides the ARBNO-LON
frameless pair, which differ only in whether the body's staged ΣK is zero." Its actual dispatch (line
215) is:
```
return _.op_arbno_body_kk > 0
         ? bb_match_arbno_frameless_k()
     : _.op_off < 0
         ? x86_alpha() + x86_bomb(...)
     : (_.op_sa < 0 || _.op_sb <= 0)
         ? x86_alpha() + x86_bomb(...)
         : bb_match_arbno_frameless();          // <-- the ELSE, reached whenever kk==0
```
`op_arbno_body_kk` is reset to 0 for every node by default (`emit.cpp:1098`) and is raised above 0 by
exactly one site: the K16 prelude (`emit.cpp:955`), which requires `_sq` ("sequence-only") to be true —
`_sq` is set false if the ARBNO body contains ANY `IR_MATCH_ALTERNATE/ARBNO/FENCE1/DEFER/VALUE/CALL/
CALL_VALUE/DISJUNCTION/ABORT` node. D12's body (`',' ITEM`, where `ITEM = SPAN(...) | *LIST`) contains an
`IR_MATCH_DEFER` (`*LIST`), so `_sq=0`, the K16 prelude declines, `op_arbno_body_kk` stays 0 — and
`bb_match_arbno()`'s dispatch falls straight into `bb_match_arbno_frameless()`, **the plain K0 arm, with
no check of `op_arbno_body_k0` anywhere on this path.** That field is computed elsewhere (`emit.cpp:958`,
consumed only by a separate, now-dead legacy dispatcher earlier in the same file at lines ~310-330, no
longer reachable from `bb_match_arbno()`'s actual `return` — confirmed by a diagnostic print, `SCRIP_
ARBNO_DIAG=1`, which for D12 prints `k0=0` yet still selects arm `FRAMELESS`).

So the bug is structural, not arithmetic: **"not eligible for the K16 arm" is silently being treated as
"eligible for the plain K0 arm,"** with no actual verification that the plain arm's own stated
precondition — *"the frontier never moves inside the activation, so the cell is `[rsp+0]`/`[rsp+4]` from
EVERY site"* — holds. It doesn't hold here: `*LIST`'s own body can CLASS-D-suspend (nested ARBNO/`*LIST`
inside it), leaving a live 32-byte resume record on the stack, and the plain frameless arm's `[rsp+4]`
yield-cursor write (`bb_match_arbno.cpp:60/72/98/106`) lands on top of that record's high 32 bits instead
of its own cell — this half of the trace (the gdb watchpoint work, below) is unaffected by the correction
above and remains the confirmed mechanism of the actual crash.

`D12`'s pattern is exactly this shape: `ITEM = SPAN(...) | *LIST`, `LIST = '(' ITEM ARBNO(',' ITEM) ')'`
— the ARBNO body is `',' ITEM`, and `ITEM` contains `*LIST`, a self-referential deferred pattern. The
subject `'(12,(3,45,(6)),78)'` has enough nesting depth (three levels of parens) to force a `*LIST`
invocation whose own body suspends mid-match (its own inner ARBNO/ITEM), landing back through the outer
ARBNO's PAIR(2) with a live resume record underneath — the exact corruption traced above.

## Scope claim, precisely

### ⛔ SECOND CORRECTION (same session, third pass) — a blanket k0==0 fix WOULD REGRESS 16 PROGRAMS

Before proposing a patch, I swept every ARBNO-bearing probe in `corpus/probe/bb/probes/` with
`SCRIP_ARBNO_DIAG=1` and cross-referenced against actual pass/fail (fixed a shell script bug in my first
pass at this — multi-line output broke a `[ ]` string comparison and silently mis-reported everything as
FAIL; re-ran with `diff`, which is the only trustworthy result below). **19 probes hit the plain-frameless
arm with `op_arbno_body_k0=0`.** Of those, **16 currently PASS** (D09-D11, G19-G20, H21, H24-H25, N12,
N17, X02-X06, X11) and only **D12 (crash), D13 (hang), X01 (wrong-output, already a named 5-REGRESSION
member)** actually fail. So `op_arbno_body_k0==0` is NOT sufficient to predict a crash — the plain
frameless arm is safe for MOST k0=0 bodies in practice, and any fix that bombs or reroutes on `k0==0`
alone would break the 16 currently-passing programs to fix (at most) 3.

**The real discriminator, found by diffing D09 (passes) against D12 (crashes):** D09's ARBNO body is
`*P` where `P = LEN(1)` — a deferred reference to a pattern that can NEVER suspend (LEN is synchronous).
D12's ARBNO body is `',' ITEM` where `ITEM = SPAN(...) | *LIST` — a plain variable reference whose
STORED PATTERN VALUE transitively contains a self-recursive `*LIST`, which CAN suspend. The IR node
inside the ARBNO body in both cases is (almost certainly — not yet confirmed via a direct IR dump,
time-boxed out this pass) an `IR_MATCH_DEFER`, and the codebase already computes exactly the right
per-node distinction: `nd->pat_static` (set at lower time, `lower_snobol4.c:1324`, via
`sno_name_static()` → `sno_pat_dfree(p,1,0)`, described in its own comment as "transitively defer-free —
the star buys late binding only, and cannot recurse"). D09's `*P` should read `pat_static=1`; D12's
implicit reference into `*LIST` (via `ITEM`) should read `pat_static=0`. I did NOT confirm this with a
direct IR/gdb dump this pass (ran out of session budget) — it is the necessary next check, not a landed
fact.

**Corrected fix shape:** narrow whatever check gets added (in either the K16 `_sq` prelude or a genuine
new third arm in `bb_match_arbno()`) to key off `pat_static` on the DEFER node specifically, not "contains
any DEFER." A blanket DEFER exclusion (my original candidate (c)) is now measured, not just suspected, to
be a regression risk — 16 real corpus programs ride the exact path a blanket fix would close off. This
raises the bar on how careful the eventual patch needs to be, and is why I did not attempt to land one
this session despite having pinpointed the mechanism.

This is a dispatcher gap in `bb_match_arbno()`'s live entry point, not a CLASS-D bug and not a
WREG/push-pop-guard bug (W-2 as literally written). It sits at the seam between two independently-correct
mechanisms:
- CLASS-D's contract (`_blob_wire`): suspend leaves a live record on the stack, by design, until β.
- ARBNO-FRAMELESS's contract: the body never moves `rsp`, by design — but that contract is a property of
  the BODY (`op_arbno_body_k0`, correctly computed as false here), and the live dispatcher never asks it.
The dispatcher's actual predicate is "is the body ALSO K16-sequence-eligible" (`op_arbno_body_kk > 0`),
which is a stricter, unrelated question (K16 additionally requires `_sq`, no ARBNO/DEFER/ALTERNATE/
FENCE1/VALUE/CALL/DISJUNCTION/ABORT anywhere in the body) — failing THAT test currently routes to the
plain frameless arm by omission, not because anyone verified the plain arm's own (weaker, K0-only)
precondition holds. It doesn't, for any body containing a suspend-capable DEFER.

## D13
Not individually traced this pass — same pattern, subject is a negative control (unbalanced parens,
`.ref` expects `=F`). The hang (rc=124 vs D12's rc=139) is consistent with the same corrupted-landing
mechanism manifesting as a wild jump into a retry loop that never reaches a terminating compare, rather
than an outright invalid-address jump — but this is a plausible reading of the symptom, not a traced
confirmation. Flagging as likely-same-class, not claiming it.

## What I did NOT do
- Did not patch `bb_match_arbno()`. The fix shape has at least three live candidates and I don't think
  this seat should pick blind:
  (a) add a real third branch: when `op_arbno_body_kk == 0` AND `op_arbno_body_k0` is ALSO false (the
      case this finding traces), fall through to the legacy chain arm — but that code now lives inside
      a function literally named `bb_match_arbno_DELETED_ARMS()` (confirmed zero external callers via
      grep), which is a much stronger "do not use this" signal than "unreachable but intact" suggested in
      an earlier pass of this finding. Reviving it is a bigger, separately-risky change, not a quick
      reroute — DEMOTED from "cheapest" to "not actually cheap, needs its own verification pass";
  (b) make ARBNO-FRAMELESS itself defensive — reserve extra headroom or re-derive its cell address
      relative to a stable anchor instead of raw `[rsp+N]`, which is closer to W-4's "arena wire-pair
      slot" territory and the RBP/EARN interaction already named in that rung;
  (c) ⛔ MEASURED, NOT JUST SUSPECTED, TO BE A REGRESSION RISK (see the second correction above): a
      blanket "any DEFER in the body declines" fix would break at least 16 currently-passing corpus
      probes (D09-D11, G19-G20, H21, H24-H25, N12, N17, X02-X06, X11) to fix at most 3 (D12, D13, X01).
      NOT viable as originally scoped. The narrower version — key off the DEFER node's own `pat_static`
      flag (already computed at lower time, already distinguishes "can recurse" from "cannot recurse" per
      its own header comment) rather than "contains any DEFER" — is the live candidate, but I did not
      confirm `pat_static`'s actual value on D12's ARBNO-body DEFER node this pass (would need a direct
      IR/gdb dump; ran out of session budget) and did not implement it blind.
  All three are the kind of "small widening or narrowing of an existing dispatcher" decision the W-0b
  policy note already flagged as needing an explicit call rather than a quiet default — (c) especially so,
  now that it has a measured blast radius rather than a guessed one.
- Did not re-run the full probe suite or check whether this same mechanism explains `dc_sib_bt`'s silent
  wrong-answer bug flagged last session — both are CLASS-D + recursive/deferred-pattern intersections, so
  it's a live suspicion, but I have not traced `dc_sib_bt` itself to confirm or rule it out.

## For the next seat
- The mechanical trace (gdb watchpoint on the corrupted stack slot, `SCRIP_ARBNO_DIAG=1` for the
  dispatcher verdict) is fully reproducible; re-run it to verify before trusting it further than "root
  cause located," per this session's own earlier INSTRUMENT RULE about verifying before publishing — this
  finding itself needed a correction pass mid-session for exactly that reason (first draft blamed `zd_k`'s
  DEFER K=0 directly; the diagnostic print showed that classifier was already correct, and the real gap
  was one level up, in the dispatcher choosing not to consult it). Trust the corrected Root Cause section,
  not the header's original title.
- `break bb_seal` needs the process started first (`start` before `break`, or `break` will silently no-op
  asking about a pending breakpoint) — `bb_seal` lives in `libscrip_rt.so`, not `scrip`. Costs a false
  start if forgotten; worth a line in RULES.md session-setup alongside the existing gdb/monitor guidance.
- `gdb` is not preinstalled in this container image; `apt-get install -y --no-install-recommends gdb`
  works (the recommended `libc6-dbg` companion package 404s from the security mirror — skip it, not
  needed for this kind of trace).
- `SCRIP_ARBNO_DIAG=1` is a fast, cheap way to see which arm a given ARBNO node actually routes through
  without gdb — use it BEFORE reading the dispatcher source by hand; it would have shortened this session's
  own mid-course correction.
- **Concrete next step, smallest first move:** confirm `nd->pat_static` for the `IR_MATCH_DEFER` node
  inside D12's ARBNO body (break in the lower or emit pipeline, print the field — should be a 5-minute
  check) before writing any patch. If it reads 0 there and 1 on D09's `*P` node as predicted, the fix is
  narrow and low-risk: teach the `_sq`/k0 scans to treat `pat_static==0` DEFER nodes as genuinely
  nonzero-K (they already do this correctly in `zd_k` for the PATV$-specific case — this would just widen
  the same idea to the general case) rather than adding a blanket DEFER exclusion.
- **Regression-checking recipe that worked well this pass, reusable:** `SCRIP_ARBNO_DIAG=1 ./scrip --run
  <probe>` for the dispatcher verdict, `diff <(./scrip --run <probe>) <probe>.ref` for ground truth (NOT
  a shell `[ "$a" == "$b" ]` string compare — multi-line output silently breaks that and every comparison
  reports FAIL; this cost one wasted round this session). Loop over `corpus/probe/bb/probes/*.sno` grepped
  for the construct in question before touching any classifier, to get a real blast-radius number instead
  of a guessed one.
