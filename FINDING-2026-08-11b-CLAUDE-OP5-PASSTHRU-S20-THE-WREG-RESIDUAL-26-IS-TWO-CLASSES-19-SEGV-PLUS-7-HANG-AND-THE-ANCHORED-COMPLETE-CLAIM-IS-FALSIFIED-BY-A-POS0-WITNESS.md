# FINDING 2026-08-11b (s20, Claude Opus 5) — PASSTHRU / LADDER WREG

## THE WREG RESIDUAL 26 IS **TWO** FAILURE CLASSES — 19 SIGSEGV + 7 HANG — AND THE HANG CLASS BILLS TO WREG-4, NOT WREG-3. THE "ANCHORED PATTERNS ARE COMPLETE UNDER THIS ARM" CLAIM IS FALSIFIED BY AN 8-LINE `POS(0)` WITNESS.

**Fingerprint:** SCRIP `afed6184` (s19 close, UNTOUCHED — **zero `src/` bytes changed this seat**) · corpus `5da04e78` UNTOUCHED · `.github` this commit.
**Scope:** measurement + instrument only. No emitter edit, no rung landed, no default flipped.

---

## 1. THE s19 BASELINE REPRODUCES EXACTLY, IN A DIFFERENT CONTAINER, BY SET

Fresh clone + fresh `-O0` build (256 objects, zero-byte-`.o` trap checked and clear), `crosscheck/patterns` 122 programs, mode 3, **same binary both arms**:

| arm | PASS |
|---|---|
| `SCRIP_WREG=0` | **100 / 122** |
| `SCRIP_WREG=1` | **74 / 122** |

**REPAIRED 0 · BROKEN 26**, and the broken set is name-for-name the set s19 named (`114 119 124 126 127 129 130 131 …`). s19's numbers are honest and they travel. That is worth recording on its own: this ladder's measurements have now survived a container change, which the s7 law says counts never do — the *sets* did.

## 2. ⭐⭐⭐ THE NEW FACT: THE 26 SPLIT 19/7 BY FAILURE MODE

The s19 cursor carries the residual as one class ("SIGSEGVs PERSIST", "the residual 26 are FENCE- and `*var`-heavy … i.e. the classes that actually suspend"). Measured by return code, that is **half the picture**:

| rc | meaning | count in the 26 |
|---|---|---|
| 139 | SIGSEGV — wild transfer | **19** |
| 124 | **HANG (timeout)** — retry loop that never advances | **7** |

**The 7 HANG programs, by name:** `114_pat_fence_via_var_in_paren_alt` · `130_pat_two_star_fence_concat_outer` · `137_pat_balanced_mixed` · `138_pat_calc_paren_expr` · `144_pat_json_nested_array` · `147_pat_fence_through_unevaluated` · `150_pat_star_var_fence_alts_no_arbno`

