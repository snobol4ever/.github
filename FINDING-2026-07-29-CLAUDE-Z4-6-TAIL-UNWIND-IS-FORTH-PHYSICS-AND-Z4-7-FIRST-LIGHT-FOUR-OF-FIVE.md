# FINDING — Z4-6: THE TAIL ONE-MOV UNWIND IS FORTH-CELL PHYSICS · Z4-7 SLICE 1: FIRST LIGHT 4/5

2026-07-29, Claude. Session under `GOAL-ZETA-FOUR.md` (Lon directive: "finish the four; default = cell-stack and continue there"). SCRIP `87a44f89` → `dd3b7cbd` (Z4-6 residual) → `1551b0bc` (Z4-7 slice 1). Corpus `123daca2`. All timings none — this is a correctness session; RT_OPT=-O0 throughout.

## 1. Z4-6 RESIDUAL — the crash that names its own class
`z4_arbno` under `--zeta-storage=frame-rsp` died exactly as s4's cursor predicted (rsp=0x1 at a push-r14). gdb (monitor-first, sanctioned instrument): fault at `mov rsp,[rsp+0x138]` → `push r14` inside `n27_match_release_α`. The emitted text showed the tail RELEASE reading the statement bracket via **raw rsp-relative** `[rsp+304]/[rsp+312]` while a sibling restore in the same program correctly read `[rbp+240]`.

Root cause: `bb_match_release.cpp`'s **R12-EXIT-1 tail arm** reads the bracket off the TOP ELEMENT's fixed cell (`RSP(op_fc_disp+0/+8)`) and collapses everything with a one-mov `mov rsp,[...]` — **FORTH-cell physics**: it presumes elements carved rsp cells. Under CSTACK (Z4-6 slice 1 gated the fc grant authorities OFF) nothing carved, yet `op_fc_disp` still composed to 304 from the HEAD constant + gated-off sums — a number with no referent. The arm predates the file's own `rfc()` gate (`port==FORTH && fc_disp>=0`) that every non-tail arm already consults.

**Fix = one conjunct**: `_.op_tail && rfc()`. A non-FORTH tail RELEASE takes the general FRQ bracket arm — `FRQ(op_off+8)` patstk restore + `zls2_release_to_call(op_off+16)` + release_pump — the exact protocol the non-tail CSTACK releases were already passing with (HEAD writes those slots under CSTACK; verified in `bb_match_head.cpp`'s `!hfc()` arms).

**VERIFIED (SCRIP `dd3b7cbd`)**: frame-rsp **5/5 m3 AND 5/5 m4** (compile + `gcc -no-pie` + run, all == refs) — the rung's completion criterion, and parity with the `d79a427a` anchor era on HEAD. Default `.s` byte-identical pre→post ×3. Smoke matrix 6/6 rows == baseline. Heap arbno rc=139 untouched (Z4-8's pre/post proof preserved).

## 2. ⭐ REGEN BONUS — a benchmark unblocked by the same conjunct
Handoff-step-4 regen committed `benchmarks/snobol4/arith_mixed.s` for the **first time ever** (corpus `123daca2`, 624 lines, zero bombs). The file had never existed: under default FORTH some tail site there carried an **unregistered** `fc_disp` (the `(int)0x80000000` sentinel the s4 finding documented), so the old unconditional tail arm emitted a wild displacement the assembler rejected, and the regen script skipped the file. With the conjunct, that site falls to the FRQ arm, assembles, and: m3 result == `.ref` (`result: 60000001`), the committed `.s` links and runs in m4 with the same result. One predicate cured a crash in one config and an emission rejection in another — the two faces of the same port-blind read.

## 3. Z4-7 SLICE 1 — the extraction doc's prescription, executed literally
`EXTRACT-Z4-R12.md` §1: R12 never named itself; make the negative predicate resolve for the island and teach two accessors to return r12. Done as written:
- `rt_zc_frame_live()` (zeta_alloc.c, prototype zeta_alloc.h) — the **ONE live-frame authority** (the Z4-6 one-authority law applied to the frame axis): returns `ZC_FRAME_ISLE` (=0, the deleted `ZC_FRAME_R12`'s value renamed, zeta_choices.h) iff the four-config selector says `ZC_STORAGE_FRAME_R12`, else the `ZC_FRAME` build constant.
- **All 69** `ZC_FRAME ==/!= ZC_FRAME_RSP` comparison sites across 11 files route through it (`x86_zc_frame()` inline for templates/emit.cpp; direct calls in scrip.c / zeta_storage.c / lower_snobol4.c). Fresh recount: 72 total mentions of the comparison form − 2 rt.c `#if` blocks − 1 zeta_choices `#error` guard = 69 code arms — the extraction doc's "18" counted only the `!=` half at an older HEAD.
- Island arms restored: `x86_zr()/x86_zr_num()` → r12/12 (the epoch third arm); `x86_fb()` family → base r12 with `x86_frame_off` compensation **identically zero** (depth-immune base — same argument as the pinned rbp); both FR prefixes spell `[r12 + ]`.
- The dead machinery was **intact** and merely dead-coded: m4 wrapper's 64KB main-frame else-arm (`sub rsp,65536` / rdi seed / `rep stosq` / args at `[rdi+16/24]`), m3's `alloca(65536)` + `rt_outer_call(fn, mf, 0)`, zeta_storage.c's graph-scope zeta-mark slot reservation. All now reachable under the selector.
- Deliberately NOT converted: rt.c's two `#if ZC_FRAME==ZC_FRAME_RSP` blocks (the `rt_proc_enter` asm flavor + the `jmp_entry` shim) — build-time in the RUNTIME, i.e. the island config runs on the RSP-flavored call ABI today. Flagged as the seam.

**VERIFIED (SCRIP `1551b0bc`)**: default `.s` **byte-identical on all 5 probes** (the truth-table fold proven by bytes, not argument) and regen ×3 zero-drift corpus-wide; cell-stack 4/5 and frame-rsp 5/5 unchanged.

## 4. ⭐⭐ FIRST LIGHT — frame-r12 runs 4/5 at HEAD, capture CORRECT
First-ever execution of the island config on today's tree: `arith` OK · `span` OK · `arbno` OK · **`capture` CORRECT** (1500000 — the frame-config oracle property Z4-1/Z4-2 measured in the old worktrees, now reproduced ON HEAD; the cell-stack capture DIFF remains its own `d79a427a..cca948c5` regression) · `fib` rc=1.

The one failure names its thread: `rt.c:1056` — **"RETURN: open call for 'FIB' carries no return wires (activation was not flat-adopted)"**. The DEFINE call path: the island activation is not being flat-adopted, so the return-wire pair (gw/ww) is never set. Suspects, in order: `bb_call_proc_staged`'s island-cursor arm (carries the verbatim "r12 IS the zeta frame" comment), xa_flat's prologue adopt arms, the rt.c `#if` seam above, and the extraction doc's ~5 net-new arms that have never run under any real basis.

**The extraction doc's thesis — re-connection, not rewriting — is validated by first light**: three probes green and the capture oracle property intact with ZERO call-path work done.

## 5. HONEST LIMITS
(a) frame-r12 is 4/5 m3 only; no m4 island runs attempted yet (m4 island wrapper emits but is unproven). (b) The rt.c `#if` seam means the island currently borrows the RSP call ABI — the fib failure may be exactly this borrow; converting those blocks to runtime is a runtime-behavior change requiring its own careful pre/post. (c) No co-expression probe exists in the Z4 set; R-D's loud-decline requirement is untested this session. (d) All numbers RT_OPT=-O0, relative-only.
