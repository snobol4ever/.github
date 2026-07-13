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
| **zls[]** | The parallel layout table (node-id → scope_id, offset, kind), built by `zls_build()` post-optimizer. PEERS-clean: zero new `IR_t` fields. Implemented 2026-07-05: `SCRIP/src/contracts/zeta_storage.{h,c}`, API prefix `zls_*` (Lon: ZLS naming — GST/GVA global-side ↔ ZLS local-side; no LVA concept). |
| **t·p** | The 16-byte DESCR_t slot unit (`{DTYPE_t v; uint32_t slen; union{s,i,r,p,arr,tbl,u}}`, `src/contracts/descr.h`). All ζ offsets are multiples of 16. |
| **IR_t.tmp** | The LOWER-granted frame offset on a node (`src/contracts/IR.h:156`). Today: one flat namespace. Tomorrow: a read of zls[]. |
| **ψ (psi)** | The moving element pointer into a COLLECTION (seed-2 idiom: `ψ13 = &ζ->_13_a[i]`). Distinct from the enclosing frame's ζ. |
| **λ (lambda)** | The landing port: post-child-call emptiness test routing to γ/ω (seed-2/3/4 idiom). |
| **Clone tier / cheap tier** | 4/28-era activation modes: memcpy a `.data` init template into a fresh block vs `lea r12,[rel template]` (run IN the static template — the single-activation bet). |

**⛔ THE TYPED PRINCIPLE (Lon, 2026-07-05).** ZLS is not a value store; it is the compiler's OWN
per-activation struct. Its fields have individual types and sizes known at zl-build time. Consequences:
(1) the zls[] map is a per-FIELD typed map, not a per-slot DESCR/non-DESCR bit (§4); (2) GC scanning of
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
PRE-EMIT into the parallel `zls[]` table, **COLLECTIONS** (realloc-grown per-iteration storage owned by
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
per-class lifetime. The emitter contract stays: read `(scope_id, off)` from zls[] ONLY, emit
`[rZ+disp]`, both modes byte-identical.

---

## 4. The Layout Classes

Built by `zls_build(g)` (zeta_storage.c) post-optimizer / pre-emit over the scope tree
**program → DEFINE/procedure body → label-group (labeled stmt + trailing unlabeled) → re-entrant box**.
Groups laid DISJOINT v1 (lifetime-unioning deferred until real liveness info exists). PEERS RULE: the
table is parallel, keyed by node id; zero new BB_t/IR_t fields.

* **ZL-GROUP** — label-group frame: every non-re-entrant box instance's fields — temporaries, one-shot
  scratch, resumable generator slots, call marshaling. **THE GLOB IS THE ALLOCATION GRAIN (Lon,
  2026-07-05 third session): ONE α-entry alloc / ONE exit release per GLOB activation covering every box
  inside — never per-BB. Each SNOBOL4 statement is a GLOB; each labeled sequence of statements is a GLOB.
  Allocation volume ∝ statements executed — this is also what makes ZC_ALLOC_MALLOC a usable per-glob-lifetime
  ASan instrument (see the §5j MALLOC ceiling empirics).** Absorbs the dead SM tier's expression
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

**zls[] entry (proposed, per the TYPED PRINCIPLE):** node side `{ int scope_id; int off; }` PLUS a
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

**AUDIT BURNDOWN — COMPLETE 2026-07-05 (fourth session same day; every shipped grant template-verified,
audit=0 repo-wide; `.s` byte-identity stash-proven — kinds/granularity metadata only, zero layout change).**
The standing rule from here: any NEW grant lands `audit=1` until its template is read. Verdicts that
CHANGED something (full evidence in the templates cited):
* **REV_ASSIGN(_VAR) `+16` was the real catch — RAW→DESCR.** `bb_rev_assign{,_var}.cpp` save the variable's
  OLD VALUE as a full t·p pair into `op_sc = off+16` and restore it on β — LIVE across the suspension window
  (γ-exit…β-resume), exactly where a collection can run. Marked RAW, a precise collector skips a live heap
  ref → premature collection. This one field is the burndown's justification.
* **SCAN_ENTER's map was MISLABELED (both fields, one non-audit):** the node is not in
  `ir_node_produces_value` and its ENTER arm never touches its own slot; IR_SCAN (the leave) aims its
  `op_off` at the ENTER's slot as a 24-byte `rt_scan_leave` out-area: `+0`=σ (heap-interior, TRANSIENT —
  written and reloaded into r13 with zero rt-calls between → dead at every v1 safe point, RAW honest),
  `+8`=δ, `+16`=Δ, `+24` unused. The old "+0 scan.value DESCR" would have made GC-1 trace a raw pointer as
  a t·p pair.
* **CREATE cells = pure marshaling:** `scrip_coexpr_create` COPIES regs[0..5] into its malloc'd pkg before
  returning → the six ζ cells (r12,r13,r14,r15,rbx,rbp) are dead at call-return, RAW, now per-field named.
  The HANDLE low qword is a raw malloc'd `ctx*` (never trace/relocate; also not a tagged DESCR — a coexpr-rung
  matter, noted there). The snapshot's GC exposure moved WITH the copy into pkg — see the §6b root additions.
* **Everything else = verified pads/ints, split to honest 8B granularity:** INITIAL once-flag lives at `+8`
  (low half unused); ITERATE `+16` = 8B index (α=0, β inc), `+24` pad; REPALT `+16` = 8B yielded flag;
  LIMIT/`SCAN_TAB`/`SCAN_MOVE`/gate/resume `+24`/`+8` pads confirmed untouched by their templates.

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
reclaimed, never what a template does. Switching an axis touches the allocator/zls units only; the ~161
templates are untouched by construction.

**The header:** `SCRIP/src/contracts/zeta_choices.h` (authored 2026-07-05; additive — included by the
allocator + zls units only, nothing else in the tree references it yet). Every axis is `#ifndef`-guarded,
so `make CFLAGS+='-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO'` swaps a mode with zero edits. One value per axis;
statically-illegal combinations are `#error`s in the header; combinations only checkable at run time
bomb LOUD.

