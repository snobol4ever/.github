# FINDING — s21x-b (2026-07-29, Claude Sonnet 4.6)

## Session identity
Goal: GOAL-SNOBOL4-BB.md (RBP-SHED ladder + artifact provenance sweep + source-comment layout diagnosis)
Watermark at session start (inherited from s21x, no emitter edit this session): **m3 311/4 · m4 311/2 · DIVERGE=2** — byte-identical to session-start baseline by construction (zero compiler source touched).

---

## THREAD 1 — ARTIFACT PROVENANCE SWEEP + DEAD TREE DELETION

**FINDING:** Full census of all committed `.s` artifacts across SCRIP + corpus. Every tree classified by header format (current emitter = wide-column `.intel_syntax    noprefix`).

Dead trees DELETED (zero consumers in scripts/src/test/Makefile):
- `SCRIP/artifacts/asm/` + `SCRIP/artifacts/x64/` — `scrip --jit-emit --x64` SM path (deleted). 25 files.
- `SCRIP/test/emit_baseline/` — 161 zero-byte files under a literal `-asm/` dirname, relic of the 152×3-backend `util_g8_session_emit_fix.sh` era.
Commit: SCRIP `2c22b2c5` — 506 files, 12,889 deletions.

Trees regenerated / brought current:
- `corpus/benchmarks/prolog/bench` — 22 stale → regenerated
- `corpus/benchmarks/icon` — 10 stale → regenerated
- `corpus/crosscheck` — 180 scrip-cc relics + 300 sources without artifacts → 480 regenerated; 17 emit/as-fail (expected mid-design)
- `corpus/programs/prolog` — 151 stale + 230 minted → 381 total
- `corpus/programs/icon` — 284 refreshed
- `SCRIP/test/{icon,prolog}`, vanroy bench — 14 straggler refreshes

**Final census:** 1,372 of 1,409 non-empty `.s` provably current-emitter. Remaining ~26: semicolonize-needing icon sources (parser now requires semicolons), 5 hand-written coverage/null references, a few lon/gimpel relics, and the 17 expected crosscheck failures.

---

## THREAD 2 — TWO NEW REGEN SCRIPTS (no maintaining script existed)

`scripts/util_regen_crosscheck_s_artifacts.sh` — new, sibling of benchmark/demo/feature.  
`scripts/util_regen_programs_s_artifacts.sh` — new, covers programs/{icon,prolog,rebus}. Defaults to refreshing EXISTING artifacts; `ALL=1` to mint new ones.  
Commit: SCRIP `26e38f9d`.

---

## THREAD 3 — RBP-SHED LADDER (Lon directive: "Make a RUNG and STEPS to fix each occurrence that are removable")

Five rungs written into `GOAL-SNOBOL4-BB.md`, order **3 → 1 → 2 → 4 → 5**, plus pointer + block. Commit: `.github` `40c854b3`.

**SHED-3 (first):** `emit_rec_pin()` reads leaky globals `g_gen_proc_active`/`g_resumable_callable_active` refreshed only at jmp-entry arm (~emit.cpp:1821). LEAK REPRODUCED on w2 (`"A" | *V` stored pattern + determinate main): hook-skip `rc=1`, 20 `[rbp+N]` refs / 1 seed in the main graph. The generator-proc conjunct is driver-bracketed and CORRECT; `g_resumable_callable_active` is the sole leaker. Fix: per-emission mirror at the `emit_chain` choke point; falsifier: hook-skip flips 1→0 on w2.

**SHED-1:** Retire `g_flat_outer_nparams >= 1` in `xaf_deep()`. Census first (zero ⇒ no-op). Param binds at `[rbp+16/24]` are FRQ-routed so they convert for free; the conjunct provenance is unrecorded — FINDING must recover it.

**SHED-2:** Move `IR_MATCH_ABORT` from FB-STMT disqualifier → bracketed set by routing abort kill through statement fail exit (restores 058 rebalance law for abort-bearing statements). 170/171 tripwire both directions.

**SHED-4:** Rewrite scanhit/scanfail hooks (emit.cpp:2183/2197) through `x86()`/FRQ — the named forbidden shape. Byte-identical completion test (flat_pat ⇒ pinned ⇒ fb_data==rbp already).

**SHED-5:** Run the env-gated alignment-dance assert (`x86_asm.h:419`); clean ⇒ delete the transient push-rbp window per its own named 8-byte alternative.

**SHED-6:** PL-DC pointer only → copy to `GOAL-PROLOG-BB.md`.  
**SHED-7:** Blocked on Lon — ARBNO `zv()` is sanctioned.

---

## THREAD 4 — PAT$ BLOB / IR_MATCH_VALUE: PROVED rbp IS LOAD-BEARING (Lon challenge "prove me wrong")

