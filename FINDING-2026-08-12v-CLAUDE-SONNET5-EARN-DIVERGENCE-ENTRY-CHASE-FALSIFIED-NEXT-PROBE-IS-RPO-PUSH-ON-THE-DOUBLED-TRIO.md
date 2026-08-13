# FINDING — 2026-08-12v (Claude Sonnet 5, SOLO) — Picked up s49's 11-file `[EARN]` divergence. Reproduced exactly (same node identities, same two call sites). One new candidate mechanism (an `entry` parameter "mismatch" between `emit_chain` and `codegen_flat_chain_body`) investigated and FALSIFIED — it is documented HQ-s26 entry-chase behavior, not a bug. Root cause still open; concrete next probe identified.

## Session scope note, recorded up front

This session declined to open EARN-4 (ARBNO from scratch) despite s49 flagging it as likely
highest-leverage. Reason: `GOAL-RBP-EARN.md`'s own RUNWAY law — *"EARN-4 and EARN-7 are full-runway
only — the fix loop is the cost center and a half-landed frame regime at end-of-context is a broken
tree by construction"* — and this session's context budget was not assessed as full-runway at the
point of picking work. Took the other NEXT option instead: root-causing the 11-file divergence, which
s48/s49 both left as "narrowed enough it's probably fast." It was not fast — recorded honestly below —
and this session also stopped short of a full root-cause for the same reason (context budget), rather
than pushing into a long single-session debug loop on a bug that is not itself gating EARN-2's numbers.

## (1) Reproduced exactly, tooling confirmed

Built the identical minimal repro s49 used (`DEFINE('INC(N)') ... LOOP N=LT(N,5) N+1 :F(DONE) ...
R=INC(R) :(LOOP) ...`), saved at `/tmp/inc_repro.sno` (not committed — trivially reconstructible from
this file). `install_system_packages.sh` run first, gdb 15.1 confirmed live, build green.

```
SCRIP_EARN_DIAG=1 ./scrip --compile /tmp/inc_repro.sno   -> 3 [EARN] lines
SCRIP_EARN_DIAG=1 ./scrip --run     /tmp/inc_repro.sno   -> 6 [EARN] lines (the same 3, doubled verbatim)
```

Temporarily enriched the `[EARN]` print (`bb_op_name`, `bb_node_id`, raw pointer) to confirm node
identity — **same `nid`/pointer both times**, exactly as s49's `SCRIP_ZPROBE` trace found:
`op=76(IR_COERCE_NUMERIC)`, `op=76(IR_COERCE_NUMERIC)`, `op=78(IR_CMP_TEST)`, same three pointers,
same order, twice. **Reverted before this write-up** — `git status`/`git diff` empty, clean rebuild
verified (see State at handoff).

## (2) gdb call-site confirmation — matches s49 exactly, no new call sites

`break bb_prepare if nd->op == 78` (had to `set breakpoint pending on` — `bb_prepare` lives in
`libscrip_rt.so`, not loaded at gdb start; same class of gotcha `REPO-SCRIP.md` already documents for
`rt_*` symbols, worth noting it applies to non-`rt_`-prefixed emitter symbols too since `emit.cpp`
compiles into the same `.so`). Two hits, both on the CMP_TEST node's identical pointer:

```
Hit 1: emit_chain(entry=0x4310b0, out=0x0, prefix="proc_flat") <- scrip.c:1603 (INC's own proc loop)
Hit 2: emit_chain(entry=0x4327d0, out=0x0, prefix="pat_flat")  <- scrip.c:1634 (main)
```

Identical to s49's finding. No new information here — confirms the bug is still live, unchanged, at
this HEAD (`5547de99`).

## (3) New candidate investigated and FALSIFIED: the entry-parameter "mismatch"

Printed `entry` explicitly at both frames for Hit 1:

```
frame 5 (emit_chain):            entry = 0x4310b0
frame 4 (codegen_flat_chain_body): entry = 0x432820
```

These differ despite `emit_chain` calling `codegen_flat_chain_body(entry, prefix)` as a direct,
non-recursive, single-level call (`bt full` confirms exactly one frame of each function — no
recursion, no second emit_chain in the stack). Looked like a promising lead — a place where the two
functions could disagree about which node "entry" names.

**Falsified by inspection of `codegen_flat_chain_body`'s own body, line 2251:**

