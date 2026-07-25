# FINDING (2026-07-24, s151, Claude) — ARBNO(*P): the per-iteration stride is COMPILE-TIME-KNOWABLE via the PS-1b emit registry; the rung's "runtime latch [p+16]" is the fallback, not the primary. PS-3 reframed + DB-2b coordination named precisely.

**Context:** PS-1b landed this session (DT_P `zstatic` now real on the live `SNO$MKPAT` path, both modes — see LIVE CURSOR). With the stamp trustworthy, I characterized the ARBNO(*P) problem against the actual emit code (`src/templates/bb_match_arbno.cpp`, `bb_match_defer.cpp`, `zeta_storage.c` fc-tail table, `emit.cpp` IR_MATCH_ARBNO drive) before touching the hot path. Three things are now established; the third reframes the PS-3 rung.

---

## 1. ARBNO(*P) is already CORRECT — the problem is the ceremony, not the answer

New canary `corpus/crosscheck/patterns/179_pat_arbno_defer_recursive_list.sno` (the SPITBOL manual ch.9 recursive nested list: `ITEM = SPAN(d) | *LIST`, `LIST = "(" ITEM ARBNO("," ITEM) ")"`, three subjects incl. a rejected one). **Byte-identical to the sbl oracle in BOTH m3 and m4** at this HEAD. So the `*P`-in-ARBNO body works today; PS-3 is a performance/ceremony rung (ARCH-SNOBOL4 §ARBNO: "FAST, IMMEDIATE γ processing … zero per-iteration linkage ceremony"), NOT a correctness fix. Whatever lands must keep 179 byte-identical.

## 2. The current path is the chain arm (the ceremony)

`--compile` of 179 emits, in the LIST proc: `IR_MATCH_ARBNO_NARY (ZB-FC-4 rsp linked-frame-chain)`. So `fc_tail_arbno()` (the fast R12-EXIT-1 tail, pure `add/sub rsp, op_sb` arithmetic, all `[rsp+const]`) FAILS for a defer-bearing body — its span walk (`zeta_storage.c` ~ln 456-470) sees only the DEFER node's own slot, never the arriving blob's self-allocated frame — and it falls to the chain arm. The chain arm's per-iteration ceremony (`bb_match_arbno.cpp` ~ln 113-163): save prev view(rbp)/link/rsp into `[rsp+0/8/16]` every β, update the link cell, φ reads them back and does a view-relative `lea rsp, [zv + op_sa-24+op_sb]` to abandon. The `arbno_fill_window` per-element zero is already NOFILL-elided (s141). The residual cost is the **link save/restore + view dance** — the thing PS-3 wants replaced by arithmetic.

## 3. THE REFRAME — the stride is COMPILE-TIME, not a runtime latch

The rung sketched "latch at α from the arriving DT_P (`[p+16]`)". Reading the code, a **pure runtime latch has a chicken-and-egg**: the deferred `*P` node lives INSIDE the ARBNO body and executes AFTER the ARBNO α, so at α the arriving blob `p` is not yet resolved — ARBNO cannot read `[p+16]` before it needs the stride to place frame 0. The chain arm sidesteps this precisely by NOT needing the stride up front (it discovers each frontier from the saved link). A latch could only fire on iteration ≥1 (after the first defer resolution), a hybrid whose win over the chain is marginal and whose first-iteration path still needs the link.

**But PS-1b makes the stride a compile-time constant for the common case.** `ARBNO("," *LIST)` where `LIST` is a stored pattern compiled to `proc_PAT$k`: that proc's per-activation `frame_bytes` (= the blob's ζ footprint, the `zsz` we stamp) is **registered at EMIT time** (`scrip.c` proc loops → `rt_proc_set_frame_bytes`, mode-3 direct + mode-4 printed startup; PS-1b added the parallel `zstatic` bit the same way). So if the EMITTER resolves `*P`'s target name → its `PAT$` proc → that registered `frame_bytes`, the uniform per-iteration stride is **known at compile time**: `op_sb = align16(HEADER + PAT$k.frame_bytes)`. No runtime latch. The construct collapses onto the existing fast **tail arm** (`bb_match_arbno_tail`), whose arithmetic is exactly right for a uniform stride.

### Why this is licensed, and by what
- **Uniformity:** every iteration transfers into the SAME blob (`*P` is one name), so every iteration's footprint is identical = that blob's `zsz`. Uniform stride ⇒ tail-arm arithmetic (`add rsp, op_sb` to abandon) is valid.
- **Self-containment (the `zstatic` guard, now real):** the arithmetic is sound only if the blob has no interior transfer into a further unknown-extent blob (a nested DEFER/VALUE), which would interleave an unknown carve between iteration frames. `zstatic==1` (PS-1b) is exactly that predicate. If `zstatic==0` (e.g. the blob itself contains `*Q`) ⇒ keep the chain arm.
- **Bind stability (DB-1, the real dependency):** a compile-time stride assumes `*P`'s target does not change identity/size mid-run. That is the DEFER-BIND ladder's write-once property (DB-1: 99.999% of deferred names are assigned exactly once — VERIFIED for the 5 demos). So **PS-3's compile-time-stride form is licensed by DB-1's write-once binding + a barrier that falls back to the chain arm on the rare reassignment.** This is the precise coupling the rung gestured at with "needs DB-2b coordination"; sharpened: it needs **DB-1's bind-license** for the stride constant, and **DB-2b's γ/ω linkage** for the frame handoff (next para).

