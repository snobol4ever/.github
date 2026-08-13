# FINDING — 2026-08-12u (s49, Claude Sonnet 5, SOLO) — EARN-3 declined for now (no attachment point yet). The 11-file m3/m4 `[EARN]` divergence (s48's item 3b) is narrowed to a concrete mechanism: a DEFINE'd proc's `"proc_flat"` emission walk in mode-3 crosses past its own body into the shared graph's next statements, re-walking nodes the main emission also visits.

## (0) EARN-3 (anchor propagation): declined this session, reason recorded so it isn't re-opened blind

EARN-3 as specified ("Fixed slot in every frame; enter copies parent; MATCH_BEGIN seeds") presumes
a live RBP-establishing ENTER/LEAVE to attach an anchor-copy step to. Checked before writing
anything: `x86_alpha()`/`x86_omega()` (x86_asm.h:681/686-687) are label-define/jump-to-omega
primitives from the existing ZW-1 carve mechanism — no `push rbp; mov rbp,rsp` ENTER exists
anywhere in the tree, and `bb_match_begin.cpp` runs an entirely different, pre-EARN legacy protocol
(`HKQ`/`HEAD-PIN`/`REPL-PIN`/`stfh`, heavily commented, load-bearing). EARN-4 (ARBNO rebuild) and
EARN-7 (residue sweep deleting the legacy pins) are the rungs that will actually build the new
frame; EARN-3 today could only be a dormant offset constant + unwired copy-helper — but guessing
the slot layout now risks baking in an assumption EARN-4 has to undo, for near-zero present value
(EARN-1's own dormant landing was 25 lines because it needed nothing else; an EARN-3 stub would be
guessing at a shape nothing yet consumes). Left for a session where EARN-4's frame layout is real.

## (1) The 11-file divergence: reproduced in seconds, root-caused to line-precision

Built a minimal pattern-free repro (`DEFINE('INC(N)') ... INC = N + 1 :(RETURN) ... LOOP N = LT(N,5)
N+1 :F(DONE) ... R = INC(R) :(LOOP) ...`), mirroring `func_call.sno`'s shape (s48 finding 3b named
this file as one of the pattern-free "clean doubling" cases). Confirmed immediately:

```
m4 (--compile): 3 [EARN] lines
m3 (--run):      6 [EARN] lines -- the same 3, doubled verbatim
```

**`SCRIP_ZPROBE=1` traced node identity, not just op counts.** The doubled region is one contiguous
~30-node subgraph (LOOP's body), visited by the *same* `IR_t*` node objects both times (identical
`nid`s in both passes) — ruling out "two copies of the IR" and pointing at "one graph, walked from
two different `emit_chain` calls."

**gdb confirmed the two call sites precisely** (`break walk_bb_node`, conditioned/continued to the
first shared node, `bt`):

```
Hit 1: emit_chain(entry=0x430fa0, prefix="proc_flat") <- scrip.c:1603 (the DEFINE/proc-table loop, compiling INC)
Hit 2: emit_chain(entry=0x432470, prefix="pat_flat")  <- scrip.c:1634 (compiling main)
```

Same `nd` (0x431c00) reachable from both. **This is not two unrelated emitters colliding — it is
the product's own documented design.** `scrip.c:923`'s comment names it: *"a shared-graph proc
(LBL__/DEFINE entry) must bind its α at proc_entry_node ... SN4-FLAT-PROC (s176): bb_proc_entry, NOT
->entry."* SNOBOL4 DEFINE'd procs and `main` share ONE physical IR graph (`s2->bbp.table[main_bb_idx]`)
by construction — `bb_proc_entry()` just returns a different starting node within that one graph, an
O(n)-total design explicitly chosen over per-proc graph duplication.

