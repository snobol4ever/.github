# ARCH-ZD-DEPTH-PLANNER — the ζ-depth planner, the admission ladder, and the frame-home denial classes

**What this is.** The recovered design rationale for the **ZD family** in `src/emitter/emit.cpp`: the one planner that decides, per statement, whether a run of boxes may price its cells as sliding `rsp` offsets, what each box carves, and — when the answer is *no flat price exists* — which node is pulled off the ζ-SPINE and re-homed in an `rbp` frame slot. Relocated by the cto on 2026-09-18 from the comments `e25a5daf` stripped on 2026-08-20 (row `rationale-emit-cpp-remainder`), verified against SCRIP `ad42031a9`.

**Why this cluster first.** Of the 746 comment spans `e25a5daf` took out of this file, the ZD family is the densest (`ZD-5b` alone appears in 35 of them, `zd_plan` in 25) and the only one that is still load-bearing for a rule in force: **RULES.md § BB FRAME-PLACEMENT CRITERION** — frame placement is decided by a behavioral, language-blind test, never by box-kind or language. The sections below are where that test's *content* was written down. It is also the material a static frame map needs under CEO-812, where every qword on the emitted stack is read as a DESCR: a map cannot be cut for a cell whose home is decided by a predicate nobody can read.

⚠ **Provenance note.** Several files these comments cite are not in the tree: `FINDING-2026-08-09g`, `FINDING s177`, `FINDING s178-L2`, `FINDING s178-FW` (deleted in the 2026-09-04 and 2026-09-16 sweeps, `.github` `f78d8b3fd` and `c0d7427ee`), and `ARCH-PASSTHRU.md`, which never existed in `.github` under that name. Where those are cited below the citation is kept as a **witness name**, not as a link, and the measurement each one names is quoted here in full — which is the point of this file. ⭐ **They are recoverable:** every deleted FINDING is still in `.github` history and can be read with `git show <commit>^:FINDING-….md` (Lon 2026-09-18: FINDING files are permitted again, and a deletion should be preceded by a summarization).

---

## §1 ZD-1 — THE ONE MAIN FUNCTION

Lon, s21x-v, verbatim: *"ONE main function that does graph traversal and calculates the zeta offsets based on the ORDER the BB's executed"* and *"NO FUNCTION-level processing whatsoever, ONLY statement level scoping"*.

`nodes[]` **is** the execution order the emitter lays down, so the traversal is a single forward pass over it, segmented into statements at `bb_src_of` heads. **Depth resets to zero at every head and never survives a statement — that is the whole of the scoping law.**

Per statement the pass renders an **ALL-OR-NOTHING VERDICT** (the per-graph all-or-nothing law of s21x-t, one level down). The statement rides ZD iff every node in it is either:

- an op-filtered spine kind whose value operands all resolve to ZD producers **inside the same statement**, or
- a passive control node that carves nothing.

**One legacy reader or one foreign carve refuses the whole statement.** That is the s21x-o *reader-frontier law* — *a BB may be armed once ALL of its consumers speak the live-depth authority* — enforced at the only granularity where it can be decided locally.

For an accepted statement the pass computes, in bytes:

| array | meaning |
|---|---|
| `zout[i]` | depth-on-exit: the running sum of α carves, 16 per result cell, suspended through γ per S10c |
| `zgpop[i]` | the statement-terminal γ release — depth at exit when the γ edge leaves the statement. **`rsp` returns to statement entry on EVERY cross-statement success edge.** |
| `zwpop[i]` | the ω twin, minus the box's own leave |

⭐ **Consumers' operand displacements are s21x-u's DIFFERENCE OF TWO DEPTHS**, staged per node in the drive loop as `op_zread[k] = delta_at_read(C) - delta_out(P)` — **the quantity no single depth can express.** This is the reason the planner exists at all: a consumer cannot be priced from its own depth or its producer's, only from the difference.

Instruments: `SCRIP_ZD=0` kills the regime; `SCRIP_ZD_ONLY` / `SCRIP_ZD_SKIP` are the per-BB dynamic arming instruments (nid csv, `zw_nid_listed`); `SCRIP_ZD_DIAG=1` prints every verdict and every number the function computes. All four still live at HEAD.

