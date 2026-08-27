# FINDING — N-2 item 2: the re-target says carve in the **enclosing graph's RBP activation frame**, and the enclosing graph does not have one

**Seat:** `hq_P` s277 · **Date:** 2026-08-27 · **Mode:** FLEET-8
**Row:** `icon-n2-generator-activation-frames` (hq_P) · blocks `icon-bench-correct-zero-of-eight` (`bench_correct` 0/8, weight 15)
**Status:** ⛔ **SCOPING FINDING — NO CURE WRITTEN.** Item 2 is not "re-point rbp"; measured below, it is a
**caller-side** change, and one input to it is genuinely unknown.

## What the ruling says

`RULES.md:72` § THE STORAGE ANSWER (Lon, via ceo, 2026-08-27), quoted: *"A suspend-surviving frame carves in the
**ENCLOSING graph's RBP activation frame** (its lifetime nests in the bounded expression that owns it — the ladder needs
nothing more)."* The workspace island is deleted; nothing may replace it off-stack.

## ⛔ What is actually on the machine, measured

Armed four-line witness (`procedure gen(); suspend 1; end` / `main` calls `write(gen())`), `--compile`, `-O0`:

**1. The enclosing graph has no RBP activation frame at all.** `main`'s prologue is `sub rsp, 8; push rdi; push rsi`
— no `push rbp; mov rbp,rsp` — and **`grep -c rbp` over the whole of `main` returns 0.** It is a pure ζ-SPINE (RSP)
graph. There is no RBP frame to carve into.

**2. The caller's own ζ is rsp-relative, and it is read on the far side of the suspend.** At the landing:

```asm
.Lx8_3: cmp al, 104; je .Lx8_8          ; DT_FAIL discriminator (suspend vs retire)
        mov rcx, rsp                     ; rcx = the 4-word resume record
        mov rax, qword ptr [rsp + 24]    ; rax = record word 3 = the generator's rbp
        lea rsp, [rax + 32]              ; ⛔ rsp := gen_rbp+32 — ABOVE the generator's whole carve
        mov qword ptr [rsp + 72], rcx    ; caller's FRQ(act+8)  ← RSP-RELATIVE
.Lx8_9: mov rax, qword ptr [rsp + 64]    ; caller's FRQ(act)    ← RSP-RELATIVE
```

⭐ **So the `lea rsp,[rax+32]` is not a stray bug — it is load-bearing.** The caller's `[rsp+64]`/`[rsp+72]` are
reached at fixed offsets from its restored rsp, and the very next instruction after the `lea` depends on it.

**3. Stack layout, measured** (`frame_total=96`; γ pushes 4 words):

| region | extent |
|---|---|
| caller's pre-call rsp | `gen_rbp + 32` |
| caller-pushed γ / ω / third word | `gen_rbp + 8 … +24` |
| saved caller rbp | `gen_rbp + 0` |
| **generator ζ frame** | `[gen_rbp-96, gen_rbp)` |
| **4-word resume record** | `[gen_rbp-128, gen_rbp-96)` |

The generator's frame **and** its record both sit **below** the caller's restored rsp. The instruction after the
landing is `call rt_proc_call_epilogue_γ@PLT`, whose own frame walks straight down through them.

## ⭐ The contradiction, stated exactly

Two requirements cannot both hold while the generator's frame lives below the caller's rsp:

- the landing **must** restore rsp to `gen_rbp+32`, or every caller ζ reference (`[rsp+64]`, `[rsp+72]`) moves; **and**
- the generator's frame **must not** be below rsp, or the next `call` clobbers it.

⛔ **Therefore the naive realization of the re-target — "leave rsp where it is, the frame is then protected" — is
UNSAFE, and it is worth writing down because it is the obvious first move.** It would silently relocate the caller's
entire ζ by 160 bytes. Confirmed by direct evidence above, not inferred.

## What item 2 therefore requires

The generator's frame must be **inside** the caller's own carve, at a fixed offset the caller already accounts for:
the caller's α reserves the callee's frame bytes as part of its own `sub rsp, N`, so the generator's frame sits at a
known `[rsp+K]` within the caller's frame, the caller's ζ offsets are computed **with that reservation included**, and
nothing has to move at the landing. That is the honest reading of *"its lifetime nests in the bounded expression that
owns it — the ladder needs nothing more."*

⚠️ **ROUTED, BLOCKING ONLY THE DESIGN CHOICE, NOT THE ROW:** this requires the caller to know the callee generator's
frame size **at compile time**. That holds for a direct call to a known generator (the witness, and `bench_correct`'s
eight). It does **not** obviously hold for an indirect or dynamically-dispatched generator call. Two candidate answers
— (a) promote the enclosing graph to a real RBP activation frame when it contains a suspend-surviving call, which the
FRAME-PLACEMENT CRITERION's own ladder language would support; (b) reserve a worst-case//dynamic region. **Not chosen
here** — this is exactly the "confirm with ceo rather than infer it from prose" case the mode box names.

## Prior item in this rung, for continuity

Item 1b landed this session (SCRIP `fb0bcbec`): the α resume-slot seed now addresses through the ζ accessor, and a
live **m3 ≢ m4 divergence on the default build** was cured underneath it (`emit_rec_fb` vs `emit_rec_fb_num` —
TEXT said `rsp`, BINARY said `rbp`), reaching Icon generators, lcl_procs, zframe graphs **and Prolog resumables**.
See `FINDING-2026-08-27-hq_P-n2-item-1b-text-and-binary-picked-different-base-registers.md`.

## Transferable lesson

⭐ **A storage ruling names a destination; it does not guarantee the destination exists.** "Carve in the enclosing
graph's RBP activation frame" is unambiguous and correct as policy, and the enclosing graph in the canonical witness
has **zero** rbp references. ⛔ Before implementing against a named location, `grep` for it on the actual artifact —
the cost of not doing so here would have been a caller-ζ corruption that every board would have reported as a
generator bug.