### The one genuine template-coordination problem (DB-2b)
The tail arm OWNS its element frame (ARBNO carves `op_sb`, body leaves write `[rsp+off]`). A `*P` body does NOT: the deferred blob SELF-allocates (`sub rsp, zsz` at its own α — see `bb_match_defer.cpp` fast arm: `jmp rax` into the blob, γ→L(4)/ω→L(5) via rcx/rdx, **β resumes via `jmp [rsp+0]`**, the blob's resume record at the frontier). So the tail arm must be reconciled with blob-owned frames: ARBNO carves only its HEADER (24B: entry-cursor/yield-cursor/elem0-flag), the blob carves `zsz` below it, and the abandon `add rsp, op_sb` (op_sb = align16(24 + zsz)) must land EXACTLY on the frontier where the blob's β expects `[rsp+0]`. Getting that offset wrong corrupts backtracking on SOME inputs only — the class of bug RULES.md mandates be found with the 2-way monitor, never guessed. **This is the DB-2b work: make the defer fast-arm's self-allocation frontier and the ARBNO uniform-stride abandon agree by construction.**

---

## Recommended PS-3 sequence (supersedes the rung's "runtime latch" sketch)
1. **DB-1 first (bind-license).** Write-once binding + barrier is the correctness license for a compile-time stride; without it the stride constant is unsound under reassignment. (Already the next-priority ladder.)
2. **Emit-time resolution.** In the IR_MATCH_ARBNO drive (`emit.cpp` ~ln 858), when the body is a single/leading defer-of-VAR whose target resolves to a `PAT$k` with `zstatic==1` and registered `frame_bytes` (both now available via PS-1b's `rt_fn_frame_bytes_known`/`rt_fn_zstatic_known` — add a name-keyed emit-side reader), stage `op_tail` with `op_sb = align16(24 + frame_bytes)` and route to `bb_match_arbno_tail`. Else keep the chain arm.
3. **DB-2b reconciliation.** Adjust the tail arm (or a defer-body variant) so the abandon frontier meets `bb_match_defer`'s `jmp [rsp+0]` β convention. Monitor-bracket any 179 divergence.
4. **Kill-switch + gates.** `SCRIP_ARBNO_LATCH=0` ⇒ chain arm (byte-identical default proven by md5 on the trio + 179 `.s`). Gates at watermark both modes, plain + POISON. Rail treebank/calc-2 (THE lever: treebank IR_MATCH_ARBNO is 58% per s140 bbprof).

## What landed vs. what's designed (said plainly, not oversold)
- **LANDED + gate-verified this session:** PS-1b (the enabler — `zstatic`/`zsz` real on the live path, both modes, watermark-exact) + canary 179 (byte-identical baseline). These are the prerequisites; they are done and tested.
- **DESIGNED, not landed:** the tail-arm compile-time-stride mechanism above. It is a hot-path template rung gated on DB-1 (bind-license) and DB-2b (frontier coordination); per RULES it must be monitor-proven, not rushed. This finding makes it mechanical — the stride is a constant the emitter can now read, not a value to be discovered at runtime.

---

## s152 RESULTS ADDENDUM (2026-07-25, Claude) — slice 1 landed; the frame simplified further in implementation

**What the .s ground truth changed:** the finding's `op_sb = align16(24+frame_bytes)` was still not the whole ζ size. Measured blob anatomy (t1.s): entry carve `align16(32+fb)`; interior FORTH port cells STAY carved on the hit path (SPAN's 16); γ pushes a 16B `{res-addr, saved-rbp}` record at the frontier; β `jmp [rsp+0]` self-pops it; ω `lea rsp,[rbp+K]` restores the entry frontier sweeping every interior carve. So **SUSP = align16(32+fb) + fp_total + 16**, and — the larger simplification — for a pure-defer body the outer arm needs NO stride arithmetic at all: β carves only a 16B cursor header, φ pops 16 and lands on the previous record, the blob does the rest. SUSP is consumed at exactly ONE point: σ's entry-cursor read `[rsp+SUSP]` (the flat yield quad is clobbered by the first yield, so the baseline must be per-element — the chain arm stores it per-element for the same reason).

**Strengthening of record:** `zstatic` (no DEFER/VALUE) does NOT license a footprint constant — an interior ARBNO retains a variable count of element carves across γ-suspension. The stride/SUSP license is `uniform = zstatic ∧ no-interior-ARBNO ∧ region-known` (`g_last_flat_uniform`).

**Order hazard (the finding's DB-1 dependency) closed without the barrier for the landed class:** prologue-dominance (`sno_name_prologue_bound`) — the seal==2 single write must sit in the unconditional entry corridor, making the slow-path frontier shape unreachable. The DB-1 barrier remains the residue for non-prologue names.

**Proof set:** 181 six-stressor canary oracle-identical both mediums with the arm firing (σ offset 160 = 128+16+16 hand-verified against the emitted blob); 070+180 fire inside the armed watermark; watermark OFF and ON identical (312/1 · 307/4 · DIVERGE=3, same sets); 10 demos ON==OFF==SBL; three `.s` regen scripts → zero drift at default; 179 declines byte-identically.

**A FACT-RULE catch worth recording:** an early "179 byte-identical" diff compared two EMPTY files (bad relative path, both compiles silently produced nothing, `diff -q` passed). Re-established on real 33 KB outputs. Lesson: byte-identity evidence must include a nonzero-size check.

**Honest scope:** slice 1 admits pure-defer bodies only; every demo ARBNO embeds the referenced pattern's tree (defer inside a windowed subtree) and declines — the rail is unmoved. The lever path is the defer-as-known-footprint-LEAF fold into the R12-EXIT tail (fp contribution = SUSP), then the record-peek cursor (`[rsp+8]→[rbp+56]`) to drop the uniformity gate and admit recursion.
