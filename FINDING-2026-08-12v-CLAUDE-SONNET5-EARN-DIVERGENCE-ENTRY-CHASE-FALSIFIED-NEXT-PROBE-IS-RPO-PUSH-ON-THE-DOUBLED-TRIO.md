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

## (5) Addendum, same session: `roman.sno`'s divergence checked — same mechanism, not a different one

s48's finding characterized `roman.sno` as showing a "larger, non-doubling divergence touching
pattern-family ops including one classified kind (ASSIGN_COND)," distinct from `func_call`'s clean
doubling — flagged there as unconfirmed ("not re-checked this session"). Built a minimal repro mirroring
`roman.sno`'s shape (`DEFINE('ROMAN(N)T') ... RPOS(1) LEN(1) . T ... BREAK(',') . T ... REPLACE(ROMAN(N),
...) ...` called from a small `LOOP`, at `/tmp/roman_repro.sno`):

```
m4: 11 [EARN] lines
m3: 14 [EARN] lines -- the first 11 BYTE-IDENTICAL to m4, then the SAME LAST 3 lines (op=76,76,78 --
    LOOP's own IR_COERCE_NUMERIC/COERCE_NUMERIC/CMP_TEST) appended a second time
```

**This is the identical `func_call` mechanism**, not a different one: ROMAN's own pattern-matching body
(the first 8 `[EARN]` lines, covering the `RPOS`/`LEN`/`BREAK`/capture ops) is emitted once in both
modes — untouched. Only the calling `LOOP`'s own tail duplicates, exactly as it does for the
pattern-free `func_call` repro. Two readings possible, not distinguished by this check: (a) s48's
original characterization was of the FULL 100k-iteration `roman.sno` (not run here — too slow for a
quick check, and unnecessary to reproduce the mechanism), which may have additional structure (deeper
recursion, more capture sites) that surfaces a genuinely different, second divergence on top of this
one; or (b) the "ASSIGN_COND touching" description was itself an artifact of a differently-shaped probe
and the mechanism really is uniform across all 11 files. **Recommend whoever picks up the `RPO_PUSH`
probe in (4) verify against the FULL `roman.sno` (or at least a repro with a real recursive call, which
this minimal version — `ROMAN('17')` called twice, no actual recursion since '17' is 2 digits and only
recurses once — does not exercise) before assuming one fix closes all 11 files.** Not chased further
this session — bounded, cheap check as flagged, and it returned a useful negative result (same
mechanism) rather than the still-open root cause.

## (6) Same session, continued: attempted a fix, it was empirically WRONG, reverted before commit

Followed through on (4)'s own recommended probe. Dumped INC's own full `proc_flat` node collection via
gdb (break at the post-pass-2 `alloca` line, conditioned on `prefix`, printing every `nodes[i]` — op,
pointer, `γ`, `ω`): **n=43** — INC's own 7-node body (`[0..6]`, ending at `[6]` = `IR_SAVE_RESTORE`,
confirmed role=1/RETURN via `nd->ival`, matching `zd_sr_role`) followed immediately by **36 more nodes
that are structurally almost the entire rest of `main`'s program** — `DEFINE`'s own tail statement,
`R=0`, `N=0`, the full `LOOP` statement (including the doubled `IR_COERCE_NUMERIC`×2/`IR_CMP_TEST`
trio), `R=INC(R)`, `DONE`, and two trailing `IR_GOTO`s. This is a **much larger over-collection than
just "LOOP doubles"** — INC's own dedicated walk structurally collects almost everything after it in
program order, but only the LOOP-tail's `[EARN]`-visible portion happens to matter for the observable
symptom (m4's SN4-M34-5a group-root guard independently prevents the *visible* consequence — duplicate
`.s` labels — by a narrower, different mechanism than whatever is happening at collection time here).

**Hypothesis formed:** `RPO_PUSH_SUCCS`'s FIRST line pushes `(c)->γ.node` UNCONDITIONALLY for every
node, no op-guard (`emit.cpp:2284`). Node `[6]`, the `IR_SAVE_RESTORE` RETURN-floater, has a live,
non-null `γ.node`. Reasoned: RETURN/FRETURN floaters terminate a proc's control flow via their own
generated jump at runtime, never a structural fall-through — so chasing this edge during a walk rooted
at a DIFFERENT proc's own entry looked like exactly the mechanism, and a natural fix by analogy to how
`IR_SUCCEED`/`IR_FAIL` are already excluded from further walking in `RPO_DRAIN`.

**Implemented, in one line + a long comment:** skip pushing `γ.node` when `(c)->op == IR_SAVE_RESTORE
&& (zd_sr_role(c) == 1 || zd_sr_role(c) == 2)`. Built clean.

**Tested empirically before trusting it — and it changed NOTHING.** Both repros still showed the exact
same doubling (`func_call`-shape: still 6 `[EARN]` lines; `roman`-shape: still 14). Re-ran the gdb node
dump: **still n=43, unchanged.** Chased node `[6]`'s own `γ.node` directly: it resolves to `IR_SUCCEED`
with BOTH `γ.node` and `ω.node` null — **already a dead end that `RPO_DRAIN` skips on its own** (the
existing `c->op == IR_SUCCEED || c->op == IR_FAIL` continue, a few lines below `RPO_PUSH_SUCCS`). Node
`[6]`'s `γ` was never the live path at all — pushing it and then immediately discarding it on drain is a
no-op either way. **The hypothesis is FALSIFIED by direct measurement, not just by re-reading code.**
`IR_SAVE_RESTORE`'s `ω.node` isn't pushed by any existing rule either (checked — not in either op-list
at emit.cpp:2293/2294), so neither of node `[6]`'s own edges explains nodes `[7..42]`.

**Reverted immediately** (`git checkout -- src/emitter/emit.cpp`) rather than commit code that doesn't
do what it claims — empirically verified against the repro before trusting it, exactly per this project's
own MONITOR-FIRST law ("the hunt is mechanical," not a plausible-looking patch shipped on reasoning
alone). Tree confirmed clean, rebuild green.

**Where this actually leaves the search:** nodes `[7..42]` are NOT reached via node `[6]`'s own edges.
They must enter the walk through some OTHER node's edge — either earlier in `[0..5]` (INC's own N+1
computation: `STATEMENT_BEGIN`/`VAR`/`LIT_INTEGER`/`BINOP`/`ASSIGN`/`STATEMENT_END`, none of which
obviously reach outside INC's own body on inspection, but none individually verified by measurement the
way node `[6]` now has been) or through the `SN4-M34-5a` group-root pull-in guard (`emit.cpp:2325`ish)
that s49 believed was inert for this program (`zls_group_mark_anchor` zero callers) but which **this
session did not independently re-verify** — worth a direct check (print `_gc` at that guard, don't trust
the prior session's claim secondhand) before ruling it out a second time. That guard remains the single
most concrete named candidate left unmeasured.

## State at handoff

SCRIP: tree clean. Started the session at `5547de99` == `origin/main` (s49's "not pushed" cursor note
was stale — already synced, nothing owed). **Mid-session, origin advanced to `3ed6dc90`** (a concurrent
seat's unrelated `MODE34-5b`/`SPAN(var)` landing) — caught via `git fetch` before this write-up,
fast-forwarded cleanly (`git pull --rebase`, no conflicts, since this session's own edit had already
been reverted), rebuilt green. Re-confirmed the bug still reproduces at the new HEAD (unrelated commit,
as expected — still 6 `[EARN]` lines / doubled, same as at `5547de99`). Repo now at `3ed6dc90` ==
`origin/main`, clean. **No code changes landed this session** — the one fix attempt (5) was reverted
after empirical testing showed it didn't work; only this finding + the goal-file cursor move are new.

**Next, no strong pull recorded:** (a) directly re-verify the `SN4-M34-5a` group-root guard's `_gc`
value for this program (print it, don't trust a prior session's secondhand claim a third time) — now
the single most concrete unmeasured candidate; (b) if that's also inert, fall back to (4)'s original
`RPO_PUSH` instrumentation across ALL of `[0..5]`'s edges, not just `[6]`'s; (c) EARN-4 (ARBNO from
scratch) remains open and likely still the highest-leverage EARN rung, gated on a session assessed as
full-runway at the start, per the goal file's own law; (d) `roman`'s divergence was checked this session
(part 5 above) and shares `func_call`'s mechanism, not a distinct one, though only against a minimal
non-recursive repro — the full 100k-iteration benchmark file was not re-verified.
