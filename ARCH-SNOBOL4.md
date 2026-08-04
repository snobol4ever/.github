# ARCH-SNOBOL4.md — SNOBOL4 Frontend

Frontend: SNOBOL4. Produces shared IR (EXPR_t/STMT_t). See ARCH-IR.md.

## Parser

`src/frontend/snobol4/CMPILE.c` — single-file SIL-faithful parser.
Public API: `cmpile_init`, `cmpile_file`, `cmpile_string`, `cmpile_free`.
Parse node type: `CMPND_t`. Statement type: `CMPILE_t`.

Key SIL procedures (implemented in CMPILE.c):
- `CMPILE` — top-level statement parser
- `ELEMNT` / `EXPR` / `EXPR_PREC` — expression parsing
- `FORWRD` / `FORBLK` / `FORRUN` — continuation handling (true streaming, no linebuf)
- `STREAM` — 6-arg: `STREAM out, in, table, error_branch, eos_branch, stop_branch`
- `IBLKTB` / `FRWDTB` — action tables

## Streaming model

True streaming — no linebuf pre-join. TEXTSP = one physical line.
FORWRD/FORBLK call FORRUN on ST_EOS to fetch the next card.
STREAM returns: ST_ERROR→arg4, ST_EOS→arg5, ST_STOP→arg6.

## Operator table names (SIL → CMPILE)

| SIL | CMPILE | Meaning |
|-----|--------|---------|
| ADDFN | ADDFN | + |
| SUBFN | SUBFN | - |
| MPYFN | MPYFN | * |
| DIVFN | DIVFN | / |
| EXPFN | EXPFN | ** |
| ORFN | ORFN | alternation `\|` |
| CATFN | CATFN | concatenation |
| BIQSFN | BIQSFN | binary `?` |
| EQTYP | EQTYP | = (assignment) |

## Runtime

Key files:
- `src/runtime/snobol4/snobol4.c` — builtins, keywords, TRACE, monitor hooks
- `src/runtime/snobol4/stmt_exec.c` — 5-phase statement executor
- `src/runtime/snobol4/invoke.c` — INVOKE_fn / APPLY_fn dispatch
- `src/runtime/snobol4/argval.c` — VARVAL_fn, INTVAL_fn, PATVAL_fn
- `src/runtime/snobol4/snobol4_nmd.c` — NAM_push/save/commit/discard

## DATATYPE convention

SPITBOL returns lowercase (`"name"`, `"pattern"`).
SCRIP returns uppercase (`"NAME"`, `"PATTERN"`).
This is intentional per SNOBOL4 spec. `.ref` files use uppercase.

## Monitor hooks (in snobol4.c)

```c
comm_var(name, val)     // emit VALUE trace event to monitor_fd, block on monitor_ack_fd
comm_stno(n)            // increment kw_stcount, fire error 22 if kw_stlimit exceeded
trace_is_active(name)   // 1 if name is in trace_set[]
monitor_fd              // from MONITOR_READY_PIPE env var
monitor_ack_fd          // from MONITOR_GO_PIPE env var
```

## Native pattern architecture — modes 3 & 4 (pattern = graph of emitted byrd-boxes, `bb_box_fn`)

Added 2026-05-31 (Lon "Eureka"); CORRECTED 2026-06-01 (Lon): the built pattern is a graph of EMITTED
BYRD-BOXES (`bb_box_fn`) driven by `bb_broker.c`, NOT a `PATND_t` and NOT a `tree_t`. See
GOAL-SNOBOL4-BB.md "CORRECTED PATTERN ARCHITECTURE" for the full statement + decided forks.
Modes 1 (AST interp) and 2 (IR interp) are DELETED (long gone — see PLAN.md Architecture + GOAL-MODE34-IDENTICAL.md); this section governs the only two modes that exist: mode 3 (`--run`, BINARY arm → RX pool) and
mode 4 (`--compile`, TEXT arm → `as`/`gcc`). Both are pure LOWER + EMITTER, no interpreter. RULES recap: the ONLY emitted thing that does work is
a **BB code block** (a byrd box) reached via `emit_core.c` dispatch; **XA blocks** only wrap/stitch
(file header/footer, flat prologue/epilogue, data/rodata, entry dispatch, pattern-blob framing). So in
modes 3/4 the ONLY vehicle to build a subject, build a pattern, or build a replacement is a **BB**.

