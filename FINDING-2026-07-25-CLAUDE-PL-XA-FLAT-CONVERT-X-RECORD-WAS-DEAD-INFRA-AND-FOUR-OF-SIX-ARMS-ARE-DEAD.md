# FINDING 2026-07-25 (s149) — XA-FLAT-CONVERT: THE `X` RECORD WAS FINISHED, WIRED, AND UNUSED; AND FOUR OF SIX PROLOGUE ARMS ARE DEAD CODE

**Rung:** XA-FLAT-CONVERT (named prerequisite for the ~20% callee-prologue sink; sole `--strict` gate violator).
**Result:** gate `xa_flat.cpp` **128 -> 109**. Rung suite **164/164 x3 modes**. Icon smoke **14/14 x2 modes**. m4 `.s` **28/28 byte-identical**. `no_new_global` ratchet **14/floor 14 UNMOVED**; `no_value_stack` PASS. RT `-O0` (no `-O2` directive this session).

---

## 1. ⭐⭐ THE `X` RECORD ALREADY EXISTED, FULLY WIRED, WITH ZERO CONSUMERS

The hardest prerequisite of this rung — patching a **caller-supplied `bb_label_t*`** (e.g. `g_emit.flat_β_p`) from inside an in-band record stream — was **already built and already decoded**:

- Producers: `x86_jmp_ext` / `x86_jcc_ext`, `x86_asm.h:635-655`, emitting tag `'X'` + 8 raw pointer bytes.
- Consumer: `bb_emit_x86`'s tag loop, `x86_asm.h:1869` — `case 'X'` reassembles the pointer and calls `bb_emit_patch_rel32`.
- Operand marker: the literal string `"extlbl"` (`x86_parse`, `x86_asm.h:1116`) + the pointer as arg 2 (`xop(unsigned long)`, tag 2).

**`grep -rn 'jmp_ext|jcc_ext|XK_EXTLBL' src/ | grep -v x86_asm.h` returned NOTHING.** It had never been used by any template. Its own header comment names `xa_flat.cpp` as the intended consumer.

**This is the same stale-blocker class as s145's "the s100 blocker was STALE" and it should be checked against REGAIN-1 slice C**, whose cursor text says it "needs the driver-minted proc-entry `bb_label_t` table + one in-band `E`/`F` record." Tags `E` (external define via `g_emit.xa_bb_emit_pair_define[]`) and `F` (external patch via `x86_pair_tgt`) are ALSO already decoded at `x86_asm.h:1867-1868`. **Slice C's record-side prerequisite may likewise be already-built.** VERIFY BEFORE DESIGNING IT.

**PROVEN, not merely present:** this session made `xa_flat.cpp`'s live outer-graph arm the first consumer. 164/164 x3 with it in the emitted path.

---

## 2. ⭐⭐ FOUR OF SIX PROLOGUE ARMS ARE DEAD — THE RUNG IS TWO ARMS, NOT SIX

Measured by instrumenting every arm of `xa_flat_prologue_str` with a distinct stderr marker and running the corpus (m3):

| arm | Prolog (28 progs) | Icon (8 progs) |
|---|---|---|
| **LEXPREP2** (jmp-entry + `flat_lex`) | **132** | **10** |
| **FRAME_RSP** (outer graph, `ZC_FRAME_RSP`) | **28** | **8** |
| NOFILL (`SPD-NOFILL` lane) | 0 | 0 |
| GEN_RESUMABLE (gen/resumable heap frame) | 0 | 0 |
| FRAME_NONRSP (legacy display-reg) | 0 | 0 |
| BARE (no frame, no jmp-entry) | 0 | 0 |

SNOBOL4 does not reach this prologue at all in the sampled corpus.

**Consequence: XA-FLAT-CONVERT is a TWO-ARM rung.** `LEXPREP2` is exactly the `rt_jmp_frame_lexprep2` callee prologue the s148 cursor named as the ~20% double-copy sink. **Lon ruling wanted:** convert the four dead arms, or DELETE them? Deleting shrinks the rung substantially and removes the tree's last raw-byte family faster.

⚠ This measurement is what saved the session from a vacuous result — see §4.

---

## 3. THE STRUCTURAL CONSTRAINT: CONVERSION IS ALL-OR-NOTHING **PER FUNCTION**, NOT PER LINE

`xa_emit_one` (`xa_flat.cpp:34`) is a **bespoke byte-splicer**, NOT the record walker: it copies the returned string byte-by-byte through `bb_emit_byte`, injecting a rel32 patch (or label define) at a **hand-counted `out_site`** carried out through reference parameters.

Therefore converting any single helper to `x86(...)` in isolation **corrupts the stream** — `x86()` in BINARY returns *tagged L-records*, which the splicer would emit as machine code. This is precisely what the pre-existing comment at `:188` warns about (*"raw bytes, NOT x86_movabs_r64: this arm is the legacy raw-byte family, an L-record would corrupt the stream"*). The gate's 128 is therefore NOT 128 independent edits.

