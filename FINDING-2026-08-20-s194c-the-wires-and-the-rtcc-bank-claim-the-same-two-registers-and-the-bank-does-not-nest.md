# FINDING — 2026-08-20 s194c (HQ, Fable 5, beauty lane solo) — ⭐⭐⭐ THE γ/ω WIRES AND THE RTCC BANK CLAIM **THE SAME TWO REGISTERS**, AND THE BANK IS A FLAT GLOBAL THAT **DOES NOT NEST**

**This is the architectural root of the M1 SIGSEGV** (`FINDING-…-s194b` bottomed out at *"r11 held `rtccb`"*; this finding says **why**). Measured at SCRIP `985dac3b`, RT_OPT `-O0`.

## 1. LON'S QUESTION, ANSWERED FIRST

> *"Also make `rt_proc_enter` an ASM function, not C."*

**It already is** — and has been. `src/runtime/rt/rt.c` defines it in **two `__asm__` blocks**, `:1595` (the active `ZC_FRAME == ZC_FRAME_RSP` arm) and `:1643` (the non-RSP arm), each `.globl rt_proc_enter`. The only C at that name is the forward declaration (`:786`, `:1692`). **There is nothing to convert; the conversion Lon remembers was already done.** What is wrong at that site is not its language — it is the register contract, below.

## 2. THE COLLISION, IN THE SOURCE

`bb_glue_flat.cpp:148` carries Lon's s12/s15 directive — *"use proper PASS-THRU glue using R10 and R11"* — with its rationale: *"registers are depth-immune BY NATURE and carry NO OFFSET."* So the Byrd-box wire contract is **γ = r10, ω = r11** (Lon s55: *"R10 and R11 for success and fail return address"*).

`x86_asm.h:12` declares the RTCC block: `extern uint64_t rtccb[32];` — *"slot layout per rtcc.h (R8=5, R9=6, **R10=7, R11=8**)"*, and `x86_asm.h:427/428/440/441` emit its writeback and reload:

```
bank:    mov qword ptr [rip + rtccb+56], r10      mov qword ptr [rip + rtccb+64], r11
reload:  mov r10, qword ptr [rip + rtccb+56]      mov r11, qword ptr [rip + rtccb+64]
```

⛔ **Two mechanisms own the same two registers.** RTCC claims r10/r11 as VM globals to be banked across every C boundary; the wire contract claims r10/r11 as the live γ/ω continuations of the activation. Both are correct in isolation; together, one must lose.

`rt_proc_enter`'s own asm shows the seam in six instructions — the RTCC inbound load fills r10/r11 with VM globals and the very next label overwrites both with the wires:

```asm
  movq rtccb@GOTPCREL(%rip), %r10
  movq 64(%r10), %r11        ; r11 := a VM GLOBAL
  movq 56(%r10), %r10        ; r10 := a VM GLOBAL
4:
  leaq 2f(%rip), %r10        ; ...immediately clobbered by the γ wire
  leaq 3f(%rip), %r11        ; ...and the ω wire
  jmp  *%rax
```

## 3. ⭐⭐⭐ THE BANK IS FLAT AND DOES NOT NEST — THAT IS THE BUG

`rtccb` is **one array, one slot per register, program-wide**. There is no stack of banks and no depth index. Emitted asm from a **three-line** program (`corpus/probe/m1eval/m1e_eval_defer1_ctl.sno`) — 6 r11 bank/reload sites in that one file:

```asm
  mov  qword ptr [rip + rtccb+56], r10     ; bank the γ WIRE
  mov  qword ptr [rip + rtccb+64], r11     ; bank the ω WIRE
  call rt_call_arr@PLT                     ; <-- the C call
  ...
  mov  r10, qword ptr [rip + rtccb+56]     ; reload
  mov  r11, qword ptr [rip + rtccb+64]     ; reload
```

⭐ **`rt_call_arr` is the exact frame at the top of the M1 backtrace** (`#9 rt_call_arr(fn="EVAL", nargs=1)`). The sequence that kills beauty:

1. The outer blob banks **its own γ/ω wires** into `rtccb+56` / `rtccb+64`.
2. It calls C: `rt_call_arr` → `EVAL` → `rt_call_named_proc` → **`rt_proc_enter`**.
3. `rt_proc_enter` runs its **own** RTCC inbound load and enters an **inner** blob, which banks **its** wires into **the same two slots**.
4. The inner activation returns; the outer blob reloads r10/r11 **and gets the inner activation's values** — or the bank pointer itself.
5. The outer blob jumps what it believes is its ω wire. `r11 = 0x7ffff49448c0` = **`rtccb`**. `rip` = `rtccb`. SIGSEGV, `rax=0`.