## §2 The RUN — statements are not contiguous ranges of `nodes[]`

**The 033/058 falsification (ZD-1 REDESIGN).** Range segmentation was wrong: right-first lowering **interleaves** statements' members. Witness 058: statement entry at `i=3`, its consumer at `i=5`, and **another statement's entry at `i=4` between them**. Segmenting by range therefore resolved operands across statements and staged releases on foreign producers.

Lon's words were *"the ORDER the BB's EXECUTED"*, so the walk follows the **γ wires**. Each `bb_src_of` head (plus the chain entry) roots a **RUN**: step `cur = zd_chase(cur->γ)` — GOTOs are chased exactly as the driver's own label resolution chases them, so dead nodes in emission are never members and are never staged — until the stepped target is off-chain, is a head, or is already claimed.

**The run IS the statement's executed spine, in execution order by construction**; membership, operand resolution, the depth walk and the crossing classification all read it. `zd_chase` is still the edge-following authority at HEAD (31 uses in `emit.cpp`).

## §3 The admission ladder — `zd_wl_kind` / `zd_nops`

Admission was widened kind by kind, each rung gated on its template growing a ZD arm first. The recovered ladder, with the reason each rung was admissible:

- **ZD-2a** `BINOP_CONCAT` — `bb_binop_concat_slot` grew its ZD arm; `binop_cat` maps it to `BINOP_CAT_CONCAT`, one template unconditionally.
- **ZD-2d/2e** `COERCE_NUMERIC` / `CMP_TEST` — both dispatch to ONE template unconditionally. `COERCE_NUMERIC` reads operand 0 as the value and operand 1 as the partner type-peek; `CMP_TEST` takes both coerced operands by address.
- **ZD-2f** the RVALUE `x[i]` form ONLY — 2-operand `IR_SUBSCRIPT` routes to `bb_subscript` (which grew a ZD arm); every other arity routes to `bb_section` and stays out.
- **ZD-2j/2k/2l/2m** the value-spine first-blocker tail — subscript gate (51+51 of its 106), the coerce tail (17+7), 13 first-blockers, and finally the LAST 5. ⭐ **With ZD-2m the census is ALL PROTOCOL** (CALL 518 / MATCH_BEGIN 247 / SAVE_RESTORE 18 / GOTO_DEFER …) — i.e. every remaining refusal was a protocol box, not a value box.
- **ZD-2h-ICN (s211)** global-non-local OR local-on-pinned (depth-immune-base). **SNOBOL4-invisible**: `graph_has_local` returns 0 for all SN4 programs, so the rung is byte-identical there by construction.
- **ZD-4 (s23q)** `IR_STATEMENT` joins the **K=0 transparent-sink class** beside `IR_ASSIGN` and `IR_GOTO_DEFER`. **s26 (Lon directive):** the statement bracket PAIR joins the same K=0 transparent class its parent earned at ZD-4 — BEGIN is a label+jmp relay.
- **ZD-5** MATCH-SPINE admission made **UNCONDITIONAL** — Lon, 2026-08-07 REGIME DELETION: *"You DELETE the other regime"*. The `SCRIP_ZD_MATCH` env gate was deleted, not defaulted.
- **ZD-7** bare `IR_CALL` admitted EXCEPT user-defined procs; **ZD-7c (s23r)** widens under `SCRIP_ZD_PROC` (default ON once `bb_call_proc_staged` gained its ZD arm). `IR_CALL`'s `n_operands` is the arg count, and the predecessor-in-run check iterates `[0..nops)`.
- **ZD-SR** the `SN4-FLAT-PROC` linkage family admitted as a **TRANSPARENT PROTOCOL BOX** — zero cells consumed, zero cells yielded.
- **ZD-ICN-CALL (s208)** `IR_CALL_BUILTIN_ICON` admitted for non-generator builtins.
- **ZK-3 (s213)** `IR_BOUND`/`IR_UNMARK` admitted on the cells arm only — a K=0 transparent bracket pair with no own cell.
- **PL-ZK-4b / PL-ZK-5** ONE AUTHORITY each: `IR_CALL_PROC_STAGED` and `IR_SUSPEND` have `nops=0` for the planner, because Prolog delivers proc-call args via `rt_arg_stage`/`g_call_args` rather than as ZD operands. ⛔ **`pl_cells_graph`, the predicate both were written against, no longer exists at HEAD** — re-derive the gate before trusting either rung.
- **ZD-5 NOTE (s22i)** `IR_MATCH_BEGIN` is deliberately NOT admitted. The 247 "MATCH_BEGIN refuses" in the census mean it was the **first blocker** in those runs, not that it was tried and failed.

