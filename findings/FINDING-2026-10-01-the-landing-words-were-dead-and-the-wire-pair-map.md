# FINDING 2026-10-01 — the staged call's landing words were dead, and the map of the jmp-entry wire pair

Row `gc-one-stack-all-descriptors-no-marker-no-map-no-ledger-every-raw-word-on-the-emitted-stack-becomes-a-tagged-cell-lon-2026-09-30` (cto, rank 0; ARCH-GC-COMPILE-TIME-FRAME-MAPS.md § 12). Landed as SCRIP `2fdfa42e8`. The census instrument is in `FINDING-2026-10-01-one-stack-raw-word-census.md`.

## 1. The landing words: what was proved and what landed

`bb_call_proc_staged.cpp` (non-generator regime) and `bb_call_value.cpp` (Prolog goal sites, `cv_pl_proto`) pushed `sub rsp,8; lea rcx,L(7)|L(11); push rcx` under the wire pair. That left a raw 16-byte unit `{code address, pad}` on the spine at every call. The templates' own notes said a deterministic callee "returned … popping the pair and this word". No emitted exit does that.

**The plant.** A scratch worktree had `x86_bomb` (prints and aborts, rc 134) at both labels. Nothing hit it, in both modes:

- 100 `scripts/gc_witnesses/` programs.
- 23 Prolog benchmarks.
- 563 Prolog master entries and 900 Icon master entries, extracted one per file with `corpus_suite_harness.py extract`.
- The standalone Icon, Prolog, Pascal and Raku tests.
- 150 IPL programs.

Every Prolog entry emits the L(11) plant, so that arm is not vacuous. There was no rc 134 anywhere.

**The cure.** The unit is now `{DT_RAW, 0}` at the same depth: `sub rsp,16; mov qword [rsp],DT_RAW; mov qword [rsp+8],0`. No zd depth moves and no `add rsp` landing moves. The generator regime's word at `[rsp+24]` is now 0, which is what its hand-written twin `rt_genp_spine_enter_n2` already wrote. Both dead landing blocks are deleted.

**Measured** with `test_gate_gc_one_stack_the_walker_sweeps_tagged_cells.sh` (64 KB, `SCRIP_GC_STRESS=1`): crypt.pl in m3 went from 190,806 code-valued raw units to 130,164. Total raw went from 300,230 to 239,586 of 2,203,438 units. In m4 the code count went from 190,804 to 130,162. The other five witnesses did not change beyond the known ±1 drift of unwritten pads.

## 2. What remains per Prolog call (crypt.pl, mode 4, symbolized after the landing)

Each `call_proc_staged` call still leaves three raw units:

- **The pushed wire pair** `{γ, ω}` on the spine. The unit's first word is the γ landing, α+178 or α+349.
- **The callee frame's top 32 bytes.** `kt-32..kt` hold `{stack word, γ copy}` and `{ω copy, caller rbp}`; the `FRAME off N code` / `off N-16 stack` pairs are these. The ω copy is the unit's first word: α+203 or α+374.

The root frame adds two more units: `main+155` (the return into the C driver) at base+0, and a code and stack pair near base+160.

## 3. The cross-box resume protocol: why a record's word 0 cannot be moved one box at a time

Word 0 of a spine record is the resume address. It is read by boxes that did not push it:

- **ARBNO_DT's L(4)** (`bb_match_arbno.cpp`): `add rsp,16; jmp [rsp]`. It pops its own record and resumes whatever record its body left below it.
- **The generator β** in `bb_call_proc_staged.cpp` and `bb_call_value.cpp`: `mov rsp,[act+8]; jmp [rsp]`. It resumes the top record of the callee's suspended spine.

So moving the resume address out of word 0 (`{DT_RAW, resume}` with `jmp [rsp+8]`) is one landing over every record producer and every generic resumer together. The landing-word class in § 1 was free of this constraint only because nothing read it.

## 4. The wire pair map (an audit by a subagent of the cto's sitting, model output — a map to verify, not a measurement)

What it verified against source, and what the cto re-checked by hand, is marked **[read]**. Line numbers were taken at SCRIP `325bac5ae` and drift.

### Layout variants

