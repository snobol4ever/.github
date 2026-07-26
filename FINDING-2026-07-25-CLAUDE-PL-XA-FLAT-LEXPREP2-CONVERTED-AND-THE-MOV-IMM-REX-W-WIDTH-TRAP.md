# FINDING 2026-07-25 (s150) — XA-FLAT-CONVERT SLICE B: THE LAST LIVE PROLOGUE ARM IS CONVERTED, AND `x86("mov", <r32>, imm)` IS A TREE-WIDE REX.W WIDTH TRAP

**Rung:** XA-FLAT-CONVERT slice B (the `LEXPREP2` arm — the last live arm of `xa_flat_prologue_str`; named prerequisite for the ~20% `rt_jmp_frame_lexprep2` + `rt_frame_bind_args` callee-prologue sink).
**Result:** gate `xa_flat.cpp` **109 -> 104**. Rung suite **164/164 x3 modes, TWICE**. Icon smoke **14/14 x2 modes**. Prolog smoke **5/5/5**. m4 `.s` **22/22 byte-identical**. Bench corpus m3 **green=22 broken=0**. `no_new_global` **PASS, ratchet 14 / floor 14 UNMOVED**; `no_value_stack` PASS. RT `-O0` (no `-O2` directive this session).

---

## 1. THE ARM IS CONVERTED AND **PROVEN LIVE** (279 Prolog + 10 Icon hits)

`LEXPREP2` (`g_emit.flat_lex && g_emit.flat_seed_off >= 16`, the `ZC_FRAME_RSP` jmp-entry lazy-seed prologue) is now a pure `x86(...)` record stream routed through the `site < 0` sentinel s149 landed:

```
xaf_jmp_hdr_x86()            sub rsp,K / wires at kt-24,kt-16 / caller rbp at kt-8 / mov rbp,rsp
xaf_anchor_enter_x86()       anchor slot <- rsp
x86("mov",  "rdi","rsp")     fb = region base
x86("mov32","esi", seed_off) NULVCL seed start
x86("mov32","edx", kt-32)    region size
x86("call", "rt_jmp_frame_lexprep2", &fn)
```

**LIVENESS PROVEN BEFORE ANY GATE WAS BELIEVED** (the s149 rule — *a green gate proves nothing unless the changed code is proven to execute*). Env-gated `SCRIP_XAF_MARK=1` marker + corpus sweep + `grep -c`:

| sweep | LEXPREP2 hits |
|---|---|
| Prolog rung corpus (192 programs, m3) | **279** |
| Icon corpus (m3) | **10** |

The Icon count reproduces s149's measured 10 **exactly**; the Prolog count is higher than s149's 132 only because this sweep covered all 192 rung programs rather than the 28-program subset. The marker is left in-tree, env-gated and inert by default — it is the instrument the s149 rule prescribes, and the next arm/epilogue conversion needs it. **Delete it if Lon prefers templates carry no scaffolding.**

## 2. ⭐ `x86_call_ro` COLLAPSED THE HAND-WRITTEN MEDIUM PAIR EXACTLY

The legacy arm carried the two media as *separate hand-written sequences*: BINARY `bytes(2,"\x48\xB8") + u64le(&fn) + bytes(2,"\xFF\xD0")` and, 130 lines away, TEXT `call rt_jmp_frame_lexprep2@PLT`. `x86("call", sym, ptr)` -> `x86_call_ro` (`x86_asm.h:250`) emits **precisely those two forms** — BINARY `48 B8 <ptr> FF D0`, TEXT ` call sym@PLT`. So the conversion is not an approximation of the legacy bytes; for the call it is byte-exact by construction, and the R10 medium-specific carve-out for RO calls is the encoder's job, not the template's.

`x86_align_assert()` prepends nothing unless `SCRIP_ALIGN_ASSERT=1`, so the default BINARY byte stream is unchanged by routing through it.

## 3. ⚠⚠ THE REAL FIND — `x86("mov", <32-bit reg>, imm)` IS A REX.W WIDTH TRAP, ~25 SITES TREE-WIDE

Writing the `esi`/`edx` immediates surfaced a latent defect class that is **not** specific to this file.

`x86("mov", reg, imm)` dispatches (`x86_asm.h:1264`) to **`x86_movimm`**, which unconditionally stamps `rex = 0x48` and a full `u64le` — i.e. `movabs r64, imm64`, **10 bytes** — while the TEXT twin ` mov esi, N` is assembled by `as` as `B8+r imm32`, **5 bytes**. Measured with `as` + `objdump`:

```
mov    esi,0x60          be 60 00 00 00              rsi = 96
movabs rsi,0x60          48 be 60 00 00 00 00 00..   rsi = 96          <- same value, 2x the bytes
mov    esi,0xffffffff    be ff ff ff ff              rsi = 4294967295
movabs rsi,-1            48 be ff ff ff ff ff ff..   rsi = -1          <- DIFFERENT VALUES
```

So the pair is:
- **always** a byte/size divergence — R10 says BINARY must match `as` on *"same REX.W width"*, and this violates it at every site;
- **additionally a SEMANTIC divergence for any negative immediate** — BINARY sign-extends to 64 bits, TEXT zero-extends through the 32-bit destination.