## §4 ZD-8 — `zd_k`, THE ONE AUTHORITY for K

⭐ **ZD-8 (b3) is THE ONE AUTHORITY for K, the α-carve byte count of an admitted node.** A value-spine sink that yields no cell (`IR_ASSIGN`, `IR_GOTO_…`) is K=0; a box that yields a result cell is K=16; the scratch-bearing match leaves are K=16 because they must save a cursor across β.

⛔ **The rule is spelled ONCE.** Two sites are explicitly forbidden from re-spelling it: ZD-8 (b1), the sink, and ZD-8 (b2), the staging site — *"This site and `zd_plan`'s depth model were the SAME RULE SPELLED TWICE until…"*. The s22k law is stated in `ZK-2`'s own text as **"no K spelled here"**. This is the `s68`/`s70` *spelled-twice disease* again, and §6 is the other place it was cured.

**ZD-8·STFH-CARVE** is the separate ONE AUTHORITY for the `MATCH_BEGIN` head-carve byte count. It returns **64** when the OS-2·SLICE-1 GLUE-O deep-main `stfh` arm fires **and has no bracket leave to reclaim it**, and 0 otherwise. Three facts make it correct, and all three are easy to lose:

1. It is called at **BOTH plan time** (from `zd_k`, before graph-level `g_emit` fields are populated) **AND emit time** (from the template, after `g_emit` is fully staged), so **every input is derived from `g_emit_cfg`** — the IR graph, the one thing available at both times.
2. ⛔ **The FLAT_STMT_FRAME disjunct contributes 0.** `stfh()` in the template also fires for `flat_stmt_frame`, but the STF bracket leave (`mov rsp,___`) already reclaims all `rsp` depth — returning 64 there would **double-count the carve**.
3. The jmp-entry flags (`flat_jmp_entry`/`flat_pat`/`flat_gen`/`flat_lcl_proc`/`zframe_graph`) are always 0 for any graph containing `IR_MATCH_BEGIN`, because those flags are set only for blob/proc/gen/zframe graphs, which are jmp-entered and never contain a `MATCH_BEGIN`. **The absence of MATCH_BEGIN-incompatible opcodes in `g_emit_cfg` is therefore the sufficient guard.**

`SCRIP_OS_CAP=0` restores 0 byte-identically. ⚠ At HEAD `SCRIP_OS_CAP` lives in `bb_match_begin.cpp`/`bb_match_end.cpp` and the named carrier function `stfh_carve_bytes` no longer greps in `src/` — the authority moved; re-locate it before citing the name.

## §5 ZD-5b — the K=0 leaf class and the ARM DESCENT

**The K=0 leaf class (s24b–s32).** Blob-interior leaf kinds were admitted **KIND BY KIND**, each after (a) its template ZD arm, (b) the wpop β-tag fix, and (c) the Kc `has_blob` gate fix. The recovered per-kind ledger, which is the cheapest correct summary of what each match leaf costs:

