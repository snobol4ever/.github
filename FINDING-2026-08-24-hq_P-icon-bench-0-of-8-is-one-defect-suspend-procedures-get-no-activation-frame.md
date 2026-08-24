# FINDING hq_P s269 — ICON `bench_correct` 0/8 IS **ONE DEFECT**, AND IT FITS IN FOUR LINES: A PROCEDURE CONTAINING `suspend` IS EMITTED WITH **NO ACTIVATION FRAME**

**Session:** s269 (2026-08-24) · **seat:** `hq_P` · **mode:** FLEET-4 · **row:** `icon-bench-correct-zero-of-eight` (rank 0 on Lon's order — *"Let's get all the Icon benchmarks running, make that a priority"*)
**Trees:** SCRIP `5ad95ab1` (harness cure landed here) · oracle `/home/resources/icon-build/bin/{icont,iconx}`, **verified present before any red was believed**
**Kin:** `FINDING-2026-08-24-hq_P-three-instruments-that-cannot-express-their-own-outcome.md` (the harness cure is a fourth of that class) · row `icon-n2-generator-activation-frames` — ⭐ **the cure below is that rung, already designed**

---

## THE HEADLINE

**There are not eight Icon benchmark failures. There is one defect with eight witnesses, and not one of them is a wrong answer.**

```icon
procedure gen()
   suspend 1;
end
procedure main()
   write(gen());
end
```

**SIGSEGV. Mode 3 and mode 4 identically** (so the m3 ≡ m4 invariant holds — this is not a medium bug). The oracle prints `1`. Replace `suspend 1` with `return 1` and it prints `1`. Drive a built-in generator instead — `every i := (1|2)` or `every i := 1 to 3` — and it works. **The defect is `suspend` in a user-defined procedure, and it fires on the first call.**

## HOW 0/8 WAS BEING MISREAD, AND WHY THAT COST DIRECTION

The board reported six rows as `DIVERGE` — a **wrong-answer** verdict. It was wrong about every one. Measured after repairing the instrument (SCRIP `5ad95ab1`, committed separately):

| program | was reported | **is actually** | good lines before death |
|---|---|---|---|
| `concord` | DIVERGE 0 vs 1345 | **SIGSEGV** | 3 |
| `geddump` | DIVERGE 0 vs 12568 | **SIGSEGV** | 0 |
| `ipxref` | DIVERGE 0 vs 1230 | **SIGSEGV** | 0 |
| `tgrlink` | DIVERGE 0 vs 3239 | **SIGSEGV** | 2 |
| `rsg` | DIVERGE 4893 vs 5000 | **SIGSEGV** | ⭐ **5000 — byte-identical to the oracle** |
| `micsum` | DIVERGE 0 vs 2 | **HANG** (non-termination) | 1 |
| `deal` | RUNAWAY | RUNAWAY (correct label) | — |
| `queens` | RUNAWAY | RUNAWAY (correct label) | — |

⭐ **`rsg` is the tell, and it was hiding in plain sight as the least-broken row.** It produces **all 5000 lines, `cmp`-identical to the oracle**, and then segfaults while generating line 5001. It was booked as `4893 vs 5000 DIVERGE` — a near-miss wrong answer, the kind of row a fixer would chase with a diff. It is nothing of the sort: it is a **correct program that does not stop**, which is the same family as the two RUNAWAYs.

⛔ **Two harness bugs combined to produce that false picture** (both cured in `5ad95ab1`): `scr_rc` was captured and never read, so a crash fell through the verdict ladder to `DIVERGE`; and stdout is a **pipe**, so libc block-buffered it and an abnormal death **discarded the buffer** — which is how a program that printed 5000 correct lines was recorded as printing 0. ⭐ Same class as the two instruments repaired in `e70f1743`: **an instrument that cannot express one of its own outcomes reports the wrong one confidently.** The cost was not accuracy but *direction* — `DIVERGE` sends you to diff outputs; the work is a crash.

## THE ROOT CAUSE, BY ASM-DIFF (RULES.md order, no gdb needed to see it)

Ablate to the minimal pair — same program, one ingredient changed — and diff the emitted `.s`:

```
=== return 1  (WORKS) ===              === suspend 1  (SIGSEGV) ===
FN__gen:                               FN__gen:
    sub  rsp, 80                       gen_α_body:
    mov  rdi, rsp                          lea  rax, [rip + n1_suspend_β]
    mov  esi, 0                            mov  [rsp + 32], rax
    mov  edx, 0                        n0_lit_integer_α:
    call rt_icn_zframe_args_install        mov  r11, 1
gen_α_body:                                mov  [rsp + 16], 3      # result tag
n0_lit_integer_α:                          mov  rax, [rip + .Lx2_0]
    sub  rsp, 16                           mov  [rsp + 24], rax
    ...                                    jmp  n1_suspend_α
```

**The `suspend` version carves no frame at all.** No `sub rsp`, no `rt_icn_zframe_args_install`. Yet its body addresses frame-relative slots `[rsp+16]`, `[rsp+24]`, `[rsp+32]` exactly as if one existed.

Those slots are not free. The caller (`n5_proc_gen_α`) pushes the {γ, ω} port pair immediately before entry, so on arrival **`[rsp+0]` = γ and `[rsp+8]` = ω**. The body writes its result descriptor at `[rsp+16]`/`[rsp+24]` — already past the pair — and then the suspend box copies it *down onto them*:

```
n1_suspend_α:   mov  r11, 2
                lea  rax, [rip + n1_suspend_β];  mov [rsp+32], rax
                mov  rax, [rsp+16]  ; 3  (the integer tag)
                mov  [rsp+0], rax   ; ⛔ overwrites γ
                mov  rax, [rsp+24]  ; 1  (the value)
                mov  [rsp+8], rax   ; ⛔ overwrites ω
                jmp  gen_γ
gen_γ:          add  rsp, 0
                mov  eax, 2
                ret                 ; ⛔ returns to [rsp+0] == 3
```

**`ret` jumps to address `0x3`.** Observed exactly: `rip 0x3`, `r11 0x2` (the value `n1_suspend_α` had just set), backtrace `#4 n1_suspend_α`. The other witnesses show the same signature from other angles — `concord` and `tgrlink` die at `rip` = `0x2`/`0x3`; `geddump` dies inside `n219_proc_gen_β`, the **β (recede) port of a generator procedure**; `ipxref` dies in `rt_gc_visit_descr` under `gc_zeta_frame`, the **conservative ζ-frame scanner walking a frame whose contents are not what it believes**. Small integers standing where code addresses belong, in every case.

⭐ **Where the emitter decides.** `emit.cpp:2781` emits a prologue only when `g_emit.zframe_graph` is set, and `:2783` only when `g_emit.flat_lcl_proc` is. A generator procedure is marked by `flat_gen` / `g_gen_proc_active` (see the `_legacy` predicate at `:2830`) and satisfies **neither**, so it falls through both arms and is emitted frameless while its body still uses frame-relative addressing. **That mismatch is the whole bug.**

## THE CURE IS ALREADY DESIGNED — IT IS RUNG N-2

⛔ **Do not open a new cure row.** `icon-n2-generator-activation-frames` (QUEUE rank 0, **FREE** — seat13 stood down under the FLEET-16→4 cap, *suspend not cancel*) is precisely this: *generators become R-4(b) activation frames + law 0a′ (α push rbp/carve; γ-SUSPEND retains frame+pair and builds the resume record; β re-entry restores rbp through the record; ω-exhausted = FRETURN retire)*. Its hard prerequisite — routing the raw flat-spine operand coordinates through ZOPQ — **is done and pushed** (seat13, SCRIP `73f1a3c7`). Its baton estimates ≈10–11 of the 16 m3 rung fails; **this FINDING adds that it is also the whole of `bench_correct`, the heaviest single Icon lever at weight 15.**

⭐ **What this FINDING gives N-2 that it did not have: a four-line witness.** The rung was scoped against rung-suite counts. It can now be driven against a program that fits on a screen, crashes in both modes, and needs no corpus, no oracle, and no link deps to reproduce. Cure that, then re-run `bench_correct`.

## RECEIPTS

```
oracle preflight   /home/resources/icon-build/bin/{icont,iconx}  PRESENT (checked before any red was read)
minimal witness    p1.icn 4 lines   m3 rc=139 SIGSEGV · m4 rc=139 SIGSEGV   (oracle: prints 1)
control            return 1         m3 prints 1                             (defect is `suspend`, not procedure calls)
control            every i := (1|2) / 1 to 3   both print correctly         (defect is USER generators, not generators)
rsg identity       cmp orc.w scr.w  ⭐ BYTE-IDENTICAL for all 5000 lines, then SIGSEGV on 5001
board after cure   5 CRASH · 1 HANG · 2 RUNAWAY · 0 DIVERGE   (bench_correct still 0/8 — labels became true, nothing was scored green)
```

⛔ **No board was run beside a build** (s268 VOID-THE-WHOLE-RUN discipline); the harness ran standalone against a settled tree.

## ROUTED

- SCRIP `5ad95ab1` — the harness cure (CRASH/HANG/UNPROVEN verdicts + `stdbuf -o0` + runtime stderr captured).
- Baton `tasks/icon-bench-correct-zero-of-eight.task.md` — rewritten to the true class and pointed at N-2.
- `ceo` — reported, with the one line for Lon.