### Five-phase statement model
A SNOBOL4 match statement `SUBJ ? PAT [= REPL]` processes in five phases, EACH emitted as BB(s):
1. **Build subject** — lower the subject value-expr → a **SUBJECT BB** that evaluates it and loads the
   locked registers `Σ` (base ptr), `δ` (cursor = 0), `Δ` (length/end). Easiest of the three builds;
   closest to existing value-box work.
2. **Build pattern** — THE KEY TURN. A SNOBOL4 pattern is a *runtime object* = a graph of EMITTED
   BYRD-BOXES (`bb_box_fn` machine code in the RX pool), driven by `bb_broker.c` four-port (`α/β/γ/ω`) —
   the SAME broker that drives Icon generators and Prolog goals. It is NOT a `PATND_t` data structure
   (that redundant runtime pattern-IR is being demolished) and NOT a `tree_t` (AST is for EVAL/CODE only —
   they compile a runtime *source string*; a pattern's structure is known at COMPILE time). The pattern
   ELEMENTS *are* byrd-boxes — the EXISTING `IR_PAT_*` matcher templates (`bb_lit`, `bb_pat_span`,
   `bb_pat_alt`, `bb_pat_cat`, `bb_pat_len`, …). Construction has two cases, decided by COMPILE-TIME
   invariance of each subtree:
   - **Invariant subtree** (literal, fixed `LEN`/`POS`, ALT/CAT of invariants) → emitted + port-wired at
     COMPILE time; referenced at runtime by a **`REF_INVARIANT`** box that loads the sealed `bb_box_fn` head
     (RO `[rip+disp]`/movabs) into a `ζ`-slot. A FULLY-invariant pattern (most patterns) costs only this one
     box — NO runtime construction.
   - **Variant subtree** (operand-variant `LEN(N)`/`SPAN(cvar)`, or structural-variant `*E`/`$NAME`/
     pattern-valued var) → for OPERAND variance the sealed element matcher reads its operand late from a
     `ζ`-slot (operand-binding, no builder box); for STRUCTURAL variance a **`BB_PAT_BUILD`** box SPLICES
     (wires ports of) the runtime box-graph and **STITCH_SEQ/STITCH_ALT** boxes wire it to the sealed pieces.
   `STITCH_SEQ`/`STITCH_ALT` are the runtime twins of LOWER's `wire_seq`/`wire_alt` (same port equations,
   one layer down): they wire box-INSTANCE records whose `code` field points at the sealed element matchers,
   so STITCH never repoints sealed interior jumps. The built/sealed graph head (a `bb_box_fn`) lives in a
   `ζ`-frame slot and IS the pattern's **`DT_P`** value (the `descr.h` `.p` slot, reborn as a box-graph head).
   **SEAL at element granularity, WIRE at instance level.**
3. **Run pattern** — control enters the generic **BB_MATCH box**, which takes the built pattern graph +
   the subject (`Σ`/`δ`/`Δ`) and runs the SPITBOL ch.18 scanner over it: the unanchored starting-cursor
   loop (advance start unless `&ANCHOR`; ch.18 step 6) wrapping the pattern's four-port (`α/β/γ/ω`)
   backtracking. ALL backtracking is carried by the four-port topology — NO value stack (FACT RULE).
4. **Build replacement** (only if `= REPL`) — lower the replacement value-expr → a **REPLACEMENT BB**.
   CAN fail (e.g. a failing conditional in the replacement expr).
5. **Do replace** — a **SUBSTITUTION BB**: requires the subject be an LVALUE — FAILS for a literal/number
   subject (`"hello"`, `99`). Splice `Σ[0:m_start] + repl + Σ[m_end:]` and assign back to the subject.