| kind | K | nops | body |
|---|---|---|---|
| `LIT` | 0 | 0 | scanner-register-only |
| `LEN` | 0 | `n_operands` | dynamic arm reads `ZOPQ(0,8)` |
| `ANY` / `NOTANY` | 0 | `n_operands` | dynamic arm reads `ZOPQ(0,8)`/`ZOPD(0,4)` for charset ptr/len |
| `POS` / `RPOS` | 0 | `n_operands` | zero-width predicate, `ZOPQ(0,8)` |
| `TAB` / `RTAB` | 16 | `n_operands` | cursor save across β in `ZRESD(0)`; RTAB targets from end (`r15d`-arg) |
| `REM` | 16 | 0 | cursor save in `ZRESD(0)`; no arg, always static |
| `SPAN` | 16 | `n_operands` | `ZRESD(0)`=old `r14d`, `ZRESD(4)`=scan counter |
| `BREAK` / `BREAKX` | 16 | — | scratch slot saves old `r14d` / scan delta across β, same shape as TAB |
| `ALTERNATE` | 0 | — | zero-cell envelope; the ALT-FLAT arm uses per-BB frame-relative address slots |
| `FENCE1` | — | — | O-7/s30: a law-4 `___` user whose watermark slot `FRQ(off)` is depth-free under the ZW canonical frame |

⭐ **The arm-descent defect and its two attempts.** The linear γ-walk threads **through** an `IR_MATCH_ALTERNATE` as one admitted K=0 node, so its arm interiors — hung as `(entry, resume)` **operand pairs, never γ-children** — were *closure-only*: `zon=0`, no `ZOPQ` staging, and every evaluated-operand charset primitive inside an arm fell back to the flat `FRQ` read.

**MEASURED, and the number is the whole lesson:** that flat read resolves across the live `mrbp` frame (64B) **plus** the s61 ALT record (32B) — exactly **96 high**. Witness `probe/zd5b/alt_span_concat_segv`: **emitted `[rsp+216]`, truth `[rsp+120]`** — the `TDump_driver` SIG11 signature verbatim.

- **First attempt (s24a) BLOCKED and the blocker is worth keeping:** a naive phase-2 walk that descends arm entries *after* the main γ-chain loop claims arm-interior nodes **speculatively, before the blob closure `cm[]` is computed** — which **steals nodes from other statements' γ-chain walks and corrupts their runs.**
- **The landing (s102):** descent roots **ONLY at ALT nodes already claimed into THIS run**, so their operands are this statement's blob *by the closure definition* — the s24a cross-statement steal **cannot occur**.
- ⛔ **LEAF-ONLY SLICE, per-ARM not per-ALT:** an arm chain admitting anything outside the op-filtered leaf set (DEFER incl. `PATV$`, nested ALT/SEQ, captures, ARBNO, FENCE1) is **unclaimed WHOLE** and stays closure-only. Because the grain is the arm and not the ALT, a `(SPAN(...) | *defer)` mix **still arms the span arm**.
- **Depth model (design §3a as amended s61):** an arm member's `zout` = `zout[ALT]` + intra-arm cumulative K — a **cells-only ledger**; the frame and the ALT record are **off-ledger and ride the crossing sum**. Reset per arm chunk via the private entry bits. `zd_arm[ci]` carries the enclosing ALT's `nodes[]` index to the `+32` conjunct at the staging site, and an ARM-INTERIOR consumer reading a producer outside its arm is the **ALT-RECORD CROSSING** case.
- **EVALUATED-ARG-ONLY (s102, a measured narrowing):** claiming const-form leaves (`n_operands==0` — literal `LIT`/`LEN(k)`/`POS(k)` arms) into the armed set buys nothing and was narrowed back out.

`SCRIP_ZD_5B=0` is the killswitch and still lives at HEAD.

## §6 `alt_arm_member` — THE ONE ALT-ARM CONTAINMENT AUTHORITY (s130)

⭐⭐⭐ **The question it answers:** *is either node ON some ALT arm's γ-chain in this run?*

Every `IR_MATCH_ALTERNATE` in the statement is walked arm by arm; **arm j is the γ-chain from `operands[2j]` (entry) to `operands[2j+1]` (resume)** — the `SN4-NARY-ALT` layout. Three structural facts make the walk exact:

- A node **WRAPPING** an ALT — `(A|B) . Y` — sits before/after the arms and is **never on one**. Control witnesses stay on the spine.
- Nested `ALT`/`ARBNO`/`DEFER` inside an arm are **single chain steps** (their γ *is* the step), so an interior member of a NESTED arm is **reached through that nesting, not missed**.
- It is **PURE and plan-independent**, and `b` may be NULL for callers with no paired second node.