```c
{ int guard = 0; while (entry && (entry->op == IR_SUCCEED || entry->op == IR_FAIL || entry->op == IR_GOTO)
  && entry->γ.node && guard++ < CH_MAX) entry = entry->γ.node; }
```

documented (HQ s26 comment, same line) as: *"a chain bound at a label-landing goto (LBL__ pseudo-procs)
binds α at the landing's TARGET, so the gate box is never collected and its `sub rsp` / trampoline
never emit."* `codegen_flat_chain_body` reassigns its OWN local copy of `entry` by design, chasing
through transparent relay nodes before the real walk starts. `0x4310b0` is `LBL__INC`'s raw pseudo-proc
entry (a relay node); `0x432820` is the chased target the RPO walk actually starts from. **This is
correct, load-bearing, pre-existing behavior, not the doubling mechanism.** Recorded so nobody re-chases
this exact lead — it looks exactly like a bug from the `bt` output alone until you read line 2251.

## (4) Where this leaves the mechanism — unresolved, but narrower

What's now established, cumulative with s48/s49:
- The doubling is two *independent* top-level RPO walks (`codegen_flat_chain_body` called once from
  each of the two `emit_chain` sites above), each with its own fresh `seen[]`/`sn` visited-set
  (confirmed: `static IR_t *postv[CH_MAX]; int pn = 0; static const IR_t *seen[CH_MAX]; int sn = 0;`
  are declared inside `codegen_flat_chain_body`, `pn`/`sn` reset to 0 every call — there is no
  cross-call membership test other than the `SN4-M34-5a` group-root guard, which s49 already showed
  has zero live callers for this program shape).
- `IR_RETURN`'s own γ-edge is unpopulated for this program (s49, ruled out).
- The `IR_BINOP`/coerce/`CMP_TEST` ω-edge push (`RPO_PUSH_SUCCS`, emit.cpp:2296) is walked identically
  by both modes and isn't where m3/m4 diverge (s49, ruled out).
- The entry-chase discrepancy is legitimate HQ-s26 behavior, not the mechanism (this session, ruled out).
- **Not yet checked:** which specific edge inside `RPO_PUSH_SUCCS`, fired from INC's OWN walk (starting
  at the chased `0x432820`), pushes the first LOOP-owned node. The walk is a two-phase iterative DFS
  (`RPO_PUSH`/`RPO_DRAIN`/`RPO_FLUSH`, emit.cpp:2276-2331) — the concrete next probe is a conditional
  breakpoint or print INSIDE the `RPO_PUSH` macro itself (not `bb_prepare`, which only sees nodes AFTER
  they're already collected into `nodes[]`), conditioned on the pushed pointer being one of the three
  doubled node addresses (capture them fresh each run — pointers are heap addresses, not stable across
  runs), printing `c` (the caller node whose edge triggered the push) each time. That directly names
  which edge and which source node is responsible, instead of continuing to falsify candidates one at
  a time from static reading. **`RPO_PUSH` is a macro, not a function — breaking on it requires either
  a line breakpoint at each of its ~9 expansion sites in `RPO_PUSH_SUCCS`, or temporarily promoting it
  to a real function for one session's debugging** (revert after, same discipline as this session's own
  temp edit).

## Impact assessment — unchanged from s48/s49

Zero impact on EARN-2's OWED/UNEARNED (m4-exclusive). Real mode-3 codegen bug, not GOAL-RBP-EARN's own
— same routing judgment as before. Not chased to a fix this session.

## State at handoff

SCRIP: tree clean, HEAD `5547de99` == `origin/main` (already fully synced — the s49 cursor's "not
pushed, holding for credential" note was stale by the time this session started; `git fetch` + `git log
origin/main..HEAD` confirmed empty, nothing owed). This session's only edit (`emit.cpp`'s `[EARN]`
print, temporary) was reverted before this write-up; `git status`/`git diff` both empty, rebuild green.
**Nothing new committed this session except this finding + the goal-file cursor update below** — no
code changes, since none landed.

**Next, no strong pull recorded:** (a) the `RPO_PUSH` instrumentation probe described in (4) — likely
the fastest remaining path to a real root-cause; (b) EARN-4 (ARBNO from scratch) remains open and
likely still the highest-leverage EARN rung, gated on a session assessed as full-runway at the start,
per the goal file's own law; (c) `roman`'s non-doubling pattern-bearing divergence (s48 finding 3b)
was never re-checked against whether it shares this mechanism or is unrelated — worth a quick check
before assuming one fix covers all 11 files.
