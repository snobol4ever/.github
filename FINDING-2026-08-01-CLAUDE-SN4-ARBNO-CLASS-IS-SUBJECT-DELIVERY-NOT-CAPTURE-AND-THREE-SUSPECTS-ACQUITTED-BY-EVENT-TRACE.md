# FINDING 2026-08-01 — SN4: the "arbno capture" class is SUBJECT DELIVERY, and three suspects were acquitted by event trace

**Session:** s22x continuation. **Witness:** `052_pat_arbno` (`X = 'aaa'; X POS(0) ARBNO('a') . V RPOS(0)` → prints empty, oracle `aaa`, rc=0 both modes).

## The falsification chain (each suspect acquitted by measurement, not reading)

1. **Suspect: capture entry never closed.** gdb at `rt_dcap_end_ok_open`: ONE entry `{V, saved_delta=0, len=0}` — looked like a stale first append. Entry contract confirmed against `rt_dcap_e {varname, saved_delta, len}` (pattern_match.c:642).
2. **Suspect: arbno re-yield bypasses the capture.** Breakpoint trace on `n12_match_assign_cond_α/β`: **1 APPEND (start=0, delta=0), 0 RETRACTs.** But the emitted topology is CORRECT — `arbno_as` re-yields through `n12_α` (052.s:381), `n12_β` retracts and chains to `arbno_β`, and `n9_match_rpos`'s fail edge targets `n12_β`. Topology acquitted.
3. **Suspect: RPOS emitted with POS semantics.** `n9_match_rpos_α` is exact: `r14 == r15 - arg`. Acquitted.
4. **The tell:** breakpoint at rpos printed **`r14=0 r15=0`** — the subject LENGTH register Δ is ZERO. Every observed behavior is then honest: 0-rep yield appends `{V,0,0}`, RPOS(0) legitimately PASSES on an empty subject at cursor 0, release closes V=''.
5. **Root cause localized:** breakpoint at `rt_match_enter` — the head handed it `rdi=0x401125` (a CODE address as the DESCR value word), `rsi=<stack addr>`. The head's legacy `!subjc()` flat-slot subject read (`FRQ(op_sa)/(op_sa+8)`) fetched garbage. **This is the s22s producer/consumer regime split on the SUBJECT: the subject producer's store and the head's read disagree on the DESCR's location under the declined+UCLAIM regime.**

## What this retires and what it opens

- The s22x cursor's remaining-fail decomposition line (a) "arbno/alt capture-start" is **WRONG as labeled** — corrected to **SUBJECT-DELIVERY class**. The dcap machinery (append/retract balance, entry contract, pump walk) and the arbno yield topology are verified LIVE-CORRECT and need no work.
- The fix surface is the SUBJECT-CELL rung s22s already named: `subjc()` (registered subject producer leaves the DESCR at TOS, head pops it) — whose PRODUCER-side gate was UNLOCATED at s22s. Locating that gate is the rung; the consumer arm already exists in `bb_match_head`.
- The CAS-MARKER-CARRY landing (`b016019d`) is UNTOUCHED by this finding: 041/042/047 fixes stand (their subjects deliver correctly; their defect was the release depth, now depth-free).

## Instrument notes

- gdb `commands` blocks DIE at an execution command: `stepi` inside `commands` silently terminates the list — break AFTER the instruction of interest instead.
- Greek-letter symbols (`n12_..._α`) do not resolve as gdb `break` operands in batch mode — `nm | grep -a` for the address, `break *0x...`.
- The event-trace ladder (append/retract counts + register values at the check boxes) bracketed in FOUR breakpoints what three sessions of static reading mislabeled. MONITOR-FIRST's bracket theorem applies to register-state divergence too: the first register that disagrees with the oracle's model (r15=0 vs 3) IS the divergence event.