**`x86("mov32", ...)` -> `x86_movimm32` is the as-matching form**, and it is already the dominant idiom (`bb_call_fn.cpp` 19 uses, `bb_call_proc_staged.cpp` 11, `bb_call.cpp` 6, …). The `mov` sites are the trap, not the norm.

**WHY IT SURVIVED THIS LONG: every gate in the tree is behavioral, and for a non-negative immediate both encodings leave the same value in the 64-bit register.** The defect is invisible to 164/164 and to `.s` diffing (the TEXT side is correct — it is BINARY that is wrong), and it costs 5 bytes per site in mode-3. This is the same shape as s149's own lesson: green gates cannot see a divergence that is size-only until an operand goes negative.

**FIXED THIS SESSION (in-file, in-rung):** `xa_flat.cpp:266`, `x86("mov","ecx",K)` -> `x86("mov32","ecx",K)` — s149's own FRAME_RSP reference conversion carried the trap. Harmless there only because `K = xaf_outer_frame_k() >= 65544` is positive.

**NOT FIXED — NEEDS A LON RULING (cross-language, outside this goal):** ~24 further sites, all in Icon/SNOBOL4 pattern + arith templates: `bb_arith.cpp` (4), `bb_binop_arith.cpp` (4), `bb_binop_relop.cpp` (4+), `bb_binop_gvar_arith_slot.cpp`, `bb_match_{any,break,breakx,notany,span,span_var,capture}.cpp`, `bb_pattern_len.cpp`. Audited by eye, the operands are opcode selectors and 0/1 constants — **non-negative, so the hazard is latent rather than live** — but `bb_pattern_len.cpp:21` passes `(long)(int)_.op_ival`, a user-supplied `LEN` operand, and `op_ival` is `int64_t`. **A one-line sed would fix all of them, but they are other goals' boxes and this rung has no mandate to touch them.** Grep to reproduce:
`grep -rnE 'x86\("mov",\s*"(e(ax|bx|cx|dx|si|di|bp|sp)|r([89]|1[0-5])d)"\s*,\s*\(?(long|int)' src/templates/*.cpp`

## 4. BYTE-IDENTITY IS **NOT** THE ACCEPTANCE TEST HERE, AND THE `.s` PROVES ONLY HALF

Per s149 §5, the encoders pick `as`-matching short forms. `xaf_outer_frame_k()` floors at 65544 so the FRAME_RSP arm had no short-form risk; **`LEXPREP2` does not have that protection** — `kt` is only required to be a 16-multiple `>= 48`, so `sub rsp,kt` takes the imm8 form and the three header stores take disp8 whenever `kt` is small. **Converted BINARY is therefore legitimately SHORTER than the legacy hand-encoded imm32/disp32 stream.** That is correct (R10) and safe (this arm carries no patch site at all — the legacy `out_site` was already `0`/`nullptr`, so the sentinel here buys the tag walker, not an `X` record).

Consequence for the reviewer: **m4 `.s` 22/22 byte-identical proves the TEXT branch was not disturbed — it does NOT validate the BINARY conversion**, because the two branches are still separate (this slice converts the `MEDIUM_BINARY` arm only, exactly as s149's did). The BINARY conversion is validated by the m3 behavioral gates + the 279/10 liveness counts, nothing else.

## 5. WHAT LANDED (SCRIP `src/templates/xa_flat.cpp` ONLY)

1. `xaf_jmp_hdr_x86()` — parameterless (R5) `x86()` twin of the raw-byte jmp-entry `hdr`. The raw `hdr` **stays** because the dead NOFILL arm below still consumes it; it dies with that arm.
2. `LEXPREP2` arm converted, `out_site = -1`, `mov32` for both immediates.
3. `xaf_anchor_enter_x86()` reused as-is from s149.
4. `xa_flat.cpp:266` width fix (§3).
5. Env-gated `SCRIP_XAF_MARK` liveness marker.

**NO new globals. NO runtime/`.so` logic change. NO IR/lower change. The encoder surface needed NO additions** — `mov32`/`call`(sym,ptr)/`sub`/`mov` reg-disp all already existed.

`.s` regeneration was **not** run as a committing script: the equivalent check was performed directly (compile all 22 bench `.pl` -> `cmp` against committed `.s`) and the delta is provably zero, so the regen would be a no-op by construction.

## 6. NEXT

1. **The gate's remaining 104 in `xa_flat.cpp` is now ALL DEAD-ARM + EPILOGUE + TEXT-branch residue.** With `FRAME_RSP` (s149) and `LEXPREP2` (s150) converted, **every arm measured live is off the raw-byte family.** The ~20% callee-prologue sink is UNBLOCKED and is now an ordinary SINK rung (inline the non-variadic `rt_frame_bind_args` arm + the lexprep2 guards).
2. **LON RULING STILL WANTED (carried from s149, now cheaper):** the four dead arms (NOFILL / GEN_RESUMABLE / FRAME_NONRSP / BARE) — convert or **DELETE**? Deletion also retires the raw `hdr` and a large block of the remaining 104.
3. **LON RULING (new, §3):** fix the ~24 cross-language `mov`->`mov32` sites, or leave them to their owning goals?
4. Epilogue conversion needs the external-DEFINE path (tag `E`) at three `out_def = true` + `flat_fail_p` sites — and per s149 §1, `E`/`F` are **already decoded** at `x86_asm.h:1867-1868`; verify before designing.
5. REGAIN-1 slice C (the spine, ~36%) remains the big untouched rung.
