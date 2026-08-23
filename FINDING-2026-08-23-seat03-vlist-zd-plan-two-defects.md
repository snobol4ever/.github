# FINDING 2026-08-23 (seat03) — row `vlist-expr-alternation`: the lowering already landed, the real blocker is `zd_plan`, and it splits into TWO distinct emitter defects, not one

## HEADLINE

The row's brief ("lower_snobol4.c has NO TT_VLIST CASE") describes a state that no longer exists on this tree. `TT_VLIST` **is** lowered, correctly, as a value alternation (commit `b7d88465`, landed earlier today, default OFF behind `SCRIP_VLIST_ALT`). The row's real content is the emitter bug that commit's own comment names but does not fix: `zd_plan` (`src/emitter/emit.cpp:2388`) cannot place an arm that is reachable only through an ω edge mid-expression. That is **one** defect. Arming the lowering and empirically testing all four `corpus/probe/vlist/*.sno` witnesses in both modes surfaces a **second**, distinct defect once the first is patched: arms of differing internal cost reconverge on a shared successor at different static depths, and nothing reconciles them. Both must close before this row is done.

## EVIDENCE 1 — arm 2+ is never claimed, confirmed with `SCRIP_ZD_DIAG=1`

`vl_alt_nested_cat.sno`, statement 2 (`OUTPUT = 'in-cat [' 'A[' (IDENT(x) 0, 7) ']' ']'`), compiled `--compile` armed:

```
[ZD] h=5 r=6  i=11 IR_ASSIGN     K=0  zout=80
[ZD] h=5 r=7  i=14 IR_VAR        K=16 zout=96   <-- i=12, i=13 never appear in ANY [ZD] line, in ANY hi run
```

`i=12` and `i=13` are arm 2 (`7` and its own synthetic `ASSIGN`, from `lower_snobol4.c`'s `for (i = n-1; i >= 0; i--) { asn = IR_ASSIGN(jn, ω); head = sx_lower(c[i], asn, nxt, &vr); nxt = head; }`). `asn`'s own `.γ` is wired straight to `jn` (the shared temp-var read) — so the ordinary γ-walk from arm 1 reaches `jn` **without ever visiting arm 2**, because arm 2 is only reachable by *failing* arm 1 (an ω edge, not a γ edge). `zd_plan`'s run-walker (`emit.cpp:2405-2412`) only ever starts a new run at `hi==0` or a `bb_src_of` statement head, and only ever advances via `cur = zd_chase(cur->γ.node)`. Arm 2 is neither a statement head nor γ-reachable from anything claimed, so it never gets `zon=1`, and whatever the emitter falls back to for an unplanned node collides with live cells (`vl_alt_nested_cat.sno`'s own comment already recorded `[rsp+320]` inside an 80-byte frame from an earlier session's asm read; the diagnostic trace above is the same fact from the planner's own side, not the asm).

This is structurally identical to what `DESIGN-SN4-ZD5B-BRANCHING-RUN-PROPOSAL.md` (s23t) solved for `IR_MATCH_ALTERNATE`: a box's alternatives aren't reachable via the plain γ-chain, so the planner needs a subtree-descent arm that gives each alternative its own depth model, seeded from a shared base. ZD5B shipped and is live (`SCRIP_ZD_5B`, default on, `emit.cpp:2413-2428`) — but it is keyed to `env->op == IR_MATCH_ALTERNATE` walking `operands[]` arm pairs. VLIST has no such host node; the arm boundary is encoded purely in per-node `.ω` wiring produced by ordinary `sx_lower` recursion, with no structural marker at all.

## EVIDENCE 2 — a prototype extension fixes the crash, not the values