### Build/run split is real
Phase 2 (build) and phase 3 (run) are GENUINELY SEPARATE steps, matching SNOBOL4 first-class patterns:
the pattern object is constructed (REF_INVARIANT / BB_PAT_BUILD / STITCH boxes — or, for a fully-invariant
pattern, just sealed at compile time and referenced), then matched (BB_MATCH drives the box-graph via the
broker). (Historical note: the old mode-2 `IR_SCAN` super-node + hidden `IR_alloc` sub-graph re-derived
topology at exec — the `sno_ring_to_tree` anti-pattern relocated into the lowerer — and was the WRONG layer.
Mode 2 is DELETED, so that path is gone; the native build/run chain above is the only design.)

### OPTIMIZATION — ALL-INVARIANT BLOB FREEZE (second step, after correctness)
Invariance is a COMPILE-TIME property of the pattern subtree: a pattern all of whose components are
compile-time constant (literal strings/ints/csets, fixed `LEN`/`POS`/`RPOS`, constant `ALT`/`CAT` of
such) is INVARIANT. The BASELINE mechanism wires even invariant patterns at the instance level (an
invariant leaf's sealed element `code` becomes an instance's `code`); correctness first. The OPTIMIZATION:
when a pattern is FULLY invariant, collapse its REF_INVARIANT + STITCH sequence into ONE sealed `bb_box_fn`
BLOB emitted ONCE at compile time (the wiring frozen to direct jumps, no ε-nodes, no runtime stitch);
`REF_INVARIANT` hands MATCH that sealed head directly. Only variant components (`*E`, `$NAME`,
pattern-valued var) keep runtime build+stitch. Rule: const subtree ⇒ freeze to a sealed BLOB;
references-runtime ⇒ keep instance-wired/built. This mirrors SPITBOL: constant patterns build once;
variable patterns rebuild/defer per match. See GOAL-SNOBOL4-BB.md rung PB-RB for the step ladder.

## Storage & call convention (pointer, 2026-07-11)
ζ storage design of record: `ARCH-ZETA-LOCAL-STORAGE.md` §7 (two MM flavors, regions, register end-state). Call convention: the ONE-ENTRY / NO-C→BB rule — mode 3 has exactly one C→BB transfer (driver MAIN); C runtime helpers are strict leaves; mode 4 entry is `main` (= the emitted graph). Live rung ladder + violation ledger: `GOAL-SNOBOL4-BB.md` Phase 1 (NCB).

---

## ARBNO iteration frames — ERADICATION GOAL (Lon ruling, 2026-07-24 s146)

The rsp linked-frame chain for ARBNO iterations (FORTH-flavor linkage headers, chain walk on unwind) is TO BE ELIMINATED — not settled architecture. Desired end state: FAST, IMMEDIATE γ processing — an iteration's success transitions with zero per-iteration linkage ceremony. Obstacle on record: a DEFER inside the body makes per-iteration extent runtime-variable (which PAT$ blob arrives at a `*VAR` site is decided at match time; retained suspensions interleave their carves between iteration frames, so even inter-frame DISTANCE varies) — uniform count×size arithmetic fails in general. This is an obstacle to SOLVE, not an accepted end state ("I want it gone for the record. That does not mean I get my wish." — keep hunting). Candidates: two-tier static-body verdict (SEQ-STATIC precedent — bodies with no dynamic construct get pure arithmetic; degrade never die) · per-blob registered frame geometry · patchable-γ/ω external linkage to cut the activation ceremony meanwhile. Until a solution lands, the chain is tolerated, not endorsed.

## Dynamic linkage — the WIRE CONTRACT and the GLUE set (design of record, 2026-08-01 s22v, Lon four-count)

**ONE dynamic linkage everywhere: the wire contract — `rcx = γ continuation, rdx = ω continuation, jmp target`.** Spoken identically by C (`rt_chain_enter`, `rt_proc_call_open`/`_slim`) and by emitted sites (defer/capture/staged-call trios). Two flavors, one distinction:

