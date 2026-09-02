# ⛔⭐⭐⭐⭐ ARCH-PROLOG-THREE-ZETAS — PROLOG ON THE THREE ZETAS: THE REDESIGN (Lon, 2026-09-02)

**Provenance (Lon, in-chat to ceo, verbatim):** 09:55 *"So what are we waiting for, give Prolog its activation ZETA like all the rest. OMG! Go fix it."* — 10:00 *"The answer to how Prolog is doing is TERRIBLE. If we did not do proper THREE ZETAS for Prolog then go do a complete re design. I want that bad code deleted now. It has been too long coming."* Written by ceo the same hour from the law (RULES.md § BB FRAME-PLACEMENT CRITERION, § THE THREE ZETAS; GOAL-PROLOG-100 § s273 DESCR ruling) and a read-only sweep of the tree at SCRIP `5ebc7961` (every line cited below was re-read by ceo). hq_C owns the mechanism sections and fills them as it builds; hq_P owns the perf shape and the two deletions in its lane; hq_B owns Term-to-zero and the instruments. This page is the ORDER OF THE WORK for the Prolog lane until the program gate in § 6 reads green; MASTER-PLAN ladder C's head points here.

## 0. What was measured, and why it is terrible

- A two-clause `fact/2` under `SCRIP_PL_GAMMA_RETAIN=1` emits **0 rbp-relative instructions, 323 rsp-relative, 0 `push rbp`** (hq_B, pristine `5839cf13`, FINDING `a4a7cfff`); the committed `nreverse.s` (regen `884d8f91d`) contains **zero `rbp`**. Prolog has no activation frame; nothing survives γ for β to resume.
- Every Prolog graph is stamped `zframe_graph = 1` blanket (`src/lower/lower_prolog.c:1515-1516`); none sets the cells-frame property (`icn_cells_graph` is set only at `src/lower/lower_icon.c:1224,1338`), so the one operand-rebase point in the emitter returns 0 for Prolog (`src/templates/x86/x86_asm.h:850-854`, consumed at `:1003` and `:1020`) and every operand is spelled `[rsp+off]`.
- Prolog's γ polls a **global** for its resume cursor (`g_pl_zf_pending_cursor`, `src/templates/xa/xa_flat.cpp:365-390`) where Icon reads its frame header (`[H+32]`).
- Control that a port should carry lives in C: the `plc_*` solver for call/N (`src/runtime/by_name_dispatch.c:4565-4753`, `rt_pl_call_gen :4878`); three live `setjmp` barriers (`:1493` `dop_call`, `:4911` `rt_call_arr_bl`, `:5064` `rt_jct_relop`, two of them the Prolog failure path via `g_plw_unwind_floor`); a polled exception flag `rt_pl_throw_pending` checked at nine sites; a 27-way `strcmp` cascade for by-name builtins (`:5582`→); and a SECOND choice-point/trail/env machine in `src/runtime/builtins/resolution.{c,h}` (`RESOLVE_CP_STACK_MAX 4096`, `Term **env`).
- The boards say exactly this: master 351/371 both modes (the forward path α→γ works), rung suite **3/15** both modes with every red a backtracking shape, 8 of 21 van Roy kernels crash (the β path does not).
- History: Prolog once had an rbp-pinned zframe (the `vanroy/*.s` artifacts of 2026-07-29 show `mov rbp, rsp` and `[rbp+…]` operands); the RBP-ERADICATION wave `708c22c1` (`src/emitter/emit.h:546`) removed it and the FRAME-PLACEMENT law that followed was applied to Icon and never to Prolog.

## 1. The law, applied to Prolog (no new law — the existing one, obeyed)

Prolog is the language the Byrd box came from; it is not a special case of THE THREE ZETAS. For every Prolog graph:

- **ζ-SPINE on RSP** — a box's operands whose every consumer reaches them at a fixed compile-time offset inside ONE activation with no unbounded growth between producer and consumer (head-unification temporaries, arithmetic scratch, builtin argument staging).
- **ζ-ACTIVATION-FRAME on RBP** — the predicate call's frame: parameters, clause locals, the clause cursor (which alternative is current), the trail mark, the resume label, the saved caller base, γ and ω wires, the cut barrier (= this frame's identity). It is carved at α and **survives γ** so β can re-enter it (the γ→β window is the canonical unbounded-growth case of the FRAME-PLACEMENT CRITERION); it is released only at ω. A suspend-surviving frame carves inside the enclosing graph's frame exactly as Icon's generators do (host reserve, transitive).
- **ζ-STANDING** — the predicate table, the dynamic-database index, the atom table, flags and stream state: root, process lifetime, never per activation.
- ⛔⭐⭐ **THE STACKS AND LISTS LIVE INSIDE THE BOX (Lon, 11:00, verbatim: *"Do you see how a BB is a pure-functional entity with the stacks and lists moved INTO the BB box, not a global value stack or choice point stack. Those structure live INSIDE the BB."*).** A Byrd box is a pure-functional entity: everything it needs to proceed, recede, succeed or concede is in its own ζ. For Prolog that means, concretely — the CHOICE POINT is the call box's own frame fields (the clause cursor, the saved sub-goal resume label); there is no choice-point stack (`rt_pl_cp_push3`/`rt_pl_cp_pop3` go). The TRAIL is each activation's own BINDING LOG — the cells this activation bound — unwound by this box's ω and on every β re-entry; the frame boundary IS the mark, so there is no global trail area and no mark integer (`g_pl_trail` + `pl_trail_mark`/`pl_trail_unwind` as a global go; the log is a frame-local list, promoted to the heap only if the frame is retained across a γ and grows without bound — the FRAME-PLACEMENT CRITERION decides, per box, never a global). The findall/bagof/setof ACCUMULATOR is a list in the collecting box's frame, promoted to heap cells only when it escapes at the end (the result unification). The EXCEPTION BALL travels on ω in registers/frame, box to box, until a catch box's β claims it — no global slot. The RESUME POINT is a frame field, never `g_pl_zf_pending_cursor`. Icon is the working example for every one of these: a generator's suspend keeps its state in its own retained frame and β re-enters it (`bb_call_proc_staged.cpp:880-885`); `every` and alternation are β into that frame; no generator stack exists. SNOBOL4 pattern matching is the register-aware form: an alternation box's β tries the next alternative with the cursor saved in its own ζ, ARBNO's count lives in its ζ, the subject cursor rides the r10/r11 wires and every operand sits at a compile-time offset — no call per step. Prolog's head unification and clause selection take that shape: cells in registers, offsets fixed at compile time, the log and the cursor in the frame.
- **Heap** — only genuine escapers: DESCR cells that outlive the activation (bindings into caller structures, findall/bagof results, asserted clause bodies); never frames, never control.

## 2. The box map — every construct onto α β γ ω