| Variant | Layout |
|---|---|
| **S** (stack pair) | `[rsp]=γ`, `[rsp+8]=ω` at entry |
| **R** (register pair) | `rcx=γ`, `rdx=ω`; the zframe and class-C prologues copy them to `[kt-24]`/`[kt-16]`, caller rbp at `[kt-8]` |
| **SIG** | `rcx` points at `{nargs, γ@+8, ω@+16, arg offsets@+24+8i}` |
| **TINY** | `[rsp]=nargs`, `γ@+16`, `ω@+24`, args `@+32+16i` |
| **G5** (generator frame) | `[rsp]=γ`, `+8=ω`, `+16=REGION`, `+24` the landing word (0 since `2fdfa42e8`), `+32=N-2` word, anchor at `+40` |

The resume record a blob's γ exit pushes is `{res, γ, ω, rbp}`.

### Producers of S

| Site | What it does |
|---|---|
| `bb_glue_flat.cpp` | `bb_glue_pass_wires_blob`, `_blob_act`, `_blob_regs`; `bb_glue_enter_c2bb` (how 0/1/3 by `_blob_regs`, how 2 builds SIG) **[read]** |
| `bb_call_proc_staged.cpp` | `bcps_wire_cross_gen` `push ω; push γ` **[read]**; the s111 floater pair `lea rcx,L(4); push; lea rcx,L(3); push` |
| `bb_define.cpp` role 4 | SIG and TINY arms: `push ω; push γ` |
| `xa_flat.cpp` | the PL-DC stub's wire-stack arm |
| `emit.cpp` | the first-guard fast_empty re-push |
| `src/driver/scrip.c` | `rt_outer_call` `{2f, 2f}` **[read]**; mode-4 main `{.Llevel_zero_return ×2}` |
| `runtime_eval.c` | `rt_chain_enter` `{9f, 9f}` **[read]** |
| `rt.c` | `rt_proc_enter`, `_named`, `_frag`, `_barrier` (`pushq %rdx; pushq %rcx`) |
| `rt_coexpr.c` | `rt_genp_spine_enter` (`{4f, 0, 0}`), `rt_genp_spine_enter_n2` (G5) |

### Consumers of S

| Site | What it does |
|---|---|
| `bb_glue_wire_exit` | `jmp [rsp]` / `jmp [rsp+8]` **[read]** |
| `bb_glue_outer_γ/ω` | `mov eax, DT_S\|DT_FAIL; ret` when `bb_glue_outer_needs_ret` **[read]** |
| `bb_glue_act_record`, `RT_ACT_RECORD_ASM` | copy `[rsp+k]` to `SNO_LVL_GAMMA` **[read]**; `core.c` compares it |
| `rt_unwind_to_activation` | reads `act[0]` or `act[8]` |
| DEFINE floaters (`bb_define.cpp` and hoisted into main) | `pop rcx; add rsp,8; jmp rcx` / `add rsp,8; pop rcx; jmp rcx` |
| PAS-NEST exits (`xa_flat.cpp`) | the same pop forms |
| Icon generator prologue (`emit.cpp`) | copies `[rsp]`/`[rsp+8]` into its frame |
| Blob thunk exits (`emit.cpp`) | the first-guard ω, fast_empty, γ and ω exits; the γ exit builds `{res, γ, ω, rbp}` |
| `blob_cont_copy` | duplicates `rbp+8/+16` to `rbp-8/-16` |
| `blob_layout_build` | marks them `GC_LAY_PTR_CODE` |
| Prolog tail call | reuses the caller's incoming pair implicitly |

### Consumers of R copies (frame slots)

- `xa_flat.cpp`: the pinned and unpinned Prolog γ/ω (`kt-24`/`kt-16`), the class-C SIG epilogue, and the PL-DC landings.
- The Prolog LCO in `bb_call_proc_staged.cpp` (`fb-24`, `fb-16`, `fb-8`) **[read]**.

### Not part of the convention, or dead

- **Not part:** `rt_defer_land_γ/ω`, `rt_gen_spine_pass_γ/ω`, every `src/runtime/rtx/*.s` leaf, and the co-expression switch.
- **Dead:** `x86_call_frame_enter`, `x86_srf_floater`, `x86_return_floater`/`x86_freturn_floater`, and `g_emit.flat_res_p`.
- **Unverified:** the non-pattern `lbl_res` block, the runtime-built pattern blobs `bb_build_len_blob`/`bb_build_break_blob`, the exits of non-cells local-variable procedures, and the non-zframe PL-DC arm.