**A flat global bank cannot serve a re-entrant machine.** HQ-70 already convicted it for observability (*"a machine whose wires bank in a global cannot be observed safely"* — the standing argument for PF-2). This finding upgrades the charge from **observability to correctness**: the bank silently loses an activation's continuations whenever activations nest through C, and beauty nests through C on **every statement carrying an expression**.

## 4. WHY LON'S DIRECTIVE IS THE CURE, NOT A MITIGATION

> *"We were going to do PUSH \<fail_location\> PUSH \<succeed_location\> at the CALLEE."*

**A pushed pair nests by construction.** Each activation's γ/ω ride that activation's own frame; there is no shared slot to clobber, no bank to reload from, and no way for an inner activation to overwrite an outer one's continuations. It also makes the contract **explicit**: a push is a positive act that must be emitted, whereas today an `EXPR$` thunk entered from C gets its wires *implicitly* — which is precisely how nobody noticed that the C by-name road sets none at all (s194b §5).

⛔ The trade Lon named at s12/s15 is real and must be paid: registers are depth-immune, a stack pair is not. The landings must drop the pair, and the depth must stay symmetric on both arms.

## 5. WHAT LANDED THIS SESSION (SCRIP `985dac3b`, DEFAULT OFF)

`SCRIP_WIRE_STACK=1` implements the contract at the two authorities:
- **pass** `bb_glue_pass_wires_blob` → `lea rcx,<ω>; push rcx; lea rcx,<γ>; push rcx; jmp rax` ⇒ `[rsp+0]=γ SUCCEED`, `[rsp+8]=ω FAIL` — the **same order `SCRIP_SLIM_PAIR` already uses**, so this is one convention, not a second spelling.
- **exit** `bb_glue_wire_exit` → `jmp [rsp+0]` / `jmp [rsp+8]` (`x86_jmp_mem`, an **existing** encoder — nothing hand-encoded, and no scratch is needed at a point where `rax:rdx` already carry the result DESCR).
- **land** `bb_glue_wire_land()` → `add rsp,16` at all **12** γ/ω continuation labels of the **6** pass sites; the same 16 on both arms so the roads stay depth-symmetric.
- **NO NEW GLOBAL**: `bb_wire_stack_on()` reads `getenv` per emission (compile-time, not hot) — the `rt.c:2000` spelling. A `static int` cache would be file-scope mutable state.

**RECEIPTS:** off arm **0 movers / 80** crosscheck programs (md5 of `--compile` output, A/B against the stashed tree, identical FAIL row both sides); gates `emit_no_lang` · `template_medium_invisible` · `icn_no_stack` green.

## 6. ⛔ THE ARMED ARM HANGS, AND THE REASON IS STRUCTURAL

Converting the **exit** authority alone is not enough, because **the wire EXIT is ONE authority while wire ENTRY has SEVERAL contracts**. Two-line asm diff on the witness proves it: `EXPR$0_γ/ω` convert to `jmp [rsp]`/`jmp [rsp+8]` while **no `push` appears anywhere** — that thunk is entered from **C** through `rt_proc_enter`, which has no template pass site at all. It then jumps through an `[rsp]` nothing pushed.

**NEXT RUNG, exactly scoped:** `rt_proc_enter`'s asm (already asm — §1) must **push the pair** under the arm instead of `leaq`-ing r10/r11 — `2f`/`3f` are already materialised there, so it is two `push`es replacing two `leaq`s — and the same for `rt_call_proc_descr`'s and `rt_tiny_record_enter`'s entries. Then the open-coded exits (`bb_define.cpp:358/360`, `xa_flat.cpp:259/265`) convert with their roads. ⛔ `bb_glue_flat.cpp:125` names the other half and it is still owed: *"rsp is NOT restored to entry depth here … you are just getting the going in part, not the coming out part"* (Lon s55).

## 7. ROUTED

`GOAL-SNOBOL4-100.md` LIVE CURSOR (s194c) · `GOAL-SCRIP-HQ.md` cursor · row `wire-stack-rung2-c-entry` · `QUEUE.tsv` in lockstep. Siblings: `FINDING-…-s194-…-spelled-twice.md`, `FINDING-…-s194b-…-rtcc-bank-residue-in-its-omega.md`, `GOAL-RTCC.md` (PF-2 / register liberation).