| construct | box and ports |
|---|---|
| predicate call `p(A,B)` | one box: α carves the frame, unifies the head of the current clause; γ succeeds with the frame RETAINED and the resume label banked in the frame; β re-enters at the resume label — redo the youngest sub-goal, or step the clause cursor to the next alternative; ω releases the frame after unwinding the trail to the mark |
| clause alternatives | the call box's β path: the clause cursor is a frame field (no choice-point stack; `rt_pl_cp_push3`/`rt_pl_cp_pop3` go); the last clause's β is the box's ω |
| conjunction `A, B` | α→γ chaining forward, γ→β chaining backward — already a box graph |
| cut `!` | the enclosing call box's ω applied to all younger alternatives: the cut barrier is the frame's identity (`bb_cut.cpp` today is α/γ/β-trampoline only; it gains the barrier), never a global flag |
| if-then-else, `\+`, `once`, `ignore`, `forall` | the existing box graphs (`lower_ite`); the runtime guard `$no_throw_or_fail` on the condition's ω edge LEAVES — the condition's ω is the edge |
| call/N and every goal unknown at compile time | compiled at run time through the EVAL/CODE runtime-compilation path (graph → optimizer → `emit_chain` → jump), then an ordinary call box (C36; the `plc_*` solver is deleted) |
| catch/3 | a box whose handler sits on its β with the ball match; `throw/1` is ω-with-ball propagating frame by frame until a catch box's β claims it — no polled flag (C37) |
| findall / bagof / setof | the forced-fail β loop already lowered (`lower_prolog.c:552-580`); the collect and group services (`rt_pl_findall_*`, `rt_pl_bag_*`) stay as value services on cells |
| the trail | β's undo, as THIS activation's own binding log in its frame: the cells this box bound, unwound by its ω and on every β re-entry; the frame boundary is the mark — no global trail area, no mark integer, no `g_pl_trail` (P10 is subsumed: there is no slot to relocate) |
| dynamic predicates | ζ-STANDING index + heap cells (the 2026-09-01 interpretation in GOAL-PROLOG-100) |
| builtins | bound at compile time to their `dop_*`/`rt_pl_*_cell` bodies (P6); no string reaches the runtime |

## 3. The mechanism (hq_C fills the sub-sections as it lands; the seam facts are fixed)

- **One rebase point, one key.** The entire rbp-vs-rsp operand switch is `icn_gen_zeta_ft()` (`x86_asm.h:850-854`) feeding `x86_zop` (`:1003`) and `x86_zref` (`:1020`); its key is `icn_gen_regime()` (`:2111-2112`) = the killswitch `icn_genframe2()` AND `g_emit_cfg->icn_cells_graph`. The design: the key becomes a LANGUAGE-BLIND IR graph property — rename `icn_cells_graph` (`src/ir/IR.h:233`) to `cells_graph`, set by `lower_icon` where it is set today and by `lower_prolog` for every predicate graph; the emitter never names a language (`test_gate_emit_no_lang.sh` polices it). ⚠ Hazard on record at `x86_asm.h:2111`: widening the key via bare `flat_gen` once dropped Prolog smoke 5/5 → 3/5, because a Prolog suspend graph took the region α without the host reserve. The cure is the property PLUS the reserve, never a language check.
- **The frame is Icon's frame, region-resident.** Icon's α (`src/emitter/emit.cpp:2955-2977`) carves nothing on the machine stack: `rbp` is loaded from a caller-supplied region pointer at `[rsp+16]`; the header `H` holds `[H+0]` saved caller rbp, `[H+8]` γ, `[H+16]` ω, `[H+24]` anchor, `[H+32]` resume label; `frame_total = flat_frame_bytes + (nparams+nlocals)*16` (`:2952`), plus the host's reservation for its generator callees (`icn_gen_host_reserve`, `:2988`). Prolog adopts this header and this β-resume protocol (`src/templates/bb/bb_call_proc_staged.cpp:880-885`: `mov rax,[act+8]; mov rsp,[rax+24]; sub rsp,40; jmp [rax+32]`; landing at `emit.cpp:3352-3356` repoints rbp and does NOT release) — hq_C decides whether the frame's storage rides the enclosing frame's reserve (as Icon) or the machine stack directly under RBP, and records the measured reason. ⚠ Icon's reserve accounting (`bcps_spine_gen_arm`, `icn_gen_host_reserve` transitivity) must come with it or the region under-carves.
- **The resume wire becomes a frame field.** `g_pl_zf_pending_cursor` / `rt_pl_zf_resume_set` / `rt_pl_zf_resume_clear` (polled in Prolog's γ arm, `xa_flat.cpp:365-390`) are deleted; the resume label lives at `[H+32]` as it does for Icon (PZ-5's "delete the pending mailbox" is this line).
- **The stubs answer or die.** `x86_fb_pinned()` returns constant 0 and `x86_fb()` constant `"rsp"` (`x86_asm.h:478,484`), which makes three emitter gates dead (`emit.cpp:2168, 2208, 2215`). Either they answer rbp for cells graphs or they and their dead gates are deleted; a stub that can only say rsp must not remain as a "shared pin machinery" anyone designs against.
- **The killswitch is the existing one.** `icn_genframe2()` (env `SCRIP_ICN_GENFRAME2`, default ON) becomes the cells-frame killswitch for both languages — one control arm, proven in the FAIL direction on the `fact/2` witness before the cure lands (INSTRUMENT LAWS).
- **The falsifiable milestone-1 test for PZ-4 (hq_P, from the flapping):** a corrupt trail mark that sometimes crashes and sometimes gets caught is reading memory whose content differs between runs — exactly § 0's mechanism, a retained frame living below rsp and clobbered by whatever the next call writes there. Prediction: IF the frame is genuinely protected, the per-kernel per-rep outcome strings go CONSTANT (whatever value they take) before any count improves. hq_C tests that on the first milestone with `bench_prolog_vanroy.sh`'s per-rep output; a milestone that leaves them flapping has not protected the frame.
- **GC roots.** The collector scans by address range (`src/runtime/rt/gc_heap.c:341-351, 606, 661, 668`), not by frame kind; whether a region-resident Prolog frame's cells fall inside a scanned range is NOT verified — a rung of PZ-4 with a witness that allocates during a retained frame and collects.


