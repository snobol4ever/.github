# FINDING-2026-08-11-CLAUDE-SN46-WREG-BOARD-DEAD-MATCH-END-CLOBBERS-R10-AND-FENCE1-DEFER-HANG-MECHANISM

**Session:** Claude Sonnet 4.6 · SCRIP `a50e2ee` (board commit) · corpus `5da04e78` UNTOUCHED · `.github` this commit.
**Scope:** GOAL-PASSTHRU-RBP-ERAD WREG ladder — instrumentation repair + hang class root cause.

---

## 1. DEAD INSTRUMENT: `test_board_wreg_byset.sh`

**Finding:** The two-arm SCRIP_WREG board is VACUOUS. Commit `855a12a` physically deleted the SCRIP_WREG killswitch; it now survives only in two comments:
- `bb_match_defer.cpp:83`
- `bb_glue_flat.cpp:150`

Both arms run identical bytes. The script reports `REPAIRED 0 / BROKEN 0`, which reads as "neutral change" but means "the knob is disconnected." This is structurally equivalent to the REAPED-BUILD-FAKED failure class — a green board with no signal behind it silently launders every claim that follows.

**Fix landed:** `scripts/board_patterns_set.sh` (SCRIP `a50e2ee`) — set-based snap/diff, preserving the s17 law. SERIAL BY CONSTRUCTION: parallel execution misclassifies SEGV as HANG (measured: 178, 179 flip SIG11→HANG at -P 8 / 10s; confirmed serial at 30s).

**Baseline snapshot at HEAD:** PASS 76 · SIG11 28 · DIFF 12 · HANG 6. Matches W-MAP3 commit claim exactly.

---

## 2. HEAD COMMIT SELF-REPORTS ARE HONEST

W-MAP3's claimed numbers (PASS 73→76, HANG 12→6, SEGV 26→28) reproduce exactly at serial 30s timeout. The discrepancy between parallel (26 SIG11 / 8 HANG) and serial (28 SIG11 / 6 HANG) is fully accounted for by the harness artifact above — 178 and 179 are SIG11 in both, but parallel contention pushes them into the HANG bucket at 10s.

---

## 3. FENCE1 ∧ DEFER = HANG — MECHANISM FOUND IN EMITTED ASM

**Reproducer (6 lines, sub-second, no input):**
```
        cmd = FENCE('a' | 'ab')
        s = 'aY'
        s  POS(0) *cmd 'Y' RPOS(0)   :S(YES)F(NO)
YES     OUTPUT = 'matched'           :(END)
NO      OUTPUT = 'fail'
END
```
- FENCE1 inline alone: **correct** (manual §FENCE oracles pass)
- defer alone: **correct**
- FENCE1 ∧ defer: **HANG**

Three hypotheses died to probes:
1. ❌ FENCE degrades to SUCCEED (oscillator) — falsified by inline oracle: both manual worked examples pass
2. ❌ Multiple deferred sites required — falsified: one site hangs
3. ❌ FENCE1 is the culprit — falsified: FENCE1 via var without `*` is correct

**Root cause — in emitted asm of `f_one.sno`, lines 953–971 of `f_one.s`:**

```asm
n43_match_end_α:
        mov   r10, r12          ; r10 = scan-structure base
.Lx88_9:
        sub   r10, 24           ; r10 used as scratch loop counter
        mov   rax, qword ptr [r10 + 0]
        test  rax, rax
        jne   .Lx88_9           ; backward scan for null terminator
        ...
        mov   r10, rsi          ; r10 reused as second scan base
.Lx88_5:
        sub   r10, 24
        mov   rax, qword ptr [r10 + 0]
        test  rax, rax
        jne   .Lx88_5
        lea   rdi, [r10 + 24]
```

`match_end_α` runs two backward-scan loops using r10 as a scratch base pointer, **with no RTCC veneer bracket**. Everywhere else in this artifact (~40 sites), r10/r11 are protected by the bracket:
```asm
        mov   qword ptr [rax + 56], r10   ; save
        mov   qword ptr [rax + 64], r11
        mov   r11, qword ptr [rip + g_rtcc_block@GOTPCREL]
        mov   r10, qword ptr [r11 + 56]   ; reload
        mov   r11, qword ptr [r11 + 64]
```
`match_end_α` is the outlier.

**Why this hangs rather than SEGVs:** The scan loop leaves r10 pointing into a live structure at a plausible address — not random junk. When the FENCE1 pending cell fires `jmp r10`, it jumps back INTO the scan loop interior. That's a real code address; it hangs, not crashes.

**FENCE1 is the victim.** It holds a pending cell live across `match_end`. Its β fires with r10 = scan-loop residue. The fix belongs in `bb_match_end`, not `bb_match_fence1.cpp`.

**Charter confirmation:** GOAL-SN4-ZETA-CLIMB.md, GOAL-SNOBOL4-RTX.md both state:
> ⛔ WREG-0's claim gate must sweep RTX asm sources, not just src/templates/

And GOAL-PASSTHRU-RBP-ERAD.md, LADDER WREG design:
> ⛔ r10 IS ALREADY CLAIMED ... ANY RTX asm that clobbers r10 or r11 silently breaks EVERY pattern blob in flight

`match_end_α` is the exact failure the claim gate was designed to catch.

---

## 4. SECONDARY FINDING: `f_two_nofence` WRONG ANSWER

`cmd = ('a' | 'ab')` (no fence), two deferred sites, `outer = (*cmd 'X' | *cmd 'Y' | LEN(0))`, subject `aY` → SCRIP returns FAIL (rc=0, output "fail") where a match is correct. This is an independent defect in the DIFF class, unrelated to the wire registers.

---

## 5. NEXT SEAT — IN ORDER

1. **Fix `bb_match_end`** — replace r10 scratch with a register that is not the wire pair. Every other site in the same artifact uses the RTCC veneer bracket; `match_end_α` is the outlier. Before committing: rebuild, run `board_patterns_set.sh snap fix`, then `diff head fix` — watch the BROKEN set, not the net count. Minimum witness: `f_one.sno` flips from HANG to match.

2. **Verify with claim gate** — `scripts/test_gate_wreg_claim.sh --strict` should catch the clobber; if it didn't, add `match_end_α`'s scan-loop r10 spelling to its coverage.

3. **Artifact-level claim gate** — add a build-step that greps every generated `.s` artifact for r10/r11 appearing outside the veneer bracket pattern. Sources-only grep would have missed this; the artifact would have caught it.

4. **UNCONFIRMED:** Whether `match_end`'s scratch use is an oversight or structural (e.g., RTCC block partially torn down at `match_end`). The asm at lines 973+ writes into `g_rtcc_block` immediately after the scan loop, suggesting the block is still live — so the veneer bracket should be safe — but verify before committing the fix.

5. **`f_two_nofence` wrong answer** — separate defect, separate rung.

---

**Reproducers:** `f_one.sno`, `f_two.sno`, `f_two_nofence.sno`, `f_inline.sno`, `f_defer_nofence.sno`, `f_fence_var_nodefer.sno`, `fence_probe.sno` — container-local at `/home/claude/work/`, NOT committed to corpus (red probes; RULES §4).

**Emitted asm:** `f_one.s` — container-local, produced by `./SCRIP/scrip --compile f_one.sno`.