- **ONE-SHOT = wire contract + pcall record.** The open pushes an `rt_pcall_t` + wire quad (`g_pcall_wires`, LIFO, index-locked); the target blob's first box (role-3 WIRE-ADOPT) records the live rcx/rdx + entry rsp + caller rbp; every exit comes home by **`bb_glue_wire_exit(is_γ)`** — snap the open record (`rt_flat_ret_snap`), restore rsp/rbp(/r12 island) FROM THE RECORD (the sync point is the adopt; no rbp assumption, no whack), `jmp` the port's wire. Consumers: the RETURN/FRETURN floaters (roles 1/2) and the stub blob's own shared γ/ω ports — one function, one sequence.
- **PASS-THROUGH = the bare contract.** Nothing recorded, nothing to release; the target's exits ride the wires straight into the site's own continuation labels. Template: **`bb_glue_pass_wires(gid, wid)`** = `lea rcx,L(gid); lea rdx,L(wid); jmp rax` (bb_glue_flat.cpp). Canonical consumer: BB_DEFER's blob entry.

**The exit-class ledger (emit.cpp shared-γ/ω site):** a graph's shared γ/ω glue is selected by HOW IT IS ENTERED. **CLASS O** (outer one-shot main, α-pinned via guarded `bb_glue_framed_enter`) → `bb_glue_outer_γ/ω` (whack = the completion sync point outside the graph, then exit/ret). **CLASS C** (chain-entered: LBL__ pseudo-procs, EVAL/CODE fragments) → same whack, ledgered as the AMBIENT-C-FRAME unwind: `rt_chain_enter` pins no rbp; the whack lands in the C caller's -O0 frame and IS the m3 return-to-C (the s22u RBPPAIR falsification's load-bearing accident, now a named decision). **CLASS P** (wire-entered DEFINE stubs, discriminated by the driver's own `g_flat_frame_floor > 0` role-3-entry verdict) → `bb_glue_wire_γ/ω`, whack-free. This is the Lon s22v law applied: whack only at completion outside the graph, FENCE checkpoints inside, or other known sync points — a wire-entered graph's sync point is its ADOPT record, so its exits restore from the record instead of whacking.