### 3a. What landed (hq_C, 2026-09-02, PZ-4 clause (a) — SCRIP commit named in the FINDING below)

**The pin, and the measured reason it is post-carve.** Every Prolog predicate graph now carries its ζ-ACTIVATION
frame in a pinned base register: α is `sub rsp,kt` · wire header `[kt-24]=γ [kt-16]=ω` · **`[kt-8]=caller base`** ·
**`rbp = rsp`**. γ and ω restore the caller's base through the pin (`mov rbp,[rbp+kt-8]`) before releasing. The
storage decision this section left open is taken: **the machine stack directly under RBP, pinned AFTER the carve**
— not Icon's region-resident frame, and not Icon's pre-carve pin. The reason is measured, not preferred:
hq_P (`adc17766`) showed Icon's `[rbp + off - ft]` rebase rests on an invariant ("rsp does not move between α and
γ") that is FALSE for a Prolog body — 34 rsp moves on the fact/2 witness including a `pop rsp`, past which no
static displacement exists. Pinning after the carve makes the rebase plain `off`, needs no per-site rsp-delta,
adds no `push` (so the two PL-CALL-ALIGN pads stay correct), and needs no new slot: `[kt-8]` was a write-only
self-anchor (s247) and now holds the caller base. Proof it is a pure rebase: normalising `rbp→rsp` in the pinned
`.s` and diffing against the killswitch arm of the same binary leaves exactly the pin/restore lines — **zero ζ
offsets changed**. Witness census: rbp-relative lines 0 → 164.

**The key, and why it is not the `cells_graph` rename above.** The pin is keyed on a new language-blind IR graph
property `zframe_pinned_base`, set by `lower_prolog.c` alone; the emitter asks `emit_zframe_pinned()` and nothing
else. It is NOT `zframe_graph` (Raku and Pascal set that too — they would have been re-homed silently) and it is
deliberately NOT the `icn_cells_graph → cells_graph` widening proposed above: that grant carries Icon's
region-resident α, host reserve and bcps generator arm along with the rebase, which is the exact widening the ⚠
hazard at `x86_asm.h:2111` records as dropping Prolog smoke 5/5→3/5. Two regimes with different pin arithmetic
cannot share one `ft`; they share the ACCESSOR (`x86_fb`/`x86_zop`/`x86_zref`) and keep their own keys.

