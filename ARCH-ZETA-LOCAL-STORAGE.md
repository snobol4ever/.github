# ARCH-ZETA-LOCAL-STORAGE.md — ζ Local Storage: History, Design Space, and the BUMP/COLLECTION/GC Plan

**STATUS: OFFICIAL DOCUMENT OF RECORD for ζ design (Lon directive, 2026-07-05).** This document is the
authority on Byrd-Box local storage — everything that today flows from `IR_t.tmp`. It consolidates and
supersedes the scattered ζ prose in ARCH-x86.md, ARCH-ICON.md, and the ZETA-BLOCKS pivot section of
GOAL-IR-IMMUTABLE-EMIT.md (those remain for their other content; on storage, THIS file wins). The ZB rung
ladder (ZB-2..ZB-6) stays in GOAL-IR-IMMUTABLE-EMIT.md as the live work queue; this file is the design it
implements.

**Why this document exists (Lon, verbatim-in-spirit):** "This is a FORK in the road that has stopped us
many times and we have reset." Six storage models have been tried across 3+ months and two repos
(one4all → SCRIP). Each reset lost design knowledge that later had to be re-excavated from git (the
2026-07-05 ZB-1 archaeology of the 4/28 milestone is the proof). This file carries the knowledge forward
so the seventh model is the last: not by doing things the way we did, but by knowing precisely what each
way bought and what it cost.

---

## 0. Terms

| Term | Meaning |
|---|---|
| **ζ (zeta)** | Per-activation READ-WRITE local storage of a Byrd box / box sequence. The RW half of PER-BOX LOCAL STORAGE. |
| **rZ** | The ζ base register. **Ratified = r12** (one4all `03acf1be`: callee-saved, survives `rt_*` calls; byte-length-identical to the r15 form it replaced). |
| **zS** | The bump ζ-stack top-of-stack cell (new, ZB-3). |
| **ZLS — Zeta Local Storage** | (Lon, 2026-07-05.) The per-activation ζ region itself. **ZLS is internal and completely TYPED data** — heterogeneous compiler-known struct layouts (ints, cursors, code-address continuations, DESCR t·p pairs, pointers) — NOT a homogeneous run of DESCR slots. Deliberately DIFFERENT from the GST/GVA concept, which IS a uniform 16-byte-DESCR-per-variable table. |
| **COLLECTION** | (Lon, 2026-07-05 — supersedes the "ZLA / array" naming retracted the same day; do not call it an array.) The growable per-iteration storage OWNED by a re-entrant box (ARBNO et al.), reached by POINTER from the owner's ZLS fields; element = the body-subgraph's TYPED layout. Replaces every `resq 64` / `[64]` cap in history. |
| **zl[]** | The parallel layout table (node-id → scope_id, offset, kind), built by `zls_build()` post-optimizer. PEERS-clean: zero new `IR_t` fields. Implemented 2026-07-05: `SCRIP/src/contracts/zeta_storage.{h,c}`, API prefix `zls_*` (Lon: ZLS naming — GST/GVA global-side ↔ ZLS local-side; no LVA concept). |
| **t·p** | The 16-byte DESCR_t slot unit (`{DTYPE_t v; uint32_t slen; union{s,i,r,p,arr,tbl,u}}`, `src/contracts/descr.h`). All ζ offsets are multiples of 16. |
| **IR_t.tmp** | The LOWER-granted frame offset on a node (`src/contracts/IR.h:156`). Today: one flat namespace. Tomorrow: a read of zl[]. |
| **ψ (psi)** | The moving element pointer into a COLLECTION (seed-2 idiom: `ψ13 = &ζ->_13_a[i]`). Distinct from the enclosing frame's ζ. |
| **λ (lambda)** | The landing port: post-child-call emptiness test routing to γ/ω (seed-2/3/4 idiom). |
| **Clone tier / cheap tier** | 4/28-era activation modes: memcpy a `.data` init template into a fresh block vs `lea r12,[rel template]` (run IN the static template — the single-activation bet). |

**⛔ THE TYPED PRINCIPLE (Lon, 2026-07-05).** ZLS is not a value store; it is the compiler's OWN
per-activation struct. Its fields have individual types and sizes known at zl-build time. Consequences:
(1) the zl[] map is a per-FIELD typed map, not a per-slot DESCR/non-DESCR bit (§4); (2) GC scanning of
live ZLS uses those typed maps and skips code-address and raw fields precisely (§6); (3) the mode-4
`struc/endstruc` overlays are literally these type declarations printed; (4) never reason about ζ by
analogy to GVA/GST — the resemblance (both `[reg+off]`) is addressing only, not shape.

---

## 1. The Problem Statement

ζ storage must simultaneously provide, with correct LIFETIMES, all of:

1. **Statement temporaries** — expression intermediates; die at statement end. (SNOBOL4/Icon/all.)
2. **Per-box one-shot scratch** — match-time cursor saves, SPAN/BREAK counters; die with the match attempt.
3. **Generator resume state** — TO counters, keyword-generator counters; live across β re-entries, die at exhaust.
4. **Per-ITERATION privacy** — re-entrant matchers (ARBNO; recursion inside a pattern body): each iteration needs the ENTIRE body-subgraph's fields fresh, prior iterations restorable on β. Depth is unbounded. **This is the COLLECTION's job.**
5. **Per-ACTIVATION privacy** — function/procedure calls, including recursion and mutual recursion: args, locals, return-continuation cells, resume cell for generator procs. (SNOBOL4 DEFINE with dynamic scoping; Icon procedures; Prolog clause frames; Raku/Pascal conventional frames.)
6. **Stored-pattern planes** — a pattern VALUE's mutable match cells, instantiated per reference site (seed-5: one code body, two ζ planes, one register).
7. **Deferred bodies** — `*EXPR` / `*PATTERN`: evaluated at match time inside the invoker's activation.
8. **Icon co-expression frames** — a captured activation that OUTLIVES its creator's LIFO discipline, is re-activated by `@`, refreshed by `^e`. **Breaks LIFO by design.**
9. **Icon suspend** — a suspended procedure's activation survives its return-to-caller until resumed or the generator context dies. Also breaks LIFO.

**Language dynamism spectrum (Lon, 2026-07-05):** SNOBOL4 is the most dynamic (patterns as first-class
values, `*EXPR` deferred evaluation, dynamic scoping, run-time DEFINE/OPSYN, EVAL/CODE). **Icon has the
same challenge but not as dynamic** — it must still properly partition ζ at (a) PROCEDURE level and (b)
CO-EXPRESSION level; its patterns-equivalent (scanning) is anchored control flow, not floating values.
Prolog needs choice-point trees (ζ-tree, proven: SCRIP `a8993f46`/`aa587c99`). One design must serve all,
with language-specific layout decisions made in LOWER only (LANG FACT RULE).

---

## 2. History — Six Models Tried, With Verdicts

Each entry: what it was · evidence · pros · cons · why it ended (the reset lesson).

### M1 — Interp-era heap ζ per box instance (one4all, 2026-03/04)

`bb_node_t` C graph; box = `str_t fn(void *zeta, int entry)`; ζ struct calloc'd per box INSTANCE, ports
are C function pointers, wiring is `γ_next`/`ω_next` fields. Evidence: `archive/BB-GRAPH.md` (the ζ
struct), `archive/BB-GEN-X86-BIN.md` (the measured ζ size grid: fail 8B … capture 56B … **arbno ~1556B**
because of the embedded `stack[64×24B]`), `archive/GENERAL-BYRD-DYNAMIC.md` (`box_fn_t` signature,
`enter()` realloc note), the SPITBOL storage comparison (SPITBOL threads 16/24/32-byte heap nodes
carrying `pcode|pthen|parms`; scrip-interp ζ = mutable fields only, code shared — no per-node `pthen`
overhead).

