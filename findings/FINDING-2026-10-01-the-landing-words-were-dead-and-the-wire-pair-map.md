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

## 5. The Prolog call's stacked wire pair was dead too (SCRIP `c8dc0d182`)

On a pinned zframe (`x86_fb_pinned`, the `bcps_wire_cross_gen` road) and at a Prolog goal call (`cv_pl_proto` in `bb_call_value.cpp`), the caller passed the pair in two places: pushed on the stack (S) and in `rcx/rdx` (R). The callee copies R into its own frame.

**The poison plant.** The pushed words held `0x5EED0001..`; the registers were left correct. The emitted plant counts were 36 sites in crypt.pl and 48 in plunit.pl. Over 628 Prolog programs (563 master entries, 23 benchmarks, the gc_witnesses and the standalone tests), output and exit code matched a clean control in both modes, with both roads planted.

**The cure.** The pair now travels in `rcx/rdx` only. Its 16 bytes stay at the same depth as a `{DT_RAW, 0}` cell, carved by the new encoder helper `x86_rsp_raw_cell` (beside `x86_rsp_store64_imm`).

**The other frontends are untouched.**
- By construction: `x86_fb_pinned` is derived language-blind, but no other frontend's call reaches these two roads.
- By measurement: 4,565 non-Prolog programs (every other master's entries extracted, the gc_witnesses and the standalone tests) emit byte-identical asm against `2fdfa42e8`.
- The edit keeps every template line number. A first cut that added one line moved the `# gc_poll <file>:<line>` annotation of 279 programs, and the bare-poll witness table keys sites by that line.

**Measured:** crypt.pl in m3 went from 130,164 code-valued raw units to 69,522, and total raw from 239,588 to 178,946.

**What remains per Prolog call:** only the callee frame's top 32 bytes, `{stack word, γ copy}` and `{ω copy, caller rbp}`. The 32 bytes of `{DT_RAW, 0}` filler under the call (the landing cell and the pair cell) keep the old depth. They can go once the `add rsp,32` landings and the LCO's `lea r10,[rsp+16]; cmp r10,rbp` adjacency test are re-based.

## 6. The zframe's ω copy is a packed cell head (SCRIP `ba10ba29f`)

The unit `{kt-16 ω copy, kt-8 caller rbp}` now begins with `(ω << 8) | DT_RAW`. That is a non-pointer cell: the tag is the low byte, the payload is the rest, and a user-space address shifted by 8 still fits. The caller's rbp stays in the value half.

| Role | Sites |
|---|---|
| **Writers** (pack) | ICN-FR-2 zframe prologue; class-C chain prologue; the PL-DC arm's local ω shim; the class-C want-name park, which keeps its request in the same slot |
| **Readers** (unpack) | pinned ω exit; unpinned ω exit; the Prolog LCO's reload into rdx; the want-name restore |

The grep for `kt - 16` missed the want-name restore, because it reads `[rsp + kt-16+8]` after its own push.

**Encoders added, both media.** `x86_or_imm` and `x86_shift_imm` (shl/shr by imm8) are wired into `x86()`. Before this, `or reg, imm` returned an empty string: the silent-drop class. The helpers `x86_raw_pack`/`x86_raw_unpack` now exist.

**Measured:** crypt.pl in m3 went from 69,522 code-valued raw units to 2,806, and total raw from 178,946 to 112,231.

**Verification against `c8dc0d182`:**
- 1,735 of 5,246 programs changed asm: Prolog 627, Raku 960, Pascal 111, Snocone 37. Icon and SNOBOL4 are byte-identical.
- All 1,735 ran identically in both modes, except four Raku benchmark kernels that print their own timing; the control differs from itself on those too.
- The 18 changed gc_witnesses ran identically at 64 KB under `SCRIP_GC_STRESS=1`.
- Re-proved after rebasing onto hq_prolog's R4.2: 628 of 628 Prolog programs.

**The next unit:** `{kt-32 frame-top address, kt-24 γ copy}`. Its first word is a stack address, the bulk of crypt's remaining 92,986 stack-valued units. `kt-32` is the fifth word of the Prolog choice quad (`kt-64` r12, `kt-56` alternative, `kt-48` 0, `kt-40` r13, `kt-32` top) that `rt_pl_choice_open` and `rt_pl_quad_seed` receive.

## 7. The frame bound at `[B+32]` is packed too (SCRIP `648e2364e`)

The Prolog choice quad's fifth word is the frame bound: the zframe prologue seeds it with the frame top, and `rt_pl_disj_open` lowers it to the frame base. It is now stored as `(bound << 8) | DT_RAW`.

There are two readers, and both now go through `pl_tr_frame_hi` / `pl_tr_frame_hi_set` in `rt_pl_trail.h`:
- the emitted trail test `pl_trail_rdi`, which unpacks with one `shr`;
- its C twin `pl_tr_needs_log`.

**Negative control:** with the emitted reader's unpack removed, 123 of 627 Prolog programs answered differently, so the differential population does see this slot. `test_gate_pl_trail_mechanism` went red on the first cut because its fixture wrote a raw pointer; the fixture now writes through the setter.

**Measured on the same tree, `ba10ba29f` against this change:** crypt.pl in m3 went from 48,144 raw units to 19,701 (stack-valued 40,449 → 12,015).

## 8. A zframe root records its ceiling (SCRIP `d77359003`)

`rt_outer_call` records the emitted-stack ceiling. The zframe root's two entries did not: `icn_zf_main_call` in mode 3 and the emitted main's zframe arm in mode 4, which is the road of every Prolog and Raku main. Their walks stopped only through the "no map above the last frame" fallback, and L3 deletes that fallback.

The census over-counted for the same reason: it sweeps the whole segment it is handed. It read the C driver's frames, the environment strings and auxv as raw units. For crypt that was 179 units over 8 collections, 38 of them ASCII.

**The cure:** `rt_gc_emit_ceiling_adopt_top(top)`. A zframe root's frame top is its entry rsp, and the existing resolve verifies it at every collection.

**Verification against `648e2364e`:**
- 100 of 100 gc_witnesses ran identically at 64 KB under stress.
- 1,587 programs changed asm and all ran identically, except four Raku timing-only kernels.
- crypt now reads the same in m3 and m4.

## 9. No env chooses a frame placement (SCRIP `8b8ff531e`)

`test_gate_no_zeta_frame_switches`, a blocking gate, read my two road switches red: `SCRIP_LEAF_FRAME` and `SCRIP_BLOB_SPINE`. Both are deleted.
- The leaf road stays the spine.
- The frameless stored-pattern thunk (`a4a9efcce`) becomes the one road.

**Verification against `d77359003`:**
- 243 of 5,246 programs changed asm: 241 SNOBOL4 and 2 Snocone.
- 242 of them ran identically. The 243rd, `arb_pos_len_replace_1`, has a pre-existing nondeterministic diagnostic: an uninitialized `saved_delta` in `rt_dcap_pump`, routed to hq_snobol4.
- The 42 SNOBOL4-family gc_witnesses ran identically under stress.

In the same landing, the coo's other three standing blocking reds and frame_reuse rungs 2 and 3(e) had two causes:
- **Semicolons:** inline Icon witnesses without the semicolons CEO-1392 requires.
- **One fewer det leaf:** `r/1` now seals three det leaves. R4.1 (`734797863`) made the `r(0)` head constant an `IR_UNIFY_CONST` box; measured on that commit and its parent.

**Open, and red in rung 3(d):** the beta-capable `IR_UNIFY_CONST` writes `r/1`'s shared dead-result scratch. So the scratch no longer overlays the pooled slot at +32, and r/1's frame grows by 16 bytes.

## 10. The staged call's activation word is packed (SCRIP `16c530808`); and a GVA slot that is not a DESCR since `99d429d4c`

**The activation word.** After the zframe header, crypt.pl's remaining stack-valued units were all one record: `callgen.act` in `top/16`'s frame. `act+0` holds a state (0/1/2) or, on the Prolog arm, the callee frame; `act+8` holds the callee β or a saved rsp.

`act+0` is now `(v << 8) | DT_RAW`:
- the immediate states become `DT_RAW` and `0x100 | DT_RAW`;
- the Prolog γ landing packs a copy of rax in rcx, because rax is tested right after;
- the three readers unpack before they test.

**Measured:** crypt.pl now reads the same in both modes, raw 19,523 → 7,551, stack-valued 11,972 → 0.

**Verification against `8b8ff531e`:**
- 689 programs changed asm (Prolog 627, Icon 62) and all ran identically in both modes.
- 14 changed gc_witnesses ran identically under stress.
- **Negative control:** with one reader left packed, 123 programs answered differently.

**Open, the next landing:** `call_value`'s twin `H` record. Its word 0 (the `hslot`) is read and written by runtime C: 13 sites in `by_name_dispatch.c`, 6 in `rt.c` and 2 in `unification.c`. It can hold a ct-allocated `ICN_OPGEN_t*`.

**The GVA anomaly, bisected, sent to the cfo.** Since the cfo's `99d429d4c`, vscroll_driver.icn's GVA island carries one non-DESCR unit at about 1,191 of its 1,833 collections: word 0 is `0x70001070`, an r12-shaped value inside the DCAP island, and word 1 is a stack address. That reds arm (b) of this row's gate.

Readings with `SCRIP_GC_SWEEP16=1`, counting `pop=gva` raw units:

| Tree | GVA raw units |
|---|---|
| `2fdfa42e8` | 0 |
| `bf3b1b98b` | 0 |
| `99d429d4c` | 1,191 |
| every later tree | 1,191 |