**The stubs answer.** `x86_fb_pinned()` = `emit_zframe_pinned()`; `x86_fb_num()` answers 5 under it; `x86_fb()`
is DERIVED from the number (never a second literal). Both ζ families (FR through `x86_fb`, SPINE through
`x86_zref`/`x86_zop`) move on the same predicate; `x86_frame_off()` drops `op_zdepth` under the pin. Killswitch:
`SCRIP_PL_ZA=0` — byte-identical `.s` to the pre-change build, proven on the fact/2 witness.

**Not landed by this step — the row is open:** (c) the caller landing re-anchoring off its own pin (the
`bb_call_proc_staged.cpp:773` bomb's stated blocker is now false and its text needs (c)); (d) the CP stack stores a
bare address with no base (`rt.c:1746-1765`) — the nested-activation backtrack witnesses (`nested.pl`, `deep.pl`)
crash in BOTH arms today, pre-existing, and are the graded witnesses for (d); (f) top-graph exclusion and the
`SCRIP_PL_GAMMA_RETAIN` flip; and the exact release `lea rsp,[rbp+kt]` in place of `add rsp,kt`, deliberately
withheld from this step to keep the rebase pure and gradeable.

## 4. The deletion list (each a rung; DONE-WHEN = the symbol absent from `src/` and from `nm -D out/libscrip_rt.so`, boards not worse)

| what leaves | where it is today | row |
|---|---|---|
| the `plc_*` solver (23 definitions), `rt_pl_call_gen`, `rt_call_arr_impl`'s route into it, the `plc_rd_*` runtime term reader | `by_name_dispatch.c:1135-1236, 4565-4893, 4992` | C36 |
| **P7a (now, behaviour-free):** `dop_call`'s `setjmp` + the errjmp push/pop around it — Prolog-only and DEAD for Prolog (hq_P measured 2026-09-02: `core_runtime_error` longjmps only when `g_error` is armed, and nothing in the Prolog frontend arms it; a raising Prolog builtin exits before any barrier). **P7b (only AFTER PZ-4 (b), the trail as each frame's own log):** `g_plw_unwind_floor`, `g_plw_floor_bypass`, `rt_plw_floor_bypass_on`, `dop_call_nothrow` + its two wrappers — the dead-C-stack floor is the guard that makes a corrupt mark a REFUSE instead of a CRASH (`pl_cell.h:66-81`; `72c7ec09` relies on it); delete it earlier and the van Roy gate reads a regression, correctly. ⛔ CORRECTION to the first draft: the barriers in `rt_call_arr_bl` (`:4911`) and `rt_jct_relop` (`:5064`) are SNOBOL4/Icon `&ERROR`-to-failure trapping on SHARED nodes (`bb_call_fn.cpp`, `bb_binop_relop*.cpp`, `bb_to*.cpp`; Prolog never reaches them) — they are NOT on this list; only the two `g_plw_unwind_floor` lines inside `rt_call_arr_bl` are Prolog's | `by_name_dispatch.c:1486-1600, 4872-4875` | P7a · P7b |
| the by-name cascade for Prolog: `try_call_builtin_by_name_bl`'s Prolog arms, `script_try_call_builtin_by_name` (19 refs), the `.L…rkfn` string literals in emitted code, the 21 `rt_pl_dop_*` wrappers (their `dop_*` bodies stay and are called directly) | `by_name_dispatch.c:5582→`, `arithmetic.c` | P6 |
| `rt_pl_throw_pending`, `g_pl_throw_ball` polling (nine sites), `$catch_check`, `$no_throw_or_fail` | `unification.c:2324-2341`, `by_name_dispatch.c:1148,1409,2721,2735,4698-4730`, `lower_prolog.c:295-311,365-383` | C37 |
| `g_pl_zf_pending_cursor`, `rt_pl_zf_resume_set/clear` | `xa_flat.cpp:365-390`, runtime | PZ-5 |
| the global trail area and mark protocol `g_pl_trail`, `pl_trail_mark`/`pl_trail_unwind` as globals, `rt_value_trail_*`, `g_pl_env_area`; the runtime choice-point stack `rt_pl_cp_push3`/`rt_pl_cp_pop3` | `resolution.c:20-52`, `pl_cell.h:53-81`, runtime | PZ-4 clauses (b)–(f): the log and the cursor move INTO the frame |
| the second choice-point/trail/env machine: `resolve_choice` CP stack, the catch stack, `Term **env` layer, `g_resolve_trail`, `g_resolve_cut_*` | `src/runtime/builtins/resolution.{c,h}` | T7 (s7) |
| `Term`, `term.h`, `pl_cell_conv.h` (75 word-refs at `5ebc7961`) | `src/parsers/prolog/`, `unification.c`, `resolution.h` | T9 |

