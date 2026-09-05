# FINDING 2026-09-05 hq_C — a flat alternation leaves 32 live bytes on the γ path that the ζ-depth model never counted, and the outer capture reads its own operand's cell

**Row:** `snobol4-outer-capture-over-a-group-containing-a-pattern-valued-variable` (QUARTET #2, ceo 21:37).
**Cure:** SCRIP `src/emitter/emit.cpp` — the `_xh` producer→consumer hop loop now adds a flat alternation's 32 live bytes.

## THE DEFECT, IN ONE PAIR

```
LIST = ",a"
LIST POS(0) "," (LEN(1) (BREAK(",") | REM)) . COMMON   SCRIP COMMON=[]   ORACLE COMMON=[a]  ⛔
LIST POS(0) "," (LEN(1)  REM             ) . COMMON   SCRIP COMMON=[a]  ORACLE COMMON=[a]  ✅
```

The two `[ZD]` traces are identical except at one node:

```
good:  r=7 i=11 IR_MATCH_REM       K=16 zout=48      capture i=12 zout=48   read = 48-32 = 16  ✅
bad:   r=7 i=11 IR_MATCH_ALTERNATE K=0  zout=32      capture i=12 zout=32   read = 32-32 =  0  ⛔
```

`IR_MATCH_ASSIGN_SAVE` (i=9, zout=32) is the capture's phase-0 half — it banks the group's start cursor.
`IR_MATCH_ASSIGN_COND` (i=12) is the phase-1 commit and reads that cell back through `ZOPD(1,0)`.

## WHY THE MODEL WAS WRONG — THE EMITTED CODE DISAGREES WITH `zd_k`

`bb_match_alternate.cpp` has two arms. The ALT-RBP arm (`cro = sn4_choice_rbp_off_nd()` non-zero) is
frame-resident and pushes nothing. The ALT-FLAT arm (`cro == 0`) emits `sub rsp, 32` at α and pops it
**only at `L(19)`, which is the ω path**. On the **γ path — the path the capture commits on — those 32
bytes stay live, deliberately**, because the choice record must survive for backtracking.

But `zd_k()` returned **0** for `IR_MATCH_ALTERNATE` unconditionally. So at run time `rsp` was 32 lower
than the compile-time depth said, and `[rsp+0]` at the commit was the alternation's own saved `r14d`
instead of the banked start cursor 32 bytes above it. Measured, before and after:

```
before:  n12_match_assign_cond_α:  mov eax, dword ptr [rsp + 0]     <- the alternation's own cell
after:   n12_match_assign_cond_α:  mov eax, dword ptr [rsp + 32]    <- the banked start cursor
```

`zd_k` already returns **32** for `IR_DISJUNCTION` with operands — the same "leaves a choice record live"
shape. The SNOBOL4 twin was the one that read 0.

## ⛔⭐ THE FIX THAT LOOKED RIGHT AND WAS NOT — `zd_k` IS NOT ALLOWED TO ASK THAT QUESTION

The obvious cure is to make `zd_k(IR_MATCH_ALTERNATE)` return 32 on the flat arm — and `zd_k` already has
exactly that shape for `IR_MATCH_ARBNO` (`emit_arbno_rbp() ? 32 : 16`), so it reads as the house idiom.
**It cures the witness and reds 18 master entries.**

The arm test has to consult `choice_frame_slot()` → `frame_slot_scan()` → `frame_slot_is_candidate()` →
`leaf_frame_member()` → **`zd_k()`**. That machinery already asks `zd_k` what a node's size is, so calling
it *from* `zd_k` closes a cycle. The compiler stack-overflowed **on its own ERROR 246** while compiling —
the same error number the defect produces at run time in `OR.sno`.

⭐ **That collision is the lesson worth keeping.** The regression announced itself as `ERROR 246 — stack
overflow` on ARBNO+alternation programs, which is exactly the symptom class this row was minted to fix.
A grader watching only the witness would have seen it go green; a grader watching only the error text
would have concluded the cure was incomplete rather than that a *new* recursion had been introduced in
the compiler. **The board is what separated them: 18 entries that were green before.** A cure whose
regression wears the same symptom as the disease cannot be graded by symptom.

⭐ Second, general: **an idiom is not a license.** `zd_k` could afford `emit_arbno_rbp()` because that is a
cheap global predicate; it could not afford `choice_frame_slot()`, a per-node scan that re-enters `zd_k`.
Copying the shape of a neighbouring line carries none of the reasoning that made the neighbour safe.

## THE CURE THAT HOLDS

The correction belongs where the code already corrects for bytes the depth model does not carry: the
`_xh` hop loop that walks from a consumer back to its operand's producer and already adds `+32` for the
consumer's own arm, `+16` per `IR_MATCH_DEFER`, `+64/+32` per `IR_MATCH_BEGIN`. One clause joins them:

```c
if (nodes[_zm]->op == IR_MATCH_ALTERNATE) { _xh += alt_flat_live_bytes(nodes[_zm]); continue; }
```

`alt_flat_live_bytes()` returns 32 only for the flat arm (`choice_frame_slot(nd) == 0 &&
sn4_choice_rbp_off() == 0`). This site runs inside the emit-drive loop where `g_emit_cfg` is built, so the
frame-slot query is legal here and recursive there. It fixes the read offset **without perturbing
`zd_out` for every node downstream of an alternation**, which is what broke ARBNO.

## WHAT THIS ROW'S EARLIER READINGS GOT RIGHT AND WRONG

- ✅ The measured mechanism — a clobbered banked **start** cursor, subject bases identical, end offset
  correct — was right, and survived two wrong attributions.
- ⛔ The row's TITLE ("a pattern-valued variable") is not the trigger; an alternation as the second element
  of a concatenation inside a captured group is. Corrected in the baton 2026-09-04 ~19:05.
- ⛔ The baton's NEXT said "start at `zd_k()` … and at how `zd_out` accumulates across the disjunction
  arms" and warned against curing in `bb_match_capture.cpp`. Both halves were right: `zd_k` **is** where
  the wrong number comes from, and the capture template is **not** where to fix it. The unstated third
  option — leave `zd_k` alone and correct the hop — is the one that holds.
- ✅ The write/read asymmetry (`ZRESD(0)` vs `ZOPD(1,0)`) is by design and is not the bug, as the baton
  said. Phase 0 and phase 1 are emitted at different nodes at different depths; the asymmetry is what
  makes them name the same cell.

## ⛔⭐ A CLAIM THIS FINDING FIRST MADE AND THEN KILLED

The first draft of this write-up said the cure "removed the m4 SIGSEGV on `fence_bal_rtab_branch_1` (+1 m4
pass)", on a clean one-run before/after pair: baseline `m4_crash=1`, cured `m4_crash=0`. **It was variance.**
Three runs of the same cured binary on the same tree:

```
run A:  m3_crash=1 (sig 6)    m4_crash=0         m3 1772 / m4 1773
run C:  m3_crash=0            m4_crash=1 (sig 6) m3 1773 / m4 1772
base :  m3_crash=1 (sig 6)    m4_crash=1 (sig11) m3 1772 / m4 1772
```

The entry aborts on `[ZHP] heap exhausted (512 MB, 0 blocks)`; which mode it kills is resource- and
load-dependent. On the merged tree it does not crash in either mode.

⭐ **A one-run before/after pair cannot distinguish a cure from a flake, and when the whole delta is a single
entry, flake is the likelier reading.** The pair had every property a good measurement is supposed to have —
same tree, same binary rebuilt from a stash, one variable changed — and it was still wrong, because the
*instrument* was noisy rather than the method. What caught it was two instruments disagreeing on one tree:
the blocking gate printed `m4 FAIL=1` minutes after my own board printed `m4_crash=0`. **Agreement between
two runs of one instrument is weaker evidence than agreement between two instruments.**

The corrected claim is the narrow one: on the merged tree `70f7b562e` the master is m3 1777/0/0 and m4
1777/0/0, FAIL=0 CRASH=0 both modes, and the *causal* evidence for this cure is the witness A/B
(`COMMON=[]` → `COMMON=[a]`, oracle `COMMON=[a]`), not any pass-count delta.

## SEPARATELY, AND NOT MY FIX: `make test`'s SNOBOL4 ARM WAS REFUSING FOR EVERY SEAT

`test_corpus_snobol4.sh` invoked the harness with `--modes m3,m4` and **no `--by-modes-column`**, so the
harness refused (rc=2, "28 entries declare modes=ast … would be EXECUTED and diffed against an AST dump")
before boarding a single program. That reds a blocking `make test` arm independently of any tree change —
no program is compiled, so no codegen change can cause or fix it, which is also how it was attributed.

⭐ I diagnosed this and added the flag locally, and **while I was measuring, the identical fix landed on
origin as `c9aff8472`** ("it could not produce a verdict at all, and the second population was going
ungraded"). My edit merged into it and left no diff of its own. Recorded here only so the diagnosis is not
re-derived a third time — the credit is that commit's. With it in place the arm boards and is green:
`mode-4 (--compile): PASS=1800 FAIL=0 SKIP=0`.

⭐ Worth noting for the class: this arm had been refusing rather than failing, and a refusal at the top of a
long blocking recipe is easy to read as "the suite is fine, the runner is fussy". It is the same shape as
the `make test` no-recipe trap that this recipe was built to replace — the difference between *not graded*
and *graded green* is invisible unless someone reads the arm's own output.
