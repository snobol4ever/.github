# FINDING 2026-08-11e — EARN-0b: THE LIFO THEOREM HOLDS ON GREEN PATHS IN BOTH DIRECTIONS, AND EARN-0b AS SPECIFIED IS UNRUNNABLE BECAUSE ITS WITNESS CLASS IS BROKEN AT HEAD

**Seat:** Claude Opus 5 + Lon in-chat · **Goal:** `GOAL-RBP-EARN.md` rung EARN-0b · **Zero src bytes.**
**Fingerprint:** SCRIP `fc5b0754` UNTOUCHED · corpus `6c601c19` UNTOUCHED · `.github` this commit.
⛔ **HEAD IS NOT s25's FINGERPRINT.** s25 recorded SCRIP `b5a288bd`; origin is at `fc5b0754`. Every number below is measured at `fc5b0754`.

---

## 1. THE HEADLINE — EARN-0b CANNOT BE RUN AS WRITTEN, AND THE REASON IS NOT A QUIBBLE

EARN-0b specifies: *"ONE program with a framed box that suspends across a SECOND framed box, compiled at HEAD; gdb-watch whether `rbp` at β equals `rbp` at γ."*

That experiment has a precondition nobody stated: **the program must RUN CORRECTLY**, or there is no discipline to observe. At HEAD the nested-framed-construct class does not run correctly. Measured, m3, against pre-baked SPITBOL `.ref`:

| Group | Result |
|---|---|
| Primitive single-construct patterns `038`–`051` (CONTROL) | **14 PASS / 0 broken** |
| FENCE family `059`–`069` (framed construct) | 7 PASS / **6 WRONG** |
| `066_pat_fence_fn_nested` (FENCE inside FENCE) | **rc=0, EMPTY OUTPUT** (want `3.14`) |
| `147_pat_fence_through_unevaluated` | **SIGSEGV** |
| `181_pat_arbno_defer_tail_stressors` | **SIGSEGV** after `T1 MATCH` |

The control group is 100% green, so this is a **class boundary, not flake**: primitives work, nesting-across-a-second-framed-box does not. `066` is the dangerous shape — **exit 0 with no output**. RULES.md's warning applies verbatim: exit 0 is NOT exoneration.

**CONSEQUENCE FOR THE LADDER'S ORDER.** EARN-0b was placed first because "the entire ladder rests on it." But its witness class is repaired by EARN-4/EARN-7 — so **as specified, the falsification gate is blocked behind the work it was meant to gate.** This ordering must be resolved by Lon; it is not a seat's call.

⛔ Also: **EARN-0b's own named ARBNO witness cannot test the theorem at all.** ARBNO establishes NO frame at HEAD — it uses an RSP-relative carve (§3). There is no `rbp` to watch. The theorem is only testable on constructs framed TODAY: MATCH_BEGIN, FENCE1, STATEMENT, FUNCTION.

## 2. WHAT WAS ACTUALLY MEASURED — THE THEOREM HOLDS, BOTH DIRECTIONS, ON GREEN PATHS

Run on witnesses that are green at HEAD, breaking on the C-linkage runtime symbol `c_rt_defer_get_pat_fn`. (⛔ `c_rt_match_enter` NEVER FIRES in m3 — match entry is inline native code, not a C call. A seat that instruments it and sees nothing has a dark board, not a null result.)

**DOWNWARD (nesting).** Witness: `'AB' ? *F()` where `F = 'A' *G()` — an outer deferred reference containing an inner one.

```
outer *F()   rsp=0x7fffffff9b10   rbp=0x7fffffff9b30
inner *G()   rsp=0x7fffffff9b00   rbp=0x7fffffff9b20
```
Inner is strictly deeper by **exactly 16 bytes**, and `rbp` tracks `rsp` at a **constant 0x20 offset at both depths**. Nesting is properly stack-ordered and the frame relation survives the OPAQUE crossing.

**UPWARD (restoration).** Witness: `161_pat_defer_fn_nested_match` (green; stacks MATCH_BEGIN → FUNCTION activation → inner MATCH_BEGIN). `c_rt_defer_get_pat_fn` fires exactly twice — once per `*F()` reference, corroborating the oracle's `calls=1`/`calls=2` and manual p.85–86 ("re-fetched at EVERY match-time reference"). Both hits:

```
rsp=0x7fffffff9ae0   rbp=0x7fffffff9b00      (identical, to the byte)
```
After a complete match containing a FUNCTION activation **and** a nested match, the spine returns to **exactly** its prior depth.

**VERDICT: the LIFO theorem is CONFIRMED on green paths, in both directions.** The EARN PROTOCOL's "γ and β are free" is credible. **It is NOT confirmed universally** — see §4 for what remains untested.

## 3. THE ARBNO EXHAUSTION SEGV — MECHANISM CONVICTED (the crash itself was already known)

⛔ **Not a new crash.** EARN-4's gate line already records "`arb1.sno` T1 **and** T2 (the exhaustion path that SEGVs at HEAD)". **What is new is the mechanism.** (Note: `arb1.sno` **does not exist in any tree** — EARN-4's gate names a witness nobody has. The pair in §5 reproduces the shape.)

Minimal pair, `P = SPAN("ab") "c"`, pattern `POS(0) ARBNO(*P) RPOS(0)`, differing ONLY in subject:

| Subject | ARBNO path | ref | m3 |
|---|---|---|---|
| `"abcabc"` | succeeds (2 instances) | `MATCH` | `MATCH` rc=0 |
| `"abcab"` | **must exhaust and peel back** | `NOMATCH` | **SIGSEGV** |

