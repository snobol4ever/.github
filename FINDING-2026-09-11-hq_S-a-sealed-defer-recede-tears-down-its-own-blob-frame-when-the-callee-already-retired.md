# FINDING 2026-09-11 hq_S — a sealed DEFER's recede tears down its OWN blob frame when the callee has already retired

**Row:** `snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries` (claimed by hq_S 2026-09-11 under CEO-546, which
re-opened SNOBOL4 for this seat and named the snobol4-master **16 CRASH + 8 HANG** class as UNASSIGNED).
**Tree:** SCRIP `1493214e4`, corpus `2e98e16ad`, .github `1673c785e`. `RT_OPT` = `-O0` (read from `Makefile`, never typed).
**Build graded on:** incremental `make` (HQ-27 per-landing pristine is VOID, RULES.md:118).
**Determinism:** every measurement below is under `setarch -R`. This family is ASLR-bimodal; a census without it is a
sample, not a measurement (hq_T's correction of 2026-09-06 stands).

## What was measured, not assumed

The class is **8 distinct CRASH programs and 4 distinct HANG programs** (×2 modes = the 16+8 on the board), read out of
the progress database at the coo's board tree `a1c6c96be` — not re-run here (ONE RUNNER, ONE BOARD, CEO-523):

    CRASH  arbno_bal_tab_replace_branch_1  arbno_fence_pos_replace_branch_2  arbno_fence_rpos_replace_branch_1
           arbno_fence_tab_replace_branch_1  arbno_span_tab_replace_branch_1  fence_arb_span_replace_branch_1
           fence_arb_tab_replace_branch_1  fence_arb_tab_replace_branch_2
    HANG   arbno_fence_span_replace_branch_2  arbno_pos_rpos_branch_81  arbno_span_break_replace_branch_1
           array_replace_branch_2

⛔ All twelve are marked `XFAIL` in `corpus/tests/snobol4/ALL.sno`. By the FACT RULE (RULES.md:214, Lon 2026-09-03
21:30) **there is no such thing as XFAIL and every one of them counts as a FAIL.**

## The witness, reduced by ablation

`fence_arb_tab_replace_branch_1`, minted standalone. Oracle `sbl -bf` prints `nomatch` rc=0; SCRIP is **rc=139 in m3,
5/5 runs**, and SIGILL in m4 (the same defect — m4 lands in a literal pool, m3 lands off the map):

          G0            =  FENCE(ARB)
          P             =  (*G0) . v1 TAB(2)
          'a b c' P RPOS(0)                          :S(OK)F(NO)

Each ingredient removed in turn, every arm measured (`scrip` vs `sbl -bf`), all under `setarch -R`:

| ablation | scrip | oracle |
|---|---|---|
| base (above) | **rc=139** | `nomatch` |
| `G0 = ARB` (drop FENCE) | `nomatch` | `nomatch` |
| `P = (*G0) TAB(2)` (drop the capture) | `nomatch` | `nomatch` |
| `P = (*G0) . v1` (drop the trailing element) | `match` | `match` |
| `P = (FENCE(ARB)) . v1 TAB(2)` (inline, no defer) | `nomatch` | `nomatch` |
| `*P` → `P` at the call site | **rc=139** | `nomatch` |

So the necessary set is **FENCE + a defer + a capture wrapping the defer + a following element**, and whether the
*statement's* reference is deferred is irrelevant. This confirms the s188 ingredient list and adds the last row.

## The mechanism (this is the part that was never root-caused)

`FINDING-2026-08-20-s188` and successors named this family "eleven fuzz SEGVs, four mechanisms" and left it there.
It is one mechanism, and it is a **frame torn down twice**.

The emitted shape, `--compile` (m4), pattern `P` compiled as blob `PAT$1`, `G0` as `PAT$0`:

1. `n33_match_defer_α` (the statement's defer) pushes the γ/ω continuation pair and enters the blob:
   `lea rcx,[L5]; push rcx; lea rcx,[L4]; push rcx; jmp *rax`. **Measured:** it pushes at `rsp=0x7ffffffee010`, so
   `PAT$1`'s frame base after its own `push rbp` is **`0x7ffffffedff8`**, with `[rbp+8]=L4`, `[rbp+16]=L5`.
2. Inside `PAT$1`, `n4_match_defer_β` — the recede of the *inner* defer `*G0` — is emitted from the
   **`op_seal == 1`** arm of `bb_match_defer.cpp:376-379`, which is an **unconditional callee-frame teardown**:
   `mov rsp,rbp ; pop rbp ; <omega>`.
3. But `G0` is `FENCE(ARB)`, and **the FENCE seal retires `PAT$0` before the recede arrives** — `PAT$0_ω` has already
   run `mov rsp,rbp ; pop rbp ; add rsp,8 ; ret`. There is no callee frame left. So step 2's teardown lands on
   **`PAT$1`'s own frame**: `mov rsp,rbp` with `rbp = 0x7ffffffedff8`, then `pop rbp` loads `PAT$1`'s *caller's* rbp.
4. Control then reaches `PAT$1_ω`, which tears the frame down a **second** time — `mov rsp,rbp` on the now-stale rbp.
   **Measured at `PAT$1_ω`: `rbp = 0x7ffffffee058`**, 0x60 above the real base, and the three words it reads as its
   frame header are the live **subject descriptor** of `'a b c'`:

       [rbp]    = 0x7fffffffe130   (main's rbp — reads plausibly, which is why nothing notices)
       [rbp+8]  = 0x500000002      (the descriptor's tag=2 / len=5 word, read as the γ continuation)
       [rbp+16] = 0x401b41         (the descriptor's STRING POINTER, read as the ω continuation)

5. `PAT$1_ω`'s `ret` therefore jumps to **`0x401b41`, which is `.Llit_string_α_78_0_s` — the bytes of `"a b c"`.**
   `0x61` (`a`) is `popa`, invalid in 64-bit ⇒ SIGILL. In m3 the same wild `ret` lands off the map ⇒ SIGSEGV.

Verified end to end by single-stepping the last 24 instructions and by a hardware watchpoint proving the cell at
`[rbp+16]` is **never written after `n32_match_begin` is entered** (`rsp=0x7ffffffee060` there) — i.e. nothing
corrupted the continuation; the ω exit simply read the wrong memory because its rbp was already gone.

## Why the capture is a necessary ingredient

The teardown is emitted the same way with and without the capture (`mov rsp,rbp ; pop rbp ; add rsp,16`, measured in
both `.s` files). The capture does not create the double teardown — it inserts `n3_match_assign_save_β` between the
sealed recede and `PAT$1_ω`, which is what routes the recede into the blob's ω on this path at all. Without it the
recede reaches ω only on paths where the callee frame is genuinely still resident.

## The cure surface, and why hq_S did not land it

The discriminator this arm lacks **already exists in the same function**, twelve lines below it: the non-sealed β arm
(`bb_match_defer.cpp:389-400`, under `SCRIP_DEFER_BETA_GUARD`, default on) tests the spine top before transferring —
`cmp qword [rsp],0 ; jne L12 ; mov rax,[rtccb+248] ; test rax,rax ; je L12 ; jmp rax ; L12: jmp qword [rsp]`. The
sealed arm has no such test and assumes a resident callee unconditionally.

⛔ **`bb_match_defer.cpp` is a Byrd box that Icon generators and Prolog backtracking both lower onto.** Under
SHARED-NODE VERDICT SCOPE the cure must be graded on every frontend that reaches it, and under ONE RUNNER, ONE BOARD
(CEO-523) hq_S cannot run the Icon or Prolog boards. A seal-protocol change proven only on SNOBOL4 is exactly the
shape of the `IR_DISJUNCTION` cure that cost 47 Icon programs. **The class is therefore routed with the mechanism
named rather than cured blind** — pattern-box surface is hq_P's by the lane rule, hq_U co-signs the shared node.

## What is NOT claimed here

- The 4 HANG programs are **not** proven to be this mechanism. They are in the same fuzz corpus and share the
  FENCE/ARBNO + defer shape, but no hang was traced in this sitting. Do not fold them in without measuring.
- A second family (`arbno_bal_tab_replace_branch_1`, `ARBNO(TAB(1) BAL)` under `ARBNO(*G0)`) was minted and its
  measurement did not complete inside this sitting. Its signature is **unconfirmed**.
- The three earlier FINDINGs' "four mechanisms" reading is superseded **only for the witness reduced above**.