⛔ **Why it is one function and not two.** It was **EXTRACTED VERBATIM from `cap_in_alt_arm`'s own loop** (s93 R-0) so that the containment *fact* is spelled ONCE and its two customers — the **CAPTURE half** (`cap_in_alt_arm`) and the **LEAF-SUSPENSION half** (`leaf_frame_member`, s130) — **cannot drift apart. They are the same ζ-SPINE denial, so they must be the same predicate.** This is the `s68`/`s70` *spelled-twice disease* named and cured in place.

### The ζ-SPINE denial classes

All of these share one shape: **`zd_plan` grants per RUN, and certain interiors are never in a run, so a node there has no flat `rsp` price and must ride a ζ-STANDING slot** (`frame_need_of()==1` → `capture_frame_slot()`).

- **R-0 (s93, GOAL-SNOBOL4-100 M1 ROOT CAUSE)** — a capture pair whose `SAVE..COND/IMM` span lies **inside an ALT arm** is the s66/s71 *ungranted ALT arm* denial class.
- **R-4(a) (s95, bb_probes class A, 15/20 m4 failures)** — the **dual** of the nested-span scan and the **sibling** of `cap_in_alt_arm`: a capture pair whose SAVE lies inside the body span of an `IR_MATCH_ARBNO` (`[operands[1]..operands[2]]` in `all[]`-order — *the* containment idiom the DEFER-unsafe scan, `arbno_frame_candidate` and the K16 prelude all use) or an `IR_MATCH_FENCE1` (`[operands[0]..operands[1]]`). **MEASURED N04:** the K16 route stages `kk=16` for the SAVE's own carve, the SAVE box carves it, then **bombs — classifier and plan disagree, in the bomb text's own words.**
- **PF-1d (s178-b)** — an **ARM-INTERIOR consumer** is the ungranted-arm denial class (nested-ALT arms are unclaimed by the descent) and its `op_sa` seat is a slot **nobody writes since the s97 dead-spill deletion**, so the producer frame-homes and the seat (`XSAQ`/`XSAD` or `ZOPQ`) reads the **SAME `rbp` slot**. Same containment authority as the CAPTURE and LFC customers. Live at HEAD inside `xop_frame_member`.

## §7 The frame-home killswitches — and what happened to them

Each was a function-local-static `getenv` cache, the shape every killswitch in this file uses. **Three of the four are gone at HEAD and their predicates went unconditional — read every "DEFAULT OFF" below as history, not as current behavior.**

### s130 `SCRIP_SPAN_FRAME` — the leaf-suspension frame ⛔ GONE at HEAD

