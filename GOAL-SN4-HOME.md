# GOAL-SN4-HOME — SNOBOL4 ALL THE WAY HOME (master orchestrator)

**⛔⭐⭐⭐ CHARTER (Lon in-chat 2026-08-12 s30, verbatim in substance):** *"This is the final stretch. Make RUNGS and STEPS to take SNOBOL4 all the way HOME, i.e. 100% working with RSP stack relative and RBP stack relative and RBX GC heap-top relative. Use multiple Opus sessions concurrently. Rearrange EVERYTHING."*

**THE EMISSION KEY (Lon, same session, verbatim in substance):** *"A BB will EITHER access its operand's RESULT and its own LOCALS via RBP, OR via RSP."* Per-BB binary, decided at plan time by `frame_need_of` (EARN-1), emitted only by `x86_alpha`/`x86_omega` (s29 ruling: RBP is never glue work). The reading-edge sharpening keeps ALT/CAT on the RSP side even with `*P` operands.

This file is the MAP. Seats execute their own seat file (below); cursors live in seat files; this file's phase table moves only at phase boundaries. All prior laws bind (RULES.md · MONITOR-FIRST · TEMPLATE-ONLY · BOTH-MEDIUM · LIVE CURSOR discipline · one clone per seat · `git config --local`, never global).

## REGISTER CONTRACT OF RECORD (the HOME state)

