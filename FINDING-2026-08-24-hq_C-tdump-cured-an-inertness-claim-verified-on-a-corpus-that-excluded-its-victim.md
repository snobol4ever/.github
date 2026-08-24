# FINDING — TDump_driver r12 SIGSEGV **CURED**: SNOBOL4 is **364/364 in both modes on `main`**, and an "inert" change was inert for nobody

**Seat:** `hq_C` (HQ-CORRECTNESS) · **date:** 2026-08-24 · **mode:** FLEET-4 · **row:** `tdump-driver-r12-cas-mark-sigsegv` (rank 0)
**Cure:** SCRIP `9df28b03` · corpus `d3299e1f0` · `.github` (this commit)
**Supersedes the red on:** `GOAL-HQ-COMPLETE.md` § THE STANDING CORRECTNESS BOARD, SNOBOL4 row

## HEADLINE

⭐⭐ **Lon's number is met on `main`: `m3 PASS=364 FAIL=0` · `m4 PASS=364 FAIL=0` · `SKIP=0`.** The last standing SNOBOL4 red is gone. The cure is **one line** — dropping the first of the two hunks `822bc8a1` landed — and it is **not a blind revert**: the commit's second hunk is kept, because it repaired something real and is not implicated.

## 1. THE DEFECT

`822bc8a1` ("zd_plan: fix arm-relative depth and gin/oin self-edge suppression") added two hunks to `zd_plan()` in `src/emitter/emit.cpp`, both gated on `zarm[i] >= 0`, and argued:

> *"Both conditions are gated on `zarm[i] >= 0`, which today is populated ONLY by the existing `IR_MATCH_ALTERNATE` admission path — so this is inert for all current callers."*

⛔⛔ **The premise is true and the conclusion inverts it.** `emit.cpp:2479` reads `if ((int)env->op != IR_MATCH_ALTERNATE) continue;` — ALTERNATE is indeed the **only** populator of `zarm[]`. That is exactly why the change is **inert for nobody**: the two new conditions fire **exclusively** on ALTERNATE, the one op the safety argument assumed they would never reach.

The remaining load-bearing claim was that *"ALTERNATE's arms never wire their own .γ/.ω literally back to the host node."* The emitted asm falsifies it twice in a single program.

## 2. THE MEASUREMENT — ASM-DIFF-FIRST, AS RULES.md ORDERS

Two worktrees, `69449f94` (PASS) and its direct child `822bc8a1` (CRASH), same program, whole-file diff of the emitted `.s`: **30 lines, 6 hunks, confined to two nodes** (`n2597`, `n2725`) — both `match_alternate`.

```diff
-  add rsp, 16;      jmp n2597_match_alternate_af
+  add rsp, 16
+  add rsp, 176;     jmp n2597_match_alternate_af
-  mov r14d, eax;    jmp n2597_match_alternate_s0
+  mov r14d, eax
+  add rsp, 192;     jmp n2597_match_alternate_s0
```

`_af` and `_s0` are ALTERNATE's **own retry wiring** — a self-edge, not a scope exit. Forcing `gin = 0` / `oin = 0` there emits a release for ζ-spine storage **nobody pushed**.

### Mechanism, end to end

RSP walks 176–192 bytes **up into the caller's frame**. A later `match_begin` then runs `push rbp; mov rbp, rsp` over corrupted ground, so its frame's `[rbp-8]` is not where the caller's r12 was saved. The r12 restore — `mov r12, qword ptr [rbp + -8]`, which is the **only** absolute write to r12 in emitted code besides the single pinned-VA load `mov r12, [0x70000000]` at `main` (censused: 50 restores, 1 init, everything else relative `add`/`sub`) — then reads a slot that never held r12.

Result: `r12 = 0` at `mov qword ptr [r12 + 0], rcx` in `n2218_match_assign_cond_α`, **with the pinned VA still holding a valid pointer** — clobbered, not uninitialised, exactly as the row's brief had narrowed it. gdb confirms the fault site and `r12 0x0`; the backtrace beyond frame 0 is `?? ()` noise, since these are jump-wired blobs and not call frames — which is why the asm diff, not gdb, is what named it.

## 3. THE CURE — AND WHY IT IS NOT A BLIND REVERT

The brief explicitly forbids a blind revert: *"822bc8a1 was a FIX for something. Find what it repaired, keep that."* Both hunks were tested separately.