## 5. What stays — value services, callable from wired code

`unification.c`'s cell services (132 definitions: unify, bind, compare, sort, copy_term, write/format on cells, findall collect, bag group), arithmetic on cells (`rt_runtime.c:111-255`), the trail primitives (`pl_cell.h:53,55,81` — the mark's HOME moves into the frame, the primitives stay), atom interning (`prolog_atom.c`), cell allocation and GC roots (shared), the 22 `dop_*` bodies (called directly), stream and I/O builtins. A value service returns a value and touches nothing else; a call that also initialises, interns, or marks is named as such on its baton (the milestone-3 lesson: a deleted round-trip carried the atom-table init).

## 6. Order and gates

**Order:** PZ-4 (the frame; C21, hq_C, first) → PZ-5 (in-frame resume; the mailbox goes) → C36 (call/N through the runtime compiler; solver deleted) → P7 (setjmp failure/cut out; hq_P) → P6 (by-name cascade out; hq_P) → C37 (exceptions through ports) → T9 to zero and T7 (resolution layer gone; hq_B). Every other Prolog rung queues behind these; the seats' partial branches (`wip/prolog-call-n-metacall-synthesis`) are inputs, not rungs.

**Per-milestone gates (shared-node scope — Prolog lowers to the shared boxes):** Prolog master board both modes ≥ 351/351 of 371 · Prolog smoke 5/5 both modes · SNOBOL4 floor FAIL=0 both modes · Icon's pinned watermark (the frame code is Icon's) · the Term ratchet not rising · every conversion consumed the hard way (write/compare of every converted class, five runs).

**Program gate (the DONE-WHEN of the redesign):** rung suite **15/15 both modes** · van Roy **REFUSE 0 AND CRASH 0 AND CLEAN ≥ the pinned floor, classified WORST-OF-N** (hq_P's gate SCRIP `d562fa6c`: each kernel runs N times, default 3, and counts CLEAN only if clean on every pass; any single counter alone is gameable — three refusals turning into crashes would read "REFUSE 0" with 16 of 21 crashing — the three together are not; measured 2026-09-02: eleven of the 21 kernels FLIP between REFUSE, CRASH and CLEAN across four passes of ONE unchanged binary) · `nm -D out/libscrip_rt.so` names none of the § 4 symbols · `grep -rcw Term src` = 0 and both headers absent · the `fact/2` witness emits rbp-relative frame addressing · C22/C23/C24/C26's witnesses green · master board not worse than 351/351.

## 7. Things this page must not let anyone get wrong

1. "Give Prolog the RBP frame Icon has" is ONE key at ONE rebase point, not forty edits — and that key was widened wrongly once (`x86_asm.h:2111`). Property plus reserve, never a language name.
2. Icon's frame is region-resident; porting the prologue without the reserve accounting under-carves the host.
3. A `BLOCKED-ON` edge names a row; a rung waits for a MECHANISM. PZ-4 sat "unblocked" for a day because P1 landed the arrival-depth half and not the frame. Re-measure the precondition, never inherit it.
4. The shallow board is not the health of the language. 351/371 with 3/15 on the deep rungs was read as progress for two days. The rung suite and the van Roy REFUSE count are the numbers this program is graded on.
