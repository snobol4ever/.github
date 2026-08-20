# ARCH-PASSTHRU — THE ONE CROSSING LAW BETWEEN BB GRAPHS (Lon 2026-08-20 in-chat, PRIORITY ONE)

**Lon, verbatim in substance:** *"Get a reliable way to go between BB's. Each BB graph has TWO continuations. Moving between them should be simply a matter of switching these TWO and switching back as they move. … You have EVERY SINGLE BB have a RESULT, so that you are forced to put it somewhere, because when it is needed that will be a problem caught ahead of time. Now some BB results are in REGISTERS."*

## THE LAW
1. **TWO CONTINUATIONS, ONE DISCIPLINE.** Every BB graph's external contract is the pair {γ-continuation, ω-continuation} riding the r10/r11 wires. EVERY crossing between graphs = bank the caller's pair, install the callee-relative pair, run; the callee's γ/ω restore the banked pair. Nothing else may carry cross-graph linkage: no pushed landing pads, no flat depth assumptions leaking across the seam, no per-road glue.
2. **THE PAIR IS ACTIVATION STATE, NOT A CALL ARTIFACT.** Graphs suspend (γ) and are re-entered (β). Whatever holds the suspension holds the banked pair, and β re-entry reinstalls it — "switching back as they move" holds in BOTH directions. Existence proof already in-tree: the PAT$ blob head (`blob_frame_bytes`: saved rbp @+0, γ wire r10 @−8, ω wire r11 @−16).
3. **⛔ THE RESULT LAW (Lon 2026-08-20).** EVERY BB has a RESULT and a DECLARED HOME for it (a register or a cell named by the lattice) — declared at compile time, uniformly, so a consumer can never discover a missing result at runtime. The s174 operand-slot flat read (needle read resolving to caller territory inside an ALT arm) is the conviction: a result whose home was an assumption. Register-resident results are fine — the law is that the home is DECLARED, not that it is memory. Enforcement joins the ZDP lattice (the one per-box ζ-semantics authority, `zeta_depth.c`) and the ZDP/ZSM/canary instruments check declared-vs-actual.

## THE FOUR PROTOCOLS IN THE TREE TODAY (the disease, measured)
1. **Blob crossing** — CONFORMANT (banks the pair in its head; the model).
2. **Pushed-pair landing** (`bb_call_proc_staged` slim/legacy: `[rsp+0]=γ [rsp+8]=ω`) — B1c's root cause (s168), R1b's sibling (fragment thunk landing, s173).
3. **DTP record road** (DEFER β = `jmp qword ptr [rsp]`) — record-held continuation.
4. **TINY shim** — third call shape with its own admission/exits.
Every M1 wall on the 2026-08 board is a mismatch between these. The cure is ONE law, proven bottom-up — not eight seats curing faces.

## THE LADDER (Lon's order, exact; each level: witnesses FIRST, oracle-refed, both modes, 2–3 layers deep in EACH direction — γ forward through the layers AND β retreat back through them)
- **L1 — ZERO-LOCAL family:** `*PATTERN_VAR` and `PATTERN_FUNC()` returning **POS, RPOS, TAB, RTAB**. Why first: ZERO allocations — pure register machines, so any failure is the crossing itself, uncontaminated by ζ. (Note: today's templates spend a scratch cell for TAB/RTAB — semantically they need NONE; L1 surfaces that debt.)
- **L2 — ONE-LOCAL family:** same crossings for the one-cell boxes (SPAN/BREAK/BREAKX/REM …) after L1 is green.
- **L3 — ARB and BAL** join *PAT_var/PAT_func (extending-β generators — retry state crosses the seam).
- **L4 — ARBNO** (interior body, per-activation records).
- **L5 — FENCE1 and FENCE0** (cut semantics across graphs).
Witness home: `corpus/probe/passthru/` (`pt<level>_*`). Instruments: WIRE-ORDER canary (live r10/r11 vs staged wires at every port), ZDP every-port probe, ZSM lifecycle.

## STATUS
- 2026-08-20 HQ (Fable): file minted; L1 witness family + HEAD baseline census this session (see GOAL-SNOBOL4-100 cursor + FINDING when pushed). Delegation suspended — HQ executes.
