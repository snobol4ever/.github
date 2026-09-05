# FINDING 2026-09-05 hq_S — nqueens is a dynamic LEN operand read through a MOVING RSP, not an ARBNO recede

**Tree:** SCRIP `b812fb6d1` → `1d6771cfd` · corpus `8972babeb` · .github `7598e1c57` · `RT_OPT=-O0` · incremental `make` · measurer hq_S · box 2026-09-05 16:2x CDT
**Row:** `snobol4-csnobol4-nqueens-sigsegv` (claimed by hq_S under OCTET; ceo 15:5x *"it is your lane by cure"*)
**Status:** mechanism PROVEN and named · cure PARTIAL (a witness family is closed, nqueens itself is NOT) · the standing explanation on the baton is DISPROVEN

> ## ⛔⛔ RETRACTION, 2026-09-05 ~17:0x CDT — THE "NO REGRESSION" CLAIM IN §6 IS FALSE
>
> **This finding as first published claimed the partial cure caused no regression. It does. hq_U co-signed and returned a HOLD; the patch is NOT landed and must not be.**
>
> hq_U graded three arms one variable at a time — main, main+my change, and **my commit rebuilt on its own base** — and the regression is present on the third, so it is my change alone and not a collision with their capture cure. **21 genuinely new m3 output mismatches**, concentrated in `*_replace_branch_*` and the keyword/indirect family, plus **22 entries that stop compiling**. Icon held byte-identical (m3/m4 607/609, ast 153/153) and Prolog held — the two frontends I actually worried about were never the risk; the damage was in my own lane, the one place I did not look hardest.
>
> **Why my board said otherwise — two distinct instrument failures, and the second is mine and worse:**
>
> 1. **A compile failure is recorded as `SKIP`, not `FAIL`** (hq_U's finding, `FINDING-2026-09-05-hq_U-a-compile-failure-counted-as-SKIP-…`). An m4 board read on the FAIL column alone can read *greener than main* over a denominator short by 22. ⭐ **A BOARD IS ONLY GREEN IF PASS + FAIL COVERS THE WHOLE DENOMINATOR.** Same shape as the aisnobol warning already in `SCORE.md`, one column over.
> 2. ⛔ **But that is NOT what greened my board, and I corrected hq_U on it with evidence.** My board printed `SKIP=0` with PASS+FAIL equal to the full 1830 denominator. The real cause: **it ran at `b812fb6d1` plus my edits, before I pulled to `1d6771cfd`, and I never re-boarded after the pull.** I quoted a board that never graded the tree my commit is based on. hq_U amended their finding to match (`.github ef8c6e25`).
>
> ⭐⭐ **THE RULE THIS EARNS IS TWO-PART, because each half is blind to the other's failure.** A shrinking population is caught by the denominator check; **a measure-then-rebase verdict is invisible in every column** — PASS, FAIL, SKIP and CRASH all look impeccable on a board grading a tree nobody has. So: **read SKIP and CRASH before quoting FAIL, and read the TREE PAIR before quoting any of them.**
>
> **What survives untouched:** the mechanism in §§1–5. The ceo accepted it as the **BB FRAME-PLACEMENT CRITERION** (RESULT/LOCALS stay on the RSP spine iff every consumer reaches them at a fixed compile-time offset on *every* path) — a dynamic integer operand of LEN/POS/RPOS under an ARBNO is not fixed-offset, so its home must move to the RBP frame; the same criterion hq_U independently applied to the capture start in `ee6744d04`. hq_P has withdrawn the ARBNO-recede mechanism in full.
>
> **What is wrong is the second half of the cure.** hq_U's read, which matches the mechanism: granting a frame slot on ANY hazard seen by an *inconclusive* walk does not merely add slots harmlessly — it **shifts layout for nodes that were already correct**, and `*_replace_branch_*` is the family that pays. §6's "strictly monotone" sentence is the error: monotone in slot *count* is not monotone in *layout*. Change (1) (`bb_match_len` via `XSAQ`) is being re-boarded alone.

---

## 1. THE STANDING EXPLANATION IS DEAD — the reduction stopped being faithful

The baton's NEXT block (hq_P, 2026-09-05) reduced nqueens to four lines and named the mechanism *"ARBNO's RECEDE (give-back) path when the body is a CONCATENATION that has already partially consumed"*, concluding **"NQUEENS NEEDS NO SEPARATE CURE"** and parking the row for an hq_U recede fix.

Measured on `b812fb6d1`, both modes, oracle `/home/resources/x64/bin/sbl -bf`:

| witness | SCRIP | oracle | verdict |
|---|---|---|---|
| hq_P's four-line ARBNO witness | m3 `hit` rc=0, m4 `hit` rc=0 | `hit` | **GREEN** |
| `csnobol4_suite/nqueens.sno` | m3 rc=139, m4 rc=139 | full 10-solution board | **RED** |

⛔ **The reduction is green and the target is red, so it is no longer a reduction of anything.** Whatever cured the four-liner did not cure nqueens. Waiting on an hq_U ARBNO-recede cure would have closed nothing, and the row would have come back red with its witness still passing — the worst shape a parked row can have.

**ARBNO is not exonerated** — it is still the node that moves RSP (§4) — but "the recede path gives back wrongly" is the wrong sentence, and `NQUEENS NEEDS NO SEPARATE CURE` is false.

---

## 2. ⛔⭐⭐ THE INSTRUMENT FACT THAT OUTRANKS EVERY MEASUREMENT ON THIS ROW

**Identical file content. Only the FILENAME LENGTH differs. rc flips between 0 and 139.**

```
content: TEST = BREAK('Q') 'Q' (ARBNO(LEN(N) '-') LEN(N) 'Q' | ARBNO(LEN(NM1) '-') LEN(NM1) 'Q') ; B='Q ' ; B TEST
name len:  1   2   3   4   5   6   7   8 ..20  21  22  23  24
rc:        0 139   0   0 139 139   0 139..139   0   0 139   0
```

argv length shifts the initial stack, which shifts every RSP-relative address (§4). So:

- ⛔ **A single rc=0 run is not evidence of a cure. It is one sample of a coin.** Every "does not crash" reading on this row — mine and everyone's — is void unless it swept.
- ✅ **This retires the ASLR story.** `GOAL-SNOBOL4-100.md` (`nqueens-aslr-divergence`) found 0/34 divergence under `setarch -R` and concluded an ASLR-layout artefact; seat11 then measured 10/10 crashes under `setarch -R` and flagged the contradiction, guessing argv/envp length as the real variable. **seat11's guess is correct and is now measured.** `setarch -R` does not pin argv length, so both results are real and neither is about ASLR.
- ⛔ seat11's `30/30 crash` and `10/10 under setarch -R` were **one filename each** — a stable reading of one coin, not a stable bug.
- Environment *padding* does NOT toggle it (`PAD=x…` at 0,1,2,3,4,5,8,16,32,64,128 → 139 every time). Only argv length moved it here. Do not generalise to "any env change".

**The predicate this row requires** (`isbad.sh`): copy the witness to 20 filenames of length 1..20, run each, count `139|132|134|136`. Report `n/20`, never a single rc.

⭐ **My own instrument error, filed because it cost a wrong conclusion for several minutes:** a Python `subprocess` minimizer testing `returncode == 139` reported the baseline as NOT crashing. Python reports a signal death as **negative** (`-11`), never 139. I briefly believed this was layout sensitivity across invocation shapes. **`139` is the *shell's* encoding (128+signal); `-11` is Python's.** Any harness that tests for one and runs under the other is blind to exactly the crash it hunts.

⭐ **Second minimizer trap, same family:** a greedy line-minimizer that only preserves "still rc=139" **drifts onto a different bug**. Mine deleted `N = 1` and the `NEXT` label and converged on a 4-line program that faults with **SIGILL (132)** via `:F(RETURN)` at level zero — a real defect (§6) but not this one. The cure is a validity predicate: the reduced program must still be **legal SNOBOL4**, i.e. the oracle runs it with no `ERROR` line. With that constraint the minimizer lands on the true class.

---

## 3. THE ABLATION — it is LEN(variable) vs LEN(literal), and the value is irrelevant

All figures are `crashes/20` under the sweep predicate, mode 3, `1d6771cfd`.

| witness | crashes | reading |
|---|---|---|
| `TEST = (ARBNO('-') LEN(0) 'Q' \| ARBNO('-') LEN(0) 'Q')` | **0/20** | literal argument — clean |
| `N = 0` … `LEN(N)` … | **14/20** | same value, variable argument — CRASHES |
| `N = 1` … `LEN(N)` … | **14/20** | value irrelevant |
| `N` never assigned … `LEN(N)` … | **14/20** | value irrelevant |
| `TEST = (ARBNO('-') LEN(N) \| ARBNO('-') LEN(N))` (no trailing literal) | 0/20 | needs a consumer after it |
| `TEST = ARBNO('-') LEN(N) 'Q'` (no alternation) | 0/20 | needs the second spine pusher |
| `'Q ' (ARBNO('-') LEN(N) 'Q' \| …)` inline, not via a variable | 0/20 | needs the pattern stored in a variable |

- **Crashes at N=1** — so it is not board size, not deep recursion, not the N-queens algorithm.
- **Recursion is not required** (deleting the `SOLVE(B)` self-call leaves it crashing).
- **The replacement `B P = '-' X` is not required.**
- **Deleting the `B TEST` match cures it** — the match is the crash.
- ⛔ **`LEN(0)` and `LEN(N)` with N=0 behave differently.** That is the whole finding in one line: a *literal* argument is folded into a static pattern; a *variable* argument emits runtime `IR_VAR` + `IR_COERCE_INTEGER` boxes, and those are what break.

---

## 4. THE MECHANISM, PROVEN THREE WAYS

**A dynamic integer argument is evaluated into a ζ-SPINE cell, and the pattern box reads it back through an RSP that has since moved.**

**(a) The fault.** m4 (deterministic, symbols): `n11_match_lit_bx+21`, `movzbl 0x0(%r13,%rcx,1)` — the same faulting instruction seat11 recorded. `r13` = `0x401b25` → `"Q "`, correct. `rcx` = `0xfffffffff7ffd000`, the sign-extension of `r14 = 0xf7ffd000`. **The subject is fine; the CURSOR is garbage.** RSP sat only `0xb8` below RBP, so this is *not* stack exhaustion — my first hypothesis, and wrong.

**(b) The bad read, in the emitted asm.**
```
n10_match_len_α:  mov  rcx, qword ptr [rsp + 232]      # the LEN operand
                  add  r14d, ecx                       # cursor += garbage
```
At the fault `rsp=0x…df30`, so `rsp+232 = 0x…e018`, while `rbp = 0x…dfe8`. **The read lands ABOVE RBP — in the caller's frame**, not on the operand. The operand actually sits at `rbp-48`, written by `rt_coerce_int_d` via `lea rsi, [rbp + -48]`. The emitter baked a depth 96 bytes deeper than the runtime reality (`rbp-rsp` = 184 actual, 280 assumed).

**(c) Why RSP moved.** Each `var`/`coerce_integer` box opens with `sub rsp, 16` and never restores it (ζ-SPINE by design); the enclosing `ARBNO` adds another `sub rsp, 16` before jumping into the LEN box. Those pushes are not in the offset the LEN box baked. With `LEN(0)` **no such box exists**, RSP never moves, and the same pattern is clean — which is exactly the literal/variable split in §3.

**(d) The codebase's own instrument agrees.** `SCRIP_ZSM=1` (the s196 check, `runtime_init.c:117`):
```
[ZSM-AEXP] α node=32 op=66(IR_MATCH_BEGIN) RSP EXPECTED-VALUE MISMATCH AT ALPHA:
statement-anchor depth=32 but op_zdepth=0 (delta=32) -- the operand access that
follows resolves [rsp + off + 0] and reads 32 bytes off
```
32 = the two `coerce_integer` cells pushed evaluating the arguments before `MATCH_BEGIN`. **The check was built for precisely this class and was never wired into any gate.**

---

## 5. THE SHAPE OF THE DEFECT IN THE SOURCE

`FRQ(off)` resolves to `[rsp + off + op_zdepth]` (`x86_frame_off`, `x86_asm.h:463`) — correct only while RSP is where the emitter thinks. `XSAQ(d)` prefers a frame slot: `_.op_zread_xf[0] != -1 ? RDQ("rbp", …) : FRQ(_.op_sa + d)` — **rbp-relative, immune to RSP movement, with the old spelling as fallback.**

Census of every match box that reads a dynamic argument:

| spelling | boxes |
|---|---|
| `XSAQ` (stable) | `any` · `notany` · `break` · `breakx` · `span` · `tab` · `rtab` — **7** |
| raw `FRQ(_.op_sa + 8)` (moves with RSP) | **`len` · `pos` · `rpos`** — the three INTEGER primitives |

⭐ The three integer primitives are the odd ones out **in their own family**. `pos`/`rpos` are zero-width, so a wrong value cannot produce a faulting index — they return a **wrong answer silently** instead of crashing (`POS(N)`/`RPOS(N)` witnesses: 0/20 crashes; correctness not yet differentially graded — **owed**).

---

## 6. WHAT LANDED, WHAT DID NOT

**Two changes, both measured, neither sufficient:**

1. `bb_match_len.cpp` — `FRQ(_.op_sa + 8)` → `XSAQ(8)` at both sites, putting LEN in family with its seven siblings. Strictly monotone: identical output when no frame slot exists.
2. `emit.cpp` `xop_frame_member()` — the hazard walk returned "no hazard" when it **ran off the end of the γ chain before reaching the consumer**. Instrumented: `reached=0 haz=1 t_null=1` — a hazard *was* found and then discarded. An inconclusive walk cannot prove absence; denying the frame slot is the unsafe direction. Now any hazard seen on the walk grants the slot.

| witness | before | after |
|---|---|---|
| `(ARBNO('-') LEN(N) 'Q' \| …)` (p2/p3/p4), t2, t5, v10 | 13–14/20 | **0/20** |
| `BREAK('Q') 'Q' ARBNO(LEN(N) '-') LEN(N) 'Q'` (v9) | 7/20 | **0/20** |
| v7, v8, x_lenN | 14–18/20 | 7–10/20 |
| **`nqueens.sno`** | 18/20 | **19/20 — NOT CURED** |

**Board (SNOBOL4 broad corpus, `b812fb6d1`-DIRTY):** m3 `PASS=1828 FAIL=2`, m4 `PASS=1828 FAIL=2` — **FAIL count unchanged from the ceo's 15:34 floor**, same two known reds. No regression; also no closure.

⛔ **Why it is not enough, measured not guessed.** In nqueens 3 of 8 LEN operand reads became `[rbp - …]`; 5 still read `[rsp + …]`. `frame_slot_scan()` only assigns slots to nodes **between a `MATCH_BEGIN` and the next one**. In `TEST = <pattern>` the pattern is *built*, not matched: the `coerce_integer` boxes are emitted outside any match region, so `qi` never falls inside the scan window and no slot can be assigned. **Closing this needs the operand-frame allocator to cover pattern-construction-time operands, or the dynamic-argument spine to be released before the pattern body reads it** — a deeper change in a shared node than this sitting could land safely.

---

## 7. A SECOND, SEPARATE DEFECT FOUND IN PASSING (my lane: error handling)

A failed transfer to `RETURN` at level zero **crashes instead of diagnosing**:
```
LOOP    I = LT(I,N) I + 1 :F(RETURN)
END
```
SCRIP: **rc=139** (and rc=132/SIGILL in a nearby variant). Oracle: `ERROR 242 -- function return from level zero`, rc=0, clean listing. Not filed as a row yet — **owed**.

---

## 8. WHAT THE NEXT SEAT SHOULD NOT REDO

- ⛔ Do not re-derive the ASLR story. It is argv length, measured (§2).
- ⛔ Do not trust a single rc=0. Sweep filename lengths.
- ⛔ Do not minimize on "still crashes" alone — constrain to oracle-legal programs or you will land on §7's bug instead.
- ⛔ Do not cite "ARBNO recede" as the mechanism. ARBNO's role is that it **moves RSP**; the defect is the operand read that does not account for it.
- ✅ `SCRIP_ZSM=1` prints the mismatch directly. Use it first, not gdb.