| reg | role | authority |
|---|---|---|
| RSP | FORTH spine: box operands, ζ cells, choice/resume records — compile-time-constant offsets always | ZETA-MECH ONE-SYSTEM + LIFO law |
| RBP | EARNED frames ONLY (LAW: cell↔RSP distance non-constant at a reading site); ONE ENTER at α; `[rbp+ANCHOR]` chain to MATCH_BEGIN; α/ω SOLE writer; callee-saved ⇒ free across C | `GOAL-RBP-EARN.md` LAW + s28/s29/s30 rulings |
| RBX | GC heap-top / allocation frontier: inline bump-alloc in emitted code; GC honors rbx as frontier; today's DESCR mint pointer, formalized | `GOAL-SN4-HOME-RBX.md` |
| R12 | capture-pending arena TOP (mmap'd, STACK discipline — Lon s30b: *"Capture pending are in their own MMAP'd R12-topped arena"*); restored at backtrack re-entry (oracle pin W5); GC-visible | RBP-EARN s30b + EARN-5 (ONE AUTHORITY vs ζ-cell arm) |
| R10 / R11 | rΓ / rΩ wires, BOTH glue kinds, one product-wide convention; per-activation template-emitted saves; preserved or veneered at every C crossing | `GOAL-SN4-HOME-WIRES.md` (absorbs LADDER WREG + PT) |
| R9 | GVA base (RTCC LIVE claim) | GOAL-RTCC |
| R8 + arg tier (rax rcx rdx rsi rdi) | RTCC slots; arg tier: claim it or stop paying for it (RC-8b) | GOAL-RTCC RC-8, GC gap owned by HOME-RBX X-1 |

## HOME GATE — Definition of DONE (every line measurable; "100%" means THIS)

1. probe suite · crosscheck/patterns · xc318 · broad-336 · demo board (honest denominator — fence-dupe fixed) · bench-22: **oracle-green BY SET, BOTH modes, m3 ≡ m4 outputs byte-identical**; xfail only where oracle-blessed (p.123 stack-overflow class, `-s` remedy).
2. EARN-2 census: **`unearned == 0 && owed == 0`**; emitted frame count == classifier output exactly.
3. Gates strict: claim gate DATA-DRIVEN over {rbx r9 r10 r11 r12 + tiers}; **zero r10/r11 scratch anywhere incl. RTX hand asm**; RC-8a GC coverage green; TEMPLATE-ONLY + BOTH-MEDIUM greps == 0.
4. Deletions complete: BLOB-GRANT pins · CLASS-D `{res,rbp}` records + res stubs + ω absolute unwind + scanfail whack · legacy ARBNO arm · every dead killswitch.
5. Monitor sees the classes it has been dark on: stdout-only divergence (MON-CAP) + table-element-assign VALUE events. `handoff_status.sh` prints COMPLETE.

## PHASES (‖ = concurrent seats; serialization points are DELIBERATE)

- **P0 — BASELINE (BOARD seat, solo, opens immediately):** m4 harness repair → floors re-proved BOTH modes at ONE hash → EARN-2 census re-cut to UNEARNED/OWED (⛔ standing law: BEFORE any frame-moving rung; also settles 557-vs-263) → discriminating refs (the 10 unclearable + polarity siblings) → claim gate data+strict. **Output = the floors every later seat judges BY SET against.**
- **P1 — ‖ FOUR SEATS (disjoint file surfaces):** **RBP** (GOAL-RBP-EARN): MONITOR-FIRST on `earn0_disc_arbno_star_fence_positive` → EARN-1 dormant → EARN-3 anchor → EARN-4 ARBNO-from-scratch (discharges ruling (c) by execution; witnesses N22–N33 + arb1 T1/T2 + 151) ‖ **LOWER** (HOME-LOWER): Defect A → B → C-9 residuals → 061 ‖ **WIRES** (HOME-WIRES): claim sweep incl. asm → ZCTX r10/r11 scratch eradication → guard unification → WREG mechanism DORMANT ‖ **RBX** (HOME-RBX): contract → RC-8a → FUNC-11 allocation instrumentation → fix.
- **P2 — ‖ THREE SEATS:** **RBP**: EARN-5 (ONE AUTHORITY: ζ-cell vs arena; W1–W5 acceptance) + EARN-6 (MATCH_BEGIN/FENCE conditional; FENCE(P) row classified) ‖ **WIRES**: PROC-shim delete (PT) + **WREG FLIP — ⛔ REQUIRES EARN-1 + EARN-3 LANDED** (EARN-10 ordering: pass-thru with zero frame is only correct once needy constructs earned theirs; the old 19-SEGV+7-HANG residual is EXPECTED cured — measure, never assume) + RTCC re-entrant preservation + default-ON revalidated (kill the m4-130 class) ‖ **RBX**: inline bump-alloc arms + ZHP-exhaustion re-check post Defect B.
- **P3 — SERIAL, one seat at a time, FULL RUNWAY each (a half-flipped sole authority is a broken tree by construction):** EARN-11 α/ω sole-RBP-writer flip (dormant byte-identical → per-node arming) → EARN-7 residue sweep (CLASS-D scaffolding, BLOB-GRANT pins, legacy ARBNO remnants) → LADDER AB call path (`fn_cell` jmp; RTX call asm) → EARN-8 STATEMENT/FUNCTION re-exam (ruling (d) becomes DECIDABLE here, with EARN-7 measurements in hand).
- **P4 — SEAL:** full-suite sweep · killswitch deletion · regen ×N · census seal · FINDINGs · handoff per FACT RULE.

## SEATS

| seat | file | absorbs / owns |
|---|---|---|
| RBP | `GOAL-RBP-EARN.md` (existing — the EARN ladder IS the plan) | EARN-0..11, ARBNO, FENCE rows, 151, D12/D13 recursion class |
| LOWER | `GOAL-SN4-HOME-LOWER.md` | s29 Defects A/B, CLIMB C-9 residuals, 061, test_string |
| WIRES | `GOAL-SN4-HOME-WIRES.md` | LADDER WREG + LADDER PT (from RBP-EARN, by reference), MECH M-1c guards, RTCC wire half |
| RBX | `GOAL-SN4-HOME-RBX.md` | rbx contract, RC-8a, RTX-FUNC-11, inline alloc, arena GC visibility |
| BOARD | `GOAL-SN4-HOME-BOARD.md` | EARN-2 census, floors, refs/witness hygiene, gates, m4 harness, MON-CAP. **ZERO compiler bytes ever** — collision-free by construction |

Legacy goals (SNOBOL4-BB · SNOBOL4-RTX · RTCC · ZETA-MECH · ZETA-CLIMB) remain HISTORY + law authority; their open SNOBOL4 items are absorbed above; their Icon/Prolog scope is untouched.

## COLLISION PINS (named in advance — this is why the partition works)

- **`emit.cpp` frame arms:** RBP seat lands EARN-1/3/4 there; WIRES must NOT cut those arms before P3/EARN-11 — the s12 "highest collision surface" note is now an ORDERING LAW.
- **Arena record layout (+16B wire-pair slot, WREG-3):** WIRES OWNS the layout; RBP/EARN-5 CONSUMES. One authority — the CAP-SYM lesson.
- **`x86_asm.h`:** encoder ADDS only (TEMPLATE-ONLY law); any seat may add, none may reshape.
- **RTCC veneer ↔ wires:** safe config = RTCC-ON **AND** wire capture/restore — neither alone (s14 arbitration). WIRES owns the pair.
- **Floors/census:** ONLY BOARD re-cuts instruments; every other seat consumes and cites.

## ⭐ LIVE CURSOR — 2026-08-12 s30 (Fable 5, minted with the plan)
P0 UNOPENED. First seat: BOARD. Fingerprints at mint: SCRIP `fc5b0754` · corpus `5c17de98`+witnesses · x64 `5035571`. Ruling ledger: (a) RULED s30/s30b (arena stands) · (b) OPEN, zero-cost · (c) discharged by EARN-4 execution when P1-RBP runs it · (d) decidable at P3.
