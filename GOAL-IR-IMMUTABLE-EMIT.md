# GOAL-IR-IMMUTABLE-EMIT.md — The emitter READS IR. It NEVER mutates it. (Ground Zero #5)

## ⛔⛔ PIVOT — ZETA-BLOCKS (Lon, 2026-07-05) — READ FIRST; gates the SN4-PAT ARBNO rung below
**[2026-07-05 later same day — OFFICIAL ζ DESIGN DOC: `.github/ARCH-ZETA-LOCAL-STORAGE.md` is now the
document of record for ζ storage (this section remains the pivot record + rung gates; on storage design
the ARCH doc WINS). NAMING RETRACTED same day (Lon): do NOT say "ZLA" or "array" — the terms are **ZLS**
(Zeta Local Storage: internal, completely TYPED data, ≠ GST/GVA) and **COLLECTION** (owner-owned
per-iteration storage, reached by pointer FROM the ZLS region). ZC_* compile-time choice axes authored
at `SCRIP/src/contracts/zeta_choices.h` (additive, included by nothing yet). ZB-2 sessions read the
ARCH doc FIRST.]**
**Directive (Lon verbatim-in-spirit):** BB locals must be allocated in BLOCKS — sets of locals per feature
activation (*PATTERN deferred bodies, FUNCTION BODIES, re-entrant matchers). Granularity is tricky; the answer
is recovered from the old one4all SM+BB hybrid (SM ran statements, BBs ran patterns), which had this working
100% at the beauty self-host milestone.

**FINDING — the current model (verified in code this session):** ALL BB local storage = ONE flat
per-graph-activation frame; r12 is a FIXED base set once (`xa_flat.cpp:84` `push r12; mov r12, rdi`);
`ir_drive_slot_assign` (`scrip_ir.c:206`) is a single bump cursor granting each node one static `base+k*16`
offset for the life of the program; ZERO per-α-entry fresh-DATA machinery exists anywhere (grep = 0). Sole
fresh-frame granularity = whole-proc calls (`g_proc_arena`, rt.c:352, PROC_FRAME_DEPTH×PROC_FRAME_QWORDS;
`bb_callee_frame.cpp` repoints r12). This contradicts ARCH-x86 ("fresh DATA block on every α-port entry"),
ARCH-ICON ("zeta struct allocated fresh per α-entry"; "ARBNO... per-box arena indexed by depth"), and
`.github/test_sno_1.c` (`ζ = &_1[ARBNO_i]` — ζ is a MOVING activation pointer). Known casualties of the flat
model: the ARBNO wall, the queens solution-4 frame clobber (cumulative backtracking), the SCAN-SCRATCH
next-node-slot overrun family.

**RECOVERED — one4all (predecessor repo, PRIVATE — ask Lon for a credential to clone):**
- SCRIP root `713c581b` (2026-05-31) = "fresh start from one4all working tree"; one4all's 4,155-commit history
  was NOT carried over, and one4all is absent from the org roster.
- **THE MILESTONE: one4all `4757bbcd` (2026-04-28) "SN-32b/SN-32d: SM_STORE_VAR two bugs fixed — --sm-run
  beauty self-host byte-identical"** (+ same-day sibling `52251653` SN-32c JIT mirror). Lon recalls Session
  **#47**; PLAN.md says #57 — unadjudicated; the pin is by date+message, unaffected.
- Era corpus: `ae9ea8d8` (2026-04-27); source at `programs/snobol4/demo/beauty.sno`; NOTE `demo/inc/` does NOT
  exist at that commit — resolve the SNO_LIB dir next session (candidates: `programs/include/`, or a corpus
  commit a few days later).
- The milestone compiler BUILDS CLEAN at `4757bbcd` (`apt-get install -y libgc-dev; rm -f scrip; make -j4
  scrip` → rc=0). Era run modes: `--ir-run` / `--sm-run` / `--jit-run` (see that tree's
  `scripts/test_gate_sn7_beauty_self_host.sh`). Self-host command: `.github/archive/MILESTONE-SN4X86-SELFHOST.md`.
  **NOT RUN this session (Lon paused it)** — success pin = output md5 `abfd19a7a834484a96e824851caee159`.

**THE .S PAYLOAD (the layout to bring forward):**
- `one4all@4757bbcd:artifacts/asm/beauty_prog.s` — **70,840 lines**, NASM three-column. Register census:
  **rbp 10,036 · r12 3,937 · r14 205 · r10/r11/r13/r15 ≈ 40–50**. Subject model lives in `.bss`
  (`cursor`/`subject_data`/`subject_len_val`) — pre-R12/R13/R14/R15 register residency. **The chunk STRUCTURE
  is the asset; the registers were later optimization** (Lon). beauty_prog.s never existed in SCRIP history.
- Already in CURRENT SCRIP HEAD: `artifacts/asm/fixtures/{arbno_alt,arbno_match,arbno_empty,alt_fail,
  alt_first,alt_second,anbn,any_vowel,...}.s` (arbno_alt.s = 156 lines — ideal compact study) and
  `archive/backend/bb_boxes.s` (the 25-box 106/106 library).

**NEXT SESSION, in order:** (1) clone one4all with Lon's credential; worktree `4757bbcd`; corpus worktree
`ae9ea8d8`. (2) EXTRACT the chunk-allocation table from beauty_prog.s + the fixtures: how blocks were carved
per statement / per pattern / per DEFINE'd function body / per ARBNO activation; rbp-frame vs r12-block roles;
how deferred (*PATTERN) bodies got blocks. (3) Diff against today's flat `ir_drive_slot_assign`. (4) Produce
the bring-forward design: block-granular ζ on the live spine (unblocks ARBNO + DEFER + honest function
frames). (5) Optionally run the paused self-host + md5 gate to certify the rebuilt milestone.

### ZB-EXTRACT — LANDED 2026-07-05 (chat session, Fable) — the recovered chunk model + bring-forward ladder

**Corrections to the pivot block above:** (a) **one4all cloned PUBLICLY this session** (`git clone
https://github.com/snobol4ever/one4all.git`, no credential, 2026-07-05) — Lon: verify the repo's visibility is
intended before relying on "private". (b) The era macro file is `archive/backend/snobol4_asm.mac` (2,177 lines),
NOT under `artifacts/asm/`. (c) `artifacts/asm/beauty_prog.s` is byte-identical at `52251653` and `4757bbcd`
(git diff empty), was last REGENERATED 2026-03-29 (`bab5b6f4`) — the 4/28 milestone ran against a late-March
artifact — and left the tree 2026-05-21 (`1544362a`). Session copies: `/home/claude/beauty_prog_0428.s`,
`/home/claude/snobol4_asm_0428.mac`.

**F1 — two-tier storage.** rbp (10,036 uses) = SM statement frame for expression temporaries; r12 (3,937) = the
MOVING ζ block base for BB/pattern/function activation state; plus 2,389 static `.bss` qwords for
single-activation per-site state (68× `scan_start_N`, 19× `dol_entry_N`, 26× `spn_expr_N`, 16× `brk_expr_N`,
`fn_*` arg/save t·p pairs, `P_*_ret_γ/ω` continuation cells).

**F2 — activation = template-clone.** Each block family: a `.data` init image `box_<X>_data_template` (`dq 0`
rows whose comment column carries the field map — 1,094 annotated slots = the chunk-allocation table, in the
artifact itself) + `box_<X>_data_size`. Function-call α: `rdi=[box_X_data_size]; call blk_alloc;
memcpy(new,template,size); r12=new` (see `fn_upr` site). Deferred `*PATTERN` bodies took the CHEAP tier:
`lea r12,[rel box_ExprN_data_template]` (34 sites) — ran IN the static template, no clone: a single-activation
bet, the same bet the flat model later lost.

**F3 — nesting discipline.** 332× `push r12 … mov r12, rax` (machine-stack save of caller ζ), or named cells
(`nref516_r12`) for deferred refs; returns via STORED CONTINUATIONS `P_X_ret_γ/ω` (code addresses), return
thunks restore r12 then `jmp`.