Read from `pattern_bt.s` (regenerated this session, provably current). PAT$ γ epilogue verbatim:
```
proc_PAT$0_g:
    push rbp                    ; 16B suspend record: [+8]=my base
    lea  rax, [rip + proc_PAT$0_res]
    push rax                    ; [+0]=my resume addr
    mov  rax, [rbp + 168]       ; caller's γ continuation
    mov  rbp, [rbp + 184]       ; caller's rbp back
    jmp  rax                    ; return WITH rsp STILL DEEP (retaining)
```
ω: `lea rsp,[rbp+192]` — absolute release sweeping ALL interior carves. The blob exports four labels (_α/_v/_γ/_ω), not one entry / one exit. ARBNO's hit-path element retention (t1.s ground truth) means the extent at β re-entry differs per pump — FLATDISP-5 wall, no compile-time rsp displacement exists. Per-activation requirement for recursive patterns (two live `*LIST` activations of the same blob) means the base must travel in the record — which is exactly what `push rbp` already provides, callee-saved across all `rt_*` calls for free.

**CONCESSION (Lon was ~80% right):** an INVARIANT blob (pure LIT/SPAN body, no interior choice points) HAS a static depth — FLATDISP-5a (inline it, no blob at all) is the right elimination. FB-STMT already proved only housekeeping needs rbp in retaining blobs (1015→220 refs).

**IR_MATCH_VALUE:** star/non-star distinction tried and DELETED 2026-07-29 (PATCTX). "Star was never the load-bearing property; γ-retention is, and every defer target can retain." Measured crashes: 125_pat_json_literal (rsp=0, alias target moved) and 072_pat_star_var_alt_backtrack (FB-STMT falsification (b)).

---

## THREAD 5 — SRC-ORDER-LAYOUT: comments are CORRECT, statement layout is scrambled

`# <source stmt>` comments are TRUTHFUL — each sits above its own code (verified: `# OK OUTPUT = "yes"` followed by its own `.string "yes"` 11 lines below). What is scrambled is the STATEMENT BODY LAYOUT ORDER:
- cm2 (5 stmts, 1 label, 1 `:S(OK)`): layout **1, 5, 2, 3, 4**
- cm3 (5 assigns, 2 labels, 0 gotos): layout **1, 2, 4, 3, 5**

Execution CORRECT (every chain ends in explicit `jmp`, verified at junctions). Defect is readability only.

**BLIND FIX BLOCKED:** `op_flat_disp` (rsp-depth prefix sum unpinned-regime FR/FRQ compensates by) is computed along emission order (BFS discovery). Reordering layout to source order may silently rebase cross-depth reads — the FLATDISP class sessions s193–s200 just healed. Needs Lon ruling:
- **(A)** Emit-side sort by `:stno` — prove/make `op_flat_disp` schedule-independent first (falsifier: byte-diff unpinned-regime benchmarks under `SCRIP_FB_STMT=1`). Make `:stno` unconditional (currently `MONITOR_BIN`-gated).
- **(B)** Find + fix the lower-side creation scramble — cm3's zero-goto permutation is the cleanest bisect probe (root cause not yet located within time-box).
- **(C)** Accept layout as-is.

Committed as rung in `GOAL-SNOBOL4-BB.md`: `.github` `7539f185`.

---

## THREAD 6 — ZHEAP / LBL__ FRAME SIZE (Lon: "each BB should allocate its own storage")

`proc_LBL__ROMAN_α` allocates 1344 bytes = the whole-graph LEXPREP carve (`K_total` from the zls slot layout: ~84 descriptor slots × 16B). The three parks at `+1320/+1328/+1336` are the U2 header contract (`kt-24/-16/-8`). The three zeroed pairs are FI8 lazy-init exemptions. SCRIP_FC_AUDIT on roman: 24 granted-box reads, 20 FLAT-BYDESIGN + 4 CROSS, 0 MISS — FORTH-cell machinery defect-free where granted; 110 distinct slots still in the flat frame.

This is exactly RUNG ZHEAP (s205 Lon pivot #1): ζ LOCALS → GC heap, ζ RESULTS → mmap VSP, only control on RSP. CELL-0 + CELL-1a are landed. Blocker: **Lon ruling on ζ_self register (jointly with VSP), §4 of the s206 finding** — unresolved at handoff.

---

## Commits this session

| Repo | Hash | Summary |
|---|---|---|
| SCRIP | `2c22b2c5` | DELETE dead .s trees (artifacts/asm, x64, emit_baseline) |
| SCRIP | `578c7d1a` | test-tree artifacts refreshed |
| SCRIP | `26e38f9d` | NEW regen scripts (crosscheck + programs) |
| corpus | multiple | benchmark+icon+prolog+programs+vanroy regen |
| .github | `40c854b3` | RBP-SHED LADDER |
| .github | `7539f185` | SRC-ORDER-LAYOUT rung |
| .github | `01801b13` | (this FINDING file) |

All pushed. Watermark UNCHANGED (no emitter source touched).