⭐⭐⭐ **TWO READERS IN LOCKSTEP** — `leaf_frame_member()` (which feeds the registry scan, hence the carve width at **both** `emit_match_begin_frame_extra` and `blob_frame_bytes`) and `leaf_frame_slot()` (which feeds the template's staged offset) — **so the frame the prologue CARVES and the slot the template ADDRESSES are one decision and cannot drift.** That is the s124 two-reader law and the s66 coherent-worlds law, mechanized.

**What the arm cures:** the *leaf-suspension wild-write class* — a leaf on an ALT arm addressing its cell at a **raw flat ZLS coordinate off `rsp`** and writing **above the live frame** once earlier statements push that coordinate past it.

**Flipped default ON at s188** (HQ-59 ruling, Lon desk delegation 2026-08-20, the fz3-flip precedent), once the s184 `TDump_driver` blocker was itself cured at `sn4_xh_frame_extra` (SCRIP `0b75fa5e`). **RECEIPTS at pristine `0b75fa5e`, `RT_OPT -O0`, one build, both arms selected by env:**

- `.s` sweep: **13 movers / 527 comparable**, every changed line a carve / `retry_whack` / ALT-arm leaf re-home / registry renumber / flat-spine rebase **by exactly the carve delta**, and **ZERO spine-resident re-homes** (the HQ-60 acceptance).
- 6-suite board: **1222 rows × 2 modes, 4 movers, ALL CURES, ZERO REGRESSIONS** (control self-run noise floor 1).
- corpus **m3 332/5, m4 325/11, SKIP 1**, fail-set identical by name.

⛔ **HQ-60 — SPINE-RESIDENT LEAVES KEEP RSP.** `leaf_frame_member()`'s `alt_arm_member` conjunct is **LOAD-BEARING** and s188 did **not** widen it: re-homing spine leaves wholesale was **measured broken** (s127: programs 120/131/165/181/182). ⭐ **This is the single most important sentence in the cluster, and it is the one the current source cannot tell you.** At HEAD the predicate reads

```c
static int leaf_frame_member(const IR_t * nd) {
    return nd && zdp_scratch_cell(nd) && (alt_arm_member(nd, 0) || blob_frame_scope());
}
```

— the two `getenv` conjuncts were deleted when the switches went away, but **the `alt_arm_member` disjunct is still doing HQ-60's work**, and a future rung that "simplifies" it to `zdp_scratch_cell(nd)` alone re-runs s127's five-program break.

### s177 `SCRIP_PT_FRAME` — the pass-thru frame ⛔ GONE at HEAD

**Law 0c mechanized:** a scratch-cell leaf inside a **SEAM-ENTERABLE graph** (a blob — no `MATCH_BEGIN` of its own) **may not price its cell as a flat `rsp` offset, because what sits above it is the CALLER'S ACTIVATION** — unknown count, unknown type. **MEASURED (s177):** `TAB(3)`'s `[rsp+64]` landed **ON the caller's banked γ wire**, `pc=0x1`.

Under the switch, every `zdp_scratch_cell` leaf in blob scope becomes a registry candidate and homes in the blob's **own `rbp` frame** (the `frame_slot_scan` rc-2 arm, a 2-slot claim). **NARROWER than `SCRIP_SPAN_FRAME`**, which also re-homes ALT-arm leaves in *statement* graphs: this one is blob scope only. Its residue at HEAD is the `blob_frame_scope()` disjunct above.

### s178 `SCRIP_PT_OPFRAME` — the crossed-operand frame ⛔ GONE at HEAD

Law 0c, **tier-2 escalation, applied to the ζ-VALUE-OPERAND plane**: a producer whose consumer's `op_zread` span **crosses a VARIABLE-RETENTION box** (`MATCH_DEFER`/`ARBNO`/`VALUE` — `earn_hazard_in`'s family) **has no flat `rsp` price.** The defer's γ road retains the inner blob's 32B resume record **plus its own suspended cells (unbounded)**; the C road retains 16. **Measured to the byte (s178-L2):** `bfn_break_var`, `[rsp+40]` needle read garbage — *four layout faces of one wild mechanism*.

It **followed `sn4_pt_frame` when unset** (the PF-1b ensemble precedent: `SCRIP_PT_FRAME=0` reverted the whole pass-thru family), with an explicit env winning either way. Its residue at HEAD is `xop_frame_member`, which still carries the hazard walk (`xop_hazard_kind` over `DEFER`/`ARBNO`/`VALUE`) and still consults `alt_arm_member` for the PF-1d case.

### s189 `SCRIP_ARBNO_REENTRY` — the ARBNO re-entry frame ✅ STILL LIVE, STILL DEFAULT OFF

⛔ **DEFAULT OFF, DELIBERATELY, AND THE REASON IS THE POINT OF THE ROW: the arm is CORRECT AND NECESSARY BUT NOT SUFFICIENT.** It moves the ARBNO cursor from a flat ζ-SPINE cell to the per-activation blob slot (`[rsp+0]`/`[rsp+4]` → `[rbp-48]`/`[rbp-44]`, measured), which is exactly what a re-entrant activation requires — **and the witness stays RED**, because a **second** fact is computed over the same wrong span: `op_arbno_body_actframe` at the drive case, which decides whether the `af->retreat` edge is emitted **at all**. Red emits `cmp r14d,eax; jmp PAT$N_ω` — the s184 absent-edge signature, with the `cmp` setting flags nothing reads.