* **Pros:** trivially correct; per-instance privacy free; sizes measurable; the SPITBOL comparison
  showed shared-code+mutable-ζ beats threaded heap nodes on storage.
* **Cons:** heap churn per instance; pointer-chasing dispatch; the ARBNO 64-cap was born HERE (inside
  the heap struct); C functions as boxes — later ruled out entirely (NO C BYRD-BOX FUNCTIONS).
* **Reset:** RT-120 (2026-04-06) voided the trampoline-into-C direction wholesale
  (`archive/BB-GEN-X86-BIN.md` §Architecture Correction). Lesson: **blobs must be self-contained x86;
  dispatch-into-C is not the design.** Heap ζ typedefs and `bb_<kind>_new()` constructors were later
  deleted outright (one4all `267429d0` EDP-10; `254dedb9` DAI-7a deleted 14 dead Icon C-BB zeta-fns).

### M2 — The 4/28 chunk model (one4all@`4757bbcd` — the beauty self-host milestone)

The asm backend's storage model at the moment the project's biggest milestone passed (beauty.sno
byte-identical to SPITBOL, md5 `abfd19a7a834484a96e824851caee159`). Fully re-verified from the one4all
clone 2026-07-05 (ZB-1) and again this session:

* **Two-tier registers:** rbp = SM statement frame for expression temporaries (10,036 uses in
  beauty_prog.s); **r12 = the MOVING ζ block base** for BB/pattern/function activation state (3,937
  uses); plus 2,389 static `.bss` qwords for single-activation per-site state, emitted BY NAME
  (`A("%-24s resq 1\n")`, emit_x64.c:579 — layout delegated to the assembler; no offset assigner for
  statics ever existed).