**The defect is a missing walk boundary, not the sharing itself.** `INC`'s own `"proc_flat"` walk
(traced independently, first ~19 ZPROBE lines before the doubled region starts) legitimately reaches
`INC`'s own `N + 1` arithmetic — then keeps going and reaches `LOOP`'s `LT(...)` comparison too,
despite `INC`'s body ending in `:(RETURN)`. `IR_RETURN` IS a real terminal control-transfer kind
(`emit_chain_arity`'s `case IR_RETURN: ... sp = 0; continue` at emit.cpp:2887, plus the identical
guard at line ~1437 in the earlier arity-sim pass) — so the walk should stop there. It doesn't, on
this program. Not yet isolated to a single line: either (a) `INC`'s own γ-chain doesn't actually
terminate cleanly at its `RETURN` node for this program shape, or (b) `codegen_flat_chain_body`'s
node-collection phase pulls in operand/ω-edge references that reach past the control-flow boundary
(the same shape `emit_chain_operand_refs`, emit.cpp:2847, uses elsewhere — a pure data-walk that
follows `.ω`/`.γ` edges without a kind-boundary check). **Ruled out, checked and eliminated before
spending more time on it:** the SN4-M34-5a group-root pull-in guard (emit.cpp:2325,
`!g_is_text || entry == g_emit_cfg->entry` — unconditionally true in binary/m3 vs. entry-gated in
text/m4, which looked like an exact match for "m3-only, m4-clean" doubling) is NOT the mechanism
here: `zls_group_mark_anchor` (the function that populates the registry that guard's loop reads) has
**zero callers anywhere in `src/`** — the loop's own `_gc` count is 0 for this program, so it cannot
be firing. A promising lead that didn't survive a direct check; recorded so the next seat doesn't
re-chase it.

**Why m4 doesn't show this:** m4's own proc-emission loop (scrip.c:882, inside the `if (out)` early-
return branch of `emit_chain`, line 3047) calls `codegen_flat_chain_body` exactly once per
`emit_chain` invocation and returns immediately — no `bb_ab_emit_nodes` posthook, no fall-through to
the binary-only tail (lines 3048-3070) that m3 always executes. The asymmetry between the `if (out)`
early return (text) and the fall-through path (binary) is the branch point where m3 and m4's
behavior for the SAME `emit_chain(bb_proc_entry(INC), ...)` call diverges — worth checking first in
any follow-up, alongside the RETURN-boundary question above.

## Impact assessment (unchanged from s48, now with a location instead of a hypothesis)

**Still zero impact on EARN-2's OWED/UNEARNED numbers** — computed from m4 exclusively, and m4
shows none of this. But this is a **real, mechanism-level bug in mode-3 codegen**, not ASLR noise
like s48's item 3a: a DEFINE'd proc's compiled code may include instructions belonging to unrelated
downstream main-chain statements, JIT'd twice into the sealed binary slab. Whether this produces
wrong *behavior* (as opposed to wasted bytes + duplicate diagnostic lines) was not checked this
session — the repro's actual program output (`result: 6`) was correct both times it ran, so if this
is silently benign today it is because the duplicated tail either re-executes idempotently or is
simply dead weight in the sealed blob and never reached at runtme via `INC`'s own fn pointer.
**Not verified either way — flagged, not chased further**, since this belongs to mode-3 codegen
correctness generally, not GOAL-RBP-EARN specifically (same routing judgment s48 made for item 3a).

## State at handoff of this finding

SCRIP: tree clean, back to the same 2-commits-ahead-of-`0954198b` state as s48 left it
(`e73f66b4`, `5547de99`) — the gdb/ZPROBE investigation used only existing `SCRIP_ZPROBE`/
`SCRIP_EARN_DIAG` instrumentation plus one temporary `walk_bb_node` edit (added `ret=%p` to the
existing ZPROBE print) that was reverted before this write-up; verified via `git status`/`git diff`
showing empty, and a clean rebuild. Nothing new committed this session. Not pushed — continuing the
s47/s48 pattern of holding the push/credential ask to session end, per this session's own instruction.

**Next, no strong pull recorded:** (a) finish this root-cause — check whether `INC`'s γ-chain fails
to terminate at `RETURN` on this graph shape, or whether the node-collection phase pulls operand/ω
references past it, using the same `walk_bb_node` return-address / gdb-conditional-breakpoint method
that got this far; (b) once root-caused, decide fix shape (bound the `proc_flat` walk at the proc's
own `RETURN`/`FRETURN`, most likely) and re-run the full 11-file list to confirm all of them share
this mechanism (the finding only traced `func_call`'s shape; `roman`'s non-doubling pattern-bearing
divergence from s48 may be a different or related mechanism — not re-checked this session); (c) EARN-4
(ARBNO from scratch) is likely the highest-leverage next EARN rung now that EARN-3 is blocked on it.
