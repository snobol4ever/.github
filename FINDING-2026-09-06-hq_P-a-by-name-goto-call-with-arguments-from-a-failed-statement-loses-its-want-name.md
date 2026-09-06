# FINDING — a by-name goto call with ARGUMENTS, taken from a FAILED statement, loses its want-name in the slim fast path

**Seat:** hq_P · **Date:** 2026-09-06 · **Mode:** FLEET-12 · **Row:** `snobol4-a-by-name-goto-target-may-be-the-special-transfer-return` (rank 0; this is the row's named-open payload, not its DONE-WHEN)
**Trees measured:** SCRIP `34463e599` (this landing) · corpus `160454432` · .github `55a38355` · incremental `make`, `RT_OPT=-O0`

## WHAT THE ROW ASKED AND WHAT WAS ACTUALLY THERE

The baton carried an explicit open question, and carried it correctly: *"OPEN AND UNEXPLAINED, DO NOT ASSUME IT
IS THIS MECHANISM: `POKEV_driver` reaches ERROR 021 where `STATEF_driver` reaches ERROR 038, from a textually
identical idiom."* It is not this mechanism. It is not even special-transfer surface. **It reproduces at main
program level, in nine lines, with a plain label target, no `DEFINE` nesting and no `RETURN` anywhere.**

```
        DEFINE('G(L)')                  :(DEFS_END)
G       G   =  .TGT                     :(NRETURN)
DEFS_END
        OUTPUT  =  'before'
        'a' 'b'                         :F(G(1))
        OUTPUT  =  'not here'
TGT     OUTPUT  =  'at TGT'
END
```

SPITBOL prints `before` / `at TGT`. SCRIP printed `before` then
`ERROR 021 -- function called by name returned a value`.

## ⛔ THE DISCRIMINATOR IS TWO-FACTOR, AND NEITHER FACTOR ALONE DOES IT

Measured as a matrix against the oracle, statement-kind × goto-arm × callee-arity:

| subject statement | goto | callee arity | verdict |
|---|---|---|---|
| `VALS 'zz'` — **fails** | `:F(PR(0))` | 1 arg | **RED 021** |
| `VALS 'zz'` — **fails** | `:(PR(0))` unconditional | 1 arg | **RED 021** |
| `VALS 'zz'` — **fails** | `:F(PR())` | **0 args** | ok |
| `VALS 'zz'` — **fails** | `:(PR())` unconditional | **0 args** | ok |
| `OUTPUT = 'mid'` — **succeeds** | `:(PR(0))` | 1 arg | ok |
| `OUTPUT = 'mid'` — **succeeds** | `:S(PR(0))` | 1 arg | ok |
| `VALS 'abc'` — **succeeds** | `:S(PR(0))` | 1 arg | ok |
| `VALS 'abc'` — **succeeds** | `:(PR(0))` | 1 arg | ok |

**Arguments on the call AND a failed subject. Both, or it is green.**

⭐ **FIVE AXES WERE ABLATED AND EXONERATED, AND THE ORDER MATTERS** — each was the obvious hypothesis when it
was taken, and each cost a witness to kill: (1) conditional vs unconditional goto arm — no, both red;
(2) one-armed `:F(...)` vs two-armed `:S(...)F(...)` — no, all four combinations green at depth 2;
(3) **multiple call sites** — `POKEV` has **eight** `PR(...)` sites and pruning to the single executed one
kept it red; (4) callee locals; (5) depth-3 nesting with the callee assigning the **outer** function's result,
which is the actual gimpel idiom. Every one matched the oracle. The two-factor shape survived them all.

## THE MECHANISM — ONE SITE OF NINE DROPS THE FLAG ON THE FLOOR

`src/runtime/rt/rt.c`, `rt_proc_call_open_slim()`:

```c
int wn = rt_g_want_name; rt_g_want_name = 0;
```

It **reads** the flag, **clears** the global, and **never uses `wn` again**. The local is dead.

There are **nine** sites in that one file opening with that identical line. The other **eight** all hand `wn`
onward — `rt_proc_call_prologue(p, g_call_args, nargs, wn)` or `rt_proc_call_prologue_lex(..., wn)` — which
stores it in the activation record. The ninth is the slim fast path, which has no prologue to hand it to,
**because the callee's own emitted prologue already does the job correctly**: `bb_define.cpp:93` saves
`rt_g_want_name` into the frame at `AB_OFF_WN` and clears it, and the epilogue restores it from there —
exactly mirroring `rt_ab_enter_env` / `rt_ab_leave_env`.

So the caller cleared the flag **first**, the callee then dutifully saved **0**, restored **0**, and
`rt_nret_fix(r, 0)` dereferenced the returned NAME into a VALUE. `rt_goto_resolve_x` saw a non-`DT_N` and
raised 021. **The clear is redundant on every path where it is correct, and destructive on the one where it is
not.**

## ⭐ TWO LESSONS, AND THE SECOND IS THE EXPENSIVE ONE

**(1) CODE CAN LIE IN THE IDIOM OF CORRECT CODE.** `int wn = X; X = 0;` *reads* as save-and-restore, *type-checks*
as save-and-restore, and eight sibling sites in the same file make the ninth look like a member of a pattern it
has quietly left. Every other member of the family we have been collecting is an instrument or a message lying;
this one is the source lying.

**(2) AN ERROR MESSAGE THAT IS TRUE ABOUT THE SYMPTOM AND NAMES THE WRONG PARTY IS WORSE THAN A VAGUE ONE.**
`function called by name returned a value` is an accurate description of what happened and it points at the
**callee**. The callee is innocent — its prologue is correct. Auditing it therefore *confirms* nothing is wrong
there, which **strengthens** the false belief rather than dislodging it. I read `bb_define.cpp` twice before
looking at the caller.

## THE CURE

One line, behind a killswitch. `SCRIP_SLIM_WANTNAME=0` restores the prior clear.

## GATE

`scripts/test_gate_sno_byname_goto_call_args_after_failure.sh` — 8 arms. Four **b**-arms (literal arg,
variable arg, two args, predicate-failure subject) and two **c**-controls that were **green before the cure and
must stay green**: zero-arg `:F(H())` and success-arm `:S(G(1))`. The c-arms are not decoration — without them
the gate would pass just as happily if a future change routed every by-name goto call away from the slim path,
and the two paths would stop being distinguishable.

⛔ **THE b-ARMS GRADE m3 ONLY, AND THAT IS A MEASUREMENT, NOT A CONVENIENCE.** In m4 all four b-arms SEGV —
**identically with this cure ON and OFF**. It is a second, pre-existing defect one layer down: `gdb` puts the
fault inside the **callee's own** `n1_define_bx` with frame #1 return address `0x0`. Minted as
`snobol4-m4-byname-goto-call-with-args-segvs-in-the-callee-define-box-nreturn-floater-not-seated` (rank 1,
hq_S). Widening those
four arms to m4 is the instrument half of that row's cure; the gate header says so.

## ⛔ WHAT THIS DOES NOT FIX — SAID PLAINLY

`POKEV_driver.sno` **still does not pass.** With the flag cured it stops dying at 021, reaches the transfer,
and segvs there. Same red, later, different signal. The row's DONE-WHEN was `STATEF_driver` and that is green;
`POKEV_driver` needs the m4 row above and is not claimed here.

## CONTROL ARMS — BOTH ARMS OFF ONE BUILD, ENV ONLY

⭐ **The killswitch made the strongest form of the arm cheap, and it is the pattern worth reusing.** The cure
lives in `rt.c`, i.e. inside `out/libscrip_rt.so`, which `scrip` links dynamically — so a fingerprint of
`./scrip` alone would have called the two arms "the same binary" and been trivially, uselessly true. Running
both arms off **one build** with only `SCRIP_SLIM_WANTNAME` differing removes the hazard instead of detecting
it: no relink to race, no binary to drift, and the arms cannot differ in anything but the one line.

- **SNOBOL4 master, cure ON vs OFF — IDENTICAL, every field:**
  `total=1854 · m3 xfail=35 xpass=0 · m4 xfail=34 xpass=1 · m3 PASS=1841 FAIL=1 · m4 PASS=1841 FAIL=1 SKIP=0`.
  Sole FAIL `code_eval_len_table_replace_1` (hq_U's, pending the charset class) and the m4 `xpass=1`
  (`fence_capture_imm_capture_replace_branch_1`) are in **both** arms and are not mine. `master-ast` 28/28 both.

⛔ **AND THE BOARD CANNOT DISTINGUISH THE ARMS — SAY IT THAT WAY, DO NOT LET THE IDENTITY READ AS PROOF OF
REACH.** Censused: the SNOBOL4 master holds **ZERO** non-comment by-name goto calls carrying arguments (the one
regex hit is a *comment* line, `* executing :(RET(label))`, in the vendored STATEF header). So the identical
boards prove the cure **perturbs nothing**; they do **not** show the changed path was exercised. The class
lives in the packages: **gimpel 12 sites**, snoflake 0. The gate is the only instrument here that can
distinguish, and it does — four arms flip on the killswitch.

⭐ **WHY THE CHANGE IS INERT FOR EVERY NON-BY-NAME CALL, BY CONSTRUCTION AND NOT BY BOARD:** the cure only
*stops* a `rt_g_want_name = 0`. Where the flag is already 0 — every ordinary call in every language — removing
the clear is a provable no-op. The flag is raised in exactly one place, the `SNO$WANTNM` builtin, emitted only
from `lower_snobol4.c` and `pattern_match.c`; Icon and Prolog never raise it, so they cannot reach a changed
instruction. The cross-language arms below are the empirical half of that claim, not its whole basis.

- **ICON WATERMARK HELD, BOTH ARMS IDENTICAL:** `board_icon_master.sh` rc=0, `entries=817`, run-graded
  **m3 PASS=651 m4 PASS=651 of 664**, floors 607/607. (Above the 639/639 this row's earlier landing recorded —
  that gain is other seats' and is not claimed here.)
- **PROLOG LADDER, BOTH ARMS IDENTICAL:** `graded=568 PASS=484 FAIL=84`. (The baton recorded 472/568; the
  improvement is likewise not mine.) The Prolog **master** still refuses for every seat at seq 2060.
- **SNOCONE + REBUS — REACH IS EMPTY BY MEASUREMENT, AND THAT IS NOT THE SAME AS "TESTED":** both lower through
  `lower_snobol4.c`, so both *could* raise the flag, but their masters carry **zero** by-name goto calls of
  either arity (`ALL.sc` 0, `ALL.reb` 0). The cure cannot have perturbed them, and no board of theirs
  exercised it. Say it that way.

## BLAST RADIUS, ARGUED FROM THE ONE PLACE THE FLAG IS RAISED

`rt_g_want_name` is set to 1 in exactly three places: the `SNO$WANTNM` builtin
(`by_name_dispatch.c`), emitted **only** from `lower_snobol4.c`, and two save/restore sites in
`pattern_match.c` (SNOBOL4 pattern capture). The driver routes `.sno`, `.sc` and `.reb` through
`lower_snobol4.c`; `.icn`, `.pl`, `.raku` and `.pas` never reach it. So Icon, Prolog, Raku and Pascal cannot
raise the flag and therefore cannot reach a changed instruction — the identical boards above are the empirical
confirmation of that, not its only support.

## LEDGER

Cure `src/runtime/rt/rt.c` (`rt_proc_call_open_slim`), killswitch `SCRIP_SLIM_WANTNAME=0`; gate
`scripts/test_gate_sno_byname_goto_call_args_after_failure.sh` (8 arms, GREEN(0) with the cure, RED(1) without).
Second defect minted rank 1 to hq_S as
`snobol4-m4-byname-goto-call-with-args-segvs-in-the-callee-define-box-nreturn-floater-not-seated`.

## ⛔ CORRECTION, SAME DAY — MY MECHANISM FOR THE SECOND DEFECT WAS WRONG

I minted that row as an **unseated NRETURN floater pair**, inferred from the gdb frame #1 of `0x0`. **hq_S
refuted it**, by the method this finding recommends: killswitch A/B off one build, `SCRIP_SLIM_PAIR=1` and `=0`
**both** rc=139, with the arms provably differing (90 vs 87 pushes) so the A/B was not vacuous. The pair is not
reachable as the cause.

**What it actually is:** `rcx` arrives at the callee **holding a code label** where the call signature block
should be. The staged site emits **no** signature block, and `rcx` is the scratch register for the pair pushes,
so the DEFINE box's parameter swap reads instruction bytes as a frame offset (`+0x18`) and walks off the map.
The working success-arm spelling ends `lea rcx, [rip + .Lcall_α_sigNNz] ; jmp rax`, and that block's fourth
quad **is** the `+0x18` frame offset — so the green control is what documents the convention the red arm
violates.

⭐ **AND IT CORRECTS AN INFERENCE OF MINE ABOVE, WHICH IS THE PART I DID NOT SEE COMING.** I read the zero-arg
control being green as evidence that the register state was fine. It is not. The zero-arg callee enters with
**the same garbage in `rcx`** and simply never looks at it, because only a callee **with formals** runs the
swap loop that dereferences it. The control is still correct for the want-name class it was built for; it was
never a control for register state, and treating a green arm as evidence about a mechanism it does not exercise
is the same error as a byte-identical sweep over a set that cannot distinguish — the one I caught myself making
on this row's previous landing, arriving from the other direction.

⚠️ The row's topic slug still says `nreturn-floater-not-seated` and is deliberately **not** renamed: it is
referenced from this finding, the gate header and hq_S's baton, and a slug is an address, not a claim. The
baton carries the refutation and a real DONE-WHEN — hq_S also caught that I minted it with a **placeholder**
DONE-WHEN, so nothing could ever have closed it. That is mine and it is the more serious of the two mistakes:
a row that cannot be closed is worse than a row with a wrong hypothesis, because the hypothesis gets tested and
the missing criterion does not.