**Landing it ON would move bytes for ZERO behavioural gain**, so it ships **armed and off**: default output is byte-identical by construction (a refused candidate never enters the registry, so count, indices and carve are unchanged) and the next seat gets the storage half already built and measured.

⭐ **The scan's span is the whole defect, and the proof is a semantically inert edit.** The two body scans ask whether *this ARBNO's own body* is defer-unsafe, but the hazard the frame slot exists to answer is *"can an ACTIVATION re-enter while this ARBNO instance is still live and RETRYABLE"* — **and that is created by everything to the ARBNO's RIGHT, not by its body.**

Witness `ptw_min_arbno_altrec_falsereject`: `E = ARBNO('a') ('+' *E | '')` on `'a+a+a'`. The body is the plain literal `'a'`, so both scans refuse, the cursor stays a flat ζ-SPINE cell (`sub rsp,16` at α, read back `[rsp+0]`/`[rsp+4]` at `_as`/`_af`), the recursive activation between the carve and the reads **displaces it**, the outer ARBNO never extends, and **a matching subject is REJECTED**.

**PROOF:** adding a **semantically inert** `*Z` with `Z = ''` inside the body — which cannot change what the pattern matches — **flips the witness GREEN**, and the asm moves the same cursor to `[rbp-48]`/`[rbp-44]` = `frame_slot_off(blob,0)`.

**Membership is LOCATION, never identity** (`leaf_frame_member`'s own law, and RULES.md's frame-placement criterion in one line): inside a blob activation — which is **by definition** the callee of a `*P` defer, R-4(b) — **any** DEFER anywhere in the graph can lead back here directly (a1) or mutually (a20: `E -> *G -> *E`, measured red), **so every ARBNO in a defer-bearing blob claims a per-activation slot.** Deliberately a **SUPERSET** of the body scans, so no arm above it changes answer.

✅ **Still true at HEAD** (`emit.cpp:2332`): `v = (e && *e == '1') ? 1 : 0` — off unless explicitly set. The storage half is still built, the `op_arbno_body_actframe` half is still owed, and the row `arbno-altsib-residue` is open in substance two sessions on.

## §8 ZK-2 — the graph-wide back-edge refuse (s226)

A chased γ/ω edge from `nodes[_bi]` landing on `nodes[_bj]` with `_bj <= _bi` (`nodes[]` is execution order) **is a loop back-edge**, and the per-run guard **cannot see it when the edge crosses run boundaries** — `while`/`until`: body-run `ASSIGN.γ → GOTO → condition-run VAR`.

**Why it must be refused:** a back-edge join is **reached at two RSP depths** — 0 on first entry vs ΣK after one lap of carves — so `ZOPQ` offsets staged for the first depth **read wrong memory on lap 2+**. **MEASURED:** `until_minimal` printed **5 not 4** under the mixed per-statement regime; `countdown` wrote **1..5 not 1..3**.

The early return leaves `zon[]` all-zero — the existing self-refuse pattern — so the whole graph takes the non-ZD `FRQ` arm, behaviorally the working UCLAIM path. ⛔ **CONSERVATIVE BY DESIGN:** it refuses **every** statement in a loop-containing graph, including straight-line ones; ZK-6's suspension mechanism owns per-lap release and will narrow it. Two details that are easy to lose: **`zd_chase` both edges**, because the back-edge's last hop is a GOTO wire and a raw-edge compare misses it; and `_bj <= _bi` **includes self-loops**. Gated on `icn_cells_graph`, so SN4/Prolog are byte-identical by construction. **s22k law: no K spelled here.**

## §9 The BRICK-WALL census — the wall is a graph property, not a construct

Lon, directive 2026-08-03c, verbatim: *"continue this for every box and every construct until you hit a BRICK WALL and realize, oh I need a register ___ stable base pointer for what I'm doing."*

⭐ **THE CLAIM THIS MEASURES: the brick wall is not a CONSTRUCT, it is a GRAPH PROPERTY.** Sliding `rsp` offsets are well defined **exactly when every box has ONE static entry depth**. The wall is a **JOIN whose predecessors arrive at DIFFERENT accumulated depths**, because no `[rsp+k]` spelling can name the same cell down both edges.

