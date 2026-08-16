# FINDING 2026-08-16 (Claude Fable 5, s166) — PROLOG MULTI-CLAUSE ROOT CAUSE: γ-RELEASE USE-AFTER-FREE; PL-Z-1a OPT-IN RETAIN ARM; R-0h INSTRUMENT LANDED

Measured at SCRIP `c2ce75b1` (HEAD), fresh clone, clean `-O0` build, gdb 15.1, all probes this session.

## 1. THE DEFECT (R-0's clause/recursion witnesses, root-caused)
Probe matrix (m3 `--run`; m4 twin-verified on p2/p3/p6):
| probe | shape | result |
|---|---|---|
| p1 | single-clause `f(a).` call | PASS `a` |
| p2 | two-clause, first solution only | rc=0, **blank line** (binding lost) |
| p3 | two-clause + fail-driven | **rc=139, rip=0x1** (m4: hang rc=124) |
| p4 | recursion `c(0). c(N):-...` | rc=0, wrong output (silent) |
| p5 | inline disjunction in main | PASS |
| p6 | member/2 backtrack | rc=139 |

Chain, each link read from emitted `/tmp/p2.s` at HEAD and gdb:
1. Multi-clause predicate ⇒ `flat_gen=1` zframe graph. Prologue IS established (FN__ face: `sub rsp,384`; γ/ω wires at `[kt-24]/[kt-16]`; own base at `[kt-8]`; `rt_jmp_frame_lexprep2`). Entry verified through the face (gdb break FN__f$2F1, hit from `n28_call_proc_staged_β`).
2. `n4_suspend_α` pushes a CP via `rt_pl_cp_push3(..., &n4_suspend_β)` — resume address INTO this activation; resume slot `[rsp+320]`.
3. `f$2F1_γ` normal-exit arm (xa_flat_zframe_epilogue_γ_str, PL-FR-4 arm, after the pending-cursor intercept) executes **`add rsp,kt` — RELEASING the activation the CP points into**.
4. Caller continues; its `write()`/libc PLT calls run below rsp and shred the released frame. Even the FIRST solution's clause-head bindings lived there ⇒ p2's blank.
5. On `fail`, backtrack re-anchors into the freed frame (`f$2F1_res: add rsp,8; pop rsp`) and jumps through a shredded cell ⇒ `rip=0x1`.

This is the exact Prolog twin of Icon's Z-3 defect fixed at HEAD for `icn_cells` only (`c2ce75b1` "gamma is suspend, not return"), under the same LIFO CONTRACT (Lon s242): **α carves, ω tears down, γ RETAINS.**

## 2. PL-Z-1a LANDED — γ-RETAIN ARM, OPT-IN `SCRIP_PL_GAMMA_RETAIN=1`, DEFAULT BYTE-IDENTICAL
`src/templates/xa_flat.cpp` PL-FR-4 normal γ-exit: retain = `mov rax,rsp` (hand base to caller's landing, ICN-FR-5/Z-3 protocol), no unwind; release arm preserved verbatim under default. OFF-arm byte-identity: p1.s/p2.s diff EMPTY. ON-arm diff is exactly one instruction (`add rsp,384` → `mov rax,rsp`).

**Why default OFF (measured, not hedged):** the caller side is compiled for the release regime.
- Caller γ landing `.Lx40_3: mov [rsp+232],rsp` under retain writes callee-base−160 = the **callee's own slot 232**, and every subsequent caller cell ref drifts by kt+8. Probes ON: p2 blank→SEGV, p4 0→139 (divergence moved to the named caller handshake — the Icon slice-2-second-half state, on purpose).
- Prolog's OUTER main is `flat_jmp_entry=1` (driver wire-jmp entry) so that conjunct cannot scope it out; under ON its γ exits `exit@PLT` kt-deep ⇒ libc fault after correct output (p5 ok→rc139). A terminal-top-graph exclusion is part of the enabling pair.

## 3. PL-Z-2 SPEC (the enabling slice for default-ON; = R-3's first concrete rung)
ζ-ACTIVATION anchor per the THREE-ZETAS tier-2 (Lon, in-chat this session): callers of retaining callees have compile-time-unknown rsp depth ⇒ they need a depth-immune base.
Sites (~5, coordinated): (a) zframe prologue: save caller's rbp in the header (reconcile with `[kt-8]` currently holding own-base) + pin rbp=own base post-carve; (b) γ-retain arm: unchanged (hands base in rax); (c) caller staged-call γ/β landings: re-anchor `mov rsp,rbp`(−staticΔ) before any cell ref; (d) `$res` backtrack path: after `pop rsp`, restore rbp=own base; (e) ω epilogue: restore caller rbp from header before releasing kt. Retained frames form the CP stack, freed LIFO by backtrack-ω — FORTH-style non-popping spine. Beware the PL-FR-4 s14 class (inner-predicate β-resume contamination; per-frame sentinel). Terminal top-graph keeps release-at-γ.

## 4. R-0h LANDED — THE INSTRUMENT CAN NO LONGER HIDE THIS CLASS
`scripts/test_prolog_bb_honest.sh` silently dropped every program whose ORACLE run crashed (`[ $ir_rc -ne 0 ] && continue`) — the mechanism behind every recent "FAIL=0" while rung10 SIGSEGV'd on screen. Landed: `ORACLE_CRASH=N` counted, printed, and **gating the exit code**; PASS/FAIL/ABORT semantics untouched (honesty-vs-walker bucket kept distinct from engine crashes). Falsified by injection both directions (planted crasher ⇒ ORACLE_CRASH=1 exit=1; planted passer ⇒ PASS=1).
**Honest board at HEAD: PASS=106 FAIL=0 ABORT=0 ORACLE_CRASH=79.** The 79 are R-0's real backlog; the clause/recursion smoke witnesses are members of the §1 class.

## 5. CANARIES AT DEFAULT (post-change)
Prolog smoke 3/5 (unchanged pre-existing red) · Icon smoke 14/14 m3 + 14/14 m4 · all-langs hello 6/6 ROWS_DRIFT=0 · OFF-arm .s byte-identity p1/p2. Non-Prolog identical by construction (arm is inside the Prolog-zframe-gen-only branch) and verified by the above.
