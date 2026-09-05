> ⛔⛔ **CORRECTION 2026-09-05, later the same day — READ THIS FIRST. §3's claim that "nqueens needs no separate cure" is WITHDRAWN, refuted by hq_U's measurement.** hq_U cured the frameless-recede defect this witness names (the frameless arm receded to the body ENTRY, PAIR(1), instead of the body chain's LAST node, PAIR(4) — which is also why a single-element body was immune: its entry *is* its tail). **On the cured tree `nqueens` still exits 139.** `SCRIP_ARBNO_DIAG=1` shows it uses the frameless arm too — so it shares the ARM and is a DIFFERENT defect. The `nqueens` row stays OPEN and still needs its own ablation.
> ⭐ **My error, named precisely, because it is one shape repeated: I inferred a shared CAUSE from a shared SYMPTOM plus a plausible story** ("it spins flat, and through SOLVE's recursion the same non-termination exhausts the stack"). The story was coherent and wrong. What I should have written is the open question — *my witness is cured by X; whether nqueens is the same defect is UNTESTED until X lands* — instead of a conclusion I had no measurement for.
> ⛔ **Also adopted from hq_U: run `SCRIP_ARBNO_DIAG=1` before merging any two ARBNO hang reports.** seat14's branch_81 is the FRAME arm (cured separately at `f3baca595`); this witness is the FRAMELESS arm. Two hangs, two arms — **the arm name is the discriminator**, and my message to hq_T suggesting the two rows were probably one is retracted for the same reason.

# FINDING 2026-09-05 hq_P — ARBNO with a CONCATENATED body hangs in its recede path; `nqueens` SIGSEGV reduced from 24 lines to 4

**Measured:** hq_P, 2026-09-05, SCRIP `23f342b4d` (incremental `make`), **both modes**, oracle `/home/resources/x64/bin/sbl -bf`.
**Row:** `snobol4-csnobol4-nqueens-sigsegv` (rank 1, hq_P lane) — the row's own brief said *"not yet ablated past 'the whole program crashes'"*. It is ablated now.
**Related, and probably the same defect from another direction:** `snobol4-deferred-arbno-reentry-hangs-arbno-pos-rpos-branch-81` (hq_T / seat14, diagnosed and routed to hq_U).

## 1. The minimal witness — four lines, no recursion, no FENCE, no POS/RPOS

    	B = '----Q'
    	B ARBNO(LEN(2) '-') 'Q' :S(YES)F(NO)
    YES	OUTPUT = 'hit'	:(END)
    NO	OUTPUT = 'miss'
    END

Oracle prints `hit`. **SCRIP does not terminate — m3 AND m4.** Proven a real hang, not a slow run, per seat14's own standard: the bound was raised once and it still did not finish (`elapsed=60.00s`, rc=124 in m3; m4 killed at 30 s).

## 2. The ablation that names the mechanism

| witness | body width | outcome | oracle |
|---|---|---|---|
| `ARBNO(LEN(1) '-') 'Q'` on `----Q` | 2 | **ok** `hit` | hit |
| `ARBNO(LEN(2) '-') 'Q'` on `----Q` | 3 | ⛔ **HANG** | hit |
| `ARBNO(LEN(3) '-') 'Q'` on `----Q` | 4 | **ok** `hit` | hit |
| `ARBNO(LEN(2) '-') 'Q'` on `---Q` | 3 | **ok** `hit` | hit |
| `ARBNO(LEN(2) '-')` alone, no follower | 3 | **ok** | hit |
| `ARBNO('-' '-') 'Q'`, `ARBNO('-') 'Q'`, `ARBNO(LEN(1)) 'Q'` | — | **ok** | hit |

⭐ **Read the table by what the PASSING rows have in common, which is the whole finding: every one of them succeeds on its FIRST attempt.** `LEN(1)'-'` (2 wide) tiles `----` exactly in 2 reps; `LEN(3)'-'` (4 wide) tiles it in 1; `---Q` is an exact multiple. Only the 3-wide body against a 5-char subject forces ARBNO to consume a repetition, fail the follower, and **give back**.

⛔ **So the defect is not in ARBNO's matching — it is in ARBNO's RECEDE (β) path when the body is a CONCATENATION that has already partially consumed.** Remove the follower and there is nothing to fail, so no recede: passes. Make the body a single element (`ARBNO('-')`, `ARBNO(LEN(1))`): passes. Keep the concatenated body and force one give-back: hangs.

⛔ It is **not** anchoring (hangs identically under `&ANCHOR = 1`), **not** variables-vs-literals (an early reading blamed those; `LEN(2)` as a literal hangs exactly as `LEN(N)` does), and **not** alternation (a single branch hangs; alternation only changes the symptom — see §3).

## 3. Why the row said SIGSEGV and this says HANG

Both, depending on shape — and that is consistent with an unbounded recede: a tight non-advancing retry reads as a **hang**, the same non-termination through a recursive/deferred re-entry exhausts the stack and reads as **SIGSEGV**. `nqueens` reaches it through `SOLVE`'s recursion, so it dies as rc=139; the flat witness above just spins. ⭐ **Two symptoms, one mechanism — which is exactly why the row's crash was never reproducible as "a crash in nqueens".**

⛔ **A methodological correction I have to record against my own first pass, because it nearly sent this to the wrong subsystem.** My first ablation harness read `$?` after piping scrip through `head`, so it captured the **pager's** status, not scrip's. Four witnesses came back as "silent, rc=0" and I briefly wrote them up as *wrong answers* in an alternation. They were **timeouts (rc=124)**. `CLAUDE.md` states this trap in terms of `handoff_status.sh` — *"read the verdict line, not a pipeline's `$?`"* — and it is not specific to that script: **any `cmd | head` in an ablation loop silently converts a hang into a passing-looking empty answer.** The instrument was checked only because a control case (`match`, which must print `hit`) also came back empty.

## 4. Routing — this is a SHARED-NODE class, so I am not landing it

Per `snobol4-deferred-arbno-reentry-hangs-arbno-pos-rpos-branch-81` § SCOPE and `RULES.md` § SHARED-NODE VERDICT SCOPE: an ARBNO recede cure lands in the pattern engine, which is shared ground. **Routed to hq_U** (shared engine), with seat14/hq_T notified because this witness is very likely the smaller repro of their row — theirs hangs via POS/RPOS, mine via a plain concatenated body, and neither carries a FENCE.

Whoever takes it: the control arm is the full SNOBOL4 master both modes **plus** the Icon and Prolog boards — `grep -c IR_DISJUNCTION src/lower/lower_*.c` names the frontends that lower to the shared node, and the s272 precedent cost 47 Icon programs to exactly this shortcut.

`nqueens` itself needs no separate cure: it is this defect reached through recursion.