Spine at fault (`SCRIP_NO_SEGV_HANDLER=1`):
```
[rsp+0x00]  0x00000003f1600095   <- BAD jump target
[rsp+0x08]  0x00007ffff1601965   <- valid slab addr
[rsp+0x50]  0x0000000500000002   <- TWO PACKED 32-BIT FIELDS
```
The faulting `rip` has an **intact low half and a corrupted high half**: `0xf1600095` is a plausible slab offset; the high half is `0x00000003` where a live slab address carries `0x00007fff`. A **32-bit write of `3` at slot+4** of a qword holding `0x00007ffff1600095` yields precisely `0x00000003f1600095`. The packed pair at `[rsp+0x50]` is the `[rsp+0]`/`[rsp+4]` cursor shape EARN-4 names.

**CONVICTED BY PREDICTION, NOT BY READING CODE.** `3` is the cursor position after the first instance `"abc"`. Prediction: lengthen the first instance, the clobber must follow.

| Subject | first instance | predicted | **measured `rip`** |
|---|---|---|---|
| `"abcab"` | `"abc"` (3) | `0x3` | `0x3f1600095` |
| `"aabcab"` | `"aabc"` (4) | `0x4` | `0x4f1600095` |

Resume address identical in both; high half tracks the cursor. **ARBNO's 32-bit cursor write at `[rsp+4]` lands on the upper half of a spine slot holding a 64-bit resume address, on the peel-back path.**

**THIS IS THE EARN LAW'S UNBOUNDED HAZARD, MEASURED IN THE WILD.** ARBNO's control cell is addressed RSP-relative; on the success path the depth happens to line up, on the exhaustion path instances peel and the distance is no longer the compile-time constant the write assumed. It is empirical support for the law and for EARN-4's instruction to delete the `[rsp+0]`/`[rsp+4]` machinery outright.

**⭐ AND IT REFRAMES THE CRASHES.** These are **not counterexamples to LIFO — they are violations of it.** An RSP-relative write landing outside its own carve is exactly what "the distance is not a compile-time constant" produces. LIFO holds where the implementation respects it, and the broken class is broken because something assumed a constancy it did not have.

## 4. WHAT REMAINS UNTESTED (do not read §2 as more than it is)

- **The fourth crossing row — heap-frame activations (resumable callables, generators, `flat_gen`), predicted NOT to hold — is UNTESTED.** SNOBOL4 does not obviously exercise it; it needs an Icon-generator or Prolog witness. **The row EARN-0b most wanted falsified is the row still standing.**
- The theorem is confirmed only where the implementation is already correct. It says nothing about the 6-WRONG FENCE set.
- ⛔ **A CONFOUND FOR THE NEXT SEAT:** FF-0's conviction on record is that blob γ/ω/res **never restore RBP**. An `rbp` mismatch at HEAD may therefore be that known old-regime defect rather than genuine non-LIFO control flow. **RSP is the confound-free instrument** — the theorem is a claim about spine DEPTH ORDERING and RSP tests it without depending on the old regime maintaining `rbp` at all. §2 uses RSP for this reason.

## 5. REPRODUCERS (6 lines each; `arb1.sno` candidates — EARN-4's gate has no file today)

```
        P = SPAN("ab") "c"                          |         P = SPAN("ab") "c"
        S1 = "abcabc"                               |         S2 = "abcab"
        S1 POS(0) ARBNO(*P) RPOS(0)  :S(A1)F(B1)    |         S2 POS(0) ARBNO(*P) RPOS(0)  :S(A2)F(B2)
A1      OUTPUT = "T1 MATCH"          :(N1)          | A2      OUTPUT = "T2 MATCH"          :(N2)
B1      OUTPUT = "T1 NOMATCH"                       | B2      OUTPUT = "T2 NOMATCH"
N1                                                  | N2
END          -> T1 MATCH  (rc=0)                    | END          -> want T2 NOMATCH; got SIGSEGV
```
LIFO nesting witness (green, rc=0, prints `match`):
```
        DEFINE('G()')     :(DEFF)
G       G = 'B'           :(RETURN)
DEFF    DEFINE('F()')     :(MAIN)
F       F = 'A' *G()      :(RETURN)
MAIN    'AB' ? *F()       :S(Y)F(N2)
Y       OUTPUT = 'match'  :(END)
N2      OUTPUT = 'fail'
END
```

## 6. ENVIRONMENT DEFECTS FOUND (cost this seat one build)

- **`gdb` is NOT installed and `scripts/install_system_packages.sh` does not cover it.** EARN-0b's specified method is a gdb experiment. Needs `apt-get update` FIRST — the stale index 404s on `libc6-dbg`.
- **`nproc` = 1.** `make -j4` in `REPO-SCRIP.md` buys nothing.
- **Backgrounded builds die when the shell call returns; `nohup … &` is NOT enough — use `setsid`.** A plain `nohup` build was killed at 83/256 objects leaving a 0-byte `.o`.
- `libscrip_rt.so` lands at **`out/libscrip_rt.so`**, not the repo root.

## 7. RULINGS THIS RAISES FOR LON

- **(1) EARN-0b's ordering.** Its witness class is repaired by EARN-4/EARN-7. Options: (a) accept §2's green-path confirmation as sufficient to proceed; (b) re-specify EARN-0b onto FUNCTION/MATCH_BEGIN witnesses that are green today (this seat's route); (c) demote it to run AFTER EARN-4. **Ordering is a Lon call.**
- **(2) Does §2 discharge EARN-0b?** The rung says "theorem CONFIRMED or the crossing table grows a fifth row." §2 confirms it in both directions on green paths, but the heap-frame row — the one predicted to fail — is untested. **This seat's recommendation: EARN-0b is PARTIALLY discharged; do not mark it done.**
- **(3) The 6-WRONG FENCE set and `066`'s silent-empty-output class** are pre-existing debt this measurement surfaced. They belong to a goal; RBP-EARN should not silently adopt them.
