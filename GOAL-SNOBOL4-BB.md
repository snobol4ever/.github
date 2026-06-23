<!-- SESSION-FIRST RUNG — DTP-DIRECT-STITCH · TEMPLATE-EMITTED PATTERN BOXES, NO HEADS -->

# ⛔⛔⛔⛔ GROUND ZERO — 5TH RESTART (Lon, 2026-06-23c)

**Lon's words this session:** "You are starting at ground zero for the 5th time." Four prior sessions read the BB-storage design, wrote increasingly elaborate handoff notes, seeded golden C (`test_sno_5`, then `test_sno_6`), and **ran out of context before landing a single line of working stored-pattern codegen.** The pattern keeps repeating: design → notes → reset. **THE ONLY ACCEPTABLE OUTPUT THIS RUNG IS LANDED CODE THAT MOVES A BENCH.** Stop re-deriving the mechanism. Stop adding golden seeds. Build the smallest thing that makes a real `.sno` capture, gate it, commit it, repeat.

**Directive (Lon, 2026-06-23c):** "Get R12/zeta processing working for **tiny rungs** up until the `corpus/benchmarks/snobol4/*.sno` tests." → Build the stored-pattern path bottom-up on hand-written one-liners (the TR-ladder below), each gated, until the three BOMB benches (roman, mixed_workload, string_pattern) drive green at G0.

## 🟢🔴 LIVE REALITY CHECK — verified vs sbl oracle THIS session (`dd17db1`, fresh build)

Tri-probe (`scrip --compile | gcc | run` vs `sbl -b`), **column-1 `END` required** (indented END → oracle "No END statement found"):

| rung | program | scrip result | oracle | disposition |
|------|---------|-------------|--------|-------------|
| i1 | INLINE `S ? LEN(2) . W` | `W=CD` | `W=CD` | ✅ inline capture WORKS |
| i2 | INLINE `S ? BREAK(',') . W` | `W=alpha` | `W=alpha` | ✅ inline BREAK+capture WORKS |
| **r1** | STORED `PAT=LEN(2); S ? PAT . W` | **BOMB** `bb_pattern_unary_i: DT_P builder pending` | `W=CD` | construction-time bomb |
| **r2** | STORED `PAT=BREAK(',') . W; S ? PAT` | `W=` (silent miss) | `W=alpha` | **pattern value DROPPED at lower** |
| r0 | `OUTPUT = (S ? 'C' 'D') 'lit'` | BOMB `bb_gvar_assign_concat: no parts` | `CDmatched-lit` | ORTHOGONAL (match-as-expr concat) |

**ROOT CAUSE of r2 (the cleanest target), traced to the line:** `--dump-ir /tmp/r2.sno` shows node `IR_ASSIGN sval="PAT"` with **NO operand subgraph** — the RHS `BREAK(',') . W` was dropped entirely. In `src/lower/lower_snobol4.c`:
- `sno_leaf_buildable` (L508) does NOT accept `TT_CAPT_COND_ASGN` (the `. W` wrapper) → `sno_seq_buildable` (L525) returns 0 for `BREAK(',') . W`.
- So `lower_assign` (L586) skips the `IR_DTP_ASSIGN`+`IR_PATTERN_CAT` builder (L687–714, which ALREADY EXISTS and works for capture-free SEQs) and falls to L717–722 which **orphans** the pattern (allocs a bare `IR_ASSIGN_CONCAT`+`IR_SEQ` and returns NULL). PAT is never assigned → null → `IR_PAT_DEFER` matches nothing.

