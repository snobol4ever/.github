# GOAL-SN4-HOME-RBX — RBX = GC heap-top; allocation + GC coverage (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER (Lon s30):** SNOBOL4 addressing is RSP + RBP + **RBX GC-heap-top relative**. Formalize rbx as the allocation frontier (today's DESCR mint pointer), make emitted code allocate inline against it, and make the GC actually see every register-resident and arena-resident root. rbx is callee-saved — the C boundary is free, same property as rbp.

## RUNGS
- [x] **X-0 · THE CONTRACT, WRITTEN (s33).** Deliverable = **§ THE CONTRACT** below (16-row GPR map + frontier invariant + safepoint/C-crossing/authority/overflow + the GC COVERAGE LEDGER that arms X-1). Zero code. Read cold as directed: `REGISTER-LAYOUT.md`, `DESIGN-SN4-REGISTER-PLANES.md`, `gc_heap.c`, `zeta_heap.c`, `x86_asm.h` REG-4b, the `rt_gcheap_alloc` mint path, + SPITBOL manual Ch.4/13/19 storage semantics. **THREE PRIOR RBX CLAIMS RECONCILED, TWO KILLED:** REGISTER-LAYOUT.md "rbx = DESCR BASE POINTER" is the frontier seen from 2026-05-31 and is SUBSUMED (a mint pointer IS a frontier); DESIGN-SN4-REGISTER-PLANES.md "rbx = VALUE plane / E frame base" is **DEAD FOR SNOBOL4** — that doc's own status line says nothing implemented, and E-as-rbx is unrepresentable alongside the frontier claim. This file is now the ONE authority; REGISTER-LAYOUT.md is history in full, not just its r12 row.
- [x] **X-1 · RC-8a — THE GC-SCAN GAP. CLOSED s33** (SCRIP `9ecb75a9`). Both regions now pin+range; gate `scripts/test_gate_rc8a_gc_coverage.sh` GREEN with a positive control on every assertion (`SCRIP_GC_UNROOT={cas,rtcc}` re-opens the hole: armed `ranges=1 cas=40`, sabotaged `ranges=0 cas=0`). Set diff vs own-HEAD control m3: patterns 76/46 **identical by set**, gc 15/15, capture 8/1. Emitted `.s` **byte-identical** HEAD vs X-1 (`cmp`) ⇒ no codegen touched, RULES step-4 regen not triggered — proved, not asserted. Original text: **RC-8a — THE GC-SCAN GAP (BLOCKING, inherited from RTCC s16).** `rtcc_gc_register` pins the pointer, scans nothing (`rt_gc_root_pin_add` only; every other block does `rt_gc_root_range_add` too). Add: RTCC block slots + **r12 pending-arena records** (they hold δ/target refs — the s30b obligation (ii)) + rbx frontier semantics to the scan. Latent at HEAD, LIVE the instant the arg tier is claimed.
- [ ] **X-2 · FUNC-11 — ⛔ PREMISE CORRECTED s34: THIS IS NOT AN ALLOCATION DEFECT.** The mechanism is a per-iteration RSP release imbalance (`+0xCC0`) on `-INCLUDE`d loop bodies — see LIVE CURSOR § s34 PLAN SCRUTINY + `FINDING-2026-08-12f`. The original rung text is retained below as history and for its still-valid `-INCLUDE` coverage-hole obligation; **the live work order is in the cursor, and the seating of this rung is an open question for Lon/BOARD.** Original: **INSTRUMENT THE ALLOCATION ITSELF.** ⛔ STANDING INSTRUCTION (three seats, three falsified threshold constants): NO more black-box sweeps. Counter in the runtime path (or core-file technique) → convict the include-scoped capacity for runtime-created variables → fix. Then own the `-INCLUDE` coverage hole (crosscheck has ZERO live `-INCLUDE`; promote the `rtx11_dynvar` probe family with BOARD). **ACCEPTANCE: the BEAUTY drivers (17/17 SIGSEGV at HEAD, one include; `probe/rtx_func_11*` is the reduced two-sided witness) go GREEN both modes — this rung owns the flagship's blocker; the flagship byte-identity itself is P4's seal (HOME GATE line 6).**
- [ ] **X-3 · INLINE BUMP-ALLOC ARMS.** Hot mint paths go register-only against rbx (M-SLEN precedent: zero C calls), killswitched per family, both media, per-family kill-switch bisectable.
- [ ] **X-4 · ZHP EXHAUSTION CLASS RE-CHECK.** The s29 rc=134 arm (`[ZHP] heap exhausted`) is plausibly LOWER Defect B's mechanism — verify AFTER HOME-LOWER L-2 lands; do not inherit the plausibility as fact.
- [ ] **X-5 · RTCC RESIDUE ADOPTED (s31): RC-8b + RC-8c.** ⛔ **GATED ON X-1** (RC-8a blocks RC-8b — RTCC s16 ruling). RC-8b arg tier (rax rcx rdx rsi rdi): claim it or stop paying — 5 of the veneer's 14 instructions are pure cost at HEAD (stores reloaded by nothing; `wb_bin`'s RAX-as-base story must be PROBED before dropping — instrument named RTCC s16c: walk the 12 `x86("rtcc_wb")` sites and identify the call each brackets; do NOT re-derive the false zero from `x86_rtcc_call` greps). RC-8c: stage XMM8–15 or AMEND the charter to 9 GPRs — at HEAD no rung stands behind the XMM claim at all. RC-5 anchor re-open + RC-7 fold stay PARKED in GOAL-RTCC pending Lon + X-1.

## ⭐ THE CONTRACT (X-0 deliverable, s33 — ONE AUTHORITY for the SNOBOL4 register file and the rbx frontier)

### A · STATE AT HEAD — the frontier is BUILT, and it is NOT the default port
The rbx bump frontier already exists and is corpus-exercised. It is **REG-4b (s78)**, `x86_asm.h:2320-2333`, gated `site==X86H_DEF && port==X86P_ALPHA && hk>0 && x86_port_mode()==ZC_PORT_HEAP`:
`mov rax,rbx` · `add rbx,K` · `cmp rbx,[RT_WS_LIMIT]` · `ja L60` → `mov edi,K` / `call rt_zh_bump_slow` / `mov rbx,[RT_WS_TOP]` · `L61`.
⛔ **`ZC_PORT_HEAP` is port 7; the compiled default is `ZC_PORT_FORTH` (6)** (`scrip.c:470`, `--zeta-port=heap`, `SCRIP_ZETA_PORT=7`). So at HEAD **rbx is architecturally claimed but dormant on the default path** — X-3 is therefore NOT "write a bump allocator", it is **"promote an existing, proven arm to the default port and make its residence real"**. K is `op_zls2_bytes` (when `ops==0`) else `op_fc_bytes` — **the SAME static-K grant `fc_geom` hands the FORTH port**, spent as `sub rsp,K` there and as the rbx bump here. Port-blind geometry, port-selected flavor. Today under HEAP the fc *consumers* stay FORTH-gated, so the block is **allocated-but-unread** — the deliberate proving configuration (frontier arithmetic + refills exercised, semantics untouched). Making the locals actually RESIDE in the block is the X-3 slice-2 work, and it is the part that has never run.

