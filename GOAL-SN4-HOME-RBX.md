# GOAL-SN4-HOME-RBX — RBX = GC heap-top; allocation + GC coverage (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER (Lon s30):** SNOBOL4 addressing is RSP + RBP + **RBX GC-heap-top relative**. Formalize rbx as the allocation frontier (today's DESCR mint pointer), make emitted code allocate inline against it, and make the GC actually see every register-resident and arena-resident root. rbx is callee-saved — the C boundary is free, same property as rbp.

## RUNGS
- [x] **X-0 · THE CONTRACT, WRITTEN (s33).** Deliverable = **§ THE CONTRACT** below (16-row GPR map + frontier invariant + safepoint/C-crossing/authority/overflow + the GC COVERAGE LEDGER that arms X-1). Zero code. Read cold as directed: `REGISTER-LAYOUT.md`, `DESIGN-SN4-REGISTER-PLANES.md`, `gc_heap.c`, `zeta_heap.c`, `x86_asm.h` REG-4b, the `rt_gcheap_alloc` mint path, + SPITBOL manual Ch.4/13/19 storage semantics. **THREE PRIOR RBX CLAIMS RECONCILED, TWO KILLED:** REGISTER-LAYOUT.md "rbx = DESCR BASE POINTER" is the frontier seen from 2026-05-31 and is SUBSUMED (a mint pointer IS a frontier); DESIGN-SN4-REGISTER-PLANES.md "rbx = VALUE plane / E frame base" is **DEAD FOR SNOBOL4** — that doc's own status line says nothing implemented, and E-as-rbx is unrepresentable alongside the frontier claim. This file is now the ONE authority; REGISTER-LAYOUT.md is history in full, not just its r12 row.
- [x] **X-1 · RC-8a — THE GC-SCAN GAP. CLOSED s33** (SCRIP `9ecb75a9`). Both regions now pin+range; gate `scripts/test_gate_rc8a_gc_coverage.sh` GREEN with a positive control on every assertion (`SCRIP_GC_UNROOT={cas,rtcc}` re-opens the hole: armed `ranges=1 cas=40`, sabotaged `ranges=0 cas=0`). Set diff vs own-HEAD control m3: patterns 76/46 **identical by set**, gc 15/15, capture 8/1. Emitted `.s` **byte-identical** HEAD vs X-1 (`cmp`) ⇒ no codegen touched, RULES step-4 regen not triggered — proved, not asserted. Original text: **RC-8a — THE GC-SCAN GAP (BLOCKING, inherited from RTCC s16).** `rtcc_gc_register` pins the pointer, scans nothing (`rt_gc_root_pin_add` only; every other block does `rt_gc_root_range_add` too). Add: RTCC block slots + **r12 pending-arena records** (they hold δ/target refs — the s30b obligation (ii)) + rbx frontier semantics to the scan. Latent at HEAD, LIVE the instant the arg tier is claimed.
- [ ] **X-2 · FUNC-11 — INSTRUMENT THE ALLOCATION ITSELF.** ⛔ STANDING INSTRUCTION (three seats, three falsified threshold constants): NO more black-box sweeps. Counter in the runtime path (or core-file technique) → convict the include-scoped capacity for runtime-created variables → fix. Then own the `-INCLUDE` coverage hole (crosscheck has ZERO live `-INCLUDE`; promote the `rtx11_dynvar` probe family with BOARD). **ACCEPTANCE: the BEAUTY drivers (17/17 SIGSEGV at HEAD, one include; `probe/rtx_func_11*` is the reduced two-sided witness) go GREEN both modes — this rung owns the flagship's blocker; the flagship byte-identity itself is P4's seal (HOME GATE line 6).**
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

## ⭐ LIVE CURSOR — 2026-08-12 s33 (Opus 5). **X-0 CLOSED · X-1 CLOSED** (SCRIP `9ecb75a9`→`51934a9f` post-rebase). FINDING: `FINDING-2026-08-12d-CLAUDE-OP5-HOME-RBX-X1-…md`.

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

**UNBLOCKS: RBX X-5** (RC-8a green). X-2, X-3 open.