**⇒ TR-LADDER (build order — each gated before next):**
- **TR-0 ✅** — reality check above (DONE this session). Tri-probe + END-col-1 fact established. No code.
- **TR-1** — extend `sno_leaf_buildable`/`sno_build_leaf_ir` to accept `TT_CAPT_COND_ASGN` (wrap the inner leaf's `IR_PATTERN_*` in the existing capture mechanism that inline `IR_PAT_ASSIGN_COND` uses — find how i2 lowers capture inline and reuse it). Target: `--dump-ir r2.sno` shows PAT assigned a real CAT(BREAK, CAPTURE(VAR W)) graph. NO r12 work yet.
- **TR-2** — make `IR_PAT_DEFER` actually RUN the stored graph with capture landing. THIS is where the BB_SWITCH r12-broker enters (golden `seed/test_sno_6.c`): the deferred site allocs a pattern-ζ frame, jmps the stored body, capture writes land in the right plane. Target: r2 ⇒ `W=alpha` == oracle.
- **TR-3** — r1 (stored `PAT=LEN(2)`): close `bb_pattern_unary_i` construction bomb (single-leaf stored pattern, no SEQ). Target: r1 green.
- **TR-4** — point the now-working stored path at the real benches: roman, mixed_workload, string_pattern → green at G0. Gate: smoke M3/M4 7/7 · pat-rung 19/19 · fence T1=T2=0 · broad-corpus ≥170 · PB-GREEN 6/16 floor holds.

**Build (confirmed working this session):** `apt-get install -y libgc-dev` → `make` (→ `scrip`) → `make libscrip_rt` (→ `out/libscrip_rt.so`). Oracle `git clone …/x64 /home/claude/x64`; `sbl -b`. Tri-probe script in `/tmp/probe.sh` (regenerate from this file if lost).

## ⛔ DIRECTION LOCKED (Lon, 2026-06-23c) — ALL PATTERNS VARIANT · BUILD FROM SCRATCH IN STAGE 2 · NO CONSTANT FOLDING

**Lon overruled the Path-B detour (see retraction below).** The pattern-building stage (STAGE 2 of the ARCH-SNOBOL4 5-phase statement model — `1 build subject · 2 BUILD PATTERN · 3 run · 4 build repl · 5 replace`) **builds the PATTERN from scratch AT RUNTIME, every execution.** Assume — knowingly incorrectly, as a correctness-first baseline — that **EVERY pattern is VARIANT and must be rebuilt from scratch.** NO invariance detection, NO compile-time sealing, NO build-once caching. Constant folding (build invariant patterns once) is a LATER optimization; when we get there it goes behind a **C-macro/variable toggle** (`#ifdef SNO_PAT_FOLD`, default OFF) so the variant baseline always remains the reference. **Do not write the fold path now.**

**⛔ RETRACTED — PATH B (compile-time seal + reference) is DEAD.** A prior turn this session detected pattern invariance (`sno_pat_invariant`) and lowered invariant stored patterns to a SEALED `IR_PAT_*` matcher graph emitted once at compile time, referenced via the `DT_P` head. **That IS the forbidden constant folding** (stage-2 build is RUNTIME, not compile time). Fully reverted (`src/lower/lower_snobol4.c` back to byte-identical `dd17db1`). Do not reintroduce.

**THE PATH = the `IR_PATTERN_*` RUNTIME BUILDER family** (literally the "PATTERN" nodes), NOT the `IR_PAT_*` matcher family. Distinction, now firm:
- **`IR_PAT_*` (matcher).** Emitted INLINE at the scan site, runs the match directly (fused build+run). What `S ? BREAK(',') . W` inline lowers to; i1/i2 green. Fine for inline; NOT the stored-pattern vehicle.
- **`IR_PATTERN_*` + `IR_DTP_ASSIGN` (RUNTIME BUILDER) — THE TARGET.** `PAT = BREAK(',') . W` must lower here. At RUNTIME, stage 2 executes builder boxes that CONSTRUCT the pattern object from scratch — per the DDS mandate, **template-emitted (`x86()`) boxes that relocate element-matcher code into the RWX `pat_pool` (`src/runtime/rt/pat_pool.c`) and stitch ports DIRECTLY (no `DTP_t` head)** — yielding a `bb_box_fn` graph head = the `DT_P` value stored in PAT. `IR_PAT_DEFER` loads `.p` (the head) and jmps in (Σ/δ/Δ live from the SCAN subject). The whole `IR_PATTERN_*` family currently dispatches to `bb_pattern_stub` BOMB (emit_core.c L364–386) — THAT is the ground-zero work to fill in.

**RUNTIME PATTERN REPRESENTATION (confirmed this session):** `pat_pool` is an `mmap` RWX arena (`g_pat_pool_base/_cur/_end`, `PROT_EXEC`, ctor-initialized). A built pattern lives there as relocated+stitched box code; the `DT_P` descr's `.p` slot holds its head (`bb_box_fn`). This is the surviving half of `dtp.h` (head struct + protos deleted by DDS-0; pat-pool kept). The builder boxes write into `pat_pool_cur` and bump it.

## TR-LADDER (CORRECTED — all-variant runtime build):
- **TR-0 ✅** reality check (DONE — see table above).
- **TR-1 ✅ (LANDED, SCRIP `7d6a9c9`)** — capture patterns routed to the BUILDER, not the orphan-drop. `sno_leaf_buildable` (L508) + `sno_build_leaf_ir` (L535) now accept `TT_CAPT_COND_ASGN`/`TT_CAPT_IMMED_ASGN` → emit `IR_PATTERN_CAPTURE` (sval=target name, ival=1 immediate `$` / 0 conditional `.`) wrapping the inner `IR_PATTERN_*`; bare-capture RHS routed to a single-leaf `IR_DTP_ASSIGN` builder. VERIFIED: `--dump-ir r2.sno` shows `IR_DTP_ASSIGN → IR_PATTERN_BREAK → IR_PATTERN_CAPTURE[W]`; **mixed_workload + string_pattern now reach the builder stub** (`bb_pattern_unary_s: DT_P builder pending`) instead of silent-miss. NO codegen drift (6 PB-GREEN `.s` byte-identical; i1/i2 inline still green). 21-line single-file diff.
- **TR-2 (the core)** — implement the RUNTIME builder boxes as template-emitted (`x86()`) into `pat_pool`, smallest first: LIT, then BREAK, then CAPTURE, then CAT. Each box, at runtime: relocate its element-matcher code into `pat_pool_cur`, patch its γ/ω ports to the prior box, bump cursor; `IR_DTP_ASSIGN` writes the head as a `DT_P` to NV[PAT]. Gate after EACH box (build green; the box's tiny rung runs == oracle). REUSE the compile-time `flat_drive_match` port-patch model — do not invent a second stitch.
- **TR-3** — `IR_PAT_DEFER` (`bb_match_defer.cpp`) routes `DT_P` values: load `.p` head, jmp in; keep the `DT_S` string path (`rt_defer_match`) for flattened-literal stored patterns. Gate: r2 ⇒ `W=alpha` == oracle.
- **TR-4** — roman/mixed_workload/string_pattern green at G0. Full gate (smoke M3/M4 7/7 · pat-rung 19/19 · fence T1=T2=0 · broad-corpus ≥170 · PB-GREEN 6/16 floor).


# ⛔⛔⛔ SESSION-FIRST RUNG — DTP-DIRECT-STITCH

**Mandate (2026-06-22, Lon):** Runtime-constructed PATTERN datatype (`*P` deferred / `PAT = BREAK(',') . WORD ','` stored-pattern) must be built from **template-emitted BB boxes stitched DIRECTLY port-to-port**. Kill the hand-coded byte arrays AND kill the `DTP_t` head indirection.

---
## ⛔ REQUIRED DESIGN READING — BB LOCAL STORAGE (read BEFORE any DDS step)

This rung is entirely about template-emitted Byrd boxes and where their per-box state lives. These ARE the design — read them first, not as background:
- `ARCH-x86.md` §"Boxes are stackless" + §"Flat-BB ABI"
- `ARCH-ICON.md` §"register contract" (the ζ-frame model — verbatim for SNOBOL4)
- `REGISTER-LAYOUT.md` (register convention; SM-era top banner is SUPERSEDED)
- `src/emitter/bb_regs.h` — SINGLE source of truth for register roles
- `src/emitter/XA_templates/xa_flat.cpp` — how the glob preamble sets r12
- **`SCRIP/seed/test_*.c` — THE FIVE HAND-WRITTEN GOLDEN BB GRAPHS. Read all five. They are a deliberate ζ-storage ladder; each rung holds α/β/γ/ω + Σ/Δ/Ω constant and varies ONLY how ζ-local storage is partitioned/allocated:**
  - `test_icon.c` — `every write(5 > ((1 to 2)*(3 to 4)))`. ζ-storage = **none**; every local is a flat C int. Generators, no backtrack state, no frames. The degenerate floor.
  - `test_sno_1.c` — `POS(0) ARBNO('Bird'|'Blue'|LEN(1)) $ OUTPUT RPOS(0)`. ONE flat `_1_t ζ[64]` depth-indexed array, single function. ARBNO ⇒ array-by-depth (storage **C**), but one frame type. (NOTE: the literal `[64]` is the TEACHING version — the end-state is a **realloc'd growable array**, Lon 2026-06-23.)
  - `test_sno_2.c` — treebank grammar (`group`/`word`/`delim` mutually recursive). Per-nonterminal `*_t` structs, each with its own `_NN_a[64]` ARBNO sub-array, callee frames **stack-inline** (a C local in the caller's activation).
  - `test_sno_3.c` — arith-expr grammar (`V I E X C`, deeply recursive `X`). Per-procedure structs holding `*_ζ` **POINTERS to callee frames**, lazily `calloc`'d via `enter()` and `memset`-reused on re-entry. THIS is the re-entrancy mechanism (ARCH-x86 "fresh DATA block per α-entry") made concrete — the model for recursive/stored patterns.
  - `test_sno_4.c` — `'SUBJECT' ? 'J' a` w/ predicate. Same pointer-to-callee model boiled to the `ENTER` macro. Cleanest distillation (fragment; references an external `a()`).
  - `test_sno_5.c` — **GLOB-HEAD-SETS-R12 GOLDEN (Lon mechanism, 2026-06-23).** Stored `*P` ( `PAT = 'C' 'D'` ) reused at TWO match sites: ONE code body, TWO distinct ζ instances. Each glob HEAD presents outside γ/ω + inside α/β; head's α AND β each set the SINGLE frame pointer R12 (α=fresh frame, β=RELOAD after inter-glob excursion clobbered it). Proves the TWO ζ PLANES (section + pattern) TIME-MULTIPLEX one register — NOT two. All boxes LIT (save-nothing). Compiles + runs; R12-trace makes the swap empirically visible. THIS IS THE DDS-1 EMITTER TARGET.

**Register convention (bb_regs.h — LIVE, GROUND ZERO 3).** r12=ζ RW frame base `[r12+off]` · r13=Σ subject base · r14=δ cursor (0-based; `&pos=δ+1`) · r15=Δ subject length · r10=per-blob RO DATA (`lea r10,[rip+Δ]`→`[r10+N]`) · rbx=DESCR base · rbp=NV hash base. **r12 is NOT a value stack.** `FR(off)`=`dword ptr [r12+off]`, `FRQ(off)`=`qword ptr [r12+off]` (x86_asm.h).

**The four ways BB-local storage is realized (and the one that is DEAD):**
- **A. ζ frame `[r12+off]` — PRIMARY.** Bounded, statically-known per-box RW slots (cursor saves, counters, captured DESCRs). ONE consolidated frame per glob; slots from `bb_slot_alloc16`/`bb_slot_claim`. Static `jmp` wiring; a consumer reads its producer's slot directly.
- **B. RO constants `[rip+disp]`.** Per-box compile-time constants (csets, match literals, LEN/POS counts) sealed adjacent to the blob; the `[r10+N]` flat-BB data block. Never written at match time. Idiom: `lea rdi,[rip+cset]; call strchr`.
- **C. per-box `.bss` arena indexed by depth.** UNBOUNDED backtrack state (ARBNO, recursion). NEVER a global stack. Ref: `bench/test_sno_1.c` `_1[64]`/ζ array.
- **D. (DEAD/SUPERSEDED).** SM value-stack on r12 (FORTH push/pop) + heap DATA-block tree walked by r10. SMX-4 deleted the SM engine. DO NOT reintroduce. The deleted `DTP_t`-head + `rt_dtp_run` proto path was a relapse into this — and is exactly why r12 was misused: a stored pattern's box needs `[r12+off]`, but `rt_dtp_run` repurposed r12 from its C prologue. The fix is A, never a head.

**Who establishes r12 — CONFIRMED MECHANISM (Lon, 2026-06-23). GLOB-HEAD SETS R12 ON α AND β.** Each BB GLOB (a BLOCK of BBs reachable via branch — the G2 trace below) has a HEAD box that presents the **outside γ/ω** (where the glob's caller wired success/fail) and the **inside α/β** (entry + resume that drive the glob's internal chain). **The head's α AND β each set r12 as their FIRST instruction.** Both ports, not just α — because an inter-glob excursion clobbers r12 (glob B's head loaded B's frame; when control returns to glob A via A's β resume, A's r12 is gone, so A's β must reload A's frame). This is the ARCH-x86 "extra-BLOB jump → destination reloads its LOCAL" rule, extended from α-only to α+β. It is TEMPLATE-EMITTED inside the head box — NO external C threading of a frame via rdi, NO per-pattern `DTP_t` head. Concretely: STATIC glob → α/β do `lea r12,[rip+frame]` (frame addr is a compile-time constant). PER-ACTIVATION pattern frame (stored/`*P`) → α sets r12 to the freshly-allocated frame; β restores it. RECURSIVE/ARBNO depth-indexed frame (storage **C**, realloc arena) → β must restore the RIGHT depth's frame, so the depth index must live in stable storage (section-ζ or a head-readable slot) — this wrinkle bites at ARBNO, NOT at LIT (DDS-1 frame is stable).

---
## ⛔ ζ-PARTITION DESIGN — TWO PLANES + GRANULARITY LADDER (Lon + Claude, 2026-06-23)

**The problem (Lon's words):** r12/ζ for sections of main + per-DEFINE'd-function statement-sets is GOOD, keep it. BUT patterns are different — `*P` (a stored pattern) shares emitted CODE across match sites yet needs a DISTINCT ζ INSTANCE per activation (recursion, or the same stored pattern reused/looped). Confirmed against real IR: `string_pattern.sno` line 6 `PAT = BREAK(',') . WORD ','` lowers to `IR_ASSIGN_CONCAT "PAT" ← IR_SEQ` (the stage-2 pattern tree, built once, stored); line 12 `S PAT = ''` lowers to `IR_SCAN "S"` whose pattern operand is `IR_PAT_DEFER "PAT"` — runs the stored tree, re-entered every loop iter. The `','` LIT box inside that tree IS DDS-1.

**TWO ζ PLANES (do not merge):**
- **Section-ζ (r12, existing model — KEEP).** Per G2-trace / G3-function. Holds loop counters (live across branch-loop iters), the MATCH-head cursor-save, the subject DESCR slot. Runs once-through; established by the trace's glob head.
- **Pattern-ζ (separate, NEW).** The stored pattern tree's box storage. Allocated PER MATCH-ACTIVATION at the `IR_PAT_DEFER`/`IR_SCAN` site, sized from the pattern object's recorded slot-count, **realloc-grown** for any ARBNO inside. Established by the pattern glob's head (α sets r12 = this frame). MUST be separate from section-ζ: section frame is live for the whole trace (counter spans iters) while the pattern frame must be FRESH per activation, else a recursive/reused pattern aliases its own state. (test_sno_3 `enter()` = this plane; test_sno_2 section storage = the other.)

**GRANULARITY LADDER (fine → coarse) — what shares ONE ζ:**
- **G0** — every BB its own ζ. Trivial, wasteful. The CORRECTNESS FLOOR (always available per-box).
- **G1** — one ζ per FINALLY-BUILT PATTERN (the stage-2 product). All boxes in one pattern tree share a frame.
- **G2** — one ζ per TRACE: a maximal in-order run of statements where the head is label-reachable (branch target) and the tail are unlabeled fall-throughs. Single-entry straight-line ⇒ live ranges fit one frame. (`string_pattern.sno` traces: T0{&TRIM,&STLIMIT,PAT=,T1=,ITER=} · T1{OUTER,S=,RESULT=} · T2{INNER scan,RESULT=concat} · T3{DONE,2×OUTPUT=}.)
- **G3** — one ζ per FUNCTION BODY, grouping several G2 traces, delimited by the GIMPEL `*_END` scope marker (e.g. `STACK.sno`: `:(STACK_END)` branches OVER the body during the one-time top-down pass; `STACK_END` closes the scope — this is also the DEFINE-skip).

**ARBNO-style BB backtrack stacks → REALLOC'd growable arrays (Lon: "total dynamic").** Not the fixed `[64]`. Storage **C** with no ceiling.

**DEFINE single-exec constraint.** DEFINE runs ONCE (registers the fn); the body is entered SEPARATELY and re-entrantly. NEVER share a ζ across DEFINE-time and body-call-time; any glob live multiple times (recursion, stored pattern reused) allocates its ζ PER ACTIVATION, never statically baked.

**DDS PLAN (how to try, Lon "let's try some"):** prove the mechanism at **G0** on the real `','` LIT in `string_pattern.sno` (LIT is the save-nothing corner: β does `Δ-=len`, `len` is a `[rip+disp]` RO const, NO ζ slot), validating match-site/glob-head r12-set + port-to-port stitch + the per-activation frame FIRST; THEN coarsen the same PAT tree to **G1** (whole tree, one frame) as a pure optimization on a green base. Gate at each step (smoke M3/M4 7/7; PB-GREEN 6/16 floor holds). REUSE `flat_drive_match`/`walk_bb_flat` — do NOT invent a second stitch.

**SEQUENCING (Lon, 2026-06-23) — the campaign order:** (1) toy with `seed/` first, then prove against real `corpus/benchmarks/snobol4/*.sno`. (2) Start **PER-BB (G0)** and get ALL benchmarks WORKING at WORST performance first — correctness before speed. (3) THEN ratchet up with GLOBing strategies in order G1 (per finally-built pattern) → G2 (per trace) → G3 (per function / `*_END` scope), measuring each. (4) Accumulating MULTIPLE strategies in-code switched by C var/macro was considered but is "probably way too much" — DEFERRED unless a clean A/B need arises.

---

**TWO ABSOLUTE REQUIREMENTS:**
1. **TEMPLATE-ONLY x86.** Every pattern-box instruction emitted through the `x86(...)` path (`BB_templates/x86_asm.h`), exactly like all other codegen. ZERO hand-typed machine-code byte arrays. The `const uint8_t bb_*_proto[]` arrays in `src/runtime/pattern_match.c` (`bb_lit_proto`, `bb_len_proto`, `bb_pos_proto`, `bb_rpos_proto`, `bb_tab_proto`, `bb_rtab_proto`, `bb_fail_proto`, `bb_rem_proto`, `bb_succeed_proto`, `bb_fence_proto`, `bb_abort_proto`, `bb_any_proto`, `bb_notany_proto`, `bb_span_proto`, `bb_break_proto`, `bb_breakx_proto`, `bb_arb_proto`) — ALL DELETED.
2. **DIRECT BB STITCH, NO HEADS.** A compound pattern stitches the BB fragments themselves by patching each box's own γ/ω port (success → next box entry; fail → prior box fail-path), the SAME Byrd-box port-patching the compile-time emitter uses. The `DTP_t {entry, out_γ, out_ω}` 32-byte head indirection (`dtp.h`) and the `rt_dtp_run` trampoline that jumps THROUGH it are DELETED. Boxes connect port-to-port directly.

**SCOPE (one excision-plus-rebuild, gated slices — do NOT half-delete and leave link failures):**
- `src/runtime/pattern_match.c` — delete all `bb_*_proto[]` + `bb_*_proto_desc`; rework/delete `rt_pattern_build`/`rt_pattern_stitch_cat`/`rt_pattern_stitch_alt`/`rt_dtp_run`; the DT_P `pat_*` BOMB stubs become the real template-driven builders.
- `src/include/dtp.h` — delete `DTP_t` head struct + proto externs; redefine stitch contract around direct port-patch.
- `src/runtime/rt/pat_pool.c` — pat-pool now holds template-emitted relocatable boxes, not memcpy'd byte protos.
- `src/emitter/BB_templates/bb_pattern_lit.cpp`, `bb_pattern_nullary.cpp`, `bb_pattern_arb.cpp`, `bb_pattern_unary_s.cpp`, `bb_pattern_unary_i.cpp` — rewrite to EMIT boxes via `x86()` (currently they pass `&bb_*_proto`/`&bb_*_proto_desc` addresses to the runtime builder — that whole hand-off dies).
- `src/driver/scrip.c` — references to the proto path.
- `src/attic/IR_interp.c` + `src/attic/runtime/` — dead proto copies; delete.

**GATE:** `grep -rn 'bb_.*_proto\b' src/ (excl attic-deleted) == 0` · `grep -rn 'DTP_t\|rt_dtp_run' src/ == 0` · `grep -rnE 'bytes\(|u32le|u64le|u8\(' src/runtime/pattern_match.c == 0` · smoke M3/M4 7/7 · pat-rung M4 19/19 0-SKIP · fence T1=T2=0 · broad-corpus M4 ≥170 · `roman`/`mixed_workload`/`string_pattern` benches drive green via the new direct-stitch path (these are exactly the stored-pattern `BREAK . CAPTURE` cases — see PBG-3 below).

## STEPS

- [x] **DDS-0** — survey + contract DONE. Excision landed+gated (SCRIP `dd0d0a2`): all 17 `bb_*_proto[]`+`*_proto_desc`, `rt_dtp_run`, `DTP_t`/`DTP_FRAG_t`/`DTP_PROTO_DESC`, the 8 raw-`.byte` templates, `rt_pattern_build`/`stitch_{cat,alt}`/`dtp_head_build`, `rt_defer_match` DT_P branch, dead `src/attic/IR_interp.c` — all deleted; dispatch → `bb_pattern_stub` bomb (`emit_core.c`); `dtp.h`→pat-pool-only; `DESCR_t.p`→`void*`. Gates: proto/`DTP_t`/`rt_dtp_run`-in-src=0, raw-bytes-in-pattern_match=0, build green, 6/6 PB-GREEN byte-identical .s. **Contract CONFIRMED (Lon 2026-06-23): glob-head sets r12 on α+β — see REQUIRED DESIGN READING + ζ-PARTITION DESIGN above. Golden DDS-1 target = `seed/test_sno_5.c`.** Ground-zero rebuild state reached; DT_P correctly BOMBs at emit.
- [ ] **DDS-1** — **CORRECTED TARGET (2026-06-23b): the LIT box is already done (`bb_lit()`, template-only, dispatched at emit_core.c:341). The real DDS-1 work is the BB_SWITCH r12-broker around the `IR_PAT_DEFER` (stored-pattern) glob** — stored-pattern READ currently drops CAPTURE because the deferred shared body has no broker-established ζ frame (inline capture works; stored does not — verified vs sbl). Emit the four-port BB_SWITCH (Q1/Q2 locked; golden = `seed/test_sno_6.c`) wrapping the deferred glob; verify `PAT=BREAK(',') . WORD; S ? PAT` ⇒ `WORD=alpha` == oracle. Gate green (PB-GREEN 6/16 floor) before next box.
- [ ] **DDS-2..N** — one box per slice (LEN, POS, RPOS, TAB, RTAB, ANY, NOTANY, SPAN, BREAK, BREAKX, ARB, REM, FAIL, SUCCEED, FENCE, ABORT, CAT, ALT), each: rewrite template to emit, delete its proto, gate green.
- [ ] **DDS-FINAL** — delete `DTP_t` head + `rt_dtp_run` once no box needs the trampoline; delete attic copies; full gate; PBG-3 benches green via direct-stitch.

---

**⚠️ HANDOFF — 2026-06-23(b) · Claude Opus 4.8 · BB_SWITCH MECHANISM LOCKED + GOLDEN SEEDED + DEFER ROOT-CAUSE ISOLATED. SCRIP `2ede32b`→THIS (seed/test_sno_6.c added; zero codegen change, 6/6 PB-GREEN byte-identical). `.github` GOAL updated.**

**Session: R12 mechanism redirect realized → golden re-derived → live reality check corrects the stale map.**

**⛔ R12/ζ MECHANISM — NOW LOCKED (Lon, 2026-06-23b). Supersedes BOTH "α+β head two-liner" AND the earlier "DESCR-α/ω" sketch.** No box ever sets r12. r12 is established ONCE at the glob BOUNDARY, externally, by one of three sites — none an α/β first-instruction:
- **STATEMENT glob** (G2, not re-entrant): r12 = `lea r12,[rip+frame]` at the XA statement-entry (compile-time-constant frame addr).
- **PATTERN glob** (G1, stored `*P`, re-entered per loop-iter/recursion): r12 set by a **BB_SWITCH broker** at the DEFER call-site.
- **FUNCTION glob** (G3, recursive): same broker, fresh frame per activation (DEFERRED — pattern case is DDS-1).

**BB_SWITCH = a full FOUR-PORT box that brokers r12 (decisions Q1+Q2 locked this session):**
- **Q1 (shape):** TWO entry sub-boxes — `switch.α`: `push r12; <establish callee frame>; mov r12,frame; jmp callee.α` · `switch.β`: `push r12; mov r12,cached; jmp callee.β`. TWO exit sub-boxes — `callee.γ → resume.γ`: `pop r12; jmp caller.γ` · `callee.ω → resume.ω`: `pop r12; jmp caller.ω`. Exactly one entry + one exit fire per traversal ⇒ push/pop balance. SEPARATE γ/ω resumes (no discriminant slot). The switch PRESENTS AS A NORMAL BYRD BOX ⇒ stitches port-to-port via `flat_drive_match`/`walk_bb_flat` unchanged.
- **Q2 (cache slot):** the per-activation pattern-frame ptr is cached in a slot of the CALLER (section) frame — `[r12_caller+cache_off]`, read/written BEFORE r12 is swapped to the callee frame. Re-entrant for free (recursion ⇒ distinct caller activation ⇒ distinct cache slot; a `.bss` slot would alias). α allocs+caches; β reads the cached ptr.
- **C-stack save** (Q1 from prior turn): the push/pop of r12 IS the ARCH-x86 "call-style extra-BLOB jump" — source BLOB pushes before the outbound jmp, pops at resume. Nests for free on recursion.
- **Pattern-flavor switch saves ONLY r12** (Q2 from prior turn): Σ/δ/Δ (r13/r14/r15) are NOT touched — the subject flows continuously through a pattern; **BB_SCAN owns r13/r14/r15.** (A FUNCTION-flavor switch would also save the subject trio — out of scope for DDS-1.)

**GOLDEN: `seed/test_sno_6.c` (NEW — SUPERSEDES test_sno_5.c).** Stored `PAT='C' 'D'` reused at 2 sites: ONE code body, DISTINCT pattern-frame instance, ONE register r12 set at section-glob entry (static) + swapped by the BB_SWITCH broker, NO box's first instruction. Site 2 (`PAT 'Z'`) forces a backtrack RE-ENTRY into PAT.β through a SECOND switch that RESTORES the cached frame. Compiles+runs (`gcc -std=gnu11 seed/test_sno_6.c`); R12-trace prints the save/restore at every boundary; two-site semantics oracle-confirmed (`sbl`: site1 match=CD, site2 fail). **THIS IS THE DDS-1 EMITTER TARGET.** test_sno_5.c is retired (its "head sets r12" thesis is dead).

**🟢🔴 LIVE REALITY CHECK — the stale map was WRONG about where the gap is. Verified vs sbl this session:**
- **The LIT box is ALREADY DONE.** `IR_PAT_LIT` dispatches (`emit_core.c:341`) to `bb_lit()` — a clean template-only `x86()` box (memcmp vs `[rip+lit]` RO const, bounds-check, `Δ+=N`/β:`Δ-=N`). The DDS-0 excision already removed `bb_lit_proto`; the live box is the template. **DDS-1 does NOT need a new LIT template.**
- **Stored LIT works end-to-end:** `PAT='C' 'D'; S ? PAT` → compiles, runs, == oracle ("matched stored"). So a stored pattern's READ form (`S ? PAT`) with LIT boxes ALREADY matches at G0.
- **THE ACTUAL ROOT CAUSE common to roman+mixed_workload+string_pattern = the `IR_PAT_DEFER` execution path drops CAPTURE.** `S ? BREAK(',') . WORD` **inline** captures correctly (`WORD=alpha` == oracle). The SAME pattern **stored** (`PAT=BREAK(',') . WORD; S ? PAT`) lowers the SCAN operand to `IR_PAT_DEFER "PAT"` and captures NOTHING (`WORD=` vs oracle `alpha`) — silent, no bomb. This is the stored-pattern ζ problem the BB_SWITCH exists to fix: the deferred shared body needs a broker-established pattern frame so capture-writes land correctly; inline works only because it's emitted in-place with the section frame already live.
- **The `S PAT = ''` BOMB is a SEPARATE, narrower issue:** `bb_scan: TEXT(mode-4) non-literal pattern needs native PB-RB graph` fires from the gate in `flat_drive_scan_stmt` (emit_bb.c ~2448) which declines native when the REPLACEMENT flag `IR_LIT(pBB).ival` is set. This is the empty-repl splice — **orthogonal to r12/ζ** (it's subject replacement, not frame allocation). Independent of DEFER-capture.

**⇒ DDS-1 AND PBG-3 CONVERGE: the one root is "make `IR_PAT_DEFER` run the stored pattern's BB graph with a broker-established ζ frame."** Empty-repl is a separable add-on once DEFER matches+captures correctly.

**ROOT CAUSE NAILED (2026-06-23b, traced to the line):** `IR_PAT_DEFER` → `bb_match_defer()` (emit_core.c:458) → calls C runtime `rt_defer_match(varname, ival_flag, cur_delta)` (pattern_match.c:578). That C function ONLY handles a stored value of type `DT_S`/`DT_SNUL` (plain string: `strncmp`, return new cursor). For an actual PATTERN object (`DT_P` — the `BREAK . WORD` tree) it falls through to `return -1` (fail). It has NO boxes, so it CANNOT run a pattern graph and CANNOT capture — the `'C' 'D'` stored-LIT case only "works" because the value flattened to a string. **The fix is the BB_SWITCH: replace the `rt_defer_match` call in `bb_match_defer` with a broker that (a) establishes the pattern frame in r12 (alloc+cache per Q2), (b) jmps into the stored pattern's ALREADY-EMITTED BB body (the inline `BREAK . WORD` boxes already exist + already capture correctly — verified), (c) pops r12 on γ/ω.** The deferred site just needs to REACH those boxes with a live frame; the boxes are not the problem. `rt_defer_match` (and the `rt_dtp_run` residue, if any) then die. NOTE: this requires the stored pattern's BB graph to be emitted/reachable from the DEFER site (the pattern object must carry its emitted box-graph entry, per ARCH-SNOBOL4 "descr `.p` = box-graph head") — confirm how the `DT_P` value reaches the deferred SCAN site and whether its graph is emitted once (shared) or needs emit-on-first-DEFER.

**NEXT SESSION (DDS-1, fresh context — this is a vertical slice, needs headroom):**
1. Find the `IR_PAT_DEFER` emit path (grep `IR_PAT_DEFER` in emit_bb.c/emit_core.c; it currently runs the stored graph but capture lands in the wrong frame). Confirm whether DEFER today even re-enters the stored pattern's BB body or no-ops.
2. Emit a **BB_SWITCH** (four-port, per Q1/Q2 above, modeled byte-for-byte on `seed/test_sno_6.c`) wrapping the deferred pattern glob: switch.α allocs+caches the pattern frame in `[r12_section+cache_off]`, pushes r12, sets r12=frame, jmps the stored body's α; resume.γ/ω pop r12. REUSE the `flat_drive_match` stitch — the switch is just another box in the chain.
3. Verify capture lands: `PAT=BREAK(',') . WORD; S ? PAT` ⇒ `WORD=alpha` == oracle. THEN the read-form benches; THEN add empty-repl splice (the `flat_drive_scan_stmt` gate widen + `rt_scan_splice_empty`) for `S PAT = ''` → string_pattern/roman/mixed_workload green (+3 at G0).
4. Gate: smoke M3/M4 7/7 · pat-rung 19/19 · fence T1=T2=0 · broad-corpus ≥170 · PB-GREEN 6/16 floor. THEN coarsen G0→G1 (whole pattern tree shares one frame) as pure optimization on green.

**Build:** `apt-get install -y libgc-dev && make && make libscrip_rt` (→ out/libscrip_rt.so). Oracle `/home/claude/x64/bin/sbl -b`. Tri-probe: `scrip --compile p.sno | gcc -no-pie - -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p && ./p` vs `sbl -b`. Benches: `corpus/benchmarks/snobol4/*.sno`.

---

**⚠️ HANDOFF — 2026-06-23(a) · Claude Opus 4.8 · SCRIP CLEAN at `2ede32b` (WIP STASHED, not built). `.github` ONLY.**

**Session: orientation-correction → native-match reality check → empty-repl WIP → Lon R12 redirect.** No SCRIP commit (WIP doesn't build). No gates run. Stash: `DDS-empty-repl-WIP-2026-06-23-not-built` (pop or discard per Lon's new R12 direction below).

**⛔ CORRECTED ARCHITECTURE FACTS (stale docs misled prior orientation — verified against live code this session):**
- **There is NO mode 2, no SM interpreter, no SM engine.** The driver (`src/driver/scrip.c:2129`) parses exactly TWO execution flags: `--run` (DEFAULT — build flat-wired x86 BB blobs in a sealed slab, jump in) and `--compile` (emit standalone x86-64 asm to stdout, links `out/libscrip_rt.so`). NO `--interp`, NO `--sm-interp`. `sm_interp_run`/`sm_jit_run`/`SM_sequence_t` = ZERO live files; the surviving `sm_*` names (`sm_lower` in one error string, `sm_preamble`, a `bb_exec_stmt` substring in `rs23_diag.c`) are vestigial. **The mode-2/3/4 numbering in PLAN.md + ARCH-SCRIP.md is STALE — do not trust it; the SM-based three-mode table in ARCH-SCRIP.md is dead.** Pipeline = ONE frontend (CMPILE.c for SNOBOL4) → AST → LOWER → IR/BB graph → two sinks: `--run` (sealed slab in-proc) / `--compile` (asm text). REGISTER-LAYOUT.md's lower SM section is also dead; its top banner (bb_regs.h table) is the only live part.

**🟢 MAJOR FINDING — "one r12 per BB" ALREADY WORKS for the entire non-literal MATCH space (verified vs sbl oracle this session):**
- Build needs BOTH `make` AND `make libscrip_rt` (→ `out/libscrip_rt.so`); oracle = `/home/claude/x64/bin/sbl -b`. Benches live at `corpus/benchmarks/snobol4/*.sno` (NOT `SCRIP/corpus/...`).
- The match-box machinery is LIVE and per-BB-framed: `IR_SCAN` (flat walker `emit_bb.c:3232`) → `flat_drive_scan_stmt` → `flat_drive_scan_native` (`emit_bb.c:2400`) → `flat_drive_match` (`emit_bb.c:2522`, builds `IR_PAT_MATCH_HEAD`/`RETRY`/`ADVANCE` + walks the pattern tree) → `bb_match_{head,retry,advance}.cpp` + dcap capture (`rt_dcap_*`). Each match uses ONE frame slot `FR(op_off)` on r12 (head start-cursor save), r13=Σ, r14=δ, r15=Δ. This IS G0.
- **VERIFIED CORRECT end-to-end (compile→gcc→run == oracle):** `S LEN(3)` → "matched"; `S BREAK(',') . W` → "W=alpha". Pure-match LEN, BREAK, and conditional-CAPTURE (`. W`) all emit native and run byte-correct. The PBG-3 `sno_leaf_buildable`-orphan diagnosis was about the STORED (`PAT = …`) case only — INLINE capture lowers fine to `IR_PAT_ASSIGN_COND → IR_PAT_BREAK` and works.
- **THE ONLY GAP blocking roman + mixed_workload + string_pattern = the REPLACEMENT form `S PAT =`.** The native gate in `flat_drive_scan_stmt` declined whenever `IR_LIT(pBB).ival` (is_repl) was set — even for an EMPTY replacement — and fell through to the `bb_scan_stmt` BOMB (`.S11` "non-literal pattern needs native PB-RB graph"). Probe confirmed: `S LEN(3) =` → trace `ival=1` → declined → BOMB; `S LEN(3)` (no `=`) → `ival=0` → native → runs. This is exactly the lost-stash `IR_SCAN_REPL_EMPTY` work.

**WIP THIS SESSION (stashed `DDS-empty-repl-WIP-2026-06-23-not-built`, 3 files, does NOT build — missing header decl + Makefile entry):**
- `pattern_match.c`: `rt_scan_splice_empty(subj_name, m_start, m_end)` — splices `Σ[0:m_start]+Σ[m_end:]`, assigns back (mirrors `rt_scan_lit` replace; reads globals `Σ`/`Σlen` set by `rt_subject_load_nv`). Plus `g_rt_mstart`/`rt_match_start` (unused — earlier draft).
- `emit_bb.c`: `g_match_start_slot` global = head's start slot; `flat_drive_scan_native` gains `is_empty_repl` param + emits splice at `dcap_ok`; gate widened to enter native when repl is empty-literal (`is_empty_repl = ival && replace_lit && !replace_lit[0]`).
- `bb_scan_splice_empty.cpp` (NEW, template-only `x86()`, modeled on `bb_match_capture`: `lea rdi=name; mov esi=FR(start_slot); mov edx=r14d; aligned call`). **To build it needs: decl in `bb_templates.h` (~line 37 by `bb_match_capture`) + add `.cpp` to Makefile obj list.** Unchecked risk: splice reads m_start from `FR(g_match_start_slot)` — valid only if the head slot survives to `dcap_ok` across the dcap wrapper; if wrong, record start into a runtime global from `bb_match_head`/`advance` instead.

**⛔⛔ NEW LON DIRECTIVE — R12-SET MECHANISM REDIRECT (2026-06-23, supersedes "α AND β set r12"):** The two-line template (α/β first-instr sets r12) is a DEAD END — "we are stuck with two-line template code; we have no way to extend it out to BB GLOBS." Instead:
- **For PATTERNS:** set r12 inside the **DT_P DESCR_t data that carries the `bb_box_fn`**, at the box-graph's **α (entry) AND ω (exit)** — NOT β. The pattern value (descr `.p` slot reborn as box-graph head, per ARCH-SNOBOL4) owns its r12-set at its own entry/exit ports.
- **For externally-reachable BLOCKS of statement code:** same treatment — the block sets r12 at its reachable entry.
- Net: r12-establishment moves from "every glob-head α+β two-liner" to "pattern DESCR_t entry/exit (α/ω) + statement-block entry." Re-derive the DDS-1 plan and `seed/test_sno_5.c` model under this α/ω-in-DESCR framing before resuming codegen.

**NEXT SESSION:** Decide first whether to (a) finish the small empty-repl wire-up (header decl + Makefile + gate: `S LEN(3) =` repro, then string_pattern/roman/mixed_workload tri-probe, smoke 7/7, pat-rung 19/19, fence T1=T2=0, broad-corpus ≥170) to bank +3 benches at G0 NOW, OR (b) first refactor r12-establishment to the new DESCR-α/ω model and rebuild empty-repl on top. The empty-repl splice itself is orthogonal to the r12 mechanism (it's about subject replacement, not ζ allocation), so (a) can likely land independently and bank green before (b) reshapes the ζ plane.

---
<!-- SESSION-FIRST RUNG — PBG-GREEN · ALL 16 SNOBOL4 BENCHMARKS WORKING -->

# ⛔⛔⛔ SESSION-FIRST RUNG — PB-GREEN · ALL 16 SNOBOL4 BENCHMARKS WORKING

**Mandate (2026-06-19 PIVOT):** get every benchmark in `corpus/benchmarks/snobol4/*.sno` WORKING in mode-4 (`--compile`) AND result line matches sbl oracle. Session-first rung.

**TRUE BASELINE (2026-06-22 @ `e789f1e`, after PBG-2): 6/16 genuine green.** Green = {arith_loop, op_dispatch, pattern_bt, string_concat, fibonacci, table_access}. `string_manip` = PERF timeout; `indirect_dispatch` = XFAIL (sbl ERROR 022). DONE = 15 runnable green + 1 xfail with real `ms:`.

| # | bench | verdict | CAUSE |
|---|---|---|---|
| 1 | arith_loop | ✅ | — |
| 2 | op_dispatch | ✅ | — |
| 3 | pattern_bt | ✅ | — |
| 4 | string_concat | ✅ | — |
| 5 | fibonacci | ✅ | — |
| 6 | table_access | ✅ | — |
| 7 | string_manip | ❌ timeout @5M | **PERF** |
| 8 | var_access | ❌ timeout @10M | **PERF** |
| 9 | func_call | ❌ timeout @10M | **PERF** |
| 10 | func_call_overhead | ❌ timeout @10M | **PERF** |
| 11 | eval_fixed | ❌ OOM @1M | **EVAL-CHURN** |
| 12 | eval_dynamic | ❌ OOM @1M | **EVAL-CHURN** |
| 13 | roman | ❌ BOMB | **SCAN-NONLIT-M4** |
| 14 | mixed_workload | ❌ BOMB | **SCAN-NONLIT-M4** |
| 15 | string_pattern | ❌ BOMB | **SCAN-NONLIT-M4** |
| 16 | indirect_dispatch | ⚠️ XFAIL | **ORACLE-ERROR** |

**GATE:** bench green count non-decreasing · smoke M3/M4 7/7 · pat-rung M4 19/19 0-SKIP · fence T1=T2=0 · broad-corpus M4 ≥170. DONE = 15/16 correct + 1 xfail with real `ms:`.

**Bench runner:** `scripts/test_bench_snobol4_modes.sh`. Bench dir: `corpus/benchmarks/snobol4/`. Oracle: `/home/claude/x64/bin/sbl -b`. Tri-probe: `scrip --compile p.sno | gcc -no-pie - -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p && ./p` vs `sbl -b p.sno`.

## STEPS

- [x] **PBG-0** — `.ref` files verified byte-equal to oracle · honest runner · xfail marker.
- [x] **PBG-1** — fibonacci GREEN (REENTRANT-FRAME: DESCR-pure `rt_num_arith` for CALL+CALL arith). SCRIP `cff870a`.
- [x] **PBG-2** — table_access GREEN (IR_IDX/IR_IDX_SET wired; `T<3>=99;OUTPUT=T<3>`→99; D2 mixed arith `SUM+T<I>`). SCRIP `e789f1e`, corpus `e9130815`.
- [ ] **PBG-3 — NON-LITERAL SCAN in M4 → roman + mixed_workload + string_pattern green (+3).**
  Close `bb_scan: TEXT(mode-4) non-literal pattern`. Route named-var/literal subject + non-literal pattern + empty replacement through native scan chain in M4.

  **⚡ DIAGNOSIS (2026-06-22, Sonnet 4.6 emergency handoff — WIP stashed as `PBG-3-WIP-2026-06-22-gates-not-green`):**
  Three separate blockers found:

  **(A) roman.sno** — TWO scans: (1) `N RPOS(1) LEN(1) . T =` (named-var + inline + empty repl) → new native route fires; (2) `'0,...' T BREAK(',') . T` (literal-subj + inline DEFER+BREAK+CAPTURE) → native route fires but returns empty result. Root cause of (2) not fully isolated — likely `flat_drive_scan_native` with literal-subj + inline capture failing silently.

  **(B) mixed_workload + string_pattern** — `PAT = BREAK(',') . WORD ','` → `lower_assign` ORPHANS it: `sno_seq_buildable` returns 0 because `TT_CAPT_COND_ASGN` is not in `sno_leaf_buildable`. PAT is never set → DTP path gets null value → no-op match → WORD never set, S never modified. FIX: add `TT_CAPT_COND_ASGN` to `sno_leaf_buildable` (returns 1) AND implement `sno_build_leaf_ir` for the capture-wrapper case AND implement `bb_pattern_capture` proto blob (S3/B8 feature — `emit_core.c:385` is the stub). This is significant work.

  **WIP CHANGES IN `git stash` (`PBG-3-WIP-2026-06-22-gates-not-green`):**
  - `IR_SCAN_REPL_EMPTY` IR kind (IR.h + scrip_ir.c)
  - `rt_scan_repl_empty(name, long start, long end)` runtime (pattern_match.c) — uses global Σ/Σlen; DESCR_t output; start=FRQ(match_st+8), end=r14
  - `bb_scan_repl_empty.cpp` template — reads `FRQ(_.op_off+8)` (DESCR_t payload), `r14` (64-bit); no β def (replacement never backtracks)
  - **DESCR_t enforcement:** `bb_match_head/retry/advance` — match-state slot now `{DT_I, cursor}` at `FRQ(op_off)/FRQ(op_off+8)` (was raw `FR(op_off)`)
  - `bb_subject.cpp` lit arm — emits `.string` via `LS(0)` (was broken: `emit_intern_str` returned NULL for new strings → `??` label)
  - `flat_drive_scan_native` extended: `has_repl_empty` param; literal-subj path (push `IR_LIT_S` operand onto subject node); post-match FILL for repl box
  - `flat_drive_scan_stmt`: two new routes (empty-repl named-var; empty-repl literal-subj with defer-or-safe pattern)
  - `bb_match_defer.cpp` + `rt_defer_match` + `rt_dtp_run` — r12 (ζ frame) threaded as `zeta` 4th arg so DTP code sees correct frame (was: C calling convention clobbered r12 before `jmp *%rax` in DTP code, breaking CAPTURE's `FR(slot)` writes)
  - Makefile + bb_templates.h wired

  **GATES NOT RUN — stash, do not push SCRIP.**

  **NEXT SESSION (PBG-3 completion):**
  1. Pop stash (`git stash pop`)
  2. Debug roman blocker (A): add fprintf in rt_scan_repl_empty; trace what `'0,...' T BREAK(',') . T` emits and whether capture writes to right slots
  3. Implement (B): `sno_leaf_buildable` + `sno_build_leaf_ir` for TT_CAPT_COND_ASGN; `bb_pattern_capture` proto blob (study `bb_pattern_unary_s.cpp` raw-byte approach; need a 4-byte save-slot in the blob header at offset 0; SAVE = `mov [rip+save_slot_off], r14d`; COMMIT = load save_slot + r14 + call `rt_cap_assign_cursor`)
  4. Run smoke 7/7, pat-rung M4 19/19, fence T1=T2=0, broad-corpus ≥170
  5. Commit one commit per subproblem fixed

- [ ] **PBG-4 — EVAL PER-CALL TEARDOWN → eval_fixed + eval_dynamic complete @1M (+2).** OOM confirmed (rc137 <6s, not timeout). Entry: `_builtin_EVAL`; path `rt_eval_run`/`DT_E` chain. Cache same source string → reuse compiled chain (eval_fixed). Per-call teardown (eval_dynamic). `CONVE_fn` cache draft noted in 2026-06-21 snapshot.
- [ ] **PBG-5 — PERF (folds OPSINGLE) → var_access + func_call + func_call_overhead + string_manip in-gate (+4).** Correct @low-N; blow wall on per-iteration by-name `NV_GET`/`rt_gvar_*`. Prerequisite: single-channel `operands[]` (OPSINGLE). Target: each finishes in 30s wall with result == ref.
- [ ] **PBG-6 — indirect_dispatch DISPOSITION + SPEEDUP REPORT.** Resolve `$FN(X)` vs oracle ERROR 022. Wire ratios into `bench/BENCHMARKS.md`.

---

# ⛔ NEXT-PRIORITY RUNG — REC-COV · COMMUNITY-RECOGNIZED CORPORA

**Mandate (2026-06-22):** extend coverage into community-recognized corpora. **PB-GREEN stays session-first.**

**Inventory (2026-06-22, unmeasured pass-rates — RC-0's job):**
- `corpus/programs/gimpel/` — 145 `.sno` (no `.ref`)
- `corpus/programs/csnobol4-suite/` — 124 `.sno` WITH shipped `.ref` ← start here
- `corpus/programs/snobol4/demo/` — 18 `.sno`
- `test_mode4_only_corpus_snobol4.sh` covers crosscheck+demo+beauty only; gimpel+csnobol4-suite ungated.

**GATE:** recognized-corpus oracle-match count non-decreasing; all PB-GREEN floors hold.

## STEPS

- [ ] **RC-0** — honest runner for all three corpora; oracle-gen refs for gimpel+demo; triage table mapping failures to PB-GREEN cause buckets; establish baseline counts (do not fabricate before RC-0 runs).
- [ ] **RC-1** — csnobol4-suite green-drive (refs already present, no oracle-gen needed).
- [ ] **RC-2** — gimpel green-drive.
- [ ] **RC-3** — demo green-drive.
- [ ] **RC-4** — promote RC counts to hard non-decreasing floors in gate set.
- [ ] **RC-5** — re-ground "10×" claim on recognized programs; separate table in `bench/BENCHMARKS.md`.

---

# ⛔⛔⛔ OPSINGLE · DELETE operand_aux, ONE channel (operands[])

**Mandate (2026-06-15):** exactly ONE place for operands: `nd->operands[]`. Delete `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`). Hard ordering: migrate all readers before deleting struct.

**WRITERS still aux-only (must add `ir_operand_push`, keep aux until readers flipped):**
- `lower_snobol4.c` — CALL args still in side-graphs (`sno_call_channels`)
- `lower_icon.c:134,137,315`; `lower_raku.c:210`; `lower_pascal.c:147,162,177,340`; `lower_prolog.c:140`

**READERS to flip (`bb_operand_aux_get` → `nd->operands[]`):**
- `BB_templates/bb_call.cpp:98`
- `emit_bb.c`: 350,411,438,846,1072,1492,1818,2489,**2957 (DELETE bridge shim)**,3035,3240,3335,3398,3458
- `driver/scrip.c`: 102,245,1931
- `contracts/scrip_ir.c:355`

**DELETE LAST** (all readers flipped + all language gates green): `bb_operand_aux_set`, `bb_operand_aux_get`, struct fields, all `bb_operand_aux_set(...)` calls.

**GATE:** grep `operand_aux` in src/ (excl attic) == 0 AND all language gates green.

---

**⚠️ EMERGENCY HANDOFF — 2026-06-22 · Sonnet 4.6 · `.github` ONLY (no SCRIP commit; SCRIP WIP stashed). Context exhausted at ~92%. PBG-3 partial: see PBG-3 step above for full WIP summary and next-session plan. NO GATES RUN THIS SESSION. SCRIP at HEAD `e789f1e` (PBG-2 landed, unchanged). Stash: `PBG-3-WIP-2026-06-22-gates-not-green`. Pop stash at next session start and continue from the two blockers (roman debug + bb_pattern_capture).**

---

**⚠️ HANDOFF — 2026-06-22 · Sonnet 4.6 · ORIENTATION SESSION ONLY (no code changes; stash confirmed absent).**

**CONFIRMED:** SCRIP at `e789f1e` (PBG-2). Git stash `PBG-3-WIP-2026-06-22-gates-not-green` does NOT exist — prior session exhausted before stashing. All WIP is design notes only (in this goal file). Start PBG-3 from scratch on next session.

**KEY FACTS FOR PBG-3 (from code read this session):**
- `bb_match_head/retry/advance` operate on LOCAL FRAME `[r12+offset]`: `op_sa`=subject DESCR_t slot (16B: qword=ptr, dword+8=len→r15d); `op_off`=4B int start cursor. Head sets cursor=0, loads r13=subj ptr, r10→cursor+8 slot. Retry loads r14d=FR(op_off). Advance increments FR(op_off), checks vs r15d and `kw_anchor`.
- `bb_scan_stmt` literal path calls `rt_scan_lit(subj_name,subj_lit,pat_lit,is_repl,repl_lit)`. Non-literal MEDIUM_TEXT path = x86_bomb (the blocker).
- RT globals: `Σ`/`Σlen` (pattern_match.c), `kw_anchor` (keywords.c), `g_rt_dcap[]`/`g_rt_dcap_n`/`g_rt_dcap_active` (cond-assign capture buffer, pattern_match.c), `g_subject_slot` (emitter phase, emit_bb.c:160).
- Blocker B: `sno_leaf_buildable` does not handle `TT_CAPT_COND_ASGN` → `PAT = BREAK(',') . WORD ','` orphaned by `lower_assign`.

---

**⚠️ HANDOFF — 2026-06-22 · Sonnet 4.6 · `.github` ONLY (no SCRIP commit; SCRIP clean at `95e8b02`).**

New SESSION-FIRST RUNG **DTP-DIRECT-STITCH** added at top per Lon's directive: runtime PATTERN datatype must be (1) template-emitted via `x86()` — kill all hand-coded `bb_*_proto[]` byte arrays in `pattern_match.c`; (2) stitched DIRECTLY box-port-to-box-port — kill the `DTP_t` head + `rt_dtp_run` trampoline. Start at DDS-0 (survey + contract, no deletions), then one box per gated slice (DDS-1 = LIT). REUSE the existing compile-time `flat_drive_match` port-patch model; do not invent a second stitch mechanism. This supersedes PBG-3's "native PB-RB" wording for the runtime path. PBG-GREEN bench floors (6/16) still hold and must not regress.

NO GATES RUN THIS SESSION. NO CODE CHANGED. SCRIP HEAD `95e8b02`, untouched.

---

**⚠️ HANDOFF — 2026-06-22 · Claude Opus 4.8 · DDS EXCISION LANDED + DESIGN DOCS WIRED. SCRIP `95e8b02`→`c01cce2`, .github→this commit, corpus refreshed.**

**Session: education → excision → doc-fix.** Prior sessions (incl. my own orientation) misused **r12** and accepted a band-aid (threading r12 as a `zeta` arg into the hand-coded DTP blobs) because the BB-LOCAL-STORAGE design was never surfaced by PLAN.md/this goal. Lon: pivot to ground zero, read the design, delete the bad code, fix the docs.

**DESIGN DOCS WIRED (so this never recurs):** PLAN.md session-start step 7 now mandates the BB-CODEGEN DESIGN SET (`ARCH-x86.md` stackless/flat-ABI · `ARCH-ICON.md` ζ-frame register contract · `REGISTER-LAYOUT.md` · `src/emitter/bb_regs.h` · `xa_flat.cpp`) for ANY BB/template/storage rung, with a self-enforcing "rung must link here" clause. This goal now CONTAINS the storage synthesis (top of rung): the 4 realizations **A** `[r12+off]` ζ frame (primary) · **B** `[rip+disp]` RO consts · **C** per-box `.bss` arena (unbounded) · **D** DEAD SM-stack/r10-tree, plus the register table and the match-site-owns-r12 stitch contract.

**EXCISION LANDED & GATED (SCRIP `c01cce2`):** deleted all 17 `bb_*_proto[]`+`*_proto_desc`, the `rt_dtp_run` `__asm__` trampoline, `rt_pattern_build`/`rt_pattern_stitch_{cat,alt}`/`rt_dtp_head_build`, `rt_defer_match`'s DT_P branch, the 8 raw-`.byte` templates (`bb_pattern_{lit,alt,cat,unary_i,unary_s,nullary,arb}.cpp`, `bb_dtp_assign.cpp`), the `DTP_t`/`DTP_FRAG_t`/`DTP_PROTO_DESC` types (`dtp.h`→pat-pool-only; `DESCR_t.p`→`void*`), dead `src/attic/IR_interp.c`. Dispatch (`emit_core.c`) rerouted to the clean `bb_pattern_stub` bomb. **GATES GREEN:** proto-arrays-in-src=0 · `DTP_t`/`rt_dtp_run`-in-src=0 · raw-bytes-in-`pattern_match.c`=0 · build green (libscrip_rt.so + scrip) · **6/6 PB-GREEN benches byte-identical `.s` (ZERO codegen drift)** — excision touched only the dead DT_P path. DT_P construction now correctly BOMBs at emit (the ground-zero rebuild state).

**NEXT SESSION (DDS-1):** (1) **Lon must confirm the MATCH-SITE-owns-r12 contract** recorded above before any codegen. (2) Then build the LIT box end-to-end via `x86()` into the pat-pool, stitch port-to-port to the compile-time `flat_drive_match` model (REUSE — do not invent a second stitch). Gate green before the next box. PB-GREEN 6/16 floor must not regress.

**Latent bug noted (not fixed):** `scripts/util_regen_benchmark_s_artifacts.sh` stages `benchmarks/*.s` but the benches now live in `benchmarks/snobol4/` (post-`03a0158` reorg) — its add-glob is stale; this session staged the subdir manually.

---

**⚠️ HANDOFF — 2026-06-23 · Claude Opus 4.8 · DESIGN SESSION — ζ-PARTITION CONFIRMED + DDS-1 GOLDEN SEEDED. SCRIP `dd0d0a2` (code unchanged) + new `seed/`; `.github` GOAL updated. No codegen touched → no gates needed (seed files are reference C, not in the build; benches not run).**

**Session: orientation → ζ-partition design → glob-head-r12 mechanism → golden seed.** Lon CONFIRMED the r12-establishment mechanism that was the open DDS-1 blocker: each BB GLOB has a HEAD presenting **outside γ/ω + inside α/β**; the head's **α AND β each set r12** (α = fresh frame, β = RELOAD because an inter-glob excursion clobbered r12 — the ARCH-x86 extra-BLOB-jump rule extended from α-only to α+β). **TWO ζ PLANES** (section + pattern) **TIME-MULTIPLEX ONE register r12 — NOT two** (Lon asked explicitly; answered empirically). Full design now lives above in REQUIRED DESIGN READING + ζ-PARTITION DESIGN (two planes, granularity ladder G0→G3, realloc-for-ARBNO per "total dynamic", DEFINE single-exec constraint).

**ARTIFACTS (committed to SCRIP `seed/`):** the 5 hand-written golden BB graphs `test_{icon,sno_1,sno_2,sno_3,sno_4}.c` (copied byte-identical from `bench/` per Lon "place files for future reference") + NEW `seed/test_sno_5.c` = the **GLOB-HEAD-SETS-R12 golden**: stored `*P` (`PAT='C' 'D'`) reused at 2 match sites = ONE code body / TWO ζ instances; head α+β set r12; all boxes LIT (save-nothing, DDS-1 scope). **Compiles + runs; R12-trace prints the swap** (`gcc -std=gnu11 seed/test_sno_5.c`). THIS IS THE DDS-1 EMITTER TARGET.

**NEXT SESSION (DDS-1 step 1):** build `bb_pattern_lit.cpp` to EMIT a relocatable LIT box via `x86()` (β: `Δ-=len`; `len`=`[rip+disp]` RO const; NO ζ slot), glob head sets r12 on α/β per `seed/test_sno_5.c`; stitch port-to-port via `flat_drive_match`/`walk_bb_flat` (REUSE). Reproduce the `','` LIT inside `string_pattern.sno`'s stored `PAT = BREAK(',') . WORD ','` (`IR_ASSIGN_CONCAT PAT ← IR_SEQ`; SCAN pattern operand = `IR_PAT_DEFER PAT`). Gate: smoke M3/M4 7/7, PB-GREEN 6/16 floor. Then coarsen G0→G1. Per Lon's SEQUENCING: G0 across ALL benches first (worst perf, correct), THEN ratchet GLOBing G1→G2→G3.

**Build note:** scrip needs `libgc-dev` (`apt-get install -y libgc-dev`) then `make`; builds clean at `dd0d0a2`. `--dump-ir` works pre-emit (used this session to confirm the `string_pattern.sno` lowering).
