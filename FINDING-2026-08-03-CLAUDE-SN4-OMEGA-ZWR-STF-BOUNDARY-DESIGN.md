# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-ZWR-STF-BOUNDARY-DESIGN: mechanism-2 boundary must be at statement head; STF-leave/MATCH_END-whack interaction design

**Session:** s37 tail (2026-08-03, Sonnet). **SCRIP HEAD:** `fa007877` (Lon's mechanism-2 infra).

## The problem

`SCRIP_ZW_RB=1` alone (Lon's `fa007877`): m3 238/63F/16T, m4 317 LERR. The `op_zw2` arm in `bb_match_begin.cpp` emits `push rbp; mov rbp, rsp` **inside MATCH_BEGIN** which fires after the VAR cell (`sub rsp, 16`) is already allocated. So the whack `mov rsp, rbp; pop rbp` in MATCH_END unwinds to post-VAR rsp, not statement-entry rsp. The VAR cell leaks; m4 LERR because the depth accounting is inconsistent across LERR locations.

## The required fix (three-part)

**Part 1 — STF admits flat_pat=1 graphs under ZW_RB (emit.cpp line 2859).**

Change:
```c
g_emit.flat_stmt_frame = ((_stf && !g_emit.flat_jmp_entry && !g_emit.flat_pat && ...))
```
to:
```c
int _stf_pat = (_stf && zw_rb_on() && !g_emit.flat_jmp_entry && g_emit.flat_pat && ...);
g_emit.flat_stmt_frame = ((_stf && !g_emit.flat_jmp_entry && !g_emit.flat_pat && ...) || _stf_pat) ? emit_stmt_frame_scan(...) : 0;
```
Gate `_stf_pat` on `zw_rb_on()` so it only fires for mechanism-2 sessions, and keep the existing `!flat_pat` path unchanged (degrade never die for SCRIP_STMT_FRAME=0 sessions).

**Part 2 — MATCH_BEGIN op_zw2 arm removes its own push; uses FRQ spellings.**

The STF bracket (`bb_glue_framed_enter`) already fired at statement-entry: `push rbp; mov rbp, rsp; sub rsp, 8`. rbp is now at statement-entry rsp. MATCH_BEGIN's op_zw2 arm must NOT do another push. Replace:
```
x86("push", "rbp") + x86("mov", "rbp", "rsp")
+ ... [rbp + 8 + off] spellings ...
```
with FRQ spellings (identical to op_zw arm). The housekeeping slots (HKN 1-4, rsp_mark, start_δ) already have correct FRQ offsets since rbp=statement-entry-rsp and FRQ = [rbp + op_off + N].

**Part 3 — Depth model: remove the +8 at hpos for zwr (emit.cpp line 2031).**

```c
if (zwr && r == hpos) zd += 8;   // REMOVE THIS
```
The 8B push happens at statement-entry via STF glue (outside zd_plan's accounting), not inside the chain. The -8 at MATCH_END (line 2028: `zd -= 8`) stays — it accounts for the pop rbp in MATCH_END's whack.

**Part 4 — STF framed_leave must not fire when op_zw2 is the mechanism-2 run's whack.**

The STF bracket fires `bb_glue_framed_leave` at statement γ/ω. For mechanism-2 runs, MATCH_END already called `mov rsp, rbp; pop rbp` mid-statement, restoring rsp to statement-entry and popping rbp. If STF's leave fires again at statement exit, it would execute a second `pop rbp` against a restored rsp — double pop.

The correct behavior: MATCH_END's whack IS the mechanism-2 equivalent of the STF bracket's leave. At statement γ/ω exit, rsp is already at statement-entry level (MATCH_END restored it) and op_zgpop releases the value-spine cells above. The STF leave must be suppressed.

Implementation: in `bb_glue_framed.cpp` `bb_glue_framed_leave()`, add a guard `IF(!_.op_zw2, ...)` — when op_zw2 is staged on the statement terminal, suppress the leave. The staging for op_zw2 on the terminal node comes from the chain's last ZD-armed terminal reading the run head's `zzwr` flag via the UCLAIM staging path (same as how op_zw is propagated to the statement terminal via zzw → op_zw at choke).

## Measurement needed

Once Parts 1-4 land (behind SCRIP_ZW_RB=1, SCRIP_STMT_FRAME=1): run ZWR diag on 060_capture_multiple and 044_pat_pos. Check that the emitted .s has FRQ spellings consistent (no +8-shifted slots). Full 318×2 gate. Expected: the 73 blob-clause programs arm correctly; op_zgpop still releases value-spine cells above the match claim; bench 18/21 hold.

## Key invariant (per Lon's HQ ruling)

The mechanism-2 whack must land rsp at statement-entry level (pre-all-cells). STF bracket at statement head (push rbp before VAR sub rsp,16) + MATCH_END whack mid-statement (mov rsp,rbp; pop rbp) achieves this. The STF leave at statement exit is then a no-op (rsp already correct, op_zgpop handles the value-spine release).