**F4 — intra-block ABI.** Hot descriptor at `[r12+16]/[r12+24]` (t·p; 140 loads / 66 stores); per-box fields
upward (ARBNO's at `+280/+288`).

**F5 — ARBNO mechanics** (`snobol4_asm.mac:2040-2077`): depth counter IN the current ζ (`r12+280`);
per-iteration state = ONE qword cursor snapshot on a per-instance STATIC stack `arbN_stack resq 64`; α1 rejects
the empty match (`cur_before==cursor → ω`) then pushes and `dep++`; β pops and restores. **Depth hard-capped at
64 by the static array.** The cap + the static ret_γ/ω and nref cells are exactly today's casualty list
(ARBNO wall, queens solution-4 clobber, SCAN-SCRATCH overruns).

**BRING-FORWARD DECISIONS (Lon, chat session 2026-07-05):**
- Per-activation ζ blocks from a BUMP ζ-STACK in the RX slab: alloc = add, release = restore; a `.prev` link
  field replaces the push-r12 machine-stack discipline (stackless preserved). Heap promotion (`blk_alloc`)
  DEFERRED to suspendable scopes (Icon suspend dependency).
- NO `.bss` in emitted programs. mode-4 prints NASM `struc/endstruc` OVERLAY headers — zero storage, pure
  layout documentation; BOTH modes address `[rZ+disp]` only (displacement-identical bytes, MODE34-IDENTICAL),
  retiring the `emit_bb_zeta_rdi(ptr,sym)` fork. rZ default = r12 (continuity; final call per `x86_asm.h`
  roster).
- Pattern GLOBs: immutable compiled shape `[rip+disp]` per RULES (READ-ONLY LOCALS ARE IP-RELATIVE); ALL
  mutable match cells — including ret_γ/ω continuations and ARBNO iteration stacks — live in the INVOKER's
  activation layout.
- Layouts computed PRE-EMIT into a PARALLEL table keyed by node id (PEERS RULE: zero new BB_t/IR_t fields);
  replaces `ir_drive_slot_assign`'s single program-lifetime cursor (`scrip_ir.c:206`) with a scope-tree
  builder: program → DEFINE body → label-group (labeled stmt + trailing unlabeled stmts) → re-entrant box.
  Groups laid DISJOINT; lifetime-unioning deferred until real liveness info exists.

**Ladder:**
- [x] **ZB-1 EXTRACT** — this entry.
- [~] **ZB-2 SCOPE-LAYOUT PASS — LANDED v1 2026-07-05 (second session same day, Fable; see watermark below).** `src/contracts/zeta_storage.{h,c}` = the ONE grant table (moved out of `ir_drive_slot_assign`, which is now a thin mirror: `nd->tmp`/vslots/resume/region all COPY from zls); typed per-FIELD maps `{off,size,kind∈DESCR/RAW/PTR_GC/PTR_CODE, audit}` with what-strings (the 4/28 1,094-row annotated chunk table reborn as `--dump-zeta` output); scope tree = FN root per graph + **ZL-GROUP via LOWER-recorded `zls_group_mark(g,label)`** (lower_snobol4 statement loop — NOT registry landings: landings are pre-created GOTO anchors clustered at low indices, index-grouping misattributes; LOWER knows the boundary, LOWER marks it — the doctrinally correct owner); `--dump-zeta` driver flag (runs the optimizer first, unlike `--dump-ir`, so it shows the layout that COMPILES); emitter re-based: `drive_value_slot` consults `zls_off(nd)` with a HARD parity abort where zls is authoritative (legacy `ir_tmp_slot_assign`/jcon graphs pass through untouched). `zeta_choices.h` now has its first includer (zeta_storage.c prints the compiled axes in the dump header). REMAINDER for ZB-2 completion: (a) Icon-side group marks (procs are separate graphs so FN-level is honest v1; statement-level groups when Icon wants them); (b) full `nd->tmp` retirement (the mirror stays until every reader migrates to zls reads — IR-REDESIGN's tmp-drop rides this); ~~(c) burn down the `(audit)` provisional kinds (GC-1's first task)~~ **(c) DONE 2026-07-05 fourth session — audit=0 repo-wide, every grant template-verified; the one real kind fix = REV_ASSIGN save RAW→DESCR (live t·p across suspension), plus the SCAN_ENTER value/save mislabel corrected (it is the leave's 24B reg out-area) and CREATE cells per-field named as dead-at-return marshal; 2 missing GC roots found and recorded in ARCH §6b (static `scan_stack[]` σ saves; malloc'd coexpr ctx/pkg holding captured snapshots — latent liveness bug noted). New-grant rule: audit=1 until template-read. Full verdict table in ARCH §4.**
- [x] **ZB-3 ACTIVATION ζ — RUNTIME SIDE LANDED 2026-07-05 (third session same day, Fable; watermark below).** The ONE bump ζ-stack exists (`src/runtime/rt/zeta_alloc.{h,c}`, all ZC axes live) and ALL FOUR frame sources folded onto it: `rt_call_proc_descr` depth-grid (4096-cap DELETED, frame_bytes honored), `g_gen_arena` (gen activations = ζ blocks, act table = resume registry), the three nest-cursor paths (64MB arena DELETED), `rt_frame()` main frame. ZERO codegen change (staged calls marshal via rt trampolines — emitted code never computes frame addresses); `bb_callee_frame.cpp` proved Prolog-facing (trail machinery), correctly untouched. REMAINDER (rides ZB-5, at GLOB grain per Lon): emitted-code-side rZ repoint + `.prev` for non-C-boundary scopes — ONE α-alloc/exit-release per GLOB (statement = GLOB; labeled sequence = GLOB), never per-BB; template-init only where a nonzero init image appears.
- [ ] **ZB-4 MODE34 + GATES** — struc-overlay emission; new no-`.bss` gate; `test_gate_emit_no_ir_mutation.sh`
  stays green; acceptance = arbno fixtures + queens solution-4 + the SCAN-SCRATCH family.
- [ ] **ZB-5 UNPAUSE SN4-PAT ARBNO** on ζ-blocks — iteration stack carved from the ζ allocator, cap removed.
- [ ] **ZB-6 (opt) MILESTONE CERTIFY** — one4all@`4757bbcd` self-host run, md5
  `abfd19a7a834484a96e824851caee159`.

#### ZB-ALLOC — THE ζ ALLOCATION PLAN (2026-07-05, from the 4/28 .s + era C sources; refines ZB-2/ZB-3)

**⌚ ZB-3 WATERMARK 2026-07-05 (third session same day, Claude Fable 5 — ACTIVATION ζ RUNTIME SIDE LANDED).**
**(1) THE ζ-STACK EXISTS:** `src/runtime/rt/zeta_alloc.{h,c}` — ONE bump ζ-stack, `zeta_choices.h`'s first runtime consumer, every axis live: mmap `ZC_ARENA_MB` MAP_NORESERVE reserve; **GC-visibility solved by `GC_add_roots` in 8MB chunks up to high-water — scan cost ∝ usage not reserve (the D3 container check; frames hold DESCR refs, invisible arenas = premature collection)**; ZC_INIT_ZERO / 0xAA-fresh-under-NONE / 0xDD-on-release poison; overflow bomb prints high-water; telemetry stderr-only under env `SCRIP_ZETA_TELEM` (oracle-stdout-safe). Header = 16B `{prev,size}` BELOW the returned fb — ⚑ deviation from ARCH §5c `{prev,mark}`: mark==base is derivable, size is required for MALLOC-mode exact `GC_remove_roots` (Lon rules if mark must also live). `.prev` chain live via `g_zls_cur` — bookkeeping-true today, load-bearing at the GC root walk.
**(2) ALL FOUR FRAME SOURCES FOLDED, runtime-only — the discovery: `bb_call_proc_staged` marshals via `rt_arg_stage`+trampolines and main frames via `rt_frame@PLT`, so EMITTED CODE NEVER COMPUTES FRAME ADDRESSES:** `rt_call_proc_descr` depth-grid DELETED (4096 cap gone; **frame_bytes now honored, max with 4KB floor — fixes the latent >4KB-frame overrun into the neighbor grid slot**); `g_gen_arena` DELETED (gen activations = ζ blocks; `g_gen_act[]` stays as the resume registry; release at exhaust-ω only — suspended frames live, §5c γ-exit-live rule); the THREE nest-cursor paths (`rt_call_named_proc`/`rt_call_proc_direct`/`rt_call_named_proc_sl`) — 64MB nest arena DELETED (**behavior note: graceful FAILDESCR exhaustion → ζ bomb; at 1GB nothing legitimate reaches it**); `rt_frame()` static 64KB → memoized ζ block. `bb_callee_frame.cpp` = Prolog trail machinery, NOT the Icon proc frame — untouched, correctly.
**(3) PROOF — the MODE-INVARIANCE GATE exercised for real:** crosscheck FAIL set BYTE-IDENTICAL to the stash-verified HEAD baseline under ALL THREE live ZC_ALLOC modes (INFINITE default / LIFO / MALLOC): m3 168/93 name-for-name (the script now prints FAIL(m3) — instrument-symmetry patch this session), m4 168/3/90 = {082,099,213}, DIVERGE=0; icon smoke 12/12×2 per mode; the 6 mandated gates PASS; full gate sweep = 23 FAILs, ALL stash-verified pre-existing at HEAD (identical verdict vector baseline vs ZB-3). Emitter/templates untouched → .s regen N/A by construction.
**(4) NEW CAPABILITY:** Icon `f(6000)` recursion runs BOTH modes (HEAD aborts at the 4096 guard) — flat-model casualty (d) closed at the arena level. LIFO telemetry exact: allocs 6002 / releases 6001 / live 1 (the main frame) / hiwater 24,741,664B = 6001×4112.
**(5) FINDINGS + THE GLOB DIRECTIVE (Lon, this session):** MALLOC diagnostic ceiling found — per-block `GC_add_roots` hits libgc MAX_ROOT_SETS (f(2000) passes, f(6000) "Too many root sets"). **Lon: the fix-by-design is GLOB-GRAIN ACTIVATION — ONE entry alloc / ONE exit release per GLOB (each SNOBOL4 statement is a GLOB; each labeled sequence of statements is a GLOB), never per-BB: volume ∝ statements executed, the ceiling recedes, MALLOC becomes a true per-glob-lifetime ASan instrument.** Recorded in ARCH §4 ZL-GROUP + §5j; it IS the grain for the ZB-3 remainder. Makefile gained `ZCFLAGS ?=` wired through BOTH products (the .so recipe had hardcoded flags — §5j's zero-edit mode swap now actually true for mode-4; caveat: flags aren't a make prerequisite, `rm out/libscrip_rt.so` before a mode rebuild).
**(6) zls[] NAMING (Lon question answered):** the code IS `zls` — `zeta_storage.{h,c}`, `zls_*` API, `zls_field_t`/`zls_scope_t`; the docs' `zl[]`/`zl_build()`/`zl.c` prose was pre-retraction leftover — normalized to `zls[]`/`zls_build()`/`zeta_storage.c` this session (ARCH + this file).
**D-ROWS TOUCHED (Lon rules):** D3 annotated with container data · D13 SELFLOAD not built (awaiting the call) · D15 LIFO flip: full-corpus proof in hand, flip-ready.
**NEXT = Lon rules D3/D13/D15; then ZB-4 (struc overlays + no-.bss gate) or ZB-5 (COLLECTIONS/ARBNO on ζ at GLOB grain).**

**⌚ ZB-2 WATERMARK 2026-07-05 (second session same day, Claude Fable 5 — VERIFY + ZB-2 v1 LANDED).**
**(1) ARCH-ZETA-LOCAL-STORAGE.md FULLY RE-VERIFIED against sources per Lon directive — every checked claim EXACT:** `ir_drive_slot_assign`@scrip_ir.c:206 single-cursor + per-op grant table · xa_flat.cpp `push r12; mov r12,rdi` · `g_proc_arena`@rt.c:348 GC_MALLOC depth×qwords · IR_t.tmp@IR.h:156 · emit.cpp:980/984/996 scratch setters · zeta_choices.h all 9 axes + #error guards, included-by-nothing (now: zeta_storage.c; ZB-3: + zeta_alloc.c, the runtime consumer) · seeds 1–6 no-realloc, seed-2 `_13_t _13_a[64]`@154 `_23_t _23_a[64]`@254 · arbno_alt.s 156 lines `arb3_stack resq 64`@:24 · one4all@4757bbcd re-cloned: beauty_prog.s 70,840 lines, census rbp 10,036 / r12 3,937 / r14 205 EXACT, fn_upr clone site @~8437 verbatim (incl. `P_upr_ret_γ` static continuation write), blk_alloc.c 58 lines header-verbatim, snobol4_asm.mac:2040 ARBNO macros, emit_x64.c 9,759 lines :579/:932/:965 quotes verbatim, **chunk table = exactly 1,094 annotated `dq 0` rows across 131 `box_*_data_template` families** (grep-precise) · BB-GEN-X86-BIN.md arbno ~1556B grid · ARCH-ICON per-α/depth-arena lines. Addendum: `x86_scratch_off` READER templates also include dormant bb_match_{arbno,fence,span_var} (only 5 of the 8 are in the Makefile; setters remain the 3 emit.cpp sites).
**(2) BASELINE RE-DERIVED at session HEAD (the 115/261 watermark below is stale):** crosscheck **mode-3 168/261 (93 FAIL), mode-4 168 PASS / 3 FAIL / 90 SKIP, DIVERGE=0** (m4 FAILs = the known 082/099/213). Icon smoke 12/12 ×2 (container needed `make libscrip_rt` — the smoke's mode-4 arm silently 0/12s without `out/libscrip_rt.so`; build it in session setup).
**(3) ZB-2 v1 LANDED** (ladder entry above has the full design record): zeta_storage.{h,c} single grant table + typed field maps + LOWER-marked groups + `--dump-zeta` + emitter parity instrument + tmp-as-mirror. **PROVEN INVARIANT:** crosscheck EXACTLY equals the re-derived baseline (same counts, same FAIL set, DIVERGE=0); Icon smoke 12/12 ×2; gates no_ir_mutation/no_lang/no_slot_alloc GREEN; **.s byte-identity vs stashed HEAD build on every checked program.**
**(4) REGEN SCRIPTS RUN (RULES step 4) — ZERO ARTIFACTS CHANGED across benchmark/feature/demo/icon suites: the mechanical invariance proof.** CORRECTION to an in-session hypothesis: manual byte-diffs first suggested stale committed .s (indirect_dispatch, rung36_jcon_{args,arith,augment,scan}) — the regen runs revealed those programs ABORT under `--compile` (EMIT-FAIL/CERR; my manual diffs compared committed full .s vs partial-crash output). Artifacts correctly untouched per the honest-current-output rule. HEAD==ZB-2 stash-verified on every diffing case regardless, so the invariance conclusion stands on both instruments.
**(5) Housekeeping:** kind_names[] gained the full IR_MATCH family (dump/print readability); `bb_label_registry_count/get` enumeration API added (lower_common.c — zl no longer uses it after the marks pivot, kept for future consumers); **`seed/beauty_prog_0428.s` committed to SCRIP (Lon directive: the 4/28 milestone artifact now lives IN the repo — the M2 carry-the-design-forward lesson, applied).**
**NEXT = ZB-3 ACTIVATION ζ** (allocator + port prologues per §2–§3 of the plan below; the ZC_ALLOC axes are live-includable now).


**Evidence addendum (C side):**
- `artifacts/c/beauty_prog.c` @4757bbcd (17,648 lines): ZERO structs, ZERO ζ — the era C backend flattened to
  C locals + runtime `pat_*` heap constructors (`pat_cat(pat_user_call(...))`). **The chunk model was an
  ASM-backend invention.** (Pivot's PRIVATE flag: CLOSED — Lon confirmed in-session the repo is public
  intentionally, for session convenience.)
- `archive/backend/blk_alloc.c` (58 lines): era allocator = **mmap PER CALL** — header verbatim: "CODE is
  shared (read-execute); DATA is per-invocation (read-write)". Correctness-first, one syscall per activation;
  the bump ζ-stack keeps the private-DATA principle, deletes the syscall.
- Era generator READ (Lon: "the C code that generates S" = this file): `archive/backend/emit_emitters/
  emit_x64.c` @4757bbcd, 9,759 lines. Self-description: "All pattern variables live flat in .bss as QWORD
  (resq 1) slots"; "ARBNO — flat .bss cursor stack, zero-advance guard". Static layout was DELEGATED TO THE
  ASSEMBLER by name (`A("%-24s resq 1\n", vars[i])`, line 579) — no offset assigner for statics ever existed;
  offsets lived only inside `box_%s_data_template` blocks, resolved through `var_register()`/`bref()`
  (`emit_arbno` registers `dep`/`cur_before` via bref → the artifact's `r12+280/+288`); clone-tier memcpy at
  3253, cheap-tier `lea r12,[rel template]` at 2156/2167. `emit_arbno` (932): the 64-slot stack sat in an
  ad-hoc 512-entry static decl list ("stk: emit as resq 64 — we track this separately", 965). ZB-2 reading
  remainder: the bref/offset-cursor internals.
- Current seeds (`SCRIP/seed/test_sno_1..6.c`): NO `realloc` anywhere; ARBNO only in seeds 1/2.
  `test_sno_2.c` declares per-instance TYPED frame arrays (`_13_t _13_a[64];` line 154, `_23_t _23_a[64];`
  line 254) — the element-array precedent. Seeds 5/6 are malloc-era models (`<malloc.h>`). The REALLOC array
  is NEW design (Lon directive, this session), grafting growth onto the seed-2 shape.
- Seed `.github/test_sno_1.c` (ARBNO region) = the distilled model: `ζ = &_1[ARBNO_i=0]` at α,
  `ζ = &_1[++ARBNO_i]` going deeper, fail path `ARBNO_i--; ζ = &_1[ARBNO_i]; goto alt_β`. **The per-iteration
  frame carries the ENTIRE body-subgraph's box fields** (`ζ->alt`, `ζ->alt_i`, `ζ->ARBNO`) — body re-entrancy
  is free because the frame IS the body's layout; the box's own depth/accumulator live in the ENCLOSING frame
  (matches asm `r12+280`). On the live 100%-BB spine (no SM), this generalizes to ALL code, not just patterns.

**THE PLAN — one allocator, four layout classes, one invariant:**
1. **Layout classes** in the parallel `zls[]` table (node-id keyed, PEERS-clean), sized by `zls_build()`
   post-optimizer / pre-emit:
   **ZL-GROUP** — label-group (labeled stmt + trailing unlabeled): every non-re-entrant box instance's fields
   (absorbs the dead SM tier's expression temporaries). **ZL-FN** — DEFINE-body aggregate: `{prev, mark}`
   header + arg/local t·p pairs + its ZL-GROUPs concatenated + ret_γ/ω continuation cells (evicted from
   statics). **ZL-PAT** — per match-activation mutable pattern state; GLOB shape sealed `[rip+disp]` per
   RULES; dynamic pattern VALUES read their shape via pointer, mutable part still ZL-PAT in the invoker.
   **ZL-ITER** — re-entrant-box iteration frame: `{prev}` + the box's BODY-subgraph layout (the seed's `_1[]`
   element) — uncapped, covers dynamic BBs (runtime-sized frames are fine: bump takes any size).
2. **Allocator: ONE bump ζ-stack in the RX slab.** `zS` in a fixed slab cell `[rbx+ZS_OFF]` (zero registers
   burned; r15 promotion only if the `x86_asm.h` roster and a bench say so). α-entry: `mark=zS;
   blk=bump(sz); blk.prev=rZ; rZ=blk`. Scope exit (final-γ or ω): `zS=mark; rZ=prev`. rZ = r12 (continuity
   with `xa_flat.cpp` and the 4/28 artifact). Init = zero-fill v1 (`rep stosq` — faithful: era templates were
   all `dq 0`); init-images only if a nonzero-init field ever appears.
3. **Iteration (REVISED — Lon directive 2026-07-05): REALLOC ARRAYS INSIDE THE ARBNO BOX.** Supersedes the
   ZL-ITER-as-stack-frame framing in §1: ZL-ITER is the ELEMENT layout (the body-subgraph's fields — the
   seed-2 `_N_t`); elements live CONTIGUOUS in a realloc-grown array OWNED by the box. The box's own zeta
   fields (in the ENCLOSING activation layout): `{iter_ptr, iter_cap, iter_i, prev_rZ}` — the seed's
   `ARBNO_i` plus its array, made growable. Ports: α `i=0; lazy-ensure cap; rZ=&ptr[0]`; child_ok/α1
   (progressed) `i++; if(i==cap) ptr=rt_zarr_grow(ptr,&cap,fsz); rZ=ptr+i*fsz`; β `if(i==0)→ω-final;
   i--; rZ=ptr+i*fsz; →child_β`; final exits restore `rZ=prev_rZ`. The element IS the body's activation
   base — body boxes keep uniform `[rZ+disp]`. **RELOAD LAW:** realloc MOVES; an rZ into an iter array is
   NEVER cached across a push — recomputed from `(ptr,i)` at every owning-box port (grow happens ONLY at
   push, so the body sees a stable base within any single child pass). Corollary: NO pointer into an iter
   element may ESCAPE the body; cross-box refs go via the enclosing zeta or `(ptr,i)`. Nesting: an outer
   element CONTAINS the inner box's `{ptr,cap,i,prev}` quad — recursion-safe by construction. Backing v1 =
   heap `realloc` (seed-5/6 house style); free at owner ω-final, plus a per-activation grown-array list
   walked at scope release for the γ-exited-live case (mark/release stays O(1)+ε). Perf rung later:
   ζ-stack-backed grow-in-place-when-top. The `resq 64` cap and the mmap both die; §4's LIFO invariant is
   untouched — arrays are box-owned, orthogonal to ζ-stack ordering.
4. **THE LIFO INVARIANT (soundness):** Byrd traversal under mark/release is LIFO — failure fully unwinds
   rightward frames before any left-β re-entry; success releases wholesale at the scope mark; a γ-exit MAY
   leave frames live (they die at the enclosing mark). Suspendables (Icon suspend / coexpr) BREAK LIFO ⇒
   their scope's block heap-promotes at creation (the already-deferred promotion rung); GATE until then: no
   suspendable box inside a bump-lifetime scope.
5. **Emitter contract:** reads `(scope_id, off)` from `zls[]` ONLY; `[rZ+disp]` in BOTH modes (byte-identical,
   MODE34); mode-4 additionally prints `struc/endstruc` overlay headers (`ZG_/ZF_/ZP_/ZI_` prefixes) —
   documentation, zero storage, NO `.bss`, NO bare `resq`.

Rung mapping: ZB-2 = `zls_build()` + `--dump-zeta` (+ read `emit_emitters/emit_x64.c` first); ZB-3 = allocator +
port prologues (§2–§3); ZB-4 = the gates as listed; ZB-5 rides §3.

**Session hygiene (this commit):** the ORIENTATION SYNOPSIS section is DELETED per Lon directive 2026-07-05 —
sessions read the directed ARCH docs in full instead. Dangling refs pending Lon's call: PLAN.md:34
(session-start step 7 still points at the deleted synopsis), ARCH-SCRIP.md:3 (same), this file's stale
"Original ORIENTATION SYNOPSIS below is UNCHANGED" sentence (~line 705), and ARCH-SCRIP.md's stale "optimizer
OFF by default" (RULES 2026-07-03: ON). The SN4-PAT ARBNO rung is PAUSED pre-implementation by this pivot;
its frontier notes stand in the ladder below.

## ⛔⛔ #1 PRIORITY — SN4-PAT — SNOBOL4 PATTERN MATCHING, RECONSTRUCT THE AMPUTATED IR FAMILY (Lon, 2026-07-04; elevated to top-of-ladder same day — this rung is read and worked FIRST, before every section below, including the JCON-IN-SCRIP directive and all Icon rungs)
**THE RUNG NAME IS `SN4-PAT`.** The non-pattern SNOBOL4 subset is already complete on the live spine (literals,
vars, keywords, `.NAME`, arith+concat, unary, `$`, subscript/`DEREF`, calls, gotos/labels, every assignment LHS
form, DEFINE/DATA/OPSYN). **The wall is pattern matching** (`lower_snobol4.c:257` — any `:pat` field or `TT_SCAN`
subject `sno_fatal`s). Pattern matching genuinely needs new opcodes — the existing Icon SCAN family is anchored
control-flow, not SNOBOL's first-class floating-needle-over-a-DT_P-pattern model — so this is NOT an
"existing-IRs" job. **It IS a RECONSTRUCTION**: the full pattern IR family existed and was amputated wholesale,
and the design is recoverable from git.

**PROVENANCE (all in `git log`):**
- `8de0fb46` GZ#5 ENUM-AMPUTATION — removed 119 non-Icon members incl. the 53-opcode pattern family (design
  survives at parent `41b53078`).
- `2e5a5a3e` — matcher family was `IR_PAT_*`, renamed `IR_MATCH_*` to mirror `bb_match_*`.
- `18133720` FZ-3 — pattern CONSTANT FOLDING: an all-constant (VARIANT-free) subpattern → sealed
  `IR_REF_INVARIANT` RO blob, built once not per-match. **This is the "IR_INVARIANT" Lon means.**
- `547de08d` / BB-REVAMP-TRACKER — the 21 `bb_match_*` templates (abort/advance/any/arb/arbno/atp/break/
  breakx/capture/defer/fence/head/len/notany/pos/rem/retry/rtab/span/span_var/tab).

**THE MODEL (SPITBOL, two families + one ref — re-added to `IR_e` this session, build stays green):**
- `IR_MATCH_*` (28) = MATCHERS: the inline needle. `lower_pat_node` (recover from `41b53078:lower_snobol4.c`,
  ~200 lines) compiles a pattern tree into one node per element, wired by γ(success)/ω(failure); `IR_MATCH_ALT`
  = backtrack tree, `IR_MATCH_CAT` = concatenation thread, `IR_MATCH_ASSIGN_IMM/_COND` = `$`/`.`. Used for
  direct `SUBJECT PAT [= REPL]`.
- `IR_PATTERN_*` = STITCH boxes ONLY. The per-element builders (LIT/ANY/SPAN/LEN/…) are the ABANDONED pre-D7
  era — do NOT resurrect them. The real design (D7 PIVOT `d7ba0fd9` → `52fce031` `rt_pattern_build` +
  `rt_pattern_stitch_cat`/`_alt`; B3 STITCH-ALT `7a12aedd`; B6 STITCH-CAT `409f62a9`/`a59f38b8`; FZ-3
  `18133720` + FZ-4 `6141434` folding): every VARIANT-free subpattern is constant-folded into a sealed
  `IR_REF_INVARIANT` blob; only VARIANT parts are stitched at the reference site via `IR_PATTERN_CAT`/`_ALT`
  stitch boxes; `IR_PATTERN_CAPTURE` is passthrough (FZ-4); `IR_PATTERN_DEFER` = `*EXPR`; `IR_DTP_ASSIGN` =
  stored-pattern `.`/`$` (DTP frag, `src/include/dtp.h`). **[HISTORY CORRECTED 2026-07-04, case-fixed grep:
  `rt_pattern_stitch_*`/`rt_pattern_build` were superseded PRE-parent by the freeze+blob design — do NOT
  resurrect them; the parent snapshot is the final authoritative form, and `sno_freeze_pat_graph_entry` lives
  in the parent's `lower_snobol4.c`, RECOVERED to disk — see FOLD + the PARK-NEVER-DELETE directive below.]**
- `IR_REF_INVARIANT` (1) = the folded-constant sealed blob that VARIANT stitching references.

**LADDER (incremental, keep build green each rung; land one matcher end-to-end at a time):**
- [x] **SN4-PAT-0 ENUM** — re-add the family to `IR_e` before `IR_OP_COUNT` (additive; `-w` build so no
  exhaustiveness break; inert until lowered). LANDED 2026-07-04, `make scrip` green. **[CORRECTED same day
  (Lon): the initial re-add faithfully copied the parent snapshot's 24 per-element `IR_PATTERN_*` builders —
  but those were the ABANDONED pre-D7 era (a grep-alternation bug hid the stitch history). Dropped to the
  stitch-era five: `IR_PATTERN_CAT`/`_ALT` (stitch boxes), `_CAPTURE` (passthrough), `_DEFER`, + re-added
  `IR_DTP_ASSIGN`. Family is now 34 members (28 `IR_MATCH_*` + `IR_REF_INVARIANT` + 5). Rebuilt green.]**
- [x] **SN4-PAT-1 TEMPLATE-REVIVE (LEN first)** — LANDED 2026-07-04, build green. `bb_match_len.cpp` back in the
  Makefile (source list + compile rule); it compiles against today's headers with **ZERO drift** (BB-FIXUP
  `547de08d` had kept it current — no `IR_node_alloc`/`bb_build_flat` reconciliation needed after all).
  `bb_match_len()` declared in `bb_templates.h`; `case IR_MATCH_LEN` added to `emit.cpp` dispatch (beside
  `IR_TO`, line ~724). Inert until SN4-PAT-2 emits the node, so Icon + existing SNOBOL4 subset unchanged.
  NOTE for SN4-PAT-2: the template reads `_.op_ival` (the LEN count) and emits the anchored δ+n≤Δ advance with
  γ/ω ports — it assumes it sits inside a floating harness, so SN4-PAT-2 must also supply the retry-at-each-
  start-position loop (that's what `IR_MATCH_HEAD`/`IR_MATCH_RETRY`/`IR_MATCH_ADVANCE` are for) unless the
  program is `&ANCHOR`-mode.
- [x] **SN4-PAT-2 LOWER-LEN** — LANDED 2026-07-04 (this session). `L LEN(3) . X` → `abc` m3==m4==oracle; bare
  `L LEN(3) :S/F` matched/nomatch both paths both modes; conditional-capture semantics oracle-pinned (X untouched
  on failure); corpus m3 115→117, m4 FAIL set byte-identical to pre-session baseline (stash-verified). DESIGN
  (Lon directive, this session): the 3-box HEAD/RETRY/ADVANCE harness was REPLACED mid-rung by ONE generator box —
  `IR_MATCH_HEAD` is generator-kind (`ir_query.c`), α = `rt_match_enter` (stateless DESCR→{ptr,len} mirroring
  `rt_scan_enter`, sets Σ/Σlen for capture) + start=0 + r14d=start + jmp γ; β = start+=1, bounds vs Δ, `g_anchor`
  gate, loop — the unanchored retry IS the Byrd resume, `bb_to.cpp` shape. Pattern-fail edges β-stamp via local
  `sno_ω_to` (lower_icon.c precedent); `fJ` chain-reachability comes free from the stock generator-kind ω rule
  (the 3-box BFS special-case was reverted). `bb_match_retry.cpp`/`bb_match_advance.cpp` restored to pre-session
  bytes, unwired, DEAD under this design. Capture = `IR_MATCH_ASSIGN_COND` → `bb_match_capture` phase-1 COND arm
  (op_off = head's start slot, operands=[pat-entry, harness-box]); op_sval whitelist in `walk_bb_node` preamble
  grew the op. NOTE for SN4-PAT-3..N: single-element capture equates pattern-start with attempt-start; multi-
  element CAT needs the phase-0 SAVE arm + its own saved-δ slot. `= REPL` splice still bombs (deferred, wall text
  updated at the old `:257` site).
- [x] **SN4-PAT-3a LIT** — LANDED 2026-07-04 (this session). `bb_match_lit.cpp` written fresh (never existed;
  `IR_MATCH_LIT` had no template — do not confuse with the orphaned pre-family `bb_lit.cpp`, unwired, park-
  candidate). memcmp-based, β rewinds δ by n (adopted from `bb_lit.cpp`'s pattern — needed once CAT chains
  backtrack through a matched LIT). Oracle-pinned: anchored/floating/absent/capture, empty lit, overlong,
  tail-boundary, capture-untouched-on-fail — m3==m4==oracle all paths.
- [x] **SN4-PAT-3b ANY/NOTANY** — LANDED 2026-07-04. Templates pre-existed on disk, unwired; wiring exposed a
  live bug on first-ever execution: the single-char fast path emitted `x86("cmp","sil",imm)` — the `x86()`
  dispatch has no 8-bit-register case, so it silently returned empty (no bomb) rather than failing loud,
  leaving the branch testing stale flags from the bounds check. Fixed: `sil`→`esi` (movzx already zero-
  extends). **Any other unwired template calling `x86()` with an unencodable form has the same latent bug —
  the dispatch declining silently instead of bombing is an emitter-wide footgun, not scoped to this rung.**
  Literal-charset-arg subset only (the parked file's `dval=1.0` var-arg tag is the DIVISION-RULE flag pattern,
  not carried over).
- [x] **SN4-PAT-3c SPAN** — LANDED 2026-07-04. **Real finding:** `_.x86_scratch_off` (read by `bb_match_span`/
  `_arb`/`_arbno`/`_break`/`_breakx`) is declared in `sm_emit_t` and read by five templates but was **written
  nowhere in the codebase** — permanently 0 via static zero-init, a live TMP-ERADICATE violation (any value
  legitimately at frame slot 0 gets silently clobbered) that was invisible only because nothing reading it had
  ever been dispatched. Fixed at LOWER: granted `IR_MATCH_SPAN` a slot in `ir_drive_slot_assign`
  (`nd->tmp = base+k*16; k+=1;`, mirrors the `IR_MATCH_HEAD` grant one line above it), then
  `g_emit.x86_scratch_off = drive_value_slot(nd)` in the DRIVE dispatch — zero emitter-side allocation, per
  rule. Verified the grant does real work (not just satisfies the FATAL-if-ungranted check) with a slot-
  collision probe: two globals alive across the SPAN scratch write, sum checked post-match against oracle.
  **⚠ CARRY FORWARD — BREAK/BREAKX (next in tracker order) read this SAME unwritten field. Grant it in
  `ir_drive_slot_assign` (same one-line pattern) BEFORE wiring their dispatch cases, or this exact landmine
  reappears.** ARB/ARBNO inherit the identical defect when their turn comes later in the ladder.
- [x] **SN4-PAT-3d BREAK/BREAKX** — LANDED 2026-07-04. Applied the SPAN lesson up front instead of rediscovering
  it: both templates read the same never-written `_.x86_scratch_off` (BREAKX uses both `+0`/`+4`, same as SPAN
  — one 16B slot covers it), so both got the `ir_drive_slot_assign` grant (`k+=1` each, same pattern) BEFORE
  their dispatch cases went live — first build was clean, no FATAL. Literal-charset-only subset (matches
  ANY/NOTANY/SPAN precedent). Oracle-pinned: BREAK head/absent/empty/zero-length-at-cursor, BREAKX head/zero-
  length-retry/absent, all m3==m4==oracle. **Two-matcher collision probe** (BREAK + BREAKX both live in one
  graph, two globals alive across both scratch writes, non-colliding sum) confirms independent per-node slots
  — the grant generalizes correctly when multiple scratch-using matchers coexist, not just one at a time.
  **⚠ CARRY FORWARD — ARB (later in tracker order) reads this SAME field. Grant it before wiring.**
- [x] **SN4-PAT-3e TAB/RTAB** — LANDED 2026-07-04. Separate opcodes (`IR_MATCH_TAB`/`IR_MATCH_RTAB`), int-literal
  arg baked directly into `IR_LIT(nd).ival` at LOWER (no operand node, no `ir_operand_push` — same as LEN;
  confirmed neither is in `ir_node_produces_value()`, so no `nd->tmp` grant applies or is needed; emitter reads
  the constant via the generic `op_ival` preamble and bakes it as an x86 immediate, never a memory load). No
  scratch slot required (unlike SPAN/BREAK/BREAKX). **Bug caught before it hit the corpus:** `bb_match_tab.cpp`
  enforced the forward-only constraint (`current_cursor > n → fail`) but had **no upper-bound check against
  `r15d` (Δ)** at all — `TAB(99)` on a 10-char subject incorrectly matched, jumping the cursor to 99 (past the
  subject end). Found by direct comparison against `bb_match_len.cpp` (the correct sibling doing an analogous
  bounds check via addition) rather than the full monitor harness — justified here because the divergence was
  already bracketed to one un-composed statement in a template authored this same session, not inherited logic;
  fix verified empirically against oracle both pre/post, including fencepost cases (`n==Δ` succeeds, `n==Δ+1`
  fails, `n==0` succeeds) since bounds-check fixes are exactly where off-by-one errors hide. Fix: added
  `cmp r15d, n; jl ω` before the existing forward check. **`bb_match_rtab.cpp` was NOT touched** — its overlong
  case (`RTAB(99)` on a 10-char subject) already failed correctly, but by accident: `Δ-n` underflows to a
  negative signed value when `n > Δ`, and any non-negative cursor position compares "greater than" a negative
  target under signed `jg`, so it fails for an incidental reason rather than an explicit check. Left alone
  since it isn't broken and isn't this rung's scope — flagged here in case a future rung's fencepost probe
  finds a case where the accident doesn't hold (e.g. `n` chosen so `Δ-n` wraps positive again at extreme
  magnitudes — not exercised, not ruled out).
- [x] **SN4-PAT-3f TAB/RTAB TWO-MODE RETROFIT** — LANDED 2026-07-04 (Lon-directed proof-of-concept). **The gap:**
  every SN4-PAT-3 matcher (LEN through RTAB) gated the AST shape at LOWER time (`t->c[0]->t == TT_ILIT`) and
  `sno_fatal`'d on anything else — meaning none could accept a variable/computed argument, which is arguably
  the *more* common real-world SNOBOL4 shape (`TAB(I)` far more common than `TAB(3)`). **The correct precedent,
  already live in this codebase:** `IR_SCAN_TAB`/`_MOVE`/`_POS` (Icon) do zero shape-checking at LOWER — the
  argument is lowered as an ordinary expression (in fact `IR_SCAN_TAB` isn't even a dedicated lowering arm; it's
  a generic `IR_CALL` whose opcode gets *retagged* post-hoc by `icn_retag_scan_body` purely from the builtin
  name) — and the EMITTER's DRIVE case is the ONLY place that folds: `a0->op == IR_LIT_INTEGER` → bake immediate
  (`op_sb`); else → read the operand's already-registered runtime slot via `bb_slot_get` (`op_sa`, sign as the
  discriminant). **Retrofit applied to TAB/RTAB, mirroring this exactly:**
  - `sno_pat_node`'s signature changed from `(IR_graph_t * g, ...)` to `(scx_t * cx, ...)` (deriving `g = cx->g`
    locally) — needed so pattern arms can reach `sx_lower`, the general recursive expression lowerer. Both call
    sites (the one recursive self-call, the one external call from `sno_lower_match`) updated. **This signature
    is now available to every future pattern arm that needs a general argument — the plumbing cost was paid
    once.**
  - `TT_TAB`/`TT_RTAB` LOWER arm: dropped the `TT_ILIT` gate entirely (matching the retag precedent's zero-
    special-casing) — now unconditionally `sx_lower`s the argument, wires it via `ir_operand_push`, returns the
    argument's own entry chain (not the TAB node) since the argument must execute first.
  - `sno_pat_supported`: TAB/RTAB relaxed from `t->c[0]->t==TT_ILIT` to "any argument present" — shape no
    longer LOWER's concern.
  - Emitter DRIVE case: rewritten to inspect `nd->operands[0]`, branch on `a0->op == IR_LIT_INTEGER` exactly
    like `IR_SCAN_TAB`, using `op_sa`/`op_sb` (replacing the old generic `op_ival` read, which is meaningless
    once the constant may live on a *different* node than `nd`).
  - Both templates: replaced the direct `(long)(int)_.op_ival` immediate with
    `IF(_.op_sa>=0, mov rax,FRQ(op_sa+8)) / IF(_.op_sa<0, mov rax,(long)op_sb)`, then unchanged bounds-check
    logic against `eax` instead of a baked constant.
  **Proof, not just passing tests:** dumped the actual `.s` output — `TAB(3)` emits `mov rax, 3` (immediate,
  zero memory access, byte-for-byte the old fast path); `TAB(N)` emits `mov rax, qword ptr [r12+104]` (genuine
  runtime load). Same opcode, same template, provably different code shape depending on what the argument
  turned out to be — not merely "tests pass," the mechanism is visibly correct. Oracle-verified: literal (all
  prior pins re-confirmed unchanged), bare variable (`TAB(N)`/`RTAB(R)`, including runtime-value overlong-
  bounds cases), and a genuine computed expression (`TAB(N+1)`, an `IR_BINOP` operand — proves "any expression,"
  not just "also accepts a variable"). Full corpus regression clean (m3/m4 counts and FAIL set unchanged —
  no existing corpus program yet exercises variable-argument TAB/RTAB, so this is net-new capability, not a
  fix to a previously-failing case).
  **⚠ DECISION PENDING (Lon) — retrofit the remaining 7 (LEN, LIT, ANY, NOTANY, SPAN, BREAK, BREAKX)?** LEN is
  the same int-arg shape as TAB (should be a quick mirror). LIT/ANY/NOTANY/SPAN/BREAK/BREAKX are all
  string/charset-arg shape — a DIFFERENT retrofit (fold check becomes `a0->op==IR_LIT_STRING`, general path
  reads a string descriptor's pointer+length instead of one int) — and SPAN/BREAK/BREAKX additionally still
  carry the scratch-slot grant from SN4-PAT-3c/3d, which needs to keep working alongside the new operand-based
  charset. Not yet started; the plumbing (`sno_pat_node`'s `cx` signature) is in place for whoever picks this
  up.
- [x] **SN4-PAT-3g POS/RPOS/REM/ARB** — LANDED 2026-07-04. POS/RPOS = one opcode (`IR_MATCH_POS`) + `"r"` sval
  marker per parked design (existing-IRs-only constraint), built TWO-MODE FROM BIRTH (TAB recipe: operand +
  emitter fold; `RPOS(N)` variable-arg oracle-proven). REM/ARB take scratch grants; REM gained α-save/β-restore
  (its consumption Δ−entry isn't recomputable, unlike LIT's fixed n); ARB added to `ir_is_generator_kind`
  (its β IS extend-and-retry) and its β exhaust path fixed to restore entry cursor (box invariant). **Parser
  fact learned:** bare `REM`/`ARB` (no parens) arrive as `TT_VAR "REM"` — the parked TT_VAR name-dispatch arm
  is load-bearing; restored for REM/ARB only (FENCE/ABORT/BAL names fatal until their rungs). **Ops note:** a
  vanished-on-rebuild fatal traced to a suspected stale link — `make ... | tail -1` hides whether the edited
  TU actually recompiled; force `rm` the .o when in doubt. All 13 session pins re-verified byte-identical;
  corpus unchanged (138/137) — single-element POS/REM/ARB are rare in corpus; the unlock arrives with CAT.
- [x] **SN4-PAT-3h CAT + phase-0 capture SAVE** — LANDED 2026-07-04 (this session). **CAT is NODE-FREE in the
  live single-HEAD design** — the parked `IR_MATCH_CAT` was a subgraph SUCCEED-sink; here pattern success
  threads straight to `sJ`, so concatenation is pure edge-threading with no node and no template (`bb_match_cat.cpp`
  stays UNWIRED — do not add it). `case TT_SEQ` in `sno_pat_node`: lower right-first `(succ,fail)`, then left with
  `succ = right-entry`; return left-entry. Deterministic elements' ω already point at `fail` (=head=retry-position,
  correct SNOBOL4 — SPAN/BREAK/LEN never back off); the ONLY resumable leaf today is ARB (generator-kind), so if the
  left tail `ir_is_generator_kind`, re-point right's tail-ω at it via `sno_ω_to` (β-aware) — the rc/lc tail nodes are
  recovered by the parked `g->all[before]` first-allocated-is-rightmost-leaf trick. `sno_pat_supported` relaxed to
  admit `TT_SEQ` recursively.
  **phase-0 capture SAVE (the SN4-PAT-2 multi-element note, now resolved):** a capture spans `[inner-start, current)`,
  NOT `[attempt-start, current)` — so `TAB(3) LEN(2) . V` on `abcdef` must yield `de`, not `abcde`. Added additive enum
  `IR_MATCH_ASSIGN_SAVE` (right after `_COND`): a phase-0 node placed at the capture's OPEN that does `mov FR(off),r14d`
  into its OWN δ-slot; the phase-1 COND reads that slot (`operands[1] = save`, so `op_off = drive_value_slot(save)`).
  Wiring per rung: enum (`IR.h`) · δ-slot grant in `ir_drive_slot_assign` (`k+=1`, HEAD one-liner precedent, `scrip_ir.c`) ·
  DRIVE case `op_off=own slot, op_phase=0` + dispatch case → `bb_match_capture()` + op_sval whitelist add (all `emit.cpp`) ·
  the template's phase-0 arm was MISSING `jmp γ` (never exercised pre-session) — added (`bb_match_capture.cpp`) · LOWER
  `TT_CAPT_COND_ASGN` rewritten to emit SAVE→inner→COND and return the SAVE as the capture entry. Single-element captures
  still pass (SAVE just records the attempt-start = old behavior).
  **RESULTS (oracle=`sbl -b`, m3=`--run`, m4=`--compile`+gcc; all m3==m4==oracle):** crosscheck patterns 8→13
  (044 pos, 045 rpos, 046 tab, 047 rtab, 048 rem, 049 arb, 055 concat_seq now green — the deterministic-concat +
  multi-capture set); capture rung 2→4 (060 multiple, 061 in_arbno); mode-3 ladder total 86→93; ZERO regressions on the
  8 already-green rungs (hello/output/assign/concat/arith_new/control_new/functions/data). NOT YET regenerated: the
  `.s` artifacts (handoff step 4 — capture codegen changed, so `util_regen_{benchmark,feature,demo}_s_artifacts.sh` owe a
  commit) — a follow-up must run them.
- [x] **SN4-PAT-3h ALT** — LANDED 2026-07-04 (this session). Phased `IR_MATCH_ALTERNATE` (mirrors the capture
  phases): phase-0 SAVE records the ALT-entry cursor into a scratch slot (grant in `ir_drive_slot_assign`,
  `k+=1`); phase-1 RESTORE reloads it before each subsequent alternative so a failed cursor-advancing
  alternative can't leave the next one mid-input. Alternatives chain via ω: `alt[i].fail → RESTORE_{i+1} →
  alt[i+1]`, last → outer fail, each `alt.succ → succ`. `sno_pat_node` `case TT_ALT`: flatten the left-assoc
  spine L-to-R, build `save = IR_MATCH_ALTERNATE` (n_operands==0 ⇒ phase 0), loop i=na-1..1 lowering alt i and
  minting a RESTORE (n_operands==1, operand=save ⇒ phase 1, `op_off = drive_value_slot(save)`), then alt 0 with
  `fail = RESTORE_1`; `lc_γ_to(save, e0)`; return save. Template `bb_match_alt.cpp` rewritten (was bare
  `x86_pair_loop`) as the two-phase `mov FR(off),r14d`/`mov r14d,FR(off)` + `jmp γ`, wired in the Makefile;
  DRIVE + dispatch in `emit.cpp`; gate relaxed for `TT_ALT`.
  **EMITTER FINDING (carry forward — bit ALT, will bite FENCE/ARBNO too):** the flat chain-BFS worklist
  (`emit.cpp` ~1350–1392, TWO passes) enqueued every node's γ but followed ω ONLY for BINOP/CALL/SUBSCRIPT/
  generator-kind — so an **ω-only backtrack target** (the ALT RESTORE, reached only via a preceding
  alternative's ω) was never discovered, never emitted, and its ω silently defaulted to `main_ω` (whole graph
  collapsed to one alternative). Root fix: **the match family's ω is a genuine control edge** (next alternative /
  fail handler), so both BFS passes now follow ω for `op ∈ [IR_MATCH_LIT, IR_MATCH_ASSIGN_SAVE]`. Behavior-neutral
  for every prior test (their ω targets — HEAD, next element — were already discovered; the enqueue dedups), only
  `.s` node-numbering shifts (never a gate). Any future SN4-PAT node that is reached ONLY via ω (FENCE seal-back,
  ARBNO retry) is now discoverable for free.
  **RESULTS (m3==m4==oracle):** crosscheck patterns 13→15 (050 alt_two, 051 alt_three), mode-3 ladder 93→95, ZERO
  regressions (8 green rungs full; capture/strings/keywords unchanged; m4 spot-checked on the green rungs).
  **053 alt_commit still fails** — it is `P = ('a'|'b'|'c'); X P`, a STORED-pattern reference (`X P`), i.e.
  DEFER/stored-pattern territory (a later rung), NOT pure ALT. NOT YET regenerated: the ALT `.s` feature
  artifacts (handoff step 4 owes another `util_regen_feature_s_artifacts.sh` run — codegen changed again).
- [x] **SN4-PAT-3i FENCE** — LANDED 2026-07-05 (Claude Sonnet 5). Bare `FENCE` and the `FENCE(P)`
  atomic-group form now lower in the single-HEAD model. FINDING THAT SHAPED IT: every deterministic
  matcher fails straight to `head` (the retry-at-next-anchor box; ω=`fJ`) — there is no left-to-right
  backtrack chain among deterministic elements — so FENCE cannot be a `β→ω` box (a later element's
  failure never reaches it). FENCE is instead node-free (the landed-CAT precedent, zero new IR/template/
  Makefile touch) and works as a **fail-retarget**: in a pattern sequence, a fence SEALS — every element
  to its right fails to the statement-level `cx->pat_fail` (=`fJ`, new `scx_t` field) instead of `head`,
  cutting off both anchor-retry and left-generator resume, exactly the manual's semantics (forward = null
  match, no effect; backtrack into it = whole match fails). `FENCE(P)` additionally lowers `P` with the
  pre-seal fail (so `P` retries normally on forward-fail) — the seal only blocks re-entry after `P`
  succeeds. `lower_snobol4.c` only (+59/-15): `sno_is_fence`/`sno_seq_has_fence` helpers; `TT_FENCE` +
  `TT_VAR "FENCE"` leaf arms; `TT_SEQ` flattens the left-assoc spine and retargets per-element fail past
  the first fence (fence-free sequences keep the untouched 2-way CAT path byte-for-byte); `sno_pat_supported`
  child-aware for `FENCE(P)`. VERIFIED vs SPITBOL x64 oracle: 058/059/060/067/069/100-104/107 all m3==oracle
  (one bug caught+fixed pre-measurement: standalone `FENCE(P)` was matching null and dropping `P`). Crosscheck
  both modes 154→168 (+14), DIVERGE=0, mode-4 FAIL back to the 3 parked (082/099/213); non-pattern FAIL set
  byte-identical to baseline (zero regressions); patterns 15→29; Icon smoke 12/12×2. Artifact regen
  (feature/benchmark/demo) = 0 changed — fence tests live in the crosscheck corpus, compiled on-the-fly,
  no committed `.s`. Remaining pattern fails are ARBNO, `*VAR` deferred-eval, and pattern-as-value/via-var
  (105/106 need the last one) — FENCE was never scoped to cover them.
  **NEXT: ARBNO, then ABORT/BAL, then ASSIGN_IMM (`$`)/DEFER — pattern-as-value (STITCH) is the other
  large lever whenever Lon wants that path instead.**
- [ ] **SN4-PAT-FOLD** — re-seat freeze+blob: `sno_freeze_pat_graph_entry` + the stored-pattern driver are IN
  the RECOVERED parent lower file (directive below); the blob-SEAL side (`xa_pattern_blobs.cpp`) is already
  LIVE in the Makefile; `bb_pat_build.cpp` parked; `src/include/dtp.h` (DTP_PROTO_DESC / DTP_FRAG_t,
  first-class β) on disk. `rt_pattern_stitch_*`/`rt_pattern_build` were superseded pre-parent — do NOT
  resurrect; port the freeze path, not the stitch path.

**⛔⛔ STANDING DIRECTIVE (Lon, restated 2026-07-04) — PARK, NEVER DELETE, parked-language code.**
Park out of the Makefile (the `8f3e4b23` "kept intact on disk" precedent); deletion of parked code is a
directive violation even inside a "reset" commit. **The violation on record:** GZ#5 followed the rule for the
118 templates but DELETED the SNOBOL4 pattern lower wholesale — the parent's `lower_snobol4.c` (1402 lines:
`lower_pat_node`, `sno_freeze_pat_graph_entry`, the match-statement driver, the generator-kind classifier)
was replaced by the 451-line non-pattern rebuild with no on-disk copy kept. **RECOVERED this session** to
`src/lower/lower_snobol4.gz5-parked-41b53078.c` (parked, NOT in the Makefile; build unaffected, verified
green). Emit-side needed no recovery: at the parent, matchers had no per-op dispatch caller (generic
`bb_build_flat` blob path only) — today's arms are written fresh in `emit.cpp`, one line per kind
(SN4-PAT-1's `IR_MATCH_LEN` is the precedent). **Any dead-code sweep (incl. GOAL-DEAD-CODE-SWEEP) must
exempt `*.gz5-parked-*` files and everything in the WIRING INVENTORY above.** SN4-PAT-2..N port FROM the
parked file INTO the live tree.

**WIRING INVENTORY (src scan 2026-07-04 — what exists on disk for re-wiring):**
- **Parser (live):** `src/parser/snobol4/` (`snobol4.l`/`.y` + generated) — full grammar incl. pattern syntax.
- **Lower:** `lower_snobol4.c`/`.h` (live, non-pattern subset complete; `:257` is the wall), `tree_to_sno.c`.
- **Runtime (live in build):** `pattern_match.c` (cset_resolve, `pat_*` atoms, `rt_cap_assign_cursor`,
  `rt_at_cursor`, `rt_defer_match`, `rt_assign_var`; `pat_cat`/`pat_alt` are B0 BOMBs — superseded by stitch),
  `pat_pool.c`, `by_name_dispatch.c`, `xa_pattern_blobs.cpp`, `src/include/dtp.h`.
- **Runtime (parked, not in Makefile):** `bb_pat_build.cpp` (mints `IR_MATCH_*` blob-builders; exempt per
  GOAL-SNOBOL4-BB session-31 note).
- **Templates on disk (kept intact by `8f3e4b23`, API-current per BB-FIXUP):** 23 `bb_match_*` (abort advance
  alt any arb arbno atp break breakx capture cat defer fence head len notany pos rem retry rtab span span_var
  tab — `len` re-wired SN4-PAT-1), 5 `bb_pattern_*` (break capture cat len lit — cat/capture are post-FZ-4
  passthroughs; `lit`/`len`/`break` are abandoned-era, audit before wiring) + `bb_pattern_stub.cpp`,
  `bb_keyword_snobol4.cpp`, `bb_scan_match.cpp`.
- **Dormant backends (X86-ONLY era):** JVM/`SnoPat.java`, .NET/`SnoRt_patterns.il`, JS/`sno_engine.js`,
  WASM/`sno_runtime.wat` — reference semantics only, not wiring targets.
- **Tools:** `src/tools/tmatch_proto.c` (matcher prototype harness).
- [ ] **SN4-PAT-DEFER** — `*EXPR` unevaluated + callback: `IR_MATCH_DEFER`/`IR_MATCH_CALLOUT` (needs the matcher
  to re-enter emitted code). The genuine hard edge; do last. EVAL/CODE stay out (runtime compilation).
## ⛔⛔ SCO-CF — SNOCONE CONTROL FLOW, DIRECT-LOWER PORT (Lon, 2026-07-04 session pivot; worked THIS session)
**THE RUNG NAME IS `SCO-CF`.** Snocone (.sc) + Rebus (.reb) ride the SNOBOL4 lower TODAY (driver scrip.c:531
`lower_entry_fn seg_fn = lower_sno_stage2` is the DEFAULT — no snocone/rebus case). The working control-flow
lower did NOT die in the GZ#5 gutting (`92903c94` removed patterns, already parked) — it died at `662f249a`
(2026-06-11, "old machinery DELETED — Lon ruling"): the v_* four-attribute walkers + lower_sno.c's explicit
TT→v_* dispatch. lower_snobol4.c's own Snocone arms were oracle-shape STUBS from birth (identical stub bodies
at initial import and in the gz5-parked 1402). **RECOVERED 2026-07-04** from `2f17bf4f` (SNO-ISO-1 — the
commit whose instrumented census ran sco 191 + rebus through this exact dispatch: IF×118 WHILE×12 ALT×10) to
three parked files, NOT in Makefile:
- `src/lower/lower.sco-parked-2f17bf4f.c` (683 ln — v_if/v_while/v_until/v_repeat/v_not/v_loop_break/
  v_loop_next/v_conj/v_alt/wire_if/wire_alt/wire_seq)
- `src/lower/lower_sno.sco-parked-2f17bf4f.c` (1095 ln — explicit TT→v_* dispatch, every arm)
- `src/lower/lower_internal.sco-parked-2f17bf4f.h` (89 ln)
**PORT RECIPE:** semantic reference = parked v_*; structural template = live lower_snobol4.c idioms
(lc_build/lc_γ_to edge-stamps, sJ/fJ statement GOTOs) — NOT a drop-in (mode-2-era: pre-sidecar-flattening,
IR_t* γ/ω, old IR_LIT_I names). tree_to_sno.c (661 ln) is ALIVE in the Makefile — the oracle bridge for .sc
is hand/mechanical transpile → `sbl`; corpus `.ref` files are the recorded oracle.
- [x] **SCO-CF-0 PARK** — recovered trio committed (this session). Build untouched (not in Makefile).
- [x] **SCO-CF-1 ROUTE+SHAPE** — pinned this session: (a) .sc routes snocone_compile → lower_sno_stage2
  (default fall-through, scrip.c:512-531); (b) **the Snocone PARSER already desugars relops** — `x > 5`
  arrives as `TT_FNC GT(x,5)`, the existing sx_call_named path — ZERO relop TT arms needed, the whole
  TT_EQ..TT_LLE family is free; (c) IF branches arrive as `TT_PROGRAM(TT_STMT(:subj …))` wrappers;
  (d) today's wall on `corpus/programs/snocone/corpus/sc4_control.sc` = sx_lower default fatal "tree kind
  47" = TT_ASSIGN-as-subject (Snocone emits TT_ASSIGN NODES; the SNOBOL4 walker only knows :eq-field
  assignment) with TT_IF immediately behind it.
- [x] **SCO-CF-2 ASSIGN+IF** — LANDED 2026-07-04. sx_lower gained `case TT_ASSIGN` (TT_VAR lhs subset;
  mirrors the walker's :eq arm: IR_ASSIGN sval=name, operand=rhs value, entry=rhs entry) + `case TT_IF`
  (cond γ→then-entry, ω→else-entry-or-γ [no-else = cond-fail falls through to statement success, SPITBOL
  shape]; branches via new `sco_branch` helper walking TT_PROGRAM's TT_STMT :subj list back-to-front, inner
  fail = fall to next inner stmt [SPITBOL default-continue]; inner-stmt gotos out of subset, unguarded).
  **ROOT-CAUSE FIX riding along (driver):** first .sc drive died at TMP-ERADICATE FATAL (IR_LIT_INTEGER
  tmp=-1) — NOT a lowering bug: scrip.c gates `ir_drive_slot_assign` on `is_icon || is_sno_bb`, and
  `saw_sno` matched only `.sno` — **Snocone/Rebus never received drive-slot grants at all** (any .sc value
  node would fatal). Fix: `.sc`/`.reb` join `saw_sno` (scrip.c:430) — they ride lower_sno_stage2, so they
  are sno-BB graphs; driver-side language conditioning is the legal zone per the LANG FACT RULE. gdb
  breakpoint at emit.cpp:822 bracketed it (compile-time abort — monitor N/A); SCRIP_OPT=0 A/B exonerated
  the optimizer. GATES GREEN: sc4_control.sc == .ref m3 AND m4 (byte-identical, both fail-paths + no-else
  exercised); snocone corpus **0/10 → 5/10** (sc1 literals/sc2 assign/sc3 arith/sc4 control/sc8 strings —
  the four non-IF passes were the same TT_ASSIGN wall); icon smoke 12/12×2; SNOBOL4 corpus m4 PASS=137
  FAIL=3 DIVERGE=0, FAIL set {082_keyword_stcount, 099_keyword_rw, 213_indirect_name} byte-identical to
  the 2835cce4 pre-session watermark. Remaining snocone walls: sc5/sc7/sc9/sc10 (WHILE + procedures →
  CF-3+), sc6 (FOR → CF-5).
- [x] **SCO-CF-3 WHILE/UNTIL + LOOP_BREAK/LOOP_NEXT** — LANDED 2026-07-04 (`a4883ba3`). One arm for
  TT_WHILE/TT_UNTIL: cond lowered with the EXIT edge pre-wired (while: ω=γ; until: γ=γ) and the BODY edge
  patched post-build via lc_γ_to/lc_ω_to on the cond value node (LOWER-side patch; emitter untouched);
  body = sco_branch with γ=cond-entry (loop-back); scx_t grew loop_exit/loop_next with save/restore
  (nested-safe). BREAK/NEXT → IR_GOTO to ctx target; labeled + outside-loop = loud fatal. Oracle-pinned
  vs sbl: sc5 ==.ref m3+m4; break/continue probe m3+m4; **UNTIL proven via .reb probe** m3+m4 (rebus
  `function main()` wrapper rode through existing machinery unmodified). **LEXER FACT (footgun):** snocone
  next-statement spelling is `continue` — `next` silently lexes as a plain IDENT→IR_VAR. Regressions: icon
  12/12×2; sno corpus DIVERGE=0, FAIL set {082,099,213} unchanged; snocone corpus **5/10 → 7/10**, and
  **sc6_for passed WITHOUT a TT_FOR arm — the snocone parser desugars FOR to while-form** (relop-desugar
  precedent confirmed; CF-5's FOR scope is dead). Remaining walls sc7/sc9/sc10 are ALL procedure-shaped:
  snocone `function` lexes T_DEFINE → a TT_DEFINE statement shape ≠ SNOBOL4's literal-DEFINE subset —
  needs its own rung (SCO-PROC) after CF-4/CF-6.
- [ ] **SCO-CF-4 NOT/INTERROGATE/NONNULL** — success-polarity unaries (parked lower.c:90 arm + v_not).
- [ ] **SCO-CF-5 DO_WHILE/CASE** — census-zero kinds (FOR struck 2026-07-04: parser-desugared, see CF-3);
  check parser desugar FIRST; tree_to_sno.c:428 has DO_WHILE goto-form semantics if an arm is needed.
- [ ] **SCO-CF-6 REBUS-WALLS** — .reb probe pinned; loud-fatal arms for never-implemented Rebus-only TTs
  (UNLESS/SWAP/ITERATE/RECORD_DECL/…) — "at least existed" parity → explicit walls (`:257` precedent).

## ✅ SCOPE UPDATE (Lon, 2026-07-04) — ICON-ONLY IS LIFTED; SNOBOL4 IS BACK IN SCOPE
**The two former "ICON ONLY" hard rules (file-scope + test-execution, both Lon 2026-06-30) are RETIRED.**
Their premise is now false: `lower_snobol4.c` was rebuilt onto the live post-GZ#5 spine — it compiles clean
(EXIT 0, warnings only) and references only live opcodes. The old warning that non-Icon lowers hold a
"wholesale-dead pre-GZ#5 IR vocabulary (`IR_SEQ`, `IR_PATTERN_*`, `IR_DTP_ASSIGN`, `IR_ALT`)" no longer
applies to SNOBOL4 (verified: grep = 0 in `lower_snobol4.c`).
- **In scope now:** everything Icon had, PLUS `src/lower/lower_snobol4.c`, the SNOBOL4-reachable templates
  (`src/templates/bb_match_*.cpp`, `bb_pattern_*.cpp`, `bb_pat_build.cpp`), `src/runtime/pattern_match.c`,
  `src/runtime/rt/pat_pool.c`, and the SNOBOL4 corpus/smoke. Icon work is unaffected and stays green.
- **Testing:** the SNOBOL4 smoke/corpus and the SPITBOL `x64` oracle (`/home/claude/x64/bin/sbl -b f.sno`)
  are now permitted and expected signals. Keep Icon green as a regression floor (additive-only changes to
  shared files — the enum re-add below is the model).
- **Raku/Prolog/Pascal remain PARKED** pending their own GZ#5 rebuilds — untouched, but no longer "forbidden
  to look at." Leave their inert enum refs alone.

## ⛔⛔ STANDING DIRECTIVE (Lon, 2026-06-28) — WHOLESALE JCON-IN-SCRIP, ICON-ONLY
We are doing a complete wholesale rewrite of the Icon LOWER + EMITTER to mirror JCON
(`refs/jcon-master/tran/`) construct-by-construct, because JCON has it CORRECT. Same IR as JCON's `ir.icn`
EXCEPT SCRIP keeps fine-grained `IR_BINOP`/`IR_UNOP` instead of one `ir_OpFunction`. **EVERYTHING ELSE IS
DEFERRED** (old TRACK A/B/C ladder, IRM numbering, the pre-pivot opcode-collapse plan) — go straight to the
JCON spine, one TT at a time, per the CONVERSION PLAYBOOK below.
- **`.s` byte-identity is NOT a gate, ever** (Lon, repeated 4×). The `.s` is the honest current output and
  will keep changing drastically. Never wire it into a gate.
- **No full regression required per rung.** Icon regression may go to zero and grow back; breaking other
  languages mid-ladder is authorized (they are already broken pending their own GZ#5 rebuild — not started).
- **No micro "baseline gate."** The old two-snippet sanity gate (`write("hello world")` + `write(1+1)`,
  both modes) is RETIRED (Lon, 2026-06-30) — it tested almost nothing and was never a script, only this line.
  The honest per-rung signal is `bash scripts/test_smoke_icon.sh` (12 programs, both modes) plus the corpus
  stash/rebuild/FAIL-set diff for the rung you touched; each TT is its own honest pass/fail — land it,
  document it precisely, move on. **Icon-only, full stop — see the ICON-ONLY TEST EXECUTION hard rule at the
  top of this file; do not run a non-Icon smoke to "double-check" anything.**
- **`IR_t.tmp` IS the temporary slot** (not `lhs`; no `IR_TMP` opcode — see CONVERSION PLAYBOOK). Only
  value-producers carry one (`ir_node_produces_value`); control/effect ops don't.

## ⛔⛔ IR-LAYOUT JCON-ALIGNMENT DIRECTIVE (Lon, 2026-07-02) — make Icon's IR match JCON's layout
**Principle (Lon verbatim-in-spirit):** match JCON's IR record set as closely as possible. THE ONE EXCEPTION is
`ir_Goto`/labels — SCRIP BBs carry the four ports INSIDE the box template, so instead of varying code output
with labels, SCRIP has varying `IR_*` opcodes that CLASSIFY each form BY NAME, one template each. SNOBOL4 was
done very differently; Icon shall be the JCON-faithful one. All BBs done = Icon at 100%.

**LANDED (`65f8c32e`):** `IR_FIELD`→`IR_FIELD_GET` · `IR_ENTER_INIT`→`IR_INITIAL` (mechanical, FAIL set byte-identical).

**DERIVED ANSWERS (fresh from refs/jcon-master/tran, 2026-07-02):**
- **while/until:** JCON emits PURE `ir_Goto` chunk wiring — `ir_Conj` does not exist ANYWHERE in JCON (0 hits
  in ir.icn/irgen.icn/gen_bc.icn). SCRIP's `IR_CONJ` is our MATERIALIZED Goto: the chain-BFS discards a
  sentinel's edges, so where JCON writes a bare Goto chunk, SCRIP needs a real node to carry the jump
  (while's exit sentinel W, repeat's header H, break/next). Same wiring, one SCRIP-ism justified by the
  ports-in-the-box exception.
- **to / to-by:** JCON has NO `ir_To` at all — `ir_a_ToBy` defaults `/p.byexpr := a_Intlit(1)` and always emits
  ONE `ir_opfn(operator("...",3))`. JCON collapses because its product is a generic opfn dispatch; per the
  classification principle SCRIP splits BY NAME instead.
- **subscript:** canonical subscript yields a VARIABLE (`oref.r` subsc/trapped vars) — lvalue AND rvalue
  through one node is CORRECT. Current `TT_IDX → lower_call("[]")` is the misfit.

**RUNG LADDER — CLOSED (all landed 2026-07-02):**
- TO-SPLIT (`7dd2baf7`): `IR_TO`/`IR_TO_BY` split, 2-op vs 3-op runtime-by; `IR_RESUME_VALUE` not needed.
- `IR_MAKE_LIST` (`138c64dc`): dedicated opcode retires by-name MAKELIST route for Icon.
- IDX-UNIFY phase 1 (`264c3994`): `x[i]` real lvalue — `IR_SUBSCRIPT`(2-op)/`IR_DEREF`/`IR_ASSIGN_VAR`; option-(ii) mini-trapped-var (`DT_V`+`VCELL_t`); corpus 194/59/36->200/53/36. Sub-rungs r1 tvsubs (`c76ce21d`), r2 subscript-revassign->`IR_REV_ASSIGN_VAR` (`fba88eae`), r3 `x[i,j]` comma form (`df46db00`), r4 `*t` table-size (stale — already correct) — ALL LANDED.
- CONJ-RENAME (`87ab07c4`->`46c1923a`): `IR_SEQ_EXPR`->`IR_CONJUNCTION`; `TT_CONJ`(`&`)/`TT_SEQ_EXPR`(`;`) share one case body, differ only in ω-wiring (lower_icon.c:298/321) — worth remembering before re-deriving this.
- RESERVED-SET RECONCILE — CLOSED: `IR_EXEC`/`IR_UNREACHABLE`/`IR_SCAN_SWAP`/`IR_MOVE`/`IR_RESUME_VALUE` all DELETED (dead or absorbed elsewhere); `IR_DEREF`/`IR_MAKE_LIST` implemented. `IR_OP_COUNT` is the sentinel, not an opcode — never delete it.
Full commit-by-commit detail: `git log`.

## ⛔⛔ TMP-ERADICATE (Lon directive, 2026-07-02) — the emitter does NOTHING for temporary allocation
**Lon verbatim-in-spirit: "We want not having emitter doing anything for temporary variable allocation
scheme."** The emit-time bump allocator is emitter-side state that makes the graph incomplete at
construction — the same defect the α/β edge-stamp fixed for edges — and the two-counters-over-one-offset-
space design is the documented root of the slot-collision bug family (`a0b3f410`, `024abd2f`, `d225d4a2`,
IR_LIMIT/IR_REPALT grant comments). End state: LOWER owns the ENTIRE ζ-frame layout; `drive_value_slot`
degenerates to a read of `nd->tmp`.

**STATUS — COMPLETE (2026-07-02, `d671e68f` + `ad613052`):** old allocators (`bb_slot_alloc16`, `bb_slot_claim`, `bb_flat_cursor_reserve`, the varslot cursor) all DELETED — gated by `scripts/test_gate_emit_no_slot_alloc.sh` (keepers: `bb_slot_get`/`bb_slot_register`, the node->offset memo, not allocators). `ir_drive_slot_assign` is now the ONLY slot source — grants: call family `k+=1+n_operands` (argv at tmp+16), `IR_DEREF`/`IR_ASSIGN_VAR`/`IR_KEYWORD` `k+=1`, `IR_CREATE` `k+=4`. Params/locals/gen-proc resume-cell intern into `graph->vslots`; `bb_varslot_peek` is a pure read. `ir_tmp_slot_assign` (not `_flat`) survives as a live parked-language dump arm (scrip.c:638) — do not delete without checking that call site.
## ⛔ FACT RULE — THE EMITTER NEVER MUTATES AN IR NODE
The emitter (`src/emitter/**`) dispatches on `nd->op` and reads `nd`'s fields. It does **NOT** write
`nd->op`, does **NOT** write `IR_LIT(nd).*`/`IR_EXEC(nd).*` on an input node, does **NOT** synthesize IR
nodes, and does **NOT** consult `rt_*` to decide IR shape. Every specialization decision is made in LOWER
(per-language) and baked into the IR shape the emitter receives.
**GATE:** `scripts/test_gate_emit_no_ir_mutation.sh` — `[-]>op[[:space:]]*=` (op-writes) + `IR_LIT(...).x =`
on an input node (field-writes) == 0. **CLOSED FOR GOOD (Lon directive 2026-07-02, SCRIP `545c3857`): HARD=0,
gate PASS — the last four op-writes (`resolve_call_kinds_descr`, emit-time call-kind retag from rt_* queries
+ a dead `if(NULL)` dval-tag tail) DELETED from the emitter and moved to LOWER as
`lower_icon_resolve_call_kinds` (proc truth from `g_stage2.proc_table`, builtin truth from the static
by_name_dispatch.c lists; ladder verbatim; byte-identical `.s` proves the move pure). Any future op-write or
field-write in `src/emitter/` is a regression against a green gate, not a baseline.**

## ⛔ DIVISION RULE (Lon, 2026-06-27) — RESUMABILITY IS ω-WIRING, NOT A STORED FLAG
"Generator vs coercive vs plain" is not three operators — it's the OPERATION (an immediate on one node) plus
**resumability, which costs ZERO template logic**: a resumable node is reached by routing a consumer's
backtrack edge AT the producer node; the chain-BFS (`codegen_flat_chain_body`) resolves that edge to the
producer's **β** (not its α) whenever `ir_is_generator_kind(producer)` and the consumer sits later in chain
order. **PROVEN (B3, 2026-06-27):** live four-port chains correctly enumerate `(1 to 3)+10`→`11 12 13` and
Cartesian `(1 to 3)+(1 to 2)`→`2 3 3 4 4 5` with **zero dedicated generator-tree walker** — `bb_conj`'s entire
body is `x86_pair_loop()` (pure in-band β-define + γ/ω jumps from the DRIVE_PAIR table). Never store a
generator/resumable flag on the node (`dval=1.0` tags are the violation pattern — remove on sight).

## DO NOT
- Re-introduce ANY `->op =` write in `src/emitter/**`.
- Decide a call kind from `rt_*` runtime state at emit time — proc/builtin tables are compile-time.
- Encode operand-source in an IR opcode — operand-source lives on the OPERAND node (a producer box).
- Add a per-language function to the emitter/templates — language lives in parser + LOWER only.
- Build a separate "generator" opcode/template family — see DIVISION RULE; it's ω-wiring, not a template.

## ⛔⛔ CONVERSION PLAYBOOK — JCON → SCRIP, ONE TT AT A TIME (Claude Sonnet 4.6, 2026-06-30)
**The mechanical recipe for converting any Icon construct from JCON into LOWER + the EMITTER DRIVER +
TEMPLATES. Read once; each TT is then fill-in-the-blanks. This is the head-start for the SNOBOL4/Snocone/
Rebus/Prolog/Pascal sessions doing the same to their own lowers later.**

### THE CENTRAL ISOMORPHISM — 4 JCON labels ⇄ (2 node positions + 2 IR_ref_t edges)
JCON's `ir_info(start, resume, failure, success)` (`irgen.icn` `ir_init`) ⇄ SCRIP's `IR_t.γ`/`IR_t.ω`
(`src/contracts/IR.h`):

| JCON label | SCRIP realization | Set/read by |
|---|---|---|
| `p.ir.start`   | the node's own **α position** in the flat chain | a predecessor's γ/ω points here |
| `p.ir.resume`  | the node's own **β position** | BFS routes a consumer's edge here iff `ir_is_generator_kind` |
| `p.ir.success` | `nd->γ.node` | LOWER: `γ_to(nd, target)` |
| `p.ir.failure` | `nd->ω.node` | LOWER: `ω_to(nd, target)` |

`start`/`resume` are **not stored** — they're positions the BFS discovers from edges pointing AT the node.
You never "set start/resume"; you set OTHER nodes' γ/ω to point here, and the generator-kind check picks
α-vs-β. This is why JCON's four labeled chunks collapse to two edges. `p.ir.x` (loopinfo/scaninfo) has no
struct field — it's carried in `icx_t` (`cx->loop_exit`, `cx->loop_next`, `cx->beta`) during lowering.
JCON's `ir_tmploc`/`ir_MoveLabel`/`ir_IndirectGoto` (unbounded-resume "label variable") usually maps to
**plain β-wiring** — wire ω at the right node and delete the indirection.

**⚙ IR_ref_t CARRIES ITS OWN α/β PORT IN `.sz` — LOWER STAMPS IT, EMITTER READS IT (LANDED 2026-06-30, `bb70a841`).**
`IR_ref_t` = `{IR_t* node; char sz[4];}`. The `sz` field is the **α/β discriminant of the edge**, written by
LOWER at construction and read by the emitter — NOT recomputed downstream. The rule LOWER applies: an edge whose
TARGET is `ir_is_generator_kind` is a RESUME edge → stamp `"β"` (`lc_γ_to_β`/`lc_ω_to_β`); every other edge →
`"α"` (`lc_γ_to`/`lc_ω_to`). The Icon `γ_to`/`ω_to`/`build` wrappers (`lower_icon.c`) do this automatically by
checking `ir_is_generator_kind(target)`. The emitter (`emit.cpp` chain-BFS) reads the stamp:
`node_γ = (γ.sz=="β") ? betas[k] : lbls[k]` (UTF-8 `β` = `CE B2`). **PROVEN equivalent to the old positional
`i > k && ir_is_generator_kind` guess:** with the positional fallback DELETED (pure-stamp routing), icon smoke
stays 11/12 and the full corpus stays 82/289 — zero divergence. The fallback is RETAINED for now only to protect
un-stamped edges during the ongoing GZ#5 rollout; the end state deletes it. **WHY THIS MATTERS (Lon, 2026-06-30):**
the graph must be CORRECT AT CONSTRUCTION — an edge has to say whether it means "enter fresh (α)" or "resume (β)"
or no optimization pass can even know what an edge *means*. Recomputing α/β positionally in the emitter made the
graph incomplete; stamping it on the ref makes the graph self-describing, which is the precondition for sound
optimization. **The remaining un-stamped resume sites** (SEQ/CONJ backtrack chaining `ω_to(val[i],val[lr])`,
`cx->loop_next` loop-backs, `lβ`/`mβ` operand resumes) currently rely on the positional fallback; stamping them
explicitly (so the fallback can be deleted) is the follow-up rung. **NOTE:** a stamp names ONE static target; a DATA-dependent resume (whichever arm last fired) is the label variable — LANDED `dc45d9e2` (`IR_MOVE_LABEL` + `IR_INDIRECT_GOTO`; see Watermark).

### lhs ⇄ tmp
JCON's `lhs`→`ir_Tmp` node ⇄ SCRIP's `int IR_t.tmp` FIELD on the producing node (one node = one value = one
slot — why the `IR_TMP` opcode is dead). LOWER assigns it; `drive_value_slot()` (`emit.cpp`) reads `nd->tmp`
first, falls back to legacy slot-alloc only for unconverted nodes. A consumer reads an operand's value via
`operand->tmp` (see `IR_CALL`'s arm: `a->tmp`).

### THE FOUR CONVERSION SHAPES (classify the JCON `ir_a_X`'s `ir_chunk` list)
1. **Pure edge-threading** (only `ir_Goto` chunks) → LOWER wires γ/ω among sub-exprs; **no opcode, no
   template, no driver case.** Landed: `TT_IF` (`lower_if`, JCON `ir_a_If`). Also this shape: `ir_a_Compound`,
   `ir_a_NoOp`, `ir_conjunction` (→ `IR_CONJ`/`bb_conj`, whose template is pure pair-table threading — the
   zero-template limit case of this shape).
2. **Value-producer + runtime call** (`ir_opfn`/`ir_Call`/lits) → ONE `IR_*` node, operand `tmp`s pushed, the
   TEMPLATE marshals slots into args and `call`s an `rt_*` helper (value work NEVER reimplemented inline —
   that's DUP FORM 1/2 in GOAL-ICON-BB.md). Operation rides as an immediate, not opcode identity. Landed:
   literals, `IR_VAR`, `IR_BINOP`/`_RELOP`, `IR_UNOP`, `IR_CALL*`, `IR_KEYWORD`, `IR_RETURN`.
3. **Resumable generator** (success loops back via resume) → per the DIVISION RULE, make the node
   `ir_is_generator_kind` and point the consumer's backtrack edge at it; the BFS does the rest. Landed:
   `IR_TO` (`bb_to.cpp`). Also landed: `TT_EVERY`, `IR_REPALT`, `IR_LIMIT`, `IR_ITERATE`.
4. **Control/effect** (`ir_Succeed`/`ir_Fail`/`ir_Assign`) → `IR_SUCCEED`/`IR_FAIL`/`IR_ASSIGN`, no tmp.
   JCON's `ir_Move` (copy closure result into target) is usually absorbed — the producer writes its own tmp.

### THE LOOP-BACK & UNCONDITIONAL-JUMP IDIOM (loops, break, next, goto — Claude Sonnet 4.6, 2026-06-30)
**THE TRAP (cost an entire prior session a "diagnosed, not fixed" entry):** an `IR_FAIL` or `IR_SUCCEED` node is
NOT a general "jump-to-my-γ-target" node — it is a CHAIN TERMINATOR. The chain-BFS (`codegen_flat_chain_body`,
`emit.cpp`) does two things that discard a sentinel's edges: (i) it *threads through / skips* `IR_SUCCEED` and
`IR_FAIL` nodes (they're never added to `nodes[]`, lines ~950/955/970), and (ii) when ANOTHER node's γ (or ω)
points AT a sentinel, it resolves that edge to the **chain's** `lbl_γ`/`lbl_ω` exit (lines ~1001-1002:
`γ.node->op == IR_FAIL → node_γ = &lbl_ω`; `== IR_SUCCEED → &lbl_γ`). So a sentinel's *own* γ-target (e.g. the
post-loop continuation you wired into a `break`) is **silently thrown away** — control goes to the enclosing
chain's exit, not your target. This is why `repeat`-via-`IR_FAIL`-loopback ran the body once then left, and why
`break`-as-`IR_FAIL` skipped its post-loop code.

**THE FIX — to jump unconditionally to an arbitrary real target T (and have T's subgraph emitted), use an
`IR_CONJ` node with γ=ω=T, never a sentinel.** `IR_CONJ`'s driver (`emit.cpp` ~line 910) is pure
`DRIVE_PAIR_JMP(lbl_γ)` + `DRIVE_PAIR_DEF_JMP(lbl_β,lbl_ω)` — i.e. "jump to my γ-target," nothing else — and
`IR_CONJ` IS a real chain node, so (a) it is added to `nodes[]`, (b) the BFS *follows* its γ edge (queuing T and
everything reachable from T), and (c) an edge pointing at the `IR_CONJ` resolves to the `IR_CONJ`'s own α label —
a real `jmp`, forward or backward. `IR_CONJ` carries no value and needs no tmp; pushing its jump-target as
operand[0] (as `lower_repeat` does) keeps slot-registration uniform with the value-producing CONJ used for `;`.

**APPLYING IT — the loop family (JCON `ir_a_Repeat`/`ir_a_While`/`ir_a_Until`, decoded to 2-edge form):**
- `while C do B`: sentinel `W=IR_FAIL` with `ω→γ_post`; `C.success→B.start`, `C.failure→W`(=exit),
  `B.success→C.start`, `B.failure→C.start`. (Works because a `while` *does* exit via C's failure — the
  `IR_FAIL` exit semantics align. **Do not "fix" `while`'s `IR_FAIL` — it is the genuine loop exit.**)
- `until C do B`: mirror — `C.success→W`(=exit), `C.failure→B.start`, body loops to `C.start`.
- `repeat B`: **no condition, no failure exit.** Header `H=IR_CONJ`, `γ=ω→B.start`; body lowered with
  `γ=ω→H` (both body success AND body failure loop back); construct entry = `H`; `cx->beta=γ_post`. The loop
  leaves ONLY via `break`/`return`/`fail`. (JCON: `expr.success→ir.start`, `expr.failure→ir.start`,
  `ir.start→expr.start`; the `ir.start` Goto collapses into `H`.)
- `break` (JCON `ir_a_Break`: `expr.success→curloop.success`, `expr.failure→curloop.failure`): jump to
  `cx->loop_exit` (the loop construct's γ = its post-loop continuation) via `IR_CONJ`, γ=ω=`loop_exit`.
- `next` (JCON `ir_a_Next`: `Goto curloop.nextlabel`): jump to `cx->loop_next` (the loop header) via `IR_CONJ`.
  For `repeat`, `cx->loop_next = H`; for `while`/`until`, set it to the condition entry so `next` re-tests.
- **`cx->loop_exit`/`cx->loop_next` save/restore is MANDATORY** around the body lower (nested loops) — already
  done by all three; copy the pattern.

### EXPORTABLE WIRING RULES (proven across LIMIT/REPALT/ALT/IF — apply to every future junction construct, any language)
- **Edge ROLE beats target KIND.** `build()`/`γ_to` auto-stamp β whenever the TARGET is generator-kind — trustworthy ONLY for backtrack edges. A producer's SUCCESS edge into a generator-kind junction (LIMIT gate, REPALT, …) is α (enter fresh); LOWER must α-restamp it (`lc_γ_to`). Enforced at 7 sites: statement spine (guarded — `every` re-aims its own γ), TT_REPALT's γ, TT_LIMIT count→entry, TT_SEQ/SEQ_EXPR, and (2026-07-02, `b3d41c74`) the loop family's body entries — lower_while C.γ→B, lower_until C.ω→B, lower_repeat H→B.
- **A synthesized `*res` junction's γ is the construct's PUBLIC success label.** Wire-later callers re-point only `*res` — internal success paths (each arm's ml) must resolve through the junction's γ at EMIT time (a READ of the finished graph, never a write).

### THE 3-FILE EDIT RECIPE (shapes 2 & 3; shape 1 is LOWER-only)
- **(a) LOWER** (`src/lower/lower_icon.c`): build the node (`build(cx,IR_X,γ,ω)`); recurse sub-exprs
  capturing `*res` + `cx->beta`; wire γ/ω per the JCON chunk list (`γ_to`/`ω_to`); push operands
  (`ir_operand_push`/`bb_operand_aux_set`); set `cx->beta` to this node if it's the resumable thing the
  consumer should target. Return the entry node; set `*res` to the value node.
- **(b) DRIVER** (`src/emitter/emit.cpp`, `emit_drive`): add `case IR_X:` — read operand slots
  (`bb_child0/1`, `ir_call_arg(nd,i)`, `→tmp`), set `g_emit.op_*`, set DRIVE_PAIR if the box jumps via the
  pair loop, `DRIVE_FILL(nd, lbl_γ, lbl_ω, lbl_β)`. **Read-only — never write `nd->op`/`IR_LIT(nd).field`.**
- **(c) TEMPLATE**: `case IR_X: bb_emit_x86(bb_x()); return 0;` in `walk_bb_node`; create
  `src/templates/bb_x.cpp` (`x86(...)` only, both BINARY+TEXT via the same calls); add to Makefile + gate
  scans. Mirror an existing same-shape template (generator→`bb_to.cpp`; pure-thread→`bb_conj.cpp`).
- **(d) BFS REACH:** confirm `codegen_flat_chain_body`'s queue-feeding follows the node's ω where needed
  (generator exhaust, relop fail) — **the single most common silent bug** (sank `until` until `59dafbc0`).
- **(e) VERIFY both modes, then commit:** `SCRIP_ICN_BB=1 ./scrip --run` AND `./scrip --compile` →
  `gcc -no-pie -x assembler X.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out` → run. Mutation gate ≤ baseline. If
  a generator diverges/hangs: **MONITOR-FIRST** (RULES.md) — bracket with the monitor, then gdb
  breakpoint-hit-count to the land mine. Do not guess.

### CANONICAL SOURCE PAIRING
Port topology ← `refs/jcon-master/tran/irgen.icn` `ir_a_X` (the `suspend ir_chunk` list IS the γ/ω wiring).
Emission ← `refs/jcon-master/tran/gen_bc.icn` `bc_gen_ir_Y` for each `ir_Y` in the chunk (JVM bytecode → x86
by analogy). Value semantics ← `refs/icon-master/src/runtime/*.r` (`oarith.r`/`ocomp.r`/`ocat.r`/`oasgn.r`/
`fscan.r`/`fstranl.r`/`invoke.r`). The m2 oracle is a transcription, not truth.

### ⚠ FILE-LAYOUT NOTE (2026-06-30 consolidation — several older docs/PLAN.md are stale on this)
`src/emitter/{emit_bb.c, emit_core.c, emit_drive.c, BB_templates/, XA_templates/, bb_regs.h}` **no longer
exist.** Current: `src/emitter/emit.cpp` + `emit.h` (the ONE driver, `emit_drive`, + dispatch) + `emit_io.c`
+ `emit_str.cpp` + `sil_macros.h`; templates flattened to `src/templates/*.cpp` (161 files, no subdirs). The
register contract is hardcoded as `"r12"`/`"r13"` string literals in templates — no macro header. Use these
paths; ignore any doc still citing the old ones (this file now does, throughout).

## ⛔ TT_* COVERAGE PUNCH LIST (Icon ladder — climb this, not an opcode ladder)
**Ground truth = `bash scripts/audit_jcon_wholesale.sh` — run it fresh; never trust this prose (TECHNIQUE Step 4).** Snapshot 2026-07-01: **64/66 both modes.**

**✅ COVERED (audit-verified OK):** literals I/R/S/CSET · ident/global/invocable · `initial` (once-per-DEPTH caveat below) · binop arith/divmod/relop/concat · unop −/+/*x/\x//x (IR_UNOP + IR_UNOP_TEST) · `not` (via `&null` IR_VAR; IR_NOT deleted) · assign/augop/swap · **if** — statement AND value-context, then+else (value convergence via the ig shared cell, JCON `ir_a_If` :583-610, landed 2026-07-01) · while/until/repeat/break/next · every (postfix, assign, assign+body, noassign-after) · to / to-by · alternation bounded + unbounded (label variable) · repalt · limit · compound · call (builtin/arglist/params/recurse/mutual) · proc fail/suspend/return · list-ctor / `|||` lconcat · record field · section `s[i:j]` + string subscript · scan (move/tab-upto/many/match/cset-arg) · create / `@` activate / exhaust · seq-expr · `&line` / `&pos`-in-scan · case + case-default.

**Landed since baseline (commits in `git log`):** `22_revassign`, `54_section_plus`, `bb_operand_aux_set/get` deletion + `IR_RASGN->IR_REV_ASSIGN`/`IR_SECTION->IR_SUBSCRIPT` renames, corpus rung03 varslot collision, `TT_CSET_COMPL`, loop-family PRODUCE-edge alpha-restamps, unary-test-op else-routing, THE CLOBBER PATTERN audit (2 live bugs), dead r10 preamble courier, `SCRIP_OPT` optimizer defer-protect.

**🟡 OPEN:**
- coexpr unary prefixes `.e`/`^e` absent from `parse_unary`.
- `IR_SCAN_TAB` absent from `ir_is_generator_kind` — reverses-on-resume contract (canonical `tabmat`) unverified.
- Computed-cset scan operands (`s ? upto(~x)`) hit the literal-only `bb_scan_upto` BOMB — blocked on the scan rung, not the operator.
- `TT_RANDOM` (`?e`) + dead `TT_INTERROGATE` — unresolved silent no-ops, deliberately unreclassified.

**⚠ STANDING AUDIT TARGETS:**
- **INLINE-ARITH POINTER HOLE (live bug, unresolved):** `bb_binop_arith`'s int fast path guards only `!=DT_DATA` — a runtime string/dynamic-real operand falls into the inline int arm and computes on pointer/double bits (`x:="3"; write(x+2)` -> 58996226, both modes; relops "pass" by pointer-compare). Canonical semantics already pinned in the deferred CVA section. Fix architecture TBD by Lon (CVA convert-box, or a minimal DT_I-only fast-path guard).
- **x86() silent-drop:** the dispatcher returns EMPTY for an unrecognized arg shape instead of erroring — has silently hidden missing template arms before. A default-bomb retrofit at 147-template scale is its own gated rung.
- `initial` is once-per-DEPTH not once-per-procedure (static `g_rt_frames[depth]`) — canonical once-ever needs writable static storage; own rung (GVA `.bss` arena is the candidate).
## ⛔⛔ MECHANICAL JCON→SCRIP CONVERSION TECHNIQUE (Claude Sonnet 4.6, 2026-06-30) — read before starting any new TT
**This is the by-eye/by-hand recipe used this session, written up so the next session (Icon or, later, any
other language doing the same JCON-mirroring exercise) doesn't have to re-derive it.** It is a refinement of
the CONVERSION PLAYBOOK above with the actual workflow steps that playbook assumes but doesn't spell out.

### Step 0 — find the JCON procedure, read it as a literal wiring diagram
`refs/jcon-master/tran/irgen.icn` has one `ir_a_X` procedure per AST node kind (`grep '^procedure ir_a_'`
gives the full list — **43** of them, one-to-one with JCON's `a_X` AST records; **the "47" this line previously claimed is WRONG — fresh `grep -c '^procedure ir_a_' refs/jcon-master/tran/irgen.icn` = 43, re-verified 2026-07-01**). Each is a `suspend
ir_chunk(LABEL, [INSN, INSN, ...])` sequence. Read it as exactly what it says: a chunk named `p.ir.start` (or
`.resume`/`.success`/`.failure`) containing a list of instructions ending in a `ir_Goto`/`ir_IndirectGoto` to
another chunk's label. **Draw the graph on paper or in your head before writing any C** — nodes = chunks,
edges = the Goto targets. This graph IS the lowering; everything downstream is mechanical translation of it.

### Step 1 — classify by the FOUR CONVERSION SHAPES (already in the playbook above)
Count how many `ir_opfn`/`ir_Call`/value-instructions appear outside pure `ir_Goto` threading. Zero ⇒ shape 1
(pure edge-threading, LOWER-only, no opcode/template). One ⇒ shape 2 or 4 depending on whether a value is
produced (`lhs`/`target` set) or not. A success-chunk that loops back to a `.start`/`.resume` ⇒ shape 3
(resumable generator) — **check this FIRST**, because shape-3 constructs disguise themselves as shape 1 if you
only look at instruction count; the tell is a `Goto` whose target is upstream of the current chunk in the
threading order (a back-edge), not just any `Goto`.

### Step 2 — find the `bounded`/`unbounded` fork, if any
Many `ir_a_X` procedures branch on `/bounded` (Icon: `if bounded is null then ... else ...`). **This single
flag is the entire difference between "this construct needs a label variable" and "this construct doesn't."**
`ir_a_Alt`/`ir_a_RepAlt`/`ir_a_ListConstructor` all do this — the unbounded arm allocates `t := ir_tmploc(...)`
and emits `ir_MoveLabel`/`ir_IndirectGoto`; the bounded arm never does. **Do not implement both arms in one
pass.** Land the bounded arm first (it is always simpler and is what 90% of real call-sites exercise — `write(x)`,
`if`, a plain consumer), prove it, commit it, THEN come back for the unbounded/label-variable arm as its own
rung. This is exactly why `TT_ALTERNATE`'s bounded case (`write(1|2)`) is done and its unbounded case
(`every write(1|2|3)`) is correctly deferred — don't fuse them.

### Step 3 — runtime semantics: which `.r` file, and what to actually extract
`refs/icon-master/src/runtime/*.r` is C, not Icon — it's the OPERATIONAL ground truth for what a value
operation actually computes (overflow rules, type coercion order, fail conditions), which JCON's `irgen.icn`
deliberately doesn't encode (JCON just emits a generic `ir_opfn`/`ir_Call` and defers semantics to its own
runtime, exactly as SCRIP's templates defer to `rt_*` helpers — **never reimplement value semantics inline in
a template; call/mirror the existing `rt_*` helper, or if none exists, the `.r` file tells you what that
helper needs to do**). The useful extraction from a `.r` file is almost never the whole function — it's the
ONE structural fact that disambiguates an implementation choice: this session's two uses were (a) `oasgn.r`'s
`GeneralAsgn` `default:` arm showing assignment is type-uniform once the destination's *address* is resolved
(`Asgn(x,y)` = `*VarLoc(dest)+Offset(dest) = src`, no type-casing at the store), which told us the global-vs-
local distinction must live in ADDRESS RESOLUTION (a template/driver concern), not in assignment semantics
(never needs its own per-kind logic); (b) `rmacros.h`'s `VarLoc`/`Offset` macros confirming a Icon "variable"
descriptor is self-locating regardless of storage class, which is the running theory for why SCRIP's existing
`bb_var_global.cpp`/`bb_gvar_assign*.cpp` family (12 templates, pre-existing, NOT new) already has the right
shape — it just isn't reachable from the new flat-chain driver yet (see GVA-FLAT rung below). Match the genre
of fact you need (control-flow shape vs. value semantics vs. storage-class resolution) to the genre of source
(`irgen.icn` vs `gen_bc.icn` vs `*.r`) — don't read all three cover-to-cover for every TT; **read the chunk
list first, and reach for the `.r` file only when a *specific* implementation choice is actually ambiguous.**

### Step 4 — BEFORE writing LOWER code, grep the CURRENT SCRIP state for the TT
`grep -n "case TT_X:" src/lower/lower_icon.c` and `grep -n "case IR_X" src/emitter/emit.cpp` (note: TWO
`emit.cpp` switches exist — `walk_bb_node`'s TEMPLATE SELECTOR switch and `emit_drive`'s DRIVER switch; a TT
can be live in one and stubbed/missing in the other, which is exactly what the global-assign bug turned out to
be). **Do not assume the punch list's prose is the ground truth for what's broken — it can be stale, and was
this session** (see CORRECTIONS below). Always re-derive from a fresh `gdb` repro + the actual switch
statements before designing a fix. The RULES.md MONITOR-FIRST methodology (bracket via a real crash/gdb
trace, not by reading code and guessing) is not optional even for "obviously" missing cases — this session's
global-assign investigation found a SECOND, upstream, more severe bug (a universal segfault, not the
documented "abort") purely because the repro was run before the fix was designed, not after.

### Step 5 — the 3-FILE EDIT RECIPE (already in the playbook above) applies; ADD: check for PRE-EXISTING
**infrastructure under a different driver mode before writing a new template from scratch.** This session
found `bb_gvar_assign.cpp` (legacy `!g_descr_flat_chain` driver, fully built, untested-but-presumably-working)
and `bb_var_global.cpp` (the flat-chain-NATIVE read-side counterpart, already correctly shaped). The
write-side flat-chain-native template does NOT exist and should be a fresh file MIRRORING `bb_var_global.cpp`'s
shape (dual-path: `[rbx+gva_k*16]` fast path when slot-allocated, `NV_SET_fn(name, DESCR_t)` runtime-call
fallback otherwise) rather than either (a) trying to reuse `bb_gvar_assign.cpp` as-is (wrong shape — it expects
raw `op_a_node_kind` node-shape introspection, the OLD driver's idiom; the flat-chain driver instead
pre-resolves every operand to a `tmp`-backed slot via `IR_t.tmp`/`drive_value_slot`, so the new template should
consume `op_a_slot`, not re-derive the producer's shape) or (b) writing global-assign from a blank page (most of
the addressing logic — `RDQ("rbx", k*16)` vs `FRQ(slot)`, the `g_gva_active`/`op_gva_k` gating — already exists
correctly in sibling templates and should be copied, not reinvented).

## ⏸ CVA — CONVERT-FOR-ARITH LADDER — **DEFERRED (Lon directive, 2026-07-02, same day as opened): ON HOLD until known-type information exists in the system; to be revisited as the future typed/untyped + boxed/unboxed data-type enhancement ("I might be totally wrong about that one" — the optimization depends on type knowledge LOWER doesn't have yet). No CVA rung may be started without Lon re-opening this section. The ladder text is RETAINED below for that day; the EMPIRICAL TRIGGER's live bug stands INDEPENDENT of the deferral — promoted to STANDING AUDIT TARGETS.**
Original directive (2026-07-02) — hoist numeric coercion into its own BB; arith/relop boxes become pure inline int/real:
**THE EMPIRICAL TRIGGER (this session, m3+m4):** `x:="3"; write(x+2)` prints **58996226** — bb_binop_arith's int fast path guards ONLY `tag != DT_DATA` (je slow L(0)), so a runtime DT_S (or dynamic DT_R) operand falls into the inline integer arm and **adds the pointer/double bits**; `"2.5"+1` likewise; `"10">9` "passes" by pointer-compare (wrong mechanism). This ladder is therefore a **CORRECTNESS fix that keeps (and completes) the inline fast path**, not merely an optimization — though the benchmark payoff is the point.
**CANONICAL SEMANTICS (pinned fresh from refs/icon-master/src/runtime, 2026-07-02):** oarith.r per-op ladder = `cnv:(exact)C_integer(x)` → large-integer → `cnv:C_double(x)` → **runerr 102** ("3" exact-converts to int; "3.0" does NOT — falls to double); mixed operands promote to double. ocomp.r numcmp: numeric relops convert BOTH by the same ladder and **return the CONVERTED y** (string comparison is the separate `<<` lexcmp family — `<` on non-convertible is runerr 102, never lexcmp). cnv.r `ston` grammar: spaces, sign, digits, optional fraction/exponent, **radix `NNrDDD`**. Known SCRIP-side divergence candidates to pin (not silently change) in CVA-0: error-102/201 vs FAILDESCR idiom; radix support in the current coercer; no large integers.
**THE ARCHITECTURE (Lon's shape):** a CONVERT box normalizes each non-statically-numeric operand to {DT_I, DT_R} ONCE, so downstream arith/relop templates dispatch on a closed 2-tag set with zero RT calls in the numeric steady state; string parsing happens in ONE runtime fn on the cold path only. **NO-DUP resolution built in:** today inline-int-add (template) + rt_num_arith int-add (RT) is a pre-existing DUP FORM 1; the end state splits ownership — tag-dispatch + int/real machine ops = TEMPLATE (the sanctioned per-medium/per-op encodings of one logic); string→numeric parsing = `rt_cnv_num` ONLY. **Language-blind:** DESCR tags are the shared contract; no `IR_LANG_*` anywhere.
**2026-07-02 CONTINUATION SHAPE RECORDED (Lon + Claude Fable 5) — DEFERRAL REAFFIRMED same day (Lon: "We'll do major optimizations like this at the very end. Not a good idea to optimize too early in the development process.")** Lon's proposed shape: the CNV box tests for string; a string parses ONCE and fills TWO temp slots (int lane + real lane) handed to ADD/MUL/…; non-strings pass a single value and the arith BB finishes conversion fully inline. Analysis against the pinned semantics (live repro, fresh sandbox 2026-07-02: `x:="3"; write(x+2)` → SCRIP `679663410` both modes / icont oracle `5`; today's `coerce_numeric` (arithmetic.c:17) is digit-strings-only via strtoll — `"2.5"` never parses at all): (1) the non-string branch IS CVA-2/CVA-4 verbatim. (2) The runtime DESCR tag IS the type knowledge — correctness + the closed 2-tag inline fast path need ZERO static type info; the deferral's stated dependency (type knowledge LOWER doesn't have) applies only to the future unboxed-lane enhancement, so the shape could un-defer on correctness grounds alone whenever Lon re-opens. (3) ARROW FLIP required: derive the real lane FROM the exact int (one cvtsi2sd), never the int from the parsed double's mantissa — mantissa-int is exact only to 2^53 (silent wrongness across the 2^53..2^63 band: `"9007199254740993"`→…992) and strtod can't read radix `NNrDDD`, so the ston grammar dispatch must exist regardless and the exact-int arm is free (hardware `cvttsd2si` already IS mantissa extraction; the objection is the exactness envelope + radix, not mechanism). (4) The second slot is DEAD weight when tag=DT_R (mixed arith promotes, never demotes) and saves exactly one cvtsi2sd on the string-meets-real path when tag=DT_I; the arith tag dispatch SURVIVES either way (result type: `5` vs `5.0` print differently) — so the recommended end-shape remains ONE canonical 16-byte DESCR out of the CNV box (single operand contract, uniform with native operands); the two-slot variant is TE-doctrine-clean as a `k+=2` LOWER grant and belongs in CVA-BENCH as a measured variant, not a design default.
- [ ] **CVA-0 SEMANTICS PIN** — oracle-pinned probes BEFORE code (today's pointer-arith outputs are the floor): `"3"+2`=5 · `"2.5"+1`=3.5 · `"3"*"4"`=12 · exactness `"3.0"+0` real · relop converted-y `write("10">9)`→9, `write(3<"7.5")`→7.5 · div/mod-by-zero current-behavior pin · non-numeric `"abc"+1` (canonical errs 102) · radix `"16rff"+0`=255 (expected-divergence flag if the coercer lacks it).
- [ ] **CVA-1 `rt_cnv_num`** — ONE conversion fn (the ston ladder: exact-int else double else fail-marked), extracted so `rt_num_arith`/`coerce_numeric` DELEGATE to it — no second parser anywhere.
- [ ] **CVA-2 `IR_CNV_NUM` + `bb_cnv_num.cpp`** — classify-by-name, one template: inline tag test, DT_I/DT_R pass through (2×8 copy to own slot), else `call rt_cnv_num`; non-convertible → ω with the pinned error idiom. Emitted only where needed (CVA-3), so pass-through cost ≈ 2 movs + 1 predictable branch.
- [ ] **CVA-3 LOWER INSERTION** — arith/relop/numeric-unop operands get a CNV_NUM producer UNLESS statically numeric: IR_LIT_INTEGER/IR_LIT_REAL **or any producer that is itself numeric-closed (arith/unop-neg output ∈ {I,R})** — so `x*x + y*y` converts only at the leaf reads; interior chain nodes need nothing.
- [ ] **CVA-4 ARITH INLINE COMPLETE** — bb_binop_arith re-guarded on the post-CVA contract: both DT_I → existing inline int ops (zero-test inline for div/mod, current fail semantics preserved); mixed/real → inline cvtsi2sd promote + SSE addsd/subsd/mulsd/divsd result DT_R; DT_DATA → the existing rt_binop_overload arm; the `!=DT_DATA` pointer hole DEAD BY CONSTRUCTION. POW may stay RT. Delete/delegate RT's now-cold two-numeric arm (the NO-DUP payoff).
- [ ] **CVA-5 RELOP** — bb_binop_relop same 2-tag inline treatment + canonical converted-y yield (success result = converted operand[1] value); numeric-required semantics per ocomp.r (lexcmp stays `<<`-family only).
- [ ] **CVA-6 UNOP** — `-e`/`+e` ride the same converts; inline neg for DT_I (neg) / DT_R (xorpd sign-bit).
- [ ] **CVA-BENCH** — tight-loop probes (variable-operand int sum, real accumulate, string-fed leaf) timed m3+m4 before/after; numbers into the Watermark. THE POINT.
- [ ] **CVA-FENCE** — grep-gate: no template reaches rt_num_arith for a two-numeric case; rt_cnv_num is the only string→numeric parser; audit + corpus green with the CVA-0 probes as the new floor.

## ⛔ ICON-100% FAIL MAP — re-derive per rung, never trust this prose (ground truth: `test_icon_all_rungs.sh`)
**Last derived 2026-07-02, corpus 208/45/36.** ASSIGN-LV rung (generator-element + section-assign lvalues) fully LANDED (LV-1 section-assign `035106f9`, LV-2 iterate-lv `11d26284`, LV-3 augop rider `28d1e7e0`, LV-3a `?x` lv -> `IR_RANDOM`+canonical LCG `c634c79e`) — zero corpus flips, but unblocked table/substring/record/string past their guards into ordinary (open) divergence.
**Open, by first-fatal bucket:** CALL-SHAPE (computed/first-class-proc callee: `coerce`/`mathfunc`/`var`/`recogn`; builtin full-arity `match`/`move`; unimplemented `open`; operator-as-call `?` in args.icn) — likely one architecture rung. `bb_var: unhandled arm` (prepro, endetab, numeric). tvsubs `bb_var_ref` gap (queens). `bb_scan_tab` needs literal positive n (scan1). Clean-exit wrong/empty, no fatal captured (kwds, kross, parse, roman, lexcmp, meander, string1, genqueen) — per-program oracle diff is the instrument.

## ⛔ ICNBENCH — GET `corpus/benchmarks/icon` RUNNING END-TO-END (SCOREBOARD 2026-07-04: oracle 10/10 · m3 **8/10** · m4 **8/10** = concord + deal + ipxref + micsum + queens + **rsg** + **tgrlink** + version; SCRIP local `93f906ff` UNPUSHED, corpus local `710deb15` UNPUSHED, Claude Opus 4.8. Harness OK = rc=0 + non-empty stdout, NOT byte-fidelity. REMAINING 2: **geddump** runs rc=0 but empty stdout — `gedload` returns an empty `.ind` list (GEDCOM-parser runtime bug, its own rung; the `!` apply crash is FIXED); **micro** TIMEOUT — it is a `&time` timing benchmark (iconx itself takes ~15s, SCRIP exceeds the 30s wall), a perf/timing rung not a correctness fix. ⚠ RE-DERIVE with a fresh `bash scripts/test_icon_bench_corpus.sh` after pushing — never trust this line.\n\n**⌚ 2026-07-04 (Claude Opus 4.8) — bench 6/10→8/10 both modes; SCRIP `93f906ff` + corpus `710deb15`, BOTH LOCAL/UNPUSHED (credential pending).** Fresh rebuild first re-derived the real HEAD-`c19db9c6` scoreboard as 6/10 (concord/deal/ipxref/micsum/queens/version — the prose's "tgrlink passing / concord failing" was rebase drift; tgrlink was FAILING Error 5, concord newly passing). FOUR fixes, each oracle-pinned, ZERO corpus regression (289 stayed 215/38/36 FAIL-set-identical), smoke 12/12×2, audit 94/94 both modes, all 6 discipline gates PASS:\n(1) **binop keyword-right-operand α-restamp** (`lower_icon.c` ~254): the inter-operand success edge used `γ_to` (β-stamps a generator-kind target), so `IR_KEYWORD_ICON` as the RIGHT operand of any arith binop was resume-to-fail'd not entered fresh — `a / &pi`→null, LEFT operand worked. Changed to `lc_γ_to` (the TT_FNC arg-boundary α-force already did exactly this, line ~119). **[tgrlink]**\n(2) **`$define` textual preprocessor** (`icon_lex.c` `icn_preprocess`, hooked in `icn_lex_init` gated on a `$` scan): canonical JCON semantics — col-1 `$define name value`, definition-before-use expansion into later defs, whole-identifier substitution skipping strings/csets/`#`-comments, directive lines blanked to spaces to preserve line numbers. SEMICOLON PRISON still green (newline-blindness untouched). **[tgrlink/geddump/micro parse; unblocks SECTORS/DefaultTime/etc.]**\n(3) **statics-as-mangled-GVA-globals** (`lower_icon.c` `icn_statics_prepass` + wired into `lower_icon_proc`): `static x`→`PROC__STATIC__x` renamed through the proc body; `initial e`→`if /PROC__INITFLAG__N := 1 then e`; BOTH mangled names `global_register`'d so they classify global (GVA `[rbx+k*16]`, persistent) instead of degrading to a depth-shared frame slot. Kills the documented cross-proc `static`/`initial` contamination (post.icn `Time__`/`labels`). m3==m4==iconx on the A/T two-static-proc repro. **[rsg; hardens queens statics family]**\n(4) **`!` apply operator** (`TT_BANG_BINARY` `f ! L`): lowered in `lower_icon.c` to a synthetic `__apply__(callee,list)` by-name call (bare proc-name callee→string literal so `rt_call_value` dispatches by name; else value); `by_name_dispatch.c` `__apply__` arm unpacks the list and `rt_call_value`s the callee with spread elements. Reuses the ENTIRE call path — no new IR kind/template. m3==m4==iconx on `mk ! [3,4]` + `(mk ! [7,8]).x`. **[geddump: op=16 crash→runs]**\nALSO FOUND, NOT fixed (separate rung): `*b.items` (`*` size on a `.field`) is a PARSER precedence error (`expected ;`) — geddump itself doesn't hit it. HANDOFF: SCRIP+corpus committed LOCAL only; `handoff_status.sh` = WAITING until pushed.\n

**KEYWORD-GENERATORS + MAIN-ARGS LANDED 2026-07-03 (SCRIP `52916a86`) — 2/10→4/10 in BOTH modes (deal + ipxref now run end-to-end).** Two coupled fixes closed the concord/deal/ipxref/queens shared wall: (1) **ICNBENCH-2c** — `&features`/`&regions`/`&storage`/`&collections` are now resumable generators (post.icn's `every put(L,&kw)` drives them). Implementation is the ONE non-obvious rung here: a keyword generator has NO operand to serve as its α-entry (unlike IR_TO whose from-operand feeds α), so three things had to line up — IR_KEYWORD granted `k+=2` (counter at [tmp+16]); IR_KEYWORD added to `ir_is_generator_kind` (so operand-β resume edges reach it — safe for single-value keywords, their β=`jmp ω`=fail-on-resume=non-generator semantics, ZERO SNOBOL4 .s churn confirmed); and `lc_key` mints a **seed IR_GOTO entry wired to the keyword's α via `lc_γ_to`** (α ALWAYS runs → counter always inits, even when Regions__/Storage__/Collections__ are called the 2nd time from Term__ — the frame-zero-init-only version silently gave count=0 on the 2nd call). Box is read-produce-increment (robust to α-first AND β-first entry). Values from libgc (`GC_get_heap_size`/`GC_get_free_bytes`/`GC_get_gc_no`) — option-(a) real-stats, oracle-SHAPE-matched (the .std region/GC/time values are 1993 Sun-4 platform constants, non-diffable per README). `&host`=gethostname. (2) **ICNBENCH-ARGS** — `main`'s `args` param was `null`, so options.icn's `get(arg)` raised error-5 "Undefined function or operation"; scrip.c now builds an empty Icon list (`rt_make_list`) into main's first param slot ([r12+16]) in BOTH mode-3 (C) and mode-4 (emitted entry) when main declares ≥1 param — `main(args)` is now `type=list size=0` matching iconx. VERIFIED: icon audit 94/94 both modes (no regression), icon smoke 12/12×2, all 4 generators oracle-shape-verified in isolation+multi-call. **KNOWN REMAINING (deal/ipxref run + harness-pass but output not yet byte-faithful):** the `write := writes := 1` output-suppression idiom (Icon's integer-apply `1(x)` no-op trick) is unimplemented, so program body output isn't suppressed and Term__'s elapsed-time line + deal's shuffle are off — a SEPARATE rung (INTEGER-APPLY / write-reassignment), NOT the generators (all 4 verified correct standalone). Superseded scoreboard below.

OLD SCOREBOARD (2026-07-03 pre-keyword-gen): oracle 10/10 · m3 **2/10** · m4 **2/10** = version + **micsum**; SCRIP `5c5697ab`+scantab, Claude Sonnet 5)
**SCANTAB LANDED 2026-07-03 (this session) — see ICNBENCH-7 below.** micsum went 1/10→2/10 in BOTH modes (byte-identical to iconx on the real 119-line micro-timing input → `112 15 4 30 14 stdin`). Zero regression: corpus rung suite IDENTICAL FAIL set before/after (PASS=212 FAIL=41 XFAIL=36 both, stash-compared), smoke 12/12 m3+m4, scan-gate tab probes (tab_3/tab_upto/move_2) all PASS. **Board diagnoses CORRECTED this session (both were mislabelled "missing template"): `IR op=19` (geddump) and `IR op=3` (tgrlink) are GUARD-SINKS inside existing emit_drive arms (drive_unowned fall-through), NOT missing cases — geddump's true wall is the binary `!` APPLY operator (`(gedsub ! a).data`; unary `!L` field-get already works), tgrlink's is a BINOP operand with slot<0 (emit.cpp:936). NEW pre-existing finding (orthogonal, do NOT fix under scantab): a FAILING position-move in a bounded scan — `s ? tab(oob)` OR `s ? move(oob)` (move untouched) — does not confine failure to the `?` boundary (execution stops at the statement); `s ? find(fail)` confines correctly. micsum's tab(0) SUCCEEDS so never hits this.**
**UPDATE, same session, after landing ICNBENCH-2/2b/4 below:** the "Init__/link" framing this section opened with was itself imprecise — root-caused this session: **SCRIP's `link` directive is a complete no-op.** It parses `link X` into a placeholder AST node and never reads `X.icn` — proved with `link this_file_does_not_exist_anywhere`, which fails identically to a real link target. The WORKAROUND (zero source changes, verified): pass the linked `.icn` files as extra arguments on `scrip`'s own command line — `src/driver/scrip.c`'s per-file loop compiles every file argument into the same program, which is enough to turn a bare unresolved `IR_CALL` into `IR_CALL_PROC_STAGED`. `scripts/test_icon_bench_corpus.sh` now does this (`SCRIP_LINK_DEPS[]` array). **Implementing real `link` resolution in the compiler is NOT done and is now explicitly OUT OF SCOPE for this rung** — the workaround fully substitutes for it at the invocation level; a proper fix (parser/driver hook to resolve+compile a link target lazily) is a separate, larger, un-scoped rung if ever wanted.

**LANDED this session (SCRIP, `src/runtime/by_name_dispatch.c`, oracle-pinned both modes, zero smoke regressions — 12/12 m3+m4 before and after each):**
- [x] **getenv(s)** — was completely unimplemented. Added to `known[]` + a real `try_call_builtin_by_name` arm (libc `getenv`, `FAILDESCR` when unset). Probe: set + unset cases, m3 +m4, byte-identical to iconx.
- [x] **open/where/close** — `open`/`close` already had full implementations (`fh_alloc`/`fh_get`, file-handle-as-int) but were missing from `rt_builtin_is_known`'s `known[]` — the ONE list `bb_call_route_classify` actually checks (a different, Pascal-facing list near line 1840 also contains these names but doesn't gate Icon's classifier — don't confuse the two). `where` had no implementation at all; added as `ftell()+1` (canonical Icon `where()` is 1-based — oracle-verified, not assumed). Probe: `open→where→reads→where→read→where→close` sequence, m3+m4 byte-identical to iconx (`1 4 12`).

**Net effect (re-ran `test_icon_bench_corpus.sh` after landing all four — this is the current, real scoreboard, not a projection):** still **1/10** (`version.icn` only) — but 8 of the other 9 moved to a DIFFERENT, more specific failure than before, which is the honest signal these were real fixes, not no-ops:
- **concord, deal, ipxref, queens — all four now fail identically**, past Init__/getenv entirely, inside `post.icn`'s `Signature__()`/`Regions__()`: `** Error 5 in statement 0 / Undefined function or operation` then SIGSEGV (rc=139, not the old rc=134 abort). Bisected (this session) to the `&host`/`&features`/`&regions` keyword-introspection family — `every write(&features)` alone silently produces nothing (should list feature strings); `&regions` (driven via `every put(regions,&regions)`) produces list entries that `right(n,8)` renders as blank, and indexing further into that list is what SIGSEGVs. **These keywords have no natural referent in SCRIP's execution model** (no classic-Icon-style static/string/block memory regions exist in a natively-compiled program) — this is a real design question (what should `&regions` even return here?), not a mechanical gap, and deliberately NOT attempted this session.
- **rsg**: past `open` cleanly, now `libscrip_rt: BOMB — bb_var_ref: variable has no addressable cell` — new, distinct, unexamined.
- **micsum**: past `open` cleanly, now `libscrip_rt: BOMB — bb_scan_tab: unhandled (needs literal positive n)` — a scan-with-non-literal-count gap, new, distinct, unexamined.
- **tgrlink**: past `where` cleanly, now `IR op=3 has no template` — likely also needs `seek()` (absent, checked, not yet implemented) once this next wall clears.
- **geddump, micro**: unchanged (`IR op=19`, `collect`) — neither depends on link/getenv/open/where, so no movement expected and none seen. Consistent.

**Also found — CORRECTED after reading RULES.md (not read earlier this session; should have been):** what looked like a parser gap (bare newline-separated statements past the first fail to parse) is `RULES.md`'s own **"ICON SEMICOLON-REQUIRED — NO NEWLINE PROCESSING"** absolute rule, deliberately gated by `scripts/test_gate_icn_semicolon_required.sh` — SCRIP's Icon front-end is INTENTIONALLY newline-blind; `icont`'s Beginner/Ender newline→`;` insertion is explicitly FORBIDDEN in `src/parser/icon/`. Not a bug, not a rung. Retracting the ICNBENCH-PARSER-SEMICOLON line below — real corpus files are unaffected (period-authentic semicolon style throughout), which is exactly why this never surfaced against them, only against this session's own hand-written probes.

**Original ORIENTATION SYNOPSIS below is UNCHANGED and still accurate for the method/tooling; only the diagnosis above is corrected.**

**Supersedes** `HANDOFF-2026-06-23-CLAUDE-ICON-BENCH-BLOCKER-MAP-AND-INITIAL-STORAGE-GAP.md` — its `IR_ALT`/assign-RHS-gate/`IR_INITIAL` analysis is STALE; none of today's failures trip those gates, the frontier moved past them (LVALUE-COLLAPSE and the rest of the intervening Watermark). **Refines** the 84208eba Watermark BENCHMARK MAP two paragraphs below — three of its five buckets moved:
- `deal` no longer dies at Init__/link — it gets past linking and dies on the **`shuffle`** call specifically (own bucket).
- `micsum` doesn't `link` at all and doesn't die at Init__ either — dies on **`open`** (joins `rsg`'s bucket).
- `geddump` no longer dies on the `!` APPLY operator (that parser gap is fixed since) — it now parses+lowers fully and dies on **`IR op=19` has no emitter template**, a distinct, later-stage blocker.
- `micro`→`collect`, `rsg`→`open`, `tgrlink`→`where` are UNCHANGED, confirmed fresh.

**Method:** oracle = Icon 9.5.25a built from `icon-master.zip` at `/home/claude/icon-master` (`make Configure name=linux && make Icont`, per `doc/files.htm` + `man/man1/icont.1`); link deps pre-built via `icont -c options.icn post.icn shuffle.icn` (man-page documented: `-c` "stops after translation... a directory of such files functions as a linkable library"; `link X` resolves `X.u1`, cwd searched first). SCRIP needs no such pre-build step — `src/driver/scrip.c`'s per-file `sno_add_include_dir` resolves `link` against sibling `.icn` SOURCE directly (verified: reaches Init__-call codegen, not a "can't find options" error — a real, useful difference from icont's model, not a bug). Tool: **`scripts/test_icon_bench_corpus.sh`** (new, this session) — idempotent build+run+compare, replaces one-off manual probing; supersedes nothing existing (`update_icon_bench_asm.sh` only checks `--compile` assembles, never links/runs/times; `audit_jcon_wholesale.sh` runs the same ORC/M3/M4 pattern but against the link-free `test/icon/jcon_audit` probes, not this corpus).

**Current scoreboard** (10 runnable programs; `options`/`post`/`shuffle` have no `main`, excluded): iconx oracle 10/10 · SCRIP `--run` 1/10 · SCRIP `--compile` 1/10 (same one: `version.icn` — m3/m4 agree with each other; both differ from iconx only in the expected way, each engine reporting its own `&version` identity).

**STEPS (ordered by leverage — programs unblocked in brackets):**
- [ ] **ICNBENCH-0 LINK-INIT** — ~~multi-file `link` initialization harness~~ **RESOLVED AS A NON-ISSUE (see UPDATE above): `link` root-caused as a no-op; `SCRIP_LINK_DEPS[]` workaround in the harness substitutes fully. Nothing to fix here unless real `link` support is wanted for its own sake — new rung if so, not this one.**
- [ ] **ICNBENCH-1 SHUFFLE-CALL** — `deal` is now PAST the keyword wall and runs end-to-end (harness-pass, both modes), but its hands print UNSHUFFLED: `shuffle()` (shuffle.icn) uses the `write := 1` output-suppression idiom on the body, and the deal itself relies on the same integer-apply mechanics that are unimplemented. Folded into the new **ICNBENCH-8 INTEGER-APPLY / WRITE-REASSIGNMENT** rung below — not a separate shuffle bug. **[deal]**
- [x] **ICNBENCH-2 OPEN-CALL-SHAPE** — **LANDED** (see above). `rsg`/`micsum` both past it now, onto their own next walls.
- [x] **ICNBENCH-2b SEEK-BUILTIN** — **LANDED 2026-07-04 (SCRIP `e5934e8e`).** Canonical `fsys.r` `seek(f,o)`: o defaults 1, 1-based; o>0 → `fseek(o-1,SEEK_SET)`, o<=0 → `fseek(o,SEEK_END)`; fseek failure → fail, else return f. Beside `where` in `script_try_call_builtin_by_name` + `known[]`. Same commit: asin/acos/atan/dtor/rtod added to `rt_builtin_is_known` (impls existed incl. 2-arg atan2; classifier rejected the calls — the getenv/collect precedent, tgrlink's second wall) + UNASSIGNED-LOCAL slot grant (`ir_drive_slot_assign` interns IR_VAR/IR_VAR_REF local reads, skipping `&`/globals — a declared-never-assigned local read was a `bb_var` bomb, now a zero-init slot = `&null`, canonical, m3==m4==iconx; fix in LOWER per TE doctrine, zero emitter edits). tgrlink cleared seek→atan→options-link→unassigned-local and runs rc=0 (2L vs 3239L — remaining wall = ICNBENCH-ARGS real arg-forwarding, `main(args)` still empty). **[tgrlink — builtins DONE, blocked on ARGS]**
- [x] **ICNBENCH-2d CONCORD-SCAN-UPTO** — **LANDED 2026-07-03 (Claude Opus 4.8, SCRIP working-tree; commit hash follows push).** `upto(&letters)`/`upto(&digits)` (and `many` of them) now work: `lower_icon.c` `lc_key` materializes the four compile-time-constant cset keywords (`&ucase`/`&lcase`/`&letters`/`&digits`) as `IR_LIT_CHARSET` instead of `IR_KEYWORD`, so the existing literal-cset scan path (driver reads `op_name1` from an `IR_LIT_STRING`/`IR_LIT_CHARSET` operand across the whole SCAN family) accepts them with ZERO driver/template change. Value context unchanged (same node `TT_CSET` literals already use — `write(&letters)` byte-identical). 3-way probe oracle==m3==m4; audit 94/94 both modes; smoke 12/12×2; **289-corpus FAIL set byte-identical (stash/rebuild/comm — 43=43, zero regressions)**. `&ascii`/`&cset` deliberately NOT materialized (NUL-exclusion + 255-vs-256 size subtlety; still IR_KEYWORD, correct as values; do them if a program needs them as scan operands). **NEW WALL:** concord cleared the scan barrier and runs its full concordance body + post.icn Regions__/Storage__, then dies at `Error 5`+SIGSEGV inside the `&storage` output (`string16977920` = SCRIP's honest live heap bytes) — the shared **keyword-introspection/STATICS/INTEGER-APPLY design wall** (ICNBENCH-8 + the STATICS rung), not a scan issue. Scoreboard unmoved (concord's flip gated there). **[concord — scan DONE, blocked downstream]**
- [x] **ICNBENCH-2c KEYWORD-INTROSPECTION FAMILY (`&host`, `&features`, `&regions`, `&storage`, `&collections`)** — **LANDED 2026-07-03 (SCRIP `52916a86`), option-(a) real libgc stats.** All 4 are now resumable generators (see scoreboard header for the full three-part implementation: `k+=2` counter grant, `ir_is_generator_kind` inclusion, and the seed-IR_GOTO-to-α entry that makes α always init the counter even on repeat proc calls). `&host`=gethostname. Oracle-SHAPE-verified in isolation + multi-call (the .std absolute values are non-diffable 1993 Sun-4 constants). This was the shared wall for concord/deal/ipxref/queens; deal+ipxref now run end-to-end, concord+queens advanced to their own next blockers (below).
- [x] **ICNBENCH-3 COLLECT-BUILTIN** — **LANDED 2026-07-03 (Claude Opus 4.8, SCRIP working-tree; commit hash follows push).** `collect` was call-shape-unsupported (missing from `rt_builtin_is_known`'s `known[]` — the getenv/open/where precedent). Added `"collect"` to `known[]` + a dispatch arm in `try_call_builtin_by_name`: `nargs<=2` → `GC_gcollect()` → `*out = NULVCL` (Icon null). Canonical `collect(region,bytes)` (fmisc.r) forces a GC and `return nulldesc` `{1}`; SCRIP has one unified libgc heap (no Static/Strings/Blocks regions), so region/bytes are accepted-and-ignored and the negative-bytes irunerr-205 edge is elided (micro calls `collect()` no-arg). Purely additive (one name, one arm, zero existing paths touched → cannot regress). 3-way probe `collect()`→`&null` + all arg forms oracle==m3==m4; audit 94/94; smoke 12/12×2. **NEW WALL:** micro cleared the `collect` bomb and now hits `emit_drive: IR op=55 has no template` — **op=55 = IR_UNOP** (a LANDED kind), so this is the `drive_unowned` **guard-sink** pattern (geddump/tgrlink family), NOT a missing kind: a specific unary-operator variant micro uses reaches the fall-through. Needs `--dump-ir`/gdb-bracket on micro to name the operator. **[micro — collect DONE, blocked on an IR_UNOP guard-sink]**
- [ ] **ICNBENCH-4 WHERE-BUILTIN** — **LANDED** (see above, with `close` as a needed companion fix). `tgrlink` past it, onto `IR op=3`. **[tgrlink partial — needs ICNBENCH-2b too]**
- [ ] **ICNBENCH-5 GEDDUMP-OP19** — unchanged, unattempted. `--dump-ir` on `geddump.icn` still the next move. **[geddump]**
- [ ] **ICNBENCH-6 RSG/QUEENS-NV-CELL** — `bb_var_ref: variable has no addressable cell (NV)`. **queens now hits this too** (it cleared the keyword wall and lands on the identical error), so this is a 2-program rung. Unexamined past the message itself — next move is `--dump-ir` on a minimal repro to see which variable class (global? tvsubs target?) has no GVA/frame cell. **[rsg, queens]**
- [x] **ICNBENCH-7 MICSUM-SCANTAB** — **LANDED 2026-07-03 (SCRIP, commit hash follows this session).** Root cause was NOT "non-literal n" — it was `tab(0)` (micsum line 39 `label := tab(0)`, the Icon tab-to-END idiom): the box's `tab_admit`/branch keyed on `op_sb >= 1`, so a literal **0 (and negatives)** were rejected as "needs positive n". Fix mirrors canonical `cnv.r` **cvpos**(pos,len) = {fail if pos>len+1 or pos<-len; pos if pos>0; else len+pos+1}: (1) `src/templates/bb_scan_tab.cpp` — operand discriminator changed from `op_sb>=1` to `op_sa` (op_sa≥0 ⟹ runtime n in slot; op_sa<0 ⟹ literal n = op_sb, ANY value), added branchless cvpos normalization (`cmp rax,1; jge L0; add rax,r15; add rax,1; def L0`) then a single `1≤n≤len+1` range check (which correctly rejects raw n>len+1 and raw n<-len); `tab_admit()` simplified to `op_off>=0`. (2) `src/emitter/emit.cpp` IR_SCAN_TAB drive arm — literal branch owns op_sb for every integer value (so a slot-less runtime operand can't masquerade as literal 0); loud-aborts (`drive_unowned`) a genuinely slot-less runtime operand + the no-operand case. Oracle-pinned m3==m4==iconx on tab(0)/tab(-2)/backward-tab/full-span-tab(-len) probes AND micsum end-to-end (byte-identical, both modes). The runtime-n path (tab(many(...)), op_sa≥0) is unchanged and also now cvpos-normalizes for free. **[micsum — DONE]**
- [ ] **ICNBENCH-8 INTEGER-APPLY / WRITE-REASSIGNMENT** — NEW (surfaced by deal/ipxref now running). post.icn's Init__ does `Save__ := write; write := writes := 1` to suppress body output (Icon's `1(x)` integer-apply no-op trick: calling an integer applies it as a selector returning its arg, so `write(x)`→`1(x)`→`x` with no I/O), and Term__ restores `write := Save__`. SCRIP doesn't implement integer-apply, so the assignment is a no-op and body output is NOT suppressed → deal prints unshuffled hands, ipxref/concord bodies leak, Term__'s elapsed-time line is dropped, and Collections__ trails off. Separate from the keyword generators (all 4 verified correct standalone). This is the main output-fidelity gap for the 2 newly-running programs. **[deal, ipxref, concord]**
- [x] **ICNBENCH-ARGS** — **LANDED 2026-07-03 (SCRIP `52916a86`).** `main`'s `args` was `null` → options.icn's `get(arg)` raised error-5. scrip.c now builds an empty Icon list (`rt_make_list`) into main's first param slot ([r12+16], ABI-fixed 16*(i+1)) in BOTH mode-3 (C, ~line 1256) and mode-4 (emitted `main:` entry, the `main_α` path ~line 973 — NOT the `flat_α` path) when `bbg->nparams>=1`. `main(args)` now `type=list size=0` matching iconx. NOTE: forwards an EMPTY list — the harness passes link-deps as scrip CLI args (indistinguishable from program args), so real CLI-arg forwarding (deal `-h`, queens `-n`) is still absent; programs run on their defaults, which is why deal/queens don't honor a hand/board count.
- [ ] **ICNBENCH-BENCH** — once ≥2 of the above land, capture real `--bench` (parse/lower/exec/total) timing vs iconx for the newly-passing programs — the actual "10× faster" data point this corpus exists to produce. Nothing to measure yet; only `version.icn` completes today and it's trivial/startup-dominated.
- [ ] **ICNBENCH-FENCE** — `bash scripts/test_icon_bench_corpus.sh` reports 10/10 on both m3 and m4 (or documents a principled, permanent exclusion per program) before this rung closes.

## Watermark

**⌚ 2026-07-05 (fourth session same day, Claude Fable 5 — ZLS AUDIT-KIND BURNDOWN COMPLETE, the ZB-2(c)/GC-1-prep rung).** All 10 shipped `(audit)` provisional kinds in `zeta_storage.c` template-verified and burned to audit=0; the zls[] typed field maps are now collector-consumable (the §6b stack-map premise holds). THE CATCH: **REV_ASSIGN(_VAR) `+16` save slot RAW→DESCR** — `bb_rev_assign{,_var}.cpp` park the variable's OLD VALUE there as a full t·p pair, restored on β, LIVE across the suspension window; RAW would have had GC-1 skip a live heap ref (premature collection). MISLABEL FIXED (was non-audit!): SCAN_ENTER's "+0 scan.value DESCR / +16 scan.save" — the node isn't in produces_value and never touches its slot; it is IR_SCAN(leave)'s 24B `rt_scan_leave` out-area (σ transient/dead-at-safe-points, δ, Δ, pad). CREATE cells verified pure marshal (scrip_coexpr_create copies regs[0..5] into pkg → dead at return; per-field named r12..rbp; handle low-qword = raw malloc'd ctx*, never trace). Remaining 7 = pads/ints split to honest 8B granularity (INITIAL flag at +8, ITERATE index, REPALT yielded flag, LIMIT/TAB/MOVE/gate/resume pads confirmed untouched). **TWO GC ROOTS the §6b enumeration missed, now recorded there:** (i) static `scan_stack[]` (gen_runtime.c) holds heap-interior σ across whole nested scans; (ii) coexpr ctx/pkg are plain-malloc — invisible to libgc, hold captured σ/rZ for coexpr lifetime = LATENT liveness bug (string reachable only via suspended coexpr's σ is collectable today; masked by creator-frame aliasing; fix home = coexpr rungs, conservative-scan-only, never relocate-through). VERIFIED: `.s` byte-identity STASH-PROVEN (Icon+SNOBOL4 probes — metadata-only change, zero layout delta; regen N/A by that proof) · crosscheck m3 168/93, m4 168/3/90 {082,099,213}, DIVERGE=0 — name-for-name the ZB-3 baseline · Icon smoke 12/12×2 · gates no_ir_mutation/no_lang/no_slot_alloc PASS · grep audit-grants = 0. New-grant rule standing: every future zls_field lands audit=1 until its template is read. NEXT: Lon rules D3/D13/D15; then ZB-4 (struc overlays + no-.bss gate — the overlays now print from CLEAN maps) or ZB-5.

Prior: **⌚ 2026-07-05 (Claude Fable 5, ζ-DESIGN session) — `ARCH-ZETA-LOCAL-STORAGE.md` AUTHORED (official ζ doc of record, .github) + SCRIP `src/contracts/zeta_choices.h` (ZC_* compile-time choice axes; additive, included by NOTHING yet — default build byte-untouched; header PROVEN: defaults compile, `-D` overrides compile, illegal combos + GC stubs `#error`).** Design-only session: zero codegen/template/lower edits ⇒ regen scripts N/A. Doc content: the 6-model ζ history (M1 interp heap ζ → M2 4/28 chunk model → M3 one-register r12 ratification → M4 seed goldens → M5 flat `ir_drive_slot_assign` → M6 ZB pivot) with a per-reset LESSON each; one4all re-cloned publicly for evidence (blk_alloc.c mmap-per-call, snobol4_asm.mac:2040 ARBNO `resq 64`, beauty_prog.s fn_upr clone-tier + `box_*_data_template` field maps re-verified @4757bbcd); seeds 1–6 laws distilled (moving-ζ, ψ element pointer, λ landing, `*ζζ` enter(), two-plane r12, broker push/pop, Prolog ζ-tree `rt_enter`); `IR_t.tmp`'s FIVE conflated lifetimes named. **NAMING RETRACTION (Lon, same day): "ZLA"/"array" are DEAD — ZLS = internal completely TYPED data (TYPED PRINCIPLE block; zls[] upgraded to per-FIELD map `{off,size,kind∈DESCR/PTR_GC/PTR_CODE/RAW}` = the future GC stack map), COLLECTION = the ARBNO-style owner-owned growable storage, pointer FROM ZLS.** New classes/captures: **ZL-COEXPR** (Lon: Icon partitions ζ at PROCEDURE and CO-EXPRESSION level; substrate options O1 pthread / O2 plane-swap / O3 hybrid-recommended; `^e` refresh = the clone tier's return); **§5h α/β R12 SELF-LOAD HOOK** (toggleable at the two central `x86()` label sites, zero per-template edits; source (a) plane-cell = seeds-3/4 `*ζζ` and mechanically discharges the RELOAD LAW; (b) ASSERT compare-and-bomb wiring checker); **§5i O-HEAP extreme** (per-box heap ownership: malloc = terrible perf, REJECTED as impl / KEPT as model; same model on GC BUMP+SLIDE = possible end-state where the LIFO requirement disappears — deferred fork D14); **§5j ZC_* axes** (ALLOC INFINITE/LIFO/MALLOC/GC · COLLECTION MALLOC/ARENA/GC · SELFLOAD · INIT · POISON · TELEMETRY · OVERFLOW · ARENA_MB · PROMOTE; experimental defaults = INFINITE+ZERO+FILL+TELEM+BOMB+1024MB; MALLOC mode = M1 resurrected as an ASan diagnostic) + **THE MODE-INVARIANCE GATE** (axis switch may change bytes/speed, NEVER behavior — FAIL set byte-identical across modes; inter-mode divergence brackets lifetime bugs like the monitor brackets semantic ones). GC ladder **GC-0..7** (SIL 3-stage MARK/ADJUST/SLIDE; SPITBOL-manual pins; ONE scrip heap, TWO families per Lon: (A) COLLECTIONS + heap-promoted ζ scopes, (B) dynamically created DESCR payloads behind user VARIABLES). Decision table **D1–D15** (OPEN for Lon: D3 arena size · D8 coexpr O3 · D10 scan-subject pin · D11 ZB-6-before-ZB-5 · D13 build self-load now · D15 confirm ZC defaults). **ZB-2 NEXT SESSION: read ARCH-ZETA-LOCAL-STORAGE.md FIRST, then zl_build() + `--dump-zeta` + typed field maps + re-base the `x86_scratch_off` consumers (emit.cpp:980/984/996).**

**⌚ 2026-07-04 (Claude Fable 5) — SN4-PAT-3a..3g: ELEVEN matchers landed in one session; corpus m3 117→138, m4 116→137, FAIL set {082,099,213} stable throughout.** LIT (template written fresh — none ever existed; orphaned pre-family `bb_lit.cpp` found wired-but-uncalled, park-candidate awaiting Lon), ANY/NOTANY (first-ever execution exposed the silent-empty `x86("cmp","sil",...)` encoder decline — 8-bit regs unknown to the classifier, dispatch returns empty instead of bombing: EMITTER-WIDE FOOTGUN, every unwired template is suspect), SPAN (found `_.x86_scratch_off` read by 5 templates, written NOWHERE — fixed via LOWER grant per TMP-ERADICATE; collision-probed), BREAK/BREAKX (grant applied up front), TAB/RTAB (TAB missing Δ bounds check — caught pre-corpus, fencepost-pinned; RTAB overlong passes by signed-underflow ACCIDENT, flagged not touched), **TAB/RTAB TWO-MODE RETROFIT (Lon-directed proof-of-concept: LOWER stops shape-gating, arg lowered generically as operand; emitter DRIVE folds `IR_LIT_INTEGER`→immediate else slot-read, mirroring `IR_SCAN_TAB`; proven by .s inspection `mov rax,3` vs `mov rax,qword ptr [r12+104]`; `sno_pat_node` now takes `scx_t*` — plumbing paid once)**, POS/RPOS/REM/ARB (two-mode from birth; parser fact: bare `REM`/`ARB` arrive as `TT_VAR`, name-dispatch arm restored; ARB now generator-kind, β-exhaust cursor-restore fixed; REM α-save/β-restore added). Gates 3/3 PASS, icon smoke 12/12×2, feature .s regenerated (11 files). NEXT: **SN4-PAT-3h CAT/ALT** (parked `TT_SEQ` 4-branch arm, the delicate one). PENDING LON: retrofit remaining 7 matchers to two-mode? park `bb_lit.cpp`? **⚠ LOST-WORK NOTICE: the 2026-07-04 Opus ICNBENCH watermark below documents SCRIP `93f906ff` + corpus `710deb15` as local/unpushed — that sandbox is gone; those 4 fixes (binop-keyword restamp, `$define`, statics-GVA, `!` apply) exist ONLY as the spec in that watermark text. Do not delete it; it is the recovery recipe.**
**2026-07-04 (this session, Claude Opus 4.8) — IR_KEYWORD SPLIT LANDED (working-tree, UNPUSHED — needs credential + SNOBOL4 `.s` regen before commit).** `IR_KEYWORD` → `IR_KEYWORD_ICON` + `IR_KEYWORD_SNOBOL4` (enum +1, AUTHORIZED carve-out to the NO-NEW-IR freeze — see the freeze line's carve-out note). lower_icon mints ICON, lower_snobol4 mints SNOBOL4; emit.cpp dispatches by opcode to `bb_keyword_icon` (verbatim ex-`bb_keyword`, `rt_keyword_read`) vs new `bb_keyword_snobol4.cpp` (single-value read, no scan-reg/generator arms, new `rt_keyword_read_snobol4`). CORRECTNESS GAIN (safe-by-accident → correct-by-construction): `IR_KEYWORD_ICON` stays in `ir_is_generator_kind` + slot `k+=2` (Icon `&features`/`&regions` resumable); `IR_KEYWORD_SNOBOL4` OUT of generator-kind + `k+=1` (no meaningless resume counter). Touch-set: IR.h enum · scrip_ir.c (name table + jcon_converted_producer + slot-grant split + print) · ir_query.c generator-kind → ICON · emit.cpp (op_sval list, template dispatch split, IR_VAR-`&` fallback→icon, drive case both, chain_arity both) · scrip.c 3 scan-classifiers (both) · both lowers · bb_templates.h decl · keywords.{h,c} (+rt_keyword_read_snobol4) · Makefile (rename+add) · emit_per_kind_audit tool. VERIFIED: build ×2 · Icon smoke 12/12 ×2 · SNOBOL4 smoke 4/3 ×2 (both byte-identical to baseline) · no-lang + mutation gates PASS · 0 bare-`IR_KEYWORD` residue · functional `write(&features)`→IR_KEYWORD_ICON→`UNIX`, `OUTPUT=SIZE(&ALPHABET)`→IR_KEYWORD_SNOBOL4→`256`. FOLLOW-ON (not this rung): physically partition the `kw_read` table so the two keyword sets are distinct DATA (closes the folded-collision for true polyglot programs; the opcode split is the prerequisite that unblocks it). HANDOFF: SNOBOL4 keyword `.s` codegen changed (`rt_keyword_read`→`rt_keyword_read_snobol4`) — run the `util_regen_*_s_artifacts.sh` set before commit per RULES.md step 4; Icon `.s` unchanged (byte-identical template). The broader LANG_*/`:lang` enum eradication (Increment 3) remains staged. **ALSO THIS SESSION — INIT-ALL LANDED (working-tree):** `polyglot_init`'s two per-language init blocks (Icon/Raku/Pascal frame+scan; Prolog atom/trail/resolve) made UNCONDITIONAL (Lon "init all languages simultaneously" — the mask no longer gates initialization; the enabler for the enum removal, since init stops needing to know the language). Verified green (Icon 12/12 ×2, SNOBOL4 4/3 ×2; the Prolog probe returns the parked-backend GZ#5 stub, not a regression). **REMAINING = the ATOMIC Increment-3 rung, now fully specified (Lon command decision 2026-07-04):** (1) ONE switch on the file extension in the driver → direct `lower_X_stage2` call (NO sentinel arg, per this file's doctrine), retiring `lower_stage2`'s mask-dispatch + `polyglot_lang_mask`; (2) relocate `polyglot_init`'s `:lang`-driven module/proc/record/global registration (polyglot.c ~64-155) INTO each lowerer, which registers knowing its own language (zero `:lang` reads) — single-language gates (Icon procs, SNOBOL labels) must stay exact; (3) delete `LANG_*` enum, the `:lang` attr (icon/raku/pascal parsers + the `stmt_ast.c` `STMT_t.lang`→`:lang` conversion), `STMT_t.lang`, the write-only `ScripModule.lang`, the `lower_snobol4.c:127` guard, the `lower_prolog.c:578` filter, and de-`LANG_*` `parse_scrip_polyglot`'s fence dispatch (tag string → parser directly). Gate: Icon 12/12 ×2 + SNOBOL4 4/3 ×2. **DOCTRINE REFINEMENT (Lon 2026-07-04):** language-SPECIFIC code lives in exactly THREE homes — PARSER, LOWER, and language-specific TEMPLATES (the `IR_KEYWORD_*` pattern); everything else (emitter driver, IR spine, runtime, shared templates) stays language-blind.
 **CONCURRENT-SESSION RECONCILIATION (2026-07-04, this hand-off):** this session's IR_KEYWORD split landed on origin the same day as a separate concurrent session's `IR_KEYWORD_ASSIGN` (KEYWORD-LVALUE `&pos := v`, entry immediately below) — both based on the same parent commit (`8f2a946`), pushed within the same window, discovered via a rejected non-fast-forward push. Reconciled by hand (not an automatic merge): every overlap was additive-adjacent, not a design collision — `IR_KEYWORD_ASSIGN` is a genuinely new sibling opcode (Icon-only lvalue WRITE) independent of the READ-side ICON/SNOBOL4 split. Merged IR.h/emit.cpp/scrip_ir.c/bb_templates.h/Makefile hunks by hand keeping both changes; lower_icon.c and .github's other hunks auto-merged clean (different regions of the file). Re-verified post-merge: build ×2, Icon smoke 12/12 ×2, SNOBOL4 smoke 4/3 ×2, no-lang + mutation gates PASS. `IR_KEYWORD_ASSIGN` is currently Icon-only (minted only from lower_icon.c) so it does not yet need an ICON/SNOBOL4 split itself — flagged as a likely future follow-on once SNOBOL4's RL-8 (`&TRIM =`/`&ANCHOR =`) lands.

**2026-07-04 SESSION (Claude Opus 4.8) — KEYWORD-LVALUE plain-assign `&pos := v` LANDED (working-tree, UNPUSHED — no credential this session).** New IR kind `IR_KEYWORD_ASSIGN` (classify-by-name per JCON-ALIGNMENT), one template `bb_keyword_assign.cpp`; RT does the value work (cvpos), BOX does ports + the δ(r14) write (NO-DUP). Canonical `oasgn.r` kywdpos: coerce→int, `cvpos(i, Δ=r15)` (OOB→**fail/ω**, `i>0` passthrough, `i≤0`→`len+i+1`), δ=pos−1, result `{DT_I,pos}`. Two paths mirroring `bb_keyword` read: scan-live → `rt_cvpos_pos(v,r15)` + r14 write; non-scan → `rt_keyword_pos_set(v)` (cvpos vs `strlen(scan_subj)`, sets `scan_pos`, `FAILDESCR` on OOB). AUGOP rides free via the existing desugar (`&pos +:= 1` → `&pos := &pos+1`). Files: IR.h (enum) · scrip_ir.c (name row + `ir_node_produces_value` + `ir_drive_slot_assign` k+=1 grant) · lower_icon.c (TT_ASSIGN keyword-lhs route, before the plain-var arm) · emit.cpp (walk `op_sval` whitelist [clobber-pattern site] + walk dispatch + `emit_drive` case + `IR_KEYWORD_ASSIGN` added to all 4 ω-follow groups — the probe-67 else-routing lesson: `if &pos:=99 then/else` needed it) · bb_keyword_assign.cpp (new) · bb_templates.h (decl) · gen_runtime.c (`rt_cvpos_pos` + `rt_keyword_pos_set`, shared `cvpos_of`) · Makefile (RT_PIC_SRCS + compile rule). **SHAPE-VERIFIED (oracle-pinned probe, m3==m4==iconx):** `&pos:=3`→3 · `+:=5`→8 · `&pos:=-1`→11 · `&pos:=0`→12 (cvpos) · `if &pos:=99`→OOB fail→else · non-scan `&pos:=4` (len 0)→fail→unchanged. **micro's blocker CLEARED:** `[TE-4] IR_ASSIGN '&pos' has no varslot` abort → GONE; micro now runs past keyword-assign and advances to its next wall = **TIMEOUT** (ICNBENCH-ARGS: `main(args)` time-budget `0.05` not forwarded → unbounded run; ~15s even for iconx). **NO REGRESSION:** icon smoke 12/12×2 · audit 94/94 both modes · 289-corpus **210/43/36 FAIL set byte-identical** (43=43, comm empty both directions) · 5 gates PASS (no_stack 0, one_reg 0, semicolon prison, local_no_nv, emit_no_ir_mutation HARD=0) · template-purity: new box x86()-only (the 2 flagged are pre-existing in bb_call_write_slot.cpp). **PRE-EXISTING LIMITATION DOCUMENTED (NOT this rung's; affects READ too):** a keyword op (`&pos` read OR write) textually immediately after a scan block emits nothing — a `g_scan_regs_live` scan-exit emission-ordering artifact (bare `"hi"?tab(2); write(&pos)` also drops the line); out of KEYWORD-LVALUE scope. **NEXT (KEYWORD-LVALUE follow-ons, in order):** `&subject := s` (set Σ/Δ, reset δ=scan_pos=1, string not int; oasgn.r kywdsubj) · keyword `:=:` swap + `<->` reversible-swap (two-sided-lvalue over a keyword — the rung37_neg_pos + rung36_jcon_subjpos family). Scoreboard unmoved 6/10 (micro's flip now gated on ICNBENCH-ARGS, not keywords). Codegen touched → handoff must run `util_regen_*_s_artifacts.sh` + `update_icon_bench_asm.sh` before commit; not run (nothing committed/pushed yet).

Prior: **2026-07-04 SESSION CLOSE (Claude Fable 5) — SCRIP `e5934e8e`, corpus `28cffd18`: THREE FIXES, BENCH HARNESS 4/10 → 6/10 BOTH MODES (queens + tgrlink fatal→rc=0).** (1) **ICNBENCH-2b `seek(f,o)`** — canonical fsys.r (1-based; o>0 `fseek(o-1,SEEK_SET)`, o<=0 `fseek(o,SEEK_END)`; fail on error else return f), beside `where`. (2) **TRIG CLASSIFIER GATE** — asin/acos/atan/dtor/rtod added to `rt_builtin_is_known` `known[]`; impls existed (incl. 2-arg atan2) but the classifier rejected the calls (getenv/collect precedent; tgrlink's atan wall). (3) **UNASSIGNED-LOCAL SLOT GRANT** — `ir_drive_slot_assign` now interns `IR_VAR`/`IR_VAR_REF` local reads (skipping `&`-keywords + globals): a declared-but-never-assigned local read had NO slot → `bb_var` "unhandled arm" bomb; zero-init slot = `&null`, canonical (`image(x)`→`&null`, `/x` succeeds), m3==m4==iconx on the minimal repro (`local x; write(image(x))`). Fix in LOWER per TE doctrine, ZERO emitter edits — honest slot-order churn possible (read-before-assign interning order), behavior-identical. **VERIFIED:** smoke 12/12×2 · audit 94/94 both modes · 289-corpus **210/43/36 FAIL set byte-identical** · gates no_stack/one_reg/semicolon/local_no_nv/emit_no_ir_mutation PASS · bench-asm total=13 updated=1(micsum) compile-err=11 (matches prior baseline) · SNOBOL4 benchmark/feature/demo regen: zero changes. **HARNESS-OK ≠ BYTE-FIDELITY:** queens rc=0 **24L vs oracle 30L** — the unassigned-local grant moved it off the DT_N-unmasked Error 3; NEXT SESSION MUST VERIFY whether the statics residue is resolved or RE-MASKED (the 409809ff reclassification precedent — do not count queens as truth until diffed); tgrlink rc=0 **2L vs 3239L** — all builtin walls cleared (seek→atan→options-link→unassigned-local), remaining wall = **ICNBENCH-ARGS** (`main(args)` still empty; tgrlink.dat consumed as a source file by the per-file loop, `*args=0` → `&input` → empty). **micro** advanced bb_var-bomb → `[TE-4] IR_ASSIGN '&pos' has no varslot` abort = the **KEYWORD-LVALUE rung** (`&pos:=n`, `:=:`, `<->` with cvpos range-fail semantics — canonical `fscan.r:25-79` `k_pos`/`k_subject`, `data.r:187`; = the rung37_neg_pos corpus FAIL family). **geddump DIAGNOSED, one line:** `TT_BANG_BINARY` (icon_parse.c:332) has NO lower_icon arm → falls to the silent `IR_SUCCEED` default (lower_icon.c:612) — bare `f ! a` prints NOTHING vs oracle 10 (minimal repro); the `IR op=16` abort is the DOWNSTREAM field-get-on-apply symptom (emit.cpp:886 `sa<0`→drive_unowned). Rung: lower TT_BANG_BINARY as an apply-call unpacking the list argvector (canonical invoke.r); the field-get then resolves for free. Open board: BANG-APPLY (geddump) · KEYWORD-LVALUE (micro, rung37_neg_pos) · ICNBENCH-ARGS (tgrlink, deal `-h`, queens `-n`) · STATICS verify-or-fix (queens/concord) · INTEGER-APPLY ICNBENCH-8 (deal/ipxref/concord fidelity).

Prior: **2026-07-03 SESSION CLOSE (Claude Opus 4.8) — TWO ICON RUNGS, working-tree (+7/−1 across `src/lower/lower_icon.c` +5 and `src/runtime/by_name_dispatch.c` +2/−1); commit+push PENDING CREDENTIAL [RESOLVED: landed at origin as `0831f2a5`+`ac00e4e0`].** (1) **ICNBENCH-2d scan-of-constant-cset-keyword** — `&ucase`/`&lcase`/`&letters`/`&digits` materialize as `IR_LIT_CHARSET` in `lc_key` so `upto`/`many` of them work (existing SCAN driver reads `op_name1` from a literal-cset operand; zero driver/template change); value context byte-identical. (2) **ICNBENCH-3 `collect` builtin** — registered in `rt_builtin_is_known` `known[]` + `try_call_builtin_by_name` arm (`GC_gcollect()`→`NULVCL`); purely additive. **VERIFIED both rungs:** audit **94/94** both modes · icon smoke **12/12 ×2** · four `test_gate_icn_*` + `test_gate_emit_no_ir_mutation` PASS · ICNBENCH-2d full **289-corpus FAIL set byte-identical** (stash/rebuild/comm, 43=43, zero regressions); `collect` additive so no diff needed · icon bench-asm total=13 new=0 updated=1(micsum, pre-existing drift — micsum uses no affected keyword) unchanged=1 compile-err=11 (matches prior). **CORPUS BASELINE CORRECTION:** this sandbox at HEAD `92903c94` (SNOBOL4-GZ#5-rung-1 in tree) is **210/43/36**, not the prose's 209/44/36 (that predates the GZ#5 commit). **SCOREBOARD UNMOVED at 4/10** both modes (version+micsum+deal+ipxref): both rungs are honest layer-movement — concord cleared its scan bomb but dies downstream at the **keyword-introspection/STATICS/INTEGER-APPLY** wall (`&storage` live-bytes `string16977920`, Error 5+SIGSEGV); micro cleared `collect` but hits **IR op=55 = IR_UNOP** at the `drive_unowned` **guard-sink** (a specific unary-op variant, geddump/tgrlink family — gdb-bracket to name it). SCOPE: Icon-only `lc_key` + language-blind runtime; ZERO SNOBOL4-session overlap. Open board: STATICS rung (queens/regions/concord) · INTEGER-APPLY (ICNBENCH-8) · micro IR_UNOP guard-sink · geddump `!` apply · tgrlink op=3+`seek`.

Prior: **2026-07-03 SESSION CLOSE (Claude Fable 5) — THREE SCRIP COMMITS `64252d4a`+`c3d124d4`+`efc45305`, corpus `4a3cf49a`: IR_FIELD_SET DELETED (enum 63→62 — the last dead-flagged opcode with a live template; write-through rides FIELD_VAR+ASSIGN_VAR since LV-TOTAL; zero build() sites mechanically verified; bb_field_set.cpp + all consumer sites purged; the three enum-only dead call kinds CALL_BYNAME/GVAR_USERPROC/USERPROC remain) + OPTIMIZER STAGE COMPLETE + ON BY DEFAULT (Lon directive 2026-07-03; opt-out `SCRIP_OPT=0`): the 07-01 crash STALE-STRUCK (re-derived — OPT=1 289-corpus FAIL set already byte-identical at HEAD pre-change); the mandated defer-protect LANDED regardless — protect set = every operand-referenced node (value-reads + MOVE_LABEL/CREATE captures) ∪ INDIRECT_GOTO γ-targets; passthrough SUCCEED→+IR_GOTO (the pure junction); retargeted edges INHERIT the final hop's α/β `sz[4]` (else an ω routed through a β-stamped junction edge into a generator enters α fresh); effect live (rung09 while: bc=2, .s 238→234); arith_fold stays unlinked (CVA deferral); dead bc_redirect_to deleted. VERIFIED per rung AND at default-ON: smoke 12/12×2 · audit 94/94 both modes · 6 gates PASS · 289-corpus FAIL set byte-identical across FOUR runs (sandbox baseline 209/44/36 — two-program drift vs the prior prose 211/42/36, within-session identity held throughout) · bench harness 4/10 m3 + 4/10 m4 both default and OPT=1 (version/micsum/deal/ipxref; zero regression, none of the six blockers targeted) · SCRIP_OPT=0 opt-out green · icon bench-asm total=13 new=0 updated=1 unchanged=1 compile-err=11 (honest churn under default-ON; was 12 CERR) · regen: corpus `4a3cf49a` only, feature/demo no changes. ALSO (pre-directive): oracle comparison executed — icont/iconx 9.5.25a + JCON 2.2 both built from the uploads; the 4 running benchmarks are 0/10 byte-faithful vs iconx (version logic-correct, `&version` is JCON-heritage "Jcon Version 2.2"; `&features` is SCRIP's own honest set matching NEITHER oracle; **micsum silently drops its data row — NEW finding**; deal/ipxref differ by INTEGER-APPLY suppression + live `&storage` bytes; m3↔m4 differ ONLY in `&storage` heap counts). Open board unchanged: STATICS rung (queens/regions) · INTEGER-APPLY ICNBENCH-8 · concord keyword-cset · geddump `!` APPLY · micro `collect` · tgrlink op=3+`seek`.**

Prior: **2026-07-03 SESSION CLOSE (Claude Opus 4.8) — THREE COMMITS: SCRIP `8e619482` (GVA-VAR_REF) + SCRIP `409809ff` (DT_N-UNIFY) + corpus `57804948` (Icon sublime triple). Bench honestly 4/10→5/10→4/10 both modes across the session (net 4/10; queens reclassified, see below).**

⚠️ **TERMINOLOGY UPDATE — READ BEFORE TRUSTING ANY `DT_V` REFERENCE IN THIS FILE.** As of SCRIP `409809ff`, **`DT_V` is DELETED repo-wide** (was enum ordinal 15). Icon's VARIABLE and SNOBOL4's NAME are UNIFIED under `DT_N` (=9) as the single first-class-lvalue datatype (Lon's verdict: NAME **is** the LVALUE concept; prep for SNOBOL4 GZ#5). The tag is `slen`-discriminated: **slen==2 = NAMETRAP** (`VCELL_t*` — plain cell / lazy tvtbl / tvsubs; this is EXACTLY what every prior `DT_V=15` + `VCELL_t{...}` reference in this document now means — read `DT_V` as `DT_N`-slen-2 throughout the historical LANDED entries below, they are NOT rewritten to preserve the record of what each commit did at the time); **slen==1 = NAMEPTR** (raw cell pointer — SNOBOL4's classic base+offset name); **slen==0 = NAMEVAL** (by-name string — the association-honoring arm for OUTPUT/INPUT/TRACE'd names; `NV_PTR_fn` already refuses to mint cells for these). Mint via `NAMETRAP(vc)` / test via `IS_NAMETRAP_fn` (descr.h, beside FAILDESCR). `rt_deref` and `rt_assign_var` (pattern_match.c) are now TOTAL over all three arms — deref: NV_GET_fn / *ptr / VCELL-walk; assign: NV_SET_fn / raw-store / trap-walk (assignment stays a runtime call so associations keep firing). This is the piece GZ#5 SNOBOL4 inherits directly: `.X` and `$` ride the same two functions. Prolog's `DT_PLVAR`/`DT_PLREF` are a DIFFERENT feature (single-assignment + trail-undo, not general lvalues) — deliberately untouched. Explicit slen==2 was mandatory: old DT_V mints zero-init slen and would alias NAMEVAL. Also fixed en route: the VARVAL printer's `DT_N` case (core.c) union-aliased a trap's VCELL pointer as `char*` — now slen-guarded. Zero `\bDT_V\b` repo-wide.

**GVA-VAR_REF `8e619482` (NV→GVA correction, Lon directive "Icon uses GVA not NV"):** the `op_gva_k` walk-preamble derivation list (emit.cpp ~710) had `IR_VAR || IR_ASSIGN` but not `IR_VAR_REF` — the CLOBBER PATTERN's **5th sighting** (the DRIVE_FILL re-derivation class documented at the "NEXT-SESSION AUDIT" note below; first time it bit `op_gva_k`). Global lvalue bases (`sol[i]:=v`, queens' `solution[c]:=r`) had their correctly-staged GVA index clobbered to −1 before `bb_var_ref` read it → the no-cell bomb. One-token fix. **Mode-3 GVA was ALREADY live** via `m3_gva_arena`+`m3_enter_with_rbx` (scrip.c) — the GOAL-ICON-BB "GVA-M3 open" note is STALE. Proof Icon is NV-free: `grep NV_GET_fn|NV_SET_fn` = **0 across all 13 bench programs' emitted `.s`**. (`bb_var`'s NV arm stays in the template — templates are language-blind and SNOBOL4 uses NV legitimately; enforcement is that Icon never emits it.)

**BENCH TRUTH — queens reclassified from false-PASS.** Under `8e619482` queens went FAIL→"OK" (5/10); under `409809ff` it surfaces Error 3 (back to 4/10). The era-diff (stash/rebuild both ways) proved the DT_N unification did NOT break queens — it UNMASKED that queens never passed: pre-change exits rc==0 with **21 lines vs the oracle's 30** — `Regions__`/`Storage__`/`Collections__` second-call bodies silently skipped. Root residue (present in BOTH eras, same writer): a NAMETRAP-over-a-GC-list-element (value 1, queens' placement writes) at rest in a **shared static cell**. Tagged DT_V=15 it was invisible to every ladder (`*labels` on it just failed goal-directed → loops skipped, rc==0); tagged DT_N the name-aware paths engage it and it surfaces as a hard Error 3 at `Regions__`#2 `labels[1]`. Same disease, honest symptom. The cell lives in a 16MB anon rw-p mapping (`0x7ffff5fdf000`–`0x7ffff7000000`, created post-startup, neither ζ-frame nor named-GVA). **Two-proc micro** (`static labels` in `A__`/`B__`, interleaved, second call) reproduces cross-proc static **slot** + **once-flag** sharing in BOTH eras: B prints A's list, rc==0, silent-wrong. (Correction to a mid-hunt reading: the "trap present before Init__" gdb stop was an unmapped-page READ ERROR on the conditional, not condition-true — the region maps in later.)