Patch (this session, `emit.cpp` only, no lowering change, no new global — see diff below): after the existing ZD5B arm-collection block, do the same thing for any claimed node whose `.ω` lands on an unclaimed, non-statement-head node still present in `nodes[]` — walk its γ-chain into the run, tag it via the existing `zarm[]`/`aent[]` mechanism, seeded (chained, for 3+-arm lists) from `zarm[i0]>=0 ? zarm[i0] : i0`. One follow-on one-line change was required: `arm_zd = zout[zarm[i]]` → `arm_zd = zout[zarm[i]] - zd_k(nodes[zarm[i]])`, because VLIST's seed node (an ordinary `IR_IDENT`/`IR_CALL`, K=16) is not a K=0 router the way `IR_MATCH_ALTERNATE`'s host is — the old formula was silently relying on the host always costing zero. **This one-line change is a proven no-op for the existing MATCH_ALTERNATE path** (`zd_k(host) == 0` always, per the ZD5B design doc's own §2: "The ALTERNATE node itself carries K=0" — so `zout[host] - 0 == zout[host]`, byte-identical).

Gated behind its own flag, `SCRIP_ZD_VLIST_OMEGA` (default OFF, on top of `SCRIP_VLIST_ALT` which is also default OFF — both must be set explicitly to reach this code; see EVIDENCE 2b for why I tightened this from an initial default-on).

Result, armed, both modes, all four probes:

| witness | before this patch | after this patch |
|---|---|---|
| `vl_alt_first_ok` | PASS/PASS | PASS/PASS (unchanged) |
| `vl_alt_second` | PASS/PASS | PASS/PASS (unchanged — this witness never touched the bug; see EVIDENCE 3) |
| `vl_alt_nested_cat` | m3 wrong values, m4 **SIGSEGV rc=139, reliably** | m3 wrong values (different!), m4 wrong values OR SIGSEGV, **non-deterministically** — see EVIDENCE 2b |
| `vlist_expr_alternation` | m3 partial, m4 clean `Error 164` rc=1 | m3 partial (different), m4 SIGSEGV or wrong values, non-deterministically |

`vl_alt_nested_cat`'s in-cat line, on the runs where it doesn't crash, goes from a crash to `7]]` where the oracle says `A[7]]` — the `'in-cat ['` and `'A['` prefixes, both live on the cell-stack *before* the VLIST even starts, are gone. That is EVIDENCE 3.

## EVIDENCE 2b — the patch does not reliably fix the crash; it makes the wild write's outcome environment-dependent, which is worse

I initially read `vl_alt_nested_cat.sno`'s m4 SIGSEGV going away as the patch fixing something. It does not — checked by holding the **compiled binary constant** and varying nothing but the runtime environment:

```
same binary, unpatched (b7d88465, no changes):
  no extra env vars set    -> SIGSEGV, rc=139        (3/3 runs)
  SCRIP_VLIST_ALT=1 set    -> SIGSEGV, rc=139        (3/3 runs)  <- inert flag, compile-time only, yet changes nothing: reliably wild
  86-byte unrelated padding var set -> SIGSEGV, rc=139  (3/3 runs)

same binary, WITH this session's prototype patch:
  no extra env vars set                        -> rc=0, wrong values   (multiple runs)
  SCRIP_VLIST_ALT=1 + SCRIP_ZD_VLIST_OMEGA=1 set (compile-time-only flags, should be runtime-inert)
                                                -> SIGSEGV, rc=139, 100% reproducible (3/3 runs)
```

Both binaries are executing the *same emitted code* every time in each row (I am not recompiling between runs) — only the process's environment-variable block, hence its initial stack-pointer address, differs. A memory access whose crash/no-crash status flips based on incidental stack-address shifts of a few dozen bytes is, by definition, an out-of-bounds/wild write, not a clean logic error with a clean fix. **The unpatched build's wild write is far enough out of bounds that it is insensitive to this — it crashes regardless.** The patched build's wild write is evidently *closer* to a valid page boundary, making it environment-sensitive: some layouts crash, others let it silently write into whatever happens to be mapped there. **This is a worse safety profile than the status quo, not a better one** — a reliable crash is honest; an environment-dependent silent corruption is exactly the failure class this row exists to eliminate. I do not know, and did not try to determine, whether the patched build's non-crashing runs are writing into memory that happens to be harmless scratch space or something that matters — either way, relying on that is not something to ship.

This also means EVIDENCE 2's earlier table entries showing "rc=0" for the patched build were true of *that one process launch*, not of the patch — a different shell, a different `PWD` string length, a different set of exported variables, all shift outcome. I flagged this to HQ as soon as I found it (superseding my earlier same-session report that the patch "kills the SIGSEGV").

## EVIDENCE 3 — the second, distinct defect: arm-length convergence

`vl_alt_second.sno` (`z = (IDENT(x) 0, 7)`) already passes armed **today, with no patch at all** — it is the only witness s193 (2026-08-20) recorded as "already green when armed." The reason: it is the last thing in its statement. `jn` (the VLIST's shared temp-var read) is followed immediately by `IR_STATEMENT_END`, which releases *everything* back to zero unconditionally — it does not need to know which arm ran, only that the statement is over. Nothing downstream needs a **specific** depth for `jn`, only "eventually zero," so an accidentally-mismatched arm cost is invisible.

`vl_alt_nested_cat.sno`'s in-cat case is not last: `jn` is read as one piece of a larger concatenation, and whatever assembles the final string reads the earlier pieces (`'in-cat ['`, `'A['`) via a **static, compile-time offset** computed from a point before the VLIST. Arm 1 (`IDENT(x)` + `0`, K=16+16) and arm 2 (`7`, K=16) cost different amounts. Both must reach `jn` at the identical accumulated depth for that static offset to mean the same thing regardless of which arm actually ran — and nothing currently makes that true. `IR_MATCH_ALTERNATE` doesn't have this problem because (per the ZD5B design doc §5) a successful arm releases its own cells back to the shared base *before* proceeding to the shared success glue (`na_s`) — the convergence point is reached at a *known, arm-independent* depth by construction. VLIST's lowering has no equivalent release-before-rejoin: `asn_i`'s γ just goes straight to `jn`, at whatever depth that specific arm happened to accumulate.

This is a real, general problem, not specific to this one witness: **any** VLIST embedded in a larger expression, with arms of differing internal node cost, needs it. It does not show up in `vl_alt_second` (nothing after `jn` in the same statement) and would not show up in any VLIST whose arms happen to cost the same K by coincidence — which is presumably part of why it went unnoticed until now.

This is also the most likely explanation for EVIDENCE 2b's non-determinism: Defect A's fix gives arm 2 a real, planned offset instead of whatever fallback an entirely-unplanned node gets — but Defect B means that offset is *systematically off by roughly one arm's worth of K* (16-32 bytes) from what the shared successor expects, not off by an arbitrary/uninitialized amount. A near-miss lands in-bounds on some stack layouts and out-of-bounds on others; a wild, unplanned offset is far enough away to miss reliably either way. I have not independently proven this is the exact mechanism (I did not instrument the specific faulting address), but it is consistent with every measurement in EVIDENCE 2b and EVIDENCE 3 together, and it is the reason Defect A's fix alone was never going to be sufficient even before I found the crash was flaky.

## WHAT WOULD ACTUALLY CLOSE THIS

Two candidate mechanisms, in the DESIGN doc (`DESIGN-SN4-ZD-VLIST-ARM-REENTRY.md`, filed alongside this FINDING): pad every arm to the max K-cost across all arms of one alternation (computable during the discovery pre-pass, since `zd_k()` is a pure function of op kind — no depth-loop dependency), or make the release-before-rejoin explicit (each arm's own last node gets a real `zgpop`-driven release down to the shared base before its γ reaches `jn`, mirroring MATCH_ALTERNATE's na_s behavior). Both need a "which nodes belong to arm 1" answer, which today only exists implicitly (arm 1 is unmarked, ordinary run nodes) — either mechanism has to also retroactively identify arm 1's own extent, not just arms 2+, which the current prototype does not attempt. I did not implement either: the risk of shipping a *plausible-looking but subtly wrong* depth reconciliation, given how dense and semantically under-documented `zd_plan`'s existing arithmetic already is (`zwpop`/`zgpop`/`zout` have no comments explaining their consumer contract; I reconstructed the consumer at `emit.cpp:2995` empirically, not from any written spec), is exactly the "silent wrong values" failure mode this row's own brief warns is worse than the current safe "statement fails."

## SCOPE NOTE ON THE PROTOTYPE ITSELF (EVIDENCE 2's patch)

The seeding formula (`zarm[new_arm_first] = zarm[i0]>=0 ? zarm[i0] : i0`) is only proven correct when the node whose `.ω` discovers the next arm is the **first** node of its own arm — true for every witness in this row (treebank's real usage, `IDENT(a(x)) 0`, and all `probe/vlist/*.sno` arms: single leading predicate, then a value). An arm shaped like `foo() IDENT(x) 0` where **both** `foo()` and `IDENT(x)` can genuinely fail, and `foo()` is first, would seed from `IDENT(x)`'s own local zwpop rather than the true pre-arm depth, under-releasing `foo()`'s cell. Not exercised by anything in this corpus today (confirmed by the full corpus board, see RECEIPTS); flagged here rather than silently assumed away.

## CURRENT STATE / WHAT I DID NOT DO

- `SCRIP_VLIST_ALT` stays default OFF. Nothing about default `scrip --run`/`--compile` behavior changed.
- `demo_treebank` is still RED — the row is NOT closed, its `.ref` is untouched (still the weak `matched bytes=327` pin HQ flagged; re-minting it is pointless before the construct is actually correct — a re-mint now would just pin a DIFFERENT wrong answer).
- The `emit.cpp` prototype (EVIDENCE 2) is committed, but gated behind its **own** flag (`SCRIP_ZD_VLIST_OMEGA`, default OFF) layered on top of `SCRIP_VLIST_ALT` (also default OFF) — reaching it requires opting into both explicitly. This is deliberately more conservative than a single shared gate: per EVIDENCE 2b, the prototype does not reliably improve on the unpatched behavior, so `SCRIP_VLIST_ALT=1` alone (already-documented, reliably-crashing behavior) is left completely undisturbed for anyone who reaches for it. The prototype is a tested, evidence-backed step toward closing Defect A, kept available for the next session rather than discarded, but it is explicitly **not** a fix and must not be read as one.

## RECEIPTS

SCRIP `ce48e3bb` pristine, corpus `d3e5abfe` pristine (pulled/rebased mid-session after HQ's baseline correction; `make pristine`, `RT_OPT` default `-O0`, zero `-O1`/`-O2` in the build log) + this session's `emit.cpp` prototype on top, style-conformant (no explanatory comment in code — RULES.md's C-style section is absolute; this doc and the DESIGN doc carry the rationale instead). `SCRIP_ZD_DIAG=1` traces for `vl_alt_second.sno` and `vl_alt_nested_cat.sno`, both armed, `--compile`. Probe results: all four `corpus/probe/vlist/*.sno` witnesses, both modes, with and without the prototype. EVIDENCE 2b's determinism check: same compiled binary (unpatched and patched), repeated runs, varying only the runtime environment-variable set — `< /dev/null` on every run throughout. Full corpus board (`bash scripts/scorecard_snobol4.sh run --jobs 4`, all 12 suites, 1952 scored rows, wall 9m54s) at `ce48e3bb`/`d3e5abfe` with the prototype uncommitted-but-built-in, `SCRIP_VLIST_ALT`/`SCRIP_ZD_VLIST_OMEGA` unset (default): `demo_treebank` still `RC1`/`RC1` (the expected red, unchanged), all four `probe/vlist/*.sno` witnesses show exactly the expected default-off pattern (`vl_alt_first_ok` PASS/PASS, `vl_alt_nested_cat`+`vl_alt_second` DIFF/DIFF, `vlist_expr_alternation` RC1/RC1 — no crashes, nothing SIG-anything), zero surprises anywhere I could find. One change from HQ's `1f281ace` fail-set-by-name: `160_pat_alt_inner_gen_resume` now PASS/PASS (re-verified in isolation, not a fluke) — unrelated to this row, presumably from the `sno_alt_tail` default flip that landed in the same pull range (`lower_snobol4.c`, `ce48e3bb`'s history), not from anything in this session's patch. Full results: `test-results/scorecard-seat03-vlist-ce48e3bb/`.
