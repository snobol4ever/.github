# FINDING s189 (HQ) — ⭐⭐⭐ BEAUTY'S WILD JUMP, ROOT-CAUSED ON A THREE-LINE WITNESS: A COMPUTED GOTO RUNS ITS TARGET AS A **NESTED ACTIVATION**, SO THE NEXT `:(RETURN)` POPS THE C SHIM'S FRAME

**Date:** 2026-08-20 · **SCRIP:** `c62c18af` (pristine, RT_OPT `-O0`) · **corpus:** `d686c91f` + this FINDING's `probe/igt/` · oracle live `sbl`.
**Provenance:** found by walking the broad-corpus board's five m3 reds through the cured automatic bug finder (FINDING s189-a), not by attacking beauty. **HQ had failed nine times to build a standalone reproducer for this crash. It did not need building — it was already a checked-in crosscheck red nobody had connected to beauty.**

## 1 · THE HEADLINE

`corpus/crosscheck/rung2/216_indirect_goto_computed.sno` — **twelve lines**, a standing corpus red — crashes with **the same signature as beauty self-host, quad for quad**:

| | beauty on `m1_min.in` | `216_indirect_goto_computed` |
|---|---|---|
| rc | 139 | 139 (stable 3/3) |
| rip | `0x7ffff7ffd000` `_rtld_global` (ld.so DATA) | identical |
| last ZSM port | `α· op=25 IR_DEFINE` | identical |
| glue at death | `pop rcx; add rsp,8; jmp rcx` | identical |
| stack at the pop | `_rtld_global` · `0x41bd68` · `0` · `0x7ffff25ff030` · … · `0x7ffff414e1eb` | **same six slots, same order** |
| α·-DEFINE events first | 236 | **2** |

## 2 · THE ABLATION LADDER — ONE TOKEN WIDE (`corpus/probe/igt/`, live-oracle refs, all four checked in)

| witness | shape | verdict |
|---|---|---|
| `igt_inline_ctl` | `DEFINE('f()')` … `:(RETURN)`, no goto | **GREEN** |
| `igt_direct_goto_ctl` | identical signature; leaves the proc by **`:(LADD)`** then `:(RETURN)` | **GREEN** |
| `igt_computed_goto` | same, but **`:($('L' OP))`** | **RED — SIGSEGV** |
| `igt_computed_goto_pre` | same + a preceding statement | **RED — SIGSEGV** |

The ingredient is **the computed goto**. Not the RETURN (control 1 green). Not leaving the procedure body (control 2 green — a direct `:(LABEL)` out of a proc to a top-level label, then RETURN, works). `igt_direct_goto_ctl` vs `igt_computed_goto` is the asm-diff pair.

## 3 · THE MECHANISM, END TO END

**Emitted (mode 4, the red arm):**
```
n9_goto_deferred_α:  mov rdi, [rip + .Lx44_0]      # "$IGT$0"
                     mov [rip+rtccb+40], r8 ; +56, r10 ; +64, r11
                     call rt_goto_transfer@PLT      # ⛔ a CALL, not a transfer
                     …restore r8..r11…             ; jmp .Lx44_1
.Lx44_1:             add rsp, 48 ; jmp main_γ
```
The green control emits a plain `jmp` here — no call, no C frame.

**`rt_goto_transfer` (`runtime_eval.c:435`)** resolves `$IGT$0` → the label's chain fn → **`rt_chain_enter(fn)`**.

**`rt_chain_enter` (`runtime_eval.c:97`, hand asm)** — its own header states the intent, *"no CALL/RET — a JUMP and a JUMP BACK"*:
```
pushq %rbx ; %r12 ; %r13 ; %r14 ; %r15      # 5 callee-saves = 40 bytes
leaq 1f(%rip), %rcx ;  movq %rcx, %rdx      # ⛔ BOTH γ and ω wired back into this shim
jmp *%rax                                    # target chain runs as a NEW ACTIVATION
1:  popq %r15…%rbx ; ret
```

**So:** the target label runs **nested inside `rt_chain_enter`'s C frame**, with both continuations pointing back into the shim. When that label's `:(RETURN)` fires, the procedure-return glue executes its pop-pair **at the current rsp — inside the shim's five pushes and the C frame** — instead of at the procedure activation that holds the real `{γ,ω}`. It pops a saved callee-save / C residue (`_rtld_global`) and jumps to it.

