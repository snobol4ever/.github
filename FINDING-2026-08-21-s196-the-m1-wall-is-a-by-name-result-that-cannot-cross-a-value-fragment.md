# FINDING s196 — THE M1 WALL IS A BY-NAME RESULT THAT CANNOT CROSS A VALUE-FRAGMENT BOUNDARY
**HQ (Fable 5), 2026-08-21 s196. SCRIP HEAD carries the receipts; every claim below was measured this session with the P1 monitor, the P2 ZSM, and gdb software watchpoints.**

## THE ONE-SENTENCE WALL
beauty's `&`-built reduce actions compile to `epsilon . *EXPR$<thunk>` where the thunk's expression is `Reduce(...)` — an **NRETURN-by-name call** — and SCRIP's EXPR$ fragments are **VALUE-typed**: the fragment's emitted rvalue marshalling structurally dereferences the by-name result (DT_N → value), so the strict capture guard (s191's oracle law — SPITBOL retreats when a capture target resolves to a VALUE) correctly refuses the corpse, `rc=1` rides to MATCH_END's strict stub, ω, `Parse Error`.

## HOW DEEP THE AGREEMENT GOES (the P1 monitor's receipt)
With the two new controller knobs (`MONITOR_SKIP_CALL_RETURN=1` — scrip's SCC road has no CALL/RETURN taps yet; `MONITOR_SKIP_VALUE_NAMES=dummy` — scrip's NRETURN-name commit emits no VALUE yet), the shipped road agrees with `sbl -bf` for **2,089 consecutive events** on the six-character witness: the whole grammar build, token classification (`tx` events payload-identical), Shift/Push/tree/Reduce, `TopCounter=1`, `nTop=1`, PopCounter's NRETURN — **everything observable matches, and the match VERDICT alone inverts** (SPL → stno 1081 = success; scrip → 1083 = mainErr1). Divergence chronology as the instrument gaps were peeled: 1035 (missing CALL taps) → 1911 (missing dummy VALUE) → **2090 (the verdict)**.

## THE WANT-NAME WRITE LEDGER (gdb `watch -l rt_g_want_name`)
1. The dcap pump arms want and calls the thunk; `rt_proc_call_open` **banks-and-zeroes** (by design — its epilogue would reapply, but the dyn/jmp-entry road never runs that epilogue).
2. **The architecture already knew**: the fragment's own emitted code re-arms want via the `SNO$WANTNM` builtin before its tail call — the tail's consult (`rt_nret_fix`, wn=1) **KEEPS the name** (measured: `r.v=DT_N r.s=dummy → KEEP-NAME`).
3. The kept DT_N then dies in the fragment's **value marshalling** — emitted rvalue reads deref it. Not `rt_nret_fix` (its deref was removed experimentally and the value still arrived deref'd; the removal also turned `m1_nret_value` red — rvalue NRETURN requires that deref — REVERTED, falsified as a cure).
4. At the pump: `by_name=0, nm.v=DT_S` (`"1"`, `""` — deref'd values) → `[DCAP] STRICT-REFUSE` ×2 (`*EXPR$206F7`, `*EXPR$204F6`) → `[DCAP] MATCH_END rc=1 -> OMEGA`.

## FOUR LIFO-DISCIPLINE REPAIRS LANDED ON THE WAY (each green-preserving; battery: nret 3/3 + the standing `m1_nret_cap` lower-refuse, ptc spot 5/5, captures 7/7, fw 7/7, smoke 7/7 both modes)
- `rt_ret_faildescr` no longer destroys the **caller's** outstanding want (a failing call returns no name; zeroing `by_name` is right, obliterating the outer want was not).
- `rt_ab_leave_env` restores the banked want **on the FAIL road too** (it skipped the restore entirely — a failing callee permanently killed its caller's want).
- The dcap pump's and `c_rt_cap_open`'s `'*'` arms **save/restore** want (nested want contexts) instead of set/zero.
- `rt_nret_fix_tiny` **restores** the live want instead of hard-zeroing it after every non-kept consult; `rt_call_proc_descr` republishes the caller's want across the generic-entry road.

## ⛔ FALSIFIED THIS SESSION — do not re-spend
- Deref removal in `rt_nret_fix` (breaks rvalue NRETURN, and the deref that kills the name is EMITTED anyway).
- The want-lifecycle repairs alone (necessary hygiene, not sufficient — the name dies structurally in the value protocol).
- Standalone reconstruction, attempts five and six (`dfail.sno` failing-deferred-conjunct green; depth-2 stored-capture green) — the carrier is the EVAL-built fragment, per the four prior falsifications.

## ⭐ THE CURE RUNG (`m1-byname-through-fragment`), SPECIFIED
Capture-target thunks must yield **by name**. The fragment compiler knows the `. *X` / `$ *X` context at build time (the same context flags that ride `dtp`/recipe construction). Either:
(a) compile capture-target fragments with a **by-name result protocol** — the tail consult keeps DT_N, the marshalling skips the rvalue deref for the fragment's RESULT (interior rvalues unaffected), and the by-name flag rides out of the fragment to the pump; or
(b) the pump evaluates a capture-target thunk's underlying tail call **directly** with want-name (unwrapping one level of the recipe), bypassing the value protocol.
(a) is the architecture-true cure (ONE protocol, no special-case caller). DONE-WHEN: the six-character witness `' X = 1'` is oracle-identical both modes; `board_beauty_m1.sh --modes both` first-red moves past 40; the nret/capture/fw/ptc batteries stay green; corpus fail-set no worse by name; killswitch; FINDING.

## ALSO BANKED THIS SESSION (separate facts, same hunt)
- The "non-SCC road crash" decomposed: the ZSM-bloat abort is a **flat-buffer capacity limit** (`SCRIP_FLAT_BUF_MB` added); the remaining SEGV is a wild jump inside a JIT blob on the by-name entry road at depth (row `nonscc-road-beauty-segv` stands, repro `SCRIP_M3_GVA=0` / `SCRIP_SCC_OFF=1`).
- The "spine leak" theory died properly: statement-entry depth excursions RETURN to baseline (function-body statements legitimately run at call depth); the constant baseline-16 is the chain's entry pair, a ZSM-AEXP calibration note.
- SPITBOL's bridge emits VALUE events for NRETURN-name commits and for immediate captures in stored patterns; scrip's equivalents are tap-gaps rows (`scc-road-call-taps`, plus the NRETURN-commit VALUE tap).
