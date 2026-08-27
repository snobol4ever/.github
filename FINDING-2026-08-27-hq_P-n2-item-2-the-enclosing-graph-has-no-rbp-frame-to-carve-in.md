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

---

# ADDENDUM (hq_P s277, after ceo's ruling) — the callee frame size IS reachable, the registry already exists, and there is a forward-reference hazard nobody has named

ceo **RATIFIED** the design: host promotes to a real RBP activation frame; a **direct** call reserves the callee's
compile-time-known frame bytes inside the host's own carve. Worst-case reservation **REFUSED**; indirect/dynamic
dispatch **UNRULED**, handed to the `hq_C` one-shape-test. This addendum records step 1's de-risking result.

## ✅ The input I flagged as unknown is actually already there

**The driver already records every proc's frame bytes by name.** In the proc-emission loop (`src/driver/scrip.c`),
immediately after each `emit_chain`, it captures:

```c
{ extern int g_last_flat_frame_bytes; proc_fb_buf[n_procs] = (... LBL__ ...) ? 0 : g_last_flat_frame_bytes; }
proc_names_buf[n_procs++] = pname ? strdup(pname) : NULL;
```

So `proc_fb_buf[]` ↔ `proc_names_buf[]` is exactly the callee-frame-size registry item 2 needs. Nothing new has to be
computed — **only exposed.**

## ✅ Emission order is favourable for host = `main`

Both driver arms emit procs first and `main` last: each proc loop explicitly `continue`s on `main`
(`scrip.c:1263`, `:1415`, `:1447`), and `main` is emitted afterwards (`:1365`, and the m3 arm's own tail). **So at
`main`'s emit time every proc's frame bytes are already recorded.** That covers the four-line witness.

## ⚠️ THE HAZARD, and it is the reason step 1 was worth doing separately

⛔ **The favourable order holds only because the host is `main`. It does NOT generalize.** If the host is itself a
**proc** that calls a generator appearing **later in the same proc loop**, the callee's frame bytes are **not yet
recorded** when the host is emitted — a forward reference, and `proc_fb_buf` would be read as 0 or absent.

⭐ **This is the same shape as three other defects found today: the value is READ AT A POINT WHERE IT IS NOT YET
DEFINED, and the read returns a plausible number rather than an error.** A 0-byte reservation would produce a host
carve that is silently too small — i.e. exactly the "silent overflow" ceo refused worst-case reservation to avoid,
arriving through a different door.

**Required before step 2 lands:** either (a) a pre-pass that records all generator procs' frame bytes before ANY graph
is emitted, or (b) an assertion that REFUSES loudly when a host reserves for a callee whose frame bytes are not yet
recorded. ⛔ **Not "read it and hope" — a missing frame size must never read as 0.** `bench_correct`'s eight programs
must be checked for the host-is-a-proc shape before anyone assumes the `main` case is representative.

## What remains for step 2

Expose an emit-time accessor `callee_frame_bytes(name)` over the existing `proc_fb_buf`/`proc_names_buf` pair, guarded
per the hazard above. **No new state, no new globals** — the data exists and is captured in the right order for the
`main` host.

## Status

⛔ **NO CODE CUT.** The promotion itself touches `x86_main_prologue()`/`bb_glue_framed_enter()` — the glue path **every
frontend shares** — and the host rebase must route through `x86_frame_off`/`op_zdepth` rather than a constant, because
the host's rsp moves (unlike the generator's, which is what made item 1's rebase exact). Ordered work is in the baton
under `## NEXT-ITEM-2`.