⛔ **CORRECTION TO FINDING s189-a §2, ON EVIDENCE.** That section read beauty's dump as *"the pair is not MISSING — it is SHIFTED"*, citing `0x41bd68` one slot below as the real continuation. **That reading is withdrawn.** `0x41bd68` is a main-binary address; a mode-3 SNOBOL continuation is a **slab** address (`0x7fffee0…`). The six quads are C-frame residue — a return address into `libscrip_rt` sits at `+40` in **both** programs. The pair is not shifted, it is **not there**: the glue is running on the wrong activation entirely. The `beauty-return-pair-shift` queue row is renamed accordingly.

## 4 · WHY THIS IS THE BEAUTY WALL

`beauty.sno:247` `DIFFER(t) :S($('pp_' t))F(RETURN)` and `:466` `$('ss_' t)` — **beauty's whole pretty-printer dispatches by computed goto inside DEFINE'd procedures** (`pp(x)`, `ss(x,len)`). The crash ring lands at `st=969` = `beauty.sno:313 pp_Comment` — a `$('pp_' t)` target — then `α· IR_DEFINE` → wild jump. Every real statement beautified takes this road, which is why the ladder dies at the 10-line prefix and every `m1_lad_*` witness is red.

## 5 · CURE DIRECTION (design note; NOT landed here — this is a dispatch brief's content)

**A GOTO is a transfer, not a call** (ARCH-PASSTHRU law 0a: the pair *is* the mechanism). The transfer road must be a **tail transfer**: resolve the target in C, hand the fn pointer *back*, and `jmp` to it from emitted code so the target runs on the **same** activation — precisely what `:(LABEL)` already does and why its control is green.

⛔ **The honest complication, stated so the seat is not ambushed:** `rt_chain_enter` is shared with the EVAL/CODE fragment road, where the jump-back **is correct** (a fragment is a nested evaluation that must come back). So the rung is not "delete the shim" — it is **two contracts that were collapsed into one**: *transfer* (no return) vs *nested evaluation* (returns). Splitting them is not a per-op filter (NO-PER-OP-FILTER is about admitting/refusing members of one family by op identity); these are two genuinely different linkage contracts, and the seat should say so in its FINDING with this citation.

Secondary question the seat must answer with a measurement, not an assumption: `.Lx44_1: add rsp,48; jmp main_γ` — the post-call fixup assumes the transfer *returns*. Under a tail transfer that code is unreachable; confirm it is removed rather than left as a dead landing that a later edit re-animates.

## 6 · RECIPES (both reproduce in seconds)

```bash
# the crash, and the ring that names it — no monitor needed
cd corpus/probe/igt
SCRIP_ZSM=1 SCRIP_ZSM_ALL=1 SCRIP_ZSM_RING=1 SCRIP_NO_SEGV_HANDLER=1 \
  gdb -batch -ex 'run igt_computed_goto.sno < /dev/null' -ex 'bt 3' \
      -ex 'call (void)zsm_dump()' ../../../SCRIP/scrip

# the death site, measured (2 = the α·-IR_DEFINE hit count on this witness)
gdb -batch -ex 'set breakpoint pending on' \
  -ex 'break rt_zdp_sm_event if ((long)$rcx & 0xff) == 5 && ((((long)$rcx) >> 8) & 0xffff) == 25' \
  -ex 'ignore 1 1' -ex 'run igt_computed_goto.sno < /dev/null' \
  -ex 'finish' -ex 'stepi 13' -ex 'x/6gx $rsp+0x50' -ex 'stepi 11' -ex 'info registers rcx' ../../../SCRIP/scrip
```

## 7 · WHAT THIS SAYS ABOUT THE BOARD (method, not blame)

`216_indirect_goto_computed` has been red on the broad corpus board for months, sitting in the *same* fail-set line the campaign quotes every session (`m3 332/5`), while nine attempts were made to construct from scratch a witness for beauty's crash. **The five-name fail-set was being read as a score, not as a set of unexamined reproducers.** The cheap standing instruction that follows: when a flagship program crashes, run the finder over the *existing* red set first and compare crash signatures — an identical `rip`, last-port, and stack shape is a same-class claim that costs one gdb batch to test.