(Whole-ON-arm context, 48 fails total: 26×rc=139, 11×rc=124, 11×rc=0. So 4 of the hangs and all 11 wrong-output fails are **pre-existing**, shared with the OFF arm, and are not WREG's debt.)

**WHY THE SPLIT IS LOAD-BEARING.** A SIGSEGV is a transfer to a bad landing — consistent with the missing resume path, i.e. **WREG-3 / W-MAP (3)**. A HANG is not: it is a loop that re-attempts without advancing, which is the signature of the **unanchored-scan retry-advance stub that WREG-4's remaining half still owes** (the s19 slice degenerated `scanfail` to a bare ω transfer and explicitly deferred the site-side stub). ⛔ **Therefore W-MAP (3) alone cannot be expected to close all 26**, and any seat that sizes the residual as one suspension problem will land W-MAP (3), measure ~19 repaired, and mis-read the leftover 7 as a W-MAP (3) defect. **Bill 19 to WREG-3 and 7 to WREG-4 before spending either.**

## 3. ⛔⭐⭐ THE ANCHORED-COMPLETE CLAIM IS IN TROUBLE — 8-LINE WITNESS

`emit.cpp:2735`'s slice-1 comment states: *"Anchored patterns are COMPLETE under this arm (manual p.204 step 6: with &ANCHOR nonzero an empty stack IS total failure — there is no advance-and-retry to lose); unanchored ones still owe the stub."*

`114_pat_fence_via_var_in_paren_alt.sno` is **8 lines** and is anchored **both ends** by explicit `POS(0)`/`RPOS(0)`:

```
        cmd = FENCE('a' | 'ab')
        outer = (*cmd 'X' | *cmd 'Y' | LEN(0))
        s = 'aY'
        s  POS(0) *outer RPOS(0)                              :S(YES)F(NO)
```

Subject `aY`: the first alternative `*cmd 'X'` matches `a` then needs `X` and gets `Y`, so control **must backtrack into the suspended blob** and take `*cmd 'Y'`. Expected output `second outer alt matched aY`; OFF arm produces it, ON arm **hangs**.

⛔ So either (a) the anchored/unanchored discriminator is not being read where the retry decision is made, or (b) the completeness claim does not hold for *interior* alternation retry as opposed to *scan-start* retry — p.204's step-6 argument is about advancing the start position, and this loop is not advancing a start position. **Do not treat the anchored column as paid.** This is the cheapest witness in the corpus for whichever answer is right: 8 lines, no input file, sub-second.

## 4. ⛔ INSTRUMENT CORRECTION — gdb IS DARK ON THIS CLASS, AND ASLR IS NOT THE REASON

FF-0's amended instrument order says *"gdb PRIMARY, monitor SECONDARY."* On the HANG members that instruction walks a seat straight into a timeout:

- `gdb -batch -ex run` on `114` under `SCRIP_WREG=1` **never reaches a fault** — killed at 100 s and again at 120 s, with and without `SCRIP_NO_SEGV_HANDLER=1`. Output is two libthread lines and nothing else.
- The obvious suspicion is gdb's ASLR disabling (this file already records *"THE TREE IS ASLR-FLAKY ON THIS SET"*). **Falsified:** `setarch -R` (ASLR off, no gdb) hangs identically, and plain runs with ASLR **on** hang identically — 4/4 and 2/2 `rc=124`. **The hang is real and deterministic, not an instrument artifact and not ASLR.**

⇒ **gdb PRIMARY is correct for the 19 SIGSEGV members and useless for the 7 HANG members.** For the hang class the discriminating instrument is a bounded-iteration probe or the 2-way monitor watching whether the retry cursor advances — not a backtrace. Recorded so the next seat does not spend the ~15 minutes this one did.

## 5. WHAT IS OWED, RE-SIZED

1. **WREG-3 / W-MAP (3)** — γ pushes `{res, r10, r11}` (24B → 32B aligned) at the deep frontier; `res` restores the pair and falls to β's dispatch. ⛔ **`res` MUST NOT take r10/r11 as scratch** — it does today (`proc_PAT$N_res` re-pushes `g_zctx` using exactly that pair), currently DORMANT only because γ is a bare `jmp r10` and never references the label. W-MAP (3) is precisely the edit that **arms** it. **Expected blast radius: the 19 SIGSEGV members.**
2. **WREG-4 remaining half** — statement-side ω retry-advance stub, attempt cursor in the statement frame's licensed slots. **Expected blast radius: the 7 HANG members**, and §3 says re-derive the anchored predicate before assuming anchored sites can skip it.
3. **Interior-free audit (s19 CORRECTION 4)** — still UNPERFORMED. The ω absolute unwind and scanfail re-base were removed; that is safe only if every interior box frees on its own internal ω. A construct that carves and does not release on its fail path now accumulates residue per retry with nothing reclaiming it — **which is also a candidate mechanism for the HANG class**, and should be checked before §5.2 is designed.
4. Registration deletion (6 `rt_proc_set_*` + `.globl proc_PAT$N_α`); the 234-site sweep; regen ×3 (still owed from s17 — **not** discharged here: zero emitter bytes changed, OFF arm unmoved).

## 6. INSTRUMENT LANDED

`SCRIP/scripts/test_board_wreg_byset.sh` — BY-SET board, both arms, same binary, and it prints the **failure-mode split** and the HANG membership, which is the column whose absence hid §2. Run one arm at a time under short tool timeouts (`… byset.sh off` / `… byset.sh on`); a both-arms run is ~10 min of wall clock on this corpus.

## 7. LIMITS OF THIS SEAT, STATED

m3 only — no m4, no probe suite, no broad-336, no xc-318. No `src/` edit, so no gate re-proof was owed and none was run. The 19/7 attribution in §2 is an inference **from failure mode**, sound on the reasoning above but **not yet convicted at an instruction** for any single member; §5.1/§5.2 should confirm on one witness each before the ladder is re-sequenced on it.
