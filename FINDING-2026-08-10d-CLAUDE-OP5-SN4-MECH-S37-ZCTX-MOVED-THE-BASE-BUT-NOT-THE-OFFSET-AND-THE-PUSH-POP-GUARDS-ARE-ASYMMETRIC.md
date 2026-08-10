# FINDING 2026-08-10d — MECH s37 (Opus 5): ZCTX moved the BASE per-activation but left the OFFSET compile-time-local; and the push/pop guards are asymmetric

**HEAD at open:** SCRIP `bce9a4b0` · corpus `bea31de0` · `.github` `37e0273c`. **Watermark PROVED at open, both modes, fresh container:** m3 **134/15/0/2** · m4 **133/16/0/2**. **PROVED at close:** identical BY SET. One commit landed: SCRIP `7aa32a3d`.

## 0. Cursor correction — s36's prescription was overtaken before this session opened
The s36 cursor (M-1b GLOBAL-EXECUTE) says `g_blob_ctx` is live and prescribes deleting it. It is already gone. `0970838f` (Fable s11, Lon-in-chat) replaced it with `g_zctx[66]` — a real depth-counted base stack, push at α+β, pop at γ+ω. `grep -rn 'g_blob_ctx\|rt_blob_ctx_ptr' src/` == 0. The ZETA-MECH file never got the entry; s36 is still its newest cursor. **H31 was repaired by that commit** (3 regressions → 2), which is why the watermark is +1 pass over s36 in both modes.

## 1. The defect ZCTX did not fix: the base is per-activation, the offset is not
Every reader computes `[g_zctx[1] + <its own blob's compile-time kt> - 24/16/32/40]`. `g_zctx[1]` is whichever activation is on top — which need not be the blob whose code is running. **Measured on D12** (`--compile` artifact truth):

| blob | kt | γ wire stored at | its CLASS-D stub read |
|---|---|---|---|
| `proc_PAT$0_α` | 128 | `[rsp+104]` | `[rax+104]` / `[rax+112]` |
| `proc_PAT$1_α` | 224 | `[rsp+200]` | `[rax+200]` / `[rax+208]` |

D12 emits carves of **64/80/128/224** — the exact non-uniformity the s36 cursor cites. `ITEM = SPAN | *LIST` / `LIST = '(' ITEM ARBNO(',' ITEM) ')'` makes the two blobs mutually recurse, so a PAT$0 stub reads 104 bytes into a 224-byte carve, lands in interior data, loads 0, and executes `jmp rcx` with rcx=0. **gdb: PC=0, rcx=0, ZCTX depth=2 with correctly-chained spills** — the stack machinery was healthy; the base was right and the offset was foreign.

This is one mechanism explaining BOTH sides of the ledger: correct exactly when every live activation shares a kt (single-activation → 16/16 green; H31 → repaired), wrong when they do not (D12/D13). **It is the same objection s36 raised against a `[kt-8]` parent LINK** — "parent_kt unknowable at the restoring blob's compile time" — and it binds a base pointer dereferenced with a local kt just as hard as it binds a link.

## 2. Fix landed (SCRIP `7aa32a3d`): publish the HEADER, not the base
α publishes `hdr = base + kt - 40`. The quad is then at **fixed** `hdr+0` (δ0) · `+8` (scan flag) · `+16` (γ wire) · `+24` (ω wire), and ω's absolute unwind `lea rsp,[hdr+40]` is *identically* `base+kt`. The scanfail retry whack still needs the base, so α stashes its own base in the reclaimed **`[kt-8]` dead pad = `hdr+32`** and the whack reads `mov rsp,[rdx+32]`.

⛔ **This is not the `[kt-8]` trap s36 rejected.** That design dereferenced a *foreign* activation and required `parent_kt`. This stores the activation's *own* base and is read at a kt-free offset. No new global, no shared cell, no new register claim. Both media, 8 arms.

**Verified in gdb after the fix** — a live header reads `hdr−base = 0xB8 = kt−40` for kt=224, both wires holding real code addresses, base slot correct. **0 regressions and 0 repairs in both modes**: the contract is now kt-free, which is a prerequisite the eventual repair needs, not the repair itself.

## 3. The second, distinct defect (D12/D13 still red) — ASYMMETRIC PUSH/POP GUARDS
Static counts balance (2 push / 2 pop, both media). The **guards do not**:

- **push** — α publication, emit.cpp:2373: `if (g_emit.flat_jmp_entry)`
- **pop** — CLASS-D γ/ω, emit.cpp:2806: `_blob_wire = (!_wire_stub && g_emit.flat_jmp_entry && g_emit.flat_pat)`

Any `flat_jmp_entry` graph outside that intersection **pushes and never pops** — POP DEBT, hazard class (b) of this file's own LIFO/DYNAMIC-DEPTH law. `g_zctx[1]` is then left aimed at a dead activation whose stack has been reused. **Measured:** the faulting "header" holds `0x0000000600000006` in the wire slot and a base slot implying kt=608, which no blob emits — it was never a header. Note emit.cpp:2955 sets `flat_jmp_entry = 1` for a non-`flat_pat` class, so the leak is structural, not incidental.

**REPAIR = make the two guards ONE predicate.** Which side to align is a genuine design call — the CLASS-O / `_wire_stub` exits are the other party — so it is ROUTED, not guessed. Do not bolt a compensating pop onto one exit; that reintroduces the two-calculators disease ONE-SYSTEM exists to kill.

## 4. Two items that are not D12
1. **WREG LANDMINE.** LADDER WREG has **not** landed in code — no `lea r10` at any call site; live glue is still `bb_glue_pass_wires` = `lea rcx,γ + lea rdx,ω + jmp rax`. But all six ZCTX sequences use **r10/r11 as scratch** (`mov r10,[rax]` depth, `mov r11,[rax+8]` base). The moment WREG-3 lands, those silently destroy rΓ/rΩ. This session deliberately did **not** re-allocate them (scope), so the collision is live-on-arrival for whoever lands WREG-3 — which the bulletin assigns to this goal.
2. **THE CLAIM GATE HAS A HOLE.** RULES.md calls `scripts/test_gate_rtcc_claimed_regs.sh` "the replacement for the window" for semantic register collisions. It knows about **r9 only**, and it runs **INFORMATIONAL** by default (`GATE: INFORMATIONAL (pass --strict to enforce)`). It would not have caught an r10/r11 collision at all. If that gate is load-bearing for 5 concurrent seats, it needs the claimed-register set to be data, not one hard-coded register, and it needs to run strict.

## 5. Manual anchors consulted
p.85–87 (`*` deferred evaluation) · p.121–123 (ARBNO; Recursive Patterns — **D12 is the p.123 example verbatim**, D13 its negative control) · p.125–127 + p.204 (FENCE, tutorial + reference) · p.203–208 (the pushdown pattern-match algorithm and bead diagram — the "one cell cannot be a stack" source).