**NEXT OPEN-BOARD BLOCKER — the STATICS rung (ICN-STORAGE).** `static` variables today share a slot across same-named procedures AND share a single `initial` once-flag → silent cross-proc contamination (queens/regions blocker + the whole silent-wrong family the micro exposes). Fix: dedicated per-static PERSISTENT cells + per-proc once-flags; the `__gva` arena is the natural persistent-writable-static region. This kills queens' blocker directly. Sits alongside rsg's INTEGER-APPLY wall (ICNBENCH-8, Error 5: `write:=1` makes a later `write(x)` apply an integer). **Icon sublime triple** (corpus `57804948`): `Icon.sublime-syntax`+`.sublime-settings`+`.sublime-build` in `corpus/editor/sublime/`, all lexical facts deduced from `src/parser/icon/icon_lex.c` with line citations, family-matched to SNOBOL4/Snocone. **VERIFIED (both commits):** both builds · smoke 12/12×2 · audit 94/94 both modes · 5 gates PASS (mutation HARD=0) · 289-corpus FAIL set byte-identical to baseline (comm empty both directions, both commits) · bench-asm regen updated=0 (no template tests the tag). **Open board:** STATICS rung (ICN-STORAGE, queens/regions) · INTEGER-APPLY (ICNBENCH-8, rsg + deal/ipxref output fidelity) · concord `bb_scan_upto` keyword-cset (ICNBENCH-2d) · geddump IR op=19 `!` APPLY (ICNBENCH) · micro `collect` builtin (ICNBENCH-3) · tgrlink IR op=3 + `seek` (ICNBENCH-2b) · SNOBOL4 GZ#5 (the DT_N unification is its runway).