| Axis | Modes | Default (experimental era) | Rationale from history |
|---|---|---|---|
| **ZC_ALLOC** — activation allocator | `BUMP_INFINITE` / `BUMP_LIFO` / `MALLOC` / `GC` | **BUMP_INFINITE** | INFINITE = monotone bump, NEVER releases, arena HUGE: removes REUSE from the suspect list entirely — any bug under INFINITE is layout/wiring, never lifetime. The testing mode Lon named. `BUMP_LIFO` = the v1 design (§5c) — flip the default at ZB-3 close. `MALLOC` = every scope block is a real heap object ⇒ ASan/valgrind catch overruns and use-after-release for free (M1's model resurrected as a DIAGNOSTIC — its churn is now the feature; ZB-3 empirics: per-block GC_add_roots caps concurrent live activations at libgc MAX_ROOT_SETS — f(2000) passes, f(6000) bombs 'Too many root sets'; GLOB-grain activation is the designed fix — volume ∝ statements). `GC` = §5i end-state; `#error` stub until GC-3. |
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

**MANUAL PINS (extracted 2026-07-05, fourth session, from the uploaded SPITBOL v3.7 manual — the pins the
ladder header mandates; page refs = the manual's printed pages via its own index):**
1. **Tag-free discrimination is the SIL cost we DROP (ch.5 p.53 + ch.13 `-m`):** the SIL/SPITBOL collector
   tells small integers from addresses BY MAGNITUDE — hence the `&MAXLNGTH` object-size cap (default 4MB,
   `-m` bound) AND the constraint max-object-size < workspace start address (memory below it is wasted).
   SCRIP's DESCR tags (§6b) make both costs vanish: no size cap, no address floor. GC-5 note: `&MAXLNGTH`
   survives as a compat keyword only, never a real limit.
2. **`COLLECT(i)` contract (p.216) — the GC-7 oracle:** forces a regeneration; `i` = MINIMUM words to free
   (Catspaw word = 4 bytes); **FAILS** if that minimum can't be met; on success returns the free-word count —
   which is explicitly NOT max-available, because SPITBOL grows from the OS when full. "Forcing garbage
   collections before they are necessary will always increase execution time" — the pacing warning, verbatim-
   in-spirit. Return-value divergence is BLESSED by the manual itself ("values returned will be different
   because of different internal representations") — SCRIP returning its own honest unit is canonical, the
   082-family crosscheck refs pin OUR unit.
3. **Relocatable-words discipline (pp.320–321) — the GC-2 contract:** per-block-TYPE knowledge of which
   words are relocatable; a relocatable word points at the FIRST WORD of another heap block (head pointers,
   NOT interior — SCRIP's σ interior-string pointer is exactly the exception D10's pin exists for); adjust
   is automatic at regeneration; "all words within a block must be properly filled in" before it goes live
   (the adjuster reads every mapped word — `ZC_INIT_ZERO` is our mechanical discharge of that rule); XNBLK
   external blocks are ALL-non-relocatable by definition — the direct precedent for our RAW kind and for the
   conservative-never-relocate treatment of register-snapshot cells (§6b coexpr finding).
4. **`&STLIMIT`/`&STCOUNT` (keywords ch. + p.65):** `&STLIMIT` default = 2,147,483,647; exceeding it = Error
   244; `&STCOUNT` increments as each statement BEGINS — **except when `&STLIMIT` is negative (unlimited
   mode), where `&STCOUNT` is NOT incremented** (a carve-out any honest 082 fix must honor). Design
   convergence worth naming: statement = GLOB (Lon, ZB-3), so the GLOB α-prologue is the ONE natural hook
   for statement counting — the ζ activation and the `&STCOUNT`/`&STLIMIT`/GC-pacing hooks all land at the
   same grain, one inc beside the frame alloc.

### 6b. Why SCRIP can do this PRECISELY (better than SIL could)

* **Tags exist.** `DESCR_t {v, slen, union}` discriminates pointer from integer by TYPE, not by address
  range — DT_S/.s, DT_A/.arr, DT_T/.tbl, DT_DATA/.u, DT_P, DT_N (slen-discriminated
  NAMETRAP/NAMEPTR/NAMEVAL), DT_E vs DT_I/.i, DT_R/.r. The &MAXLNGTH-style small-int-vs-address hack is
  unnecessary. Per-block relocatable maps derive from the block type + the DESCR layout.
* **The zls[] typed field maps ARE the stack maps.** The live ζ region `[current-mark chain … zS]` is
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
  · live ζ region via zls kind maps · COLLECTION owner quads (via the same maps) + the grown-collection lists ·
  heap-promoted ζ blocks (coexpr/suspend — each carries its scope's kind map id in its header) ·
  `g_proc_arena` live depth (until it folds into ZL-FN, ZB-3) · `g_call_args` marshaling window ·
  machine registers at a SAFE-POINT ONLY (see 6d) ·
  **[ADDED 2026-07-05, GC-1-prep audit burndown — two roots the original enumeration missed, found by
  reading the templates+runtime rather than the design:] (i) the C-side static `scan_stack[SCAN_STACK_MAX]`
  (gen_runtime.c) — nested-scan save of the OUTER `{sigma, delta, Delta}`; each `sigma` is a heap-interior
  string pointer held live across the ENTIRE inner scan (arbitrary code, arbitrary allocation) — a root, or
  covered by D10's pin generalized to the whole save stack. (ii) coexpr `ctx`/`pkg` structs
  (rt_coexpr.c) — plain `malloc`, INVISIBLE to libgc today AND absent from this root set: `pkg` holds the
  creator's captured register snapshot (r12=rZ, r13=σ possibly heap-interior, rbx, rbp) for the coexpr's whole
  lifetime. LATENT BUG (v1, pre-existing): a string reachable ONLY via a suspended coexpr's captured σ can be
  collected under libgc today (masked in practice because the creator's frame usually also holds the ref).
  Fix home = the coexpr rungs (O3/promotion): allocate ctx/pkg GC-visibly or register them as conservative
  roots — snapshot cells are conservative by nature (a captured r13 outside any scan is garbage; a precise
  trace+fix over them is UNSOUND — treat as conservative-scan-only, never relocate-through).**
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

**[RESOLVED v1, 2026-07-05 GC-1/2/3 session — with the WHY from the true oracle:] `silly/arena.c
GC_fn` (v311.sil GC line 1367) shows SIL's allocation-site trigger is safe by INVARIANT, not
mechanism — the descriptor stack IS an arena block whose title.v gets refreshed to current used
length at GC entry (`SETSIZ STKPTR`, arena.c:391-395), so every live value is in enumerable arena
storage at every ALLOC; the interpreter never holds arena refs in machine state across it. SCRIP's C
helpers violate exactly this (concat's src locals), and the conservative patch for it (C-stack scan)
ratchets the slide (§6e GC-1/2/3 note). v1 resolution: allocation-site collect survives only as the
exhaustion fallback (conservative, rare); the working trigger is DEFERRED-PENDING consumed at the
runtime gateway seams with in-flight DESCRs shielded as precise roots — restoring total enumerability
at the moments that matter. Option (i) realized as pin-the-block (`gen_gc_roots` pins scan_subj's
block; outer subjects restore through scan_stack and adjust precisely). The end-state remains ZB-4
map emission + the GLOB α-prologue statement hook (GC-7), which retire both the ζ validated-adjust
heuristic and the exhaustion-flavor conservatism.**

### 6e. The SN4-GC ladder (built AFTER ZB-4/ZB-5; designed-for NOW via the kind column)

- [x] **GC-0 HEADERS — LANDED 2026-07-05 (Fable, Lon-directed session: "ZLS via GC just like in SIL").**
      `src/runtime/rt/gc_heap.{h,c}`: scrip-owned bump heap (mmap NORESERVE, ZC_HEAP_MB=512, loud bomb on
      exhaustion naming the knob — Stage-α discipline, no collector yet). ONE 16B header per block = the SIL
      title DESCR reborn: `{fwd(8) ↔ title.a.i forward-address home for GC-2; size(4) ↔ title.v, TOTAL bytes
      16-aligned for the linear walk; type(2) = DTYPE_t VERBATIM for value blocks (DT_S=1 first) or HB_ZCOL/
      HB_ZPROM above the range; flags(2) with HBF_TTL always set ↔ the SIL TTL marker, HBF_MARK reserved}`.
      `rt_gcheap_verify()` linear title walk (asserts TTL+alignment+bounds, counts blocks) runs in the
      `SCRIP_ZETA_TELEM` exit report `[ZHP]` — the runtime-side seed of GC-1's `--dump-heap`. Payloads
      zero-initialized (manual pin 3 discharged the ZC_INIT_ZERO way). **Coexistence contract stated in the
      module header:** scrip blocks aren't libgc objects (never freed by it); libgc ignores non-heap pointers;
      the migrated family is ATOMIC so a scrip block can never be a libgc object's sole liveness holder —
      pointer-bearing families must NOT migrate before their GC-5 row. **Lon ruling (2026-07-05, post-landing):
      the libgc coexistence is TRANSITIONAL, not a design stance — the `ZC_HEAP_STRINGS` switch stays for
      testing while ours matures ("we can have both for a while"); retirement (GC-6) is the destination.**
      **PROOF (Lon-chosen scope): the DT_S
      strings row of GC-5 wired through NOW** — `rt_str_alloc(n)` is THE entry point (n chars + NUL), switch
      inside the function: `ZC_HEAP_STRINGS` (zeta_choices.h, default SCRIP; `-DZC_HEAP_STRINGS=0` = the
      intact libgc-atomic fallback, proven by a one-object rebuild giving identical output). 24 explicit-length
      producer sites migrated across pattern_match.c (14: captures, dcap, subject int/real→str, replace/
      substr/rand paths), gen_runtime.c (rt_substr), core/coerce.c (descr_to_str int+real), string_ops.c
      (concat), string_builtins.c (DUPL/binary-REPLACE/UTF8-SUBSTR/TRIM/LPAD/RPAD/REVERSE/CHAR), arithmetic.c
      (cset complement). Churn probe (50-concat loop + every builtin + capture) == oracle in BOTH modes with
      `[ZHP] blocks=57(alloc'd)=57(walked) verify=OK`; full crosscheck byte-identical to baseline (m3 172/89,
      m4 172/3/86, DIVERGE=0) with the whole corpus on the heap; icon 12/12×2; emit gates + sno_pat_reg rc=0.
      **Strings-row TAIL for GC-5:** 9 `GC_strdup` copy sites (string_builtins width<=slen shortcuts etc.) —
      mechanical `rt_str_dup` migration when the row completes. NOT migrated by design: DESCR arrays
      (string_ops.c:27), VCELLs, keys arrays, the capture stack u32[] (family A), all Prolog Term machinery.
- [x] **GC-1 MARK + GC-2 ADJUST + GC-3 SLIDE — LANDED 2026-07-05 (Fable, Lon-directed "mark, slide and adjust"; CSNOBOL4 cross-audit same session).** The SIL 3-stage storage
      regeneration lives in `gc_heap.c` (`rt_gc_collect` + `gc_collect_ex`), v1 scope = the resident DT_S strings family. **TWO ROOT LAYERS:** PRECISE (marked AND adjusted; dedup/cycle
      hash makes every cell adjust EXACTLY once) = NV buckets incl. bound GVA cells (`core_gc_roots`) · `_var_reg` · `g_call_args` window (`rt_gc_root_args`) · drive_val + gen frames +
      scan_stack σ/subj (`gen_gc_roots` — restored FROM MEMORY at leave, hence adjustable) · full aggregate tracing through libgc-owned ARBLK/TBBLK/DATINST/VCELL/NAMEPTR (aggregates
      don't move; the DESCR cells inside them adjust) · **the live ζ chain in VALIDATED-ADJUST mode** (`gc_zeta_frame`: DESCR-shaped pairs `v==DT_S` + head-exact + slen-plausible adjust
      as descriptors, bare in-arena qwords (σ saves) adjust as raws — under a strings-only heap any in-arena qword in a live frame IS a string ref; the residual integer-collision risk is
      SIL's magnitude-discrimination heritage reborn (manual pin 1 parallel), retired when ZB-4 emits the zls maps into binaries). CONSERVATIVE (marked and PINNED `HBF_PIN`, fwd=self,
      never moved) = C stack + setjmp register spill, **EXHAUSTION FLAVOR ONLY**. **THE TWO FLAVORS (the session's central finding):** collecting inside `rt_gcheap_alloc` conservatively
      pins the topmost blocks (the triggering helper's own locals) and with bump-from-top allocation ANY top pin makes all reclaimed space below unusable — the ratchet: 2,710 collections,
      773KB monotone, reclaimed 0. Gateway collects are therefore FULLY PRECISE (SIL-pure, pinned 0): `SCRIP_GC_STRESS`/pending sets `g_gc_pending`, consumed at the runtime seams the .s
      call-surface audit found — `rt_call_arr` (every call-shaped op) · `rt_assign_var` (pattern/indirect assign) · `rt_gvar_assign_{str,descr,var,int}` · `rt_arg_stage` · `rt_scan_enter`
      · `rt_zls_alloc` — each SHIELDING its in-flight DESCRs as extra precise roots (`rt_gc_point`/`rt_gc_point_arr`, adjusted not pinned). Exhaustion inside the allocator keeps the full
      conservative scan (sound; residual ratchet risk documented — corpus never nears 512MB). SLIDE: dest cursor; pins are barriers; sub-pin gaps get `HB_FILL` dead-filler titles so the
      linear walk verifies (fillers compact next cycle); the contiguous live prefix gets fwd==self ⇒ no memmove ⇒ SIL's MVSGPT frontier behavior emerges from the pin condition (convergent,
      confirmed against `silly/arena.c` GCLAD/GCLAM); adjust skips fwd==self (GCLAP `>= mvsgpt` analog). Coexprs: any created coexpr ⇒ collection DECLINES with an honest stderr note
      (§6b finding ii; `g_scrip_coexpr_live`; fix home = coexpr rungs). `[ZGC]` telemetry under `SCRIP_ZETA_TELEM`. **EVIDENCE:** churn probe (60 keeps + table + 4000-iter DUPL churn)
      == oracle in BOTH modes plain AND `SCRIP_GC_STRESS=3` — 2,707 regenerations, heap PLATEAU 2.4KB (was 773KB monotone), reclaimed>0 every cycle, pinned 0 fill 0; pattern/capture
      probe == oracle plain + STRESS=2 (751 collections, σ pin + captures allocating mid-scan); **full crosscheck plain = exact baseline** m3 172/89 · m4 172/3 {082,099,213}/86 ·
      DIVERGE=0; **crosscheck under STRESS=25 = IDENTICAL counts AND fail-sets** (the MODE-INVARIANCE gate applied to collection — behavior-invisible, 36s vs 35s); icon hard gate 4/4 +
      all_rungs == pristine-HEAD (stash-proven); emit gates ×3 + sno_pat_reg rc=0.
- [ ] **GC-4 COLLECTIONS-ONTO-HEAP** — COLLECTION v2: realloc/free replaced by GC blocks; owner-quad
      fixup proven by a forced-collect-inside-ARBNO probe.
- [~] **GC-5 VALUE-WORLD MIGRATION** — strings/ARBLK/TBBLK/DATINST/VCELL onto the heap, family by
      family, oracle-pinned each. **(Strings row LANDED 2026-07-05 with GC-0 — Lon-directed proof family;
      tail = 9 GC_strdup copy sites via a mechanical rt_str_dup. ARBLK/TBBLK/DATINST/VCELL remain.)**
      **Strings-row TAIL — LANDED 2026-07-06 (Claude Sonnet 5): `rt_str_dup(const char*)` added beside
      `rt_str_alloc` in `gc_heap.{h,c}` (thin wrapper: strlen + rt_str_alloc + memcpy, so both heap paths
      stay in sync automatically, zero switch-logic duplication). Migrated 6 value-world DESCR-copy sites:
      `string_builtins.c` DUPL/SUBSTR empty-string shortcuts + LPAD/RPAD width<=slen shortcuts (4),
      `arithmetic.c` cset-complement base-string copy (1), `pattern_match.c` int-to-string conversion
      result (1). **Deliberately NOT migrated:** `pattern_match.c:709,836` (`vc->key = GC_strdup(...)`) —
      VCELL internal hash-bucket keys, not DESCR_t value-world payloads; out of this row's family-B scope
      per §6/§6b, not audited against the root enumeration. **VERIFIED both ZC_HEAP_STRINGS switch
      positions** (scrip heap default + `ZCFLAGS='-DZC_HEAP_STRINGS=0'` libgc-atomic fallback, real
      Makefile rebuild): crosscheck IDENTICAL both ways (m3 252/276, m4 251/9/16, DIVERGE=1, same FAIL
      sets). Also identical under `SCRIP_GC_STRESS=25` and Icon smoke 12/12×2. ARBLK/TBBLK/DATINST/VCELL
      still remain — this closes only the strings-row tail, not GC-5 as a whole.**
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
| D3 | Arena Stage-α size | 256 MiB RW / 1 GiB reserve+commit | **HUGE per Lon; exact number after a container check** | **RULED 2026-07-05 (Lon): 1024 MB — "we'll see when it breaks"** (container check: mmap MAP_NORESERVE reserve + GC_add_roots in 8MB high-water chunks — scan cost ∝ usage not reserve; frames MUST be GC-visible, they hold DESCR refs; telemetry stays ON to catch the break) |
| D4 | zls[] kind column now | now / retrofit | **NOW** (one byte; it's the GC stack map; ZB-2 touches every grant once) | OPEN |
| D5 | ZL-GROUP granularity v1 | disjoint label-groups / liveness-unioned | **disjoint** (unioning deferred) | per ZB-ALLOC; confirm |
| D6 | Init v1 | zero-fill / clone | **zero-fill** (4/28 evidence: all dq 0); clone machinery kept in design for ^e + future nonzero images | per ZB-ALLOC; confirm |
| D7 | COLLECTION backing v1 | heap realloc / ζ-stack frames | **heap realloc** (Lon directive); v2 = GC blocks | RULED (collections; "ZLA/array" naming retracted same day) |
| D8 | Coexpr substrate | O1 / O2 / **O3 hybrid** | **O3**: keep pthread transport, adopt ZL-COEXPR planes now | OPEN |
| D9 | GC scope | replace libgc everywhere / **per-path coexist→retire** | coexist (GC-0..5), retire SNOBOL4 path first (GC-6) | OPEN |
| D10 | Scan-subject pinning at safe points | pin-cell at scan-enter / pinned string sub-arena | **pin-cell** (one store per scan-enter) — v1 implemented as pin-the-block (`gen_gc_roots` pins scan_subj's block; register r13 unrewritable so the BLOCK stays put; outer subjects adjust via scan_stack) | OPEN |
| D11 | ZB-6 milestone-certify timing | before ARBNO unpause / after | **before ZB-5** — the 4/28 run is the fidelity pin for the chunk semantics being brought forward | OPEN |
| D12 | Continuations home | ZL-FN header cells (evicted from statics) | forced by no-.bss; **header cells** | confirm |
| D13 | α/β R12 self-load hook (§5h) | build now toggleable / defer | **BUILD NOW, OFF by default** — two central x86() sites, zero per-template edits, the standing A/B lever; source option (a) plane-cell when experimenting | **RULED 2026-07-05 (Lon): BUILD — sequenced AFTER D15** (order: D15 flip first, then this hook; OFF by default, ASSERT mode on the shelf for ZB-5 ARBNO bring-up) **— α-site LANDED 2026-07-05 fifth session (SCRIP `261cbbcb`): env-flippable at emit time, ASSERT full-corpus mode-invariance proven; β-define site = remainder; record in GOAL watermark**
**— β-site LANDED 2026-07-06 (Claude Sonnet 5): hook added inside `x86_pair_loop()` (`src/templates/x86_asm.h`), the sole flush point for every `DRIVE_PAIR_DEF_JMP(lbl_β,...)` staged by `emit.cpp` (confirmed by exhaustive grep — every populate-site across `src/emitter/` and `src/templates/` passes `lbl_β`, none other) — reaches all 5 direct callers (`bb_conjunction.cpp`, `bb_goto.cpp`, `bb_ite.cpp`, `bb_match_cat.cpp`, `bb_ref_invariant.cpp`) with zero per-template edits, same as the α-site. Self-contained (own `x86_zeta_selfload_mode()`/`x86_zeta_selfload_beta()` inline pair in `x86_asm.h`, not shared with emit.cpp's α-hook, to avoid touching already-proven code) but bit-identical ASSERT encoding (`test r12,r12 / jnz +2 / ud2`, both mediums). OFF-default byte-identity re-proven: full SNOBOL4 crosscheck unchanged (m3 252/276, m4 251/9/16, DIVERGE=1, same FAIL sets). ASSERT-mode canary checked and NEVER fired across SNOBOL4 crosscheck (276×2), Icon smoke (12/12×2), Prolog smoke (5/5×3), polyglot smoke (2/2×2) — the R12 wiring invariant holds at every β entry point in the live tree, not just SNOBOL4's. D13 both sites CLOSED.** |
| D14 | ZLS itself onto the GC heap (§5i O-HEAP/GC-bump-slide) | end-state unification / keep hybrid | keep **hybrid v1**; REVISIT AFTER GC-3 proves slide — the model was never the problem, the allocator was | OPEN (deliberately deferred fork) |
| D15 | ZC_* defaults (§5j, `zeta_choices.h`) | as authored / adjust | **as authored**: INFINITE+MALLOC-collections+SELFLOAD-OFF+ZERO+FILL+TELEM+BOMB+1024MB+GATE; flip ZC_ALLOC→LIFO at ZB-3 close | **RULED 2026-07-05 (Lon): defaults CONFIRMED; flip ZC_ALLOC→BUMP_LIFO — EXECUTE FIRST, before D13's hook** (LIFO full-corpus byte-identity already proven at ZB-3 — flip is one line in zeta_choices.h; re-run smoke+crosscheck on landing) **— EXECUTED 2026-07-05 fifth session (SCRIP `261cbbcb`): default = BUMP_LIFO; smoke+crosscheck byte-identity re-proven on landing** |

---

## 9. Relationship to Standing Rules (nothing here contradicts them)

* **PER-BOX LOCAL STORAGE FACT RULE** — unchanged; this document defines the RW side's ALLOCATION.
  Every reference stays (RO) `[rip+disp]` or (RW) `[rZ+off]`.
* **STACKLESS / ONE-REGISTER FRAME** — preserved; `.prev` replaces push-r12; rZ MOVES (that was always
  the 4/28 truth; M5's fixed-r12 was the deviation).
* **TMP-ERADICATE** — `zls_build()` is its COMPLETION, not reversal: LOWER (via the post-optimizer pass)
  owns the ENTIRE layout; `drive_value_slot` degenerates to a zls read; the emitter allocates nothing.
* **PEERS RULE** — zls[] is a parallel table; zero new IR_t/BB_t fields.
* **THE EMITTER NEVER MUTATES IR** — zls is read-only to the emitter; `test_gate_emit_no_ir_mutation.sh`
  stays hard-zero.
* **NO .bss / MODE34** — struc/endstruc overlays (`ZG_/ZF_/ZP_/ZI_/ZC_`), displacement-identical bytes
  both modes; new no-.bss gate at ZB-4.
* **LANG FACT RULES** — layout DECISIONS per language live in each LOWER; zls[], the allocator, the COLLECTION
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

---

## 7. M7 — THE 2026-07-11 CONSOLIDATION: BB-OWNED TWO-FLAVOR MM, REGIONS, AND THE ONE-ENTRY CONVENTION (Lon directives s21+s22; design of record — live work queue = `GOAL-SNOBOL4-BB.md` Phases 1–3)

**7a. The two MM flavors (Lon, verbatim intent).** Each BB generated with g_emit switches between TWO memory-management flavors: **ζ-on-STACK** (α decrements the cursor, ω increments; grows down — pure LIFO, which is exactly backtracking's nesting) and **ζ-on-HEAP** (α bump-allocates, ω marks-as-garbage; the ZH collector slides — provider already in-tree: `src/runtime/rt/zeta_heap.c`, `rt_zh_alloc`/`rt_zh_mark_dead`/handles/pin). The flavor is chosen per-KIND by LIFETIME (the s6 ruling, promoted through g_emit): control-flow-lifetime frames → stack; frames that ESCAPE control flow (IR_SUSPEND, IR_CREATE, IR_PROC_GEN, blob-carrying DEFER) → heap. **The escape set is expected to SHRINK toward coexpr-only once the one-entry convention (7c) lands** — most of today's "must survive a C return" class exists only because the C trampoline forces a return. Co-expressions already ride their OWN per-thread C stacks (consistent with stack flavor, one stack per thread). The current `ZC_PORT_*` ledger (`src/contracts/zeta_choices.h`) carries the flavors' scaffolding: CSTACK=4 (compiled default; rsp cursor for dynamic blocks + statement bracket), OWNED=5 (**rung-0 balance-proving SHADOW only — Lon s22: no shadow wanted; scaffolding, replaced as boxes start addressing the owned cursor for real at ZB-OWN-1**).

**7b. Regions — the hybrid that dissolves black-and-white ownership.** Today's split (BB-owned vs caller-owned; ζ allocated after vs before the jump into the BB) becomes a CONTINUUM: any straight branch-delimited sequence of BBs COALESCES into a **region** — a separate synthetic ENTER/handshake BB allocates for itself and the whole following block with recalculated region-relative offsets; interior boxes' own alloc/free are suppressed; region exits free. **BB-owned is the region-of-one; today's caller-alloc flat frame is the maximal region** — so caller-allocation is re-derived as an OPTIMIZER THEOREM, never an emitter assumption (the WALL rule applied to storage), and the gate is a dial: crosscheck must be identical at EVERY coalescing level, with max = today's frame byte-for-byte. Regions are VIEWS over the ONE stored IR graph (never a second structure), single-entry/single-exit (α/γ); inter-region branches are external jumps; regions nest; boundary-crossing values (the op_sa operand-slot protocol) are promoted to the parent region's frame — **a region is exactly the unit inside which slot-passing stays frame-relative**. Natural seeds: procedures/functions, whole statements, pattern portions — derived from the operand-recorded ranges the lowerer leaves behind (ARBNO body spans, ALT/capture T/F adjacency) + γ-threading, NEVER raw `g->all[]` allocation intervals (the scout's v0 finding: a bracket is allocated before the body it brackets). **This is CHUNKS, recovered.** γ-FREE LIVENESS: the read-only scout (`src/optimizer/region_report.c`, `SCRIP_REGION_REPORT=1`) already classifies every region GAMMA-FREE-SAFE (external β-in==0 ⇒ frame dead past its γ, freeable on success) vs HELD — proven live: a FENCE-seal region reports β-in=0 (the SPITBOL manual's "fails when the scanner backs up through it" IS mechanical γ-free safety) while an ARBNO HEAD reports HELD ("each retry supplies another instance" — the frame must outlive its γ). Computable only because of the s21 uniform-β wiring: every backtrack edge is an explicit sigil-marked IR edge.

**7c. The ONE-ENTRY CONVENTION (NCB — Lon s22: "Should always be C → BB → BB → BB (C call) → BB … RETURN to C in MODE 3! For mode 4 it's just main start").** Mode 3 has exactly ONE C→BB transfer: the driver MAIN branch. The graph runs BB→BB entirely in assembly land; C runtime helpers are STRICT LEAVES (a BB calls C, C returns to that BB, C never calls or jmps a BB); the graph returns to C once at program end. Mode 4: crt `_start` → libc → `main` = the emitted graph; same leaf rule. The co-expression pthread trampoline is sanctioned as a per-thread MAIN (fresh stack, 6-register contract, `jmp` not call, never returns). The seven current violations (proc-call trampolines, generator α/β from C, the C-called EVAL `call *%rax` shim) are ledgered with file:line in GOAL-SNOBOL4-BB.md Phase 1. **Why load-bearing:** the C-trampoline convention is the single root under (i) rsp-unreachability for BB-owned positioning (C frames interleave above BB frames), (ii) the blob-β wall (call/ret returns once and is dead; four-port jmp makes β an edge), (iii) the error-path C/BB-interleave SEGV class.

**7d. Register end-state (supersedes, for the end-state only, the ratified R12-frame reading of the GZ3 contract; as-built default remains ZC_FRAME_R12 until NCB lands).** **There is NO static BB local storage pointed at by r12 in the end-state — r12 is FREE (Lon s22). ALL control-flow ζ goes through the C stack**: rsp is the cursor (per-BB or per-region ENTER bumps, matched LIFO sub/add only — see 7e); rbp is also free (zero live template uses; callee-saved across C leaves) and is the CANDIDATE REGION-ζ BASE for the region model, where each region's boxes address `[ζ_reg + local_off]` and the entrance repoints ζ_reg. **The two RESTOREs must never be conflated (Lon s21):** cursor-ARITHMETIC restore at β is RETIRED (the ω landing on a β already put the shared cursor right); **REGISTER-restore of ζ_reg at β is REQUIRED** in the region model (`mov ζ, PARENT_FRQ(region_slot)`, the ARB/ARBNO save-slot pattern) because a β arriving from another region has ζ_reg aimed at the wrong frame.

**7e. THE NEVER-HOIST COMPOSITION RULE (proven live, ZB-OWN-0):** dynamic (runtime-count) allocations and static (emit-time) positioning share one cursor only if static positioning is FLOOR-ONLY — store iff strictly below; the dynamic RELEASE restores the ceiling. An unconditional absolute store hoists over live dynamic activation blocks and the next C call smashes them (25 tests red on first cut). Corollary: rsp becomes safely positionable exactly when no C frame can interleave above BB frames — i.e., after 7c.

---

## 10. The FORTH-CELL Stack Design (Lon eureka, 2026-07-11, s28 post-handoff design session — the conversation to RESUME next session)

**Provenance:** born directly from the s28 `ZC_FRAME_RSP` ablation (GOAL-SNOBOL4-BB.md s28: mode-3 174/118 with r12 freed, zero code changes; blockers G1/G2/G3). Lon, verbatim-in-spirit: *"Let's have some fun designing an ultimate push, pop, and slide stack arena. We have full control of everything hanging off a moving RSP and index from it much like FORTH does."*

### 10a. THE LOCKED-IN CORE (Lon ruling 2026-07-11 — LOCKED)
1. **ALL ζ data lands on the process stack**, hanging off a moving rsp, direct-indexed v1.
2. **Each BB = one variable-length CELL** holding ALL that box's ζ locals.
3. **The box's ONE result is ALWAYS at cell-relative offset ZERO.**
4. **The compiler generates every operand offset statically** — it knows the order and size of each cell (`zls_build` computes exactly this today).
5. rbp/rsp coordination DEFERRED (Lon: "right now, I see working with direct indexing") — see Sd.
6. Every cell size a multiple of 16 (t·p already is) ⇒ **rsp invariantly 16-aligned at every port**.

### 10b. Why this is the RATIFIED direction, not a new one
§9 already confessed it: *"rZ MOVES (that was always the 4/28 truth; M5's fixed-r12 was the deviation)."* M2's chunk model WAS this design on malloc'd chunks with `.prev` chains. Delete the chain; hardware push/pop IS the allocator. The s28 blockers die **BY CONSTRUCTION, not by workaround**: **G1** — 16-multiple cells make the align dance DELETED, not fixed; **G2** — the xfer r13/r14/r15 saves become three slots in the box's OWN cell, zero rsp motion; **G3** — the six-`jmp ω` problem becomes VISIBLE per-path pop constants (auditable arithmetic instead of hidden frees).

### 10c. The ONE bend in the FORTH analogy (SUSPEND ≠ POP)
FORTH pops operands at consume time. Byrd boxes CANNOT: `plus.resume → E2.resume` needs E2's cell live, state intact, after consumption. **Operands SUSPEND.** Lifetime law: **α = push (`sub rsp,K`) · cell live through ALL γ/β cycling · ω = pop (`add rsp,K`)** — LIFO holds because ω order reverses α order along every control path. **The port invariant: control standing at any port of box X ⇒ rsp at X's frontier.** Consequence: depth to an operand = the operand's **SUBTREE FOOTPRINT AT YIELD** (its cell + all still-suspended descendants), not one cell — still compile-time for static trees. This resolves Lon's "first (or maybe last depending on direction)" question: **parent-α-first push order ⇒ each subtree's ROOT cell sits at the HIGH end of its region.** The `plus(E1,E2)` picture at E2's yield:

```
rsp → [E2 descendants…][E2 cell: result@0]   ← fp(E2)
      [E1 descendants…][E1 cell: result@0]   ← fp(E1)
      [plus cell: result@0]                   ← szPlus
      [ancestors…]
E2.value = [rsp + fp(E2) − 16]
E1.value = [rsp + fp(E2) + fp(E1) − 16]
plus.value = [rsp + fp(E2) + fp(E1)]          — all compile-time constants
```

### 10d. The FORTH resonance (alternation)
Alternation makes footprint path-dependent: `(A|B)` at yield is fp(A) or fp(B) deep. Fix: **pad each arm to max(fp(arms))** — which is LITERALLY ANS FORTH's own control-flow law: both arms of an IF must have identical stack effect. FORTH already legislated the alternation problem.

### 10e. UNWIND — the SINGLE dynamic escape hatch
Only three things cannot be constant-depth: ARBNO teardown (n live iterations), bare FENCE's cut, and the statement/C-driver return. All three are ONE primitive, one saved qword:
```
UNWIND:  mov rsp, [anchor]
         jmp  target
```

### 10f. FENCE — VERIFIED FROM THE MANUAL this session (seemed tricky; is two instructions)
⚠ Discovery: `1-spitbol-manual-v3_7.pdf` is actually a TEXT file (header bytes `MACRO`) — pdftotext/pypdf choke on it; **grep it directly**.
- **Bare FENCE** (manual ln 4644): matches null forward; scanner backing INTO it ⇒ **the whole match FAILS** (and no other-anchor retries if it is the first component, ln 4656). β = `mov rsp,[scan_anchor]; jmp scan.fail`.
- **FENCE(P)** (ln 4716): P's INTERNAL alternatives invisible on backup, but backup **continues LEFT of it normally**. β = pop exactly fp(P) (`add rsp,K` if P static; restore own-cell anchor if P contains ARBNO), then `jmp left.resume`.
The semantic asymmetry (cut-the-MATCH vs cut-P's-INTERIOR) = which anchor you restore. Nothing else.

### 10g. Decision rows Sa–Sf (OPEN — Lon rules each; recommendations recorded)
| # | Decision | Recommendation | Status |
|---|---|---|---|
| Sa | Operand-reach convention | **footprint constants** (zero copies; zls_build already knows sizes); copy-out-to-parent-slot kept as fallback for dynamic-footprint operands | OPEN |
| Sb | Alternation arms | **pad to max** (the FORTH stack-effect law); unwind-anchor is the alternative if padding cost measures ugly | OPEN |
| Sc | Anchor slot | **lock a fixed cell offset** for the saved-rsp qword in scan-driver / FENCE(P) / ARBNO cells | OPEN |
| Sd | rbp role | **defer** (Lon ruling); natural candidate = STATEMENT BASE: `rsp==rbp` at every statement boundary is a FREE hard assert; trivializes error unwind + mode-3 C-return | OPEN |
| Se | Stack budget | process ulimit ~8MiB vs the HUGE 1024MB ruling (D3) — `setrlimit` at start, or run the BB spine on an mmap'd stack; telemetry + loud bomb per standing style | OPEN |
| Sf | GC | precise linear scan `[rsp, stmt_base)` via the zls TYPED kind maps — live set exactly delimited; BETTER than the arena story | OPEN |

### 10h. WHAT RESUMES NEXT SESSION (Lon: "we'll spark up the entire conversation")
1. **ARBNO's cell shape — LON HAS A SOLUTION IN MIND AND SPEAKS FIRST.** His sketch on record: since the stack grows down, rsp points at a LENGTH field to jump over the variable per-iteration section to reach the fixed quads. Alternatives on the table: anchor-restore; keeping the heap COLLECTION (§5f). NOT yet discussed.
2. Rule Sa–Sf.
3. Reconcile with **ZB-OWN-1a** (GOAL-SNOBOL4-BB.md s28): **§10 SUPERSEDES its "make rsp a stable base" framing** — rsp is not stabilized, it is DISCIPLINED (the port invariant, 10c). G1/G2 fixes become DELETIONS, not patches.
4. Statement temporaries: statement = outermost region; rsp returns to statement base at every statement boundary (the Sd assert point).
5. Escapers stay off-spine (heap ZH). For SNOBOL4 the escape set is NEAR-EMPTY (no suspend, no coexpr); the EVAL/CODE chain is the exception. Icon's suspend/coexpr keep §7's ZL-FN/ZL-COEXPR promotion story unchanged.

### 10i. s29 RESOLUTIONS (Lon + Claude live design conversation, 2026-07-12 UTC) — §10h item 1 IS RESOLVED
1. **TWO MM FLAVORS, BOTH KEPT, as ZLS compile defines (Lon ruling):** `ZLS_FRAME_REGION` (region ENTER pushes a whole ζ block at α, pops at ω; head + single entry/exit; β from another region = register re-establish) and `ZLS_FORTH_CELL` (per-BB push@α/pop@ω per 10a; direct jumps; rsp is the base). 10a's per-cell law = the FORTH flavor; this ruling AMENDS the lock to flavor-selectable. Both ride the process stack — unbounded growth, loud guard-page fault at the limit (the wanted property; Se's setrlimit/telemetry note stands).
2. **ARBNO = ITERATION-FRAME CHAIN (Lon's 10h length-prefix sketch and the iteration-frame design CONVERGED — same design):** variability is per-ITERATION, not per-box. One frame per extension: header `{resume_ptr, saved_δ, prev_delta, chain_total}` (+index for monitor, droppable) + P's cells at static footprint-sum offsets (Sb's pad-to-max at ALT arms, adopted). `chain_total` in the newest header = Lon's "rsp points at a LENGTH field"; ARBNO's own cell (pushed at its α) = the "fixed quads" at the high end. **The chain IS the count** — backtracking needs structure, not a number. LIFO puts rsp at the newest header whenever ARBNO-level code runs ⇒ counter/length read at `[rsp+k]`; interior boxes of P carry NOTHING extra.
3. **Interior FRAME discipline per iteration:** one `sub rsp, hdr+F_P` per extension (16-multiple), interior boxes at static offsets, rsp motionless during the iteration ⇒ interior β re-entries need zero restore; one `add rsp` on iteration abandon. Incremental exhaust rides the s21 TRANSIT ruling (static β wiring, per-box post-processing); direct-resume stays a controlled optimization. `resume_ptr` = the NCB-2a lea/mov slot, per-iteration, serving the BLOB-body case (P = pattern-var / `*E`) — nested/recursive ARBNO falls out free (no per-box .bss depth arena).
4. **v1 SCOPE FENCE (incremental wedge, not the end state):** only the ARBNO chain rides rsp; the statement frame stays `[r12+off]`; iteration base held in ARBNO's existing r12 zls slot (the zcol-cursor slot, re-backed). This dodges G1/G2 for v1 outright (align dance save/restores rsp; cells above survive — verified x86_asm.h:1062). The r12 crutch DIES at full conversion, replaced by the length-prefix hop (header fields carried + monitor-asserted from day one so they are proven before load-bearing). ⚠ RECORDED CONFLICT for the regions rung: ζ_reg=rbp collides with F2 (x86_align_save uses rbp when frame=r12) — resolve when the align dance dies by deletion (10b), not before.
5. **UNWIND scope (10e confirmed):** only match-level abandons (bare-FENCE cut, anchor restart, match end), paired with dcap height-restore; iteration-level exhaust NEVER unwinds — it pops through transit.
6. Live rung ladder: `GOAL-SNOBOL4-BB.md` → RUNG ZB-ITER (Phase 3 entry, first priority per Lon s29).
7. **s29 addendum (Lon, same session, after a hold/reactivate cycle probing the two-base hybrid): the END STATE is a ONE-REGISTER ζ solution — rsp only.** The v1 r12 crutch is accepted BECAUSE it is removable at a sequencing flip (pure-rsp arrives when G1/G2 die by deletion), not because the hybrid is a design. **r12's candidate afterlife = the ZH BASE REGISTER** — the zeta-heap side of the ZB-OWN-2 lifetime split (Icon suspend/coexpr, EVAL/CODE chains, blob-carrying DEFER escape to ZH; register-relative addressing for escaped frames). Register end-state candidate map: rsp=ζ stack · rbx=GVA · r13/r14/r15=Σ/δ/Δ · r12=ZH base · rbp=Sd statement-base assert. [Recorded s29; Lon may still re-rule rbp/Sd.]

## 11. THREE-REGION RATIFICATION (2026-07-12 s37, Lon: "we are now proceeding with the three region memory scheme") — supersedes §7-M7's HEAP side; the STACK side (ζ on rsp, α/ω brackets, §10 cells) UNCHANGED
Three regions, one collector, one mark phase, two outcomes — data slides, code free-lists. **R1 C stack:** as §7/§10, plus ONE new obligation: a walkable ζ frame chain at α/ω (root scan + saved-RIP range check). **R2 data workspace:** ONE reserved-VA span, bump alloc + title words (type|size|mark, forwarding at GC-W-2), STW MARK→FORWARD→ADJUST→SLIDE on exhaustion, tail re-zero, grow-from-OS; REFCOUNT RULED OUT (emitted-code inc/dec cost, slide already needs the tracer, promptness is an anti-goal per the manual, cycles); the s35/s36 arena taxonomy (A-PROG/A-TRANS/A-SUSP/A-COEXPR) is RETIRED as policy — §5's bump design and §6's SIL collect/mark/slide notes are the surviving reading list; s36's rt_slab pool + rt_slab_region + title words are the surviving CODE. **R3 code slab:** dual-mapped RW/RX (memfd, constant delta, protections never change), CODE NEVER MOVES (deliberate divergence from SPITBOL, which collects code blocks in-workspace), v1 grow-only, CS-2 first-fit free list with boundary-tag coalescing. Full design of record + the live ladder: `GOAL-SNOBOL4-BB.md` PHASE 0 RUNG TR (s37 rewrite).

## 12. REGISTER-ANCHORED ISLANDS RULING (2026-07-12 s39, Lon: "I'm with you on this. All your choices" — the GVA/EVAL-growth design conversation) — the region count STAYS THREE; islands are infrastructure, not regions
**THE RULE:** the three-region taxonomy (§11) counts what the COLLECTOR does — one mark phase, data slides, code free-lists. It does not count mmaps. Any register-anchored structure whose base must never move gets its own **RESERVED ISLAND** — reserve big, commit on demand (48-bit VA per D5: reservation is free, only touched pages cost RSS; TR-2 measured 11.5MB RSS under ~1.5GB of reserves). Islands are ROOT INFRASTRUCTURE (the GVA slot table, same shelf as the dictionary bucket array) or REGION-1-CLASS stacks (a second stack anchored by a register other than rsp — the coexpr per-thread stacks already stretched R1 to "stacks, plural"); they are never a fourth collector region.
**WHY MANDATORY, NOT NICE (the "Yikes"):** emitted graphs SELF-LOAD their anchor register at entry (rbx←g_gva_base, the F4/xa_flat contract) — a mid-EVAL growth that relocates the backing can update the global but CANNOT patch the live rbx already held in running frames. Relocation-on-growth is intolerable; base-pinning is the only correct answer.
**MECHANISM, PER STRUCTURE (Lon delegated the choice s39):** (a) **ever-growing LIST (GVA):** `rt_slab_region(BIG)` — malloc-backed, lazily faulted, base pinned for program lifetime, ZERO ledger movement (rt_slab.c stays the ONE malloc caller; MMAP gate arm stays 0). ⚠ rt_slab_get RECYCLES slabs from free lists ⇒ a region can arrive DIRTY: the consumer zeroes its used prefix, and any future growth-grant API zeroes granted slots. (b) **true STACK (a future Prolog r14-class structure):** a dedicated mmap with a PROT_NONE guard tail — loud SEGV on overflow like the C stack, at the price of ONE sanctioned ledger row (precedent: pat_pool, machine/). Chosen per structure, not globally.
**LANDED s39 (SCRIP, this session):** `rt_gva_island(n)` in rt.c beside gva_register — 16MB reserved (1M DESCR slots), prefix-zeroed, one-time static base; both mode-3 driver sites rehomed onto it. **This RETIRES the latent conflict s39 itself created:** the same session's TR-3 flip had moved m3_gva_arena into the A_PROG workspace, which GC-W-0 folds into the SLIDING Region 2 — the GVA would have moved under a live rbx the day GC-W-2 landed. Grow-only today masked it; the island kills it.
**GVA GROWTH SEMANTICS (recorded, not yet needed):** GVA is an ever-growing LIST, never shrinks, never pops — bump-append into the island. Today gva_register is called ONCE at startup (verified s39); runtime-minted globals (EVAL/CODE) fall back to the NV dictionary. The future slot-grant-for-EVAL rung appends into the island headroom with zero relocation. GVA slots are ROOTS: GC-W-2's ADJUST rewrites slot CONTENTS (per D4, unchanged); the table itself never moves.
**MODE-4 GAP, NAMED AS ITS OWN RUNG (do not smuggle into a TR flip — it changes emitted code):** mode-4's GVA is `lea rsi,[rip+__gva]` — a linker-sized symbol, zero growth path. Two candidate fixes when that rung opens: (i) huge NOBITS `.bss` GVA (lazily committed by the kernel, fully static, cheapest) or (ii) both modes uniform through g_gva_base→island (one story, rides the existing rbx self-load). Claude recommends (ii); Lon rules when it opens.
**PROLOG r14 (honest state):** r14 in the CURRENT tree is SNOBOL4's scan cursor δ (x86_asm.h xfer/scan conventions); no Prolog r14 exists in the templates yet (verified by grep s39). The islands mechanism is ratified for it IN PRINCIPLE; pin what it anchors when that rung opens.

## 13. THE AMENDED TWO-FLAVOR LAW + RUNG ZB-FC-0 (2026-07-12 s40, Lon pivot: "Switch over to the FORTH zeta cell stack implementation ... main spine on the RSP for all languages" — self-corrected same session)
**THE LAW (Lon, verbatim intent after his own correction):** **STACK flavor** — every ζ cell on rsp is FIXED SIZE, exactly ONE cell per BB, **no other allocation on the spine** (pure §10a: α=`sub rsp,K`, ω=`add rsp,K`, compile-time offsets). **HEAP flavor (escapable BBs)** — ζ lives on GC **and so does the box's variable COLLECTION data** (e.g. ARBNO's per-iteration array); γ/ω overload to alloc/free that external collection storage. External storage is legitimate on the heap side; it is BANNED from the rsp spine.
**SUPERSESSION:** this AMENDS §10i item 2 — the s29 ARBNO iteration-frame-chain-ON-RSP design is retired; ARBNO's variable per-iteration data becomes a heap array under the γ/ω overloads, the rsp spine stays purely fixed-cell, killing the length-prefix hop, the per-iteration `sub rsp`, and most of §10e's UNWIND surface. §10i item 1's flavor names stand (the FORTH flavor is now `ZC_PORT_FORTH`, a ZC_PORT axis value rather than a compile define — runtime-selectable proved cheaper and the axis already existed).
**RUNG ZB-FC-0 LANDED (SCRIP, s40):** `ZC_PORT_FORTH=6` (`SCRIP_ZETA_PORT=6`/`--zeta-port 6`; NOT default) — a strict CSTACK SUPERSET (`x86_port_cstack()` predicate at every CSTACK seam + `rt_zeta_cstack` runtime mirror). Per-box fixed cell via the `fc_geom()` authority (zeta_storage.c, the zls2_geom pattern) promoted to `g_emit.op_fc_bytes/op_fc_base` at dispatch, consumed by ONE hook arm (α `sub rsp,K` / jmp-ω `add rsp,K`; γ suspends per §10c; β emits nothing per the s7 α/ω-only ruling) + the FR/FRQ in-range translation (`[rsp + off − op_fc_base]`, new `XK_RSP32` operand kind + four rsp-SIB encoders). **Conditional ω = the invert+pop+jmp SYNTH inside `x86_jcc`** (`jcc′ L(synth); jmp ω` — the interior jmp fires the one pop arm; synth ids descend from 240 per box) — §10b's G3 as visible per-path pops, ZERO template edits. v1 fence: fc_geom grants IR_MATCH_SPAN only (keystone looping box; two private 4B fields, dirty-cell-safe, ±8 strchr dance verified non-straddling). **GATES:** default byte-identical (crosscheck watermark-exact m3 302/4 · m4 301/3/2 · DIVERGE=1(1017), same lists; all three .s regen scripts no-op); PORT=6 crosscheck IDENTICAL fail sets across the full corpus; sno 7/7, icon 12/12, prolog 5/5 under BOTH flavors; emitted-code probe verified vs SPITBOL oracle (m3==m4==oracle) with the cell live at `[rsp+0/+4]`.
**NEXT RUNGS:** widen fc_geom per-kind (LEN/TAB/RTAB/ANY/NOTANY, each checked against the §10c port invariant), then the operand-footprint reach (§10c/Sa) toward consumer reads and retiring the flat frame; the heap-flavor γ/ω alloc/free overloads for escapables = ZB-ACT-3's entry.
**✅ RUNG ZB-FC-3a LANDED (SCRIP `a775820a`, s41 same session) — ALTERNATE LINEAR-ARM v1 onto the spine.** LOWER computes per-arm EXACT fp at construction time (granted leaves=16; SEQ/captures/wiring=0; nested ALT/ARBNO/ARB/DEFER → decline whole ALT → stays flat). `fc_alt_{register,fpmax,fp}` side-table. ALT template fc arm: own 16B cell at α/ω, β reads alt_i at `[rsp+FPMAX+8]`, per-arm resume adds `(FPMAX−fp_j)` back (alt_resume_chain_fc), N pad-stub PAIRs at 2N+2+j. ALSO FIXED: `x86_pair_tgt` fallback — define-only pair slots now serve as jmp targets; previously `??`/skipped-patch → silent SEGV (the stubs' `jmp na_s` hit this). Census: **181 fc cells (89 ALT + 92 ZB-FC-1/2)**; watermark-exact both flavors; all prior probes clean.
**⛔ ZB-FC-3 RESIDUE:** SEQ (per-i fp sums; reuse alt_resume_chain_fc + stub design verbatim), ASSIGN_SAVE/COND, HEAD/RELEASE/REPLACE.
**✅ RUNG ZB-FC-1 LANDED (SCRIP `b2a869fe`, s41 2026-07-12) — THE WIDENING, per-kind checked as §13 mandated, and the check corrected the list both directions.** GRANTED (16B cells each, §10c verified): **TAB/RTAB** (one 4B entry-δ save @+0, α-writes-before-read, β reads at frontier, zero internal rsp motion) + **BREAK/BREAKX** (counter @+0; BREAKX +entry-δ save @+4, generator-kind — cell suspends across γ/β cycling per §10c; both strchr ±8 dances verified non-straddling like SPAN's). **MEASURED ZERO-CELL VERDICT — LEN/ANY/NOTANY own NO ζ locals** (pure register machines: state = r14 arithmetic, β-undo re-reads the OPERAND slot/immediate); under this section's own fixed-size law a box with no locals has a ZERO cell = no rsp motion, so fc_geom returning 0 IS their grant — they join when SU-C gives them a result field to home. POS/RPOS stay the canonical pure boxes; ARB/ARBNO excluded (zls2 grants — the heap flavor's business). The window is the SHIFTED locals base (zls_off = result+16) so result + operand slots stay flat-frame outside it — the future SU-C reader is unaffected by construction. ⛔ **THE WIDENING EXPOSED A SILENT-DROP ENCODER GAP (found by oracle probe BEFORE the crosscheck — the instrument sequence worked):** `sub reg32,[rsp+disp]` had no dispatch arm; the x86() fall-through returned EMPTY and BREAKX's β δ-undo VANISHED from the emitted stream (capture start slid, `C=bXc` vs oracle `aXbXc`); TAB/RTAB passed only because their β is a mov (covered). ZB-FC-0's "four rsp-SIB encoders" were exactly SPAN's shapes — every future grant whose template uses a NEW mnemonic×FR shape must check the dispatch, so the fall-through is now FATAL for any frame/cell operand on add/sub (the 2026-07-08 mov precedent extended; a frame/cell access that emits nothing is never legitimate). `x86_rsp_sub_from_reg32` added (0x2B, as-byte-verified: `2b 04 24` / `2b 44 24 NN` / REX.R `44 2b ...`). Gates: default + PORT=6 crosschecks watermark-exact (m3 302/4, m4 301/3/2, DIVERGE=1/1017, identical sets); sno 7/7 · icon 12/12 · prolog 5/5 · raku 11 PASS/6 FAIL (the 6 BISECT-PROVEN pre-existing — stash/rebuild/re-run at `b99e9348`, identical set; this smoke had no recorded baseline before) ×2 flavors ×2 media; TAB/RTAB + BREAK/BREAKX oracle probes m3==m4==oracle both flavors, cells inspected in the .s (sub/add rsp,16 at α/ω, [rsp+0] rebase, synth per-path pops, β-at-frontier reads); `.s` regen scripts all no-op = default byte-identity proven. **The fixed-cell grant set is now the complete eligible population under the v1 fence: SPAN+TAB+RTAB+BREAK+BREAKX (every scratch-owning non-zls2 pattern leaf).** NEXT: the operand-footprint reach (§10c/Sa) — consumer reads at [rsp + footprint offsets], retiring the flat frame — and the heap-flavor γ/ω overloads (ZB-ACT-3).
**✅ RUNG ZB-FC-2 LANDED (SCRIP `3bd2fc1e`, s41 same session, Lon: "Concentrate on SNOBOL4 ONLY... Convert all wholesale if possible") — BAL + REM granted.** BAL: n/δ0/depth triple @+0/+4/+8, ZERO internal rsp motion, β falls into the scan with the cell intact (one loop serves both ports — the s34 SPAN-shape claim verified in-template); REM: the TAB shape. Probes m3==m4==oracle both flavors including BAL multi-extent β cycling through nested parens; crosschecks watermark-exact both flavors; regen no-op. Survey corrections: POS/RPOS's single FR ref is the OPERAND read — the s21 pure verdict STANDS; `bb_match_fence` has NO dispatch site (s34 unreachable-template residue; keyword FENCE is an edge/seal — not a candidate, route to the s34 FENCE-vs-FENCE(P) rung).

**⛔ THE WHOLESALE MAP (s41, complete SNOBOL4 census — every match-family kind classified; "convert all" = finish these tiers in order):**
**TIER A — CONVERTED, rsp cells LIVE (9 kinds):** SPAN TAB RTAB BREAK BREAKX (ZB-FC-1) + BAL REM (ZB-FC-2). Every self-contained scratch owner is on the spine.
**TIER B — ZERO-CELL, converted BY LAW with zero code (8 kinds):** LEN ANY NOTANY LIT ATP POS RPOS CAT — zero ζ locals (FR census 0, or operand-read-only); fc_geom=0 IS their FORTH form under this section's fixed-size law. ABORT/FAIL/keyword-FENCE/SUCCEED are edges (s31 rule) — nothing to convert.
**TIER C — RUNG ZB-FC-3, THE FOOTPRINT RUNG (the wholesale blocker, design derived s41 from the live templates):** ALTERNATE (δ/dcap/alt_i @+0/+4/+8) and SEQUENCE (δ/seq_i) own FIXED quads — convertible — but their GLUE runs at rsp = frontier − fp(live children): na_s/ns_s entered from a succeeded arm/element with its subtree SUSPENDED; ALT.β likewise; SEQ's fail-glue dispatch target frontier varies with RUNTIME seq_i. THE DESIGN (per §10c/§10d, mapped to the live machinery): (1) `fc_footprint(nd)` beside fc_geom — fp(leaf)=granted k or 0; fp(SEQ)=own+Σfp(elems); fp(ALT)=own+MAX over arms (§10d pad-to-max is ANS FORTH's own IF law); (2) per-arm/per-element σ landing stubs — the pairs machinery already allocates per-i labels (PAIR(base+i)) and flat_drive_match_alt already re-tags σ/φ edges per-operand, so each arm i's σ stub does the STATIC pad `sub rsp,(FPMAX−fp(arm_i))` before the common glue, and β's existing per-i cmp/je dispatch chain (alt_dispatch_chain) gains a static `add rsp,(FPMAX−fp(arm_i))` per branch before the jmp — every adjust is a compile-time constant inside an ALREADY per-i branch; (3) SEQ identically: element i's σ stub knows Σfp(0..i) statically; fail-glue's per-i resume dispatch adds the per-i delta. ALSO TIER C (cross-box reads = the same fp machinery): ASSIGN_SAVE (own 4B δ-slot; its ADDRESS is pushed into the rt_cap ring — an ABSOLUTE pointer to a live cell stays valid under rsp motion, verified reasoning s41, so only the LEA SITES need fp) + ASSIGN_COND (its lea to SAVE's cell = rsp + fp(P) at COND's α); HEAD (8 FR refs, anchor state) + RELEASE (reads HEAD's slot at op_off+8/+24 — the design-noted cross-box read); REPLACE (5 FR refs, reads splice state). Order inside C: ALT first (pad-to-max is the simplest fp consumer), SEQ second (per-i sums), SAVE/COND third (first true consumer-read), HEAD/RELEASE/REPLACE last (subject-level lifetime = outermost cells).
**TIER D — HEAP FLAVOR by this section's own law (= ZB-ACT-3, NOT rsp):** ARBNO's zcol COLLECTION (variable per-iteration data — the law's named example), ARB's zls2 BUMP/RELEASE ζ-blocks (re-entrancy under recursion/ARBNO bodies — the same variable-population argument), DEFER's blob-call escape + EVAL/CODE chains (§10h item 5's named exception). Their own FIXED quads (ARBNO's owner quad, DEFER's fn/frame quad) can ride rsp AFTER their variable halves are re-homed on GC — do not grant them before ZB-ACT-3 lands.
**THE HONEST WHOLESALE ANSWER (s41): 17 of ~21 kinds are DONE (9 converted + 8 zero-cell). The remainder is not grant-shaped — it is two named rungs (ZB-FC-3 footprint, ZB-ACT-3 heap flavor), both now specified against the live tree.**