**The four linkage needs (Lon's grid):** (ONE) MAIN → initial graph = one-shot static (framed pin + outer landing). (TWO) BB_DEFER → pattern blob = pass-through (`bb_glue_pass_wires`). (THREE) call site → SAVE_RESTORE/CALL_FUNC = one-shot dynamic (C-side open today; emitted role-0 is the CALL2BB slice; exits via `bb_glue_wire_exit`). (FOUR) shim → first statement of a DEFINE body = pass-through THROUGH THE REGISTRY (`rt_goto_transfer`) — ⛔ must stay dynamic: SPITBOL CODE semantics let runtime-compiled fragments override same-name labels, so the hop resolves at run time; a static `jmp` fast-path requires a label-never-redefined license. Conversion backlog for the remaining hand-rolled trios lives in GOAL-SNOBOL4-BB.md's s22v cursor.

## ZETA-PER-BOX FRAME DISCIPLINE — the coherence challenge, named (HQ analysis 2026-08-04, Lon-directed, Fable seat; one-week history scan 2026-07-27→08-04, 402 SCRIP commits)

**The target model (Lon, restated this session):** every BB allocates ζ storage (result value + locals) at α ONLY; frees own K at ω ONLY; frees OUTSIDE γ at final success (STATEMENT_END whack); frees AT γ moving forward past FENCE0/FENCE1 (commit whack). Every construct with unbounded (compile-time-undeterminable) growth gets an RBP/RSP frame so release is a simple whack via RBP.

**The week's arc:** ZW-12→ZW-16 built/debugged the canonical match frame · ENDJMP landed then superseded same-day by the UNWIND ruling (failure never whacks; failure is an unwind) · U-1a/U-1b landed DEFAULT ON (every value-spine BB frees own K on ω, rolls to pred β) · mechanism-2 (nested RBP frame at the match boundary) built through W-1, five bugs fixed (`1b38958d`, `2a12b8fe`) · gate-ON at 278/317, 11 regressions remaining, ALL one class.

### What is already SOLVED (do not re-litigate)
- α-carve / ω-own-K-free / unwind law: landed, default ON.
- Whack encoders: `bb_glue_framed_enter/leave`, both media, exist.
- WHERE frames belong: the ZD-DEPTH census (FINDING 2026-08-03 ALPHA) proved the wall is a GRAPH PROPERTY — a join whose predecessor edges arrive at different accumulated RSP depths — measured 469 of 12,510 joins (3.7%), 96.3% of joins flat-safe today. Kind distribution: IR_STATEMENT_BEGIN 55.2% · IR_MATCH_BEGIN (ARBNO/FENCE1 live here) 18.3% · IR_SAVE_RESTORE 12.4% · IR_MATCH_ASSIGN_SAVE 6.6% · 7-kind tail 7.5%. The five-construct list (STATEMENT · MATCH_BEGIN · ARBNO · FENCE1 · FUNCTION) is the OUTPUT of the graph test, confirmed.

### THE GREATEST CURRENT CHALLENGE — frame-base/register coherence at β re-entry under NESTED frames
The RBP saved-link chain assumes LIFO entry/exit. Byrd-Box fail edges violate that: a backtrack jumps into a β whose surrounding frame's registers were clobbered by boxes that ran since, BEFORE the frame owner's β restores them. And the registers are over-booked:

| register | concurrent roles, all live in-tree at HEAD |
|---|---|
| rbp | STF statement base · mech-2 match base · ZW-15 claim_base · ARBNO element view (`zv()="rbp"`, bb_match_arbno.cpp:15) · HEAD-PIN construct base |
| r12 | CAS top (ZW-3) · mech-2 frame-base parking (W-1b Bug 5 fix) |

**Three convictions in seven days:**
1. **ZW16 (reverted):** ALTERNATE's arm-β fires the failed arm's CAPTURE_COND β BEFORE MATCH_BEGIN's β restores r12 from `[rbp-40]` — r12 undershoots, CAS corrupts. Finding's own conclusion = Lon's ruling verbatim: every indeterminacy boundary (ALTERNATE, ARBNO) needs its own mech-2 frame saving/restoring r12 at each arm boundary.
2. **Bug 5 (patched):** ARBNO borrows rbp as element view → MATCH_END `[rbp-N]` header reads return garbage. Patch = park base in r12 — a patch ON the discipline violation, and it double-books r12 against the CAS role.
3. **Bug 6 (OPEN, the 11 gate-ON regressions):** STF outer frame ⊗ mech-2 inner frame ⊗ multi-attempt. After mech-2's whack (`mov rsp,r12; pop rbp`) the popped value is the STF's PARENT, not the STF base — the retry loop's rsp restores desynchronize which stack cell the pop consumes. STATEMENT_END then reads `[rbp+328]` against the wrong base. Wrong output, no crash.

### Design verdicts (Lon's four questions, answered from the week's evidence)
**Why not just RBP-frame-whack at every unbounded spot?** That IS mechanism-2; it is landed and works (+123 programs in one session). The residue is not more whacks — it is that `pop rbp` only restores the enclosing base if NOTHING between push and pop wrote rbp outside the discipline. ARBNO's rbp borrow and multi-attempt rsp restores break the precondition. The work item is the BASE CONTRACT, not the whack.

**ARBNO allocating on α AND β to chain RETURN-β addresses?** Not needed for stack extent — the frame delta (rsp vs frame base) covers unknown unbounded growth; exhaustion is one restore. A per-iteration chain only buys individual backward traversal, and the per-retry side state that actually needs undoing (CAS entries, cursor) is already O(1)-bulk-restored from the frame's cas_base/anchor snapshot slots (`[rbp-40]`, `[rbp-72]`). The frame slots ARE the chain, linked by saved outer base. Skip the explicit chain unless the monitor someday proves a capture needs item-wise unwind.

**SEQUENCE BB for unbounded growth inside ALTERNATE/ARBNO?** Same verdict: the frame boundary IS the sequence delimiter. Only earns a place if interior growth must survive the parent whack (it cannot — whack means committed) or be traversed item-wise (covered above). ZW16 root cause 2 names the one real gap: blob-interior captures are not ZD-planned runs, so cell-offset reads hit uninitialized stack — cured by W-2's own step (ALTERNATE/ARBNO interiors become their own planned runs when they get their own frames). Routing, not a new box kind.

**FENCE0/FENCE1 whack-free ON γ, with an ABORT structure for backtrack?** Already law (four-clause, clause 3) and partially landed (FENCE1 own frame `4d902148`; fence_whack_commit under ZW frame `6c02ad5b`). The replacement structure = ONE SLOT: the match-frame floor (or saved outer base) in the fence's frame; the fence's β does `mov rsp,<floor>; jmp <match-fail/ABORT>` — O(1), the model's own "bare FENCE backward = O(1) unwind to the match frame floor." The γ-whack's one subtlety: after whacking, the dead region's βs must be UNREACHABLE — every backward edge that would have entered them is retargeted to the fence's β at PLAN time (ENDJMP's edge-chase shape, at the fence boundary, forward-legal under clause 3). Planner edit, not new machinery.

### ⭐⭐⭐ SESSION 2026-08-04 (Fable/HQ seat, Lon hands-on) — FOUR RULINGS FROM THE C REFERENCE LADDER

Method: Lon's hand-written Byrd-Box C references were compiled and diffed against the SPITBOL oracle rather than reasoned about. Four results, each measured.

**RULING 1 — NO CONSTRUCT NEEDS AN RBP FRAME. The chain in ζ replaces it.** (Lon: *"Prove me wrong."* Not provable — conceded.) RBP *is* a linked list: `push rbp; mov rbp,rsp` sets `[rbp]=prev`. Two ζ cells are the same structure with the head in memory instead of a register, so the question was never chain-vs-frame but only "cache the head in a register or not." For ARBNO: at β, after the child's ω freed own-K, rsp points exactly at the current iteration's cell — `[rsp+0]`/`[rsp+8]` address it, O(1), no register. Refinement: make the second cell the ARBNO ROOT pointer, not merely the previous link — a DISPLAY, not a chain — so ARBNO's own datum is one indirection from any depth instead of an O(N) walk. **PRECONDITION (the only one):** the chain is findable only if rsp is correct on arrival — to read the cell you need rsp, to correct rsp you'd need the cell. A register breaks that circularity; nothing else does. So the chain suffices IFF the unwind is exact, and a register is insurance against an inexact unwind, nothing more. Under the exact-unwind guarantee, RBP is redundant. **COST:** non-local exits (ABORT, deep fence commit) walk O(depth) instead of O(1) — acceptable for aborts. **PAYOFF:** the five-way rbp collision that IS Bug 6 evaporates; `zv()="rbp"` was only ever "the current iteration cell" = `[rsp+0]`. The answer to the A/B/C register question posed earlier in this file is **D: no construct holds a frame base.** Supersedes the "open design point" below.

**RULING 2 — ARBNO's local storage is ONE datum: the cursor at α (`Δ0`).** Not a counter, not a depth, not an accumulator. Result, null-match and exhaustion-restore are all DERIVED: `str(Σ+Δ0, Δ−Δ0)`. Stack-depth locals are redundant BY INDUCTION (one own-K unwind step lands exactly on the previous iteration's cell); the induction premise is 100% ω-coverage, so until the ladder is green a per-iteration entry-rsp cell is available as insurance but is not otherwise earned. `_1[64]` arenas disappear entirely — **the stack IS the arena and the index is implicit in rsp.**

**RULING 3 — ACCUMULATORS DOUBLE-COUNT ON RE-ENTRY; DERIVE, DON'T ACCUMULATE.** Measured in Lon's own case-1 reference: `seq = cat(seq, X)` mutates in place and γ is re-entered once per retry, so it summed ELEVEN times and reached the right answer by accident. `str(Σ+Δ0, Δ−Δ0)` is idempotent under re-entry, kills the whole bug class, and collapsed the per-iteration cell from `{str_t ARBNO; str_t alt; int alt_i;}` to `{int alt_i;}`. **This is a general law for every accumulating box (SEQUENCE, ARBNO, capture extents), not an ARBNO special case.**

**RULING 4 — ⛔ THE CAS MUST REMAIN A SEPARATE ARENA, AND WHACK-FREE ON FENCE0/FENCE1 IS MANDATORY** (Lon, this session, verbatim: *"if we WHACK-free on SUCCESS for FENCED versus wait until FINAL success, then we MUST have a separate CAS... we must free the stack memory or it will grow so HUGE it would be COLLOSAL"*). The derivation closes: the whack is mandatory for memory; the pending entry must survive it for semantics; therefore the entry cannot live in the whacked region. **MEASURED WITNESS** (`f1.sno`, this session): `'ab' ? ('a' . X) FENCE 'z'` → match FAILED, **X stays `<unset>`**; control `FENCE 'b'` → Y commits as `a`. So a pending `.` entry must SURVIVE the fence whack while NOT committing at it — a fence forbids backtracking but the match can still fail afterward, and `.` must not commit on a failed match. ⛔ **CORRECTION TO THIS SESSION'S OWN EARLIER CLAIM:** "the zeta stack IS the CAS" is TRUE on the failure path (entry lifetime == capture box's cell lifetime, α to ω) and **FALSE across a forward whack** — that is exactly where the lifetimes diverge. Three folding schemes were priced and all fail: hoist-on-whack is unbounded per fence in a loop; parenting capture cells to the match floor fails because the capture count is unbounded so the region cannot be carved at MATCH_BEGIN — a region that grows independently of rsp IS a separate arena. **WHAT SURVIVES is SCOPE, not existence:** the CAS should be MATCH-SCOPED (carved/reset at MATCH_BEGIN, released at MATCH_END), not the current process-wide 8MB pinned island at `RT_CAS_TOP` (`pin_va.h:9`). That is a narrowing — less to change, not more. **EXCEPTION LIST IS ONE ITEM LONG:** captures only. `$` immediate assignments are already performed; retained `*VAR` suspensions are backtrack points a fence kills by definition; the match's cursor/result live in the match frame above the fence floor.