### B · THE 16-ROW GPR MAP (supersedes REGISTER-LAYOUT.md entirely for SNOBOL4)

| reg | class | SNOBOL4 role at HOME | who writes it | live across C? |
|---|---|---|---|---|
| **rax** | caller-saved | scratch; **fresh-block base out of the REG-4b bump** (see HAZARD-3); RTCC arg-tier candidate (X-5) | anyone | no |
| **rcx** | caller-saved | scratch; RTCC arg-tier candidate (X-5) | anyone | no |
| **rdx** | caller-saved | scratch; RTCC arg-tier candidate (X-5) | anyone | no |
| **rbx** | **callee-saved** | ⭐ **GC HEAP-TOP / ALLOCATION FRONTIER** — next free byte in the current ζ-heap block | **α only** (REG-4b) + flat prologue seed + `rt_zh_bump_slow` publish/reload | **YES — by SysV, and the contract depends on it** |
| **rsi** | caller-saved | scratch; RTCC arg-tier candidate (X-5) | anyone | no |
| **rdi** | caller-saved | scratch; first C arg; RTCC arg-tier candidate (X-5) | anyone | no |
| **rsp** | special | FORTH spine — box operands, ζ cells, choice/resume records; compile-time-constant offsets always | carve (`sub rsp,K`) / cut | yes |
| **rbp** | **callee-saved** | **EARNED frames ONLY** (`frame_need_of`); ONE ENTER at α; `[rbp+ANCHOR]` chain to MATCH_BEGIN | **α/ω SOLE writer** (EARN-11) | yes |
| **r8** | caller-saved | RTCC slot | RTCC | via veneer only |
| **r9** | caller-saved | **GVA base** (RTCC LIVE claim) | RTCC | via veneer only |
| **r10** | caller-saved | **rΓ wire** (both glue kinds, one product-wide convention) | template-emitted per-activation saves | via veneer/save only |
| **r11** | caller-saved | **rΩ wire** | template-emitted per-activation saves | via veneer/save only |
| **r12** | **callee-saved** | **capture-pending arena TOP** (CAS discipline, mmap'd, STACK discipline); restored at backtrack re-entry (oracle pin W5) | CAS push/pop | yes |
| **r13** | **callee-saved** | **Σ — subject BASE ptr** | match entry | yes |
| **r14** | **callee-saved** | **δ — CURSOR** | match step; restore rides the choice record | yes |
| **r15** | **callee-saved** | **Δ — subject LENGTH/END** | match entry | yes |

**Corollary — the callee-saved set is FULLY SUBSCRIBED:** `{rbx, rbp, r12, r13, r14, r15}` = `{frontier, earned frame, pending arena, Σ, δ, Δ}`. Six of six. There is **no callee-saved register left** for any future claimant; every further claim must come out of the caller-saved tier through RTCC veneering (X-5) or out of an existing tenant by eviction. Record this before someone spends it twice.

### C · RBX = FRONTIER INVARIANT
1. **rbx always points at the next free byte** of the current ζ-heap block: `g_zh_block_base ≤ rbx ≤ [RT_WS_LIMIT]`.
2. **rbx is never a live-object pointer.** It is one-past-the-last-allocation. Nothing may dereference rbx; only `rax = rbx` (pre-bump copy) is an object base.
3. **`[RT_WS_TOP]` (`pin_va.h:11`) is the SYNC CELL, not the frontier.** It is authoritative only (i) across a refill and (ii) at the outer-graph seed. Between those it is STALE by design — the live frontier is the register. Anyone reading `[RT_WS_TOP]` to learn the frontier mid-graph reads a lie.
4. **Cold rbx is NOT self-healing.** `garbage + K` vs limit is unsigned luck. The outer flat prologue **SEEDS** rbx from `[RT_WS_TOP]` (zero page ⇒ rbx=0 ⇒ first guard trips ⇒ lazy init falls out for free). **Inner entries — jmp-entry procs, EVAL/CODE fragments — SEED NOTHING and inherit rbx live.** Their correctness rests entirely on rule E.
5. **ω emits nothing.** There is no frontier decrement; reclamation belongs to the LIVE/DEAD lifecycle, never to a pop. Allocation is monotone within a block.

### D · SAFEPOINT PORTS
A **safepoint** is any instruction boundary where `gc_collect_ex` can run: every `call` into the runtime that may reach `rt_gcheap_alloc`, plus the explicit `COLLECT()` builtin. **α is a safepoint** (its slow arm calls `rt_zh_bump_slow` → `rt_gcheap_alloc` under `ZC_ZH_IN_GCHEAP=1`, `zeta_choices.h:108`).
Roots are gathered at `gc_heap.c:625-638` in this order: pins → ranges → WS interior → `rt_gc_ws_roots` → (env) static blanket → coexpr roots → **`setjmp(jb)` + conservative scan of `jb`** → C stack → `gc_root_zeta` → `core/gen/args` roots → shields.
⭐ **The register file is rooted by the `setjmp` trick alone** (`gc_heap.c:634`): `setjmp` spills the callee-saved set into `jmp_buf`, which is then conservatively scanned. **Therefore rbx/r12/r13/r14/r15 are GC-visible only on the `!pz && cons_stack` path.** `pz` ("punt zero", `:621`) skips all of it.
⛔ **CORRECTED s33 by X-1 measurement — this paragraph originally predicted that arming rbx would disable `pz`, and charged that cost to X-3. FALSE: `pz` is ALREADY DEAD AT HEAD and X-3 does not owe it.** RTCC's constructor (`rtcc_init.c:24`) calls `rtcc_gc_register()` unconditionally with `g_rtcc_on` defaulting to **1**, so `g_gc_rpin_n >= 1` from before `main`, so `pz` is false in every run and `cons_stack` is forced to 1 at `:622`. Measured, not reasoned: **every** `[GC-COV]` line emitted across the X-1 census reads `pz=0 cons_stack=1` (2432 collections on one program under stress, plus every witness). The conservative stack+register scan is therefore the *existing* regime, not a new charge. **Standing lesson for this seat: I predicted a cost from reading the guard and was wrong about who already paid it — the census line is cheap, run it before pricing anything else.**

### E · C-CROSSING RULE
rbx is callee-saved under SysV, so **an ordinary C call preserves the frontier for free** — the same property that makes rbp workable, and the reason the charter pairs them. Rules:
- **No veneer is needed or permitted for rbx.** RTCC veneering exists for the caller-saved tier; adding rbx to it would create a second writer and break § F.
- **Any hand-written asm that clobbers rbx must save/restore it.** This is a live obligation, not a hypothetical: see HAZARD-1.
- **Coexpression switch must carry rbx.** `bb_create.cpp:22` already stores `{r12,r13,r14,r15,rbx,rbp}` into the coexpr frame — that six-register set is *exactly* the callee-saved tenancy in § B, and it is correct by construction. **Do not add a seventh name there without amending § B.**

### F · ONE AUTHORITY — who may move rbx
**Exactly three writers, and no fourth may be added without amending this section:**
1. **α under `ZC_PORT_HEAP`** — `add rbx,K` (REG-4b, `x86_asm.h:2323`). The only *fast-path* writer.
2. **The outer flat prologue** — seeds rbx from `[RT_WS_TOP]` at graph entry. The only *seeding* writer.
3. **The REG-4b slow arm** — `mov rbx,[RT_WS_TOP]` after `rt_zh_bump_slow` publishes. The only *refill* writer.
Everything else — templates, RTX hand asm, runtime C, wires, ZCTX — **reads never, writes never**. Enforcement is a claim-gate row over `rbx` (HOME GATE line 3 already names rbx in the data-driven claim gate); the gate is what makes this checkable rather than aspirational.

### G · OVERFLOW → ISLAND GROWTH PATH
`rt_zh_bump_slow(bytes)` (`zeta_heap.c:152-168`): round `need=(bytes+15)&~15`; `blk = max(need+16, 1MB)`; carve via `rt_gcheap_alloc(HB_ZBLK, blk)` **from the collected span** (`ZC_ZH_IN_GCHEAP=1`); on success **`rt_gc_root_pin_add(base)` AND `rt_gc_root_range_add(base, base+blk)`**; publish `[RT_WS_TOP]=base+need`, `[RT_WS_LIMIT]=base+blk`; return `base`. Failure ⇒ `abort()` with `[ZH-BUMP] FATAL`.
Three properties to carry forward:
- **The whole 1MB block is a root RANGE.** Every object bump-allocated inside it is conservatively scanned wholesale. Individual bump results therefore need **no** individual rooting — this is what makes the inline fast path safe without a write barrier.
- **Old-block tail residue is LEAKED BY DESIGN (v0).** The refill abandons the remainder of the previous block; nothing recovers it.
- ⛔ **Pins and ranges are added and NEVER removed** (`root_pin_del`/`root_range_del` exist but are not called on this path). Under a long run this is monotone growth of both the pinned set and the conservatively-scanned area — i.e. **GC cost rises with the number of refills, forever.** Not a defect to fix in X-0; a number to measure in X-3 and a candidate for the LIVE/DEAD promotion the REG-4b comment defers to.

### H · GC COVERAGE LEDGER — the X-1 work order, mechanically established
`rt_gc_root_pin_add` → `rt_gc_pin_ptr` keeps the *containing block* alive (`:625`). `rt_gc_root_range_add` → `gc_cons_scan` walks the *interior* and marks referents (`:626`). **Pin ≠ scan. A pinned-only region's contents are invisible.**

| region | pin | range-scan | verdict |
|---|---|---|---|
| ζ-heap refill blocks (`zeta_heap.c:161`) | ✅ | ✅ | **COVERED** — the correct pattern, and the template for the rest |
| coexpr stacks (`rt_coexpr.c:74,170`) | ✅ | ✅ | **COVERED** |
| callee-saved registers incl. rbx/r12 | — | ✅ via `setjmp(jb)` `:634` | **COVERED, conditionally** — only when `!pz && cons_stack`; see § D |
| **RTCC block** (`rtcc_init.c:26`) | ✅ | ✅ s33 | ⛔ **GAP — CLOSED s33 by X-1.** `rtcc_gc_register` calls `rt_gc_root_pin_add(&g_rtcc_block[0])` and nothing else. Block memory survives; **every DESCR the block holds is unreachable to the marker.** Latent only because the arg tier is unclaimed — **X-5 makes it live**, which is precisely why X-5 is gated on X-1. |
| **CAS capture-pending island** (`pattern_match.c:603-614`) | ❌ | ❌ | ⛔⛔ **TOTAL GAP — CLOSED s33 by X-1.** Carved from `rt_slab_region` (private slab, **not** the collected span). ⭐ **The root cause was a FALSE COMMENT, not an oversight:** the CAS-1 banner claimed the stacks were "covered by `RT_SLAB_GC_ROOTS` today" — that macro is `#define RT_SLAB_GC_ROOTS 0` (`rt_slab.h:14`) **and gates ZERO `#if` bodies tree-wide**; it was the TR-3 libgc compensation and died with libgc at TR-4, taking the coverage with it and leaving the sentence. `rt_cas_roots` had zero consumers from the day it was written. Fixed: `rt_cas_live_span` + `gc_root_cas`, banner corrected in place. |

⇒ **X-1's scope is now exact:** add range-scan to the RTCC block; move or root the CAS island (either carve it from the gcheap like `HB_ZBLK`, or wire `rt_cas_roots` into `gc_collect_ex` as pin+range); assert the rbx frontier's `pz` interaction. **Positive control is mandatory** (GATES): a coverage gate that passes because nothing was allocated is not a gate — it must be shown to FAIL on a deliberately unrooted DESCR.

### I · SPITBOL SEMANTIC ANCHORS (manual v3.7 — the behaviour SCRIP owes, paraphrased)
- **Ch.4 Caution + Ch.19 note 12 — integer/address discrimination.** SPITBOL's collector separates small integers from addresses by MAGNITUDE, which is what forces object size below `&MAXLNGTH`/MXLEN and requires MXLEN to sit numerically below the workspace start. **SCRIP does not inherit that constraint** (DESCR carries a type tag; discrimination is by tag, not range) — but SCRIP's *conservative* `gc_cons_scan` reintroduces the same ambiguity wherever it scans raw ranges, which is now everywhere the frontier blocks live. Expect **false retention** from integers that look like heap addresses; it is a cost, not a bug, and it belongs in the X-3 measurement.
- **Ch.19 note 7 — variable blocks are permanent.** A user-created name (label, function, or variable) allocates a variable block that is **never reclaimed**; the manual explicitly steers associative data to TABLE for this reason. ⭐ **This is the semantic X-2 must satisfy:** runtime-created variables are an unbounded, monotone, never-freed population. Any *fixed* include-scoped capacity is wrong by the language definition, so FINDING-2026-08-11's "include-scoped capacity for runtime-created variables" describes a design that cannot be made correct by raising a constant — it has to grow. That also retires the three falsified threshold constants by argument, not by another sweep.
- **Ch.19 note 8 — CODE blocks ARE collectible** when no longer accessible. Combined with § C.4 (EVAL/CODE fragments inherit rbx and seed nothing), CODE-block collection is a re-entry edge the frontier must survive — it belongs in the HOME GATE line 7 inventory.
- **Ch.11 `COLLECT(i)`** — forces a collection, returns free words, and **FAILS** when it cannot obtain `i` words. Failure (not an error) is the contract; SCRIP's `COLLECT` must preserve SNOBOL4 failure semantics, and the manual notes forcing collections early always costs time.

### J · CONTRACT HAZARDS FOUND (each with a site; none fixed in X-0 — zero code)
- **HAZARD-1 · `xa_flat.cpp:520,526` uses rbx as a SCRATCH SAVE SLOT.** The ICN-FR-2 zframe generator-ω sequence does `mov rbx,rax` (save caller_rbp) … `mov rbp,rbx`, i.e. it **clobbers rbx across a call**, relying on callee-saved to protect its *own* value. This is Icon's surface, not SNOBOL4's — but it is the **same emitter and the same `x86_asm.h`**, and it is a direct § F violation the moment the two planes share a graph (EVAL/CODE, coexpr, any polyglot path). **It also proves the claim gate does not yet cover rbx** — this would have fired. Assign: claim-gate row (BOARD/HOME GATE 3) + a WIRES-style scratch eradication for the Icon arm. Do not "fix" it silently from this seat; file it.
- **HAZARD-2 · `[RT_WS_TOP]` has two writers with different meanings.** `rt_zh_bump_slow` writes it as *the published frontier*; the flat prologue reads it as *a seed*. Nothing writes it back when the graph exits, so after any graph the cell trails the register. Benign today (only refill+seed read it); becomes a live defect the instant anything else consults it. Pin it here so it is never "fixed" by adding a third reader.
- **HAZARD-3 · the fresh block base lives only in `rax` across the α slow arm.** On the fast path `rax=rbx` pre-bump; on the slow path `rax` = `rt_zh_bump_slow`'s return. `rax` is caller-saved and **is not in the `jmp_buf`**, so a collection between the bump and the first rooted store cannot see it *as a register*. **Currently harmless** because the whole block is a root range (§ G) so the object is scanned regardless — but that means **the block-range root is load-bearing for fast-path safety**, not merely a convenience. Anyone who later narrows the range to live extents must add a barrier or root `rax`. State it now, because the narrowing is the obvious future optimization.

## GATES (every rung)
RC-8a coverage gate (self-arming, lands WARN→FAIL on tier claim) · probe + bench BY SET vs P0 floors · positive control on every census (a gate that cannot fail for the right reason is not a gate) · FINDING + cursor move.

## ⭐ LIVE CURSOR — 2026-08-12 s38 (Sonnet 5) — first REAL CODE landed on X-3 this session (SCRIP `044f80f0`). **X-0 CLOSED · X-1 CLOSED · X-2 unchanged from s34** (untouched).

**X-3 fork (a), HALF LANDED, MEASURED, NOT SUFFICIENT.** `bb_glue_flat_enter`/`_leave` now carve RSP
under `ZC_STORAGE_CELL_HEAP` identically to `CELL_STACK`, replacing the deliberate `x86_bomb()` a prior
session put there. FINDING: `FINDING-2026-08-12m-…md`. **Proven zero regression** (probe/bb m3+m4
identical-by-set to s35's baseline; `.s` byte-diff clean on the default FORTH port). **Proven
insufficient** (this is the important, honest result, not a footnote): full BY-SET re-measurement of
patterns/gc/capture under HEAP shows the **pass set is completely unchanged** (36/122, 13/15, 6/9, `diff`
clean against pre-fix snapshots) — only one witness's failure *mode* moved (`158_pat_cap_arbno_each_iter`
SIG11→DIFF; crash eliminated, still wrong). `041_pat_span` (s35's witness) is **unchanged, still SIG11**
— confirming `FINDING-2026-08-12k`'s own fork description: this landed only the `bb_glue_flat_enter` half
of fork (a); the REG-4b central-hook path (`x86_asm.h:2320-2333`) is the sibling gap the fork explicitly
named and this session did not attempt. **NEXT RUNG: read REG-4b in full, add its RSP-carve counterpart
under the same TEMPLATE-ONLY/BOTH-MEDIUM discipline, re-run the same three BY-SET measurements —
acceptance is the pass SET actually growing this time, not just a failure-mode shift.** Do not consider
fork (a) closed until that lands and is BY-SET verified; do not start fork (b) before fork (a) is closed
(per `FINDING-2026-08-12k`'s own ordering).

⛔ **PUSH STATUS: NOT YET PUSHED.** Commits sit local, rebased clean on origin, credential requested
in-chat and not yet supplied (RULES 6b) — this is not a handoff claim, this cursor entry is committed
locally same as everything else this session. Own-HEAD floors stand at the s35 baseline throughout;
nothing in this cursor has been re-measured against a moving floor without saying so.

### PRIOR — 2026-08-12 s37 (Sonnet 5) — RECONCILIATION of two concurrent same-seat sessions (s35/s36, both starting from s34, s38b-class near-miss — see s36's own CONCURRENT-SESSION NOTE below; no file-write collision occurred, both pushed cleanly, this entry merges the substance per RULES "if two seats touch one file, merge it"). **X-0 CLOSED · X-1 CLOSED · X-2 unchanged from s34** (still open, seating still Lon/BOARD's call — untouched by either s35 or s36).

**X-3: MECHANISM IS s36's, NOT s35's — self-correction, not a tie.** Both sessions independently opened
X-3 and reproduced the same HEAP-port residence gap from the same starting cursor. s35 (`FINDING-2026-08-12j`)
measured the gap's *size* (36/122 patterns under HEAP vs 76/122 FORTH, DIFF-not-crash dominant) and, via a
correct MONITOR-FIRST run + gdb, traced ONE witness's crash to `g_emit.x86_scratch_off = drive_value_slot(nd)`
feeding an always-RSP-relative `FR()` macro with what looked like a garbage large offset (`FINDING-2026-08-12l`,
renamed from a same-letter collision with s36's file — both sessions picked the same next-free FINDING letter
concurrently, harmless, just untidy). **s36's asm-diff on a smaller, independently-discovered witness
(`158_pat_cap_arbno_each_iter.sno`, 2 lines) found the actual root cause and it SUBSUMES s35's observation
rather than contradicting it:** the offset isn't garbage — it's a real, legitimate flat-frame slot number
(regime-4 fallback, `x86_zop_regime` falling through because `x86_fc_hit` hard-gates to
`ZC_PORT_FORTH`) — **the defect is that NOTHING CARVES RSP SPACE FOR IT under `ZC_PORT_HEAP` at all.**
`x86_scratch_off`/`drive_value_slot()` (s35's site) is just one more consumer of an offset space that's
correctly *numbered* but never *reserved* on the RSP side under HEAP — a downstream symptom of the same
upstream gap s36 named, not a separate defect. **s36 also found why the codebase's own existing defense
doesn't catch this:** `bb_glue_flat.cpp`'s `bb_glue_flat_enter` already has a deliberate loud `x86_bomb()`
for exactly `CELL_HEAP && fc_bytes>0` — built by a prior session specifically to fail loudly rather than
silently on this class — but this witness's carve routes through the *separate* REG-4b central-hook path
in `x86_asm.h` (~2320-2333), which the bomb doesn't cover, so the failure surfaces three layers
downstream at the consumer instead of loudly at the guard. FINDINGS: `FINDING-2026-08-12k` (s36, the
mechanism — treat as authoritative for X-3's root cause) · `FINDING-2026-08-12j` (s35, the measured size —
stands) · `FINDING-2026-08-12l` (s35, superseded by s36's finding — kept for the record, the
`drive_value_slot()` observation is a correct-but-incomplete symptom, not the fix site).

**NEXT RUNG (s36's fork, adopted as-is — real codegen surgery, its own gate-proving session, not this
turn):** **(a) SAFE, do this first** — make the RSP-side carve fire under `CELL_HEAP` symmetrically with
`CELL_STACK` (replace `bb_glue_flat_enter`'s bomb with the same `sub rsp,K`/`add rsp,K` FORTH already
does, AND close the REG-4b central-hook path's sibling gap so every carve site double-allocates under
HEAP) — wasteful (rbx bump AND rsp carve both pay) but converts today's *broken* dormant claim into an
*actually* byte-safe dormant one, restoring § A's stated invariant and giving everything after it a
foundation to stand on. Acceptance: full `crosscheck/patterns` under HEAP matches the FORTH baseline **BY
SET, not count** — an improved pass count alone proves nothing (s36's own words: "has not proven
byte-safety, it has proven different wrong answers"). **(b) AMBITIOUS, do not start before (a) lands** —
actual slice-2 residence (heap-block-relative addressing through a new granted regime), inherits
HAZARD-3 (§ J) and needs new carve/stash infrastructure since HEAP carves nothing on RSP today to spill
into. Neither (a) nor (b) attempted this session by either party — zero code changed by s35, s36, or this
reconciliation; own-HEAD floors from s35's baseline stand.

**Housekeeping filed:** two sessions independently grabbed the same next-free FINDING letter (`k`) — s35's
was renamed to `l` post-hoc; no data lost, just a naming race, noted for anyone auditing the FINDING
sequence.

### PRIOR — 2026-08-12 s36 (Sonnet 5). (still open, seating still Lon/BOARD's call, not touched). **X-3: MECHANISM FOUND — answers s35's own "next rung" question, zero code landed.** FINDING: `FINDING-2026-08-12k-…md`. ⛔ **CONCURRENT-SESSION NOTE:** this session started from s34's cursor and did not learn s35 had already opened/measured X-3 until mid-investigation (a `git pull --rebase` surfaced s35's push already in flight) — the ONE-INVARIANT held (s35 had finished and pushed before this session's own X-3 finding was written), but it was a near-miss; both sessions independently reproduced the same gap from the same s34 starting point. **THE MECHANISM (asm-diff on a NEW 2-line witness, `158_pat_cap_arbno_each_iter.sno` — smaller than s35's `041_pat_span`):** the residence gap is not "reads a stale-but-valid cell," it is an **unreserved stack write**. Every fc_geom-granted box that would get a FORTH `sub rsp,K` cell gets NOTHING carved on the RSP side under HEAP (`x86_fc_hit` hard-gates to `ZC_PORT_FORTH`, so `x86_zop_regime` falls through to regime 3/4, whose `off` is a real flat-frame slot number that nothing ever reserved space for — confirmed by grepping every `sub rsp` in both compiled `.s`: only the fixed 8B prologue exists in either, FORTH additionally carves 16B immediately before use, HEAP does not carve at all before writing `[rsp+272]`). **The existing guard does not catch this:** `bb_glue_flat.cpp`'s `bb_glue_flat_enter` already has a deliberate `x86_bomb(...)` for CELL_HEAP with fc_bytes>0, built specifically to fail loudly rather than silently on this exact class (its own header comment says so) — but the witness's carve routes through the *separate* REG-4b central-hook path, not through this helper, so the bomb never fires and the failure surfaces three layers downstream at the FR/FRQ consumer instead. **THE FORK NAMED (not resolved):** (a) SAFE — make CELL_HEAP's RSP-side carve fire identically to CELL_STACK (delete/replace the bomb, double-allocate rbx+rsp temporarily), restoring the § A byte-safety claim that is currently FALSE; (b) AMBITIOUS — actual HZ-1 slice-2 residence (new granted regime through the heap-block base, inherits HAZARD-3's stash problem, needs new carve infra since HEAP carves nothing on RSP to spill into). **RECOMMENDATION: (a) first, verified BY SET (not just count) against the FORTH baseline before attempting (b).** Numbers reconciled against s35's, not re-litigated (STALENESS LAW — the ~5-program patterns delta between sessions is ordinary concurrent-seat drift, mechanism is HEAD-invariant). ⛔ **(a) NOT ATTEMPTED THIS SESSION, and deliberately so — see FINDING addendum.** Tried to pin the exact K-granting field behind the witness's slot (`op_fc_bytes` vs `op_zls2_bytes`) before touching REG-4b; `--dump-zeta` confirmed the slot is a real, port-independent, planning-time static-table offset (`region_end=288`), but the field attribution stayed genuinely ambiguous from static reading alone — `op_zls2_bytes` has carve/release arms for `ZC_PORT_ALLOC`/`ZC_PORT_HEAP` only, **no `ZC_PORT_FORTH` arm anywhere in `x86_asm.h`**, which is inconsistent with FORTH working correctly unless either the hunk-to-slot pairing was mismatched by eye, or the FORTH carve for this class lives outside this file entirely. Matching disassembly to a planning table by eye is not rigorous enough to patch a TEMPLATE-ONLY/ONE-AUTHORITY file on. **NEXT RUNG, sharpened: instrument (env-gated trace of `op_fc_bytes`/`op_zls2_bytes`/`op_zls2_ops` at the `X86H_DEF/ALPHA` choke, matching the `SCRIP_FC_AUDIT` idiom) before writing into REG-4b — trace, don't infer, the field attribution, then implement (a).** Zero code changed this session; tree clean.

### PRIOR — 2026-08-12 s35 (Sonnet 5). **X-0 CLOSED · X-1 CLOSED** (unchanged). **X-2 unchanged from s34 — still open, mechanism named, fix not landed, seating still Lon/BOARD's call — not touched this session.** **X-3 OPENED (per s34's own recommendation to decouple from X-2): SCOPED AND MEASURED, ZERO CODE.** FINDING: `FINDING-2026-08-12j-CLAUDE-SONNET5-HOME-RBX-X3-…md`. Own-HEAD baseline re-proved fresh (not transcribed): probe/bb m3 159/1xfail/5-REGRESSION-by-set (unchanged names), m4 157/2xfail/**6-REGRESSION — new name X05 alongside the known five**, patterns 76/122, gc 15/15, capture 8/9 — all identical by set to s33's recorded floor except the new X05 (filed, not chased — outside X-3). **Measured the § A residence gap directly** (`SCRIP_ZETA_PORT=7` swaps port at both emit- and run-time for m3 in one process, same reader `x86_port_mode()`≡`rt_zeta_port_mode()`): HEAP port already matches FORTH on hello+assign (16/16, frontier arithmetic is sound) but drops to **36/122 on patterns** (vs 76/122), 13/15 on gc, 6/9 on capture — and critically **the dominant failure mode inverts from crash to DIFF** (48/122 DIFF under HEAP vs 12/122 under FORTH) — silently-wrong output, not a fault, which is the SPITBOL-semantics violation the HOME GATE measures against. Census: 26 `ZC_PORT_FORTH`-gated consumer sites across 8 files (`emit.cpp`, `x86_asm.h`, three `bb_match_*.cpp`, `bb_call_proc_staged.cpp`, `emit.h`, `zeta_alloc.c`) vs only 5 `ZC_PORT_HEAP`-aware sites in 3 files — ~5:1 blast radius, confirms § A's "slice-2, never run" framing rather than a quick default flip. **NEXT RUNG:** point the MONITOR-FIRST 2-way sync-step monitor at `041_pat_span` (passes FORTH, SIG11s HEAP) — cheapest named divergence pair on record, same source/oracle, one env var different — to find the first divergent trace event before touching `x86_fc_hit`/`fc_alt_active` cold.

**s35 UPDATE (same session, continuation):** ran MONITOR-FIRST (`spl` vs `scr`, `SCRIP_ZETA_PORT=7`) on
`041_pat_span` — first divergence is the capture write (`V = SPAN(...)`), matching the census exactly.
gdb (`SCRIP_NO_SEGV_HANDLER=1`) at the fault: `mov %r14d,0x7f004(%rsp)` — a garbage **offset**
(520196), not a garbage pointer; rsp/rbp both ordinary. Correlated against `--compile` text output both
ports: HEAP correctly suppresses the SPAN box's `sub rsp,16` carve (matches § A) but its own-cell
save/restore still emits `[rsp+off]` via `FR(_.x86_scratch_off)`, with `off` now 520196 instead of 20.
Traced to source: `emit.cpp:1428/1435` `g_emit.x86_scratch_off = drive_value_slot(nd)` feeds `FR()` in
`bb_match_span.cpp` and eight siblings (BREAK/BREAKX/TAB/RTAB/REM/ARB/BAL — same `emit.cpp:940-950`
shape). Hypothesis, not yet confirmed: `drive_value_slot()` doesn't branch on port, so a HEAP-scale
cumulative in-block offset is landing in an always-RSP-relative macro. FINDING:
`FINDING-2026-08-12k-CLAUDE-SONNET5-HOME-RBX-X3-…md`. **NEXT RUNG (X-3 slice-2, real surgery, not this
turn's scope): read `drive_value_slot()`, confirm/falsify, fix under TEMPLATE-ONLY/BOTH-MEDIUM, gate
against all nine `x86_scratch_off` consumers before closing.** Zero code changed this session; own-HEAD
floors from the s35 baseline (above) stand unchanged.

### PRIOR CURSOR — 2026-08-12 s34 (Sonnet 5). **X-0 CLOSED · X-1 CLOSED** (unchanged). **X-2 OPEN, MECHANISM NAMED, FIX NOT LANDED.** FINDING: `FINDING-2026-08-12f-CLAUDE-SONNET5-HOME-RBX-X2-…md` — RTX-FUNC-11 is **not** a capacity defect (the `_var_reg`/WSI/`global_names`/`errjmp_n` hypotheses are all killed, see FINDING §2-3). The `SNO$NAME` dispatch over-releases exactly `0xCC0` (3264) bytes of RSP on every loop iteration, **only when the loop body arrives via `-INCLUDE`** — confirmed by two independent instruments (live RSP tracing at the `rt_call_arr` JIT call-site boundary, and core-dump disassembly of an independent crash instance) converging on the identical constant. Zero drift on the non-`-INCLUDE` control (53 calls, byte-identical rsp). This is the first mechanical explanation in the investigation's history for why every red witness requires `-INCLUDE` and every inline control is clean. **NEXT RUNG WORK: find the emitter/lowering site emitting the per-included-block `add rsp,0xcc0` cleanup and why it fires per-iteration instead of per-block** (candidates: `-INCLUDE` handling in `lower_snobol4.c`, or the enclosing statement-frame emitter in `emit.cpp`) — not yet located, this is instrumentation + mechanism, not a patch. Three env-gated diagnostic counters added to `core.c`/`by_name_dispatch.c` (`SCRIP_NV_TRACE`, `SCRIP_CALLARR_TRACE` incl. rsp column) — **uncommitted at cursor-write time**, recommend committing as permanent diagnostic infra (matches `SCRIP_ALLOC_HIST` idiom).

### ⭐⭐ s34 PLAN SCRUTINY — X-2's PREMISE IS FALSIFIED AND THE RUNG MAY BE MIS-SEATED (read before spending another session on X-2)

**1. X-2 IS NOT AN ALLOCATION DEFECT — THE RUNG WAS POINTED AT THE WRONG SUBSYSTEM.** The rung text ("INSTRUMENT THE ALLOCATION ITSELF", "convict the include-scoped capacity for runtime-created variables") and § I's Ch.19-note-7 anchor ("runtime-created variables are an unbounded, monotone, never-freed population … any *fixed* include-scoped capacity is wrong by the language definition") are a TRUE semantic statement about SNOBOL4 that is **NOT the mechanism of FUNC-11**. Measured s34: the fault is a **stack release imbalance in emitted code** — `+0xCC0` (3264B) of RSP handed back per loop iteration, deterministic across runs, present ONLY on the `-INCLUDE` arm, **zero drift** on the inline control (53 calls, byte-identical rsp). No allocator, table, or capacity is involved anywhere in the path; four capacity candidates died by inspection/measurement (FINDING §2–3: `_var_reg` is dead code, WSI is bounded+`abort()`-guarded at 1GB, `global_names`/`Scope` are compile-time-only, `errjmp_n` is flat at 1). ⇒ **Ch.19 note 7 remains a correct standing semantic obligation for SCRIP, but it must stop being cited as FUNC-11's diagnosis.**

**2. ⛔ THEREFORE X-2 MAY BELONG TO ANOTHER SEAT.** This seat's charter is `rbx = GC heap-top; allocation + GC coverage`. A per-call RSP release imbalance is **RSP spine discipline** — master-file row: `RSP | FORTH spine … | ZETA-MECH ONE-SYSTEM + LIFO law`. **A per-call RSP imbalance is precisely a LIFO violation** — the exact class `FINDING-2026-08-11e … EARN-0B-THE-LIFO-THEOREM-HOLDS-ON-GREEN-PATHS-IN-BOTH-DIRECTIONS` built its instrument to detect. That theorem was proved on GREEN paths; this witness is a RED path, so it is **not** a counterexample — it is the **first known live instance of the class that instrument exists for, and nobody has pointed the instrument at it.** ⭐ CHEAPEST NEXT EXPERIMENT, whoever owns it: **run the EARN-0b LIFO instrument on `probe/rtx11_dynvar_include.sno`.** RECOMMENDATION filed outward, **not unilaterally re-seated** (seats own their files; RULES "DO NOT READ UNRELATED GOAL FILES"): Lon/BOARD decide whether X-2 stays here or moves to the RBP/EARN or ZETA-MECH authority.

**3. THE `-INCLUDE` COVERAGE HOLE IS NOW A CORRECTNESS GATE, NOT HYGIENE.** X-2 already owns it ("crosscheck has ZERO live `-INCLUDE`"). s34 raises its priority: the addendum (FINDING §10) found **zero `INCLUDE` hits in `emit.cpp` AND `lower_snobol4.c`** — there is no explicit `-INCLUDE` branch in lowering or codegen, so the divergence is **structural**, in the AST/IR shape the splice produces upstream. If spliced loop bodies diverge structurally in frame accounting, all 318 crosscheck programs are constitutionally blind to the class — exactly as the 2026-08-11 FINDING warned. Promote `rtx11_dynvar_*` with BOARD and mint ≥1 `-INCLUDE` member per rung suite.

**4. DENOMINATOR PIN (this file contains two).** X-2's ACCEPTANCE says "`beauty_suite/` **34 files** green both modes"; the INSTRUMENT MAP row says "**17/17** drivers SIGSEGV at HEAD". Verified s34: **34 `.sno` exist in `beauty_suite/`**, of which the "17" counts `*_driver.sno` only. Both denominators are live in one file. **Pin which is acceptance BEFORE the fix lands** — this plan has already voided a rung on a denominator error (`FINDING-2026-08-03 … ALREADY-DONE-WAS-A-DENOMINATOR-ERROR`).

**5. DECOUPLE X-3 FROM X-2.** X-3 is written "P2, after X-2 acceptance." X-3 is **port promotion** (`ZC_PORT_FORTH`→`ZC_PORT_HEAP`, § A: "not a build — a promotion") and has **no dependency** on the FUNC-11 defect, now known to be RSP-side frame accounting rather than anything on the rbx frontier. Recommend X-3 open **immediately, in parallel** — it is this seat's only remaining rung unambiguously in-charter, and blocking it behind a possibly-mis-seated X-2 idles the seat.

**6. INSTRUMENT LESSONS (offer for RULES.md, alongside the WIRES instrument rule).** (a) `SCRIP_ALLOC_HIST` reports via `atexit()` and therefore **cannot observe any crash class** — on the exact RED runs under study it silently emits nothing, and a null result from it means nothing. Standing corollary to "instrument, don't sweep": *the instrument must survive the failure mode being studied — verify it emits on the RED arm before trusting any null result from it.* (b) From s34's own caught mistake: *a probe whose construction supplies a known threshold-shifting factor cannot test the factor it varies.* My first V=1,R=50 probe built its table from 50 literal statements, silently supplying exactly the headroom the 2026-08-11 FINDING §6 padding sweep had already measured; rebuilt with a fixed-size loop and oracle-verified before the result was trusted. Same genus as the piped-`head` and SIGBUS-scored-clean traps already on record.

### PRIOR CURSOR — 2026-08-12 s33 (Opus 5). **X-0 CLOSED · X-1 CLOSED** (SCRIP `9ecb75a9`→`51934a9f` post-rebase). FINDING: `FINDING-2026-08-12d-CLAUDE-OP5-HOME-RBX-X1-…md`.

**WATERMARK (m3, BY SET, own-HEAD control — BOARD P0 floors do not exist yet):** `crosscheck/patterns` 76/46 **identical by set** HEAD vs X-1 · `crosscheck/gc` 15/15 · `crosscheck/capture` 8/1 (`061_capture_in_arbno`, pre-existing). Emitted `.s` **byte-identical** (`cmp`) ⇒ no codegen touched ⇒ RULES step-4 regen not triggered, proved not asserted. Gate `scripts/test_gate_rc8a_gc_coverage.sh` **GREEN**, every assertion positive-controlled by `SCRIP_GC_UNROOT={cas,rtcc}`.

### ⛔⭐⭐⭐ CROSS-SEAT INTELLIGENCE — READ BEFORE X-2 OR X-5 (s33 other seats)

**From RBP seat (FINDING-2026-08-12e):** The `main_α` bridge never established R9. `flat_α` gets `rtcc_load_all`; `main_α` (~scrip.c:1278-1290) does not. Every program through `main_α` emits `[r9+…]` GVA refs with r9 never loaded → first GVA-slotted write faults m4. ONE LINE FIX in `scrip.c`. Effect: `patterns` m4 SEGV 82→11 (42 repaired, 0 regressions). ⛔ **Build order is load-bearing: `install_system_packages.sh` BEFORE any build** — a scrip built before it omits `call rtcc_load_all@PLT` and manufactures phantom m4 SEGVs. The r9 fix may already be on origin; `git pull --rebase` and verify `git log --oneline SCRIP -3` before building.

**From WIRES seat (s33 cursor):** `g_blob_ctx`/`rt_blob_ctx_ptr` now grep to 0 (W-1, `26c84e72`). WIRES m3 floor: probe/bb suite 157 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10} by set — pre-existing, hold BY SET. WIRES INSTRUMENT RULE (offer for RULES.md): an instrument reports a class only after one member has been confirmed by hand; three scanner bugs in one session all caught this way.

**Impact on X-2:** FUNC-11 (`rtx_func_11_include.sno`) is an m4 SIGSEGV class. The r9 fix may cure some as a side effect. **Verify which programs flip before and after the r9 fix before instrumenting the allocation path** — do not instrument a class the r9 fix already repaired.

### NEXT RUNG: X-2 (FUNC-11) — SHARPENED

No ⛔ REQUIRES; opens immediately.

**MANUAL-LEVEL ARGUMENT (do not re-sweep).** SPITBOL v3.7 Ch.19 note 7: a variable block for a user-created name is allocated and **never reclaimed** ("this space is never reclaimed once it has been allocated"). Runtime-created-variable population is **unbounded and monotone by the language definition** — a fixed include-scoped capacity is wrong by construction, not merely undersized. The fix must GROW the structure; three falsified threshold constants prove raising the constant does not work.

**INSTRUMENT FIRST.** Counter in the runtime allocation path — `NV_SET_fn` / `rt_nv_set_by_name` call sites where a name never seen before creates a variable block, distinguishing STATIC (compile-time) from RUNTIME (DEFINE/CODE path) creation. Show the counter grows unboundedly on the witness before proposing a fix.

**Witnesses (verified at corpus `14dc06bd`):** `probe/rtx_func_11_{inline,include}.sno` + `probe/rtx11_dynvar_{inline,include}.sno`, refs baked, two-sided. ACCEPTANCE: `programs/snobol4/beauty_suite/` **34 files** green both modes. ⛔ Re-measure after the r9 fix lands — the m4 acceptance number may shift.

### X-5 (post-X-1, gate now green)

⛔ Before touching it: the r9 one-line fix changes the m4 surface for the arg tier. Do the RTCC s16c instrument **on a correctly-built binary after the r9 fix.** On RC-8c (XMM8–15): AMEND the charter to 9 GPRs and explicitly park XMM — no rung has verified the XMM claim at all. Amendment belongs on GOAL-RTCC.

### X-3 (P2, after X-2 acceptance)

Port promotion, not a build (§ A). Does NOT owe the `pz` cost (§ D corrected — `pz` was already dead at HEAD, measured `pz=0` on every collection). Two costs X-3 DOES owe: pin/range monotone growth per refill; and false retention from integers in ZH refill blocks that look like heap addresses. Measure both on a long-running program before promoting HEAP as the default port.

### FILED OUTWARD

- ⛔ **HAZARD-1 → BOARD + WIRES:** `xa_flat.cpp:520,526` clobbers rbx as a scratch save slot (Icon ICN-FR-2 zframe ω) — claim gate does not yet cover rbx.
- ⛔ **→ BOARD:** all 15 `crosscheck/gc` programs trigger ZERO natural collections (instrument live: 2432 under stress). The GC suite does not exercise the GC.
- **→ RBP / LOWER:** `ARB . A` capture diverges from oracle at HEAD; a capture loop SIGSEGVs where oracle prints 2290; both pre-existing.
- ⛔ **→ BOARD (from WIRES):** WIRES instrument rule — offer for RULES.md.

- ⛔⭐ **→ LON / BOARD (s34, SEATING DECISION):** X-2's mechanism is an RSP LIFO violation, not an allocation defect — decide whether X-2 stays in RBX (charter: heap-top/allocation/GC) or moves to the RBP/EARN or ZETA-MECH authority that owns RSP spine + LIFO law. Seat did NOT re-seat it unilaterally.
- ⛔ **→ RBP/EARN (s34):** `probe/rtx11_dynvar_include.sno` is the **first known RED-path instance** of the EARN-0b LIFO-violation class. The LIFO instrument has never been pointed at it. One command, likely decisive.
- **→ BOARD (s34):** promote `rtx11_dynvar_{inline,include}` to the named-witness layer and mint ≥1 live `-INCLUDE` member per rung suite — crosscheck's zero-`-INCLUDE` hole is now a demonstrated correctness gap, not hygiene. Also: pin the `beauty_suite` acceptance denominator (34 files vs 17 drivers — both live in this file).
- **→ RULES.md (s34, two offers):** (a) an instrument must survive the failure mode under study (`SCRIP_ALLOC_HIST`'s `atexit()` cannot observe a crash class — its null result is uninformative); (b) a probe whose construction supplies a known threshold-shifting factor cannot test the factor it varies.

**UNBLOCKS: RBX X-3** (independent of X-2 — see s34 SCRUTINY §5; open it immediately rather than idling behind a possibly-mis-seated X-2). X-2 mechanism named, fix NOT landed, emitter site NOT located; next search starts at how `-INCLUDE` is expanded upstream and diffs `--dump-ir` between the two arms — **not** by grepping emitter/lowering for the string `INCLUDE` (zero hits, already checked s34).