**MIGRATION MECHANISM LANDED — the `site < 0` sentinel.** `xa_emit_one` now reads:
```
if (site < 0) { bb_emit_x86(out); return; }
```
A converted arm returns a record stream and sets `out_site = -1`, routing to the ordinary `bb_emit_x86` tag walker; unconverted arms are untouched (they never produce a negative site). This lets the arms convert **one at a time** instead of in one high-risk lump. When the last arm flips, the sentinel branch and the whole raw splicer die together.

**Bonus property:** the hand-counted `out_site = (int)r.size() - 4` is RETIRED per converted arm — the `X` record makes `bb_emit_x86` DISCOVER the patch site as it walks, so the offset cannot drift when an encoder picks a different short form. That is the `bb_bin_t`-era debt this file's own header comment complains about.

---

## 4. ⚠⚠ THE HONEST PART: THE FIRST CONVERSION WAS OF **DEAD CODE**, AND GREEN GATES PROVED NOTHING

The first arm converted was **BARE** (3 instructions: `sub rsp,8` / `cmp esi,0` / `jne β`) — chosen because m4 `hello.s` opens with `sub rsp, 8`, which *looked* like proof it was live. It was not: that text comes from the separate TEXT arm.

After conversion: rung suite **164/164 x3**, all 28 `.s` **byte-identical**, every gate green. **All of it vacuous** — instrumentation then measured **0 hits, both modes, every language**. The BARE arm is dead.

⭐ **THE RULE THIS REINFORCES (sibling of s147's "prove the `.s` reaches the code" and s146's "one run is not a measurement"): A GREEN GATE AFTER A CHANGE PROVES NOTHING UNLESS THE CHANGED CODE IS PROVEN TO EXECUTE.** Byte-identical output is the *expected* result of editing dead code, and it is indistinguishable from a correct conversion. The instrument-and-count step is not optional polish; it is what separates a proof from a coincidence. **Method: a distinct `fprintf(stderr, ...)` marker per arm + a corpus sweep + `sort | uniq -c`.** Cheap, exact, no rebuild of the runtime, and it doubles as the reachability map in §2. (This container has **no `perf` and no `gdb`** — see s148 — so marker-counting and `LD_PRELOAD` interposition are the available instruments.)

The rung was then re-aimed at **FRAME_RSP** (28 hits — one per program), which produced the genuine runtime proof: all 164 m3 rung tests and all 14 Icon m3/m4 smoke tests execute through the converted arm and its `X` record.

BARE's conversion was KEPT (it compiles, it is inert, and it is a type-checked reference of the idiom) but it is **labeled dead in-file** and must not be cited as validation of anything.

---

## 5. WHAT LANDED (SCRIP `src/templates/xa_flat.cpp` only)

1. `xa_emit_one` — `site < 0` record-stream sentinel (§3).
2. **BARE arm** — converted to `x86("sub"/"cmp") + x86("jne","extlbl",flat_β_p)`. **PROVEN DEAD; not a validation.**
3. **FRAME_RSP arm (LIVE)** — the outer-graph prologue, fully converted: `sub rsp,K` / `mov rdi,rsp` / `mov ecx,K` / `xor eax,eax` / `rep_stosb` / anchor store / `rbx`+`r12` outer seeds (absolute loads) / caller-rbp save / `mov rbp,rsp` / the `nparams` `main(args)` sub-arm (`push rsi`, `movabs`, `call rax`, `pop rsi`, param-0 stores) / `cmp esi,0` / `jne extlbl β`.
4. `xaf_anchor_enter_x86()` — `x86()` twin of `xaf_anchor_enter_bin`, frame-register-agnostic via `x86_zr()` so `ZC_FRAME_RSP` and `ZC_FRAME_RBP` both encode.

**NO new globals. NO runtime (`.so` logic) change. NO IR/lower change.** Encoder surface needed NO additions — `x86()` already covered every form (`ret`, `rep_stosb`, `push`/`pop`, `call reg`, `movabs`, `xor`/`sub`/`add`/`cmp`, and `mov` with rsp-disp / reg-disp32 / absolute).

⭐ **`xaf_outer_frame_k()` floors at 65544**, so every immediate/displacement in this arm is genuinely imm32/disp32 — there is **no imm8-vs-imm32 short-form divergence risk** here. That will NOT hold for arms with small offsets: expect `as`-matching short forms to make converted bytes *shorter* than the legacy hand-encoded imm32. That is CORRECT (R10) and harmless (the `X` record discovers the site), but it means **byte-identity against the legacy BINARY is NOT the acceptance test** — behavioral gates are.

---

## 6. NEXT

1. **LEXPREP2 arm** (132 hits) — the last live arm. Converting it drives the gate to ~0 for the live path AND unblocks the ~20% `rt_jmp_frame_lexprep2` + `rt_frame_bind_args` double-copy sink named by s148.
2. **Lon ruling:** convert vs DELETE the four dead arms (§2). Deletion is likely correct and much cheaper.
3. **Re-check REGAIN-1 slice C against §1** before designing anything — its `E`/`F` record prerequisite appears to be already built and decoded.
4. Then the epilogue (`xa_flat_epilogue_str`), which additionally needs the external-**define** path (tag `E`), used at three sites via `out_def = true` + `g_emit.flat_fail_p`.