**RETRO-EXPLANATION 1 — ZW16's revert was correct for a reason nobody named.** It moved CAS into r12 / ζ cells via op_zw staging and broke precisely where cell lifetime and entry lifetime diverge. The finding blamed r12 incoherence at ALTERNATE arm boundaries — real, but DOWNSTREAM. Root cause: captures cannot be ζ-resident at all.

**RETRO-EXPLANATION 2 — the mandatory fence whack is ALREADY BUILT AND GATED OFF.** `bb_match_fence1.cpp`'s own header states Lon's memory argument verbatim: *"retention drops O(activations) → O(depth): each committed sub-match's retained frame dies at the next enclosing fence commit instead of at the match bracket."* The whack is `mov rsp, rbp` behind `fence_whack_on()`; `fence_u2_frame()` reads `SCRIP_U2`, **default OFF**. So "WHACK-free on FENCE is mandatory" is not new construction — it is flipping a gate that was built, documented with the same argument, and never turned on. **Cheapest real win on the board; natural W-1c rung.**

**TERMINOLOGY — `CAS` is UNDOCUMENTED in-tree.** No expansion exists anywhere in `src/`. Usage supports **stack of pending Conditional ASsignments** (writers = CAPTURE_COND/CAPTURE_SAVE, record = `bb_dcap_t {varname,start,len}`, grouped with `rt_dcap` in `rt_arena.c:93`). ⚠ Collides with the universal systems meaning **Compare-And-Swap** in a codebase full of x86 — a reader will assume lock-free semantics. Owed: a one-line definition at `pin_va.h:9`.

### Fix direction for Bug 6 / the class (two options, both named in W-1c's own cursor line) — SUPERSEDED BY RULING 1 (option D)
(a) **Evict non-frame rbp writers** — move ARBNO's `zv()` off rbp (another register or a frame slot) so `pop rbp` is trustworthy BY CONSTRUCTION. Removes the disease.
(b) **Never trust the popped rbp** — STATEMENT_END recovers the STF base from a saved slot in the mech-2 header (chain walkable through fixed offsets), not from the register. Armors every read.
Recommendation: (a), keeping one saved-outer-base slot as belt-and-suspenders. Expected yield: the 11-regression class falls.

### The one OPEN DESIGN POINT (needs Lon's ruling — FINDING 2026-08-02h §6.2, still unruled)
ONE rbp discipline per statement: either the match frame NESTS inside STF (current W-1 path; Bug 6 is the nesting bill) or it ABSORBS — one frame per statement, match housekeeping at fixed offsets inside it, which deletes the inner push/pop entirely and with it this whole coherence class. Absorb is simpler; nest is landed further. Lon rules.

**Session mode (Lon, 2026-08-04):** hands-on from here until the end.