* **Activation = template-clone (clone tier):** per block family a `.data` init image
  `box_X_data_template` (all `dq 0` rows; the comment column carries the field map — 1,094 annotated
  slots = the chunk-allocation table, in the artifact itself) + `box_X_data_size`. Function-call α:
  `mov rdi,[box_X_data_size]; call blk_alloc; memcpy(new,template,size); mov r12,rax` (verified verbatim
  at the `fn_upr` site, beauty_prog.s:8437). `blk_alloc` = **mmap PER CALL** (58-line
  `archive/backend/blk_alloc.c`; header: "CODE is shared (read-execute); DATA is per-invocation
  (read-write)").
* **Cheap tier:** deferred `*PATTERN` bodies ran IN the static template via
  `lea r12,[rel box_ExprN_data_template]` (34 sites) — a single-activation bet.
* **Nesting:** 332× `push r12 … mov r12,rax` (machine-stack save of caller ζ) or named cells for
  deferred refs; returns via STORED CONTINUATIONS `P_X_ret_γ/ω` (code addresses in statics); return
  thunks restore r12 then `jmp`.
* **Intra-block ABI:** hot descriptor t·p at `[r12+16]/[r12+24]`; per-box fields upward (ARBNO's at
  `+280/+288`).
* **ARBNO:** depth counter IN the current ζ; per-iteration state = ONE qword cursor snapshot on a
  per-instance STATIC `arbN_stack resq 64` (macros verified at `snobol4_asm.mac:2040-2077`; α1 rejects
  the zero-advance empty match). **Depth hard-capped at 64.**
* **Pros:** IT SHIPPED THE MILESTONE. Per-invocation privacy real (recursion correct). The chunk
  STRUCTURE — what fields each activation carries, per statement / pattern / DEFINE body / ARBNO — is
  the asset (Lon: "the chunk structure is the asset; the registers were later optimization"). The
  template comment column IS documentation-as-artifact.
* **Cons:** one mmap **syscall per activation** (correctness-first, brutal cost); static `.bss` for
  ret-continuations and per-site state = not re-entrant where it mattered (the cap, the shared
  continuation cells); cheap tier's single-activation bet is exactly the bet the flat model later
  re-lost; two registers (rbp+r12) where the ratified design wants one.
* **Reset:** SCRIP fresh-started from the one4all working tree (`713c581b`, 2026-05-31) WITHOUT the
  4,155-commit history. Lesson: **carry the design forward in documents** — dropping history cost us
  this model and forced the ZB-1 archaeology. (This file is that lesson, applied.)

### M3 — One-register frame ratification (one4all GZ3, 2026-05-30/31)

Icon value stack demolished (`50a6d07a`: 23 vstack consumers stubbed to ICN_STACKLESS_ABORT); TWO FACT
RULES born — **ICON STACKLESS ONE-REGISTER FRAME** (all RW in ONE per-sequence frame `[reg+off]`) and
**RO LOCALS ARE IP-RELATIVE** (`[rip+disp]`, sealed adjacent to the blob). ζ register switched r15→r12
(`03acf1be`) as the ratified layout. The tri-language **PER-BOX LOCAL STORAGE FACT RULE**
(byte-identical in GOAL-SNOBOL4-BB / GOAL-ICON-BB / GOAL-PROLOG-BB) fixes the law: every box value
reference is exactly **(RO)** `[rip+disp]` or **(RW)** `[ζ+off]` — never a ring, never a value stack,
never an NV round-trip for an intermediate.

* **Pros:** the addressing law that everything since obeys; gates exist and stay green
  (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`).
* **Cons:** none — but note it ratified the ADDRESSING, not the ALLOCATION. It says `[r12+off]`; it does
  not say what r12 points AT or when that changes. M5's mistake was reading it as "r12 is set once."

### M4 — The seed ladder (SCRIP/seed/test_sno_1..6.c + test_icon.c — the golden designs)

Hand-written C goldens, each pinning one allocation law (commits `2ede32bd`, `dd17db1a` document 5/6):

* **seed 1** — ONE function; ARBNO per-iteration state = fixed `_1_t _1[64]` + **moving ζ pointer**:
  `ζ=&_1[ARBNO_i=0]` at α, `ζ=&_1[++ARBNO_i]` going deeper, fail path `ARBNO_i--; ζ=&_1[ARBNO_i]; goto
  alt_β`. **The per-iteration frame carries the ENTIRE body-subgraph's box fields** (`ζ->alt, ζ->alt_i,
  ζ->ARBNO`) — body re-entrancy is free because the frame IS the body's layout; the box's own depth
  counter lives in the ENCLOSING scope. This is the distilled COLLECTION.
* **seed 2** — callable BBs `str_t f(f_t *ζ, int entry)`; the CALLER stack-allocates the child's ζ
  (`word_t word12_ζ;` as a plain local); typed per-iteration element storage lives INSIDE the owner's ζ
  (`_13_t _13_a[64]` in `group_t`); **ψ** is the moving element pointer; **λ** landing ports route on
  child-return emptiness. The typed-element precedent the COLLECTION generalizes.
* **seeds 3/4** — `enter(ζζ,size)`: lazy calloc-or-memset — "fresh DATA per α-entry" with instance
  REUSE (memset an existing block instead of re-allocating); seed 4 chains the child ζ as a POINTER
  field in the parent (`a_t *a6_ζ;`) — the ζ-tree in miniature.
* **seed 5** — stored pattern `P` used at TWO sites: ONE code body, TWO distinct ζ instances, **ONE
  register r12 time-multiplexed by the glob heads** (α sets, β reloads). The two-plane law.
* **seed 6** — BB_SWITCH broker: the C call stack IS the push/pop of r12 across plane switches; "NO box
  first-instruction touches r12" — the caller/broker owns the swap.
* **Prolog ζ-tree on real silicon** — `e8e728cc` (calls as δ/ε port edges) → `a8993f46` (**ζ-TREE
  substrate**: `rt_enter(void**slot,int nslots)` reuse-or-alloc; each call SITE owns one child-POINTER
  slot in the caller frame, placed AFTER the init range so "**rt_enter reads before write**" — the
  load-bearing invariant; callee α: `push` caller ζ, `mov r12,rdi`) → `aa587c99` (self/mutual RECURSION
  admitted onto the tree). Also `b27e06ee` (D5 zeta-arena instance alloc, OWNED-BUILD ledger).
* **Pros:** every law the end-state needs exists here, proven executable, tiny, readable.
* **Cons:** the fixed `[64]` caps (a seed simplification, not a design); seeds 5/6 are `<malloc.h>`-era
  transports.
* **No reset — the seeds are permanent references.** The 2026-07-05 REALLOC-collection directive grafts
  growth onto the seed-2 shape; nothing in the seeds is repudiated.

### M5 — The flat model (SCRIP current HEAD — TMP-ERADICATE era)

`ir_drive_slot_assign` (`src/contracts/scrip_ir.c:206`) is the ONLY slot source: a single compile-time
bump cursor over `g->all[]` granting each node a static `base + k*16` offset **for the life of the
program**. Per-op grant table (verified in source this session): TO/TO_BY/SCAN_ENTER/ITERATE/LIMIT/
REPALT/KEYWORD_ICON/REV_ASSIGN/INDIRECT_GOTO/DISJUNCTION k+=2 · MAKE_LIST/CALL 1+n_operands · CREATE 4 ·
MATCH_HEAD/SPAN/BREAK(X)/ARB/REM/ASSIGN_SAVE/ALTERNATE/DEREF/ASSIGN(_VAR)/RANDOM/SWAP_VAR/KEYWORD_SNOBOL4
/KEYWORD_ASSIGN/INITIAL k+=1 · generic producers k++; params ABI-fixed `16*(i+1)` from `g->pnames`;
named locals interned to `g->vslots`; `resume_slot` carved at the tmp high-water. r12 is set ONCE
(`src/templates/xa_flat.cpp` prologue: `push r12; mov r12, rdi`). ZERO per-α fresh-DATA machinery exists
(grep = 0). Sole fresh-frame mechanism = whole-proc `g_proc_arena` (`rt.c:348`,
PROC_FRAME_DEPTH×PROC_FRAME_QWORDS, GC_MALLOC'd) + `bb_callee_frame.cpp` repointing r12. Per-box scratch
rides `g_emit.x86_scratch_off = drive_value_slot(nd)` (emit.cpp:980/984/996 → templates
bb_match_rem/break/breakx/span/arb/**arbno**).

* **Pros:** TMP-ERADICATE was a genuine, kept victory — **LOWER owns the layout** (`d671e68f`+
  `ad613052`); emit-time allocators deleted; `IR_RESUME_VALUE` dissolved into durable-frame arithmetic
  ("counter at tmp+16", `ed0ac777`); slot-collision family closed; gates
  (`test_gate_emit_no_slot_alloc.sh`) hold. Simple, fast, zero runtime allocation.
* **Cons — the named casualties (the pivot's finding):** one lifetime for everything = whole-graph.
  (a) **The ARBNO wall** — per-iteration state cannot exist; (b) **queens solution-4 frame clobber** —
  cumulative backtracking reuses live slots; (c) **the SCAN-SCRATCH overrun family** — boxes writing
  into the NEXT node's slot (patched case-by-case with k+=2 grants); (d) recursion only via the
  whole-proc arena's coarse depth×frame grid; (e) statics/initial contamination (queens/rsg) because
  "persistent" had no home distinct from "frame".
* **Reset lesson (2026-07-05 pivot):** **LIFETIME is a first-class property of storage. A single
  program-lifetime cursor cannot express activation or iteration lifetimes, no matter how many k+=2
  patches it receives.** This model contradicted ARCH-x86's "fresh DATA on every α-entry" and
  ARCH-ICON's "zeta struct allocated fresh per α-entry / per-box arena indexed by depth" — those were
  the aspiration; M5 was the shortcut; the contradiction was invisible until ARBNO forced it.

### M6 — The ZETA-BLOCKS pivot (2026-07-05, current frontier — ZB ladder)

Bring the 4/28 chunk STRUCTURE forward onto the live spine, minus its costs: bump ζ-stack in the RX
slab (alloc = add, release = restore-to-mark), `.prev` link replaces push-r12 (stackless preserved),
NO `.bss` in emitted programs (mode-4 prints NASM `struc/endstruc` OVERLAY headers — pure layout
documentation, zero storage; both modes address `[rZ+disp]`, MODE34-identical), layouts computed
PRE-EMIT into the parallel `zl[]` table, **COLLECTIONS** (realloc-grown per-iteration storage owned by
re-entrant boxes, pointed to from ZLS; cap removed), heap promotion deferred to suspendable scopes. This document is M6's design record; §4–§8 below ARE the
design.

---

## 3. What `IR_t.tmp` Is Today — Five Lifetimes In One Namespace

| # | Client | Today's grant | True lifetime | Target class (§4) |
|---|---|---|---|---|
| 1 | Expression temporaries (`ir_node_produces_value`) | k++ | statement | ZL-GROUP |
| 2 | One-shot match/scan scratch (`x86_scratch_off` family; SCAN k+=2) | k+=1/2 | match attempt | ZL-GROUP (or ZL-PAT when pattern-owned) |
| 3 | Generator resume state (TO counter at tmp+16; keyword counters; ITERATE/LIMIT/REPALT) | k+=2 | generator lifetime (α..exhaust) | ZL-GROUP (resumable slots within the group) |
| 4 | Call argv regions (CALL 1+n; argv at tmp+16) | 1+n | call | ZL-GROUP (marshaling) → callee's ZL-FN |
| 5 | Named locals + params + gen-proc resume cell (`vslots`, `pnames`, `resume_slot`) | interned | activation | ZL-FN |

Plus the states with NO home today: per-iteration frames (→ **COLLECTIONS / ZL-ITER**), stored-pattern mutable
cells (→ **ZL-PAT**), ret-γ/ω continuations (statics in 4/28; proc-arena rows now → **ZL-FN header**),
persistent statics/initial flags (**NOT ζ at all** → GVA arena, already the landed Icon precedent),
co-expression frames (→ **ZL-COEXPR**, §7).

**The delineation requirement (Lon):** partition tmp's flat namespace into `(scope_id, off)` with
per-class lifetime. The emitter contract stays: read `(scope_id, off)` from zl[] ONLY, emit
`[rZ+disp]`, both modes byte-identical.

---

## 4. The Layout Classes

Built by `zls_build(g)` (zeta_storage.c) post-optimizer / pre-emit over the scope tree
**program → DEFINE/procedure body → label-group (labeled stmt + trailing unlabeled) → re-entrant box**.
Groups laid DISJOINT v1 (lifetime-unioning deferred until real liveness info exists). PEERS RULE: the
table is parallel, keyed by node id; zero new BB_t/IR_t fields.

* **ZL-GROUP** — label-group frame: every non-re-entrant box instance's fields — temporaries, one-shot
  scratch, resumable generator slots, call marshaling. Absorbs the dead SM tier's expression
  temporaries (4/28's rbp tier folds into r12's world; ONE register, per M3).
* **ZL-FN** — DEFINE/procedure-body aggregate: `{prev, mark}` header + arg/local t·p pairs + its
  ZL-GROUPs concatenated + **ret_γ/ω continuation cells (EVICTED from statics — the no-.bss rule forces
  this anyway)** + gen-proc resume cell. Serves SNOBOL4 DEFINE (dynamic scoping via the existing
  save/restore-by-name runtime, storage per-activation here) and **Icon procedures** (params ABI
  `16*(i+1)` continuity). Icon `static`/`initial` are NOT in ZL-FN — they are persistent, already
  correctly homed in the GVA arena (mangled-GVA-globals precedent, 2026-07-04).
* **ZL-PAT** — per match-activation mutable pattern state, allocated in the INVOKER's activation. The
  GLOB's compiled shape stays immutable sealed `[rip+disp]` (RO rule); a stored pattern VALUE reads its
  shape via pointer; ALL mutable match cells — including any pattern-side continuations and COLLECTION owner
  quads — live here. Seed-5's two-plane law realized: one shape, N planes, planes are ZL-PAT instances.
* **ZL-ITER** — the **COLLECTION element layout**: the re-entrant box's BODY-subgraph fields (seed-2's
  `_N_t`; seed-1's `_1_t`) — a TYPED struct, per the Typed Principle. Elements live contiguous in a
  realloc-grown COLLECTION OWNED by the box and reached by POINTER from the owner's ZLS fields. The
  owner's own fields, in the ENCLOSING activation layout, are the quad `{iter_ptr, iter_cap, iter_i,
  prev_rZ}`. Uncapped. Runtime-sized elements are fine (bump takes any size).
* **ZL-COEXPR** (new, this document, per Lon 2026-07-05 — Icon co-expression level): the captured
  activation block of a co-expression — see §7. Heap-lifetime by definition (breaks LIFO at birth).

**Mode-4 overlay prefixes:** `ZG_` `ZF_` `ZP_` `ZI_` `ZC_` — struc/endstruc documentation headers,
zero storage.

**zl[] entry (proposed, per the TYPED PRINCIPLE):** node side `{ int scope_id; int off; }` PLUS a
per-scope FIELD MAP: `{ int off; int size; uint8_t kind; }[]` with **kind ∈ {DESCR (t·p pair), PTR_GC
(collection/promoted-block pointer — the collector follows AND fixes it), PTR_CODE (ret-γ/ω
continuation — skipped, never relocated), RAW (int/cursor/counter — skipped)}**. This is a per-FIELD
typed map, not a per-16B-slot bit, because ZLS fields are heterogeneous. It is UNUSED by the collector
until the GC ladder — but ZB-2 touches every grant site exactly once, so the map is built NOW (§6: the
field maps ARE the collector's stack maps; retrofitting later means re-walking every grant). The mode-4
struc overlays print straight from these maps.

**ZB-2 v1 MECHANISM NOTE (landed 2026-07-05, second session):** group boundaries come from
**LOWER-recorded marks** (`zls_group_mark(g, label)` at the top of each labeled statement's lowering,
lower_snobol4 first), NOT from label-registry landings — landings are pre-created GOTO anchors clustered
at low `all[]` indices, so index-based grouping misattributes; the statement boundary is knowledge only
LOWER has at the moment it has it, which is also the doctrinally correct owner (LOWER owns the layout).
`zls_build` consumes the marks post-optimizer. An `audit` bit per field flags kinds provisional pending
template verification (GC-1 burns these to zero before any collector reads the maps). Live in
`SCRIP/src/contracts/zeta_storage.{h,c}`; `--dump-zeta` prints the table.

---

## 5. The BUMP Allocator — Design Space, All Options On The Table

**Lon (verbatim-in-spirit, 2026-07-05): "What is neat about a BUMP allocator is we can make it HUGE and
get things working WITHOUT proper GC. So it can be done in stages."** This is the staging spine: bump
first, huge; GC later, when the COLLECTIONS and the value world are ready to move onto it together.

### 5a. Where zS (the bump top) lives

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **Slab cell `[rbx+ZS_OFF]`** (rbx = the GVA/slab base, rides through untouched) | Zero registers burned; both modes identical; mode-3 slab already exists | One memory op per alloc/release | **v1 DEFAULT** (per ZB-ALLOC) |
| Dedicated register (r15 candidate) | Fastest alloc (add r15, sz) | r15 = Δ subject length in the scan contract; any promotion needs the `x86_asm.h` roster + a bench | Only if a bench says so, later |
| Global `.bss` cell | — | BANNED in emitted programs (no-.bss rule); mode-3-only asymmetry violates MODE34 | Rejected |

### 5b. Arena size & growth — the HUGE-first staging

| Stage | Policy | Notes |
|---|---|---|
| **Stage α (ZB-3)** | ONE HUGE reservation. mmap reserve (e.g. 1 GiB PROT_NONE) + commit an initial run (e.g. 64 MiB RW), or simply a large RW map — decide by container limits. Overflow = **loud bomb** with the ζ high-water printed. | Correctness ships with ZERO GC. Leaks-within-a-run tolerated. The whole point. |
| Stage β | Guard page → grow-on-fault, or explicit high-water check per scope entry (one cmp) | Cheap safety once α is proven |
| Stage γ | GC pressure trigger: allocation-threshold regeneration (§6), &STLIMIT-style pacing | Only after SN4-GC lands |

### 5c. Alloc/release protocol (the mark/release LIFO)

α-entry of a scope: `mark = zS; blk = bump(sz); blk.prev = rZ; rZ = blk`.
Scope exit (final-γ or ω): `zS = mark; rZ = blk.prev`.
Header = `{prev, mark}` (16B, one t·p unit).
**THE LIFO INVARIANT (soundness):** Byrd traversal under mark/release is LIFO — failure fully unwinds
rightward frames before any left-β re-entry; success releases wholesale at the scope mark; a γ-exit MAY
leave frames live (they die at the enclosing mark). **Suspendables (Icon suspend / coexpr) BREAK LIFO ⇒
their scope's block heap-promotes at creation** (§7); GATE until promotion lands: no suspendable box
inside a bump-lifetime scope.

### 5d. Frame identity across nesting

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **`.prev` link field** in the block header | Stackless preserved (the foundational rule); restore is one load; works identically for heap-promoted blocks | One t·p of header per frame | **CHOSEN** (ZB-ALLOC) |
| Machine-stack `push r12` (4/28 F3, seed-6 broker) | Zero header bytes | Reintroduces a stack discipline the STACKLESS rule bans; coexpr/suspend can't ride it | Rejected for the spine; the C-transport seed-6 broker remains a reference only |
| Named static cells (4/28 `nref516_r12`) | — | .bss ban; not re-entrant | Rejected |

### 5e. Initialization

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **Zero-fill `rep stosq` v1** | FAITHFUL: the 4/28 templates were ALL `dq 0` rows (verified) — zero-fill loses nothing; simple; matches seeds 3/4 `enter()` memset semantics | Pays for slots never written (cheap) | **v1** |
| Template memcpy clone (4/28 clone tier) | Needed the day a nonzero init image exists; **and is exactly the mechanism Icon `^e` coexpr REFRESH wants** (§7) — keep the machinery in the design | More emitted data; a memcpy per activation | Deferred until a nonzero-init field or ^e lands |
| No init (read-before-write discipline) | Free | The rt_enter invariant only covered specific slots; general graphs read `&null`-expecting slots | Rejected as default |

### 5f. The COLLECTION — per-iteration storage of re-entrant boxes (Lon directive 2026-07-05; naming corrected same day: NOT "ZLA", NOT "array" — elements are TYPED, this is unlike GST/GVA)

Element = ZL-ITER layout (the body-subgraph's TYPED fields). Elements contiguous in a realloc-grown
COLLECTION OWNED by the box, reached by POINTER from the owner's ZLS fields. Owner quad
`{ptr, cap, i, prev_rZ}` in the ENCLOSING activation layout (the seed's `ARBNO_i` + its storage, made
growable).

**Ports:** α `i=0; lazy-ensure cap; rZ=&ptr[0]` · child-ok/α1 (progressed)
`i++; if(i==cap) ptr=rt_zcol_grow(ptr,&cap,elem_sz); rZ=ptr+i*elem_sz` · β `if(i==0)→ω-final; i--;
rZ=ptr+i*elem_sz; →child_β` · final exits restore `rZ=prev_rZ`.

**THE RELOAD LAW:** realloc MOVES; an rZ into a COLLECTION is NEVER cached across a push — recomputed
from `(ptr,i)` at every owning-box port (grow happens ONLY at push, so the body sees a stable base
within any single child pass). Corollary: NO pointer into a COLLECTION element may ESCAPE the body;
cross-box refs go via the enclosing ζ or `(ptr,i)`. **Nesting:** an outer element CONTAINS the inner
box's quad — recursion-safe by construction. (§5h's self-load hook, source option (a), discharges this
law mechanically when enabled.)

**Backing, staged:** v1 = heap `realloc` (seed-5/6 house style) + free at owner ω-final + a
per-activation grown-collection list walked at scope release (covers the γ-exited-live case; keeps
mark/release O(1)+ε). **v2 = the scrip GC heap (§6) — GC and the COLLECTIONS go together (Lon).** Perf
rung later: ζ-stack-backed grow-in-place-when-top.

**Alternative considered — per-iteration frames pushed on the ζ-stack itself** (seed-1's `_1[64]`
generalized to stack frames, the pre-directive ZL-ITER framing): pros — no realloc, no RELOAD LAW,
pure LIFO; cons — iteration frames interleave with unrelated scope frames on backtrack-heavy graphs
(release ordering gets subtle), no contiguity/locality, the owner can't index prior iterations O(1),
and a γ-exit-live iteration set pins the whole stack above it. **Lon chose owner-owned contiguous
COLLECTIONS** — locality, single ownership, O(1) indexing, uncapped, and a COLLECTION is a clean future
GC object. The `resq 64` and the mmap both die.

### 5g. Bump-allocator ideas ledger (everything proposed, kept for the record)

1. High-water telemetry cell beside zS: max depth per run, printed under a flag — sizing data for
   Stage β and the GC trigger, nearly free.
2. Per-scope one-cmp overflow check vs guard-page fault — pick after Stage α numbers exist.
3. Red-zone poisoning under a debug flag (fill released region 0xDD) — makes use-after-release loud;
   pairs with the monitor.
4. `--dump-zeta` (ZB-2): print the scope tree, per-scope sizes, per-slot kind — the inspector that makes
   layout bugs mechanical instead of exploratory.
5. Grow-in-place-when-top for a COLLECTION (when it IS the newest bump allocation → extend zS instead
   of realloc) — perf rung, after correctness.
6. Frame-reuse/LCO: the WAM-CP-6 design (one4all `860d1163`/`afa770d3`/`baf8397d` + the settled design
   doc) proved tail+deterministic calls can REUSE the caller's frame — on the bump model this is
   "don't bump, re-mark": a later optimization rung, Prolog first.
7. seeds-3/4 `enter()` REUSE semantics (memset-not-realloc when a block already exists) is subsumed by
   mark/release — the bump gives back the same bytes on the next α anyway.

### 5h. The α/β R12 SELF-LOAD HOOK — a toggleable emitter feature (Lon idea, 2026-07-05)

**The idea (Lon, verbatim-in-spirit):** at ALPHA and BETA we can hook into the `x86()` calls that
DEFINE those port labels inside the templates, and OPTIONALLY emit ONE EXTRA instruction that loads
R12 for that box — so R12 is ALWAYS set on entry to any box, regardless of which edge jumped there.
Make the extra-instruction emission a code FEATURE that can be turned ON or OFF as we experiment
("sometimes we'll try that and sometimes we will not — this is a QUICK way").

**Why this is cheap to build and cheap to try:** every template already speaks only through the
`x86()` funnel; the α label and the β define go through central sites (`x86("label",…)` and the
DRIVE_PAIR β-define path). Hooking THOSE two sites gives the feature to all ~161 templates with ZERO
per-template edits — both mediums for free (the funnel is BOTH-MEDIUM by law). Toggle = one flag
(working name `SCRIP_ZETA_SELFLOAD`, env + `g_emit` mirror), OFF by default; flipping it is the whole
experiment.

**Where the loaded value comes from — sub-options, all on the table:**
* **(a) The plane cell — a per-plane pointer cell holding "current ζ for this plane," i.e. the seeds-3/4
  double-pointer `*ζζ` made real.** The box's α/β loads `r12 ← [plane_cell]` (RIP-relative for a
  static/single plane; slab-relative for dynamic planes). The OWNER of a plane updates the cell — a
  COLLECTION owner writes `cell = ptr + i*elem_sz` at its ports; a clone-tier activation writes the
  fresh block; a coexpr `@` writes the target plane. **This mechanically DISCHARGES the RELOAD LAW:**
  children never cache — they self-load from the cell every entry; grow/realloc only has to update ONE
  word. Also makes cross-plane jumps (stored patterns seed-5, coexpr O2) trivially correct.
* **(b) The rZ shadow cell (debug/assert flavor)** — reload from the slab's canonical rZ mirror; with a
  compare-and-bomb variant this becomes a wiring-invariant CHECKER: any template or edge that clobbered
  or skipped an rZ update dies loudly at the next port. A monitor-class debugging lever.
* **(c) Baked static-plane pointer** — for provably single-activation boxes (the 4/28 cheap tier),
  `lea r12,[rip+template]`: correct only under the single-activation bet; useful as a bring-up mode.

**Costs / cautions:** +1 instruction per port entry (icache + a load); with (a), one store per plane
switch at owners. Interaction with the `.prev` protocol: under self-load, `.prev`/restore can shrink to
"owner updates the cell" — two disciplines must not BOTH be authoritative, so the toggle spec is: when
SELFLOAD is ON, the plane cell is truth and ports load it; when OFF, rZ register discipline is truth
(v1 default). MODE34 holds either way (same funnel). Fits the DIVISION-RULE spirit: it's port wiring +
one immediate, not a stored per-node flag.

**Verdict:** BUILD THE HOOK NOW (it is a few lines at two central sites), keep it OFF by default, and
use it as the standing A/B lever for every ζ experiment — including as the fastest path to unblock
awkward wiring cases (stored patterns, coexpr planes) before their "proper" rungs land. Decision row
D13.

### 5i. EXTREME OPTION — per-box heap ownership; ZLS itself on the heap (Lon, 2026-07-05; captured)

**The idea (Lon, verbatim-in-spirit):** one extreme is to use REALLOC heap storage for this — **each BB
box owns its own allocation**; use heap for the ZLS AND for the COLLECTIONS (used by ARBNO for
instance), which are pointers from the ZLS region. "This is terrible performance. But use the same
model with GC BUMP and SLIDE — might be really nice."

| Variant | What | Pros | Cons | Verdict |
|---|---|---|---|---|
| **O-HEAP/malloc** | Every box (or scope) mallocs/reallocs its own ZLS block; COLLECTIONS likewise | Maximal privacy + lifetime freedom; conceptually the M1 model with today's layouts | TERRIBLE performance (allocator call per activation — the blk_alloc-mmap lesson at finer grain); fragmentation; free-discipline bugs | **Rejected as implementation; KEPT as the ownership MODEL** |
| **O-HEAP/GC-bump-slide** | The SAME ownership model, but blocks come from the scrip GC heap: alloc = bump (one add), dead activations reclaimed by mark+slide, no explicit free | Alloc as cheap as the ζ-stack; **the LIFO requirement DISAPPEARS** — suspend/coexpr/γ-exit-live all become the normal case, promotion stops being an exception; one storage story for ZLS + COLLECTIONS + values; slide compacts naturally | Every activation adds GC pressure; slide must FIX `.prev`, plane cells, and owner `ptr`s (the §4 typed field maps make this precise — PTR_GC vs PTR_CODE vs RAW); safe-point discipline everywhere, not just rt-allocation sites; rZ itself must be a root at collect | **ON THE TABLE as the possible END-STATE unification** — revisit after GC-3 proves slide (row D14) |
| **Hybrid (v1, the ZB-ALLOC design)** | LIFO ζ-stack for bump-lifetime scopes + heap COLLECTIONS + heap-promoted blocks for LIFO-breakers | Ships WITHOUT any GC (the HUGE staging, §5b); smallest delta from today | Two lifetimes to reason about; promotion is an explicit act | **v1 CHOSEN** |

The deep observation to preserve: **the objection to per-box heap ownership was never the MODEL — it
was the ALLOCATOR.** M1 had the model with calloc and paid in churn; M2 had it per-function with mmap
and paid in syscalls; O-HEAP/GC-bump-slide keeps the model and removes the price. If GC-3 lands clean,
D14 is a genuine fork-again point where the ζ-stack could dissolve into the heap entirely.

### 5j. THE CHOICE MACROS (`ZC_*`) — every open design axis as a compile-time switch (Lon directive, 2026-07-05)

**The directive (verbatim-in-spirit):** the next sessions are EXPERIMENTAL; create `#define`s for the
varying CHOICES so we can switch between them — e.g. an INFINITE BUMP allocator for testing, a proper GC
mode, a C malloc/realloc/free mode. Each mode works until proven not to; pick good defaults from the
history above.

**Why this is legal at zero design cost:** each BB is a pure-functional entity with respect to storage —
a box reads `[rZ+off]`, full stop. The axes below change WHERE those bytes come from and WHEN they are
reclaimed, never what a template does. Switching an axis touches the allocator/zl units only; the ~161
templates are untouched by construction.

**The header:** `SCRIP/src/contracts/zeta_choices.h` (authored 2026-07-05; additive — included by the
allocator + zl units only, nothing else in the tree references it yet). Every axis is `#ifndef`-guarded,
so `make CFLAGS+='-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO'` swaps a mode with zero edits. One value per axis;
statically-illegal combinations are `#error`s in the header; combinations only checkable at run time
bomb LOUD.

| Axis | Modes | Default (experimental era) | Rationale from history |
|---|---|---|---|
| **ZC_ALLOC** — activation allocator | `BUMP_INFINITE` / `BUMP_LIFO` / `MALLOC` / `GC` | **BUMP_INFINITE** | INFINITE = monotone bump, NEVER releases, arena HUGE: removes REUSE from the suspect list entirely — any bug under INFINITE is layout/wiring, never lifetime. The testing mode Lon named. `BUMP_LIFO` = the v1 design (§5c) — flip the default at ZB-3 close. `MALLOC` = every scope block is a real heap object ⇒ ASan/valgrind catch overruns and use-after-release for free (M1's model resurrected as a DIAGNOSTIC — its churn is now the feature). `GC` = §5i end-state; `#error` stub until GC-3. |
| **ZC_COLLECTION** — COLLECTION backing | `MALLOC` / `ARENA` / `GC` | **MALLOC** (D7 ruled) | realloc house style; `ARENA` = grow-in-place-when-top (`#error` under `ZC_ALLOC_MALLOC` — needs a bump arena); `GC` = v2 (GC-4). |
| **ZC_SELFLOAD** — §5h hook | `OFF` / `PLANE_CELL` / `ASSERT` / `STATIC` | **OFF** | Hook code is compiled ALWAYS (two central `x86()` sites); this macro sets the built-in default and env `SCRIP_ZETA_SELFLOAD` overrides per RUN — that is the QUICK lever. `ASSERT` = the compare-and-bomb wiring checker. |
| **ZC_INIT** — fresh-frame init | `ZERO` / `NONE` / `CLONE` | **ZERO** | 4/28-faithful (all templates were `dq 0`). `NONE` + poison exposes missing-init assumptions. `CLONE` reserved for `^e` refresh / future nonzero images (§5e). |
| **ZC_POISON** — debug fills | `OFF` / `FILL` | **FILL** while experimenting; OFF for bench | 0xDD on release; 0xAA on fresh under `INIT_NONE`. Makes use-after-release loud; pairs with the monitor. |
| **ZC_TELEMETRY** | `OFF` / `ON` | **ON** | zS high-water + per-scope alloc counts; feeds the D3 sizing decision; near-free. |
| **ZC_OVERFLOW** | `BOMB` / `GUARD` | **BOMB** | one `cmp` per scope entry v1, prints the high-water; guard-page grow is Stage β. |
| **ZC_ARENA_MB** | integer | **1024** | HUGE per §5b; adjust to container. Meaningful for BUMP modes only. |
| **ZC_PROMOTE** — LIFO-breaker scopes | `GATE` / `ON` | **GATE** | suspendable box inside a bump-lifetime scope bombs (the standing gate) until the promotion rung lands. |

**⛔ THE MODE-INVARIANCE GATE.** Switching any ZC axis may change BYTES and SPEED, NEVER BEHAVIOR: the
crosscheck FAIL set and every oracle pin must be byte-identical across modes. An A/B run across two
modes is therefore the standing per-axis regression instrument — and doubles as the bug-hunting move
(a divergence BETWEEN modes brackets a lifetime bug the way the monitor brackets a semantic one).

**Recipes (the intended experimental grammar):**
BRING-UP = `INFINITE + ZERO + FILL + TELEM + BOMB` · SOAK = `LIFO + ZERO + FILL` ·
HUNT-LIFETIME = `MALLOC` (+ ASan build) · HUNT-WIRING = `ASSERT` self-load ·
BENCH = `LIFO + ZERO + no-POISON + TELEM-OFF + GUARD` · FUTURE = `GC + GC`.

---

## 6. GC — The 3-Stage SIL Collect/Mark/Slide, and the COLLECTION↔GC Coupling

**Lon (2026-07-05): "I think that GC and [the COLLECTIONS] go together. However GC will be used for
dynamically created DESCR for user VARIABLES also."** So ONE scrip-owned heap, TWO client families:

* **(A) Activation-adjacent objects:** COLLECTIONS (reached by pointer from the ZLS region);
  heap-promoted ζ scopes (Icon suspend, co-expressions §7).
* **(B) The value world:** every dynamically created DESCR payload behind user VARIABLES — strings,
  ARBLK arrays, TBBLK tables, DATINST records, VCELLs/name traps, pattern blobs' mutable companions,
  code/expression blocks (EVAL/CODE, someday).

### 6a. The heritage (why this exact collector)

SNOBOL4's SIL implementation allocates **sequentially from a free pointer — bump was SNOBOL4's original
allocator** — and runs *storage regeneration* when exhausted. SPITBOL kept the design; its manual
(v3.7) confirms: "a fast garbage collector … needs to distinguish between small integers and memory
addresses" (hence the &MAXLNGTH object-size restriction), and — the external-function chapter —
"SPITBOL distinguishes between relocatable and non-relocatable words within a block … when the target
block is moved during **storage regeneration**, SPITBOL adjusts the pointer automatically. For each
block type, SPITBOL knows which words can contain relocatable pointers" (XNBLK external blocks are
all-non-relocatable). `COLLECT(i)` forces a regeneration and returns free words; the manual warns
forcing early collections always costs time — pacing matters.

**The 3 stages:**
1. **MARK** — trace from the ROOTS; set the mark flag in each live block's title/header word.
2. **COLLECT/ADJUST** — one linear sweep computes each marked block's slid-down address; then every
   relocatable word (per-block-type maps) in marked blocks AND in the roots is adjusted by its target's
   displacement.
3. **SLIDE** — one linear memmove compacts marked blocks downward; the free pointer resets to the end.

**Properties:** allocation stays PURE BUMP between collections; zero fragmentation; allocation ORDER
preserved (age-ordered heap); no free lists; cost linear in live+heap.

### 6b. Why SCRIP can do this PRECISELY (better than SIL could)

* **Tags exist.** `DESCR_t {v, slen, union}` discriminates pointer from integer by TYPE, not by address
  range — DT_S/.s, DT_A/.arr, DT_T/.tbl, DT_DATA/.u, DT_P, DT_N (slen-discriminated
  NAMETRAP/NAMEPTR/NAMEVAL), DT_E vs DT_I/.i, DT_R/.r. The &MAXLNGTH-style small-int-vs-address hack is
  unnecessary. Per-block relocatable maps derive from the block type + the DESCR layout.
* **The zl[] typed field maps ARE the stack maps.** The live ζ region `[current-mark chain … zS]` is
  precisely scannable: for each live frame, its scope's field map says which fields are DESCR (trace
  the payload), PTR_GC (trace AND fix), PTR_CODE (skip — continuations never relocate), RAW (skip).
  ZLS frames themselves DO NOT MOVE in the v1 hybrid (the ζ-stack is not the heap); only heap blocks
  slide. (Under O-HEAP/GC-bump-slide, §5i, frames DO move and `.prev`/plane cells are PTR_GC.)
* **The COLLECTION is slide-ready by construction.** The RELOAD LAW already forbids caching pointers
  into a COLLECTION across a push; the ONE pointer that must be fixed on slide is `owner.iter_ptr` —
  which lives in a ZLS field the map marks PTR_GC. The per-activation grown-collection list (already
  mandated for the γ-exited-live release case) is LITERALLY a GC root/fixup list, specified before the
  GC existed. With §5h option (a) enabled, the plane CELL is one more PTR_GC word the collector fixes,
  and every consumer self-heals on next entry.
* **Root set enumeration:** GVA slab `[rbx+k*16]` (all DESCR slots) · NV dictionary buckets (name→cell)
  · live ζ region via zl kind maps · COLLECTION owner quads (via the same maps) + the grown-collection lists ·
  heap-promoted ζ blocks (coexpr/suspend — each carries its scope's kind map id in its header) ·
  `g_proc_arena` live depth (until it folds into ZL-FN, ZB-3) · `g_call_args` marshaling window ·
  machine registers at a SAFE-POINT ONLY (see 6d).
* **What never moves:** sealed RO blobs (`[rip+disp]` — outside the heap by construction); the ζ-stack;
  the GVA arena; code.

### 6c. The coupling, stated as design

COLLECTION v2 backing = GC blocks (header: type=ZCOL, elem_map_id, cap, mark). Value-world blocks = GC
blocks (header: DT-derived type, size, mark — the SIL title word reborn). ONE bump allocator serves the
heap too (heap alloc between regenerations is bump — the SIL way), so the ζ-stack and the heap are two
bump arenas with different release disciplines: LIFO mark/release vs mark-adjust-slide. **A user
variable's DESCR cell itself** lives in NV/GVA/ζ-frame (a root or a mapped slot); what the GC manages is
the BLOCK its `.p` points at. That is exactly Lon's split: "GC used for dynamically created DESCR for
user VARIABLES" = family (B); "GC and the COLLECTIONS go together" = family (A) shares the heap, the
header discipline, and the collector.

### 6d. Safe points & the register question

v1: collections triggered ONLY at allocation sites inside `rt_*` helpers (the classic design — SIL
regenerated inside its allocator). At that boundary the box ABI has no live heap pointers in scratch
registers that aren't also in mapped slots — EXCEPT the scan registers: Σ (r13) points INTO a subject
string block. Two options: (i) pin the current subject block (a one-slot root cell the scan-enter
writes), or (ii) treat subject strings as non-moving for v1 (allocate them in a pinned sub-arena).
Option (i) is cleaner and one store per scan-enter. δ/Δ are integers. rZ points at the ζ-stack
(non-heap) or a promoted block (a root). This is a DESIGN DECISION ROW in §8.

### 6e. The SN4-GC ladder (built AFTER ZB-4/ZB-5; designed-for NOW via the kind column)

- [ ] **GC-0 HEADERS** — block-header discipline `{type, size, mark}` behind the existing allocation
      entry points on a scrip-owned bump heap; libgc still resident (coexistence: scrip heap for new
      families, libgc for compiler-side allocations).
- [ ] **GC-1 MARK** — trace from the §6b root set; `--dump-heap` inspector (the --dump-zeta sibling).
- [ ] **GC-2 ADJUST** — per-type relocatable maps (DESCR-derived + zl typed field maps + COLLECTION element maps);
      linear new-address computation.
- [ ] **GC-3 SLIDE** — the compaction memmove; free pointer reset; post-slide verify pass under a flag
      (every root's target has a valid header).
- [ ] **GC-4 COLLECTIONS-ONTO-HEAP** — COLLECTION v2: realloc/free replaced by GC blocks; owner-quad
      fixup proven by a forced-collect-inside-ARBNO probe.
- [ ] **GC-5 VALUE-WORLD MIGRATION** — strings/ARBLK/TBBLK/DATINST/VCELL onto the heap, family by
      family, oracle-pinned each.
- [ ] **GC-6 RETIRE-LIBGC (SNOBOL4 path)** — per-path; Icon coexpr transport may keep libgc longer.
- [ ] **GC-7 PACING** — allocation-threshold trigger, &STLIMIT semantics, `COLLECT(i)` builtin wired to
      a real regeneration (crosscheck 082-family finally honest); bench vs libgc.

---

## 7. Icon — Procedure-Level and Co-Expression-Level Partitioning (Lon directive, 2026-07-05)

Icon has the same challenge as SNOBOL4, less dynamic, and needs TWO explicit partitions:

### 7a. Procedure level → ZL-FN

Params at ABI `16*(i+1)` (continuity with the landed driver/`rt_frame_bind_args` contract), locals
above, resume cell for generator procs, ret-γ/ω continuation cells in the header region.
`static`/`initial` stay OUT of ζ (persistent → GVA arena; the mangled-GVA precedent is the model).
`g_proc_arena` + `bb_callee_frame` fold INTO the ζ-stack at ZB-3 (an activation is a ZL-FN bump, not
an arena row). **Icon suspend:** a suspended activation outlives its return — its ZL-FN block
HEAP-PROMOTES (GC block, family A) at suspend (or at α of a proc statically known to suspend);
until the promotion rung lands, the existing GATE holds (no suspendable box inside a bump-lifetime
scope).

### 7b. Co-expression level → ZL-COEXPR (new class)

A co-expression is a CAPTURED ACTIVATION: `create e` snapshots an environment; `@` transfers control
into it; results transfer back; `^e` REFRESHES it to its creation state. It breaks LIFO at birth —
so ZL-COEXPR blocks are heap-lifetime (family A) from creation, never bump-lifetime.

**Options considered for the execution substrate:**

| Option | What | Pros | Cons |
|---|---|---|---|
| **O1 — pthreads transport (LANDED)** | `rt_coexpr.c` pthread+semaphore; each coexpr owns a thread (its own machine stack); `bb_create/bb_activate/bb_coret/bb_cofail` templates; CREATE k+=4 | Already end-to-end both modes (2026-07-01 RUNGs 1-5); real OS substrate; sidesteps continuation plumbing | Heavy per coexpr; per-thread zS/rZ plumbing needed once ζ-stacks exist; MODE34 text-side must mirror |
| **O2 — single-thread ζ-plane swap** | seed-5/6 law at scale: coexpr = ONE heap ZL-COEXPR block (its ζ plane + its OWN ζ-substack pointer + stored continuation cells, the 4/28 `P_X_ret_γ/ω` pattern relocated INTO the block); `@` = save current (rZ,zS,resume-label) into the source plane, load the target's, `jmp` its resume | Stackless-pure; cheap activation (a few moves + jmp); refresh/clone trivial; no threads | Continuation cells must be stored per plane (the machinery M2 had in statics, now per-block — fine); C-transport interop (rt_* helpers mid-coexpr) needs care |
| **O3 — hybrid (RECOMMENDED v1)** | Keep O1 as TRANSPORT; adopt the ZL-COEXPR PLANE regardless: each coexpr body's boxes address rZ = its own promoted block; per-coexpr zS sub-arena (its bump region) | The plane is the DESIGN, the thread is transport; O2 becomes a later swap-out with zero layout change | Two mechanisms alive until the swap |

**Refresh `^e` is where the CLONE TIER earns its return:** refresh = restore the block to its
creation-time image ⇒ store a creation SNAPSHOT (the template-clone memcpy, per-coexpr rather than
per-type) beside the live block; `^e` = memcpy snapshot→live + reset its zS. Zero-fill v1 does not
cover this — refresh restores the CAPTURED environment (bound locals at create time), not zeros. This
is the one place §5e's deferred clone machinery is already known to be needed.

**Per-coexpr ζ-substack sizing** rides the HUGE principle: reserve big, commit small, bomb loud, tune
from telemetry.

---

## 8. Decision Rows (the fork, made explicit — Lon rules each)

| # | Decision | Options | Recommendation | Status |
|---|---|---|---|---|
| D1 | rZ register | r12 / r15-promote | **r12** (continuity, ratified, callee-saved) | per ZB-ALLOC; confirm |
| D2 | zS home | slab cell / register / .bss | **slab `[rbx+ZS_OFF]`** | per ZB-ALLOC; confirm |
| D3 | Arena Stage-α size | 256 MiB RW / 1 GiB reserve+commit | **HUGE per Lon; exact number after a container check** | OPEN |
| D4 | zl[] kind column now | now / retrofit | **NOW** (one byte; it's the GC stack map; ZB-2 touches every grant once) | OPEN |
| D5 | ZL-GROUP granularity v1 | disjoint label-groups / liveness-unioned | **disjoint** (unioning deferred) | per ZB-ALLOC; confirm |
| D6 | Init v1 | zero-fill / clone | **zero-fill** (4/28 evidence: all dq 0); clone machinery kept in design for ^e + future nonzero images | per ZB-ALLOC; confirm |
| D7 | COLLECTION backing v1 | heap realloc / ζ-stack frames | **heap realloc** (Lon directive); v2 = GC blocks | RULED (collections; "ZLA/array" naming retracted same day) |
| D8 | Coexpr substrate | O1 / O2 / **O3 hybrid** | **O3**: keep pthread transport, adopt ZL-COEXPR planes now | OPEN |
| D9 | GC scope | replace libgc everywhere / **per-path coexist→retire** | coexist (GC-0..5), retire SNOBOL4 path first (GC-6) | OPEN |
| D10 | Scan-subject pinning at safe points | pin-cell at scan-enter / pinned string sub-arena | **pin-cell** (one store per scan-enter) | OPEN |
| D11 | ZB-6 milestone-certify timing | before ARBNO unpause / after | **before ZB-5** — the 4/28 run is the fidelity pin for the chunk semantics being brought forward | OPEN |
| D12 | Continuations home | ZL-FN header cells (evicted from statics) | forced by no-.bss; **header cells** | confirm |
| D13 | α/β R12 self-load hook (§5h) | build now toggleable / defer | **BUILD NOW, OFF by default** — two central x86() sites, zero per-template edits, the standing A/B lever; source option (a) plane-cell when experimenting | OPEN (Lon named it QUICK — recommend rule YES) |
| D14 | ZLS itself onto the GC heap (§5i O-HEAP/GC-bump-slide) | end-state unification / keep hybrid | keep **hybrid v1**; REVISIT AFTER GC-3 proves slide — the model was never the problem, the allocator was | OPEN (deliberately deferred fork) |
| D15 | ZC_* defaults (§5j, `zeta_choices.h`) | as authored / adjust | **as authored**: INFINITE+MALLOC-collections+SELFLOAD-OFF+ZERO+FILL+TELEM+BOMB+1024MB+GATE; flip ZC_ALLOC→LIFO at ZB-3 close | OPEN (confirm defaults) |

---

## 9. Relationship to Standing Rules (nothing here contradicts them)

* **PER-BOX LOCAL STORAGE FACT RULE** — unchanged; this document defines the RW side's ALLOCATION.
  Every reference stays (RO) `[rip+disp]` or (RW) `[rZ+off]`.
* **STACKLESS / ONE-REGISTER FRAME** — preserved; `.prev` replaces push-r12; rZ MOVES (that was always
  the 4/28 truth; M5's fixed-r12 was the deviation).
* **TMP-ERADICATE** — `zl_build()` is its COMPLETION, not reversal: LOWER (via the post-optimizer pass)
  owns the ENTIRE layout; `drive_value_slot` degenerates to a zl read; the emitter allocates nothing.
* **PEERS RULE** — zl[] is a parallel table; zero new IR_t/BB_t fields.
* **THE EMITTER NEVER MUTATES IR** — zl is read-only to the emitter; `test_gate_emit_no_ir_mutation.sh`
  stays hard-zero.
* **NO .bss / MODE34** — struc/endstruc overlays (`ZG_/ZF_/ZP_/ZI_/ZC_`), displacement-identical bytes
  both modes; new no-.bss gate at ZB-4.
* **LANG FACT RULES** — layout DECISIONS per language live in each LOWER; zl[], the allocator, the COLLECTION
  runtime, and the GC are language-blind.
* **DIVISION RULE** — resumability stays ω-wiring; a COLLECTION owner's β is Byrd resume, not a stored flag.
* **ARCH-x86 / ARCH-ICON corrections** — their "fresh DATA per α-entry" / "per-box arena indexed by
  depth" lines were the ASPIRATION this document now gives a MECHANISM; read them through this file.

## 10. Reading List (the primary sources, all verified on disk this session)

Seeds: `SCRIP/seed/test_sno_1..6.c`, `test_icon.c`. 4/28 era (one4all@`4757bbcd`):
`artifacts/asm/beauty_prog.s` (fn_upr site ~:8437; box_*_data_template field maps),
`archive/backend/snobol4_asm.mac:2040-2077` (ARBNO), `archive/backend/blk_alloc.c`,
`archive/backend/emit_emitters/emit_x64.c`. Current-tree study set:
`SCRIP/artifacts/asm/fixtures/arbno_alt.s` (156 lines; `.bss arb3_stack resq 64` — the enemy, visible),
`SCRIP/archive/backend/bb_boxes.s`. Live spine: `src/contracts/scrip_ir.c:206` (`ir_drive_slot_assign`),
`src/contracts/IR.h` (IR_t), `src/templates/xa_flat.cpp` (prologue), `src/runtime/rt/rt.c:348`
(`g_proc_arena`), `src/emitter/emit.cpp:980/984/996` (`x86_scratch_off` stages), `src/contracts/descr.h`
(DESCR_t). History: one4all `03acf1be` `50a6d07a` `267429d0` `254dedb9` `dd17db1a` `2ede32bd`; SCRIP
`e8e728cc` `a8993f46` `aa587c99` `b27e06ee` `d671e68f` `ad613052` `ed0ac777` `79448a32`. Archive docs:
`BB-GEN-X86-BIN.md` `BB-GRAPH.md` `BB-DRIVER.md` `GENERAL-BYRD-DYNAMIC.md` `MILESTONE_BONE_PILE.md`.
SPITBOL manual v3.7 (uploaded): GC/&MAXLNGTH ch.5; storage-regeneration relocatable words, external
functions chapter; `COLLECT(i)`.