Prior: **2026-07-02 (later same day, Claude Sonnet 5, ICNBENCH session — hand-off in progress, commit hash follows this entry) — FOUR builtins landed in `src/runtime/by_name_dispatch.c`, zero smoke regressions (12/12 m3+m4 before/after each), ICON-ONLY (no non-Icon test run, per this file's standing directive).** `getenv`/`open`/`where`/`close` were either fully unimplemented (`getenv`, `where`) or implemented-but-unregistered in `rt_builtin_is_known`'s `known[]` (`open`, `close` — a different, Pascal-facing list near by_name_dispatch.c:1840 has these names too but does NOT gate Icon's `bb_call_route_classify`; don't confuse the two). Each oracle-pinned against `icont`/`iconx` built fresh from `icon-master.zip` at `/home/claude/icon-master`, byte-identical m3+m4 vs oracle on both the success and FAIL branches. Root-caused the standing "Init__ harness" framing along the way: **`link` is a no-op in SCRIP today** — parses `TT_LINK`, never reads the target (proved: a nonexistent-file link target fails identically to a real one). Verified substitute: pass linked `.icn` files as extra `scrip` command-line arguments — `scripts/test_icon_bench_corpus.sh` (new) does this via `SCRIP_LINK_DEPS[]`. Net effect on the benchmark corpus: still 1/10 end-to-end (`version.icn` only — reporting the honest number, not a proxy) but 8 of the other 9 moved to a new, later, more specific wall — concord/deal/ipxref/queens now converge on ONE shared blocker (`&host`/`&features`/`&regions` keyword-introspection family, no natural referent in a natively-compiled program, needs a design call — not attempted); rsg/micsum/tgrlink each hit their own new distinct wall; geddump/micro unchanged (no dependency on anything touched). Full new blocker map + STEPS ladder in ICNBENCH above. Also ran `update_icon_bench_asm.sh`: `micsum.s` legitimately updated (honest output changed now that `open` compiles further; was already flagged STALE by the 06-23 handoff before this session). **Housekeeping:** this session's repos live at `/home/claude/work/{.github,corpus,SCRIP}`, not PLAN.md's canonical root-level `/home/claude/{...}` — caught mid-session, not worth a disruptive re-clone; `handoff_status.sh` auto-discovers correctly regardless (walks up from its own location), but any script with a hardcoded `/home/claude/...` default needs an explicit path override until a session clones at the canonical root.

Prior: **2026-07-02 (later session, Claude Sonnet 5) — SCRIP `e9677a1d` + `5c5697ab`: TWO RUNGS, corpus 210→211/42/36, audit 92→94/94 both modes.** (1) **ARG-SLOTS-UNBOUNDED + M4-TEXT-OPERAND-TRUNCATION `e9677a1d`:** `g_emit.op_arg_slot`'s fixed int[16] (three drive sites, three different guards — MAKE_LIST/CALL_VALUE loud-sink, CALL family SILENT TRUNCATE) now heap-grown via `drive_arg_slots_reserve`; `OP_ARG_SLOT_MAX` deleted. THE REAL FIND: mode-4 TEXT silently misread ANY staged-call frame offset ≥1000 — `bb_call_proc_staged` hand-built space-less `[r12+N]` operand strings owned by no `x86_parse` arm, falling to the terminal `[...]` fallback's 7-char base field (`r12+992` fits, `r12+1000` loses its last digit — every staged marshal past 1K read the wrong slot). Fixed: templates speak canonical `FRQ()`; `x86_parse`'s fallback now validates the base is a register and ABORTS LOUD on malformed operands instead of truncating. Probe 93 oracle-pinned FIRST. (2) **LVALUE-COLLAPSE increment 2 / LV-TOTAL `5c5697ab`** (closes the filed rung below): `lower_lvalue_var` now TOTAL — TT_FIELD via new `rt_field_var` (the `rt_subscript_var` record-arm sibling: `data_field_ptr` name→cell) and TT_NULL/TT_NONNULL (variable-transparent per canonical `ir_rval`, irgen.icn:459) added onto the identifier/IDX/section/bang/random front. TT_ASSIGN collapsed to {TT_VAR fast path, ONE generic lv→ASSIGN_VAR}; TT_AUGOP to {TT_VAR desugar, ONE rider} — nine ritual arms deleted (IDX, LV-1 section, LV-2/3b iterate, LV-3a random ×2, NULLTEST-LV, FIELD_SET, FIELD-AUGOP); β-delta wiring on both consumers (capture `cx->beta` before the front, aim rhs ω at whatever the front minted) inherits the bang re-pump generically — `every (!L).a +:= 100` pumps with zero bespoke code. UNION LESSON (two gdb-bracketed segfaults): `IR_LIT`'s `ival`/`sval` overlap — a flag clobbered a field name once, then a value-mode `ival` TT-code got read as a `sval` pointer once; kind-level opcodes (`IR_FIELD_VAR`, `IR_NULLTEST_VAR`) are the union-safe fix. `IR_FIELD_SET` now Icon-dead (joins the three dead call routes). Also hoisted the new `bb_unop` lv arm above the pre-existing `UO_UNHANDLED` silent-empty guard (untouched otherwise — a standing wart, not this rung's to fix). Probe 94 oracle-pinned FIRST. VERIFIED (both rungs): smoke 12/12×2 · 6 gates PASS · corpus 210/43/36→211/42/36 (`rung24_records_record_loop` FAIL→PASS, zero new fails, comm-diffed) · bench-asm 13/0/0/1/12 updated=0. **Open board:** coerce HANG rc=124 (likely ω/β wiring) · keyword-lvalue family (`&pos:=:&subject`, scan.icn) · `!` APPLY operator + variadic `a[]` (unblocks args.icn/geddump) · scan-call bucket (recogn/htprep/scan2) · dead-opcode cleanup (now four: `IR_CALL_BYNAME`/`GVAR_USERPROC`/`USERPROC`/`FIELD_SET`) · PARKED (no rt fixes, per standing directive): `subscript_get2` cvpos p≤0 off-by-one (mindfa's last blocker).**

Prior: **2026-07-02 (late session, Claude Fable 5) — SCRIP `84208eba`: FOUR PIPELINE RUNGS, corpus 208→210/43/36, audit 89→92/92 both modes.** (1) **AUGOP-LV:** TT_AUGOP's non-VAR fallthrough was a mint-and-abandon (IR_BINOP, ZERO pushes, no write-back — the record/wordcnt op=3 sink, bisected to `a.f1 +:= 10`; x[i]/s[i:j] augop equally dead). Field arm = shared-base FIELD_GET/FIELD_SET (base once, JCON ir_augmented_assignment order); generic arm = lower_lvalue_var → DEREF → BINOP → ASSIGN_VAR (LV-3a rider). Probe 90. **record FAIL→PASS**; wordcnt advanced (multi-blocker: sort/left/read + computed-cset scan). (2) **NULLTEST-LV:** `/x := v`, `\x := v` (canonical onull.r) — lower_lvalue_var → DEREF → UNOP_TEST → ASSIGN_VAR; probe 91. mindfa's guard cleared, full stdin now consumed. (3) **CONJ-JUNCTIONS:** `every q := !Q & a := !S` never re-pumped the left — post-hoc ω_to(val) only rewired the conjunct RESULT node; a wrapping conjunct leaves the inner generator's exhaust at outer ω. Each conjunct i>0 now lowered WITH a pre-minted IR_GOTO junction as its ω, patched to nearest-resumable-left's RESUME node (per-conjunct cx->beta, reset each). is_resumable += TT_ITERATE (REVASSIGN one-token class) + TT_SWAP recursion. Probe 92. **BONUS: rung13_alt_alt_filter FAIL→PASS.** (4) **LVALUE-COLLAPSE increment 1 + OPND-TMP-FALLBACK:** ITERATE/RANDOM lv mints relocated INTO lower_lvalue_var (bang writes cx->beta, random doesn't) — `every !x :=: ?x` oracle-exact both modes; emitter's descr_binop_opnd_slot falls back to the LOWER grant `o->tmp` on drive-order memo miss (ipxref gdb-bracketed: BINOP before its CALL operand, tmp=592 present yet aborting) — resolver change proven byte-identical FAIL set. Every rung: smoke 12/12×2 · 6 gates PASS · corpus comm-diff = exactly {record, alt_alt_filter}, ZERO new fails · bench-asm updated=0.
**BENCHMARK MAP (corpus/benchmarks/icon, fresh derive):** version RUNS · options/shuffle = mainless link-libraries · concord/queens/deal/ipxref/micsum → **LINK multi-file + Init__ harness** (one architecture rung) · geddump/args → **`!` APPLY operator** (parser/lower rung) · micro/rsg/post/tgrlink → collect/open/getenv/where builtins (rt). **FOUND+PARKED rt bug (session directive: no rt fixes):** subscript_get2's section position normalization for p≤0 is wrong — `s[1:-1]`→whole, `s[2:0]`→fail, `s[-3:-1]`→off-by-one vs canonical cvpos len+p+1 (oracle-probed); mindfa's last blocker.
**2026-07-02 (evening session, Claude Fable 5) — THREE RUNGS: SCRIP `5c70c612` + `a8a31b31` + `9cdac6ee`, corpus `c5dbca3c` — corpus 206/47/36 → 208/45/36, audit 87→89/89 both modes.** (1) **SWAP-LV `5c70c612`:** `x[i]:=:y[j]` / section swaps via classify-by-name `IR_SWAP_VAR` (plain×plain keeps the IR_SWAP frame fast path); `rt_swap_var` = canonical swap (oasgn.r:265) composed write-once from rt_deref+rt_assign_var with the adj1/adj2 same-string tvsubs position shift computed from ORIGINAL pos/len (ultimate-cell identity via new `vcell_ultimate`); result = fresh x-deref through the adjusted trap; new `lower_lvalue_var` shared front (identifier→VAR_REF, IDX→lower_idx_var, sections incl ±: desugar → the LV-1 sval="lv" shape); keywords (&pos:=:&subject, scan.icn) decline loud — keyword-lvalue family = own rung. Probe 88 oracle-pinned FIRST (adj2 shift `aedbcf`, int-into-splice `wxy20`, result-is-x-deref `q qp`). (2) **PROC-VALUE `a8a31b31` (the CALL-SHAPE architecture rung):** first-class procedures — `IR_PROC_VALUE` leaf (rt_proc_value mints DT_E{slen=0xFFFFFFFE,.s=name}, coexisting with proc()'s entry_pc DT_E) + `IR_CALL_VALUE` (operands[0]=callee producer; in ir_is_call_kind so the 1+n grant/op_ival ride free); `rt_call_value` = canonical invoke: int callee = 1-based arg selection (mutual-goal), name → the g_call_args+rt_call_proc_descr trampoline (registered procs, BOTH modes) else `rt_call_arr` (THE builtin door — script_try_call_builtin_by_name was the wrong entry, reverse echoed its arg); LOWER: per-proc DECLARED-name set on icx_t → TT_FNC routes declared-local/non-identifier callees by value; resolve-pass IR_VAR retag (¬param ∧ ¬assigned-in-graph [the drive-slot-assign interning set] ∧ ¬global ∧ [proc-table name incl. main | is_known ∪ is_generator ∪ {push,put}]); RT-REGISTRY truth for image/type/args DT_E arms + the call branch (g_stage2 is EMPTY in a mode-4 binary — first cut broke m4); mode-4 proc_startup now carries ARITY (new rt_proc_set_nparams beside set_fn; set_fn alone inserted nparams=0); `main` special-cased in the 3 consumers (registration skips main at all 6 driver sites by design, not perturbed). Probe 89 oracle-pinned FIRST (type/image/args ×user+builtin, by-value ×both, string invocation, ± int selection). rung37_coerce FAIL→PASS. (3) **NUMERIC-ARITH `9cdac6ee`:** two pointer-hole/pow faces — cset-op operands (CUNION/CDIFF/CINTER) coerce like rt_cset_compl (numeric's `100 -- 4` segfault, gdb-bracketed cset_diff(a=0x64,b=0x4)); LOWER const-folder int^int now folds with rt_ipow_descr's exact iipow ladder instead of C pow()-to-REAL (all edges iconx-pinned pre-patch; 0^neg left unfolded → runtime FAIL). FALLOUT: five rung19/26 pow expecteds encoded the OLD real-fold — probe-bad doctrine, each verified SCRIP==iconx then REGENERATED (corpus `c5dbca3c`). numeric FAIL→PASS (111/111 both modes). Every rung: audit clean sweep both modes · smoke 12/12×2 · 6 gates PASS · FAIL-set comm-diffed (zero unexplained flips) · bench-asm 13/0/0/1/12 updated=0. **Open board (re-censused this session):** coerce HANG rc=124 · args.icn IR_MAKE_LIST op=29 guard-sink (mint-and-abandon sibling?) · lists/proc_lookup clean-exit diffs · mathfunc math-builtin gap (asin/acos/atan/dtor/rtod unclassified AND unimplemented?) · var.icn name() builtin · recogn/htprep/scan2 full-arity scan-call bucket · open() ×3 · keyword-lvalue family (scan.icn swap) · record/wordcnt IR_BINOP n_operands=0 guard-sink (prior bracket stands) · bb_var_ref no-cell tvsubs bucket now 3 (queens/mutual/string) · prepro = $-preprocessor, reclassified OUT of bb_var to its own parser rung.**

**2026-07-02 (session, Claude Fable 5) — SCRIP `c634c79e`: ASSIGN-LV LV-3a LANDED — `?x` random-element lvalue end-to-end both modes: classify-by-name `IR_RANDOM` (JCON collapses `?` to opfn u_random/"Select"; SCRIP splits per JCON-ALIGNMENT — the enum insertion shifts later ordinals, pure slot arithmetic per the CONJ precedent) · `rt_random_var` rolls the canonical LCG ONCE per evaluation (RandA/RandC/RanScale from oref.r:216 + rmacros.h verbatim; state = `g_random`, keywords.c — the &random READ aligns for free, &random := reseed still unwired) and mints the LV VCELL family (string-under-variable tvsubs len=1 · list cell · record field · table nth-pair LAZY TRAP on the found key, canonical tvtbl) or plain values (cset via cset_resolve — the DT_S slen=0xFFFFFFFF sentinel guarded FIRST, before the string arms misread it as length · string-value char · `?n` int [1,n] · `?0` real; n<0 FAILs, canonical-runerr-205-vs-FAILDESCR divergence pinned) · LOWER: TT_RANDOM OUT of is_unop_tt (was bb_unop's UO_UNHANDLED SILENT no-op — a standing discipline wart, now dead for this TT) + three arms: rvalue (IR_VAR_REF identifier base → IR_RANDOM → IR_DEREF partner, the TT_IDX shape), TT_ASSIGN lv (LV-2 recipe MINUS the generator plumbing — `?` is operator{0,1}, single-shot, no cx->beta, no rhs-ω-backtrack), TT_AUGOP once-evaluated rider (LV-3b shape minus β — DEREF/BINOP/ASSIGN_VAR all read rn->tmp) · bb_random.cpp = bb_deref's exact shape, one call · grant k+=1 on the DEREF row · produces_value · 4 ω-follow walk sites · drive case mirrors IR_DEREF. METHOD NOTE: the LCG was verified byte-exact against iconx BEFORE any SCRIP code (sequenced C repro: 22/42/4/Lidx3/spos3/hpos2/0.0796… — first attempt used printf args and unspecified eval order scrambled it; sequence the calls). VERIFIED: probe 87 oracle-pinned 4-way (list/table-single-entry/record/string-tvsubs lv + augop rider + rvalues; multi-entry-table element identity is hash-order-dependent and NOT oracle-comparable — keep table forks single-entry) · audit 87/87 both modes · smoke 12/12×2 · 5 gates PASS (mutation HARD=0) · corpus 206/47/36 FAIL set byte-identical (stash/rebuild comm=0, ZERO flips — honest layer movement: record past `?b := 15` — its op=3 guard-sink GDB-BRACKETED this session: the emit.cpp:920 IR_BINOP slot guard fires on a node with **n_operands=0** (conditional break `sa<0||sb<0`; first :920 hit passes 720/736 — spin past it), i.e. a LOWER mint-and-abandon: some path yields an IR_BINOP with ZERO pushes (push has no NULL-guard, so zero means never called; every lower_icon.c mint site pushes same-frame — the site is NOT one of the six greppable `build(cx, IR_BINOP` lines nor the generic variable-kind arm at :185); **line-35 attribution FALSIFIED by minimal repro** (`b["f" || (1 to 3)]` standalone + no-every + no-subscript shrinks all PASS — the abort needs record.icn's fuller context or originates elsewhere); next move: at the conditional break, walk the graph for edges pointing AT the node / add per-site mint markers; lists into the pre-existing bb_var-arm bucket) · bench-asm 13/0/0/1/12 updated=0. Known divergence (pre-existing family): `?0` prints full precision vs Icon's 11-sig-digit real format — value identical. Open board: SWAP-LV (scout in prior watermark) · record's IR_BINOP guard-sink diagnosis · bb_var arm ×3(+lists) · CALL-SHAPE cluster (incl. args.icn `?`-as-call, a route distinct from TT_RANDOM) · pointer-hole architecture (Lon).**

Prior: **2026-07-02 (session, Claude Fable 5) — SCRIP `28d1e7e0`: ASSIGN-LV LV-2 + LV-3b LANDED (two commits) — iterate-lv `!x := v` (`11d26284`: `rt_list_bang_var_at`, the rt_subscript_var sibling — list cell / record field / table pair-val / string-tvsubs VCELL, DT_V base deref keeping bvar; LOWER TT_ASSIGN bang arm — IR_ITERATE `sval="lv"` element-VARIABLE producer into the existing IR_ASSIGN_VAR, identifier base → IR_VAR_REF, cx->beta=it before rhs, rhs ω→it auto-β, is_resumable bang token per the REVASSIGN lesson; bb_iterate one-call-swap lv arm; IR_ITERATE joined the walk-preamble op_sval whitelist — the clobber pattern's 4th sighting, caught preemptively) · augop-through-lv `!x OP:= v` (`28d1e7e0`: the once-evaluated-variable form — TT_AUGOP bang arm; DEREF reads old / BINOP folds / ASSIGN_VAR writes back, all reading it->tmp fresh per β-resume, generator never double-lowered; ZERO new opcodes, zero template/runtime edits). Fresh-sandbox baseline re-derived FIRST and matched the prior close exactly (icont 9.5.25a rebuilt from upload, refs/ symlinked, x64 cloned: audit 84/84 · corpus 206/47/36 · HARD=0). Post-rungs: audit 84→**86/86 both modes** (probes 85/86 oracle-pinned) · smoke 12/12×2 · 6 gates PASS (mutation HARD=0) · corpus 206/47/36 FAIL set byte-identical throughout (comm empty — ZERO flips, honest layer movement: table/substring past the guard into ordinary divergence; record's first-fatal now `?b := 15` = LV-3a) · bench-asm 13/0/0/1/12 updated=0 both commits. IR_SWAP scouted: the drive case (emit.cpp ~1090) is bb_varslot_peek(sval)-only (NAMED vars); string.icn swaps through SUBSCRIPT lvalues (`s[2] :=: s[3]`) → nameless guard — SWAP-LV rung = lv producers both sides + `rt_swap_var` deref/cross-assign, the LV recipe verbatim. Open board: LV-3a `?x` lv · SWAP-LV · computed-cset scan operands · pointer-hole architecture (Lon).**

Prior: **2026-07-02 (same session, Claude Fable 5) — SCRIP `035106f9`: ASSIGN-LV LV-1 LANDED — `s[i:j] := v` (and `s[i+:n] :=`, negatives, empty-splice insert) works end-to-end both modes, oracle-paired verbatim: `rt_section_var` (the :681 tvsubs sibling, subscript_get2's canonical normalization) · LOWER TT_ASSIGN section arm mirroring the rvalue arm incl. the synthetic-BINOP `+:`/`-:` desugar, `sval="lv"` selecting · bb_section lv arm (DT_FAIL→ω) · IR_SUBSCRIPT whitelisted in the walk-preamble op_sval re-derivation (the post-drive clobber had nulled the marker — the REV_ASSIGN clobber-pattern lesson, third sighting). Verified: 4-case oracle parity m3+m4 · smoke 12/12×2 · audit 84/84 · mutation PASS HARD=0 · no_slot_alloc PASS · corpus 206/47/36 FAIL set byte-identical (zero regressions; string.icn advanced one layer — next blocker IR_SWAP `s:=:t`, a construct NOT in the original map) · bench-asm 13/0/1/12 updated=0. Remaining in the rung: LV-2 iterate-lv · LV-3 riders · new: IR_SWAP drive/template (2-op, emit.cpp:1092 guard).**

Prior: **2026-07-02 (same session, Claude Fable 5) — SCRIP `858b6e8c`: ASSIGN-LV DIAGNOSIS LANDED — the FAIL-map's `emit_drive op=N` bucket was a GUARD-SINK MISLABEL, gdb-bracketed at emit.cpp:944 with the node in hand: LOWER's TT_ASSIGN terminal arm mints a NAMELESS 2-operand IR_ASSIGN placeholder for any lhs ∉ {VAR, IDX, FIELD}; operands[1]=IR_ITERATE for `!x := v` (lists/table/record/substring) and IR_SUBSCRIPT-3op for `s[i:j] := v` (string/mindfa) — both faces of the trapped-variable lvalue architecture (queens' tvsubs bomb, same family; `?x` and augop are riders). Emitter change MESSAGE-ONLY (precise :944 guard text + drive_unowned guard-sink note). CENSUS verified in source: `rt_assign_var` write-through COMPLETE (cell · table-trap · full canonical tvsubs-string splice); `rt_subscript_var` mints four VCELL shapes incl. single-char string tvsubs — the gaps are `rt_section_var` + iterate-lv producers + LOWER routing. LV-1..LV-3 ladder opened in the FAIL MAP section with per-program flip expectations. Exact-baseline verification: smoke 12/12×2 · mutation gate PASS HARD=0 · no_slot_alloc PASS · corpus 206/47/36 comm=0 · audit 84/84 · bench-asm 13/0/1/12 updated=0.**

Prior: **2026-07-02 (same session, Claude Fable 5) — SCRIP `545c3857`: IRM→0 LANDED, THE EMITTER NEVER MUTATES IR — gate HARD 4→0 PASS, CLOSED FOR GOOD (Lon directive). `resolve_call_kinds_descr` (the last four `->op` writes + a dead `if(NULL)` dval==2/3/5 tail) DELETED from emit.cpp; the decision moved to LOWER as `lower_icon_resolve_call_kinds` at the end of `lower_icon_stage2`: user-proc truth = `g_stage2.proc_table` via `icn_callable_proc_index` mirroring the driver's `rt_proc_register` declare-set exactly (named · not main · lowered graph with entry), generator bit = `proc_table[pi].is_generator` (the same value the driver stamps into rt), builtin sets = the static by_name_dispatch.c lists (`rt_builtin_is_known`'s registered-guard reachability-equivalent — table-callable names take branch 1/2 first); ladder + write/writes exclusion verbatim; four scrip.c call sites + emit.h decl deleted; gate [C] informational 14→10. VERIFIED: mutation gate PASS HARD=0 · smoke 12/12×2 · audit 84/84 both modes · corpus 206/47/36 FAIL set byte-identical (comm=0, session baseline) · gates icn×4 + no_slot_alloc PASS · bench-asm 13/0/1/12 updated=0 — byte-identical `.s`, identical ops reach the emitter, the proof the move is pure. From this watermark on, "mutation HARD=4 baseline" is history: the gate is a hard-zero prison. Open board: computed-cset scan operands · pointer-hole architecture (Lon) · the 47-FAIL corpus map (GOAL-ICON-FULL-PASS).**

Prior: **2026-07-02 (session, Claude Fable 5) — SCRIP `ad613052`: TE-4 VARSLOT ABSORPTION + TE-FENCE LANDED, TMP-ERADICATE COMPLETE — the emit-time varslot allocator and `g_flat_slot_count` (the THIRD counter, a0b3f410 collision family) are DELETED; LOWER owns the ENTIRE ζ-frame via `ir_drive_slot_assign` (params from `graph->pnames` at ABI-fixed 16*(i+1) · IR_ASSIGN/IR_REV_ASSIGN locals above the tmp region on the ONE counter · gen-proc suspend-resume cell as `graph->resume_slot` at the tmp high-water, the old per-chain carve's exact position); `bb_varslot_peek` is a pure read of `graph->vslots` through `g_emit_cfg`, drive arms + bb_call marshal/truthy abort LOUD on missing grants, `g_last_flat_frame_bytes` is now honestly published = `jcon_value_region` (previously NEVER written — frames rode the runtime arena default). Honest byte-churn only (gen-proc locals +8 to 16-alignment; main-chain locals above tmps), behavior-identical. VERIFIED FROM SCRATCH POST-FENCE: smoke 12/12×2 · audit 84/84 both modes · corpus 206/47/36 of 289 FAIL set byte-identical pre→post (comm=0) · gates icn×4 PASS · emit_no_slot_alloc PASS · mutation HARD=4 pre-existing baseline · bench-asm 13/0/1/12 updated=0 (exact baseline). ALSO this session: CVA continuation shape recorded + deferral reaffirmed (see the CVA section — Lon: major optimizations at the very end). Open board: computed-cset scan operands · pointer-hole architecture (Lon) · the 47-FAIL corpus map (GOAL-ICON-FULL-PASS).**

Prior: **2026-07-02 (same session, Claude Fable 5) — SCRIP `d671e68f`: TMP-ERADICATE TE-1/2/3 LANDED IN ONE SWEEP (Lon directive, scope widened to ALL LANGUAGES) — emit-time temporary allocation is ERADICATED: the four allocator symbols deleted repo-wide (defs/externs/21 reserve calls/decls), live refs 0 compiler-enforced, new gate `test_gate_emit_no_slot_alloc.sh` PASS 0. Grants added (call family 1+n_operands argv-at-tmp+16 · DEREF/ASSIGN_VAR/KEYWORD ·  CREATE k+=4); discovery method = gouge-the-allocator-and-read-the-abort (cheap, reusable). CORPUS WIN: rung08_strbuiltins_find FAIL→PASS (latent call-slot collision) — 206/47/36, zero new fails, FAIL set byte-identical across the sweep. Audit 84/84 both modes · smoke 12/12×2 · TE gate PASS · 4 gates PASS · mutation HARD=4 baseline · bench-asm honest-churn updated=1 (version.s call-slot layout). Remaining: TE-4 varslot cursor (+ gen-proc suspend-resume-slot, same bucket) · TE-FENCE. Open board: TE-4 · computed-cset scan operands · pointer-hole architecture (Lon).**

Prior: **2026-07-02 (session, Claude Fable 5) — SCRIP `c76ce21d`: IDX-UNIFY r1 tvsubs LANDED — IDX-UNIFY sub-rung ladder COMPLETE (r1-r4 all closed). `s[i]` is a string lvalue: `IR_VAR_REF` classify-by-name variable-reference producer (DT_V over the variable's cell, GVA/local lea arms, `bb_var_ref.cpp` + `rt_var_ref_cell`); DT_V flows through subscript chains (`rt_subscript_var` derefs DT_V bases internally per canonical subsc — between-level IR_DEREFs retired, `t[k][i]:=v` lvalue-correct via lazy ssvar); `VCELL_t`+`{sv,pos,len}`; rt_deref/rt_assign_var tvsubs arms per cnv.r:482/oasgn.r:345 (recursive write-back collapses canonical's type_case; trap-len update = revassign β-restore correctness). One wiring bug (nested TT_IDX base lost the variable through the rvalue DEREF wrapper) caught by probe 83, fixed by self-recursion. Fresh-sandbox baseline re-derived FIRST and matched the prior close exactly (icont 9.5.25a rebuilt from upload, refs/ symlinked, audit 81/81). Post-rung: audit 81→**84/84 both modes** (probes 82/83/84 oracle-pinned) · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (comm empty) · bench-asm 13/0/0/1/12 updated=0. **TMP-ERADICATE rung OPENED (Lon directive) with executed survey + TE-0..TE-FENCE ladder** — see its section; key findings: eradication half-landed (`ir_drive_slot_assign` + the drive_value_slot abort), survivors = 15 alloc16 + 14 claim sites (Icon-reachable core = the bb_call* argv family, TE-1), `ir_tmp_slot_assign{,_flat}` are DEAD, varslot cursor = the third counter (TE-4). Open board: TE-1 call-family grant · computed-cset scan operands · pointer-hole fix architecture (Lon).**

Prior: **2026-07-02 (new session, Claude Fable 5) — SCRIP `c34d4125`: IR_MOVE DELETED (Lon verdict) — RESERVED-SET RECONCILE CLOSED, all rows resolved. Tmp-doctrine absorption RATIFIED vs JCON ir_Move (gen_bc:220); only client copy_prop.c/.h (unexercised, zero live material) deleted wholesale with it (Makefile source-list + object rule, optimizer.c cp_run/stats arm); residual grep IR_MOVE|cp_run|copy_prop = 0, IR_MOVE_LABEL untouched (word-bounded census, exactly 3 sites). Fresh-sandbox baseline re-derived FIRST (icont 9.5.25a oracle rebuilt from upload, refs/ symlinked per RULES.md recipe, x64 cloned) and matched the prior close exactly before cutting. Audit 81/81 both modes · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (comm empty vs pre-rung capture) · bench-asm 13/0/1/12 updated=0. Open board: IDX-UNIFY r1 tvsubs · computed-cset scan operands · pointer-hole fix architecture (Lon).**

Prior: **2026-07-02 SESSION CLOSE (Claude Fable 5) — two rungs landed: IDX-UNIFY r2 subscript-revassign (SCRIP `fba88eae`, IR_REV_ASSIGN_VAR, probe 80) · TT_CSET_COMPL silent no-op killed (SCRIP `bf7f9392`, rt_cset_compl, probe 81). Audit 79→**81/81 both modes** · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical throughout · bench-asm 13/0/1/12 updated=0 every rung. CVA convert-for-arith ladder authored then **DEFERRED same day (Lon)** — held for the future typed/untyped + boxed/unboxed enhancement; its empirical finding (inline-arith POINTER HOLE, `"3"+2`→58996226) promoted to STANDING AUDIT TARGETS as a live bug independent of fix architecture. Findings also filed: scan boxes are literal-cset-only (own future rung); cset `\0`-universe divergence flagged. Open board: IR_MOVE verdict (Lon) · IDX-UNIFY r1 tvsubs · computed-cset scan operands · pointer-hole fix architecture (Lon).**

Prior: **2026-07-02 (session, Claude Fable 5, second rung) — SCRIP `bf7f9392`: TT_CSET_COMPL (`~e`) SILENT NO-OP KILLED — real IR_UNOP arm + `rt_cset_compl`; probe 81 oracle-pinned 4-way (membership, involution, `**`-composition; absolute-count assertions avoided per the flagged `\0`-universe divergence). FINDING goal-filed: scan boxes are literal-cset-only (computed-cset scan operands = own future rung; bare-call upto = pre-existing rung06 FAIL). Audit 80→**81/81 both modes** · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (comm empty) · bench-asm 13/0/1/12 updated=0. Session total 2 rungs (r2 subscript-revassign `fba88eae` + this). Next rung: Lon's call (IR_MOVE verdict; IDX-UNIFY r1 tvsubs; computed-cset scan operands now also on the board).**

Prior: **2026-07-02 (session, Claude Fable 5) — SCRIP `fba88eae`: IDX-UNIFY r2 LANDED — subscript-revassign `x[i] <- v` via `IR_REV_ASSIGN_VAR` (through-variable sibling of IR_REV_ASSIGN; IR_ASSIGN_VAR operand order; canonical rasgn on the phase-1 rt_deref/rt_assign_var rails; bb_rasgn.cpp's dormant pre-doctrine subscript arm deleted). Probe 80 oracle-pinned 4-way incl. the absent-key restore fork (key stays PRESENT at default, `*u`=1). One in-session splice bug (emit_drive insertion ate `case IR_GOTO:`, loop family op=20 FATAL) found by the audit and fixed with full re-verify. Audit 79→**80/80 both modes** · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (stash comm empty) · bench-asm 13/0/1/12 updated=0. Next rung: Lon's call (IR_MOVE verdict; IDX-UNIFY r1 tvsubs).**

**Prior sessions (2026-07-02, chronological — gate baseline throughout: smoke 12/12x2, mutation HARD=4, all 4 discipline gates PASS):** r10 dead-courier deletion (`2ae6155d`) - IDX-UNIFY r3+r4 closed (`df46db00`) - CLOBBER-PATTERN audit, 2 live bugs (`dde4e9fd`) - IDX-UNIFY phase 1 (`264c3994`) - IR_SEQ_EXPR->IR_CONJUNCTION rename (`46c1923a`) - CONJ-RENAME 4 commits (`87ab07c4`) - TO-SPLIT/IR_MAKE_LIST/IR_RESUME_VALUE-deleted session (`ed0ac777`) - slot-collision/unop-else/loop-restamp/renames session (`65f8c32e`). Corpus climbed 190->194->200->205 across these; audit climbed 66->79. Full detail: `git log`.

### Landed history (compressed 2026-07-01 per RULES.md "DELETE completed steps" — full narratives in `git log` + `.github/HANDOFF-2026-0*.md`)
- **Foundations (06-30):** CONVERSION PLAYBOOK + `TT_EVERY` keystone · IR_ref_t α/β edge-stamp (`bb70a841`) · ICON-ONLY hard rules · `IR_ALT` deleted repo-wide (alternation = pure threading) · repeat/break/next via the IR_CONJ loop-back idiom · unop operand-push fix (`2d2b1ec8`) · universal `op_sval`/`gva_index_of` segfault fixed (`baa3a592`) · GVA-FLAT global assign (`feab99c7`) + slot-collision fixes (`024abd2f`, `d225d4a2`) · the every/TO/TO_BY regression cycle — fixed at HEAD, oracle-confirmed · scan-builtin opcodes TAB/MOVE/UPTO/ANY/MANY/FIND/MATCH/POS/BAL · IR_FIELD_SET / IR_PROC_GEN / IR_SUSPEND incl. binary-mode resume slots (`44c0da…`) · TT_IDX/MAKELIST union-clobber fixed (`8e296381`).
- **Opcode hygiene (07-01):** IR_TERNOP→IR_SECTION · IR_SUBSCRIPT / IR_GOTO / IR_NOT / IR_*_GENERIC deleted · four-opcode can-fail grid (IR_UNOP / IR_UNOP_TEST / IR_BINOP / IR_BINOP_TEST; the `_GEN` axis REJECTED per the DIVISION RULE) · `=s` desugared to `tab(match(s))` per `omisc.r:84` · prove_lower retired.
- **OPTIMIZER stage (07-01, `18a3440e`):** `src/optimizer/` between LOWER and EMITTER, `SCRIP_OPT`-gated OFF; branch_chain + copy_prop built (open items → PUNCH LIST standing targets).
- **Co-expressions (07-01, RUNGs 1-5):** create/coret/cofail pthread+semaphore model (`rt_coexpr.c`), `@` activation end-to-end both modes; three bring-up bugs gdb-bracketed (uninitialized create fields, bb_create k=5 clobber of the staged body-entry, coret γ→chain-default).
- **Label-variable infra (07-01, `dc45d9e2`):** IR_INDIRECT_GOTO re-added + IR_MOVE_LABEL; ig-owned shared 32-byte cell (value + `t`), t0-port sibling-label LEA; unbounded alternation `every write(1|2|3)` → `1 2 3`; corpus exactly +9; also fixed literal-arm ω-cascade discoverability and runtime-failing-arm0 value convergence.
- **Wholesale audit (07-01):** 66-probe icont-oracle instrument built · csetlit/&line/&pos/LIMIT (9 root causes) → 60/66 · initial + lconcat → 62/66 · repalt (`7edb9b9a`: `flat_drive_repalt` built — the phantom exorcised — + three β-mis-stamp PRODUCE-edge fixes + IR_REPALT `k+=2` grant) → 63/66 · if_value_else → **64/66** (SCRIP `6a509382`).
## ⛔⛔ WHOLESALE FROM-SCRATCH VERIFICATION — the executable audit + first fix ladder (Claude Sonnet, 2026-07-01, continuation session)

**Lon's directive verbatim-in-spirit: "do not trust any of it. We need to start the list from scratch and run through a one by one verification step. We are missing and are doing some thing wrong."** This session built the from-scratch list as an EXECUTABLE instrument, ran it, and fixed the first 4 construct families it caught (9 distinct root causes). The instrument is the head start for every future rung AND for the other-language LOWER/EMITTER rewrites.

### THE TECHNIQUE — what, where, when, why, how
- **WHERE:** `SCRIP/scripts/audit_jcon_wholesale.sh` + `SCRIP/test/icon/jcon_audit/NN_name.{icn,.expected}` (66 probes).
- **WHAT:** one minimal probe per JCON `ir_a_*` (all 43 — count re-derived fresh by `grep '^procedure ir_a_' refs/jcon-master/tran/irgen.icn`, matching the prior session's corrected 43; CoexpList excluded, JCON itself punts) plus SCRIP-specific TT extras (swap, revassign, augop, lconcat, scan suite, seq_expr, &pos, string subscript). Each probe runs **4-way**: canonical **icont/iconx ORACLE** vs hand-derived **EXPECTED** vs **MODE-3** vs **MODE-4**. Truth = oracle output when the oracle compiles the probe, else expected; oracle≠expected ⇒ **PROBE-BAD** (the probe is wrong, not SCRIP).
- **WHY the oracle:** hand-expected values drift and encode the author's misconceptions. The oracle caught TWO probe-suite bugs before they could masquerade as SCRIP bugs: (a) declarations joined with `;` — declarations are not statements, rejected by SCRIP AND standard Icon; use a NEWLINE between `end`/`global`/`record`/`invocable` and the next declaration (statements inside bodies stay `;`-separated for SCRIP); (b) icont flag order is `icont -s -o OUT FILE`.
- **HOW to build the oracle:** `cd <icon-master> && make Configure name=linux && make` → `bin/icont`,`bin/iconx` (this session: the uploaded `2-icon-master.zip`, extracted at `/home/claude/workspace/refs-src/icon-master`; a backgrounded make stalled at src/common — foreground retry completed in ~2 min). Harness auto-probes that path + `SCRIP/refs/icon-master/bin/icont`; override with `ICONT=`.
- **HOW to run/extend:** `bash scripts/audit_jcon_wholesale.sh [name-filter]`. To extend: drop `NN_name.icn` + `NN_name.expected` in the audit dir. Verdicts: OK / M3-or-M4 BAD / HANG / CRASH / NOASM (--compile aborted) / NOCC (gcc failed) / PROBE-BAD.
- **WHEN:** per-rung, before AND after — it is cheap (~40s), per-construct, and oracle-anchored, unlike the corpus (feature-rung-organized) and smoke (12 fixtures) suites.

### THE CLOBBER PATTERN — systemic, now named (~~audit target for next session~~ **EXECUTED 2026-07-02, SCRIP `dde4e9fd` — see the struck STANDING AUDIT TARGETS entry for the findings record; the technique below stays for the other-language rewrites**)
`DRIVE_FILL` order is: emit_drive stages `g_emit.*` → `walk_bb_node` RE-DERIVES `op_sval`/`op_ival`/`op_stno`/`op_dval` from the node → template reads. **Any emit_drive staging of those four fields for an opcode outside walk's derivation lists is silently discarded.** Two instances found this session (CHARSET sval, LIMIT ival). NEXT-SESSION AUDIT: diff every `g_emit.op_{sval,ival,dval}` assignment inside emit_drive cases against walk_bb_node's preamble lists; each mismatch is a live or latent bug of this class.


**Status + remaining ladder: single source = the Watermark and the PUNCH LIST above; ground truth = the harness itself.**


## RUNG — LANG-GLOBAL ERADICATION (declared 2026-07-03 by Lon; COMPLETE 2026-07-04 — all three increments landed; whole-tree grep for LANG_/:lang/IR_LANG_ = 0)
DOCTRINE (FACT, mirrored in RULES.md): language-specific code is for PARSER and LOWER — they KNOW their language implicitly, so there is no reason for ANY global/enum/attribute that says which language is being processed. EMITTER and TEMPLATES are past language and into PLATFORM: they may condition ONLY on the IR graph (op kinds, operands, payloads, edge stamps) and platform state. Sorry Charlie — no LANG for you in the later stages of SCRIP.
PREVENTION IS BY VISIBILITY, NOT DISCIPLINE: language is a variable at exactly ONE place — FIRST DISPATCH, where the driver reads the extension/fence-tag string and selects which frontend parses and which lowerer lowers. After first dispatch NO language token exists — not a global, not an enum, not a :lang AST attr, not a ".icn"/".sno" sentinel argument passed into LOWER. Each parser and each lowerer knows who it is by BEING that source. Removed = prevented forever.
STEPS:
1. ~~INVENTORY~~ DONE (2026-07-03): whole-tree grep classified every site. Two enums found: LANG_* (frontend, scrip_cc.h) and IR_LANG_* (spine, IR.h). PIVOTAL RESULT — emitter + all 180 templates read NEITHER enum NOR ->lang in ANY form; the ONLY emitter/template language access was one dead global read (g_lang in xa_file_header). IR_LANG_* proved diagnostic-only (its sole reader was a lang_names[] debug print). Both g_lang readers were dead: the xa_file_header path baked a call to rt_set_lang, which has NO definition anywhere in the tree, and the runtime NO_AST_WALK_GUARD sat behind g_sm_dispatch_active which is initialized 0 and never set.
2. ~~EXCISE + PREVENT (Increment 1 — dead globals)~~ LANDED (2026-07-03), verified Icon 12/12 ×2 + SNOBOL4 4/3 ×2: deleted g_lang (defn/extern/setter), the rt_set_lang emission in xa_file_header (kept rt_gc_init + rt_register_expressions in the main: prologue), and the inert NO_AST_WALK_GUARD macro + g_sm_dispatch_active/g_ast_pump_active flags + its driver_call.c call site. 0 hits each.
3. ~~EXCISE + PREVENT (Increment 2 — IR-spine enum)~~ LANDED (2026-07-03), verified Icon 12/12 ×2 + SNOBOL4 4/3 ×2: deleted the IR_LANG_* enum (7 #defines), the IR_graph_t.lang and stage2_t.lang fields (both write-only), the lang param on IR_alloc and lc_arg_block (~20 call sites updated), and the lang_names[] diagnostic in bb_print_v. 0 hits for IR_LANG_ / bbg->lang / g_stage2.lang.
4. ~~GATE~~ LANDED (2026-07-03): scripts/test_gate_emit_no_lang.sh — identifier-scoped (strips comments + string literals so "Icon-only reset" diagnostics and dormant-backend "Snobol4.Runtime"/"java/lang" output strings are NOT flagged), bans g_lang/rt_set_lang/LANG_/IR_LANG_/is_<language>/->lang in src/emitter + src/templates. Verified: PASSES clean, CATCHES an injected g_lang. Wire beside the smoke gates.
5. ~~EXCISE + PREVENT (Increment 3 — frontend LANG_* enum + :lang attr)~~ LANDED (2026-07-04), verified Icon 12/12 ×2 + SNOBOL4 4/3 ×2 + corpus 210/43/36 byte-identical. Original spec follows for the record; ImportEntry.lang (parser-side FFI string, icn_main.c) left in place as out-of-spec. This is the only LIVE, load-bearing use: the driver's polyglot router (polyglot.c, ~21 sites) + lower_common's mask dispatch + lower_prolog's :lang filter + lower_snobol4's mask guard, sourced from parser :lang stamps. It is ATOMIC (writers in the 5 parsers + readers in driver/lower must change together; no independently-green half). ARCHITECTURE (per Lon, 2026-07-03): (a) route to the SPECIFIC lowerer at FIRST DISPATCH from the driver's extension-derived locals — retire the generic mask-dispatch lower_stage2; (b) MOVE polyglot_init's per-language setup (module segmentation, Icon/Raku/Pascal frame reset, Prolog atom/trail init, per-language proc-registration conventions) INTO each lowerer, which knows who it is; (c) where lowerers share a helper that must differ, name the difference behaviorally (e.g. "arity from child param-list node" vs "arity from ival") and call variants — never branch on a language token; (d) delete :lang from the parsers + the STMT_t.lang/ScripModule.lang fields + scrip_cc.h's LANG_*. NOTE: the mixed-.scrip path is GZ#5-broken at baseline (cross_lang.scrip et al. abort in drive_value_slot, same as the SNOBOL smoke fails), so it is NOT a regression gate; the invariants are Icon smoke 12/12 ×2 and SNOBOL4 4/3 ×2 (both single-language, both through the same dispatch). Do this as its own unit with those two smokes as the oracle.
WATERMARK 2026-07-03 (this session): emitter + templates now PROVABLY language-blind — g_lang, rt_set_lang, and the entire IR_LANG_* enum + graph/stage2 lang fields deleted; test_gate_emit_no_lang.sh green and catching injections; Icon 12/12 ×2 and SNOBOL4 4/3 ×2 held across both increments. The blind-emitter doctrine is now enforced by a gate, not just observed. Remaining: the frontend LANG_*/:lang eradication (Increment 3, step 5 above).
WATERMARK 2026-07-04 (Increment 3 + POLYGLOT, Lon directives 2026-07-04): LANG-GLOBAL ERADICATION COMPLETE — LANG_* enum, :lang attr (5 parsers, .y AND .tab.c), STMT_t.lang (+ prolog/rebus writers, stmt_ast converter), ScripModule.lang, lower_snobol4 mask guard, lower_prolog :lang filter, polyglot_lang_mask, and the mask-dispatch lower_stage2 are DELETED; whole-tree grep = 0. Architecture landed in the same unit: FIRST DISPATCH is now PER-FILE (extension string) and PER-FENCE (tag string), each producing a lower_seg_t {prog, fn} (contract in stage2.h); sm_preamble(ast_prog, segs, nsegs) does stage2_reset + polyglot_init(merged) ONCE UNCONDITIONALLY (init-all for every language regardless of input — verified g_fi8 counters == 1), then runs each segment through ITS OWN lowerer into the shared g_stage2; per-language registration (modules via blind polyglot_module_open/extend, Icon/Pascal/Raku globals+records+procs, Prolog pred inserts, SNO label counts) lives INSIDE each lowerer; the five entries are unified as stage2_t *lower_X_stage2(const tree_t*).
WATERMARK 2026-07-04 (POLYGLOT RUN-TOGETHER landed, Lon directive): all 5 REAL lowerers now compile into BOTH artifacts — RT_PIC_SRCS swapped lower_noicon_stubs.c/rt_noicon_stubs.c (files DELETED; bb_gather/mapgrep_prepare had zero callers) for lower_prolog/raku/pascal.c + parser/prolog/prolog_lower.c + parser/rebus/rebus_lower.c. SNOBOL4+Icon+Prolog load and run TOGETHER in one process, BOTH as three files (scrip a.sno b.icn c.pl) and as one .scrip with three fences; sno→icon cross-language call proven in mode-3 AND mode-4 (DOUBLE(21)=42); prolog preds registered+resolvable in shared stage2 (nmod=3, likes/2 lookup non-NULL, g_resolve_active=1). NEW HARD GATE: scripts/test_smoke_polyglot.sh (tri-file + tri-fence, both modes, 4/4). Two driver record passes (icn_register_record_types + inline clone) walked all graphs reading IR_OP_COUNT payloads as sval — IR_t payload is an anonymous UNION, prolog ival=1 read as sval=0x1 => segfault; PROVEN no-op on Icon (lower_icon.c creates zero IR_OP_COUNT nodes) and deleted. is_sno_bb dropped !has_non_sno (no-mixing era over) and gained is_scrip. cross_lang.scrip remains blocked on RL-5/6 patterns + Prolog run semantics — it now fails EARLY + HONEST at the sno subset guard through the correct per-fence lowerer (baseline: deep drive_value_slot abort). Standalone .pl still parks at its GZ#5 driver message (untouched). Gates: Icon 12/12 ×2, SNOBOL4 4/3 ×2, emit_no_lang PASS, emit_no_ir_mutation PASS, corpus 210/43/36 byte-identical.
WATERMARK 2026-07-03 (SNOBOL4 GZ#5 rung 1 landed earlier): a SECOND language runs end-to-end on the shared emitter with ZERO language-conditionals in emitter or templates — sno rides the NV arms of bb_var_global/bb_assign_global via is_global() + gva-inactive, m3+m4 oracle-exact. Details: GOAL-SNOBOL4-BB.md.
WATERMARK 2026-07-04 (SN4-PAT-2 landed, Lon design directive mid-rung): SNOBOL4 PATTERN MATCHING IS LIVE for the LEN(n) subset — `L LEN(3) . X` → abc and bare `LEN :S/F` both paths, m3==m4==SPITBOL oracle; corpus m3 115→117 with the m4 FAIL set stash-verified byte-identical. THE DESIGN: ONE β-resuming generator box (IR_MATCH_HEAD, generator-kind) replaced the 3-box HEAD/RETRY/ADVANCE harness mid-rung on Lon's call — the unanchored retry loop IS Byrd β-resume (bb_to.cpp shape: α=rt_match_enter+start=0, β=start+=1/Δ-bound/g_anchor-gate), pattern-fail edges β-stamp via sno_ω_to, fJ reachability free from the stock generator-kind ω rule, zero chain-BFS special-casing. This is the composition template for every remaining matcher: leaves are one-shot γ/ω boxes; multi-shot elements (ARB/ARBNO/ALT) are β-resuming generator-kind boxes; CAT telescopes failure leftward through β. rt_match_enter is STATELESS (no scan-stack, no leave box) and sets Σ/Σlen so rt_cap_assign_cursor works unchanged. bb_match_retry/advance restored to pre-session bytes, dead. Next: SN4-PAT-3 (LIT, then the tracker order), the `= REPL` splice, and the phase-0 SAVE arm when CAT lands multi-element captures.


## SNOBOL4 RE-LIGHT LADDER — SNOBOL4 on the post-GZ#5 spine (RELOCATED here from GOAL-SNOBOL4-BB.md, Lon directive 2026-07-04)

**RELOCATION NOTE (2026-07-04).** This is the SNOBOL4-subset re-light ladder (RL-0…RL-9). It was moved here from GOAL-SNOBOL4-BB.md because that file is titled *"SNOBOL4 on the shared BB spine (GZ#5 rebuild)"* — it IS Ground Zero #5 work, and THIS file is the GZ#5 home. The move consolidates the live SNOBOL4 climb with the rest of GZ#5 rather than cross-referencing it.
- **SCOPE FLAG for Lon (NOT silently resolved):** the ICON-ONLY HARD RULE at the top of this file is Icon-climb-scoped — it constrains which `lower_*.c` and which tests the *Icon* rungs may touch. It does not, by itself, govern this relocated SNOBOL4 ladder, so the two now coexist. If you want one unified scope, reconcile that hard rule (e.g. re-title it "Icon-climb scope" or add an explicit SNOBOL4-climb carve-out). Flagged here rather than changed on my own initiative.
- GOAL-SNOBOL4-BB.md **retains** all SNOBOL4-specific detail (monitor RUNG-0/1/2, DEMO-PAT, NRG, PERF-GVA, fail maps); ONLY the RL ladder moved. A breadcrumb there points back here.
- The ladder assumes GOAL-SNOBOL4-BB.md's **"ONE EMITTER FOR ALL LANGUAGES"** FACT RULE (Lon, 2026-07-03; mirrored in RULES.md) — referenced below as "the ONE-EMITTER FACT RULE".
- PLAN.md's SNOBOL4-BB row still points at GOAL-SNOBOL4-BB.md (left as-is per RULES.md "do not edit PLAN.md goals table on routine handoff"); update it to point here if/when you want.

### THE RE-LIGHT LADDER — SNOBOL4 on the post-GZ#5 spine (Lon pivot 2026-07-03, session 31)
**Ground truth (session 31, live-run — NOT inferred):** crosscheck `--run PASS=5 FAIL=256`, `--compile SKIP=261` (every compile aborts in the gvar_* GROUND-ZERO stubs; the 5 "passes" are vacuous — aborted runs with empty stdout matching empty/whitespace refs; TRUE BASELINE = 0). The RUNG-1 fail-set numbers below (PASS 159/179, FAIL 76, DIVERGE 22) are PRE-RESET and STALE — do not chase them. `lower_snobol4.c` compiles but is GUTTED: node kinds mass-replaced with the `IR_OP_COUNT` sentinel (`--dump-ir` shows them as `IR_UNKNOWN`); REM/ARB/FENCE/ABORT/BAL, TT_NUL, seq/def-call minting — all placeholders.
**Constraint (Lon directives 2026-07-03): NO NEW IR — `IR_e` is FROZEN AGAINST ADDITIONS for this entire first climb; deleting UNUSED ops is DIRECTED, not forbidden.** **[CARVE-OUT 2026-07-04, Lon-authorized: the `IR_KEYWORD` → `IR_KEYWORD_ICON`/`IR_KEYWORD_SNOBOL4` split IS permitted against this freeze (enum +1). Rationale: as the emitter loses its language global (LANG-eradication), a single name-dispatched keyword BB over one case-fold `kw_read` table cannot distinguish `&LCASE`(SNOBOL4) from `&lcase`(Icon) — the two keyword SETS are different and the distinction must live in the opcode. This is the classify-by-name doctrine, not a rung that "needs" a new op by accident. Do NOT re-merge these to "restore" the freeze.]** The never-minted sweep landed same day: full 63-op audit (mint-count per op across lower/parser/driver/runtime/optimizer/machine) found EXACTLY THREE never-minted ops — `IR_CALL_BYNAME`, `IR_CALL_USERPROC`, `IR_CALL_GVAR_USERPROC` — all three DELETED (enum members, scrip_ir.c name rows + case-list, emit.cpp case-lists, proc_collect.c case-list, bb_call.cpp staged-predicate) → **enum now 60 ops + sentinel; the GVAR name left the IR enum by deletion, no rename needed** (by-name call routing lives at emit time in `bb_call_route_classify`'s `CALL_ROUTE_*` over `IR_CALL`, where it belongs). Kind numbers shifted −3 past the CALL block — symbolic names are the anchor (RL-1's recorded "op=29" is pre-shift). Deletion gates: build ×2 green, Icon smoke 12/12 ×2, Icon corpus 209/44/36 exact, crosscheck counts unchanged, kind-residue grep = 0 repo-wide. The vocabulary that implements all of Icon is the vocabulary; it covers a large portion of SNOBOL4. The known delta is addressing (GST(NV)+GVA vs GVA-only, per the ONE-EMITTER FACT RULE), not opcodes. If a rung appears to need a new opcode, the rung is wrong — find the existing-vocabulary lowering or park the program and note it here.
**Method:** STATIC-FIRST → ONE STAB → THEN MONITOR (unchanged). Rung supply = `test_crosscheck_snobol4.sh` (261 programs, category dirs under `corpus/crosscheck/`). Every rung gated on: both modes, `.ref` byte-match, DIVERGE=0, zero regression of previously-green categories.
**SESSION 31 CLOSE (2026-07-03) — ▶ NEXT SESSION START AT RL-2.** Landed: emit_chain consolidation (the ONE-EMITTER FACT RULE), RL-0/RL-1, unused-IR sweep (enum 60). RL-2 opening moves in order: (1) `scrip.c:609` — route SNOBOL4 through `ir_drive_slot_assign` (TMP-ERADICATE grants) instead of legacy `ir_tmp_slot_assign`; (2) mode-4 SNOBOL4 branch: replace the `gva_collect_graph` stub call with zero-collect (GST(NV)-first — n_gva=0, names ride NV) or a real collector — Lon's call; (3) re-lower assignment+OUTPUT in `lower_snobol4.c` onto `IR_ASSIGN`/NV (DT_N NAMEVAL association prints), replacing the IR_OP_COUNT placeholders. Gate: `hello/`, `output/`, `assign/` green both modes, zero Icon regression (209/44/36 anchor).
### Steps
- [x] **RL-0 — baseline recorded.**
- [x] **RL-1 — driver reroute onto the one emitter.** `scrip.c:609/612` now routes SNOBOL4 through `ir_drive_slot_assign` (was legacy `ir_tmp_slot_assign`). Dormant-arm template files are KEPT (may be reused later) — future re-light happens by LOWERING onto live kinds, never by resurrecting per-language emitter paths.
- [x] **RL-2 — re-lower assignment + OUTPUT.** `hello/` 4/4, `assign/` 8/8, `output/` 7/8 (the one fail, `&ALPHABET` keyword read, belongs to RL-8).
- [ ] **RL-3 — concat + arith.** Value concat, `IR_BINOP`/`IR_UNOP`/`IR_BINOP_TEST`/`IR_UNOP_TEST`, `IR_LIT_*`. Gate: `concat/`, `arith/`, `arith_new/` green.
- [~] **RL-4 — statement control flow.** END-GOTO LANDED (2026-07-04, this session, `src/lower/lower_snobol4.c` +1 line, local/unpushed): `:(END)`/`:S(END)`/`:F(END)` now resolve — `END` (SNOBOL4's reserved terminator, so no user label can collide) is registered as a label pointing at the program-exit `IR_SUCCEED` node (`bb_label_registry_add(lp_strdup("END"), exitnd)` after the label-registry loop). Was: `sno_resolve_label("END")` failed because END is the `:end` terminal, never registered. **MEASURED +24 both modes** (crosscheck mode-3 41→65, mode-4 40→64, DIVERGE=0; Icon smoke 12/12 ×2 unchanged) — END-goto is a pervasive exit idiom, so it was the SOLE remaining blocker for ~24 otherwise-in-subset programs. REMAINING for RL-4: the `:S()/:F()` forms that branch on a **pattern-match** result (`X 'lit' :S(L)F(L)`, e.g. control_new 033/034/035) — those need the IR_MATCH_* family and are really RL-5. Non-pattern control flow is now green.
- [ ] **RL-5 — primitive patterns onto the SCAN family.** Candidate mapping (verify per-rung vs SPITBOL semantics, manual Ch. 4/6): literal→`IR_SCAN_MATCH`, ANY/NOTANY→`IR_SCAN_ANY`, SPAN/BREAK→`IR_SCAN_MANY`/`IR_SCAN_UPTO`, LEN→`IR_SCAN_MOVE`, POS/RPOS→`IR_SCAN_POS`, TAB/RTAB→`IR_SCAN_TAB`, BAL→`IR_SCAN_BAL`, find-forms→`IR_SCAN_FIND`, all inside `IR_SCAN_ENTER`/`IR_SCAN`. Gate: `patterns/` subset without alternation/capture.
- [ ] **RL-6 — alternation, backtrack, capture.** Four-port ω-wiring (`IR_REPALT`, β re-entry), `.`/`$` capture. Gate: remaining `patterns/`, `capture/`.
- [ ] **RL-7 — DEFINE + user functions.** `IR_CALL_BYNAME`/`IR_CALL_USERPROC`/`IR_RETURN` (+FRETURN/NRETURN semantics on ω/γ). Gate: `functions/` green.
- [ ] **RL-8 — indirection, aggregates, keywords.** `$X` (NV by computed name), ARRAY/TABLE via `IR_SUBSCRIPT`/`IR_MAKE_LIST`/`IR_FIELD_*`, `&`-keywords via `IR_KEYWORD`. Gate: `data/`, `keywords/`, `strings/`, `library/`.
- [ ] **RL-9 — full-suite green + stale-section purge.** Crosscheck FAIL=0 both modes, DIVERGE=0; then (Lon approval) delete the superseded pre-reset sections below.

### SNOBOL4 RE-LIGHT — WATERMARK 2026-07-04 (re-derived baseline + END-goto landing; Claude Opus 4.8)
**Re-derived HEAD `0831f2a5` baseline (the session-31 "TRUE BASELINE=0" is long stale — much landed via SNOBOL4-GZ#5-rung-1).** Full `test_crosscheck_snobol4.sh` at HEAD: **mode-3 41/261, mode-4 40/261 (SKIP 221 = `--compile` aborts on the same feature gaps; mode-4 tracks mode-3, DIVERGE=0)**. Per-category mode-3 (the rung supply, biggest first): patterns 1/92 · strings 4/17 · keywords 0/12 · rung9 0/10 · rung10 0/9 · functions 0/8 · rung8/rung11/capture 0/7 · data 0/6 · rung4/rungW05/rungW07 0/5 · control_new 3/7 · arith 0/2 · output 7/8 · GREEN: hello 4/4, concat 6/6, assign 8/8, arith_new 8/8.
**Landed 2026-07-04 (END-goto, on origin `a1a3b404`):** END-goto (RL-4 slice) → mode-3 65/261, mode-4 64/261. One line in `lower_snobol4.c`; zero new IR; zero emitter touch.
**Landed 2026-07-04 (STRING-BUILTIN REGISTRATION, this session — blocker-map item 4):** `SUBSTR`/`REVERSE`/`LPAD`/`RPAD`/`INTEGER` were bombing `bb_call: unsupported call shape` purely because they were absent from `rt_builtin_is_known`'s `known[]` (so `bb_call_route_classify` fell to CALL_ROUTE_FATAL). All five already had runtime impls (`SUBSTR_fn`/`REVERS_fn`/`lpad_fn`/`rpad_fn` in `string_builtins.c`); the emitter's CALL_ROUTE_FN path (`bb_call_fn_str`) is fully generic (marshals args, calls `rt_call_arr(name, args, nargs)` — passes the name as a runtime string, stays language-blind). FIX = two pure additions, no new IR, runtime-only: (1) five names → `known[]`; (2) five dispatch arms in `try_call_builtin_by_name` calling the existing `*_fn` (INTEGER is a SPITBOL predicate → NULVCL success / FAILDESCR fail, mirroring IDENT/DIFFER; 2-arg LPAD/RPAD/SUBSTR defaults handled). **MEASURED: crosscheck mode-3 65→76, mode-4 64→75, DIVERGE=0** (strings 4→9, rung8 3→6, rung9 7→8 by category sweep — the builtins are cross-category; every other category byte-identical, zero regression). Both modes verified oracle-exact on all five; Icon smoke 12/12 ×2 held (emitter/templates untouched, so mutation + no-lang gates unaffected). **HANDOFF: codegen output changed for SNOBOL4 programs calling these (they now emit `call rt_call_arr` instead of aborting), so run the `util_regen_*_s_artifacts.sh` set before commit per RULES.md step 4.**
**Landed 2026-07-04 (KEYWORD-READ + DATATYPE, this session — blocker-map item 2 partial):** `lower_snobol4.c` bombed `tree kind 6` (= `TT_KEYWORD`) on every keyword read. FIX = three localized changes, no new IR, no emitter/template touch: (1) `case TT_KEYWORD` in `sx_lower` → `IR_KEYWORD` (mirrors Icon's `lc_key`; the emitter's `bb_keyword` generic tail already calls `rt_keyword_read`); (2) `rt_keyword_read` now case-folds the keyword id before `kw_read` — SNOBOL4 keyword tokens are UPPERCASE `&`-stripped (`(TT_KEYWORD ALPHABET)` per `--dump-ast`) while `kw_read`'s keys are all lowercase (Icon-style); folding unifies both frontends, Icon unaffected; (3) `&alphabet` aliased to the 256-char `&cset` in `kw_read` (SPITBOL's name for the full set). Also registered `DATATYPE` = the existing lowercase `type` builtin (identical lowercase output; one `known[]` entry + widened the `type` arm condition). **MEASURED: crosscheck mode-3 76→83, mode-4 75→82, DIVERGE=0** (keywords 6→8, output 7→8, rung8 6→7, rung9 8→9, strings 9→11; every other category byte-identical, zero regression). 097_keyword_alphabet (`SIZE(&ALPHABET/&UCASE/&LCASE)`=256/26/26) + 081_builtin_datatype both modes oracle-exact; Icon smoke 12/12 ×2 held. **ONE mode-4 FAIL (082_keyword_stcount): NOT a regression** — it advanced from compile-abort (SKIP) to compiling-but-wrong; it uses `&STNO`, which has no runtime statement-counter (kw_read → FAILDESCR → NV null), so it fails both modes identically (hence DIVERGE=0). Was already failing mode-3 before this change. A real `&STNO`/`&STCOUNT` counter is a future rung.
**Blocker map ahead (existing-IR, ranked by leverage):** (1) **PATTERNS = RL-5/6, 91 programs** — the mega-lever and the whole point of SNOBOL4; `lower_snobol4.c` currently bombs any `:pat`/TT_SCAN subject LOUD (`sno_fatal` at the `if (pat || subj==TT_SCAN)` guard, line ~157). Maps onto the EXISTING Icon SCAN family (IR_SCAN_MATCH/ANY/MANY/UPTO/MOVE/POS/TAB/BAL/FIND) per the RL-5 candidate table — no new IR. This is the next real rung; it is large (multi-session). (2) **Keyword read/assign** (`&ALPHABET` read, `&TRIM =`/`&ANCHOR =` assign) — blocks output/006, arith's fileinfo+triplet (both die on `&TRIM = 1`), keywords 0/12; note `&ANCHOR` also changes pattern semantics so it couples to RL-5. (3) **DEFINE + call/return** (RL-7) — functions 0/8, expr_eval. (4) string builtins SUBSTR/REVERSE/LPAD/RPAD (SPITBOL extensions — `bb_call: unsupported call shape`; check runtime actually implements them before registering by-name).

**Landed 2026-07-04 (DEFINE + AGGREGATES + KEYWORD-ASSIGN + INCLUDES, this session — blocker-map items 2/3 + user-fn ladder, on SCRIP `9146f606`):** mode-3 **115/261**, mode-4 **114/116 non-skip** (DIVERGE=0; the two m4-only fails are pre-existing 082_keyword_stcount &STNO and 213_indirect_name NRETURN-read). Icon smoke 12/12 ×2 held; polyglot/emit gates untouched-green. Landed in four rungs over EXISTING IR only (enum still frozen at 62 ops; zero new opcodes):
- **DEFINE (user functions, functions 8/8 + rung10 1010/1012/1014/1018):** dynamic scoping is a per-proc behavioral property `dyn_scope` (is_generator precedent) + a `result_name` plumb for alt-entry/alias result cells. Function bodies carve as SEPARATE IR graphs over the full statement list (entry = anchor of the entry-label stmt); RETURN→graph `IR_SUCCEED`, FRETURN→`IR_FAIL`, NRETURN aliased to RETURN. Runtime path already existed (`rt_call_named_proc`, rt.c): added `result_name` to `rt_proc_t`+`ProcEntry`, `rt_proc_set_result_name`, both dyn call paths use `rname=result_name?:name` for the save-push + result read; resolve_cells binds rcell to rname. `DEFINE` entry arg accepts `.label` (TT_NAME) as well as `'label'` (TT_QLIT). scrip.c registers result_name after all three set_generator sites (mode-3 driver loop + mode-4 startup asm `.Lstartup_prn%d` + `rt_proc_set_result_name@PLT`). **Shadowed-name idiom** `DEFINE('max(max,x)')` (parameter name == function name): the result-cell save-push is SKIPPED when a param already shadows rname, so the param's binding is what the body reads/writes and what the caller receives — fixes the whole math.sno family.
- **AGGREGATES/RECORDS/INDIRECTION (data 6/6, rung11 7/7, rung2 210/211/212, rung9 910):** `by_name_dispatch.c` known[] += ARRAY TABLE ITEM PROTOTYPE CONVERT DATA APPLY OPSYN VALUE SNO$KWSET; arms after SNO$NAME. ARRAY via `sno_array_from_proto` (recursive nested 1-D ARBLKs, `'lo:hi'`/`'n'` comma-split dims, init arg, proto stashed in new `ARBLK_t.proto`). ITEM = chained `rt_subscript_var`+`rt_deref`. CONVERT INTEGER/REAL/STRING. DATA guarded `dat_register`. APPLY (DT_N name→registered proc via g_call_args+rt_call_proc_descr, else recursive builtin). VALUE (DT_N deref / NV_GET by name). **EARLY instance-field guard at dispatcher head** (nargs==1 && DT_DATA && fn is a field of the instance's own DATBLK → dat_field_get) beats Icon `real()`/`type()` cast-shadowing — keyed on `args[0].u->type` (DATBLK_t), NOT the DatType registry (that cast was the segfault). `lower_snobol4.c`: TT_IDX rvalue arm (chained IR_SUBSCRIPT + final IR_DEREF), `sx_subscript_lv` helper (+fwd decl), assignment-subject arms for TT_IDX / `ITEM(...)=` / record-field `f(obj)=` (IR_FIELD_VAR + IR_ASSIGN_VAR), TT_NAME generalized to subscript-lv NAMETRAP (no deref), TT_INDIRECT special-cases a TT_NAME inner (direct IR_DEREF, no SNO$NAME wrap → `$.a<2>`). `sno_prescan_expr` recursive walker in the pre-scan loop: DATA literal → `dat_register`; OPSYN(alias,old) → old∈defs ? clone the def with `result_name`=orig fname : `rt_builtin_synonym_add`. DATATYPE returns the instance's own type name for DT_DATA when no gen_type tag.
- **KEYWORD-ASSIGN (arith/fileinfo, arith/triplet, keywords 098/099):** `&KW = v` subject (TT_KEYWORD) lowers to `IR_CALL "SNO$KWSET"(kwname-literal, v)` — SNO$NAME precedent, zero new IR. keywords.c gained writeable storage (`g_anchor`/`g_trim`/`g_maxlngth` + existing error/trace/dump/random) with read arms for anchor/trim/maxlngth/fullscan/stlimit, and `rt_keyword_write_snobol4` (lowercases, coerces to long, routes to the global or falls back NV_SET). (&ANCHOR/&TRIM are STORED and round-trip; their pattern/I-O *semantics* land with IR_MATCH_*.)
- **INCLUDES (library test_case/math/stack/string — math+stack now PASS; case+string park on the pattern wall as expected):** driver include seeding was resolving the source dir from the *relative* argv path so the ancestor-`/lib` walk missed — fixed to `realpath()` the input first, split `SNO_LIB` on `:` (multi-root), and `strdup` the dir strings (they were stack-buffer pointers handed to the lexer's `inc_dirs[]`, a latent lifetime bug).
- **EMITTER (touched — regression-gated, artifacts regenerated):** the flat spine's per-node γ/ω target resolution now CHASES through `IR_GOTO` runs (the label-registry landing for RETURN/etc. is a GOTO node, so a raw pointer-match missed it and the fail/return edge fell to the proc-ω fail exit — this is why a conditional `f = PRED(...) val :(RETURN)` that failed the predicate returned FAILDESCR instead of the prior value), and an unresolved ω whose target is `IR_SUCCEED` now maps to the success port. Proven pure: Icon `.s` bench artifacts + smoke unchanged in shape, IR-mutation + no-lang gates still HARD-zero.

PARKED (existing-IR, with reasons — do NOT fake): 1011 runtime redefinition (static last-wins can't do mid-program re-DEFINE of a live binding); 1013+213 NRETURN by-name lvalue/read; 1015 operator-OPSYN (TT_OPSYN kind 23 needs parser operator machinery); 1016 EVAL (TT_DEFER kind 8 — impossible under the frozen enum per directive); 1017 ARG/LOCAL (would pass ONLY by uppercasing param names — SPITBOL case-fold vs SCRIP case-sensitivity, declined); 082 &STNO statement counter; END-inside-function terminating the whole program (currently returns).

**NEXT LEVER = PATTERNS (RL-5/6, ~91 programs + capture 7 + rungW* 26 + strings cross/word1-4/wordcount + control_new-3):** the one-shot IR_MATCH_* family. Dormant `bb_match_*.cpp` templates exist on disk (NOT in the Makefile). This is the mega-lever gating the largest single block of the corpus and the honest end of the existing-IR ladder.