⛔ **The consequence for the law:** the standing list of four `___` constructs (`STATEMENT`/`FUNCTION`/`ARBNO`/`FENCE1`, the s21x-c law 4) should be the **OUTPUT** of this test, not its input — **and if the measured set is wider, the list was never the rule, it was a sample of the rule.** This is the same conclusion RULES.md § BB FRAME-PLACEMENT CRITERION reaches from the other side: placement is decided by a behavioral test, never by box-kind.

**ARRIVAL-DEPTH MODEL**, taken verbatim from the UNWIND four-clause law (HQ 2026-08-03b) **so the census cannot drift from the emission it audits**:

- a **γ** edge SUSPENDS the box's own cell (clause 1, roll up forward) → arrives at `zout[i]`;
- an **ω** edge FREES the box's own K first (clause 2, *"box N's omega frees N's OWN K only"*) → arrives at `zout[i] - K`;
- **two edges into one target with unequal arrival depth = WALL.**

**READ-ONLY BY CONSTRUCTION:** no `g_emit` write, no emission, no `zd_*` mutation — it consumes `zd_plan`'s finished `zon[]`/`zout[]` and prints. Inert unless `SCRIP_ZD_DEPTH=1`, so the default build is byte-identical and it can ride any rung without gating it.

⛔ **REFUSED nodes (`zon=0`) are SKIPPED, not assumed depth 0.** Their depth lives in the UCLAIM wholesale claim — precisely the regime the census exists to help retire — and **counting them as 0 would manufacture disagreements that are artifacts of the claim, not of the graph.** `SCRIP_ZD_DEPTH` still lives at HEAD.

## §10 Names in the recovered text that no longer exist

| name | status |
|---|---|
| `sn4_span_frame` / `SCRIP_SPAN_FRAME` | ⛔ gone; residue = the `alt_arm_member` disjunct of `leaf_frame_member` (§7, HQ-60) |
| `sn4_pt_frame` / `SCRIP_PT_FRAME` | ⛔ gone; residue = the `blob_frame_scope()` disjunct of `leaf_frame_member` |
| `sn4_pt_opframe` / `SCRIP_PT_OPFRAME` | ⛔ gone; residue = `xop_frame_member` + `xop_hazard_kind` |
| `stfh_carve_bytes` | ⛔ no longer greps in `src/`; `SCRIP_OS_CAP` moved to `bb_match_begin.cpp`/`bb_match_end.cpp` (§4) |
| `pl_cells_graph` | ⛔ gone; PL-ZK-4b/PL-ZK-5 were written against it (§3) |
| `leaf_frame_off` | ⛔ gone as a function; survives as the staged field `op_leaf_frame_off` (`x86_asm.h`: `LFC_ON`/`LFC`/`LFCQ`) |
| `SCRIP_ZD_MATCH` | ⛔ deleted, not defaulted — Lon's REGIME DELETION (§3, ZD-5) |
| `FINDING-2026-08-09g`, `FINDING s177`, `FINDING s178-L2`, `FINDING s178-FW` | ⚠ deleted from the tree (`f78d8b3fd`, `c0d7427ee`), **recoverable from `.github` history**; their measurements are quoted in §4, §6, §7 |
| `ARCH-PASSTHRU.md` (law 0c) | ⛔ never existed under that name in `.github`; law 0c is stated in §7 |

## §11 What this file does NOT yet cover

`src/emitter/emit.cpp` had **746** stripped comment spans; this relocation covers the **109** in the ZD/frame-home family. The remainder is still owed and is ranked in `RATIONALE-INDEX.md`. The next-densest untouched clusters in this file, by tag count, are **FZ-1/FZ-2/FZ-3** (the FENCE0 release plan and the depth model's visibility of the release, s166/s168), **ZW-5/O-1/O-2** (the ω stub pool and the staging choke), **M-2** (the MATCH_BEGIN pre-head depth bugs), **R-3(c)/R-5b** (the subject seat and driver handoff), and **PL-ZK-3/LP-2** (the proc-entry cells carve and the layout pass). Row-factory rule: take one, not all of them.
