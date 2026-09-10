# FINDING 2026-09-10 hq_U — a converted Icon error did not CONCEDE, so the scan family ran on a value it never produced

**Row** `icon-scan-match-box-hands-memcmp-a-bad-pointer-or-length-record-every-replace-12` (rank 0, hq_U, minted CEO-516).
**Tree measured** SCRIP `25e087f34` (cure landed; measured at `e6390409d`+cure, re-proven after the rebase) + the cure below · corpus `0fe51f37d` · `.github` `ab86158d` · RT_OPT=`-O0` · incremental `make`.
**Witness** `procedure_record_every_replace_12` in `corpus/tests/icon/ALL.icn` (205 lines, origin `rung36_jcon_errors`).

## What the row said, and what it actually was

The row names the symptom exactly: `n1537_scan_match_bx` hands `memcmp` a bad pointer. gdb on the mode-4 binary:

```
#0  __memcmp_evex_movbe ()
#1  n1537_scan_match_bx ()
#2  n1543_call_proc_staged_bx ()
rdi 0x7fffcda14070   rsi 0x0   rdx 0x4   r13 0x0   r14 0x0   r15 0x7ffff7ffd000
```

`rsi` is `r13 + r14` — the scan SUBJECT — and it is NULL. `bb_scan_match.cpp` is not the author of that state; it is the first box to dereference it.

## The minimal witness, and the ingredient that mattered

Two lines, both required, and the first is the one that does the damage:

```icon
procedure main()
   &error := -1;
   write("A ", image([] ? []) | "none");    # icont: none   SCRIP: list_2(0)
   write("B ", image(=[]) | "none");        # icont: none   SCRIP: SIGSEGV rc=139
   write("C done");
end
```

Drop the `&error := -1` and SCRIP is CORRECT in both lines — a clean `Run-time error 103 / string expected`, matching `icont` byte for byte. Drop the first `write` and `=[]` alone is CORRECT too. **The defect lives only on the error-CONVERSION path**, which is why every ordinary Icon program in the corpus walks past it.

## The cause: `core_icn_error` returns, and nobody was reading the answer

`core_icn_error(code, val)` (src/runtime/core/core.c) has two exits. With `&error == 0` it prints the traceback and `exit(1)`. With `&error != 0` it decrements the budget, records `&errornumber`/`&errortext`/`&errorvalue`, and — absent a `setexit`/`runtime_eval` jmp frame, which Icon never has — **RETURNS 1**. `core_icn_argtype_check` was `void` and discarded that 1, so `rt_scan_enter` walked on and installed a LIST as `&subject`: `VARVAL_fn` on a list descriptor yields a pointer, `scan_subj` takes it, and the scan proceeds. `[] ? []` then SUCCEEDS and returns the body's value, where `icont` fails.

⭐ **The error was RECORDED and the expression still SUCCEEDED.** `&errornumber` already read 103 while the program ran on. That is not "a missing check" — the check was there, correct, and firing; what was missing was anybody asking it what it said. **A guard whose return value has no caller is indistinguishable from no guard, and it is worse than none, because a census of guards finds it.**

## The same class was already cured once, in the family next door

`src/templates/bb/bb_to.cpp` carries the cure and the reasoning verbatim: *"core_icn_to_int_check hands back an int64 and cannot say 'this failed', so a converted error 101 came back as the integer 0 and seq("a") generated 0,1,2... Asking BEFORE converting lets the box CONCEDE, which is what &error converts an error TO."* The range family was fixed; the scan family was not, and nothing connected the two. ⛔ **A class cure that stops at the family where it was found leaves the class open under a different box name** — this is the same bug with `IR_SCAN_*` on the front.

## The cure — one shape, applied to the whole family (NO PER-OP FILTER)

1. `core_icn_argtype_check` returns `int` (1 = the error was converted and the caller must fail).
2. `rt_scan_enter` returns `{ptr = 0, len = 0}` on a converted 103 and installs nothing — `ptr` is never 0 on the success path (`if (!s) s = "";`), so 0 is an unambiguous sentinel.
3. Every scan box that argtype-checks concedes on it: `bb_gen_scan` (both `rt_scan_enter` sites) tests `rax` and takes ω; `bb_scan_{match,any,upto,many,find,bal}` test `eax` after the check and take ω.
4. The integer half of the same family, which the same run exposed one screen later: `bb_scan_{move,tab,pos}` gained the `core_icn_int_operand_ok` guard `bb_to.cpp` already uses. `bb_scan_pos` had **no** integer check at all and read `FRQ(op_sa + 8)` raw, so `pos("a")` answered 1.

## Measured, before and after — and the second face of the same bug

| | before (origin `d4929f63f`, hq_V's board) | after |
|---|---|---|
| `record_every_replace_12` on the Icon master | **CRASH** | **FAIL** (output mismatch) |
| the witness, m3 / m4 | rc=139 SIGSEGV at line 112 `=[]` | rc=1, runs to the end, m3 ≡ m4 |
| lines of the 533-line ref produced | 276 | 456 |

⛔ **The crash was not the only thing hiding behind it.** With the pointer cure alone the program stopped crashing and started HANGING — `"abcdef" ? (tab(0) & (while write(move("a"))))` looped forever, because `core_icn_to_int_check` returned the integer 0 for `move("a")` by exactly the mechanism above, and `move(0)` succeeds forever. One class, two faces, and the second was invisible while the first was live. ⭐ **A witness that grades only wrong-VALUE would have called both of these absent** — a SIGSEGV and an infinite loop each produce no wrong value at all.

## Control arms

- **Icon master board** (`board_icon_master.sh`, this tree): run-graded **756/759 both modes, CRASH=0 HANG=0**, ast-shape 153/153. Watermarks held; `PASS` count unmoved at 756 against hq_V's 756/758, over a denominator that grew by one when the corpus absorbed a new entry.
- **`procedure_every_alt_replace_4`** appears red on this tree and NOT on hq_V's. ⛔ It is **not** this landing: A/B'd with `git stash` as the only variable, the clean tree produces byte-identical output. It went red on a corpus ref re-cut between `726448e76` and `0fe51f37d` — named here rather than smoothed, and not attributed.
- **SHARED-NODE VERDICT SCOPE**: `grep -w` over `src/lower/lower_*.c` — `IR_SCAN` icon=8, `IR_SCAN_ENTER` icon=1, `IR_SCAN_{MATCH,ANY,UPTO,MANY,FIND,BAL}` icon=1 each, **no other frontend lowers to any of them**. `core_icn_*` is Icon-only by construction. SNOBOL4 control arm is the `make test` blocking set.

## What is still red in this witness, and it is NOT this row

The program remains FAIL on output: it is a 205-line probe of ~100 distinct error paths, and the surviving diffs are error-NUMBER and error-COUNT divergences (e.g. `set([]) ++ 'a'` answers a cset where `icont` raises 120; `&error` runs to -36 against the oracle's -49). Those are **the `&error := -1` shared-node class**, the second row CEO-516 assigned, and they are grading, not crashing. ⭐ The honest split: this row's cure moved the entry from CRASH to FAIL — **the crash class is closed, the conformance class is open** — and a receipt that claimed the program green would be claiming the second row on the first row's evidence.