| hunk | what it does | disposition | why |
|---|---|---|---|
| 1 — gin/oin self-edge suppression | forces `gin=0`/`oin=0` when γ/ω targets the arm's host | ⛔ **DROPPED** | sole cause of the spurious release; dropping it **alone** cures the crash |
| 2 — `_wzdepth = zarm[i] >= 0 ? zout[i] : zd` | arm-relative depth instead of the outer linear accumulator | ✅ **KEPT** | repaired a measured pred-disagreement WALL (`SCRIP_ZD_DEPTH=1`: 8 preds `0/0/0/0/16/32/48/48` → zero disagreement); not implicated |

⭐ **Hunk 1 has no current beneficiary and one measured victim.** Its intended beneficiary was the `IR_DISJUNCTION` arm path — and that landed **separately** at `0e57de3b` via the `fc_geom` flat-cell grant, which does not populate `zarm[]`. So dropping it is evidence-based, not reflexive.

## 4. VERIFICATION — RE-RUN **AFTER** THE REBASE, PER s270's OWN LESSON

⛔ First measurement was taken at `0e57de3b` + revert. A `pull --rebase` then brought in **`94dd91ba`** — a corpus path-flattening sweep that removes the `programs/` level and rewrites 200+ path references. That is precisely the **measure-then-rebase publishes a stale board** trap s270 recorded, and it would have made the commit message certify a tree that never existed on origin. **The entire board was re-run on a `make pristine` build at the merged HEAD before this FINDING was written.** Numbers were identical either side.

**At SCRIP `9df28b03`, `make pristine`, `RT_OPT=-O0`:**

| check | result |
|---|---|
| `test_corpus_snobol4.sh` m3 | ⭐ **PASS=364 FAIL=0** |
| `test_corpus_snobol4.sh` m4 | ⭐ **PASS=364 FAIL=0 SKIP=0** (364 total) |
| `TDump_driver` m3 / m4 | rc=0, **byte-equal to `TDump_driver.ref`** in both |
| gates | `emit_no_lang` · `template_medium_invisible` · `bb_one_box` · `rtx_unit` · `no_handencoded_bytes` · `audit_m3_native_binary_arms` — **all rc=0** |
| vlist ladder | `v01`–`v05` + controls `c01`/`c02` PASS in m3 (unchanged) |

⛔ **TAIL NAMED, NOT BURIED:** `v05` still SIGSEGVs in **m4** while passing m3 — an m3 ≢ m4 divergence, **unchanged by this commit**, its own open row `vlist-v05-m4-sigsegv-m3-m4-divergence`. **364/364 does not mean selection expressions are finished.**

## 5. ⭐ THE TRANSFERABLE RULE

**`822bc8a1` certified itself on *"SNOBOL4 crosscheck 325/325 both modes."* Its victim, `TDump_driver`, lives in `beauty_suite` — outside crosscheck.**

An inertness claim verified on a corpus that **excludes the affected program** is not verified. Stated generally, and this is the half worth carrying:

> ⭐ **"Inert for all current callers" is a claim about the CALLER SET, and it must be checked against whoever actually populates the gate.** Here the gate's *sole populator was the sole victim* — the fact that made the change look safe (only one op reaches it) is the same fact that made it dangerous (that one op is the only one it can break).

Two supporting notes:

- ⛔ **`beauty_suite` carries no checked-in `.s` artifacts at all** (0 files), so the drift sweep that catches this class elsewhere could not have caught it here either. Two independent blind spots over the same directory.
- ⭐ **Artifact regen conflates drift with change, so measure the split.** RULES.md step 4 regen produced churn across many Icon programs and 2 Snocone files. Emitting 5 of them under a purpose-built `0e57de3b` worktree vs the cured build gave **0 of 5 different** — the churn is **pre-existing drift** from three codegen commits that were never regenerated, *not* this change. This revert affects only ALTERNATE arms with host self-edges, and no checked-in artifact program has that shape. ⛔ Without that check the regen commits would have read as "the cure rewrote Icon codegen."

## 6. BOARD LINE TO CARRY FORWARD

**SNOBOL4 #1 — `m3 364/364 · m4 364/364 · SKIP=0` on `main` at SCRIP `9df28b03`, pristine `-O0`. Zero known reds.** The next SNOBOL4 correctness work is the named tail (`v05` m4), not a corpus failure.
