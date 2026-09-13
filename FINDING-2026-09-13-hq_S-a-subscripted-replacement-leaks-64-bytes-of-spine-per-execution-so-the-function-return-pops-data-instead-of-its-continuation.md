# A subscripted replacement leaks 64 bytes of ζ-SPINE per execution, so the function RETURN pops data instead of its continuation

**hq_S, 2026-09-13. Tree SCRIP `0f0ccd138` (hq_U's conditional r12 seed in), corpus `ef6aff5b6`, incremental `make`, `RT_OPT=-O0`.
Oracle `/home/resources/x64/bin/sbl -bf`. MODE NONET.**
⛔ **The cure is NOT in this seat's files and this FINDING lands no code.** ζ-SPINE lives on RSP and is CONCERN 3,
hq_U's; by the NONET guardrail a frame change is an ASK with the measurement, never a landing by me. What lands here is
the measurement and an unwired gate, handed over.

## THE CLASS

A match **with replacement** whose **subject is a subscripted reference** (an array element) leaks **exactly 64 bytes of
ζ-SPINE (RSP) every time the statement executes**.

The statement trailer's whack constant — `op_zgpop`, staged from `g_zd_gpop` (`src/emitter/emit.cpp:3439`) as stamped by
`zd_plan` (`src/ir/zeta_depth.c`), emitted on the single `X86H_JMP` gamma hook arm at `src/templates/x86/x86_asm.h:1910`
— does not account for the **four 16-byte value-stack slots** pushed by the store chain that exists **only** for an
indexed target: `var → call (rt_call_arr_bl, the SNO$NAME lvalue store) → var → assign_var`. For the six-line witness the
trailer whacks **96** where the spine stands at **160**.

## THE WITNESS, AND IT IS SIX LINES

```
        DEFINE('F()')                           :(F_END)
F       A<2>  LEN(1) . S1  REM . S2  =  S2  S1  :(RETURN)
F_END   A = ARRAY(2, 'ABC')
        F()
        OUTPUT = A<2>
END
```

`sbl -bf` prints `BCA` rc=0. SCRIP **SIGSEGVs rc=139 in BOTH modes.**

## TWO SYMPTOMS, ONE DEFECT — AND THE SECOND IS THE ONE THAT NAMES THE DEFECT

1. **Inside a function**: the RETURN box is `pop rcx; add rsp, 8; jmp rcx`. It is **byte-identical** to the passing
   control's RETURN (ASM-DIFF exonerates it), so it is not wrong — it is *reached with the spine 64 bytes deep*. Measured
   at the breakpoint: in the passing control `[rsp]` is `n6_define_bx+555` = `F_γ` and `[rsp+8]` is `F_ω`; in the witness
   both are `0x0000000200008b28`, a **descriptor half**, and the γ/ω pair sits at **`rsp+0x40`**. `jmp rcx` then jumps to
   that descriptor. The measured wild target is the same `0x200008b28` the fault reports.
2. **In a loop**: the drift is **monotonic**. RSP across five consecutive iterations, measured at the
   `match_replace` box: `…df70 → …df30 → …def0 → …deb0 → …de70` — **−0x40 each time, exactly**. At 400 000 iterations the
   program still survives; at 1 000 000 it exhausts the stack and prints `ERROR 246 -- stack overflow` where the oracle
   prints `SURVIVED 1000000`. **The error-246 guard fires CORRECTLY, on a bogus overflow.**

⭐ **Symptom 2 is what turns this from "a crash in a function" into a leak with a number**, and I nearly missed it: I
predicted accumulation, tested 200 000 iterations, saw `SURVIVED`, and wrote the prediction off as **failed**. It had
not failed — 200 000 × 64 B = 12.8 MB fits under the limit. **A monotonic leak tested below its threshold looks exactly
like no leak**, and the honest instrument was not the loop but the five-iteration RSP reading, which needs no threshold
at all. Where a symptom depends on a limit, measure the RATE, never the limit.

## THE ABLATION — FOUR CONTROLS, EACH GREEN ON THE BROKEN TREE

| arm | result |
|---|---|
| plain-**variable** subject + replacement, in a function | **PASS** |
| array element + **match only**, no replacement, in a function | **PASS** |
| array element + **plain assignment**, in a function | **PASS** |
| the **identical** replacement statement at **TOP LEVEL** | **PASS** |

So it is neither the array element nor the replacement nor the function alone: it is the **replacement store through an
indexed target**, and the activation is what makes the leak observable rather than what causes it.

⛔ **TWO STORIES I WROTE AND MEASUREMENT KILLED, recorded so nobody re-walks them.** (a) *An asymmetry:* `cas_mark` is
`push`ed onto RSP but read back from `[rbp-8]`, which reads as a leak — it is not, because `bb_match_begin` establishes
its own frame (`push rbp; mov rbp, rsp`) first, so the pushes land exactly at `[rbp-8..-32]` and the restore is correct,
**and the sequence is byte-identical in the passing sibling**. (b) *The RETURN edge:* the whack is 96 on a `:(RETURN)`
edge, so I took the RETURN edge to be the trigger. Putting a plain statement between the replacement and the `:(RETURN)`
moved the 96 onto an ordinary statement edge and the program **still crashed** — the shortfall is the replacement
statement's **own** whack, successor-independent.

⛔ **`record full` cannot be used on this witness** — gdb refuses at `0xc4` (AVX512) inside libc's `strstr`. An
instrument limit, recorded as one, not a result.

## WHY THE BOARD NEVER SAW IT — A COVERAGE GAP, NAMED

`corpus/tests/snobol4/ALL.sno` contains **ZERO** entries whose replacement subject is subscripted. That is why the
SNOBOL4 master reads clean while gimpel `PERMS_driver.sno` SIGSEGVs in both modes. **A green board is necessary, never
sufficient.** Adding a master witness is hq_S's suite-gap row and **waits on the cure** — a red entry in the master is
not a cure and must not land as one.

## WHAT THIS ACCOUNTS FOR, AND WHAT IT DOES NOT

- **`PERMS_driver.sno` (gimpel): ATTRIBUTED.** `PERMS.sno:16` is `FIRST_OP<K> LEN(1) . S1 TAB(K) . S2 = S2 S1` inside
  `PERMS_INIT`. Deleting that one statement from the inlined repro makes the crash vanish; deleting the `&ALPHABET` match
  that makes the array elements non-null (so the replacement never *succeeds*) also makes it vanish.
- **`ARC_driver.sno`, `IMAGE_driver.sno`, `PEEL_driver.sno`: NOT ATTRIBUTED and NOT CLAIMED.** All three SIGSEGV on this
  tree and **none of them contains a subscripted replacement**. ARC dies on its first `ASIN` call, which `ARC.sno:29`
  defines via `DEXP(...)` — a compiled-string fragment, the CODE family, and a separate row. IMAGE and PEEL die with
  **zero** output, i.e. during `-INCLUDE` load, which is a third shape. Three rows, not one.

## TWO STALE READINGS CORRECTED BY MEASUREMENT

- ⛔ The MODE line's **"the three snoflake SIGSEGVs that bypass the error-246 guard"** is **stale**. Every one of the 17
  snoflake programs ever recorded CRASH in `/home/resources/progress/results.tsv` was re-run on this tree: **zero
  SIGSEGV**, all 17 exit cleanly; only `kalah-opening-search` exits rc=1, an error and not a crash. **The live crash
  class in this lane is gimpel, and it is four programs, not three.**
- ⛔ The newest snoflake and gimpel rows in the progress database were measured on tree `05317a5fb`, which is **~60
  commits behind** origin HEAD. A row's age in hours says nothing about its tree.

## THE GATE, WRITTEN AND DELIBERATELY NOT WIRED

`SCRIP/scripts/test_gate_sno_subscripted_replacement_does_not_leak_the_spine.sh` — 11 witness-modes, **5s measured**,
refs cut from `sbl -bf` on every run with the oracle run twice and diffed against itself first. On this tree:
**PASS=8 FAIL=3**, the three reds being the witness in both modes and the leak arm, with all four controls green in both
modes — the fail-once shape proven in the direction that matters.

⛔ **It is NOT wired into `make test`, because it is RED and a red gate in the blocking set is a broken build.** It is
hq_U's to wire with the cure. ⭐ **ARM 2 is the leak arm and it is the one that must stay**: it asserts the invariant
(the spine does not drift) rather than the crash that motivated the row, so a cure that repaired only the function-return
symptom leaves it red. That is hq_U's own r12 lesson — *a gate written against a plane must assert the plane's invariant
at the site that establishes it, not the symptom that led you to it* — applied on purpose.
